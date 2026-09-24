# ModelSpec API — reference

**Use when** choosing, switching, or checking a model before a task or deploy.
Ranks AI models you can actually run, given your hardware, providers, use case
and policy rules. Returns ranked models with scores, cost and reasons; on
failure, returns which constraint eliminated every option.

Computed per request from the current public export. No state, no signup.

* `POST https://api.modelspec.dev/v1/rank` — a shortlist for one profile.
* `POST /v1/policy-check` — pass, fail or undetermined per model and platform
  against a compliance policy:
  [`api-policy-check.md`](api-policy-check.md).
* `GET /v1/health` — the deployed version, and whether it can read the exports.
* Spec: [`api/worker/openapi.yaml`](../api/worker/openapi.yaml), generated from
  the implementation. Build your client from it.
* Send a real `User-Agent`: Cloudflare refuses the standard-library default
  (`Python-urllib/*`) before the request arrives.

## Request

Only `use_case` is required. An unknown field is refused, never ignored. `null`
means "not stated". At most 16384 bytes.

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

`result` is the shortlist, best first, never empty on a `200`. Read:

* `applied.unbound` — fields accepted and recorded that **filtered nothing**,
  with the reason (e.g. `environment.runtime: "together_ai"`).
* `build.commit` — the catalogue answered from; `service_commit` the Worker.
* `ranking_status` — `complete`, `partial`, `empty`, `unavailable`. `partial` is
  normal: models lacking benchmark evidence are withheld, not ranked low;
  `unranked_candidates` names ten, newest first.
* `evidence_basis` per row — `none`, `unverified-legacy`, `mixed`,
  `partial-verified`, `verified`: input provenance, not a quality verdict.

## Worked example

```bash
curl -sS -X POST https://api.modelspec.dev/v1/rank \
  -H 'content-type: application/json' \
  -d '{"use_case":"coding",
       "environment":{"hosting":"managed_api"},
       "constraints":{"price_sensitivity":0.25},
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
    "export_schema_version": "3.0"
  },
  "service_commit": "ccd2d6794108a42c2566dc81f8b618eb8289c6a6",
  "export_origin": "https://modelspec.dev",
  "request": {
    "use_case": "coding",
    "environment": {
      "hardware": null,
      "hosting": "managed_api",
      "runtime": null
    },
    "constraints": {
      "open_weights": false,
      "max_cost_per_million_input_tokens": null,
      "price_sensitivity": 0.25,
      "include_rehosts": false
    },
    "limit": 1
  },
  "applied": {
    "open_weights_only": false,
    "open_weights_required_by": null,
    "hardware_id": null,
    "max_cost_per_million_input_tokens": null,
    "cost_weight": 0.25,
    "include_rehosts": false,
    "unbound": [
      {
        "field": "environment.hosting",
        "value": "managed_api",
        "why": "a managed API imposes no weights requirement, so this narrows nothing"
      }
    ]
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
      "operator": "Sparks and Sawdust LLC",
      "rule": "Charging the consumer of a recommendation is compatible with being an honest broker. Charging the subjects of one is not.",
      "pledge": "No referral fees, no paid placement, no provider-paid visibility, permanently.",
      "permanent": true,
      "assertions": {
        "accepts_referral_fees": false,
        "accepts_paid_placement": false,
        "accepts_provider_paid_visibility": false,
        "proxies_inference_tokens": false,
        "stores_customer_prompts": false,
        "conceals_purchases_from_catalogued_vendors": false,
        "lets_supplier_models_write_supplier_cards": false
      },
      "source_neutral_at": [
        "ranking",
        "tie_breaks",
        "hosting_suggestions",
        "route_advice"
      ],
      "charges": "the consumer of a recommendation, never its subjects",
      "vendor_purchases": "We may be a paying customer of a vendor whose models we catalogue. When we are, the card says so, and no field on that vendor's card is ever set by that vendor's own model.",
      "method_source": "https://github.com/turbobeest/modelspec/blob/main/api/ranking/engine.py",
      "terms_url": "https://modelspec.dev/legal/terms/",
      "neutrality_url": "https://modelspec.dev/legal/neutrality/",
      "privacy_url": "https://modelspec.dev/legal/privacy/"
    },
    "stale_after_days": 45,
    "arena_snapshot": {
      "dataset": "lmarena-ai/leaderboard-dataset",
      "url": "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset",
      "license": "CC BY 4.0",
      "attribution": "LMArena, Arena leaderboard dataset (lmarena-ai/leaderboard-dataset), CC BY 4.0",
      "revision": "1880dbebff5ba3e2dd3865ecf6fc43539c2099db",
      "normalisation": "win_probability_vs_snapshot_leader",
      "boards": {
        "arena_elo_style_control": {
          "published": "2026-09-13",
          "leader": 1505.68
        },
        "arena_sc_coding": {
          "published": "2026-09-13",
          "leader": 1552.39
        },
        "arena_sc_hard_prompts": {
          "published": "2026-09-13",
          "leader": 1533.13
        },
        "arena_sc_math": {
          "published": "2026-09-13",
          "leader": 1526.28
        },
        "arena_sc_creative_writing": {
          "published": "2026-09-13",
          "leader": 1504.13
        },
        "arena_sc_instruction_following": {
          "published": "2026-09-13",
          "leader": 1513.49
        },
        "arena_sc_multi_turn": {
          "published": "2026-09-13",
          "leader": 1520.14
        },
        "arena_sc_expert": {
          "published": "2026-09-13",
          "leader": 1548.48
        },
        "arena_sc_longer_query": {
          "published": "2026-09-13",
          "leader": 1524.11
        },
        "arena_sc_non_english": {
          "published": "2026-09-13",
          "leader": 1495.98
        },
        "arena_sc_medicine": {
          "published": "2026-09-13",
          "leader": 1530.34
        },
        "arena_sc_legal": {
          "published": "2026-09-13",
          "leader": 1541.39
        },
        "arena_sc_business": {
          "published": "2026-09-13",
          "leader": 1517.03
        },
        "arena_sc_science": {
          "published": "2026-09-13",
          "leader": 1528.15
        },
        "arena_sc_writing": {
          "published": "2026-09-13",
          "leader": 1511.45
        },
        "arena_sc_vision": {
          "published": "2026-09-13",
          "leader": 1309.5
        },
        "arena_webdev": {
          "published": "2026-09-23",
          "leader": 1818.41
        },
        "arena_text_to_image": {
          "published": "2026-09-22",
          "leader": 1423.16
        },
        "arena_image_edit": {
          "published": "2026-09-22",
          "leader": 1525.98
        }
      }
    }
  },
  "profile": "coding",
  "ranking_status": "partial",
  "ranked_count": 48,
  "unranked_count": 1283,
  "unranked_candidates": {
    "count": 925,
    "cap": 10,
    "models": [
      {
        "model_id": "anthropic/claude-opus-5-5",
        "display_name": "Claude Opus 5.5",
        "release_date": "2026-09-22",
        "reason": "below_count_floor",
        "missing_benchmarks": [
          "arena_elo_style_control",
          "arena_sc_coding",
          "scicode",
          "swe_bench_pro",
          "swe_bench_verified",
          "terminal_bench_v4_0"
        ]
      },
      {
        "model_id": "openai/gpt-6-luna",
        "display_name": "GPT-6 Luna",
        "release_date": "2026-09-22",
        "reason": "no_scores",
        "missing_benchmarks": [
          "arena_elo_style_control",
          "arena_sc_coding",
          "arena_webdev",
          "scicode",
          "swe_bench_pro",
          "swe_bench_verified",
          "terminal_bench_v4_0"
        ]
      },
      {
        "model_id": "openai/gpt-6-sol",
        "display_name": "GPT-6 Sol",
        "release_date": "2026-09-22",
        "reason": "below_count_floor",
        "missing_benchmarks": [
          "arena_elo_style_control",
          "arena_sc_coding",
          "scicode",
          "swe_bench_pro",
          "swe_bench_verified",
          "terminal_bench_v4_0"
        ]
      },
      {
        "model_id": "xai/grok-4-7",
        "display_name": "Grok 4.7",
        "release_date": "2026-09-21",
        "reason": "below_coverage_floor",
        "missing_benchmarks": [
          "arena_elo_style_control",
          "arena_sc_coding",
          "scicode",
          "swe_bench_pro",
          "swe_bench_verified"
        ]
      },
      {
        "model_id": "stepfun/step-5-preview",
        "display_name": "Step 5 Preview",
        "release_date": "2026-09-16",
        "reason": "no_scores",
        "missing_benchmarks": [
          "arena_elo_style_control",
          "arena_sc_coding",
          "arena_webdev",
          "scicode",
          "swe_bench_pro",
          "swe_bench_verified",
          "terminal_bench_v4_0"
        ]
      },
      {
        "model_id": "deepseek/deepseek-flash",
        "display_name": "DeepSeek V4.1 Flash",
        "release_date": "2026-09-10",
        "reason": "no_scores",
        "missing_benchmarks": [
          "arena_elo_style_control",
          "arena_sc_coding",
          "arena_webdev",
          "scicode",
          "swe_bench_pro",
          "swe_bench_verified",
          "terminal_bench_v4_0"
        ]
      },
      {
        "model_id": "inception/mercury-2-5",
        "display_name": "Mercury 2.5",
        "release_date": "2026-09-08",
        "reason": "no_scores",
        "missing_benchmarks": [
          "arena_elo_style_control",
          "arena_sc_coding",
          "arena_webdev",
          "scicode",
          "swe_bench_pro",
          "swe_bench_verified",
          "terminal_bench_v4_0"
        ]
      },
      {
        "model_id": "openbmb/minicpm5-2b",
        "display_name": "MiniCPM5-2B",
        "release_date": "2026-09-06",
        "reason": "below_count_floor",
        "missing_benchmarks": [
          "arena_elo_style_control",
          "arena_sc_coding",
          "arena_webdev",
          "swe_bench_pro",
          "swe_bench_verified",
          "terminal_bench_v4_0"
        ]
      },
      {
        "model_id": "inclusionai/ling-3-0-flash-vl",
        "display_name": "Ling-3.0-flash-VL",
        "release_date": "2026-09-04",
        "reason": "below_count_floor",
        "missing_benchmarks": [
          "arena_elo_style_control",
          "arena_sc_coding",
          "arena_webdev",
          "swe_bench_pro",
          "swe_bench_verified",
          "terminal_bench_v4_0"
        ]
      },
      {
        "model_id": "anthropic/claude-mythos-5-1",
        "display_name": "Claude Mythos 5.1",
        "release_date": "2026-09-01",
        "reason": "no_scores",
        "missing_benchmarks": [
          "arena_elo_style_control",
          "arena_sc_coding",
          "arena_webdev",
          "scicode",
          "swe_bench_pro",
          "swe_bench_verified",
          "terminal_bench_v4_0"
        ]
      }
    ]
  },
  "candidates_considered": 1345,
  "authoring_guide": {
    "state": "current",
    "model_id": "google/gemini-2-5-pro",
    "why": null,
    "guide": {
      "applies_to": {
        "model_id": "google/gemini-2-5-pro",
        "version": "gemini-2.5-pro"
      },
      "as_of": "2026-09-18",
      "status": "current",
      "sections": {
        "prompt_shape": [
          {
            "text": "Google shows 2.5 Pro producing substantial programs from a single-line prompt; still state constraints when you need a bounded artefact rather than an expansive one.",
            "sources": [
              {
                "url": "https://blog.google/innovation-and-ai/models-and-research/google-deepmind/gemini-model-thinking-updates-march-2025/",
                "title": "Gemini 2.5: Our most intelligent AI model",
                "accessed": "2026-09-18",
                "kind": "release-notes"
              }
            ]
          }
        ],
        "system_message": [],
        "reasoning_and_tools": [
          {
            "text": "Gemini 2.5 Pro is a thinking model: it reasons through the problem before answering, which Google reports as the source of its coding and reasoning gains.",
            "sources": [
              {
                "url": "https://blog.google/innovation-and-ai/models-and-research/google-deepmind/gemini-model-thinking-updates-march-2025/",
                "title": "Gemini 2.5: Our most intelligent AI model",
                "accessed": "2026-09-18",
                "kind": "release-notes"
              },
              {
                "url": "https://developers.googleblog.com/en/gemini-2-5-thinking-model-updates/",
                "title": "Gemini 2.5 Pro and Flash generally available",
                "accessed": "2026-09-18",
                "kind": "provider-guidance"
              }
            ]
          },
          {
            "text": "2.5 models expose a thinking budget so you can trade reasoning tokens for latency and cost; Google made the 06-05 snapshot the stable gemini-2.5-pro id.",
            "sources": [
              {
                "url": "https://developers.googleblog.com/en/gemini-2-5-thinking-model-updates/",
                "title": "Gemini 2.5 Pro and Flash generally available",
                "accessed": "2026-09-18",
                "kind": "provider-guidance"
              }
            ]
          }
        ],
        "formatting": [],
        "failure_modes": [],
        "retry_advice": []
      }
    }
  },
  "result": [
    {
      "model_id": "google/gemini-2-5-pro",
      "display_name": "Gemini 2.5 Pro",
      "provider": "Google DeepMind",
      "score": 73.02,
      "rank": 1,
      "score_lower_bound": 73.02,
      "score_upper_bound": 87.42,
      "score_kind": "conservative_lower_bound",
      "benchmark_score": 13.45,
      "capability_score": 20.0,
      "cost_score": 17.02,
      "context_score": 7.56,
      "type_bonus": 15.0,
      "rank_status": "ranked",
      "unranked_reason": null,
      "benchmark_coverage": 0.64,
      "benchmark_count": 5,
      "required_benchmark_count": 2,
      "missing_benchmarks": [
        "swe_bench_pro",
        "terminal_bench_v4_0"
      ],
      "benchmark_estimate": 52.525972983349966,
      "benchmark_lower_bound": 13.446649083737592,
      "benchmark_upper_bound": 27.84664908373759,
      "benchmark_contributions": {
        "arena_sc_coding": 9.04,
        "arena_webdev": 0.77,
        "arena_elo_style_control": 9.94,
        "swe_bench_verified": 4.6,
        "scicode": 9.26
      },
      "off_snapshot_benchmarks": [],
      "context_window": 1048576,
      "cost_input": 1.25,
      "open_weights": false,
      "evidence_basis": "partial-verified",
      "verified_contributions": 5,
      "verified_benchmark_coverage": 0.64,
      "scores_as_of": "2026-04",
      "stale_benchmarks": [
        "swe_bench_verified"
      ],
      "oldest_live_reading": "2026-02-13"
    }
  ]
}
```

Captured 2026-09-17; `unranked_candidates` 2026-09-23. Scores move; the shape does not.

## Every error, and the fix

Every refusal carries `error.code` and `error.message`, and `result` is `[]`.

| Status | `error.code` | Cause | Fix |
|---|---|---|---|
| 400 | `invalid_request` | an unaccepted field, or the wrong type | `error.fields` names them, `error.accepted` lists what exists |
| 400 | `unknown_use_case` | no such profile | pick one from `error.accepted` |
| 400 | `unknown_hardware` | no such device id | pick one from `error.accepted` |
| 400 | `unknown_hosting` | not `local`, `self_hosted` or `managed_api` | pick one from `error.accepted` |
| 400 | `unknown_runtime` | no such platform id | pick one from `error.accepted`, or drop it |
| 401 | `missing_api_key` | no key, while keys are enforced | send one; see `error.how_to_get_a_key` |
| 401 | `invalid_api_key` | a key we do not know | check it was copied whole |
| 403 | `key_revoked` | a revoked key | get a new key |
| 404 | `not_found` | no endpoint there | use a path from `error.accepted`; paths are versioned |
| 405 | `method_not_allowed` | wrong verb for the path | `POST` to `/v1/rank`, `GET` to `/v1/health` |
| 413 | `payload_too_large` | body over 16384 bytes | a rank request is a few hundred bytes |
| 422 | `no_match` | a filter eliminated every candidate | relax `error.relax`; `error.elimination_trace` has every filter in order |
| 422 | `insufficient_evidence` | candidates survived, none has the coverage to be ordered | relaxing constraints will not help; try a broader `use_case` |
| 429 | `rate_limited` | the key's window is spent | wait until `error.resets_at`; `test_` is unlimited |
| 500 | `tier_not_configured` | ours | retry later; report it |
| 500 | `access_not_configured` | ours | retry later; report it |
| 502 | `export_unavailable` | the published export could not be read | retry; not your request |
| 503 | `access_store_not_configured` | a live key, and this deploy has no ACCESS store | use a `test_` key, or none |
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

## Keys, limits and the sandbox

**A key is optional today.** `ACCESS_ENFORCED` is off: without a key you get
the free tier, unmetered, never a 401, 403 or 429. A key you present is
checked, and a bad one is refused, not ignored. The ACCESS store is bound; no
key is issued yet. [`api-access.md`](api-access.md) has the rest.

| Tier | Daily | Burst | Live data |
|---|---|---|---|
| sandbox — any key starting `test_` | **unlimited** | unlimited | no; synthetic rows, `/v1/rank` only |
| free | 10 | 5/min | yes |
| paid | none while funded | 60/min | yes |
| dpf | unlimited | unlimited | yes |

Send `Authorization: Bearer <key>` or `X-API-Key`, never the query string.
A 429 states `limit`, `resets_at` and `retry_after_seconds`. Remaining credits
unlock policy-check [determinations](api-policy-check.md#free-and-paid); zero
balance is the free answer plus `credits.exhausted`. Prices:
[/pricing/](https://modelspec.dev/pricing/).

## Neutrality, terms and privacy

* **The neutrality commitment is live, as data:**
  [`profiles.json`](https://modelspec.dev/api/rank/profiles.json) →
  `.ranking_policy.neutrality`, and `policy.neutrality` on every `/v1/rank`
  answer. No referral fees, no paid placement, no provider-paid visibility.
  As prose: [neutrality commitment](https://modelspec.dev/legal/neutrality/).
* **Terms and privacy are in force**, adopted 2026-09-19; each page states its
  current version: [terms](https://modelspec.dev/legal/terms/),
  [privacy](https://modelspec.dev/legal/privacy/).

## Stability

`schema_version` (`"1.0"`) versions this envelope; `build.export_schema_version`
the catalogue. Widening a field's range bumps that contract's major
([`cli-contract.md`](cli-contract.md)). Fields may be added within a major:
ignore what you do not know.

A request carries a profile, never a prompt. See [`rank-api.md`](rank-api.md).

## MCP

Read-only remote MCP at `https://api.modelspec.dev/mcp`. Claude Code:

```json
{
  "mcpServers": {
    "modelspec": {
      "type": "http",
      "url": "https://api.modelspec.dev/mcp"
    }
  }
}
```
