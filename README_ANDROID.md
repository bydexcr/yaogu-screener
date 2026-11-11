# 大A小散 · 安卓 App（云构建版）

> App 名称：**大A小散**（桌面图标名，`AndroidManifest.xml` 的 `android:label`）。
> 首页为「个股分析」，顶部导航「妖股雷达」进入原低吸看板。

用 GitHub Actions **云端打包 APK**，本机无需安装 Android Studio / SDK。
App 是独立运行的：内置 Python（Chaquopy）+ 同花顺 REST 数据层 + 本机看板 + 系统通知，
不需要电脑、不需要 Termux、不需要 Node CLI / DuckDB。

> **v2：首页已改为「个股综合分析」**，顶部导航两个入口：`个股分析`（默认）｜`妖股雷达`。
> 个股分析完全在手机本地计算（Python 直连同花顺 REST，与 PC 版分析口径一致）；
> 妖股雷达即原低吸看板，路径 `/radar`。

## 结构

```
android/                          # Android 工程（Gradle + Chaquopy）
  settings.gradle / build.gradle
  app/build.gradle                # Chaquopy Python 3.11，arm64-v8a
  app/src/main/AndroidManifest.xml
  app/src/main/java/com/yaogu/radar/
    MainActivity.kt               # WebView 全屏看板 + 首次输入 API Key
    DashboardService.kt           # 前台服务：常驻运行 Python 主循环（30s 轮询）
    Notifier.java                 # Python -> 系统通知 桥
  app/src/main/python/            # 内嵌 Python 代码（与仓库根 web/ mobile/ 同步）
    android_main.py               # 入口
    strategy.py / web/ / mobile/  # 复用 PC/手机版逻辑与看板页面
.github/workflows/build-apk.yml   # 云构建：手动触发 → 产出 APK
```

### web/ 目录（个股分析 + 妖股雷达 + 复盘）

| 文件 | 作用 |
| --- | --- |
| `stock.html` / `stock.js` / `stock.css` | 个股分析页（`/`）：市场全景、搜索、16 章节分析、章节折叠 |
| `stock_data.py` | 数据层：直连同花顺 REST + 进程内 TTL 缓存 + 板块成分索引落盘 |
| `stock_analysis.py` | 分析引擎：报价/财务/估值/资金/热度/趋势/杜邦/分红/风险矩阵/同业/评分/相似股 |
| `stock_market.py` | 市场全景：宽度、板块排行（一级/细分/概念 + 领涨股）、涨跌停池、连板梯队、热门榜 |
| `stock_review.py` | **复盘引擎**：一句话总收口 / 盘型环境 / 资金流证据 / 主线轮动 / 高度单元 / 四分层 / 次日观察与证伪 / 股票池更新 / 风险边界，按日存档 `review_<date>.json` |
| `review.html` / `review.css` / `review.js` | **复盘页**（`/review`），章节编号 1 / 2 / 2.5 / 4 / 4.5 / 4.6 / 6 / 10 / 12 / 13 |
| `dashboard.py` | 零依赖 HTTP 服务：`/`（个股分析）、`/radar`（妖股雷达）、`/review`（复盘）、`/api/state`、`/api/market*`、`/api/stock`、`/api/search`、`/api/review*`、`/api/diag` |
| `index.html` / `index_html.py` | 妖股雷达看板（`/radar`） |
| `stock_assets.py` / `review_assets.py` | 由构建脚本生成：APK 内文件缺失时内嵌的前端资源 |
| `build_stock_frontend.py` / `build_review_assets.py` / `build_index_html.py` | 分别重建上面三份内嵌资源 |

复盘接口：`GET /api/review[?date=YYYY-MM-DD][&force=1]`、`GET /api/review/dates`。
口径说明：同花顺 REST **没有**官方「主力资金/大单资金」指标，复盘页「资金流证据」用**龙虎榜净额**，
页面上已标注，不冒充主力资金。

个股分析页的 16 个章节由 `_part_sections.css` 用 CSS 计数器自动编号（1. 2. 3. …），与复盘页编号视觉统一。

改前端后执行：`python web/build_stock_frontend.py`（+ `build_review_assets.py` / `build_index_html.py`），
并把 `web/*` 同步到 `android/app/src/main/python/web/`。

### 桌面端 / 手机端是两套版式

`web/stock.css` 末尾由 `_part_desktop.css` 追加桌面层（构建时自动拼接），按宽度切换：

| 宽度 | 版式 |
|---|---|
| `< 900px` | 手机端：单栏、大按钮、顶部两行（标题 + 两个导航 Tab）、底部安全区留白 —— App 的 WebView 就是这个 |
| `≥ 900px` | 顶部变**单行三段**（品牌 / 导航 Tab / 搜索框），容器最宽 1400px，表格与卡片密度提高 |
| `≥ 1150px` | 市场全景与个股分析结果改**两栏**，宽表/多图模块（业绩趋势、近 5 日、同业对比、风险矩阵）自动跨两列 |
| `≥ 1600px` | 市场全景**三栏**，容器最宽 1640px |

妖股雷达页（`index.html`）自带 `680 / 1280` 断点，宽屏本来就是两栏，未再叠桌面层。
另修了一个窄屏 bug：`@media (max-width:679px)` 里原先 `.tbl{overflow:visible}` 会让板块资金等宽表把**整页撑宽**（实测 390px 页面宽 495px、可左右滑），现已改回 `.tbl{overflow-x:auto}` 只在表格内滚动。

### 浅色主题（默认）

三个页面统一改为**浅色**，不再有深色底：

| 令牌 | 值 | 用途 |
|---|---|---|
| `--bg` / `--bg-soft` | `#f3f6fb` / `#eaf0f9` | 页面底色 |
| `--panel` / `--panel-2` / `--panel-3` | `#ffffff` / `#f7f9fd` / `#e9eff8` | 卡片 / 嵌套块 / 进度条槽 |
| `--line` / `--line-soft` | `#dbe3ef` / `#e8eef7` | 描边 |
| `--text` / `--text-dim` / `--text-mute` | `#12233a` / `#52637a` / `#7d8ca1` | 三级文字 |
| `--accent` / `--accent-2` | `#2563eb` / `#3b82f6` | 主色 |
| `--up` / `--down` / `--warn` | `#e11d33` / `#0d9b6c` / `#c77700` | 红涨 / 绿跌 / 警示 |

- 顶部应用栏改为**白色毛玻璃**（`rgba(255,255,255,.92)` + blur），导航当前项用强调色底 + 蓝字；
- 图表（蜡烛/折线/柱状 SVG）的网格线、坐标文字、涨跌色在 `stock.js` 里同步换成浅色配色；
- 妖股雷达页 `main` 去掉 `max-width:1280px` 上限，改为铺满窗口（左右 28px 内距），消除两侧大片留白；
- 个股分析结果区 `#result` 由 `align-items:start` 改为 **`stretch` + 卡片 `height:100%`（flex 列）**，
  同一行卡片等高，短内容的模块不再在行尾留白。

### 浅色 / 深色切换

右下角悬浮按钮（`☾ / ☀`）切换主题，选择写入 `localStorage['yaogu.theme']`，三页共用；也支持 `?theme=dark` / `?theme=light` 直接指定。

| 文件 | 作用 |
|---|---|
| `theme.js` | 按钮注入 + 记忆 + 切换（`link[data-theme-dark]` 用 `media="not all" → all` 预加载切换，无闪烁） |
| `stock-dark.css` | 深色主题：由 `stock.css` 反向映射生成（个股分析 + 复盘页共用） |
| `radar-dark.css` | 深色主题：由 `index.html` 内联样式反向映射生成（妖股雷达页） |
| `theme_assets.py` | 上述三者打进 APK 的内嵌副本（`build_theme_assets.py` 生成） |
| 图表配色 | `stock.css` 定义 `--chart-grid/--chart-zero/--chart-axis/--chart-ink`，`stock.js` 用 `cv()` 读取，切主题后由 `window.__rerenderCharts()` 重绘 |

生成/重建顺序：改完 `stock.css` 或雷达内联样式后 → 跑 `make_dark_theme.py`（反向映射）→ `build_theme_assets.py` → `build_stock_frontend.py` / `build_index_html.py`。

### 顶部导航三页对齐

三页顶部在 `≥900px` 都是同一套三段网格 `260px | 导航 | 右侧`，并统一 `min-height:76px`、`padding:12px 26px`、`gap:24px`；
妖股雷达页用 `.bar-top{display:contents}` 让 brand / badges 直接落在网格列里，导航固定在**第 1 行第 2 列**。
实测三页导航按钮矩形完全一致：`x = 314 / 413 / 512`，`y = 22`，高 `31px`，容器 `x=310,y=19,高38`。

### web/ 有三份副本，必须保持一致（实际踩过的坑）

| 位置 | 用途 | 放什么 |
|---|---|---|
| `web/` | **唯一源**，改代码只改这里 | 全部文件 |
| `android/app/src/main/python/web/` | 打进 APK | 只放运行时文件：`__init__.py`、`dashboard.py`、`stock_{data,analysis,market}.py`、`stock.{html,css,js}`、`stock_assets.py`、`index.html`、`index_html.py`（不要放 `_part_*.js`、`build_*.py`、`dev_server.py` 这类开发工具） |
| 电脑常驻版的 `yaogu_screener/web/` | PC 上 `screener.py` 实际加载的那份 | 与 `web/` 相同 |

> 只同步了仓库、忘记同步电脑那份时，PC 看板还是旧代码，典型症状是
> **「市场全景加载失败」或板块一直空白**（旧代码缺 `web/__init__.py` 与模块加载兜底）。
> 改完代码把三份对齐后，PC 端要 `stop_screener.ps1` → `start_screener.ps1` 重启才生效。

### 出问题先看 `/api/diag`

`GET /api/diag` 返回环境自检：Python 版本、服务目录、已加载模块、板块索引状态与缓存目录、Key 是否可取到、后台任务日志、最近错误。
页面加载失败时，错误提示旁边有「诊断」按钮，一点就能看到这些信息。

## 使用方法（3 步）

1. **建一个 GitHub 仓库**，把整个 `yaogu_screener` 目录（含 `android/`、`.github/`、`mobile/`、`strategy.py`、`web/`）推上去；
2. 仓库页面 → **Actions → build-apk → Run workflow**，等约 5~10 分钟；
3. 在运行结果页底部下载 **`daxiaosan-v<版本>-apks`** 产物 → 传到手机安装（允许"未知来源"），
   里面 release / debug 各一个包，装哪个都行。
   首次打开 App 输入同花顺 **API Key**（与电脑版 hithink-finance 相同），点"保存并启动"。

> 想以后**直接覆盖安装**不用卸载？按下面「版本号与签名」做一次 Secret 配置即可。
> 仓库可以是私有仓库；GitHub 免费账户每月有 2000 分钟 Actions 额度，足够多次构建。
> 若 Actions 被网络限制，也可把仓库导入任意支持 GitHub Actions 的平台，或本地装 Android Studio 打开 `android/` 目录直接 Run。

## App 行为

- 启动后：

  1. 前台服务运行 Python 主循环（默认 30 秒轮询）；
  2. WebView 打开 `http://127.0.0.1:8311/` → **个股分析首页**（市场全景 + 搜索框）；
     点顶部「妖股雷达」→ `/radar` 低吸看板（候选池 / 低开命中 / 深水 / 承接·走弱 / 情绪）；
  3. 命中/承接/走弱 → 系统通知（"盘中提醒"渠道，高优先级）；
  4. 右上角 **⚙ 设置页**：API Key（可清空重填）、轮询间隔、低开主栏区间、深水区间、
     T-1 涨幅阈值、成交额阈值、新高天数、剔除 ST / 北交所开关。

- **个股分析页**（手机端独立实现，口径与 PC 版一致）：
  - 首页展示市场全景：涨跌家数与分布、成交额、涨停/跌停/炸板、连板梯队、热门板块（一级行业/细分行业/概念，含领涨股与成分下钻）、热股榜/飙升榜/龙虎榜净买/成交额榜；
  - 搜索个股后给出 16 个章节：综合评分、深度解读、企业基本面、多期财务趋势、杜邦分解、业绩成长、主营优势、行业地位、估值、盘面资金、市场热度、近 5 日走势、技术形态、分红送转、风险矩阵、相似股票；
  - 手机端默认只展开前 3 章，标题可点开/收起，右上角「展开全部／收起全部」；
  - 板块成分索引（710 个板块）首次启动后台构建约 30 秒，按日落盘，之后秒开。

- **设置保存即热生效**：无需重启 App/服务。配置写入 App 私有目录，
  Python 侧 ≤15 秒内检测到文件变化即重新加载（间隔/区间/阈值/开关），Key 修改下一轮请求即用新 Key。
- 数据源：同花顺 REST（`https://fuyao.aicubes.cn`，请求头 `X-api-key`），行情/涨停池/炸板池/快照/日K/财报/估值/板块/热榜。
- Key 存放：App 私有目录（`filesDir/key`），不写入仓库。

## 版本号与签名（不用每次卸载重装）

手机能"直接覆盖安装"只认两条规则，现在两条都自动满足了：

| 条件 | 现状 |
|---|---|
| `versionCode` 不能比已安装的小 | 自动取**构建时间戳（分钟）**，每次构建必然变大，不用手改 |
| 签名证书必须完全一致 | 需要你**一次性**把 keystore 存进仓库 Secrets，之后所有构建都用它签名 |

- `versionName` 形如 `2.0.137`（137 = GitHub Actions 运行号；本地构建则是 `2.0.20261109.2015`）；
- App 里能看到版本：**设置页顶部**显示「版本 2.0.137 · 构建号 29867123」；
- 产物命名带版本：`daxiaosan-v2.0.137-apks`（内含 `daxiaosan-v2.0.137-release.apk` 与 `-debug.apk`）；
- 需要手工指定版本时，构建前设置环境变量 `VERSION_CODE` / `VERSION_NAME` 覆盖即可。

### 一次性配置稳定签名（约 2 分钟）

> ✅ **本仓库已配置完成**（2026-11-10）：`KEYSTORE_BASE64` / `KEYSTORE_PASSWORD` 两个 Secret 已就位，
> 构建日志会显示「签名来源：仓库 Secret（签名稳定，可覆盖安装）」，已无 keystore 产物残留在 Actions 里。
> keystore 备份在本地私密位置（不在仓库内）。下面步骤仅在新仓库/迁移时参考。

1. 先跑一次构建：Actions → build-apk → **Run workflow**；
2. 在该次运行页面底部下载产物 **`yaogu-keystore-keep-as-secret`**，解压得到 `keystore.jks` 与 `keystore-password.txt`
   （没配过密码时密码是构建时随机生成的，文件里就是它）；
3. 把 `keystore.jks` 转成 base64（Windows PowerShell）：
   ```powershell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("keystore.jks")) | Set-Content ks.b64
   ```
4. 仓库 → Settings → Secrets and variables → Actions → **New repository secret**，加两条：
   - `KEYSTORE_BASE64` = `ks.b64` 的全部内容（一长串，别带换行）；
   - `KEYSTORE_PASSWORD` = `keystore-password.txt` 里的密码；
5. 把 `keystore.jks` + 密码另存到自己的私密位置，然后**删除该次运行里的 keystore 产物**；
6. 再跑一次构建，日志里出现 `签名来源：仓库 Secret（签名稳定，可覆盖安装）`、运行摘要显示 ✅ 就成功了；
7. **最后一次**卸载旧 App，装这次的新包。之后每次新包都是「下载 → 点安装 → 覆盖」，不用再卸载，Key 和设置都保留。

> 未配置 `KEYSTORE_BASE64` 时，每次构建会临时生成一把新钥匙 —— 那种包**装不到旧版之上**，只能卸载重装。
> 如果先配了 `KEYSTORE_PASSWORD` 再构建，生成的 keystore 就用你设的密码，省得记随机串。

注意事项：

- keystore **不要提交进仓库**（泄漏等于别人能签发"更新包"覆盖你手机上的 App）；
- **建议把仓库设为 private**（Settings → General → 最下方 Danger Zone → Change visibility）：
  这样 Actions 日志和产物只有你能看，keystore 放在产物里也不担心；
- 公开仓库里 `yaogu-keystore-keep-as-secret` 产物等于公开（含密码文件），配好 Secret 后请**立即删除该产物**
  （本仓库在配置完成后已把历史 keystore 产物全部清掉，现只剩 APK 产物）；
- 把 `keystore.jks` + 密码备份到自己的私密位置（换电脑/重装系统后没有它，就只能卸载重装一次）；
- `debug` 与 `release` 两个包现在共用同一把钥匙，可以互相覆盖安装，随意切换。

## 已知边界

| 项目 | 说明 |
|---|---|
| 机型 | 已内置 **arm64-v8a + armeabi-v7a**（老机型/部分模拟器可用），APK 因此略大 |
| 最低系统 | Android 7.0（minSdk 24），targetSdk 34 |
| 后台保活 | 前台服务已声明 `dataSync` 类型 + 常驻通知；建议在系统设置里给 App **关闭电池优化**，否则部分厂商 ROM 仍可能杀后台 |
| 通知 | Android 13+ 首次运行会请求"通知权限"，请允许；否则看不到提醒 |
| 流量/电量 | 盘中每 30s 一次快照（候选 ≤100 只），每天候选构建约 60~200 次日K请求 |
| 审核/上架 | 自用直接装 APK 即可，无需上架；上架需开发者账号且涉及金融类目资质，不建议 |
| 安全 | **不要**把 API Key 写进仓库或代码；App 内输入保存即可（Key 泄露请到 fuyao.aicubes.cn/admin 重置） |

## 构建失败排查

- `Chaquopy` 报 Python 版本不支持：把 `app/build.gradle` 中 `version = "3.11"` 改为 `"3.10"`；
- 网络拉不到依赖：在 Workflow 中可加 `--offline` 无效时检查 GitHub Actions 网络；
- APK 安装失败：手机需允许"安装未知应用"，或先在设置里关闭"应用安装校验"。

⚠️ 仅供技术研究，不构成投资建议。
