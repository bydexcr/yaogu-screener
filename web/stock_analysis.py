# -*- coding: utf-8 -*-
"""
stock_analysis.py —— 个股综合分析引擎（手机端 Python 版）
与 PC 版 stock-analyzer/lib/(analysis|insights|peers|stats).js 输出结构一致：
quote / scores / fundamentals / performance / valuation / recent5 / trendTech /
capital / popularity / sector / moat / trends / dupont / dividends / tradingStats /
riskMatrix / industryRank / keyFacts / peers / narrative
"""
from __future__ import annotations

import datetime as dt
import math
import statistics
from typing import Any, Dict, List, Optional

import stock_data as sd

PERIOD_ORDER = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4, "FY": 5}


# ------------------------------------------------------------------ 数值工具
def num(v):
    return sd._num(v)


def rnd(v, d: int = 2):
    if v is None:
        return None
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    if math.isnan(v) or math.isinf(v):
        return None
    return round(v, d)


def safe_div(a, b, scale: float = 100.0):
    if a is None or b is None:
        return None
    try:
        a = float(a); b = float(b)
    except (TypeError, ValueError):
        return None
    if b == 0 or math.isnan(a) or math.isnan(b):
        return None
    return a / b * scale


def pct_change(cur, prev):
    if cur is None or prev is None:
        return None
    try:
        if float(prev) == 0:
            return None
        return (float(cur) / float(prev) - 1) * 100
    except (TypeError, ValueError):
        return None


def avg(vals):
    vs = [v for v in vals if v is not None]
    return sum(vs) / len(vs) if vs else None


def median(vals):
    vs = sorted(v for v in vals if v is not None)
    if not vs:
        return None
    n = len(vs)
    return vs[n // 2] if n % 2 else (vs[n // 2 - 1] + vs[n // 2]) / 2


def percentile_rank(vals, v):
    vs = [x for x in vals if x is not None]
    if not vs or v is None:
        return None
    return sum(1 for x in vs if x <= v) / len(vs)


def piecewise(x, pts):
    """分段线性映射 pts=[(x,y),...] 需按 x 升序"""
    if x is None:
        return None
    if x <= pts[0][0]:
        return pts[0][1]
    if x >= pts[-1][0]:
        return pts[-1][1]
    for i in range(1, len(pts)):
        x1, y1 = pts[i]
        x0, y0 = pts[i - 1]
        if x <= x1:
            t = (x - x0) / ((x1 - x0) or 1)
            return y0 + t * (y1 - y0)
    return pts[-1][1]


def clamp(v, lo=0.0, hi=100.0):
    return max(lo, min(hi, v))


def daily_returns(series: List[dict]) -> List[float]:
    out = []
    for i in range(1, len(series)):
        a, b = series[i - 1].get("close"), series[i].get("close")
        if a and b is not None and a != 0:
            out.append(b / a - 1)
    return out


def range_return(series: List[dict], n: int):
    if not series or len(series) < 2:
        return None
    end = series[-1].get("close")
    start = series[max(0, len(series) - 1 - n)].get("close")
    return pct_change(end, start)


def max_drawdown(series: List[dict]):
    peak = None
    worst = 0.0
    for bar in series:
        c = bar.get("close")
        if c is None:
            continue
        peak = c if peak is None else max(peak, c)
        if peak:
            worst = min(worst, (c / peak - 1) * 100)
    return worst


def moving_average(series: List[dict], n: int):
    if len(series) < n:
        return None
    return avg([b.get("close") for b in series[-n:]])


def pearson(a: List[float], b: List[float]):
    n = min(len(a), len(b))
    if n < 10:
        return None
    x, y = a[-n:], b[-n:]
    mx, my = avg(x), avg(y)
    sxy = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    sxx = sum((x[i] - mx) ** 2 for i in range(n))
    syy = sum((y[i] - my) ** 2 for i in range(n))
    if sxx == 0 or syy == 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def fmt_money(v):
    if v is None:
        return "—"
    a = abs(v)
    if a >= 1e12:
        return f"{v / 1e12:.2f} 万亿"
    if a >= 1e8:
        return f"{v / 1e8:.2f} 亿"
    if a >= 1e4:
        return f"{v / 1e4:.2f} 万"
    return f"{v:.2f}"


def fmt_num(v, d=2):
    return "—" if v is None else f"{v:.{d}f}"


def fmt_pct(v, d=2):
    return "—" if v is None else f"{v:+.{d}f}%"


def limit_pct_of(ticker: str, is_st: bool) -> int:
    t = str(ticker or "")
    if t[:2] in ("92",) or t[:1] in ("8", "4"):
        return 30
    if t[:3] in ("688", "689") or t[:3] in ("300", "301"):
        return 20
    return 5 if is_st else 10


def report_string(fy, period):
    q = PERIOD_ORDER.get(str(period))
    if not q or q > 4:
        return None
    return f"{fy}-{q}"


def single_quarters(quarters: List[dict]) -> List[dict]:
    by_year: Dict[int, Dict[int, dict]] = {}
    for row in quarters:
        q = PERIOD_ORDER.get(str(row.get("fiscal_period")))
        if not q or q > 4:
            continue
        by_year.setdefault(row.get("fiscal_year"), {})[q] = row
    out = []
    for year in sorted(by_year):
        m = by_year[year]
        for q in (1, 2, 3, 4):
            row = m.get(q)
            if not row:
                continue
            rev, prof, cost = num(row.get("operating_income")), num(row.get("parent_holder_net_profit")), num(row.get("operating_costs"))
            srev, sprof, scost = rev, prof, cost
            if q > 1:
                prev = m.get(q - 1)
                srev = rev - num(prev.get("operating_income")) if prev and rev is not None and num(prev.get("operating_income")) is not None else None
                sprof = prof - num(prev.get("parent_holder_net_profit")) if prev and prof is not None and num(prev.get("parent_holder_net_profit")) is not None else None
                scost = cost - num(prev.get("operating_costs")) if prev and cost is not None and num(prev.get("operating_costs")) is not None else None
            out.append({
                "label": f"{year}Q{q}", "fiscalYear": year, "quarter": q,
                "revenue": rnd(srev), "profit": rnd(sprof),
                "cumRevenue": rnd(rev), "cumProfit": rnd(prof),
                "grossMargin": safe_div((srev - scost) if (srev is not None and scost is not None) else None, srev),
            })
    return out


# ------------------------------------------------------------------ 主流程
def analyze(query: str, progress=None) -> Dict[str, Any]:
    def stage(msg):
        if callable(progress):
            try:
                progress(msg)
            except Exception:  # noqa: BLE001
                pass

    warnings: List[str] = []
    sources: List[str] = []

    stage("解析标的信息")
    target = sd.resolve_stock(query)
    thscode, name = target["thscode"], target["name"]
    sources.append("symbol.search")

    stage("拉取行情与历史K线")
    snap = sd.snapshot([thscode])
    market = sd.market_snapshot_all()
    vals = sd.valuations([thscode])
    hist = sd.history(thscode, 420)
    hot = sd.hot_stock("day")
    sources += ["market.snapshot", "valuation.snapshot", "market.history", "special.hot-stock"]
    if not hist:
        warnings.append("未取到该股日线历史，技术面与近 5 日走势将不完整。")

    stage("拉取财务报表与指标")
    income_annual = sd.statements(thscode, "income", "annual", 8)
    income_quarterly = sd.statements(thscode, "income", "quarterly", 20)
    balances = sd.statements(thscode, "balance-sheet", "annual", 5)
    cashflows = sd.statements(thscode, "cash-flow", "annual", 5)
    sources += ["financials.income", "financials.balance-sheet", "financials.cash-flow"]

    latest_q = income_quarterly[-1] if income_quarterly else None
    ind = None
    if latest_q:
        for report in [report_string(latest_q.get("fiscal_year"), latest_q.get("fiscal_period"))]:
            if report:
                ind = sd.indicators(thscode, report)
                if ind:
                    sources.append("financials.indicators")
                    break
        if not ind:
            warnings.append("最新报告期财务指标未取到，部分比率改用报表数据自行计算。")

    stage("解析行业与概念归属")
    mem = sd.MEMBERSHIP.get(thscode)
    if sd.MEMBERSHIP.stats()["status"] != "ready":
        sd.MEMBERSHIP.ensure_async()
        warnings.append("行业/概念成分索引仍在后台构建，板块与同类对比可能不完整。")

    stage("拉取板块行情与热度趋势")
    sector_codes = [i["code"] for i in mem["industries"]] + [c["code"] for c in mem["concepts"][:10]]
    focus = mem["industries"][0] if mem["industries"] else None
    annual_reports = [f"{r.get('fiscal_year')}-4" for r in income_annual[-6:]]
    idx_snap = sd.index_snapshot(sector_codes) if sector_codes else {}
    idx_hist = sd.index_history(focus["code"], 90) if focus else []
    hot_tr = sd.hot_trend(thscode, 120)
    ind_hist = sd.indicator_history(thscode, annual_reports)
    actions = sd.corporate_actions(thscode, 10)
    sky = sd.skyrocket("day")
    if idx_snap:
        sources.append("index.snapshot")
    if idx_hist:
        sources.append("index.history")
    if hot_tr:
        sources.append("special.hot-stock-trend")
    if ind_hist:
        sources.append("financials.indicators(多期)")
    if actions:
        sources.append("market.corporate-actions")
    if sky:
        sources.append("special.skyrocket")

    stage("核对龙虎榜与资金席位")
    quote = build_quote(target, snap.get(thscode), hist)
    raw_dates = [b["date"] for b in hist[-5:]][::-1]
    trade_dates = [d for d in raw_dates if d and sd.is_trade_date(d)][:3]
    boards = sd.parallel_map(lambda d: sd.dragon_tiger(d), trade_dates)
    dragon = []
    for b in boards:
        if not b:
            continue
        for it in b.get("items") or []:
            if it.get("thscode") == thscode:
                dragon.append({**it, "tradeDate": b.get("tradeDate")})
        if any(it.get("thscode") == thscode for it in b.get("items") or []):
            sources.append("special.dragon-tiger")

    limit_rec = None
    lim = quote["limit"]
    if lim["isLimitUp"] or lim["isLimitDown"] or lim["touchedLimitUp"] or lim["touchedLimitDown"]:
        limit_rec = find_limit_record(thscode, hist[-1]["date"] if hist else None, quote["lastPrice"])
        if limit_rec:
            sources.append("special.limit-up-pool")

    fundamentals = build_fundamentals(income_annual, balances, cashflows, ind, mem)
    if fundamentals["size"]["shares"] and quote["lastPrice"]:
        fundamentals["size"]["marketCap"] = int(fundamentals["size"]["shares"] * quote["lastPrice"])
    performance = build_performance(income_annual, income_quarterly)
    valuation = build_valuation(vals.get(thscode), fundamentals)
    recent5 = build_recent5(hist, quote)
    trend = build_trend(hist, quote)

    stage("扫描同行业可比公司")
    peer_res = build_peers(thscode, target, mem, market, quote, fundamentals, valuation, hist)
    sources += peer_res.get("usedSources", [])

    sector = build_sector(mem, idx_snap, idx_hist, focus, recent5)
    popularity = build_popularity(thscode, hot, hot_tr, dragon, market, quote, limit_rec, sky)
    capital = build_capital(quote, hist, recent5, dragon, market, fundamentals)
    moat = build_moat(fundamentals, performance, peer_res)

    stage("计算财务趋势、杜邦与风险检查")
    trends = build_trends(income_annual, balances, cashflows, ind_hist)
    dupont = build_dupont(trends, fundamentals)
    dividends = build_dividends(actions, quote, fundamentals)
    trading = build_trading_stats(hist, quote, lim["limitPct"])
    risk = build_risk_matrix(quote, valuation, fundamentals, performance, capital, popularity, trend, recent5)
    industry_rank = build_industry_rank(
        {"thscode": thscode, "name": name, "quote": quote, "valuation": valuation,
         "fundamentals": fundamentals, "performance": performance},
        peer_res["peers"], peer_res["peerIndicators"], peer_res.get("universeLabel"), peer_res.get("universeSize"))

    scores = build_scores(fundamentals, performance, valuation, capital, popularity, trend)
    narrative = build_narrative(quote, fundamentals, performance, valuation, recent5, trend, capital,
                                popularity, sector, scores, peer_res, moat, limit_rec, trends, dupont,
                                dividends, trading, risk, industry_rank, warnings)
    key_facts = build_key_facts(quote, fundamentals, performance, valuation, capital, popularity,
                                trend, recent5, sector, dividends, dupont,
                                {"label": peer_res.get("universeLabel"), "size": peer_res.get("universeSize")})

    return {
        "ok": True,
        "query": str(query),
        "resolved": target,
        "meta": {
            "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
            "tradeDate": hist[-1]["date"] if hist else None,
            "limitRecord": limit_rec,
            "adjust": "forward",
            "sources": sources,
            "warnings": warnings,
            "membership": sd.MEMBERSHIP.stats(),
            "disclaimer": "本页所有数字来自同花顺金融数据服务，结论为基于这些数字的规则化描述，不构成任何投资建议。",
        },
        "quote": quote,
        "scores": scores,
        "fundamentals": fundamentals,
        "performance": performance,
        "moat": moat,
        "capital": capital,
        "popularity": popularity,
        "recent5": recent5,
        "trendTech": trend,
        "valuation": valuation,
        "sector": sector,
        "trends": trends,
        "dupont": dupont,
        "dividends": dividends,
        "tradingStats": trading,
        "riskMatrix": risk,
        "industryRank": industry_rank,
        "keyFacts": key_facts,
        "peers": peer_res["peers"],
        "universe": {
            "label": peer_res.get("universeLabel"), "size": peer_res.get("universeSize"),
            "kind": peer_res.get("universeKind"), "industryStats": peer_res.get("industryStats"),
        },
        "narrative": narrative,
    }


# ------------------------------------------------------------------ 各模块
def build_quote(target: dict, snap: Optional[dict], hist: List[dict]) -> dict:
    last_bar = hist[-1] if hist else None
    prev_bar = hist[-2] if len(hist) > 1 else None
    snap = snap or {}
    last_price = num(snap.get("last_price"))
    if last_price is None and last_bar:
        last_price = last_bar.get("close")
    prev_close = num(snap.get("prev_price"))
    if prev_close is None and prev_bar:
        prev_close = prev_bar.get("close")
    change_pct = num(snap.get("price_change_ratio_pct"))
    if change_pct is None:
        change_pct = pct_change(last_price, prev_close)
    open_p = num(snap.get("open_price"))
    if open_p is None and last_bar:
        open_p = last_bar.get("open")
    high = num(snap.get("high_price"))
    if high is None and last_bar:
        high = last_bar.get("high")
    low = num(snap.get("low_price"))
    if low is None and last_bar:
        low = last_bar.get("low")
    volume = num(snap.get("volume"))
    if volume is None and last_bar:
        volume = last_bar.get("volume")
    turnover = num(snap.get("turnover"))
    if turnover is None and last_bar:
        turnover = last_bar.get("turnover")
    change = num(snap.get("price_change"))
    if change is None and last_price is not None and prev_close is not None:
        change = last_price - prev_close

    is_st = "ST" in str(target.get("name") or "").upper()
    ticker = str(target.get("ticker") or "")
    lim_pct = limit_pct_of(ticker, is_st)
    tick = 0.011
    up_price = round(prev_close * (1 + lim_pct / 100), 2) if prev_close else None
    down_price = round(prev_close * (1 - lim_pct / 100), 2) if prev_close else None
    is_up = last_price is not None and up_price is not None and abs(last_price - up_price) <= tick
    is_down = last_price is not None and down_price is not None and abs(last_price - down_price) <= tick
    touched_up = (not is_up) and high is not None and up_price is not None and high >= up_price - tick
    touched_down = (not is_down) and low is not None and down_price is not None and low <= down_price + tick
    label = "涨停" if is_up else "跌停" if is_down else "触板未封（炸板）" if touched_up else "触跌停后回升" if touched_down else None

    board = None
    if len(ticker) == 6:
        if ticker.startswith("688"):
            board = "科创板"
        elif ticker.startswith(("300", "301")):
            board = "创业板"
        elif ticker[:1] in ("8", "4") or ticker.startswith("92"):
            board = "北交所"
        else:
            board = "主板"

    return {
        "thscode": target["thscode"], "ticker": ticker, "name": target["name"],
        "exchange": target.get("exchange"),
        "lastPrice": rnd(last_price), "change": rnd(change), "changePct": rnd(change_pct),
        "open": rnd(open_p), "high": rnd(high), "low": rnd(low), "prevClose": rnd(prev_close),
        "volume": int(volume) if volume is not None else None,
        "turnover": rnd(turnover),
        "amplitude": rnd(((high - low) / prev_close * 100) if (high is not None and low is not None and prev_close) else None),
        "isST": is_st, "board": board,
        "limit": {
            "limitPct": lim_pct, "limitUpPrice": rnd(up_price), "limitDownPrice": rnd(down_price),
            "isLimitUp": is_up, "isLimitDown": is_down,
            "touchedLimitUp": touched_up, "touchedLimitDown": touched_down, "label": label,
        },
    }


def build_fundamentals(income_annual, balances, cashflows, ind, mem) -> dict:
    li = income_annual[-1] if income_annual else None
    lb = balances[-1] if balances else None
    lc = cashflows[-1] if cashflows else None
    flat = (ind or {}).get("flat") or {}

    revenue = num(li.get("operating_income")) if li else None
    cost = num(li.get("operating_costs")) if li else None
    gross = (revenue - cost) if (revenue is not None and cost is not None) else None
    net = num(li.get("net_profit")) if li else None
    parent = num(li.get("parent_holder_net_profit")) if li else None
    eps = num(li.get("basic_eps")) if li else None
    shares = (parent / eps) if (parent and eps and parent / eps > 0) else None

    equity = num(lb.get("holder_equity_total")) if lb else None
    roe = flat.get("index_weighted_avg_roe")
    if roe is None:
        roe = safe_div(parent, equity)

    return {
        "industry": mem["industries"],
        "concepts": mem["concepts"],
        "latestReport": {
            "fiscalYear": li.get("fiscal_year"), "period": li.get("fiscal_period"),
            "periodEnd": sd._date_of_ms(li["period_end_ms"]) if li.get("period_end_ms") else None,
            "reportDate": sd._date_of_ms(li["report_date_ms"]) if li.get("report_date_ms") else None,
            "currency": li.get("currency") or "CNY",
        } if li else None,
        "income": {
            "revenue": rnd(revenue), "operatingCost": rnd(cost), "grossProfit": rnd(gross),
            "operatingProfit": rnd(num(li.get("operating_profit")) if li else None),
            "profitTotal": rnd(num(li.get("profit_total")) if li else None),
            "netProfit": rnd(net), "parentNetProfit": rnd(parent), "eps": rnd(eps, 3),
            "salesFee": rnd(num(li.get("sales_fee")) if li else None),
            "manageFee": rnd(num(li.get("manage_fee")) if li else None),
            "rdExpense": rnd(num(li.get("research_and_development_expenses")) if li else None),
            "interestExpense": rnd(num(li.get("interest_expenses")) if li else None),
        },
        "ratios": {
            "grossMargin": safe_div(gross, revenue),
            "netMargin": safe_div(net, revenue),
            "operatingMargin": safe_div(num(li.get("operating_profit")) if li else None, revenue),
            "parentNetMargin": safe_div(parent, revenue),
            "rdRatio": safe_div(num(li.get("research_and_development_expenses")) if li else None, revenue),
            "salesFeeRatio": safe_div(num(li.get("sales_fee")) if li else None, revenue),
            "manageFeeRatio": safe_div(num(li.get("manage_fee")) if li else None, revenue),
            "taxRate": safe_div(num(li.get("income_tax_expense")) if li else None, num(li.get("profit_total")) if li else None),
        },
        "balance": {
            "period": lb.get("fiscal_year"),
            "assetsTotal": rnd(num(lb.get("assets_total"))), "currentAssets": rnd(num(lb.get("total_current_assets"))),
            "nonCurrentAssets": rnd(num(lb.get("non_current_nets_total"))), "cash": rnd(num(lb.get("cash"))),
            "receivable": rnd(num(lb.get("accounts_receivable"))), "totalDebt": rnd(num(lb.get("total_debt"))),
            "equity": rnd(num(lb.get("holder_equity_total"))),
            "debtRatio": safe_div(num(lb.get("total_debt")), num(lb.get("assets_total"))),
            "equityRatio": safe_div(num(lb.get("holder_equity_total")), num(lb.get("assets_total"))),
            "cashToAssets": safe_div(num(lb.get("cash")), num(lb.get("assets_total"))),
        } if lb else None,
        "cashflow": {
            "period": lc.get("fiscal_year"),
            "operating": rnd(num(lc.get("act_cash_flow_net"))),
            "investing": rnd(num(lc.get("invest_cash_flow_net"))),
            "financing": rnd(num(lc.get("financing_cash_flow_net"))),
            "capex": rnd(num(lc.get("pay_fixed_assets_etc_cash"))),
            "dividendsPaid": rnd(num(lc.get("pay_dividends_profits_interest_cash"))),
            "cashAdded": rnd(num(lc.get("cash_equivalents_net_addition"))),
            "ocfToProfit": safe_div(num(lc.get("act_cash_flow_net")), net, 1),
            "freeCashFlow": rnd((num(lc.get("act_cash_flow_net")) or 0) - (num(lc.get("pay_fixed_assets_etc_cash")) or 0)),
        } if lc else None,
        "quality": {
            "report": (ind or {}).get("report"),
            "roe": rnd(roe), "roeDeducted": rnd(flat.get("index_deduct_weighted_avg_roe")),
            "roa": rnd(flat.get("total_assets_net_ratio")),
            "assetsDebtRatio": rnd(flat.get("assets_debt_ratio")),
            "currentRatio": rnd(flat.get("current_ratio"), 3), "quickRatio": rnd(flat.get("quick_ratio"), 3),
            "cashRatio": rnd(flat.get("cash_ratio"), 3),
            "totalAssetsTurnover": rnd(flat.get("total_assets_turnover_ratio"), 3),
            "inventoryTurnover": rnd(flat.get("inventory_turnover_ratio"), 3),
            "receivableTurnover": rnd(flat.get("receive_account_turnover_ratio")),
            "netProfitCashContent": rnd(flat.get("net_profit_cash_content")),
            "cashOperatingIndex": rnd(flat.get("cash_operating_index"), 3),
            "ocfToIncome": rnd(flat.get("operating_cash_flow_net_divide_income")),
            "cashMeetInvest": rnd(flat.get("cash_meet_invest_ratio"), 3),
        },
        "size": {"shares": int(shares) if shares else None, "marketCap": None},
        "prevYear": {
            "fiscalYear": income_annual[-2].get("fiscal_year"),
            "revenue": rnd(num(income_annual[-2].get("operating_income"))),
            "netProfit": rnd(num(income_annual[-2].get("net_profit"))),
            "parentNetProfit": rnd(num(income_annual[-2].get("parent_holder_net_profit"))),
        } if len(income_annual) > 1 else None,
    }


def build_performance(income_annual, income_quarterly) -> dict:
    annual = []
    for i, row in enumerate(income_annual):
        prev = income_annual[i - 1] if i > 0 else None
        rev, prof, cost = num(row.get("operating_income")), num(row.get("parent_holder_net_profit")), num(row.get("operating_costs"))
        annual.append({
            "fiscalYear": row.get("fiscal_year"), "revenue": rnd(rev),
            "revenueYoY": rnd(pct_change(rev, num(prev.get("operating_income")))) if prev else None,
            "parentNetProfit": rnd(prof),
            "profitYoY": rnd(pct_change(prof, num(prev.get("parent_holder_net_profit")))) if prev else None,
            "grossMargin": safe_div((rev - cost) if (rev is not None and cost is not None) else None, rev),
            "netMargin": safe_div(num(row.get("net_profit")), rev),
            "eps": rnd(num(row.get("basic_eps")), 3),
            "rdExpense": rnd(num(row.get("research_and_development_expenses"))),
            "rdRatio": safe_div(num(row.get("research_and_development_expenses")), rev),
        })

    singles = single_quarters(income_quarterly)
    same = {r["label"]: r for r in singles}
    for r in singles:
        prev = same.get(f"{r['fiscalYear'] - 1}Q{r['quarter']}")
        r["revenueYoY"] = rnd(pct_change(r["revenue"], prev["revenue"])) if prev else None
        r["profitYoY"] = rnd(pct_change(r["profit"], prev["profit"])) if prev else None

    def cagr(key, years):
        if len(annual) < years + 1:
            return None
        last, base = annual[-1].get(key), annual[-1 - years].get(key)
        if not last or not base or last <= 0 or base <= 0:
            return None
        return rnd(((last / base) ** (1 / years) - 1) * 100)

    last = annual[-1] if annual else None
    last3 = annual[-5:-1]
    consec = 0
    for r in reversed(annual[1:]):
        if r.get("revenueYoY") and r["revenueYoY"] > 0:
            consec += 1
        else:
            break

    return {
        "annual": annual,
        "quarterly": singles[-12:],
        "summary": {
            "latestFiscalYear": last.get("fiscalYear") if last else None,
            "revenue": last.get("revenue") if last else None,
            "revenueYoY": last.get("revenueYoY") if last else None,
            "parentNetProfit": last.get("parentNetProfit") if last else None,
            "profitYoY": last.get("profitYoY") if last else None,
            "grossMargin": last.get("grossMargin") if last else None,
            "netMargin": last.get("netMargin") if last else None,
            "revenueCagr3": cagr("revenue", 3),
            "profitCagr3": cagr("parentNetProfit", 3),
            "consecutiveGrowthYears": consec,
            "avgRevenueGrowthPrev3": rnd(avg([r.get("revenueYoY") for r in last3])),
            "avgProfitGrowthPrev3": rnd(avg([r.get("profitYoY") for r in last3])),
            "latestQuarter": singles[-1] if singles else None,
            "quartersWithPositiveYoY": sum(1 for q in singles[-4:] if q.get("profitYoY") and q["profitYoY"] > 0),
        },
    }


def build_valuation(v: Optional[dict], fundamentals: dict) -> dict:
    v = v or {}
    pe, pb = num(v.get("pe_ttm")), num(v.get("pb_mrq"))
    return {
        "peTtm": rnd(pe), "peMrq": rnd(num(v.get("pe_mrq"))), "pb": rnd(pb),
        "ps": rnd(num(v.get("ps_ttm"))), "pcf": rnd(num(v.get("pcf_ttm"))),
        "pePositive": bool(pe and pe > 0),
        "industryPeMedian": None, "industryPbMedian": None,
        "pePercentile": None, "pbPercentile": None,
        "earningsYield": rnd((1 / pe) * 100) if (pe and pe > 0) else None,
        "roe": fundamentals["quality"]["roe"],
    }


def build_recent5(hist: List[dict], quote: dict) -> dict:
    bars = hist[-5:]
    rows = []
    for i, bar in enumerate(bars):
        gi = len(hist) - len(bars) + i
        prev = hist[gi - 1] if gi > 0 else None
        prev_close = prev["close"] if prev else bar.get("open")
        chg = pct_change(bar.get("close"), prev_close)
        amp = ((bar["high"] - bar["low"]) / prev_close * 100) if (bar.get("high") is not None and bar.get("low") is not None and prev_close) else None
        pos = ((bar["close"] - bar["low"]) / (bar["high"] - bar["low"]) * 100) if (bar.get("high") is not None and bar.get("low") is not None and bar["high"] != bar["low"]) else None
        avg5 = avg([b.get("volume") for b in hist[max(0, gi - 5):gi]])
        rows.append({
            "date": bar["date"], "open": rnd(bar.get("open")), "high": rnd(bar.get("high")),
            "low": rnd(bar.get("low")), "close": rnd(bar.get("close")), "prevClose": rnd(prev_close),
            "changePct": rnd(chg), "amplitude": rnd(amp),
            "volume": int(bar["volume"]) if bar.get("volume") is not None else None,
            "turnover": rnd(bar.get("turnover")),
            "volumeRatio5": rnd(bar["volume"] / avg5) if (bar.get("volume") and avg5) else None,
            "closePosition": rnd(pos, 1),
        })

    first = bars[0] if bars else None
    last = bars[-1] if bars else None
    base_idx = len(hist) - len(bars) - 1
    base = hist[base_idx] if base_idx >= 0 else first
    cum = pct_change(last["close"], base["close"]) if (first and last and base) else None
    turnover_sum = sum((r.get("turnover") or 0) for r in rows)
    up_days = sum(1 for r in rows if r.get("changePct") and r["changePct"] > 0)
    down_days = sum(1 for r in rows if r.get("changePct") and r["changePct"] < 0)
    up_turn = sum(r["turnover"] or 0 for r in rows if r.get("changePct") and r["changePct"] > 0)

    dd_series = [b for b in ([base] if base else []) + bars if b]
    peak, dd = None, 0.0
    for bar in dd_series:
        c = bar.get("close")
        if c is None:
            continue
        peak = c if peak is None else max(peak, c)
        if peak:
            dd = min(dd, (c / peak - 1) * 100)

    vol_trend = None
    if len(rows) >= 4:
        fh = avg([r.get("volume") for r in rows[:2]])
        lh = avg([r.get("volume") for r in rows[-2:]])
        if fh and lh:
            vol_trend = rnd((lh / fh - 1) * 100, 1)

    return {
        "rows": rows,
        "summary": {
            "startDate": first["date"] if first else None,
            "endDate": last["date"] if last else None,
            "cumChangePct": rnd(cum),
            "cumTurnover": rnd(turnover_sum),
            "avgTurnover": rnd(turnover_sum / (len(rows) or 1)),
            "avgAmplitude": rnd(avg([r.get("amplitude") for r in rows])),
            "upDays": up_days, "downDays": down_days, "flatDays": len(rows) - up_days - down_days,
            "high": max((r["high"] for r in rows if r.get("high") is not None), default=None),
            "low": min((r["low"] for r in rows if r.get("low") is not None), default=None),
            "maxDrawdown": rnd(dd),
            "upDayTurnoverShare": rnd(up_turn / turnover_sum * 100, 1) if turnover_sum else None,
            "lastClosePosition": rows[-1]["closePosition"] if rows else None,
            "volumeTrend": vol_trend,
        },
    }


def build_trend(hist: List[dict], quote: dict) -> dict:
    ma5, ma10, ma20, ma60, ma120 = (moving_average(hist, n) for n in (5, 10, 20, 60, 120))
    rets = daily_returns(hist[-40:])
    vol = statistics.stdev(rets) if len(rets) > 1 else None
    price = quote.get("lastPrice")
    state = "均线数据不足"
    if None not in (ma5, ma10, ma20, ma60) and price:
        if price > ma5 > ma10 > ma20 > ma60:
            state = "多头排列"
        elif price < ma5 < ma10 < ma20 < ma60:
            state = "空头排列"
        elif price > ma20 > ma60:
            state = "中期偏强"
        elif price < ma20 < ma60:
            state = "中期偏弱"
        else:
            state = "震荡整理"
    last20 = hist[-20:]
    last60 = hist[-60:]
    return {
        "ma5": rnd(ma5), "ma10": rnd(ma10), "ma20": rnd(ma20), "ma60": rnd(ma60), "ma120": rnd(ma120),
        "state": state,
        "ret5": rnd(range_return(hist, 5)), "ret20": rnd(range_return(hist, 20)), "ret60": rnd(range_return(hist, 60)),
        "volatilityAnnual": rnd(vol * math.sqrt(250) * 100) if vol else None,
        "maxDrawdown60": rnd(max_drawdown(last60)),
        "support20": min((b["low"] for b in last20 if b.get("low") is not None), default=None),
        "resistance20": max((b["high"] for b in last20 if b.get("high") is not None), default=None),
        "high60": max((b["high"] for b in last60 if b.get("high") is not None), default=None),
        "low60": min((b["low"] for b in last60 if b.get("low") is not None), default=None),
        "series": [{"date": b["date"], "close": b["close"], "volume": b.get("volume")} for b in hist[-120:]],
        "candles": [{"date": b["date"], "open": b.get("open"), "high": b.get("high"), "low": b.get("low"),
                     "close": b.get("close"), "volume": b.get("volume")} for b in hist[-40:]],
    }


def build_sector(mem, idx_snap: Dict[str, dict], idx_hist: List[dict], focus, recent5) -> dict:
    industries = []
    for i in mem["industries"]:
        s = idx_snap.get(i["code"]) or {}
        industries.append({"code": i["code"], "name": i["name"],
                           "changePct": rnd(num(s.get("price_change_ratio_pct"))),
                           "lastPrice": rnd(num(s.get("last_price")))})
    industries.sort(key=lambda x: -(x["changePct"] if x["changePct"] is not None else -999))
    concepts = []
    for c in mem["concepts"][:12]:
        s = idx_snap.get(c["code"]) or {}
        concepts.append({"code": c["code"], "name": c["name"], "changePct": rnd(num(s.get("price_change_ratio_pct")))})
    concepts.sort(key=lambda x: -(x["changePct"] if x["changePct"] is not None else -999))

    focus_obj = None
    if focus:
        r5, r20 = rnd(range_return(idx_hist, 5)), rnd(range_return(idx_hist, 20))
        focus_obj = {"code": focus["code"], "name": focus["name"],
                     "changePct": next((i["changePct"] for i in industries if i["code"] == focus["code"]), None),
                     "ret5": r5, "ret20": r20, "series": idx_hist[-40:]}
    rel5 = None
    if focus_obj and focus_obj.get("ret5") is not None and recent5["summary"].get("cumChangePct") is not None:
        rel5 = rnd(recent5["summary"]["cumChangePct"] - focus_obj["ret5"])
    return {"industries": industries, "concepts": concepts, "focus": focus_obj, "relative5": rel5}


def build_popularity(thscode, hot, hot_tr, dragon, market, quote, limit_rec, sky) -> dict:
    entry = next((h for h in hot if h["thscode"] == thscode), None)
    sky_hit = next((s for s in (sky or []) if s["thscode"] == thscode), None)
    ranks = [r["rank"] for r in hot_tr if r.get("rank") is not None]
    last10, last30 = ranks[-10:], ranks[-30:]

    all_turn = [num(r.get("turnover")) for r in market["rows"]]
    all_turn = [t for t in all_turn if t is not None]
    my_turn = num((market["map"].get(thscode) or {}).get("turnover"))
    turn_rank = turn_pct = None
    if my_turn is not None and all_turn:
        turn_rank = sum(1 for t in all_turn if t > my_turn) + 1
        turn_pct = rnd(percentile_rank(all_turn, my_turn) * 100, 1)

    chg_list = [num(r.get("price_change_ratio_pct")) for r in market["rows"]]
    chg_list = [c for c in chg_list if c is not None]
    my_chg = num((market["map"].get(thscode) or {}).get("price_change_ratio_pct"))
    chg_pct = rnd(percentile_rank(chg_list, my_chg) * 100, 1) if (my_chg is not None and chg_list) else None

    def heat_score():
        parts = []
        if entry:
            parts.append(clamp(100 - (entry["rank"] - 1) * 2.2))
        elif hot_tr and hot_tr[-1].get("rank") is not None:
            parts.append(clamp(piecewise(hot_tr[-1]["rank"], [(1, 96), (30, 82), (100, 62), (300, 45), (800, 30), (2000, 15)])))
        if turn_pct is not None:
            parts.append(turn_pct)
        if ranks:
            parts.append(clamp(piecewise(avg(last10), [(1, 95), (30, 80), (100, 60), (300, 42), (800, 28), (2000, 12)])))
        if dragon:
            parts.append(88)
        lim = quote["limit"]
        if lim["isLimitUp"]:
            parts.append(96)
        elif lim["touchedLimitUp"] or lim["isLimitDown"]:
            parts.append(72)
        return rnd(avg(parts), 1) if parts else None

    return {
        "inTop30Today": bool(entry),
        "rankToday": entry["rank"] if entry else (hot_tr[-1]["rank"] if hot_tr else None),
        "heatToday": entry["heat"] if entry else None,
        "rankChange": entry["rankChange"] if entry else None,
        "limitStatus": quote["limit"],
        "limitRecord": limit_rec,
        "skyrocketRank": sky_hit["rank"] if sky_hit else None,
        "skyrocketHeat": sky_hit["heat"] if sky_hit else None,
        "hotRankListSize": len(hot),
        "trendDays": len(ranks),
        "bestRank": min(ranks) if ranks else None,
        "worstRank": max(ranks) if ranks else None,
        "avgRank10": rnd(avg(last10), 1), "avgRank30": rnd(avg(last30), 1),
        "daysTop10": sum(1 for r in ranks if r <= 10),
        "daysTop50": sum(1 for r in ranks if r <= 50),
        "daysTop100": sum(1 for r in ranks if r <= 100),
        "trend": [{"date": r["date"], "rank": r["rank"]} for r in hot_tr],
        "dragonTigerCount": len(dragon),
        "dragonTigerNet": rnd(sum((d.get("netValue") or 0) for d in dragon)),
        "dragonTigerOrgNet": rnd(sum((d.get("orgNetValue") or 0) for d in dragon)),
        "turnoverRank": turn_rank, "turnoverPercentile": turn_pct, "changePercentile": chg_pct,
        "heatScore": heat_score(),
    }


def build_capital(quote, hist, recent5, dragon, market, fundamentals) -> dict:
    vols20 = [b.get("volume") for b in hist[-20:] if b.get("volume") is not None]
    vols5 = [b.get("volume") for b in hist[-5:] if b.get("volume") is not None]
    avg20, avg5 = avg(vols20), avg(vols5)
    vol_ratio20 = rnd(quote["volume"] / avg20) if (quote.get("volume") and avg20) else None
    shares = fundamentals["size"]["shares"]
    turnover_rate = rnd(quote["volume"] / shares * 100, 3) if (quote.get("volume") and shares) else None

    turn5 = [num(b.get("turnover")) for b in hist[-5:]]
    turn20 = [num(b.get("turnover")) for b in hist[-20:]]
    amt_ratio = None
    a5, a20 = avg(turn5), avg(turn20)
    if a5 and a20:
        amt_ratio = rnd(a5 / a20 * 100 - 100, 1)

    all_turn = [num(r.get("turnover")) for r in market["rows"]]
    all_turn = [t for t in all_turn if t is not None]
    my_turn = num((market["map"].get(quote["thscode"]) or {}).get("turnover"))
    turn_rank = (sum(1 for t in all_turn if t > my_turn) + 1) if (my_turn is not None and all_turn) else None

    records = sorted(dragon, key=lambda r: str(r.get("tradeDate") or ""), reverse=True)
    cum = recent5["summary"].get("cumChangePct")
    trend5 = recent5["summary"].get("volumeTrend")
    pattern = "数据不足"
    if cum is not None and trend5 is not None:
        if cum > 0 and trend5 > 8:
            pattern = "放量上行"
        elif cum > 0 and trend5 < -8:
            pattern = "缩量上行"
        elif cum < 0 and trend5 > 8:
            pattern = "放量下行"
        elif cum < 0 and trend5 < -8:
            pattern = "缩量下行"
        else:
            pattern = "量能平稳"

    return {
        "turnover": quote.get("turnover"), "volume": quote.get("volume"),
        "turnoverRate": turnover_rate,
        "volRatio5": rnd(quote["volume"] / avg5) if (quote.get("volume") and avg5) else None,
        "volRatio20": vol_ratio20,
        "amountRatio5v20": amt_ratio,
        "avgTurnover20": rnd(a20),
        "amplitude": quote.get("amplitude"),
        "closePosition": recent5["summary"].get("lastClosePosition"),
        "turnoverRank": turn_rank, "turnoverRankOf": len(all_turn),
        "priceVolume": {
            "upDayTurnoverShare": recent5["summary"].get("upDayTurnoverShare"),
            "volumeTrend5": trend5, "pattern": pattern,
        },
        "dragonTiger": {
            "count": len(records),
            "records": [{
                "tradeDate": r.get("tradeDate"), "netValue": r.get("netValue"), "netRate": r.get("netRate"),
                "buyValue": r.get("buyValue"), "sellValue": r.get("sellValue"),
                "orgNetValue": r.get("orgNetValue"), "hotMoneyNetValue": r.get("hotMoneyNetValue"),
                "rangeDays": r.get("rangeDays"), "limitReason": r.get("limitReason"), "concepts": r.get("concepts"),
            } for r in records],
            "netValueSum": rnd(sum((r.get("netValue") or 0) for r in records)),
            "orgNetSum": rnd(sum((r.get("orgNetValue") or 0) for r in records)),
            "hotMoneyNetSum": rnd(sum((r.get("hotMoneyNetValue") or 0) for r in records)),
            "onBoard": bool(records),
        },
    }


def build_moat(fundamentals, performance, peer_res) -> dict:
    items = []
    ratios, quality = fundamentals["ratios"], fundamentals["quality"]
    s = performance["summary"]
    peer_med = (peer_res.get("industryStats") or {})

    def push(title, level, metric, evidence):
        items.append({"title": title, "level": level, "metric": metric, "evidence": evidence})

    gm = ratios.get("grossMargin")
    if gm is not None:
        pm = peer_med.get("grossMargin")
        rel = (gm - pm) if (pm is not None) else None
        if rel is not None:
            level = "强" if rel > 15 else "偏强" if rel > 3 else "持平" if rel > -3 else "偏弱" if rel > -12 else "弱"
            ev = f"毛利率 {gm:.2f}%，同行业样本中位数 {pm:.2f}%，{'高出' if rel > 0 else '低于'} {abs(rel):.2f} 个百分点。"
        else:
            level = "强" if gm > 50 else "偏强" if gm > 30 else "持平" if gm > 15 else "偏弱"
            ev = f"毛利率 {gm:.2f}%（同业样本不足，按经验阈值判断）。"
        push("毛利率 / 定价能力", level, f"{gm:.2f}%", ev)

    roe = quality.get("roe")
    if roe is not None:
        level = "强" if roe >= 20 else "偏强" if roe >= 13 else "持平" if roe >= 8 else "偏弱" if roe >= 3 else "弱"
        ded = quality.get("roeDeducted")
        push("净资产收益率 ROE", level, f"{roe:.2f}%",
             f"加权 ROE {roe:.2f}%" + (f"（扣非 {ded:.2f}%）" if ded is not None else "") + "，反映股东资本回报效率。")

    if s.get("revenueYoY") is not None or s.get("profitYoY") is not None:
        py = s.get("profitYoY")
        level = "强" if (py is not None and py > 20) else "偏强" if (py is not None and py > 8) else "持平" if (py is not None and py > 0) else "偏弱"
        push("成长动能", level, f"营收 {fmt_pct(s.get('revenueYoY'))} / 归母净利 {fmt_pct(s.get('profitYoY'))}",
             f"最新年报营收同比 {fmt_pct(s.get('revenueYoY'))}，归母净利润同比 {fmt_pct(s.get('profitYoY'))}"
             + (f"，近三年营收复合增速 {fmt_pct(s.get('revenueCagr3'))}" if s.get("revenueCagr3") is not None else "") + "。")

    rd = ratios.get("rdRatio")
    if rd is not None:
        level = "强" if rd > 8 else "偏强" if rd > 4 else "持平" if rd > 1.5 else "偏弱"
        push("研发投入强度", level, f"{rd:.2f}%",
             f"研发费用 {fmt_money(fundamentals['income'].get('rdExpense'))}，占营收 {rd:.2f}%"
             + ("，投入强度处于较高水平" if rd > 5 else "") + "。")

    cf = fundamentals.get("cashflow")
    if cf and cf.get("ocfToProfit") is not None:
        v = cf["ocfToProfit"]
        level = "强" if v >= 1 else "偏强" if v >= 0.6 else "持平" if v >= 0.2 else "弱"
        detail = (f"经营性现金流净额 {fmt_money(cf.get('operating'))} 为负，与净利润方向背离；"
                  if v < 0 else
                  f"经营性现金流净额 {fmt_money(cf.get('operating'))}，为净利润的 {v:.2f} 倍；") + \
                 f"自由现金流 {fmt_money(cf.get('freeCashFlow'))}。"
        push("现金流质量", level, "经营现金流为负" if v < 0 else f"{v:.2f} 倍", detail)

    debt = quality.get("assetsDebtRatio")
    if debt is not None:
        level = "强" if debt < 25 else "偏强" if debt < 45 else "持平" if debt < 65 else "偏弱"
        push("财务结构", level, f"资产负债率 {debt:.2f}%",
             f"资产负债率 {debt:.2f}%，流动比率 {fmt_num(quality.get('currentRatio'))}，速动比率 {fmt_num(quality.get('quickRatio'))}。")

    rt = quality.get("receivableTurnover")
    if rt is not None:
        level = "强" if rt > 10 else "偏强" if rt > 3 else "偏弱"
        push("产业链话语权（应收周转）", level, f"{rt:.2f} 次",
             f"应收账款周转率 {rt:.2f} 次，应收账款 {fmt_money((fundamentals.get('balance') or {}).get('receivable'))}。")

    if cf and cf.get("dividendsPaid") is not None and fundamentals["income"].get("netProfit"):
        ratio = safe_div(cf["dividendsPaid"], fundamentals["income"]["netProfit"])
        if ratio is not None and ratio > 0.3:
            push("股东回报", "强" if ratio > 0.7 else "偏强", f"分红/付息 {ratio:.1f}%",
                 f"年度「分配股利、利润或偿付利息支付的现金」{fmt_money(cf['dividendsPaid'])}，约为净利润的 {ratio:.1f}%。")

    names = [c["name"] for c in (fundamentals.get("concepts") or [])[:6]]
    if names:
        push("题材与赛道标签", "信息", "、".join(names),
             f"该股被同花顺概念库归入 {len(fundamentals['concepts'])} 个概念板块，前 6 个为：" + "、".join(names) + "。")

    strong = sum(1 for i in items if i["level"] == "强")
    weak = sum(1 for i in items if i["level"] == "弱")
    if strong >= 3:
        summary = f"共 {len(items)} 项可量化优势维度中 {strong} 项评定为「强」，主营竞争力数据证据较充分。"
    elif strong >= 1:
        summary = f"共 {len(items)} 项维度中 {strong} 项为「强」、{weak} 项为「弱」，竞争力呈现结构性特征。"
    else:
        summary = f"各项维度未出现「强」评级（{len(items)} 项），竞争力更多体现为跟随行业水平。"
    return {"items": items, "summary": summary, "conceptCount": len(fundamentals.get("concepts") or [])}


def build_scores(fundamentals, performance, valuation, capital, popularity, trend) -> dict:
    ratios, q = fundamentals["ratios"], fundamentals["quality"]
    s = performance["summary"]

    def combine(parts):
        valid = [(v, w) for v, w in parts if v is not None]
        if not valid:
            return None
        tw = sum(w for _, w in valid)
        return rnd(clamp(sum(v * w for v, w in valid) / (tw or 1)), 1)

    quality_parts = []
    if q.get("roe") is not None:
        quality_parts.append((piecewise(q["roe"], [(-5, 8), (0, 18), (5, 38), (10, 55), (15, 70), (20, 82), (25, 90), (35, 97)]), 0.28))
    if ratios.get("grossMargin") is not None:
        quality_parts.append((piecewise(ratios["grossMargin"], [(0, 15), (10, 33), (20, 48), (30, 60), (45, 74), (60, 85), (80, 94)]), 0.16))
    if ratios.get("netMargin") is not None:
        quality_parts.append((piecewise(ratios["netMargin"], [(-10, 8), (0, 22), (5, 40), (10, 55), (15, 66), (25, 80), (40, 92)]), 0.16))
    if q.get("assetsDebtRatio") is not None:
        quality_parts.append((piecewise(q["assetsDebtRatio"], [(8, 96), (20, 90), (30, 82), (45, 70), (60, 55), (75, 36), (90, 20)]), 0.2))
    cf = fundamentals.get("cashflow")
    if cf and cf.get("ocfToProfit") is not None:
        quality_parts.append((piecewise(cf["ocfToProfit"], [(-0.5, 18), (0, 34), (0.3, 48), (0.6, 63), (1, 79), (1.4, 90), (2, 96)]), 0.2))

    growth_parts = []
    if s.get("revenueYoY") is not None:
        growth_parts.append((piecewise(s["revenueYoY"], [(-30, 8), (-10, 26), (0, 42), (10, 58), (20, 70), (35, 82), (60, 92), (100, 97)]), 0.28))
    if s.get("profitYoY") is not None:
        growth_parts.append((piecewise(s["profitYoY"], [(-40, 8), (-15, 24), (0, 42), (15, 62), (30, 76), (60, 88), (120, 96)]), 0.3))
    if s.get("revenueCagr3") is not None:
        growth_parts.append((piecewise(s["revenueCagr3"], [(-10, 15), (0, 40), (10, 60), (20, 74), (35, 88), (60, 96)]), 0.22))
    lq = s.get("latestQuarter") or {}
    if lq.get("profitYoY") is not None:
        growth_parts.append((piecewise(lq["profitYoY"], [(-50, 10), (-15, 28), (0, 45), (15, 62), (40, 80), (80, 92)]), 0.2))

    val_parts = []
    if valuation.get("pePercentile") is not None:
        val_parts.append((clamp(100 - valuation["pePercentile"]), 0.55))
    elif valuation.get("peTtm") and valuation["peTtm"] > 0:
        val_parts.append((piecewise(valuation["peTtm"], [(8, 94), (12, 88), (18, 78), (25, 66), (35, 52), (50, 36), (80, 20), (150, 8)]), 0.55))
    if valuation.get("pbPercentile") is not None:
        val_parts.append((clamp(100 - valuation["pbPercentile"]), 0.45))
    elif valuation.get("pb") and valuation["pb"] > 0:
        val_parts.append((piecewise(valuation["pb"], [(1, 94), (2, 87), (3, 78), (4, 68), (6, 55), (10, 38), (20, 20)]), 0.45))

    cap_parts = []
    if popularity.get("turnoverPercentile") is not None:
        cap_parts.append((popularity["turnoverPercentile"], 0.34))
    if capital.get("volRatio20") is not None:
        cap_parts.append((piecewise(capital["volRatio20"], [(0.4, 28), (0.7, 42), (1, 55), (1.5, 70), (2.2, 82), (3.2, 90), (5, 95)]), 0.24))
    if capital.get("turnoverRate") is not None:
        cap_parts.append((piecewise(capital["turnoverRate"], [(0.1, 32), (0.3, 42), (0.6, 52), (1, 60), (2, 68), (4, 77), (8, 86), (15, 92)]), 0.18))
    pv = capital["priceVolume"].get("upDayTurnoverShare")
    if pv is not None:
        cap_parts.append((piecewise(pv, [(10, 30), (30, 44), (50, 56), (70, 70), (90, 84)]), 0.14))
    if capital["dragonTiger"]["onBoard"]:
        cap_parts.append((86 if capital["dragonTiger"]["netValueSum"] > 0 else 62, 0.1))

    pop_parts = []
    if popularity.get("heatScore") is not None:
        pop_parts.append((popularity["heatScore"], 0.7))
    if popularity.get("dragonTigerCount"):
        pop_parts.append((clamp(60 + popularity["dragonTigerCount"] * 9), 0.15))
    if popularity.get("changePercentile") is not None:
        pop_parts.append((popularity["changePercentile"], 0.15))

    trend_parts = []
    ma_state = {"多头排列": 92, "中期偏强": 78, "震荡整理": 55, "中期偏弱": 34, "空头排列": 16}.get(trend.get("state"))
    if ma_state is not None:
        trend_parts.append((ma_state, 0.34))
    if trend.get("ret20") is not None:
        trend_parts.append((piecewise(trend["ret20"], [(-30, 8), (-15, 22), (-5, 40), (0, 52), (8, 66), (20, 80), (40, 92), (70, 97)]), 0.28))
    if trend.get("ret60") is not None:
        trend_parts.append((piecewise(trend["ret60"], [(-40, 10), (-20, 28), (-5, 45), (5, 58), (20, 72), (45, 86), (80, 95)]), 0.2))
    if trend.get("maxDrawdown60") is not None:
        trend_parts.append((piecewise(trend["maxDrawdown60"], [(-50, 20), (-35, 36), (-25, 50), (-15, 64), (-8, 78), (-3, 90)]), 0.18))

    quality, growth = combine(quality_parts), combine(growth_parts)
    val_score, cap_score = combine(val_parts), combine(cap_parts)
    pop_score, trend_score = combine(pop_parts), combine(trend_parts)

    weights = {"quality": 0.22, "growth": 0.18, "valuation": 0.18, "capital": 0.14, "popularity": 0.10, "trend": 0.18}
    labels = {"quality": "基本面质量", "growth": "成长性", "valuation": "估值性价比",
              "capital": "盘面资金", "popularity": "市场热度", "trend": "技术走势"}
    entries = [(k, v) for k, v in (("quality", quality), ("growth", growth), ("valuation", val_score),
                                   ("capital", cap_score), ("popularity", pop_score), ("trend", trend_score)) if v is not None]
    tw = sum(weights[k] for k, _ in entries) or 1
    overall = rnd(sum(v * weights[k] for k, v in entries) / tw, 1) if entries else None
    grade = None
    if overall is not None:
        grade = ("A（数据面整体强势）" if overall >= 80
                 else "B（数据面偏强）" if overall >= 70
                 else "C（数据面中性偏强）" if overall >= 60
                 else "D（数据面中性）" if overall >= 50
                 else "E（数据面偏弱）" if overall >= 40
                 else "F（数据面弱势）")
    return {
        "overall": overall, "quality": quality, "growth": growth, "valuation": val_score,
        "capital": cap_score, "popularity": pop_score, "trend": trend_score,
        "breakdown": [{"key": k, "label": labels[k], "score": v, "weight": rnd(weights[k] / tw * 100, 1)} for k, v in entries],
        "grade": grade,
    }


# ------------------------------------------------------------------ 相似股
def _shift_date(date: str, days: int) -> str:
    d = dt.date.fromisoformat(date) + dt.timedelta(days=days)
    return d.strftime("%Y-%m-%d")


def find_limit_record(thscode: str, trade_date: Optional[str], last_price) -> Optional[dict]:
    if not trade_date:
        return None
    cands = [d for d in (_shift_date(trade_date, 1), trade_date, _shift_date(trade_date, -1)) if sd.is_trade_date(d)]
    for date in cands:
        pools = sd.parallel_map(lambda k: sd.limit_pool(k, date), ["limit-up-pool", "limit-down-pool", "limit-break-pool"])
        for kind, board in zip(["limit-up-pool", "limit-down-pool", "limit-break-pool"], pools):
            if not board:
                continue
            for it in board.get("items") or []:
                if it.get("thscode") != thscode:
                    continue
                price = num(it.get("last_price"))
                if last_price and price and abs(price - last_price) / last_price > 0.02:
                    continue
                chg = num(it.get("price_change_ratio_pct"))
                return {
                    "kind": "pool",
                    "poolKind": "limit-up" if it.get("continue_day_text") else ("limit-down" if (chg or 0) < 0 else "limit-break"),
                    "date": date, "name": it.get("name"), "lastPrice": price, "changePct": chg,
                    "reason": it.get("limit_up_reason"), "continueDayText": it.get("continue_day_text"),
                    "continueDayCount": num(it.get("continue_day_cnt")), "sealMoney": num(it.get("seal_money")),
                    "maxSealMoney": num(it.get("max_seal_money")), "openTimes": num(it.get("open_times")),
                    "limitUpTime": it.get("limit_up_time"), "firstSealTime": it.get("first_seal_time"),
                    "lastSealTime": it.get("last_seal_time"), "turnoverRate": num(it.get("turnover_ratio_pct")),
                    "isST": bool(it.get("is_st")), "isNew": bool(it.get("is_new")),
                }
    return None


def _align_corr(a: List[dict], b: List[dict]):
    if not a or not b or len(a) < 12 or len(b) < 12:
        return None
    bmap = {x["date"]: x["close"] for x in b}
    pairs = [(x["date"], x["close"], bmap[x["date"]]) for x in a
             if x["date"] in bmap and x.get("close") is not None and bmap[x["date"]] is not None]
    if len(pairs) < 12:
        return None
    ra, rb = [], []
    for i in range(1, len(pairs)):
        if pairs[i - 1][1] and pairs[i - 1][2]:
            ra.append(pairs[i][1] / pairs[i - 1][1] - 1)
            rb.append(pairs[i][2] / pairs[i - 1][2] - 1)
    if len(ra) < 10:
        return None
    return pearson(ra, rb)


def _log_dist_score(a, b, tolerance=math.log(3)):
    if not a or not b or a <= 0 or b <= 0:
        return None
    d = abs(math.log(a / b))
    return clamp(100 * (1 - min(1, d / tolerance)))


def build_peers(thscode, target, mem, market, quote, fundamentals, valuation, hist) -> dict:
    universe = sd.MEMBERSHIP.peer_universe(thscode, 60)
    used: List[str] = []
    res = {"peers": [], "industryStats": None, "universeLabel": None, "universeSize": 0,
           "universeKind": None, "peerIndicators": {}, "usedSources": used}
    if not universe["pool"]:
        return res

    pool = universe["pool"]
    shortlist = pool[:16]
    codes = [p["thscode"] for p in pool]
    vals = sd.valuations(codes[:90])
    hist_list = sd.parallel_map(lambda p: sd.history(p["thscode"], 90), shortlist)
    used += ["valuation.snapshot", "market.history"]
    pool_hist = {p["thscode"]: h for p, h in zip(shortlist, hist_list)}

    pes = [num(v.get("pe_ttm")) for v in vals.values() if num(v.get("pe_ttm")) and 0 < num(v.get("pe_ttm")) < 300]
    pbs = [num(v.get("pb_mrq")) for v in vals.values() if num(v.get("pb_mrq")) and 0 < num(v.get("pb_mrq")) < 40]
    if valuation.get("peTtm") and valuation["peTtm"] > 0:
        pes.append(valuation["peTtm"])
    if valuation.get("pb") and valuation["pb"] > 0:
        pbs.append(valuation["pb"])
    stats = {
        "sampleSize": len(vals), "peMedian": rnd(median(pes)), "pbMedian": rnd(median(pbs)),
        "peCount": len(pes), "pbCount": len(pbs),
        "grossMargin": None,
        "peList": [rnd(p) for p in pes[:150]], "pbList": [rnd(p) for p in pbs[:150]],
    }
    res["industryStats"] = stats
    if valuation.get("peTtm") and valuation["peTtm"] > 0 and stats["peMedian"]:
        valuation["industryPeMedian"] = stats["peMedian"]
        valuation["pePercentile"] = rnd(percentile_rank(pes, valuation["peTtm"]) * 100, 1)
    if valuation.get("pb") and valuation["pb"] > 0 and stats["pbMedian"]:
        valuation["industryPbMedian"] = stats["pbMedian"]
        valuation["pbPercentile"] = rnd(percentile_rank(pbs, valuation["pb"]) * 100, 1)

    target_turn = num((market["map"].get(thscode) or {}).get("turnover"))
    target_ret20 = range_return(hist, 20)
    target_concepts = {c["name"] for c in mem["concepts"]}
    scored = []

    for cand in pool:
        snap = market["map"].get(cand["thscode"]) or {}
        v = vals.get(cand["thscode"]) or {}
        ch = pool_hist.get(cand["thscode"]) or []
        parts = []

        corr = _align_corr(hist, ch)
        if corr is not None:
            parts.append(("corr", 0.30, clamp((corr + 1) / 2 * 100), corr))

        pe_c, pb_c = num(v.get("pe_ttm")), num(v.get("pb_mrq"))
        vs = [x for x in (_log_dist_score(valuation.get("peTtm"), pe_c), _log_dist_score(valuation.get("pb"), pb_c)) if x is not None]
        if vs:
            parts.append(("valuation", 0.20, avg(vs), None))

        size_score = _log_dist_score(target_turn, num(snap.get("turnover")), math.log(6))
        if size_score is not None:
            parts.append(("size", 0.20, size_score, None))

        cand_ret20 = range_return(ch, 20)
        if target_ret20 is not None and cand_ret20 is not None:
            diff = abs(target_ret20 - cand_ret20)
            parts.append(("momentum", 0.15, clamp(100 * (1 - min(1, diff / 45))), cand_ret20))

        cmem = sd.MEMBERSHIP.get(cand["thscode"])
        shared = len(target_concepts & {c["name"] for c in cmem["concepts"]})
        parts.append(("sector", 0.15, clamp(70 + shared * 10) if shared else 60, None))

        if not parts:
            continue
        tw = sum(p[1] for p in parts)
        score = sum(p[2] * p[1] for p in parts) / (tw or 1)
        is_st = "ST" in str(cand.get("name") or "").upper()
        if is_st:
            score *= 0.88
        scored.append({
            "thscode": cand["thscode"], "ticker": cand.get("ticker"), "name": cand.get("name"),
            "similarity": rnd(clamp(score), 1), "isST": is_st,
            "price": rnd(num(snap.get("last_price"))), "changePct": rnd(num(snap.get("price_change_ratio_pct"))),
            "turnover": rnd(num(snap.get("turnover"))), "peTtm": rnd(pe_c), "pb": rnd(pb_c),
            "ret20": rnd(cand_ret20), "corr": rnd(corr, 3) if corr is not None else None,
            "detail": [{"key": p[0], "label": {"corr": "股价节奏", "valuation": "估值", "size": "体量",
                                               "momentum": "动量", "sector": "题材重合"}[p[0]],
                        "score": rnd(p[2], 1)} for p in parts],
        })

    scored.sort(key=lambda x: -x["similarity"])
    top = scored[:5]
    for it in top:
        reasons = []
        if it["corr"] is not None:
            c = it["corr"]
            reasons.append(f"近 60 日股价节奏高度同步（相关 {c:.2f}）" if c > 0.6
                           else f"股价节奏较同步（相关 {c:.2f}）" if c > 0.3
                           else f"股价节奏相关性一般（相关 {c:.2f}）")
        if it["peTtm"] and valuation.get("peTtm"):
            d = (it["peTtm"] / valuation["peTtm"] - 1) * 100
            reasons.append(f"PE(TTM) {it['peTtm']} ，较目标股{'高' if d >= 0 else '低'} {abs(d):.1f}%")
        if it["turnover"] and it["ret20"] is not None:
            reasons.append(f"近 20 日涨幅 {fmt_pct(it['ret20'])}，今日成交 {fmt_money(it['turnover'])}")
        if it["isST"]:
            reasons.append("含 ST 标识，注意风险警示")
        it["reasons"] = reasons[:3]

    # 同业指标（用于行业地位横截面）
    peer_ind: Dict[str, dict] = {}
    if top:
        report = None
        q = fundamentals.get("quality") or {}
        if q.get("report"):
            report = q["report"]
        elif fundamentals.get("latestReport"):
            report = report_string(fundamentals["latestReport"]["fiscalYear"], fundamentals["latestReport"]["period"])
        if report:
            got = sd.parallel_map(lambda p: sd.indicators(p["thscode"], report), top)
            for p, ind in zip(top, got):
                if ind:
                    peer_ind[p["thscode"]] = ind
            if peer_ind:
                used.append("financials.indicators(同业)")
            gms = [num((ind.get("flat") or {}).get("sale_gross_margin")) for ind in peer_ind.values()]
            gms = [g for g in gms if g is not None]
            if gms:
                stats["grossMargin"] = rnd(median(gms))

    res.update({"peers": top, "universeLabel": universe["label"],
                "universeSize": len(pool) + 1, "universeKind": universe["kind"], "peerIndicators": peer_ind})
    return res


# ------------------------------------------------------------------ 多期趋势 / 杜邦
def build_trends(income_annual, balances, cashflows, ind_hist) -> dict:
    years: Dict[int, dict] = {}

    def ensure(y):
        return years.setdefault(y, {"year": y})

    for r in income_annual:
        row = ensure(r.get("fiscal_year"))
        row.update({
            "revenue": num(r.get("operating_income")), "cost": num(r.get("operating_costs")),
            "netProfit": num(r.get("net_profit")), "parentProfit": num(r.get("parent_holder_net_profit")),
            "opProfit": num(r.get("operating_profit")), "salesFee": num(r.get("sales_fee")),
            "manageFee": num(r.get("manage_fee")), "rdExpense": num(r.get("research_and_development_expenses")),
            "eps": num(r.get("basic_eps")), "taxExpense": num(r.get("income_tax_expense")),
            "profitTotal": num(r.get("profit_total")),
        })
    for r in balances:
        row = ensure(r.get("fiscal_year"))
        row.update({
            "assets": num(r.get("assets_total")), "debt": num(r.get("total_debt")), "cash": num(r.get("cash")),
            "receivable": num(r.get("accounts_receivable")), "equity": num(r.get("holder_equity_total")),
        })
    for r in cashflows:
        row = ensure(r.get("fiscal_year"))
        row.update({
            "ocf": num(r.get("act_cash_flow_net")), "capex": num(r.get("pay_fixed_assets_etc_cash")),
            "dividendsPaid": num(r.get("pay_dividends_profits_interest_cash")),
        })

    ordered = [years[y] for y in sorted(years)]
    out = []
    for i, row in enumerate(ordered):
        prev = ordered[i - 1] if i > 0 else None
        rev, cost = row.get("revenue"), row.get("cost")
        gross = (rev - cost) if (rev is not None and cost is not None) else None
        avg_equity = ((row.get("equity") or 0) + (prev.get("equity") or 0)) / 2 if (prev and row.get("equity") is not None and prev.get("equity") is not None) else row.get("equity")
        avg_assets = ((row.get("assets") or 0) + (prev.get("assets") or 0)) / 2 if (prev and row.get("assets") is not None and prev.get("assets") is not None) else row.get("assets")
        out.append({
            "year": row["year"],
            "revenue": rnd(rev), "revenueYoY": rnd(pct_change(rev, prev.get("revenue"))) if prev else None,
            "parentProfit": rnd(row.get("parentProfit")),
            "profitYoY": rnd(pct_change(row.get("parentProfit"), prev.get("parentProfit"))) if prev else None,
            "grossMargin": rnd(safe_div(gross, rev)), "netMargin": rnd(safe_div(row.get("netProfit"), rev)),
            "opMargin": rnd(safe_div(row.get("opProfit"), rev)),
            "salesFeeRatio": rnd(safe_div(row.get("salesFee"), rev)),
            "manageFeeRatio": rnd(safe_div(row.get("manageFee"), rev)),
            "rdRatio": rnd(safe_div(row.get("rdExpense"), rev)),
            "taxRate": rnd(safe_div(row.get("taxExpense"), row.get("profitTotal"))),
            "roe": rnd(safe_div(row.get("parentProfit"), avg_equity)),
            "roa": rnd(safe_div(row.get("netProfit"), avg_assets)),
            "debtRatio": rnd(safe_div(row.get("debt"), row.get("assets"))),
            "cashToAssets": rnd(safe_div(row.get("cash"), row.get("assets"))),
            "receivableToRevenue": rnd(safe_div(row.get("receivable"), rev)),
            "assetTurnover": rnd(rev / avg_assets, 3) if (rev and avg_assets) else None,
            "equityMultiplier": rnd(avg_assets / avg_equity, 3) if (avg_assets and avg_equity) else None,
            "ocf": rnd(row.get("ocf")),
            "ocfToProfit": rnd(safe_div(row.get("ocf"), row.get("netProfit"), 1)),
            "capex": rnd(row.get("capex")),
            "freeCashFlow": rnd((row.get("ocf") or 0) - (row.get("capex") or 0)) if row.get("ocf") is not None else None,
            "dividendsPaid": rnd(row.get("dividendsPaid")), "eps": rnd(row.get("eps"), 3),
        })

    ratio_series = []
    for report, data in (ind_hist or {}).items():
        try:
            y, q = str(report).split("-")
            y, q = int(y), int(q)
        except ValueError:
            continue
        flat = data.get("flat") or {}
        ratio_series.append({
            "label": f"{y}FY" if q == 4 else f"{y}Q{q}", "year": y, "quarter": q,
            "roe": rnd(num(flat.get("index_weighted_avg_roe"))),
            "roeDeducted": rnd(num(flat.get("index_deduct_weighted_avg_roe"))),
            "grossMargin": rnd(num(flat.get("sale_gross_margin"))),
            "netMargin": rnd(num(flat.get("sale_net_interest_ratio"))),
            "debtRatio": rnd(num(flat.get("assets_debt_ratio"))),
            "currentRatio": rnd(num(flat.get("current_ratio"))),
            "quickRatio": rnd(num(flat.get("quick_ratio"))),
            "assetTurnover": rnd(num(flat.get("total_assets_turnover_ratio")), 3),
            "receivableTurnover": rnd(num(flat.get("receive_account_turnover_ratio"))),
            "inventoryTurnover": rnd(num(flat.get("inventory_turnover_ratio")), 3),
            "netProfitCashContent": rnd(num(flat.get("net_profit_cash_content"))),
            "revenueYoY": rnd(num(flat.get("calculate_operating_income_yoy_growth_ratio"))),
            "profitYoY": rnd(num(flat.get("calculate_parent_holder_net_profit_yoy_growth_ratio"))),
        })
    ratio_series.sort(key=lambda r: (r["year"], r["quarter"]))

    conclusions = []
    ann = [y for y in out if y.get("grossMargin") is not None]
    if len(ann) >= 4:
        last, base = ann[-1], ann[-4]

        def tone(d, eps=0.5):
            return "flat" if d is None else ("good" if d > eps else "bad" if d < -eps else "flat")

        gd = (last["grossMargin"] - base["grossMargin"]) if base.get("grossMargin") is not None else None
        if gd is not None:
            conclusions.append({"tone": tone(gd), "text": f"毛利率 {base['year']} 年 {base['grossMargin']}% → {last['year']} 年 {last['grossMargin']}%（{gd:+.2f}pct）" + ("，定价能力增强" if gd > 0.5 else "，价格或成本端承压" if gd < -0.5 else "，基本稳定")})
        nd = (last["netMargin"] - base["netMargin"]) if (base.get("netMargin") is not None and last.get("netMargin") is not None) else None
        if nd is not None:
            conclusions.append({"tone": tone(nd), "text": f"净利率 {base['year']} 年 {base['netMargin']}% → {last['year']} 年 {last['netMargin']}%（{nd:+.2f}pct）" + ("，费用或税负优化" if nd > 0.5 else "，期间费用或税负抬升" if nd < -0.5 else "，变化不大")})
        if base.get("revenueYoY") is not None and last.get("revenueYoY") is not None:
            rd = last["revenueYoY"] - base["revenueYoY"]
            conclusions.append({"tone": "good" if rd > 1 else "bad" if rd < -1 else "flat",
                                "text": f"营收增速 {base['year']} 年 {base['revenueYoY']}% → {last['year']} 年 {last['revenueYoY']}%，{'加速' if rd > 0 else '放缓'} {abs(rd):.1f} 个百分点"})
        ocf = [y for y in out if y.get("ocfToProfit") is not None]
        if len(ocf) >= 3:
            last3 = ocf[-3:]
            below = sum(1 for y in last3 if y["ocfToProfit"] < 1)
            conclusions.append({"tone": "bad" if below == 3 else "flat" if below >= 2 else "good",
                                "text": "近 3 年经营现金流/净利润：" + "、".join(f"{y['year']} {y['ocfToProfit']}" for y in last3)
                                        + ("，连续三年现金含量不足 1 倍" if below == 3 else "")})
        debt = [y for y in out if y.get("debtRatio") is not None]
        if len(debt) >= 3:
            l, b = debt[-1], debt[-3]
            d = l["debtRatio"] - b["debtRatio"]
            conclusions.append({"tone": "good" if d < -0.5 else "bad" if d > 0.5 else "flat",
                                "text": f"资产负债率 {b['year']} {b['debtRatio']}% → {l['year']} {l['debtRatio']}%（{'加杠杆' if d >= 0 else '去杠杆'} {abs(d):.2f}pct）"})

    return {"years": out, "ratioSeries": ratio_series, "conclusions": conclusions}


def build_dupont(trends: dict, fundamentals: dict) -> dict:
    years = [y for y in trends["years"] if y.get("netMargin") is not None and y.get("assetTurnover") is not None]
    if not years:
        return {"available": False, "factors": [], "series": [], "conclusion": None}
    latest = years[-1]
    fy = [r for r in trends["ratioSeries"] if str(r["label"]).endswith("FY") and r.get("roe") is not None]
    fy.sort(key=lambda r: r["year"])
    reported_annual = fy[-1]["roe"] if fy else None
    deduct_annual = fy[-1]["roeDeducted"] if fy else None
    mult = latest.get("equityMultiplier")
    factors = [
        {"key": "netMargin", "label": "净利率（盈利性）", "value": rnd(latest["netMargin"]), "unit": "%",
         "desc": "每 100 元收入留下多少净利润，反映定价权与费用控制"},
        {"key": "assetTurnover", "label": "总资产周转率（效率）", "value": rnd(latest["assetTurnover"], 3), "unit": "次",
         "desc": "资产一年周转几次，反映运营效率与资产使用强度"},
        {"key": "equityMultiplier", "label": "权益乘数（杠杆）", "value": rnd(mult, 3), "unit": "倍",
         "desc": "总资产÷股东权益，反映财务杠杆高低"},
    ]
    series = [{"year": y["year"], "netMargin": y.get("netMargin"), "assetTurnover": y.get("assetTurnover"), "roe": y.get("roe")} for y in years]
    contribution = None
    if len(series) >= 2:
        first = series[0]
        parts = []
        if first.get("netMargin") is not None:
            d = latest["netMargin"] - first["netMargin"]
            parts.append(f"净利率{'提升' if d >= 0 else '下降'} {abs(d):.2f}pct")
        if first.get("assetTurnover") is not None:
            d = latest["assetTurnover"] - first["assetTurnover"]
            parts.append(f"资产周转{'加快' if d >= 0 else '放缓'} {abs(d):.3f} 次")
        if parts:
            contribution = f"{first['year']} 年至 {latest['year']} 年，" + "、".join(parts)
    conclusion = None
    if reported_annual is not None:
        if deduct_annual is not None and reported_annual:
            conclusion = (f"{latest['year']} 年加权 ROE {reported_annual}%、扣非 ROE {deduct_annual}%，"
                          f"扣非/加权 = {deduct_annual / reported_annual * 100:.1f}%（比值越低说明非经常性损益贡献越大）")
        else:
            conclusion = f"{latest['year']} 年加权 ROE {reported_annual}%"
    return {"available": True, "year": latest["year"], "reportedRoeAnnual": reported_annual,
            "roeDeductedAnnual": deduct_annual, "reportedRoeLatest": (fundamentals.get("quality") or {}).get("roe"),
            "reportedPeriod": (fundamentals.get("quality") or {}).get("report"),
            "approxRoe": latest.get("roe"), "factors": factors, "series": series,
            "contribution": contribution, "conclusion": conclusion}


def build_dividends(actions, quote, fundamentals) -> dict:
    events = [a for a in (actions or []) if a.get("dividendPerShare") or a.get("bonusPerShare")]
    if not events:
        return {"available": False, "events": [], "annualDividend": [], "yearsCovered": 0, "consecutiveYears": 0,
                "payoutLast12m": None, "payoutRatio": None, "dividendYieldTTM": None, "perShareSum6y": 0,
                "avgPerYear": 0, "conclusion": "近 10 年无除权除息记录（未分红或数据未覆盖）。"}

    now = dt.datetime.now().timestamp() * 1000
    last12 = [e for e in events if e["exDateMs"] >= now - 365 * 86400000]
    sum12 = sum((e.get("dividendPerShare") or 0) for e in last12)
    price = quote.get("lastPrice")
    shares = (fundamentals.get("size") or {}).get("shares")
    net = (fundamentals.get("income") or {}).get("netProfit")

    by_year: Dict[int, dict] = {}
    for e in events:
        y = int(str(e["exDate"])[:4])
        row = by_year.setdefault(y, {"year": y, "perShare": 0.0, "bonus": 0.0, "times": 0})
        row["perShare"] += e.get("dividendPerShare") or 0
        row["bonus"] += e.get("bonusPerShare") or 0
        row["times"] += 1
    annual = [{"year": r["year"], "perShare": rnd(r["perShare"], 3), "bonus": rnd(r["bonus"], 3), "times": r["times"],
               "total": rnd(r["perShare"] * shares) if shares else None}
              for r in sorted(by_year.values(), key=lambda x: -x["year"])]

    consecutive, expect = 0, max(by_year) if by_year else None
    for y in sorted(by_year, reverse=True):
        if y == expect:
            consecutive += 1
            expect = y - 1
        else:
            break

    payout = None
    if shares and net and net > 0:
        payout = rnd(sum12 * shares / net * 100)
    yld = rnd(sum12 / price * 100) if (price and sum12) else None
    total6 = sum((e.get("dividendPerShare") or 0) for e in events)
    concl = [f"近 {len(by_year)} 年共 {len(events)} 次除权除息，连续分红 {consecutive} 年"]
    if sum12:
        concl.append(f"近 12 个月每股派息合计 {sum12:.3f} 元")
    if yld is not None:
        concl.append(f"按现价折算股息率约 {yld:.2f}%")
    return {
        "available": True,
        "events": [{**e, "dividendPerShare": rnd(e.get("dividendPerShare"), 4), "bonusPerShare": rnd(e.get("bonusPerShare"), 4)} for e in events],
        "annualDividend": annual, "yearsCovered": len(by_year), "consecutiveYears": consecutive,
        "payoutLast12m": rnd(sum12 * shares) if shares else None, "payoutRatio": payout,
        "dividendYieldTTM": yld, "perShareSum6y": rnd(total6, 3),
        "avgPerYear": rnd(total6 / max(1, len(by_year)), 3), "conclusion": "，".join(concl) + "。",
    }


def build_trading_stats(hist, quote, limit_pct: int) -> dict:
    bars = hist[-120:]
    st = {"limitUp": 0, "limitDown": 0, "breakUp": 0}
    details = []
    for i in range(1, len(bars)):
        prev, cur = bars[i - 1], bars[i]
        chg = pct_change(cur.get("close"), prev.get("close"))
        if chg is None:
            continue
        up_price = (prev["close"] * (1 + limit_pct / 100)) if prev.get("close") else None
        if chg >= limit_pct - 0.2:
            st["limitUp"] += 1
            details.append({"date": cur["date"], "type": "涨停", "chg": rnd(chg)})
        elif chg <= -limit_pct + 0.2:
            st["limitDown"] += 1
            details.append({"date": cur["date"], "type": "跌停", "chg": rnd(chg)})
        elif up_price and cur.get("high") is not None and cur["high"] >= up_price - 0.011:
            st["breakUp"] += 1
            details.append({"date": cur["date"], "type": "触及涨停未封", "chg": rnd(chg)})

    turns = [b.get("turnover") for b in bars if b.get("turnover") is not None]
    today_turn = quote.get("turnover")
    turn_pct = rnd(percentile_rank(turns, today_turn) * 100, 0) if (today_turn and len(turns) > 10) else None
    vols = [b.get("volume") for b in bars]
    avg20 = avg(vols[-20:])
    streak = 0
    for b in reversed(bars):
        v = b.get("volume")
        if not v or not avg20:
            break
        if v / avg20 > 1.3:
            streak += 1
        else:
            break

    last10 = bars[-10:]
    price_chg10 = pct_change(last10[-1]["close"], last10[0]["close"]) if len(last10) > 1 else None
    turn_chg10 = None
    if len(last10) >= 6:
        fh = avg([b.get("turnover") for b in last10[:5]])
        lh = avg([b.get("turnover") for b in last10[-5:]])
        if fh and lh:
            turn_chg10 = rnd((lh / fh - 1) * 100, 1)
    divergence = "量价配合正常"
    if price_chg10 is not None and turn_chg10 is not None:
        if price_chg10 > 3 and turn_chg10 < -20:
            divergence = "缩量上涨（上涨动能存疑）"
        elif price_chg10 < -3 and turn_chg10 < -20:
            divergence = "缩量下跌（抛压趋缓）"
        elif price_chg10 > 3 and turn_chg10 > 30:
            divergence = "放量上涨（资金主动进场）"
        elif price_chg10 < -3 and turn_chg10 > 30:
            divergence = "放量下跌（资金撤退）"

    return {
        "limitUpDays120": st["limitUp"], "limitDownDays120": st["limitDown"], "breakUpDays120": st["breakUp"],
        "limitEvents": details[-8:][::-1], "turnoverPercentile120": turn_pct, "volumeStreak": streak,
        "priceChg10": rnd(price_chg10), "turnoverChg10": turn_chg10, "divergence": divergence,
        "avgTurnover5": rnd(avg([b.get("turnover") for b in bars[-5:]])),
        "avgTurnover20": rnd(avg([b.get("turnover") for b in bars[-20:]])),
        "avgTurnover60": rnd(avg([b.get("turnover") for b in bars[-60:]])),
    }


def build_risk_matrix(quote, valuation, fundamentals, performance, capital, popularity, trend, recent5) -> dict:
    rows = []

    def push(dim, item, threshold, value, status):
        rows.append({"dim": dim, "item": item, "threshold": threshold, "value": value, "status": status})

    pep, pbp = valuation.get("pePercentile"), valuation.get("pbPercentile")
    if pep is not None:
        push("估值", "PE 同业分位", ">85% 偏高 / <25% 偏低", f"{pep}%", "alert" if pep > 85 else "ok" if pep < 25 else "watch")
    if pbp is not None:
        push("估值", "PB 同业分位", ">85% 偏高 / <25% 偏低", f"{pbp}%", "alert" if pbp > 85 else "ok" if pbp < 25 else "watch")
    elif valuation.get("pb") is not None:
        pb = valuation["pb"]
        push("估值", "PB 绝对值", ">6 偏高", pb, "alert" if pb > 6 else "ok" if pb < 2 else "watch")
    if valuation.get("pePositive") is False:
        push("估值", "PE 为负", "亏损公司不适用 PE 估值", valuation.get("peTtm"), "alert")

    s = performance["summary"]
    if s.get("profitYoY") is not None:
        v = s["profitYoY"]
        push("业绩", "最新年报归母净利同比", "<0 下滑 / <-20% 大幅下滑", f"{v}%", "alert" if v < -20 else "watch" if v < 0 else "ok")
    if s.get("revenueYoY") is not None:
        push("业绩", "最新年报营收同比", "<0 下滑", f"{s['revenueYoY']}%", "watch" if s["revenueYoY"] < 0 else "ok")
    if s.get("quartersWithPositiveYoY") is not None:
        q = s["quartersWithPositiveYoY"]
        push("业绩", "近 4 季盈利同比为正", "≤2 季视为疲弱", f"{q}/4", "watch" if q <= 2 else "ok")

    cf = fundamentals.get("cashflow")
    if cf and cf.get("ocfToProfit") is not None:
        v = cf["ocfToProfit"]
        push("财务", "经营现金流/净利润", "<0.4 含金量弱 / <0 背离", v, "alert" if v < 0 else "watch" if v < 0.4 else "ok")
    debt = (fundamentals.get("quality") or {}).get("assetsDebtRatio")
    if debt is not None:
        push("财务", "资产负债率", ">65% 偏高", f"{debt}%", "alert" if debt > 65 else "watch" if debt > 50 else "ok")
    cr = (fundamentals.get("quality") or {}).get("currentRatio")
    if cr is not None:
        push("财务", "流动比率", "<1 短期偿债紧张", cr, "alert" if cr < 1 else "watch" if cr < 1.5 else "ok")
    rd = (fundamentals.get("ratios") or {}).get("rdRatio")
    if rd is not None:
        push("财务", "研发费用率", "<1% 偏低（制造业口径）", f"{rd}%", "watch" if rd < 1 else "ok")

    lim = quote["limit"]
    if lim["isLimitUp"]:
        push("交易", "今日涨停", "次日波动大", f"{lim['limitPct']}% 涨停", "alert")
    if lim["isLimitDown"]:
        push("交易", "今日跌停", "抛压集中", f"{lim['limitPct']}% 跌停", "alert")
    if quote.get("isST"):
        push("交易", "ST 风险警示", "退市与流动性风险", quote.get("name"), "alert")
    if capital.get("turnoverRate") is not None:
        tr = capital["turnoverRate"]
        push("交易", "换手率（总股本）", ">12% 短线情绪重", f"{tr}%", "watch" if tr > 12 else "ok")
    if capital.get("volRatio20") is not None:
        vr = capital["volRatio20"]
        push("交易", "量比（vs20日均量）", ">2.5 明显放量", vr, "watch" if vr > 2.5 else "ok")

    if trend.get("volatilityAnnual") is not None:
        v = trend["volatilityAnnual"]
        push("波动", "年化波动率", ">55% 高波动", f"{v}%", "alert" if v > 55 else "watch" if v > 40 else "ok")
    if trend.get("maxDrawdown60") is not None:
        v = trend["maxDrawdown60"]
        push("波动", "60 日最大回撤", "<-30% 趋势破坏", f"{v}%", "alert" if v < -30 else "watch" if v < -15 else "ok")
    if trend.get("state"):
        st = trend["state"]
        push("趋势", "均线形态", "空头排列为弱势", st, "alert" if st == "空头排列" else "watch" if st in ("中期偏弱", "震荡整理") else "ok")
    mdd = recent5["summary"].get("maxDrawdown")
    if mdd is not None and mdd < -8:
        push("趋势", "近 5 日区间回撤", "<-8% 短期走弱", f"{mdd}%", "watch")

    if capital.get("turnoverRank") is not None:
        push("资金", "成交额全市场排名", "排名后 20% 关注度低", f"第 {capital['turnoverRank']} 名",
             "watch" if capital["turnoverRank"] > 4400 else "ok")
    dt = capital.get("dragonTiger") or {}
    if dt.get("onBoard") and (dt.get("netValueSum") or 0) < 0:
        push("资金", "龙虎榜净额", "<0 席位净卖出", fmt_money(dt.get("netValueSum")), "watch")
    if popularity.get("heatScore") is not None:
        h = popularity["heatScore"]
        push("热度", "热度综合分", "<40 关注度偏低", h, "watch" if h < 40 else "ok")

    alert = sum(1 for r in rows if r["status"] == "alert")
    watch = sum(1 for r in rows if r["status"] == "watch")
    ok = sum(1 for r in rows if r["status"] == "ok")
    level = "高风险" if alert >= 3 else "中等风险" if alert >= 1 else "低风险（偏多瑕疵）" if watch >= 4 else "低风险"
    return {"rows": rows, "summary": {"alert": alert, "watch": watch, "ok": ok, "total": len(rows)},
            "level": level,
            "conclusion": f"{len(rows)} 项量化检查中，{alert} 项触发风险阈值、{watch} 项需观察、{ok} 项正常。"}


def build_industry_rank(self_info, peers, peer_indicators, universe_label, universe_size) -> dict:
    f, v, perf, q = self_info["fundamentals"], self_info["valuation"], self_info["performance"], self_info["quote"]
    rows = [{
        "name": self_info["name"], "thscode": self_info["thscode"], "isSelf": True,
        "pe": v.get("peTtm"), "pb": v.get("pb"),
        "roe": f["quality"].get("roe"), "grossMargin": f["ratios"].get("grossMargin"),
        "netMargin": f["ratios"].get("netMargin"),
        "revenueYoY": perf["summary"].get("revenueYoY"), "profitYoY": perf["summary"].get("profitYoY"),
        "turnover": q.get("turnover"),
    }]
    for p in peers:
        flat = ((peer_indicators or {}).get(p["thscode"]) or {}).get("flat") or {}
        rows.append({
            "name": p["name"], "thscode": p["thscode"], "ticker": p.get("ticker"), "isSelf": False,
            "similarity": p.get("similarity"), "pe": p.get("peTtm"), "pb": p.get("pb"),
            "roe": rnd(num(flat.get("index_weighted_avg_roe"))),
            "grossMargin": rnd(num(flat.get("sale_gross_margin"))),
            "netMargin": rnd(num(flat.get("sale_net_interest_ratio"))),
            "revenueYoY": rnd(num(flat.get("calculate_operating_income_yoy_growth_ratio"))),
            "profitYoY": rnd(num(flat.get("calculate_parent_holder_net_profit_yoy_growth_ratio"))),
            "turnover": p.get("turnover"),
        })

    def rank_of(key, higher_better=True):
        vals = [r[key] for r in rows if r.get(key) is not None]
        own = rows[0].get(key)
        if own is None or len(vals) < 3:
            return None
        s = sorted(vals, reverse=higher_better)
        return {"rank": s.index(own) + 1, "total": len(vals), "median": rnd(median(vals)), "avg": rnd(avg(vals))}

    ranks = {k: rank_of(k, hb) for k, hb in (("roe", True), ("grossMargin", True), ("netMargin", True),
                                             ("profitYoY", True), ("pe", False), ("pb", False), ("turnover", True))}
    parts = []
    if ranks["roe"]:
        parts.append(f"ROE 在 {ranks['roe']['total']} 只样本中排第 {ranks['roe']['rank']}（中位 {ranks['roe']['median']}%）")
    if ranks["grossMargin"]:
        parts.append(f"毛利率排第 {ranks['grossMargin']['rank']}（中位 {ranks['grossMargin']['median']}%）")
    if ranks["pe"]:
        parts.append(f"PE 由低到高排第 {ranks['pe']['rank']}（中位 {ranks['pe']['median']}）")
    return {"rows": rows, "ranks": ranks, "sampleSize": len(rows), "universeLabel": universe_label,
            "conclusion": ("，".join(parts) + "。") if parts else "同业样本不足，未计算横截面排名。"}

# ------------------------------------------------------------------ 叙事与速览
def build_narrative(quote, fundamentals, performance, valuation, recent5, trend, capital, popularity,
                    sector, scores, peer_res, moat, limit_rec, trends, dupont, dividends, trading,
                    risk, industry_rank, warnings) -> dict:
    s = performance["summary"]
    highlights: List[str] = []
    risks: List[str] = []

    if scores.get("quality") is not None and scores["quality"] >= 70:
        highlights.append(f"基本面质量评分 {scores['quality']}，ROE {fmt_num((fundamentals['quality'] or {}).get('roe'))}%、"
                          f"毛利率 {fmt_num((fundamentals['ratios'] or {}).get('grossMargin'))}%。")
    if s.get("profitYoY") is not None and s["profitYoY"] > 15:
        highlights.append(f"最新年报归母净利润同比 {fmt_pct(s['profitYoY'])}，成长仍在延续。")
    if scores.get("valuation") is not None and scores["valuation"] >= 70:
        highlights.append(f"估值处于同业偏低位（PE {fmt_num(valuation.get('peTtm'))} / PB {fmt_num(valuation.get('pb'))}），"
                          f"估值性价比评分 {scores['valuation']}。")
    lim = quote["limit"]
    if lim["isLimitUp"]:
        extra = ""
        if limit_rec:
            extra = f"，{limit_rec.get('continueDayText') or '涨停'}"
            if limit_rec.get("sealMoney"):
                extra += f"，封单 {fmt_money(limit_rec['sealMoney'])}"
            if limit_rec.get("reason"):
                extra += f"，涨停原因：{limit_rec['reason']}"
        highlights.append(f"今日{lim['limitPct']}% 涨停（涨停价 {fmt_num(lim['limitUpPrice'])}）{extra}。")
    elif lim["touchedLimitUp"]:
        highlights.append(f"盘中触及 {lim['limitPct']}% 涨停价 {fmt_num(lim['limitUpPrice'])} 但未能封住，"
                          f"收盘回落至 {fmt_num(quote.get('lastPrice'))}。")
    dt = capital.get("dragonTiger") or {}
    if dt.get("onBoard"):
        highlights.append(f"近 {dt['count']} 次龙虎榜合计净额 {fmt_money(dt.get('netValueSum'))}，"
                          f"机构净额 {fmt_money(dt.get('orgNetSum'))}。")
    if popularity.get("inTop30Today"):
        highlights.append(f"位列同花顺热股榜第 {popularity['rankToday']} 名（热度 {popularity.get('heatToday')}），当前关注度处于全市场前列。")
    elif popularity.get("turnoverPercentile") and popularity["turnoverPercentile"] > 90:
        highlights.append(f"成交额排名全市场第 {popularity.get('turnoverRank')} 位，"
                          f"资金关注度处于前 {100 - popularity['turnoverPercentile']:.0f}%。")
    if trend.get("state") in ("多头排列", "中期偏强"):
        highlights.append(f"技术形态「{trend['state']}」，MA20 {fmt_num(trend.get('ma20'))}，现价 {fmt_num(quote.get('lastPrice'))}。")

    if scores.get("valuation") is not None and scores["valuation"] <= 35:
        risks.append(f"估值处于同业偏高位置（PE {fmt_num(valuation.get('peTtm'))} / PB {fmt_num(valuation.get('pb'))}），需警惕估值回落。")
    if s.get("profitYoY") is not None and s["profitYoY"] < 0:
        risks.append(f"最新年报归母净利润同比 {fmt_pct(s['profitYoY'])}，业绩出现下滑。")
    debt = (fundamentals.get("quality") or {}).get("assetsDebtRatio")
    if debt is not None and debt > 65:
        risks.append(f"资产负债率 {fmt_num(debt)}%，杠杆水平偏高。")
    cf = fundamentals.get("cashflow")
    if cf and cf.get("ocfToProfit") is not None and cf["ocfToProfit"] < 0.4:
        risks.append(f"经营现金流为负（{fmt_money(cf.get('operating'))}），与净利润方向背离。" if cf["ocfToProfit"] < 0
                     else f"经营现金流仅为净利润的 {cf['ocfToProfit']:.2f} 倍，利润含金量偏弱。")
    if trend.get("volatilityAnnual") is not None and trend["volatilityAnnual"] > 55:
        risks.append(f"年化波动率 {trend['volatilityAnnual']:.1f}%，价格波动显著高于市场平均。")
    if capital.get("turnoverRate") is not None and capital["turnoverRate"] > 12:
        risks.append(f"日均换手 {capital['turnoverRate']:.2f}%，短线交易情绪较重。")
    if trend.get("maxDrawdown60") is not None and trend["maxDrawdown60"] < -30:
        risks.append(f"近 60 日最大回撤 {trend['maxDrawdown60']:.1f}%，趋势曾出现较大破坏。")
    if dt.get("onBoard") and (dt.get("netValueSum") or 0) < 0:
        risks.append(f"龙虎榜合计净卖出 {fmt_money(abs(dt['netValueSum']))}。")
    if quote.get("isST"):
        risks.append("股票简称含 ST/*ST 标识，存在退市风险警示与特殊交易规则。")
    if lim["isLimitDown"]:
        risks.append(f"今日 {lim['limitPct']}% 跌停（跌停价 {fmt_num(lim['limitDownPrice'])}），抛压集中。")
    if lim["isLimitUp"]:
        risks.append("涨停后次日波动与情绪反转风险较高，追高需注意封单与换手变化。")

    for c in (trends.get("conclusions") or []):
        if c["tone"] == "bad":
            risks.append(c["text"])
        elif c["tone"] == "good":
            highlights.append(c["text"])
    if dupont.get("available") and dupont.get("contribution"):
        (risks if "放缓" in dupont["contribution"] else highlights).append(f"杜邦拆解：{dupont['contribution']}。")
    rr = industry_rank.get("ranks") or {}
    if rr.get("roe") and rr["roe"]["rank"] <= 2:
        highlights.append(f"行业内 ROE 领先：{industry_rank['conclusion']}")
    elif rr.get("roe") and rr["roe"]["total"] >= 5 and rr["roe"]["rank"] > rr["roe"]["total"] - 1:
        risks.append(f"行业内 ROE 垫底：{industry_rank['conclusion']}")
    if dividends.get("available") and dividends.get("dividendYieldTTM") is not None:
        if dividends["dividendYieldTTM"] >= 2:
            highlights.append(f"股东回报：股息率(TTM) {dividends['dividendYieldTTM']}%，连续分红 {dividends['consecutiveYears']} 年。")
        elif dividends["dividendYieldTTM"] < 0.5:
            risks.append(f"股息率(TTM) 仅 {dividends['dividendYieldTTM']}%，现金回报偏低。")
    if any(k in (trading.get("divergence") or "") for k in ("存疑", "撤退")):
        risks.append(f"近 10 日量价特征：{trading['divergence']}（价格 {fmt_pct(trading.get('priceChg10'))}，"
                     f"成交额 {fmt_pct(trading.get('turnoverChg10'))}）。")
    elif "进场" in (trading.get("divergence") or ""):
        highlights.append(f"近 10 日量价特征：{trading['divergence']}（价格 {fmt_pct(trading.get('priceChg10'))}，"
                          f"成交额 {fmt_pct(trading.get('turnoverChg10'))}）。")
    if risk.get("summary", {}).get("alert", 0) >= 3:
        risks.append(f"风险矩阵共 {risk['summary']['alert']} 项触发阈值，整体判定为「{risk.get('level')}」。")

    week = recent5["summary"]
    five = None
    if week.get("cumChangePct") is not None:
        five = (f"近 5 个交易日累计 {fmt_pct(week['cumChangePct'])}，{week['upDays']} 涨 {week['downDays']} 跌，"
                f"区间最大回撤 {week['maxDrawdown']:.2f}%，累计成交 {fmt_money(week.get('cumTurnover'))}")
        if sector.get("relative5") is not None:
            r = sector["relative5"]
            five += f"，{'跑赢' if r >= 0 else '跑输'}所属板块 {abs(r):.2f} 个百分点。"
        else:
            five += "。"
    else:
        five = "近 5 日走势数据不足。"

    headline = " · ".join(x for x in [
        f"{quote['name']}（{quote['ticker']}）",
        f"现价 {fmt_num(quote.get('lastPrice'))}（{fmt_pct(quote.get('changePct'))}）" if quote.get("changePct") is not None else "",
        f"数据面综合评分 {scores['overall']}" if scores.get("overall") is not None else "",
    ] if x)

    peers = peer_res.get("peers") or []
    trend_notes = trends.get("conclusions") or []
    return {
        "headline": headline, "grade": scores.get("grade"), "fiveDayText": five,
        "highlights": highlights[:8], "risks": risks[:8],
        "moatSummary": moat.get("summary"),
        "trendNotes": trend_notes,
        "dupontText": dupont.get("conclusion") or dupont.get("contribution"),
        "industryText": industry_rank.get("conclusion"),
        "riskText": f"{risk.get('conclusion', '')} 整体风险等级：{risk.get('level')}。",
        "dividendText": dividends.get("conclusion"),
        "tradingText": (f"近 120 个交易日：涨停 {trading.get('limitUpDays120')} 次、跌停 {trading.get('limitDownDays120')} 次、"
                        f"触及涨停未封 {trading.get('breakUpDays120')} 次；今日成交额为近 120 日的 "
                        f"{trading.get('turnoverPercentile120') if trading.get('turnoverPercentile120') is not None else '—'} 分位，"
                        f"{trading.get('divergence')}。"),
        "peerText": (f"在「{peer_res.get('universeLabel') or '同行业'}」的 {peer_res.get('universeSize')} 只可比标的中，"
                     f"以下 {len(peers)} 只与该股在估值、体量与股价节奏上最接近。") if peers
                    else "可比公司样本不足，暂无法给出相似度排序。",
        "warnings": warnings,
    }


def build_key_facts(quote, fundamentals, performance, valuation, capital, popularity, trend, recent5,
                    sector, dividends, dupont, universe) -> List[dict]:
    s = performance["summary"]
    facts = [{"label": "价位", "value": f"{fmt_num(quote.get('lastPrice'))}（{fmt_pct(quote.get('changePct'))}）",
              "note": f"振幅 {fmt_num(quote.get('amplitude'))}% · 换手 {fmt_num(capital.get('turnoverRate'))}%"}]
    if fundamentals.get("latestReport"):
        facts.append({"label": "最新年报", "value": f"{fundamentals['latestReport']['fiscalYear']} 年",
                      "note": f"营收 {fmt_money(fundamentals['income'].get('revenue'))}（{fmt_pct(s.get('revenueYoY'))}）"
                              f" · 归母净利 {fmt_money(fundamentals['income'].get('parentNetProfit'))}（{fmt_pct(s.get('profitYoY'))}）"})
    facts.append({"label": "盈利质量",
                  "value": f"ROE {fmt_num((fundamentals['quality'] or {}).get('roe'))}% · 毛利率 {fmt_num((fundamentals['ratios'] or {}).get('grossMargin'))}%",
                  "note": f"净利率 {fmt_num((fundamentals['ratios'] or {}).get('netMargin'))}% · 现金流/净利 "
                          f"{fmt_num((fundamentals.get('cashflow') or {}).get('ocfToProfit'))}"})
    facts.append({"label": "估值",
                  "value": "PE " + fmt_num(valuation.get("peTtm"))
                           + (f"（同业分位 {valuation['pePercentile']}%）" if valuation.get("pePercentile") is not None else ""),
                  "note": "PB " + fmt_num(valuation.get("pb"))
                          + (f"（分位 {valuation['pbPercentile']}%）" if valuation.get("pbPercentile") is not None else "")
                          + f" · 同业 PE 中位 {fmt_num(valuation.get('industryPeMedian'))}"})
    facts.append({"label": "盘面资金",
                  "value": f"成交 {fmt_money(capital.get('turnover'))}"
                           + (f"（全市场第 {capital['turnoverRank']}）" if capital.get("turnoverRank") else ""),
                  "note": f"量比 {fmt_num(capital.get('volRatio20'))} · {capital['priceVolume'].get('pattern')}"})
    facts.append({"label": "市场热度",
                  "value": f"热股榜第 {popularity['rankToday']} 名" if popularity.get("rankToday") else "未上榜",
                  "note": f"热度分 {fmt_num(popularity.get('heatScore'), 1)} · 近 30 日均排名 {fmt_num(popularity.get('avgRank30'), 0)}"})
    wk = recent5["summary"]
    sector_note = ""
    if sector.get("relative5") is not None:
        sector_note = (f"{'跑赢' if sector['relative5'] >= 0 else '跑输'}板块 "
                       f"{abs(sector['relative5']):.2f}pct · ")
    facts.append({"label": "近 5 日",
                  "value": f"{fmt_pct(wk.get('cumChangePct'))}（{wk['upDays']} 涨 {wk['downDays']} 跌）",
                  "note": sector_note + f"最大回撤 {fmt_num(wk.get('maxDrawdown'))}%"})
    facts.append({"label": "技术位置", "value": trend.get("state"),
                  "note": f"MA20 {fmt_num(trend.get('ma20'))} · 20 日 {fmt_pct(trend.get('ret20'))} · 年化波动 {fmt_num(trend.get('volatilityAnnual'))}%"})
    if dupont.get("available"):
        fs = {f["key"]: f for f in dupont["factors"]}
        facts.append({"label": "杜邦 ROE",
                      "value": f"净利率 {fmt_num(fs['netMargin']['value'])}% × 周转 {fmt_num(fs['assetTurnover']['value'], 3)} × 杠杆 {fmt_num(fs['equityMultiplier']['value'], 2)}",
                      "note": f"≈ ROE {fmt_num(dupont.get('approxRoe'))}%（{dupont.get('year')} 年加权口径 {fmt_num(dupont.get('reportedRoeAnnual'))}%）"})
    if dividends.get("available"):
        facts.append({"label": "股东回报", "value": f"股息率(TTM) {fmt_num(dividends.get('dividendYieldTTM'))}%",
                      "note": f"连续分红 {dividends.get('consecutiveYears')} 年 · 近 10 年每股累计 {fmt_num(dividends.get('perShareSum6y'), 3)} 元"})
    if universe.get("label"):
        facts.append({"label": "行业归属",
                      "value": " / ".join(i["name"] for i in (fundamentals.get("industry") or [])) or universe["label"],
                      "note": f"可比样本 {universe.get('size')} 只 · 概念 {len(fundamentals.get('concepts') or [])} 个"})
    return facts
