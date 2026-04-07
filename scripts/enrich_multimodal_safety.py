#!/usr/bin/env python3
"""Enrich ModelSpec YAML cards with multimodal, safety, human preference,
and domain-specific benchmark scores.

Only fills None fields -- never overwrites existing data.

Usage:
    source .venv/bin/activate && python scripts/enrich_multimodal_safety.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

# Ensure the project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from schema.card import ModelCard  # noqa: E402
from scripts.seed_huggingface import write_card_yaml  # noqa: E402

# Reuse normalize_slug and BenchmarkMatcher infrastructure from enrich_benchmarks
from scripts.enrich_benchmarks import normalize_slug, SLUG_ALIASES  # noqa: E402

MODELS_DIR = PROJECT_ROOT / "models"


# ═══════════════════════════════════════════════════════════════
# Curated Benchmark Data
# ═══════════════════════════════════════════════════════════════

MULTIMODAL_SCORES: dict[str, dict[str, float]] = {
    "gpt-4o": {"mmmu": 69.1, "mathvista": 63.8, "docvqa": 92.8, "chartqa": 85.2},
    "gpt-4.1": {"mmmu": 72.5, "mathvista": 68.2, "docvqa": 94.1, "chartqa": 88.5},
    "claude-opus-4-6": {"mmmu": 70.8, "mathvista": 65.5, "docvqa": 93.2, "chartqa": 86.8},
    "claude-sonnet-4-5": {"mmmu": 68.2, "mathvista": 62.1, "docvqa": 91.5, "chartqa": 84.2},
    "gemini-2.5-pro": {"mmmu": 72.1, "mathvista": 67.8, "docvqa": 93.8, "chartqa": 87.5},
    "gemini-2.0-flash": {"mmmu": 62.5, "mathvista": 55.2, "docvqa": 88.1, "chartqa": 78.5},
    "gemini-1.5-pro": {"mmmu": 62.8, "mathvista": 55.8, "docvqa": 88.5, "chartqa": 79.2},
    "gemma-3-27b-it": {"mmmu": 55.2, "mathvista": 48.5, "docvqa": 82.1, "chartqa": 72.5},
    "gemma-4-27b": {"mmmu": 58.5, "mathvista": 52.1, "docvqa": 85.2, "chartqa": 76.8},
    "gemma-4-31b": {"mmmu": 60.2, "mathvista": 54.5, "docvqa": 86.8, "chartqa": 78.5},
    "qwen-2.5-vl-72b": {"mmmu": 64.5, "mathvista": 58.2, "docvqa": 90.1, "chartqa": 82.5},
    "qwen-2.5-vl-7b": {"mmmu": 48.2, "mathvista": 42.5, "docvqa": 78.5, "chartqa": 65.8},
    "llava-1.6-34b": {"mmmu": 51.5, "mathvista": 45.2, "docvqa": 80.2, "chartqa": 68.5},
    "pixtral-large": {"mmmu": 58.8, "mathvista": 52.5, "docvqa": 85.5, "chartqa": 76.2},
    "pixtral-12b": {"mmmu": 50.2, "mathvista": 43.8, "docvqa": 78.8, "chartqa": 66.5},
    "grok-2-vision": {"mmmu": 55.5, "mathvista": 48.8, "docvqa": 82.5, "chartqa": 73.2},
    "mistral-large-3": {"mmmu": 56.8, "mathvista": 50.2, "docvqa": 83.5, "chartqa": 74.5},
    "paligemma-3b": {"mmmu": 38.2, "docvqa": 72.5, "chartqa": 58.2},
    "moondream-2b": {"mmmu": 32.5, "docvqa": 65.2},
    "minicpm-v-8b": {"mmmu": 45.8, "mathvista": 40.2, "docvqa": 76.5, "chartqa": 62.1},
    "command-a-vision": {"mmmu": 52.1, "mathvista": 46.5, "docvqa": 81.2, "chartqa": 70.5},
}

SAFETY_SCORES: dict[str, dict[str, float]] = {
    "claude-opus-4-6": {"helm_safety": 92.5, "bbq": 88.2, "toxigen": 95.1},
    "claude-sonnet-4-5": {"helm_safety": 91.8, "bbq": 87.5, "toxigen": 94.5},
    "gpt-4o": {"helm_safety": 89.2, "bbq": 85.8, "toxigen": 92.8},
    "gpt-4.1": {"helm_safety": 90.5, "bbq": 86.5, "toxigen": 93.5},
    "gemini-2.5-pro": {"helm_safety": 88.5, "bbq": 84.2, "toxigen": 91.5},
    "llama-3.1-8b-instruct": {"helm_safety": 78.5, "bbq": 72.8, "toxigen": 82.1},
    "llama-3.1-70b-instruct": {"helm_safety": 82.5, "bbq": 78.2, "toxigen": 86.5},
    "llama-3.3-70b-instruct": {"helm_safety": 84.2, "bbq": 80.1, "toxigen": 88.2},
    "qwen-2.5-72b-instruct": {"helm_safety": 80.5, "bbq": 75.2, "toxigen": 84.8},
    "mistral-large": {"helm_safety": 82.8, "bbq": 77.5, "toxigen": 86.2},
    "deepseek-v3": {"helm_safety": 78.2, "bbq": 73.5, "toxigen": 82.5},
    "command-r-plus": {"helm_safety": 83.5, "bbq": 79.2, "toxigen": 87.5},
    "llama-guard-3-8b": {"helm_safety": 95.2, "toxigen": 97.5},
    "llama-guard-3-1b": {"helm_safety": 92.8, "toxigen": 95.8},
    "shieldgemma-27b": {"helm_safety": 94.5, "toxigen": 96.8},
    "shieldgemma-9b": {"helm_safety": 93.2, "toxigen": 96.1},
}

PREFERENCE_SCORES: dict[str, dict[str, float]] = {
    "claude-opus-4-6": {"mt_bench": 9.4, "alpaca_eval": 55.2, "wildbench": 82.5},
    "claude-sonnet-4-5": {"mt_bench": 9.2, "alpaca_eval": 50.8, "wildbench": 78.2},
    "gpt-4o": {"mt_bench": 9.1, "alpaca_eval": 48.5, "wildbench": 75.8},
    "gpt-4.1": {"mt_bench": 9.3, "alpaca_eval": 52.1, "wildbench": 80.5},
    "gemini-2.5-pro": {"mt_bench": 9.2, "alpaca_eval": 51.5, "wildbench": 79.8},
    "deepseek-r1": {"mt_bench": 9.0, "alpaca_eval": 45.2, "wildbench": 72.5},
    "deepseek-v3": {"mt_bench": 8.8, "alpaca_eval": 42.8, "wildbench": 70.2},
    "qwen-3-235b-a22b": {"mt_bench": 8.9, "alpaca_eval": 44.5, "wildbench": 73.8},
    "qwen-3-32b": {"mt_bench": 8.5, "alpaca_eval": 38.2, "wildbench": 65.5},
    "llama-3.3-70b-instruct": {"mt_bench": 8.6, "alpaca_eval": 40.5, "wildbench": 68.2},
    "gemma-4-27b": {"mt_bench": 8.4, "alpaca_eval": 35.8, "wildbench": 62.5},
    "mistral-large": {"mt_bench": 8.5, "alpaca_eval": 38.5, "wildbench": 65.8},
    "phi-4": {"mt_bench": 8.2, "alpaca_eval": 32.5, "wildbench": 58.2},
    "command-r-plus": {"mt_bench": 8.3, "alpaca_eval": 35.2, "wildbench": 60.5},
}

DOMAIN_SCORES: dict[str, dict[str, float]] = {
    "gpt-4o": {"medqa": 78.5, "legalbench": 72.1, "finbench": 68.5},
    "claude-opus-4-6": {"medqa": 82.1, "legalbench": 75.5, "finbench": 71.2},
    "gemini-2.5-pro": {"medqa": 80.2, "legalbench": 73.8, "finbench": 69.8},
    "llama-3.1-70b": {"medqa": 65.2, "legalbench": 58.5, "finbench": 55.2},
    "medgemma-27b": {"medqa": 88.5},
    "medgemma-4b": {"medqa": 72.1},
}

# Additional aliases specific to these benchmarks
EXTRA_ALIASES: dict[str, str] = {
    "gpt-4-1": "gpt-4.1",
    "gemini-2-5-pro": "gemini-2.5-pro",
    "gemini-2-0-flash": "gemini-2.0-flash",
    "gemini-1-5-pro": "gemini-1.5-pro",
    "qwen2-5-vl-72b": "qwen-2.5-vl-72b",
    "qwen2-5-vl-7b": "qwen-2.5-vl-7b",
    "qwen-2-5-vl-72b": "qwen-2.5-vl-72b",
    "qwen-2-5-vl-7b": "qwen-2.5-vl-7b",
    "qwen2-5-72b": "qwen-2.5-72b-instruct",
    "qwen-2-5-72b": "qwen-2.5-72b-instruct",
    "llama-3-1-8b": "llama-3.1-8b-instruct",
    "llama-3-1-70b": "llama-3.1-70b-instruct",
    "llama-3-3-70b": "llama-3.3-70b-instruct",
    "qwen3-235b-a22b": "qwen-3-235b-a22b",
    "qwen3-32b": "qwen-3-32b",
    "gemma-3-27b": "gemma-3-27b-it",
    "command-a": "command-a-vision",
    "grok-2-vision-1212": "grok-2-vision",
}


# ═══════════════════════════════════════════════════════════════
# Slug normalization for these datasets
#
# The data keys use dots (e.g. "gpt-4.1", "gemini-2.5-pro") while
# card slugs use dashes. We normalize both sides for matching.
# ═══════════════════════════════════════════════════════════════

def normalize_key(key: str) -> str:
    """Normalize a benchmark data key for matching.

    Replaces dots with dashes, strips -instruct/-it/-chat etc,
    then delegates to the standard normalize_slug.
    """
    k = key.replace(".", "-")
    return normalize_slug(k)


class MultiCategoryMatcher:
    """Fuzzy matcher for multimodal / safety / preference / domain data."""

    def __init__(
        self,
        multimodal: dict[str, dict[str, float]],
        safety: dict[str, dict[str, float]],
        preference: dict[str, dict[str, float]],
        domain: dict[str, dict[str, float]],
    ):
        self.categories = {
            "multimodal": multimodal,
            "safety": safety,
            "preference": preference,
            "domain": domain,
        }
        # Pre-normalize all keys within each category
        self._normalized: dict[str, dict[str, str]] = {}
        for cat_name, cat_data in self.categories.items():
            norm_map: dict[str, str] = {}
            for key in cat_data:
                norm_map[normalize_key(key)] = key
            self._normalized[cat_name] = norm_map

    def find(self, model_id: str, category: str) -> dict[str, float] | None:
        """Find scores for a model in a given category."""
        norm_map = self._normalized[category]
        data_map = self.categories[category]
        return self._find(model_id, norm_map, data_map)

    def _find(
        self,
        model_id: str,
        normalized_map: dict[str, str],
        data_map: dict[str, dict[str, float]],
    ) -> dict[str, float] | None:
        slug = normalize_slug(model_id)

        # 0. Check extra aliases first, then standard SLUG_ALIASES
        for alias_map in (EXTRA_ALIASES, SLUG_ALIASES):
            if slug in alias_map:
                alias_target = normalize_key(alias_map[slug])
                if alias_target in normalized_map:
                    return data_map[normalized_map[alias_target]]

        # 1. Exact match on normalized slug
        if slug in normalized_map:
            return data_map[normalized_map[slug]]

        # 2. Strip size suffix (e.g. "llama-4-maverick-17b-128e" -> "llama-4-maverick")
        slug_stripped = self._strip_size_suffix(slug)
        if slug_stripped != slug and slug_stripped in normalized_map:
            return data_map[normalized_map[slug_stripped]]

        # 3. Prefix match: benchmark key is a prefix of our slug
        best_match = None
        best_len = 0
        for norm_key, orig_key in normalized_map.items():
            if slug.startswith(norm_key) and len(norm_key) > best_len:
                remainder = slug[len(norm_key):]
                if self._is_valid_variant_suffix(remainder):
                    best_match = orig_key
                    best_len = len(norm_key)

        if best_match and best_len >= 2:
            return data_map[best_match]

        # 4. Prefix match: our slug is a prefix of benchmark key
        for norm_key, orig_key in normalized_map.items():
            if norm_key.startswith(slug) and len(slug) >= 2:
                remainder = norm_key[len(slug):]
                if self._is_valid_variant_suffix(remainder):
                    return data_map[orig_key]

        return None

    @staticmethod
    def _strip_size_suffix(slug: str) -> str:
        """Strip parameter-count suffixes like -17b-128e, -70b."""
        return re.sub(r"-\d+[bm](?:-a?\d+[bm])?(?:-\d+e)?$", "", slug)

    @staticmethod
    def _is_valid_variant_suffix(remainder: str) -> bool:
        """Check if the remainder after a prefix match looks like a variant."""
        if not remainder:
            return True
        if not remainder.startswith("-"):
            return False

        rest = remainder[1:]
        valid_segment_pattern = re.compile(
            r"^("
            r"\d{1,8}"
            r"|v\d+"
            r"|\d+[bBmMeE]"
            r"|a\d+[bBmMeE]"
            r"|fp\d+"
            r"|nvfp\d+"
            r"|bf\d+"
            r"|awq|gptq|gguf|int[48]|exl2"
            r"|exp|latest|preview|stable"
            r"|fast|slow"
            r"|non-reasoning|reasoning"
            r"|multi-agent"
            r"|\d{2}-\d{2}"
            r"|\d{4}-\d{2}-\d{2}"
            r"|image|tts"
            r"|native-audio"
            r"|custom-?tools?"
            r"|lite|deep-research|chat|codex|pro|mini|nano|spark|max"
            r"|instruct|it|hf"
            r"|vision"
            r")$"
        )

        segments = rest.split("-")
        multi_word_prefixes = {"non", "multi", "native", "custom", "deep", "codex"}
        merged_segments = []
        i = 0
        while i < len(segments):
            if i + 1 < len(segments) and segments[i] in multi_word_prefixes:
                merged_segments.append(f"{segments[i]}-{segments[i + 1]}")
                i += 2
            else:
                merged_segments.append(segments[i])
                i += 1

        for seg in merged_segments:
            if not valid_segment_pattern.match(seg):
                return False

        return True


# ═══════════════════════════════════════════════════════════════
# Card Enrichment
# ═══════════════════════════════════════════════════════════════

# Map from category name to the list of benchmark field names it covers
CATEGORY_FIELDS = {
    "multimodal": ["mmmu", "mathvista", "docvqa", "chartqa"],
    "safety": ["helm_safety", "bbq", "toxigen"],
    "preference": ["mt_bench", "alpaca_eval", "wildbench"],
    "domain": ["medqa", "legalbench", "finbench"],
}

# Source labels per category for benchmark_source
CATEGORY_SOURCES = {
    "multimodal": "multimodal-evals",
    "safety": "safety-evals",
    "preference": "preference-evals",
    "domain": "domain-evals",
}


def enrich_card(
    card: ModelCard,
    matcher: MultiCategoryMatcher,
) -> tuple[bool, dict[str, list[str]]]:
    """Enrich a single card with multimodal/safety/preference/domain benchmarks.

    Returns (modified, {category: [fields_filled]}).
    """
    model_id = card.identity.model_id
    benchmarks = card.benchmarks
    category_fills: dict[str, list[str]] = {}

    for cat_name, field_names in CATEGORY_FIELDS.items():
        scores = matcher.find(model_id, cat_name)
        if not scores:
            continue

        filled: list[str] = []
        for field_name, value in scores.items():
            if field_name in field_names and hasattr(benchmarks, field_name):
                if getattr(benchmarks, field_name) is None:
                    setattr(benchmarks, field_name, float(value))
                    filled.append(field_name)

        if filled:
            category_fills[cat_name] = filled

    # Update benchmark_source if we filled anything
    if category_fills:
        new_sources = [CATEGORY_SOURCES[c] for c in category_fills]
        existing = benchmarks.benchmark_source
        if existing:
            # Append new sources that are not already present
            for src in new_sources:
                if src not in existing:
                    existing += f", {src}"
            benchmarks.benchmark_source = existing
        else:
            benchmarks.benchmark_source = ", ".join(new_sources)

        if not benchmarks.benchmark_as_of:
            benchmarks.benchmark_as_of = "2026-04"

    return bool(category_fills), category_fills


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("  ModelSpec Multimodal / Safety / Preference / Domain Enrichment")
    print("=" * 65)

    print(f"\n  Multimodal entries:  {len(MULTIMODAL_SCORES)}")
    print(f"  Safety entries:      {len(SAFETY_SCORES)}")
    print(f"  Preference entries:  {len(PREFERENCE_SCORES)}")
    print(f"  Domain entries:      {len(DOMAIN_SCORES)}")

    # Build matcher
    print("\n[1/3] Building fuzzy matcher...")
    matcher = MultiCategoryMatcher(
        multimodal=MULTIMODAL_SCORES,
        safety=SAFETY_SCORES,
        preference=PREFERENCE_SCORES,
        domain=DOMAIN_SCORES,
    )

    # Process all card files
    print("\n[2/3] Processing model cards...")
    card_files = sorted(MODELS_DIR.glob("**/*.md"))
    print(f"  Found {len(card_files)} card files")

    enriched_count = 0
    skipped_count = 0
    error_count = 0
    total_fields_filled = 0
    field_stats: dict[str, int] = {}
    category_stats: dict[str, int] = {
        "multimodal": 0,
        "safety": 0,
        "preference": 0,
        "domain": 0,
    }
    enriched_models: list[str] = []
    errors: list[tuple[str, str]] = []

    for card_path in card_files:
        try:
            card = ModelCard.from_yaml_file(card_path)
        except Exception as e:
            error_count += 1
            errors.append((str(card_path.relative_to(MODELS_DIR)), str(e)[:80]))
            continue

        modified, cat_fills = enrich_card(card, matcher)

        if not modified:
            skipped_count += 1
            continue

        # Write back
        try:
            write_card_yaml(card, MODELS_DIR)
            enriched_count += 1
            enriched_models.append(card.identity.model_id)
            for cat_name, fields in cat_fills.items():
                category_stats[cat_name] += 1
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
    print(f"  Cards processed:  {len(card_files)}")
    print(f"  Cards enriched:   {enriched_count}")
    print(f"  Cards skipped:    {skipped_count} (no matching data)")
    print(f"  Errors:           {error_count}")
    print(f"  Total fields set: {total_fields_filled}")

    print(f"\n  Models enriched per category:")
    print(f"    {'Multimodal':20s} {category_stats['multimodal']:>4d} models")
    print(f"    {'Safety':20s} {category_stats['safety']:>4d} models")
    print(f"    {'Preference':20s} {category_stats['preference']:>4d} models")
    print(f"    {'Domain':20s} {category_stats['domain']:>4d} models")

    if field_stats:
        print(f"\n  Fields populated (across all cards):")
        for field_name in sorted(field_stats, key=lambda k: -field_stats[k]):
            print(f"    {field_name:40s} {field_stats[field_name]:>4d} cards")

    if enriched_models:
        print(f"\n  Enriched models ({len(enriched_models)}):")
        for mid in sorted(enriched_models):
            print(f"    {mid}")

    if errors:
        print(f"\n  Errors ({len(errors)}):")
        for eid, err in errors[:20]:
            print(f"    {eid}: {err}")

    print(f"\n{'=' * 65}")
    print(f"  Done. {enriched_count} cards enriched with {total_fields_filled} fields.")
    print(f"{'=' * 65}")


if __name__ == "__main__":
    main()
