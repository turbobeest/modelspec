"""The weekly refresh can advance the Arena revision without editing the pin."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from scripts import refresh_leaderboards as refresh

PIN = refresh.ARENA_REVISION
NEW = "0123456789abcdef0123456789abcdef01234567"
API = "https://huggingface.co/api/datasets/lmarena-ai/leaderboard-dataset"
DATASET = "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset"
ENV = "MODELSPEC_ARENA_REVISION"


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
    assert "fallback to the pinned default" in text
    assert "OSError: offline" in text


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


def test_weekly_workflow_keeps_the_arena_revision_pinned() -> None:
    text = Path(".github/private-writers/leaderboard-refresh.yml").read_text(encoding="utf-8")

    assert "MODELSPEC_ARENA_REVISION: pinned" in text
    assert "revision-free" in text
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


def test_latest_mode_falls_back_every_config_when_one_is_missing(
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

    head = [url for url in fetched if NEW in url and "leaderboard-dataset/resolve/" in url]
    pin = [url for url in fetched if PIN in url and "leaderboard-dataset/resolve/" in url]
    assert {_config_of(url) for url in head} == ARENA_CONFIGS
    assert {_config_of(url) for url in pin} == ARENA_CONFIGS
    assert projected
    assert all(PIN in url and NEW not in url for url in projected)
    assert len(projected) == len(refresh.ARENA_BOARDS)
    assert report.arena_revision == PIN
    fallbacks = [row for row in report.failures if row.reason.startswith("config fallback:")]
    assert len(fallbacks) == 1
    assert "document" in fallbacks[0].reason
    assert PIN in fallbacks[0].reason
    assert "config fallback:" in refresh.render_report(report)
    path = tmp_path / "report.json"
    refresh.write_report_json(path, report)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert sum(row["reason"].startswith("config fallback:") for row in payload["failures"]) == 1
