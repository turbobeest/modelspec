# The benchgraph graph (MODEL-9)

Benchmarks as nodes in FalkorDB, served read-only from a Cloudflare Container
behind a Worker. Decision (Jamie, 2026-09-15): FalkorDB is a **read-only query
service**; `benchmarks/*.md` stays canonical.

Part 1 (this doc's code) needs no Cloudflare account. Part 2 is Jamie's checklist
at the end.

## Architecture

```
benchmarks/*.md ─┐
models/*.md  ────┴─▶ CI: python -m pipeline.benchgraph_graph export --verify
   (evidence)              │  manifest.json + nodes.json + edges.json
                           ▼
                        R2 bucket  (part 2; part 1 stops at a workflow artifact)
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
| `GET /graph/health` | 200 `{status, build_commit, format_version}`; 503 while loading |
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
builds the container and smoke-tests `/graph/health`, one query and a 404 for a
non-allowlisted route, then uploads `dist/benchgraph-graph/` as the workflow
artifact `benchgraph-graph-<sha>`. No R2 upload. It is not a required check;
`Run pytest` and `Build both sites` are unchanged.

## Part 2 checklist (Jamie)

1. **Workers Paid plan** on the account (Containers require it).
2. **R2 bucket** for exports, e.g. `benchgraph-graph-exports`. Layout:
   `benchgraph-graph/<commit>/…` plus `benchgraph-graph/latest/…`. Give it a
   read-only public custom domain (or r2.dev URL): the export is derived from
   public Markdown. That host is `<R2_EXPORT_HOST>`.
3. **API token** for CI, scoped to that account only:
   - Workers Scripts: Edit
   - Containers: Edit (Cloudflare's "Workers Containers" / Cloudchamber permission)
   - Workers R2 Storage: Edit, limited to the export bucket
   - (Account Settings: Read if wrangler asks for it)
   Store as `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` repository secrets.
4. **wrangler.jsonc values** in `graph-service/worker/wrangler.jsonc`:
   `account_id` = `<CLOUDFLARE_ACCOUNT_ID>`; `routes` = `<GRAPH_HOST>/graph/*` in
   zone `<ZONE_NAME>` (for example `benchgraph.dev/graph/*`, which Pages does not
   serve); `vars.GRAPH_EXPORT_URL` =
   `https://<R2_EXPORT_HOST>/benchgraph-graph/latest`; review `instance_type`
   and `max_instances`.
5. **CI upload step** (on push to main only): after `export --verify`, upload the
   three files to `benchgraph-graph/<sha>/` and then `benchgraph-graph/latest/`
   with `wrangler r2 object put`, manifest last.
6. **Deploy**: `cd graph-service/worker && npm ci && npx wrangler deploy` (builds
   and pushes the image to Cloudflare's registry). Then check
   `curl https://<GRAPH_HOST>/graph/health` reports the expected `build_commit`.
7. Decide whether a new export should restart running containers; today a
   container picks up `latest` on its next cold start (after `sleepAfter`, 15 min idle).

## Not built

- No deploy, no R2 upload, no Cloudflare resources (part 2).
- No site or CLI caller of `/graph/*` yet.
- No reload of a running container when a new export lands.
- No auth or rate limiting on the Worker beyond the allowlist and parameter bounds.
- `sources`, `freshness`, the Markdown body and the unverified `benchmarks.scores`
  dict are not in the graph.
- Only one named query. New ones go in `QUERIES` and the Worker's `ALLOWED`.
