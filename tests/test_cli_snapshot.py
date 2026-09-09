"""The CLI contract dpf consumes.

This is an interface another program calls, so the tests pin the things a caller
depends on: that answers work offline, that the envelope is versioned, that
freshness is always disclosed, and that exit codes distinguish the cases a
script has to tell apart.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from cli.modelspec import offline, snapshot  # noqa: E402


@pytest.fixture
def cache(tmp_path: Path) -> Path:
    directory = tmp_path / "cache"
    directory.mkdir()
    return directory


def _write(directory: Path, fetched_at: datetime | None = None) -> None:
    when = fetched_at or datetime.now(timezone.utc)
    (directory / "snapshot.json").write_text(json.dumps({
        "meta": {"fetched_at": when.isoformat(), "origin": "https://example.test",
                 "build_commit": "abc123def456", "built_at": "2026-09-09T00:00:00+00:00"},
        "data": {
            "index": {"build": {"commit": "abc123def456"}},
            "candidates": {"candidates": [
                {"model_id": "a/one", "display_name": "One", "provider": "A",
                 "model_type": "llm-chat", "benchmark_scores": {"humaneval": 90.0},
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
    for key in ("fetched_at", "age_days", "stale", "origin", "build_commit"):
        assert key in freshness


def test_an_old_snapshot_is_stale_but_still_loads(cache: Path) -> None:
    """Continuity beats freshness: a dated answer beats no answer."""
    _write(cache, datetime.now(timezone.utc) - timedelta(days=snapshot.STALE_AFTER_DAYS + 5))
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


def test_exit_codes_are_distinct() -> None:
    """A caller has to tell "no answer" from "no snapshot" from "broken"."""
    codes = {offline.EXIT_OK, offline.EXIT_ERROR, offline.EXIT_NO_MATCH,
             offline.EXIT_NO_SNAPSHOT, offline.EXIT_STALE}
    assert len(codes) == 5


def _run(args: list[str], cache: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(REPO_ROOT / ".venv/bin/modelspec"), *args],
        capture_output=True, text=True, timeout=120,
        env={"PATH": "/usr/bin:/bin", "MODELSPEC_CACHE": str(cache), "HOME": str(cache.parent)},
    )


@pytest.mark.skipif(not (REPO_ROOT / ".venv/bin/modelspec").exists(),
                    reason="CLI not installed in this environment")
def test_missing_snapshot_exits_three(cache: Path) -> None:
    result = _run(["offline", "rank", "coding"], cache)
    assert result.returncode == offline.EXIT_NO_SNAPSHOT
    assert "snapshot fetch" in result.stderr


@pytest.mark.skipif(not (REPO_ROOT / ".venv/bin/modelspec").exists(),
                    reason="CLI not installed in this environment")
def test_a_stale_snapshot_fails_only_when_asked(cache: Path) -> None:
    _write(cache, datetime.now(timezone.utc) - timedelta(days=snapshot.STALE_AFTER_DAYS + 5))
    lenient = _run(["offline", "rank", "coding", "--json"], cache)
    assert lenient.returncode == offline.EXIT_OK
    assert "stale" in lenient.stderr.lower()
    strict = _run(["offline", "rank", "coding", "--require-fresh"], cache)
    assert strict.returncode == offline.EXIT_STALE


@pytest.mark.skipif(not (REPO_ROOT / ".venv/bin/modelspec").exists(),
                    reason="CLI not installed in this environment")
def test_json_output_carries_version_and_freshness(cache: Path) -> None:
    _write(cache)
    result = _run(["offline", "rank", "coding", "--json"], cache)
    assert result.returncode == offline.EXIT_OK
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == offline.SCHEMA_VERSION
    assert payload["command"] == "rank"
    assert payload["freshness"]["build_commit"] == "abc123def456"
    assert payload["result"][0]["model_id"] == "a/one"


@pytest.mark.skipif(not (REPO_ROOT / ".venv/bin/modelspec").exists(),
                    reason="CLI not installed in this environment")
def test_no_match_is_its_own_exit_code(cache: Path) -> None:
    """Not an error. The honest answer is sometimes "nothing fits"."""
    _write(cache)
    result = _run(["offline", "rank", "coding", "--fits", "nonexistent-gpu"], cache)
    assert result.returncode == offline.EXIT_ERROR  # unknown device is a usage error
    result = _run(["offline", "rank", "coding", "--max-cost", "0.0001"], cache)
    assert result.returncode == offline.EXIT_NO_MATCH


@pytest.mark.skipif(not (REPO_ROOT / ".venv/bin/modelspec").exists(),
                    reason="CLI not installed in this environment")
def test_unknown_use_case_is_a_usage_error(cache: Path) -> None:
    _write(cache)
    result = _run(["offline", "rank", "not-a-use-case"], cache)
    assert result.returncode == offline.EXIT_ERROR
    assert "unknown use case" in result.stderr
