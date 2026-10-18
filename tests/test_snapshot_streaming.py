"""Bounded snapshot decoding preserves signed JSON and retained records."""

import gc
import gzip
import hashlib
import io
import json
import weakref

import pytest

from decision import snapshot

KEY = "streaming-snapshot-test-key"


def _snapshot(record):
    built = snapshot.build_snapshot(snapshot.SnapshotInputs())
    content = {**built.content, "records": {"streaming": record}}
    digest = snapshot.content_hash(content)
    return snapshot.Snapshot(content, digest, snapshot.snapshot_id_for(digest))


def _load(raw):
    return snapshot.load_snapshot_bytes(raw, key=KEY, public_keys={})


def test_canonical_snapshot_does_not_decompress_the_whole_document(monkeypatch):
    record = {"text": "é🙂\\\" },\"content_hash\": " * 4000,
              "rows": [{"shared_field": index} for index in range(1000)]}
    raw = _snapshot(record).to_bytes(key=KEY, ed25519_signer=None)

    def whole_document(*args, **kwargs):
        pytest.fail("canonical snapshot allocated the entire decompressed document")

    monkeypatch.setattr(gzip, "decompress", whole_document)
    loaded = _load(raw)
    assert loaded.signature_verified
    assert loaded.record("streaming") == record


@pytest.mark.parametrize("chunk_size", [1, 7, 64, 65536])
def test_streaming_json_preserves_values_across_refills(monkeypatch, chunk_size):
    from decision import json_stream

    monkeypatch.setattr(json_stream, "_CHUNK_SIZE", chunk_size)
    value = {"é🙂": [None, True, False, -1, 1.2e-20, {}, [],
                     {"text": '\\\" },"content_hash": [ ] , : '},
                     {"same_key": 1}, {"same_key": 2}]}
    encoded = json.dumps(value, ensure_ascii=False)
    result = json_stream.load_json(io.StringIO(" \n" + encoded + "\t\r"))
    assert result == value
    assert next(iter(result["é🙂"][-2])) is next(iter(result["é🙂"][-1]))


@pytest.mark.parametrize("chunk_size", [7, 64, 65536])
def test_streamed_arrays_share_keys_with_surrounding_objects(monkeypatch, chunk_size):
    from decision import json_stream

    monkeypatch.setattr(json_stream, "_CHUNK_SIZE", chunk_size)
    value = {"shared_field": 0, "first": [{"shared_field": 1}],
             "second": [{"shared_field": 2}]}
    loaded = json_stream.load_json(io.StringIO(json.dumps(value)))
    assert loaded == value
    key = next(iter(loaded))
    assert next(iter(loaded["first"][0])) is key
    assert next(iter(loaded["second"][0])) is key


@pytest.mark.parametrize("chunk_size", [1, 7, 64, 65536])
def test_signed_snapshot_hashes_exact_streamed_text(monkeypatch, chunk_size):
    from decision import json_stream

    record = {"text": "é🙂\\\" },\"content\": { " * 4000,
              "values": [None, True, False, {}, [], -12, 1.25e-20]}
    raw = _snapshot(record).to_bytes(key=KEY, ed25519_signer=None)
    monkeypatch.setattr(json_stream, "_CHUNK_SIZE", chunk_size)

    def semantic_hash(*args):
        pytest.fail("canonical stream fell back to a second content serialization")

    monkeypatch.setattr(snapshot, "content_hash", semantic_hash)
    loaded = _load(raw)
    assert loaded.signature_verified
    assert loaded.record("streaming") == record


def test_json_reader_hashes_source_bytes_including_whitespace():
    from decision.json_stream import JSONStreamReader

    encoded = ' \n{"é🙂" : [1.25e-20, "\\\\\\\""], "empty": {}}\t\r'
    digest = hashlib.sha256()
    reader = JSONStreamReader(io.StringIO(encoded), digest=digest)
    assert reader.read_value() == json.loads(encoded)
    reader.finish()
    assert digest.hexdigest() == hashlib.sha256(encoded.encode()).hexdigest()


@pytest.mark.parametrize("encoded", ["null", "true", "false", "-12", "1.2e-20", '"é🙂"'])
def test_json_reader_accepts_complete_scalars_at_eof(encoded):
    from decision.json_stream import load_json

    assert load_json(io.StringIO(encoded)) == json.loads(encoded)


@pytest.mark.parametrize("encoded", [
    "", "{", '{"x":1,', '{"x":1, \n', '{"x":1,}', '{"x":1,,"y":2}',
    "[1,", "[1,]", "[1,,2]", "[1}", '{"x":"unfinished\\', "true false", "1e",
])
def test_streaming_json_rejects_incomplete_and_invalid_values(encoded):
    from decision.json_stream import load_json

    with pytest.raises(json.JSONDecodeError):
        load_json(io.StringIO(encoded))


@pytest.mark.parametrize("fragment", [b'{"x":1,', b'{"x":1, \n', b'{"x":[1,]}'])
def test_invalid_canonical_content_raises_snapshot_integrity_error(fragment):
    with pytest.raises(snapshot.SnapshotIntegrityError):
        _load(gzip.compress(b'{"content":' + fragment))


def test_streamed_provenance_tampering_is_rejected_before_indexing(monkeypatch):
    raw = _snapshot({"text": "original"}).to_bytes(key=KEY, ed25519_signer=None)
    altered = gzip.compress(gzip.decompress(raw).replace(b'"original"', b'"modified"'))

    def indexed(*args, **kwargs):
        pytest.fail("tampered content reached snapshot indexing")

    monkeypatch.setattr(snapshot, "LoadedSnapshot", indexed)
    with pytest.raises(snapshot.SnapshotIntegrityError, match="content hash"):
        _load(altered)


def test_escaped_duplicate_outer_content_is_rejected():
    raw = _snapshot({"text": "original"}).to_bytes(key=KEY, ed25519_signer=None)
    altered = gzip.decompress(raw)[:-1] + b',"\\u0063ontent":{}}'
    with pytest.raises(snapshot.SnapshotIntegrityError, match="duplicate content"):
        _load(gzip.compress(altered))


def test_duplicate_content_fields_keep_standard_json_last_value_semantics():
    raw = _snapshot({"text": "original"}).to_bytes(key=KEY, ed25519_signer=None)
    altered = gzip.decompress(raw).replace(
        b'{"content":{', b'{"content":{"records":{"obsolete":null},', 1)
    loaded = _load(gzip.compress(altered))
    assert loaded.signature_verified
    assert loaded.record("streaming") == {"text": "original"}


def test_deep_legacy_snapshot_uses_standard_decoder_without_losing_signature():
    value = 1
    for _ in range(600):
        value = {"child": value}
    loaded = _load(_snapshot({"nested": value}).to_bytes(key=KEY, ed25519_signer=None))
    assert loaded.signature_verified
    actual = loaded.record("streaming")["nested"]
    for _ in range(600):
        actual = actual["child"]
    assert actual == 1


def test_deep_fallback_still_rejects_duplicate_outer_content():
    value = 1
    for _ in range(600):
        value = {"child": value}
    raw = _snapshot({"text": "original"}).to_bytes(key=KEY, ed25519_signer=None)
    first_content = json.dumps({"nested": value}, separators=(",", ":")).encode()
    altered = b'{"content":' + first_content + b"," + gzip.decompress(raw)[1:]
    with pytest.raises(snapshot.SnapshotIntegrityError, match="duplicate content"):
        _load(gzip.compress(altered))


@pytest.mark.parametrize("encoded", ['{"x":1,', '[{"same_key":1},'])
def test_failed_json_parse_releases_reader_without_cyclic_collection(monkeypatch, encoded):
    from decision import json_stream

    readers = []
    original = json_stream.JSONStreamReader

    class TrackedReader(original):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            readers.append(weakref.ref(self))

    monkeypatch.setattr(json_stream, "JSONStreamReader", TrackedReader)
    enabled = gc.isenabled()
    gc.disable()
    try:
        try:
            json_stream.load_json(io.StringIO(encoded))
        except json.JSONDecodeError:
            pass
        assert readers and all(reader() is None for reader in readers)
    finally:
        if enabled:
            gc.enable()
