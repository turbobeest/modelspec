# Cost-to-correct: creator attribution, measured across model classes

**MODEL-99. Measured 2026-09-20. This is a measurement, not a product feature:
nothing user-facing reads it, and it is not folded into `rank_score`.**

Benchmarks score *generated answers*, so a decision model has no MMLU or
SWE-bench number and never will. Against the ranking floors
(`MIN_BENCHMARK_COUNT = 2`, `MIN_BENCHMARK_COVERAGE = 0.50`) such a model is
unrankable by construction. One metric does span the classes, because it
measures the job rather than the mechanism:

> For this defined task, what is the accuracy, the latency, and the cost per
> correct answer?

This is the first run of that measurement. Three arms, one decision model and
two LLMs, answered the **same 627 questions from byte-identical inputs**.

## The result

627 cases, 1,881 paid calls, $1.428 spent. Prices read 2026-09-20 (below).

| arm | model | n | accuracy | p50 latency | p95 latency | total cost | **cost / 1,000 correct** |
| --- | --- | --: | --: | --: | --: | --: | --: |
| decision model | `jev-1.13.0` | 627 | 90.1% | **180 ms** | 243 ms | $0.0203 | **$0.036** |
| LLM, cheap | `openai/gpt-5-nano` | 627 | 77.3% | 12,128 ms | 21,616 ms | $0.5189 | $1.070 (29.8×) |
| LLM, mid | `openai/gpt-5-mini` | 627 | **97.9%** | 5,253 ms | 9,725 ms | $0.8886 | $1.447 (40.3×) |

Three things in that table are worth more than the headline:

1. **The most accurate arm is not the one we pay for.** `gpt-5-mini` answered
   97.9% correctly against Jev's 90.1%, and was uniquely right on 47 cases
   where both other arms failed. Jev was uniquely wrong on 3. A cost-to-correct
   axis that only ever flattered the supplier would not be worth publishing;
   this one does not.
2. **Cheaper is not cheaper.** `gpt-5-nano` costs a fifth of `gpt-5-mini` per
   token and was *both* less accurate (77.3%) and slower (p50 12.1 s against
   5.3 s), because it spent a mean of 1,993 output tokens per answer against
   mini's 633 — and hit the 4,000-token ceiling 20 times, each of which is
   scored as a wrong answer. Per correct answer the cheap model is only 26%
   cheaper than the mid one, for 20 points of accuracy.
3. **Nobody misattributed anything.** Across 1,881 answers, **zero** named the
   wrong organisation. Every single error, in every arm, was an abstention
   (`cannot_establish`) on a case where an organisation was in fact
   establishable. For a field published as fact, that is the failure mode you
   want, and it is the same failure mode in all three classes.

### The subset production actually pays for

560 of the 627 cases are settled by `decide_deterministically()` before any
model is asked; in production no model is called for them. The 67 **ambiguous**
cases are the ones that cost money in the real pipeline:

| arm | deterministic (n=560) | ambiguous (n=67) |
| --- | --: | --: |
| `jev-1.13.0` | 91.6% | 77.6% |
| `openai/gpt-5-nano` | 80.2% | 53.7% |
| `openai/gpt-5-mini` | 97.9% | 98.5% |

The gap widens where it matters. On the cases the deterministic rules cannot
settle, the mid LLM is 21 points better than the decision model, and the cheap
LLM is barely better than a coin toss.

## The task

Creator attribution (MODEL-82): given a models.dev listing, the model's name
and family, and the same model's ids on other platforms, **which organisation
trained and released it** — or `cannot_establish`? A listing is evidence of
availability, not of authorship: Alibaba's page lists Moonshot's Kimi K3, which
is how PR #92 proposed `models/qwen/kimi-k3.md`.

Ground truth is `scripts/eval_attribution.py`'s `real` variant: cards whose
creator is established by something *other* than a models.dev page — written or
curated by a person, seeded from a Hugging Face namespace that maps to the
provider, or seeded from models.dev and independently corroborated by a product
name or an id prefix elsewhere. Cards the corpus sweep flags are excluded, and
so is any card where the deterministic rules disagree with the card.

Today's corpus: 1,064 established cards, 383 matched to a bare-id listing, 627
`real` cases (2 listings per card, seed 82). Of those, 612 offer a single
candidate organisation plus `cannot_establish`, and 15 offer two.

## Method

- **The case set is built once**, and every arm is handed the *same* state and
  the *same* questions. Each row carries `request_sha256` over
  `{state, questions}`; the run's summary records `identical_inputs: true`, and
  a sceptic can recompute those hashes from the published rows.
- **The LLM arms get Jev's own state and Jev's own questions, verbatim**, as
  JSON — the same candidate list, the same instructions, the same
  "`listing.platform` is where the model is offered, not who made it" warning.
  The only addition is one sentence naming the reply format, because an LLM has
  no typed answer channel. That is an adapter, not a better prompt. No
  few-shot examples, no tuning, no self-consistency, no tools.
- **A malformed answer is a wrong answer.** Truncated, unparseable, refused or
  out-of-vocabulary replies are recorded with their failure kind and counted as
  errors. Dropping them would flatter the arm that produces them.
- **Latency is wall-clock**, from one machine, at 4 concurrent requests per
  arm, over one ~50-minute window (14:55–15:45 UTC, 2026-09-20).
- **A hard spend cap** (`--max-usd`) aborts before it is exceeded, in code
  rather than in prose. This run was capped at $2.00 and spent $1.428; a
  20-case smoke run beforehand cost $0.035.

## Prices, and the date they were read

| arm | input $/Mtok | output $/Mtok | source | read (UTC) |
| --- | --: | --: | --- | --- |
| `jev-1.13.0` | 0.042 | — (not billed) | <https://docs.typesafe.ai/models> | 2026-09-20 14:55 |
| `openai/gpt-5-nano` | 0.05 | 0.40 | <https://openrouter.ai/api/v1/models> | 2026-09-20 14:55 |
| `openai/gpt-5-mini` | 0.25 | 2.00 | <https://openrouter.ai/api/v1/models> | 2026-09-20 14:55 |

The harness reads the LLM prices from the endpoint at run time, so the date read
is the run's own. For both LLM arms the cost computed from those list prices
matched OpenRouter's own reported cost for the run to the cent
(`provider_reported_cost_usd` in the summary).

Token totals: Jev 482,913 in / 34,288 out (output is not billed); each LLM arm
380,668 in, with 1,249,573 out for nano and 396,701 for mini. Jev's own
tokeniser counts the same evidence at ~770 tokens where OpenAI's counts ~607.

## Where each arm was wrong

| failure kind | `jev-1.13.0` | `gpt-5-nano` | `gpt-5-mini` |
| --- | --: | --: | --: |
| correct | 565 | 485 | 614 |
| abstained when the answer was establishable | 62 | 120 | 12 |
| truncated at the output ceiling | 0 | 20 | 0 |
| unparseable JSON / no `choice` field | 0 | 2 | 1 |
| **named the wrong organisation** | **0** | **0** | **0** |

Every error clusters in one place. All 217 wrong answers were on
single-candidate cases, and 98 of them were listings on the creator's **own**
page — `cohere/c4ai-aya-expanse-8b`, `llama/llama-3.3-8b-instruct`,
`xai/grok-imagine-video`, `upstage/solar-mini`. There the instructions
explicitly forbid treating the platform as evidence of authorship, the id
carries no `org/` prefix, and the model is listed nowhere else, so the only
route to the right answer is recognising the product name. Abstention is the
conservative reading of the question; it is also, for these cards, wrong.

> **MODEL-102 followed this up and it does not mean what it looks like.** Every
> own-page case in this run is settled by `decide_deterministically()` before
> any model is asked, and **none** of the 67 ambiguous cases is one. These
> errors are an artefact of this harness asking every arm every case; they were
> never costing the catalogue a creator. Amending the question does recover
> them (+22.6 points for Jev on that subset), and is recommended *against*
> anyway. See [`cascade-attribution.md`](cascade-attribution.md).

12 cases defeated all three arms, and they are all of that shape. Jev's three
unique misses are the same:
`cohere/command-a-vision-07-2025`, `mistral/ministral-3b-latest`,
`mistral/open-mistral-nemo`.

By how ground truth was established — `jev` / `nano` / `mini`:
curated 95% / 84% / 97%; Hugging Face namespace 99% / 86% / 100%;
corroborated 88% / 75% / 98%.

## What this does **not** show

- **It is one task.** Creator attribution over pre-gathered evidence is a
  narrow, structured judgment. Nothing here generalises to summarisation, code,
  reasoning, or any task with a long output. A cross-class axis needs many
  tasks; this is the first.
- **It is not a statement about LLMs' knowledge of who made which model.** The
  arms are told to judge *only from the state* and not to use outside
  knowledge, because that is what production needs — an LLM drawing on its
  training data would answer differently, sometimes better, with a failure mode
  (confident hallucinated attribution) that this harness would not detect as an
  abstention. That would be a different experiment.
- **It is not a tuned comparison.** One prompt, default sampling, no few-shot,
  no retries-on-disagreement. A prompt written for `gpt-5-nano` would very
  likely raise its 77.3% and cut its 1,993 output tokens. The measurement is of
  the arms *as asked in the same way*, which is the only way to keep it honest,
  not of the best each could do.
- **Latency is not a product SLA, and not a benchmark.** One machine, one
  network, one location, one hour, 4 concurrent requests, no warm-up,
  provider-side queueing included. These numbers are not card evidence and do
  not enter the benchmark eligibility contract — they would not meet the bar
  in [`../agentic-latency-benchmark.md`](../agentic-latency-benchmark.md).
  They exist only to price a correct answer in time as well as in money.
- **The ground truth is the catalogue's own rule**, not an independent gold
  set. It deliberately excludes anything resting on a models.dev page alone or
  on a model's judgment, but it was built by this project, and a reviewer who
  disputes a card disputes a row.
- **Prices move.** List prices on 2026-09-20, no batch or committed-use
  discount, OpenRouter's routing to an underlying provider included. Cost per
  1,000 correct conflates price and accuracy on purpose; at n=627 a handful of
  flipped answers moves it.
- **It does not change any ranking.** This is evidence of fitness for a task.
  It is not a benchmark score, it must not be silently folded into
  `rank_score`, and it does not lift a model over the ranking floors.
- **The corpus is today's.** 627 cases from the models.dev snapshot of
  2026-09-20 (`sha256 0fdbc1ed…dacf`), not the 802 of the 2026-09-17 archive.
  The archived Jev-only run measured 91.9%; this one measures 90.1% on a
  different, larger corpus with the same method. Numbers from the two runs are
  not the same numbers.

## Re-running it

```bash
curl -fsSL https://models.dev/api.json -o api.json   # sha256 0fdbc1ed…dacf on 2026-09-20

# 20 cases, ~$0.04, to check the shape
TYPESAFE_API_KEY=… TEXT_MODEL_API_KEY=… TEXT_MODEL_BASE_URL=https://openrouter.ai/api/v1 \
python scripts/eval_cost_to_correct.py --api-json api.json \
  --out smoke.jsonl --limit 20 --max-usd 0.25

# the full run, ~50 minutes, $1.43 at the prices above
python scripts/eval_cost_to_correct.py --api-json api.json \
  --out scripts/cost_to_correct_$(date +%F).jsonl.gz --max-usd 2.00 --max-tokens 4000

# the table again, from the stored rows: no key, no call, no money
python scripts/eval_cost_to_correct.py --analyse scripts/cost_to_correct_2026-09-20.jsonl.gz
```

Keys are read from the environment, or from a file outside this repository via
`--env-file`. They are never printed, logged or committed. `--plan-only` counts
the cases and calls nothing.

Every paid answer is in `scripts/cost_to_correct_2026-09-20.jsonl.gz`: one row
per arm per case, with the chosen answer, the expected answer, correctness, the
failure kind, wall latency, both token counts, the cost, and the
`request_sha256` proving the arms were asked the same thing. The last line is
the run summary.

**Tolerance on a re-run.** The case set is deterministic for a given api.json
and seed; the models are not. The LLM arms run at default sampling, models.dev
changes daily, and provider latency varies by hour. Expect accuracy within a
couple of points, cost within ~10% at the same list prices, and latency to
differ by more than that. If a re-run contradicts the direction of any finding
above — particularly "zero misattributions" — that is a result worth reporting
against this page.

## Disclosure

ModelSpec is a paying TypeSafe customer and the attribution pipeline depends on
Jev (MODEL-101). This page was produced by the party with the conflict, so the
only defence is that the harness, the case construction, the raw rows, the
prices, the failures and the re-run command are all here, and the result is not
the flattering one: the mid-tier LLM was the most accurate arm, by 8 points
overall and 21 on the subset that matters. What the decision model wins is
price and speed — 40× cheaper per correct answer and 29× faster at the median —
and that is a trade, stated as a trade, not a verdict.

`neutrality_commitment()` in `api/ranking/engine.py` is the standard: a result
that flatters a supplier and cannot be reproduced by a stranger is worth
nothing. Contradiction is invited; the data to contradict it is in this
directory.
