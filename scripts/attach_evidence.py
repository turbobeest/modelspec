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
    # "GLM-5.3 (max)": no card exists. GLM cards reach 5.2. Do not map this to
    # glm-5-2 — a score for 5.3 attached to 5.2 would be a fabricated claim.
    # "Qwen3.8-Max": the Qwen3.8 HF table is dated only as "Updated 27 days ago".
    # "Claude Fable 5.1": the system card does not report SWE-bench Verified or
    # GPQA Diamond, and Terminal-Bench 4.0 is not the ranked terminal_bench key.
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
    args = parser.parse_args()

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
    for name, count in sorted(unmapped.items()):
        print(f"  UNMAPPED  {name}: {count} results skipped — no card, or no verified mapping")

    cards = _card_index()
    written = 0
    for model_id, records in sorted(by_card.items()):
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
