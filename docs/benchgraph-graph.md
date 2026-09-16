# The benchgraph graph (MODEL-9)

Benchmarks as nodes in FalkorDB, served read-only from a Cloudflare Container
behind a Worker. Decision (Jamie, 2026-09-15): FalkorDB is a **read-only query
service**; `benchmarks/*.md` stays canonical.

Part 1 (this doc's code) needs no Cloudflare account. Part 2 (Cloudflare deploy)
is at the end.

## Architecture

```
benchmarks/*.md ─┐
models/*.md  ────┴─▶ CI: python -m pipeline.benchgraph_graph export --verify
   (evidence)              │  manifest.json + nodes.json + edges.json
                           ▼
                        R2 bucket  benchgraph-graph-exports (push to main only)
                           │  fetched on every container start (disk is ephemeral)
                           ▼
          Container: FalkorDB (loopback) + graph-service/service.py :8080
                           ▲  GET /graph/<allowlisted name>?params
          Worker: graph-service/worker (only /graph/*)
                           ▲
                   site / CLI ad-hoc graph queries
```

- The curation loop edits Markdown. Nothing writes to the graph except the
  loader, which replaces the whole graph from an export.
- The public sites stay static on Pages. Anything a normal page view needs stays
  in static JSON. The container answers ad-hoc graph queries only.
- This is one Worker, scoped to graph queries. It is **not** MODEL-3.

## Graph model

Graph name: `benchgraph`. Every node has `id` (and `_key`, a sha1 of `id` used
only to join edges at load time: free-text ids such as publisher names can hold
newlines that the client's parameter encoding does not match reliably).

| Node | `id` | From |
|---|---|---|
| `Benchmark` | page `id` | every page; `stub: true` for lineage targets without a page |
| `Family` | `lineage.family` | non-empty values |
| `Publisher` | `publisher.org` | non-empty values |
| `Dataset` | `dataset.url` | non-empty values |
| `Capability` | `category` | the page category (the schema has no separate capabilities list) |
| `Model` | card `model_id` | cards with `benchmarks.evidence` records |

| Edge | Direction | Properties |
|---|---|---|
| `MEASURES` | Benchmark → Capability | `declared_in`, `field` |
| `BELONGS_TO` | Benchmark → Family | `declared_in`, `field` |
| `PUBLISHED_BY` | Benchmark → Publisher | `declared_in`, `field`, `authors`, `url` |
| `USES_DATASET` | Benchmark → Dataset | `declared_in`, `field` |
| `SUPERSEDES` | Benchmark → its `lineage.predecessor`; each `lineage.successors` entry → Benchmark | `declared_in`, `field`, `pos` (lists) |
| `VARIANT_OF` | each `lineage.variants` entry → Benchmark | `declared_in`, `field`, `pos` |
| `SCORED_ON` | Model → Benchmark | `value`, `unit`, `date` (evidence_date), `date_type`, `source` (source_url), `source_kind`, `protocol` (configuration), `benchmark_version`, `model_id_as_evaluated`, `verified_at` |

Lineage edges are stored once per declaring page (`declared_in`), so A's
`successors: [B]` and B's `predecessor: A` are two edges with the same shape.
That is what lets the graph give each page back exactly what it said, including
duplicates and order.

`SCORED_ON` comes only from verified `benchmarks.evidence` records on model
cards. The flat `benchmarks.scores` dict is unverified-legacy and not in the
graph. Evidence for a benchmark with no page is skipped and counted in the
manifest.

### Mapped front-matter fields

Node properties on `Benchmark` (`a.b` is stored as `a__b`):
`id`, `name`, `aliases`, `page_kind`, `subcategory`, `status`, `summary`,
`measures`, `task_format`, `metric.name`, `metric.direction`, `metric.unit`,
`metric.max_score`, `metric.random_baseline`, `metric.human_baseline`,
`metric.baseline_note`, `dataset.size`, `dataset.size_note`, `dataset.license`,
`dataset.languages`, `dataset.modalities`, `dataset.splits`,
`dataset.public_test_set`, `paper.title`, `paper.arxiv`, `paper.url`,
`paper.year`, `leaderboard_url`, `repo_url`, `released`, `last_updated`,
`saturation.status`, `saturation.top_score`, `saturation.as_of`,
`saturation.note`, `contamination.risk`, `contamination.note`,
`harness.lm_eval`, `harness.inspect_evals`, `harness.helm`,
`harness.opencompass`, `harness.bigbench`, `harness.other`, `tags`.

Edges: `category`, `lineage.family`, `lineage.predecessor`,
`lineage.successors`, `lineage.variants`, `publisher.org`, `dataset.url`;
`publisher.authors` and `publisher.url` ride on `PUBLISHED_BY`.

When an edge field is empty (`""`, `[]`) or has an odd type, its raw value is
kept on the node as `<field>__raw` so the round trip still returns it. Values
FalkorDB cannot store (objects, YAML dates, lists with nulls) are stored as a
tagged JSON string (`@@json:`) and decoded on the way out.

### Unmapped fields (explicit allowlist, `UNMAPPED_FIELDS`)

- `sources`: citations, a list of objects. Read them from the page.
- `freshness`: research bookkeeping.
- `models_covered`: must never be authored.
- the Markdown body.
- Stray keys that are not `BenchmarkCard` fields at all (YAML parse accidents,
  for example `dataset.validation` or a sentence split into a key under
  `saturation`). They are reported by `unmapped_paths()` and not carried.

### Round trip

`tests/test_benchgraph_graph.py::test_every_benchmark_page_round_trips` loads
every page into a real FalkorDB, exports the graph back to front-matter dicts
with `read_front_matter()`, and requires every mapped field to be equal on
every page (absent and null are treated alike). Result on `0c8747c`: 1,112
pages, no loss. The fixture test covers duplicates in lists, newlines in ids,
dates, lists with nulls, empty edge fields and stray keys.

## "Still separates top models"

Named query `benchmarks_still_separating`. A benchmark qualifies when:

1. it `MEASURES` the requested capability (its `category`);
2. `saturation.status` is `open` — or `open`/`watch` with `include_watch=true`.
   `watch` is excluded by default because AUTHORING.md defines it as "the spread
   among top models has collapsed or a harder successor exists";
3. `status` is not `deprecated`, `superseded` or `saturated`;
4. if at least `top_n` models have `SCORED_ON` evidence, the spread between the
   best and the `top_n`-th best model is at least `min_spread`. Each model counts
   once, with its best score; `metric.direction` decides what best means. With
   fewer scored models the page qualifies on its saturation label alone and
   `spread` is null, unless `require_scores=true`.

Parameters: `capability` (required, category id), `include_watch` (false),
`top_n` (5, 2–20), `min_spread` (5, 0–10000), `require_scores` (false),
`limit` (100, 1–500).

Limits:

- the saturation label is an author's judgement dated `saturation.as_of`, and
  659 of 1,112 pages say `unknown`, which never qualifies;
- evidence covers only 28 benchmarks today, so most rows qualify on the label;
- spread is in the evidence's own units (percent, hours, Elo). A fixed
  `min_spread` means different things on different benchmarks, and a
  benchmark's records can mix units.

Example on the real pages (`capability=agentic&include_watch=true&require_scores=true&top_n=3&min_spread=2`):
`metr_time_horizon_50` (watch, 22 scored models, spread 660.6),
`metr_time_horizon_80` (watch, 22, 116.0), `gdpval_aa` (open, 124, 3.3).
With defaults, `capability=coding` returns `open` pages such as
`aider_polyglot`, `bigcodebench`, `bird_sql` with `spread: null`.

## Export format

`python -m pipeline.benchgraph_graph export --out dist/benchgraph-graph/ [--verify]`

- `manifest.json`: `format` (`benchgraph-graph`), `format_version` (`1.0`),
  `graph_name`, `build.commit`, `build.generated_at`, `falkordb_tested`,
  `counts` (nodes by label, edges by type, pages, stubs, skipped evidence),
  `files` (sha256 and bytes), `mapped_fields`, `unmapped_fields`, `queries`.
- `nodes.json`: `[{label, id, props}]`.
- `edges.json`: `[{type, from: [label, id], to: [label, id], props}]`.

**JSON, not an RDB dump.** An RDB file is tied to the FalkorDB module's encoding
version, so an image bump could make last night's export unloadable. JSON loads
into any FalkorDB, diffs in review, and is checked by sha256. The cost is load
time: about 3,100 nodes and 5,300 edges load in a few seconds, well inside a
cold start. Size on `0c8747c`: 6.0 MB raw (nodes 4.47 MB, edges 1.57 MB), about
1.3 MB gzipped. The FalkorDB image is still pinned (`falkordb/falkordb:v4.20.1`)
in CI and the container because the queries are tested against it.

Versioning: this is a new artefact, so under the MODEL-59 rule it is additive
and bumps nothing (`build.export_schema_version` and the CLI `schema_version`
are unchanged). Its own `format_version` starts at `1.0`; a widening of any of
its fields bumps its major, and `read_export` refuses a different major.

`--verify` loads the export into FalkorDB (`BENCHGRAPH_FALKORDB_HOST`/`PORT`,
default `localhost:6382`) and fails if any page's mapped fields do not round-trip.

## Query service and allowlist

`graph-service/service.py`, in `graph-service/Dockerfile` (FalkorDB
`v4.20.1` base, FalkorDB bound to `127.0.0.1`, no browser UI, no persistence).

On start it reads `GRAPH_EXPORT_URL` (directory path, `file://`, or `https://`
base URL), checks sha256s, loads the graph, then serves:

| Route | Returns |
|---|---|
| `GET /graph/health` | 200 `{status: ok, build_commit, format_version}`; 503 `{status: loading\|error, error: export_not_loaded}` |
| `GET /graph/manifest` | the export manifest |
| `GET /graph/benchmarks_still_separating?...` | `{build_commit, format_version, query, params, rows}` |

Anything else is 404; non-GET is 405; unknown, repeated, missing or out-of-range
parameters are 400. No Cypher comes from a request: the path selects a query from
`QUERIES`, parameters are validated and passed as Cypher parameters, and queries
run through `GRAPH.RO_QUERY`. The Worker has its own copy of the allowlist; a
test keeps the two equal.

## Run it locally

```bash
docker run -d --rm --name benchgraph-falkordb -p 127.0.0.1:6382:6379 falkordb/falkordb:v4.20.1
PYTHONPATH=$PWD .venv/bin/python -m pytest -q tests/test_benchgraph_graph.py
PYTHONPATH=$PWD .venv/bin/python -m pipeline.benchgraph_graph export --out dist/benchgraph-graph --verify
PYTHONPATH=$PWD .venv/bin/python -m pipeline.benchgraph_graph query benchmarks_still_separating capability=coding

# the container, with a local export
docker build -f graph-service/Dockerfile -t benchgraph-graph .
docker run --rm -p 8080:8080 -v "$PWD/dist/benchgraph-graph:/export:ro" \
  -e GRAPH_EXPORT_URL=/export benchgraph-graph
curl 'http://localhost:8080/graph/benchmarks_still_separating?capability=agentic&include_watch=true'

# the Worker (needs Docker; no Cloudflare login for local dev)
cd graph-service/worker && npm ci
python3 -m http.server 8766 --directory ../../dist/benchgraph-graph &   # serves the export
echo 'GRAPH_EXPORT_URL=http://host.docker.internal:8766' > .dev.vars
npx wrangler dev
```

The FalkorDB tests skip when no server is reachable; CI sets
`BENCHGRAPH_REQUIRE_FALKORDB=1` so they fail instead.

## CI

`.github/workflows/benchgraph-graph.yml`, job **Benchgraph graph export**, on
every PR and push to main. It starts `falkordb/falkordb:v4.20.1` as a service
container, runs `tests/test_benchgraph_graph.py`, builds and verifies the export,
builds the container and smoke-tests `/graph/health` (including that the image
echoes its `BUILD_COMMIT` back as `service_commit`), one query and a 404 for a
non-allowlisted route, then uploads `dist/benchgraph-graph/` as the workflow
artifact `benchgraph-graph-<sha>`. No R2 upload. It is not a required check;
`Run pytest` and `Build both sites` are unchanged.

## Part 2: Cloudflare deploy

Created by Jamie on 2026-09-15 (account "Sparks and Sawdust LLC",
`43840d11c8c4586acdba8b048414900a`, Workers Paid, Containers enabled):

- **R2 bucket** `benchgraph-graph-exports` (Standard). Public custom domain
  `graph-exports.benchgraph.dev`; r2.dev URL disabled. Layout
  `benchgraph-graph/<commit>/{nodes,edges,manifest}.json` plus
  `benchgraph-graph/latest/…`.
- **API token** `benchgraph-graph-ci`: Workers Scripts Edit, Workers Containers
  Edit, Workers R2 Storage Edit (account-wide), Workers Routes Edit on zone
  `benchgraph.dev`. Stored as the repo secret **`CLOUDFLARE_GRAPH_API_TOKEN`**.
  Do **not** store it as `CLOUDFLARE_API_TOKEN`: that secret is the Pages deploy
  token. The deploy job maps the graph secret into wrangler's
  `CLOUDFLARE_API_TOKEN` env var on that job only. `CLOUDFLARE_ACCOUNT_ID` is the
  existing secret.
- **Query host** `graph.benchgraph.dev`, zone `benchgraph.dev`.

`graph-service/worker/wrangler.jsonc` holds the account id, the route
`graph.benchgraph.dev/graph/*` on zone `benchgraph.dev`, the R2 binding
`EXPORTS` → `benchgraph-graph-exports`, and
`GRAPH_EXPORT_URL=http://graph-export.internal/benchgraph-graph/latest`.

The container does **not** fetch the public custom domain: from inside
Cloudflare Containers that load never succeeded (health stayed
`export_not_loaded` even with a named User-Agent). `GraphContainer.outboundByHost`
intercepts the container's requests to `graph-export.internal` and the Worker
serves them from the `EXPORTS` binding: GET only, and only
`benchgraph-graph/latest/{manifest,nodes,edges}.json`. No listing and no writes,
and nothing new on the public `/graph/*` route.

### Why the interception approach is correct

Checked against `@cloudflare/containers` 0.3.7 (`dist/lib/container.js`) and
Cloudflare's [outbound traffic
docs](https://developers.cloudflare.com/containers/guides/outbound-traffic/):

- Interception is transparent to the process inside the container. It is applied
  by the runtime with `ctx.container.interceptOutboundHttp(host, fetcher)`, so a
  plain `http://` request from **any** process — Python's `urllib` included —
  is routed to the handler. There is no proxy environment variable to set.
- A hostname that does not resolve publicly is the intended usage. Cloudflare's
  own docs use a fake host: "Calls to `http://my.worker` from the container
  invoke the handler, which runs inside the Workers runtime, outside the
  container sandbox."
- Only **HTTPS** interception needs `interceptHttps = true` plus the ephemeral CA
  at `/etc/cloudflare/certs/cloudflare-containers-ca.crt`. `GRAPH_EXPORT_URL` is
  `http://`, so neither is needed.
- `graph-export.internal` is matched by `outboundByHost` and everything else by
  the `outbound` catch-all, which refuses it. `allowedHosts` stays unset: it is a
  deny-by-default gate that would have to list the export host as well, and
  `blockOutbound` already denies by default while *naming* what it denied.
- `applyOutboundInterception()` runs immediately before `container.start()`, so
  interception is in place before the container's loader runs.
- `enableInternet` is **not** irrelevant, which is what the first three attempts
  at this got wrong: with it true, a request that matches no handler is fetched
  for real. That is the 530, and it is why the catch-all exists.

So the *approach* is right, and each bullet above still holds. What was wrong
was the registration, one line below all of it — see the next section.

### The 530 the container saw: `static outboundByHost` never registered

A container woken fresh on post-#79 code reported, on all 21 loader attempts:

```json
{"attempts": 21, "status": "loading",
 "last_error": {"exception": "HTTPError", "message": "HTTP Error 530:"}}
```

while `wrangler tail` logged one Worker event per attempt,
`GET http://graph-export.internal/benchgraph-graph/latest/manifest.json - Ok`.
The request reached the Worker, the Worker did not throw, and the container
still got an empty-bodied 530.

Cause, proven: **the handler was never registered.** `Container` declares
`outboundByHost` and `outbound` as static *accessor pairs*
(`@cloudflare/containers` 0.3.7, `dist/lib/container.js:272-296`) whose setters
are the only writers of the module-level registries `ContainerProxy` reads
(`outboundByHostRegistry`, `outboundHandlersRegistry`). The Worker declared

```js
static outboundByHost = { [EXPORT_HOST]: serveExport };   // inside the class body
```

and a native `static` class field **defines an own property on the subclass**
rather than invoking the inherited setter — [cloudflare/containers#247][247].
So:

- `ctor.outboundByHost` still read back the shadowing object, so
  `getHostsToIntercept()` registered `graph-export.internal` and interception
  was armed. That is the tail event;
- `outboundByHostRegistry.get(className)` in `ContainerProxy.fetch` was
  `undefined`, so no handler matched;
- per-host mode ends with `if (allowedHosts || enableInternet) return
  fetch(request);` and `enableInternet` defaults to true, so the Worker made a
  **real subrequest** for `graph-export.internal`. That name does not resolve
  publicly — by design — and Workers answers an unresolvable origin with
  [530 / error 1016][530], empty body. `Ok` in tail tracks uncaught exceptions,
  not status, so the event still read `Ok`.

`tests/test_benchgraph_graph.py::test_outbound_handlers_are_assigned_not_declared_as_static_fields`
pins all of it: the file must assign, the library must still be accessor pairs
over a registry, and the shadowing itself is demonstrated under node.

The fix is the assignment form, after the class body:

```js
GraphContainer.outboundByHost = { [EXPORT_HOST]: serveExport };
GraphContainer.outbound = blockOutbound;
```

Two hardening changes ride along, neither of them the cause:

- `blockOutbound` refuses and **names** every other HTTP host (502 plus an
  `outbound blocked:` log) instead of letting it fall through to the public
  internet. It also promotes the container to intercept-all HTTP
  (`needsCatchAllInterception`), so if the registration ever breaks again the
  symptom is that log line, not another unexplained 530. The container makes no
  other HTTP calls: FalkorDB is on loopback and the browser UI is off.
- `serveExport` buffers (`await object.arrayBuffer()`) and sets an explicit
  `content-length` instead of returning the R2 stream. Streaming a `Response`
  body across the boundary is supported, but a body with no `content-length` is
  re-framed as connection-close-delimited for the container
  ([cloudflare/containers#220][220]); the largest file is a few MB, so buffering
  costs nothing and removes the question.

`enableInternet` stays at its default. 0.3.7 still carries `// TODO: hopefully,
enableInternet can be false in a future where we enable DNS and TLS paths` beside
the start config, and the container has to resolve `EXPORT_HOST`.

[247]: https://github.com/cloudflare/containers/issues/247
[220]: https://github.com/cloudflare/containers/issues/220
[530]: https://developers.cloudflare.com/workers/platform/known-issues/

### Diagnosing a container that never loads

The container's own stdout/stderr does **not** reach `wrangler tail` — tail sees
Worker and Durable Object logs. Container logs go to the dashboard Container logs
page, which needs `observability.enabled` on the Worker (already set). Per the
[Containers FAQ](https://developers.cloudflare.com/containers/faq/#how-do-container-logs-work),
that is the only switch; the library exposes no stdout-forwarding option. So two
Worker-side channels carry the diagnosis instead:

1. **`/graph/health`** reports `service_commit` (the version the running image
   was started for) always, and the last loader failure when the export is not
   loaded — `attempts` plus `last_error: {exception, message}`. The message is
   redacted by `redact_diagnostic()`: every URL becomes `<url>` and every
   hostname, IP and port becomes `<host>`, capped at 200 characters. No stack
   trace, no environment. The `error` code stays `export_not_loaded`.
2. **`serveExport` logs every intercepted request** with its status *and byte
   count* (`export GET /path -> 200 4512B`), `blockOutbound` logs every other
   host it refuses, and `GraphContainer` logs `onStart`/`onStop`/`onError`. All
   appear in `wrangler tail`. This splits the failure modes apart:

| `wrangler tail` shows | Meaning |
|---|---|
| no `export …` line at all | the container never requested the export: interception or the loader never ran |
| `outbound blocked: GET …` | the request was intercepted but matched no handler — the host in that line is what to fix |
| `export GET … -> 404 9B` | interception works; the object is missing in R2 |
| `export GET … -> 200 0B` | the object exists but produced no bytes |
| `export GET … failed:` | the handler threw; the line carries the exception |
| `export GET … -> 200 <n>B`, health still failing | the bytes were delivered but FalkorDB ingest failed — read `last_error` |

### DNS step (Jamie, once)

The Worker uses a **route**, not a Custom Domain. A Custom Domain creates its own
DNS record, which needs DNS edit on the zone; the CI token does not have it.
Cloudflare's routes docs say every hostname a route serves must have a proxied
DNS record. Add, in zone `benchgraph.dev`:

| Type | Name | Content | Proxy |
|---|---|---|---|
| `AAAA` | `graph` | `100::` | Proxied (orange cloud) |

`100::` is the discard prefix: the route intercepts `/graph/*`, and any other
path on that host has no origin.

### CI (`deploy` job in `.github/workflows/benchgraph-graph.yml`)

Runs only on `push` to `main`, after the `graph` export job, with
`contents: read` and concurrency group `benchgraph-graph-deploy` (never
cancelled). It:

1. downloads the `benchgraph-graph-<sha>` artifact;
2. uploads `nodes.json`, `edges.json`, then `manifest.json` to
   `benchgraph-graph/<sha>/` and then `benchgraph-graph/latest/` with
   `wrangler r2 object put --remote` (manifest last, so a reader never sees a
   manifest pointing at missing files);
3. runs `npx wrangler deploy --var "BUILD_COMMIT:${GITHUB_SHA}"` in
   `graph-service/worker` (builds and pushes the container image, and records
   the deployed version — see "Rolling the container" below);
4. polls `https://graph.benchgraph.dev/graph/health` for up to 5 minutes until
   **both** `service_commit` (the running image) and `build_commit` (the loaded
   export) equal the pushed sha, then calls
   `benchmarks_still_separating?capability=coding&limit=3`. It fails with a
   DNS/route hint instead of hanging, and names the case — unreachable, never
   rolled, or rolled but the export did not load — in the `::error::` line.

### Rolling the container onto the deployed version

`wrangler deploy` replaces the Worker and the Durable Object code, but a
container instance that is already running survives and keeps serving the
previous image. `sleepAfter` is 15 min and the deploy's own smoke test polls
every 10 s, so the instance never goes idle either: #77, #78 and #79 all shipped
without their container-side change ever being exercised, and the old smoke test
could not see it. `build_commit` does not catch this — it comes from the export
the container loaded, so any restart makes it current while the code stays old.

`BUILD_COMMIT` is the deployed version:

- the deploy injects it (`wrangler deploy --var`, merged over the config vars, so
  `GRAPH_EXPORT_URL` is unaffected; `wrangler.jsonc` keeps `"dev"` for local dev);
- `GraphContainer.envVars` passes it to the container **at start**, so a
  container left from an earlier deploy still reports the earlier value;
- `graph-service/service.py` echoes it back as `service_commit` on every
  response. That is the only field that identifies the running image;
- `GraphContainer.fetch` (`graph-service/worker/src/rollout.js`) compares it with
  the Durable Object storage key `ROLLED_FOR_BUILD` and, on a mismatch, calls
  `ctx.container.destroy()` — `destroy(): Promise<void>` in
  `@cloudflare/containers` 0.3.7 (`dist/lib/container.js`: `async destroy() {
  await this.container.destroy(); }`), a SIGKILL that triggers `onStop`. The
  `super.fetch` that follows starts a fresh instance on the deployed image.
  `stop()` is the graceful twin; `destroy()` is used because the point here is to
  be decisive.

The marker is written **before** the destroy, so there is at most one roll per
`BUILD_COMMIT`. A container that starts and then fails to load its export is
never killed again on the next request — no restart loop — and the failure stays
visible as `export_not_loaded` with `attempts` and `last_error`.

The Worker also gates `/graph/health` on `service_commit`: an answer from an
older image becomes a 503 `version_rolling` instead of a 200, which keeps the two
failures apart.

| `/graph/health` says | Meaning |
|---|---|
| 503 `version_rolling` | an old image is still answering: the roll did not take |
| 503 `export_not_loaded` | the deployed image is running but its load failed — read `last_error` |
| 200, both commits equal to the sha | the deploy is live and was actually exercised |

## Not built

- No site or CLI caller of `/graph/*` yet.
- No reload of a running container when a new export lands *without* a deploy:
  the roll is keyed on `BUILD_COMMIT`, so an export-only change still waits for
  `sleepAfter`. Every export published today rides a deploy.
- No auth or rate limiting on the Worker beyond the allowlist and parameter bounds.
- `sources`, `freshness`, the Markdown body and the unverified `benchmarks.scores`
  dict are not in the graph.
- Only one named query. New ones go in `QUERIES` and the Worker's `ALLOWED`.
