# How an agent does the downselect: the CLI in plain language, and its gaps

**From:** Jamie's design session, 2026-09-27. Phase 2, following the facet-board
brief ([`2026-09-27-facet-board.md`](2026-09-27-facet-board.md), MODEL-168).
**The question:** if a person can downselect well on the page, can an agent do
exactly the same through the CLI or API? Wherever it can't, that is a ticket.

## Part 1: how the CLI works, in plain language

### The pieces

Think of ModelSpec as a library with a strict librarian.

- **The cards** (`models/*.md`) are the library's books: one per model, with
  facts, and a source for every fact.
- **The decision snapshot** is a photocopy of every fact the librarian is
  allowed to use today. There is one per build, it's a single gzipped JSON
  file, and it's published at `https://modelspec.dev/api/decision/snapshot.json.gz`.
  - Its name is its fingerprint. `snap_f0a30b23be5070c7` is the first 16
    hex digits of the SHA-256 hash of its content.
  - Change one fact and you get a different name.
  - Two people holding `snap_f0a3…` hold identical facts.
- **The vocabulary** (`/api/decision/vocabulary.json`) is the index card that
  lists what you are allowed to ask about: 52 facets, 39 benchmarks, 12
  capability domains, the providers, and how many models have each fact.
- **The spec** is your question, written as a short YAML form.
- **The engine** (`decision/`) is the librarian. Given the same spec and the
  same snapshot, it always returns the same answer, byte for byte. The page,
  the API and the CLI all run this one engine.

### A worked example

A person on the page wants "a coding agent on a budget". An agent writes the
same thing as a spec (`budget.yaml`):

```yaml
spec_version: 1
snapshot: latest
task_type: new_feature
capabilities: {software_engineering: required}
task_tokens: {input: 40000, output: 4000}      # how big one task is
where:                                          # the Musts: fail one, you're out
  - model.class = text-generator
  - model.lifecycle = active
  - model.context_window >= 200000
  - offering.cost_per_task <= 0.25
optimize:                                       # the Prefers: they rank, never remove
  weights: {software_engineering: 0.6, -offering.cost_per_task: 0.4}
explain: summary
limit: 500
```

Then it runs:

```bash
modelspec decide budget.yaml --snapshot-file snapshot.json.gz --json
```

What the engine does, step by step:

1. **Filter.** Every offering is checked against each Must. There are three
   possible answers per check: yes, no, and *unknown*. A "no" removes the
   offering. An "unknown" puts it in `may_qualify` instead of dropping it.
2. **Estimate capability.** "Software engineering" is not one benchmark. It
   is an estimate learned from every benchmark tagged to that domain (12
   here), each weighted by how direct and how recent it is. The estimate
   comes with an 80% interval: a range, not a single number.
3. **Score.** Each Prefer is rescaled to 0–1 across the survivors
   (cheapest = 1 for cost, strongest = 1 for capability), multiplied by its
   weight, and summed.
4. **Explain.** The engine records every number with its formula and its
   source record. For example, cost reads `(0.75 USD per 1M × 40,000 + 3.75
   USD per 1M × 4,000) ÷ 1,000,000 = 0.045 USD per task`.

The real run against `snap_f0a30b23be5070c7` (contract 1.7):

| Rank | Model | Provider | Software engineering (80% interval) |
| --- | --- | --- | --- |
| 1, 2 | Gemini 3.7 Flash | Gemini API, Vertex | 0.10 (−0.70 to 0.89) |
| 3, 4 | Gemini 3.8 Flash | Gemini API, Vertex | −0.09 (−0.76 to 0.57) |
| 5 | GLM-5.3 | Z.ai | 0.18 (−0.62 to 0.98) |
| 6 | Qwen3.8 Max 0902 | Alibaba | 0.23 (−1.87 to 2.33) |
| 7, 8 | GPT-6 Sol | Azure, OpenAI | 0.23 (−1.87 to 2.34) |
| 9–11 | Claude Opus 5.5 | Anthropic, Bedrock, Vertex | 1.44 (0.35 to 2.54) |
| … | 24 offerings in all; 3 may qualify (Kimi K2.6, Kimi K3, Qwen3.8 Flash Next: cost unknown) | | |

How to read that answer:

- Gemini 3.7 Flash comes first because it is the cheapest, and cost carries
  40% of the score.
- Claude Opus 5.5 has the highest estimate, but its interval overlaps
  Gemini's, so the evidence can't say Opus is better for this task. Cost
  breaks the tie.
- That is exactly what the page should say as "These N fit, and the
  evidence can't separate them" (MODEL-170).

### How an agent reads the answer

- `status`: `answered`, `partial` (some offerings may qualify) or
  `no_feasible`.
- `results[]`: one entry per **offering** (model × provider), in rank order.
  Each has `estimates`, `contributions` (each weight's share of the score,
  with the formula and records), `evidence` and `warnings`.
- `may_qualify`, `eliminated` (who failed which Must), `constraint_costs`
  (what each Must cost you), `relax` / `relax_to` (what to loosen to get an
  answer), and with `explain: full`, `near_misses` and `sources`.
- `decision_id`, `spec_hash` and `snapshot` make the answer reproducible.
  Same spec + same snapshot = same answer. An agent can cache on
  `(spec_hash, snapshot)`.

### Where it runs

- **CLI, offline:** `modelspec decide` runs the engine on your machine
  against a snapshot file. There's no network after the download and no
  cost per call.
- **API:** `POST https://api.modelspec.dev/v1/decide` runs the same engine
  on the Worker. Browsers are allowed only from modelspec.dev (CORS), so an
  agent calls it from a server.
- **MCP:** `https://api.modelspec.dev/mcp` has `decide` and `vocab` beside
  `rank`, `model_info`, `list_use_cases` and `policy_check`.

## Part 2: an agent choosing a model for the next subagent

The stages are the person's stages. What changes is who supplies each input,
and how often.

| Stage | A person on the page | An agent, per ticket or subagent |
| --- | --- | --- |
| Estate | Set once: keys, plans, hardware | Set once per organisation. Plus **live state** the page never sees: how much of each plan's window is left, and which rate limit is closest |
| Musts | Clicked | Mostly standing policy (data, licence, region), plus a few per ticket (context size, tool calling) |
| Prefers | Two or three sliders | Derived from the task type. It repeats thousands of times, so it should be a saved profile, not re-derived each time |
| Answer | A tied group is fine; the person picks | Must end on **one** offering, every time, with a stated, deterministic tie-break |
| Test | Reads the Why panel | Keeps the explanation as an audit record; rarely reads it |
| Revisit | Occasionally | Every call pins a snapshot. The answer changes only when the snapshot does, and the agent should be told what changed |

Two things matter at scale that don't matter to a person.

1. **The estate is live.** Jamie's own worker pacing is this decision made
   by hand: "Codex over Claude when tokens are low", CodexBar quotas, and
   overnight pacing. ModelSpec can't see an agent's remaining allowance.
   The agent has to pass it in. The simplest honest shape is for the agent
   to state what it holds and what is exhausted right now, and let the
   engine answer "with what you have".
2. **Cost and speed per call.** An agent deciding per ticket should not pay
   a network round trip each time. The offline CLI, with a pinned snapshot
   and results cached by `spec_hash`, is the right tool. The API suits
   agents that can't hold a file.

## Part 3: the gap map

For every step of the human flow: can an agent do the same, and if not, which
ticket covers it.

| # | Human step (facet board) | Agent equivalent today | Gap | Ticket |
| --- | --- | --- | --- | --- |
| 1 | Page loads today's facts | `snapshot fetch` downloads only the rank export; no command downloads the decision snapshot | The command the page shows fails | MODEL-176 (in progress) |
| 2 | See every facet and its coverage | The CLI never reads the vocabulary | An agent can't discover valid facets, benchmarks, domains or providers | MODEL-177 |
| 3 | Pick a template | None | No shared templates; the page's templates are hard-coded in TypeScript | MODEL-178 |
| 4 | Set my estate | No spec field | Can't say "I hold these keys, plans, devices", or "this plan is exhausted now" | MODEL-179 (with MODEL-173, MODEL-174) |
| 5 | Must | `where` | Works | — |
| 6 | Prefer (and Must + Prefer on scales) | `optimize.weights` on capability, cost and speed only | Other facets can't be preferred | MODEL-172 |
| 7 | Switch off a distrusted benchmark | None | Can't exclude a benchmark from the estimate | MODEL-171 |
| 8 | The answer: tied group or single pick | Ranked offerings; `p_best` is **null** under a weighted objective | No group, no deterministic tie-break, no probability in the common case | MODEL-170 |
| 9 | Nothing qualifying is hidden | `limit` cuts offerings and marks them excluded | Same bug as the page | MODEL-169 (in progress) |
| 10 | Choose the offering | One result per offering; cost per task sits inside `contributions` | No flat `cost_per_task` on a result; the same model repeats per provider | MODEL-180 |
| 11 | Why, why not X, what each Must costs | `contributions`, `constraint_costs`, `near_misses` and `eliminated` are all there | No direct "why not X"; the agent has to search three lists | MODEL-180 |
| 12 | Read it as a person | Output is JSON only (plus `--html`) | No terminal summary for a developer at the shell | MODEL-180 |
| 13 | Leave with a link, config or summary | The spec is portable; `--html` writes a report | Works once MODEL-176 lands | — |
| 14 | Watch the answer | None | Can't ask "what changed since snapshot X for this spec" | MODEL-181 |
| 15 | Trust the facts | Hash and ID are checked; the signature is HMAC with a private key | The public can't verify the signature | MODEL-182 |
| 16 | Use from an agent platform | MCP exposes `decide` and `vocab` | Closed by MODEL-183 | MODEL-183 |

## A question for Jamie (business, not engineering)

The page is free, and the CLI is the low-cost product. But the decision
snapshot the page uses is public and current, and `modelspec decide` runs
offline against it. A free user can therefore run the CLI on today's facts at
no cost. What does the paid CLI sell: freshness, the hosted API at volume, the
estate and plan data, alerts on a watched decision, or something else? The
answer decides which of the gaps above are free features and which are paid.
Billing, keys and x402 belong to another session; this is only the question.
