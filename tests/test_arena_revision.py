"""The weekly refresh can advance the Arena revision without editing the pin."""

from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from scripts import refresh_leaderboards as refresh

PIN = refresh.ARENA_REVISION
NEW = "0123456789abcdef0123456789abcdef01234567"
API = "https://huggingface.co/api/datasets/lmarena-ai/leaderboard-dataset"
DATASET = "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset"
ENV = "MODELSPEC_ARENA_REVISION"
ARENA_REVISION_EXPRESSION = "${{ vars.MODELSPEC_ARENA_REVISION || 'pinned' }}"
PRIVATE_WRITERS = Path(__file__).resolve().parents[1] / ".github" / "private-writers"
REFRESH_ENTRYPOINTS = ("scripts.refresh_leaderboards", "scripts.process_release_signals")


def test_resolver_reads_a_40_hex_dataset_sha() -> None:
    def fetch(url: str) -> bytes:
        assert url == API
        return json.dumps({
            "sha": NEW,
            "lastModified": "2026-11-02T03:04:05.000Z",
        }).encode()

    got = refresh.readers.resolve_arena_revision(fetch)

    assert got.sha == NEW
    assert got.fallback is None
    assert got.modified == "2026-11-02T03:04:05.000Z"


@pytest.mark.parametrize("body", [
    b"not-json",
    b"[]",
    b'{"sha": "NOPE"}',
    b'{"sha": "1880dbebff5ba3e2dd3865ecf6fc43539c2099db "}',
    b'{"sha": "1880DBEBFF5BA3E2DD3865ECF6FC43539C2099DB"}',
    b"{}",
])
def test_resolver_falls_back_on_a_malformed_response(body: bytes) -> None:
    got = refresh.readers.resolve_arena_revision(lambda _url: body)

    assert got.sha == PIN
    assert got.fallback


def test_resolver_falls_back_on_a_network_error() -> None:
    def fetch(_url: str) -> bytes:
        raise OSError("offline")

    got = refresh.readers.resolve_arena_revision(fetch)

    assert got.sha == PIN
    assert got.fallback is not None
    assert "OSError" in got.fallback
    assert "offline" in got.fallback


def test_flag_off_does_not_ask_the_dataset_api(monkeypatch: pytest.MonkeyPatch) -> None:
    def fetch(_url: str) -> bytes:
        raise AssertionError("dataset API was called")

    monkeypatch.setattr(refresh, "_fetch", fetch)

    got = refresh.choose_arena_revision(False)

    assert got.sha == PIN
    assert got.fallback is None


def test_cli_without_the_flag_leaves_the_setting_open(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict = {}

    def run(**kwargs):
        captured.update(kwargs)
        return refresh.RefreshReport()

    monkeypatch.setattr(refresh, "run", run)
    refresh.main(["--dry-run", "--observed-at", "2026-11-11"])

    assert captured["arena_latest"] is None


def test_cli_flag_requests_the_latest_revision(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict = {}

    def run(**kwargs):
        captured.update(kwargs)
        return refresh.RefreshReport()

    monkeypatch.setattr(refresh, "run", run)
    refresh.main(["--arena-latest", "--dry-run", "--observed-at", "2026-11-11"])

    assert captured["arena_latest"] is True


def test_run_without_the_flag_reads_the_pin(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    monkeypatch.delenv(ENV, raising=False)

    def resolve(_fetch):
        raise AssertionError("resolver was called")

    seen: dict = {}

    def collect(_observed_at, _store, _tau_urls, arena_revision=None, **_kwargs):
        seen["revision"] = arena_revision
        return [], []

    monkeypatch.setattr(refresh.readers, "resolve_arena_revision", resolve)
    monkeypatch.setattr(refresh, "collect_readings", collect)

    report = refresh.run(
        observed_at="2026-11-11", dry_run=True, root=tmp_path, model_ids=(),
    )

    assert seen["revision"] == PIN
    assert report.arena_revision == PIN
    assert report.arena_revision_fallback is None
    text = refresh.render_report(report)
    assert PIN in text
    assert "pinned default" in text


def test_run_with_the_flag_records_the_resolved_revision(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    def resolve(_fetch):
        return refresh.readers.ArenaRevision(sha=NEW, fallback=None, modified="2026-11-02")

    seen: dict = {}

    def collect(_observed_at, _store, _tau_urls, arena_revision=None, **_kwargs):
        seen["revision"] = arena_revision
        return [], []

    monkeypatch.setattr(refresh.readers, "resolve_arena_revision", resolve)
    monkeypatch.setattr(refresh, "collect_readings", collect)

    report = refresh.run(
        observed_at="2026-11-11", dry_run=True, root=tmp_path, model_ids=(),
        arena_latest=True,
    )

    assert seen["revision"] == NEW
    assert report.arena_revision == NEW
    assert report.arena_revision_fallback is None
    assert NEW in refresh.render_report(report)
    path = tmp_path / "report.json"
    refresh.write_report_json(path, report)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["arena_revision"] == NEW
    assert payload["arena_revision_fallback"] is None
    assert payload["arena_revision_latest"] is True


def test_run_with_the_flag_names_a_fallback_and_still_finishes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    def resolve(_fetch):
        return refresh.readers.ArenaRevision(sha=PIN, fallback="OSError: offline")

    seen: dict = {}

    def collect(_observed_at, _store, _tau_urls, arena_revision=None, **_kwargs):
        seen["revision"] = arena_revision
        return [], []

    monkeypatch.setattr(refresh.readers, "resolve_arena_revision", resolve)
    monkeypatch.setattr(refresh, "collect_readings", collect)

    report = refresh.run(
        observed_at="2026-11-11", dry_run=True, root=tmp_path, model_ids=(),
        arena_latest=True,
    )

    assert seen["revision"] == PIN
    text = refresh.render_report(report)
    assert f"Arena revision: {PIN} read, no rows written: resolver fallback: OSError: offline" in text
    assert "fallback to the pinned default" not in text


def test_collect_without_a_revision_stays_on_the_pin(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    fetched: list[str] = []

    def fetch(url: str) -> bytes:
        fetched.append(url)
        raise OSError("stop")

    monkeypatch.setattr(refresh, "_fetch", fetch)
    refresh.collect_readings("2026-11-11", refresh.CopyStore(tmp_path), ())

    arena = [url for url in fetched if "leaderboard-dataset/resolve/" in url]
    assert arena
    assert all(PIN in url for url in arena)
    assert API not in fetched


def _arena_card(root: Path, rows: list[tuple[str, str, str]]) -> Path:
    """One card. Each tuple is benchmark id, source id, score."""
    evidence = []
    for benchmark_id, source_id, score in rows:
        evidence.append(
            f"""  - benchmark_id: {benchmark_id}
    model_id_as_evaluated: Example Model
    score: {score}
    unit: Arena score (Elo scale)
    source_url: {DATASET}
    source_kind: independent_evaluator
    evidence_date: '2026-11-01'
    date_type: published
    verified_at: '2026-11-01'
    id: lab/model#{benchmark_id}#old
    sources:
    - source_id: {source_id}
      snapshot_ref: sha256:{'a' * 64}
      cited_regions: [rows]
"""
        )
    card = root / "models" / "lab" / "model.md"
    card.parent.mkdir(parents=True)
    card.write_text(
        "---\nmodel_id: lab/model\ndisplay_name: Example Model\nversion: example\n"
        "benchmarks:\n  evidence:\n" + "".join(evidence) + "---\n",
        encoding="utf-8",
    )
    return card


def _registry(root: Path, sources: dict[str, str]) -> None:
    body = ["schema_version: 1", "sources:"]
    for source_id, url in sources.items():
        body.append(
            f"- id: {source_id}\n"
            f"  url: {url}\n"
            "  fetch: http\n"
            "  normaliser: text-default\n"
            "  cited_regions:\n"
            "  - id: rows\n"
            "    locator: {kind: page, value: ''}\n"
        )
    path = root / "registry" / "sources.yaml"
    path.parent.mkdir(parents=True)
    path.write_text("".join(line if line.endswith("\n") else line + "\n" for line in body),
                    encoding="utf-8")


def _arena_reading(cache: Path, *, source_id: str, benchmark: str, revision: str):
    url = (
        "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/"
        f"{revision}/text/latest-00000-of-00001.parquet"
    )
    store = refresh.CopyStore(cache)
    projection = refresh.readers.document(
        [{
            "model_name": "Example Model",
            "rating": 1200.0,
            "leaderboard_publish_date": "2026-11-01",
        }],
        url=url, page_ref="sha256:" + "b" * 64, read_date="2026-11-11", note="test",
    )
    return refresh._reading_from_projection(
        key=f"arena:{benchmark}", source_id=source_id, benchmarks=(benchmark,),
        source_url=url, projected=projection, observed_at="2026-11-11",
        value_field="rating", store=store, card_urls=(DATASET,),
    )


def _run_latest(monkeypatch: pytest.MonkeyPatch, root: Path, cache: Path, boards) -> refresh.RefreshReport:
    monkeypatch.delenv(ENV, raising=False)
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: (boards, []))
    monkeypatch.setattr(
        refresh.readers, "resolve_arena_revision",
        lambda _fetch: refresh.readers.ArenaRevision(sha=NEW, fallback=None),
    )
    (root / "verification").mkdir(exist_ok=True)
    return refresh.run(
        observed_at="2026-11-11", dry_run=False, root=root, source_cache=cache,
        model_ids=("lab/model",), arena_latest=True,
    )


def test_rewritten_row_cites_the_revision_that_was_read(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    cache = tmp_path / "copies"
    source_id = "model-160-arena-text"
    card = _arena_card(root, [("arena_elo_overall", source_id, "1100.0")])
    _registry(root, {
        source_id: (
            "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/"
            f"{NEW}/text/latest-00000-of-00001.parquet"
        ),
    })
    board = _arena_reading(cache, source_id=source_id, benchmark="arena_elo_overall", revision=NEW)

    report = _run_latest(monkeypatch, root, cache, [board])

    assert report.quarantined == []
    assert len(report.changes) == 1
    assert report.changes[0].source == board.source_url
    assert NEW in report.changes[0].source
    row = yaml.safe_load(card.read_text(encoding="utf-8").split("---", 2)[1])[
        "benchmarks"
    ]["evidence"][0]
    assert row["source_url"] == DATASET
    assert row["sources"][0]["source_id"] == source_id
    cited = str(refresh.load_sources(root / "registry" / "sources.yaml")[source_id].url)
    assert NEW in cited
    assert PIN not in cited
    retained = refresh.CopyStore(cache).path(row["sources"][0]["snapshot_ref"]).read_bytes()
    assert NEW.encode() in retained
    assert board.source_url.encode() in retained


def test_latest_mode_writes_no_arena_rows_when_the_registry_cites_another_revision(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    cache = tmp_path / "copies"
    text_id = "model-160-arena-text"
    vision_id = "model-160-arena-vision"
    card = _arena_card(root, [
        ("arena_elo_overall", text_id, "1100.0"),
        ("arena_elo_vision", vision_id, "900.0"),
    ])
    pinned = (
        "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/"
        f"{PIN}/text/latest-00000-of-00001.parquet"
    )
    _registry(root, {text_id: pinned, vision_id: pinned.replace("/text/", "/vision/")})
    boards = [
        _arena_reading(cache, source_id=text_id, benchmark="arena_elo_overall", revision=NEW),
        _arena_reading(cache, source_id=vision_id, benchmark="arena_elo_vision", revision=NEW),
    ]

    report = _run_latest(monkeypatch, root, cache, boards)

    text = refresh.render_report(report)
    conflicts = [row for row in report.failures if "registry cites a different revision" in row.reason]
    assert len(conflicts) == 1
    assert text_id in conflicts[0].reason
    assert vision_id in conflicts[0].reason
    assert "registry cites a different revision" in text
    _assert_revision_withheld(report, NEW)
    assert report.changes == []
    written = yaml.safe_load(card.read_text(encoding="utf-8").split("---", 2)[1])
    assert [row["score"] for row in written["benchmarks"]["evidence"]] == [1100.0, 900.0]
    path = tmp_path / "report.json"
    refresh.write_report_json(path, report)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert sum(
        "registry cites a different revision" in row["reason"] for row in payload["failures"]
    ) == 1


def test_latest_mode_writes_arena_rows_when_the_registry_url_has_no_revision(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    cache = tmp_path / "copies"
    source_id = "model-160-arena-text"
    card = _arena_card(root, [("arena_elo_overall", source_id, "1100.0")])
    _registry(root, {source_id: DATASET})
    board = _arena_reading(cache, source_id=source_id, benchmark="arena_elo_overall", revision=NEW)

    report = _run_latest(monkeypatch, root, cache, [board])

    assert report.quarantined == []
    assert len(report.changes) == 1
    assert NEW in report.changes[0].source
    row = yaml.safe_load(card.read_text(encoding="utf-8").split("---", 2)[1])[
        "benchmarks"
    ]["evidence"][0]
    assert row["score"] == 1200.0
    assert row["sources"][0]["source_id"] == source_id
    cited = str(refresh.load_sources(root / "registry" / "sources.yaml")[source_id].url)
    assert cited == DATASET
    assert PIN not in cited
    assert NEW not in cited


def test_run_follows_the_environment_when_the_argument_is_omitted(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    seen: dict = {}

    def resolve(_fetch):
        seen["resolved"] = True
        return refresh.readers.ArenaRevision(sha=NEW, fallback=None)

    def collect(_observed_at, _store, _tau_urls, arena_revision=None, **_kwargs):
        seen["revision"] = arena_revision
        return [], []

    monkeypatch.setattr(refresh.readers, "resolve_arena_revision", resolve)
    monkeypatch.setattr(refresh, "collect_readings", collect)
    monkeypatch.delenv(ENV, raising=False)

    report = refresh.run(
        observed_at="2026-11-11", dry_run=True, root=tmp_path, model_ids=(),
    )

    assert seen["revision"] == PIN
    assert "resolved" not in seen
    assert report.arena_revision == PIN

    monkeypatch.setenv(ENV, "latest")
    refresh.run(observed_at="2026-11-11", dry_run=True, root=tmp_path, model_ids=())

    assert seen["revision"] == NEW
    assert seen["resolved"] is True


def test_explicit_argument_wins_over_the_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    def resolve(_fetch):
        raise AssertionError("resolver was called")

    seen: dict = {}

    def collect(_observed_at, _store, _tau_urls, arena_revision=None, **_kwargs):
        seen["revision"] = arena_revision
        return [], []

    monkeypatch.setenv(ENV, "latest")
    monkeypatch.setattr(refresh.readers, "resolve_arena_revision", resolve)
    monkeypatch.setattr(refresh, "collect_readings", collect)

    report = refresh.run(
        observed_at="2026-11-11", dry_run=True, root=tmp_path, model_ids=(),
        arena_latest=False,
    )

    assert seen["revision"] == PIN
    assert report.arena_revision == PIN


def test_empty_environment_stays_on_the_pin(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    def resolve(_fetch):
        raise AssertionError("resolver was called")

    seen: dict = {}

    def collect(_observed_at, _store, _tau_urls, arena_revision=None, **_kwargs):
        seen["revision"] = arena_revision
        return [], []

    monkeypatch.setenv(ENV, "")
    monkeypatch.setattr(refresh.readers, "resolve_arena_revision", resolve)
    monkeypatch.setattr(refresh, "collect_readings", collect)

    report = refresh.run(
        observed_at="2026-11-11", dry_run=True, root=tmp_path, model_ids=(),
    )

    assert seen["revision"] == PIN
    assert report.arena_revision == PIN


def test_an_unknown_environment_value_names_the_variable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    monkeypatch.setenv(ENV, "head")

    with pytest.raises(ValueError, match="MODELSPEC_ARENA_REVISION"):
        refresh.run(
            observed_at="2026-11-11", dry_run=True, root=tmp_path, model_ids=(),
        )


def test_release_signal_follows_the_arena_revision_variable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    from release_signals.pipeline import GatherResult, Resolution
    from scripts import process_release_signals as processor

    root = tmp_path / "repo"
    card = root / "models" / "acme" / "orbit-1.md"
    card.parent.mkdir(parents=True)
    card.write_text("---\nmodel_id: acme/orbit-1\n---\n", encoding="utf-8")
    (root / "verification").mkdir()
    pending = tmp_path / "pending.json"
    pending.write_text(
        json.dumps({"signals": [{"model_name": "Orbit 1", "provider": "Acme",
                                 "first_seen_url": "https://x.com/acme/status/123456789",
                                 "timestamp": "2026-11-11T00:00:00Z", "confidence": 0.9,
                                 "signal_id": "grok-20261111-123456789"}]}),
        encoding="utf-8",
    )
    seen: list[str | None] = []

    def collect(_observed_at, _store, _tau_urls, arena_revision=None, **_kwargs):
        seen.append(arena_revision)
        return [], []

    def resolve(_fetch):
        return refresh.readers.ArenaRevision(sha=NEW, fallback=None)

    monkeypatch.setattr(
        processor, "resolve_signal",
        lambda *_args, **_kwargs: Resolution("existing", "acme/orbit-1"),
    )
    monkeypatch.setattr(
        processor, "gather_signal",
        lambda *_args, **_kwargs: GatherResult(
            resolution=Resolution("existing", "acme/orbit-1"),
        ),
    )
    monkeypatch.setattr(processor, "update_existing_card", lambda *_args, **_kwargs: card)
    monkeypatch.setattr(refresh, "collect_readings", collect)
    monkeypatch.setattr(refresh.readers, "resolve_arena_revision", resolve)
    monkeypatch.delenv(ENV, raising=False)

    processor.process(pending, tmp_path / "unset.json", root=root)

    assert seen == [PIN]

    monkeypatch.setenv(ENV, "latest")
    processor.process(pending, tmp_path / "latest.json", root=root)

    assert seen == [PIN, NEW]


def _run_invokes(run: str, module: str) -> bool:
    return (
        f"-m {module}" in run
        or f'run_module("{module}"' in run
        or f"run_module('{module}'" in run
    )


def test_every_private_writer_refresh_reads_the_arena_revision_variable() -> None:
    found = []
    for path in sorted(PRIVATE_WRITERS.glob("*.yml")):
        document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for job in (document.get("jobs") or {}).values():
            for step in job.get("steps") or []:
                run = step.get("run")
                if not isinstance(run, str):
                    continue
                if not any(_run_invokes(run, module) for module in REFRESH_ENTRYPOINTS):
                    continue
                env = step.get("env") or {}
                found.append((path.name, step.get("name"), env.get(ENV)))

    assert found == [
        ("leaderboard-refresh.yml", "Re-read every covered board once", ARENA_REVISION_EXPRESSION),
        ("release-signals.yml", "Process one isolated work item", ARENA_REVISION_EXPRESSION),
    ]


def test_weekly_workflow_keeps_the_arena_revision_pinned() -> None:
    path = PRIVATE_WRITERS / "leaderboard-refresh.yml"
    text = path.read_text(encoding="utf-8")

    assert f"{ENV}: {ARENA_REVISION_EXPRESSION}" in text
    assert "--arena-latest" not in text


ARENA_CONFIGS = {
    "text", "text_style_control", "vision", "vision_style_control",
    "document", "text_factuality", "webdev",
}


def _config_of(url: str) -> str:
    return url.split("/resolve/", 1)[1].split("/", 2)[1]


def test_resolver_fallback_is_a_reported_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    def resolve(_fetch):
        return refresh.readers.ArenaRevision(sha=PIN, fallback="OSError: offline")

    monkeypatch.setattr(refresh.readers, "resolve_arena_revision", resolve)
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([], []))
    monkeypatch.delenv(ENV, raising=False)

    report = refresh.run(
        observed_at="2026-11-11", dry_run=True, root=tmp_path, model_ids=(),
        arena_latest=True,
    )

    assert report.arena_revision == PIN
    reasons = [row.reason for row in report.failures]
    assert any(reason.startswith("resolver fallback:") and "OSError: offline" in reason
               for reason in reasons)
    assert "resolver fallback:" in refresh.render_report(report)
    path = tmp_path / "report.json"
    refresh.write_report_json(path, report)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert any(row["reason"].startswith("resolver fallback:") for row in payload["failures"])


def test_latest_mode_reads_all_seven_configs_at_one_revision(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    fetched: list[str] = []
    projected: list[str] = []

    def fetch(url: str) -> bytes:
        fetched.append(url)
        if url == API:
            return json.dumps({"sha": NEW}).encode()
        if "leaderboard-dataset/resolve/" in url and NEW in url:
            return b"fixture"
        raise OSError(url)

    def project(_parquet, _config, _category, *, url, page_ref, read_date):
        projected.append(url)
        return refresh.readers.document(
            [{"model_name": "Example", "rating": 1.0, "leaderboard_publish_date": "2026-11-01"}],
            url=url, page_ref=page_ref, read_date=read_date, note="test",
        )

    monkeypatch.setenv(ENV, "latest")
    monkeypatch.setattr(refresh, "_fetch", fetch)
    monkeypatch.setattr(refresh.readers, "project_arena", project)

    report = refresh.run(
        observed_at="2026-11-11", dry_run=True, root=tmp_path, model_ids=(),
        source_cache=tmp_path / "copies",
    )

    head = [url for url in fetched if "leaderboard-dataset/resolve/" in url]
    assert {_config_of(url) for url in head} == ARENA_CONFIGS
    assert all(NEW in url for url in head)
    assert all(NEW in url for url in projected)
    assert len(projected) == len(refresh.ARENA_BOARDS)
    assert report.arena_revision == NEW
    assert not any(row.reason.startswith("config fallback:") for row in report.failures)


FRONTIER_DATA = "https://cognition.com/data/frontiercode-leaderboard/data.json"
FRONTIER_ID = "model-160-frontiercode"
TEXT_ID = "model-160-arena-text"


def _frontier_bytes() -> bytes:
    return json.dumps({
        "v1_1": {
            "data": {
                "Example Model": {
                    "none": {"main": {"new_score": 0.5, "correct": 0.25}},
                },
            },
        },
    }).encode()


def _changed_arena(_parquet, _config, _category, *, url, page_ref, read_date):
    return refresh.readers.document(
        [{
            "model_name": "Example Model",
            "rating": 1200.0,
            "leaderboard_publish_date": "2026-11-09",
        }],
        url=url, page_ref=page_ref, read_date=read_date, note="test",
    )


def _two_board_card(root: Path) -> Path:
    frontier_url = refresh.readers.FRONTIERCODE_URL
    card = root / "models" / "lab" / "model.md"
    card.parent.mkdir(parents=True)
    card.write_text(
        f"""---
model_id: lab/model
display_name: Example Model
version: example
benchmarks:
  evidence:
  - benchmark_id: arena_elo_overall
    model_id_as_evaluated: Example Model
    score: 1100.0
    unit: Arena score (Elo scale)
    source_url: {DATASET}
    source_kind: independent_evaluator
    evidence_date: '2026-11-01'
    date_type: published
    verified_at: '2026-11-01'
    id: lab/model#arena_elo_overall#old
    sources:
    - source_id: {TEXT_ID}
      snapshot_ref: sha256:{'a' * 64}
      cited_regions: [rows]
  - benchmark_id: frontiercode_v1_1
    model_id_as_evaluated: Example Model
    score: 10.0
    unit: percent
    source_url: {frontier_url}
    source_kind: benchmark_author
    evidence_date: '2026-11-01'
    date_type: published
    verified_at: '2026-11-01'
    id: lab/model#frontiercode_v1_1#old
    sources:
    - source_id: {FRONTIER_ID}
      snapshot_ref: sha256:{'c' * 64}
      cited_regions: [rows]
---
""",
        encoding="utf-8",
    )
    return card


def _scores(card: Path) -> dict[str, float]:
    front = yaml.safe_load(card.read_text(encoding="utf-8").split("---", 2)[1])
    return {
        row["benchmark_id"]: row["score"]
        for row in front["benchmarks"]["evidence"]
    }


def _arena_failures(report: refresh.RefreshReport) -> list[refresh.RowFailure]:
    return [
        row for row in report.failures
        if row.benchmark == "arena"
        or row.benchmark.startswith("arena:")
        or row.benchmark.startswith("arena_")
    ]


def _assert_revision_withheld(report: refresh.RefreshReport, sha: str) -> None:
    reason = next(
        row.reason for row in report.failures
        if row.reason.startswith("resolver fallback:")
        or row.reason.startswith("config fallback:")
        or "registry cites a different revision" in row.reason
    )
    lines = [
        line for line in refresh.render_report(report).splitlines()
        if line.startswith("Arena revision:")
    ]
    assert lines == [f"Arena revision: {sha} read, no rows written: {reason}"]


def _latest_with_other_board(monkeypatch, tmp_path, fetch, project):
    root = tmp_path / "repo"
    cache = tmp_path / "copies"
    card = _two_board_card(root)
    _registry(root, {
        TEXT_ID: (
            "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/"
            f"{PIN}/text/latest-00000-of-00001.parquet"
        ),
        FRONTIER_ID: refresh.readers.FRONTIERCODE_URL,
    })
    (root / "verification").mkdir(parents=True)
    monkeypatch.delenv(ENV, raising=False)
    monkeypatch.setattr(refresh, "_fetch", fetch)
    monkeypatch.setattr(refresh.readers, "project_arena", project)
    report = refresh.run(
        observed_at="2026-11-11", dry_run=False, root=root, source_cache=cache,
        model_ids=("lab/model",), arena_latest=True,
    )
    return report, card


def _assert_latest_fallback_writes_nothing(report, card, fetched, projected) -> None:
    assert _scores(card)["arena_elo_overall"] == 1100.0
    assert _scores(card)["frontiercode_v1_1"] == 50.0
    assert [change.benchmark for change in report.changes] == ["frontiercode_v1_1"]
    assert projected == []
    assert not any(
        "leaderboard-dataset/resolve/" in url and PIN in url for url in fetched
    )
    assert len(_arena_failures(report)) == 1


def test_latest_resolver_error_writes_no_arena_rows(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    fetched: list[str] = []
    projected: list[str] = []

    def fetch(url: str) -> bytes:
        fetched.append(url)
        if url == API:
            raise OSError("offline")
        if "leaderboard-dataset/resolve/" in url:
            return b"fixture"
        if url == FRONTIER_DATA:
            return _frontier_bytes()
        raise OSError(url)

    def project(_parquet, _config, _category, *, url, page_ref, read_date):
        projected.append(url)
        return _changed_arena(
            _parquet, _config, _category, url=url, page_ref=page_ref, read_date=read_date,
        )

    report, card = _latest_with_other_board(monkeypatch, tmp_path, fetch, project)

    _assert_latest_fallback_writes_nothing(report, card, fetched, projected)
    assert not any("leaderboard-dataset/resolve/" in url for url in fetched)
    reason = _arena_failures(report)[0].reason
    assert reason.startswith("resolver fallback:")
    assert "OSError" in reason
    assert "offline" in reason
    _assert_revision_withheld(report, PIN)


def test_latest_missing_config_writes_no_arena_rows(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    fetched: list[str] = []
    projected: list[str] = []

    def fetch(url: str) -> bytes:
        fetched.append(url)
        if url == API:
            return json.dumps({"sha": NEW}).encode()
        if "/document/" in url and NEW in url:
            raise OSError("missing")
        if "leaderboard-dataset/resolve/" in url:
            return b"fixture"
        if url == FRONTIER_DATA:
            return _frontier_bytes()
        raise OSError(url)

    def project(_parquet, _config, _category, *, url, page_ref, read_date):
        projected.append(url)
        return _changed_arena(
            _parquet, _config, _category, url=url, page_ref=page_ref, read_date=read_date,
        )

    report, card = _latest_with_other_board(monkeypatch, tmp_path, fetch, project)

    _assert_latest_fallback_writes_nothing(report, card, fetched, projected)
    head = [url for url in fetched if NEW in url and "leaderboard-dataset/resolve/" in url]
    assert {_config_of(url) for url in head} == ARENA_CONFIGS
    reason = _arena_failures(report)[0].reason
    assert reason.startswith("config fallback:")
    assert "document" in reason
    assert "no Arena rows written" in reason
    assert "OSError" in reason
    assert PIN not in reason
    assert report.arena_revision == NEW
    _assert_revision_withheld(report, NEW)
    path = tmp_path / "report.json"
    refresh.write_report_json(path, report)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert sum(row["reason"].startswith("config fallback:") for row in payload["failures"]) == 1


def test_latest_config_timeout_writes_no_arena_rows(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    fetched: list[str] = []
    projected: list[str] = []

    def fetch(url: str) -> bytes:
        fetched.append(url)
        if url == API:
            return json.dumps({"sha": NEW}).encode()
        if "/webdev/" in url and NEW in url:
            raise TimeoutError("timed out")
        if "leaderboard-dataset/resolve/" in url:
            return b"fixture"
        if url == FRONTIER_DATA:
            return _frontier_bytes()
        raise OSError(url)

    def project(_parquet, _config, _category, *, url, page_ref, read_date):
        projected.append(url)
        return _changed_arena(
            _parquet, _config, _category, url=url, page_ref=page_ref, read_date=read_date,
        )

    report, card = _latest_with_other_board(monkeypatch, tmp_path, fetch, project)

    _assert_latest_fallback_writes_nothing(report, card, fetched, projected)
    reason = _arena_failures(report)[0].reason
    assert reason.startswith("config fallback:")
    assert "webdev" in reason
    assert "TimeoutError" in reason
    assert "no Arena rows written" in reason
    assert report.arena_revision == NEW
    _assert_revision_withheld(report, NEW)


def test_pinned_mode_keeps_the_arena_configs_it_could_read(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    fetched: list[str] = []
    projected: list[str] = []

    def fetch(url: str) -> bytes:
        fetched.append(url)
        if "/document/" in url:
            raise OSError("missing")
        if "leaderboard-dataset/resolve/" in url:
            return b"fixture"
        raise OSError(url)

    def project(_parquet, _config, _category, *, url, page_ref, read_date):
        projected.append(url)
        return refresh.readers.document(
            [{"model_name": "Example", "rating": 1.0, "leaderboard_publish_date": "2026-11-01"}],
            url=url, page_ref=page_ref, read_date=read_date, note="test",
        )

    monkeypatch.delenv(ENV, raising=False)
    monkeypatch.setattr(refresh, "_fetch", fetch)
    monkeypatch.setattr(refresh.readers, "project_arena", project)

    report = refresh.run(
        observed_at="2026-11-11", dry_run=True, root=tmp_path, model_ids=(),
        source_cache=tmp_path / "copies",
    )

    kept = [
        benchmark for benchmark, (config, _category) in refresh.ARENA_BOARDS.items()
        if config != "document"
    ]
    assert len(projected) == len(kept)
    assert projected
    assert all(PIN in url and "/document/" not in url for url in projected)
    assert not any(row.reason.startswith("config fallback:") for row in report.failures)
    assert any(
        row.benchmark == "arena:document" and row.reason.startswith("OSError:")
        for row in report.failures
    )
    assert report.arena_revision == PIN
    assert report.arena_revision_fallback is None


def _run_with_boards(monkeypatch, root, cache, boards, *, latest: bool):
    monkeypatch.delenv(ENV, raising=False)
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: (boards, []))

    def resolve(_fetch):
        if not latest:
            raise AssertionError("resolver was called")
        return refresh.readers.ArenaRevision(sha=NEW, fallback=None)

    monkeypatch.setattr(refresh.readers, "resolve_arena_revision", resolve)
    (root / "verification").mkdir(exist_ok=True)
    return refresh.run(
        observed_at="2026-11-11", dry_run=False, root=root, source_cache=cache,
        model_ids=("lab/model",), arena_latest=latest,
    )


def _cited(root: Path, url: str):
    cache = root.parent / "copies"
    card = _arena_card(root, [("arena_elo_overall", TEXT_ID, "1100.0")])
    _registry(root, {TEXT_ID: url})
    board = _arena_reading(
        cache, source_id=TEXT_ID, benchmark="arena_elo_overall", revision=PIN,
    )
    return card, cache, board


def test_pinned_mode_writes_arena_rows_when_the_registry_cites_the_pin(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    card, cache, board = _cited(
        root,
        "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/"
        f"{PIN}/text/latest-00000-of-00001.parquet",
    )

    report = _run_with_boards(monkeypatch, root, cache, [board], latest=False)

    assert len(report.changes) == 1
    assert _scores(card)["arena_elo_overall"] == 1200.0
    assert not any("registry cites a different revision" in row.reason for row in report.failures)


def test_pinned_mode_writes_no_arena_rows_when_the_registry_cites_another_revision(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    card, cache, board = _cited(
        root,
        "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/"
        f"{NEW}/text/latest-00000-of-00001.parquet",
    )

    report = _run_with_boards(monkeypatch, root, cache, [board], latest=False)

    assert report.changes == []
    assert _scores(card)["arena_elo_overall"] == 1100.0
    conflicts = [
        row for row in report.failures if "registry cites a different revision" in row.reason
    ]
    assert len(conflicts) == 1
    assert TEXT_ID in conflicts[0].reason
    _assert_revision_withheld(report, PIN)


def test_todays_registry_matches_the_pin() -> None:
    registered = refresh.load_sources(Path("registry/sources.yaml"))
    source_ids = set()
    for _benchmark, (config, _category) in refresh.ARENA_BOARDS.items():
        if config == "webdev":
            source_ids.add("model-143-evidence-arena-webdev-json")
        else:
            source_ids.add(refresh.readers.arena_source(config))
    boards = [
        SimpleNamespace(key=f"arena:{source_id}", source_id=source_id)
        for source_id in sorted(source_ids)
    ]
    cited = [str(registered[board.source_id].url) for board in boards]
    assert any(PIN in url for url in cited)
    assert refresh.registry_revision_conflict(registered, boards, PIN) == []


def _conflict_for(root: Path, url: str, revision: str) -> list[str]:
    _registry(root, {TEXT_ID: url})
    registered = refresh.load_sources(root / "registry" / "sources.yaml")
    board = SimpleNamespace(key="arena:arena_elo_overall", source_id=TEXT_ID)
    return refresh.registry_revision_conflict(registered, [board], revision)


@pytest.mark.parametrize("kind", ["resolve", "tree", "blob"])
def test_a_matching_abbreviation_is_not_a_registry_conflict(tmp_path: Path, kind: str) -> None:
    url = (
        "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/"
        f"{kind}/{NEW[:12]}/text/latest-00000-of-00001.parquet"
    )
    assert _conflict_for(tmp_path / kind, url, NEW) == []


@pytest.mark.parametrize("kind", ["resolve", "tree", "blob"])
def test_a_differing_abbreviation_is_a_registry_conflict(tmp_path: Path, kind: str) -> None:
    url = (
        "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/"
        f"{kind}/ffffffffffff/text/latest-00000-of-00001.parquet"
    )
    assert _conflict_for(tmp_path / kind, url, NEW) == [TEXT_ID]


def test_a_six_character_hex_segment_is_not_a_revision(tmp_path: Path) -> None:
    url = (
        "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/"
        "resolve/ffffff/text/latest-00000-of-00001.parquet"
    )
    assert _conflict_for(tmp_path, url, NEW) == []


@pytest.mark.parametrize("url", [
    "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/"
    + NEW[:12] + "/text/latest-00000-of-00001.parquet",
    "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/"
    "main/text/latest-00000-of-00001.parquet",
    DATASET,
    "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/"
    "ffffff/text/latest-00000-of-00001.parquet",
])
def test_an_agreed_or_unpinned_registry_url_still_writes_arena_rows(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, url: str,
) -> None:
    root = tmp_path / "repo"
    card, cache, board = _cited(root, url)
    board = _arena_reading(
        cache, source_id=TEXT_ID, benchmark="arena_elo_overall", revision=NEW,
    )

    report = _run_with_boards(monkeypatch, root, cache, [board], latest=True)

    assert len(report.changes) == 1
    assert _scores(card)["arena_elo_overall"] == 1200.0


@pytest.mark.parametrize("sha", ["abcdef0", "ffffffffffff"])
def test_an_abbreviated_sha_that_does_not_match_writes_no_arena_rows(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, sha: str,
) -> None:
    root = tmp_path / "repo"
    url = (
        "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/"
        f"{sha}/text/latest-00000-of-00001.parquet"
    )
    card, cache, board = _cited(root, url)
    board = _arena_reading(
        cache, source_id=TEXT_ID, benchmark="arena_elo_overall", revision=NEW,
    )

    report = _run_with_boards(monkeypatch, root, cache, [board], latest=True)

    assert report.changes == []
    assert _scores(card)["arena_elo_overall"] == 1100.0
    conflicts = [
        row for row in report.failures if "registry cites a different revision" in row.reason
    ]
    assert len(conflicts) == 1
    assert TEXT_ID in conflicts[0].reason


@pytest.mark.parametrize("where", ["projection", "copy-store"])
def test_one_arena_config_error_leaves_the_other_boards(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, where: str,
) -> None:
    root = tmp_path / "repo"
    cache = tmp_path / "copies"
    card = _two_board_card(root)
    _registry(root, {
        TEXT_ID: (
            "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/"
            f"{NEW}/text/latest-00000-of-00001.parquet"
        ),
        FRONTIER_ID: refresh.readers.FRONTIERCODE_URL,
    })
    (root / "verification").mkdir()

    def fetch(url: str) -> bytes:
        if url == API:
            return json.dumps({"sha": NEW}).encode()
        if "leaderboard-dataset/resolve/" in url:
            return b"fixture"
        if url == FRONTIER_DATA:
            return _frontier_bytes()
        raise OSError(url)

    def project(_parquet, config, _category, *, url, page_ref, read_date):
        if where == "projection" and config == "document":
            raise ValueError("projection failed")
        return _changed_arena(
            _parquet, config, _category, url=url, page_ref=page_ref, read_date=read_date,
        )

    real_reading = refresh._reading_from_projection

    def reading(**kwargs):
        if where == "copy-store" and "/document/" in kwargs.get("source_url", ""):
            raise OSError("copy store full")
        return real_reading(**kwargs)

    monkeypatch.delenv(ENV, raising=False)
    monkeypatch.setattr(refresh, "_fetch", fetch)
    monkeypatch.setattr(refresh.readers, "project_arena", project)
    monkeypatch.setattr(refresh, "_reading_from_projection", reading)

    report = refresh.run(
        observed_at="2026-11-11", dry_run=False, root=root, source_cache=cache,
        model_ids=("lab/model",), arena_latest=True,
    )

    marker = "projection failed" if where == "projection" else "copy store full"
    hits = [row for row in report.failures if marker in row.reason]
    assert len(hits) == 1
    assert hits[0].benchmark == "arena:document"
    assert _scores(card)["frontiercode_v1_1"] == 50.0
    assert "frontiercode" in report.boards
    assert not any(key.startswith("arena:") and "document" in key for key in report.boards)


def test_stray_arena_revision_env_is_cleared() -> None:
    assert os.environ.get(ENV) is None


def _named_arena_card(root: Path, model_id: str, score: str, revision: str) -> Path:
    lab, name = model_id.split("/")
    card = root / "models" / lab / f"{name}.md"
    card.parent.mkdir(parents=True, exist_ok=True)
    version = (
        f"text / overall, latest split, revision {revision}"
        if revision else "text / overall, latest split"
    )
    card.write_text(
        f"""---
model_id: {model_id}
display_name: {name}
version: {name}
benchmarks:
  evidence:
  - benchmark_id: arena_elo_overall
    model_id_as_evaluated: {name}
    score: {score}
    unit: Arena score (Elo scale)
    source_url: {DATASET}
    source_kind: independent_evaluator
    evidence_date: '2026-11-01'
    date_type: published
    verified_at: '2026-11-01'
    benchmark_version: {version}
    id: {model_id}#old
    sources:
    - source_id: model-160-arena-text
      snapshot_ref: sha256:{'a' * 64}
      cited_regions: [rows]
---
""",
        encoding="utf-8",
    )
    return card


def _two_model_board(cache: Path):
    source_id = "model-160-arena-text"
    url = (
        "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/"
        f"{NEW}/text/latest-00000-of-00001.parquet"
    )
    store = refresh.CopyStore(cache)
    projection = refresh.readers.document(
        [
            {"model_name": "premier", "rating": 1200.0, "leaderboard_publish_date": "2026-11-01"},
            {"model_name": "other", "rating": 1300.0, "leaderboard_publish_date": "2026-11-01"},
        ],
        url=url, page_ref="sha256:" + "b" * 64, read_date="2026-11-11", note="test",
    )
    return refresh._reading_from_projection(
        key="arena:arena_elo_overall", source_id=source_id, benchmarks=("arena_elo_overall",),
        source_url=url, projected=projection, observed_at="2026-11-11",
        value_field="rating", store=store, card_urls=(DATASET,),
    )


def _catalogue(root: Path, *, cited: str) -> tuple[Path, Path]:
    (root / "premier").mkdir(parents=True)
    (root / "verification").mkdir()
    (root / "premier" / "slice-1.yaml").write_text(
        "models:\n- model_id: lab/premier\n", encoding="utf-8",
    )
    _registry(root, {"model-160-arena-text": DATASET})
    premier = _named_arena_card(root, "lab/premier", "1100.0", cited)
    other = _named_arena_card(root, "lab/other", "900.0", cited)
    return premier, other


def _refresh_catalogue(monkeypatch, root: Path, cache: Path, *, latest: bool,
                       model_ids: tuple[str, ...] | None = None):
    board = _two_model_board(cache)
    monkeypatch.delenv(ENV, raising=False)
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([board], []))
    monkeypatch.setattr(
        refresh.readers, "resolve_arena_revision",
        lambda _fetch: refresh.readers.ArenaRevision(sha=NEW),
    )
    return refresh.run(
        observed_at="2026-11-11", dry_run=False, root=root, source_cache=cache,
        model_ids=model_ids, arena_latest=latest,
    )


def test_latest_mode_refreshes_a_non_premier_card_when_the_revision_moves(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    premier, other = _catalogue(root, cited="")

    report = _refresh_catalogue(monkeypatch, root, tmp_path / "copies", latest=True)

    assert report.quarantined == [], report.quarantined
    assert _scores(premier)["arena_elo_overall"] == 1200.0
    assert _scores(other)["arena_elo_overall"] == 1300.0
    written = refresh._front(other)["benchmarks"]["evidence"][0]["benchmark_version"]
    assert written == "text / overall, latest split"
    assert NEW[:12] not in written


def test_pinned_mode_does_not_refresh_a_non_premier_card(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    _premier, other = _catalogue(root, cited="aaaaaaaaaaaa")

    _refresh_catalogue(monkeypatch, root, tmp_path / "copies", latest=False)

    assert _scores(other)["arena_elo_overall"] == 900.0


def test_an_explicit_model_selection_does_not_expand(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    _premier, other = _catalogue(root, cited="aaaaaaaaaaaa")

    _refresh_catalogue(
        monkeypatch, root, tmp_path / "copies", latest=True, model_ids=("lab/premier",),
    )

    assert _scores(other)["arena_elo_overall"] == 900.0


def test_latest_mode_leaves_a_non_arena_row_on_an_expanded_card_unchanged(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """A non-premier card can carry one Arena row and one other row.

    Latest mode may refresh the Arena row. The other row stays byte-identical.
    """
    root = tmp_path / "repo"
    (root / "premier").mkdir(parents=True)
    (root / "verification").mkdir()
    (root / "premier" / "slice-1.yaml").write_text(
        "models:\n- model_id: lab/premier\n", encoding="utf-8",
    )
    _registry(root, {
        "model-160-arena-text": DATASET,
        "fixture-source": "https://example.test/leaderboard.json",
    })
    _named_arena_card(root, "lab/premier", "1100.0", "")
    other = root / "models" / "lab" / "other.md"
    fixture_row = """  - benchmark_id: fixture_benchmark
    model_id_as_evaluated: other
    score: 50.0
    unit: percent
    source_url: https://example.test/leaderboard.json
    source_kind: benchmark_author
    evidence_date: '2026-11-01'
    date_type: published
    verified_at: '2026-11-01'
    id: lab/other#fixture
    sources:
    - source_id: fixture-source
      snapshot_ref: sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
      cited_regions: [rows]
"""
    other.write_text(
        f"""---
model_id: lab/other
display_name: other
version: other
benchmarks:
  evidence:
  - benchmark_id: arena_elo_overall
    model_id_as_evaluated: other
    score: 900.0
    unit: Arena score (Elo scale)
    source_url: {DATASET}
    source_kind: independent_evaluator
    evidence_date: '2026-11-01'
    date_type: published
    verified_at: '2026-11-01'
    benchmark_version: text / overall, latest split
    id: lab/other#arena
    sources:
    - source_id: model-160-arena-text
      snapshot_ref: sha256:{"a" * 64}
      cited_regions: [rows]
{fixture_row}---
""",
        encoding="utf-8",
    )
    cache = tmp_path / "copies"
    arena = _two_model_board(cache)
    store = refresh.CopyStore(cache)
    projection = refresh.readers.document(
        [{"model": "other", "score": "80%", "date": "2026-11-11"}],
        url="https://example.test/leaderboard.json",
        page_ref="sha256:" + "d" * 64,
        read_date="2026-11-11",
        note="fixture",
    )
    fixture = refresh._reading_from_projection(
        key="fixture", source_id="fixture-source", benchmarks=("fixture_benchmark",),
        source_url="https://example.test/leaderboard.json", projected=projection,
        observed_at="2026-11-11", value_field="score", store=store,
        card_urls=("https://example.test/leaderboard.json",),
    )
    monkeypatch.delenv(ENV, raising=False)
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([arena, fixture], []))
    monkeypatch.setattr(
        refresh.readers, "resolve_arena_revision",
        lambda _fetch: refresh.readers.ArenaRevision(sha=NEW),
    )

    refresh.run(
        observed_at="2026-11-11", dry_run=False, root=root, source_cache=cache,
        arena_latest=True,
    )

    written = other.read_text(encoding="utf-8")
    assert _scores(other)["arena_elo_overall"] == 1300.0
    assert fixture_row in written


def test_a_non_arena_plan_does_not_inherit_the_arena_revision(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    cache = tmp_path / "copies"
    store = refresh.CopyStore(cache)
    url = "https://example.test/leaderboard.json"
    projection = refresh.readers.document(
        [{"model": "Example Model", "score": "81%"}],
        url=url, page_ref="sha256:" + "e" * 64, read_date="2026-11-11", note="fixture",
    )
    board = refresh._reading_from_projection(
        key="fixture", source_id="fixture-source", benchmarks=("fixture_benchmark",),
        source_url=url, projected=projection, observed_at="2026-11-11",
        value_field="score", store=store, card_urls=(url,),
    )
    observations, failures = refresh._plan_observations(
        "lab/model", "models/lab/model.md",
        [{
            "benchmark_id": "fixture_benchmark",
            "model_id_as_evaluated": "Example Model",
            "score": 80.0,
            "unit": "percent",
            "source_url": url,
        }],
        board,
        revision=NEW,
    )

    assert failures == []
    assert len(observations) == 1
    assert observations[0].reading_checked is False
    assert observations[0].reading_revision == ""


def test_a_matching_revision_quote_still_refreshes_the_whole_board(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    _premier, other = _catalogue(root, cited=NEW[:12])
    before = refresh._front(other)["benchmarks"]["evidence"][0]["benchmark_version"]

    _refresh_catalogue(monkeypatch, root, tmp_path / "copies", latest=True)

    written = refresh._front(other)["benchmarks"]["evidence"][0]
    assert _scores(other)["arena_elo_overall"] == 1300.0
    assert written["benchmark_version"] == before


def test_a_board_over_the_cap_is_not_saved_as_rows_left(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    (root / "premier").mkdir(parents=True)
    (root / "verification").mkdir()
    (root / "premier" / "slice-1.yaml").write_text(
        "models:\n- model_id: lab/first\n- model_id: lab/second\n", encoding="utf-8",
    )
    _registry(root, {"model-160-arena-text": DATASET})
    first = _named_arena_card(root, "lab/first", "1100.0", "")
    second = _named_arena_card(root, "lab/second", "1100.0", "")
    monkeypatch.setattr(refresh, "ARENA_ROWS_PER_RUN", 1)
    cache = tmp_path / "copies"
    source_id = "model-160-arena-text"
    url = (
        "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/"
        f"{PIN}/text/latest-00000-of-00001.parquet"
    )
    store = refresh.CopyStore(cache)
    projection = refresh.readers.document(
        [
            {"model_name": "first", "rating": 1200.0},
            {"model_name": "second", "rating": 1300.0},
        ],
        url=url, page_ref="sha256:" + "c" * 64, read_date="2026-11-11", note="test",
    )
    board = refresh._reading_from_projection(
        key="arena:arena_elo_overall", source_id=source_id, benchmarks=("arena_elo_overall",),
        source_url=url, projected=projection, observed_at="2026-11-11",
        value_field="rating", store=store, card_urls=(DATASET,),
    )
    monkeypatch.delenv(ENV, raising=False)
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([board], []))

    report = refresh.run(
        observed_at="2026-11-11", dry_run=False, root=root, source_cache=cache,
    )

    assert _scores(first)["arena_elo_overall"] == 1100.0
    assert _scores(second)["arena_elo_overall"] == 1100.0
    assert report.arena_rows_left == 0
    assert report.boards["arena:arena_elo_overall"]["rows_planned_rewrites"] == 2
    assert report.boards["arena:arena_elo_overall"]["rows_rewritten"] == 0
    assert any("too large for the cap" in row.reason for row in report.failures)
    rendered = refresh.render_report(report)
    assert "Arena rows left" not in rendered
    path = tmp_path / "report.json"
    refresh.write_report_json(path, report)
    assert json.loads(path.read_text(encoding="utf-8"))["arena_rows_left"] == 0


def test_latest_mode_writes_nothing_when_benchmark_version_names_another_revision(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    premier, other = _catalogue(root, cited="aaaaaaaaaaaa")

    report = _refresh_catalogue(monkeypatch, root, tmp_path / "copies", latest=True)

    assert _scores(premier)["arena_elo_overall"] == 1100.0
    assert _scores(other)["arena_elo_overall"] == 900.0
    reasons = [row.reason for row in report.failures if "benchmark_version still names a revision" in row.reason]
    assert reasons == ["the cards' benchmark_version still names a revision (2)"]
    assert report.arena_rows_left == 0


def test_pinned_mode_writes_when_benchmark_version_names_the_pin(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """Today's versions quote no other revision, so the pinned gate does not fire."""
    root = tmp_path / "repo"
    premier, other = _catalogue(root, cited=PIN[:12])

    report = _refresh_catalogue(monkeypatch, root, tmp_path / "copies", latest=False)

    assert _scores(premier)["arena_elo_overall"] == 1200.0
    assert _scores(other)["arena_elo_overall"] == 900.0
    assert not any(
        "benchmark_version still names a revision" in row.reason for row in report.failures
    )
    written = refresh._front(premier)["benchmarks"]["evidence"][0]["benchmark_version"]
    assert PIN[:12] in written


def test_pinned_mode_writes_when_benchmark_version_names_no_revision(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    premier, _other = _catalogue(root, cited="")

    report = _refresh_catalogue(monkeypatch, root, tmp_path / "copies", latest=False)

    assert _scores(premier)["arena_elo_overall"] == 1200.0
    assert not any(
        "benchmark_version still names a revision" in row.reason for row in report.failures
    )


def test_pinned_mode_writes_nothing_when_benchmark_version_names_another_revision(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    premier, other = _catalogue(root, cited="aaaaaaaaaaaa")

    report = _refresh_catalogue(monkeypatch, root, tmp_path / "copies", latest=False)

    assert _scores(premier)["arena_elo_overall"] == 1100.0
    assert _scores(other)["arena_elo_overall"] == 900.0
    reasons = [
        row.reason for row in report.failures
        if "benchmark_version still names a revision" in row.reason
    ]
    assert reasons == ["the cards' benchmark_version still names a revision (1)"]
    assert report.arena_rows_left == 0


def test_a_board_that_fits_is_written_and_the_next_board_waits(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    (root / "premier").mkdir(parents=True)
    (root / "verification").mkdir()
    (root / "premier" / "slice-1.yaml").write_text(
        "models:\n- model_id: lab/older\n- model_id: lab/newer\n", encoding="utf-8",
    )
    _registry(root, {"model-160-arena-text": DATASET})
    older = _named_arena_card(root, "lab/older", "1100.0", "")
    newer = _named_arena_card(root, "lab/newer", "1100.0", "")
    older.write_text(older.read_text(encoding="utf-8").replace(
        "benchmark_id: arena_elo_overall", "benchmark_id: arena_elo_overall",
    ).replace("verified_at: '2026-11-01'", "verified_at: '2026-11-01'\n    observed_at: '2026-01-01'"))
    newer.write_text(newer.read_text(encoding="utf-8").replace(
        "benchmark_id: arena_elo_overall", "benchmark_id: arena_webdev",
    ).replace("verified_at: '2026-11-01'", "verified_at: '2026-11-01'\n    observed_at: '2026-06-01'"))
    monkeypatch.setattr(refresh, "ARENA_ROWS_PER_RUN", 1)
    cache = tmp_path / "copies"
    store = refresh.CopyStore(cache)

    def board_for(benchmark: str, model: str, rating: float) -> object:
        url = (
            "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/"
            f"{PIN}/text/latest-00000-of-00001.parquet"
        )
        projection = refresh.readers.document(
            [{"model_name": model, "rating": rating}],
            url=url, page_ref="sha256:" + "c" * 64, read_date="2026-11-11", note="test",
        )
        return refresh._reading_from_projection(
            key=f"arena:{benchmark}", source_id="model-160-arena-text",
            benchmarks=(benchmark,), source_url=url, projected=projection,
            observed_at="2026-11-11", value_field="rating", store=store, card_urls=(DATASET,),
        )

    boards = [
        board_for("arena_webdev", "newer", 1400.0),
        board_for("arena_elo_overall", "older", 1200.0),
    ]
    monkeypatch.delenv(ENV, raising=False)
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: (boards, []))

    report = refresh.run(
        observed_at="2026-11-11", dry_run=False, root=root, source_cache=cache,
    )

    assert _scores(older)["arena_elo_overall"] == 1200.0
    assert _scores(newer)["arena_webdev"] == 1100.0
    assert report.arena_rows_left == 1
    assert "Arena rows left for the next run: 1" in refresh.render_report(report)
    left_path = tmp_path / "left.json"
    refresh.write_report_json(left_path, report)
    assert json.loads(left_path.read_text(encoding="utf-8"))["arena_rows_left"] == 1
    newer_summary = report.boards["arena:arena_webdev"]
    assert newer_summary["rows_left"] == 1
    assert newer_summary["rows_rewritten"] == 0
    assert newer_summary["rows_planned_rewrites"] == 1


def _dated_card(root: Path, model_id: str, benchmark: str, observed_at: str) -> Path:
    card = _named_arena_card(root, model_id, "1100.0", "")
    text = card.read_text(encoding="utf-8").replace(
        "benchmark_id: arena_elo_overall", f"benchmark_id: {benchmark}",
    ).replace(
        "verified_at: '2026-11-01'",
        f"verified_at: '2026-11-01'\n    observed_at: '{observed_at}'",
    )
    card.write_text(text, encoding="utf-8")
    return card


def _two_board_run(monkeypatch, root: Path, cache: Path, boards: list) -> refresh.RefreshReport:
    monkeypatch.delenv(ENV, raising=False)
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: (boards, []))
    return refresh.run(
        observed_at="2026-11-11", dry_run=False, root=root, source_cache=cache,
    )


def _rating_board(cache: Path, benchmark: str, rows: list[dict]):
    url = (
        "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/"
        f"{PIN}/text/latest-00000-of-00001.parquet"
    )
    store = refresh.CopyStore(cache)
    projection = refresh.readers.document(
        rows, url=url, page_ref="sha256:" + "c" * 64, read_date="2026-11-11", note="test",
    )
    return refresh._reading_from_projection(
        key=f"arena:{benchmark}", source_id="model-160-arena-text",
        benchmarks=(benchmark,), source_url=url, projected=projection,
        observed_at="2026-11-11", value_field="rating", store=store, card_urls=(DATASET,),
    )


def test_board_order_uses_the_rows_the_run_will_write(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """A skipped row's old date does not pull its board ahead of a planned write."""
    root = tmp_path / "repo"
    (root / "premier").mkdir(parents=True)
    (root / "verification").mkdir()
    (root / "premier" / "slice-1.yaml").write_text(
        "models:\n- model_id: lab/ghost\n- model_id: lab/writer\n- model_id: lab/web\n",
        encoding="utf-8",
    )
    _registry(root, {"model-160-arena-text": DATASET})
    ghost = _dated_card(root, "lab/ghost", "arena_elo_overall", "2020-01-01")
    writer = _dated_card(root, "lab/writer", "arena_elo_overall", "2026-06-01")
    web = _dated_card(root, "lab/web", "arena_webdev", "2026-01-01")
    monkeypatch.setattr(refresh, "ARENA_ROWS_PER_RUN", 1)
    cache = tmp_path / "copies"
    boards = [
        _rating_board(cache, "arena_webdev", [
            {"model_name": "web", "rating": 1400.0},
        ]),
        _rating_board(cache, "arena_elo_overall", [
            {"model_name": "writer", "rating": 1200.0},
        ]),
    ]

    report = _two_board_run(monkeypatch, root, cache, boards)

    assert _scores(web)["arena_webdev"] == 1400.0
    assert _scores(writer)["arena_elo_overall"] == 1100.0
    assert _scores(ghost)["arena_elo_overall"] == 1100.0
    assert report.boards["arena:arena_webdev"]["rows_rewritten"] == 1
    assert report.boards["arena:arena_elo_overall"]["rows_rewritten"] == 0
    assert report.boards["arena:arena_elo_overall"]["rows_left"] == 1


def test_a_board_larger_than_the_cap_does_not_block_a_later_board(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    (root / "premier").mkdir(parents=True)
    (root / "verification").mkdir()
    (root / "premier" / "slice-1.yaml").write_text(
        "models:\n- model_id: lab/one\n- model_id: lab/two\n- model_id: lab/later\n",
        encoding="utf-8",
    )
    _registry(root, {"model-160-arena-text": DATASET})
    one = _dated_card(root, "lab/one", "arena_elo_overall", "2026-01-01")
    two = _dated_card(root, "lab/two", "arena_elo_overall", "2026-01-01")
    later = _dated_card(root, "lab/later", "arena_webdev", "2026-06-01")
    monkeypatch.setattr(refresh, "ARENA_ROWS_PER_RUN", 1)
    cache = tmp_path / "copies"
    boards = [
        _rating_board(cache, "arena_elo_overall", [
            {"model_name": "one", "rating": 1200.0},
            {"model_name": "two", "rating": 1300.0},
        ]),
        _rating_board(cache, "arena_webdev", [
            {"model_name": "later", "rating": 1400.0},
        ]),
    ]

    report = _two_board_run(monkeypatch, root, cache, boards)

    assert _scores(one)["arena_elo_overall"] == 1100.0
    assert _scores(two)["arena_elo_overall"] == 1100.0
    assert _scores(later)["arena_webdev"] == 1400.0
    assert report.boards["arena:arena_elo_overall"]["rows_rewritten"] == 0
    assert report.boards["arena:arena_webdev"]["rows_rewritten"] == 1
    assert report.arena_rows_left == 0
    assert any("too large for the cap" in row.reason for row in report.failures)


def test_an_arena_id_with_no_board_is_counted_once(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    card = root / "models" / "lab" / "model.md"
    card.parent.mkdir(parents=True)
    card.write_text(
        """---
model_id: lab/model
benchmarks:
  evidence:
  - benchmark_id: arena_elo_overall
    configuration: text overall
    benchmark_version: revision aaaaaaaaaaaa
  - benchmark_id: arena_not_a_board
    configuration: revision bbbbbbbbbbbb
    benchmark_version: revision cccccccccccc
---
""",
        encoding="utf-8",
    )

    assert refresh._arena_rows_without_board(root) == 1
