#!/usr/bin/env python3
"""Enrich ModelSpec YAML cards with Open LLM Leaderboard v2 benchmark scores.

Uses REAL scraped data from the HuggingFace open-llm-leaderboard/contents dataset
(4,500+ models evaluated on the v2 benchmark suite).

Populates benchmarks.scores with:
  - ifeval (IFEval raw score, 0-100)
  - bbh (Big Bench Hard raw score, 0-100)
  - math_500 (MATH Lvl 5 raw score, 0-100)
  - gpqa_diamond (GPQA raw score, 0-100)
  - musr (MuSR raw score, 0-100)
  - mmlu_pro (MMLU-PRO raw score, 0-100)

Only fills keys that are not already present in benchmarks.scores.

Usage:
    source .venv/bin/activate && python scripts/enrich_v2_benchmarks.py
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

V2_BENCHMARKS = ["ifeval", "bbh", "math_500", "gpqa_diamond", "musr", "mmlu_pro"]


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


class V2Matcher:
    """Match model card model_ids to v2 leaderboard data keys."""

    def __init__(self, v2_data: dict[str, dict[str, float]]):
        self.data = v2_data
        self._norm_to_hf: dict[str, str] = {}
        for hf_name in v2_data:
            norm = _normalize(hf_name)
            self._norm_to_hf[norm] = hf_name

    def find(self, model_id: str) -> dict[str, float] | None:
        """Find v2 leaderboard scores for a model card."""
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

        # 5. Prefix matching
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

        return None


# ═══════════════════════════════════════════════════════════════
# Card Enrichment
# ═══════════════════════════════════════════════════════════════

def enrich_card(card: ModelCard, matcher: V2Matcher) -> tuple[bool, list[str]]:
    """Enrich a single card with v2 leaderboard scores."""
    model_id = card.identity.model_id
    scores = matcher.find(model_id)
    if not scores:
        return False, []

    fields_filled: list[str] = []
    benchmarks = card.benchmarks

    for bench in V2_BENCHMARKS:
        if bench in scores and bench not in benchmarks.scores:
            benchmarks.scores[bench] = scores[bench]
            fields_filled.append(bench)

    if fields_filled:
        existing_source = benchmarks.benchmark_source
        if existing_source:
            if "open-llm-leaderboard-v2" not in existing_source:
                benchmarks.benchmark_source = f"{existing_source}, open-llm-leaderboard-v2"
        else:
            benchmarks.benchmark_source = "open-llm-leaderboard-v2"
        if not benchmarks.benchmark_as_of:
            benchmarks.benchmark_as_of = "2025-03"

    return bool(fields_filled), fields_filled


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("  Open LLM Leaderboard v2 Benchmark Enrichment (scraped data)")
    print("  (IFEval, BBH, MATH Lvl 5, GPQA, MuSR, MMLU-PRO)")
    print("=" * 65)

    # Step 1: Load scraped v2 data
    v2_data_path = Path("/tmp/v2_extracted_scores.json")
    if not v2_data_path.exists():
        print("ERROR: /tmp/v2_extracted_scores.json not found.")
        print("Run the parquet extraction first.")
        sys.exit(1)

    with open(v2_data_path) as f:
        v2_data = json.load(f)

    print(f"\n[1/3] Loaded {len(v2_data)} models from v2 leaderboard data")

    # Step 2: Build matcher
    print(f"\n[2/3] Building fuzzy matcher...")
    matcher = V2Matcher(v2_data)

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
        print(f"\n  Benchmarks populated:")
        for field_name in sorted(field_stats, key=lambda k: -field_stats[k]):
            print(f"    {field_name:30s} {field_stats[field_name]:>4d} cards")

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
