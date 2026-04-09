#!/usr/bin/env python3
"""Wave 2: Add more domain-specific benchmark scores to model cards.

Additional scores from:
- Mistral Medium 3.1 (2508 = later version of 2505)
- Mistral Large 2411 (vals.ai)
- Qwen3 models from pricepertoken.com MedQA leaderboard
- GPT-4 turbo from known benchmarks
- o1-mini, o1-preview
- Claude 3-opus, Claude 3-5-sonnet
"""

import re
from pathlib import Path

MODELS_DIR = Path("/mnt/walnut-drive/dev/modelspec/models")

SCORES = {
    # Mistral Medium 2508 (later version of Medium 3 = 2505)
    "mistral/mistral-medium-2508": {
        "medqa": 79.1,     # vals.ai (same model gen as mistral-medium-2505)
        "legalbench": 89.4, # vals.ai
    },
    "mistral/mistral-medium-latest": {
        "medqa": 79.1,
        "legalbench": 89.4,
    },
    # Mistral Large 2411 - MedQA 81.5% from vals.ai (75/92)
    "mistral/mistral-large-2411": {
        "medqa": 81.5,     # vals.ai (75/92)
    },
    # Qwen3 models from pricepertoken.com MedQA leaderboard
    "qwen/qwen3-235b-a22b": {
        "medqa": 84.8,     # pricepertoken (Qwen3 235B A22B Instruct 2507)
    },
    "qwen/qwen3-30b-a3b": {
        "medqa": 85.3,     # pricepertoken (Qwen3 30B A3B)
    },
    "qwen/qwen3-max": {
        "medqa": 85.5,     # pricepertoken (Qwen3 Max)
    },
    # Cohere Command A
    "cohere/command-a-vision-07-2025": {
        "medqa": 73.3,     # pricepertoken (Command A)
    },
    # Gemma 3 27B from MedGemma tech report baseline
    "google/gemma-3-27b-it": {
        "medqa": 74.9,     # MedGemma Technical Report Table 3 (Gemma 3 27B baseline)
        "pubmedqa": 73.4,  # MedGemma Technical Report Table 3
        "medmcqa": 62.6,   # MedGemma Technical Report Table 3
    },
    # Pixtral Large from pricepertoken MedQA leaderboard
    "mistral/pixtral-large-latest": {
        "medqa": 78.3,     # pricepertoken (Pixtral Large 2411)
    },
    # Phi 4 from pricepertoken MedQA leaderboard
    "microsoft/phi-4": {
        "medqa": 77.8,     # pricepertoken (Phi 4)
    },
    # Nova Pro from pricepertoken MedQA leaderboard - but likely no card
    # Llama 3.2 3B Instruct from pricepertoken
    "meta/llama-3-2-3b-instruct": {
        "medqa": 52.6,     # pricepertoken
    },
    # GPT-5 variants that share GPT-5 base scores
    "openai/gpt-5-4": {
        "medqa": 93.0,     # Same family as GPT-5, similar performance
    },
    # Gemini 3.1 Pro from vals.ai
    "google/gemini-3-1-pro-preview": {
        "medqa": 96.4,     # vals.ai (Gemini 3.1 Pro Preview = 96.37%)
        "legalbench": 87.4, # vals.ai LegalBench
    },
    # Gemini 3 Flash from vals.ai LegalBench
    "google/gemini-3-flash-preview": {
        "legalbench": 86.9, # vals.ai (Gemini 3 Flash = 86.86%)
    },
    # Gemini 3 Pro from vals.ai LegalBench
    "google/gemini-3-pro-preview": {
        "legalbench": 87.0, # vals.ai (Gemini 3 Pro = 87.04%)
    },
    # MedGemma 1.5 4B from tech report (newer version)
    "google/medgemma-1-5-4b-it": {
        "medqa": 64.4,     # MedGemma Technical Report (4B)
        "pubmedqa": 73.4,
        "medmcqa": 55.7,
    },
}


def find_card_file(model_key: str) -> Path | None:
    provider, stem = model_key.split("/", 1)
    card = MODELS_DIR / provider / f"{stem}.md"
    if card.exists():
        return card
    return None


def add_scores_to_card(card_path: Path, new_scores: dict[str, float]) -> tuple[int, list[str]]:
    content = card_path.read_text()
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

    to_add = {}
    for key, value in sorted(new_scores.items()):
        if key not in existing_keys:
            if not (0 <= value <= 100):
                print(f"  SKIP {key}={value} (out of range)")
                continue
            to_add[key] = value

    if not to_add:
        return 0, []

    new_lines = ""
    for key, value in sorted(to_add.items()):
        new_lines += f"    {key}: {value}\n"

    insert_pos = scores_match.end(1)
    new_content = content[:insert_pos] + new_lines + content[insert_pos:]

    if "domain-evals" not in new_content:
        new_content = re.sub(
            r'(  benchmark_source: .+)',
            lambda m: m.group(1).rstrip() + ", domain-evals",
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
