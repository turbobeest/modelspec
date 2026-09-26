"""Weekly live-board refreshes are deterministic and score-only (MODEL-124)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

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


def test_weekly_workflow_uses_the_guard_pat_and_audit_artifact() -> None:
    workflow = (Path(__file__).parents[1] / ".github" / "workflows" /
                "leaderboard-refresh.yml").read_text(encoding="utf-8")

    assert "cron: '20 6 * * 1'" in workflow
    assert "workflow_dispatch:" in workflow
    assert "RESEARCH_PR_TOKEN" in workflow
    assert "check_score_only" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "steps.result.outputs.updates != '0'" in workflow
    assert "len(report['changes']) + len(report['reconfirmed'])" in workflow
    assert "gh pr merge --auto --squash" in workflow
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
