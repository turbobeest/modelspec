# MODEL-468-F absent cache copy

Branch `model-468-f`. Base `b2a1f6404f7b43b9d6c75b81756e722f188f6765`. Implementation commits, oldest first:

- `a22f440872072f5c3b27c215c0799711b9bdc1da` skip a copy this cache never fetched
- `5aab091a9dcacc75200e2f2cd264774622bfa6ba` a failed fetch on that cache stays unreachable
- `6f83bca4d15504b5d58322a9b050c3bdde5f109c` empty cache and completeness regression
- `2da8db8406504e53bcff52d2c602a70f2e185b19` process job timeout 30 minutes
- `67d192e8130d6fe3c43f529e844d74546203a5b0` `skipped_no_copy` count

This file was added in `a33a70d8bcc3ac1cb420378e07823c3f7066af3a`. The corrupt-copy distinction is `55c618eea2ab4a05f6f26ac1da1dda0d7bd5229f`.

Python 3.14.4 and pytest 9.1.1, from `/Users/terbeest/dev/modelspec/.venv`. Focused pytest was serial, with no `-n` and no cache provider. Exit codes were read directly. No live network.

## Absent copy is skipped

`CopyStore` did not record a failed fetch, so a missing file and a failed fetch were the same `unreachable`. A fetch failure now writes an empty file under the cache root, named by the hash of the source id. The file stores no URL and no error text. `recheck` writes it only when the fetch outcome is not `ok`. Rendered sources that are not fetched, and the grace period (`DEFAULT_GRACE` is 3), are unchanged.

`StoredRegions.miss_reason` returns `no_copy` when the source and region are registered, the copy is absent, no citation record is present, and no failure marker exists. Anything else that makes `text` return `None` stays `unreachable`. A regions object with only `text` stays `unreachable`.

The skip reason is `no retained copy in this cache: <source>#<region>`. `run` already leaves a skipped claim queued and unlogged.

## Red, then green

Command, against the unchanged tree, after the new expectations were written:

`env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_verify.py::test_an_empty_cache_skips_claims_and_leaves_them_queued tests/test_decision_verify.py::test_a_retained_copy_that_matches_is_verified tests/test_decision_verify.py::test_a_fetch_that_failed_in_this_run_is_unreachable_and_logged tests/test_decision_verify.py::test_every_seeded_claim_ends_as_expected tests/test_decision_verify.py::test_a_second_run_has_nothing_left_to_do tests/test_decision_snapshot.py::test_an_absent_copy_does_not_quarantine_a_verified_fact`

Exit 1. Five failed, one passed, 0.96s.

- `test_an_empty_cache_skips_claims_and_leaves_them_queued`: both claims were `unreachable` and carried a `Verification`. The test required `skipped` and no verification.
- `test_every_seeded_claim_ends_as_expected`: `sol-copy-missing` was `unreachable` (`unreachable:seeded-missing#results`). The fixture now requires `skipped`.
- `test_a_second_run_has_nothing_left_to_do`: the second run's pending ids were `orion-absent` and `sol-prose-no-extractor`. `sol-copy-missing` had been logged, so it was not still pending.
- `test_an_absent_copy_does_not_quarantine_a_verified_fact`: `CompletenessError`, `model.context_window` quarantined (`unreachable`).
- `test_a_fetch_that_failed_in_this_run_is_unreachable_and_logged`: `AttributeError`, `CopyStore` had no `fetch_failed`.
- `test_a_retained_copy_that_matches_is_verified` passed on the unchanged code.

With the skip in place and the failure marker not yet written, the same failed-fetch path returned `skipped`, reason `no retained copy in this cache: seeded-missing#results`, appended nothing, and left the claim pending. `test_a_fetch_that_failed_in_this_run_is_unreachable_and_logged` then failed at `assert store.fetch_failed("seeded-missing")` (`False`). After `recheck` records the marker, that test passes: outcome `unreachable`, one log row, claim not pending, `consecutive_failures` 1, not quarantined.

## Green

`env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_verify.py tests/test_decision_snapshot.py::test_an_absent_copy_does_not_quarantine_a_verified_fact tests/test_release_signals.py::test_the_process_job_cannot_open_issues tests/test_accuracy.py::test_a_plain_http_source_403_is_still_unreachable tests/test_accuracy.py::test_a_403_on_a_rendered_source_beside_a_failed_http_source_stays_unreachable tests/test_accuracy.py::test_fidelity_fails_when_render_required_draws_exceed_the_undetermined_share`

Exit 0. 456 passed in 2.15s.

`verify --json` counts include `skipped_no_copy`. Outcome stays `skipped`. A changed-only run with no claims reports `skipped_no_copy` 0.

The release-signals process job `timeout-minutes` is 30. `test_the_process_job_cannot_open_issues` pins it.

## CI follow-up

Pull request 1057, workflow run 43244932426. Pytest shard 6/8 and shard 8/8 failed, and the `Run pytest` check failed because those shards failed. Three tests got `skipped` where they required `unreachable`: a corrupt copy, a deleted xAI page copy, and a deleted architecture config copy.

A file at the copy path whose bytes do not hash to the ref is a retained copy that cannot be read. `miss_reason` returns `unreachable` when that path exists. A path that does not exist, with no failure marker, stays `no_copy`.

The corrupt-copy case stays `unreachable`, reason `unreachable:pricing#page`, with a verification. The two deleted-copy cases are `skipped`, with no verification. Their reasons are `no retained copy in this cache: pricing#page` and `no retained copy in this cache: config#page`.

`env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_xai_matrix_reader.py tests/test_architecture_extractors.py`

Exit 0. 501 passed in 0.94s. Same Python 3.14.4 and pytest 9.1.1.

## Not observed

No full pytest suite locally, and no site build in this note. No live fetch. No Worker deploy, no Linear write, and no merge. The follow-up pull-request checks after the corrupt-copy commit had not been observed when this note was added.
