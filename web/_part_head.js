(function () {
  'use strict';

  const $ = (s) => document.querySelector(s);
  const el = (id) => document.getElementById(id);

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
