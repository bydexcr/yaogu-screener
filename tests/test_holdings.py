# -*- coding: utf-8 -*-
"""持仓深度分析（web/holdings.py）单元测试

覆盖：
  · 15:00 时间闸门（盘中不生成）
  · 只取「已持有 + 已填成本价」的自选股
  · 浮盈计算、加权浮盈、最好/最差、需关注计数
  · 规则化观察条目的方向（盈利/亏损、站上/跌破 20 日线、放量/缩量、风险项）
  · 单只分析失败不影响其他持仓
"""
import datetime as dt
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "web"))

import holdings as H     # noqa: E402


class FakeStore:
    def __init__(self, items):
        self._items = items

    def items(self):
        return list(self._items)


HELD = [
    {"thscode": "600519.SH", "name": "贵州茅台", "held": True, "cost": 1500.0},
    {"thscode": "000001.SZ", "name": "平安银行", "held": True, "cost": 10.0},
    {"thscode": "300750.SZ", "name": "宁德时代", "held": False, "cost": None},
    {"thscode": "002119.SZ", "name": "康强电子", "held": True, "cost": None},
]


def fake_analysis(code, **over):
    """构造一份接近真实结构的分析结果。"""
    base = {
        "ok": True,
        "meta": {"tradeDate": "2026-11-24"},
        "quote": {"thscode": code, "name": {"600519.SH": "贵州茅台", "000001.SZ": "平安银行"}.get(code, code),
                  "lastPrice": 1600.0 if code == "600519.SH" else 9.0,
                  "changePct": 1.2, "turnover": 3.2e9, "limit": {"label": ""}},
        "scores": {"overall": 60.0, "trend": 55.0, "capital": 70.0, "quality": 50.0, "valuation": 40.0},
        "trendTech": {"ma5": 1550.0, "ma20": 1500.0, "ma60": 1400.0, "state": "上升",
                      "ret5": 3.0, "ret20": 8.0, "support20": 1400.0, "resistance20": 1650.0,
                      "high60": 1700.0, "low60": 1200.0, "maxDrawdown60": -12.0},
        "capital": {"volRatio5": 1.1, "amountRatio5v20": 1.05, "closePosition": 80.0, "turnoverRate": 2.0},
        "narrative": {"headline": "headline", "grade": "C（数据面中性偏强）",
                      "fiveDayText": "近 5 日 +3%", "highlights": ["亮点1"], "risks": ["风险1"],
                      "riskText": "17 项检查中 2 项触发风险阈值。"},
        "riskMatrix": {"rows": [{"item": "估值偏高", "status": "alert", "value": "91%"},
                                {"item": "波动率", "status": "watch", "value": "50%"},
                                {"item": "现金流", "status": "ok", "value": "1.1"}]},
    }
    base.update(over)
    return base


@pytest.fixture(autouse=True)
def _clear_cache():
    """holdings 有进程级缓存（30 分钟），用例之间必须清掉，否则会读到上一条假数据。"""
    H._CACHE.clear()
    yield
    H._CACHE.clear()


AFTER = dt.datetime(2026, 11, 24, 15, 30)
BEFORE = dt.datetime(2026, 11, 24, 14, 59)


# ---------------------------------------------------------------- 时间闸门
def test_gate_before_15_is_closed():
    g = H.gate(BEFORE)
    assert g["available"] is False
    assert "15:00" in g["reason"]


def test_gate_at_15_is_open():
    assert H.gate(dt.datetime(2026, 11, 24, 15, 0))["available"] is True
    assert H.gate(AFTER)["available"] is True


def test_build_before_15_returns_unavailable():
    r = H.build(now=BEFORE, store=FakeStore(HELD), analysis_fn=fake_analysis)
    assert r["ok"] is True
    assert r["available"] is False
    assert r["items"] == []
    assert r["count"] == 2        # 仍然告诉页面有几只待分析


# ---------------------------------------------------------------- 筛选
def test_only_held_with_cost_is_analyzed():
    seen = []

    def fn(code):
        seen.append(code)
        return fake_analysis(code)

    r = H.build(now=AFTER, store=FakeStore(HELD), analysis_fn=fn)
    assert r["available"] is True
    assert r["count"] == 2
    assert sorted(seen) == ["000001.SZ", "600519.SH"]      # 未持有 / 无成本都被排除
    assert r["summary"]["held"] == 2
    assert r["summary"]["analyzed"] == 2


def test_no_held_stock_explains_why():
    r = H.build(now=AFTER, store=FakeStore([HELD[2]]), analysis_fn=fake_analysis)
    assert r["available"] is True and r["count"] == 0
    assert "已持有" in (r["reason"] or "")


# ---------------------------------------------------------------- 数值
def test_pnl_and_summary_math():
    r = H.build(now=AFTER, store=FakeStore(HELD[:2]), analysis_fn=fake_analysis)
    items = {i["thscode"]: i for i in r["items"]}
    # 茅台 1600/1500-1 = +6.67%；平安 9/10-1 = -10%
    assert items["600519.SH"]["pnl_pct"] == pytest.approx(6.67, abs=0.01)
    assert items["000001.SZ"]["pnl_pct"] == pytest.approx(-10.0, abs=0.01)
    # 加权：(6.67*1500 + -10*10) / 1510
    assert r["summary"]["weighted_pnl"] == pytest.approx(6.56, abs=0.05)
    assert r["summary"]["best"]["name"] == "贵州茅台"
    assert r["summary"]["worst"]["name"] == "平安银行"
    # 两只都需关注：一个风险项 alert，一个亏损
    assert r["summary"]["attention"] == 2


def test_trade_date_propagated():
    r = H.build(now=AFTER, store=FakeStore(HELD[:1]), analysis_fn=fake_analysis)
    assert r["trade_date"] == "2026-11-24"


# ---------------------------------------------------------------- 观察条目
def test_observations_reflect_numbers():
    r = H.build(now=AFTER, store=FakeStore(HELD[:2]), analysis_fn=fake_analysis)
    items = {i["thscode"]: i for i in r["items"]}

    mao = items["600519.SH"]
    tones = {o["text"].split("：")[0][:6]: o["tone"] for o in mao["observations"]}
    text = " ".join(o["text"] for o in mao["observations"])
    assert "盈利" in text and "站上 20 日线" in text
    assert any(o["tone"] == "good" for o in mao["observations"])

    pa = items["000001.SZ"]
    ptext = " ".join(o["text"] for o in pa["observations"])
    assert "亏损" in ptext
    assert "已跌破成本价" in ptext
    assert any(o["tone"] == "bad" for o in pa["observations"])
    # 风险矩阵里 1 条 alert → 必须出现在观察里
    assert "量化风险：1 项触发阈值" in ptext


def test_observation_flags_below_ma20_and_volume():
    held = [{"thscode": "600519.SH", "name": "贵州茅台", "held": True, "cost": 1000.0}]

    def fn(code):
        d = fake_analysis(code)
        d["quote"]["lastPrice"] = 1200.0            # 低于 20 日线 1500
        d["capital"]["volRatio5"] = 2.2             # 明显放量
        d["capital"]["closePosition"] = 15.0        # 收在低位
        return d

    r = H.build(now=AFTER, store=FakeStore(held), analysis_fn=fn)
    obs = r["items"][0]["observations"]
    text = " ".join(o["text"] for o in obs)
    assert "跌破 20 日线" in text
    assert "明显放量" in text
    assert "收在低位" in text


# ---------------------------------------------------------------- 容错
def test_single_failure_does_not_break_others():
    def fn(code):
        if code == "000001.SZ":
            raise RuntimeError("接口超时")
        return fake_analysis(code)

    r = H.build(now=AFTER, store=FakeStore(HELD[:2]), analysis_fn=fn)
    errs = [i for i in r["items"] if i.get("error")]
    oks = [i for i in r["items"] if not i.get("error")]
    assert len(errs) == 1 and "接口超时" in errs[0]["error"]
    assert len(oks) == 1
    assert r["summary"]["errors"] == 1


def test_analysis_returning_not_ok_is_reported():
    r = H.build(now=AFTER, store=FakeStore(HELD[:1]),
                analysis_fn=lambda code: {"ok": False, "error": "未找到该股票"})
    assert r["items"][0]["error"] == "未找到该股票"
    assert r["summary"]["errors"] == 1


def test_max_stocks_cap(monkeypatch):
    monkeypatch.setattr(H, "MAX_STOCKS", 2)
    many = [{"thscode": "60%04d.SH" % i, "name": "S%d" % i, "held": True, "cost": 10.0}
            for i in range(5)]
    r = H.build(now=AFTER, store=FakeStore(many), analysis_fn=fake_analysis)
    assert r["count"] == 2
    assert len(r["items"]) == 2
