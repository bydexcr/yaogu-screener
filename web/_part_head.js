(function () {
  'use strict';

  const $ = (s) => document.querySelector(s);
  const el = (id) => document.getElementById(id);

  // 后端错误既可能是字符串（Python 版），也可能是 { message }（Node 版），统一取出可读文本
  function errText(payload, fallback) {
    const e = payload && payload.error;
    if (!e) return fallback;
    if (typeof e === 'string') return e;
    return e.message || e.detail || fallback;
  }

  const state = {
    data: null,
    market: null,
    loading: false,
    query: '',
    sectorKind: 'l1',
    sectorSort: 'change',
    sectorOpen: null,
    suggestIndex: -1,
    suggestItems: [],
  };
