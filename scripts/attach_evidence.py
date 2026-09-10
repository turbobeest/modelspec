#!/usr/bin/env python3
"""Attach reviewed benchmark evidence from the census ledger onto model cards.

The census verifies results against their sources and records them in
`benchmarks/_census/eligibility/current-report.json`. Ranking-profile evidence
extracted from dated primary-source pages lives in
`benchmarks/_census/ranking_evidence/accepted.json`. Those records identify a
model by the name the evaluator used — "GPT-6 Astra (max)" — which is not a
ModelSpec model_id and frequently is not any single card.

**Mapping is explicit and never inferred.** Attaching a score to the wrong model
is worse than attaching nothing: it produces a confident, sourced, dated,
verified-looking claim about a model nobody evaluated. An unmapped identifier is
reported and skipped.

    python scripts/attach_evidence.py --dry-run
    python scripts/attach_evidence.py
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import yaml  # noqa: E402

from schema.card import BenchmarkEvidence, ModelCard  # noqa: E402

REPORT = PROJECT_ROOT / "benchmarks/_census/eligibility/current-report.json"
RANKING_LEDGER = PROJECT_ROOT / "benchmarks/_census/ranking_evidence/accepted.json"
LEDGER_PATHS = (REPORT, RANKING_LEDGER)

#: Evaluator's model identifier -> ModelSpec model_id.
#:
#: Every entry here is a human judgement that two names denote the same model.
#: Add one only after checking the evaluator's configuration notes: a "(max)"
#: suffix, a reasoning-effort setting or a dated snapshot can all mean the
#: evaluated model is *not* the card you would first reach for.
LEDGER_TO_CARD: dict[str, str] = {
    "GPT-6 Astra (max)": "openai/gpt-6-astra",
    "GPT-5.6 Sol": "openai/gpt-5-6-sol",
    "GPT-5.6 Terra": "openai/gpt-5-6-terra",
    "GPT-5.6 Luna": "openai/gpt-5-6-luna",
    "Claude Opus 4.8": "anthropic/claude-opus-4-8",
    "Claude Opus 5": "anthropic/claude-opus-5",
    "Claude Sonnet 5": "anthropic/claude-sonnet-5",
    "Gemma 4 31B IT": "google/gemma-4-31b-it",
    "GLM-5.1": "zhipu/glm-5-1",
    "Llama 4 Scout Instruct": "meta/llama-4-scout-17b-16e-instruct",
    "Llama 4 Maverick Instruct": "meta/llama-4-maverick-17b-128e-instruct",
    "Qwen3-32B (thinking)": "qwen/qwen3-32b",
    "DeepSeek-V4-Pro (max)": "deepseek/deepseek-v4-pro",
    "DeepSeek-V4-Flash (max)": "deepseek/deepseek-v4-flash",
    # Live AA / LM Arena names. Explicit unique matches only.
    # Effort rows (high/low/medium/xhigh/thinking) stay unmapped.
    # "(max)" is the boards' canonical product row, same judgement as Astra.
    "Molmo2-8B": "allen-ai/molmo2-8b",
    "Olmo 3.1 32B Instruct": "allen-ai/olmo-3-1-32b-instruct",
    "Olmo 3 7B Think": "allen-ai/olmo-3-7b-think",
    "claude-3-5-sonnet-20241022": "anthropic/claude-3-5-sonnet-20241022",
    "claude-3-7-sonnet-20250219": "anthropic/claude-3-7-sonnet-20250219",
    "claude-fable-5": "anthropic/claude-fable-5",
    "claude-fable-5.1-max": "anthropic/claude-fable-5-1",
    "claude-haiku-4-5-20251001": "anthropic/claude-haiku-4-5-20251001",
    "claude-opus-4-1-20250805": "anthropic/claude-opus-4-1-20250805",
    "claude-opus-4-20250514": "anthropic/claude-opus-4-20250514",
    "Claude Opus 4.5": "anthropic/claude-opus-4-5-20251101",
    "claude-opus-4-5-20251101": "anthropic/claude-opus-4-5-20251101",
    "Claude Opus 4.6 (max)": "anthropic/claude-opus-4-6",
    "claude-opus-4-6": "anthropic/claude-opus-4-6",
    "Claude Opus 4.7 (max)": "anthropic/claude-opus-4-7",
    "claude-opus-4-7": "anthropic/claude-opus-4-7",
    "Claude Opus 4.8 (max)": "anthropic/claude-opus-4-8",
    "claude-opus-4-8": "anthropic/claude-opus-4-8",
    "Claude Opus 5 (max)": "anthropic/claude-opus-5",
    "claude-opus-5-max": "anthropic/claude-opus-5",
    "claude-sonnet-4-20250514": "anthropic/claude-sonnet-4-20250514",
    "claude-sonnet-4-5-20250929": "anthropic/claude-sonnet-4-5-20250929",
    "Claude Sonnet 4.6 (max)": "anthropic/claude-sonnet-4-6",
    "claude-sonnet-4-6": "anthropic/claude-sonnet-4-6",
    "Claude Sonnet 5 (max)": "anthropic/claude-sonnet-5",
    "gpt-oss-120b": "cerebras/gpt-oss-120b",
    "Qwen3.8 27B": "cerebras/qwen-3-8-27b",
    "qwen3.8-27b": "cerebras/qwen-3-8-27b",
    "Command A": "cohere/command-a-03-2025",
    "command-a-03-2025": "cohere/command-a-03-2025",
    "Command A+": "cohere/command-a-plus-05-2026",
    "North Mini Code": "cohere/north-mini-code-1-0",
    "deepseek-r1": "deepseek/deepseek-r1",
    "DeepSeek R1 0528": "deepseek/deepseek-r1-0528",
    "deepseek-r1-0528": "deepseek/deepseek-r1-0528",
    "DeepSeek R1 0528 Qwen3 8B": "deepseek/deepseek-r1-0528-qwen3-8b",
    "DeepSeek R1 Distill Llama 70B": "deepseek/deepseek-r1-distill-llama-70b",
    "DeepSeek R1 Distill Llama 8B": "deepseek/deepseek-r1-distill-llama-8b",
    "DeepSeek R1 Distill Qwen 1.5B": "deepseek/deepseek-r1-distill-qwen-1-5b",
    "DeepSeek R1 Distill Qwen 14B": "deepseek/deepseek-r1-distill-qwen-14b",
    "DeepSeek R1 Distill Qwen 32B": "deepseek/deepseek-r1-distill-qwen-32b",
    "deepseek-v3": "deepseek/deepseek-v3",
    "DeepSeek V3 0324": "deepseek/deepseek-v3-0324",
    "deepseek-v3-0324": "deepseek/deepseek-v3-0324",
    "DeepSeek V3.1": "deepseek/deepseek-v3-1",
    "deepseek-v3.1": "deepseek/deepseek-v3-1",
    "DeepSeek V3.2": "deepseek/deepseek-v3-2",
    "deepseek-v3.2": "deepseek/deepseek-v3-2",
    "DeepSeek V3.2 Exp": "deepseek/deepseek-v3-2-exp",
    "deepseek-v3.2-exp": "deepseek/deepseek-v3-2-exp",
    "DeepSeek V4 Flash (max)": "deepseek/deepseek-v4-flash",
    "deepseek-v4-flash": "deepseek/deepseek-v4-flash",
    "DeepSeek V4 Pro (max)": "deepseek/deepseek-v4-pro",
    "deepseek-v4-pro": "deepseek/deepseek-v4-pro",
    "Gemini 1.5 Flash-8B": "google/gemini-1-5-flash-8b",
    "Gemini 2.0 Flash": "google/gemini-2-0-flash",
    "Gemini 2.5 Flash": "google/gemini-2-5-flash",
    "gemini-2.5-flash": "google/gemini-2-5-flash",
    "Gemini 2.5 Flash-Lite": "google/gemini-2-5-flash-lite",
    "Gemini 2.5 Pro": "google/gemini-2-5-pro",
    "gemini-2.5-pro": "google/gemini-2-5-pro",
    "Gemini 3.1 Flash-Lite": "google/gemini-3-1-flash-lite",
    "Gemini 3.1 Pro Preview": "google/gemini-3-1-pro-preview",
    "Gemini 3.5 Flash": "google/gemini-3-5-flash",
    "Gemini 3.5 Flash-Lite": "google/gemini-3-5-flash-lite",
    "gemini-3.5-flash-lite": "google/gemini-3-5-flash-lite",
    "Gemini 3.6 Flash": "google/gemini-3-6-flash",
    "Gemma 3 12B": "google/gemma-3-12b-it",
    "Gemma 3 27B": "google/gemma-3-27b-it",
    "gemma-3-27b-it": "google/gemma-3-27b-it",
    "Gemma 3 4B": "google/gemma-3-4b-it",
    "gemma-4-31b": "google/gemma-4-31b",
    "Granite 4.0 1B": "ibm/granite-4-0-1b",
    "Granite 4.0 350M": "ibm/granite-4-0-350m",
    "Granite 4.0 H 1B": "ibm/granite-4-0-h-1b",
    "Granite 4.0 H 350M": "ibm/granite-4-0-h-350m",
    "Granite 4.0 H Small": "ibm/granite-4-0-h-small",
    "Granite 4.0 Micro": "ibm/granite-4-0-micro",
    "Mercury 2": "inception/mercury-2",
    "LFM2.5-1.2B-Instruct": "liquid/lfm2-5-1-2b-instruct",
    "LFM2.5-VL-1.6B": "liquid/lfm2-5-vl-1-6b",
    "LFM2 8B A1B": "liquid/lfm2-8b-a1b",
    "Llama 3.2 11B (Vision)": "meta/llama-3-2-11b-vision",
    "Llama 3.2 90B (Vision)": "meta/llama-3-2-90b-vision",
    "Muse Spark": "meta/muse-spark",
    "muse-spark": "meta/muse-spark",
    "Phi-4": "microsoft/phi-4",
    "MiniMax-M2": "minimax/minimax-m2",
    "MiniMax-M2.1": "minimax/minimax-m2-1",
    "MiniMax-M2.5": "minimax/minimax-m2-5",
    "minimax-m2.5": "minimax/minimax-m2-5",
    "MiniMax-M2.7": "minimax/minimax-m2-7",
    "minimax-m2.7": "minimax/minimax-m2-7",
    "MiniMax-M3": "minimax/minimax-m3",
    "minimax-m3": "minimax/minimax-m3",
    "Devstral Medium": "mistral/devstral-medium-2507",
    "Devstral Small": "mistral/devstral-small-2507",
    "Devstral Small 2": "mistral/labs-devstral-small-2512",
    "Mistral Large 3": "mistral/mistral-large-2512",
    "mistral-large-3": "mistral/mistral-large-2512",
    "Mistral Medium 3": "mistral/mistral-medium-2505",
    "Mistral Medium 3.1": "mistral/mistral-medium-2508",
    "Mistral Medium 3.5": "mistral/mistral-medium-2604",
    "Mistral Small 3.2": "mistral/mistral-small-2506",
    "mistral-small-2506": "mistral/mistral-small-2506",
    "Mistral Small 4": "mistral/mistral-small-2603",
    "Mistral 7B": "mistral/open-mistral-7b",
    "Mixtral 8x22B": "mistral/open-mixtral-8x22b",
    "Mixtral 8x7B": "mistral/open-mixtral-8x7b",
    "Kimi K2 0905": "moonshot/kimi-k2-0905-preview",
    "Kimi K2.5": "moonshot/kimi-k2-5",
    "Kimi K2.6": "moonshot/kimi-k2-6",
    "kimi-k2.6": "moonshot/kimi-k2-6",
    "Kimi K2.7 Code": "moonshot/kimi-k2-7-code",
    "Kimi K2 Thinking": "moonshot/kimi-k2-thinking",
    "Kimi K3 (max)": "moonshot/kimi-k3",
    "kimi-k3-max": "moonshot/kimi-k3",
    "Nemotron Cascade 2 30B A3B": "nvidia/nemotron-cascade-2-30b-a3b",
    "NVIDIA Nemotron Nano 9B V2": "nvidia/nvidia-nemotron-nano-9b-v2",
    "GPT-4": "openai/gpt-4",
    "GPT-4.1": "openai/gpt-4-1",
    "GPT-4.1 mini": "openai/gpt-4-1-mini",
    "GPT-4.1 nano": "openai/gpt-4-1-nano",
    "GPT-4o mini": "openai/gpt-4o-mini",
    "gpt-5.4": "openai/gpt-5-4",
    "GPT-5.4 nano": "openai/gpt-5-4-nano",
    "gpt-5.5": "openai/gpt-5-5",
    "GPT-5.6 Luna (max)": "openai/gpt-5-6-luna",
    "GPT-5.6 Sol (max)": "openai/gpt-5-6-sol",
    "GPT-5.6 Terra (max)": "openai/gpt-5-6-terra",
    "o1": "openai/o1",
    "o1-mini": "openai/o1-mini",
    "o1-preview": "openai/o1-preview",
    "o3": "openai/o3",
    "o3-mini": "openai/o3-mini",
    "o3-pro": "openai/o3-pro",
    "Sonar": "perplexity/sonar",
    "Sonar Pro": "perplexity/sonar-pro",
    "DeepSeek V4 Flash 0731 (max)": "qwen/deepseek-v4-flash-0731",
    "Qwen3 1.7B": "qwen/qwen3-1-7b",
    "Qwen3 14B": "qwen/qwen3-14b",
    "qwen3-235b-a22b": "qwen/qwen3-235b-a22b",
    "qwen3-30b-a3b-instruct-2507": "qwen/qwen3-30b-a3b-instruct-2507",
    "Qwen3 32B": "qwen/qwen3-32b",
    "Qwen3 4B": "qwen/qwen3-4b",
    "Qwen3.5 0.8B": "qwen/qwen3-5-0-8b",
    "Qwen3.5 122B A10B": "qwen/qwen3-5-122b-a10b",
    "qwen3.5-122b-a10b": "qwen/qwen3-5-122b-a10b",
    "Qwen3.5 27B": "qwen/qwen3-5-27b",
    "qwen3.5-27b": "qwen/qwen3-5-27b",
    "Qwen3.5 2B": "qwen/qwen3-5-2b",
    "Qwen3.5 35B A3B": "qwen/qwen3-5-35b-a3b",
    "qwen3.5-35b-a3b": "qwen/qwen3-5-35b-a3b",
    "Qwen3.5 397B A17B": "qwen/qwen3-5-397b-a17b",
    "qwen3.5-397b-a17b": "qwen/qwen3-5-397b-a17b",
    "Qwen3.5 4B": "qwen/qwen3-5-4b",
    "Qwen3.5 9B": "qwen/qwen3-5-9b",
    "Qwen3.6 27B": "qwen/qwen3-6-27b",
    "Qwen3.6 35B A3B": "qwen/qwen3-6-35b-a3b",
    "Qwen3.6 Max Preview": "qwen/qwen3-6-max-preview",
    "Qwen3.6 Plus": "qwen/qwen3-6-plus",
    "qwen3.6-plus": "qwen/qwen3-6-plus",
    "Qwen3.7 Max": "qwen/qwen3-7-max",
    "Qwen3.7 Plus": "qwen/qwen3-7-plus",
    "qwen3.7-plus": "qwen/qwen3-7-plus",
    "Qwen3.8 Max": "qwen/qwen3-8-max",
    "Qwen3 8B": "qwen/qwen3-8b",
    "qwen3-coder-480b-a35b-instruct": "qwen/qwen3-coder-480b-a35b-instruct",
    "Qwen3 Coder Next": "qwen/qwen3-coder-next",
    "Qwen3 Max": "qwen/qwen3-max",
    "qwen3-next-80b-a3b-instruct": "qwen/qwen3-next-80b-a3b-instruct",
    "Qwen3 VL 235B A22B": "qwen/qwen3-vl-235b-a22b",
    "Qwen3 VL 30B A3B": "qwen/qwen3-vl-30b-a3b",
    "Step 3.5 Flash": "stepfun/step-3-5-flash",
    "step-3.5-flash": "stepfun/step-3-5-flash",
    "Step 3.5 Flash 2603": "stepfun/step-3-5-flash-2603",
    "Step 3.7 Flash": "stepfun/step-3-7-flash",
    "Falcon-H1R-7B": "tii/falcon-h1r-7b",
    "Solar Pro 4": "upstage/solar-pro4",
    "solar-pro4": "upstage/solar-pro4",
    "Grok 2": "xai/grok-2",
    "Grok 3": "xai/grok-3",
    "Grok 4": "xai/grok-4",
    "Grok 4.1 Fast": "xai/grok-4-1-fast",
    "Grok 4.1 Fast (Non-reasoning)": "xai/grok-4-1-fast-non-reasoning",
    "grok-4.3": "xai/grok-4-3",
    "grok-4.5": "xai/grok-4-5",
    "Grok 4 Fast": "xai/grok-4-fast",
    "Grok 4 Fast (Non-reasoning)": "xai/grok-4-fast-non-reasoning",
    "Grok Beta": "xai/grok-beta",
    "Grok Code Fast 1": "xai/grok-code-fast-1",
    "GLM-4.5": "zhipu/glm-4-5",
    "glm-4.5": "zhipu/glm-4-5",
    "GLM-4.5-Air": "zhipu/glm-4-5-air",
    "glm-4.5-air": "zhipu/glm-4-5-air",
    "GLM-4.5V": "zhipu/glm-4-5v",
    "glm-4.5v": "zhipu/glm-4-5v",
    "GLM-4.6": "zhipu/glm-4-6",
    "glm-4.6": "zhipu/glm-4-6",
    "GLM-4.6V": "zhipu/glm-4-6v",
    "glm-4.6v": "zhipu/glm-4-6v",
    "GLM-4.7": "zhipu/glm-4-7",
    "glm-4.7": "zhipu/glm-4-7",
    "GLM-4.7-Flash": "zhipu/glm-4-7-flash",
    "glm-4.7-flash": "zhipu/glm-4-7-flash",
    "GLM-5": "zhipu/glm-5",
    "glm-5": "zhipu/glm-5",
    "glm-5.1": "zhipu/glm-5-1",
    "GLM-5.3 (max)": "zhipu/glm-5-3",
    "glm-5.3-max": "zhipu/glm-5-3",
    "GLM-5.3-Flash": "zhipu/glm-5-3-flash",
    "glm-5.3-flash": "zhipu/glm-5-3-flash",
    # MODEL-13: cards that existed only after the live-board harvest.
    # Unique identity checked against AA slug/creator (or Arena org), not
    # inferred from a family name. Effort / quant / sibling-size rows stay out.
    "Inkling": "thinkingmachines/inkling",
    "inkling": "thinkingmachines/inkling",
    "Nemotron 3.5 Lightning": "nvidia/nvidia-nemotron-3-5-lightning-30b-a3b",
    "Nemotron 3 Ultra": "nvidia/nvidia-nemotron-3-ultra-550b-a55b",
    "Cogito v2.1": "deepcogito/cogito-671b-v2-1",
    "muse-glimmer": "meta/muse-glimmer-30b",
    # Unmapped on purpose:
    # "Claude Opus 5 (high)" / other effort rows — not the product card.
    # "GLM-5.2 (max)" — two cards (mistral/zai-glm-5-2, qwen/glm-5-2).
    # "Qwen3.8-Max" as a *static* HF score still has no stated day;
    # the live AA row is mapped separately as "Qwen3.8 Max".
    # "Muse Glimmer (high)" — effort row, not meta/muse-glimmer-30b.
    # "Inkling Small" — distinct later size, not thinkingmachines/inkling.
    # NVFP4 Lightning/Ultra Arena rows — serving quants, not the BF16 cards.
    # "Llama Nemotron Ultra" — Llama 3.1 Nemotron Ultra 253B, not 3 Ultra.
    # "rnj-1" / "rnj-1-base-evals" — a dataset, not essentialai/rnj-1-instruct.
    # Claude Mythos 5 / 5.1 — no primary ranked score in the census.
}


def load_accepted() -> list[tuple[str, dict]]:
    accepted: list[tuple[str, dict]] = []
    for path in LEDGER_PATHS:
        if not path.is_file():
            continue
        report = json.loads(path.read_text(encoding="utf-8"))
        accepted.extend(
            (row["canonical_id"], result)
            for row in report.get("rows", [])
            if row.get("status") == "active"
            for result in row.get("accepted_results", [])
        )
    return accepted


def to_evidence(benchmark_id: str, raw: dict, verified_at: str) -> BenchmarkEvidence:
    return BenchmarkEvidence(
        benchmark_id=benchmark_id,
        model_id_as_evaluated=raw["model_id"],
        score=float(raw["score"]),
        unit=str(raw.get("unit") or ""),
        source_url=raw["source_url"],
        source_kind=raw["source_kind"],
        evidence_date=raw["evidence_date"],
        date_type=raw["date_type"],
        verified_at=raw.get("verified_at") or verified_at,
        benchmark_version=str(raw.get("benchmark_version") or ""),
        configuration=str(raw.get("configuration") or ""),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--only",
        default="",
        help="comma-separated model_ids to write; default is every mapped card",
    )
    args = parser.parse_args()
    only = {part.strip() for part in args.only.split(",") if part.strip()} or None

    accepted = load_accepted()
    today = date.today().isoformat()

    by_card: dict[str, list[BenchmarkEvidence]] = {}
    unmapped: dict[str, int] = {}

    for benchmark_id, raw in accepted:
        model_id = LEDGER_TO_CARD.get(raw["model_id"])
        if not model_id:
            unmapped[raw["model_id"]] = unmapped.get(raw["model_id"], 0) + 1
            continue
        by_card.setdefault(model_id, []).append(to_evidence(benchmark_id, raw, today))

    print(f"{len(accepted)} accepted results across {len(by_card)} mapped models")
    if only:
        print(f"restricting writes to {len(only)} model_id(s)")
    for name, count in sorted(unmapped.items()):
        print(f"  UNMAPPED  {name}: {count} results skipped — no card, or no verified mapping")

    cards = _card_index()
    written = 0
    for model_id, records in sorted(by_card.items()):
        if only is not None and model_id not in only:
            continue
        path = cards.get(model_id)
        if path is None:
            print(f"  ERROR     {model_id}: mapped but no card file found")
            continue
        text = path.read_text(encoding="utf-8")
        front_raw, body = text.split("---", 2)[1], text.split("---", 2)[2]
        front = yaml.safe_load(front_raw)
        block = front.setdefault("benchmarks", {}) or {}
        existing = {(e.get("benchmark_id"), e.get("model_id_as_evaluated"))
                    for e in (block.get("evidence") or [])}
        fresh = [r.model_dump() for r in records
                 if (r.benchmark_id, r.model_id_as_evaluated) not in existing]
        if not fresh:
            print(f"  UNCHANGED {model_id}: already carries this evidence")
            continue
        block["evidence"] = (block.get("evidence") or []) + fresh
        front["benchmarks"] = block

        print(f"  {'WOULD ADD' if args.dry_run else 'ADDED    '} {model_id}: "
              f"{len(fresh)} records ({', '.join(sorted(r.benchmark_id for r in records))})")
        if args.dry_run:
            continue
        path.write_text(
            "---\n" + yaml.safe_dump(front, sort_keys=False, allow_unicode=True) + "---" + body,
            encoding="utf-8")
        ModelCard.from_yaml_file(path)  # round-trip: refuse to leave a broken card
        written += 1

    print(f"\n{written} cards updated" if not args.dry_run else "\n(dry run)")
    return 0


def _card_index() -> dict[str, Path]:
    index: dict[str, Path] = {}
    for path in (PROJECT_ROOT / "models").rglob("*.md"):
        if path.name == "LICENSE.md":
            continue
        model_id = _model_id_of(path)
        if model_id and model_id not in index:
            index[model_id] = path
    return index


def _model_id_of(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return None
    try:
        return (yaml.safe_load(text.split("---", 2)[1]) or {}).get("model_id")
    except yaml.YAMLError:
        return None


if __name__ == "__main__":
    raise SystemExit(main())
