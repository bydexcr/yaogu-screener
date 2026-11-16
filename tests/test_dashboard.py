# -*- coding: utf-8 -*-
"""
dashboard.py 的关键行为测试（不启服务，只测纯函数与处理器绑定）

回归重点：
  1. save_snapshot_html 必须转义 `</`（否则股票名带 `</script>` 会截断快照）
  2. /api/state 的回调不能再走"类属性存普通函数"的写法（会把 handler 当 self 传进去）
"""
import json

import pytest

from web import dashboard as D


# ---------------------------------------------------------------- 快照 HTML
def test_save_snapshot_html_escapes_closing_script():
    html = D.save_snapshot_html({"name": "</script><b>injected</b>", "n": 1})
    assert "</script><b>injected</b>" not in html
    assert "<\\/script>" in html
    assert "injected" in html          # 内容本身保留（只是转义了斜杠）


def test_save_snapshot_html_injects_state():
    html = D.save_snapshot_html({"phase": "idle", "pool_size": 3})
    assert "window.__DSH_STATE__ = " in html
    assert D._STATE_MARK not in html
    # 内插的 JSON 片段本身可解析
    start = html.index("window.__DSH_STATE__ = ") + len("window.__DSH_STATE__ = ")
    end = html.index(";", start)
    payload = html[start:end].replace("<\\/", "</")
    assert json.loads(payload)["pool_size"] == 3


# ---------------------------------------------------------------- 回调绑定
def test_handler_reads_state_from_server_instance():
    """/api/state 的回调必须从 server 实例上取，普通函数也不该被绑定成方法。"""

    class FakeServer:
        dashboard_state = staticmethod(lambda: '{"phase": "idle"}')
        dashboard_html = "<html>radar</html>"
        dashboard_token = ""

    handler = D._Handler.__new__(D._Handler)     # 不走 BaseHTTPRequestHandler 的构造函数
    handler.server = FakeServer()

    assert handler._state_fn() == '{"phase": "idle"}'
    assert handler._page_html == "<html>radar</html>"
    assert handler._token == ""


def test_handler_token_gate():
    class FakeServer:
        dashboard_state = staticmethod(lambda: "{}")
        dashboard_html = "<html/>"
        dashboard_token = "s3cret"

    handler = D._Handler.__new__(D._Handler)
    handler.server = FakeServer()
    handler.path = "/api/state?token=s3cret"
    assert handler._authed() is True

    handler.path = "/api/state?token=wrong"
    assert handler._authed() is False

    handler.path = "/api/state"
    assert handler._authed() is False


def test_handler_falls_back_to_class_defaults():
    """server 上没有属性时，回落到类上的兜底值，不应抛错。"""

    class Bare:
        pass

    handler = D._Handler.__new__(D._Handler)
    handler.server = Bare()
    assert handler._state_fn() == "{}"
    assert handler._token == ""


# ---------------------------------------------------------------- 其它纯函数
def test_locate_state_mark_exists():
    """index.html 必须保留占位符，否则 save_snapshot_html 会 raise。"""
    html = D._load_index_html()
    assert D._STATE_MARK in html
