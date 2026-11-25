# MODEL-494: the refresh report carried an unsubstituted placeholder

## What was wrong

`scripts/refresh_leaderboards.py` wrote the text `${PR_URL}` into the `pr` field of every score-change row and into the last column of the "Score changes" table. The workflow uploads `audit.json`, `report.json` and `report.md` as the artifact `leaderboard-refresh-report` before any pull request exists, so that artifact always held the placeholder. Nothing filled `report.md` or `report.json` afterwards. A run that opened no pull request (a dry run, a failed run) left the placeholder everywhere.

## What the engine writes now

- `ScoreChange.to_dict` writes `"pr": null`. The key stays.
- `audit_markdown` has no pull-request column. The table is Model, Benchmark, Old value, New value, Source, Observed date.
- Nothing the engine writes contains `${PR_URL}`.

## Where the pull request address is still recorded

Only the workflow knows the address. The step "Put the PR URL in the audit records" sets `row["pr"]` on a copy of `audit.json` once a pull request exists. That copy is the artifact `leaderboard-refresh-audit-<number>`. The step "Fill the pull request URL into the body" still runs its `.replace` on the body. It now finds nothing to replace and changes nothing.

`tests/test_leaderboard_refresh.py::test_refresh_report_files_carry_no_pull_request_placeholder` holds the behaviour.
