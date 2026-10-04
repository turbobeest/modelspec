"""Weekly live-board refreshes are deterministic and score-only (MODEL-124)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
import yaml

from decision.excluded import REMOVED_HOSTS
from scripts import accuracy
from scripts import refresh_leaderboards as refresh

FIXTURES = Path(__file__).parent / "fixtures" / "leaderboard_refresh"


def evidence(model: str, score: float) -> dict:
    return {
        "benchmark_id": "fixture_benchmark",
        "model_id_as_evaluated": model,
        "score": score,
        "unit": "percent",
        "source_url": "https://example.test/leaderboard.json",
        "source_kind": "benchmark_author",
        "evidence_date": "2026-09-01",
        "date_type": "evaluated",
        "verified_at": "2026-09-24",
        "id": f"lab/model#{model.casefold().replace(' ', '-')}"
    }


def test_fixture_board_changes_one_value_and_leaves_one_unchanged() -> None:
    body = (FIXTURES / "board.json").read_bytes()
    board = refresh.json_board(
        key="fixture",
        source_id="fixture-source",
        benchmark_ids={"fixture_benchmark"},
        source_url="https://example.test/leaderboard.json",
        body=body,
        observed_at="2026-09-25",
        value_field="score",
    )
    rows = [evidence("Changed Model", 80.0), evidence("Stable Model", 72.0)]

    changes, failures = refresh.plan_rows("lab/model", "models/lab/model.md", rows, board)

    assert failures == []
    assert [(c.model, c.old_value, c.new_value) for c in changes] == [
        ("Changed Model", 80.0, 81.5)
    ]


def test_model_missing_from_a_readable_board_is_reported_not_deleted() -> None:
    body = (FIXTURES / "board.json").read_bytes()
    board = refresh.json_board(
        key="fixture",
        source_id="fixture-source",
        benchmark_ids={"fixture_benchmark"},
        source_url="https://example.test/leaderboard.json",
        body=body,
        observed_at="2026-09-25",
        value_field="score",
    )

    changes, failures = refresh.plan_rows(
        "lab/missing", "models/lab/missing.md", [evidence("Missing Model", 70.0)], board
    )

    assert changes == []
    assert failures == [
        refresh.RowFailure(
            "lab/missing",
            "fixture_benchmark",
            "https://example.test/leaderboard.json",
            "no unique row for 'Missing Model'",
        )
    ]


def test_one_board_snapshot_cannot_mix_observation_dates() -> None:
    body = json.dumps({
        "rows": [
            {"model": "A", "score": 1, "observed_at": "2026-09-25"},
            {"model": "B", "score": 2, "observed_at": "2026-09-24"},
        ]
    }).encode()

    with pytest.raises(ValueError, match="one observation date"):
        refresh.json_board(
            key="mixed",
            source_id="fixture-source",
            benchmark_ids={"fixture_benchmark"},
            source_url="https://example.test/leaderboard.json",
            body=body,
            observed_at="2026-09-25",
            value_field="score",
        )


def test_arena_coverage_includes_the_webdev_dataset_config() -> None:
    assert refresh.ARENA_BOARDS["arena_webdev"] == ("webdev", "overall")
    assert refresh.ARENA_REVISION in refresh.readers.ARENA_URL


def test_arena_coverage_includes_refinement_slices() -> None:
    expected = {
        "arena_sc_english": ("text_style_control", "english"),
        "arena_sc_chinese": ("text_style_control", "chinese"),
        "arena_sc_japanese": ("text_style_control", "japanese"),
        "arena_sc_korean": ("text_style_control", "korean"),
        "arena_sc_russian": ("text_style_control", "russian"),
        "arena_sc_spanish": ("text_style_control", "spanish"),
        "arena_sc_german": ("text_style_control", "german"),
        "arena_sc_french": ("text_style_control", "french"),
        "arena_sc_polish": ("text_style_control", "polish"),
        "arena_sc_vision_ocr": ("vision_style_control", "ocr"),
        "arena_sc_vision_diagram": ("vision_style_control", "diagram"),
        "arena_sc_vision_homework": ("vision_style_control", "homework"),
        "arena_sc_document": ("document", "overall"),
        "arena_sc_industry_software_it_services": (
            "text_style_control",
            "industry_software_and_it_services",
        ),
        "arena_sc_industry_entertainment_sports_media": (
            "text_style_control",
            "industry_entertainment_and_sports_and_media",
        ),
        "arena_sc_industry_mathematical": (
            "text_style_control",
            "industry_mathematical",
        ),
        "arena_sc_factuality": ("text_factuality", "overall"),
    }

    assert expected.items() <= refresh.ARENA_BOARDS.items()


def test_score_only_check_refuses_a_card_creating_diff(tmp_path: Path) -> None:
    before = tmp_path / "before"
    after = tmp_path / "after"
    before.mkdir()
    after.mkdir()
    added = after / "models" / "lab" / "new.md"
    added.parent.mkdir(parents=True)
    added.write_text("---\nmodel_id: lab/new\n---\n", encoding="utf-8")

    result = refresh.check_score_only(before, after)

    assert not result.ok
    assert result.errors == ("card created: models/lab/new.md",)


def _card(observed_at: str, *, extra_row: bool = False) -> str:
    rows = f"""  - benchmark_id: fixture_benchmark
    model_id_as_evaluated: Stable Model
    score: 72.0
    unit: percent
    source_url: https://example.test/leaderboard.json
    source_kind: benchmark_author
    evidence_date: '2026-09-01'
    date_type: published
    observed_at: '{observed_at}'
    verified_at: '{observed_at}'
    id: lab/model#stable
    sources:
    - source_id: fixture-source
      snapshot_ref: sha256:{'a' * 64}
      cited_regions: [rows]
"""
    if extra_row:
        rows += rows.replace("fixture_benchmark", "added_benchmark").replace(
            "lab/model#stable", "lab/model#added"
        )
    return f"---\nmodel_id: lab/model\nbenchmarks:\n  evidence:\n{rows}---\nprose\n"


def _write_guard_cards(tmp_path: Path, before_text: str, after_text: str) -> tuple[Path, Path]:
    before, after = tmp_path / "before", tmp_path / "after"
    for root, text in ((before, before_text), (after, after_text)):
        card = root / "models" / "lab" / "model.md"
        card.parent.mkdir(parents=True)
        card.write_text(text, encoding="utf-8")
    return before, after


def test_score_only_check_accepts_observation_metadata_only_diff(tmp_path: Path) -> None:
    before, after = _write_guard_cards(
        tmp_path, _card("2026-08-01"), _card("2026-09-25")
    )

    assert refresh.check_score_only(before, after).ok


def test_score_only_check_refuses_an_evidence_row_addition(tmp_path: Path) -> None:
    before, after = _write_guard_cards(
        tmp_path, _card("2026-09-25"), _card("2026-09-25", extra_row=True)
    )

    result = refresh.check_score_only(before, after)

    assert not result.ok
    assert "evidence row count changed: models/lab/model.md" in result.errors


@pytest.mark.parametrize("url", [f"https://{host}/forbidden" for host in REMOVED_HOSTS])
def test_excluded_sources_are_refused_before_fetch(url: str) -> None:
    with pytest.raises(ValueError, match="excluded source"):
        refresh.require_allowed_source(url)


def test_private_weekly_workflow_uses_guard_token_and_audit_artifact() -> None:
    workflow = (Path(__file__).parents[1] / ".github" / "private-writers" /
                "leaderboard-refresh.yml").read_text(encoding="utf-8")

    assert "cron: 20 6 * * 1" in workflow
    assert "workflow_dispatch:" in workflow
    assert "secrets.GITHUB_TOKEN" in workflow
    assert "check_score_only" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "steps.result.outputs.updates != '0'" in workflow
    assert "len(report['changes']) + len(report['reconfirmed'])" in workflow
    assert "gh pr merge" not in workflow
    assert "signoff: true" in workflow
    assert "draft: true" not in workflow


def test_changed_row_goes_through_the_two_key_verifier(monkeypatch, tmp_path: Path) -> None:
    root = tmp_path / "repo"
    cache = tmp_path / "copies"
    (root / "premier").mkdir(parents=True)
    (root / "models" / "lab").mkdir(parents=True)
    (root / "registry").mkdir(parents=True)
    (root / "verification").mkdir(parents=True)
    (root / "premier" / "slice-1.yaml").write_text(
        "models:\n- model_id: lab/model\n", encoding="utf-8"
    )
    (root / "registry" / "sources.yaml").write_text(
        """schema_version: 1
sources:
- id: fixture-source
  url: https://example.test/leaderboard.json
  fetch: http
  normaliser: text-default
  cited_regions:
  - id: rows
    locator: {kind: page, value: ''}
""",
        encoding="utf-8",
    )
    card = root / "models" / "lab" / "model.md"
    card.write_text(
        """---
model_id: lab/model
display_name: Changed Model
version: Changed Model
benchmarks:
  evidence:
  - benchmark_id: fixture_benchmark
    model_id_as_evaluated: Changed Model
    score: 80.0
    unit: percent
    source_url: https://example.test/leaderboard.json
    source_kind: benchmark_author
    evidence_date: '2026-09-01'
    date_type: evaluated
    verified_at: '2026-09-24'
    id: lab/model#fixture#old
    sources:
    - source_id: fixture-source
      snapshot_ref: sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
      cited_regions: [rows]
---
""",
        encoding="utf-8",
    )
    store = refresh.CopyStore(cache)
    projection = refresh.readers.document(
        [{"model": "Changed Model", "score": "81.5%", "date": "2026-09-01"}],
        url="https://example.test/leaderboard.json",
        page_ref="sha256:" + "b" * 64,
        read_date="2026-09-25",
        note="fixture",
    )
    board = refresh._reading_from_projection(
        key="fixture",
        source_id="fixture-source",
        benchmarks=("fixture_benchmark",),
        source_url="https://example.test/leaderboard.json",
        projected=projection,
        observed_at="2026-09-25",
        value_field="score",
        store=store,
        card_urls=("https://example.test/leaderboard.json",),
    )
    monkeypatch.setattr(refresh, "collect_readings", lambda *_: ([board], []))

    report = refresh.run(
        observed_at="2026-09-25", dry_run=False, root=root, source_cache=cache
    )

    assert len(report.changes) == 1
    assert report.quarantined == []
    changed = card.read_text(encoding="utf-8")
    assert "score: 81.5" in changed
    assert "verified_at: '2026-09-25'" in changed
    log = json.loads((root / "verification" / "log.jsonl").read_text(encoding="utf-8"))
    assert log["outcome"] == "verified"
    assert log["verifier"]["model_family"] == "deterministic"


def test_new_card_gets_a_matching_registered_board_evidence_row(
    monkeypatch, tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    cache = tmp_path / "copies"
    (root / "models" / "lab").mkdir(parents=True)
    (root / "registry").mkdir(parents=True)
    (root / "verification").mkdir(parents=True)
    (root / "registry" / "sources.yaml").write_text(
        """schema_version: 1
sources:
- id: fixture-source
  url: https://example.test/leaderboard.json
  fetch: http
  normaliser: text-default
  cited_regions:
  - id: rows
    locator: {kind: page, value: ''}
""",
        encoding="utf-8",
    )
    card = root / "models" / "lab" / "new.md"
    card.write_text(
        """---
model_id: lab/new
display_name: New Model
version: new-model
benchmarks:
  scores: {}
  evidence: []
---
""",
        encoding="utf-8",
    )
    template = root / "models" / "lab" / "template.md"
    template.write_text(
        _card("2026-09-25").replace("lab/model", "lab/template").replace(
            "Stable Model", "Template Model"
        ).replace("prose\n", ""),
        encoding="utf-8",
    )
    store = refresh.CopyStore(cache)
    projection = refresh.readers.document(
        [{"model": "New Model", "score": "81.5%"}],
        url="https://example.test/leaderboard.json",
        page_ref="sha256:" + "b" * 64,
        read_date="2026-09-26",
        note="fixture",
    )
    board = refresh._reading_from_projection(
        key="fixture", source_id="fixture-source", benchmarks=("fixture_benchmark",),
        source_url="https://example.test/leaderboard.json", projected=projection,
        observed_at="2026-09-26", value_field="score", store=store,
    )
    monkeypatch.setattr(refresh, "collect_readings", lambda *_: ([board], []))

    report = refresh.run(
        observed_at="2026-09-26", dry_run=False, root=root, source_cache=cache,
        model_ids=("lab/new",), add_missing=True,
    )

    front = yaml.safe_load(card.read_text(encoding="utf-8").split("---", 2)[1])
    assert len(front["benchmarks"]["evidence"]) == 1
    row = front["benchmarks"]["evidence"][0]
    assert (row["benchmark_id"], row["score"], row["unit"]) == (
        "fixture_benchmark", 81.5, "percent"
    )
    assert row["source_url"] == "https://example.test/leaderboard.json"
    assert report.added == 1
    assert report.quarantined == []


def test_added_row_takes_the_board_rows_date_and_keeps_the_card_text(
    monkeypatch, tmp_path: Path,
) -> None:
    """MODEL-233: a board row's own date is the evidence date, as for an update.

    The add path stamped the observation date, so the verifier, which reads the
    row's date from the projection, quarantined every added row; and it left out
    ``measured_by``, which the snapshot requires. The card's existing text is
    appended to, not re-serialised.
    """
    root = tmp_path / "repo"
    cache = tmp_path / "copies"
    (root / "models" / "lab").mkdir(parents=True)
    (root / "registry").mkdir(parents=True)
    (root / "verification").mkdir(parents=True)
    (root / "registry" / "sources.yaml").write_text(
        """schema_version: 1
sources:
- id: fixture-source
  url: https://example.test/leaderboard.json
  fetch: http
  normaliser: text-default
  cited_regions:
  - id: rows
    locator: {kind: page, value: ''}
""",
        encoding="utf-8",
    )
    card = root / "models" / "lab" / "new.md"
    before = _card("2026-09-01").replace("fixture_benchmark", "other_benchmark").replace(
        "lab/model", "lab/new").replace("Stable Model", "New Model").replace(
        "model_id: lab/new\n", "model_id: lab/new\ndisplay_name: New Model  # kept\n")
    card.write_text(before, encoding="utf-8")
    (root / "models" / "lab" / "template.md").write_text(
        _card("2026-09-25").replace("lab/model", "lab/template").replace(
            "Stable Model", "Template Model"
        ).replace("prose\n", ""),
        encoding="utf-8",
    )
    store = refresh.CopyStore(cache)
    projection = refresh.readers.document(
        [{"model": "New Model", "score": "81.5%", "date": "2026-09-13"}],
        url="https://example.test/leaderboard.json",
        page_ref="sha256:" + "b" * 64,
        read_date="2026-09-26",
        note="fixture",
    )
    board = refresh._reading_from_projection(
        key="fixture", source_id="fixture-source", benchmarks=("fixture_benchmark",),
        source_url="https://example.test/leaderboard.json", projected=projection,
        observed_at="2026-09-26", value_field="score", store=store,
    )
    monkeypatch.setattr(refresh, "collect_readings", lambda *_: ([board], []))

    report = refresh.run(
        observed_at="2026-09-26", dry_run=False, root=root, source_cache=cache,
        model_ids=("lab/new",), add_missing=True,
    )

    after = card.read_text(encoding="utf-8")
    added = yaml.safe_load(after.split("---", 2)[1])["benchmarks"]["evidence"][-1]
    assert (added["benchmark_id"], added["evidence_date"], added["observed_at"]) == (
        "fixture_benchmark", "2026-09-13", "2026-09-26"
    )
    assert (added["measured_by"], added["effort"], added["harness"]) == (
        "benchmark_author", None, None
    )
    assert report.added == 1
    assert report.quarantined == []
    assert after.startswith(before.removesuffix("---\nprose\n"))
    assert after.endswith("---\nprose\n")


def test_signal_refresh_changes_only_the_resolved_model(monkeypatch, tmp_path: Path) -> None:
    root = tmp_path / "repo"
    cache = tmp_path / "copies"
    (root / "models" / "lab").mkdir(parents=True)
    (root / "registry").mkdir(parents=True)
    (root / "verification").mkdir(parents=True)
    (root / "registry" / "sources.yaml").write_text(
        """schema_version: 1
sources:
- id: fixture-source
  url: https://example.test/leaderboard.json
  fetch: http
  normaliser: text-default
  cited_regions:
  - id: rows
    locator: {kind: page, value: ''}
""",
        encoding="utf-8",
    )
    target = root / "models" / "lab" / "target.md"
    other = root / "models" / "lab" / "other.md"
    target.write_text(
        _card("2026-08-01").replace("lab/model", "lab/target").replace(
            "Stable Model", "Target Model"
        ).replace("prose\n", ""),
        encoding="utf-8",
    )
    other.write_text(
        _card("2026-08-01").replace("lab/model", "lab/other").replace(
            "Stable Model", "Other Model"
        ).replace("prose\n", ""),
        encoding="utf-8",
    )
    store = refresh.CopyStore(cache)
    projection = refresh.readers.document(
        [
            {"model": "Target Model", "score": "73.0%", "date": "2026-09-01"},
            {"model": "Other Model", "score": "99.0%", "date": "2026-09-01"},
        ],
        url="https://example.test/leaderboard.json",
        page_ref="sha256:" + "b" * 64,
        read_date="2026-09-25",
        note="fixture",
    )
    board = refresh._reading_from_projection(
        key="fixture", source_id="fixture-source", benchmarks=("fixture_benchmark",),
        source_url="https://example.test/leaderboard.json", projected=projection,
        observed_at="2026-09-25", value_field="score", store=store,
    )
    monkeypatch.setattr(refresh, "collect_readings", lambda *_: ([board], []))
    other_before = other.read_bytes()

    report = refresh.run(
        observed_at="2026-09-25", dry_run=False, root=root, source_cache=cache,
        model_ids=("lab/target",),
    )

    assert [(change.model_id, change.new_value) for change in report.changes] == [
        ("lab/target", 73.0)
    ]
    assert other.read_bytes() == other_before


def test_confirmed_row_advances_observation_date_and_freshness(monkeypatch, tmp_path: Path) -> None:
    root = tmp_path / "repo"
    cache = tmp_path / "copies"
    (root / "premier").mkdir(parents=True)
    (root / "models" / "lab").mkdir(parents=True)
    (root / "registry").mkdir(parents=True)
    (root / "verification").mkdir(parents=True)
    (root / "premier" / "slice-1.yaml").write_text(
        "models:\n- model_id: lab/model\n", encoding="utf-8"
    )
    (root / "registry" / "sources.yaml").write_text(
        """schema_version: 1
sources:
- id: fixture-source
  url: https://example.test/leaderboard.json
  volatility: live
  fetch: http
  normaliser: text-default
  cited_regions:
  - id: rows
    locator: {kind: page, value: ''}
""",
        encoding="utf-8",
    )
    card = root / "models" / "lab" / "model.md"
    card.write_text(_card("2026-08-01").replace("prose\n", ""), encoding="utf-8")
    store = refresh.CopyStore(cache)
    projection = refresh.readers.document(
        [{"model": "Stable Model", "score": "72.0%", "date": "2026-09-01"}],
        url="https://example.test/leaderboard.json",
        page_ref="sha256:" + "b" * 64,
        read_date="2026-09-25",
        note="fixture",
    )
    board = refresh._reading_from_projection(
        key="fixture",
        source_id="fixture-source",
        benchmarks=("fixture_benchmark",),
        source_url="https://example.test/leaderboard.json",
        projected=projection,
        observed_at="2026-09-25",
        value_field="score",
        store=store,
    )
    monkeypatch.setattr(refresh, "collect_readings", lambda *_: ([board], []))

    report = refresh.run(
        observed_at="2026-09-25", dry_run=False, root=root, source_cache=cache
    )

    front = refresh._front(card)
    row = front["benchmarks"]["evidence"][0]
    assert report.changes == []
    assert report.boards["fixture"]["models_reconfirmed"] == 1
    assert str(row["observed_at"]) == "2026-09-25"
    assert row["sources"][0]["snapshot_ref"] == board.snapshot_ref
    assert (root / "verification" / "log.jsonl").read_text().count("\n") == 1

    class Row:
        benchmark_id = "fixture_benchmark"
        value = 72.0
        date = date(2026, 9, 1)
        date_type = "published"
        source_kind = "benchmark_author"
        source_ids = ("fixture-source",)
        verified = True
        record_id = "lab/model#stable"

    class Snapshot:
        def candidates(self): return ("lab/model",)
        def lifecycle(self, _candidate): return "active"
        def model_of(self, candidate): return candidate
        def fact(self, _candidate, _facet):
            return type("Fact", (), {"value": "2026-09-01"})()
        def domain_ids(self): return ("software_engineering",)
        def evidence_for_domain(self, _candidate, _domain): return (Row(),)
        def record(self, _record_id): return row

    sources = refresh.load_sources(root / "registry" / "sources.yaml")
    result = accuracy.check_freshness(
        Snapshot(),
        as_of=date(2026, 10, 24),
        config=accuracy.load_config(Path("accuracy.yaml")).freshness,
        sources=sources,
    )
    assert result.status == "pass"
    assert result.counts["live_readings"] == 1


def test_mteb_row_without_its_own_date_uses_the_board_observation_date(
    monkeypatch, tmp_path: Path
) -> None:
    root = tmp_path / "repo"
    cache = tmp_path / "copies"
    (root / "premier").mkdir(parents=True)
    (root / "models" / "lab").mkdir(parents=True)
    (root / "registry").mkdir(parents=True)
    (root / "verification").mkdir(parents=True)
    (root / "premier" / "slice-1.yaml").write_text(
        "models:\n- model_id: lab/embedding-model\n", encoding="utf-8"
    )
    source_url = "https://example.test/mteb/scores"
    (root / "registry" / "sources.yaml").write_text(
        f"""schema_version: 1
sources:
- id: fixture-mteb
  url: {source_url}
  volatility: live
  fetch: http
  normaliser: text-default
  cited_regions:
  - id: rows
    locator: {{kind: page, value: ''}}
""",
        encoding="utf-8",
    )
    card = root / "models" / "lab" / "embedding-model.md"
    card.write_text(
        f"""---
model_id: lab/embedding-model
display_name: Fixture Embedding Model
version: Fixture/Embedding-Model
benchmarks:
  evidence:
  - benchmark_id: mteb_eng_v2
    model_id_as_evaluated: Fixture/Embedding-Model
    score: 75.98
    unit: percent
    source_url: {source_url}
    source_kind: benchmark_author
    evidence_date: '2026-09-24'
    date_type: published
    observed_at: '2026-09-24'
    verified_at: '2026-09-24'
    id: lab/embedding-model#mteb_eng_v2#fixture
    sources:
    - source_id: fixture-mteb
      snapshot_ref: sha256:{'a' * 64}
      cited_regions: [rows]
---
""",
        encoding="utf-8",
    )
    raw = (FIXTURES / "mteb_without_row_dates.json").read_bytes()
    store = refresh.CopyStore(cache)
    projection = refresh.readers.project_mteb(
        raw,
        url=source_url,
        page_ref="sha256:" + "b" * 64,
        read_date="2026-09-28",
    )
    board = refresh._reading_from_projection(
        key="mteb:mteb_eng_v2",
        source_id="fixture-mteb",
        benchmarks=("mteb_eng_v2",),
        source_url=source_url,
        projected=projection,
        observed_at="2026-09-28",
        value_field="mean_task",
        fraction=True,
        store=store,
    )
    monkeypatch.setattr(refresh, "collect_readings", lambda *_: ([board], []))

    report = refresh.run(
        observed_at="2026-09-28", dry_run=False, root=root, source_cache=cache
    )

    row = refresh._front(card)["benchmarks"]["evidence"][0]
    verification = json.loads(
        (root / "verification" / "log.jsonl").read_text(encoding="utf-8")
    )
    assert report.quarantined == []
    assert verification["outcome"] == "verified"
    assert str(row["evidence_date"]) == "2026-09-28"
    assert str(row["observed_at"]) == "2026-09-28"


def test_unread_board_keeps_the_old_observation_date(monkeypatch, tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "premier").mkdir(parents=True)
    (root / "models" / "lab").mkdir(parents=True)
    (root / "registry").mkdir(parents=True)
    (root / "verification").mkdir(parents=True)
    (root / "premier" / "slice-1.yaml").write_text(
        "models:\n- model_id: lab/model\n", encoding="utf-8"
    )
    (root / "registry" / "sources.yaml").write_text(
        "schema_version: 1\nsources: []\n", encoding="utf-8"
    )
    card = root / "models" / "lab" / "model.md"
    card.write_text(_card("2026-08-01").replace("prose\n", ""), encoding="utf-8")
    failure = refresh.RowFailure("*", "fixture_benchmark", "https://example.test", "unread")
    monkeypatch.setattr(refresh, "collect_readings", lambda *_: ([], [failure]))

    report = refresh.run(observed_at="2026-09-25", dry_run=False, root=root)

    assert report.failures == [failure]
    assert str(refresh._front(card)["benchmarks"]["evidence"][0]["observed_at"]) == "2026-08-01"


# ── Finance Benchmark v2 (MODEL-232) ────────────────────────────────────────

FINANCE_CARDS = (
    "anthropic/claude-fable-5", "anthropic/claude-opus-4-6", "anthropic/claude-opus-4-7",
    "deepseek/deepseek-v4-pro", "google/gemini-3-5-flash", "moonshot/kimi-k3",
    "openai/gpt-5-4", "openai/gpt-5-6-sol",
)
REPO_ROOT = Path(__file__).resolve().parents[1]


def _finance_repo(tmp_path: Path, cards: tuple[str, ...] = FINANCE_CARDS) -> Path:
    """The given lineup cards (by default those with finance_benchmark_v2 rows) and the
    real registry."""
    root = tmp_path / "repo"
    (root / "premier").mkdir(parents=True)
    (root / "registry").mkdir()
    (root / "verification").mkdir()
    (root / "premier" / "slice-1.yaml").write_text(
        "models:\n" + "".join(f"- model_id: {m}\n" for m in cards), encoding="utf-8")
    (root / "registry" / "sources.yaml").write_bytes(
        (REPO_ROOT / "registry" / "sources.yaml").read_bytes())
    for model_id in cards:
        rel = Path("models") / f"{model_id}.md"
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes((REPO_ROOT / rel).read_bytes())
    return root


def _replay_finbenchmark(monkeypatch) -> None:
    """Serve the 2026-09-29 finbenchmark.ai page; every other board is unreachable."""
    import gzip

    page = gzip.decompress((FIXTURES / "finbenchmark_2026-09-29.html.gz").read_bytes())

    def fetch(url: str) -> bytes:
        if url == refresh.FINBENCH_URL:
            return page
        raise OSError(f"offline replay: {url}")

    monkeypatch.setattr(refresh, "_fetch", fetch)


def _finance_row(card: Path) -> dict:
    return next(row for row in refresh._front(card)["benchmarks"]["evidence"]
                if row["benchmark_id"] == "finance_benchmark_v2")


def test_replayed_refresh_reconfirms_every_finance_benchmark_row(
    monkeypatch, tmp_path: Path,
) -> None:
    root = _finance_repo(tmp_path)
    before = {m: _finance_row(root / "models" / f"{m}.md") for m in FINANCE_CARDS}
    _replay_finbenchmark(monkeypatch)

    report = refresh.run(observed_at="2026-09-29", dry_run=False, root=root,
                         source_cache=tmp_path / "copies")

    assert report.boards["finbenchmark"] == {
        "models_read": 8, "models_reconfirmed": 8, "values_changed": 0, "failures": [],
    }
    assert report.changes == []
    assert report.quarantined == []
    assert not [f for f in report.failures if f.source == refresh.FINBENCH_URL]
    for model_id in FINANCE_CARDS:
        row = _finance_row(root / "models" / f"{model_id}.md")
        assert row["score"] == before[model_id]["score"]
        assert str(row["evidence_date"]) == str(before[model_id]["evidence_date"])
        assert str(row["observed_at"]) == "2026-09-29"
        assert row["sources"][0]["source_id"] == "model-192-finance-benchmark-v2"
        assert row["sources"][0]["snapshot_ref"] != before[model_id]["sources"][0]["snapshot_ref"]
    log = [json.loads(line) for line in
           (root / "verification" / "log.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [entry["outcome"] for entry in log] == ["verified"] * 8


def test_replayed_refresh_moves_a_changed_finance_score_through_verification(
    monkeypatch, tmp_path: Path,
) -> None:
    root = _finance_repo(tmp_path)
    card = root / "models" / "openai" / "gpt-5-4.md"
    card.write_text(card.read_text(encoding="utf-8").replace("score: 63.0137", "score: 61.6438"),
                    encoding="utf-8")
    _replay_finbenchmark(monkeypatch)

    report = refresh.run(observed_at="2026-09-29", dry_run=False, root=root,
                         source_cache=tmp_path / "copies")

    assert [(c.model_id, c.old_value, c.new_value) for c in report.changes] == [
        ("openai/gpt-5-4", 61.6438, 63.0137)
    ]
    assert report.quarantined == []
    assert _finance_row(card)["score"] == 63.0137


def _rsc_page(payload: str) -> str:
    return f'<script>self.__next_f.push([1,{json.dumps(payload)}])</script>'


def test_finance_projection_keeps_only_v2_rows() -> None:
    run = {"provider": "lab", "harness_version": "0.2.0",
           "completed_at": "2026-07-01T00:00:00+00:00"}
    rows = [
        {**run, "model_name": "m", "task_set_version": "v2", "pass_at_1": 0.5},
        {**run, "model_name": "m", "task_set_version": "v3", "pass_at_1": 0.9},
        {**run, "model_name": "m", "task_set_version": "v2.1", "pass_at_1": 0.8},
    ]
    projected = json.loads(refresh._project_finbenchmark(
        _rsc_page('["$","$L12",null,{"rows":' + json.dumps(rows) + "}]"),
        url=refresh.FINBENCH_URL, page_ref="sha256:" + "c" * 64, observed_at="2026-09-29",
    ))

    assert projected["rows"] == [{"model": "lab/m", "pass_at_1": 50.0, "date": "2026-07-01",
                                  "harness": "finance-benchmark 0.2.0", "task_set_version": "v2"}]


@pytest.mark.parametrize("payload", ['{"rows":[]}', '{"other":1}'])
def test_finance_projection_refuses_a_page_without_run_records(payload: str) -> None:
    with pytest.raises(ValueError, match="Finance Benchmark"):
        refresh._project_finbenchmark(_rsc_page(payload), url=refresh.FINBENCH_URL,
                                      page_ref="sha256:" + "c" * 64, observed_at="2026-09-29")


@pytest.mark.parametrize("benchmark,column,value,unit,expected", [
    ("fixture_reranking", "reranking", 0.6583, "percent", 65.83),
    ("followir", "mean_task", -0.029, "p-MRR (x100)", -2.9),
])
def test_board_seeds_a_benchmark_no_card_carries_yet(
    monkeypatch, tmp_path: Path, benchmark, column, value, unit, expected,
) -> None:
    root = tmp_path / "repo"
    cache = tmp_path / "copies"
    (root / "models" / "lab").mkdir(parents=True)
    (root / "registry").mkdir(parents=True)
    (root / "verification").mkdir(parents=True)
    (root / "benchmarks").mkdir()
    (root / "benchmarks" / f"{benchmark}.md").write_text(
        '---\n' + yaml.safe_dump({"metric": {"unit": unit, "max_score": 100,
                                           "min_score": -100 if benchmark == "followir" else 0}})
        + '---\n', encoding="utf-8",
    )
    url = "https://example.test/mteb/scores"
    (root / "registry" / "sources.yaml").write_text(
        f"""schema_version: 1
sources:
- id: fixture-mteb
  url: {url}
  fetch: http
  normaliser: text-default
  cited_regions:
  - id: rows
    locator: {{kind: page, value: ''}}
""",
        encoding="utf-8",
    )
    for model_id, display in (("lab/reranker-x", "Reranker X"), ("lab/embedder", "Embedder")):
        (root / "models" / f"{model_id}.md").write_text(
            f"---\nmodel_id: {model_id}\ndisplay_name: {display}\n"
            "benchmarks:\n  scores: {}\n  evidence: []\n---\n",
            encoding="utf-8",
        )
    raw = json.dumps({"rows": [
        {"model": {"name": "Lab/Reranker-X"}, "meanTask": value if column == "mean_task" else None,
         "scoresByTaskType": {"Reranking": value} if column == "reranking" else {}},
        {"model": {"name": "Lab/Embedder"}, "scoresByTaskType": {}},
    ]}).encode()
    store = refresh.CopyStore(cache)
    board = refresh._reading_from_projection(
        key=f"mteb:{benchmark}", source_id="fixture-mteb",
        benchmarks=(benchmark,), source_url=url,
        projected=refresh.readers.project_mteb(raw, url=url, page_ref="sha256:" + "c" * 64,
                                               read_date="2026-09-29"),
        observed_at="2026-09-29", value_field=column, fraction=True, store=store,
        card_urls=(url,), row_template={**refresh.MTEB_ROW, "unit": unit},
    )
    monkeypatch.setattr(refresh, "collect_readings", lambda *_: ([board], []))

    report = refresh.run(
        observed_at="2026-09-29", dry_run=False, root=root, source_cache=cache,
        model_ids=("lab/reranker-x", "lab/embedder"), add_missing=True,
    )

    added = refresh._front(root / "models" / "lab" / "reranker-x.md")["benchmarks"]["evidence"]
    assert [(r["benchmark_id"], r["model_id_as_evaluated"], r["unit"],
             r["source_kind"], r["source_url"]) for r in added] == [
        (benchmark, "Lab/Reranker-X", unit, "benchmark_author", url)
    ]
    assert added[0]["score"] == pytest.approx(expected)
    assert refresh._front(root / "models" / "lab" / "embedder.md")["benchmarks"]["evidence"] == []
    assert (report.added, report.failures, report.quarantined) == (1, [], [])
    log = json.loads((root / "verification" / "log.jsonl").read_text(encoding="utf-8"))
    assert (log["outcome"], log["verifier"]["model_family"]) == ("verified", "deterministic")


def test_weekly_refresh_collects_mteb_subboards(monkeypatch, tmp_path: Path) -> None:
    urls = {url for _, url, _, _, _ in refresh.MTEB_BOARDS}
    fetched = []

    def fetch(url):
        if url not in urls:
            raise ValueError("board outside this fixture")
        fetched.append(url)
        value = -0.029 if url.endswith("FollowIR/scores") else 0.6583
        return json.dumps({"rows": [{
            "model": {"name": "Lab/Reranker-X"}, "meanTask": value,
            "scoresByTaskType": {"Reranking": value, "Retrieval": value},
        }]}).encode()

    monkeypatch.setattr(refresh, "_fetch", fetch)
    boards, failures = refresh.collect_readings("2026-09-29", refresh.CopyStore(tmp_path), ())

    assert set(fetched) == urls
    assert len(fetched) == len(urls)
    assert not [f for f in failures if f.benchmark.startswith("mteb:")]
    readings = {next(iter(board.benchmark_ids)): board for board in boards}
    assert set(readings) == {
        "mteb_eng_v2", "mteb_v2_reranking", "mteb_v2_retrieval", "mteb_multilingual_v2",
        "mteb_multilingual_v2_reranking", "mteb_cmn_v1_reranking", "followir",
    }
    for benchmark, source, unit, expected in [
        ("mteb_multilingual_v2_reranking", "model-143-evidence-mteb-multilingual-v2-json",
         "percent", 65.83),
        ("mteb_cmn_v1_reranking", "model-242-mteb-cmn-v1-json", "percent", 65.83),
        ("followir", "model-242-mteb-followir-json", "p-MRR (x100)", -2.9),
    ]:
        board = readings[benchmark]
        assert board.source_id == source
        assert board.row_template == {"unit": unit, "source_kind": "benchmark_author"}
        assert refresh._value(board, board.rows[0], unit) == pytest.approx(expected)


MATHARENA_CARDS = (
    "anthropic/claude-fable-5-1", "anthropic/claude-opus-5-5", "deepseek/deepseek-flash",
    "google/gemini-3-8-flash", "meta/muse-spark-1-3", "openai/gpt-6-astra",
    "openai/gpt-6-sol", "xai/grok-4-7",
)


def _replay_matharena(monkeypatch) -> None:
    """Serve the 2026-09-29 MathArena Overall tables; every other board is unreachable."""
    import gzip

    pages = {url: gzip.decompress(
        (FIXTURES / f"matharena_{url.rsplit('/', 1)[1]}_2026-09-29.json.gz").read_bytes())
        for _, url in refresh.MATHARENA_BOARDS.values()}
    pages[refresh.readers.MATHARENA_INDEX] = gzip.decompress(
        (FIXTURES / "matharena_index_2026-09-29.html.gz").read_bytes())

    def fetch(url: str) -> bytes:
        if url in pages:
            return pages[url]
        raise OSError(f"offline replay: {url}")

    monkeypatch.setattr(refresh, "_fetch", fetch)


def test_a_later_matharena_reread_keeps_every_flagged_row_admitted(
    monkeypatch, tmp_path: Path,
) -> None:
    """A re-read re-dates the row, so its only verification is the refresh's own.

    The rows carry MathArena's contamination warning. The snapshot counts a
    verification only when it binds the score and the flags together.
    """
    from decision.model import evidence_verification_value, value_hash

    root = _finance_repo(tmp_path, MATHARENA_CARDS)
    _replay_matharena(monkeypatch)

    report = refresh.run(observed_at="2026-10-06", dry_run=False, root=root,
                         source_cache=tmp_path / "copies")

    for benchmark in ("brokenarxiv", "arxivmath"):
        assert report.boards[f"matharena:{benchmark}"] == {
            "models_read": 8, "models_reconfirmed": 8, "values_changed": 0, "failures": [],
        }
    assert report.changes == []
    assert report.quarantined == []
    sol = {row["benchmark_id"]: row for row in
           refresh._front(root / "models" / "openai" / "gpt-6-sol.md")["benchmarks"]["evidence"]}
    assert (sol["brokenarxiv"]["score"], sol["arxivmath"]["score"]) == (86.98, 91.32)
    assert sol["brokenarxiv"]["quality_flags"] == ["contamination_warning"]
    log = [json.loads(line) for line in
           (root / "verification" / "log.jsonl").read_text(encoding="utf-8").splitlines()]
    counted = {(e["target"]["id"], e["target"]["value_hash"]) for e in log
               if e["outcome"] == "verified"}
    reread = [row for model_id in MATHARENA_CARDS
              for row in refresh._front(root / "models" / f"{model_id}.md")
              ["benchmarks"]["evidence"] if row["benchmark_id"] in ("brokenarxiv", "arxivmath")]
    assert len(reread) == 16
    assert {str(row["evidence_date"]) for row in reread} == {"2026-10-06"}
    assert [row["id"] for row in reread
            if (row["id"], value_hash(evidence_verification_value(row))) not in counted] == []


def test_matharena_research_boards_are_registered_sources() -> None:
    from decision.sources import load_sources

    registered = load_sources(REPO_ROOT / "registry" / "sources.yaml")
    for source_id, url in refresh.MATHARENA_BOARDS.values():
        assert str(registered[source_id].url) == url


def test_the_matharena_index_marks_only_retired_competitions() -> None:
    import gzip

    index = gzip.decompress(
        (FIXTURES / "matharena_index_2026-09-29.html.gz").read_bytes()).decode()
    assert refresh.readers.matharena_deprecated(index, "aime--aime_2026") is True
    assert refresh.readers.matharena_deprecated(index, "overall--brokenarxiv") is False
    assert refresh.readers.matharena_deprecated(index, "overall--arxivmath") is False
    with pytest.raises(ValueError, match="no competition"):
        refresh.readers.matharena_deprecated(index, "aime--aime_2099")
