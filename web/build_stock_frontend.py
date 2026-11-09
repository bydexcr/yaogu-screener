# -*- coding: utf-8 -*-
"""
build_stock_frontend.py —— 生成手机端「个股分析」前端

做的事情：
  1. 从 PC 版 stock-analyzer/public/app.js 抽取渲染层（格式化/图表/各章节渲染/市场全景渲染）
  2. 与手写控制层（_part_head.js、_part_control.js）拼装成 web/stock.js
  3. 合并 PC 版 styles.css + 手机端覆盖层（_part_mobile.css）为 web/stock.css
  4. 生成 APK 用的内嵌资源模块 web/stock_assets.py（文件缺失时 dashboard.py 回退使用）

用法：python web/build_stock_frontend.py
依赖：仓库内 ../stock-analyzer（PC 版个股分析工具）存在；不存在时直接用已生成的 stock.js/stock.css
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PC = Path(r"D:\DeepSeek_workspace\stock-analyzer\public")


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def extract_pc_parts(app_js: str):
    """"抽取 PC 版 app.js 的两段：渲染层 与 市场全景层"""
    lines = app_js.splitlines(keepends=True)

    def idx_of(pattern):
        for i, l in enumerate(lines):
            if re.search(pattern, l):
                return i
        raise SystemExit(f"未找到标记: {pattern}")

    i_format = idx_of(r"/\* -+ 格式化")
    i_search = idx_of(r"/\* -+ 搜索")
    i_market = idx_of(r"/\* -+ 首页：市场全景")
    i_poll = idx_of(r"async function pollStatus")
    renders = "".join(lines[i_format:i_search])
    market = "".join(lines[i_market:i_poll])
    # 章节渲染结束后触发折叠绑定
    needle = '$("#statusText").textContent = `已分析 ${d.resolved.name}`;'
    if needle in renders:
        renders = renders.replace(
            needle, needle + '\n    if (typeof initCollapse === "function") initCollapse();', 1)
    # 手机端没有快捷标签容器
    market = market.replace(
        'if (hot.length) {\n      $("#quickChips").innerHTML',
        'if (hot.length && $("#quickChips")) {\n      $("#quickChips").innerHTML')
    return renders, market


def py_literal(text: str) -> str:
    return 'r"""' + text.replace('"""', '"\\""') + '"""'


def main():
    head = read(HERE / "_part_head.js")
    control = read(HERE / "_part_control.js")

    js_target = HERE / "stock.js"
    if (PC / "app.js").exists():
        renders, market = extract_pc_parts(read(PC / "app.js"))
        js = "\n".join([head.rstrip(), "", renders.rstrip(), "", market.rstrip(), "", control.lstrip()])
        js_target.write_text(js, encoding="utf-8")
        css = read(PC / "styles.css") + "\n" + read(HERE / "_part_mobile.css")
        (HERE / "stock.css").write_text(css, encoding="utf-8")
        print(f"[build] 从 PC 版抽取渲染层：renders {renders.count(chr(10))} 行 / market {market.count(chr(10))} 行")
    else:
        js = js_target.read_text(encoding="utf-8")
        css = read(HERE / "stock.css")
        print("[build] 未找到 PC 版源码，保留现有 stock.js / stock.css")

    html = read(HERE / "stock.html")
    assets = "\n".join([
        "# -*- coding: utf-8 -*-",
        '"""由 web/build_stock_frontend.py 生成：APK 内嵌的个股分析前端资源（勿手改）"""',
        "",
        "HTML = " + py_literal(html),
        "",
        "CSS = " + py_literal(css),
        "",
        "JS = " + py_literal(js),
        "",
    ])
    (HERE / "stock_assets.py").write_text(assets, encoding="utf-8")

    print(f"[build] stock.js  {js.count(chr(10))} 行")
    print(f"[build] stock.css {css.count(chr(10))} 行")
    print(f"[build] stock_assets.py {(HERE / 'stock_assets.py').stat().st_size} 字节")


if __name__ == "__main__":
    main()
