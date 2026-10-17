"""A loaded price snapshot stops answering when its signed interval ends."""

from __future__ import annotations

import asyncio
from datetime import date

import pytest

from decision.contract import parse_spec
from decision.engine import decide
from decision.snapshot import (
    Snapshot,
    SnapshotError,
    SnapshotInputs,
    build_snapshot,
    content_hash,
    load_snapshot_bytes,
    snapshot_id_for,
)
from tests.snapshot_records import SOURCES, model
from tests.test_decide_snapshot_refresh import Clock, GatedOrigin, Origin, _load_service

KEY = b"dated-price-serving-test"
PAYLOAD = {
    "spec_version": 1,
    "optimize": {"min": "model.context_window"},
    "explain": "none",
}


def _snapshot_bytes(start: str = "2026-11-01", until: str = "2026-12-01") -> bytes:
    built = build_snapshot(
        SnapshotInputs(models=[model("lab/a")], sources=SOURCES),
        as_of=date.fromisoformat(start),
    )
    content = {**built.content, "valid_from": start, "valid_until": until}
    digest = content_hash(content)
    return Snapshot(content, digest, snapshot_id_for(digest)).to_bytes(key=KEY)


@pytest.fixture
def service():
    return _load_service()


def test_engine_refuses_an_expired_signed_snapshot() -> None:
    snapshot = load_snapshot_bytes(_snapshot_bytes("2000-01-01", "2000-01-02"), key=KEY)

    with pytest.raises(SnapshotError, match="valid|expir"):
        decide(parse_spec(PAYLOAD, facets=None), snapshot)


def test_historical_decision_requires_an_explicit_validity_bypass() -> None:
    snapshot = load_snapshot_bytes(_snapshot_bytes("2000-01-01", "2000-01-02"), key=KEY)
    spec = parse_spec(PAYLOAD, facets=None)

    with pytest.raises(SnapshotError, match="valid|expir"):
        decide(spec, snapshot, comparison=True)
    answer = decide(spec, snapshot, comparison=True, _validate_current=False)

    assert answer.snapshot == snapshot.snapshot_id
    assert [row.offering.model for row in answer.results] == ["lab/a"]


def test_hosted_decide_maps_expiry_to_the_existing_unavailable_response(service) -> None:
    snapshot = load_snapshot_bytes(_snapshot_bytes("2000-01-01", "2000-01-02"), key=KEY)

    status, body = service.decide(PAYLOAD, snapshot)

    assert status == 503
    assert body["error"] == "no_snapshot"
    assert body["snapshot"] is None
    assert "valid" in body["message"] or "expir" in body["message"]


def test_hosted_comparison_can_read_an_expired_historical_snapshot(service) -> None:
    old = load_snapshot_bytes(_snapshot_bytes("2000-01-01", "2000-01-02"), key=KEY)
    current = load_snapshot_bytes(_snapshot_bytes("2000-01-02", "2099-01-01"), key=KEY)

    status, body = service.compare(
        {"compare_to": old.snapshot_id, "spec": PAYLOAD}, old, current,
    )

    assert status == 200
    assert body["snapshot"] == current.snapshot_id
    assert body["compare_to"] == old.snapshot_id


@pytest.mark.parametrize("refresh", ["cached", "304", "same-bytes", "network", "http"])
def test_a_warm_snapshot_cannot_serve_after_midnight(service, refresh: str) -> None:
    origin, clock = Origin(_snapshot_bytes()), Clock()
    today = [date(2026, 11, 30)]
    holder = service.SnapshotHolder(origin, clock=clock, today=lambda: today[0])
    first = asyncio.run(holder.current(KEY))
    assert first.snapshot_id

    today[0] = date(2026, 12, 1)
    if refresh != "cached":
        clock.now += service.REVALIDATE_SECONDS
    if refresh == "same-bytes":
        origin.etag = '"same-body-new-etag"'
    elif refresh == "network":
        origin.fail = OSError("origin unavailable")
    elif refresh == "http":
        origin.status = 500

    with pytest.raises(service.SnapshotRefusalError, match="valid|expir"):
        asyncio.run(holder.current(KEY))


def test_a_bundled_snapshot_cannot_serve_after_midnight(service) -> None:
    snapshot = load_snapshot_bytes(_snapshot_bytes(), key=None, public_keys={})
    today = [date(2026, 11, 30)]

    async def no_fetch(etag):
        raise AssertionError("a bundled snapshot must not fetch")

    holder = service.SnapshotHolder(
        no_fetch, bundled_snapshot=snapshot, today=lambda: today[0],
    )
    assert asyncio.run(holder.current(KEY)) is snapshot
    today[0] = date(2026, 12, 1)

    with pytest.raises(service.SnapshotRefusalError, match="valid|expir"):
        asyncio.run(holder.current(KEY))


def test_a_new_snapshot_restores_service_after_the_boundary(service) -> None:
    origin, clock = Origin(_snapshot_bytes()), Clock()
    today = [date(2026, 11, 30)]
    holder = service.SnapshotHolder(origin, clock=clock, today=lambda: today[0])
    before = asyncio.run(holder.current(KEY))
    today[0] = date(2026, 12, 1)
    origin.publish(_snapshot_bytes("2026-12-01", "2027-01-01"), '"december"')
    clock.now += service.REVALIDATE_SECONDS

    after = asyncio.run(holder.current(KEY))

    assert after.snapshot_id != before.snapshot_id
    assert holder.headers() == {"x-modelspec-snapshot": after.snapshot_id}


def test_an_expired_snapshot_is_refused_while_a_refresh_is_loading(service) -> None:
    origin, clock = GatedOrigin(_snapshot_bytes()), Clock()
    today = [date(2026, 11, 30)]
    holder = service.SnapshotHolder(origin, clock=clock, today=lambda: today[0])

    async def cross_boundary():
        await holder.current(KEY)
        today[0] = date(2026, 12, 1)
        clock.now += service.REVALIDATE_SECONDS
        origin.gate = asyncio.Event()
        refresh = asyncio.create_task(holder.current(KEY))
        try:
            await asyncio.sleep(0)
            with pytest.raises(service.SnapshotRefusalError, match="valid|expir"):
                await holder.current(KEY)
        finally:
            origin.gate.set()
            outcome = await asyncio.gather(refresh, return_exceptions=True)
        assert len(outcome) == 1
        assert isinstance(outcome[0], service.SnapshotRefusalError)

    asyncio.run(asyncio.wait_for(cross_boundary(), timeout=5))


def test_waiters_refuse_a_snapshot_that_expires_during_its_first_load(service) -> None:
    origin, clock = GatedOrigin(_snapshot_bytes()), Clock()
    today = [date(2026, 11, 30)]
    holder = service.SnapshotHolder(origin, clock=clock, today=lambda: today[0])

    async def cross_boundary():
        origin.gate = asyncio.Event()
        loader = asyncio.create_task(holder.current(KEY))
        await asyncio.sleep(0)
        waiter = asyncio.create_task(holder.current(KEY))
        await asyncio.sleep(0)
        today[0] = date(2026, 12, 1)
        origin.gate.set()
        outcomes = await asyncio.gather(loader, waiter, return_exceptions=True)
        assert all(isinstance(outcome, service.SnapshotRefusalError) for outcome in outcomes)

    asyncio.run(asyncio.wait_for(cross_boundary(), timeout=5))
