# MODEL-407 hardware-fit implementation evidence

Production code before the changes was `b4a7074f`. Root committed the design at
`008da9cc` before these tests and changes. Python was 3.14.4 from
`/Users/terbeest/dev/modelspec/.venv/bin/python`.

The initial tests ran against unchanged production code. Three failed and five
passed in 0.69s, exit 1, in `red.log`:

- `test_hardware_fit_snapshot_retains_source_ids_and_one_copy_of_each_record`
  found the eager duplicate `hardware_fit_records` payload.
- `test_hardware_fit_fields_do_not_pad_every_other_provenance_record` found that
  one hardware workload changed the general provenance table's fields and rows.
- `test_hardware_fit_loads_records_once_on_first_assessment` observed zero lazy
  workload decodes because the workload was already parsed eagerly.

The four new endpoint golden tests and legacy round trip already passed before
the production change. The fixtures were captured before editing
`decision/snapshot.py`, from `assess(snapshot=fixture_snapshot(...))` for
measured, full, lower-bound, and undetermined cases. Capture used the Worker's
`json.dumps(body, indent=2, default=str)`, with only `snapshot` replaced by
`snap_golden_hardware_fit_2_0`. See the committed fixture README.

Commands and direct results:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_hardware_fit_memory.py
# Before production changes: 3 failed, 5 passed in 0.69s; exit 1.

PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python mcp/test/fixtures/generate-hardware-fit.py
# Exit 0. Generated diff changes exactly two content-addressed snapshot IDs.

PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_hardware_fit_memory.py tests/test_hardware_fit.py tests/test_hardware_fit_worker.py tests/test_decision_snapshot.py
# Final focused run: 208 passed in 38.65s; exit 0. Full output in green.log.

git diff --check
# Exit 0.

/Users/terbeest/dev/modelspec/.venv/bin/python --version
# Python 3.14.4; exit 0.
```

Implementation stores hardware workload and numeric input provenance in the
separate signed `hardware_fit_record_table`, using the existing canonical JSON
value pool. The new `hardware_fit_record_ids` contains only workload IDs. The
loader decodes those records through `record()` at the first assessment and
reuses the same cached records. Legacy eager snapshots remain readable.

The tiny public test fixture's shared table had 41 fields, 7 rows, and 287
slots. The new general table has 27 fields, 3 rows, and 81 slots; the separate
hardware table has 30 fields, 4 rows, and 120 slots. Every general record avoids
14 unused hardware columns. The tiny fixture adds metadata overhead in JSON
bytes, 4,263 versus 4,001; savings depend on the much larger general catalogue.
These figures are in `storage-attribution.json`, calculated by unpacking both
new tables and repacking them together with the unchanged `_pack_records`.

No API contract, decision/ranking code, production data, or switches changed.
No Worker deployment or paid-provider calls were made. These CPython tests do
not establish Pyodide steady memory; root owns that measured acceptance gate.
