/* 主题切换（浅色 / 深色）：入口在设置面板里（桌面端顶栏齿轮按钮；手机端走原生设置页） */
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
      // 焦点进面板即可，别聚焦某个按钮：按钮一拿到焦点，浏览器会画一圈默认黑描边，
      // 和整套配色完全不符（用户反馈的"关闭按钮底框不一致"就是这个）。
      // 聚焦容器同样能把 Tab 圈在面板里。
      try {
        mask.tabIndex = -1;
        mask.focus({ preventScroll: true });
      } catch (e) { /* 老 WebView 不支持 focus(options) */ mask.focus(); }
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

  // ?sheet=1（截图/排障用）必须在脚本求值时就记下来：
  // 个股分析页的 showMarket() 会 history.replaceState 清掉 query，
  // 等到 DOMContentLoaded 再读 location.search 就已经是空的了。
  var wantSheet = (function () {
    try { return new URLSearchParams(location.search).get('sheet') === '1'; } catch (e) { return false; }
  })();

  // 安卓端有 JS 桥（MainActivity 注入的 YaoguApp）时，才显示「数据接口与阈值」这一行；
  // 浏览器里没有桥，这一行保持隐藏。
  function initNativeBridge() {
    var row = document.getElementById('apiRow');
    var btn = document.getElementById('apiOpen');
    if (!row || !btn) return;
    var bridge = window.YaoguApp;
    if (!bridge || typeof bridge.openSettings !== 'function') return;
    row.hidden = false;
    btn.addEventListener('click', function () {
      try { bridge.openSettings(); } catch (e) { /* 忽略 */ }
    });
  }

  function init() {
    apply(fromQuery() || stored());
    initSheet();
    initNativeBridge();
    if (wantSheet) openSheet(true);
  }

  // 尽早切一次，避免深色用户看到浅色闪屏
  apply(fromQuery() || stored());
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
