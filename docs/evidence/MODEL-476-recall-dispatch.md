# MODEL-476: writer workflows start the recall check on their own pull requests

## The gap

The files under `.github/private-writers/` are the sources of workflows that run only in the
private data repository. Eleven of them open or update a pull request there with the
repository token. GitHub starts no `pull_request` workflow for a pull request opened that
way, so the check "Approved answers on private data" (workflow "Private production-data
recall", file `recall-private.yml`) never ran until a person closed and reopened the pull
request or dispatched the workflow by hand.

The recall workflow has a `workflow_dispatch` trigger with no inputs, and its only
permission is `contents: read`. A dispatched run is a check run on the head commit of the
branch it was started on, so the pull request lists it. (Read in the data repository's
installed copy, which is byte-identical to `.github/private-writers/recall-private.yml`.
Nothing was dispatched to prove the check shows on a pull request: see "Not verified".)

## What changed

Each writer below gets one new job, `recall-dispatch`. It dispatches `recall-private.yml`
on the pull request branch with `gh workflow run recall-private.yml --ref <branch>`, then
comments on the pull request that the check was started. If the dispatch fails, the same
job comments the fallback text ("close and reopen the pull request" and the manual
dispatch). The fallback text exists only in that job.

| Writer file | Job that opens the pull request | Job that holds `actions: write` | Branch pattern the dispatch job enforces |
| --- | --- | --- | --- |
| `admission-drafter.yml` | `draft` | `recall-dispatch` | `^admission/[a-z0-9][a-z0-9.-]*/[a-z0-9][a-z0-9.-]*$` |
| `curation-benchmarks.yml` | `draft` | `recall-dispatch` | `^curation/benchmarks/[A-Za-z0-9][A-Za-z0-9._-]*-[0-9]{4}-[0-9]{2}-[0-9]{2}$` |
| `daily-research.yml` | `research`, then `sync` | `recall-dispatch` | `^research/daily-models$` |
| `data-trust-audit.yml` | `audit` | `recall-dispatch` | `^data/data-trust-[0-9]{4}-[0-9]{2}-[0-9]{2}$` |
| `leaderboard-refresh.yml` | `refresh` | `recall-dispatch` | `^data/weekly-leaderboard-refresh$` |
| `lineup-proposer.yml` | `propose` | `recall-dispatch` | `^data/lineup-proposal$` |
| `model-week.yml` | `draft` | `recall-dispatch` | `^data/model-week$` |
| `price-reread.yml` | `reread` (two pull requests) | `recall-dispatch` | `^data/weekly-price-(reread\|reconfirm)$` |
| `release-signals.yml` | `process` (matrix) | `recall-dispatch` | `^data/release-signal-[A-Za-z0-9._-]{1,150}-[0-9]{1,3}$` |
| `rendered-reread.yml` | `reread` | `recall-dispatch` | `^data/weekly-rendered-reread$` |
| `speed-probe.yml` | `probe` | `recall-dispatch` | `^data/speed-pilot-[0-9]{1,20}$` |

Every dispatch job also rejects a name containing `..` or longer than 200 characters.
`recall-private.yml`, `public-leak-guard.yml`, `release-coverage.yml` and
`workflow-health.yml` open no pull request and are unchanged.

### Permissions, before and after

Every existing job keeps exactly its permissions. `tests/test_recall_dispatch.py` pins each
one. The only addition is the new job.

| Writer | Existing jobs (unchanged) | New job `recall-dispatch` |
| --- | --- | --- |
| `admission-drafter` | `draft`: contents write, pull-requests write | actions write, pull-requests write |
| `curation-benchmarks` | `gate`: contents read. `watch`: contents read, actions read. `draft`: contents write, pull-requests write. `issues`: contents read, issues write | same |
| `daily-research` | `research`, `sync`: contents write, pull-requests write | same |
| `data-trust-audit` | `audit`: contents write, pull-requests write | same |
| `leaderboard-refresh` | `refresh`: contents write, pull-requests write | same |
| `lineup-proposer` | `propose`: contents write, pull-requests write | same |
| `model-week` | `draft`: contents write, pull-requests write | same |
| `price-reread` | `render`: contents read. `fallback`: contents read, actions read. `reread`: contents write, pull-requests write, issues write, actions read | same |
| `release-signals` | `pending`: none. `process`: contents write, pull-requests write. `review`: contents read, issues write | same |
| `rendered-reread` | `reread`: contents write, pull-requests write, issues write, actions read | same |
| `speed-probe` | `probe`: contents write, pull-requests write | same |

The workflow-level permission stays `contents: read`. The new job has no `contents`
permission at all. It holds `pull-requests: write` only to post the one comment, by branch
name. That is the one addition beyond the brief's "actions: write"; the comment is what
lets the fallback text appear only when the dispatch failed.

## The riskiest rule: who can reach the token that starts workflows

`actions: write` lives only in `recall-dispatch`. Per writer, that job:

- has no checkout, no `uses:` step, no `working-directory`, and exactly one `run:` step that
  contains no Python and runs nothing from a working tree;
- receives, besides fixed text and `github.token`, one input: the branch name or names in
  `BRANCHES`, copied from `needs.<job>.outputs` into `env:`. No `${{ }}` appears in the
  `run:` text;
- checks each name against the writer's fixed pattern with a bash regular expression held
  in `BRANCH_PATTERN`, and against `..` and length, before any `gh` call. A name that fails
  is never echoed (a name could carry `::` workflow commands) and nothing is dispatched
  for it; the job fails but continues to the next name;
- calls only `gh workflow run recall-private.yml --ref "$branch"` and `gh pr comment
  "$branch" --body "$MESSAGE"`, with the branch quoted and always starting with a letter
  and a fixed prefix, so it cannot be read as an option (a leading `-`), carry shell
  metacharacters (the classes above exclude `;|&$()` backticks space and newline), or name a
  ref outside the writer's namespace;
- has `continue-on-error: true`, `timeout-minutes: 5`, and no job depends on it. A failure
  turns the job red and posts the fallback comment but leaves the workflow run green and
  the pull request open.

Per writer, where the branch name comes from and why no attacker controls more than the
pattern allows:

| Writer | Where the name comes from | Fetched web text or model text in the name? |
| --- | --- | --- |
| `admission-drafter` | the human dispatch input `model`, already validated to `^[a-z0-9][a-z0-9.-]*/[a-z0-9][a-z0-9.-]*$` before the writer used it | no |
| `curation-benchmarks` | the `draft` job lists today's open draft pull requests with `gh pr list` and keeps only heads that match the pattern with `jq`. The page id in the branch comes from the curation registry; the date is `date -u` | page ids are registry names, and the pattern refuses anything else. The job that runs `claude -p` on page text holds no `actions: write`, and its branch list is filtered twice |
| `daily-research` | the fixed string `research/daily-models`, written by the existing `sync` step only when an open pull request from that branch exists | no |
| `data-trust-audit` | `data/data-trust-` plus the date from `date` | no |
| `leaderboard-refresh`, `lineup-proposer`, `model-week`, `rendered-reread` | fixed strings in the action's `branch:` input | no |
| `price-reread` | two fixed strings | no |
| `speed-probe` | `data/speed-pilot-` plus `github.run_id` | no |
| `release-signals` | the writer builds `data/release-signal-<signal id>-<day>` from a signal id served by the signals API, with every character outside `[A-Za-z0-9._-]` replaced by `-`; or, when it updates an open pull request, that pull request's head branch. The matrix job re-checks the name against the pattern in step `recall_branch` before it becomes an output; the dispatch job checks it again | yes: this is the one writer with a name derived from fetched content. Both pattern checks and the `..` check hold, and a head branch that is not `data/release-signal-...` is dropped with a warning |

What the dispatched run can itself start: nothing. `recall-private.yml` declares
`permissions: contents: read` and contains no `actions` permission, no `gh workflow run`,
no `repository_dispatch`, and no secret other than the default token it uses to check out the
repository. A run started by `GITHUB_TOKEN` through `workflow_dispatch` is the documented
exception that does start a run, and the run it starts cannot start another.

Three differences between a dispatched run and the `pull_request` run it stands in for:

1. **Baseline.** On `pull_request` the recall check compares private baselines with the
   merge-base baseline (`--approved-baseline`). A dispatched run takes `github.event_name ==
   workflow_dispatch`, skips that step and compares with the branch's own
   `reports/recall/baseline.json`.
2. **Base-pin check.** The check that the branch's `.engine-pin` still matches the base
   branch's runs on `pull_request` only. A dispatched run skips it.
3. **What is tested.** A `pull_request` run tests the merge of the branch with `main`. A
   dispatched run tests the branch head alone, so a change on `main` that conflicts in meaning
   with the branch is not seen.

Why that is acceptable for writer branches: no writer changes `.engine-pin`,
`reports/recall/` or anything under `.github/` (the `add-paths` of each writer list data
files only, and `release-signals` makes its own approved-answers comparison before it
pushes). So the skipped baseline comparison and the skipped base-pin check have nothing to
compare, and `daily-research` merges `main` into its branch before the dispatch, so the
branch head it tests already contains `main`. A human who edits the baseline or the pin on a
pull request still gets the stricter `pull_request` run on that pull request.

## Behaviour per writer (what the runner does)

- **Peter Evans writers** (`admission-drafter`, `data-trust-audit`, `leaderboard-refresh`,
  `lineup-proposer`, `model-week`, `rendered-reread`, `speed-probe`, and the two in
  `price-reread`): the pull-request step gets an `id`. The job output is
  `(op == 'created' || op == 'updated') && branch || ''`, built from the action's
  `pull-request-operation` and `pull-request-branch` outputs. A run with no diff, a dry run
  or a closed pull request leaves the output empty and the dispatch job is skipped.
- **`daily-research`**: the dispatch waits for `sync`, which already finds the one open pull
  request from the branch, so the dispatch also runs after a push to `main` merged `main`
  into the branch. `update-branch` is asynchronous, so `sync` writes `pr_branch` only once the
  pull request head is current. It polls `gh pr view --json headRefOid` up to 12 times, 5
  seconds apart (about a minute), until the head differs from the one it saw before the
  call. Three outcomes: the branch is already up to date (`behind_by` is 0), the head is
  current and the branch is written at once; the head moves within the bound, the branch is
  written after the move; the head never moves, no branch is written (so no run starts on the
  old head), `sync` posts the fallback text on the pull request itself with its own
  `pull-requests: write`, and the job stays green. If `update-branch` is refused the head did
  not change, the branch is written and the job fails as before. This is the only change to
  an existing step, and the poll uses the token `sync` already had. `STARTED_MESSAGE` is empty there, so a push to `main` does not add a comment each
  time; the pull request body states that a follow-up job starts the check.
- **`curation-benchmarks`**: one run can open several pull requests, so a step after the
  existing "Open draft PRs" step (`continue-on-error`) writes a space-separated list of
  matching open drafts to `branches`, and the dispatch job loops over it.
- **`release-signals`**: `process` is a matrix. Job outputs of matrix legs merge by name, so
  each leg writes one of ten fixed names, `branch_0` to `branch_9`, selected by
  `strategy.job-index`, equal to `MAX_RELEASE_SIGNAL_WORK_ITEMS`. A test ties the two
  numbers together. The dispatch job joins the ten outputs into one line.
- **A refused name in `release-signals`**: the matrix step `recall_branch` drops a branch name
  that fails the pattern, so the dispatch job never sees it. That step now posts the fallback
  text on the pull request itself (`gh pr comment` by URL, with the `pull-requests: write` the
  `process` job already has) and no branch is written. A pull request therefore gets either
  a started check or the fallback text, never silence.
- **The PR body line in `release-signals`** that said the check does not start by itself now
  says a follow-up job starts it and a comment reports the result. The text "close and
  reopen" remains only in the dispatch job's fallback message.

## What was checked by hand

These workflows never run in this repository, and `actionlint` is not installed on the
build host, so the YAML was read as the runner would:

1. **Contexts at each key.** `jobs.<id>.if` uses `needs` with a status function and `if` takes
   `${{ }}` with `!cancelled()`. `jobs.<id>.outputs` uses `steps` and `strategy.job-index`,
   both available there. `steps.env` uses `needs`, `github.token`, `github.repository`.
   Nothing reads `secrets`, `matrix` or `inputs` in the new job.
2. **`needs.<job>.outputs` wiring.** Every output name read in `recall-dispatch` is declared
   on the job it needs, and every declared output reads a step with an `id` in that job. The
   tests walk this.
3. **Skipped or empty upstream.** An upstream job skipped by its `if` (for example
   `github.ref == 'refs/heads/main'`, or `count == '0'` for `release-signals`) leaves an
   empty output, so the dispatch condition is false and the job is skipped. Because the
   condition contains `!cancelled()`, an upstream job that failed after it opened the pull
   request still lets the dispatch run: outputs of a failed job are still available.
   `data-trust-audit` fails its job on purpose after the pull request exists, and the
   dispatch still runs.
4. **No pull request, no dispatch.** The `if:` on each pull-request step (`dry_run`, no
   diff, a zero count) leaves `pull-request-operation` empty, so no branch is exposed.
5. **Token.** `GH_TOKEN` is `${{ github.token }}`, scoped by the job's `permissions` to
   actions write and pull-requests write. No personal token and no secret appears in the
   job. The test rejects `secrets.` anywhere in it.
6. **Shell.** The dispatch script and the two new step scripts pass `shellcheck -s bash`.
   `tests/test_recall_dispatch.py` runs the dispatch script against a stub `gh` for every
   writer: a valid name dispatches once and comments, an invalid name is never passed to
   `gh` and not echoed, a failed dispatch posts the fallback, a failed comment is only a
   warning, an empty list does nothing. The existing `tests/test_writer_isolation.py` guard
   passes with the new job.
7. **jq filter** of `curation-benchmarks` run by hand on sample input: it keeps today's
   `curation/benchmarks/...` heads and drops other dates, spaces, `$(...)` and `main`.

## Not verified

- No workflow was dispatched in either repository. That a dispatched run shows as the check
  "Approved answers on private data" on the pull request, and that `gh pr comment <branch>`
  works with only `pull-requests: write` and no `contents` permission, are read from the
  documentation, not seen.
- That an empty job output from one matrix leg does not overwrite a value from another leg
  (`release-signals`) is documented behaviour of Actions that was not exercised.
- The poll in `daily-research` and the refused-name comment in `release-signals` were run
  against a stub `gh` and checked with `shellcheck`, not on a runner.
- The three things nobody has seen run: a dispatched run showing as the pull request's check
  (the supervised first runs below prove it); `gh workflow run` and `gh pr comment <branch>`
  working with only `actions: write` and `pull-requests: write` in the dispatch job; and the
  runner dropping empty job outputs from matrix legs instead of overwriting a value from
  another leg (`release-signals`).

## Install in the data repository

**Order matters. The data repository's mirror step compares its workflow copies with this
repository's `main`, so from the moment this merges, every recall run in the data repository
fails that step until the pin and all eleven copies are installed in one data pull request.
Merge only when no data pull request is waiting on its check, and install immediately.**

One pull request in `turbobeest/modelspec-data`:

1. Merge this pull request to the public repository (only at a quiet moment, see above).
2. Move `.engine-pin` to a commit of public `main` that contains the merge.
3. Copy the eleven changed files from `.github/private-writers/` to
   `.github/workflows/` byte for byte. `.github/scripts/check_writer_mirrors.py` fails the
   pull request if a copy differs from its public source, and checks the pin.
4. Supervise the first runs. First `lineup-proposer` (cheapest): see that the job
   `recall-dispatch` starts, that "Private production-data recall" runs on the branch, that
   the check appears on the pull request, and that one comment is posted. Then one
   `release-signals` run that opens at least two pull requests, to prove that every matrix
   leg's branch reaches the dispatch job.
5. Do not add a personal access token or change a workflow permission when it fails: the
   fallback comment already says how to run the check by hand.

## Round three: a dispatched run reports its result as a commit status

### Measurement

On 2026-11-13, for a pull request head whose only recall run came from `workflow_dispatch`,
the commit carried the check suite and the check run, but the commit's `statusCheckRollup`
was null, `gh pr checks` said "no checks reported" and the pull request's check list was
empty. GitHub does not count a check run from a `workflow_dispatch` run in a pull request's
checks. With the check required on `main`, a writer-opened pull request would wait forever.
On 2026-11-14 a commit status posted through the REST API
(`POST /repos/{owner}/{repo}/statuses/{sha}` with a `context`) did appear in the commit's
rollup next to check runs. So a dispatched recall run posts a commit status.

### The new jobs in `recall-private.yml`

Two small jobs, both only for `workflow_dispatch`. `pull_request` and `schedule` runs skip
both, because there the check run itself is what counts. The `context` of every status is
"Approved answers on private data", exactly the recall job's check name, and `target_url` is
the run's URL.

| Job | `permissions` | `needs` | `if` | Inputs (all through `env:`) |
| --- | --- | --- | --- | --- |
| `recall` (unchanged) | none of its own: inherits the workflow's `contents: read` | none | none | unchanged |
| `status-pending` | `statuses: write` and nothing else | none | `github.event_name == 'workflow_dispatch'` | `github.token`, `github.sha`, `github.repository`, `github.run_id`, the fixed context |
| `status-final` | `statuses: write` and nothing else | `status-pending`, `recall` | `always() && github.event_name == 'workflow_dispatch'` | the same, plus `needs.recall.result` |

Each status job has one step, a fixed `gh api` call, no checkout, no `uses:`, no secret, no
`${{ }}` in `run:`, no `continue-on-error`. `status-pending` starts at once, in parallel
with `recall`, and posts `pending`. `status-final` waits for both jobs (so the final status
always lands after the pending one) and posts the true result.

### Recall result against the status posted

| Recall job result | Status posted |
| --- | --- |
| `success` | `success` |
| `failure` (including the 20-minute timeout) | `failure` |
| `cancelled` | `error` |
| `skipped` | `error` |
| empty, unset or any other value | `error` |
| the status job itself fails (API refused, input missing) | the job turns red; no new status is posted, so the previous one stands: `pending` when the final job failed, or none when the pending job failed |

A failure to post never changes the recall job's own result: neither status job is a
dependency of `recall`. A missing status is visible as a red `status-pending` or
`status-final` job.

### Endings: cancelled runs, and what is left pending

- The workflow has `concurrency: recall-private-${{ github.ref }}` with
  `cancel-in-progress: true`. `always()` makes `status-final` run on a cancelled run too, so a
  run cancelled by a newer dispatch on the same branch posts `error` on its own commit.
- If the newer run is on the same commit, that `error` can land after the newer run's
  `pending` and shows red until the newer run's final status overwrites it. If the older job
  is delayed past the newer run's end, `error` can be the last state on a commit whose check
  passed. The remedy is one more dispatch of the workflow on that branch. No ordering gives a
  `success` that the commit's own run did not earn.
- Only a cancel by hand or a runner outage during `status-final` leaves `pending`. That
  blocks the pull request; it does not pass it.
- `status-final` failing to post (the API refused) also leaves the earlier status, and the
  job is red.
- `status-pending` posting after `status-final` cannot happen: the final job needs it.
- A pull request opened by a person gets the check run from `pull_request` and no dispatch.
  If a dispatch is also run on its branch, the status and the check run share the name and
  both then count.

### Permissions

The workflow-level block stays `contents: read`. A job-level `permissions` block replaces the
workflow-level one, so each status job holds `statuses: write` and nothing else, not even
`contents`. The recall job checks out and runs code from the branch under test and holds no
write permission; its steps are unchanged (a test pins their names and order). No other job
in any private-writer file holds `statuses: write`.

### A branch can change this very file

The workflow file that runs on `workflow_dispatch` is the copy on the dispatched ref. A
branch that changes `recall-private.yml` could post any status. This design does not rely on
the branch's copy being unmodified. It relies on who can push: the writers' own branches
(`data/...`, `research/...`, `admission/...`, `curation/benchmarks/...`) are written by
workflows whose `add-paths` list data files only, and pushing any branch in the private
repository needs write access to that repository, which also lets that person post a commit
status with their own token. The recall job's mirror step compares the branch's workflow
copies with public `main` and fails on a difference, but that step runs in the recall job,
which the same branch could change: it catches mistakes, not an attacker with push access.
The protection that counts against such a change is review of the workflow diff in the pull
request.

### Install order

`recall-private.yml` is the twelfth changed file. In ONE data pull request: move
`.engine-pin` to a commit of public `main` that contains this merge, and copy
`.github/private-writers/recall-private.yml` byte for byte to
`.github/workflows/recall-private.yml` (with the eleven writer copies from the earlier round
when they are still not installed). From the moment this merges, the data repository's mirror
step fails until the copy is installed. Merge only when no data pull request is waiting on its
check.

### What only a real run proves

- That the repository token can post the status.
- That it shows in `gh pr checks` on a writer-opened pull request.
- That it satisfies a required check of that name. The branch-protection proposal depends on
  this and it is still to be seen on a runner.

### What was checked by hand

`actionlint` is not installed on the build host. The YAML was read as the runner would:
`needs.recall.result` is available in `jobs.<id>.steps[*].env` of a job that lists `recall` in
`needs`, and takes the values `success`, `failure`, `cancelled`, `skipped`; `always()` is
allowed in a job-level `if`; `github.token`, `github.sha`, `github.repository` and
`github.run_id` are available in `env:`; `GITHUB_SERVER_URL` is a default variable; `gh api`
needs no checkout; `gh api` exits non-zero on an HTTP error, and `set -e` carries that out of
the step. `shellcheck -s bash` passes on both scripts (a test runs it when installed), and
`tests/test_recall_status.py` runs both scripts against a stub `gh`.
