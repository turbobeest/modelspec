# ModelSpec

An open-source model intelligence platform. Catalog every AI model, map it to your hardware and use cases, rank what's best for you.

**ModelSpec** maintains a knowledge graph of AI models — LLMs, embedding models, image generators, safety classifiers, and everything in between — enriched with benchmark scores, hardware compatibility, licensing details, platform availability, and institutional compliance data. Query it through a web UI, CLI, or MCP tool.

## Why this exists

There's no single place that answers: *"What's the best model I can actually run on my hardware, for my use case, that my organization is allowed to use?"*

- **models.dev** tracks pricing and context limits but not hardware fit or benchmarks
- **HuggingFace** has model cards but no ranking engine
- **LMArena** has human preference scores but no deployment guidance
- **Artificial Analysis** has speed benchmarks but no compliance data

ModelSpec synthesizes **25+ data sources** into a unified knowledge graph with **~750 fields per model** across a universal template that covers all model types.

## Architecture

```
Web UI ─┐
CLI ────┤──▶ API Layer ──▶ FalkorDB Knowledge Graph ◀── Backend Researcher
MCP ────┘                       │                         (25+ scrapers)
                          Model Card Repo
                          (YAML + Markdown)
```

- **12 node types**, **22 edge types**, estimated **25K-50K edges** at maturity
- **83 platform availability** entries per model (from AWS Bedrock to Ollama)
- **50+ benchmark** slots across 10 categories
- **4 hardware profiles** with per-device TPS/TTFT/memory measurements
- **Institutional downselect** overlays for defense, government, compliance

## Quick Start

```bash
# Clone and start the stack
git clone https://github.com/YOUR_ORG/modelspec.git
cd modelspec
docker compose up -d

# Install the CLI
pip install -e ./cli

# Search for models
modelspec search --type llm-chat --hardware macbook_air_m4_24gb
modelspec rank --use-case agentic-coding --hardware nvidia_5090_32gb
modelspec info qwen/qwen3-30b-a3b
```

## Project Structure

```
modelspec/
├── schema/              # Pydantic models — the source of truth
│   ├── card.py          # Universal model card schema (~750 fields)
│   ├── graph.py         # Node and edge type definitions
│   └── enums.py         # Controlled vocabularies (model types, tiers, etc.)
├── models/              # Model card repository (YAML + Markdown)
│   ├── anthropic/
│   ├── openai/
│   ├── qwen/
│   └── .../
├── api/                 # FastAPI backend
├── cli/                 # Command-line tool
├── mcp/                 # MCP server for agent integration
├── researcher/          # Automated scrapers and gap-filler
├── web/                 # React frontend
├── hardware/            # Hardware profile definitions
├── docker-compose.yml
└── pyproject.toml
```

## Schema

Every model gets a single YAML+Markdown file following the V3 Universal Template. The template covers **all model types** (LLMs, embeddings, image gen, safety classifiers, etc.) in one schema. Null fields = not yet researched.

See [schema/](./schema/) for the Pydantic models.

## Contributing

We need help with:
- **Model cards**: Add or update YAML data for models you know well
- **Benchmarks**: Help us track scores from new evaluation suites
- **Hardware testing**: Measure TPS/TTFT/memory on your devices
- **Scrapers**: Build connectors to new data sources
- **UI/UX**: The graph visualization needs to be extraordinary

## License

MIT
