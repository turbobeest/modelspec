# MODEL-458-MEMTOOLS execution evidence

Base: `a29bf9c6d12b0ca093b42a2f662e0a53150014ca`.
AUD-10-F3: `282e72253dcb2a1448c6bdb1a64f869b86c61f47`.
AUD-10-F4: `f27c52132fdd20ab72d205db6ff0a189bec8557d`.
The round 2 evidence commit is the PR head.

Focused tests use `env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider` from this worktree. Python 3.14.4, pytest 9.1.1. No `-n`.

Bundle builds used Node 22.22.3, uv 0.12.19, Wrangler 4.139.0, and pywrangler 1.17.4 (`workers-py`). The machine `uv` is 0.7.13 and stops pywrangler, which requires uv 0.12.3 or newer. The 0.12.19 binary was used only for this build. The memory probe used Pyodide 0.28.3 and a throwaway snapshot key. Private catalogue bytes stayed in scratch.

## AUD-10-F3

The built-bundle checker follows ordinary imports inside functions, async functions, methods, and loops. `TYPE_CHECKING` imports stay out of the graph. Builder, standalone CLI, and operator scopes are excluded by the full lexical path, so a nested function of the same name stays checked. Ed25519 imports inside `load_snapshot_bytes` stay excluded. The same imports in another function are reported. Preload calls that loader with `key=None` and `public_keys={}`. A request load refuses an empty HMAC key before the call.

`tests/test_worker_bundle.py`, the tests committed before round 2, against the base checker: 10 failed, 8 passed, exit 1. The literal `import_module` test already passed.

After the change, `tests/test_worker_bundle.py` and `tests/test_worker_vendor_imports.py`: 19 passed, exit 0.

Public Wrangler dry-run, then `api/worker/bundle_check.py` on that directory: exit 0, 82 local modules reachable from `entry.py`. Private dry-run with `--require-data`: exit 0, 83 local modules. No unresolved import in either artifact.

## AUD-10-F4

The diagnostic counter walks instance dictionaries and slots after the steady-memory sample. Shared objects count once. Cycles stop. Modules, functions, and classes are not traversed. Packed array storage stays in `sys.getsizeof` and is not expanded into Python integers. The result labels the walk as `python_retained_graph_bytes`, separate from `wasm_bytes` and `steady_bytes`, and records that category sizes overlap.

`tests/test_worker_memory.py -k snapshot_attribution` before the helper change: exit 1. A fact payload counted 277 bytes, a lazy driver mapping counted 80 bytes, and a slotted cycle counted 120 bytes. A module shell counted 72. The array-storage test already passed.

After both changes, `tests/test_worker_memory.py`, `tests/test_worker_bundle.py`, and `tests/test_worker_vendor_imports.py`: 51 passed, exit 0.

Private probe, same bundle, `--limit-mib 120`:

| run | steady bytes | steady MiB | snapshot index bytes | exit |
| --- | ---: | ---: | ---: | ---: |
| corrected, current | 114277306 | 108.98 | 4825298 | 0 |
| previous helper, current, measure-only | 109744650 | 104.66 | 3261910 | 0 |
| corrected, successor | 109772298 | 104.69 | 4825369 | 0 |

The difference between the two current-bundle steady-memory rows is run-to-run variation, because the attribution step runs after the steady sample.

Provenance table bytes stayed 1565862 on the current bundle for both helpers. Vocabulary bytes stayed 640555. Wasm allocation stayed 62783488 on all three runs. The first current run warned that its noisy peak, 117988898 bytes, was above 112 MiB. That warning does not fail the probe. Steady memory stayed under 115 MiB and under the 120 MiB gate. The 120 MiB, 115 MiB, and 100 ms gates were not changed. The 100 ms gate was not measured here.

## Limits of observation

No full local suite, no public synthetic 115 MiB fixture probe, and no corpus byte compare. Hand-written Worker modules and `decision/` were not edited, so the corpus artifact is the same one CI already tests. No production request, deployment, merge, package publish, ranking floor, legal text, price, Worker var, or contract field change. Independent review of round 2 is pending.

## Round 2

Merge of `origin/main` is `aeff194d522176fffb7f0dcd9484be8139bfe363`. Focused tests on that merge, before the edits below, were 51 passed, exit 0.

The focused command, from this worktree, is `env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_worker_bundle.py tests/test_worker_memory.py tests/test_worker_vendor_imports.py`. After the round 2 edits it reports 60 passed, exit 0.

Base checker measurement, before the round 2 tests. `api/worker/bundle_check.py` was replaced with the copy from `a29bf9c6d12b0ca093b42a2f662e0a53150014ca`, the bundle test file was run, and the checker was restored. Command: `env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_worker_bundle.py`. Result: 10 failed, 8 passed, exit 1.

The signature exemption test also places `from missing_from_package import answer` and `from cryptography.hazmat.primitives import serialization` inside `load_snapshot_bytes`. Both are reported. The two exempt imports stay unreported. On the head, `tests/test_worker_bundle.py::test_ed25519_imports_stay_excluded_only_inside_load_snapshot_bytes` passed, exit 0. The same test fails, exit 1, when the exemption stops checking which dependency is imported, when it accepts any module under that package, and when the exempt set gains `cryptography.hazmat.primitives`. Each edit was reverted.

The label test evaluates the diagnostic `json.dumps` expression. It asserts kind `python_retained_graph_bytes`, an overlap flag of true, and `distinct_from` equal to `wasm_bytes`, `steady_bytes`, and `process_rss`. The sampling-order assertion remains. On the head, `tests/test_worker_memory.py::test_attribution_labels_distinguish_python_graph_bytes_from_the_gate` passed, exit 0. It fails, exit 1, when the overlap flag is false, when `wasm_bytes` is dropped, and when `steady_bytes` is dropped. Each edit was reverted.

`test_excluded_function_name_in_another_module_is_reported` reports a `main` function in `entry.py` that imports a missing package. `test_signature_exemption_does_not_apply_in_another_module` reports the signature imports when `load_snapshot_bytes` is in `entry.py`. On the head, both passed, exit 0. When the builder exclusion ignores its module, the `main` test fails and the signature test passes, exit 1. When the signature exemption ignores its module, the signature test fails and the `main` test passes, exit 1. Each edit was reverted.

`test_every_worker_snapshot_call_is_a_site_the_hmac_test_checks` walks every Python file under `api/worker/src/` except the package directories `.gitignore` omits. Vendor writes those directories beside the entry point, and CI does not have them. The calls that remain are the two sites `test_worker_snapshot_callers_stay_on_the_hmac_path` checks. On the head, that census and the HMAC caller test passed, exit 0. A temporary `decision.snapshot.load_snapshot` call added in `entry.py`, then reverted, makes the census fail, exit 1. The first CI run failed this test because it required calls inside the generated `decision/snapshot.py` copy. That requirement is removed.

`test_import_graph_reports_a_function_local_import_in_each_block` covers a `match` case, a loop `else`, a `with` body, a function nested three levels, a relative import, and a `try`/`except ImportError`. The `try`/`except ImportError` import is reported. On the unmodified checker, 6 passed, exit 0. `api/worker/bundle_check.py` did not change.

`api/worker/measure_memory.cjs` has one comment. The `process_rss` label names a quantity the output does not carry. The file's behaviour did not change.

The 120 MiB, 115 MiB, and 100 ms gates were not changed. No workflow file changed. No new test module, so `tests/shard_durations.json` did not change.
