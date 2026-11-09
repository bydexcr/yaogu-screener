# -*- coding: utf-8 -*-
"""
stock_data.py —— 个股分析数据层（手机端，直连同花顺 REST）
  * 复用 mobile/rest_client.py 的鉴权、重试与基址配置
  * 进程内 TTL 缓存 + 板块成分索引落盘缓存（首次约 1~2 分钟，之后秒开）
  * 与 PC 版 stock-analyzer/lib/api.js 保持同构的返回结构，便于前端复用渲染
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for _p in (str(ROOT), str(ROOT / "mobile")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import rest_client as rc  # noqa: E402

MAX_WORKERS = int(os.environ.get("STOCK_MAX_WORKERS", "6"))

# ------------------------------------------------------------------ 缓存
_cache: Dict[str, tuple] = {}
_cache_lock = threading.Lock()
_inflight: Dict[str, threading.Event] = {}


def _now() -> float:
    return time.time()


def cache_get(key: str):
    with _cache_lock:
        hit = _cache.get(key)
        if not hit:
            return None
        expire, value = hit
        if expire < _now():
            _cache.pop(key, None)
            return None
        return value


def cache_set(key: str, value, ttl: float):
    with _cache_lock:
        _cache[key] = (_now() + ttl, value)
        if len(_cache) > 800:
            cut = _now()
            for k in [k for k, v in _cache.items() if v[0] < cut]:
                _cache.pop(k, None)
    return value


def cached(key: str, ttl: float, fn):
    """带缓存与并发去重：同一 key 同时只执行一次"""
    hit = cache_get(key)
    if hit is not None:
        return hit
    with _cache_lock:
        ev = _inflight.get(key)
        owner = ev is None
        if owner:
            ev = threading.Event()
            _inflight[key] = ev
    if not owner:
        ev.wait(timeout=60)
        return cache_get(key)
    try:
        value = fn()
        return cache_set(key, value, ttl)
    finally:
        with _cache_lock:
            _inflight.pop(key, None)
        ev.set()


def _num(v):
    if isinstance(v, (int, float)):
        return float(v)
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _round(v, d: int = 2):
    if v is None:
        return None
    try:
        return round(float(v), d)
    except (TypeError, ValueError):
        return None


def _ms_of_date(date_str: str) -> int:
    return rc.to_ms(date_str)


def _date_of_ms(ms: int) -> str:
    return rc.from_ms(int(ms))


def _today() -> str:
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).strftime("%Y-%m-%d")


# ------------------------------------------------------------------ 基础接口
def calendar() -> List[str]:
    return cached("calendar", 12 * 3600, lambda: rc.calendar_days())


def last_trade_date() -> Optional[str]:
    days = calendar()
    return days[-1] if days else None


def is_trade_date(date: str) -> bool:
    days = calendar()
    if not days:
        return True
    if date < days[0] or date > days[-1]:
        return True
    return date in set(days)


def search(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    q = (query or "").strip()
    if not q:
        return []

    def _do():
        d = rc._get("/api/meta/tickers/search",
                    {"q": q, "limit": limit, "asset_type": "a-share,a-share-index"})
        return [{
            "thscode": it.get("thscode"), "ticker": it.get("ticker"),
            "name": it.get("name"), "exchange": it.get("exchange"),
            "assetType": it.get("asset_type"),
        } for it in (d.get("item") or [])]

    return cached(f"search:{q}:{limit}", 6 * 3600, _do)


def resolve_stock(query: str) -> Dict[str, Any]:
    tokens = search(query, 12)
    stocks = [t for t in tokens if t.get("assetType") == "a-share"]
    if not stocks:
        raise LookupError(f"未找到与「{query}」匹配的 A 股标的")
    q = str(query).strip().upper()
    for s in stocks:
        if s["ticker"] == q or s["thscode"] == q:
            return s
    return stocks[0]


def snapshot(codes: Iterable[str]) -> Dict[str, dict]:
    codes = [c for c in codes if c]
    key = "snap:" + ",".join(sorted(set(codes)))

    def _do():
        d = rc._get("/api/a-share/prices/snapshot", {"thscodes": ",".join(codes)})
        return {it["thscode"]: it for it in (d.get("item") or []) if it.get("thscode")}

    return cached(key, 30, _do)


def market_snapshot_all() -> Dict[str, Any]:
    """全市场快照（分页），返回 {map, rows, total}"""

    def _do():
        rows: List[dict] = []
        offset = 0
        total = None
        for _ in range(4):
            d = rc._get("/api/a-share/prices/snapshot", {"limit": 5000, "offset": offset})
            total = d.get("total")
            items = d.get("item") or []
            rows.extend(items)
            if not items or (total and len(rows) >= int(total)):
                break
            offset += len(items)
        mp = {r["thscode"]: r for r in rows if r.get("thscode")}
        return {"map": mp, "rows": rows, "total": int(total or len(rows))}

    return cached("market:all", 60, _do)


def valuations(codes: Iterable[str]) -> Dict[str, dict]:
    lst = sorted(set(c for c in codes if c))
    out: Dict[str, dict] = {}
    chunks = [lst[i:i + 90] for i in range(0, len(lst), 90)]

    def _one(chunk):
        d = rc._get("/api/a-share/valuations/snapshot", {"thscodes": ",".join(chunk)})
        return d.get("item") or []

    for chunk in chunks:
        key = "val:" + ",".join(chunk)
        for it in cached(key, 10 * 60, lambda c=chunk: _one(c)):
            out[it.get("thscode")] = it
    return out


def history(thscode: str, days: int = 300) -> List[dict]:
    def _do():
        end = int(time.time() * 1000)
        start = end - days * 24 * 3600 * 1000
        items = rc.history(thscode, start, end, adjust="forward")
        out = []
        for it in items:
            close = _num(it.get("close_price"))
            if close is None:
                continue
            ms = it.get("date_ms")
            out.append({
                "dateMs": int(ms) if ms else None,
                "date": _date_of_ms(ms) if ms else None,
                "open": _num(it.get("open_price")),
                "high": _num(it.get("high_price")),
                "low": _num(it.get("low_price")),
                "close": close,
                "volume": _num(it.get("volume")),
                "turnover": _num(it.get("turnover")),
            })
        out.sort(key=lambda r: r["dateMs"] or 0)
        return out

    return cached(f"hist:{thscode}:{days}", 10 * 60, _do)


def statements(thscode: str, kind: str, period: str, limit: int) -> List[dict]:
    endpoint = {
        "income": "/api/a-share/financials/income-statements",
        "balance-sheet": "/api/a-share/financials/balance-sheets",
        "cash-flow": "/api/a-share/financials/cash-flow-statements",
    }[kind]

    def _do():
        d = rc._get(endpoint, {"thscode": thscode, "period": period, "limit": limit})
        rows = d.get("item") or []
        order = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4, "FY": 5}
        rows.sort(key=lambda r: (r.get("fiscal_year") or 0, order.get(str(r.get("fiscal_period")), 0)))
        return rows

    return cached(f"stmt:{kind}:{thscode}:{period}:{limit}", 6 * 3600, _do)


def indicators(thscode: str, report: str, retries: int = 0) -> Optional[dict]:
    def _do():
        try:
            d = rc._get("/api/a-share/financials/indicators",
                        {"thscode": thscode, "report": report}, retries=max(1, retries))
        except Exception:
            return None
        flat = {}
        for group in d.get("abilities") or []:
            for ind in group.get("indicators") or []:
                flat[ind.get("index_id")] = _num(ind.get("value"))
        return {"report": d.get("report") or report, "abilities": d.get("abilities") or [], "flat": flat}

    return cached(f"ind:{thscode}:{report}", 6 * 3600, _do)


def indicator_history(thscode: str, reports: Iterable[str]) -> Dict[str, dict]:
    reports = [r for r in dict.fromkeys(reports) if r]
    out: Dict[str, dict] = {}
    if not reports:
        return out
    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(reports))) as pool:
        for report, data in zip(reports, pool.map(lambda r: indicators(thscode, r), reports)):
            if data:
                out[report] = data
    return out


def corporate_actions(thscode: str, years: int = 10) -> List[dict]:
    def _do():
        end = _today()
        start = (dt.date.today() - dt.timedelta(days=365 * years)).strftime("%Y-%m-%d")
        try:
            d = rc._get("/api/a-share/corporate-actions/adjustment-factors",
                        {"thscode": thscode, "from": start, "to": end}, retries=1)
        except Exception:
            return []
        rows = []
        for it in d.get("item") or []:
            ms = it.get("ex_date_ms")
            if not ms:
                continue
            rows.append({
                "exDate": _date_of_ms(ms),
                "exDateMs": int(ms),
                "dividendPerShare": _num(it.get("dividend_per_share")),
                "bonusPerShare": _num(it.get("per_share_bonus")),
            })
        rows.sort(key=lambda r: -r["exDateMs"])
        return rows

    return cached(f"actions:{thscode}:{years}", 6 * 3600, _do)


def hot_stock(period: str = "day") -> List[dict]:
    def _do():
        d = rc._get("/api/a-share/special-data/hot-stock-list", {"period": period})
        return [{
            "thscode": it.get("thscode"), "ticker": it.get("ticker"), "name": it.get("name"),
            "rank": _num(it.get("rank")), "heat": _num(it.get("heat")),
            "rankChange": _num(it.get("rank_change")), "rankTrend": it.get("rank_trend"),
        } for it in (d.get("item") or [])]

    return cached(f"hot:{period}", 120, _do)


def hot_trend(thscode: str, days: int = 120) -> List[dict]:
    def _do():
        end = _today()
        start = (dt.date.today() - dt.timedelta(days=days)).strftime("%Y-%m-%d")
        try:
            d = rc._get("/api/a-share/special-data/hot-stock-rank-trend",
                        {"thscode": thscode, "start_date": start, "end_date": end}, retries=1)
        except Exception:
            return []
        rows = [{"date": it.get("date"), "rank": _num(it.get("rank"))} for it in (d.get("item") or [])]
        rows = [r for r in rows if r["rank"] is not None and r["date"]]
        rows.sort(key=lambda r: str(r["date"]))
        return rows

    return cached(f"hottrend:{thscode}:{days}", 120, _do)


def skyrocket(period: str = "day") -> List[dict]:
    def _do():
        try:
            d = rc._get("/api/a-share/special-data/skyrocket-list", {"period": period}, retries=1)
        except Exception:
            return []
        return [{
            "thscode": it.get("thscode"), "ticker": it.get("ticker"), "name": it.get("name"),
            "rank": _num(it.get("rank")), "heat": _num(it.get("heat")), "rankChange": _num(it.get("rank_change")),
        } for it in (d.get("item") or [])]

    return cached(f"sky:{period}", 120, _do)


def dragon_tiger(date: Optional[str]) -> Dict[str, Any]:
    def _do():
        params = {"board_type": "all"}
        if date:
            params["date"] = date
        try:
            d = rc._get("/api/a-share/special-data/dragon-tiger-list", params, retries=1)
        except Exception:
            return {"tradeDate": date, "items": []}
        items = []
        for it in d.get("stock_items") or []:
            items.append({
                "thscode": it.get("thscode"), "name": it.get("name"),
                "change": _num(it.get("change")),
                "concepts": [c.get("name") for c in (it.get("concept_list") or [])],
                "netValue": _num(it.get("net_value")), "netRate": _num(it.get("net_rate")),
                "buyValue": _num(it.get("buy_value")), "sellValue": _num(it.get("sell_value")),
                "orgNetValue": _num(it.get("org_net_value")),
                "hotMoneyNetValue": _num(it.get("hot_money_net_value")),
                "rangeDays": _num(it.get("range_days")) or 1,
                "limitReason": it.get("limit_reason"),
            })
        return {"tradeDate": d.get("trade_date") or date, "items": items}

    return cached(f"dt:{date or 'latest'}", 20 * 60, _do)


def limit_pool(kind: str, date: str, size: int = 200) -> Dict[str, Any]:
    """kind: limit-up-pool / limit-down-pool / limit-break-pool"""
    path = f"/api/a-share/special-data/{kind}"

    def _do():
        items: List[dict] = []
        total = None
        for page in range(1, 4):
            try:
                d = rc._get(path, {"date_ms": _ms_of_date(date), "page": page, "size": size}, retries=1)
            except Exception:
                break
            total = (d.get("pagination") or {}).get("total", total)
            part = d.get("item") or []
            items.extend(part)
            if len(part) < size:
                break
        return {"date": date, "items": items, "total": int(total) if total is not None else len(items)}

    return cached(f"pool:{kind}:{date}", 300, _do)


def ladder() -> Optional[dict]:
    def _do():
        try:
            d = rc._get("/api/a-share/special-data/limit-up-ladder", {}, retries=1)
        except Exception:
            return None
        for it in d.get("item") or []:
            return {"date": it.get("date"), "boards": it.get("boards") or {}, "days": len(d.get("item") or [])}
        return None

    return cached("ladder", 300, _do)


def index_catalog(tag: str) -> List[dict]:
    def _do():
        d = rc._get("/api/a-share-index/catalog/ths-index-list", {"tag": tag}, retries=1)
        return [{"code": it.get("thscode"), "name": it.get("name")} for it in (d.get("item") or [])]

    return cached(f"idxcat:{tag}", 12 * 3600, _do)


def index_constituents(code: str) -> List[dict]:
    def _do():
        try:
            d = rc._get("/api/a-share-index/constituents/ths-stock-list", {"thscode": code}, retries=1)
        except Exception:
            return []
        return [{"thscode": it.get("thscode"), "ticker": it.get("ticker"), "name": it.get("name")}
                for it in (d.get("item") or [])]

    return cached(f"idxcon:{code}", 12 * 3600, _do)


def index_snapshot(codes: Iterable[str]) -> Dict[str, dict]:
    lst = sorted(set(c for c in codes if c))
    if not lst:
        return {}
    out: Dict[str, dict] = {}
    chunks = [lst[i:i + 250] for i in range(0, len(lst), 250)]

    def _one(chunk):
        d = rc._get("/api/a-share-index/prices/snapshot", {"thscodes": ",".join(chunk)}, retries=1)
        return d.get("item") or []

    for chunk in chunks:
        for it in cached("idxsnp:" + ",".join(chunk), 120, lambda c=chunk: _one(c)):
            out[it.get("thscode")] = it
    return out


def index_history(code: str, days: int = 90) -> List[dict]:
    def _do():
        end = int(time.time() * 1000)
        start = end - days * 24 * 3600 * 1000
        try:
            d = rc._get("/api/a-share-index/prices/historical",
                        {"thscode": code, "start": start, "end": end, "interval": "1d"}, retries=1)
        except Exception:
            return []
        rows = []
        for it in d.get("item") or []:
            close = _num(it.get("close_price"))
            ms = it.get("date_ms")
            if close is None or not ms:
                continue
            rows.append({"dateMs": int(ms), "date": _date_of_ms(ms), "close": close})
        rows.sort(key=lambda r: r["dateMs"])
        return rows

    return cached(f"idxhist:{code}:{days}", 10 * 60, _do)


# ------------------------------------------------------------------ 行业/概念成分索引
class MembershipIndex:
    """把「板块 → 成分股」建成反向索引；首次构建约 700+ 次请求（1~2 分钟），按日落盘。"""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = Path(cache_dir or os.environ.get("YAOGU_DATA_DIR") or (ROOT / "data_mobile"))
        self._forward: Dict[str, List[dict]] = {"industries": [], "concepts": []}
        self._reverse: Dict[str, Dict[str, list]] = {}
        self._name_map: Optional[Dict[str, str]] = None
        self._status = "idle"
        self._progress = {"done": 0, "total": 0}
        self._lock = threading.Lock()
        self._date: Optional[str] = None

    # ---- 持久化
    def _file(self, date: str) -> Path:
        return self.cache_dir / f"stock_membership_{date}.json"

    def _load_latest(self) -> bool:
        try:
            files = sorted(self.cache_dir.glob("stock_membership_*.json"))
        except Exception:
            return False
        for f in reversed(files[-3:]):
            try:
                payload = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            if not payload.get("industries") or not payload.get("concepts"):
                continue
            with self._lock:
                self._forward = {"industries": payload["industries"], "concepts": payload["concepts"]}
                self._date = payload.get("date") or f.stem.replace("stock_membership_", "")
                self._status = "ready"
                self._rebuild_reverse()
            return True
        return False

    def _save(self, date: str):
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            payload = {"date": date, "industries": self._forward["industries"], "concepts": self._forward["concepts"]}
            self._file(date).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    def _rebuild_reverse(self):
        rev: Dict[str, Dict[str, list]] = {}
        for bucket in ("industries", "concepts"):
            for idx in self._forward[bucket]:
                for m in idx["members"]:
                    rev.setdefault(m["thscode"], {"industries": [], "concepts": []})[bucket].append(
                        {"code": idx["code"], "name": idx["name"]})
        self._reverse = rev
        self._name_map = None

    # ---- 构建
    def build(self, max_workers: int = 6) -> Dict[str, Any]:
        today = _today()
        self._status = "running"
        catalogs: List[tuple] = []
        for tag, bucket in (("industry", "industries"), ("cn_concept", "concepts")):
            for it in index_catalog(tag):
                catalogs.append((bucket, it["code"], it["name"]))
        self._progress = {"done": 0, "total": len(catalogs)}
        forward: Dict[str, List[dict]] = {"industries": [], "concepts": []}

        def work(job):
            bucket, code, name = job
            members = index_constituents(code)
            self._progress["done"] += 1
            if members:
                return bucket, {"code": code, "name": name, "members": members}
            return bucket, None

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            for bucket, idx in pool.map(work, catalogs):
                if idx:
                    forward[bucket].append(idx)

        with self._lock:
            self._forward = forward
            self._date = today
            self._status = "ready"
            self._rebuild_reverse()
        self._save(today)
        return {"industries": len(forward["industries"]), "concepts": len(forward["concepts"])}

    def ensure(self) -> Dict[str, Any]:
        """同步确保索引可用：当日缓存 → 历史缓存（后台补当日）→ 现建"""
        if self._status == "ready" and self._date == _today():
            return self.stats()
        with self._lock:
            if self._status == "ready" and self._date == _today():
                return self.stats()
            if self._status == "running":
                return self.stats()
            today_file = self._file(_today())
            if today_file.exists():
                try:
                    payload = json.loads(today_file.read_text(encoding="utf-8"))
                    self._forward = {"industries": payload["industries"], "concepts": payload["concepts"]}
                    self._date = payload.get("date") or _today()
                    self._status = "ready"
                    self._rebuild_reverse()
                    return self.stats()
                except Exception:
                    pass
            if self._load_latest():
                return self.stats()
        self.build()
        return self.stats()

    def ensure_async(self):
        if self._status in ("ready", "running"):
            return
        threading.Thread(target=self._safe_build, daemon=True).start()

    def _safe_build(self):
        try:
            self._load_latest()
            if self._date != _today():
                self.build()
        except Exception as e:  # noqa: BLE001
            print(f"[stock] 板块索引构建失败: {e}")

    # ---- 查询
    def get(self, thscode: str) -> Dict[str, list]:
        hit = self._reverse.get(thscode)
        if not hit:
            return {"industries": [], "concepts": []}
        return {
            "industries": sorted(hit["industries"], key=lambda x: x["code"]),
            "concepts": list(hit["concepts"]),
        }

    def index_by_code(self, code: str) -> Optional[dict]:
        for bucket in ("industries", "concepts"):
            for idx in self._forward[bucket]:
                if idx["code"] == code:
                    return idx
        return None

    def name_map(self) -> Dict[str, str]:
        if self._name_map is None:
            mp: Dict[str, str] = {}
            for bucket in ("industries", "concepts"):
                for idx in self._forward[bucket]:
                    for m in idx["members"]:
                        mp.setdefault(m["thscode"], m["name"])
            self._name_map = mp
        return self._name_map

    def peer_universe(self, thscode: str, limit: int = 60) -> Dict[str, Any]:
        m = self.get(thscode)
        pools = []
        for idx in m["industries"]:
            full = self.index_by_code(idx["code"])
            if full and len(full["members"]) >= 3:
                pools.append({"code": idx["code"], "name": idx["name"], "members": full["members"], "kind": "industry"})
        if not pools:
            for idx in m["concepts"][:3]:
                full = self.index_by_code(idx["code"])
                if full and len(full["members"]) >= 3:
                    pools.append({"code": idx["code"], "name": idx["name"], "members": full["members"], "kind": "concept"})
        if not pools:
            return {"pool": [], "label": None, "kind": None}
        pools.sort(key=lambda p: len(p["members"]))
        primary = next((p for p in pools if len(p["members"]) >= 5), pools[-1])
        return {
            "pool": [x for x in primary["members"] if x["thscode"] != thscode][:limit],
            "label": primary["name"], "kind": primary["kind"],
            "alternatives": [p["name"] for p in pools if p is not primary][:3],
        }

    def stats(self) -> Dict[str, Any]:
        return {
            "status": self._status, "date": self._date,
            "industries": len(self._forward["industries"]), "concepts": len(self._forward["concepts"]),
            "stocksIndexed": len(self._reverse), "progress": dict(self._progress),
        }


MEMBERSHIP = MembershipIndex()


def parallel_map(fn, items: Iterable, workers: int = MAX_WORKERS):
    items = list(items)
    if not items:
        return []
    with ThreadPoolExecutor(max_workers=min(workers, len(items))) as pool:
        return list(pool.map(fn, items))
