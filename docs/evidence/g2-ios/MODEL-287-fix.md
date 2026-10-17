# MODEL-287 execution evidence

Base: `2b2e9a38f19012658f2b390cbb3f00eb8a00ae75`.
Final implementation SHA: pending.

## Design recorded before implementation

`POST /v1/hardware-fit` and MCP `hardware_fit` accept a strict object with
`model`, `sku`, `device_count`, `memory`, `runtime`, `quantisation`, `batch`,
and `context`. Memory is optional, in decimal GB per device. Other omitted
inputs produce an `undetermined` answer. Invalid types and unknown fields
produce HTTP 400. Unknown identifiers remain valid questions.

The new response has `hardware_fit_version: "1.0"`, `endpoint`, `snapshot`,
`request`, `sources`, and a closed `status` discriminant:

- `measured` carries `measured_fit` and an exact cited measurement.
- `estimated` carries `estimated_fit: likely|unlikely`, `margin_bytes`, the
  formula, every numeric input with its provenance, and explicit assumptions.
- `undetermined` carries `missing`, with input names and reasons.

No estimate contains `fits`. Nothing changes the Decision contract 2.18,
estate reach, ranking floors, or `rank_score`. New response variants belong
to this endpoint's own contract. MODEL-59 applies to that contract separately.

The signed snapshot may retain optional verified hardware-fit records read
from `hardware/fit/records.yaml` in the selected data checkout. Records bind
the exact model, SKU, device count, runtime, quantisation, batch, and context.
Every record and parameter has retained provenance and registered sources.
The latest independent verification controls admission. Quarantined,
unregistered, excluded, or incomplete inputs cannot yield an estimate.
Existing frozen curated data is not changed.

Estimate records provide sourced resident `weights_bytes`, per-token
`kv_bytes_per_token`, and `runtime_headroom_bytes`, each scoped per device
for that exact topology and workload. Capacity comes from the dated hardware
record, or the explicit caller override. A SKU with several memory options
requires the override. Model maximum context is a verified snapshot fact.
The calculation is:

```text
kv_cache_bytes = kv_bytes_per_token * batch * context
required_bytes = weights_bytes + kv_cache_bytes + runtime_headroom_bytes
margin_bytes = capacity_bytes - required_bytes
estimated_fit = likely when margin_bytes >= 0, otherwise unlikely
```

Device memory is never pooled. A measurement must also match the effective
memory capacity. Runtime identifiers include any version/settings needed to
identify the cited run. Missing exact records remain undetermined. Generic
quantisation byte constants, fixed 25 percent allowance, raw card geometry,
and existing `model.fits_hardware` membership are not proof for this route.

Both API and MCP require a key even when their optional access-enforcement
switch is off. Visit tokens do not admit this endpoint. Billing uses the
existing `decide.full` resource from `api/worker/tiers.json`, currently two
credits, following named comparison. Successful assessments, including honest
undetermined answers, use the normal reserve/settle flow. Refusals release it.

## Validation

Red and green commands, outputs, versions, and observation limits will be
recorded here after execution. No provider calls, deployment, production
switch changes, Linear writes, or merge are authorized by this work.
