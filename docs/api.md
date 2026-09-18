# ModelSpec API — reference

**Use when** choosing, switching, or checking a model before a task or deploy.
Ranks AI models you can actually run, given your hardware, providers, use case
and policy rules. Returns ranked models with scores, cost and reasons; on
failure, returns which constraint eliminated every option.

Computed per request from the current public export. No state, no signup, and
today no key.

* `POST https://api.modelspec.dev/v1/rank` — a shortlist for one profile.
  Below.
* `POST /v1/policy-check` — pass, fail or undetermined per model and platform
  against a compliance policy:
  [`api-policy-check.md`](api-policy-check.md).
* `GET /v1/health` — the deployed version, and whether it can read the exports.
* Spec: [`api/worker/openapi.yaml`](../api/worker/openapi.yaml), generated from
  the implementation. Build your client from it.
* Send a real `User-Agent`: Cloudflare refuses the standard-library default
  (`Python-urllib/*`) before the request arrives.

## Request

Only `use_case` is required. An unknown field is refused, never ignored, so you
never mistake an unapplied constraint for an applied one. `null` means "not
stated". At most 16384 bytes.

| Field | Values |
|---|---|
| `use_case` | one of 51 profiles; the spec enumerates them |
| `environment.hardware` | a device id from `/api/rank/hardware.json` |
| `environment.hosting` | `local`, `self_hosted`, `managed_api` |
| `environment.runtime` | a platform id; only local runtimes filter anything |
| `constraints.open_weights` | boolean |
| `constraints.max_cost_per_million_input_tokens` | USD, applied before scoring |
| `constraints.price_sensitivity` | 0–1; profiles weigh cost at 0 without it |
| `constraints.include_rehosts` | boolean, default false |
| `limit` | 0–100, default 10; caps the ranked list, not the pool |

`local`, `self_hosted` and any local runtime imply open weights.

## Response

`result` is the shortlist, best first, never empty on a `200`. Read four things
before acting:

* `applied.unbound` — fields accepted, recorded, and **filtered nothing**, with
  the reason. The export holds no runtime-level evidence, so
  `environment.runtime: "together_ai"` narrows nothing and says so.
* `build.commit` — the catalogue answered from; `service_commit` the Worker.
* `ranking_status` — `complete`, `partial`, `empty`, `unavailable`. `partial` is
  normal: models without enough benchmark evidence are withheld, not ranked low.
* `evidence_basis` per row — `none`, `unverified-legacy`, `mixed`,
  `partial-verified`, `verified`. Where the benchmark inputs came from; not a
  quality verdict, and `verified` is not a certificate.

## Worked example

```bash
curl -sS -X POST https://api.modelspec.dev/v1/rank \
  -H 'content-type: application/json' \
  -d '{"use_case":"coding",
       "environment":{"hosting":"local","runtime":"ollama"},
       "constraints":{"max_cost_per_million_input_tokens":2.0,"price_sensitivity":0.25},
       "limit":1}'
```

```json
{
  "schema_version": "1.0",
  "endpoint": "rank",
  "build": {
    "commit": "ccd2d6794108a42c2566dc81f8b618eb8289c6a6",
    "built_at": "2026-09-18T01:44:51+00:00",
    "eligibility_as_of": "2026-09-09",
    "export_schema_version": "2.0"
  },
  "service_commit": "ccd2d6794108a42c2566dc81f8b618eb8289c6a6",
  "export_origin": "https://modelspec.dev",
  "request": {
    "use_case": "coding",
    "environment": {"hardware": null, "hosting": "local", "runtime": "ollama"},
    "constraints": {
      "open_weights": true,
      "max_cost_per_million_input_tokens": 2.0,
      "price_sensitivity": 0.25,
      "include_rehosts": false
    },
    "limit": 1
  },
  "applied": {
    "open_weights_only": true,
    "open_weights_required_by": "environment.hosting",
    "hardware_id": null,
    "max_cost_per_million_input_tokens": 2.0,
    "cost_weight": 0.25,
    "include_rehosts": false,
    "unbound": []
  },
  "policy": {
    "version": "incomplete-evidence-v1",
    "ordering": "conservative_lower_bound",
    "min_benchmark_coverage": 0.5,
    "cli_min_benchmark_coverage": 0.5,
    "wizard_min_benchmark_coverage": 0.25,
    "min_benchmark_count": 2,
    "limit_applies_to": "ranked_only",
    "uncertainty": "missing-benchmark bounds, not statistical confidence intervals",
    "neutrality": {
      "version": "neutrality-v1",
      "operator": "Sparks & Sawdust LLC",
      "rule": "Charging the consumer of a recommendation is compatible with being an honest broker. Charging the subjects of one is not.",
      "pledge": "No referral fees, no paid placement, no provider-paid visibility, permanently.",
      "permanent": true,
      "assertions": {
        "accepts_referral_fees": false,
        "accepts_paid_placement": false,
        "accepts_provider_paid_visibility": false,
        "proxies_inference_tokens": false,
        "stores_customer_prompts": false
      },
      "source_neutral_at": ["ranking", "tie_breaks", "hosting_suggestions", "route_advice"],
      "charges": "the consumer of a recommendation, never its subjects",
      "method_source": "https://github.com/turbobeest/modelspec/blob/main/api/ranking/engine.py",
      "terms_url": "https://modelspec.dev/legal/terms/",
      "neutrality_url": "https://modelspec.dev/legal/neutrality/",
      "privacy_url": "https://modelspec.dev/legal/privacy/"
    }
  },
  "profile": "coding",
  "ranking_status": "partial",
  "ranked_count": 30,
  "unranked_count": 280,
  "candidates_considered": 1339,
  "result": [
    {
      "model_id": "deepseek/deepseek-v3-2",
      "display_name": "DeepSeek V3.2",
      "provider": "DeepSeek",
      "score": 84.78,
      "rank": 1,
      "score_lower_bound": 84.78,
      "score_upper_bound": 92.78,
      "score_kind": "conservative_lower_bound",
      "benchmark_score": 25.01,
      "capability_score": 18.15,
      "cost_score": 21.77,
      "context_score": 4.85,
      "type_bonus": 15.0,
      "rank_status": "ranked",
      "unranked_reason": null,
      "benchmark_coverage": 0.8,
      "benchmark_count": 7,
      "required_benchmark_count": 2,
      "missing_benchmarks": ["scicode"],
      "benchmark_estimate": 78.14355158730159,
      "benchmark_lower_bound": 25.00593650793651,
      "benchmark_upper_bound": 33.00593650793651,
      "benchmark_contributions": {
        "humaneval": 13.96,
        "swe_bench_verified": 9.71,
        "live_code_bench": 11.86,
        "aider_polyglot": 7.8,
        "arena_elo_coding": 10.5,
        "arena_elo_overall": 6.8,
        "terminal_bench": 1.89
      },
      "context_window": 131072,
      "cost_input": 0.14,
      "open_weights": true,
      "evidence_basis": "unverified-legacy",
      "verified_contributions": 0,
      "verified_benchmark_coverage": 0.0,
      "scores_as_of": "2026-04"
    }
  ]
}
```

Captured 2026-09-17. Scores move; the shape does not.

## Every error, and the fix

Every refusal carries `error.code` and `error.message`, and `result` is `[]`.

| Status | `error.code` | Cause | Fix |
|---|---|---|---|
| 400 | `invalid_request` | an unaccepted field, or the wrong type | `error.fields` names them, `error.accepted` lists what exists |
| 400 | `unknown_use_case` | no such profile | pick one from `error.accepted` |
| 400 | `unknown_hardware` | no such device id | pick one from `error.accepted`. Never means "nothing fits" — that is a 422 |
| 400 | `unknown_hosting` | not `local`, `self_hosted` or `managed_api` | pick one from `error.accepted` |
| 400 | `unknown_runtime` | no such platform id | pick one from `error.accepted`, or drop it: only local runtimes filter |
| 404 | `not_found` | no endpoint there | use a path from `error.accepted`; paths are versioned |
| 405 | `method_not_allowed` | wrong verb for the path | `POST` to `/v1/rank`, `GET` to `/v1/health` |
| 413 | `payload_too_large` | body over 16384 bytes | a rank request is a few hundred bytes |
| 422 | `no_match` | a filter eliminated every candidate | relax `error.relax`. `error.eliminated_by` has the survivor counts, `error.elimination_trace` every filter in order |
| 422 | `insufficient_evidence` | candidates survived, none has the coverage to be ordered | relaxing constraints will not help; try a broader `use_case` |
| 502 | `export_unavailable` | the published export could not be read | retry; not your request |
| 403 | *(not JSON)* | Cloudflare refused the client at the edge: `error code: 1010` | send a real `User-Agent` |

A no-match is an answer, not an empty list:

```jsonc
{
  "ranking_status": "empty",
  "error": {
    "code": "no_match",
    "message": "no model survives constraints.max_cost_per_million_input_tokens=0.0: it took the pool from 1339 to 0.",
    "eliminated_by": {"constraint": "constraints.max_cost_per_million_input_tokens",
                      "value": 0.0, "survivors_before": 1339, "survivors_after": 0},
    "elimination_trace": [ /* every filter, in the order the scorer applies them */ ],
    "relax": "constraints.max_cost_per_million_input_tokens"
  },
  "result": []
}
```

## Keys, rate limits and the sandbox — **not live yet**

**Today the API takes no key and meters nothing.** It never returns 401,
403 or 429. Do not build a client that depends on those statuses; do build one
that tolerates them.

The access layer is implemented (MODEL-69, `docs/api-access.md`) and not yet
wired into the deployed Worker. When it is, from `api/worker/tiers.json`:

| Tier | Daily | Burst | Live data |
|---|---|---|---|
| sandbox — any key starting `test_` | **unlimited** | unlimited | no; fixed synthetic rows |
| free | 10 | 5/min | yes |
| paid | by plan | by plan | yes |
| dpf | unlimited | unlimited | yes |

Keys go in `Authorization: Bearer <key>` or `X-API-Key`, never the query string.
The daily window is a UTC calendar day, the burst window a UTC minute; a 429
will state `limit`, `used`, `resets_at` and `retry_after_seconds`. No pricing
page exists yet. No request is granted policy-check's paid tier either:
[`api-policy-check.md`](api-policy-check.md#free-and-paid).

## Neutrality, and what is not in force

* **The neutrality commitment is live, as data:**
  [`profiles.json`](https://modelspec.dev/api/rank/profiles.json) →
  `.ranking_policy.neutrality`, and `policy.neutrality` on every `/v1/rank`
  answer. No referral fees, no paid placement, no provider-paid visibility.
* **No terms of use are in force.** The MODEL-70 terms and privacy pages are
  unadopted drafts, not linked here; they bind nobody yet.
* **No landing page** — MODEL-24.

## Stability

`schema_version` (`"1.0"`) versions this envelope; `build.export_schema_version`
the published catalogue. Widening a field's range — nullable, a new enum value,
may-be-absent — bumps that contract's major ([`cli-contract.md`](cli-contract.md)).
Fields may be added within a major: ignore what you do not know.

A request carries a profile, never a prompt — architectural, not missing.
Design and deployment: [`rank-api.md`](rank-api.md).
