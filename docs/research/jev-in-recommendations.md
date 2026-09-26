# Jev in ModelSpec decisions

**MODEL-112. Measured 2026-09-25. Research only. No production path reads these results.**

## Decision

Jev should not replace `parseRealTask`, enter `/v1/decide`, or become verification's
second key. It did not improve task-to-spec accuracy and it failed to confirm prose
claims that the existing two-key process had verified.

Keep one narrower candidate for follow-up research:

1. Explanation checking. Jev classified all 16 supported and unsupported sentences
   correctly at a 174 ms median and $0.038 per 1,000 correct checks.

Do not add a cascade to ingestion attribution. The real MODEL-99 and MODEL-102
corpus contains 627 verified rows and 383 quarantined rows. Jev made no
misattributions. The `gpt-5-mini` arm made seven, and the Jev to `gpt-5-mini`
cascade accepted six of them. The existing Jev-only path and disabled cascade remain
unchanged.

Every evaluated role obeys the boundary for this work. Jev judges evidence already
in state. It never supplies a fact. Every Choice has `no_match`. Thresholds and
arithmetic stay in code. A Jev answer cannot affect ranking, scoring, a reproducible
Decision, a Determination, or any uncited published claim.

## Where Jev could run

The decide page currently parses task text in the browser with
`parseRealTask` and sends an explicit Spec to the hosted adapter. The adapter calls
`POST /v1/decide`; the Worker parses that Spec and runs the shared `decision/` engine
against its verified Snapshot. `decision.resolve` rejects a free-text-only task in
slice 1.

Putting a TypeSafe key in the static page would expose it. Any later task-text service
would therefore run in the Worker with a server-side secret. It should return a draft
Spec for the caller to inspect and submit, not alter `/v1/decide` or its Decision. At
the measured mean, the Jev routing call cost $0.0000679 per request. This candidate is
dropped because its accuracy was worse than the local parser, not because of cost.

Ingestion attribution and explanation checks belong in offline ingestion and report
generation. They can select or refuse among supplied rows. The cited row remains the
source of every displayed fact.

## Jev contract used

TypeSafe documents Jev as a model that evaluates state against typed Choice, Score,
and Noul questions. Choice returns an option, probabilities, and confidence; Noul
returns a probability from 0 to 1. Questions in one request run independently against
the same state. The experiment used `jev-1.13.0`, not a moving alias. TypeSafe listed
the price as $0.042 per million input tokens with free output, and a 64k request
context. Source read 2026-09-25:
[Introduction](https://docs.typesafe.ai/introduction),
[models and price](https://docs.typesafe.ai/models), and
[HTTP API](https://docs.typesafe.ai/api).

The policy bands were fixed in code before the paid run:

- `act`: Choice confidence at least 0.90.
- `flag`: confidence from 0.60 through 0.8999.
- `null`: confidence below 0.60 or any selected `no_match`.

These are the existing attribution bands from `scripts/attribution.yaml`. The run did
not tune them.

## Method

### Arms

Every newly paid case sent byte-equivalent state and questions to two arms:

- Jev `jev-1.13.0` through `POST /v1/systemone`.
- `openai/gpt-5-mini`, the mid baseline from the cost-to-correct harness, through
  OpenRouter. It received the same JSON state and questions plus only a compact reply
  shape. Malformed and truncated replies counted as wrong. Prices came from
  [OpenRouter's model endpoint](https://openrouter.ai/api/v1/models), read
  2026-09-25.

`parseRealTask` was a third local arm for task routing. The harness executed the real
TypeScript function against the decide page vocabulary. It did not reimplement its
regular expressions.

The attribution comparison re-analysed the committed MODEL-99 and MODEL-102 rows.
The three arms were Jev, `openai/gpt-5-mini`, and the Jev to `openai/gpt-5-mini`
cascade. The comparison made no new attribution calls. Each arm received the same
labelled ingestion state in the original runs.

Cost-to-correct is total list-price cost divided by correct answers, multiplied by
1,000. Latency is wall-clock time on one machine with eight concurrent requests. It
is an experiment measurement, not an offering speed fact.

### Label sets

The labels were committed before inference:

- `tests/fixtures/jev_task_routing.yaml`: 60 task descriptions, three phrasings of
  each recall question. Labels cover domain, class, and exact extraction of the four
  text conditions the page currently handles: 200k context, open weights, commercial
  use, and low latency. The paid arms chose from the full domain and class registries.
- `tests/fixtures/jev_judgment_labels.yaml`: the MODEL-99 and MODEL-102 attribution
  sources, 21 second-key cases, and 16 explanation-support cases.

The attribution set uses the ingestion outcomes published for MODEL-99 and MODEL-102
on 2026-09-20. The verified cohort has 627 real creator-attribution rows. The
quarantined cohort has 383 `relisted_withheld` rows where every offered organisation
is wrong and `cannot_establish` is the only correct answer. The committed files are
`scripts/cost_to_correct_2026-09-20.jsonl.gz`,
`scripts/cascade_real_2026-09-20.jsonl.gz`, and
`scripts/cascade_guard_2026-09-20.jsonl.gz`. The original source was
[`https://models.dev/api.json`](https://models.dev/api.json), read 2026-09-20.

The second-key set uses 12 verified and 9 mismatched production claims whose latest
two-key outcome came from a prose model reader and whose retained cited region was
available. The registered sources, all read and verified on 2026-09-25, were the
[Claude Fable 5.1 system card](https://www.anthropic.com/claude-fable-5-1-system-card),
[Z.ai privacy policy](https://docs.z.ai/legal-agreement/privacy-policy.md),
[Alibaba Model Studio privacy notice](https://www.alibabacloud.com/help/en/model-studio/privacy-notice),
and [Amazon Bedrock data protection](https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html).
The filed claim and cited region were the whole state. The collector's conclusion and
the prior verifier's answer were not shown.

The explanation set pairs a generated sentence with one evidence row and its cited
region. Eight sentences stay within the row. Eight change a value, subject, effort,
harness, date, or claim more than the row establishes.

### Reproducibility

Run without spending:

```bash
PYTHONPATH=$PWD python scripts/research/eval_jev_recommendations.py --plan
python scripts/research/eval_jev_recommendations.py --analyse <run.jsonl>
```

The paid command requires both keys in environment variables, an output path, and a
positive `--max-usd` no greater than $5. Before a worker starts a call, it atomically
reserves the estimated input and the maximum 4,000 baseline output tokens. It
reconciles the reservation with actual usage after the call. Keys are never written
to a result row.

## Results

### 1. Task text to Spec: drop

Accuracy is exact against all 60 labels. "Conditions" means the whole four-condition
set, not per-condition accuracy.

| arm | domain | class | conditions | all exact | p50 | p95 | total cost | $ / 1,000 exact |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `parseRealTask` | **85.0%** | **88.3%** | 90.0% | **76.7%** | <0.1 ms | 0.1 ms | $0 | $0 |
| Jev | 60.0% | 45.0% | **96.7%** | 25.0% | 169 ms | 240 ms | $0.004076 | $0.272 |
| `gpt-5-mini` | 48.3% | 43.3% | 85.0% | 25.0% | 8,082 ms | 11,880 ms | $0.104715 | $6.981 |

Jev's confidence did not rescue the candidate. Its `act` band contained 8 cases and
4 were jointly correct. The `flag` band was 4/16 and the `null` band 7/36. The
right decision is to keep the deterministic parser and improve its vocabulary rules
with tests. Jev must not run inside `/v1/decide` or change the reproducible Decision.

The round-2 labels no longer treat "large", "long", "big", or "lengthy" as an
explicit 200,000-token minimum. Removing those six leaked labels reduced
`parseRealTask` joint accuracy from 78.3% to 76.7%. The comparison still rejects both
paid replacements by more than 50 percentage points.

### 2. Ingestion attribution: keep Jev alone and reject the cascade

| arm | all | verified rows | quarantined rows | p50 | p95 | total cost | $ / 1,000 correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Jev | 93.9% | 565/627 | **383/383** | **183 ms** | **278 ms** | **$0.031919** | **$0.034** |
| `gpt-5-mini` | **98.0%** | **614/627** | 376/383 | 5,129 ms | 9,706 ms | $1.431954 | $1.446 |
| cascade | 97.9% | 612/627 | 377/383 | 234 ms | 9,788 ms | $0.670002 | $0.678 |

Jev abstained on all 383 quarantined rows and made no misattributions. It missed 62
verified rows. The standalone LLM named seven wrong organisations in the quarantined
cohort. The cascade's reseller veto rejected one of those answers and accepted six.
Accuracy and cost do not outweigh those six false attributions. Keep the current
Jev-only ingestion path and keep the cascade disabled. This result does not authorize
Jev to verify Evidence or to turn an attribution into a Fact.

### 3. Verification's second key: drop

| arm | all | verified rows | quarantined rows | p50 | p95 | total cost | $ / 1,000 correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Jev | 28.6% | **0/12** | 6/9 | **195 ms** | **221 ms** | **$0.004134** | **$0.689** |
| `gpt-5-mini` | 33.3% | 1/12 | 6/9 | 4,655 ms | 8,977 ms | $0.043765 | $6.252 |

Jev did not confirm any of the 12 claims the existing two-key process verified. It
mostly selected `no_match`, which is safe but does no verification work. Its two
`flag` answers were both wrong, and it produced no `act` answer. Keep the current
different-family extractors in `decision/verify.py`.

### 4. Explanation support: keep for a real-sentence holdout

| arm | all | supported | unsupported | p50 | p95 | total cost | $ / 1,000 correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Jev | **100%** | **8/8** | **8/8** | **174 ms** | **203 ms** | **$0.000609** | **$0.038** |
| `gpt-5-mini` | 93.8% | 8/8 | 7/8 | 3,828 ms | 5,123 ms | $0.013677 | $0.912 |

All eight supported sentences landed in Jev's `act` band. All eight unsupported
sentences selected `no_match` and therefore `null`. This is the cleanest fit for a
model that selects rather than generates. A larger holdout must use sentences from
the real Explanation path before any production change. Failure must suppress or
regenerate the sentence; it must never rewrite the evidence or invent a replacement.

## Spend

Five paid runs were made. Three were superseded after the harness exposed a missing
registry description, an LLM reply shape that did not match the established harness,
and an output ceiling below the established 4,000-token baseline. Their labels were
not changed, and their costs remain in the total.

| charge | amount |
| --- | ---: |
| OpenRouter provider-reported cost | $0.556201 |
| Jev, actual input tokens at the posted price | $0.030024 |
| **Actual total** | **$0.586224** |
| Conservative list-price ledger | $0.656265 |
| Spend cap | $5.00 |

The provider-reported total plus Jev's token charge is the actual spend. The larger
ledger reprices OpenRouter usage from token counts and its public list price. The
MODEL-99 and MODEL-102 attribution calls predate this work, so their historical costs
appear in the attribution comparison but not in MODEL-112 spend.

## Limits

- The task set has 60 authored descriptions, not live traffic. The three phrasings per
  recall question are related observations.
- The attribution corpus measures creator attribution during ingestion. It does not
  measure numeric benchmark, variant, effort, harness, or unit matching.
- The second-key set reuses ModelSpec's recorded two-key outcomes as labels. It is not
  an independently adjudicated third-party set.
- Latency includes network and queue time from one machine and one short window.
- The baseline used the same state and questions, not a prompt tuned for text
  generation. This is the existing cost-to-correct comparison method, not the best
  possible `gpt-5-mini` system.
- The result says nothing about generation quality and must not enter a capability
  estimate or any scoring path.

## Follow-on tickets

### Research: Jev attribution for benchmark Evidence

Scope: build at least 200 independently labelled benchmark Evidence rows, balanced
across verified and quarantined outcomes, model siblings, effort, harness, unit, and
benchmark versions. Run Jev in shadow mode with the same 0.90 and 0.60 bands.

Done when: the labels are fixed before inference; every row has a source URL and read
date; the `act` band has zero false acceptances with a stated binomial upper bound;
accuracy, coverage, latency, spend, and cost-to-correct against `gpt-5-mini` are
published; no catalogue value is changed.

### Research: explanation checker on real Decisions

Scope: collect at least 200 sentences generated from real Decision rows, with a
balanced set of supported sentences and single-error mutations. Include facts,
Evidence, qualifiers, constraint costs, and near misses.

Done when: an independent reviewer labels the set before inference; Jev has zero
unsupported `act` results; supported coverage, latency, spend, and cost-to-correct are
published; a failure only suppresses the sentence.

### Decide: extend and test `parseRealTask`

Scope: use the 60 routing labels as regression tests, then add a separate held-out set
for classes and conditions the parser misses, including transcriber, orderer, numeric
price caps, device fit, and retrieval generation versus vectorisation.

Done when: the original 60 remain at least 76.7% joint exact; the untouched holdout is
at least 90% for domain, class, and condition-set accuracy separately; parsing stays
local, deterministic, and below 1 ms p95; `/v1/decide` remains unchanged.
