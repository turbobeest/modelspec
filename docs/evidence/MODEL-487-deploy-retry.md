# MODEL-487 deploy retry and deploy alert

Part of MODEL-487. Base: `origin/main` when the branch `model-487-deploy-retry` was created. No Worker source, wrangler configuration, secret, switch, or file under `.github/private-writers/` changed. Nothing was deployed, dispatched, or rerun, and no issue or label was created.

## Why

On 2026-11-13 the job "Deploy the rank Worker" failed three times at its `Deploy` step with a transient Cloudflare API error (code 10013 twice, "malformed response" once). Each time a rerun of the failed job passed with no change. While the job is red production serves the previous commit, and nothing told anyone: no other workflow reads this one.

## How the deploy ran, and what it printed

Before: step `Deploy` in job `deploy` (private-reading, pinned by `tests/test_accuracy_alert.py`) ran one command in `api/worker`: `uv run --project . pywrangler deploy --var "BUILD_COMMIT:${GITHUB_SHA}"`. It is a command, not a third-party action. Its stdout and stderr went straight to the log. On failure the log therefore held the tool's own error text (for example the Cloudflare API path and code) and the step exited non-zero. No `echo` in the step.

After: the same command runs inside `scripts/deploy_retry.py` (standard library only), called as `python3 "$GITHUB_WORKSPACE/scripts/deploy_retry.py" -- <the same command>`. The step keeps its name, its `working-directory`, and has no `if`, `env`, `shell`, or `continue-on-error`.

## What the changed step can print

| # | Line | Kind | When |
| --- | --- | --- | --- |
| 1 | `deploy attempt 1 of 3 failed with a transient API error; retrying` | fixed | first attempt failed with a transient error |
| 2 | `deploy attempt 2 of 3 failed with a transient API error; retrying` | fixed | second attempt failed with a transient error |
| 3 | the deploy tool's combined stdout and stderr of the LAST attempt | tool output | the attempt that passed, or the one that ended the run |
| 4 | `::error::deploy-failure-class=transient-exhausted` or `=rejected` or `=unknown` | fixed (one of three) | the run ends red |
| 5 | `deploy command could not start` | fixed | the command cannot be launched (an `OSError`; its text is not printed) |

Line 3 is the one place tool output still prints. It prints what the old step printed for a single attempt, and nothing from earlier attempts, whose text is captured, classified, and dropped. It is kept, instead of replaced by a fixed line, because the reason for a rejection (a size or binding error) is what an operator needs, and the old step already printed it. A reviewer who wants a stricter rule can drop line 3 on failure in `run()`; the alert and the class do not depend on it.

Why none of lines 1, 2, 4, 5 can carry private data: they are string literals or built from the integer attempt number (1 or 2) and one of three constant class names. None is formatted from the tool's output, an environment variable, a path, or the commit.

Line 3 cannot carry the private commit or a card, lab, or path from the private repository for the same reason the old step could not: the deploy command reads the already-vendored bundle in `api/worker`, not the private checkout. That is an existing property of the deploy tool's output, not something this change establishes or changes.

## The classifier

Decided from the captured output without printing it:

- Retry only if the output holds `[code: 10013]` or `Received a malformed response from the API`, and holds no other `[code: N]`.
- Any other Cloudflare error code (validation, size, binding, text var) is a rejection and is not retried, even beside a transient marker.
- Neither marker present is unknown and is not retried ("if you cannot tell, do not retry").

Bound: at most 3 attempts in all, pauses 20 seconds then 60 seconds. A passing attempt ends the loop. The tool's exit code is the step's exit code.

## The alert

New job `deploy-alert` in `.github/workflows/rank-api.yml`:

- `needs: deploy`, `if: always() && github.ref == 'refs/heads/main' && (needs.deploy.result == 'failure' || needs.deploy.result == 'success')`. `always()` is needed because a job whose dependency failed is otherwise skipped. A skipped or cancelled deploy does nothing.
- `permissions: issues: write` and nothing else. `github.token` is the only credential (`GH_TOKEN`). It has no `env` at job level, no `outputs`, no secrets, no private token or name, and no artifact step.
- It reads only `needs.deploy.result`, never `needs.deploy.outputs`.
- Steps: a public checkout (`persist-credentials: false`, the same pinned SHA the other jobs use), then on `failure` open or update, on `success` close.
- Issue: title `Rank Worker deploy failed`, label `alert`. The first red deploy creates it (and `gh label create alert --force`, the nightly's own call). A later red deploy comments on it with the same four fields. The listing matches the exact title, so the accuracy nightly's alert issue is never touched. The next green deploy closes every open issue with that exact title and the comment `Green again: <run URL>`.
- Body, from `scripts/deploy_alert.py`, four lines and nothing else: `Workflow:` (the workflow name, validated as a plain name), `Run:` (a `https://github.com/<owner>/<repo>/actions/runs/<id>` URL), `Commit:` (the 40-hex SHA of this public repository), `Failure class:` (`transient-exhausted`, `rejected`, or `unknown`). A field that is not what it should be raises and no issue is written.
- The class: `needs.<job>.result` carries no class, and the guard forbids reading outputs. The alert script therefore asks the public API for the failed deploy job's check-run annotations and takes the one allow-listed `deploy-failure-class=<class>` message that line 4 leaves. Anything else, or any failure to read, gives `unknown`; the alert is never skipped for that.

Why this fits the nightly's mechanism: the same `gh label create`, `gh issue list`, `gh issue comment` or `create`, and close-on-green shape as `accuracy-nightly.yml`. `scripts/accuracy_alert.py` writes a nightly layer table from a report and does not fit this body, so a small sibling script writes the four fixed fields.

## Guard data

Only the pinned data for the step I changed moved in `tests/test_accuracy_alert.py`:

- `_PRIVATE_JOB_TAILS[("rank-api.yml", "deploy")]`: the `Deploy` step's `run_sha256` (old `65400d86...` to `7f11d5c0...`).
- `_STEP_PINS[("rank-api.yml", "deploy")]`: the job's step digest (old `06d88e49...` to `ee6da731...`).

Unchanged: `_SURROUNDING_PINS` (no workflow or job `env`, `defaults`, `permissions`, `environment` change on `deploy`), the `deploy-staging` pins, and the free-key lists. The new job is not guarded and passes every rule as written: it names neither the private repository nor its tokens, reads only `needs.deploy.result`, and downloads no artifact. No rule was weakened and no exception was added.

Two other tests that read the `Deploy` step changed with it: `tests/test_reference_access.py` (the documented command is the step's command inside the wrapper) and `tests/test_worker_memory.py` (its stand-in for `uv` became an executable, because the command now runs in a child process, and it passes `GITHUB_WORKSPACE`).

## Checked by hand, not run

The workflow was not run, and `actionlint` is not installed on the build host. `shellcheck` was run on the three new or changed shell blocks and was clean. Read as the runner would:

- `needs.deploy.result` in the job `if` and in step `if` keys: the `needs` context is available at both. With `always()` the job runs after a failed dependency; without it, it would be skipped.
- `github.token`, `github.repository`, `github.run_id`, `github.server_url`, `github.sha`, `github.workflow` are available in step `env`.
- The `permissions` block grants `issues: write` and sets every other scope to none. Public checkout and public reads of the jobs and annotations endpoints need no scope on a public repository.
- A re-run of the failed deploy job that passes sets `needs.deploy.result` to `success` and closes the issue.

Not verifiable without a run: that a check-run annotation's `message` is exactly the text after `::error::` (the script matches on the message alone, not on a title), that the annotation is visible by the time the alert job reads it (otherwise the class is `unknown`), and that the public checkout and the two public API reads succeed with only `issues: write`.
