# MVP remainder

MODEL-7, MODEL-30 and MODEL-34 are **Done** (Linear, verified 2026-09-14).
They stay in this file as history so nobody reopens the settled questions.
The live remainder is **MODEL-5**, blocked in a new way that an agent cannot
clear.

Grok Build's job on MODEL-5 is still to be a **preparer**, not a decider, and
not to invent a merge path that bypasses required checks.

---

## MODEL-5 — Daily model research (open)

**Status: blocked on a GitHub token Jamie has to create.** Seven consecutive
green days still have not happened, and the PRs the workflow opens **cannot
merge** on the current token.

### What was measured 2026-09-14

- Workflow: `.github/workflows/daily-research.yml`.
- PR create step: `peter-evans/create-pull-request@v7` with **no** `token:`
  input, so it uses `GITHUB_TOKEN`.
- Permissions on the workflow are `contents: write` and `pull-requests: write`.
  That is enough to *open* a PR. It is not enough for GitHub to run other
  workflows on that PR (recursive-workflow guard).
- Required checks on `main`: **Run pytest** and **Build both sites**
  (branch protection, GitHub Actions app 15368).
- Open PR [#35](https://github.com/turbobeest/modelspec/pull/35)
  (`research/daily-models`, author `app/github-actions`, title "catalogue: 2
  newly released models"): `statusCheckRollup` empty, `check-runs.total_count`
  0, `mergeStateStatus: BLOCKED`, `mergeable: MERGEABLE`. The branch can merge
  in git; GitHub will not allow it until the required checks exist.

So the daily job can seed cards and open a PR, and that PR can sit forever.
`research/*` is also excluded from auto-merge, which is still correct: a human
must look. A human cannot merge while required checks have never run.

### What Jamie has to do

Create a **PAT or GitHub App token** with permission to open pull requests
*and* to trigger workflows on the resulting PR (classic fine-grained PAT with
`contents` + `pull-requests`, or a GitHub App installation token). Store it as
a repo Action secret and pass it as `token:` to `peter-evans/create-pull-request`.
Do not weaken branch protection to let unchecked `research/*` PRs merge.

This ticket's workers must not edit `.github/**`. Record the need; stop.

### What an agent can still do (unchanged)

* Watch the daily run. Report whether it completed and whether it opened a PR.
  Do not merge it.
* The survey still only covers **new models from models.dev**, while the ticket
  asks for every card against every listed source.
* The seeder still creates only a `models_dev_url` source and populates neither
  licence nor per-source freshness.
* **Prove the failure path deliberately** on a scratch branch if that has not
  been done.

**Close only when:** seven consecutive successful runs exist, a human-merged PR
has actually happened, required checks ran on that PR, and the
deliberate-failure test passed.

---

## MODEL-7 — Serve the benchmark wiki at benchgraph.dev (Done)

Linear **Done**. Site serves; domain property and sitemap (1,108 pages at
close) were the remaining acceptance. modelspec.dev Search Console lag is
MODEL-38, not a reopen of 7.

---

## MODEL-30 — Two defects in the ranking profiles (Done)

Linear **Done**. Shipped behaviour to keep:

1. `image_generation` stays out of featured profiles until `clip_score` range
   is sourced.
2. Default `cost_weight` is 0; price is `--price-sensitivity` / wizard control.
   Putting 0.10 on every profile made GPT-5.4 nano win coding on price.
3. `speech_to_text` is hidden from `FEATURED_PROFILES` until it produces a
   ranking (`04ce964` / PR #21).

Do not re-ask these.

---

## MODEL-34 — Ranking under unequal evidence (Done)

Linear **Done**. A model is ranked only if its measurements cover **≥50% of a
profile's benchmark weight across ≥2 benchmarks** on the CLI/API
(`MIN_BENCHMARK_COVERAGE`, `MIN_BENCHMARK_COUNT`). The wizard uses **0.25**.
Live `profiles.json` publishes both. Everything else is explicitly unranked.

Do not change a floor without Jamie.
