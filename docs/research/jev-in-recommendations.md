# Jev in ModelSpec decisions

**MODEL-112. Measured 2026-09-25. Research only. No production path reads these results.**

## Decision

Jev should not replace `parseRealTask`, enter `/v1/decide`, or become verification's
second key. It did not improve task-to-spec accuracy and it failed to confirm prose
claims that the existing two-key process had verified.

Keep two narrower candidates for follow-up research:

1. Evidence attribution in shadow mode. At the `act` threshold, Jev made 4 decisions
   and all 4 were correct. The set is too small to authorize a write to the catalogue.
2. Explanation checking. Jev classified all 16 supported and unsupported sentences
   correctly at a 174 ms median and $0.038 per 1,000 correct checks.

Both roles obey the boundary for this work: Jev judges evidence already in state. It
never supplies a fact. Every Choice has `no_match`. Thresholds and arithmetic stay in
code. A Jev answer cannot affect ranking, scoring, a reproducible Decision, a
Determination, or any uncited published claim.

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

Evidence attribution and explanation checks belong in offline ingestion and report
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

Every paid case sent byte-equivalent state and questions to two arms:

- Jev `jev-1.13.0` through `POST /v1/systemone`.
- `openai/gpt-5-mini`, the mid baseline from the cost-to-correct harness, through
  OpenRouter. It received the same JSON state and questions plus only a compact reply
  shape. Malformed and truncated replies counted as wrong. Prices came from
  [OpenRouter's model endpoint](https://openrouter.ai/api/v1/models), read
  2026-09-25.

`parseRealTask` was a third, local arm for task routing. The harness executed the real
TypeScript function against the decide page vocabulary. It did not reimplement its
regular expressions.

Cost-to-correct is total list-price cost divided by correct answers, multiplied by
1,000. Latency is wall-clock time on one machine with eight concurrent requests. It
is an experiment measurement, not an offering speed fact.

### Label sets

The labels were committed before inference:

- `tests/fixtures/jev_task_routing.yaml`: 60 task descriptions, three phrasings of
  each recall question. Labels cover domain, class, and exact extraction of the four
  text conditions the page currently handles: 200k context, open weights, commercial
  use, and low latency. The paid arms chose from the full domain and class registries.
- `tests/fixtures/jev_judgment_labels.yaml`: 16 exact evidence-attribution cases,
  21 second-key cases, and 16 explanation-support cases.

The attribution set uses the MODEL-140 seeded leaderboard fixture. Seven rows belong
to the exact model variant, benchmark version, effort, harness, and unit. Nine rows
contain a copied sibling value, wrong effort, wrong harness, wrong unit, absent model,
or wrong version and are labelled `no_match`. This is the same distinction that sends
a value to verification or Quarantine.

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
positive `--max-usd` no greater than $5. It reserves the maximum 4,000 baseline output
tokens before each call. Keys are never written to a result row.

## Results

### 1. Task text to Spec: drop

Accuracy is exact against all 60 labels. "Conditions" means the whole four-condition
set, not per-condition accuracy.

| arm | domain | class | conditions | all exact | p50 | p95 | total cost | $ / 1,000 exact |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `parseRealTask` | **85.0%** | **88.3%** | **93.3%** | **78.3%** | <0.1 ms | 0.1 ms | $0 | $0 |
| Jev | 60.0% | 46.7% | 86.7% | 21.7% | 172 ms | 226 ms | $0.004076 | $0.314 |
| `gpt-5-mini` | 50.0% | 50.0% | 83.3% | 26.7% | 8,621 ms | 14,536 ms | $0.110292 | $6.893 |

Jev's confidence did not rescue the candidate. Its `act` band contained 9 cases and
only 1 was jointly correct. The `flag` band was 4/15 and the `null` band 8/36. The
right decision is to keep the deterministic parser and improve its vocabulary rules
with tests. Jev must not run inside `/v1/decide` or change the reproducible Decision.

### 2. Evidence attribution: keep for a larger shadow run

| arm | all | verified rows | quarantined rows | p50 | p95 | total cost | $ / 1,000 correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Jev | **87.5%** | **6/7** | 8/9 | **156 ms** | **220 ms** | **$0.000584** | **$0.042** |
| `gpt-5-mini` | 81.3% | 4/7 | **9/9** | 4,258 ms | 6,992 ms | $0.015790 | $1.215 |

Jev's `act` band was 4/4 and its single `flag` was correct. The two errors stayed in
the `null` band: one conservative refusal of a rounded supported value, and one low
confidence acceptance of a wrong unit. No wrong row would have passed the `act`
threshold in this set.

Keep means a larger shadow measurement, not permission to publish. The set is a small
seeded fixture, not live ingestion. Any future integration must retain deterministic
identity checks, source URL and read date, and the two-key rule. Jev may nominate a
row for verification. It may not turn the row into verified Evidence.

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

Four paid runs were made. Three were superseded after the harness exposed a missing
registry description, an LLM reply shape that did not match the established harness,
and an output ceiling below the established 4,000-token baseline. Their labels were
not changed, and their costs remain in the total.

| charge | amount |
| --- | ---: |
| OpenRouter provider-reported cost | $0.463466 |
| Jev, actual input tokens at the posted price | $0.025948 |
| **Actual total** | **$0.489413** |
| Conservative list-price ledger | $0.547474 |
| Spend cap | $5.00 |

The provider-reported total plus Jev's token charge is the actual spend. The larger
ledger reprices OpenRouter usage from token counts and its public list price. Both are
reported so the accounting does not hide the discarded runs.

## Limits

- The task set has 60 authored descriptions, not live traffic. The three phrasings per
  recall question are related observations.
- The attribution and explanation sets are deliberately small and use a test fixture.
  Four correct `act` attributions do not establish a low production error rate.
- The second-key set reuses ModelSpec's recorded two-key outcomes as labels. It is not
  an independently adjudicated third-party set.
- Latency includes network and queue time from one machine and one short window.
- The baseline used the same state and questions, not a prompt tuned for text
  generation. This is the existing cost-to-correct comparison method, not the best
  possible `gpt-5-mini` system.
- The result says nothing about generation quality and must not enter a capability
  estimate or any scoring path.

## Follow-on tickets

### Research: Jev attribution on live ingestion rows

Scope: build at least 200 independently labelled rows, balanced across verified and
quarantined Evidence, model siblings, effort, harness, unit, and benchmark versions.
Run Jev in shadow mode with the same 0.90/0.60 bands.

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

Done when: the original 60 remain at least 78.3% joint exact; the untouched holdout is
at least 90% for domain, class, and condition-set accuracy separately; parsing stays
local, deterministic, and below 1 ms p95; `/v1/decide` remains unchanged.
