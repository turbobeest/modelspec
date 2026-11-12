# MODEL-468-B processing evidence

Base SHA is `18c7c31902cc745c076220890f5891cbdf935559`, which matched `origin/main` when this branch started. The code commits are `088d2f0c`, `99a1c9b0`, `7f5f5a14`, `74ec40b5`, `30decccb`, `1f68236a`, and `45d8748c`. This file is the commit after those.

Pytest used `/Users/terbeest/dev/modelspec/.venv/bin/python` with `PYTHONPATH` set to the worktree, flags `-q -p no:cacheprovider`, and no `-n`. Logs from the red and green runs are under `/tmp/MODEL-468-B-scratch/`.

## Existing card

`test_existing_card_stays_existing_when_the_source_refresh_misses_the_lab` failed first with `assert 'uncertain' == 'existing'` at `tests/test_release_signals.py:2305`. Exit 1. After the change, that test and the nearby existing-card tests passed, 16 passed, exit 0. Commit `088d2f0c`.

## One trailing suffix

`test_one_trailing_suffix_resolves_to_the_unsuffixed_card` and `test_a_suffixed_name_that_is_itself_a_card_is_not_stripped` failed with `AttributeError: 'Resolution' object has no attribute 'suffix_stripped'`. `test_a_stripped_name_matching_two_cards_stays_uncertain` failed with `assert 'new' == 'uncertain'`. Three failed, exit 1. After the change, 5 passed, exit 0. Commit `99a1c9b0`.

## Zero models.dev rows

`test_zero_models_dev_rows_are_not_listed_and_several_stay_uncertain`, `test_not_listed_uses_a_registered_lab_page_and_names_other_host_classes`, `test_several_models_dev_listings_are_not_guessed`, and `test_existing_card_stays_existing_when_models_dev_does_not_list_it` failed at collection. `ImportError: cannot import name 'ModelsDevNotListed'`. Exit 4. After the change, those tests and the required-source regressions passed, 31 passed, exit 0. Commit `7f5f5a14`.

A discovery signal cannot use an excluded `first_seen_url`. The contract rejects it before processing. The excluded-host case therefore uses a registered lab URL whose final URL is the excluded host, and asserts that the excluded host is not requested.

## Lab page

`test_a_registered_lab_page_that_names_the_model_identifies_the_lab` failed with `TypeError: _primary_identity() got an unexpected keyword argument 'lab_hosts'`. Exit 1. After the change, that test and the existing identity tests passed, 21 passed, exit 0. Commit `74ec40b5`.

## Test signal

`test_a_test_signal_is_ignored_and_writes_no_catalogue_files` failed with `AssertionError: fetched https://models.dev/api.json`. Exit 1. After the change, that test and `test_closed_unmerged_new_card_pr_stops_before_redrafting` passed, 2 passed, exit 0. Commit `30decccb`.

The result record is written so the acknowledgement has a status. No card, offering, or audit is written, and nothing is fetched. A `test-` id is ignored before the scope check, including when the name would otherwise be out of scope.

## Out of scope

`tests/test_release_scope.py` failed at collection with `ModuleNotFoundError: No module named 'release_signals.scope'`. Exit 2. After the change, 5 passed, exit 0, including `test_an_out_of_scope_alias_writes_nothing_and_does_not_resolve`. Commit `1f68236a`.

## Workflow cap and one issue

`test_each_run_keeps_at_most_ten_work_items_signals_before_rechecks` failed because `MAX_RELEASE_SIGNAL_WORK_ITEMS: "10"` was absent. Exit 1. After the change, that test, `test_the_roll_up_opens_one_issue_only_for_uncertain_results`, the hourly workflow test, the ambiguous-identity test, the writer-isolation parametrized test, the engine-pin checkout test, and the price-workflow tests passed, 15 passed, exit 0. Commit `45d8748c`.

The closed-unmerged step still has the name `Flag a new-model PR closed without merge` and still supplies the pull request URL to the acknowledgement. It no longer runs `gh issue create`. Uncertain results are collected by the `review` job, which opens one issue. Statuses `existing` with no diff, `ignored`, and `out_of_scope` open nothing.

## Focused run before push

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_release_signals.py tests/test_release_scope.py tests/test_writer_isolation.py tests/test_engine_pin.py tests/test_release_signal_prices.py
```

610 passed in 16.69s. Exit 0.

## Not observed

No full pytest suite. No site build. No worker memory probe. No production fetch. No Linear write. CI status is not in this file, because the pull request did not exist when this file was committed.

## First CI check

Draft pull request 1049. The first `gh pr checks` call, after three waits of 240 seconds, exited 1.

`pytest shard 5/8` failed `tests/test_ci_workflows.py::test_shard_timings_cover_the_current_suite_and_browser_modules` with `only 362/382 test modules have measured timings`. `tests/test_release_scope.py` had no row in `tests/shard_durations.json`. A serial JUnit run of that file summed to 0.003 seconds, and that value is now the row.

`Run pytest` failed in 3 seconds as the shard aggregator.

`Test decide page (human gate true, visit gate false)` failed `browser-tests/simple-decide.spec.ts` on an old-board link. The page URL kept a `#s=` hash the assertion did not expect. The other three decide-page variants passed. This branch does not change the decide page, the site, the worker, or frozen data. `Build both sites` failed in 5 seconds because that browser result was `failure`.

The second check follows the timing push. Its result is not in this file.
