# -*- coding: utf-8 -*-
"""
build_watchlist_assets.py —— 把自选股页的 html/css/js 打包成 APK 内嵌的 web/watchlist_assets.py

APK 里 web/watchlist.* 文件有时不随包（或路径不同），dashboard.py 会回退到
`from web.watchlist_assets import HTML/CSS/JS`。这里用三引号字面量内嵌。

用法：python web/build_watchlist_assets.py
产物：web/watchlist_assets.py
"""
from __future__ import annotations

import pathlib

HERE = pathlib.Path(__file__).resolve().parent
DST = HERE / "watchlist_assets.py"


def read(name: str) -> str:
    return (HERE / name).read_text(encoding="utf-8").replace("\r\n", "\n")


def py_literal(text: str) -> str:
    return 'r"""' + text.replace('"""', '"\\""') + '"""'


def main() -> None:
    html = read("watchlist.html")
    css = read("watchlist.css")
    js = read("watchlist.js")
    assets = "\n".join([
        "# -*- coding: utf-8 -*-",
        '"""由 web/build_watchlist_assets.py 生成：APK 内嵌的自选股页资源（勿手改）"""',
        "",
        "HTML = " + py_literal(html),
        "",
        "CSS = " + py_literal(css),
        "",
        "JS = " + py_literal(js),
        "",
    ])
    DST.write_text(assets, encoding="utf-8", newline="\n")
    print(f"[build_watchlist_assets] html {len(html)} / css {len(css)} / js {len(js)} 字符 "
          f"-> {DST.name} {DST.stat().st_size} 字节")


if __name__ == "__main__":
    main()
