# MODEL-460 FU-F execution evidence

Base: `7451e880e1d1ae64b20a4ad62515647e569de6be` (`origin/main` at start, after `git fetch origin`).
Worktree: `/Users/terbeest/dev/worktrees/model-460-fu-f`. Branch: `model-460-fu-f`.

Item commits:

- Bare and aliased unsigned-loader calls: `8b269b6da5844c94a20e00af3cef0f95bb5a4d64`
- Repo-root `decision/snapshot.py` walk: `4a1ffc63515fcc7bf6d3ea186b1d0263066d6f5f`
- Exact module identity: `e9a64673c0480aeea11cc2f4ffe6d5bad55ca814`
- `if` else, depth four, and submodule `from` import: `39455e69538425fc16b92955088161d52fcf29ff`

The evidence commit is the one that adds this file. Identify it with
`git log -1 --format=%H -- docs/evidence/MODEL-460-FU-F-fix.md`.

## Tools

Python 3.14.4, pytest 9.1.1, Git 2.50.1.
Python is `/Users/terbeest/dev/modelspec/.venv/bin/python`.
Pytest was serial, with `-q -p no:cacheprovider` and no `-n`.
Exit codes were read directly. No local full suite. No `web/` build.
No Worker memory probe.

Each temporary edit was restored before the next one. After the last restore,
`git diff -- api/worker/bundle_check.py decision/snapshot.py` was empty.
The item commits change only `tests/test_worker_bundle.py`.
`tests/shard_durations.json` is unchanged. No production file changed.
Before these commits the file had 38 passed. After them it has 45 passed.

The focused command, with a node id appended when a section names one test:

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD \
  /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_worker_bundle.py
```

## F6. Unsigned-loader census

The census reports a bare `load_built_snapshot()` call after
`from decision.snapshot import load_built_snapshot`, and a call through
`from decision.snapshot import load_built_snapshot as y`.
`from decide_service import load_snapshot_bytes as q` then `q()` stays the
existing case `aliased-import-other-module`. No second copy was added.

`test_the_snapshot_census_reports_an_indirect_loader_call` on the unmodified
census: 7 passed, exit 0.

Each line below is that same command. The census edit was in
`tests/test_worker_bundle.py` and was restored before the next line.

- Return no site for a bare name `load_built_snapshot`: `unsigned-loader-bare` failed, 6 passed, exit 1.
- Do not bind an aliased `load_built_snapshot`: `unsigned-loader-alias` failed, 6 passed, exit 1.
- Do not bind `load_snapshot_bytes` imported from `decide_service`: `aliased-import-other-module` failed, 6 passed, exit 1.
- Census restored: 7 passed, exit 0.

## F7. Repo-root decision/snapshot.py

`_worker_snapshot_call_sites` parses repo-root `decision/snapshot.py` as well
as `api/worker/src/`. The generated-package skip still applies only under
`api/worker/src/`.

`test_every_worker_snapshot_call_is_a_site_the_hmac_test_checks` requires
exactly these sites:

- `decide_service.py`, function `load_snapshot`, call `load_snapshot_bytes`
- `decision/snapshot.py`, function `load_built_snapshot`, call `load_snapshot_bytes`
- `decision/snapshot.py`, function `load_snapshot`, call `load_snapshot_bytes`
- `entry.py`, module scope, call `load_snapshot_bytes`

The two worker rows are the rows the test already required. On the unmodified
tree: 1 passed, exit 0.

A temporary `load_snapshot_bytes(b"")` at the end of `decision/snapshot.py`
made the census report `decision/snapshot.py` at module scope. The same test
failed, exit 1. The line was removed. The test then passed, exit 0, and
`git diff -- decision/snapshot.py` was empty.

## F8. Exact module identity

`test_signature_exemption_does_not_follow_a_module_suffix` defines
`load_snapshot_bytes` in module `other.snapshot`. Both
`cryptography.exceptions` and
`cryptography.hazmat.primitives.asymmetric.ed25519` must be reported as
imported by `other.snapshot`.

`test_builder_exclusion_does_not_follow_the_top_level_package` defines
`collect_repo` in module `decision.other`. `missing_runtime_package` must be
reported as imported by `decision.other`.

On the unmodified checker both tests passed, exit 0. Each edit below was in
`api/worker/bundle_check.py` and was restored before the next one. The command
was the focused command with both test node ids.

- Exemption predicate `module.endswith("snapshot")`: the suffix test failed, the package test passed, exit 1.
- Exclusion matched on the top-level package of the module: the package test failed, the suffix test passed, exit 1.
- Checker restored: 2 passed, exit 0. `git diff -- api/worker/bundle_check.py` was empty.

## F9. If else, depth four, and a present submodule

`test_import_graph_reports_a_function_local_import_in_each_block` also
requires an import in the `else` branch of an `if` inside a function
(`if-else`) and an import nested four functions deep (`four-levels`).

`test_from_import_reaches_a_present_submodule` uses `from repo import engine`
where `repo/engine.py` imports `missing_runtime_package`. The missing import
must be reported from `repo.engine`, and the visited set must be `entry`,
`repo`, and `repo.engine`.

On the unmodified checker those tests passed: 15 passed, exit 0. No case was
dropped. The checker already walks all three forms. Each edit below was in
`api/worker/bundle_check.py` and was restored before the next one.

- Skip the `else` of an `if` other than `TYPE_CHECKING`. Command: the block test, the from-import test, and `test_annotation_only_import_inside_a_function_is_not_a_bundle_dependency`. Result: `if-else` failed, 15 passed, exit 1.
- Skip function and class bodies once the scope length reaches 4. Command: the block test and the from-import test. Result: `four-levels` failed, 14 passed, exit 1. `three-levels` passed.
- Do not follow an absolute `from pkg import submodule` into a submodule that is present in the bundle. Command: the from-import test, `test_import_graph_walks_relative_imports_from_package_initializers`, and the block test. Result: `test_from_import_reaches_a_present_submodule` failed, 15 passed, exit 1.
- Checker restored. `git diff -- api/worker/bundle_check.py` was empty.

## Focused suite

The command above, with no node id, on the tree the four item commits contain:
45 passed in 1.24s, exit 0.

## Not observed

The full pytest suite, both site builds, the Worker memory probe, and the
GitHub checks. Those checks are read after the push.

## Follow-ups

None. F6, F7, F8, and F9 are pinned. No case was dropped.
