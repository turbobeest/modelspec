# MODEL-450 execution evidence

Status: implementation and local verification complete; scheduled private
execution is blocked. The existing public coverage workflow has no private
release-history input. The spec allows data-repository changes only in its
named data worktree, but supplies no such path or branch. No scheduled
producer, private issue job, or public counts handoff has been deployed.

Base SHA: `6815544116839f991c10904772e7357f12d5b566`.
Verified implementation SHA: `aec4ec0ea9234f64043b11e033f0f5c4db9a1027`.
The final evidence-only commit is recorded by its exact SHA in the executor's
untracked `.pr-commit.txt` and final handoff. Obtain that final SHA from the PR
head with `git rev-parse HEAD`; this evidence file cannot contain its own
commit hash.

## Changes

Four 28-day release targets measure discovery to card, price, score and
decidable milestones, with 1/2/2/3-day limits. Main first-parent history
supplies merged milestones. Retained discovery and snapshot files supply
observations. The detailed report includes p50, p90 and per-release rows.
Pending work contributes elapsed lower bounds; imported or stale history is
unknown. Only clause-1 labs enter the decidable cohort.

Alerts use one issue per late release and stage. The existing deduplication,
update, close and 24-hour escalation behavior remains. Public reports copy
only counts; private detail and issue routing stay in modelspec-data. The
offline `--issues-json` path cannot apply GitHub changes.

## Red first

All commands ran from `/Users/terbeest/dev/worktrees/model-450` with:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider <files and selectors below>
```

| Command suffix | Defect and named test | Recorded red output | Final green coverage |
| --- | --- | --- | --- |
| `tests/test_release_slo.py` | `test_release_lags_include_pending_work_and_scope_decidable_to_eligible_labs`, privacy and missing snapshot tests | `3 failed`; `AttributeError: module 'scripts.slo.report' has no attribute 'ReleaseHistory'`, exit 1 | All three pass |
| `tests/test_release_slo_history.py` | `test_merged_stages_use_discovery_value_bound_verification_and_snapshot` and baseline, branch, malformed-history tests | `4 failed`; `ModuleNotFoundError: scripts.slo.releases`, exit 1 | All four pass |
| `tests/test_coverage_slo.py -k release_stage_alerts_keep_each_release_separate_and_deduplicate` | Two late releases collapsed into one price-stage issue | One issue returned where two were expected, exit 1 | Per-release creation, deduplication and private routing pass |
| `tests/test_coverage_slo.py -k release_stage_alerts_refuse_an_incomplete_issue_listing` | An incomplete issue list could create duplicates | `DID NOT RAISE ValueError`, exit 1 | Cap exhaustion refuses planning |
| `tests/test_release_slo.py` | `test_staged_price_breach_runs_through_cli_render_and_offline_alert` and private-context refusal | `2 failed, 4 passed`; missing releases module and `invalid choice: 'releases'`, exit 1 | Both pass |
| `tests/test_release_slo.py -k public_report_imports` | Public input needed a counts-only boundary | `AttributeError: ... no attribute 'public_release_report'`, exit 1 | Names, raw errors and timings discarded; stale and inconsistent counts refused |
| `tests/test_release_slo_history.py` | Imported stages and undated cards | `2 failed, 3 passed`; baseline unknown stages empty; one undated card aborted extraction, exit 1 | Unknown milestones and count-only omitted-card errors pass |
| `tests/test_release_slo.py -k 'stale_or_future_snapshot or fresh_snapshot_bounds or observed_decidable_completion'` | Old/future snapshots falsely established pending lag; completed observations were lost | `5 failed, 1 passed`; false breach, lag `4` instead of `3.75`, completion reported unknown, exit 1 | All six cases pass |
| `tests/test_release_slo_history.py` | Snapshot watermark and malformed artifact rows | `2 failed, 4 passed` before watermark support; malformed rows raised `AttributeError`, exit 1 | Latest watermark, earliest inclusion and sanitized errors pass |
| `tests/test_release_slo_history.py -k 'real_watch_signal or unknown_provider'` | Real six-field signals without cards disappeared | `2 failed, 7 deselected`; pending release absent, unmatched errors empty, exit 1 | Pending identity survives later merge; ambiguity counted |

`test_one_late_release_opens_one_issue_per_late_stage_and_none_for_on_time_stages`
checks the acceptance fixture: an on-time card and three late stages create
exactly three issues. The on-time release creates none. A second plan creates
no duplicate issues.

## Final verification

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_coverage_slo.py tests/test_release_slo.py tests/test_release_slo_history.py tests/test_removed_sources.py
```

Exit 0: `148 passed, 1 skipped in 64.52s`. The skipped test requires
`MODELSPEC_DIST` pointing to a built site. No full local suite ran.

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check scripts/slo/report.py scripts/slo/render.py scripts/slo/alerts.py scripts/slo/__main__.py scripts/slo/releases.py tests/test_release_slo.py tests/test_release_slo_history.py
git diff --check
```

Both exit 0. Ruff initially reported import/unused-import and line-length
findings in new code; those were corrected before the final pass.

Tools: Python 3.14.4, pytest 9.1.1, PyYAML 6.0.3, pydantic 2.13.5,
ruff 0.16.6, git 2.50.1, gh 2.102.0. No Node toolchain was needed.

## Offline alert proof

A local synthetic main history had an empty baseline commit and one card
committed on the report day. Its price age was within the two-day limit.
These actual commands exited 0:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.slo releases --data-dir /tmp/model-450-scratch/executor/synthetic-data --private-detail --now 2026-11-04T12:00:00+00:00 --stage-breach release-price-lag --out /tmp/model-450-scratch/executor/staged
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.slo alert --report /tmp/model-450-scratch/executor/staged/coverage.json --issues-json /tmp/model-450-scratch/executor/issues.json --only release-price-lag --now 2026-11-04T12:00:00+00:00
```

The issue file contained `[]`. Alert stdout was exactly:

```text
create Coverage SLO breach: release-price-lag: staged-breach (release-price-lag)
```

No GitHub call or real issue write occurred. The focused CLI and git-history
fixtures reproduce both halves of this proof.

## Real data, counts only

The authorized scratch clone command was:

```bash
git clone https://github.com/turbobeest/modelspec-data.git /tmp/model-450-scratch/private-inputs/modelspec-data
```

The clone had complete history. This report command exited 0:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m scripts.slo releases --data-dir /tmp/model-450-scratch/private-inputs/modelspec-data --ref origin/main --last 10 --window-days 3650 --now 2026-11-04T12:00:00+00:00 --out /tmp/model-450-scratch/executor/last-ten
```

The wider audit window selects ten releases; the production target remains
28 days. The reader found 1,352 dated releases and 33 cards without a usable
discovery or release date. Nine of the selected ten qualify for the decidable
target. No retained discovery series or canonical snapshot series was supplied.

| Stage | Measured | Completed | Pending | Unknown | Late |
| --- | ---: | ---: | ---: | ---: | ---: |
| Card | 5 | 5 | 0 | 5 | 5 |
| Price | 6 | 1 | 5 | 4 | 6 |
| Score | 6 | 0 | 6 | 4 | 6 |
| Decidable | 0 | 0 | 0 | 9 | 0 |

All four targets have error status because input history is incomplete.
Unknown times are not counted as late or successful. A second local probe,
`env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/model-450-scratch/executor/verify-private.py`,
computed the detailed report in memory, checked ten rows and percentile fields
for all four stages, and compared every catalogue model ID against the public
JSON, Markdown and HTML. Exit 0: ten releases checked, four percentile stages
checked, zero private names in public output. No private timings or rows are
published here. The private scratch clone was deleted after measurement.

## Not observed

- No production run, live GitHub breach issue, scheduled private producer, or
  public counts handoff was observed. Missing authorized data-worktree scope
  blocks that integration. The draft PR must not be treated as a completed
  daily SLO deployment.
- No evidence establishes four consecutive weeks with decidable p90 at most
  three days. The missing snapshot history prevents that claim.
- No full pytest gate, site build, CI result, deployed Worker memory probe,
  or production deployment was run. Worker exports, frozen data and production
  switches were not changed.
- No source-page fetch, paid-provider call, Linear write, merge, or force push
  occurred. Private data was read only in the scratch clone.
