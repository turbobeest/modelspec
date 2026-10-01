# The decide API (MODEL-151)

`POST https://api.modelspec.dev/v1/decide` returns a Decision for one decision-contract
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
                  | verified per isolate, revalidated at most once a minute
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
`2.4`.

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

### Estate (MODEL-179)

A Spec may carry an `estate` (provider keys, subscription plans, devices, and
what is exhausted right now; see [The estate](decision-contract.md#the-estate-model-179)).
The response then also has `with_estate`, the same question answered from what
the caller holds, with a `gap` and a `gain` list; the unrestricted answer is
unchanged. It is computed inside the decision engine, so the Worker and
`modelspec decide --json` return the same bytes. The Worker does not store or
log the estate: it lives in the request body and the reply. An estate ID the
vocabulary does not list is a `400 invalid_spec` naming its path
(`estate.providers[0]`). The estate is part of `spec_hash`.

Unknown fields and unknown facet IDs are errors. Free-text `task` remains
unsupported in slice 1. A Spec may request `latest` or the ID of the loaded
Snapshot. Any other ID returns `409 snapshot_not_loaded` rather than silently
using different data.

A client that built the Spec from `/api/decision/vocabulary.json` sends that
file's `snapshot` field as the `X-ModelSpec-Snapshot` request header. The header
is optional and is not part of the Spec, so it does not change `spec_hash` or
the Decision. See [Snapshot refresh](#snapshot-refresh).

The body limit is 64 KiB.

### Comparing snapshots

`POST /v1/compare` runs one Spec against the current signed Snapshot and a
retained signed Snapshot. The body wraps the Spec because `compare_to` selects
the second Snapshot:

```json
{
  "compare_to": "snap_0123456789abcdef",
  "spec": {
    "spec_version": 1,
    "where": ["model.context_window >= 150"],
    "optimize": {"min": "offering.cost_per_task"}
  }
}
```

The response groups changes by model and includes entries, departures, changed
Must values, capability estimates, and prices with their record IDs. The
Worker reads the retained Snapshot from
`/api/decision/snapshots/<snapshot-id>.json.gz` and verifies its signature with
the same key as the current Snapshot. The static origin does not publish that
history yet. Until it does, the endpoint returns
`409 comparison_snapshot_unavailable`; local cached comparisons remain
available through `modelspec decide --compare-to`.

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
  "contract_version": "2.4",
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
decide page asks for `explain: summary` first and draws the ranking from it,
then asks for `full` in the background; if that fails, the summary stands and
only the detailed explanation is marked unavailable.

`no_feasible` is a valid Decision with the smallest set of conditions to relax.
It is a `200`, not a transport failure.

## Snapshot trust boundary

The site build signs the Snapshot content hash with HMAC-SHA256. The build and
Worker receive `MODELSPEC_SNAPSHOT_KEY` as a secret. The secret is never in the
Snapshot, repository, response, or Worker variables.

For a deployment without `bundled_data.py`, on the first decision request in
an isolate the Worker:

1. downloads `/api/decision/snapshot.json.gz` from `EXPORT_ORIGIN`;
2. checks its format version, canonical content hash, and Snapshot ID;
3. requires a signature and verifies it with `MODELSPEC_SNAPSHOT_KEY`;
4. builds the in-memory index and retains it for that isolate.

The Worker refuses an unsigned Snapshot, changed content, a recomputed hash
with an invalid signature, and a deployment without the verification key. With
no verified Snapshot held, a failed verification is cached as a refusal for one
revalidation interval, then tried again. The Worker never answers from an
unverified Snapshot.

A bundled deployment parses, hash-checks, and indexes its snapshot at module
scope, which Cloudflare captures in the deployment memory snapshot. The first
request still requires the runtime verification key and authenticates the
checked content hash before serving that index. The bundle is immutable for a
deployment, so requests reuse it without decompressing, parsing, or indexing it
again. A deployment replaces the bundled snapshot. See the phase-2 profile below.

An isolate that fetches its snapshot runs one load at a time (MODEL-153). Requests that arrive while a
cold isolate is loading wait for that load and share its outcome, a Snapshot
or an error, so a burst costs one download and one parsed Snapshot in memory.
During a refresh, requests that can answer from the held Snapshot do so
without waiting. A load older than 20 seconds (`LOAD_WAIT_SECONDS`) is
presumed dead, and the next request starts another.

## Snapshot refresh

A site deploy publishes a new Snapshot and a new `vocabulary.json` together
(MODEL-159). A warm isolate that fetches static exports picks the new Snapshot up without
a restart. Bundled deployments replace their Snapshot on the next Worker deploy.
The fetched path works as follows:

1. At most once every 60 seconds (`REVALIDATE_SECONDS`), the next decision
   request sends a conditional `GET` of the Snapshot with `If-None-Match` set
   to the stored ETag. A `304` costs no download.
2. On a `200` with different bytes, the Worker verifies the new Snapshot as
   above. Only a verified Snapshot replaces the held one, in one assignment.
3. If the refresh fails (network error, HTTP error, or a Snapshot that fails
   verification), the Worker keeps answering from the verified Snapshot it
   holds and adds `X-ModelSpec-Snapshot-Stale`, which says why. The next
   attempt is one interval later.

Every decide response from an isolate that holds a Snapshot carries
`X-ModelSpec-Snapshot`, the ID that answered. Both headers are exposed to the
browser through CORS.

### `snapshot_changed`

A page loaded before a deploy holds the old vocabulary. It can offer a
benchmark or facet the new Snapshot does not have. To stop that becoming a
confusing `400 invalid_spec`, the page sends `X-ModelSpec-Snapshot`:

- When the header names the Snapshot the isolate holds, the request proceeds.
- When it names another one, the isolate revalidates at once (at most once
  every 5 seconds, `FORCED_REVALIDATE_SECONDS`), because the site may have
  just deployed the Snapshot the caller has.
- If the IDs still differ, the Worker answers `409` before it reads the Spec:

```json
{
  "contract_version": "2.4",
  "endpoint": "decide",
  "snapshot": "snap_new0123456789ab",
  "error": {
    "code": "snapshot_changed",
    "message": "the request was built for snap_old0123456789ab, but the Worker answers from snap_new0123456789ab; reload the vocabulary and retry",
    "requested": "snap_old0123456789ab",
    "current": "snap_new0123456789ab"
  }
}
```

The decide page sends the header on every request: the summary, the
background `full`, and each next-question probe. A `snapshot_changed` on any of
them reloads `vocabulary.json` once, shared by every request that heard it, and
retries that request once with the new Snapshot ID. A second
`snapshot_changed` on the summary is shown as an error; on the background
`full` after the summary already reloaded, it leaves the summary standing
and does not reload again.

## Access and browser calls

The endpoint runs through the same `access.gate` and x402 wrapper as
`POST /v1/rank`. `ACCESS_ENFORCED`, `BILLING_ENABLED`, and `X402_ENABLED` remain
off in `wrangler.jsonc`. A sandbox key is refused because there is no synthetic
signed Snapshot.

Browser access is allowed only from `https://modelspec.dev`,
`https://www.modelspec.dev` and the preview `https://internal.modelspec-7np.pages.dev`.
The Worker echoes the exact requesting origin from that list and handles its
`OPTIONS` preflight. It does not send a wildcard CORS header.

## Status codes

| Status | `error.code` | Meaning | Fix |
|---|---|---|---|
| 200 | none | A Decision, including `no_feasible`. | Read `status`, `results`, `may_qualify`, and `relax`. |
| 400 | `invalid_request` | The body is not valid JSON. | Send one JSON object as the request body. |
| 400 | `invalid_spec` | The body is not a valid decision Spec. This includes an `optimize.weights` refinement key whose vocabulary `evidence_state` is `not_measured` or `no_benchmark`, or that the snapshot does not register. | Apply every item in `error.issues`; unknown fields are not ignored. For a refinement weight, remove the named key or use its parent domain. |
| 409 | `snapshot_changed` | `X-ModelSpec-Snapshot` names another Snapshot than the one answering. | Reload `/api/decision/vocabulary.json`, rebuild the Spec from it, and retry once with its `snapshot`. |
| 409 | `snapshot_not_loaded` | The Spec pinned a different Snapshot. | Send `latest`, use the response's loaded Snapshot ID, or retry after the requested Snapshot is deployed. |
| 409 | `comparison_snapshot_changed` | The retained Snapshot does not match `compare_to`. | Send the retained Snapshot's exact ID. |
| 409 | `comparison_snapshot_unavailable` | The origin does not publish the named retained Snapshot. | Use a locally cached Snapshot, or retry after the origin publishes Snapshot history. |
| 413 | `payload_too_large` | The JSON body exceeds 64 KiB. | Reduce the Spec below the documented body limit. |
| 502 | `snapshot_unavailable` | The static Snapshot could not be fetched. | Retry after the static origin is healthy. |
| 503 | `no_snapshot` | Pages has not published a complete signed Snapshot. | Retry after the `Retry-After` interval. `/v1/rank` remains available. |
| 503 | `snapshot_refused` | The Snapshot is unsigned, altered, or wrongly signed. | Fix the site build or Worker secret. Never retry as if this were a valid empty answer. |

## Access errors

These refusals occur before a Decision is produced. They sit outside the
closed decision-contract error enum and do not change its version. The
`human_*` responses use the same transport envelope and route as
`origin_not_allowed`, with `endpoint: decide` and `snapshot: null`.

| Status | `error.code` | Meaning | Fix |
|---|---|---|---|
| 404 | `origin_not_allowed` | A browser preflight came from another origin. | Call from a permitted site origin or make a server-side request. |
| 401 | `human_origin_required` | Keyless manual access requires a permitted site origin. | Use the paid API or MCP for machine access. |
| 403 | `human_challenge_required` | The Turnstile token is absent, invalid, expired or replayed. | Complete fresh verification before each lookup. |
| 429 | `human_burst_limit` | Three admitted lookups in a rolling minute. | Wait for `Retry-After`, then verify again. |
| 429 | `human_day_limit` | The daily allowance of 20 is spent. | Return after midnight UTC or use the paid API or MCP. |
| 429 | `human_sweep_limit` | Five lookups have four nearly equal intervals. | Wait for `Retry-After`, then verify again or use the paid API or MCP. |
| 503 | `human_gate_unavailable` | Verification, identity configuration or storage is unavailable. | Retry verification after the service recovers. |

The shared access layer can also return its documented `401`, `402`, `403`,
`429`, and `503` responses. See [`api-access.md`](api-access.md) and
[`x402.md`](x402.md).

## Local parity and timing

When a request had to load, revalidate, or wait for the Snapshot, its
successful response carries `Server-Timing: snapshot;dur=45.6` (milliseconds,
one decimal), exposed to browsers through CORS. The decision itself is not
timed in the Worker: Cloudflare freezes the clock during synchronous work, so
an in-Worker timer reads 0.0 ms however long the engine runs (MODEL-263, seen
in production on 2026-10-01). Decision latency is measured from outside, as a
round trip, and from Cloudflare's per-request CPU-time metrics (MODEL-269).

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

### MODEL-269 offline profile, 2026-10-01

Cloudflare freezes the clock during CPU work. `Server-Timing` can therefore
report zero and cannot establish the latency SLO. The offline profile uses
live timers in Node with Pyodide 0.28.3 and in CPython 3.14.4. Pyodide runs
Python 3.13.2 and its bundled Pydantic 2.10.6.

`scripts/profile_decide.py` drives `entry.Default.fetch` with the same public
card data as `measure_memory.cjs`. The ordinary memory fixture keeps the
premier lineup, 44 models and 87 candidates. Because the public catalogue is
available, this profile also builds a signed snapshot without the premier
restriction: 1,372 models, 1,415 candidates, snapshot
`snap_15b0a6fb295a206e`. It loads and verifies through the real Worker holder.
No private checkout or production signing key is needed.

The Spec asks for active text generators, software-engineering weight 1,
and limit 500, matching the reported template-1 workload. Each explanation
level has 50 warm runs. p95 is the nearest-rank 95th percentile. Phase times
are exclusive: nested filtering, ranking, and serialization are subtracted
from explanation time. JSON serialization includes Pydantic's JSON conversion
and the compact UTF-8 response. Other work includes result construction and
transport overhead. The cold first full request includes snapshot loading and
verification, but excludes runtime startup and imports. Local timings exclude
the network and do not prove the production round-trip SLO.

Before and after response SHA-256 hashes match for every explanation level in
both runtimes, including cross-runtime equality. The engine retains parsed
evidence records and benchmark tags with each snapshot. The deterministic
probability cache holds at most 16 entries and keys on the complete seed,
ordered model IDs, means, standard deviations, and sample count. The older
Pydantic serializer inspects exclusion metadata once per contract type, and
number origins dump only the sections they traverse. None of these changes
alters the Spec, ranking, probabilities, explanations, or JSON format.

All warm values below are **p50 / p95 in milliseconds**. Phase percentiles
need not add to the whole-request percentiles.

| Explain | Phase | CPython before | CPython after | Pyodide before | Pyodide after |
| --- | --- | ---: | ---: | ---: | ---: |
| none | Spec parse and validation | 0.25 / 0.34 | 0.17 / 0.20 | 0.52 / 0.74 | 0.36 / 0.66 |
| none | Filtering | 10.23 / 20.06 | 5.88 / 6.65 | 34.20 / 38.35 | 21.97 / 27.03 |
| none | Capability estimate and ranking | 0.33 / 0.44 | 0.21 / 0.28 | 0.72 / 0.85 | 0.47 / 0.64 |
| none | Tie bands and probability draws | 7.48 / 15.99 | 1.01 / 1.37 | 16.53 / 18.53 | 2.18 / 3.17 |
| none | Explanation building | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 | 0.00 / 0.00 |
| none | JSON serialization | 9.20 / 15.29 | 4.86 / 6.06 | 62.66 / 92.59 | 32.78 / 46.31 |
| none | Other Worker and engine work | 17.75 / 34.67 | 9.14 / 14.85 | 38.11 / 69.32 | 23.38 / 56.80 |
| none | Whole request | 49.34 / 66.40 | 21.65 / 27.12 | 155.84 / 194.64 | 82.34 / 118.74 |
| summary | Spec parse and validation | 0.24 / 0.37 | 0.17 / 0.23 | 0.51 / 0.95 | 0.35 / 0.47 |
| summary | Filtering | 37.98 / 51.44 | 20.93 / 22.35 | 113.62 / 150.30 | 77.34 / 104.03 |
| summary | Capability estimate and ranking | 1.06 / 1.42 | 0.65 / 0.76 | 2.21 / 2.62 | 1.51 / 1.88 |
| summary | Tie bands and probability draws | 6.81 / 11.82 | 0.99 / 1.14 | 15.69 / 18.36 | 2.14 / 2.73 |
| summary | Explanation building | 10.90 / 15.64 | 4.68 / 5.02 | 20.94 / 25.17 | 11.14 / 12.63 |
| summary | JSON serialization | 9.78 / 15.78 | 5.67 / 6.40 | 69.04 / 115.39 | 38.20 / 48.54 |
| summary | Other Worker and engine work | 16.50 / 28.72 | 8.73 / 14.94 | 37.35 / 71.49 | 24.41 / 58.50 |
| summary | Whole request | 88.72 / 105.68 | 41.92 / 49.06 | 266.42 / 322.92 | 158.07 / 195.18 |
| full | Spec parse and validation | 0.25 / 0.34 | 0.17 / 0.19 | 0.47 / 0.73 | 0.36 / 0.46 |
| full | Filtering | 37.23 / 68.68 | 20.98 / 22.35 | 109.26 / 119.91 | 76.84 / 85.77 |
| full | Capability estimate and ranking | 1.08 / 2.82 | 0.66 / 0.77 | 2.13 / 2.37 | 1.52 / 1.73 |
| full | Tie bands and probability draws | 6.71 / 30.08 | 0.99 / 1.07 | 14.60 / 16.73 | 2.19 / 2.77 |
| full | Explanation building | 23.38 / 57.50 | 11.25 / 17.04 | 46.13 / 56.05 | 28.05 / 36.95 |
| full | JSON serialization | 19.23 / 26.23 | 8.09 / 9.14 | 142.18 / 164.27 | 54.75 / 85.97 |
| full | Other Worker and engine work | 27.15 / 68.68 | 12.83 / 18.22 | 52.21 / 99.68 | 36.00 / 67.27 |
| full | Whole request | 118.96 / 236.09 | 55.81 / 62.76 | 376.11 / 439.89 | 202.82 / 244.94 |

The cold first full request has one observation per phase, in milliseconds.

| Phase | CPython before | CPython after | Pyodide before | Pyodide after |
| --- | ---: | ---: | ---: | ---: |
| Spec parse and validation | 301.32 | 147.06 | 554.16 | 313.44 |
| Filtering | 74.54 | 21.71 | 127.98 | 76.33 |
| Capability estimate and ranking | 1.05 | 0.70 | 3.23 | 1.60 |
| Tie bands and probability draws | 15.76 | 5.40 | 20.99 | 14.26 |
| Explanation building | 29.39 | 16.73 | 93.12 | 39.60 |
| JSON serialization | 22.39 | 7.78 | 282.50 | 56.45 |
| Other Worker and engine work | 100.53 | 45.23 | 211.15 | 119.38 |
| Whole request | 544.98 | 244.61 | 1293.13 | 621.07 |

To reproduce against public data from the repository root:

```sh
export MODELSPEC_SNAPSHOT_KEY=model247-memory-fixture-key
python api/worker/vendor.py --data-dir .
python scripts/profile_decide.py --build-public-snapshot /tmp/model269-full-snapshot.json.gz
python scripts/profile_decide.py api/worker/src --snapshot /tmp/model269-full-snapshot.json.gz --out /tmp/model269-cpython.json
npm install --cache /tmp/model269-npm-cache --prefix /tmp/model269-profile --no-save pyodide@0.28.3
NODE_PATH=/tmp/model269-profile/node_modules node api/worker/profile_decide.cjs api/worker/src /tmp/model269-pyodide.json /tmp/model269-full-snapshot.json.gz
```

Omit the snapshot argument to measure the ordinary public memory fixture.
Keep the same signed snapshot for before and after measurements. The JSON
reports include response hashes, response sizes, phase percentiles, and cold
phase times. Run each runtime in a fresh process. Restore the ordinary bundle
with `python api/worker/vendor.py --check` after profiling.

The deployment smoke is extended by the phase-2 measurements below.

### MODEL-269 phase 2, 2026-10-01

The Worker now imports the decision stack and loads the registry at module scope.
For bundled deployments, it also decompresses, hash-checks, parses, and indexes
the decision snapshot there. Cloudflare captures this work in the deployment
[memory snapshot](https://developers.cloudflare.com/workers/languages/python/how-python-workers-work/#deployment-lifecycle-and-cold-start-optimizations).
The first request authenticates the checked content hash with the runtime HMAC
key before serving the prepared index. Missing keys and invalid signatures still
refuse. Fetched snapshots retain their complete hash, ID, and signature checks.
Bundled data is immutable for a deployment, so forced refreshes reuse the index.
Fetched deployments retain conditional revalidation and stale-snapshot handling.

The dominant warm phase was filtering. `_unknown_disposition` previously walked
every unknown candidate and repeatedly inspected the same Pydantic condition.
A leaf has one facet and one unknown policy, so the filter now partitions its
whole unknown bitset once. Compound conditions still select unknown facets per
candidate. A per-filter cache retains each leaf's facet tuple.

The live vocabulary fetched on 2026-10-01 has 40 templates. Its first template,
`coding-best`, contains class/lifecycle conditions and `software_engineering: 1.0`.
It has no task type, capability preference, token counts, or cost objective.
The exact vocabulary spec is measured separately below, with its default limit
of 20. The supplied heavier workload description is measured with this explicit
Spec; its cost weight of 0.25 is an assumption because the supplied description
does not give that weight:

```json
{
  "spec_version": 1,
  "where": [
    "model.class = text-generator",
    "model.lifecycle = active"
  ],
  "optimize": {
    "weights": {
      "software_engineering": 1,
      "-offering.cost_per_task": 0.25
    }
  },
  "task_type": "new_feature",
  "capabilities": {
    "software_engineering": "preferred"
  },
  "task_tokens": {
    "input": 40000,
    "output": 4000
  },
  "limit": 500
}
```

Both revisions use the same signed public full-catalogue fixture from phase 1,
`snap_15b0a6fb295a206e`: 1,372 models and 1,415 candidate rows, including the archive.
Pyodide is 0.28.3 with Python 3.13.2 and Pydantic 2.10.6. Each explanation level
has five excluded warmups and 50 samples. p95 is nearest rank. The Node process
has live timers; Cloudflare's frozen clock is not used.

Cold measurements have one observation per revision. The fixture substitutes
local signed bytes for bundle retrieval, so network transfer is excluded.
Runtime startup and package loading are fresh Node/Pyodide measurements, not
Cloudflare memory-snapshot restore measurements. Deploy-time work moves out of
requests; these results do not measure Cloudflare's restore cost.

| Cold stage, heavy full response | Before ms | After ms | After execution point |
| --- | ---: | ---: | --- |
| Pyodide runtime startup | 729.93 | 702.10 | Local runtime bootstrap |
| Package loading | 100.50 | 96.65 | Local bootstrap; captured on Cloudflare |
| Other Python imports | 766.14 | 759.38 | Deploy initialization |
| Registry / first validation | 315.14 | 301.62 | Deploy initialization; request validation 1.11 ms |
| Snapshot retrieval from local fixture | 0.01 | 0.02 | Deploy initialization |
| Snapshot decompression, parse, hash checks | 48.02 | 47.18 | Deploy initialization |
| Snapshot index construction | 24.04 | 21.97 | Deploy initialization |
| HMAC computation | 0.14 | 0.09 | First request |
| First full request after module initialization | 701.52 | 229.52 | First request |
| First full request, exact vocabulary template 1 | 566.31 | 172.74 | First request |

The first-request rows include the request phases above and are not additive
with them. All warm values below are p50 / p95 in milliseconds.

| Workload | Explain | Before | After |
| --- | --- | ---: | ---: |
| Described heavy spec | none | 76.90 / 100.24 | 60.19 / 80.71 |
| Described heavy spec | summary | 164.97 / 192.35 | 112.99 / 134.72 |
| Described heavy spec | full | 222.15 / 253.16 | 167.62 / 193.49 |
| Exact vocabulary template 1 | none | 74.22 / 93.43 | 69.59 / 95.14 |
| Exact vocabulary template 1 | summary | 139.13 / 160.52 | 101.67 / 125.32 |
| Exact vocabulary template 1 | full | 169.53 / 190.97 | 130.15 / 155.98 |

| Heavy full response phase | Before | After |
| --- | ---: | ---: |
| Spec parse and validation | 0.37 / 0.45 | 0.34 / 0.38 |
| Filtering | 78.25 / 84.63 | 31.99 / 34.20 |
| Capability and ranking | 2.66 / 2.86 | 2.47 / 2.60 |
| Tie bands and probability draws | 1.58 / 1.79 | 1.52 / 1.71 |
| Explanation | 39.52 / 42.08 | 37.97 / 40.51 |
| JSON serialization | 62.67 / 89.38 | 60.31 / 81.55 |
| Other Worker and engine work | 34.59 / 61.99 | 32.59 / 53.35 |
| Whole request | 222.15 / 253.16 | 167.62 / 193.49 |

Response hashes match before and after for both profiled workloads at all three
explanation levels in Pyodide. The heavier workload's response hashes also match
across CPython and Pyodide. A separate CPython Worker replay checks all 40
vocabulary templates at limit 500: all 120 response hashes match before and after.
The public bundled memory fixture passes the steady gate at 103.43 MiB, with
a measured peak of 108.70 MiB. This memory fixture retains the ordinary premier
lineup, as in the deployment gate; timing uses the separate full-catalogue fixture.

The production measurements supplied for phase 2 remain the deployment baseline:
warm template 1 p50/p95 541/940 ms, warm template 2 209/390 ms, and immediate
post-deploy smoke 1,000/6,800 ms. Local results exclude the network and cannot
establish the production p95 ≤ 500 ms target. The new smoke measures that after
a deployment.

`profile_decide.py --spec exact-spec.json` and the optional fifth argument to
`profile_decide.cjs` select an exact JSON Spec. Reports now separate runtime
startup, package loading, import initialization, snapshot retrieval, parsing and
hash checks, index construction, HMAC computation, and the first full request.
The reproduction commands above still work. Append the Spec path to select one
of these workloads, and retain the same signed snapshot for both revisions.

`.github/scripts/check_decide_latency.py` reads `/v1/vocabulary` from the deployed
Worker and samples every template, including unavailable templates that should
produce valid `no_feasible` Decisions. By default it uses `explain: full` and
limit 500, records one initial call, excludes five warmups, then measures 20 calls
per template. `--warmups`, `--count`, `--explain`, and `--vocabulary-url` configure
the measurement. The step summary reports initial latency and warm p50/p95 for
each template. Initial calls are cold candidates; the client cannot force or
identify a fresh isolate, and even later samples can encounter one. Only warm
p95 warns against the 500 ms target. Access refusals record a skip and stop
sampling. The smoke remains warning-only and uses no new credential.
