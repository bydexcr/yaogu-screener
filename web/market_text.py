# -*- coding: utf-8 -*-
"""
market_text.py —— 市场全景页的「派生结论」文案

把 /api/market 的数字翻成人话（今日一句 / 结构句 / 涨跌分布结论 / 情绪标签）。
纯函数、不取数、不写盘，方便单元测试；前端只负责展示。

口径红线：
  * 只陈述能由 breadth / limits / sectors 直接算出来的事实，
    不写"缩量""放量""主力进场"这类没有基准数据支撑的判断。
  * 涨跌方向用 A 股口径：红涨绿跌（颜色由前端决定，这里只给文字）。
"""
from __future__ import annotations

from typing import Dict, List, Optional


def _f(v) -> Optional[float]:
    try:
        if v is None or v == "":
            return None
        x = float(v)
        return x if x == x and abs(x) != float("inf") else None
    except (TypeError, ValueError):
        return None


def _amt(v) -> str:
    v = _f(v) or 0.0
    return "%.2f 万亿" % (v / 1e12) if v >= 1e12 else "%.0f 亿" % (v / 1e8)


def _pct(v, d: int = 1, sign: bool = False) -> str:
    x = _f(v)
    if x is None:
        return "—"
    return ("%+.*f%%" if sign else "%.*f%%") % (d, x)


def mood(up_ratio: Optional[float]) -> str:
    """情绪标签：只按上涨家数占比切三档。"""
    r = _f(up_ratio)
    if r is None:
        return "—"
    if r < 30:
        return "情绪偏冷"
    if r < 55:
        return "情绪温和"
    return "情绪偏热"


def distribution(breadth: Dict) -> str:
    """涨跌分布结论：最大那桶 + 两侧极端（跌超 7% / 涨超 7%）。"""
    buckets: List[dict] = list(breadth.get("buckets") or [])
    total = _f(breadth.get("total")) or 0
    if not buckets or total <= 0:
        return ""
    if sum((b.get("count") or 0) for b in buckets) <= 0:
        return ""            # 盘前/未开盘：全 0 时不要输出"0 只落在…"这种误导文案
    dom = max(buckets, key=lambda b: b.get("count") or 0)
    big_down = sum((b.get("count") or 0) for b in buckets[:2])
    big_up = sum((b.get("count") or 0) for b in buckets[-2:])
    share = (dom.get("count") or 0) / total * 100
    return ("%d 只落在 %s，占全市场 %.1f%%；跌超 7%% 的 %d 只，涨超 7%% 的 %d 只。"
            % (dom.get("count") or 0, dom.get("label") or "—", share, big_down, big_up))


def _leading(board: List[dict], n: int = 3) -> List[str]:
    return [b.get("name") for b in (board or [])[:n] if b.get("name")]


def _defensive(board: List[dict], n: int = 2, floor: int = 5) -> List[dict]:
    """抗跌/强势结构：成分 >= floor 只、且上涨占比最高的板块。"""
    cand = [b for b in (board or []) if (_f(b.get("memberCount")) or 0) >= floor]
    return sorted(cand, key=lambda b: -((b.get("upCount") or 0) / max(1, b.get("memberCount") or 1)))[:n]


def structure(sectors: Dict) -> str:
    """板块结构句。"""
    boards = (sectors or {}).get("boards", {}).get("l1") or []
    if not boards or sum((b.get("upCount") or 0) for b in boards) <= 0:
        return ""            # 盘前：板块还没有涨跌数据
    top = _defensive(boards)
    if not top:
        return ""
    names = "、".join(b["name"] for b in top)
    ratio = (top[0].get("upCount") or 0) / max(1, top[0].get("memberCount") or 1) * 100
    mono = [b for b in boards if (b.get("memberCount") or 0) >= 5
            and (b.get("upCount") or 0) == (b.get("memberCount") or 0)]
    if mono:
        return "结构：%s 全部上涨，资金明显偏向这几个方向" % "、".join(
            "%s %d 只" % (b["name"], b["memberCount"]) for b in mono[:2])
    return "结构：%s 相对占优（上涨占比 %.0f%%），板块内部分化明显" % (names, ratio)


def one_sentence(market: Dict) -> str:
    """今日一句：按涨跌方向分三种句式，只用可核验的数字。"""
    b = market.get("breadth") or {}
    lim = market.get("limits") or {}
    boards = (market.get("sectors") or {}).get("boards", {}).get("l1") or []
    lead = _leading(boards, 3)
    up_ratio = _f(b.get("upRatio"))
    total = _f(b.get("total")) or 0
    avg = b.get("avg")
    seal = _f(lim.get("sealRate"))
    lu, ld = lim.get("limitUpCount") or 0, lim.get("limitDownCount") or 0
    amt = _amt(b.get("turnover"))
    if not lead or up_ratio is None or total <= 0:
        return ""

    down_pct = b.get("down", 0) / total * 100 if total else 0
    up_pct = up_ratio
    tail = ("涨停 %d 只对跌停 %d 只、封板率 %s" % (lu, ld, _pct(seal)))

    if up_ratio < 35:
        return ("资金只在 %s 这类方向里避险；%.0f%% 的个股下跌、平均 %s，成交额仍有 %s——"
                "%s，是普跌，不是恐慌出逃。" % ("、".join(lead), down_pct, _pct(avg, 2, True), amt, tail))
    if up_ratio > 65:
        return ("资金集中在 %s 这类方向做多；%.0f%% 的个股上涨、平均 %s，成交额 %s——"
                "%s，是普涨行情。" % ("、".join(lead), up_pct, _pct(avg, 2, True), amt, tail))
    return ("涨跌家数 %s 对 %s，市场明显分化；%s 领涨，平均涨跌 %s，成交额 %s——%s。"
            % (b.get("up", 0), b.get("down", 0), "、".join(lead), _pct(avg, 2, True), amt, tail))


def summarize(market: Dict) -> Dict[str, str]:
    """一次性给出页面上四段派生文案。"""
    b = market.get("breadth") or {}
    return {
        "mood": mood(b.get("upRatio")),
        "oneSentence": one_sentence(market),
        "structure": structure(market.get("sectors") or {}),
        "distribution": distribution(b),
    }
