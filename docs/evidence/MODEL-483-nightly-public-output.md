# MODEL-483 nightly public output

Base `a2e029b53004a9d7575d84fde05d6c378fafd8fa` (`origin/main` when this branch was created).
Worktree `/Users/terbeest/dev/worktrees/model-483-log`, branch `model-483-log`.

The evidence commit is the one that adds this file. Read its SHA with `git log -1 --format=%H -- docs/evidence/MODEL-483-nightly-public-output.md`.

## What the public sinks carry

`public_nightly_report` in `scripts/accuracy.py` is the only text a private nightly writes to stdout, and the only report text `scripts/accuracy_alert.py` puts in the public issue. Each layer line is a status, a yes/no gate, and counts. The job writes no step summary and uploads no artifact. The full report is still written under the output directory for a local run.

A failed layer still prints FAIL. `main` still returns 1 when `report.status` is `fail`.

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

## Tests

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
