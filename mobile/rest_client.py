# -*- coding: utf-8 -*-
"""
rest_client.py —— 安卓(Termux)版数据层：直连同花顺 REST，无需 Node CLI / DuckDB。
鉴权：环境变量 HITHINK_FINANCE_API_KEY（或 ~/.config/yaogu/key 文件）。
接口基址：https://fuyao.aicubes.cn   （请求头 X-api-key）
"""
from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from typing import Dict, List, Optional

BASE = os.environ.get("HITHINK_BASE_URL", "https://fuyao.aicubes.cn").rstrip("/")
UA = "Mozilla/5.0 (yaogu-mobile/1.0)"
TZ_OFFSET_MS = 8 * 3600 * 1000   # 北京时间固定 +08（无夏令时）


class ApiError(RuntimeError):
    def __init__(self, code, message):
        super().__init__(f"[{code}] {message}")
        self.code = code


class ApiKeyMissing(RuntimeError):
    """缺少 API Key。

    注意：这里必须是可被 `except Exception` 捕获的普通异常，不能是 SystemExit ——
    否则看板的请求线程会静默退出，浏览器只看到「空响应」，排查成本极高。
    """


def _read_text(path: str) -> str:
    try:
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return f.read().strip()
    except OSError:
        pass
    return ""


def _key_from_env_file(path: str) -> str:
    """从 hithink-finance CLI 的 credentials.env 里取 Key（PC 端复用已保存的凭据）。"""
    txt = _read_text(path)
    if not txt:
        return ""
    for line in txt.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, _, val = line.partition("=")
        if name.strip() in ("HITHINK_FINANCE_API_KEY", "HITHINK_API_KEY", "API_KEY"):
            val = val.strip().strip('"').strip("'")
            if val:
                return val
    return ""


def api_key() -> str:
    # 安卓 App 模式：优先读 App 私有目录的 key 文件（设置页可随时改，下一轮请求即生效）
    k = _read_text((os.environ.get("YAOGU_KEY_FILE") or "").strip())
    if k:
        return k
    k = (os.environ.get("HITHINK_FINANCE_API_KEY") or "").strip()
    if k:
        return k
    k = _read_text(os.path.expanduser("~/.config/yaogu/key"))
    if k:
        return k
    # PC 端兜底：复用 hithink-finance CLI 已保存的凭据，电脑版看板免配置
    home = os.path.expanduser("~")
    cands = []
    if os.environ.get("APPDATA"):
        cands.append(os.path.join(os.environ["APPDATA"], "hithink-finance", "credentials.env"))
    cands += [os.path.join(home, ".config", "hithink-finance", "credentials.env"),
              os.path.join(home, ".hithink-finance", "credentials.env")]
    for env_file in cands:
        k = _key_from_env_file(env_file)
        if k:
            return k
    raise ApiKeyMissing("缺少 API Key：请先设置环境变量 HITHINK_FINANCE_API_KEY，"
                        "或把 Key 写入 ~/.config/yaogu/key（App 内在设置页填写）")


def _get(path: str, params: Optional[dict] = None, retries: int = 3, timeout: int = 20) -> dict:
    url = BASE + path
    if params:
        clean = {k: v for k, v in params.items() if v is not None}
        url += "?" + urllib.parse.urlencode(clean)
    headers = {"X-api-key": api_key(), "accept": "application/json", "User-Agent": UA}
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8", "replace")
            env = json.loads(body)
            if env.get("code") != 0:
                raise ApiError(env.get("code"), env.get("message") or body[:200])
            return env.get("data") or {}
        except ApiError as e:
            # 429 / 5xxx 才重试
            last = e
            if str(e.code) not in ("429",) and not str(e.code).startswith("5"):
                raise
            time.sleep(3 * (attempt + 1))
        except Exception as e:  # 网络抖动
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"请求失败 {path}: {last}")


# ------------------------------------------------------------------ 工具
def to_ms(date_str: str) -> int:
    """'2026-09-29' -> 当日 00:00 (+08) 的 epoch ms"""
    import datetime as dt
    d = dt.datetime.strptime(date_str, "%Y-%m-%d")
    return int(d.replace(tzinfo=dt.timezone(dt.timedelta(hours=8))).timestamp() * 1000)


def from_ms(ms: int) -> str:
    """epoch ms -> '+08' 的 'YYYY-MM-DD'"""
    import datetime as dt
    return dt.datetime.fromtimestamp(ms / 1000, tz=dt.timezone(dt.timedelta(hours=8))).strftime("%Y-%m-%d")


def _paged(path: str, date_ms: Optional[int], size: int = 200, max_pages: int = 10) -> List[dict]:
    out = []
    for page in range(1, max_pages + 1):
        d = _get(path, {"date_ms": date_ms, "page": page, "size": size})
        items = d.get("item") or []
        if not items:
            break
        out.extend(items)
        p = d.get("pagination") or {}
        if len(items) < size or (p.get("pages") and page >= p["pages"]):
            break
    return out


# ------------------------------------------------------------------ 接口封装
def calendar_days() -> List[str]:
    d = _get("/api/a-share/calendar/trading-days")
    ds = []
    for it in d.get("item") or []:
        if isinstance(it, dict):
            if it.get("date"):
                ds.append(str(it["date"]))
            elif it.get("date_ms"):
                ds.append(from_ms(int(it["date_ms"])))
        elif isinstance(it, str):
            ds.append(it[:10])
    # 兼容 '20260909'
    fix = []
    for s in ds:
        s = s.replace("-", "")
        if len(s) == 8 and s.isdigit():
            fix.append(f"{s[:4]}-{s[4:6]}-{s[6:8]}")
        else:
            fix.append(s[:10])
    return sorted(set(fix))


def limit_up_pool(date: Optional[str] = None) -> List[dict]:
    return _paged("/api/a-share/special-data/limit-up-pool", to_ms(date) if date else None)


def limit_break_pool(date: Optional[str] = None) -> List[dict]:
    return _paged("/api/a-share/special-data/limit-break-pool", to_ms(date) if date else None)


def limit_down_pool(date: Optional[str] = None) -> List[dict]:
    return _paged("/api/a-share/special-data/limit-down-pool", to_ms(date) if date else None)


def snapshot(codes: Optional[List[str]] = None) -> Dict[str, dict]:
    """实时快照；codes 为空时取全市场第一页（调用方一般传候选代码）。"""
    params: dict = {}
    if codes:
        params["thscodes"] = ",".join(codes)
    d = _get("/api/a-share/prices/snapshot", params)
    out = {}
    for it in d.get("item") or []:
        code = it.get("thscode")
        if code:
            out[code] = it
    return out


def history(thscode: str, start_ms: int, end_ms: int, adjust: str = "none") -> List[dict]:
    """日K；返回 [{date_ms, open_price, high_price, low_price, close_price, volume, turnover}] 升序。"""
    d = _get("/api/a-share/prices/historical",
             {"thscode": thscode, "start": start_ms, "end": end_ms,
              "adjust": adjust, "interval": "1d"})
    items = d.get("item") or []
    items.sort(key=lambda r: r.get("date_ms", 0))
    return items


def sentiment() -> dict:
    """今日市场情绪：涨停/炸板/跌停家数（用分页 total，size=1 省流量）。"""
    def total(path):
        try:
            d = _get(path, {"page": 1, "size": 1})
            return int((d.get("pagination") or {}).get("total", -1))
        except Exception:
            return -1
    lu = total("/api/a-share/special-data/limit-up-pool")
    bk = total("/api/a-share/special-data/limit-break-pool")
    ld = total("/api/a-share/special-data/limit-down-pool")
    denom = lu + bk if (lu >= 0 and bk >= 0) else 0
    ratio = round(bk / denom * 100, 1) if denom > 0 else None
    return {"limit_up": lu, "break": bk, "limit_down": ld, "break_ratio_pct": ratio, "ts": int(time.time())}
