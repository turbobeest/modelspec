# MODEL-483 other public workflows

Base `b374f1ed8be60c8e2d603490a24e882515ca0cd4` (`origin/main` when this branch was created).
Worktree `/home/turbobeest/dev/04-modelspec/worktrees/model-483-b`, branch `model-483-b`.

Inventory below was written from the workflow files and from public Actions logs before any workflow edit. Field kinds only. No log line is copied. No private commit value is recorded.

There is no `.github/actions/` directory, so the silent fetch is repeated. It is not a composite action.

## Inventory

A step "reads the private repository" when it checks that repository out, clones it, calls its API, or passes it as a data root. Writer stubs that only name a private workflow URL do not read it.

### Already silent: `accuracy-nightly.yml`

Job `accuracy`, step `Read private verification records`. Shallow fetch of `refs/heads/main` into `.accuracy-private`, output discarded, token only on `http.extraheader`. The public `actions/checkout` is this repository.

Public log read: scheduled run `43379646594` on `main` (2026-11-13, conclusion failure). The private fetch step printed no 40-hex value. The only `git log -1 --format=%H` in the log is the public checkout. The following accuracy step exited non-zero; that failure is outside this change. Prints the private commit: no. Not changed here.

### `data-lag.yml` job `lag`

`actions/checkout` pin `11d5960a326750d5838078e36cf38b85af677262`, `repository: turbobeest/modelspec-data`, `path: modelspec-data`, `fetch-depth: 0`. The file does not set `ref`, `persist-credentials`, sparse paths, submodules, or LFS. The job `if` is `vars.DATA_SPLIT_ENABLED == 'true'`. Triggers are schedule and `workflow_dispatch` only.

Public logs read, all scheduled successes on `main`: `42566168331` (2026-11-09), `41392827749` (2026-11-02), `40273917394` (2026-10-26).

Observed checkout shape, same in each log: `fetch-depth: 0`, `persist-credentials: true` (the action default), `fetch-tags: false`, `lfs: false`, `submodules: false`, no sparse checkout, and the ref actually checked out was `refs/remotes/origin/main`.

Sinks from that private checkout:

- Log. Prints the private commit: yes. The action runs `git log -1 --format=%H` and the next line is a 40-hex value, after `Syncing repository` for the private repository. Confirmed in all three logs.
- Log. Prints other private data: yes. `fetch-depth: 0` lists every remote branch. Line counts of those branch announcements were 110, 95, and 93. Kind: private branch names. The names are not recorded here.
- Step `Publish the image as of today minus nine months`. Runs `scripts/data_lag.py --private modelspec-data` with stdout redirected to a temp file, then writes `status=` to `GITHUB_OUTPUT`. The script's JSON includes a commit field. None of the three logs contained a `source_commit` field or a JSON object from that step. The pull-request step did not run.
- Step `Open the pull request` (`peter-evans/create-pull-request`). Runs only when `status` is `published`. It commits public data paths plus `data-image.json`. It does not read the private directory itself.

`scripts/data_lag.py` needs the private commit. It walks `git rev-list --first-parent HEAD` and writes `source_commit` into `data-image.json` on the public `data-lag/image` branch (see `docs/design/data-split.md`). That use stays. Where the value ends up: a file on a public pull request, not the Actions log in the runs above. Whether that commit may stay in that public file is the owner's existing decision. This change does not remove it. The fix is the log only.

Later steps that read the private directory: the publish step (`--private modelspec-data`). The pull-request step reads the public paths the publish step updated.

### `rank-api.yml` jobs `deploy-staging` and `deploy`

`actions/checkout` at the same pin, `path: modelspec-data`, `persist-credentials: false`, no `fetch-depth` (the action default is 1), no `ref`, no sparse paths. Step `if`: `DATA_SPLIT_ENABLED`, `refs/heads/main`, and event `push`, `workflow_dispatch`, or `schedule`. `deploy` runs on a push to `main`, or on `workflow_dispatch` or schedule on `main` when the split is on. `deploy-staging` runs on `workflow_dispatch` only. Neither runs on `pull_request`. Jobs `memory` and `bundle` do not check the private repository out.

Public logs read, all successes on `main`: `43424799605` (2026-11-13 schedule), `43378696675` (2026-11-13 schedule), `43374412140` (2026-11-13 push). Each ran `Deploy the rank Worker`. `deploy-staging` did not run in these three.

Observed private checkout: `fetch-depth: 1`, `persist-credentials: false`, `fetch-tags: false`, `lfs: false`, `submodules: false`, no sparse checkout, ref checked out `refs/remotes/origin/main`. One branch announcement, and that ref was `main`.

Sinks:

- Log. Prints the private commit: yes. `git log -1 --format=%H` then a 40-hex line, after the private `Syncing repository`. Confirmed in all three logs.
- Step `Vendor the scorer into the Worker bundle`. Passes `--data-dir modelspec-data` when the directory exists. The step also prints a coverage sentence from `JurisdictionCoverage.__str__` (`decision/snapshot.py`), forwarded by `api/worker/vendor.py`. Fixed words are counts (`known`, `explicit null`, `gap`). In each of the three logs the sentence also carried two alphabetic tokens that are not those fixed words, and the sentence appeared twice. Kind: identifiers. Stopped. Silencing it means changing Worker code or the deploy step's diagnostics. This ticket does not change Worker code, `wrangler.jsonc`, or what the deploy publishes.
- The private commit is not a deploy stamp. `BUILD_COMMIT` is `GITHUB_SHA` (this repository). `build.commit` comes from `git rev-parse HEAD` on the overlay, whose `.git` is the public checkout (`pipeline/data_source.py`). The private tree is an input to the bundle. The fetch must keep that tree. The commit value is not removed from anywhere because this job does not put it in a deployed file.
- Step `Check private steady bundle memory against 120 MiB` reads the vendored bundle, writes `both` or `current` to a temp file, and cats that word.
- Smoke and the OpenAPI probe run after deploy. In the latest schedule log the smoke section had no 40-hex value. `check_private_rank.py` prints a path, a status, and a byte count. The probe prints requests built from the committed spec. Not changed: that is deploy behavior.

Later steps that read the private directory: the vendor step (`--data-dir modelspec-data`). The memory, deploy, secret, and smoke steps read the vendored bundle or the live host, not the private git directory.

A failed fetch must fail the job before `Deploy` / `Deploy staging`. The replacement uses `set -euo pipefail`, does not use `|| true`, and sets no `continue-on-error`. Those deploy steps have no `if` that runs on failure.

No pull-request job runs the private fetch. `memory` and `bundle` run on a pull request and do not use the private directory. The first real run of the rank fetch is the next deploy on `main` (the merge of this pull request, or the six-hour schedule) and must be watched. The first real run of the data-lag fetch is the next Monday schedule or a dispatch on `main`. This change does not dispatch either workflow.

### `coverage-slo.yml`

Does not check the private repository out.

- Job `private-health`. Public checkout, then `python -m scripts.slo workflows --repo turbobeest/modelspec-data --quiet`. Log read: scheduled run `43403363500` (2026-11-13, conclusion failure). No private `Syncing repository`. The command's own output was empty. The step then ended with Actions' fixed completion sentence (the words are the usual process-completed sentence; no private repository name, no workflow file name, no 40-hex). Prints the private commit: no.
- Job `release-counts`. Public checkout, then `python -m scripts.slo release-counts --github-output`. Command output in that log was empty. The job output is the validated counts handoff. Prints the private commit: no. Kind of private data that leaves the job: numeric counts only, by the existing guard in `tests/test_data_workflows.py`.
- Job `report` has no private token. It publishes the public coverage report (step summary, artifact, issues, Pages). Not a private checkout.

Not changed.

### Dispatch only

`curation-gate.yml`, `release-signals-gate.yml`, and `release-watch.yml` run `gh workflow run <workflow> --repo turbobeest/modelspec-data --ref main`. No checkout, no clone, no data root. Logs were not read. The command text names the repository and the ref. Not changed.

These public files name a private workflow URL and run `true`: `daily-research.yml`, `price-reread.yml`, `speed-probe.yml`, `curation-benchmarks.yml`, `leaderboard-refresh.yml`, `release-signals.yml`. They do not read the repository. `data-freeze.yml` names it in a comment and checks this repository only.

`.github/private-writers/` is not an Actions workflow directory and was not edited.

## Change

There is no `.github/actions/` directory, so the silent fetch is repeated in three steps. It is not a composite action.

`data-lag.yml` job `lag`, step `Read the private data with its history`, replaces the private `actions/checkout`. Directory `modelspec-data` before and after. Before: `fetch-depth: 0`, credential persisted (the action default), ref checked out `refs/remotes/origin/main`, no sparse paths. After: `git fetch` of `refs/heads/*` with no `--depth`, then a detached checkout of `origin/main`. The token is `http.extraheader` on that fetch only. It is not written with `git config`. Every git line discards stdout and stderr. Later reader: `Publish the image as of today minus nine months` (`--private modelspec-data`). `Open the pull request` reads public paths only.

`rank-api.yml` jobs `deploy-staging` and `deploy`, step `Read the private data`, replace the private `actions/checkout`. Directory `modelspec-data` before and after. Before: depth 1, `persist-credentials: false`, ref checked out `refs/remotes/origin/main`, no sparse paths, same step `if`. After: `--depth=1` of `refs/heads/main`, then a detached checkout of `origin/main`. The token is `http.extraheader` on that fetch only. Later reader: `Vendor the scorer into the Worker bundle` (`--data-dir modelspec-data` when the directory exists). The memory, deploy, secret, and smoke steps read the vendored bundle or the live host. A skipped fetch leaves the directory absent, as a skipped checkout did. Detached `HEAD` versus branch `main` does not change the files those steps read.

A failed fetch fails the step. Each script starts with `set -euo pipefail`, has no `|| true`, and sets no `continue-on-error`. The publish step and both deploy steps have no `if` that runs on failure, and they come after the fetch.

`scripts/data_lag.py` still writes `source_commit` into `data-image.json` on the public `data-lag/image` branch. That use stays. Where the value ends up: a file on a public pull request when the publish step changes the image. The three logs above did not show the field. Whether that commit may stay in that public file is the owner's decision. Stopped.

The vendor coverage sentence can still carry identifier words besides the fixed counts. Silencing it would change Worker code or the deploy step's diagnostics. Stopped. The deploy artifact is unchanged by leaving it.

`tests/test_private_serving.py` is a companion update. `test_private_workflow_jobs_have_main_event_gates_and_no_artifacts` used to find an `actions/checkout` of `turbobeest/modelspec-data`. It now requires that checkout to be absent, and it binds the same main, `DATA_SPLIT_ENABLED`, push, and `workflow_dispatch` gate to the silent fetch, plus `set -euo pipefail`, no `|| true`, no `continue-on-error`, `http.extraheader`, no `git config`, and a redirect on every git line. `deploy-sites.yml` still has neither a private checkout nor a fetch, and the test still asserts that. The assertion was not weakened.

The allow-list in `tests/test_accuracy_alert.py` pins the three step names and the normalised `run` text (and the rank step `if`). A step that reads the private directory with `git log`, `git rev-parse`, `cat`, `head`, or `jq`, or that uploads an artifact, fails the test.

## Tests

Python 3.12.3, pytest 9.2.0, from `/home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python`. Git 2.43.0. Serial, `-q -p no:cacheprovider`, no `-n`. Exit codes read directly. No full local suite.

Red, from the worktree, before the workflow edit. Exit 1. 3 failed in 1.02s.

```bash
env PYTHONPATH=$PWD /home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_accuracy_alert.py::test_data_lag_and_rank_private_fetches_match_the_allow_list \
  tests/test_accuracy_alert.py::test_private_fetches_fail_closed_before_publish_or_deploy \
  tests/test_private_serving.py::test_private_workflow_jobs_have_main_event_gates_and_no_artifacts \
  --tb=line
```

- `test_data_lag_and_rank_private_fetches_match_the_allow_list`: the three jobs were not on the allow-list (`data-lag.yml:lag`, `rank-api.yml:deploy-staging`, `rank-api.yml:deploy`).
- `test_private_fetches_fail_closed_before_publish_or_deploy`: the named fetch step did not exist (`StopIteration`).
- `test_private_workflow_jobs_have_main_event_gates_and_no_artifacts`: `rank-api.yml` still checked out `turbobeest/modelspec-data` with `actions/checkout`.

Green, same interpreter, after the workflow edit. The seven-file run exited 1: 623 passed, 8 skipped, 14 failed, in 483.47s. All 14 failures were `test_private_deploy_requires_memory_for_both_periods`. The shell reported `python: command not found`. This machine has `python3` and no `python` on `PATH`. The memory step and both deploy steps are byte-identical to `b374f1ed8be60c8e2d603490a24e882515ca0cd4`. Rerun of that test with the project interpreter's directory on `PATH` exited 0: 14 passed in 1.09s.

```bash
env PYTHONPATH=$PWD /home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_accuracy_alert.py tests/test_data_workflows.py tests/test_data_lag.py \
  tests/test_private_serving.py tests/test_writer_isolation.py \
  tests/test_ci_workflows.py tests/test_worker_memory.py
```

```bash
env PYTHONPATH=$PWD PATH="/home/turbobeest/dev/04-modelspec/modelspec/.venv/bin:$PATH" \
  /home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_worker_memory.py::test_private_deploy_requires_memory_for_both_periods
```

This file is committed with the workflow change. `git log -1 --format=%H -- docs/evidence/MODEL-483-other-public-workflows.md` is that commit.

## Not observed

- No enable, disable, or dispatch of any workflow. No workflow run or log was deleted.
- No fetch of `turbobeest/modelspec-data`, and no use of `MODELSPEC_DATA_TOKEN`.
- Logs of the dispatch-only workflows were not read. The nightly log and the checkout workflows' logs were read, at most three each, before the edit.
- No change under `.github/private-writers/`, and no change to Worker code, wrangler config, production switches, or secrets.
- No pull-request job runs the new fetch. The first real rank-api run is the deploy on `main` after merge and must be watched. The first real data-lag run is the next Monday schedule or a dispatch on `main`.
