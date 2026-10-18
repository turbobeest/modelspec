"""Lazy successors keep one resident price period and authenticate before use."""

import asyncio
import gc
import hashlib
import weakref
from datetime import UTC, datetime

import pytest

from tests.test_snapshot_successor import (
    API_KEY,
    BOUNDARY,
    SPEC,
    SUCCESSOR_PATH,
    deploy,
    request,
)
from tests.test_snapshot_successor import (
    signed_pair as signed_pair,
)
from tests.test_snapshot_successor import (
    utc_clock as utc_clock,
)
from tests.test_x402 import _Req
from tests.test_x402 import entry as entry


def test_successor_is_not_read_parsed_or_verified_at_isolate_start(
    entry, monkeypatch, utc_clock, signed_pair,
):
    parsed, verified = [], []
    load = entry.decide_service.load_snapshot_bytes
    verify = entry.decide_service.verify_hmac_signature

    def record_parse(*args, **kwargs):
        parsed.append(kwargs.get("source"))
        return load(*args, **kwargs)

    def record_verify(*args, **kwargs):
        verified.append(kwargs.get("source"))
        return verify(*args, **kwargs)

    monkeypatch.setattr(entry.decide_service, "load_snapshot_bytes", record_parse)
    monkeypatch.setattr(entry.decide_service, "verify_hmac_signature", record_verify)
    _, _, bundle = deploy(entry, monkeypatch, utc_clock, *signed_pair)
    assert parsed == ["bundled decision snapshot"]
    assert verified == []
    assert SUCCESSOR_PATH not in bundle.reads
    assert "/api/decision/vocabulary-successor.json" not in bundle.reads


def test_successor_stays_unparsed_through_the_utc_preload_window(
    entry, monkeypatch, utc_clock, signed_pair,
):
    utc_clock[0][0] = datetime(2026, 11, 29, 23, 59, 59, tzinfo=UTC)
    worker, _, bundle = deploy(entry, monkeypatch, utc_clock, *signed_pair)
    for instant in (
        utc_clock[0][0],
        datetime(2026, 11, 30, tzinfo=UTC),
        datetime(2026, 11, 30, 23, 59, 59, tzinfo=UTC),
    ):
        utc_clock[0][0] = instant
        response = request(worker)
        assert response.status == 200, response.json()
        assert response.json()["results"][0]["cost_per_task"] == 12
        assert SUCCESSOR_PATH not in bundle.reads
    utc_clock[0][0] = BOUNDARY
    response = request(worker)
    assert response.status == 200, response.json()
    assert response.json()["results"][0]["cost_per_task"] == 24
    assert bundle.reads.count(SUCCESSOR_PATH) == 1
    assert request(worker).status == 200
    assert bundle.reads.count(SUCCESSOR_PATH) == 1


def test_rollover_releases_current_snapshot_and_vocabulary_before_loading_successor(
    entry, monkeypatch, utc_clock, signed_pair,
):
    utc_clock[0][0] = datetime(2026, 11, 30, tzinfo=UTC)
    worker, module, bundle = deploy(entry, monkeypatch, utc_clock, *signed_pair)
    assert request(worker, "/v1/vocabulary").status == 200
    holder = module._decision_holder(worker.env.EXPORT_ORIGIN)
    assert module._decision_holder("https://another-export.example") is holder
    previous = weakref.ref(holder.snapshot)
    read = bundle.read
    loads = []

    def check_release(path):
        if path == SUCCESSOR_PATH:
            gc.collect()
            assert previous() is None
            assert module._bundled_vocabulary is None
            assert module._bundled_vocabulary_text is None
            loads.append(path)
        return read(path)

    bundle.read = check_release
    utc_clock[0][0] = BOUNDARY
    response = request(worker, "/v1/vocabulary")
    assert response.status == 200, response.json()
    assert loads == [SUCCESSOR_PATH]
    assert previous() is None
    assert response.json()["snapshot"] == holder.snapshot.snapshot_id


@pytest.mark.parametrize("query", ["", "?section=facets&detail=full"])
def test_vocabulary_metering_does_not_retain_old_snapshot_or_parsed_vocabulary(
    entry, monkeypatch, utc_clock, signed_pair, query,
):
    class TrackedDict(dict):
        pass

    utc_clock[0][0] = datetime(2026, 11, 30, 23, 59, 59, tzinfo=UTC)
    worker, module, bundle = deploy(entry, monkeypatch, utc_clock, *signed_pair)
    module._bundled_vocabulary = TrackedDict(module._bundled_vocabulary)
    module._bundled_vocabulary["facets"][0] = TrackedDict(
        module._bundled_vocabulary["facets"][0])
    expected_body = request(worker, "/v1/vocabulary" + query).body
    holder = module._decision_holder(worker.env.EXPORT_ORIGIN)
    previous_id = holder.snapshot.snapshot_id
    previous = weakref.ref(holder.snapshot)
    vocabulary = weakref.ref(module._bundled_vocabulary)
    facet = weakref.ref(module._bundled_vocabulary["facets"][0])
    read = bundle.read
    released_at_load = []

    def check_release(path):
        if path == SUCCESSOR_PATH:
            gc.collect()
            released_at_load.append((previous() is None, vocabulary() is None, facet() is None))
        return read(path)

    bundle.read = check_release

    async def interleave():
        reached, release = asyncio.Event(), asyncio.Event()

        async def pause_metering(*args):
            reached.set()
            await release.wait()
            return None

        monkeypatch.setattr(worker, "_meter_catalog_read", pause_metering)
        headers = {"Authorization": "Bearer " + API_KEY}
        pending = asyncio.create_task(worker.fetch(_Req(
            "/v1/vocabulary" + query, {}, method="GET", headers=headers)))
        try:
            await reached.wait()
            utc_clock[0][0] = BOUNDARY
            newer = await worker.fetch(_Req("/v1/decide", SPEC, headers=headers))
            assert newer.status == 200, newer.json()
            assert newer.json()["snapshot"] != previous_id
            assert released_at_load == [(True, True, True)]
            assert previous() is None
        finally:
            release.set()
            before = await pending
        assert before.status == 200, before.json()
        assert before.body == expected_body

    asyncio.run(asyncio.wait_for(interleave(), timeout=5))


def test_successor_metadata_signature_refuses_current_more_than_24_hours_before_expiry(
    entry, monkeypatch, utc_clock, signed_pair,
):
    utc_clock[0][0] = datetime(2026, 11, 29, tzinfo=UTC)
    worker, _, bundle = deploy(entry, monkeypatch, utc_clock, *signed_pair)
    bundle.SNAPSHOTS[SUCCESSOR_PATH]["signature"]["value"] = "0" * 64
    response = request(worker)
    assert response.status == 503
    assert response.json()["error"]["code"] == "snapshot_refused"
    assert SUCCESSOR_PATH not in bundle.reads


@pytest.mark.parametrize("replace_blob_hash", [False, True])
def test_successor_payload_must_match_authenticated_content_and_exact_blob(
    entry, monkeypatch, utc_clock, signed_pair, replace_blob_hash,
):
    utc_clock[0][0] = datetime(2026, 11, 30, tzinfo=UTC)
    worker, module, bundle = deploy(entry, monkeypatch, utc_clock, *signed_pair)
    assert request(worker).status == 200
    bundle.blobs[SUCCESSOR_PATH] = signed_pair[0]
    if replace_blob_hash:
        bundle.SNAPSHOTS[SUCCESSOR_PATH]["blob_sha256"] = hashlib.sha256(signed_pair[0]).hexdigest()
    utc_clock[0][0] = BOUNDARY
    response = request(worker)
    assert response.status == 503
    assert response.json()["error"]["code"] == "snapshot_refused"
    assert "x-modelspec-snapshot" not in response.headers
    assert module._decision_holder(worker.env.EXPORT_ORIGIN).snapshot is None
    repeated = request(worker)
    assert repeated.status == 503
    assert repeated.json()["error"]["code"] == "snapshot_refused"


def test_successor_load_failure_stays_a_refusal_on_following_requests(
    entry, monkeypatch, utc_clock, signed_pair,
):
    utc_clock[0][0] = datetime(2026, 11, 30, tzinfo=UTC)
    worker, _, bundle = deploy(entry, monkeypatch, utc_clock, *signed_pair)
    assert request(worker).status == 200
    read = bundle.read
    loads = []

    def broken_read(path):
        if path == SUCCESSOR_PATH:
            loads.append(path)
            raise OSError("synthetic corrupt bundled compression")
        return read(path)

    bundle.read = broken_read
    utc_clock[0][0] = BOUNDARY
    for _ in range(2):
        response = request(worker)
        assert response.status == 503, response.json()
        assert response.json()["error"]["code"] == "snapshot_refused"
        assert "x-modelspec-snapshot" not in response.headers
    assert loads == [SUCCESSOR_PATH]
