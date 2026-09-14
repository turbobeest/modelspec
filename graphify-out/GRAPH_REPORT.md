> Scope: exactly 24 files in `scope.json` (current handoff, CLI/export contract, ranking implementation and tests). models/** and benchmarks/** are DATA and are excluded; the graph does not fact-check cards. Raw zero token fields are library placeholders. Refresh is manual and scoped; see README.md and scope-manifest.json.

# Graph Report - modelspec-model-40  (2026-09-14)

## Corpus Check
- Corpus is ~36,596 words - fits in a single context window. You may not need a graph.

## Summary
- 403 nodes · 686 edges · 38 communities (16 shown, 22 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 20 edges (avg confidence: 0.86)
- Token cost: unavailable (host-session usage not exposed; library zeros are placeholders)

## Community Hubs (Navigation)
- Ranking engine
- Interactive CLI
- Ranking pipeline tests
- Offline CLI contract
- Snapshot CLI tests
- Site build pipeline
- Graph JSON export
- Current serving path
- Catalogue data policy
- Evidence provenance labels
- Current-state serving facts
- MODEL-5 token block
- Do-not-start tickets
- Ranking coverage floors
- Freeze superseded
- Standing honesty rules
- Worktree isolation
- Export schema versions
- Required CI checks
- DPF contract registry
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
- `Rank only at 50 percent coverage and two benchmarks` --semantically_similar_to--> `CLI MIN_BENCHMARK_COVERAGE 0.50`  [INFERRED] [semantically similar]
  docs/incomplete-evidence-ranking.md → CLAUDE.md
- `Required checks pytest and Build both sites` --semantically_similar_to--> `Required checks Run pytest and Build both sites`  [INFERRED] [semantically similar]
  docs/handoff/post-mvp-loop.md → CLAUDE.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **DPF CLI contract** — docs_cli_contract_cli_contract, docs_cli_contract_json_envelope, docs_cli_contract_exit_codes, docs_cli_contract_evidence_basis, docs_handoff_current_dpf_consumers [EXTRACTED 1.00]
- **MODEL-5 GITHUB_TOKEN merge block** — docs_handoff_current_model_5_github_token, docs_handoff_mvp_remainder_github_token, docs_handoff_current_pr_35, docs_handoff_current_pat_or_app_token, agents_github_token_block [EXTRACTED 1.00]

## Communities (38 total, 22 thin omitted)

### Community 0 - "Ranking engine"
Cohesion: 0.06
Nodes (66): _apply_verified_additions(), _benchmark_evidence(), IncompleteEvidenceError, ModelData, ranking_policy(), _ranking_status(), RankingEngine, ModelSpec Ranking Engine — 4-stage pipeline. Queries FalkorDB directly, scores… (+58 more)

### Community 1 - "Interactive CLI"
Cohesion: 0.07
Nodes (53): _apply_hf_updates(), _bool_icon(), compare(), _compute_gap_info(), contribute(), _discover_card_files(), _edge_props(), _fetch_huggingface_data() (+45 more)

### Community 2 - "Ranking pipeline tests"
Cohesion: 0.06
Nodes (50): _normalize_benchmark(), Normalize a benchmark score to 0-100, higher always meaning better. Direction…, _basis(), Score one candidate. Mirrors RankingEngine._score. `cost_weight` overrides the…, Provenance of benchmark inputs, never a certification of the composite., score(), _candidate(), The ranking pipeline: filter, score, rank, explain. The profiles, benchmark… (+42 more)

### Community 3 - "Offline CLI contract"
Cohesion: 0.07
Nodes (36): _candidates(), ContractCommand, ContractGroup, _emit_error(), _envelope(), fit_offline(), _load_or_exit(), rank_offline() (+28 more)

### Community 4 - "Snapshot CLI tests"
Cohesion: 0.11
Nodes (34): load(), Read the cached snapshot. Never touches the network., _modelspec_cli(), The CLI contract dpf consumes. This is an interface another program calls, so…, Snapshots fetched before the field existed are 1.x, not an error., A caller has to tell "no answer" from "no snapshot" from "broken"., Absolute path to the installed ``modelspec`` console script. The public entry…, Not an error. The honest answer is sometimes "nothing fits". (+26 more)

### Community 5 - "Site build pipeline"
Cohesion: 0.10
Nodes (29): _copy_static(), _fallback_home(), _inject(), main(), missing_internal_hrefs(), _output_exists(), Build both sites from the repository. python -m pipeline.build [--out dist]…, Copy a prebuilt landing page tree if it exists. Never overwrite generated pages. (+21 more)

### Community 6 - "Graph JSON export"
Cohesion: 0.16
Nodes (17): huggingface_ids(), is_hf_repo_id(), node_key(), _node_payload(), _norm_seg(), prefer_card(), _publish_edge(), Emit the knowledge graph as JSON, one file per edge view. The derivation lives… (+9 more)

### Community 7 - "Current serving path"
Cohesion: 0.12
Nodes (17): DPF offline CLI contract, Current orientation current.md, ModelSpec AGENTS entry, Static-first serving path, evidence_basis provenance labels, FalkorDB optional local exploration, ModelSpec CLAUDE.md, No R2 or D1 on serving path (+9 more)

### Community 8 - "Catalogue data policy"
Cohesion: 0.29
Nodes (7): Architecture map coverage policy, benchmarks/** excluded from Graphify, Cards are DATA not fact-checked, models/** excluded from Graphify, Model cards are DATA, MODEL-40-PROBE-2026-09-14, MODEL-40-REFRESH-2026-09-14

### Community 9 - "Evidence provenance labels"
Cohesion: 0.40
Nodes (5): evidence_basis mixed partial-verified verified, partial-verified provenance, unverified-legacy provenance, verified provenance, evidence_basis five labels

### Community 10 - "Current-state serving facts"
Cohesion: 0.40
Nodes (5): Current ModelSpec state 2026-09-14, export_schema_version pin, MODEL-2 static Pages JSON, Static Pages serving path, Handoff who owns what

### Community 11 - "MODEL-5 token block"
Cohesion: 0.40
Nodes (5): MODEL-5 GITHUB_TOKEN required-check block, PAT or GitHub App token required, PR 35 research/daily-models blocked, GITHUB_TOKEN cannot trigger required checks, MVP remainder MODEL-5

### Community 12 - "Do-not-start tickets"
Cohesion: 0.50
Nodes (4): Do not start MODEL-3 or MODEL-6, Daily research GITHUB_TOKEN block, Do not meter ModelSpec yet, Do not start MODEL-3 and MODEL-6

### Community 13 - "Ranking coverage floors"
Cohesion: 0.50
Nodes (4): CLI MIN_BENCHMARK_COVERAGE 0.50, Wizard WIZARD_BENCHMARK_COVERAGE 0.25, MODEL-34 Done, Rank only at 50 percent coverage and two benchmarks

### Community 14 - "Freeze superseded"
Cohesion: 0.67
Nodes (3): 2026-09-12 freeze lifted, Session freeze 2026-09-12 superseded, Freeze superseded 2026-09-14

### Community 15 - "Standing honesty rules"
Cohesion: 0.67
Nodes (3): Absence is data, A wrong answer is worse than no answer, Eight standing rules

## Knowledge Gaps
- **58 isolated node(s):** `Worktree isolation`, `CodeGraph this checkout only`, `Daily research GITHUB_TOKEN block`, `No R2 or D1 on serving path`, `export_schema_version 1.0` (+53 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 178 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `rank_report()` connect `Ranking engine` to `Ranking pipeline tests`, `Offline CLI contract`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Why does `Candidate` connect `Ranking engine` to `Ranking pipeline tests`, `Offline CLI contract`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Why does `score()` connect `Ranking pipeline tests` to `Ranking engine`, `Graph JSON export`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `score()` (e.g. with `prefer_card()` and `_tier_rank()`) actually correct?**
  _`score()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Worktree isolation`, `CodeGraph this checkout only`, `Daily research GITHUB_TOKEN block` to the rest of the system?**
  _58 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Ranking engine` be split into smaller, more focused modules?**
  _Cohesion score 0.055176890619928594 - nodes in this community are weakly interconnected._
- **Should `Interactive CLI` be split into smaller, more focused modules?**
  _Cohesion score 0.06868686868686869 - nodes in this community are weakly interconnected._