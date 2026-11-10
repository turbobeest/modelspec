# MODEL-460-FU-A execution evidence

Base: `4b10eb58112f92f4ae94fea32f3e5e34cfc29f85` (`origin/main` at start, after `git fetch origin`).
Worktree: `/Users/terbeest/dev/worktrees/model-460-fu-a`. Branch: `model-460-fu-a`.

Item commits:

- Exempt import set: `eb109ecfb4537505d1b13980618d348bc91c736b`
- Block forms: `4e36702643aea9499a14b50b61f644284f34a557`
- Snapshot census: `cb25139f7b6431d1333bada02447c0bd1279a924`
- Relaxation pins: `bede600b626269ee52e01da8e11f11a26ef62f7b`

The evidence commit is the one that adds this file. Identify it with
`git log -1 --format=%H -- docs/evidence/MODEL-460-FU-A-fix.md`.

## Tools

Python 3.14.4, pytest 9.1.1, Git 2.50.1.
Python is `/Users/terbeest/dev/modelspec/.venv/bin/python`.
Pytest was serial, with `-q -p no:cacheprovider` and no `-n`.
Exit codes were read directly. No local full suite. No `web/` build.
No Worker memory probe.

Each temporary edit was restored before the next one. After the last restore,
`git diff --name-only -- api decision` was empty and `git status --porcelain`
showed only the two test files. Those files are the only ones in the item
commits. `tests/test_rank_worker.py`, `api/ranking/engine.py`, and
`tests/shard_durations.json` are unchanged. No floor value changed.

## F1. Integer floor guard

Not shipped. The extended guard, run on this base before any commit, flags 2
lines. Both names are `X402_VERSION`:

- `api/worker/src/x402.py:58`
- `api/worker/src/x402_facilitator.py:27`

The scan is the existing loop over `api/worker/src/*.py`. A line is flagged
when an `UPPER_CASE` name is assigned an integer literal equal to an integer
floor, and the name is not the floor's own definition. The floors are
`MIN_BENCHMARK_COVERAGE` 0.50, `WIZARD_BENCHMARK_COVERAGE` 0.25, and
`MIN_BENCHMARK_COUNT` 2. The only integer floor is 2. Quoted versions such as
`SCHEMA_VERSION = "2.0"` and `PENDING_SCHEMA_VERSION = "2"` are not integer
literals and were not flagged. No production file was edited, and no exemption
list was added. The dotted-literal guard is unchanged.

## F2. Exempt import set

`test_ed25519_imports_stay_excluded_only_inside_load_snapshot_bytes` asserts
`HMAC_ONLY_IMPORTS` equals
`{"cryptography.exceptions", "cryptography.hazmat.primitives.asymmetric.ed25519"}`.
The existing missing-import assertions in that test are unchanged.

Temporary edit in `api/worker/bundle_check.py`, then
`tests/test_worker_bundle.py::test_ed25519_imports_stay_excluded_only_inside_load_snapshot_bytes`.

- Add `cryptography.x509`: exit 1. Restore: exit 0.
- Drop `cryptography.exceptions`: exit 1. Restore: exit 0.

## F3. Snapshot census

`test_the_snapshot_census_reports_an_indirect_loader_call` reports these calls:

- `from decision.snapshot import load_snapshot_bytes as x`
- `from decide_service import load_snapshot_bytes as q`
- `getattr(module, "load_snapshot_bytes")()`
- `importlib.import_module("decision.snapshot").load_snapshot()`
- `decision.snapshot.load_built_snapshot()`

The committed Worker tree is unchanged, so
`test_every_worker_snapshot_call_is_a_site_the_hmac_test_checks` still expects
the same two sites. Each case below was a temporary edit of the census in
`tests/test_worker_bundle.py`, then that case, then a restore.

- Aliased import, `decision.snapshot`: exit 1, then exit 0.
- Aliased import, `decide_service`: exit 1, then exit 0.
- `getattr`: exit 1, then exit 0.
- `import_module`: exit 1, then exit 0.
- `load_built_snapshot`: exit 1, then exit 0.

No case was dropped. Seeing these forms did not require a change to
`api/worker/bundle_check.py`.

## F4. Block forms

`test_import_graph_reports_a_function_local_import_in_each_block` now also
covers an `except` handler, a `try` `else`, a `try` `finally`, a `while`, an
`async with`, and an `except*` handler. On the unmodified checker every new
case passed. Each case below skipped only that block in
`api/worker/bundle_check.py`, then ran that case, then restored the file.

- `except-handler`: exit 1, then exit 0.
- `try-else`: exit 1, then exit 0.
- `try-finally`: exit 1, then exit 0.
- `while`: exit 1, then exit 0.
- `async-with`: exit 1, then exit 0.
- `except-star`: exit 1, then exit 0.

No case was dropped. The checker already walks all six.

## F5. Relaxation

(a) Already pinned by `test_a_feasible_tie_prefers_the_numeric_cap`. Replacing
`for caps_wanted in range(size, -1, -1)` with `for caps_wanted in range(0, size + 1)`
in `_lazy_drops` made that test exit 1. Restore: exit 0. No new assertion was
added, and no existing assertion was changed.

(b) `test_relax_to_counts_distinct_models_when_one_model_has_two_offerings`
gives one model two offerings at price 2.0 and expects `admits == 1`.
Replacing `len({snapshot.model_of(cid) for cid in admitted})` with
`len(list(admitted))` made `admits` 2. That test exited 1. Restore: exit 0.

(c) `_draw_generated` again returns a licence gate with
`licence.commercial_use` as the requested domain. The generated comparison
counts those draws and asserts the count is greater than 0. With seed 458,
80 + 80 + 24 draws, the count was 29. Removing that branch from the draw made
the count 0 and the test exit 1 (`assert 0 > 0`). Restore: exit 0.

`tests/test_decision_relax.py` alone: 30 passed in 0.47s, exit 0.

## Focused suite

```text
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD \
  /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_rank_worker.py tests/test_worker_bundle.py tests/test_decision_relax.py
```

135 passed in 9.58s, exit 0. This was the tree that the four item commits contain.

## Not observed

The full pytest suite, both site builds, the Worker memory probe, and the
GitHub checks. Those checks are read after the push.

## Follow-ups

- F1. The integer-floor guard flags 2 existing lines, both named
  `X402_VERSION`, in `api/worker/src/x402.py` and
  `api/worker/src/x402_facilitator.py`. It was not added.
