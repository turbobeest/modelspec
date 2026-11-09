# MODEL-458-CI-B verification

Base SHA: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`, also the remote main SHA at start.
The final implementation SHA and draft PR are recorded in the PR body and executor result.

All checks run from the ticket worktree. Python is 3.14.4, pytest uses the
repository virtualenv, Node is v22.22.3, Bash is 5.3.9, jq is 1.7.1-apple,
and Git is 2.50.1. Test commands use `PYTHONPATH=$PWD`,
`PYTHONDONTWRITEBYTECODE=1`, and the prescribed Node bin directory first on PATH.
Tests run serially with the cache provider disabled. CI remains the full gate.

## AUD-08-F3

The site Build step preserves the builder exit status with pipefail. A successful
build still writes the JSON and GitHub step summaries.

The supplied offline reproduction exited 1 before the change. The builder
returned 42 while the step returned 0. Permanent regression
`test_site_build_preserves_builder_status_and_summary[failed]` then failed with
`assert 0 == 42`; its successful-builder control passed.

Commands, using `/Users/terbeest/dev/modelspec/.venv/bin/python`:

```text
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/MODEL-458-CI-B-scratch/root/repro/F3/probe_deploy.py build
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py -k site_build_preserves
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py tests/test_decide_preview_workflow.py --basetemp /tmp/MODEL-458-CI-B-scratch/root/F3-green
```

Red: 1 failed, 1 passed, exit 1. Green: 78 passed in 3.38s, exit 0,
3.617s measured process elapsed time.

Only the workflow shell ran with an offline builder fixture. No site build,
production request, deployment, private data read or credential operation ran.

## AUD-08-F4

The pending-work count requires one JSON object with array-valued `signals` and
`rechecks`. Invalid shapes fail with a body-free diagnostic. Empty arrays count
as zero; nonempty queues trigger one dispatch through the existing condition.
The response shape was checked against `docs/grok-bot-signals.md` and
`docs/release-watch.md`; no API contract changed.

The supplied reproduction had 5 failures, exit 1. Permanent regressions
`test_pending_gate_rejects_malformed_response_without_publishing_body` and
`test_pending_gate_counts_valid_queues_and_dispatches_once` had 9 failures and
9 passes before the fix. The failures returned zero for malformed input.

```text
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -s -p no:cacheprovider /tmp/MODEL-458-CI-B-scratch/root/repro/F4/test_repro.py --basetemp /tmp/MODEL-458-CI-B-scratch/root/F4-repro
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_data_workflows.py tests/test_release_signals.py -k pending_gate --basetemp /tmp/MODEL-458-CI-B-scratch/root/F4-red
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_data_workflows.py tests/test_release_signals.py --basetemp /tmp/MODEL-458-CI-B-scratch/root/F4-green
```

Green: 177 passed in 1.85s, exit 0, 2.287s process elapsed. Only local jq and
shell fixtures ran; no HTTP request or GitHub dispatch was sent.

## AUD-08-F5

The nightly close-alert step preserves issue-list and issue-close exit status.
Its existing success condition is unchanged. Empty lists succeed and every
listed issue is closed when all commands succeed.

The supplied reproduction exited 1 with list status 42 and step status 0.
`test_nightly_close_alert_propagates_command_results[list-failure]` failed with
`assert 0 == 42`; the other three controls passed before the change.

```text
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -s -p no:cacheprovider /tmp/MODEL-458-CI-B-scratch/root/repro/F5/test_repro.py --basetemp /tmp/MODEL-458-CI-B-scratch/root/F5-repro
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_accuracy_alert.py -k nightly_close --basetemp /tmp/MODEL-458-CI-B-scratch/root/F5-red
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_accuracy_alert.py tests/test_ci_workflows.py --basetemp /tmp/MODEL-458-CI-B-scratch/root/F5-green
```

All issue commands were shell function fixtures. No GitHub issue was listed,
closed or commented on by these checks.

Green: 79 passed in 2.00s, exit 0, 2.210s process elapsed.

## AUD-08-F6

The card-validation comment takes its success state from the validation step.
Report structure is checked before tables render. Complete valid, invalid and
regression reports retain their tables. Both new-comment and update-comment
paths are exercised against in-memory GitHub fixtures. The final failure gate
is unchanged and is executed for failing validation fixtures.

The supplied reproduction exited 1. Permanent test
`test_validation_comment_agrees_with_gate_and_renders_tables` produced 28 red
cases before the fix, including an incorrect success message after validator
exit 42, unsafe table rendering, and missing pass-flag wiring.

```text
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -s -p no:cacheprovider /tmp/MODEL-458-CI-B-scratch/root/repro/F6/test_repro.py --basetemp /tmp/MODEL-458-CI-B-scratch/root/F6-repro
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py -k validation_comment --basetemp /tmp/MODEL-458-CI-B-scratch/root/F6-red
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py tests/test_validate_pr.py --basetemp /tmp/MODEL-458-CI-B-scratch/root/F6-green
```

Green: 131 passed in 38.17s, exit 0, 38.420s process elapsed. No comment or
label was sent to GitHub. The renderer ran on Node v22.22.3.

A follow-up review added zero-exit incomplete-row controls. Four failed because
the pass flag was true for rows lacking required display data. The validation
step now rejects those rows too, so the comment and final gate agree.

```text
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py -k validation_comment --basetemp /tmp/MODEL-458-CI-B-scratch/root/F6-row-red
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py tests/test_validate_pr.py --basetemp /tmp/MODEL-458-CI-B-scratch/root/F6-row-green
```

Follow-up red: 4 failed, 32 passed, exit 1. Green: 139 passed in 33.40s,
exit 0, 33.646s process elapsed.

## AUD-08-F2

Both private deployment jobs check current and successor memory before deploy.
The deployment ceiling remains 120 MiB; the public ceiling remains 115 MiB.
Synthetic measurements use the real `assessMemory` function. The actual gate
and deploy run blocks execute with offline installation/deployment fixtures.

The supplied current-failure control exited 0, observing a failing step for
both jobs. The successor-failure reproduction exited 1 because each step ran
only the current period. Permanent regression
`test_private_deploy_requires_memory_for_both_periods` had 4 failures and
2 passes before the fix. Afterward it checks both periods, failure propagation,
no deploy after failure, and both-pass controls exactly at 120 MiB.

```text
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/MODEL-458-CI-B-scratch/root/repro/F2/probe_deploy.py current
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/MODEL-458-CI-B-scratch/root/repro/F2/probe_deploy.py successor
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_worker_memory.py -k private_deploy --basetemp /tmp/MODEL-458-CI-B-scratch/root/F2-red
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_worker_memory.py tests/test_ci_workflows.py --basetemp /tmp/MODEL-458-CI-B-scratch/root/F2-green
```

Green: 123 passed in 13.24s, exit 0, 13.526s process elapsed. These checks do
not measure a real private bundle. No Pyodide load, network package install,
private data access, credentials or deployment was involved.

## AUD-08-F8

Four functions, six collected cases, now have the perf marker. The collection
regression checks all six exact IDs under `perf` and none under `not perf`.
The existing workflow still runs one serial perf job. Timing assertions and
all their limits are unchanged.

The supplied reproduction exited 1 after its inner collection exited 5 with
`no tests collected (6 deselected)`. Both cases of
`test_wall_clock_cases_are_collected_only_by_the_serial_perf_job` failed before
the marker change: perf selected none, while not-perf selected all six.

```text
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -s -p no:cacheprovider /tmp/MODEL-458-CI-B-scratch/root/repro/F8/test_repro.py --basetemp /tmp/MODEL-458-CI-B-scratch/root/F8-repro
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py -k wall_clock --basetemp /tmp/MODEL-458-CI-B-scratch/root/F8-red
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider -p no:xdist -m perf tests/test_decide_worker.py::test_explain_none_p95_is_under_200_ms tests/test_decide_worker.py::test_fresh_snapshot_load_and_first_domain_decision_stay_under_budget tests/test_decision_summary.py::test_a_huge_tie_and_objective_keep_the_leaderboard_item_bounded_and_fast tests/test_speed_harness.py::test_the_live_transport_measures_a_stream_of_known_timing --basetemp /tmp/MODEL-458-CI-B-scratch/root/F8-perf --junitxml=/tmp/MODEL-458-CI-B-scratch/root/F8-perf.xml
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider -p no:xdist -m 'not perf' tests/test_ci_workflows.py tests/test_decide_worker.py tests/test_decision_summary.py tests/test_speed_harness.py --basetemp /tmp/MODEL-458-CI-B-scratch/root/F8-green
```

Perf: 6 passed in 16.96s, exit 0. Process elapsed was 17.285s; summed JUnit
testcase time was 16.256s. Remaining focused tests: 315 passed, 1 skipped,
6 deselected in 33.38s, exit 0, 33.705s process elapsed.
The local runner was Darwin 27.2.0 arm64 with Python 3.14.4, rather than CI's
Ubuntu runner. These timings do not predict GitHub runner performance. The
stream fixtures use localhost; no provider API was called.


## AUD-08-F7

All 109 external action references across the 29 workflows use full commit
SHAs. The original version/ref remains in each inline comment. The permanent
guard covers both workflow extensions, step actions and reusable workflow jobs,
and allows local actions. Blog tests select by action identity and preserve
their ordering and checkout-depth assertions.

The supplied reproduction exited 1 with 109 mutable references. Permanent
`test_external_workflow_actions_use_full_commit_references` failed before the
pins; the 16 guard controls passed.

Every SHA below was resolved on 2026-11-09 with `git ls-remote` over HTTPS,
with exit 0. The annotated setup-uv tag uses its peeled commit. The PyPI
publisher's release/v1 ref is a branch. No GitHub API call was used for these
lookups. No updater configuration existed; the version comments retain the
standard format understood by action update tools.

| Action and original ref | Resolved commit |
| --- | --- |
| `actions/cache@v4` | `0057852bfaa89a56745cba8c7296529d2fc39830` |
| `actions/checkout@v4` | `11d5960a326750d5838078e36cf38b85af677262` |
| `actions/download-artifact@v4` | `d3f86a106a0bac45b974a628896c90dbdf5c8093` |
| `actions/github-script@v7` | `f28e40c7f34bde8b3046d885e986cb6290c5673b` |
| `actions/setup-node@v4` | `49933ea5288caeca8642d1e84afbd3f7d6820020` |
| `actions/setup-python@v5` | `a26af69be951a213d495a4c3e4e4022e16d87065` |
| `actions/upload-artifact@v4` | `ea165f8d65b6e75b540449e92b4886f43607fa02` |
| `astral-sh/setup-uv@v6` | `d0cc045d04ccac9d8b7881df0226f9e82c39688e` |
| `cloudflare/wrangler-action@v3` | `9acf94ace14e7dc412b076f2c5c20b8ce93c79cd` |
| `peter-evans/create-pull-request@v7` | `22a9089034f40e5a961c8808d113e2c98fb63676` |
| `pypa/gh-action-pypi-publish@release/v1` | `7245906fb61fa33a13554f9d5fb856fe61758086` |

Exact resolution commands:

```text
git ls-remote https://github.com/actions/cache.git refs/tags/v4 'refs/tags/v4^{}' refs/heads/v4
git ls-remote https://github.com/actions/checkout.git refs/tags/v4 'refs/tags/v4^{}' refs/heads/v4
git ls-remote https://github.com/actions/download-artifact.git refs/tags/v4 'refs/tags/v4^{}' refs/heads/v4
git ls-remote https://github.com/actions/github-script.git refs/tags/v7 'refs/tags/v7^{}' refs/heads/v7
git ls-remote https://github.com/actions/setup-node.git refs/tags/v4 'refs/tags/v4^{}' refs/heads/v4
git ls-remote https://github.com/actions/setup-python.git refs/tags/v5 'refs/tags/v5^{}' refs/heads/v5
git ls-remote https://github.com/actions/upload-artifact.git refs/tags/v4 'refs/tags/v4^{}' refs/heads/v4
git ls-remote https://github.com/astral-sh/setup-uv.git refs/tags/v6 'refs/tags/v6^{}' refs/heads/v6
git ls-remote https://github.com/cloudflare/wrangler-action.git refs/tags/v3 'refs/tags/v3^{}' refs/heads/v3
git ls-remote https://github.com/peter-evans/create-pull-request.git refs/tags/v7 'refs/tags/v7^{}' refs/heads/v7
git ls-remote https://github.com/pypa/gh-action-pypi-publish.git refs/tags/release/v1 'refs/tags/release/v1^{}' refs/heads/release/v1
```

Validation commands:

```text
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -s -p no:cacheprovider /tmp/MODEL-458-CI-B-scratch/root/repro/F7/test_repro.py --basetemp /tmp/MODEL-458-CI-B-scratch/root/F7-repro
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py -k 'external_workflow_actions or action_reference_guard' --basetemp /tmp/MODEL-458-CI-B-scratch/root/F7-red
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py tests/test_data_workflows.py tests/test_decide_preview_workflow.py tests/test_card_stats_workflow.py tests/test_mcp_ci.py tests/test_workflow_dependencies.py tests/test_blog_deployment.py::test_workflows_gate_blog_publication_and_notify_only_after_production_deploy tests/test_blog_deployment.py::test_pytest_ci_fetches_the_base_for_publication_history_checks tests/test_data_lag.py::test_add_paths_in_the_lag_workflow_match_the_data_paths tests/test_release_watch_filter.py::test_workflow_keeps_normalized_reports_for_a_30_day_replay tests/test_pypi_packaging.py::test_only_release_pypi_publishes_and_only_by_trusted_publishing tests/test_pypi_packaging.py::test_ci_builds_and_installs_the_wheel_in_a_fresh_environment --basetemp /tmp/MODEL-458-CI-B-scratch/root/F7-green
actionlint -shellcheck= -pyflakes=
git diff --check
```

Green: 317 passed in 10.96s, exit 0, 11.227s process elapsed.
Actionlint 1.7.12 passed with shellcheck and pyflakes disabled, matching the
workflow's actionlint scope. YAML parsed successfully for every workflow.
A normalization check replaced each pin with its original ref in memory and
confirmed that the parsed workflow values were otherwise unchanged by pinning.
The final diff passed whitespace checks.

## Verification limits and final revision

Pytest version was 9.1.1. The one skipped test in F8 was the existing
MODEL-139 recall-spec placeholder. Six timing cases were deliberately excluded
from the non-perf run and all six passed in the separate serial run.

Read-only review found no further defect in the seven changes. This does not
replace the independent review required before the draft PR is ready to merge.
No local full suite, site build, live deployment, private-bundle measurement,
paid service, production switch change or release-tag operation was performed.
Remote action resolution and publishing this ticket branch/draft PR are the
only intended network operations. GitHub CI remains the full validation gate.

The exact final SHA is the commit containing this evidence revision. Resolve
it with `git log -1 --format=%H -- docs/evidence/MODEL-458-CI-B-fix.md`.
The immutable value is also included in the draft PR body and final executor
result, outside the commit whose hash it names.
