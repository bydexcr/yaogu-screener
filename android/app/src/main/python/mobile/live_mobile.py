# -*- coding: utf-8 -*-
"""
live_mobile.py —— 安卓 Termux 版主程序（无需 PC、无需 Node CLI、无需 DuckDB）
  - 数据：同花顺 REST（rest_client.py）
  - 候选：T-1 涨停池 ∪ 炸板池 为种子，逐只拉日K → C1~C4（复用 PC 版 strategy.py）
  - 盘中：30 秒快照校验 C5（主栏 -8~-5% / 深水 -10~-7%），并跟踪承接/走弱
  - 看板：复用 PC 版 web/index.html（http://127.0.0.1:8311）
  - 通知：Termux 系统通知 / Server酱

用法：
  python live_mobile.py                # 常驻（30s 轮询）
  python live_mobile.py --once         # 只跑一轮
  python live_mobile.py --as-of 2026-09-29   # 回放某日（用历史K线校验 C5）
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))      # strategy.py / web/
sys.path.insert(0, str(HERE))      # rest_client / pool_mobile / notify_mobile

from strategy import apply_cond5, intraday_flags  # noqa: E402
import rest_client as api                        # noqa: E402
import pool_mobile as pm                         # noqa: E402
import notify_mobile                             # noqa: E402

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Asia/Shanghai")
except Exception:
    TZ = dt.timezone(dt.timedelta(hours=8))

GREEN = "\033[92m"; RED = "\033[91m"; YELLOW = "\033[93m"; CYAN = "\033[96m"
BOLD = "\033[1m"; DIM = "\033[2m"; RESET = "\033[0m"


def now_local() -> dt.datetime:
    return dt.datetime.now(TZ)


def now_str() -> str:
    return now_local().strftime("%Y-%m-%d %H:%M:%S")


class MobileEngine:
    def __init__(self, cfg: dict, data_dir: Path):
        self.cfg = cfg
        self.strat = cfg.get("strategy", {})
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        dr = self.strat.get("deep_open_pct_range") or [-10.0, -7.0]
        self.deep_range = [float(dr[0]), float(dr[1])] if dr and len(dr) == 2 else None
        self.calendar: list = []
        self.t_date = self.t1_date = self.t2_date = ""
        self.offline = False
        self.pool = []
        self.pool_key = ""
        self.cycle_no = 0
        self.watch: dict = {}
        self.hits: list = []
        self.deep_hits: list = []
        self.events: list = []
        self.sentiment: dict = {}
        self.errors: list = []
        self.phase = ""
        self.phase_time = 0.0
        self.source_label = "同花顺REST"
        self.data_ready = True
        self.state: dict = {}
        self._notify_on = bool(cfg.get("notify", {}).get("enabled", True))

    # ---------------------------------------------------------- 日期
    def load_calendar(self):
        self.calendar = api.calendar_days()

    def resolve_dates(self, as_of: str | None = None) -> bool:
        if as_of:
            if as_of not in self.calendar:
                return False
            self.t_date, self.offline = as_of, True
        else:
            today = now_local().strftime("%Y-%m-%d")
            if today in self.calendar:
                self.t_date = today
            else:
                prev = [d for d in self.calendar if d < today]
                self.t_date = prev[-1] if prev else today
            self.offline = False
        if self.t_date not in self.calendar:
            return False
        idx = self.calendar.index(self.t_date)
        if idx < 2:
            return False
        self.t1_date, self.t2_date = self.calendar[idx - 1], self.calendar[idx - 2]
        return True

    # ---------------------------------------------------------- 候选池
    def ensure_pool(self, force=False):
        if self.pool and self.pool_key == self.t1_date and not force:
            return True
        print(f"[日期] T={self.t_date}  T-1={self.t1_date}  T-2={self.t2_date}", flush=True)
        self.pool = pm.build_pool(self.t1_date, self.t2_date, self.strat,
                                  self.data_dir, force=force,
                                  exclude_st=bool(self.cfg.get("exclude_st", True)),
                                  exclude_bj=bool(self.cfg.get("exclude_bj", True)))
        self.pool_key = self.t1_date
        self.watch, self.hits, self.deep_hits, self.events = {}, [], [], []
        return True

    # ---------------------------------------------------------- 行情
    def _snapshot_quotes(self, codes):
        out = {}
        for i in range(0, len(codes), 100):
            chunk = codes[i:i + 100]
            snap = api.snapshot(chunk)
            for code, it in snap.items():
                out[code] = {
                    "open": _f(it.get("open_price")),
                    "prev": _f(it.get("prev_price")),
                    "last": _f(it.get("last_price")),
                    "pct": _f(it.get("price_change_ratio_pct")),
                }
        return out

    def _replay_quotes(self):
        """回放：用 T 日历史K线的 开/收 作为 C5 依据。"""
        start = api.to_ms(self.t_date) - 10 * 86400 * 1000
        end = api.to_ms(self.t_date) + 20 * 3600 * 1000
        out = {}
        for c in self.pool:
            try:
                bars = api.history(c.thscode, start, end)
                row = next((r for r in bars if api.from_ms(int(r["date_ms"])) == self.t_date), None)
                if not row:
                    continue
                out[c.thscode] = {"open": float(row["open_price"]), "prev": c.t1_close,
                                  "last": float(row["close_price"]),
                                  "pct": (float(row["close_price"]) / c.t1_close - 1) * 100 if c.t1_close else None}
            except Exception:
                continue
        return out

    # ---------------------------------------------------------- 单轮
    def run_cycle(self) -> dict:
        self.cycle_no += 1
        res = {"ts": now_str(), "t_date": self.t_date, "t1_date": self.t1_date,
               "t2_date": self.t2_date, "pool_size": len(self.pool),
               "new_hits": [], "deep_new": [], "errors": list(self.errors[-3:])}
        if not self.pool:
            self._update_state(res)
            return res
        codes = [c.thscode for c in self.pool]
        try:
            quotes = self._replay_quotes() if self.offline else self._snapshot_quotes(codes)
        except Exception as e:
            self.errors.append(f"{now_str()} 行情获取失败: {e}")
            res["errors"] = list(self.errors[-3:])
            self._update_state(res)
            return res

        for cand in self.pool:
            q = quotes.get(cand.thscode)
            if not q:
                continue
            apply_cond5(cand, open_price=q["open"], prev_close=q["prev"], last_price=q["last"],
                        last_pct=q["pct"], cfg_strategy=self.strat)
            self._apply_zone(cand)
            self._record_zone_hit(cand, res)
        for cand in self.pool:
            self._track_sig(cand)
        res["candidates"] = [c.to_dict() for c in self.pool]
        self._update_state(res)
        return res

    def _apply_zone(self, cand):
        p = cand.open_pct
        if p is None:
            cand.zone, cand.hit = "", False
            return
        lo, hi = self.strat.get("t_open_pct_range", [-8.0, -5.0])
        if lo <= p <= hi:
            cand.zone, cand.hit = "main", True
            return
        if self.deep_range and self.deep_range[0] <= p <= self.deep_range[1]:
            cand.zone, cand.hit = "deep", True
            return
        cand.zone, cand.hit = "", False

    def _record_zone_hit(self, cand, res: dict):
        zone = cand.zone
        if zone not in ("main", "deep"):
            return
        now = now_str()
        if zone == "main":
            if cand.thscode in {r["thscode"] for r in self.hits}:
                return
            rec = cand.to_dict(); rec["hit_time"] = now
            self.hits.append(rec); res["new_hits"].append(rec)
            if self._notify_on:
                notify_mobile.send("hit", f"★低开命中 {cand.name}({cand.thscode})",
                                   f"T-1 {cand.t1_pct:+.2f}% 开盘{cand.open_pct:+.2f}% 现价{cand.last_price}")
        else:
            if cand.thscode in {r["thscode"] for r in self.deep_hits}:
                return
            rec = cand.to_dict(); rec["hit_time"] = now
            self.deep_hits.append(rec); res["deep_new"].append(rec)
            if self._notify_on:
                notify_mobile.send("deephit", f"💧深水低吸 {cand.name}({cand.thscode})",
                                   f"T-1 {cand.t1_pct:+.2f}% 开盘{cand.open_pct:+.2f}% 现价{cand.last_price}")

    def _track_sig(self, cand):
        if not cand.hit:
            cand.sig = ""
            return
        confirm, broken = intraday_flags(self.cfg.get("intraday"), cand.hit,
                                         cand.open_price, cand.last_price, cand.last_pct)
        w = self.watch.setdefault(cand.thscode, {"confirm": False, "broken": False})
        now = now_str()
        if confirm and not w["confirm"]:
            w["confirm"] = True
            rec = {"ts": now, "type": "confirm", "thscode": cand.thscode, "name": cand.name,
                   "open_pct": cand.open_pct, "last_pct": cand.last_pct, "last_price": cand.last_price}
            self.events.append(rec)
            if self._notify_on:
                notify_mobile.send("confirm", f"✅承接确认 {cand.name}", f"现价{cand.last_price} 收复开盘{cand.open_price}")
        if broken and not w["broken"]:
            w["broken"] = True
            rec = {"ts": now, "type": "broken", "thscode": cand.thscode, "name": cand.name,
                   "open_pct": cand.open_pct, "last_pct": cand.last_pct, "last_price": cand.last_price}
            self.events.append(rec)
            if self._notify_on:
                notify_mobile.send("broken", f"⚠走弱预警 {cand.name}", f"现价{cand.last_price}（{cand.last_pct:+.2f}%）")
        cand.sig = "confirm" if w["confirm"] else ("broken" if w["broken"] else "hit")

    # ---------------------------------------------------------- 状态
    def _update_state(self, res: dict):
        self.state = {
            "updated": res.get("ts", now_str()), "cycle": self.cycle_no,
            "source": self.source_label, "phase": self.phase, "offline": self.offline,
            "data_ready": self.data_ready,
            "t_date": self.t_date, "t1_date": self.t1_date, "t2_date": self.t2_date,
            "pool_size": len(self.pool), "interval": self.cfg.get("interval_seconds", 30),
            "open_range": self.strat.get("t_open_pct_range", [-8, -5]),
            "zones": {"main": self.strat.get("t_open_pct_range", [-8, -5]),
                      "deep": self.deep_range or [-10, -7],
                      "deep_enabled": bool(self.deep_range)},
            "sentiment": self.sentiment,
            "watch": {"hit": sum(1 for c in self.pool if c.zone == "main"),
                      "deep": sum(1 for c in self.pool if c.zone == "deep"),
                      "confirm": sum(1 for c in self.pool if c.sig == "confirm"),
                      "broken": sum(1 for c in self.pool if c.sig == "broken")},
            "events": list(reversed(self.events[-80:])),
            "hits": list(reversed(self.hits[-200:])),
            "deep_hits": list(reversed(self.deep_hits[-200:])),
            "new_hits": res.get("new_hits", []),
            "errors": res.get("errors", []),
            "candidates": res.get("candidates", [c.to_dict() for c in self.pool]),
        }

    def state_json(self) -> str:
        return json.dumps(self.state, ensure_ascii=False, default=str)


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def session_phase(now: dt.datetime, t_date: str, interval: int):
    if now.strftime("%Y-%m-%d") != t_date:
        return "非交易日", False, 120
    hhmm = now.strftime("%H:%M")
    if hhmm < "08:45":
        return "盘前静默", False, 120
    if hhmm < "09:15":
        return "盘前准备", False, 30
    if hhmm < "09:30":
        return "集合竞价", True, 10
    if hhmm < "11:30":
        return "连续竞价", True, interval
    if hhmm < "13:00":
        return "午间休市", False, 120
    if hhmm < "15:00":
        return "连续竞价", True, interval
    return "已收盘", False, 300


def main() -> int:
    ap = argparse.ArgumentParser(description="妖股低吸 · 安卓Termux版")
    ap.add_argument("--config", default=str(HERE / "config_mobile.json"))
    ap.add_argument("--interval", type=int, default=None)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--as-of", default=None, metavar="YYYY-MM-DD")
    ap.add_argument("--no-web", action="store_true")
    ap.add_argument("--port", type=int, default=None)
    ap.add_argument("--refresh-pool", action="store_true")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8-sig"))
    if args.interval:
        cfg["interval_seconds"] = args.interval
    interval = max(5, int(cfg.get("interval_seconds", 30)))
    data_dir = Path(os.environ.get("YAOGU_DATA_DIR") or (HERE / cfg.get("data_dir", "data_mobile")))

    engine = MobileEngine(cfg, data_dir)
    web = None
    if cfg.get("web", {}).get("enabled", True) and not args.no_web and not args.as_of:
        try:
            from web.dashboard import start_dashboard
            web = start_dashboard(engine, host=cfg["web"].get("host", "127.0.0.1"),
                                  port=args.port or cfg["web"].get("port", 8311),
                                  token=cfg["web"].get("token", ""))
            print(f"[看板] 本机看板: http://127.0.0.1:{web.port}", flush=True)
        except Exception as e:
            print(f"[看板] 启动失败: {e}", flush=True)

    print(BOLD + "妖股低吸 · 手机版(Termux)".center(60, "=") + RESET)
    print("数据源: 同花顺 REST；候选: T-1涨停池∪炸板池→逐只日K；盘中30s快照验证")
    print("=" * 60)

    engine.load_calendar()
    if not engine.resolve_dates(as_of=args.as_of):
        print(f"[错误] 交易日历中不存在 {args.as_of or '今日'}"); return 1
    print(f"[日期] T={engine.t_date}  T-1={engine.t1_date}  T-2={engine.t2_date}", flush=True)

    if not engine.ensure_pool(force=args.refresh_pool):
        print("[错误] 候选池构建失败"); return 2

    if args.once or args.as_of:
        try:
            engine.sentiment = {} if engine.offline else api.sentiment()
        except Exception:
            pass
        res = engine.run_cycle()
        print(f"[{res['ts']}] 轮询#{engine.cycle_no} 候选:{len(engine.pool)} "
              f"命中:{len([c for c in engine.pool if c.hit])}", flush=True)
        for c in engine.pool:
            if c.hit:
                print(f"  ★ {c.name}({c.thscode}) zone={c.zone} 开盘{c.open_pct:+.2f}% 现价{c.last_price}")
        if web:
            web.stop()
        return 0

    last_phase = ""
    cfg_path = Path(args.config)
    last_cfg_ts = [-1.0]

    def maybe_reload_cfg():
        """设置页保存后：配置文件变化则热加载（间隔/区间/阈值），无需重启服务。"""
        nonlocal cfg, interval
        try:
            ts = cfg_path.stat().st_mtime
        except OSError:
            return
        if ts == last_cfg_ts[0]:
            return
        last_cfg_ts[0] = ts
        try:
            new_cfg = json.loads(cfg_path.read_text(encoding="utf-8-sig"))
        except Exception:
            return
        if new_cfg == cfg:
            return
        cfg = new_cfg
        engine.cfg = cfg
        engine.strat = cfg.get("strategy", engine.strat)
        dr = engine.strat.get("deep_open_pct_range") or [-10.0, -7.0]
        engine.deep_range = [float(dr[0]), float(dr[1])] if dr and len(dr) == 2 else None
        interval = max(5, int(cfg.get("interval_seconds", interval)))
        print(f"[设置] 配置已热加载：间隔 {interval}s，主栏 {engine.strat.get('t_open_pct_range')}，"
              f"深水 {engine.strat.get('deep_open_pct_range')}", flush=True)
        engine._update_state({"ts": now_str(), "new_hits": [], "deep_new": []})

    while True:
        now = now_local()
        maybe_reload_cfg()
        engine.load_calendar()
        if not engine.resolve_dates():
            time.sleep(60); continue
        if not engine.ensure_pool(force=args.refresh_pool):
            time.sleep(60); continue
        args.refresh_pool = False
        phase, active, sleep_s = session_phase(now, engine.t_date, interval)
        engine.phase = phase
        if phase != last_phase:
            if last_phase:
                print(f"{CYAN}── 阶段切换: {last_phase} → {phase}{RESET}", flush=True)
            last_phase = phase
        if phase in ("连续竞价", "集合竞价"):
            try:
                engine.sentiment = api.sentiment()
            except Exception:
                pass
        if active or (now.strftime("%Y-%m-%d") == engine.t_date and phase in ("午间休市", "已收盘")):
            res = engine.run_cycle()
            hits = [c for c in engine.pool if c.hit]
            print(f"[{res['ts']}] {phase} 轮询#{engine.cycle_no} 候选:{len(engine.pool)} "
                  f"低开:{sum(1 for c in engine.pool if c.zone=='main')} "
                  f"深水:{sum(1 for c in engine.pool if c.zone=='deep')}", flush=True)
            for rec in res.get("new_hits", []):
                print(f"{BOLD}{RED}★ 命中 {rec['name']}({rec['thscode']}) 开盘{rec['open_pct']:+.2f}%{RESET}", flush=True)
            for rec in res.get("deep_new", []):
                print(f"{BOLD}{RED}💧 深水 {rec['name']}({rec['thscode']}) 开盘{rec['open_pct']:+.2f}%{RESET}", flush=True)
        # 分片休眠：每 ≤15 秒检查一次配置，保证设置页保存后快速热生效（无需重启）
        deadline = time.time() + sleep_s
        while time.time() < deadline:
            maybe_reload_cfg()
            time.sleep(max(1.0, min(15.0, deadline - time.time())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
