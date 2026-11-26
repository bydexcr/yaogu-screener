# -*- coding: utf-8 -*-
"""holdings.py —— 收盘后的「持仓深度分析」

触发条件（两个都要满足）：
  1) 当天 15:00 之后（收盘后才有完整日线，盘中口径会误导）
  2) 自选股里标记了「持有」**且**填了成本价

每个持仓输出：
  · 持仓视图：成本 / 现价 / 浮盈亏
  · 技术位：MA5/20/60、20 日支撑压力、60 日高低、近 60 日最大回撤
  · 量能与盘口：5 日量比、5v20 成交额比、收盘位置、换手
  · 量化风险矩阵：触发风险阈值的条目数 + 明细
  · 观察清单（observations）：全部是「数字 → 事实描述」，不做涨跌预测
  · 来自 stock_analysis 的评分与叙事（headline / grade / highlights / risks）

所有结论都只是对已发生数据的规则化描述，不构成投资建议。
"""
from __future__ import annotations

import datetime as dt
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

CUTOFF_HOUR = 15          # 15:00 之后才生成
CACHE_TTL = 1800          # 30 分钟：收盘后行情不变，重复进页面不用重算
MAX_STOCKS = 20           # 超过就只分析前 20 只（按自选顺序）

_CACHE: Dict[tuple, tuple] = {}
_LOCK = threading.RLock()


# ------------------------------------------------------------------ 时间闸门
def now_local() -> dt.datetime:
    return dt.datetime.now()


def gate(now: Optional[dt.datetime] = None) -> Dict[str, Any]:
    """返回 {'available': bool, 'reason': str}。"""
    now = now or now_local()
    if now.hour >= CUTOFF_HOUR:
        return {"available": True, "reason": ""}
    return {"available": False,
            "reason": "%d:00 收盘后生成（现在 %s，盘中数据不完整）" % (CUTOFF_HOUR, now.strftime("%H:%M"))}


# ------------------------------------------------------------------ 小工具
def _num(v) -> Optional[float]:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f == f else None          # 过滤 NaN


def _pct(v, d: int = 2) -> str:
    n = _num(v)
    return "—" if n is None else ("%+.*f%%" % (d, n))


def _tone(text_tone: str) -> str:
    return text_tone if text_tone in ("good", "bad", "warn", "info") else "info"


# ------------------------------------------------------------------ 单只分析
def _pick(analysis: dict, item: dict) -> Dict[str, Any]:
    """从 stock_analysis 的完整结果里挑出持仓复盘需要的字段（体积要小）。"""
    q = analysis.get("quote") or {}
    sc = analysis.get("scores") or {}
    tech = analysis.get("trendTech") or {}
    cap = analysis.get("capital") or {}
    nar = analysis.get("narrative") or {}
    risk = analysis.get("riskMatrix") or {}
    meta = analysis.get("meta") or {}

    cost = _num(item.get("cost"))
    qty = _num(item.get("qty"))
    last = _num(q.get("lastPrice"))
    pnl = (last / cost - 1) * 100 if (cost and last) else None
    value = round(qty * last, 2) if (qty and last) else None
    cost_amt = round(qty * cost, 2) if (qty and cost) else None

    rows = risk.get("rows") or []
    alerts = [r for r in rows if (r.get("status") or "") == "alert"]
    watches = [r for r in rows if (r.get("status") or "") == "watch"]

    return {
        "thscode": item.get("thscode"),
        "name": q.get("name") or item.get("name") or item.get("thscode"),
        "cost": cost,
        "qty": qty,
        "value": value,
        "cost_amt": cost_amt,
        "pnl_amt": (round(value - cost_amt, 2) if (value is not None and cost_amt is not None) else None),
        "last": last,
        "pct": _num(q.get("changePct")),
        "pnl_pct": round(pnl, 2) if pnl is not None else None,
        "board": q.get("board") or "",
        "limit": (q.get("limit") or {}).get("label") or "",
        "trade_date": meta.get("tradeDate"),
        "turnover": _num(q.get("turnover")),
        "scores": {
            "overall": _num(sc.get("overall")),
            "trend": _num(sc.get("trend")),
            "capital": _num(sc.get("capital")),
            "quality": _num(sc.get("quality")),
            "valuation": _num(sc.get("valuation")),
        },
        "grade": nar.get("grade") or "",
        "ma": {
            "ma5": _num(tech.get("ma5")), "ma20": _num(tech.get("ma20")),
            "ma60": _num(tech.get("ma60")), "state": tech.get("state") or "",
            "ret5": _num(tech.get("ret5")), "ret20": _num(tech.get("ret20")),
            "support20": _num(tech.get("support20")),
            "resistance20": _num(tech.get("resistance20")),
            "high60": _num(tech.get("high60")), "low60": _num(tech.get("low60")),
            "maxDrawdown60": _num(tech.get("maxDrawdown60")),
        },
        "capital": {
            "volRatio5": _num(cap.get("volRatio5")),
            "amountRatio5v20": _num(cap.get("amountRatio5v20")),
            "closePosition": _num(cap.get("closePosition")),
            "turnoverRate": _num(cap.get("turnoverRate")),
        },
        "risk": {"alerts": len(alerts), "watches": len(watches),
                 "total": len(rows), "text": nar.get("riskText") or "",
                 "top": [{"item": r.get("item"), "value": r.get("value")} for r in alerts[:4]]},
        "five_day": nar.get("fiveDayText") or "",
        "headline": nar.get("headline") or "",
        "highlights": (nar.get("highlights") or [])[:3],
        "risks": (nar.get("risks") or [])[:3],
    }


def observations(p: Dict[str, Any]) -> List[Dict[str, str]]:
    """把数字翻译成事实描述（不预测涨跌），供页面按风险/机会分色。"""
    out: List[Dict[str, str]] = []
    pnl, cost, last = p.get("pnl_pct"), p.get("cost"), p.get("last")
    ma20 = (p.get("ma") or {}).get("ma20")
    cap = p.get("capital") or {}
    ma = p.get("ma") or {}

    if pnl is not None:
        amt = p.get("pnl_amt")
        extra = ("，折合 %+.0f 元（%d 股 × 现价）" % (amt, p.get("qty"))) if (amt is not None and p.get("qty")) else ""
        out.append({"tone": "good" if pnl >= 0 else "bad",
                    "text": "相对成本 %s：现价 %.2f / 成本 %.2f，浮动 %s%s"
                            % ("盈利" if pnl >= 0 else "亏损", last, cost, _pct(pnl), extra)})

    if last and ma20:
        diff = (last / ma20 - 1) * 100
        out.append({"tone": "good" if diff >= 0 else "bad",
                    "text": "现价%s 20 日线（%.2f）%.2f%%%s"
                            % ("站上" if diff >= 0 else "跌破", ma20, diff,
                               "，趋势结构尚在" if diff >= 0 else "，短线转弱信号")})

    hi, lo = ma.get("resistance20"), ma.get("support20")
    if last and hi and lo:
        out.append({"tone": "info",
                    "text": "20 日区间 %.2f ~ %.2f：距高点 %.2f%%，距低点 %.2f%%"
                            % (lo, hi, (last / hi - 1) * 100, (last / lo - 1) * 100)})

    r5 = cap.get("volRatio5")
    if _num(r5) is not None:
        out.append({"tone": "warn" if r5 >= 1.6 else ("info" if r5 >= 0.7 else "warn"),
                    "text": "量能：近 5 日成交量为 20 日均量的 %.2f 倍%s"
                            % (r5, "（明显放量）" if r5 >= 1.6 else ("（明显缩量）" if r5 < 0.7 else ""))})

    cp = cap.get("closePosition")
    if _num(cp) is not None:
        out.append({"tone": "good" if cp >= 70 else ("bad" if cp <= 30 else "info"),
                    "text": "当日收盘位于日内区间 %.0f%%（%s）"
                            % (cp, "收在高位" if cp >= 70 else ("收在低位" if cp <= 30 else "收在中段"))})

    dd = ma.get("maxDrawdown60")
    if _num(dd) is not None:
        out.append({"tone": "warn" if dd <= -25 else "info",
                    "text": "近 60 日最大回撤 %s%s" % (_pct(dd), "（波动偏大）" if dd <= -25 else "")})

    risk = p.get("risk") or {}
    if risk.get("alerts"):
        out.append({"tone": "bad",
                    "text": "量化风险：%d 项触发阈值（共 %d 项检查）%s"
                            % (risk["alerts"], risk.get("total") or 0,
                               "：" + "、".join(str(x.get("item")) for x in (risk.get("top") or [])[:3])
                               if risk.get("top") else "")})

    if pnl is not None and pnl < 0:
        out.append({"tone": "bad", "text": "已跌破成本价，处于亏损持仓"})
    if p.get("limit"):
        out.append({"tone": "good" if "涨停" in str(p.get("limit")) else "bad",
                    "text": "当日 %s" % p.get("limit")})
    return out


# ------------------------------------------------------------------ 组装
def _default_analyze(code: str) -> dict:
    """默认实现：调用个股分析引擎（web/stock_analysis.py）。"""
    import stock_analysis as A          # 延迟导入，测试可注入替身
    return A.analyze(code)


def build(state_json_fn=None, analysis_fn=None, now: Optional[dt.datetime] = None,
          store=None) -> Dict[str, Any]:
    """生成持仓深度分析。

    state_json_fn / analysis_fn / now / store 都可注入，便于测试。
    """
    g = gate(now)
    store = store or _default_store()
    items = [it for it in (store.items() or [])
             if it.get("held") and _num(it.get("cost"))]

    if not g["available"]:
        return {"ok": True, "available": False, "reason": g["reason"],
                "count": len(items), "items": [], "summary": None}
    if not items:
        return {"ok": True, "available": True, "count": 0, "items": [], "summary": None,
                "reason": "自选股里还没有「已持有 + 已填成本价」的股票"}

    items = items[:MAX_STOCKS]
    analyze = analysis_fn or _default_analyze
    trade_date = None

    def work(it):
        code = it["thscode"]
        key = (code, dt.date.today().isoformat())
        with _LOCK:
            hit = _CACHE.get(key)
        if hit and time.time() - hit[0] < CACHE_TTL:
            return hit[1]
        try:
            raw = analyze(code)
        except BaseException as e:              # noqa: BLE001  单只失败不影响整体
            return {"thscode": code, "name": it.get("name"), "error": "%s: %s" % (type(e).__name__, e)}
        if not isinstance(raw, dict) or raw.get("ok") is False:
            return {"thscode": code, "name": it.get("name"),
                    "error": str((raw or {}).get("error") or "分析失败")}
        picked = _pick(raw, it)
        with _LOCK:
            _CACHE[key] = (time.time(), picked)
        return picked

    results: List[Dict[str, Any]] = [None] * len(items)      # type: ignore[list-item]

    def slot(i, it):
        return i, work(it)

    with ThreadPoolExecutor(max_workers=min(3, len(items))) as ex:
        for i, res in ex.map(lambda p: slot(p[0], p[1]), list(enumerate(items))):
            results[i] = res

    for r in results:
        if r and r.get("trade_date"):
            trade_date = r["trade_date"]
            break

    # 持仓总览
    ok = [r for r in results if r and not r.get("error") and _num(r.get("pnl_pct")) is not None]
    weights = [(_num(r.get("cost")) or 0) for r in ok]
    total_w = sum(weights) or 1.0
    total_pnl = sum((_num(r.get("pnl_pct")) or 0) * w for r, w in zip(ok, weights)) / total_w if ok else None
    best = max(ok, key=lambda r: _num(r.get("pnl_pct")) or -1e9) if ok else None
    worst = min(ok, key=lambda r: _num(r.get("pnl_pct")) or 1e9) if ok else None
    attention = [r for r in ok
                 if (_num(r.get("pnl_pct")) or 0) < 0
                 or ((r.get("risk") or {}).get("alerts") or 0) > 0
                 or (_num((r.get("ma") or {}).get("ma20")) and _num(r.get("last"))
                     and r["last"] < r["ma"]["ma20"])]

    for r in results:
        if r and not r.get("error"):
            r["observations"] = observations(r)

    return {
        "ok": True, "available": True, "count": len(items),
        "trade_date": trade_date,
        "generated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "held": len(items),
            "analyzed": len(ok),
            "weighted_pnl": round(total_pnl, 2) if total_pnl is not None else None,
            "cost_amt": (round(sum(_num(r.get("cost_amt")) or 0 for r in ok), 2)
                         if any(_num(r.get("cost_amt")) for r in ok) else None),
            "value": (round(sum(_num(r.get("value")) or 0 for r in ok), 2)
                      if any(_num(r.get("value")) for r in ok) else None),
            "pnl_amt": (round(sum(_num(r.get("pnl_amt")) or 0 for r in ok), 2)
                        if any(_num(r.get("pnl_amt")) is not None for r in ok) else None),
            "best": {"name": best.get("name"), "pnl": best.get("pnl_pct")} if best else None,
            "worst": {"name": worst.get("name"), "pnl": worst.get("pnl_pct")} if worst else None,
            "attention": len(attention),
            "errors": len([r for r in results if r and r.get("error")]),
        },
        "items": results,
    }


def _default_store():
    try:
        import watchlist_store as W
        return W
    except Exception:
        from web import watchlist_store as W      # noqa: F401
        return W
