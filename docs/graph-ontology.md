# ModelSpec Knowledge Graph Ontology — Complete Specification

## Design Philosophy

The graph has three layers:
1. **Factual layer** — directly observed data (scraped, measured, documented)
2. **Derived layer** — computed relationships (competition, similarity, ranking)
3. **Institutional layer** — organization-specific overlays (downselect, approvals, custom scores)

Every node property is either **intrinsic** (belongs to the entity itself) or **contextual** 
(depends on the relationship). Contextual data lives on edges, not nodes.

Example: "Qwen3-30B-A3B gets 45 TPS on MacBook Air M4" — the TPS is contextual 
(it depends on the hardware AND the quantization), so it lives on the 
`:FITS_ON` edge, not on the `:Model` node.

---

## NODE TYPES

### :Model
The central entity. Every other node connects through a model.

```
Properties:
  id                    String    REQUIRED  INDEXED  # canonical ID "provider/model-name"
  display_name          String    REQUIRED
  model_type            String    REQUIRED  INDEXED  # from taxonomy (llm-chat, embedding-text, etc.)
  model_subtypes        String[]                      # secondary types
  status                String    REQUIRED  INDEXED  # active | beta | alpha | deprecated | sunset
  release_date          Date      REQUIRED  INDEXED
  last_updated          Date
  
  # Architecture (intrinsic to the model)
  architecture_type     String    INDEXED             # dense-transformer | MoE | SSM | hybrid | diffusion
  total_parameters      Integer   INDEXED             # total param count
  active_parameters     Integer                        # for MoE
  num_experts           Integer
  experts_per_token     Integer
  num_layers            Integer
  hidden_size           Integer
  attention_type        String                         # MHA | GQA | MQA | MLA
  positional_encoding   String                         # RoPE | ALiBi | etc.
  vocab_size            Integer
  tokenizer_type        String
  embedding_dimensions  Integer                        # output dims for embedding models
  precision_native      String                         # BF16 | FP16 | FP8
  context_window        Integer   INDEXED
  max_input             Integer
  max_output            Integer
  
  # Capabilities (intrinsic qualitative)
  reasoning             Boolean   INDEXED
  tool_call             Boolean   INDEXED
  structured_output     Boolean
  attachment            Boolean
  multilingual          Boolean
  num_languages         Integer
  open_weights          Boolean   INDEXED
  fill_in_middle        Boolean                        # code completion mode
  vision_input          Boolean   INDEXED
  audio_input           Boolean
  audio_output          Boolean
  video_input           Boolean
  video_output          Boolean
  image_generation      Boolean   INDEXED
  
  # Cost (intrinsic to primary provider)
  cost_input            Float     INDEXED              # $/M input tokens
  cost_output           Float     INDEXED              # $/M output tokens
  cost_reasoning        Float
  cost_cache_read       Float
  cost_cache_write      Float
  
  # Composite scores (derived, updated by ranking engine)
  arena_elo_overall     Integer   INDEXED
  arena_elo_coding      Integer
  arena_elo_math        Integer
  arena_elo_vision      Integer
  custom_score          Float     INDEXED              # 0-100, institution-specific
  card_completeness     Float                          # 0-100, % of fields filled
  
  # Lineage
  base_model_id         String                         # parent model ID
  base_model_relation   String                         # finetune | quantized | merged | distilled
  
  # Provenance
  origin_country        String    INDEXED              # ISO country code
  origin_org_type       String                         # private | state-backed | academic
  training_data_tokens  Integer
  training_compute_flops Float
  co2_emissions_kg      Float
  
  # Adoption
  hf_downloads          Integer
  hf_likes              Integer
  ollama_pulls          Integer
  openrouter_rank       Integer
```

### :Provider
The organization that created the model.

```
Properties:
  id                    String    REQUIRED  INDEXED  # slug (e.g. "anthropic")
  display_name          String    REQUIRED
  country               String    INDEXED
  org_type              String                         # private | state-backed | academic
  website               String
  api_endpoint          String
  npm_package           String                         # AI SDK package
  env_vars              String[]
  doc_url               String
  founded_year          Integer
  parent_org            String                         # e.g. "Alibaba" for Qwen
```

### :Platform
Anywhere a model can be accessed — cloud, inference service, app, local tool.

```
Properties:
  id                    String    REQUIRED  INDEXED  # slug (e.g. "groq", "cursor", "ollama")
  display_name          String    REQUIRED
  category              String    REQUIRED  INDEXED  # cloud | inference | aggregator | ai-app | provider | cn-platform | regional | local | model-hub
  url                   String
  has_free_tier         Boolean
  has_fine_tuning        Boolean
  has_api               Boolean
  compliance_certs      String[]                       # hipaa | fedramp | soc2 | iso27001
  regions               String[]
  country               String                         # HQ country
```

### :Capability
A thing a model can do. Leaf nodes in the capability taxonomy.

```
Properties:
  id                    String    REQUIRED  INDEXED  # e.g. "coding:agentic_coding"
  category              String    REQUIRED  INDEXED  # coding | reasoning | tool_use | language | creative | safety | agent | domain
  name                  String    REQUIRED           # human-readable
  description           String
  measurable            Boolean                        # can be benchmarked?
  related_benchmarks    String[]                       # IDs of benchmarks that test this
```

### :Hardware
A specific compute device that can run models locally.

```
Properties:
  id                    String    REQUIRED  INDEXED  # e.g. "nvidia_5090_32gb"
  display_name          String    REQUIRED
  memory_gb             Integer   REQUIRED  INDEXED
  memory_type           String                         # GDDR7 | HBM3 | unified | DDR5
  unified_memory        Boolean                        # Apple Silicon style
  compute_type          String                         # gpu | unified | cpu
  architecture          String                         # ada-lovelace | blackwell | apple-m4 | grace-blackwell
  gpu_chip              String                         # e.g. "GB202", "M4 Max"
  tdp_watts             Integer
  pcie_gen              Integer
  tensor_cores          Boolean
  fp16_tflops           Float
  bf16_tflops           Float
  int8_tops             Float
  memory_bandwidth_gbps Float
  msrp_usd              Float
  release_date          Date
  form_factor           String                         # desktop-gpu | workstation | laptop | server | edge
```

### :Quantization
A specific quantization format/method.

```
Properties:
  id                    String    REQUIRED  INDEXED  # e.g. "Q4_K_M"
  format                String    REQUIRED           # gguf | awq | gptq | exl2 | fp16 | bf16 | fp8
  bits                  Integer   REQUIRED           # 2 | 3 | 4 | 5 | 6 | 8 | 16 | 32
  method                String                         # k-quant | round-to-nearest | gptq | awq
  description           String
```

### :Benchmark
A specific evaluation test or leaderboard.

```
Properties:
  id                    String    REQUIRED  INDEXED  # e.g. "gpqa_diamond"
  name                  String    REQUIRED
  category              String    REQUIRED  INDEXED  # knowledge | math | coding | multimodal | safety | human-preference | embedding | generation | domain | agentic | composite
  description           String
  max_score             Float                          # theoretical maximum
  human_baseline        Float                          # human expert performance
  random_baseline       Float                          # random chance performance
  saturated             Boolean                        # top models at ceiling?
  contamination_risk    String                         # low | medium | high
  dynamic               Boolean                        # refreshed periodically (LiveBench)?
  url                   String
  administered_by       String                         # org that runs it
  first_published       Date
```

### :License
A specific license type with use-case permissions.

```
Properties:
  id                    String    REQUIRED  INDEXED  # e.g. "apache-2.0"
  name                  String    REQUIRED
  spdx_id               String                         # SPDX license identifier
  url                   String
  commercial_ok         Boolean   INDEXED
  modification_ok       Boolean
  distribution_ok       Boolean
  patent_grant          Boolean
  copyleft              Boolean
  attribution_required  Boolean
  defense_ok            String                         # allowed | restricted | prohibited | unspecified
  government_ok         String
  medical_ok            String
```

### :UseCase
A specific application pattern that models serve.

```
Properties:
  id                    String    REQUIRED  INDEXED  # e.g. "agentic_coding"
  name                  String    REQUIRED
  description           String
  category              String    INDEXED              # coding | rag | chat | creative | analysis | safety | domain
  typical_model_types   String[]                       # which model_types typically serve this
  required_capabilities String[]                       # capability IDs that are must-haves
  preferred_capabilities String[]                      # nice-to-haves
  typical_hardware      String[]                       # common hardware for this use case
  example_tools         String[]                       # e.g. "Claude Code", "Cursor", "LangChain"
```

### :DownselectProfile
An institution's set of constraints and preferences.

```
Properties:
  id                    String    REQUIRED  INDEXED
  name                  String    REQUIRED
  institution           String
  description           String
  compliance_tags       String[]                       # fedramp-high | hipaa | itar | cmmc
  clearance_tags        String[]                       # approved-cui | approved-fouo
  defense_tags          String[]                       # approved-dod | five-eyes-ok
  sovereignty_tags      String[]                       # us-only-hosting | no-cn-origin
  use_case_tags         String[]
  max_cost_per_million  Float
  required_license      String[]
  excluded_countries    String[]
  open_weights_required Boolean
  min_arena_elo         Integer
  created_by            String
  created_at            Date
  updated_at            Date
```

### :Runtime
An inference engine/framework that can execute models.

```
Properties:
  id                    String    REQUIRED  INDEXED  # e.g. "vllm", "ollama", "llama_cpp"
  name                  String    REQUIRED
  url                   String
  language              String                         # Python | C++ | Rust | Swift
  supports_quantization String[]                       # which quant formats
  supports_platforms    String[]                       # linux | macos | windows
  gpu_required          Boolean
  metal_support         Boolean                        # Apple Metal
  cuda_support          Boolean
  rocm_support          Boolean
  tensor_rt_support     Boolean
  open_source           Boolean
```

### :Tag
Freeform metadata tag for discoverability.

```
Properties:
  id                    String    REQUIRED  INDEXED
  category              String                         # domain | technique | audience | compliance
```

---

## EDGE TYPES — Complete Catalog

### Factual Edges (directly observed/documented)

```
┌─────────────────────────────────────────────────────────────────────┐
│ EDGE TYPE              │ FROM      │ TO          │ CARDINALITY      │
├────────────────────────┼───────────┼─────────────┼──────────────────┤
│ :MADE_BY               │ :Model    │ :Provider   │ many-to-one      │
│ :DERIVED_FROM          │ :Model    │ :Model      │ many-to-one      │
│ :MERGED_FROM           │ :Model    │ :Model      │ many-to-many     │
│ :LICENSED_AS           │ :Model    │ :License    │ many-to-one      │
│ :HAS_CAPABILITY        │ :Model    │ :Capability │ many-to-many     │
│ :SCORED_ON             │ :Model    │ :Benchmark  │ many-to-many     │
│ :FITS_ON               │ :Model    │ :Hardware   │ many-to-many     │
│ :AVAILABLE_AS          │ :Model    │ :Quantization│ many-to-many    │
│ :RUNS_ON               │ :Model    │ :Runtime    │ many-to-many     │
│ :AVAILABLE_ON          │ :Model    │ :Platform   │ many-to-many     │
│ :TAGGED_WITH           │ :Model    │ :Tag        │ many-to-many     │
│ :SUITED_FOR            │ :Model    │ :UseCase    │ many-to-many     │
│ :PUBLISHED_BY          │ :Platform │ :Provider   │ many-to-many     │
│ :SUPPORTS_RUNTIME      │ :Hardware │ :Runtime    │ many-to-many     │
│ :TESTS_CAPABILITY      │ :Benchmark│ :Capability │ many-to-many     │
│ :REQUIRED_BY           │ :Capability│ :UseCase   │ many-to-many     │
└─────────────────────────────────────────────────────────────────────┘
```

### Derived Edges (computed by the ranking engine)

```
┌─────────────────────────────────────────────────────────────────────┐
│ EDGE TYPE              │ FROM      │ TO          │ CARDINALITY      │
├────────────────────────┼───────────┼─────────────┼──────────────────┤
│ :COMPETES_WITH         │ :Model    │ :Model      │ many-to-many     │
│ :OUTPERFORMS           │ :Model    │ :Model      │ many-to-many     │
│ :SIMILAR_TO            │ :Model    │ :Model      │ many-to-many     │
│ :UPGRADE_PATH          │ :Model    │ :Model      │ many-to-many     │
│ :BEST_FOR              │ :Model    │ :UseCase    │ many-to-many     │
│ :PARETO_OPTIMAL        │ :Model    │ :Hardware   │ many-to-many     │
└─────────────────────────────────────────────────────────────────────┘
```

### Institutional Edges (organization-specific overlay)

```
┌─────────────────────────────────────────────────────────────────────┐
│ EDGE TYPE              │ FROM             │ TO       │ CARDINALITY  │
├────────────────────────┼──────────────────┼──────────┼──────────────┤
│ :APPROVED_BY           │ :DownselectProfile│ :Model  │ many-to-many │
│ :EXCLUDED_BY           │ :DownselectProfile│ :Model  │ many-to-many │
│ :REVIEWED_BY           │ :DownselectProfile│ :Model  │ many-to-many │
│ :PREFERRED_BY          │ :DownselectProfile│ :UseCase│ many-to-many │
└─────────────────────────────────────────────────────────────────────┘
```

---

## EDGE PROPERTIES (the data that lives on relationships)

### :MADE_BY
```
  (no additional properties — the relationship itself is the data)
```

### :DERIVED_FROM
```
  relation              String    REQUIRED  # finetune | quantized | merged | distilled | continuation | adapter
  method                String              # LoRA | QLoRA | full-finetune | DPO | RLHF | knowledge-distillation
  adapter_rank          Integer             # for LoRA-based
  performance_retention Float               # 0-1, how much of parent's quality retained
  date                  Date
```

### :MERGED_FROM
```
  merge_method          String              # linear | slerp | ties | dare | passthrough
  weight                Float               # 0-1, contribution weight
```

### :LICENSED_AS
```
  license_url           String
  additional_restrictions String[]          # beyond the base license
  aup_url               String              # acceptable use policy
```

### :HAS_CAPABILITY
```
  tier                  String    REQUIRED  # tier-1 | tier-2 | tier-3
  confidence            String              # high | medium | low
  source                String              # benchmark | expert-eval | self-reported | community
  evidence_url          String
  assessed_date         Date
```

### :SCORED_ON
```
  value                 Float     REQUIRED  # the benchmark score
  normalized_value      Float               # 0-100 normalized
  percentile            Float               # percentile rank among all models
  date                  Date      REQUIRED  # when this score was recorded
  source_url            String
  methodology           String              # provider-reported | independent | community
  model_version         String              # exact version tested
  prompt_template       String              # if methodology varies
  num_shots             Integer             # 0-shot, 5-shot, etc.
```

### :FITS_ON
```
  quantization          String    REQUIRED  # which quant format
  vram_usage_gb         Float
  ram_usage_gb          Float               # for unified memory systems
  tokens_per_sec        Float               # output TPS
  prompt_tps            Float               # input processing TPS
  ttft_ms               Float               # time to first token
  max_context_tokens    Integer             # max context that fits in memory
  max_batch_size        Integer
  inference_engine      String              # which runtime was used for measurement
  measured_date         Date
  measured_by           String              # who measured (community, provider, our team)
  notes                 String
```

### :AVAILABLE_AS
```
  size_gb               Float               # file size of this quantization
  hf_repo               String              # where to download
  community_author      String              # who made this quant (e.g. "bartowski")
  perplexity_delta      Float               # quality loss vs full precision
  verified              Boolean             # has someone validated quality?
```

### :RUNS_ON
```
  verified              Boolean             # confirmed working
  config_notes          String              # any special config needed
  min_version           String              # minimum runtime version
```

### :AVAILABLE_ON
```
  model_id_on_platform  String              # the ID string you pass to the API
  available_since       Date
  fine_tuning           Boolean             # can you fine-tune here?
  serverless            Boolean             # serverless or dedicated?
  gated                 Boolean             # requires access approval?
  pricing_url           String
  regions               String[]            # available in which regions
  notes                 String
```

### :TAGGED_WITH
```
  (no additional properties)
```

### :SUITED_FOR
```
  rank                  Integer             # 1 = best fit
  score                 Float               # 0-100
  rationale             String              # why this model fits
  confidence            String              # high | medium | low
  assessed_by           String              # algorithm | expert | community
  assessed_date         Date
```

### :COMPETES_WITH (derived)
```
  dimension             String    REQUIRED  # overall | coding | reasoning | cost | speed
  overlap_score         Float               # 0-1, how similar the capability profiles are
  computed_date         Date
```

### :OUTPERFORMS (derived)
```
  dimension             String    REQUIRED  # benchmark ID or capability category
  margin                Float               # score difference
  computed_date         Date
```

### :SIMILAR_TO (derived)
```
  similarity_score      Float     REQUIRED  # 0-1
  dimensions            String[]            # which dimensions drive similarity
  computed_date         Date
```

### :UPGRADE_PATH (derived)
```
  direction             String    REQUIRED  # scale-up | scale-down | switch-license | switch-provider
  trade_offs            String              # what you gain/lose
  computed_date         Date
```

### :BEST_FOR (derived)
```
  hardware_context      String              # for which hardware profile
  rank                  Integer             # 1 = best
  score                 Float
  computed_date         Date
```

### :PARETO_OPTIMAL (derived)
```
  dimensions            String[]  REQUIRED  # e.g. ["quality", "cost"] or ["quality", "speed"]
  computed_date         Date
```

### :APPROVED_BY / :EXCLUDED_BY / :REVIEWED_BY (institutional)
```
  date                  Date      REQUIRED
  reviewer              String
  reason                String
  expiry_date           Date                # approval may expire
  conditions            String[]            # conditional approvals
```

### :PREFERRED_BY (institutional)
```
  priority              Integer             # 1 = highest
```

### :PUBLISHED_BY
```
  relationship          String              # owns | hosts | resells | open-source-maintainer
```

### :SUPPORTS_RUNTIME
```
  performance_tier      String              # optimal | supported | experimental
  notes                 String
```

### :TESTS_CAPABILITY
```
  directness            String              # direct | proxy | partial
  notes                 String
```

### :REQUIRED_BY
```
  importance            String              # required | preferred | nice-to-have
```

---

## GRAPH STATISTICS (estimated at maturity)

| Entity Type       | Estimated Count | Notes |
|---|---|---|
| :Model            | 500-800         | All model types across all providers |
| :Provider         | 80-120          | From models.dev + Chinese + regional |
| :Platform         | 80-100          | All availability destinations |
| :Capability       | 50-70           | Leaf capabilities in taxonomy |
| :Hardware         | 15-25           | Reference devices + common configs |
| :Quantization     | 15-20           | Standard quant formats |
| :Benchmark        | 60-80           | All tracked benchmarks |
| :License          | 15-20           | Distinct license types |
| :UseCase          | 25-40           | Application patterns |
| :DownselectProfile| 5-20            | Per institution |
| :Runtime          | 15-20           | Inference engines |
| :Tag              | 100-200         | Freeform tags |
|                   |                 | |
| **Total nodes**   | **~1,000-1,500**| |
| **Total edges**   | **~25,000-50,000**| Average ~40 edges per model |

---

## KEY TRAVERSAL PATTERNS

These are the queries that power the ranking engine and UI:

### 1. "Best model for my hardware and use case"
```cypher
MATCH (m:Model)-[:FITS_ON {quantization: $quant}]->(h:Hardware {id: $hw})
MATCH (m)-[:HAS_CAPABILITY {tier: 'tier-1'}]->(c:Capability)
MATCH (uc:UseCase {id: $use_case})-[:REQUIRED_BY]-(c)
WHERE m.status = 'active'
RETURN m, collect(c.name) AS capabilities
ORDER BY m.arena_elo_overall DESC
LIMIT 10
```

### 2. "Model lineage tree"
```cypher
MATCH path = (m:Model {id: $model_id})-[:DERIVED_FROM*0..5]->(ancestor:Model)
RETURN path
```

### 3. "All derivatives of a base model"
```cypher
MATCH (base:Model {id: $model_id})<-[:DERIVED_FROM*1..3]-(derivative:Model)
RETURN derivative.id, derivative.display_name, derivative.base_model_relation
ORDER BY derivative.release_date DESC
```

### 4. "Where can I use this model?"
```cypher
MATCH (m:Model {id: $model_id})-[a:AVAILABLE_ON]->(p:Platform)
RETURN p.display_name, p.category, p.url, a.model_id_on_platform, a.fine_tuning
ORDER BY p.category
```

### 5. "Competition landscape"
```cypher
MATCH (m:Model {id: $model_id})-[:COMPETES_WITH]->(rival:Model)
OPTIONAL MATCH (m)-[s1:SCORED_ON]->(b:Benchmark)<-[s2:SCORED_ON]-(rival)
RETURN rival.display_name, 
       collect({benchmark: b.name, ours: s1.value, theirs: s2.value}) AS scores
```

### 6. "Institutional downselect"
```cypher
MATCH (dp:DownselectProfile {id: $profile})-[:APPROVED_BY]->(m:Model)
MATCH (m)-[:FITS_ON]->(h:Hardware {id: $hw})
WHERE NOT (dp)-[:EXCLUDED_BY]->(m)
RETURN m
ORDER BY m.custom_score DESC
```

### 7. "Pareto frontier: quality vs cost"
```cypher
MATCH (m:Model)-[:PARETO_OPTIMAL {dimensions: ['quality', 'cost']}]->(h:Hardware {id: $hw})
RETURN m.display_name, m.arena_elo_overall, m.cost_input, m.cost_output
```

### 8. "Chinese-origin models with Apache license that fit my MacBook"
```cypher
MATCH (m:Model)-[:FITS_ON]->(h:Hardware {id: 'macbook_air_m4_24gb'})
MATCH (m)-[:LICENSED_AS]->(l:License {id: 'apache-2.0'})
WHERE m.origin_country = 'CN' AND m.status = 'active'
RETURN m.display_name, m.total_parameters, m.arena_elo_overall
ORDER BY m.arena_elo_overall DESC
```

### 9. "Upgrade path: what's better than what I'm using?"
```cypher
MATCH (current:Model {id: $model_id})-[:UPGRADE_PATH]->(better:Model)
MATCH (better)-[:FITS_ON]->(h:Hardware {id: $hw})
RETURN better.display_name, better.arena_elo_overall, better.cost_input
ORDER BY better.arena_elo_overall DESC
```

### 10. "Embedding models ranked by MTEB for my hardware"
```cypher
MATCH (m:Model)-[:FITS_ON]->(h:Hardware {id: $hw})
MATCH (m)-[s:SCORED_ON]->(b:Benchmark {id: 'mteb_overall'})
WHERE m.model_type = 'embedding-text' AND m.status = 'active'
RETURN m.display_name, s.value AS mteb_score, m.embedding_dimensions
ORDER BY s.value DESC
LIMIT 10
```

---

## DERIVED EDGE COMPUTATION

The backend researcher computes derived edges on a schedule:

### :COMPETES_WITH
```
Two models compete if:
  - Same model_type
  - Parameter count within 3x of each other
  - At least 3 shared benchmarks
  - Released within 12 months of each other
  - Both status = 'active'

Overlap score = Jaccard similarity of capability sets
```

### :OUTPERFORMS
```
Model A outperforms Model B on dimension X if:
  - A.score > B.score on benchmark X
  - OR A has higher tier on capability X
  - AND they :COMPETES_WITH each other
```

### :SIMILAR_TO
```
Similarity = weighted combination of:
  - Capability profile cosine similarity (0.3)
  - Benchmark score correlation (0.3)
  - Parameter count proximity (0.1)
  - Same model_type (0.15)
  - Same origin_country (0.05)
  - Same license_type (0.1)

Threshold: similarity > 0.7 creates edge
```

### :UPGRADE_PATH
```
Model B is an upgrade from Model A if:
  - B scores higher on 60%+ of shared benchmarks
  - B.release_date > A.release_date
  - One of:
    - Same provider (natural upgrade)
    - Same model_type + similar params (lateral upgrade)
    - Higher params but fits same hardware (scale-up)
    - Lower params + similar quality (efficiency upgrade)
```

### :PARETO_OPTIMAL
```
Model M is Pareto-optimal on dimensions [D1, D2, ...] for hardware H if:
  - M :FITS_ON H
  - No other model N exists where:
    - N :FITS_ON H
    - N is equal or better on ALL of [D1, D2, ...]
    - N is strictly better on at least ONE

Common Pareto frontiers:
  - quality × cost (arena_elo vs $/M tokens)
  - quality × speed (arena_elo vs TPS on hardware)
  - quality × size (arena_elo vs total_parameters)
  - quality × memory (arena_elo vs VRAM usage)
```

### :BEST_FOR
```
Computed by the full ranking algorithm:
  1. Filter by hardware + constraints
  2. Score by capability match to use case
  3. Weight by benchmarks + arena ELO
  4. Rank 1 = highest score for that use case + hardware combo
```
