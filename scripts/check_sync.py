# -*- coding: utf-8 -*-
"""
check_sync.py —— 校验「三份副本」是否一致（本地与 CI 都跑）

本仓库的 Python 前端代码有两份物理拷贝：
  web/                                  ← 源（改代码只改这里）
  android/app/src/main/python/web/      ← 打进 APK 的那份
另外 mobile/ 与 strategy.py 也要同步到 android/app/src/main/python/ 下。

用法：python scripts/check_sync.py
"""
from __future__ import annotations

import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
APK_PY = ROOT / "android" / "app" / "src" / "main" / "python"
APK_WEB = APK_PY / "web"
APK_MOBILE = APK_PY / "mobile"

# APK 里只需要运行时文件（开发工具不打包）
RUNTIME_WEB = [
    "__init__.py", "dashboard.py",
    "stock_data.py", "stock_analysis.py", "stock_market.py", "stock_review.py",
    "hit_log.py", "market_text.py",
    "nav.css", "nav.js", "overview.html", "overview.css", "overview.js",
    "analysis.css",
    "radar.css",
    "pages-dark.css",
    "stock.html", "stock.css", "stock.js", "stock_assets.py", "stock-dark.css",
    "review.html", "review.css", "review.js", "review_assets.py",
    "watchlist_store.py", "watchlist.html", "watchlist.css", "watchlist.js",
    "watch-core.js", "watchlist_assets.py",
    "build_watchlist_assets.py",
    "index.html", "index_html.py", "radar-dark.css",
    "theme.js", "theme_assets.py",
]
DEV_ONLY = [
    "_part_head.js", "_part_control.js", "_part_mobile.css", "_part_desktop.css",
    "_part_sections.css", "build_stock_frontend.py", "build_index_html.py",
    "build_review_assets.py", "build_theme_assets.py", "build_dark_theme.py",
    "dev_server.py",
]


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    problems: list[str] = []

    for name in RUNTIME_WEB:
        src, dst = WEB / name, APK_WEB / name
        if not src.exists():
            problems.append("源文件缺失: web/%s" % name)
        elif not dst.exists():
            problems.append("APK 副本缺失: android/.../web/%s" % name)
        elif sha(src) != sha(dst):
            problems.append("内容不一致（请从 web/ 覆盖过去）: %s" % name)

    for p in sorted((WEB).glob("*.py")) + sorted((WEB).glob("*.js")) + sorted((WEB).glob("*.html")) + sorted((WEB).glob("*.css")):
        if p.name in DEV_ONLY and (APK_WEB / p.name).exists():
            problems.append("APK 目录不该包含开发文件: %s" % p.name)

    for name in ("theme_assets.py",):
        if (WEB / name).exists() and not (APK_WEB / name).exists():
            problems.append("APK 副本缺失: android/.../web/%s" % name)

    for src_dir, dst_dir, label in ((ROOT / "mobile", APK_MOBILE, "mobile"),):
        # *.json 也要查：config_mobile.json 里的策略参数一直是漏同步的
        for p in sorted(src_dir.glob("*.py")) + sorted(src_dir.glob("*.json")):
            dst = dst_dir / p.name
            if not dst.exists():
                problems.append("%s 副本缺失: %s" % (label, p.name))
            elif sha(p) != sha(dst):
                problems.append("%s 内容不一致: %s" % (label, p.name))

    # APK python 根目录还有一份 config_mobile.json（App 以它为工作目录）
    cfg_src = ROOT / "mobile" / "config_mobile.json"
    cfg_dst = APK_PY / "config_mobile.json"
    if cfg_src.exists():
        if not cfg_dst.exists():
            problems.append("config_mobile.json 未同步到 android/.../python/")
        elif sha(cfg_src) != sha(cfg_dst):
            problems.append("config_mobile.json 内容不一致")

    st_src, st_dst = ROOT / "strategy.py", APK_PY / "strategy.py"
    if not st_dst.exists():
        problems.append("strategy.py 未同步到 android/.../python/")
    elif sha(st_src) != sha(st_dst):
        problems.append("strategy.py 内容不一致")

    if problems:
        print("[FAIL] 副本一致性检查未通过：")
        for x in problems:
            print("   -", x)
        return 1

    print("[OK] 副本一致性检查通过（web %d 个运行时文件 / mobile / strategy.py）" % len(RUNTIME_WEB))
    return 0


if __name__ == "__main__":
    # Windows 控制台默认 GBK，输出中文/符号会抛 UnicodeEncodeError 盖掉真实结果
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
