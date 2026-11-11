# -*- coding: utf-8 -*-
"""
stock_review.py —— 当日盘面复盘（AI 复盘系统结构）

输出结构对齐复盘页设计稿：
  1   一句话总收口      oneSentence
  2   盘型 / 环境       env（涨跌家数、涨停/炸板/涨停率、主要指数）
  2.5 资金流证据       money（龙虎榜净额口径：个股 / 板块净流入·净流出 TOP5）
  4   主线 / 次主线 / 活口 / 失败轮动   rotation
  4.5 连板高度单元     height
  6   四分层核心角色   layers
  10  次日观察与证伪   nextday
  12  股票池更新       pool
  13  市场风险与参与边界 risk

口径说明：同花顺 REST 没有官方「主力资金/大单资金」指标，
本页「资金流证据」用**龙虎榜净额**（buyValue - sellValue）作为可核验的资金证据，
并在页面上明确标注，不冒充主力资金。
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys
from typing import Any, Dict, List, Optional

try:
    from . import stock_data as sd
    from . import stock_market as sm
except ImportError:  # pragma: no cover - 非包方式加载
    _HERE = pathlib.Path(__file__).resolve().parent
    if str(_HERE) not in sys.path:
        sys.path.insert(0, str(_HERE))
    import stock_data as sd  # type: ignore
    import stock_market as sm  # type: ignore

_n = sd._num
_r = sd._round

# 报告结构版本：结构升级后，旧存档不再直接复用（会重新生成覆盖）
SCHEMA = 2

INDEXES = [
    ("000001.SH", "上证指数"),
    ("399001.SZ", "深证成指"),
    ("399006.SZ", "创业板指"),
    ("000688.SH", "科创50"),
    ("899050.BJ", "北证50"),
    ("000300.SH", "沪深300"),
    ("000905.SH", "中证500"),
    ("000852.SH", "中证1000"),
]


# ------------------------------------------------------------------ 存档
def _cache_dir() -> pathlib.Path:
    return sd._writable_dir()


def _file(date: str) -> pathlib.Path:
    return _cache_dir() / f"review_{date}.json"


def saved_dates() -> List[str]:
    try:
        names = sorted(p.stem.replace("review_", "") for p in _cache_dir().glob("review_*.json"))
    except Exception:  # noqa: BLE001
        return []
    return names


# ------------------------------------------------------------------ 小工具
def _yi(v) -> float:
    """元 → 亿元（保留 2 位）"""
    v = _n(v)
    return round(v / 1e8, 2) if v is not None else None


def _ind_label(v: Optional[float]) -> str:
    if v is None:
        return "—"
    if v >= 9.8:
        return "涨%.2f%%" % v
    if v > 0:
        return "涨%.2f%%" % v
    if v == 0:
        return "平"
    return "跌%.2f%%" % v


# ------------------------------------------------------------------ 环境
def _indices() -> List[Dict[str, Any]]:
    snaps = sd.index_snapshot([c for c, _ in INDEXES])
    out = []
    for code, name in INDEXES:
        s = snaps.get(code) or {}
        out.append({
            "code": code, "name": name,
            "last": _n(s.get("last_price")),
            "changePct": _r(_n(s.get("price_change_ratio_pct"))),
            "turnover": _n(s.get("turnover")),
        })
    return out


def _heat(breadth: Dict[str, Any], limits: Dict[str, Any]) -> Dict[str, Any]:
    up = _n(breadth.get("up")) or 0
    down = _n(breadth.get("down")) or 0
    total = up + down
    breadth_score = (up / total * 100) if total else 50.0
    up_n = _n(limits.get("limitUpCount")) or 0
    down_n = _n(limits.get("limitDownCount")) or 0
    limit_score = (up_n / (up_n + down_n) * 100) if (up_n + down_n) else 50.0
    seal = _n(limits.get("sealRate"))
    seal_score = seal if seal is not None else 50.0
    top = _n(limits.get("highestBoard")) or 0
    top_score = max(0.0, min(100.0, top / 8 * 100))
    score = breadth_score * 0.4 + limit_score * 0.2 + seal_score * 0.2 + top_score * 0.2
    if score >= 75:
        label, tone = "过热", "hot"
    elif score >= 60:
        label, tone = "偏暖", "warm"
    elif score >= 45:
        label, tone = "中性", "mid"
    elif score >= 30:
        label, tone = "偏冷", "cool"
    else:
        label, tone = "冰点", "cold"
    return {"score": _r(score, 1), "label": label, "tone": tone,
            "parts": {"涨跌家数": _r(breadth_score, 1), "涨停占比": _r(limit_score, 1),
                      "封板率": _r(seal_score, 1), "连板高度": _r(top_score, 1)}}


def _regime(indices: List[Dict[str, Any]], breadth: Dict[str, Any], limits: Dict[str, Any]) -> Dict[str, str]:
    """盘型判定：指数强弱 × 个股广度 × 题材高度。"""
    idx_up = sum(1 for i in indices if (_n(i.get("changePct")) or 0) > 0)
    idx_n = len(indices) or 1
    up, down = _n(breadth.get("up")) or 0, _n(breadth.get("down")) or 0
    up_pct = (up / (up + down) * 100) if (up + down) else 50.0
    up_n = _n(limits.get("limitUpCount")) or 0
    top = _n(limits.get("highestBoard")) or 0

    weak_idx = idx_up <= idx_n / 2
    if weak_idx and up_pct >= 50:
        name = "弱指数 / 结构抱团"
    elif weak_idx and up_pct < 50:
        name = "指数与个股共振走弱"
    elif (not weak_idx) and up_pct >= 55:
        name = "指数与个股共振走强"
    elif not weak_idx and up_pct < 50:
        name = "指数强 / 个股分化"
    else:
        name = "震荡分化"

    if up_n >= 80 and top >= 4:
        flavor = "题材高度充足"
    elif up_n >= 50:
        flavor = "题材中等活跃"
    elif up_n >= 25:
        flavor = "题材偏弱"
    else:
        flavor = "题材冰点"
    return {"name": name, "flavor": flavor,
            "text": "%s · %s（%d/%d 指数收红，上涨占比 %.1f%%，涨停 %d 家，最高 %d 连板）" % (
                name, flavor, idx_up, idx_n, up_pct, up_n, top)}


# ------------------------------------------------------------------ 资金证据
def _money(dragon: Dict[str, Any], sectors: Dict[str, Any]) -> Dict[str, Any]:
    items = [x for x in (dragon.get("items") or []) if _n(x.get("netValue")) is not None]
    items.sort(key=lambda x: -(_n(x.get("netValue")) or 0))

    def one(x):
        return {"name": x.get("name"), "code": (x.get("thscode") or "").split(".")[0],
                "net": _yi(x.get("netValue")),
                "changePct": _r((_n(x.get("change")) or 0) * 100) if x.get("change") is not None else None,
                "org": _yi(x.get("orgNetValue")), "hot": _yi(x.get("hotMoneyNetValue")),
                "concepts": (x.get("concepts") or [])[:3]}

    stock_in = [one(x) for x in items[:5]]
    stock_out = [one(x) for x in list(reversed(items[-5:]))] if len(items) > 5 else []

    # 板块：用涨停池 + 龙虎榜所属概念聚合，得到「板块资金证据」的净额合计
    by_sec: Dict[str, Dict[str, Any]] = {}
    name_of = sectors.get("labels") or {}
    boards = (sectors.get("boards") or {})
    sec_change = {}
    for kind in ("l1", "concept"):
        for b in boards.get(kind) or []:
            sec_change[b["name"]] = _n(b.get("changePct"))

    for x in items:
        for c in (x.get("concepts") or [])[:4]:
            rec = by_sec.setdefault(c, {"name": c, "net": 0.0, "count": 0})
            rec["net"] += _n(x.get("netValue")) or 0
            rec["count"] += 1
    rows = []
    for rec in by_sec.values():
        rows.append({"name": rec["name"], "net": _yi(rec["net"]), "count": rec["count"],
                     "changePct": _r(sec_change.get(rec["name"]))})
    rows = [r for r in rows if (r["net"] or 0) != 0]
    rows.sort(key=lambda r: -(r["net"] or 0))
    return {
        "caliber": "龙虎榜净额口径（同花顺无官方主力资金指标）；板块为龙虎榜个股所属概念聚合",
        "stockIn": stock_in, "stockOut": stock_out,
        "sectorIn": rows[:5], "sectorOut": list(reversed(rows[-5:])) if len(rows) > 5 else [],
        "listCount": len(items),
    }


# ------------------------------------------------------------------ 主线轮动
def _rotation(limits: Dict[str, Any], sectors: Dict[str, Any]) -> Dict[str, Any]:
    up_items = limits.get("up") or []
    boards = (sectors.get("boards") or {}).get("l1") or []

    # 按题材（涨停原因）聚合
    theme: Dict[str, Dict[str, Any]] = {}
    for s in up_items:
        reason = (s.get("reason") or "").replace("＋", "+")
        tags = [t.strip() for t in reason.split("+") if t and t.strip()]
        for t in tags[:3]:
            rec = theme.setdefault(t, {"name": t, "count": 0, "boards": 0, "seal": 0.0, "members": []})
            rec["count"] += 1
            rec["boards"] = max(rec["boards"], _n(s.get("continueCount")) or 1)
            rec["seal"] += _n(s.get("sealMoney")) or 0
            rec["members"].append({"name": s.get("name"), "code": s.get("ticker"),
                                   "board": _n(s.get("continueCount")) or 1,
                                   "time": s.get("limitUpTime"),
                                   "seal": _yi(s.get("sealMoney"))})

    themes = [t for t in theme.values() if t["count"] >= 2]
    themes.sort(key=lambda t: (-t["boards"], -t["count"], -t["seal"]))
    for t in themes:
        t["members"].sort(key=lambda m: (-(m["board"] or 1), -(m["seal"] or 0)))
        t["members"] = t["members"][:6]
        t["seal"] = _yi(t["seal"])

    def verdict(t) -> str:
        if t["boards"] >= 4:
            return "AI 裁定：高度主线，看前排分歧是否一致"
        if t["boards"] >= 3:
            return "AI 裁定：主线延续，只做前排与容量票"
        if t["boards"] >= 2:
            return "AI 裁定：次主线，看是否出现中军"
        return "AI 裁定：活口方向，缩量则降级"

    main = themes[0] if themes else None
    subs = themes[1:3]
    alive = themes[3:5]

    # 失败反馈：优先取当日收跌的板块；若全行业收红，则取「相对最弱」并标注
    failed = []
    rows = [b for b in boards if _n(b.get("changePct")) is not None]
    rows.sort(key=lambda b: _n(b.get("changePct")) or 0)
    losers = [b for b in rows if (_n(b.get("changePct")) or 0) < 0]
    picked = losers[:3] if losers else rows[:3]
    for b in picked:
        chg = _n(b.get("changePct")) or 0
        failed.append({"name": b.get("name"), "changePct": _r(chg),
                       "limitCount": None,
                       "isLoser": chg < 0,
                       "note": "%s %+.2f%%，%d 只成分，领涨 %s" % (
                           "收跌" if chg < 0 else "相对最弱", chg, b.get("memberCount") or 0,
                           (b.get("leader") or {}).get("name") or "—")})

    def pack(t):
        if not t:
            return None
        return {"name": t["name"], "count": t["count"], "boards": t["boards"], "seal": t["seal"],
                "members": t["members"], "verdict": verdict(t)}

    return {
        "main": pack(main),
        "subs": [pack(x) for x in subs],
        "alive": [pack(x) for x in alive],
        "failed": failed,
        "themeCount": len(themes),
    }


# ------------------------------------------------------------------ 高度单元 & 分层
def _height(limits: Dict[str, Any], sectors: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    ups = [x for x in (limits.get("up") or []) if (_n(x.get("continueCount")) or 1) >= 2]
    if not ups:
        ups = limits.get("up") or []
    if not ups:
        return None
    ups.sort(key=lambda x: (-(_n(x.get("continueCount")) or 1), -(_n(x.get("sealMoney")) or 0)))
    top = ups[0]
    industry = _industry_of(top.get("thscode"))
    return {
        "name": top.get("name"), "code": top.get("ticker"),
        "board": _n(top.get("continueCount")) or 1,
        "changePct": _r(_n(top.get("changePct"))),
        "seal": _yi(top.get("sealMoney")), "maxSeal": _yi(top.get("maxSealMoney")),
        "time": top.get("limitUpTime"), "reason": top.get("reason"),
        "industry": industry,
        "isNew": bool(top.get("isNew")), "isST": bool(top.get("isST")),
    }


def _industry_of(thscode: Optional[str]) -> str:
    if not thscode:
        return "—"
    try:
        d = sd.MEMBERSHIP.index_by_code  # 保证属性存在
        rev = sd.MEMBERSHIP.get(thscode)
        if rev.get("industries"):
            return rev["industries"][0].get("name") or "—"
        if rev.get("concepts"):
            return rev["concepts"][0].get("name") or "—"
    except Exception:  # noqa: BLE001
        pass
    return "—"


def _layers(rotation: Dict[str, Any], limits: Dict[str, Any], money: Dict[str, Any]) -> Dict[str, Any]:
    """四分层核心角色：沿主线方向，把涨停股按身位分层。"""
    main = rotation.get("main")
    if not main:
        return {"direction": None, "rows": []}
    rows = []
    for i, m in enumerate(main.get("members") or []):
        if i == 0:
            tag, status = "高度锚", "封板"
        elif i == 1:
            tag, status = "强度锚", "封板"
        elif i == 2:
            tag, status = "次核心", "封板"
        else:
            tag, status = "活口", "封板"
        rows.append({
            "name": m["name"], "code": m["code"], "tag": tag, "status": status,
            "board": m["board"], "seal": m["seal"], "time": m["time"],
            "direction": main["name"],
        })
    return {"direction": main["name"], "rows": rows, "count": main.get("count")}


def _nextday(rotation: Dict[str, Any], limits: Dict[str, Any], heat: Dict[str, Any],
             money: Dict[str, Any]) -> Dict[str, List[str]]:
    main = rotation.get("main")
    top = _n(limits.get("highestBoard")) or 0
    brk = _n(limits.get("breakCount")) or 0
    down_n = _n(limits.get("limitDownCount")) or 0
    seal = _n(limits.get("sealRate"))
    failed = [f["name"] for f in (rotation.get("failed") or [])[:2]]

    watch: List[str] = []
    falsify: List[str] = []
    if main:
        watch.append("%s（今日 %d 只涨停、最高 %d 连板）能否继续缩量一致" % (main["name"], main["count"], main["boards"]))
        falsify.append("%s 前排低开低走或大面积炸板 → 主线降级" % main["name"])
    if top >= 3:
        watch.append("最高 %d 连板的高度股与同高度个股的分歧情况" % top)
        falsify.append("高度股断板且无同高度接力 → 情绪进入退潮")
    if money.get("sectorIn"):
        watch.append("资金证据最强方向（%s）是否延续净流入" % money["sectorIn"][0]["name"])
    if failed:
        watch.append("失败方向（%s）能否止跌，决定后排补跌是否扩散" % "、".join(failed))
        falsify.append("%s 继续扩大跌幅、出现新的跌停 → 弱势扩散" % "、".join(failed))
    if seal is not None:
        watch.append("封板率（%.1f%%）能否回到 75%% 以上，决定接力意愿" % seal)
        falsify.append("封板率跌破 65%% 且炸板 %d 只以上 → 打板胜率快速下降" % max(20, brk))
    if down_n >= 5:
        falsify.append("跌停家数升破 %d 只 → 亏钱效应显性化" % max(down_n, 8))
    return {"watch": watch[:4], "falsify": falsify[:4]}


def _pool(limits: Dict[str, Any], rotation: Dict[str, Any]) -> Dict[str, Any]:
    ups = limits.get("up") or []
    themes = []
    for key in ("main",):
        t = rotation.get(key)
        if t and t.get("name"):
            themes.append(t["name"])
    for t in (rotation.get("subs") or []) + (rotation.get("alive") or []):
        if t and t.get("name"):
            themes.append(t["name"])
    # 去掉引号等装饰，按关键词匹配题材
    keywords = [t.replace("“", "").replace("”", "").replace("\"", "").strip() for t in themes if t]
    keywords = [k for k in keywords if len(k) >= 2]

    added, keep, risk = [], [], []
    for s in ups:
        reason = s.get("reason") or ""
        board = _n(s.get("continueCount")) or 1
        item = {"name": s.get("name"), "code": s.get("ticker"), "board": board,
                "changePct": _r(_n(s.get("changePct"))), "reason": reason[:20]}
        if board == 1 and any(k in reason for k in keywords):
            added.append(item)
        elif board >= 2:
            keep.append(item)
        else:
            risk.append(item)
    for b in (limits.get("break") or [])[:6]:
        risk.append({"name": b.get("name"), "code": b.get("ticker"), "board": 0,
                     "changePct": _r(_n(b.get("changePct"))),
                     "reason": "炸板 %s 次" % (_n(b.get("openTimes")) or 0)})
    key = lambda x: (-(x.get("board") or 0), -(x.get("changePct") or 0))
    added.sort(key=key); keep.sort(key=key); risk.sort(key=key)
    return {"added": added[:6], "keep": keep[:6], "risk": risk[:6]}


def _risk(heat: Dict[str, Any], limits: Dict[str, Any], rotation: Dict[str, Any],
          breadth: Dict[str, Any]) -> Dict[str, Any]:
    score = _n(heat.get("score")) or 50
    brk = _n(limits.get("breakCount")) or 0
    down_n = _n(limits.get("limitDownCount")) or 0

    level = "中"
    if score >= 75 and brk <= 15:
        level = "中低"
    elif score >= 60:
        level = "中"
    elif score >= 45 and brk >= 20:
        level = "中高"
    elif score < 45:
        level = "高"

    parts = []
    losers = [f["name"] for f in (rotation.get("failed") or []) if f.get("isLoser")]
    weakest = [f["name"] for f in (rotation.get("failed") or []) if not f.get("isLoser")]
    if losers:
        parts.append("最大风险是 %s 等方向继续负反馈，未止跌前相关后排只能降级观察" % "、".join(losers[:2]))
    elif weakest:
        parts.append("全行业收红，但 %s 相对最弱，注意资金是否回流" % "、".join(weakest[:2]))
    if brk >= 20:
        parts.append("炸板 %d 只，尾盘承接偏弱，追高需看回封质量" % brk)
    if down_n:
        parts.append("跌停 %d 只，注意亏钱效应扩散" % down_n)
    up_pct = _n(breadth.get("upRatio"))
    if up_pct is not None:
        parts.append("上涨占比 %.1f%%，只做最强方向的前排与容量确认票" % up_pct)
    return {"level": level, "score": _r(score, 1),
            "text": "；".join(parts) if parts else "未见明显异常（按数据口径描述）"}


# ------------------------------------------------------------------ 一句话总收口
def _one_liner(regime: Dict[str, str], rotation: Dict[str, Any], risk: Dict[str, Any],
               breadth: Dict[str, Any], limits: Dict[str, Any]) -> Dict[str, Any]:
    main = rotation.get("main")
    up, down = _n(breadth.get("up")) or 0, _n(breadth.get("down")) or 0
    sents = []
    if main:
        sents.append("%s下，%s拿到最大宽度（%d 只涨停、最高 %d 连板），是本日唯一可操作主线"
                     % (regime["name"], main["name"], main["count"], main["boards"]))
    else:
        sents.append("%s，题材分散、无明确主线" % regime["name"])
    subs = [x["name"] for x in (rotation.get("subs") or []) if x]
    if subs:
        sents.append("次主线在 %s，属于接力方向而非主升" % "、".join(subs))
    losers = [f["name"] for f in (rotation.get("failed") or []) if f.get("isLoser")]
    if losers:
        sents.append("风险主要在 %s 持续负反馈" % "、".join(losers[:2]))
    sents.append("涨 %d / 跌 %d，涨停 %d 家、炸板 %d 家，风险等级 %s"
                 % (up, down, _n(limits.get("limitUpCount")) or 0,
                    _n(limits.get("breakCount")) or 0, risk.get("level")))
    return {"verdict": sents[0], "sentences": sents}


# ------------------------------------------------------------------ 主入口
def review(date: Optional[str] = None, save: bool = True, force: bool = False) -> Dict[str, Any]:
    trade_date = (date or "").strip() or sd.last_trade_date()
    if trade_date and not sd.is_trade_date(trade_date):
        trade_date = sd.last_trade_date()
    today = sd.last_trade_date()

    cached_file = _file(trade_date) if trade_date else None
    if not force and cached_file and cached_file.exists():
        try:
            payload = json.loads(cached_file.read_text(encoding="utf-8"))
            has_sectors = bool(((payload.get("sectors") or {}).get("industry") or {}).get("top"))
            if payload.get("ok") and payload.get("schema") == SCHEMA and (has_sectors or trade_date != today):
                payload["fromArchive"] = True
                return payload
        except Exception:  # noqa: BLE001
            pass

    mstat = sd.MEMBERSHIP.stats()
    hint = ""
    if mstat.get("status") != "ready":
        sd.MEMBERSHIP.ensure_async()
        hint = "行业/概念成分索引构建中（首次约 30~90 秒），板块与分层稍后自动补全。"
    elif trade_date and mstat.get("date") and mstat["date"] != trade_date:
        sd.MEMBERSHIP.refresh_async()
        hint = "板块成分索引来自 %s，正在后台更新到 %s。" % (mstat.get("date"), trade_date)

    breadth = sm.breadth()
    limits_raw = sd.cached("mk:limits", 60, sm.limit_board) if trade_date == today else sm.limit_board()
    sectors_raw = sd.cached("mk:sectors", 90, sm.sector_board)
    hot = sd.cached("mk:hot", 60, sm.hot_board)
    dragon = sd.dragon_tiger(trade_date)
    indices = _indices()
    heat = _heat(breadth, limits_raw)
    regime = _regime(indices, breadth, limits_raw)
    labels = sectors_raw.get("labels") or {}
    sectors_view = {
        "labels": labels,
        "boards": sectors_raw.get("boards") or {},
        "totals": sectors_raw.get("totals") or {},
        "industry": {"top": (sectors_raw.get("boards", {}).get("l1") or [])[:6],
                     "bottom": list(reversed((sectors_raw.get("boards", {}).get("l1") or [])[-6:]))},
        "concept": {"top": (sectors_raw.get("boards", {}).get("concept") or [])[:6],
                    "bottom": list(reversed((sectors_raw.get("boards", {}).get("concept") or [])[-6:]))},
    }
    money = _money(dragon, sectors_raw)
    rotation = _rotation(limits_raw, sectors_raw)
    height = _height(limits_raw, sectors_raw)
    layers = _layers(rotation, limits_raw, money)
    risk = _risk(heat, limits_raw, rotation, breadth)
    nextday = _nextday(rotation, limits_raw, heat, money)
    pool = _pool(limits_raw, rotation)
    one_line = _one_liner(regime, rotation, risk, breadth, limits_raw)

    up_n = _n(limits_raw.get("limitUpCount")) or 0
    brk = _n(limits_raw.get("breakCount")) or 0
    limit_rate = _r(up_n / (up_n + brk) * 100, 2) if (up_n + brk) else None

    payload: Dict[str, Any] = {
        "ok": True,
        "schema": SCHEMA,
        "date": trade_date,
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "head": {"title": "%s 正式收复盘" % (trade_date or "—"), "system": "AI 复盘系统",
                 "regime": regime["name"]},
        "oneSentence": one_line,
        "env": {
            "up": _n(breadth.get("up")), "down": _n(breadth.get("down")), "flat": _n(breadth.get("flat")),
            "total": _n(breadth.get("total")), "upRatio": _n(breadth.get("upRatio")),
            "turnover": _n(breadth.get("turnover")),
            "limitUp": up_n, "limitDown": _n(limits_raw.get("limitDownCount")),
            "breakCount": brk, "limitRate": limit_rate,
            "sealRate": _n(limits_raw.get("sealRate")), "highestBoard": _n(limits_raw.get("highestBoard")),
            "indices": indices, "regime": regime,
            "breadth": breadth,
        },
        "heat": heat,
        "money": money,
        "rotation": rotation,
        "height": height,
        "layers": layers,
        "ladder": {"tiers": limits_raw.get("tiers") or [], "up": (limits_raw.get("up") or [])[:12],
                   "break": (limits_raw.get("break") or [])[:8], "down": (limits_raw.get("down") or [])[:8]},
        "limits": {"limitUpCount": up_n, "limitDownCount": _n(limits_raw.get("limitDownCount")),
                   "breakCount": brk, "sealRate": _n(limits_raw.get("sealRate")),
                   "breakRate": _n(limits_raw.get("breakRate")),
                   "highestBoard": _n(limits_raw.get("highestBoard"))},
        "sectors": sectors_view,
        "breadth": breadth,
        "nextday": nextday,
        "pool": pool,
        "risk": risk,
        "membership": {**mstat, "hint": hint},
        "archive": {"saved": False, "path": None, "count": len(saved_dates())},
        "fromArchive": False,
        "disclaimer": "数据来自同花顺金融数据服务（行情/涨停池/炸板池/跌停池/连板天梯/龙虎榜）。"
                      "「资金流证据」为龙虎榜净额口径，非官方主力资金；以上均为数据描述，不构成投资建议。",
    }

    if save and trade_date:
        try:
            p = _file(trade_date)
            p.parent.mkdir(parents=True, exist_ok=True)
            to_write = dict(payload)
            to_write["archive"] = {"saved": True, "path": p.name, "count": 0}
            p.write_text(json.dumps(to_write, ensure_ascii=False, default=str), encoding="utf-8")
            payload["archive"] = {"saved": True, "path": p.name, "count": len(saved_dates())}
        except Exception as e:  # noqa: BLE001
            sd._note("复盘存档失败: %s" % e)
    return payload
