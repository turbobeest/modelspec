# MODEL-481 alerting

Base `a2e029b53004a9d7575d84fde05d6c378fafd8fa` on `model-481-alert`.
The head SHA is the commit that adds this file.

Environment: Python 3.14.4, pytest 9.1.1, PyYAML 6.0.3. Tests ran serially with `env PYTHONPATH=$PWD` and `/Users/terbeest/dev/modelspec/.venv/bin/python`. No network.

## Red, then green

These eight tests in `tests/test_price_reread_alert.py` ran against the unchanged tree.

- `test_alert_comment_counts_sources_without_cutting_a_row`
- `test_json_keeps_the_whole_reason_and_markdown_keeps_the_trailing_count`
- `test_pull_request_body_under_the_limit_is_unchanged`
- `test_pull_request_body_keeps_a_complete_table_or_leaves_it_out`
- `test_the_reread_job_uploads_the_report_and_can_label_issues`
- `test_alert_issue_step_labels_create_and_an_existing_issue` with no existing issue
- `test_alert_issue_step_labels_create_and_an_existing_issue` with issue 17
- `test_a_label_failure_warns_and_leaves_the_alert_step_green`

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_price_reread_alert.py
```

Exit 1. 8 failed in 0.51s.

`alert_comment` and `fit_pull_request_body` were missing, so four tests raised `AttributeError`. The workflow test raised `StopIteration` because no artifact was named `price-reread-report`. The Markdown Why cell for a long unreadable reason ended at 120 characters and dropped `41823 characters of text`. The three shell tests exited 1 because the alert step still contained `${{ github.server_url }}` and `${{ github.repository }}` inside `run:`.

After the script and workflow edits, the same command exited 0. 8 passed in 2.41s.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_writer_isolation.py tests/test_writer_artifacts.py tests/test_engine_pin.py
```

Exit 0. 423 passed in 14.20s.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_price_reread.py tests/test_price_reread_fallback.py tests/test_price_reread_alert.py
```

Exit 0. 258 passed in 4.57s.

## What changed

The price re-read workflow source is `.github/private-writers/price-reread.yml`. The public stub `.github/workflows/price-reread.yml` is unchanged. The private data repository installs its own byte-identical copy. This commit does not change `modelspec-data`.

`fit_pull_request_body` in `scripts/price_reread.py` returns a body unchanged when it is at most 60,000 characters. Over that cap it keeps the report header, then each whole section that fits, preferring Changed values, then Needs a person, then Not re-read, then Source diffs. A section that does not fit is replaced by one line. A table line names how many rows were left out. The source-diff line says the diffs were left out. Both lines name the `price-reread-report` artifact. The fitter was copied here. `scripts/refresh_leaderboards.py` stays as it is. That fitter counts leaderboard failure rows and a pull-request URL placeholder, and that file is outside this change.

The alert Markdown Why cell still stops at 120 characters. It now keeps the start and the end, so a trailing page-size count stays in the cell. Old and new value cells still cut at the end. `report.json` still stores the full reason.

The reread job uploads `report.md` and `report.json` as `price-reread-report` with `if: always()`, retention 35 days, and `if-no-files-found: error`, after "Re-read every page once". The change pull request and the reconfirmation pull request both use a fitted body. The reconfirmation body is written to `reconfirm-body.md` and leaves `report.md` whole for the artifact.

The alert issue is created with label `alert`. An open issue with the same title gets `gh issue edit --add-label alert`. If the label is missing, the step runs `gh label create alert`. A create or edit failure prints `::warning::` and the step exits 0. Stderr that contains `already exists` is success and prints no warning. If listing open issues fails, the step does not open a second issue. "Fail a run with alerts" is unchanged and still exits 1 when the alert count is not 0. The job permissions stay `contents: write`, `pull-requests: write`, `issues: write`, and `actions: read`.

`.github/private-writers/rendered-reread.yml` is unchanged. Its shape differs.

- Alerts go through `python -I .github/scripts/rendered_reread.py --sync-alerts`. That script lives in the data checkout. This repository has no shell step that pastes a markdown report onto an issue.
- The pull-request body is a short static template written to `rendered-pr-body.md`. The workflow has no `head -c`.
- The job uploads `report.json` as `rendered-reread-ledger` and source copies as `rendered-reread-copies`. There is no markdown report artifact.
- The job already has `issues: write`.

## Not observed

The full pytest suite, a live price-reread run, and GitHub's response to the label and issue calls.
