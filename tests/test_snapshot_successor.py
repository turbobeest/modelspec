"""Bundled signed price periods hand over at midnight without a deployment."""

from __future__ import annotations

import asyncio
import gzip
import hashlib
import importlib.util
import json
import sys
from datetime import UTC, date, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

import decision.snapshot as snapshots
from decision.snapshot import SnapshotInputs, build_snapshot, load_snapshot_bytes
from tests.snapshot_records import SOURCES, fact, model, offering, verification
from tests.test_decide_snapshot_refresh import Clock, Origin
from tests.test_x402 import _Req, _entry_env, entry  # noqa: F401

KEY = b"MODEL-402-synthetic-signing-key"
API_KEY = "sk_model402_fixture"
MODEL = "lab/argon"
OFFERING = f"sambanova/{MODEL}/global/standard"
CURRENT_PATH = "/api/decision/snapshot.json.gz"
SUCCESSOR_PATH = "/api/decision/snapshot-successor.json.gz"
BOUNDARY = datetime(2026, 12, 1, tzinfo=UTC)
SPEC = {
    "spec_version": 1,
    "optimize": {"min": "offering.cost_per_task"},
    "task_tokens": {"input": 1_000_000, "output": 1_000_000},
    "explain": "full",
}


def test_health_contract_adds_optional_snapshot_metadata_with_declared_nullability():
    schema = yaml.safe_load((Path(__file__).resolve().parents[1]
                             / "api/worker/openapi.yaml").read_text())
    health = schema["components"]["schemas"]["Health"]
    assert "decision_snapshot" not in health["required"]
    metadata = health["properties"]["decision_snapshot"]["properties"]
    for name in ("id", "valid_until", "successor_valid_from"):
        assert metadata[name]["type"] == "string"
        assert metadata[name]["nullable"] is True
    assert metadata["successor_held"]["type"] == "boolean"


@pytest.fixture(scope="module")
def signed_pair():
    rows = []
    for side, old, new in (("input", 2, 4), ("output", 10, 20)):
        for amount, start, end in (
            (old, "2026-10-14", "2026-11-30"),
            (new, "2026-12-01", "2026-12-31"),
        ):
            row = fact("offering", OFFERING, f"offering.price.{side}", amount,
                       source="src-pricing")
            row.update(id=row["id"] + "@" + start,
                       effective_from=start, effective_until=end)
            row["verification"] = verification("fact", row["id"], value={
                "value": amount, "effective_from": start, "effective_until": end,
            })
            rows.append(row)
    inputs = SnapshotInputs(models=[model(MODEL)],
                            offerings=[offering(MODEL, facts=rows)], sources=SOURCES)
    return tuple(build_snapshot(inputs, as_of=day).to_bytes(key=KEY, ed25519_signer=None)
                 for day in (date(2026, 11, 30), date(2026, 12, 1)))


@pytest.fixture
def utc_clock(monkeypatch):
    now = [BOUNDARY]

    class FrozenDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return now[0].astimezone(tz) if tz is not None else now[0].replace(tzinfo=None)

    monkeypatch.setattr(snapshots, "datetime", FrozenDatetime)
    return now, FrozenDatetime


def deploy(entry, monkeypatch, utc_clock, primary, successor=None):
    import access_keys

    blobs = {
        CURRENT_PATH: primary,
        "/api/rank/candidates.json": json.dumps({
            "build": {"commit": "fixture", "built_at": "2026-11-30T00:00:00Z",
                      "export_schema_version": "2.0"}, "candidates": [],
        }).encode(),
        "/api/policy/catalogue.json": b'{"models":[]}',
    }
    if successor is not None:
        blobs[SUCCESSOR_PATH] = successor
    for raw, path in ((primary, "/api/decision/vocabulary.json"),
                      (successor, "/api/decision/vocabulary-successor.json")):
        if raw is not None:
            snapshot = load_snapshot_bytes(raw, key=None, public_keys={})
            blobs[path] = json.dumps({
                "snapshot": snapshot.snapshot_id,
                "vocabulary_version": "1.0", "contract_version": "2.18",
                "facets": [{"id": "offering.price.input", "has_data": True,
                            "values": [snapshot.fact(OFFERING, "offering.price.input").value]}],
            }).encode()
    previous = load_snapshot_bytes(primary, key=KEY, public_keys={})
    blobs[f"/api/decision/snapshots/{previous.snapshot_id}.json.gz"] = primary
    metadata = {}
    if successor is not None:
        envelope = json.loads(gzip.decompress(successor))
        metadata[SUCCESSOR_PATH] = {
            "content_hash": envelope["content_hash"],
            "signature": envelope["signature"],
            "snapshot_id": envelope["snapshot_id"],
            "valid_from": envelope["content"].get("valid_from"),
            "valid_until": envelope["content"].get("valid_until"),
            "blob_sha256": hashlib.sha256(successor).hexdigest(),
        }
    reads = []

    def read(path):
        reads.append(path)
        return blobs.get(path)

    bundle = SimpleNamespace(read=read, SNAPSHOTS=metadata, blobs=blobs, reads=reads)
    monkeypatch.setitem(sys.modules, "bundled_data", bundle)
    spec = importlib.util.spec_from_file_location("model402_worker", entry.__file__)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module.decide_service, "datetime", utc_clock[1])
    worker = module.Default()
    worker.env = _entry_env(ACCESS_ENFORCED="true", X402_ENABLED="false",
                            MODELSPEC_SNAPSHOT_KEY=KEY.decode())
    record = access_keys.KeyRecord(key_id="model402", tier="dpf", owner="test",
                                   created_at="2026-11-30")
    asyncio.run(worker.env.ACCESS.put(access_keys.storage_name(API_KEY),
                                      json.dumps(record.to_json())))
    return worker, module, bundle


def request(worker, path="/v1/decide", payload=None, *, expected=None):
    headers = {"Authorization": "Bearer " + API_KEY}
    if expected is not None:
        headers["x-modelspec-snapshot"] = expected
    return asyncio.run(worker.fetch(_Req(
        path, SPEC if payload is None else payload,
        method="GET" if path.startswith(("/v1/health", "/v1/vocabulary")) else "POST", headers=headers,
    )))


@pytest.mark.parametrize("cold", [False, True])
@pytest.mark.parametrize("bounded", [False, True])
def test_keyed_decide_uses_the_correct_price_and_snapshot_at_the_boundary(
    entry, monkeypatch, utc_clock, signed_pair, cold, bounded,
):
    worker, module, bundle = deploy(entry, monkeypatch, utc_clock, *signed_pair)
    ids = [load_snapshot_bytes(raw, key=KEY, public_keys={}).snapshot_id for raw in signed_pair]
    payload = SPEC | ({"fields": ["model", "cost_per_task"]} if bounded else {})
    for instant, index, price in (
        (datetime(2026, 11, 30, 23, 59, 59, tzinfo=UTC), 0, 12),
        (BOUNDARY, 1, 24),
        (datetime(2026, 12, 2, tzinfo=UTC), 1, 24),
    ):
        utc_clock[0][0] = instant
        if cold:
            worker, module, bundle = deploy(entry, monkeypatch, utc_clock, *signed_pair)
        response = request(worker, payload=payload)
        body = response.json()
        assert response.status == 200, body
        assert body["snapshot"] == ids[index]
        assert response.headers["x-modelspec-snapshot"] == ids[index]
        assert body["results"][0]["cost_per_task"] == price
        if bounded:
            assert body["bounded_version"] == "1.5"
            assert body["projects_contract"] == "2.18"
        else:
            assert body["contract_version"] == "2.18"
        held = module._decision_holder(worker.env.EXPORT_ORIGIN).snapshot
        assert held.fact(OFFERING, "offering.price.input").value == (2 if index == 0 else 4)
        assert held.fact(OFFERING, "offering.price.output").value == (10 if index == 0 else 20)


@pytest.mark.parametrize("with_successor", [False, True])
def test_no_covering_bundled_snapshot_returns_no_snapshot(
    entry, monkeypatch, utc_clock, signed_pair, with_successor,
):
    utc_clock[0][0] = datetime(2027, 1, 1, tzinfo=UTC) if with_successor else BOUNDARY
    worker, _, _ = deploy(entry, monkeypatch, utc_clock, signed_pair[0],
                          signed_pair[1] if with_successor else None)
    response = request(worker)
    assert response.status == 503
    assert response.json()["error"] == "no_snapshot"
    assert response.json()["snapshot"] is None


@pytest.mark.parametrize("at_boundary", [False, True])
def test_tampered_successor_signature_refuses_the_bundle_before_either_is_used(
    entry, monkeypatch, utc_clock, signed_pair, at_boundary,
):
    utc_clock[0][0] = BOUNDARY if at_boundary else datetime(2026, 11, 30, tzinfo=UTC)
    envelope = json.loads(gzip.decompress(signed_pair[1]))
    envelope["signature"]["value"] = "0" * 64
    corrupt = gzip.compress(json.dumps(envelope).encode(), mtime=0)
    worker, module, _ = deploy(entry, monkeypatch, utc_clock, signed_pair[0], corrupt)
    response = request(worker)
    assert response.status == 503
    assert response.json()["error"]["code"] == "snapshot_refused"
    assert "signature" in response.json()["error"]["message"]
    assert module._decision_holder(worker.env.EXPORT_ORIGIN).snapshot is None


def test_health_selects_the_serving_snapshot_even_before_the_first_decision(
    entry, monkeypatch, utc_clock, signed_pair,
):
    utc_clock[0][0] = datetime(2026, 11, 30, 23, 59, 59, tzinfo=UTC)
    worker, _, _ = deploy(entry, monkeypatch, utc_clock, *signed_pair)
    for instant, index, until in (
        (utc_clock[0][0], 0, "2026-12-01"),
        (BOUNDARY, 1, "2027-01-01"),
        (datetime(2027, 1, 1, tzinfo=UTC), None, None),
    ):
        utc_clock[0][0] = instant
        response = request(worker, "/v1/health")
        assert response.status == 200, response.json()
        assert response.json()["schema_version"] == "1.0"
        expected_id = (load_snapshot_bytes(signed_pair[index], key=KEY, public_keys={}).snapshot_id
                       if index is not None else None)
        assert response.json()["decision_snapshot"] == {
            "id": expected_id, "valid_until": until,
            "successor_held": True, "successor_valid_from": "2026-12-01",
        }


def test_health_selects_after_metadata_io_crosses_midnight(
    entry, monkeypatch, utc_clock, signed_pair,
):
    utc_clock[0][0] = datetime(2026, 11, 30, 23, 59, 59, tzinfo=UTC)
    worker, _, _ = deploy(entry, monkeypatch, utc_clock, *signed_pair)

    async def cross_midnight():
        await asyncio.sleep(0)
        utc_clock[0][0] = BOUNDARY
        return {}

    monkeypatch.setattr(worker, "_determinations_health", cross_midnight)
    response = request(worker, "/v1/health")
    successor = load_snapshot_bytes(signed_pair[1], key=KEY, public_keys={})
    assert response.status == 200
    assert response.json()["decision_snapshot"]["id"] == successor.snapshot_id
    assert response.json()["decision_snapshot"]["valid_until"] == "2027-01-01"


def test_unbounded_snapshot_keeps_the_same_decision_bytes_and_no_successor(
    entry, monkeypatch, utc_clock,
):
    raw = build_snapshot(SnapshotInputs(models=[model(MODEL)], offerings=[offering(MODEL)],
                                        sources=SOURCES), as_of=date(2026, 11, 30)).to_bytes(
                                            key=KEY, ed25519_signer=None)
    worker, module, _ = deploy(entry, monkeypatch, utc_clock, raw)
    payload = {"spec_version": 1, "optimize": {"min": "model.context_window"}, "explain": "none"}
    response = request(worker, payload=payload)
    original = module.decide_service.decide(payload, module.decide_service.load_snapshot(raw, key=KEY))
    assert response.status == original[0] == 200
    assert response.body.encode() == module.decide_service.serialise(original[1])
    assert request(worker, "/v1/health").json()["decision_snapshot"] == {
        "id": original[1]["snapshot"], "valid_until": None,
        "successor_held": False, "successor_valid_from": None,
    }


def test_comparison_uses_successor_for_now_and_keeps_historical_prices(
    entry, monkeypatch, utc_clock, signed_pair,
):
    worker, module, _ = deploy(entry, monkeypatch, utc_clock, *signed_pair)
    old, new = [load_snapshot_bytes(raw, key=KEY, public_keys={}) for raw in signed_pair]
    response = request(worker, "/v1/compare", {"spec": SPEC, "compare_to": old.snapshot_id})
    assert response.status == 200, response.json()
    assert response.json()["snapshot"] == new.snapshot_id
    assert response.json()["compare_to"] == old.snapshot_id
    assert response.headers["x-modelspec-snapshot"] == new.snapshot_id
    assert old.fact(OFFERING, "offering.price.input").value == 2
    assert new.fact(OFFERING, "offering.price.input").value == 4


def test_failed_fetched_refresh_cannot_keep_old_prices_but_new_snapshot_restores_service(
    entry, monkeypatch, utc_clock, signed_pair,
):
    worker, module, _ = deploy(entry, monkeypatch, utc_clock, signed_pair[0])
    clock, origin = Clock(), Origin(signed_pair[0])
    holder = module.decide_service.SnapshotHolder(origin, clock=clock)
    monkeypatch.setattr(module, "_decision_holder", lambda origin: holder)
    utc_clock[0][0] = datetime(2026, 11, 30, 23, 59, 59, tzinfo=UTC)
    assert request(worker).status == 200
    utc_clock[0][0] = BOUNDARY
    clock.now += 60
    origin.fail = OSError("origin unavailable")
    response = request(worker)
    assert response.status == 503
    assert response.json()["error"] == "no_snapshot"
    origin.fail = None
    origin.publish(signed_pair[1], '"successor"')
    clock.now += 60
    response = request(worker)
    assert response.status == 200, response.json()
    assert response.json()["results"][0]["cost_per_task"] == 24
    assert "x-modelspec-snapshot-stale" not in response.headers


@pytest.mark.parametrize("query", ["", "?section=facets&id=offering.price.input&detail=full"])
def test_vocabulary_and_pinned_decisions_handover_together(
    entry, monkeypatch, utc_clock, signed_pair, query,
):
    worker, _, _ = deploy(entry, monkeypatch, utc_clock, *signed_pair)
    ids = [load_snapshot_bytes(raw, key=KEY, public_keys={}).snapshot_id for raw in signed_pair]
    for instant, index, price in (
        (datetime(2026, 11, 30, 23, 59, 59, tzinfo=UTC), 0, 2),
        (BOUNDARY, 1, 4),
        (datetime(2026, 12, 2, tzinfo=UTC), 1, 4),
    ):
        utc_clock[0][0] = instant
        vocabulary = request(worker, "/v1/vocabulary" + query)
        assert vocabulary.status == 200, vocabulary.json()
        assert vocabulary.headers["cache-control"] == "no-store"
        selected_id = (request(worker, "/v1/vocabulary").json()["snapshot"] if query
                       else vocabulary.json()["snapshot"])
        assert selected_id == ids[index]
        assert vocabulary.json()["facets"][0]["values"] == [price]
        decision = request(worker, expected=selected_id)
        assert decision.status == 200, decision.json()
        assert decision.json()["snapshot"] == ids[index]


def test_expired_warm_bundle_clears_snapshot_header_and_refuses_vocabulary(
    entry, monkeypatch, utc_clock, signed_pair,
):
    utc_clock[0][0] = datetime(2026, 11, 30, 23, 59, 59, tzinfo=UTC)
    worker, _, _ = deploy(entry, monkeypatch, utc_clock, signed_pair[0])
    assert request(worker).status == 200
    utc_clock[0][0] = BOUNDARY
    decision = request(worker)
    assert decision.status == 503
    assert "x-modelspec-snapshot" not in decision.headers
    vocabulary = request(worker, "/v1/vocabulary")
    assert vocabulary.status == 503
    assert vocabulary.json()["error"]["code"] == "no_snapshot"


def test_each_response_header_keeps_its_own_snapshot_during_concurrent_handover(
    entry, monkeypatch, utc_clock, signed_pair,
):
    utc_clock[0][0] = datetime(2026, 11, 30, 23, 59, 59, tzinfo=UTC)
    worker, module, _ = deploy(entry, monkeypatch, utc_clock, *signed_pair)
    old_id = load_snapshot_bytes(signed_pair[0], key=KEY, public_keys={}).snapshot_id
    gate = module.access.gate

    async def interleave():
        produced, release = asyncio.Event(), asyncio.Event()

        async def delayed_gate(**kwargs):
            outcome = await gate(**kwargs)
            if outcome.body.get("snapshot") == old_id:
                produced.set()
                await release.wait()
            return outcome

        monkeypatch.setattr(module.access, "gate", delayed_gate)
        headers = {"Authorization": "Bearer " + API_KEY}
        first = asyncio.create_task(worker.fetch(_Req("/v1/decide", SPEC, headers=headers)))
        try:
            await produced.wait()
            utc_clock[0][0] = BOUNDARY
            second = await worker.fetch(_Req("/v1/decide", SPEC, headers=headers))
        finally:
            release.set()
            before = await first
        assert before.status == second.status == 200
        assert before.json()["snapshot"] == old_id
        assert before.headers["x-modelspec-snapshot"] == old_id
        assert second.headers["x-modelspec-snapshot"] == second.json()["snapshot"]
        assert second.json()["snapshot"] != old_id

    asyncio.run(asyncio.wait_for(interleave(), timeout=5))
