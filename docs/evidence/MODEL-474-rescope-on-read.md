# MODEL-474 rescope on read

Processing a signal reads one repository object, `https://huggingface.co/api/models/<org>/<repo>`, for a first-seen model repository on a Hugging Face organisation registered for its lab. That is the per-repository object, not the watcher's organisation listing. `hub_metadata` parses both. The read calls the watcher's `_hub_scope_reason` before the signal can resolve as new and before a card is drafted. The same check runs on a re-check row. A first-seen URL that is not such a repository is not requested.

Out of scope ends the signal with the watcher's reason. A failed or empty read is not out of scope. The signal stays on today's path. The result names `hub_metadata` as `Hub metadata could not be read`.

The run summary is per result row. `finish` calls `summary` with that one row, and the release-signals workflow prints the row (`result.json` is appended to the step summary). Production does not group reasons across signals. `summary` can fold several rows the way the watcher summary folds a reason, and `test_the_run_summary_groups_reasons_the_way_the_watcher_does` passes several rows. A production run does not.

Round 1 base `b374f1ed8be60c8e2d603490a24e882515ca0cd4`. `tests/test_release_hub_on_read.py` reported 20 failed and 1 passed before that change, then 21 passed. The focused set reported 565 passed and 8 skipped. `tests/shard_durations.json` has `tests/test_release_hub_on_read.py` at 0.311 seconds, the summed JUnit testcase time from that round, so `test_shard_timings_cover_the_current_suite_and_browser_modules` still covers the suite. This round does not change that weight. The module already has one.

Round 2 merges `origin/main` at `618b0a8a34b778829b409e570eb63bc455072083`. The merge commit is `ade9f3bb065fdd89636b18488fc4c761d8648af4`. A read is unread unless both of these hold: the final URL is `https://huggingface.co/api/models/<org>/<repo>` (org and repo case-insensitive, one trailing slash allowed), and the payload `id`, or `modelId` when `id` is absent, equals `<org>/<repo>` case-insensitively. A payload with no id is unread. A present `tags` that is not a list of strings is unread. `tags` absent or null with a pipeline tag stays a valid read. The watcher treats absent and null the same way (`relevant_hub_tags` keeps nothing from a non-list, and `tag_scope` uses the pipeline tag). The watcher would still decide from the pipeline tag when `tags` is a string or a mixed list. This read does not. Any exception from the fetch is unread. The test double records an unexpected URL and fails after `process` returns, so the fetch path does not re-raise `AssertionError`.

Red first, same file, before the round 2 change: 8 failed, 30 passed, exit 1. After: 38 passed, exit 0. Focused set (`tests/test_release_hub_on_read.py`, `tests/test_release_signals.py`, `tests/test_release_signal_prices.py`, `tests/test_writer_isolation.py`): 582 passed, 8 skipped, exit 0.

| Case | Red result |
| --- | --- |
| off-host redirect | `out_of_scope`, expected `new` with the unread note |
| same-host redirect to another repository | `out_of_scope`, expected `new` with the unread note |
| `id` names another repository | `out_of_scope`, expected `new` with the unread note |
| `modelId` names another repository | `out_of_scope`, expected `new` with the unread note |
| no `id` | `out_of_scope`, expected `new` with the unread note |
| `tags` is a string | `out_of_scope`, expected `new` with the unread note |
| `tags` list contains a non-string | `KeyError: 'hub_metadata'` (the read was kept) |
| `AssertionError` from the fetch | `AssertionError: fetch failed closed` |

HTTP 500, a non-JSON body, and a JSON list already ended unread. Those three passed in the red run. A correct read (case-shifted final URL, one trailing slash, `id` or `modelId`) passed in the red run because the body was already applied, and it still passes. Absent and null `tags` with `text-to-image` and with `text-generation` passed before and after. Each unread case ends where Orbit 9 ends when the check does not run (`new`, `acme/orbit-9`, card drafted) and the row's summary is `Hub metadata could not be read.`

Commands, serial, no `-n`:

```bash
env PYTHONPATH=$PWD /home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_hub_on_read.py
env PYTHONPATH=$PWD /home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_hub_on_read.py tests/test_release_signals.py tests/test_release_signal_prices.py tests/test_writer_isolation.py
```

Python 3.12.3, pytest 9.2.0, ruff 0.17.4. Ruff on the edited Python files reports the same four findings as the pre-change `pipeline.py` (import order, `ModelsDevNotListed`, two long lines). No full suite, no site build, and no live Hub fetch. CI runs the full suite after the push.
