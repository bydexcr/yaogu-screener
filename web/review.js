(function () {
  'use strict';

  const $ = (s) => document.querySelector(s);
  const el = (id) => document.getElementById(id);
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const isNum = (v) => typeof v === 'number' && Number.isFinite(v);
  const pct = (v, d = 2) => (isNum(v) ? `${v > 0 ? '+' : ''}${v.toFixed(d)}%` : '—');
  const cls = (v) => (!isNum(v) ? 'flat' : v > 0 ? 'up' : v < 0 ? 'down' : 'flat');
  const n2 = (v, d = 2) => (isNum(v) ? v.toFixed(d) : '—');
  const yi = (v) => (isNum(v) ? `${v > 0 ? '+' : ''}${v.toFixed(2)}` : '—');
  const money = (v) => {
    if (!isNum(v)) return '—';
    const a = Math.abs(v);
    if (a >= 1e12) return `${(v / 1e12).toFixed(2)}万亿`;
    if (a >= 1e8) return `${(v / 1e8).toFixed(2)}亿`;
    return `${(v / 1e4).toFixed(0)}万`;
  };

  const state = { data: null, loading: false, retry: 0 };

  /* ------------------------------------------------------------------ 通用小件 */
  function section(no, title, hint, body, extraClass) {
    return `<section class="rv-sec ${extraClass || ''}">
      <header class="rv-sec-head">
        <span class="rv-no">${esc(no)}</span>
        <h3 class="rv-sec-title">${esc(title)}</h3>
        ${hint ? `<span class="rv-sec-hint">${esc(hint)}</span>` : ''}
      </header>
      <div class="rv-sec-body">${body}</div>
    </section>`;
  }

  function kv(k, v, tone) {
    return `<div class="rv-kv"><span class="k">${esc(k)}</span><span class="v ${tone || ''}">${v}</span></div>`;
  }

  /* ------------------------------------------------------------------ 顶部条形 */
  function renderTop(d) {
    const head = d.head || {};
    el('rvSys').textContent = head.system || 'AI 复盘系统';
    el('rvTitle').textContent = head.title || `${d.date || '—'} 正式收复盘`;
    const heat = d.heat || {};
    el('rvRegime').textContent = head.regime || (d.env && d.env.regime && d.env.regime.name) || '—';
    el('rvHeat').textContent = `情绪 ${n2(heat.score, 1)} · ${heat.label || '—'}`;
    el('rvHeat').className = 'rv-tag heat ' + (heat.tone || 'mid');
    el('rvRisk').textContent = `风险等级 ${(d.risk || {}).level || '—'}`;
    el('rvArchived').hidden = !d.fromArchive;
    el('statusText').textContent = d.fromArchive ? '历史存档' : '今日快照';
    el('rvFoot').textContent = (d.disclaimer || '') +
      (d.archive && d.archive.count ? `　已存档 ${d.archive.count} 天。` : '');
  }

  /* ------------------------------------------------------------------ 1 一句话总收口 */
  function secOneLine(d) {
    const o = d.oneSentence || {};
    const body = `<p class="rv-verdict">${esc(o.verdict || '—')}</p>
      <ul class="rv-points">${(o.sentences || []).slice(1).map((s) => `<li>${esc(s)}</li>`).join('')}</ul>`;
    return section('1', '一句话总收口', '本日盘面定性', body, 'rv-wide');
  }

  /* ------------------------------------------------------------------ 2 盘型与环境 */
  function secEnv(d) {
    const e = d.env || {};
    const regime = e.regime || {};
    const idx = e.indices || [];
    const left = [
      kv('上涨家数', `<b class="up">${esc(e.up ?? '—')}</b>`),
      kv('下跌家数', `<b class="down">${esc(e.down ?? '—')}</b>`),
      kv('市场合计', `${esc(e.total ?? '—')} 只`),
      kv('封住涨停', `<b class="up">${esc(e.limitUp ?? '—')}</b> 只`),
      kv('炸板', `${esc(e.breakCount ?? '—')} 只`),
      kv('正式收报涨停率', `<b>${isNum(e.limitRate) ? e.limitRate.toFixed(2) + '%' : '—'}</b>`),
      kv('封板率', `${isNum(e.sealRate) ? e.sealRate.toFixed(1) + '%' : '—'}`),
      kv('最高连板', `${esc(e.highestBoard ?? '—')} 板`),
      kv('涨跌家数比', `${esc(e.up ?? 0)} : ${esc(e.down ?? 0)}`),
      kv('两市成交额', money(e.turnover)),
    ].join('');
    const right = idx.map((i) => `
      <div class="rv-idx-row">
        <span class="n">${esc(i.name)}</span>
        <span class="p ${cls(i.changePct)}">${n2(i.last, 2)}</span>
        <span class="c ${cls(i.changePct)}">${pct(i.changePct)}</span>
      </div>`).join('');
    const body = `<div class="rv-env">
        <div class="rv-env-left">
          <div class="rv-regime">
            <span class="rv-regime-name">${esc(regime.name || '—')}</span>
            <span class="rv-regime-flavor">${esc(regime.flavor || '')}</span>
          </div>
          <div class="rv-kvs">${left}</div>
        </div>
        <div class="rv-env-right">
          <div class="rv-idx-head"><span class="n">指数</span><span class="p">点位</span><span class="c">涨跌幅</span></div>
          ${right}
        </div>
      </div>`;
    return section('2', '盘型 / 环境', regime.text || '', body, 'rv-wide');
  }

  /* ------------------------------------------------------------------ 2.5 资金流证据 */
  function rankTable(rows, kind) {
    if (!rows || !rows.length) return '<div class="rv-empty">暂无数据</div>';
    const head = kind === 'stock'
      ? '<div class="rv-tb-head"><span>名称</span><span>涨跌幅</span><span>净额(亿)</span></div>'
      : '<div class="rv-tb-head"><span>板块</span><span>成分</span><span>净额(亿)</span></div>';
    const body = rows.map((r) => {
      if (kind === 'stock') {
        return `<div class="rv-tb-row" data-code="${esc(r.code || '')}">
          <span class="nm">${esc(r.name)}<small>${esc(r.code || '')}</small></span>
          <span class="${cls(r.changePct)}">${pct(r.changePct)}</span>
          <span class="${(r.net || 0) >= 0 ? 'up' : 'down'}">${yi(r.net)}</span></div>`;
      }
      return `<div class="rv-tb-row">
        <span class="nm">${esc(r.name)}</span>
        <span>${esc(r.count ?? '—')}</span>
        <span class="${(r.net || 0) >= 0 ? 'up' : 'down'}">${yi(r.net)}</span></div>`;
    }).join('');
    return head + body;
  }

  function secMoney(d) {
    const m = d.money || {};
    const body = `<div class="rv-money">
        <div class="rv-money-col"><div class="rv-col-title up">个股净流入 TOP5</div>${rankTable(m.stockIn, 'stock')}</div>
        <div class="rv-money-col"><div class="rv-col-title down">个股净流出 TOP5</div>${rankTable(m.stockOut, 'stock')}</div>
        <div class="rv-money-col"><div class="rv-col-title up">板块净流入 TOP5</div>${rankTable(m.sectorIn, 'sector')}</div>
        <div class="rv-money-col"><div class="rv-col-title down">板块净流出 TOP5</div>${rankTable(m.sectorOut, 'sector')}</div>
      </div>
      <p class="rv-caliber">口径：${esc(m.caliber || '龙虎榜净额')}；当日龙虎榜 ${esc(m.listCount ?? 0)} 只。</p>`;
    return section('2.5', '资金流证据', '单位：亿元', body, 'rv-wide');
  }

  /* ------------------------------------------------------------------ 4 主线轮动 */
  function rotCard(t, kind) {
    if (!t) return `<div class="rv-rot-card empty"><div class="rv-rot-head"><span class="rv-rot-kind">${esc(kind)}</span><span class="rv-rot-name">—</span></div><div class="rv-empty">无</div></div>`;
    const chips = (t.members || []).map((m) => `<span class="rv-chip" data-code="${esc(m.code || '')}">${esc(m.name)}<i>${esc(m.board)}板</i></span>`).join('');
    return `<div class="rv-rot-card">
      <div class="rv-rot-head">
        <span class="rv-rot-kind">${esc(kind)}</span>
        <span class="rv-rot-name">${esc(t.name)}</span>
        <span class="rv-rot-meta">${esc(t.count)} 只涨停 · 最高 ${esc(t.boards)} 板</span>
      </div>
      <div class="rv-chips">${chips}</div>
      <p class="rv-verdict-sm">${esc(t.verdict)}</p>
    </div>`;
  }

  function secRotation(d) {
    const r = d.rotation || {};
    const failed = (r.failed || []).map((f) => `
      <div class="rv-failed-item">
        <span class="nm">${esc(f.name)}</span>
        <span class="${cls(f.changePct)}">${pct(f.changePct)}</span>
        <span class="note">${esc(f.note || '')}</span>
      </div>`).join('') || '<div class="rv-empty">无</div>';
    const body = `<div class="rv-rot">
        ${rotCard(r.main, '主线')}
        ${(r.subs || []).map((t) => rotCard(t, '次主线')).join('')}
        ${(r.alive || []).map((t) => rotCard(t, '活口')).join('')}
      </div>
      <div class="rv-failed">
        <div class="rv-col-title down">失败反馈方向</div>
        ${failed}
      </div>`;
    return section('4', '主线 / 次主线 / 活口 / 失败轮动', `题材 ${esc(r.themeCount ?? 0)} 个`, body, 'rv-wide');
  }

  /* ------------------------------------------------------------------ 4.5 高度单元 */
  function secHeight(d) {
    const h = d.height;
    if (!h) return section('4.5', '连板高度单元', '市场最高高度股', '<div class="rv-empty">今日无连板股</div>');
    const body = `<div class="rv-height">
      <div class="rv-height-main">
        <div class="rv-height-name">${esc(h.name)}<small>${esc(h.code)}</small></div>
        <div class="rv-height-board"><b>${esc(h.board)}</b> 连板</div>
        <div class="rv-height-pct ${cls(h.changePct)}">${pct(h.changePct)}</div>
      </div>
      <div class="rv-height-facts">
        ${kv('封单额', `${n2(h.seal, 2)} 亿`)}
        ${kv('最大封单', `${n2(h.maxSeal, 2)} 亿`)}
        ${kv('首封时间', esc(h.time || '—'))}
        ${kv('所属行业', esc(h.industry || '—'))}
      </div>
      <p class="rv-height-reason">${esc(h.reason || '')}</p>
    </div>`;
    return section('4.5', '连板高度单元', '市场最高高度股', body);
  }

  /* ------------------------------------------------------------------ 6 四分层核心角色 */
  function secLayers(d) {
    const l = d.layers || {};
    const rows = (l.rows || []).map((r) => `
      <div class="rv-tb-row rv-layer-row" data-code="${esc(r.code || '')}">
        <span class="tag">${esc(r.tag)}</span>
        <span class="nm">${esc(r.name)}<small>${esc(r.code || '')}</small></span>
        <span>${esc(r.status)}</span>
        <span>${esc(r.board)} 板</span>
        <span>${n2(r.seal, 2)} 亿</span>
        <span>${esc(r.time || '—')}</span>
      </div>`).join('');
    const body = rows
      ? `<div class="rv-tb-head rv-layer-head"><span>身份</span><span>股票</span><span>状态</span><span>连板</span><span>封单</span><span>时间</span></div>${rows}`
      : '<div class="rv-empty">暂无分层数据</div>';
    return section('6', '四分层核心角色', l.direction ? `方向：${l.direction}（部分展示）` : '部分展示', body);
  }

  /* ------------------------------------------------------------------ 10 次日观察与证伪 */
  function secNextday(d) {
    const n = d.nextday || {};
    const body = `<div class="rv-next">
      <div class="rv-next-col">
        <div class="rv-col-title">次日三大观察</div>
        <ol class="rv-list">${(n.watch || []).map((x) => `<li>${esc(x)}</li>`).join('') || '<li>无</li>'}</ol>
      </div>
      <div class="rv-next-col">
        <div class="rv-col-title down">证伪条件（重点预警）</div>
        <ol class="rv-list warn">${(n.falsify || []).map((x) => `<li>${esc(x)}</li>`).join('') || '<li>无</li>'}</ol>
      </div>
    </div>`;
    return section('10', '次日观察与证伪', '计划与反证', body, 'rv-wide');
  }

  /* ------------------------------------------------------------------ 12 股票池更新 */
  function poolCol(title, rows, kind) {
    const list = (rows || []).map((r) => `
      <div class="rv-pool-item" data-code="${esc(r.code || '')}">
        <span class="nm">${esc(r.name)}</span>
        <span class="meta">${r.board ? esc(r.board) + ' 板' : ''}${r.reason ? ' · ' + esc(r.reason) : ''}</span>
        <span class="${cls(r.changePct)}">${pct(r.changePct)}</span>
      </div>`).join('') || '<div class="rv-empty">无</div>';
    return `<div class="rv-pool-col ${kind}"><div class="rv-col-title ${kind}">${esc(title)}</div>${list}</div>`;
  }

  function secPool(d) {
    const p = d.pool || {};
    const body = `<div class="rv-pool">
      ${poolCol('新补入 / 上修', p.added, 'up')}
      ${poolCol('保留观察', p.keep, 'mid')}
      ${poolCol('降级 / 风险', p.risk, 'down')}
    </div>`;
    return section('12', '股票池更新', '按当日结构自动归类', body, 'rv-wide');
  }

  /* ------------------------------------------------------------------ 13 风险与边界 */
  function secRisk(d) {
    const r = d.risk || {};
    const body = `<div class="rv-risk">
      <div class="rv-risk-level lv-${esc(r.level || '中')}">
        <span class="lb">风险等级</span><span class="vl">${esc(r.level || '—')}</span>
        <span class="sc">情绪 ${n2(r.score, 1)}</span>
      </div>
      <p class="rv-risk-text">${esc(r.text || '')}</p>
    </div>`;
    return section('13', '市场风险与参与边界', '', body, 'rv-wide');
  }

  /* ------------------------------------------------------------------ 连板梯队（附加） */
  function secLadder(d) {
    const tiers = ((d.ladder || {}).tiers) || [];
    const max = Math.max(1, ...tiers.map((t) => t.count || 0));
    const body = `<div class="rv-tiers">${tiers.map((t) => `
      <div class="rv-tier"><span class="tl">${esc(t.label)}</span>
        <span class="tk"><i style="width:${Math.max(2, (t.count || 0) / max * 100)}%"></i></span>
        <span class="tc">${esc(t.count || 0)}</span></div>`).join('')}</div>
      <div class="rv-legend">涨停 ${esc((d.env || {}).limitUp ?? '—')} · 炸板 ${esc((d.env || {}).breakCount ?? '—')} · 跌停 ${esc((d.env || {}).limitDown ?? '—')}</div>`;
    return section('4.6', '连板梯队', '', body);
  }

  /* ------------------------------------------------------------------ 渲染 */
  function render(d) {
    state.data = d;
    renderTop(d);
    el('rvFlow').innerHTML = [
      secOneLine(d),
      secEnv(d),
      secMoney(d),
      secRotation(d),
      secHeight(d),
      secLadder(d),
      secLayers(d),
      secNextday(d),
      secPool(d),
      secRisk(d),
    ].join('');
    el('rvFlow').querySelectorAll('[data-code]').forEach((n) => {
      const code = n.getAttribute('data-code');
      if (!code) return;
      n.classList.add('clickable');
      n.addEventListener('click', () => { location.href = '/?q=' + encodeURIComponent(code); });
    });

    const mainName = ((d.rotation || {}).main || {}).name;
    if (!mainName && state.retry < 8) {
      state.retry += 1;
      el('statusText').textContent = '板块索引构建中…';
      setTimeout(() => { if (!document.hidden) loadReview(currentDate(), true); }, 15000);
    }
  }

  function showError(msg) {
    el('rvFlow').innerHTML = `<div class="rv-sec rv-wide"><div class="rv-warn">复盘加载失败：${esc(msg)}</div>
      <div style="margin-top:12px"><button class="btn-ghost" id="rvRetry" type="button">重试</button></div></div>`;
    const b = el('rvRetry');
    if (b) b.addEventListener('click', () => loadReview(currentDate(), true));
    el('statusText').textContent = '复盘加载失败';
  }

  function currentDate() {
    const sel = el('rvDateSelect');
    return sel && sel.value && sel.value !== 'latest' ? sel.value : '';
  }

  async function loadReview(date, force) {
    if (state.loading) return;
    state.loading = true;
    if (force) el('rvFlow').innerHTML = '<div class="rv-skeleton">正在刷新…</div>';
    try {
      const q = [];
      if (date) q.push('date=' + encodeURIComponent(date));
      if (force) q.push('force=1');
      const res = await fetch('/api/review' + (q.length ? '?' + q.join('&') : ''));
      const d = await res.json();
      if (!d.ok) throw new Error(d.error || '复盘数据加载失败');
      render(d);
    } catch (err) {
      showError(err.message || '未知错误');
    } finally {
      state.loading = false;
    }
  }

  async function loadDates() {
    try {
      const res = await fetch('/api/review/dates');
      const d = await res.json();
      const dates = (d.dates || []).slice().reverse();
      const sel = el('rvDateSelect');
      sel.innerHTML = '<option value="latest">最新</option>' +
        dates.map((x) => `<option value="${esc(x)}">${esc(x)}</option>`).join('');
      sel.addEventListener('change', () => { state.retry = 0; loadReview(currentDate(), true); });
    } catch (err) { /* 忽略 */ }
  }

  /* ------------------------------------------------------------------ 搜索 */
  function bindSearch() {
    const input = el('searchInput');
    const box = el('suggest');
    const btn = el('searchBtn');
    let items = [];
    const close = () => { box.hidden = true; items = []; };
    const submit = (q) => {
      const v = (q || input.value || '').trim();
      if (v) location.href = '/?q=' + encodeURIComponent(v);
    };
    let timer;
    input.addEventListener('input', () => {
      clearTimeout(timer);
      const q = input.value.trim();
      if (!q) { close(); return; }
      timer = setTimeout(async () => {
        try {
          const res = await fetch('/api/search?q=' + encodeURIComponent(q));
          const d = await res.json();
          items = d.items || [];
          if (!items.length) { close(); return; }
          box.innerHTML = items.map((it, i) => `<div class="suggest-item" data-i="${i}">
            <span>${esc(it.name)}</span><span class="cd">${esc(it.ticker)}</span></div>`).join('');
          box.hidden = false;
          box.querySelectorAll('.suggest-item').forEach((n) => {
            n.addEventListener('click', () => submit(items[+n.getAttribute('data-i')].ticker));
          });
        } catch (err) { close(); }
      }, 180);
    });
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') { submit(); close(); }
      if (e.key === 'Escape') close();
    });
    btn.addEventListener('click', () => submit());
    document.addEventListener('click', (e) => { if (!el('searchBox').contains(e.target)) close(); });
  }


  /* ------------------------------------------------------------------ 历史命中回顾 */
  const HITS_DAYS = 30;
  const fpct = (v, d = 2) => (isNum(v) ? `${v > 0 ? '+' : ''}${v.toFixed(d)}%` : '—');

  function statRow(label, s, opts) {
    const o = opts || {};
    if (!s) {
      return `<span class="nm">${esc(label)}</span><span>—</span><span>—</span>
        <span>—</span><span>—</span><span>—</span><span>—</span>`;
    }
    // 最大回撤天然 <= 0：胜率恒为 0、最好恒为 0，展示出来只会误导
    return `<span class="nm">${esc(label)}</span>
      <span>${s.n}</span>
      <span class="${cls(s.mean)}">${fpct(s.mean)}</span>
      <span class="${cls(s.median)}">${fpct(s.median)}</span>
      <span class="${o.noWin ? '' : (s.win >= 50 ? 'up' : 'down')}">${o.noWin ? '—' : `${s.win}%`}</span>
      <span class="down">${fpct(s.worst)}</span>
      <span class="${o.noWin ? '' : 'up'}">${o.noWin ? '—' : fpct(s.best)}</span>`;
  }

  function hitRow(r) {
    const status = r.status === 'done' ? '已验证' : (r.status === 'pending' ? '待验证' : '无日线');
    const zone = r.zone === 'deep' ? '深水' : '主栏';
    // 日志里的开盘涨幅来自 09:25 快照，可能还停在前一日；与真实开盘价差得多就标出来
    const warn = r.suspect
      ? ` title="日志记的开盘涨幅 ${fpct(r.open_pct)}，当日真实开盘 ${fpct(r.gap_real)}；收益按真实开盘价计算"`
      : '';
    const mark = r.suspect ? '<b class="sus">⚠</b>' : '';
    return `<span>${esc(String(r.date || '').slice(5))}</span>
      <span class="nm" data-code="${esc(r.thscode)}"${warn}>${mark}${esc(r.name || r.thscode)}<small>${esc(zone)}</small></span>
      <span>${fpct(r.open_pct, 1)}</span>
      <span>${n2(r.buy)}</span>
      <span class="${cls(r.r0)}">${fpct(r.r0)}</span>
      <span class="${cls(r.o1)}">${fpct(r.o1)}</span>
      <span class="${cls(r.r1)}">${fpct(r.r1)}</span>
      <span class="${cls(r.r2)}">${fpct(r.r2)}</span>
      <span class="${cls(r.r3)}">${fpct(r.r3)}</span>
      <span class="st">${status}</span>`;
  }

  function renderHits(d) {
    const box = el('rvHitsBody');
    const hint = el('rvHitsHint');
    if (!box) return;
    if (!d || !d.ok) {
      box.innerHTML = `<div class="rv-empty">历史命中加载失败：${esc((d && d.error) || '未知错误')}</div>`;
      return;
    }
    const rows = d.rows || [];
    const dirs = ((d.meta || {}).dirs || []).map(esc).join(' · ') || '—';
    if (!rows.length) {
      if (hint) hint.textContent = '暂无命中日志';
      box.innerHTML = `<div class="rv-empty">${esc(d.note || '还没有命中日志')}</div>
        <p class="rv-caliber">已查找目录：${dirs}</p>`;
      return;
    }

    const cov = d.coverage || {};
    const s = d.stats || {};
    const r1 = s.r1;
    if (hint) hint.textContent = `近 ${d.days} 天 · 命中 ${rows.length} 次`;
    const chips = [
      `<span class="rv-hits-chip">命中<b>${rows.length}</b><i>次</i></span>`,
      r1 ? `<span class="rv-hits-chip">T+1 胜率<b>${r1.win}%</b><i>(n=${r1.n})</i></span>` : '',
      r1 ? `<span class="rv-hits-chip">T+1 均值<b class="${cls(r1.mean)}">${fpct(r1.mean)}</b></span>` : '',
      `<span class="rv-hits-chip">已验证<b>${cov.done || 0}</b>`,
      cov.pending ? `<i>待验证 ${cov.pending}</i></span>` : '</span>',
      cov.missing ? `<span class="rv-hits-chip">无日线<b>${cov.missing}</b></span>` : '',
      cov.suspect ? `<span class="rv-hits-chip warn">疑似假命中<b>${cov.suspect}</b><i>开盘价口径</i></span>` : '',
    ].join('');

    const statHead = `<span class="hd">指标</span><span class="hd">n</span><span class="hd">均值</span>
      <span class="hd">中位</span><span class="hd">胜率</span><span class="hd">最差</span><span class="hd">最好</span>`;
    const statBody = [
      statRow('T 日 开盘→收盘 r0', s.r0),
      statRow('T 日 最大回撤 dd', s.dd, { noWin: true }),
      statRow('T+1 开盘 o1', s.o1),
      ...[1, 2, 3, 4, 5].filter((k) => d.horizon >= k).map((k) => statRow(`T+${k} 收盘 r${k}`, s['r' + k])),
    ].join('');

    const hitHead = `<span class="hd">T 日</span><span class="hd">名称</span><span class="hd">开盘涨</span>
      <span class="hd">买入价</span><span class="hd">r0</span><span class="hd">T+1开</span>
      <span class="hd">r1</span><span class="hd">r2</span><span class="hd">r3</span><span class="hd">状态</span>`;
    const hitBody = rows.slice(0, 60).map(hitRow).join('');

    const groups = (d.groups || []).filter((g) => g.stats && g.stats.r1);
    const groupLine = groups.map((g) =>
      `<span class="rv-hits-chip">${esc(g.label)}<b>n=${g.n}</b><i>T+1 ${fpct(g.stats.r1.mean)} · 胜率 ${g.stats.r1.win}%</i></span>`
    ).join('');

    box.innerHTML = `<div class="rv-hits-sum">${chips}${groupLine}</div>
      <div class="rv-hit-scroll"><div class="rv-stat-tb">${statHead}${statBody}</div></div>
      <div class="rv-hit-scroll"><div class="rv-hit-tb">${hitHead}${hitBody}</div></div>
      <p class="rv-caliber">口径与离线 backtest.py 一致：买入价 = T 日开盘（09:25 集合竞价），
        价格取前复权日线；r{k} = T+k 收盘 / 买入价 − 1。样本 ${cov.total} 笔
        （已验证 ${cov.done} · 待验证 ${cov.pending} · 无日线 ${cov.missing}），
        ${rows.length < 5 ? '样本不足 5 笔，胜率仅供参考。' : '仅统计已发生的交易日。'}
        ${cov.suspect ? `其中 ${cov.suspect} 笔标了 ⚠：日志里的开盘涨幅（09:25 快照）与当日真实开盘价不一致，
          收益一律按真实开盘价计算。` : ''}</p>`;
  }

  async function loadHits() {
    const box = el('rvHitsBody');
    if (!box) return;
    try {
      const res = await fetch('/api/hits?days=' + HITS_DAYS);
      const d = await res.json();
      renderHits(d);
      box.querySelectorAll('[data-code]').forEach((n) => {
        const code = n.getAttribute('data-code');
        if (!code) return;
        n.classList.add('clickable');
        n.addEventListener('click', () => { location.href = '/?q=' + encodeURIComponent(code); });
      });
    } catch (err) {
      box.innerHTML = `<div class="rv-empty">历史命中加载失败：${esc(err.message || '网络错误')}</div>`;
    }
  }

  function init() {
    bindSearch();
    loadHits();
    el('rvRefresh').addEventListener('click', () => { state.retry = 0; loadReview(currentDate(), true); });
    loadDates();
    loadReview('', false);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
