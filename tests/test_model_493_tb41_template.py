"""MODEL-493: the Terminal-Bench 4.1 board declares a row template and an effort-aware match.

Invented values in the board's real structure (the rows ``_project_tbench`` returns).
"""

from __future__ import annotations

from scripts import model_233_evidence, refresh_leaderboards as refresh

URL = refresh.TBENCH_URL
CARD = {"model_id": "acme/model-x", "display_name": "Model X", "version": "model-x"}


def _board(rows, key="terminal-bench-4-1", **extra):
    return refresh.BoardReading(
        key=key, source_id="x", benchmark_ids=frozenset({"terminal_bench_v4_1"}),
        source_url=URL, observed_at="2026-11-17", snapshot_ref="sha256:" + "0" * 64,
        rows=tuple({**row, "observed_at": "2026-11-17"} for row in rows), value_field="accuracy",
        **{"row_template": refresh.TBENCH_ROW, "effort_basis": "terminal_bench_v4_0", **extra},
    )


def _row(model, effort, agent="Claude Code", accuracy=40.0, date="2026-09-01"):
    return {"model": model, "reasoning_effort": effort, "agent": agent,
            "accuracy": accuracy, "date": date}


def _card(**stored):
    row = {"benchmark_id": "terminal_bench_v4_0", "source_kind": "benchmark_author",
           "source_url": "https://www.tbench.ai/leaderboard/terminal-bench/4.0",
           "model_id_as_evaluated": "Model X", **stored}
    return {**CARD, "benchmarks": {"evidence": [row]}}


def _new(board, front, tmp_path):
    return refresh._new_evidence(root=tmp_path, model_id=front["model_id"], front=front, board=board)


def test_declared_template_is_the_refreshed_4_0_shape():
    assert refresh.TBENCH_ROW == {
        "unit": "percent", "source_kind": "benchmark_author",
        "benchmark_version": "Terminal-Bench 4.1", "harness": "unregistered"}


def test_first_row_is_filed_with_the_template(tmp_path):
    rows, failures = _new(_board([_row("Model X", "max", accuracy=41.5)]), _card(effort="max"), tmp_path)
    assert not failures and len(rows) == 1
    row = rows[0]
    assert (row["benchmark_id"], row["unit"], row["source_kind"], row["measured_by"]) \
        == ("terminal_bench_v4_1", "percent", "benchmark_author", "benchmark_author")
    assert (row["benchmark_version"], row["harness"], row["effort"], row["score"]) \
        == ("Terminal-Bench 4.1", "unregistered", "max", 41.5)
    assert row["configuration"] == \
        "tbench.ai leaderboard row read 2026-11-17: agent Claude Code, reasoning effort max."
    assert row["source_url"] == URL and row["evidence_date"] == "2026-09-01"


def test_same_name_rows_select_the_stored_effort(tmp_path):
    rows = [_row("Model X", e, accuracy=a) for e, a in
            (("low", 10.0), ("high", 20.0), ("max", 30.0))]
    filed, failures = _new(_board(rows), _card(effort="high"), tmp_path)
    assert not failures and [(r["effort"], r["score"]) for r in filed] == [("high", 20.0)]


def test_stored_effort_read_from_a_hand_entered_name(tmp_path):
    front = _card(model_id_as_evaluated="Model X (max) with Claude Code")
    rows = [_row("Model X", "high", accuracy=20.0), _row("Model X", "max", accuracy=30.0)]
    filed, _ = _new(_board(rows), front, tmp_path)
    assert [(r["effort"], r["score"]) for r in filed] == [("max", 30.0)]


def test_no_unique_effort_selects_nothing(tmp_path):
    rows = [_row("Model X", "high"), _row("Model X", "max")]
    assert refresh._matching_new_row(_board(rows), {**CARD, "benchmarks": {"evidence": []}}) is None
    assert refresh._matching_new_row(_board(rows), _card(effort="low")) is None
    assert refresh._matching_new_row(_board(rows), _card(effort="max"))["reasoning_effort"] == "max"


def test_lab_self_report_does_not_state_the_effort(tmp_path):
    front = _card(effort="max")
    front["benchmarks"]["evidence"].append({
        "benchmark_id": "terminal_bench_v4_0", "source_url": "https://lab.example/card",
        "model_id_as_evaluated": "Model X", "effort": "low"})
    rows = [_row("Model X", "low"), _row("Model X", "max")]
    assert refresh._matching_new_row(_board(rows), front)["reasoning_effort"] == "max"


def test_other_boards_keep_the_name_only_match():
    rows = [_row("Model X", "high"), _row("Model X", "max")]
    board = _board(rows, key="other", effort_basis=None, row_template=None)
    assert refresh._matching_new_row(board, _card(effort="max")) is None
    assert refresh._matching_new_row(
        _board(rows[:1], key="other", effort_basis=None), _card(effort="max"))["model"] == "Model X"


def test_agent_wording_does_not_fire_on_another_board(monkeypatch, tmp_path):
    monkeypatch.setattr(refresh, "_matching_new_row", refresh._matching_new_row)
    monkeypatch.setattr(refresh, "_new_evidence", refresh._new_evidence)
    model_233_evidence._with_board_names(refresh)
    front = {"model_id": "anthropic/claude-fable-5-2", "display_name": "Claude Fable 5.2",
             "version": "claude-fable-5-2"}
    board = refresh.BoardReading(
        key="epoch", source_id="x", benchmark_ids=frozenset({"gpqa_diamond"}),
        source_url="https://epoch.ai/benchmarks/gpqa-diamond", observed_at="2026-11-17",
        snapshot_ref="sha256:" + "0" * 64, value_field="accuracy",
        rows=({"model": "claude-fable-5-2_max", "accuracy": 50.0, "agent": "Some Agent",
               "observed_at": "2026-11-17"},),
        row_template={"unit": "percent", "source_kind": "benchmark_author"})
    rows, failures = refresh._new_evidence(
        root=tmp_path, model_id=front["model_id"], front=front, board=board)
    assert not failures and rows[0]["effort"] == "max"
    assert rows[0]["configuration"] == "" and rows[0]["harness"] is None


def test_board_names_without_claude_match_an_anthropic_card(tmp_path):
    front = {"model_id": "anthropic/claude-fable-x", "display_name": "Claude Fable X",
             "version": "claude-fable-x",
             "benchmarks": {"evidence": [{
                 "benchmark_id": "terminal_bench_v4_0", "effort": "max",
                 "source_url": "https://www.tbench.ai/leaderboard/terminal-bench/4.0",
                 "model_id_as_evaluated": "Fable X"}]}}
    rows = [_row("Fable X", "high"), _row("Fable X", "max", accuracy=33.0)]
    filed, failures = _new(_board(rows), front, tmp_path)
    assert not failures and [(r["effort"], r["score"]) for r in filed] == [("max", 33.0)]
    other = _board(rows, key="other", effort_basis=None, row_template=None)
    assert refresh._matching_new_row(other, front) is None
