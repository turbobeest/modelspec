> Scope: exactly 24 files in `scope.json` (current handoff, CLI/export contract, ranking implementation and tests). models/** and benchmarks/** are DATA and are excluded; the graph does not fact-check cards. Raw zero token fields are library placeholders. Refresh is manual and scoped; see README.md and scope-manifest.json.

# Graph Report - modelspec-182-signing  (2026-09-28)

## Corpus Check
- 24 files · ~54,049 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 532 nodes · 979 edges · 45 communities (23 shown, 22 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 21 edges (avg confidence: 0.86)
- Token cost: unavailable (host-session usage not exposed; library zeros are placeholders)

## Community Hubs (Navigation)
- Snapshot CLI tests
- Ranking engine
- Snapshot fetch and cache
- Interactive CLI
- Site build pipeline
- Offline CLI contract
- Ranking pipeline tests
- Graph JSON export
- Serving and CLI docs
- Scoring unit tests
- Ranking implementation
- Rank report integration
- Report CLI
- Graph scope data policy
- Static export pipeline
- Rehost identity tests
- Evidence provenance labels
- Current serving handoff
- Research token block
- Do-not-start tickets
- Ranking coverage floors
- Freeze superseded
- Standing honesty rules
- Worktree isolation
- Contract schema versions
- Required CI checks
- DPF contract registry
- Ranking source locators
- Closed MVP tickets
- CodeGraph setup
- CodeGraph per checkout
- CodeGraph checkout scope
- Rankings JSON version
- Card schema source
- Agent commerce assessment
- Hardware fit computation
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
1. `score()` - 28 edges
2. `rank_report()` - 28 edges
3. `_run()` - 27 edges
4. `_write()` - 24 edges
5. `main()` - 23 edges
6. `load()` - 21 edges
7. `_candidate()` - 18 edges
8. `fetch()` - 16 edges
9. `Candidate` - 15 edges
10. `info()` - 13 edges

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

## Communities (45 total, 22 thin omitted)

### Community 0 - "Snapshot CLI tests"
Cohesion: 0.06
Nodes (73): decision_snapshot_path(), decision_vocabulary_path(), load(), Read the cached snapshot. Never touches the network., _decision_artifacts(), _fetch_bodies(), _install_decision_pair(), _mock_http_client() (+65 more)

### Community 1 - "Ranking engine"
Cohesion: 0.07
Nodes (49): _apply_verified_additions(), _benchmark_evidence(), IncompleteEvidenceError, ModelData, neutrality_commitment(), ranking_policy(), _ranking_status(), RankingEngine (+41 more)

### Community 2 - "Snapshot fetch and cache"
Cohesion: 0.06
Nodes (52): Download the published export. The only command that needs the network. Unkeyed…, snapshot_fetch(), age_of(), cache_dir(), cached_decision_generations(), _check_refusal(), Credential, _current_decision_generation() (+44 more)

### Community 3 - "Interactive CLI"
Cohesion: 0.07
Nodes (55): _apply_hf_updates(), _bool_icon(), compare(), _compute_gap_info(), contribute(), _discover_card_files(), _edge_props(), _fetch_huggingface_data() (+47 more)

### Community 4 - "Site build pipeline"
Cohesion: 0.07
Nodes (49): benchgraph_headline_stats(), _copy_static(), _div_end(), _fallback_home(), _inject(), llms_txt(), main(), missing_internal_hrefs() (+41 more)

### Community 5 - "Offline CLI contract"
Cohesion: 0.10
Nodes (24): _candidates(), class_fit_offline(), ContractCommand, ContractGroup, _emit_error(), _envelope(), fit_offline(), _load_or_exit() (+16 more)

### Community 6 - "Ranking pipeline tests"
Cohesion: 0.09
Nodes (23): _normalize_benchmark(), Normalize a benchmark score to 0-100, higher always meaning better. Direction…, _basis(), Provenance of benchmark inputs, never a certification of the composite., The ranking pipeline: filter, score, rank, explain. The profiles, benchmark…, Word error rate: 2% is excellent, 20% is poor. Higher must not win., MODEL-32 option B: reviewed evidence is load-bearing. The active set may be…, The cap is the point: evidence matters without one source deciding "best". (+15 more)

### Community 7 - "Graph JSON export"
Cohesion: 0.14
Nodes (19): huggingface_ids(), is_hf_repo_id(), node_key(), _node_payload(), _norm_seg(), prefer_card(), _publish_edge(), Emit the knowledge graph as JSON, one file per edge view. The derivation lives… (+11 more)

### Community 8 - "Serving and CLI docs"
Cohesion: 0.11
Nodes (19): DPF offline CLI contract, Current orientation current.md, ModelSpec AGENTS entry, Static-first serving path, evidence_basis provenance labels, FalkorDB optional local exploration, ModelSpec CLAUDE.md, No R2 or D1 on serving path (+11 more)

### Community 9 - "Scoring unit tests"
Cohesion: 0.18
Nodes (18): Score one candidate. Mirrors RankingEngine._score. `cost_weight` overrides the…, score(), _candidate(), The cost curve itself is correct, when a caller asks for it., MODEL-48: None is unknown. Only a sourced 0.0 is published-free., Every shipped profile carries cost_weight 0.0, deliberately. Setting them all…, test_a_model_with_no_data_is_unranked(), test_a_ranking_reports_how_much_of_it_is_verified() (+10 more)

### Community 10 - "Ranking implementation"
Cohesion: 0.20
Nodes (12): Candidate, _matches_profile_type(), rank(), Rank models against a use-case profile, without a database.…, Return the models that can honestly be ordered for this profile. Unrankable…, Which floor withheld this row. Reads the evidence `score` already computed., The type test `score` uses for its type bonus, as a membership test., Name the models that would have been candidates but lack the evidence… (+4 more)

### Community 11 - "Rank report integration"
Cohesion: 0.21
Nodes (13): rank_report(), Rank sufficiently covered models and retain all others as unranked. `limit`…, Other models lacking coverage is ordinary; rank() must not raise., Provenance is disclosed; `verified` is not applied to incomplete evidence.…, _real(), test_a_hardware_constrained_ranking_is_smaller_and_still_useful(), test_a_rehost_is_left_out_of_default_rankings_and_fit(), test_every_featured_profile_reports_whether_it_can_rank() (+5 more)

### Community 12 - "Report CLI"
Cohesion: 0.22
Nodes (10): build_candidates(), format_report(), main(), One ranking record per card, with capability tiers and hardware fit attached., Human-readable contract shared by the report CLI and its tests., Report CLI, usable without changes to the legacy list-only CLI., Sparse real-card evidence is visible and unranked, never a low numeric rank.…, test_real_astra_is_visible_unranked_instead_of_ranked_low() (+2 more)

### Community 13 - "Graph scope data policy"
Cohesion: 0.29
Nodes (7): Architecture map coverage policy, benchmarks/** excluded from Graphify, Cards are DATA not fact-checked, models/** excluded from Graphify, Model cards are DATA, MODEL-40-PROBE-2026-09-14, MODEL-40-REFRESH-2026-09-14

### Community 14 - "Static export pipeline"
Cohesion: 0.40
Nodes (6): authoring_guides_from_cards(), Card authoring guides as JSON, keyed by `model_id`. Cards with no guide are…, Emit the tables the browser needs, plus precomputed rankings., write_export(), MODEL-81: the Worker reads guides from candidates.json, not by generating them., test_write_export_puts_card_guides_on_candidates_json()

### Community 15 - "Rehost identity tests"
Cohesion: 0.40
Nodes (6): The canonical id a repackaged card re-hosts, or None. Only `repackaged` counts.…, rehost_of(), _catalogue_cards(), Same display name AND same safetensors parameter count is the same weights. Two…, test_every_repackaged_card_points_at_a_catalogue_card(), test_no_byte_identical_rehost_reenters_the_default_fit_pool()

### Community 16 - "Evidence provenance labels"
Cohesion: 0.40
Nodes (5): evidence_basis mixed partial-verified verified, partial-verified provenance, unverified-legacy provenance, verified provenance, evidence_basis five labels

### Community 17 - "Current serving handoff"
Cohesion: 0.40
Nodes (5): Current ModelSpec state 2026-09-20, export_schema_version 3.0 current-state pin, MODEL-2 static Pages JSON, Static Pages serving path, Handoff who owns what

### Community 18 - "Research token block"
Cohesion: 0.40
Nodes (5): MODEL-5 GITHUB_TOKEN required-check block, PAT or GitHub App token required, PR 35 research/daily-models blocked, GITHUB_TOKEN cannot trigger required checks, MVP remainder MODEL-5

### Community 19 - "Do-not-start tickets"
Cohesion: 0.50
Nodes (4): Do not start MODEL-3 or MODEL-6, Daily research GITHUB_TOKEN block, Do not meter ModelSpec yet, Do not start MODEL-3 and MODEL-6

### Community 20 - "Ranking coverage floors"
Cohesion: 0.50
Nodes (4): CLI MIN_BENCHMARK_COVERAGE 0.50, Wizard WIZARD_BENCHMARK_COVERAGE 0.25, MODEL-34 Done, Rank only at 50 percent coverage and two benchmarks

### Community 21 - "Freeze superseded"
Cohesion: 0.67
Nodes (3): 2026-09-12 freeze lifted, Session freeze 2026-09-12 superseded, Freeze superseded 2026-09-14

### Community 22 - "Standing honesty rules"
Cohesion: 0.67
Nodes (3): Absence is data, A wrong answer is worse than no answer, Eight standing rules

## Knowledge Gaps
- **58 isolated node(s):** `Worktree isolation`, `CodeGraph this checkout only`, `Daily research GITHUB_TOKEN block`, `No R2 or D1 on serving path`, `export_schema_version 3.0` (+53 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 223 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `rank_report()` connect `Rank report integration` to `Ranking engine`, `Offline CLI contract`, `Ranking pipeline tests`, `Scoring unit tests`, `Ranking implementation`, `Report CLI`, `Static export pipeline`?**
  _High betweenness centrality (0.138) - this node is a cross-community bridge._
- **Why does `Candidate` connect `Ranking implementation` to `Ranking engine`, `Offline CLI contract`, `Ranking pipeline tests`, `Scoring unit tests`, `Rank report integration`, `Report CLI`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Why does `main()` connect `Site build pipeline` to `Static export pipeline`, `Graph JSON export`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `score()` (e.g. with `prefer_card()` and `_tier_rank()`) actually correct?**
  _`score()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Worktree isolation`, `CodeGraph this checkout only`, `Daily research GITHUB_TOKEN block` to the rest of the system?**
  _58 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Snapshot CLI tests` be split into smaller, more focused modules?**
  _Cohesion score 0.06350877192982456 - nodes in this community are weakly interconnected._
- **Should `Ranking engine` be split into smaller, more focused modules?**
  _Cohesion score 0.06721215663354763 - nodes in this community are weakly interconnected._