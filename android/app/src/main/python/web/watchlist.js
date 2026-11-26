/* ============================================================================
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
