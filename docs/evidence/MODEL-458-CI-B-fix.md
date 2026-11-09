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
