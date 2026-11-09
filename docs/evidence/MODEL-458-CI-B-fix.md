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
python /tmp/MODEL-458-CI-B-scratch/root/repro/F3/probe_deploy.py build
python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py -k site_build_preserves
python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py tests/test_decide_preview_workflow.py --basetemp /tmp/MODEL-458-CI-B-scratch/root/F3-green
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
python -m pytest -q -s -p no:cacheprovider /tmp/MODEL-458-CI-B-scratch/root/repro/F4/test_repro.py --basetemp /tmp/MODEL-458-CI-B-scratch/root/F4-repro
python -m pytest -q -p no:cacheprovider tests/test_data_workflows.py tests/test_release_signals.py -k pending_gate --basetemp /tmp/MODEL-458-CI-B-scratch/root/F4-red
python -m pytest -q -p no:cacheprovider tests/test_data_workflows.py tests/test_release_signals.py --basetemp /tmp/MODEL-458-CI-B-scratch/root/F4-green
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
python -m pytest -q -s -p no:cacheprovider /tmp/MODEL-458-CI-B-scratch/root/repro/F5/test_repro.py --basetemp /tmp/MODEL-458-CI-B-scratch/root/F5-repro
python -m pytest -q -p no:cacheprovider tests/test_accuracy_alert.py -k nightly_close --basetemp /tmp/MODEL-458-CI-B-scratch/root/F5-red
python -m pytest -q -p no:cacheprovider tests/test_accuracy_alert.py tests/test_ci_workflows.py --basetemp /tmp/MODEL-458-CI-B-scratch/root/F5-green
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
python -m pytest -q -s -p no:cacheprovider /tmp/MODEL-458-CI-B-scratch/root/repro/F6/test_repro.py --basetemp /tmp/MODEL-458-CI-B-scratch/root/F6-repro
python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py -k validation_comment --basetemp /tmp/MODEL-458-CI-B-scratch/root/F6-red
python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py tests/test_validate_pr.py --basetemp /tmp/MODEL-458-CI-B-scratch/root/F6-green
```

Green: 131 passed in 38.17s, exit 0, 38.420s process elapsed. No comment or
label was sent to GitHub. The renderer ran on Node v22.22.3.

A follow-up review added zero-exit incomplete-row controls. Four failed because
the pass flag was true for rows lacking required display data. The validation
step now rejects those rows too, so the comment and final gate agree.

```text
python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py -k validation_comment --basetemp /tmp/MODEL-458-CI-B-scratch/root/F6-row-red
python -m pytest -q -p no:cacheprovider tests/test_ci_workflows.py tests/test_validate_pr.py --basetemp /tmp/MODEL-458-CI-B-scratch/root/F6-row-green
```

Follow-up red: 4 failed, 32 passed, exit 1. Green: 139 passed in 33.40s,
exit 0, 33.646s process elapsed.
