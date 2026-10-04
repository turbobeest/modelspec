# AGENTS.md — ModelSpec

The single agent entry for every tool (Claude Code imports it from `CLAUDE.md`).
Open work and its state live in Linear (`MODEL-*`), not in this repository.

## What it is

ModelSpec is an analysis of alternatives for AI models: it decides which models
fit a job from your requirements, sourced benchmarks and real cost, and shows
its work. (Source: `pipeline/entity.py`.)

## Architecture

- Sites: `pipeline/build.py` renders `modelspec.dev` on Cloudflare Pages from the frozen public data image in this repository, never from private data. With `DATA_SPLIT_ENABLED` on, `/api` keeps only `build.json`, `rank/profiles.json`, `rank/class-fit.json` and the feedback schema. No database on that path.
- Fresh curated data lives in the private `turbobeest/modelspec-data`. While `DATA_SPLIT_ENABLED` is on, main deploys of the Worker embed exports built from it (`api/worker/vendor.py --data-dir`).
- The Python Worker on `api.modelspec.dev` (`api/worker/`) serves `/v1/decide`, `/v1/compare`, `/v1/rank`, `/v1/policy-check`, `/v1/feedback`, `/v1/vocabulary`, `/v1/health`, billing and credits, and the visit gate that admits site visitors. Its state: Workers KV (private policy determinations, API-key records) and Durable Objects (credit ledger, human gate).
- Machines come in through the keyed CLI (`cli/modelspec`, `modelspec-dev` on PyPI; a thin client with no data download) and the remote MCP, a separate TypeScript Worker at `api.modelspec.dev/mcp` (`mcp/`).
- Cards and benchmark pages are DATA, not checked facts.

## Binding rules

- Ranking floors in `api/ranking/engine.py` change only with Jamie.
- `neutrality_commitment()` in `api/ranking/engine.py` and `docs/legal/` are published terms, held together by `tests/test_legal.py`. Legal text changes need Jamie.
- No number orders one class above another, and cost-to-correct never reaches `rank_score` (MODEL-100, `tests/test_class_fit.py`).
- Widening a contract field's range (nullable, new enum value, may be absent) bumps that contract's major (MODEL-59). Read the contract file; never reconstruct it from memory.
- Data freeze: fresh data goes to `modelspec-data`; the required "Data freeze" check fails a PR that changes frozen data here.
- Only human lookup on the site is free. Machine access is keyed; treat any keyless machine path as a defect.
- Agent, UX and judge testing runs on subscription CLIs (`qa/`). Any vendor API spend, including the manual speed probe, needs Jamie's yes for that run.
- Production switches are Jamie's, as Worker vars (`api/worker/wrangler.jsonc`) or repo variables: `ACCESS_ENFORCED`, `BILLING_ENABLED`, `X402_ENABLED`, `X402_MAINNET`, `FEEDBACK_ENABLED`, `HUMAN_GATE_ENABLED`, `VISIT_GATE_ENABLED`, `SIGNALS_ENABLED`, `SITE_MODE`, `DATA_SPLIT_ENABLED`, and live Stripe keys. No `FEEDBACK` KV namespace is bound until he adopts `docs/design/feedback-privacy.md`.
- The sites stay on Cloudflare Pages (MODEL-3, Jamie).
- Open PRs as draft until reviewed: `automerge.yml` queues every green non-draft PR from this repository, except PRs that touch workflows and the `data-lag/image` branch, which a human merges.
- The feedback digest runs on the operator's machine, never in CI (repo and logs are public).
- Put limits in code, not prompts. Verify by running, not by reading a ticket. Check exit codes directly, not through a pipe.

## Commands

Work in your own worktree, never another session's checkout:

```bash
git -C /Users/terbeest/dev/modelspec worktree add -b <branch> \
  /Users/terbeest/dev/worktrees/<name> origin/main
```

Tests (what "Run pytest" runs; drop `-n auto --dist loadfile` for serial; any Python 3.11+ env with the repo installed works):

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n auto --dist loadfile
```

Sites (the core of "Build both sites", which also runs the decide browser and corpus suites):

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
(cd web && npm ci && npm run build && npm test)
```

Required checks on `main`: **Run pytest**, **Build both sites**, **Check
evidence against release charts**, **Data freeze**.

## Pointers

- Contracts: [`docs/decision-contract.md`](docs/decision-contract.md), [`docs/cli-contract.md`](docs/cli-contract.md), [`docs/api.md`](docs/api.md), [`docs/rank-api.md`](docs/rank-api.md), [`docs/policy-check-api.md`](docs/policy-check-api.md).
- Legal: [`docs/legal/`](docs/legal/). Billing and access: [`docs/billing.md`](docs/billing.md), [`docs/api-access.md`](docs/api-access.md).
- Data split: [`docs/design/data-split.md`](docs/design/data-split.md). Design (class selection, decision engine, feedback privacy): [`docs/design/`](docs/design/).
- Before writing a card, benchmark page or evidence: [`docs/handoff/README.md`](docs/handoff/README.md) (standing rules, pytest shards).
- QA harness: [`qa/README.md`](qa/README.md).
- Worktrees and CodeGraph: [`docs/handoff/worktrees.md`](docs/handoff/worktrees.md). Architecture map: [`docs/handoff/architecture-map.md`](docs/handoff/architecture-map.md).
- Orchestration playbook, operator machine only: `~/.config/ai-budget/ORCHESTRATION-PLAYBOOK.md`.
- History, not policy: [`docs/history/`](docs/history/).
