# The rank API (MODEL-68)

`POST https://api.modelspec.dev/v1/rank` returns a ranked shortlist for a
supplied environment, use case and constraints, computed per request from the
current published export.

This file is the design record: why the endpoint exists, how it is bundled and
deployed, and what it deliberately does not do. **Callers want
[`api.md`](api.md)** — the agent-facing reference — and
[`../api/worker/openapi.yaml`](../api/worker/openapi.yaml), which is generated
from this implementation by `api/worker/openapi.py` (MODEL-72).

This is the first piece of the enrichment layer: the origin that later carries
keys, limits and billing (MODEL-69, MODEL-73, MODEL-75). None of that is here.
Today it serves exactly the data the public export already has.

## It is not a second ranker

The endpoint imports `pipeline.ranking.rank_report` — the function
`modelspec offline rank --json` calls. `api/worker/vendor.py` copies that file
and `api/ranking/engine.py` into the Worker bundle byte for byte at build time;
neither copy is committed, so there is no second file to drift.

That is why the Worker is written in Python rather than JavaScript, which was
the obvious choice for a Worker and is the wrong one here. The acceptance
criterion is a ranking **byte-identical** to the CLI's, and a port cannot keep
that promise:

```
>>> math.log10(0.5714285714285715)   CPython  bfcf1bdeeb6548ff
                                     V8       bfcf1bdeeb6548fe
```

Four of the 121 `log10` inputs that occur in today's catalogue differ by one ULP
between the two runtimes. The composite is rounded to two decimals only *after*
those terms are summed, so a one-ULP difference can move a published score. Four
today is four too many, and nothing stops the count from growing with the next
card. A port would have had to reimplement `log10` and `round`-half-to-even
bit-exactly — which is a fork with extra steps, and a fork that looks correct.

So: same source, same arithmetic, no test vectors needed to bridge two
implementations. `tests/test_rank_worker.py` runs twelve request/argv pairs
through both the endpoint and the real CLI over the whole catalogue and compares
the serialised bytes of `result`. What it is actually testing is the *adapter* —
whether a request maps onto the scorer's arguments the way the CLI does
(`--max-cost` applied before `rank_report`, `cost_weight=price_sensitivity or
None`, `include_rehosts`, `limit`), which is where a hand-written endpoint goes
wrong.

## Architecture

```
models/*.md ──▶ pipeline/build.py ──▶ static JSON on Cloudflare Pages
                                      modelspec.dev/api/rank/{candidates,hardware}.json
                                            │  fetched per isolate, 5 min TTL
                                            ▼
                          Worker  modelspec-rank  (Python, Pyodide)
                            api/worker/src/entry.py       transport only
                            api/worker/src/rank_service.py  the answer
                            python_modules/pipeline/ranking.py   ← vendored verbatim
                            python_modules/api/ranking/engine.py ← vendored verbatim
                                            ▲
                                  POST api.modelspec.dev/v1/rank
```

The Worker holds no data. It has no KV namespace, no D1 database and no R2
bucket; it reads the same public JSON the sites and the CLI read. A request
carries a **profile** — use case, environment, constraints — and never a prompt.
Widening these fields toward prompt text is a contract change under MODEL-59,
not a feature request.

## Request

```http
POST /v1/rank
content-type: application/json

{
  "use_case": "coding",
  "environment": {
    "hardware": "apple_m3_ultra",
    "hosting":  "local",
    "runtime":  "ollama"
  },
  "constraints": {
    "open_weights": true,
    "max_cost_per_million_input_tokens": 2.0,
    "price_sensitivity": 0.25,
    "include_rehosts": false
  },
  "limit": 10
}
```

Only `use_case` is required. Any unknown field is refused rather than ignored,
so a caller never believes a constraint was applied when it was not.

| Field | Maps onto | Notes |
|---|---|---|
| `use_case` | the profile | one of `api/ranking/engine.py`'s 51 |
| `environment.hardware` | `--fits` | a device id from `/api/rank/hardware.json` |
| `environment.hosting` | `--open-weights` | `local` and `self_hosted` require downloadable weights; `managed_api` narrows nothing |
| `environment.runtime` | `--open-weights` | a local runtime implies downloadable weights; anything else is recorded and reported as **unbound** |
| `constraints.open_weights` | `--open-weights` | |
| `constraints.max_cost_per_million_input_tokens` | `--max-cost` | applied before the scorer, as the CLI applies it |
| `constraints.price_sensitivity` | `--price-sensitivity` | 0–1; every shipped profile weights cost at 0 |
| `constraints.include_rehosts` | `--include-rehosts` | |
| `limit` | `--limit` | caps the **ranked** shortlist only; 0–100 |

`applied.unbound` is the honest half of this table. The published export carries
no runtime-level evidence, so `environment.runtime: "together_ai"` is echoed back
with the reason it filtered nothing instead of being quietly turned into a guess.
A null beats a guess here as everywhere else.

## Response

Every response — success or failure — carries `build.commit` and
`build.export_schema_version` (`"3.0"`, `pipeline/export.py`), plus
`service_commit`, the sha of the deployed Worker.

```jsonc
{
  "schema_version": "1.0",
  "endpoint": "rank",
  "build": { "commit": "b1cb67d…", "built_at": "…", "export_schema_version": "3.0" },
  "service_commit": "…",
  "export_origin": "https://modelspec.dev",
  "request": { … as received, normalised … },
  "applied": { "open_weights_only": true, "open_weights_required_by": "environment.hosting",
               "hardware_id": "apple_m3_ultra", "cost_weight": 0.25, "unbound": [ … ] },
  "policy":  { "min_benchmark_coverage": 0.5, "min_benchmark_count": 2, … },
  "ranking_status": "partial",
  "ranked_count": 126, "unranked_count": 1213, "candidates_considered": 1339,
  "unranked_candidates": { "count": 848, "cap": 10, "models": [
    { "model_id": "anthropic/claude-opus-5-5", "display_name": "Claude Opus 5.5",
      "release_date": "2026-09-22", "reason": "no_scores",
      "missing_benchmarks": ["aider_polyglot", …] }, … ] },
  "authoring_guide": {
    "state": "current",
    "model_id": "openai/gpt-5-6",
    "why": null,
    "guide": { "applies_to": {…}, "as_of": "2026-09-15", "status": "current",
               "sections": { "prompt_shape": [ { "text": "…",
                 "sources": [ { "url": "https://…", "accessed": "2026-09-15",
                                "kind": "provider-guidance" } ] } ] } }
  },
  "result": [ { "model_id": …, "score": …, "cost_input": …, "evidence_basis": "mixed", … } ]
}
```

`result` rows are `pipeline.ranking.score` rows, unchanged. `evidence_basis` is
`pipeline/ranking.py::_basis` — `none`, `unverified-legacy`, `mixed`,
`partial-verified` or `verified`. It describes the provenance of the benchmark
inputs. It is **not** a quality verdict on the composite, and `verified` is not a
certificate.

`authoring_guide` is the **recommended** model's card guide (`result[0]`),
always present on a 200 and a 422. It is not on each row, so the CLI
byte-identity of `result` holds. The Worker copies what
`/api/rank/candidates.json`.`authoring_guides` already holds — MODEL-8's dated,
sourced claims — and does not generate text at request time.

| `state` | meaning |
|---|---|
| `current` | the card's guide, `status: current` |
| `stale` | the card's guide, `status: stale` (MODEL-65: pinned `identity.version` moved). Served as stale, never rewritten to current |
| `absent` | no guide to serve. `guide` is `null`, never `""` |

`why` is set only when `state` is `absent`: `no_guide` (the recommended card
has none) or `no_recommendation` (the shortlist is empty, including `limit: 0`
and a 422). `guide` is the card payload, including `applies_to`, `as_of`,
`status`, and every claim's `sources` (`url`, `accessed`, `kind`). An older
export with no `authoring_guides` map degrades to `absent` / `no_guide`.

**Payload** (measured 2026-09-18, 1,339 candidates, 6 guides, all `current`,
0 stale). `candidates.json` is 2,289,044 bytes without the map and 2,318,171
with it (+29,127, 1.3%). A `POST /v1/rank` `coding` `limit: 1` body is 3,183
bytes without `authoring_guide` and 3,294 with the absent state (+111). The
largest card guide is 7,788 bytes (`anthropic/claude-fable-5-1`). Included by
default: an opt-in would make the field absences that MODEL-59 treats as a
major bump, and the bytes do not justify it. Re-measure if the guide count
grows by an order of magnitude. None of the six guided cards is currently
rankable under any profile — today's #1 is `absent` / `no_guide` until those
cards have enough benchmark evidence. That is the catalogue, not a serving bug.

**Tier.** Public card data, same as the rest of `/v1/rank`. Free. Not a
MODEL-80 determination; nothing is read from Workers KV.

**MODEL-59.** `schema_version` stays `"1.0"`. `authoring_guide` is a new
always-present envelope field (absent is a *state*, not an omitted key).
`result` rows are unchanged. That is additive under the rule in
[`cli-contract.md`](cli-contract.md), not a range widening. A major bump here
would also bump policy-check: the two endpoints share one OpenAPI
`info.version`. `build.export_schema_version` was unmoved by that change: the new
`authoring_guides` map on `candidates.json` is an optional object, not a
widened field.

**`unranked_candidates`** (MODEL-110) names up to ten models the answer could
not rank: they passed every filter, their type is one the use case prefers, and
they lack the evidence — `reason` is `no_scores`, `below_count_floor` or
`below_coverage_floor`, with the profile benchmarks each is missing. Newest
`release_date` first, undated last. `count` is the uncapped total and never
exceeds `unranked_count`. It rides on a 200 and a 422 alike — on an
`insufficient_evidence` 422 it is the list of what would have ranked. It comes
from `rank_report`, like `result`, so `tests/test_rank_worker.py` holds it to
the CLI's bytes on every vector; the full semantics are in
[`cli-contract.md`](cli-contract.md). The Worker reads `release_date` from
`candidates.json`; an older export without it degrades to all-undated.

**MODEL-59, again.** A new always-present field, not a widened one: the
envelope stays `"1.0"`, `result` rows are unchanged, and the new
`release_date` on `candidates.json` rows leaves `export_schema_version` at
`"3.0"`.

`policy` comes from `api.ranking.engine.ranking_policy()`. The floors —
`MIN_BENCHMARK_COVERAGE = 0.50`, `MIN_BENCHMARK_COUNT = 2` — are not written
down anywhere in `api/worker/`; `tests/test_rank_worker.py` fails the build if
they ever are. Changing one is Jamie's call.

**MODEL-123.** `policy` also carries `stale_after_days` and `arena_snapshot`,
and every `result` row carries `stale_benchmarks`, `oldest_live_reading` and
`off_snapshot_benchmarks`, all from `rank_report`. The Worker reads
`evidence_dates` and `live_benchmarks` from `candidates.json` and measures
staleness from the day of the request (UTC). New fields only: the envelope
stays `"1.0"`. Semantics: [`cli-contract.md`](cli-contract.md).

### Status codes

| Code | Meaning | CLI equivalent |
|---|---|---|
| `200` | a ranking. `result` is never empty | exit 0 |
| `400` | refused: `invalid_request`, `unknown_use_case`, `unknown_hardware`, `unknown_hosting`, `unknown_runtime` | exit 1 |
| `404` | no such endpoint, the bare root included. Names `/v1/health`, `/v1/rank` and `/v1/policy-check` | — |
| `405` | `/v1/rank` and `/v1/policy-check` take POST; `/v1/health` takes GET | — |
| `413` | body over 16 KiB | — |
| `422` | **no match** — see below | exit 2 |
| `502` | the published export could not be read | — |

### A no-match is an answer

A request that eliminates every candidate returns `422` with the constraint that
did it. It never returns `200` with an empty list, because a caller cannot act on
that.

```jsonc
{
  "ranking_status": "empty",
  "error": {
    "code": "no_match",
    "message": "no model survives constraints.max_cost_per_million_input_tokens=0.0: it took the pool from 1339 to 0.",
    "eliminated_by": { "constraint": "constraints.max_cost_per_million_input_tokens",
                       "value": 0.0, "survivors_before": 1339, "survivors_after": 0 },
    "elimination_trace": [ … every filter, in the order the scorer applies them … ],
    "relax": "constraints.max_cost_per_million_input_tokens"
  },
  "result": []
}
```

Two codes, because they send a caller in opposite directions:

* **`no_match`** — a filter emptied the pool. Relax the named constraint.
* **`insufficient_evidence`** — everything survived the filters and still nothing
  could be ordered honestly. `eliminated_by.constraint` is
  `policy.min_benchmark_coverage`. Loosening the constraints will not help; the
  catalogue does not have the benchmark coverage for that use case yet. Telling
  a caller "no match" here would send them off adjusting things that were never
  the problem.

An unknown device id is a `400`, not "nothing fits your GPU" — the same call
`modelspec offline rank --fits` makes, and for the same reason: those are
different answers.

## Deploying

`.github/workflows/rank-api.yml`. Deploys on push to `main` only; pull-request
runs never reach the `deploy` job or its secrets. **No hand deploys** — the
smoke test is the only thing that proves a deploy landed.

The `bundle` job runs on every pull request and is the cheap half of the safety
net: it vendors the scorer, imports the bundle in isolation (a new third-party
import in `pipeline/ranking.py` would break the Worker, and this catches it on
the PR), runs the byte-identity suite, and builds the bundle with
`wrangler deploy --dry-run`, which needs no credential.

The `deploy` job uses `CLOUDFLARE_API_MODELSPEC_TOKEN` — Workers Scripts:Edit,
Workers KV Storage:Edit and Workers Routes:Edit on the `modelspec.dev` zone, and
nothing else. It is **not** `CLOUDFLARE_API_TOKEN` (Pages) or
`CLOUDFLARE_GRAPH_API_TOKEN` (benchgraph).

Wrangler is pinned at `4.134.0`. The `4.94.0` that `graph-service` uses ships a
workerd older than this Worker's `compatibility_date` and refuses to start it.

### The MODEL-9 lesson, applied

MODEL-9 shipped three changes whose container-side code never ran, because the
smoke test could not tell a fresh deployment from an old instance still
answering. A Worker has no container to go stale, but a smoke test that only
checks "something answered 200" has the same blind spot.

So the deploy injects `--var BUILD_COMMIT:$GITHUB_SHA`, the Worker echoes it as
`service_commit` on `/v1/health` and on every response, and the smoke test polls
for up to five minutes and **fails** unless the value it reads is the sha it just
pushed. Then it exercises the contract against the live host:

1. `service_commit == $GITHUB_SHA`, and `export_loaded` is true.
2. `GET /` → 404 naming `POST /v1/rank`, `POST /v1/policy-check` and
   `GET /v1/health`.
3. `POST /v1/rank` → 200, non-empty, `build.commit` and `export_schema_version`
   present, `evidence_basis` on every row from the documented set, and the served
   floors still 0.50 / 2.
4. a no-match vector → 422 naming the eliminating constraint.
5. an unknown use case → 400.
6. `DELETE` on any of the three endpoints → 405.
7. `POST /v1/policy-check` → 200 with a per-platform verdict on every row,
   422 for `require_no_undetermined`, 400 for an empty policy
   (`docs/policy-check-api.md`).

Each failure has its own `::error::` line saying which case it is, and appends a
digest of what it actually read: the status, the **path** that was requested —
not the URL, so a query string added by a future check cannot reach a public run
log — and the first 200 bytes of the body.
`.github/scripts/check_rank_response.py` holds (2), (3) and (4) so the
assertions are reviewable and are themselves unit-tested in
`tests/test_ci_workflows.py`.

### The second scar: a red gate on a healthy deploy

MODEL-68's own deploy of `e0265a5` failed while the Worker it had just published
was live and correct. The workflow read each response with an inline
`json.loads`; the first thing it read was Cloudflare's `error code: 522` page,
because the route had been published 100 ms earlier and had not yet reached the
edge. The `JSONDecodeError` traceback, under GitHub's default `bash -e`, ended
the step before the five-minute retry loop got a second turn — the loop existed
precisely for that wait and never ran.

Two things follow, and both are pinned by tests:

* **The workflow parses nothing.** Every read of a body goes through
  `check_rank_response.py`, which describes an unreadable response (status, path,
  first bytes) instead of raising on it. `field` exits 0 whatever it read, so a
  body the poll loop cannot parse means *retry*, never *abort*.
* **Every check targets a path the route serves.** The route now covers the whole
  host, so this is no longer a way to test Cloudflare by accident.

### DNS (Jamie, already done 2026-09-17)

The Worker uses a **route**, not a Custom Domain: a Custom Domain creates its own
DNS record and the CI token has no DNS permission. Zone `modelspec.dev`:

| Type | Name | Content | Proxy |
|---|---|---|---|
| `AAAA` | `api` | `100::` | Proxied |

`100::` is the discard prefix: nothing listens there, and a request Cloudflare
cannot match to a Worker route is proxied to it and answered `522`.

The route is therefore `api.modelspec.dev/*`, the whole host, and **not**
`/v1/*`. A narrower route would leave the bare root — and every typo, crawler and
health checker — reading a `522` that is indistinguishable from the endpoint
being down. The Worker answers those itself: a documented 404 in the same
envelope as the other errors, naming `/v1/health`, `/v1/rank` and
`/v1/policy-check`. It costs one
isolate invocation and no subrequest, because a 404 never touches the export.

A `522` from `api.modelspec.dev` now means one thing only: the route is not
bound. That is what the host returned before this Worker existed, and for a few
seconds after each deploy while the new route propagates.

## Local development

```bash
python api/worker/vendor.py --check      # assemble python_modules/, prove it imports
cd api/worker && npx wrangler@4.134.0 dev --local --var BUILD_COMMIT:dev
curl -s localhost:8787/v1/health
curl -s -X POST localhost:8787/v1/rank -H 'content-type: application/json' \
  -d '{"use_case":"coding","limit":3}'
```

`dev --local` reads the live export from `modelspec.dev`. `python_modules/` is
generated and git-ignored; rerun `vendor.py` after touching `pipeline/ranking.py`
or `api/ranking/engine.py`.

No `uv` or `pywrangler` is needed. Those exist to vendor third-party Python
packages, and this Worker has none: `compatibility_flags` carries
`disable_python_external_sdk`, which serves the `workers` SDK from the runtime
itself.

## Known limits

* One isolate holds the whole 2.2 MB catalogue in memory after parsing it. At
  1,339 models that is comfortable; it is not free, and it is the first thing to
  look at if the Worker starts hitting its memory ceiling as the catalogue grows.
* The export is cached per isolate for five minutes, so a site deploy takes up to
  that long to reach every caller. `build.commit` in the response always names
  the export actually used.
* An export from before this ticket has no `/api/rank/hardware.json`. The
  endpoint still ranks; `environment.hardware` is refused rather than answered
  wrongly, and `/v1/health` still reports the build.

## Not built (deliberately)

Keys, rate limits and the sandbox are MODEL-69. Billing is MODEL-73 and
MODEL-75. Enrichment fields — determinations withheld from the cards — are not
here: this endpoint serves the public export and nothing else.
