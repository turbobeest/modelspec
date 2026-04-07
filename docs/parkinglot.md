# Parking Lot

Ideas, future features, and design questions that aren't ready for implementation yet.

---

## Downselect Profiles (YAML/JSON presets)

**Date**: 2026-04-07
**Priority**: High — enables programmatic/agent use of ModelSpec

### The Problem

A user or agent has a known operational environment (hardware, hosting, compliance) and needs to quickly answer: "What's the best model for THIS specific task?" without re-specifying their entire environment every time.

### Example Scenario

An agent building system has a complex prompt. It knows:
- It runs on a MacBook M4 Max 128GB
- It needs local hosting (Ollama)
- It needs US-origin models only
- The task is: "best Rust coding model right now"

Today this requires manually clicking through the downselect UI or constructing a POST body. It should be a one-liner:

```bash
# Load environment from a saved profile, override with task-specific needs
modelspec rank --profile ~/.modelspec/my-env.yaml --use-case coding --lang rust
```

### Proposed: Downselect Profile Format

```yaml
# ~/.modelspec/profiles/local-mac.yaml
name: "Local Mac Development"
description: "M4 Max 128GB, US-only, open weights, Ollama"

environment:
  hosting: [local]
  runtime: [ollama]
  hardware:
    preset: mbpro_m4max  # or explicit specs:
    # memory_gb: 128
    # bandwidth_gbps: 546
    # tops: 152
    # quant: Q8

constraints:
  open_weights: true
  origin_countries: [US]
  openai_compatible: true
  min_context: 32000
  max_cost_input: null  # local = free

# Default use case if none specified
default_use_case: general
```

Then queries become:
```bash
modelspec rank --profile local-mac --use-case coding --top 5
modelspec rank --profile local-mac --use-case embedding
modelspec rank --profile cloud-prod --use-case agentic --lang rust
```

### The `--lang` Problem: Language-Specific Coding Benchmarks

Current coding benchmarks (HumanEval, SWE-bench) are mostly Python-centric. For "best Rust model", we need:

1. **MultiPL-E** — translates HumanEval to 18 languages including Rust, Go, Java, TypeScript
2. **Aider Polyglot** — already in our schema, tests multi-language coding
3. **Language-specific leaderboards**: 
   - Rust: no dedicated leaderboard exists yet
   - TypeScript: partially covered by SWE-bench
   - There are informal benchmarks (e.g., "Rust port of HumanEval") but nothing standardized

**What we could do:**
- Add `benchmarks.multipl_e_rust`, `multipl_e_typescript`, etc. to the schema (or a dict of per-language scores)
- Scrape MultiPL-E results from the HuggingFace leaderboard
- For now: use Aider Polyglot as a proxy for multi-language coding ability
- Long-term: community-contributed language-specific eval results

### Deeper Capability Nuance

The user's real question isn't just "good at coding" — it's "good at Rust specifically, with agentic capabilities, running locally." This requires:

1. **Capability taxonomy expansion**: 
   - `capabilities.coding.languages` already exists (list of strong languages)
   - Need to populate it from benchmarks and community data
   - Need per-language scoring, not just a list

2. **Compound queries**: The ranking engine should support:
   ```yaml
   use_case: coding
   task_specifics:
     languages: [rust]
     agentic: true
     long_context: true  # big codebases
   ```

3. **LLM-as-judge for nuance**: For questions like "which model handles Rust borrow checker errors best?", no benchmark exists. This could be:
   - Community-reported capability tags
   - LLM-evaluated micro-benchmarks
   - A "task description" field that the ranking engine interprets with an LLM

---

## Agent-Facing API (MCP / Tool Use)

**Date**: 2026-04-07

An MCP server that agents can call to get model recommendations mid-task:

```python
# Agent's inner loop:
result = mcp.call("modelspec.recommend", {
    "task": "Generate and compile Rust code with complex lifetime annotations",
    "environment": "local-mac",  # references a saved profile
    "constraints": {"max_latency_ms": 500}
})
best_model = result["ranked"][0]["model_id"]
# Agent switches to using that model for this subtask
```

---

## Sparse YAML Cards

**Date**: 2026-04-07

Current model cards dump all 750 fields even when null. Switch to `exclude_defaults=True` in serialization — a card with 30 known fields should be 30 lines, not 900.

---

## Live Benchmark Scraping

**Date**: 2026-04-07

Scheduled scraping from:
- LMArena (Arena ELO, refreshes weekly)
- Artificial Analysis (speed/cost, refreshes daily)
- Open LLM Leaderboard (HuggingFace, refreshes on new submissions)
- MultiPL-E (per-language coding scores)
- LiveCodeBench (continuously updated coding eval)
- SEAL Leaderboards (safety evals)

Could run as a GitHub Action on a schedule, auto-PRing new data.

---

## Hardware Profiling Tool

**Date**: 2026-04-07

A CLI command that benchmarks your actual hardware:

```bash
modelspec benchmark --model qwen3:14b --runtime ollama
# Runs a standardized prompt, measures:
#   - TTFT (time to first token)
#   - Output tok/s
#   - Peak memory usage
#   - Quality (optional: run a mini eval)
# Submits results to the community database
```

This would replace our estimated tok/s with real measurements.

---

## Model Comparison Deep Dive

**Date**: 2026-04-07

Side-by-side comparison page in the web UI:
- Pick 2-4 models
- Radar chart of capabilities
- Benchmark score overlay
- Cost/quality Pareto frontier
- "When to use A vs B" generated summary

---

## Institutional Overlay (Phase 5)

**Date**: 2026-04-07

Private downselect profiles for organizations:
- Compliance tags (FedRAMP, HIPAA, CMMC)
- Approved/excluded model lists
- Custom scoring weights
- Audit trail for model selection decisions

---
