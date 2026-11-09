# 大A小散（妖股低吸雷达 + 个股综合分析）

> 安卓 App 名称：**大A小散**；首页是「个股分析」，顶部「妖股雷达」进入低吸看板。

> **v2.0 首页改版**：App/网页首页现在是 **个股综合分析**（市场全景 + 个股 16 章深度分析），
> 顶部导航「个股分析｜妖股雷达」两枚按钮切换；原来的低吸看板移到 `/radar`。
> 个股分析同样纯本地运行（Python 直连同花顺 REST），见 [README_ANDROID.md](README_ANDROID.md)。

T-1 强势、T 日竞价低开 5%~8% 的“妖股低吸”信号扫描器。默认 **30 秒轮询**一次，
数据源以**同花顺为主**（本地全市场日线 + 同花顺远端实时快照），失败时自动降级
**东财 → 腾讯 → 网易**。

**v1.1 增强**：候选池 JSON 跨进程缓存｜`--as-of` 历史日期回放｜盘前/竞价/午休/收盘时段状态机｜
T-1 涨停池质量标签（连板/封板时间/封单额/涨停原因题材）｜市场情绪面板（涨停/炸板/跌停家数+炸板率）｜
综合评分排序。

**v1.2（P2/P3）**：
- 日内状态机：低开命中后盘中跟踪 **承接确认**（现价收复开盘价）与 **走弱预警**（较开盘再跌3%或逼近昨收-9%），
  事件写入 `events_<T-1>.csv`、看板动态面板实时显示（阈值见 config `intraday`）；
- 离线回测 `backtest.py`：区间回放命中并统计 T+1..T+N 收益/胜率/分组（承接 vs 走弱）。
- **消息推送** `notifier.py`：命中/承接/走弱 → Server酱/企业微信群机器人/自定义 Webhook（config `notify`，默认关闭）。
- **参数网格寻优** `grid_search.py`：对多组低开区间一次扫描评估，输出命中数/胜率/回撤排序表。

**v1.3**：**深水低吸副栏 [-10,-7]** —— 同一候选池内把 T 日低开 7~10% 的“深水区”单独成栏跟踪
（与主栏 [-8,-5] 并列计数、独立时间线/`alerts_deep_<T-1>.csv`/推送标签），
区间在 `config.json → strategy.deep_open_pct_range` 调整。

**v1.4**：**板块资金矩阵模块**（`sector_flow.py`）—— 在主看板之外回答“钱在往哪些板块走”，
并与低吸候选池互证。三类真实证据交叉验证：①**龙虎榜**近 N 个交易日按概念聚合净买入/机构净额（真实成交）
②**板块指数**量价（量比 = 近5日均额/近20日均额、5/10/20 日涨跌幅，扫描成交额前 N 个板块）
③**涨停结构**（涨停/炸板/跌停家数、连板天梯、涨停原因题材）。输出两个名单：
🟥**资金悄悄铺垫**（放量 + 涨幅温和 + 位置不高）、🟩**资金流出警示**（放量下跌 / 高位急跌退潮 / 高位滞涨），
并**穿透到成分股**（本地全市场日线算个股量比/涨幅 × 龙虎榜净额 × 涨停连板标签 → 资金评分排序）。

> ⚠️ **口径必读**：同花顺 API **没有**官方“主力/大单资金流向”指标，本模块全部是上述**代理指标推导**。
> 龙虎榜仅覆盖每日约 55~70 只异动上榜股，**不代表全市场资金**；概念聚合时同一股票计入其所有概念，
> 金额仅可横向排序、**不可加总**；板块量价来自指数接口。信号仅供研究，非投资建议。

### 显示模式（v1.4.1）

主看板“🌊 板块资金矩阵”默认只显示**精简摘要条**，点「展开」进入 Tab 分页：

| 模式 | 位置 | 内容 |
|---|---|---|
| **A 精简摘要条**（默认） | 主看板常驻一行 | `🟥 潜伏 N·板块(量比)… ｜ 🟩 流出 N·… ｜ 🎯 共振流入 N ｜ ⏳ 资金先行 N ｜ 涨停/炸板(率)/跌停 ｜ 弱势 N`，悬停看完整名单 |
| **C 资金共振四象限** | 展开后 `🎯 资金共振` 页签 | 龙虎榜真实资金 × 板块量价：🟥共振流入（资金进+价涨）／⏳资金先行（资金进+价未动，潜伏首选）／⚠上涨派发（价涨但资金净卖出，追高风险）／🟩资金撤离（资金出+价跌） |
| **E 柱状图** | 展开后 `📊 柱状图` 页签 | 三张**纯 CSS 横向柱状图**（零依赖、无 CDN）：①**龙虎榜概念资金发散柱**（净买入向右／红，净卖出向左／绿，中轴为零）②**板块量比柱**（自左向右，橙色虚线 = 潜伏阈值 1.08）③**板块 5 日涨跌幅发散柱**（潜伏 vs 流出对照） |
| **D Tab 分页签** | 展开后顶部 | `📋 名单｜📊 柱状图｜🎯 资金共振｜🔎 成分股穿透｜🌡️ 情绪题材`，切换不刷新；展开状态与页签记忆在浏览器本地 |

柱状图交互细节：每根柱子悬停显示明细（板块类型、5 日涨幅、5 日均额、上榜个股等）；
柱子最窄保留 0.6% 宽度，避免小值消失；发散图共用同一 scale_max，保证长短可比。


独立页 `output/sector_flow.html` 使用同一套摘要条 + 页签布局，并保留全量明细（龙虎榜 TOP18、连板天梯 10 日）。

### 锚定日与扫描口径

- **锚定日**：盘中（交易日 <15:05）自动用**上一完整交易日**（当日 K 线未完成、龙虎榜尚未发布）；
  收盘后（≥15:05）或非交易日用最近完整交易日。可设 `sector_flow.intraday_use_prev_day: false` 改为盘中锚定当日。
- **缓存分离**：盘中锚定当日时量价结果写入 `*_live` 缓存，收盘后（日 K 定格）会用另一份缓存重算，
  不会把盘中未完成的当日 K 线当成收盘数据复用。
- **扫描范围**：按**最新快照成交额**取前 `scan_top_n`（默认 150）个板块计算量价；
  历史复盘时若某板块已掉出成交额 Top N，复核报告会标为「退出扫描范围」，而非信号消失。
- **名单互斥**：潜伏/流出互斥（先判流出，再从剩余挑潜伏），同一板块不会同时上两个榜。

### 资金共振四象限（v1.4.1）

以**龙虎榜净额**为横轴、**板块量价**为纵轴，把有量资金数据的板块分到四类：
`🟥 共振流入`（净买入 + 上涨）｜`⏳ 资金先行`（净买入 + 未涨，潜伏首选）｜
`⚠ 上涨派发`（上涨但净卖出，借涨出货）｜`🟩 资金撤离`（净卖出 + 下跌）。
未覆盖龙虎榜的板块会以数量提示（每日仅数十只个股上榜，故多数板块没有量资金数据）。

> ⚠️ 本工具仅作技术研究/复盘参考，**不构成任何投资建议**。数据可能存在延迟或口径差异，
> 请以交易所与券商终端为准，投资有风险，决策需独立判断。

## 一、策略条件（与 config.json 中的 strategy 一一对应）

记 T 为当前交易日，T-1 / T-2 为往前第 1 / 2 个交易日：

| # | 条件 | 默认参数 |
|---|------|----------|
| C1 | T-1 涨停 **或** 涨幅 > 8% | `t1_gain_min_pct: 8.0`（>8 即含涨停） |
| C2 | T-1 成交量 < T-2 成交量（缩量） | `t1_volume_lt_t2: true` |
| C3 | T-1 收盘价创 30 日新高（严格高于此前 30 根日K收盘最高） | `high_ndays: 30` |
| C4 | T-1 成交额 ≥ 5 亿元 | `t1_amount_min_yi: 5.0` |
| C5 | T 日开盘涨跌幅 ∈ [-8%, -5%]（即低开 5~8 个点） | `t_open_pct_range: [-8.0, -5.0]` |

**过滤**：剔除 ST / *ST（名称含 ST）与北交所股票（默认打开，可用配置关闭）。

口径说明：
- 历史日线取**不复权**价格，T-1 涨幅 = T-1 收盘 / T-2 收盘 − 1；期间发生除权除息会使当日
  涨幅口径偏离交易所值，但 30 日窗口内对妖股筛选影响很小（README 所在窗口内无除权为主）。
- “涨停”标签仅用于展示（按板块粗判 10%/20% 板），筛选本身用的是涨幅 >8%，天然包含涨停。
- 30 日新高按个股自身交易序列比较；上市不足 31 个交易日的自动跳过。

## 二、安装与准备

1. Python ≥ 3.9（只用标准库；网页看板亦零依赖）。
2. 安装并登录同花顺 CLI（提供全市场历史与实时数据）：
   ```bash
   npm i -g @hithink-tech/hithink-finance-cli
   hithink-finance auth login        # 或: echo <API_KEY> | hithink-finance auth login --api-key-stdin
   ```
3. 准备本地全市场日线库（策略 C1~C4 在本地 DuckDB 上跑，一次导出即可扫描全市场）：
   ```bash
   hithink-finance --db data/market.duckdb data init       # 首次（远端全量，耗时较长）
   hithink-finance --db data/market.duckdb data sync       # 每个交易日收盘后增量补到最新
   ```
   之后工具检测到本地库缺 T-1 数据时会自动尝试 `data sync`。

## 三、运行

```bash
cd yaogu_screener
python -X utf8 screener.py            # 循环运行：每 30s 轮询（交易日盘中）
python -X utf8 screener.py --once     # 只扫描一轮（用于盘后复盘/快速核对）
python -X utf8 screener.py --once --as-of 2026-09-08   # 历史回放：把 09-08 当作 T 日（本地K线校验 C5）
python -X utf8 screener.py --refresh-pool              # 忽略候选池缓存强制重算
python -X utf8 screener.py --interval 10 --no-sound
```

python -X utf8 backtest.py --to 2026-09-03 --horizon 3              # 离线回测（默认低开[-8,-5]）
python -X utf8 backtest.py --to 2026-09-03 --horizon 3 --lo -9 --hi -4   # 放宽低开区间对比
python -X utf8 grid_search.py --to 2026-09-03 --horizon 3            # 低开区间网格寻优
```

**推送配置示例**（`config.json → notify`，默认关闭；不配 key 则完全静默）：

```jsonc
"notify": {
  "channel": "serverchan",      // "serverchan" | "wecom" | "webhook"
  "key": "SCTxxxxxxxx",         // serverchan: SendKey；wecom: 机器人key；webhook: 完整URL
  "send_on": ["hit", "confirm", "broken"],
  "cooldown_sec": 300           // 同代码同类事件冷却
}
```

回测输出：`output/backtest_hits_<from>_<to>_h<n>.csv`（逐笔明细）+ 控制台汇总
（T日开盘→收盘、T+1..T+N 收益均值/中位/胜率、入场最大回撤、承接vs走弱分组）。
⚠️ 本工具样本常较小，结果仅用于研究规则方向，切勿过度外推。

常用参数：

| 参数 | 说明 |
|------|------|
| `--interval <秒>` | 覆盖轮询间隔（默认 30，最小 5） |
| `--db <路径>` | 指定本地 DuckDB（默认 `data/market.duckdb`） |
| `--once` | 只跑一轮后退出 |
| `--as-of <YYYY-MM-DD>` | **回放模式**：指定日期作为 T 日，用本地日线的当日开盘/收盘校验 C5 |
| `--refresh-pool` | 强制重算 C1~C4 候选池（默认优先读 `output/pool_<T-1>.json` 缓存） |
| `--no-sector` | 关闭板块资金矩阵模块（只跑低吸扫描） |
| `--sector-recheck [YYYY-MM-DD]` | **板块资金复核**：与指定日快照对比（留空自动取最近一份）后输出报告并退出 |
| `--no-web` / `--no-sound` / `--no-color` | 关闭网页看板 / 声音 / 颜色 |

运行后控制台每次轮询打印一行状态（含**市场情绪**：涨停/炸板/跌停家数与炸板率），命中
（C1~C5 全满足）时高亮 + 蜂鸣提醒。候选池按**综合评分**排序（连板高度/缩量程度/封板早晚/
成交额规模加权），并显示**成色**（首板/2连板…或“大涨”）与**封板时间/封单/涨停原因**。

同时自动开启本地网页看板（默认 <http://127.0.0.1:8311>），3 秒自动刷新，展示：阶段徽标
（盘前/集合竞价/连续竞价/午间休市/已收盘）、情绪面板、候选池（评分/成色/题材列，悬停题材看涨停原因）、
命中时间线与声音提醒。

**时段状态机**（交易日自动切换，非交易时段低频轮询省接口）：
盘前静默(0:00-8:45) → 盘前准备(8:45-9:15) → 集合竞价(9:15-9:30，10s) → 连续竞价(9:30-11:30/
13:00-15:00，按 interval) → 午间休市(11:30-13:00) → 已收盘(≥15:00，如需可自动增量同步本地库供次日使用)。

**网页显示两种方式：**
1. 实时看板：工具运行时打开 <http://127.0.0.1:8311>（控制台会打印地址）；
2. 静态快照：每轮自动把最新状态内嵌生成 `output/latest.html`，
   无需 Python 服务，浏览器**双击该文件**即可查看最近一轮结果（标题会标注“快照”）。

细节：
- 9:15–9:35 若实时快照尚无开盘价，会用同花顺集合竞价快照（live 阶段）补充参考；
- 候选池按 T-1 缓存复用，跨进程秒启；历史回放（`--as-of`）不依赖实时行情，全程走本地K线；
- 异常自动降级并自愈：同花顺快照失败切东财/腾讯，主循环单轮异常不会中断进程。

**常驻运行（推荐盘中全天使用）** —— 用独立进程启动，避免被会话/后台任务的运行时限回收：

```powershell
# 启动（后台常驻；日志与 PID 落盘）
$p = Start-Process python -ArgumentList '-u','-X','utf8','screener.py','--interval','30','--no-sound' `
     -WorkingDirectory 'D:\DeepSeek_workspace\yaogu_screener' `
     -RedirectStandardOutput 'D:\DeepSeek_workspace\yaogu_screener\output\run.log' `
     -RedirectStandardError  'D:\DeepSeek_workspace\yaogu_screener\output\run.log.err' `
     -WindowStyle Hidden -PassThru
$p.Id | Out-File 'D:\DeepSeek_workspace\yaogu_screener\output\screener.pid'

# 停止
Stop-Process -Id (Get-Content 'D:\DeepSeek_workspace\yaogu_screener\output\screener.pid')
```

进程按状态机自行休眠/唤醒；跨日后首次启动若发现 T-1 数据缺失会自动 `data sync`（实测已自动补齐并重建当日候选池）。

**开机/登录自启（已配置）**
- 登录启动项：`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\YaoguScreener.cmd`
  → 隐藏启动 `watchdog_screener.ps1`；
- 看门狗：每 60 秒检查 8311 端口，掉线即调用 `start_screener.ps1` 重新拉起（幂等，不会重复启动）；
- 相关脚本：`start_screener.ps1`（启动并记录真实监听 PID）、`stop_screener.ps1`（停止）、
  `watchdog_screener.ps1`（保活，日志 `output\watchdog.log`）；
- 实测自愈：手动杀掉进程后 **21 秒**自动恢复服务。

> 说明：启动目录方式在**用户登录后**生效。若需要“开机即运行（无需登录）”，可在**管理员** PowerShell 中执行：
> ```powershell
> schtasks /Create /TN YaoguScreener /TR "D:\DeepSeek_workspace\yaogu_screener\launch_screener.cmd" /SC ONSTART /RU SYSTEM /RL HIGHEST /F
> ```
> （本机当前非管理员环境无法注册计划任务，故默认采用启动目录 + 看门狗方案。）

## 四、输出文件（output/ 目录）

| 文件 | 内容 |
|------|------|
| `pool_<T-1日期>.csv` | 当日通过 C1~C4 的候选池（含评分/连板/封板/封单/题材） |
| `pool_<T-1日期>.json` | 候选池缓存（下次启动秒加载；`--refresh-pool` 强制重算） |
| `alerts_<T-1日期>.csv` | 每次 C5 命中的时间戳明细（历史追加） |
| `latest.html` | 最新一轮结果的自包含网页快照（双击即可查看） |
| `symbols_<日期>.json` | 同花顺股票名称表缓存（每日） |
| `calendar_<日期>.json` | 交易日历缓存（每日） |
| `bars_<起>_<止>.csv` | 全市场日线导出缓存（用于本地扫描） |
| `sector_flow_<T>.json` | 板块资金矩阵完整快照（含板块指标/龙虎榜聚合/穿透明细，供复核 diff） |
| `sector_flow_<T>.csv` | 板块矩阵表格（Excel 可看：分组/量比/涨跌/龙虎榜净额/共振） |
| `sector_flow.html` | **板块资金矩阵独立看板**（自包含，双击即看，无需服务） |
| `recheck_sector_flow_<前>_<后>.md` / `.html` | **复核报告**：潜伏是否延续、流出是否止跌、题材与龙虎榜概念迁移 |
| `sf_cache/` | 板块资金专用缓存（板块目录/快照/日线/成分股/涨停池，按交易日粒度，可安全删除） |

## 板块资金矩阵（v1.4）用法

```bash
# 独立跑一轮并落盘（默认扫描成交额 Top150 板块；首次约 60~90s，当日重跑走缓存仅数秒）
python -X utf8 sector_flow.py --once
python -X utf8 sector_flow.py --once --top-n 40        # 快速试跑（只看大板块）
python -X utf8 sector_flow.py --as-of 2026-09-30       # 指定 T 日（复盘回放）
python -X utf8 sector_flow.py --recheck --prev 2026-09-30   # 与指定日快照对比复核

# 集成在主工具里（默认开启，后台线程每 300s 刷新，不阻塞低吸轮询）
python -X utf8 screener.py --interval 30
python -X utf8 screener.py --sector-recheck            # 复核最近两份快照
```

**锚定日规则**：盘中用 T-1（保证涨停池/龙虎榜数据完整），已收盘(≥15:05)或非交易日用 T 日。
看板顶部“🌊 板块资金矩阵”面板展示潜伏/流出名单、龙虎榜概念资金 TOP、以及穿透出的成分股资金信号。

**节后/事件后复核**：节前或事件前正常跑过一轮后，节后首个交易日直接运行
`python -X utf8 screener.py --sector-recheck 2026-09-30`（或 `sector_flow.py --recheck --prev <节前日期>`），
即可得到“原潜伏板块是否延续、原流出板块是否止跌、题材与主力概念如何迁移”的对照报告。

**关键配置**（`config.json → sector_flow`）：`scan_top_n`（量价扫描板块数，越大越慢）、
`light_refresh_seconds`（后台刷新间隔）、`penetrate_top_n`/`penetrate_stocks`（穿透板块与个股数）、
`thresholds`（潜伏/流出的量比与涨跌幅阈值，可自行调松紧）。

## 五、修改策略参数

直接编辑 `config.json`，例如把低开区间放宽到 -9%~-4%：

```json
"strategy": { "t_open_pct_range": [-9.0, -4.0], ... }
```

或把成交额门槛调成 8 亿：`"t1_amount_min_yi": 8.0`。改完重启即可。

其他可选配置：

```jsonc
"sentiment_refresh_seconds": 60,   // 市场情绪(涨停/炸板/跌停)刷新间隔，0=关闭
"auto_sync_daily": false           // 15:02 后自动 data sync 一次，为次日预生成候选做准备
```
注意：`auto_sync_daily: true` 需要 CLI 登录态可用且数据目录可写；也可保持关闭，盘中
每次启动时若发现 T-1 数据缺失，工具仍会自动尝试同步。
