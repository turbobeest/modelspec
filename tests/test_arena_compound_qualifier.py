"""The verifier owns an Arena row whose display name has a compound qualifier.

One board holds the bare sibling, the high-context row, and the thinking-budget
row. Token-set equality is the whole match. A subset, a different date, or a
second row with the same tokens is refused. Names and numbers are invented.
"""

from __future__ import annotations

from pathlib import Path

from decision import verify
from scripts import refresh_leaderboards as refresh
from tests.test_leaderboard_refresh import (
    _ARENA_DATASET,
    _ARENA_NEW,
    _arena_registry,
    _arena_skip_classes,
    _evidence_row,
    _run_arena_effort_refresh,
    _verification_log,
)

_BARE = "Acme Orbit 4.5 (20251101)"
_HIGH = "Acme Orbit 4.5 (High, 32K, 20251101)"
_THINK = "Acme Orbit 4.5 (Thinking 16K, 20251101)"
_BARE_ID = "acme-orbit-4-5-20251101"
_HIGH_ID = "acme-orbit-4-5-20251101-high-32k"
_THINK_ID = "acme-orbit-4-5-20251101-thinking-16k"
_DISPLAY = "Acme Orbit 4.5"
_MODEL = "lab/acme-orbit-4-5"


def _dataset_row(name: str, rating: float, votes: int, rank: int) -> dict:
    return {
        "model_name": name,
        "rating": rating,
        "rating_lower": rating - 6,
        "rating_upper": rating + 6,
        "vote_count": votes,
        "leaderboard_publish_date": "2026-11-11",
        "rank": rank,
    }


def _board() -> list[dict]:
    return [
        _dataset_row(_BARE, 1366.0, 42962, 20),
        _dataset_row(_HIGH, 1447.0, 36239, 12),
        _dataset_row(_THINK, 1377.0, 35843, 18),
    ]


def _run(
    monkeypatch,
    tmp_path: Path,
    *,
    evaluated: str,
    dataset_rows: list[dict] | None = None,
    effort: str | None = None,
    score: float = 1000.0,
    version: str = _BARE_ID,
):
    """Refresh one invented Arena card through ``refresh.run``. No network.

    ``version`` is the bare dated slug, as a card stores it beside a longer
    ``model_id_as_evaluated``. The shared helper pins version to the evaluated
    id, so this runner is the helper with that one field free.
    """
    root = tmp_path / "repo"
    cache = tmp_path / "copies"
    source_id = "fixture-arena"
    card = root / "models" / "lab" / "model.md"
    card.parent.mkdir(parents=True)
    card.write_text(
        f"""---
model_id: {_MODEL}
display_name: {_DISPLAY}
version: {version}
benchmarks:
  evidence:
  - benchmark_id: arena_elo_overall
    model_id_as_evaluated: {evaluated}
    score: {score}
    unit: Arena score (Elo scale)
    interval: [990.0, 1010.0]
    n: 500
    effort: {"null" if effort is None else effort}
    source_url: {_ARENA_DATASET}
    source_kind: independent_evaluator
    evidence_date: '2026-10-01'
    date_type: published
    observed_at: '2026-10-01'
    verified_at: '2026-10-01'
    benchmark_version: text / overall, latest split, rating 1000
    configuration: >-
      Pinned LMArena dataset; publication date 2026-10-01; rating {score:.2f}
      [990.00, 1010.00], 500 votes, rank 40. Observed 2026-10-01.
    id: {_MODEL}#arena_elo_overall#old
    sources:
    - source_id: {source_id}
      snapshot_ref: sha256:{'a' * 64}
      cited_regions: [rows]
---
""",
        encoding="utf-8",
    )
    _arena_registry(root, source_id)
    (root / "verification").mkdir()
    url = f"{_ARENA_DATASET}/resolve/{_ARENA_NEW}/text/latest-00000-of-00001.parquet"
    store = refresh.CopyStore(cache)
    projection = refresh.readers.document(
        dataset_rows if dataset_rows is not None else _board(),
        url=url,
        page_ref="sha256:" + "b" * 64,
        read_date="2026-11-11",
        note="fixture",
    )
    board = refresh._reading_from_projection(
        key="arena:text",
        source_id=source_id,
        benchmarks=("arena_elo_overall",),
        source_url=url,
        projected=projection,
        observed_at="2026-11-11",
        value_field="rating",
        store=store,
        card_urls=(_ARENA_DATASET,),
    )
    monkeypatch.delenv(refresh.ARENA_REVISION_ENV, raising=False)
    monkeypatch.setattr(
        refresh.readers,
        "resolve_arena_revision",
        lambda _fetch: refresh.readers.ArenaRevision(sha=_ARENA_NEW),
    )
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([board], []))
    report = refresh.run(
        observed_at="2026-11-11",
        dry_run=False,
        root=root,
        source_cache=cache,
        model_ids=(_MODEL,),
        arena_latest=True,
    )
    return report, card, root


def _unchanged(card: Path, score: float = 1000.0) -> dict:
    row = _evidence_row(card)
    assert row["score"] == score
    assert str(row["observed_at"]) == "2026-10-01"
    assert "36239" not in row["configuration"]
    assert "42962" not in row["configuration"]
    assert "35843" not in row["configuration"]
    return row


def test_a_compound_parenthesis_names_high_and_keeps_every_token() -> None:
    """High in a compound qualifier is the row's effort. Thinking 16K is not."""
    identity, effort = verify.split_model_cell(_HIGH)
    assert effort == "high"
    assert identity.split() == ["acme", "orbit", "4", "5", "high", "32k", "20251101"]
    identity, effort = verify.split_model_cell(_THINK)
    assert effort is None
    assert "thinking" in identity.split()
    assert "16k" in identity.split()
    assert verify.split_model_cell("Acme Orbit 4.5 (High)") == ("acme orbit 4 5", "high")
    assert verify.split_model_cell("example-model-high") == ("example model high", None)
    assert verify.split_model_cell("model-high-32k")[1] is None
    assert verify.structured_name_effort("Acme Orbit 4.5 (High)") == "High"
    assert verify.structured_name_effort("example-model-high") is None


def test_a_compound_high_row_is_the_one_the_verifier_reads(monkeypatch, tmp_path: Path) -> None:
    """(a) The high-32k slug reads the High, 32K row, not the bare sibling."""
    report, card, root = _run(monkeypatch, tmp_path, evaluated=_HIGH_ID)

    assert report.quarantined == []
    assert report.failures == [], report.failures
    row = _evidence_row(card)
    assert row["model_id_as_evaluated"] == _HIGH_ID
    assert row["score"] == 1447.0
    assert row["n"] == 36239
    assert row["interval"] == [1441.0, 1453.0]
    assert "36239" in row["configuration"]
    assert "42962" not in row["configuration"]
    assert "35843" not in row["configuration"]
    assert _verification_log(root)["outcome"] == "verified"


def test_a_stated_high_effort_matches_the_compound_row(monkeypatch, tmp_path: Path) -> None:
    report, card, root = _run(monkeypatch, tmp_path, evaluated=_HIGH_ID, effort="high")

    assert report.failures == [], report.failures
    row = _evidence_row(card)
    assert row["score"] == 1447.0
    assert row["effort"] == "high"
    assert row["n"] == 36239
    assert _verification_log(root)["outcome"] == "verified"


def test_a_stated_other_effort_does_not_read_the_compound_row(
    monkeypatch, tmp_path: Path,
) -> None:
    report, card, _root = _run(monkeypatch, tmp_path, evaluated=_HIGH_ID, effort="max")

    assert report.quarantined == []
    assert any("effort" in row.reason for row in report.failures)
    row = _unchanged(card)
    assert row["effort"] == "max"


def test_the_bare_sibling_stays_the_bare_stored_name(monkeypatch, tmp_path: Path) -> None:
    """(b) The bare slug reads the bare row, as on main."""
    report, card, root = _run(monkeypatch, tmp_path, evaluated=_BARE_ID, version=_BARE_ID)

    assert report.failures == [], report.failures
    row = _evidence_row(card)
    assert row["model_id_as_evaluated"] == _BARE_ID
    assert row["score"] == 1366.0
    assert row["n"] == 42962
    assert "42962" in row["configuration"]
    assert "36239" not in row["configuration"]
    assert "35843" not in row["configuration"]
    assert _verification_log(root)["outcome"] == "verified"


def test_a_thinking_budget_row_is_not_the_bare_sibling(monkeypatch, tmp_path: Path) -> None:
    """(c) Thinking 16K stays identity. The slug reads that row's numbers."""
    report, card, root = _run(monkeypatch, tmp_path, evaluated=_THINK_ID)

    assert report.failures == [], report.failures
    row = _evidence_row(card)
    assert row["model_id_as_evaluated"] == _THINK_ID
    assert row["score"] == 1377.0
    assert row["n"] == 35843
    assert row["effort"] is None
    assert "35843" in row["configuration"]
    assert "36239" not in row["configuration"]
    assert "42962" not in row["configuration"]
    assert _verification_log(root)["outcome"] == "verified"


def test_a_different_thinking_budget_is_refused(monkeypatch, tmp_path: Path) -> None:
    """(d) A 32K thinking slug does not read the 16K row."""
    report, card, _root = _run(
        monkeypatch, tmp_path, evaluated="acme-orbit-4-5-20251101-thinking-32k",
    )

    assert report.quarantined == []
    assert any("no unique row" in row.reason for row in report.failures)
    assert _arena_skip_classes(report) == {"no-unique-row": 1}
    row = _unchanged(card)
    assert row["model_id_as_evaluated"] == "acme-orbit-4-5-20251101-thinking-32k"


def test_a_high_name_without_the_context_size_is_refused(monkeypatch, tmp_path: Path) -> None:
    """(e) The slug without 32k does not read the (High, 32K) row."""
    report, card, _root = _run(
        monkeypatch, tmp_path, evaluated="acme-orbit-4-5-20251101-high",
    )

    assert any("no unique row" in row.reason for row in report.failures)
    assert _arena_skip_classes(report) == {"no-unique-row": 1}
    _unchanged(card)


def test_a_different_parenthesis_date_is_refused(monkeypatch, tmp_path: Path) -> None:
    """(f) A different date in the parenthesis is not the stored row."""
    rows = [
        _dataset_row(_BARE, 1366.0, 42962, 20),
        _dataset_row("Acme Orbit 4.5 (High, 32K, 20250929)", 1447.0, 36239, 12),
        _dataset_row(_THINK, 1377.0, 35843, 18),
    ]
    report, card, _root = _run(monkeypatch, tmp_path, evaluated=_HIGH_ID, dataset_rows=rows)

    assert any("no unique row" in row.reason for row in report.failures)
    assert _arena_skip_classes(report) == {"no-unique-row": 1}
    _unchanged(card)


def test_two_rows_with_one_token_set_are_refused(monkeypatch, tmp_path: Path) -> None:
    """(g) Two rows with the stored token set are refused, even when one score agrees."""
    rows = [
        _dataset_row(_BARE, 1366.0, 42962, 20),
        _dataset_row(_HIGH, 1447.0, 36239, 12),
        _dataset_row("Acme Orbit 4.5 (20251101, High, 32K)", 1511.0, 37001, 11),
    ]
    report, card, _root = _run(
        monkeypatch, tmp_path, evaluated=_HIGH_ID, dataset_rows=rows, score=1447.0,
    )

    assert report.quarantined == []
    assert report.failures, "a duplicated token set was written"
    row = _evidence_row(card)
    assert row["score"] == 1447.0
    assert row["n"] == 500
    assert str(row["observed_at"]) == "2026-10-01"
    assert "37001" not in row["configuration"]
    assert "36239" not in row["configuration"]


def test_a_reordered_name_without_a_compound_qualifier_is_still_not_owned(
    monkeypatch, tmp_path: Path,
) -> None:
    """Token order alone is not ownership. That case stays the one on main."""
    report, card, _root = _run_arena_effort_refresh(
        monkeypatch,
        tmp_path,
        dataset_name="unused",
        evaluated="Beta Alpha",
        display="Alpha",
        dataset_rows=[
            {
                "model_name": "Alpha Beta",
                "rating": 1300.0,
                "rating_lower": 1290.0,
                "rating_upper": 1310.0,
                "vote_count": 3333,
                "leaderboard_publish_date": "2026-11-02",
                "rank": 1,
            },
            {
                "model_name": "Alpha",
                "rating": 1210.25,
                "rating_lower": 1190.5,
                "rating_upper": 1230.75,
                "vote_count": 2222,
                "leaderboard_publish_date": "2026-11-02",
                "rank": 3,
            },
        ],
    )

    assert any("verifier" in row.reason for row in report.failures)
    assert _evidence_row(card)["score"] == 1100.0


def test_a_single_effort_parenthesis_still_adopts_high(monkeypatch, tmp_path: Path) -> None:
    report, card, root = _run_arena_effort_refresh(
        monkeypatch,
        tmp_path,
        dataset_name="Example Model (High)",
        evaluated="example-model-high",
        display="Example Model",
    )

    assert report.failures == [], report.failures
    row = _evidence_row(card)
    assert row["score"] == 1210.25
    assert row["effort"] == "high"
    assert _verification_log(root)["outcome"] == "verified"
