/* nav.js —— 左侧导航栏渲染（四个页面共用；只生成结构，样式在 nav.css） */
(function () {
  'use strict';

  var ICON = {
    grid: '<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/>' +
          '<rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
    candle: '<path d="M7 4v16M7 8h4v8H7zM17 6v12M15 10h4v6h-4z"/>',
    radar: '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 12l6-4"/>',
    note: '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/>',
    clock: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    gear: '<circle cx="12" cy="12" r="3"/><path d="M19 12a7 7 0 0 0-.1-1.2l2-1.5-2-3.4-2.3 1a7 7 0 0 0-2-1.2L14.2 3H9.8l-.4 2.7a7 7 0 0 0-2 1.2l-2.3-1-2 3.4 2 1.5A7 7 0 0 0 5 12c0 .4 0 .8.1 1.2l-2 1.5 2 3.4 2.3-1a7 7 0 0 0 2 1.2l.4 2.7h4.4l.4-2.7a7 7 0 0 0 2-1.2l2.3 1 2-3.4-2-1.5c.1-.4.1-.8.1-1.2z"/>'
  };

  // key: 用来判断当前高亮的路径；settings 不开新页，直接呼出设置面板
  // short: 窄屏（手机）用的短标签。6 个完整标签在 440px 宽的手机上排不下，
  // 横向滚动条会把文字切一半（"股分析"、"历5"），所以窄屏直接换短名。
  var ITEMS = [
    { key: '/', href: '/', name: '市场全景', short: '全景', icon: 'grid' },
    { key: '/stock', href: '/stock', name: '个股分析', short: '分析', icon: 'candle' },
    { key: '/radar', href: '/radar', name: '妖股雷达', short: '雷达', icon: 'radar', badge: true },
    { key: '/review', href: '/review', name: '复盘', short: '复盘', icon: 'note' },
    { key: '/review#hits', href: '/review#hits', name: '历史', short: '历史', icon: 'clock' },
    { key: 'settings', href: '', name: '设置', short: '设置', icon: 'gear' }
  ];

  function svg(name) {
    return '<svg class="side-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
      'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      (ICON[name] || '') + '</svg>';
  }

  function currentKey() {
    var p = (location.pathname || '/').replace(/\/+$/, '') || '/';
    if (p === '/index.html') p = '/stock';
    if (p === '/overview' || p === '/overview.html') p = '/';
    if (p === '/review' && /(^|#)hits$/.test(location.hash || '')) return '/review#hits';
    return p;
  }

  // 窄屏换短标签，避免横向溢出把文字切一半
  function fitLabels() {
    var narrow = window.innerWidth < 680;   // 实测 6 个完整标签 + 图标要 ~625px 才排得下
    var nodes = document.querySelectorAll('.side-nav a > span[data-full]');
    for (var i = 0; i < nodes.length; i++) {
      var n = nodes[i];
      n.textContent = narrow ? n.getAttribute('data-short') : n.getAttribute('data-full');
    }
  }

  function render() {
    var host = document.getElementById('appSide');
    if (!host) return;
    var active = currentKey();
    host.innerHTML =
      '<div class="side-logo"><i>散</i><b>大A小散</b></div>' +
      '<div class="side-who"><div class="av"></div><p>Welcome back,</p><b>盯盘模式</b></div>' +
      '<nav class="side-nav">' + ITEMS.map(function (it) {
        var on = it.key === active ? ' on' : '';
        var bdg = it.badge ? '<span class="side-bdg" hidden></span>' : '';
        return '<a class="' + (on ? 'on' : '') + '" data-key="' + it.key + '"' +
          (it.href ? ' href="' + it.href + '"' : ' role="button" tabindex="0"') + '>' +
          svg(it.icon) + '<span data-full="' + it.name + '" data-short="' + (it.short || it.name) +
          '">' + it.name + '</span>' + bdg + '</a>';
      }).join('') + '</nav>' +
      '<div class="side-foot">数据源 同花顺金融数据服务<br>仅供技术研究与复盘</div>';

    var set = host.querySelector('[data-key="settings"]');
    if (set) {
      var open = function (e) {
        e.preventDefault();
        if (window.__openSheet) window.__openSheet(true);
      };
      set.addEventListener('click', open);
      set.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') open(e);
      });
    }
    if (document.body) document.body.classList.add('has-side');
  // 移动端导航条是横向滚动的，当前页可能在屏幕外（复盘/历史/设置），
  // 进来先把当前项滚到可视区中间。block:'nearest' 避免顺带把页面纵向滚走。
  fitLabels();
  window.addEventListener('resize', fitLabels);

  try {
    var cur = host.querySelector('.side-nav a.on');
    if (cur && window.innerWidth < 900 && cur.scrollIntoView) {
      cur.scrollIntoView({ block: 'nearest', inline: 'center' });
    }
  } catch (e) { /* 老 WebView 不支持对象参数，忽略 */ }
    loadBadge(host);
  }

  // 妖股雷达徽章 = 当前承接确认只数（拿不到就不显示，不编数字）
  function loadBadge(host) {
    var el = host.querySelector('.side-bdg');
    if (!el) return;
    fetch('/api/state', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
      var n = ((d || {}).watch || {}).confirm || 0;
      if (n > 0) { el.textContent = String(n); el.hidden = false; }
    }).catch(function () { /* 忽略 */ });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', render);
  } else {
    render();
  }
})();
