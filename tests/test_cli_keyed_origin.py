"""MODEL-71: `snapshot fetch` against an origin that keys its export.

The ticket's own statement of intent is that *nothing else changes*. So these
tests are mostly about what stayed the same: the envelope, the exit codes, the
unkeyed path. The new surface is one option, one environment variable, four
named failures, and a snapshot whose `fetched_at` is now.

The origin here is a real HTTP server on a loopback port rather than a patched
`httpx.Client`, because three of the properties under test — the key travels in
a header and not in a URL, it does not survive a cross-host redirect, and it is
absent from the access log — are properties of what goes over the socket. A
fake client cannot be wrong about them, which makes it useless for proving them.
"""

from __future__ import annotations

import json
import subprocess
import sys
import threading
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from cli.modelspec import offline, snapshot  # noqa: E402
from tests.test_cli_snapshot import _modelspec_cli, _write  # noqa: E402

#: A key with a shape the origin would recognise (MODEL-69 mints `live_…`) and
#: a body distinctive enough that a substring search for it cannot false-match.
KEY = "live_MODEL71xxxxTESTONLYsecretVALUE"

#: What the origin refuses with. The codes are `docs/api-access.md`'s.
REFUSALS = {
    "missing": (401, {"error": {"code": "missing_api_key",
                                "message": "this endpoint requires an API key."}}),
    "invalid": (401, {"error": {"code": "invalid_api_key",
                                "message": "that API key is not recognised."}}),
    "revoked": (403, {"error": {"code": "key_revoked",
                                "message": "that API key has been revoked."}}),
    "limited": (429, {"error": {"code": "rate_limited", "retry_after_seconds": 42,
                                "message": "rate limit reached: 10 request(s) per 1 day."}}),
}


def _export_bodies(commit: str = "keyedcommit01") -> dict[str, Any]:
    """The four required parts, in the shape `snapshot._snapshot_from_raw` wants."""
    from api.ranking.engine import USE_CASE_PROFILES

    return {
        "/api/index.json": {"build": {
            "commit": commit, "built_at": datetime.now(UTC).isoformat(),
            "export_schema_version": snapshot.EXPORT_SCHEMA_VERSION}},
        "/api/rank/candidates.json": {"candidates": [{
            "model_id": "a/one", "display_name": "One", "provider": "A",
            "model_type": "llm-chat",
            "benchmark_scores": {
                b: 90.0 for b in USE_CASE_PROFILES["coding"]["benchmark_weights"]},
            "capability_tiers": {}, "cost_input": 1.0, "context_window": 128000,
            "open_weights": True, "fits": {"gpu": 40.0}}]},
        "/api/rank/profiles.json": {
            "profiles": {"coding": {"benchmark_weights": {"humaneval": 1.0},
                                    "preferred_types": ["llm-chat"]}},
            "featured": ["coding"]},
        "/api/graph/views/hardware.json": {"nodes": [{
            "id": "gpu", "label": "Hardware", "display_name": "A GPU",
            "memory_gb": 24, "memory_bandwidth_gb_s": 1000}]},
    }


class Origin:
    """A stub of the keyed origin, and a record of what actually reached it."""

    def __init__(self) -> None:
        self.mode = "ok"
        self.requires_key = True
        self.redirect_to: str | None = None
        self.seen: list[tuple[str, dict[str, str]]] = []
        self.access_log: list[str] = []
        self.bodies = _export_bodies()
        origin = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, fmt: str, *args: Any) -> None:
                # The server's own access log, kept rather than silenced: a key
                # in a query string would land here, which is the point.
                origin.access_log.append(fmt % args)

            def _send(self, status: int, body: dict[str, Any],
                      headers: dict[str, str] | None = None) -> None:
                blob = json.dumps(body).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(blob)))
                for name, value in (headers or {}).items():
                    self.send_header(name, value)
                self.end_headers()
                self.wfile.write(blob)

            def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler's name
                origin.seen.append((self.path, dict(self.headers)))
                if origin.redirect_to:
                    self.send_response(302)
                    self.send_header("Location", origin.redirect_to + self.path)
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                if origin.mode != "ok":
                    status, body = REFUSALS[origin.mode]
                    extra = {"Retry-After": "42"} if status == 429 else {}
                    self._send(status, body, extra)
                    return
                presented = self.headers.get("Authorization")
                if origin.requires_key and presented != f"Bearer {KEY}":
                    status, body = REFUSALS["missing" if not presented else "invalid"]
                    self._send(status, body)
                    return
                body = origin.bodies.get(self.path)
                if body is None:
                    self._send(404, {"error": {"code": "not_found", "message": "no"}})
                    return
                self._send(200, body)

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def start(self) -> None:
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture
def origin() -> Any:
    stub = Origin()
    stub.start()
    try:
        yield stub
    finally:
        stub.stop()


@pytest.fixture
def cache(tmp_path: Path) -> Path:
    directory = tmp_path / "cache"
    directory.mkdir()
    return directory


def _run(args: list[str], cache: Path, key: str | None = None) -> subprocess.CompletedProcess:
    env = {"PATH": "/usr/bin:/bin", "MODELSPEC_CACHE": str(cache),
           "HOME": str(cache.parent), "PYTHONPATH": str(REPO_ROOT)}
    if key is not None:
        env[snapshot.API_KEY_ENV] = key
    return subprocess.run([_modelspec_cli(), *args], capture_output=True, text=True,
                          timeout=120, env=env)


# ── the credential has no printable form ─────────────────────────────────────

def test_the_key_has_no_printable_form() -> None:
    """The secrecy is a property of the shape, not a rule to remember.

    `docs/api-access.md` makes the same argument about the origin's key store:
    there is no field that holds a secret, so an accidental `repr()` in a log
    line cannot print one. The CLI side needs the secret in memory to send it,
    so the guarantee is narrower — no *representation* of it carries the key.
    """
    credential = snapshot.Credential(secret=KEY, source="environment")
    for rendering in (repr(credential), str(credential), f"{credential}",
                      format(credential), repr({"credential": credential}),
                      repr([credential]), repr(RuntimeError(credential))):
        assert KEY not in rendering
        assert credential.key_id in rendering
    assert len(credential.key_id) == snapshot.KEY_ID_LENGTH
    assert credential.redact(f"a {KEY} b") == f"a {snapshot.REDACTED} b"


def test_the_environment_is_the_source_and_the_flag_is_an_override() -> None:
    assert snapshot.resolve_credential(None, {}) is None
    assert snapshot.resolve_credential(None, {snapshot.API_KEY_ENV: "  "}) is None
    from_env = snapshot.resolve_credential(None, {snapshot.API_KEY_ENV: KEY})
    assert from_env is not None and from_env.source == "environment"
    both = snapshot.resolve_credential("flagged", {snapshot.API_KEY_ENV: KEY})
    assert both is not None and both.source == "flag"


# ── what goes over the socket ────────────────────────────────────────────────

def test_the_key_travels_in_a_header_and_never_in_a_url(origin: Origin, cache: Path) -> None:
    """A key in a URL is a key in somebody else's access log."""
    snapshot.fetch(origin.url, cache, credential=snapshot.Credential(secret=KEY))

    assert origin.seen, "the origin was never called"
    for path, headers in origin.seen:
        assert headers.get("Authorization") == f"Bearer {KEY}"
        assert KEY not in path
        assert "?" not in path
    assert not any(KEY in line for line in origin.access_log)


def test_the_unkeyed_path_sends_no_credential(origin: Origin, cache: Path) -> None:
    """The free path is what it was: no account, no header, no change."""
    origin.requires_key = False
    snapshot.fetch(origin.url, cache)

    assert origin.seen
    assert all("Authorization" not in headers for _, headers in origin.seen)


def test_a_cross_host_redirect_does_not_carry_the_key(origin: Origin, cache: Path) -> None:
    """`Authorization` is dropped when a redirect leaves the origin it was for.

    This is why the key is presented as `Authorization` and not as the
    `X-API-Key` header the origin also accepts: a custom header survives a
    redirect to anywhere, and an origin that can be made to redirect could then
    hand the key to the destination.
    """
    elsewhere = Origin()
    elsewhere.start()
    try:
        origin.redirect_to = elsewhere.url
        with pytest.raises(snapshot.FetchError):
            snapshot.fetch(origin.url, cache, credential=snapshot.Credential(secret=KEY))
        assert elsewhere.seen, "the redirect was not followed, so nothing was proven"
        assert all(h.get("Authorization") is None for _, h in elsewhere.seen)
    finally:
        elsewhere.stop()


# ── the point of the ticket: fetched_at is current ───────────────────────────

def test_a_keyed_fetch_is_current(origin: Origin, cache: Path) -> None:
    """`age_days` ~0 and `stale` false, which is the whole outcome."""
    fetched = snapshot.fetch(origin.url, cache, credential=snapshot.Credential(secret=KEY))

    assert fetched.age_days == pytest.approx(0.0, abs=0.01)
    assert fetched.is_stale is False
    assert fetched.freshness()["stale"] is False
    assert fetched.freshness()["age_days"] == pytest.approx(0.0, abs=0.01)
    assert fetched.build_commit == "keyedcommit01"


def test_require_fresh_passes_on_a_keyed_fetch_and_fails_on_a_ninety_day_export(
    origin: Origin, cache: Path
) -> None:
    """The failure this ticket exists to remove, and the state it replaces.

    A 90-day-delayed public export is 60 days past `STALE_AFTER_DAYS`, so
    `--require-fresh` could never succeed on one — every dpf answer would exit
    4 on the day it was fetched. After a keyed fetch the same command exits 0.
    """
    delayed = _run(["snapshot", "status"], cache)  # no snapshot at all yet
    assert delayed.returncode == offline.EXIT_NO_SNAPSHOT

    _write(cache, datetime.now(UTC) - timedelta(days=90))
    assert snapshot.load(cache).age_days > snapshot.STALE_AFTER_DAYS
    stale = _run(["offline", "rank", "coding", "--require-fresh", "--json"], cache)
    assert stale.returncode == offline.EXIT_STALE

    fetched = _run(["snapshot", "fetch", "--origin", origin.url], cache, key=KEY)
    assert fetched.returncode == offline.EXIT_OK, fetched.stderr
    fresh = _run(["offline", "rank", "coding", "--require-fresh", "--json"], cache, key=KEY)
    assert fresh.returncode == offline.EXIT_OK, fresh.stderr
    payload = json.loads(fresh.stdout)
    assert payload["freshness"]["stale"] is False
    assert payload["freshness"]["age_days"] < 1
    assert payload["freshness"]["build_commit"] == "keyedcommit01"


# ── the four failures, and the exit code each one produces ───────────────────

@pytest.mark.parametrize(("mode", "code", "says"), [
    ("missing", offline.EXIT_KEY_REFUSED, "requires an API key"),
    ("invalid", offline.EXIT_KEY_REFUSED, "rejected the API key"),
    ("revoked", offline.EXIT_KEY_REFUSED, "rejected the API key"),
    ("limited", offline.EXIT_RATE_LIMITED, "rate-limited"),
])
def test_each_refusal_has_its_own_documented_outcome(
    origin: Origin, cache: Path, mode: str, code: int, says: str
) -> None:
    origin.mode = mode
    key = None if mode == "missing" else KEY

    result = _run(["snapshot", "fetch", "--origin", origin.url], cache, key=key)

    assert result.returncode == code
    assert result.stdout == ""
    assert says in result.stderr
    assert result.stderr.startswith("error: ")
    assert "Traceback" not in result.stderr
    # The origin's own sentence is relayed, not paraphrased into something less
    # useful than what the service already said.
    assert REFUSALS[mode][1]["error"]["message"] in result.stderr
    assert not (cache / "snapshot.json").exists()


def test_a_rate_limit_says_when_to_come_back(origin: Origin, cache: Path) -> None:
    origin.mode = "limited"
    result = _run(["snapshot", "fetch", "--origin", origin.url], cache, key=KEY)
    assert result.returncode == offline.EXIT_RATE_LIMITED
    assert "Retry after 42s" in result.stderr


def test_an_unreachable_origin_keeps_the_exit_code_it_always_had(cache: Path) -> None:
    """Not a new code. This path existed before MODEL-71 and is unchanged."""
    result = _run(["snapshot", "fetch", "--origin", "http://127.0.0.1:1"], cache, key=KEY)

    assert result.returncode == offline.EXIT_ERROR
    assert result.stderr.startswith("error: could not fetch the snapshot:")
    assert "could not reach http://127.0.0.1:1" in result.stderr
    assert "Traceback" not in result.stderr


def test_the_flag_works_and_warns_that_it_is_visible(origin: Origin, cache: Path) -> None:
    """`docs/agent-commerce-assessment.md` §4: argv lands in `ps` and history."""
    result = _run(["snapshot", "fetch", "--origin", origin.url, "--api-key", KEY], cache)

    assert result.returncode == offline.EXIT_OK, result.stderr
    assert "shell history" in result.stderr
    assert snapshot.API_KEY_ENV in result.stderr
    assert KEY not in result.stderr


# ── the key reaches no stream, no file and no log ────────────────────────────

def test_the_key_appears_in_no_output_no_error_and_no_cached_file(
    origin: Origin, cache: Path
) -> None:
    """Every branch of `snapshot fetch`, searched for the secret it was given.

    Success, all four refusals, and an unreachable origin — stdout, stderr, the
    origin's access log, and the snapshot written to disk. A key that leaks
    into any of those is a key in a CI log, a terminal scrollback or a file
    somebody copies around.
    """
    runs: list[subprocess.CompletedProcess] = []
    for mode in ("ok", "missing", "invalid", "revoked", "limited"):
        origin.mode = mode
        runs.append(_run(["snapshot", "fetch", "--origin", origin.url], cache, key=KEY))
    runs.append(_run(["snapshot", "fetch", "--origin", "http://127.0.0.1:1"], cache, key=KEY))
    runs.append(_run(["snapshot", "fetch", "--origin", origin.url, "--api-key", KEY], cache))
    origin.mode = "ok"
    runs.append(_run(["snapshot", "status", "--json"], cache, key=KEY))

    for result in runs:
        assert KEY not in result.stdout
        assert KEY not in result.stderr
    assert not any(KEY in line for line in origin.access_log)

    cached = (cache / "snapshot.json").read_text(encoding="utf-8")
    assert KEY not in cached
    assert snapshot.API_KEY_ENV not in cached
    # Nor any run of it: a truncated key is still most of a key. (The catalogue
    # has a benchmark called `livecodebench`, so a prefix search is not enough.)
    fragments = {KEY[i:i + 12] for i in range(len(KEY) - 11)}
    assert not any(fragment in cached for fragment in fragments)


def test_a_rejection_names_the_key_only_by_its_fingerprint(origin: Origin, cache: Path) -> None:
    """A support conversation has to be able to name the key. `key_id` does it.

    It is the same 12 hex characters the origin logs (MODEL-69), so both ends
    can talk about one key without either quoting it.
    """
    origin.mode = "invalid"
    result = _run(["snapshot", "fetch", "--origin", origin.url], cache, key=KEY)

    assert snapshot.Credential(secret=KEY).key_id in result.stderr
    assert KEY not in result.stderr


# ── nothing else changed ─────────────────────────────────────────────────────

#: The envelope as it stood before MODEL-71. Frozen here rather than derived,
#: so a change to the code cannot quietly change what the test expects.
#: MODEL-110 added `unranked_candidates` to every rank envelope, keyed or not —
#: an additive field under schema 1.0, added here by hand for that reason.
RANK_ENVELOPE_KEYS = {"schema_version", "command", "freshness", "result",
                      "ranking_status", "ranked_count", "unranked_count",
                      "unranked_candidates"}
FIT_ENVELOPE_KEYS = {"schema_version", "command", "freshness", "result"}
FRESHNESS_KEYS = {"fetched_at", "age_days", "stale", "stale_after_days", "origin",
                  "build_commit", "built_at", "export_schema_version"}
FIT_ROW_KEYS = {"model_id", "display_name", "predicted_decode_tps", "prediction_basis"}


@pytest.mark.parametrize("keyed", [False, True])
def test_the_rank_and_fit_envelopes_are_unchanged(
    origin: Origin, cache: Path, keyed: bool
) -> None:
    """The acceptance criterion this ticket is most at risk of failing.

    Run against a snapshot fetched with a key and against one fetched without,
    because "the keyed path quietly grew a field" is exactly the failure the
    ticket's "nothing else changes" is guarding against.
    """
    origin.requires_key = keyed
    fetch = ["snapshot", "fetch", "--origin", origin.url]
    assert _run(fetch, cache, key=KEY if keyed else None).returncode == offline.EXIT_OK

    ranked = _run(["offline", "rank", "coding", "--json"], cache)
    assert ranked.returncode == offline.EXIT_OK, ranked.stderr
    envelope = json.loads(ranked.stdout)
    assert envelope["schema_version"] == offline.SCHEMA_VERSION == "1.0"
    assert set(envelope) == RANK_ENVELOPE_KEYS
    assert set(envelope["freshness"]) == FRESHNESS_KEYS
    assert envelope["command"] == "rank"

    fitted = _run(["offline", "fit", "gpu", "--json"], cache)
    assert fitted.returncode == offline.EXIT_OK, fitted.stderr
    envelope = json.loads(fitted.stdout)
    assert envelope["schema_version"] == offline.SCHEMA_VERSION
    assert set(envelope) == FIT_ENVELOPE_KEYS
    assert set(envelope["freshness"]) == FRESHNESS_KEYS
    assert set(envelope["result"][0]) == FIT_ROW_KEYS


def test_the_keyed_and_unkeyed_snapshots_have_the_same_shape(
    origin: Origin, tmp_path: Path
) -> None:
    """The credential changes where the tree came from, not what it is.

    Nothing about having presented a key is recorded in the snapshot: no key
    id, no tier, no "authenticated" flag. There is nothing there to leak, and
    nothing for a consumer to start branching on.
    """
    keyed, free = tmp_path / "keyed", tmp_path / "free"
    keyed.mkdir()
    free.mkdir()
    with_key = snapshot.fetch(origin.url, keyed, credential=snapshot.Credential(secret=KEY))
    origin.requires_key = False
    without = snapshot.fetch(origin.url, free)

    assert set(with_key.freshness()) == set(without.freshness()) == FRESHNESS_KEYS
    keyed_meta = json.loads((keyed / "snapshot.json").read_text())["meta"]
    free_meta = json.loads((free / "snapshot.json").read_text())["meta"]
    assert set(keyed_meta) == set(free_meta)
    assert with_key.data.keys() == without.data.keys()
