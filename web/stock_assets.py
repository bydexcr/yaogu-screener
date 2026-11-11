# -*- coding: utf-8 -*-
"""由 web/build_stock_frontend.py 生成：APK 内嵌的个股分析前端资源（勿手改）"""

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#070a0f">
<title>大A小散 · 个股分析</title>
<link rel="stylesheet" href="/stock.css">
<link rel="stylesheet" href="/stock-dark.css" data-theme-dark media="not all">
</head>
<body>

<header class="appbar">
  <div class="appbar-top">
    <div class="brand">
      <span class="logo" aria-hidden="true">
        <svg viewBox="0 0 64 64" width="22" height="22"><path d="M10 46l11-13 9 8 12-21 12 10" fill="none" stroke="#4e8cff" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="54" cy="30" r="3.4" fill="#7fb0ff"/></svg>
      </span>
      <div class="brand-text">
        <h1>大A小散</h1>
        <p class="status-line"><span class="dot" id="statusBadge"></span><span id="statusText">数据加载中</span></p>
      </div>
    </div>
  </div>
  <nav class="appnav" aria-label="主导航">
    <a class="nav-btn on" href="/">个股分析</a>
    <a class="nav-btn" href="/radar">妖股雷达</a>
    <a class="nav-btn" href="/review">复盘</a>
  </nav>
  <div class="search-box" id="searchBox">
    <svg class="search-icon" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><circle cx="11" cy="11" r="6.6" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M16.2 16.2L21 21" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
    <input id="searchInput" type="search" autocomplete="off" spellcheck="false" enterkeyhint="search"
           placeholder="股票名称或代码，如 贵州茅台 / 600519" aria-label="股票搜索">
    <button id="searchBtn" class="btn-primary" type="button">分析</button>
    <div class="suggest" id="suggest" hidden></div>
  </div>
  <button id="settingsBtn" class="icon-btn" type="button" aria-label="设置" title="设置">⚙</button>
</header>

<main id="main">

  <!-- 首页：市场全景 -->
  <section id="marketView">
    <div class="mk-hero" id="mkHero"><div class="mk-skeleton">正在加载市场全景…</div></div>

    <section class="card" id="mkSectors"></section>

    <section class="card" id="mkLimits"></section>

    <section class="card" id="mkUpPool"></section>

    <section class="card" id="mkDownPool"></section>

    <section class="card" id="mkBreakPool"></section>

    <div class="mk-hot-grid" id="mkHot"></div>

    <div class="mk-foot" id="mkFoot"></div>
  </section>

  <!-- 加载中 -->
  <section id="loadingState" class="loading" hidden>
    <div class="loading-head">
      <div class="spinner"></div>
      <div>
        <h2 id="loadingTitle">正在分析…</h2>
        <p id="loadingStage">准备数据</p>
      </div>
      <div class="loading-timer" id="loadingTimer">0.0s</div>
    </div>
    <p class="loading-tip">首次分析约 5~10 秒（行情 + 三大报表 + 板块 + 同业对比）</p>
  </section>

  <!-- 错误 -->
  <section id="errorState" class="error-box" hidden>
    <h2>分析失败</h2>
    <p id="errorMsg"></p>
    <button id="errorRetry" class="btn-primary" type="button">重新分析</button>
  </section>

  <!-- 分析结果 -->
  <section id="result" hidden>
    <div id="backBar" class="back-bar" hidden>
      <button id="backBtn" class="btn-ghost" type="button">← 返回市场全景</button>
      <button id="expandAll" class="btn-ghost" type="button">展开全部</button>
    </div>

    <div class="quote-card" id="quoteCard"></div>
    <div class="facts" id="keyFacts"></div>

    <div class="grid-2">
      <section class="card" id="sec-score"></section>
      <section class="card" id="sec-narrative"></section>
    </div>
    <section class="card" id="sec-fundamentals"></section>
    <section class="card" id="sec-trends"></section>
    <section class="card" id="sec-dupont"></section>
    <section class="card" id="sec-performance"></section>
    <section class="card" id="sec-moat"></section>
    <section class="card" id="sec-industry"></section>
    <div class="grid-2">
      <section class="card" id="sec-valuation"></section>
      <section class="card" id="sec-capital"></section>
    </div>
    <section class="card" id="sec-popularity"></section>
    <section class="card" id="sec-recent5"></section>
    <section class="card" id="sec-tech"></section>
    <section class="card" id="sec-dividend"></section>
    <section class="card" id="sec-risk"></section>
    <section class="card" id="sec-peers"></section>
    <footer class="footer" id="footer"></footer>
  </section>

</main>

<script src="/stock.js"></script>

<div class="settings-mask" id="settingsMask" hidden>
  <div class="settings-sheet" role="dialog" aria-label="设置">
    <h3>设置</h3>
    <p class="sub">偏好保存在本机浏览器，三个页面共用。</p>
    <div class="settings-row">
      <div>
        <div class="lbl">界面主题</div>
        <div class="hint">深色适合盯盘，浅色适合白天</div>
      </div>
      <div class="seg" id="themeSeg">
        <button type="button" data-theme="light">浅色</button>
        <button type="button" data-theme="dark">深色</button>
      </div>
    </div>
    <div class="settings-foot"><button class="btn-ghost" id="settingsClose" type="button">关闭</button></div>
  </div>
</div>

<script src="/theme.js"></script>
</body>
</html>
"""

CSS = r"""/* ============================================================
   大A小散 · 视觉系统 v2（统一设计语言）
   令牌 → 布局 → 组件 → 图表 → 市场全景 → 响应式
   规范：中性深色底 / 单一蓝色主色 / 语义涨跌色 / 8pt 间距 / 18px 卡片圆角
   ============================================================ */

/* ---------------- 1. 设计令牌 ---------------- */
:root {
  /* 表面层级：底 → 卡片 → 嵌套块 → 交互态 */
  --bg: #f3f6fb;
  --bg-soft: #eaf0f9;
  --panel: #ffffff;
  --panel-2: #f7f9fd;
  --panel-3: #e9eff8;

  /* 描边：全部为低对比发丝线 */
  --line: #dbe3ef;
  --line-soft: #e8eef7;

  /* 文本：三级灰阶 */
  --text: #12233a;
  --text-dim: #52637a;
  --text-mute: #7d8ca1;

  /* 主色：单一蓝，仅用于强调与交互 */
  --accent: #2563eb;
  --accent-2: #3b82f6;
  --accent-weak: rgba(37, 99, 235, .12);

  /* 语义色：红涨绿跌（A 股习惯） */
  --up: #e11d33;
  --down: #0d9b6c;
  --good: #0d9b6c;
  --bad: #e11d33;
  --warn: #c77700;

  /* 圆角 / 阴影 / 字体 */
  --radius-lg: 18px;
  --radius: 18px;
  --radius-sm: 12px;
  --radius-xs: 10px;
  --shadow: 0 18px 40px -28px rgba(15, 32, 51, .16);
  /* 图表配色（跟随浅色/深色主题） */
  --chart-grid: #e3e9f2;
  --chart-zero: #dbe3ef;
  --chart-axis: #8b98ab;
  --chart-ink: #143049;
  --mono: ui-monospace, "SF Mono", "Roboto Mono", "Droid Sans Mono", Menlo, Consolas, monospace;
  --font: -apple-system, "SF Pro Text", "PingFang SC", "HarmonyOS Sans SC", "MiSans",
          "Noto Sans SC", "Microsoft YaHei", system-ui, sans-serif;
}

* { box-sizing: border-box; }

/* 关键：显式覆盖 UA 的 [hidden]，避免被 display 声明抵消 */
[hidden] { display: none !important; }

html, body {
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font);
  font-size: 14px;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
  -webkit-text-size-adjust: 100%;
  min-height: 100vh;
}

/* 顶部极淡的光晕，只做层次，不抢内容 */
body::before {
  content: "";
  position: fixed;
  inset: 0 0 auto 0;
  height: 320px;
  background: radial-gradient(120% 100% at 50% 0%, rgba(37, 99, 235, .10) 0%, transparent 62%);
  pointer-events: none;
  z-index: 0;
}

html { scroll-behavior: smooth; --topbar-h: 108px; }

h1, h2, h3, h4 { margin: 0; font-weight: 600; letter-spacing: -.1px; }
p { margin: 0; }
a { color: inherit; text-decoration: none; }
button { font-family: inherit; -webkit-tap-highlight-color: transparent; }
input { -webkit-tap-highlight-color: transparent; }

/* ---------------- 2. 顶部应用栏 ---------------- */
.appbar {
  position: sticky;
  top: 0;
  z-index: 60;
  padding: 12px 16px 10px;
  background: rgba(255, 255, 255, .92);
  -webkit-backdrop-filter: saturate(160%) blur(20px);
  backdrop-filter: saturate(160%) blur(20px);
  border-bottom: 1px solid var(--line-soft);
}

/* 右上角是安卓原生设置按钮（40dp + 8dp 边距），右侧留白避免遮挡 */
.appbar-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding-right: 50px;
}

.brand { display: flex; align-items: center; gap: 10px; min-width: 0; }

.brand .logo {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  flex: none;
  background: linear-gradient(160deg, #ccdcf5, #eef3fb);
  border: 1px solid #ccd9ee;
  box-shadow: inset 0 1px 0 rgba(15, 32, 51, .06);
}

.brand-text h1 {
  font-size: 17px;
  font-weight: 650;
  letter-spacing: .2px;
  white-space: nowrap;
  line-height: 1.25;
}

.brand-text .status-line {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 2px;
  font-size: 10.5px;
  color: var(--text-mute);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 220px;
}

.brand-text .dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  flex: none;
  background: var(--good);
  box-shadow: 0 0 0 2px rgba(13, 155, 108, .16);
}
.brand-text .dot.busy {
  background: var(--warn);
  box-shadow: 0 0 0 2px rgba(199, 119, 0, .16);
  animation: pulse 1.4s infinite;
}
@keyframes pulse { 50% { opacity: .35; } }

/* 二级导航：分段控件（与妖股雷达页一致） */
.appnav {
  display: flex;
  gap: 2px;
  margin-top: 12px;
  padding: 3px;
  background: var(--bg-soft);
  border: 1px solid var(--line-soft);
  border-radius: 13px;
}

.nav-btn {
  flex: 1;
  text-align: center;
  padding: 8px 0;
  border: 1px solid transparent;
  border-radius: 10px;
  font-size: 13px;
  line-height: 1.2;
  color: var(--text-dim);
  background: transparent;
  white-space: nowrap;
  transition: color .15s, background .15s;
}

.nav-btn.on {
  color: #1d4ed8;
  font-weight: 650;
  background: linear-gradient(180deg, rgba(37, 99, 235, .14), rgba(37, 99, 235, .05));
  border-color: rgba(37, 99, 235, .34);
  box-shadow: 0 2px 10px -6px rgba(37, 99, 235, .5), inset 0 1px 0 rgba(255, 255, 255, .7);
}

.nav-btn:active { transform: scale(.98); }

/* ---------------- 3. 搜索 ---------------- */
.search-box {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  padding: 5px 5px 5px 12px;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 14px;
  transition: border-color .18s, box-shadow .18s;
}

.search-box:focus-within {
  border-color: #c3d5ee;
  box-shadow: 0 0 0 3px var(--accent-weak);
}

.search-icon { color: var(--text-mute); flex: none; }

#searchInput {
  flex: 1;
  min-width: 0;
  padding: 8px 0;
  background: none;
  border: none;
  outline: none;
  color: var(--text);
  font-size: 16px; /* iOS / WebView 防缩放 */
  -webkit-appearance: none;
}
#searchInput::placeholder { color: #8b98ab; }
#searchInput::-webkit-search-cancel-button { -webkit-appearance: none; }

.btn-primary {
  border: none;
  cursor: pointer;
  padding: 9px 18px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 650;
  letter-spacing: .3px;
  color: #e8eef8;
  background: var(--accent);
  transition: filter .15s, transform .12s;
  white-space: nowrap;
}
.btn-primary:active { transform: scale(.97); filter: brightness(.95); }

.suggest {
  position: absolute;
  left: 0;
  right: 0;
  top: calc(100% + 8px);
  z-index: 70;
  max-height: 320px;
  overflow-y: auto;
  background: var(--panel-2);
  border: 1px solid var(--line);
  border-radius: 14px;
  box-shadow: 0 24px 48px -24px rgba(15, 32, 51, .16);
  -webkit-overflow-scrolling: touch;
}

.suggest-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 14px;
  cursor: pointer;
  border-bottom: 1px solid var(--line-soft);
}
.suggest-item:last-child { border-bottom: none; }
.suggest-item:active,
.suggest-item.active { background: var(--panel-3); }
.suggest-item .nm { font-size: 13.5px; }
.suggest-item .cd { margin-left: auto; font-family: var(--mono); font-size: 11.5px; color: var(--text-mute); }

/* ---------------- 4. 按钮 / 标签 ---------------- */
.btn-ghost {
  border: 1px solid var(--line);
  background: var(--panel-2);
  color: var(--text-dim);
  font-size: 12.5px;
  padding: 8px 14px;
  border-radius: 11px;
  cursor: pointer;
  transition: color .15s, border-color .15s, background .15s;
}
.btn-ghost:active { color: var(--text); border-color: #c3d5ee; background: var(--panel-3); }

.chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 11px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: var(--panel-2);
  color: var(--text-dim);
  font-size: 11.5px;
  line-height: 1.5;
  cursor: pointer;
  transition: all .15s;
}
.chip:active { background: var(--panel-3); }
.chip:hover { color: var(--text); }

.tag {
  display: inline-block;
  padding: 2px 9px;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: var(--panel-2);
  color: var(--text-dim);
  font-size: 11px;
  line-height: 1.6;
  white-space: nowrap;
}
.tag.accent { color: var(--accent-2); border-color: rgba(37, 99, 235, .32); background: var(--accent-weak); }
.tag.warn { color: var(--warn); border-color: rgba(199, 119, 0, .32); background: rgba(199, 119, 0, .1); }

.quick-chips { display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap; }

/* ---------------- 5. 主体 / 卡片 ---------------- */
main {
  position: relative;
  z-index: 1;
  max-width: 100%;
  margin: 0 auto;
  padding: 12px 12px calc(40px + env(safe-area-inset-bottom));
}

.card {
  background: var(--panel);
  border: 1px solid var(--line-soft);
  border-radius: var(--radius);
  padding: 16px;
  margin-bottom: 12px;
  scroll-margin-top: 0;
}

.card > h2 {
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 2px;
}

/* 章节标识：3px 主色竖条 */
.card > h2::before {
  content: "";
  width: 3px;
  height: 14px;
  border-radius: 2px;
  flex: none;
  background: linear-gradient(180deg, var(--accent), rgba(37, 99, 235, .35));
}

.card .sub {
  margin: 6px 0 14px 12px;
  font-size: 11.5px;
  line-height: 1.65;
  color: var(--text-mute);
}

.grid-2 { display: grid; grid-template-columns: 1fr; gap: 12px; }

.section-head { display: flex; align-items: baseline; gap: 10px; margin-bottom: 12px; }
.section-head h3 { font-size: 14px; }
.hint { font-size: 11.5px; color: var(--text-mute); }

/* ---------------- 6. 加载 / 错误 / 空态 ---------------- */
.loading {
  display: block;
  padding: 48px 18px;
  text-align: center;
}

.loading-head {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  text-align: left;
}

.loading-head h2 { font-size: 15.5px; }
.loading-head p { margin-top: 3px; font-size: 12.5px; color: var(--accent-2); }

.loading-timer {
  font-family: var(--mono);
  font-size: 12.5px;
  color: var(--text-mute);
  margin-left: 6px;
}

.loading-tip {
  margin-top: 18px;
  font-size: 11.5px;
  line-height: 1.75;
  color: var(--text-mute);
}

.spinner {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  flex: none;
  border: 2.5px solid #dbe3ef;
  border-top-color: var(--accent);
  animation: spin .85s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.stage-list { list-style: none; padding: 0; margin: 0 0 22px; display: flex; flex-wrap: wrap; gap: 8px; }
.stage-list li { font-size: 12px; color: var(--text-dim); background: var(--panel-2); border: 1px solid var(--line-soft); border-radius: 999px; padding: 5px 12px; }
.stage-list li.done { color: var(--good); border-color: rgba(13, 155, 108, .3); }
.stage-list li.active { color: var(--accent-2); border-color: rgba(37, 99, 235, .45); background: var(--accent-weak); }

.skeleton { display: grid; gap: 12px; }
.sk-block {
  height: 110px;
  border-radius: var(--radius);
  background: linear-gradient(100deg, #f4f7fc 30%, #eef3fb 50%, #f4f7fc 70%);
  background-size: 220% 100%;
  animation: shimmer 1.4s infinite;
}
.sk-hero { height: 140px; }
.sk-tall { height: 300px; }
.sk-row { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
@keyframes shimmer { to { background-position: -220% 0; } }

.error-box { text-align: center; padding: 56px 18px; }
.error-box h2 { font-size: 17px; color: var(--bad); }
.error-box p { margin: 10px auto 20px; max-width: 300px; font-size: 12.5px; line-height: 1.7; color: var(--text-dim); }

.empty-hero { text-align: center; padding: 48px 18px 34px; }
.empty-hero h2 { font-size: 22px; letter-spacing: -.3px; }
.empty-hero p { margin: 10px auto 0; max-width: 620px; font-size: 13px; line-height: 1.75; color: var(--text-dim); }

.badge-note {
  margin-top: 12px;
  padding: 10px 12px;
  border: 1px dashed var(--line);
  border-radius: 11px;
  font-size: 11px;
  line-height: 1.7;
  color: var(--text-mute);
}
.warn-note { border-color: rgba(199, 119, 0, .3); color: #8a6300; }

/* ---------------- 7. 行情卡 ---------------- */
.quote-card {
  position: relative;
  overflow: hidden;
  padding: 18px 16px 14px;
  margin-bottom: 12px;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background:
    radial-gradient(120% 120% at 100% 0%, rgba(37, 99, 235, .10) 0%, transparent 55%),
    linear-gradient(180deg, #eef3fb, #eef3fb);
  box-shadow: var(--shadow);
}

.qc-top { display: flex; align-items: flex-start; gap: 10px; }
.qc-name { font-size: 20px; font-weight: 700; letter-spacing: .2px; }
.qc-code { margin-left: 8px; font-family: var(--mono); font-size: 11.5px; color: var(--text-mute); }
.qc-tags { display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap; }

.qc-price { margin-left: auto; text-align: right; flex: none; }
.qc-price .p { font-family: var(--mono); font-size: 28px; font-weight: 700; line-height: 1.05; letter-spacing: -.5px; }
.qc-price .chg { margin-top: 6px; font-family: var(--mono); font-size: 12.5px; }

.up { color: var(--up); }
.down { color: var(--down); }
.flat { color: var(--text-dim); }

/* 行情卡数据格：flex 让末行自动铺满，不留空洞 */
.qc-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 1px;
  margin-top: 16px;
  overflow: hidden;
  border-radius: 14px;
  background: var(--line-soft);
}
.qc-stat { flex: 1 1 100px; padding: 9px 11px; background: #eef3fb; }
.qc-stat .k { font-size: 11px; color: var(--text-mute); }
.qc-stat .v { margin-top: 4px; font-family: var(--mono); font-size: 13px; color: var(--text); white-space: nowrap; }

/* 速览卡 */
.facts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-bottom: 12px;
}
.fact {
  padding: 11px 13px;
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-sm);
  background: var(--panel);
}
.fact .fl { font-size: 11px; color: var(--text-mute); }
.fact .fv { margin-top: 5px; font-family: var(--mono); font-size: 13px; line-height: 1.5; color: var(--text); }
.fact .fn { margin-top: 4px; font-size: 11px; line-height: 1.55; color: var(--text-mute); }

/* ---------------- 8. 评分 ---------------- */
.score-top { display: flex; flex-direction: column; align-items: flex-start; gap: 14px; margin: 8px 0 18px; }

.score-ring { position: relative; width: 112px; height: 112px; flex: none; }
.score-ring svg { width: 112px; height: 112px; display: block; }
.score-ring .num { position: absolute; inset: 0; font-family: var(--mono); font-weight: 700; }
.score-ring .num .val {
  position: absolute; left: 0; right: 0; top: 50%;
  transform: translateY(-50%);
  text-align: center; font-size: 29px; line-height: 1;
}
.score-ring .num small {
  position: absolute; left: 0; right: 0; top: 50%;
  margin-top: 15px;
  text-align: center; font-size: 10.5px; line-height: 1;
  color: var(--text-mute); font-weight: 500;
}

.score-meta .grade { font-size: 14px; color: var(--text); }
.score-meta .grade-sub { margin-top: 6px; font-size: 11.5px; line-height: 1.7; color: var(--text-mute); }

.bars { display: grid; gap: 10px; }
.bar-row { display: grid; grid-template-columns: 84px minmax(0, 1fr) 46px; align-items: center; gap: 10px; }
.bar-row .lb { font-size: 12px; color: var(--text-dim); }
.bar-row .vv { font-family: var(--mono); font-size: 12px; text-align: right; color: var(--text); }
.bar-track { height: 6px; border-radius: 999px; background: #e4eaf4; overflow: hidden; }
.bar-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
  transition: width .6s cubic-bezier(.22, 1, .36, 1);
}

/* ---------------- 9. 表格 ---------------- */
.table-wrap {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-sm);
  background: var(--bg-soft);
}

table { width: 100%; border-collapse: collapse; font-size: 12px; }
thead th {
  position: sticky;
  top: 0;
  z-index: 1;
  padding: 9px 10px;
  text-align: right;
  font-weight: 500;
  font-size: 11px;
  color: var(--text-mute);
  white-space: nowrap;
  background: #f4f7fc;
  border-bottom: 1px solid var(--line);
}
thead th:first-child { text-align: left; }
tbody td {
  padding: 9px 10px;
  text-align: right;
  white-space: nowrap;
  font-family: var(--mono);
  font-variant-numeric: tabular-nums;
  color: var(--text);
  border-bottom: 1px solid var(--line-soft);
}
tbody td:first-child { text-align: left; font-family: inherit; color: var(--text-dim); }
tbody tr:last-child td { border-bottom: none; }
tbody tr:active td { background: var(--panel-3); }

td.strong { color: var(--accent-2); font-weight: 600; }
tr.self-row td { background: rgba(37, 99, 235, .08) !important; }

/* ---------------- 10. 图表 / 图例 ---------------- */
.chart { width: 100%; height: auto; display: block; }
.chart text { font-family: var(--mono); font-size: 10.5px; fill: var(--text-mute); }

.chart-box { margin-top: 14px; }
.chart-title { margin: 0 0 8px; font-size: 12.5px; color: var(--text); }

.legend { display: flex; gap: 14px; flex-wrap: wrap; margin-top: 10px; font-size: 11px; color: var(--text-mute); }
.legend i { display: inline-block; width: 9px; height: 9px; border-radius: 3px; margin-right: 5px; vertical-align: -1px; }

.mini-legend { display: flex; gap: 14px; flex-wrap: wrap; margin-top: 8px; font-size: 11px; color: var(--text-mute); }
.mini-legend i { display: inline-block; width: 14px; height: 3px; border-radius: 2px; margin-right: 5px; vertical-align: 3px; }

/* ---------------- 11. 列表 / 内容块 ---------------- */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(132px, 1fr)); gap: 8px; }
.kpi {
  padding: 11px 12px;
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-sm);
  background: var(--panel-2);
}
.kpi .k { font-size: 11px; color: var(--text-mute); }
.kpi .v { margin-top: 5px; font-family: var(--mono); font-size: 15px; color: var(--text); }
.kpi .s { margin-top: 3px; font-size: 10.5px; color: var(--text-mute); }
.kpi.good { border-color: rgba(13, 155, 108, .26); }
.kpi.warn { border-color: rgba(199, 119, 0, .26); }
.kpi.bad { border-color: rgba(225, 29, 51, .26); }

.tag-cloud { display: flex; flex-wrap: wrap; gap: 6px; }
.tag-cloud .tag { cursor: default; }
.sector-item { display: flex; align-items: center; gap: 8px; }
.sector-item .pct { font-family: var(--mono); font-size: 12px; }

.moat-list { display: grid; gap: 8px; }
.moat-item {
  display: grid;
  grid-template-columns: 24px minmax(0, 1fr);
  gap: 10px;
  padding: 12px 13px;
  border: 1px solid var(--line-soft);
  border-left: 2px solid var(--line);
  border-radius: var(--radius-sm);
  background: var(--panel-2);
}
.moat-item.lv-强 { border-left-color: var(--good); }
.moat-item.lv-偏强 { border-left-color: #0d9b6c; }
.moat-item.lv-持平 { border-left-color: #9aa9bd; }
.moat-item.lv-偏弱 { border-left-color: var(--warn); }
.moat-item.lv-弱 { border-left-color: var(--bad); }
.moat-item .idx { font-family: var(--mono); font-size: 11.5px; color: var(--text-mute); padding-top: 2px; }
.moat-item .ttl { display: flex; align-items: center; gap: 7px; flex-wrap: wrap; font-size: 13px; font-weight: 600; }
.moat-item .metric { font-family: var(--mono); font-size: 12px; color: var(--accent-2); }
.moat-item .ev { margin-top: 5px; font-size: 12px; line-height: 1.65; color: var(--text-dim); }

.lv-badge { font-size: 10.5px; padding: 1px 8px; border-radius: 7px; border: 1px solid currentColor; }
.lv-badge.s-强 { color: var(--good); }
.lv-badge.s-偏强 { color: #0d9b6c; }
.lv-badge.s-持平 { color: var(--text-mute); }
.lv-badge.s-偏弱 { color: var(--warn); }
.lv-badge.s-弱 { color: var(--bad); }
.lv-badge.s-信息 { color: var(--accent-2); }

.narr h3 { margin: 16px 0 8px; font-size: 13px; color: var(--text); }
.narr h3:first-child { margin-top: 0; }
.narr ul { margin: 0; padding-left: 16px; }
.narr li { font-size: 12.5px; line-height: 1.8; color: var(--text-dim); }
.narr li::marker { color: var(--accent); }
.narr .headline { font-size: 14px; line-height: 1.65; color: var(--text); }

.concl-list { display: grid; gap: 8px; margin-top: 12px; }
.concl { display: grid; grid-template-columns: 16px minmax(0, 1fr); gap: 8px; font-size: 12.5px; line-height: 1.7; color: var(--text-dim); }
.concl .ic { font-family: var(--mono); font-size: 12px; text-align: center; }
.concl.good .ic { color: var(--good); }
.concl.bad .ic { color: var(--bad); }
.concl.flat .ic { color: var(--text-mute); }

.dupont-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 8px; }
.dupont-card { padding: 12px 13px; border: 1px solid var(--line-soft); border-radius: var(--radius-sm); background: var(--panel-2); }
.dupont-card .dl { font-size: 11.5px; color: var(--text-mute); }
.dupont-card .dv { margin: 6px 0 5px; font-family: var(--mono); font-size: 18px; color: var(--text); }
.dupont-card .dd { font-size: 11px; line-height: 1.6; color: var(--text-mute); }
.dupont-eq { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 12px; font-family: var(--mono); font-size: 12px; color: var(--text-dim); }
.dupont-eq b { color: var(--accent-2); font-weight: 600; }

.risk-summary { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
.risk-pill { padding: 6px 12px; border-radius: 999px; border: 1px solid var(--line); background: var(--panel-2); font-size: 11.5px; }
.risk-pill.alert { color: var(--bad); border-color: rgba(225, 29, 51, .38); background: rgba(225, 29, 51, .1); }
.risk-pill.watch { color: var(--warn); border-color: rgba(199, 119, 0, .38); background: rgba(199, 119, 0, .1); }
.risk-pill.ok { color: var(--good); border-color: rgba(13, 155, 108, .34); background: rgba(13, 155, 108, .08); }

.st { display: inline-block; padding: 1px 8px; border-radius: 7px; border: 1px solid currentColor; font-size: 10.5px; }
.st.alert { color: var(--bad); }
.st.watch { color: var(--warn); }
.st.ok { color: var(--good); }

/* ---------------- 12. 相似股 ---------------- */
.peer-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }
.peer-card {
  position: relative;
  overflow: hidden;
  padding: 13px 14px;
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-sm);
  background: var(--panel-2);
  cursor: pointer;
  transition: border-color .15s, transform .15s;
}
.peer-card:active { border-color: #c3d5ee; transform: scale(.995); }
.peer-card .rank {
  position: absolute; top: 0; right: 0;
  padding: 2px 8px;
  font-family: var(--mono); font-size: 10px;
  color: var(--text-mute);
  background: #e4eaf4;
  border-bottom-left-radius: 9px;
}
.peer-card .pn { font-size: 14.5px; font-weight: 650; }
.peer-card .pc { margin-top: 2px; font-family: var(--mono); font-size: 11px; color: var(--text-mute); }
.peer-card .sim { display: flex; align-items: center; gap: 8px; margin: 11px 0 9px; }
.peer-card .sim .track { flex: 1; height: 4px; border-radius: 999px; background: #e4eaf4; overflow: hidden; }
.peer-card .sim .fill { height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent-2)); }
.peer-card .sim .val { font-family: var(--mono); font-size: 12px; color: var(--accent-2); }
.peer-card .pm { display: flex; gap: 12px; flex-wrap: wrap; font-family: var(--mono); font-size: 11.5px; color: var(--text-dim); }
.peer-card .rs { display: grid; gap: 3px; margin-top: 9px; }
.peer-card .rs span { font-size: 11px; line-height: 1.5; color: var(--text-mute); }
.peer-card .dims { display: grid; gap: 5px; margin-top: 9px; }
.peer-card .dim { display: grid; grid-template-columns: 50px minmax(0, 1fr) 28px; align-items: center; gap: 6px; }
.peer-card .dim .dl2 { font-size: 10px; color: var(--text-mute); }
.peer-card .dim .dt2 { height: 3px; border-radius: 999px; background: #e4eaf4; overflow: hidden; }
.peer-card .dim .dt2 i { display: block; height: 100%; border-radius: 999px; background: linear-gradient(90deg, #b7cbe8, var(--accent-2)); }
.peer-card .dim .dv2 { font-family: var(--mono); font-size: 10px; text-align: right; color: var(--text-dim); }

/* ---------------- 13. 页脚 ---------------- */
.footer {
  margin-top: 18px;
  padding: 16px 4px 8px;
  border-top: 1px solid var(--line-soft);
  font-size: 11px;
  line-height: 1.85;
  color: var(--text-mute);
}
.footer b { color: var(--text-dim); font-weight: 500; }

/* ---------------- 14. 首页：市场全景 ---------------- */
.market { display: block; }

.mk-skeleton { padding: 36px 12px; text-align: center; font-size: 12.5px; color: var(--text-mute); }

.mk-hero {
  padding: 15px 16px 16px;
  margin-bottom: 12px;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background:
    radial-gradient(120% 120% at 100% 0%, rgba(37, 99, 235, .08) 0%, transparent 55%),
    var(--panel);
  box-shadow: var(--shadow);
}

.mk-hero-top { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 14px; }
.mk-title { font-size: 14.5px; font-weight: 600; }
.mk-date { font-size: 11px; color: var(--text-mute); }

.mk-refresh {
  margin-left: auto;
  padding: 5px 12px;
  border: 1px solid var(--line);
  border-radius: 9px;
  background: var(--panel-2);
  color: var(--text-dim);
  font-size: 11.5px;
  cursor: pointer;
}
.mk-refresh:active { color: var(--text); border-color: #c3d5ee; }

.mk-hero-body { display: grid; grid-template-columns: minmax(0, 1fr); gap: 16px; align-items: stretch; }

.mk-breadth .bk-num { font-family: var(--mono); font-size: 22px; font-weight: 700; letter-spacing: -.5px; }
.mk-breadth .bk-num .up { color: var(--up); }
.mk-breadth .bk-num .down { color: var(--down); }
.mk-breadth .bk-sub { margin-top: 5px; font-size: 11px; color: var(--text-mute); }
.mk-breadth .bk-bar {
  display: flex;
  height: 6px;
  margin-top: 11px;
  overflow: hidden;
  border-radius: 999px;
  background: #e4eaf4;
}
.mk-breadth .bk-bar i { display: block; height: 100%; }
.mk-breadth .bk-bar .u { background: var(--up); }
.mk-breadth .bk-bar .f { background: #a9b6c9; }
.mk-breadth .bk-bar .d { background: var(--down); }

/* 涨跌分布：柱状 */
.mk-dist { display: flex; align-items: flex-end; gap: 4px; height: 104px; }
.mk-dist .col { flex: 1; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; gap: 4px; height: 100%; min-width: 0; }
.mk-dist .col .cnt { font-family: var(--mono); font-size: 10px; color: var(--text-mute); }
.mk-dist .col .bar { width: 100%; border-radius: 4px; min-height: 2px; }
.mk-dist .col .lb { font-size: 9px; color: var(--text-mute); white-space: nowrap; transform: scale(.9); }

.mk-kpis { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.mk-kpi { padding: 10px 11px; border: 1px solid var(--line-soft); border-radius: var(--radius-sm); background: var(--panel-2); }
.mk-kpi .k { font-size: 10.5px; color: var(--text-mute); }
.mk-kpi .v { margin-top: 4px; font-family: var(--mono); font-size: 14px; color: var(--text); }
.mk-kpi .s { margin-top: 2px; font-size: 10px; color: var(--text-mute); }

.mk-row { display: grid; gap: 12px; margin-bottom: 12px; align-items: start; }
.mk-row-2 { grid-template-columns: minmax(0, 1fr); }
.mk-row .card { margin-bottom: 0; }
.mk-stack { display: grid; gap: 12px; align-content: start; }

.mk-tabs { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
.mk-tab {
  padding: 5px 11px;
  border: 1px solid var(--line);
  border-radius: 9px;
  background: var(--panel-2);
  color: var(--text-dim);
  font-size: 11.5px;
  cursor: pointer;
  transition: all .15s;
}
.mk-tab.on {
  color: var(--accent-2);
  border-color: rgba(37, 99, 235, .45);
  background: var(--accent-weak);
  font-weight: 600;
}

.mk-sector-list { display: grid; gap: 6px; }
.mk-sector {
  display: grid;
  grid-template-columns: 18px minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  padding: 10px 11px;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  background: var(--panel-2);
  cursor: pointer;
  transition: border-color .15s, background .15s;
}
.mk-sector:active { border-color: #c3d5ee; background: var(--panel-3); }
.mk-sector .idx { font-family: var(--mono); font-size: 10.5px; color: var(--text-mute); }
.mk-sector .nm { font-size: 12.5px; font-weight: 600; }
.mk-sector .nm em { font-style: normal; margin-left: 6px; font-size: 10px; font-weight: 400; color: var(--text-mute); }
.mk-sector .lead { margin-top: 2px; font-size: 10.5px; color: var(--text-mute); }
.mk-sector .pct { font-family: var(--mono); font-size: 13px; font-weight: 600; text-align: right; }
.mk-sector .amt { margin-top: 1px; font-family: var(--mono); font-size: 10px; color: var(--text-mute); text-align: right; }

.mk-detail { margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--line-soft); }
.mk-detail-head { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.mk-detail-head h4 { font-size: 12.5px; }
.mk-detail-head .sub { font-size: 11px; color: var(--text-mute); }
.mk-detail .close { margin-left: auto; cursor: pointer; color: var(--text-mute); font-size: 12px; }
.mk-detail .close:active { color: var(--text); }

.mk-tiers { display: grid; gap: 8px; }
.mk-tier { display: grid; grid-template-columns: 56px minmax(0, 1fr) 34px; gap: 9px; align-items: center; }
.mk-tier .tl { font-size: 11.5px; color: var(--text-dim); }
.mk-tier .tb { height: 14px; border-radius: 7px; background: #e4eaf4; overflow: hidden; }
.mk-tier .tb i { display: block; height: 100%; border-radius: 7px; background: linear-gradient(90deg, rgba(225, 29, 51, .55), rgba(225, 29, 51, .95)); }
.mk-tier .tc { font-family: var(--mono); font-size: 12px; text-align: right; color: var(--text); }

.mk-list { display: grid; gap: 4px; }
.mk-item {
  display: grid;
  grid-template-columns: 16px minmax(0, 1fr) auto;
  gap: 8px;
  align-items: center;
  padding: 8px 9px;
  border: 1px solid transparent;
  border-radius: var(--radius-xs);
  background: var(--panel-2);
  cursor: pointer;
  transition: border-color .15s, background .15s;
}
.mk-item:active { border-color: #c3d5ee; background: var(--panel-3); }
.mk-item .r { font-family: var(--mono); font-size: 10px; color: var(--text-mute); }
.mk-item .n { font-size: 12.5px; font-weight: 600; }
.mk-item .t { margin-top: 1px; font-size: 10px; line-height: 1.5; color: var(--text-mute); }
.mk-item .v { font-family: var(--mono); font-size: 12px; text-align: right; }

.mk-hot-grid { display: grid; grid-template-columns: minmax(0, 1fr); gap: 12px; margin-bottom: 12px; }

.mk-foot { padding: 4px 2px 8px; font-size: 11px; line-height: 1.85; color: var(--text-mute); }

/* 返回条 */
.back-bar { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.back-bar .btn-ghost { font-size: 12.5px; padding: 7px 13px; }
.back-hint { font-size: 11px; color: var(--text-mute); }

/* ---------------- 15. 章节折叠 ---------------- */
.card.acc > * { display: block; }
.card.collapsed > *:not(h2) { display: none !important; }

.acc-head {
  position: relative;
  padding-right: 22px;
  cursor: pointer;
  user-select: none;
  -webkit-user-select: none;
}
.acc-head::after {
  content: "";
  position: absolute;
  right: 3px;
  top: 50%;
  width: 7px;
  height: 7px;
  border-right: 1.6px solid var(--text-mute);
  border-bottom: 1.6px solid var(--text-mute);
  transform: translateY(-70%) rotate(45deg);
  transition: transform .18s;
}
.card.collapsed .acc-head::after { transform: translateY(-30%) rotate(-135deg); }

/* ---------------- 16. 响应式（≥720px 桌面预览） ---------------- */
@media (min-width: 720px) {
  main { max-width: 1080px; padding: 20px 20px 80px; }
  .appbar { padding: 14px 24px 12px; }
  .card { padding: 20px 22px; margin-bottom: 16px; }
  .grid-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
  .score-top { flex-direction: row; align-items: center; gap: 22px; }
  .mk-hero { padding: 18px 22px; }
  .mk-hero-body { grid-template-columns: 180px minmax(0, 1fr) 280px; gap: 24px; }
  .mk-row-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .mk-hot-grid { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
  .mk-kpis { grid-template-columns: 1fr 1fr; }
  .qc-name { font-size: 23px; }
  .qc-price .p { font-size: 34px; }
  .mk-dist { height: 118px; }
}

@media (max-width: 380px) {
  .brand-text .status-line { max-width: 140px; }
  .qc-price .p { font-size: 25px; }
  .facts { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .mk-kpis { grid-template-columns: 1fr; }
  .mk-dist { height: 92px; }
}
/* ============================================================
   桌面端版式层（手机端布局一行不改）
   900px+  ：顶部单行三段导航、宽容器、表格/卡片密度提高
   1150px+ ：市场全景与分析结果改两栏
   1600px+ ：市场全景三栏
   ============================================================ */
@media (min-width: 900px) {

  /* ---------------- 顶部：一行三段（品牌 | 导航 | 搜索） ---------------- */
  .appbar {
    display: grid;
    grid-template-columns: 260px auto minmax(280px, 1fr) auto;
    align-items: center;
    justify-content: start;
    gap: 24px;
    padding: 12px 26px;
    min-height: 76px;      /* 与妖股雷达页 .bar 同高，保证导航垂直位置一致 */
  }
  .appbar-top { padding-right: 0; justify-self: start; min-width: 0; }
  .brand .logo { width: 34px; height: 34px; border-radius: 10px; }
  .brand-text h1 { font-size: 17px; }
  .brand-text .status-line { max-width: none; font-size: 11px; }
  .appnav { margin-top: 0; gap: 6px; }
  .nav-btn { flex: none; padding: 7px 20px; border-radius: 8px; font-size: 13px; }
  .nav-btn:active { transform: none; }
  .nav-btn:hover { border-color: #9dbfe8; color: var(--text); }
  .search-box { margin-top: 0; position: relative; width: 100%; max-width: 560px; justify-self: end; }
  #searchInput { font-size: 14px; padding: 6px 0; }
  .suggest { left: 0; right: 0; top: calc(100% + 8px); }
  .suggest-item:active { background: none; }
  .suggest-item:hover { background: #e6eefb; }

  /* ---------------- 主体容器 ---------------- */
  main { max-width: 1400px; margin: 0 auto; padding: 18px 26px 56px; }

  /* ---------------- 卡片与文字密度 ---------------- */
  .card { padding: 16px 18px 18px; }
  .card > h2 { font-size: 15px; }
  .card .sub { font-size: 12px; }
  table { font-size: 12.5px; }
  thead th, tbody td { padding: 8px 11px; }
  tbody tr:hover { background: #eef3fa; }
  .fact { padding: 11px 13px; }
  .facts { grid-template-columns: repeat(auto-fit, minmax(168px, 1fr)); gap: 10px; }

  .quote-card { padding: 18px 22px 16px; }
  .qc-name { font-size: 23px; }
  .qc-price .p { font-size: 34px; }
  .qc-stats { grid-template-columns: repeat(auto-fit, minmax(124px, 1fr)); }
  .qc-stat .v { font-size: 13.5px; }

  .back-bar { margin-bottom: 0; }
  .btn-ghost { flex: none; padding: 8px 18px; }
  .btn-ghost:hover { border-color: #9dbfe8; color: var(--text); }

  /* 两栏区块（评分/解读、估值/资金）在平板上也能并排 */
  .grid-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin-bottom: 0; }
  .grid-2 > .card { margin-bottom: 0; }

  /* ---------------- 市场全景：内部两栏（首屏信息不挤成一条） ---------------- */
  .mk-hero { margin-bottom: 12px; padding: 18px 20px; }
  .mk-hero-top { margin-bottom: 14px; }
  .mk-title { font-size: 15px; }
  .mk-date { font-size: 11.5px; }
  .mk-refresh { font-size: 12px; padding: 6px 12px; }
  .mk-hero-body { grid-template-columns: minmax(0, 1.15fr) minmax(0, .85fr); gap: 22px; }
  .mk-breadth .bk-num { font-size: 26px; }
  .mk-dist { height: 122px; }
  .mk-kpis { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .mk-kpi { padding: 10px 12px; }
  .mk-kpi .v { font-size: 15px; }
  .mk-row-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
  .mk-stack { gap: 16px; }
  .mk-hot-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
  .mk-sector { padding: 11px 12px; }
  .mk-sector:hover, .mk-item:hover { background: #e6eefb; }
  .mk-foot { font-size: 11.5px; line-height: 1.8; }

  /* ---------------- 加载 / 错误 ---------------- */
  .loading { padding: 64px 20px; }
  .error-box { padding: 80px 24px; }
}

/* ============================================================
   1150px+：市场全景 + 分析结果 两栏
   ============================================================ */
@media (min-width: 1150px) {

  #marketView {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
    align-items: start;
  }
  #marketView > .mk-hero,
  #marketView > .mk-hot-grid,
  #marketView > .mk-foot { grid-column: 1 / -1; }
  #marketView > .card { margin-bottom: 0; }
  .mk-hero { margin-bottom: 0; }
  .mk-hot-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }

  #result {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
    align-items: stretch;   /* 同一行卡片等高，避免内容不一导致的下方留白 */
  }
  #result > .card,
  #result > .grid-2 > .card { margin-bottom: 0; height: 100%; display: flex; flex-direction: column; }
  /* 需要整行宽度的模块：宽表格 / 多图 / 矩阵 */
  #result > #backBar,
  #result > #quoteCard,
  #result > #keyFacts,
  #result > #sec-trends,
  #result > #sec-fundamentals,
  #result > #sec-recent5,
  #result > #sec-peers,
  #result > #sec-risk,
  #result > .grid-2,
  #result > #footer { grid-column: 1 / -1; }
}

/* ============================================================
   1600px+：再加一栏，超宽屏塞满
   ============================================================ */
@media (min-width: 1600px) {
  main { max-width: 1640px; }
  #marketView { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  #marketView > .mk-hero,
  #marketView > .mk-hot-grid,
  #marketView > .mk-foot { grid-column: 1 / -1; }
}
/* ============================================================
   章节序号层：个股分析页 16 个章节按文档顺序自动编号
   （与复盘页的「1 / 2 / 2.5 …」编号视觉保持一致）
   ============================================================ */
#result {
  counter-reset: sec;
}

#result > .card,
#result > .grid-2 > .card {
  counter-increment: sec;
}

#result .card > h2::before {
  content: counter(sec) ".";
  color: var(--accent-2);
  font: 700 11px/1 var(--mono);
  margin-right: 6px;
  vertical-align: 2px;
}

/* ---------------- 设置入口（顶栏 ⚙）与设置面板 ---------------- */
.icon-btn {
  display: none;
  width: 38px;
  height: 38px;
  place-items: center;
  border-radius: 10px;
  border: 1px solid var(--line);
  background: var(--panel-2);
  color: var(--text-dim);
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  transition: color .15s, border-color .15s, background .15s;
}
.icon-btn:hover { color: var(--accent); border-color: var(--accent); }

.settings-mask {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(15, 32, 51, .38);
  -webkit-backdrop-filter: blur(2px);
  backdrop-filter: blur(2px);
}
.settings-mask[hidden] { display: none; }
.settings-sheet {
  width: min(420px, 100%);
  padding: 18px 18px 16px;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 16px;
  box-shadow: 0 30px 70px -40px rgba(15, 32, 51, .6);
}
.settings-sheet h3 { margin: 0 0 4px; font-size: 15px; }
.settings-sheet .sub { margin: 0 0 12px; font-size: 11.5px; color: var(--text-mute); }
.settings-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 0 4px;
  border-top: 1px solid var(--line-soft);
}
.settings-row .lbl { font-size: 13px; color: var(--text); }
.settings-row .hint { margin-top: 2px; font-size: 11px; color: var(--text-mute); }
.seg {
  display: inline-flex;
  gap: 4px;
  padding: 3px;
  border-radius: 10px;
  background: var(--bg-soft);
  border: 1px solid var(--line-soft);
}
.seg button {
  padding: 6px 14px;
  border: 1px solid transparent;
  border-radius: 8px;
  background: transparent;
  color: var(--text-dim);
  font-size: 12.5px;
  cursor: pointer;
  transition: color .15s, background .15s, border-color .15s;
}
.seg button.on {
  color: #1d4ed8;
  font-weight: 650;
  background: linear-gradient(180deg, rgba(37, 99, 235, .14), rgba(37, 99, 235, .05));
  border-color: rgba(37, 99, 235, .34);
}
.settings-foot { display: flex; justify-content: flex-end; margin-top: 14px; }
@media (min-width: 900px) {
  .icon-btn { display: grid; }
}
"""

JS = r"""(function () {
  'use strict';

  const $ = (s) => document.querySelector(s);
  const el = (id) => document.getElementById(id);

  // 后端错误既可能是字符串（Python 版），也可能是 { message }（Node 版），统一取出可读文本
  function errText(payload, fallback) {
    const e = payload && payload.error;
    if (!e) return fallback;
    if (typeof e === 'string') return e;
    return e.message || e.detail || fallback;
  }


  // 图表配色跟随主题：颜色取自 CSS 变量（stock.css / stock-dark.css 各定义一套）
  const cv = (name, fb) => {
    try {
      const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
      return v || fb;
    } catch (e) {
      return fb;
    }
  };

  const state = {
    data: null,
    market: null,
    loading: false,
    query: '',
    sectorKind: 'l1',
    sectorSort: 'change',
    sectorOpen: null,
    suggestIndex: -1,
    suggestItems: [],
  };

  /* ------------------------------ 格式化 ------------------------------ */
  const isNum = (v) => typeof v === 'number' && Number.isFinite(v);
  const n = (v, d = 2) => (isNum(v) ? v.toFixed(d) : '—');
  const pct = (v, d = 2) => (isNum(v) ? `${v > 0 ? '+' : ''}${v.toFixed(d)}%` : '—');
  const plainPct = (v, d = 2) => (isNum(v) ? `${v.toFixed(d)}%` : '—');
  const cls = (v) => (!isNum(v) ? 'flat' : v > 0 ? 'up' : v < 0 ? 'down' : 'flat');
  const money = (v) => {
    if (!isNum(v)) return '—';
    const a = Math.abs(v);
    if (a >= 1e12) return `${(v / 1e12).toFixed(2)}万亿`;
    if (a >= 1e8) return `${(v / 1e8).toFixed(2)}亿`;
    if (a >= 1e4) return `${(v / 1e4).toFixed(2)}万`;
    return v.toFixed(2);
  };
  const vol = (v) => {
    if (!isNum(v)) return '—';
    const a = Math.abs(v);
    if (a >= 1e8) return `${(v / 1e8).toFixed(2)}亿股`;
    if (a >= 1e4) return `${(v / 1e4).toFixed(2)}万股`;
    return `${v.toFixed(0)}股`;
  };
  const sharesFmt = (v) => {
    if (!isNum(v)) return '—';
    if (Math.abs(v) >= 1e8) return `${(v / 1e8).toFixed(2)} 亿股`;
    if (Math.abs(v) >= 1e4) return `${(v / 1e4).toFixed(2)} 万股`;
    return `${v.toFixed(0)} 股`;
  };
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const levelClass = (lv) => `s-${String(lv || '信息')}`;

  function kpi(k, v, s, variant = '') {
    return `<div class="kpi ${variant}"><div class="k">${esc(k)}</div><div class="v">${v}</div>${s ? `<div class="s">${s}</div>` : ''}</div>`;
  }
  function cardTitle(t, sub) {
    return `<h2>${esc(t)}</h2>${sub ? `<p class="sub">${sub}</p>` : ''}`;
  }

  /* ------------------------------ SVG 图 ------------------------------ */
  function candleChart(candles, opts = {}) {
    if (!candles || candles.length < 2) return '<p class="badge-note">日线数据不足，无法绘制。</p>';
    const W = 400;
    const H = opts.height || 250;
    const volH = opts.volume === false ? 0 : 52;
    const gap = 14;
    const priceH = H - volH - gap - 18;
    const padL = 4;
    const padR = 54;
    const innerW = W - padL - padR;

    const highs = candles.map((c) => c.high).filter(isNum);
    const lows = candles.map((c) => c.low).filter(isNum);
    const maxP = Math.max(...highs);
    const minP = Math.min(...lows);
    const pad = (maxP - minP) * 0.06 || maxP * 0.01;
    const top = maxP + pad;
    const bottom = minP - pad;
    const yOf = (p) => 12 + ((top - p) / (top - bottom || 1)) * priceH;

    const maxV = Math.max(...candles.map((c) => c.volume || 0));
    const vTop = 12 + priceH + gap;
    const yVol = (v) => vTop + volH - ((v || 0) / (maxV || 1)) * volH;

    const step = innerW / candles.length;
    const bw = Math.max(1.4, step * 0.6);

    let grid = '';
    for (let i = 0; i <= 3; i += 1) {
      const p = bottom + ((top - bottom) * i) / 3;
      const y = yOf(p);
      grid += `<line x1="${padL}" y1="${y.toFixed(1)}" x2="${padL + innerW}" y2="${y.toFixed(1)}" stroke="${cv('--chart-grid', '#e3e9f2')}" stroke-width="1"/>`;
      grid += `<text x="${padL + innerW + 6}" y="${(y + 3).toFixed(1)}">${p.toFixed(2)}</text>`;
    }

    let body = '';
    let volBody = '';
    let maPts = [];
    candles.forEach((c, i) => {
      const x = padL + i * step + step / 2;
      const color = c.close >= c.open ? '#e11d33' : '#0d9b6c';
      const yO = yOf(c.open);
      const yC = yOf(c.close);
      const yH = yOf(c.high);
      const yL = yOf(c.low);
      body += `<line x1="${x.toFixed(1)}" y1="${yH.toFixed(1)}" x2="${x.toFixed(1)}" y2="${yL.toFixed(1)}" stroke="${color}" stroke-width="1"/>`;
      body += `<rect x="${(x - bw / 2).toFixed(1)}" y="${Math.min(yO, yC).toFixed(1)}" width="${bw.toFixed(1)}" height="${Math.max(1, Math.abs(yC - yO)).toFixed(1)}" fill="${color}" rx="0.5"/>`;
      if (volH) volBody += `<rect x="${(x - bw / 2).toFixed(1)}" y="${yVol(c.volume).toFixed(1)}" width="${bw.toFixed(1)}" height="${Math.max(0.6, vTop + volH - yVol(c.volume)).toFixed(1)}" fill="${color}" opacity="0.42" rx="0.5"/>`;
      if (i >= candles.length - 20) {
        const slice = candles.slice(Math.max(0, i - 19), i + 1).map((k) => k.close);
        const ma = slice.reduce((a, b) => a + b, 0) / slice.length;
        maPts.push(`${x.toFixed(1)},${yOf(ma).toFixed(1)}`);
      }
    });

    let dates = '';
    const tick = Math.max(1, Math.floor(candles.length / 6));
    candles.forEach((c, i) => {
      if (i % tick === 0 || i === candles.length - 1) {
        const x = padL + i * step + step / 2;
        dates += `<text x="${x.toFixed(1)}" y="${H - 2}" text-anchor="middle">${String(c.date).slice(5)}</text>`;
      }
    });

    const last = candles[candles.length - 1];
    const lastColor = last.close >= last.open ? '#e11d33' : '#0d9b6c';
    return `
    <svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="K线图">
      ${grid}
      ${volH ? `<line x1="${padL}" y1="${vTop}" x2="${padL + innerW}" y2="${vTop}" stroke="${cv('--chart-grid', '#e3e9f2')}"/>` : ''}
      ${volBody}
      ${body}
      ${maPts.length > 2 ? `<polyline points="${maPts.join(' ')}" fill="none" stroke="#3b82f6" stroke-width="1.4" opacity="0.9"/>` : ''}
      <line x1="${padL}" y1="${yOf(last.close).toFixed(1)}" x2="${padL + innerW}" y2="${yOf(last.close).toFixed(1)}" stroke="${lastColor}" stroke-width="0.8" stroke-dasharray="3 3" opacity="0.6"/>
      ${dates}
    </svg>`;
  }

  function rankChart(trend) {
    if (!trend || trend.length < 3) return '<p class="badge-note">热度趋势数据不足（该股近期未进入热度统计样本）。</p>';
    const W = 400;
    const H = 200;
    const padL = 46;
    const padR = 12;
    const innerW = W - padL - padR;
    const maxRank = Math.max(...trend.map((t) => t.rank), 10);
    const scaleMax = Math.max(maxRank, 100);
    const yOf = (r) => 12 + (Math.log10(Math.max(1, r)) / Math.log10(scaleMax)) * (H - 42);
    const step = innerW / Math.max(1, trend.length - 1);

    let grid = '';
    [1, 10, 100, 1000].filter((v) => v <= scaleMax).forEach((r) => {
      const y = yOf(r);
      grid += `<line x1="${padL}" y1="${y.toFixed(1)}" x2="${W - padR}" y2="${y.toFixed(1)}" stroke="${cv('--chart-grid', '#e3e9f2')}"/>`;
      grid += `<text x="${padL - 8}" y="${(y + 3).toFixed(1)}" text-anchor="end">#${r}</text>`;
    });

    const pts = trend.map((t, i) => {
      const x = padL + i * step;
      return { x, y: yOf(t.rank), rank: t.rank, date: t.date };
    });
    const line = pts.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ');
    const area = `${padL},${(H - 28).toFixed(1)} ${line} ${(padL + (trend.length - 1) * step).toFixed(1)},${(H - 28).toFixed(1)}`;

    const dotStep = Math.max(1, Math.floor(trend.length / 10));
    let dots = '';
    pts.forEach((p, i) => {
      if (i % dotStep === 0 || i === pts.length - 1) {
        dots += `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="2" fill="#2563eb"/>`;
        dots += `<text x="${p.x.toFixed(1)}" y="${H - 8}" text-anchor="middle">${String(p.date).slice(5)}</text>`;
      }
    });
    const best = trend.reduce((a, b) => (b.rank < a.rank ? b : a), trend[0]);
    return `
    <svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="热度排名趋势">
      ${grid}
      <polygon points="${area}" fill="rgba(37, 99, 235, 0.10)"/>
      <polyline points="${line}" fill="none" stroke="#2563eb" stroke-width="1.8"/>
      ${dots}
      <text x="${padL}" y="10">排名越靠上越热门 · 最佳 #${best.rank}</text>
    </svg>`;
  }

  function profitBars(quarters) {
    if (!quarters || quarters.length < 2) return '<p class="badge-note">单季数据不足。</p>';
    const W = 400;
    const H = 190;
    const padL = 8;
    const padR = 8;
    const innerW = W - padL - padR;
    const vals = quarters.map((q) => q.profit).filter(isNum);
    const maxV = Math.max(...vals, 1);
    const minV = Math.min(...vals, 0);
    const span = maxV - minV || maxV;
    const zeroY = 14 + (maxV / span) * (H - 46);
    const step = innerW / quarters.length;
    const bw = Math.max(3, step * 0.56);
    let bars = '';
    quarters.forEach((q, i) => {
      const x = padL + i * step + step / 2;
      const y = 14 + ((maxV - (q.profit || 0)) / span) * (H - 46);
      const h = Math.abs(zeroY - y);
      const up = (q.profitYoY || 0) >= 0;
      const color = up ? '#e11d33' : '#0d9b6c';
      bars += `<rect x="${(x - bw / 2).toFixed(1)}" y="${Math.min(y, zeroY).toFixed(1)}" width="${bw.toFixed(1)}" height="${Math.max(1, h).toFixed(1)}" fill="${color}" opacity="0.78" rx="1.5"/>`;
      if (i % 2 === 0 || quarters.length <= 8) {
        bars += `<text x="${x.toFixed(1)}" y="${H - 6}" text-anchor="middle">${esc(String(q.label).replace('Q', 'Q'))}</text>`;
      }
    });
    return `
    <svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="单季归母净利润">
      <line x1="${padL}" y1="${zeroY.toFixed(1)}" x2="${W - padR}" y2="${zeroY.toFixed(1)}" stroke="${cv('--chart-zero', '#dbe3ef')}"/>
      ${bars}
    </svg>`;
  }

  /* ------------------------------ 渲染 ------------------------------ */
  function renderQuote(d) {
    const q = d.quote;
    const fr = d.fundamentals;
    const tags = [];
    if (q.board) tags.push(`<span class="tag">${q.board}</span>`);
    if (q.limit && q.limit.label) tags.push(`<span class="tag ${q.limit.isLimitUp || q.limit.isLimitDown ? 'warn' : 'accent'}">${q.limit.label}</span>`);
    if (q.isST) tags.push('<span class="tag warn">ST / 风险警示</span>');
    (fr.industry || []).slice(0, 3).forEach((i) => tags.push(`<span class="tag accent">${esc(i.name)}</span>`));
    if (isNum(d.scores.overall)) tags.push(`<span class="tag">综合评分 ${d.scores.overall}</span>`);

    el('quoteCard').innerHTML = `
      <div class="qc-top">
        <div>
          <div><span class="qc-name">${esc(q.name)}</span><span class="qc-code">${esc(q.thscode)}</span></div>
          <div class="qc-tags">${tags.join('')}</div>
        </div>
        <div class="qc-price">
          <div class="p ${cls(q.changePct)}">${n(q.lastPrice)}</div>
          <div class="chg ${cls(q.changePct)}">${isNum(q.change) ? (q.change > 0 ? '+' : '') + q.change.toFixed(2) : '—'} · ${pct(q.changePct)}</div>
        </div>
      </div>
      <div class="qc-stats">
        ${[
          ['今开', n(q.open), ''],
          ['最高', n(q.high), ''],
          ['最低', n(q.low), ''],
          ['昨收', n(q.prevClose), ''],
          ['振幅', plainPct(q.amplitude), ''],
          ['成交量', vol(q.volume), ''],
          ['成交额', money(q.turnover), ''],
          ['总市值', money(fr.size.marketCap), '按股本推算'],
          ['总股本', sharesFmt(fr.size.shares), '按净利/EPS 推算'],
          ['换手率', plainPct(d.capital.turnoverRate), '总股本口径'],
        ].map(([k, v, s]) => `<div class="qc-stat"><div class="k">${k}</div><div class="v">${v}</div>${s ? `<div class="k" style="font-size:10px;margin-top:2px">${s}</div>` : ''}</div>`).join('')}
      </div>`;
  }

  /* ------------------------------ 通用折线 / 柱状图 ------------------------------ */
  function lineChart(opts) {
    const { series, points, height = 210, refLine = null, ySuffix = '', yDigits = 2 } = opts;
    const rows = (points || []).filter((p) => series.some((s) => isNum(p.values[s.key])));
    if (rows.length < 2) return '<p class="badge-note">可用数据点不足，无法绘制趋势。</p>';
    const W = 400;
    const H = height;
    const padL = 48;
    const padR = 42;
    const padT = 14;
    const padB = 26;
    const vals = rows.flatMap((p) => series.map((s) => p.values[s.key])).filter(isNum);
    let min = Math.min(...vals);
    let max = Math.max(...vals);
    if (isNum(refLine)) { min = Math.min(min, refLine); max = Math.max(max, refLine); }
    const rawSpan = max - min || Math.abs(max) || 1;
    min -= rawSpan * 0.14;
    max += rawSpan * 0.14;
    const span = max - min || 1;
    const xOf = (i) => padL + (rows.length === 1 ? 0 : (i / (rows.length - 1)) * (W - padL - padR));
    const yOf = (v) => padT + ((max - v) / span) * (H - padT - padB);

    let grid = '';
    for (let i = 0; i <= 3; i += 1) {
      const v = min + (span * i) / 3;
      const y = yOf(v);
      grid += `<line x1="${padL}" y1="${y.toFixed(1)}" x2="${W - padR}" y2="${y.toFixed(1)}" stroke="${cv('--chart-grid', '#e3e9f2')}"/>`;
      grid += `<text x="${padL - 6}" y="${(y + 3).toFixed(1)}" text-anchor="end">${v.toFixed(yDigits)}${ySuffix}</text>`;
    }
    if (isNum(refLine)) {
      grid += `<line x1="${padL}" y1="${yOf(refLine).toFixed(1)}" x2="${W - padR}" y2="${yOf(refLine).toFixed(1)}" stroke="#8b98ab" stroke-dasharray="4 4"/>`;
    }

    let paths = '';
    let dots = '';
    series.forEach((s) => {
      const pts = rows.map((p, i) => ({ i, v: p.values[s.key] })).filter((q) => isNum(q.v));
      if (pts.length < 2) return;
      paths += `<polyline points="${pts.map((q) => `${xOf(q.i).toFixed(1)},${yOf(q.v).toFixed(1)}`).join(' ')}" fill="none" stroke="${s.color}" stroke-width="1.8" stroke-linejoin="round"/>`;
      const lastPt = pts[pts.length - 1];
      dots += `<circle cx="${xOf(lastPt.i).toFixed(1)}" cy="${yOf(lastPt.v).toFixed(1)}" r="2.6" fill="${s.color}"/>`;
      dots += `<text x="${(xOf(lastPt.i) + 6).toFixed(1)}" y="${(yOf(lastPt.v) - 5).toFixed(1)}" fill="${s.color}">${lastPt.v.toFixed(yDigits)}${ySuffix}</text>`;
    });

    let labels = '';
    const tick = Math.max(1, Math.ceil(rows.length / 8));
    rows.forEach((p, i) => {
      if (i % tick === 0 || i === rows.length - 1) {
        labels += `<text x="${xOf(i).toFixed(1)}" y="${H - 6}" text-anchor="middle">${esc(p.label)}</text>`;
      }
    });

    return `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(opts.title || '趋势图')}">${grid}${paths}${dots}${labels}</svg>
      <div class="mini-legend">${series.map((s) => `<span><i style="background:${s.color}"></i>${esc(s.label)}</span>`).join('')}${isNum(refLine) ? `<span><i style="background:#8b98ab"></i>参考线 ${refLine}${ySuffix}</span>` : ''}</div>`;
  }

  function barChart(opts) {
    const { bars, height = 180, ySuffix = '', refLine = null, digits = 2 } = opts;
    const rows = (bars || []).filter((b) => isNum(b.value));
    if (rows.length < 2) return '<p class="badge-note">可用数据点不足。</p>';
    const W = 400;
    const H = height;
    const padL = 48;
    const padR = 14;
    const padT = 14;
    const padB = 26;
    const vals = rows.map((b) => b.value);
    const max = Math.max(...vals, isNum(refLine) ? refLine : -Infinity, 0);
    const min = Math.min(...vals, 0);
    const span = (max - min) || 1;
    const yOf = (v) => padT + ((max - v) / span) * (H - padT - padB);
    const step = (W - padL - padR) / rows.length;
    const bw = Math.max(4, step * 0.55);
    let out = '';
    for (let i = 0; i <= 3; i += 1) {
      const v = min + (span * i) / 3;
      const y = yOf(v);
      out += `<line x1="${padL}" y1="${y.toFixed(1)}" x2="${W - padR}" y2="${y.toFixed(1)}" stroke="${cv('--chart-grid', '#e3e9f2')}"/>`;
      out += `<text x="${padL - 6}" y="${(y + 3).toFixed(1)}" text-anchor="end">${v.toFixed(digits)}${ySuffix}</text>`;
    }
    if (isNum(refLine)) {
      out += `<line x1="${padL}" y1="${yOf(refLine).toFixed(1)}" x2="${W - padR}" y2="${yOf(refLine).toFixed(1)}" stroke="#3b82f6" stroke-dasharray="4 4"/>`;
    }
    rows.forEach((b, i) => {
      const x = padL + i * step + step / 2;
      const y = yOf(b.value);
      const zeroY = yOf(0);
      const color = b.color || (b.value >= (isNum(refLine) ? refLine : 0) ? '#0d9b6c' : '#e11d33');
      out += `<rect x="${(x - bw / 2).toFixed(1)}" y="${Math.min(y, zeroY).toFixed(1)}" width="${bw.toFixed(1)}" height="${Math.max(1, Math.abs(zeroY - y)).toFixed(1)}" fill="${color}" opacity="0.85" rx="1.5"/>`;
      if (rows.length <= 12 || i % 2 === 0) {
        out += `<text x="${x.toFixed(1)}" y="${(Math.min(y, zeroY) - 4).toFixed(1)}" text-anchor="middle" fill="#52637a">${b.value.toFixed(digits)}</text>`;
        out += `<text x="${x.toFixed(1)}" y="${H - 6}" text-anchor="middle">${esc(b.label)}</text>`;
      }
    });
    return `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(opts.title || '柱状图')}">${out}</svg>`;
  }

  function histogram(opts) {
    const { values, marker, bins = 12, height = 150, label = '' } = opts;
    const vals = (values || []).filter(isNum).slice().sort((a, b) => a - b);
    if (vals.length < 5) return '<p class="badge-note">样本不足，无法绘制分布。</p>';
    const cap = vals[Math.min(vals.length - 1, Math.floor(vals.length * 0.97))] || vals[vals.length - 1];
    const min = Math.min(...vals, 0);
    const span = (cap - min) || 1;
    const counts = new Array(bins).fill(0);
    for (const v of vals) {
      const idx = Math.min(bins - 1, Math.max(0, Math.floor(((Math.min(v, cap) - min) / span) * bins)));
      counts[idx] += 1;
    }
    const maxCount = Math.max(...counts, 1);
    const W = 400;
    const H = height;
    const padL = 10;
    const padR = 10;
    const padT = 12;
    const padB = 24;
    const step = (W - padL - padR) / bins;
    let out = '';
    counts.forEach((c, i) => {
      const h = (c / maxCount) * (H - padT - padB);
      const x = padL + i * step;
      const lo = min + (span * i) / bins;
      const hi = min + (span * (i + 1)) / bins;
      const isSelf = isNum(marker) && marker >= lo && marker <= hi;
      out += `<rect x="${(x + 1).toFixed(1)}" y="${(H - padB - h).toFixed(1)}" width="${(step - 2).toFixed(1)}" height="${Math.max(1, h).toFixed(1)}" fill="${isSelf ? '#2563eb' : '#cfd9e8'}" rx="1.5"/>`;
      if (i % 2 === 0) out += `<text x="${(x + step / 2).toFixed(1)}" y="${H - 8}" text-anchor="middle">${lo.toFixed(1)}</text>`;
    });
    if (isNum(marker)) {
      const x = padL + ((Math.min(marker, cap) - min) / span) * (W - padL - padR);
      out += `<line x1="${x.toFixed(1)}" y1="${padT}" x2="${x.toFixed(1)}" y2="${H - padB}" stroke="#c77700" stroke-dasharray="4 3"/>`;
      out += `<text x="${(x + 4).toFixed(1)}" y="${padT + 8}" fill="#c77700">本股 ${marker}</text>`;
    }
    return `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(label)}">${out}</svg>`;
  }

  function renderScores(d) {
    const s = d.scores;
    const circ = 2 * Math.PI * 46;
    const pctv = isNum(s.overall) ? s.overall : 0;
    const dash = (pctv / 100) * circ;
    el('sec-score').innerHTML = `${cardTitle('综合评分', '六个维度加权（权重随可用数据自动归一），全部由下方量化指标推导')}
      <div class="score-top">
        <div class="score-ring">
          <svg viewBox="0 0 110 110" width="118" height="118">
            <circle cx="55" cy="55" r="46" fill="none" stroke="${cv('--chart-grid', '#e3e9f2')}" stroke-width="9"/>
            <circle cx="55" cy="55" r="46" fill="none" stroke="url(#sg)" stroke-width="9" stroke-linecap="round"
              stroke-dasharray="${dash.toFixed(1)} ${(circ - dash).toFixed(1)}" transform="rotate(-90 55 55)"/>
            <defs><linearGradient id="sg" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="#2563eb"/><stop offset="100%" stop-color="#3b82f6"/>
            </linearGradient></defs>
          </svg>
          <div class="num"><span class="val">${isNum(s.overall) ? s.overall : '—'}</span><small>/100</small></div>
        </div>
        <div class="score-meta">
          <div class="grade">${esc(s.grade || '—')}</div>
          <div class="grade-sub">评分口径：基本面质量、成长性、估值性价比、盘面资金、市场热度、技术走势。<br/>分数越高代表该维度在样本中的相对位置越靠前，不代表未来收益。</div>
        </div>
      </div>
      <div class="bars">
        ${(s.breakdown || []).map((b) => `
          <div class="bar-row">
            <div class="lb">${esc(b.label)}</div>
            <div class="bar-track"><div class="bar-fill" style="width:${Math.max(2, b.score)}%"></div></div>
            <div class="vv">${b.score.toFixed(1)}</div>
          </div>`).join('')}
      </div>`;
  }

  function renderNarrative(d) {
    const nz = d.narrative;
    const list = (arr, empty) => (arr && arr.length ? `<ul>${arr.map((x) => `<li>${esc(x)}</li>`).join('')}</ul>` : `<p class="badge-note">${empty}</p>`);
    const block = (title, text) => (text ? `<h3>${esc(title)}</h3><p class="sub" style="margin:0;color:var(--text-dim);font-size:12.8px;line-height:1.75">${esc(text)}</p>` : '');
    el('sec-narrative').innerHTML = `${cardTitle('深度解读', '规则化描述：每条结论都能在下方数字中找到依据')}
      <div class="narr">
        <p class="headline">${esc(nz.headline)}</p>
        ${block('近 5 日区间表现', nz.fiveDayText)}
        ${block('财务趋势', (nz.trendNotes || []).map((c) => (c && c.text ? c.text : c)).slice(0, 3).join('；') + (nz.trendNotes && nz.trendNotes.length ? '。' : ''))}
        ${block('盈利结构（杜邦）', nz.dupontText)}
        ${block('行业地位', nz.industryText)}
        ${block('股东回报', nz.dividendText)}
        ${block('交易行为', nz.tradingText)}
        ${block('风险检查', nz.riskText)}
        <h3>积极信号</h3>
        ${list(nz.highlights, '当前可量化的积极信号不明显。')}
        <h3>风险与瑕疵</h3>
        ${list(nz.risks, '未触发主要风险阈值。')}
      </div>`;
  }

  function renderFundamentals(d) {
    const f = d.fundamentals;
    const bal = f.balance || {};
    const cf = f.cashflow || {};
    const q = f.quality || {};
    const r = f.ratios || {};
    const rep = f.latestReport;
    el('sec-fundamentals').innerHTML = `${cardTitle('企业基本面',
      rep ? `最新年报：${rep.fiscalYear} 年（报告期 ${esc(rep.periodEnd || '—')}）· 金额单位：元` : '未取到财报数据')}
      <div class="tag-cloud" style="margin-bottom:16px">
        ${(f.industry || []).map((i) => `<span class="tag accent">${esc(i.name)}</span>`).join('')}
        ${(f.concepts || []).slice(0, 14).map((c) => `<span class="tag">${esc(c.name)}</span>`).join('')}
        ${(f.concepts || []).length > 14 ? `<span class="tag">+${f.concepts.length - 14}</span>` : ''}
      </div>
      <div class="kpi-grid">
        ${kpi('营业总收入', money(f.income.revenue), `同比 ${pct(d.performance.summary.revenueYoY)}`, cls(d.performance.summary.revenueYoY) === 'up' ? 'good' : '')}
        ${kpi('归母净利润', money(f.income.parentNetProfit), `同比 ${pct(d.performance.summary.profitYoY)}`)}
        ${kpi('毛利率', plainPct(r.grossMargin), '经营定价能力')}
        ${kpi('净利率', plainPct(r.netMargin), '')}
        ${kpi('ROE(加权)', plainPct(q.roe), isNum(q.roeDeducted) ? `扣非 ${plainPct(q.roeDeducted)}` : '')}
        ${kpi('ROA', plainPct(q.roa), '')}
        ${kpi('资产负债率', plainPct(q.assetsDebtRatio), '')}
        ${kpi('流动比率', n(q.currentRatio, 2), `速动 ${n(q.quickRatio, 2)}`)}
        ${kpi('总资产', money(bal.assetsTotal), `负债 ${money(bal.totalDebt)}`)}
        ${kpi('股东权益', money(bal.equity), '')}
        ${kpi('货币资金', money(bal.cash), `占总资产 ${plainPct(bal.cashToAssets)}`)}
        ${kpi('应收账款', money(bal.receivable), `周转 ${n(q.receivableTurnover, 2)} 次`)}
        ${kpi('经营现金流', money(cf.operating), `为净利 ${n(cf.ocfToProfit, 2)} 倍`, isNum(cf.ocfToProfit) && cf.ocfToProfit >= 1 ? 'good' : isNum(cf.ocfToProfit) && cf.ocfToProfit < 0.4 ? 'bad' : '')}
        ${kpi('自由现金流', money(cf.freeCashFlow), `资本开支 ${money(cf.capex)}`)}
        ${kpi('研发费用', money(f.income.rdExpense), `占营收 ${plainPct(r.rdRatio)}`)}
        ${kpi('现金分红(含付息)', money(cf.dividendsPaid), '')}
      </div>
      <div class="badge-note">数据来自同花顺财报接口；比率优先取「财务指标」口径，缺失时用报表科目自行计算。金额为年报累计口径。</div>`;
  }

  function renderPerformance(d) {
    const p = d.performance;
    const s = p.summary;
    el('sec-performance').innerHTML = `${cardTitle('业绩成长轨迹', '年报口径 + 单季拆解（单季 = 累计值差分）')}
      <div class="kpi-grid" style="margin-bottom:16px">
        ${kpi('营收 3 年复合', pct(s.revenueCagr3), 'CAGR')}
        ${kpi('净利 3 年复合', pct(s.profitCagr3), 'CAGR')}
        ${kpi('连续增长年数', isNum(s.consecutiveGrowthYears) ? `${s.consecutiveGrowthYears} 年` : '—', '营收同比 > 0')}
        ${kpi('近 4 季盈利增长', isNum(s.quartersWithPositiveYoY) ? `${s.quartersWithPositiveYoY} / 4` : '—', '单季归母净利同比为正')}
        ${kpi('近三年平均营收增速', pct(s.avgRevenueGrowthPrev3), '')}
        ${kpi('最新单季归母净利', money(s.latestQuarter && s.latestQuarter.profit), s.latestQuarter ? `${esc(s.latestQuarter.label)} 同比 ${pct(s.latestQuarter.profitYoY)}` : '')}
      </div>
      <div class="table-wrap" style="margin-bottom:16px">
        <table>
          <thead><tr><th>年度</th><th>营业收入</th><th>营收同比</th><th>归母净利</th><th>净利同比</th><th>毛利率</th><th>净利率</th><th>EPS</th></tr></thead>
          <tbody>
          ${p.annual.slice().reverse().map((a) => `<tr>
            <td>${a.fiscalYear}</td>
            <td>${money(a.revenue)}</td>
            <td class="${cls(a.revenueYoY)}">${pct(a.revenueYoY)}</td>
            <td>${money(a.parentNetProfit)}</td>
            <td class="${cls(a.profitYoY)}">${pct(a.profitYoY)}</td>
            <td>${plainPct(a.grossMargin)}</td>
            <td>${plainPct(a.netMargin)}</td>
            <td>${n(a.eps, 3)}</td>
          </tr>`).join('')}
          </tbody>
        </table>
      </div>
      <h3 style="font-size:13px;color:#143049;margin:0 0 8px">近 12 个单季归母净利润（亿元）</h3>
      ${profitBars(p.quarterly)}
      <div class="legend"><span><i style="background:#e11d33"></i>同比正增长</span><span><i style="background:#0d9b6c"></i>同比下滑</span></div>
      <div class="table-wrap" style="margin-top:16px">
        <table>
          <thead><tr><th>单季</th><th>单季营收</th><th>营收同比</th><th>单季归母净利</th><th>净利同比</th><th>毛利率</th></tr></thead>
          <tbody>
          ${p.quarterly.slice().reverse().map((qq) => `<tr>
            <td>${esc(qq.label)}</td>
            <td>${money(qq.revenue)}</td>
            <td class="${cls(qq.revenueYoY)}">${pct(qq.revenueYoY)}</td>
            <td>${money(qq.profit)}</td>
            <td class="${cls(qq.profitYoY)}">${pct(qq.profitYoY)}</td>
            <td>${plainPct(qq.grossMargin)}</td>
          </tr>`).join('')}
          </tbody>
        </table>
      </div>`;
  }

  function renderMoat(d) {
    const m = d.moat;
    el('sec-moat').innerHTML = `${cardTitle('主营业务优势（数据证据）', '不含公司公告文本，全部由财务与行情数据推导：毛利率看定价权、ROE 看资本效率、现金流看利润含金量、周转看产业链地位')}
      <div class="moat-list">
        ${m.items.map((it, i) => `
          <div class="moat-item lv-${esc(it.level)}">
            <div class="idx">${String(i + 1).padStart(2, '0')}</div>
            <div>
              <div class="ttl">${esc(it.title)}<span class="metric">${esc(it.metric)}</span><span class="lv-badge ${levelClass(it.level)}">${esc(it.level)}</span></div>
              <div class="ev">${esc(it.evidence)}</div>
            </div>
          </div>`).join('')}
      </div>
      <div class="badge-note">${esc(m.summary)}</div>`;
  }

  function renderKeyFacts(d) {
    const facts = d.keyFacts || [];
    el('keyFacts').innerHTML = facts.map((f) => `<div class="fact">
      <div class="fl">${esc(f.label)}</div>
      <div class="fv">${esc(f.value)}</div>
      ${f.note ? `<div class="fn">${esc(f.note)}</div>` : ''}
    </div>`).join('');
  }

  function renderTrends(d) {
    const t = d.trends || {};
    const years = (t.years || []).filter((y) => isNum(y.revenue));
    const points = years.map((y) => ({
      label: String(y.year),
      values: { grossMargin: y.grossMargin, netMargin: y.netMargin, roe: y.roe },
    }));
    const ocfBars = years.filter((y) => isNum(y.ocfToProfit)).map((y) => ({ label: String(y.year), value: y.ocfToProfit }));
    const rateRows = (t.ratioSeries || []).filter((r) => String(r.label).endsWith('FY'));
    const concl = t.conclusions || [];

    el('sec-trends').innerHTML = `${cardTitle('多期财务趋势', '近 8 个财年的利润率 / ROE 演化，叠加 6 个年度报告期的财务指标（同花顺指标口径）')}
      ${points.length >= 2 ? `<div class="chart-box"><h3 class="chart-title">利润率与 ROE 趋势（%）</h3>${lineChart({
        series: [
          { key: 'grossMargin', label: '毛利率', color: '#2563eb' },
          { key: 'netMargin', label: '净利率', color: '#3b82f6' },
          { key: 'roe', label: 'ROE（平均净资产）', color: '#c77700' },
        ],
        points,
        ySuffix: '%',
        height: 220,
      })}</div>` : ''}
      ${ocfBars.length >= 2 ? `<div class="chart-box"><h3 class="chart-title">经营现金流 / 净利润（倍，蓝线为 1 倍参考）</h3>${barChart({ bars: ocfBars, refLine: 1, digits: 2, height: 170 })}</div>` : ''}
      ${points.length >= 3 ? `<div class="chart-box"><h3 class="chart-title">期间费用率趋势（% of 营收）</h3>${lineChart({
        series: [
          { key: 'salesFeeRatio', label: '销售费用率', color: '#c94b28' },
          { key: 'manageFeeRatio', label: '管理费用率', color: '#5c8f1f' },
          { key: 'rdRatio', label: '研发费用率', color: '#1f78c8' },
          { key: 'taxRate', label: '实际税率', color: '#6f5aa8' },
        ],
        points: years.map((y) => ({
          label: String(y.year),
          values: { salesFeeRatio: y.salesFeeRatio, manageFeeRatio: y.manageFeeRatio, rdRatio: y.rdRatio, taxRate: y.taxRate },
        })),
        ySuffix: '%',
        height: 190,
      })}</div>` : ''}
      <div class="table-wrap" style="margin-top:16px">
        <table>
          <thead><tr><th>年度</th><th>营收</th><th>营收同比</th><th>归母净利</th><th>净利同比</th><th>毛利率</th><th>净利率</th><th>ROE</th><th>资产负债率</th><th>现金流/净利</th><th>EPS</th></tr></thead>
          <tbody>
          ${years.slice().reverse().map((y) => `<tr>
            <td>${y.year}</td>
            <td>${money(y.revenue)}</td>
            <td class="${cls(y.revenueYoY)}">${pct(y.revenueYoY)}</td>
            <td>${money(y.parentProfit)}</td>
            <td class="${cls(y.profitYoY)}">${pct(y.profitYoY)}</td>
            <td>${plainPct(y.grossMargin)}</td>
            <td>${plainPct(y.netMargin)}</td>
            <td>${plainPct(y.roe)}</td>
            <td>${plainPct(y.debtRatio)}</td>
            <td class="${isNum(y.ocfToProfit) && y.ocfToProfit >= 1 ? 'up' : isNum(y.ocfToProfit) && y.ocfToProfit < 0.6 ? 'down' : ''}">${n(y.ocfToProfit, 2)}</td>
            <td>${n(y.eps, 3)}</td>
          </tr>`).join('')}
          </tbody>
        </table>
      </div>
      ${rateRows.length >= 2 ? `
      <div class="table-wrap" style="margin-top:14px">
        <table>
          <thead><tr><th>报告期</th><th>加权 ROE</th><th>扣非 ROE</th><th>毛利率</th><th>净利率</th><th>资产负债率</th><th>流动比率</th><th>应收周转</th><th>总资产周转</th><th>净利现金含量</th></tr></thead>
          <tbody>
          ${rateRows.slice().reverse().map((r) => `<tr>
            <td>${esc(r.label)}</td>
            <td>${plainPct(r.roe)}</td>
            <td>${plainPct(r.roeDeducted)}</td>
            <td>${plainPct(r.grossMargin)}</td>
            <td>${plainPct(r.netMargin)}</td>
            <td>${plainPct(r.debtRatio)}</td>
            <td>${n(r.currentRatio, 2)}</td>
            <td>${n(r.receivableTurnover, 2)}</td>
            <td>${n(r.assetTurnover, 3)}</td>
            <td>${plainPct(r.netProfitCashContent)}</td>
          </tr>`).join('')}
          </tbody>
        </table>
      </div>` : ''}
      ${concl.length ? `<div class="concl-list">${concl.map((c) => `<div class="concl ${c.tone}"><span class="ic">${c.tone === 'good' ? '▲' : c.tone === 'bad' ? '▼' : '·'}</span><span>${esc(c.text)}</span></div>`).join('')}</div>` : ''}
      <div class="badge-note">ROE 采用「归母净利 ÷ 期初期末平均净资产」；财务指标表中的口径为同花顺加权 ROE。年报期间可比，季报为年内累计值。</div>`;
  }

  function renderDupont(d) {
    const dp = d.dupont || {};
    if (!dp.available) {
      el('sec-dupont').innerHTML = `${cardTitle('杜邦分解')}<p class="badge-note">报表科目不足（缺少营业成本或资产负债表数据），无法做杜邦分解。</p>`;
      return;
    }
    const series = (dp.series || []).filter((s) => isNum(s.roe));
    el('sec-dupont').innerHTML = `${cardTitle('杜邦分解', `ROE = 净利率 × 总资产周转率 × 权益乘数（${dp.year} 年，期初期末平均口径）`)}
      <div class="dupont-grid">
        ${dp.factors.map((f) => `<div class="dupont-card">
          <div class="dl">${esc(f.label)}</div>
          <div class="dv">${n(f.value, f.unit === '%' ? 2 : 3)}${esc(f.unit)}</div>
          <div class="dd">${esc(f.desc)}</div>
        </div>`).join('')}
      </div>
      <div class="dupont-eq">
        净利率 <b>${n(dp.factors[0].value)}%</b> × 周转 <b>${n(dp.factors[1].value, 3)}</b> 次 × 杠杆 <b>${n(dp.factors[2].value, 2)}</b> 倍
        ≈ ROE <b>${n(dp.approxRoe)}%</b>${isNum(dp.reportedRoeAnnual) ? `（同口径加权 ROE ${n(dp.reportedRoeAnnual)}%）` : ''}
      </div>
      ${series.length >= 2 ? `<div class="chart-box"><h3 class="chart-title">ROE 及其驱动因子（近似口径，%）</h3>${lineChart({
        series: [
          { key: 'roe', label: 'ROE', color: '#c77700' },
          { key: 'netMargin', label: '净利率', color: '#2563eb' },
          { key: 'turnover', label: '总资产周转率(次)', color: '#3b82f6' },
        ],
        points: series.map((s) => ({ label: String(s.year), values: { roe: s.roe, netMargin: s.netMargin, turnover: isNum(s.assetTurnover) ? s.assetTurnover * 50 : null } })),
        ySuffix: '',
        height: 200,
      })}</div><div class="badge-note">为便于同图对比，总资产周转率被放大 50 倍显示（0.5 次 → 25），实际数值见上方卡片。</div>` : ''}
      ${dp.contribution ? `<div class="concl-list"><div class="concl flat"><span class="ic">·</span><span>${esc(dp.contribution)}</span></div>${dp.conclusion ? `<div class="concl flat"><span class="ic">·</span><span>${esc(dp.conclusion)}</span></div>` : ''}</div>` : (dp.conclusion ? `<div class="concl-list"><div class="concl flat"><span class="ic">·</span><span>${esc(dp.conclusion)}</span></div></div>` : '')}`;
  }

  function renderIndustry(d) {
    const ir = d.industryRank || {};
    const rows = ir.rows || [];
    if (!rows.length) {
      el('sec-industry').innerHTML = `${cardTitle('行业地位')}<p class="badge-note">同行业样本不足，暂无法做横截面定位。</p>`;
      return;
    }
    const chips = [];
    const r = ir.ranks || {};
    const addChip = (label, obj, suffix = '') => {
      if (obj && isNum(obj.rank)) chips.push(`<span class="risk-pill">${label} 第 ${obj.rank}/${obj.total}${suffix ? ` · 中位 ${obj.median}${suffix}` : ''}</span>`);
    };
    addChip('ROE', r.roe, '%');
    addChip('毛利率', r.grossMargin, '%');
    addChip('净利率', r.netMargin, '%');
    addChip('净利增速', r.profitYoY, '%');
    addChip('PE(低→高)', r.pe);
    addChip('成交额', r.turnover);
    el('sec-industry').innerHTML = `${cardTitle('行业地位（横截面）', `${esc(ir.universeLabel || '同行业')} · ${ir.sampleSize} 只样本（自身 + 相似公司，同报告期指标 ${esc(d.fundamentals.quality && d.fundamentals.quality.report ? d.fundamentals.quality.report : '—')}）`)}
      <div class="risk-summary">${chips.join('')}</div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>公司</th><th>PE</th><th>PB</th><th>ROE</th><th>毛利率</th><th>净利率</th><th>营收同比</th><th>净利同比</th><th>成交额</th></tr></thead>
          <tbody>
          ${rows.map((row) => `<tr class="${row.isSelf ? 'self-row' : ''}">
            <td>${esc(row.name)}${row.isSelf ? ' <span class="tag accent" style="font-size:10px">本股</span>' : (row.similarity ? ` <span style="color:var(--text-mute);font-size:10.5px">相似 ${row.similarity}</span>` : '')}</td>
            <td class="${row.isSelf ? 'strong' : ''}">${n(row.pe)}</td>
            <td class="${row.isSelf ? 'strong' : ''}">${n(row.pb)}</td>
            <td class="${row.isSelf ? 'strong' : ''}">${plainPct(row.roe)}</td>
            <td class="${row.isSelf ? 'strong' : ''}">${plainPct(row.grossMargin)}</td>
            <td class="${row.isSelf ? 'strong' : ''}">${plainPct(row.netMargin)}</td>
            <td class="${row.isSelf ? 'strong' : ''} ${cls(row.revenueYoY)}">${pct(row.revenueYoY)}</td>
            <td class="${row.isSelf ? 'strong' : ''} ${cls(row.profitYoY)}">${pct(row.profitYoY)}</td>
            <td>${money(row.turnover)}</td>
          </tr>`).join('')}
          </tbody>
        </table>
      </div>
      <div class="concl-list"><div class="concl flat"><span class="ic">·</span><span>${esc(ir.conclusion || '')}</span></div></div>
      <div class="badge-note">排名基于同报告期财务指标与最新估值；样本为相似度最高的公司，若样本数少则仅代表「可比公司组」内部高低。</div>`;
  }

  function renderDividend(d) {
    const dv = d.dividends || {};
    if (!dv.available) {
      el('sec-dividend').innerHTML = `${cardTitle('分红送转')}<p class="badge-note">${esc(dv.conclusion || '近 6 年无除权除息记录。')}</p>`;
      return;
    }
    const recent = (dv.events || []).slice(0, 8);
    el('sec-dividend').innerHTML = `${cardTitle('分红送转（近 10 年）', '来自同花顺公司行动接口，除权除息日口径')}
      <div class="kpi-grid" style="margin-bottom:16px">
        ${kpi('股息率 (TTM)', plainPct(dv.dividendYieldTTM), '近 12 个月每股派息/现价', isNum(dv.dividendYieldTTM) && dv.dividendYieldTTM >= 2 ? 'good' : '')}
        ${kpi('连续分红年数', `${dv.consecutiveYears} 年`, `覆盖 ${dv.yearsCovered} 个年度`)}
        ${kpi('区间每股累计派息', `${n(dv.perShareSum6y, 3)} 元`, '近 10 年合计')}
        ${kpi('近 12 个月派息总额', money(dv.payoutLast12m), '按总股本折算')}
        ${kpi('分红/归母净利', plainPct(dv.payoutRatio), '近 12 个月派息 ÷ 最新年报净利', isNum(dv.payoutRatio) && dv.payoutRatio > 30 ? 'good' : '')}
        ${kpi('除权除息次数', `${(dv.events || []).length} 次`, `年均 ${n(dv.avgPerYear, 3)} 元/股`)}
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>除权除息日</th><th>每股派息(元)</th><th>每股送转(股)</th><th>备注</th></tr></thead>
          <tbody>
          ${recent.map((e) => `<tr>
            <td>${esc(e.exDate)}</td>
            <td>${n(e.dividendPerShare, 4)}</td>
            <td>${isNum(e.bonusPerShare) && e.bonusPerShare > 0 ? n(e.bonusPerShare, 4) : '—'}</td>
            <td>${isNum(e.bonusPerShare) && e.bonusPerShare > 0 ? '含送转' : '现金分红'}</td>
          </tr>`).join('')}
          </tbody>
        </table>
      </div>
      <div class="concl-list"><div class="concl ${isNum(dv.dividendYieldTTM) && dv.dividendYieldTTM >= 2 ? 'good' : 'flat'}"><span class="ic">·</span><span>${esc(dv.conclusion || '')}</span></div></div>`;
  }

  function renderRisk(d) {
    const rm = d.riskMatrix || {};
    const rows = rm.rows || [];
    const sm = rm.summary || {};
    const statusText = { alert: '警戒', watch: '观察', ok: '正常' };
    el('sec-risk').innerHTML = `${cardTitle('风险矩阵', '把规则、阈值、当前值并列检查；不是评级，只是把「哪些条件已被触发」列清楚')}
      <div class="risk-summary">
        <span class="risk-pill ${sm.alert ? 'alert' : 'ok'}">触发阈值 ${sm.alert || 0} 项</span>
        <span class="risk-pill ${sm.watch ? 'watch' : 'ok'}">需观察 ${sm.watch || 0} 项</span>
        <span class="risk-pill ok">正常 ${sm.ok || 0} 项</span>
        <span class="risk-pill">整体：${esc(rm.level || '—')}</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>维度</th><th>检查项</th><th>阈值</th><th>当前值</th><th>状态</th></tr></thead>
          <tbody>
          ${rows.map((r) => `<tr>
            <td>${esc(r.dim)}</td>
            <td>${esc(r.item)}</td>
            <td style="text-align:left;font-family:inherit;color:var(--text-mute)">${esc(r.threshold)}</td>
            <td>${esc(String(r.value))}</td>
            <td><span class="st ${r.status}">${statusText[r.status] || r.status}</span></td>
          </tr>`).join('')}
          </tbody>
        </table>
      </div>`;
  }

  function renderValuation(d) {
    const v = d.valuation;
    const u = d.universe || {};
    const st = u.industryStats || {};
    el('sec-valuation').innerHTML = `${cardTitle('估值水平', `同业样本 ${isNum(st.sampleSize) ? st.sampleSize : 0} 只（${esc(u.label || '同行业')}）取中位数对比`)}
      <div class="kpi-grid">
        ${kpi('PE (TTM)', n(v.peTtm), isNum(v.pePercentile) ? `同业分位 ${v.pePercentile}%` : (v.pePositive === false ? '亏损，负 PE 不参与分位' : ''))}
        ${kpi('PB (MRQ)', n(v.pb), isNum(v.pbPercentile) ? `同业分位 ${v.pbPercentile}%` : '')}
        ${kpi('PS (TTM)', n(v.ps), '')}
        ${kpi('PCF (TTM)', n(v.pcf), '')}
        ${kpi('盈利收益率', plainPct(v.earningsYield), '1/PE')}
        ${kpi('同业 PE 中位', n(st.peMedian), isNum(v.peTtm) && isNum(st.peMedian) ? (v.peTtm < st.peMedian ? '低于同业中位' : '高于同业中位') : '')}
        ${kpi('同业 PB 中位', n(st.pbMedian), isNum(v.pb) && isNum(st.pbMedian) ? (v.pb < st.pbMedian ? '低于同业中位' : '高于同业中位') : '')}
        ${kpi('样本 ROE 参考', plainPct(v.roe), '本股口径')}
      </div>
      ${isNum(v.pePercentile) ? `
      <div style="margin-top:16px">
        <div class="bar-row" style="grid-template-columns:110px 1fr 60px">
          <div class="lb">PE 相对便宜度</div>
          <div class="bar-track"><div class="bar-fill" style="width:${Math.max(2, 100 - v.pePercentile)}%"></div></div>
          <div class="vv">${(100 - v.pePercentile).toFixed(1)}%</div>
        </div>
        <div class="bar-row" style="grid-template-columns:110px 1fr 60px;margin-top:8px">
          <div class="lb">PB 相对便宜度</div>
          <div class="bar-track"><div class="bar-fill" style="width:${isNum(v.pbPercentile) ? Math.max(2, 100 - v.pbPercentile) : 0}%"></div></div>
          <div class="vv">${isNum(v.pbPercentile) ? `${(100 - v.pbPercentile).toFixed(1)}%` : '—'}</div>
        </div>
        <div class="badge-note">条越满表示相对同业越便宜（= 100 - 同业分位）。同业分位按 PE(TTM)/PB(MRQ) 横截面计算，亏损公司（负 PE）不参与。</div>
        ${(st.peList || []).length >= 8 ? `<div class="chart-box"><h3 class="chart-title">同业 PE 分布（横轴 PE，柱高为家数，橙线为本股）</h3>${histogram({ values: st.peList, marker: v.peTtm, label: '同业 PE 分布' })}</div>` : ''}
      </div>` : '<div class="badge-note">同业样本不足，未计算相对分位。</div>'}`;
  }

  function renderCapital(d) {
    const c = d.capital;
    const dt = c.dragonTiger;
    const ts = d.tradingStats || {};
    el('sec-capital').innerHTML = `${cardTitle('盘面资金', '成交额/换手率/量比/量价配合 + 龙虎榜席位 + 近 120 日交易行为统计（不提供主力资金净流入，不做推测）')}
      <div class="kpi-grid">
        ${kpi('今日成交额', money(c.turnover), isNum(c.turnoverRank) ? `全市场第 ${c.turnoverRank} 名` : '')}
        ${kpi('换手率', plainPct(c.turnoverRate), '按总股本')}
        ${kpi('量比(vs 20日均)', n(c.volRatio20, 2), isNum(c.volRatio20) && c.volRatio20 > 1.5 ? '明显放量' : '')}
        ${kpi('5日 vs 20日成交', isNum(c.amountRatio5v20) ? `${c.amountRatio5v20 > 0 ? '+' : ''}${c.amountRatio5v20}%` : '—', '')}
        ${kpi('量价配合', esc(c.priceVolume.pattern), `上涨日成交占比 ${plainPct(c.priceVolume.upDayTurnoverShare, 1)}`)}
        ${kpi('20日均成交额', money(c.avgTurnover20), `5日 ${money(ts.avgTurnover5)} / 60日 ${money(ts.avgTurnover60)}`)}
        ${kpi('振幅', plainPct(c.amplitude), '')}
        ${kpi('收盘位置', isNum(c.closePosition) ? `${c.closePosition}%` : '—', '0=最低 100=最高')}
        ${kpi('今日成交额分位', isNum(ts.turnoverPercentile120) ? `${ts.turnoverPercentile120}%` : '—', '近 120 个交易日')}
        ${kpi('连续放量天数', isNum(ts.volumeStreak) ? `${ts.volumeStreak} 天` : '—', '量比 > 1.3 连续天数')}
        ${kpi('近 10 日量价', esc(ts.divergence || '—'), `价格 ${pct(ts.priceChg10)} / 成交额 ${pct(ts.turnoverChg10)}`)}
        ${kpi('近 120 日涨停', `${ts.limitUpDays120 ?? 0} 次`, `跌停 ${ts.limitDownDays120 ?? 0} 次 · 炸板 ${ts.breakUpDays120 ?? 0} 次`)}
        ${kpi('龙虎榜上榜', dt.count ? `${dt.count} 次` : '近 4 日未上榜', dt.count ? `净额 ${money(dt.netValueSum)}` : '')}
        ${kpi('机构净买入', dt.count ? money(dt.orgNetSum) : '—', dt.count ? `游资 ${money(dt.hotMoneyNetSum)}` : '')}
      </div>
      ${(ts.limitEvents || []).length ? `
      <h3 style="font-size:13px;color:#143049;margin:18px 0 8px">近 120 日涨跌停 / 触板记录</h3>
      <div class="table-wrap">
        <table>
          <thead><tr><th>日期</th><th>类型</th><th>当日涨跌幅</th></tr></thead>
          <tbody>
          ${ts.limitEvents.map((e) => `<tr><td>${esc(e.date)}</td><td>${esc(e.type)}</td><td class="${cls(e.chg)}">${pct(e.chg)}</td></tr>`).join('')}
          </tbody>
        </table>
      </div>` : ''}
      ${dt.count ? `
      <h3 style="font-size:13px;color:#143049;margin:18px 0 8px">龙虎榜明细</h3>
      <div class="table-wrap">
        <table>
          <thead><tr><th>交易日</th><th>区间</th><th>净买入</th><th>净买占比</th><th>机构净额</th><th>游资净额</th><th>上榜原因</th></tr></thead>
          <tbody>
          ${dt.records.map((r) => `<tr>
            <td>${esc(r.tradeDate || '—')}</td>
            <td>${r.rangeDays || 1} 日</td>
            <td class="${cls(r.netValue)}">${money(r.netValue)}</td>
            <td class="${cls(r.netRate)}">${plainPct((r.netRate || 0) * 100)}</td>
            <td class="${cls(r.orgNetValue)}">${money(r.orgNetValue)}</td>
            <td class="${cls(r.hotMoneyNetValue)}">${money(r.hotMoneyNetValue)}</td>
            <td>${esc(r.limitReason || '—')}</td>
          </tr>`).join('')}
          </tbody>
        </table>
      </div>` : '<div class="badge-note">最近 4 个交易日未进入龙虎榜。龙虎榜为交易所披露的异动席位数据，未上榜不代表无大资金活动。</div>'}`;
  }

  function renderPopularity(d) {
    const p = d.popularity;
    const ls = p.limitStatus || {};
    const lr = p.limitRecord || {};
    el('sec-popularity').innerHTML = `${cardTitle('市场热度', '热股榜排名 + 近 120 日热度轨迹 + 成交额全市场分位 + 涨跌停与封板状态')}
      <div class="kpi-grid" style="margin-bottom:18px">
        ${kpi('涨跌停状态', ls.label ? esc(ls.label) : '未触板', isNum(ls.limitPct) ? `涨跌停幅度 ${ls.limitPct}%` : '', ls.isLimitUp ? 'bad' : ls.isLimitDown ? 'good' : '')}
        ${isNum(lr.continueDayCount) ? kpi('封板梯队', esc(lr.continueDayText || `${lr.continueDayCount} 连板`), isNum(lr.limitUpTime) || lr.limitUpTime ? `首次封板 ${esc(lr.limitUpTime || lr.firstSealTime || '—')}` : '') : ''}
        ${isNum(lr.sealMoney) ? kpi('封单金额', money(lr.sealMoney), `最大封单 ${money(lr.maxSealMoney)}`) : ''}
        ${isNum(lr.openTimes) ? kpi('开板次数', `${lr.openTimes} 次`, lr.openTimes > 2 ? '封板不稳' : '') : ''}
        ${kpi('今日热度排名', p.rankToday ? `#${p.rankToday}` : '—', p.inTop30Today ? '进入热股榜 TOP30' : (p.rankToday ? '近期上榜' : '未进入统计'))}
        ${kpi('飙升榜排名', p.skyrocketRank ? `#${p.skyrocketRank}` : '未上榜', isNum(p.skyrocketHeat) ? `热度值 ${Number(p.skyrocketHeat).toLocaleString('zh-CN')}` : '')}
        ${kpi('热度值', isNum(p.heatToday) ? Number(p.heatToday).toLocaleString('zh-CN') : '—', '')}
        ${kpi('近 10 日平均排名', n(p.avgRank10, 1), '')}
        ${kpi('上榜 TOP50 天数', `${p.daysTop50} 天`, `TOP10 ${p.daysTop10} 天`)}
        ${kpi('成交额分位', isNum(p.turnoverPercentile) ? `${p.turnoverPercentile}%` : '—', '全市场')}
        ${kpi('涨幅分位', isNum(p.changePercentile) ? `${p.changePercentile}%` : '—', '今日全市场')}
        ${kpi('热度综合分', n(p.heatScore, 1), '0-100')}
      </div>
      ${lr.reason ? `<div class="badge-note" style="border-color:rgba(199, 119, 0, .35);color:#8a6300">涨停/异动原因（同花顺涨停池）：${esc(lr.reason)}${lr.date ? ` · 数据日 ${esc(lr.date)}` : ''}</div>` : ''}
      ${rankChart(p.trend)}`;
  }

  function renderRecent5(d) {
    const r = d.recent5;
    const s = r.summary;
    const sec = d.sector;
    const vsSector = isNum(sec.relative5)
      ? `${sec.relative5 >= 0 ? '跑赢' : '跑输'}板块 ${Math.abs(sec.relative5).toFixed(2)} 个百分点`
      : null;
    el('sec-recent5').innerHTML = `${cardTitle('近 5 个交易日盘面走势', `区间 ${esc(s.startDate || '—')} ~ ${esc(s.endDate || '—')} · 前复权口径`)}
      <div class="kpi-grid" style="margin-bottom:18px">
        ${kpi('5 日累计涨跌', pct(s.cumChangePct), vsSector || '—', cls(s.cumChangePct) === 'up' ? 'good' : cls(s.cumChangePct) === 'down' ? 'bad' : '')}
        ${kpi('涨跌天数', `${s.upDays} 涨 / ${s.downDays} 跌`, `平 ${s.flatDays} 天`)}
        ${kpi('累计成交额', money(s.cumTurnover), `日均 ${money(s.avgTurnover)}`)}
        ${kpi('平均振幅', plainPct(s.avgAmplitude), '')}
        ${kpi('区间最大回撤', plainPct(s.maxDrawdown), '收盘价口径', isNum(s.maxDrawdown) && s.maxDrawdown < -8 ? 'bad' : '')}
        ${kpi('量能趋势', isNum(s.volumeTrend) ? `${s.volumeTrend > 0 ? '+' : ''}${s.volumeTrend}%` : '—', '后 2 日 vs 前 2 日')}
      </div>
      ${candleChart(r.rows.map((x) => ({ date: x.date, open: x.open, high: x.high, low: x.low, close: x.close, volume: x.volume })), { height: 210 })}
      <div class="table-wrap" style="margin-top:16px">
        <table>
          <thead><tr><th>日期</th><th>开盘</th><th>最高</th><th>最低</th><th>收盘</th><th>涨跌幅</th><th>振幅</th><th>成交量</th><th>成交额</th><th>量比(vs5日)</th><th>收盘位置</th></tr></thead>
          <tbody>
          ${r.rows.map((x) => `<tr>
            <td>${esc(x.date)}</td>
            <td>${n(x.open)}</td>
            <td>${n(x.high)}</td>
            <td>${n(x.low)}</td>
            <td class="${cls(x.changePct)}">${n(x.close)}</td>
            <td class="${cls(x.changePct)}">${pct(x.changePct)}</td>
            <td>${plainPct(x.amplitude)}</td>
            <td>${vol(x.volume)}</td>
            <td>${money(x.turnover)}</td>
            <td>${n(x.volumeRatio5, 2)}</td>
            <td>${isNum(x.closePosition) ? `${x.closePosition}%` : '—'}</td>
          </tr>`).join('')}
          </tbody>
        </table>
      </div>
      <div class="badge-note">「收盘位置」= (收盘-最低)/(最高-最低)，衡量当日多空收盘强弱；「跑赢板块」为 5 日累计涨跌减去所属一级行业指数同期涨跌。</div>`;
  }

  function renderTech(d) {
    const t = d.trendTech;
    const sec = d.sector;
    el('sec-tech').innerHTML = `${cardTitle('技术形态与中期走势', '前复权日线 · 近 40 个交易日 K 线（紫线为 20 日均线）')}
      ${candleChart(t.candles, { height: 260 })}
      <div class="kpi-grid" style="margin-top:16px">
        ${kpi('均线状态', esc(t.state), `MA5 ${n(t.ma5)} / MA20 ${n(t.ma20)}`)}
        ${kpi('5 日涨幅', pct(t.ret5), '', cls(t.ret5) === 'up' ? 'good' : cls(t.ret5) === 'down' ? 'bad' : '')}
        ${kpi('20 日涨幅', pct(t.ret20), '')}
        ${kpi('60 日涨幅', pct(t.ret60), '')}
        ${kpi('年化波动率', plainPct(t.volatilityAnnual), '20 日收益率年化')}
        ${kpi('60 日最大回撤', plainPct(t.maxDrawdown60), '')}
        ${kpi('20 日支撑', n(t.support20), '区间最低')}
        ${kpi('20 日压力', n(t.resistance20), '区间最高')}
        ${kpi('60 日区间', `${n(t.low60)} ~ ${n(t.high60)}`, '')}
        ${kpi('板块 5 日', pct(sec.focus && sec.focus.ret5), esc((sec.focus && sec.focus.name) || '—'))}
      </div>
      ${(sec.industries || []).length ? `<div style="margin-top:16px">
        <h3 style="font-size:13px;color:#143049;margin:0 0 8px">所属行业板块当日表现</h3>
        <div class="tag-cloud">${sec.industries.map((i) => `<span class="tag">${esc(i.name)} <b class="${cls(i.changePct)}" style="font-family:var(--mono)">${pct(i.changePct)}</b></span>`).join('')}</div>
      </div>` : ''}`;
  }

  function renderPeers(d) {
    const u = d.universe || {};
    el('sec-peers').innerHTML = `${cardTitle('高度相似的 5 只股票', esc(d.narrative.peerText))}
      <div class="peer-grid">
        ${d.peers.map((p, i) => `
          <div class="peer-card" data-code="${esc(p.ticker)}">
            <div class="rank">#${i + 1}</div>
            <div class="pn">${esc(p.name)}</div>
            <div class="pc">${esc(p.thscode)}</div>
            <div class="sim"><div class="track"><div class="fill" style="width:${Math.max(4, p.similarity)}%"></div></div><div class="val">${p.similarity}</div></div>
            <div class="pm">
              <span class="${cls(p.changePct)}">${pct(p.changePct)}</span>
              <span>PE ${n(p.peTtm)}</span>
              <span>PB ${n(p.pb)}</span>
            </div>
            <div class="pm" style="margin-top:6px"><span>20日 ${pct(p.ret20)}</span><span>成交 ${money(p.turnover)}</span></div>
            <div class="dims">
              ${(p.detail || []).map((dt) => `<div class="dim"><span class="dl2">${esc(dt.label)}</span><span class="dt2"><i style="width:${Math.max(3, dt.score)}%"></i></span><span class="dv2">${dt.score}</span></div>`).join('')}
            </div>
            <div class="rs">${p.reasons.map((r) => `<span>· ${esc(r)}</span>`).join('')}</div>
          </div>`).join('') || '<p class="badge-note">样本不足，暂无法给出相似度排序。</p>'}
      </div>
      <div class="badge-note">相似度 = 股价节奏相关性 30% + 估值接近度 20% + 体量流动性 20% + 动量接近度 15% + 题材重合 15%（缺失维度自动归一）。可比池取自「${esc(u.label || '同行业')}」，共 ${isNum(u.size) ? u.size : 0} 只。点击任意卡片可直接分析该股。</div>`;
    el('sec-peers').querySelectorAll('.peer-card').forEach((node) => {
      node.addEventListener('click', () => {
        const code = node.getAttribute('data-code');
        if (code) runAnalysis(code, true);
      });
    });
  }

  function renderFooter(d) {
    const m = d.meta;
    el('footer').innerHTML = `
      <div><b>数据来源</b>：同花顺金融数据服务（hithink-finance）· ${(m.sources || []).join(' / ')}</div>
      <div><b>交易日</b>：${esc(m.tradeDate || '—')} · <b>复权</b>：前复权 · <b>生成时间</b>：${new Date(m.generatedAt).toLocaleString('zh-CN')}</div>
      <div><b>行业/概念索引</b>：${esc(m.membership && m.membership.status)}（产业 ${m.membership ? m.membership.industries : 0} 个 / 概念 ${m.membership ? m.membership.concepts : 0} 个）</div>
      ${(m.warnings || []).length ? `<div class="badge-note warn-note">数据提示：${m.warnings.map(esc).join('；')}</div>` : ''}
      <div style="margin-top:8px">${esc(m.disclaimer)}</div>`;
  }

  function render(d) {
    $("#marketView").hidden = true;
    $("#loadingState").hidden = true;
    $("#errorState").hidden = true;
    $("#result").hidden = false;
    $("#backBar").hidden = false;
    renderQuote(d);
    renderKeyFacts(d);
    renderScores(d);
    renderNarrative(d);
    renderFundamentals(d);
    renderTrends(d);
    renderDupont(d);
    renderPerformance(d);
    renderMoat(d);
    renderIndustry(d);
    renderValuation(d);
    renderCapital(d);
    renderPopularity(d);
    renderRecent5(d);
    renderTech(d);
    renderDividend(d);
    renderRisk(d);
    renderPeers(d);
    renderFooter(d);
    $("#statusBadge").classList.remove('busy');
    $("#statusText").textContent = `已分析 ${d.resolved.name}`;
    if (typeof initCollapse === "function") initCollapse();
  }

  /* ------------------------------ 首页：市场全景 ------------------------------ */
  const fmtYi = (v) => (isNum(v) ? `${(v / 1e8).toFixed(v >= 1e10 ? 0 : 1)}亿` : '—');

  function renderMarketHero(d) {
    const b = d.breadth;
    const l = d.limits;
    if (!b) {
      el('mkHero').innerHTML = '<div class="mk-skeleton">市场概览数据暂不可用</div>';
      return;
    }
    const total = b.total || 1;
    const upPct = (b.up / total) * 100;
    const flatPct = (b.flat / total) * 100;
    const downPct = (b.down / total) * 100;
    const maxBucket = Math.max(...b.buckets.map((x) => x.count), 1);

    el('mkHero').innerHTML = `
      <div class="mk-hero-top">
        <span class="mk-title">市场全景</span>
        <span class="mk-date">交易日 ${esc(d.tradeDate || '—')} · 更新 ${new Date(d.generatedAt).toLocaleTimeString('zh-CN')}</span>
        <button class="mk-refresh" id="mkRefresh">刷新</button>
      </div>
      <div class="mk-hero-body">
        <div class="mk-breadth">
          <div class="bk-num"><span class="up">${b.up}</span> <span style="font-size:14px;color:var(--text-mute)">涨</span> / <span class="down">${b.down}</span> <span style="font-size:14px;color:var(--text-mute)">跌</span></div>
          <div class="bk-sub">全市场 ${b.total} 只 · 上涨占比 ${b.upRatio}% · 平盘 ${b.flat}</div>
          <div class="bk-bar">
            <i class="u" style="width:${upPct}%"></i>
            <i class="f" style="width:${flatPct}%"></i>
            <i class="d" style="width:${downPct}%"></i>
          </div>
          <div class="bk-sub" style="margin-top:10px">平均涨幅 <b class="${cls(b.avg)}">${pct(b.avg)}</b> · 中位数 <b class="${cls(b.median)}">${pct(b.median)}</b></div>
        </div>

        <div class="mk-dist">
          ${b.buckets.map((x) => {
    const h = Math.max(2, (x.count / maxBucket) * 78);
    const color = x.label.includes('-') ? '#0d9b6c' : (x.label.includes('0~') || x.label.includes('3~') ? '#b7cbe8' : '#e11d33');
    return `<div class="col" title="${esc(x.label)}：${x.count} 只">
              <div class="cnt">${x.count}</div>
              <div class="bar" style="height:${h}px;background:${color};opacity:${x.count ? 0.9 : 0.25}"></div>
              <div class="lb">${esc(x.label)}</div>
            </div>`;
  }).join('')}
        </div>

        <div class="mk-kpis">
          ${[
            ['两市成交额', fmtYi(b.turnover), ''],
            ['涨停家数', l ? `${l.limitUpCount}` : '—', l ? `跌停 ${l.limitDownCount}` : ''],
            ['封板率', l && isNum(l.sealRate) ? `${l.sealRate}%` : '—', l ? `炸板 ${l.breakCount}` : ''],
            ['最高连板', l && isNum(l.highestBoard) ? `${l.highestBoard} 板` : '—', l ? `${(l.up || []).filter((x) => (x.continueCount || 1) >= 3).length} 只 3 板以上` : ''],
          ].map(([k, v, s]) => `<div class="mk-kpi"><div class="k">${k}</div><div class="v">${v}</div>${s ? `<div class="s">${s}</div>` : ''}</div>`).join('')}
        </div>
      </div>`;

    const btn = el('mkRefresh');
    if (btn) btn.addEventListener('click', () => loadMarket(true));
  }

  function renderMarketSectors(d) {
    const sectors = d.sectors;
    const boards = (sectors && sectors.boards) || {};
    const labels = (sectors && sectors.labels) || { l1: '一级行业', l2: '细分行业', concept: '概念板块' };
    const all = boards[state.sectorKind] || [];
    const kindTabs = [['l1', labels.l1], ['l2', labels.l2], ['concept', labels.concept]];
    const sortTabs = [['change', '涨幅榜'], ['turnover', '成交额榜']];
    if (!all.length) {
      el('mkSectors').innerHTML = `${cardTitle('热门板块', '板块行情聚合自同花顺指数快照')}<p class="badge-note">板块数据暂不可用（或行业/概念索引仍在构建）。</p>`;
      return;
    }
    const sorted = all.slice().sort((a, b) => (state.sectorSort === 'turnover'
      ? (b.turnover || 0) - (a.turnover || 0)
      : b.changePct - a.changePct));
    const items = sorted.slice(0, 12);
    const weakest = state.sectorSort === 'change'
      ? ((sectors.bottoms && sectors.bottoms[state.sectorKind]) || [])
      : [];

    el('mkSectors').innerHTML = `${cardTitle('热门板块', `按${state.sectorSort === 'change' ? '涨幅' : '成交额'}排序 · 共 ${(sectors.totals && sectors.totals[state.sectorKind]) || all.length} 个${esc(labels[state.sectorKind] || '')} · 点击查看成分股`)}
      <div class="mk-tabs">${kindTabs.map(([k, label]) => `<span class="mk-tab ${state.sectorKind === k ? 'on' : ''}" data-kind="${k}">${label}</span>`).join('')}
        <span style="width:8px"></span>
        ${sortTabs.map(([k, label]) => `<span class="mk-tab ${state.sectorSort === k ? 'on' : ''}" data-sort="${k}">${label}</span>`).join('')}
      </div>
      <div class="mk-sector-list">
        ${items.map((s, i) => `<div class="mk-sector" data-code="${esc(s.code)}">
          <div class="idx">${i + 1}</div>
          <div>
            <div class="nm">${esc(s.name)}<em>${s.memberCount} 只 · 涨 ${s.upCount}/跌 ${s.downCount}</em></div>
            <div class="lead">${s.leader ? `领涨 ${esc(s.leader.name)} <span class="${cls(s.leader.changePct)}">${pct(s.leader.changePct)}</span>` : '—'}</div>
          </div>
          <div>
            <div class="pct ${cls(s.changePct)}">${pct(s.changePct)}</div>
            <div class="amt">${fmtYi(s.turnover)}</div>
          </div>
        </div>`).join('')}
      </div>
      ${weakest.length ? `<div class="badge-note">板块跌幅前列：${weakest.map((s) => `<span class="${cls(s.changePct)}">${esc(s.name)} ${pct(s.changePct)}</span>`).join(' · ')}</div>` : ''}
      <div class="mk-detail" id="mkSectorDetail" hidden></div>`;

    el('mkSectors').querySelectorAll('.mk-tab[data-kind]').forEach((n) => n.addEventListener('click', () => {
      state.sectorKind = n.getAttribute('data-kind');
      renderMarketSectors(state.market);
    }));
    el('mkSectors').querySelectorAll('.mk-tab[data-sort]').forEach((n) => n.addEventListener('click', () => {
      state.sectorSort = n.getAttribute('data-sort');
      renderMarketSectors(state.market);
    }));
    el('mkSectors').querySelectorAll('.mk-sector').forEach((n) => n.addEventListener('click', () => {
      openSector(n.getAttribute('data-code'));
    }));
    if (state.sectorOpen) openSector(state.sectorOpen, true);
  }

  async function openSector(code, keepOpen) {
    const box = el('mkSectorDetail');
    if (!box) return;
    if (!keepOpen && state.sectorOpen === code && !box.hidden) {
      box.hidden = true;
      state.sectorOpen = null;
      return;
    }
    state.sectorOpen = code;
    box.hidden = false;
    box.innerHTML = '<p class="badge-note">正在加载板块成分股…</p>';
    try {
      const res = await fetch(`/api/market/sector?code=${encodeURIComponent(code)}`);
      const d = await res.json();
      if (!d.ok) throw new Error(errText(d, '加载失败'));
      box.innerHTML = `
        <div class="mk-detail-head">
          <h4>${esc(d.name || code)}</h4>
          <span class="sub">${d.memberCount} 只成分 · 涨 ${d.upCount} / 跌 ${d.downCount}</span>
          <span class="close" id="mkDetailClose">收起</span>
        </div>
        <div class="table-wrap" style="max-height:280px;overflow:auto">
          <table>
            <thead><tr><th>名称</th><th>现价</th><th>涨跌幅</th><th>成交额</th></tr></thead>
            <tbody>
            ${d.members.slice(0, 40).map((m) => `<tr class="mk-stock-row" data-code="${esc(m.ticker)}" style="cursor:pointer">
              <td>${esc(m.name)}</td>
              <td>${n(m.lastPrice)}</td>
              <td class="${cls(m.changePct)}">${pct(m.changePct)}</td>
              <td>${fmtYi(m.turnover)}</td>
            </tr>`).join('')}
            </tbody>
          </table>
        </div>`;
      const close = el('mkDetailClose');
      if (close) close.addEventListener('click', () => { box.hidden = true; state.sectorOpen = null; });
      box.querySelectorAll('.mk-stock-row').forEach((row) => row.addEventListener('click', () => {
        runAnalysis(row.getAttribute('data-code'), true);
      }));
    } catch (err) {
      box.innerHTML = `<p class="badge-note">板块成分加载失败：${esc(err.message)}</p>`;
    }
  }

  function renderMarketLimits(d) {
    const l = d.limits;
    if (!l) {
      el('mkLimits').innerHTML = `${cardTitle('连板梯队')}<p class="badge-note">涨停池数据暂不可用。</p>`;
      return;
    }
    const maxCount = Math.max(...(l.tiers || []).map((t) => t.count), 1);
    el('mkLimits').innerHTML = `${cardTitle('连板梯队', `${esc(l.date || '')} · 涨停 ${l.limitUpCount} 家 / 跌停 ${l.limitDownCount} 家 / 炸板 ${l.breakCount} 家`)}
      <div class="mk-tiers">
        ${(l.tiers || []).map((t) => `<div class="mk-tier">
          <div class="tl">${esc(t.label)}</div>
          <div class="tb"><i style="width:${Math.max(2, (t.count / maxCount) * 100)}%"></i></div>
          <div class="tc">${t.count}</div>
        </div>`).join('')}
      </div>
      <div class="mk-kpis" style="margin-top:14px">
        <div class="mk-kpi"><div class="k">封板率</div><div class="v">${isNum(l.sealRate) ? `${l.sealRate}%` : '—'}</div><div class="s">炸板率 ${isNum(l.breakRate) ? `${l.breakRate}%` : '—'}</div></div>
        <div class="mk-kpi"><div class="k">最高连板</div><div class="v">${isNum(l.highestBoard) ? `${l.highestBoard} 板` : '—'}</div><div class="s">${l.up && l.up[0] ? esc(l.up[0].name) : ''}</div></div>
      </div>
      <div class="badge-note">梯队取自连板天梯（2 板及以上）与涨停池家数推算的首板数量。</div>`;
  }

  function renderMarketPools(d) {
    const l = d.limits;
    const mkStockList = (items, valueOf, subOf, emptyText, limit = 10) => (items && items.length ? `<div class="mk-list">
        ${items.slice(0, limit).map((it, i) => `<div class="mk-item" data-code="${esc(it.ticker)}">
          <div class="r">${i + 1}</div>
          <div><div class="n">${esc(it.name)}</div><div class="t">${subOf(it)}</div></div>
          <div class="v">${valueOf(it)}</div>
        </div>`).join('')}
      </div>` : `<p class="badge-note">${emptyText}</p>`);

    el('mkUpPool').innerHTML = `${cardTitle('涨停板明细', l ? `共 ${l.limitUpCount} 家 · 按连板数与封单排序 · 点击进入个股分析` : '')}
      ${l ? mkStockList(l.up, (it) => `<span class="${cls(it.changePct)}">${it.continueText || `${it.continueCount} 板`}</span>`,
    (it) => `${esc(it.limitUpTime || '')}${it.sealMoney ? ` · 封单 ${fmtYi(it.sealMoney)}` : ''}${it.openTimes ? ` · 开板 ${it.openTimes} 次` : ''}${it.reason ? ` · ${esc(it.reason)}` : ''}`,
    '今日无涨停股', 10) : '<p class="badge-note">数据不可用</p>'}`;

    el('mkDownPool').innerHTML = `${cardTitle('跌停板', l ? `共 ${l.limitDownCount} 家` : '')}
      ${l ? mkStockList(l.down, (it) => `<span class="${cls(it.changePct)}">${pct(it.changePct)}</span>`,
    (it) => `${esc(it.lastLimitTime || it.firstLimitTime || '')}${isNum(it.turnoverRate) ? ` · 换手 ${plainPct(it.turnoverRate)}` : ''}`,
    '今日无跌停股', 8) : '<p class="badge-note">数据不可用</p>'}`;

    el('mkBreakPool').innerHTML = `${cardTitle('炸板股', l ? `共 ${l.breakCount} 家 · 按开板次数排序` : '')}
      ${l ? mkStockList(l.break, (it) => `<span class="${cls(it.changePct)}">${pct(it.changePct)}</span>`,
    (it) => `${isNum(it.openTimes) ? `开板 ${it.openTimes} 次` : ''}${it.lastSealTime ? ` · 最后封板 ${esc(it.lastSealTime)}` : ''}`,
    '今日无炸板股', 8) : '<p class="badge-note">数据不可用</p>'}`;

    ['mkUpPool', 'mkDownPool', 'mkBreakPool'].forEach((id) => {
      el(id).querySelectorAll('.mk-item').forEach((n) => n.addEventListener('click', () => runAnalysis(n.getAttribute('data-code'), true)));
    });
  }

  function renderMarketHot(d) {
    const h = d.hot || {};
    const cards = [];

    cards.push({ title: '热股榜', sub: '同花顺热股榜（日榜）', items: (h.hot || []).map((x) => ({
      code: x.ticker, name: x.name, sub: `热度 ${Number(x.heat || 0).toLocaleString('zh-CN')}`, value: `#${x.rank}`,
    })) });

    cards.push({ title: '飙升榜', sub: '关注度上升最快', items: (h.skyrocket || []).map((x) => ({
      code: x.ticker, name: x.name, sub: `热度 ${Number(x.heat || 0).toLocaleString('zh-CN')}`, value: `#${x.rank}`,
    })) });

    cards.push({ title: '龙虎榜净买入', sub: h.date ? `${h.date} 席位净买额` : '', items: (h.dragonTiger || []).map((x) => ({
      code: x.thscode, name: x.name, sub: `${x.rangeDays || 1} 日${x.limitReason ? ` · ${x.limitReason}` : ''}`, value: `<span class="${cls(x.netValue)}">${fmtYi(x.netValue)}</span>`,
    })) });

    cards.push({ title: '成交额榜', sub: '全市场资金关注度', items: (h.turnoverTop || []).map((x) => ({
      code: x.ticker, name: x.name, sub: '', value: `<span class="${cls(x.changePct)}">${pct(x.changePct)}</span> <span style="color:var(--text-mute)">${fmtYi(x.turnover)}</span>`,
    })) });

    el('mkHot').innerHTML = cards.map((c) => `<section class="card">
      ${cardTitle(c.title, c.sub)}
      ${c.items.length ? `<div class="mk-list">${c.items.slice(0, 10).map((it, i) => `<div class="mk-item" data-code="${esc(it.code)}">
        <div class="r">${i + 1}</div>
        <div><div class="n">${esc(it.name)}</div>${it.sub ? `<div class="t">${it.sub}</div>` : ''}</div>
        <div class="v">${it.value}</div>
      </div>`).join('')}</div>` : '<p class="badge-note">暂无数据</p>'}
    </section>`).join('');

    el('mkHot').querySelectorAll('.mk-item').forEach((n) => n.addEventListener('click', () => {
      runAnalysis(n.getAttribute('data-code'), true);
    }));
  }

  function renderMarketFoot(d) {
    const l = d.limits || {};
    el('mkFoot').innerHTML = `
      <div>数据来源：同花顺金融数据服务（hithink-finance）· 行情/板块指数快照 · 涨停池/跌停池/炸板池 · 连板天梯 · 热股榜/飙升榜 · 龙虎榜</div>
      <div>涨跌分布按个股当日涨跌幅分档（±9.8% 为极端档，0% 计入 0~3% 档），涨停/跌停家数以交易所涨停池为准；主板 10%、创业板/科创板 20%、北交所 30%、ST 5%。</div>
      <div>「领涨股」= 该板块成分股中当日涨幅最高者，成分来自同花顺行业/概念指数。点击任意股票名称可进入深度分析；以上均为数据描述，不构成投资建议。</div>`;
  }

  function renderMarket(d) {
    state.market = d;
    try {
      renderMarketHero(d);
      renderMarketSectors(d);
      renderMarketLimits(d);
      renderMarketPools(d);
      renderMarketHot(d);
      renderMarketFoot(d);
    } catch (err) {
      el('mkHero').innerHTML = `<div class="mk-skeleton">市场全景渲染失败：${esc(err.message)}</div>`;
    }
    // 顶部快捷标签：热股榜前三 + 固定样本
    const hot = (d.hot && d.hot.hot) || [];
    if (hot.length && $("#quickChips")) {
      $("#quickChips").innerHTML = hot.slice(0, 4).map((h) => `<span class="chip" data-code="${esc(h.ticker)}">${esc(h.name)}</span>`).join('')
        + '<span class="chip" data-code="600519">贵州茅台</span><span class="chip" data-code="300750">宁德时代</span>';
      $("#quickChips").querySelectorAll('.chip').forEach((node) => {
        node.addEventListener('click', () => runAnalysis(node.getAttribute('data-code'), true));
      });
    }
  }

  let marketLoading = false;
  async function loadMarket(force) {
    if (marketLoading) return;
    marketLoading = true;
    if (force && el('mkHero')) {
      el('mkHero').innerHTML = '<div class="mk-skeleton">正在刷新市场全景…</div>';
    }
    try {
      const params = new URLSearchParams({ kind: state.sectorKind, sortBy: state.sectorSort });
      const res = await fetch(`/api/market?${params.toString()}`);
      const d = await res.json();
      if (!d.ok) throw new Error(errText(d, '市场数据加载失败'));
      renderMarket(d);
    } catch (err) {
      if (el('mkHero')) el('mkHero').innerHTML = `<div class="mk-skeleton">市场全景加载失败：${esc(err.message)}<div style="margin-top:12px"><button class="btn-ghost" id="mkRetry">重试</button> <button class="btn-ghost" id="mkDiag">诊断</button></div><pre id="mkDiagOut" hidden style="margin-top:10px;white-space:pre-wrap;font-size:11px;line-height:1.6;opacity:.85"></pre></div>`;
    } finally {
      marketLoading = false;
    }
  }

  function showMarket() {
    $("#marketView").hidden = false;
    $("#result").hidden = true;
    $("#loadingState").hidden = true;
    $("#errorState").hidden = true;
    $("#backBar").hidden = true;
    $("#searchInput").value = '';
    if (!state.market) loadMarket();
    window.scrollTo({ top: 0, behavior: 'auto' });
    history.replaceState(null, '', location.pathname);
  }

/* ------------------------------ 手机端控制层 ------------------------------ */
  const STAGE_HINTS = [
    '解析股票代码',
    '拉取行情与 K 线',
    '读取三大报表',
    '计算多期指标',
    '解析行业与概念',
    '核对龙虎榜与涨跌停',
    '扫描同行业公司',
    '计算评分与风险',
  ];
  let timerId = null;
  let hintId = null;

  function updateUrl(query) {
    const next = `?q=${encodeURIComponent(query)}`;
    try {
      if (location.search !== next) history.pushState({ q: query }, '', next);
    } catch (e) { /* ignore */ }
  }

  function showLoading(query) {
    state.loading = true;
    $("#marketView").hidden = true;
    $("#result").hidden = true;
    $("#errorState").hidden = true;
    $("#backBar").hidden = true;
    $("#loadingState").hidden = false;
    $("#loadingTitle").textContent = `正在分析 ${query}`;
    $("#loadingStage").textContent = STAGE_HINTS[0];
    $("#statusText").textContent = '分析中';
    const t0 = Date.now();
    clearInterval(timerId);
    clearInterval(hintId);
    timerId = setInterval(() => {
      $("#loadingTimer").textContent = `${((Date.now() - t0) / 1000).toFixed(1)}s`;
    }, 100);
    let i = 0;
    hintId = setInterval(() => {
      i = Math.min(STAGE_HINTS.length - 1, i + 1);
      $("#loadingStage").textContent = STAGE_HINTS[i];
    }, 1200);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function showError(message, query) {
    state.loading = false;
    clearInterval(timerId);
    clearInterval(hintId);
    $("#marketView").hidden = true;
    $("#loadingState").hidden = true;
    $("#result").hidden = true;
    $("#errorState").hidden = false;
    $("#backBar").hidden = false;
    $("#errorMsg").textContent = message;
    $("#statusText").textContent = '分析失败';
    $("#errorRetry").onclick = () => runAnalysis(query, true);
  }

  async function runAnalysis(query, _stream, opts = {}) {
    if (!query) return;
    state.loading = true;
    state.query = query;
    showLoading(query);
    if (!opts.fromHistory) updateUrl(query);
    try {
      const res = await fetch(`/api/stock?q=${encodeURIComponent(query)}`);
      const json = await res.json();
      if (!json.ok) throw new Error(errText(json, '分析失败'));
      if (state.query !== query) return;
      state.data = json;
      state.loading = false;
      clearInterval(timerId);
      clearInterval(hintId);
      render(json);
    } catch (err) {
      if (state.query !== query) return;
      showError(err.message || '分析失败', query);
    }
  }

  /* ------------------------------ 章节折叠 ------------------------------ */
  function sectionsOf() {
    return Array.from(document.querySelectorAll('#result .card'));
  }

  function initCollapse() {
    sectionsOf().forEach((card, i) => {
      const h2 = card.querySelector('h2');
      if (!h2 || h2.dataset.accBound) return;
      h2.dataset.accBound = '1';
      h2.classList.add('acc-head');
      h2.addEventListener('click', () => card.classList.toggle('collapsed'));
      // 手机端：默认只展开前 3 个章节
      card.classList.toggle('collapsed', i > 2);
    });
    const all = el('expandAll');
    if (all) all.textContent = '展开全部';
  }

  function bindExpandAll() {
    const all = el('expandAll');
    if (!all) return;
    all.addEventListener('click', () => {
      const cards = sectionsOf();
      const anyOpen = cards.some((c) => !c.classList.contains('collapsed'));
      cards.forEach((c) => c.classList.toggle('collapsed', anyOpen));
      all.textContent = anyOpen ? '展开全部' : '收起全部';
    });
  }

  /* ------------------------------ 搜索 ------------------------------ */
  function showSuggest(items) {
    const box = $("#suggest");
    state.suggestItems = items;
    state.suggestIndex = -1;
    if (!items.length) { box.hidden = true; return; }
    box.innerHTML = items.map((it, i) => `
      <div class="suggest-item" data-i="${i}">
        <span class="nm">${esc(it.name)}</span>
        <span class="cd">${esc(it.ticker)}</span>
      </div>`).join('');
    box.hidden = false;
    box.querySelectorAll('.suggest-item').forEach((node) => {
      node.addEventListener('mousedown', (e) => {
        e.preventDefault();
        const it = items[Number(node.getAttribute('data-i'))];
        box.hidden = true;
        $("#searchInput").value = it.ticker;
        $("#searchInput").blur();
        runAnalysis(it.ticker, true);
      });
    });
  }

  let suggestTimer = null;
  let suggestSeq = 0;
  async function fetchSuggest(q) {
    const seq = ++suggestSeq;
    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
      const json = await res.json();
      if (seq !== suggestSeq) return;
      showSuggest(json.items || []);
    } catch (e) { /* ignore */ }
  }

  function bindSearch() {
    const input = $("#searchInput");
    input.addEventListener('input', () => {
      const v = input.value.trim();
      clearTimeout(suggestTimer);
      if (!v) { $("#suggest").hidden = true; return; }
      suggestTimer = setTimeout(() => fetchSuggest(v), 260);
    });
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const v = input.value.trim();
        if (v) {
          $("#suggest").hidden = true;
          input.blur();
          runAnalysis(v, true);
        }
      } else if (e.key === 'Escape') {
        $("#suggest").hidden = true;
      }
    });
    input.addEventListener('blur', () => setTimeout(() => { $("#suggest").hidden = true; }, 150));
    $("#searchBtn").addEventListener('click', () => {
      const v = input.value.trim();
      if (v) {
        $("#suggest").hidden = true;
        $("#searchInput").blur();
        runAnalysis(v, true);
      }
    });
  }

  /* ------------------------------ 状态条 ------------------------------ */
  function refreshStatus() {
    const m = state.market;
    if (!m) return;
    if (state.loading) return;
    const mem = m.membership || {};
    const parts = [];
    if (m.tradeDate) parts.push(`交易日 ${m.tradeDate}`);
    if (mem.status === 'running' && mem.progress) parts.push(`板块索引 ${mem.progress.done}/${mem.progress.total}`);
    else if (mem.status === 'ready' && mem.date) parts.push(`板块索引 ${mem.date}`);
    if (state.data && state.data.resolved) parts.push(`已分析 ${state.data.resolved.name}`);
    const text = parts.join(' · ');
    if (text && $("#statusText")) $("#statusText").textContent = text;
  }

  /* ------------------------------ 启动 ------------------------------ */
  // 加载失败时点「诊断」：把服务端自检信息摊开，免得只看到一句「加载失败」
  async function showDiag() {
    const box = el('mkDiagOut');
    if (!box) return;
    box.hidden = false;
    box.textContent = '正在读取诊断信息…';
    try {
      const res = await fetch('/api/diag');
      const d = await res.json();
      const mem = d.membership || {};
      const lines = [];
      lines.push(`Python ${d.python || '?'} · ${d.platform || ''}`);
      lines.push(`服务目录：${d.webDir || '?'}`);
      Object.keys(mem).forEach((k) => {
        const s = (mem[k] && mem[k].stats) || {};
        lines.push(`板块索引[${k}]：${s.status} · 日期 ${s.date || '-'} · 行业 ${s.industries || 0} / 概念 ${s.concepts || 0}`);
        lines.push(`  缓存目录：${mem[k].cacheDir || '-'}（文件 ${(mem[k].files || []).length} 个）`);
      });
      const envs = Object.keys(d.env || {}).map((k) => `${k}=${d.env[k]}`);
      if (envs.length) lines.push('环境：' + envs.join(' · '));
      if ((d.stockDiagLog || []).length) lines.push('后台任务：', ...d.stockDiagLog.slice(-6));
      if ((d.lastErrors || []).length) lines.push('最近错误：' + JSON.stringify(d.lastErrors.slice(-5)));
      box.textContent = lines.join('\n');
    } catch (err) {
      box.textContent = '诊断接口也失败了：' + err.message;
    }
  }


  /* 主题切换后重绘图表（theme.js 调用） */
  window.__rerenderCharts = () => {
    try {
      if (state.data) render(state.data);
    } catch (e) { /* 忽略 */ }
  };

  function init() {
    bindSearch();
    bindExpandAll();
    $("#backBtn").addEventListener('click', showMarket);
    // 市场全景加载失败时注入的「重试」/「诊断」按钮（事件委托）
    document.addEventListener('click', (e) => {
      const id = e.target && e.target.id;
      if (id === 'mkRetry') loadMarket(true);
      if (id === 'mkDiag') showDiag();
    });
    window.addEventListener('popstate', (ev) => {
      const q = (ev.state && ev.state.q) || new URLSearchParams(location.search).get('q');
      if (q) {
        $("#searchInput").value = q;
        state.loading = false;
        runAnalysis(q, true, { fromHistory: true });
      } else {
        state.loading = false;
        showMarket();
      }
    });
    const q = new URLSearchParams(location.search).get('q');
    if (q) {
      $("#searchInput").value = q;
      runAnalysis(q, true, { fromHistory: true });
    } else {
      loadMarket();
    }
    setInterval(refreshStatus, 2000);
    setInterval(() => {
      if (!document.hidden && !$("#marketView").hidden && !state.loading) loadMarket();
    }, 60 * 1000);
  }

  document.addEventListener('DOMContentLoaded', init);
})();
"""
