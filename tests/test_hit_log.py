# -*- coding: utf-8 -*-
"""web/hit_log.py —— 历史命中回顾：日志解析 + 收益口径（与离线 backtest.py 对齐）。"""
import datetime as dt
import json

import pytest

from web import hit_log as HL


# ---------------------------------------------------------------- 日期取谁
def test_hit_date_prefers_hit_time_over_filename():
    """PC 的 alerts_{T-1}.csv 文件名是 T-1，真正日期必须取 hit_time，否则整体错一天。"""
    assert HL._hit_date("2026-10-22 09:25:01", "2026-10-21") == "2026-10-22"
    assert HL._hit_date("", "2026-10-21") == "2026-10-21"        # 坏数据才回落到文件名
    assert HL._hit_date(None, "2026-10-21") == "2026-10-21"
    assert HL._hit_date("2026-10-22", "") == "2026-10-22"


# ---------------------------------------------------------------- CSV / JSON 解析
CSV_HEADER = ("hit_time,thscode,name,board,score,t1_pct,t1_limitup,continue_text,limit_up_time,"
              "seal_money_yi,t1_amount_yi,volume_ratio,high30_margin_pct,open_pct,open_price,"
              "prev_close,last_price,last_pct\r\n")


def _write_csv(path, rows):
    lines = [CSV_HEADER]
    for when, code, name, score, open_pct, open_price in rows:
        lines.append("%s,%s,%s,main,%s,9.99,True,3连板,09:35,1.46,10.58,0.574,5.19,%s,%s,56.12,60.0,0.01\r\n"
                     % (when, code, name, score, open_pct, open_price))
    path.write_text("".join(lines), encoding="utf-8-sig")


def test_parse_alert_csv_main_and_deep(tmp_path):
    _write_csv(tmp_path / "alerts_2026-10-21.csv",
               [("2026-10-22 09:25:01", "002929.SZ", "润建股份", "96.6", "-5.35", "53.12")])
    _write_csv(tmp_path / "alerts_deep_2026-10-16.csv",
               [("2026-10-19 09:25:02", "300750.SZ", "宁德时代", "88.0", "-8.10", "200.5")])

    main = HL._from_alert_csv(tmp_path / "alerts_2026-10-21.csv")
    assert len(main) == 1
    h = main[0]
    assert h["date"] == "2026-10-22" and h["zone"] == "main"
    assert h["thscode"] == "002929.SZ" and h["name"] == "润建股份"
    assert h["open_pct"] == -5.35 and h["buy_logged"] == 53.12
    assert h["score"] == 96.6 and h["continue"] == "3连板"

    deep = HL._from_alert_csv(tmp_path / "alerts_deep_2026-10-16.csv")
    assert deep[0]["zone"] == "deep" and deep[0]["date"] == "2026-10-19"


def test_parse_session_json(tmp_path):
    (tmp_path / "session_hits_2026-10-22.json").write_text(json.dumps({
        "date": "2026-10-22",
        "hits": [{"thscode": "600000.SH", "name": "浦发银行", "hit_time": "2026-10-22 09:30:05",
                  "open_pct": -6.1, "open_price": 10.2, "score": 71.0, "t1_pct": 9.9}],
        "deep_hits": [{"thscode": "300750.SZ", "name": "宁德时代", "hit_time": "2026-10-22 09:31:00",
                       "open_pct": -8.4, "open_price": 180.0, "score": 65.0}],
    }, ensure_ascii=False), encoding="utf-8")

    rows = HL._from_session_json(tmp_path / "session_hits_2026-10-22.json")
    assert [r["zone"] for r in rows] == ["main", "deep"]
    assert all(r["date"] == "2026-10-22" for r in rows)
    assert rows[0]["thscode"] == "600000.SH" and rows[0]["buy_logged"] == 10.2


# ---------------------------------------------------------------- 汇总逻辑（纯函数）
def _hit(date, code, zone="main", score=80.0):
    return {"date": date, "thscode": code, "name": code, "zone": zone, "open_pct": -6.0,
            "buy_logged": None, "score": score, "t1_pct": 9.9, "continue": "", "hit_time": ""}


def _bars(rows):
    """rows: [(date, open, high, low, close), ...]"""
    return [{"date": d, "open": o, "high": h, "low": lo, "close": c, "volume": 1.0}
            for d, o, h, lo, c in rows]


def test_summarize_matches_backtest_formula():
    """买入价 = T 日开盘；r0 收盘/买-1；dd 最低/买-1；rk = T+k 收盘/买-1；o1 = T+1 开盘/买-1。"""
    bars = _bars([
        ("2026-10-22", 10.0, 10.9, 9.4, 10.5),      # T：买 10.0，收 10.5，最低 9.4
        ("2026-10-23", 10.8, 11.0, 10.6, 10.9),     # T+1：开 10.8 收 10.9
        ("2026-10-26", 11.0, 11.2, 10.7, 11.1),     # T+2
        ("2026-10-27", 11.2, 11.3, 10.9, 10.0),     # T+3
    ])
    rows, stats, groups, coverage = HL.summarize(
        [_hit("2026-10-22", "600000.SH")], {"600000.SH": bars}, horizon=3)

    r = rows[0]
    assert r["status"] == "done"
    assert r["buy"] == 10.0
    assert r["r0"] == 5.0                       # 10.5/10.0-1
    assert r["dd"] == -6.0                      # 9.4/10.0-1
    assert r["o1"] == 8.0                       # 10.8/10.0-1
    assert r["r1"] == 9.0                       # 10.9/10.0-1
    assert r["r2"] == 11.0
    assert r["r3"] == 0.0                       # 10.0/10.0-1
    assert stats["r1"]["n"] == 1 and stats["r1"]["win"] == 100.0
    assert coverage == {"total": 1, "done": 1, "pending": 0, "missing": 0, "suspect": 0}


def test_summarize_marks_pending_and_excludes_from_win_rate():
    """T+3 还没到：状态 pending，r3 为 None，且不进胜率统计（不能把"还没发生"算成亏）。"""
    bars = _bars([
        ("2026-11-16", 10.0, 10.5, 9.8, 10.2),
        ("2026-11-17", 10.1, 10.4, 9.9, 9.8),       # T+1 收盘低于买入价
    ])
    rows, stats, _, coverage = HL.summarize(
        [_hit("2026-11-16", "600000.SH")], {"600000.SH": bars}, horizon=3)

    assert rows[0]["status"] == "pending"
    assert rows[0]["r1"] == -2.0
    assert rows[0]["r2"] is None and rows[0]["r3"] is None
    assert stats["r1"]["n"] == 1 and stats["r1"]["win"] == 0.0
    assert stats["r2"] is None and stats["r3"] is None
    assert coverage["pending"] == 1 and coverage["done"] == 0


def test_summarize_marks_missing_when_no_bar_for_hit_day():
    """取不到 T 日那根 K 线（或当天还没收盘）→ missing，不参与任何均值。"""
    bars = _bars([("2026-11-17", 10.0, 10.5, 9.8, 10.2)])
    rows, stats, _, coverage = HL.summarize(
        [_hit("2026-11-16", "600000.SH")], {"600000.SH": bars}, horizon=3)
    assert rows[0]["status"] == "missing" and rows[0]["r0"] is None
    assert stats["r0"] is None
    assert coverage["missing"] == 1

    rows2, _, _, _ = HL.summarize([_hit("2026-11-16", "999999.SZ")], {}, horizon=3)
    assert rows2[0]["status"] == "missing"


def test_stats_are_none_safe_and_median_correct():
    s = HL._stats([None, 4.0, -2.0, None, 10.0])
    assert s["n"] == 3
    assert s["mean"] == 4.0                 # (4-2+10)/3
    assert s["median"] == 4.0
    assert round(s["win"], 1) == 66.7       # 2/3 为正
    assert s["worst"] == -2.0 and s["best"] == 10.0
    assert HL._stats([None, None]) is None


def test_groups_split_main_and_deep():
    bars = _bars([("2026-10-22", 10.0, 10.2, 9.9, 10.1),
                  ("2026-10-23", 10.2, 10.4, 10.1, 10.3)])
    hits = [_hit("2026-10-22", "600000.SH", "main"), _hit("2026-10-22", "300750.SZ", "deep")]
    _, _, groups, _ = HL.summarize(hits, {"600000.SH": bars, "300750.SZ": bars}, horizon=3)
    assert [g["key"] for g in groups] == ["main", "deep"]
    assert groups[0]["label"].startswith("低开命中")
    assert groups[1]["n"] == 1


# ---------------------------------------------------------------- 读目录 + 去重 + 窗口
def test_load_hits_dedups_and_applies_window(tmp_path):
    today = dt.date.today()
    d1 = (today - dt.timedelta(days=3)).isoformat()
    old = (today - dt.timedelta(days=400)).isoformat()

    # 同一笔命中被 PC(CSV) 与安卓(JSON) 各记了一次，且一条有 score 一条没有
    _write_csv(tmp_path / ("alerts_" + d1 + ".csv"),
               [(d1 + " 09:25:01", "600000.SH", "浦发银行", "", "-6.00", "10.0")])
    (tmp_path / ("session_hits_" + d1 + ".json")).write_text(json.dumps({
        "date": d1,
        "hits": [{"thscode": "600000.SH", "name": "浦发银行", "hit_time": d1 + " 09:25:01",
                  "open_pct": -6.0, "open_price": 10.0, "score": 77.0}],
        "deep_hits": [],
    }, ensure_ascii=False), encoding="utf-8")
    # 窗口外的老命中要被滤掉
    _write_csv(tmp_path / ("alerts_" + old + ".csv"),
               [(old + " 09:25:01", "300750.SZ", "宁德时代", "60", "-7.00", "100.0")])

    rows, meta = HL.load_hits(30, [tmp_path])
    assert len(rows) == 1
    assert rows[0]["date"] == d1 and rows[0]["thscode"] == "600000.SH"
    assert rows[0]["score"] == 77.0                 # 保留了信息更全的那条
    assert meta["found"] == 1 and meta["last_hit"] == d1
    assert len(meta["files"]) == 2                  # 老文件在窗口内没行，不算


def test_build_without_any_log_explains_where_to_look(tmp_path, monkeypatch):
    monkeypatch.setattr(HL, "_cache_file", lambda: None)
    out = HL.build(days=30, horizon=3, dirs=[tmp_path])
    assert out["ok"] is True
    assert out["rows"] == [] and out["coverage"]["total"] == 0
    assert "alerts_*.csv" in out["note"] and "session_hits_*.json" in out["note"]
    assert out["meta"]["dirs"] == [str(tmp_path)]


def test_build_computes_and_reports_coverage(tmp_path, monkeypatch):
    today = dt.date.today()
    d = (today - dt.timedelta(days=2)).isoformat()
    d1 = (today - dt.timedelta(days=1)).isoformat()
    _write_csv(tmp_path / ("alerts_" + d + ".csv"),
               [(d + " 09:25:01", "600000.SH", "浦发银行", "80", "-6.00", "10.0")])

    bars = {d: (10.0, 10.4, 9.9, 10.2), d1: (10.2, 10.5, 10.1, 10.4)}
    seq = [{"date": k, "open": v[0], "high": v[1], "low": v[2], "close": v[3], "volume": 1.0}
           for k, v in sorted(bars.items())]
    monkeypatch.setattr(HL, "_fetch_bars", lambda codes: ({"600000.SH": seq}, []))
    monkeypatch.setattr(HL, "_cache_file", lambda: None)

    out = HL.build(days=30, horizon=3, dirs=[tmp_path])
    assert out["ok"] and out["coverage"]["total"] == 1
    assert out["rows"][0]["r0"] == 2.0            # 10.2/10.0-1
    assert out["stats"]["r1"]["mean"] == 4.0      # 10.4/10.0-1
    assert out["failed"] == []

# ---------------------------------------------------------------- 疑似假命中（开盘价口径）
def test_summarize_flags_suspect_when_logged_gap_disagrees_with_bar():
    """真实案例：09:25 快照的开盘价还是前一日 → 记为 -5.35%，实际高开 +6.91%。"""
    bars = _bars([
        ("2026-10-21", 53.10, 56.12, 52.42, 56.12),
        ("2026-10-22", 60.00, 61.50, 56.23, 56.86),      # 真实开盘 60.00 = 高开 +6.91%
        ("2026-10-23", 55.97, 56.95, 52.67, 55.03),
        ("2026-10-26", 55.51, 55.99, 49.90, 51.78),
        ("2026-10-27", 51.82, 56.96, 51.66, 54.04),
    ])
    hit = _hit("2026-10-22", "002929.SZ")
    hit["open_pct"] = -5.35                                # 引擎在 09:25 记的值（错的）
    rows, _, _, cov = HL.summarize([hit], {"002929.SZ": bars}, horizon=3)

    r = rows[0]
    assert r["buy"] == 60.00                               # 买入价用日线真实开盘
    assert r["prev_close"] == 56.12
    assert r["gap_real"] == 6.91
    assert r["suspect"] is True
    assert cov["suspect"] == 1


def test_summarize_not_suspect_when_gap_agrees():
    bars = _bars([("2026-10-21", 10.0, 10.2, 9.9, 10.0),
                  ("2026-10-22", 9.45, 9.6, 9.3, 9.5),
                  ("2026-10-23", 9.5, 9.7, 9.4, 9.6),
                  ("2026-10-26", 9.6, 9.8, 9.5, 9.7)])
    hit = _hit("2026-10-22", "600000.SH")
    hit["open_pct"] = -5.50                                # 9.45/10.0-1 ≈ -5.5%
    rows, _, _, cov = HL.summarize([hit], {"600000.SH": bars}, horizon=3)
    assert rows[0]["suspect"] is False and cov["suspect"] == 0
    assert rows[0]["gap_real"] == -5.5