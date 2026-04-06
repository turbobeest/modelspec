# Claude Code Setup Guide

## Step 1: Get the repo onto your Linux workstation

Download all files from this chat and put them in a directory. The key structure:

```
~/projects/modelspec/              ← This is your repo root
├── CLAUDE.md                      ← Claude Code reads this automatically
├── README.md
├── LICENSE
├── .gitignore
├── pyproject.toml
├── docker-compose.yml
├── schema/
│   ├── __init__.py
│   ├── enums.py                   ★ Controlled vocabularies (30 model types, etc.)
│   ├── card.py                    ★ 750-field ModelCard Pydantic schema
│   └── graph.py                   ★ FalkorDB ingestion + edge types
├── docs/
│   ├── graph-ontology.md          ★ Complete node/edge/property specification
│   ├── system-architecture-v3.md  ★ Full system design + Cypher examples
│   ├── model-card-template-v3.md  ★ Raw YAML template (750 fields)
│   ├── gap-analysis.md            Analysis of what V1 was missing
│   └── metadata-and-categories-audit.md  All metadata sources + model categories
├── models/                        Empty dirs, ready for model card YAML
│   ├── anthropic/
│   ├── openai/
│   ├── google/
│   ├── qwen/
│   ├── meta/
│   ├── mistral/
│   └── deepseek/
├── api/                           Empty scaffolds with __init__.py
│   ├── routes/
│   ├── ranking/
│   └── graph/
├── cli/
│   └── modelspec/
│       └── commands/
├── mcp/
├── researcher/
│   └── scrapers/
├── web/
│   └── src/
├── hardware/
├── scripts/
└── tests/
    ├── __init__.py
    └── test_schema.py             ★ Schema validation test (run this first!)
```

## Step 2: Initialize git and push to GitHub

```bash
cd ~/projects/modelspec
git init
git add .
git commit -m "Initial scaffold: 750-field schema, graph ontology, FalkorDB ingestion"
gh repo create modelspec --public --source=. --push
```

## Step 3: Start Claude Code

```bash
cd ~/projects/modelspec
claude
```

Claude Code will automatically read `CLAUDE.md` from the repo root and have full context on the project.

## Step 4: Verify the schema works

Tell Claude Code:
> Run the schema tests to make sure everything compiles

It should run:
```bash
pip install pydantic pyyaml
python tests/test_schema.py
```
Expected output: "750 fields, ALL TESTS PASSED"

## Step 5: Suggested first tasks for Claude Code

Here are good opening prompts, in order:

### Task 1: Start FalkorDB
> Start the FalkorDB docker container and verify it's running

### Task 2: Seed model cards from models.dev
> Write a scraper that pulls the models.dev API (https://models.dev/api.json), 
> generates skeleton model card YAML files for each model, and saves them to 
> the models/ directory. Map the TOML schema fields to our Pydantic ModelCard.

### Task 3: Ingest into the graph
> Load all model cards from models/ into FalkorDB using the ingest_model_card 
> function. Then run some Cypher queries to verify the graph looks right.

### Task 4: Build the CLI
> Implement the CLI using Typer: `modelspec info <model_id>` should query 
> FalkorDB and pretty-print the model card. `modelspec search` should support 
> --type, --hardware, --license, --origin-country filters.

### Task 5: Graph visualization
> Build a React frontend with a force-directed graph visualization using D3.
> Dark theme. Node types colored by model_type. Edge view toggles to switch 
> between relationship types (MADE_BY, DERIVED_FROM, COMPETES_WITH, FITS_ON, 
> AVAILABLE_ON). Legend showing node type counts. Search overlay.

## What Claude Code has access to via CLAUDE.md

Claude Code reads `CLAUDE.md` automatically and gets:
- Project purpose and architecture overview
- Tech stack and design decisions
- Complete project structure
- Schema details (node types, edge types, key relationships)
- Development commands
- Implementation roadmap with current phase highlighted
- UI vision description
- List of the 5 most important files to read

## What's NOT in the repo (context from this chat session)

Some design context from our conversation that's useful but lives in the chat:
- The network knowledge graph screenshot (dark theme inspiration for the UI)
- The iterative design process (V1→V2→V3 template evolution)
- The specific hardware profiles we're targeting (5090, DGX Spark, M4 Pro 64GB, M4 Air 24GB)
- The defense/government use case focus for downselect profiles

The key information from all of these is captured in `CLAUDE.md` and the `docs/` files,
so Claude Code should have everything it needs.
