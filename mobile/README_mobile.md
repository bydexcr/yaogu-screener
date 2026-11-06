# 妖股低吸 · 安卓 Termux 独立版

不依赖电脑、不装 Node CLI、不装 1GB DuckDB：直接用 Python + 同花顺 REST 接口在手机上运行。

## 与 PC 版的差异（先看）

| 项目 | PC 版 | 手机版 |
|---|---|---|
| 数据源 | 本地 DuckDB（全市场 10 年）+ 同花顺快照 | **纯 REST**（同花顺接口直连） |
| C1 候选来源 | 全市场涨幅>8% 扫描 | **T-1 涨停池 ∪ 炸板池** 为种子（覆盖绝大多数妖股；创业板/科创板“大涨但未涨停且未炸板”的极少数会漏） |
| C2~C4 | 本地日线 | 对种子逐只拉近 40 日K（约 60~200 次请求/天） |
| C5 / 承接 / 走弱 | 30 秒快照 + 状态机 | 相同 |
| 通知 | 控制台/声音/看板 | **Termux 系统通知**（或 Server酱） |
| 看板 | http://127.0.0.1:8311 | 相同（复用同一份 index.html） |

## 安装（Termux）

```bash
pkg update && pkg install -y python termux-api
# 把整个 yaogu_screener 目录（或至少 strategy.py + web/ + mobile/）放进 Termux 主目录
cd ~/yaogu_screener/mobile

export HITHINK_FINANCE_API_KEY=你的key      # 或：mkdir -p ~/.config/yaogu && echo 你的key > ~/.config/yaogu/key

bash run_mobile.sh                          # 启动（默认 30s 轮询 + 本机看板）
# 手机浏览器打开：http://127.0.0.1:8311
```

只跑一轮 / 回放：

```bash
python live_mobile.py --once
python live_mobile.py --as-of 2026-09-29 --once
```

## 保活（防止 Android 杀后台）

1. 系统设置 → 应用 → Termux → 电池 → **不优化/无限制**；
2. `termux-wake-lock` 已包含在 `run_mobile.sh` 里（会持有唤醒锁，状态栏有通知）；
3. 建议用 Termux 前台会话运行，不要切走清后台；
4. 可选：`pkg install termux-boot`，在 Termux:Boot 里放一个开机脚本执行 `bash run_mobile.sh`。

## 性能与流量（参考值）

- 每天 1 轮候选构建：涨停池/炸板池分页 ≈ 3~5 次 + 逐股日K ≈ 60~200 次（每次返回 40 根，几十 KB）；
- 盘中：每 30 秒 1 次快照（候选 ≤100 只一批），流量约 100KB/次；
- 存储：候选池缓存 JSON/CSV 约 100KB/天。

## 文件说明

| 文件 | 作用 |
|---|---|
| `rest_client.py` | 同花顺 REST 客户端（日历/涨停池/炸板池/跌停池/快照/日K/情绪） |
| `pool_mobile.py` | 候选池构建（种子→逐只日K→C1~C4→标签+评分） |
| `live_mobile.py` | 主循环：C5 主栏/深水、承接/走弱、看板、通知 |
| `notify_mobile.py` | Termux 通知 / Server酱 |
| `config_mobile.json` | 参数（区间、间隔、端口） |
| `run_mobile.sh` | 启动脚本（含 wake-lock） |

数据接口基址 `https://fuyao.aicubes.cn`，鉴权头 `X-api-key`；该 Key 与电脑上的 `hithink-finance` 通用。

⚠️ 仅供技术研究，不构成投资建议；手机端数据量/延迟与电脑版不同，请以券商终端为准。
