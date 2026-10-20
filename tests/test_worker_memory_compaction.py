"""MODEL-417: the Worker holds its bundled data compactly, with unchanged answers."""

from __future__ import annotations

import gzip
import importlib.util
import io
import json
from array import array
from pathlib import Path

import pytest

from decision import json_stream
from decision import snapshot as snapshots

KEY = "model417-test-key"
ROOT = Path(__file__).resolve().parents[1]


def _signed(content_records):
    built = snapshots.build_snapshot(snapshots.SnapshotInputs())
    content = {**built.content, "record_table": snapshots._pack_records(content_records)}
    digest = snapshots.content_hash(content)
    return snapshots.Snapshot(content, digest, snapshots.snapshot_id_for(digest))


RECORDS = {
    f"fact:{index:04d}": {
        "id": f"fact:{index:04d}",
        "value": index,
        **({"citation": {"status": "cited", "sources": [{"source_id": "s"}]},
            "verification": None} if index % 7 == 0 else {"verification": {"outcome": "verified"}}),
    }
    for index in range(300)
}


def test_streamed_snapshot_packs_every_row_and_returns_the_same_records():
    raw = _signed(RECORDS).to_bytes(key=KEY, ed25519_signer=None)
    loaded = snapshots.load_snapshot_bytes(raw, key=KEY, public_keys={})
    rows = loaded._record_table["rows"]
    assert {type(row) for row in rows.values()} == {array}
    assert {row.typecode for row in rows.values()} == {"H"}
    assert {rid: loaded.record(rid) for rid in RECORDS} == RECORDS


@pytest.mark.parametrize("row, unpacked", [
    ([None, 0, 1, None], [None, 0, 1, None]),
    ([65534, None], [65534, None]),
    ([65535, 70000], [65535, 70000]),
    ([True, False, None], [1, 0, None]),
])
def test_packed_rows_read_back_the_loaded_positions(row, unpacked):
    packed = snapshots._pack_row(row)
    assert type(packed) is array
    table = {"fields": [("a",), ("b",), ("c",), ("d",)][:len(row)],
             "values": [json.dumps(i) for i in range(70001)], "rows": {"r": packed}}
    expected = {path[0]: position for path, position in zip(table["fields"], unpacked)
                if position is not None}
    assert snapshots._unpack_record(table, "r") == expected


@pytest.mark.parametrize("row", [
    [-1, None], [None, -2], [1.0], ["1"], [[1]], [2 ** 32 - 1], [2 ** 40], (1, 2), {"a": 1},
])
def test_rows_that_are_not_plain_positions_stay_as_loaded(row):
    assert snapshots._pack_row(row) is row


def test_non_canonical_snapshot_is_hashed_from_unpacked_content():
    built = _signed(RECORDS)
    envelope = json.loads(gzip.decompress(built.to_bytes(key=KEY, ed25519_signer=None)))
    # Indented JSON is not canonical: its digest must come from the content.
    raw = gzip.compress(json.dumps(envelope, indent=1).encode(), mtime=0)
    loaded = snapshots.load_snapshot_bytes(raw, key=KEY, public_keys={})
    assert loaded.snapshot_id == built.snapshot_id
    assert {rid: loaded.record(rid) for rid in RECORDS} == RECORDS


@pytest.mark.parametrize("chunk_size", [1, 7, 65536])
def test_stream_transforms_apply_only_at_their_paths(monkeypatch, chunk_size):
    monkeypatch.setattr(json_stream, "_CHUNK_SIZE", chunk_size)
    value = {"a": {"rows": {"x": [1, None], "y": [2]}, "other": [3]},
             "rows": {"x": [4]}, "b": {"rows": {"x": [5]}}}
    seen = []

    def mark(item):
        seen.append(item)
        return ("packed", tuple(item))

    reader = json_stream.JSONStreamReader(
        io.StringIO(json.dumps(value)), transforms={"a": {"rows": {"*": {None: mark}}}})
    result = reader.read_value()
    reader.finish()
    assert result == {"a": {"rows": {"x": ("packed", (1, None)), "y": ("packed", (2,))},
                            "other": [3]},
                      "rows": {"x": [4]}, "b": {"rows": {"x": [5]}}}
    assert seen == [[1, None], [2]]


def test_generated_bundle_streams_the_same_bytes_it_reads():
    import base64
    import types

    spec = importlib.util.spec_from_file_location("model417_vendor", ROOT / "api/worker/vendor.py")
    vendor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vendor)
    exports = {"/api/rank/candidates.json": json.dumps({"candidates": ["é"] * 5000}).encode(),
               "/api/policy/catalogue.json": b"{}"}
    blobs = {path: base64.b64encode(gzip.compress(raw, mtime=0)).decode("ascii")
             for path, raw in exports.items()}
    data = types.ModuleType("model417_bundled")
    exec(vendor.bundled_data_source(blobs, {}), data.__dict__)
    for path, raw in exports.items():
        assert data.read(path) == raw
        assert data.stream(path).read() == raw
    assert data.read("/api/missing.json") is None and data.stream("/api/missing.json") is None


def test_uncited_rank_candidates_share_one_empty_citation_value():
    from api.worker.src import rank_service

    base = {"model_id": "lab/a", "display_name": "A", "provider": "lab"}
    cited = {**base, "model_id": "lab/c", "cited_facts": [{"facet": "model.class"}],
             "cited_benchmarks": {"b": {"status": "cited", "url": "https://x.ai/"}}}
    prepared = rank_service.candidates_from_export(
        {"candidates": [base, {**base, "model_id": "lab/b"}, cited]})
    assert prepared[0].cited_facts is prepared[1].cited_facts
    assert prepared[0].cited_benchmarks is prepared[1].cited_benchmarks
    assert not prepared[0].cited_facts and not prepared[0].cited_benchmarks
    assert prepared[2].cited_facts == [{"facet": "model.class"}]
    assert prepared[2].cited_benchmarks == {"b": {"status": "cited", "url": "https://x.ai/"}}


@pytest.mark.parametrize("cited_facts, cited_benchmarks", [
    ([{"facet": "model.class"}], None),
    (None, {"humaneval": {"status": "cited", "url": "https://x.ai/"}}),
])
def test_one_sided_citation_serializes_the_shared_empty_as_json(cited_facts, cited_benchmarks):
    """`score` emits both citation fields when either is non-empty (review of #843)."""
    from api.worker.src import rank_service
    from pipeline import ranking

    row = {"model_id": "lab/c", "display_name": "C", "provider": "lab",
           "benchmark_scores": {"humaneval": 80.0}}
    if cited_facts is not None:
        row["cited_facts"] = cited_facts
    if cited_benchmarks is not None:
        row["cited_benchmarks"] = cited_benchmarks
    [candidate] = rank_service.candidates_from_export({"candidates": [row]})
    scored = ranking.score(candidate, {"benchmark_weights": {"humaneval": 1}})
    # The Worker's encoder (`entry._json_response`) and a plain encoder.
    for text in (json.dumps(scored, indent=2, default=str), json.dumps(scored)):
        body = json.loads(text)
        assert body["cited_facts"] == (cited_facts or [])
        assert body["cited_benchmarks"] == (cited_benchmarks or {})
    assert type(scored["cited_facts"]) is list and type(scored["cited_benchmarks"]) is dict
