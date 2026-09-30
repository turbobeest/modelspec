# Data split: a frozen public image, a private working copy (MODEL-246)

Status: MODEL-246 built the overlay, lag job and freeze guard. MODEL-247 W
closes the writer and leak-guard gaps below. The private workflows are submitted
on `modelspec-data` branch `writers-setup` for human merge. MODEL-247 S owns
site deployment and Worker bundling. No split or access flag changes here.
Parent: MODEL-245. MODEL-247 is 245-B.

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

Deploy jobs set `MODELSPEC_REQUIRE_DATA_DIR=1` when `DATA_SPLIT_ENABLED` is
true. The build then fails, exit 2, if neither `--data-dir` nor
`MODELSPEC_DATA_DIR` is given, instead of silently publishing the public image
as if it were fresh.

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

Rank Worker: it needs no runtime access to the private repository, but its
bundle step is not data-free: `api/worker/vendor.py` copies registry and
hardware files from the repository root. See "Gaps 245-B must close" below.

The Actions read+write permission on `MODELSPEC_DATA_DISPATCH_TOKEN` also
allows reading private Actions artifacts and logs. Treat it like
`MODELSPEC_DATA_TOKEN`: keep it away from checked-out code and installs in
public jobs, and never expose it to pull-request or fork runs. Its intended
use is dispatch, but its permission is broader than dispatch.

## Writers

All six data writers run in `turbobeest/modelspec-data`. Their workflow files
are submitted there on `writers-setup`. Reviewable source copies live in the
public engine under `.github/private-writers/`, which Actions does not execute.
Each private workflow checks out the public engine at a full commit SHA,
without a private-engine credential, and uses its own `GITHUB_TOKEN` for git,
issues and pull requests. No writer auto-merges a pull request.

| Workflow | Writes | Cadence in the private repo |
| --- | --- | --- |
| `daily-research.yml` | `models/**`; research scratch outputs stay uncommitted | daily; manual dry run |
| `leaderboard-refresh.yml` | `models/`, verification log and queue events | weekly; manual dry run |
| `price-reread.yml` | `offerings/`, verification log and queue events | weekly; manual dry run |
| `speed-probe.yml` | `measurements/speed/**` | manual only; existing paid caps preserved |
| `release-signals.yml` | `models/`, `verification/` | public hourly count gate dispatches only when work exists |
| `curation-benchmarks.yml` | `benchmarks/` | public trial/weekly cadence gate dispatches when due; private watcher decides whether drafting is needed |

The six old public workflow files have no schedules. Their manual dispatches
only print the private workflow URL. `release-watch.yml` remains a public-source
watcher and dispatches private processing when it posts discoveries. The new `release-signals-gate.yml` publishes only a pending-work count,
with no pending payload artifact, and `curation-gate.yml` decides only whether
its cadence is due. Both dispatch with `MODELSPEC_DATA_DISPATCH_TOKEN`. Curation stays disabled
until the existing `DATA_SPLIT_ENABLED` repository variable is true. Its
dispatch job has no checkout or dependency installation.

### Writer root and git audit, closed by MODEL-247 W

Writers run in the private checkout rather than in the reader overlay. The
reader overlay's `.git` still belongs to the public engine.
`scripts/prepare_data_writer.py` copies tracked engine code beside private data,
excluding every `DATA_PATHS` entry, `.github/` and the private README. It puts
copied code and generated Python files in the private checkout's local git
exclude file. It refuses any origin other than `turbobeest/modelspec-data`.
Physical copies make `__file__`-derived roots resolve to the private checkout;
registry vocabulary comes from the pin and registry data remains private.

The audit covered writer scripts, their validators, the speed harness, curation,
release-signal processing, accuracy and recall checks, and workflow git calls:

- Daily research, leaderboard refresh and speed scripts have no git subprocess
  calls. Their PR action uses `path: data`, stages only declared data paths, and
  authenticates with the private repository's token.
- Price re-read's workflow checks git status and the verification-log diff from
  the private working directory. Its two PR actions also use `path: data`.
- `scripts/validate_pr.py` sets git's working directory from its own file root.
  The copied validator reads and compares the private `origin/main`.
- Release-signal workflow git config, branch, add, commit and push commands all
  run under `data/`. Rechecks follow only private PR URLs; old public links do
  not receive new comments or updates. The private pending job builds its own
  matrix and holds its snapshot as a private artifact.
- `scripts/curation/propose.py` uses the caller's working directory for every
  git operation and derives page paths from its copied file root. The private
  workflow supplies `github.repository` to every issue and PR operation.
- The accuracy and recall scripts and `modelspec verify` resolve their roots to
  copied engine code in the private checkout. Their workflow runs do not call
  the CLI's separate PR-opening command.

A fixture test executes copied writer code, stages its output in a real private
checkout, and proves the public checkout receives no write. It also checks that
private sources, README and workflows survive composition, code is ignored,
and a public git origin is refused.

### Gaps 245-B (MODEL-247) must close

MODEL-247 W closes these gaps:

- All six fresh-data writers and their data PRs move to the private repository.
  Writer artifacts, including raw speed runs, remain there.
- The public leak guard scans `.yml` and `.yaml` workflows and local composite
  actions, follows local reusable workflows, and treats inherited secrets,
  any `MODELSPEC_DATA` marker and any `turbobeest/modelspec-data` reference as
  private access. In those jobs it rejects artifact uploads, cache actions
  including restore and third-party caches, public PR creation and git push.
  Only `data-lag.yml` may open the eligible old-image PR.
- Shell checks flag common output commands, including `sed`, `awk`, `find`,
  `base64`, tracing, summary writes and aliases for data paths. Job outputs
  are restricted to literal scalar decisions. Diagnostics name steps without
  quoting commands. This is a static lint, not a proof that arbitrary scripts
  or third-party actions cannot leak. It cannot follow arbitrary subprocesses,
  dynamic shell evaluation or arbitrary output transformations; review remains
  necessary. External reusable workflows with private access are refused.
- Private parser and loader boundaries redact YAML, card, source, registry,
  hardware, host and verification-log errors and suppress exception chains.
  Location recovery fails closed to line 1. A plain YAML value containing
  `---` is never treated as a front-matter separator. Private writer jobs set
  `MODELSPEC_REQUIRE_DATA_DIR=1`; data-dir arguments, environment, checkout
  origins and nested `modelspec-data` paths also activate redaction.
- Public release watching detects source changes without reading the frozen
  catalogue. Private release processing resolves catalogue identity. Public
  watching opens no burst or outage issues and dispatches only newly filed
  discoveries, so a deduplicated discovery does not dispatch on every run.

MODEL-247 S separately owns these deployment gaps:

- `api/worker/vendor.py` must use private registry and hardware data, supplied
  through `--data-dir`, and `rank-api.yml` must check out that data.
- `deploy-sites.yml` must restrict private access to main deployment, avoid
  uploading fresh builds as public artifacts and deploy from the same job or a
  non-public channel.

The freeze guard's documented limits remain: it trusts branch names, ignores
some derived files and skips binary contents. Repointing writers stops public
PR publication; branch protection and human review still matter.

### Public CI must not leak the private data

Actions logs, artifacts and caches on a public repository are public. A job
with any `MODELSPEC_DATA` environment or secret marker, or a private checkout,
must have no artifact upload, Pages artifact upload or cache save. It must
never print data: no `cat`, `head`, `tail`, `echo`, `git diff`, `git show` or
  `git log` of data paths, and no workflow-command annotations quoting rows.

Counts and pass/fail are fine. `tests/test_data_workflows.py` statically checks
workflow declarations and local actions. Passing the lint does not prove that
all scripts or third-party actions run by a workflow are safe.

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

After the private writer PR and public W change merge, no fresh writer opens
public data PRs. Jamie can then make `Data freeze` required. The lag job alone
publishes eligible old data images through human-reviewed public PRs.

## The lag job

`scripts/data_lag.py`, run weekly by `.github/workflows/data-lag.yml`.

1. `cutoff = today - 9 calendar months`, clamped to the month end
   (`2027-05-31 -> 2026-08-31`, `2026-11-30 -> 2026-02-28`).
2. Walk the private default branch first-parent and pick the newest commit
   whose committer date is at or before the cutoff **and whose whole history
   has nothing newer**. A backdated commit on top of fresh history is
   refused. None means no-op (`no-image-yet`).
3. Extract that commit's data paths (`git archive`), replace the public data
   directories with them, and write `data-image.json`:
   `as_of` (the cutoff), `lag_months`, `source_repo`, `source_commit`,
   `source_committed` (that commit's own committer date), `paths`.
4. If the tree is already that image the job reports `unchanged` and opens
   nothing.
5. Otherwise it opens a pull request from `data-lag/image`. `automerge.yml`
   skips `data-lag/image` (the only lag branch): a human merges it.

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
  `source_committed` after today's cutoff; or
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

The private repository was seeded on 2026-09-30 with the current `DATA_PATHS`.
The W setup PR adds only workflows and its minimal README. A single seed commit
is enough for the lag schedule. Public data and history remain unchanged.

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
| Seed `modelspec-data` with the current `DATA_PATHS` | Done, 2026-09-30 |
| Main-only private site deployment and private Worker bundling | MODEL-247 S |
| Repoint six writers and audit git/file roots; harden leak guard and parser errors | MODEL-247 W, submitted |
| Create `MODELSPEC_DATA_DISPATCH_TOKEN` in the public repo, fine-grained, scoped only to `modelspec-data`, Actions read+write | Jamie |
| Merge the private `writers-setup` PR after the pinned public engine commit is available | Jamie |
| Enable private Actions to create PRs and provide the writers' existing provider/research credentials listed in its README | Jamie |
| Move public engine tests to fixtures | 245-C |
| Make "Data freeze" a required check, after the writers are repointed | Jamie |
