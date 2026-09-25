# The decide API (MODEL-151)

`POST https://api.modelspec.dev/v1/decide` returns a Decision for one contract-v1
Spec. It runs `decision.engine.decide` against the signed decision Snapshot
published at `/api/decision/snapshot.json.gz`.

This is the hosted transport for the same engine as `modelspec decide`. It does
not translate a Spec into a v1 rank request, call `pipeline/ranking.py`, or keep
a separate catalogue.

## Architecture

```text
models, offerings, registry and verification records
                  |
                  v
pipeline.build --decision-snapshot-if-ready
                  |
                  v
modelspec.dev/api/decision/snapshot.json.gz
                  | fetched and verified once per Worker isolate
                  v
POST /v1/decide -> decision.contract.parse_spec -> decision.engine.decide
                  ^
                  |
          modelspec decide uses the same modules
```

`api/worker/vendor.py` copies the required `decision/`, `schema/`, and
`registry/` files byte for byte into the Worker bundle. `--check` loads the
bundle in isolation and refuses an undeclared dependency. Pydantic and PyYAML
are the Worker's declared Python dependencies.

## Request

The JSON body is a Spec from [`decision-contract.md`](decision-contract.md).
`spec_version` is the integer `1`; the current compatible contract release is
`1.1`.

```http
POST /v1/decide
content-type: application/json

{
  "spec_version": 1,
  "snapshot": "latest",
  "capabilities": {"software_engineering": "required"},
  "where": [
    "model.max_output_tokens >= 8000",
    "offering.price.input <= 3"
  ],
  "optimize": {"max": "swe_bench_pro"},
  "explain": "summary",
  "limit": 5
}
```

Unknown fields and unknown facet IDs are errors. Free-text `task` remains
unsupported in slice 1. A Spec may request `latest` or the ID of the loaded
Snapshot. Any other ID returns `409 snapshot_not_loaded` rather than silently
using different data.

The body limit is 64 KiB.

## Response

A successful body is the decision contract's Decision object without a Worker
wrapper, as compact JSON (contract 1.4). This keeps it byte-identical to the
JSON printed by `modelspec decide --json` for the same Spec and Snapshot. It is
shown indented here for reading.

```json
{
  "near_misses": [],
  "top": [],
  "chart": null,
  "number_origins": [],
  "sources": [],
  "contract_version": "1.4",
  "decision_id": "dec_0123456789abcdef01234567",
  "snapshot": "snap_0123456789abcdef",
  "spec_hash": "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
  "explain": "none",
  "status": "answered",
  "results": [],
  "may_qualify": [],
  "eliminated": {"funnel": [], "models": []},
  "constraint_costs": [],
  "tipping_points": [],
  "relax": [],
  "warnings": []
}
```

The engine sets `snapshot` from the verified loaded Snapshot. It does not copy
the request's `snapshot` value. The response changes with `explain` as defined
by the decision contract:

- `none` returns result identities and probabilities, with explanation work
  skipped.
- `summary` adds contributions, the funnel, constraint costs, and tipping
  points.
- `full` also adds per-model reasons, the top candidates' relevant values,
  provenance with each source listed once, and a chart. On the live
  snapshot's default coding task at `limit: 20` it is about 230 KB (MODEL-163;
  before 1.4 it was 7.5 MB and exhausted the Worker).

A request that exhausts the Worker's resources gets Cloudflare's own error
page (`1102`, HTTP 503, not JSON, no CORS header), not a contract error. The
decide page treats a `full` request that fails that way, or fails to connect,
as a limit: it asks once more with `explain: summary` and says the detailed
explanation was unavailable.

`no_feasible` is a valid Decision with the smallest set of conditions to relax.
It is a `200`, not a transport failure.

## Snapshot trust boundary

The site build signs the Snapshot content hash with HMAC-SHA256. The build and
Worker receive `MODELSPEC_SNAPSHOT_KEY` as a secret. The secret is never in the
Snapshot, repository, response, or Worker variables.

On the first decision request in an isolate, the Worker:

1. downloads `/api/decision/snapshot.json.gz` from `EXPORT_ORIGIN`;
2. checks its format version, canonical content hash, and Snapshot ID;
3. requires a signature and verifies it with `MODELSPEC_SNAPSHOT_KEY`;
4. builds the in-memory index and retains it for that isolate.

The Worker refuses an unsigned Snapshot, changed content, a recomputed hash
with an invalid signature, and a deployment without the verification key. A
failed verification is cached as a refusal in that isolate. It never falls
back to an older export or an unverified answer.

## Access and browser calls

The endpoint runs through the same `access.gate` and x402 wrapper as
`POST /v1/rank`. `ACCESS_ENFORCED`, `BILLING_ENABLED`, and `X402_ENABLED` remain
off in `wrangler.jsonc`. A sandbox key is refused because there is no synthetic
signed Snapshot.

Browser access is allowed only from
`https://internal.modelspec-7np.pages.dev`. The Worker echoes that exact origin
and handles its `OPTIONS` preflight. It does not send a wildcard CORS header.

## Status codes

| Status | `error.code` | Meaning | Fix |
|---|---|---|---|
| 200 | none | A Decision, including `no_feasible`. | Read `status`, `results`, `may_qualify`, and `relax`. |
| 400 | `invalid_request` | The body is not valid JSON. | Send one JSON object as the request body. |
| 400 | `invalid_spec` | The body is not a contract-v1 Spec. | Apply every item in `error.issues`; unknown fields are not ignored. |
| 404 | `origin_not_allowed` | A browser preflight came from another origin. | Call from the internal preview origin or make a server-side request. |
| 409 | `snapshot_not_loaded` | The Spec pinned a different Snapshot. | Send `latest`, use the response's loaded Snapshot ID, or retry after the requested Snapshot is deployed. |
| 413 | `payload_too_large` | The JSON body exceeds 64 KiB. | Reduce the Spec below the documented body limit. |
| 502 | `snapshot_unavailable` | The static Snapshot could not be fetched. | Retry after the static origin is healthy. |
| 503 | `no_snapshot` | Pages has not published a complete signed Snapshot. | Retry after the `Retry-After` interval. `/v1/rank` remains available. |
| 503 | `snapshot_refused` | The Snapshot is unsigned, altered, or wrongly signed. | Fix the site build or Worker secret. Never retry as if this were a valid empty answer. |

The shared access layer can also return its documented `401`, `402`, `403`,
`429`, and `503` responses. See [`api-access.md`](api-access.md) and
[`x402.md`](x402.md).

## Local parity and timing

`tests/test_decide_worker.py` builds one signed Snapshot, invokes the endpoint
adapter and `modelspec decide` for each explanation level, and compares their
serialized Decision bytes. It also discovers every `*.spec.yaml` below
`tests/recall/`, so additions to the recall set enter the same parity test.

The timing gate measures a warm isolate: load and verify once, run 10 warmups,
then time 200 `explain: none` decisions and their JSON serialization with
`perf_counter`. The fixture has 30 models, three offerings per model, and 40
benchmarks at two effort levels. On 2026-09-25, 1,000 measured calls on CPython
3.14.4 produced p50 0.617 ms, p95 0.971 ms, and max 7.202 ms. Snapshot loading
and network transfer are excluded because the Worker performs them once per
isolate.
