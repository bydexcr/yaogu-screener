# -*- coding: utf-8 -*-
"""
build_review_assets.py —— 把复盘页的 html/css/js 打包成 Chaquopy APK 内嵌的 web/review_assets.py

APK 里 web/review.html 等文件有时不随包（或路径不同），dashboard.py 会回退到
`from web.review_assets import HTML/CSS/JS`。这里用三引号字面量内嵌。

用法：python web/build_review_assets.py
产物：web/review_assets.py
"""
from __future__ import annotations

import pathlib

HERE = pathlib.Path(__file__).resolve().parent
DST = HERE / "review_assets.py"


def read(name: str) -> str:
    return (HERE / name).read_text(encoding="utf-8")


def py_literal(text: str) -> str:
    return 'r"""' + text.replace('"""', '"\\""') + '"""'


def main() -> None:
    html = read("review.html")
    css = read("review.css")
    js = read("review.js")
    assets = "\n".join([
        "# -*- coding: utf-8 -*-",
        '"""由 web/build_review_assets.py 生成：APK 内嵌的复盘页资源（勿手改）"""',
        "",
        "HTML = " + py_literal(html),
        "",
        "CSS = " + py_literal(css),
        "",
        "JS = " + py_literal(js),
        "",
    ])
    DST.write_text(assets, encoding="utf-8")
    print(f"[build_review_assets] html {len(html)} / css {len(css)} / js {len(js)} 字符 -> {DST.name} {DST.stat().st_size} 字节")


if __name__ == "__main__":
    main()
