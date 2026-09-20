# Current ModelSpec state — 2026-09-20

This is the current-state entry for a fresh Claude, Codex, or Grok session,
including a DPF integration session. Historical freeze, census-run, and Phase 1
instructions are not current policy.

**As of:** 2026-09-20, `origin/main` `7a63129`
(`schema: decision-model class and inapplicable-vs-unknown fields (#150)`),
deployed: the Worker and the live export both report
`export_schema_version: 3.0`.

## Read this first if you are picking the work up

Three draft PRs are open and **all three are finished work waiting on Jamie's
merge decision**, not work in progress. Nothing is half-written.

| PR | Ticket | What it is | Why it is still a draft |
| --- | --- | --- | --- |
| [#152](https://github.com/turbobeest/modelspec/pull/152) | MODEL-101 | The TypeSafe Jev card, the catalogue's first `decision-model`, plus the guard that stops any TypeSafe card field being written by a Jev judgment | Jamie reviews a card about a supplier we pay |
| [#153](https://github.com/turbobeest/modelspec/pull/153) | MODEL-102 | A **negative result**: the Jev→LLM cascade measured 97.6% at $0.188/1,000 correct, then misattributed 6 of 383 on the MODEL-82 guard set. Ships switched off, with the gap pinned by a test | It documents something we chose not to ship |
| [#154](https://github.com/turbobeest/modelspec/pull/154) | MODEL-100 | `class-fit`: which *class* of model a task needs, as a keyless static file plus a CLI command | New public surface |

**Do not mark any of them ready without Jamie saying so** — ready means
auto-merge (`automerge.yml`).

### What is switched off, deliberately

- **`BILLING_ENABLED` is `false`** (`api/worker/wrangler.jsonc`). Billing went
  live on 2026-09-20 and was paused the same day: Stripe Tax is on every
  Checkout, but the live account holds **no Rhode Island registration**, so
  Stripe computes 0% silently and the LLC still owes the tax. The live Price
  ids are already in `api/worker/tiers.json` — only the flag moves. **MODEL-96**
  is the re-enable ticket and lists every step.
- **`ACCESS_ENFORCED` is `false`**: an unkeyed request is still served free.
- **`X402_ENABLED` is `false`**.
- **`escalation.enabled` is `false`** (`scripts/attribution.yaml`) — the cascade
  from #153, measured and refused.

### Waiting on Jamie, nobody else can do these

1. **Rhode Island Division of Taxation.** Who holds the current sales tax
   permit — Jamie personally under the dev-mux DBA, or Sparks & Sawdust LLC?
   That one answer unblocks MODEL-96 (and therefore any revenue) and decides 2.
2. **Stripe's legal entity name** reads "James J Ter Beest III", not the LLC.
   It is the **shared** legal entity: changing it changes dev-mux's live
   account too, and a name that does not match the EIN on file can trigger
   re-verification and hold payouts. Establish which EIN belongs to which name
   before touching it.
3. **A sentence in the adopted neutrality commitment.** It covers money coming
   *in* (no paid placement, no referral fees) but says nothing about ModelSpec
   *buying from* a lab it catalogues. `neutrality_commitment()` in
   `api/ranking/engine.py` is held to `docs/legal/neutrality.md` by
   `tests/test_legal.py`; the legal documents were adopted v1.0 on 2026-09-19,
   so editing them is Jamie's call, not an agent's.
4. **A $5 live smoke test with a real card**, once billing is back on.

### The open tickets, and what they are blocked on

- **MODEL-96** re-enable billing — blocked on the tax office call.
- **MODEL-95** Search Console / Bing — verified and sitemaps submitted on both
  domains; the only open item is the first coverage review, which needs Google
  to crawl. Indexed pages were 0 on 2026-09-20.
- **MODEL-69** keys and limits — its acceptance criteria still describe the
  10/day free tier that MODEL-93 replaced with credits. Needs rewriting against
  credits, and Jamie's call on `ACCESS_ENFORCED`.
- **MODEL-100/101/102** — the three PRs above.

### Standing rules a new session will not guess

- **One worktree and one chat session per ticket** (Jamie, 2026-09-20). The
  exception made that day: MODEL-97 and MODEL-98 shared one worktree because
  they shared one contract bump.
- **Automate the human steps.** Drive dashboards in the browser rather than
  handing Jamie a checklist. Come back to him only for a government ID value,
  a credential, a legal attestation, or an action a permission classifier
  refuses — and for that last case, say what was blocked and ask, rather than
  converting it into manual work for him.
- **The research workflow's scratch files** (`survey.txt`, `validation.json`,
  `scripts/attribution_judgments.jsonl`) are no longer committed: `add-paths`
  in `daily-research.yml` limits the daily PR to `models/**` (#148).
- **The session scratchpad is shared between concurrent sessions.** A worker
  had a file overwritten mid-task on 2026-09-20. Give each worker its own
  subdirectory.

## Serving path

YAML cards export to versioned JSON on Cloudflare Pages. The CLI downloads that
export (`modelspec snapshot fetch`, default origin `https://modelspec.dev`) and
answers from the cache. **No database is on the static serving path.** MODEL-2
closed on that basis: static Pages JSON plus `export_schema_version`, refuse an
incompatible major. Not R2, not D1.

That sentence describes the **static** path — the one that answers a page view
and a `snapshot fetch`. It is not a prohibition on a keyed layer beside it, and
should not be quoted as one. MODEL-68 built the first such layer:

**`POST https://api.modelspec.dev/v1/rank`**, a Cloudflare Worker
(`api/worker/`, deployed by `.github/workflows/rank-api.yml` on push to main
only). It is stateless — no KV, no D1, no R2 — fetches the same static export,
and ranks by running the repository's own `pipeline/ranking.py`, vendored into
the bundle verbatim rather than reimplemented. Its answers are byte-identical to
`modelspec offline rank --json` for the same input against the same build, held
there by `tests/test_rank_worker.py`. Contract, status codes and the deploy
scars: [`../rank-api.md`](../rank-api.md).

**`POST https://api.modelspec.dev/v1/policy-check`** (MODEL-80) rides the same
Worker and answers a caller's policy document per model **and per platform**,
with `pass` / `fail` / `undetermined`. It is the first thing here that reads a
store: **Workers KV**, holding the policy determinations, which live outside
this repository permanently and are loaded by a step run from the private
checkout — never by this repository's CI. The public half it reads is
`/api/policy/catalogue.json`, written by `pipeline/policy_export.py`. Contract,
trust boundary and what still needs Jamie:
[`../policy-check-api.md`](../policy-check-api.md).

Source locators:

| Fact | Where |
|---|---|
| Export shape / `export_schema_version` `"2.0"` | `pipeline/export.py` (`EXPORT_SCHEMA_VERSION`) |
| Snapshot fetch, pin, refuse other major | `cli/modelspec/snapshot.py` (`DEFAULT_ORIGIN`, `PARTS`, `EXPORT_SCHEMA_VERSION`) |
| CLI `--json` envelope `schema_version` `"1.0"` and exit codes 0–4 | `cli/modelspec/offline.py`; contract: [`../cli-contract.md`](../cli-contract.md) |
| Site + CLI consume one export | `pipeline/export.py` module docstring; `pipeline/build.py` |
| Pages 25 MiB file cap | `pipeline/graph.py` (`CLOUDFLARE_PAGES_MAX_FILE_BYTES`) |
| Rank implementation | `pipeline/ranking.py` (`rank`, `rank_report`, `_basis`) — one implementation, shared by the CLI, the sites and the rank Worker |
| Rank API (MODEL-68) | `api/worker/` (`src/rank_service.py`, `vendor.py`); contract [`../rank-api.md`](../rank-api.md) |
| Policy-check API (MODEL-80) | `api/worker/src/policy_service.py`, `load_determinations.py`, `pipeline/policy_export.py`; contract [`../policy-check-api.md`](../policy-check-api.md) |
| Shared floors and policy | `api/ranking/engine.py` (`MIN_BENCHMARK_COVERAGE`, `WIZARD_BENCHMARK_COVERAGE`, `MIN_BENCHMARK_COUNT`, `ranking_policy`) |
| Tests: envelope, pin, floors, provenance | `tests/test_cli_snapshot.py`, `tests/test_ranking.py`, `tests/test_incomplete_evidence_ranking.py`, `tests/test_export.py` |
| Tests: rank API byte-identity, no-match, deploy gate | `tests/test_rank_worker.py`, `tests/test_ci_workflows.py` |

Live check 2026-09-14, cache-busted `GET https://modelspec.dev/api/rank/profiles.json`:
`cli_min_benchmark_coverage` 0.5, `wizard_min_benchmark_coverage` 0.25,
`min_benchmark_count` 2, `ordering` `conservative_lower_bound`.

## CLI contract (DPF)

DPF consumers (DPF-22 and the ticket author) rely on [`../cli-contract.md`](../cli-contract.md).
That document is the promised schema and exit codes. **Do not change them in a
docs-only pass.** Provenance text there now matches `_basis`: results may be
`unverified-legacy`, `mixed`, `partial-verified`, or `verified` (or `none` when
nothing contributed). `verified` is not a quality certificate.

The DPF Graphify map (`dpf-operating-contracts`) **does not index this
repository**. Its exclusions say so. This repo's map is
[`../../graphify-out/README.md`](../../graphify-out/README.md), registered
globally as `modelspec-architecture` when the snapshot is refreshed. Canonical
contract URL after merge:
`https://github.com/turbobeest/modelspec/blob/main/docs/cli-contract.md`.

## Freeze

The 2026-09-12 hold is **lifted**. The record is kept at
[`session-freeze-2026-09-12.md`](session-freeze-2026-09-12.md). GitHub PR #34
(`docs/session-freeze-2026-09-12`) added that notice; this file supersedes it.

## Remainder and do-not-start

- **MODEL-7, MODEL-30, MODEL-34:** Linear **Done**. Details:
  [`mvp-remainder.md`](mvp-remainder.md).
- **MODEL-5:** still open by design (it becomes a daily cron). The token
  blocker is resolved: the workflow uses the `RESEARCH_PR_TOKEN` PAT and fails
  fast if it is empty, so required checks run on `research/daily-models` PRs
  (e.g. [PR #106](https://github.com/turbobeest/modelspec/pull/106), all green).
  A human still reviews and merges each one; do not auto-merge `research/*`.
- **MODEL-3:** do not start (one Worker serving site + API + snapshot + MCP).
  **MODEL-6 is cancelled**, superseded by MODEL-68, MODEL-69, MODEL-73 and
  MODEL-75. MODEL-68 is built (above). **MODEL-69** (keys, rate limits,
  sandbox) and the billing tickets are the next pieces and are not started.
  Older assessment, now partly superseded:
  [`../agent-commerce-assessment.md`](../agent-commerce-assessment.md).
- **MODEL-39:** still Todo (graph export size / required site build). Re-measure
  the 25 MiB cap on a full main build; do not bypass the guard.

## Ranking floors (do not re-ask)

CLI/API **0.50**, wizard **0.25**, count floor **2**. The rank Worker reads them
from `api/ranking/engine.py` and writes none of them down; a floor literal in
`api/worker/` fails the suite. Cost default
`cost_weight: 0`. `speech_to_text` hidden from featured profiles until it
produces a ranking. `image_generation` not featured until `clip_score` range is
sourced.

## Cards are DATA

`models/**` and `benchmarks/**` are catalogue data. Presence in git or in a
graph is not fact-checking. Coverage policy:
[`architecture-map.md`](architecture-map.md).

## Worktrees and CodeGraph

Use an isolated worktree. Initialise CodeGraph **in that worktree**. The index
under `/Users/terbeest/dev/modelspec/.codegraph` is that checkout only.
Procedure: [`worktrees.md`](worktrees.md).

## Historical — do not promote as current

- [`session-freeze-2026-09-12.md`](session-freeze-2026-09-12.md) — hold record
- [`../system-architecture-v3.md`](../system-architecture-v3.md) — 2026-04 FalkorDB-served design
- [`../superpowers/`](../superpowers/) — dated plans and census notes
- Root `CLAUDE.md` Phase 1 / FastAPI→FalkorDB diagram (rewritten in this pass)

Graphify refresh probe: `MODEL-40-PROBE-2026-09-14`.
Graphify incremental refresh token: `MODEL-40-REFRESH-2026-09-14`.
