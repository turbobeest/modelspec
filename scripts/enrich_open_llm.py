#!/usr/bin/env python3
"""Enrich ModelSpec YAML cards with Open LLM Leaderboard v2 benchmark scores.

Populates the 6 Open LLM Leaderboard v2 benchmarks (mmlu_pro, gpqa_pooled,
bbh, ifeval, math_lvl5, musr) from the leaderboard's own data.

Only fills None fields -- never overwrites existing data.

Usage:
    source .venv/bin/activate && python scripts/enrich_open_llm.py
"""

from __future__ import annotations

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
from scripts.enrich_benchmarks import normalize_slug, SLUG_ALIASES  # noqa: E402

MODELS_DIR = PROJECT_ROOT / "models"

# The 6 benchmarks tracked by Open LLM Leaderboard v2. Its "MATH Lvl 5" is not
# MATH-500 and its "GPQA" is not GPQA Diamond (MODEL-116).
OPEN_LLM_V2_BENCHMARKS = ["mmlu_pro", "gpqa_pooled", "bbh", "ifeval", "math_lvl5", "musr"]


# ═══════════════════════════════════════════════════════════════
# API Data Fetching (best-effort)
# ═══════════════════════════════════════════════════════════════

def try_fetch_open_llm_api() -> dict[str, dict[str, float]]:
    """Attempt to fetch Open LLM Leaderboard v2 data from HuggingFace APIs.

    Tries multiple API endpoints. Returns empty dict on failure.
    """
    try:
        import httpx
    except ImportError:
        print("  httpx not available, skipping API fetch")
        return {}

    # Strategy 1: Try the datasets API (leaderboard data is often a dataset)
    dataset_urls = [
        "https://huggingface.co/api/datasets/open-llm-leaderboard/results",
        "https://huggingface.co/api/datasets/open-llm-leaderboard/contents",
        "https://datasets-server.huggingface.co/rows?dataset=open-llm-leaderboard/results&config=default&split=train&offset=0&length=100",
    ]

    for url in dataset_urls:
        try:
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    parsed = _parse_dataset_response(data)
                    if parsed:
                        print(f"  [API] Fetched {len(parsed)} models from {url}")
                        return parsed
        except Exception as e:
            print(f"  [API] {url}: {e}")
            continue

    # Strategy 2: Try the Gradio Space API
    gradio_urls = [
        "https://open-llm-leaderboard-open-llm-leaderboard.hf.space/api/predict",
        "https://open-llm-leaderboard-open-llm-leaderboard.hf.space/api/queue/join",
    ]

    for url in gradio_urls:
        try:
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                resp = client.post(url, json={"data": [], "fn_index": 0})
                if resp.status_code == 200:
                    data = resp.json()
                    parsed = _parse_gradio_response(data)
                    if parsed:
                        print(f"  [API] Fetched {len(parsed)} models from Gradio API")
                        return parsed
        except Exception as e:
            print(f"  [API] Gradio: {e}")
            continue

    # Strategy 3: Try the Spaces API for metadata
    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            resp = client.get(
                "https://huggingface.co/api/spaces/open-llm-leaderboard/open_llm_leaderboard"
            )
            if resp.status_code == 200:
                print("  [API] Space metadata accessible but no parseable leaderboard data")
    except Exception:
        pass

    return {}


def _parse_dataset_response(data: Any) -> dict[str, dict[str, float]]:
    """Parse HuggingFace datasets API response."""
    result = {}

    # Handle rows format from datasets-server
    rows = None
    if isinstance(data, dict):
        rows = data.get("rows", data.get("data", None))
    elif isinstance(data, list):
        rows = data

    if not rows or not isinstance(rows, list):
        return result

    for entry in rows:
        row = entry.get("row", entry) if isinstance(entry, dict) else entry
        if not isinstance(row, dict):
            continue

        # Try various name fields
        name = (
            row.get("model", "")
            or row.get("model_name", "")
            or row.get("Model", "")
            or row.get("fullname", "")
        )
        if not name:
            continue

        slug = slugify(name)
        scores: dict[str, float] = {}

        # Map potential field names to our schema
        field_mappings = {
            "mmlu_pro": ["mmlu_pro", "MMLU-PRO", "mmlu-pro", "IFEval_mmlu_pro"],
            "gpqa_pooled": ["gpqa_pooled", "GPQA", "gpqa"],
            "bbh": ["bbh", "BBH", "Big Bench Hard"],
            "ifeval": ["ifeval", "IFEval", "IF Eval"],
            "math_lvl5": ["math_lvl5", "MATH Lvl 5", "math_hard"],
            "musr": ["musr", "MUSR", "MuSR"],
        }

        for our_field, possible_names in field_mappings.items():
            for api_name in possible_names:
                val = row.get(api_name)
                if val is not None and isinstance(val, (int, float)):
                    scores[our_field] = float(val)
                    break

        if scores:
            result[slug] = scores

    return result


def _parse_gradio_response(data: Any) -> dict[str, dict[str, float]]:
    """Parse Gradio Space API response."""
    result = {}

    if not isinstance(data, dict):
        return result

    # Gradio responses usually have a "data" key with nested arrays
    data_list = data.get("data", [])
    if not isinstance(data_list, list):
        return result

    for item in data_list:
        if isinstance(item, list) and len(item) >= 7:
            # Typical leaderboard table: [model_name, avg, mmlu_pro, gpqa, bbh, ifeval, math, musr]
            name = item[0] if isinstance(item[0], str) else str(item[0])
            slug = slugify(name)
            scores: dict[str, float] = {}
            benchmark_order = ["mmlu_pro", "gpqa_pooled", "bbh", "ifeval", "math_lvl5", "musr"]
            for idx, bench in enumerate(benchmark_order):
                val_idx = idx + 2  # skip name and average
                if val_idx < len(item) and isinstance(item[val_idx], (int, float)):
                    scores[bench] = float(item[val_idx])
            if scores:
                result[slug] = scores

    return result


# Additional slug aliases specific to this script
# Maps file-system slugs to leaderboard keys
OPEN_LLM_ALIASES: dict[str, str] = {
    # Qwen 2.5 file slugs use "2-5" not "2.5"
    "qwen2-5-72b": "qwen-2.5-72b-instruct",
    "qwen2-5-32b": "qwen-2.5-32b-instruct",
    "qwen2-5-14b": "qwen-2.5-14b-instruct",
    "qwen2-5-7b": "qwen-2.5-7b-instruct",
    # Qwen 3 file slugs use "qwen3" not "qwen-3"
    "qwen3-32b": "qwen-3-32b",
    "qwen3-14b": "qwen-3-14b",
    "qwen3-8b": "qwen-3-8b",
    "qwen3-30b-a3b": "qwen-3-30b-a3b",
    # Llama file slugs: "llama-3-1" not "llama-3.1"
    "llama-3-1-8b": "llama-3.1-8b-instruct",
    "llama-3-1-70b": "llama-3.1-70b-instruct",
    "llama-3-3-70b": "llama-3.3-70b-instruct",
    # Gemma file slugs: "gemma-2-27b-it" -> "gemma-2-27b-it"
    "gemma-2-27b": "gemma-2-27b-it",
    "gemma-2-9b": "gemma-2-9b-it",
    "gemma-3-27b": "gemma-3-27b-it",
    "gemma-3-12b": "gemma-3-12b-it",
    "gemma-4-27b": "gemma-4-27b",
    "gemma-4-31b": "gemma-4-31b",
    "gemma-4-26b": "gemma-4-27b",  # 26b variant maps to 27b data
    # Phi file slugs
    "phi-4": "phi-4",
    "phi-3-5-mini": "phi-3.5-mini-instruct",
    # Mistral file slugs
    "mistral-nemo": "mistral-nemo-instruct",
    "mistral-large": "mistral-large-instruct",
    "mixtral-8x22b": "mixtral-8x22b-instruct",
    "mixtral-8x7b": "mixtral-8x7b-instruct",
    "open-mixtral-8x22b": "mixtral-8x22b-instruct",
    "open-mixtral-8x7b": "mixtral-8x7b-instruct",
    # DeepSeek
    "deepseek-v3": "deepseek-v3",
    "deepseek-r1": "deepseek-r1",
    "deepseek-reasoner": "deepseek-r1",
    "deepseek-chat": "deepseek-v3",
    # Cohere file slugs
    "command-r-plus": "command-r-plus",
    "command-r": "command-r",
    # Falcon
    "falcon3-10b": "falcon-3-10b-instruct",
    # Yi
    "yi-1-5-34b": "yi-1.5-34b-chat",
    # Granite
    "granite-3-1-8b": "granite-3.1-8b-instruct",
}


# ═══════════════════════════════════════════════════════════════
# Matching Logic
# ═══════════════════════════════════════════════════════════════

def _normalize_for_open_llm(slug: str) -> str:
    """Normalize a model slug for matching against Open LLM data keys.

    Similar to normalize_slug from enrich_benchmarks but preserves dots
    that are part of version numbers in the leaderboard keys.
    """
    s = slug.lower().strip()

    # Remove provider prefix
    if "/" in s:
        s = s.split("/", 1)[1]

    # Remove trailing date stamps
    s = re.sub(r"-\d{8}$", "", s)
    s = re.sub(r"-\d{4}-\d{2}-\d{2}$", "", s)
    s = re.sub(r"-(?:25|26)\d{2}$", "", s)

    # Remove common suffixes iteratively
    suffixes = [
        "-instruct", "-it", "-chat", "-hf",
        "-latest", "-base", "-preview",
        "-fp8", "-awq", "-gptq-int4", "-bf16", "-nvfp4", "-gguf",
    ]
    for _ in range(3):
        stripped = False
        prev = s
        s = re.sub(r"-\d{8}$", "", s)
        s = re.sub(r"-(?:25|26)\d{2}$", "", s)
        if s != prev:
            stripped = True
        for suffix in suffixes:
            if s.endswith(suffix):
                s = s[: -len(suffix)]
                stripped = True
                break
        if not stripped:
            break

    return s


class OpenLLMMatcher:
    """Fuzzy matcher for Open LLM Leaderboard v2 scores."""

    def __init__(self, data: dict[str, dict[str, float]]):
        self.data = data

        # Build normalized lookup: normalized_key -> original_key
        self._normalized: dict[str, str] = {}
        for key in data:
            norm = _normalize_for_open_llm(key)
            self._normalized[norm] = key
            # Also add the key with dots replaced by dashes (file-system form)
            norm_dashed = norm.replace(".", "-")
            if norm_dashed != norm and norm_dashed not in self._normalized:
                self._normalized[norm_dashed] = key

    def find(self, model_id: str) -> dict[str, float] | None:
        """Find Open LLM Leaderboard v2 scores for a model."""
        slug = _normalize_for_open_llm(model_id)

        # 0. Check explicit aliases (both from enrich_benchmarks and our own)
        if slug in OPEN_LLM_ALIASES:
            target_key = OPEN_LLM_ALIASES[slug]
            if target_key in self.data:
                return self.data[target_key]

        # Also check the general SLUG_ALIASES
        if slug in SLUG_ALIASES:
            alias_norm = _normalize_for_open_llm(SLUG_ALIASES[slug])
            if alias_norm in self._normalized:
                return self.data[self._normalized[alias_norm]]

        # 1. Exact match on normalized slug
        if slug in self._normalized:
            return self.data[self._normalized[slug]]

        # 2. Try with dots replaced by dashes
        slug_dashed = slug.replace(".", "-")
        if slug_dashed in self._normalized:
            return self.data[self._normalized[slug_dashed]]

        # 3. Try stripping size suffixes (e.g., "-17b-128e")
        slug_stripped = re.sub(r"-\d+[bm](?:-a?\d+[bm])?(?:-\d+e)?$", "", slug)
        if slug_stripped != slug:
            if slug_stripped in OPEN_LLM_ALIASES:
                target = OPEN_LLM_ALIASES[slug_stripped]
                if target in self.data:
                    return self.data[target]
            if slug_stripped in self._normalized:
                return self.data[self._normalized[slug_stripped]]

        # 4. Prefix matching: our slug starts with a known key
        best_match = None
        best_len = 0
        for norm_key, orig_key in self._normalized.items():
            if slug.startswith(norm_key) and len(norm_key) > best_len:
                remainder = slug[len(norm_key):]
                if _is_valid_suffix(remainder):
                    best_match = orig_key
                    best_len = len(norm_key)
        if best_match and best_len >= 4:
            return self.data[best_match]

        # 5. Reverse prefix: a known key starts with our slug
        for norm_key, orig_key in self._normalized.items():
            if norm_key.startswith(slug) and len(slug) >= 4:
                remainder = norm_key[len(slug):]
                if _is_valid_suffix(remainder):
                    return self.data[orig_key]

        return None


def _is_valid_suffix(remainder: str) -> bool:
    """Check if remainder after prefix match is a valid variant suffix."""
    if not remainder:
        return True
    if not remainder.startswith("-"):
        return False
    rest = remainder[1:]
    valid_pattern = re.compile(
        r"^("
        r"\d{1,8}|v\d+|\d+[bBmMeE]|a\d+[bBmMeE]"
        r"|fp\d+|nvfp\d+|bf\d+|awq|gptq|gguf|int[48]"
        r"|exp|latest|preview|stable|fast|slow"
        r"|instruct|it|chat|hf|base"
        r"|\d{2}-\d{2}|\d{4}-\d{2}-\d{2}"
        r")$"
    )
    segments = rest.split("-")
    # Handle multi-word segments
    for seg in segments:
        if not valid_pattern.match(seg):
            return False
    return True


# ═══════════════════════════════════════════════════════════════
# Card Enrichment
# ═══════════════════════════════════════════════════════════════

def enrich_card(
    card: ModelCard,
    matcher: OpenLLMMatcher,
) -> tuple[bool, list[str]]:
    """Enrich a single card with Open LLM Leaderboard v2 scores.

    Only fills None fields -- never overwrites existing data.
    Returns (modified, fields_filled).
    """
    model_id = card.identity.model_id
    fields_filled: list[str] = []

    scores = matcher.find(model_id)
    if not scores:
        return False, []

    benchmarks = card.benchmarks

    for field_name in OPEN_LLM_V2_BENCHMARKS:
        if field_name in scores and field_name not in benchmarks.scores:
            benchmarks.scores[field_name] = float(scores[field_name])
            fields_filled.append(field_name)

    # Set metadata if we filled anything
    if fields_filled:
        # Append our source to existing benchmark_source if present
        existing_source = benchmarks.benchmark_source
        if existing_source:
            if "open-llm-leaderboard-v2" not in existing_source:
                benchmarks.benchmark_source = f"{existing_source}, open-llm-leaderboard-v2"
        else:
            benchmarks.benchmark_source = "open-llm-leaderboard-v2"
        if not benchmarks.benchmark_as_of:
            benchmarks.benchmark_as_of = "2026-04"

    return bool(fields_filled), fields_filled


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("  Open LLM Leaderboard v2 Benchmark Enrichment")
    print("=" * 65)

    # Step 1: Try live API data
    print("\n[1/4] Attempting Open LLM Leaderboard API fetch...")
    api_data = try_fetch_open_llm_api()

    # No curated fallback: the hand-typed table this script once carried did
    # not match the leaderboard it named (MODEL-116).
    merged = dict(api_data)
    if api_data:
        print(f"  API data: {len(api_data)} models fetched")
    else:
        print("  API data: unavailable, nothing to enrich")

    print(f"  Total leaderboard entries: {len(merged)}")

    # Step 2: Build matcher
    print("\n[2/4] Building fuzzy matcher...")
    matcher = OpenLLMMatcher(merged)

    # Step 3: Process all card files
    print("\n[3/4] Processing model cards...")
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

    # Step 4: Report
    print(f"\n{'=' * 65}")
    print("  RESULTS")
    print(f"{'=' * 65}")
    print(f"  Cards processed:     {len(card_files)}")
    print(f"  Cards enriched:      {enriched_count}")
    print(f"  Cards skipped:       {skipped_count} (no matching data or already filled)")
    print(f"  Errors:              {error_count}")
    print(f"  Total new fields:    {total_fields_filled}")

    if field_stats:
        print(f"\n  Benchmarks populated (across all cards):")
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
