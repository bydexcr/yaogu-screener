/* 主题切换（浅色 / 深色）：入口在「设置」面板里（桌面端顶栏 ⚙；手机端走原生设置页） */
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

  // ---------------- 设置面板 ----------------
  function openSheet(open) {
    var mask = document.getElementById('settingsMask');
    if (!mask) return;
    mask.hidden = !open;
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
      if (e.key === 'Escape') openSheet(false);
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
