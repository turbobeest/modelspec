# Class selection: which *class* of model a problem needs (MODEL-100)

*Design, written before the code. Decided 2026-09-20.*

ModelSpec answers "which model?" once you have already decided you want an LLM.
Every ranking profile in `api/ranking/engine.py` is built of benchmark weights,
and benchmarks score generated answers, so the whole apparatus presumes a
generator before the caller has said anything. The question that comes first —
**"which class of model does this problem need?"** — is not asked anywhere, by
us or by anyone else, and getting it wrong is not an inefficiency. It is the
architecture.

MODEL-99 measured the first case where the answer is not obvious. On creator
attribution, byte-identical inputs to every arm:

| arm | accuracy | p50 latency | $/1,000 correct |
| --- | --: | --: | --: |
| `jev-1.13.0` (decision model) | 90.1% | 180 ms | $0.036 |
| `openai/gpt-5-mini` (LLM, mid) | **97.9%** | 5,253 ms | $1.447 |

40× cheaper and 29× faster, 8 points less accurate overall and 21 points less
on the 67 ambiguous cases production actually pays for. **Neither arm is
better.** That is the shape of a good class-fit answer, and it is also the
shape of the refusal: no single number orders those two rows, and inventing one
would be the whole failure mode this ticket exists to avoid.

This document answers the six questions the work order asks, in order, and
records what is deliberately not built.

---

## 1. A coherent class taxonomy

### The problem with `ModelType`

`schema/enums.py` holds 35 values on four different axes at once:

| axis | values |
| --- | --- |
| **modality** | `image-generation`, `video-generation`, `audio-tts`, `vlm`, … |
| **role** | `reward-model`, `router`, `reranker`, `agent-model` |
| **lineage** | `adapter`, `quantized-variant`, `distilled`, `merged` |
| **domain** | `medical`, `legal`, `financial` |

A builder cannot select on that. `quantized-variant` and `llm-chat` are not
alternatives — one is a *provenance relation to the other*. `medical` and
`llm-reasoning` are not alternatives either; a medical model is a text
generator with a domain constraint, and the catalogue already ranks it that way
with a `medical` profile. The enum is a good publishing field and a bad
selection axis, and those are different jobs.

### The axis

**What it consumes, what it emits, and what decision it makes on the caller's
behalf.** Three facets, published per `ModelType`. A class is not a hand-written
list: it is **derived** from the pair `(emit_kind, decides)`, which is a
function a sceptic can evaluate.

`decides` has exactly six values, and it is the facet that does the real work,
because it is the one that changes the caller's code:

| `decides` | the caller's code afterwards |
| --- | --- |
| `nothing` | reads or renders the output; the model produced material, not a verdict |
| `what_order` | takes a permutation of items it supplied |
| `which_of_a_fixed_set` | switches on a label from a taxonomy the *model* defines |
| `which_of_a_caller_defined_set` | switches on a value from a set **the caller** defined at request time |
| `how_good` | compares two of its own outputs |
| `what_to_do_next` | executes an action |

The difference between rows 3 and 4 is the difference between a safety
classifier and a decision model, and it is already written down: the
`DECISION_MODEL` docstring in `schema/enums.py` says a safety classifier "has a
fixed harm taxonomy, while these labels are defined per request". This taxonomy
promotes that sentence to the axis.

`emit_kind` has twelve values (`open_text`, `media`, `transcript`, `vector`,
`ordering`, `label`, `choice`, `preference_score`, `action`, `series`,
`world_state`, `annotation`). `consumes` is a set over `text`, `image`, `audio`,
`video`, `page_image`, `structured_state`, `numeric_series`, `model_output`,
`item_list`, `observations`.

### The classes, derived

`(emit_kind, decides) -> class` is injective, so the table below is the
function, printed:

| class | consumes | emits | decides | `ModelType` values |
| --- | --- | --- | --- | --- |
| `text-generator` | text, image, audio | `open_text` | `nothing` | `llm-chat`, `llm-reasoning`, `llm-code`, `llm-base`, `vlm`, `medical`, `legal`, `financial`, `audio-realtime` |
| `media-generator` | text, image, audio | `media` | `nothing` | `image-generation`, `image-editing`, `video-generation`, `audio-tts`, `audio-music` |
| `transcriber` | audio, page_image | `transcript` | `nothing` | `audio-asr`, `document-ocr` |
| `vectoriser` | text, image | `vector` | `nothing` | `embedding-text`, `embedding-multimodal`, `embedding-code` |
| `orderer` | text, item_list | `ordering` | `what_order` | `reranker` |
| `labeller` | text, image | `label` | `which_of_a_fixed_set` | `safety-classifier` |
| `decider` | text, structured_state | `choice` | `which_of_a_caller_defined_set` | `decision-model`, `router` |
| `scorer` | text, model_output | `preference_score` | `how_good` | `reward-model` |
| `actor` | text, image, observations | `action` | `what_to_do_next` | `agent-model`, `robotics` |
| `forecaster` | numeric_series | `series` | `nothing` | `time-series` |
| `simulator` | observations | `world_state` | `nothing` | `world-model` |
| `analyser` | text, image, video | `annotation` | `which_of_a_fixed_set` | `vision-encoder`, `text-encoder` |

Twelve classes. Thirty of the thirty-five `ModelType` values. The remaining
five are the interesting part.

### Derive, do not replace

`ModelType` stays exactly as it is: it is published in
`/api/models/<id>.json`, `index.json`, `candidates.json` and every graph node,
and MODEL-98 has just spent a major version on it. The taxonomy is a **view
over it**, computed from the value and nothing else — the same discipline
`schema/applicability.py` adopted last commit, for the same reason: one table,
reviewed once, that cannot disagree with a card because a card never states it.

Two consequences, both deliberate:

* **No card gains a field.** Nothing to round-trip, nothing to drift.
* **The map is held to the enum by a test**, not by care. `api/classes.py` is
  keyed on `ModelType` *values as strings*, never on the enum itself — so the
  module imports nothing the Worker bundle does not already carry
  (`api/ranking/engine.py` is in it; `schema/`, which needs pydantic, is not)
  and can be vendored unchanged — and
  `tests/test_class_fit.py` fails if its key set is not exactly
  `{t.value for t in ModelType}`. A new enum member is a red test on the commit
  that adds it, which is where the argument about its class belongs.

### The values that do not fit the axis

**Lineage — `adapter`, `quantized-variant`, `distilled`, `merged`.** These
answer "where did these weights come from", not "what does this do". A
distilled model is a *smaller instance of its base model's class*; it is not an
alternative to it. They are mapped to the non-class `derived`, and the taxonomy
publishes the resolution beside it: **follow `lineage.base_model` and take that
card's class.** Class-fit never guesses one — `derived` appears in `excluded`
with `excluded_reason: "not_a_class"` and that resolution attached, rather than
being silently absent.

We deliberately do **not** fix this in the card data. The right fix is visible
and cheap to describe — `BaseModelRelation` already carries `adapter`,
`quantized`, `distillation` and `merge`, so the lineage value belongs there and
`model_type` should hold the base's class — but that is a migration across
every affected card, it would move a published field on hundreds of cards, and
it is a different ticket. Recorded here so the next person does not rediscover
it.

**Domain — `medical`, `legal`, `financial`.** A domain narrows the pool
*inside* a class; it does not name one. All three emit open text and decide
nothing, so all three are `text-generator`, with the domain carried as a
separate published facet. Nothing is lost: `USE_CASE_PROFILES` already holds
`medical`, `medical_clinical`, `medical_radiology`, `legal`,
`legal_contract_review`, `financial`, `financial_analysis` and
`financial_compliance`, which is exactly where a domain constraint should live —
within-class ranking.

**Role — `router`, `reranker`, `reward-model`.** A role earns a class only when
its `(emits, decides)` pair is distinct. `reranker` decides `what_order` and
`reward-model` decides `how_good`; both are distinct, both are classes.
`router` is not: it chooses one of a set of models the caller supplied, which is
`which_of_a_caller_defined_set` — the decider pair. It folds into `decider`,
which is what `schema/enums.py` already says in prose ("`router` and `reranker`
are *applications* of this class rather than the class"). Half that sentence
survives contact with the axis and half does not, and the axis is why we can
tell which half.

> **One tension, flagged not fixed.** `schema/applicability.py` puts `router`
> in `TEXT_WRITING_MODEL_TYPES`, so the catalogue currently believes a router
> has a maximum output-token count. Under this axis a router emits a choice,
> not text. Changing that set would change published `applicability` blocks on
> real cards one commit after they shipped, so it is left alone and written
> down here.

**`miscellaneous`.** Not a class, by its own definition ("for models no
specific type describes honestly"). Mapped to the non-class `unclassified`.
Class-fit excludes it and says so.

---

## 2. What a class-fit answer contains — refusal designed first

### What ModelSpec actually holds

Before designing an answer, the honest inventory of the evidence:

* **Per class:** the facets above, the `ModelType` values that derive to it,
  and how many active cards claim it. That is real, derived, and checkable.
* **Per card:** benchmark scores — which are *within-class by construction*.
  There is no MMLU for a vectoriser and never will be.
* **Across classes:** **one measurement, of one task** (MODEL-99), whose own
  page says "It is one task… Nothing here generalises."

So the rule that can be honestly applied is a **filter over facets**, not a
comparison. ModelSpec can say which classes *could* produce what the caller
needs. It cannot say which of them is better, for almost every task, and the
answer shape has to make that the normal case rather than an error.

### The refusal, first

Four statuses, mirroring `_ranking_status`'s `complete` / `partial` /
`unavailable` / `empty` rather than inventing a vocabulary:

| `fit_status` | when | what the caller gets instead of a guess |
| --- | --- | --- |
| `resolved` | exactly one class survives the filter | the class, its facets, its catalogue evidence, and the ranking profiles that rank within it |
| `partial` | **two or more survive** | every survivor, unordered, plus the *distinguishing question* — the facet they differ on, phrased as something the caller can answer |
| `unavailable` | zero survive | the published `emits` vocabulary and the full class list; nothing in this taxonomy produces what was asked for |
| `refused` | the request cannot be read as a task | the refusal code, and the vocabulary or the term list that would have matched |

`partial` is the **expected** answer, not a degraded one. It is the same
distinction the ranker already makes between `unranked` and "scored low":
a class ModelSpec cannot order is not a class ModelSpec disrecommends.

Per class, `class_status` is `candidate` or `excluded`, with
`excluded_reason` from a closed set:

| `excluded_reason` | meaning |
| --- | --- |
| `emits_wrong_kind` | it cannot produce the artefact the task needs |
| `consumes_unsupported` | it cannot take the inputs the task has |
| `decision_shape_mismatch` | it decides something other than what was asked |
| `not_described` | the task used none of this class's terms. **Only reachable when the caller supplied no facets** — a term is a hint and may discover a class, but it may never remove one the caller's own constraints admit |
| `not_a_class` | lineage or `miscellaneous`; the value names no class |

Request-level refusals, each naming what would have worked:

| code | when |
| --- | --- |
| `no_term_matched` | prose given, no published term in it |
| `unknown_facet_value` | a structured facet outside the published vocabulary |
| `empty_request` | neither prose nor a facet |

### Catalogue evidence, including "none"

Each candidate class carries `catalogue: {card_count, example_model_ids,
evidence_state}` where `evidence_state` is `populated` or `empty`.

**`empty` is a first-class answer and it is the answer today.** MODEL-98 added
`decision-model` to the enum last commit; MODEL-101 has not yet added a card.
So a caller whose task needs a `decider` is told, in the open: *this is the
class your problem needs, and ModelSpec catalogues zero of them — it cannot
name you a model.* An endpoint that could not say that would be worse than
useless on the very first case it was built for.

`example_model_ids` is at most three, sorted by `model_id`, so the answer is
reproducible and no ordering can be read as a recommendation.

### The distinguishing question

When two or more classes survive, computing the facet they differ on turns
"I cannot tell you" into work the caller can do. The questions are **published
per facet pair in the taxonomy file**, not generated:

> `open_text` vs `choice` — *"Does your code branch on the answer, or does a
> person read it? A value your code switches on wants a `decider`; prose a
> person reads wants a `text-generator`."*

Three or four of these cover the pairs that actually co-occur. They are data,
they ship in the published file, and a caller can disagree with the wording by
reading it.

### Composition — "both, in this order"

Some pairs of classes do not compete; they compose. The rule, published:

> When a candidate class `abstains` (its published `abstains: true` — it has an
> "I cannot tell" output state) **and** another candidate class decides the same
> shape from the same inputs, name the composition *A, then B on A's
> abstention.*

This is **not an ordering**. Neither class is placed above the other; the claim
is only that they chain. It applies today to exactly one pair — `decider` then
`text-generator` — and its evidence is one measured task: MODEL-99 found every
error in every arm was an abstention and no arm ever named a wrong
organisation, which is the precondition a cascade needs, and MODEL-102 is the
ticket that measures whether the cascade is worth it. The answer carries
`evidence: "one measured task"` and the document URL, never the numbers (§3).

---

## 3. No cross-class scores

### The rule

**No number that orders one class above another is ever emitted, and no
cost-to-correct evidence ever reaches `rank_score`.**

Cost-to-correct is *fitness evidence for a task*. `rank_score` is a
*within-class quality composite* over benchmarks, capabilities, cost and
context. Folding the first into the second would let a measurement of one task
lift a model in a ranking of a different one, and would do it invisibly,
because `rank_score` is a single number.

### Where it is enforced, in code

Four mechanisms, each a test rather than a convention:

1. **Shape.** The answer carries no numeric field under `classes[]` except
   `catalogue.card_count`. A test walks the response recursively and fails on
   any other `int`/`float`, naming the path. A score cannot be added by
   accident, only by editing that test.
2. **Order.** Candidates are returned sorted by class `id`. A test asserts the
   order is the sorted order, so no ranking can hide in the list order.
3. **Dependency direction.** `api/class_fit.py` imports `api/classes.py` and
   the standard library, nothing else. `api/ranking/engine.py` and
   `pipeline/ranking.py` import **neither**. An AST test over all four files'
   import statements enforces both directions — the same technique
   `tests/test_rank_worker.py` uses to prove no numeric floor exists in the
   Worker package. The boundary is therefore one a reviewer can see in a
   `git diff`, not one they have to trust.
4. **The numbers are not served.** MODEL-99's measurements stay in
   `docs/research/cost-to-correct-attribution.md`. Class-fit may cite the
   document and the task it measured; it never carries the figures, because a
   number printed beside a class name is a score whatever the key is called,
   and a reader will generalise it to their own task in exactly the way that
   page forbids.

---

## 4. How a task description becomes candidate classes

### The options, honestly

**(a) Keyword rules over a published mapping.**
*Deterministic, reproducible, free, auditable, and offline.* The caller can
fetch the same term list and run the same match themselves — which makes the
rule genuinely checkable rather than merely documented.
*It is dumb.* It misses paraphrase, it has no notion of negation ("it must not
write anything" matches the writing terms), it is English-only, and a task
described entirely in the caller's own vocabulary gets `refused`
(`no_term_matched`) rather than an answer.

**(b) Reuse the existing `use_case` taxonomy.**
Cheap: the 51 profiles already carry `preferred_types`, so a use case implies
classes for nothing. **Rejected, and this one is disqualifying rather than
merely weak.** Every profile is defined by `benchmark_weights`, and benchmarks
score generated text. `coding` presumes a text generator before the caller has
spoken. Routing class selection through that taxonomy could never return
`decider` for any input, which is precisely the bias MODEL-100 exists to
remove. A selector that cannot produce the surprising answer is not a selector.

**(c) A model call.**
Better recall on prose, by a lot. It costs three things:
*reproducibility* — the same request stops returning the same answer, and the
published rule stops being the rule; *money* — on a public, unmetered surface,
where MODEL-3's projection already shows CPU is the binding constraint on the
$5 plan; and *the architecture of the neutrality claim* —
`rank_service.py` states that "the request carries a *profile*, not a prompt.
… widening these fields toward prompt text is a contract change", and
`neutrality_commitment()` publishes `stores_customer_prompts: false` as
something the service is *structurally unable* to do rather than a promise. A
class-fit request that carries prose and forwards it to a provider weakens a
published assertion, for recall.

### Recommendation

**(a), with the facets as the primary input and prose as a convenience.**

The request accepts the facet vocabulary directly — `emits`, `consumes`,
`decides` — and a caller who knows what they need gets an exact, deterministic
answer with no text matching at all. Prose is a *term source only*: it is
tokenised, matched against published terms, and the response echoes **the
matched terms, never the input**. It is not stored, not logged and not
forwarded, which keeps the "nothing to retain" architecture intact rather than
converting it into a retention promise.

**A facet is a constraint; a term is a hint**, and they are not combined
symmetrically. A facet the caller supplied is an assertion about their own
problem, so it binds. A term match is our guess about their words, so it may
*discover* a class when nothing else was given, but it may never remove one the
caller's own constraints admit. A guess never overrides an assertion. This is
why the worked example below still returns `text-generator` even though the
attribution description contains none of that class's terms: the caller's
`emits` and `consumes` admit it, and our word list does not get a veto.

**`decides` is the strict facet.** `emits` and `consumes` admit published
adaptations — prose parsed into a choice, typed state serialised into text,
both of which MODEL-99 actually did and measured. `decides` admits none,
because adapting it means the caller writes the decision logic themselves,
which is a different architecture rather than a different model. There are
exactly two adaptations today and each is a claim that page can back.

**What it cannot do**, stated plainly and repeated in the published rule:
paraphrase; negation; any language but English; any task whose class depends on
volume, latency or budget rather than on words; and any task described without
using one of the published terms — which is `refused`, not guessed at. The
terms are the weakest part of this design and they are the part most likely to
need a second pass once real requests exist.

---

## 5. The published decision rule

`ranking_policy()` publishes the floors and `neutrality_commitment()` publishes
the honest-broker promise, both keyless, both beside the answer they shaped.
The class-fit rule ships the same way — as **data a sceptic can read and
re-run**, not a black box:

```jsonc
// https://modelspec.dev/api/rank/class-fit.json  — static Pages, no key
{
  "build": { "commit": "…", "export_schema_version": "3.0" },
  "policy": {
    "version": "class-fit-v1",
    "basis": "model_type",
    "axis": ["consumes", "emits", "decides"],
    "derivation": "class = CLASS_BY_PAIR[(emit_kind, decides)]",
    "orders_classes": false,
    "cross_class_scores": "never",
    "task_matching": "exact token match over the published terms below; no model call",
    "request_text": "matched and discarded; never stored, logged or forwarded",
    "cannot": ["paraphrase", "negation", "languages other than English",
               "constraints of volume, latency or budget"],
    "refuses_when": [
      {"code": "no_term_matched",    "meaning": "…"},
      {"code": "unknown_facet_value","meaning": "…"},
      {"code": "empty_request",      "meaning": "…"}
    ],
    "fit_statuses": ["resolved", "partial", "unavailable", "refused"],
    "excluded_reasons": ["emits_wrong_kind", "consumes_unsupported",
                         "decision_shape_mismatch", "not_a_class"],
    "composition_rule": "…",
    "neutrality": { /* neutrality_commitment(), called not copied */ }
  },
  "vocabulary": { "consumes": [...], "emits": [...], "decides": [...] },
  "classes": [
    {
      "id": "decider",
      "consumes": ["text", "structured_state"],
      "emits": "choice",
      "decides": "which_of_a_caller_defined_set",
      "abstains": true,
      "model_types": ["decision-model", "router"],
      "terms": ["classify", "decide", "route", "triage", "judge", …],
      "rank_profiles": [],
      "catalogue": {"card_count": 0, "example_model_ids": [],
                    "evidence_state": "empty"}
    }
    // … 11 more, plus the non-classes `derived` and `unclassified`
  ],
  "distinguishing_questions": [ {"between": ["open_text", "choice"], "ask": "…"} ]
}
```

Three properties worth naming:

* **`neutrality` is the function's return value, not a copy of its strings.**
  `neutrality_commitment()` is called. Editing the published terms stays a
  single-source edit, and `tests/test_legal.py` keeps prose and JSON together
  exactly as before.
* **`rank_profiles` is derived, not authored.** It is every
  `USE_CASE_PROFILES` entry whose `preferred_types` intersect the class's
  `ModelType` values. For `decider` that list is **empty today**, which is the
  true and useful statement that ranking stops at this class boundary.
* **The whole rule is in the file.** A caller can run the match locally against
  a static asset, with no key, no account and no request. That is a stronger
  form of publication than an endpoint that merely documents its behaviour.

---

## 6. Surfaces, and what each costs

| surface | what it costs | verdict |
| --- | --- | --- |
| **Static `/api/rank/class-fit.json`** | one small file (14 KB measured) written at build time; zero request CPU; no key | **ship** |
| **`modelspec offline class-fit` (CLI)** | a command beside `offline rank` / `offline fit`; counts classes from the snapshot's own `candidates.json`, so no new snapshot file and no contract change | **ship** |
| **`POST /v1/class-fit`** | entry routing, the access gate, and — because `tests/test_api_docs.py::test_the_spec_describes_exactly_the_endpoints_the_worker_routes` reads `entry.ACCEPTED_ENDPOINTS` — a full generated OpenAPI operation with inferred response schemas, cross-checked error codes and a word-budgeted reference doc | **defer** |
| **A step inside `POST /v1/rank`** | would add a prose field to a request whose contract says it carries a profile, not a prompt | **refuse** |
| **MCP tool** | a proxy tool beside `list_use_cases`, ~15 lines of TypeScript fetching the static file | **defer, but it is next** |
| **Wizard step** | a step in `web3d/downselect.v2.html` reading the same file | **defer** |

### The CPU argument

MODEL-3's traffic projection (2026-09-20) is the binding number: **121 ms CPU
per request measured, 288.78 ms median on the active deployment**, against
30M included CPU-ms a month, so the included CPU runs out at ~104,000–248,000
requests a month while requests are barely 2% used. Per-request CPU is the
scarce resource, and the overage economics on the Team credit rate are already
a loss at 289 ms.

Class-fit's own work is negligible, and measured rather than assumed: **0.43 ms
per answer** on CPython for the worked example below, against a published file
of **14,297 bytes** that costs **0.52 ms to parse**. `candidates.json` is
~2 MB, so class-fit does not even pay the parse that ranking pays — an answer
is roughly 0.4% of a rank call's measured 121 ms, and a rounding error against
the 288.78 ms median. That is exactly why the endpoint is the wrong place to spend
first: the answer costs nothing to compute and can be served as a static file,
so paying Worker CPU and a full OpenAPI operation for it buys only the HTTP
verb. `MODEL-100`'s own acceptance test — *"how often is the answer
surprising?"* — is answered by the static file and the CLI just as well, and by
the time an endpoint is justified we will know what the terms should have been.

---

## What ships in the first slice

1. `api/classes.py` — the taxonomy: vocabularies, facets per `ModelType`, the
   `(emit_kind, decides) -> class` derivation, terms, distinguishing questions,
   `class_fit_policy()`. Standard library only, so it can be vendored into the
   Worker bundle unchanged when the endpoint is built.
2. `api/class_fit.py` — the rule: facets and/or prose in, a `fit_status` answer
   out, every refusal path present from the first commit.
3. `pipeline/ranking.py::write_export` — dumps `class-fit.json` beside
   `profiles.json`, with catalogue counts computed from the cards.
4. `modelspec offline class-fit` — the CLI surface.
5. `tests/test_class_fit.py` — exhaustive `ModelType` coverage, every refusal,
   the no-score boundary tests of §3, and the MODEL-99 case worked end to end.
6. This document, and a note in `CLAUDE.md`.

**Contract impact: none.** Every addition is a new file or a new key.
`build.export_schema_version` stays `3.0`, the CLI envelope stays `1.0`, and
`rankings.json` stays `2.0`. No field's range widens (MODEL-59).

## Scope kept out

* **No Jev card.** MODEL-101 is running in parallel; `models/typesafe/` is not
  touched. The `decider` class correctly reports zero cards, and that is the
  worked example, not a gap.
* **No ranking floor and no `neutrality_commitment()` string is touched.**
  The commitment is *called*, never transcribed.
* **No `ModelType` value is added, removed or re-spelled.** The taxonomy is a
  view.
* **No lineage migration.** `adapter` / `quantized-variant` / `distilled` /
  `merged` keep their `model_type`; the taxonomy refuses to class them and
  names `lineage.base_model` as the resolution.
* **No cost-to-correct number is served**, on any surface.

## The single biggest weakness

The terms. Everything else in this design is derived from something —
the classes from the facets, the facets from `ModelType`, the profiles from
`preferred_types`, the counts from the cards. The term list is the one place
where a human wrote down what words a task might use, and it is the part that
decides whether a real request gets an answer or a `no_term_matched`. It is
published so it can be argued with, and it will be wrong until real requests
show which words people actually use.
