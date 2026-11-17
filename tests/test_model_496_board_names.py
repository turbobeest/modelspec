"""MODEL-496: exact board names for Claude Fable 5.2, and the neighbours that stay out."""

from __future__ import annotations

import pytest

from scripts import model_233_evidence, refresh_leaderboards as refresh

FABLE_5_2 = {"model_id": "anthropic/claude-fable-5-2", "display_name": "Claude Fable 5.2",
             "version": "claude-fable-5-2"}
OTHER = {"model_id": "anthropic/claude-fable-5-1", "display_name": "Claude Fable 5.1",
         "version": "claude-fable-5-1"}


def _board(key, field, names, benchmark="gpqa_diamond"):
    rows = tuple({"model": n, field: 0.5, "observed_at": "2026-11-17"} for n in names)
    return refresh.BoardReading(
        key=key, source_id="x", benchmark_ids=frozenset({benchmark}),
        source_url="https://epoch.ai/benchmarks/gpqa-diamond", observed_at="2026-11-17",
        rows=rows, value_field=field,
    )


@pytest.fixture
def matcher(monkeypatch):
    monkeypatch.setattr(refresh, "_matching_new_row", refresh._matching_new_row)
    monkeypatch.setattr(refresh, "_new_evidence", refresh._new_evidence)
    model_233_evidence._with_board_names(refresh)
    return refresh._matching_new_row


def _hit(matcher, names, front=FABLE_5_2, field="mean_score"):
    found = matcher(_board("t", field, names), front)
    return None if found is None else found["model"]


def test_epoch_max_row_maps_to_fable_5_2(matcher):
    assert _hit(matcher, ["claude-fable-5-1_max", "claude-fable-5-2_max", "claude-fable-5_max"]) \
        == "claude-fable-5-2_max"


def test_epoch_row_carries_effort_max(matcher, tmp_path):
    board = refresh.BoardReading(
        key="epoch", source_id="model-143-evidence-epoch-gpqa-diamond-csv",
        benchmark_ids=frozenset({"gpqa_diamond"}), source_url="https://epoch.ai/benchmarks/gpqa-diamond",
        observed_at="2026-11-17", rows=({"model": "claude-fable-5-2_max", "mean_score": 0.5,
                                         "observed_at": "2026-11-17"},),
        value_field="mean_score", fraction=True, snapshot_ref="sha256:" + "0" * 64,
        row_template={"unit": "percent", "source_kind": "benchmark_author"},
    )
    rows, failures = refresh._new_evidence(
        root=tmp_path, model_id="anthropic/claude-fable-5-2", front=FABLE_5_2, board=board)
    assert not failures
    assert [(r["model_id_as_evaluated"], r["effort"], r["score"]) for r in rows] \
        == [("claude-fable-5-2_max", "max", 50.0)]


def test_terminal_bench_exact_name_maps(matcher):
    assert _hit(matcher, ["Fable 5", "Fable 5.1", "Fable 5.2"], field="accuracy") == "Fable 5.2"


def test_fallback_row_stays_unmatched(matcher):
    assert _hit(matcher, ["claude-fable-5-2-fallback_max"]) is None
    assert _hit(matcher, ["claude-fable-5-2-fallback_max", "claude-fable-5-2_max"]) \
        == "claude-fable-5-2_max"


def test_arena_xhigh_stays_unmatched(matcher):
    assert _hit(matcher, ["Claude Fable 5.2 (xHigh)", "Claude Fable 5.1 (Max)"],
                field="rating") is None


@pytest.mark.parametrize("names", [
    ["claude-fable-5-1_max", "claude-fable-5_max"],
    ["Fable 5.1", "Fable 5"],
    ["Claude-Fable-5.1 (high)", "Claude Fable 5.1 (Max)"],
    ["Claude Mythos 5.2", "claude-mythos-5-2_max", "Mythos 5.2"],
])
def test_neighbours_stay_unmatched(matcher, names):
    assert _hit(matcher, names) is None


def test_entries_do_not_leak_to_other_cards(matcher):
    assert _hit(matcher, ["claude-fable-5-2_max", "Fable 5.2"], front=OTHER) is None
