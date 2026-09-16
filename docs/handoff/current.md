# Current ModelSpec state — 2026-09-14

This is the current-state entry for a fresh Claude, Codex, or Grok session,
including a DPF integration session. Historical freeze, census-run, and Phase 1
instructions are not current policy.

**As of:** 2026-09-14, branch built from `origin/main` `0b4a612`
(`catalogue: Liquid LFM2.5 Audio total from Hub safetensors (#33)`).
Working-tree bytes are the source; the commit is context until this lands.

## Serving path

YAML cards export to versioned JSON on Cloudflare Pages. The CLI downloads that
export (`modelspec snapshot fetch`, default origin `https://modelspec.dev`) and
answers from the cache. **No database is on the serving path.** MODEL-2 closed
on that basis: static Pages JSON plus `export_schema_version`, refuse an
incompatible major. Not R2, not D1.

Source locators:

| Fact | Where |
|---|---|
| Export shape / `export_schema_version` `"2.0"` | `pipeline/export.py` (`EXPORT_SCHEMA_VERSION`) |
| Snapshot fetch, pin, refuse other major | `cli/modelspec/snapshot.py` (`DEFAULT_ORIGIN`, `PARTS`, `EXPORT_SCHEMA_VERSION`) |
| CLI `--json` envelope `schema_version` `"1.0"` and exit codes 0–4 | `cli/modelspec/offline.py`; contract: [`../cli-contract.md`](../cli-contract.md) |
| Site + CLI consume one export | `pipeline/export.py` module docstring; `pipeline/build.py` |
| Pages 25 MiB file cap | `pipeline/graph.py` (`CLOUDFLARE_PAGES_MAX_FILE_BYTES`) |
| Rank implementation | `pipeline/ranking.py` (`rank`, `rank_report`, `_basis`) |
| Shared floors and policy | `api/ranking/engine.py` (`MIN_BENCHMARK_COVERAGE`, `WIZARD_BENCHMARK_COVERAGE`, `MIN_BENCHMARK_COUNT`, `ranking_policy`) |
| Tests: envelope, pin, floors, provenance | `tests/test_cli_snapshot.py`, `tests/test_ranking.py`, `tests/test_incomplete_evidence_ranking.py`, `tests/test_export.py` |

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
- **MODEL-5:** still open, newly blocked. Daily-research PRs are opened by
  `peter-evans/create-pull-request` with the default `GITHUB_TOKEN`. GitHub will
  not run required checks on those PRs, so they cannot merge. Measured:
  [PR #35](https://github.com/turbobeest/modelspec/pull/35) `research/daily-models`,
  author `app/github-actions`, `statusCheckRollup: []`, check-runs total 0,
  `mergeStateStatus: BLOCKED`. Required checks on `main` are **Run pytest** and
  **Build both sites** (GitHub Actions app 15368). Fix: a PAT or GitHub App
  token as the workflow `token`. **Jamie has to create that credential.** Do
  not auto-merge `research/*`.
- **MODEL-3 / MODEL-6:** do not start. Assessment:
  [`../agent-commerce-assessment.md`](../agent-commerce-assessment.md).
- **MODEL-39:** still Todo (graph export size / required site build). Re-measure
  the 25 MiB cap on a full main build; do not bypass the guard.

## Ranking floors (do not re-ask)

CLI/API **0.50**, wizard **0.25**, count floor **2**. Cost default
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
