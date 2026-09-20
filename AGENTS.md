# AGENTS.md — ModelSpec

**Current orientation:** [`docs/handoff/current.md`](docs/handoff/current.md).
Standing rules: [`docs/handoff/README.md`](docs/handoff/README.md).
DPF / offline CLI contract: [`docs/cli-contract.md`](docs/cli-contract.md).
Architecture map: [`graphify-out/README.md`](graphify-out/README.md).
Worktrees and CodeGraph: [`docs/handoff/worktrees.md`](docs/handoff/worktrees.md).
Contract versioning (MODEL-59): a change that widens a contract field's range (nullable, new enum value, may be absent) bumps that contract's major version. See [`docs/cli-contract.md`](docs/cli-contract.md).

This file is the Codex / ChatGPT.app / Cursor / Grok Build entry. Claude Code
also reads [`CLAUDE.md`](CLAUDE.md). Do not fork serving-path facts per TUI.

## Serving path

Static-first. YAML cards in `models/` export to JSON on Cloudflare Pages
(`modelspec.dev`). The CLI fetches that export into a local snapshot and ranks
offline. **No database is on the static serving path** — MODEL-2's "not R2, not
D1" rule describes that path. FalkorDB is optional local graph exploration only.

Beside it, MODEL-68 serves `POST api.modelspec.dev/v1/rank` from a Cloudflare
Worker: stateless, no KV/D1/R2, reading the same static export and running the
same `pipeline/ranking.py`. The MODEL-2 rule is not a prohibition on that layer.
Contract: [`docs/rank-api.md`](docs/rank-api.md).

MODEL-80 added `POST /v1/policy-check` to that Worker: a caller's policy
document answered per model **and per platform**, `pass` / `fail` /
`undetermined`. It reads **Workers KV**, holding the policy determinations —
private, never in this repository, loaded from the private checkout and not by
this repository's CI. The MODEL-2 rule does not bind that path either. Contract
and trust boundary: [`docs/policy-check-api.md`](docs/policy-check-api.md).

The JSON envelope and exit codes for `modelspec snapshot` / `modelspec offline`
are the contract. Read the file; do not reconstruct it from memory.

MODEL-100 added **class fit**: which *class* of model a problem needs, before
ranking within one. `api/classes.py` is a view over `ModelType` (what it
consumes, emits, decides); `api/class_fit.py` decides over it and refuses when
the evidence cannot separate two classes. **No number orders one class above
another**, and cost-to-correct evidence (MODEL-99) must never reach
`rank_score` — the scorer imports neither module and a test enforces it. The
rule is published keyless at `/api/rank/class-fit.json`. Design:
[`docs/design/class-selection.md`](docs/design/class-selection.md).

## Worktrees

Never check out a branch in another session's tree. Create a new worktree from
`origin/main`. CodeGraph indexes **this checkout only** — initialise and refresh
it here. Instructions: [`docs/handoff/worktrees.md`](docs/handoff/worktrees.md).
Tests: `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q`
or `-n auto --dist loadfile` (what the "Run pytest" check uses).

## Do not start / do not touch

- **MODEL-3** is not a one-Worker rebuild: the site stays on Pages (Jamie,
  2026-09-18). What remains is MODEL-95 (Search Console, Bing) and a traffic
  projection. **MODEL-6** is cancelled, superseded by MODEL-68/69/73/75.
- MODEL-68/69/73/75/93 are built (rank Worker, keys, Stripe Checkout, x402,
  credit ledger). `ACCESS_ENFORCED`, `BILLING_ENABLED` and `X402_ENABLED` ship
  off; turning one on, or adding live Stripe keys, is Jamie's call.
- Auto-merge of `research/*`. Daily-research PRs need a human. They are opened
  with the `RESEARCH_PR_TOKEN` PAT, so required checks run and they can merge.
