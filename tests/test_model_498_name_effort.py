"""MODEL-498: a board name that states an effort files that effort; any other name is unchanged."""

from __future__ import annotations

import pytest

from scripts import refresh_leaderboards as refresh

FABLE_5_2 = {"model_id": "anthropic/claude-fable-5-2", "display_name": "Claude Fable 5.2",
             "version": "claude-fable-5-2"}


def _rows(tmp_path, name):
    board = refresh.BoardReading(
        key="matharena", source_id="x", benchmark_ids=frozenset({"aime_2026"}),
        source_url="https://matharena.ai/competition_tables/aime--aime_2026",
        observed_at="2026-11-17",
        rows=({"model": name, "mean_score": 0.5, "observed_at": "2026-11-17"},),
        value_field="mean_score", fraction=True, snapshot_ref="sha256:" + "0" * 64,
        row_template={"unit": "percent", "source_kind": "benchmark_author"},
    )
    rows, failures = refresh._new_evidence(
        root=tmp_path, model_id=FABLE_5_2["model_id"], front=FABLE_5_2, board=board)
    assert not failures
    return rows


@pytest.mark.parametrize("name,effort", [
    ("Claude-Fable-5.2 (max)", "max"),
    ("Claude Fable 5.2 (xHigh)", "xhigh"),
    ("Claude Fable 5.2 (High)", "high"),
    ("Claude Fable 5.2 (max effort)", "max"),
    ("Claude Fable 5.2 (maximum)", "max"),
])
def test_effort_suffix_is_filed(tmp_path, name, effort):
    rows = _rows(tmp_path, name)
    assert [(r["model_id_as_evaluated"], r["effort"]) for r in rows] == [(name, effort)]


@pytest.mark.parametrize("name", [
    "Claude Fable 5.2 (thinking)",
    "Claude Fable 5.2 (20261101)",
    "Claude Fable 5.2 (Thinking 16K)",
    "Claude Fable 5.2 (default)",
    "Claude Fable 5.2",
])
def test_other_names_state_no_effort(tmp_path, name):
    assert refresh._name_effort(name) is None
    for row in _rows(tmp_path, name):
        assert row["effort"] is None


def test_name_effort_reads_only_the_trailing_parenthesis():
    assert refresh._name_effort("Model (max) preview") is None
    assert refresh._name_effort(None) is None
