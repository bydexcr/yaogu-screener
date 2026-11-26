# -*- coding: utf-8 -*-
"""由 web/build_watchlist_assets.py 生成：APK 内嵌的自选股页资源（勿手改）"""

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light" id="metaColorScheme">
<meta name="theme-color" content="#f7f5f1" id="metaThemeColor">
<title>大A小散 · 自选股</title>
<link rel="stylesheet" href="/stock.css">
<link rel="stylesheet" href="/watchlist.css">
<link rel="stylesheet" href="/stock-dark.css" data-theme-dark media="not all">
<link rel="stylesheet" href="/nav.css">
<link rel="stylesheet" href="/pages-dark.css" data-theme-dark media="not all">
</head>
<body class="wl">
<aside class="side" id="appSide"></aside>

<main class="wl-main">
  <div class="wl-head">
    <div>
      <h1>自选股</h1>
      <p class="wl-sub" id="wlSub">加载中…</p>
    </div>
  </div>

  <form class="wl-add" id="wlForm" autocomplete="off">
    <input id="wlInput" type="search" enterkeyhint="search" spellcheck="false"
           placeholder="输入代码或名称，如 600519 / 贵州茅台">
    <button class="btn-primary" type="submit">＋ 加入自选</button>
    <div class="wl-sug" id="wlSug" hidden></div>
  </form>

  <div class="wl-portfolio" id="wlPortfolio" hidden></div>

  <div class="wl-tools">
    <button class="wl-tool" type="button" id="btnImport">批量导入</button>
    <a class="wl-tool" href="/api/watchlist?action=export" download="watchlist.csv">导出 CSV</a>
    <span class="wl-tip" id="wlDragTip">拖动行可排序</span>
  </div>

  <section class="wl-import" id="wlImport" hidden>
    <textarea id="wlText" spellcheck="false" placeholder="每行一个，支持这几种写法：&#10;600519 贵州茅台&#10;000001,平安银行&#10;sz300750&#10;（以 # 开头的行会被忽略）"></textarea>
    <div class="wl-import-foot">
      <span class="wl-tip" id="wlImportTip"></span>
      <button class="btn-ghost" type="button" id="wlCancel">取消</button>
      <button class="btn-primary" type="button" id="wlDoImport">导入</button>
    </div>
  </section>

  <div class="wl-list" id="wlList"></div>

  <div class="wl-empty" id="wlEmpty" hidden>
    <p class="wl-empty-t">还没有自选股</p>
    <p class="wl-empty-s">在上方输入代码/名称加入；也可在「个股分析」「妖股雷达」「市场全景」「复盘」里点股票旁的 ☆。</p>
  </div>

  <p class="wl-foot" id="wlFoot"></p>
</main>

<script src="/theme.js"></script>
<script src="/nav.js"></script>
<script src="/watchlist.js"></script>
</body>
</html>
"""

CSS = r"""/* ============================================================================
   自选股页（/watchlist）
   与复盘/全景同一套白卡体系：卡片 22px 圆角、表格行细分割线、等宽数字对齐。
   ========================================================================== */

body.wl {
  padding-top: 14px;
  padding-right: 18px;
  padding-bottom: 44px;
  padding-left: 18px;
}

.wl-main {
  max-width: 1240px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* ---------------------------------------------------------------- 标题 */
.wl-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; }
.wl-head h1 { font-size: 26px; letter-spacing: -.4px; }
.wl-sub { margin-top: 5px; font-size: 12.5px; color: var(--text-mute); font-family: var(--mono); }

/* ---------------------------------------------------------------- 添加框 */
.wl-add { position: relative; display: flex; gap: 8px; }
.wl-add input {
  flex: 1; min-width: 0; padding: 11px 13px; font: inherit; font-size: 13.5px;
  color: var(--text); background: var(--panel);
  border: 1px solid var(--line); border-radius: 12px;
}
.wl-add input:focus { outline: none; border-color: var(--accent); }
.wl-sug {
  position: absolute; top: calc(100% + 6px); left: 0; right: 0; z-index: 40;
  background: var(--panel); border: 1px solid var(--line); border-radius: 12px;
  box-shadow: 0 14px 34px rgba(0, 0, 0, .12); overflow: hidden;
}
.wl-sug button {
  display: flex; width: 100%; align-items: baseline; justify-content: space-between; gap: 12px;
  padding: 9px 13px; border: 0; background: none; color: var(--text);
  font: inherit; font-size: 13px; text-align: left; cursor: pointer;
}
.wl-sug button:hover { background: var(--panel-2); }
.wl-sug .cd { color: var(--text-mute); font-family: var(--mono); font-size: 11.5px; }

/* ---------------------------------------------------------------- 持仓汇总条 */
.wl-portfolio {
  display: flex; align-items: baseline; gap: 18px; flex-wrap: wrap;
  padding: 11px 16px; border-radius: 16px;
  background: #1b1a17; color: #f3efe6;
}
.wl-pf-t { font-size: 12px; font-weight: 700; letter-spacing: .3px; color: #d9a400; }
.wl-pf-i { display: inline-flex; align-items: baseline; gap: 6px; font-size: 12px; }
.wl-pf-i i { font-style: normal; color: rgba(243, 239, 230, .55); }
.wl-pf-i b {
  font-family: var(--mono); font-variant-numeric: tabular-nums;
  font-size: 13px; font-weight: 700; color: #f3efe6;
}
.wl-pf-i em { font-style: normal; font-family: var(--mono); font-size: 11px; color: rgba(243, 239, 230, .6); }
.wl-pf-i b.up, .wl-pf-i em.up { color: #ff6b6b; }
.wl-pf-i b.down, .wl-pf-i em.down { color: #4ade80; }
.wl-pf-hint { font-size: 11px; color: rgba(243, 239, 230, .45); }

/* ---------------------------------------------------------------- 工具条 */
.wl-tools { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.wl-tool {
  padding: 6px 11px; font: inherit; font-size: 12px; cursor: pointer;
  color: var(--text-dim); background: var(--panel); text-decoration: none;
  border: 1px solid var(--line); border-radius: 999px;
}
.wl-tool:hover { color: var(--text); border-color: var(--text-mute); }
.wl-tip { font-size: 11.5px; color: var(--text-mute); }

/* ---------------------------------------------------------------- 批量导入 */
.wl-import {
  display: flex; flex-direction: column; gap: 10px; padding: 14px;
  background: var(--panel); border: 1px solid var(--line); border-radius: 16px;
}
.wl-import textarea {
  min-height: 120px; resize: vertical; padding: 11px 12px; font: inherit;
  font-family: var(--mono); font-size: 12.5px; line-height: 1.7; color: var(--text);
  background: var(--panel-2); border: 1px solid var(--line); border-radius: 12px;
}
.wl-import textarea:focus { outline: none; border-color: var(--accent); }
.wl-import-foot { display: flex; align-items: center; justify-content: flex-end; gap: 8px; }
.wl-import-foot .wl-tip { margin-right: auto; }

/* ---------------------------------------------------------------- 列表 */
.wl-list {
  background: var(--panel); border: 1px solid var(--line);
  border-radius: 22px; overflow: hidden;
}

.wl-row {
  display: grid;
  grid-template-columns: 20px minmax(140px, 1.3fr) 112px 86px 64px 86px 72px 116px 116px minmax(64px, 1fr) 28px;
  align-items: center; gap: 10px;
  padding: 11px 16px 11px 10px;
  border-top: 1px solid var(--line-soft);
  cursor: grab;
}
.wl-row:first-child { border-top: 0; }
.wl-row:hover { background: var(--panel-2); }
.wl-row.dragging { opacity: .45; }
.wl-row.over { box-shadow: inset 0 2px 0 var(--accent); }

.wl-grip { color: var(--line); font-size: 13px; text-align: center; user-select: none; }
.wl-row:hover .wl-grip { color: var(--text-mute); }

.wl-name { min-width: 0; }
.wl-name a {
  display: block; font-size: 13.5px; font-weight: 650; color: var(--text);
  text-decoration: none; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.wl-name a:hover { color: var(--accent); }
.wl-name .cd { display: block; font-size: 11px; color: var(--text-mute); font-family: var(--mono); margin-top: 1px; }

.wl-px { text-align: right; font-family: var(--mono); font-variant-numeric: tabular-nums; }
.wl-px b { display: block; font-size: 13.5px; font-weight: 700; }
.wl-px span { display: block; font-size: 11.5px; margin-top: 1px; }

.wl-cell {
  font-family: var(--mono); font-variant-numeric: tabular-nums; font-size: 12px;
  color: var(--text-dim); text-align: right; white-space: nowrap;
}
.wl-cell.l { text-align: left; }

.wl-badge {
  display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px;
  font-family: var(--font); white-space: nowrap;
  background: var(--panel-3); color: var(--text-dim);
}
.wl-badge.hit { background: rgba(225, 29, 51, .12); color: var(--up); font-weight: 600; }
.wl-badge.deep { background: rgba(30, 79, 191, .12); color: var(--accent); }
.wl-badge.confirm { background: rgba(13, 155, 108, .12); color: var(--down); }
.wl-badge.broken { background: rgba(225, 29, 51, .1); color: var(--up); }
.wl-badge.cand { background: var(--panel-3); color: var(--text-dim); }
.wl-badge.none { background: transparent; color: var(--text-mute); border: 1px dashed var(--line); }

.wl-note {
  font-size: 11.5px; color: var(--text-mute); min-width: 0; cursor: text;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.wl-note:hover { color: var(--text-dim); }
.wl-note.empty { color: var(--line); }
.wl-note.empty:hover::after { content: '（点here写备注）'; }

.wl-rm {
  width: 26px; height: 26px; padding: 0; border: 0; border-radius: 8px;
  background: none; color: var(--text-mute); font-size: 15px; line-height: 1;
  cursor: pointer; opacity: 0;
}
.wl-row:hover .wl-rm { opacity: 1; }
.wl-rm:hover { background: rgba(225, 29, 51, .1); color: var(--up); }

/* ---------------------------------------------------------------- 持有 / 成本价 */
.wl-hold-cell { text-align: center; }
.wl-hold {
  padding: 3px 9px; font: inherit; font-size: 11px; line-height: 1.5; cursor: pointer;
  color: var(--text-mute); background: transparent;
  border: 1px dashed var(--line); border-radius: 999px; white-space: nowrap;
}
.wl-hold:hover { color: var(--text); border-color: var(--text-mute); border-style: solid; }
.wl-hold.on {
  color: #fff; background: #1b1a17; border: 1px solid #1b1a17; font-weight: 600;
}

.wl-cost-cell { display: flex; align-items: center; gap: 6px; justify-content: flex-end; }
.wl-cost {
  width: 84px; padding: 5px 8px; font: inherit; font-size: 12px;
  font-family: var(--mono); font-variant-numeric: tabular-nums; text-align: right;
  color: var(--text); background: var(--panel-2);
  border: 1px solid var(--line); border-radius: 8px; -moz-appearance: textfield;
}
.wl-cost::-webkit-outer-spin-button,
.wl-cost::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
.wl-cost:focus { outline: none; border-color: var(--accent); background: var(--panel); }
.wl-cost-ph { font-family: var(--mono); color: var(--line); font-size: 12px; }

.wl-qty-cell {
  display: flex; flex-direction: column; align-items: flex-end; gap: 1px;
  justify-content: center; line-height: 1.15;
}
.wl-qty {
  width: 74px; padding: 5px 7px; font: inherit; font-size: 12px;
  font-family: var(--mono); font-variant-numeric: tabular-nums; text-align: right;
  color: var(--text); background: var(--panel-2);
  border: 1px solid var(--line); border-radius: 8px; -moz-appearance: textfield;
}
.wl-qty::-webkit-outer-spin-button,
.wl-qty::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
.wl-qty:focus { outline: none; border-color: var(--accent); background: var(--panel); }
.wl-qty-cell small { font-family: var(--mono); font-size: 10.5px; color: var(--text-mute); }

.wl-pnl {
  font-family: var(--mono); font-variant-numeric: tabular-nums;
  font-size: 11.5px; font-weight: 650; white-space: nowrap;
}

/* ---------------------------------------------------------------- 空态 / 页脚 */
.wl-empty {
  padding: 46px 20px; text-align: center;
  background: var(--panel); border: 1px solid var(--line); border-radius: 22px;
}
.wl-empty-t { font-size: 14.5px; font-weight: 650; }
.wl-empty-s { margin-top: 7px; font-size: 12.5px; color: var(--text-mute); line-height: 1.8; }
.wl-foot { font-size: 11.5px; color: var(--text-mute); line-height: 1.8; }

/* 表头（桌面显示，手机隐藏） */
.wl-thead {
  display: grid;
  grid-template-columns: 20px minmax(140px, 1.3fr) 112px 86px 64px 86px 72px 116px 116px minmax(64px, 1fr) 28px;
  gap: 10px; padding: 9px 16px 9px 10px;
  font-size: 11px; color: var(--text-mute); background: var(--panel-2);
  border-bottom: 1px solid var(--line-soft);
}
.wl-thead .r { text-align: right; }
.wl-thead .c { text-align: center; }

/* ---------------------------------------------------------------- 手机端：卡片式 */
@media (max-width: 899px) {
  body.wl { padding-left: 12px; padding-right: 12px; }
  .wl-head h1 { font-size: 22px; }
  .wl-thead { display: none; }
  .wl-list { background: transparent; border: 0; border-radius: 0; display: flex; flex-direction: column; gap: 10px; }
  .wl-row {
    grid-template-columns: auto minmax(0, 1fr) auto;
    grid-template-areas:
      'grip name rm'
      'px px badge'
      'hold hold cost'
      'meta meta qty'
      'note note note';
    gap: 6px 10px; padding: 13px 14px; cursor: default;
    background: var(--panel); border: 1px solid var(--line); border-radius: 16px;
  }
  .wl-row:first-child { border-top: 1px solid var(--line); }
  .wl-grip { grid-area: grip; align-self: center; }
  .wl-name { grid-area: name; }
  .wl-px { grid-area: px; text-align: left; display: flex; align-items: baseline; gap: 8px; }
  .wl-px b, .wl-px span { display: inline; }
  .wl-badge, .wl-cell.badge-cell { grid-area: badge; text-align: right; }
  .wl-cell.c-turnover { grid-area: meta; text-align: left; }
  .wl-cell.c-t1 { display: none; }
  .wl-note { grid-area: note; white-space: normal; }
  .wl-rm { grid-area: rm; opacity: 1; width: 30px; height: 30px; }
  .wl-hold-cell { grid-area: hold; text-align: left; }
  .wl-cost-cell { grid-area: cost; justify-content: flex-end; }
  .wl-cost { width: 92px; }
  .wl-qty-cell { grid-area: qty; justify-content: flex-end; flex-direction: row; align-items: baseline; gap: 5px; }
  .wl-qty { width: 78px; }
  .wl-portfolio { gap: 12px; padding: 10px 13px; }
}
"""

JS = r"""/* ============================================================================
   自选股页逻辑（/watchlist）
   * 列表 + 实时行情 + T-1 涨幅 + 雷达状态
   * 拖拽排序、备注、删除、批量导入、CSV 导出
   * 手机端从电脑同步时，页脚会显示同步状态（synced / offline）
   ========================================================================== */
(function () {
  'use strict';

  var $ = function (s) { return document.querySelector(s); };
  var state = { items: [], loading: false, dragging: null, timer: null };

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function isNum(v) { return typeof v === 'number' && isFinite(v); }
  function pct(v) { return isNum(v) ? (v > 0 ? '+' : '') + v.toFixed(2) + '%' : '—'; }
  function cls(v) { return !isNum(v) ? '' : (v > 0 ? 'up' : (v < 0 ? 'down' : 'flat')); }
  function px(v) { return isNum(v) ? v.toFixed(2) : '—'; }
  function money2(v) {
    // 汇总/市值用两位小数：几万块的四舍五入成整数太糊
    if (!isNum(v)) return '—';
    var a = Math.abs(v);
    var sign = v < 0 ? '-' : '';
    if (a >= 1e8) return sign + (a / 1e8).toFixed(2) + ' 亿';
    if (a >= 1e4) return sign + (a / 1e4).toFixed(2) + ' 万';
    return sign + a.toFixed(0);
  }

  function money(v) {
    if (!isNum(v)) return '—';
    if (v >= 1e8) return (v / 1e8).toFixed(1) + ' 亿';
    if (v >= 1e4) return (v / 1e4).toFixed(0) + ' 万';
    return String(Math.round(v));
  }
  function url(code) { return '/stock?q=' + encodeURIComponent(code); }

  function api(qs) {
    var q = [];
    Object.keys(qs || {}).forEach(function (k) {
      var v = qs[k];
      if (v !== undefined && v !== null && v !== '') q.push(encodeURIComponent(k) + '=' + encodeURIComponent(v));
    });
    return fetch('/api/watchlist' + (q.length ? '?' + q.join('&') : ''), { cache: 'no-store' })
      .then(function (r) { return r.json(); });
  }

  /* ------------------------------------------------------------------ 渲染 */
  function badge(it) {
    var r = it.radar;
    if (!r || !r.status) return '<span class="wl-badge none">未入选</span>';
    var map = { '低开命中': 'hit', '深水命中': 'hit', '深水': 'deep', '承接': 'confirm',
                '走弱': 'broken', '候选': 'cand' };
    var c = map[r.status] || 'cand';
    var t = r.status;
    if (r.status === '候选' && r.continue_text) t = '候选·' + r.continue_text;
    return '<span class="wl-badge ' + c + '">' + esc(t) + '</span>';
  }

  function pnl(it) {
    // 盈亏 = 现价 / 成本 - 1；没成本或没行情就不显示
    if (!it.held || !isNum(it.cost) || !isNum(it.last) || it.cost <= 0) return '';
    var v = (it.last / it.cost - 1) * 100;
    return '<span class="wl-pnl ' + cls(v) + '" title="按成本价计算，未计手续费">' + pct(v) + '</span>';
  }

  function row(it) {
    var t1 = isNum(it.t1_pct) ? pct(it.t1_pct) : '—';
    var lim = it.radar && it.radar.t1_limitup ? '板' : '';
    var note = (it.note || '').trim();
    var held = !!it.held;
    return '<div class="wl-row" draggable="true" data-code="' + esc(it.thscode) + '">' +
      '<span class="wl-grip" title="拖动排序">⋮⋮</span>' +
      '<span class="wl-name"><a href="' + url(it.thscode) + '">' + esc(it.name) + '</a>' +
      '<span class="cd">' + esc(it.thscode) + '</span></span>' +
      '<span class="wl-px"><b class="' + cls(it.pct) + '">' + px(it.last) + '</b>' +
      '<span class="' + cls(it.pct) + '">' + pct(it.pct) + '</span></span>' +
      '<span class="wl-cell c-turnover">' + money(it.turnover) + '</span>' +
      '<span class="wl-cell c-t1 ' + cls(it.t1_pct) + '">' + t1 + lim + '</span>' +
      '<span class="wl-cell badge-cell" style="text-align:right">' + badge(it) + '</span>' +
      '<span class="wl-hold-cell"><button class="wl-hold' + (held ? ' on' : '') + '" type="button"' +
      ' data-hold="' + esc(it.thscode) + '" title="' + (held ? '点击改为未持有' : '点击标记为持有') + '">' +
      (held ? '持有' : '未持有') + '</button></span>' +
      '<span class="wl-cost-cell">' +
      (held
        ? '<input class="wl-cost" type="number" step="0.001" min="0" inputmode="decimal"' +
          ' data-cost="' + esc(it.thscode) + '" placeholder="成本价"' +
          ' value="' + (isNum(it.cost) ? it.cost : '') + '">' + pnl(it)
        : '<span class="wl-cost-ph">—</span>') +
      '</span>' +
      '<span class="wl-qty-cell">' +
      (held
        ? '<input class="wl-qty" type="number" step="100" min="0" inputmode="numeric"' +
          ' data-qty="' + esc(it.thscode) + '" placeholder="股数"' +
          ' value="' + (isNum(it.qty) ? it.qty : '') + '">' +
          (isNum(it.value) ? '<small>' + money2(it.value) + '</small>' : '')
        : '<span class="wl-cost-ph">—</span>') +
      '</span>' +
      '<span class="wl-note' + (note ? '' : ' empty') + '" data-note="' + esc(it.thscode) + '"' +
      ' title="点击写备注">' + (note ? esc(note) : '') + '</span>' +
      '<button class="wl-rm" type="button" data-rm="' + esc(it.thscode) + '" title="移出自选">×</button>' +
      '</div>';
  }

  function thead() {
    return '<div class="wl-thead"><span></span><span>名称 / 代码</span>' +
      '<span class="r">最新价</span><span class="r">成交额</span>' +
      '<span class="r">T-1</span><span class="r">雷达状态</span>' +
      '<span class="c">持有</span><span class="r">成本价 / 盈亏</span><span class="r">数量 / 市值</span>' +
      '<span>备注</span><span></span></div>';
  }

  function render() {
    var list = $('#wlList'), empty = $('#wlEmpty');
    var items = state.items || [];
    if (!items.length) {
      list.innerHTML = '';
      empty.hidden = false;
      return;
    }
    empty.hidden = true;
    list.innerHTML = thead() + items.map(row).join('');
    bindDrag();
  }

  function foot(d) {
    var el = $('#wlFoot');
    if (!el) return;
    var bits = [];
    if (isNum(d.count)) bits.push('共 ' + d.count + ' 只');
    if (d.updated) bits.push('更新 ' + d.updated);
    if (d.synced === false) bits.push('⚠ 未连上电脑，显示的是本地缓存');
    else if (d.sync_source) bits.push('同步自 ' + d.sync_source);
    bits.push('行情 20 秒自动刷新');
    el.textContent = bits.join(' · ');
  }

  function portfolioBar(d) {
    var p = d && d.portfolio;
    var box = $('#wlPortfolio');
    if (!box) return;
    if (!p || !p.held) { box.hidden = true; box.innerHTML = ''; return; }
    var bits = ['<span class="wl-pf-t">持仓</span>'];
    bits.push('<span class="wl-pf-i"><i>只数</i><b>' + p.held + '</b></span>');
    if (isNum(p.cost_amt)) {
      bits.push('<span class="wl-pf-i"><i>总成本</i><b>' + money2(p.cost_amt) + '</b></span>');
      bits.push('<span class="wl-pf-i"><i>市值</i><b>' + money2(p.value) + '</b></span>');
    }
    if (isNum(p.pnl_amt)) {
      bits.push('<span class="wl-pf-i"><i>浮动盈亏</i><b class="' + cls(p.pnl_amt) + '">' +
        (p.pnl_amt > 0 ? '+' : '') + money2(p.pnl_amt) + '</b>' +
        (isNum(p.pnl_pct) ? '<em class="' + cls(p.pnl_pct) + '">' + pct(p.pnl_pct) + '</em>' : '') +
        '</span>');
    } else if (isNum(p.pnl_pct)) {
      bits.push('<span class="wl-pf-i"><i>加权浮盈</i><b class="' + cls(p.pnl_pct) + '">' +
        pct(p.pnl_pct) + '</b><em>未填数量，仅按成本加权</em></span>');
    }
    if (isNum(p.today_amt)) {
      bits.push('<span class="wl-pf-i"><i>今日盈亏</i><b class="' + cls(p.today_amt) + '">' +
        (p.today_amt > 0 ? '+' : '') + money2(p.today_amt) + '</b></span>');
    }
    if (p.with_qty < p.held) {
      bits.push('<span class="wl-pf-hint">' + (p.held - p.with_qty) + ' 只未填数量，不计入金额</span>');
    }
    box.hidden = false;
    box.innerHTML = bits.join('');
  }

  function sub(d) {
    var el = $('#wlSub');
    if (!el) return;
    var n = (d.items || []).length;
    var hit = (d.items || []).filter(function (x) { return x.radar && x.radar.hit; }).length;
    var inPool = (d.items || []).filter(function (x) { return x.radar; }).length;
    el.textContent = n ? ('自选 ' + n + ' 只 · 今日在雷达池 ' + inPool + ' 只 · 已命中 ' + hit + ' 只')
                       : '还没有自选股';
  }

  /* ------------------------------------------------------------------ 加载 */
  function load(quiet) {
    if (state.loading) return Promise.resolve();
    state.loading = true;
    if (!quiet) $('#wlSub').textContent = '加载中…';
    return api({ action: 'list' })
      .then(function (d) {
        state.loading = false;
        if (!d || d.ok === false) throw new Error((d && d.error) || '接口异常');
        state.items = d.items || [];
        render(); sub(d); foot(d); portfolioBar(d);
      })
      .catch(function (e) {
        state.loading = false;
        if (!quiet) $('#wlSub').textContent = '加载失败：' + (e.message || '未知错误');
      });
  }

  function applyPromise(p) {
    return p.then(function (d) {
      if (!d || d.ok === false) throw new Error((d && d.error) || '操作失败');
      state.items = d.items || [];
      render(); sub(d); foot(d); portfolioBar(d);
      return d;
    });
  }

  /* ------------------------------------------------------------------ 拖拽排序 */
  function bindDrag() {
    var rows = Array.prototype.slice.call(document.querySelectorAll('.wl-row'));
    rows.forEach(function (row) {
      row.addEventListener('dragstart', function (e) {
        state.dragging = row.getAttribute('data-code');
        row.classList.add('dragging');
        try { e.dataTransfer.setData('text/plain', state.dragging); } catch (ignore) {}
        e.dataTransfer.effectAllowed = 'move';
      });
      row.addEventListener('dragend', function () {
        row.classList.remove('dragging');
        rows.forEach(function (r) { r.classList.remove('over'); });
        state.dragging = null;
      });
      row.addEventListener('dragover', function (e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        rows.forEach(function (r) { if (r !== row) r.classList.remove('over'); });
        row.classList.add('over');
      });
      row.addEventListener('drop', function (e) {
        e.preventDefault();
        row.classList.remove('over');
        var from = state.dragging;
        var to = row.getAttribute('data-code');
        if (!from || !to || from === to) return;
        var codes = state.items.map(function (x) { return x.thscode; });
        var i = codes.indexOf(from), j = codes.indexOf(to);
        if (i < 0 || j < 0) return;
        codes.splice(j, 0, codes.splice(i, 1)[0]);
        // 先在本地应用，界面立即响应；失败再回滚
        var byCode = {};
        state.items.forEach(function (x) { byCode[x.thscode] = x; });
        state.items = codes.map(function (c) { return byCode[c]; });
        render();
        applyPromise(api({ action: 'reorder', order: codes.join(',') })).catch(function (e) {
          $('#wlSub').textContent = '排序保存失败：' + e.message;
          load(true);
        });
      });
    });
  }

  /* ------------------------------------------------------------------ 搜索联想 */
  var sugTimer = null;
  function hideSug() { var s = $('#wlSug'); if (s) { s.hidden = true; s.innerHTML = ''; } }
  function showSug(items) {
    var box = $('#wlSug');
    if (!box) return;
    if (!items || !items.length) { hideSug(); return; }
    box.innerHTML = items.slice(0, 8).map(function (it) {
      return '<button type="button" data-code="' + esc(it.thscode) + '" data-name="' + esc(it.name || '') + '">' +
        '<span>' + esc(it.name || it.thscode) + '</span>' +
        '<span class="cd">' + esc(it.thscode || '') + '</span></button>';
    }).join('');
    box.hidden = false;
  }
  function search(q) {
    fetch('/api/search?q=' + encodeURIComponent(q), { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(function (d) { showSug((d && d.items) || []); })
      .catch(hideSug);
  }

  /* ------------------------------------------------------------------ 增删改 */
  function addStock(code) {
    if (!code) return;
    $('#wlSub').textContent = '正在加入 ' + code + ' …';
    applyPromise(api({ action: 'add', code: code })).then(function (d) {
      if (d.added === false) $('#wlSub').textContent = d.note || '已在自选里';
    }).catch(function (e) {
      $('#wlSub').textContent = '加入失败：' + e.message;
    });
  }

  function removeStock(code) {
    applyPromise(api({ action: 'remove', code: code })).catch(function (e) {
      $('#wlSub').textContent = '移除失败：' + e.message;
    });
  }

  function toggleHold(code, held) {
    applyPromise(api({ action: 'hold', code: code, held: held ? 1 : 0 })).catch(function (e) {
      $('#wlSub').textContent = '持有状态保存失败：' + e.message;
    });
  }

  function saveCost(code, value, input) {
    var v = (value || '').trim();
    if (v !== '' && !(Number(v) > 0)) {
      $('#wlSub').textContent = '成本价要大于 0';
      return;
    }
    var it = (state.items || []).filter(function (x) { return x.thscode === code; })[0];
    if (it && String(it.cost == null ? '' : it.cost) === v) return;   // 没改就不发请求
    if (input) input.disabled = true;
    applyPromise(api({ action: 'hold', code: code, held: 1, cost: v }))
      .then(function () {
        var fresh = (state.items || []).filter(function (x) { return x.thscode === code; })[0];
        if (fresh && !fresh.held) {                // 已在别处取消了持有
          $('#wlSub').textContent = '这只已不在持有里';
        }
      })
      .catch(function (e) {
        $('#wlSub').textContent = '成本价保存失败：' + e.message;
        if (input) input.disabled = false;
      });
  }

  function saveQty(code, value, input) {
    var v = (value || '').trim().replace(/,/g, '');
    if (v !== '' && !(Number(v) > 0)) {
      $('#wlSub').textContent = '持股数量要大于 0';
      return;
    }
    if (v !== '' && Number(v) !== Math.round(Number(v))) {
      $('#wlSub').textContent = '持股数量需为整数（股）';
      return;
    }
    var it = (state.items || []).filter(function (x) { return x.thscode === code; })[0];
    if (it && String(it.qty == null ? '' : it.qty) === v) return;
    if (input) input.disabled = true;
    applyPromise(api({
      action: 'hold', code: code, held: 1,
      cost: (it && it.cost != null) ? it.cost : '', qty: v
    })).catch(function (e) {
      $('#wlSub').textContent = '数量保存失败：' + e.message;
      if (input) input.disabled = false;
    });
  }

  function editNote(code) {
    var it = (state.items || []).filter(function (x) { return x.thscode === code; })[0];
    var cur = (it && it.note) || '';
    var v = window.prompt('备注（最多 120 字，留空清除）', cur);
    if (v === null) return;
    applyPromise(api({ action: 'note', code: code, note: v.trim() })).catch(function (e) {
      $('#wlSub').textContent = '备注保存失败：' + e.message;
    });
  }

  /* ------------------------------------------------------------------ 事件 */
  function bind() {
    $('#wlForm').addEventListener('submit', function (e) {
      e.preventDefault();
      var v = ($('#wlInput').value || '').trim();
      if (!v) return;
      hideSug();
      if (/^[0-9]{6}/.test(v) || /\.[A-Za-z]{2}$/.test(v)) {
        addStock(v);
        $('#wlInput').value = '';
        return;
      }
      // 名称：取联想第一条
      fetch('/api/search?q=' + encodeURIComponent(v), { cache: 'no-store' })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          var first = ((d && d.items) || [])[0];
          if (first && first.thscode) { addStock(first.thscode); $('#wlInput').value = ''; }
          else $('#wlSub').textContent = '没找到「' + v + '」';
        })
        .catch(function () { $('#wlSub').textContent = '搜索失败'; });
    });

    $('#wlInput').addEventListener('input', function () {
      var v = (this.value || '').trim();
      clearTimeout(sugTimer);
      if (v.length < 2) { hideSug(); return; }
      sugTimer = setTimeout(function () { search(v); }, 220);
    });
    $('#wlInput').addEventListener('blur', function () { setTimeout(hideSug, 160); });
    $('#wlSug').addEventListener('click', function (e) {
      var b = e.target && e.target.closest ? e.target.closest('button[data-code]') : null;
      if (!b) return;
      addStock(b.getAttribute('data-code'));
      hideSug();
      $('#wlInput').value = '';
    });

    $('#wlList').addEventListener('click', function (e) {
      var rm = e.target.closest ? e.target.closest('[data-rm]') : null;
      if (rm) { removeStock(rm.getAttribute('data-rm')); return; }
      var hd = e.target.closest ? e.target.closest('[data-hold]') : null;
      if (hd) {
        var code = hd.getAttribute('data-hold');
        var cur = (state.items || []).filter(function (x) { return x.thscode === code; })[0];
        toggleHold(code, !(cur && cur.held));
        return;
      }
      var nt = e.target.closest ? e.target.closest('[data-note]') : null;
      if (nt) { editNote(nt.getAttribute('data-note')); }
    });

    // 成本价：失焦或回车保存（input 事件不保存，避免每敲一个数字就打接口）
    $('#wlList').addEventListener('change', function (e) {
      var c = e.target;
      if (!c || !c.getAttribute) return;
      if (c.getAttribute('data-cost')) { saveCost(c.getAttribute('data-cost'), c.value, c); return; }
      if (c.getAttribute('data-qty')) { saveQty(c.getAttribute('data-qty'), c.value, c); }
    });
    $('#wlList').addEventListener('keydown', function (e) {
      var c = e.target;
      if (!c || !c.getAttribute) return;
      if (!c.getAttribute('data-cost') && !c.getAttribute('data-qty')) return;
      if (e.key === 'Enter') { e.preventDefault(); c.blur(); }
    });
    // 点输入框不要触发拖拽
    $('#wlList').addEventListener('mousedown', function (e) {
      var t2 = e.target;
      if (t2 && t2.tagName === 'INPUT') {
        var row = t2.closest('.wl-row');
        if (row) row.setAttribute('draggable', 'false');
      }
    });
    $('#wlList').addEventListener('mouseup', function (e) {
      var t3 = e.target;
      if (t3 && t3.tagName === 'INPUT') {
        var row2 = t3.closest('.wl-row');
        if (row2) row2.setAttribute('draggable', 'true');
      }
    });

    $('#btnImport').addEventListener('click', function () {
      var box = $('#wlImport');
      box.hidden = !box.hidden;
      if (!box.hidden) { $('#wlText').focus(); $('#wlImportTip').textContent = ''; }
    });
    $('#wlCancel').addEventListener('click', function () {
      $('#wlImport').hidden = true;
    });
    $('#wlDoImport').addEventListener('click', function () {
      var text = ($('#wlText').value || '').trim();
      if (!text) { $('#wlImportTip').textContent = '先粘贴要导入的代码'; return; }
      $('#wlImportTip').textContent = '导入中…';
      api({ action: 'batch', text: text }).then(function (d) {
        if (!d || d.ok === false) throw new Error((d && d.error) || '导入失败');
        state.items = d.items || [];
        render(); sub(d); foot(d); portfolioBar(d);
        var added = (d.added || []).length;
        $('#wlImportTip').textContent = '新增 ' + added + ' 只' +
          (d.skipped ? '，跳过 ' + d.skipped + '（已存在或重复）' : '');
        $('#wlText').value = '';
      }).catch(function (e) {
        $('#wlImportTip').textContent = '导入失败：' + e.message;
      });
    });
  }

  /* ------------------------------------------------------------------ 启动 */
  function boot() {
    bind();
    load(false);
    state.timer = setInterval(function () {
      if (document.visibilityState === 'visible' && !state.dragging) load(true);
    }, 20000);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
"""
