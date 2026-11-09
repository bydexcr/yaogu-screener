# -*- coding: utf-8 -*-
"""
零依赖本地网页看板 + 个股分析页
  GET /                    → 个股分析首页（市场全景 + 搜索 + 分析结果）
  GET /radar               → 妖股雷达看板（原 index.html，轮询 /api/state）
  GET /api/state           → 引擎状态 JSON
  GET /api/market           → 市场全景
  GET /api/stock?q=…        → 个股综合分析
  GET /api/market/sector?code=… → 板块成分股
  GET /api/search?q=…        → 代码/名称联想
  GET /stock.css|/stock.js  → 个股分析页静态资源
"""
from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable
from urllib.parse import parse_qs, urlparse

WEB_DIR = Path(__file__).resolve().parent
_STATE_MARK = "window.__DSH_STATE__ = null;"


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


def save_snapshot_html(state: dict) -> str:
    """把引擎状态内嵌为自包含 HTML（双击即可查看，无需服务器）。"""
    html = _load_index_html()
    payload = json.dumps(state, ensure_ascii=False, default=str)
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


class _Handler(BaseHTTPRequestHandler):
    get_state: Callable[[], str] = lambda: "{}"
    index_html = ""
    token: str = ""            # 非空时要求 ?token=xxx（局域网访问保护）

    def log_message(self, *a):
        pass

    def _authed(self) -> bool:
        if not self.token:
            return True
        qs = parse_qs(urlparse(self.path).query)
        return qs.get("token", [""])[0] == self.token

    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code: int = 200):
        self._send(code, json.dumps(obj, ensure_ascii=False, default=str).encode("utf-8"),
                   "application/json; charset=utf-8")

    def do_GET(self):  # noqa: N802
        if not self._authed():
            self._send(401, "需要访问令牌：请在网址后加 ?token=<你的令牌>".encode("utf-8"),
                       "text/plain; charset=utf-8")
            return
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path.startswith("/api/state"):
            self._send(200, self.get_state().encode("utf-8"), "application/json; charset=utf-8")
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
        if path in ("/stock.js",):
            self._send(200, _load_stock_js().encode("utf-8"), "text/javascript; charset=utf-8")
            return
        if path in ("/", "/index.html", "/stock"):
            if path == "/radar":
                self._send(200, self.index_html.encode("utf-8"), "text/html; charset=utf-8")
            else:
                self._send(200, _load_stock_html().encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/radar":
            self._send(200, self.index_html.encode("utf-8"), "text/html; charset=utf-8")
            return
        self.send_response(404)
        self.end_headers()

    @staticmethod
    def _safe(fn, *args):
        try:
            return fn(*args)
        except LookupError as e:
            return {"ok": False, "error": str(e)}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": f"{type(e).__name__}: {e}"}

    def do_OPTIONS(self):  # noqa: N802
        self.send_response(204)
        self.end_headers()


class Dashboard:
    def __init__(self, get_state: Callable[[], str], host: str = "127.0.0.1",
                 port: int = 8311, token: str = ""):
        self.host = host
        self.port = port
        self.token = token or ""
        self.get_state = get_state
        self._httpd: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> "Dashboard":
        _Handler.index_html = _load_index_html()
        _Handler.get_state = self.get_state
        _Handler.token = self.token

        for p in range(self.port, self.port + 20):
            try:
                self._httpd = ThreadingHTTPServer((self.host, p), _Handler)
                self.port = p
                break
            except OSError:
                continue
        if not self._httpd:
            raise RuntimeError(f"网页看板端口被占用（{self.host}:{self.port}~{self.port + 19}）")
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()
        # 后台预热板块成分索引（首次约 30~90 秒，之后走落盘缓存）
        try:
            stock_data = _load_stock_module("stock_data")
            threading.Thread(target=stock_data.MEMBERSHIP.ensure, daemon=True).start()
        except Exception as e:  # noqa: BLE001
            print(f"[看板] 板块索引预热跳过: {e}")
        return self

    def stop(self):
        if self._httpd:
            self._httpd.shutdown()


def start_dashboard(engine, host: str = "127.0.0.1", port: int = 8311,
                    token: str = "") -> Dashboard | None:
    try:
        dash = Dashboard(get_state=engine.state_json, host=host, port=port, token=token)
        dash.start()
        return dash
    except Exception as e:
        print(f"[看板] 启动失败: {e}")
        return None
