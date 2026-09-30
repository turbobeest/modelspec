# Data split: a frozen public image, a private working copy (MODEL-246)

Status: design, with the parts that do not need the private repository built
(`pipeline/data_source.py`, `scripts/data_lag.py`,
`scripts/data_freeze_guard.py`, two workflows, tests).
Parent: MODEL-245. This ticket is 245-A. Repointing the writer workflows is
245-B and is not in this change.

## Decision

Fresh curated data does not land in this repository. The public repository
keeps a data image that is **nine months old**. The live site's manual lookup
and the keyed API, MCP and CLI answer from the fresh data.

- The fresh data lives in the private repository `turbobeest/modelspec-data`.
- The public repository keeps all code, the schema, the vocabulary, the tests
  and the frozen data image.
- The image is refreshed by a scheduled job that publishes the private data
  *as of today minus nine calendar months*. Nothing changes in the public
  data directories until the first eligible commit ages past the cutoff.

Nothing here moves, deletes or rewrites data already in this repository, and
git history is untouched.

## What counts as data

`pipeline/data_source.DATA_PATHS` is the single list. Everything else is code
or vocabulary and stays public.

| Path | Holds | Written by |
| --- | --- | --- |
| `models/` | model cards | daily-research, leaderboard-refresh, release-signals, humans |
| `benchmarks/` | benchmark wiki pages | curation watcher (via `scripts/curation/propose.py`), humans |
| `hardware/` | device SKUs | humans |
| `hosts/` | host and provider records | humans |
| `offerings/` | prices and plans | price-reread |
| `verification/` | evidence log, queue, event stream | leaderboard-refresh, price-reread, release-signals |
| `measurements/` | speed pilot measurements | speed-probe |
| `premier/` | curated premier sets | humans |
| `research/` | research outputs and sources | daily-research |
| `registry/sources.yaml` | dated source-of-record entries | humans, curation |
| `registry/providers.yaml` | provider records | humans, price-reread |
| `registry/harnesses.yaml` | harness records | humans |
| `registry/release-watch-baseline.json` | last-seen release state | release-signals |

Kept public on purpose:

- The rest of `registry/` is vocabulary that changes in lock step with the
  engine: `domains.yaml`, `facets.yaml`, `families.yaml`, `templates.yaml`,
  `refinements.yaml`, `release-watch.yaml`. An audit on 2026-09-30 found
  the four data files above among them and declared them data. They are
  declared, not moved: the public copies stay where they are, frozen.
- `decision/` is code.
- `scripts/*.jsonl.gz` and `attribution.yaml` are historical evaluation
  evidence, already public, and not refreshed.
- `docs/`, `schema/`, `pipeline/`, `api/`, `cli/`, `web3d/`, `tests/`.

A path in `DATA_PATHS` may be a directory or a single file. When a file sits
in a directory that also holds public vocabulary, the overlay makes that
directory real and links each entry separately.

## Reading the private data: the overlay root

Almost every reader and writer in the repository assumes the data directories
sit next to the code. Changing each one to accept a second path is a large,
error-prone edit. Instead the build composes a **overlay root**: a temporary
directory whose entries are symlinks. Data paths point into the private
checkout, everything else points into the public checkout.

```
overlay/
  models        -> modelspec-data/models
  verification  -> modelspec-data/verification
  ...
  pipeline      -> public/pipeline
  registry/             # a real directory, entries linked one by one
    sources.yaml -> modelspec-data/registry/sources.yaml
    facets.yaml  -> public/registry/facets.yaml
  .git          -> public/.git      # the export pin stays the code commit
```

- A data path absent from the private checkout is absent from the overlay. It
  never falls back to the stale public copy, so a mistake cannot silently
  publish old data as fresh.
- The private checkout must contain `models/` and `benchmarks/`, or the overlay
  refuses to build (`DataSourceError`, exit 2).
- Writes through the overlay land in the private checkout.
- Code that finds its files from its own `__file__` resolves through the
  symlink back to the public tree and would read the stale copy. The build
  handles the one that matters: `decision.registry.use_root(root)` points the
  decision registry at the overlay for the duration of the build. Every other
  such script is an audit item for 245-B (for example
  `release_signals/watch.py`); it must be given the overlay root, or the
  private checkout, explicitly.
- `.git` is the public one, so `build.commit` in the export is still the code
  commit. The export contract gains no field and there is no contract bump.

Use:

```bash
python -m pipeline.build --data-dir ../modelspec-data     # or MODELSPEC_DATA_DIR
python -m pipeline.data_source overlay --private ../modelspec-data --out /tmp/root
```

Verified: a build with `--data-dir` pointing at this repository is byte-identical
to the plain build (7,988 files, timestamps normalised). That check caught one
leak, card links in `pipeline/agent_ready.py` embedding the temporary root,
now fixed and tested.

With neither set the build reads the repository's own directories exactly as
before, which is what public pull requests and forks get.

## Building the sites and the Worker

`deploy-sites.yml` and `rank-api.yml` gain a checkout step for
`turbobeest/modelspec-data` into `modelspec-data/`, using
`secrets.MODELSPEC_DATA_TOKEN`, then build with `--data-dir modelspec-data`.
The build fails, and does not deploy, if the secret is empty. Only the
`main`-branch deploy jobs get the token. Pull-request builds and fork builds
do not; they build from the frozen public image.

`MODELSPEC_DATA_TOKEN` is a fine-grained token with **read-only Contents access
to `turbobeest/modelspec-data` and nothing else**. It is created by Jamie. The
lag job and the writers need a *write* path to the private repository; that is
a separate credential (or the private repository's own `GITHUB_TOKEN`, once the
writers run there).

Rank Worker: it builds from the same static export, so it needs no runtime
access to the private repository. The private data reaches it only inside the
built JSON.

## Writers

Six workflows write data today (verified from the workflow files):

| Workflow | Writes | Cadence |
| --- | --- | --- |
| `daily-research.yml` | `models/**`, `research/**` | daily |
| `leaderboard-refresh.yml` | `models/`, `verification/log.jsonl`, `verification/queue/events.jsonl` | weekly |
| `price-reread.yml` | `offerings/`, `verification/` | weekly |
| `speed-probe.yml` | `measurements/speed/**` | manual dispatch |
| `release-signals.yml` | `git add models verification` | hourly gate, work-driven |
| `curation-benchmarks.yml` | `benchmarks/` (through `scripts/curation/propose.py`) | daily trial, then weekly |

Plan (245-B): each writer keeps its logic and runs in an overlay root, with
any `__file__`-derived root replaced by an explicit one. It commits and opens its pull request **in the private repository**.
Scripts that call `git` relative to the repository root need a per-script check
before the move; the overlay's `.git` points at the public repository, so a
writer that shells out to `git add` must run `git -C <private checkout>` instead.
That check is the first task of 245-B.

### Public CI must not leak the private data

Actions logs and artifacts on a public repository are public. So a job that
holds `MODELSPEC_DATA_TOKEN`, or checks out `modelspec-data`, must:

- have no `actions/upload-artifact` step, and
- never print data: no `cat`, `head`, `tail`, `echo`, `git diff`, `git show` or
  `git log` of data paths, and no workflow-command annotations quoting rows.

Counts and pass/fail are fine. `tests/test_data_workflows.py` parses every
workflow and fails on a violation, so the rule holds for 245-B's edits too.

Existing artifact uploads that would carry fresh data once repointed. 245-B
must move each into the private repository, drop it, or reduce it to counts:

| Workflow | Artifact | Carries |
| --- | --- | --- |
| `speed-probe.yml` | `speed-pilot-runs-*` | raw pilot runs under `measurements/`. Must run in the private repository |
| `deploy-sites.yml` | `sites`, `sites-holding`, `sites-internal` | built site JSON. Rebuilt from fresh data. Keep only where the artifact is exactly what is published |
| `price-reread.yml` | `price-reread-copies` | copies of the pages read, with fresh prices |
| `curation-benchmarks.yml` | `curation-change-report-*` | `benchmarks/_curation/reports/` |
| `leaderboard-refresh.yml` | `leaderboard-refresh-audit-*` | audit of fresh scores |
| `release-signals.yml` | `release-signals-pending`, `release-signal-audit-*` | pending signals and audit |
| `coverage-slo.yml` | `coverage-report` | per-model coverage from fresh cards |
| `accuracy.yml`, `accuracy-nightly.yml` | `decision-accuracy*` | accuracy reports over fresh cards |
| `benchgraph-graph.yml` | `benchgraph-graph-*` | graph export from benchmark data |

`test.yml` uploads only collection lists and timings and stays as is.

Cheap watchers and gates that only read public sources or decide whether work
exists (`release-watch`, the release-signals pending matrix) stay in this
repository, where they cost nothing, and dispatch the private workflow only
when there is work.

Until 245-B lands, the existing writers still open pull requests that touch
`models/`. Those will fail the freeze guard (below). That is intended: the guard
is not yet a required check, so it reports the drift without blocking merges,
and it becomes required only after the writers are repointed.

## The lag job

`scripts/data_lag.py`, run weekly by `.github/workflows/data-lag.yml`.

1. `cutoff = today - 9 calendar months`, clamped to the month end
   (`2027-05-31 -> 2026-08-31`, `2026-11-30 -> 2026-02-28`).
2. Pick the last commit on the private default branch whose **committer date is
   at or before the cutoff**. None means no-op (`no-image-yet`).
3. Extract that commit's data paths (`git archive`), replace the public data
   directories with them, and write `data-image.json`:
   `as_of`, `lag_months`, `source_repo`, `source_commit`, `paths`.
4. If the tree is already that image the job reports `unchanged` and opens
   nothing.
5. Otherwise it opens a pull request from `data-lag/image`.

The private repository is seeded with a single commit dated 2026-09-30. The
cutoff reaches it on 2027-06-30, so **the public image does not change until
2027-06-30**. `--dry-run` prints `would-publish` without writing.

The workflow only runs when the repository variable `DATA_SPLIT_ENABLED` is
`true`, and fails loudly if `MODELSPEC_DATA_TOKEN` or `RESEARCH_PR_TOKEN` is
empty (the second so that the pull request runs the required checks).

## The freeze guard

`scripts/data_freeze_guard.py`, run by `.github/workflows/data-freeze.yml` on
every pull request. It reads the three-dot diff against the base and fails when:

- a data path or `data-image.json` changes on any branch other than
  `data-lag/*`; or
- on a `data-lag/*` branch, `data-image.json` is missing, unreadable, or has
  `as_of` after today's cutoff; or
- on a `data-lag/*` branch, a changed data file adds an ISO date after the
  cutoff.

It judges the diff, not the tree, so data already in the repository is
grandfathered and there is no baseline manifest to maintain. Binary files are
skipped. Error lines name the file and point at the private repository.

Limits, stated plainly: the guard checks the branch name, so it defends against
mistakes, not a determined contributor; branch protection and review are what
stop that. The new workflow is not a required check until Jamie adds it, and
touching `.github/workflows/` means this PR is merged by hand.

## Tests on fixtures

About 99 test files read the real data directories. With a stale image that is
acceptable for now, but the public engine tests should not depend on which
image is checked out. Phase 245-C moves them onto `tests/fixtures/` (a small
synthetic catalogue) and keeps a thin set of tests that assert the *shape* of
whatever image is present. Not done here.

New tests in this change use temporary trees and temporary git repositories, so
they are independent of the data.

## Seeding the private repository

After this document is reviewed: create one commit in `modelspec-data` holding
the current `DATA_PATHS`, dated 2026-09-30. A single seed commit is enough for
the schedule above; carrying history is optional and does not change it. The
public repository, its data and its history are read only for the seed.

## Estimated Actions minutes in the private repository

Only workflows that run *in* `modelspec-data` count. Watchers, the guard, the
lag job and the site builds run in the public repository. Estimates use the
timeouts already declared and typical run lengths; they are planning figures to
be replaced by measured values after a month.

| Job | Runs per month | Minutes each | Minutes |
| --- | --- | --- | --- |
| daily research | 30 | 15-25 | 450-750 |
| curation (daily trial; weekly afterwards) | 30 (then 4) | 5-10 | 150-300 (then 20-40) |
| release signals, work-driven | ~100 | 2-4 | 200-400 |
| leaderboard refresh | 4-5 | 8-10 | 32-50 |
| price re-read | 4-5 | 8-15 | 32-75 |
| speed probe (manual) | 2-4 | 20-45 | 40-180 |
| seed, tidy-up, dispatch glue | - | - | ~20 |
| **Total** | | | **~925-1,775** |

If the hourly release-signals gate ran in the private repository instead, it
would add about 720 minutes a month for a one-minute job. That is why the gate
stays public.

## What is left, and who does it

| Item | Owner |
| --- | --- |
| Create `MODELSPEC_DATA_TOKEN` (read-only) and store it in this repository's secrets | Jamie |
| Set `DATA_SPLIT_ENABLED=true` when ready | Jamie |
| Seed `modelspec-data` (single commit, current `DATA_PATHS` including the four registry files) | this ticket |
| Add the checkout step and `--data-dir` to `deploy-sites.yml` and `rank-api.yml` | 245-B |
| Repoint the six writers; audit their `git` calls and any `__file__`-derived roots; resolve the artifact table above | 245-B |
| Move public engine tests to fixtures | 245-C |
| Make "Data freeze" a required check, after the writers are repointed | Jamie |
