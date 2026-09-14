> Scope: exactly 24 files in `scope.json` (current handoff, CLI/export contract, ranking implementation and tests). models/** and benchmarks/** are DATA and are excluded; the graph does not fact-check cards. Raw zero token fields are library placeholders. Refresh is manual and scoped; see README.md and scope-manifest.json.

# Graph Report - modelspec-model-40  (2026-09-14)

## Corpus Check
- Corpus is ~36,591 words - fits in a single context window. You may not need a graph.

## Summary
- 402 nodes · 687 edges · 36 communities (14 shown, 22 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 21 edges (avg confidence: 0.87)
- Token cost: unavailable (host-session usage not exposed; library zeros are placeholders)

## Community Hubs (Navigation)
- Ranking engine
- Interactive CLI
- Ranking pipeline tests
- Offline CLI contract
- Snapshot CLI tests
- Site build pipeline
- Current serving path
- Graph JSON export
- MODEL-5 token block
- Catalogue data policy
- Evidence provenance labels
- Ranking coverage floors
- Freeze superseded
- Standing honesty rules
- Worktree isolation
- Export schema versions
- Required CI checks
- Rank source locators
- Closed MVP tickets
- CodeGraph commands
- CodeGraph per checkout
- CodeGraph this checkout
- Rankings JSON version
- Card schema source
- Agent commerce assessment
- Hardware fit computed
- Offline fit command
- Graphify scope guard
- Live ranking floors
- Global Graphify registry
- Offline module locator
- Export module locator
- Ranking snapshot tests
- Snapshot module locator
- Post-MVP loop
- Incomplete evidence ranking

## God Nodes (most connected - your core abstractions)
1. `score()` - 27 edges
2. `rank_report()` - 26 edges
3. `load()` - 17 edges
4. `_write()` - 16 edges
5. `_candidate()` - 16 edges
6. `_run()` - 15 edges
7. `main()` - 14 edges
8. `Candidate` - 13 edges
9. `candidate()` - 13 edges
10. `RankingEngine` - 12 edges

## Surprising Connections (you probably didn't know these)
- `DPF offline CLI contract` --semantically_similar_to--> `ModelSpec CLI contract`  [INFERRED] [semantically similar]
  AGENTS.md → docs/cli-contract.md
- `Worktree isolation` --semantically_similar_to--> `Own git worktree per session`  [INFERRED] [semantically similar]
  AGENTS.md → docs/handoff/worktrees.md
- `Do not start MODEL-3 and MODEL-6` --semantically_similar_to--> `Do not start MODEL-3 or MODEL-6`  [INFERRED] [semantically similar]
  docs/handoff/post-mvp-loop.md → AGENTS.md
- `Daily research GITHUB_TOKEN block` --semantically_similar_to--> `MODEL-5 GITHUB_TOKEN required-check block`  [INFERRED] [semantically similar]
  AGENTS.md → docs/handoff/current.md
- `Static Pages export` --semantically_similar_to--> `MODEL-2 static Pages JSON`  [INFERRED] [semantically similar]
  CLAUDE.md → docs/handoff/current.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **DPF CLI contract** — docs_cli_contract_cli_contract, docs_cli_contract_json_envelope, docs_cli_contract_exit_codes, docs_cli_contract_evidence_basis, docs_handoff_current_dpf_consumers [EXTRACTED 1.00]
- **MODEL-5 GITHUB_TOKEN merge block** — docs_handoff_current_model_5_github_token, docs_handoff_mvp_remainder_github_token, docs_handoff_current_pr_35, docs_handoff_current_pat_or_app_token, agents_github_token_block [EXTRACTED 1.00]
- **Static Pages serving path** — agents_static_first_serving, claude_static_pages_export, docs_handoff_current_serving_path, docs_handoff_current_export_schema_version, docs_cli_contract_snapshot_fetch [EXTRACTED 1.00]

## Communities (36 total, 22 thin omitted)

### Community 0 - "Ranking engine"
Cohesion: 0.06
Nodes (64): _apply_verified_additions(), _benchmark_evidence(), IncompleteEvidenceError, ModelData, ranking_policy(), _ranking_status(), RankingEngine, ModelSpec Ranking Engine — 4-stage pipeline. Queries FalkorDB directly, scores… (+56 more)

### Community 1 - "Interactive CLI"
Cohesion: 0.07
Nodes (53): _apply_hf_updates(), _bool_icon(), compare(), _compute_gap_info(), contribute(), _discover_card_files(), _edge_props(), _fetch_huggingface_data() (+45 more)

### Community 2 - "Ranking pipeline tests"
Cohesion: 0.06
Nodes (52): _normalize_benchmark(), Normalize a benchmark score to 0-100, higher always meaning better. Direction…, _basis(), Score one candidate. Mirrors RankingEngine._score. `cost_weight` overrides the…, Provenance of benchmark inputs, never a certification of the composite., score(), _candidate(), The ranking pipeline: filter, score, rank, explain. The profiles, benchmark… (+44 more)

### Community 3 - "Offline CLI contract"
Cohesion: 0.07
Nodes (36): _candidates(), ContractCommand, ContractGroup, _emit_error(), _envelope(), fit_offline(), _load_or_exit(), rank_offline() (+28 more)

### Community 4 - "Snapshot CLI tests"
Cohesion: 0.11
Nodes (34): load(), Read the cached snapshot. Never touches the network., _modelspec_cli(), The CLI contract dpf consumes. This is an interface another program calls, so…, Snapshots fetched before the field existed are 1.x, not an error., A caller has to tell "no answer" from "no snapshot" from "broken"., Absolute path to the installed ``modelspec`` console script. The public entry…, Not an error. The honest answer is sometimes "nothing fits". (+26 more)

### Community 5 - "Site build pipeline"
Cohesion: 0.10
Nodes (29): _copy_static(), _fallback_home(), _inject(), main(), missing_internal_hrefs(), _output_exists(), Build both sites from the repository. python -m pipeline.build [--out dist]…, Copy a prebuilt landing page tree if it exists. Never overwrite generated pages. (+21 more)

### Community 6 - "Current serving path"
Cohesion: 0.09
Nodes (23): DPF offline CLI contract, Current orientation current.md, ModelSpec AGENTS entry, Static-first serving path, evidence_basis provenance labels, FalkorDB optional local exploration, ModelSpec CLAUDE.md, No R2 or D1 on serving path (+15 more)

### Community 7 - "Graph JSON export"
Cohesion: 0.16
Nodes (17): huggingface_ids(), is_hf_repo_id(), node_key(), _node_payload(), _norm_seg(), prefer_card(), _publish_edge(), Emit the knowledge graph as JSON, one file per edge view. The derivation lives… (+9 more)

### Community 8 - "MODEL-5 token block"
Cohesion: 0.22
Nodes (9): Do not start MODEL-3 or MODEL-6, Daily research GITHUB_TOKEN block, Do not meter ModelSpec yet, MODEL-5 GITHUB_TOKEN required-check block, PAT or GitHub App token required, PR 35 research/daily-models blocked, GITHUB_TOKEN cannot trigger required checks, MVP remainder MODEL-5 (+1 more)

### Community 9 - "Catalogue data policy"
Cohesion: 0.33
Nodes (6): Architecture map coverage policy, benchmarks/** excluded from Graphify, Cards are DATA not fact-checked, models/** excluded from Graphify, Model cards are DATA, MODEL-40-PROBE-2026-09-14

### Community 10 - "Evidence provenance labels"
Cohesion: 0.40
Nodes (5): evidence_basis mixed partial-verified verified, partial-verified provenance, unverified-legacy provenance, verified provenance, evidence_basis five labels

### Community 11 - "Ranking coverage floors"
Cohesion: 0.50
Nodes (4): CLI MIN_BENCHMARK_COVERAGE 0.50, Wizard WIZARD_BENCHMARK_COVERAGE 0.25, MODEL-34 Done, Rank only at 50 percent coverage and two benchmarks

### Community 12 - "Freeze superseded"
Cohesion: 0.67
Nodes (3): 2026-09-12 freeze lifted, Session freeze 2026-09-12 superseded, Freeze superseded 2026-09-14

### Community 13 - "Standing honesty rules"
Cohesion: 0.67
Nodes (3): Absence is data, A wrong answer is worse than no answer, Eight standing rules

## Knowledge Gaps
- **57 isolated node(s):** `Worktree isolation`, `CodeGraph this checkout only`, `No R2 or D1 on serving path`, `export_schema_version 1.0`, `CLI envelope schema_version 1.0` (+52 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 177 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `rank_report()` connect `Ranking engine` to `Ranking pipeline tests`, `Offline CLI contract`?**
  _High betweenness centrality (0.147) - this node is a cross-community bridge._
- **Why does `Candidate` connect `Ranking engine` to `Ranking pipeline tests`, `Offline CLI contract`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Why does `score()` connect `Ranking pipeline tests` to `Ranking engine`, `Graph JSON export`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `score()` (e.g. with `prefer_card()` and `_tier_rank()`) actually correct?**
  _`score()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Worktree isolation`, `CodeGraph this checkout only`, `No R2 or D1 on serving path` to the rest of the system?**
  _57 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Ranking engine` be split into smaller, more focused modules?**
  _Cohesion score 0.05707450444292549 - nodes in this community are weakly interconnected._
- **Should `Interactive CLI` be split into smaller, more focused modules?**
  _Cohesion score 0.06868686868686869 - nodes in this community are weakly interconnected._