# Web 层：看板功能与前端工程

> 这一份讲**页面本身**：三个页面各有什么、接口怎么调、版式与主题怎么切、前端产物怎么生成、改完要同步到哪。
> 打包安装看 [README_APP.md](README_APP.md)；改动流程速查看 [CONTRIBUTING.md](CONTRIBUTING.md)。

Web 层是**零第三方依赖**的：`web/dashboard.py` 用标准库 `ThreadingHTTPServer` 起服务，
页面是原生 HTML/CSS/JS（无框架、无 CDN），数据由 `web/stock_data.py` 直连同花顺 REST 取得。
同一套页面同时服务**电脑浏览器**和**手机 App 的 WebView**（App 只是把本机 `127.0.0.1:8311` 装进 WebView）。

## 一、三个页面

| 路径 | 页面 | 说明 |
|---|---|---|
| `/` | **个股分析** | 市场全景（涨跌分布 / 热门板块 / 涨停·跌停·炸板池 / 连板梯队 / 热股榜·飙升榜·龙虎榜·成交额榜）+ 搜索个股后的 16 章深度分析 |
| `/radar` | **妖股雷达** | 原低吸看板：候选池、低开命中时间线、深水副栏、承接/走弱动态、情绪与板块资金矩阵 |
| `/review` | **复盘** | 当日盘面复盘：1 一句话总收口 / 2 盘型环境 / 2.5 资金流证据 / 4 主线轮动 / 4.5 连板高度 / 4.6 连板梯队 / 6 四分层 / 10 次日观察与证伪 / 12 股票池更新 / 13 风险边界 |

顶部导航三个 Tab 在 `≥900px` 是**像素级对齐**的（同一套三段网格 `260px | 导航 | 右侧`，统一 `min-height:76px`、
`padding:12px 26px`、`gap:24px`；妖股雷达页用 `.bar-top{display:contents}` 让品牌/徽标直接落进网格列）。
实测三页导航按钮矩形一致：`x = 314 / 413 / 512`，`y = 22`，高 `31px`。

个股分析的 16 个章节由 `_part_sections.css` 用 CSS 计数器自动编号（1. 2. 3. …），与复盘页编号视觉统一。

## 二、接口

| 接口 | 作用 |
|---|---|
| `GET /api/market` | 市场全景（宽度、板块排行、涨跌停池、连板梯队、热榜） |
| `GET /api/market/sector?code=` | 单个板块的成分股 |
| `GET /api/stock?q=` | 个股 16 章分析（`q` 可传代码或名称） |
| `GET /api/search?q=` | 代码/名称联想 |
| `GET /api/review[?date=YYYY-MM-DD][&force=1]` | 当日复盘；`date` 查历史存档，`force=1` 强制重算 |
| `GET /api/review/dates` | 已存档的复盘日期列表 |
| `GET /api/state` | 引擎状态（妖股雷达用） |
| `GET /api/diag` | 环境自检：Python 版本、服务目录、已加载模块、板块索引状态与缓存目录、Key 是否可取到、后台任务日志、最近错误 |

> 安全：看板默认只监听 `127.0.0.1`；若配置成 `0.0.0.0` 或局域网 IP 且没设 token，
> `start_dashboard()` 会**自动生成访问令牌**并要求 `?token=…`，避免看板在局域网裸奔。

性能（实测，本机）：`/api/market` 冷启动 7 s 左右，但 `Dashboard.start()` 会在后台**预热一次**，
所以首屏通常是 **0.01 s**；`/api/stock` 冷 0.3~3 s，缓存 TTL 内 26 ms 级。
`/api/review` 冷 6~7 s，读当日存档 0.03 s。

出问题先开 `/api/diag`；页面加载失败时错误提示旁有「诊断」按钮，点了直接摊开这些信息。

## 三、数据口径（必读）

- 数据源：同花顺 REST（`https://fuyao.aicubes.cn`，请求头 `X-api-key`）；行情/涨停池/炸板池/跌停池/连板天梯/龙虎榜/热榜。
- **同花顺 REST 没有官方「主力资金 / 大单资金」指标**。复盘页「资金流证据」用的是**龙虎榜净额**
  （`buyValue - sellValue`），页面上明确标注口径，不冒充主力资金。
- 龙虎榜每日只覆盖数十只上榜股，**不代表全市场资金**；概念聚合时同一只票会计入它所有的概念，金额只能横向排序、不可加总。
- 涨跌分布按个股当日涨跌幅分档（±9.8% 为极端档，0% 计入 0~3% 档）；涨停/跌停家数以交易所涨停池为准。
- 板块成分索引首次构建约 700 次请求（1~2 分钟），按日落盘到 `data_mobile/stock_membership_<date>.json`，之后秒开。

## 四、版式：手机端 / 桌面端两套

`web/stock.css` 由 PC 样式 + `_part_mobile.css` + `_part_desktop.css` + `_part_sections.css` 拼接而成（构建时自动完成）：

| 宽度 | 版式 |
|---|---|
| `< 900px` | 手机端：单栏、大按钮、顶部标题 + 三枚导航 Tab、底部安全区留白 —— App 的 WebView 就是这个 |
| `≥ 900px` | 顶部变**单行三段**（品牌 / 导航 Tab / 搜索框 + ⚙），容器最宽 1400px，表格与卡片密度提高 |
| `≥ 1150px` | 市场全景与个股分析结果改**两栏**；市场全景的「热门板块」占整行，其余 4 张池子卡 2×2 等高（列表内部限高滚动）；热榜 2 列 |
| `≥ 1600px` | 市场全景容器 1640px；热榜 4 张一行 |

妖股雷达页（`index.html`）自带 `680 / 1280` 断点，宽屏本来就是两栏，未再叠桌面层。
窄屏曾有个 bug：`@media (max-width:679px)` 里 `.tbl{overflow:visible}` 会让板块资金等宽表把**整页撑宽**
（实测 390px 页面宽 495px、可左右滑），现已改回 `.tbl{overflow-x:auto}` 只在表格内滚动。

## 五、主题：浅色（默认）/ 深色

- 入口在**设置面板**：桌面端顶栏最右 ⚙ → 「界面主题：浅色 / 深色」；手机端走原生设置页（见 README_APP.md）。
- 选择写 `localStorage['yaogu.theme']`，三页共用；也支持 `?theme=dark` / `?theme=light`（还有 `?sheet=1` 直接打开设置面板，便于排障）。
- 深色样式表用 `media="not all" → all` 预加载切换，**同一帧生效、无闪白**。

| 令牌 | 浅色 | 深色 |
|---|---|---|
| `--bg` / `--bg-soft` | `#f3f6fb` / `#eaf0f9` | `#070a0f` / `#0b1017` |
| `--panel` / `--panel-2` / `--panel-3` | `#ffffff` / `#f7f9fd` / `#e9eff8` | `#0f141c` / `#141a24` / `#1a2330` |
| `--text` / `--text-dim` / `--text-mute` | `#12233a` / `#52637a` / `#7d8ca1` | `#eef3fa` / `#9aa7b9` / `#657180` |
| `--up` / `--down` / `--warn` | `#e11d33` / `#0d9b6c` / `#c77700` | `#ff5468` / `#16c784` / `#ffb020` |

相关文件：

| 文件 | 作用 |
|---|---|
| `theme.js` | 设置面板与主题切换（记忆 + `media` 开关切换 + 切完重绘图表） |
| `stock-dark.css` | 深色：由 `stock.css` 反向映射生成（个股分析 + 复盘共用） |
| `radar-dark.css` | 深色：由 `index.html` 内联样式反向映射生成（妖股雷达） |
| 图表配色 | `stock.css` 定义 `--chart-grid/--chart-zero/--chart-axis/--chart-ink`，`stock.js` 用 `cv()` 读取，切主题后 `window.__rerenderCharts()` 重绘 |

深色下导航/分段控件的当前项是**亮青底 + 深字**（`.nav-btn.on` / `.seg button.on` 在生成脚本里用 `!important` 兜底），
避免"深字压深底"看不清。

## 六、前端产物与生成脚本

`web/` 里有 4 份**内嵌副本**（把 html/css/js 塞进 `.py` 字符串，供 APK 在文件缺失时兜底）
+ 2 份深色样式，全部是**生成物**，不要手改：

| 生成物 | 由谁生成 |
|---|---|
| `index_html.py` | `build_index_html.py` ← `index.html` |
| `stock_assets.py` | `build_stock_frontend.py --no-pc` ← `stock.html` / `stock.css` / `stock.js` |
| `review_assets.py` | `build_review_assets.py` ← `review.html` / `review.css` / `review.js` |
| `theme_assets.py` | `build_theme_assets.py` ← `theme.js` + `stock-dark.css` + `radar-dark.css` |
| `stock-dark.css` / `radar-dark.css` | `build_dark_theme.py` ← `stock.css` / `index.html` 内联样式 |

改完前端按这个顺序跑（**5 个生成器 + 1 个同步校验**）：

```powershell
python web/build_dark_theme.py
python web/build_stock_frontend.py --no-pc
python web/build_index_html.py
python web/build_review_assets.py
python web/build_theme_assets.py
python scripts/check_sync.py
```

这些脚本统一按 **LF** 读写（`.gitattributes` 为 `* text=auto eol=lf`），本机与 CI 生成的产物逐字节一致。
`build_stock_frontend.py` 需要 PC 版渲染层时用环境变量 `STOCK_ANALYZER_PUBLIC` 指定其 `public/` 目录；
本仓库不含 PC 源码，所以通常直接带 `--no-pc` 使用。

## 七、三份副本必须一致

| 位置 | 用途 | 放什么 |
|---|---|---|
| `web/` | **唯一源**，改代码只改这里 | 全部文件（含 `_part_*`、`build_*.py`、`dev_server.py` 这些开发工具） |
| `android/app/src/main/python/web/` | 打进 APK | 只放运行时文件；**不要**放 `_part_*.js`、`_part_*.css`、`build_*.py`、`dev_server.py` |
| PC 常驻版的 `yaogu_screener/web/`（不在本仓库） | PC 上 `screener.py` 实际加载的那份 | 与 `web/` 相同 |

`python scripts/check_sync.py` 会逐字节比对（并检查 APK 目录有没有混进开发文件），CI 的 `check.yml` 每次也会跑。

> 只同步了仓库、忘了同步电脑那份时，症状是 PC 看板还是旧代码（例如「市场全景加载失败」或板块一直空白）。
> 改完把副本对齐后，PC 端要 `stop_screener.ps1` → `start_screener.ps1` 重启才生效。

## 八、本机预览

```powershell
python web/dev_server.py     # 起在 http://127.0.0.1:8399
```

这是**联调模式**：用假的引擎状态喂 `/api/state`，个股分析与复盘页可以正常用真实数据看，
但妖股雷达页只有骨架（没有候选池引擎）。想看完整雷达请装 App，或用 PC 项目的引擎。

## 九、已知边界

- 首屏 `/api/market` 依赖同花顺 REST，网络差时会等几秒（有骨架屏兜住）；预热后通常 0.01 s。
- 板块成分索引首次 1~2 分钟，期间板块领涨股可能缺失，页面会自动重试并提示。
- 个股分析 16 章的数值口径与 PC 版一致，但**未逐章做过业务正确性回归**（见 `docs/` 里的检测报告结论）。
- 复盘「资金流证据」是龙虎榜口径，覆盖范围有限（见第三节）。
- 免责声明：数据来自同花顺金融数据服务，仅供技术研究，**不构成投资建议**。
