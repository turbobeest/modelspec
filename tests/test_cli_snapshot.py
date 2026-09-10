"""The CLI contract dpf consumes.

This is an interface another program calls, so the tests pin the things a caller
depends on: that answers work offline, that the envelope is versioned, that
freshness is always disclosed, and that exit codes distinguish the cases a
script has to tell apart.
"""

from __future__ import annotations

import functools
import json
import shutil
import subprocess
import sys
import sysconfig
from datetime import UTC, datetime, timedelta
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from api.ranking.engine import USE_CASE_PROFILES  # noqa: E402
from cli.modelspec import offline, snapshot  # noqa: E402


@pytest.fixture
def cache(tmp_path: Path) -> Path:
    directory = tmp_path / "cache"
    directory.mkdir()
    return directory


def _write(directory: Path, fetched_at: datetime | None = None) -> None:
    when = fetched_at or datetime.now(UTC)
    (directory / "snapshot.json").write_text(json.dumps({
        "meta": {"fetched_at": when.isoformat(), "origin": "https://example.test",
                 "build_commit": "abc123def456", "built_at": "2026-09-09T00:00:00+00:00"},
        "data": {
            "index": {"build": {"commit": "abc123def456"}},
            "candidates": {"candidates": [
                {"model_id": "a/one", "display_name": "One", "provider": "A",
                 "model_type": "llm-chat", "benchmark_scores": {
                     b: 90.0 for b in USE_CASE_PROFILES["coding"]["benchmark_weights"]},
                 "capability_tiers": {}, "cost_input": 1.0, "context_window": 128000,
                 "open_weights": True, "fits": {"gpu": 40.0}},
            ]},
            "profiles": {"profiles": {"coding": {"benchmark_weights": {"humaneval": 1.0},
                                                 "preferred_types": ["llm-chat"]}},
                         "featured": ["coding"]},
            "hardware": {"nodes": [{"id": "gpu", "label": "Hardware", "display_name": "A GPU",
                                    "memory_gb": 24, "memory_bandwidth_gb_s": 1000}]},
        },
    }), encoding="utf-8")


# ── the snapshot ─────────────────────────────────────────────────────────────

def test_a_missing_snapshot_says_what_to_do(cache: Path) -> None:
    with pytest.raises(snapshot.SnapshotMissing, match="snapshot fetch"):
        snapshot.load(cache)


def test_loading_never_touches_the_network(cache: Path, monkeypatch) -> None:
    """The whole point is that it works on a machine with no connection."""
    import httpx

    def explode(*a, **k):
        raise AssertionError("the offline path made a network call")

    monkeypatch.setattr(httpx, "Client", explode)
    _write(cache)
    loaded = snapshot.load(cache)
    assert loaded.build_commit == "abc123def456"


def test_freshness_is_always_reported(cache: Path) -> None:
    _write(cache)
    freshness = snapshot.load(cache).freshness()
    for key in ("fetched_at", "age_days", "stale", "origin", "build_commit",
                "export_schema_version"):
        assert key in freshness
    assert freshness["export_schema_version"] == snapshot.EXPORT_SCHEMA_VERSION


def test_an_old_snapshot_is_stale_but_still_loads(cache: Path) -> None:
    """Continuity beats freshness: a dated answer beats no answer."""
    _write(cache, datetime.now(UTC) - timedelta(days=snapshot.STALE_AFTER_DAYS + 5))
    loaded = snapshot.load(cache)
    assert loaded.is_stale
    assert loaded.age_days > snapshot.STALE_AFTER_DAYS
    assert loaded.data["candidates"]["candidates"], "a stale snapshot must still answer"


def test_status_reports_absence_without_raising(cache: Path) -> None:
    assert snapshot.status(cache)["present"] is False


# ── the contract ─────────────────────────────────────────────────────────────

def test_the_envelope_is_versioned() -> None:
    assert offline.SCHEMA_VERSION
    assert offline.SCHEMA_VERSION[0].isdigit()


def test_legacy_snapshot_without_export_schema_version_is_current_shape(cache: Path) -> None:
    """Snapshots fetched before the field existed are 1.x, not an error."""
    _write(cache)
    loaded = snapshot.load(cache)
    assert loaded.export_schema_version == "1.0"
    assert "export_schema_version" not in loaded.data["index"].get("build", {})


def test_compatible_export_minor_is_accepted(cache: Path) -> None:
    _write(cache)
    path = cache / "snapshot.json"
    payload = json.loads(path.read_text())
    payload["data"]["index"]["build"]["export_schema_version"] = "1.1"
    path.write_text(json.dumps(payload))
    loaded = snapshot.load(cache)
    assert loaded.export_schema_version == "1.1"


def test_incompatible_export_schema_is_refused(cache: Path) -> None:
    _write(cache)
    path = cache / "snapshot.json"
    payload = json.loads(path.read_text())
    payload["data"]["index"]["build"]["export_schema_version"] = "2.0"
    path.write_text(json.dumps(payload))
    with pytest.raises(snapshot.SnapshotInvalid, match="export_schema_version 2.0"):
        snapshot.load(cache)


def test_incompatible_export_schema_is_a_runtime_error_without_traceback(cache: Path) -> None:
    _write(cache)
    path = cache / "snapshot.json"
    payload = json.loads(path.read_text())
    payload["data"]["index"]["build"]["export_schema_version"] = "2.0"
    path.write_text(json.dumps(payload))
    result = _run(["offline", "rank", "coding", "--json"], cache)
    assert result.returncode == offline.EXIT_ERROR
    error = json.loads(result.stderr)
    assert error["schema_version"] == offline.SCHEMA_VERSION
    assert "export_schema_version" in error["error"]["message"]
    assert "Traceback" not in result.stderr
    assert not result.stdout


def test_fetch_refuses_incompatible_export_without_clobbering(cache: Path, monkeypatch) -> None:
    import httpx

    _write(cache)
    original = (cache / "snapshot.json").read_text()

    class FakeResponse:
        def __init__(self, body: dict) -> None:
            self._body = body

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return self._body

    bodies = {
        "/api/index.json": {
            "build": {"commit": "newcommit", "built_at": "2026-09-10T00:00:00+00:00",
                      "export_schema_version": "2.0"},
        },
        "/api/rank/candidates.json": {"candidates": []},
        "/api/rank/profiles.json": {"profiles": {}},
        "/api/graph/views/hardware.json": {"nodes": []},
    }

    class FakeClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args) -> None:
            return None

        def get(self, url: str) -> FakeResponse:
            for route, body in bodies.items():
                if url.endswith(route):
                    return FakeResponse(body)
            raise AssertionError(url)

    monkeypatch.setattr(httpx, "Client", FakeClient)
    with pytest.raises(snapshot.SnapshotInvalid, match="export_schema_version 2.0"):
        snapshot.fetch("https://example.test", cache)
    assert (cache / "snapshot.json").read_text() == original


def test_exit_codes_are_distinct() -> None:
    """A caller has to tell "no answer" from "no snapshot" from "broken"."""
    codes = {offline.EXIT_OK, offline.EXIT_ERROR, offline.EXIT_NO_MATCH,
             offline.EXIT_NO_SNAPSHOT, offline.EXIT_STALE}
    assert len(codes) == 5


@functools.cache
def _modelspec_cli() -> str:
    """Absolute path to the installed ``modelspec`` console script.

    The public entry point is ``[project.scripts] modelspec = cli.modelspec.cli:app``.
    There is no ``python -m modelspec`` module (``python -m modelspec`` fails), so
    these tests locate the generated console script for *this* interpreter — the
    local venv, CI's system Python, or any other install. ``shutil.which`` alone
    is not enough: ``.venv/bin/python -m pytest`` does not put ``.venv/bin`` on
    ``PATH``. A missing CLI is an install failure, not a skip.
    """
    try:
        dist = distribution("modelspec")
    except PackageNotFoundError as exc:
        raise RuntimeError(
            "The modelspec package is not installed in this interpreter. "
            "Install it with `pip install -e '.[dev]'` so the `modelspec` "
            "console script is created."
        ) from exc
    if not any(
        ep.group == "console_scripts" and ep.name == "modelspec"
        for ep in dist.entry_points
    ):
        raise RuntimeError(
            "The installed modelspec distribution does not declare a "
            "`modelspec` console script (pyproject.toml [project.scripts])."
        )

    searched: list[Path] = [
        Path(sysconfig.get_path("scripts")) / "modelspec",
        Path(sys.executable).resolve().parent / "modelspec",
    ]
    which = shutil.which("modelspec")
    if which is not None:
        searched.append(Path(which))

    seen: set[Path] = set()
    for path in searched:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if path.is_file():
            return str(path)

    raise RuntimeError(
        "modelspec console script is declared but was not found on disk. "
        "Looked in: " + ", ".join(str(p) for p in searched) + ". "
        "Install the package into this interpreter."
    )


def _run(args: list[str], cache: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [_modelspec_cli(), *args],
        capture_output=True, text=True, timeout=120,
        env={"PATH": "/usr/bin:/bin", "MODELSPEC_CACHE": str(cache), "HOME": str(cache.parent)},
    )


def test_missing_snapshot_exits_three(cache: Path) -> None:
    result = _run(["offline", "rank", "coding"], cache)
    assert result.returncode == offline.EXIT_NO_SNAPSHOT
    assert "snapshot fetch" in result.stderr


def test_a_stale_snapshot_fails_only_when_asked(cache: Path) -> None:
    _write(cache, datetime.now(UTC) - timedelta(days=snapshot.STALE_AFTER_DAYS + 5))
    lenient = _run(["offline", "rank", "coding", "--json"], cache)
    assert lenient.returncode == offline.EXIT_OK
    assert "stale" in lenient.stderr.lower()
    strict = _run(["offline", "rank", "coding", "--require-fresh"], cache)
    assert strict.returncode == offline.EXIT_STALE


def test_json_output_carries_version_and_freshness(cache: Path) -> None:
    _write(cache)
    result = _run(["offline", "rank", "coding", "--json"], cache)
    assert result.returncode == offline.EXIT_OK
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == offline.SCHEMA_VERSION
    assert payload["command"] == "rank"
    assert payload["freshness"]["build_commit"] == "abc123def456"
    assert payload["freshness"]["export_schema_version"] == snapshot.EXPORT_SCHEMA_VERSION
    assert "export_schema_version" not in payload  # tree version lives on freshness, not the envelope
    assert payload["ranking_status"] == "complete"
    assert payload["ranked_count"] == 1
    assert payload["unranked_count"] == 0
    assert payload["result"][0]["model_id"] == "a/one"


def test_no_match_is_its_own_exit_code(cache: Path) -> None:
    """Not an error. The honest answer is sometimes "nothing fits"."""
    _write(cache)
    result = _run(["offline", "rank", "coding", "--fits", "nonexistent-gpu"], cache)
    assert result.returncode == offline.EXIT_ERROR  # unknown device is a usage error
    result = _run(["offline", "rank", "coding", "--max-cost", "0.0001"], cache)
    assert result.returncode == offline.EXIT_NO_MATCH


def test_json_status_has_the_common_envelope(cache: Path) -> None:
    _write(cache)

    result = _run(["snapshot", "status", "--json"], cache)

    assert result.returncode == offline.EXIT_OK
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == offline.SCHEMA_VERSION
    assert payload["command"] == "status"
    assert payload["freshness"]["build_commit"] == "abc123def456"
    assert payload["result"]["present"] is True
    assert result.stderr == ""


def test_json_missing_snapshot_is_structured_on_stderr(cache: Path) -> None:
    result = _run(["offline", "rank", "coding", "--json"], cache)

    assert result.returncode == offline.EXIT_NO_SNAPSHOT
    assert not result.stdout
    error = json.loads(result.stderr)
    assert error["schema_version"] == offline.SCHEMA_VERSION
    assert error["command"] == "rank"
    assert "snapshot fetch" in error["error"]["message"]


def test_parser_usage_errors_use_runtime_error_code(cache: Path) -> None:
    missing_argument = _run(["offline", "rank"], cache)
    unknown_option = _run(["offline", "rank", "coding", "--not-an-option"], cache)

    assert missing_argument.returncode == offline.EXIT_ERROR
    assert unknown_option.returncode == offline.EXIT_ERROR
    assert "Traceback" not in missing_argument.stderr
    assert "Traceback" not in unknown_option.stderr


def test_unknown_use_case_is_a_usage_error(cache: Path) -> None:
    _write(cache)
    result = _run(["offline", "rank", "not-a-use-case"], cache)
    assert result.returncode == offline.EXIT_ERROR
    assert "unknown use case" in result.stderr


@pytest.mark.parametrize("json_output", [False, True])
def test_cli_reports_sparse_evidence_without_runtime_error(cache: Path, json_output) -> None:
    _write(cache)
    path = cache / "snapshot.json"
    payload = json.loads(path.read_text())
    payload["data"]["candidates"]["candidates"][0]["benchmark_scores"] = {"scicode": 100.0}
    path.write_text(json.dumps(payload))
    result = _run(["offline", "rank", "coding", *(["--json"] if json_output else [])], cache)
    assert result.returncode == offline.EXIT_NO_MATCH
    assert "Traceback" not in result.stderr
    if json_output:
        report = json.loads(result.stdout)
        assert report["ranking_status"] == "unavailable"
        assert report["ranked_count"] == 0
        assert report["unranked_count"] == 1
        assert report["result"] == []
    else:
        assert "unavailable ordering" in result.stdout
        assert "0 ranked, 1 unranked" in result.stdout
        assert "No model has enough evidence to be ranked." in result.stdout


def test_cli_partial_ranking_is_success_and_discloses_withheld_models(cache: Path) -> None:
    _write(cache)
    path = cache / "snapshot.json"
    payload = json.loads(path.read_text())
    sparse = dict(payload["data"]["candidates"]["candidates"][0])
    sparse["model_id"] = "b/two"
    sparse["display_name"] = "Two"
    sparse["benchmark_scores"] = {"scicode": 100.0}
    payload["data"]["candidates"]["candidates"].append(sparse)
    path.write_text(json.dumps(payload))

    result = _run(["offline", "rank", "coding", "--json"], cache)

    assert result.returncode == offline.EXIT_OK
    report = json.loads(result.stdout)
    assert report["ranking_status"] == "partial"
    assert report["ranked_count"] == 1
    assert report["unranked_count"] == 1
    assert [row["model_id"] for row in report["result"]] == ["a/one"]


@pytest.mark.parametrize("snapshot_kind", ["truncated", "unreadable"])
def test_invalid_snapshot_is_a_runtime_error_without_traceback(
    cache: Path, snapshot_kind: str
) -> None:
    path = cache / "snapshot.json"
    if snapshot_kind == "truncated":
        path.write_text('{"meta":')
    else:
        path.mkdir()

    result = _run(["offline", "rank", "coding", "--json"], cache)

    assert result.returncode == offline.EXIT_ERROR
    error = json.loads(result.stderr)
    assert error["schema_version"] == offline.SCHEMA_VERSION
    assert error["command"] == "rank"
    assert "unreadable or invalid" in error["error"]["message"]
    assert "Traceback" not in result.stderr
    assert not result.stdout


def test_snapshot_fetch_unreachable_origin_is_a_runtime_error(cache: Path) -> None:
    result = _run(["snapshot", "fetch", "--origin", "http://127.0.0.1:1"], cache)

    assert result.returncode == offline.EXIT_ERROR
    assert result.stdout == ""
    assert result.stderr.startswith("error: could not fetch the snapshot:")
    assert "Traceback" not in result.stderr
