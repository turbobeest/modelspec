# AEO engineering: answer engines and agents

AEO (answer engine optimisation) is the work that lets two kinds of reader find ModelSpec:

* answer engines (ChatGPT, Claude, Perplexity, Google AI Overviews), so they can quote and cite ModelSpec correctly;
* agents, so they can find the hosted API and MCP server and decide to call them.

This folder holds only the engineering contracts: what the site emits, and what CI checks. Positioning, prompt lists, measurement results and budgets are private and live outside this repository.

| Document | What it fixes | Ticket |
|---|---|---|
| [`crawler-policy.md`](crawler-policy.md) | Which crawlers may fetch what, and the one place `robots.txt` is written | MODEL-253 |
| [`json-ld.md`](json-ld.md) | How structured data is generated, and the rules it must keep | MODEL-252 |
| [`prompt-inventory.md`](prompt-inventory.md) | The schema for the prompts we measure, and for one measured run | MODEL-254, MODEL-256 |
| [`surface-lint.md`](surface-lint.md) | The check that fails CI when a public surface drifts from the entity registry | MODEL-255 |

## Rules every surface keeps

1. **One sentence, everywhere.** The canonical description of ModelSpec is generated from one entity registry (MODEL-252), never typed into a page:

   > ModelSpec is an analysis of alternatives for AI models: it decides which models fit a job from your requirements, sourced benchmarks and real cost, and shows its work.

2. **No fresh data on a keyless page.** Answer engines can quote the method and worked examples computed from the frozen public image. Each example is dated and labelled as a delayed image. Current answers come only from the decision board (people) and the keyed API and MCP server (machines).
3. **Claims must be true over HTTP.** A page doesn't claim a capability the service doesn't have today. In particular, nothing claims x402 payment while `X402_ENABLED` is false.
4. **Neutrality.** No wording reads as paid placement, sponsorship or affiliate ranking. `docs/legal/` and `neutrality_commitment()` change only with Jamie's approval (`tests/test_legal.py`).
5. **Categories, not competitors.** A comparison describes kinds of tool (an analysis of alternatives, a model router, a hard-coded model). It never names another product.
6. **Not OpenAI's Model Spec.** Any page that could be confused with OpenAI's Model Spec, CNCF ModelPack or the PyPI `modelspec` package says so in its first paragraph.

## What engines can read

| Surface | Crawlable | Notes |
|---|---|---|
| `/`, `/method/`, `/pricing/`, `/legal/*` | yes | Server-rendered HTML |
| `/decide/` | capsule only | The board is a JavaScript app behind a human gate. MODEL-253 adds a server-rendered capsule (what the board does, with no model data). |
| `llms.txt`, `.well-known/mcp.json`, `auth.md`, `openapi.yaml` | yes | Agent discovery files |
| `/api/rank/profiles.json`, `/api/rank/class-fit.json` | yes | Ranking policy, no per-model data |
| `/graph/`, `llms-full.txt` | being removed | MODEL-251 |
| `/api/models/**` and other bulk JSON | being removed | MODEL-247 |
