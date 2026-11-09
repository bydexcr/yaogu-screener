# -*- coding: utf-8 -*-
"""
stock_market.py —— 首页「市场全景」：市场宽度 / 板块排行 / 涨跌停与连板梯队 / 热门榜
与 PC 版 stock-analyzer/lib/market.js 同构。
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import stock_data as sd

_n = sd._num
_r = sd._round


def _avg(vals):
    vs = [v for v in vals if v is not None]
    return sum(vs) / len(vs) if vs else None


def _median(vals):
    vs = sorted(v for v in vals if v is not None)
    if not vs:
        return None
    n = len(vs)
    return vs[n // 2] if n % 2 else (vs[n // 2 - 1] + vs[n // 2]) / 2


# ------------------------------------------------------------------ 市场宽度
def breadth() -> Dict[str, Any]:
    market = sd.market_snapshot_all()
    rows = market["rows"]
    up = down = flat = 0
    turnover = 0.0
    changes: List[float] = []
    buckets = [
        {"label": "≤-9.8%", "count": 0},
        {"label": "-9.8~-7%", "count": 0},
        {"label": "-7~-3%", "count": 0},
        {"label": "-3~0%", "count": 0},
        {"label": "0~3%", "count": 0},
        {"label": "3~7%", "count": 0},
        {"label": "7~9.8%", "count": 0},
        {"label": "≥9.8%", "count": 0},
    ]

    def bucket_index(c: float) -> int:
        if c < -9.8:
            return 0
        if c < -7:
            return 1
        if c < -3:
            return 2
        if c < 0:
            return 3
        if c < 3:
            return 4
        if c < 7:
            return 5
        if c < 9.8:
            return 6
        return 7

    for r in rows:
        c = _n(r.get("price_change_ratio_pct"))
        t = _n(r.get("turnover"))
        if t is not None:
            turnover += t
        if c is None:
            continue
        if c > 0:
            up += 1
        elif c < 0:
            down += 1
        else:
            flat += 1
        changes.append(c)
        buckets[bucket_index(c)]["count"] += 1

    changes.sort()
    return {
        "total": len(rows), "up": up, "down": down, "flat": flat,
        "turnover": _r(turnover), "avg": _r(_avg(changes)), "median": _r(_median(changes)),
        "upRatio": _r(up / len(changes) * 100, 1) if changes else None,
        "buckets": buckets,
    }


# ------------------------------------------------------------------ 涨跌停与连板
def limit_board() -> Dict[str, Any]:
    date = sd.last_trade_date()
    pools = sd.parallel_map(lambda k: sd.limit_pool(k, date), ["limit-up-pool", "limit-down-pool", "limit-break-pool"])
    up_pool, down_pool, brk_pool = pools
    ladder = sd.ladder()

    up_items = [{
        "thscode": it.get("thscode"), "ticker": it.get("ticker"), "name": it.get("name"),
        "lastPrice": _n(it.get("last_price")), "changePct": _n(it.get("price_change_ratio_pct")),
        "limitUpTime": it.get("limit_up_time"), "reason": it.get("limit_up_reason"),
        "continueText": it.get("continue_day_text"), "continueCount": _n(it.get("continue_day_cnt")) or 1,
        "sealMoney": _n(it.get("seal_money")), "maxSealMoney": _n(it.get("max_seal_money")),
        "openTimes": _n(it.get("open_times")), "isST": bool(it.get("is_st")), "isNew": bool(it.get("is_new")),
    } for it in (up_pool.get("items") or [])]
    up_items.sort(key=lambda x: (-(x["continueCount"] or 1), -(x["sealMoney"] or 0)))

    down_items = [{
        "thscode": it.get("thscode"), "ticker": it.get("ticker"), "name": it.get("name"),
        "lastPrice": _n(it.get("last_price")), "changePct": _n(it.get("price_change_ratio_pct")),
        "firstLimitTime": it.get("first_limit_time"), "lastLimitTime": it.get("last_limit_time"),
        "turnoverRate": _n(it.get("turnover_ratio_pct")),
    } for it in (down_pool.get("items") or [])]

    brk_items = [{
        "thscode": it.get("thscode"), "ticker": it.get("ticker"), "name": it.get("name"),
        "lastPrice": _n(it.get("last_price")), "changePct": _n(it.get("price_change_ratio_pct")),
        "openTimes": _n(it.get("open_times")), "turnover": _n(it.get("turnover")),
        "firstSealTime": it.get("first_seal_time"), "lastSealTime": it.get("last_seal_time"),
    } for it in (brk_pool.get("items") or [])]
    brk_items.sort(key=lambda x: -(x["openTimes"] or 0))

    tiers: List[dict] = []
    if ladder:
        boards = ladder.get("boards") or {}
        order = [("two_board", 2), ("three_board", 3), ("four_board", 4),
                 ("five_board", 5), ("six_board", 6), ("seven_over", 7)]
        multi = []
        for key, level in order:
            items = [{"thscode": it.get("thscode"), "ticker": it.get("ticker"),
                      "name": it.get("name"), "boardNum": _n(it.get("board_num")) or level}
                     for it in (boards.get(key) or [])]
            if items:
                multi.append({"level": level, "label": "7 板及以上" if level >= 7 else f"{level} 连板",
                              "items": items, "count": len(items)})
        multi.sort(key=lambda t: t["level"])
        total_up = up_pool.get("total") or len(up_items)
        first_board = max(0, int(total_up) - sum(t["count"] for t in multi))
        if first_board > 0:
            tiers.append({"level": 1, "label": "首板", "items": [], "count": first_board})
        tiers.extend(multi)

    up_count = up_pool.get("total") if up_pool.get("total") is not None else len(up_items)
    down_count = down_pool.get("total") if down_pool.get("total") is not None else len(down_items)
    brk_count = brk_pool.get("total") if brk_pool.get("total") is not None else len(brk_items)
    seal_rate = _r(len(up_items) / (len(up_items) + len(brk_items)) * 100, 1) if (up_items or brk_items) else None

    return {
        "date": date, "limitUpCount": int(up_count), "limitDownCount": int(down_count), "breakCount": int(brk_count),
        "sealRate": seal_rate,
        "breakRate": _r(100 - seal_rate, 1) if seal_rate is not None else None,
        "highestBoard": max((i["continueCount"] or 1) for i in up_items) if up_items else None,
        "tiers": tiers, "up": up_items, "down": down_items, "break": brk_items,
    }


# ------------------------------------------------------------------ 板块排行
SECTOR_KIND = {
    "l1": {"label": "一级行业", "prefix": ("881",)},
    "l2": {"label": "细分行业", "prefix": ("884",)},
    "concept": {"label": "概念板块", "prefix": ("885", "886")},
}


def _kind_of(code: str) -> str:
    if code.startswith("881"):
        return "l1"
    if code.startswith("884"):
        return "l2"
    return "concept"


def sector_board() -> Dict[str, Any]:
    market = sd.market_snapshot_all()
    by_code = market["map"]
    catalogs = sd.index_catalog("industry") + sd.index_catalog("cn_concept")
    snaps = sd.index_snapshot([c["code"] for c in catalogs])

    boards: Dict[str, List[dict]] = {"l1": [], "l2": [], "concept": []}
    for item in catalogs:
        code = item["code"]
        s = snaps.get(code) or {}
        chg = _n(s.get("price_change_ratio_pct"))
        if chg is None:
            continue
        detail = sd.MEMBERSHIP.index_by_code(code)
        members = detail["members"] if detail else []
        if not members:
            continue
        leader = None
        up_n = down_n = 0
        for m in members:
            r = by_code.get(m["thscode"]) or {}
            c = _n(r.get("price_change_ratio_pct"))
            if c is None:
                continue
            if c > 0:
                up_n += 1
            elif c < 0:
                down_n += 1
            if leader is None or c > leader["changePct"]:
                leader = {"thscode": m["thscode"], "ticker": m.get("ticker"), "name": m.get("name"), "changePct": _r(c)}
        boards[_kind_of(code)].append({
            "code": code, "name": item["name"], "changePct": _r(chg),
            "turnover": _r(_n(s.get("turnover"))), "memberCount": len(members),
            "upCount": up_n, "downCount": down_n, "leader": leader,
        })

    totals, bottoms = {}, {}
    for k in boards:
        totals[k] = len(boards[k])
        boards[k].sort(key=lambda x: -x["changePct"])
        bottoms[k] = list(reversed(boards[k][-5:]))
        boards[k] = boards[k][:40]
    return {
        "labels": {k: v["label"] for k, v in SECTOR_KIND.items()},
        "totals": totals, "bottoms": bottoms, "boards": boards,
    }


def sector_detail(code: str) -> Dict[str, Any]:
    detail = sd.MEMBERSHIP.index_by_code(code)
    if not detail:
        return {"code": code, "name": None, "members": [], "memberCount": 0,
                "upCount": 0, "downCount": 0, "kind": _kind_of(code)}
    market = sd.market_snapshot_all()
    by_code = market["map"]
    members = []
    for m in detail["members"]:
        r = by_code.get(m["thscode"]) or {}
        c = _n(r.get("price_change_ratio_pct"))
        if c is None:
            continue
        members.append({
            "thscode": m["thscode"], "ticker": m.get("ticker"), "name": m.get("name"),
            "lastPrice": _n(r.get("last_price")), "changePct": c,
            "turnover": _n(r.get("turnover")), "volume": _n(r.get("volume")),
        })
    members.sort(key=lambda x: -x["changePct"])
    return {
        "code": code, "name": detail["name"], "kind": _kind_of(code),
        "memberCount": len(members), "members": members,
        "upCount": sum(1 for m in members if m["changePct"] > 0),
        "downCount": sum(1 for m in members if m["changePct"] < 0),
    }


# ------------------------------------------------------------------ 热门榜
def hot_board() -> Dict[str, Any]:
    date = sd.last_trade_date()
    hot = sd.hot_stock("day")
    sky = sd.skyrocket("day")
    dt = sd.dragon_tiger(date) if date else {"items": []}
    market = sd.market_snapshot_all()
    names = sd.MEMBERSHIP.name_map()

    top = []
    for r in market["rows"]:
        t = _n(r.get("turnover"))
        if t is None:
            continue
        top.append((t, r))
    top.sort(key=lambda x: -x[0])
    turnover_top = []
    for t, r in top[:12]:
        turnover_top.append({
            "thscode": r["thscode"], "ticker": r.get("ticker"),
            "name": names.get(r["thscode"]) or r.get("ticker"),
            "lastPrice": _n(r.get("last_price")),
            "changePct": _n(r.get("price_change_ratio_pct")), "turnover": t,
        })

    dt_items = sorted([x for x in (dt.get("items") or []) if x.get("netValue") is not None],
                      key=lambda x: -x["netValue"])[:12]
    dt_items = [{
        "thscode": x["thscode"], "name": x["name"],
        "changePct": _r(x["change"] * 100) if x.get("change") is not None else None,
        "netValue": x["netValue"], "orgNetValue": x.get("orgNetValue"),
        "hotMoneyNetValue": x.get("hotMoneyNetValue"), "rangeDays": x.get("rangeDays"),
        "limitReason": x.get("limitReason"),
    } for x in dt_items]

    return {
        "date": date,
        "hot": hot[:12], "skyrocket": sky[:12],
        "dragonTiger": dt_items, "turnoverTop": turnover_top,
    }


# ------------------------------------------------------------------ 聚合
def dashboard() -> Dict[str, Any]:
    import datetime as dt
    date = sd.last_trade_date()
    warnings: List[str] = []
    if sd.MEMBERSHIP.stats()["status"] != "ready":
        sd.MEMBERSHIP.ensure_async()
        warnings.append("行业/概念成分索引构建中，板块领涨股与成分股可能暂缺。")
    return {
        "ok": True,
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "tradeDate": date,
        "breadth": sd.cached("mk:breadth", 60, breadth),
        "limits": sd.cached("mk:limits", 60, limit_board),
        "sectors": sd.cached("mk:sectors", 90, sector_board),
        "hot": sd.cached("mk:hot", 60, hot_board),
        "membership": sd.MEMBERSHIP.stats(),
        "warnings": warnings,
    }
