# -*- coding: utf-8 -*-
"""把浅色主题文件的深色版本与切换脚本拼进 APK 内嵌资源 theme_assets.py。

用法：先跑 _probe/make_dark_theme.py（或手工更新 stock-dark.css / radar-dark.css），再执行本脚本。
产物：web/theme_assets.py（THEME_JS / STOCK_DARK / RADAR_DARK）
"""
from __future__ import annotations

import pathlib

HERE = pathlib.Path(__file__).resolve().parent
DST = HERE / "theme_assets.py"


def read(name: str) -> str:
    return (HERE / name).read_text(encoding="utf-8")


def py_literal(text: str) -> str:
    return 'r"""' + text.replace('"""', '"\\""') + '"""'


def main() -> None:
    js = read("theme.js")
    stock_dark = read("stock-dark.css")
    radar_dark = read("radar-dark.css")
    out = "\n".join([
        "# -*- coding: utf-8 -*-",
        '"""由 web/build_theme_assets.py 生成：APK 内嵌的主题切换资源（勿手改）"""',
        "",
        "THEME_JS = " + py_literal(js),
        "",
        "STOCK_DARK = " + py_literal(stock_dark),
        "",
        "RADAR_DARK = " + py_literal(radar_dark),
        "",
    ])
    DST.write_text(out, encoding="utf-8")
    print("[build_theme_assets] js %d / stock-dark %d / radar-dark %d -> %s %d 字节" % (
        len(js), len(stock_dark), len(radar_dark), DST.name, DST.stat().st_size))


if __name__ == "__main__":
    main()
