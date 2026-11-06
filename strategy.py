# -*- coding: utf-8 -*-
"""
strategy.py —— 妖股低吸选股策略核心（纯逻辑，无 IO）

条件（T 为当前交易日，T-1/T-2 为往前数第 1/2 个交易日）：
  C1  T-1 涨停 或 涨幅 > t1_gain_min_pct%(默认 8.0)
  C2  T-1 成交量 < T-2 成交量
  C3  T-1 收盘价创出 high_ndays(默认 30) 日新高
  C4  T-1 成交额 >= t1_amount_min_yi 亿元(默认 5.0)
  C5  T 日开盘涨跌幅 ∈ t_open_pct_range(默认 [-8, -5]，即低开 5%~8%)

过滤：剔除 ST / 北交所
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Optional, Sequence

ST_RE = re.compile(r"ST", re.IGNORECASE)
BJ_CODE_RE = re.compile(r"^(4|8|92)\d{4}$")


# ---------------------------------------------------------------- 代码/板块工具
def split_thscode(thscode: str):
    """'600000.SH' -> ('600000', 'SH')"""
    if "." in thscode:
        code, exch = thscode.rsplit(".", 1)
        return code, exch.upper()
    return thscode, ""


def is_bj(thscode: str) -> bool:
    code, exch = split_thscode(thscode)
    if exch == "BJ":
        return True
    return bool(BJ_CODE_RE.match(code)) and exch != "SH"


def is_st(name: Optional[str]) -> bool:
    if not name:
        return False
    return bool(ST_RE.search(name))


def board_key(thscode: str) -> str:
    """返回板块：gem(创业板) / star(科创板) / main(主板) / bj / other"""
    code, exch = split_thscode(thscode)
    if is_bj(thscode):
        return "bj"
    if code.startswith(("300", "301")):
        return "gem"
    if code.startswith(("688", "689")):
        return "star"
    if code.startswith(("60", "00", "001", "002", "003", "601", "603", "605")):
        return "main"
    return "other"


def is_limit_up_like(pct_pct: float, thscode: str) -> bool:
    """按板块粗略判断是否(接近)涨停，仅用于展示标签，不参与筛选。"""
    b = board_key(thscode)
    if b == "gem" or b == "star":
        return pct_pct >= 19.7
    if b == "main":
        return pct_pct >= 9.8
    return pct_pct >= 9.8


# ---------------------------------------------------------------- 数据模型
@dataclass
class DailyBar:
    date: str          # YYYY-MM-DD
    open: float
    high: float
    low: float
    close: float
    volume: float      # 股
    amount: float      # 元


@dataclass
class Candidate:
    """通过 C1~C4（T-1 静态条件）的候选股"""
    thscode: str
    name: str
    board: str
    t1_date: str
    t2_date: str
    t1_pct: float            # T-1 涨幅 %
    t1_limitup: bool         # 展示用：是否接近涨停
    t1_close: float
    t1_volume: float
    t2_volume: float
    t1_amount_yi: float
    volume_ratio: float      # T-1量 / T-2量
    high_ndays: int
    high30_margin_pct: float # T-1收盘较前30日最高收盘高出 %
    # T-1 涨停质量标签（P1：来自同花顺涨停池，仅在取到数据时填充）
    continue_day_cnt: Optional[int] = None
    continue_text: str = ""
    limit_up_time: str = ""
    limit_up_reason: str = ""
    seal_money_yi: Optional[float] = None
    # 综合评分（P1：连板/缩量/封板时间/成交额）
    score: float = 0.0
    # 日内状态机（P2：hit=低开命中 / confirm=承接确认 / broken=走弱预警）
    sig: str = ""
    sig_since: Optional[str] = None
    # 命中区间归属（P4副栏：main=低开5~8%主栏 / deep=深水低吸7~10% / 空=未命中）
    zone: str = ""
    # 动态部分（每 30s 刷新）
    open_price: Optional[float] = None
    prev_close: Optional[float] = None
    open_pct: Optional[float] = None
    last_price: Optional[float] = None
    last_pct: Optional[float] = None
    hit: bool = False        # C5 命中
    hit_since: Optional[str] = None
    alert_round: int = 0

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


def enrich_with_limit_pool(cands: Sequence[Candidate], lu_map: dict) -> None:
    """把同花顺 T-1 涨停池明细合并进候选并计算综合评分（就地修改）。"""
    for c in cands:
        m = lu_map.get(c.thscode)
        if m:
            c.continue_day_cnt = m.get("continue_day_cnt")
            c.continue_text = m.get("continue_day_text") or ""
            c.limit_up_time = m.get("limit_up_time") or ""
            c.limit_up_reason = m.get("limit_up_reason") or ""
            sm = m.get("seal_money")
            c.seal_money_yi = round(sm / 1e8, 2) if isinstance(sm, (int, float)) else None
    _score_candidates(cands)


def _score_candidates(cands: Sequence[Candidate]) -> None:
    """评分(0~100，仅排序参考)：连板高度 + 缩量程度 + 封板早晚 + 成交额规模。"""
    for c in cands:
        s = 30.0
        if c.continue_day_cnt:                       # 首板12分，每多一板再加
            s += min(max(c.continue_day_cnt, 1), 4) * 12.0
        elif not c.t1_limitup:
            s += 4.0                                 # 涨幅>8%但非涨停
        shrink = 1.0 - min(max(c.volume_ratio, 0.0), 1.0)   # 缩得越狠分越高
        s += shrink * 40.0
        s += min(max(c.t1_amount_yi - 5.0, 0.0) / 10.0, 1.0) * 10.0   # 5亿起步，超15亿满分
        if c.limit_up_time:
            hm = c.limit_up_time
            if hm <= "09:35":
                s += 8.0
            elif hm <= "10:30":
                s += 5.0
            elif hm <= "13:00":
                s += 2.0
        c.score = round(max(0.0, min(s, 100.0)), 1)


@dataclass
class CycleResult:
    ts: str
    t_date: str
    t1_date: str
    t2_date: str
    pool_size: int
    hit_list: list = field(default_factory=list)   # 命中的 candidate dict
    pool_list: list = field(default_factory=list)  # 全部候选 dict（已带动态数据）
    new_hits: list = field(default_factory=list)   # 本轮新命中（主栏）
    deep_new: list = field(default_factory=list)   # 本轮新命中（深水副栏）
    errors: list = field(default_factory=list)


# ---------------------------------------------------------------- 策略判定
def check_c1(bar_t1: DailyBar, bar_t2: DailyBar, min_gain_pct: float) -> float:
    """返回 T-1 涨幅%；>min_gain_pct(默认8) 即满足「涨停或涨幅大于8%」。"""
    if bar_t2.close <= 0:
        return float("-inf")
    return (bar_t1.close / bar_t2.close - 1.0) * 100.0


def is_new_high(close_t1: float, prev_closes: Sequence[float]) -> bool:
    """T-1 收盘价须严格高于此前 high_ndays 根K线的最高收盘（创 N 日新高）。"""
    if len(prev_closes) == 0:
        return False
    prev_high = max(prev_closes)
    return close_t1 > prev_high


def evaluate_stock(bars: Sequence[DailyBar], thscode: str, name: str,
                   t1_date: str, t2_date: str, cfg_strategy: dict,
                   exclude_st: bool = True, exclude_bj: bool = True) -> Optional[Candidate]:
    """对单只股票做 C1~C4 判定。bars 为该股升序日线（须覆盖 T-1 往前至少 high_ndays 个交易日）。
    返回通过者(Candidate)或 None。"""
    if exclude_bj and is_bj(thscode):
        return None
    if exclude_st and is_st(name):
        return None

    high_ndays = int(cfg_strategy.get("high_ndays", 30))
    min_gain = float(cfg_strategy.get("t1_gain_min_pct", 8.0))
    amount_min = float(cfg_strategy.get("t1_amount_min_yi", 5.0)) * 1e8
    vol_lt = bool(cfg_strategy.get("t1_volume_lt_t2", True))

    if len(bars) <= high_ndays:
        return None

    # 定位 T-1 / T-2
    i1 = None
    i2 = None
    for idx, b in enumerate(bars):
        if b.date == t1_date:
            i1 = idx
        if b.date == t2_date:
            i2 = idx
        if i1 is not None and i2 is not None:
            break
    if i1 is None or i2 is None or i1 < high_ndays or i2 < 0:
        return None  # 数据不足或非交易日

    b1 = bars[i1]
    b2 = bars[i2]

    # C1: T-1 涨停或涨幅 > 8%
    pct1 = check_c1(b1, b2, min_gain)
    if pct1 <= min_gain:
        return None

    # C2: T-1 量 < T-2 量
    if vol_lt and not (b1.volume < b2.volume):
        return None

    # C3: T-1 收盘创 N 日新高
    prev_closes = [b.close for b in bars[i1 - high_ndays: i1]]
    if not is_new_high(b1.close, prev_closes):
        return None

    # C4: T-1 成交额 >= 阈值
    if b1.amount < amount_min:
        return None

    prev_high = max(prev_closes)
    margin = (b1.close / prev_high - 1.0) * 100.0 if prev_high > 0 else 0.0
    cand = Candidate(
        thscode=thscode,
        name=name or thscode,
        board=board_key(thscode),
        t1_date=t1_date,
        t2_date=t2_date,
        t1_pct=round(pct1, 2),
        t1_limitup=is_limit_up_like(pct1, thscode),
        t1_close=round(b1.close, 2),
        t1_volume=b1.volume,
        t2_volume=b2.volume,
        t1_amount_yi=round(b1.amount / 1e8, 2),
        volume_ratio=round(b1.volume / b2.volume, 3) if b2.volume > 0 else float("inf"),
        high_ndays=high_ndays,
        high30_margin_pct=round(margin, 2),
    )
    return cand


def apply_cond5(cand: Candidate, open_price: Optional[float],
                prev_close: Optional[float], last_price: Optional[float],
                last_pct: Optional[float], cfg_strategy: dict) -> bool:
    """C5：T 日开盘涨跌幅 ∈ [lo, hi]，返回是否命中。"""
    lo, hi = cfg_strategy.get("t_open_pct_range", [-8.0, -5.0])
    cand.open_price = open_price
    cand.prev_close = prev_close
    cand.last_price = last_price
    cand.last_pct = last_pct
    cand.open_pct = None
    if open_price is not None and prev_close and prev_close > 0:
        cand.open_pct = round((open_price / prev_close - 1.0) * 100.0, 2)
        cand.hit = lo <= cand.open_pct <= hi
    else:
        cand.hit = False
    return cand.hit


DEFAULT_INTRADAY_CFG = {
    "confirm_above_open": True,     # 现价 >= 开盘价 视为承接确认
    "broken_below_open_pct": -3.0,  # 现价较开盘价再跌超过 3% → 走弱预警
    "broken_below_prev_pct": -9.0,  # 现价较昨收跌破 -9%（近跌停）→ 走弱预警
}


def intraday_flags(cfg_intraday: Optional[dict], hit: bool,
                   open_price: Optional[float], last_price: Optional[float],
                   last_pct: Optional[float]) -> tuple:
    """P2 日内状态机判定（纯函数，返回 (confirmed, broken)）。
    仅对 C5 命中股生效；承接确认默认=现价收复开盘价；走弱=跌破开盘价X%或逼近昨收-9%。"""
    c = {**DEFAULT_INTRADAY_CFG, **(cfg_intraday or {})}
    if not hit or last_price is None or open_price is None or last_pct is None:
        return False, False
    confirmed = bool(c.get("confirm_above_open", True)) and last_price >= open_price
    broken = (last_pct <= float(c.get("broken_below_prev_pct", -9.0))
              or last_price < open_price * (1.0 + float(c.get("broken_below_open_pct", -3.0)) / 100.0))
    return bool(confirmed), bool(broken)
