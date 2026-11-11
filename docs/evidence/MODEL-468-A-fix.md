# MODEL-468-A execution evidence

Base `18c7c31902cc745c076220890f5891cbdf935559`.
Worktree `/Users/terbeest/dev/worktrees/model-468-a`, branch `model-468-a`.

The evidence commit is the one that adds this file. Read it with `git log -1 --format=%H -- docs/evidence/MODEL-468-A-fix.md`.

Item commits:

- Page extraction skips a serialised `.$<id>.<digits>:$` record. `a4667bcff09c283421286a30f841e95a06f199bc`
- The live run applies each source's `max_new` cap. `0cdb822de222279aba923ece84be7129372ee1d5`
- The run report counts filed ids whose `created` time is missing. This commit.

## Tools

Python 3.14.4 and pytest 9.1.1 from `/Users/terbeest/dev/modelspec/.venv/bin/python`. Ruff 0.16.6. Git 2.50.1.

Focused pytest was serial, with `-q -p no:cacheprovider` and no `-n`. Exit codes were read directly. No local full suite. No site build. No network fetch.

`registry/release-watch.yaml` is unchanged. OpenRouter stays at `max_new` 15. Every other source keeps the default of 10.

## R1, serialised page ids

Command, before the extraction change:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_watch.py::test_page_extraction_skips_serialised_ids_and_keeps_listed_ones
```

Exit 1. 1 failed in 0.56s. `test_page_extraction_skips_serialised_ids_and_keeps_listed_ones` found an extra id, `claude-opus-4-20250514.1`, taken from `.$claude-opus-4-20250514.1:$`.

The same command after the change exited 0. 1 passed in 0.41s.

The focused files then exited 0. 231 passed in 61.09s.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_watch.py tests/test_release_watch_filter.py tests/test_release_watch_precision.py tests/test_release_watch_triage.py
```

A match immediately preceded by `.$` is skipped. A match followed by `.<digits>:$` is skipped. The id pattern can absorb a trailing `.<digits>`, so a match that ends in `.<digits>` and is followed by `:$` is treated as that same suffix and skipped. A bare id on the page is kept. `claude-opus-5.5` is kept, and `signal_id` still matches `claude-opus-5-5`. A prose id that really ends in `.1` is kept.

## R2, per-source cap

Commands, before the cap change:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_watch.py::test_a_source_at_its_default_cap_files_every_new_id tests/test_release_watch.py::test_one_new_id_over_the_cap_files_nothing_and_reports_burst tests/test_release_watch.py::test_public_source_detection_retains_observations_before_catalogue_filtering
```

Exit 1. 2 failed, 1 passed in 0.45s.

`test_a_source_at_its_default_cap_files_every_new_id` passed. `test_one_new_id_over_the_cap_files_nothing_and_reports_burst` got exit 0 and 11 discoveries. `test_public_source_detection_retains_observations_before_catalogue_filtering` got status `ok` from a source with `max_new` 0.

The same three tests, plus `test_a_burst_of_new_ids_is_held_for_a_person`, after the change exited 0. 4 passed in 0.44s.

The focused files then exited 0. 233 passed in 52.15s.

The live command calls `run_all` with no catalogue predicate. The cap used to run only when that predicate was present. It now runs for every source. At the default cap of 10 the source files every new id. One over that cap marks the source `burst`, files nothing from that run, and the report detail starts with the count. An already-carded id that is absent from the baseline is still a rejected observation when the source stays within its cap.

## R3, missing created time

Command, before the report field:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_watch.py::test_run_report_counts_filed_ids_whose_created_is_missing
```

Exit 1. 1 failed in 0.48s. `KeyError: 'missing_created'`. The assertions before that line passed: an old timestamp was left out, and a row with no `created` time was still filed.

After the field existed, the same test was extended so a carded id with no `created` time is not counted. That assertion exited 1. The page count was 1 and the expected count was 0.

The same command after counting only filed ids exited 0. 1 passed in 0.44s.

The focused files then exited 0. 234 passed in 53.57s.

Each source row has `missing_created`. The count is the ids that source filed with `created` missing. A burst counts 0. An id rejected as already carded counts 0. The summary names each source whose count is above 0. The date filter is unchanged.

## Not observed

No live page fetch. No full local suite. No site build. CI was not checked in this file. `ruff check` on the touched Python files still reports line-length and import findings that were already present on those files. The new lines are within the 100 character limit.
