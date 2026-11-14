"""The Terminal-Bench 4.1 declaration checks the board's own name (MODEL-493-F).

No network: a stub sits under the real redirect machinery, and the page is an
invented payload in the shape of the real one.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from decision.sources import CopyStore
from scripts import refresh_leaderboards as refresh
from tests.test_refresh_final_address import _install

OBSERVED = "2026-11-14"
OLD_ADDRESS = "https://www.tbench.ai/leaderboard/terminal-bench/4.0"
SOURCE_ID = "model-493-evidence-terminal-bench-4-1-json"
BENCHMARK = "terminal_bench_v4_1"
ROWS = [
    {"metadata": {"model_display": {"label": "Alpha One"}, "reasoning_effort": "high",
                  "agent_display": {"label": "Harness A"}, "date": "2026-10-01"},
     "metrics": {"accuracy": 41.5}},
    {"metadata": {"model_display": "Beta Two", "reasoning_effort": None,
                  "agent_display": "Harness B", "date": "2026-10-02"},
     "metrics": {"accuracy": 12.25}},
]


def _page(leaderboard=None, *, rows=ROWS, key: str = "leaderboard") -> bytes:
    """An invented page: React payload chunks carrying one leaderboard object and its rows."""
    board = {"name": "4-1-0", "title": "Terminal-Bench 4.1"} if leaderboard is None else leaderboard
    payload = "7:" + json.dumps({"state": {"data": {key: board, "rows": rows}}}, separators=(",", ":"))
    chunk = json.dumps(payload)[1:-1]
    return f'<html><script>self.__next_f.push([1,"{chunk}"])</script></html>'.encode()


def _wrap(obj: dict) -> bytes:
    payload = "7:" + json.dumps(obj, separators=(",", ":"))
    chunk = json.dumps(payload)[1:-1]
    return f'<html><script>self.__next_f.push([1,"{chunk}"])</script></html>'.encode()


NAMED = {"name": "4-1-0", "title": "Terminal-Bench 4.1"}
OTHER = {"name": "4-2-0", "title": "Terminal-Bench 4.2"}
OTHER_ROWS = [{"metadata": {"model_display": "Gamma", "date": "2026-11-01"},
               "metrics": {"accuracy": 99.0}}]


def _project(body: bytes, **kwargs) -> dict:
    return json.loads(refresh._project_tbench(
        body.decode(), url=refresh.TBENCH_URL, page_ref="ref", observed_at=OBSERVED, **kwargs))


# ── (a) the name matches: rows are projected ────────────────────────────────

def test_matching_name_projects_the_rows():
    rows = _project(_page())["rows"]
    assert [(r["model"], r.get("reasoning_effort"), r.get("agent"), r["accuracy"])
            for r in rows] == [("Alpha One", "high", "Harness A", 41.5),
                               ("Beta Two", None, "Harness B", 12.25)]


def test_the_declaration_names_the_4_1_board():
    assert (refresh.TBENCH_URL, refresh.TBENCH_NAME, refresh.TBENCH_TITLE) == (
        "https://www.tbench.ai/", "4-1-0", "Terminal-Bench 4.1")


# ── (b) a different version, (c) no name ────────────────────────────────────

@pytest.mark.parametrize("board, found", [
    ({"name": "4-2-0", "title": "Terminal-Bench 4.2"}, "name '4-2-0' (title 'Terminal-Bench 4.2')"),
    ({"name": "4-1-0", "title": "Terminal-Bench 4.2"}, "name '4-1-0' (title 'Terminal-Bench 4.2')"),
    ({"title": "Terminal-Bench 4.1"}, "name None (title 'Terminal-Bench 4.1')"),
    ({"name": "4-2-0"}, "name '4-2-0' (title None)"),
])
def test_a_board_that_is_not_the_expected_version_fails(board, found):
    with pytest.raises(refresh.BoardVersionMismatch) as error:
        _project(_page(board))
    assert str(error.value) == (
        f"board_version: expected name 4-1-0 (title Terminal-Bench 4.1), found {found}")
    assert (error.value.expected, error.value.found) == (
        "name 4-1-0 (title Terminal-Bench 4.1)", found)


def test_a_payload_with_no_leaderboard_object_fails():
    with pytest.raises(refresh.BoardVersionMismatch, match="found no leaderboard object"):
        _project(_page(key="other"))


MISMATCH = "board_version"


def _data(board, rows=ROWS, **more) -> dict:
    """The page's own shape: ``leaderboard`` and ``rows`` are siblings under one object."""
    return {"leaderboard": board, "rows": rows, **more}


@pytest.mark.parametrize("payload", [
    # a 4.1 identity elsewhere, a 4.2 board with its rows: both orders
    {"a": {"leaderboard": NAMED}, "b": _data(OTHER, OTHER_ROWS)},
    {"b": _data(OTHER, OTHER_ROWS), "a": {"leaderboard": NAMED}},
    # the name on an identity with no rows of its own, rows beside another board
    {"a": {"leaderboard": NAMED}, "b": {"leaderboard": OTHER, "rows": ROWS}},
    {"a": {"leaderboard": NAMED, "rows": []}, "b": {"rows": ROWS}},
    # two identities both named 4.1
    {"a": _data(NAMED), "b": _data(NAMED)},
    {"a": {"leaderboard": NAMED}, "b": {"leaderboard": NAMED}, "rows": ROWS},
    # a second rows list anywhere
    _data(NAMED, ROWS, other={"rows": OTHER_ROWS}),
    # rows inside the identity, not beside it
    {"leaderboard": {**NAMED, "rows": ROWS}},
    # no identity, or no enclosing sibling rows
    {"rows": ROWS},
    {"leaderboard": NAMED, "x": {"rows": ROWS}},
    # wrong name, wrong title
    _data(OTHER),
    _data({"name": "4-1-0", "title": "Terminal-Bench 4.2"}),
])
def test_only_one_board_with_its_own_rows_passes(payload):
    with pytest.raises(refresh.BoardVersionMismatch):
        _project(_wrap({"state": {"data": payload}}))


def test_the_single_well_formed_board_with_sibling_rows_projects():
    body = _wrap({"state": {"data": _data(NAMED, ROWS, extra=1)}, "x": [1]})
    assert [r["model"] for r in _project(body)["rows"]] == ["Alpha One", "Beta Two"]


def test_a_second_board_named_for_another_version_files_nothing(monkeypatch, tmp_path):
    for order in (("a", "b"), ("b", "a")):
        sub = tmp_path / "-".join(order)
        root, card = _repo(sub, with_row=True)
        before = card.read_bytes()
        parts = {"a": _data(NAMED), "b": _data(OTHER, OTHER_ROWS)}
        report, _ = _run(monkeypatch, sub, root,
                         _wrap({"state": {k: {"data": parts[k]} for k in order}}))
        reasons = [f.reason for f in _on_board(report.failures)]
        assert len(reasons) == 1 and reasons[0].startswith(MISMATCH)
        assert card.read_bytes() == before
        assert report.changes == [] and not (root / "verification" / "log.jsonl").exists()


def test_the_check_runs_before_any_row_is_projected():
    bad_rows = [{"metadata": {}, "metrics": {}}]  # would raise KeyError if projected
    with pytest.raises(refresh.BoardVersionMismatch):
        _project(_page({"name": "4-2-0"}, rows=bad_rows))


# ── a repository with an invented card for the board ────────────────────────

def _repo(tmp_path: Path, *, with_row: bool, row_effort: str | None = "high",
          score: float = 40.0) -> tuple[Path, Path]:
    root = tmp_path / "repo"
    (root / "models" / "lab").mkdir(parents=True)
    (root / "registry").mkdir()
    (root / "verification").mkdir()
    (root / "premier").mkdir()
    (root / "premier" / "slice-1.yaml").write_text("models:\n- model_id: lab/alpha\n", encoding="utf-8")
    (root / "registry" / "sources.yaml").write_text(
        "schema_version: 1\nsources:\n"
        f"- id: {SOURCE_ID}\n  volatility: live\n  url: {refresh.TBENCH_URL}\n  fetch: http\n"
        "  normaliser: text-default\n  cited_regions:\n  - id: rows\n    locator:\n"
        "      kind: page\n      value: ''\n", encoding="utf-8")
    effort_line = f"effort: {row_effort}\n    " if row_effort else ""
    row = f"""  - benchmark_id: {BENCHMARK}
    model_id_as_evaluated: Alpha One
    {effort_line}score: {score}
    unit: percent
    source_url: {refresh.TBENCH_URL}
    source_kind: benchmark_author
    evidence_date: '2026-10-01'
    date_type: published
    observed_at: '2026-11-07'
    verified_at: '2026-11-07'
    id: lab/alpha#{BENCHMARK}#aaaaaaaaaaaa
    sources:
    - source_id: {SOURCE_ID}
      snapshot_ref: sha256:{'a' * 64}
      cited_regions: [rows]
"""
    other = row.replace(BENCHMARK, "other_benchmark").replace(refresh.TBENCH_URL, "https://example.test/x")
    rows = row if with_row else other
    card = root / "models" / "lab" / "alpha.md"
    card.write_text(f"---\nmodel_id: lab/alpha\nbenchmarks:\n  evidence:\n{rows}---\nprose\n",
                    encoding="utf-8")
    return root, card


def _run(monkeypatch, tmp_path, root, page: bytes):
    seen: list[str] = []

    def fetch(url: str, **_declared) -> bytes:
        seen.append(url)
        if url == refresh.TBENCH_URL:
            return page
        raise OSError(f"offline: {url}")

    monkeypatch.setattr(refresh, "_fetch", fetch)
    report = refresh.run(observed_at=OBSERVED, dry_run=False, root=root,
                         source_cache=tmp_path / "copies")
    return report, seen


def _on_board(failures):
    return [f for f in failures if f.benchmark == BENCHMARK]


def test_a_wrong_version_files_nothing_and_leaves_the_card_byte_identical(monkeypatch, tmp_path):
    root, card = _repo(tmp_path, with_row=True)
    before = card.read_bytes()
    report, _ = _run(monkeypatch, tmp_path, root, _page({"name": "4-2-0", "title": "Terminal-Bench 4.2"}))

    reasons = [f.reason for f in _on_board(report.failures)]
    assert reasons == ["board_version: expected name 4-1-0 (title Terminal-Bench 4.1), "
                       "found name '4-2-0' (title 'Terminal-Bench 4.2')"]
    assert card.read_bytes() == before
    assert "terminal-bench-4-1" not in report.boards
    assert report.changes == [] and report.reconfirmed == []
    assert not (root / "verification" / "log.jsonl").exists()
    assert reasons[0] in refresh.render_report(report)
    out = tmp_path / "report.json"
    refresh.write_report_json(out, report)
    assert {"model_id": "*", "benchmark": BENCHMARK, "source": refresh.TBENCH_URL,
            "reason": reasons[0]} in json.loads(out.read_text(encoding="utf-8"))["failures"]


def test_a_missing_name_files_nothing_and_leaves_the_card_byte_identical(monkeypatch, tmp_path):
    root, card = _repo(tmp_path, with_row=True)
    before = card.read_bytes()
    report, _ = _run(monkeypatch, tmp_path, root, _page({"title": "Terminal-Bench 4.1"}))
    assert [f.reason for f in _on_board(report.failures)] == [
        "board_version: expected name 4-1-0 (title Terminal-Bench 4.1), "
        "found name None (title 'Terminal-Bench 4.1')"]
    assert card.read_bytes() == before
    assert report.changes == [] and not (root / "verification" / "log.jsonl").exists()


def test_a_matching_board_updates_a_tracked_row(monkeypatch, tmp_path):
    root, card = _repo(tmp_path, with_row=True)
    report, _ = _run(monkeypatch, tmp_path, root, _page())
    assert not _on_board(report.failures)
    assert "terminal-bench-4-1" in report.boards
    assert refresh._front(card)["benchmarks"]["evidence"][0]["score"] == 41.5


# ── (d) the 4.0 declaration is gone ─────────────────────────────────────────

def test_the_old_address_is_never_read(monkeypatch, tmp_path):
    calls = _install(monkeypatch, {refresh.TBENCH_URL: (200, _page())})
    readings, failures = refresh.collect_readings(
        OBSERVED, CopyStore(tmp_path / "copies"), [], skip_arena=True)
    assert OLD_ADDRESS not in calls and refresh.TBENCH_URL in calls
    assert [r.key for r in readings if r.key.startswith("terminal-bench")] == ["terminal-bench-4-1"]
    assert not _on_board(failures)
    reading = next(r for r in readings if r.key == "terminal-bench-4-1")
    assert (reading.source_id, reading.source_url, reading.card_urls, reading.benchmark_ids) == (
        SOURCE_ID, refresh.TBENCH_URL, frozenset({refresh.TBENCH_URL}), frozenset({BENCHMARK}))
    assert not any("terminal_bench_v4_0" in f.benchmark or f.source == OLD_ADDRESS for f in failures)


def test_the_script_declares_no_4_0_board():
    source = (Path(refresh.__file__)).read_text(encoding="utf-8")
    assert "terminal-bench/4.0" not in source and '"terminal_bench_v4_0"' not in source


# ── (f) 4.1 declared, no 4.1 row on any card ────────────────────────────────

def test_with_no_4_1_row_on_any_card_nothing_is_filed_and_no_failure(monkeypatch, tmp_path):
    root, card = _repo(tmp_path, with_row=False)
    before = card.read_bytes()
    report, seen = _run(monkeypatch, tmp_path, root, _page())
    assert refresh.TBENCH_URL in seen
    assert not _on_board(report.failures)
    assert card.read_bytes() == before
    assert report.changes == [] and report.added == 0
    assert not (root / "verification" / "log.jsonl").exists()


# ── the update path narrows by the stored ``effort:`` key ───────────────────

TWO = [
    {"metadata": {"model_display": "Alpha One", "reasoning_effort": "high", "agent_display": "H",
                  "date": "2026-10-01"}, "metrics": {"accuracy": 41.5}},
    {"metadata": {"model_display": "Alpha One", "reasoning_effort": "low", "agent_display": "H",
                  "date": "2026-10-01"}, "metrics": {"accuracy": 20.5}},
]


def _two_page() -> bytes:
    return _wrap({"state": {"data": _data(NAMED, TWO)}})


def test_a_stored_effort_selects_exactly_that_page_row(monkeypatch, tmp_path):
    root, card = _repo(tmp_path, with_row=True, row_effort="high")
    report, _ = _run(monkeypatch, tmp_path, root, _two_page())
    assert not _on_board(report.failures)
    assert refresh._front(card)["benchmarks"]["evidence"][0]["score"] == 41.5
    assert report.boards["terminal-bench-4-1"]["values_changed"] == 1


def test_a_stored_row_with_no_effort_and_no_equal_score_is_left_alone(monkeypatch, tmp_path):
    root, card = _repo(tmp_path, with_row=True, row_effort=None, score=33.0)
    before = card.read_bytes()
    report, _ = _run(monkeypatch, tmp_path, root, _two_page())
    assert card.read_bytes() == before
    assert report.changes == [] and report.reconfirmed == []
