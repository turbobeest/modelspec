# MODEL-460-FU-E execution evidence

Base: `2a97ff2424774381815b86bea964a44e3e55a301` (`origin/main` after `git fetch origin`).
The worktree had been created at `53d4c94457b8403168cc05a2935d4b3b255ab97f`.
That commit was one behind `origin/main`, so the branch was fast-forwarded before any test.

Worktree: `/Users/terbeest/dev/worktrees/model-460-fu-e`. Branch: `model-460-fu-e`.

Item commits:

- Architecture export sentence: `62e6686cfa5349236d5ef9f932ee9e3aba0a55aa`
- Signal credential order: `cba1f93efbd392dc2706726188de4b5d06d8c256`
- Benchmark validator findings: `fdd7591809ea4c3b1851a155369c53f7943f65d3`
- Budget lock: `c76e4f599e0c5e95bed501cf9fe6cd5fdb64950d`

The evidence commit is the one that adds this file. Identify it with
`git log -1 --format=%H -- docs/evidence/MODEL-460-FU-E-fix.md`.

## Tools

Python 3.14.4, pytest 9.1.1, Git 2.50.1.
Python is `/Users/terbeest/dev/modelspec/.venv/bin/python`.
Every pytest command set `PYTHONDONTWRITEBYTECODE=1` and `PYTHONPATH=$PWD`,
and used `-q -p no:cacheprovider`. No `-n`. Exit codes were read directly.
No local full suite. No `web/` build.

## E1. Architecture export sentence

The Architecture Sites bullet now lists `build.json`, `rank/profiles.json`,
`rank/class-fit.json`, and the feedback schema as files `/api` keeps when
`DATA_SPLIT_ENABLED` is on. The following sentence already names `coverage.json`,
the retained snapshot files, and the allowlist `KEEP_API` plus
`is_retained_snapshot`. Binding rules are unchanged.

Command, before the wording change:

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_reference_agent_entry.py::test_agent_entry_documents_public_export_exceptions
```

Exit 1. `test_agent_entry_documents_public_export_exceptions` found ` keeps only ` on the Sites line.

The same file after the wording change: 2 passed, exit 0.

## E2. Signal credential order

Intake rejects a signature header other than `sha256=` plus 64 lowercase hex digits before it reads the body. Discovery and acknowledgement reject a missing or failed bearer before they read the body. A signature header that already has that shape is still checked against the body bytes. Acknowledgement JSON is parsed after the bearer check. With a valid bearer, nested acknowledgement JSON is still 400 `invalid_request`.

Commands, before the order change, selecting:

- `test_unauthenticated_signal_routes_do_not_read_the_body`
- `test_nested_acknowledgement_without_a_bearer_returns_401`
- `test_valid_bearer_keeps_nested_acknowledgement_invalid`
- `test_a_well_formed_signature_is_checked_against_the_body`

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_signals.py::test_unauthenticated_signal_routes_do_not_read_the_body tests/test_release_signals.py::test_nested_acknowledgement_without_a_bearer_returns_401 tests/test_release_signals.py::test_nested_acknowledgement_with_a_valid_bearer_is_still_invalid_request tests/test_release_signals.py::test_a_well_formed_signature_is_checked_against_the_body
```

Exit 1. 11 failed, 2 passed. Nine failures were a body read count of 1. Two unsigned oversized intake cases returned 413. The two passes were the valid-bearer nested acknowledgement (400 `invalid_request`) and a well-formed signature checked after the read (401 `invalid_signal`).

The same four tests after the order change, with the valid-bearer test named `test_valid_bearer_keeps_nested_acknowledgement_invalid`: 14 passed, exit 0. `test_nested_acknowledgement_json_returns_client_error` passed in that run.

`git diff` of `api/worker/src/entry.py` against the base has no import hunk. No export, snapshot, or rank file is in the diff. The Worker memory probe was not run. `SIGNALS_ENABLED` and the other Worker vars are unchanged.

## E3. Both benchmark key findings

`check()` returns duplicate-key findings and unknown-key findings together, duplicates first, and returns that list before the later schema checks. A page with one of those defects still returns that one group.

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_benchmark_validation.py::test_benchmark_validator_reports_duplicate_and_unknown_keys
```

Before the change, exit 1. `check()` returned only `duplicate_yaml_key: line 10, column 1`.

After the change, that test plus `test_benchmark_validator_reports_duplicate_aliases` and `test_benchmark_validator_rejects_unknown_nested_key`: 6 passed, exit 0. `tests/test_benchmark_validation.py`: 19 passed, exit 0.

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_public_diagnostic_counts.py
```

3 passed, exit 0. `tests/fixtures/public_diagnostic_counts.json` is unchanged.

## E4. Shared judge allowance

`Budget.reserve` holds one lock across the allowance check and the `reserved` update. `judge_evidence` holds that lock for the `spent` update. `reserve(self, amount)` still returns `None`.

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_attribution.py::test_shared_reserve_admits_only_as_many_callers_as_the_allowance
```

Eight threads share one budget that admits three reservations of the same amount. They leave a start barrier together and call `reserve`. The test subclasses `Budget` and calls the inherited method. It replaces the `max` lookup that method already uses. The replacement calls `time.sleep(0)`, then waits on a second barrier. No production hook was added.

Before the lock, exit 1. All 8 calls reserved.

After the lock, that test plus `test_input_allowance_refuses_request_before_transport`, `test_input_allowance_reserves_each_transport_attempt`, and `test_spent_budget_stops_calls_and_leaves_creators_null`: 5 passed, exit 0. `tests/test_attribution.py`: 78 passed, exit 0.

No network call and no vendor call.

## Focused suite

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_signals.py tests/test_benchmark_validation.py tests/test_public_diagnostic_counts.py tests/test_attribution.py tests/test_reference_agent_entry.py
```

248 passed in 12.96s, exit 0.

## Follow-ups

`scripts/curation/draft.py` stays as it is for pre-existing unknown-key pages. It ships with the data repo's curation pin and is tracked on MODEL-458.

Unregistered-hardware-URL notices stay as they are. They are pre-existing.

## Not observed

No local full pytest suite. No site build. No Worker memory probe. CI results are outside this file.
