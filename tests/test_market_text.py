# -*- coding: utf-8 -*-
"""web/market_text.py —— 市场全景页的派生文案（纯函数）。"""
from web import market_text as MT

BREADTH = {
    "total": 5583, "up": 1326, "down": 4119, "flat": 138, "upRatio": 23.8, "avg": -1.49,
    "turnover": 1467532914063.2,
    "buckets": [
        {"label": "≤-9.8%", "count": 110}, {"label": "-9.8~-7%", "count": 149},
        {"label": "-7~-3%", "count": 1046}, {"label": "-3~0%", "count": 2814},
        {"label": "0~3%", "count": 1218}, {"label": "3~7%", "count": 165},
        {"label": "7~9.8%", "count": 20}, {"label": "≥9.8%", "count": 51},
    ],
}
LIMITS = {"limitUpCount": 36, "limitDownCount": 77, "breakCount": 20,
          "sealRate": 64.3, "highestBoard": 3}
SECTORS = {"boards": {"l1": [
    {"name": "贵金属", "changePct": 1.63, "memberCount": 14, "upCount": 13, "downCount": 1},
    {"name": "小家电", "changePct": 1.34, "memberCount": 26, "upCount": 14, "downCount": 11},
    {"name": "电子化学品", "changePct": 1.07, "memberCount": 44, "upCount": 27, "downCount": 17},
    {"name": "半导体", "changePct": 0.23, "memberCount": 190, "upCount": 96, "downCount": 92},
]}}
MARKET = {"breadth": BREADTH, "limits": LIMITS, "sectors": SECTORS}


# ---------------------------------------------------------------- 情绪标签
def test_mood_three_tiers():
    assert MT.mood(23.8) == "情绪偏冷"
    assert MT.mood(40) == "情绪温和"
    assert MT.mood(72) == "情绪偏热"
    assert MT.mood(None) == "—"


# ---------------------------------------------------------------- 涨跌分布结论
def test_distribution_picks_dominant_bucket_and_tails():
    s = MT.distribution(BREADTH)
    assert "2814 只落在 -3~0%" in s
    assert "50.4%" in s                      # 2814/5583
    assert "跌超 7% 的 259 只" in s          # 110+149
    assert "涨超 7% 的 71 只" in s           # 20+51


def test_distribution_empty_safe():
    assert MT.distribution({}) == ""
    assert MT.distribution({"total": 0, "buckets": []}) == ""


# ---------------------------------------------------------------- 结构句
def test_structure_uses_highest_up_ratio_board():
    s = MT.structure(SECTORS)
    assert "贵金属" in s and "相对占优" in s
    assert "93%" in s                        # 13/14


def test_structure_reports_all_up_boards_when_present():
    sectors = {"boards": {"l1": [
        {"name": "银行", "memberCount": 42, "upCount": 42},
        {"name": "保险", "memberCount": 5, "upCount": 5},
        {"name": "煤炭", "memberCount": 30, "upCount": 10},
    ]}}
    s = MT.structure(sectors)
    assert "全部上涨" in s and "银行 42 只" in s and "保险 5 只" in s


def test_structure_ignores_tiny_samples():
    """成分不足 5 只的小板块不该代表全市场结构。"""
    sectors = {"boards": {"l1": [{"name": "袖珍", "memberCount": 2, "upCount": 2},
                                 {"name": "大板块", "memberCount": 40, "upCount": 20}]}}
    s = MT.structure(sectors)
    assert "袖珍" not in s and "大板块" in s


# ---------------------------------------------------------------- 今日一句
def test_one_sentence_down_day_is_honest():
    s = MT.one_sentence(MARKET)
    assert "避险" in s and "普跌" in s
    assert "74%" in s                        # 4119/5583
    assert "1.47 万亿" in s
    assert "涨停 36 只对跌停 77 只" in s and "64.3%" in s
    # 不许出现没有基准支撑的定性
    for banned in ("缩量", "放量", "主力"):
        assert banned not in s


def test_one_sentence_up_day_uses_bullish_template():
    m = {"breadth": dict(BREADTH, upRatio=78.0, avg=1.8, down=800),
         "limits": LIMITS, "sectors": SECTORS}
    s = MT.one_sentence(m)
    assert "做多" in s and "普涨" in s


def test_one_sentence_mixed_day():
    m = {"breadth": dict(BREADTH, upRatio=48.0, avg=0.1), "limits": LIMITS, "sectors": SECTORS}
    s = MT.one_sentence(m)
    assert "分化" in s


def test_one_sentence_empty_safe():
    assert MT.one_sentence({}) == ""
    assert MT.one_sentence({"breadth": {"total": 0}}) == ""


# ---------------------------------------------------------------- 汇总
def test_summarize_returns_all_four_keys():
    out = MT.summarize(MARKET)
    assert set(out) == {"mood", "oneSentence", "structure", "distribution"}
    assert all(isinstance(v, str) and v for v in out.values())

# ---------------------------------------------------------------- 盘前空数据
def test_preopen_all_zero_returns_empty_copy():
    """盘前：total 有了但各桶全 0，不能输出"0 只落在…"这种误导文案。"""
    b = {"total": 5583, "up": 0, "down": 0, "flat": 0, "upRatio": None, "avg": None,
         "buckets": [{"label": "≤-9.8%", "count": 0}, {"label": "-3~0%", "count": 0}]}
    assert MT.distribution(b) == ""
    assert MT.structure({"boards": {"l1": [{"name": "银行", "memberCount": 42, "upCount": 0}]}}) == ""
    assert MT.mood(None) == "—"
    assert MT.one_sentence({"breadth": b, "limits": {}, "sectors": {}}) == ""