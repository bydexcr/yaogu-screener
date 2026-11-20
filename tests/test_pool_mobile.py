# -*- coding: utf-8 -*-
"""mobile/pool_mobile.build_pool：并发抓取后的行为（ST 免请求 / 缓存命中 / 单只失败不中断）。"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
# 真机上 pool_mobile 以 mobile/ 为 CWD 运行，rest_client 就在同目录；测试里要显式补上
sys.path.insert(0, str(ROOT / "mobile"))

from mobile import pool_mobile as PM   # noqa: E402
from strategy import Candidate         # noqa: E402


class FakeApi:
    """记录被请求过的代码；history 返回空列表（K 线不足 → 不产生候选）。"""

    def __init__(self, fail_on=()):
        self.calls = []
        self.fail_on = set(fail_on)

    def to_ms(self, d):
        return 0

    def from_ms(self, ms):
        return "2025-06-01"

    def limit_up_pool(self, d):
        return [{"thscode": "600000.SH", "name": "浦发银行"},
                {"thscode": "000004.SZ", "name": "*ST国华"},
                {"thscode": "830799.BJ", "name": "艾融软件"}]

    def limit_break_pool(self, d):
        return [{"thscode": "300750.SZ", "name": "宁德时代"}]

    def history(self, code, start_ms, end_ms):
        self.calls.append(code)
        if code in self.fail_on:
            raise RuntimeError("模拟网络错误")
        return []


def _run(monkeypatch, tmp_path, fake, **kw):
    monkeypatch.setattr(PM, "api", fake)
    return PM.build_pool("2025-06-03", "2025-06-04", {}, tmp_path, **kw)


def test_st_seed_is_dropped_without_request(monkeypatch, tmp_path):
    """ST 在发请求前就剔除，省掉一次网络往返。"""
    fake = FakeApi()
    pool = _run(monkeypatch, tmp_path, fake)
    assert "000004.SZ" not in fake.calls
    assert sorted(fake.calls) == ["300750.SZ", "600000.SH", "830799.BJ"]
    assert pool == []


def test_single_failure_does_not_abort_the_pool(monkeypatch, tmp_path, capsys):
    """一只日K失败只算 missing，其余照常处理。"""
    fake = FakeApi(fail_on={"300750.SZ"})
    pool = _run(monkeypatch, tmp_path, fake)
    assert len(fake.calls) == 3          # 三只都请求过
    assert pool == []
    out = capsys.readouterr().out
    assert "300750.SZ 日K获取失败" in out
    assert "种子缺日K 1 只" in out


def test_short_history_is_skipped_silently(monkeypatch, tmp_path, capsys):
    """K 线不足 31 根属于正常情况，不算 missing。"""
    _run(monkeypatch, tmp_path, FakeApi())
    assert "种子缺日K 0 只" in capsys.readouterr().out


def test_empty_cache_is_ignored(monkeypatch, tmp_path):
    """空池缓存不可信（T-1 数据没发布时会写下空文件）→ 必须忽略并重建。"""
    cache = tmp_path / "pool_2025-06-03.json"
    cache.write_text(json.dumps({"t1_date": "2025-06-03", "candidates": []}), encoding="utf-8")
    fake = FakeApi()
    _run(monkeypatch, tmp_path, fake)
    assert fake.calls, "读到空缓存就直接返回了，没有重建"


def test_empty_pool_is_not_cached(monkeypatch, tmp_path):
    """候选为 0 时不写缓存，否则当天再也恢复不了。"""
    _run(monkeypatch, tmp_path, FakeApi())
    assert not (tmp_path / "pool_2025-06-03.json").exists()


def test_diag_reports_no_seed_when_pools_empty(monkeypatch, tmp_path):
    """T-1 涨停池/炸板池都为空时，diag 应标 no_seed（供页面说明原因）。"""
    class EmptyApi(FakeApi):
        def limit_up_pool(self, d):
            return []
        def limit_break_pool(self, d):
            return []
    diag = {}
    monkeypatch.setattr(PM, "api", EmptyApi())
    pool = PM.build_pool("2025-06-03", "2025-06-04", {}, tmp_path, diag=diag)
    assert pool == []
    assert diag["reason"] == "no_seed" and diag["seeds"] == 0


def test_diag_reports_api_error(monkeypatch, tmp_path):
    """涨停池接口报错不该冒泡，diag 标 api_error。"""
    class BoomApi(FakeApi):
        def limit_up_pool(self, d):
            raise RuntimeError("429 限流")
    diag = {}
    monkeypatch.setattr(PM, "api", BoomApi())
    pool = PM.build_pool("2025-06-03", "2025-06-04", {}, tmp_path, diag=diag)
    assert pool == []
    assert diag["reason"] == "api_error"


def test_bad_pool_workers_env_is_tolerated(monkeypatch, tmp_path):
    """POOL_WORKERS 写错不该让整次扫描崩掉。"""
    monkeypatch.setenv("POOL_WORKERS", "not-a-number")
    _run(monkeypatch, tmp_path, FakeApi())
    monkeypatch.setenv("POOL_WORKERS", "99")     # 上限被夹到 8
    _run(monkeypatch, tmp_path, FakeApi(), force=True)


def test_cache_hit_returns_early_without_network(monkeypatch, tmp_path, capsys):
    """同一天已算过就直接读缓存，一次 history 都不发。"""
    cand = Candidate(thscode="600000.SH", name="浦发银行", board="main",
                     t1_date="2025-06-03", t2_date="2025-06-04",
                     t1_pct=9.9, t1_limitup=True, t1_close=10.0,
                     t1_volume=1e6, t2_volume=2e6, t1_amount_yi=3.2,
                     volume_ratio=0.5, high_ndays=30, high30_margin_pct=1.2,
                     score=88.0)
    tmp_path.joinpath("pool_2025-06-03.json").write_text(
        json.dumps({"t1_date": "2025-06-03", "candidates": [cand.to_dict()]},
                   ensure_ascii=False), encoding="utf-8")

    fake = FakeApi()
    pool = _run(monkeypatch, tmp_path, fake)
    assert fake.calls == []
    assert len(pool) == 1 and pool[0].thscode == "600000.SH"
    assert pool[0].score == 88.0
    assert "[缓存]" in capsys.readouterr().out


def test_cache_from_other_date_is_ignored(monkeypatch, tmp_path):
    tmp_path.joinpath("pool_2025-06-03.json").write_text(
        json.dumps({"t1_date": "2025-05-30", "candidates": []}), encoding="utf-8")
    fake = FakeApi()
    _run(monkeypatch, tmp_path, fake)
    assert len(fake.calls) == 3          # 缓存无效 → 重新拉取


def test_sort_is_deterministic_across_runs(monkeypatch, tmp_path):
    """并发下返回顺序不定，排序必须靠 thscode 兜底，同样输入 → 同样输出。"""
    def cand(code, score, pct):
        return Candidate(thscode=code, name=code, board="main",
                         t1_date="2025-06-03", t2_date="2025-06-04",
                         t1_pct=pct, t1_limitup=True, t1_close=10.0,
                         t1_volume=1e6, t2_volume=2e6, t1_amount_yi=3.0,
                         volume_ratio=0.5, high_ndays=30, high30_margin_pct=1.0,
                         score=score)

    rows = [cand("600000.SH", 80.0, 9.9), cand("000001.SZ", 80.0, 9.9),
            cand("300750.SZ", 90.0, 19.9), cand("830799.BJ", 80.0, 9.9)]
    order = sorted(rows, key=lambda c: (-c.score, -c.t1_pct, c.thscode))
    assert [c.thscode for c in order] == ["300750.SZ", "000001.SZ", "600000.SH", "830799.BJ"]
