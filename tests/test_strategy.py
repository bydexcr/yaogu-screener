# -*- coding: utf-8 -*-
"""
strategy.py 的金标用例（纯函数，无 IO，无网络）

运行：python -m pytest -q
"""
import datetime as dt
import json

import pytest

import strategy as S
from strategy import Candidate, DailyBar


# ---------------------------------------------------------------- 构造工具
def make_bars(n=40, close=10.0, volume=2_000_000.0, amount=1_000_000_000.0):
    """n 根平盘日线（升序、日期唯一），足够覆盖 high_ndays=30 的窗口。"""
    base = dt.date(2025, 11, 1)
    return [
        DailyBar(date=(base + dt.timedelta(days=i)).isoformat(), open=close, high=close,
                 low=close, close=close, volume=volume, amount=amount)
        for i in range(n)
    ]


def dates_of(bars):
    """bars 升序：最后一根是 T-1，倒数第二根是 T-2。"""
    return bars[-1].date, bars[-2].date


CFG = {"t1_gain_min_pct": 8.0, "t1_volume_lt_t2": True, "high_ndays": 30, "t1_amount_min_yi": 5.0}


def eval_stock(bars, thscode="600000.SH", name="浦发银行", cfg=None, **kw):
    t1, t2 = dates_of(bars)
    return S.evaluate_stock(bars, thscode, name, t1, t2, cfg or CFG, **kw)


# ---------------------------------------------------------------- 代码 / 板块工具
def test_split_thscode():
    assert S.split_thscode("600000.SH") == ("600000", "SH")
    assert S.split_thscode("000001") == ("000001", "")


@pytest.mark.parametrize("code,expect", [
    ("830799.BJ", True),    # 北交所
    ("920001.BJ", True),
    ("430047.BJ", True),
    ("600000.SH", False),
    ("300750.SZ", False),
])
def test_is_bj(code, expect):
    assert S.is_bj(code) is expect


@pytest.mark.parametrize("code", [
    "430047", "830799", "870204", "880101",      # 4/8 开头：老北交所代码
    "430047.BJ", "830799.BJ", "870204.BJ", "880101.BJ",
    "920001", "920999", "920001.BJ",             # 920 段：新北交所代码
])
def test_is_bj_accepts_bare_bse_codes(code):
    """接口不给 .BJ 后缀时，靠代码段也要认得出北交所（否则会被当主板 10% 涨幅）。"""
    assert S.is_bj(code) is True
    assert S.board_key(code) == "bj"


@pytest.mark.parametrize("code", [
    "600000", "600519", "601318", "603288", "605599",   # 60 开头是沪市主板，不能误判
    "000001", "002594", "003816",                       # 00 开头深市主板 / 中小板
    "300750", "301001", "688111", "689009", "510300", "900901",
])
def test_is_bj_rejects_non_bse_codes(code):
    assert S.is_bj(code) is False
    assert S.board_key(code) != "bj"


@pytest.mark.parametrize("name,expect", [
    ("*ST美谷", True),
    ("ST中珠", True),
    ("st小写", True),
    ("贵州茅台", False),
    ("", False),
    (None, False),
])
def test_is_st(name, expect):
    assert S.is_st(name) is expect


@pytest.mark.parametrize("code,expect", [
    ("300750.SZ", "gem"),
    ("301001.SZ", "gem"),
    ("688111.SH", "star"),
    ("600000.SH", "main"),
    ("000001.SZ", "main"),
    ("002594.SZ", "main"),
    ("003816.SZ", "main"),
    ("605599.SH", "main"),
    ("830799.BJ", "bj"),
    ("430047.BJ", "bj"),
    ("920001", "bj"),
    ("900901.SH", "other"),
])
def test_board_key(code, expect):
    assert S.board_key(code) == expect


def test_board_key_ignores_suffix_noise():
    """带交易所后缀、大小写不一致时结论必须一致。"""
    assert S.board_key("600000.sh") == "main"
    assert S.board_key("300750.sz") == "gem"
    assert S.board_key("830799.bj") == "bj"


def test_is_limit_up_like_by_board():
    assert S.is_limit_up_like(9.8, "600000.SH") is True      # 主板 10%
    assert S.is_limit_up_like(9.7, "600000.SH") is False
    assert S.is_limit_up_like(19.7, "300750.SZ") is True     # 创业板 20%
    assert S.is_limit_up_like(10.0, "300750.SZ") is False


def test_is_limit_up_like_bj_uses_30pct():
    """北交所涨跌幅 30%：+12% 在北交所不是涨停，在主板才是。"""
    assert S.is_limit_up_like(29.7, "830799.BJ") is True
    assert S.is_limit_up_like(29.6, "830799.BJ") is False
    assert S.is_limit_up_like(12.0, "830799.BJ") is False
    assert S.is_limit_up_like(12.0, "920001") is False
    # 同样的涨幅，主板口径下算涨停 → 说明板块判定真的生效了
    assert S.is_limit_up_like(12.0, "600000.SH") is True


# ---------------------------------------------------------------- C1 / C3 原子函数
def test_check_c1_returns_pct():
    b1 = DailyBar("2026-01-02", 1, 1, 1, 11.0, 1, 1)
    b2 = DailyBar("2026-01-01", 1, 1, 1, 10.0, 1, 1)
    assert S.check_c1(b1, b2, 8.0) == pytest.approx(10.0)


def test_check_c1_guards_zero_prev_close():
    b1 = DailyBar("2026-01-02", 1, 1, 1, 11.0, 1, 1)
    b2 = DailyBar("2026-01-01", 1, 1, 1, 0.0, 1, 1)
    assert S.check_c1(b1, b2, 8.0) == float("-inf")


def test_is_new_high_is_strict():
    assert S.is_new_high(10.01, [10.0, 9.0]) is True
    assert S.is_new_high(10.0, [10.0, 9.0]) is False      # 等于不算新高
    assert S.is_new_high(99.0, []) is False               # 无历史 → 不判


# ---------------------------------------------------------------- C1~C4 组合（evaluate_stock）
def test_evaluate_stock_happy_path():
    bars = make_bars()
    bars[-1].close = 11.0                      # T-1 +10%（> 8%）
    bars[-1].volume = 1_000_000.0              # 缩量
    bars[-1].amount = 600_000_000.0            # 6 亿 ≥ 5 亿
    c = eval_stock(bars)
    assert c is not None
    assert c.thscode == "600000.SH"
    assert c.board == "main"
    assert c.t1_pct == pytest.approx(10.0, abs=0.01)
    assert c.volume_ratio == pytest.approx(0.5, abs=0.001)
    assert c.t1_amount_yi == pytest.approx(6.0, abs=0.01)
    assert c.t1_limitup is True
    assert c.high30_margin_pct == pytest.approx(10.0, abs=0.01)


def test_c1_threshold_is_exclusive():
    """C1 要求「涨幅 > 8%」，正好 +8.0% 必须被排除。

    注意 10.8/10.0 在二进制浮点下是 8.000000000000007%，故实现里带 1e-9 容差。
    """
    bars = make_bars()
    bars[-1].close = 10.8                      # 恰好 +8.0%
    bars[-1].volume = 1_000_000.0
    bars[-1].amount = 600_000_000.0
    assert eval_stock(bars) is None


def test_c1_accepts_slightly_above_threshold():
    """8.01% 这种真实高于阈值的不该被容差误杀。"""
    bars = make_bars()
    bars[-1].close = 10.801                    # +8.01%
    bars[-1].volume = 1_000_000.0
    bars[-1].amount = 600_000_000.0
    c = eval_stock(bars)
    assert c is not None
    assert c.t1_pct >= 8.0


def test_c2_requires_volume_shrink():
    bars = make_bars()
    bars[-1].close = 11.0
    bars[-1].volume = 3_000_000.0              # 放量 > T-2
    bars[-1].amount = 600_000_000.0
    assert eval_stock(bars) is None


def test_c2_can_be_disabled():
    bars = make_bars()
    bars[-1].close = 11.0
    bars[-1].volume = 3_000_000.0
    bars[-1].amount = 600_000_000.0
    cfg = {**CFG, "t1_volume_lt_t2": False}
    assert eval_stock(bars, cfg=cfg) is not None


def test_c3_requires_new_high():
    bars = make_bars()
    bars[20].close = 10.6                      # 历史最高收盘 10.6
    bars[-2].close = 9.4
    bars[-1].close = 10.5                      # 涨幅 +11.7% 但没创 30 日新高
    bars[-1].volume = 1_000_000.0
    bars[-1].amount = 600_000_000.0
    assert eval_stock(bars) is None


def test_only_main_board_rejects_gem():
    """only_main_board=True：创业板(300)同样的形态也要被剔除，主板照常通过。"""
    cfg = {**CFG, "only_main_board": True}
    for code, expect in (("300001.SZ", None), ("600001.SH", "pass")):
        bars = make_bars()
        bars[-1].close = 11.0
        bars[-1].volume = 1_000_000.0
        bars[-1].amount = 600_000_000.0
        got = eval_stock(bars, thscode=code, cfg=cfg)
        if expect is None:
            assert got is None
        else:
            assert got is not None and got.board == "main"


def test_only_main_board_off_keeps_gem():
    bars = make_bars()
    bars[-1].close = 11.0
    bars[-1].volume = 1_000_000.0
    bars[-1].amount = 600_000_000.0
    assert eval_stock(bars, thscode="300001.SZ", cfg={**CFG, "only_main_board": False}) is not None


def _no_new_high_bars():
    bars = make_bars()
    bars[20].close = 10.6                      # 历史最高收盘 10.6
    bars[-2].close = 9.4
    bars[-1].close = 10.5                      # +11.7%，但没创 30 日新高
    bars[-1].volume = 1_000_000.0
    bars[-1].amount = 600_000_000.0
    return bars


def test_require_new_high_false_accepts_non_new_high():
    """require_new_high=False：未创 30 日新高也能进候选（降级为评分项）。"""
    cand = eval_stock(_no_new_high_bars(), cfg={**CFG, "require_new_high": False})
    assert cand is not None
    assert cand.high30_margin_pct <= 0


def test_require_new_high_true_rejects_non_new_high():
    assert eval_stock(_no_new_high_bars(), cfg={**CFG, "require_new_high": True}) is None


def test_score_rewards_new_high():
    """创 30 日新高仍进评分：同条件下新高候选分数至少高 5 分。"""
    cfg = {**CFG, "require_new_high": False}
    hi_bars = make_bars()
    hi_bars[-1].close = 11.0
    hi_bars[-1].volume = 1_000_000.0
    hi_bars[-1].amount = 600_000_000.0
    hi = eval_stock(hi_bars, cfg=cfg)
    lo = eval_stock(_no_new_high_bars(), cfg=cfg)
    assert hi is not None and lo is not None
    S._score_candidates([hi])
    S._score_candidates([lo])
    assert hi.score >= lo.score + 5.0


def test_c4_requires_min_amount():
    bars = make_bars()
    bars[-1].close = 11.0
    bars[-1].volume = 1_000_000.0
    bars[-1].amount = 400_000_000.0            # 4 亿 < 5 亿
    assert eval_stock(bars) is None


def test_insufficient_history():
    bars = make_bars(n=20)                     # 不足 high_ndays + 1
    bars[-1].close = 11.0
    bars[-1].volume = 1_000_000.0
    bars[-1].amount = 600_000_000.0
    assert eval_stock(bars) is None


def test_missing_trade_dates():
    bars = make_bars()
    bars[-1].close = 11.0
    bars[-1].volume = 1_000_000.0
    bars[-1].amount = 600_000_000.0
    assert S.evaluate_stock(bars, "600000.SH", "浦发银行", "2099-01-01", "2099-01-02", CFG) is None


def test_filters_st_and_bj():
    bars = make_bars()
    bars[-1].close = 11.0
    bars[-1].volume = 1_000_000.0
    bars[-1].amount = 600_000_000.0
    assert eval_stock(bars, name="*ST美谷") is None
    assert eval_stock(bars, thscode="830799.BJ") is None
    # 关掉过滤就能通过
    assert eval_stock(bars, name="*ST美谷", exclude_st=False) is not None


# ---------------------------------------------------------------- C5 与日内状态机
def test_apply_cond5_in_range():
    c = eval_stock(_happy_bars())
    assert S.apply_cond5(c, open_price=9.2, prev_close=10.0, last_price=9.3, last_pct=-7.0, cfg_strategy=CFG) is True
    assert c.open_pct == pytest.approx(-8.0, abs=0.01)
    assert c.hit is True


def test_apply_cond5_out_of_range():
    c = eval_stock(_happy_bars())
    assert S.apply_cond5(c, open_price=9.9, prev_close=10.0, last_price=9.9, last_pct=-1.0, cfg_strategy=CFG) is False
    assert c.hit is False


def test_apply_cond5_needs_prev_close():
    c = eval_stock(_happy_bars())
    assert S.apply_cond5(c, open_price=9.2, prev_close=None, last_price=9.2, last_pct=-8.0, cfg_strategy=CFG) is False
    assert S.apply_cond5(c, open_price=None, prev_close=10.0, last_price=None, last_pct=None, cfg_strategy=CFG) is False


def test_intraday_flags_confirm_and_broken():
    # 未命中 → 一律 False
    assert S.intraday_flags(None, False, 9.2, 9.9, -1.0) == (False, False)
    # 收复开盘价 → 承接确认
    assert S.intraday_flags(None, True, 9.2, 9.3, -7.0) == (True, False)
    # 跌破开盘价 3% → 走弱
    assert S.intraday_flags(None, True, 9.2, 8.9, -11.0) == (False, True)
    # 逼近昨收 -9% → 走弱（即使还在开盘价附近）
    assert S.intraday_flags(None, True, 9.2, 9.19, -9.1) == (False, True)


def test_intraday_flags_custom_threshold():
    cfg = {"broken_below_open_pct": -1.0, "broken_below_prev_pct": -20.0}
    assert S.intraday_flags(cfg, True, 9.2, 9.05, -9.5) == (False, True)


def test_intraday_flags_missing_price():
    assert S.intraday_flags(None, True, None, 9.0, -9.0) == (False, False)


# ---------------------------------------------------------------- 评分
def _happy_bars():
    bars = make_bars()
    bars[-1].close = 11.0
    bars[-1].volume = 1_000_000.0
    bars[-1].amount = 600_000_000.0
    return bars


def _cand(**kw):
    base = dict(thscode="600000.SH", name="X", board="main", t1_date="2026-01-02", t2_date="2026-01-01",
                t1_pct=10.0, t1_limitup=True, t1_close=11.0, t1_volume=1e6, t2_volume=2e6,
                t1_amount_yi=5.0, volume_ratio=0.5, high_ndays=30, high30_margin_pct=10.0)
    base.update(kw)
    return Candidate(**base)


def test_score_monotonic_in_board_count():
    a = _cand(continue_day_cnt=1)
    b = _cand(continue_day_cnt=3)
    S._score_candidates([a, b])
    assert b.score > a.score


def test_score_monotonic_in_shrink():
    looser = _cand(volume_ratio=0.9)
    tighter = _cand(volume_ratio=0.2)
    S._score_candidates([looser, tighter])
    assert tighter.score > looser.score


def test_score_rewards_early_limit_up():
    late = _cand(limit_up_time="14:30")
    early = _cand(limit_up_time="09:30")
    S._score_candidates([late, early])
    assert early.score > late.score


def test_score_is_capped_at_100():
    c = _cand(continue_day_cnt=9, volume_ratio=0.0, t1_amount_yi=50.0, limit_up_time="09:25")
    S._score_candidates([c])
    assert 0.0 <= c.score <= 100.0
    assert c.score == 100.0


def test_score_handles_inf_volume_ratio():
    """volume_ratio=inf（T-2 量为 0 的兜底值）不能让评分崩掉。"""
    c = _cand(volume_ratio=float("inf"))
    S._score_candidates([c])
    assert 0.0 <= c.score <= 100.0


# ---------------------------------------------------------------- 涨停池合并
def test_enrich_with_limit_pool():
    c = _cand()
    lu = {"600000.SH": {"continue_day_cnt": 2, "continue_day_text": "2连板",
                        "limit_up_time": "09:31", "limit_up_reason": "机器人+算力",
                        "seal_money": 230_000_000}}
    S.enrich_with_limit_pool([c], lu)
    assert c.continue_day_cnt == 2
    assert c.continue_text == "2连板"
    assert c.limit_up_time == "09:31"
    assert c.limit_up_reason == "机器人+算力"
    assert c.seal_money_yi == pytest.approx(2.3, abs=0.01)
    assert c.score > 0


def test_enrich_without_pool_entry_keeps_defaults():
    c = _cand()
    S.enrich_with_limit_pool([c], {})
    assert c.continue_day_cnt is None
    assert c.score > 0          # 仍会算分


# ---------------------------------------------------------------- 序列化兜底（P2-7 回归）
def test_to_dict_converts_non_finite_floats():
    c = _cand(volume_ratio=float("inf"), high30_margin_pct=float("nan"),
              t1_pct=float("-inf"))
    d = c.to_dict()
    assert d["volume_ratio"] is None
    assert d["high30_margin_pct"] is None
    assert d["t1_pct"] is None
    # 必须能被合法 JSON 序列化（前端 JSON.parse 才不会炸）
    json.dumps(d, allow_nan=False)


def test_to_dict_keeps_normal_values():
    c = _cand(volume_ratio=0.42)
    d = c.to_dict()
    assert d["volume_ratio"] == pytest.approx(0.42)
    assert d["thscode"] == "600000.SH"
