"""MODEL-482: a refresh run reports live rows it left stale, and the workflow fails on them."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import yaml

from scripts import refresh_leaderboards as refresh

LIVE = SimpleNamespace(volatility="live")
STATIC = SimpleNamespace(volatility="static")
REGISTERED = {"live-src": LIVE, "static-src": STATIC}
WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "private-writers" / "leaderboard-refresh.yml"


def _row(benchmark: str, source: str, observed: str, **extra) -> dict:
    return {
        "benchmark_id": benchmark, "source_url": f"https://example.test/{benchmark}",
        "model_id_as_evaluated": "M", "score": 1.0,
        "sources": [{"source_id": source}], "observed_at": observed, **extra,
    }


def _stale(rows, refreshed=frozenset(), registered=REGISTERED):
    cards = {"a/m": {"benchmarks": {"evidence": rows}}}
    return refresh.left_stale_rows(cards, set(refreshed), registered, observed_at="2026-11-22")


def test_old_live_row_is_reported():
    found = _stale([_row("b1", "live-src", "2026-10-19")])
    assert [(f.model_id, f.benchmark) for f in found] == [("a/m", "b1")]
    assert "2026-10-19" in found[0].reason


def test_edge_of_the_stale_line():
    on_line = "2026-11-01"  # 21 days
    past_line = "2026-10-31"  # 22 days
    assert _stale([_row("b1", "live-src", on_line)]) == []
    assert len(_stale([_row("b1", "live-src", past_line)])) == 1


def test_rewritten_marked_static_and_arena_rows_are_not_reported():
    rewritten = _row("b1", "live-src", "2026-10-01")
    key = refresh.evidence_key(rewritten)
    assert _stale([rewritten], refreshed={("a/m", key)}) == []
    assert _stale([_row("b2", "live-src", "2026-10-01", not_published_since="2026-11-01")]) == []
    assert _stale([_row("b3", "static-src", "2026-10-01")]) == []
    arena = _row("arena_text", "live-src", "2026-10-01",
                 source_url=refresh.ARENA_DATASET_ROOT)
    assert _stale([arena]) == []


def test_observation_day_falls_back_to_source_ref_then_verified_at():
    row = _row("b1", "live-src", "")
    row.pop("observed_at")
    row["sources"][0]["retrieved_at"] = "2026-10-01T00:00:00"
    assert len(_stale([row])) == 1
    row["sources"][0].pop("retrieved_at")
    row["verified_at"] = "2026-11-20"
    assert _stale([row]) == []


def test_report_renders_and_serialises_the_stale_rows(tmp_path):
    report = refresh.RefreshReport()
    report.left_stale = _stale([_row("b1", "live-src", "2026-10-19")])
    assert "Live rows left stale" in refresh.render_report(report)
    target = tmp_path / "report.json"
    refresh.write_report_json(target, report)
    assert '"left_stale"' in target.read_text()


def test_workflow_fails_a_run_that_left_a_live_row_stale():
    steps = yaml.safe_load(WORKFLOW.read_text())["jobs"]["refresh"]["steps"]
    result = next(step for step in steps if step.get("id") == "result")
    assert "left_stale=" in result["run"]
    gate = next(step for step in steps if step.get("name") == "Fail a run that left a live row stale")
    assert gate["if"] == "steps.result.outputs.left_stale != '0'"
    assert "continue-on-error" not in gate and "exit 1" in gate["run"]
    # It runs after the pull request is opened, so the written rows are not lost.
    opened = next(i for i, s in enumerate(steps) if s.get("name") == "Open the score-only pull request")
    assert steps.index(gate) > opened
