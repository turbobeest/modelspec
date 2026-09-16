# AGENTS.md — ModelSpec

**Current orientation:** [`docs/handoff/current.md`](docs/handoff/current.md).
Standing rules: [`docs/handoff/README.md`](docs/handoff/README.md).
DPF / offline CLI contract: [`docs/cli-contract.md`](docs/cli-contract.md).
Business context (product, pricing, licensing): [`docs/business/README.md`](docs/business/README.md).
Architecture map: [`graphify-out/README.md`](graphify-out/README.md).
Worktrees and CodeGraph: [`docs/handoff/worktrees.md`](docs/handoff/worktrees.md).
Contract versioning (MODEL-59): a change that widens a contract field's range (nullable, new enum value, may be absent) bumps that contract's major version. See [`docs/cli-contract.md`](docs/cli-contract.md).

This file is the Codex / ChatGPT.app / Cursor / Grok Build entry. Claude Code
also reads [`CLAUDE.md`](CLAUDE.md). Do not fork serving-path facts per TUI.

## Serving path

Static-first. YAML cards in `models/` export to JSON on Cloudflare Pages
(`modelspec.dev`). The CLI fetches that export into a local snapshot and ranks
offline. **No database is on the serving path.** FalkorDB is optional local
graph exploration only.

The JSON envelope and exit codes for `modelspec snapshot` / `modelspec offline`
are the contract. Read the file; do not reconstruct it from memory.

## Worktrees

Never check out a branch in another session's tree. Create a new worktree from
`origin/main`. CodeGraph indexes **this checkout only** — initialise and refresh
it here. Instructions: [`docs/handoff/worktrees.md`](docs/handoff/worktrees.md).

## Do not start

- **MODEL-3** (Cloudflare Worker ranking) and **MODEL-6** (payment rail).
- Auto-merge of `research/*`. Daily-research PRs need a human, and today they
  cannot merge because they are opened with `GITHUB_TOKEN` so required checks
  never run. The token replacement is Jamie's.
