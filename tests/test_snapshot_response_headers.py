"""Each response keeps its selected snapshot across real credit settlement I/O."""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, date, datetime

import pytest

from decision.snapshot import SnapshotInputs, build_snapshot, load_snapshot_bytes
from tests.snapshot_records import SOURCES, model, offering
from tests.test_snapshot_successor import (
    API_KEY,
    BOUNDARY,
    KEY,
    MODEL,
    OFFERING,
    SPEC,
    deploy,
)
from tests.test_snapshot_successor import signed_pair as signed_pair
from tests.test_snapshot_successor import utc_clock as utc_clock
from tests.test_x402 import _entry_env, _Req, credits, x402
from tests.test_x402 import entry as entry

PEER = "lab/argon-peer"
BEFORE = datetime(2026, 11, 30, 23, 59, 59, tzinfo=UTC)


@pytest.fixture(scope="module")
def comparison_pair(signed_pair):
    """Retain the Argon schedules and add the second named comparison model."""
    rows = []
    for raw in signed_pair:
        loaded = load_snapshot_bytes(raw, key=KEY, public_keys={})
        for facet in ("offering.price.input", "offering.price.output"):
            record_id = loaded.fact(OFFERING, facet).record_id
            assert record_id is not None
            rows.append(loaded.record(record_id))
    inputs = SnapshotInputs(
        models=[model(MODEL), model(PEER)],
        offerings=[offering(MODEL, facts=rows), offering(PEER)],
        sources=SOURCES,
    )
    return tuple(
        build_snapshot(inputs, as_of=day).to_bytes(key=KEY, ed25519_signer=None)
        for day in (date(2026, 11, 30), date(2026, 12, 1))
    )


class BlockingLedger(credits.MemoryLedger):
    """Use the real ledger state, pausing at the actual post-answer RPC."""

    def __init__(self, action: str):
        super().__init__()
        self.action = action
        self.reached = asyncio.Event()
        self.resume = asyncio.Event()
        self.calls: list[str] = []

    async def _pause(self, action: str) -> None:
        self.calls.append(action)
        if action == self.action:
            self.reached.set()
            await self.resume.wait()

    async def commit(self, holder: str, reservation_id: int):
        await self._pause("commit")
        return await super().commit(holder, reservation_id)

    async def release(self, holder: str, reservation_id: int):
        await self._pause("release")
        return await super().release(holder, reservation_id)


def exercise_boundary(entry, monkeypatch, utc_clock, pair, *, path, payload,
                      action, expected_status, enabled, missing_key=False):
    import access_keys

    utc_clock[0][0] = BEFORE
    worker, module, _ = deploy(entry, monkeypatch, utc_clock, *pair)
    worker.env.X402_ENABLED = enabled
    ledger = BlockingLedger(action)
    worker.env.CREDITS = ledger
    old_id, new_id = [load_snapshot_bytes(raw, key=KEY, public_keys={}).snapshot_id
                      for raw in pair]
    # A non-exempt key must reach the real charge path rather than bypass it.
    record = access_keys.KeyRecord(key_id="model402", tier="free", owner="test",
                                   created_at="2026-11-30")
    health_worker = module.Default()
    health_worker.env = _entry_env(MODELSPEC_SNAPSHOT_KEY=KEY.decode(),
                                   EXPORT_ORIGIN=worker.env.EXPORT_ORIGIN)

    async def interleave():
        await worker.env.ACCESS.put(access_keys.storage_name(API_KEY),
                                    json.dumps(record.to_json()))
        holder = x402.holder_from_key(API_KEY)
        assert holder is not None
        funded = await ledger.credit(holder, "round3-test-pack", 100, "fixture-tx")
        assert funded.credited
        selected = module._decision_holder(worker.env.EXPORT_ORIGIN)
        assert (await selected.current(KEY)).snapshot_id == old_id
        if missing_key:
            worker.env.MODELSPEC_SNAPSHOT_KEY = ""
        headers = {"Authorization": "Bearer " + API_KEY}
        first = asyncio.create_task(worker.fetch(_Req(path, payload, headers=headers)))
        try:
            await asyncio.wait_for(ledger.reached.wait(), timeout=3)
            reserved = await ledger.balance(holder)
            assert reserved.reserved == 2
            assert not first.done(), "the real credit RPC must hold delivery"
            utc_clock[0][0] = BOUNDARY
            current = await health_worker.fetch(_Req("/v1/health", method="GET"))
            assert current.status == 200, current.json()
            assert current.json()["decision_snapshot"]["id"] == new_id
            assert selected.snapshot.snapshot_id == new_id
        finally:
            ledger.resume.set()
            response = await first
        body = response.json()
        assert response.status == expected_status, body
        assert ledger.calls == [action], "exercise the intended real commit or release"
        balance = await ledger.balance(holder)
        assert balance.reserved == 0
        assert balance.available == (98 if action == "commit" else 100)
        if missing_key:
            assert body["snapshot"] is None
            assert "x-modelspec-snapshot" not in response.headers
        else:
            assert body["snapshot"] == old_id
            assert response.headers["x-modelspec-snapshot"] == body["snapshot"]
        return body

    return asyncio.run(asyncio.wait_for(interleave(), timeout=8))


@pytest.mark.parametrize("enabled", ["false", "true"], ids=["x402-off", "x402-on"])
@pytest.mark.parametrize("outcome,action,status", [
    ("undetermined", "commit", 200),
    ("invalid-request", "release", 400),
    ("no-snapshot", "release", 503),
])
def test_hardware_fit_snapshot_header_survives_credit_io(
    entry, monkeypatch, utc_clock, signed_pair, enabled, outcome, action, status,
):
    payload = {"model": MODEL, "sku": "fixture_gpu", "device_count": 1,
               "runtime": "fixture-runtime@1", "quantisation": "q4", "batch": 1,
               "context": 1024}
    if outcome == "invalid-request":
        payload["device_count"] = 0
    body = exercise_boundary(
        entry, monkeypatch, utc_clock, signed_pair,
        path="/v1/hardware-fit", payload=payload, action=action,
        expected_status=status, enabled=enabled, missing_key=outcome == "no-snapshot",
    )
    if outcome == "undetermined":
        assert body["status"] == "undetermined"
    else:
        assert body["error"]["code"] == ("no_snapshot" if outcome == "no-snapshot"
                                           else "invalid_request")


@pytest.mark.parametrize("enabled", ["false", "true"], ids=["x402-off", "x402-on"])
@pytest.mark.parametrize("route,outcome,action,status", [
    ("decide", "success", "commit", 200),
    ("decide", "refused", "release", 400),
    ("compare", "success", "release", 200),
    ("compare", "refused", "release", 400),
    ("compare-models", "success", "commit", 200),
    ("compare-models", "refused", "release", 400),
])
def test_decision_routes_keep_their_snapshot_header_during_credit_io(
    entry, monkeypatch, utc_clock, signed_pair, comparison_pair,
    enabled, route, outcome, action, status,
):
    pair = comparison_pair if route == "compare-models" else signed_pair
    spec = SPEC if outcome == "success" else SPEC | {
        "optimize": {"min": "unregistered.facet"},
    }
    if route == "compare":
        previous = load_snapshot_bytes(pair[0], key=KEY, public_keys={})
        payload = {"compare_to": previous.snapshot_id, "spec": spec}
    elif route == "compare-models":
        payload = {"models": [MODEL, PEER] if outcome == "success" else [MODEL]}
    else:
        payload = spec
    exercise_boundary(
        entry, monkeypatch, utc_clock, pair,
        path="/v1/" + route, payload=payload, action=action,
        expected_status=status, enabled=enabled,
    )
