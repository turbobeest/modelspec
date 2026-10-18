# Hardware-fit API contract

Contract version: **2.0**, identified by `hardware_fit_version`.

Changelog: 2.0 (MODEL-401) permits omitted runtime headroom in estimate records
and adds `basis: "full"|"lower_bound"`. A lower bound can establish only
`unlikely`.

`POST /v1/hardware-fit` checks one model, hardware topology, runtime, and
workload against the signed snapshot. The MCP tool is `hardware_fit`.
Both require an API key, including when optional access enforcement is off.
A browser visit token does not admit this route.

This contract is independent of Decision 2.18. Its `status` is a closed set.
Widening a field's range requires a major version under MODEL-59. No existing
Decision field changes. This check does not change estate reach or ranking.

## Request

The body is a strict JSON object. Unknown fields and invalid types return 400.
Omitted or null inputs return an `undetermined` assessment naming what is
missing. Identity strings contain 1 to 512 characters and cannot be whitespace.

| Field | Type | Meaning |
| --- | --- | --- |
| `model` | string | Exact catalogue model ID. |
| `sku` | string | Exact hardware SKU ID, including underscores where the catalogue uses them. |
| `device_count` | integer, 1 to 1,024 | Number of devices in this topology. No default. |
| `memory` | finite number, greater than 0 and at most 1,000,000, optional | Decimal GB per device, supplied by the caller. Required when the SKU has several memory options. |
| `runtime` | string | Exact runtime identity, including any version and settings that the source requires. |
| `quantisation` | string | Exact quantisation identity. `Q4_K_M` and generic `q4` do not substitute for each other. |
| `batch` | integer, 1 to 1,000,000 | Number of concurrent sequences. No default. |
| `context` | integer, 1 to 1,000,000,000 | Tokens per sequence, including the requested context budget. No default. |

An optional `X-ModelSpec-Snapshot` header pins the expected snapshot. A
mismatch returns 409 `snapshot_changed` before validating request fields.
Unknown model, SKU, runtime, or quantisation values are valid questions and
produce `undetermined` when no matching evidence exists.

## Response

Every successful assessment returns HTTP 200 with `hardware_fit_version`,
`endpoint: "hardware-fit"`, `snapshot`, `request`, `sources`, and exactly one
`status`: `measured`, `estimated`, or `undetermined`.

`measured` carries `measured_fit` and a cited measurement that matches every
request dimension and the effective memory capacity. It reports the
observation in that run. Different counts, runtime settings, quantisations,
batches, contexts, or memory capacities cannot inherit the measurement.

`estimated` carries `basis`, `estimated_fit: "likely"|"unlikely"`, `margin_bytes`,
the formula, all numeric inputs with provenance, and explicit assumptions.
Inputs and calculations are per device. The response has no `fits` field.
An estimate does not establish successful loading, runtime compatibility,
latency, throughput, or fit in a measured run.

For `basis: "full"`, `per_device` lists each device's sourced `weights_bytes`,
`kv_bytes_per_token`, and `runtime_headroom_bytes`, followed by calculated
`kv_cache_bytes`, `required_bytes`, and `margin_bytes`. Source numbers carry
`value`, `record_id`, and `source_ids`. Measurements and estimates retain their
winning `verification`.

```text
kv_cache_bytes = kv_bytes_per_token * batch * context
required_bytes = weights_bytes + kv_cache_bytes + runtime_headroom_bytes
margin_bytes = capacity_bytes - required_bytes
```

`margin_bytes` is the smallest per-device margin. A full estimate is `likely`
when every device has a nonnegative margin and `unlikely` otherwise.

If any device lacks sourced runtime headroom, the engine instead calculates
lower bounds for every device:

```text
kv_cache_bytes = kv_bytes_per_token * batch * context
lower_bound_bytes = weights_bytes + kv_cache_bytes
margin_bytes = capacity_bytes - lower_bound_bytes
```

If any lower bound exceeds capacity, the response is `estimated` with
`basis: "lower_bound"` and `estimated_fit: "unlikely"`. Each `per_device`
entry has `lower_bound_bytes` instead of `required_bytes`. The top-level
margin is negative. Absent headroom has this explicit shape:

```json
{"status": "not_required", "reason": "Runtime headroom is not required to establish this lower bound."}
```

That object is the value of `runtime_headroom_bytes`, never a numeric zero.
Devices with sourced headroom retain that input, but the lower-bound formula
excludes headroom on every device. The response includes the formula, sourced
inputs, caller batch and context, capacity provenance, and this assumption.
If every lower bound is at or below capacity, missing headroom instead yields
`undetermined`. Equality without headroom is `undetermined`. A lower bound
never yields `likely`.

Device memory is never pooled. Every device's sourced weight and cache allocation
must match the complete requested topology and workload.
Estimates require verified open weights and a SKU exposing one usable memory pool.

Capacity comes from the dated vendor record or the caller's explicit memory
override. The latter is identified as a caller input, with no invented source
citation. Maximum context comes from a verified model fact. The response
resolves cited source IDs to registered URLs.

`undetermined` carries a `missing` list. Each item names an input and the
reason it cannot be established. Examples include an omitted batch, an
unknown SKU, unsourced quantisation weights, missing runtime headroom, and
context above the model's verified maximum. It contains no fit verdict.

## Data admission

The snapshot builder reads optional curated records from
`hardware/fit/records.yaml` in the selected data checkout. Each record binds
the exact model, SKU, device count, runtime, quantisation, batch, and context.
All records also bind effective memory capacity. Estimate records
provide each device's resident weight bytes and KV bytes per token. Runtime
headroom bytes may be omitted per device. When present, headroom must be
sourced under the same admission rules. Numeric inputs retain their record
IDs and source IDs. Omitted headroom remains absent in the signed record.

The latest independent, value-bound verification covers the whole record.
Missing, mismatched, quarantined, excluded, or unregistered source evidence
cannot yield a measurement or estimate. Existing `model.fits_hardware`
membership, raw card geometry, generic quantisation byte constants, and the
legacy fixed working allowance do not supply missing inputs.

This change adds no curated production records. Existing snapshots without
these records return `undetermined` for concrete workload checks. Fresh
curated records belong in the private `modelspec-data` repository.

## Billing and refusals

The route uses the existing `decide.full` resource from `tiers.json`, currently
two credits. Normal key quotas and credit exemptions apply. A successful
`undetermined` assessment uses the same cost as other successful assessments.
Transport, access, schema, and snapshot refusals do not settle a charge.
When the normal unfunded fallback applies, optional `credits` metadata reports
exhaustion. Payment and human-gate settings can require funding instead.

Missing credentials return 401 `missing_api_key`. Invalid fields return 400
`invalid_request`. A stale snapshot pin returns 409 `snapshot_changed`.
Unavailable signed data returns 503. The generated OpenAPI document lists
the remaining transport, key, quota, and billing refusals.
