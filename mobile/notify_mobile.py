# -*- coding: utf-8 -*-
"""
notify_mobile.py —— 手机通知：Termux 通知优先，其次 Server酱，最后仅控制台。
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import urllib.parse
import urllib.request

_last: dict = {}


def _cooldown_ok(key: str, seconds: int = 300) -> bool:
    now = time.time()
    if now - _last.get(key, 0) < seconds:
        return False
    _last[key] = now
    return True


def send(etype: str, title: str, text: str, code: str = "") -> None:
    """etype: hit / deephit / confirm / broken；冷却 5 分钟（按 类型+代码）。"""
    if not _cooldown_ok(f"{etype}:{code}"):
        return
    # 0) 安卓 App 模式（Chaquopy）：调用 Java 通知桥
    try:
        from java import jclass  # 仅安卓 App 内可用
        jclass("com.yaogu.radar.Notifier").callAttr("post", title, text)
        print(f"[通知] {title}", flush=True)
        return
    except ImportError:
        pass
    except Exception:
        pass
    # 1) Termux 系统通知（需 termux-api 包）
    if shutil.which("termux-notification"):
        try:
            subprocess.run(["termux-notification", "--title", title, "--content", text,
                            "--priority", "high"], timeout=10,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"[通知] {title}", flush=True)
            return
        except Exception:
            pass
    # 2) Server酱（可选：环境变量 SERVERCHAN_KEY）
    key = os.environ.get("SERVERCHAN_KEY", "").strip()
    if key:
        try:
            data = urllib.parse.urlencode({"title": title, "desp": text}).encode()
            req = urllib.request.Request(f"https://sctapi.ftqq.com/{key}.send", data=data)
            urllib.request.urlopen(req, timeout=10).read()
            print(f"[推送] {title}", flush=True)
            return
        except Exception as e:
            print(f"[推送失败] {e}", flush=True)
    print(f"[提醒] {title} | {text}", flush=True)
