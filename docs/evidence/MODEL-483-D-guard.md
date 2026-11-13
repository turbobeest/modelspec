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

- Workflow `env`, `defaults`, and `permissions`.
- Job `env`, `defaults`, `container`, `services`, `strategy`, `runs-on`, `permissions`, and `environment`. `environment` is included because that name selects variables that are not in the file. `deploy` names `production`. The other guarded jobs set none.
- Every step of the job, not only the tail. Checkout `with`, a step `shell`, and a step inserted before the fetch all fail. The old tail pin is unchanged.
- Every `uses` on the job or its steps must be a full commit SHA (`[0-9a-f]{40}`). A docker reference must carry `@sha256:` and 64 hex digits. A local `./` path is exempt: it has no ref and moves with this commit. There is no `.github/actions/` directory. A job-level `uses` of a branch fails even when the steps are unchanged, so updating the step digest cannot legalize a moving ref.

A different job that `needs` the guarded job and whose steps use `download-artifact` or `gh run download` fails. A job that only `needs` it does not.

Left free, and tested: workflow and job `concurrency`, and `timeout-minutes`. Also left free, because they do not change what a running step prints: workflow `on` and `name`, and job `if`, `name`, `needs`, and `outputs`.

## `uses` in a guarded job

Each one is `owner/name@` plus 40 hex digits. None is a tag, a branch, or a docker image.

| Job | `uses` |
| --- | --- |
| `accuracy-nightly.yml` `accuracy` | `actions/checkout@11d5960a326750d5838078e36cf38b85af677262`, `actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065` |
| `data-lag.yml` `lag` | those two, and `peter-evans/create-pull-request@22a9089034f40e5a961c8808d113e2c98fb63676` |
| `rank-api.yml` `deploy-staging` and `deploy` | `actions/checkout@11d5960a326750d5838078e36cf38b85af677262`, `actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065`, `astral-sh/setup-uv@d0cc045d04ccac9d8b7881df0226f9e82c39688e`, `actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020` |

## Review duty

Out of reach of a static test of the workflow file:

- The image behind `runs-on: ubuntu-latest`. The label is pinned. The image moves.
- Repository, organization, and environment variables and secrets, and an Actions re-run that turns debug logging on. `ACTIONS_STEP_DEBUG`, `ACTIONS_RUNNER_DEBUG`, `GIT_TRACE`, and `BASH_ENV` can be set there without a workflow edit. The `production` environment name on `deploy` is pinned. Its values are not.
- The programs the pinned steps run, including `scripts/accuracy.py`, `scripts/accuracy_alert.py`, `scripts/data_lag.py`, and `api/worker/vendor.py`. A change there is not a workflow-text edit.
- A local `./` action, if one is added later. The step pin fails until it names that path. After that, edits under the path need a review. None exist today.

## Green

Same interpreter, after the pin. Exit 0. 200 passed in 1.46s.

```bash
env PYTHONPATH=$PWD /home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_accuracy_alert.py --tb=line
```

`tests/test_writer_isolation.py`, same flags. Exit 0. 288 passed, 8 skipped, in 9.22s.

```bash
env PYTHONPATH=$PWD /home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_writer_isolation.py --tb=line
```

## Not observed

- No enable, disable, or dispatch of any workflow. No Actions log was read.
- No fetch of the private data repository, and no use of its token.
- No workflow, script, or Worker change. `tests/shard_durations.json` was not changed. This edit adds no test module.
- CI is the full gate and is checked after the push.
