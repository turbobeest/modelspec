# MODEL-467-WF

Base `58748fec44f4055a16e37229764f60467278a5a8` on `model-467-wf`.
The head SHA is the commit that adds this file.

Environment: Python 3.14.4, pytest 9.1.1, PyYAML 6.0.3. Tests ran serially, with no network.

## Red, then green

These five tests ran against the unchanged tree:

- `test_pull_request_body_under_the_limit_is_unchanged`
- `test_pull_request_body_over_the_limit_cuts_on_a_change_row`
- `test_pull_request_body_keeps_every_failure_row_when_changes_are_cut`
- `test_fitted_body_stays_within_the_limit_after_the_pull_request_url_expands`
- `test_large_refresh_uploads_the_report_before_a_body_edit_can_fail`

Exit 1. 5 failed in 0.38s.

The four body tests raised `AttributeError` because `scripts.refresh_leaderboards` had no `fit_pull_request_body`. The workflow test found the step after "Re-read every covered board once" was "Prove the generated diff is score-only", whose `if` is `inputs.dry_run != true`.

After the fitter and the workflow reorder:

```sh
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider tests/test_leaderboard_refresh.py tests/test_arena_revision.py
```

Exit 0. 101 passed in 5.37s.

`tests/test_writer_isolation.py -k leaderboard-refresh` exited 0. 4 passed, 292 deselected.

## What changed

`fit_pull_request_body` returns a body unchanged when it fits in 60,000 characters. It counts each `${PR_URL}` as a 60-character pull request URL. Over the limit it keeps the opening line, the Arena revision line, the per-board table and every failure row, then as many score-change rows as fit, then one line naming how many change rows were left out. The full `report.md`, `report.json` and `audit.json` upload as `leaderboard-refresh-report` with `if: always()` immediately after the read step. The audit artifact uploads before `gh pr edit`. That edit is `continue-on-error: true` and emits `::warning::` when it fails. The score-only guard and the no-update failure still fail the run.

A 750-change body of 98,581 characters, after the pull request URL was filled in, fitted to 59,838 characters, kept all 12 failure rows, and left out 416 change rows.

## Not observed

The full pytest suite, a live leaderboard-refresh run, and GitHub's response to the edited body. This commit leaves the private data repository unchanged. That repository installs its own copy of this workflow.
