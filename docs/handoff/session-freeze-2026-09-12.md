# Session freeze — 2026-09-12

Jamie is holding **all further ModelSpec development** until refreshed tickets
next week (about four days). Do not start a 30-minute loop. Do not open PRs.
Do not Linear-Done anything from this freeze. Reopen this file first.

**Workspace:** `/Users/terbeest/dev/modelspec`
**Remote:** `turbobeest/modelspec`
**`origin/main` at freeze:** `0b4a612` — `catalogue: Liquid LFM2.5 Audio total from Hub safetensors (#33)`
**Open PRs:** none
**Scheduler:** cancelled (was `01a0924f-e11b-7431-851e-e090f5205120`)

Also read `docs/handoff/README.md` (standing rules). `mvp-remainder.md` is
stale on MODEL-7/30/34 — those are Done.

## Next week starts here

Linear already has two GTM tickets written 2026-09-11. They are the first
work after the hold, unless Jamie says otherwise.

| Ticket | State | What |
|---|---|---|
| [MODEL-39](https://linear.app/sparksandsawdust/issue/MODEL-39) | Todo | Deployable graph exports + require site build before auto-merge |
| [MODEL-40](https://linear.app/sparksandsawdust/issue/MODEL-40) | Todo | Current handoff + reproducible architecture map for DPF |

**MODEL-39 partial:** PR #28 landed (`graph: omit edge props on hairball views so Pages stays under 25 MiB`). `main` required checks are **Run pytest** and **Build both sites** (GitHub Actions app 15368). Re-measure `dist/modelspec/api/graph/views/hardware.json` against the 25 MiB cap on a full main build before calling 39 Done. Do not bypass the guard. Do not delete hardware rows to shrink the file.

**MODEL-40:** this freeze file is the current-state note. Root `CLAUDE.md` still says Phase 1. There is no root `AGENTS.md`. No `graphify-out/graph.json`. `docs/cli-contract.md` still says all results are unverified-legacy; provenance is now mixed/verified. MODEL-2 closed as **static Pages export**, not R2/D1.

## Standing product decisions (do not re-ask)

| Decision | Value |
|---|---|
| Coverage floors | CLI / API **0.50**; wizard **0.25**; count floor **2** (`MIN_BENCHMARK_COVERAGE`, `WIZARD_BENCHMARK_COVERAGE`) |
| Cost | default `cost_weight: 0`; CLI `--price-sensitivity`; wizard Price sensitivity |
| `speech_to_text` | hidden from `FEATURED_PROFILES` until it produces a ranking |
| `image_generation` | not featured until `clip_score` range is sourced |
| MODEL-2 | static Pages JSON + `export_schema_version` + refuse incompatible major. No R2/D1 |
| MODEL-3 / MODEL-6 | **do-not-start** (no Worker, no payment rail) |
| MODEL-9 | BenchGraph *graph* on the back burner |
| MODEL-11 | human + lawyer |
| MODEL-24 | taste, Claude + Jamie, later |
| Auto-merge | same-repo non-draft PRs squash-auto-merge when checks pass (`.github/workflows/automerge.yml`) |
| Never auto-merge | `research/*` (MODEL-5 daily cards) |
| Actions | workflow permissions **write** + can create PRs (needed for daily-research to open PRs) |

## Standing rules (still expensive)

1. Absence is data. Null beats a guess.
2. Wrong `total_parameters` is worse than none (1,589 false "it fits"). Hub `safetensors.total` only; never filenames.
3. Firecrawl budget lives in `scripts/benchmarks/fetch.py`.
4. Verify by running, not by ticket comments.
5. Record the exact variant (TB 4.0 ≠ `terminal_bench`).
6. A provider's table of a competitor is not evidence for that competitor.
7. Carding a missing model raises the unrankable count. Do not chase that metric.

## Closed this stretch (measured)

MODEL-2, 7, 30, 31, 32, 34, 37.

- MODEL-7: benchgraph.dev Domain property + sitemap **1,108** pages. modelspec.dev GSC was live-test OK, report lagged — [MODEL-38](https://linear.app/sparksandsawdust/issue/MODEL-38).
- MODEL-34: live `profiles.json` wizard 0.25 / CLI 0.50.
- MODEL-37: Hub safetensors totals on Cohere, Mistral (Mixtral 8x7B is **46.7B not 7B**), Kimi K2, DeepSeek V4.1 Flash, Liquid LFM2.5-Audio. Unique Hub maps **exhausted**. Skip Hub-200-no-count (Microsoft, RWKV, Google, Together, Salesforce, BAAI, NVIDIA, Allen-AI, …). Skip gated 401 Meta.

## Still open (do not drive unless next week's tickets say so)

| Ticket | State | Note |
|---|---|---|
| MODEL-1 | Backlog | Last. Repo restructure for online instantiation |
| MODEL-3 | Backlog | **Do not start** |
| MODEL-5 | In Review | Daily research. Human-merged #20 (Flash + Mercury 2.5; dropped misfiled glm-5-2). Needs **seven consecutive green days**. Never auto-merge `research/*` |
| MODEL-6 | Backlog | **Do not start** |
| MODEL-8 | Backlog | Authoring guides after card shape stops |
| MODEL-9 | Backlog | Back burner |
| MODEL-10 | Backlog | After MODEL-5 survives seven days |
| MODEL-11 | Backlog | Lawyer |
| MODEL-24 | Backlog | Taste |
| MODEL-25 | In Progress | Wave 2+3 largely filed. **No-datasheet holds:** Groq, Cerebras WSE-2, full-size RTX 4000 Ada, Jetson T3000/T2000. Do not invent bandwidth |
| MODEL-26 | Backlog | Comment on ticket: decode TPS ≠ agentic wall-clock. No Host nodes yet |
| MODEL-38 | Backlog | modelspec.dev sitemap in Search Console |
| MODEL-39 | Todo | GTM graph export + required site build |
| MODEL-40 | Todo | GTM current handoff for DPF |

## Catalogue / ranking facts

- ~1,337 cards. Newest `release_date` seen 2026-09-06.
- GPT-6 Astra: coding still unranked (SciCode 20%, count 1). Reasoning wizard-rankable at 0.25 (GPQA+CritPt 36%). Official TB 4.0 is `terminal_bench_v4_0`, not profile `terminal_bench`.
- METR Time Horizon 1.1 pages: `metr_time_horizon`, `_50`, `_80`. Unit **minutes** (YAML). Not in ranking profiles.
- Graph hairball views omit edge properties so Pages stays under 25 MiB.

## How to reopen

1. `git fetch origin && git checkout main && git pull`
2. Read this file, then `docs/handoff/README.md`
3. Ask Jamie which refreshed tickets to run — default guess is MODEL-39 then MODEL-40
4. Do not recreate a 10-minute or 30-minute overnight loop unless Jamie asks
5. Linear operator of record is this Mac's Grok session; do not Linear-Done without measured ACs
