# MODEL-474 rescope on read

Processing a signal reads a first-seen model repository on a Hugging Face organisation registered for its lab, then calls the watcher's `_hub_scope_reason` before the signal can resolve as new and before a card is drafted. The same check runs on a re-check row. A first-seen URL that is not such a repository is not requested.

The read is one models API object, `huggingface.co/api/models/{org}/{repo}`, through the pipeline fetcher. Out of scope ends the signal with the watcher's reason. The result summary groups those reasons with `_report_reason`.

A failed or empty metadata read is not out of scope. The signal stays on today's path. The result names `hub_metadata` as `Hub metadata could not be read`, and the summary adds that note once.

`tests/test_release_hub_on_read.py` reported 20 failed and 1 passed before the change, then 21 passed. The focused set (that file, `tests/test_release_signals.py`, `tests/test_release_signal_prices.py`, `tests/test_writer_isolation.py`) reported 565 passed and 8 skipped. After the line wrap, the hub file passed again, 21 passed. `tests/shard_durations.json` records this file at 0.311 seconds, the summed JUnit testcase time, so the shard timing check still covers the suite. Ruff on the edited Python files reports only findings already present on the base.

Base `b374f1ed8be60c8e2d603490a24e882515ca0cd4`. Serial pytest, `-q -p no:cacheprovider`, no `-n`.
Python 3.12.3, pytest 9.2.0, ruff 0.17.4. CI runs the full suite after the push.
