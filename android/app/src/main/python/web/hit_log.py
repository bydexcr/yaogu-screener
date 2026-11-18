# -*- coding: utf-8 -*-
"""
hit_log.py —— 历史命中回顾（这套低吸策略最近到底准不准）

命中日志两端各写一种，读取端都认：
  PC 引擎   output/alerts_{T-1}.csv / alerts_deep_{T-1}.csv   ← 文件名是 T-1，真实日期取 hit_time
  安卓引擎  data_mobile/session_hits_{T}.json                 ← 文件名就是 T

收益口径与离线 backtest.py **完全一致**（两边数字可以直接对照）：
  买入价 = T 日开盘价（09:25 集合竞价成交的那一笔）
  r0 = T 日收盘 / 买入价 - 1      dd = T 日最低 / 买入价 - 1
r0_stop = 当日最低触及 -3% 时按 -3% 计，否则等于 r0（日内止损口径，主指标）
  rk = T+k 日收盘 / 买入价 - 1    o1 = T+1 日开盘 / 买入价 - 1（次日高开还是低开）

价格统一取**前复权**日线；日志里记的原始开盘价只用于展示，不参与计算
（除权后原始价与前复权价不可混用）。
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import os
import pathlib
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple

MAX_HITS = 200
SUSPECT_PCT = 1.0        # 日志开盘涨幅与真实开盘涨幅差超过 1 个百分点 → 标"疑似假命中"
STOP_PCT = -3.0          # 日内止损线(%)：当日最低触及即离场
SCHEMA = 3               # 结果结构版本：改字段就 +1，否则会读到旧结构的缓存
BAR_TIMEOUT_CACHE_TTL = 600          # 结果缓存 10 分钟（命中日志本身是低频数据）
WORKERS = 5


# ------------------------------------------------------------------ 小工具
def _sd():
    """兼容「包内导入」与「同目录平铺导入」（Chaquopy/APK 与 PC 两种加载方式）。"""
    try:
        from . import stock_data as sd
    except ImportError:  # pragma: no cover - 平铺加载时才走到
        import stock_data as sd          # noqa: F401
    return sd


def _f(v) -> Optional[float]:
    """转 float，坏值一律 None。"""
    try:
        if v is None or v == "":
            return None
        f = float(v)
        return f if f == f and abs(f) != float("inf") else None
    except (TypeError, ValueError):
        return None


def _r2(v) -> Optional[float]:
    f = _f(v)
    return round(f, 2) if f is not None else None


def _hit_date(hit_time, fallback: str) -> str:
    """命中日期以 hit_time 为准。

    PC 的 alerts 文件名是 **T-1**，直接用文件名会整体错一天；hit_time 才是 T 日的时间戳。
    """
    s = str(hit_time or "")[:10]
    if len(s) == 10 and s[4] == "-" and s[7] == "-":
        return s
    return fallback or ""


def _norm(rec: dict, day: str, zone: str) -> dict:
    return {
        "date": _hit_date(rec.get("hit_time"), day),
        "thscode": str(rec.get("thscode") or "").strip(),
        "name": str(rec.get("name") or "").strip(),
        "zone": zone,
        "open_pct": _r2(rec.get("open_pct")),
        "buy_logged": _r2(rec.get("open_price")),
        "score": _f(rec.get("score")),
        "t1_pct": _r2(rec.get("t1_pct")),
        "continue": str(rec.get("continue_text") or "").strip(),
        "hit_time": str(rec.get("hit_time") or ""),
    }


# ------------------------------------------------------------------ 读日志
def _from_alert_csv(path: pathlib.Path) -> List[dict]:
    """PC 端 alerts_{T-1}.csv / alerts_deep_{T-1}.csv。"""
    zone = "deep" if "_deep" in path.stem else "main"
    stem_date = path.stem.split("_")[-1]
    out = []
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as fh:
            for rec in csv.DictReader(fh):
                h = _norm(rec, stem_date, zone)
                if h["thscode"]:
                    out.append(h)
    except Exception:  # noqa: BLE001 - 单个文件坏掉不影响其它
        return out
    return out


def _from_session_json(path: pathlib.Path) -> List[dict]:
    """安卓端 session_hits_{T}.json：{date, hits:[...], deep_hits:[...]}。"""
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:  # noqa: BLE001
        return []
    stem_date = path.stem.split("_")[-1]
    day = str(data.get("date") or stem_date)
    out = []
    for key, zone in (("hits", "main"), ("deep_hits", "deep")):
        for rec in (data.get(key) or []):
            if not isinstance(rec, dict):
                continue
            h = _norm(rec, day, zone)
            if h["thscode"]:
                out.append(h)
    return out


def candidate_dirs() -> List[pathlib.Path]:
    """命中日志可能落脚的目录。

    两端写法不同、目录也不同（PC 写 output/，安卓写 data_mobile/），这里把常见的都试一遍；
    返回值会原样回给前端，方便一眼看出"到底在哪儿找过"。
    """
    dirs: List[pathlib.Path] = []
    env = os.environ.get("YAOGU_HITS_DIR", "").strip()
    if env:
        dirs.append(pathlib.Path(env))
    try:
        w = _sd()._writable_dir()
    except Exception:  # noqa: BLE001
        w = None
    if w is not None:
        dirs.append(pathlib.Path(w))
        for name in ("output", "data", "data_mobile"):
            dirs.append(pathlib.Path(w) / name)
            dirs.append(pathlib.Path(w).parent / name)
    here = pathlib.Path(__file__).resolve().parent
    for base in (here, here.parent, pathlib.Path.cwd()):
        for name in ("output", "data_mobile", "data"):
            dirs.append(base / name)
    seen, out = set(), []
    for d in dirs:
        try:
            key = str(d.resolve()).lower()
        except Exception:  # noqa: BLE001
            continue
        if key in seen:
            continue
        seen.add(key)
        if d.is_dir():
            out.append(d)
    return out


def load_hits(days: int = 30, dirs: Optional[List[pathlib.Path]] = None) -> Tuple[List[dict], dict]:
    """读全部命中日志，按日期窗口过滤。返回 (hits, meta)。"""
    dirs = list(dirs) if dirs is not None else candidate_dirs()
    cutoff = (dt.date.today() - dt.timedelta(days=max(1, int(days)))).isoformat()

    hits: Dict[Tuple[str, str, str], dict] = {}
    files: List[dict] = []
    for d in dirs:
        paths = sorted(list(d.glob("alerts_*.csv")) + list(d.glob("session_hits_*.json")))
        for p in paths:
            rows = _from_alert_csv(p) if p.suffix == ".csv" else _from_session_json(p)
            kept = [h for h in rows if h["date"] and h["date"] >= cutoff]
            if not kept:
                continue                       # 空文件或整份都在窗口外，不算命中来源
            files.append({"dir": str(d), "file": p.name, "rows": len(kept)})
            for h in kept:
                key = (h["date"], h["thscode"], h["zone"])
                old = hits.get(key)
                # 同一笔命中可能被两端都记过：保留信息更全的那条
                if old is None or (old.get("score") is None and h.get("score") is not None):
                    hits[key] = h

    rows = sorted(hits.values(), key=lambda x: (x["date"], x["thscode"]), reverse=True)[:MAX_HITS]
    last = max((h["date"] for h in hits.values()), default="")
    meta = {
        "dirs": [str(d) for d in dirs],
        "files": files,
        "cutoff": cutoff,
        "found": len(rows),
        "last_hit": last,
    }
    return rows, meta


# ------------------------------------------------------------------ 统计
def _stats(vals: List[float]) -> Optional[dict]:
    """与 backtest.py 的 _stats 同口径：n / mean / median / win / worst / best。"""
    v = [x for x in vals if x is not None]
    if not v:
        return None
    pos = sum(1 for x in v if x > 0)
    return {
        "n": len(v),
        "mean": round(statistics.mean(v), 2),
        "median": round(statistics.median(v), 2),
        "win": round(pos / len(v) * 100, 1),
        "worst": round(min(v), 2),
        "best": round(max(v), 2),
    }


def summarize(hits: List[dict], bars_by_code: Dict[str, List[dict]], horizon: int = 3):
    """纯函数：把命中记录 + 日线拼成逐笔结果与统计。

    日线取不到（或 T 日还没收盘）时标 pending/missing，**不计入胜率**，
    避免把"还没发生"当成"亏了"。
    """
    rows = []
    for h in hits:
        bars = bars_by_code.get(h["thscode"]) or []
        idx = next((i for i, b in enumerate(bars) if b.get("date") == h["date"]), None)
        row = dict(h)
        row.update({"buy": None, "r0": None, "r0_stop": None, "stopped": False,
                    "dd": None, "o1": None,
                    "prev_close": None, "gap_real": None, "suspect": False,
                    "status": "missing"})
        if idx is not None:
            bar = bars[idx]
            buy = _f(bar.get("open"))
            prev_close = _f(bars[idx - 1].get("close")) if idx > 0 else None
            row["prev_close"] = round(prev_close, 2) if prev_close else None
            if buy and buy > 0:
                # 日志里的 open_pct 来自 09:25 的快照，而快照的 open_price 在集合竞价
                # 阶段可能还是**前一日**的值（真实案例：记为 -5.35%，实际开盘 +6.91%）。
                # 这里用前复权日线自己算一遍，差得多就标 suspect，不当权威。
                if prev_close:
                    row["gap_real"] = _r2((buy / prev_close - 1) * 100)
                    if h.get("open_pct") is not None:
                        row["suspect"] = abs(row["gap_real"] - h["open_pct"]) >= SUSPECT_PCT
                fwd = bars[idx + 1: idx + 1 + horizon]
                row["status"] = "done" if len(fwd) >= horizon else "pending"
                row["buy"] = round(buy, 2)
                row["r0"] = _r2((_f(bar.get("close")) / buy - 1) * 100)
                low = _f(bar.get("low"))
                row["dd"] = _r2((low / buy - 1) * 100) if low is not None else None
                # 日内口径（-STOP_PCT 止损）：当日最低触及止损位就按止损价离场，否则持到收盘
                if row["dd"] is not None and row["dd"] <= STOP_PCT:
                    row["r0_stop"] = _r2(STOP_PCT)
                    row["stopped"] = True
                else:
                    row["r0_stop"] = row["r0"]
                    row["stopped"] = False
                if fwd:
                    o = _f(fwd[0].get("open"))
                    row["o1"] = _r2((o / buy - 1) * 100) if o is not None else None
                for k in range(1, horizon + 1):
                    row["r%d" % k] = None
                    if len(fwd) >= k:
                        c = _f(fwd[k - 1].get("close"))
                        row["r%d" % k] = _r2((c / buy - 1) * 100) if c is not None else None
        rows.append(row)

    # r0 / r0_stop 是「日内口径」的主指标；o1 与 r1..r3 保留作参考
    keys = ["r0", "r0_stop", "dd", "o1"] + ["r%d" % k for k in range(1, horizon + 1)]
    stats = {k: _stats([r.get(k) for r in rows]) for k in keys}

    groups = []
    for zone, label in (("main", "低开命中（主栏）"), ("deep", "深水低吸（副栏）")):
        sub = [r for r in rows if r.get("zone") == zone]
        if not sub:
            continue
        groups.append({
            "key": zone, "label": label, "n": len(sub),
            "stats": {k: _stats([r.get(k) for r in sub]) for k in ("r0", "r0_stop", "dd", "r1")},
        })

    coverage = {
        "total": len(rows),
        "done": sum(1 for r in rows if r["status"] == "done"),
        "pending": sum(1 for r in rows if r["status"] == "pending"),
        "missing": sum(1 for r in rows if r["status"] == "missing"),
        "suspect": sum(1 for r in rows if r.get("suspect")),
    }
    return rows, stats, groups, coverage


# ------------------------------------------------------------------ 取日线
def _fetch_bars(codes: List[str]) -> Tuple[Dict[str, List[dict]], List[str]]:
    sd = _sd()

    bars: Dict[str, List[dict]] = {}
    failed: List[str] = []

    def one(code: str):
        try:
            return code, sd.history(code, 300), None
        except Exception as e:  # noqa: BLE001
            return code, [], "%s: %s" % (type(e).__name__, e)

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for code, data, err in ex.map(one, codes):
            if err or not data:
                failed.append(code)
            else:
                bars[code] = data
    return bars, failed


_cache_lock = threading.Lock()


def _cache_file() -> Optional[pathlib.Path]:
    try:
        return pathlib.Path(_sd()._writable_dir()) / "hits_stats.json"
    except Exception:  # noqa: BLE001
        return None


def _fingerprint(meta: dict, days: int, horizon: int) -> str:
    parts = ["v%d" % SCHEMA]
    parts += ["%s:%d" % (f["file"], f["rows"]) for f in meta.get("files", [])]
    parts.append("d%d-h%d" % (days, horizon))
    return "|".join(parts)


def build(days: int = 30, horizon: int = 3, dirs: Optional[List[pathlib.Path]] = None) -> dict:
    """历史命中回顾：读日志 → 拉前复权日线 → 逐笔算收益 → 汇总。"""
    try:
        days = max(1, min(365, int(days)))
    except (TypeError, ValueError):
        days = 30
    try:
        horizon = max(1, min(5, int(horizon)))
    except (TypeError, ValueError):
        horizon = 3

    hits, meta = load_hits(days, dirs)
    base = {"ok": True, "days": days, "horizon": horizon, "meta": meta}
    if not hits:
        return dict(base, rows=[], stats={}, groups=[], coverage={"total": 0, "done": 0,
                    "pending": 0, "missing": 0},
                    note="还没读到命中日志。PC 版命中会写到 output/alerts_*.csv，"
                         "安卓版写到 data_mobile/session_hits_*.json；"
                         "跑过几个交易日后这里才有数据。")

    fp = _fingerprint(meta, days, horizon)
    cf = _cache_file()
    now = dt.datetime.now().timestamp()
    if cf is not None:
        try:
            cached = json.loads(cf.read_text(encoding="utf-8"))
            if cached.get("fingerprint") == fp and now - float(cached.get("at", 0)) < BAR_TIMEOUT_CACHE_TTL:
                return dict(cached["payload"], cached=True)
        except Exception:  # noqa: BLE001
            pass

    codes = sorted({h["thscode"] for h in hits})
    bars, failed = _fetch_bars(codes)
    rows, stats, groups, coverage = summarize(hits, bars, horizon)

    payload = dict(base, rows=rows, stats=stats, groups=groups, coverage=coverage,
                   failed=failed, cached=False)
    if not stats.get("r1"):
        payload["note"] = ("命中记录有了，但对应日线还没取到（或 T 日尚未收盘），"
                           "暂时算不出收益。")
    if cf is not None:
        try:
            with _cache_lock:
                cf.write_text(json.dumps({"fingerprint": fp, "at": now, "payload": payload},
                                         ensure_ascii=False), encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass
    return payload
