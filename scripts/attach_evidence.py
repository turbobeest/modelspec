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
    # Live LM Arena names. Explicit unique matches only.
    # Effort rows (high/low/medium/xhigh/thinking) stay unmapped.
    # "(max)" is the board's canonical product row, same judgement as Astra.
    "claude-3-5-sonnet-20241022": "anthropic/claude-3-5-sonnet-20241022",
    "claude-3-7-sonnet-20250219": "anthropic/claude-3-7-sonnet-20250219",
    "claude-fable-5": "anthropic/claude-fable-5",
    "claude-fable-5.1-max": "anthropic/claude-fable-5-1",
    "claude-haiku-4-5-20251001": "anthropic/claude-haiku-4-5-20251001",
    "claude-opus-4-1-20250805": "anthropic/claude-opus-4-1-20250805",
    "claude-opus-4-20250514": "anthropic/claude-opus-4-20250514",
    "claude-opus-4-5-20251101": "anthropic/claude-opus-4-5-20251101",
    "claude-opus-4-6": "anthropic/claude-opus-4-6",
    "claude-opus-4-7": "anthropic/claude-opus-4-7",
    "claude-opus-4-8": "anthropic/claude-opus-4-8",
    "claude-opus-5-max": "anthropic/claude-opus-5",
    "claude-sonnet-4-20250514": "anthropic/claude-sonnet-4-20250514",
    "claude-sonnet-4-5-20250929": "anthropic/claude-sonnet-4-5-20250929",
    "claude-sonnet-4-6": "anthropic/claude-sonnet-4-6",
    "gpt-oss-120b": "cerebras/gpt-oss-120b",
    "qwen3.8-27b": "cerebras/qwen-3-8-27b",
    "command-a-03-2025": "cohere/command-a-03-2025",
    "deepseek-r1": "deepseek/deepseek-r1",
    "deepseek-r1-0528": "deepseek/deepseek-r1-0528",
    "deepseek-v3": "deepseek/deepseek-v3",
    "deepseek-v3-0324": "deepseek/deepseek-v3-0324",
    "deepseek-v3.1": "deepseek/deepseek-v3-1",
    "deepseek-v3.2": "deepseek/deepseek-v3-2",
    "deepseek-v3.2-exp": "deepseek/deepseek-v3-2-exp",
    "deepseek-v4-flash": "deepseek/deepseek-v4-flash",
    "deepseek-v4-pro": "deepseek/deepseek-v4-pro",
    "gemini-2.5-flash": "google/gemini-2-5-flash",
    "gemini-2.5-pro": "google/gemini-2-5-pro",
    "gemini-3.5-flash-lite": "google/gemini-3-5-flash-lite",
    "gemma-3-27b-it": "google/gemma-3-27b-it",
    "gemma-4-31b": "google/gemma-4-31b",
    "muse-spark": "meta/muse-spark",
    "minimax-m2.5": "minimax/minimax-m2-5",
    "minimax-m2.7": "minimax/minimax-m2-7",
    "minimax-m3": "minimax/minimax-m3",
    "mistral-large-3": "mistral/mistral-large-2512",
    "mistral-small-2506": "mistral/mistral-small-2506",
    "kimi-k2.6": "moonshot/kimi-k2-6",
    "kimi-k3-max": "moonshot/kimi-k3",
    "gpt-5.4": "openai/gpt-5-4",
    "gpt-5.5": "openai/gpt-5-5",
    "o1-preview": "openai/o1-preview",
    "qwen3-235b-a22b": "qwen/qwen3-235b-a22b",
    "qwen3-30b-a3b-instruct-2507": "qwen/qwen3-30b-a3b-instruct-2507",
    "qwen3.5-122b-a10b": "qwen/qwen3-5-122b-a10b",
    "qwen3.5-27b": "qwen/qwen3-5-27b",
    "qwen3.5-35b-a3b": "qwen/qwen3-5-35b-a3b",
    "qwen3.5-397b-a17b": "qwen/qwen3-5-397b-a17b",
    "qwen3.6-plus": "qwen/qwen3-6-plus",
    "qwen3.7-plus": "qwen/qwen3-7-plus",
    "qwen3-coder-480b-a35b-instruct": "qwen/qwen3-coder-480b-a35b-instruct",
    "qwen3-next-80b-a3b-instruct": "qwen/qwen3-next-80b-a3b-instruct",
    "step-3.5-flash": "stepfun/step-3-5-flash",
    "solar-pro4": "upstage/solar-pro4",
    "grok-4.3": "xai/grok-4-3",
    "grok-4.5": "xai/grok-4-5",
    "glm-4.5": "zhipu/glm-4-5",
    "glm-4.5-air": "zhipu/glm-4-5-air",
    "glm-4.5v": "zhipu/glm-4-5v",
    "glm-4.6": "zhipu/glm-4-6",
    "glm-4.6v": "zhipu/glm-4-6v",
    "glm-4.7": "zhipu/glm-4-7",
    "glm-4.7-flash": "zhipu/glm-4-7-flash",
    "glm-5": "zhipu/glm-5",
    "glm-5.1": "zhipu/glm-5-1",
    # Unique Z.ai product row. mistral/zai-glm-5-2 and qwen/glm-5-2
    # no longer exist in the catalogue. Non-reasoning stays unmapped.
    "glm-5.2-max": "zhipu/glm-5-2",
    "glm-5.3-max": "zhipu/glm-5-3",
    "glm-5.3-flash": "zhipu/glm-5-3-flash",
    # MODEL-13: cards that existed only after the live-board harvest.
    # Unique identity checked against the Arena org, not
    # inferred from a family name. Effort / quant / sibling-size rows stay out.
    "inkling": "thinkingmachines/inkling",
    "muse-glimmer": "meta/muse-glimmer-30b",
    # Naming-drift aliases. Re-verified 2026-09-10 against the live
    # catalogue (1337 cards). Unique spelling matches only; a wrong
    # alias is worse than a refusal. Already-present MODEL-13 keys are
    # not repeated.
    "gemini-2.0-flash-001": "google/gemini-2-0-flash",
    "gemma-4-26b-a4b": "google/gemma-4-26b-a4b-it",
    "gpt-4.1-2025-04-14": "openai/gpt-4-1",
    "gpt-4.1-mini-2025-04-14": "openai/gpt-4-1-mini",
    "grok-4-0709": "xai/grok-4",
    "grok-4.20-multi-agent-beta-0309": "xai/grok-4-20-multi-agent-0309",
    "o1-2024-12-17": "openai/o1",
    "o3-2025-04-16": "openai/o3",
    "o4-mini-2025-04-16": "openai/o4-mini",
    "qwen3-235b-a22b-instruct-2507": "cerebras/qwen-3-235b-a22b-instruct-2507",
    "qwen3-vl-235b-a22b-instruct": "qwen/qwen3-vl-235b-a22b",
    "qwen3.8-max": "qwen/qwen3-8-max",
    # Newly-carded leaderboard names. Unique exact display/slug matches
    # plus four dated/size spellings that are not exact. Gemma 4 12B and
    # Qwen2 72B stay unmapped (base+IT / unqualified Instruct).
    "deepseek-v3.1-terminus": "deepseek/deepseek-v3-1-terminus",
    "hy3": "tencent/hy3",
    "Inkling Small": "thinkingmachines/inkling-small",
    "intellect-3": "primeintellect/intellect-3",
    "longcat-flash-chat": "meituan/longcat-flash-chat",
    "mimo-v2.5": "xiaomi/mimo-v2-5",
    "mimo-v2.5-pro": "xiaomi/mimo-v2-5-pro",
    # Unmapped on purpose:
    # "Claude Opus 5 (high)" / other effort rows — not the product card.
    # "GLM-5.2 (Non-reasoning)" — serving variant, not the (max) product row.
    # "Qwen3.8-Max" as a *static* HF score still has no stated day.
    # "Inkling Small" maps to thinkingmachines/inkling-small, never Inkling.
    # NVFP4 Lightning/Ultra Arena rows — serving quants, not the BF16 cards.
    # "Llama 4 Scout" — base and instruct both exist.
    # "Gemini 3 Flash" / gemini-3-flash — not gemini-3-flash-preview.
    # "Gemma 4 12B" / "Qwen2 72B" — unqualified names with Instruct siblings.
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
