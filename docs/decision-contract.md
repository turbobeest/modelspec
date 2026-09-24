# The ModelSpec decision contract

Contract version: **1.0**

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

> **Status, slice 1.** The types, the parser, the canonical hash and
> `modelspec decide` are built. The engine is not: `decision.decide` raises
> `NotImplementedError`, and the CLI reports "engine not yet built" (MODEL-141,
> MODEL-142, MODEL-145). Free-text `task` is parsed but refused.

---

## The spec

```yaml spec
spec_version: 1
snapshot: latest
profile: profile:acme-prod
task_type: refactor
capabilities:
  coding.rust: required
  formal_verification: preferred
where:
  - input_price in [0.50, 3.00]
  - swe_bench_pro >= 55 @independent @default_effort measured_after 2026-06-01
  - any: [ offered_on = aws-bedrock:us-east-1, deployment = self_hosted ]
  - not: license = noncommercial
  - coding >= model(openai/gpt-6-sol)
  - context_window >= 200000 soft(0.2)
  - facet: data.trains_on_customer_data
    op: "="
    value: false
    unknown: fail
optimize:
  weights: { coding: 0.6, -cost_per_task: 0.3, output_tps: 0.1 }
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

**Identifiers.** A facet ID is lowercase and dotted (`origin.lab_country`). A
model ID is `lab/model`. A harness ID is `name@major.minor`
(`claude-code@2.1`). Every facet a spec names must be in the facet registry
(`decision.registry`, MODEL-133), or the spec is refused.

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
    - origin.lab_country in {US}
    - license.commercial_use = true
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
input_price in [0.5, 3.0]
origin.lab_country in {US, CA}
origin.lab_country not in {CN, RU}
license != noncommercial
offered_on = aws-bedrock:us-east-1
offered_on = "a value with spaces, or a comma"
known(parameters.total)
coding >= model(openai/gpt-6-sol)
context_window >= 200000 soft(0.2)
data.trains_on_customer_data = false unknown(fail)
swe_bench_pro >= 55 @independent @default_effort measured_after 2026-06-01
swe_bench_pro >= 40 @any @effort(high) @harness(claude-code@2.1) @direct
any(offered_on = aws-bedrock:us-east-1; deployment = self_hosted)
all(input_price <= 3; not(license = noncommercial)) soft(0.5)
not(license = noncommercial)
```

- **Comparisons:** `=`, `!=`, `<`, `<=`, `>`, `>=`. `==` is refused.
- **Windows:** `facet in [low, high]`, both ends inclusive. The ends are both
  numbers or both dates, and `low <= high`.
- **Sets:** `facet in {a, b}` and `facet not in {a, b}`. The engine sorts set
  values and removes duplicates.
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
- facet: context_window
  op: ">="
  value: 200000
  soft: { penalty: 0.2 }
- any:
    - offered_on = aws-bedrock:us-east-1
    - { facet: deployment, op: "=", value: self_hosted }
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
| `@direct` | `direct: true` | Direct evidence only; proxies are excluded. |
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
| `min` | `min: cost_per_task` | Lowest value first. |
| `lexicographic` | see below | Order by the first step, then break near-ties with the next. |
| `weights` | `weights: { coding: 0.6, -cost_per_task: 0.3 }` | A weighted sum over normalised facets. The normalisation is reported in each contribution. |
| `pareto` | `pareto: [ coding, -cost_per_task, output_tps ]` | The non-dominated set. |

In `weights` and `pareto`, a leading `-` on a facet means lower is better.
Weights are positive; a facet may appear once. `pareto` needs at least two
dimensions.

```yaml
optimize:
  lexicographic:
    - max: output_tps within 5%
    - { min: cost_per_task, within: 0.25 }
    - max: coding
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
compact and YAML forms. It changes if any field changes, including the order of
`where`, which orders the funnel. It covers every field, `explain` and `limit`
included.

## The decision

```json decision
{
  "contract_version": "1.0",
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
        {"domain": "coding.rust", "items": [
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
        {"dimension": "coding.rust", "weight": 0.6, "value": 0.81,
         "normalisation": "min-max over the feasible set", "evidence": []}
      ],
      "warnings": ["provisional_released_2_days_ago"]
    }
  ],
  "may_qualify": [
    {"model": "google/gemini-3-8-pro", "offering": null,
     "unknown": ["data.trains_on_customer_data"]}
  ],
  "eliminated": {
    "funnel": [
      {"condition": "input_price in [0.5, 3.0]", "before": 212, "after": 64, "may_qualify": 3}
    ],
    "models": []
  },
  "constraint_costs": [
    {"condition": "origin.lab_country in {US}", "admits": 12, "gain": {"coding.rust": 0.06}}
  ],
  "tipping_points": [
    {"description": "rank 1 holds unless the cost weight exceeds 0.35",
     "dimension": "-cost_per_task", "threshold": 0.35, "new_top": "openai/gpt-6-sol"}
  ],
  "relax": [],
  "warnings": []
}
```

| Field | Meaning |
|---|---|
| `contract_version` | `"1.0"`. |
| `decision_id` | `dec_<id>`. Cite it in outcome records. |
| `snapshot` | The snapshot ID the decision was computed from. Never `latest`. |
| `spec_hash` | The canonical spec hash. |
| `explain` | The explanation level used. |
| `status` | `answered`, `partial` or `no_feasible`; see below. |
| `results` | Ranked results, `rank` 1 to n in order. Empty only when `no_feasible`. |
| `may_qualify` | Models not ranked because a condition could not be evaluated. Each lists the facets it is `unknown` on, and an `offering` when the unknown is offering-level. |
| `eliminated` | The `funnel`: for each condition in order, the candidate count `before` and `after` it, and how many it moved to `may_qualify`. The per-model `models` list, each with the `model`, the `condition` it failed and the `value` it had. |
| `constraint_costs` | For each condition: the `condition`, how many models relaxing it `admits`, and the `gain` on each objective dimension. |
| `tipping_points` | The objective changes that would change the top result: a `description`, and where they apply, the `dimension`, the `threshold` and the `new_top` model. |
| `relax` | For `no_feasible` only: the fewest conditions whose removal gives a feasible answer. |
| `warnings` | Codes about the decision as a whole. |

**`status`:**

- `answered`: the spec was answered in full.
- `partial`: results were returned, but part of the spec could not be
  addressed, for example a requested capability with no evidence for any
  result. `warnings` says which part.
- `no_feasible`: no candidate satisfies the hard conditions. `results` is empty
  and `relax` names the fewest conditions to relax.

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
`date`, `date_type`, `source` (the URL it was read from), `source_snapshot`
(the content hash of the retained copy) and `directness`.

- `measured_by` is one of `benchmark_author`, `independent`,
  `provider_self_report`, `modelspec`, `outcome_protocol`.
- `date_type` is `observed` (a live leaderboard, dated by when it was read) or
  `published` (a paper or launch post, dated by publication).
- `directness` is `direct` or `proxy`, relative to the requested domain.

Only verified evidence reaches a decision; quarantined values never do.

### Explanation levels

| `explain` | Populated |
|---|---|
| `none` | `results` without `contributions`; `may_qualify`. For high-rate automated calls. |
| `summary` | Adds `contributions`, the `funnel`, `constraint_costs` and `tipping_points`. |
| `full` | Adds `eliminated.models` (per-model reasons). |

The fields are always present. At a lower level, the lists it does not populate
are empty.

## The library and the CLI

```python
from decision import decide, parse_spec
from decision.registry import facet

spec = parse_spec(open("spec.yaml").read(), facets=facet)   # raises SpecError
decision = decide(spec, snapshot)                             # NotImplementedError until the engine lands
```

`parse_spec(raw, facets=...)` takes YAML text or a mapping. `facets=None`
checks structure only. A `SpecError` lists every issue; each names the `path`
(`where[1].any[0]`), the `condition` as written, the `field` (the facet or spec
field) and the `reason`.

```
modelspec decide SPEC.yaml [--explain none|summary|full] [--json]
```

`--explain` overrides the spec's `explain`. Until the engine lands, the command
validates the spec and exits **1** in both cases:

- **Invalid spec:** every issue, on stderr. With `--json`, stderr carries
  `{"contract_version", "command": "decide", "error": {"code": "invalid_spec",
  "issues": [{"path", "condition", "field", "reason"}]}}`.
- **Valid spec:** the `spec_hash` and "engine not yet built", on stderr. With
  `--json`, the error code is `engine_not_built`, beside `spec_hash` and
  `explain`.

If the facet registry cannot be loaded, the command says so in a warning, and
facet IDs are not checked.

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
