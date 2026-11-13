"""A live board that still lists a row but no longer prints its value (MODEL-482)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from decision.model import Evidence, evidence_verification_value, value_hash
from schema.evidence import BenchmarkEvidence
from scripts.model_143_evidence import evidence_id
from scripts import refresh_leaderboards as refresh

SOURCE_URL = "https://example.test/leaderboard.json"
OBSERVED = "2026-11-13"
LAST_SEEN = "2026-10-12"
SOURCES_YAML = """schema_version: 1
sources:
- id: fixture-source
  url: https://example.test/leaderboard.json
  fetch: http
  normaliser: text-default
  cited_regions:
  - id: rows
    locator: {kind: page, value: ''}
"""


def stored(name: str = "Orbit 9", score: float = 61.5, **extra: object) -> dict:
    row = {
        "benchmark_id": "fixture_benchmark",
        "model_id_as_evaluated": name,
        "score": score,
        "unit": "percent",
        "source_url": SOURCE_URL,
        "source_kind": "benchmark_author",
        "evidence_date": "2026-09-01",
        "date_type": "evaluated",
        "observed_at": LAST_SEEN,
        "verified_at": LAST_SEEN,
        "effort": "high",
        "quality_flags": ["contamination_warning"],
        "id": "lab/orbit#old",
        "sources": [{
            "source_id": "fixture-source",
            "snapshot_ref": "sha256:" + "a" * 64,
            "cited_regions": ["rows"],
        }],
    }
    row.update(extra)
    return row


def board_of(
    rows: list[dict], *, key: str = "fixture", observed_at: str = OBSERVED, declared: bool = True,
):
    return refresh.json_board(
        key=key,
        source_id="fixture-source",
        benchmark_ids={"fixture_benchmark"},
        source_url=SOURCE_URL,
        body=json.dumps({"rows": rows}).encode(),
        observed_at=observed_at,
        value_field="score",
        explicit_empty_cells=declared,
    )


#: The refusal texts MODEL-482-C gives each case that used to read "no unique row".
UNDECLARED = (
    "empty cell for 'Orbit 9' on a board that does not declare empty cells; not marked"
)
FEW_SCORED = "empty cell for 'Orbit 9' with fewer than 3 other rows scored; not marked"
SINGLE_TRACKED = "empty cell for 'Orbit 9' on a board with a single tracked row; not marked"


def missing_tracked(card: str, name: str = "Orbit 9") -> str:
    return (
        f"empty cell for {name!r} while the tracked row of {card} "
        "(fixture_benchmark) is missing from the read; not marked"
    )


#: Three scored neighbours: the least a read may show before an empty cell counts.
SCORED = [{"model": f"Rival {n}", "score": 70 + n} for n in (1, 2, 3)]
SCORED_PCT = [{"model": f"Rival {n}", "score": f"{70 + n}%"} for n in (1, 2, 3)]


def plan(
    rows: list[dict],
    evidence_rows: list[dict] | None = None,
    *,
    key: str = "fixture",
    declared: bool = True,
    tracked_extra: tuple[str, ...] = ("Rival 1",),
):
    """Plan one card's rows. The board also tracks the rows named in ``tracked_extra``."""
    own = evidence_rows or [stored()]
    tracked = [("lab/orbit", row) for row in own] + [
        (f"lab/{name.lower().replace(' ', '-')}", stored(name)) for name in tracked_extra
    ]
    return refresh._plan_observations(
        "lab/orbit",
        "models/lab/orbit.md",
        own,
        board_of(rows, key=key, declared=declared),
        tracked=tracked,
    )


def card_text(
    *,
    score: str = "61.5",
    marked: str | None = None,
    name: str = "Orbit 9",
    effort: bool = True,
    flags: bool = True,
    extra: tuple[str, ...] = (),
) -> str:
    mark = f"    not_published_since: '{marked}'\n" if marked is not None else ""
    more = "".join(
        f"""  - benchmark_id: fixture_benchmark
    model_id_as_evaluated: {other}
    score: 55.0
    unit: percent
    source_url: {SOURCE_URL}
    source_kind: benchmark_author
    evidence_date: '2026-09-01'
    date_type: evaluated
    observed_at: '{LAST_SEEN}'
    verified_at: '{LAST_SEEN}'
{mark}    id: lab/orbit#fixture_benchmark#extra{n}
    sources:
    - source_id: fixture-source
      snapshot_ref: sha256:{"a" * 64}
      cited_regions: [rows]
"""
        for n, other in enumerate(extra)
    )
    effort_line = "    effort: high\n" if effort else ""
    flag_line = "    quality_flags:\n    - contamination_warning\n" if flags else ""
    return f"""---
model_id: lab/orbit
display_name: {name}
version: {name}
benchmarks:
  evidence:
  - benchmark_id: fixture_benchmark
    model_id_as_evaluated: {name}
    score: {score}
    unit: percent
    source_url: {SOURCE_URL}
    source_kind: benchmark_author
    evidence_date: '2026-09-01'
    date_type: evaluated
    observed_at: '{LAST_SEEN}'
    verified_at: '{LAST_SEEN}'
{effort_line}{flag_line}{mark}    id: lab/orbit#fixture_benchmark#old
    sources:
    - source_id: fixture-source
      snapshot_ref: sha256:{"a" * 64}
      cited_regions: [rows]
{more}---
prose stays
"""


def setup_repo(tmp_path: Path, text: str) -> tuple[Path, Path, Path]:
    root = tmp_path / "repo"
    cache = tmp_path / "copies"
    (root / "models" / "lab").mkdir(parents=True)
    (root / "registry").mkdir()
    (root / "verification").mkdir()
    (root / "registry" / "sources.yaml").write_text(SOURCES_YAML, encoding="utf-8")
    card = root / "models" / "lab" / "orbit.md"
    card.write_text(text, encoding="utf-8")
    return root, cache, card


def run_boards(
    monkeypatch, root: Path, cache: Path, rows: list[dict], *,
    failed: str | None = None, declared: bool = True,
):
    monkeypatch.setenv("MODELSPEC_ARENA_REVISION", "pinned")
    if failed is None:
        store = refresh.CopyStore(cache)
        projection = refresh.readers.document(
            rows,
            url=SOURCE_URL,
            page_ref="sha256:" + "b" * 64,
            read_date=OBSERVED,
            note="fixture",
        )
        board = refresh._reading_from_projection(
            key="matharena" if declared else "fixture",
            source_id="fixture-source",
            benchmarks=("fixture_benchmark",),
            source_url=SOURCE_URL,
            projected=projection,
            observed_at=OBSERVED,
            value_field="score",
            store=store,
            card_urls=(SOURCE_URL,),
        )
        monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([board], []))
    else:
        monkeypatch.setattr(
            refresh,
            "collect_readings",
            lambda *_args, **_kwargs: ([], [
                refresh.RowFailure("*", "fixture_benchmark", SOURCE_URL, failed),
            ]),
        )
    return refresh.run(
        observed_at=OBSERVED,
        dry_run=False,
        root=root,
        source_cache=cache,
        model_ids=("lab/orbit",),
    )


def front_row(card: Path) -> dict:
    front = yaml.safe_load(card.read_text(encoding="utf-8").split("---", 2)[1])
    return front["benchmarks"]["evidence"][0]


def test_not_published_since_is_optional_and_outside_the_identity() -> None:
    base = {
        "benchmark_id": "fixture_benchmark",
        "model_id_as_evaluated": "Orbit 9",
        "score": 61.5,
        "unit": "percent",
        "source_url": SOURCE_URL,
        "source_kind": "benchmark_author",
        "evidence_date": "2026-09-01",
        "date_type": "evaluated",
        "verified_at": "2026-09-24",
        "quality_flags": ["contamination_warning"],
    }
    plain = BenchmarkEvidence.model_validate(base)
    marked = BenchmarkEvidence.model_validate({**base, "not_published_since": OBSERVED})
    flagged = Evidence.model_validate({**base, "not_published_since": OBSERVED})

    assert plain.not_published_since is None
    assert marked.not_published_since == OBSERVED
    assert flagged.not_published_since == OBSERVED
    assert "not_published_since" not in plain.model_dump()
    assert plain.model_dump()["interval"] is None
    assert plain.model_dump()["n"] is None
    assert marked.model_dump()["not_published_since"] == OBSERVED
    with pytest.raises(ValidationError):
        BenchmarkEvidence.model_validate({**base, "not_published_since": "2026-11"})
    with pytest.raises(ValidationError):
        BenchmarkEvidence.model_validate({**base, "not_published_since": ""})

    bare = dict(base)
    carrying = {**base, "not_published_since": OBSERVED}
    assert evidence_id("lab/orbit", bare) == evidence_id("lab/orbit", carrying)
    assert value_hash(evidence_verification_value(bare)) == value_hash(
        evidence_verification_value(carrying)
    )
    assert value_hash(evidence_verification_value(plain)) == value_hash(
        evidence_verification_value(marked)
    )


def test_not_published_since_marks_one_empty_cell_when_another_row_is_scored() -> None:
    """(a) The row is present, its cell is empty, and another row has a number."""
    original = stored()
    untouched = stored()
    observations, failures, marks = plan(
        [{"model": "Orbit 9", "score": None}, *SCORED],
        [original],
    )

    assert original == untouched
    assert observations == []
    assert failures == []
    assert [(mark.kind, mark.day, mark.last_seen, mark.benchmark, mark.card) for mark in marks] == [
        ("newly_marked", OBSERVED, LAST_SEEN, "fixture_benchmark", "models/lab/orbit.md"),
    ]


def test_not_published_since_last_seen_falls_back_to_the_evidence_date() -> None:
    row = stored()
    del row["observed_at"]

    _observations, failures, marks = plan(
        [{"model": "Orbit 9", "score": None}, *SCORED],
        [row],
    )

    assert failures == []
    assert marks[0].kind == "newly_marked"
    assert marks[0].last_seen == "2026-09-01"


def test_not_published_since_does_not_mark_a_board_with_no_numeric_value() -> None:
    """(b) Every cell is empty, including a board that is only this row."""
    for rows in (
        [{"model": "Orbit 9"}],
        [{"model": "Orbit 9"}, {"model": "Harbor 2"}],
    ):
        observations, failures, marks = plan(rows)
        assert observations == []
        assert marks == []
        assert [failure.reason for failure in failures] == ["no unique row for 'Orbit 9'"]


def test_not_published_since_does_not_mark_a_missing_row() -> None:
    """(c) The stored name is not on the parsed board."""
    observations, failures, marks = plan([{"model": "Harbor 2", "score": 70}])

    assert observations == []
    assert marks == []
    assert [failure.reason for failure in failures] == ["no unique row for 'Orbit 9'"]


def test_not_published_since_does_not_mark_two_rows_of_the_stored_name(monkeypatch, tmp_path: Path) -> None:
    """(g) Two rows match the stored name and one cell is empty."""
    rows = [
        {"model": "Orbit 9"},
        {"model": "Orbit 9", "score": 61.5},
        {"model": "Harbor 2", "score": 70},
    ]
    observations, failures, marks = plan(rows)

    assert observations == []
    assert marks == []
    assert [failure.reason for failure in failures] == ["no unique row for 'Orbit 9'"]

    root, cache, card = setup_repo(tmp_path, card_text())
    before = card.read_bytes()
    report = run_boards(monkeypatch, root, cache, rows)

    assert card.read_bytes() == before
    assert report.not_published == []
    assert report.changes == []
    assert [failure.reason for failure in report.failures] == ["no unique row for 'Orbit 9'"]


def test_not_published_since_keeps_score_disambiguation_when_every_match_has_a_value() -> None:
    observations, failures, marks = plan([
        {"model": "Orbit 9", "score": 10},
        {"model": "Orbit 9", "score": 61.5},
    ])

    assert failures == []
    assert marks == []
    assert len(observations) == 1
    assert observations[0].new_value == 61.5


def test_not_published_since_arena_path_never_sets_the_key() -> None:
    observations, failures, marks = plan(
        [{"model": "Orbit 9", "score": None}, *SCORED],
        key="arena:text",
    )

    assert observations == []
    assert marks == []
    assert [failure.reason for failure in failures] == ["no unique row for 'Orbit 9'"]


def test_not_published_since_writes_only_the_key(monkeypatch, tmp_path: Path) -> None:
    """(a) A sound read writes the observation day and leaves the reading alone."""
    root, cache, card = setup_repo(tmp_path, card_text(extra=("Quill 3",)))
    before = card.read_text(encoding="utf-8").splitlines()
    before_row = front_row(card)

    report = run_boards(
        monkeypatch, root, cache,
        [{"model": "Orbit 9", "score": None}, {"model": "Quill 3", "score": None}, *SCORED_PCT],
    )

    after = card.read_text(encoding="utf-8").splitlines()
    added = [line for line in after if line not in before]
    removed = [line for line in before if line not in after]
    row = front_row(card)
    # Both tracked rows are empty on the board, so both are marked, one line each.
    assert added == [f"    not_published_since: '{OBSERVED}'"] * 2
    assert removed == []
    assert isinstance(row["not_published_since"], str)
    assert row["not_published_since"] == OBSERVED
    for field in (
        "score", "observed_at", "evidence_date", "date_type", "effort",
        "model_id_as_evaluated", "quality_flags", "verified_at", "sources", "id",
    ):
        assert row[field] == before_row[field]
    assert "prose stays" in card.read_text(encoding="utf-8")
    assert report.changes == []
    assert report.reconfirmed == []
    assert report.failures == []
    assert [(mark.kind, mark.last_seen) for mark in report.not_published] == [
        ("newly_marked", LAST_SEEN),
    ] * 2
    text = refresh.render_report(report)
    assert "## No longer published" in text
    assert "2 newly marked, 0 still marked, 0 unmarked this run." in text
    assert "models/lab/orbit.md" in text
    assert "fixture_benchmark" in text
    assert LAST_SEEN in text
    assert "## Failures" not in text
    assert "no unique row" not in text


def test_not_published_since_empty_board_and_missing_row_write_nothing(
    monkeypatch, tmp_path: Path,
) -> None:
    """(b) and (c) through the writer, not only the planner."""
    root, cache, card = setup_repo(tmp_path, card_text())
    before = card.read_bytes()

    empty = run_boards(monkeypatch, root, cache, [{"model": "Orbit 9"}, {"model": "Harbor 2"}])
    assert card.read_bytes() == before
    assert empty.not_published == []
    # Every cell is empty: the page's rows have no number, so fewer than 3 are scored.
    assert [failure.reason for failure in empty.failures] == [FEW_SCORED]

    missing = run_boards(monkeypatch, root, cache, [{"model": "Harbor 2", "score": "70%"}])
    assert card.read_bytes() == before
    assert missing.not_published == []
    assert [failure.reason for failure in missing.failures] == ["no unique row for 'Orbit 9'"]


def test_not_published_since_fetch_failure_marks_nothing(monkeypatch, tmp_path: Path) -> None:
    """(d) A failed read, including a projector that never built a board, marks nothing."""
    root, cache, card = setup_repo(tmp_path, card_text())
    before = card.read_bytes()

    report = run_boards(monkeypatch, root, cache, [], failed="OSError: timed out")

    assert card.read_bytes() == before
    assert report.not_published == []
    assert [failure.reason for failure in report.failures] == ["OSError: timed out"]


def test_not_published_since_value_returning_removes_the_key(monkeypatch, tmp_path: Path) -> None:
    """(e) A later read with a value writes the reading and drops the key."""
    root, cache, card = setup_repo(
        tmp_path, card_text(marked="2026-10-01", effort=False, flags=False),
    )

    report = run_boards(
        monkeypatch, root, cache,
        [{"model": "Orbit 9", "score": "70%"}, {"model": "Harbor 2", "score": "40%"}],
    )

    row = front_row(card)
    text = card.read_text(encoding="utf-8")
    assert "not_published_since" not in row
    assert "not_published_since" not in text
    assert row["score"] == 70
    assert str(row["observed_at"])[:10] == OBSERVED
    assert str(row["evidence_date"])[:10] == OBSERVED
    assert str(row["verified_at"])[:10] == OBSERVED
    assert row["date_type"] == "evaluated"
    assert "effort" not in row
    assert row["model_id_as_evaluated"] == "Orbit 9"
    assert "quality_flags" not in row
    assert "prose stays" in text
    assert report.quarantined == []
    assert len(report.changes) == 1
    assert [(mark.kind, mark.last_seen, mark.benchmark, mark.card) for mark in report.not_published] == [
        ("unmarked", LAST_SEEN, "fixture_benchmark", "models/lab/orbit.md"),
    ]
    rendered = refresh.render_report(report)
    failure_at = rendered.find("## Failures")
    published = rendered if failure_at < 0 else rendered[:failure_at]
    assert "unmarked this run" in published
    assert "models/lab/orbit.md" in published


def test_not_published_since_later_empty_read_keeps_the_stored_day(
    monkeypatch, tmp_path: Path,
) -> None:
    """(f) The cell is still empty, so the stored day does not move and nothing is written."""
    root, cache, card = setup_repo(
        tmp_path, card_text(marked="2026-10-01", extra=("Quill 3",)),
    )
    before = card.read_bytes()

    report = run_boards(
        monkeypatch, root, cache,
        [{"model": "Orbit 9", "score": None}, {"model": "Quill 3", "score": None}, *SCORED_PCT],
    )

    assert card.read_bytes() == before
    assert front_row(card)["not_published_since"] == "2026-10-01"
    assert report.changes == []
    assert report.reconfirmed == []
    assert report.failures == []
    assert [(mark.kind, mark.day, mark.last_seen) for mark in report.not_published] == [
        ("still_marked", "2026-10-01", LAST_SEEN),
    ] * 2


def test_not_published_since_report_names_cards_outside_failures(tmp_path: Path) -> None:
    report = refresh.RefreshReport(
        not_published=[
            refresh.PublicationMark(
                "newly_marked", "models/lab/orbit.md", "lab/orbit", "fixture_benchmark",
                "Orbit 9", SOURCE_URL, 61.5, LAST_SEEN, OBSERVED,
            ),
            refresh.PublicationMark(
                "still_marked", "models/lab/harbor.md", "lab/harbor", "other_benchmark",
                "Harbor 2", SOURCE_URL, 40.0, "2026-09-02", "2026-09-02",
            ),
            refresh.PublicationMark(
                "unmarked", "models/lab/quill.md", "lab/quill", "third_benchmark",
                "Quill 1", SOURCE_URL, 12.0, "2026-08-08", "",
            ),
        ],
        failures=[refresh.RowFailure("lab/other", "missing_benchmark", SOURCE_URL, "no unique row")],
    )
    text = refresh.render_report(report)
    published, failures = text.split("## Failures", 1)

    assert "1 newly marked, 1 still marked, 1 unmarked this run." in published
    assert "| Card | Benchmark | Last seen | |" in published
    assert "models/lab/orbit.md" in published
    assert "`fixture_benchmark`" in published
    assert "newly marked" in published
    assert "still marked" in published
    assert "unmarked this run" in published
    assert "models/lab/orbit.md" not in failures
    assert "fixture_benchmark" not in failures
    assert "lab/other" in failures

    path = tmp_path / "report.json"
    refresh.write_report_json(path, report)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["not_published_since"] == {
        "newly_marked": [{
            "card": "models/lab/orbit.md",
            "benchmark": "fixture_benchmark",
            "last_seen": LAST_SEEN,
        }],
        "still_marked": [{
            "card": "models/lab/harbor.md",
            "benchmark": "other_benchmark",
            "last_seen": "2026-09-02",
        }],
        "unmarked": [{
            "card": "models/lab/quill.md",
            "benchmark": "third_benchmark",
            "last_seen": "2026-08-08",
        }],
    }
    assert set(payload["not_published_since"]["newly_marked"][0]) == {
        "card", "benchmark", "last_seen",
    }


def test_not_published_since_report_key_is_present_when_nothing_was_marked(tmp_path: Path) -> None:
    path = tmp_path / "report.json"
    refresh.write_report_json(path, refresh.RefreshReport())
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["not_published_since"] == {
        "newly_marked": [],
        "still_marked": [],
        "unmarked": [],
    }
    assert "## No longer published" not in refresh.render_report(refresh.RefreshReport())


def _guard_card(score: str = "61.5", *, marked: str | None = None, evaluated: str = "Orbit 9") -> str:
    mark = f"    not_published_since: '{marked}'\n" if marked else ""
    return f"""---
model_id: lab/orbit
benchmarks:
  evidence:
  - benchmark_id: fixture_benchmark
    model_id_as_evaluated: {evaluated}
    score: {score}
    unit: percent
    source_url: {SOURCE_URL}
    source_kind: benchmark_author
    evidence_date: '2026-09-01'
    date_type: evaluated
    observed_at: '{LAST_SEEN}'
    verified_at: '{LAST_SEEN}'
{mark}    id: lab/orbit#old
---
prose
"""


def _guard_trees(tmp_path: Path, before: str, after: str) -> tuple[Path, Path]:
    old, new = tmp_path / "before", tmp_path / "after"
    for root, text in ((old, before), (new, after)):
        path = root / "models" / "lab" / "orbit.md"
        path.parent.mkdir(parents=True)
        path.write_text(text, encoding="utf-8")
    return old, new


def test_not_published_since_key_alone_is_its_own_guard_class(tmp_path: Path) -> None:
    added = _guard_trees(tmp_path / "add", _guard_card(), _guard_card(marked=OBSERVED))
    removed = _guard_trees(tmp_path / "drop", _guard_card(marked=OBSERVED), _guard_card())

    for before, after in (added, removed):
        result = refresh.check_score_only(before, after)
        assert result.ok
        assert result.errors == ()
        assert result.classes == {"not_published_since": 1}


def test_not_published_since_with_another_field_is_not_that_class(tmp_path: Path) -> None:
    allowed = _guard_trees(
        tmp_path / "score", _guard_card(), _guard_card(score="70.0", marked=OBSERVED),
    )
    refused = _guard_trees(
        tmp_path / "name",
        _guard_card(),
        _guard_card(marked=OBSERVED, evaluated="Harbor 2"),
    )

    score = refresh.check_score_only(*allowed)
    assert score.ok
    assert score.classes == {}

    name = refresh.check_score_only(*refused)
    assert not name.ok
    assert name.errors == ("non-score card data changed: models/lab/orbit.md",)
    assert name.classes == {}


def test_not_published_since_is_not_named_in_the_workflow_log() -> None:
    text = (
        Path(__file__).parents[1] / ".github" / "private-writers" / "leaderboard-refresh.yml"
    ).read_text(encoding="utf-8")

    assert "not_published_since" not in text
    assert "len(report['changes']) + len(report['reconfirmed'])" in text


def test_missing_value_key_marks_nothing() -> None:
    """A row whose value key is absent is a re-shaped read, not an empty cell."""
    observations, failures, marks = plan([{"model": "Orbit 9"}, *SCORED])

    assert observations == []
    assert marks == []
    assert [failure.reason for failure in failures] == ["no unique row for 'Orbit 9'"]


def test_only_declared_boards_can_mark() -> None:
    """An undeclared board (a METR-shaped one) never marks, even with an explicit None."""
    for row in ({"model": "Orbit 9"}, {"model": "Orbit 9", "score": None}):
        observations, failures, marks = plan([row, *SCORED], declared=False)

        assert observations == []
        assert marks == []
        assert [failure.reason for failure in failures] == [UNDECLARED]


def test_matharena_boards_are_the_only_declared_boards() -> None:
    assert refresh.UNPUBLISHED_CELL_BOARDS == {
        "matharena", "matharena:brokenarxiv", "matharena:arxivmath",
    }


def test_one_scored_neighbour_is_not_enough() -> None:
    _observations, failures, marks = plan(
        [{"model": "Orbit 9", "score": None}, SCORED[0]],
    )

    assert marks == []
    assert [failure.reason for failure in failures] == [FEW_SCORED]


def test_mostly_empty_board_marks_nothing() -> None:
    """MODEL-482-C: a mostly empty board is the normal state, not a reason to refuse.

    The half rule is gone: 3 scored of 10 other rows marks, as do 5, 6 and 10.
    Only fewer than three scored rows refuse."""
    def board(scored: int, others: int = 10) -> list[dict]:
        return [
            {"model": "Orbit 9", "score": None},
            *({"model": f"Rival {n}", "score": 70 + n} for n in range(scored)),
            *({"model": f"Quiet {n}", "score": None} for n in range(others - scored)),
        ]

    _o, failures, marks = plan(board(3))
    assert failures == []
    assert [mark.kind for mark in marks] == ["newly_marked"]

    _o, failures, marks = plan(board(6))
    assert failures == []
    assert [mark.kind for mark in marks] == ["newly_marked"]

    _o, failures, marks = plan(board(10))
    assert failures == []
    assert [mark.kind for mark in marks] == ["newly_marked"]

    # Exactly half of the other rows scored.
    _o, failures, marks = plan(board(5))
    assert failures == []
    assert [mark.kind for mark in marks] == ["newly_marked"]

    # Fewer than three scored rows, though they are every other row.
    _o, failures, marks = plan(board(2, others=2))
    assert marks == []
    assert [failure.reason for failure in failures] == [FEW_SCORED]


def test_matharena_predicted_cell_is_treated_like_an_empty_one(tmp_path: Path) -> None:
    """The projector drops None, and a site estimate has no measured value either."""
    def cell(rank: int, name: str, accuracy: str, predicted: str = "no") -> str:
        return (
            f'<tr><td>{rank}</td><td class="model-name"><a>{name}</a></td><td>Lab</td>'
            f'<td data-predicted="{predicted}">{accuracy}</td></tr>'
        )

    def reading(rows: str):
        table = (
            "<table><thead><tr><th>Rank</th><th>Model Name</th><th>Provider</th>"
            "<th>Accuracy (± 95% CI)</th></tr></thead><tbody>" + rows + "</tbody></table>"
        )
        body = refresh.readers.project_matharena(
            json.dumps({"table": table}).encode(),
            url=SOURCE_URL, page_ref="sha256:" + "b" * 64, read_date=OBSERVED,
        )
        return refresh._reading_from_projection(
            key="matharena", source_id="fixture-source", benchmarks=("fixture_benchmark",),
            source_url=SOURCE_URL, projected=body, observed_at=OBSERVED, value_field="accuracy",
            store=refresh.CopyStore(tmp_path / "copies"), card_urls=(SOURCE_URL,),
        )

    neighbours = "".join(cell(n + 2, f"Rival {n}", f"{70 + n}% ± 4.00%") for n in (1, 2, 3))
    stored_row = [stored()]
    tracked = [("lab/orbit", stored_row[0]), ("lab/rival-1", stored("Rival 1"))]
    for empty in (cell(1, "Orbit 9", "N/A"), cell(1, "Orbit 9", "42.00% ± 5.00%", "yes")):
        observations, failures, marks = refresh._plan_observations(
            "lab/orbit", "models/lab/orbit.md", stored_row, reading(empty + neighbours),
            tracked=tracked,
        )
        assert observations == []
        assert failures == []
        assert [(mark.kind, mark.score) for mark in marks] == [("newly_marked", 61.5)]

    # A measured cell on the same row is a reading, not a mark.
    observations, failures, marks = refresh._plan_observations(
        "lab/orbit", "models/lab/orbit.md", stored_row,
        reading(cell(1, "Orbit 9", "62.00% ± 5.00%") + neighbours),
        tracked=tracked,
    )
    assert marks == [] and failures == []
    assert [o.new_value for o in observations] == [62.0]

    # An undeclared key never gets the empty value key back.
    projected = json.dumps({"rows": [{"model": "Orbit 9"}]}).encode()
    undeclared = refresh._reading_from_projection(
        key="metr:fixture", source_id="fixture-source", benchmarks=("fixture_benchmark",),
        source_url=SOURCE_URL, projected=projected, observed_at=OBSERVED,
        value_field="accuracy", store=refresh.CopyStore(tmp_path / "copies"),
    )
    assert undeclared.explicit_empty_cells is False
    assert "accuracy" not in undeclared.rows[0]


def test_guard_refuses_a_changed_mark_date(tmp_path: Path) -> None:
    changed = _guard_trees(
        tmp_path / "date", _guard_card(marked="2026-11-01"), _guard_card(marked=OBSERVED),
    )
    with_score = _guard_trees(
        tmp_path / "both",
        _guard_card(marked="2026-11-01"),
        _guard_card(score="70.0", marked=OBSERVED),
    )

    for trees in (changed, with_score):
        result = refresh.check_score_only(*trees)
        assert not result.ok
        assert result.errors == ("non-score card data changed: models/lab/orbit.md",)
        assert result.classes == {}


# --- MODEL-482-C: the mark floor tests that the read is complete, not that the board is full ---

#: Tracked on the real-shape board: one scored, seven empty. Invented names.
TRACKED_EMPTY = ("Orbit 9", "Orbit 8", "Harbor 2", "Harbor 3", "Quill 1", "Quill 2", "Vale 4")
TRACKED_SCORED = "Vale 5"


def real_shape_rows() -> list[tuple[str, float | None]]:
    """24 rows, 8 with a number, 16 empty: the state of a real MathArena board.

    Eight rows are tracked by the card (seven empty, ``Vale 5`` scored)."""
    rows: list[tuple[str, float | None]] = [(name, None) for name in TRACKED_EMPTY]
    rows.append((TRACKED_SCORED, 55.0))
    rows += [(f"Rival {n}", 70.0 + n) for n in range(1, 8)]
    rows += [(f"Idle {n}", None) for n in range(1, 10)]
    assert len(rows) == 24 and sum(1 for _n, v in rows if v is not None) == 8
    return rows


def matharena_table(rows: list[tuple[str, float | None]]) -> bytes:
    def cell(rank: int, name: str, accuracy: float | None) -> str:
        shown = "N/A" if accuracy is None else f"{accuracy:.2f}% ± 1.00%"
        return (
            f'<tr><td>{rank}</td><td class="model-name"><a>{name}</a></td><td>Lab</td>'
            f'<td data-predicted="no">{shown}</td></tr>'
        )

    table = (
        "<table><thead><tr><th>Rank</th><th>Model Name</th><th>Provider</th>"
        "<th>Accuracy (± 95% CI)</th></tr></thead><tbody>"
        + "".join(cell(n + 1, name, value) for n, (name, value) in enumerate(rows))
        + "</tbody></table>"
    )
    return refresh.readers.project_matharena(
        json.dumps({"table": table}).encode(),
        url=SOURCE_URL, page_ref="sha256:" + "b" * 64, read_date=OBSERVED,
    )


def run_matharena(monkeypatch, root: Path, cache: Path, rows: list[tuple[str, float | None]]):
    """The real ``run()`` over a MathArena-shaped read: the page's table, projected."""
    monkeypatch.setenv("MODELSPEC_ARENA_REVISION", "pinned")
    board = refresh._reading_from_projection(
        key="matharena", source_id="fixture-source", benchmarks=("fixture_benchmark",),
        source_url=SOURCE_URL, projected=matharena_table(rows), observed_at=OBSERVED,
        value_field="accuracy", store=refresh.CopyStore(cache), card_urls=(SOURCE_URL,),
    )
    monkeypatch.setattr(refresh, "collect_readings", lambda *_a, **_k: ([board], []))
    return refresh.run(
        observed_at=OBSERVED, dry_run=False, root=root, source_cache=cache,
        model_ids=("lab/orbit",),
    )


def evidence_rows(card: Path) -> dict[str, dict]:
    front = yaml.safe_load(card.read_text(encoding="utf-8").split("---", 2)[1])
    return {row["model_id_as_evaluated"]: row for row in front["benchmarks"]["evidence"]}


def real_shape_card(tmp_path: Path) -> tuple[Path, Path, Path]:
    text = card_text(extra=(*TRACKED_EMPTY[1:], TRACKED_SCORED))
    return setup_repo(tmp_path, text)


def test_sparse_board_marks_when_every_tracked_row_is_present(monkeypatch, tmp_path: Path) -> None:
    root, cache, card = real_shape_card(tmp_path)

    report = run_matharena(monkeypatch, root, cache, real_shape_rows())

    rows = evidence_rows(card)
    assert report.failures == []
    assert sorted(mark.model for mark in report.not_published) == sorted(TRACKED_EMPTY)
    assert {mark.kind for mark in report.not_published} == {"newly_marked"}
    for name in TRACKED_EMPTY:
        assert rows[name]["not_published_since"] == OBSERVED
    assert "not_published_since" not in rows[TRACKED_SCORED]
    assert rows[TRACKED_SCORED]["score"] == 55.0


def test_missing_tracked_row_blocks_every_mark_on_the_board(monkeypatch, tmp_path: Path) -> None:
    root, cache, card = real_shape_card(tmp_path)
    board = [(name, value) for name, value in real_shape_rows() if name != "Quill 2"]
    assert len(board) == 23

    report = run_matharena(monkeypatch, root, cache, board)

    assert report.not_published == []
    assert "not_published_since" not in card.read_text(encoding="utf-8")
    reasons = sorted(failure.reason for failure in report.failures)
    expected = [missing_tracked("lab/orbit", name) for name in TRACKED_EMPTY if name != "Quill 2"]
    expected.append("no unique row for 'Quill 2'")
    assert reasons == sorted(expected)


def test_truncated_board_marks_nothing(monkeypatch, tmp_path: Path) -> None:
    root, cache, card = real_shape_card(tmp_path)
    ordered = [
        ("Orbit 9", None), ("Rival 1", 71.0), ("Rival 2", 72.0), ("Rival 3", 73.0),
        ("Orbit 8", None), ("Idle 1", None),
    ]
    assert len(ordered) == 6

    report = run_matharena(monkeypatch, root, cache, ordered)

    assert report.not_published == []
    assert "not_published_since" not in card.read_text(encoding="utf-8")
    reasons = {failure.reason for failure in report.failures}
    assert missing_tracked("lab/orbit") in reasons
    assert missing_tracked("lab/orbit", "Orbit 8") in reasons


def test_single_tracked_row_is_never_marked(monkeypatch, tmp_path: Path) -> None:
    root, cache, card = setup_repo(tmp_path, card_text())
    before = card.read_bytes()

    report = run_matharena(monkeypatch, root, cache, real_shape_rows())

    assert card.read_bytes() == before
    assert report.not_published == []
    assert [failure.reason for failure in report.failures] == [SINGLE_TRACKED]


def test_fewer_than_three_scored_neighbours_marks_nothing(monkeypatch, tmp_path: Path) -> None:
    both = [("Orbit 9", None), ("Orbit 8", None)]
    for scored in (
        [("Rival 1", 71.0), ("Rival 2", 72.0)],  # two numeric neighbours
        [],  # every value gone
    ):
        root, cache, card = setup_repo(tmp_path / f"n{len(scored)}", card_text(extra=("Orbit 8",)))
        before = card.read_bytes()

        report = run_matharena(monkeypatch, root, cache, both + scored)

        assert card.read_bytes() == before
        assert report.not_published == []
        assert sorted(failure.reason for failure in report.failures) == sorted([
            FEW_SCORED, FEW_SCORED.replace("'Orbit 9'", "'Orbit 8'"),
        ])


def test_a_renamed_value_column_is_a_failed_read_not_a_mark(monkeypatch, tmp_path: Path) -> None:
    table = (
        "<table><thead><tr><th>Rank</th><th>Model Name</th><th>Provider</th>"
        "<th>Score</th></tr></thead><tbody></tbody></table>"
    )
    with pytest.raises(ValueError):
        refresh.readers.project_matharena(
            json.dumps({"table": table}).encode(),
            url=SOURCE_URL, page_ref="sha256:" + "b" * 64, read_date=OBSERVED,
        )


def test_refused_mark_reasons_are_distinct_from_no_unique_row() -> None:
    rows = [{"model": "Orbit 9", "score": None}, *SCORED]
    cases = {
        UNDECLARED: plan(rows, declared=False),
        FEW_SCORED: plan([{"model": "Orbit 9", "score": None}, SCORED[0], SCORED[1]]),
        missing_tracked("lab/quill-3"): plan(rows, tracked_extra=("Quill 3",)),
        SINGLE_TRACKED: plan(rows, tracked_extra=()),
    }
    seen = set()
    for reason, (_observations, failures, marks) in cases.items():
        assert marks == []
        assert [failure.reason for failure in failures] == [reason]
        assert "no unique row" not in reason
        assert refresh._skip_class(reason) == "empty-cell-not-marked"
        seen.add(reason)
    assert len(seen) == 4

    _o, failures, _m = plan([{"model": "Harbor 2", "score": 70}])
    assert [failure.reason for failure in failures] == ["no unique row for 'Orbit 9'"]
    assert refresh._skip_class(failures[0].reason) == "no-unique-row"
