# -*- coding: utf-8 -*-
"""android_main.py —— 安卓 App(Chaquopy) 内的 Python 入口：启动手机版主循环+看板。"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

DEFAULT_CFG = {
    "interval_seconds": 30,
    "data_dir": "data_mobile",
    "web": {"enabled": True, "host": "127.0.0.1", "port": 8311, "token": ""},
    "strategy": {
        "t1_gain_min_pct": 8.0,
        "t1_volume_lt_t2": True,
        "high_ndays": 30,
        "t1_amount_min_yi": 5.0,
        "t_open_pct_range": [-8.0, -5.0],
        "deep_open_pct_range": [-10.0, -7.0],
    },
    "intraday": {"confirm_above_open": True,
                 "broken_below_open_pct": -3.0,
                 "broken_below_prev_pct": -9.0},
    "notify": {"enabled": True, "sound": True},
    "timezone": "Asia/Shanghai",
}


def _ensure_config(data_dir: Path) -> Path:
    """配置文件路径：App 设置页写入的 YAOGU_CONFIG_FILE 优先，其次内置/可写目录兜底。"""
    cands = [Path(os.environ["YAOGU_CONFIG_FILE"]) if os.environ.get("YAOGU_CONFIG_FILE") else None,
             HERE / "config_mobile.json",
             data_dir / "config_mobile.json"]
    for p in cands:
        if p and p.exists():
            return p
    p = data_dir / "config_mobile.json"
    p.write_text(json.dumps(DEFAULT_CFG, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def main():
    data_dir = Path(os.environ.get("YAOGU_DATA_DIR") or (HERE / "data_mobile"))
    data_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("YAOGU_DATA_DIR", str(data_dir))
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    sys.path.insert(0, str(HERE))            # strategy.py / web/
    sys.path.insert(0, str(HERE / "mobile"))  # live_mobile / rest_client / ...
    cfg = _ensure_config(data_dir)
    import live_mobile
    sys.argv = ["live_mobile.py", "--config", str(cfg), "--interval", "30", "--port", "8311"]
    live_mobile.main()


if __name__ == "__main__":
    main()
