"""The CLI contract dpf consumes.

This is an interface another program calls, so the tests pin the things a caller
depends on: that answers work offline, that the envelope is versioned, that
freshness is always disclosed, and that exit codes distinguish the cases a
script has to tell apart.
"""

from __future__ import annotations

import functools
import gzip
import json
import shutil
import subprocess
import sys
import sysconfig
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path

import pytest
from typer.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from api.ranking.engine import USE_CASE_PROFILES  # noqa: E402
from cli.modelspec import offline, snapshot  # noqa: E402
from decision.snapshot import Snapshot as DecisionSnapshot  # noqa: E402
from decision.snapshot import content_hash as decision_content_hash  # noqa: E402
from decision.snapshot import snapshot_id_for  # noqa: E402


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
            "index": {"build": {"commit": "abc123def456",
                                "export_schema_version": snapshot.EXPORT_SCHEMA_VERSION}},
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


def _decision_artifacts(as_of: str = "2026-09-27") -> tuple[bytes, dict]:
    content = {
        "format_version": 1,
        "as_of": as_of,
        "facet_subjects": {"model.context_window": "model"},
        "lineup": {
            "candidates": [{"id": "a/one", "kind": "model", "model": "a/one",
                            "lifecycle": "active"}],
            "facets": {"model.context_window": {
                "row": [0], "state": ["known"], "value": [128000], "sources": [[]],
            }},
            "evidence": {},
        },
        "archive": {"candidates": [], "facets": {}, "evidence": {}},
        "out_of_lineup": 0,
        "benchmark_domains": {},
        "capability": {},
        "sources": {},
        "excluded": {},
    }
    digest = decision_content_hash(content)
    built = DecisionSnapshot(content, digest, snapshot_id_for(digest))
    return built.to_bytes(key="publisher-only-key"), {
        "vocabulary_version": 1,
        "snapshot": built.snapshot_id,
    }


def _fetch_bodies() -> dict[str, object]:
    decision, vocabulary = _decision_artifacts()
    return {
        "/api/index.json": {
            "build": {"commit": "newcommit", "built_at": "2026-09-10T00:00:00+00:00",
                      "export_schema_version": snapshot.EXPORT_SCHEMA_VERSION},
        },
        "/api/rank/candidates.json": {"candidates": []},
        "/api/rank/profiles.json": {"profiles": {}},
        "/api/graph/views/hardware.json": {"nodes": []},
        snapshot.DECISION_SNAPSHOT_ROUTE: decision,
        snapshot.DECISION_VOCABULARY_ROUTE: vocabulary,
    }


def _mock_http_client(monkeypatch: pytest.MonkeyPatch, bodies: dict[str, object]) -> None:
    import httpx

    class FakeResponse:
        status_code = 200
        headers: dict[str, str] = {}

        def __init__(self, body: object) -> None:
            self._body = body
            self.content = body if isinstance(body, bytes) else json.dumps(body).encode()

        def raise_for_status(self) -> None:
            return None

        def json(self):
            return self._body

    class FakeClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args) -> None:
            return None

        def get(self, url: str) -> FakeResponse:
            route = next((route for route in bodies if url.endswith(route)), None)
            if route is None:
                raise AssertionError(url)
            return FakeResponse(bodies[route])

    monkeypatch.setattr(httpx, "Client", FakeClient)


def _install_decision_pair(cache: Path, decision: bytes, vocabulary: dict) -> Path:
    generation = cache / "decision" / vocabulary["snapshot"]
    generation.mkdir(parents=True)
    (generation / "snapshot.json.gz").write_bytes(decision)
    (generation / "vocabulary.json").write_text(json.dumps(vocabulary))
    (cache / "decision" / "current").write_text(vocabulary["snapshot"] + "\n")
    return generation


def _write_old_decision_pair(cache: Path) -> tuple[bytes, bytes]:
    old_snapshot, old_vocabulary = _decision_artifacts("2026-09-26")
    _install_decision_pair(cache, old_snapshot, old_vocabulary)
    return old_snapshot, json.dumps(old_vocabulary).encode()


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
    status = snapshot.status(cache)
    assert status["present"] is False
    assert status["decision_snapshot"]["present"] is False


def test_fetch_caches_the_decision_snapshot_and_vocabulary(cache: Path, monkeypatch) -> None:
    import httpx

    bodies = _fetch_bodies()

    class FakeResponse:
        status_code = 200
        headers: dict[str, str] = {}

        def __init__(self, body: object) -> None:
            self._body = body
            self.content = body if isinstance(body, bytes) else json.dumps(body).encode()

        def raise_for_status(self) -> None:
            return None

        def json(self):
            return self._body

    class FakeClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args) -> None:
            return None

        def get(self, url: str) -> FakeResponse:
            route = next((route for route in bodies if url.endswith(route)), None)
            if route is None:
                return FakeResponse({})
            return FakeResponse(bodies[route])

    monkeypatch.setattr(httpx, "Client", FakeClient)
    snapshot.fetch("https://example.test", cache)

    decision_path = snapshot.decision_snapshot_path(cache)
    current = (cache / "decision" / "current").read_text().strip()
    assert decision_path == cache / "decision" / current / "snapshot.json.gz"
    assert decision_path.read_bytes() == bodies[snapshot.DECISION_SNAPSHOT_ROUTE]
    assert json.loads(snapshot.decision_vocabulary_path(cache).read_text())["snapshot"].startswith(
        "snap_"
    )
    decision_status = snapshot.status(cache)["decision_snapshot"]
    assert decision_status["present"] is True
    assert decision_status["signature_verified"] is False
    assert decision_status["as_of"] == "2026-09-27"


def test_successive_fetches_keep_current_and_previous_generations(
    cache: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ids = []
    for day in (25, 26, 27):
        decision, vocabulary = _decision_artifacts(f"2026-09-{day}")
        bodies = _fetch_bodies()
        bodies[snapshot.DECISION_SNAPSHOT_ROUTE] = decision
        bodies[snapshot.DECISION_VOCABULARY_ROUTE] = vocabulary
        _mock_http_client(monkeypatch, bodies)

        result = snapshot._fetch_decision_files("https://example.test", cache, None)

        assert result["available"] is True
        ids.append(vocabulary["snapshot"])
        assert (cache / "decision" / "current").read_text().strip() == ids[-1]
        generation_ids = {
            path.name for path in (cache / "decision").iterdir() if path.is_dir()
        }
        assert generation_ids == set(ids[-2:])


def test_fetch_refuses_decision_hash_mismatch_and_keeps_old_cache(
    cache: Path, monkeypatch
) -> None:
    import httpx

    _write(cache)
    old_decision, old_vocabulary = _decision_artifacts()
    _install_decision_pair(cache, old_decision, old_vocabulary)
    originals = {path: path.read_bytes() for path in (
        cache / "snapshot.json", snapshot.decision_snapshot_path(cache),
        snapshot.decision_vocabulary_path(cache),
    )}
    bodies = _fetch_bodies()
    envelope = json.loads(gzip.decompress(bodies[snapshot.DECISION_SNAPSHOT_ROUTE]))
    envelope["content"]["as_of"] = "2026-09-26"
    bodies[snapshot.DECISION_SNAPSHOT_ROUTE] = gzip.compress(
        json.dumps(envelope).encode(), mtime=0
    )

    class FakeResponse:
        status_code = 200
        headers: dict[str, str] = {}

        def __init__(self, body: object) -> None:
            self._body = body
            self.content = body if isinstance(body, bytes) else json.dumps(body).encode()

        def raise_for_status(self) -> None:
            return None

        def json(self):
            return self._body

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
            return FakeResponse({})

    monkeypatch.setattr(httpx, "Client", FakeClient)
    fetched = snapshot.fetch("https://example.test", cache)
    assert fetched.decision_fetch is not None
    assert fetched.decision_fetch["available"] is False
    assert "content hash mismatch" in fetched.decision_fetch["error"]
    assert snapshot.decision_snapshot_path(cache).read_bytes() == originals[
        snapshot.decision_snapshot_path(cache)
    ]
    assert snapshot.decision_vocabulary_path(cache).read_bytes() == originals[
        snapshot.decision_vocabulary_path(cache)
    ]
    assert snapshot.load(cache).build_commit == "newcommit"


def test_fetch_refuses_wrong_decision_snapshot_id_and_keeps_old_pair(
    cache: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    old_snapshot, old_vocabulary = _write_old_decision_pair(cache)
    bodies = _fetch_bodies()
    envelope = json.loads(gzip.decompress(bodies[snapshot.DECISION_SNAPSHOT_ROUTE]))
    envelope["snapshot_id"] = "snap_wrong"
    bodies[snapshot.DECISION_SNAPSHOT_ROUTE] = gzip.compress(
        json.dumps(envelope).encode(), mtime=0
    )
    _mock_http_client(monkeypatch, bodies)

    result = snapshot._fetch_decision_files("https://example.test", cache, None)

    assert result["available"] is False
    assert "snapshot ID does not match" in result["error"]
    assert snapshot.decision_snapshot_path(cache).read_bytes() == old_snapshot
    assert snapshot.decision_vocabulary_path(cache).read_bytes() == old_vocabulary


def test_fetch_refuses_vocabulary_snapshot_mismatch_and_keeps_old_pair(
    cache: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    old_snapshot, old_vocabulary = _write_old_decision_pair(cache)
    bodies = _fetch_bodies()
    bodies[snapshot.DECISION_VOCABULARY_ROUTE] = {
        "vocabulary_version": 1,
        "snapshot": "snap_wrong",
    }
    _mock_http_client(monkeypatch, bodies)

    result = snapshot._fetch_decision_files("https://example.test", cache, None)

    assert result["available"] is False
    assert "vocabulary snapshot does not match" in result["error"]
    assert snapshot.decision_snapshot_path(cache).read_bytes() == old_snapshot
    assert snapshot.decision_vocabulary_path(cache).read_bytes() == old_vocabulary


def test_current_replace_failure_keeps_old_generation_and_rank_fetch_succeeds(
    cache: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    old_snapshot, old_vocabulary = _write_old_decision_pair(cache)
    bodies = _fetch_bodies()
    _mock_http_client(monkeypatch, bodies)
    old_current = (cache / "decision" / "current").read_text()
    original_replace = snapshot.os.replace
    failed = False

    def fail_current_replace(source: Path, target: Path) -> None:
        nonlocal failed
        if Path(target) == cache / "decision" / "current" and not failed:
            failed = True
            raise OSError("injected current replace failure")
        return original_replace(source, target)

    monkeypatch.setattr(snapshot.os, "replace", fail_current_replace)

    fetched = snapshot.fetch("https://example.test", cache)

    assert failed is True
    assert fetched.decision_fetch is not None
    assert fetched.decision_fetch["available"] is False
    assert "injected current replace failure" in fetched.decision_fetch["error"]
    assert (cache / "decision" / "current").read_text() == old_current
    assert snapshot.decision_snapshot_path(cache).read_bytes() == old_snapshot
    assert snapshot.decision_vocabulary_path(cache).read_bytes() == old_vocabulary
    assert snapshot.load(cache).build_commit == "newcommit"


def test_status_reports_a_corrupt_decision_snapshot_without_changing_rank_status(
    cache: Path,
) -> None:
    _write(cache)
    decision, vocabulary = _decision_artifacts()
    generation = _install_decision_pair(cache, decision, vocabulary)
    (generation / "snapshot.json.gz").write_bytes(b"not a snapshot")

    result = _run(["snapshot", "status", "--json"], cache)

    assert result.returncode == offline.EXIT_OK
    decision = json.loads(result.stdout)["result"]["decision_snapshot"]
    assert decision["present"] is True
    assert decision["valid"] is False
    assert "invalid" in decision["error"]


@pytest.mark.parametrize("as_json", [False, True])
def test_fetch_reports_optional_decision_files_as_unavailable(
    cache: Path, monkeypatch: pytest.MonkeyPatch, as_json: bool
) -> None:
    _write(cache)
    fetched = replace(
        snapshot.load(cache),
        decision_fetch={"available": False, "error": "both decision origins returned 404"},
    )
    monkeypatch.setattr(snapshot, "fetch", lambda *args, **kwargs: fetched)

    result = CliRunner().invoke(
        offline.app, ["snapshot", "fetch", *(["--json"] if as_json else [])]
    )

    assert result.exit_code == offline.EXIT_OK
    if as_json:
        decision = json.loads(result.stdout)["result"]["decision_snapshot"]
        assert decision["available"] is False
        assert "returned 404" in decision["error"]
    else:
        assert "decision   unavailable" in result.stdout


# ── the contract ─────────────────────────────────────────────────────────────

def test_the_envelope_is_versioned() -> None:
    assert offline.SCHEMA_VERSION
    assert offline.SCHEMA_VERSION[0].isdigit()


def test_snapshot_without_export_schema_version_is_read_as_the_1x_tree(cache: Path) -> None:
    """A missing field means "the tree as it was before the field existed".

    That is 1.0, not "whatever this CLI is". While the CLI was itself 1.x the
    two coincided and the distinction was invisible; MODEL-77 moved the tree to
    2.0, and now reading a fieldless snapshot as current would parse a
    pre-MODEL-77 card — `commercial_use: true` — as if it were the new shape.
    So it is refused, like any other incompatible major.
    """
    _write(cache)
    path = cache / "snapshot.json"
    payload = json.loads(path.read_text())
    del payload["data"]["index"]["build"]["export_schema_version"]
    path.write_text(json.dumps(payload))
    assert snapshot.PRE_VERSIONED_EXPORT_SCHEMA_VERSION == "1.0"
    with pytest.raises(snapshot.SnapshotInvalid, match="export_schema_version 1.0"):
        snapshot.load(cache)


def test_compatible_export_minor_is_accepted(cache: Path) -> None:
    _write(cache)
    path = cache / "snapshot.json"
    payload = json.loads(path.read_text())
    payload["data"]["index"]["build"]["export_schema_version"] = "3.1"
    path.write_text(json.dumps(payload))
    loaded = snapshot.load(cache)
    assert loaded.export_schema_version == "3.1"


def test_incompatible_export_schema_is_refused(cache: Path) -> None:
    _write(cache)
    path = cache / "snapshot.json"
    payload = json.loads(path.read_text())
    payload["data"]["index"]["build"]["export_schema_version"] = "4.0"
    path.write_text(json.dumps(payload))
    with pytest.raises(snapshot.SnapshotInvalid, match="export_schema_version 4.0"):
        snapshot.load(cache)


def test_incompatible_export_schema_is_a_runtime_error_without_traceback(cache: Path) -> None:
    _write(cache)
    path = cache / "snapshot.json"
    payload = json.loads(path.read_text())
    payload["data"]["index"]["build"]["export_schema_version"] = "4.0"
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
        # `status_code` and `headers` are what MODEL-71 reads before
        # `raise_for_status` to tell a refusal from a served part.
        status_code = 200
        headers: dict[str, str] = {}

        def __init__(self, body: dict) -> None:
            self._body = body
            self.content = body if isinstance(body, bytes) else json.dumps(body).encode()

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return self._body

    bodies = {
        "/api/index.json": {
            "build": {"commit": "newcommit", "built_at": "2026-09-10T00:00:00+00:00",
                      "export_schema_version": "4.0"},
        },
        "/api/rank/candidates.json": {"candidates": []},
        "/api/rank/profiles.json": {"profiles": {}},
        "/api/graph/views/hardware.json": {"nodes": []},
    }
    decision, vocabulary = _decision_artifacts()
    bodies[snapshot.DECISION_SNAPSHOT_ROUTE] = decision
    bodies[snapshot.DECISION_VOCABULARY_ROUTE] = vocabulary

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
    with pytest.raises(snapshot.SnapshotInvalid, match="export_schema_version 4.0"):
        snapshot.fetch("https://example.test", cache)
    assert (cache / "snapshot.json").read_text() == original


def test_exit_codes_are_distinct() -> None:
    """A caller has to tell "no answer" from "no snapshot" from "broken"."""
    codes = {offline.EXIT_OK, offline.EXIT_ERROR, offline.EXIT_NO_MATCH,
             offline.EXIT_NO_SNAPSHOT, offline.EXIT_STALE,
             offline.EXIT_KEY_REFUSED, offline.EXIT_RATE_LIMITED}
    assert len(codes) == 7


def test_the_original_exit_codes_keep_their_values() -> None:
    """MODEL-71 added two codes. It must not have moved any of the five."""
    assert (offline.EXIT_OK, offline.EXIT_ERROR, offline.EXIT_NO_MATCH,
            offline.EXIT_NO_SNAPSHOT, offline.EXIT_STALE) == (0, 1, 2, 3, 4)


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
        env={
            "PATH": "/usr/bin:/bin",
            "MODELSPEC_CACHE": str(cache),
            "HOME": str(cache.parent),
            # Worktree pytest sets PYTHONPATH=$PWD; the subprocess must too,
            # or it ranks the primary checkout's CLI instead of this tree.
            "PYTHONPATH": str(REPO_ROOT),
        },
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
    # The tree version lives on freshness, not the envelope.
    assert "export_schema_version" not in payload
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
    decision, _vocabulary = _decision_artifacts()
    _install_decision_pair(cache, decision, _vocabulary)

    result = _run(["snapshot", "status", "--json"], cache)

    assert result.returncode == offline.EXIT_OK
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == offline.SCHEMA_VERSION
    assert payload["command"] == "status"
    assert payload["freshness"]["build_commit"] == "abc123def456"
    assert payload["result"]["present"] is True
    assert payload["result"]["decision_snapshot"]["present"] is True
    assert payload["result"]["decision_snapshot"]["snapshot_id"].startswith("snap_")
    assert payload["result"]["decision_snapshot"]["as_of"] == "2026-09-27"
    assert "age_days" in payload["result"]["decision_snapshot"]
    assert result.stderr == ""


def test_decide_uses_the_cached_decision_snapshot_by_default(cache: Path) -> None:
    decision, vocabulary = _decision_artifacts()
    _install_decision_pair(cache, decision, vocabulary)
    spec = cache.parent / "spec.yaml"
    spec.write_text(
        "spec_version: 1\n"
        "optimize:\n  max: model.context_window\n"
        "explain: none\n",
        encoding="utf-8",
    )

    result = _run(["decide", str(spec), "--json"], cache)

    assert result.returncode == offline.EXIT_OK, result.stderr
    payload = json.loads(result.stdout)
    assert payload["snapshot"] == vocabulary["snapshot"]
    assert payload["results"][0]["offering"]["model"] == "a/one"


def test_decide_without_a_cached_snapshot_says_to_fetch(cache: Path) -> None:
    spec = cache.parent / "spec.yaml"
    spec.write_text(
        "spec_version: 1\n"
        "optimize:\n  max: model.context_window\n"
        "explain: none\n",
        encoding="utf-8",
    )

    result = _run(["decide", str(spec), "--json"], cache)

    assert result.returncode == offline.EXIT_ERROR
    error = json.loads(result.stderr)["error"]
    assert error["code"] == "snapshot_required"
    assert "modelspec snapshot fetch" in error["message"]


def test_decide_treats_current_pointing_at_missing_generation_as_absent(cache: Path) -> None:
    decision_root = cache / "decision"
    decision_root.mkdir()
    (decision_root / "current").write_text("snap_missing\n")
    spec = cache.parent / "spec-missing-generation.yaml"
    spec.write_text(
        "spec_version: 1\n"
        "optimize:\n  max: model.context_window\n"
        "explain: none\n",
        encoding="utf-8",
    )

    result = _run(["decide", str(spec), "--json"], cache)

    assert result.returncode == offline.EXIT_ERROR
    error = json.loads(result.stderr)["error"]
    assert error["code"] == "snapshot_required"
    assert "modelspec snapshot fetch" in error["message"]


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


def _with_unscored(cache: Path, count: int) -> None:
    """`count` new coding-type models with no benchmark scores at all."""
    _write(cache)
    path = cache / "snapshot.json"
    payload = json.loads(path.read_text())
    for i in range(count):
        payload["data"]["candidates"]["candidates"].append({
            "model_id": f"new/m{i:02d}", "display_name": f"New {i}", "provider": "N",
            "model_type": "llm-chat", "benchmark_scores": {}, "capability_tiers": {},
            "cost_input": 1.0, "context_window": 128000, "open_weights": True,
            "release_date": f"2026-08-{i + 1:02d}"})
    path.write_text(json.dumps(payload))


def test_cli_json_names_the_unranked_candidates(cache: Path) -> None:
    """MODEL-110: additive envelope field; `result` is still the ranked list."""
    _with_unscored(cache, 3)
    report = json.loads(_run(["offline", "rank", "coding", "--json"], cache).stdout)
    assert report["schema_version"] == "1.0"
    assert [row["model_id"] for row in report["result"]] == ["a/one"]
    block = report["unranked_candidates"]
    assert block["count"] == 3
    assert [m["model_id"] for m in block["models"]] == ["new/m02", "new/m01", "new/m00"]
    assert {m["reason"] for m in block["models"]} == {"no_scores"}


def test_cli_human_output_names_models_not_ranked_yet(cache: Path) -> None:
    _with_unscored(cache, 12)
    result = _run(["offline", "rank", "coding"], cache)
    assert result.returncode == offline.EXIT_OK
    lines = result.stdout.splitlines()
    line = next(x for x in lines if "not ranked yet" in x)
    assert line.startswith("12 models are not ranked yet (not enough benchmark evidence)")
    # Newest first, ten named, and the remainder counted rather than dropped.
    assert "new/m11, new/m10," in line
    assert "new/m01" not in line
    assert line.endswith("and 2 more.")
    # Under the table, above the freshness footer.
    assert lines.index(line) > next(i for i, x in enumerate(lines) if "One" in x)


def test_cli_human_output_is_silent_when_nothing_is_withheld(cache: Path) -> None:
    _write(cache)
    assert "not ranked yet" not in _run(["offline", "rank", "coding"], cache).stdout


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


def test_offline_rank_keeps_snapshot_verified_benchmarks(cache: Path) -> None:
    """Dropping verified_benchmarks makes every ranked row unverified-legacy."""
    _write(cache)
    path = cache / "snapshot.json"
    payload = json.loads(path.read_text())
    payload["data"]["candidates"]["candidates"][0]["verified_benchmarks"] = ["humaneval"]
    path.write_text(json.dumps(payload))

    rebuilt = offline._candidates(snapshot.load(cache))
    assert rebuilt[0].verified_benchmarks == {"humaneval"}

    result = _run(["offline", "rank", "coding", "--json", "-n", "1"], cache)
    assert result.returncode == offline.EXIT_OK
    report = json.loads(result.stdout)
    assert report["schema_version"] == offline.SCHEMA_VERSION == "1.0"
    row = report["result"][0]
    assert row["evidence_basis"] == "mixed"
    assert row["verified_contributions"] == 1


# ── offline fit: null decode does not crash or lead the list (MODEL-53) ─────

def _write_fit_fixture(directory: Path) -> None:
    """Two models that fit `gpu`: one decodes tokens, one does not.

    A vision encoder's weights fit the same as any other model's, but it has
    no decode speed — `fits["gpu"]` is `None`, not a dropped key. Before
    MODEL-53, `predicted_decode_tps`/`fastest_predicted_decode_tps` were never
    null, so nothing sorted or printed this case; a naive `-tps` sort key
    would raise `TypeError` on `None`, and a naive f-string would crash on it too.
    """
    _write(directory)
    path = directory / "snapshot.json"
    payload = json.loads(path.read_text())
    candidates = payload["data"]["candidates"]["candidates"]
    chat = dict(candidates[0])
    chat["model_id"], chat["display_name"] = "a/chat", "Chat Model"
    chat["model_type"] = "llm-chat"
    chat["fits"] = {"gpu": 40.0}
    vision = dict(candidates[0])
    vision["model_id"], vision["display_name"] = "b/vision", "Vision Encoder"
    vision["model_type"] = "vision-encoder"
    vision["fits"] = {"gpu": None}
    payload["data"]["candidates"]["candidates"] = [vision, chat]
    path.write_text(json.dumps(payload))


def test_offline_fit_does_not_crash_on_a_null_decode_rate(cache: Path) -> None:
    _write_fit_fixture(cache)
    result = _run(["offline", "fit", "gpu", "--json"], cache)
    assert result.returncode == offline.EXIT_OK
    assert "Traceback" not in result.stderr


def test_offline_fit_sorts_null_decode_after_real_rates(cache: Path) -> None:
    """A model with no decode prediction must never lead the list."""
    _write_fit_fixture(cache)
    result = _run(["offline", "fit", "gpu", "--json"], cache)
    assert result.returncode == offline.EXIT_OK
    rows = json.loads(result.stdout)["result"]
    assert [r["model_id"] for r in rows] == ["a/chat", "b/vision"]
    assert rows[0]["predicted_decode_tps"] == 40.0
    assert rows[1]["predicted_decode_tps"] is None


def test_offline_fit_prints_na_for_null_decode(cache: Path) -> None:
    _write_fit_fixture(cache)
    result = _run(["offline", "fit", "gpu"], cache)
    assert result.returncode == offline.EXIT_OK
    assert "n/a tok/s  Vision Encoder" in result.stdout
    assert "~   40.0 tok/s  Chat Model" in result.stdout
    lines = [line for line in result.stdout.splitlines() if "tok/s" in line]
    assert lines[0].endswith("Chat Model")
    assert lines[1].endswith("Vision Encoder")


# ── offline fit: rehosts are out of the default pool (MODEL-54) ─────────────

def _write_rehost_fixture(directory: Path) -> None:
    _write(directory)
    path = directory / "snapshot.json"
    payload = json.loads(path.read_text())
    base = payload["data"]["candidates"]["candidates"][0]
    canonical = dict(base, model_id="meta/x", display_name="X", fits={"gpu": 40.0})
    copy = dict(base, model_id="mirror/x", display_name="X", fits={"gpu": 40.0},
                rehost_of="meta/x")
    payload["data"]["candidates"]["candidates"] = [canonical, copy]
    path.write_text(json.dumps(payload))


def test_offline_fit_excludes_rehosts_by_default(cache: Path) -> None:
    _write_rehost_fixture(cache)
    result = _run(["offline", "fit", "gpu", "--json"], cache)
    assert result.returncode == offline.EXIT_OK
    assert [r["model_id"] for r in json.loads(result.stdout)["result"]] == ["meta/x"]
    result = _run(["offline", "fit", "gpu", "--json", "--include-rehosts"], cache)
    assert {r["model_id"] for r in json.loads(result.stdout)["result"]} == {"meta/x", "mirror/x"}
