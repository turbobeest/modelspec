# ModelSpec policy-check API — reference

**Use when** you must know whether a model is permitted where you will deploy it,
and which document says so. Checks every model, on every platform it is served
from, against a licence, origin, residency and commercial-use policy. Returns
`pass`, `fail` or `undetermined` per (model, platform), citing the source.

* `POST https://api.modelspec.dev/v1/policy-check`. Shared matters — the
  `User-Agent` rule, keys, neutrality, stability — are in [`api.md`](api.md).
* Spec: [`api/worker/openapi.yaml`](../api/worker/openapi.yaml), generated from
  the implementation. Design and trust boundary:
  [`policy-check-api.md`](policy-check-api.md).

## Request

Only `policy` is required, and it must state at least one constraint: an empty
policy is refused, never passed. Unknown fields are refused. At most 262144
bytes.

| Field | Values |
|---|---|
| `policy.licence` | `allowed` and/or `prohibited` licence types |
| `policy.origin` | `permitted_countries` and/or `prohibited_countries` |
| `policy.residency` | `required_regions`, spelled as the platform publishes them; `match`: `any` (default) or `all` |
| `policy.commercial_use` | `required: true`; `accept_restricted` default false |
| `policy.name` | optional label, echoed back |
| `require_no_undetermined` | `true` turns any undetermined row into a 422 |
| `models`, `platforms` | narrow the check; an unknown id is a 400 |
| `verdicts` | filter returned rows; counts are unaffected |
| `limit`, `offset` | 0–500, default 50; page `result` only |

Regions match literally. No country is mapped onto a cloud region.

## Response

Branch on the tag, never on the absence of a key:

* each check has `state` and exactly one of `satisfied`, `violated`,
  `undetermined`;
* each row has `verdict` and exactly one of `passed`, `failed`,
  `undetermined`.

An undetermined check carries **no** `satisfied` key, so code that reads only
passes fails loudly instead of deploying on a guess. A row that violates one
constraint and leaves another unknown is a `fail`; the unknowns ride in
`failed.also_undetermined`.

`undetermined.why` says who can fix it: `tier` (a paid entitlement),
`not_determined` (research), `not_on_card` and `no_platform` (the catalogue),
`uncited` (a value nobody sourced), `unbounded` (a local runtime: residency is
your machine's, and no tier sells it).

`summary` counts every selected row, whatever the paging; `page` says what
`result` holds. `build.commit` and `provenance` let an answer be defended
later.

## Free and paid

**The endpoint is free, and without a paid-tier key every answer is the free
tier.** `determinations.entitlement` is `public_export`: licence and origin are settled
from public cards. Commercial-use and residency determinations are the paid
product; without them those checks are `undetermined` with `why: tier` and
`available_in_tier: paid`, and `determinations.undetermined_for_lack_of_entitlement`
counts them. A free answer is never a `pass` a paid one would turn into a
`fail`.

**The paid answer is granted to a key with remaining credits** (MODEL-93; the
exempt DPF tier is still on the same path, via a paid unlimited row).
`determinations.entitlement` is then `determinations`. A key whose credits are
exhausted gets the free answer plus `credits.exhausted`, not an error. No paid
key has been issued yet, so every answer today is the free tier. Keys, limits
and their refusals (401, 403, 429, 500, 503 `access_store_not_configured`) are
in [`api.md`](api.md#keys-limits-and-the-sandbox); a request without a key is
not refused while enforcement is off.

## Worked example

```bash
curl -sS -X POST https://api.modelspec.dev/v1/policy-check \
  -H 'content-type: application/json' \
  -d '{"policy":{"licence":{"allowed":["apache-2.0","mit"]},
                 "residency":{"required_regions":["eu-west-1"]}},
       "models":["deepcogito/cogito-671b-v2-1"],"platforms":["together_ai"]}'
```

```json
{
  "schema_version": "1.0",
  "endpoint": "policy-check",
  "build": {
    "commit": "ccd2d6794108a42c2566dc81f8b618eb8289c6a6",
    "built_at": "2026-09-18T01:44:51+00:00",
    "eligibility_as_of": "2026-09-09",
    "export_schema_version": "2.0"
  },
  "service_commit": "ccd2d6794108a42c2566dc81f8b618eb8289c6a6",
  "export_origin": "https://modelspec.dev",
  "policy": {
    "name": null,
    "constraints": {
      "licence": {"allowed": ["apache-2.0", "mit"], "prohibited": []},
      "residency": {"required_regions": ["eu-west-1"], "match": "any"}
    },
    "require_no_undetermined": false
  },
  "determinations": {
    "entitlement": "public_export",
    "included": false,
    "answered_from": "the public export only",
    "store": {
      "loaded": false,
      "generated_on": null,
      "commercial_use_records": 0,
      "residency_platforms": 0
    },
    "undetermined_for_lack_of_entitlement": 1,
    "why": "commercial_use and data_residency are determinations, and determinations are the paid tier. The endpoint itself is free and this answer is complete for every constraint the public export can settle; the checks it could not settle say so individually, with available_in_tier: paid."
  },
  "summary": {
    "models_checked": 1,
    "rows": 1,
    "verdicts": {"pass": 0, "fail": 0, "undetermined": 1},
    "models_with_a_passing_platform": 0,
    "models_undetermined_somewhere": 1,
    "by_constraint": {
      "licence": {"satisfied": 1, "violated": 0, "undetermined": 0},
      "residency": {"satisfied": 0, "violated": 0, "undetermined": 1}
    }
  },
  "provenance": {"determination_read_dates": {}, "determinations_generated_on": null},
  "page": {
    "offset": 0,
    "limit": 50,
    "returned": 1,
    "matching_rows": 1,
    "truncated": false,
    "verdicts_shown": ["pass", "fail", "undetermined"]
  },
  "result": [
    {
      "model_id": "deepcogito/cogito-671b-v2-1",
      "display_name": "Cogito v2.1 671B",
      "provider": "deepcogito",
      "platform": "together_ai",
      "checks": [
        {
          "constraint": "licence",
          "requirement": {"allowed": ["apache-2.0", "mit"], "prohibited": []},
          "state": "satisfied",
          "satisfied": {
            "license_type": "mit",
            "license_url": "https://huggingface.co/deepcogito/cogito-671b-v2.1/blob/main/LICENSE"
          }
        },
        {
          "constraint": "residency",
          "requirement": {"required_regions": ["eu-west-1"], "match": "any"},
          "state": "undetermined",
          "undetermined": {
            "why": "tier",
            "meaning": "this request's tier reads the public export only; the determination is a paid entitlement",
            "available_in_tier": "paid",
            "platform": "together_ai"
          }
        }
      ],
      "verdict": "undetermined",
      "undetermined": {
        "constraints": ["residency"],
        "checks": [
          {
            "constraint": "residency",
            "requirement": {"required_regions": ["eu-west-1"], "match": "any"},
            "state": "undetermined",
            "undetermined": {
              "why": "tier",
              "meaning": "this request's tier reads the public export only; the determination is a paid entitlement",
              "available_in_tier": "paid",
              "platform": "together_ai"
            }
          }
        ]
      }
    }
  ]
}
```

Captured 2026-09-17. The licence is settled from the card; residency needs the
paid tier, so the row is `undetermined`, not `pass`.

## Every error, and the fix

Every refusal carries `error.code` and `error.message`, and `result` is `[]`.

| Status | `error.code` | Cause | Fix |
|---|---|---|---|
| 400 | `invalid_request` | malformed body, unknown field, or an empty policy | `error.fields` and `error.accepted` name what to change |
| 400 | `unknown_model` | a `models` id not in the catalogue | fix or drop the ids in `error.fields` |
| 400 | `unknown_platform` | a `platforms` id outside the platform namespace | pick one from `error.accepted` |
| 404 | `not_found` | no endpoint there | use a path from `error.accepted` |
| 405 | `method_not_allowed` | not `POST` | send `POST` with a JSON body |
| 413 | `payload_too_large` | body over 262144 bytes | omit `models` and page with `limit` and `offset` |
| 422 | `undetermined_present` | `require_no_undetermined` and some rows are unknown | narrow with `models` or `platforms`, or drop the flag. `error.examples` holds up to ten rows |
| 502 | `export_unavailable` | the policy export could not be read | retry; not your request |
| 400 | `sandbox_not_available` | a `test_` key: the sandbox answers `/v1/rank` only | call without a key, or with a live key |
| 503 | `determinations_unavailable` | a paid-tier key, and the store could not be read | retry. Never downgraded to the free answer |
