"""MODEL-407: retain compact provenance until a hardware-fit request needs it."""

from __future__ import annotations

import asyncio
import copy
import gzip
import json
from pathlib import Path

import pytest

from decision import snapshot as snapshots
from tests.test_decide_worker import KEY
from tests.test_hardware_fit import (
    MODEL,
    REQUEST,
    SKU,
    assess,
    fixture_snapshot,
    hardware_fit_record,
    lower_bound_record,
)
from tests.test_hardware_fit_worker import _keyed_worker
from tests.test_x402 import _Req
from tests.test_x402 import entry as entry


def test_hardware_fit_snapshot_retains_source_ids_and_one_copy_of_each_record():
    compiled = fixture_snapshot(built=True)
    assert "hardware_fit_records" not in compiled.content
    assert compiled.content["hardware_fit_record_ids"] == ["hardware-fit:fixture"]
    record = snapshots._unpack_record(
        compiled.content["hardware_fit_record_table"], "hardware-fit:fixture")
    assert record["source_ids"] == ["run-source"]
    assert record["per_device"][0]["weights_bytes"]["source_ids"] == ["run-source"]
    assert "https://" not in json.dumps(record)


def test_hardware_fit_fields_do_not_pad_every_other_provenance_record():
    without = fixture_snapshot([], built=True).content["record_table"]
    with_hardware = fixture_snapshot(built=True).content["record_table"]
    assert with_hardware == without


def test_hardware_fit_loads_records_once_on_first_assessment(monkeypatch):
    compiled = fixture_snapshot(built=True)
    decoded = []
    unpack = snapshots._unpack_record

    def tracked_unpack(table, record_id):
        decoded.append(record_id)
        return unpack(table, record_id)

    monkeypatch.setattr(snapshots, "_unpack_record", tracked_unpack)
    snapshot = snapshots.load_snapshot_bytes(compiled.to_bytes(key=KEY), key=KEY)
    assert decoded == []
    assert snapshot.candidates() == (MODEL,)
    assert decoded == []

    _, first = assess(snapshot=snapshot)
    assert decoded.count("hardware-fit:fixture") == 1
    _, second = assess(snapshot=snapshot)
    assert decoded.count("hardware-fit:fixture") == 1
    assert first == second
    assert snapshot.hardware_fit_records(MODEL, SKU)[0] is snapshot.record("hardware-fit:fixture")


def test_legacy_hardware_fit_snapshot_keeps_its_response():
    compiled = fixture_snapshot(built=True)
    current = snapshots.load_snapshot_bytes(compiled.to_bytes(key=KEY), key=KEY)
    content = copy.deepcopy(compiled.content)
    content.pop("hardware_fit_record_ids", None)
    hardware = content.pop("hardware_fit_record_table")
    content["record_table"] = snapshots._pack_records({
        rid: snapshots._unpack_record(table, rid)
        for table in (content["record_table"], hardware)
        for rid in table["rows"]
    })
    content["hardware_fit_records"] = [dict(current.record("hardware-fit:fixture"))]
    digest = snapshots.content_hash(content)
    legacy = snapshots.Snapshot(content, digest, snapshots.snapshot_id_for(digest))
    loaded = snapshots.load_snapshot_bytes(legacy.to_bytes(key=KEY), key=KEY)
    _, expected = assess(snapshot=current)
    _, actual = assess(snapshot=loaded)
    expected["snapshot"] = actual["snapshot"]
    assert actual == expected


def test_unloaded_hardware_fit_provenance_is_still_signature_covered():
    compiled = fixture_snapshot(built=True)
    envelope = json.loads(gzip.decompress(compiled.to_bytes(key=KEY)))
    envelope["content"]["hardware_fit_record_table"]["values"][0] = '"altered"'
    tampered = gzip.compress(snapshots.canonical_json(envelope))
    with pytest.raises(snapshots.SnapshotIntegrityError, match="content hash"):
        snapshots.load_snapshot_bytes(tampered, key=KEY)


@pytest.mark.parametrize("case", ["measured", "full", "lower-bound", "undetermined"])
def test_hardware_fit_2_0_response_bytes_match_before_memory_change(entry, monkeypatch, case):
    records = {
        "measured": [hardware_fit_record("measured")],
        "full": [hardware_fit_record()],
        "lower-bound": [lower_bound_record()],
        "undetermined": [],
    }[case]
    compiled = fixture_snapshot(records, memory_gb=32 if case == "lower-bound" else 24, built=True)
    snapshot = snapshots.load_snapshot_bytes(compiled.to_bytes(key=KEY), key=KEY)
    monkeypatch.setattr(entry, "_bundled_decision_snapshot", snapshot)
    worker, headers = _keyed_worker(entry)
    response = asyncio.run(worker.fetch(_Req("/v1/hardware-fit", REQUEST, headers=headers)))
    assert response.status == 200
    # Snapshot IDs address the signed representation, which this change compacts.
    actual = response.body.replace(snapshot.snapshot_id, "snap_golden_hardware_fit_2_0")
    golden = Path(__file__).parent / "fixtures/hardware-fit-2.0" / f"{case}.json"
    assert actual.encode("utf-8") == golden.read_bytes()
