"""The verifier owns an Arena row whose display name has a compound qualifier.

One board holds the bare sibling, the high-context row, and the thinking-budget
row. The name outside the parenthesis is an ordered token sequence. The
qualifier inside it is a multiset. A subset, a reordered version, a repeated
token that collapses, a different date, or a second row with the same identity
is refused. Names and numbers are invented.
"""

from __future__ import annotations

import json
import shutil
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
import pytest

pytestmark = pytest.mark.usefixtures("terms_register_present")

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
    snapshot: bool = False,
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
    model_id_as_evaluated: {json.dumps(evaluated)}
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
    before = tmp_path / "before"
    if snapshot:
        shutil.copytree(root, before)
    report = refresh.run(
        observed_at="2026-11-11",
        dry_run=False,
        root=root,
        source_cache=cache,
        model_ids=(_MODEL,),
        arena_latest=True,
    )
    if snapshot:
        return report, card, root, before
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


def test_compound_refuses_a_reordered_version(monkeypatch, tmp_path: Path) -> None:
    """5-4 is not 4.5. The matcher can still find the row. The card is not written."""
    stored = "acme-orbit-5-4-20251101-high-32k"
    assert verify._reading_subject_matches(_HIGH, [stored]) is False
    report, card, _root = _run(monkeypatch, tmp_path, evaluated=stored)

    assert report.failures, "a reordered version was written"
    row = _unchanged(card)
    assert row["model_id_as_evaluated"] == stored


def test_compound_refuses_a_version_token_moved_after_the_qualifier(
    monkeypatch, tmp_path: Path,
) -> None:
    """A 5 after the qualifier is not the 5 in 4.5, and 32k is not a version token."""
    stored = "acme-orbit-4-20251101-high-32k-5"
    assert verify._reading_subject_matches(_HIGH, [stored]) is False
    assert verify._reading_subject_matches(
        _HIGH, ["acme-orbit-32k-4-5-20251101-high"],
    ) is False
    assert verify._reading_subject_matches(
        "Acme Orbit 4.5 32K (High, 20251101)", [_HIGH_ID],
    ) is False
    report, card, _root = _run(monkeypatch, tmp_path, evaluated=stored)

    assert report.failures, "a version token after the qualifier was written"
    row = _unchanged(card)
    assert row["model_id_as_evaluated"] == stored


def test_compound_refuses_a_repeated_token_collapsing(monkeypatch, tmp_path: Path) -> None:
    """4.4 keeps both fours. The slug with one 4 is a different name."""
    subject = "Acme Orbit 4.4 (High, 32K, 20251101)"
    stored = "acme-orbit-4-20251101-high-32k"
    assert verify._reading_subject_matches(subject, [stored]) is False
    rows = [
        _dataset_row(subject, 1447.0, 36239, 12),
        _dataset_row("Acme Orbit 4.4 (20251101)", 1366.0, 42962, 20),
    ]
    report, card, _root = _run(monkeypatch, tmp_path, evaluated=stored, dataset_rows=rows)

    assert report.failures, "a repeated version token collapsed and was written"
    row = _unchanged(card)
    assert row["model_id_as_evaluated"] == stored


def test_compound_still_owns_the_exact_row(monkeypatch, tmp_path: Path) -> None:
    """(a), (b) and (c) still read the row round 1 accepted. Qualifier order is free."""
    assert verify._reading_subject_matches(_HIGH, [_HIGH_ID]) is True
    assert verify._reading_subject_matches(_THINK, [_THINK_ID]) is True
    assert verify._reading_subject_matches(_BARE, [_BARE_ID]) is True
    assert verify._reading_subject_matches(
        "Acme Orbit 4.5 (32K, 20251101, High)", [_HIGH_ID],
    ) is True

    high, high_card, high_root = _run(monkeypatch, tmp_path / "a", evaluated=_HIGH_ID)
    assert high.failures == [], high.failures
    assert _evidence_row(high_card)["score"] == 1447.0
    assert _evidence_row(high_card)["n"] == 36239
    assert _verification_log(high_root)["outcome"] == "verified"

    bare, bare_card, bare_root = _run(
        monkeypatch, tmp_path / "b", evaluated=_BARE_ID, version=_BARE_ID,
    )
    assert bare.failures == [], bare.failures
    assert _evidence_row(bare_card)["score"] == 1366.0
    assert _evidence_row(bare_card)["n"] == 42962
    assert _verification_log(bare_root)["outcome"] == "verified"

    think, think_card, think_root = _run(
        monkeypatch, tmp_path / "c", evaluated=_THINK_ID,
    )
    assert think.failures == [], think.failures
    think_row = _evidence_row(think_card)
    assert think_row["score"] == 1377.0
    assert think_row["n"] == 35843
    assert think_row["effort"] is None
    assert _verification_log(think_root)["outcome"] == "verified"


def test_display_name_as_stored_id_writes_the_named_effort(
    monkeypatch, tmp_path: Path,
) -> None:
    """The stored id is the display name, and the card effort starts null.

    The writer sets effort to high, the level that parenthesis names. The
    score-only guard accepts that null-to-named-level change.
    """
    report, card, root, before = _run(
        monkeypatch, tmp_path, evaluated=_HIGH, snapshot=True,
    )

    assert report.failures == [], report.failures
    row = _evidence_row(card)
    assert row["model_id_as_evaluated"] == _HIGH
    assert row["score"] == 1447.0
    assert row["n"] == 36239
    assert row["interval"] == [1441.0, 1453.0]
    assert row["effort"] == "high"
    assert "36239" in row["configuration"]
    assert _verification_log(root)["outcome"] == "verified"
    guard = refresh.check_score_only(before, root)
    assert guard.ok, guard.errors


# Round 3. Each pair carries the result measured on main for that pair
# (hard-coded in the comments and asserts). This change only turns a main
# refusal into a match for an exact compound row.


def _assert_refused_and_unwritten(monkeypatch, tmp_path: Path, subject: str, stored: str) -> None:
    # main measured: _reading_subject_matches is False for this pair.
    assert verify._reading_subject_matches(subject, [stored]) is False
    rows = [_dataset_row(subject, 1447.0, 36239, 12)]
    report, card, _root = _run(monkeypatch, tmp_path, evaluated=stored, dataset_rows=rows)
    assert report.failures, "another row's numbers were written"
    row = _unchanged(card)
    assert row["model_id_as_evaluated"] == stored


def test_compound_refuses_an_effort_word_in_the_slug_name(monkeypatch, tmp_path: Path) -> None:
    """Max is a name token in the slug. The display name keeps it outside the parenthesis."""
    _assert_refused_and_unwritten(
        monkeypatch,
        tmp_path,
        "Acme Orbit (Max, High, 32K, 20251101)",
        "acme-orbit-max-20251101-high-32k",
    )


def test_compound_refuses_a_size_in_the_slug_name(monkeypatch, tmp_path: Path) -> None:
    """32k before the date is part of the slug name, not the qualifier."""
    _assert_refused_and_unwritten(
        monkeypatch,
        tmp_path,
        "Acme Orbit (32K, High, 20251101)",
        "acme-orbit-32k-20251101-high",
    )


def test_compound_refuses_a_second_eight_digit_token(monkeypatch, tmp_path: Path) -> None:
    """12345678 is not a calendar date, so it stays in the slug name."""
    _assert_refused_and_unwritten(
        monkeypatch,
        tmp_path,
        "Acme Orbit (12345678, High, 32K, 20251101)",
        "acme-orbit-12345678-20251101-high-32k",
    )


def test_compound_requires_exactly_one_valid_date() -> None:
    subject = "Acme Orbit 4.5 (High, 32K, 20251101)"
    # main measured False for each of these pairs.
    assert verify._reading_subject_matches(subject, ["acme-orbit-4-5-high-32k"]) is False
    assert verify._reading_subject_matches(
        subject, ["acme-orbit-4-5-20251101-high-32k-20251102"],
    ) is False
    assert verify._reading_subject_matches(
        subject, ["acme-orbit-4-5-20251101-20251102-high-32k"],
    ) is False
    assert verify._reading_subject_matches(
        subject, ["acme-orbit-4-5-20251345-high-32k"],
    ) is False
    assert verify._reading_subject_matches(
        "Acme Orbit 4.5 (High, 32K, 20251345)", ["acme-orbit-4-5-20251345-high-32k"],
    ) is False
    # A parenthesis with no date, or two parentheses, is not compound.
    assert verify._reading_subject_matches(
        "Acme Orbit 4.5 (High, 32K)", ["acme-orbit-4-5-20251101-high-32k"],
    ) is False
    assert verify._reading_subject_matches(
        "Acme Orbit (4.5) (High, 32K, 20251101)", [_HIGH_ID],
    ) is False
    # main accepted this flattened pair through the older path. Still accepted.
    assert verify._reading_subject_matches(
        subject, ["acme-orbit-4-5-high-32k-20251101"],
    ) is True
    # The exact row is matched (main: False).
    assert verify._reading_subject_matches(subject, [_HIGH_ID]) is True


def test_compound_name_with_a_qualifier_word_matches_only_itself() -> None:
    stored = "acme-thinking-2-20251101-high-32k"
    # main measured False for both pairs.
    assert verify._reading_subject_matches(
        "Acme Thinking 2 (High, 32K, 20251101)", [stored],
    ) is True
    assert verify._reading_subject_matches(
        "Acme 2 (Thinking, High, 32K, 20251101)", [stored],
    ) is False


def test_two_compound_display_names_are_not_flattened_into_one() -> None:
    # MODEL-486: these pairs flatten to one string and are different names.
    pairs = [
        ("Acme Orbit Max (High, 32K, 20251101)", "Acme Orbit (Max, High, 32K, 20251101)"),
        ("Acme Orbit Thinking (32K, 20251101)", "Acme Orbit (Thinking 32K, 20251101)"),
    ]
    for left, right in pairs:
        assert verify.split_model_cell(left)[0] == verify.split_model_cell(right)[0]
        assert verify._reading_subject_matches(left, [right]) is False
        assert verify._reading_subject_matches(right, [left]) is False
        # The same name, and the name with its parenthesis re-spaced, still match.
        assert verify._reading_subject_matches(left, [left]) is True
        assert verify._reading_subject_matches(left, [left.replace(", ", " , ")]) is True
    # A display name still matches its own slug through the flat identity.
    assert verify._reading_subject_matches(
        "Acme Orbit Max (High, 32K, 20251101)", ["acme-orbit-max-high-32k-20251101"],
    ) is True


# MODEL-524: the board renamed four models after their readings were filed. The
# exact map in ``refresh.ARENA_RENAMED`` refiles each row under the board's name.
_RENAMED = [
    ("olmo-2-0325-32b-instruct", "OLMo 2 32B Instruct (0325)"),
    ("kimi-k2-0711-preview", "Kimi K2 Preview (0711)"),
    ("kimi-k2-0905-preview", "Kimi K2 Preview (0905)"),
    (
        "gemini-2.5-flash-lite-preview-06-17-thinking",
        "Gemini 2.5 Flash-Lite Preview (Thinking, 06-17)",
    ),
    # MODEL-524 item 2: the 2026-11 renames, each anchored at the September revision.
    ("c4ai-aya-expanse-32b", "Aya Expanse 32B"),
    ("c4ai-aya-expanse-8b", "Aya Expanse 8B"),
    ("c4ai-aya-vision-32b", "Aya Vision 32B"),
    ("command-r-plus-08-2024", "Command R+ (08-2024)"),
    (
        "gemini-2.5-flash-lite-preview-09-2025-no-thinking",
        "Gemini 2.5 Flash-Lite Preview (Non-Thinking, 09-2025)",
    ),
    ("mistral-medium-2505", "Mistral Medium 3 (2505)"),
    ("mistral-medium-2508", "Mistral Medium 3.1 (2508)"),
    ("mistral-small-2506", "Mistral Small 3.2 (2506)"),
    ("gpt-5.3-chat-latest", "GPT-5.3 Chat"),
    ("solar-pro4", "Solar Pro 4"),
]


def test_the_alias_map_is_exactly_the_renamed_models() -> None:
    assert refresh.ARENA_RENAMED == dict(_RENAMED)


def test_an_alias_match_refiles_the_row_under_the_board_name(monkeypatch, tmp_path: Path) -> None:
    """Each of the four is refiled whole: name, score, interval, votes, date, revision."""
    for index, (stored, current) in enumerate(_RENAMED):
        report, card, root, before = _run(
            monkeypatch, tmp_path / str(index), evaluated=stored,
            dataset_rows=[_dataset_row(current, 1450.0, 7777, 9)], snapshot=True,
        )
        assert report.failures == [], report.failures
        assert report.quarantined == []
        row = _evidence_row(card)
        assert row["model_id_as_evaluated"] == current
        assert row["score"] == 1450.0
        assert row["interval"] == [1444.0, 1456.0]
        assert row["n"] == 7777
        assert str(row["observed_at"]) == "2026-11-11"
        assert "7777" in row["configuration"]
        assert "2026-11-11" in row["configuration"]
        assert _verification_log(root)["outcome"] == "verified"
        # The score-only check allows the refile, and only to the mapped name.
        old = _evidence_row(before / "models" / "lab" / "model.md")
        assert refresh._row_allows_refresh(old, row)
        assert not refresh._row_allows_refresh(old, {**row, "model_id_as_evaluated": "other"})


def test_an_alias_never_maps_to_a_non_thinking_or_other_dated_row(
    monkeypatch, tmp_path: Path,
) -> None:
    """The board's name is one row's whole subject. A near name refiles nothing."""
    stored = "gemini-2.5-flash-lite-preview-06-17-thinking"
    for index, wrong in enumerate((
        "Gemini 2.5 Flash-Lite Preview (Non-Thinking, 06-17)",
        "Gemini 2.5 Flash-Lite Preview (Thinking, 09-2025)",
        "Gemini 2.5 Flash-Lite Preview (Thinking, 06-17) extra",
    )):
        report, card, _root = _run(
            monkeypatch, tmp_path / str(index), evaluated=stored,
            dataset_rows=[_dataset_row(wrong, 1450.0, 7777, 9)],
        )
        row = _unchanged(card)
        assert row["model_id_as_evaluated"] == stored
        assert [failure.reason for failure in report.failures] == [
            f"no unique row for {stored!r}",
        ]


def test_without_an_alias_a_missing_name_behaves_as_before(monkeypatch, tmp_path: Path) -> None:
    """A stored name outside the map is refused when the board spells it differently."""
    report, card, _root = _run(
        monkeypatch, tmp_path, evaluated="kimi-k2-0000-preview",
        dataset_rows=[_dataset_row("Kimi K2 Preview (0000)", 1450.0, 7777, 9)],
    )
    row = _unchanged(card)
    assert row["model_id_as_evaluated"] == "kimi-k2-0000-preview"
    assert len(report.failures) == 1


def test_an_alias_never_maps_command_r_plus_to_command_r(monkeypatch, tmp_path: Path) -> None:
    """``+`` is part of the board's name: the plain sibling is not the renamed row."""
    stored = "command-r-plus-08-2024"
    report, card, _root = _run(
        monkeypatch, tmp_path, evaluated=stored,
        dataset_rows=[_dataset_row("Command R (08-2024)", 1450.0, 7777, 9)],
    )
    row = _unchanged(card)
    assert row["model_id_as_evaluated"] == stored
    assert [failure.reason for failure in report.failures] == [
        f"no unique row for {stored!r}",
    ]


# MODEL-524 item 3: two dataset rows normalise to the stored name. The row whose
# identifier is exactly the stored one, ``+`` included, is the reading; with no
# such row, or two, nothing is filed and the refusal names both rows.
_PLAIN = "Acme R (08-2024)"
_PLUS = "Acme R+ (08-2024)"


def test_a_collision_takes_the_row_whose_identifier_is_the_stored_one(
    monkeypatch, tmp_path: Path,
) -> None:
    report, card, root, before = _run(
        monkeypatch, tmp_path, evaluated="acme-r-08-2024",
        dataset_rows=[_dataset_row(_PLUS, 1300.0, 9999, 7), _dataset_row(_PLAIN, 1250.0, 7777, 9)],
        snapshot=True,
    )
    assert report.failures == [], report.failures
    assert report.quarantined == []
    row = _evidence_row(card)
    # The stored name normalises to the row, so it stays, as for any single hit.
    assert row["model_id_as_evaluated"] == "acme-r-08-2024"
    assert row["score"] == 1250.0
    assert row["n"] == 7777
    assert row["interval"] == [1244.0, 1256.0]
    assert "7777" in row["configuration"]
    assert "9999" not in row["configuration"]
    assert _verification_log(root)["outcome"] == "verified"
    assert refresh._row_allows_refresh(_evidence_row(before / "models" / "lab" / "model.md"), row)


def test_a_collision_with_no_exact_identifier_files_nothing_and_names_both(
    monkeypatch, tmp_path: Path,
) -> None:
    """Both rows spell the stored identifier: undetermined, never a guess."""
    report, card, _root = _run(
        monkeypatch, tmp_path, evaluated="acme-r-08-2024",
        dataset_rows=[_dataset_row(_PLAIN, 1250.0, 7777, 9),
                      _dataset_row("acme-r-08-2024", 1300.0, 9999, 7)],
    )
    row = _unchanged(card)
    assert row["model_id_as_evaluated"] == "acme-r-08-2024"
    assert "9999" not in row["configuration"]
    assert [failure.reason for failure in report.failures] == [
        "two dataset rows normalise to the stored name; undetermined, no exact "
        "identifier match among 'Acme R (08-2024)', 'acme-r-08-2024'",
    ]
    assert _arena_skip_classes(report) == {"no-unique-row": 1}
    assert report.quarantined == []


def test_exact_identifier_hits_read_plus_as_a_token() -> None:
    hits = [{"model_name": _PLAIN}, {"model_name": _PLUS}]
    assert refresh._exact_identifier_hits(hits, "acme-r-08-2024") == [{"model_name": _PLAIN}]
    assert refresh._exact_identifier_hits(hits, "acme-r-plus-08-2024") == [{"model_name": _PLUS}]
    assert refresh._exact_identifier_hits(hits, "acme-r-08") == []
    assert refresh._exact_identifier_hits(hits, "") == []


# MODEL-524: an executable anchor for the ten 2026-11 aliases, independent of the map.
# The evidence is the dataset's own rename record: category ``overall`` of one config
# at two consecutive commits that update it (CC BY 4.0, LMArena; see the fixture's
# ``credit``). Each old name vanishes at the step and the board's new name appears;
# the rating and the vote count continue across it. The map is only compared with
# what the record says, never used to find it.
_RECORD = Path(__file__).parent / "fixtures" / "leaderboard_refresh" / "arena_rename_record_2026-10.json"
#: A rename step moves a rating by at most this much, and the votes by this ratio.
_RATING_STEP = 2.0
_VOTES_STEP = (0.995, 1.15)
#: The four aliases of modelspec#1120, anchored there by stored votes and slug.
_EARLIER = {
    "olmo-2-0325-32b-instruct", "kimi-k2-0711-preview", "kimi-k2-0905-preview",
    "gemini-2.5-flash-lite-preview-06-17-thinking",
}


def _record() -> dict:
    return json.loads(_RECORD.read_text(encoding="utf-8"))


def _continues(before: dict, after: dict) -> bool:
    low, high = _VOTES_STEP
    return (
        abs(after["rating"] - before["rating"]) <= _RATING_STEP
        and low <= after["vote_count"] / before["vote_count"] <= high
    )


def _anchor_failures(record: dict, aliases: dict[str, str]) -> list[str]:
    """Why each alias is not the record's rename, or nothing when all are.

    An alias holds when, at every step where its old name vanishes, the new name is
    the only appeared row that continues it, and at one step or more the old name is
    the only vanished row the new name continues (the pair is mutual).
    """
    failures: list[str] = []
    for old, new in sorted(aliases.items()):
        seen = mutual = False
        for step in record["steps"]:
            vanished = {row["model_name"]: row for row in step["before"]["vanished"]}
            appeared = {row["model_name"]: row for row in step["after"]["appeared"]}
            if old not in vanished:
                continue
            seen = True
            forward = [name for name, row in appeared.items() if _continues(vanished[old], row)]
            if forward != [new]:
                failures.append(f"{old} -> {new}: {step['config']} continues to {forward}")
                continue
            back = [name for name, row in vanished.items() if _continues(row, appeared[new])]
            mutual = mutual or back == [old]
        if not seen:
            failures.append(f"{old} -> {new}: the record shows no step where {old} vanishes")
        elif not mutual and not any(failure.startswith(f"{old} ->") for failure in failures):
            failures.append(f"{old} -> {new}: no step where {new} continues only {old}")
    return failures


def test_the_rename_record_is_two_consecutive_dataset_commits() -> None:
    record = _record()
    assert record["licence"] == "CC BY 4.0" and "LMArena" in record["credit"]
    for step in record["steps"]:
        for side in ("before", "after"):
            assert refresh.readers.valid_arena_revision(step[side]["revision"])
            assert step[side]["commit_title"].startswith(f"Update {step['config']} for ")
        vanished = {row["model_name"] for row in step["before"]["vanished"]}
        appeared = {row["model_name"] for row in step["after"]["appeared"]}
        assert vanished and appeared and not vanished & appeared


def test_every_2026_11_alias_is_the_datasets_own_rename() -> None:
    later = {old: new for old, new in refresh.ARENA_RENAMED.items() if old not in _EARLIER}
    assert len(later) == 10
    assert _anchor_failures(_record(), later) == []


def test_a_planted_wrong_alias_fails_the_anchor() -> None:
    later = {old: new for old, new in refresh.ARENA_RENAMED.items() if old not in _EARLIER}
    record = _record()
    planted = [
        # Two siblings swapped: each name exists, the pairing is wrong.
        {**later, "mistral-medium-2505": later["mistral-medium-2508"],
         "mistral-medium-2508": later["mistral-medium-2505"]},
        {**later, "c4ai-aya-expanse-32b": later["c4ai-aya-expanse-8b"]},
        # The "+" sibling instead of the row itself.
        {**later, "command-r-plus-08-2024": "Command R (08-2024)"},
        # A name the record never shows appearing.
        {**later, "solar-pro4": "Solar Pro 4 (Preview)"},
        # An old name the record never shows vanishing.
        {**later, "solar-pro5": "Solar Pro 4"},
    ]
    for aliases in planted:
        assert _anchor_failures(record, aliases), aliases
