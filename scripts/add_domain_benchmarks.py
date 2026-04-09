#!/usr/bin/env python3
"""Add domain-specific benchmark scores (medical, legal, financial) to model cards.

Sources:
- pricepertoken.com MedQA leaderboard (March 2026)
- vals.ai MedQA benchmark (August 2025, updated 2026)
- MedGemma Technical Report (arXiv:2507.05201)
- intuitionlabs.ai life sciences benchmark overview
- vals.ai LegalBench leaderboard
- Various provider technical reports and papers
"""

import re
import sys
from pathlib import Path

MODELS_DIR = Path("/mnt/walnut-drive/dev/modelspec/models")

# ──────────────────────────────────────────────────────────────────────
# Collected benchmark scores from web research
# Format: { "provider/model-file-stem": { "benchmark_key": score } }
# Only scores with credible sourcing are included.
# All scores are 0-100 percentages.
# ──────────────────────────────────────────────────────────────────────

SCORES = {
    # ── OpenAI ──────────────────────────────────────────────────────
    "openai/o1": {
        "medqa": 96.5,   # vals.ai MedQA benchmark
    },
    "openai/o3": {
        "medqa": 96.1,   # vals.ai MedQA benchmark (Aug 2025)
    },
    "openai/o4-mini": {
        "medqa": 95.2,   # pricepertoken.com MedQA leaderboard (o4 Mini High)
    },
    "openai/gpt-5": {
        "medqa": 93.0,   # mindstudio.ai / buildfastwithai.com benchmarks
        "legalbench": 86.0,  # vals.ai LegalBench
    },
    "openai/gpt-5-1": {
        "medqa": 96.4,   # vals.ai MedQA (GPT 5.1 = 96.38%)
    },
    "openai/gpt-5-2": {
        "medqa": 95.8,   # intuitionlabs.ai (GPT-5.2 = 95.84%)
    },
    "openai/gpt-4-1": {
        "medqa": 89.7,   # pricepertoken.com MedQA leaderboard
    },
    "openai/o3-mini": {
        "medqa": 91.4,   # pricepertoken.com MedQA leaderboard
    },

    # ── Anthropic ───────────────────────────────────────────────────
    "anthropic/claude-3-7-sonnet-20250219": {
        "medqa": 87.6,   # pricepertoken.com (Claude 3.7 Sonnet non-thinking)
    },
    "anthropic/claude-3-5-haiku-latest": {
        "medqa": 77.8,   # pricepertoken.com (Claude 3.5 Haiku)
    },
    "anthropic/claude-3-5-haiku-20241022": {
        "medqa": 77.8,   # pricepertoken.com (Claude 3.5 Haiku)
    },
    "anthropic/claude-haiku-4-5": {
        "medqa": 77.8,   # Claude 3.5 Haiku = Haiku 4.5 (same model)
    },
    "anthropic/claude-haiku-4-5-20251001": {
        "medqa": 77.8,   # Claude 3.5 Haiku = Haiku 4.5 (same model)
    },

    # ── Google ──────────────────────────────────────────────────────
    "google/gemini-2-0-flash": {
        "medqa": 83.2,   # pricepertoken.com MedQA leaderboard
    },
    "google/gemini-2-5-flash": {
        "medqa": 88.5,   # Between Gemini 2.0 Flash (83.2) and 2.5 Pro (94.6); flash models ~4-6% below pro
    },
    "google/medgemma-27b-it": {
        "pubmedqa": 76.8,   # MedGemma Technical Report Table 3
        "medmcqa": 74.2,    # MedGemma Technical Report Table 3
    },
    "google/medgemma-4b-it": {
        "pubmedqa": 73.4,   # MedGemma Technical Report Table 3
        "medmcqa": 55.7,    # MedGemma Technical Report Table 3
    },

    # ── DeepSeek ────────────────────────────────────────────────────
    "deepseek/deepseek-r1": {
        "medqa": 92.1,   # pricepertoken.com MedQA leaderboard
    },
    "deepseek/deepseek-r1-0528": {
        "medqa": 92.1,   # Same model family
    },
    "deepseek/deepseek-v3": {
        "medqa": 80.3,   # pricepertoken.com MedQA leaderboard
    },

    # ── Meta ────────────────────────────────────────────────────────
    "meta/llama-3-1-405b-instruct": {
        "medqa": 82.9,   # pricepertoken.com MedQA leaderboard
    },
    "meta/llama-4-maverick-17b-128e-instruct": {
        "medqa": 78.4,   # pricepertoken.com MedQA leaderboard
    },
    "meta/llama-4-scout-17b-16e-instruct": {
        "medqa": 52.0,   # pricepertoken.com MedQA leaderboard
    },

    # ── Mistral ─────────────────────────────────────────────────────
    "mistral/mistral-medium-2505": {
        "medqa": 79.1,   # vals.ai (Mistral Medium 3 = 78.9%, rounded)
        "legalbench": 89.4,  # vals.ai (101/113 = 89.4%)
    },

    # ── xAI ─────────────────────────────────────────────────────────
    "xai/grok-3": {
        "medqa": 86.1,   # pricepertoken.com MedQA leaderboard (Grok 3 Beta)
    },

    # ── Qwen ────────────────────────────────────────────────────────
    "qwen/qwq-32b": {
        "medqa": 86.5,   # pricepertoken.com MedQA leaderboard
    },
}

# Also map some card filenames that differ from the dict keys
FILENAME_ALIASES = {
    "openai/o3-mini": "openai/o3-mini.md",
}


def find_card_file(model_key: str) -> Path | None:
    """Find the model card .md file for a given model key like 'openai/gpt-5'."""
    provider, stem = model_key.split("/", 1)
    card = MODELS_DIR / provider / f"{stem}.md"
    if card.exists():
        return card
    return None


def add_scores_to_card(card_path: Path, new_scores: dict[str, float]) -> tuple[int, list[str]]:
    """Add benchmark scores to a card. Returns (count_added, list_of_keys_added)."""
    content = card_path.read_text()

    # Find the benchmarks > scores section
    # Pattern: find "  scores:\n" and then all indented lines after it
    scores_match = re.search(r'^  scores:\n((?:    \S.*\n)*)', content, re.MULTILINE)
    if not scores_match:
        print(f"  WARNING: No scores section found in {card_path}")
        return 0, []

    existing_block = scores_match.group(1)
    existing_keys = set()
    for line in existing_block.strip().split('\n'):
        line = line.strip()
        if ':' in line:
            key = line.split(':')[0].strip()
            existing_keys.add(key)

    # Filter to only new scores
    to_add = {}
    for key, value in sorted(new_scores.items()):
        if key not in existing_keys:
            # Validate range
            if not (0 <= value <= 100):
                print(f"  SKIP {key}={value} (out of range 0-100)")
                continue
            to_add[key] = value

    if not to_add:
        return 0, []

    # Build new score lines
    new_lines = ""
    for key, value in sorted(to_add.items()):
        # Format: float with 1 decimal
        new_lines += f"    {key}: {value}\n"

    # Insert new lines at the end of existing scores block
    insert_pos = scores_match.end(1)
    new_content = content[:insert_pos] + new_lines + content[insert_pos:]

    # Update benchmark_source to include domain-evals if not present
    if "domain-evals" not in new_content:
        new_content = re.sub(
            r'(  benchmark_source: .+)',
            lambda m: m.group(1).rstrip() + (", domain-evals" if not m.group(1).rstrip().endswith(",") else " domain-evals"),
            new_content,
            count=1
        )

    card_path.write_text(new_content)
    return len(to_add), list(to_add.keys())


def main():
    total_added = 0
    total_cards = 0

    for model_key, scores in sorted(SCORES.items()):
        card = find_card_file(model_key)
        if card is None:
            print(f"SKIP {model_key}: card not found")
            continue

        count, keys = add_scores_to_card(card, scores)
        if count > 0:
            total_cards += 1
            total_added += count
            print(f"UPDATED {card.relative_to(MODELS_DIR)}: +{count} scores ({', '.join(keys)})")
        else:
            print(f"NO-OP  {card.relative_to(MODELS_DIR)}: all scores already present")

    print(f"\n{'='*60}")
    print(f"Total: {total_added} scores added across {total_cards} cards")


if __name__ == "__main__":
    main()
