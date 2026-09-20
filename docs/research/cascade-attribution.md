# The own-page question, and the Jev→LLM cascade

**MODEL-102. Measured 2026-09-20, on the same corpus and the same case set as
[`cost-to-correct-attribution.md`](cost-to-correct-attribution.md) (MODEL-99).
Nothing here is user-facing, nothing here enters `rank_score`, and the cascade
ships disabled.**

MODEL-99 measured three arms on 627 identical creator-attribution questions and
found the decision model cheap and fast but abstaining, and a mid-tier LLM
accurate and slow. It left two follow-ups, and this page answers them in order,
because the first could have made the second unnecessary.

| | |
| --- | --- |
| Step 1 | The 98 errors on listings sitting on the creator's **own page** looked like prompt design. Are they? |
| Step 2 | Run Jev first and escalate **only its abstentions** to the LLM. Does it pay, and is it safe? |

The short version, and neither half is the answer that was expected:

- **Step 1's fix works and is worth nothing.** The amended question recovers
  22.6 points on the affected cases. Every one of those cases is already
  settled in code before a model is asked, and none of the cases production
  actually pays for is of that shape. Recommended against.
- **Step 2's cascade is accurate, cheap — and misattributed six models.** On
  the adversarial variant built for MODEL-82 it named a wrong organisation six
  times where Jev abstained 383 times out of 383. That is the acceptance
  criterion MODEL-102 set for itself, so the cascade does not ship, and no
  tuning was attempted.

Both are committed, both are off, and both are re-runnable.

---

## Step 1 — the own-page question

### What the question says now

`build_questions()` in `scripts/attribution.py` tells the judgment, under
`not_evidence`:

> `listing.platform` is where the model is offered. Platforms serve and resell
> models made by others, so being listed there does not make that platform's
> organisation the creator.

That is the MODEL-82 rule and it is correct. What it never says is whether the
platform's organisation is *eligible to be chosen at all* when the model's own
id or name identifies it. Read strictly — and a decision model reads strictly —
"being listed there does not make that platform's organisation the creator"
can be taken as "never pick the platform's organisation", which suppresses
`c4ai-aya-expanse-8b` on Cohere's page as surely as it suppresses Kimi K3 on
Alibaba's. The rule is not wrong. It is silent in a place where silence costs
answers.

### The narrowest change

One clause appended to `not_evidence`, adding no evidence and removing no
prohibition — it grants eligibility and immediately re-states the ban:

> An organisation that runs a platform may also be the creator of a model
> listed there. It may be chosen when `listing.listed_id`,
> `listing.model_name` or `listing.model_family` identifies it on its own —
> because the id or the name identifies it, never because of where it is
> listed.

It lives in `scripts/eval_cost_to_correct.py` as `OWN_PAGE_CLAUSE`, reachable
with `--question-variant own-page-eligible`. It is **not** in the shipped
question, for the reason below.

### Measured

164 of the 627 cases are listings on the creator's own page
(`--own-page-only`). Same cases, same state, same bytes, only the clause added:

| `jev-1.13.0`, own-page cases (n=164) | accuracy | recovered | newly wrong | misattributions |
| --- | --: | --: | --: | --: |
| production question | 71.3% | — | — | **0** |
| `own-page-eligible` | **93.9%** | 37 | **0** | **0** |

+22.6 points, 37 abstentions turned into right answers, nothing broken, nobody
misattributed. It is exactly the free accuracy it looked like.

### And it is worth nothing

**All 164 own-page cases are settled by `decide_deterministically()` before any
model is asked.** Not most of them — all of them. The tier that catches them is

```python
if not ev.prefix_orgs and ev.vendor and ev.named_orgs == {ev.vendor} ...
    # "listing page and product name agree"
```

which is the same reasoning the amended clause asks a model to perform, already
done in code, for nothing, on every one of them.

Of the **67 ambiguous cases** — the only ones production pays a model for —
**zero** are own-page listings. The number is not small; it is zero.

So the 98 own-page errors in MODEL-99's table are an artefact of the *harness*,
which asks every arm every case, including the 560 production never sends to a
model. They were never costing the catalogue a creator. Fixing the question
moves a number in a comparison harness and changes nothing that ships.

### Recommendation: do not ship the clause

Not because it fails. Because it buys nothing and it spends the one thing this
module cannot afford to spend. The sentence it weakens — the platform is not
evidence of authorship — is the whole of MODEL-82, and the `relisted*` and
`withheld` variants exist to catch exactly the failure that loosening it
invites. Paying any risk against that fence for a measured production gain of
**zero cases** is a bad trade at any exchange rate.

The clause, the flag and the numbers stay in the repository so that the day an
own-page listing *is* ambiguous — a new provider page, a model with no
recognisable product name — the work is measured and waiting, not re-argued.

---

## Step 2 — the cascade

### The design

Jev answers, exactly as now. Only an **abstention** (`cannot_establish`) is
asked again, of an LLM, with byte-identical state and byte-identical questions.
The LLM's answer is taken only when it names one of the same candidates code
extracted; otherwise Jev's abstention stands.

Four things make that narrow on purpose:

1. **Only abstentions escalate.** A judgment the policy *refused* — below the
   review band, or the reseller veto — is a decision, not a shrug, and is never
   shopped to a second model. (`test_only_an_abstention_is_escalated_never_a_refusal`)
2. **The veto gets stricter, not looser.** The platform's own organisation is
   refused if *either* model calls that platform a reseller. Two graders,
   either one of whom can stop it.
3. **An LLM's confidence is never banded.** The bands in
   `scripts/attribution.yaml` were calibrated against Jev's own probabilities
   and mean nothing for a chat completion. An escalated answer earns its place
   by naming a candidate, not by claiming a number — and it is written with
   status `escalated`, which puts it in front of a human in the PR body rather
   than onto a card silently.
4. **Provenance on every judgment.** Every `Attribution` and every ledger row
   carries an `arm`: `rule`, `jev`, `llm` or `none`.
   (`test_every_judgment_records_which_arm_produced_it`)

**The flag ships off.** `escalation.enabled: false`. A per-run
`max_escalations_per_run` caps the spend the way the Firecrawl credit cap does;
exhausting it leaves the remaining abstentions as abstentions and the run
completes normally. A failed escalation call does the same.

### The fourth row

The same 627 `real` cases as MODEL-99, byte-identical requests (all 627
`request_sha256` match the published run). The first three rows are that run's;
the fourth is this one's.

| arm | model | n | accuracy | p50 | p95 | total $ | **$ / 1,000 correct** | misattributions |
| --- | --- | --: | --: | --: | --: | --: | --: | --: |
| decision model | `jev-1.13.0` | 627 | 90.1% | **180 ms** | 243 ms | $0.0203 | **$0.036** | 0 |
| LLM, cheap | `openai/gpt-5-nano` | 627 | 77.3% | 12,128 ms | 21,616 ms | $0.5189 | $1.070 | 0 |
| LLM, mid | `openai/gpt-5-mini` | 627 | **97.9%** | 5,253 ms | 9,725 ms | $0.8886 | $1.447 | 0 |
| **cascade** | `jev-1.13.0` → `openai/gpt-5-mini` | 627 | 97.6% | **184 ms** | 9,190 ms | $0.1150 | **$0.188** | 0 |

It does what MODEL-102 predicted, and the numbers are good:

- **60 of 627 cases escalated** (9.6%); 45 of those escalations produced an
  answer that was taken.
- **Accuracy 97.6%** — within 0.3 points of the mid LLM, 7.5 points above Jev.
- **$0.188 per 1,000 correct** — **7.7× cheaper** than asking the LLM
  everything, and the p50 is still Jev's 184 ms, because nine answers in ten
  never leave the decision model. The p95 is the escalation showing up.
- **Zero misattributions** on this set.

On the evidence production actually sees, the cascade is the right answer and
the cost is pennies. That is not the whole evidence.

### The guard — and the result that stops it

MODEL-99's headline was that **no arm misattributed anything**: all 1,881
answers were either right or an abstention. That is the property the catalogue
is built on, and a cascade exists precisely to convert abstentions into
answers. So the cascade has to be measured where abstention is the *only*
correct answer, or it has not been measured at all.

`relisted_withheld` is that shape, and it is the PR #92 failure built on
purpose: the model is moved, bare, onto another organisation's page, and the
true creator is removed from the options and from every cross-listed id. Every
remaining option is wrong. 383 cases, production's own question:

| | |
| --- | --: |
| Jev abstained | **383 / 383** (100%) |
| escalated to `openai/gpt-5-mini` | 383 |
| the LLM also abstained | 376 |
| the LLM named an organisation | 7 |
| refused by the candidate / reseller veto | 1 |
| **taken — and wrong** | **6** |

**Six misattributions. The cascade does not ship.** That outranks any accuracy
or cost number, and per MODEL-102's own acceptance criterion it ends the
question. No tuning was attempted.

### What the six actually were

They are worth reading, because they are not the failure the veto was built
for. **None of the six named the page's own organisation.** The MODEL-82
reseller veto worked: the platform was never picked.

| page | listed id | true creator (withheld) | the LLM named |
| --- | --- | --- | --- |
| anthropic | `deepseek-r1-distill-llama-70b` | deepseek | **meta** |
| inception | `deepseek-r1-distill-qwen-1-5b` | deepseek | **qwen** |
| perplexity | `deepseek-r1-distill-qwen-14b` | deepseek | **qwen** |
| cerebras | `deepseek-r1-distill-qwen-7b` | deepseek | **qwen** |
| moonshotai | `deepseek-r1-distill-qwen-32b` | deepseek | **qwen** |
| alibaba | `hermes-2-pro-llama-3-8b` | nous-research | **meta** |

Every one is the same error: **the base model's organisation, read out of the
product name, mistaken for the creator.** A DeepSeek distillation of a Qwen
base is DeepSeek's; `hermes-2-pro-llama-3-8b` is Nous Research's, not Meta's.

The deterministic layer already knows this — `candidate_orgs()` refuses to make
a page's organisation a candidate when it is only named as a base model, and
`test_page_org_named_only_as_a_base_model_is_still_not_a_candidate` pins it.
Jev, asked the same question, abstained on all 383. The LLM did not have that
rule and does not infer it, and a `-distill-` in a string is exactly the kind
of thing an accurate model will helpfully resolve the wrong way.

Two things follow, and both are why this was worth measuring rather than
assuming:

1. **The existing veto does not cover this.** It guards the listing platform.
   These answers came in past it because the wrong organisation was never the
   platform. A cascade built on the current veto is not protected.
2. **It only bites when the truth is absent from the options** — the new
   provider page, the freshly released model nobody else lists yet. That is
   precisely the case the daily research job meets first, and precisely where a
   wrong creator gets written to a card nobody is checking.

### Recommendation: do not enable the cascade

It ships off and stays off. The code, the flag, the budget, the provenance and
this measurement are committed so the decision is re-checkable, not so that it
is one config edit from live.

A future attempt has a defined bar to clear, and it is not a better prompt: the
escalation would need a **derivation rule** — a model named `<a>-distill-<b>`
or `<a>-on-<b>` is `<a>`'s — enforced in code on the way out, the way
`candidate_orgs()` enforces the base-model rule on the way in. Until something
like that exists and is measured on this same guard set at **zero**
misattributions, the honest answer is the one the catalogue already ships: Jev
abstains, the creator stays null, and a null beats a guess.

---

## Re-running it

```bash
curl -fsSL https://models.dev/api.json -o api.json

# step 1: the own-page subset, both questions, Jev only (~$0.006 the pair)
python scripts/eval_cost_to_correct.py --api-json api.json --arms jev \
  --own-page-only --question-variant own-page-eligible \
  --out ownpage.jsonl --max-usd 0.05

# step 2: the cascade as a fourth arm on the published case set
python scripts/eval_cost_to_correct.py --api-json api.json \
  --arms cascade:openai/gpt-5-mini --escalation-rate 0.15 \
  --out cascade.jsonl.gz --max-usd 0.30

# the guard: the cascade where naming any organisation is the MODEL-82 failure
python scripts/eval_cost_to_correct.py --api-json api.json \
  --arms cascade:openai/gpt-5-mini --variants relisted_withheld \
  --out guard.jsonl.gz --max-usd 0.80
```

`--escalation-rate` is the operator's stated pre-flight assumption about how
many cases reach the second model; `--max-usd` is enforced per call regardless,
and the run reserves each call's worst-case cost before making it.

Every paid answer behind this page is committed, one row per case, with the
chosen answer, the expected answer, correctness, the `misattribution` flag,
which arm produced the answer (`arm_used`), whether it escalated, both token
counts and the `request_sha256`:

| run | rows | file |
| --- | --: | --- |
| step 1, own-page, amended question | 164 | `scripts/ownpage_question_2026-09-20.jsonl.gz` |
| step 2, the fourth arm, `real` | 627 | `scripts/cascade_real_2026-09-20.jsonl.gz` |
| step 2, the guard, `relisted_withheld` | 383 | `scripts/cascade_guard_2026-09-20.jsonl.gz` |

```bash
# any of them, re-tabled with no key, no call and no money
python scripts/eval_cost_to_correct.py --analyse scripts/cascade_guard_2026-09-20.jsonl.gz
```

The step-1 baseline is not re-run here: it is the `jev` arm of MODEL-99's own
`scripts/cost_to_correct_2026-09-20.jsonl.gz`, and the 164 `case_id`s and
`request_sha256`s match it exactly.

Total spend for this page: **$0.69**, against a $2.00 budget.

### Tolerance on a re-run

The case set is deterministic for a given `api.json` and seed; the models are
not, and the corpus changes daily. The finding that matters is not the exact
six: it is that **the count is not zero**. A re-run that produces a different
six, or four, or nine, says the same thing. A re-run that produces zero on 383
`relisted_withheld` cases would be worth reporting against this page — and
would still not clear the bar on its own, because the failure has a mechanism
(base-model names in product strings) that no single clean run retires.

## Disclosure

ModelSpec pays for TypeSafe and the attribution pipeline depends on Jev
(MODEL-101). The escalation model is not TypeSafe's. Nothing here recommends a
supplier: it is one pipeline choosing the cheaper instrument first and paying
for a second opinion only when the first says it cannot tell. The harness, the
case construction, the prices and the raw rows are all in this repository, and
the finding that cost the most work — step 1's fix — is the one being
recommended *against*.
