# 参与开发 / 改代码速查

> 这份文档只回答一件事：**我改了某个东西，接下来要跑哪些命令、同步到哪、CI 会检查什么。**

本仓库的"源"只有一个：`web/`、`mobile/`、`strategy.py`。
`android/app/src/main/python/` 下的是**副本**（打进 APK 用），`web/` 里还有 4 份**内嵌产物**和 2 份**深色样式**，全部由脚本生成。

## 一、改什么 → 跑什么

| 你改了 | 必须执行 | 说明 |
|---|---|---|
| `web/stock.html` / `stock.css` / `stock.js` / `_part_*.css` / `_part_*.js` | `python web/build_dark_theme.py`<br>`python web/build_stock_frontend.py --no-pc`<br>`python web/build_theme_assets.py` | 生成 `stock-dark.css`、`stock_assets.py`、`theme_assets.py` |
| `web/index.html`（妖股雷达页内联样式） | `python web/build_dark_theme.py`<br>`python web/build_index_html.py` | 生成 `radar-dark.css`、`index_html.py` |
| `web/review.html` / `review.css` / `review.js` | `python web/build_review_assets.py`<br>`python web/build_theme_assets.py` | 生成 `review_assets.py` |
| `web/theme.js` | `python web/build_theme_assets.py` | |
| `web/*.py`（服务/数据/分析/复盘引擎） | 无需生成，但要把副本同步过去 | 见第二节 |
| `mobile/*.py`、`strategy.py` | 无需生成，同步副本 | 见第二节 |
| `android/**`（Kotlin / XML / Gradle） | 无需生成 | CI 会构建 APK 验证 |
| 改了任一处 | `python scripts/check_sync.py` | 提交前跑一次，能挡住 90% 的"忘了同步" |

**懒人版（全跑一遍，幂等）：**

```powershell
python web/build_dark_theme.py
python web/build_stock_frontend.py --no-pc
python web/build_index_html.py
python web/build_review_assets.py
python web/build_theme_assets.py
python scripts/check_sync.py
```

## 二、三份副本：改完把 `web/` 同步过去

| 位置 | 用途 | 放什么 |
|---|---|---|
| `web/` | **唯一源** | 全部文件（含 `_part_*`、`build_*.py`、`dev_server.py`） |
| `android/app/src/main/python/web/` | 打进 APK | **只放运行时文件**：`__init__.py`、`dashboard.py`、`stock_{data,analysis,market,review}.py`、`stock.{html,css,js}`、`stock-dark.css`、`stock_assets.py`、`review.{html,css,js}`、`review_assets.py`、`index.html`、`index_html.py`、`radar-dark.css`、`theme.js`、`theme_assets.py` |
| `android/app/src/main/python/mobile/` | 打进 APK | `mobile/*.py` |
| `android/app/src/main/python/strategy.py` | 打进 APK | 与根目录 `strategy.py` 相同 |
| PC 项目的 `yaogu_screener/web/`（不在本仓库） | PC 上 `screener.py` 实际加载 | 与 `web/` 相同 |

**不要**把 `_part_*.js` / `_part_*.css` / `build_*.py` / `dev_server.py` 放进 APK 目录 —— `check_sync.py` 会直接报错。

`scripts/check_sync.py` 输出 `✓ 副本一致性检查通过（web 20 个运行时文件 / mobile / strategy.py）` 才算干净。

## 三、提交前检查清单

```powershell
python -m compileall -q web mobile strategy.py   # 语法
python -m pytest -q                              # 单元测试（strategy / dashboard）
python scripts/check_sync.py                     # 副本一致
python web/build_dark_theme.py                   # 生成物可重现（跑完 git status 应无新增改动）
python web/build_stock_frontend.py --no-pc
python web/build_index_html.py
python web/build_review_assets.py
python web/build_theme_assets.py
git status                                       # 除预期文件外应为空
```

### 单元测试

`tests/` 下是纯函数级别的金标用例（无网络、无 IO、毫秒级）：

| 文件 | 覆盖 |
|---|---|
| `tests/test_strategy.py` | 代码/板块工具、C1~C5 判定（含「正好 +8.0% 必须排除」的浮点边界）、日内承接/走弱状态机、评分单调性与 100 分封顶、涨停池合并、`to_dict()` 的 inf/nan 兜底 |
| `tests/test_dashboard.py` | `save_snapshot_html` 的 `</` 转义、`/api/state` 回调从 server 实例取、token 鉴权 |

跑法：`python -m pytest -q`（首次需 `pip install pytest`）。CI 的 `check.yml` 每次都会跑。

## 四、CI 会检查什么

| 工作流 | 触发 | 做什么 |
|---|---|---|
| `.github/workflows/check.yml` | 每次 push / PR | `compileall` → `pytest` → 重跑 5 个生成器 → `git diff --exit-code`（生成物必须与提交一致）→ `scripts/check_sync.py` |
| `.github/workflows/build-apk.yml` | push 且改动 `android/**` 或该 workflow 本身；也可手动 | 构建 debug + release APK，按版本号命名产物 |

两个工作流都绿了才算"可以发版"。

## 五、几个已经踩过的坑（别再踩）

1. **换行统一 LF**：仓库有 `.gitattributes`（`* text=auto eol=lf`），所有生成脚本也按 LF 读写。
   混入 CRLF 会让 `check.yml` 的"生成物一致"步骤必然失败（曾真实发生过）。
2. **生成物不是源码**：`*_assets.py`、`*_dark.css`、`index_html.py` 都是生成物，手改会被下一次构建覆盖，
   而且 CI 会报 diff 不一致。
3. **`web/` 改了但没同步 APK 副本**：浏览器里看是新样式、装到手机上还是旧的。
4. **PC 端要重启才生效**：`web/` 的 Python 改动需要 `stop_screener.ps1` → `start_screener.ps1`；
   静态资源（html/css/js）每次请求都会重读，不用重启。
5. **`.js` 片段不是独立模块**：`_part_head.js` / `_part_control.js` 用 `node --check` 会报语法错，这是正常的
   （它们只是被 `build_stock_frontend.py` 拼进 `stock.js` 的片段）。
6. **改前端断点/主题时**：两套版式（手机/桌面）与浅色/深色都要各看一眼；主题的深色是**生成**的，
   改浅色后一定要重跑 `build_dark_theme.py`。

## 六、想加新页面时

1. 新建 `web/<page>.html|css|js`（可复用 `stock.css` 的令牌与 `theme.js`）；
2. `web/dashboard.py` 里加路由 + `_load_<page>_html/css/js()`（走 `_read_asset`，为 APK 兜底）；
3. 三个页面的顶部导航 `<nav class="appnav">` 各加一个 Tab（`≥900px` 会自动落在同一网格列，位置对齐）；
4. 若要内嵌进 APK：仿 `build_review_assets.py` 写一个生成脚本，并在 `check.yml` 里加一步；
5. 更新 `README_WEB.md` 的页面表与接口表。

## 七、数据口径红线

- **不要**把龙虎榜净额叫成"主力资金"：同花顺 REST 没有官方主力资金指标，页面上必须标注口径。
- 新增指标时，在 `README_WEB.md`「数据与口径」补一句口径说明。
- 任何页面的结论性文字都要带上「不构成投资建议」的口径。
