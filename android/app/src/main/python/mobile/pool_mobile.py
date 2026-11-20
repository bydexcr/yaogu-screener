# -*- coding: utf-8 -*-
"""
pool_mobile.py —— 安卓版候选池构建（不依赖 DuckDB）
思路：先用「T-1 涨停池 ∪ 炸板池」做种子（覆盖绝大多数妖股），
     再对每只种子拉近 40 根日K，复用 PC 版 strategy.evaluate_stock 判定 C1~C4，
     并合并涨停池标签（连板/封板时间/封单/题材）与评分。
"""
from __future__ import annotations

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))          # 复用 PC 版 strategy.py
from strategy import (Candidate, DailyBar, enrich_with_limit_pool,  # noqa: E402
                      evaluate_stock, is_st)

import rest_client as api  # noqa: E402


def _lu_map(items: List[dict]) -> Dict[str, dict]:
    out = {}
    for it in items:
        code = it.get("thscode")
        if not code:
            continue
        out[code] = {
            "continue_day_cnt": it.get("continue_day_cnt"),
            "continue_day_text": it.get("continue_day_text") or "",
            "limit_up_time": it.get("limit_up_time") or "",
            "limit_up_reason": it.get("limit_up_reason") or "",
            "seal_money": it.get("seal_money"),
            "max_seal_money": it.get("max_seal_money"),
        }
    return out


def _bars_to_daily(items: List[dict], until_date: str) -> List[DailyBar]:
    bars = []
    for r in items:
        d = api.from_ms(int(r.get("date_ms", 0)))
        if d > until_date:
            continue
        try:
            bars.append(DailyBar(date=d,
                                 open=float(r["open_price"]), high=float(r["high_price"]),
                                 low=float(r["low_price"]), close=float(r["close_price"]),
                                 volume=float(r["volume"]), amount=float(r["turnover"])))
        except (KeyError, TypeError, ValueError):
            continue
    bars.sort(key=lambda b: b.date)
    return bars


def build_pool(t1_date: str, t2_date: str, strat: dict, cache_dir: Path,
               force: bool = False, exclude_st: bool = True,
               exclude_bj: bool = True, diag: Optional[Dict[str, object]] = None) -> List[Candidate]:
    """构建并缓存候选池；返回 Candidate 列表（按评分降序）。

    diag（可选出参）：写入 seeds / missing / reason，供上层把"为什么 0 只"讲清楚。
      reason: ok / no_seed（T-1 涨停池+炸板池为空）/ api_error / no_bars
    """
    d = diag if diag is not None else {}
    d.setdefault("seeds", 0)
    d.setdefault("missing", 0)
    d.setdefault("reason", "ok")

    cache = cache_dir / f"pool_{t1_date}.json"
    if not force and cache.exists():
        try:
            data = json.loads(cache.read_text(encoding="utf-8"))
            cands = data.get("candidates") or []
            # 空池缓存不可信：可能是 T-1 涨停池还没发布时写下的，读到就重建（自愈）
            if data.get("t1_date") == t1_date and cands:
                print(f"[缓存] 候选池 {len(cands)} 只来自 {cache.name}", flush=True)
                return [Candidate(**e) for e in cands]
            if data.get("t1_date") == t1_date and not cands:
                print(f"[缓存] {cache.name} 是空池（可能上次 T-1 数据未就绪），忽略并重建", flush=True)
        except Exception:
            pass

    print("[扫描] 拉取 T-1 涨停池 / 炸板池…", flush=True)
    try:
        lu_items = api.limit_up_pool(t1_date)
        bk_items = api.limit_break_pool(t1_date)
    except Exception as e:      # 接口失败/限流：不要冒泡成整轮失败，如实报告
        print(f"[扫描] 涨停池/炸板池获取失败: {type(e).__name__}: {e}", flush=True)
        d["reason"] = "api_error"
        return []
    lu_map = _lu_map(lu_items)

    seeds: Dict[str, dict] = {}
    for it in lu_items:
        code = it.get("thscode")
        if code:
            seeds[code] = {"name": it.get("name") or code, "is_st": bool(it.get("is_st"))}
    for it in bk_items:
        code = it.get("thscode")
        if code and code not in seeds:
            seeds[code] = {"name": it.get("name") or code, "is_st": False}
    d["seeds"] = len(seeds)
    if not seeds:
        # T-1 涨停池/炸板池都是空的：多半是数据还没发布，下一轮重试
        print(f"[种子] 涨停池 0 + 炸板池 0 → T-1({t1_date}) 数据可能尚未发布", flush=True)
        d["reason"] = "no_seed"
        return []
    print(f"[种子] 涨停池 {len(lu_items)} + 炸板池 {len(bk_items)} -> 去重 {len(seeds)} 只，逐只拉日K…", flush=True)

    end_ms = api.to_ms(t1_date) + 20 * 3600 * 1000     # T-1 收盘后
    start_ms = api.to_ms(t1_date) - 75 * 86400 * 1000  # 往前约 75 天，保证 ≥31 根K线

    # 先剔除 ST（不发请求），余下的并发拉日K：原来逐只串行，100 只种子要 1~2 分钟
    targets = [(code, meta) for code, meta in seeds.items()
               if not (meta.get("is_st") or is_st(meta["name"]))]
    try:
        workers = max(1, min(int(os.environ.get("POOL_WORKERS", "5")), 8))
    except ValueError:
        workers = 5
    print(f"[并发] {len(targets)} 只种子 × {workers} 线程拉日K…", flush=True)

    def _fetch(item):
        code, meta = item
        try:
            raw = api.history(code, start_ms, end_ms)
        except Exception as e:      # 网络/接口错误只影响这一只
            return code, meta, None, e
        try:
            return code, meta, _bars_to_daily(raw, until_date=t1_date), None
        except Exception as e:
            return code, meta, None, e

    pool: List[Candidate] = []
    missing = 0
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(_fetch, it) for it in targets]
        for fut in as_completed(futures):
            code, meta, bars, err = fut.result()
            done += 1
            if err is not None:
                missing += 1
                print(f"  [跳过] {code} 日K获取失败: {err}", flush=True)
            elif bars is not None and len(bars) >= 31:
                cand = evaluate_stock(bars, code, meta["name"], t1_date, t2_date, strat,
                                      exclude_st=exclude_st, exclude_bj=exclude_bj)
                if cand:
                    pool.append(cand)
            if done % 20 == 0:
                print(f"  …{done}/{len(targets)} 已处理，当前命中 {len(pool)}", flush=True)

    enrich_with_limit_pool(pool, lu_map)
    # 并发抓取后顺序不定，排序用 thscode 兜底，保证同样输入永远同样输出
    pool.sort(key=lambda c: (-c.score, -c.t1_pct, c.thscode))

    # 缓存：空池不落盘，避免把"数据没到"固化成当天的空结果
    d["missing"] = missing
    if not pool:
        d["reason"] = "no_bars" if missing else "ok"
        print(f"[结果] 候选 0 只 (T-1={t1_date}, 种子缺日K {missing} 只)，不写缓存，下轮重试",
              flush=True)
        return []
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"t1_date": t1_date,
                                 "candidates": [c.to_dict() for c in pool]},
                                ensure_ascii=False), encoding="utf-8")
    try:
        import csv
        with open(cache_dir / f"pool_{t1_date}.csv", "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["thscode", "name", "score", "t1_pct", "continue_text",
                        "limit_up_time", "seal_money_yi", "t1_amount_yi", "volume_ratio", "reason"])
            for c in pool:
                w.writerow([c.thscode, c.name, c.score, c.t1_pct, c.continue_text,
                            c.limit_up_time, c.seal_money_yi, c.t1_amount_yi,
                            c.volume_ratio, c.limit_up_reason])
    except Exception:
        pass

    print(f"[结果] 候选 {len(pool)} 只 (T-1={t1_date}, 种子缺日K {missing} 只)", flush=True)
    for c in pool[:10]:
        col = c.continue_text or ("涨停" if c.t1_limitup else "大涨")
        print(f"   {c.thscode:11s} {c.name:<8s} 评分{c.score:>5.1f} {col:>4} "
              f"{c.limit_up_time:>6} T-1涨幅{c.t1_pct:+.2f}% 额{c.t1_amount_yi:.1f}亿", flush=True)
    return pool
