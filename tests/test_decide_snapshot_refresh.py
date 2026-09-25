"""The Worker picks up a new decision snapshot after a site deploy (MODEL-159).

Each isolate holds one verified snapshot. At most once a minute it revalidates
with a conditional fetch; a changed snapshot is verified before it replaces the
old one, and a refresh that fails keeps the old one and says so.
"""

from __future__ import annotations

import asyncio
import gzip
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKER_SRC = REPO_ROOT / "api" / "worker" / "src"
sys.path.insert(0, str(REPO_ROOT))

from decision.snapshot import SnapshotInputs, build_snapshot  # noqa: E402
from tests.snapshot_records import SOURCES, evidence, fact, model  # noqa: E402

KEY = b"model-159-test-key"


def _load_service():
    spec = importlib.util.spec_from_file_location(
        "modelspec_decide_service_refresh", WORKER_SRC / "decide_service.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def service():
    return _load_service()


def _snapshot_bytes(as_of: date, benchmark: str = "swe_bench_pro") -> bytes:
    models = [
        model("lab/" + name, facts=[fact("model", "lab/" + name, "model.max_output_tokens", 8_000)])
        for name in ("a", "b")
    ]
    rows = [
        evidence("lab/a", benchmark, 70, measured_by="independent"),
        evidence("lab/b", benchmark, 60, measured_by="independent"),
    ]
    return build_snapshot(
        SnapshotInputs(
            models=models,
            evidence=rows,
            sources=SOURCES,
            benchmark_domains={benchmark: [("software_engineering", "direct")]},
        ),
        as_of=as_of,
    ).to_bytes(key=KEY)


@pytest.fixture(scope="module")
def old_bytes() -> bytes:
    return _snapshot_bytes(date(2026, 9, 24))


@pytest.fixture(scope="module")
def new_bytes() -> bytes:
    return _snapshot_bytes(date(2026, 9, 25), benchmark="terminal_bench")


def _tampered(raw: bytes) -> bytes:
    envelope = json.loads(gzip.decompress(raw))
    envelope["content"]["as_of"] = "2099-01-01"
    return gzip.compress(json.dumps(envelope).encode("utf-8"))


class Origin:
    """A static origin that honours `If-None-Match`, as Pages does."""

    def __init__(self, body: bytes, etag: str = '"v1"'):
        self.body = body
        self.etag = etag
        self.requests: list[str | None] = []
        self.fail: Exception | None = None
        self.status: int | None = None

    def publish(self, body: bytes, etag: str) -> None:
        self.body, self.etag = body, etag

    async def __call__(self, if_none_match: str | None):
        from types import SimpleNamespace

        self.requests.append(if_none_match)
        if self.fail is not None:
            raise self.fail
        if self.status is not None:
            return SimpleNamespace(status=self.status, etag=None, body=None)
        if if_none_match == self.etag:
            return SimpleNamespace(status=304, etag=self.etag, body=None)
        return SimpleNamespace(status=200, etag=self.etag, body=self.body)


class Clock:
    def __init__(self) -> None:
        self.now = 1_000.0

    def __call__(self) -> float:
        return self.now


def _holder(service, origin: Origin, clock: Clock):
    return service.SnapshotHolder(origin, clock=clock)


def _run(coro):
    return asyncio.run(coro)


def test_a_new_snapshot_is_picked_up_within_the_interval(service, old_bytes, new_bytes) -> None:
    origin, clock = Origin(old_bytes), Clock()
    holder = _holder(service, origin, clock)
    first = _run(holder.current(KEY))

    origin.publish(new_bytes, '"v2"')
    clock.now += service.REVALIDATE_SECONDS - 1
    assert _run(holder.current(KEY)) is first, "no revalidation inside the interval"
    assert origin.requests == [None]

    clock.now += 1
    second = _run(holder.current(KEY))
    assert second.snapshot_id != first.snapshot_id
    assert "terminal_bench" in second.benchmark_ids()
    assert origin.requests == [None, '"v1"'], "the revalidation is conditional"
    assert holder.headers() == {"x-modelspec-snapshot": second.snapshot_id}


def test_an_unchanged_snapshot_costs_one_conditional_request(service, old_bytes) -> None:
    origin, clock = Origin(old_bytes), Clock()
    holder = _holder(service, origin, clock)
    first = _run(holder.current(KEY))
    for _ in range(3):
        clock.now += service.REVALIDATE_SECONDS
        assert _run(holder.current(KEY)) is first
    assert origin.requests == [None, '"v1"', '"v1"', '"v1"']
    assert "x-modelspec-snapshot-stale" not in holder.headers()


def test_a_tampered_new_snapshot_is_refused_and_the_old_one_serves(
    service, old_bytes, new_bytes
) -> None:
    origin, clock = Origin(old_bytes), Clock()
    holder = _holder(service, origin, clock)
    first = _run(holder.current(KEY))

    origin.publish(_tampered(new_bytes), '"v2"')
    clock.now += service.REVALIDATE_SECONDS
    assert _run(holder.current(KEY)) is first
    stale = holder.headers()["x-modelspec-snapshot-stale"]
    assert "content hash mismatch" in stale
    assert holder.headers()["x-modelspec-snapshot"] == first.snapshot_id

    # The fixed build replaces it on the next revalidation.
    origin.publish(new_bytes, '"v3"')
    clock.now += service.REVALIDATE_SECONDS
    assert _run(holder.current(KEY)).snapshot_id != first.snapshot_id
    assert "x-modelspec-snapshot-stale" not in holder.headers()


@pytest.mark.parametrize("failure", ["network", "http"])
def test_a_failed_refresh_keeps_the_verified_snapshot_and_says_so(
    service, old_bytes, failure: str
) -> None:
    origin, clock = Origin(old_bytes), Clock()
    holder = _holder(service, origin, clock)
    first = _run(holder.current(KEY))

    if failure == "network":
        origin.fail = RuntimeError("connection reset")
    else:
        origin.status = 500
    clock.now += service.REVALIDATE_SECONDS
    assert _run(holder.current(KEY)) is first
    assert holder.headers()["x-modelspec-snapshot-stale"]
    header = holder.headers()["x-modelspec-snapshot-stale"]
    assert header.isascii() and "\n" not in header and len(header) <= 200

    # A failure is not retried on every request.
    requests = len(origin.requests)
    _run(holder.current(KEY))
    assert len(origin.requests) == requests


def test_a_first_load_that_fails_verification_is_refused(service, old_bytes) -> None:
    origin, clock = Origin(_tampered(old_bytes)), Clock()
    holder = _holder(service, origin, clock)
    with pytest.raises(service.SnapshotRefusalError, match="content hash mismatch"):
        _run(holder.current(KEY))
    # Cached as a refusal for the interval, then retried.
    with pytest.raises(service.SnapshotRefusalError):
        _run(holder.current(KEY))
    assert len(origin.requests) == 1
    origin.publish(old_bytes, '"v2"')
    clock.now += service.REVALIDATE_SECONDS
    assert _run(holder.current(KEY)).snapshot_id


def test_a_missing_first_snapshot_is_reported_as_missing(service) -> None:
    origin, clock = Origin(b""), Clock()
    origin.status = 404
    holder = _holder(service, origin, clock)
    with pytest.raises(service.SnapshotMissingError):
        _run(holder.current(KEY))


def test_a_forced_revalidation_skips_the_interval_but_not_the_floor(
    service, old_bytes, new_bytes
) -> None:
    origin, clock = Origin(old_bytes), Clock()
    holder = _holder(service, origin, clock)
    first = _run(holder.current(KEY))
    origin.publish(new_bytes, '"v2"')

    assert _run(holder.current(KEY, force=True)) is first, "inside the floor"
    clock.now += service.FORCED_REVALIDATE_SECONDS
    assert _run(holder.current(KEY, force=True)).snapshot_id != first.snapshot_id


def test_a_stale_vocabulary_request_gets_snapshot_changed(service, old_bytes, new_bytes) -> None:
    origin, clock = Origin(new_bytes), Clock()
    snapshot = _run(_holder(service, origin, clock).current(KEY))
    old_id = service.load_snapshot(old_bytes, key=KEY).snapshot_id
    # The stale page asks about a benchmark the new snapshot does not know:
    # it must learn the snapshot changed, not get a 400 for the benchmark.
    payload = {"spec_version": 1, "optimize": {"max": "swe_bench_pro"}, "explain": "none"}

    status, body = service.decide(payload, snapshot, expected_snapshot=old_id)
    assert status == 409
    assert body["snapshot"] == snapshot.snapshot_id
    assert body["error"]["code"] == "snapshot_changed"
    assert body["error"]["current"] == snapshot.snapshot_id
    assert body["error"]["requested"] == old_id


def test_a_matching_vocabulary_request_is_answered(service, new_bytes) -> None:
    origin, clock = Origin(new_bytes), Clock()
    snapshot = _run(_holder(service, origin, clock).current(KEY))
    payload = {"spec_version": 1, "optimize": {"max": "terminal_bench"}, "explain": "none"}
    status, body = service.decide(payload, snapshot, expected_snapshot=snapshot.snapshot_id)
    assert status == 200
    assert body["snapshot"] == snapshot.snapshot_id


def test_entry_revalidates_and_reads_the_snapshot_header() -> None:
    source = (WORKER_SRC / "entry.py").read_text(encoding="utf-8")
    assert "SnapshotHolder(" in source
    assert "x-modelspec-snapshot" in source.lower()
    assert "force=True" in source
    assert "If-None-Match" in source
    assert "_decision_cache" not in source, "the unbounded per-isolate cache is gone"


# ── single flight: a cold burst waits on one load (MODEL-153) ──────────────
#
# The decide page's first answer is followed by the full explanation and six
# next-question probes at once. On a cold isolate each of them used to fetch,
# verify and parse its own copy of the snapshot.


class GatedOrigin(Origin):
    """An origin whose answers wait until the test opens the gate."""

    def __init__(self, body: bytes, etag: str = '"v1"'):
        super().__init__(body, etag)
        self.gate: asyncio.Event | None = None

    async def __call__(self, if_none_match: str | None):
        gate = self.gate
        if gate is not None:
            self.requests.append(if_none_match)
            await gate.wait()
            self.requests.pop()
        return await super().__call__(if_none_match)


@pytest.fixture
def parses(service, monkeypatch) -> list[str]:
    seen: list[str] = []
    real = service.load_snapshot

    def counting(data, *, key):
        snapshot = real(data, key=key)
        seen.append(snapshot.snapshot_id)
        return snapshot

    monkeypatch.setattr(service, "load_snapshot", counting)
    return seen


def _bounded(coro):
    """A red single-flight test fails in seconds rather than hanging the suite."""
    return asyncio.run(asyncio.wait_for(coro, timeout=5))


async def _started(*tasks: asyncio.Task) -> None:
    """Let every task run up to its first await."""
    for _ in range(len(tasks) + 3):
        await asyncio.sleep(0)


def test_a_cold_burst_waits_on_one_load(service, old_bytes, parses) -> None:
    origin, clock = GatedOrigin(old_bytes), Clock()
    holder = _holder(service, origin, clock)

    async def burst():
        origin.gate = asyncio.Event()
        tasks = [asyncio.create_task(holder.current(KEY)) for _ in range(11)]
        await _started(*tasks)
        origin.gate.set()
        return await asyncio.gather(*tasks)

    answers = _bounded(burst())
    assert origin.requests == [None], "one fetch for the whole burst"
    assert len(parses) == 1, "one verify-and-parse, so memory holds one snapshot"
    assert all(answer is answers[0] for answer in answers)


@pytest.mark.parametrize("failure", ["network", "refused"])
def test_a_cold_burst_shares_one_failure(service, old_bytes, parses, failure: str) -> None:
    origin, clock = GatedOrigin(old_bytes if failure == "network" else _tampered(old_bytes)), Clock()
    if failure == "network":
        origin.fail = RuntimeError("connection reset")
    holder = _holder(service, origin, clock)

    async def burst():
        origin.gate = asyncio.Event()
        tasks = [asyncio.create_task(holder.current(KEY)) for _ in range(6)]
        await _started(*tasks)
        origin.gate.set()
        return await asyncio.gather(*tasks, return_exceptions=True)

    outcomes = _bounded(burst())
    expected = RuntimeError if failure == "network" else service.SnapshotRefusalError
    assert all(isinstance(outcome, expected) for outcome in outcomes), outcomes
    assert origin.requests == [None], "the burst does not retry the failure six times"


def test_a_warm_isolate_serves_the_held_snapshot_during_a_refresh(
    service, old_bytes, new_bytes, parses
) -> None:
    origin, clock = GatedOrigin(old_bytes), Clock()
    holder = _holder(service, origin, clock)
    first = _run(holder.current(KEY))
    origin.publish(new_bytes, '"v2"')
    clock.now += service.REVALIDATE_SECONDS

    async def burst():
        origin.gate = asyncio.Event()
        refresh = asyncio.create_task(holder.current(KEY))
        await _started(refresh)
        # Unforced callers answer from the verified snapshot at once.
        assert await holder.current(KEY) is first
        # A caller whose vocabulary names another snapshot waits for the refresh.
        forced = asyncio.create_task(holder.current(KEY, force=True))
        await _started(forced)
        assert not forced.done()
        origin.gate.set()
        return await refresh, await forced

    refreshed, forced = _bounded(burst())
    assert refreshed is forced and refreshed.snapshot_id != first.snapshot_id
    assert origin.requests == [None, '"v1"'], "the forced caller joined the refresh"


def test_a_cancelled_load_hands_over_to_the_waiting_request(service, old_bytes, parses) -> None:
    origin, clock = GatedOrigin(old_bytes), Clock()
    holder = _holder(service, origin, clock)

    async def burst():
        origin.gate = asyncio.Event()
        loader = asyncio.create_task(holder.current(KEY))
        await _started(loader)
        waiter = asyncio.create_task(holder.current(KEY))
        await _started(waiter)
        origin.gate = None  # the next fetch answers at once
        loader.cancel()
        return await waiter

    assert _bounded(burst()).snapshot_id
    assert len(parses) == 1


def test_a_stuck_load_does_not_hold_the_isolate_forever(service, old_bytes, parses) -> None:
    origin, clock = GatedOrigin(old_bytes), Clock()
    holder = _holder(service, origin, clock)

    async def burst():
        origin.gate = asyncio.Event()  # never opened: this fetch hangs
        stuck = asyncio.create_task(holder.current(KEY))
        await _started(stuck)
        origin.gate = None
        clock.now += service.LOAD_WAIT_SECONDS
        try:
            return await holder.current(KEY)
        finally:
            stuck.cancel()

    assert _bounded(burst()).snapshot_id
    assert len(parses) == 1
