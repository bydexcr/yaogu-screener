# 大A小散 · 安卓 App（云构建版）

> App 名称：**大A小散**（桌面图标名，`AndroidManifest.xml` 的 `android:label`）。
> 首页为「个股分析」，顶部导航三个入口：`个股分析`（默认）｜`妖股雷达`｜`复盘`。

用 GitHub Actions **云端打包 APK**，本机无需安装 Android Studio / SDK。
App 独立运行：内置 Python（Chaquopy）+ 同花顺 REST 数据层 + 本机看板 + 系统通知，
不需要电脑、不需要 Termux、不需要 Node CLI / DuckDB。

- 页面功能、接口、版式与主题怎么改 → 看 [README_WEB.md](README_WEB.md)
- 改代码要跑哪些脚本、同步到哪 → 看 [CONTRIBUTING.md](CONTRIBUTING.md)

## 一、工程结构（本仓库与 App 相关的部分）

```
android/                            # Android 工程（Gradle + Chaquopy Python 3.11）
  app/build.gradle                  # 版本号自动递增 + 统一签名配置
  app/src/main/AndroidManifest.xml  # 权限最小化、allowBackup=false
  app/src/main/java/com/yaogu/radar/
    MainActivity.kt                 # WebView 全屏看板；把设置里的主题注入 WebView
    SettingsActivity.kt             # 设置页：API Key / 区间 / 阈值 / 主题 …
    DashboardService.kt             # 前台服务：常驻运行 Python 主循环（30s 轮询）
    Notifier.java                   # Python -> 系统通知 桥
  app/src/main/python/              # 内嵌 Python（与仓库根 web/、mobile/、strategy.py 同步）
    android_main.py                 # 入口：起主循环 + 看板服务
    strategy.py / web/ / mobile/
.github/workflows/
  build-apk.yml                     # 云构建：产出 APK（签名 / 版本号 / 产物命名）
  check.yml                         # 轻量校验：语法 / 生成物一致 / 副本一致
mobile/                             # REST 版主循环（不依赖 DuckDB）
web/                                # 看板与个股分析（唯一源）
strategy.py                         # 低吸策略纯函数
```

## 二、使用方法（3 步）

1. 把本仓库推到 GitHub（或直接用现成的仓库）；
2. 仓库页面 → **Actions → build-apk → Run workflow**，等约 2~10 分钟；
3. 在运行结果页底部下载 **`daxiaosan-v<版本>-apks`** 产物 → 传到手机安装（允许"未知来源"），
   里面 `release/` 与 `debug/` 各一个包，装哪个都行。
   首次打开 App 输入同花顺 **API Key**（与电脑版 hithink-finance 相同），点"保存并启动"。

> 想以后**直接覆盖安装**不用卸载？见下一节「版本号与签名」，做一次 Secret 配置即可。
> 仓库可以是私有仓库；GitHub 免费账户每月 2000 分钟 Actions 额度，足够多次构建。
> 本地有 Android Studio 的话，也可以直接打开 `android/` 目录 Run（需要本地 Gradle + JDK 17）。

## 三、App 行为

- 启动后：
  1. 前台服务运行 Python 主循环（默认 30 秒轮询）；
  2. WebView 打开 `http://127.0.0.1:8311/` → **个股分析首页**（市场全景 + 搜索框）；
     顶部可切到「妖股雷达」（`/radar`，候选池 / 低开命中 / 深水 / 承接·走弱 / 情绪）与「复盘」（`/review`）；
  3. 命中 / 承接 / 走弱 → 系统通知（"盘中提醒"渠道，高优先级）；**点击通知直接回到 App 主界面**；
  4. 右上角 **⚙ 设置页**：API Key（**可清空重填**，清空后需重新填写才能取数）、轮询间隔、
     低开主栏区间、深水区间、T-1 涨幅阈值、成交额阈值、新高天数、剔除 ST / 北交所开关、
     **界面主题（浅色 / 深色）**、声音提醒、**停止后台监控**（停止后重开 App 恢复）。
- **设置保存即热生效**：配置写入 App 私有目录，Python 侧 ≤15 秒内检测到文件变化即重新加载；
  Key 修改下一轮请求即用新 Key；主题切换即时生效。
- 数据源：同花顺 REST（`https://fuyao.aicubes.cn`，请求头 `X-api-key`）——
  行情 / 涨停池 / 炸板池 / 跌停池 / 连板天梯 / 龙虎榜 / 热榜 / 财报 / 估值 / 板块。
- Key 存放：App 私有目录（`filesDir/key`），不写入仓库。

## 四、版本号与签名（不用每次卸载重装）

手机"直接覆盖安装"只认两条规则，现在两条都自动满足：

| 条件 | 现状 |
|---|---|
| `versionCode` 不能比已安装的小 | 自动取**构建时间戳（分钟）**，每次构建必然变大，不用手改 |
| 签名证书必须完全一致 | 需要**一次性**把 keystore 存进仓库 Secrets，之后所有构建都用它签名 |

- `versionName` 形如 `2.0.26`（26 = GitHub Actions 运行号；本地构建则是 `2.0.20261109.2015`）；
- App 里能看到版本：**设置页顶部**显示「版本 2.0.26 · 构建号 29904712」；
- 产物命名带版本：`daxiaosan-v2.0.26-apks`（内含 `daxiaosan-v2.0.26-release.apk` 与 `-debug.apk`）；
- 需要手工指定版本时，构建前设置环境变量 `VERSION_CODE` / `VERSION_NAME` 覆盖即可。

### 一次性配置稳定签名（约 2 分钟）

> ✅ **本仓库已配置完成**（2026-11-10）：`KEYSTORE_BASE64` / `KEYSTORE_PASSWORD` 两个 Secret 已就位，
> 构建日志会显示「签名来源：仓库 Secret（签名稳定，可覆盖安装）」，Actions 里已无 keystore 产物残留。
> keystore 备份在本地私密位置（不在仓库内）。下面步骤仅供新仓库/迁移时参考。

1. 先跑一次构建：Actions → build-apk → **Run workflow**；
2. 在该次运行页面底部下载产物 **`yaogu-keystore-keep-as-secret`**，解压得到 `keystore.jks` 与 `keystore-password.txt`；
3. 把 `keystore.jks` 转成 base64（Windows PowerShell）：
   ```powershell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("keystore.jks")) | Set-Content ks.b64
   ```
4. 仓库 → Settings → Secrets and variables → Actions → **New repository secret**，加两条：
   - `KEYSTORE_BASE64` = `ks.b64` 的全部内容（一长串，别带换行）；
   - `KEYSTORE_PASSWORD` = `keystore-password.txt` 里的密码；
5. 把 `keystore.jks` + 密码另存到私密位置，然后**删除该次运行里的 keystore 产物**；
6. 再跑一次构建，日志出现 `签名来源：仓库 Secret（签名稳定，可覆盖安装）` 即成功；
7. **最后一次**卸载旧 App，装这次的新包。之后每次新包都是「下载 → 点安装 → 覆盖」，Key 和设置都保留。

注意事项：

- keystore **不要提交进仓库**（泄漏等于别人能签发"更新包"覆盖你手机上的 App）；
- **建议把仓库设为 private**（Settings → General → Danger Zone → Change visibility）；
- 公开仓库里 `yaogu-keystore-keep-as-secret` 产物等同公开（含密码文件），配好 Secret 后**立即删除该产物**；
- `debug` 与 `release` 共用同一把钥匙，可以互相覆盖安装。

## 五、已知边界

| 项目 | 说明 |
|---|---|
| 机型 | 内置 **arm64-v8a + armeabi-v7a**（老机型/部分模拟器可用），APK 因此略大；想跑 x86_64 模拟器需自行加 ABI |
| 最低系统 | Android 7.0（minSdk 24），targetSdk 34 |
| 后台保活 | 前台服务已声明 `dataSync` 类型 + 常驻通知；建议在系统设置里给 App **关闭电池优化**，否则部分厂商 ROM 仍可能杀后台 |
| 通知 | Android 13+ 首次运行会请求"通知权限"，请允许；否则看不到提醒 |
| 流量/电量 | 盘中每 30s 一次快照（候选 ≤100 只），每天候选构建约 60~200 次日K请求 |
| 明文 HTTP | 已用 `res/xml/network_security_config.xml` 收紧：**只允许 `127.0.0.1` / `localhost` 明文**，其余域名强制 TLS（不再全局 `usesCleartextTraffic="true"`） |
| API Key 存储 | 存放于 App 私有目录（`filesDir/key` + SharedPreferences），`allowBackup=false`；未做加密存储 |
| 局域网暴露 | 看板默认只绑 `127.0.0.1`；若把 host 改成 `0.0.0.0` 或局域网 IP，服务端会**自动生成访问令牌**并要求 `?token=…` |
| 后台控制 | 设置页提供「停止后台监控」；停止后不再轮询与推送，重新打开 App 恢复 |
| 审核/上架 | 自用直接装 APK 即可；上架需开发者账号且涉及金融类目资质，不建议 |
| 安全 | **不要**把 API Key 写进仓库或代码；App 内输入保存即可（Key 泄露请到 fuyao.aicubes.cn/admin 重置） |

## 六、构建失败排查

- `Chaquopy` 报 Python 版本不支持：把 `app/build.gradle` 中 `version = "3.11"` 改为 `"3.10"`；
- 拉不到依赖：检查 GitHub Actions 网络，必要时在 `android/gradle.properties` 里调代理；
- APK 安装失败（`INSTALL_FAILED_UPDATE_INCOMPATIBLE`）：签名与旧版不一致，说明 Secret 没配好，见第四节；
- APK 安装失败（其它）：手机需允许"安装未知应用"，或先关闭"应用安装校验"；
- App 打开白屏 / 页面报「市场全景加载失败」：进设置页确认 API Key 已填；再打开 `/api/diag`（浏览器或页面「诊断」按钮）看自检信息。

⚠️ 仅供技术研究，不构成投资建议。
