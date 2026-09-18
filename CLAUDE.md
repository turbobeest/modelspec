# CLAUDE.md — ModelSpec

**Current orientation:** [`docs/handoff/current.md`](docs/handoff/current.md).
Standing rules: [`docs/handoff/README.md`](docs/handoff/README.md).
DPF / offline CLI contract: [`docs/cli-contract.md`](docs/cli-contract.md).
Codex/AGENTS parity: [`AGENTS.md`](AGENTS.md).
Contract versioning (MODEL-59): a change that widens a contract field's range (nullable, new enum value, may be absent) bumps that contract's major version. See [`docs/cli-contract.md`](docs/cli-contract.md).

This file used to describe Phase 1 and a FalkorDB-served architecture. That is
historical. MODEL-2 closed on a **static Pages export**: no R2 and no D1 on the
**static** serving path, which is the path that answers `modelspec.dev` and
feeds `modelspec snapshot fetch`. That rule describes that path and binds it.

It does not forbid a keyed layer beside it. MODEL-68 added one: a Cloudflare
Worker on `api.modelspec.dev` serving `POST /v1/rank`. It holds no store of its
own — no KV, no D1, no R2 — and computes each answer from the same static export
by running the repository's own `pipeline/ranking.py`. See
[`docs/rank-api.md`](docs/rank-api.md).

MODEL-80 added `POST /v1/policy-check` on that same Worker, and it **does** read
a store: **Workers KV**, holding the policy determinations, which are private
and are never in this repository. That is the enrichment path, not the static
one, and the MODEL-2 rule does not bind it — do not quote that rule against the
KV binding in `api/worker/wrangler.jsonc`. Trust boundary and the reasoning:
[`docs/policy-check-api.md`](docs/policy-check-api.md).

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
CLI `snapshot fetch` ───────────────────────┤
Wizard / 3D graph read the same JSON in the browser.
                                            │
Worker `POST api.modelspec.dev/v1/rank` ────┘  MODEL-68; stateless, same JSON,
                                               same scorer, no store of its own.

Worker `POST api.modelspec.dev/v1/policy-check`  MODEL-80; the same static JSON
   │                                             (`/api/policy/catalogue.json`)
   └── Workers KV ── the policy determinations, private, loaded from outside
                     this repository. See docs/policy-check-api.md.

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

`ranking_policy()` also carries `neutrality` — the honest-broker rule and the
permanent refusal of referral fees, paid placement and provider-paid visibility,
published as data beside the floors so an agent can check it rather than trust
it (MODEL-70). Single source: `neutrality_commitment()` in
`api/ranking/engine.py`; drafts in `docs/legal/`, still unadopted. Editing those
strings edits the published terms, and `tests/test_legal.py` fails if the prose
and the JSON drift. Neither is a routine edit.

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

MODEL-3 (the one Worker that would serve site + API + snapshot + MCP together).
MODEL-6 is **cancelled**, superseded by MODEL-68/69/73/75. MODEL-68 (the rank
Worker) is built — see [`docs/rank-api.md`](docs/rank-api.md); do not start
MODEL-69 (keys, limits, sandbox) or the billing tickets from here.
Do not auto-merge `research/*`.
MODEL-5 daily PRs are opened with `GITHUB_TOKEN`, so required checks never
run; Jamie must install a PAT or GitHub App token.

## Architecture map

Bounded Graphify coverage, exclusions, and refresh:
[`docs/handoff/architecture-map.md`](docs/handoff/architecture-map.md) and
[`graphify-out/README.md`](graphify-out/README.md). Model and benchmark cards
are DATA. Worktree CodeGraph: [`docs/handoff/worktrees.md`](docs/handoff/worktrees.md).
