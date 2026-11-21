"""MODEL-521: the stale label is display and reports only, with exact lines and text."""

from __future__ import annotations

import ast
import inspect
from datetime import date, timedelta
from pathlib import Path

from decision import staleness
from decision.staleness import FIRST_QUARTER_END, age_line, is_stale, label
from pipeline import render
from scripts.data_trust import trust_line
from scripts.data_trust.catalogue import Catalogue

AFTER = FIRST_QUARTER_END + timedelta(days=1)


def _checked(today, days):
    return (today - timedelta(days=days)).isoformat()


def test_override_end_date_is_one_named_constant():
    assert FIRST_QUARTER_END == date(2027, 3, 31)
    assert staleness.FIRST_QUARTER_DAYS == 120


def test_lines_during_the_first_quarter_are_120_for_every_facet():
    for today in (date(2026, 11, 21), FIRST_QUARTER_END):
        for facet in ("model.context_window", "offering.price.input", "offering.subscription.x"):
            assert age_line(facet, today) == 120
            assert not is_stale(_checked(today, 120), facet, today)
            assert is_stale(_checked(today, 121), facet, today)


def test_lines_after_the_override_are_90_and_45():
    assert age_line("model.context_window", AFTER) == 90
    for facet in ("offering.price.input", "offering.subscription.plan"):
        assert age_line(facet, AFTER) == 45
        assert not is_stale(_checked(AFTER, 45), facet, AFTER)
        assert is_stale(_checked(AFTER, 46), facet, AFTER)
    assert not is_stale(_checked(AFTER, 90), "model.context_window", AFTER)
    assert is_stale(_checked(AFTER, 91), "model.context_window", AFTER)
    assert not is_stale(None, "model.context_window", AFTER)


def test_label_text_is_exact():
    assert label("2026-09-20") == "Last checked 2026-09-20, may be out of date"


def test_site_row_shows_the_exact_label_only_when_stale():
    rec = {"verified_at": "2026-09-01"}
    shown = render._stale_note(rec, date(2027, 4, 1))
    assert "Last checked 2026-09-01, may be out of date" in shown
    assert render._stale_note(rec, date(2026, 10, 1)) == ""
    assert render._stale_note({}, date(2027, 4, 1)) == ""
    assert render._stale_note(rec, None) == ""


def test_trust_report_uses_the_rule_in_force(tmp_path):
    def fact(field, when):
        return {"kind": "fact", "field": field, "verification": {"date": when}}

    c = Catalogue(facts=[fact("offering.price.input", "2027-02-10"), fact("model.x", "2027-02-10")])
    during = trust_line.compute(c, tmp_path, date(2027, 3, 31))["stale"]
    after = trust_line.compute(c, tmp_path, AFTER)["stale"]
    assert (during["age_line_days"], during["age_line_days_price_subscription"]) == (120, 120)
    assert during["older"] == 0
    assert (after["age_line_days"], after["age_line_days_price_subscription"]) == (90, 45)
    assert after["older"] == 1 and after["by_group"]["offering price"]["older"] == 1


def test_staleness_is_not_a_ranking_input():
    ROOT = Path(__file__).resolve().parents[1]
    for rel in ("api/ranking", "decision"):
        for path in (ROOT / rel).rglob("*.py"):
            if path.name == "staleness.py":
                continue
            src = path.read_text()
            assert "decision.staleness" not in src and "import staleness" not in src, path


def test_no_module_scope_clock_read():
    tree = ast.parse(inspect.getsource(staleness))
    src = inspect.getsource(staleness)
    assert "today()" not in src and "now(" not in src
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.Expr)):
            assert "today" not in ast.dump(node) or isinstance(node, ast.Expr)
