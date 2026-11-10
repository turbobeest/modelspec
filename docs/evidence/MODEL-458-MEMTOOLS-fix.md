# MODEL-458-MEMTOOLS execution evidence

Base: `a29bf9c6d12b0ca093b42a2f662e0a53150014ca`.
AUD-10-F3: `282e72253dcb2a1448c6bdb1a64f869b86c61f47`.
AUD-10-F4: `f27c52132fdd20ab72d205db6ff0a189bec8557d`.
The evidence commit is the PR head.

Focused tests use `env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider` from this worktree. Python 3.14.4, pytest 9.1.1. No `-n`.

Bundle builds used Node 22.22.3, uv 0.12.19, Wrangler 4.139.0, and pywrangler 1.17.4 (`workers-py`). The machine `uv` is 0.7.13 and stops pywrangler, which requires uv 0.12.3 or newer. The 0.12.19 binary was used only for this build. The memory probe used Pyodide 0.28.3 and a throwaway snapshot key. Private catalogue bytes stayed in scratch.

## AUD-10-F3

The built-bundle checker follows ordinary imports inside functions, async functions, methods, and loops. `TYPE_CHECKING` imports stay out of the graph. Builder, standalone CLI, and operator scopes are excluded by the full lexical path, so a nested function of the same name stays checked. Ed25519 imports inside `load_snapshot_bytes` stay excluded. The same imports in another function are reported. Preload calls that loader with `key=None` and `public_keys={}`. A request load refuses an empty HMAC key before the call.

`tests/test_worker_bundle.py` before the checker change: 11 failed, 7 passed, exit 1. Ten failures were a function-local import the checker did not report. One failure was a new caller test that treated the loader docstring as its first statement. That assertion was corrected to skip the docstring. The literal `import_module` test already passed.

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

Provenance table bytes stayed 1565862 on the current bundle for both helpers. Vocabulary bytes stayed 640555. Wasm allocation stayed 62783488 on all three runs. The first current run warned that its noisy peak, 117988898 bytes, was above 112 MiB. That warning does not fail the probe. Steady memory stayed under 115 MiB and under the 120 MiB gate. The 120 MiB, 115 MiB, and 100 ms gates were not changed. The 100 ms gate was not measured here.

## Limits of observation

No full local suite, no public synthetic 115 MiB fixture probe, and no corpus byte compare. Hand-written Worker modules and `decision/` were not edited, so the corpus artifact is the same one CI already tests. No production request, deployment, merge, package publish, ranking floor, legal text, price, Worker var, or contract field change. CI and independent review are pending.
