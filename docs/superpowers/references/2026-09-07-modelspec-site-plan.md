# ModelSpec public site — draft plan

**Status:** draft for operator review, 2026-09-07. Companion to Linear DPF-22 (ModelSpec in the DPF runtime) and DPF-21 (authoring guides). Domain: `modelspec.dev`, bought through the operator's Cloudflare Registrar, zone active since 2026-09-07. Holding page deployed the same day (Cloudflare Pages project `modelspec`).

## What the site is for

Two jobs, in this order. First, answer the one question every AI builder has, "what is the best model I can actually run, for my use case, on my hardware, under my rules", from evidence that is refreshed as the models change. Second, introduce Dark Product Factories to the people who ask that question, by being visibly built and kept current by the same team. The data is open and free; the factory's own evidence (which model graduated which genre of ticket on the first pass, the budget and genre selection logic, the walk integration) stays with dpf.

## What we found when we looked for the running instance (2026-09-07)

- The repository (`turbobeest/modelspec`, MIT) holds the model cards as YAML-plus-Markdown files, the Pydantic schema, the ranking engine, the FastAPI app, the Typer CLI, the 3D graph UI, and scrapers for HuggingFace, models.dev and Artificial Analysis. There is no scheduler, and the last commit is 2026-07-21.
- On the tailnet, the two reachable Raspberry Pi 5 boards (`beestgraph`, `homelab`; 16 GB RAM, 1.8 TB disk each, Debian 13) run FalkorDB containers, but neither holds a ModelSpec graph or a ModelSpec checkout: `beestgraph` carries the operator's personal knowledge graph and its cron jobs, `homelab` a `network_intel` graph. The device named `rankmatrix` (ModelSpec's earlier name, per the licence's "ModelRank Contributors") is offline, and `dev-pi` refuses SSH under the current tailnet policy and answers nothing on the API ports. So the "ModelSpec on a Pi" instance either lives on `rankmatrix`, currently off, or on `dev-pi` behind a port we cannot see. Either way, nothing on the tailnet is serving ModelSpec today.

## Architecture recommendation: Cloudflare only for everything users touch

The graph is small. 1,469 nodes and 8,472 edges, 1,140 cards of 750 fields, is a few megabytes of JSON. That changes the hosting question: nothing about serving ModelSpec to the public or to the CLI needs a database process running somewhere.

1. **Source of truth: the GitHub repository.** Cards stay as files, edited by pull request, exactly as the contribute flow already works. Every change is reviewable and every history question is a `git log`.
2. **Build: a static export.** A build step turns the cards into versioned JSON (one file per card, plus a compact index, plus the precomputed graph for the 3D view and precomputed rankings for each use-case profile and hardware preset). Runs in GitHub Actions on every merge and on the daily research schedule.
3. **Serve: Cloudflare Pages.** The site is static: home, one page per model (the search magnet), one page per provider, one page per benchmark once the benchmark graph exists, compare pages for common pairs, the 3D graph reading the exported JSON, and the downselect wizard running client-side against the index. Pages gives HTTPS, the edge cache, the same Search Console and robots discipline as darkproductfactories.com, and zero servers.
4. **Ranking: a Worker, later.** The wizard can filter and rank client-side from the index for a long time. If the ranking engine grows beyond what a browser should do, port the four-stage pipeline to a Worker with the index in KV or R2. Still no database.
5. **The CLI: fetches the export.** `modelspec` downloads the versioned JSON snapshot from modelspec.dev (cached locally, with a freshness stamp) and ranks locally in Python, which is what dpf's ticket author will call. No dedicated compute for CLI users, and the CLI works offline against its last snapshot, the same continuity rule as the dpf library.
6. **Daily research: GitHub Actions, not a Pi.** The researcher runs on a schedule, with the Firecrawl allowlist and backoff already built for dpf's own crawl, and opens pull requests. A validation agent reviews them; a human merges; nothing auto-merges. Actions minutes are free for a public repository, there is no home hardware in the critical path, and a failed run leaves the last good data untouched.
7. **FalkorDB: a developer convenience.** Keep the Docker Compose file for local exploration and Cypher queries. It is no longer on the serving path.

## What that means for the Pi and the MacBook

- **The MacBook is a development machine, not a host.** Clone the repository locally for work; never serve from it.
- **The Pi is optional.** It can keep running FalkorDB for interactive queries and can run the research job if you prefer local compute over Actions, but the public site and the CLI must not depend on it. Before anything on a Pi is relied on, its data needs a backup off the device; `beestgraph` already has a nightly backup script that could be extended.
- **No "transfer off the Pi" is needed**, because nothing on the tailnet is serving ModelSpec now. The transfer is from "wherever the working instance was" to the repository plus the static export.

## Sequence

1. Holding page live at modelspec.dev (done 2026-09-07; custom-domain attachment pending DNS).
2. Bring the repository back to life: run `modelspec validate` and the ingest on a laptop, fix what rotted since July, tag a release.
3. Static export and Pages build, with per-model pages and the 3D graph; publish.
4. Daily research on Actions with human merge; freshness on every card.
5. Benchmark graph and per-model authoring guides (DPF-21), then the compare pages that use them.
6. dpf integration (DPF-22): setup downselect, per-ticket ranking, usage signals flowing back.

## Open questions for the operator

- Which machine held the working ModelSpec instance, and does it have data newer than the repository? If `rankmatrix` is that Pi, powering it on and exporting its cards to a pull request preserves any work not yet committed.
- Search-page scope: per-model pages only at first, or per-benchmark and compare pages from day one?
- Whether the daily research job should also file the dpf-side "model changed" tickets from the start, or after the first month of clean runs.

## Revision, 2026-09-07 evening: online-first, no Mac runtime, no Pi

Operator direction (16:26): do not run ModelSpec on the MacBook; design directly for the online instantiation from the ground up; find the cheapest way to run it, a Cloudflare Worker if possible. The `rankmatrix` device is unrelated to ModelSpec, so the "export before decommissioning" caveat above is withdrawn. The local clone at `~/dev/modelspec` is a checkout for editing and pull requests only; `wrangler dev` previews are the only thing that runs locally.

### Recommended shape: one Worker, one repository, no server

- **Repository (GitHub) holds the cards.** The 750-field schema and the 1,143 cards are the assets worth keeping; they stay YAML plus Markdown, edited by pull request, validated by the existing Actions workflow.
- **Pipeline on GitHub Actions.** Validate, export and research run on the schedule and on merge: cards become versioned JSON (one file per card, an index, the precomputed graph for the 3D view, precomputed rankings per use-case profile and hardware preset, one file per benchmark), uploaded with wrangler to R2 (versioned exports the CLI downloads) and loaded into D1 (tables for cards, benchmarks, scores, providers, platforms, edges). The researcher opens pull requests; a human merges; nothing auto-merges. Public repository, so Actions minutes are free.
- **One Worker (TypeScript) serves everything.** Static assets for the site (a page per model, provider and benchmark, the 3D graph reading the export, the downselect running in the browser), the JSON API, the snapshot endpoint, the recommender, and a remote MCP server over Streamable HTTP on the same Worker so agents call the recommender natively. The four-stage ranking engine is ported from Python to TypeScript; it is filters and weighted sums, not a graph algorithm. Python Workers exist (Pyodide) but the port is smaller than the packaging risk.
- **Storage.** D1 for queries (which models does benchmark X cover, compare A and B), KV for the hot index and rate counters, R2 for versioned exports. FalkorDB leaves the architecture entirely; the 3D graph and the benchmark graph read precomputed JSON.
- **Credentials and money.** API keys hashed in D1, issued and metered through Stripe; the agent rail answers 402 with a payment requirement and verifies the receipt; the free tier is a per-key daily allowance enforced in the Worker. Honest-broker rules from DPF-22 apply.
- **Cost.** Workers Paid at $5 per month is the realistic floor (10M requests, D1 and KV paid allowances included; the Free plan's D1 daily row limits are enforced since 2026-09-01). R2's free 10 GB covers the exports for years. Domains aside, the whole service runs for about the price of one coffee a month; there is no machine to patch.
- **Alternatives considered.** A small VM (Fly, Railway, Hetzner) running FastAPI and FalkorDB costs about the same but is a server to babysit, which the "no router operating burden" rule rules out. Vercel or Netlify plus serverless functions is equivalent to Workers but splits the estate across vendors when DNS, Pages, Registrar and the token already live at Cloudflare.

### benchgraph.dev

The operator bought benchgraph.dev on 2026-09-07 (16:33) and asked whether a live graph of every benchmark with a wiki page per benchmark (what it measures, who publishes it, the dataset and its licence, saturation, lineage, the models it covers with dated scores) adds value as a learning tool and a second front door into ModelSpec. Assessment: yes, buy and hold it; benchmark names are what people search, so per-benchmark pages are the strongest discovery surface the project has. Build those pages once, under the same Worker and export, canonical at modelspec.dev/benchmarks/<slug> at first so authority accrues to one domain, with benchgraph.dev redirecting; promote it to its own front door when the learning-tool identity proves distinct. Collision note: "Benchgraph" is also Memgraph's graph-database benchmarking tool and the name of several small developer plotting utilities; none is about AI model benchmarks, but the tagline must make the difference obvious.

### Revised sequence

1. Holding page live (done). Merge PR #4.
2. Design the online instantiation: repository restructure on a branch (`cards/`, `pipeline/`, `worker/`, `cli/`), schema kept, FalkorDB and the FastAPI/React stack retired.
3. Pipeline: validate, export to R2 and D1 on merge.
4. Worker: site with per-model, per-provider and per-benchmark pages, the 3D graph, the browser downselect; sitemap, robots, llms.txt, Search Console.
5. CLI snapshot mode (free path, no credential).
6. Daily research on Actions with human merge; freshness on every card.
7. Benchmark graph and wiki pages; benchgraph.dev redirect.
8. Authoring guides on every card (DPF-21 counterpart).
9. Recommender, remote MCP, keys and metering, agent rail, free tier (DPF-22 revenue line).
