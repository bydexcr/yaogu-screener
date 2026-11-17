# -*- coding: utf-8 -*-
"""stock_analysis.build_trend：首屏 K 线取多少根、字段是否够画图。"""
from web import stock_analysis as SA


def _hist(n: int):
    bars = []
    for i in range(n):
        close = 10.0 + i * 0.1
        bars.append({
            "date": "2025-01-%02d" % (i % 28 + 1) if i < 28 else "2025-02-%02d" % (i - 27),
            "open": close - 0.05, "high": close + 0.2, "low": close - 0.2,
            "close": close, "volume": 1000.0 + i, "turnover": 1e7,
        })
    return bars


def test_build_trend_keeps_60_candles_for_hero_chart():
    """首屏 K 线与技术面共用 candles：必须是最近 60 根，且带画蜡烛所需的 OHLCV。"""
    hist = _hist(120)
    t = SA.build_trend(hist, {"lastPrice": hist[-1]["close"]})

    assert len(t["candles"]) == 60
    assert [c["date"] for c in t["candles"]] == [b["date"] for b in hist[-60:]]
    for c in t["candles"][:3] + t["candles"][-3:]:
        for k in ("date", "open", "high", "low", "close", "volume"):
            assert k in c and c[k] is not None


def test_build_trend_candles_short_history_is_not_padded():
    """历史不足 60 根时按实际条数返回，不能拿 None 补齐（画图端按长度判断）。"""
    hist = _hist(20)
    t = SA.build_trend(hist, {"lastPrice": hist[-1]["close"]})
    assert len(t["candles"]) == 20
    assert all(c["close"] is not None for c in t["candles"])
