# MODEL-483 nightly public output

Base `a2e029b53004a9d7575d84fde05d6c378fafd8fa` (`origin/main` when this branch was created).
Worktree `/Users/terbeest/dev/worktrees/model-483-log`, branch `model-483-log`.

The latest commit that changes this file is the round 2 evidence commit. Read its SHA with `git log -1 --format=%H -- docs/evidence/MODEL-483-nightly-public-output.md`.

## What the public sinks carry

`public_nightly_report` in `scripts/accuracy_public.py` is the report text a private nightly writes to stdout, and the report text `scripts/accuracy_alert.py` puts in the public issue. After that report, both sinks add one sentence. The sentence says the full report is on the machine that ran the job, and it names the output directory only. Each layer line is a status, a yes or no gate, and named counts. The job writes no step summary and uploads no artifact. The full report is still written under the output directory for a local run.

A failed layer still prints FAIL. `main` still returns 1 when `report.status` is `fail`. An unknown layer name prints as `layer`. The named counts are failures, mismatches, unreachable, undetermined, and over the undetermined limit as yes or no. Frozen-image recall also counts verdicts that differ from the baseline. When `--private-data-root` is set, an exception from the run or from the public form prints one fixed line to stderr, with the exception class name only, and `main` returns 1. `KeyboardInterrupt` and `SystemExit` still propagate. Without the flag, the traceback still prints.

## Private checkout

`actions/checkout` at pin `11d5960a326750d5838078e36cf38b85af677262` runs `git log -1 --format=%H` with the silent flag off when a format is given (`GitCommandManager.log1` in that pin). The private step is a shallow fetch of `refs/heads/main` into `.accuracy-private`. Each git command discards stdout and stderr. `set -euo pipefail` still checks the exit code. The token is `http.extraheader` on that fetch only and is not echoed. The public engine checkout is unchanged.

## Item 3: private sink

`docs/design/data-split.md` describes `MODELSPEC_DATA_TOKEN` as a fine-grained token with read-only Contents access to `turbobeest/modelspec-data` and nothing else. A write path is a separate credential. `docs/method/coverage-slo.md` adds Actions: read for the coverage job, which does not check the repository out.

A private issue titled "Accuracy nightly failed" with label `alert` would need Issues: write on `turbobeest/modelspec-data`. That sink was not built. The public issue adds this line: `details are not published; run the nightly profile locally against the private data`.

## Other workflows that check out the private data repository

Left unchanged. Read from the workflow files, not from a run log.

- `.github/workflows/data-lag.yml`, job `lag`. `actions/checkout` at the same pin, `repository: turbobeest/modelspec-data`, `path: modelspec-data`, `fetch-depth: 0`. That action prints the private commit. The publish step redirects `scripts/data_lag.py` into a temp file and writes `status=` to `GITHUB_OUTPUT`.
- `.github/workflows/rank-api.yml`, jobs `deploy-staging` and `deploy`. The same pin, `path: modelspec-data`, `persist-credentials: false`, gated on `DATA_SPLIT_ENABLED`, `refs/heads/main`, and push, `workflow_dispatch`, or schedule. The action prints the private commit. Later steps pass `--data-dir modelspec-data` to `api/worker/vendor.py`. The memory step writes `both` or `current` to a temp file and cats that word.

`coverage-slo.yml` does not check the private repository out. It runs `python -m scripts.slo workflows --repo turbobeest/modelspec-data --quiet`. The writer stubs name the private workflow URL and do not check the data repository out.

## Round 1 tests

Python 3.14.4 and pytest 9.1.1 from `/Users/terbeest/dev/modelspec/.venv/bin/python`. Git 2.50.1. Serial, `-q -p no:cacheprovider`, no `-n`. Exit codes read directly. No full local suite. No site build.

Red, from the worktree, before the production change. Exit 1. 4 failed in 0.37s.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_accuracy.py::test_public_nightly_report_keeps_counts_and_drops_private_fields \
  tests/test_accuracy.py::test_a_failing_private_nightly_exits_non_zero_with_a_failing_public_form \
  tests/test_accuracy_alert.py::test_the_public_issue_lists_mismatch_and_unreachable_counts_only \
  tests/test_accuracy_alert.py::test_nightly_fetch_does_not_print_the_private_commit_or_the_report \
  --tb=line
```

- `test_public_nightly_report_keeps_counts_and_drops_private_fields`: `AttributeError`, `public_nightly_report` missing.
- `test_a_failing_private_nightly_exits_non_zero_with_a_failing_public_form`: stdout was the full markdown report.
- `test_the_public_issue_lists_mismatch_and_unreachable_counts_only`: the issue body still listed per-draw rows.
- `test_nightly_fetch_does_not_print_the_private_commit_or_the_report`: a step still checked out `turbobeest/modelspec-data` with `actions/checkout`.

Green, same interpreter, after the change. Exit 0. 531 passed in 17.91s.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_accuracy.py tests/test_accuracy_alert.py \
  tests/test_data_workflows.py tests/test_writer_isolation.py
```

`python scripts/accuracy_alert.py` with no `PYTHONPATH`, the workflow's invocation, exited 0 on a counts-only fixture.

## Not observed

- No enable, disable, or dispatch of `accuracy-nightly`.
- No fetch of `turbobeest/modelspec-data`, and no GitHub API call with `MODELSPEC_DATA_TOKEN`.
- No edit, comment, or close of issue 1045. No workflow run or log was deleted.
- No live Actions log was read. The checkout claim is from the action source at the pin.

## Round 2

Work continued on the same branch after merging `origin/main` `317778b484e838cc468728fba51383db3471f4f5` as `470dadf6862774dd5f2c1adb0fb6953bf3f1c37a`. The last code commit before this evidence commit is `7c3390678619de646579e3570e0a1c84fc108409`.

The first run after merge must be a watched manual dispatch. The new fetch step has never run against GitHub. This round did not enable, disable, or dispatch `accuracy-nightly`.

`docs/design/data-split.md` describes `MODELSPEC_DATA_TOKEN` as a fine-grained token with read-only Contents access to `turbobeest/modelspec-data` and nothing else. `docs/method/coverage-slo.md` gives the coverage job Contents: read and Actions: read. A private issue titled "Accuracy nightly failed" with label `alert` would need Issues: write on `turbobeest/modelspec-data` for that token. That issue was not built.

Other public workflows that check out the private data repository, re-read from the workflow files on this branch on 2026-11-13. No live Actions log was read. The claim that `actions/checkout` at pin `11d5960a326750d5838078e36cf38b85af677262` prints the private commit is the same claim as above, from that pin's source.

- `.github/workflows/data-lag.yml`, job `lag`. `actions/checkout` at that pin, `repository: turbobeest/modelspec-data`, `path: modelspec-data`, `fetch-depth: 0`. That action prints the private commit. The publish step redirects `scripts/data_lag.py` into a temp file and writes `status=` to `GITHUB_OUTPUT`.
- `.github/workflows/rank-api.yml`, jobs `deploy-staging` and `deploy`. The same pin, `path: modelspec-data`, `persist-credentials: false`, gated on `DATA_SPLIT_ENABLED`, `refs/heads/main`, and push, `workflow_dispatch`, or schedule. The action prints the private commit. The vendor step passes `--data-dir modelspec-data` to `api/worker/vendor.py`. The memory step writes `both` or `current` to a temp file and cats that word.

A search of `.github/workflows` for `turbobeest/modelspec-data` finds no other `actions/checkout` of that repository. `coverage-slo.yml` does not check it out. It runs `python -m scripts.slo workflows --repo turbobeest/modelspec-data --quiet`. The writer stubs name the private workflow URL and do not check the data repository out. `.github/private-writers/` is not an Actions workflow directory.

### Round 2 commits

- `c7b416cd1c4f1630221d67d818537636d41ce926` private failure prints a fixed stderr line.
- `61ab1a2352e91a54f23b74e2a146b02a83ad98ec` the alert runs without PyYAML, and Python setup runs before the private fetch.
- `1e877975eb8aaf68e369bcb85db1367c045d15b8` the nightly workflow guard is an allow-list.
- `9ee9e8f6a636bde189842a2426030bd9d588379b` a public layer name must be one the code defines.
- `d286580f5be40bf91a37f6f37b303a0219e90980` public counts name what they count.
- `7c3390678619de646579e3570e0a1c84fc108409` the public text names only the output directory.

### Round 2 tests

Same interpreter and versions as round 1. Python 3.14.4, pytest 9.1.1, Git 2.50.1. Confirmed again on 2026-11-13. Serial, `-q -p no:cacheprovider`, no `-n`. Exit codes read directly. Each red command ran from the worktree before that item's production change.

Red P2a. Exit 1. 2 failed, 3 passed in 0.60s. The two private-exception tests still raised.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_accuracy.py::test_a_private_layer_exception_prints_a_fixed_line \
  tests/test_accuracy.py::test_a_private_public_form_exception_prints_a_fixed_line \
  tests/test_accuracy.py::test_without_the_private_flag_a_layer_exception_still_prints_a_traceback \
  tests/test_accuracy.py::test_a_private_run_lets_interrupt_and_system_exit_through \
  --tb=short
```

Red P2b. Exit 1. 3 failed in 0.11s. The missing-report body differed, Python setup was still after the fetch, and the alert import failed when `yaml` was blocked.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_accuracy_alert.py::test_a_run_that_wrote_no_report_still_alerts \
  tests/test_accuracy_alert.py::test_python_is_installed_before_the_private_fetch \
  tests/test_accuracy_alert.py::test_the_alert_builder_runs_when_yaml_cannot_be_imported \
  --tb=line
```

Red P2c. Exit 1. 9 failed in 0.06s. The guard stub accepted seven unlisted commands, a new step, and a new action.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_accuracy_alert.py::test_an_unlisted_command_fails_the_nightly_allow_list \
  tests/test_accuracy_alert.py::test_a_new_nightly_step_fails_the_allow_list \
  tests/test_accuracy_alert.py::test_a_new_nightly_action_fails_the_allow_list \
  --tb=line
```

Red P3a. Exit 1. 2 failed in 0.40s. A hex layer name was printed, and `PUBLIC_LAYER_NAMES` was missing.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_accuracy.py::test_a_hex_layer_name_is_printed_as_layer \
  tests/test_accuracy.py::test_public_layer_names_are_the_names_the_code_defines \
  --tb=line
```

Red P3b. Exit 1. 2 failed in 0.39s. An undetermined-share failure did not name the limit, and a recall fail verdict was counted as a failure.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_accuracy.py::test_an_undetermined_share_failure_names_the_limit \
  tests/test_accuracy.py::test_recall_fail_verdicts_are_not_called_failures \
  --tb=line
```

Red P3c. Exit 1. 2 failed in 0.42s. Stdout and the public issue omitted the output-directory sentence.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_accuracy.py::test_private_stdout_names_only_the_output_directory \
  tests/test_accuracy_alert.py::test_the_public_issue_names_only_the_output_directory \
  --tb=line
```

Green, same interpreter, against `7c3390678619de646579e3570e0a1c84fc108409`, before this evidence commit. Exit 0. 554 passed in 18.70s.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_accuracy.py tests/test_accuracy_alert.py \
  tests/test_data_workflows.py tests/test_writer_isolation.py
```

### Round 2, not observed

- No enable, disable, or dispatch of `accuracy-nightly`. No fetch of `turbobeest/modelspec-data`, and no GitHub API call with `MODELSPEC_DATA_TOKEN`.
- No edit, comment, or close of issue 1045. No workflow run or log was deleted.
- No live Actions log was read.
