# -*- coding: utf-8 -*-
"""
build_dark_theme.py —— 由浅色样式生成深色主题样式表

浅色是"源"：`stock.css` 与雷达页 `index.html` 的内联样式；
深色是通过一张固定的颜色映射表反向生成的，改浅色后重跑本脚本即可。

用法：python web/build_dark_theme.py
产物：web/stock-dark.css、web/radar-dark.css
"""
from __future__ import annotations

import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent

# 浅色 → 深色
INV = {
    "#ffffff": "#0f141c",
    # —— 微暖纸色系（去 AI 味那版）——
    "#f7f5f1": "#070a0f",   # --bg
    "#efece6": "#0b1017",   # --bg-soft
    "#f4f1eb": "#141a24",   # --panel-2
    "#f5f2ec": "#141a24",   # 雷达页 --card-2
    "#e9e5dc": "#1a2330",   # --panel-3
    "#ddd8cf": "#232c3a",   # --line
    "#e9e4db": "#181f29",   # --line-soft
    "#14181d": "#eef3fa",   # --text
    "#4c545e": "#9aa7b9",   # --text-dim
    "#828b96": "#657180",   # --text-mute
    "#1e4fbf": "#4e8cff",   # --accent
    "#2f6fd0": "#7fb0ff",   # --accent-2
    "#414a56": "#aeb9c6",   # 分区带标题色（深色下要提亮）
    # —— 旧冷蓝灰系（保留兼容）——
    "#f7f9fd": "#141a24",
    "#f4f7fc": "#10161f",
    "#f3f6fb": "#070a0f",
    "#eef3fb": "#131a25",
    "#eef3fa": "#0b1017",
    "#eaf0f9": "#0b1017",
    "#e9eff8": "#1a2330",
    "#e8eef7": "#181f29",
    "#e6eefb": "#16233a",
    "#e4eaf4": "#1a2330",
    "#dbe3ef": "#232c3a",
    "#e3e9f2": "#1f2836",
    "#ccdcf5": "#1b2b47",
    "#ccd9ee": "#23314a",
    "#c3d5ee": "#2a4a72",
    "#b7cbe8": "#3c5f92",
    "#cfd9e8": "#26313f",
    "#c9d5e6": "#2b3646",
    "#a9b6c9": "#3b4656",
    "#9dbfe8": "#2a4a72",
    "#9aa9bd": "#4a5c72",
    "#8b98ab": "#5b6778",
    "#7d8ca1": "#657180",
    "#52637a": "#9aa7b9",
    "#143049": "#e6edf8",
    "#12233a": "#eef3fa",
    "#b32434": "#ffb3bd",
    "#0a7050": "#9ae6c4",
    "#8a6300": "#e7c27e",
    "#1d4ed8": "#04141c",
    "#2563eb": "#4e8cff",
    "#3b82f6": "#7fb0ff",
    "#e11d33": "#ff5468",
    # —— 市场全景三张彩色卡（深色下换成低饱和的深色块，避免刺眼）——
    "#dde3d1": "#1b2620",   # 涨跌家数（灰绿）
    "#f4d06b": "#2c2513",   # 两市成交额（琥珀）
    "#c9c5e7": "#232037",   # 涨停结构（淡紫）
    "#2e2b24": "#e6edf8",   # 彩色卡标题字
    "#4a453b": "#a9b6c9",   # 彩色卡副行字
    "#1b1a17": "#e9e5dc",   # 「分析」深色按钮：深色下反相成浅底（字色 #fff 同时被映射成深色）
    "#0a6b5f": "#7fd8b8",   # 复盘页深绿字
    # —— 涨跌分布柱状图（浅色：近黑为主 + 米色高亮；深色：近白为主 + 深灰高亮）——
    "#1e1d1a": "#e6edf8",
    "#ddd6c4": "#3d4c63",
    # 深色块在深色背景上要略微提亮，否则和页面底色糊在一起
    "#191816": "#12161d",
    "#0d9b6c": "#16c784",
    "#c77700": "#ffb020",
    "#e8eef8": "#e8eef8",
}

RGBA = [
    (r"rgba\(\s*15\s*,\s*32\s*,\s*51\s*,\s*(\.\d+)\s*\)", r"rgba(255, 255, 255, \1)"),
    (r"rgba\(\s*255\s*,\s*255\s*,\s*255\s*,\s*(\.\d+)\s*\)", r"rgba(9, 12, 18, \1)"),
    (r"rgba\(\s*30\s*,\s*79\s*,\s*191\s*,\s*([\d.]+)\s*\)", r"rgba(78, 140, 255, \1)"),
    (r"rgba\(\s*37\s*,\s*99\s*,\s*235\s*,\s*([\d.]+)\s*\)", r"rgba(78, 140, 255, \1)"),
    (r"rgba\(\s*225\s*,\s*29\s*,\s*51\s*,\s*([\d.]+)\s*\)", r"rgba(255, 84, 104, \1)"),
    (r"rgba\(\s*13\s*,\s*155\s*,\s*108\s*,\s*([\d.]+)\s*\)", r"rgba(22, 199, 132, \1)"),
    (r"rgba\(\s*199\s*,\s*119\s*,\s*0\s*,\s*([\d.]+)\s*\)", r"rgba(255, 176, 32, \1)"),
    # 新样式表里的暖色投影：深色下改成纯黑投影
    (r"rgba\(\s*28\s*,\s*24\s*,\s*16\s*,\s*([\d.]+)\s*\)", r"rgba(0, 0, 0, \1)"),
]

HEADER = "/* 由 web/build_dark_theme.py 生成：深色主题（浅色 stock.css / 雷达内联样式的反向映射） */\n"

TAIL = """
/* ===== 深色主题兜底：亮底深字，避免「深字压深底」看不清 ===== */
.nav-btn.on,
.seg button.on {
  color: #04141c !important;
  background: linear-gradient(135deg, #22d3ee, #61e6c9) !important;
  border-color: transparent !important;
  box-shadow: 0 2px 10px -6px rgba(34, 211, 238, .55) !important;
}
"""


def read(name: str) -> str:
    """统一按 LF 读取（避免 Windows CRLF 让产物在 CI 上不一致）。"""
    return (HERE / name).read_text(encoding="utf-8").replace("\r\n", "\n")


def write(name: str, text: str) -> None:
    (HERE / name).write_text(text, encoding="utf-8", newline="\n")


def expand_short_hex(text: str) -> str:
    """#fff → #ffffff。映射表是 6 位的，3 位缩写不展开就会被漏掉
    （踩过：按钮 background:#fff 没被映射，配上被映射成浅色的字，直接看不见）。"""
    def sub(m):
        h = m.group(1)
        return "#" + "".join(c * 2 for c in h)
    return re.sub(r"#([0-9a-fA-F]{3})\b", sub, text)


def convert(text: str) -> str:
    # 先做色相替换（深色里的白色浮层 → 浅墨浮层），再做黑白/深底色替换
    for rgx, rep in RGBA:
        text = re.sub(rgx, rep, text)
    text = expand_short_hex(text)

    def sub(m):
        return INV.get(m.group(0).lower(), m.group(0))

    return re.sub(r"#[0-9a-fA-F]{6}\b", sub, text)


def main() -> None:
    write("stock-dark.css", HEADER + convert(read("stock.css")) + TAIL)
    print("[build_dark_theme] stock-dark.css")

    # 四个页面新增的样式表（analysis / overview / radar / review）合成一份深色表：
    # 它们都按 body.an / body.ov / body.rd / body.rv 隔离，合并后互不干扰，
    # 页面只需多挂一个 link，省掉四条路由与四份生成物。
    parts = []
    for name in ("analysis.css", "overview.css", "radar.css", "review.css"):
        parts.append("\n/* ===== %s ===== */\n" % name + convert(read(name)))
    write("pages-dark.css", HEADER + "".join(parts) + TAIL)
    print("[build_dark_theme] pages-dark.css（%d 个来源）" % len(parts))

    html = read("index.html")
    m = re.search(r"<style>(.*?)</style>", html, re.S)
    if not m:
        print("[build_dark_theme] 未找到雷达页内联样式，跳过 radar-dark.css")
        return
    write("radar-dark.css", HEADER + convert(m.group(1)) + TAIL)
    print("[build_dark_theme] radar-dark.css（内联样式 %d 字符）" % len(m.group(1)))


if __name__ == "__main__":
    main()
