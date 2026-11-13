# MODEL-483-D private-read guard

Base `8d74c676a46149207f89da2e4a361d1340d40d29` (`origin/main` when this branch was created).
The commit that adds this file is `git log -1 --format=%H -- docs/evidence/MODEL-483-D-guard.md`.

No workflow file changed. Nothing under `.github/private-writers/` changed. Worker source, wrangler config, switches, and secrets did not change.

## Tools

Python 3.12.3 and pytest 9.2.0 from `/home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python`. Git 2.43.0. Ruff 0.17.4 reports four pre-existing lines over 100 characters in `tests/test_accuracy_alert.py`; none of them are lines this change added.

Focused pytest was serial, with `-q -p no:cacheprovider` and no `-n`. Exit codes were read directly. No local full suite. No site build. The Worker memory probe was not run. This change does not touch snapshot fields, rank rows, or the engine import graph.

## What was already pinned

`tests/test_accuracy_alert.py` had two allow-lists.

`accuracy-nightly.yml` job `accuracy` compared step name, `uses`, and `run`. A new step already failed. A changed `uses` already failed. `shell`, `env`, `with`, `if`, `continue-on-error`, and `working-directory` were not compared.

`data-lag.yml` job `lag`, and `rank-api.yml` jobs `deploy-staging` and `deploy`, pinned every key of every step from the private fetch through the end of the job: name, `uses`, id, and `working-directory` as values, and a hash of `run`, `if`, `env`, and `with`. `shell` and `continue-on-error` were pinned by that key set. Adding either key already failed. Steps before the fetch (the public checkout, and the token check) were not pinned.

The loader was `yaml.BaseLoader`. Aliases were already resolved by the composer. `on` was already a string, not `True`. Merge keys were not resolved: `<<` stayed a literal key.

Workflow `env`, `defaults`, and `permissions`, and job `env`, `defaults`, `container`, `services`, `strategy`, `runs-on`, `permissions`, and `environment`, were not pinned.

## Red

Same interpreter, before the guard consulted those fields. Exit 1. 100 failed, 91 passed, in 1.67s. Each failure was `assert [] == [<the review message for that workflow>]`.

```bash
env PYTHONPATH=$PWD /home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_accuracy_alert.py --tb=line
```

Already returning the review message, so those cases passed in this run:

- On `data-lag.yml` and both rank deploy jobs: `step-shell`, `step-env`, `step-if`, `step-continue-on-error`, and `step-working-directory` on the fetch step.
- On `accuracy-nightly.yml`: `uses-tag` on the checkout, and a step inserted before the fetch (`insert-github-env`, `insert-bash-env`, `insert-hooks-path`, `insert-git-alias`).
- `on` stayed a string on all three files.
- Changing `concurrency` or `timeout-minutes` stayed free.
- Editing env on a job that does not read the private repository stayed free.
- A later job that `needs` the guarded job and does not download an artifact stayed free.

The merged `bash -x {0}` shell was visible on the loaded job. The guard still returned no problem. The same was true for workflow and job `defaults`, `env`, `container`, `services`, `strategy`, `runs-on`, `permissions`, and `environment`; for `ACTIONS_STEP_DEBUG` and `ACTIONS_RUNNER_DEBUG` on the workflow `env`; for `persist-credentials` on the checkout; for a job-level `uses` on `@main` with the steps left in place; for a step inserted before the fetch on data-lag and both rank jobs; and for a later job that downloads an artifact.

## What is pinned now

`context_guard_problems` is the allow-list the two match tests call. A miss returns the same message as before: the nightly message for `accuracy-nightly.yml`, and the job message for data-lag and the rank deploy jobs.

The loader resolves anchors and `<<` merge keys, and it still leaves scalars as strings, so `on` is not `True`. The three workflow files load equal to `BaseLoader`. A merge that sets `defaults.run.shell` to `bash -x {0}` fails the guard on each guarded job.

Pinned for each guarded job, including absence:

- Workflow `on`, `env`, `defaults`, and `permissions`. `on` is pinned because the triggers decide which events, and which `inputs`, reach the steps.
- Job `env`, `defaults`, `container`, `services`, `strategy`, `runs-on`, `permissions`, `environment`, and `outputs`. `environment` is included because that name selects variables that are not in the file. `deploy` names `production`. The other guarded jobs set none.
- Every step of the job, not only the tail. Checkout `with`, a step `shell`, and a step inserted before the fetch all fail. The old tail pin is unchanged.
- Every `uses` on the job or its steps must be a full commit SHA (`[0-9a-f]{40}`). A docker reference must carry `@sha256:` and 64 hex digits. A local `./` path is exempt: it has no ref and moves with this commit. There is no `.github/actions/` directory. A job-level `uses` of a branch fails even when the steps are unchanged, so updating the step digest cannot legalize a moving ref.

## The four routes closed in round two

A review found four edits that passed round one. Each now fails, on all four guarded jobs, with a case that first checks the edited workflow differs from the original.

1. A new sibling job, or a new workflow file, that uses the token or names the private repository. `test_only_guarded_jobs_may_touch_the_private_repository` scans every workflow under `.github/workflows/` and every `action.yml` under `.github/actions/` (none exists today). Every job and the workflow level of every file other than the guarded jobs, derived from the same `_STEP_PINS` data the guard uses, must hold no key or text that names `modelspec-data` (any spelling of the private repository's name, so the `MODELSPEC_DATA_TOKEN` and `MODELSPEC_DATA_DISPATCH_TOKEN` secrets too), hands on every secret (`secrets: inherit`), dumps `toJSON(secrets)`, or indexes `secrets[...]`.
2. `outputs:` on a guarded job, and any job that reads `needs.<guarded>` beyond `.result`, or dumps `toJSON(needs)`. `test_guarded_job_outputs_are_pinned`. No guarded job has `outputs` today, so the pin is absence.
3. An unknown key. `test_unknown_workflow_or_job_key_fails_closed`. Every key at workflow level and at guarded-job level is either pinned or in the free list below. Anything else fails, including a misspelt key.
4. A download of artifacts. `test_artifact_downloads_from_guarded_workflows_are_refused`. In a workflow that has a guarded job, any other job, with or without `needs`, whose text names a download-artifact action, `gh run download`, an `/artifacts` API path, or the artifact calls of `actions/github-script`, fails. A guarded job that gains an upload-artifact step still fails the step pin; a case keeps that. A sibling job that only uploads stays free.

Free keys, one reason each. Everything else at those two levels fails.

| Level | Key | Why free |
| --- | --- | --- |
| workflow | `name` | Display only. Its expressions see no secret and no step output. |
| workflow | `run-name` | Display only. Its expressions see the `github`, `inputs`, and `vars` contexts, not steps. |
| workflow | `concurrency` | Orders or cancels runs. It does not change what a step prints. |
| job | `name` | Display only. |
| job | `if` | Can only skip the job, which prints nothing. |
| job | `needs` | Orders jobs. A pinned step that read a `needs` context would carry that text in its pin. |
| job | `timeout-minutes` | Ends a run early. |
| job | `concurrency` | Orders or cancels runs. |

Pinned, not free: workflow `on`, `env`, `defaults`, `permissions`; job `env`, `defaults`, `container`, `services`, `strategy`, `runs-on`, `permissions`, `environment`, `outputs`. Not named, so failing when present: job `uses`, `with`, `secrets`, `continue-on-error`, and any other key. A job-level `uses` also fails the full-SHA rule.

Jobs on `main` that are not guarded and name the private repository today. Nothing was changed; each is pinned in `_private_reference_exceptions()` as the exact set of keys and lines, so a new line, a new job, or a removed line fails the test.

| File | Job | What it names |
| --- | --- | --- |
| `coverage-slo.yml` | `private-health` | `MODELSPEC_DATA_TOKEN` in a step env and the repository name in its command. Prints nothing and uploads nothing, by its own comment. |
| `coverage-slo.yml` | `release-counts` | `MODELSPEC_DATA_TOKEN` in a step env. Has `outputs:` (validated counts) that `report` reads. That job is not guarded, so rule 2 does not reach it. |
| `curation-gate.yml`, `release-signals-gate.yml`, `release-watch.yml` | `dispatch`, `pending`, `dispatch` | `MODELSPEC_DATA_DISPATCH_TOKEN` and `gh workflow run ... --repo` the private repository. A dispatch reads no private data. |
| `curation-benchmarks.yml`, `daily-research.yml`, `leaderboard-refresh.yml`, `price-reread.yml`, `release-signals.yml`, `speed-probe.yml` | `moved` | A step name that holds the private workflow's URL. The step runs `true`. |

Left free, and tested: the free keys above. Workflow-level `on` is pinned, so a cron or trigger edit on a guarded workflow now fails the test.

The one sentence for a future editor: if one of these tests fails, a workflow edit may have changed what a private-reading job prints or where it goes; read every step of that job and every job that reads it, and then update the pinned data in `tests/test_accuracy_alert.py` in the same pull request.

## `uses` in a guarded job

Each one is `owner/name@` plus 40 hex digits. None is a tag, a branch, or a docker image.

| Job | `uses` |
| --- | --- |
| `accuracy-nightly.yml` `accuracy` | `actions/checkout@11d5960a326750d5838078e36cf38b85af677262`, `actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065` |
| `data-lag.yml` `lag` | those two, and `peter-evans/create-pull-request@22a9089034f40e5a961c8808d113e2c98fb63676` |
| `rank-api.yml` `deploy-staging` and `deploy` | `actions/checkout@11d5960a326750d5838078e36cf38b85af677262`, `actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065`, `astral-sh/setup-uv@d0cc045d04ccac9d8b7881df0226f9e82c39688e`, `actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020` |

## Review duty

Out of reach of a static test of the workflow file:

- Anything a static test of the workflow file cannot see. The image behind `runs-on: ubuntu-latest`. The label is pinned. The image moves.
- Repository, organization, and environment variables and secrets, and an Actions re-run that turns debug logging on. `ACTIONS_STEP_DEBUG`, `ACTIONS_RUNNER_DEBUG`, `GIT_TRACE`, and `BASH_ENV` can be set there without a workflow edit. The `production` environment name on `deploy` is pinned. Its values are not.
- The programs the pinned steps run, including `scripts/accuracy.py`, `scripts/accuracy_alert.py`, `scripts/data_lag.py`, and `api/worker/vendor.py`. A change there is not a workflow-text edit.
- A workflow triggered by `workflow_run`, or an API call from outside Actions, that reads a run's artifacts: a guarded job uploads none, so there is nothing to read, but that stays true only while the step pin holds.
- A local `./` action, if one is added later. The step pin fails until it names that path. After that, edits under the path need a review. None exist today.

## Green

Same interpreter. Round two went red first: 125 failed, 221 passed before the guard was extended, every failure on an empty problem list for a case whose edit had been applied. After the guard: exit 0, 346 passed in 3.3s. The four named tests have 14, 28, 48, and 44 parametrised cases.

```bash
env PYTHONPATH=$PWD /home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_accuracy_alert.py --tb=line
```

`tests/test_writer_isolation.py`, same flags. Exit 0. 288 passed, 8 skipped.

## Not observed

- No enable, disable, or dispatch of any workflow. No Actions log was read.
- No fetch of the private data repository, and no use of its token.
- No workflow, script, or Worker change. `tests/shard_durations.json` was not changed. This edit adds no test module.
- CI is the full gate and is checked after the push.
