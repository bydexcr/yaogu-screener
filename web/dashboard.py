# -*- coding: utf-8 -*-
"""零依赖本地网页看板：引擎状态每 ~3s 由前端轮询 /api/state。"""
from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable

WEB_DIR = Path(__file__).resolve().parent
_STATE_MARK = "window.__DSH_STATE__ = null;"


def _load_index_html() -> str:
    """优先读 index.html；打包进 APK 时文件可能缺失，退化为 web.index_html 模块内的字符串。"""
    idx = WEB_DIR / "index.html"
    if idx.exists():
        return idx.read_text(encoding="utf-8")
    try:
        from web.index_html import HTML  # 由构建脚本生成
        return HTML
    except Exception:
        return "<h1>index.html 缺失</h1>"


def save_snapshot_html(state: dict) -> str:
    """把引擎状态内嵌为自包含 HTML（双击即可查看，无需服务器）。"""
    html = _load_index_html()
    payload = json.dumps(state, ensure_ascii=False, default=str)
    if _STATE_MARK not in html:
        raise RuntimeError("index.html 缺少状态占位符")
    return html.replace(_STATE_MARK, f"window.__DSH_STATE__ = {payload};", 1)


class _Handler(BaseHTTPRequestHandler):
    get_state: Callable[[], str] = lambda: "{}"
    index_html = ""
    token: str = ""            # 非空时要求 ?token=xxx（局域网访问保护）

    def log_message(self, *a):
        pass

    def _authed(self) -> bool:
        if not self.token:
            return True
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(self.path).query)
        return (qs.get("token", [""])[0] == self.token)

    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if not self._authed():
            self._send(401, "需要访问令牌：请在网址后加 ?token=<你的令牌>".encode("utf-8"),
                       "text/plain; charset=utf-8")
            return
        if self.path.startswith("/api/state"):
            self._send(200, self.get_state().encode("utf-8"), "application/json; charset=utf-8")
        elif self.path.startswith("/") and self.path.split("?")[0] in ("/", "/index.html"):
            self._send(200, self.index_html.encode("utf-8"), "text/html; charset=utf-8")
        else:
            self.send_response(404)
            self.end_headers()

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
