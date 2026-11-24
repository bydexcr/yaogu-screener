# -*- coding: utf-8 -*-
"""自选股存储层（PC 引擎与手机引擎共用）

设计要点
* 单一 JSON 文件、带 schema 版本；写入用「临时文件 + os.replace」原子替换，
  避免进程被杀时留下半截文件。
* 只存用户意图（代码/名称/加入时间/排序/备注），不存行情：
  行情每次请求实时取（缓存由 stock_data 层负责），避免数据陈旧。
* 代码归一：'600519' / '600519.sh' / 'sh600519' 都归一成 '600519.SH'；
  交易所后缀按代码段推断（见 guess_suffix），非法输入返回空串。
"""
from __future__ import annotations

import csv
import io
import json
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

SCHEMA = 1
MAX_ITEMS = 300            # 上限：超过就别叫自选了，也防止页面被拖垮

_LOCK = threading.RLock()


# ------------------------------------------------------------------ 路径
def _data_dir() -> Path:
    """优先引擎 data 目录（YAOGU_DATA_DIR），退化到本模块上级的 data/。"""
    env = os.environ.get("YAOGU_DATA_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent / "data"


def store_path() -> Path:
    p = _data_dir() / "watchlist.json"
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        if os.access(str(p.parent), os.W_OK):
            return p
    except Exception:
        pass
    # 只读环境（某些 APK 打包场景）退化到临时目录，保证功能不整体失效
    return Path(tempfile.gettempdir()) / "yaogu_watchlist.json"


# ------------------------------------------------------------------ 代码归一
def guess_suffix(digits: str) -> str:
    """按代码段推断交易所：与 strategy.board_key 的口径保持一致。"""
    if not digits or not digits.isdigit() or len(digits) != 6:
        return ""
    if digits.startswith(("600", "601", "603", "605", "688", "689", "900")):
        return "SH"
    if digits.startswith(("000", "001", "002", "003", "300", "301", "200")):
        return "SZ"
    if digits.startswith(("4", "8")) or digits.startswith("920"):
        return "BJ"
    # 兜底：6/9 开头归沪，0/2/3 归深
    if digits[0] in "69":
        return "SH"
    if digits[0] in "023":
        return "SZ"
    return ""


def norm_code(code: str) -> str:
    """'600519' -> '600519.SH'；'sz000001' -> '000001.SZ'；无法识别返回 ''。"""
    s = (code or "").strip().upper().replace(" ", "")
    if not s:
        return ""
    if "." in s:
        ticker, _, suffix = s.partition(".")
        ticker = "".join(ch for ch in ticker if ch.isdigit())
        suffix = suffix[:2]
        if len(ticker) == 6 and suffix in ("SH", "SZ", "BJ"):
            return f"{ticker}.{suffix}"
        return ""
    # sh600519 / sz000001
    for pre in ("SH", "SZ", "BJ"):
        if s.startswith(pre):
            rest = "".join(ch for ch in s[len(pre):] if ch.isdigit())
            if len(rest) == 6:
                return f"{rest}.{pre}"
    digits = "".join(ch for ch in s if ch.isdigit())
    if len(digits) != 6:
        return ""
    suffix = guess_suffix(digits)
    return f"{digits}.{suffix}" if suffix else ""


# ------------------------------------------------------------------ 读写
def _empty() -> dict:
    return {"schema": SCHEMA, "updated": "", "items": []}


def load() -> dict:
    """读整个文件；损坏/不存在都返回空结构（不抛异常，页面永远能开）。"""
    p = store_path()
    with _LOCK:
        if not p.exists():
            return _empty()
        try:
            raw = json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception:
            return _empty()
        if not isinstance(raw, dict):
            return _empty()
        items = [it for it in (raw.get("items") or []) if isinstance(it, dict) and it.get("thscode")]
        return {"schema": int(raw.get("schema") or SCHEMA),
                "updated": raw.get("updated") or "",
                "items": items}


def _save(data: dict) -> None:
    p = store_path()
    data = dict(data)
    data["schema"] = SCHEMA
    data["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    with _LOCK:
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".json.tmp")
        tmp.write_text(payload, encoding="utf-8")
        os.replace(tmp, p)          # 原子替换


def items() -> List[dict]:
    return load()["items"]


# ------------------------------------------------------------------ 增删改
def add(code: str, name: str = "") -> Dict[str, object]:
    thscode = norm_code(code)
    if not thscode:
        return {"ok": False, "error": f"无法识别的代码：{code}"}
    data = load()
    cur = data["items"]
    for it in cur:
        if it.get("thscode") == thscode:
            return {"ok": True, "added": False, "items": cur, "note": f"{thscode} 已在自选里"}
    if len(cur) >= MAX_ITEMS:
        return {"ok": False, "error": f"自选股最多 {MAX_ITEMS} 只"}
    cur.append({"thscode": thscode, "name": (name or "").strip() or thscode.split(".")[0],
                "added_at": time.strftime("%Y-%m-%d %H:%M:%S"), "note": ""})
    _save(data)
    return {"ok": True, "added": True, "items": cur}


def remove(code: str) -> Dict[str, object]:
    thscode = norm_code(code)
    if not thscode:
        return {"ok": False, "error": f"无法识别的代码：{code}"}
    data = load()
    new = [it for it in data["items"] if it.get("thscode") != thscode]
    removed = len(new) != len(data["items"])
    if removed:
        data["items"] = new
        _save(data)
    return {"ok": True, "removed": removed, "items": new}


def rename(code: str, name: str) -> Dict[str, object]:
    """改名（加入时竞态拿不到名字时用）。"""
    thscode = norm_code(code)
    nm = (name or "").strip()
    if not thscode or not nm:
        return {"ok": False, "error": "缺少代码或名称"}
    data = load()
    for it in data["items"]:
        if it.get("thscode") == thscode:
            it["name"] = nm
            _save(data)
            return {"ok": True, "items": data["items"]}
    return {"ok": False, "error": "不在自选里"}


def set_note(code: str, note: str) -> Dict[str, object]:
    thscode = norm_code(code)
    if not thscode:
        return {"ok": False, "error": "代码非法"}
    data = load()
    for it in data["items"]:
        if it.get("thscode") == thscode:
            it["note"] = (note or "").strip()[:120]
            _save(data)
            return {"ok": True, "items": data["items"]}
    return {"ok": False, "error": "不在自选里"}


def reorder(order: List[str]) -> Dict[str, object]:
    """按给定代码顺序重排（拖拽排序）。未列出的排在其后，保持原相对顺序。"""
    data = load()
    want = [norm_code(c) for c in (order or [])]
    want = [c for c in want if c]
    by_code = {it["thscode"]: it for it in data["items"]}
    new = [by_code.pop(c) for c in want if c in by_code]
    new.extend(it for it in data["items"] if it["thscode"] in by_code)
    data["items"] = new
    _save(data)
    return {"ok": True, "items": new}


def clear() -> Dict[str, object]:
    data = load()
    data["items"] = []
    _save(data)
    return {"ok": True, "items": []}


# ------------------------------------------------------------------ 批量导入/导出
def parse_batch(text: str) -> List[dict]:
    """批量解析：每行 '600519 贵州茅台' / '600519,贵州茅台' / 'sh600519' 均可。"""
    out, seen = [], set()
    for line in (text or "").splitlines():
        line = line.strip().strip(",;")
        if not line:
            continue
        if line.startswith("#"):
            continue
        parts = line.replace("\t", " ").replace(",", " ").split()
        if not parts:
            continue
        code = ""
        name = ""
        for p in parts:
            c = norm_code(p)
            if c and not code:
                code = c
            elif not name and not norm_code(p):
                name = p
        if not code:
            c = norm_code(parts[0])
            if not c:
                continue
            code = c
            name = " ".join(parts[1:]).strip()
        if code in seen:
            continue
        seen.add(code)
        out.append({"thscode": code, "name": name})
    return out


def batch_add(text: str, resolve=None) -> Dict[str, object]:
    """resolve(thscode) -> name：调用方可传名称解析函数（如查行情源）。"""
    parsed = parse_batch(text)
    if resolve:
        for it in parsed:
            if not it.get("name"):
                try:
                    nm = (resolve(it["thscode"]) or "").strip()
                except Exception:
                    nm = ""
                if nm:
                    it["name"] = nm
    if not parsed:
        return {"ok": False, "error": "没有解析到有效代码"}
    data = load()
    have = {it["thscode"] for it in data["items"]}
    added = []
    for it in parsed:
        if it["thscode"] in have:
            continue
        if len(data["items"]) >= MAX_ITEMS:
            break
        data["items"].append({"thscode": it["thscode"],
                              "name": it["name"] or it["thscode"].split(".")[0],
                              "added_at": time.strftime("%Y-%m-%d %H:%M:%S"), "note": ""})
        have.add(it["thscode"])
        added.append(it["thscode"])
    if added:
        _save(data)
    return {"ok": True, "added": added, "skipped": len(parsed) - len(added), "items": data["items"]}


def export_csv() -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["thscode", "name", "added_at", "note"])
    for it in items():
        w.writerow([it.get("thscode", ""), it.get("name", ""),
                    it.get("added_at", ""), it.get("note", "")])
    return "\ufeff" + buf.getvalue()      # BOM：Excel 直接打开不乱码
