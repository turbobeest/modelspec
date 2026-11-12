# MODEL-468-A execution evidence

Base `101a9eede9eed21fc7ed14ccaa50c0b3a4e4ead5`, the `origin/main` commit merged into this branch.
Branch `model-468-a`. The head is the commit that last updates this file. Read it with `git log -1 --format=%H -- docs/evidence/MODEL-468-A-fix.md`.

Review commits:

- Drop the live-run cap. `ad50095df8bc1bd71e4869fedb9d06e2df64e148`
- Unwrap serialised page ids. `9bb62d6c5940ffb9abc74eb320e1ae875a18a0e3`
- Limit the missing-created summary line. This commit.

## Tools

Python 3.14.4, pytest 9.1.1, Ruff 0.16.6, Git 2.50.1.

Focused pytest was serial, with `-q -p no:cacheprovider` and no `-n`. Exit codes were read directly. No local full suite. No site build. No network fetch.

## What the pull request does

Page extraction keeps the id from a flight key `.$<id>.<digits>:`, with that trailing `.<digits>` removed. `.$claude-opus-5.5.1:` yields `claude-opus-5.5`. `.$claude-opus-4-20250514.1:$x` yields `claude-opus-4-20250514`. Any other match immediately preceded by `$` is dropped. The string `".0:$claude-opus-4-8.1"` yields nothing. A match with no preceding `$` is kept as matched. `gpt-6.1:$2.50` yields `gpt-6.1`, and `deepseek-v5.2:$1` yields `deepseek-v5.2`. Prose keeps a bare id, `claude-opus-5.5`, `claude-opus-5.1`, `claude-sonnet-4-5.1`, `claude-sonnet-5.5`, and `gpt-7.1`.

The live command calls `run_all` with no catalogue predicate. The per-source cap runs only when that predicate is present. `test_public_source_detection_retains_observations_before_catalogue_filtering` matches `origin/main`. An id is new when it is absent from the committed baseline. That baseline is a frozen path, and `release-watch.yml` has `contents: read`. The sink de-duplicates.

Each source row has `missing_created` and `kind`. The count is the ids that source filed with `created` missing. A burst counts 0. An id rejected before filing counts 0. The summary line names a source when the count is above zero and `kind` is `openrouter` or `huggingface`. A page row keeps its count and stays off the line. A zero count stays off the line. The date filter is unchanged.

## D1, live-run cap

Command, with the restored assertion and the cap still applied on every source:

```bash
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider tests/test_release_watch.py::test_public_source_detection_retains_observations_before_catalogue_filtering
```

Exit 1. 1 failed in 0.78s. The source status was `burst` where the test requires `ok`.

After the cap again required a catalogue predicate, that test and `test_a_burst_of_new_ids_is_held_for_a_person` exited 0. 2 passed in 0.43s.

## D2, unwrap

Command, before the extraction change:

```bash
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider tests/test_release_watch.py::test_page_extraction_unwraps_serialised_ids_and_keeps_prose
```

Exit 1. 1 failed in 0.44s. `.$claude-opus-5.5.1:` yielded no ids. The test requires `claude-opus-5.5`.

The same command after the change exited 0. 1 passed in 0.43s.

## D3, summary line

Command, before the summary change. The JSON counts were already `[1, 1]`.

```bash
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider tests/test_release_watch.py::test_run_report_counts_filed_ids_whose_created_is_missing
```

Exit 1. 1 failed in 0.42s. The summary contained `` `page` 1 ``.

The same command after the change exited 0. 1 passed in 0.38s.

## Focused suite

```bash
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider tests/test_release_watch.py tests/test_release_watch_filter.py tests/test_release_watch_precision.py tests/test_release_watch_triage.py
```

Exit 0. 232 passed in 50.40s.

## Not observed

No live page fetch. No full local suite. No site build. CI is checked after the push and is not copied into this file. `ruff check` on the touched Python files still reports line-length and import findings that were already present on those files. The new lines are within the 100 character limit.
