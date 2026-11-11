# -*- coding: utf-8 -*-
"""由 web/build_theme_assets.py 生成：APK 内嵌的主题切换资源（勿手改）"""

THEME_JS = r"""/* 主题切换（浅色 / 深色）：按钮固定在右下角，选择记在 localStorage */
(function () {
  'use strict';
  var KEY = 'yaogu.theme';
  var DARK = 'dark';
  var LIGHT = 'light';

  function links() {
    return Array.prototype.slice.call(document.querySelectorAll('link[data-theme-dark]'));
  }

  function apply(theme) {
    var dark = theme === DARK;
    if (document.body) document.body.classList.toggle('dark', dark);
    document.documentElement.setAttribute('data-theme', dark ? DARK : LIGHT);
    links().forEach(function (l) {
      // 用 media 开关：带 `media="not all"` 的样式表会被预加载但不生效，切换瞬间生效
      l.disabled = false;
      l.media = dark ? 'all' : 'not all';
    });
    var btn = document.getElementById('themeToggle');
    if (btn) {
      btn.textContent = dark ? '☀' : '☾';
      btn.setAttribute('aria-label', dark ? '切换到浅色' : '切换到深色');
      btn.title = dark ? '切换到浅色' : '切换到深色';
    }
  }

  function set(theme) {
    try { localStorage.setItem(KEY, theme); } catch (e) { /* 隐私模式忽略 */ }
    apply(theme);
    // 图表配色由 CSS 变量驱动，切换后主动让页面重绘一次（个股分析页）
    try {
      if (window.__rerenderCharts) window.__rerenderCharts();
    } catch (e) { /* 忽略 */ }
  }

  function stored() {
    try { return localStorage.getItem(KEY) || LIGHT; } catch (e) { return LIGHT; }
  }

  // 支持 ?theme=dark / ?theme=light 直接指定（便于分享链接与排查）
  function fromQuery() {
    try {
      var v = new URLSearchParams(location.search).get('theme');
      if (v === DARK || v === LIGHT) {
        try { localStorage.setItem(KEY, v); } catch (e) { /* 忽略 */ }
        return v;
      }
    } catch (e) { /* 忽略 */ }
    return null;
  }

  // 暴露给其它脚本
  window.__theme = { set: set, get: stored, isDark: function () { return stored() === DARK; } };

  function init() {
    if (!document.body) {
      document.addEventListener('DOMContentLoaded', init);
      return;
    }
    var btn = document.getElementById('themeToggle');
    if (!btn) {
      btn = document.createElement('button');
      btn.id = 'themeToggle';
      btn.type = 'button';
      btn.className = 'theme-toggle';
      document.body.appendChild(btn);
    }
    btn.addEventListener('click', function () {
      set(stored() === DARK ? LIGHT : DARK);
    });
    apply(stored());
  }

  // 尽早切一次，避免深色用户看到浅色闪屏
  apply(fromQuery() || stored());
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
"""

STOCK_DARK = r"""/* 由 _probe/make_dark_theme.py 生成：深色主题（浅色 stock.css / 雷达内联样式的反向映射） */
/* ============================================================
   大A小散 · 视觉系统 v2（统一设计语言）
   令牌 → 布局 → 组件 → 图表 → 市场全景 → 响应式
   规范：中性深色底 / 单一蓝色主色 / 语义涨跌色 / 8pt 间距 / 18px 卡片圆角
   ============================================================ */

/* ---------------- 1. 设计令牌 ---------------- */
:root {
  /* 表面层级：底 → 卡片 → 嵌套块 → 交互态 */
  --bg: #070a0f;
  --bg-soft: #0b1017;
  --panel: #0f141c;
  --panel-2: #141a24;
  --panel-3: #1a2330;

  /* 描边：全部为低对比发丝线 */
  --line: #232c3a;
  --line-soft: #181f29;

  /* 文本：三级灰阶 */
  --text: #eef3fa;
  --text-dim: #9aa7b9;
  --text-mute: #657180;

  /* 主色：单一蓝，仅用于强调与交互 */
  --accent: #4e8cff;
  --accent-2: #7fb0ff;
  --accent-weak: rgba(78, 140, 255, .12);

  /* 语义色：红涨绿跌（A 股习惯） */
  --up: #ff5468;
  --down: #16c784;
  --good: #16c784;
  --bad: #ff5468;
  --warn: #ffb020;

  /* 圆角 / 阴影 / 字体 */
  --radius-lg: 18px;
  --radius: 18px;
  --radius-sm: 12px;
  --radius-xs: 10px;
  --shadow: 0 18px 40px -28px rgba(9, 12, 18, .16);
  /* 图表配色（跟随浅色/深色主题） */
  --chart-grid: #1f2836;
  --chart-zero: #232c3a;
  --chart-axis: #5b6778;
  --chart-ink: #e6edf8;
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
  background: radial-gradient(120% 100% at 50% 0%, rgba(78, 140, 255, .10) 0%, transparent 62%);
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
  background: rgba(9, 12, 18, .92);
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
  background: linear-gradient(160deg, #1b2b47, #131a25);
  border: 1px solid #23314a;
  box-shadow: inset 0 1px 0 rgba(9, 12, 18, .06);
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
  box-shadow: 0 0 0 2px rgba(22, 199, 132, .16);
}
.brand-text .dot.busy {
  background: var(--warn);
  box-shadow: 0 0 0 2px rgba(255, 176, 32, .16);
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
  color: #04141c;
  font-weight: 650;
  background: linear-gradient(180deg, rgba(78, 140, 255, .14), rgba(78, 140, 255, .05));
  border-color: rgba(78, 140, 255, .34);
  box-shadow: 0 2px 10px -6px rgba(78, 140, 255, .5), inset 0 1px 0 rgba(9, 12, 18, .7);
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
  border-color: #2a4a72;
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
#searchInput::placeholder { color: #5b6778; }
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
  box-shadow: 0 24px 48px -24px rgba(9, 12, 18, .16);
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
.btn-ghost:active { color: var(--text); border-color: #2a4a72; background: var(--panel-3); }

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
.tag.accent { color: var(--accent-2); border-color: rgba(78, 140, 255, .32); background: var(--accent-weak); }
.tag.warn { color: var(--warn); border-color: rgba(255, 176, 32, .32); background: rgba(255, 176, 32, .1); }

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
  background: linear-gradient(180deg, var(--accent), rgba(78, 140, 255, .35));
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
  border: 2.5px solid #232c3a;
  border-top-color: var(--accent);
  animation: spin .85s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.stage-list { list-style: none; padding: 0; margin: 0 0 22px; display: flex; flex-wrap: wrap; gap: 8px; }
.stage-list li { font-size: 12px; color: var(--text-dim); background: var(--panel-2); border: 1px solid var(--line-soft); border-radius: 999px; padding: 5px 12px; }
.stage-list li.done { color: var(--good); border-color: rgba(22, 199, 132, .3); }
.stage-list li.active { color: var(--accent-2); border-color: rgba(78, 140, 255, .45); background: var(--accent-weak); }

.skeleton { display: grid; gap: 12px; }
.sk-block {
  height: 110px;
  border-radius: var(--radius);
  background: linear-gradient(100deg, #10161f 30%, #131a25 50%, #10161f 70%);
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
.warn-note { border-color: rgba(255, 176, 32, .3); color: #e7c27e; }

/* ---------------- 7. 行情卡 ---------------- */
.quote-card {
  position: relative;
  overflow: hidden;
  padding: 18px 16px 14px;
  margin-bottom: 12px;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background:
    radial-gradient(120% 120% at 100% 0%, rgba(78, 140, 255, .10) 0%, transparent 55%),
    linear-gradient(180deg, #131a25, #131a25);
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
.qc-stat { flex: 1 1 100px; padding: 9px 11px; background: #131a25; }
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
.bar-track { height: 6px; border-radius: 999px; background: #1a2330; overflow: hidden; }
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
  background: #10161f;
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
tr.self-row td { background: rgba(78, 140, 255, .08) !important; }

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
.kpi.good { border-color: rgba(22, 199, 132, .26); }
.kpi.warn { border-color: rgba(255, 176, 32, .26); }
.kpi.bad { border-color: rgba(255, 84, 104, .26); }

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
.moat-item.lv-偏强 { border-left-color: #16c784; }
.moat-item.lv-持平 { border-left-color: #4a5c72; }
.moat-item.lv-偏弱 { border-left-color: var(--warn); }
.moat-item.lv-弱 { border-left-color: var(--bad); }
.moat-item .idx { font-family: var(--mono); font-size: 11.5px; color: var(--text-mute); padding-top: 2px; }
.moat-item .ttl { display: flex; align-items: center; gap: 7px; flex-wrap: wrap; font-size: 13px; font-weight: 600; }
.moat-item .metric { font-family: var(--mono); font-size: 12px; color: var(--accent-2); }
.moat-item .ev { margin-top: 5px; font-size: 12px; line-height: 1.65; color: var(--text-dim); }

.lv-badge { font-size: 10.5px; padding: 1px 8px; border-radius: 7px; border: 1px solid currentColor; }
.lv-badge.s-强 { color: var(--good); }
.lv-badge.s-偏强 { color: #16c784; }
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
.risk-pill.alert { color: var(--bad); border-color: rgba(255, 84, 104, .38); background: rgba(255, 84, 104, .1); }
.risk-pill.watch { color: var(--warn); border-color: rgba(255, 176, 32, .38); background: rgba(255, 176, 32, .1); }
.risk-pill.ok { color: var(--good); border-color: rgba(22, 199, 132, .34); background: rgba(22, 199, 132, .08); }

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
.peer-card:active { border-color: #2a4a72; transform: scale(.995); }
.peer-card .rank {
  position: absolute; top: 0; right: 0;
  padding: 2px 8px;
  font-family: var(--mono); font-size: 10px;
  color: var(--text-mute);
  background: #1a2330;
  border-bottom-left-radius: 9px;
}
.peer-card .pn { font-size: 14.5px; font-weight: 650; }
.peer-card .pc { margin-top: 2px; font-family: var(--mono); font-size: 11px; color: var(--text-mute); }
.peer-card .sim { display: flex; align-items: center; gap: 8px; margin: 11px 0 9px; }
.peer-card .sim .track { flex: 1; height: 4px; border-radius: 999px; background: #1a2330; overflow: hidden; }
.peer-card .sim .fill { height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent-2)); }
.peer-card .sim .val { font-family: var(--mono); font-size: 12px; color: var(--accent-2); }
.peer-card .pm { display: flex; gap: 12px; flex-wrap: wrap; font-family: var(--mono); font-size: 11.5px; color: var(--text-dim); }
.peer-card .rs { display: grid; gap: 3px; margin-top: 9px; }
.peer-card .rs span { font-size: 11px; line-height: 1.5; color: var(--text-mute); }
.peer-card .dims { display: grid; gap: 5px; margin-top: 9px; }
.peer-card .dim { display: grid; grid-template-columns: 50px minmax(0, 1fr) 28px; align-items: center; gap: 6px; }
.peer-card .dim .dl2 { font-size: 10px; color: var(--text-mute); }
.peer-card .dim .dt2 { height: 3px; border-radius: 999px; background: #1a2330; overflow: hidden; }
.peer-card .dim .dt2 i { display: block; height: 100%; border-radius: 999px; background: linear-gradient(90deg, #3c5f92, var(--accent-2)); }
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
    radial-gradient(120% 120% at 100% 0%, rgba(78, 140, 255, .08) 0%, transparent 55%),
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
.mk-refresh:active { color: var(--text); border-color: #2a4a72; }

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
  background: #1a2330;
}
.mk-breadth .bk-bar i { display: block; height: 100%; }
.mk-breadth .bk-bar .u { background: var(--up); }
.mk-breadth .bk-bar .f { background: #3b4656; }
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
  border-color: rgba(78, 140, 255, .45);
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
.mk-sector:active { border-color: #2a4a72; background: var(--panel-3); }
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
.mk-tier .tb { height: 14px; border-radius: 7px; background: #1a2330; overflow: hidden; }
.mk-tier .tb i { display: block; height: 100%; border-radius: 7px; background: linear-gradient(90deg, rgba(255, 84, 104, .55), rgba(255, 84, 104, .95)); }
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
.mk-item:active { border-color: #2a4a72; background: var(--panel-3); }
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
    grid-template-columns: 260px auto minmax(280px, 480px);
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
  .nav-btn:hover { border-color: #2a4a72; color: var(--text); }
  .search-box { margin-top: 0; position: relative; width: 100%; justify-self: end; }
  #searchInput { font-size: 14px; padding: 6px 0; }
  .suggest { left: 0; right: 0; top: calc(100% + 8px); }
  .suggest-item:active { background: none; }
  .suggest-item:hover { background: #16233a; }

  /* ---------------- 主体容器 ---------------- */
  main { max-width: 1400px; margin: 0 auto; padding: 18px 26px 56px; }

  /* ---------------- 卡片与文字密度 ---------------- */
  .card { padding: 16px 18px 18px; }
  .card > h2 { font-size: 15px; }
  .card .sub { font-size: 12px; }
  table { font-size: 12.5px; }
  thead th, tbody td { padding: 8px 11px; }
  tbody tr:hover { background: #0b1017; }
  .fact { padding: 11px 13px; }
  .facts { grid-template-columns: repeat(auto-fit, minmax(168px, 1fr)); gap: 10px; }

  .quote-card { padding: 18px 22px 16px; }
  .qc-name { font-size: 23px; }
  .qc-price .p { font-size: 34px; }
  .qc-stats { grid-template-columns: repeat(auto-fit, minmax(124px, 1fr)); }
  .qc-stat .v { font-size: 13.5px; }

  .back-bar { margin-bottom: 0; }
  .btn-ghost { flex: none; padding: 8px 18px; }
  .btn-ghost:hover { border-color: #2a4a72; color: var(--text); }

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
  .mk-sector:hover, .mk-item:hover { background: #16233a; }
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

/* ---------------- 主题切换按钮（右下角悬浮） ---------------- */
.theme-toggle {
  position: fixed;
  right: 14px;
  bottom: calc(14px + env(safe-area-inset-bottom, 0px));
  z-index: 90;
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  border: 1px solid var(--line);
  background: var(--panel);
  color: var(--text-dim);
  font-size: 17px;
  line-height: 1;
  box-shadow: 0 12px 26px -16px rgba(9, 12, 18, .6);
  cursor: pointer;
  transition: color .15s, border-color .15s, transform .15s, background .15s;
}
.theme-toggle:hover { color: var(--accent); border-color: var(--accent); transform: translateY(-1px); }
.theme-toggle:active { transform: scale(.94); }
"""

RADAR_DARK = r"""/* 由 _probe/make_dark_theme.py 生成：深色主题（浅色 stock.css / 雷达内联样式的反向映射） */

/* ============================================================
   大A小散 · 视觉系统 v2（雷达页）— 与个股分析页共用同一套令牌
   ============================================================ */
:root{
  --bg:#070a0f; --bg-soft:#0b1017;
  --card:#0f141c; --card-2:#141a24; --card-3:#1a2330;
  --line:#232c3a; --line-soft:#181f29;
  --fg:#eef3fa; --dim:#9aa7b9; --muted:#657180;
  --hit:#ff5468; --ok:#16c784; --warn:#ffb020; --accent:#4e8cff; --accent-2:#7fb0ff;
  --up:#ff5468; --down:#16c784;
  --accent-weak:rgba(78, 140, 255, .12);
  --radius:18px; --radius-sm:12px; --radius-xs:10px;
  --mono:ui-monospace,"SF Mono","Roboto Mono","Droid Sans Mono",Menlo,Consolas,monospace;
  --font:-apple-system,"SF Pro Text","PingFang SC","HarmonyOS Sans SC","MiSans","Noto Sans SC","Microsoft YaHei",system-ui,sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0}
[hidden]{display:none!important}
html{-webkit-text-size-adjust:100%}
body{
  background:var(--bg);color:var(--fg);font:14px/1.55 var(--font);
  -webkit-font-smoothing:antialiased;min-height:100vh;padding:0;
}
body::before{
  content:"";position:fixed;inset:0 0 auto 0;height:300px;pointer-events:none;z-index:0;
  background:radial-gradient(120% 100% at 50% 0%,rgba(78, 140, 255, .10) 0%,transparent 62%);
}
h1,h2,h3,h4{font-weight:600;letter-spacing:-.1px}
a{color:inherit;text-decoration:none}
button{font-family:inherit;-webkit-tap-highlight-color:transparent;cursor:pointer}

/* ---------- 顶栏 ---------- */
.bar{
  position:sticky;top:0;z-index:60;
  padding:12px 16px 10px;
  background:rgba(9, 12, 18, .92);
  -webkit-backdrop-filter:saturate(160%) blur(20px);backdrop-filter:saturate(160%) blur(20px);
  border-bottom:1px solid var(--line-soft);
}
.bar-top{display:flex;align-items:center;gap:10px;padding-right:50px}
.brand{display:flex;align-items:center;gap:10px;min-width:0}
.logo{
  display:grid;place-items:center;width:32px;height:32px;flex:none;border-radius:10px;
  background:linear-gradient(160deg,#1b2b47,#131a25);border:1px solid #23314a;
  box-shadow:inset 0 1px 0 rgba(9, 12, 18, .06);
}
.brand-text h1{font-size:17px;font-weight:650;line-height:1.25;letter-spacing:.2px}
.brand-sub{font-size:10.5px;color:var(--muted);margin-top:2px;white-space:nowrap}
.bar-badges{margin-left:auto;display:flex;gap:6px;flex:none}
.badge{
  display:inline-flex;align-items:center;gap:4px;padding:3px 9px;border-radius:999px;
  border:1px solid var(--line);background:var(--card-2);color:var(--dim);
  font-size:10.5px;line-height:1.5;white-space:nowrap;
}
.badge.live{color:var(--ok);border-color:rgba(22, 199, 132, .34);background:rgba(22, 199, 132, .1)}
.badge.live::before{content:"";width:5px;height:5px;border-radius:50%;background:var(--ok);box-shadow:0 0 0 2px rgba(22, 199, 132, .16)}
.badge.hit{color:var(--hit);border-color:rgba(255, 84, 104, .34);background:rgba(255, 84, 104, .1)}

.appnav{
  display:flex;gap:2px;margin-top:11px;padding:3px;
  background:var(--bg-soft);border:1px solid var(--line-soft);border-radius:13px;
}
.nav-btn{
  flex:1;text-align:center;padding:8px 0;border:1px solid transparent;border-radius:10px;
  font-size:13px;line-height:1.2;color:var(--dim);background:transparent;white-space:nowrap;
  transition:color .15s,background .15s,border-color .15s;
}
.nav-btn.on{
  color:#04141c;font-weight:650;
  background:linear-gradient(180deg,rgba(78, 140, 255, .14),rgba(78, 140, 255, .05));
  border-color:rgba(78, 140, 255, .34);
  box-shadow:0 2px 10px -6px rgba(78, 140, 255, .5),inset 0 1px 0 rgba(9, 12, 18, .7);
}

/* ---------- 数据条 ---------- */
.panel-top{padding:12px 16px 0;position:relative;z-index:1}
.stats{display:flex;flex-wrap:wrap;gap:5px 14px;align-items:baseline}
.stat{display:flex;align-items:baseline;gap:5px}
.stat i{font-style:normal;font-size:10.5px;color:var(--muted)}
.stat b{font-family:var(--mono);font-size:11.5px;font-weight:500;color:var(--fg)}
.stat b.hl{color:var(--hit)}
.stat b.ok{color:var(--ok)}
.stat b.warn{color:var(--warn)}
.bar-meta{margin-top:6px;font-size:10.5px;color:var(--muted);font-family:var(--mono)}
.bar-meta b{color:var(--dim);font-weight:500}

.warnbar{
  margin:10px 16px 0;padding:10px 12px;border-radius:var(--radius-sm);
  border:1px solid rgba(255, 176, 32, .28);background:rgba(255, 176, 32, .08);
  color:#e7c27e;font-size:11.5px;line-height:1.7;
}
.chips{display:flex;flex-wrap:wrap;gap:6px;padding:10px 16px 0}
.chip{
  display:inline-flex;align-items:center;gap:5px;padding:4px 10px;border-radius:999px;
  border:1px solid var(--line);background:var(--card-2);color:var(--dim);
  font-size:11px;line-height:1.5;
}
.chip.hot{color:#ffb3bd;border-color:rgba(255, 84, 104, .3);background:rgba(255, 84, 104, .1)}
.chip.ice{color:#9ae6c4;border-color:rgba(22, 199, 132, .3);background:rgba(22, 199, 132, .1)}
.chip.dim{color:var(--muted)}
.chip b{font-family:var(--mono)}

/* ---------- 布局 ---------- */
main{position:relative;z-index:1;padding:12px 12px 8px}
.cols{display:grid;grid-template-columns:minmax(0,1fr);gap:12px}
.card{
  background:var(--card);border:1px solid var(--line-soft);border-radius:var(--radius);
  padding:16px;min-width:0;
}
.card h2{
  display:flex;align-items:center;gap:9px;font-size:15px;font-weight:600;margin:0 0 2px;flex-wrap:wrap;
}
.card h2::before{
  content:"";width:3px;height:14px;border-radius:2px;flex:none;
  background:linear-gradient(180deg,var(--accent),rgba(78, 140, 255, .35));
}
.tick{font-size:11px;line-height:1.65;color:var(--muted);font-weight:400}
.sub{
  margin:14px 0 8px;font-size:11.5px;color:var(--dim);
  display:flex;align-items:center;gap:6px;
}
.sub::before{content:"";width:3px;height:3px;border-radius:50%;background:var(--muted);flex:none}
.subhead{
  display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;
  margin:16px 0 8px;padding-top:14px;border-top:1px solid var(--line-soft);
  font-size:13px;font-weight:600;color:var(--fg);
}
.empty{
  padding:22px 12px;text-align:center;font-size:11.5px;line-height:1.8;color:var(--muted);
}
.err{font-size:11px;color:var(--hit);margin-top:8px;line-height:1.6}

/* ---------- 时间线 / 事件 ---------- */
.event{
  display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;
  padding:10px 2px;border-bottom:1px solid var(--line-soft);
  font-size:12px;
}
.event:last-child{border-bottom:none}
.event .time{font-family:var(--mono);font-size:11px;color:var(--muted);min-width:38px}
.event .nm{font-size:13px;font-weight:650;color:var(--fg)}
.event .nm.hl{color:var(--hit)}
.event .nm.dp{color:var(--accent-2)}
.event .up{color:var(--up)}
.event .dp{color:var(--accent-2)}

/* ---------- 表格 ---------- */
.tbl{overflow-x:auto;-webkit-overflow-scrolling:touch}
.tbl table{width:max-content;min-width:100%}
.sfpanel td.nm{white-space:nowrap}
table{width:100%;border-collapse:collapse;font-size:12px;font-family:var(--mono);font-variant-numeric:tabular-nums}
th{
  position:sticky;top:0;z-index:1;text-align:right;font-weight:500;font-size:10.5px;
  color:var(--muted);padding:8px 8px;white-space:nowrap;
  background:#10161f;border-bottom:1px solid var(--line);font-family:var(--font);
}
th:first-child{text-align:left}
td{
  padding:8px;text-align:right;white-space:nowrap;color:var(--fg);
  border-bottom:1px solid var(--line-soft);
}
td:first-child{text-align:left}
td.nm{font-family:var(--font);color:var(--dim);text-align:left;white-space:normal}
td.sc{color:var(--accent-2);font-weight:600}
td.rr{font-family:var(--font);color:var(--muted);font-size:11px;max-width:160px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-align:left}
tr:last-child td{border-bottom:none}
tbody tr:active td{background:var(--card-3)}
.up{color:var(--up)}
.down{color:var(--down)}
td.empty{text-align:center;color:var(--muted);font-family:var(--font)}

/* 候选表：手机端转卡片 */
@media (max-width:679px){
  /* 只有候选表转卡片、不需要横向滚动；其它宽表（板块资金等）仍要 .tbl 的横向滚动，
     否则会把整页撑宽（实测 390px 下页面宽 495px，可以左右滑动） */
  .tbl{overflow-x:auto}
  table.cand{display:block}
  table.cand thead{display:none}
  table.cand tbody{display:grid;gap:8px}
  table.cand tr{
    display:grid;grid-template-columns:minmax(0,1fr) auto;
    column-gap:10px;row-gap:3px;align-items:center;
    padding:12px 14px;border-radius:14px;background:var(--card-2);
    border:1px solid var(--line-soft);
  }
  table.cand tr:active{border-color:#2a4a72}
  table.cand tr.hit-row{border-color:rgba(255, 84, 104, .35);background:rgba(255, 84, 104, .06)}
  table.cand td{border:none;padding:0;white-space:nowrap;word-break:keep-all}
  table.cand td[data-label="名称"]{grid-column:1;grid-row:1;text-align:left;font:650 15px/1.3 var(--font);color:var(--fg)}
  table.cand td[data-label="代码"]{grid-column:1;grid-row:2;text-align:left;font:11px/1.4 var(--mono);color:var(--muted);letter-spacing:.4px}
  table.cand td[data-label="时间"]{grid-column:1;grid-row:3;text-align:left;font:11px/1.4 var(--mono);color:var(--muted)}
  table.cand td[data-label="评分"]{
    grid-column:2;grid-row:1;text-align:right;font:700 18px/1.2 var(--mono);color:var(--accent-2);
  }
  table.cand td[data-label="状态"]{grid-column:2;grid-row:2;text-align:right;font-size:11.5px;min-width:max-content}
  table.cand td[data-label="状态"],
  table.cand td[data-label="状态"] *{white-space:nowrap}
  table.cand td[data-label="开盘涨幅"]{grid-column:1;grid-row:3;text-align:left;font-size:11.5px}
  table.cand td[data-label="现涨幅"]{grid-column:2;grid-row:3;text-align:right;font-size:11.5px}
  table.cand td[data-label="开盘涨幅"]::before,
  table.cand td[data-label="现涨幅"]::before{font-size:10px;opacity:.62;font-family:var(--font);margin-right:3px}
  table.cand td[data-label="开盘涨幅"]::before{content:"开盘"}
  table.cand td[data-label="现涨幅"]::before{content:"现"}
  table.cand td[data-label="成色"],
  table.cand td[data-label="题材"],
  table.cand td[data-label="T-1涨幅"],
  table.cand td[data-label="T-1额(亿)"],
  table.cand td[data-label="量比"],
  table.cand td[data-label="今日开盘"],
  table.cand td[data-label="最新价"]{display:none}
}

/* ---------- 资金矩阵 ---------- */
.sfbtn{
  padding:4px 10px;border-radius:9px;border:1px solid var(--line);
  background:var(--card-2);color:var(--dim);font-size:11.5px;margin-left:auto;
}
.sfbtn:active{color:var(--fg);border-color:#2a4a72}
.sftabs{display:flex;gap:6px;flex-wrap:nowrap;overflow-x:auto;margin:10px 0 12px;padding-bottom:2px;scrollbar-width:none;-webkit-overflow-scrolling:touch}
.sftabs::-webkit-scrollbar{display:none}
.sftab{
  flex:0 0 auto;padding:6px 12px;border-radius:10px;border:1px solid var(--line);
  background:var(--card-2);color:var(--dim);font-size:11.5px;white-space:nowrap;
}
.sftab.on{color:var(--accent-2);border-color:rgba(78, 140, 255, .45);background:var(--accent-weak);font-weight:600}
.cols2{display:grid;grid-template-columns:minmax(0,1fr);gap:14px}
.sfpanel table{width:100%}
.qbox{
  padding:12px 13px;border:1px solid var(--line-soft);border-radius:var(--radius-sm);background:var(--card-2);
}
.qbox h4{font-size:12.5px;margin-bottom:4px}
.qsub{font-size:11px;line-height:1.6;color:var(--muted);margin-bottom:8px}

/* 横条图 */
.bars{display:grid;gap:7px}
.bar-row{display:grid;grid-template-columns:88px minmax(0,1fr) 62px;gap:8px;align-items:center}
.bar-name{font-size:11px;color:var(--dim);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bar-track{position:relative;height:7px;border-radius:999px;background:#1a2330;overflow:hidden}
.bar-fill{position:absolute;top:0;height:100%;border-radius:999px}
.bar-fill.pos{background:linear-gradient(90deg,rgba(255, 84, 104, .55),rgba(255, 84, 104, .95))}
.bar-fill.neg{background:linear-gradient(90deg,rgba(22, 199, 132, .95),rgba(22, 199, 132, .55))}
.bar-zero{position:absolute;left:50%;top:-2px;bottom:-2px;width:1px;background:#2b3646}
.bar-thr{position:absolute;top:-3px;bottom:-3px;width:1px;border-left:1px dashed rgba(255, 176, 32, .75)}
.bar-val{font-family:var(--mono);font-size:11px;text-align:right}
.bar-val.pos{color:var(--hit)}
.bar-val.neg{color:var(--ok)}

/* 标签 */
.tag{
  display:inline-block;padding:1px 7px;border-radius:7px;border:1px solid var(--line);
  background:var(--card-3);color:var(--dim);font-size:10.5px;line-height:1.7;
}
.tag.lhb{color:var(--warn);border-color:rgba(255, 176, 32, .3)}
.tag.org{color:var(--accent-2);border-color:rgba(78, 140, 255, .3)}
.tag.up{color:var(--hit);border-color:rgba(255, 84, 104, .3)}
.res{font-size:10.5px;color:var(--accent-2)}

/* ---------- 弹窗（手机端底部抽屉） ---------- */
.modal-mask{
  position:fixed;inset:0;z-index:80;background:rgba(9, 12, 18, .88);
  -webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);
  display:flex;align-items:flex-end;justify-content:center;
}
.modal{
  width:100%;max-width:520px;max-height:86vh;overflow-y:auto;-webkit-overflow-scrolling:touch;
  background:var(--card);border:1px solid var(--line);
  border-radius:20px 20px 0 0;padding:16px 16px calc(16px + env(safe-area-inset-bottom));
  box-shadow:0 -20px 48px -24px rgba(9, 12, 18, .16);
}
.modal-head{
  display:flex;align-items:center;gap:10px;padding-bottom:12px;margin-bottom:6px;
  border-bottom:1px solid var(--line-soft);font-size:15px;font-weight:650;
}
.modal-close{
  margin-left:auto;width:28px;height:28px;border-radius:9px;border:1px solid var(--line);
  background:var(--card-2);color:var(--dim);font-size:13px;line-height:1;
}
.m-row{display:flex;align-items:baseline;gap:12px;padding:8px 2px;border-bottom:1px solid var(--line-soft);font-size:12.5px}
.m-row:last-child{border-bottom:none}
.m-row .k{color:var(--muted);flex:none;min-width:88px}
.m-row .v{margin-left:auto;text-align:right;font-family:var(--mono);color:var(--fg);white-space:normal}

footer{
  padding:16px 16px calc(24px + env(safe-area-inset-bottom));
  font-size:11px;line-height:1.85;color:var(--muted);
  border-top:1px solid var(--line-soft);margin-top:4px;
}

/* 命中闪烁 */
@keyframes flashBorder{
  0%{box-shadow:0 0 0 0 rgba(255, 84, 104, .35)}
  100%{box-shadow:0 0 0 8px rgba(255, 84, 104, 0)}
}
.card.flash{animation:flashBorder .95s ease-out 1}

/* ---------- 桌面 ---------- */
@media (min-width:680px){
  .bar{padding:14px 24px 12px}
  .panel-top{padding:14px 24px 0}
  .chips{padding:12px 24px 0}
  .warnbar{margin:12px 24px 0}
  main{padding:16px 28px 10px;max-width:none;margin:0}
  .cols2{grid-template-columns:minmax(0,1fr)}
  .sfquad{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
  .card{padding:20px 22px}
  .modal{border-radius:18px;margin:auto;max-height:80vh}
  .modal-mask{align-items:center}
  .event{font-size:12.5px;padding:11px 2px}
  table.cand{font-size:11.5px}
  table.cand th,table.cand td{padding:8px 5px}
  table.cand th{font-size:10px}
}
@media (min-width:900px){
  /* 顶部三段网格：品牌(260px) | 导航 Tab | 状态徽标 —— 与个股分析 / 复盘页完全一致 */
  .bar{
    display:grid;grid-template-columns:260px auto minmax(0,1fr);
    align-items:center;gap:24px;padding:12px 26px;min-height:76px;
  }
  .bar-top{display:contents}
  .brand{grid-column:1;grid-row:1;min-width:0}
  .appnav{
    grid-column:2;grid-row:1;justify-self:start;
    margin-top:0;gap:6px;padding:3px;max-width:none;
  }
  .bar-badges{grid-column:3;grid-row:1;justify-self:end;margin-left:0}
  .nav-btn{flex:none;padding:7px 20px;border-radius:10px;font-size:13px}
}
@media (min-width:1280px){
  .cols{grid-template-columns:minmax(0,1.15fr) minmax(0,2fr);align-items:start}
  .cols2{grid-template-columns:repeat(2,minmax(0,1fr))}
  .sfquad{grid-template-columns:repeat(2,minmax(0,1fr))}
}

/* ---------- 主题切换按钮 ---------- */
.theme-toggle{position:fixed;right:14px;bottom:calc(14px + env(safe-area-inset-bottom,0px));z-index:90;width:42px;height:42px;display:grid;place-items:center;border-radius:50%;border:1px solid var(--line);background:var(--card);color:var(--dim);font-size:17px;line-height:1;cursor:pointer;box-shadow:0 12px 26px -16px rgba(9, 12, 18, .6);transition:color .15s,border-color .15s,transform .15s}
.theme-toggle:hover{color:var(--accent);border-color:var(--accent);transform:translateY(-1px)}
.theme-toggle:active{transform:scale(.94)}
"""
