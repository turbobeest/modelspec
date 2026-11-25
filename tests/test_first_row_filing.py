"""MODEL-478: first-row filing on the Arena boards, built as docs/design/first-row-filing.md.

Every fixture is synthetic: invented labs, cards, board names and figures.
"""

from __future__ import annotations

import ast
import json
import shutil
from pathlib import Path

import pytest

from decision.model import VerificationActor
from scripts import refresh_leaderboards as refresh

DATASET = refresh.ARENA_DATASET_ROOT
REVISION = "0123456789abcdef0123456789abcdef01234567"
OBSERVED = "2026-11-11"
SOURCE_ID = "fixture-arena"
PARQUET = f"{DATASET}/resolve/{REVISION}/text/latest-00000-of-00001.parquet"
TERMS = {"huggingface.co": "restricts", "example.test": "permits"}


def _card(root: Path, slug: str, display: str, *, status: str = "active",
          rows: str = "  evidence: []\n", extra: str = "", lab: str = "lab",
          released: str | None = None) -> Path:
    path = root / "models" / lab / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    if released:
        extra = f"release_date: '{released}'\n" + extra
    path.write_text(
        f"---\nmodel_id: {lab}/{slug}\ndisplay_name: {display}\nstatus: {status}\n{extra}"
        f"benchmarks:\n{rows}---\nProse stays.\n",
        encoding="utf-8",
    )
    return path


TEMPLATE_ROWS = f"""  evidence:
  - benchmark_id: arena_elo_overall
    model_id_as_evaluated: Template Model
    score: 1100.0
    unit: Arena score (Elo scale)
    interval: [1080.0, 1120.0]
    n: 1000
    effort: null
    source_url: {DATASET}
    source_kind: independent_evaluator
    evidence_date: '2026-10-01'
    date_type: published
    observed_at: '2026-10-01'
    verified_at: '2026-10-01'
    benchmark_version: text / overall, latest split
    configuration: >-
      LMArena leaderboard dataset, subset text, category overall,
      leaderboard_publish_date 2026-10-01. Rating 1100.00 [1080.00, 1120.00], 1000 votes, rank 9.
    id: lab/template#arena_elo_overall#old
    sources:
    - source_id: {SOURCE_ID}
      snapshot_ref: sha256:{'a' * 64}
      cited_regions: [rows]
"""


def _dataset_row(name: str, rating: float, rank: int = 3, **overrides) -> dict:
    row = {
        "model_name": name,
        "rating": rating,
        "rating_lower": rating - 20.25,
        "rating_upper": rating + 20.25,
        "vote_count": 2222,
        "leaderboard_publish_date": "2026-11-02",
        "rank": rank,
    }
    row.update(overrides)
    return row


def _repo(tmp_path: Path, terms: dict | None = None) -> Path:
    root = tmp_path / "repo"
    _card(root, "template", "Template Model", rows=TEMPLATE_ROWS)
    (root / "premier").mkdir(parents=True)
    (root / "premier" / "slice-1.yaml").write_text(
        "models:\n- model_id: lab/template\n", encoding="utf-8",
    )
    (root / "registry").mkdir(parents=True)
    (root / "registry" / "sources.yaml").write_text(
        f"""schema_version: 1
sources:
- id: {SOURCE_ID}
  url: {PARQUET}
  fetch: http
  normaliser: text-default
  cited_regions:
  - id: rows
    locator: {{kind: page, value: ''}}
""",
        encoding="utf-8",
    )
    (root / "registry" / "source-terms.json").write_text(
        json.dumps(TERMS if terms is None else terms), encoding="utf-8",
    )
    (root / "verification").mkdir()
    return root


def _board(tmp_path: Path, rows: list[dict]) -> refresh.BoardReading:
    store = refresh.CopyStore(tmp_path / "copies")
    projection = refresh.readers.document(
        [_dataset_row("Template Model", 1100.0, rank=9), *rows],
        url=PARQUET, page_ref="sha256:" + "b" * 64, read_date=OBSERVED, note="fixture",
    )
    return refresh._reading_from_projection(
        key="arena:arena_elo_overall", source_id=SOURCE_ID, benchmarks=("arena_elo_overall",),
        source_url=PARQUET, projected=projection, observed_at=OBSERVED,
        value_field="rating", store=store, card_urls=(DATASET,),
    )


def _run(monkeypatch, tmp_path: Path, root: Path, rows: list[dict], **options):
    board = _board(tmp_path, rows)
    monkeypatch.delenv(refresh.ARENA_REVISION_ENV, raising=False)
    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)
    monkeypatch.setattr(
        refresh.readers, "resolve_arena_revision",
        lambda _fetch: refresh.readers.ArenaRevision(sha=REVISION),
    )
    monkeypatch.setattr(refresh, "collect_readings", lambda *_a, **_k: ([board], []))
    options.setdefault("first_rows", True)
    if options["first_rows"]:
        options.setdefault("collector", refresh.COLLECTOR)
    return refresh.run(
        observed_at=OBSERVED, dry_run=options.pop("dry_run", False), root=root,
        source_cache=tmp_path / "copies", arena_latest=True, **options,
    )


def _rows(path: Path) -> list[dict]:
    return refresh._front(path)["benchmarks"]["evidence"]


_TWO = "two board rows name this card"


def _refusals(report) -> dict[str, tuple[str, str]]:
    return {entry.board_name: (entry.model_id, entry.reason) for entry in report.first_rows_refused}


# --- hosts ------------------------------------------------------------------------------------


@pytest.mark.parametrize(("klass", "files"), [
    ("permits", True), ("restricts", True),
    ("unclear", False), ("forbids", False), (None, False),
])
def test_only_a_permits_or_restricts_host_files_a_first_row(
    monkeypatch, tmp_path: Path, klass, files,
) -> None:
    terms = {"example.test": "permits"}
    if klass is not None:
        terms["huggingface.co"] = klass
    root = _repo(tmp_path, terms)
    card = _card(root, "new-one", "New One")

    report = _run(monkeypatch, tmp_path, root, [_dataset_row("New One", 1200.0)])

    assert len(report.first_rows) == (1 if files else 0)
    assert len(_rows(card)) == (1 if files else 0)
    if not files:
        assert any("first rows: the board's host is" in row.reason for row in report.failures)


def test_the_host_class_reads_the_canonical_host() -> None:
    assert refresh.first_row_host_class(DATASET, TERMS) == "restricts"
    assert refresh.first_row_host_class("https://HuggingFace.co./datasets/x", TERMS) == "restricts"
    assert refresh.first_row_host_class("https://unlisted.test/board", TERMS) == "missing"
    assert refresh.first_row_host_class("not a url", TERMS) == "missing"
    assert refresh.first_row_host_class(
        "https://example.test/x", {"example.test": "cite-only"}) == "cite-only"


# --- identity ---------------------------------------------------------------------------------


def test_an_exact_name_files_one_row_on_an_active_card_outside_the_premier_set(
    monkeypatch, tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    card = _card(root, "new-one", "New One")

    report = _run(monkeypatch, tmp_path, root, [_dataset_row("New One", 1210.256789)])

    assert report.failures == [], report.failures
    assert report.quarantined == [], report.quarantined
    [entry] = report.first_rows
    assert (entry.model_id, entry.benchmark, entry.board_name, entry.match_key) == (
        "lab/new-one", "arena_elo_overall", "New One", "new-one")
    assert entry.source == DATASET and entry.capped is False
    [row] = _rows(card)
    assert row["score"] == 1210.26
    assert row["source_url"] == DATASET
    assert row["observed_at"] == OBSERVED and row["verified_at"] == OBSERVED
    assert row["evidence_date"] == "2026-11-02"
    assert row["id"] == refresh.evidence_id("lab/new-one", row)
    assert card.read_text(encoding="utf-8").endswith("---\nProse stays.\n")
    log = [json.loads(line) for line in
           (root / "verification" / "log.jsonl").read_text().splitlines()]
    mine = [line for line in log if line["target"]["id"] == row["id"]]
    assert [line["outcome"] for line in mine] == ["verified"]
    assert mine[0]["collector"] == refresh.COLLECTOR.model_dump(mode="json")


def test_an_added_arena_row_is_published_and_quotes_its_reading_like_peer_rows(
    monkeypatch, tmp_path: Path,
) -> None:
    """MODEL-511 item 2 and the orchestrator addendum: ``published``, and the reading sentence."""
    root = _repo(tmp_path)
    card = _card(root, "new-one", "New One")

    _run(monkeypatch, tmp_path, root, [_dataset_row("New One", 1200.0, rank=4)])

    [row] = _rows(card)
    assert row["date_type"] == "published"
    assert row["interval"] == [1179.75, 1220.25]
    assert row["n"] == 2222
    assert row["configuration"] == (
        "LMArena leaderboard dataset, subset text, category overall, "
        "leaderboard_publish_date 2026-11-02. Rating 1200.00 [1179.75, 1220.25], "
        "2222 votes, rank 4."
    )
    assert list(row)[:6] == [
        "benchmark_id", "model_id_as_evaluated", "score", "unit", "interval", "n",
    ]


def test_the_next_weekly_refresh_retells_a_first_row_and_the_guard_calls_it_score_only(
    monkeypatch, tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    card = _card(root, "new-one", "New One")
    _run(monkeypatch, tmp_path, root, [_dataset_row("New One", 1200.0, rank=4)])
    # The new card is not premier; latest mode reaches it as a card already on the board.
    before = tmp_path / "before"
    shutil.copytree(root, before)

    again = _run(monkeypatch, tmp_path, root,
                 [_dataset_row("New One", 1203.5, rank=3, vote_count=2300)], first_rows=False)

    assert again.failures == [], again.failures
    assert again.quarantined == [], again.quarantined
    assert [change.model_id for change in again.changes] == ["lab/new-one"]
    [row] = _rows(card)
    assert row["score"] == 1203.5 and row["n"] == 2300
    assert "Rating 1203.50 [1183.25, 1223.75], 2300 votes, rank 3." in row["configuration"]
    result = refresh.check_score_only(before, root)
    assert result.ok, result.errors
    assert result.merge_class == refresh.SCORE_ONLY_MERGE_CLASS
    assert result.labels == ()


def test_two_cards_that_share_a_display_name_get_no_row(monkeypatch, tmp_path: Path) -> None:
    root = _repo(tmp_path)
    one = _card(root, "twin-a", "Twin")
    two = _card(root, "twin-b", "Twin")

    report = _run(monkeypatch, tmp_path, root, [_dataset_row("Twin", 1200.0)])

    assert report.first_rows == []
    assert _rows(one) == [] and _rows(two) == []
    assert _refusals(report)["Twin"] == ("", "2 cards share this name")


def test_a_display_name_that_is_another_cards_model_id_is_shared(
    monkeypatch, tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    one = _card(root, "orbit-2", "Orbit Two")
    two = _card(root, "other", "Orbit 2")

    report = _run(monkeypatch, tmp_path, root, [_dataset_row("orbit-2", 1200.0)])

    assert report.first_rows == []
    assert _rows(one) == [] and _rows(two) == []
    assert _refusals(report)["orbit-2"][1] == "2 cards share this name"


def test_a_variant_name_never_lands_on_another_card(monkeypatch, tmp_path: Path) -> None:
    """The reviewer's question: can a row land on the wrong card through an effort variant?"""
    root = _repo(tmp_path)
    base = _card(root, "deep-2", "Deep 2")
    thinking = _card(root, "deep-2-thinking", "Deep 2 Thinking")

    report = _run(monkeypatch, tmp_path, root, [
        _dataset_row("Deep 2 (high)", 1250.0),        # an effort label: the base card, at high
        _dataset_row("deep-2-high", 1240.0),          # strip=False keeps "high": no card
        _dataset_row("Deep 2 Thinking", 1230.0),      # its own card, not the base
        _dataset_row("Deep 2 (thinking)", 1220.0),    # not an effort label: refused
    ])

    [base_row] = _rows(base)
    assert (base_row["model_id_as_evaluated"], base_row["effort"]) == ("Deep 2 (high)", "high")
    [row] = _rows(thinking)
    assert row["model_id_as_evaluated"] == "Deep 2 Thinking"
    assert row["score"] == 1230.0 and row.get("effort") is None
    refused = _refusals(report)
    # The nearest card keeps the qualifier: the folded name is the Thinking card's.
    assert refused["Deep 2 (thinking)"] == (
        "lab/deep-2-thinking", "board name contains parentheses")
    assert "deep-2-high" not in refused and "Deep 2 (high)" not in refused
    assert report.first_rows_unmatched == {"arena:arena_elo_overall": 1}


def test_an_effort_label_lands_on_the_base_card_with_that_effort(
    monkeypatch, tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    card = _card(root, "claude-fable-5-2", "Claude Fable 5.2", lab="anthropic")

    report = _run(monkeypatch, tmp_path, root, [_dataset_row("Claude Fable 5.2 (xHigh)", 1500.0)])

    assert report.quarantined == [], report.quarantined
    [entry] = report.first_rows
    assert (entry.model_id, entry.effort, entry.match_key) == (
        "anthropic/claude-fable-5-2", "xhigh", "claude-fable-5-2")
    [row] = _rows(card)
    assert row["effort"] == "xhigh"
    assert row["model_id_as_evaluated"] == "Claude Fable 5.2 (xHigh)"
    assert row["id"] == refresh.evidence_id("anthropic/claude-fable-5-2", row)


@pytest.mark.parametrize("name", [
    "Claude Fable 5.2 (Thinking)",        # not an effort label
    "Claude Fable 5.2 (preview)",
    "Claude Fable 5.2 (Claude Opus 5.5)",  # names a different model
    "Claude Fable 5.2 (thinking) (high)",  # the base name still has a parenthesis
])
def test_any_other_parenthesis_is_refused(monkeypatch, tmp_path: Path, name: str) -> None:
    root = _repo(tmp_path)
    fable = _card(root, "claude-fable-5-2", "Claude Fable 5.2", lab="anthropic")
    opus = _card(root, "claude-opus-5-5", "Claude Opus 5.5", lab="anthropic")

    report = _run(monkeypatch, tmp_path, root, [_dataset_row(name, 1500.0)])

    assert report.first_rows == []
    assert _rows(fable) == [] and _rows(opus) == []
    assert _refusals(report)[name][1] == "board name contains parentheses"


def test_an_effort_label_on_a_base_name_two_cards_share_is_refused(
    monkeypatch, tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    one = _card(root, "fable-a", "Claude Fable 5.2")
    two = _card(root, "fable-b", "Claude Fable 5.2")

    report = _run(monkeypatch, tmp_path, root, [_dataset_row("Claude Fable 5.2 (xHigh)", 1500.0)])

    assert _rows(one) == [] and _rows(two) == []
    assert _refusals(report)["Claude Fable 5.2 (xHigh)"] == ("", "2 cards share this name")


ARENA_ROW_AT_MAX = TEMPLATE_ROWS.replace("arena_elo_overall", "arena_webdev").replace(
    "Template Model", "Effort Card (max)").replace("effort: null", "effort: max").replace(
    "lab/template#", "lab/effort-card#")


def test_an_effort_row_needs_the_effort_the_card_is_read_at(monkeypatch, tmp_path: Path) -> None:
    root = _repo(tmp_path)
    card = _card(root, "effort-card", "Effort Card", rows=ARENA_ROW_AT_MAX)
    other = _card(root, "no-controls", "No Controls", extra=(
        "facts:\n- facet: feature.effort_controls\n  value: false\n"))

    report = _run(monkeypatch, tmp_path, root, [
        _dataset_row("Effort Card (high)", 1200.0),   # the card is read at max: refused
        _dataset_row("No Controls (high)", 1100.0),   # the card states no effort controls
    ])

    assert len(_rows(card)) == 1 and _rows(other) == []
    refused = _refusals(report)
    assert refused["Effort Card (high)"] == (
        "lab/effort-card", "the card is read at another effort on Arena")
    assert refused["No Controls (high)"] == (
        "lab/no-controls", "the card states it has no effort controls")


def test_the_board_row_at_the_cards_effort_is_the_one_filed(monkeypatch, tmp_path: Path) -> None:
    root = _repo(tmp_path)
    card = _card(root, "effort-card", "Effort Card", rows=ARENA_ROW_AT_MAX)

    report = _run(monkeypatch, tmp_path, root, [
        _dataset_row("Effort Card (high)", 1200.0), _dataset_row("Effort Card (max)", 1210.0),
    ])

    rows = _rows(card)
    assert [(row["benchmark_id"], row["effort"]) for row in rows] == [
        ("arena_webdev", "max"), ("arena_elo_overall", "max")]
    assert [entry.board_name for entry in report.first_rows] == ["Effort Card (max)"]


def test_two_effort_rows_for_a_card_read_at_no_effort_file_neither(
    monkeypatch, tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    card = _card(root, "fresh", "Fresh Model")

    report = _run(monkeypatch, tmp_path, root, [
        _dataset_row("Fresh Model (high)", 1200.0), _dataset_row("Fresh Model (max)", 1210.0),
    ])

    assert _rows(card) == []
    assert {entry.reason for entry in report.first_rows_refused} == {_TWO}


# --- the MODEL-478 adversarial review's confirmed cases ---------------------------------------


def test_an_unqualified_name_never_selects_the_qualified_card(monkeypatch, tmp_path: Path) -> None:
    """Qwen3-Next: the card side keeps "(Thinking)" and "Instruct"; nothing is stripped."""
    root = _repo(tmp_path)
    thinking = _card(root, "qwen3-next-80b-a3b-thinking", "Qwen3-Next 80B-A3B (Thinking)",
                     lab="qwen")
    instruct = _card(root, "qwen3-next-80b-a3b-instruct", "Qwen3-Next 80B-A3B Instruct",
                     lab="qwen")

    report = _run(monkeypatch, tmp_path, root, [_dataset_row("Qwen3-Next 80B-A3B", 1200.0)])

    assert _rows(thinking) == [] and _rows(instruct) == []
    assert report.first_rows == []
    assert report.first_rows_unmatched == {"arena:arena_elo_overall": 1}


def test_the_full_qualified_name_files_on_its_own_card(monkeypatch, tmp_path: Path) -> None:
    root = _repo(tmp_path)
    thinking = _card(root, "qwen3-next-80b-a3b-thinking", "Qwen3-Next 80B-A3B (Thinking)",
                     lab="qwen")
    instruct = _card(root, "qwen3-next-80b-a3b-instruct", "Qwen3-Next 80B-A3B Instruct",
                     lab="qwen")

    report = _run(monkeypatch, tmp_path, root, [
        _dataset_row("qwen3-next-80b-a3b-thinking", 1210.0),
        _dataset_row("Qwen3-Next 80B-A3B Instruct", 1190.0),
    ])

    assert report.quarantined == [], report.quarantined
    assert [(row["model_id_as_evaluated"], row["score"]) for row in _rows(thinking)] == [
        ("qwen3-next-80b-a3b-thinking", 1210.0)]
    assert [(row["model_id_as_evaluated"], row["score"]) for row in _rows(instruct)] == [
        ("Qwen3-Next 80B-A3B Instruct", 1190.0)]


def test_a_lone_effort_variant_card_is_never_its_own_base(monkeypatch, tmp_path: Path) -> None:
    root = _repo(tmp_path)
    by_name = _card(root, "foo-xhigh", "Foo (xHigh)")
    by_id = _card(root, "bar", "Bar xHigh")

    report = _run(monkeypatch, tmp_path, root, [
        _dataset_row("Foo (xHigh)", 1200.0), _dataset_row("Bar (xHigh)", 1190.0),
        _dataset_row("Bar xHigh", 1180.0),
    ])

    assert _rows(by_name) == [] and _rows(by_id) == []
    refused = _refusals(report)
    variant = "the card is itself an effort variant, not a base card"
    assert refused["Foo (xHigh)"] == ("lab/foo-xhigh", variant)
    assert refused["Bar (xHigh)"] == ("lab/bar", variant)
    assert refused["Bar xHigh"] == ("lab/bar", variant)


def test_a_sole_dated_snapshot_card_never_takes_a_base_row(monkeypatch, tmp_path: Path) -> None:
    root = _repo(tmp_path)
    dated = _card(root, "gpt-x-2025-01-31", "GPT X")
    stamped = _card(root, "orbit-0711", "Orbit")

    report = _run(monkeypatch, tmp_path, root, [
        _dataset_row("GPT X", 1200.0), _dataset_row("Orbit", 1190.0),
        _dataset_row("gpt-x-2025-01-31", 1180.0),
    ])

    refused = _refusals(report)
    dated_reason = "a dated snapshot card; the board name states none of its dates"
    assert refused["GPT X"] == ("lab/gpt-x-2025-01-31", dated_reason)
    assert refused["Orbit"] == ("lab/orbit-0711", dated_reason)
    assert _rows(stamped) == []
    # The board name that states the snapshot's date is the snapshot's own name.
    assert [row["model_id_as_evaluated"] for row in _rows(dated)] == ["gpt-x-2025-01-31"]


def _stored_arena_row(name: str, model: str) -> str:
    return TEMPLATE_ROWS.replace("arena_elo_overall", "arena_webdev").replace(
        "Template Model", name).replace("lab/template#", f"{model}#")


def test_a_former_name_of_another_card_is_refused(monkeypatch, tmp_path: Path) -> None:
    root = _repo(tmp_path)
    new = _card(root, "orbit-3", "Orbit 3")
    # Orbit 3 Pro was filed on Arena under the name "Orbit 3" before the board renamed it.
    pro = _card(root, "orbit-3-pro", "Orbit 3 Pro",
                rows=_stored_arena_row("Orbit 3", "lab/orbit-3-pro"))
    renamed = _card(root, "orbit-4", "Orbit 4", extra="former_names:\n- Orbit Four\n")
    other = _card(root, "orbit-four", "Orbit Four")

    report = _run(monkeypatch, tmp_path, root, [
        _dataset_row("Orbit 3", 1200.0), _dataset_row("Orbit Four", 1190.0),
    ])

    assert _rows(new) == [] and _rows(other) == [] and _rows(renamed) == []
    assert len(_rows(pro)) == 1
    refused = _refusals(report)
    alias = "the board name is another card's alias or former name"
    assert refused["Orbit 3"] == ("lab/orbit-3", alias)
    assert refused["Orbit Four"] == ("lab/orbit-four", alias)


def test_a_name_reused_by_two_cards_is_refused(monkeypatch, tmp_path: Path) -> None:
    root = _repo(tmp_path)
    one = _card(root, "nova", "Nova", rows=_stored_arena_row("Nova", "lab/nova"))
    two = _card(root, "nova-2", "Nova 2", rows=_stored_arena_row("Nova", "lab/nova-2"))

    # Nova has a webdev row already; the coding board is its first row there.
    report = _run(monkeypatch, tmp_path, root, [_dataset_row("Nova", 1200.0)])

    assert len(_rows(one)) == 1 and len(_rows(two)) == 1
    assert _refusals(report)["Nova"] == (
        "lab/nova", "the board name is reused by more than one card")


def test_the_verifier_reads_the_card_identity_not_the_copied_board_name() -> None:
    board = refresh.BoardReading(
        key="arena:arena_elo_overall", source_id=SOURCE_ID, benchmark_ids=frozenset({"x"}),
        source_url=PARQUET, observed_at=OBSERVED, rows=(), value_field="rating",
        snapshot_ref="sha256:" + "c" * 64,
    )
    row = {"id": "x", "benchmark_id": "arena_elo_overall", "model_id_as_evaluated": "Other",
           "score": 1.0}
    front = {"display_name": "Card Name", "version": "card-name-v1"}

    copied = refresh._claim("lab/card", front, row, board).names
    own = refresh._claim("lab/card", front, row, board, card_identity=True).names

    assert "Other" in copied
    assert own == ("Card Name", "card-name-v1", "card", "lab/Card Name")


def test_two_board_rows_that_name_one_card_file_neither(monkeypatch, tmp_path: Path) -> None:
    root = _repo(tmp_path)
    card = _card(root, "dup-model", "Dup Model")

    report = _run(monkeypatch, tmp_path, root, [
        _dataset_row("Dup Model", 1200.0), _dataset_row("dup-model", 1190.0),
    ])

    assert _rows(card) == []
    reasons = {entry.reason for entry in report.first_rows_refused}
    assert reasons == {"two board rows name this card"}
    assert len(report.first_rows_refused) == 2


def test_an_alias_and_an_unmatched_name_write_nothing(monkeypatch, tmp_path: Path) -> None:
    root = _repo(tmp_path)
    card = _card(root, "alias-card", "Alias Card", extra="aliases:\n- Alias Board Name\n")

    report = _run(monkeypatch, tmp_path, root, [
        _dataset_row("Alias Board Name", 1200.0), _dataset_row("Nobody Has This", 1100.0),
    ])

    assert _rows(card) == []
    assert report.first_rows == []
    assert report.first_rows_unmatched == {"arena:arena_elo_overall": 2}


def test_an_inactive_card_and_a_foreign_publisher_write_nothing(
    monkeypatch, tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    old = _card(root, "old-model", "Old Model", status="sunset")
    other = _card(root, "new-two", "New Two")

    report = _run(monkeypatch, tmp_path, root, [
        _dataset_row("Old Model", 1200.0), _dataset_row("otherlab/New Two", 1190.0),
    ])

    assert _rows(old) == [] and _rows(other) == []
    refused = _refusals(report)
    assert refused["Old Model"] == ("lab/old-model", "card is not active")
    assert refused["otherlab/New Two"] == ("lab/new-two", "publisher prefix is not the card's lab")


def test_a_publisher_prefix_that_is_the_cards_lab_files(monkeypatch, tmp_path: Path) -> None:
    root = _repo(tmp_path)
    card = _card(root, "new-two", "New Two")

    report = _run(monkeypatch, tmp_path, root, [_dataset_row("lab/New Two", 1190.0)])

    assert [entry.model_id for entry in report.first_rows] == ["lab/new-two"]
    assert len(_rows(card)) == 1


def test_a_card_that_already_has_a_row_on_the_board_gets_no_second_one(
    monkeypatch, tmp_path: Path,
) -> None:
    root = _repo(tmp_path)

    report = _run(monkeypatch, tmp_path, root, [_dataset_row("template", 1300.0)])

    assert report.first_rows == [] and report.first_rows_refused == []
    assert len(_rows(root / "models" / "lab" / "template.md")) == 1


def test_a_dry_run_reports_first_rows_and_writes_nothing(monkeypatch, tmp_path: Path) -> None:
    root = _repo(tmp_path)
    card = _card(root, "new-one", "New One")

    report = _run(monkeypatch, tmp_path, root, [_dataset_row("New One", 1200.0)], dry_run=True)

    assert [entry.model_id for entry in report.first_rows] == ["lab/new-one"]
    assert _rows(card) == []
    assert not (root / "verification" / "log.jsonl").exists()
    text = refresh.render_report(report)
    assert "## First rows (human review)" in text
    assert f"Label: `{refresh.FIRST_ROW_LABEL}`" in text


# --- cap --------------------------------------------------------------------------------------


def test_the_50th_first_row_is_written_and_the_51st_is_reported(
    monkeypatch, tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    cards = [_card(root, f"model-{index:02d}", f"Model {index:02d}") for index in range(51)]

    report = _run(monkeypatch, tmp_path, root, [
        _dataset_row(f"Model {index:02d}", 1000.0 + index) for index in range(51)
    ])

    assert refresh.FIRST_ROWS_PER_RUN == 50
    assert len(report.first_rows) == 50
    assert [entry.model_id for entry in report.first_rows_capped] == ["lab/model-50"]
    assert report.first_rows_capped[0].capped is True
    assert all(len(_rows(card)) == 1 for card in cards[:50])
    assert _rows(cards[50]) == []
    assert report.added == 50


def test_the_cap_reads_premier_cards_first_then_newest_release_then_board(
    monkeypatch, tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    (root / "premier" / "slice-1.yaml").write_text(
        "models:\n- model_id: lab/template\n- model_id: lab/old-premier\n", encoding="utf-8",
    )
    _card(root, "old-premier", "Old Premier", released="2024-01-01")
    _card(root, "newest", "Newest", released="2026-11-01")
    _card(root, "middle", "Middle", released="2025-06-01")
    _card(root, "undated", "Undated")
    monkeypatch.setattr(refresh, "FIRST_ROWS_PER_RUN", 3)

    report = _run(monkeypatch, tmp_path, root, [
        _dataset_row(name, 1100.0 + index)
        for index, name in enumerate(("Undated", "Middle", "Newest", "Old Premier"))
    ])

    assert [entry.model_id for entry in report.first_rows] == [
        "lab/old-premier", "lab/newest", "lab/middle"]
    assert [entry.model_id for entry in report.first_rows_capped] == ["lab/undated"]
    assert report.first_rows[0].premier is True


def _entry(model_id: str, benchmark: str, *, premier: bool = False, released: str = ""):
    return refresh.FirstRow(card="", model_id=model_id, benchmark=benchmark, board_name="",
                            match_key="", source="", score=0.0, evidence_date="",
                            premier=premier, release_date=released)


def test_the_order_is_a_constant_and_ties_break_on_board_then_model() -> None:
    entries = [
        _entry("lab/b", "arena_sc_math", released="2026-01-01"),
        _entry("lab/a", "arena_sc_math", released="2026-01-01"),
        _entry("lab/a", "arena_elo_coding", released="2026-01-01"),
        _entry("lab/p", "arena_webdev", premier=True),
        _entry("lab/n", "arena_webdev", released="2026-05-01"),
    ]

    assert refresh.FIRST_ROW_ORDER == ("premier", "release_date", "board")
    assert [(e.model_id, e.benchmark) for e in refresh.order_first_rows(entries)] == [
        ("lab/p", "arena_webdev"), ("lab/n", "arena_webdev"), ("lab/a", "arena_elo_coding"),
        ("lab/a", "arena_sc_math"), ("lab/b", "arena_sc_math")]
    by_board = refresh.order_first_rows(entries, ("board",))
    assert [(e.model_id, e.benchmark) for e in by_board][:2] == [
        ("lab/a", "arena_elo_coding"), ("lab/a", "arena_sc_math")]


# --- collector --------------------------------------------------------------------------------


def test_a_run_that_adds_rows_without_a_collector_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="must name its collector"):
        refresh.run(observed_at=OBSERVED, dry_run=True, root=tmp_path, first_rows=True)
    with pytest.raises(ValueError, match="must name its collector"):
        refresh.run(observed_at=OBSERVED, dry_run=True, root=tmp_path,
                    model_ids=("lab/x",), add_missing=True)


def test_an_add_missing_run_logs_its_own_collector(monkeypatch, tmp_path: Path) -> None:
    root = _repo(tmp_path)
    card = _card(root, "new-one", "New One")
    (root / "premier" / "slice-1.yaml").write_text(
        "models:\n- model_id: lab/template\n- model_id: lab/new-one\n", encoding="utf-8",
    )
    actor = VerificationActor(agent="fixture-signal", model_family="deterministic",
                              method="fixture@1")

    report = _run(monkeypatch, tmp_path, root, [_dataset_row("New One", 1200.0)],
                  first_rows=False, model_ids=("lab/new-one",), add_missing=True,
                  collector=actor)

    assert report.added == 1
    [row] = _rows(card)
    assert row["date_type"] == "published"
    assert "1 votes" not in row["configuration"] and "2222 votes" in row["configuration"]
    log = [json.loads(line) for line in
           (root / "verification" / "log.jsonl").read_text().splitlines()]
    assert {line["collector"]["agent"] for line in log} == {"fixture-signal"}


def test_the_add_missing_callers_pass_a_collector() -> None:
    for name in ("process_release_signals.py", "model_233_evidence.py"):
        tree = ast.parse((Path(refresh.ROOT) / "scripts" / name).read_text(encoding="utf-8"))
        calls = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "run"
            and any(k.arg == "add_missing" for k in node.keywords)
        ]
        assert calls, name
        assert all(any(k.arg == "collector" for k in call.keywords) for call in calls), name
    source = (Path(refresh.ROOT) / "scripts" / "model_233_evidence.py").read_text()
    assert "refresh_leaderboards.COLLECTOR =" not in source


# --- guard and merge class --------------------------------------------------------------------


def _filed(monkeypatch, tmp_path: Path, **options) -> tuple[Path, Path, Path]:
    root = _repo(tmp_path)
    card = _card(root, "new-one", "New One")
    before = tmp_path / "before"
    shutil.copytree(root, before)
    _run(monkeypatch, tmp_path, root, [_dataset_row("New One", 1200.0)], **options)
    return before, root, card


def test_the_guard_accepts_one_first_row_from_the_weekly_job_and_classes_it_human_review(
    monkeypatch, tmp_path: Path,
) -> None:
    before, after, _card_path = _filed(monkeypatch, tmp_path)

    result = refresh.check_score_only(before, after, first_rows=True, terms=TERMS)

    assert result.ok, result.errors
    assert result.classes["first_row"] == 1
    assert result.merge_class == refresh.FIRST_ROW_MERGE_CLASS == "human-review"
    assert result.labels == (refresh.FIRST_ROW_LABEL,)


def test_without_first_rows_the_guard_still_refuses_an_added_row(
    monkeypatch, tmp_path: Path,
) -> None:
    before, after, _card_path = _filed(monkeypatch, tmp_path)

    result = refresh.check_score_only(before, after)

    assert not result.ok
    assert any("evidence row count changed" in error for error in result.errors)


def test_the_guard_refuses_a_first_row_from_another_writer(monkeypatch, tmp_path: Path) -> None:
    actor = VerificationActor(agent="someone-else", model_family="deterministic", method="x@1")
    before, after, _card_path = _filed(monkeypatch, tmp_path, collector=actor)

    result = refresh.check_score_only(before, after, first_rows=True, terms=TERMS)

    assert not result.ok
    assert any("weekly refresh collector" in error for error in result.errors)


def test_the_guard_refuses_a_first_row_on_a_non_qualifying_host(
    monkeypatch, tmp_path: Path,
) -> None:
    before, after, _card_path = _filed(monkeypatch, tmp_path)

    for klass in ("unclear", "forbids", None):
        terms = {} if klass is None else {"huggingface.co": klass}
        result = refresh.check_score_only(before, after, first_rows=True, terms=terms)
        assert not result.ok
        assert any("host is" in error for error in result.errors), klass


def test_the_guard_refuses_any_other_change_beside_a_first_row(
    monkeypatch, tmp_path: Path,
) -> None:
    before, after, card = _filed(monkeypatch, tmp_path)
    text = card.read_text(encoding="utf-8")

    card.write_text(text.replace("display_name: New One", "display_name: New One X"),
                    encoding="utf-8")
    assert not refresh.check_score_only(before, after, first_rows=True, terms=TERMS).ok

    card.write_text(text.replace("unit: Arena score (Elo scale)", "unit: percent"),
                    encoding="utf-8")
    edited = refresh.check_score_only(before, after, first_rows=True, terms=TERMS)
    assert not edited.ok
    assert any("evidence id" in error for error in edited.errors)

    card.write_text(text.replace("Prose stays.", "Prose changed."), encoding="utf-8")
    assert not refresh.check_score_only(before, after, first_rows=True, terms=TERMS).ok

    card.write_text(text, encoding="utf-8")
    _card(after, "brand-new", "Brand New")
    created = refresh.check_score_only(before, after, first_rows=True, terms=TERMS)
    assert not created.ok
    assert any("card created" in error for error in created.errors)


def test_the_report_json_names_the_merge_class_and_label(monkeypatch, tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _card(root, "new-one", "New One")
    report = _run(monkeypatch, tmp_path, root, [_dataset_row("New One", 1200.0)])
    path = tmp_path / "report.json"

    refresh.write_report_json(path, report)

    payload = json.loads(path.read_text())
    assert payload["merge_class"] == "human-review"
    assert payload["labels"] == ["first-row"]
    assert [row["model_id"] for row in payload["first_rows"]] == ["lab/new-one"]
    plain = refresh.RefreshReport()
    refresh.write_report_json(path, plain)
    assert json.loads(path.read_text())["merge_class"] == "score-only"
    assert json.loads(path.read_text())["labels"] == []
