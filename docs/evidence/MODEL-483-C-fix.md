# MODEL-483-C execution evidence

Base `618b0a8a34b778829b409e570eb63bc455072083` (`origin/main`, the merge of pull request 1066).
Worktree `/home/turbobeest/dev/04-modelspec/worktrees/model-483-c`, branch `model-483-c`.

This file's latest commit is `git log -1 --format=%H -- docs/evidence/MODEL-483-C-fix.md`.

No workflow file changed. Nothing under `.github/private-writers/` changed. Worker source, wrangler config, switches, and secrets did not change. `decision/snapshot.py` did not change. Printing in `api/worker/vendor.py` and the git-failure path in `scripts/data_lag.py` did.

## Tools

Python 3.12.3 and pytest 9.2.0 from `/home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python`. Git 2.43.0.

Focused pytest was serial, with `-q -p no:cacheprovider` and no `-n`. Exit codes were read directly. The private vendor runs went through `ops/tools/heavy.sh`. No local full suite. No site build. The Worker memory probe was not run. This change does not touch snapshot fields, rank rows, or the engine import graph, and it does not move the 120 MiB, 115 MiB, or 100 ms gates.

## Inventory

Counts and fixed words only. No line from an Actions log is copied. The table is what each step writes after this change. Jobs `memory` and `bundle` do not fetch the private repository.

| Job | Step | What the log gets | From the private directory |
| --- | --- | --- | --- |
| `data-lag.yml` `lag` | Read the private data with its history | Nothing. Git stdout and stderr are discarded. | No |
| `data-lag.yml` `lag` | setup-python | Nothing from the private directory. | No |
| `data-lag.yml` `lag` | Publish the image as of today minus nine months | The status word, via `GITHUB_OUTPUT`. Script stdout goes to `$RUNNER_TEMP/lag-status.json`. A git failure prints one fixed stderr line: the subcommand name and the exit code. No arguments, no git stderr. | The status word. `source_commit` stays in that temp JSON and, when the image is published, in `data-image.json`. That file use is the existing owner decision. It is not a log line. |
| `data-lag.yml` `lag` | Open the pull request | The pull-request action's own log. It runs only when the status is `published`. It does not read the private directory. | No |
| `rank-api.yml` `deploy-staging` and `deploy` | Read the private data | Nothing. Git stdout and stderr are discarded. | No |
| `rank-api.yml` `deploy-staging` and `deploy` | setup-python, setup-uv, setup-node | Nothing from the private directory. | No |
| `rank-api.yml` `deploy-staging` and `deploy` | Vendor the scorer into the Worker bundle | The coverage sentence: three counts (`known`, `explicit null`, `gap`). When identifiers would have followed, the log names `modelspec-private-build-detail.txt` and the identifiers go in that file under the runner temp directory. No step uploads it. The sentence is still forwarded twice. `uncited policy rows:` plus a count, when that guard fires. On failure: the data-dir argument and the exception category. | The three counts. The uncited-row count when the guard fires. |
| `rank-api.yml` `deploy-staging` and `deploy` | Check private steady bundle memory against 120 MiB | The word `both` or `current`. | That word. |
| `rank-api.yml` `deploy` | Smoke-test api.modelspec.dev | A path, a status, and a byte count, as previously recorded. Not changed. | Not the private git directory. |

Later deploy, secret, and probe steps were not changed. They read the vendored bundle or the live host.

Still printed, and derived from private data: the three coverage counts, the uncited-row count when raised, the word `both` or `current`, and the lag status word. The detail filename is a fixed name. Not printed: lab slugs, record ids, device ids, source URLs, paths of files inside the private directory, git arguments, git stderr, and private commit SHAs.

## Coverage sentence

Red, before the print change, from the worktree. Exit 1. 19 failed, 1 passed in 0.61s. `test_public_vendor_stdout_stays_the_file_count` passed.

```bash
env PYTHONPATH=$PWD /home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_vendor_private_log.py \
  tests/test_data_lag.py::test_a_failing_git_prints_the_subcommand_and_the_exit_code \
  tests/test_accuracy_alert.py::test_a_changed_private_job_step_needs_a_review \
  --tb=short
```

- `test_private_vendor_stderr_keeps_counts_and_drops_the_marker`: the fixture slug was on stderr, in the coverage sentence and in the failed-path line.
- `test_private_coverage_handler_prints_counts_and_the_detail_name`: the fixture slug was on stderr, in the coverage sentence and in a mismatch warning.
- `test_a_private_system_exit_prints_the_category_and_not_the_marker` was added with the fix. It was not in the red run.

With `--data-dir`, a coverage sentence on stdout or stderr keeps the three counts. An identifier tail is appended to `modelspec-private-build-detail.txt` and the log prints that name. The same path stashes any other snapshot log line, a modality `SystemExit` message, and a private file path from an exception. The public path, without `--data-dir`, still prints `vendored <count> files into <out>` and still prints a traceback. `uncited policy rows:` stays a count. A failure still names the data-dir argument the command was given, which is the directory itself, and the exception class.

## Git failure

`test_a_failing_git_prints_the_subcommand_and_the_exit_code` was in the red run above. The uncaught `CalledProcessError` named `git log` and included the marker argument. Exit status 23. It was not `SystemExit`.

After the wrap, the same test exits 23 with stderr exactly `git log failed with exit code 23` and empty stdout. The marker is in neither stream. A successful git call is unchanged. The publish step's redirect is unchanged.

A private SystemExit returns an integer code unchanged and returns 0 for None, and any other value exits 1 on the fixed line with the message on neither stream; a missing git binary prints that same kind of fixed line and exits non-zero.

## Allow-list

`test_a_changed_private_job_step_needs_a_review` was in the red run above. Sixteen cases. Dropping the publish redirect, `working-directory: modelspec-data` plus `git log`, and appending `git show`, `tail`, or `grep` returned no problem. A new upload step returned the nightly message (`this workflow runs...`) rather than `this job runs in a public repository against private data; a reviewer must check every output of a changed step`.

The pin now covers every step from the private fetch through the end of the job: step name, `uses`, id, `working-directory`, and a hash of `run`, `if`, `env`, and `with`. An `actions/checkout` of `turbobeest/modelspec-data` still fails. Unmodified workflow files return no problem. The nightly allow-list and its message are unchanged.

## Green

Same interpreter, after the change, serial, no `-n`. Exit 0. 428 passed, 8 skipped in 14.21s. That run is the focused tests, the vendor tests, and `tests/test_writer_isolation.py`.

`tests/test_vendor_private_log.py` is a new module. The suite requires a measured duration for at least 95 percent of test modules. The first CI shard run failed at 365/385. A junit run of this file alone is 0.181 seconds, recorded in `tests/shard_durations.json`. That is the only generated file this change adds a weight to.

```bash
env PYTHONPATH=$PWD /home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_vendor_private_log.py tests/test_data_lag.py tests/test_accuracy_alert.py \
  tests/test_private_serving.py::test_vendor_diagnostics_keep_public_tracebacks_but_hide_private_values \
  tests/test_private_serving.py::test_private_policy_guard_reports_only_the_count \
  tests/test_worker_vendor_imports.py tests/test_tier_policy_bundle.py tests/test_worker_bundle.py \
  tests/test_snapshot_successor_vendor.py tests/test_writer_isolation.py \
  --tb=line
```

## Vendor output files

Public frozen image, `python api/worker/vendor.py --out <dir>` with no `--data-dir`, before the print change and after it. 130 files each. Only-before 0. Only-after 0. Differ 0. Identical: yes.

Private data directory, read-only, `--data-dir /home/turbobeest/dev/04-modelspec/modelspec-data`, both runs through `ops/tools/heavy.sh` with the same throwaway `MODELSPEC_SNAPSHOT_KEY`. 131 files each. Only-before 0. Only-after 0. 130 files byte-identical, including both decision snapshots and both vocabularies inside `bundled_data.py`. `bundled_data.py` is the one file that differs. Inside it, `/api/policy/catalogue.json`, `/api/rank/candidates.json`, and `/api/rank/hardware.json` each differ by one `built_at` value. That field is the wall clock in `pipeline/export.py` and this change does not write it. No other field differs. Identical: yes for every file except that clock field in `bundled_data.py`.

The private run's stderr matched the counts-only pattern. The detail filename was on stderr. The detail file was not read and was deleted.

## Not observed

- No enable, disable, or dispatch of any workflow. No Actions log was read for this change.
- No fetch of `turbobeest/modelspec-data` from a workflow, and no use of `MODELSPEC_DATA_TOKEN`.
- No private commit SHA and no per-card value is recorded here.
- The first real rank-api run of this print path is the next deploy on `main`. The first real data-lag run is the next Monday schedule or a dispatch on `main`. This change does not dispatch either workflow.
