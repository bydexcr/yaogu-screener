/* overview.js —— 市场全景页渲染（数据全部来自 /api/overview） */
(function () {
  'use strict';

  var $ = function (s) { return document.querySelector(s); };
  var esc = function (s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  };
  var isNum = function (v) { return typeof v === 'number' && isFinite(v); };
  var pct = function (v, d) {
    if (!isNum(v)) return '—';
    d = d == null ? 2 : d;
    return (v > 0 ? '+' : '') + v.toFixed(d) + '%';
  };
  var yi = function (v) { return isNum(v) ? (v / 1e8).toFixed(1) + ' 亿' : '—'; };
  var big = function (v) {
    if (!isNum(v)) return '—';
    if (Math.abs(v) >= 1e8) return (v / 1e8).toFixed(2) + ' 亿';
    if (Math.abs(v) >= 1e4) return (v / 1e4).toFixed(1) + ' 万';
    return String(Math.round(v));
  };
  var amtParts = function (v) {
    v = isNum(v) ? v : 0;
    return v >= 1e12 ? [(v / 1e12).toFixed(2), '万亿'] : [Math.round(v / 1e8), '亿'];
  };
  var upDown = function (v) { return !isNum(v) ? '' : (v > 0 ? 'up' : (v < 0 ? 'down' : '')); };

  var state = { data: null, hot: 'hot' };

  /* 盘前/未开盘：breadth 各桶全 0 —— 这时候不要摆一排 0，直接说"盘前" */
  function isEmptyMarket(d) {
    var b = (d || {}).breadth || {};
    var sum = 0;
    (b.buckets || []).forEach(function (x) { sum += x.count || 0; });
    return sum === 0 && !b.up && !b.down;
  }

  /* ---------------------------------------------------------------- 涨跌分布柱状 */
  function bars(buckets) {
    if (!buckets || !buckets.length) return '<div class="ov-skel">暂无涨跌分布数据</div>';
    // 按容器实际宽度出图：固定 920 宽的 viewBox 在手机上会被整体缩到 ~39%，
    // 11.5px 的刻度字只剩 4~5px，等于看不见。窄屏就让 viewBox 跟着窄。
    var host = document.getElementById('ovBars');   // 注意：本文件里 el 是错误处理里的局部变量，不是工具函数
    var avail = host ? host.clientWidth : 0;
    var W = avail > 280 ? Math.min(avail, 920) : 920;
    var H = Math.round(W * (W >= 700 ? 470 / 920 : 0.62));   // 窄屏略矮一点，别占满一屏
    if (H < 260) H = 260;
    var padL = 10, padB = 44, padT = 42, padR = 10;
    var innerW = W - padL - padR, innerH = H - padT - padB;
    var mx = 0;
    buckets.forEach(function (b) { mx = Math.max(mx, b.count || 0); });
    mx = mx || 1;
    var step = innerW / buckets.length, bw = step * 0.52, out = '';
    // 窄屏（手机）8 个刻度挤在一行会连成一片：去掉 % 号，配合 CSS 把字号压到 10px
    var narrow = W < 520;
    var thin = function (s) {
      return String(s).replace('%', '').replace('≤', '<').replace('≥', '>');
    };
    buckets.forEach(function (b, i) {
      var h = (b.count || 0) / mx * innerH;
      var x = padL + i * step + (step - bw) / 2;
      var y = padT + innerH - h;
      // 颜色交给 CSS（.ov-bar / .ov-bar-hi），深色主题的映射才能作用到柱子上
      var cls = b.label === '0~3%' ? 'ov-bar ov-bar-hi' : 'ov-bar';
      out += '<rect class="' + cls + '" x="' + x.toFixed(1) + '" y="' + y.toFixed(1) +
        '" width="' + bw.toFixed(1) + '" height="' + Math.max(h, 2).toFixed(1) + '" rx="3"/>' +
        '<text x="' + (x + bw / 2).toFixed(1) + '" y="' + (y - 9).toFixed(1) + '" text-anchor="middle">' +
        (b.count || 0) + '</text>' +
        '<text x="' + (x + bw / 2).toFixed(1) + '" y="' + (H - 24) + '" text-anchor="middle">' +
        esc(narrow ? thin(b.label) : b.label) + '</text>';
    });
    out += '<line x1="' + padL + '" y1="' + (padT + innerH) + '" x2="' + (W - padR) + '" y2="' +
      (padT + innerH) + '" stroke="var(--line-soft)"/>';
    return '<svg class="ov-chart" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="涨跌分布">' + out + '</svg>';
  }

  /* ---------------------------------------------------------------- 封板率环形 */
  function donut(seal, brk, down) {
    var size = 190, r = 66, C = 2 * Math.PI * r, cx = size / 2;
    var rest = 100 - seal, tot = (brk + down) || 1, acc = 0;
    var segs = [
      [seal, '#e8c87a'],
      [rest * brk / tot, '#b7addf'],
      [rest * down / tot, '#e2dbcb']
    ];
    var out = '<svg viewBox="0 0 ' + size + ' ' + size + '" width="' + size + '" height="' + size +
      '" role="img" aria-label="封板率">';
    segs.forEach(function (s) {
      var len = C * s[0] / 100;
      out += '<circle cx="' + cx + '" cy="' + cx + '" r="' + r + '" fill="none" stroke="' + s[1] +
        '" stroke-width="26" stroke-dasharray="' + len.toFixed(2) + ' ' + (C - len).toFixed(2) +
        '" stroke-dashoffset="' + (-(C * acc / 100)).toFixed(2) + '" transform="rotate(-90 ' + cx + ' ' + cx + ')"/>';
      acc += s[0];
    });
    out += '</svg>';
    return out + '<div class="c"><div><i>封板率</i><b>' + (isNum(seal) ? seal.toFixed(1) : '—') + '%</b></div></div>';
  }

  /* ---------------------------------------------------------------- 各区块 */
  function renderHead(d) {
    var b = d.breadth || {}, lim = d.limits || {}, copy = d.copy || {};
    var pre = isEmptyMarket(d);
    var t = d.tradeDate || '—', gen = (d.generatedAt || '').slice(11, 19);
    $('#ovMeta').textContent = t + ' · 全市场 ' + (b.total || 0) + ' 只' +
      (gen ? ' · ' + gen : '') + (pre ? ' · 盘前，开盘后自动更新' : '');

    $('#ovPillTotal').textContent = '全市场';
    $('#ovUpDown').innerHTML = pre ? '—'
      : (b.up || 0) + ' <small>涨</small> / ' + (b.down || 0) + ' <small>跌</small>';
    $('#ovUpDownSub').innerHTML = pre ? '等待开盘'
      : '上涨占比 <em>' + (isNum(b.upRatio) ? b.upRatio.toFixed(1) : '—') +
        '%</em> · 平盘 ' + (b.flat || 0) + ' · 平均 <em>' + pct(b.avg, 2) + '</em>';

    var a = amtParts(b.turnover);
    $('#ovPillAmt').textContent = Math.round((b.turnover || 0) / 1e8) + ' 亿';
    $('#ovAmt').innerHTML = pre ? '—' : a[0] + ' <small>' + a[1] + '</small>';
    $('#ovAmtSub').innerHTML = '沪 + 深合计 · 覆盖 ' + (b.total || 0) + ' 只<a class="link" href="/radar">看资金流</a>';

    $('#ovPillMood').textContent = copy.mood || '—';
    $('#ovLimit').innerHTML = pre ? '—'
      : (lim.limitUpCount || 0) + ' <small>涨停</small> / ' +
        (lim.limitDownCount || 0) + ' <small>跌停</small>';
    $('#ovLimitSub').innerHTML = pre ? '等待开盘'
      : '封板率 <em>' + (isNum(lim.sealRate) ? lim.sealRate.toFixed(1) : '—') +
        '%</em> · 炸板 ' + (lim.breakCount || 0) + ' · 最高 ' + Math.round(lim.highestBoard || 0) + ' 板';
  }

  function renderDist(d) {
    if (isEmptyMarket(d)) {
      $('#ovBars').innerHTML = '<div class="ov-skel">盘前暂无涨跌分布，开盘后自动更新</div>';
      $('#ovDist').textContent = '';
      return;
    }
    $('#ovBars').innerHTML = bars((d.breadth || {}).buckets || []);
    $('#ovDist').textContent = (d.copy || {}).distribution || '';
  }

  function renderSectors(d) {
    var sec = d.sectors || {}, boards = ((sec.boards || {}).l1 || []).slice().sort(function (x, y) {
      return (y.changePct || -999) - (x.changePct || -999);
    });
    $('#ovSectorHint').textContent = '前 4 / 共 ' + ((sec.totals || {}).l1 || 0);
    $('#ovSectorBody').innerHTML = boards.slice(0, 4).map(function (b) {
      var ld = b.leader || {};
      return '<tr><td><span class="nm">' + esc(b.name) + '</span>' +
        '<span class="nm2">' + (b.memberCount || 0) + ' 只 · 涨' + (b.upCount || 0) + '/跌' + (b.downCount || 0) + '</span></td>' +
        '<td class="ld">' + esc(ld.name || '—') + '<i>' + pct(ld.changePct) + '</i></td>' +
        '<td>' + pct(b.changePct) + '</td><td>' + yi(b.turnover) + '</td></tr>';
    }).join('');
    $('#ovStruct').textContent = (d.copy || {}).structure || '';
    var b = d.breadth || {};
    $('#ovChips').innerHTML = [['全市场', b.total], ['上涨', b.up], ['下跌', b.down], ['平盘', b.flat]]
      .map(function (x) { return '<span class="ov-chip">' + x[0] + '<b>' + (x[1] == null ? '—' : x[1]) + '</b></span>'; })
      .join('');
    $('#ovTopHint').textContent = '全部 ' + ((sec.totals || {}).l1 || 0);
    $('#ovTop4').innerHTML = boards.slice(0, 4).map(function (b, i) {
      var ld = b.leader || {};
      return '<div class="ov-t4"><span class="ov-rk">' + (i < 9 ? '0' : '') + (i + 1) + '</span>' +
        '<span><span class="nm">' + esc(b.name) + '</span><span class="nm2">' + esc(ld.name || '—') + ' ' +
        pct(ld.changePct) + '</span></span>' +
        '<span class="v">' + pct(b.changePct) + '<small>' + yi(b.turnover) + '</small></span></div>';
    }).join('');
  }

  function renderSeal(d) {
    var lim = d.limits || {}, pre = isEmptyMarket(d);
    $('#ovSealHint').textContent = '涨停 ' + (lim.limitUpCount || 0) + ' / 炸板 ' + (lim.breakCount || 0);
    if (pre) {
      $('#ovDonut').innerHTML = donut(0, 0, 0);
      var c = $('#ovDonut').querySelector('.c b');
      if (c) c.textContent = '—';
    } else {
      $('#ovDonut').innerHTML = donut(lim.sealRate || 0, lim.breakCount || 0, lim.limitDownCount || 0);
    }
    $('#ovLeg').innerHTML = [['守住涨停', lim.limitUpCount, '#e8c87a'], ['炸板', lim.breakCount, '#b7addf'],
      ['跌停', lim.limitDownCount, '#e2dbcb']].map(function (x) {
      return '<div><i style="background:' + x[2] + '"></i>' + x[0] + '<b>' +
        (pre ? '—' : (x[1] || 0)) + '</b></div>';
    }).join('');
  }

  /* ---------------------------------------------------------------- 热门个股（三档） */
  function renderHot() {
    var hot = (state.data || {}).hot || {};
    var list, view;
    if (state.hot === 'amt') {
      view = (hot.turnoverTop || []).slice().sort(function (x, y) { return (y.turnover || 0) - (x.turnover || 0); });
      list = view.slice(0, 4).map(function (s) {
        return { name: s.name, sub: (s.ticker || s.thscode || '') + ' · ' + pct(s.changePct),
                 v: big(s.turnover), unit: '成交额' };
      });
    } else if (state.hot === 'lhb') {
      view = (hot.dragonTiger || []).slice().sort(function (x, y) { return (y.netValue || 0) - (x.netValue || 0); });
      list = view.slice(0, 4).map(function (s) {
        return { name: s.name, sub: (s.thscode || '') + ' · ' + pct(s.changePct),
                 v: (s.netValue > 0 ? '+' : '') + big(s.netValue), unit: '净额' };
      });
    } else {
      view = (hot.hot || []).slice(0, 4);
      list = view.map(function (s) {
        return { name: s.name, sub: (s.ticker || s.thscode || '') + ' · 人气第 ' + Math.round(s.rank || 0),
                 v: big(s.heat), unit: '热度' };
      });
    }
    $('#ovHot').innerHTML = list.length ? list.map(function (s, i) {
      return '<div class="r"><span class="ov-rk">' + (i < 9 ? '0' : '') + (i + 1) + '</span>' +
        '<span><span class="nm">' + esc(s.name) + '</span><span class="nm2">' + esc(s.sub) + '</span></span>' +
        '<span class="v">' + s.v + '<small>' + s.unit + '</small></span></div>';
    }).join('') : '<div class="ov-skel">暂无数据</div>';

    // 跨榜对照：缺哪一榜就只说有的，别输出「—（—）」这种空括号
    var amt0 = ((hot.turnoverTop || [])[0] || {}), lhb0 = ((hot.dragonTiger || [])[0] || {});
    var bits = ['人气榜前 ' + list.length];
    if (amt0.name) bits.push('成交额榜首位 ' + amt0.name + '（' + big(amt0.turnover) + '）');
    if (lhb0.name && isNum(lhb0.netValue)) {
      bits.push('龙虎榜净买首位 ' + lhb0.name +
        '（' + (lhb0.netValue > 0 ? '+' : '') + big(lhb0.netValue) + '）');
    }
    $('#ovHotNote').textContent = bits.join('；') + '。';
  }

  function renderTail(d) {
    var lim = d.limits || {}, pre = isEmptyMarket(d);
    var one = (d.copy || {}).oneSentence;
    var p = $('#ovOne');
    if (one) {
      p.innerHTML = one;
      p.classList.remove('muted');
    } else {
      p.textContent = pre ? '盘前，开盘后自动生成今日一句' : '暂无';
      p.classList.add('muted');
    }
    $('#ovBrief').innerHTML = [
      ['涨停 / 跌停', (lim.limitUpCount || 0) + ' / ' + (lim.limitDownCount || 0)],
      ['炸板', lim.breakCount || 0],
      ['封板率', (isNum(lim.sealRate) ? lim.sealRate.toFixed(1) : '—') + '%'],
      ['最高连板', Math.round(lim.highestBoard || 0) + ' 板']
    ].map(function (x) {
      return '<div class="ov-kv">' + x[0] + '<b>' + (pre ? '—' : x[1]) + '</b></div>';
    }).join('');
    var gen = (d.generatedAt || '').slice(11, 19);
    $('#ovSrc').innerHTML = '数据源 同花顺金融数据服务' + (gen ? ' · 生成于 ' + esc(gen) : '') +
      '<br>仅供技术研究与复盘，不构成投资建议';
  }

  function render(d) {
    state.data = d;
    renderHead(d); renderDist(d); renderSectors(d); renderSeal(d);
    renderHot(); renderTail(d);
  }

  function showError(msg) {
    var el = document.getElementById('ovBars');
    if (el) el.innerHTML = '<div class="ov-err">市场全景加载失败：' + esc(msg) + '</div>';
    ['ovUpDown', 'ovAmt', 'ovLimit'].forEach(function (id) {
      var n = document.getElementById(id);
      if (n) n.textContent = '—';
    });
    var m = document.getElementById('ovMeta');
    if (m) m.textContent = '加载失败';
  }

  async function load() {
    try {
      var r = await fetch('/api/overview', { cache: 'no-store' });
      var d = await r.json();
      if (!d || d.ok === false) throw new Error((d && d.error) || '接口返回异常');
      render(d);
    } catch (e) {
      showError(e.message || '未知错误');
    }
  }

  function init() {
    document.getElementById('ovHotSeg').addEventListener('click', function (e) {
      var t = e.target && e.target.getAttribute('data-t');
      if (!t) return;
      state.hot = t;
      Array.prototype.forEach.call(this.querySelectorAll('span'), function (s) {
        s.classList.toggle('on', s === e.target);
      });
      renderHot();
    });
    var go = function () {
      var v = (document.getElementById('ovSearch').value || '').trim();
      if (v) location.href = '/stock?q=' + encodeURIComponent(v);
    };
    document.getElementById('ovGo').addEventListener('click', go);
    document.getElementById('ovSearch').addEventListener('keydown', function (e) {
      if (e.key === 'Enter') go();
    });
    load();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
