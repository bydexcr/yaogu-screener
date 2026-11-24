# -*- coding: utf-8 -*-
"""
零依赖本地网页看板 + 个股分析页
  GET /                    → 个股分析首页（市场全景 + 搜索 + 分析结果）
  GET /radar               → 妖股雷达看板（原 index.html，轮询 /api/state）
  GET /api/state           → 引擎状态 JSON（带 ETag，未变化回 304）
  GET /api/market           → 市场全景
  GET /api/stock?q=…        → 个股综合分析
  GET /api/market/sector?code=… → 板块成分股
  GET /api/search?q=…        → 代码/名称联想
  GET /api/hits?days=30     → 历史命中回顾（命中日志 + 前复权日线算入场后收益）
  GET /stock.css|/stock.js  → 个股分析页静态资源
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import secrets
import threading
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable
from urllib.parse import parse_qs, urlparse

WEB_DIR = Path(__file__).resolve().parent
_STATE_MARK = "window.__DSH_STATE__ = null;"
# 最近的服务端错误（/api/diag 可查；App 端没有控制台时也能自救）
_ERRORS: deque = deque(maxlen=20)


# ------------------------------------------------------------------ 模块加载
def _ensure_paths():
    """把 web/ 与其父目录加入 sys.path，兼容 包导入 / 同目录导入 / Chaquopy(APK) 三种情况。"""
    import sys as _sys
    for p in (str(WEB_DIR.parent), str(WEB_DIR)):
        if p not in _sys.path:
            _sys.path.insert(0, p)


def _load_stock_module(name: str):
    """加载 web 下的个股分析模块：先按包导入，失败再按同目录导入。"""
    import importlib
    _ensure_paths()
    try:
        return importlib.import_module(f"web.{name}")
    except ImportError:
        return importlib.import_module(name)


# ------------------------------------------------------------------ 资源加载
def _read_asset(name: str, module_attr: str, module_name: str) -> str:
    f = WEB_DIR / name
    if f.exists():
        return f.read_text(encoding="utf-8")
    try:
        _ensure_paths()
        mod = __import__(module_name, fromlist=[module_attr])
        return getattr(mod, module_attr)
    except Exception:
        return ""


def _load_index_html() -> str:
    """妖股雷达看板 HTML：优先读 index.html，打包进 APK 时退化为 web.index_html 模块。"""
    html = _read_asset("index.html", "HTML", "web.index_html")
    return html or "<h1>index.html 缺失</h1>"


def _load_stock_html() -> str:
    html = _read_asset("stock.html", "HTML", "web.stock_assets")
    return html or "<h1>stock.html 缺失</h1>"


def _load_stock_css() -> str:
    return _read_asset("stock.css", "CSS", "web.stock_assets")


def _load_stock_js() -> str:
    return _read_asset("stock.js", "JS", "web.stock_assets")


def _load_review_html() -> str:
    html = _read_asset("review.html", "HTML", "web.review_assets")
    return html or "<h1>review.html 缺失</h1>"


def _load_review_css() -> str:
    return _read_asset("review.css", "CSS", "web.review_assets")


def _load_review_js() -> str:
    return _read_asset("review.js", "JS", "web.review_assets")


# ---------------- 主题（浅色/深色）资源 ----------------
def _load_theme_js() -> str:
    return _read_asset("theme.js", "THEME_JS", "web.theme_assets")


def _load_stock_dark() -> str:
    return _read_asset("stock-dark.css", "STOCK_DARK", "web.theme_assets")


def _load_radar_dark() -> str:
    return _read_asset("radar-dark.css", "RADAR_DARK", "web.theme_assets")


# ---------------- 市场全景页 + 左侧导航 ----------------
def _load_overview_html() -> str:
    html = _read_asset("overview.html", "HTML", "web.overview_assets")
    return html or "<h1>overview.html 缺失</h1>"


def _load_overview_css() -> str:
    return _read_asset("overview.css", "CSS", "web.overview_assets")


def _load_overview_js() -> str:
    return _read_asset("overview.js", "JS", "web.overview_assets")


def _load_nav_css() -> str:
    return _read_asset("nav.css", "NAV_CSS", "web.nav_assets")


def _load_nav_js() -> str:
    return _read_asset("nav.js", "NAV_JS", "web.nav_assets")


def _load_analysis_css() -> str:
    return _read_asset("analysis.css", "CSS", "web.analysis_assets")


def _load_radar_css() -> str:
    return _read_asset("radar.css", "CSS", "web.radar_assets")


def _load_watch_html() -> str:
    """自选股页 HTML（APK 里文件缺失时退回 web.watchlist_assets）。"""
    html = _read_asset("watchlist.html", "HTML", "web.watchlist_assets")
    return html or "<h1>watchlist.html 缺失</h1>"


def _load_watch_css() -> str:
    return _read_asset("watchlist.css", "CSS", "web.watchlist_assets")


def _load_watch_core_js() -> str:
    """全站星标脚本：纯文件资源（不内嵌，随 APK 的 web/ 目录一起打包）。"""
    f = WEB_DIR / "watch-core.js"
    return f.read_text(encoding="utf-8") if f.exists() else ""


def _load_watch_js() -> str:
    return _read_asset("watchlist.js", "JS", "web.watchlist_assets")


def _load_pages_dark() -> str:
    return _read_asset("pages-dark.css", "PAGES_DARK", "web.theme_assets")


def _load_review_module():
    return _load_stock_module("stock_review")


def save_snapshot_html(state: dict) -> str:
    """把引擎状态内嵌为自包含 HTML（双击即可查看，无需服务器）。"""
    html = _load_index_html()
    payload = json.dumps(state, ensure_ascii=False, default=str)
    # 内插进 <script>：必须转义 </script>，否则股票名里带 "</script>" 会把快照截断
    payload = payload.replace("</", "<\\/")
    if _STATE_MARK not in html:
        raise RuntimeError("index.html 缺少状态占位符")
    return html.replace(_STATE_MARK, f"window.__DSH_STATE__ = {payload};", 1)


# ------------------------------------------------------------------ 业务接口
def api_market() -> dict:
    stock_market = _load_stock_module("stock_market")
    return stock_market.dashboard()


def api_stock(query: str) -> dict:
    stock_analysis = _load_stock_module("stock_analysis")
    return stock_analysis.analyze(query)


def api_sector(code: str) -> dict:
    stock_market = _load_stock_module("stock_market")
    out = stock_market.sector_detail(code)
    out["ok"] = True
    return out


def api_search(q: str) -> dict:
    stock_data = _load_stock_module("stock_data")
    items = stock_data.search(q, 12) if q else []
    return {"ok": True, "items": [i for i in items if i.get("assetType") == "a-share"]}


def _watch_source(engine) -> str:
    """手机端同步源（电脑地址）；电脑端配置里没有这个键 → 空串。"""
    try:
        cfg = getattr(engine, "cfg", None) or {}
        src = str(cfg.get("watch_source") or "").strip()
    except Exception:
        return ""
    if not src:
        return ""
    if not src.startswith(("http://", "https://")):
        src = "http://" + src
    return src.rstrip("/")


def _remote_watch(src: str, qs: dict, timeout: float = 4.0):
    """请求电脑端的 /api/watchlist；失败返回 None（调用方决定降级方式）。"""
    import urllib.parse as _up
    import urllib.request as _ur
    url = src + "/api/watchlist?" + _up.urlencode(qs)
    try:
        with _ur.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


def _watch_cache_path() -> pathlib.Path:
    d = pathlib.Path(os.environ.get("YAOGU_DATA_DIR") or ".")
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return d / "watchlist_cache.json"


def _watch_cache_read():
    p = _watch_cache_path()
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _watch_cache_write(payload: dict) -> None:
    try:
        import time as _t
        p = _watch_cache_path()
        p.write_text(json.dumps({"cached_at": _t.strftime("%Y-%m-%d %H:%M:%S"),
                                 "payload": payload}, ensure_ascii=False),
                     encoding="utf-8")
    except Exception:
        pass


def _radar_index(state_json_fn=None) -> dict:
    """把引擎状态里的候选池整理成 {thscode: 状态}，供自选股标注「今天在雷达里吗」。"""
    try:
        raw = state_json_fn() if callable(state_json_fn) else "{}"
        st = json.loads(raw or "{}")
    except Exception:
        return {}
    idx = {}
    for c in (st.get("candidates") or []):
        code = (c.get("thscode") or "").strip()
        if not code:
            continue
        zone = c.get("zone") or ""
        hit = bool(c.get("hit"))
        sig = c.get("sig") or ""
        if hit and zone == "deep":
            status = "深水命中"
        elif hit:
            status = "低开命中"
        elif zone == "deep":
            status = "深水"
        elif sig == "confirm":
            status = "承接"
        elif sig == "broken":
            status = "走弱"
        else:
            status = "候选"
        idx[code] = {"status": status, "zone": zone, "hit": hit,
                     "score": c.get("score"), "t1_pct": c.get("t1_pct"),
                     "t1_limitup": bool(c.get("t1_limitup")),
                     "continue_text": c.get("continue_text") or ""}
    return idx


def _resolve_name(stock_data, thscode: str) -> str:
    """把 '600519.SH' 解析成中文名（加自选时用）。失败返回空串。"""
    ticker = thscode.split(".")[0]
    try:
        for q in (ticker, thscode):
            for it in (stock_data.search(q, 8) or []):
                if (it.get("thscode") or "").upper() == thscode:
                    return (it.get("name") or "").strip()
    except Exception:
        return ""
    return ""


def _t1_pct(stock_data, code: str):
    """上一交易日涨跌幅（用于自选股页「T-1」列）。取 10 天日线，前复权。"""
    try:
        bars = stock_data.history(code, days=10)
    except Exception:
        return None
    if not bars or len(bars) < 2:
        return None
    today = __import__("time").strftime("%Y-%m-%d")
    if (bars[-1].get("date") or "") == today and len(bars) >= 3:
        prev, cur = bars[-3], bars[-2]
    else:
        prev, cur = bars[-2], bars[-1]
    pc, cc = _num(prev.get("close")), _num(cur.get("close"))
    if not pc or not cc:
        return None
    return round((cc / pc - 1) * 100, 2)


def _num(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f


def api_watchlist(action: str = "list", code: str = "", name: str = "",
                  note: str = "", text: str = "", order: str = "",
                  state_json_fn=None, engine=None) -> dict:
    """自选股：list/add/remove/rename/note/reorder/batch/clear。

    统一返回 {ok, items:[用户字段 + 实时行情 + T-1 涨幅 + 雷达状态], ...}。
    行情失败不影响列表（降级为 —），这是自选股页必须的韧性。
    """
    W = _load_stock_module("watchlist_store")   # 兼容 包导入 / 同目录 / APK
    act = (action or "list").strip().lower()
    src = _watch_source(engine)
    if act == "ids":                       # 轻量：只返回代码列表（其他页面的星标状态用）
        if src:
            remote = _remote_watch(src, {"action": "ids"}, timeout=2.5)
            if remote and remote.get("ok"):
                return remote
            cached = _watch_cache_read()
            if cached:
                return {"ok": True, "codes": [i.get("thscode") for i in (cached.get("payload") or {}).get("items", [])
                                              if i.get("thscode")], "synced": False}
            return {"ok": True, "codes": [], "synced": False}
        return {"ok": True, "codes": [it["thscode"] for it in W.items()]}

    # 手机端：所有写操作转发给电脑，避免两端各存一份互相打架
    if src and act != "list":
        fwd = {"action": act}
        for k, v in (("code", code), ("name", name), ("note", note), ("text", text), ("order", order)):
            if v:
                fwd[k] = v
        remote = _remote_watch(src, fwd, timeout=6.0)
        if remote is None:
            return {"ok": False, "synced": False,
                    "error": f"未连上电脑（{src}），自选股需要电脑端在线才能修改"}
        if remote.get("ok"):
            _watch_cache_write(remote)
        remote["synced"] = True
        remote["sync_source"] = src
        return remote

    if src and act == "list":
        remote = _remote_watch(src, {"action": "list"}, timeout=5.0)
        if remote is not None and remote.get("ok"):
            _watch_cache_write(remote)
            remote["synced"] = True
            remote["sync_source"] = src
            return remote
        cached = _watch_cache_read()
        if cached and isinstance(cached.get("payload"), dict):
            out = dict(cached["payload"])
            out["synced"] = False
            out["sync_source"] = src
            out["cached_at"] = cached.get("cached_at")
            return out
        return {"ok": False, "synced": False,
                "error": f"未连上电脑（{src}），本地也没有缓存；请确认手机与电脑在同一局域网"}

    extra = {}
    if act == "add":
        if not (name or "").strip():                 # 调用方没带名字就先解析，别让列表显示成一串代码
            try:
                name = _resolve_name(_load_stock_module("stock_data"), W.norm_code(code))
            except BaseException:
                name = ""
        r = W.add(code, name)
        if not r.get("ok"):
            return r
        extra["added"] = r.get("added")
        if r.get("note"):
            extra["note"] = r["note"]
    elif act == "remove":
        r = W.remove(code)
        if not r.get("ok"):
            return r
        extra["removed"] = r.get("removed")
    elif act == "rename":
        r = W.rename(code, name)
        if not r.get("ok"):
            return r
    elif act == "note":
        r = W.set_note(code, note)
        if not r.get("ok"):
            return r
    elif act == "reorder":
        r = W.reorder([c for c in (order or "").split(",") if c.strip()])
        if not r.get("ok"):
            return r
    elif act == "batch":
        try:
            _sd = _load_stock_module("stock_data")
            _res = lambda c: _resolve_name(_sd, c)      # noqa: E731
        except BaseException:
            _res = None
        r = W.batch_add(text, resolve=_res)
        if not r.get("ok"):
            return r
        extra["added"] = r.get("added") or []
        extra["skipped"] = r.get("skipped") or 0
    elif act == "clear":
        W.clear()
    elif act != "list":
        return {"ok": False, "error": f"未知动作：{action}"}

    data = W.load()
    items = data["items"]
    codes = [it["thscode"] for it in items]

    quotes, radar = {}, {}
    try:
        quotes = _load_stock_module("stock_data").snapshot(codes) if codes else {}
    except BaseException as e:                      # noqa: BLE001
        _ERRORS.append({"at": __import__("time").strftime("%H:%M:%S"),
                        "error": f"watchlist 行情失败: {type(e).__name__}: {e}"})
    try:
        radar = _radar_index(state_json_fn)
    except BaseException:
        radar = {}

    # 非候选股的 T-1 涨幅需要日线：并发取，失败就留空
    need_t1 = [c for c in codes if c not in radar]
    t1map = {}
    if need_t1:
        try:
            sd = _load_stock_module("stock_data")
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=min(6, len(need_t1))) as ex:
                for c, v in zip(need_t1, ex.map(lambda x: _t1_pct(sd, x), need_t1)):
                    if v is not None:
                        t1map[c] = v
        except BaseException:
            pass

    out = []
    for it in items:
        code_ = it["thscode"]
        q = quotes.get(code_) or {}
        r = radar.get(code_) or {}
        prev = _num(q.get("prev_price"))
        last = _num(q.get("last_price"))
        pct = _num(q.get("price_change_ratio_pct"))
        if pct is None and prev and last:
            pct = (last / prev - 1) * 100
        out.append({
            "thscode": code_,
            "name": it.get("name") or code_.split(".")[0],
            "added_at": it.get("added_at") or "",
            "note": it.get("note") or "",
            "last": last,
            "pct": round(pct, 2) if pct is not None else None,
            "open": _num(q.get("open_price")),
            "turnover": _num(q.get("turnover")),
            "volume": _num(q.get("volume")),
            "t1_pct": r.get("t1_pct") if r else t1map.get(code_),
            "radar": ({"status": r.get("status"), "zone": r.get("zone"), "hit": r.get("hit"),
                       "score": r.get("score"), "t1_limitup": r.get("t1_limitup"),
                       "continue_text": r.get("continue_text")} if r else None),
        })

    res = {"ok": True, "items": out, "count": len(out),
           "updated": data.get("updated") or "", "schema": data.get("schema")}
    res.update(extra)
    return res


def api_review(date: str = "", force: bool = False) -> dict:
    """当日盘面复盘（默认最新交易日，可查已存档日期；force=True 重新生成）。"""
    rv = _load_review_module()
    return rv.review(date or None, force=force)


def api_review_dates() -> dict:
    rv = _load_review_module()
    return {"ok": True, "dates": rv.saved_dates()}


def api_hits(days: int = 30) -> dict:
    """历史命中回顾：读引擎落盘的命中日志，按前复权日线算入场后收益。"""
    hit_log = _load_stock_module("hit_log")
    return hit_log.build(days=days)


def api_overview() -> dict:
    """市场全景：/api/market 的全量数据 + 服务端生成的派生文案（今日一句/结构句等）。"""
    stock_market = _load_stock_module("stock_market")
    d = stock_market.dashboard()
    try:
        market_text = _load_stock_module("market_text")
        d["copy"] = market_text.summarize(d)
    except BaseException as e:  # noqa: BLE001 - 文案挂了不能拖垮整页数字
        d["copy"] = {}
        _ERRORS.append({"at": __import__("time").strftime("%H:%M:%S"),
                        "error": "market_text: %s" % e})
    return d


def api_diag() -> dict:
    """环境自检：页面上「诊断」按钮调用，PC/手机出问题时不看日志也能定位。"""
    import os
    import platform
    import sys

    _ensure_paths()
    out: dict = {
        "ok": True,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "cwd": os.getcwd(),
        "webDir": str(WEB_DIR),
        "sysPath": sys.path[:8],
        "threads": threading.active_count(),
    }
    mods = {}
    for name in ("rest_client", "stock_data", "web.stock_data",
                 "stock_market", "web.stock_market", "stock_analysis", "web.stock_analysis"):
        m = sys.modules.get(name)
        if m is not None:
            mods[name] = {"file": getattr(m, "__file__", None), "id": id(m)}
    out["modules"] = mods

    groups = {}
    for name in ("stock_data", "web.stock_data"):
        m = sys.modules.get(name)
        if m is not None and hasattr(m, "MEMBERSHIP"):
            mi = m.MEMBERSHIP
            try:
                files = sorted(p.name for p in mi.cache_dir.glob("stock_membership_*.json"))
            except Exception:  # noqa: BLE001
                files = []
            groups[name] = {"stats": mi.stats(), "cacheDir": str(mi.cache_dir), "files": files}
    out["membership"] = groups

    env = {}
    for k, v in os.environ.items():
        if k.startswith(("YAOGU_", "HITHINK_", "STOCK_")):
            env[k] = ("<已设置 长度%d>" % len(v)) if ("KEY" in k or "TOKEN" in k) else v
    out["env"] = env
    try:
        rc = _load_stock_module("rest_client")
        k = rc.api_key()
        env["apiKey"] = "<可取到 长度%d>" % len(k)
    except BaseException as e:  # noqa: BLE001
        env["apiKey"] = "%s: %s" % (type(e).__name__, e)
    try:
        sdm = _load_stock_module("stock_data")
        out["stockDiagLog"] = list(getattr(sdm, "DIAG_LOG", []))
    except BaseException as e:  # noqa: BLE001
        out["stockDiagLog"] = ["读取失败: %s: %s" % (type(e).__name__, e)]
    out["lastErrors"] = list(_ERRORS)
    return out


class _Handler(BaseHTTPRequestHandler):
    """请求处理器。

    注意：回调（get_state）、页面 HTML、token **不再写在类的属性上**。
    类属性 + 普通函数会被 Python 当成方法绑定（self 会被塞成第一个参数），
    且同进程起两个 Dashboard 时会互相覆盖。真正的值挂在 ThreadingHTTPServer 实例上
    （见 Dashboard.start()），这里只做兜底读取。
    """

    # 兜底默认值（正常都会被 server 实例上的属性覆盖）
    get_state: Callable[[], str] = staticmethod(lambda: "{}")
    index_html = ""
    token: str = ""            # 非空时要求 ?token=xxx（局域网访问保护）

    # ---------------- 从 server 实例取配置 ----------------
    @property
    def _state_fn(self) -> Callable[[], str]:
        fn = getattr(self.server, "dashboard_state", None)
        return fn if callable(fn) else self.get_state

    @property
    def _page_html(self) -> str:
        html = getattr(self.server, "dashboard_html", None)
        return html if isinstance(html, str) and html else self.index_html

    @property
    def _engine(self):
        return getattr(self.server, "dashboard_engine", None)

    @property
    def _token(self) -> str:
        tok = getattr(self.server, "dashboard_token", "")
        return tok if isinstance(tok, str) else ""

    def log_message(self, *a):
        # 正常请求日志噪声太大，不打印
        pass

    def log_error(self, fmt, *args):
        """把异常信息留给 stderr（PC 端落到 run_*.log.err，App 端进 logcat），便于排查。"""
        try:
            import sys as _sys
            import traceback
            if not _sys.stderr:
                return
            _sys.stderr.write("[看板] " + (fmt % args) + "\n")
            if _sys.exc_info()[0] is not None:
                traceback.print_exc(file=_sys.stderr)
            _sys.stderr.flush()
        except Exception:
            pass

    def _authed(self) -> bool:
        if not self._token:
            return True
        # 本机访问不需要令牌（看板默认就绑本机；绑 0.0.0.0 时也只拦局域网请求）
        try:
            peer = self.client_address[0]
        except Exception:  # noqa: BLE001
            peer = ""
        if _is_loopback(peer):
            return True
        qs = parse_qs(urlparse(self.path).query)
        return qs.get("token", [""])[0] == self._token

    def _send(self, code: int, body: bytes, ctype: str, etag: str = ""):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        if etag:
            self.send_header("ETag", etag)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_not_modified(self, etag: str):
        """304 Not Modified：不写 body（服务端是 HTTP/1.0，连接随即关闭，不存在分帧问题）。"""
        self.send_response(304)
        self.send_header("ETag", etag)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def _json(self, obj, code: int = 200):
        self._send(code, json.dumps(obj, ensure_ascii=False, default=str).encode("utf-8"),
                   "application/json; charset=utf-8")

    def do_GET(self):  # noqa: N802
        if not self._authed():
            hint = ""
            f = _token_file()
            if f is not None:
                hint = f"\n令牌文件：{f}（内容即令牌）"
            self._send(401, ("需要访问令牌：请在网址后加 ?token=<你的令牌>" + hint).encode("utf-8"),
                       "text/plain; charset=utf-8")
            return
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path.startswith("/api/state"):
            # 轮询里绝大多数响应和上一轮逐字节相同：带 ETag，未变化只回 304，
            # 前端既不用解析 JSON 也不用重建表格 DOM（滚动位置/悬停状态得以保留）。
            body = self._state_fn().encode("utf-8")
            etag = '"%s"' % hashlib.sha1(body).hexdigest()[:20]
            if (self.headers.get("If-None-Match") or "").strip() == etag:
                self._send_not_modified(etag)
                return
            self._send(200, body, "application/json; charset=utf-8", etag=etag)
            return
        if path.startswith("/api/diag"):
            self._json(self._safe(api_diag))
            return
        if path.startswith("/api/hits"):
            try:
                days = int(qs.get("days", ["30"])[0] or 30)
            except ValueError:
                days = 30
            self._json(self._safe(api_hits, days))
            return
        if path.startswith("/api/overview"):
            self._json(self._safe(api_overview))
            return
        if path.startswith("/api/review/dates"):
            self._json(self._safe(api_review_dates))
            return
        if path.startswith("/api/review"):
            force = (qs.get("force", [""])[0] or "") in ("1", "true", "yes")
            self._json(self._safe(api_review, (qs.get("date", [""])[0] or "").strip(), force))
            return
        if path.startswith("/api/market/sector"):
            code = (qs.get("code", [""])[0] or "").strip()
            if not code:
                self._json({"ok": False, "error": "缺少参数 code"}, 400)
                return
            self._json(self._safe(api_sector, code))
            return
        if path.startswith("/api/market"):
            self._json(self._safe(api_market))
            return
        if path.startswith("/api/watchlist"):
            act = (qs.get("action", ["list"])[0] or "list").strip()
            if act == "export":
                _W = _load_stock_module("watchlist_store")
                import time as _time
                body = _W.export_csv().encode("utf-8")
                self._send(200, body, "text/csv; charset=utf-8")
                return
            self._json(self._safe(api_watchlist,
                                  act,
                                  (qs.get("code", [""])[0] or "").strip(),
                                  (qs.get("name", [""])[0] or "").strip(),
                                  (qs.get("note", [""])[0] or "").strip(),
                                  (qs.get("text", [""])[0] or ""),
                                  (qs.get("order", [""])[0] or ""),
                                  self._state_fn,
                                  self._engine))
            return
        if path.startswith("/api/search"):
            self._json(self._safe(api_search, (qs.get("q", [""])[0] or "").strip()))
            return
        if path.startswith("/api/stock"):
            q = (qs.get("q", [""])[0] or "").strip()
            if not q:
                self._json({"ok": False, "error": "缺少参数 q"}, 400)
                return
            self._json(self._safe(api_stock, q))
            return
        if path in ("/stock.css",):
            self._send(200, _load_stock_css().encode("utf-8"), "text/css; charset=utf-8")
            return
        if path in ("/overview.css",):
            self._send(200, _load_overview_css().encode("utf-8"), "text/css; charset=utf-8")
            return
        if path in ("/overview.js",):
            self._send(200, _load_overview_js().encode("utf-8"), "text/javascript; charset=utf-8")
            return
        if path in ("/nav.css",):
            self._send(200, _load_nav_css().encode("utf-8"), "text/css; charset=utf-8")
            return
        if path in ("/nav.js",):
            self._send(200, _load_nav_js().encode("utf-8"), "text/javascript; charset=utf-8")
            return
        if path in ("/analysis.css",):
            self._send(200, _load_analysis_css().encode("utf-8"), "text/css; charset=utf-8")
            return
        if path in ("/radar.css",):
            self._send(200, _load_radar_css().encode("utf-8"), "text/css; charset=utf-8")
            return
        if path in ("/pages-dark.css",):
            self._send(200, _load_pages_dark().encode("utf-8"), "text/css; charset=utf-8")
            return
        if path in ("/stock.js",):
            self._send(200, _load_stock_js().encode("utf-8"), "text/javascript; charset=utf-8")
            return
        if path in ("/review.css",):
            self._send(200, _load_review_css().encode("utf-8"), "text/css; charset=utf-8")
            return
        if path in ("/review.js",):
            self._send(200, _load_review_js().encode("utf-8"), "text/javascript; charset=utf-8")
            return
        if path in ("/theme.js",):
            self._send(200, _load_theme_js().encode("utf-8"), "text/javascript; charset=utf-8")
            return
        if path in ("/stock-dark.css",):
            self._send(200, _load_stock_dark().encode("utf-8"), "text/css; charset=utf-8")
            return
        if path in ("/radar-dark.css",):
            self._send(200, _load_radar_dark().encode("utf-8"), "text/css; charset=utf-8")
            return
        if path in ("/overview", "/overview.html"):
            self._send(200, _load_overview_html().encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/":
            # 落地页＝市场全景；带 ?q= 时仍然进个股分析（老链接与 ?q= 分享保持可用）
            q = (qs.get("q", [""])[0] or "").strip()
            html = _load_stock_html() if q else _load_overview_html()
            self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path in ("/index.html", "/stock"):
            self._send(200, _load_stock_html().encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/radar":
            self._send(200, self._page_html.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path in ("/watchlist", "/watchlist.html"):
            self._send(200, _load_watch_html().encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/watchlist.css":
            self._send(200, _load_watch_css().encode("utf-8"), "text/css; charset=utf-8")
            return
        if path == "/watch-core.js":
            self._send(200, _load_watch_core_js().encode("utf-8"), "text/javascript; charset=utf-8")
            return
        if path == "/watchlist.js":
            self._send(200, _load_watch_js().encode("utf-8"),
                       "text/javascript; charset=utf-8")
            return
        if path in ("/review", "/review.html"):
            self._send(200, _load_review_html().encode("utf-8"), "text/html; charset=utf-8")
            return
        self.send_response(404)
        self.end_headers()

    @staticmethod
    def _safe(fn, *args):
        try:
            return fn(*args)
        except LookupError as e:
            _ERRORS.append({"at": __import__("time").strftime("%H:%M:%S"), "error": str(e)})
            return {"ok": False, "error": str(e)}
        except BaseException as e:  # noqa: BLE001
            # 必须是 BaseException：SystemExit 之类若不拦住，请求线程会静默退出，
            # 前端只能看到「空响应」，错误原因完全丢失。
            _ERRORS.append({"at": __import__("time").strftime("%H:%M:%S"),
                            "error": f"{type(e).__name__}: {e}"})
            return {"ok": False, "error": f"{type(e).__name__}: {e}"}

    def do_OPTIONS(self):  # noqa: N802
        self.send_response(204)
        self.end_headers()


class Dashboard:
    def __init__(self, get_state: Callable[[], str], host: str = "127.0.0.1",
                 port: int = 8311, token: str = "", engine=None):
        self.engine = engine
        self.host = host
        self.port = port
        self.token = token or ""
        self.get_state = get_state
        self._httpd: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> "Dashboard":
        page_html = _load_index_html()

        for p in range(self.port, self.port + 20):
            try:
                self._httpd = ThreadingHTTPServer((self.host, p), _Handler)
                self.port = p
                break
            except OSError:
                continue
        if not self._httpd:
            raise RuntimeError(f"网页看板端口被占用（{self.host}:{self.port}~{self.port + 19}）")
        # 交给 server 实例：普通函数/绑定方法都能正确调用，多个 Dashboard 也互不影响
        self._httpd.dashboard_state = self.get_state
        self._httpd.dashboard_html = page_html
        self._httpd.dashboard_token = self.token
        self._httpd.dashboard_engine = self.engine
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()
        # 后台预热板块成分索引（首次约 30~90 秒，之后走落盘缓存）
        try:
            stock_data = _load_stock_module("stock_data")
            threading.Thread(target=stock_data.MEMBERSHIP.ensure, daemon=True).start()
        except Exception as e:  # noqa: BLE001
            print(f"[看板] 板块索引预热跳过: {e}")
        # 后台预热市场全景缓存（首屏 /api/market 冷启动 7~10 秒 → 预热后秒开）
        try:
            stock_market = _load_stock_module("stock_market")
            threading.Thread(target=stock_market.dashboard, daemon=True).start()
        except Exception as e:  # noqa: BLE001
            print(f"[看板] 市场全景预热跳过: {e}")
        return self

    def stop(self):
        if self._httpd:
            self._httpd.shutdown()


LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _is_loopback(addr: str) -> bool:
    """请求方是不是本机（127.0.0.0/8、::1、IPv4-mapped 形式）。"""
    a = (addr or "").strip().lower()
    return (a in LOCAL_HOSTS or a.startswith("127.")
            or a == "::1" or a == "::ffff:127.0.0.1")


def _token_file():
    """令牌落盘位置：优先 YAOGU_DATA_DIR，其次 ~/.config/yaogu。"""
    import os
    from pathlib import Path as _P
    base = (os.environ.get("YAOGU_DATA_DIR") or "").strip()
    root = _P(base) if base else (_P.home() / ".config" / "yaogu")
    try:
        root.mkdir(parents=True, exist_ok=True)
    except Exception:  # noqa: BLE001
        return None
    return root / "web_token.txt"


def _effective_token(host: str, token: str) -> str:
    """决定本次监听要不要访问令牌。

    - 只监听本机 → 空令牌（本来就只有本机能访问）；
    - 监听 0.0.0.0 / 局域网 IP 且没给令牌 → 自动生成并**落盘复用**，
      此时仅**非本机请求**需要 ?token=…（本机浏览器照旧直接打开）。
    """
    tok = (token or "").strip()
    if tok:
        return tok
    h = (host or "").strip().lower()
    if h in LOCAL_HOSTS:
        return ""
    f = _token_file()
    if f is not None:
        try:
            if f.exists():
                saved = f.read_text(encoding="utf-8").strip()
                if saved:
                    return saved
        except Exception:  # noqa: BLE001
            pass
    tok = secrets.token_urlsafe(9)
    if f is not None:
        try:
            f.write_text(tok + "\n", encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass
    return tok


def start_dashboard(engine, host: str = "127.0.0.1", port: int = 8311,
                    token: str = "") -> Dashboard | None:
    eff = _effective_token(host, token)
    if eff and eff != (token or "").strip():
        print(f"[看板] 监听 {host} 且未设置令牌，已自动生成: {eff}"
              f"（访问时需带 ?token={eff}）")
    try:
        dash = Dashboard(get_state=engine.state_json, host=host, port=port, token=eff,
                         engine=engine)
        dash.start()
        return dash
    except Exception as e:
        print(f"[看板] 启动失败: {e}")
        return None
