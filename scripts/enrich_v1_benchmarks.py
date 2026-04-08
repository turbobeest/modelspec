#!/usr/bin/env python3
"""Enrich ModelSpec YAML cards with Open LLM Leaderboard v1 benchmark scores.

Populates benchmarks.scores with:
  - arc_challenge (ARC-Challenge acc_norm)
  - gsm8k (GSM8K acc)
  - hellaswag (HellaSwag acc_norm)
  - truthfulqa (TruthfulQA mc2)
  - winogrande (Winogrande acc)
  - 57 MMLU per-subject scores (mmlu_abstract_algebra, mmlu_anatomy, etc.)

Data source: HuggingFace open-llm-leaderboard-old/results repository.
All scores are real evaluation data from the EleutherAI lm-evaluation-harness.

Only fills keys that are not already present in benchmarks.scores.

Usage:
    source .venv/bin/activate && python scripts/enrich_v1_benchmarks.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

# Ensure the project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from schema.card import ModelCard  # noqa: E402
from scripts.seed_huggingface import write_card_yaml, slugify  # noqa: E402

MODELS_DIR = PROJECT_ROOT / "models"

# v1 leaderboard benchmark keys we'll write
V1_BENCHMARKS = ["arc_challenge", "gsm8k", "hellaswag", "truthfulqa", "winogrande"]

# All 57 MMLU subjects from the MMLU (hendrycksTest) evaluation
MMLU_SUBJECTS = [
    "mmlu_abstract_algebra", "mmlu_anatomy", "mmlu_astronomy",
    "mmlu_business_ethics", "mmlu_clinical_knowledge", "mmlu_college_biology",
    "mmlu_college_chemistry", "mmlu_college_computer_science",
    "mmlu_college_mathematics", "mmlu_college_medicine", "mmlu_college_physics",
    "mmlu_computer_security", "mmlu_conceptual_physics", "mmlu_econometrics",
    "mmlu_electrical_engineering", "mmlu_elementary_mathematics",
    "mmlu_formal_logic", "mmlu_global_facts", "mmlu_high_school_biology",
    "mmlu_high_school_chemistry", "mmlu_high_school_computer_science",
    "mmlu_high_school_european_history", "mmlu_high_school_geography",
    "mmlu_high_school_government_and_politics", "mmlu_high_school_macroeconomics",
    "mmlu_high_school_mathematics", "mmlu_high_school_microeconomics",
    "mmlu_high_school_physics", "mmlu_high_school_psychology",
    "mmlu_high_school_statistics", "mmlu_high_school_us_history",
    "mmlu_high_school_world_history", "mmlu_human_aging", "mmlu_human_sexuality",
    "mmlu_international_law", "mmlu_jurisprudence", "mmlu_logical_fallacies",
    "mmlu_machine_learning", "mmlu_management", "mmlu_marketing",
    "mmlu_medical_genetics", "mmlu_miscellaneous", "mmlu_moral_disputes",
    "mmlu_moral_scenarios", "mmlu_nutrition", "mmlu_philosophy",
    "mmlu_prehistory", "mmlu_professional_accounting", "mmlu_professional_law",
    "mmlu_professional_medicine", "mmlu_professional_psychology",
    "mmlu_public_relations", "mmlu_security_studies", "mmlu_sociology",
    "mmlu_us_foreign_policy", "mmlu_virology", "mmlu_world_religions",
]


# ═══════════════════════════════════════════════════════════════
# Normalize and Match
# ═══════════════════════════════════════════════════════════════

def _normalize(name: str) -> str:
    """Normalize model name for matching."""
    s = name.lower().strip()
    if "/" in s:
        s = s.split("/", 1)[1]
    s = s.replace(".", "-")
    s = re.sub(r"[_:\\]+", "-", s)
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s)
    s = s.strip("-")
    return s


def _strip_suffixes(slug: str) -> str:
    """Strip common suffixes for broader matching."""
    suffixes = [
        "-instruct", "-it", "-chat", "-hf", "-base",
        "-latest", "-preview", "-fp8", "-awq", "-nvfp4", "-gguf",
        "-gptq-int4", "-bf16",
    ]
    s = slug
    for _ in range(3):
        changed = False
        # Strip date stamps
        prev = s
        s = re.sub(r"-\d{8}$", "", s)
        s = re.sub(r"-\d{4}-\d{2}-\d{2}$", "", s)
        s = re.sub(r"-(?:25|26)\d{2}$", "", s)
        if s != prev:
            changed = True
        for suffix in suffixes:
            if s.endswith(suffix):
                s = s[: -len(suffix)]
                changed = True
                break
        if not changed:
            break
    return s


class V1Matcher:
    """Match model card model_ids to v1 leaderboard data keys."""

    def __init__(self, v1_data: dict[str, dict[str, float]]):
        self.data = v1_data

        # Build normalized lookup
        self._norm_to_hf: dict[str, str] = {}
        for hf_name in v1_data:
            norm = _normalize(hf_name)
            self._norm_to_hf[norm] = hf_name

    def find(self, model_id: str) -> dict[str, float] | None:
        """Find v1 leaderboard scores for a model card."""
        norm = _normalize(model_id)

        # 1. Exact match
        if norm in self._norm_to_hf:
            return self.data[self._norm_to_hf[norm]]

        # 2. Try adding common suffixes
        for suffix in ["-instruct", "-it", "-chat", "-hf"]:
            if (norm + suffix) in self._norm_to_hf:
                return self.data[self._norm_to_hf[norm + suffix]]

        # 3. Strip suffixes from card slug and match
        stripped = _strip_suffixes(norm)
        if stripped in self._norm_to_hf:
            return self.data[self._norm_to_hf[stripped]]

        # 4. Try stripped + common suffixes
        for suffix in ["-instruct", "-it", "-chat", "-hf"]:
            if (stripped + suffix) in self._norm_to_hf:
                return self.data[self._norm_to_hf[stripped + suffix]]

        # 5. Prefix matching: card slug starts with known v1 key
        best_match = None
        best_len = 0
        for norm_key, hf_name in self._norm_to_hf.items():
            if norm.startswith(norm_key) and len(norm_key) > best_len:
                remainder = norm[len(norm_key):]
                if not remainder or remainder.startswith("-"):
                    best_match = hf_name
                    best_len = len(norm_key)

        if best_match and best_len >= 6:
            return self.data[best_match]

        # 6. Reverse prefix: v1 key starts with our slug
        for norm_key, hf_name in self._norm_to_hf.items():
            if norm_key.startswith(norm) and len(norm) >= 6:
                remainder = norm_key[len(norm):]
                if not remainder or remainder.startswith("-"):
                    return self.data[hf_name]

        return None


# ═══════════════════════════════════════════════════════════════
# Card Enrichment
# ═══════════════════════════════════════════════════════════════

def enrich_card(card: ModelCard, matcher: V1Matcher) -> tuple[bool, list[str]]:
    """Enrich a single card with v1 leaderboard scores.

    Only fills keys not already present. Returns (modified, fields_filled).
    """
    model_id = card.identity.model_id
    scores = matcher.find(model_id)
    if not scores:
        return False, []

    fields_filled: list[str] = []
    benchmarks = card.benchmarks

    # Fill v1 benchmarks
    for bench in V1_BENCHMARKS:
        if bench in scores and bench not in benchmarks.scores:
            benchmarks.scores[bench] = scores[bench]
            fields_filled.append(bench)

    # Fill MMLU subjects
    for subject in MMLU_SUBJECTS:
        if subject in scores and subject not in benchmarks.scores:
            benchmarks.scores[subject] = scores[subject]
            fields_filled.append(subject)

    # Update metadata if we filled anything
    if fields_filled:
        existing_source = benchmarks.benchmark_source
        if existing_source:
            if "open-llm-leaderboard-v1" not in existing_source:
                benchmarks.benchmark_source = f"{existing_source}, open-llm-leaderboard-v1"
        else:
            benchmarks.benchmark_source = "open-llm-leaderboard-v1"
        if not benchmarks.benchmark_as_of:
            benchmarks.benchmark_as_of = "2024-07"

    return bool(fields_filled), fields_filled


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("  Open LLM Leaderboard v1 Benchmark Enrichment")
    print("  (ARC, GSM8K, HellaSwag, TruthfulQA, Winogrande, MMLU subjects)")
    print("=" * 65)

    # Step 1: Load scraped v1 data
    v1_data_path = Path("/tmp/v1_extracted_scores.json")
    if not v1_data_path.exists():
        print("ERROR: /tmp/v1_extracted_scores.json not found.")
        print("Run the scraper first to download v1 leaderboard data.")
        sys.exit(1)

    with open(v1_data_path) as f:
        v1_data = json.load(f)

    print(f"\n[1/3] Loaded {len(v1_data)} models from v1 leaderboard data")

    # Show benchmark coverage in source data
    bench_counts: dict[str, int] = {}
    for model_scores in v1_data.values():
        for key in model_scores:
            bench_counts[key] = bench_counts.get(key, 0) + 1

    v1_count = sum(1 for k in bench_counts if k in V1_BENCHMARKS)
    mmlu_count = sum(1 for k in bench_counts if k.startswith("mmlu_"))
    print(f"  v1 benchmark types: {v1_count}/{len(V1_BENCHMARKS)}")
    print(f"  MMLU subject types: {mmlu_count}/57")

    # Step 2: Build matcher
    print(f"\n[2/3] Building fuzzy matcher...")
    matcher = V1Matcher(v1_data)

    # Step 3: Process all card files
    print(f"\n[3/3] Processing model cards...")
    card_files = sorted(MODELS_DIR.glob("**/*.md"))
    print(f"  Found {len(card_files)} card files")

    enriched_count = 0
    skipped_count = 0
    error_count = 0
    total_fields_filled = 0
    field_stats: dict[str, int] = {}
    enriched_models: list[str] = []
    errors: list[tuple[str, str]] = []

    for card_path in card_files:
        try:
            card = ModelCard.from_yaml_file(card_path)
        except Exception as e:
            error_count += 1
            errors.append((str(card_path.relative_to(MODELS_DIR)), str(e)[:80]))
            continue

        modified, fields = enrich_card(card, matcher)

        if not modified:
            skipped_count += 1
            continue

        # Write back
        try:
            write_card_yaml(card, MODELS_DIR)
            enriched_count += 1
            enriched_models.append(card.identity.model_id)
            total_fields_filled += len(fields)
            for f in fields:
                field_stats[f] = field_stats.get(f, 0) + 1
        except Exception as e:
            error_count += 1
            errors.append((card.identity.model_id, f"Write error: {str(e)[:60]}"))

    # Report
    print(f"\n{'=' * 65}")
    print("  RESULTS")
    print(f"{'=' * 65}")
    print(f"  Cards processed:     {len(card_files)}")
    print(f"  Cards enriched:      {enriched_count}")
    print(f"  Cards skipped:       {skipped_count} (no matching data or already filled)")
    print(f"  Errors:              {error_count}")
    print(f"  Total new fields:    {total_fields_filled}")

    if field_stats:
        # Group by type
        v1_fields = {k: v for k, v in field_stats.items() if k in V1_BENCHMARKS}
        mmlu_fields = {k: v for k, v in field_stats.items() if k.startswith("mmlu_")}

        if v1_fields:
            print(f"\n  v1 Benchmarks populated:")
            for field_name in sorted(v1_fields, key=lambda k: -v1_fields[k]):
                print(f"    {field_name:30s} {v1_fields[field_name]:>4d} cards")

        if mmlu_fields:
            print(f"\n  MMLU subjects populated (top 20):")
            sorted_mmlu = sorted(mmlu_fields, key=lambda k: -mmlu_fields[k])
            for field_name in sorted_mmlu[:20]:
                print(f"    {field_name:50s} {mmlu_fields[field_name]:>4d} cards")
            if len(sorted_mmlu) > 20:
                remaining = len(sorted_mmlu) - 20
                total_mmlu = sum(mmlu_fields[k] for k in sorted_mmlu[20:])
                print(f"    ... and {remaining} more subjects ({total_mmlu} more field entries)")

    if enriched_models:
        print(f"\n  Enriched models ({len(enriched_models)}):")
        for mid in sorted(enriched_models):
            print(f"    {mid}")

    if errors:
        print(f"\n  Errors ({len(errors)}):")
        for eid, err in errors[:20]:
            print(f"    {eid}: {err}")

    print(f"\n{'=' * 65}")
    print(f"  Done. {enriched_count} cards enriched with {total_fields_filled} new benchmark fields.")
    print(f"{'=' * 65}")


if __name__ == "__main__":
    main()
