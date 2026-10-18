#!/usr/bin/env python3
"""Public differential checks against the production buffered JSON reader."""
import gc
import hashlib
import io
import json
from pathlib import Path
import random
import subprocess
import sys
import weakref

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from decision import json_stream as reader

source_sha256 = hashlib.sha256(Path(reader.__file__).read_bytes()).hexdigest()
source_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
rng = random.Random(407820)


def value(depth=0):
    leaves = [None, True, False, -12, 1.2e-20, "é🙂", '\\\" },"content_hash": [ ] , : ']
    if depth >= 4 or rng.random() < .4:
        return rng.choice(leaves)
    if rng.random() < .6:
        return [value(depth + 1) for _ in range(rng.randrange(6))]
    return {rng.choice(["same_key", "é🙂", "text", "rows", "values"]): value(depth + 1)
            for _ in range(rng.randrange(6))}


cases = [json.dumps(value(), ensure_ascii=False) for _ in range(1000)]
cases.extend([
    '[{"same_key": 1, "same_key": 2}]',
    '[{"same_key": 1, "\\u0073ame_key": 2}]',
    '{"same_key":0,"array":[{"same_key":1},{"same_key":2}],"last":{"same_key":3}}',
    '[{"same_key": 1}, {"same_key": 2}, "' + 'é🙂' * 40000 + '"]',
    '[{"same_key": 1}, {"same_key": 2}, ',
    '[{"same_key": 1}, {"same_key": 2}] true',
    '{"array":[1,2,3]x}', '{"array":[1,2,3],}', '[1,2,3]]',
    '[NaN,Infinity,-Infinity]',
])
for encoded in cases[:1000]:
    if len(encoded) > 1:
        where = rng.randrange(len(encoded))
        cases.extend([encoded[:where], encoded[:where] + ',' + encoded[where:],
                      encoded[:where] + encoded[where + 1:]])
checks = 0
for chunk in [1, 7, 64, 65536]:
    reader._CHUNK_SIZE = chunk
    for encoded in cases:
        try:
            expected = json.loads(encoded)
        except (ValueError, RecursionError):
            try:
                reader.load_json(io.StringIO(encoded))
            except (ValueError, RecursionError):
                pass
            else:
                raise AssertionError(("unexpected acceptance", chunk, repr(encoded)))
        else:
            digest = hashlib.sha256()
            parsed = reader.JSONStreamReader(io.StringIO(encoded), digest=digest)
            actual = parsed.read_value()
            parsed.finish()
            assert json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True), (chunk, repr(encoded))
            assert digest.hexdigest() == hashlib.sha256(encoded.encode()).hexdigest(), (chunk, repr(encoded))
        checks += 1

# All three paths share key identities: surrounding streamed object, fully buffered
# array, and array whose first attempted decode fails after complete dictionaries.
key_identity_cases = 0
for chunk in [7, 64, 65536]:
    reader._CHUNK_SIZE = chunk
    encoded = '{"same_key":0,"array":[{"same_key":1},{"same_key":2},"' + 'x' * (chunk + 1) + '"],"last":{"same_key":3}}'
    parsed = reader.load_json(io.StringIO(encoded))
    key = next(iter(parsed))
    assert next(iter(parsed["array"][0])) is key
    assert next(iter(parsed["array"][1])) is key
    assert next(iter(parsed["last"])) is key
    key_identity_cases += 1

# The hook must not capture the reader and make it depend on cyclic collection.
reader._CHUNK_SIZE = 64
refs = []
original = reader.JSONStreamReader
class TrackedReader(original):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        refs.append(weakref.ref(self))
reader.JSONStreamReader = TrackedReader
enabled = gc.isenabled()
gc.disable()
try:
    for encoded in ['[{"same_key":1}]', '[{"same_key":1},',
                    '[{"same_key":1},"' + 'x' * 200 + '"]',
                    '[{"same_key":1},"' + 'x' * 200]:
        try:
            result = reader.load_json(io.StringIO(encoded))
        except json.JSONDecodeError:
            pass
        else:
            del result
        assert refs[-1]() is None
finally:
    if enabled:
        gc.enable()
print(json.dumps({"source_head": source_head, "source_sha256": source_sha256,
                  "differential_and_exact_hash_cases": checks,
                  "key_identity_cases": key_identity_cases,
                  "gc_disabled_lifetime_cases": len(refs), "passed": True}))
