# -*- coding: utf-8 -*-
"""
build_index_html.py —— 把 index.html 打包成 Chaquopy APK 内嵌的 web/index_html.py

APK 里 web/index.html 有时不随包（或路径不同），dashboard.py 会回退到
`from web.index_html import HTML`。这里用 base64 内嵌，避免三引号/转义问题。

用法：python web/build_index_html.py
产物：web/index_html.py
"""
from __future__ import annotations

import base64
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "index.html"
DST = HERE / "index_html.py"

HEADER = (
    "# -*- coding: utf-8 -*-\n"
    "# 由 build_index_html.py 自动生成，内嵌网页 HTML（Chaquopy APK 内打包使用），请勿手改\n"
    "import base64\n\n"
)


def main() -> None:
    html = SRC.read_text(encoding="utf-8")
    b64 = base64.b64encode(html.encode("utf-8")).decode("ascii")
    DST.write_text(HEADER + f"HTML = base64.b64decode('{b64}').decode('utf-8')\n", encoding="utf-8")
    print(f"[build_index_html] {SRC.name} {len(html)} 字符 -> {DST.name} {DST.stat().st_size} 字节")


if __name__ == "__main__":
    main()
