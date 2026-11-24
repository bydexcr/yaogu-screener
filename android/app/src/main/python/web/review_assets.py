# -*- coding: utf-8 -*-
"""由 web/build_review_assets.py 生成：APK 内嵌的复盘页资源（勿手改）"""

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light" id="metaColorScheme">
<meta name="theme-color" content="#f7f5f1" id="metaThemeColor">
<title>大A小散 · 复盘</title>
<link rel="stylesheet" href="/stock.css">
<link rel="stylesheet" href="/review.css">
<link rel="stylesheet" href="/stock-dark.css" data-theme-dark media="not all">
<link rel="stylesheet" href="/nav.css">
<link rel="stylesheet" href="/pages-dark.css" data-theme-dark media="not all">
</head>
<body class="rv">
<aside class="side" id="appSide"></aside>


<main id="main">
  <section id="reviewView">

    <div class="rv-head">
      <div>
        <h1>复盘</h1>
        <p class="rv-sub"><span class="dot" id="statusBadge"></span><span id="statusText">复盘加载中</span></p>
      </div>
      <div class="rv-head-r">
        <div class="search-box" id="searchBox">
      <svg class="search-icon" viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><circle cx="11" cy="11" r="6.6" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M16.2 16.2L21 21" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
      <input id="searchInput" type="search" autocomplete="off" spellcheck="false" enterkeyhint="search"
             placeholder="名称或代码" aria-label="股票搜索">
      <button id="searchBtn" class="btn-primary" type="button">分析</button>
      <div class="suggest" id="suggest" hidden></div>
    </div>
        <select id="rvDateSelect" class="rv-select" aria-label="选择复盘日期"></select>
        <button id="rvRefresh" class="btn-ghost" type="button">刷新</button>
      </div>
    </div>

    <div class="rv-topbar card">
      <div class="rv-topbar-main">
        <span class="rv-sys" id="rvSys">AI 复盘系统</span>
        <h2 class="rv-title" id="rvTitle">— 正式收复盘</h2>
        <div class="rv-tags">
          <span class="rv-tag" id="rvRegime">—</span>
          <span class="rv-tag heat" id="rvHeat">—</span>
          <span class="rv-tag" id="rvRisk">风险 —</span>
          <span class="rv-tag ghost" id="rvArchived" hidden>历史存档</span>
        </div>
      </div>
    </div>

    <div class="rv-flow" id="rvFlow">
      <div class="rv-skeleton">正在生成复盘…</div>
    </div>

    <section class="rv-sec rv-hits" id="rvHits">
      <header class="rv-sec-head">
        <span class="rv-no">★</span>
        <h3 class="rv-sec-title">历史命中回顾</h3>
        <span class="rv-sec-hint" id="rvHitsHint">这套低吸策略最近准不准</span>
      </header>
      <div class="rv-sec-body" id="rvHitsBody"><div class="rv-skeleton">加载中…</div></div>
    </section>

    <p class="rv-foot" id="rvFoot"></p>
  </section>
</main>

<script src="/review.js"></script>

<div class="settings-mask" id="settingsMask" hidden>
  <div class="settings-sheet" role="dialog" aria-modal="true" aria-label="设置">
    <h3>设置</h3>
    <p class="sub">偏好保存在本机浏览器，四个页面共用。</p>
    <div class="settings-row">
      <div>
        <div class="lbl">界面主题</div>
        <div class="hint">深色适合盯盘，浅色适合白天</div>
      </div>
      <div class="seg" id="themeSeg">
        <button type="button" data-theme="light"><svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.1 5.1l1.4 1.4M17.5 17.5l1.4 1.4M18.9 5.1l-1.4 1.4M6.5 17.5l-1.4 1.4"/></svg>浅色</button>
        <button type="button" data-theme="dark"><svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20.5 13.4A8.2 8.2 0 1 1 10.6 3.5a6.6 6.6 0 0 0 9.9 9.9z"/></svg>深色</button>
      </div>
    </div>
    <div class="settings-row" id="apiRow" hidden>
      <div>
        <div class="lbl">数据接口与阈值</div>
        <div class="hint">同花顺 API Key · 轮询间隔 · 低开区间</div>
      </div>
      <button class="btn-ghost" id="apiOpen" type="button">打开</button>
    </div>
    <div class="settings-foot"><button class="btn-ghost" id="settingsClose" type="button">关闭</button></div>
  </div>
</div>

<script src="/theme.js"></script>
<script src="/nav.js"></script>
</body>
</html>
"""

CSS = r"""/* ============================================================
   复盘页（/review）—— 结构对齐复盘设计稿：
   1 一句话总收口 / 2 盘型环境 / 2.5 资金流证据 / 4 主线轮动 /
   4.5 连板高度 / 4.6 连板梯队 / 6 四分层 / 10 次日观察与证伪 /
   12 股票池更新 / 13 风险边界
   ============================================================ */

/* ---------------- 顶部条 ---------------- */
.rv-topbar {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 12px;
  padding: 14px 16px;
  margin-bottom: 12px;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: var(--panel);
}
.rv-topbar-main { min-width: 0; }
.rv-sys {
  /* 低调化：不做"系统徽章"，只做灰色小标签 */
  font-size: 10.5px; letter-spacing: 1.2px; color: var(--text-mute);
  border: 0; background: none; padding: 0;
}
.rv-title { font-size: 19px; margin: 8px 0 0; letter-spacing: .4px; }
.rv-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.rv-tag {
  font-size: 11.5px; color: var(--text-dim); background: var(--panel-2);
  border: 1px solid var(--line); border-radius: 999px; padding: 3px 10px;
}
.rv-tag.ghost { color: var(--text-mute); background: transparent; }
.rv-tag.heat.hot { color: #fff; background: var(--up); border-color: transparent; }
.rv-tag.heat.warm { color: #fff; background: var(--warn); border-color: transparent; }
.rv-tag.heat.mid { color: var(--text); }
.rv-tag.heat.cool { color: #ffffff; background: var(--down); border-color: transparent; }
.rv-tag.heat.cold { color: #ffffff; background: #0a6b5f; border-color: transparent; }
.rv-topbar-actions { display: flex; align-items: center; gap: 8px; flex: none; }
.rv-select {
  appearance: none; color: var(--text); background: var(--panel-2);
  border: 1px solid var(--line); border-radius: 999px;
  font-size: 12.5px; padding: 7px 26px 7px 12px; max-width: 140px;
  background-image: linear-gradient(45deg, transparent 50%, var(--text-mute) 50%), linear-gradient(135deg, var(--text-mute) 50%, transparent 50%);
  background-position: calc(100% - 14px) 52%, calc(100% - 9px) 52%;
  background-size: 5px 5px, 5px 5px; background-repeat: no-repeat;
}
.rv-topbar-actions .btn-ghost { padding: 7px 14px; font-size: 12.5px; }

/* ---------------- 区块骨架 ---------------- */
.rv-flow { display: grid; grid-template-columns: minmax(0, 1fr); gap: 12px; }
.rv-sec {
  /* 分区带：透明底 + 顶部发丝线 */
  background: transparent;
  border: 0;
  border-top: 1px solid var(--line);
  border-radius: 0;
  padding: 16px 0 20px;
}
.rv-sec-head { display: flex; align-items: baseline; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }
.rv-no {
  font: 700 11px/1 var(--mono); color: var(--accent-2);
  background: var(--accent-weak); border-radius: 6px; padding: 3px 6px;
}
.rv-sec-title { font-size: 14px; margin: 0; letter-spacing: .3px; }
.rv-sec-hint { font-size: 11px; color: var(--text-mute); }
.rv-skeleton { padding: 40px 8px; text-align: center; color: var(--text-mute); font-size: 13px; }
.rv-empty { padding: 10px 2px; font-size: 12px; color: var(--text-mute); }
.rv-warn {
  padding: 9px 11px; border-radius: 10px; font-size: 12px; line-height: 1.65;
  color: var(--warn); background: rgba(199, 119, 0, .1); border: 1px solid rgba(199, 119, 0, .3);
}
.rv-caliber, .rv-legend { margin: 9px 0 0; font-size: 10.5px; line-height: 1.7; color: var(--text-mute); }
.rv-col-title {
  font-size: 11.5px; color: var(--text-dim); letter-spacing: .4px; margin-bottom: 7px;
  padding-bottom: 5px; border-bottom: 1px solid var(--line-soft);
}
.rv-col-title.up { color: var(--up); }
.rv-col-title.down { color: var(--down); }
.rv-col-title.mid { color: var(--text-dim); }
.clickable { cursor: pointer; }
.clickable:hover { background: var(--panel-3); }

/* ---------------- 1 一句话 ---------------- */
.rv-verdict {
  margin: 0 0 10px; font-size: 14.5px; line-height: 1.75; color: var(--text); font-weight: 600;
  padding: 11px 13px; border-radius: 12px;
  background: var(--panel);
  border: 1px solid var(--line);
}
.rv-points { margin: 0; padding-left: 18px; }
.rv-points li { font-size: 12.5px; line-height: 1.85; color: var(--text-dim); }

/* ---------------- 2 环境 ---------------- */
.rv-env { display: grid; grid-template-columns: minmax(0, 1fr); gap: 14px; }
.rv-regime { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }
.rv-regime-name { font-size: 15px; font-weight: 650; color: var(--accent-2); }
.rv-regime-flavor { font-size: 11.5px; color: var(--text-mute); }
.rv-kvs { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 7px; }
.rv-kv {
  display: flex; align-items: baseline; justify-content: space-between; gap: 8px;
  background: var(--panel-2); border-radius: 9px; padding: 7px 9px;
}
.rv-kv .k { font-size: 11px; color: var(--text-mute); }
.rv-kv .v { font: 650 12.5px/1.2 var(--mono); color: var(--text); }
.rv-kv .v.up { color: var(--up); } .rv-kv .v.down { color: var(--down); }
.rv-idx-head, .rv-idx-row {
  display: grid; grid-template-columns: minmax(0, 1fr) 78px 68px; gap: 8px; align-items: center;
  padding: 6px 8px; font-size: 12px; font-family: var(--mono);
}
.rv-idx-head { color: var(--text-mute); font-size: 10.5px; border-bottom: 1px solid var(--line-soft); font-family: var(--font); }
.rv-idx-row { border-bottom: 1px solid var(--line-soft); }
.rv-idx-row:last-child { border-bottom: none; }
.rv-idx-row .n { font-family: var(--font); color: var(--text-dim); }
.rv-idx-row .p, .rv-idx-row .c { text-align: right; }
.rv-idx-head .p, .rv-idx-head .c { text-align: right; }
.rv-idx-row .up, .rv-idx-row .c.up { color: var(--up); }
.rv-idx-row .down, .rv-idx-row .c.down { color: var(--down); }

/* ---------------- 2.5 资金 ---------------- */
.rv-money { display: grid; grid-template-columns: minmax(0, 1fr); gap: 12px; }
.rv-tb-head, .rv-tb-row {
  display: grid; grid-template-columns: minmax(0, 1fr) 62px 66px; gap: 6px; align-items: center;
  padding: 6px 7px; font-size: 12px;
}
.rv-tb-head { color: var(--text-mute); font-size: 10.5px; border-bottom: 1px solid var(--line-soft); }
.rv-tb-head span:nth-child(2), .rv-tb-head span:nth-child(3) { text-align: right; }
.rv-tb-row { border-bottom: 1px solid var(--line-soft); border-radius: 6px; }
.rv-tb-row:last-child { border-bottom: none; }
.rv-tb-row > span:nth-child(2), .rv-tb-row > span:nth-child(3) { text-align: right; font-family: var(--mono); }
.rv-tb-row .nm { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rv-tb-row .nm small { color: var(--text-mute); font-size: 10.5px; margin-left: 5px; font-family: var(--mono); }
.rv-tb-row .up { color: var(--up); } .rv-tb-row .down { color: var(--down); }

/* ---------------- 4 轮动 ---------------- */
.rv-rot { display: grid; grid-template-columns: minmax(0, 1fr); gap: 10px; }
.rv-rot-card {
  background: var(--panel-2); border: 1px solid var(--line-soft);
  border-radius: 12px; padding: 10px 11px;
}
.rv-rot-card.empty { opacity: .6; }
.rv-rot-head { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
.rv-rot-kind {
  font-size: 10px; color: var(--text-mute); border: 1px solid var(--line);
  border-radius: 5px; padding: 1px 5px;
}
.rv-rot-name { font-size: 13.5px; font-weight: 650; color: var(--text); }
.rv-rot-meta { margin-left: auto; font-size: 10.5px; color: var(--text-mute); font-family: var(--mono); }
.rv-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.rv-chip {
  display: inline-flex; align-items: baseline; gap: 4px;
  font-size: 11.5px; color: var(--text); background: var(--panel-3);
  border-radius: 999px; padding: 3px 9px;
}
.rv-chip i { font-style: normal; font-size: 10px; color: var(--text-mute); }
.rv-verdict-sm { margin: 8px 0 0; font-size: 11.5px; color: var(--accent-2); line-height: 1.6; }
.rv-failed { margin-top: 12px; }
.rv-failed-item {
  display: grid; grid-template-columns: minmax(0, 1fr) 62px; gap: 8px; align-items: center;
  padding: 7px 9px; background: var(--panel-2); border-radius: 9px; margin-bottom: 6px;
}
.rv-failed-item .nm { font-size: 12.5px; }
.rv-failed-item > span:nth-child(2) { text-align: right; font-family: var(--mono); font-size: 12px; }
.rv-failed-item .note { grid-column: 1 / -1; font-size: 10.5px; color: var(--text-mute); }
.rv-failed-item .up { color: var(--up); } .rv-failed-item .down { color: var(--down); }

/* ---------------- 4.5 高度 ---------------- */
.rv-height-main { display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }
.rv-height-name { font-size: 17px; font-weight: 700; }
.rv-height-name small { font-size: 11px; color: var(--text-mute); font-family: var(--mono); margin-left: 6px; }
.rv-height-board { font-size: 12px; color: var(--text-dim); }
.rv-height-board b { font-size: 17px; color: var(--up); font-family: var(--mono); }
.rv-height-pct { font: 650 13px/1 var(--mono); margin-left: auto; }
.rv-height-pct.up { color: var(--up); } .rv-height-pct.down { color: var(--down); }
.rv-height-facts { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 7px; margin-top: 10px; }
.rv-height-reason { margin: 9px 0 0; font-size: 11.5px; color: var(--text-mute); line-height: 1.6; }

/* ---------------- 6 分层 ---------------- */
.rv-layer-head, .rv-layer-row {
  grid-template-columns: 62px minmax(0, 1fr) 46px 46px 62px 52px;
}
.rv-layer-row .tag {
  font-size: 10.5px; color: var(--accent-2); background: var(--accent-weak);
  border-radius: 5px; padding: 2px 5px; text-align: center;
}
.rv-layer-row .nm { font-size: 12.5px; }

/* ---------------- 10 次日 ---------------- */
.rv-next { display: grid; grid-template-columns: minmax(0, 1fr); gap: 12px; }
.rv-list { margin: 0; padding-left: 18px; }
.rv-list li { font-size: 12.5px; line-height: 1.85; color: var(--text-dim); }
.rv-list.warn li { color: #b32434; }

/* ---------------- 12 股票池 ---------------- */
.rv-pool { display: grid; grid-template-columns: minmax(0, 1fr); gap: 12px; }
.rv-pool-item {
  display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 4px 8px;
  padding: 7px 9px; background: var(--panel-2); border-radius: 9px; margin-bottom: 6px;
}
.rv-pool-item .nm { font-size: 12.5px; }
.rv-pool-item .meta { grid-column: 1 / -1; font-size: 10.5px; color: var(--text-mute); }
.rv-pool-item > span:last-child { font-family: var(--mono); font-size: 12px; text-align: right; }
.rv-pool-item .up { color: var(--up); } .rv-pool-item .down { color: var(--down); }

/* ---------------- 13 风险 ---------------- */
.rv-risk { display: flex; align-items: flex-start; gap: 12px; flex-wrap: wrap; }
.rv-risk-level {
  display: inline-flex; align-items: baseline; gap: 8px; flex: none;
  border-radius: 12px; padding: 8px 12px; background: var(--panel-2);
  border: 1px solid var(--line);
}
.rv-risk-level .lb { font-size: 10.5px; color: var(--text-mute); }
.rv-risk-level .vl { font-size: 15px; font-weight: 700; }
.rv-risk-level .sc { font-size: 10.5px; color: var(--text-mute); font-family: var(--mono); }
.rv-risk-level.lv-低, .rv-risk-level.lv-中低 { border-color: rgba(13, 155, 108, .4); color: var(--down); }
.rv-risk-level.lv-中 { border-color: rgba(199, 119, 0, .4); color: var(--warn); }
.rv-risk-level.lv-中高, .rv-risk-level.lv-高 { border-color: rgba(225, 29, 51, .45); color: var(--up); }
.rv-risk-text { flex: 1 1 240px; margin: 0; font-size: 12.5px; line-height: 1.8; color: var(--text-dim); }

/* ---------------- 4.6 梯队 ---------------- */
.rv-tiers { display: grid; gap: 7px; }
.rv-tier { display: grid; grid-template-columns: 74px minmax(0, 1fr) 34px; gap: 8px; align-items: center; }
.rv-tier .tl { font-size: 11.5px; color: var(--text-dim); }
.rv-tier .tk { height: 15px; background: var(--panel-3); border-radius: 4px; overflow: hidden; }
.rv-tier .tk i { display: block; height: 100%; border-radius: 4px; background: var(--up); }
.rv-tier .tc { font-size: 11.5px; color: var(--text-mute); text-align: right; font-family: var(--mono); }

/* ---------- 历史命中回顾 ---------- */
.rv-hits-sum { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
.rv-hits-chip {
  padding: 5px 10px; border: 1px solid var(--line-soft); border-radius: 9px;
  background: var(--panel-2); font-size: 11.5px; color: var(--text-dim);
}
.rv-hits-chip b { font-family: var(--mono); font-size: 12.5px; color: var(--text); margin-left: 3px; }
.rv-hits-chip i { font-style: normal; color: var(--text-mute); margin-left: 4px; font-size: 10.5px; }

.rv-hit-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; margin-bottom: 10px; }
.rv-stat-tb, .rv-hit-tb {
  display: grid; min-width: 560px; font-size: 11.5px;
  border-top: 1px solid var(--line-soft);
}
.rv-stat-tb { grid-template-columns: minmax(140px, 1fr) repeat(6, minmax(56px, auto)); }
.rv-hit-tb { grid-template-columns: 62px minmax(118px, 1fr) repeat(9, minmax(50px, auto)); min-width: 790px; }
    /* 列数 = T日 名称 开盘涨 买入价 r0 止损口径 T+1开 r1 r2 r3 状态 = 11 列 */
.rv-stat-tb > span, .rv-hit-tb > span {
  padding: 7px 8px; text-align: right; border-bottom: 1px solid var(--line-soft);
  font-family: var(--mono); white-space: nowrap; color: var(--text-dim);
}
.rv-stat-tb > span.nm, .rv-hit-tb > span.nm,
.rv-hit-tb > span:first-child { text-align: left; font-family: var(--font); color: var(--text); }
.rv-hit-tb > span.st { font-family: var(--font); color: var(--text-mute); }
.rv-hit-tb > span.nm small { color: var(--text-mute); font-size: 10.5px; margin-left: 5px; font-family: var(--mono); }
.rv-stat-tb > .hd, .rv-hit-tb > .hd {
  color: var(--text-mute); font-size: 10.5px; font-weight: 400; background: var(--panel-2);
}
.rv-stat-tb > .up, .rv-hit-tb > .up { color: var(--up); }
.rv-stat-tb > .down, .rv-hit-tb > .down { color: var(--down); }
.rv-stat-tb > .flat, .rv-hit-tb > .flat { color: var(--text-mute); }
.rv-hit-tb > span.nm .sus { color: var(--warn); margin-right: 3px; font-weight: 700; }
.rv-hits-chip.warn { border-color: rgba(199, 119, 0, .45); color: var(--warn); }
.rv-hits-chip.warn b { color: var(--warn); }
.rv-hit-tb > span[data-code] { cursor: pointer; }
.rv-hit-tb > span[data-code]:hover { color: var(--accent); }

.rv-foot { margin: 14px 2px 0; font-size: 11px; line-height: 1.8; color: var(--text-mute); }

/* ============================================================
   宽屏
   ============================================================ */
@media (min-width: 900px) {
  .rv-flow { gap: 16px; }
  .rv-sec { padding: 16px 18px 18px; }
  .rv-sec-title { font-size: 15px; }
  .rv-topbar { padding: 18px 22px; }
  .rv-title { font-size: 22px; }
  .rv-env { grid-template-columns: minmax(0, 1.05fr) minmax(0, .95fr); gap: 22px; }
  .rv-money { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
  .rv-rot { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .rv-next { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .rv-pool { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .rv-height-facts { grid-template-columns: repeat(4, minmax(0, 1fr)); }
}
@media (min-width: 1400px) {
  .rv-money { grid-template-columns: repeat(4, minmax(0, 1fr)); }
  .rv-rot { grid-template-columns: repeat(4, minmax(0, 1fr)); }
}

/* ============================================================
   复盘页 v2：与市场全景 / 个股分析 / 妖股雷达 同一套卡片体系
   ============================================================ */

body.rv {
  padding-top: 32px;
  padding-right: 32px;
  padding-bottom: 56px;
  background: var(--bg);
}
@media (max-width: 899px) {
  body.rv { padding-top: 14px; padding-right: 12px; padding-bottom: 40px; padding-left: 12px; }
}
body.rv #main { max-width: 1620px; margin: 0 auto; padding: 0; }

/* ---------------- 页内标题行 ---------------- */
.rv-head { display: flex; align-items: flex-start; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
.rv-head h1 { font-size: 30px; font-weight: 700; letter-spacing: -.02em; line-height: 1.1; }
.rv-sub {
  display: flex; align-items: center; gap: 7px; margin-top: 8px;
  font-size: 12.5px; color: var(--text-mute);
}
.rv-sub .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--down); flex: none; }
.rv-head-r { margin-left: auto; display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
body.rv .search-box {
  margin: 0; width: min(320px, 30vw); max-width: none;
  padding: 4px 6px 4px 14px; background: var(--panel);
  border: 1px solid var(--line); border-radius: 999px;
}
body.rv .search-box:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-weak); }
body.rv .search-box input { height: 32px; font-size: 13px; }
body.rv .search-box #searchBtn { border-radius: 999px; padding: 6px 16px; font-size: 12.5px; }
body.rv .search-box .suggest { top: calc(100% + 6px); left: 0; right: 0; }

/* ---------------- 白卡 ---------------- */
body.rv .rv-topbar,
body.rv .rv-sec {
  background: var(--panel);
  border: 0;
  border-top: 0;
  border-radius: 22px;
  padding: 20px 22px;
  margin-bottom: 16px;
  box-shadow: 0 1px 2px rgba(28, 24, 16, .05), 0 12px 28px -18px rgba(28, 24, 16, .20);
}
body.rv .rv-topbar { display: block; }
body.rv .rv-topbar .rv-title { margin-top: 6px; }
body.rv .rv-flow { gap: 16px; }
body.rv .rv-hits { margin-bottom: 0; }

/* 章节标题与其它页对齐 */
body.rv .rv-sec-title { font-size: 15px; font-weight: 700; letter-spacing: -.01em; }
body.rv .rv-no { color: var(--accent-2); font-weight: 700; }
body.rv .rv-sec-head { margin-bottom: 12px; }

@media (max-width: 899px) {
  .rv-head { flex-direction: column; gap: 12px; }
  .rv-head h1 { font-size: 24px; }
  .rv-head-r { margin-left: 0; width: 100%; }
  body.rv .search-box { width: 100%; }
  body.rv .rv-topbar,
  body.rv .rv-sec { padding: 16px; border-radius: 18px; }
}
"""

JS = r"""(function () {
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
      n.addEventListener('click', () => { location.href = '/stock?q=' + encodeURIComponent(code); });
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
      if (v) location.href = '/stock?q=' + encodeURIComponent(v);
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
      <span class="nm" data-code="${esc(r.thscode)}"${warn}>${mark}${esc(r.name || r.thscode)}<small>${esc(zone)}</small><button class="wstar" type="button" data-watch="${esc(r.thscode)}" title="加自选">★</button></span>
      <span>${fpct(r.open_pct, 1)}</span>
      <span>${n2(r.buy)}</span>
      <span class="${cls(r.r0)}">${fpct(r.r0)}</span>
      <span class="${cls(r.r0_stop)}"${r.stopped ? ' title="当日最低触及 -3%，按止损价离场"' : ''}>${fpct(r.r0_stop)}${r.stopped ? '<b class="sus">≈</b>' : ''}</span>
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
    // 口径：T 日开→收 是主指标（离线 walk-forward 显示 T+3 在样本外多为负，只作参考）
    const r0 = s.r0, r0s = s.r0_stop;
    if (hint) hint.textContent = `近 ${d.days} 天 · 命中 ${rows.length} 次`;
    const chips = [
      `<span class="rv-hits-chip">命中<b>${rows.length}</b><i>次</i></span>`,
      r0 ? `<span class="rv-hits-chip">日内胜率<b>${r0.win}%</b><i>(n=${r0.n})</i></span>` : '',
      r0 ? `<span class="rv-hits-chip">日内均值<b class="${cls(r0.mean)}">${fpct(r0.mean)}</b></span>` : '',
      r0s ? `<span class="rv-hits-chip">-3% 止损口径<b class="${cls(r0s.mean)}">${fpct(r0s.mean)}</b><i>胜率 ${r0s.win}%</i></span>` : '',
      `<span class="rv-hits-chip">已验证<b>${cov.done || 0}</b>`,
      cov.pending ? `<i>待验证 ${cov.pending}</i></span>` : '</span>',
      cov.missing ? `<span class="rv-hits-chip">无日线<b>${cov.missing}</b></span>` : '',
      cov.suspect ? `<span class="rv-hits-chip warn">疑似假命中<b>${cov.suspect}</b><i>开盘价口径</i></span>` : '',
    ].join('');

    const statHead = `<span class="hd">指标</span><span class="hd">n</span><span class="hd">均值</span>
      <span class="hd">中位</span><span class="hd">胜率</span><span class="hd">最差</span><span class="hd">最好</span>`;
    const statBody = [
      statRow('T 日 开→收（日内主指标）', s.r0),
      statRow('T 日 -3% 止损口径', s.r0_stop),
      statRow('T 日 最大回撤 dd', s.dd, { noWin: true }),
      statRow('T+1 开盘 o1（次日跳空）', s.o1),
      ...[1, 2, 3, 4, 5].filter((k) => d.horizon >= k)
        .map((k) => statRow(`T+${k} 收盘 r${k}（参考）`, s['r' + k])),
    ].join('');

    const hitHead = `<span class="hd">T 日</span><span class="hd">名称</span><span class="hd">开盘涨</span>
      <span class="hd">买入价</span><span class="hd">r0</span><span class="hd">止损口径</span><span class="hd">T+1开</span>
      <span class="hd">r1</span><span class="hd">r2</span><span class="hd">r3</span><span class="hd">状态</span>`;
    const hitBody = rows.slice(0, 60).map(hitRow).join('');

    const groups = (d.groups || []).filter((g) => g.stats && g.stats.r0);
    const groupLine = groups.map((g) => {
      const a = g.stats.r0, b = g.stats.r0_stop;
      return `<span class="rv-hits-chip">${esc(g.label)}<b>n=${g.n}</b>` +
        `<i>日内 ${fpct(a.mean)} · 胜率 ${a.win}%${b ? ` · 止损口径 ${fpct(b.mean)}` : ''}</i></span>`;
    }).join('');

    box.innerHTML = `<div class="rv-hits-sum">${chips}${groupLine}</div>
      <div class="rv-hit-scroll"><div class="rv-stat-tb">${statHead}${statBody}</div></div>
      <div class="rv-hit-scroll"><div class="rv-hit-tb">${hitHead}${hitBody}</div></div>
      <p class="rv-caliber">口径与离线 backtest.py 一致：买入价 = T 日开盘（09:25 集合竞价），
        价格取前复权日线。<b>主指标是 T 日开→收</b>（r0）与 <b>-3% 止损口径</b>
        （当日最低触及 -3% 即按 -3% 离场，标 ≈）；r{k} = T+k 收盘 / 买入价 − 1 仅作参考
        —— 离线 walk-forward 显示 T+3 在样本外方向不稳定。样本 ${cov.total} 笔
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
        n.addEventListener('click', () => { location.href = '/stock?q=' + encodeURIComponent(code); });
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
"""
