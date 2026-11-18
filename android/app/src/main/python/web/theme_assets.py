# -*- coding: utf-8 -*-
"""由 web/build_theme_assets.py 生成：APK 内嵌的主题切换资源（勿手改）"""

THEME_JS = r"""/* 主题切换（浅色 / 深色）：入口在设置面板里（桌面端顶栏齿轮按钮；手机端走原生设置页） */
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
    // 移动端浏览器的地址栏 / 原生控件跟着主题走：默认主题是浅色，
    // 别再让浅色用户顶着一条深色地址栏（App 内 WebView 没有地址栏，这里是浏览器场景）
    var cs = document.getElementById('metaColorScheme');
    if (cs) cs.setAttribute('content', dark ? DARK : LIGHT);
    var tc = document.getElementById('metaThemeColor');
    if (tc) tc.setAttribute('content', dark ? '#070a0f' : '#f7f5f1');
    try { document.documentElement.style.colorScheme = dark ? DARK : LIGHT; } catch (e) { /* 老 WebView */ }
    links().forEach(function (l) {
      // 用 media 开关：带 `media="not all"` 的样式表会被预加载但不生效，切换瞬间生效
      l.disabled = false;
      l.media = dark ? 'all' : 'not all';
    });
    // 设置面板里的分段按钮同步高亮
    var seg = document.getElementById('themeSeg');
    if (seg) {
      Array.prototype.forEach.call(seg.querySelectorAll('button[data-theme]'), function (b) {
        b.classList.toggle('on', b.getAttribute('data-theme') === (dark ? DARK : LIGHT));
      });
    }
  }

  function stored() {
    try { return localStorage.getItem(KEY) || LIGHT; } catch (e) { return LIGHT; }
  }

  function set(theme) {
    if (theme !== DARK && theme !== LIGHT) return;
    try { localStorage.setItem(KEY, theme); } catch (e) { /* 隐私模式忽略 */ }
    apply(theme);
    try {
      if (window.__rerenderCharts) window.__rerenderCharts();
    } catch (e) { /* 忽略 */ }
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

  window.__theme = { set: set, get: stored, isDark: function () { return stored() === DARK; } };
  window.__openSheet = function (open) { openSheet(open); };   // 供侧栏「设置」调用

  // ---------------- 设置面板 ----------------
  // 焦点陷阱：设置面板与雷达页的候选详情弹窗共用（Tab 在弹窗内循环，不跑到背后的页面）
  window.__dlgTrap = function (e, box) {
    if (!box || e.key !== 'Tab') return;
    var list = Array.prototype.filter.call(
      box.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),select,textarea,[tabindex]:not([tabindex="-1"])'),
      function (n) { return n.offsetParent !== null || n === document.activeElement; });
    if (!list.length) return;
    var first = list[0], last = list[list.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  };

  var sheetFocusBack = null;

  function openSheet(open) {
    var mask = document.getElementById('settingsMask');
    if (!mask) return;
    if (open === !mask.hidden) return;              // 状态没变就别反复折腾焦点
    var btn = document.getElementById('settingsBtn');
    if (open) {
      sheetFocusBack = document.activeElement;
      mask.hidden = false;
      if (btn) btn.setAttribute('aria-expanded', 'true');
      var close = document.getElementById('settingsClose');
      if (close) close.focus();                     // 焦点进面板，Tab 不会再跑到背景
    } else {
      mask.hidden = true;
      if (btn) btn.setAttribute('aria-expanded', 'false');
      if (sheetFocusBack && sheetFocusBack.focus) sheetFocusBack.focus();
      sheetFocusBack = null;
    }
  }

  function initSheet() {
    var btn = document.getElementById('settingsBtn');
    var mask = document.getElementById('settingsMask');
    var close = document.getElementById('settingsClose');
    var seg = document.getElementById('themeSeg');

    if (btn) btn.addEventListener('click', function () { openSheet(true); });
    if (close) close.addEventListener('click', function () { openSheet(false); });
    if (mask) {
      mask.addEventListener('click', function (e) {
        if (e.target === mask) openSheet(false);
      });
    }
    if (seg) {
      Array.prototype.forEach.call(seg.querySelectorAll('button[data-theme]'), function (b) {
        b.addEventListener('click', function () { set(b.getAttribute('data-theme')); });
      });
    }
    document.addEventListener('keydown', function (e) {
      var m = document.getElementById('settingsMask');
      var isOpen = !!(m && !m.hidden);
      if (e.key === 'Escape') { openSheet(false); return; }
      if (isOpen) window.__dlgTrap(e, m);
    });
  }

  function init() {
    apply(fromQuery() || stored());
    initSheet();
    // 便于截图/排障：?sheet=1 直接打开设置面板
    try {
      if (new URLSearchParams(location.search).get('sheet') === '1') openSheet(true);
    } catch (e) { /* 忽略 */ }
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

STOCK_DARK = r"""/* 由 web/build_dark_theme.py 生成：深色主题（浅色 stock.css / 雷达内联样式的反向映射） */
/* ============================================================
   大A小散 · 视觉系统 v2（统一设计语言）
   令牌 → 布局 → 组件 → 图表 → 市场全景 → 响应式
   规范：中性深色底 / 单一蓝色主色 / 语义涨跌色 / 8pt 间距 / 18px 卡片圆角
   ============================================================ */

/* ---------------- 1. 设计令牌 ---------------- */
:root {
  /* 表面层级：底 → 卡片 → 嵌套块 → 交互态 */
  /* 微暖纸色：不用冷蓝灰（那是最典型的"AI SaaS 背景"） */
  --bg: #070a0f;
  --bg-soft: #0b1017;
  --panel: #0f141c;
  --panel-2: #141a24;
  --panel-3: #1a2330;

  /* 描边：低对比发丝线（分区带靠它切段） */
  --line: #232c3a;
  --line-soft: #181f29;

  /* 文本：三级灰阶，偏墨色 */
  --text: #eef3fa;
  --text-dim: #9aa7b9;
  --text-mute: #657180;

  /* 主色：只用于"可点击 / 已选中"，不承担信息强调 */
  --accent: #4e8cff;
  --accent-2: #7fb0ff;
  --accent-weak: rgba(78, 140, 255, .10);

  /* 数字三档：一个 hero + 一组 key + 正文 */
  --num-hero: 34px;
  --num-key: 20px;
  --num-body: 13px;

  /* 语义色：红涨绿跌（A 股习惯） */
  --up: #ff5468;
  --down: #16c784;
  --good: #16c784;
  --bad: #ff5468;
  --warn: #ffb020;

  /* 圆角 / 阴影 / 字体 */
  --radius-lg: 12px;
  --radius: 10px;
  --radius-sm: 8px;
  --radius-xs: 6px;
  --shadow: 0 18px 40px -28px rgba(9, 12, 18, .16);
  /* 图表配色（跟随浅色/深色主题） */
  --chart-grid: #e6e1d8;
  --chart-zero: #232c3a;
  --chart-axis: #657180;
  --chart-ink: #2a3138;
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
  background: var(--fg);
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
  /* 去 AI 味：胶囊渐变 + 内发光 → 白底 + 底部强调线（像标签页，不像徽章） */
  color: var(--text);
  font-weight: 650;
  background: var(--panel);
  border-color: var(--line);
  border-bottom: 2px solid var(--accent);
  box-shadow: none;
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

/* 分区带：透明底 + 顶部发丝线，取代"每个模块一个白盒子" */
.card {
  background: transparent;
  border: 0;
  border-top: 1px solid var(--line);
  border-radius: 0;
  padding: 18px 0 22px;
  margin-bottom: 0;
  scroll-margin-top: 0;
}

/* 只保留三个"英雄级"容器：行情卡 / 市场全景头 / 评分卡 */
.quote-card,
.mk-hero,
#sec-score,
#quoteCard {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: var(--radius);
}

.card > h2 {
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 13.5px;
  font-weight: 650;
  letter-spacing: .06em;
  color: #aeb9c6;
  margin: 0 0 4px;
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
  border: 2.5px solid var(--line);
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
  background: linear-gradient(100deg, var(--panel-2) 30%, var(--bg-soft) 50%, var(--panel-2) 70%);
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
    var(--panel);
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
/* 首屏 K 线：刻意不用 .card —— .card 会参与章节自动编号（#result .card>h2::before），
   也会被 initCollapse 折叠；这里要的恰恰是"永远可见" */
.hero-k {
  border-top: 1px solid var(--line);
  padding: 14px 0 6px;
}
.hero-k:empty { display: none; }
.hero-k h2 {
  display: flex;
  align-items: baseline;
  gap: 10px;
  flex-wrap: wrap;
  margin: 0 0 6px;
  font-size: 13.5px;
  font-weight: 650;
  color: var(--text);
}

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
  background: var(--accent);
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
  background: var(--panel-3);
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
.peer-card .sim .fill { height: 100%; background: var(--accent); }
.peer-card .sim .val { font-family: var(--mono); font-size: 12px; color: var(--accent-2); }
.peer-card .pm { display: flex; gap: 12px; flex-wrap: wrap; font-family: var(--mono); font-size: 11.5px; color: var(--text-dim); }
.peer-card .rs { display: grid; gap: 3px; margin-top: 9px; }
.peer-card .rs span { font-size: 11px; line-height: 1.5; color: var(--text-mute); }
.peer-card .dims { display: grid; gap: 5px; margin-top: 9px; }
.peer-card .dim { display: grid; grid-template-columns: 50px minmax(0, 1fr) 28px; align-items: center; gap: 6px; }
.peer-card .dim .dl2 { font-size: 10px; color: var(--text-mute); }
.peer-card .dim .dt2 { height: 3px; border-radius: 999px; background: #1a2330; overflow: hidden; }
.peer-card .dim .dt2 i { display: block; height: 100%; border-radius: 999px; background: var(--accent); }
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
  border-radius: var(--radius);
  background: var(--panel);
  box-shadow: none;
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

.mk-breadth .bk-num { font-family: var(--mono); font-size: var(--num-hero); font-weight: 700; letter-spacing: -.02em; }
.mk-breadth .bk-num .up { color: var(--up); }
.mk-breadth .bk-num .down { color: var(--down); }
.mk-breadth .bk-sub { margin-top: 5px; font-size: 11px; color: var(--text-mute); }
.mk-breadth .bk-bar {
  display: flex;
  height: 6px;
  margin-top: 11px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--panel-3);
}
.mk-breadth .bk-bar i { display: block; height: 100%; }
.mk-breadth .bk-bar .u { background: var(--up); }
.mk-breadth .bk-bar .f { background: var(--text-mute); }
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
.mk-kpi .v { margin-top: 4px; font-family: var(--mono); font-size: var(--num-key); font-weight: 650; color: var(--text); }
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
.mk-tier .tb i { display: block; height: 100%; border-radius: 7px; background: var(--up); }
.mk-tier .tc { font-family: var(--mono); font-size: 12px; text-align: right; color: var(--text); }

.mk-list { display: grid; gap: 0; }
.mk-item {
  /* 榜单：表格行而不是"每条一个小圆角卡" */
  display: grid;
  grid-template-columns: 18px minmax(0, 1fr) auto;
  gap: 8px;
  align-items: center;
  padding: 7px 4px;
  border: 0;
  border-bottom: 1px solid var(--line-soft);
  border-radius: 0;
  background: transparent;
  cursor: pointer;
  transition: background .15s;
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
  .mk-hot-grid { display: block; }
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
  .brand-text h1 { font-size: 17px; font-weight: 800; letter-spacing: -.01em; }
  .brand-text .status-line { max-width: none; font-size: 11px; }
  .appnav { margin-top: 0; gap: 6px; }
  .nav-btn { flex: none; padding: 7px 20px; border-radius: 8px; font-size: 13px; }
  .nav-btn:active { transform: none; }
  .nav-btn:hover { border-color: #2a4a72; color: var(--text); }
  .search-box { margin-top: 0; position: relative; width: 100%; max-width: 560px; justify-self: end; }
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
  .grid-2 { display: block; margin-bottom: 0; }
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
  .mk-hot-grid { gap: 16px; }
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

  /* 市场全景排版：
     - 热门板块占整行（内容最多，单独一行不会被别的卡片拉高）；
     - 其余 4 张（连板梯队 / 涨停 / 跌停 / 炸板）2×2 等高网格：每行都填满，同行等高，
       列表内部限高滚动，避免「内容少的卡片被拉出大块留白」；
     - 热榜 4 张同样 2 列（≥1600 时 4 列一行），不会出现「3+1」尴尬空位。 */
  #marketView { display: block; }
  .mk-full { margin-bottom: 16px; }
  /* 分区带：单栏流式，不再切 2×2 网格 */
  .mk-cards {
    display: block;
  }
  .mk-cards > .card { margin: 0; }
  /* 名单类卡片限高，内容再多也不把同行卡片拉成一条缝 */
  .mk-cards .mk-list,
  .mk-cards .mk-tiers {
    max-height: 264px;
    overflow-y: auto;
    scrollbar-width: thin;
  }
  .mk-hot-grid {
    display: block;
  }
  .mk-hero { margin-bottom: 16px; }

  /* 分区带：分析结果单栏，靠发丝线切段 */
  #result { display: block; }
  #result > .card,
  #result > .grid-2 > .card { margin-bottom: 0; }
  /* 需要整行宽度的模块：宽表格 / 多图 / 矩阵 */
  /* 单栏分区带：不再需要 grid-column 跨列 */
}

/* ============================================================
   1600px+：再加一栏，超宽屏塞满
   ============================================================ */
@media (min-width: 1600px) {
  main { max-width: 1640px; }
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
  background: rgba(9, 12, 18, .38);
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
  box-shadow: 0 30px 70px -40px rgba(9, 12, 18, .6);
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
.seg button svg { vertical-align: -2px; margin-right: 4px; }
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
  color: #04141c;
  font-weight: 650;
  background: var(--panel);
  border-color: rgba(78, 140, 255, .34);
}
.settings-foot { display: flex; justify-content: flex-end; margin-top: 14px; }
@media (min-width: 900px) {
  .icon-btn { display: grid; }
}

/* ===== 深色主题兜底：亮底深字，避免「深字压深底」看不清 ===== */
.nav-btn.on,
.seg button.on {
  color: #04141c !important;
  background: linear-gradient(135deg, #22d3ee, #61e6c9) !important;
  border-color: transparent !important;
  box-shadow: 0 2px 10px -6px rgba(34, 211, 238, .55) !important;
}
"""

RADAR_DARK = r"""/* 由 web/build_dark_theme.py 生成：深色主题（浅色 stock.css / 雷达内联样式的反向映射） */

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
  --accent-weak:rgba(78, 140, 255, .10);
  --radius:10px; --radius-sm:8px; --radius-xs:6px;
  --num-hero:34px; --num-key:20px; --num-body:13px;
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
  background:var(--fg);border:1px solid var(--fg);color:#0f141c;
  box-shadow:inset 0 1px 0 rgba(9, 12, 18, .06);
}
.brand-text h1{font-size:17px;font-weight:800;line-height:1.25;letter-spacing:-.01em}
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
  color:var(--fg);font-weight:650;
  background:var(--card);
  border-color:var(--line);
  border-bottom:2px solid var(--accent);
  box-shadow:none;
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
  /* 分区带：透明底 + 顶部发丝线 */
  background:transparent;border:0;border-top:1px solid var(--line);border-radius:0;
  padding:18px 0 22px;min-width:0;
}
.card h2{
  display:flex;align-items:center;gap:9px;font-size:15px;font-weight:600;margin:0 0 2px;flex-wrap:wrap;
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
  background:var(--card-3);border-bottom:1px solid var(--line);font-family:var(--font);
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
/* 命中行：左侧 3px 强调条 + 底色。刚命中(红) / 承接(绿) / 走弱(黄) 分开，
   滚动盯盘时不用逐个读文字也能看出方向（≤679px 的卡片布局还会覆盖 border-color）。 */
table.cand tr.hit-row{background:rgba(255, 84, 104, .06);box-shadow:inset 3px 0 0 rgba(255, 84, 104, .62)}
table.cand tr.hit-row.confirm{background:rgba(22, 199, 132, .07);box-shadow:inset 3px 0 0 rgba(22, 199, 132, .72)}
table.cand tr.hit-row.broken{background:rgba(255, 176, 32, .08);box-shadow:inset 3px 0 0 rgba(255, 176, 32, .72)}

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
.bar-fill.pos{background:var(--hit)}
.bar-fill.neg{background:var(--ok)}
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
/* 入场动效只做位移，不做透明度：动画在后台标签页可能被节流停在首帧，
   停在首帧时它最多是低 8px，绝不会变成"看不见"。关闭即时（盯盘不做拖沓退场）。 */
.modal-mask.anim-in .modal{animation:mSlide .18s ease}
@keyframes mSlide{from{transform:translateY(8px)}to{transform:none}}
@media (prefers-reduced-motion:reduce){.modal-mask.anim-in .modal{animation:none}}

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
    display:grid;grid-template-columns:260px auto minmax(0,1fr) auto;
    align-items:center;gap:24px;padding:12px 26px;min-height:76px;
  }
  .bar-top{display:contents}
  .brand{grid-column:1;grid-row:1;min-width:0}
  .appnav{
    grid-column:2;grid-row:1;justify-self:start;
    margin-top:0;gap:6px;padding:3px;max-width:none;
  }
  .bar-badges{grid-column:3;grid-row:1;justify-self:end;margin-left:0}
  .icon-btn{grid-column:4;grid-row:1;justify-self:end}
  .nav-btn{flex:none;padding:7px 20px;border-radius:10px;font-size:13px}
}
@media (min-width:1280px){
  .cols{grid-template-columns:minmax(0,1.15fr) minmax(0,2fr);align-items:start}
  .cols2{grid-template-columns:repeat(2,minmax(0,1fr))}
  .sfquad{grid-template-columns:repeat(2,minmax(0,1fr))}
}


/* ---------- 设置入口与设置面板 ---------- */
.icon-btn{display:none;width:38px;height:38px;place-items:center;border-radius:10px;border:1px solid var(--line);background:var(--card-2);color:var(--dim);font-size:16px;line-height:1;cursor:pointer;transition:color .15s,border-color .15s}
.icon-btn:hover{color:var(--accent);border-color:var(--accent)}
.settings-mask{position:fixed;inset:0;z-index:200;display:grid;place-items:center;padding:24px;background:rgba(9, 12, 18, .38);-webkit-backdrop-filter:blur(2px);backdrop-filter:blur(2px)}
.settings-mask[hidden]{display:none}
.settings-sheet{width:min(420px,100%);padding:18px 18px 16px;background:var(--card);border:1px solid var(--line);border-radius:16px;box-shadow:0 30px 70px -40px rgba(9, 12, 18, .6)}
.settings-sheet h3{margin:0 0 4px;font-size:15px}
.settings-sheet .sub{margin:0 0 12px;font-size:11.5px;color:var(--muted)}
.settings-row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 0 4px;border-top:1px solid var(--line-soft)}
.settings-row .lbl{font-size:13px;color:var(--fg)}
.settings-row .hint{margin-top:2px;font-size:11px;color:var(--muted)}
.seg{display:inline-flex;gap:4px;padding:3px;border-radius:10px;background:var(--bg-soft);border:1px solid var(--line-soft)}
.seg button svg{vertical-align:-2px;margin-right:4px}
.seg button{padding:6px 14px;border:1px solid transparent;border-radius:8px;background:transparent;color:var(--dim);font-size:12.5px;cursor:pointer;transition:color .15s,background .15s}
.seg button.on{color:var(--fg);font-weight:650;background:var(--card);border-color:var(--line);border-bottom:2px solid var(--accent)}
.settings-foot{display:flex;justify-content:flex-end;margin-top:14px}
@media (min-width:900px){.icon-btn{display:grid}}

/* ===== 深色主题兜底：亮底深字，避免「深字压深底」看不清 ===== */
.nav-btn.on,
.seg button.on {
  color: #04141c !important;
  background: linear-gradient(135deg, #22d3ee, #61e6c9) !important;
  border-color: transparent !important;
  box-shadow: 0 2px 10px -6px rgba(34, 211, 238, .55) !important;
}
"""

PAGES_DARK = r"""/* 由 web/build_dark_theme.py 生成：深色主题（浅色 stock.css / 雷达内联样式的反向映射） */

/* ===== analysis.css ===== */
/* ============================================================
   analysis.css —— 个股分析页 v2：与「市场全景」同一套卡片体系
   只作用于 body.an，不影响复盘 / 雷达页
   ============================================================ */

/* 只用三边 padding：左边距由 nav.css 的 body.has-side 负责，
   写成 padding 简写会把 356px 覆盖成 32px，内容列就会跑到侧栏底下去 */
body.an {
  padding-top: 32px;
  padding-right: 32px;
  padding-bottom: 56px;
  background: var(--bg);
}
@media (max-width: 899px) {
  body.an { padding-top: 14px; padding-right: 12px; padding-bottom: 40px; padding-left: 12px; }
}

/* 内容列：与「市场全景」一致（1620 上限，窗宽不够时自然铺满） */
body.an #main {
  max-width: 1620px;
  margin: 0 auto;
  padding: 0;
}

/* ---------------- 标题行（搜索框已从顶栏下移到这里） ---------------- */
.an-head { display: flex; align-items: flex-start; gap: 20px; margin-bottom: 18px; }
.an-head h1 { font-size: 30px; font-weight: 700; letter-spacing: -.02em; line-height: 1.1; }
.an-sub {
  display: flex; align-items: center; gap: 7px; margin-top: 7px;
  font-size: 12.5px; color: var(--text-mute);
}
.an-sub .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--down); flex: none; }
/* 搜索行：放在标题行下方（原「市场全景」起始位置），与空态卡同宽居中 */
.an-search { max-width: 760px; margin: 0 auto 18px; }

body.an .search-box {
  margin: 0;
  width: 100%;
  max-width: none;        /* stock.css 给的是 560px，会把搜索行缩窄并顶到右边 */
  margin-left: 0;
  padding: 4px 6px 4px 14px;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 999px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, .04);
}
body.an .search-box:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-weak); }
body.an .search-box input { height: 34px; font-size: 13.5px; }
body.an .search-box #searchBtn { border-radius: 999px; padding: 7px 18px; font-size: 13px; }
body.an .search-box .suggest { top: calc(100% + 6px); left: 0; right: 0; }

/* ---------------- 空态 ---------------- */
.an-empty {
  max-width: 760px;
  margin: 0 auto;
  background: var(--panel);
  border-radius: 22px;
  padding: 44px 28px 40px;
  text-align: center;
  box-shadow: 0 1px 2px rgba(0, 0, 0, .05), 0 12px 28px -18px rgba(0, 0, 0, .20);
}
.an-empty h2 { font-size: 17px; font-weight: 700; letter-spacing: -.01em; }
.an-empty p { margin-top: 8px; font-size: 12.5px; color: var(--text-mute); }
.an-eg { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 20px; }
.an-eg a {
  padding: 7px 14px; border-radius: 999px; background: var(--panel-2);
  font-size: 12.5px; color: var(--text-dim); text-decoration: none; font-family: var(--mono);
}
.an-eg a:hover { background: var(--panel-3); color: var(--text); }

/* ---------------- 卡片：从「分区带」改成白卡 ---------------- */
body.an .card {
  background: var(--panel);
  border: 1px solid transparent;
  border-top: 1px solid transparent;
  border-radius: 22px;
  padding: 20px 22px;
  margin-bottom: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, .05), 0 12px 28px -18px rgba(0, 0, 0, .20);
}
body.an .card > h2 { font-size: 15px; font-weight: 700; letter-spacing: -.01em; color: var(--text); }
body.an .card .sub { margin-left: 0; }
/* stock.css 里有 `#result > .card{margin-bottom:0}`（id 选择器），
   普通类选择器压不住，这里用同级的 body.an #result 提权，模块之间才有 16px 白隙 */
body.an #result > .card,
body.an #result > .grid-2 > .card { margin-bottom: 16px; }
body.an #result > .grid-2 { display: grid; gap: 16px; margin-bottom: 16px; }
body.an #result > .card:last-of-type,
body.an #result > .grid-2:last-of-type { margin-bottom: 0; }

/* 英雄容器 + 首屏 K 线：同一套圆角与投影 */
body.an .quote-card,
body.an .hero-k,
body.an #sec-score {
  border-radius: 22px;
  border: 1px solid transparent;
  box-shadow: 0 1px 2px rgba(0, 0, 0, .05), 0 12px 28px -18px rgba(0, 0, 0, .20);
}
body.an .hero-k { padding: 18px 22px 10px; margin-bottom: 16px; background: var(--panel); }
body.an .hero-k h2 { font-size: 15px; font-weight: 700; }

/* ---------------- 关键指标：前 4 个升级成主 KPI ---------------- */
body.an .facts { gap: 12px; margin-bottom: 16px; }
body.an .fact {
  border-radius: 16px;
  border: 1px solid var(--line-soft);
  background: var(--panel);
  padding: 14px 16px;
}
body.an .fact .fl { font-size: 11px; }
body.an .fact:nth-child(-n+4) {
  border-color: var(--line);
  box-shadow: 0 1px 2px rgba(0, 0, 0, .04);
}
body.an .fact:nth-child(-n+4) .fv {
  font-size: var(--num-key);
  font-weight: 650;
  letter-spacing: -.02em;
  margin-top: 8px;
}

/* ---------------- 返回栏 ---------------- */
body.an .back-bar { margin-bottom: 14px; }
body.an .back-bar a.btn-ghost { text-decoration: none; display: inline-flex; align-items: center; }

/* ---------------- 加载 / 错误态与卡片对齐 ---------------- */
body.an .loading,
body.an .error-box {
  border-radius: 22px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, .05), 0 12px 28px -18px rgba(0, 0, 0, .20);
}

/* 移动端：标题行竖排，搜索占满 */
@media (max-width: 899px) {
  .an-head { flex-direction: column; gap: 12px; }
  .an-head h1 { font-size: 24px; }
  .an-search { max-width: none; margin-bottom: 14px; }
  body.an .card { padding: 16px; border-radius: 18px; }
  body.an .hero-k { padding: 14px 16px 8px; }
}
/* ---------------- 色彩收口：把遗留的冷蓝灰换成暖纸色 ----------------
   这些 #131a25 / #1a2330 / #16233a 是去 AI 味之前的旧色阶，
   在暖纸底 + 白卡的体系里会突兀（行情卡的指标带尤其明显）。 */
body.an .qc-stat { background: var(--panel-2); border-radius: 12px; }
body.an .bar-track,
body.an .peer-card .sim .track,
body.an .peer-card .dim .dt2 { background: var(--panel-3); }
body.an .suggest-item:hover { background: var(--panel-2); }
body.an .suggest-item.active { background: var(--panel-3); }
/* ===== overview.css ===== */
/* ============================================================
   overview.css —— 市场全景页（左栏 + 主力区 + 右栏）
   令牌沿用 stock.css 的 :root；本文件只加页面级版式
   ============================================================ */

body.ov {
  background: var(--bg);
  padding-top: 32px;
  padding-right: 32px;
  padding-bottom: 32px;
}
@media (max-width: 899px) {
  body.ov, body.ov.has-side { padding: 0 0 24px; }
  .ov-side-host { display: block; }
}

.ov-main {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 396px;
  gap: 16px;
  align-items: start;
  max-width: 1620px;
}
.ov-col { display: flex; flex-direction: column; gap: 16px; min-width: 0; }

/* ---------------- 标题区 ---------------- */
.ov-head { display: flex; align-items: flex-start; gap: 20px; padding: 6px 4px 2px; }
.ov-head h1 { font-size: 30px; font-weight: 700; letter-spacing: -.02em; line-height: 1.1; }
.ov-head p { font-size: 12.5px; color: var(--text-mute); margin-top: 6px; }
.ov-head .sr { margin-left: auto; display: flex; gap: 10px; align-items: center; }
.ov-search {
  display: flex; align-items: center; gap: 9px; min-width: 300px; padding: 11px 16px;
  border-radius: 999px; background: var(--panel); border: 1px solid var(--line);
  color: var(--text-mute); font-size: 13.5px;
}
.ov-search input {
  border: 0; outline: 0; background: transparent; font: inherit; color: var(--text);
  width: 100%; min-width: 0;
}
.ov-btn-dark {
  padding: 11px 26px; border-radius: 999px; background: #e9e5dc; color: #0f141c; font-size: 14px;
  font-weight: 600; border: 0; cursor: pointer; font-family: inherit;
}

/* ---------------- 三张彩色 hero ---------------- */
.ov-hero3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.ov-hc {
  border-radius: 22px; padding: 20px; min-height: 150px; display: flex; flex-direction: column;
  min-width: 0; container-type: inline-size;
}
/* 三张彩色卡片的底色（原来是内联 style，深色主题的映射改不到，挪到这里） */
.ov-hc.ov-sage { background: #1b2620; }
.ov-hc.ov-amber { background: #2c2513; }
.ov-hc.ov-lav { background: #232037; }

.ov-hc .top { display: flex; align-items: center; gap: 8px; font-size: 13.5px; font-weight: 600; color: #e6edf8; }
.ov-hc .pill {
  padding: 3px 10px; border-radius: 999px; background: rgba(9, 12, 18, .62);
  font-size: 11.5px; font-weight: 500; color: #a9b6c9;
}
.ov-hc .big {
  font-family: var(--mono); font-variant-numeric: tabular-nums; letter-spacing: -.05em;
  font-size: clamp(24px, 1.9vw, 36px); font-weight: 700; line-height: 1.15; margin: 10px 0 0;
  white-space: nowrap;
}
@supports (container-type: inline-size) {
  .ov-hc .big { font-size: clamp(19px, 11cqw, 36px); }
}
.ov-hc .big small { font-size: .44em; font-weight: 600; letter-spacing: 0; margin: 0 2px; }
.ov-hc .sub { margin-top: auto; padding-top: 10px; font-size: 12px; color: #a9b6c9; opacity: .85; }
.ov-hc .sub em { font-style: normal; font-weight: 600; }
.ov-hc .link {
  margin-left: auto; padding: 6px 14px; border-radius: 999px; background: #0f141c; color: #e6edf8;
  font-size: 12px; font-weight: 600; text-decoration: none; white-space: nowrap;
}

/* ---------------- 通用卡 ---------------- */
.ov-card {
  background: var(--panel); border-radius: 22px; padding: 20px 22px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, .05), 0 12px 28px -18px rgba(0, 0, 0, .22);
  min-width: 0;
}
.ov-ch { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; flex-wrap: wrap; }
.ov-ch h2 { font-size: 15px; font-weight: 700; letter-spacing: -.01em; }
.ov-ch .hint { font-size: 11.5px; color: var(--text-mute); }
.ov-seg { margin-left: auto; display: flex; gap: 2px; padding: 3px; background: var(--panel-2); border-radius: 999px; }
.ov-seg span { padding: 5px 13px; border-radius: 999px; font-size: 12px; color: var(--text-dim); white-space: nowrap; }
.ov-seg span.on { background: var(--panel); color: var(--text); font-weight: 600; box-shadow: 0 1px 2px rgba(0, 0, 0, .10); }
.ov-chart { width: 100%; height: auto; display: block; }
.ov-chart .ov-bar { fill: #e6edf8; }
.ov-chart .ov-bar-hi { fill: #3d4c63; }

.ov-chart text { font-family: var(--mono); font-size: 11.5px; fill: var(--text-mute); }
.ov-concl { font-size: 12.5px; color: var(--text-dim); line-height: 1.75; margin-top: 6px; }
.ov-concl b { font-weight: 700; color: var(--text); }

/* ---------------- 热门板块表 ---------------- */
.ov-pt { width: 100%; border-collapse: collapse; }
/* 表头只留小灰字、不要底色：stock.css 的 thead th 带 --panel-3 米色带，
   在这里会变成一条和卡片背景不一致的色块 */
.ov-pt th {
  font-size: 11px; color: var(--text-mute); font-weight: 500; text-align: right;
  padding: 0 0 10px; background: transparent; position: static;
  border-bottom: 1px solid var(--line-soft);
}
.ov-pt th:first-child { text-align: left; }
.ov-pt td {
  padding: 11px 0; border-top: 1px solid var(--line-soft); text-align: right;
  font-size: 13px; font-family: var(--mono); font-variant-numeric: tabular-nums;
}
.ov-pt td:first-child { text-align: left; font-family: var(--font); }
.ov-pt td.ld { text-align: left; font-size: 12.5px; color: var(--text-dim); white-space: nowrap; }
.ov-pt .nm { font-size: 14px; font-weight: 600; display: block; }
.ov-pt .nm2 { font-size: 11.5px; color: var(--text-mute); margin-top: 2px; }
.ov-pt .ld i { font-style: normal; color: var(--up); margin-left: 4px; }
.ov-struct { font-size: 12.5px; color: var(--text-dim); margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--line-soft); }
.ov-chips { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }
.ov-chip { padding: 5px 12px; border-radius: 999px; background: var(--panel-2); font-size: 11.5px; color: var(--text-dim); }
.ov-chip b { font-family: var(--mono); font-weight: 700; color: var(--text); margin-left: 4px; }

/* ---------------- 右栏 ---------------- */
.ov-donut { display: flex; align-items: center; gap: 16px; }
.ov-donut .ring { position: relative; flex: none; }
.ov-donut .c { position: absolute; inset: 0; display: grid; place-items: center; text-align: center; }
.ov-donut .c i { font-style: normal; display: block; font-size: 11px; color: var(--text-mute); }
.ov-donut .c b { font-family: var(--mono); font-size: 23px; font-weight: 700; letter-spacing: -.02em; }
.ov-leg { display: flex; flex-direction: column; gap: 10px; font-size: 12.5px; color: var(--text-dim); }
.ov-leg i { display: inline-block; width: 9px; height: 9px; border-radius: 3px; margin-right: 7px; }
.ov-leg b { font-family: var(--mono); color: var(--text); margin-left: 6px; }

.ov-top4 { display: flex; flex-direction: column; }
.ov-t4 {
  display: grid; grid-template-columns: 22px minmax(0, 1fr) auto; gap: 10px; align-items: center;
  padding: 11px 0; border-top: 1px solid var(--line-soft);
}
.ov-t4:first-child { border-top: 0; }
.ov-rk {
  width: 22px; height: 22px; border-radius: 7px; background: var(--panel-2); color: var(--text-dim);
  font: 600 11px/22px var(--mono); text-align: center;
}
.ov-t4 .nm { font-size: 13.5px; font-weight: 600; }
.ov-t4 .nm2 { display: block; font-size: 11.5px; color: var(--text-mute); margin-top: 2px; font-weight: 400; }
.ov-t4 .v { text-align: right; font-family: var(--mono); font-variant-numeric: tabular-nums; font-size: 13.5px; font-weight: 600; color: var(--up); }
.ov-t4 .v small { display: block; font-size: 11px; color: var(--text-mute); font-weight: 400; margin-top: 1px; }

.ov-hs { display: flex; flex-direction: column; }
.ov-hs .r {
  display: grid; grid-template-columns: 22px minmax(0, 1fr) auto; gap: 10px; align-items: center;
  padding: 10px 0; border-top: 1px solid var(--line-soft);
}
.ov-hs .r:first-child { border-top: 0; }
.ov-hs .nm { font-size: 13.5px; font-weight: 600; }
.ov-hs .nm2 { display: block; font-size: 11px; color: var(--text-mute); margin-top: 2px; font-family: var(--mono); font-weight: 400; }
.ov-hs .v { text-align: right; font-family: var(--mono); font-variant-numeric: tabular-nums; font-size: 13.5px; font-weight: 600; }
.ov-hs .v small { display: block; font-size: 11px; color: var(--text-mute); font-weight: 400; margin-top: 1px; }

.ov-src { font-size: 11px; line-height: 1.8; color: var(--text-mute); padding: 0 4px; }

/* ---------------- 今日一句 + 结构速览 ---------------- */
.ov-row3 { display: grid; grid-template-columns: 1.94fr 1fr; gap: 16px; align-items: stretch; }
.ov-one { display: flex; flex-direction: column; }
.ov-one .ov-ch { margin-bottom: 0; }
.ov-one p { font-size: 17px; line-height: 1.8; font-weight: 500; letter-spacing: -.01em; margin: auto 0; }
.ov-one p b { background: linear-gradient(transparent 62%, rgba(232, 200, 122, .55) 62%); font-weight: 700; }
.ov-one .foot { font-size: 11.5px; color: var(--text-mute); }
.ov-one p.muted { font-size: 14px; font-weight: 400; color: var(--text-mute); }
.ov-dark { background: #12161d; border-radius: 22px; padding: 20px 22px; color: #efeade; box-shadow: 0 12px 28px -18px rgba(0, 0, 0, .35); }
/* 这张卡在深浅两套主题下都是深底，所以标题要用「两套都亮」的固定浅色；
   写 #0f141c 会被深色映射表反转成近黑，标题直接消失 */
.ov-dark h2 { font-size: 15px; font-weight: 700; margin-bottom: 16px; color: #e6edf8; }
.ov-kv {
  display: flex; align-items: baseline; justify-content: space-between; padding: 12px 0;
  border-top: 1px solid rgba(9, 12, 18, .08); font-size: 13px; color: #a8a294;
}
.ov-kv:first-of-type { border-top: 0; }
.ov-kv b {
  font-family: var(--mono); font-variant-numeric: tabular-nums; font-size: 17px; color: #e8c87a;
  font-weight: 700; letter-spacing: -.01em;
}

/* ---------------- 骨架 / 错误 ---------------- */
.ov-skel { padding: 40px 8px; text-align: center; color: var(--text-mute); font-size: 13px; }
.ov-err { padding: 14px 18px; border-radius: 14px; background: rgba(255, 84, 104, .08); color: var(--up); font-size: 13px; }

/* ---------------- 断点 ---------------- */
@media (max-width: 1599px) {
  .ov-main { grid-template-columns: minmax(0, 1fr); max-width: 1100px; }
  .ov-col { width: 100%; }
}
@media (max-width: 1099px) {
  .ov-hero3 { grid-template-columns: minmax(0, 1fr); }
  .ov-h3grid, .ov-row3 { grid-template-columns: minmax(0, 1fr) !important; }
}
@media (max-width: 899px) {
  .ov-head { flex-direction: column; gap: 12px; padding: 14px 12px 0; }
  .ov-head h1 { font-size: 24px; }
  .ov-head .sr { margin-left: 0; width: 100%; }
  .ov-search { min-width: 0; flex: 1; }
  .ov-main { padding: 0 12px; gap: 12px; }
  .ov-card { padding: 16px 16px; border-radius: 18px; }
  .ov-one p { font-size: 15px; }
}

/* ===== radar.css ===== */
/* ============================================================
   radar.css —— 妖股雷达页：与「市场全景」「个股分析」同一套卡片体系
   只作用于 body.rd；令牌沿用 index.html 内联的 :root（--bg/--card/--line/--fg…）
   ============================================================ */

body.rd {
  padding-top: 32px;
  padding-right: 32px;
  padding-bottom: 56px;
  background: var(--bg);
}
@media (max-width: 899px) {
  body.rd { padding-top: 14px; padding-right: 12px; padding-bottom: 40px; padding-left: 12px; }
}

/* 页内所有区块统一内容列（原顶部 .bar 已移除，导航在左侧栏） */
body.rd .rd-head,
body.rd .panel-top,
body.rd .chips,
body.rd main,
body.rd .sf,
body.rd footer {
  max-width: 1620px;
  margin-left: auto;
  margin-right: auto;
}

/* ---------------- 标题行 ---------------- */
.rd-head { display: flex; align-items: flex-start; gap: 16px; margin-bottom: 6px; flex-wrap: wrap; }
.rd-head h1 { font-size: 30px; font-weight: 700; letter-spacing: -.02em; line-height: 1.1; }
.rd-sub {
  display: flex; align-items: center; gap: 8px; margin-top: 8px;
  font-size: 12.5px; color: var(--muted); flex-wrap: wrap;
}
.rd-head .bar-meta { margin-left: auto; margin-top: 0; align-self: flex-end; }

/* ---------------- 运行状态 / 筛选条件 ---------------- */
body.rd .panel-top { padding: 0 0 12px; }
body.rd .chips { padding: 0 0 14px; }

/* ---------------- 卡片：从「分区带」改成白卡 ---------------- */
body.rd .card {
  background: var(--card);
  border: 0;
  border-top: 0;
  border-radius: 22px;
  padding: 20px 22px;
  margin-bottom: 16px;
  min-width: 0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, .05), 0 12px 28px -18px rgba(0, 0, 0, .20);
}
body.rd .card > h2 { font-size: 15px; font-weight: 700; letter-spacing: -.01em; margin: 0 0 4px; }
body.rd .cols { gap: 16px; }
body.rd main { padding: 0; }

/* 表头只留小灰字、不要底色（index.html 内联的 th 带 --card-3 米色带，
   在白卡里会变成一条和卡片背景不一致的色块） */
body.rd th {
  background: transparent;
  position: static;
  border-bottom: 1px solid var(--line-soft);
}

/* ---------------- 表格列距：让候选池 13 列整表放得下 ----------------
   内联样式里 td/th 都是 8px 内边距，13 列共 208px，最后「状态」列会被挤出可视区；
   收到 4px 后可省 ~104px，配合题材列限宽即可整表显示。 */
body.rd table td,
body.rd table th { padding: 8px 4px; }
body.rd td.rr { max-width: 128px; }
/* 首列贴卡片左边、末列贴右边，视觉上仍留一点气口 */
body.rd table td:first-child,
body.rd table th:first-child { padding-left: 2px; }
body.rd table td:last-child,
body.rd table th:last-child { padding-right: 2px; }

/* ---------------- 底部板块资金矩阵 / 页脚 ---------------- */
body.rd .sf { padding: 0; }
body.rd .sf > .card { margin-bottom: 16px; }
body.rd footer {
  padding: 4px 2px 0;
  border-top: 0;
  font-size: 11px;
  color: var(--muted);
}

@media (max-width: 899px) {
  .rd-head h1 { font-size: 24px; }
  .rd-head .bar-meta { margin-left: 0; }
  body.rd .card { padding: 16px; border-radius: 18px; }
}

/* ===== review.css ===== */
/* ============================================================
   复盘页（/review）—— 结构对齐复盘设计稿：
   1 一句话总收口 / 2 盘型环境 / 2.5 资金流证据 / 4 主线轮动 /
   4.5 连板高度 / 4.6 连板梯队 / 6 四分层 / 10 次日观察与证伪 /
   12 股票池更新 / 13 风险边界
   ============================================================ */

/* ---------------- 顶部条 ---------------- */
.rv-topbar {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 12px;
  padding: 14px 16px;
  margin-bottom: 12px;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: var(--panel);
}
.rv-topbar-main { min-width: 0; }
.rv-sys {
  /* 低调化：不做"系统徽章"，只做灰色小标签 */
  font-size: 10.5px; letter-spacing: 1.2px; color: var(--text-mute);
  border: 0; background: none; padding: 0;
}
.rv-title { font-size: 19px; margin: 8px 0 0; letter-spacing: .4px; }
.rv-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.rv-tag {
  font-size: 11.5px; color: var(--text-dim); background: var(--panel-2);
  border: 1px solid var(--line); border-radius: 999px; padding: 3px 10px;
}
.rv-tag.ghost { color: var(--text-mute); background: transparent; }
.rv-tag.heat.hot { color: #0f141c; background: var(--up); border-color: transparent; }
.rv-tag.heat.warm { color: #0f141c; background: var(--warn); border-color: transparent; }
.rv-tag.heat.mid { color: var(--text); }
.rv-tag.heat.cool { color: #0f141c; background: var(--down); border-color: transparent; }
.rv-tag.heat.cold { color: #0f141c; background: #7fd8b8; border-color: transparent; }
.rv-topbar-actions { display: flex; align-items: center; gap: 8px; flex: none; }
.rv-select {
  appearance: none; color: var(--text); background: var(--panel-2);
  border: 1px solid var(--line); border-radius: 999px;
  font-size: 12.5px; padding: 7px 26px 7px 12px; max-width: 140px;
  background-image: linear-gradient(45deg, transparent 50%, var(--text-mute) 50%), linear-gradient(135deg, var(--text-mute) 50%, transparent 50%);
  background-position: calc(100% - 14px) 52%, calc(100% - 9px) 52%;
  background-size: 5px 5px, 5px 5px; background-repeat: no-repeat;
}
.rv-topbar-actions .btn-ghost { padding: 7px 14px; font-size: 12.5px; }

/* ---------------- 区块骨架 ---------------- */
.rv-flow { display: grid; grid-template-columns: minmax(0, 1fr); gap: 12px; }
.rv-sec {
  /* 分区带：透明底 + 顶部发丝线 */
  background: transparent;
  border: 0;
  border-top: 1px solid var(--line);
  border-radius: 0;
  padding: 16px 0 20px;
}
.rv-sec-head { display: flex; align-items: baseline; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }
.rv-no {
  font: 700 11px/1 var(--mono); color: var(--accent-2);
  background: var(--accent-weak); border-radius: 6px; padding: 3px 6px;
}
.rv-sec-title { font-size: 14px; margin: 0; letter-spacing: .3px; }
.rv-sec-hint { font-size: 11px; color: var(--text-mute); }
.rv-skeleton { padding: 40px 8px; text-align: center; color: var(--text-mute); font-size: 13px; }
.rv-empty { padding: 10px 2px; font-size: 12px; color: var(--text-mute); }
.rv-warn {
  padding: 9px 11px; border-radius: 10px; font-size: 12px; line-height: 1.65;
  color: var(--warn); background: rgba(255, 176, 32, .1); border: 1px solid rgba(255, 176, 32, .3);
}
.rv-caliber, .rv-legend { margin: 9px 0 0; font-size: 10.5px; line-height: 1.7; color: var(--text-mute); }
.rv-col-title {
  font-size: 11.5px; color: var(--text-dim); letter-spacing: .4px; margin-bottom: 7px;
  padding-bottom: 5px; border-bottom: 1px solid var(--line-soft);
}
.rv-col-title.up { color: var(--up); }
.rv-col-title.down { color: var(--down); }
.rv-col-title.mid { color: var(--text-dim); }
.clickable { cursor: pointer; }
.clickable:hover { background: var(--panel-3); }

/* ---------------- 1 一句话 ---------------- */
.rv-verdict {
  margin: 0 0 10px; font-size: 14.5px; line-height: 1.75; color: var(--text); font-weight: 600;
  padding: 11px 13px; border-radius: 12px;
  background: var(--panel);
  border: 1px solid var(--line);
}
.rv-points { margin: 0; padding-left: 18px; }
.rv-points li { font-size: 12.5px; line-height: 1.85; color: var(--text-dim); }

/* ---------------- 2 环境 ---------------- */
.rv-env { display: grid; grid-template-columns: minmax(0, 1fr); gap: 14px; }
.rv-regime { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }
.rv-regime-name { font-size: 15px; font-weight: 650; color: var(--accent-2); }
.rv-regime-flavor { font-size: 11.5px; color: var(--text-mute); }
.rv-kvs { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 7px; }
.rv-kv {
  display: flex; align-items: baseline; justify-content: space-between; gap: 8px;
  background: var(--panel-2); border-radius: 9px; padding: 7px 9px;
}
.rv-kv .k { font-size: 11px; color: var(--text-mute); }
.rv-kv .v { font: 650 12.5px/1.2 var(--mono); color: var(--text); }
.rv-kv .v.up { color: var(--up); } .rv-kv .v.down { color: var(--down); }
.rv-idx-head, .rv-idx-row {
  display: grid; grid-template-columns: minmax(0, 1fr) 78px 68px; gap: 8px; align-items: center;
  padding: 6px 8px; font-size: 12px; font-family: var(--mono);
}
.rv-idx-head { color: var(--text-mute); font-size: 10.5px; border-bottom: 1px solid var(--line-soft); font-family: var(--font); }
.rv-idx-row { border-bottom: 1px solid var(--line-soft); }
.rv-idx-row:last-child { border-bottom: none; }
.rv-idx-row .n { font-family: var(--font); color: var(--text-dim); }
.rv-idx-row .p, .rv-idx-row .c { text-align: right; }
.rv-idx-head .p, .rv-idx-head .c { text-align: right; }
.rv-idx-row .up, .rv-idx-row .c.up { color: var(--up); }
.rv-idx-row .down, .rv-idx-row .c.down { color: var(--down); }

/* ---------------- 2.5 资金 ---------------- */
.rv-money { display: grid; grid-template-columns: minmax(0, 1fr); gap: 12px; }
.rv-tb-head, .rv-tb-row {
  display: grid; grid-template-columns: minmax(0, 1fr) 62px 66px; gap: 6px; align-items: center;
  padding: 6px 7px; font-size: 12px;
}
.rv-tb-head { color: var(--text-mute); font-size: 10.5px; border-bottom: 1px solid var(--line-soft); }
.rv-tb-head span:nth-child(2), .rv-tb-head span:nth-child(3) { text-align: right; }
.rv-tb-row { border-bottom: 1px solid var(--line-soft); border-radius: 6px; }
.rv-tb-row:last-child { border-bottom: none; }
.rv-tb-row > span:nth-child(2), .rv-tb-row > span:nth-child(3) { text-align: right; font-family: var(--mono); }
.rv-tb-row .nm { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rv-tb-row .nm small { color: var(--text-mute); font-size: 10.5px; margin-left: 5px; font-family: var(--mono); }
.rv-tb-row .up { color: var(--up); } .rv-tb-row .down { color: var(--down); }

/* ---------------- 4 轮动 ---------------- */
.rv-rot { display: grid; grid-template-columns: minmax(0, 1fr); gap: 10px; }
.rv-rot-card {
  background: var(--panel-2); border: 1px solid var(--line-soft);
  border-radius: 12px; padding: 10px 11px;
}
.rv-rot-card.empty { opacity: .6; }
.rv-rot-head { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
.rv-rot-kind {
  font-size: 10px; color: var(--text-mute); border: 1px solid var(--line);
  border-radius: 5px; padding: 1px 5px;
}
.rv-rot-name { font-size: 13.5px; font-weight: 650; color: var(--text); }
.rv-rot-meta { margin-left: auto; font-size: 10.5px; color: var(--text-mute); font-family: var(--mono); }
.rv-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.rv-chip {
  display: inline-flex; align-items: baseline; gap: 4px;
  font-size: 11.5px; color: var(--text); background: var(--panel-3);
  border-radius: 999px; padding: 3px 9px;
}
.rv-chip i { font-style: normal; font-size: 10px; color: var(--text-mute); }
.rv-verdict-sm { margin: 8px 0 0; font-size: 11.5px; color: var(--accent-2); line-height: 1.6; }
.rv-failed { margin-top: 12px; }
.rv-failed-item {
  display: grid; grid-template-columns: minmax(0, 1fr) 62px; gap: 8px; align-items: center;
  padding: 7px 9px; background: var(--panel-2); border-radius: 9px; margin-bottom: 6px;
}
.rv-failed-item .nm { font-size: 12.5px; }
.rv-failed-item > span:nth-child(2) { text-align: right; font-family: var(--mono); font-size: 12px; }
.rv-failed-item .note { grid-column: 1 / -1; font-size: 10.5px; color: var(--text-mute); }
.rv-failed-item .up { color: var(--up); } .rv-failed-item .down { color: var(--down); }

/* ---------------- 4.5 高度 ---------------- */
.rv-height-main { display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }
.rv-height-name { font-size: 17px; font-weight: 700; }
.rv-height-name small { font-size: 11px; color: var(--text-mute); font-family: var(--mono); margin-left: 6px; }
.rv-height-board { font-size: 12px; color: var(--text-dim); }
.rv-height-board b { font-size: 17px; color: var(--up); font-family: var(--mono); }
.rv-height-pct { font: 650 13px/1 var(--mono); margin-left: auto; }
.rv-height-pct.up { color: var(--up); } .rv-height-pct.down { color: var(--down); }
.rv-height-facts { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 7px; margin-top: 10px; }
.rv-height-reason { margin: 9px 0 0; font-size: 11.5px; color: var(--text-mute); line-height: 1.6; }

/* ---------------- 6 分层 ---------------- */
.rv-layer-head, .rv-layer-row {
  grid-template-columns: 62px minmax(0, 1fr) 46px 46px 62px 52px;
}
.rv-layer-row .tag {
  font-size: 10.5px; color: var(--accent-2); background: var(--accent-weak);
  border-radius: 5px; padding: 2px 5px; text-align: center;
}
.rv-layer-row .nm { font-size: 12.5px; }

/* ---------------- 10 次日 ---------------- */
.rv-next { display: grid; grid-template-columns: minmax(0, 1fr); gap: 12px; }
.rv-list { margin: 0; padding-left: 18px; }
.rv-list li { font-size: 12.5px; line-height: 1.85; color: var(--text-dim); }
.rv-list.warn li { color: #ffb3bd; }

/* ---------------- 12 股票池 ---------------- */
.rv-pool { display: grid; grid-template-columns: minmax(0, 1fr); gap: 12px; }
.rv-pool-item {
  display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 4px 8px;
  padding: 7px 9px; background: var(--panel-2); border-radius: 9px; margin-bottom: 6px;
}
.rv-pool-item .nm { font-size: 12.5px; }
.rv-pool-item .meta { grid-column: 1 / -1; font-size: 10.5px; color: var(--text-mute); }
.rv-pool-item > span:last-child { font-family: var(--mono); font-size: 12px; text-align: right; }
.rv-pool-item .up { color: var(--up); } .rv-pool-item .down { color: var(--down); }

/* ---------------- 13 风险 ---------------- */
.rv-risk { display: flex; align-items: flex-start; gap: 12px; flex-wrap: wrap; }
.rv-risk-level {
  display: inline-flex; align-items: baseline; gap: 8px; flex: none;
  border-radius: 12px; padding: 8px 12px; background: var(--panel-2);
  border: 1px solid var(--line);
}
.rv-risk-level .lb { font-size: 10.5px; color: var(--text-mute); }
.rv-risk-level .vl { font-size: 15px; font-weight: 700; }
.rv-risk-level .sc { font-size: 10.5px; color: var(--text-mute); font-family: var(--mono); }
.rv-risk-level.lv-低, .rv-risk-level.lv-中低 { border-color: rgba(22, 199, 132, .4); color: var(--down); }
.rv-risk-level.lv-中 { border-color: rgba(255, 176, 32, .4); color: var(--warn); }
.rv-risk-level.lv-中高, .rv-risk-level.lv-高 { border-color: rgba(255, 84, 104, .45); color: var(--up); }
.rv-risk-text { flex: 1 1 240px; margin: 0; font-size: 12.5px; line-height: 1.8; color: var(--text-dim); }

/* ---------------- 4.6 梯队 ---------------- */
.rv-tiers { display: grid; gap: 7px; }
.rv-tier { display: grid; grid-template-columns: 74px minmax(0, 1fr) 34px; gap: 8px; align-items: center; }
.rv-tier .tl { font-size: 11.5px; color: var(--text-dim); }
.rv-tier .tk { height: 15px; background: var(--panel-3); border-radius: 4px; overflow: hidden; }
.rv-tier .tk i { display: block; height: 100%; border-radius: 4px; background: var(--up); }
.rv-tier .tc { font-size: 11.5px; color: var(--text-mute); text-align: right; font-family: var(--mono); }

/* ---------- 历史命中回顾 ---------- */
.rv-hits-sum { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
.rv-hits-chip {
  padding: 5px 10px; border: 1px solid var(--line-soft); border-radius: 9px;
  background: var(--panel-2); font-size: 11.5px; color: var(--text-dim);
}
.rv-hits-chip b { font-family: var(--mono); font-size: 12.5px; color: var(--text); margin-left: 3px; }
.rv-hits-chip i { font-style: normal; color: var(--text-mute); margin-left: 4px; font-size: 10.5px; }

.rv-hit-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; margin-bottom: 10px; }
.rv-stat-tb, .rv-hit-tb {
  display: grid; min-width: 560px; font-size: 11.5px;
  border-top: 1px solid var(--line-soft);
}
.rv-stat-tb { grid-template-columns: minmax(140px, 1fr) repeat(6, minmax(56px, auto)); }
.rv-hit-tb { grid-template-columns: 62px minmax(118px, 1fr) repeat(8, minmax(50px, auto)); min-width: 720px; }
.rv-stat-tb > span, .rv-hit-tb > span {
  padding: 7px 8px; text-align: right; border-bottom: 1px solid var(--line-soft);
  font-family: var(--mono); white-space: nowrap; color: var(--text-dim);
}
.rv-stat-tb > span.nm, .rv-hit-tb > span.nm,
.rv-hit-tb > span:first-child { text-align: left; font-family: var(--font); color: var(--text); }
.rv-hit-tb > span.st { font-family: var(--font); color: var(--text-mute); }
.rv-hit-tb > span.nm small { color: var(--text-mute); font-size: 10.5px; margin-left: 5px; font-family: var(--mono); }
.rv-stat-tb > .hd, .rv-hit-tb > .hd {
  color: var(--text-mute); font-size: 10.5px; font-weight: 400; background: var(--panel-2);
}
.rv-stat-tb > .up, .rv-hit-tb > .up { color: var(--up); }
.rv-stat-tb > .down, .rv-hit-tb > .down { color: var(--down); }
.rv-stat-tb > .flat, .rv-hit-tb > .flat { color: var(--text-mute); }
.rv-hit-tb > span.nm .sus { color: var(--warn); margin-right: 3px; font-weight: 700; }
.rv-hits-chip.warn { border-color: rgba(255, 176, 32, .45); color: var(--warn); }
.rv-hits-chip.warn b { color: var(--warn); }
.rv-hit-tb > span[data-code] { cursor: pointer; }
.rv-hit-tb > span[data-code]:hover { color: var(--accent); }

.rv-foot { margin: 14px 2px 0; font-size: 11px; line-height: 1.8; color: var(--text-mute); }

/* ============================================================
   宽屏
   ============================================================ */
@media (min-width: 900px) {
  .rv-flow { gap: 16px; }
  .rv-sec { padding: 16px 18px 18px; }
  .rv-sec-title { font-size: 15px; }
  .rv-topbar { padding: 18px 22px; }
  .rv-title { font-size: 22px; }
  .rv-env { grid-template-columns: minmax(0, 1.05fr) minmax(0, .95fr); gap: 22px; }
  .rv-money { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
  .rv-rot { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .rv-next { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .rv-pool { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .rv-height-facts { grid-template-columns: repeat(4, minmax(0, 1fr)); }
}
@media (min-width: 1400px) {
  .rv-money { grid-template-columns: repeat(4, minmax(0, 1fr)); }
  .rv-rot { grid-template-columns: repeat(4, minmax(0, 1fr)); }
}

/* ============================================================
   复盘页 v2：与市场全景 / 个股分析 / 妖股雷达 同一套卡片体系
   ============================================================ */

body.rv {
  padding-top: 32px;
  padding-right: 32px;
  padding-bottom: 56px;
  background: var(--bg);
}
@media (max-width: 899px) {
  body.rv { padding-top: 14px; padding-right: 12px; padding-bottom: 40px; padding-left: 12px; }
}
body.rv #main { max-width: 1620px; margin: 0 auto; padding: 0; }

/* ---------------- 页内标题行 ---------------- */
.rv-head { display: flex; align-items: flex-start; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
.rv-head h1 { font-size: 30px; font-weight: 700; letter-spacing: -.02em; line-height: 1.1; }
.rv-sub {
  display: flex; align-items: center; gap: 7px; margin-top: 8px;
  font-size: 12.5px; color: var(--text-mute);
}
.rv-sub .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--down); flex: none; }
.rv-head-r { margin-left: auto; display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
body.rv .search-box {
  margin: 0; width: min(320px, 30vw); max-width: none;
  padding: 4px 6px 4px 14px; background: var(--panel);
  border: 1px solid var(--line); border-radius: 999px;
}
body.rv .search-box:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-weak); }
body.rv .search-box input { height: 32px; font-size: 13px; }
body.rv .search-box #searchBtn { border-radius: 999px; padding: 6px 16px; font-size: 12.5px; }
body.rv .search-box .suggest { top: calc(100% + 6px); left: 0; right: 0; }

/* ---------------- 白卡 ---------------- */
body.rv .rv-topbar,
body.rv .rv-sec {
  background: var(--panel);
  border: 0;
  border-top: 0;
  border-radius: 22px;
  padding: 20px 22px;
  margin-bottom: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, .05), 0 12px 28px -18px rgba(0, 0, 0, .20);
}
body.rv .rv-topbar { display: block; }
body.rv .rv-topbar .rv-title { margin-top: 6px; }
body.rv .rv-flow { gap: 16px; }
body.rv .rv-hits { margin-bottom: 0; }

/* 章节标题与其它页对齐 */
body.rv .rv-sec-title { font-size: 15px; font-weight: 700; letter-spacing: -.01em; }
body.rv .rv-no { color: var(--accent-2); font-weight: 700; }
body.rv .rv-sec-head { margin-bottom: 12px; }

@media (max-width: 899px) {
  .rv-head { flex-direction: column; gap: 12px; }
  .rv-head h1 { font-size: 24px; }
  .rv-head-r { margin-left: 0; width: 100%; }
  body.rv .search-box { width: 100%; }
  body.rv .rv-topbar,
  body.rv .rv-sec { padding: 16px; border-radius: 18px; }
}

/* ===== 深色主题兜底：亮底深字，避免「深字压深底」看不清 ===== */
.nav-btn.on,
.seg button.on {
  color: #04141c !important;
  background: linear-gradient(135deg, #22d3ee, #61e6c9) !important;
  border-color: transparent !important;
  box-shadow: 0 2px 10px -6px rgba(34, 211, 238, .55) !important;
}
"""
