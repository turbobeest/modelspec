# Model Intelligence Platform — System Architecture V3

## Project Name: **ModelSpec** (working title)

An open-source model intelligence platform that catalogs every AI model, maps it to hardware and use cases, and ranks recommendations through a knowledge graph.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACES                               │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────────┐    │
│  │   Web UI      │  │   CLI Tool    │  │  MCP / Agent Skill      │    │
│  │              │  │              │  │                         │    │
│  │  Browse       │  │  modelspec    │  │  Tool: recommend_models │    │
│  │  Filter       │  │   search     │  │  Tool: compare_models   │    │
│  │  Compare      │  │   compare    │  │  Tool: model_info       │    │
│  │  Downselect   │  │   rank       │  │  Tool: hardware_fit     │    │
│  │  Export       │  │   install    │  │                         │    │
│  └──────┬───────┘  └──────┬───────┘  └────────────┬────────────┘    │
│         │                  │                        │                  │
└─────────┼──────────────────┼────────────────────────┼─────────────────┘
          │                  │                        │
          ▼                  ▼                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        API LAYER (REST + GraphQL)                     │
│                                                                       │
│  /api/v1/models          — list, filter, search                      │
│  /api/v1/models/:id      — full model card                           │
│  /api/v1/rank            — ranked recommendations                    │
│  /api/v1/compare         — side-by-side comparison                   │
│  /api/v1/hardware/:id    — what fits on this hardware                │
│  /api/v1/downselect      — apply institutional constraints           │
│  /api/v1/graph           — direct Cypher queries (admin)             │
│  /api/v1/stats           — database coverage stats                   │
│                                                                       │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          ▼                      ▼                      ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│  RANKING ENGINE   │  │  FALKORDB GRAPH   │  │  BACKEND RESEARCHER   │
│                  │  │                  │  │                      │
│  Filter:         │  │  Nodes:          │  │  Scheduled jobs:     │
│   hardware_fit   │  │   :Model         │  │   sync_models_dev    │
│   license_ok     │  │   :Provider      │  │   scrape_huggingface │
│   downselect_ok  │  │   :Capability    │  │   scrape_benchmarks  │
│                  │  │   :Hardware      │  │   scrape_pricing     │
│  Score:          │  │   :License       │  │   scrape_performance │
│   capability     │  │   :Benchmark     │  │   scrape_arena       │
│   benchmark      │  │   :Quantization  │  │   fill_gaps (LLM)    │
│   custom_score   │  │   :UseCase       │  │   validate_cards     │
│   arena_elo      │  │   :Downselect    │  │                      │
│   cost_efficiency│  │   :CloudProvider │  │  Event-driven:       │
│                  │  │                  │  │   new_model_detected  │
│  Rank:           │  │  Edges:          │  │   benchmark_updated   │
│   weighted_sum   │  │   :MADE_BY       │  │   price_changed       │
│   pareto_front   │  │   :HAS_CAPABILITY│  │   model_deprecated    │
│                  │  │   :FITS_ON       │  │                      │
└──────────────────┘  │   :LICENSED_AS   │  └──────────────────────┘
                      │   :SCORED_ON     │
                      │   :AVAILABLE_ON  │
                      │   :AVAILABLE_AS  │
                      │   :DERIVED_FROM  │
                      │   :COMPETES_WITH │
                      │   :APPROVED_BY   │
                      │   :EXCLUDED_BY   │
                      │   :SUITED_FOR    │
                      └──────────────────┘
                               │
                               ▼
                      ┌──────────────────┐
                      │  MODEL CARD REPO  │
                      │  (Git)           │
                      │                  │
                      │  models/         │
                      │   anthropic/     │
                      │   openai/        │
                      │   qwen/          │
                      │   ...            │
                      └──────────────────┘
```

---

## Component 1: Web UI

### Purpose
Browser-based model discovery, comparison, and downselect tool. Think "PCPartPicker for AI models."

### Key Views

**1. Explorer View** — Browse all models with faceted filtering
- Left sidebar: filter panels for every template section
  - Model type (checkboxes: LLM, embedding, image gen, etc.)
  - Hardware fit (dropdown: "What device are you running?")
  - License (Apache-2.0, MIT, proprietary, etc.)
  - Origin country
  - Price range (slider)
  - Parameter count range (slider)
  - Capability tiers (coding, reasoning, tool use)
  - Status (active, beta, deprecated)
- Main area: model cards in grid or list view
- Sort by: arena ELO, custom score, price, parameters, release date, completeness
- Each card shows: name, type badge, param count, top 3 benchmark scores, hardware fit icons, price

**2. Downselect Wizard** — Guided narrowing from 500+ models to top 5
- Step 1: What's your use case? (coding, RAG, customer-facing chat, etc.)
- Step 2: What hardware? (select from profiles or add custom)
- Step 3: Constraints (license, origin country, compliance tags)
- Step 4: Priorities (rank: quality vs speed vs cost vs safety)
- Result: ranked shortlist with rationale for each recommendation

**3. Compare View** — Side-by-side model comparison (2-4 models)
- Unified diff-style comparison across all template fields
- Radar chart for capability tiers
- Benchmark table with highlighting for winners per category
- Cost comparison calculator (input your expected token volume)
- Hardware fit comparison matrix

**4. Model Detail View** — Full model card rendered from YAML
- All 15 sections rendered with progress bars for completeness
- Benchmark charts
- Hardware fit matrix with TPS/TTFT numbers
- Lineage graph (base model → forks → quantizations)
- "Similar models" recommendations
- Edit/contribute button (links to git repo)

**5. Admin / Downselect Profile Manager**
- Create institutional downselect profiles
- Tag models as approved/excluded
- Set custom scores
- Export approved model lists

### Tech Stack
- **Frontend**: React + TypeScript + Tailwind
- **State**: TanStack Query for API caching
- **Charts**: Recharts or Chart.js
- **Search**: Client-side filtering + server-side Cypher for complex queries
- **Auth**: Optional — needed only for downselect profiles
- **Deployment**: Static site + API backend, or single container

---

## Component 2: CLI Tool

### Purpose
Command-line interface for developers and agent pipelines. Install models, query rankings, integrate with CI/CD.

### Commands

```bash
# Search and filter
modelspec search "coding model under 8B that fits MacBook Air"
modelspec search --type llm-code --max-params 8B --hardware macbook_air_m4_24gb
modelspec search --capability tool_use:tier-1 --license apache-2.0

# Get full model card
modelspec info qwen/qwen3-30b-a3b
modelspec info qwen/qwen3-30b-a3b --section benchmarks
modelspec info qwen/qwen3-30b-a3b --format json

# Compare models
modelspec compare anthropic/claude-opus-4-6 openai/gpt-5 google/gemini-3.1-pro
modelspec compare --type llm-code --top 5

# Rank for a use case
modelspec rank --use-case agentic-coding --hardware nvidia_5090_32gb
modelspec rank --use-case rag-embedding --max-cost 0.10
modelspec rank --use-case customer-chat --downselect-profile my-org

# Hardware fit
modelspec hardware nvidia_5090_32gb             # what fits on this device
modelspec hardware macbook_air_m4_24gb --type llm-chat --top 10

# Downselect
modelspec downselect --profile dod-approved --hardware dgx_spark_128gb
modelspec downselect --no-cn-origin --license apache-2.0 --min-arena-elo 1400

# Install/setup (for local models)
modelspec install qwen/qwen3-30b-a3b --runtime ollama --quant Q4_K_M
modelspec install --recommended --hardware macbook_air_m4_24gb --use-case coding

# Database stats
modelspec stats                                # coverage report
modelspec stats --gaps                         # what fields need research
modelspec stats --type embedding-text          # category-specific coverage

# Agent skill mode (pipe-friendly JSON output)
modelspec rank --use-case coding --hardware macbook_air_m4_24gb --format json
```

### Tech Stack
- **Language**: Python (Click or Typer for CLI framework)
- **Distribution**: pip install modelspec + homebrew tap
- **Config**: ~/.modelspec/config.yaml for default hardware, downselect profiles
- **Cache**: Local SQLite cache of recent queries
- **Output**: Rich terminal formatting (Rich library) + JSON mode for piping

---

## Component 3: MCP Tool / Agent Skill

### Purpose
An MCP-compatible tool that any LLM agent can call to get model recommendations in context.

### Tool Definitions

```json
{
  "tools": [
    {
      "name": "recommend_models",
      "description": "Get ranked model recommendations for a use case, hardware, and constraints",
      "parameters": {
        "use_case": "string — what you need the model for (coding, rag, chat, embedding, image-gen, etc.)",
        "hardware": "string — target device (nvidia_5090_32gb, macbook_air_m4_24gb, api-only, etc.)",
        "constraints": {
          "license": "string — required license type",
          "origin_exclude": "array — country codes to exclude",
          "max_cost_per_million": "number — max $/M tokens",
          "min_arena_elo": "number",
          "downselect_profile": "string — institutional profile name",
          "model_type": "string — from taxonomy",
          "open_weights_required": "boolean"
        },
        "top_n": "number — how many results (default 5)"
      }
    },
    {
      "name": "compare_models",
      "description": "Compare 2-4 models across all dimensions",
      "parameters": {
        "model_ids": "array of model IDs to compare",
        "focus": "string — which dimensions to emphasize (benchmarks, cost, hardware, safety)"
      }
    },
    {
      "name": "model_info",
      "description": "Get complete information about a specific model",
      "parameters": {
        "model_id": "string",
        "sections": "array — which sections to return (all if empty)"
      }
    },
    {
      "name": "hardware_fit",
      "description": "What models fit on a specific device",
      "parameters": {
        "hardware": "string — device identifier",
        "model_type": "string — filter by type",
        "min_quality": "string — minimum capability tier"
      }
    }
  ]
}
```

### Integration Points
- **Claude Desktop**: MCP server config in claude_desktop_config.json
- **Claude Code**: MCP tool available in coding sessions
- **OpenAI function calling**: Compatible schema
- **LangChain/LangGraph**: Tool wrapper
- **Any MCP client**: Standard MCP server protocol

---

## Component 4: Backend Researcher

### Purpose
Automated system that discovers new models, scrapes metadata sources, fills gaps in model cards, and keeps the database current.

### Data Pipeline

```
┌───────────────────────────────────────────────────────────┐
│                    SCHEDULED SCRAPERS                       │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ models.dev   │  │ HuggingFace  │  │ Ollama      │       │
│  │ API sync     │  │ Hub API      │  │ Library     │       │
│  │ (daily)      │  │ (daily)      │  │ (daily)     │       │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │
│         │                 │                 │               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ Artificial   │  │ LMArena     │  │ HELM        │       │
│  │ Analysis     │  │ Leaderboard │  │ Leaderboard │       │
│  │ (weekly)     │  │ (weekly)    │  │ (weekly)    │       │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │
│         │                 │                 │               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ Provider     │  │ Cloud       │  │ Benchmark   │       │
│  │ Docs/APIs    │  │ Catalogs    │  │ Papers      │       │
│  │ (weekly)     │  │ (weekly)    │  │ (on-release)│       │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │
│         │                 │                 │               │
│         └────────────┬────┴────────────┬───┘               │
│                      ▼                 ▼                    │
│         ┌─────────────────────────────────────┐            │
│         │       NORMALIZATION LAYER            │            │
│         │                                     │            │
│         │  • Map external IDs to canonical ID │            │
│         │  • Convert units (costs, params)    │            │
│         │  • Validate against V3 schema       │            │
│         │  • Detect conflicts/contradictions  │            │
│         │  • Flag fields that changed         │            │
│         └───────────────┬─────────────────────┘            │
│                         ▼                                   │
│         ┌─────────────────────────────────────┐            │
│         │       GAP FILLER (LLM-assisted)     │            │
│         │                                     │            │
│         │  For each model card:               │            │
│         │  1. Calculate completeness %        │            │
│         │  2. Identify missing fields         │            │
│         │  3. For factual fields: search web  │            │
│         │  4. For qualitative fields: LLM     │            │
│         │     assessment from provider docs   │            │
│         │  5. Flag low-confidence fills       │            │
│         │  6. Queue for human review          │            │
│         └───────────────┬─────────────────────┘            │
│                         ▼                                   │
│         ┌─────────────────────────────────────┐            │
│         │       MODEL CARD WRITER             │            │
│         │                                     │            │
│         │  • Update YAML frontmatter          │            │
│         │  • Update prose sections            │            │
│         │  • Commit to git repo               │            │
│         │  • Trigger graph ingestion          │            │
│         └─────────────────────────────────────┘            │
│                                                             │
└───────────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  GRAPH INGESTION    │
              │                     │
              │  YAML → Cypher      │
              │  CREATE/MERGE nodes │
              │  CREATE/MERGE edges │
              │  Update indexes     │
              │  Validate integrity │
              └─────────────────────┘
```

### Scraper Priority Matrix

| Source | Frequency | Fields It Fills | Priority |
|---|---|---|---|
| models.dev API | Daily | Identity, cost, limits, modalities, capabilities | P0 |
| HuggingFace Hub API | Daily | Lineage, downloads, tags, license, architecture | P0 |
| Ollama Library | Daily | GGUF availability, tags, sizes | P0 |
| Provider pricing pages | Weekly | Cost section | P0 |
| LMArena API/scrape | Weekly | Arena ELO scores (6 categories) | P1 |
| Artificial Analysis | Weekly | Speed, latency, quality index | P1 |
| HELM results | Weekly | Safety scores, holistic eval | P1 |
| HF Open LLM Leaderboard | Weekly | GPQA, MATH, MMLU-Pro | P1 |
| LiveBench | Monthly | Contamination-resistant scores | P1 |
| Cloud provider catalogs | Weekly | Cloud availability, regions, compliance | P2 |
| Provider release blogs | On-release | Architecture details, training info | P2 |
| ArXiv papers | On-release | Technical details, benchmark claims | P2 |
| OpenRouter rankings | Weekly | Usage rankings | P2 |
| MTEB leaderboard | Monthly | Embedding benchmarks | P2 |
| MLX Community (HF) | Weekly | Apple Silicon availability | P2 |
| Community benchmarks (r/LocalLLaMA) | Monthly | Local inference TPS, hardware fit | P3 |

### New Model Detection

```
Event: new model appears in models.dev or HuggingFace trending
  → Create skeleton card with identity + lineage
  → Queue all scrapers for this model
  → LLM gap-filler runs on provider docs
  → Card reaches ~40% completeness automatically
  → Flag for human review of capability tiers
  → Publish to graph after validation
```

---

## Component 5: FalkorDB Knowledge Graph

### Node Types (complete)

```cypher
// Core entities
(:Model {id, display_name, model_type, model_subtypes, status,
         total_parameters, active_parameters, architecture_type,
         open_weights, origin_country, origin_org_type,
         context_window, max_input, max_output,
         cost_input, cost_output, arena_elo_overall,
         custom_score, card_completeness, release_date})

(:Provider {id, display_name, country, org_type, npm_package, api_endpoint})

(:Capability {id, category, name, description})
  // e.g. {id: "coding:agentic", category: "coding", name: "Agentic Coding"}

(:Hardware {id, display_name, memory_gb, memory_type, compute_type,
            architecture, tdp_watts})

(:License {id, type, commercial_ok, defense_ok, government_ok, medical_ok})

(:Quantization {id, format, bits, method})
  // e.g. {id: "Q4_K_M", format: "gguf", bits: 4, method: "k-quant"}

(:Benchmark {id, name, category, description, max_score, saturated})

(:UseCase {id, name, description, required_capabilities, typical_hardware})

(:DownselectProfile {id, name, institution, constraints})

(:CloudProvider {id, name, regions, compliance_certs})

(:Platform {id, name, category, url, notes})
  // category: cloud | inference | aggregator | ai-app | provider | cn-platform | regional | local | model-hub
  // e.g. {id: "groq", name: "Groq", category: "inference", url: "https://groq.com"}
  // e.g. {id: "cursor", name: "Cursor", category: "ai-app", url: "https://cursor.com"}
  // e.g. {id: "deepseek", name: "DeepSeek", category: "cn-platform", url: "https://platform.deepseek.com"}
  // ~83 platforms tracked per model

(:Runtime {id, name, url})
  // e.g. {id: "ollama", name: "Ollama"}, {id: "vllm", name: "vLLM"}
```

### Edge Types (complete)

```cypher
// Identity & lineage
(:Model)-[:MADE_BY]->(:Provider)
(:Model)-[:DERIVED_FROM {relation}]->(:Model)  // finetune, quantized, merged, distilled
(:Model)-[:LICENSED_AS]->(:License)

// Capabilities
(:Model)-[:HAS_CAPABILITY {tier, confidence}]->(:Capability)

// Hardware & deployment
(:Model)-[:FITS_ON {quant, vram_gb, tps, ttft_ms, max_context}]->(:Hardware)
(:Model)-[:AVAILABLE_AS {size_gb}]->(:Quantization)
(:Model)-[:RUNS_ON]->(:Runtime)
(:Model)-[:HOSTED_BY {regions, pricing_url}]->(:CloudProvider)
(:Model)-[:AVAILABLE_ON {model_id_on_platform, fine_tuning, gated, notes}]->(:Platform)

// Benchmarks
(:Model)-[:SCORED {value, date, source_url}]->(:Benchmark)

// Use cases & ranking
(:Model)-[:SUITED_FOR {rank, rationale, confidence}]->(:UseCase)

// Downselect
(:DownselectProfile)-[:APPROVES {date, reviewer}]->(:Model)
(:DownselectProfile)-[:EXCLUDES {reason, date}]->(:Model)

// Competition graph
(:Model)-[:COMPETES_WITH {dimension}]->(:Model)  // same-tier, same-category alternatives
```

### Indexes

```cypher
CREATE INDEX ON :Model(id)
CREATE INDEX ON :Model(model_type)
CREATE INDEX ON :Model(status)
CREATE INDEX ON :Model(origin_country)
CREATE INDEX ON :Model(open_weights)
CREATE INDEX ON :Model(total_parameters)
CREATE INDEX ON :Model(arena_elo_overall)
CREATE INDEX ON :Model(cost_input)
CREATE INDEX ON :Provider(id)
CREATE INDEX ON :Hardware(id)
CREATE INDEX ON :Benchmark(id)
CREATE INDEX ON :Benchmark(category)
CREATE INDEX ON :UseCase(id)
CREATE INDEX ON :DownselectProfile(id)
```

---

## Ranking Algorithm

The ranking engine applies a 4-stage pipeline:

### Stage 1: Hardware Filter
```
IF user specified hardware:
  MATCH (m:Model)-[:FITS_ON]->(h:Hardware {id: $hardware})
  WHERE m.status = 'active'
ELSE:
  MATCH (m:Model) WHERE m.status = 'active'
```

### Stage 2: Constraint Filter
```
Apply all hard constraints (boolean pass/fail):
  - license type matches requirement
  - origin_country not in exclusion list
  - model_type matches requirement
  - open_weights if required
  - downselect profile approves (if specified)
  - cost <= budget (if specified)
  - NOT excluded by downselect profile
```

### Stage 3: Score
```
For each surviving model, compute weighted score:

  score = (
    w_capability  * capability_match(model, use_case)  +  // 0-100
    w_benchmark   * benchmark_composite(model)         +  // 0-100 normalized
    w_arena       * arena_elo_normalized(model)        +  // 0-100
    w_cost        * cost_efficiency(model)             +  // 0-100 (inverse cost)
    w_speed       * speed_score(model, hardware)       +  // 0-100 (TPS)
    w_safety      * safety_score(model)                +  // 0-100
    w_adoption    * adoption_score(model)              +  // 0-100
    w_custom      * custom_score(model)                   // 0-100
  )

Default weights (adjustable by user):
  w_capability = 0.25
  w_benchmark  = 0.20
  w_arena      = 0.15
  w_cost       = 0.10
  w_speed      = 0.10
  w_safety     = 0.10
  w_adoption   = 0.05
  w_custom     = 0.05
```

### Stage 4: Rank & Explain
```
Sort by score DESC
Return top N with:
  - Rank
  - Score breakdown (which factors contributed most)
  - Key differentiators vs next-best alternative
  - Hardware fit details (quant, TPS, memory)
  - Caveats (missing benchmarks, low confidence fields)
```

---

## Tech Stack Summary

| Component | Technology | Rationale |
|---|---|---|
| Knowledge Graph | FalkorDB | GraphBLAS performance, OpenCypher, Redis-compatible |
| Backend API | Python (FastAPI) | Async, type-safe, ecosystem fit |
| Web UI | React + TypeScript + Tailwind | Standard, fast, component ecosystem |
| CLI | Python (Typer + Rich) | Clean CLI framework, beautiful terminal output |
| MCP Server | Python (mcp-sdk) | Standard MCP protocol |
| Scrapers | Python (httpx + BeautifulSoup + provider SDKs) | Async scraping |
| LLM Gap Filler | Claude API (via Anthropic SDK) | Best at structured data extraction |
| Model Card Repo | Git (GitHub) | Version control, PRs for community contributions |
| Task Queue | Celery + Redis (same Redis as FalkorDB) | Job scheduling for scrapers |
| Container | Docker Compose | Single `docker compose up` for full stack |

---

## Repository Structure

```
modelspec/
├── README.md
├── LICENSE                          # MIT
├── docker-compose.yml               # Full stack: FalkorDB + API + workers
├── schema/
│   └── model-card-v3.yaml           # The template (source of truth)
│
├── models/                          # Model card repository
│   ├── anthropic/
│   │   ├── claude-opus-4-6.md
│   │   ├── claude-sonnet-4-6.md
│   │   └── ...
│   ├── openai/
│   ├── google/
│   ├── qwen/
│   ├── meta/
│   ├── mistral/
│   ├── deepseek/
│   └── .../
│
├── api/                             # FastAPI backend
│   ├── main.py
│   ├── routes/
│   ├── ranking/
│   ├── graph/                       # FalkorDB queries
│   └── schemas/                     # Pydantic models from V3 template
│
├── web/                             # React frontend
│   ├── src/
│   │   ├── views/
│   │   │   ├── Explorer.tsx
│   │   │   ├── Downselect.tsx
│   │   │   ├── Compare.tsx
│   │   │   └── ModelDetail.tsx
│   │   ├── components/
│   │   └── hooks/
│   └── package.json
│
├── cli/                             # CLI tool
│   ├── modelspec/
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   ├── commands/
│   │   └── formatters/
│   └── pyproject.toml
│
├── mcp/                             # MCP server
│   ├── server.py
│   ├── tools.py
│   └── schema.json
│
├── researcher/                      # Backend researcher
│   ├── scrapers/
│   │   ├── models_dev.py
│   │   ├── huggingface.py
│   │   ├── ollama.py
│   │   ├── artificial_analysis.py
│   │   ├── lmarena.py
│   │   ├── helm.py
│   │   ├── cloud_catalogs.py
│   │   └── provider_docs.py
│   ├── gap_filler.py                # LLM-assisted field completion
│   ├── normalizer.py                # Data normalization
│   ├── ingestion.py                 # YAML → FalkorDB Cypher
│   ├── validator.py                 # Schema validation
│   └── scheduler.py                 # Cron job definitions
│
├── hardware/                        # Hardware profile definitions
│   ├── nvidia_5090_32gb.yaml
│   ├── dgx_spark_128gb.yaml
│   ├── macbook_m4_pro_64gb.yaml
│   ├── macbook_air_m4_24gb.yaml
│   └── README.md                    # How to add custom hardware
│
└── tests/
    ├── test_ranking.py
    ├── test_ingestion.py
    ├── test_scrapers.py
    └── test_schema.py
```

---

## Implementation Phases

### Phase 1: Foundation (Weeks 1-3)
- [ ] Finalize V3 template schema
- [ ] Build YAML → FalkorDB ingestion pipeline
- [ ] Seed 30-50 model cards (manually + models.dev API)
- [ ] Basic CLI: `modelspec info` and `modelspec search`
- [ ] Docker Compose for FalkorDB + API

### Phase 2: Ranking Engine (Weeks 4-5)
- [ ] Implement 4-stage ranking pipeline
- [ ] CLI: `modelspec rank` and `modelspec compare`
- [ ] Hardware fit calculation logic
- [ ] Downselect profile CRUD

### Phase 3: Backend Researcher (Weeks 6-8)
- [ ] Build scrapers for P0 sources (models.dev, HF, Ollama)
- [ ] Normalization layer
- [ ] LLM gap-filler for qualitative fields
- [ ] Automated card generation for new models
- [ ] Scheduler (Celery)

### Phase 4: Web UI (Weeks 8-11)
- [ ] Explorer view with faceted search
- [ ] Model detail view
- [ ] Compare view
- [ ] Downselect wizard

### Phase 5: Agent Integration (Weeks 11-12)
- [ ] MCP server implementation
- [ ] Tool schema definitions
- [ ] Claude Desktop integration test
- [ ] Claude Code integration test

### Phase 6: Community & Polish (Ongoing)
- [ ] Contribution guide for model cards
- [ ] GitHub Actions for schema validation on PR
- [ ] Coverage dashboard
- [ ] Public API documentation
- [ ] Homebrew formula for CLI
