"""Weekly live-board refreshes are deterministic and score-only (MODEL-124)."""

from __future__ import annotations

import json
import shutil
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
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([board], []))

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
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([board], []))

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
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([board], []))

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
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([board], []))
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
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([board], []))

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
    source_url = refresh.readers.MTEB_URL
    (root / "registry" / "sources.yaml").write_text(
        f"""schema_version: 1
sources:
- id: fixture-mteb
  url: "{source_url}"
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
    source_url: "{source_url}"
    source_kind: benchmark_author
    evidence_date: '2026-09-24'
    date_type: published
    observed_at: '2026-09-24'
    verified_at: '2026-09-24'
    configuration: MTEB leaderboard backend JSON read 2026-09-24; tasks updated 2026-09-10.
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
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([board], []))

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
    assert row["date_type"] == "evaluated"
    assert row["configuration"] == (
        "MTEB leaderboard backend JSON read 2026-09-28; tasks updated 2026-09-10."
    )


def test_source_dated_row_keeps_its_read_date_and_date_type(
    monkeypatch, tmp_path: Path,
) -> None:
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
    card.write_text(
        """---
model_id: lab/model
display_name: Stable Model
version: Stable Model
benchmarks:
  evidence:
  - benchmark_id: fixture_benchmark
    model_id_as_evaluated: Stable Model
    score: 72.0
    unit: percent
    source_url: https://example.test/leaderboard.json
    source_kind: benchmark_author
    evidence_date: '2026-09-01'
    date_type: published
    observed_at: '2026-09-24'
    verified_at: '2026-09-24'
    configuration: Board row read 2026-09-24; published 2026-09-01.
    id: lab/model#stable
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
        [{"model": "Stable Model", "score": "72.0%", "date": "2026-09-01"}],
        url="https://example.test/leaderboard.json",
        page_ref="sha256:" + "b" * 64,
        read_date="2026-09-28",
        note="fixture",
    )
    board = refresh._reading_from_projection(
        key="fixture", source_id="fixture-source", benchmarks=("fixture_benchmark",),
        source_url="https://example.test/leaderboard.json", projected=projection,
        observed_at="2026-09-28", value_field="score", store=store,
    )
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([board], []))

    report = refresh.run(
        observed_at="2026-09-28", dry_run=False, root=root, source_cache=cache
    )

    row = refresh._front(card)["benchmarks"]["evidence"][0]
    assert report.quarantined == []
    assert str(row["evidence_date"]) == "2026-09-01"
    assert str(row["observed_at"]) == "2026-09-28"
    assert row["date_type"] == "published"
    assert row["configuration"] == "Board row read 2026-09-24; published 2026-09-01."


def _run_one_row_refresh(
    monkeypatch, tmp_path: Path, *,
    board_row: dict, configuration: str, evidence_date: str, card_observed_at: str,
    refresh_observed_at: str,
    source_url: str = "https://example.test/leaderboard.json",
) -> dict:
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
        f"""schema_version: 1
sources:
- id: fixture-source
  url: "{source_url}"
  volatility: live
  fetch: http
  normaliser: text-default
  cited_regions:
  - id: rows
    locator: {{kind: page, value: ''}}
""",
        encoding="utf-8",
    )
    card = root / "models" / "lab" / "model.md"
    card.write_text(
        f"""---
model_id: lab/model
display_name: Stable Model
version: Stable Model
benchmarks:
  evidence:
  - benchmark_id: fixture_benchmark
    model_id_as_evaluated: Stable Model
    score: 72.0
    unit: percent
    source_url: "{source_url}"
    source_kind: benchmark_author
    evidence_date: '{evidence_date}'
    date_type: published
    observed_at: '{card_observed_at}'
    verified_at: '{card_observed_at}'
    configuration: {configuration}
    id: lab/model#stable
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
        [board_row],
        url=source_url,
        page_ref="sha256:" + "b" * 64,
        read_date=refresh_observed_at,
        note="fixture",
    )
    board = refresh._reading_from_projection(
        key="fixture", source_id="fixture-source", benchmarks=("fixture_benchmark",),
        source_url=source_url, projected=projection,
        observed_at=refresh_observed_at, value_field="score", store=store,
    )
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([board], []))
    report = refresh.run(
        observed_at=refresh_observed_at, dry_run=False, root=root, source_cache=cache
    )
    assert report.quarantined == []
    return refresh._front(card)["benchmarks"]["evidence"][0]


@pytest.mark.parametrize("date_key", refresh._SOURCE_DATE_KEYS)
def test_same_day_source_date_stays_published_and_unchanged(
    monkeypatch, tmp_path: Path, date_key: str,
) -> None:
    configuration = "dataset re-read 2026-09-24. Board row read 2026-09-24."
    row = _run_one_row_refresh(
        monkeypatch, tmp_path,
        board_row={"model": "Stable Model", "score": "72.0%", date_key: "2026-09-28"},
        configuration=configuration,
        evidence_date="2026-09-01",
        card_observed_at="2026-09-24",
        refresh_observed_at="2026-09-28",
    )

    assert str(row["evidence_date"]) == "2026-09-28"
    assert str(row["observed_at"]) == "2026-09-28"
    assert row["date_type"] == "published"
    assert row["configuration"] == configuration


def test_dataset_reread_text_is_not_rewritten(monkeypatch, tmp_path: Path) -> None:
    row = _run_one_row_refresh(
        monkeypatch, tmp_path,
        board_row={"model": "Stable Model", "score": "72.0%"},
        configuration="dataset re-read 2026-09-24. Board row read 2026-09-24.",
        evidence_date="2026-09-24",
        card_observed_at="2026-09-24",
        refresh_observed_at="2026-09-28",
        source_url=refresh.readers.METR_URL,
    )

    assert str(row["evidence_date"]) == "2026-09-28"
    assert row["date_type"] == "evaluated"
    assert row["configuration"] == (
        "dataset re-read 2026-09-24. Board row read 2026-09-28."
    )


def test_blank_date_on_a_dated_projector_stays_published() -> None:
    configuration = "Board row read 2026-09-24."
    epoch = "https://epoch.ai/benchmarks/gpqa-diamond"
    for extra in ({"date": None}, {"date": ""}, {}):
        aligned = refresh.align_observation_dating({
            "source_url": epoch,
            "evidence_date": "2026-09-28",
            "observed_at": "2026-09-28",
            "date_type": "published",
            "configuration": configuration,
            **extra,
        })
        assert aligned["date_type"] == "published"
        assert aligned["configuration"] == configuration


def test_epoch_blank_started_at_passes_score_only(monkeypatch, tmp_path: Path) -> None:
    root = tmp_path / "repo"
    cache = tmp_path / "copies"
    source_url = "https://epoch.ai/benchmarks/gpqa-diamond"
    configuration = "Board row read 2026-09-24."
    (root / "premier").mkdir(parents=True)
    (root / "models" / "lab").mkdir(parents=True)
    (root / "registry").mkdir(parents=True)
    (root / "verification").mkdir(parents=True)
    (root / "premier" / "slice-1.yaml").write_text(
        "models:\n- model_id: lab/model\n", encoding="utf-8"
    )
    (root / "registry" / "sources.yaml").write_text(
        f"""schema_version: 1
sources:
- id: fixture-epoch
  url: "{source_url}"
  volatility: live
  fetch: http
  normaliser: text-default
  cited_regions:
  - id: rows
    locator: {{kind: page, value: ''}}
""",
        encoding="utf-8",
    )
    card = root / "models" / "lab" / "model.md"
    card.write_text(
        f"""---
model_id: lab/model
display_name: Grok 4
version: grok-4-0709
benchmarks:
  evidence:
  - benchmark_id: gpqa_diamond
    model_id_as_evaluated: grok-4-0709
    score: 50.0
    unit: percent
    source_url: "{source_url}"
    source_kind: independent_evaluator
    evidence_date: '2026-09-24'
    date_type: published
    observed_at: '2026-09-24'
    verified_at: '2026-09-24'
    configuration: {configuration}
    id: lab/model#gpqa
    sources:
    - source_id: fixture-epoch
      snapshot_ref: sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
      cited_regions: [rows]
---
""",
        encoding="utf-8",
    )
    projection = refresh.readers.project_epoch(
        "Model version,mean_score,stderr,Started at\ngrok-4-0709,0.5,,\n",
        url=source_url,
        page_ref="sha256:" + "b" * 64,
        read_date="2026-09-28",
    )
    assert "date" not in json.loads(projection)["rows"][0]
    store = refresh.CopyStore(cache)
    board = refresh._reading_from_projection(
        key="epoch:gpqa_diamond",
        source_id="fixture-epoch",
        benchmarks=("gpqa_diamond",),
        source_url=source_url,
        projected=projection,
        observed_at="2026-09-28",
        value_field="mean_score",
        fraction=True,
        store=store,
        card_urls=(source_url,),
    )
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([board], []))
    before = tmp_path / "before"
    shutil.copytree(root, before)

    report = refresh.run(
        observed_at="2026-09-28", dry_run=False, root=root, source_cache=cache
    )

    row = refresh._front(card)["benchmarks"]["evidence"][0]
    result = refresh.check_score_only(before, root)
    assert report.quarantined == []
    assert row["date_type"] == "published"
    assert row["configuration"] == configuration
    assert str(row["observed_at"]) == "2026-09-28"
    assert str(row["evidence_date"]) == "2026-09-28"
    assert result.ok, result.errors


def test_folded_reread_is_not_a_read_date() -> None:
    reread = "configuration: dataset re-read\n      2026-09-24."
    assert refresh._replace_folded_read_date(reread, "2026-09-28") == reread
    folded = "configuration: Board read\n      2026-09-24."
    replaced = refresh._replace_folded_read_date(folded, "2026-09-28")
    assert "2026-09-28" in replaced
    assert "2026-09-24" not in replaced


def test_score_only_check_accepts_an_aligned_observation_date(tmp_path: Path) -> None:
    configuration = "Board row read {day}; tasks updated 2026-09-10."
    before_text = _card("2026-09-24").replace(
        "https://example.test/leaderboard.json", refresh.readers.METR_URL,
    ).replace(
        "    date_type: published\n",
        "    date_type: published\n"
        f"    configuration: {configuration.format(day='2026-09-24')}\n",
    )
    after_text = _card("2026-10-05").replace(
        "https://example.test/leaderboard.json", refresh.readers.METR_URL,
    ).replace(
        "evidence_date: '2026-09-01'\n",
        "evidence_date: '2026-10-05'\n",
    ).replace(
        "    date_type: published\n",
        "    date_type: evaluated\n"
        f"    configuration: {configuration.format(day='2026-10-05')}\n",
    )
    before, after = _write_guard_cards(tmp_path, before_text, after_text)

    assert refresh.check_score_only(before, after).ok


def test_score_only_check_refuses_an_unrelated_configuration_edit(tmp_path: Path) -> None:
    before_text = _card("2026-10-05").replace(
        "evidence_date: '2026-09-01'\n", "evidence_date: '2026-10-05'\n",
    )
    after_text = before_text.replace(
        "    date_type: published\n",
        "    date_type: published\n    configuration: a different sentence\n",
    )
    before, after = _write_guard_cards(tmp_path, before_text, after_text)

    result = refresh.check_score_only(before, after)

    assert not result.ok
    assert result.errors == ("non-score card data changed: models/lab/model.md",)


def _arena_guard_card(observed_at: str, *, model: str = "Example Model (High)") -> str:
    return _card(observed_at).replace(
        "benchmark_id: fixture_benchmark", "benchmark_id: arena_text",
    ).replace(
        "source_url: https://example.test/leaderboard.json",
        "source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset",
    ).replace(
        "model_id_as_evaluated: Stable Model", f"model_id_as_evaluated: {model}",
    ).replace("unit: percent", "unit: Arena score (Elo scale)")


def _guard_result(tmp_path: Path, before_text: str, after_text: str):
    before, after = _write_guard_cards(tmp_path, before_text, after_text)
    return refresh.check_score_only(before, after)


def test_score_only_check_refuses_interval_and_vote_count_on_a_non_arena_row(
    tmp_path: Path,
) -> None:
    before_text = _card("2026-09-24")
    after_text = before_text.replace("score: 72.0", "score: 73.0").replace(
        "    id: lab/model#stable\n",
        "    interval: [70.0, 76.0]\n    n: 40\n    id: lab/model#stable\n",
    )
    result = _guard_result(tmp_path, before_text, after_text)

    assert not result.ok
    assert result.errors == ("non-score card data changed: models/lab/model.md",)


def test_score_only_check_accepts_interval_and_vote_count_on_a_refreshed_arena_row(
    tmp_path: Path,
) -> None:
    before_text = _arena_guard_card("2026-09-24").replace(
        "source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset",
        "source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/",
    )
    after_text = before_text.replace("score: 72.0", "score: 73.0").replace(
        "    id: lab/model#stable\n",
        "    interval: [70.0, 76.0]\n    n: 40\n    id: lab/model#stable\n",
    )
    assert _guard_result(tmp_path, before_text, after_text).ok


def test_score_only_check_accepts_a_figures_only_configuration_on_an_arena_row(
    tmp_path: Path,
) -> None:
    before_text = _arena_guard_card("2026-09-24").replace(
        "    date_type: published\n",
        "    date_type: published\n"
        "    configuration: rating 1100, CI 1080 to 1120, votes 100, rank 4, "
        "revision aaaaaaa, published 2026-09-01\n",
    )
    after_text = before_text.replace("score: 72.0", "score: 1200.5").replace(
        "evidence_date: '2026-09-01'",
        "evidence_date: '2026-11-12'",
    ).replace(
        "    id: lab/model#stable\n",
        "    interval: [1180.0, 1220.0]\n    n: 200\n    id: lab/model#stable\n",
    ).replace(
        "rating 1100, CI 1080 to 1120, votes 100, rank 4, "
        "revision aaaaaaa, published 2026-09-01",
        "rating 1200.50, CI 1180 to 1220, votes 200, rank 3, "
        "revision aaaaaaa, published 2026-11-12",
    )
    assert _guard_result(tmp_path, before_text, after_text).ok


def _arena_sentence_with_token(before_token: str, after_token: str) -> tuple[str, str]:
    before_sentence = (
        f"model {before_token}; publication date 2026-10-01; rating 1100.00 "
        "[1080.00, 1120.00], CI 1080.00-1120.00, 2222 votes, rank 4. "
        "Observed 2026-10-01."
    )
    after_sentence = (
        f"model {after_token}; publication date 2026-11-02; rating 1210.25 "
        "[1190.50, 1230.75], CI 1190.50-1230.75, 3333 votes, rank 3. "
        "Observed 2026-11-11."
    )
    before_text = _arena_guard_card("2026-10-01").replace(
        "score: 72.0", "score: 1100.0",
    ).replace(
        "    date_type: published\n",
        f"    date_type: published\n    configuration: {before_sentence}\n",
    )
    after_text = before_text.replace("score: 1100.0", "score: 1210.25").replace(
        "evidence_date: '2026-09-01'", "evidence_date: '2026-11-02'",
    ).replace(
        "observed_at: '2026-10-01'", "observed_at: '2026-11-11'",
    ).replace(
        "verified_at: '2026-10-01'", "verified_at: '2026-11-11'",
    ).replace(
        "    id: lab/model#stable\n",
        "    interval: [1190.5, 1230.75]\n    n: 3333\n    id: lab/model#stable\n",
    ).replace(before_sentence, after_sentence)
    return before_text, after_text


def test_score_only_check_accepts_an_unchanged_id_that_contains_a_date(
    tmp_path: Path,
) -> None:
    before_text, after_text = _arena_sentence_with_token(
        "gpt-4o-2024-08-06", "gpt-4o-2024-08-06",
    )

    assert _guard_result(tmp_path, before_text, after_text).ok


def test_score_only_check_refuses_a_changed_id_that_contains_a_date(
    tmp_path: Path,
) -> None:
    before_text, after_text = _arena_sentence_with_token(
        "gpt-4o-2024-08-06", "gpt-4o-2026-11-11",
    )
    result = _guard_result(tmp_path, before_text, after_text)

    assert not result.ok
    assert result.errors == ("non-score card data changed: models/lab/model.md",)


def test_score_only_check_accepts_a_writer_shaped_arena_sentence(tmp_path: Path) -> None:
    """Two-decimal rating, bracket, CI a-b, votes over 1000, rank, and both dates."""
    before_sentence = (
        "publication date 2026-10-01; rating 1100.00 [1080.00, 1120.00], "
        "CI 1080.00-1120.00, 2222 votes, rank 4. Observed 2026-10-01."
    )
    after_sentence = (
        "publication date 2026-11-02; rating 1210.25 [1190.50, 1230.75], "
        "CI 1190.50-1230.75, 3333 votes, rank 3. Observed 2026-11-11."
    )
    before_text = _arena_guard_card("2026-10-01").replace(
        "score: 72.0", "score: 1100.0",
    ).replace(
        "    date_type: published\n",
        f"    date_type: published\n    configuration: {before_sentence}\n",
    )
    after_text = before_text.replace("score: 1100.0", "score: 1210.25").replace(
        "evidence_date: '2026-09-01'", "evidence_date: '2026-11-02'",
    ).replace(
        "observed_at: '2026-10-01'", "observed_at: '2026-11-11'",
    ).replace(
        "verified_at: '2026-10-01'", "verified_at: '2026-11-11'",
    ).replace(
        "    id: lab/model#stable\n",
        "    interval: [1190.5, 1230.75]\n    n: 3333\n    id: lab/model#stable\n",
    ).replace(before_sentence, after_sentence)

    assert _guard_result(tmp_path, before_text, after_text).ok


@pytest.mark.parametrize("before_sentence, after_sentence", [
    ("context 32k", "context 16k"),
    ("model v2", "model v3"),
    ("cutoff 32.", "cutoff 16."),
    ("serial 1234567", "serial 7654321"),
    ("revision aaaaaaa", "revision bbbbbbb"),
])
def test_score_only_check_refuses_an_unchecked_figure_on_an_arena_row(
    tmp_path: Path, before_sentence: str, after_sentence: str,
) -> None:
    before_text, after_text = _arena_sentence(before_sentence, after_sentence)
    result = _guard_result(tmp_path, before_text, after_text)

    assert not result.ok
    assert result.errors == ("non-score card data changed: models/lab/model.md",)


def _arena_sentence(before_sentence: str, after_sentence: str) -> tuple[str, str]:
    before_text = _arena_guard_card("2026-09-24").replace(
        "    date_type: published\n",
        f"    date_type: published\n    configuration: {before_sentence}\n",
    )
    after_text = before_text.replace("score: 72.0", "score: 73.0").replace(
        before_sentence, after_sentence,
    )
    return before_text, after_text


@pytest.mark.parametrize("before_sentence, after_sentence", [
    ("top 10 of 190 at 95%", "top 3 of 20 at 50%"),
    ("row 12 of the board", "row 17 of the board"),
    ("see MODEL-100 for the note", "see MODEL-467 for the note"),
    ("rating 1100", "rating -5"),
])
def test_score_only_check_refuses_a_changed_number_that_is_not_the_reading(
    tmp_path: Path, before_sentence: str, after_sentence: str,
) -> None:
    before_text, after_text = _arena_sentence(before_sentence, after_sentence)
    result = _guard_result(tmp_path, before_text, after_text)

    assert not result.ok
    assert result.errors == ("non-score card data changed: models/lab/model.md",)


def test_score_only_check_refuses_a_configuration_wording_change_on_an_arena_row(
    tmp_path: Path,
) -> None:
    before_text = _arena_guard_card("2026-09-24").replace(
        "    date_type: published\n",
        "    date_type: published\n    configuration: rating 1100 overall\n",
    )
    after_text = before_text.replace("score: 72.0", "score: 73.0").replace(
        "rating 1100 overall", "rating 1200 on the style-controlled board",
    )
    result = _guard_result(tmp_path, before_text, after_text)

    assert not result.ok
    assert result.errors == ("non-score card data changed: models/lab/model.md",)


def test_score_only_check_accepts_null_effort_becoming_the_canonical_level(
    tmp_path: Path,
) -> None:
    before_text = _arena_guard_card("2026-09-24")
    after_text = before_text.replace("score: 72.0", "score: 73.0").replace(
        "    date_type: published\n",
        "    date_type: published\n    effort: high\n",
    )
    assert _guard_result(tmp_path, before_text, after_text).ok


def test_score_only_check_refuses_a_non_canonical_effort_spelling(tmp_path: Path) -> None:
    before_text = _arena_guard_card("2026-09-24")
    after_text = before_text.replace("score: 72.0", "score: 73.0").replace(
        "    date_type: published\n",
        "    date_type: published\n    effort: High\n",
    )
    result = _guard_result(tmp_path, before_text, after_text)

    assert not result.ok
    assert result.errors == ("non-score card data changed: models/lab/model.md",)


def test_score_only_check_refuses_effort_changing_from_a_stored_value(tmp_path: Path) -> None:
    before_text = _arena_guard_card("2026-09-24").replace(
        "    date_type: published\n",
        "    date_type: published\n    effort: high\n",
    )
    after_text = before_text.replace("score: 72.0", "score: 73.0").replace(
        "effort: high", "effort: max",
    )
    result = _guard_result(tmp_path, before_text, after_text)

    assert not result.ok
    assert result.errors == ("non-score card data changed: models/lab/model.md",)


def test_score_only_check_refuses_benchmark_version_on_any_row(tmp_path: Path) -> None:
    for root_name, before_text in (
        ("arena", _arena_guard_card("2026-09-24")),
        ("other", _card("2026-09-24")),
    ):
        after_text = before_text.replace("score: 72.0", "score: 73.0").replace(
            "    date_type: published\n",
            "    date_type: published\n    benchmark_version: revision 0123456789ab\n",
        )
        result = _guard_result(tmp_path / root_name, before_text, after_text)
        assert not result.ok
        assert result.errors == ("non-score card data changed: models/lab/model.md",)


def test_score_only_check_refuses_the_arena_widening_on_a_non_arena_row(tmp_path: Path) -> None:
    before_text = _card("2026-09-24").replace(
        "model_id_as_evaluated: Stable Model",
        "model_id_as_evaluated: Example Model (High)",
    ).replace(
        "    date_type: published\n",
        "    date_type: published\n    configuration: rating 1100\n",
    )
    after_text = before_text.replace("score: 72.0", "score: 73.0").replace(
        "rating 1100", "rating 1200",
    ).replace(
        "    date_type: published\n",
        "    date_type: published\n    effort: high\n",
    )
    result = _guard_result(tmp_path, before_text, after_text)

    assert not result.ok
    assert result.errors == ("non-score card data changed: models/lab/model.md",)


def test_score_only_check_refuses_arena_widening_when_the_source_is_not_the_dataset_root(
    tmp_path: Path,
) -> None:
    before_text = _arena_guard_card("2026-09-24").replace(
        "source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset",
        "source_url: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/main",
    )
    after_text = before_text.replace("score: 72.0", "score: 73.0").replace(
        "    id: lab/model#stable\n",
        "    interval: [70.0, 76.0]\n    n: 40\n    id: lab/model#stable\n",
    )
    result = _guard_result(tmp_path, before_text, after_text)

    assert not result.ok
    assert result.errors == ("non-score card data changed: models/lab/model.md",)


def test_score_only_check_refuses_a_changed_model_id(tmp_path: Path) -> None:
    before_text = _card("2026-09-24")
    after_text = before_text.replace("score: 72.0", "score: 73.0").replace(
        "model_id_as_evaluated: Stable Model",
        "model_id_as_evaluated: Other Model",
    )
    before, after = _write_guard_cards(tmp_path, before_text, after_text)

    result = refresh.check_score_only(before, after)

    assert not result.ok
    assert result.errors == ("non-score card data changed: models/lab/model.md",)


def test_score_only_check_refuses_a_changed_benchmark_id(tmp_path: Path) -> None:
    before_text = _card("2026-09-24")
    after_text = before_text.replace("score: 72.0", "score: 73.0").replace(
        "benchmark_id: fixture_benchmark",
        "benchmark_id: other_benchmark",
    )
    before, after = _write_guard_cards(tmp_path, before_text, after_text)

    result = refresh.check_score_only(before, after)

    assert not result.ok
    assert result.errors == ("non-score card data changed: models/lab/model.md",)


def test_score_only_check_refuses_a_changed_source_url(tmp_path: Path) -> None:
    before_text = _card("2026-09-24")
    after_text = before_text.replace("score: 72.0", "score: 73.0").replace(
        "source_url: https://example.test/leaderboard.json",
        "source_url: https://example.test/other.json",
    )
    before, after = _write_guard_cards(tmp_path, before_text, after_text)

    result = refresh.check_score_only(before, after)

    assert not result.ok
    assert result.errors == ("non-score card data changed: models/lab/model.md",)


def test_score_only_check_refuses_effort_the_card_id_does_not_name(tmp_path: Path) -> None:
    before_text = _card("2026-09-24")
    after_text = before_text.replace("score: 72.0", "score: 73.0").replace(
        "    date_type: published\n",
        "    date_type: published\n    effort: high\n",
    )
    before, after = _write_guard_cards(tmp_path, before_text, after_text)

    result = refresh.check_score_only(before, after)

    assert not result.ok
    assert result.errors == ("non-score card data changed: models/lab/model.md",)


def test_a_sentence_that_quotes_no_reading_is_left_unchanged() -> None:
    text = "Text Arena overall, style-controlled"
    assert refresh._retell_reading(
        text, old_score=1100, new_score=1200, old_interval=None, new_interval=None,
        old_n=None, new_n=None, old_dates=(), new_publish=None,
        new_observed="2026-11-11", new_revision="0123456789abcdef", new_effort=None,
    ) == text


def test_two_revision_quotes_are_not_rewritten() -> None:
    assert refresh._retell_reading(
        "revision aaaaaaa and revision bbbbbbb",
        old_score=1, new_score=2, old_interval=None, new_interval=None,
        old_n=None, new_n=None, old_dates=(), new_publish=None,
        new_observed="2026-11-11", new_revision="c" * 40, new_effort=None,
    ) is None


def test_score_only_check_refuses_reread_and_carried_source_date_edits(tmp_path: Path) -> None:
    before_reread = _card("2026-09-24").replace(
        "evidence_date: '2026-09-01'\n",
        "evidence_date: '2026-09-13'\n",
    ).replace(
        "    date_type: published\n",
        "    date_type: published\n    configuration: dataset re-read 2026-09-24.\n",
    )
    after_reread = _card("2026-09-28").replace(
        "evidence_date: '2026-09-01'\n",
        "evidence_date: '2026-09-28'\n",
    ).replace(
        "    date_type: published\n",
        "    date_type: evaluated\n    configuration: dataset re-read 2026-09-28.\n",
    )
    before, after = _write_guard_cards(tmp_path / "reread", before_reread, after_reread)
    reread = refresh.check_score_only(before, after)
    assert not reread.ok
    assert reread.errors == ("non-score card data changed: models/lab/model.md",)

    before_carried = _card("2026-09-24").replace(
        "evidence_date: '2026-09-01'\n",
        "evidence_date: '2026-09-28'\n",
    ).replace(
        "    date_type: published\n",
        "    date_type: published\n    configuration: Board row read 2026-09-24.\n",
    )
    after_carried = _card("2026-09-28").replace(
        "evidence_date: '2026-09-01'\n",
        "evidence_date: '2026-09-28'\n",
    ).replace(
        "    date_type: published\n",
        "    date_type: evaluated\n    configuration: Board row read 2026-09-28.\n",
    )
    before, after = _write_guard_cards(tmp_path / "carried", before_carried, after_carried)
    carried = refresh.check_score_only(before, after)
    assert not carried.ok
    assert carried.errors == ("non-score card data changed: models/lab/model.md",)


def test_score_only_check_accepts_a_standalone_read_beside_reread(tmp_path: Path) -> None:
    before_text = _card("2026-09-24").replace(
        "https://example.test/leaderboard.json", refresh.readers.MTEB_URL,
    ).replace(
        "evidence_date: '2026-09-01'\n",
        "evidence_date: '2026-09-24'\n",
    ).replace(
        "    date_type: published\n",
        "    date_type: published\n"
        "    configuration: dataset re-read 2026-09-24. Board row read 2026-09-24.\n",
    )
    after_text = _card("2026-09-28").replace(
        "https://example.test/leaderboard.json", refresh.readers.MTEB_URL,
    ).replace(
        "evidence_date: '2026-09-01'\n",
        "evidence_date: '2026-09-28'\n",
    ).replace(
        "    date_type: published\n",
        "    date_type: evaluated\n"
        "    configuration: dataset re-read 2026-09-24. Board row read 2026-09-28.\n",
    )
    before, after = _write_guard_cards(tmp_path, before_text, after_text)

    assert refresh.check_score_only(before, after).ok


ARENA_CARD_URL = "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset"


def test_observation_sources_are_projectors_without_a_row_date() -> None:
    urls = refresh._OBSERVATION_SOURCE_URLS
    assert {
        refresh.readers.METR_URL,
        refresh.readers.MTEB_URL,
        refresh.MTEB_API.format("MTEB(Multilingual,%20v2)"),
        refresh.MTEB_API.format("MTEB(cmn,%20v1)"),
        refresh.MTEB_API.format("FollowIR"),
        refresh.readers.MATHARENA_URL,
        refresh.MATHARENA_AIME_2025_URL,
        "https://matharena.ai/competition_tables/overall--brokenarxiv",
        "https://matharena.ai/competition_tables/overall--arxivmath",
        refresh.readers.CURSOR_URL,
        refresh.readers.DEEPSWE_URL,
        refresh.DEEPSWE_CARD_URL,
        refresh.readers.VENDING_URL,
        refresh.readers.FRONTIERCODE_URL,
        refresh.readers.OSWORLD_URL,
        refresh.HLE_URL,
    } <= urls
    dated = {
        ARENA_CARD_URL,
        "https://epoch.ai/benchmarks/gpqa-diamond",
        "https://epoch.ai/frontiermath",
        "https://epoch.ai/benchmarks/swe-bench-verified",
        "https://epoch.ai/benchmarks/simpleqa-verified",
        "https://www.tbench.ai/leaderboard/terminal-bench/4.0",
        refresh.readers.SCALE_URL,
        "https://labs.scale.com/leaderboard/swe_bench_pro",
        refresh.FINBENCH_URL,
        refresh.readers.SWEBENCH_URL,
        "https://example.test/leaderboard.json",
    }
    assert dated.isdisjoint(urls)


def test_align_observation_cards_rewrites_stored_rows_only(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    card = root / "models" / "lab" / "model.md"
    card.parent.mkdir(parents=True)
    card.write_text(
        f"""---
model_id: lab/model
benchmarks:
  evidence:
  - benchmark_id: fixture_benchmark
    model_id_as_evaluated: Dated By Observation
    score: 1.0
    unit: percent
    source_url: {refresh.readers.METR_URL}
    source_kind: benchmark_author
    evidence_date: '2026-10-05'
    date_type: published
    observed_at: '2026-10-05'
    configuration: Board read
      2026-09-24; tasks updated 2026-09-10.
  - benchmark_id: fixture_benchmark
    model_id_as_evaluated: Same Day Source
    score: 2.0
    unit: percent
    source_url: {ARENA_CARD_URL}
    source_kind: benchmark_author
    evidence_date: '2026-10-05'
    date_type: published
    observed_at: '2026-10-05'
    configuration: dataset re-read 2026-09-24. Board row read 2026-09-24.
  - benchmark_id: fixture_benchmark
    model_id_as_evaluated: Older Day
    score: 3.0
    unit: percent
    source_url: {refresh.readers.METR_URL}
    source_kind: benchmark_author
    evidence_date: '2026-09-01'
    date_type: published
    observed_at: '2026-10-05'
    configuration: Board read 2026-09-24; published 2026-09-01.
---
""",
        encoding="utf-8",
    )

    changed = refresh.align_observation_cards(root)

    text = card.read_text(encoding="utf-8")
    rows = refresh._front(card)["benchmarks"]["evidence"]
    assert changed == ["models/lab/model.md"]
    assert rows[0]["date_type"] == "evaluated"
    assert rows[0]["configuration"] == "Board read 2026-10-05; tasks updated 2026-09-10."
    assert "    configuration: Board read\n      2026-10-05; tasks updated 2026-09-10.\n" in text
    assert rows[1]["date_type"] == "published"
    assert rows[1]["configuration"] == (
        "dataset re-read 2026-09-24. Board row read 2026-09-24."
    )
    assert rows[2]["date_type"] == "published"
    assert rows[2]["configuration"] == "Board read 2026-09-24; published 2026-09-01."
    assert refresh.align_observation_cards(root) == []


def test_score_only_check_refuses_a_same_day_source_measurement(tmp_path: Path) -> None:
    before_text = _card("2026-09-28").replace(
        "https://example.test/leaderboard.json", ARENA_CARD_URL,
    ).replace(
        "evidence_date: '2026-09-01'\n",
        "evidence_date: '2026-09-28'\n",
    ).replace(
        "    date_type: published\n",
        "    date_type: published\n"
        "    configuration: dataset re-read 2026-09-24. Board row read 2026-09-24.\n",
    )
    after_text = _card("2026-09-28").replace(
        "https://example.test/leaderboard.json", ARENA_CARD_URL,
    ).replace(
        "evidence_date: '2026-09-01'\n",
        "evidence_date: '2026-09-28'\n",
    ).replace(
        "    date_type: published\n",
        "    date_type: evaluated\n"
        "    configuration: dataset re-read 2026-09-24. Board row read 2026-09-28.\n",
    )
    before, after = _write_guard_cards(tmp_path, before_text, after_text)

    result = refresh.check_score_only(before, after)

    assert not result.ok
    assert result.errors == ("non-score card data changed: models/lab/model.md",)


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
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([], [failure]))

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
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([board], []))

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


def _weekly_pull_request_body(report: refresh.RefreshReport) -> str:
    opening = (
        "This weekly job re-read the registered live boards for existing models "
        "in the premier set.\n\n"
    )
    closing = (
        "\nThe diff guard proved that no card, evidence row, identity fact, "
        "or licence fact was added or removed.\n\n"
        "Written by GPT-5 Codex.\n"
    )
    return opening + refresh.render_report(report) + closing


def _refresh_report(*, changes: int, failures: int) -> refresh.RefreshReport:
    return refresh.RefreshReport(
        boards={
            "arena": {
                "models_read": 4,
                "models_reconfirmed": 1,
                "values_changed": changes,
                "failures": [],
            },
        },
        changes=[
            refresh.ScoreChange(
                card=f"models/lab/m{index}.md",
                model_id=f"lab/m{index}",
                model=f"Model {index}",
                benchmark="change_bench",
                old_value=float(index),
                new_value=float(index) + 0.5,
                source="https://example.test/board",
                observed_date="2026-11-12",
            )
            for index in range(changes)
        ],
        failures=[
            refresh.RowFailure(
                f"lab/f{index}",
                "fail_bench",
                "https://example.test/board",
                f"reason {index}",
            )
            for index in range(failures)
        ],
        arena_revision="abc123def456",
    )


def _marked_lines(text: str, marker: str) -> list[str]:
    return [line for line in text.splitlines() if marker in line]


def test_pull_request_body_under_the_limit_is_unchanged() -> None:
    body = _weekly_pull_request_body(_refresh_report(changes=2, failures=1))

    assert len(body) <= 60_000
    assert refresh.fit_pull_request_body(body) == body


def test_pull_request_body_over_the_limit_cuts_on_a_change_row() -> None:
    body = _weekly_pull_request_body(_refresh_report(changes=40, failures=2))
    change_rows = _marked_lines(body, "`change_bench`")
    fitted = refresh.fit_pull_request_body(body, limit=2_500)

    assert len(fitted) <= 2_500
    kept = _marked_lines(fitted, "`change_bench`")
    assert kept == change_rows[:len(kept)]
    assert len(kept) < len(change_rows)
    omitted = len(change_rows) - len(kept)
    note = next(line for line in fitted.splitlines() if "left out" in line)
    assert str(omitted) in note
    assert "leaderboard-refresh-report" in note


def test_pull_request_body_keeps_both_board_tables_when_failures_are_cut() -> None:
    report = _refresh_report(changes=2271, failures=1060)
    report.boards["arena"].update(
        rows_rewritten=10, rows_reconfirmed=2, rows_left=0, rows_skipped={"configuration": 3},
    )
    report.arena_rows_without_board = 19
    report.arena_rows_off_root = 7
    body = _weekly_pull_request_body(report)
    fitted = refresh.fit_pull_request_body(body)

    assert len(fitted) < refresh._PR_BODY_LIMIT
    assert "| Board | Models read |" in fitted
    assert "| Board | Rewritten |" in fitted
    assert "Arena rows with no board: 19" in fitted
    assert "Arena rows whose source is not the dataset root: 7" in fitted
    failure_rows = _marked_lines(body, "`fail_bench`")
    kept = _marked_lines(fitted, "`fail_bench`")
    assert kept == failure_rows[:len(kept)]
    assert len(kept) < len(failure_rows)
    omitted = len(failure_rows) - len(kept)
    note = next(line for line in fitted.splitlines() if "failure" in line and "left out" in line)
    assert str(omitted) in note
    assert "leaderboard-refresh-report" in note


def test_pull_request_body_keeps_every_failure_row_when_changes_are_cut() -> None:
    body = _weekly_pull_request_body(_refresh_report(changes=40, failures=6))
    failure_rows = _marked_lines(body, "`fail_bench`")
    fitted = refresh.fit_pull_request_body(body, limit=2_500)

    assert len(fitted) <= 2_500
    for row in failure_rows:
        assert row in fitted.splitlines()
    assert len(_marked_lines(fitted, "`change_bench`")) < 40


def test_fitted_body_stays_within_the_limit_after_the_pull_request_url_expands() -> None:
    body = _weekly_pull_request_body(_refresh_report(changes=80, failures=3))
    fitted = refresh.fit_pull_request_body(body, limit=4_000)
    url = "https://github.com/turbobeest/modelspec-data/pull/" + "9" * 10

    filled = fitted.replace("${PR_URL}", url)

    assert "${PR_URL}" not in filled
    assert len(filled) <= 4_000
    assert "leaderboard-refresh-report" in filled


def test_dates_the_writer_cannot_retell_are_listed_for_a_person() -> None:
    """Those refusals have their own heading, count, and card list, including over the limit."""
    report = _refresh_report(changes=40, failures=1)
    report.failures.extend([
        refresh.RowFailure(
            "lab/stale-a", "arena_elo_overall", "https://example.test/arena",
            refresh._DATE_THE_WRITER_CANNOT_RETELL,
        ),
        refresh.RowFailure(
            "lab/stale-b", "arena_elo_code", "https://example.test/arena",
            refresh._DATE_THE_WRITER_CANNOT_RETELL,
        ),
    ])
    rendered = refresh.render_report(report)
    heading = "## Dates the writer cannot retell"
    sentence = (
        "These rows need a person to rewrite the sentence; they will not refresh until then."
    )
    section = rendered.split(heading, 1)[1].split("\n## ", 1)[0]
    assert "2 rows." in section
    assert sentence in section
    assert "| `lab/stale-a` | `arena_elo_overall` |" in section
    assert "| `lab/stale-b` | `arena_elo_code` |" in section
    failures = rendered.split("## Failures", 1)[1]
    assert "lab/stale-a" not in failures
    assert "lab/stale-b" not in failures
    assert "`lab/f0`" in failures

    fitted = refresh.fit_pull_request_body(_weekly_pull_request_body(report), limit=2_500)
    assert len(fitted) <= 2_500
    fitted_section = fitted.split(heading, 1)[1].split("\n## ", 1)[0]
    assert "2 rows." in fitted_section
    assert sentence in fitted_section
    assert fitted.count("`lab/stale-a`") == 1
    assert fitted.count("`lab/stale-b`") == 1
    assert "`lab/f0`" in fitted


def test_large_refresh_uploads_the_report_before_a_body_edit_can_fail() -> None:
    workflow = yaml.safe_load(
        (Path(__file__).parents[1] / ".github" / "private-writers" /
         "leaderboard-refresh.yml").read_text(encoding="utf-8")
    )
    steps = workflow["jobs"]["refresh"]["steps"]
    read_at = next(
        index for index, step in enumerate(steps)
        if step.get("name") == "Re-read every covered board once"
    )
    report_upload = steps[read_at + 1]

    assert report_upload["if"] == "always()"
    assert report_upload["uses"] == "actions/upload-artifact@v4"
    assert report_upload["with"]["name"] == "leaderboard-refresh-report"
    assert report_upload["with"]["if-no-files-found"] == "ignore"
    uploaded = report_upload["with"]["path"]
    assert "report.md" in uploaded
    assert "report.json" in uploaded
    assert "audit.json" in uploaded

    prepare = next(step for step in steps if step.get("name") == "Prepare the pull-request body")
    assert "fit_pull_request_body" in prepare["run"]
    assert "pr-body.md" in prepare["run"]

    audit_at = next(
        index for index, step in enumerate(steps)
        if str((step.get("with") or {}).get("name", "")).startswith("leaderboard-refresh-audit-")
    )
    edit_at = next(index for index, step in enumerate(steps) if "gh pr edit" in step.get("run", ""))
    assert audit_at < edit_at
    assert steps[edit_at].get("continue-on-error") is True
    assert "::warning::" in steps[edit_at]["run"]

    guard = next(step for step in steps if step.get("name") == "Prove the generated diff is score-only")
    assert "continue-on-error" not in guard
    assert "raise SystemExit(1)" in guard["run"]
    no_update = next(
        step for step in steps
        if step.get("name") == "Fail a no-update run that could not read every board"
    )
    assert "continue-on-error" not in no_update
    assert no_update["if"] == "steps.result.outputs.updates == '0' && steps.result.outputs.failures != '0'"
    assert "exit 1" in no_update["run"]


_ARENA_DATASET = "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset"
_ARENA_NEW = "0123456789abcdef0123456789abcdef01234567"
_ARENA_OLD_REV = "aaaaaaaaaaaa"


def _arena_registry(root: Path, source_id: str) -> None:
    (root / "registry").mkdir(parents=True)
    (root / "registry" / "sources.yaml").write_text(
        f"""schema_version: 1
sources:
- id: {source_id}
  url: {_ARENA_DATASET}/resolve/{_ARENA_NEW}/text/latest-00000-of-00001.parquet
  fetch: http
  normaliser: text-default
  cited_regions:
  - id: rows
    locator: {{kind: page, value: ''}}
""",
        encoding="utf-8",
    )


def _arena_effort_card(
    root: Path, *, model: str, evaluated: str, display: str,
    store_reading: bool = True, configuration: str | None = None,
    effort: str | None = None, unit: str = "Arena score (Elo scale)",
    score: float = 1100.0,
) -> Path:
    card = root / "models" / "lab" / "model.md"
    card.parent.mkdir(parents=True)
    reading = "interval: [1080.0, 1120.0]\n    n: 1000\n    " if store_reading else ""
    sentence = configuration or (
        "Pinned LMArena dataset; publication date 2026-10-01; rating 1100.00 "
        "[1080.00, 1120.00], 1000 votes, rank 4. Observed 2026-10-01."
    )
    card.write_text(
        f"""---
model_id: {model}
display_name: {display}
version: {evaluated}
benchmarks:
  evidence:
  - benchmark_id: arena_elo_overall
    model_id_as_evaluated: {evaluated}
    score: {score}
    unit: {unit}
    {reading}effort: {"null" if effort is None else effort}
    source_url: {_ARENA_DATASET}
    source_kind: independent_evaluator
    evidence_date: '2026-10-01'
    date_type: published
    observed_at: '2026-10-01'
    verified_at: '2026-10-01'
    benchmark_version: text / overall, latest split, rating 1100
    configuration: >-
      {sentence}
    id: {model}#arena_elo_overall#old
    sources:
    - source_id: fixture-arena
      snapshot_ref: sha256:{'a' * 64}
      cited_regions: [rows]
---
""",
        encoding="utf-8",
    )
    return card


def _run_arena_effort_refresh(monkeypatch, tmp_path: Path, *, dataset_name: str,
                              evaluated: str, display: str,
                              dataset_rows: list[dict] | None = None,
                              model: str = "lab/example-model",
                              snapshot: Path | None = None, **card):
    """Refresh one Arena row from a fixture projection. No network."""
    root = tmp_path / "repo"
    cache = tmp_path / "copies"
    source_id = "fixture-arena"
    card = _arena_effort_card(
        root, model=model, evaluated=evaluated, display=display, **card,
    )
    _arena_registry(root, source_id)
    (root / "verification").mkdir()
    url = (
        f"{_ARENA_DATASET}/resolve/{_ARENA_NEW}/text/latest-00000-of-00001.parquet"
    )
    store = refresh.CopyStore(cache)
    projection = refresh.readers.document(
        dataset_rows or [{
            "model_name": dataset_name,
            "rating": 1210.25,
            "rating_lower": 1190.5,
            "rating_upper": 1230.75,
            "vote_count": 2222,
            "leaderboard_publish_date": "2026-11-02",
            "rank": 3,
        }],
        url=url, page_ref="sha256:" + "b" * 64, read_date="2026-11-11", note="fixture",
    )
    board = refresh._reading_from_projection(
        key="arena:text", source_id=source_id, benchmarks=("arena_elo_overall",),
        source_url=url, projected=projection, observed_at="2026-11-11",
        value_field="rating", store=store, card_urls=(_ARENA_DATASET,),
    )
    monkeypatch.delenv(refresh.ARENA_REVISION_ENV, raising=False)
    monkeypatch.setattr(
        refresh.readers, "resolve_arena_revision",
        lambda _fetch: refresh.readers.ArenaRevision(sha=_ARENA_NEW),
    )
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([board], []))
    if snapshot is not None:
        shutil.copytree(root, snapshot)
    report = refresh.run(
        observed_at="2026-11-11", dry_run=False, root=root, source_cache=cache,
        model_ids=(model,), arena_latest=True,
    )
    return report, card, root


def _evidence_row(card: Path) -> dict:
    return refresh._front(card)["benchmarks"]["evidence"][0]


def _arena_skip_classes(report) -> dict:
    return report.boards["arena:text"]["rows_skipped"]


def _verification_log(root: Path) -> dict:
    return json.loads((root / "verification" / "log.jsonl").read_text(encoding="utf-8"))


def test_refreshed_arena_row_verifies_against_the_matched_reading(
    monkeypatch, tmp_path: Path,
) -> None:
    """The model id names High in parentheses, and so does the dataset row."""
    report, card, root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="Example Model (High)",
        evaluated="Example Model (High)",
        display="Example Model",
    )

    assert report.quarantined == [], report.quarantined
    assert report.failures == [], report.failures
    row = _evidence_row(card)
    assert row["model_id_as_evaluated"] == "Example Model (High)"
    assert row["score"] == 1210.25
    assert row["interval"] == [1190.5, 1230.75]
    assert row["n"] == 2222
    assert row["effort"] == "high"
    assert "1210.25" in row["configuration"]
    assert "1190.50" in row["configuration"]
    assert "1230.75" in row["configuration"]
    assert "2222 votes" in row["configuration"]
    assert "2026-11-02" in row["configuration"]
    assert "2026-11-11" in row["configuration"]
    assert "rank 3" in row["configuration"]
    assert "rank 4" not in row["configuration"]
    for stale in ("1100", "1080", "1120", "1000", "2026-10-01"):
        assert stale not in row["configuration"]
    assert row["benchmark_version"] == "text / overall, latest split, rating 1100"
    log = _verification_log(root)
    assert log["outcome"] == "verified"
    assert log["diff"] is None


def test_a_score_only_rewrite_is_refused_before_it_is_written(
    monkeypatch, tmp_path: Path,
) -> None:
    def score_only(old, observation, *, observed_at):
        return {**dict(old), "score": observation.new_value}, None

    monkeypatch.setattr(refresh, "_copy_matched_reading", score_only)
    report, card, root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="Example Model (High)",
        evaluated="example-model-high",
        display="Example Model",
    )

    assert report.quarantined == []
    assert any(row.reason.startswith("verifier:") for row in report.failures)
    assert _evidence_row(card)["score"] == 1100.0
    assert not (root / "verification" / "log.jsonl").exists()


def test_a_hyphenated_dataset_name_keeps_null_effort(
    monkeypatch, tmp_path: Path,
) -> None:
    """A hyphen is not an effort separator. The verifier leaves effort null."""
    report, card, root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="example-model-high",
        evaluated="example-model-high",
        display="example-model-high",
    )

    assert report.quarantined == [], report.quarantined
    assert report.failures == [], report.failures
    row = _evidence_row(card)
    assert row["effort"] is None
    assert row["score"] == 1210.25
    log = _verification_log(root)
    assert log["outcome"] == "verified"
    assert log["diff"] is None


def test_a_model_name_without_an_effort_suffix_still_verifies(
    monkeypatch, tmp_path: Path,
) -> None:
    report, card, root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="Example Model",
        evaluated="Example Model",
        display="Example Model",
    )

    assert report.quarantined == [], report.quarantined
    row = _evidence_row(card)
    assert row["effort"] is None
    assert row["score"] == 1210.25
    assert row["interval"] == [1190.5, 1230.75]
    assert row["n"] == 2222
    log = _verification_log(root)
    assert log["outcome"] == "verified"
    assert log["diff"] is None


def test_a_quoted_interval_is_rewritten_when_the_card_field_is_empty(
    monkeypatch, tmp_path: Path,
) -> None:
    report, card, root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="Example Model",
        evaluated="Example Model",
        display="Example Model",
        store_reading=False,
    )

    assert report.quarantined == [], report.quarantined
    assert report.failures == [], report.failures
    row = _evidence_row(card)
    assert row["interval"] == [1190.5, 1230.75]
    assert row["n"] == 2222
    assert "1190.50" in row["configuration"]
    assert "2222 votes" in row["configuration"]
    assert "1080" not in row["configuration"]
    assert "1000 votes" not in row["configuration"]
    log = _verification_log(root)
    assert log["outcome"] == "verified"
    assert log["diff"] is None


def test_a_quoted_rank_with_no_dataset_rank_is_not_written(
    monkeypatch, tmp_path: Path,
) -> None:
    report, card, _root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="Example Model",
        evaluated="Example Model",
        display="Example Model",
        dataset_rows=[{
            "model_name": "Example Model",
            "rating": 1210.25,
            "rating_lower": 1190.5,
            "rating_upper": 1230.75,
            "vote_count": 2222,
            "leaderboard_publish_date": "2026-11-02",
        }],
    )

    assert any("rank" in row.reason for row in report.failures)
    assert _evidence_row(card)["score"] == 1100.0
    assert "rank 4" in _evidence_row(card)["configuration"]


@pytest.mark.parametrize("configuration, old_rank, kept", [
    (
        "Pinned LMArena dataset; publication date 2026-11-02; rating 1100.00 "
        "[1080.00, 1120.00], 1000 votes, rank 11. Observed 2026-10-01.",
        "rank 11",
        "2026-11-02",
    ),
    (
        "Pinned LMArena dataset; publication date 2026-11-02; rating 1100.00 "
        "[1080.00, 1120.00], 1000 votes, rank 2. Observed 2026-10-01.",
        "rank 2",
        "2026-11-02",
    ),
    (
        "Pinned LMArena dataset; publication date 2026-10-01; rating 1100.00 "
        "[1080.00, 1120.00], 1000 votes, rank 191. See MODEL-191 for the note. "
        "Observed 2026-10-01.",
        "rank 191",
        "MODEL-191",
    ),
])
def test_an_old_rank_equal_to_a_date_part_or_ticket_id_is_written(
    monkeypatch, tmp_path: Path, configuration: str, old_rank: str, kept: str,
) -> None:
    """November, day 02, and MODEL-191 are not the previous rank."""
    report, card, _root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="Example Model",
        evaluated="Example Model",
        display="Example Model",
        configuration=configuration,
    )

    assert report.failures == [], report.failures
    assert report.quarantined == [], report.quarantined
    row = _evidence_row(card)
    assert row["score"] == 1210.25
    assert "rank 3" in row["configuration"]
    assert old_rank not in row["configuration"]
    assert kept in row["configuration"]


_ARENA_WRITER_FIXTURES = [
    {
        "dataset_name": "Example Model",
        "evaluated": "Example Model",
        "display": "Example Model",
    },
    {
        "dataset_name": "Example Model",
        "evaluated": "Example Model",
        "display": "Example Model",
        "configuration": (
            "Pinned LMArena dataset; publication date 2026-10-01; rating 1100.00 "
            "CI 1080.00-1120.00, 1000 votes, rank 4. Observed 2026-10-01."
        ),
    },
    {
        "dataset_name": "Example Model",
        "evaluated": "Example Model",
        "display": "Example Model",
        "store_reading": False,
    },
    {
        "dataset_name": "Example Model (High)",
        "evaluated": "Example Model (High)",
        "display": "Example Model",
    },
    {
        "dataset_name": "Example Model",
        "evaluated": "Example Model",
        "display": "Example Model",
        "configuration": (
            "Pinned LMArena dataset; publication date 2026-11-02; rating 1100.00 "
            "[1080.00, 1120.00], 1000 votes, rank 11. Observed 2026-10-01."
        ),
    },
    {
        "dataset_name": "Example Model",
        "evaluated": "Example Model",
        "display": "Example Model",
        "configuration": (
            "Pinned LMArena dataset; publication date 2026-11-02; rating 1100.00 "
            "[1080.00, 1120.00], 1000 votes, rank 2. Observed 2026-10-01."
        ),
    },
    {
        "dataset_name": "Example Model",
        "evaluated": "Example Model",
        "display": "Example Model",
        "configuration": (
            "Pinned LMArena dataset; publication date 2026-10-01; rating 1100.00 "
            "[1080.00, 1120.00], 1000 votes, rank 191. See MODEL-191 for the note. "
            "Observed 2026-10-01."
        ),
    },
    {
        "dataset_name": "Example Model",
        "evaluated": "Example Model",
        "display": "Example Model",
        "dataset_rows": [{
            "model_name": "Example Model",
            "rating": 1100.0,
            "rating_lower": 1080.0,
            "rating_upper": 1120.0,
            "vote_count": 1000,
            "leaderboard_publish_date": "2026-10-01",
            "rank": 4,
        }],
    },
]


@pytest.mark.parametrize("card", _ARENA_WRITER_FIXTURES, ids=[
    "bracket", "ci", "quoted-interval", "effort", "november-rank", "day-rank",
    "ticket-rank", "observed-date",
])
def test_the_guard_accepts_the_writers_arena_fixture_row(
    monkeypatch, tmp_path: Path, card: dict,
) -> None:
    """The weekly guard sees the sentence this writer actually emits."""
    before = tmp_path / "before"
    report, _card, root = _run_arena_effort_refresh(
        monkeypatch, tmp_path, snapshot=before, **card,
    )

    assert report.failures == [], report.failures
    assert report.quarantined == [], report.quarantined
    result = refresh.check_score_only(before, root)
    assert result.ok, result.errors


def test_a_bracket_that_does_not_contain_the_score_is_not_rewritten(
    monkeypatch, tmp_path: Path,
) -> None:
    report, card, _root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="Example Model",
        evaluated="Example Model",
        display="Example Model",
        store_reading=False,
        configuration=(
            "Pinned LMArena dataset; publication date 2026-10-01; rating 1100.00 "
            "[1.00, 2.00], 1000 votes, rank 4. Observed 2026-10-01."
        ),
    )

    assert report.quarantined == []
    assert any("configuration" in row.reason for row in report.failures)
    assert _arena_skip_classes(report) == {"configuration": 1}
    assert _evidence_row(card)["score"] == 1100.0


def test_a_parenthetical_effort_the_card_does_not_name_is_not_written(
    monkeypatch, tmp_path: Path,
) -> None:
    report, card, _root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="Example Model (High)",
        evaluated="Example Model",
        display="Example Model",
    )

    assert report.quarantined == []
    assert any("effort" in row.reason for row in report.failures)
    assert _arena_skip_classes(report) == {"effort": 1}
    assert _evidence_row(card)["score"] == 1100.0


def test_a_card_effort_the_dataset_does_not_name_is_not_written(
    monkeypatch, tmp_path: Path,
) -> None:
    report, card, _root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="Example Model",
        evaluated="Example Model",
        display="Example Model",
        effort="high",
    )

    assert report.quarantined == []
    assert any("effort" in row.reason for row in report.failures)
    assert _arena_skip_classes(report) == {"effort": 1}
    assert _evidence_row(card)["score"] == 1100.0
    assert _evidence_row(card)["effort"] == "high"


def test_an_elo_unit_is_not_refreshed(monkeypatch, tmp_path: Path) -> None:
    """The extractor reads rating as an Arena score. ``elo`` is another dimension."""
    report, card, _root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="Example Model",
        evaluated="Example Model",
        display="Example Model",
        unit="elo",
        dataset_rows=[{
            "model_name": "Example Model",
            "rating": 1100.0,
            "rating_lower": 1080.0,
            "rating_upper": 1120.0,
            "vote_count": 1000,
            "leaderboard_publish_date": "2026-11-02",
            "rank": 3,
        }],
    )

    assert report.quarantined == []
    assert any("unit" in row.reason for row in report.failures)
    assert _arena_skip_classes(report) == {"unit": 1}
    assert _evidence_row(card)["score"] == 1100.0
    assert _evidence_row(card)["unit"] == "elo"


def test_a_token_match_the_verifier_does_not_own_is_not_swapped(
    monkeypatch, tmp_path: Path,
) -> None:
    report, card, _root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
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

    assert report.quarantined == []
    assert any("verifier" in row.reason for row in report.failures)
    assert _arena_skip_classes(report) == {"other-row": 1}
    row = _evidence_row(card)
    assert row["score"] == 1100.0
    assert "1210.25" not in row.get("configuration", "")
    assert "1300" not in row.get("configuration", "")


def test_a_match_the_verifier_does_not_own_is_not_written(
    monkeypatch, tmp_path: Path,
) -> None:
    report, card, _root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="Example Model (High)",
        evaluated="Example-Model-High",
        display="Example-Model-High",
        model="lab/zz-unrelated",
    )

    assert report.quarantined == []
    assert any("verifier" in row.reason for row in report.failures)
    assert _arena_skip_classes(report) == {"not-owned": 1}
    assert _evidence_row(card)["score"] == 1100.0


def test_an_observed_date_alone_reconfirms_the_row(monkeypatch, tmp_path: Path) -> None:
    report, card, _root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="Example Model",
        evaluated="Example Model",
        display="Example Model",
        dataset_rows=[{
            "model_name": "Example Model",
            "rating": 1100.0,
            "rating_lower": 1080.0,
            "rating_upper": 1120.0,
            "vote_count": 1000,
            "leaderboard_publish_date": "2026-10-01",
            "rank": 4,
        }],
    )

    assert report.failures == [], report.failures
    row = _evidence_row(card)
    assert row["score"] == 1100.0
    assert "Observed 2026-11-11" in row["configuration"]
    assert "rating 1100.00" in row["configuration"]
    summary = report.boards["arena:text"]
    assert summary["rows_rewritten"] == 0
    assert summary["rows_reconfirmed"] == 1


def test_an_arena_row_off_the_dataset_root_is_one_count(
    monkeypatch, tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    (root / "models" / "lab").mkdir(parents=True)
    (root / "premier").mkdir(parents=True)
    (root / "verification").mkdir()
    (root / "registry").mkdir()
    (root / "premier" / "slice-1.yaml").write_text("models: []\n", encoding="utf-8")
    (root / "registry" / "sources.yaml").write_text(
        "schema_version: 1\nsources: []\n", encoding="utf-8",
    )

    def write_card(name: str, url: str) -> None:
        (root / "models" / "lab" / f"{name}.md").write_text(
            f"""---
model_id: lab/{name}
benchmarks:
  evidence:
  - benchmark_id: arena_elo_overall
    source_url: {url}
    score: 1.0
---
""",
            encoding="utf-8",
        )

    write_card("root", _ARENA_DATASET + "/")
    write_card("off", _ARENA_DATASET + "/resolve/main/text/file.parquet")
    (root / "models" / "lab" / "plain.md").write_text(
        """---
model_id: lab/plain
benchmarks:
  evidence:
  - benchmark_id: fixture_benchmark
    source_url: https://example.test/leaderboard.json
    score: 1.0
---
""",
        encoding="utf-8",
    )
    monkeypatch.delenv(refresh.ARENA_REVISION_ENV, raising=False)
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([], []))

    report = refresh.run(
        observed_at="2026-11-11", dry_run=True, root=root, source_cache=tmp_path / "cache",
    )

    rendered = [
        line for line in refresh.render_report(report).splitlines()
        if "dataset root" in line
    ]
    assert rendered == ["Arena rows whose source is not the dataset root: 1"]
    path = tmp_path / "report.json"
    refresh.write_report_json(path, report)
    assert json.loads(path.read_text(encoding="utf-8"))["arena_rows_off_root"] == 1


def test_no_unique_dataset_row_is_its_own_skip_class(monkeypatch, tmp_path: Path) -> None:
    report, card, _root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="Some Other Model",
        evaluated="Example Model",
        display="Example Model",
    )

    assert report.quarantined == []
    assert any("no unique row" in row.reason for row in report.failures)
    assert _arena_skip_classes(report) == {"no-unique-row": 1}
    assert _evidence_row(card)["score"] == 1100.0


_RAW_ARENA_RATING = 1000.987722764275
_ROUNDED_ARENA_RATING = 1000.99


def _arena_dataset_row(**overrides) -> dict:
    row = {
        "model_name": "Example Model",
        "rating": _RAW_ARENA_RATING,
        "rating_lower": 990.125,
        "rating_upper": 1010.875,
        "vote_count": 2222,
        "leaderboard_publish_date": "2026-11-02",
        "rank": 3,
    }
    row.update(overrides)
    return row


def test_an_arena_score_is_written_with_two_decimals(monkeypatch, tmp_path: Path) -> None:
    """The card, the sentence, the id, the report and the table share one rounded score."""
    report, card, root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="Example Model",
        evaluated="Example Model",
        display="Example Model",
        dataset_rows=[_arena_dataset_row()],
    )

    assert report.failures == [], report.failures
    assert report.quarantined == [], report.quarantined
    row = _evidence_row(card)
    assert row["score"] == _ROUNDED_ARENA_RATING
    assert str(_RAW_ARENA_RATING) not in card.read_text(encoding="utf-8")
    assert "1000.99" in row["configuration"]
    assert row["id"] == refresh.evidence_id("lab/example-model", row)
    assert report.changes[0].new_value == _ROUNDED_ARENA_RATING
    rendered = refresh.render_report(report)
    assert "1000.99" in rendered
    assert str(_RAW_ARENA_RATING) not in rendered
    audit_path = tmp_path / "audit.json"
    refresh.write_audit(audit_path, report.changes)
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    assert audit[0]["new_value"] == _ROUNDED_ARENA_RATING
    assert str(_RAW_ARENA_RATING) not in audit_path.read_text(encoding="utf-8")
    log = _verification_log(root)
    assert log["outcome"] == "verified"
    assert log["diff"] is None


def test_a_rounded_arena_score_verifies_against_the_raw_dataset_value() -> None:
    """The verifier's existing tolerance accepts a score rounded to 2 decimals."""
    from decision.verify import numbers_agree, parse_quantity

    found = parse_quantity(str(_RAW_ARENA_RATING), "Arena score (Elo scale)")
    assert found is not None
    assert numbers_agree(_ROUNDED_ARENA_RATING, "Arena score (Elo scale)", found)


def test_a_raw_arena_score_on_the_card_is_reconfirmed_at_two_decimals(
    monkeypatch, tmp_path: Path,
) -> None:
    """A card score with more than 2 decimals is rewritten rounded and is not a value change."""
    raw = 1100.123456789012
    report, card, _root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="Example Model",
        evaluated="Example Model",
        display="Example Model",
        score=raw,
        configuration=(
            "Pinned LMArena dataset; publication date 2026-10-01; rating 1100.12 "
            "[1080.00, 1120.00], 1000 votes, rank 4."
        ),
        dataset_rows=[{
            "model_name": "Example Model",
            "rating": raw,
            "rating_lower": 1080.0,
            "rating_upper": 1120.0,
            "vote_count": 1000,
            "leaderboard_publish_date": "2026-10-01",
            "rank": 4,
        }],
    )

    assert report.failures == [], report.failures
    assert report.changes == []
    assert len(report.reconfirmed) == 1
    assert report.reconfirmed[0].new_value == round(raw, 2)
    row = _evidence_row(card)
    assert row["score"] == round(raw, 2)
    assert row["configuration"] == (
        "Pinned LMArena dataset; publication date 2026-10-01; rating 1100.12 "
        "[1080.00, 1120.00], 1000 votes, rank 4."
    )
    summary = report.boards["arena:text"]
    assert summary["rows_rewritten"] == 0
    assert summary["rows_reconfirmed"] == 1
    assert summary["values_changed"] == 0


def test_a_read_date_beside_the_publish_date_becomes_the_observed_date(
    monkeypatch, tmp_path: Path,
) -> None:
    before = tmp_path / "before"
    report, card, root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="Example Model",
        evaluated="Example Model",
        display="Example Model",
        snapshot=before,
        configuration=(
            "LMArena leaderboard dataset, CC BY 4.0, category overall, "
            "leaderboard_publish_date 2026-10-01, read 2026-09-24. "
            "Rank 4, 1000 votes, interval [1080.00, 1120.00]."
        ),
        dataset_rows=[_arena_dataset_row()],
    )

    assert report.failures == [], report.failures
    row = _evidence_row(card)
    assert row["score"] == _ROUNDED_ARENA_RATING
    assert row["configuration"] == (
        "LMArena leaderboard dataset, CC BY 4.0, category overall, "
        "leaderboard_publish_date 2026-11-02, read 2026-11-11. "
        "Rank 3, 2222 votes, interval [990.12, 1010.88]."
    )
    assert refresh.check_score_only(before, root).ok


def test_a_stale_snapshot_sentence_is_removed_when_the_publish_date_changes(
    monkeypatch, tmp_path: Path,
) -> None:
    before = tmp_path / "before"
    report, card, root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="Example Model",
        evaluated="Example Model",
        display="Example Model",
        snapshot=before,
        store_reading=False,
        configuration=(
            "LMArena's official leaderboard dataset, split latest, subset `text` "
            "(raw, non-style-controlled), category overall; "
            "leaderboard_publish_date 2026-10-01 is the stated date. "
            "Rating 1100.00 (95% CI 1080.00-1120.00), 1000 votes. "
            "The live arena.ai board read 2026-09-24 still shows this snapshot "
            "(same vote counts)."
        ),
        dataset_rows=[_arena_dataset_row()],
    )

    assert report.failures == [], report.failures
    row = _evidence_row(card)
    assert row["score"] == _ROUNDED_ARENA_RATING
    assert "still shows this snapshot" not in row["configuration"]
    assert "read 2026-09-24" not in row["configuration"]
    assert "leaderboard_publish_date 2026-11-02" in row["configuration"]
    assert "1000.99" in row["configuration"]
    assert "2222 votes" in row["configuration"]
    assert refresh.check_score_only(before, root).ok


def test_a_configuration_date_the_writer_cannot_retell_is_not_written(
    monkeypatch, tmp_path: Path,
) -> None:
    report, card, _root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="Example Model",
        evaluated="Example Model",
        display="Example Model",
        configuration=(
            "LMArena leaderboard dataset, category overall, "
            "leaderboard_publish_date 2026-10-01, read 2026-09-24. "
            "Tasks noted 2026-08-01. Rank 4, 1000 votes, interval [1080.00, 1120.00]."
        ),
        dataset_rows=[_arena_dataset_row()],
    )

    assert report.changes == []
    assert _evidence_row(card)["score"] == 1100.0
    assert "2026-08-01" in _evidence_row(card)["configuration"]
    matched = [
        row for row in report.failures
        if row.reason == "configuration states a date the writer cannot retell"
    ]
    assert len(matched) == 1
    assert matched[0].model_id == "lab/example-model"
    assert matched[0].benchmark == "arena_elo_overall"


@pytest.mark.parametrize("extra", [
    "model gpt-4o-2024-08-06",
    "model `gpt-4o-2024-08-06` noted `2024-08-06`",
    "see https://example.test/cards?id=gpt-4o&on=2024-08-06",
])
def test_a_date_inside_an_id_backticks_or_a_url_is_written(
    monkeypatch, tmp_path: Path, extra: str,
) -> None:
    """Those dates are not a date the writer can retell, and the token stays."""
    report, card, _root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="Example Model",
        evaluated="Example Model",
        display="Example Model",
        configuration=(
            "LMArena leaderboard dataset, CC BY 4.0, category overall, "
            "leaderboard_publish_date 2026-10-01, read 2026-09-24. "
            f"{extra}. "
            "Rank 4, 1000 votes, interval [1080.00, 1120.00]."
        ),
        dataset_rows=[_arena_dataset_row()],
    )

    assert report.failures == [], report.failures
    sentence = _evidence_row(card)["configuration"]
    assert extra in sentence
    assert "leaderboard_publish_date 2026-11-02, read 2026-11-11" in sentence
    assert "2024-08-06" in sentence


def test_an_unchanged_publish_date_leaves_the_configuration_sentence_alone(
    monkeypatch, tmp_path: Path,
) -> None:
    sentence = (
        "LMArena leaderboard dataset, CC BY 4.0, category overall, "
        "leaderboard_publish_date 2026-10-01, read 2026-09-24. "
        "Rank 4, 1000 votes, interval [1080.00, 1120.00]. "
        "The live arena.ai board read 2026-09-24 still shows this snapshot "
        "(same vote counts)."
    )
    report, card, _root = _run_arena_effort_refresh(
        monkeypatch, tmp_path,
        dataset_name="Example Model",
        evaluated="Example Model",
        display="Example Model",
        configuration=sentence,
        dataset_rows=[{
            "model_name": "Example Model",
            "rating": 1100.0,
            "rating_lower": 1080.0,
            "rating_upper": 1120.0,
            "vote_count": 1000,
            "leaderboard_publish_date": "2026-10-01",
            "rank": 4,
        }],
    )

    assert report.failures == [], report.failures
    assert report.changes == []
    assert _evidence_row(card)["configuration"] == sentence
    summary = report.boards["arena:text"]
    assert summary["rows_reconfirmed"] == 1


def test_a_non_arena_score_keeps_its_precision() -> None:
    raw = 81.5123456789
    body = json.dumps({
        "rows": [{"model": "Changed Model", "score": raw, "observed_at": "2026-09-25"}],
    }).encode()
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
        "lab/model", "models/lab/model.md", [evidence("Changed Model", 80.0)], board,
    )

    assert failures == []
    assert len(changes) == 1
    assert changes[0].new_value == raw
    assert changes[0].new_value != round(raw, 2)


def test_an_added_arena_row_is_stored_rounded_and_the_next_refresh_keeps_it(
    monkeypatch, tmp_path: Path,
) -> None:
    """A release-signal add and the next refresh share one rounded score and one id."""
    raw = 1210.256789
    rounded = round(raw, 2)
    root = tmp_path / "repo"
    cache = tmp_path / "copies"
    source_id = "fixture-arena"
    _arena_effort_card(
        root, model="lab/template", evaluated="Template Model", display="Template Model",
    )
    card = root / "models" / "lab" / "new.md"
    card.write_text(
        """---
model_id: lab/new-model
display_name: Example Model
version: example-model
benchmarks:
  evidence: []
---
""",
        encoding="utf-8",
    )
    _arena_registry(root, source_id)
    (root / "verification").mkdir()
    url = f"{_ARENA_DATASET}/resolve/{_ARENA_NEW}/text/latest-00000-of-00001.parquet"
    store = refresh.CopyStore(cache)
    projection = refresh.readers.document(
        [_arena_dataset_row(rating=raw, rating_lower=1190.0, rating_upper=1230.0)],
        url=url, page_ref="sha256:" + "b" * 64, read_date="2026-11-11", note="fixture",
    )
    board = refresh._reading_from_projection(
        key="arena:text", source_id=source_id, benchmarks=("arena_elo_overall",),
        source_url=url, projected=projection, observed_at="2026-11-11",
        value_field="rating", store=store, card_urls=(_ARENA_DATASET,),
    )
    monkeypatch.delenv(refresh.ARENA_REVISION_ENV, raising=False)
    monkeypatch.setattr(
        refresh.readers, "resolve_arena_revision",
        lambda _fetch: refresh.readers.ArenaRevision(sha=_ARENA_NEW),
    )
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([board], []))

    added = refresh.run(
        observed_at="2026-11-11", dry_run=False, root=root, source_cache=cache,
        model_ids=("lab/new-model",), add_missing=True, arena_latest=True,
    )

    assert added.quarantined == [], added.quarantined
    assert added.failures == [], added.failures
    assert added.added == 1
    row = _evidence_row(card)
    assert row["score"] == rounded
    assert row["score"] != raw
    assert row["id"] == refresh.evidence_id("lab/new-model", row)
    raw_row = {**row, "score": raw}
    assert row["id"] != refresh.evidence_id("lab/new-model", raw_row)

    again = refresh.run(
        observed_at="2026-11-11", dry_run=False, root=root, source_cache=cache,
        model_ids=("lab/new-model",), arena_latest=True,
    )

    assert again.failures == [], again.failures
    assert again.quarantined == [], again.quarantined
    assert again.changes == []
    assert len(again.reconfirmed) == 1
    kept = _evidence_row(card)
    assert kept["score"] == rounded
    assert kept["id"] == row["id"]


def test_an_added_non_arena_row_keeps_its_precision(monkeypatch, tmp_path: Path) -> None:
    shown = "81.5123456789%"
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
        [{"model": "New Model", "score": shown}],
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
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([board], []))

    report = refresh.run(
        observed_at="2026-09-26", dry_run=False, root=root, source_cache=cache,
        model_ids=("lab/new",), add_missing=True,
    )

    assert report.quarantined == [], report.quarantined
    assert report.failures == [], report.failures
    row = refresh._front(card)["benchmarks"]["evidence"][0]
    expected = refresh.readers.parse_quantity(shown).number
    assert row["score"] == expected
    assert row["score"] != round(expected, 2)


def _arena_read_date_cards(tmp_path: Path, after_sentence: str, *, evidence_date: str,
                           observed_at: str) -> tuple[str, str]:
    before_sentence = (
        "leaderboard_publish_date 2026-09-13, read 2026-09-24. Rank 4, 1000 votes. "
        "The live arena.ai board read 2026-09-24 still shows this snapshot "
        "(same vote counts)."
    )
    before_text = _arena_guard_card("2026-09-13").replace(
        "    date_type: published\n",
        f"    date_type: published\n    configuration: {before_sentence}\n",
    )
    after_text = before_text.replace("score: 72.0", "score: 73.0").replace(
        "evidence_date: '2026-09-01'", f"evidence_date: '{evidence_date}'",
    ).replace(
        "observed_at: '2026-09-13'", f"observed_at: '{observed_at}'",
    ).replace(
        "verified_at: '2026-09-13'", f"verified_at: '{observed_at}'",
    ).replace(
        "    id: lab/model#stable\n",
        "    n: 2222\n    id: lab/model#stable\n",
    ).replace(before_sentence, after_sentence)
    return before_text, after_text


def test_score_only_check_accepts_a_retold_read_date_and_a_removed_snapshot_sentence(
    tmp_path: Path,
) -> None:
    before_text, after_text = _arena_read_date_cards(
        tmp_path,
        "leaderboard_publish_date 2026-11-02, read 2026-11-12. Rank 3, 2222 votes.",
        evidence_date="2026-11-02",
        observed_at="2026-11-12",
    )

    assert _guard_result(tmp_path, before_text, after_text).ok


def test_score_only_check_refuses_a_word_change_beside_a_retold_read_date(
    tmp_path: Path,
) -> None:
    before_text, after_text = _arena_read_date_cards(
        tmp_path,
        "leaderboard_publish_date 2026-11-02, read 2026-11-12. Place 3, 2222 votes.",
        evidence_date="2026-11-02",
        observed_at="2026-11-12",
    )
    result = _guard_result(tmp_path / "word", before_text, after_text)

    assert not result.ok
    assert result.errors == ("non-score card data changed: models/lab/model.md",)


def test_score_only_check_refuses_snapshot_removal_when_the_publish_date_stays(
    tmp_path: Path,
) -> None:
    before_text, after_text = _arena_read_date_cards(
        tmp_path,
        "leaderboard_publish_date 2026-09-13, read 2026-09-24. Rank 4, 1000 votes.",
        evidence_date="2026-09-13",
        observed_at="2026-09-13",
    )
    result = _guard_result(tmp_path / "kept", before_text, after_text)

    assert not result.ok
    assert result.errors == ("non-score card data changed: models/lab/model.md",)


def test_the_matharena_index_marks_only_retired_competitions() -> None:
    import gzip

    index = gzip.decompress(
        (FIXTURES / "matharena_index_2026-09-29.html.gz").read_bytes()).decode()
    assert refresh.readers.matharena_deprecated(index, "aime--aime_2026") is True
    assert refresh.readers.matharena_deprecated(index, "overall--brokenarxiv") is False
    assert refresh.readers.matharena_deprecated(index, "overall--arxivmath") is False
    with pytest.raises(ValueError, match="no competition"):
        refresh.readers.matharena_deprecated(index, "aime--aime_2099")
