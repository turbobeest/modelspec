# The ModelSpec decision contract

Contract version: **2.14**

The opt-in bounded HTTP response is a separate representation with its own
version, **bounded 1.0**. It does not carry a 2.x `contract_version`. See
[Bounded HTTP responses for agents](#bounded-http-responses-for-agents-model-293).

A **spec** asks for a decision. A **decision** is the engine's answer to one
spec against one snapshot. This document is the public contract for both. The
same contract serves the local library and CLI, the hosted API, and the MCP
`decide` tool. MCP clients can read the published vocabulary through the
companion `vocab` tool before constructing a spec.

- Types: [`decision/contract.py`](../decision/contract.py).
- JSON Schema, generated from the types:
  [`decision-contract.schema.json`](decision-contract.schema.json). Regenerate
  it with `python -m decision.schema`. Do not edit it by hand.
- Design: `docs/design/decision-engine.md` §6–§7. Terms: `CONTEXT.md`.

`tests/test_decision_contract.py` fails if this document, the schema and the
types disagree: every field and every closed value below must appear here, and
every example below must parse.

This contract is separate from the v1 CLI envelope (`schema_version`, see
[`cli-contract.md`](cli-contract.md)) and from `/v1/rank`. Neither changes.

> **Status, slice 1.** The types, parser, canonical hash, engine, explanations,
> and `modelspec decide` are built. Free-text `task` is parsed but refused.

---

## The spec

```yaml spec
spec_version: 1
snapshot: latest
profile: profile:acme-prod
task_type: refactor
capabilities:
  software_engineering: required
  formal_verification: preferred
exclude_benchmarks: [swe_bench_pro]
task_tokens: { input: 60000, output: 6000 }
where:
  - offering.price.input in [0.50, 3.00]
  - swe_bench_pro >= 55 @independent @default_effort measured_after 2026-06-01
  - any: [ offering.provider = aws-bedrock, model.weights_openness = open_weights ]
  - not: licence.commercial_use = prohibited
  - software_engineering >= model(openai/gpt-6-sol)
  - model.context_window >= 200000 soft(0.2)
  - offering.cost_per_task <= 0.25
  - facet: offering.data.trains_on_customer_data
    op: "="
    value: false
    unknown: fail
optimize:
  weights:
    software_engineering: 0.5
    -offering.price.output: 0.2
    model.weights_openness: { prefer: open_weights, weight: 0.3 }
unknowns: default
explain: summary
limit: 20
save_as: acme-rust-refactor
```

| Field | Type | Default | Meaning |
|---|---|---|---|
| `spec_version` | `1` | required | The spec format. Only `1` exists. |
| `snapshot` | `latest` or a snapshot ID (`snap_…`) | `latest` | Which snapshot to answer from. Pin an ID to reproduce a decision. |
| `profile` | `profile:<name>`, or an inline profile | none | The inventory profile. Without one, the whole catalogue is the inventory. |
| `task` | string | none | Free text for the decision model. **Not yet in slice 1:** a spec that sets it is refused. Send `task_type` and `capabilities`. |
| `task_type` | closed set, below | none | What kind of task this is. |
| `capabilities` | map of domain ID to `required` or `preferred` | none | The capabilities the task needs. |
| `exclude_benchmarks` | list of benchmark IDs | `[]` | Verified evidence from these benchmarks cannot filter, answer an objective or contribute to a capability estimate. Unknown IDs are refused. |
| `task_tokens` | `{input, output}`, whole numbers ≥ 0 | `{input: 40000, output: 4000}` | Tokens one task takes. Prices `offering.cost_per_task`; see below. |
| `where` | list of conditions | `[]` | Conditions, ANDed, applied in order. The order sets the order of the elimination funnel. |
| `optimize` | objective | required | Exactly one objective form. |
| `unknowns` | `default` | `default` | How unknown values are handled when a condition does not say. The only value is `default`: capability facets list the model as "may qualify", governance facets count it as not satisfied. |
| `explain` | `none`, `summary`, `full` | `summary` | How much explanation to return. |
| `limit` | integer, 1–500 | `20` | The maximum number of results. |
| `save_as` | lowercase slug | none | A name to save the spec under. Saved specs and alerts arrive in a later slice. |
| `estate` | object, see [The estate](#the-estate-model-179) | none | What the caller holds: provider keys, subscription plans, devices, and what is exhausted right now. It adds a second answer, `with_estate`; the unrestricted answer does not change. |

A spec with a field not named here is refused. Nothing is silently ignored.

### Excluding benchmarks

`exclude_benchmarks` lets the person asking distrust one or more registered
benchmarks for one decision. The engine treats the list as a set, sorts it for
the canonical spec hash, and removes those evidence rows before it filters,
optimises or explains. It then refits the capability estimates from the
snapshot's remaining verified evidence. No fixed replacement weights or
benchmark list are used.

An omitted field and `exclude_benchmarks: []` have the same canonical JSON and
produce byte-identical decisions. A non-empty list must contain benchmark IDs
from the loaded snapshot. An unknown ID returns `invalid_spec` at the field's
list position.

The loaded snapshot caches a refit by its content hash and the sorted excluded
set. The first request for a set pays the full deterministic fit. Later
requests reuse it. This keeps warm Worker requests within the one-second
budget at the cost of retaining up to 16 fits per loaded snapshot; the least
recently used set is evicted when a seventeenth arrives. On 2026-09-28, the
current lineup took 2.24 seconds for the first refit and 90.20 ms cached warm
p95 over 20 requests on the shared development Mac. The Worker test gates
cached warm p95 below one second.

**`task_type`** is one of `new_feature`, `bug_fix`, `refactor`,
`test_writing`, `docs`, `migration`, `performance`, `security_fix`, `review`,
`analysis`, `data_transform`, `config_infra`: the outcome protocol's task
types.

**Identifiers.** A facet ID is lowercase and dotted (`origin.lab_jurisdiction`). A
model ID is `lab/model`. A harness ID is `name@major.minor`
(`claude-code@2.1`). Every facet a spec names must be in the facet registry
(`decision.registry`, MODEL-133), or the spec is refused.

**Values.** Every value a condition or preference names must fit its facet
(MODEL-318). An enum or set value must be one of the facet's registered values,
unless the list is open, such as ISO 3166 codes; `offering.provider` also
takes a registered vendor, the owner of a subscription plan. A boolean takes `true` or
`false`, a number facet takes a number (or `unbounded` or `not_offered` where
the facet admits it), and a date facet takes an ISO date. Anything else is
refused with `invalid_spec`. The issue names the `field`, the `value` sent, the
facet's `value_type`, its `allowed_values` when the list is finite, and `next`,
the vocabulary lookup for that facet in the section that lists it: `facets`,
`benchmarks` or `domains`
(`https://api.modelspec.dev/v1/vocabulary?section=facets&id=<facet>`).

### Cost per task

The design's unit of cost is one task. `task_tokens` says how many input and
output tokens a task takes, and the engine computes the facet
`offering.cost_per_task` (unit `usd_per_task`) for every offering:

```text
offering.cost_per_task = (offering.price.input × input + offering.price.output × output) / 1,000,000
```

- Both prices are the offering's list prices in USD per 1M tokens. When either
  is unknown, the cost per task is unknown, and a condition on it follows the
  unknown rules below (it is a capability facet, so the offering may qualify).
- Without `task_tokens` the engine prices at `input: 40000`, `output: 4000`.
  The spec hash leaves an absent `task_tokens` out, so a spec that does not use
  it keeps its 1.2 hash; writing the default values explicitly is a different
  spec with a different hash.
- It is a computed facet (`computed_by` in the registry): it is never stored in
  a snapshot or written on a card, and it has no record of its own. Wherever an
  explanation shows it (a contribution, a near miss, an elimination, a shown
  fact), `records` names the two price records and `formula` shows the
  calculation with the numbers:
  `(1 USD per 1M input tokens × 40,000 input tokens + 5 USD per 1M output tokens × 4,000 output tokens) ÷ 1,000,000 = 0.06 USD per task`.
- Use it like any number facet: `offering.cost_per_task <= 0.10` in `where`,
  `-offering.cost_per_task` in `weights` or `pareto`, `min:
  offering.cost_per_task`.

### The inventory profile

A profile is referenced as `profile:<name>`, or written inline:

```yaml
profile:
  profile_version: 1
  id: profile:acme-prod
  offerings:
    - { model: anthropic/claude-opus-5-5, provider: aws-bedrock, region: us-east-1, tier: enterprise }
  local:
    - model: qwen/qwen3-8-27b
      runtime: vllm
      hardware: { class: nvidia-dgx-spark, count: 2, memory_gb: 256 }
  harnesses: [ claude-code@2.1, dpf-native@1.0 ]
  rules:
    - origin.lab_jurisdiction in {US}
    - licence.commercial_use != prohibited
  budget: { max_cost_per_task_usd: 2.00 }
```

- `profile_version`: `1`.
- `id`: optional `profile:<name>`.
- `offerings`: what the customer can call. Each has `model`, `provider`, and
  optional `region` and `tier`.
- `local`: self-hosted models. Each has `model`, optional `runtime`, and
  optional `hardware` with `class`, `count` (default 1) and `memory_gb`.
- `harnesses`: harness IDs the customer runs.
- `rules`: conditions applied to every decision, before `where`.
- `budget`: optional `max_cost_per_task_usd`.

## Conditions

Every condition has two spellings that parse to the same thing: a compact
string and a YAML mapping. A list may mix them. The spec hash does not change
between spellings.

### The compact form

```text conditions
offering.price.input in [0.5, 3.0]
origin.lab_jurisdiction in {US, CA}
origin.lab_jurisdiction not in {CN, RU}
licence.commercial_use != prohibited
offering.provider = aws-bedrock
offering.provider = "a value with spaces, or a comma"
known(model.parameters_total)
software_engineering >= model(openai/gpt-6-sol)
software_engineering >= best(1.0)
model.context_window >= 200000 soft(0.2)
offering.data.trains_on_customer_data = false unknown(fail)
swe_bench_pro >= 55 @independent @default_effort measured_after 2026-06-01
swe_bench_pro >= 40 @any @effort(high) @harness(claude-code@2.1) @direct
any(offering.provider = aws-bedrock; model.weights_openness = open_weights)
all(offering.price.input <= 3; not(licence.commercial_use = prohibited)) soft(0.5)
not(licence.commercial_use = prohibited)
```

- **Comparisons:** `=`, `!=`, `<`, `<=`, `>`, `>=`. `==` is refused.
- **Windows:** `facet in [low, high]`, both ends inclusive. The ends are both
  numbers or both dates, and `low <= high`.
- **Sets:** `facet in {a, b}` and `facet not in {a, b}`. The engine sorts set
  values and removes duplicates. On a facet whose value is itself a set, such
  as `model.input_modalities` or `origin.lab_jurisdiction`, `in` passes when
  the model's set holds at least one listed value, and `not in` passes only
  when it holds none of them.
- **Existence:** `known(facet)` passes when the value is known. It is never
  unknown itself, so it takes no unknown policy.
- **Relative:** `facet op model(<model ID>)` compares against another model's
  value on the same facet. `facet >= best(m)` keeps the models within `m` of
  the highest value on the facet among the models that pass every other hard
  condition; see [Relative to the best](#relative-to-the-best). Only `>=` takes
  `best(m)`, `m` is a number of 0 or more, and the facet must be a number.
- **Capability domains:** a condition on a domain, such as
  `software_engineering >= 0.5` or `known(software_engineering)`, reads the
  model's capability estimate on that domain (after `exclude_benchmarks`).
- **Groups:** `any(…; …)`, `all(…; …)` with at least two conditions, and
  `not(…)` with one, separated by `;`.
- **Values:** `true` and `false`; numbers; ISO dates (`2026-06-01`); bare
  words, which may contain `. : / + @ -`; anything else in double quotes.
- **Modifiers** follow the condition, in any order: evidence qualifiers,
  `measured_after <date>`, `soft(<penalty>)`, `unknown(<policy>)`.

The canonical compact form writes `soft(0.2)` and `unknown(fail)`. The spellings
`soft(penalty: 0.2)` and `unknown: fail` are also accepted inside a string, but
in YAML an unquoted `: ` starts a mapping. A spec that YAML has split this way
is refused with a message that says to quote the condition.

### The YAML form

| Condition | Keys |
|---|---|
| Comparison, relative | `facet`, `op`, `value` (a scalar, `{ model: <model ID> }`, or `{ best: <margin> }` with `op: ">="`) |
| Window | `facet`, and `between` as `[low, high]` |
| Set | `facet`, and a list under one of `in` or `not_in` |
| Existence | `known`, naming the facet |
| Groups | `any` or `all` with a list of conditions; `not` with one |

Comparisons and windows also take `qualifiers`. Every condition except
`known` takes `unknown`, and every condition takes `soft`:

```yaml
- facet: swe_bench_pro
  op: ">="
  value: 55
  qualifiers: { measured_by: independent, effort: default, measured_after: 2026-06-01 }
- facet: model.context_window
  op: ">="
  value: 200000
  soft: { penalty: 0.2 }
- any:
    - offering.provider = aws-bedrock
    - { facet: model.weights_openness, op: "=", value: open_weights }
  unknown: list
```

### Relative to the best

`facet >= best(m)` is a floor that moves with the answer, not with the lineup.
Its anchor is the set of models still feasible once every hard condition
without `best(…)` has run: never a model that only may qualify, and never one
already eliminated. The bar is the highest known value on the facet among the
anchor models, less `m`: for an evidence facet, each model's highest admitted
result; for a domain, its capability estimate. With no known value in the
anchor, the condition is unknown for every model. A model below the bar is
eliminated with its own value, and a near miss's `distance` is measured to the
bar: 0.28 against a bar of 0.32 is a distance of 0.04.

Every condition that contains `best(…)` runs after the others, in the spec's
order, and the funnel lists it after them. All of them share the one anchor,
so two `best(…)` conditions give the same answer in either order, and a
`best(…)` written first still anchors on what the other conditions leave. A
soft `best(…)` costs its penalty and removes no one.

The margin is on the point value, not a probability such as the bands' `P(its
score >= the leader's)`. A probability floor would let a model pass because it
has little evidence: a wide interval cannot be shown to be worse. Every other
condition compares point values too. Among the models that pass, the bands
still decide the answer.

### Evidence qualifiers

Qualifiers restrict which evidence can satisfy a condition on an evidence
facet.

| Compact | YAML (`qualifiers`) | Admits |
|---|---|---|
| `@independent` | `measured_by: independent` | Evidence not measured by the model's lab or provider. |
| `@provider_self_report` | `measured_by: provider_self_report` | Only the lab's or provider's own reports. |
| `@any` | `measured_by: any` (`any`) | Any measurer. This is also what an absent `measured_by` means. |
| `@default_effort` | `effort: default` | Evidence run at the model's default effort. |
| `@max_effort` | `effort: max` | Evidence run at the model's maximum effort. |
| `@effort(x)` | `effort: x` | Evidence run at effort `x`. |
| `@harness(x)` | `harness: x` | Evidence run inside harness `x`, a `name@major.minor` ID. |
| `@direct` | `direct: true` | Direct evidence only; proxies are excluded. Directness is relative to the spec's `capabilities`: the benchmark must be tagged `direct` for one of them. With no `capabilities`, a `direct` tag for any domain is enough. |
| `measured_after <date>` | `measured_after` | Evidence dated after the given date. |

Two qualifiers that set the same thing differently, such as `@independent
@provider_self_report`, are refused.

### Unknown values

`unknown` says what a condition does with a model whose value is unknown:

- `list`: the model is not ranked, and appears in `may_qualify`.
- `fail`: the model counts as failing the condition.
- `pass`: the model counts as passing the condition.

Without `unknown`, the facet's risk direction decides: capability facets
`list`, governance facets `fail`. A capability filter never silently drops a
model, and a governance filter never passes one it cannot confirm.

### Soft conditions

`soft(penalty)`, with `0 < penalty <= 1`, makes a condition a preference.
Violating it does not eliminate the model; it costs the result `penalty` on its
normalised objective. How the penalty enters each objective form is specified
with the engine (MODEL-142). A result's total is always reported in
`soft_penalty`.

## The objective

`optimize` takes exactly one of these forms.

| Form | Example | Meaning |
|---|---|---|
| `max` | `max: swe_bench_pro` | Highest value first. |
| `min` | `min: offering.price.output` | Lowest value first. |
| `lexicographic` | see below | Order by the first step, then break near-ties with the next. |
| `weights` | `weights: { software_engineering: 0.6, -offering.price.output: 0.3 }` | A weighted sum over normalised facets. The normalisation is reported in each contribution. |
| `pareto` | `pareto: [ software_engineering, -offering.price.output, offering.speed.throughput ]` | The non-dominated set. |

In `weights` and `pareto`, a leading `-` on a facet means lower is better.
Weights are positive; a facet may appear once. `pareto` needs at least two
dimensions.

Number facets use a positive number as their weight and retain feasible-set
continuous normalisation. Boolean and enum facets use a value preference:

```yaml
optimize:
  weights:
    model.weights_openness: { prefer: open_weights, weight: 0.3 }
    offering.data.zero_retention: { prefer: true, weight: 0.2 }
```

A value preference contributes 1 when the fact equals `prefer`, and 0 when it
does not. An unknown fact also contributes 0, remains in `results`, and adds
`unknown_preference_value` to the result's `warnings`. Its contribution sets
`preference_status` to `unknown`; known facts use `satisfied` or
`not_satisfied`. The contribution's `preferred_value` repeats the requested
value. A value preference cannot use a leading minus sign. A plain numeric
weight on a boolean or enum facet is refused because it does not name the
preferred value.

A scale facet can be Must and Prefer at once by naming it in both places. Put
the threshold in `where` and its continuous weight in `optimize.weights`:

```yaml
where: [offering.cost_per_task <= 0.25]
optimize:
  weights: {-offering.cost_per_task: 0.4, software_engineering: 0.6}
```

The `where` condition remains a gate and never adds points. The weight ranks
only the candidates that pass the gate.

An evidence objective can carry the same qualifiers as an evidence condition:

```yaml
optimize:
  max: swe_bench_pro @independent @default_effort
```

Qualifiers also work on weighted, Pareto, and lexicographic terms. Quote a
qualified mapping key, for example
`weights: {"swe_bench_pro @independent": 1}`. They select matching verified
measurements before optimisation; they never add a score. Qualifiers on a
non-evidence facet are refused.

```yaml
optimize:
  lexicographic:
    - max: offering.speed.throughput within 5%
    - { min: offering.price.output, within: 0.25 }
    - max: software_engineering
```

A `lexicographic` objective has at least two steps. Each step is one of `max` or
`min`, with an optional `within`: a tolerance for ties, either `relative`
(`5%`, stored as `{ relative: 0.05 }`) or `absolute` (`0.25`, stored as
`{ absolute: 0.25 }`). The last step has nothing after it, so it takes no
`within`.

### Refinement weights

A `weights` key can name a refinement: `<domain>/<refinement>`, the
`weight_key` the vocabulary publishes (MODEL-190).

```yaml
optimize:
  weights: {software_engineering: 0.3, software_engineering/rust: 0.3, -offering.cost_per_task: 0.4}
```

A refinement estimate nests in its parent domain. It is the domain estimate,
read without the refinement's own benchmarks, plus a partially pooled
adjustment learned from every benchmark tagged to the refinement. A model with
no refinement evidence keeps its domain value with a wider interval, and stays
in `results`: it is never dropped for missing refinement evidence. A
cross-domain refinement (parent `any`) nests in the population prior instead.

A refinement weight is a positive number, never a value preference. The engine
accepts it only when the vocabulary's `evidence_state` for that refinement is
`live` or `thin`. A `not_measured` or `no_benchmark` refinement, or a key the
snapshot does not register, is refused with `invalid_spec`, naming the state
and the parent domain to rank on instead. A refinement is unknown only when its
parent is; `may_qualify[].unknown` then names the parent. The tie rules of the
`answer` block apply unchanged.

The `max`, `min`, `lexicographic` and `pareto` forms must name ordered facets.
A `bool`, `enum` or `string` facet cannot be maximised, windowed or compared
with `<`; boolean and enum facets are usable only as value terms in `weights`.

## The estate (MODEL-179)

A caller holds some things and not others: a key for one provider, a
subscription plan, a GPU. `estate` says which, and the decision answers twice:
the unrestricted answer, exactly as without an estate ("if you could use
anything"), and `with_estate` ("with what you have"). An estate is optional; a
spec without one gets a decision with no `with_estate` and is unchanged.

```yaml
estate:
  providers: [anthropic, together-ai]
  plans: [anthropic/subscription/pro]
  devices: [apple_m3_max]
  exhausted: [anthropic/subscription/pro]
```

| Field | Meaning |
|---|---|
| `providers` | Provider IDs the caller has a key for. Their offerings are reachable at list price. |
| `plans` | Subscription plan IDs (`<provider>/subscription/<plan>`) the caller pays for. The plan's documented models are reachable from that provider at a marginal cost of 0: the fee is already paid. A plan that does not disclose its coverage reaches nothing for certain; the provider's offerings are `may_qualify` on `offering.subscription.models_covered`. |
| `devices` | Hardware SKU IDs. Open-weights models whose published fit includes the device are added as self-hosted rows at a marginal cost of 0. A device the fit is indeterminate on makes the model `may_qualify` on `model.fits_hardware`. |
| `exhausted` | Providers or plans that cannot be used right now (a spent window, a hit rate limit). An exhausted plan drops out of `with_estate` only, and the key path to the same provider stays usable. An exhausted provider takes its key and its plans with it. |

IDs come from the published vocabulary's `estate` section. An ID it does not
list is refused as `invalid_spec`, naming the path (`estate.providers[1]`).
Each list is sorted and deduplicated before hashing, so `spec_hash` does not
depend on order. A key the caller holds is never sent: an estate names a
provider, not a secret.

**Not stored.** The estate travels in the spec and is used for that one
decision. ModelSpec keeps no estate server-side, writes none to a log and
echoes it nowhere but the `with_estate` block of the reply. A caller who wants
the same answer sends the same spec again.

### `with_estate`

The same question over the rows the estate reaches. The unrestricted `answer`,
`results`, `may_qualify` and probabilities are computed without the estate and
are byte-identical to the decision for the same spec without one.

| Field | Meaning |
|---|---|
| `status` | `answered`, `partial` or `no_feasible`, as for the decision, over the estate lineup. It can differ from the unrestricted status when the estate does not reach a model the unrestricted lineup left in `may_qualify`, or reaches one the unrestricted lineup did not. The ranked models can be the same in both answers. `no_feasible` here means the estate reaches nothing that qualifies; it carries no `relax`, because the gap and `gain` say what to add. |
| `answer` | The model-level answer over the estate, as in [The answer](#the-answer). Null when the estate reaches no scored model. |
| `results` | Ranked as the decision's results are. Each is `rank`, `offering` (a self-hosted row has no `provider`), `soft_penalty`, `warnings` and `estate`. |
| `results[].estate` | How the estate reaches the row: `via` is `{kind, id}` with `kind` one of `provider`, `plan` or `device`; `cost_basis` is `list_price`, `plan_included` or `owned_hardware`; `marginal_cost_per_task_usd` is what one more task costs the caller (0 inside a plan or on an owned device, the list `offering.cost_per_task` on a key, null when the price is unknown). The marginal cost drives a cost objective. When several holds reach a row the plan wins, then the key, then the device. |
| `may_qualify` | As for the decision, over the estate. |
| `truncated` | As for the decision. |
| `gap` | Why the two answers differ. `same_answer` is true when the estate reaches the unrestricted answer, `unreachable_models` lists the models the unrestricted ranking puts above the estate's leader that it cannot reach, and, when the unrestricted answer is a tie, every tied member it cannot reach, and `summary` says so in a sentence. |
| `gain` | Holds the caller lacks whose addition would change the `with_estate` answer, each as `add` (`{kind, id}`), the `status` and `leader` it would give, and the `answer`. A hold that reaches nothing new, an exhausted one and one already held are not offered. |

### Contract note

`with_estate` and `estate` are new optional fields, so this is a minor bump.
No closed value is widened: `status` is reused, and the error for an unknown
estate ID is the existing `invalid_spec`.

## Access and plans (MODEL-200)

People choose a model by how they will use it. `access` says how; leaving it
out means it does not matter, and the decision is byte-identical to one from
before 2.6 but for `contract_version`.

```yaml spec
spec_version: 1
optimize: {max: model.context_window}
access: {kind: coding_tool, harness: claude-code}
estate:
  plans: [anthropic/subscription/max-20x]
```

`access` is `{kind, harness}`, or the bare kind as a string
(`access: chat_app`). `harness` is a harness name from
`registry/harnesses.yaml`, without a version, and only for `coding_tool`; an
unregistered one is `invalid_spec` at `access.harness`.

| `kind` | Routes that count |
|---|---|
| `chat_app` | Subscription plans whose surfaces include `chat_app`, `desktop_app` or `mobile_app`. Ranked on capability. A plan has no per-task price, so `cost_per_task` is null; the plan's monthly price is the `where` facet `offering.plan.price_monthly` and breaks ties (`answer.tie_breakers.cheapest` is the model with the cheapest plan). |
| `coding_tool` | Pay-per-use offerings, and plans whose surfaces include `coding_tool:<harness>` (any harness when `harness` is absent). Each result lists its plans with a break-even. |
| `own_software` | Pay-per-use offerings, and plans whose surfaces include `api`. A plan without `api` does not cover the caller's own software. |
| `own_hardware` | Self-hosting only: models with a published fit on some device. An open-weights model with no published fit is `may_qualify` on `model.fits_hardware`; a closed-weights one is not a route. |

A route outside the access is not in the lineup at all. A plan whose surfaces
are unknown makes the rows it may cover `may_qualify` on
`offering.subscription.surfaces`, and a plan whose coverage is unknown on
`offering.subscription.models_covered`, as for an estate. A row another route
reaches is ranked through that route.

### Plans

A plan is a set of sourced facts on `offering.subscription.*`, each under the
fact and two-key rules, each null until published:

- **price**: `offering.subscription.price` and `offering.subscription.billing_period`,
  in US dollars.
- **coverage**: `offering.subscription.models_covered` names model IDs, and
  `offering.subscription.families_covered` names families from
  `registry/families.yaml`, with the plan page's exact words in
  `offering.subscription.coverage_quote`. Providers name families, not model
  IDs. **The resolution rule:** a family resolves to every model in the
  snapshot's lineup, not retired, whose ID starts with the family's `prefix`
  (`anthropic/claude-opus` resolves by `anthropic/claude-opus-`). A plan
  covers the union of the models named and the families resolved. Coverage is
  unknown only when both facts are.
- **surfaces**: `offering.subscription.surfaces`, from `chat_app`,
  `desktop_app`, `mobile_app`, `coding_tool:<harness>` and `api`.
- **allowance**: `offering.subscription.allowance.relative_to` (a plan ID),
  `.multiplier`, `.window` and `.tokens`. `tokens` is null unless the provider
  publishes it; it is never derived.

The vocabulary's `estate.plans` publishes each plan as this record: `price`,
`surfaces`, `coverage` (each entry as below) and `allowance`, with null for
anything unknown.

A result reached by plans lists them in `plans`, cheapest first. Each is a
plan route:

| Field | Meaning |
|---|---|
| `plan`, `name` | The plan's ID and name. |
| `surface` | The plan surface the access uses. |
| `price` | `amount`, `currency` and `period`: `currency` is `USD`, `period` `monthly` or `annual`. Null when not published. |
| `price_monthly_usd` | The price per month: an annual price divided by twelve. |
| `coverage` | Why the plan covers this model: `family` and `quote` (absent when `models_covered` names the model), `resolves_to`, every model the entry reaches, and the `rule` it resolved by. |
| `allowance` | `relative_to`, `multiplier`, `window` and `tokens`, each null unless published. |
| `break_even_tasks_per_month` | For `coding_tool`: the plan's monthly price divided by this result's pay-per-use `cost_per_task`. Above it the plan is cheaper, provided the tasks fit the allowance. Null when either number is unknown, and for any other access. |
| `basis` | How the break-even was computed or why there is none. It says when the allowance in tokens is not published. |

ModelSpec never turns a plan's price into a per-task cost.

With an estate, a held plan reaches its covered models only on a matching
surface, at a marginal cost of 0 inside its window; `exhausted` removes it
from `with_estate` only. A provider key reaches pay-per-use rows only for
`coding_tool` and `own_software`, a device only for `own_hardware`. A plan
row's `estate` adds `coverage`, as above. For `own_software`, `with_estate`
adds `warnings: [plan_excludes_own_software]` when a held plan's surfaces are
known and lack `api`.

### Subscription-only vendors (MODEL-205)

Some plans are sold by a vendor that serves no model pay-per-use: Cursor,
GitHub Copilot and Perplexity bundle several labs' models into their own tools.
Such a vendor is listed under `subscription_vendors` in
`registry/providers.yaml`, not among the providers, and:

- it may sell plans (`offerings/subscriptions/<vendor>.yaml`, plan IDs
  `cursor/subscription/pro`), whose surfaces are usually its own tool
  (`coding_tool:cursor`);
- it owns no metered offering, so it never appears as a pay-per-use route;
- `estate.providers` refuses it (`invalid_spec`, saying to name its plan in
  `estate.plans`); `estate.exhausted` accepts it, removing its plans.

Its plan reaches each covered model's own row (`offering.provider` null), as a
provider's plan reaches a covered model the provider does not sell. The route's
`break_even_tasks_per_month` is null there, and its `basis` says why: the
plan is not compared with any one provider's price, and each pay-per-use
offering of the model is a result of its own. The vocabulary names vendors in
`vendors`, apart from `providers`.

Nothing in the decision's shape changes, so MODEL-205 does not bump `contract_version`:
no response field is added, `estate.exhausted` accepts more IDs (compatible
under MODEL-59), and the vocabulary's `vendors` is compatible under its own
`vocabulary_version` 1. A provider kind was not added: `kind` in
`registry/providers.yaml` is closed, and a fifth value would widen it.

### Contract note

`access`, `plans`, `estate.coverage` and `with_estate.warnings` are new
optional fields, so this is a minor bump. `kind` (`chat_app`, `coding_tool`,
`own_software`, `own_hardware`) is a new closed value set on a new field; no
existing closed field widens. `EstateMark.cost_basis`, `EstateHold.kind` and
the error codes are unchanged, and `plan_excludes_own_software` is a warning,
which is an open set.

## The canonical spec hash

`spec_hash` identifies a spec independent of how it was written:

1. Parse the spec. Compact conditions become their structured form, set values
   are sorted, and omitted defaults are filled in.
2. Serialise to JSON with aliases (`in`, `not`, `class`), omitting absent
   optional fields. Write floats with an integral value as integers (`3.0`
   becomes `3`).
3. Sort keys, use no whitespace (`,` and `:` separators), and encode as UTF-8.
4. Hash with SHA-256 and write `sha256:<hex>`.

The hash is stable under key order, whitespace, and the choice between the
compact and YAML forms. It changes if any field changes, including an objective
qualifier and the order of `where`, which orders the funnel. It covers every
field, `explain` and `limit` included. An unqualified 1.1 objective keeps the
same canonical representation it had in 1.0.

## The decision

Responses may include the optional agent reporting block `reading` (MODEL-284).
Its `tied`, `not_applied`, `estimates` and `do_not_claim` lists are derived from
the answer, validation issues and applied objective. Empty lists are omitted;
the block is absent when none applies. `omitted` counts identifiers removed
to stay within 600 UTF-8 bytes of compact JSON; the complete tie remains in
`answer.members`, and rejected fields remain in `error.issues`. This is additive
in contract 2.12. Published contract 2.11 has no `reading` field.
See [the reading rules](cli-contract.md) for reporting ties, rejected
requirements and hardware estimates. The `tied` list names the engine's
best-band tie (`answer.members`). A `do_not_claim` line also names a tied
`with_estate.answer`. It changes no ranking; the updated page decoder ignores it.

```json decision
{
  "contract_version": "2.14",
  "decision_id": "dec_01J8ZK3Q7Y",
  "snapshot": "snap_2026-09-24T06:00Z",
  "signature_verified": true,
  "spec_hash": "sha256:9f2c1e4b7a0d3f6e8c5b2a1d4e7f0c3b6a9d2e5f8c1b4a7d0e3f6c9b2a5d8e1f",
  "explain": "summary",
  "status": "answered",
  "answer": {
    "kind": "tied",
    "members": ["anthropic/claude-opus-5-5", "openai/gpt-6-sol"],
    "basis": "probability bands: a model joins the leader when P(its score >= the leader's) >= 0.25 under the score posteriors; a weighted capability with an 80% interval wider than 2.8 is not enough evidence",
    "tie_breakers": {
      "cheapest": "openai/gpt-6-sol",
      "open_weights": "openai/gpt-6-sol",
      "most_independently_measured": "anthropic/claude-opus-5-5",
      "fastest": null
    },
    "deterministic_order": ["anthropic/claude-opus-5-5", "openai/gpt-6-sol"]
  },
  "bands": {
    "basis": "probability bands: a model joins the leader when P(its score >= the leader's) >= 0.25 under the score posteriors; a weighted capability with an 80% interval wider than 2.8 is not enough evidence",
    "band_probability": 0.25,
    "thin_interval_width": 2.8,
    "leader": "anthropic/claude-opus-5-5",
    "best": [
      {"model": "anthropic/claude-opus-5-5",
       "offering": {"model": "anthropic/claude-opus-5-5", "provider": "aws-bedrock",
                    "region": "us-east-1", "tier": "enterprise"},
       "score": 0.81, "score_interval": [0.62, 1.0], "p_best": 0.55, "p_beats_leader": null,
       "cost_per_task": 0.42,
       "estimates": [{"dimension": "software_engineering", "value": 1.32,
                      "interval": [0.35, 2.29], "benchmarks": 2, "direct_benchmarks": 2}]},
      {"model": "openai/gpt-6-sol",
       "offering": {"model": "openai/gpt-6-sol", "provider": "openai",
                    "region": "global", "tier": "standard"},
       "score": 0.74, "score_interval": [0.55, 0.93], "p_best": 0.31, "p_beats_leader": 0.31,
       "cost_per_task": 0.12,
       "estimates": [{"dimension": "software_engineering", "value": 1.02,
                      "interval": [0.05, 1.99], "benchmarks": 3, "direct_benchmarks": 3}]}
    ],
    "rest": [],
    "thin": [
      {"model": "qwen/qwen3-8-max-0902",
       "offering": {"model": "qwen/qwen3-8-max-0902", "provider": "alibaba-cloud",
                    "region": "global", "tier": "standard"},
       "score": 0.66, "score_interval": [0.24, 1.08], "p_best": 0.14, "p_beats_leader": 0.37,
       "cost_per_task": 0.1,
       "estimates": [{"dimension": "software_engineering", "value": 0.28,
                      "interval": [-1.72, 2.27], "benchmarks": 1, "direct_benchmarks": 0}]}
    ]
  },
  "blend": [
    {"dimension": "software_engineering", "weight": 0.6, "share": 0.6, "estimated": true,
     "leaders": ["anthropic/claude-opus-5-5"], "value": 1.32, "p_best": 0.55,
     "runner_up": "openai/gpt-6-sol", "p_runner_up": 0.31,
     "order": ["anthropic/claude-opus-5-5", "openai/gpt-6-sol"],
     "thin": ["qwen/qwen3-8-max-0902"]},
    {"dimension": "-offering.price.output", "weight": 0.4, "share": 0.4, "estimated": false,
     "leaders": ["qwen/qwen3-8-max-0902"], "value": 1.6, "p_best": null,
     "runner_up": null, "p_runner_up": null,
     "order": ["qwen/qwen3-8-max-0902", "openai/gpt-6-sol", "anthropic/claude-opus-5-5"],
     "thin": []}
  ],
  "results": [
    {
      "rank": 1,
      "model": "anthropic/claude-opus-5-5",
      "model_rank": 1,
      "cost_per_task": 0.42,
      "offering": {"model": "anthropic/claude-opus-5-5", "provider": "aws-bedrock",
                   "region": "us-east-1", "tier": "enterprise"},
      "harness": "claude-code@2.1",
      "effort": "high",
      "evidence": [
        {"domain": "software_engineering", "items": [
          {"benchmark": "multi_swe_bench", "version": "1.0", "sub_category": "rust",
           "value": 48.2, "unit": "percent", "measured_by": "independent",
           "effort": "default", "date": "2026-09-20", "date_type": "observed",
           "source": "https://example.org/leaderboard", "directness": "direct"}
        ]}
      ],
      "estimates": null,
      "p_best": null,
      "top3_stability": null,
      "soft_penalty": 0.0,
      "contributions": [
        {"dimension": "software_engineering", "weight": 0.6, "value": 0.81,
         "normalisation": "min-max over the feasible set", "evidence": []}
      ],
      "warnings": ["provisional_released_2_days_ago"]
    }
  ],
  "by_model": [
    {"model": "anthropic/claude-opus-5-5", "status": "ranked", "rank": 1, "cost_per_task": 0.42,
     "offerings": [
       {"offering": {"model": "anthropic/claude-opus-5-5", "provider": "aws-bedrock",
                     "region": "us-east-1", "tier": "enterprise"},
        "status": "ranked", "rank": 1, "cost_per_task": 0.42, "unknown": [], "reason": null}
     ]},
    {"model": "google/gemini-3-8-pro", "status": "may_qualify", "rank": null, "cost_per_task": null,
     "offerings": [
       {"offering": {"model": "google/gemini-3-8-pro"}, "status": "may_qualify", "rank": null,
        "cost_per_task": null, "unknown": ["offering.data.trains_on_customer_data"], "reason": null}
     ]}
  ],
  "may_qualify": [
    {"model": "google/gemini-3-8-pro", "offering": null,
     "unknown": ["offering.data.trains_on_customer_data"]}
  ],
  "eliminated": {
    "funnel": [
      {"condition": "offering.price.input in [0.5, 3.0]", "before": 212, "after": 64,
       "may_qualify": 3, "models_before": 106, "models_after": 38,
       "offerings_before": 180, "offerings_after": 52,
       "models_may_qualify": 2, "offerings_may_qualify": 3}
    ],
    "models": [],
    "model_groups": []
  },
  "truncated": {"offerings": 0, "models": 0},
  "constraint_costs": [
    {"condition": "origin.lab_jurisdiction in {US}", "admits": 12, "gain": {"software_engineering": 0.06}}
  ],
  "tipping_points": [
    {"description": "rank 1 holds unless the cost weight exceeds 0.35",
     "dimension": "-offering.price.output", "threshold": 0.35, "new_top": "openai/gpt-6-sol"}
  ],
  "relax": [],
  "relax_to": [],
  "warnings": [],
  "out_of_lineup": 1334,
  "feedback": {
    "endpoint": "https://api.modelspec.dev/v1/feedback",
    "method": "POST",
    "request_schema": "https://modelspec.dev/api/feedback/v1.schema.json",
    "ratings": ["reliable", "unreliable", "trustworthy", "untrustworthy", "confusing"],
    "cli": "modelspec feedback <decision_id> --rating <rating>"
  }
}
```

| Field | Meaning |
|---|---|
| `contract_version` | `"2.14"`. |
| `decision_id` | `dec_<id>`. Cite it in outcome records. |
| `snapshot` | The snapshot ID the decision was computed from. Never `latest`. |
| `signature_verified` | `true` when this process verified either the pinned Ed25519 signature or the private Worker HMAC. |
| `benchmark_exclusions` | Present for `summary` and `full` decisions with a non-empty `exclude_benchmarks` set. `benchmarks` lists the removed IDs. Each `estimate_changes` row names a result `model` and `domain`, the `before` and `after` estimate and interval, and the sourced `removed_drivers`. An estimate is null when the remaining evidence cannot fit it. |
| `spec_hash` | The canonical spec hash. |
| `explain` | The explanation level used. |
| `status` | `answered`, `partial` or `no_feasible`; see below. |
| `answer` | The model-level answer for a scalar objective, or null when the objective has no scalar order, no result, or no ranked model with enough evidence to lead. See below. |
| `bands` | The ranked models in three bands: `best`, `rest` and `thin` (not enough evidence yet). Absent when `answer` has no scalar order to band. See below. Added in 2.7. |
| `blend` | What a scalar objective mixes: each weighted dimension, heaviest first, its `share` of the weights and who leads on it alone. Absent with `bands`. See below. Added in 2.7. |
| `results` | Ranked results, `rank` 1 to n in order. Empty only when `no_feasible`. |
| `by_model` | The decision grouped by model, best first. See below. |
| `may_qualify` | Models not ranked because a condition could not be evaluated, or because they pass every condition but have no value for the objective. Each lists the facets it is `unknown` on (for a missing objective value, the objective's facet or benchmark), and an `offering` when the unknown is offering-level. A model is never ranked on an unknown objective value. A model that passed every hard condition and has no estimate for a domain objective is listed here on that objective. It is not dropped. |
| `eliminated` | Candidates that failed a condition or were Pareto-dominated. The `funnel` reports each condition in order, the candidate count `before` and `after` it, and how many it moved to `may_qualify`. Each step also reports `models_before`, `models_after`, `offerings_before` and `offerings_after`. The `models_may_qualify` and `offerings_may_qualify` counts report what that step moved aside because a capability fact was unknown. The candidate-grained `models` list remains for compatibility. The `model_groups` list groups eliminations by model, with a nullable `model_elimination` for a bare model row and the model's `offerings` beneath it. Each offering keeps its `condition`, `value`, `values`, `unit`, `records` and `formula`. A qualifying candidate omitted by `limit` is never an elimination. |
| `truncated` | Qualifying candidates omitted only because of `limit`. `offerings` counts omitted offering rows. `models` counts models with no row in `results`; a model with one returned offering and another omitted offering is not counted as an omitted model. Both counts are always present and are zero when the complete qualifying result set was returned. |
| `constraint_costs` | For each condition: the `condition`, how many models relaxing it `admits`, and the `gain` on each objective dimension. Gains on refinement dimensions are in `refinement_gains`, each a `dimension`, `refinement` and `gain`; absent when there are none (2.4). |
| `tipping_points` | The objective changes that would change the top result: a `description`, and where they apply, the `dimension`, the `threshold` and the `new_top` model. A refinement weight's point also names its `refinement` (2.4). |
| `relax` | For `no_feasible` only: the fewest conditions whose removal gives a feasible answer. Never the model class or a condition on a requested capability domain, which would change the question; among equally few, numeric caps and floors first. When a reach is already in force (`access`, or an estate), this is the condition that emptied that lineup, not a relaxation computed as if the reach were absent. When models passed every hard condition and none has an objective value, it names that objective. The text does not name an internal ticket. |
| `relax_to` | For `no_feasible` only (1.5): for each numeric cap or floor, the smallest change that admits a model. Each names the spec's `condition`, the `relaxed` condition (same facet and direction, at the nearest value an excluded candidate has), the `facet`, that `value`, its `unit`, and how many models it `admits`. |
| `relax_task_tokens` | For `no_feasible` only, and absent otherwise (2.14): the spec gave no `task_tokens`, `relax` is a single `offering.cost_per_task` cap, and that cap fails only at the default task size. Names the cap as `condition`, the `default` task size cost was priced at (40,000 input, 4,000 output tokens), `admits_at` (the largest task at the default's input-to-output ratio that a model meets the cap at, strictly under a strict cap) and a `message`. Set `task_tokens` to the real task's size rather than copying `admits_at`. Kept in bounded answers. |
| `warnings` | Codes about the decision as a whole. |
| `out_of_lineup` | How many active catalogue models the snapshot leaves outside its lineup, and so outside this decision. `0` when the snapshot was built without a premier list. |
| `feedback` | Where to say whether this answer held up: send the `method` (`POST`) to the `endpoint`, with a body that follows `request_schema` and a rating from `ratings` (`reliable`, `unreliable`, `trustworthy`, `untrustworthy`, `confusing`) and this `decision_id`, or run the `cli` line. No key. The same on every decision. See [`feedback-api.md`](feedback-api.md). Added in 2.10. |
| `reading` | Optional reporting limits: `tied` names the engine's best-band tie (`answer.members`), `not_applied` names requirements not applied, `estimates` names estimated fields, and `do_not_claim` lists claims to avoid, including a tied `with_estate.answer`. `omitted` counts identifiers removed to meet the 600-byte compact UTF-8 limit. Added in 2.12. |
| `coverage` | Optional typed scope explanation with `kind: "out_of_coverage"`, a message, the snapshot date, covered classes and model counts, covered domains, and the requested classes or domains that the board cannot decide. Links to `https://modelspec.dev/api/coverage.json`. Also retained in bounded answers and added to applicable `invalid_spec` refusals. Existing statuses and error codes remain unchanged. Added in 2.13. |

**`status`:**

- `answered`: the spec was answered in full.
- `partial`: results were returned, but part of the spec could not be
  addressed, for example a requested capability with no evidence for any
  result. `warnings` says which part.
- `no_feasible`: no candidate satisfies the hard conditions, or none that does
  has a value for the objective. `results` is empty and `relax` names the
  fewest conditions to relax, or the reason no result could be ranked. Models
  that passed every hard condition and have no objective value stay in
  `may_qualify` and `by_model`.

**`coverage` (`CoverageRefusal`):** `kind` is `out_of_coverage`. `message`
explains the scope limit; `url` links to the keyless generated summary.
`snapshot` and `as_of` identify the snapshot, with a null date only when the
index has no date. `classes` contains `CoveredClass` rows (`id`, `models`),
listed alphabetically. `domains` lists domains with stored estimates for
active models. `requested_classes` and `requested_domains` name the requested
scope that the board cannot decide. Catalogue presence alone does not establish
decision coverage. The field adds an explanation to the existing result;
it never orders classes or changes ranking, status or error code.

**The lineup.** A decision ranges over the snapshot's lineup. A snapshot built
from a premier list (slice 1: `premier/slice-1.yaml`) holds only the premier
models and their offerings, plus the live archive of retired models. Retired
models enter a decision only when a condition asks for lifecycle `retired`.
Every other catalogue model is left out and counted in `out_of_lineup`; it is
never listed as a candidate or in `may_qualify`.

A model with offerings is represented by those offerings. A model without an
offering can rank only when its verified `model.weights_openness` is `open_weights`.
Closed or unknown weights establish no self-host route. The engine eliminates
those rows using `model.weights_openness = open_weights unknown(fail)` before
the user's conditions, including when the user permits unknown values. The same
elimination applies to a sold model's bare row when a self-host reach holds it
(`own_hardware`, or a device). An offering does not make closed or unknown
weights a self-host route.

### The answer

`answer` is the evidence-supported model-level conclusion. Each model is
represented by its best offering under the spec's objective. A model's own
offerings never compete with one another in this block.

For a scalar objective, each candidate has a weighted score and a
`score_interval`. Both are in feasible-set normalised units, which are
dimensionless. The engine applies the same feasible-set affine transform to
interval bounds that it uses for the point estimate. It does not clamp
transformed bounds to 0 through 1. A zero span, one scored value or several
equal values, maps to the same constant the reference ranker uses: 1 when the
objective maximises the dimension and 0 when it minimises it. When the raw
estimate has a width, that candidate's own raw interval width is the span, so
the interval stays dimensionless and is not a point. An exact value, such as
cost with no published interval, contributes that constant as a point. A
capability estimate contributes its 80% interval. A measured benchmark term
contributes its source-published interval. The weighted interval is the sum of
each transformed interval times its objective weight, less the exact soft
penalty.

The answer's `members` are the `best` band (below): the leader, and every model
with enough evidence whose score is at least the leader's with probability 0.25
or more. Before 2.7 a model was a member when its interval merely overlapped
the leader's. That rule tied models the evidence ranks well apart, because
overlapping 80% intervals can still leave 95% or more of the probability on one
side, and it tied every thin-evidence model, whose interval overlaps
everything.

| Field | Meaning |
|---|---|
| `kind` | `separated` when the best band holds only the leader, otherwise `tied`. |
| `members` | The best band's model IDs, in point-score order. A separated answer contains only its leader. |
| `leader` | Present only for `separated`, and equal to its sole member. A tied answer cannot carry this field. |
| `basis` | The band rule and interval level used. |
| `tie_breakers` | Four model IDs or nulls, computed only for a tied answer. `cheapest` minimises exact cost per task, `fastest` maximises offering throughput, `open_weights` names the sole open-weights member when there is one, and `most_independently_measured` counts admitted measurements from independent measurers. A non-unique or unknown value is null. |
| `deterministic_order` | The members ordered by point estimate, then exact cost, then model ID. This lets an agent process the group repeatably. It is not evidence that the first member is better. |

A `separated` answer carries all four `tie_breakers` as null. A `tied` answer
contains at least two unique `members`, and each non-null tie-breaker names one
of them. `answer` is null when every ranked model is thin: then no model has
the evidence to lead, and `bands.thin` lists them all.

### The bands

`bands` sorts every ranked model, through its best offering, into exactly one
of three bands (MODEL-206).

Each model's weighted score is read as a normal distribution: the point score,
with variance from its capability terms (each estimate's standard deviation,
through the objective's transform and weight) and from any measured term's
source-published interval, read as a 95% interval. Exact terms add none.
Models are independent. `p_beats_leader` is then P(this score ≥ the leader's),
computed in closed form: the limit of comparing the posterior draws pairwise,
without their sampling error.

- **`best`, best for your weights.** The leader is the best point score among
  models with enough evidence. A model with enough evidence joins it when
  `p_beats_leader` ≥ `band_probability` (0.25): the leader is then ahead with
  at most 75% probability. Ordered by `p_best`, then score.
- **`rest`.** The other models with enough evidence, in score order, each with
  its `p_beats_leader`.
- **`thin`, not enough evidence yet.** A model is thin when any weighted
  capability's 80% interval is wider than `thin_interval_width` (2.8 on the
  capability scale). One fresh direct benchmark gives an interval about 2.0
  wide; a model measured only on three proxy benchmarks, or on one direct
  benchmark more than about fourteen months old, is wider than 2.8; the prior
  alone is 5.1. A thin model is never in the leader's band, whatever its point
  score. In score order.

The result warning `not_separable` is unchanged by the bands: it still marks a
row whose interval overlaps any other model's, a weaker test. A separated
leader can carry it. Read the bands for the answer, and the warning as a hint
that intervals touch.

The width threshold is on the capability scale, not on `score_interval`: a
score interval is in feasible-set normalised units, which change with the
lineup, so a fixed width there would mean different evidence in different
decisions.

| Field | Meaning |
|---|---|
| `basis` | The rule, as text. The same string as `answer.basis`. |
| `band_probability` | The P(score ≥ leader's) a model needs to join the best band. |
| `thin_interval_width` | The 80% capability interval width above which a model is thin. |
| `leader` | The best point score among models with enough evidence, or null when every model is thin. |
| `best` | The leader's band, ordered by `p_best`. |
| `rest` | Other models with enough evidence, in score order. |
| `thin` | Models without enough evidence yet, in score order. |

Each band entry:

| Field | Meaning |
|---|---|
| `model` | The model ID. |
| `offering` | The model's best offering under the objective. |
| `score` | The weighted score, rounded to 6 places. |
| `score_interval` | The weighted interval, rounded to 6 places. |
| `p_best` | The result's `p_best` for this model: its probability of being best among every ranked model, thin ones included. It resamples the capability posteriors only, so a measured benchmark term's published interval widens `p_beats_leader` but not `p_best`. Null when the objective has no capability posterior. |
| `p_beats_leader` | P(this score ≥ the leader's), to 4 places. Null for the leader, and for every entry when there is no leader. |
| `cost_per_task` | The offering's cost per task, as in `results`. |
| `estimates` | One per weighted capability, in objective order: the signed weight key as `dimension`, the estimate's `value`, its 80% `interval`, `benchmarks`, the distinct fitted benchmarks the model is measured on for it, and `direct_benchmarks`, how many of those are tagged direct for it. |

The capability intervals were recalibrated in 2.7: see
[`research/capability-interval-calibration.md`](research/capability-interval-calibration.md).
Before, they covered held-out benchmark results 94% of the time where 80% was
claimed.

### The blend

A weighted score mixes unlike things, so a band on the mix is only one reading
of the question. `blend` names the mix and gives the order on each dimension
alone: "on your 60/40 mix of software engineering and cost …, and on software
engineering alone, … leads".

| Field | Meaning |
|---|---|
| `dimension` | The signed weight key. |
| `weight` | The weight as given. |
| `share` | `weight` over the sum of the objective's weights, to 4 places. |
| `estimated` | `true` for a capability estimate, `false` for an exact value (cost, a fact, a preference, a measured benchmark). |
| `leaders` | Who leads on this dimension alone. For a capability, the best point estimate among models with enough evidence on it. For an exact dimension, every model sharing the best value. |
| `value` | The leaders' value on this dimension in its own unit: a capability estimate or a raw value such as dollars per task. |
| `p_best` | Capability only: P(the leader is best on this dimension alone) among models with enough evidence, from the same deterministic posterior draws as `p_best` on a result. |
| `runner_up` | Capability only: the second model by point estimate among models with enough evidence. |
| `p_runner_up` | Capability only: P(the runner-up's estimate ≥ the leader's), to 4 places. |
| `order` | Models with enough evidence, best first on this dimension alone. Each model is read at its best ranked offering for this dimension. |
| `thin` | Models whose estimate on this dimension is thin, by model ID. |

### The model view

`by_model` answers "which models, and through which offerings?" once, so the
page, the CLI and agents cannot disagree. It has one `ModelRow` per model: its
`model`, its `status`, its `rank` (the result's `model_rank`, ranked models
only), its `cost_per_task` (its best ranked offering's) and its `offerings`.

`status` is `ranked` when any of the model's offerings is ranked,
`may_qualify` when none is ranked but one is unknown on a facet, and
`eliminated` otherwise. Rows run ranked (by `rank`), then `may_qualify`, then
`eliminated` (by model ID). Each `ModelOffering` carries its `offering`, the
strongest `status` the decision gives it, its `rank` in `results` (ranked only),
its `cost_per_task`, the facets it is `unknown` on (may-qualify only) and
`reason`. `reason` is the Must an eliminated offering failed, and also the
sentence for a may-qualify offering that is unknown on `offering.region`
because its region name guarantees no country. Otherwise it is null.

Eliminated models are listed only when the explanation carries them, at `full`.
At `none` and `summary`, `by_model` holds ranked and may-qualify models only.
`cost_per_task` is null when the offering has no priced task. The field is
always present, and is empty when `results` and `may_qualify` are.

### A result

| Field | Meaning |
|---|---|
| `rank` | 1-based position. |
| `model` | The offering's model ID, flat, so an agent need not open `offering`. Always equal to `offering.model`. |
| `model_rank` | 1-based position among models: the model's best offering's place. Ties are expressed only by `answer`. |
| `cost_per_task` | The offering's exact cost of one task in USD, or null when it cannot be priced. Filled at every explanation level. |
| `offering` | `model`, and when the result is an offering, its `provider`, `region` and `tier`. |
| `harness` | The harness the evidence and estimate apply to, or null. |
| `effort` | The effort setting the evidence and estimate apply to, or null. |
| `evidence` | For each requested `domain`, the verified evidence `items`. |
| `estimates` | Capability estimates per `domain`, each a `value` and an 80% `interval` `[low, high]`, with the `harness` and `effort` they apply to. Null when the snapshot has no fitted estimate. |
| `refinement_estimates` | One per refinement key in `optimize.weights`, absent otherwise: the `key`, its parent `domain` (or `any`), the `refinement`, a `value` and an 80% `interval`, and `evidence_count`, the refinement-tagged measurements behind the adjustment. `evidence_count` 0 means no refinement evidence: the value is the parent's estimate and the interval is wider. Added in 2.4. |
| `p_best` | The probability this model is best among the feasible models. For a weighted objective, the engine resamples each capability posterior, applies the objective's affine transform and weights, and keeps exact facets fixed. Null when the objective has no capability posterior. |
| `top3_stability` | The share of those deterministic posterior resamples in which the model stays in the top three. Null when `p_best` is null. |
| `soft_penalty` | The total penalty from violated soft conditions. |
| `contributions` | Per objective `dimension`: its `weight`, normalised `value`, the `normalisation` used, and the `evidence` behind it. A boolean or enum term also carries `preferred_value` and `preference_status`. A refinement term's `dimension` is its signed parent domain, and `refinement` names the refinement (2.4). |
| `warnings` | Codes about this result. |

**An evidence item** carries `benchmark`, `version`, `sub_category`, `value`,
`unit`, `n` (a sample or vote count), `interval` (the source-published
measurement interval, or null), `quality_flags`, `measured_by`, `effort`, `harness`,
`harness_unregistered`, `date`, `date_type`, `source` (the URL it was read
from), `source_snapshot` (the content hash of the retained copy), and
`directness`. Evidence used in a capability estimate also carries its
directness `loading`, its `estimate_weight`, and its age-based
`recency_weight`. Those three fields are null for unblended evidence.

- `measured_by` is one of `benchmark_author`, `independent`,
  `provider_self_report`, `modelspec`, `outcome_protocol`.
- `date_type` is `observed` (a live leaderboard, dated by when it was read) or
  `published` (a paper or launch post, dated by publication).
- `directness` is `direct` or `proxy`, relative to the requested domain.
- `harness` is a registered `name@major.minor` ID or null. When the evidence
  names a harness the registry does not know, `harness` is null and
  `harness_unregistered` is `true` (the registry reports such a harness as
  `unregistered`, never as free text). Otherwise `harness_unregistered` is
  `false`.

Only verified evidence reaches a decision; quarantined values never do.
Evidence with a `deprecated` or `contamination_warning` quality flag remains
visible in provenance but does not count as the direct answer to an objective.
When every fitted benchmark for an estimate is tagged `proxy`, the result's
`warnings` includes `proxy_evidence_only`. Its contribution formula also names
the estimate as proxy-only.

### Explanation levels

| `explain` | Populated |
|---|---|
| `none` | `results` without `contributions`; `may_qualify`. For high-rate automated calls. |
| `summary` | Adds `contributions`, the `funnel`, `constraint_costs`, `tipping_points` and, when requested, `benchmark_exclusions`. |
| `full` | Adds `eliminated.models`, `eliminated.model_groups`, `top` candidates with their relevant values, `chart`, `number_origins`, the `sources` they cite and, when requested, `benchmark_exclusions`. |

The fields are always present. At a lower level, the lists it does not populate
are empty.

### Bounded HTTP responses for agents (MODEL-293)

`POST /v1/decide` also accepts two optional response controls alongside the
spec. These controls are HTTP-only; the offline Spec and its canonical hash
are unchanged. The existing `limit` remains 1–500, default 20. It limits ranked
offering rows, not unique models, and never changes the full `answer.members`.

- `fields`: an array of 1–16 Result field names. The names are `rank`, `model`,
  `model_rank`, `offering`, `cost_per_task`, `harness`, `effort`, `evidence`,
  `estimates`, `refinement_estimates`, `p_best`, `top3_stability`, `soft_penalty`,
  `contributions`, `warnings` and `plans`. Unknown names and invalid shapes
  return HTTP 400 `invalid_spec`. `rank`, `model`, `offering` and row `warnings`
  are always included. Unselected fields are absent only in the separate
  `ProjectedResult` type. The complete `Result` type keeps its required fields.
- `evidence_for`: one `lab/model` ID in the snapshot's active lineup. Resend
  the same structured spec to inspect that model, even outside `limit`, or
  when it was eliminated. A missing model returns HTTP 400 `invalid_spec`.
  `model_evidence` contains its `model`, `status`, best ranked `offering` or a
  representative offering for an unranked model, overall offering `rank` or
  null, domain `evidence`, objective `contributions`, `unknown` facets and
  elimination `reasons` and model-row `warnings`. It contains evidence for this model only. The ranking
  and answer still use the full feasible set; this is not a model filter.

#### A separate representation, versioned on its own

Either non-null control opts into `BoundedDecision`, the **bounded
representation, version 1.0**. It is not a 2.x minor version. A bounded body
omits lists that every 2.x Decision always carries (`by_model`, `eliminated`,
`number_origins` and the other explanation sections), and its rows omit fields
a 2.x `Result` requires. Under the [versioning rule](#versioning-model-59) a
field that may be absent is a widening, so labelling such a body as a 2.x
contract would need a major bump. It is a different representation instead:

- `representation` is always `"bounded"`. Branch on it first.
- `bounded_version` is the bounded representation's own version, `"1.0"`. It
  follows the same MODEL-59 rule on its own: widening any bounded field bumps
  its major.
- `projects_contract` names the complete contract the body is projected from,
  currently `"2.14"`. Every field the bounded body does carry has that
  contract's type and meaning.
- A bounded body has **no** `contract_version`. A 2.x decoder that requires
  `contract_version` refuses it rather than misreading it as a complete
  Decision.

Requests with only `limit`, or `fields: null`, receive complete contract 2.14
responses. The decide page never sends `fields` or `evidence_for`, so its
decoder never sees a bounded body and
needs no change.

A bounded response retains the complete `answer`, `warnings`, `reading` when
applicable, `with_estate` when applicable, status, identity, feedback pointer,
`truncated`, `out_of_lineup`, `relax`, `relax_to` and `relax_task_tokens` when present. It projects ranked
`results` and shows at most 10 `may_qualify` rows. It adds required
`explanation` with `not_applied`, explicit per-section `omitted` counts, an
optional `fetch` string and a `note` that omitted data is incomplete. `fetch`
is present when `omitted` is non-empty and absent otherwise. It names the
follow-up: resend the spec with `evidence_for` set to the top model, narrow
`fields`, lower `limit`, or POST `/v1/decide` without `fields` for the complete
Decision. Ties and reporting limits cannot be
projected away. Counts for omitted ancillary explanations do not imply an
elimination or a missing fact. Use a complete response to inspect those
sections. `explain` still controls which details the engine computes; selecting
`contributions` with `explain: none` returns an empty list.

The bounded body stays within the agent byte budget. That budget is 16,384
compact UTF-8 bytes for the MCP text as a whole (the origin envelope
`{"origin":"https://api.modelspec.dev/v1/decide","status":200,"body":…}` plus
the one-line `decisionSummary`). `RESPONSE_BYTES` is 16,384 minus that
envelope and minus the longest summary line for a 61-byte model id, the
longest id in the catalogue. When a projection is larger, whole records are removed until the compact body
fits, and `explanation.fetch` is included in that count. The order is: result
rows that are neither the top result nor an answer member, then `may_qualify`
rows, then any remaining result row except the top, then `with_estate`, then
`reading` and `relax_task_tokens`, then one heavy field of the top result at a
time (`evidence`, `contributions`, `estimates`, `refinement_estimates`,
`plans`), then any other field on that row besides rank, model, offering and
warnings. A heavy field is removed whole. The top result's explanation is
removed only after the earlier records are gone. Provenance inside a kept
record stays intact, and no value is replaced with null. Each removal
increments `explanation.omitted`. `answer`, `status`, `warnings`, `coverage`,
`summary_for_user`, `must_mention`, and the top result's rank, model, offering
and warnings remain. If those essentials still exceed the budget, the call
returns HTTP 400 `invalid_spec` and the issue says how to request the complete
Decision. The
one-model drill-down keeps its own 7,400-byte cap, and that cap includes `fetch`.

Drill-down returns no ranked result rows or may-qualify rows; their omission
counts are explicit, and `model_evidence` is the one-model detail. A
summariser reads the answer from `answer.members` and the one model from
`model_evidence.model`, `status` and `rank`, never from the empty `results`. The complete
answer remains unchanged. The compact UTF-8 body is capped at 7,400 bytes,
leaving room for the MCP envelope and summary under 2,000 estimated tokens.
If needed, whole evidence records or contributions are omitted and counted in
`explanation.omitted`. Provenance fields are never cut off. If reporting
necessities alone exceed this budget, the call returns HTTP 400 `invalid_spec`
with guidance to narrow the spec. An omission is not evidence of absence.
Drill-down cites retained verification records even at `explain: none`. A
snapshot built before provenance retention cannot cite them, so `evidence_for`
against it returns HTTP 503 `explanation_unavailable`; retry without
`evidence_for`. Only a request that sends `evidence_for` can receive this code,
so it belongs to the bounded representation: its body carries `representation`,
`bounded_version` and `projects_contract` instead of a `contract_version`, and
the 2.x decision error enum is unchanged.

No decision store is added. `decision_id` remains a citation, not a lookup
handle. Pin `snapshot` before the first call for reproducibility and resend the
same spec plus `evidence_for`. A `latest` call can observe a newer snapshot.
Changing `snapshot`, `limit` or `explain` changes the existing canonical spec
hash; adding `fields` or `evidence_for` does not. For example:

```json
{"spec_version":1,"snapshot":"snap_example","optimize":{"max":"software_engineering"},"explain":"none","limit":10,"evidence_for":"lab/model"}
```

The MCP decide tool returns a bounded answer by default. When `explain` is
unset or `none`, it sends `explain: none`, `limit: 10` and `fields` of
`model_rank`, `cost_per_task`, `estimates` and `p_best`. When the caller sets
`explain` to `summary` or `full`, it sends those fields plus `contributions`
and `evidence`, still inside the same byte budget. A caller-supplied `fields`
value, including null, replaces that list. Null `fields` asks the Worker for
the complete Decision. If that body, with the MCP envelope and summary, exceeds
16,384 bytes, the tool returns a short bounded notice instead of the raw body.
The notice keeps `status`, `answer`, `warnings`, `coverage`,
`summary_for_user`, `must_mention` and the top result, and
`explanation.fetch` tells the caller how to request the rest. The tool does
not call the Worker a second time. HTTP defaults remain unchanged: a request
with no `fields` and no `evidence_for` is still the complete Decision.

Size tests use the repository's public premier snapshot built as of
2026-10-02, a software-engineering objective and `limit: 10`. The unit is
compact UTF-8 bytes / 4, not a tokenizer count. The measured baselines and
regression ceilings are:

| Representation | Measured estimated tokens | Test ceiling |
|---|---:|---:|
| Complete `none` | 6,743 | 8,000 |
| Complete `summary` | 24,107 | 28,000 |
| Complete `full` | 69,991 | 80,000 |
| MCP default projection | about 1,900 with envelope and summary | 3,000 |
| One-model drill-down | about 1,600 with envelope and summary | 2,000 |

The agent path (the MCP text, and the bounded body it requests) stays within
16,384 UTF-8 bytes. The complete-decision ceilings above apply to responses
with no `fields` and no `evidence_for`.

There is no `evidence` explain level in this contract; drill-down uses
`evidence_for`. These fixture measurements differ from the ticket's measured
production response because the fixture and row limit differ. Tests cover all
three current explanation levels. Regenerate the MCP public fixture with
`python -m qa.decide_budget`; pytest also checks fresh public Worker responses against these budgets.

#### Bounded representation change log

- **bounded 1.0 — MODEL-293:** First version. HTTP-only `fields` and
  `evidence_for` request controls; a `BoundedDecision` body with
  `representation`, `bounded_version` and `projects_contract`, projected rows,
  one-model provenance in `model_evidence` and explicit omission counts in
  `explanation`. Projects contract 2.12. Complete decisions stay 2.12 and are
  unchanged; `limit` was already supported and is unchanged. Adds the
  bounded `explanation_unavailable` refusal, reachable only with
  `evidence_for`; the 2.x error enum is unchanged.
- **bounded 1.0 — MODEL-334:** Adds optional `explanation.fetch`. No existing
  field changes range, and `bounded_version` stays `1.0`. A bounded body over
  the agent budget drops whole tail records, leaving the top result's
  explanation until nothing else will fit, and records each removal in
  `explanation.omitted`. `fetch` says how to request the removed records.
  Essentials that still exceed the budget are HTTP 400 `invalid_spec`.
  MCP `explain` of `summary` or `full` keeps the bounded projection.
- **bounded 1.0 — MODEL-339:** Adds optional `summary_for_user` and
  `must_mention`. No existing field changes range, and `bounded_version` stays
  `1.0`. Both are written from the full Decision before trimming, and neither
  is removed to fit the 16,384-byte MCP text. `summary_for_user` is one
  paragraph for the end user. `must_mention` lists the facts a report of that
  answer carries, at most 10 items.

## The library and the CLI

```python
from decision import decide, parse_spec
from decision.registry import facet

spec = parse_spec(open("spec.yaml").read(), facets=facet)   # raises SpecError
decision = decide(spec, snapshot)                             # one loaded decision snapshot
```

`parse_spec(raw, facets=...)` takes YAML text or a mapping. `facets=None`
checks structure only. A `SpecError` lists every issue; each names the `path`
(`where[1].any[0]`), the `condition` as written, the `field` (the facet or spec
field) and the `reason`.

```
modelspec decide SPEC.yaml [--explain none|summary|full] [--check] [--json]
modelspec decide SPEC.yaml --compare-to SNAPSHOT_ID [--json]
```

`--explain` overrides the spec's `explain`. By default the command reads the
decision snapshot cached by `modelspec snapshot fetch`. Pass `--snapshot-file
SNAPSHOT.gz` or set `MODELSPEC_DECISION_SNAPSHOT` to override it. No network
request is made. `--explain full --html out.html` writes a self-contained report
with an inline SVG contribution chart, light and dark styles, and source links.
The command emits the decision as JSON. Invalid specs, unavailable snapshots,
and unresolved explanation provenance exit **1** with a structured error when
`--json` is set. Successful decisions, including `no_feasible`, exit **0**.

`--check` runs the same validation `decide` runs and stops before filtering and
ranking: it parses the spec and resolves it against the same snapshot and
registry, through the engine's `validate()`, which `run_decision` also calls.
A spec that `--check` accepts is one `decide` accepts, and a spec it rejects,
`decide` rejects with the same error code (`invalid_spec` for a parse error,
`decision_failed` for a resolve error such as an unloaded profile). The cached
vocabulary is advisory. It adds "did you mean" suggestions to an unknown facet
or benchmark, and it warns, without failing, when the spec names something the
vocabulary lacks but the engine accepts: a benchmark with no verified evidence
in this snapshot, a parameterized facet family, an unknown provider value, or a
capability domain with no coverage. Human output is `ok` plus one line with the
Must count, Prefer count, and snapshot pin. JSON success includes `ok`,
`summary`, `warnings`, and the cached `snapshot`. A snapshot pin that differs
from the cached vocabulary produces a warning, not a failure.

`--compare-to` is additive CLI behavior. It accepts a cached decision snapshot
ID, `previous`, or a path to a snapshot `.gz`; it runs the real decision engine
against both snapshots and groups the difference by model. The comparison
ignores a `snapshot` pin in the spec. Internally it requests full explanation
data so departures can name the failed Must and changed values can retain their
record IDs, but it does not change ordinary decision output or the decision
contract. JSON comparison output uses the CLI envelope documented in
`cli-contract.md`; unchanged comparisons still exit 0.

The hosted equivalent is `POST /v1/compare` with a body containing `spec` and
`compare_to`. It runs the same comparison function after verifying both signed
Snapshots. The current static origin does not publish retained Snapshot files,
so the endpoint reports `comparison_snapshot_unavailable` until that separate
hosting work ships. See [`decide-api.md`](decide-api.md#comparing-snapshots).

### Explanation provenance (MODEL-145)

These additive response fields were introduced without changing the 1.0
contract version. Version 1.1 retains them.

- Contributions add `raw_value`, `unit`, and `records`. The existing `value`
  remains the feasible-set normalised value, never a capability estimate.
  `normalisation` states the observed minimum, maximum and direction.
- Evidence adds `requested_domain` to make contribution directness explicit, and `record_id`, resolving to the snapshot's admitted evidence and
  its winning verification record. Source dates and measurement qualifiers are
  preserved. Snapshot date type `evaluated` is exposed as contract `observed`;
  `independent_evaluator` is exposed as `independent`.
- `near_misses` lists models whose best offering fails exactly one hard
  condition while passing the others. A bare model row is never a near miss
  for an offering facet. Each includes `offering`, `condition`, `facet`, `value`,
  `distance`, `unit` and `records`. Distance is to the boundary; a strict
  inequality can have zero distance. Compound, categorical and unknown distances
  remain null rather than inventing a conversion or epsilon.
- Constraint costs add `units` and `records`. Each `gain` is the best raw
  objective value after relaxing that condition minus the current best, per
  dimension. A negative gain on a minimised dimension is an improvement. With
  no comparable values the gain mapping is empty. Profile rules are included.
- Per-model eliminations add `offering`, `unit` and `records`, preserving
  offering identity when a model has several providers or tiers. Eliminations
  and near misses add `values` for conditions with multiple measurements; the
  scalar `value` remains null in that case.
- `top` contains up to 20 optimised candidates independently of the result
  limit, with `offering`, `facts`, `contributions` and domain `evidence`.
  From 1.4 it is compact (MODEL-163):
  - `facts` are the known facets the spec names, in its conditions (profile
    rules included) and its objective, plus a fixed display set: context
    window, class, lifecycle, weights openness, release date, commercial-use
    licence, lab jurisdiction, input and output price, `$ per task`,
    throughput, time to first token and data retention. Not every value the
    candidate holds.
  - Shown facts carry `facet`, `value`, `unit`, and `record_id`; a computed
    fact (1.3) has no `record_id` and carries `records` and `formula` instead.
    Each carries `source_ids` (1.4): its record's registered sources, as IDs
    into `sources`.
  - `evidence` is limited to the benchmarks the spec names, grouped under the
    requested domain that tags them, or else the first domain that does.
  - `contributions` is empty for a candidate that `results` ranks: its
    contributions are there, with the same numbers. A candidate beyond the
    result limit carries its own.
- `chart` is inline SVG, with separate raw-value scales by objective dimension.
- `number_origins` covers the numbers a decision presents: every numeric JSON
  leaf in `results`, in `top`'s `evidence`, in `near_misses`,
  `constraint_costs`, `tipping_points` and `eliminated.models`. Each entry has
  its JSON-pointer `path`, calculation or input `basis`, supporting `records`
  and `source_ids`, the registered sources of those records. Measurements
  match retained snapshot records. Distances, gains, normalised values and
  thresholds are explicitly derived numbers, not new measurements. Numbers with
  nothing to trace have no entry: spec weights echoed back (`weight`), the sum
  of spec soft penalties (`soft_penalty`), ranks, the counts `admits`, the
  funnel counts and `out_of_lineup`. A shown fact carries its provenance itself
  (`record_id` or `records`, and `source_ids`), and `top`'s contributions are
  the optimiser's arithmetic on records they list. Before 1.4 every numeric
  leaf had an entry and each repeated its source URLs in `sources`; from 1.4
  `sources` on an origin is always empty.
- `sources` (1.4) lists every source the origins and shown facts cite, once:
  its `id`, `url`, `title` (null: the snapshot records no titles yet) and
  `date`, the latest date a record in this decision citing it was verified.
  Source URLs and winning verification records resolve through
  `snapshot.source_url()` and `snapshot.record()`.
- An offering answers its model's evidence; an evidence row the offering and
  its model both return is listed once (1.4; before, it was listed twice).
- `constraint_costs[].records` are the records behind the two values each gain
  subtracts: the best current and the best relaxed value (1.4; before, every
  record of every row on that dimension).

Raw measurements without retained provenance fail explanation with a rebuild
message. Old snapshots still load for `none`. A missing unit is displayed as
“unit not recorded”; the engine does not infer units from facet names.

The library accepts optional `facets`, `profiles` and `evidence_selectors`
arguments for the registry and explicit benchmark/version/sub-category bindings.
Ambiguous benchmark measurements remain missing. Capability objectives have no
composite until MODEL-129. Requested domains come from `capabilities` and use
snapshot domain tags, never a fixed benchmark list.

## The published vocabulary (MODEL-153)

The site build writes `/api/decision/vocabulary.json` beside the decision
snapshot it describes, and only when it publishes that snapshot. A client reads
it instead of carrying its own list of facets or benchmarks. Built by
[`decision/vocabulary.py`](../decision/vocabulary.py):

- `snapshot`, `contract_version`, `default_task_tokens` and `task_types`.
- `facets`: every registered facet except the parameterised families and the
  `offering.subscription.*` facets. MODEL-173 carries subscription facts in
  snapshot metadata, but MODEL-179 must add holder-cost comparison before a
  client can use them in a spec or objective. Each published facet has
  `id`, `label`, `definition`, `subject`, `value_type`, `unit`, the
  condition `operators` its type admits (`=`, `!=`, `<`, `<=`, `>`, `>=`,
  `between` for `facet in [low, high]`, `in` and `not in` for `facet in {…}`,
  `known`), whether it can be an `objective`, its `risk` and `computed_by`, and
  how much of the lineup knows it: `known` of `of` models or offerings, with
  the `values` (and counts) or the `range` it takes there. Each value of an
  enum or set facet carries the registry's plain `label` where
  `registry/facets.yaml` gives one (`value_labels`), so a client shows
  "Permitted with conditions", not `permitted_with_conditions`. A client offers
  nothing with `known: 0`. `offering.cost_per_task` is counted and ranged at
  `default_task_tokens`. A facet whose lineup values ModelSpec measured adds
  `measurement` (MODEL-212): `measured_by` (`["ModelSpec"]`), `methods` (each
  `id` and `url`), `workloads`, `measured` (how many of the `known` values are
  measurements), `min_n` (the smallest sample behind any of them) and
  `window` (`start` and `end`, UTC). A client that shows a measured number
  names who measured it, the method and the sample. A facet with no measured
  value has no `measurement` key. Each measured value's median, IQR and 95%
  interval are in the fact's record, which a decision's `top` facts reference.
- `benchmarks`: every benchmark with verified evidence in the snapshot, with
  `id`, `name`, `unit`, `higher_is_better`, `models` (lineup models with a
  verified row), `independent_models` (those with a row that `@independent`
  admits), the `range` of those values, and its `domains` with `directness`.
- `refinements`: every registered refinement, with its parent domain, kind,
  definition, benchmark tags, weight key, evidence state, and coverage as
  `measured_models` of `of_models`. The denominator includes only the lineup
  classes eligible for that refinement. Generative refinements count text
  generators; retrieval refinements count vectorisers and orderers.
- `domains`: every registered domain with a listed benchmark. Each row emits
  `id`, `name`, `proxy_only`, `default_basis`, `estimate_models`,
  `estimate_benchmarks`, `direct_models`, `default_benchmark` and `benchmarks`.
  `default_basis` is
  `capability_estimate`; `estimate_models` counts distinct lineup models with
  a stored estimate. `estimate_benchmarks` lists the benchmark drivers that
  contribute to stored lineup estimates for the domain. It can differ from
  `benchmarks`, which is the explicit measured-by drill-down. `direct_models`
  counts distinct lineup models with verified direct evidence.
  `default_benchmark` is only the preselected
  explicit "Measured by" drill-down and is null when the registry preference
  has no verified lineup evidence. It does not select the default ranking
  basis. `benchmarks` puts that verified registry preference first, then
  orders the rest direct before proxy, by descending `models`, then by ID.
- `providers`: every registered provider's display name by ID
  (`registry/providers.yaml`), so a client shows "Anthropic API", not
  `anthropic`.
- `vendors`: every subscription-only vendor's display name by ID
  (`subscription_vendors` in `registry/providers.yaml`, MODEL-205), so a client
  names the seller of a plan such as `cursor/subscription/pro`. A vendor sells
  plans only: it is never in `providers`, `estate.providers` refuses it, and it
  owns no pay-per-use offering. Adding this field is compatible, so
  `vocabulary_version` remains `1`.
- `signatures` (MODEL-227): an Ed25519 signature over the vocabulary, made
  with the snapshot's release key. The signed message is
  `"modelspec.vocabulary\n"` plus `sha256:` and the SHA-256 of the canonical
  JSON of the vocabulary without this block (sorted keys, compact separators),
  so the snapshot's signature cannot be replayed on it. The vocabulary's
  `snapshot` field is inside that digest, which ties it to one snapshot. Each
  row is `{alg, key_id, value}` with `value` base64. `modelspec snapshot
  fetch` verifies it against the pinned key set and refuses a vocabulary whose
  block is present but has no valid signature from a pinned key. A vocabulary
  with no `signatures` (published before MODEL-227) is still accepted on the
  snapshot ID alone, with a warning, and `decision_fetch.vocabulary_signature`
  reports `verified`, `unsigned` or `unpinned`. The block is optional and
  additive, so `vocabulary_version` remains `1` and `contract_version` is
  unchanged. The decide page ignores it: the browser fetches both files over
  HTTPS from the origin it trusts, and does not verify the snapshot either.
- `models`: every snapshot model by ID, with `display_name`, `lab`, `lab_name`,
  and optional `class`. The class is the snapshot's `model.class` fact and may
  be null when that fact is unknown.
- `template_categories` and `template_tiers`: the rows and columns of the
  template grid, from `registry/templates.yaml`, in file order. A category has
  `id`, `name` and `kind` (`use`, what the work is, or `constraint`, what it
  must meet); a tier has `id` and `name` (Best available, Balanced, Budget,
  Fastest, Private / self-hosted). Added in 2.8 (MODEL-204).
- `templates`: the partial decision specs from `registry/templates.yaml`.
  Each row has `id`, `category`, `tier`, `name`, `tradeoff` (the one line a
  grid cell shows), `purpose`, reasoned `where` Musts, reasoned `weights`
  Prefers, optional non-default `task_tokens`, `needs`, `canvas` (the trade-off
  canvas axes to set when the template is applied: `x` and `y`, each
  `facet:<numeric or date facet>` or `capability:<domain>`), `teaches`, and the
  expanded contract fragment under `spec`. A category holds at most one
  template per tier. `category`, `tier`, `tradeoff` and `canvas` were added in
  2.8. The build expands each template and runs it against this same snapshot
  with `explain: none`. `available` is true exactly when that decision has at
  least one ranked result. Otherwise it is false and `unavailable_reason` says
  why: when every candidate only may qualify, it names the facet most of them
  lack (for example no offering has a measured output throughput yet);
  otherwise it describes the decision's first Must whose funnel reaches zero,
  or its `no_feasible` relaxation when no Must does. Before 2.8 a template
  whose candidates only may qualify counted as available. Rows stay present so
  clients can explain why a template is unavailable. Adding these fields is
  compatible, so `vocabulary_version` remains `1`.
- `estate`: the IDs a spec's `estate` accepts: `providers` (every registered
  provider ID), `plans` (each subscription plan in the snapshot as `id`,
  `provider` and `name`) and `devices` (every hardware SKU ID). Adding it is
  compatible, so `vocabulary_version` remains `1`.
- `coverage`: what the lineup holds, so a client can say what an empty answer
  was measured against without writing it per question: `as_of` (the snapshot
  date), `models` (lineup size) and `verified` (lineup models with at least one
  verified evidence row); `classes`, every registered model class with the same
  two counts, zeros included, and per domain how many of its models have
  verified evidence there; `domains`, every registered domain with the lineup
  models that have verified evidence on any benchmark tagged to it (`verified`)
  and on a direct one (`direct`).

The field set is additive: a client ignores fields it does not know.
Templates do not add a spec field. A client expands one before parsing the
spec, so the decision contract and its hash rules are unchanged.

## Versioning (MODEL-59)

Any change that **widens** a field's range bumps the major version of this
contract (`contract_version`). Widening means a client that handled every old
value can now receive one it does not handle: a number becoming nullable, a new
enum value, a field that can be absent. Adding optional fields to a response,
or accepting more in a spec, is compatible and keeps the major.

Decided now, so that later slices do not widen anything:

- `estimates`, `p_best` and `top3_stability` are **nullable from 1.0**. Version
  1.7 fills them without a major bump.
- Every list and object defined before 1.12 is **always present**. Explanation
  levels decide what is populated, not what is present. The optional 1.12
  `benchmark_exclusions` object is absent unless a non-empty exclusion set is
  explained.
- `warnings` (on the decision and on each result) are **an open set of
  lowercase codes**. Clients must accept codes they do not know. A new code is
  not a widening.
- `status`, `measured_by`, `date_type`, `directness`, `explain` and the
  `by_model` row `status` (`ranked`, `may_qualify`, `eliminated`) are **closed**.
  A new value in any of them bumps the major.
- The spec hash algorithm above is part of the contract. Changing it changes
  every published hash, so it bumps the major.

Changes to a spec's inputs follow the same rule in reverse: refusing a spec
that used to be accepted is a major change; accepting more is not.

## Change log

- **2.14 — MODEL-316:** A `no_feasible` decision adds optional
  `relax_task_tokens` when a per-task cost cap fails only because the spec gave
  no `task_tokens`, so cost was priced at the default 40,000 input and 4,000
  output tokens. It names the cap, the default, the largest task at the
  default's ratio that a model meets the cap at, and asks for the real task
  size. A clean agent asking for summarisation under $0.01 per task got
  `no_feasible` from the default alone. Additive: `relax`, `relax_to`,
  `status` and every other field keep their ranges. Bounded answers carry it.

- **MODEL-318, under 2.14 without a version change:** A condition or
  preference value outside its facet's vocabulary is refused with
  `invalid_spec` instead of gating every model out, or none. Such an issue adds
  the optional keys `value`, `value_type`, `allowed_values` and `next`. The
  error-code enum and successful responses are unchanged. This is an exception
  to the input rule above, accepted by Jamie on 2026-10-04 when the contract was
  at 2.13;
  [cli-contract.md](cli-contract.md#contract-versioning-model-59) records why.

- **2.13 — MODEL-308:** Optional `coverage` explains requests outside the board's classes or domains. It includes covered classes and counts and links to the keyless, generated `/api/coverage.json` summary. Complete and bounded decisions retain their existing statuses; `invalid_spec` retains its code, issues and recovery. No class ordering or ranking changes.

- **2.12 — MODEL-284:** A decision adds optional `reading` guidance derived
  from the engine's answers, unapplied requirements, estimates and objective.
  Refusals may also carry guidance for rejected fields. Empty lists are
  omitted and the block is capped at 600 UTF-8 bytes with explicit omission
  counts. Additive: no existing field changes. An `invalid_spec` refusal
  carries both `error.recovery` (at most five registry-backed hints, with
  `error.recovery_omitted` counting the issues left without one) and the
  top-level `reading`. `error.recovery` (MODEL-285, #547/#551) first shipped
  under 2.11 without a version bump; 2.12 records it here.
- **2.11 — MODEL-228:** A comparison takes `facet >= best(m)`, compact `best(1.0)` or YAML
  `value: { best: 1.0 }`: within `m` of the highest value among the models that
  pass every other hard condition. Such a condition runs after the others and
  the funnel lists it after them; see [Relative to the best](#relative-to-the-best).
  A condition on a capability domain now reads the capability estimate: before,
  `software_engineering >= model(…)`, `software_engineering >= 0.5` and
  `known(software_engineering)` left every model unknown. Every Fastest
  template now keeps the models within `best(1.0)` on its domain and ranks
  them by speed alone (High volume: speed 0.6, cost 0.4). Additive:
  `Compare.value` accepts one more shape, and no decision field changes.
- **2.10 — MODEL-221:** A decision adds `feedback`: the endpoint, request
  schema, the five ratings and the CLI line for telling ModelSpec whether the
  answer was reliable, unreliable, trustworthy, untrustworthy or confusing. It
  is a constant, so the CLI and the Worker still return the same bytes.
  Additive: no existing field changes.
- **2.9, unchanged — MODEL-227:** The vocabulary gains an optional `signatures`
  block (see above). No decision field changes and no closed range widens, so
  neither `contract_version` nor `vocabulary_version` moves.
- **2.9 — MODEL-212:** A vocabulary facet adds `measurement` when ModelSpec
  measured any of its lineup values, so a client can say who measured a speed
  and how. A measured fact carries its method, workload, sample size, median,
  IQR and the 95% interval of the median in its record, and that interval
  enters the answer bands like a published benchmark interval, so two
  offerings whose speeds cannot be told apart are not separated by speed.
  Additive: no decision field changes. See
  [`docs/method/speed-measurement.md`](method/speed-measurement.md).
- **2.8 — MODEL-204:** The vocabulary adds `template_categories` and
  `template_tiers`, and each template adds `category`, `tier`, `tradeoff` and
  `canvas`, so a client draws templates as a category-by-tier grid and sets the
  trade-off canvas when one is applied. Templates grow from eight to forty; the
  eight earlier ids are kept. A template is `available` only when its decision
  ranks at least one result; a template whose candidates only may qualify is
  unavailable, and its `unavailable_reason` names the missing facet. Additive:
  no decision field changes.
- **2.7 — MODEL-206:** A decision adds `bands` (the ranked models as `best`,
  `rest` and `thin`, each entry with its score, interval, `p_beats_leader`,
  cost and capability estimates with benchmark and direct-benchmark counts) and `blend` (each
  weighted dimension's share and its order alone). The answer keeps its
  fields and `kind` values; its `members` are now the `best` band, a model
  whose score is at least the leader's with probability 0.25 or more, never a
  thin-evidence model. Before, `members` were every model whose interval
  overlapped the leader's. `answer` can be null for a scalar objective when
  every ranked model is thin; it was already nullable. The capability
  model's intervals are recalibrated: the noise variance of a measurement is
  fitted to held-out benchmark results, so the 80% intervals are narrower.
  All new fields are optional, so the major stays 2.

- **2.6 — MODEL-200:** A spec adds the optional `access` (`chat_app`,
  `coding_tool` with an optional `harness`, `own_software`, `own_hardware`).
  Results add `plans` (plan routes with price, coverage, allowance and, for a
  coding tool, `break_even_tasks_per_month` and its `basis`); an estate row
  reached by a plan adds `coverage`; `with_estate` adds `warnings`. Plan facts
  add surfaces, quoted family coverage and allowance, and the vocabulary's
  `estate.plans` publishes each plan record. All new and optional, so the
  major stays 2. Without `access`, a decision is byte-identical to 2.5's but
  for `contract_version`. That now holds on the Worker too: its pydantic
  (2.10, from Pyodide) ignored `exclude_if` and sent absent optional fields
  as `null` or `[]`, which the contract applies itself from 2.6.

- **2.5 — MODEL-180:** Each result adds the flat `model`, `model_rank` and
  `cost_per_task`, and the decision adds `by_model`, the model-grouped view
  the page used to build for itself. All are new optional fields, so the
  major stays 2. `by_model` lists eliminated models only at `explain: full`.
- **2.4 — MODEL-190:** `optimize.weights` accepts refinement keys
  (`software_engineering/rust`) for refinements the vocabulary marks `live` or
  `thin`, and ranks them on a nested estimate. Results add optional
  `refinement_estimates`; contributions and tipping points add an optional
  `refinement` beside their parent-domain `dimension`; constraint costs add
  optional `refinement_gains`. No closed field widens: `dimension` still
  carries a facet ID, and an unrankable refinement is still `invalid_spec`.
- **2.3 — MODEL-179:** A spec adds the optional `estate` (`providers`, `plans`,
  `devices`, `exhausted`) and a decision adds `with_estate`, the same question
  answered from what the caller holds, with a `gap` to the unrestricted answer
  and a `gain` list. The vocabulary adds `estate`. The estate is never stored.
  No closed value widens.
- **2.2 — MODEL-189:** The vocabulary adds registered refinements and their
  evidence coverage. Until MODEL-190 adds refinement estimates, the hosted
  decide API rejects a refinement weight with the existing closed error code
  `invalid_spec` and names its parent domain. The error-code enum is unchanged.
- **2.1 — MODEL-170:** A decision adds the model-level `answer` block. Its
  `kind` is `separated` or `tied`; `members` overlap the point-estimate
  leader's weighted score interval, without following overlap chains. The
  block also carries `leader` only when separated, its `basis`, four nullable
  `tie_breakers`, and a non-evidentiary `deterministic_order`. Weighted
  objectives now fill `p_best` and `top3_stability` by resampling their
  capability posteriors. The response addition is compatible.
- **2.0 — MODEL-172 (major):** `optimize.weights` values widen from a number
  to a number or a value preference (`{prefer, weight}`). A 1.x client that
  read every weight of a spec or echoed spec as a number must handle the new
  form, so by the versioning rule above this is a major bump. Nothing else
  about the decision's existing fields changed. `optimize.weights` accepts
  value preferences for boolean and enum facets. A match contributes 1, a mismatch or unknown
  contributes 0, and an unknown adds `unknown_preference_value`. Contributions
  add the optional `preferred_value` and `preference_status` fields. The facet
  vocabulary reports whether a facet uses continuous, value-match, or no
  preference scoring. Scale thresholds use the existing `where` plus weight
  form, so Must remains a gate and never adds points.
- **1.12 (MODEL-171):** A spec adds `exclude_benchmarks`. The engine removes
  those evidence rows from conditions and objectives, refits capability
  estimates from the remaining verified evidence, and reports the before and
  after intervals with the removed drivers in `benchmark_exclusions`. An
  omitted or empty set retains the prior canonical spec and decision bytes.
- **1.11 — MODEL-168:** Vocabulary domain rows add the optional
  `estimate_benchmarks` list, and vocabulary model rows add the optional
  `class` field. Both additions are compatible.
- **1.10 — MODEL-182:** A decision adds `signature_verified`. The CLI verifies
  the snapshot against its pinned Ed25519 key set. The Worker can continue to
  verify the HMAC signature with its private key.
- **1.9 — MODEL-169:** A decision adds `truncated`, with counts of qualifying
  offerings and models omitted by `limit`. Qualifying candidates are no longer
  listed in `eliminated` because of the result limit. Pareto-dominated
  candidates remain in `eliminated`. The field addition is compatible and the
  elimination change narrows the existing lists, so neither change widens an
  existing field's range.
- **1.8 — MODEL-161:** Evidence items add the optional source-published
  `interval` and the always-present `quality_flags` list. Deprecated or
  contamination-warned observations remain visible but are not direct answers.
  Overlapping selected measurement intervals add `not_separable`. The additions
  are compatible.
- **1.7 — MODEL-129:** The estimate stage fills `estimates`, `p_best`, and
  `top3_stability`. Estimate evidence adds the optional `loading`,
  `estimate_weight`, and `recency_weight` fields. The additions are compatible.
- **1.6 — MODEL-155:** Funnel steps add model and offering counts beside the
  candidate counts. `near_misses` now has at most one row per model and names
  the best offering that fails exactly one condition. `model_groups` groups
  candidate eliminations by model and places offering eliminations beneath
  that model. The candidate-grained fields remain unchanged.
- **1.5 — MODEL-153:** A `no_feasible` decision adds `relax_to`, the smallest
  change to each numeric cap or floor that admits a model, stated in the
  facet's unit. Additive, so not a major change. `relax` keeps its meaning but
  no longer names the model class or a condition on a requested capability
  domain: recall Q10 (input price at most $0.20 per 1M) was told to drop
  `model.class = text-generator`, which would have admitted a decider. It now
  names the price cap, and `relax_to` says `offering.price.input <= 0.75`.
- **1.4 — MODEL-163:** A `full` decision is compact: since the snapshot
  carried hundreds of verified evidence rows it exhausted the Worker. No field
  changes its range, so by the rule above this is not a major change, but
  three fields change what they hold. A 1.3 client should know:
  - `number_origins[].sources` is always empty. The new `source_ids` name the
    sources, resolved through the new top-level `sources` table (`id`, `url`,
    `title`, `date`).
  - `number_origins` covers the presented numbers, not every numeric leaf:
    see *Explanation provenance*.
  - `top[].facts` holds the named facets and the display set, not every value;
    `top[].evidence` holds the named benchmarks; `top[].contributions` is empty
    for a candidate `results` ranks. A shown fact adds `source_ids`.

  Behaviour at every level: an offering no longer lists its model's evidence
  twice, and a constraint cost's `records` are those behind its gain. The
  Worker and `modelspec decide --json` print compact JSON (no indentation),
  still byte for byte the same; without `--json` the CLI still indents.
  Measured on the live snapshot's default coding task at `limit: 20`, `full`
  went from 7.5 MB to 232 KB.

- **1.3 — MODEL-153:** Additive. A spec accepts `task_tokens` (`input`,
  `output`), and the registry adds the computed facet `offering.cost_per_task`
  in `usd_per_task`. A contribution, a near miss, an elimination and a shown
  fact add `formula`; a shown fact adds `records`, for a computed value with no
  record of its own. `contract_version` is `"1.3"`. A spec without
  `task_tokens` keeps its hash.

- **1.2 — MODEL-157:** Additive. A decision adds `out_of_lineup`, the count of
  active catalogue models outside the snapshot's premier lineup. An evidence
  item adds `harness_unregistered`; `harness` keeps its range, so a 1.1 client
  never sees a value it cannot parse. Behaviour, not shape: a feasible model
  without an objective value moves to `may_qualify` instead of being ranked
  last, `@direct` is read against the spec's `capabilities`, and `in` and
  `not in` on a set-valued facet test for a shared value (before, `in` failed
  every known set and `not in` passed every one).

- **1.1 — MODEL-148:** Objective terms accept evidence qualifiers. This is an
  additive input change; unqualified spec hashes retain their 1.0 canonical
  representation.
- **1.0 — MODEL-145:** Added the optional explanation response fields
  `near_misses`, `top`, `chart`, and `number_origins`, plus retained-record
  provenance on explanation values. Older snapshots must be rebuilt before
  those explanations can be generated.
