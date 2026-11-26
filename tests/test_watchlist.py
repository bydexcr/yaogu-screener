# -*- coding: utf-8 -*-
"""自选股存储层 + 同步代理的单元测试

覆盖：
  · 代码归一（裸代码 / 前缀 / 后缀 / 非法）
  · 增删改查、重复加入、排序、备注、批量导入、CSV 导出
  · 空文件/坏文件不炸（返回空结构）
  · 同步源解析：电脑端（无 watch_source）→ 空串；手机端 → 规范化 URL
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "web"))

import watchlist_store as W      # noqa: E402


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    """每个用例用自己的 data 目录，避免污染真实 watchlist.json。"""
    monkeypatch.setenv("YAOGU_DATA_DIR", str(tmp_path))
    yield tmp_path


# ---------------------------------------------------------------- 代码归一
@pytest.mark.parametrize("raw,expect", [
    ("600519", "600519.SH"),
    ("600519.sh", "600519.SH"),
    ("sh600519", "600519.SH"),        # 前缀写法：字母前缀 + 6 位数字
    ("sz000001", "000001.SZ"),
    ("000001.SZ", "000001.SZ"),
    ("300750", "300750.SZ"),
    ("688981", "688981.SH"),
    ("830799", "830799.BJ"),
    ("920001", "920001.BJ"),
    ("  600519  ", "600519.SH"),
    ("abc", ""),
    ("", ""),
    ("12345", ""),
    ("60051", ""),
])
def test_norm_code(raw, expect):
    assert W.norm_code(raw) == expect


def test_guess_suffix_matches_strategy_boards():
    """与 strategy.board_key 的口径一致：主板/创业板/科创板/北交所都能推断。"""
    assert W.guess_suffix("600519") == "SH"
    assert W.guess_suffix("000001") == "SZ"
    assert W.guess_suffix("300750") == "SZ"
    assert W.guess_suffix("688981") == "SH"
    assert W.guess_suffix("830799") == "BJ"
    assert W.guess_suffix("123") == ""


# ---------------------------------------------------------------- 增删改查
def test_add_and_duplicate():
    r = W.add("600519", "贵州茅台")
    assert r["ok"] and r["added"] is True
    items = W.items()
    assert items[0]["thscode"] == "600519.SH"
    assert items[0]["name"] == "贵州茅台"
    assert items[0]["added_at"]        # 加入时间必须落盘
    # 重复加入：不改顺序、不重复、给出提示
    r2 = W.add("600519.sh")
    assert r2["added"] is False and "已在自选" in r2["note"]
    assert len(W.items()) == 1


def test_add_invalid_code_is_rejected():
    r = W.add("not-a-code")
    assert r["ok"] is False and "无法识别" in r["error"]
    assert W.items() == []


def test_remove_and_clear():
    W.add("600519")
    W.add("000001")
    assert W.remove("600519")["removed"] is True
    assert [i["thscode"] for i in W.items()] == ["000001.SZ"]
    assert W.remove("600519")["removed"] is False
    assert W.clear()["items"] == []
    assert W.items() == []


def test_note_and_rename():
    W.add("600519", "600519")
    assert W.set_note("600519", "核心仓位，只做低吸")["ok"] is True
    assert W.items()[0]["note"] == "核心仓位，只做低吸"
    assert W.rename("600519", "贵州茅台")["ok"] is True
    assert W.items()[0]["name"] == "贵州茅台"
    # 不在自选里
    assert W.set_note("000001", "x")["ok"] is False


def test_note_is_truncated():
    W.add("600519")
    W.set_note("600519", "长" * 500)
    assert len(W.items()[0]["note"]) == 120


def test_add_defaults_to_not_held():
    W.add("600519", "贵州茅台")
    it = W.items()[0]
    assert it["held"] is False
    assert it["cost"] is None


def test_set_hold_with_cost():
    W.add("600519", "贵州茅台")
    assert W.set_hold("600519", True, "1500.5")["ok"] is True
    it = W.items()[0]
    assert it["held"] is True
    assert it["cost"] == 1500.5


def test_set_hold_rejects_bad_cost():
    W.add("600519")
    assert "不是数字" in W.set_hold("600519", True, "abc")["error"]
    assert "大于 0" in W.set_hold("600519", True, "0")["error"]
    assert "大于 0" in W.set_hold("600519", True, "-3")["error"]
    assert "看起来不对" in W.set_hold("600519", True, "999999")["error"]
    # 校验失败不能落库
    assert W.items()[0]["held"] is False


def test_set_hold_allows_empty_cost():
    """先标持有、成本待补：合法（页面上成本框留空）。"""
    W.add("600519")
    assert W.set_hold("600519", True)["ok"] is True
    it = W.items()[0]
    assert it["held"] is True and it["cost"] is None


def test_unhold_clears_cost():
    W.add("600519")
    W.set_hold("600519", True, "1500")
    assert W.set_hold("600519", False)["ok"] is True
    it = W.items()[0]
    assert it["held"] is False and it["cost"] is None


# ---------------------------------------------------------------- 持股数量
def test_set_qty_with_cost():
    W.add("600519", "贵州茅台")
    assert W.set_hold("600519", True, "1500", "1000")["ok"] is True
    it = W.items()[0]
    assert it["cost"] == 1500 and it["qty"] == 1000


def test_qty_rejects_bad_values():
    W.add("600519")
    assert "不是数字" in W.set_hold("600519", True, "10", "abc")["error"]
    assert "大于 0" in W.set_hold("600519", True, "10", "0")["error"]
    assert "整数" in W.set_hold("600519", True, "10", "100.5")["error"]
    assert "看起来不对" in W.set_hold("600519", True, "10", "99999999999")["error"]
    # 校验失败不能落库
    assert W.items()[0]["qty"] is None


def test_qty_accepts_commas_and_space():
    W.add("600519")
    assert W.set_hold("600519", True, "1500", " 1,000 ")["ok"] is True
    assert W.items()[0]["qty"] == 1000


def test_qty_cleared_when_unheld():
    W.add("600519")
    W.set_hold("600519", True, "1500", "1000")
    W.set_hold("600519", False)
    it = W.items()[0]
    assert it["qty"] is None and it["cost"] is None


# ---------------------------------------------------------------- 持仓汇总
def test_portfolio_amount_and_weighted_pct():
    items = [
        {"thscode": "A", "name": "甲", "held": True, "cost": 10.0, "qty": 1000, "last": 11.0, "prev": 10.5},
        {"thscode": "B", "name": "乙", "held": True, "cost": 20.0, "qty": 500, "last": 18.0, "prev": 19.0},
        {"thscode": "C", "name": "丙", "held": False, "cost": 5.0, "qty": 100, "last": 9.0},
    ]
    p = W.portfolio(items)
    assert p["held"] == 2 and p["with_qty"] == 2
    assert p["cost_amt"] == 20000.0            # 10*1000 + 20*500
    assert p["value"] == 20000.0               # 11*1000 + 18*500
    assert p["pnl_amt"] == 0.0
    assert p["pnl_pct"] == 0.0                 # 按金额加权：(+1000 -1000)/20000
    assert p["today_amt"] == 0.0               # prev 10.5*1000 + 19*500 = 20000


def test_portfolio_falls_back_to_cost_weighted_pct():
    """没填数量时只给百分比（按成本加权），金额字段为 None。"""
    items = [
        {"thscode": "A", "name": "甲", "held": True, "cost": 10.0, "qty": None, "last": 11.0, "pnl_pct": 10.0},
        {"thscode": "B", "name": "乙", "held": True, "cost": 30.0, "qty": None, "last": 27.0, "pnl_pct": -10.0},
    ]
    p = W.portfolio(items)
    assert p["with_qty"] == 0
    assert p["cost_amt"] is None and p["value"] is None and p["pnl_amt"] is None
    assert p["pnl_pct"] == -5.0                # (10*10 + 30*-10)/40


def test_portfolio_empty():
    p = W.portfolio([])
    assert p["held"] == 0 and p["pnl_pct"] is None and p["pnl_amt"] is None


def test_portfolio_partial_qty():
    """部分填了数量：金额只算填了的那几只，并标出未计入的数量。"""
    items = [
        {"thscode": "A", "name": "甲", "held": True, "cost": 10.0, "qty": 1000, "last": 12.0},
        {"thscode": "B", "name": "乙", "held": True, "cost": 20.0, "qty": None, "last": 20.0, "pnl_pct": 0.0},
    ]
    p = W.portfolio(items)
    assert p["held"] == 2 and p["with_qty"] == 1
    assert p["cost_amt"] == 10000.0
    assert p["value"] == 12000.0
    assert p["pnl_amt"] == 2000.0
    assert p["pnl_pct"] == 20.0                # 只按有数量的那只


def test_set_hold_unknown_code():
    assert W.set_hold("600519", True, "10")["ok"] is False


def test_reorder_moves_and_keeps_others():
    for c in ("600519", "000001", "300750"):
        W.add(c)
    W.reorder(["300750.SZ", "600519.SH"])
    assert [i["thscode"] for i in W.items()] == ["300750.SZ", "600519.SH", "000001.SZ"]


def test_reorder_ignores_unknown_codes():
    W.add("600519")
    W.reorder(["999999.SH", "600519.SH"])
    assert [i["thscode"] for i in W.items()] == ["600519.SH"]


# ---------------------------------------------------------------- 批量导入
def test_parse_batch_variants():
    parsed = W.parse_batch("""600519 贵州茅台
000001,平安银行
sz300750
# 注释行
  688981  中芯国际  
abc
""")
    codes = [p["thscode"] for p in parsed]
    assert codes == ["600519.SH", "000001.SZ", "300750.SZ", "688981.SH"]
    assert parsed[0]["name"] == "贵州茅台"
    assert parsed[2]["name"] == ""


def test_batch_add_dedups_and_uses_resolver():
    W.add("600519", "贵州茅台")
    r = W.batch_add("600519\n000001\n300750", resolve=lambda c: {"000001.SZ": "平安银行"}.get(c, ""))
    assert r["added"] == ["000001.SZ", "300750.SZ"]
    assert r["skipped"] == 1
    names = {i["thscode"]: i["name"] for i in W.items()}
    assert names["000001.SZ"] == "平安银行"          # resolver 补上了名字
    assert names["300750.SZ"] == "300750"            # 解析不到就用代码兜底


def test_batch_add_empty_text():
    r = W.batch_add("   \n# x\n")
    assert r["ok"] is False


def test_max_items_limit():
    for i in range(W.MAX_ITEMS):
        code = "6%05d" % i
        W.add(code)
    r = W.add("000001")
    assert r["ok"] is False and "最多" in r["error"]


# ---------------------------------------------------------------- 导出 / 容错
def test_export_csv_has_bom_and_header():
    W.add("600519", "贵州茅台")
    text = W.export_csv()
    assert text.startswith("\ufeff")
    lines = text.lstrip("\ufeff").splitlines()
    assert lines[0] == "thscode,name,added_at,note,held,cost,qty"
    assert lines[1].startswith("600519.SH,贵州茅台,")


def test_corrupt_file_degrades_to_empty(tmp_path):
    p = W.store_path()
    p.write_text("{ 这不是 JSON", encoding="utf-8")
    assert W.items() == []
    # 坏文件后仍可正常写入
    assert W.add("600519")["added"] is True


def test_schema_and_updated_written(tmp_path):
    W.add("600519")
    raw = json.loads(W.store_path().read_text(encoding="utf-8"))
    assert raw["schema"] == W.SCHEMA
    assert raw["updated"]
    assert not (tmp_path / "watchlist.json.tmp").exists()     # 原子写：临时文件已 rename
