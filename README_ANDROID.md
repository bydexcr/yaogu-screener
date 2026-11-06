# 妖股低吸雷达 · 安卓 App（云构建版）

用 GitHub Actions **云端打包 APK**，本机无需安装 Android Studio / SDK。
App 是独立运行的：内置 Python（Chaquopy）+ 同花顺 REST 数据层 + 本机看板 + 系统通知，
不需要电脑、不需要 Termux、不需要 Node CLI / DuckDB。

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
  app/src/main/python/            # 内嵌 Python 代码（自动从仓库根复制）
    android_main.py               # 入口
    strategy.py / web/ / mobile/  # 复用 PC/手机版逻辑与看板页面
.github/workflows/build-apk.yml   # 云构建：手动触发 → 产出 APK
```

## 使用方法（3 步）

1. **建一个 GitHub 仓库**，把整个 `yaogu_screener` 目录（含 `android/`、`.github/`、`mobile/`、`strategy.py`、`web/`）推上去；
2. 仓库页面 → **Actions → build-apk → Run workflow**，等约 5~10 分钟；
3. 在运行结果页底部下载 **yaogu-debug-apk** 产物 → 传到手机安装（允许"未知来源"）。
   首次打开 App 输入同花顺 **API Key**（与电脑版 hithink-finance 相同），点"保存并启动"。

> 提示：仓库可以是私有仓库；GitHub 免费账户每月有 2000 分钟 Actions 额度，足够多次构建。
> 若 Actions 被网络限制，也可把仓库导入任意支持 GitHub Actions 的平台，或本地装 Android Studio 打开 `android/` 目录直接 Run。

## App 行为

- 启动后：

  1. 前台服务运行 Python 主循环（默认 30 秒轮询）；
  2. WebView 显示看板 `http://127.0.0.1:8311`（候选池 / 低开命中 / 深水 / 承接·走弱 / 情绪）；
  3. 命中/承接/走弱 → 系统通知（"盘中提醒"渠道，高优先级）；
  4. 右上角 **⚙ 设置页**：API Key（可清空重填）、轮询间隔、低开主栏区间、深水区间、
     T-1 涨幅阈值、成交额阈值、新高天数、剔除 ST / 北交所开关。

- **设置保存即热生效**：无需重启 App/服务。配置写入 App 私有目录，
  Python 侧 ≤15 秒内检测到文件变化即重新加载（间隔/区间/阈值/开关），Key 修改下一轮请求即用新 Key。
- 数据源：同花顺 REST（`https://fuyao.aicubes.cn`，请求头 `X-api-key`），行情/涨停池/炸板池/快照/日K。
- Key 存放：App 私有目录（`filesDir/key`），不写入仓库。

## 签名与产物（云构建）

- 每次构建产出 **debug + 已签名 release** 两个 APK（`yaogu-android-apks` 产物）；
- 首次构建若仓库没有密钥，会自动生成一个签名 keystore，并额外上传 `yaogu-keystore-keep-as-secret` 产物：
  **下载它**，把文件内容 base64 后存到仓库 Secrets（`KEYSTORE_BASE64`，可选再设 `KEYSTORE_PASSWORD`），
  之后每次构建都复用同一签名，升级安装不会冲突；
- 未设置 Secret 时每次构建签名随机，需卸载旧版再装新版（数据会丢，慎用）；
- 自用可直接安装 APK；上架商店需开发者账号且涉及金融类目资质，不建议。

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
