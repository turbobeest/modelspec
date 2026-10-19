# MODEL-411 round 2 writer audit

Implementation: `44f8ca7623edbc7ae4f4d2ad51205d43d3e6065b`.
Review baseline: `3b2745368523dfe64f1ead318e1376876b406b9f`.
The [execution evidence](MODEL-411-fix.md#round-2--rev-840-changes) records tests
and gates. This file lists the persistence paths inspected for the requested
whole-repository search. References are to this branch; line numbers in worker
notes are approximate after the final edits.

## Search and scope

The search included hidden workflow files and all tracked code families, not
just the six writers named in the first design. It screened 187 non-test writer
paths, then intersected fetch/reader call sites and traced raw-content,
excerpt, cache, copy, and upload paths. Search-hit inventory appears below;
a hit alone is not a claim that the file fetches publisher pages. The detailed
tables identify the source-to-write paths actually inspected.

```sh
rg --hidden -n --glob '*.{py,ts,tsx,js,sh,yml,yaml}' --glob '!.git/**' --glob '!tests/**' --glob '!**/__tests__/**' --glob '!mcp/test/**' --glob '!web/browser-tests/**' 'write_text|write_bytes|shutil\.copy|\.write\(|open\([^\n]*["\x27][aw][b+]*["\x27]|upload-artifact|firecrawl scrape' .
rg --hidden -n --glob '*.{py,ts,tsx,js,sh,yml,yaml}' --glob '!.git/**' --glob '!tests/**' 'urlopen|httpx\.|requests\.|urllib.request|\.fetch\(|scrape\(|load_or_get|CopyStore|StoredRegions' .
rg -n 'upload-artifact|actions/cache|path:|copy|reports|sources' .github/private-writers/{curation-benchmarks,price-reread,leaderboard-refresh}.yml scripts/prepare_data_writer.py scripts/data_lag.py
```

Initial output logs are under `tmp/model-411-r2/root/`: `writer-search.txt`,
`writer-paths.txt`, `fetch-paths.txt`, `network-search.txt`, and
`retention-callers.txt`. Additional focused searches and current-file reads
traced the paths below. All probes were synthetic; no live collector or private
workflow ran.

## Shared readers, reports, and copy/upload boundaries

| Paths inspected | Result |
|---|---|
| `decision/sources.py` | HTTPX retains every response-history origin; rendered reads retain reported redirect origins. CopyStore checks shared host policy on writes and reads; cite-only writes retain URL/hash/time metadata. Rechecks cannot treat a citation as a retained copy or a verification. |
| `decision/verify.py` | Early cited outcome precedes specialized extraction and StoredRegions text access. It writes queue/result metadata, not copied regions for restricted sources. |
| `decision/firecrawl.py` | Transient rendered response adapter; no local source-text writer. Its source result feeds guarded reader/storage boundaries. |
| `scripts/price_reread.py` | CopyStore, rendered artifacts, proposal manifests and source refs carry origin metadata. Restricted HTML/text and extractor snippets are suppressed; later reads retain citation metadata. |
| `scripts/price_reread_fallback.py` | Fallback HTML/markdown and artifacts use shared origin policy; restricted results produce metadata only. Ordinary host allowlist and budget behavior remain. |
| `scripts/fetch_pricing.py` | Direct cite-only URLs refused before CLI/cache read. One CLI JSON stdout response stays transient until all metadata origins pass; only then is exact markdown written. Ordinary CLI credentials, credits, wait and main-content options preserved. |
| `scripts/benchmarks/fetch.py` | Hash and named caches use shared policy. Direct HTTP now records every redirect, including restricted intermediate hops followed by ordinary final URLs; restricted cache output is citation metadata only. Firecrawl metadata is checked before named/hash writes. |
| `scripts/benchmarks/census.py` | Newly guarded source getter prevents restricted registry/excerpt input. Search cache writes and replays replace restricted titles/descriptions/markdown with citation metadata; aggregator parsing checks all reported origins before creating leads. |
| `scripts/curation/watch.py` | Newly guarded HTTP/Firecrawl state, reuse, change classification and source export. Restricted state is URL/origins/hash/time only; known old text exports and derived report snippets cannot be revived. |
| `scripts/curation/ci.py` | Draft planning skips restricted changes before opening source_text. Dead-link issue output uses fixed status evidence, not fetched page text. |
| `scripts/curation/draft.py` | Refuses restricted current/replayed origins before reading source text, building prompts, calling drafter or writing candidate. Reused manifest rows are scrubbed for known citations. |
| `scripts/curation/propose.py` | Common proposal plan refuses restricted manifests before page copying or PR preparation. Dry-run output uses a fixed refusal rather than old copied error/kind text. No publication was run. |
| `scripts/policy/distribution_licence.py` | Shared retained-source opener rejects direct/intermediate/final restricted sources before JSON parsing or licence-file/head writes. Ordinary licence document and head unchanged. |
| `scripts/policy/audit_provider_defaults.py` | HTTPX source helper checks direct/full-history/final origins before declared licence links, LICENSE or README bodies can reach raw-text fields and derived notes. Fixed closed-provider policy labels do not fetch source pages. |
| `scripts/build_manifest.py` | No source fetching; builds local manifest from existing records. |
| `scripts/prepare_data_writer.py` | Copies the explicitly selected engine code into a private writer checkout. It does not copy publisher responses or data. |
| `scripts/data_lag.py` | Copies frozen repository data/image paths. It does not fetch publisher pages. Existing-data migration is outside this ticket. |
| `.github/private-writers/curation-benchmarks.yml` | Uploaded state and reports come from guarded watcher/export/draft paths. Actual private pins/caches/artifacts were not changed or inspected live; deployment requires adopting the new engine commit. |
| `.github/private-writers/price-reread.yml` | Rendered, fallback and source-copy uploads consume the guarded price reader outputs. The upload action does not independently fetch publisher pages. |
| `.github/private-writers/leaderboard-refresh.yml` | Audit upload consumes guarded refresh output; source-to-projection guard is covered in collector table. |
| `.github/private-writers/data-trust-audit.yml`, `.github/private-writers/release-signals.yml`, `.github/private-writers/speed-probe.yml` | Persist typed audit/discovery/measurement records. No source-page download-to-artifact route identified; release discovery/body selection traced below. Speed calls were not run. |
| `.github/workflows/test.yml`, `.github/workflows/deploy-sites.yml`, `.github/workflows/accuracy.yml`, `.github/workflows/coverage-slo.yml`, `.github/workflows/latency-probe.yml`, `.github/workflows/release-breakdown.yml` | Upload built-site/test/measurement outputs, not an independent publisher fetch/cache. Builds consume the frozen local image. |
| `.github/workflows/publish-mcp-registry.yml`, `qa/docker/Dockerfile` | Downloads are release software archives/CLI binaries, not source-page text. No changes. |
| `scripts/seo_audit.py` | HTML held transiently. Report emits status, URLs, canonical/schema findings; it does not serialize fetched body or PageReport title. |
| `pipeline/build.py`, `pipeline/render.py`, `pipeline/export.py`, `pipeline/live.py`, `pipeline/public_data.py` | Build/output writers serialize local frozen/compiled data. Smoke reads inspect endpoint status/shape; do not save publisher pages. Retained historical authored values are not migrated. |
| `cli/modelspec/snapshot.py`, `cli/modelspec/legacy.py` | Snapshot writes are typed ModelSpec snapshot/vocabulary data; legacy enrichment selects metadata into cards. Neither is a publisher-page cache. |
| `qa/agent_harness.py`, `qa/ablation.py`, `qa/ablation_proxy.py`, `qa/record_fixtures.py`, `qa/subscription_aeo.py`, `qa/subscription_ux.py`, `scripts/aeo/visibility.py` | Outputs are model/test responses, configured fixtures and metrics. External agent tool transcripts are an observation limit; no live subscription/vendor agent was run or certified as a source reader. |

## Collector paths

| Audited path | Source-to-write disposition |
| --- | --- |
| `scripts/model_143_collect.py:267` | `recheck()` retains through guarded CopyStore; line 298 reads using `store.get(..., source_url=registered_url)` before `make_facts()` and card writes. Includes a configured docs.x.ai source, which cannot supply text through this read boundary. |
| `scripts/model_143_evidence.py:62` | No live fetch. Reads existing snapshot input files, derives the source URL from the fixed filename map or snapshot metadata, and calls `CopyStore.put(..., source_url=...)` at 252. Direct restricted origins receive metadata only. Card changes contain existing evidence values and identifiers, not a fetched page body. Historical local-input provenance remains deferred. |
| `scripts/model_143_round2.py:380` | New HTTP reads use `recheck()`. Both fetched and preexisting rendered refs pass `store.get(..., source_url=...)` at 415/422 before extraction. The configured x.ai legal/function sources cannot supply page text. Later rereads at 646 use the same boundary. |
| `scripts/model_158_fable_terminal_bench.py:55` | The shared opener rejects direct, intermediate and final restricted origins before reading the fixed system-card PDF or extracting an excerpt. Projected excerpt `put()` also receives the resolved URL. |
| `scripts/model_159_requeue_dependent.py:18` | No source fetch or page read. Writes queue requeue events containing target references/value hashes from the verification log. |
| `scripts/model_160_evidence.py:417` | **Found and fixed.** Both HTTP transports use the shared per-hop opener. Rendered publisher metadata is checked separately before caching or projection. Every new projection is downstream of those guards. Ordinary caches remain reusable; unknown historical cache provenance is deferred. |
| `scripts/model_161_data.py:97` | Generic `fetch()` uses the shared per-hop opener before returning bytes. All network-backed hardware, Arena, MathArena, and MTEB projections use it; `retain()` tags every CopyStore write with its source URL. |
| `scripts/model_163_collect.py:192` | Uses `recheck()`/CopyStore. The DeepSeek text-to-table projection first calls guarded `store.get()` at 213; later source extraction does the same at 311. Other collected fact values are authored constants, not fresh quotations. |
| `scripts/model_163_evidence.py:89` | No live fetch. Input snapshot projections go through the source-aware CopyStore; existing referenced copies are read with registered URLs at 118/190 before row matching or GPQA projection. Historical input-file provenance is deferred. |
| `scripts/model_163_local.py:348` | **Found and fixed.** Both URL-based readers use the shared per-hop opener before returning JSON/text. This blocks the memory-table `cited_region` projection at the source, without changing the parser or projection format. |
| `scripts/model_174_hardware_private.py:88` | `fetch_bytes()` uses the shared per-hop opener before returning bytes. `fetch_json()` delegates to it. Hardware metadata and private-deployment source copies use these readers and source-aware `put()` calls. |
| `scripts/model_174_verify_derived.py:145` | No network fetching or page-copy writer. Existing source bodies pass registered URLs to `store.get()` at 173/215 before derived/private checks. Writes verification and queue records, not extracted page copies. |
| `scripts/model_175_add_speed_facts.py:80` | No network or source-body reading. Appends generated missing-speed fact YAML based on existing offering metadata and registered source IDs. |
| `scripts/model_191_refinements.py:287` | `_copies()` delegates HTTP fetching and derived retention to `model_160_evidence.Registry`; the corrected upstream refusal covers its Arena projections. Benchmark page prose is authored locally. |
| `scripts/model_191_verify_existing.py:106` | `_fetch()` uses the shared per-hop opener before returning bytes. PDF/HTML excerpt generation occurs afterward; the excerpt `put()` receives the resolved URL. |
| `scripts/model_192_evidence.py:49` | Fetches a fixed ordinary Finance Benchmark URL through the shared per-hop opener before reading/parsing. Raw and projected copies are source-tagged. The original URL is a code constant, not a generic caller parameter. |
| `scripts/model_201_collect.py:651` | No live fetch or CopyStore body extraction. Checks presence of fixed historic copies, then serializes authored plan constants/existing fact values and claims. Existing quote constants are not newly extracted publisher text; their migration is deferred. |
| `scripts/model_205_collect.py:309` | Same static-plan pattern: no live fetch or body extraction; `store.has()` checks historic refs and writes authored plan/quote constants. Includes Perplexity authored values, but does not download or extract new Perplexity quotations. |
| `scripts/model_233_evidence.py:267` | `retain()` delegates fetching to `_fetch()`, which uses the shared per-hop opener. PDF excerpt extraction occurs afterward; CopyStore also receives the resolved URL. |
| `scripts/model_233_matharena.py:136` | Uses guarded `refresh_leaderboards._fetch()` before raw/projected CopyStore writes. No alternate fresh fetch path. |
| `scripts/model_233_thin_templates.py:26` | Builds a local snapshot and prints template outcome counts. No network, publisher page reading, raw cache, or quotation extraction. |
| `scripts/model_235_recite.py:46` | No live fetch. Reuses a fixed existing source ref through `StoredRegions`/`verify()` and refuses to write recitations unless verification succeeds. Does not copy or extract new page text. |
| `scripts/model_344_lab_jurisdiction.py:281` | Reads supplied local fetch files, not the network. `retain()` refuses each source URL before CopyStore ingestion, including configured x.ai terms. `main()` reaches this refusal before lab-registry writes. `check_regions()` reads local files earlier but performs no page-text disk write. |
| `scripts/model_345_collect.py:533` | Fetches via `recheck()`. Licence and README text must pass source-aware `store.get()` before rule/quote checks. Report quotations are authored readings checked against those guarded bodies, so a new restricted fetch cannot supply text to this output path. |
| `scripts/model_348_architecture.py:265` | Fetches API/config/README through `recheck()` and obtains all extraction text through `StoredRegions.text()`. Restricted URL/marker cases return no source text, so architecture quote diagnostics cannot extract new restricted content. |
| `scripts/model_360_openai_jurisdiction.py:280` | No live fetch. Ingests one explicitly supplied local foundation-page file under a fixed ordinary source URL through CopyStore. Registry updates use authored jurisdiction values. This is local historical-input handling, not an arbitrary fresh-URL downloader. |
| `scripts/collect_claude_sonnet_5_5.py:118` | Its shared httpx fetcher refuses the original URL and every reported response-history/final URL before returning bytes. All raw, launch, pricing-table, and fact-source projections at 595–599 use that fetcher, then source-aware CopyStore. |
| `scripts/migrate_oll_evidence.py:165` | `_get()` refuses direct restricted origins before cache lookup and uses the shared per-hop opener before new cache writes/return. `_published()` builds raw/row copies only afterward. Existing ordinary cache files without redirect metadata remain unchanged and deferred. |
| `scripts/refresh_leaderboards.py:1024` | All live board collection uses `_fetch()`, which enforces allowed-source policy and then uses the shared per-hop opener before returning bytes. `_reading_from_projection()` and raw-copy writes are downstream and source-tagged. Saved input readings are historical local artifacts, not a new fetch bypass. |

The urllib source readers in the changed collector paths use
`decision.retention.open_retained_source`, which refuses each restricted hop
before following it. Model 191 refinements and model 233 MathArena inherit the
shared guarded fetchers. HTTPX/rendered paths check full available metadata.
Ordinary historical caches without origin metadata are not reconstructed or
mass-refetched; their migration remains MODEL-409.

## Other enrichment and orchestration paths

| Entry point | Fetch and persistence path | Disposition |
| --- | --- | --- |
| `scripts/fetch_ranking_leaderboards.py` | `main` reads the fixed Arena URL through `load_or_get` at line 604, and optional Firecrawl through shared `scrape` at line 620. Shared cache writes use `cite_only_origin` in `scripts/benchmarks/fetch.py:333` and `:504`; existing cache reads check origin metadata at `:351` and `:401`. `extract_arena` at line 228 selects model names, ratings and dates. `to_ledger_row` at line 500 emits those values, URLs and fixed configuration prose. Lines 694–700 write the ledger, ID mapping and refusal report. | Raw HTML/markdown persistence is delegated to guarded shared caches. Local output contains selected factual values and generated reasons, not an extracted page or prose excerpt. Error reports retain exception text, not an explicit successful page payload. No separate bypass found here. |
| `scripts/enrich_cards.py` | No network fetch. `enrich_capabilities` at line 67 derives flags from existing card type. `write_card_yaml` at line 143 serializes the existing card, including its existing `prose_body`, at line 180. | Local card transformation. No newly fetched body or excerpt. Existing authored prose is preserved. |
| `scripts/enrich_costs.py` | No network fetch. `enrich_cost` at line 485 reads the in-module numeric mapping and assigns a fixed cost note at line 502. `enrich_availability` at line 505 assigns platform fields. `write_card_yaml` at line 556 writes these values and existing card prose at line 590. | Local factual enrichment and fixed prose. No fetched text persistence. |
| `scripts/enrich_open_llm.py` | `try_fetch_open_llm_api` at line 41 reads fixed Hugging Face dataset/Gradio endpoints into memory. `_parse_dataset_response` at line 107 and `_parse_gradio_response` at line 162 select model keys and numeric benchmark scores. `enrich_card` at line 389 writes floats and fixed source/date labels; `main` calls the shared card serializer at line 483. | No response-body cache or excerpt write. Only selected model identifiers/scores survive the fetch. Existing card content is serialized unchanged apart from enrichment. |
| `scripts/enrich_ollama.py` | `try_fetch_ollama_models` at line 88 reads API model names/tags or matches `/library/<identifier>` links in transient HTML at line 139. `enrich_card_ollama` at line 342 assigns booleans, model tags and constructed Ollama URLs. `save_card` at line 379 delegates to the card serializer. | Identifiers and availability facts only. No HTML, description, snippet or other fetched prose is written. |
| `scripts/enrich_benchmarks.py` | `try_fetch_live_arena_data` at line 840 reads fixed endpoints into memory. `_parse_arena_response` at line 873 selects a normalized model name and float rating. `enrich_card` at line 784 fills numeric scores and fixed metadata; line 956 serializes the card. | No raw response persistence. Numeric scores and generated labels are the newly written data. |
| `scripts/enrich_mteb.py` | `try_fetch_mteb_data` at line 286 reads fixed Hugging Face endpoints. `_parse_mteb_response` at line 317 selects model keys and float scores. `enrich_card_mteb` at line 364 fills those scores and fixed source labels, then uses the shared card serializer. | No raw JSON/page cache or excerpt write. Selected benchmark facts only. |
| `scripts/policy/verify_quotes.py` | `as_text` at line 41 reads and strips the page in memory. `main` at line 72 compares it with pre-existing `READINGS` quotes. Failure output at lines 95–97 prints a missing segment from the existing reading, not a segment extracted from the fetched document. No file writer exists. | Transient reread. It can echo an already-authored quote on failure, but does not acquire and persist a new page excerpt. Existing quote migration is separate from this audit. |
| `scripts/benchmarks/downselect.py` | No network fetch. `build_report` at line 44 validates local evidence and invokes `schema.benchmark_eligibility.evaluate`. That function returns selected result fields, source URLs and computed reasons at lines 283–303. `main` writes the report at line 91. | Local evidence projection. It preserves factual configuration fields already in supplied evidence; it does not fetch or copy a source document. |
| `scripts/benchmarks/next_batch.py` | No network fetch. Reads local queue/evidence/card identifiers. Lines 145–169 select name, aliases, source names/URLs, harness/category hints and a fixed explanatory note. Line 173 writes the batch JSON. | Local queue projection, no page/excerpt persistence. |
| `scripts/benchmarks/queue_p1.py` | No network fetch. Reads existing card scores and source/date labels at lines 37–62. Lines 66–76 build selected model/score/source/date metadata; lines 82 and 103 write queue and slices. | Local factual aggregation. No fetched page or authored source excerpt is introduced. |
| `scripts/benchmarks/run_eligible.py` | No built-in HTTP fetch. Lines 140–142 save a backup of the existing authored benchmark page. Lines 164–177 copy local eligibility/reference records. Writer/reviewer prompts require opening sources; `run_logged` at lines 54–65 redirects all subprocess stdout/stderr to files. Commands request `streaming-json` and `permission-mode auto` at lines 178–192 and 227–241. | Existing-page/evidence copies are local authored inputs. This script is not a source-page downloader. The external CLI transcript is an observation limit, not a guarded reader or demonstrated page leak; see below. |
| `scripts/release_watch.py` | `http_fetch` at line 50 returns response bytes in memory to `release_signals.watch`. Baseline output contains IDs at line 245. Reports at lines 298–301 contain counts, statuses, identifiers and URLs. `post_discoveries` at line 73 and `file_issues` at line 107 upload parsed `ReleaseSignal` values and fixed issue prose, not the source body. | Selected discovery facts only. Upload destinations are the signal API/GitHub, with no source body included. Their non-success response details can be logged, but those are service responses, not the watched source page. |
| `release_signals/watch.py` | `extract` at line 160 routes transient JSON/HTML to parsers. `_page` at line 169 retains matched model-ID tokens; `_openrouter`/`_huggingface` at lines 192/213 retain IDs and dates. `write_baseline` at line 150 writes only source-to-ID sets. `discoveries` at line 328 creates a typed signal from name, provider, URL, timestamp and confidence. `_robots_once` at line 302 is an in-memory dictionary. | No page-body, snippet or persistent robots cache. Only selected discovery fields leave the reader. |
| `release_signals/pipeline.py` | `_fetch_allowed` at line 185 returns transient fetched data. `_primary_identity` at line 287 examines JSON-LD/visible text but returns only model name/date at lines 337 and 353. `gather_signal` at line 424 returns these selected values and URLs. `update_existing_card` at line 508 writes URL/date metadata and preserves existing authored body. `draft_signal` at line 555 writes fields plus fixed prose at lines 610–621. | Source prose is inspected but is not copied. The new card sentence is generated from a model name, URL and read date. No source-body cache or excerpt field. |
| `scripts/process_release_signals.py` | `_fetch` at line 32 returns body bytes in memory, validating requested/final source URLs. `process` at line 98 invokes the preceding gather/draft paths and writes IDs, status, URLs, counts and generated diagnostics at lines 154, 193 and 221. It also invokes `refresh_leaderboards.run` at lines 162 and 201. That reader calls `open_retained_source` at `scripts/refresh_leaderboards.py:1029`, refusing direct, intermediate and final restricted origins before returning content, and its raw/projected persistence uses `CopyStore` at lines 1230 and 1044. | No additional page-copy writer in this wrapper. The indirect leaderboard-copy boundary is guarded by its shared fetch refusal and CopyStore. This audit inspected those calls, not every leaderboard projector again. |

## Seed and metadata helpers

| Exact path and relevant lines | Persistence disposition |
|---|---|
| `scripts/seed_models_dev.py:194`, `:643`, `:750`, `:997` | Fetches structured models.dev JSON into memory. The builder selects identity, modalities, limits, costs, booleans and source URLs. `_build_prose()` uses fixed templates around factual names/family/knowledge-date fields. The writer serializes the constructed card, not the raw response, page HTML, markdown, description or a source excerpt. No raw-page/excerpt writer found. |
| `scripts/seed_huggingface.py:93`, `:137`, `:494`, `:740` | Fetches Hub API model metadata. Selected identifiers, tags, licence enum, parameter count, dates, deployment and adoption fields populate a card. Prose is a fixed metadata-origin sentence. `write_card_yaml()` writes only that constructed card. No README download, raw API cache or copied page excerpt found. |
| `scripts/fetch_geometry.py:731`, `:769`, `:793`, `:804`, `:1003`, `:1080` | Holds config JSON and README text transiently. README parsers return numeric parameter values plus fixed extraction-reason labels; base-model reads return identifiers. `_write_architecture()` writes selected numeric geometry, preserving the existing card body. Reports contain numeric gains/conflicts, statuses, identifiers and fixed provenance/refusal strings. No raw config/README or quoted span is written. |
| `scripts/fetch_total_parameters.py:313`, `:412`, `:572`, `:667`, `:691` | Reuses transient Hub/config/README fetching. `_resolve_total()` retains a numeric total, source label, repository IDs and fetch-status trail. Architecture patches and the JSON report contain these factual metadata fields, not README prose or excerpts. No raw-page/excerpt writer found. |
| `scripts/resolve_huggingface.py:160`, `:211`, `:249`, `:273`, `:281` | Hub search JSON remains in memory. Only selected repo ID, download count, calculated confidence and locally generated reason labels enter the resolution report; `_write_repo_id()` updates the Hub ID/URL/available fields. No search snippets, README, page text or full response cache is retained. |

## Observation limits

- `scripts/benchmarks/run_eligible.py` saves external CLI stdout/stderr and asks
  that agent to open sources. It is not itself a publisher downloader. If the
  external CLI emits page text, its transcript can contain it; no code-level
  retention guarantee for that external runtime is claimed. No live CLI/source
  run or transcript inspection was performed. The same limit applies to
  general agent-test transcript writers above. This is not presented as a
  reproduced deterministic publisher-copy path or as a guarded reader.
- Third-party scrapers must report origin metadata for indirect publisher
  origins to be recognized. The local CLI output routing and synthetic metadata
  were inspected/tested; live service/browser cache behavior was not observed.
- Historical source copies, local supplied snapshots, authored quotations and
  ordinary caches with missing provenance remain the separate MODEL-409
  migration. Known reused curation outputs and search-cache rows are guarded;
  no blanket historical deletion was performed.
- Private workflows must adopt a commit containing these guards. No deployment,
  private data edit, Actions cache inspection, artifact upload or production
  policy switch occurred.

## Whole-repository writer-search hits

These are the 187 initial non-test writer-search hits. They include local
renderers, generators, test harnesses and historical evidence scripts in
addition to fetched-source writers. The tables above state the meaningful
fetch-to-persistence dispositions; this inventory is not a blanket assertion
that every hit handles live source content.

```text
./.github/private-writers/curation-benchmarks.yml
./.github/private-writers/data-trust-audit.yml
./.github/private-writers/leaderboard-refresh.yml
./.github/private-writers/price-reread.yml
./.github/private-writers/release-signals.yml
./.github/private-writers/speed-probe.yml
./.github/scripts/check_decide_latency.py
./.github/workflows/accuracy.yml
./.github/workflows/coverage-slo.yml
./.github/workflows/deploy-sites.yml
./.github/workflows/latency-probe.yml
./.github/workflows/release-breakdown.yml
./.github/workflows/test.yml
./api/worker/instrument_startup.py
./api/worker/load_determinations.py
./api/worker/memory_fixture.py
./api/worker/openapi.py
./api/worker/vendor.py
./cli/modelspec/auth.py
./cli/modelspec/cli.py
./cli/modelspec/decide_cmd.py
./cli/modelspec/legacy.py
./cli/modelspec/outcome.py
./cli/modelspec/outcome_cmd.py
./cli/modelspec/setup.py
./cli/modelspec/snapshot.py
./cli/modelspec/snapshot_build_cmd.py
./decision/schema.py
./decision/snapshot.py
./decision/sources.py
./decision/verify.py
./docs/evidence/g2-ios/MODEL-235-readers-replay.py
./docs/evidence/g2-ios/MODEL-367/snapshot_size.py
./docs/evidence/g2-ios/MODEL-395-engine/mutations.py
./docs/evidence/g2-ios/MODEL-404/gates/generate-screenshot-decisions.py
./docs/evidence/g2-ios/MODEL-404/routing/round3/generate-display-vocabulary.py
./docs/evidence/g2-ios/MODEL-404/routing/round3/post819/audit-generated.py
./docs/evidence/g2-ios/MODEL-404/routing/sync/audit-artifacts.py
./docs/evidence/g2-ios/MODEL-407/inspect-public-bundles.py
./docs/evidence/g2-ios/MODEL-407/round3/profile_snapshot.py
./docs/evidence/g2-ios/MODEL-orchestrator-recipe-r2/flag-off-audit.py
./graphify-out/build_artifacts.py
./graphify-out/prepare_scope.py
./mcp/scripts/registry_manifest.py
./pipeline/about.py
./pipeline/agent_copy.py
./pipeline/agent_ready.py
./pipeline/blog.py
./pipeline/blog_indexnow.py
./pipeline/brand.py
./pipeline/brand_page.py
./pipeline/build.py
./pipeline/class_export.py
./pipeline/comparison_pages.py
./pipeline/coverage.py
./pipeline/export.py
./pipeline/feedback_page.py
./pipeline/guides.py
./pipeline/holding.py
./pipeline/hosts.py
./pipeline/landing.py
./pipeline/legal.py
./pipeline/live.py
./pipeline/method.py
./pipeline/orchestrators.py
./pipeline/policy_export.py
./pipeline/pricing.py
./pipeline/public_data.py
./pipeline/ranking.py
./pipeline/render.py
./pipeline/social_cards.py
./pipeline/structured_data.py
./pipeline/surface_lint.py
./qa/ablation.py
./qa/ablation_proxy.py
./qa/agent_harness.py
./qa/contracts.py
./qa/decide_budget.py
./qa/install_subscription_jobs.py
./qa/latency_probe.py
./qa/record_fixtures.py
./qa/subscription_aeo.py
./qa/subscription_jobs.py
./qa/subscription_ux.py
./qa/tui_auth.py
./qa/tui_docker.py
./qa/tui_harness.py
./qa/tui_inventory.py
./qa/tui_isolation.py
./qa/tui_providers.py
./release_blog/__main__.py
./release_blog/model.py
./release_blog/pipeline.py
./release_blog/platforms.py
./release_blog/render.py
./release_signals/pipeline.py
./release_signals/watch.py
./scripts/accuracy.py
./scripts/accuracy_alert.py
./scripts/add_domain_benchmarks.py
./scripts/add_domain_benchmarks_wave2.py
./scripts/aeo/surface_drift.py
./scripts/aeo/visibility.py
./scripts/attach_evidence.py
./scripts/attribution.py
./scripts/benchmarks/census.py
./scripts/benchmarks/downselect.py
./scripts/benchmarks/fetch.py
./scripts/benchmarks/next_batch.py
./scripts/benchmarks/queue_p1.py
./scripts/benchmarks/run_eligible.py
./scripts/build_manifest.py
./scripts/capability_calibration.py
./scripts/capability_validate.py
./scripts/card_updates.py
./scripts/chart_check.py
./scripts/chart_check_pr.py
./scripts/classify_unmapped_leaderboard_names.py
./scripts/collect_claude_sonnet_5_5.py
./scripts/curation/ci.py
./scripts/curation/draft.py
./scripts/curation/propose.py
./scripts/curation/watch.py
./scripts/data_lag.py
./scripts/data_trust/report.py
./scripts/decide_dev_server.py
./scripts/enrich_cards.py
./scripts/enrich_costs.py
./scripts/eval_attribution.py
./scripts/eval_cost_to_correct.py
./scripts/feedback/digest.py
./scripts/feedback/export.py
./scripts/fetch_geometry.py
./scripts/fetch_pricing.py
./scripts/fetch_ranking_leaderboards.py
./scripts/fetch_total_parameters.py
./scripts/independent_review.py
./scripts/migrate_benchmarks_to_dict.py
./scripts/migrate_oll_evidence.py
./scripts/model_143_collect.py
./scripts/model_143_evidence.py
./scripts/model_143_round2.py
./scripts/model_158_fable_terminal_bench.py
./scripts/model_160_evidence.py
./scripts/model_161_data.py
./scripts/model_163_collect.py
./scripts/model_163_evidence.py
./scripts/model_174_hardware_private.py
./scripts/model_175_add_speed_facts.py
./scripts/model_191_refinements.py
./scripts/model_191_verify_existing.py
./scripts/model_192_evidence.py
./scripts/model_201_collect.py
./scripts/model_205_collect.py
./scripts/model_233_evidence.py
./scripts/model_233_matharena.py
./scripts/model_235_recite.py
./scripts/model_344_lab_jurisdiction.py
./scripts/model_345_collect.py
./scripts/model_348_architecture.py
./scripts/model_360_openai_jurisdiction.py
./scripts/package_smoke.py
./scripts/package_smoke_fixture.py
./scripts/policy/audit_provider_defaults.py
./scripts/policy/distribution_licence.py
./scripts/premier_slice1.py
./scripts/prepare_data_writer.py
./scripts/price_reread.py
./scripts/price_reread_fallback.py
./scripts/process_release_signals.py
./scripts/profile_decide.py
./scripts/recall_run.py
./scripts/refresh_leaderboards.py
./scripts/refresh_shard_durations.py
./scripts/release_watch.py
./scripts/research/eval_jev_recommendations.py
./scripts/resolve_huggingface.py
./scripts/retype_non_token_cards.py
./scripts/seed_huggingface.py
./scripts/seed_models_dev.py
./scripts/seo_audit.py
./scripts/slo/__main__.py
./scripts/slo/render.py
./scripts/social/generator.py
./scripts/speed/__main__.py
./scripts/sweep_next_move.py
./scripts/write_unmapped_classification.py
```
