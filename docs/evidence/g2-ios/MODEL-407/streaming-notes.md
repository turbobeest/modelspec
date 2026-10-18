# Streaming loader handoff

Production files owned by successor worker:

- `decision/json_stream.py`: shared standard-library JSON reader. Containers are read incrementally; standard `JSONDecoder` decodes scalar values. The reader shares dictionary keys across the document, retains a cursor instead of repeatedly copying the unconsumed tail, and hashes consumed UTF-8 source in 4 KiB blocks at refill/finalization. Syntax errors remain `JSONDecodeError` for existing rank callers.
- `decision/snapshot.py`: canonical snapshots use the reader and hash exact stored content. Other layouts and unusually deep legacy snapshots retain the standard decoder path. Canonical duplicate outer content is still refused on the depth fallback. Writers, public content shape and format version are unchanged.
- `tests/test_snapshot_streaming.py`: 38 cases covering no whole-document gzip allocation, chunk boundaries, Unicode/escaping, exact source hash, shared key identity, EOF/scalars, invalid framing, tampering before indexing, duplicate member compatibility, deep legacy fallback and immediate failure cleanup.

The parent owns commits. The memory-probe worker owns the rank/policy caller changes and vendor source registration.

## Red and green

Before source changes:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_snapshot_streaming.py > tmp/model-407/successor/streaming-red.txt 2>&1
```

Exit 1: all initial five cases fail (whole-document gzip allocation and absent incremental reader).

After parser integration and digest batching:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_snapshot_streaming.py tests/test_decision_snapshot.py tests/test_hardware_fit_memory.py > tmp/model-407/successor/streaming-green.txt 2>&1
```

Exit 0: 149 passed in 35.91 seconds.

A final cleanup inlined cursor increments and made the scalar delimiter string constant. Its focused rerun:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_snapshot_streaming.py tests/test_decision_snapshot.py::test_a_thirty_model_snapshot_is_small_and_loads_fast > tmp/model-407/successor/streaming-perf-green.txt 2>&1
```

Exit 0: 39 passed in 1.00 seconds. Standalone best-of-five load samples were 71.64–75.68 ms against the existing 100 ms bound. New-file Ruff and `git diff --check` pass.

Independent local review found no blocking parser or signature issue. The committed regression suite covers chunk boundaries, bad hashes, gzip corruption, duplicate keys, and deep legacy snapshots. This was self-review, not the pending cross-model review.

## Public memory evidence

Pinned Node 22.22.3 and Pyodide 0.28.3, original public synthetic data; no private data were read or copied by this worker. The full shared-stream reader plus rank/policy caller variant, immediately before the cursor-call cleanup, measured:

- Warm rollover: 104.526283 MiB; 59.875 MiB WASM. `public-successor-shared-streams-warm.json`.
- Native `--successor`, exact four requests: 104.488917 MiB; 59.875 MiB WASM. `public-successor-shared-streams-cold.json`.
- Retained successor index: 3,706,510 bytes, exactly the original representation; provenance table 1,997,163 bytes; vocabulary 633,718 bytes.

Warm invocation:

```sh
MODEL407_MEMORY_MODE=warm NODE_PATH=$PWD/tmp/model-407/memory_probe/runtime/node_modules MODELSPEC_SNAPSHOT_KEY=model247-ci-fixture-key /Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --expose-gc --require ./tmp/model-407/successor/successor-probe-hook.cjs api/worker/measure_memory.cjs tmp/model-407/successor/public-bundle-stream-reader --limit-mib 115 --attribute --output tmp/model-407/successor/public-successor-shared-streams-warm.json > tmp/model-407/successor/public-successor-shared-streams-warm.log 2>&1
```

Cold invocation:

```sh
NODE_PATH=$PWD/tmp/model-407/memory_probe/runtime/node_modules MODELSPEC_SNAPSHOT_KEY=model247-ci-fixture-key /Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --expose-gc api/worker/measure_memory.cjs tmp/model-407/successor/public-bundle-stream-reader --successor --limit-mib 115 --attribute --output tmp/model-407/successor/public-successor-shared-streams-cold.json > tmp/model-407/successor/public-successor-shared-streams-cold.log 2>&1
```

Both exit 0. Warm assertions prove predecessor destruction before successor bytes are read, one successor load, HMAC verification, and holder/body/header binding, without added GC. The parent runs the final private-bundle matrix against final source.
