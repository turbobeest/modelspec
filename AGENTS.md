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

The JSON envelope and exit codes for `modelspec snapshot` / `modelspec offline`
are the contract. Read the file; do not reconstruct it from memory.

## Worktrees

Never check out a branch in another session's tree. Create a new worktree from
`origin/main`. CodeGraph indexes **this checkout only** — initialise and refresh
it here. Instructions: [`docs/handoff/worktrees.md`](docs/handoff/worktrees.md).

## Do not start

- **MODEL-3** (one Worker serving site + API + snapshot + MCP). **MODEL-6** is
  cancelled, superseded by MODEL-68/69/73/75. MODEL-68, the rank Worker, is
  built ([`docs/rank-api.md`](docs/rank-api.md)); MODEL-69 (keys, rate limits,
  sandbox) and the billing tickets are not started from here.
- Auto-merge of `research/*`. Daily-research PRs need a human, and today they
  cannot merge because they are opened with `GITHUB_TOKEN` so required checks
  never run. The token replacement is Jamie's.
