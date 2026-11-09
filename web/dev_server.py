# -*- coding: utf-8 -*-
"""本地联调：启动合并后的看板服务（个股分析 + 妖股雷达）"""
import json
import os
import pathlib
import sys
import time

cred = pathlib.Path(os.environ["APPDATA"]) / "hithink-finance" / "credentials.env"
for line in cred.read_text(encoding="utf-8").splitlines():
    if line.strip().startswith("HITHINK_FINANCE_API_KEY="):
        os.environ["HITHINK_FINANCE_API_KEY"] = line.split("=", 1)[1].strip()

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "web"))

import dashboard  # noqa: E402


def fake_state() -> str:
    return json.dumps({
        "phase": "idle", "updated": time.strftime("%H:%M:%S"),
        "t0": "-", "t1": "-", "t2": "-", "pool": 0, "hits": 0, "wd": 0, "wc": 0, "wb": 0,
        "candidates": [], "hitslist": [], "events": [], "deep": [], "errors": ["联调模式：引擎未启动"],
    }, ensure_ascii=False)


if __name__ == "__main__":
    dash = dashboard.Dashboard(get_state=fake_state, host="127.0.0.1", port=8399)
    dash.start()
    print(f"dashboard on http://127.0.0.1:{dash.port}")
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        dash.stop()

