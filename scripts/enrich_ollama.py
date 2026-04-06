#!/usr/bin/env python3
"""Enrich ModelSpec cards with Ollama availability and OpenAI SDK compatibility tags.

Part 1: Match Ollama model registry entries to existing model cards.
Part 2: Add "openai-compatible" tag to models accessible via the OpenAI SDK.

Usage:
    source .venv/bin/activate && python scripts/enrich_ollama.py
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

from schema.card import ModelCard, PlatformEntry
from scripts.seed_huggingface import write_card_yaml, slugify, _convert_enums

MODELS_DIR = PROJECT_ROOT / "models"


# ═══════════════════════════════════════════════════════════════
# Part 1: Ollama Model Registry
# ═══════════════════════════════════════════════════════════════

# Curated list of known Ollama models (public data from ollama.com/library)
OLLAMA_MODELS: dict[str, list[str]] = {
    "llama3.3": ["70b"],
    "llama3.1": ["8b", "70b", "405b"],
    "llama3.2": ["1b", "3b"],
    "llama3": ["8b", "70b"],
    "gemma3": ["1b", "4b", "12b", "27b"],
    "gemma2": ["2b", "9b", "27b"],
    "gemma": ["2b", "7b"],
    "qwen3": ["0.6b", "1.7b", "4b", "8b", "14b", "30b-a3b", "32b", "235b-a22b"],
    "qwen2.5": ["0.5b", "1.5b", "3b", "7b", "14b", "32b", "72b"],
    "qwen2.5-coder": ["0.5b", "1.5b", "3b", "7b", "14b", "32b"],
    "qwq": ["32b"],
    "deepseek-r1": ["1.5b", "7b", "8b", "14b", "32b", "70b", "671b"],
    "deepseek-v3": ["671b"],
    "deepseek-coder-v2": ["16b", "236b"],
    "mistral": ["7b"],
    "mistral-nemo": ["12b"],
    "mistral-large": ["123b"],
    "mixtral": ["8x7b", "8x22b"],
    "codestral": ["22b"],
    "phi4": ["14b"],
    "phi3.5": ["3.8b"],
    "phi3": ["3.8b", "14b"],
    "command-r": ["35b"],
    "command-r-plus": ["104b"],
    "yi": ["6b", "9b", "34b"],
    "starcoder2": ["3b", "7b", "15b"],
    "codellama": ["7b", "13b", "34b", "70b"],
    "llama-guard3": ["1b", "8b"],
    "nomic-embed-text": [],
    "mxbai-embed-large": [],
    "all-minilm": [],
    "snowflake-arctic-embed": ["22m", "33m", "110m", "137m", "335m"],
    "granite3.1-dense": ["2b", "8b"],
    "granite3.1-moe": ["1b", "3b"],
    "granite-code": ["3b", "8b", "20b", "34b"],
    "falcon": ["7b", "40b", "180b"],
    "falcon3": ["1b", "3b", "7b", "10b"],
    "olmo2": ["7b", "13b"],
    "smollm2": ["135m", "360m", "1.7b"],
    "stablelm2": ["1.6b"],
    "nemotron-mini": ["4b"],
    "llava": ["7b", "13b", "34b"],
    "llava-llama3": ["8b"],
    "moondream": ["1.8b"],
    "bakllava": ["7b"],
    "cogvlm2": ["19b"],
    "minicpm-v": ["8b"],
    "stable-diffusion-3": [],
    "rwkv-6-world": [],
}


def try_fetch_ollama_models() -> dict[str, list[str]] | None:
    """Try to fetch models from Ollama API endpoints. Returns None if all fail."""
    import httpx

    # Attempt 1: Official API
    for url in [
        "https://ollama.com/api/models",
        "https://ollama.com/api/tags",
    ]:
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    models = data.get("models", data.get("tags", []))
                    if models:
                        result: dict[str, list[str]] = {}
                        for m in models:
                            name = m.get("name", "")
                            if ":" in name:
                                model_name, tag = name.rsplit(":", 1)
                                result.setdefault(model_name, []).append(tag)
                            else:
                                result.setdefault(name, [])
                        print(f"  Fetched {len(result)} models from {url}")
                        return result
        except Exception as e:
            print(f"  API {url} failed: {e}")

    # Attempt 2: Registry catalog
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get("https://registry.ollama.ai/v2/_catalog")
            if resp.status_code == 200:
                data = resp.json()
                repos = data.get("repositories", [])
                if repos:
                    result = {r: [] for r in repos}
                    print(f"  Fetched {len(result)} models from registry catalog")
                    return result
    except Exception as e:
        print(f"  Registry catalog failed: {e}")

    # Attempt 3: Scrape library page
    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            resp = client.get("https://ollama.com/library")
            if resp.status_code == 200:
                # Parse model names from the page
                # Ollama library page has model names in various link/card patterns
                names = set(re.findall(r'href="/library/([a-z0-9._-]+)"', resp.text))
                if names:
                    result = {n: [] for n in names}
                    print(f"  Scraped {len(result)} models from ollama.com/library")
                    return result
    except Exception as e:
        print(f"  Library scrape failed: {e}")

    return None


def get_ollama_models() -> dict[str, list[str]]:
    """Get the Ollama model list, trying API first then falling back to curated list."""
    print("Fetching Ollama model registry...")
    fetched = try_fetch_ollama_models()
    if fetched and len(fetched) > 10:
        return fetched
    print("  Using curated fallback list")
    return OLLAMA_MODELS


# ═══════════════════════════════════════════════════════════════
# Matching logic: Ollama names -> our model card filenames
# ═══════════════════════════════════════════════════════════════

def normalize_for_matching(name: str) -> str:
    """Normalize a model name for fuzzy matching: lowercase, dots->dashes, strip whitespace."""
    s = name.lower().strip()
    s = s.replace(".", "-")
    s = re.sub(r"[_/:\\]+", "-", s)
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def build_card_index() -> dict[str, tuple[str, Path]]:
    """Build an index of normalized-filename -> (model_id, path) for all model cards."""
    index: dict[str, tuple[str, Path]] = {}
    for md_file in MODELS_DIR.rglob("*.md"):
        stem = md_file.stem  # e.g. "llama-3-1-8b-instruct"
        norm = normalize_for_matching(stem)
        # Read just enough to get model_id
        try:
            content = md_file.read_text(encoding="utf-8")
            # Quick parse of model_id from YAML frontmatter
            match = re.search(r"^model_id:\s*(.+)$", content, re.MULTILINE)
            if match:
                model_id = match.group(1).strip().strip("'\"")
                index[norm] = (model_id, md_file)
        except Exception:
            pass
    return index


# Explicit mapping rules: (ollama_model, ollama_tag) -> list of card filename patterns to try
def generate_match_candidates(ollama_model: str, ollama_tag: str) -> list[str]:
    """Generate candidate normalized filenames to search for a given Ollama model:tag.

    Returns a list of patterns to try, in order of preference (most specific first).
    """
    candidates: list[str] = []

    # Normalize the ollama model name: dots -> dashes
    base = normalize_for_matching(ollama_model)
    tag_norm = normalize_for_matching(ollama_tag) if ollama_tag else ""

    # Special cases for known naming divergences
    special_mappings: dict[str, str] = {
        "llama3-3": "llama-3-3",
        "llama3-2": "llama-3-2",
        "llama3-1": "llama-3-1",
        "llama3": "meta-llama-3",
        "gemma3": "gemma-3",
        "gemma2": "gemma-2",
        "phi4": "phi-4",
        "phi3-5": "phi-3-5",
        "phi3": "phi-3",
        "qwen2-5": "qwen2-5",
        "qwen2-5-coder": "qwen2-5-coder",
        "qwen3": "qwen3",
        "qwq": "qwq",
        "deepseek-r1": "deepseek-r1",
        "deepseek-v3": "deepseek-v3",
        "deepseek-coder-v2": "deepseek-coder-v2",
        "mistral-nemo": "mistral-nemo",
        "mistral-large": "mistral-large",
        "mixtral": "mixtral",
        "codestral": "codestral",
        "command-r": "command-r",
        "command-r-plus": "command-r-plus",
        "llama-guard3": "llama-guard-3",
        "granite3-1-dense": "granite-3-1",
        "granite3-1-moe": "granite-3-1",
        "granite-code": "granite",
        "falcon3": "falcon3",
        "falcon": "falcon",
        "olmo2": "olmo-2",
        "stablelm2": "stablelm-2",
        "nemotron-mini": "nemotron",
        "cogvlm2": "cogvlm2",
        "minicpm-v": "minicpm-v",
        "nomic-embed-text": "nomic-embed-text",
        "mxbai-embed-large": "mxbai-embed-large",
        "all-minilm": "all-minilm",
        "snowflake-arctic-embed": "snowflake-arctic-embed",
        "rwkv-6-world": "rwkv-6-world",
        "smollm2": "smollm2",
        "starcoder2": "starcoder2",
        "llava": "llava",
        "llava-llama3": "llava-llama3",
        "moondream": "moondream",
        "bakllava": "bakllava",
        "yi": "yi",
        "codellama": "codellama",
        "stable-diffusion-3": "stable-diffusion-3",
    }

    mapped_base = special_mappings.get(base, base)

    if tag_norm:
        # For Ollama model:tag, try both "instruct" and base variants
        # e.g. llama3.1:8b -> llama-3-1-8b-instruct, llama-3-1-8b

        # Patterns with tag, instruct suffix
        candidates.append(f"{mapped_base}-{tag_norm}-instruct")
        candidates.append(f"{mapped_base}-{tag_norm}-it")
        candidates.append(f"{mapped_base}-{tag_norm}-chat")
        # Pattern with tag, no suffix
        candidates.append(f"{mapped_base}-{tag_norm}")
        # With "b" suffix variants (e.g. tag=8b -> 8b already has b)
        # Also try without the b (for filenames like qwen3-0-6b)
        if tag_norm.endswith("b"):
            without_b = tag_norm[:-1]
            if without_b:
                candidates.append(f"{mapped_base}-{without_b}b-instruct")
                candidates.append(f"{mapped_base}-{without_b}b")
    else:
        # No tag — embedding models or single-variant models
        candidates.append(f"{mapped_base}")
        candidates.append(f"{mapped_base}-v1-5")
        candidates.append(f"{mapped_base}-v1")
        candidates.append(f"{mapped_base}-l6-v2")
        candidates.append(f"{mapped_base}-l12-v2")

    # Deduplicate while preserving order
    seen = set()
    unique: list[str] = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique


def find_best_match(
    ollama_model: str,
    ollama_tag: str,
    card_index: dict[str, tuple[str, Path]],
) -> tuple[str, Path] | None:
    """Find the best matching model card for an Ollama model:tag.

    Returns (model_id, path) or None if no confident match found.
    """
    candidates = generate_match_candidates(ollama_model, ollama_tag)

    # Direct match against the index
    for candidate in candidates:
        if candidate in card_index:
            return card_index[candidate]

    # Partial/prefix match as fallback: look for index keys that contain the candidate
    # Only do this for more specific patterns (model + tag)
    tag_norm = normalize_for_matching(ollama_tag) if ollama_tag else ""
    if tag_norm:
        # Build a search pattern from the base + tag
        base = normalize_for_matching(ollama_model)
        special_mappings = {
            "llama3-3": "llama-3-3", "llama3-2": "llama-3-2", "llama3-1": "llama-3-1",
            "llama3": "meta-llama-3", "gemma3": "gemma-3", "gemma2": "gemma-2",
            "phi4": "phi-4", "phi3-5": "phi-3-5", "phi3": "phi-3",
            "olmo2": "olmo-2", "llama-guard3": "llama-guard-3",
            "granite3-1-dense": "granite-3-1", "granite3-1-moe": "granite-3-1",
            "stablelm2": "stablelm-2", "falcon3": "falcon3",
        }
        mapped = special_mappings.get(base, base)

        # Try substring matching: the card's normalized filename should contain
        # both the model base name and the tag
        for norm_key, (model_id, path) in card_index.items():
            if mapped in norm_key and tag_norm in norm_key:
                return (model_id, path)

    return None


# ═══════════════════════════════════════════════════════════════
# Card enrichment
# ═══════════════════════════════════════════════════════════════

def load_card(path: Path) -> ModelCard:
    """Load a model card from a YAML+Markdown file."""
    return ModelCard.from_yaml_file(path)


def enrich_card_ollama(card: ModelCard, ollama_tag: str) -> bool:
    """Add Ollama availability to a model card. Returns True if modified."""
    modified = False
    ollama_base = ollama_tag.split(":")[0]

    # deployment.runtimes.ollama
    if not card.deployment.runtimes.ollama:
        card.deployment.runtimes.ollama = True
        modified = True

    # deployment.runtimes.ollama_tag — fill if empty
    if not card.deployment.runtimes.ollama_tag:
        card.deployment.runtimes.ollama_tag = ollama_tag
        modified = True

    # availability.ollama — set available and fill empty sub-fields
    if not card.availability.ollama.available:
        card.availability.ollama.available = True
        modified = True

    if not card.availability.ollama.model_id:
        card.availability.ollama.model_id = ollama_tag
        modified = True

    ollama_url = f"https://ollama.com/library/{ollama_base}"
    if not card.availability.ollama.url or card.availability.ollama.url == "https://ollama.com/":
        card.availability.ollama.url = ollama_url
        modified = True

    # sources.ollama_url
    if not card.sources.ollama_url:
        card.sources.ollama_url = ollama_url
        modified = True

    return modified


def save_card(card: ModelCard) -> Path:
    """Save a model card back to disk."""
    return write_card_yaml(card, MODELS_DIR)


# ═══════════════════════════════════════════════════════════════
# Part 2: OpenAI SDK Compatibility
# ═══════════════════════════════════════════════════════════════

# Providers with OpenAI-compatible endpoints
OPENAI_COMPAT_PLATFORMS = {
    "together_ai", "groq", "fireworks_ai", "deepinfra",
    "openrouter", "cerebras",
}

# Providers requiring their own SDKs
NATIVE_SDK_PROVIDERS = {
    "anthropic": "anthropic-sdk",
    "google": "google-sdk",
    "cohere": "cohere-sdk",
}


def check_openai_compatible(card: ModelCard) -> bool:
    """Determine if a model is accessible via the OpenAI SDK."""
    provider = card.identity.provider

    # OpenAI models natively use their own SDK
    if provider == "openai":
        return True

    # Ollama serves an OpenAI-compatible endpoint
    if card.deployment.runtimes.ollama:
        return True

    # vLLM serves an OpenAI-compatible endpoint
    if card.deployment.runtimes.vllm:
        return True

    # Check availability on OpenAI-compatible inference platforms
    for plat_name in OPENAI_COMPAT_PLATFORMS:
        plat_entry = getattr(card.availability, plat_name, None)
        if plat_entry and plat_entry.available:
            return True

    return False


def enrich_card_openai_compat(card: ModelCard) -> bool:
    """Add 'openai-compatible' tag if the model can be accessed via the OpenAI SDK.
    Returns True if modified.
    """
    TAG = "openai-compatible"
    if TAG in card.identity.tags:
        return False

    if check_openai_compatible(card):
        card.identity.tags.append(TAG)
        return True

    return False


# ═══════════════════════════════════════════════════════════════
# Main pipeline
# ═══════════════════════════════════════════════════════════════

def run_ollama_enrichment() -> dict[str, Any]:
    """Run the Ollama enrichment pipeline."""
    print("\n" + "=" * 60)
    print("  Part 1: Ollama Availability Enrichment")
    print("=" * 60)

    ollama_models = get_ollama_models()
    print(f"  Ollama registry: {len(ollama_models)} model families")

    # Build index of all our model cards
    print("  Building model card index...")
    card_index = build_card_index()
    print(f"  Indexed {len(card_index)} model cards")

    # Expand model families into individual model:tag entries
    entries: list[tuple[str, str, str]] = []  # (ollama_model, ollama_tag_size, ollama_pull_name)
    for model_name, tags in ollama_models.items():
        if tags:
            for tag in tags:
                pull_name = f"{model_name}:{tag}"
                entries.append((model_name, tag, pull_name))
        else:
            # No tags = single variant (embedding models etc.)
            entries.append((model_name, "", model_name))

    print(f"  Total Ollama entries to match: {len(entries)}")

    matched = []
    unmatched = []
    enriched_count = 0
    errors = []

    for ollama_model, ollama_tag, pull_name in entries:
        result = find_best_match(ollama_model, ollama_tag, card_index)
        if result:
            model_id, card_path = result
            matched.append((pull_name, model_id, card_path))
        else:
            unmatched.append(pull_name)

    print(f"\n  Matched: {len(matched)} / {len(entries)} Ollama entries")
    print(f"  Unmatched: {len(unmatched)}")

    # Enrich matched cards
    for pull_name, model_id, card_path in matched:
        try:
            card = load_card(card_path)
            modified = enrich_card_ollama(card, pull_name)
            if modified:
                save_card(card)
                enriched_count += 1
                print(f"    + {pull_name} -> {model_id}")
            else:
                print(f"    = {pull_name} -> {model_id} (already set)")
        except Exception as e:
            errors.append((pull_name, model_id, str(e)))
            print(f"    ! ERROR {pull_name} -> {model_id}: {e}")

    # Print summary
    print(f"\n  --- Ollama Enrichment Summary ---")
    print(f"  Matched entries:    {len(matched)}")
    print(f"  Cards enriched:     {enriched_count}")
    print(f"  Already set:        {len(matched) - enriched_count}")
    print(f"  Errors:             {len(errors)}")

    if unmatched:
        print(f"\n  Unmatched Ollama models ({len(unmatched)}):")
        for name in sorted(unmatched):
            print(f"    - {name}")

    return {
        "matched": len(matched),
        "enriched": enriched_count,
        "unmatched": len(unmatched),
        "errors": len(errors),
    }


def run_openai_compat_enrichment() -> dict[str, Any]:
    """Run the OpenAI SDK compatibility enrichment across all cards."""
    print("\n" + "=" * 60)
    print("  Part 2: OpenAI SDK Compatibility Tags")
    print("=" * 60)

    all_cards = list(MODELS_DIR.rglob("*.md"))
    print(f"  Scanning {len(all_cards)} model cards...")

    tagged_count = 0
    already_tagged = 0
    errors = []
    tagged_models: list[str] = []

    for card_path in all_cards:
        try:
            card = load_card(card_path)
            if "openai-compatible" in card.identity.tags:
                already_tagged += 1
                continue
            modified = enrich_card_openai_compat(card)
            if modified:
                save_card(card)
                tagged_count += 1
                tagged_models.append(card.identity.model_id)
        except Exception as e:
            errors.append((str(card_path), str(e)))

    print(f"\n  --- OpenAI Compatibility Summary ---")
    print(f"  Newly tagged:     {tagged_count}")
    print(f"  Already tagged:   {already_tagged}")
    print(f"  Errors:           {len(errors)}")

    if tagged_models and len(tagged_models) <= 50:
        print(f"\n  Newly tagged models:")
        for mid in sorted(tagged_models):
            print(f"    + {mid}")
    elif tagged_models:
        print(f"\n  Newly tagged {len(tagged_models)} models (showing first 30):")
        for mid in sorted(tagged_models)[:30]:
            print(f"    + {mid}")
        print(f"    ... and {len(tagged_models) - 30} more")

    if errors and len(errors) <= 10:
        print(f"\n  Errors:")
        for path, err in errors:
            print(f"    ! {path}: {err}")

    return {
        "tagged": tagged_count,
        "already_tagged": already_tagged,
        "errors": len(errors),
    }


def main() -> None:
    print("ModelSpec Ollama & OpenAI Compatibility Enrichment")
    print("=" * 60)

    # Part 1: Ollama availability
    ollama_stats = run_ollama_enrichment()

    # Part 2: OpenAI SDK compatibility
    compat_stats = run_openai_compat_enrichment()

    # Final summary
    print("\n" + "=" * 60)
    print("  FINAL SUMMARY")
    print("=" * 60)
    print(f"  Ollama:  {ollama_stats['matched']} matched, {ollama_stats['enriched']} enriched")
    print(f"  OpenAI:  {compat_stats['tagged']} newly tagged openai-compatible")
    print(f"  Errors:  {ollama_stats['errors'] + compat_stats['errors']} total")
    print("\nDone. Run 'python scripts/ingest_all.py' to reload the graph.")


if __name__ == "__main__":
    main()
