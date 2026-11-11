/* 主题切换（浅色 / 深色）：按钮固定在右下角，选择记在 localStorage */
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
