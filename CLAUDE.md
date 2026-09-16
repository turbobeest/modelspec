# CLAUDE.md — ModelSpec

**Current orientation:** [`docs/handoff/current.md`](docs/handoff/current.md).
Standing rules: [`docs/handoff/README.md`](docs/handoff/README.md).
DPF / offline CLI contract: [`docs/cli-contract.md`](docs/cli-contract.md).
Codex/AGENTS parity: [`AGENTS.md`](AGENTS.md).
Contract versioning (MODEL-59): a change that widens a contract field's range (nullable, new enum value, may be absent) bumps that contract's major version. See [`docs/cli-contract.md`](docs/cli-contract.md).

This file used to describe Phase 1 and a FalkorDB-served architecture. That is
historical. MODEL-2 closed on a **static Pages export**. There is no R2/D1 on
the serving path.

## What is this?

ModelSpec catalogs AI models (LLMs, embeddings, image, speech, safety
classifiers, …) as YAML+Markdown cards, exports them to versioned JSON, and
serves rankings through a static Web UI and an offline CLI. DPF's ticket author
calls the CLI.

## Architecture (current)

```
models/*.md ──▶ pipeline/build.py ──▶ static JSON on Cloudflare Pages
                                      (modelspec.dev /api/*.json)
                                            │
CLI `snapshot fetch` ───────────────────────┘
Wizard / 3D graph read the same JSON in the browser.

FalkorDB ── optional local exploration (`modelspec stats|search|info`).
            Not required to rank, fit, or render the sites.
```

Pin identity for a snapshot: `build.commit` plus `build.export_schema_version`
(`pipeline/export.py`, currently `"2.0"` — MODEL-77 reshaped the published
policy fields). That is not the CLI `--json`
envelope (`cli.modelspec.offline.SCHEMA_VERSION`, also `"1.0"`) and not
`rankings.json` (`schema_version` `"2.0"`).

## Ranking floors (product defaults)

In `api/ranking/engine.py`:

- CLI / API: `MIN_BENCHMARK_COVERAGE = 0.50`, `MIN_BENCHMARK_COUNT = 2`
- Wizard: `WIZARD_BENCHMARK_COVERAGE = 0.25`

Live `https://modelspec.dev/api/rank/profiles.json` publishes the same policy.
Do not change a floor without Jamie.

## Provenance

Ranked rows report `evidence_basis`: `none`, `unverified-legacy`, `mixed`,
`partial-verified`, or `verified`. That is input provenance, not a quality
verdict. The CLI contract documents the labels; `_basis` in
`pipeline/ranking.py` produces them.

## Schema (still the card source of truth)

`schema/` is the card and ontology source. Null on a card means "not yet
researched" or "not published" — a null beats a guess.

- `schema/enums.py` — ModelType, ArchitectureType, LicenseType, Tier, …
- `schema/card.py` — `ModelCard` (universal template, YAML serialization)
- `schema/graph.py` — how a card becomes FalkorDB nodes/edges **when ingested
  locally**. Ingestion is not the serving path.

Ontology: [`docs/graph-ontology.md`](docs/graph-ontology.md). The 2026-04
design doc [`docs/system-architecture-v3.md`](docs/system-architecture-v3.md)
is historical.

## Project layout (serving-relevant)

```
schema/      card + graph types
models/      DATA — model cards (not fact-checked by the architecture map)
benchmarks/  DATA — benchmark wiki pages
hardware/    DATA — device SKUs
pipeline/    export, ranking, site build
cli/         Typer CLI; offline path in cli/modelspec/offline.py + snapshot.py
api/         ranking engine shared with the pipeline
web3d/       static explorer + wizard
docs/        contracts and handoff
tests/
```

## Development

```bash
# Isolated worktree, never someone else's checkout
git -C /Users/terbeest/dev/modelspec worktree add -b <branch> \
  /Users/terbeest/dev/worktrees/<name> origin/main
cd /Users/terbeest/dev/worktrees/<name>

PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q
```

Required checks on `main`: **Run pytest** and **Build both sites**.

Optional FalkorDB for graph commands: `docker compose up -d`, browser
`http://localhost:3000`.

## Do not start

MODEL-3 (Worker), MODEL-6 (payment rail). Do not auto-merge `research/*`.
MODEL-5 daily PRs are opened with `GITHUB_TOKEN`, so required checks never
run; Jamie must install a PAT or GitHub App token.

## Architecture map

Bounded Graphify coverage, exclusions, and refresh:
[`docs/handoff/architecture-map.md`](docs/handoff/architecture-map.md) and
[`graphify-out/README.md`](graphify-out/README.md). Model and benchmark cards
are DATA. Worktree CodeGraph: [`docs/handoff/worktrees.md`](docs/handoff/worktrees.md).
