/* ============================================================================
   watch-core.js —— 全站「加自选」星标（各页面共享）
   * nav.js 会自动加载并初始化本文件，页面无需再引 <script>
   * 用法一（模板里写死）：<button class="wstar" data-watch="600519.SH" title="加自选"></button>
   * 用法二（自动挂到个股分析页）：观察 #quoteCard 里的 .qc-code，把星标插到名称旁
   * 状态：已收录的按钮带 .on（样式在 nav.css）
   ========================================================================== */
(function () {
  'use strict';

  if (window.__WATCH_CORE__) return;
  window.__WATCH_CORE__ = true;

  var codes = {};          // {thscode: true}
  var loading = null;

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function paint() {
    var nodes = document.querySelectorAll('[data-watch]');
    for (var i = 0; i < nodes.length; i++) {
      var c = (nodes[i].getAttribute('data-watch') || '').toUpperCase();
      var on = !!codes[c];
      nodes[i].classList.toggle('on', on);
      nodes[i].setAttribute('title', on ? '已在自选，点击移出' : '加自选');
      nodes[i].setAttribute('aria-label', on ? '已在自选' : '加自选');
    }
  }

  function load() {
    if (loading) return loading;
    loading = fetch('/api/watchlist?action=ids', { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        codes = {};
        ((d && d.codes) || []).forEach(function (c) { codes[String(c).toUpperCase()] = true; });
        paint();
        return codes;
      })
      .catch(function () { return codes; })
      .then(function (v) { loading = null; return v; });
    return loading;
  }

  function toggle(code) {
    var c = String(code || '').toUpperCase();
    if (!c) return;
    var has = !!codes[c];
    var qs = 'action=' + (has ? 'remove' : 'add') + '&code=' + encodeURIComponent(c);
    fetch('/api/watchlist?' + qs, { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (!d || d.ok === false) throw new Error((d && d.error) || '操作失败');
        if (has) delete codes[c]; else codes[c] = true;
        paint();
      })
      .catch(function (e) {
        // 失败要让人看见，否则以为点了没反应
        var msg = '自选操作失败：' + (e.message || '未知错误');
        if (window.console && console.warn) console.warn(msg);
        alert(msg);
      });
  }

  function html(code, cls) {
    return '<button class="wstar' + (cls ? ' ' + cls : '') + '" type="button" data-watch="' +
      esc(String(code || '').toUpperCase()) + '" title="加自选" aria-label="加自选">★</button>';
  }

  /* 个股分析页：把星标自动插到 .qc-top 的名称旁 */
  function mountQuoteStar() {
    var card = document.getElementById('quoteCard');
    if (!card) return;
    var insert = function () {
      var codeEl = card.querySelector('.qc-code');
      var top = card.querySelector('.qc-top');
      if (!codeEl || !top || card.querySelector('.wstar')) return;
      var code = (codeEl.textContent || '').trim().toUpperCase();
      if (!/^\d{6}\.[A-Z]{2}$/.test(code)) return;
      var btn = document.createElement('span');
      btn.innerHTML = html(code, 'wstar-lg');
      var node = btn.firstChild;
      var nameRow = codeEl.parentNode;
      if (nameRow && nameRow.parentNode) nameRow.parentNode.appendChild(node);
      paint();
    };
    insert();
    try {
      new MutationObserver(insert).observe(card, { childList: true, subtree: true });
    } catch (ignore) { /* 老 WebView 没有 MutationObserver 就不自动插 */ }
  }

  function init() {
    document.addEventListener('click', function (e) {
      var t = e.target;
      if (!t || !t.closest) return;
      var b = t.closest('[data-watch]');
      if (!b) return;
      e.preventDefault();
      e.stopPropagation();
      toggle(b.getAttribute('data-watch'));
    }, true);
    load();
    mountQuoteStar();
  }

  window.Watch = { init: init, load: load, paint: paint, toggle: toggle, html: html,
                   has: function (c) { return !!codes[String(c || '').toUpperCase()]; } };
})();
