
  /* ------------------------------ 手机端控制层 ------------------------------ */
  const STAGE_HINTS = [
    '解析股票代码',
    '拉取行情与 K 线',
    '读取三大报表',
    '计算多期指标',
    '解析行业与概念',
    '核对龙虎榜与涨跌停',
    '扫描同行业公司',
    '计算评分与风险',
  ];
  let timerId = null;
  let hintId = null;

  function updateUrl(query) {
    const next = `?q=${encodeURIComponent(query)}`;
    try {
      if (location.search !== next) history.pushState({ q: query }, '', next);
    } catch (e) { /* ignore */ }
  }

  function showLoading(query) {
    state.loading = true;
    $("#marketView").hidden = true;
    $("#result").hidden = true;
    $("#errorState").hidden = true;
    $("#backBar").hidden = true;
    $("#loadingState").hidden = false;
    $("#loadingTitle").textContent = `正在分析 ${query}`;
    $("#loadingStage").textContent = STAGE_HINTS[0];
    $("#statusText").textContent = '分析中';
    const t0 = Date.now();
    clearInterval(timerId);
    clearInterval(hintId);
    timerId = setInterval(() => {
      $("#loadingTimer").textContent = `${((Date.now() - t0) / 1000).toFixed(1)}s`;
    }, 100);
    let i = 0;
    hintId = setInterval(() => {
      i = Math.min(STAGE_HINTS.length - 1, i + 1);
      $("#loadingStage").textContent = STAGE_HINTS[i];
    }, 1200);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function showError(message, query) {
    state.loading = false;
    clearInterval(timerId);
    clearInterval(hintId);
    $("#marketView").hidden = true;
    $("#loadingState").hidden = true;
    $("#result").hidden = true;
    $("#errorState").hidden = false;
    $("#backBar").hidden = false;
    $("#errorMsg").textContent = message;
    $("#statusText").textContent = '分析失败';
    $("#errorRetry").onclick = () => runAnalysis(query, true);
  }

  async function runAnalysis(query, _stream, opts = {}) {
    if (!query) return;
    state.loading = true;
    state.query = query;
    showLoading(query);
    if (!opts.fromHistory) updateUrl(query);
    try {
      const res = await fetch(`/api/stock?q=${encodeURIComponent(query)}`);
      const json = await res.json();
      if (!json.ok) throw new Error(json.error || '分析失败');
      if (state.query !== query) return;
      state.data = json;
      state.loading = false;
      clearInterval(timerId);
      clearInterval(hintId);
      render(json);
    } catch (err) {
      if (state.query !== query) return;
      showError(err.message || '分析失败', query);
    }
  }

  /* ------------------------------ 章节折叠 ------------------------------ */
  function sectionsOf() {
    return Array.from(document.querySelectorAll('#result .card'));
  }

  function initCollapse() {
    sectionsOf().forEach((card, i) => {
      const h2 = card.querySelector('h2');
      if (!h2 || h2.dataset.accBound) return;
      h2.dataset.accBound = '1';
      h2.classList.add('acc-head');
      h2.addEventListener('click', () => card.classList.toggle('collapsed'));
      // 手机端：默认只展开前 3 个章节
      card.classList.toggle('collapsed', i > 2);
    });
    const all = el('expandAll');
    if (all) all.textContent = '展开全部';
  }

  function bindExpandAll() {
    const all = el('expandAll');
    if (!all) return;
    all.addEventListener('click', () => {
      const cards = sectionsOf();
      const anyOpen = cards.some((c) => !c.classList.contains('collapsed'));
      cards.forEach((c) => c.classList.toggle('collapsed', anyOpen));
      all.textContent = anyOpen ? '展开全部' : '收起全部';
    });
  }

  /* ------------------------------ 搜索 ------------------------------ */
  function showSuggest(items) {
    const box = $("#suggest");
    state.suggestItems = items;
    state.suggestIndex = -1;
    if (!items.length) { box.hidden = true; return; }
    box.innerHTML = items.map((it, i) => `
      <div class="suggest-item" data-i="${i}">
        <span class="nm">${esc(it.name)}</span>
        <span class="cd">${esc(it.ticker)}</span>
      </div>`).join('');
    box.hidden = false;
    box.querySelectorAll('.suggest-item').forEach((node) => {
      node.addEventListener('mousedown', (e) => {
        e.preventDefault();
        const it = items[Number(node.getAttribute('data-i'))];
        box.hidden = true;
        $("#searchInput").value = it.ticker;
        $("#searchInput").blur();
        runAnalysis(it.ticker, true);
      });
    });
  }

  let suggestTimer = null;
  let suggestSeq = 0;
  async function fetchSuggest(q) {
    const seq = ++suggestSeq;
    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
      const json = await res.json();
      if (seq !== suggestSeq) return;
      showSuggest(json.items || []);
    } catch (e) { /* ignore */ }
  }

  function bindSearch() {
    const input = $("#searchInput");
    input.addEventListener('input', () => {
      const v = input.value.trim();
      clearTimeout(suggestTimer);
      if (!v) { $("#suggest").hidden = true; return; }
      suggestTimer = setTimeout(() => fetchSuggest(v), 260);
    });
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const v = input.value.trim();
        if (v) {
          $("#suggest").hidden = true;
          input.blur();
          runAnalysis(v, true);
        }
      } else if (e.key === 'Escape') {
        $("#suggest").hidden = true;
      }
    });
    input.addEventListener('blur', () => setTimeout(() => { $("#suggest").hidden = true; }, 150));
    $("#searchBtn").addEventListener('click', () => {
      const v = input.value.trim();
      if (v) {
        $("#suggest").hidden = true;
        $("#searchInput").blur();
        runAnalysis(v, true);
      }
    });
  }

  /* ------------------------------ 状态条 ------------------------------ */
  function refreshStatus() {
    const m = state.market;
    if (!m) return;
    if (state.loading) return;
    const mem = m.membership || {};
    const parts = [];
    if (m.tradeDate) parts.push(`交易日 ${m.tradeDate}`);
    if (mem.status === 'running' && mem.progress) parts.push(`板块索引 ${mem.progress.done}/${mem.progress.total}`);
    else if (mem.status === 'ready' && mem.date) parts.push(`板块索引 ${mem.date}`);
    if (state.data && state.data.resolved) parts.push(`已分析 ${state.data.resolved.name}`);
    const text = parts.join(' · ');
    if (text && $("#statusText")) $("#statusText").textContent = text;
  }

  /* ------------------------------ 启动 ------------------------------ */
  function init() {
    bindSearch();
    bindExpandAll();
    $("#backBtn").addEventListener('click', showMarket);
    window.addEventListener('popstate', (ev) => {
      const q = (ev.state && ev.state.q) || new URLSearchParams(location.search).get('q');
      if (q) {
        $("#searchInput").value = q;
        state.loading = false;
        runAnalysis(q, true, { fromHistory: true });
      } else {
        state.loading = false;
        showMarket();
      }
    });
    const q = new URLSearchParams(location.search).get('q');
    if (q) {
      $("#searchInput").value = q;
      runAnalysis(q, true, { fromHistory: true });
    } else {
      loadMarket();
    }
    setInterval(refreshStatus, 2000);
    setInterval(() => {
      if (!document.hidden && !$("#marketView").hidden && !state.loading) loadMarket();
    }, 60 * 1000);
  }

  document.addEventListener('DOMContentLoaded', init);
})();
