# CLAUDE.md — Project Context for Claude Code

## What is this?

**ModelSpec** is an open-source model intelligence platform. It catalogs every AI model (LLMs, embeddings, image gen, safety classifiers, etc.) in a FalkorDB knowledge graph and serves recommendations through a Web UI, CLI, and MCP tool.

## Architecture

```
Web UI ─┐
CLI ────┤──▶ FastAPI ──▶ FalkorDB Knowledge Graph ◀── Backend Researcher (scrapers)
MCP ────┘                      │
                         Model Card Repo (YAML + Markdown)
```

## Key Design Decisions

1. **One universal template** for ALL model types (750 fields). Null = "not yet researched."
2. **The template IS the graph schema** — every YAML field maps to a node property or edge.
3. **Three graph layers**: factual (scraped), derived (computed), institutional (private overlay).
4. **12 node types, 22 edge types**, ~25K-50K edges at maturity.
5. **83 platform availability entries** per model — from AWS Bedrock to Ollama to Chinese platforms.

## Tech Stack

- **Graph DB**: FalkorDB (Redis-compatible, OpenCypher, GraphBLAS)
- **Backend**: Python 3.11+, FastAPI, Pydantic v2
- **Frontend**: React + TypeScript + Tailwind (dark theme, force-directed graph viz)
- **CLI**: Python, Typer + Rich
- **MCP**: Python mcp-sdk
- **Scrapers**: httpx + BeautifulSoup
- **Containers**: Docker Compose

## Project Structure

```
modelspec/
├── schema/              # ★ Source of truth — Pydantic models
│   ├── enums.py         # 30 model types, all controlled vocabularies
│   ├── card.py          # ModelCard: 750-field universal schema
│   └── graph.py         # FalkorDB nodes, edges, ingestion, Cypher
├── models/              # Model card YAML+Markdown files
├── api/                 # FastAPI backend (routes, ranking engine)
├── cli/                 # CLI tool (Typer)
├── mcp/                 # MCP server for agent integration
├── researcher/          # Automated scrapers and LLM gap-filler
├── web/                 # React frontend
├── hardware/            # Hardware profile definitions
├── docs/                # Design documents from planning phase
├── tests/
├── docker-compose.yml
└── pyproject.toml
```

## Schema Details

The `schema/` directory is the foundation everything else builds on:
- `enums.py` — ModelType (30 values), ArchitectureType, LicenseType, Tier, etc.
- `card.py` — `ModelCard` Pydantic model with 15 sections, YAML serialization, completeness tracking
- `graph.py` — `ingest_model_card()` takes a ModelCard and creates all FalkorDB nodes + edges

Run `python tests/test_schema.py` to validate the schema compiles (should show 750 fields, all tests pass).

## Graph Ontology

### Node Types
`:Model`, `:Provider`, `:Platform`, `:Capability`, `:Hardware`, `:Benchmark`, `:License`, `:Quantization`, `:UseCase`, `:DownselectProfile`, `:Runtime`, `:Tag`

### Key Edge Types
- `:MADE_BY` (Model→Provider)
- `:DERIVED_FROM` (Model→Model, with relation: finetune/quantized/merged/distilled)
- `:HAS_CAPABILITY` (Model→Capability, with tier property)
- `:SCORED_ON` (Model→Benchmark, with value + date)
- `:FITS_ON` (Model→Hardware, with quant/TPS/TTFT/memory)
- `:AVAILABLE_ON` (Model→Platform, with model_id + fine_tuning flag)
- `:COMPETES_WITH` (Model→Model, derived)
- `:APPROVED_BY` / `:EXCLUDED_BY` (DownselectProfile→Model, institutional)

Full ontology in `docs/graph-ontology.md`.

## Development Commands

```bash
# Start FalkorDB
docker compose up -d

# Install Python deps
pip install -e ".[dev]"

# Run schema tests
python tests/test_schema.py

# FalkorDB browser UI
open http://localhost:3000
```

## Implementation Roadmap (Current Phase: 1)

### Phase 1: Foundation ← WE ARE HERE
- [x] V3 universal template (750 fields)
- [x] Pydantic schema (card.py, enums.py)
- [x] Graph schema + ingestion (graph.py)
- [x] Docker Compose for FalkorDB
- [ ] Seed 30-50 model cards (scrape models.dev API → skeleton YAML)
- [ ] Ingestion pipeline: load cards into FalkorDB
- [ ] Basic CLI: `modelspec info`, `modelspec search`

### Phase 2: Ranking Engine
- [ ] 4-stage ranking pipeline (filter → score → rank → explain)
- [ ] CLI: `modelspec rank`, `modelspec compare`
- [ ] Hardware fit calculation logic

### Phase 3: Backend Researcher
- [ ] Scrapers: models.dev, HuggingFace, Ollama, LMArena, Artificial Analysis
- [ ] LLM gap-filler for qualitative fields
- [ ] New model detection

### Phase 4: Web UI
- [ ] Force-directed graph visualization (dark theme, edge view toggles)
- [ ] Explorer with faceted search
- [ ] Downselect wizard
- [ ] Compare view

### Phase 5: Agent Integration
- [ ] MCP server with recommend/compare/info/hardware_fit tools

## UI Vision

The graph visualization should be inspired by network knowledge graph UIs:
- Dark theme
- Force-directed + spatial layout modes
- Edge view toggles (switch between competition network, lineage tree, hardware fit, platform availability)
- Node coloring by model type
- Legend with node type counts
- Search overlay
- Click-through to model detail panels

## Important Files to Read First

1. `schema/card.py` — the 750-field ModelCard (this IS the project)
2. `schema/graph.py` — how cards become graph nodes + edges
3. `docs/graph-ontology.md` — complete node/edge/property specification
4. `docs/system-architecture-v3.md` — full system design with Cypher query examples
5. `docs/model-card-template-v3.md` — the raw YAML template
