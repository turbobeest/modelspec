# Successor handoff

Base b4a7074f, implementation authorized after design commit 008da9cc. No commits or external writes by this worker.

Runtime now authenticates the current snapshot and detached successor signature on the first request. It leaves the successor gzip and vocabulary unread until the first request at or after the successor UTC boundary. This deliberately uses the latest permitted load time, so the original price period need not coexist with the successor.

The holder and module release the current snapshot before successor parsing, proved with a weak reference collected inside the bundle-read callback. The module also clears both old vocabulary representations. All bundled export origins share the same holder. Comparison drops its initial current reference before historical I/O and reselects after that I/O. Existing body-bound response headers remain unchanged and all REV-813 billing/compare regressions pass.

The generated SNAPSHOTS descriptor includes content hash, HMAC signature, snapshot id, date bounds and exact raw gzip SHA-256. At handover the loader verifies the exact bytes, the actual signed content, and agreement with the descriptor. Failed immutable bundle loads cache only the error text and return 503 on repeated requests, without retaining exception traceback state.

Authentication scope: detached signatures authenticate before either period serves. Raw successor bytes are checked at lazy parse. Corruption introduced after descriptor generation is refused at the boundary; it does not stop the valid primary serving before then. Root reviewed and accepted this interpretation of the committed design. No production Worker or paid provider was contacted. No private memory measurement was run by this worker.

## Reproduction commands

All commands run in /Users/terbeest/dev/worktrees/model-407. Python 3.14.4, pytest 9.1.1, ruff 0.16.6.

1. Red against unchanged runtime: `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_snapshot_successor_memory.py`. Exit 1, six failures in 0.63 seconds. Full output `tmp/model-407/successor/red.txt`.
   Tests: startup does not read/parse/verify successor; successor remains unread before boundary; prior snapshot/vocabulary are released before parse; corrupt detached signature refuses primary more than 24 hours before expiry; two payload substitutions require exact gzip and authenticated content match.
2. Initial focused: `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_snapshot_successor_memory.py tests/test_snapshot_successor.py tests/test_snapshot_response_headers.py tests/test_compare_midnight_refresh.py tests/test_snapshot_successor_vendor.py`. Exit 0, 54 passed in 11.64 seconds. Full output `tmp/model-407/successor/green-initial.txt`.
3. Repeated loader error red: `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_snapshot_successor_memory.py::test_successor_load_failure_stays_a_refusal_on_following_requests`. Exit 1, one failure in 0.66 seconds. Initial 502 snapshot_unavailable was expected 503 snapshot_refused. Full output `tmp/model-407/successor/load-error-red.txt`.
4. Broader Worker suites: `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_snapshot_successor_memory.py tests/test_snapshot_successor.py tests/test_snapshot_response_headers.py tests/test_compare_midnight_refresh.py tests/test_snapshot_successor_vendor.py tests/test_decide_worker.py tests/test_decide_snapshot_refresh.py tests/test_hardware_fit_worker.py tests/test_visit_gate_off.py tests/test_policy_store_state.py tests/test_dated_price_snapshot.py`. Exit 0, 250 passed and 1 skipped in 75.41 seconds. Full output `tmp/model-407/successor/green-broader.txt`.
5. Final focused after formatting cleanup, same command as step 2. Exit 0, 55 passed in 2.63 seconds. Full output `tmp/model-407/successor/green-final.txt`.
6. `/Users/terbeest/dev/modelspec/.venv/bin/ruff check tests/test_snapshot_successor_memory.py` and `git diff --check -- api/worker/src/entry.py api/worker/src/decide_service.py api/worker/vendor.py tests/test_snapshot_successor.py tests/test_snapshot_successor_vendor.py tests/test_snapshot_successor_memory.py`. Both exit 0.

Full touched-file ruff was also run. It reports 78 predominantly pre-existing formatting/import/line-length issues. New-file import formatting and newly added long source lines were corrected. No existing tests were weakened: original successor assertions were unchanged; the shared fixture helper gained descriptor/read tracking, and the vendor test gained an exact descriptor assertion.

## Independent review correction

The hardware reviewer found that a vocabulary request paused in `_meter_catalog_read` retained the selected snapshot and parsed vocabulary while another request handed over. Added an async regression with weak references to the snapshot, the complete vocabulary dictionary and a nested facet. Both a complete vocabulary response and a full-detail facet lookup failed before the correction. At successor read, all three prior objects were still alive.

Three explicit releases now run before metering I/O. The selected snapshot reference is dropped after date/binding validation, the selected dictionary is dropped after serialization, and the complete vocabulary local is dropped before awaiting the meter. The suspended request keeps its serialized body, proved byte-identical after the concurrent handover.

Red command: `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_snapshot_successor_memory.py::test_vocabulary_metering_does_not_retain_old_snapshot_or_parsed_vocabulary`. Exit 1, two failed in 0.64 seconds. Log `tmp/model-407/successor/vocabulary-residency-red.txt`.

Green command: `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_snapshot_successor_memory.py tests/test_snapshot_successor.py tests/test_snapshot_response_headers.py tests/test_compare_midnight_refresh.py tests/test_visit_gate_off.py`. Exit 0, 63 passed in 1.89 seconds. Log `tmp/model-407/successor/vocabulary-residency-green.txt`. New test file ruff and changed-file `git diff --check` also exit 0. No commits by this worker.
