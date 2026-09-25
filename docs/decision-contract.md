# The ModelSpec decision contract

Contract version: **1.5**

A **spec** asks for a decision. A **decision** is the engine's answer to one
spec against one snapshot. This document is the public contract for both. The
same contract serves the local library and CLI, the hosted API and MCP.

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
  weights: { software_engineering: 0.6, -offering.price.output: 0.3, offering.speed.throughput: 0.1 }
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
| `task_tokens` | `{input, output}`, whole numbers ≥ 0 | `{input: 40000, output: 4000}` | Tokens one task takes. Prices `offering.cost_per_task`; see below. |
| `where` | list of conditions | `[]` | Conditions, ANDed, applied in order. The order sets the order of the elimination funnel. |
| `optimize` | objective | required | Exactly one objective form. |
| `unknowns` | `default` | `default` | How unknown values are handled when a condition does not say. The only value is `default`: capability facets list the model as "may qualify", governance facets count it as not satisfied. |
| `explain` | `none`, `summary`, `full` | `summary` | How much explanation to return. |
| `limit` | integer, 1–500 | `20` | The maximum number of results. |
| `save_as` | lowercase slug | none | A name to save the spec under. Saved specs and alerts arrive in a later slice. |

A spec with a field not named here is refused. Nothing is silently ignored.

**`task_type`** is one of `new_feature`, `bug_fix`, `refactor`,
`test_writing`, `docs`, `migration`, `performance`, `security_fix`, `review`,
`analysis`, `data_transform`, `config_infra`: the outcome protocol's task
types.

**Identifiers.** A facet ID is lowercase and dotted (`origin.lab_jurisdiction`). A
model ID is `lab/model`. A harness ID is `name@major.minor`
(`claude-code@2.1`). Every facet a spec names must be in the facet registry
(`decision.registry`, MODEL-133), or the spec is refused.

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
    - licence.commercial_use = true
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
  value on the same facet.
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
| Comparison, relative | `facet`, `op`, `value` (a scalar, or `{ model: <model ID> }`) |
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

An objective must name an ordered facet. A `bool`, `enum` or `string` facet
cannot be maximised, windowed or compared with `<`.

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

```json decision
{
  "contract_version": "1.5",
  "decision_id": "dec_01J8ZK3Q7Y",
  "snapshot": "snap_2026-09-24T06:00Z",
  "spec_hash": "sha256:9f2c1e4b7a0d3f6e8c5b2a1d4e7f0c3b6a9d2e5f8c1b4a7d0e3f6c9b2a5d8e1f",
  "explain": "summary",
  "status": "answered",
  "results": [
    {
      "rank": 1,
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
  "may_qualify": [
    {"model": "google/gemini-3-8-pro", "offering": null,
     "unknown": ["offering.data.trains_on_customer_data"]}
  ],
  "eliminated": {
    "funnel": [
      {"condition": "offering.price.input in [0.5, 3.0]", "before": 212, "after": 64, "may_qualify": 3}
    ],
    "models": []
  },
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
  "out_of_lineup": 1334
}
```

| Field | Meaning |
|---|---|
| `contract_version` | `"1.5"`. |
| `decision_id` | `dec_<id>`. Cite it in outcome records. |
| `snapshot` | The snapshot ID the decision was computed from. Never `latest`. |
| `spec_hash` | The canonical spec hash. |
| `explain` | The explanation level used. |
| `status` | `answered`, `partial` or `no_feasible`; see below. |
| `results` | Ranked results, `rank` 1 to n in order. Empty only when `no_feasible`. |
| `may_qualify` | Models not ranked because a condition could not be evaluated, or because they pass every condition but have no value for the objective. Each lists the facets it is `unknown` on (for a missing objective value, the objective's facet or benchmark), and an `offering` when the unknown is offering-level. A model is never ranked on an unknown objective value. |
| `eliminated` | The `funnel`: for each condition in order, the candidate count `before` and `after` it, and how many it moved to `may_qualify`. The per-model `models` list, each with the `model`, the `condition` it failed and the `value` it had. |
| `constraint_costs` | For each condition: the `condition`, how many models relaxing it `admits`, and the `gain` on each objective dimension. |
| `tipping_points` | The objective changes that would change the top result: a `description`, and where they apply, the `dimension`, the `threshold` and the `new_top` model. |
| `relax` | For `no_feasible` only: the fewest conditions whose removal gives a feasible answer. Never the model class or a condition on a requested capability domain, which would change the question; among equally few, numeric caps and floors first. |
| `relax_to` | For `no_feasible` only (1.5): for each numeric cap or floor, the smallest change that admits a model. Each names the spec's `condition`, the `relaxed` condition (same facet and direction, at the nearest value an excluded candidate has), the `facet`, that `value`, its `unit`, and how many models it `admits`. |
| `warnings` | Codes about the decision as a whole. |
| `out_of_lineup` | How many active catalogue models the snapshot leaves outside its lineup, and so outside this decision. `0` when the snapshot was built without a premier list. |

**`status`:**

- `answered`: the spec was answered in full.
- `partial`: results were returned, but part of the spec could not be
  addressed, for example a requested capability with no evidence for any
  result. `warnings` says which part.
- `no_feasible`: no candidate satisfies the hard conditions, or none that does
  has a value for the objective. `results` is empty and `relax` names the
  fewest conditions to relax, or the reason no result could be ranked.

**The lineup.** A decision ranges over the snapshot's lineup. A snapshot built
from a premier list (slice 1: `premier/slice-1.yaml`) holds only the premier
models and their offerings, plus the live archive of retired models. Retired
models enter a decision only when a condition asks for lifecycle `retired`.
Every other catalogue model is left out and counted in `out_of_lineup`; it is
never listed as a candidate or in `may_qualify`.

### A result

| Field | Meaning |
|---|---|
| `rank` | 1-based position. |
| `offering` | `model`, and when the result is an offering, its `provider`, `region` and `tier`. |
| `harness` | The harness the evidence and estimate apply to, or null. |
| `effort` | The effort setting the evidence and estimate apply to, or null. |
| `evidence` | For each requested `domain`, the evidence `items`, unblended. In slice 1 this is the capability answer. |
| `estimates` | Capability estimates per `domain`, each a `value` and an `interval` `[low, high]`, with the `harness` and `effort` they apply to. **Null until slice 2** (the capability model, MODEL-129). |
| `p_best` | The probability this result is the best choice. Null until slice 2. |
| `top3_stability` | The share of resamples in which the result stays in the top 3. Null until slice 2. |
| `soft_penalty` | The total penalty from violated soft conditions. |
| `contributions` | Per objective `dimension`: its `weight`, normalised `value`, the `normalisation` used, and the `evidence` behind it. |
| `warnings` | Codes about this result. |

**An evidence item** carries `benchmark`, `version`, `sub_category`, `value`,
`unit`, `n` (a count, for outcome rates), `measured_by`, `effort`, `harness`,
`harness_unregistered`, `date`, `date_type`, `source` (the URL it was read
from), `source_snapshot` (the content hash of the retained copy) and
`directness`.

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

### Explanation levels

| `explain` | Populated |
|---|---|
| `none` | `results` without `contributions`; `may_qualify`. For high-rate automated calls. |
| `summary` | Adds `contributions`, the `funnel`, `constraint_costs` and `tipping_points`. |
| `full` | Adds `eliminated.models`, `top` candidates with their relevant values, `chart`, `number_origins` and the `sources` they cite. |

The fields are always present. At a lower level, the lists it does not populate
are empty.

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
modelspec decide SPEC.yaml [--explain none|summary|full] [--json]
```

`--explain` overrides the spec's `explain`. Pass `--snapshot-file SNAPSHOT.gz`
or set `MODELSPEC_DECISION_SNAPSHOT` to a local decision snapshot. No network
request is made. `--explain full --html out.html` writes a self-contained report
with an inline SVG contribution chart, light and dark styles, and source links.
The command emits the decision as JSON. Invalid specs, unavailable snapshots,
and unresolved explanation provenance exit **1** with a structured error when
`--json` is set. Successful decisions, including `no_feasible`, exit **0**.

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
- `near_misses` lists candidates that fail exactly one hard condition while
  passing the others. Each includes `offering`, `condition`, `facet`, `value`,
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
- `facets`: every registered facet except the parameterised families, each
  with `id`, `label`, `definition`, `subject`, `value_type`, `unit`, the
  condition `operators` its type admits (`=`, `!=`, `<`, `<=`, `>`, `>=`,
  `between` for `facet in [low, high]`, `in` and `not in` for `facet in {…}`,
  `known`), whether it can be an `objective`, its `risk` and `computed_by`, and
  how much of the lineup knows it: `known` of `of` models or offerings, with
  the `values` (and counts) or the `range` it takes there. Each value of an
  enum or set facet carries the registry's plain `label` where
  `registry/facets.yaml` gives one (`value_labels`), so a client shows
  "Permitted with conditions", not `permitted_with_conditions`. A client offers
  nothing with `known: 0`. `offering.cost_per_task` is counted and ranged at
  `default_task_tokens`.
- `benchmarks`: every benchmark with verified evidence in the snapshot, with
  `id`, `name`, `unit`, `higher_is_better`, `models` (lineup models with a
  verified row), `independent_models` (those with a row that `@independent`
  admits), the `range` of those values, and its `domains` with `directness`.
- `domains`: every registered domain with a listed benchmark, its `benchmarks`
  ordered direct first, then by `models`.
- `providers`: every registered provider's display name by ID
  (`registry/providers.yaml`), so a client shows "Anthropic API", not
  `anthropic`.
- `coverage`: what the lineup holds, so a client can say what an empty answer
  was measured against without writing it per question: `as_of` (the snapshot
  date), `models` (lineup size) and `verified` (lineup models with at least one
  verified evidence row); `classes`, every registered model class with the same
  two counts, zeros included, and per domain how many of its models have
  verified evidence there; `domains`, every registered domain with the lineup
  models that have verified evidence on any benchmark tagged to it (`verified`)
  and on a direct one (`direct`).

The field set is additive: a client ignores fields it does not know.

## Versioning (MODEL-59)

Any change that **widens** a field's range bumps the major version of this
contract (`contract_version`). Widening means a client that handled every old
value can now receive one it does not handle: a number becoming nullable, a new
enum value, a field that can be absent. Adding optional fields to a response,
or accepting more in a spec, is compatible and keeps the major.

Decided now, so that later slices do not widen anything:

- `estimates`, `p_best` and `top3_stability` are **nullable from 1.0**. Slice 2
  fills them without a bump.
- Every list and object in a decision is **always present**. Explanation
  levels decide what is populated, not what is present.
- `warnings` (on the decision and on each result) are **an open set of
  lowercase codes**. Clients must accept codes they do not know. A new code is
  not a widening.
- `status`, `measured_by`, `date_type`, `directness` and `explain` are **closed**.
  A new value in any of them bumps the major.
- The spec hash algorithm above is part of the contract. Changing it changes
  every published hash, so it bumps the major.

Changes to a spec's inputs follow the same rule in reverse: refusing a spec
that used to be accepted is a major change; accepting more is not.

## Change log

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
