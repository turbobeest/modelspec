"""The weekly refresh can advance the Arena revision without editing the pin."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import refresh_leaderboards as refresh

PIN = refresh.ARENA_REVISION
NEW = "0123456789abcdef0123456789abcdef01234567"
API = "https://huggingface.co/api/datasets/lmarena-ai/leaderboard-dataset"


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


def test_cli_without_the_flag_keeps_the_pin(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict = {}

    def run(**kwargs):
        captured.update(kwargs)
        return refresh.RefreshReport()

    monkeypatch.setattr(refresh, "run", run)
    refresh.main(["--dry-run", "--observed-at", "2026-11-11"])

    assert captured["arena_latest"] is False


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
    def resolve(_fetch):
        raise AssertionError("resolver was called")

    seen: dict = {}

    def collect(_observed_at, _store, _tau_urls, arena_revision=None):
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

    def collect(_observed_at, _store, _tau_urls, arena_revision=None):
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

    def collect(_observed_at, _store, _tau_urls, arena_revision=None):
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


def test_rewritten_row_cites_the_revision_that_was_read(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    def fetch(url: str) -> bytes:
        if "leaderboard-dataset/resolve/" in url and NEW in url:
            return b"fixture"
        raise OSError(url)

    def project(_parquet, _config, _category, *, url, page_ref, read_date):
        assert NEW in url
        return refresh.readers.document(
            [{
                "model_name": "Example Model",
                "rating": 1200.0,
                "leaderboard_publish_date": "2026-11-01",
            }],
            url=url, page_ref=page_ref, read_date=read_date, note="test",
        )

    monkeypatch.setattr(refresh, "_fetch", fetch)
    monkeypatch.setattr(refresh.readers, "project_arena", project)

    boards, _failures = refresh.collect_readings(
        "2026-11-11", refresh.CopyStore(tmp_path), (), NEW,
    )
    board = next(item for item in boards if "arena_elo_overall" in item.benchmark_ids)
    assert NEW in board.source_url
    assert PIN not in board.source_url

    changes, failures = refresh.plan_rows(
        "lab/model",
        "models/lab/model.md",
        [{
            "benchmark_id": "arena_elo_overall",
            "model_id_as_evaluated": "Example Model",
            "score": 1100.0,
            "unit": "Arena score (Elo scale)",
            "source_url": "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset",
        }],
        board,
    )

    assert failures == []
    assert len(changes) == 1
    assert changes[0].source == board.source_url
    assert NEW in changes[0].source
