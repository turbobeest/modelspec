#!/usr/bin/env python3
"""Enrich existing ModelSpec YAML cards with inferred data.

Post-processing script that loads each existing card, fills in missing
license_type and capability flags based on provider defaults and model_type,
then writes the card back. Does not create new cards or re-scrape anything.

Usage:
    source .venv/bin/activate && python scripts/enrich_cards.py
"""

from __future__ import annotations

import glob
import sys
import time
from pathlib import Path
from typing import Any

import yaml

# Ensure the project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from schema.card import ModelCard  # noqa: E402
from schema.enums import LicenseType, ModelType, Tier  # noqa: E402

MODELS_DIR = PROJECT_ROOT / "models"


# ═══════════════════════════════════════════════════════════════
# Provider → License defaults
# ═══════════════════════════════════════════════════════════════

PROVIDER_LICENSE: dict[str, LicenseType] = {
    "anthropic": LicenseType.PROPRIETARY,
    "openai": LicenseType.PROPRIETARY,
    "google": LicenseType.PROPRIETARY,  # except Gemma — handled as special case
    "mistral": LicenseType.APACHE_2_0,
    "meta": LicenseType.LLAMA_COMMUNITY,
    "qwen": LicenseType.APACHE_2_0,
    "deepseek": LicenseType.DEEPSEEK,
    "cohere": LicenseType.OTHER,
    "xai": LicenseType.PROPRIETARY,
    "stability": LicenseType.OTHER,
    "tii": LicenseType.APACHE_2_0,       # Falcon
    "microsoft": LicenseType.MIT,         # Phi models
    "ibm": LicenseType.APACHE_2_0,       # Granite
    "nvidia": LicenseType.OTHER,
    "allen-ai": LicenseType.APACHE_2_0,
    "baai": LicenseType.MIT,
    "sentence-transformers": LicenseType.APACHE_2_0,
    # Additional providers
    "voyage": LicenseType.PROPRIETARY,
    "perplexity": LicenseType.PROPRIETARY,
    "01-ai": LicenseType.APACHE_2_0,     # Yi models
    "snowflake": LicenseType.APACHE_2_0,
    "salesforce": LicenseType.APACHE_2_0,
    "together": LicenseType.APACHE_2_0,
    "nomic": LicenseType.APACHE_2_0,
    "jina": LicenseType.APACHE_2_0,
    "intfloat": LicenseType.MIT,
    "cerebras": LicenseType.LLAMA_COMMUNITY,  # They host Llama
    "upstage": LicenseType.APACHE_2_0,
    "minimax": LicenseType.OTHER,
    "moonshot": LicenseType.PROPRIETARY,
    "tencent": LicenseType.OTHER,
    "zhipu": LicenseType.OTHER,
    "baichuan": LicenseType.OTHER,
    "samsung": LicenseType.OTHER,
    "kakao": LicenseType.OTHER,
    "inception": LicenseType.APACHE_2_0,
    "rwkv": LicenseType.APACHE_2_0,
    "skywork": LicenseType.OTHER,
    "stepfun": LicenseType.OTHER,
    "openbmb": LicenseType.APACHE_2_0,
    "liquid": LicenseType.OTHER,
    "moondream": LicenseType.APACHE_2_0,
    "nous-research": LicenseType.APACHE_2_0,
    "teknium": LicenseType.APACHE_2_0,
    "unsloth": LicenseType.APACHE_2_0,
    "black-forest-labs": LicenseType.OTHER,  # FLUX
    "ai21": LicenseType.PROPRIETARY,
}


# ═══════════════════════════════════════════════════════════════
# Fix 1 & 3: License inference
# ═══════════════════════════════════════════════════════════════

def _is_gemma_model(card: ModelCard) -> bool:
    """Check if this is a Google Gemma-family model (not Gemini)."""
    model_id = card.identity.model_id.lower()
    family = card.identity.family.lower() if card.identity.family else ""
    display = card.identity.display_name.lower()
    return "gemma" in model_id or "gemma" in family or "gemma" in display


def infer_license(card: ModelCard) -> LicenseType | None:
    """Infer license_type from provider, model name, open_weights flag, and tags."""
    provider = card.identity.provider.lower()
    tags = [t.lower() for t in card.identity.tags]

    # Special case: Google Gemma → gemma license
    if provider == "google" and _is_gemma_model(card):
        return LicenseType.GEMMA

    # Special case: Cerebras hosts Llama models
    if provider == "cerebras":
        model_id = card.identity.model_id.lower()
        if "llama" in model_id:
            return LicenseType.LLAMA_COMMUNITY

    # Special case: models with "llama" in name from any provider
    model_id = card.identity.model_id.lower()
    family = (card.identity.family or "").lower()
    if "llama" in model_id or family == "llama":
        return LicenseType.LLAMA_COMMUNITY

    # Check tags for license hints
    for tag in tags:
        if "apache" in tag:
            return LicenseType.APACHE_2_0
        if "mit" in tag:
            return LicenseType.MIT

    # Provider default
    if provider in PROVIDER_LICENSE:
        return PROVIDER_LICENSE[provider]

    # Fallback: if closed-weights, assume proprietary
    if not card.licensing.open_weights:
        return LicenseType.PROPRIETARY

    # Open-weights model from unknown provider → other
    return LicenseType.OTHER


def enrich_license(card: ModelCard) -> bool:
    """Fill in license_type if missing. Returns True if changed."""
    if card.licensing.license_type is not None:
        return False

    license_type = infer_license(card)
    if license_type is None:
        return False

    card.licensing.license_type = license_type
    return True


# ═══════════════════════════════════════════════════════════════
# Fix 2: Capabilities from model_type
# ═══════════════════════════════════════════════════════════════

def enrich_capabilities(card: ModelCard) -> bool:
    """Infer capability flags from model_type. Returns True if changed."""
    model_type = card.identity.model_type
    if model_type is None:
        return False

    changed = False
    caps = card.capabilities
    mods = card.modalities

    if model_type == ModelType.LLM_CHAT:
        # Most chat models support function calling and chain-of-thought
        if not caps.tool_use.function_calling:
            caps.tool_use.function_calling = True
            changed = True
        if not caps.reasoning.chain_of_thought:
            caps.reasoning.chain_of_thought = True
            changed = True

    elif model_type == ModelType.LLM_REASONING:
        if not caps.reasoning.chain_of_thought:
            caps.reasoning.chain_of_thought = True
            changed = True
        if not caps.reasoning.mathematical:
            caps.reasoning.mathematical = True
            changed = True
        if not caps.reasoning.multi_step:
            caps.reasoning.multi_step = True
            changed = True

    elif model_type == ModelType.LLM_CODE:
        if caps.coding.overall is None:
            caps.coding.overall = Tier.TIER_2
            changed = True
        if not caps.coding.code_completion:
            caps.coding.code_completion = True
            changed = True
        if not caps.coding.debugging:
            caps.coding.debugging = True
            changed = True

    elif model_type == ModelType.VLM:
        if not mods.vision.supported:
            mods.vision.supported = True
            changed = True

    elif model_type == ModelType.EMBEDDING_TEXT:
        if not mods.embeddings.supported:
            mods.embeddings.supported = True
            changed = True

    elif model_type == ModelType.RERANKER:
        if not mods.reranking.supported:
            mods.reranking.supported = True
            changed = True

    # safety-classifier: no special capabilities needed

    return changed


# ═══════════════════════════════════════════════════════════════
# YAML writing (same pattern as seed_huggingface.py)
# ═══════════════════════════════════════════════════════════════

def _convert_enums(obj: Any) -> Any:
    """Recursively convert enum values in a dict/list."""
    if isinstance(obj, dict):
        return {k: _convert_enums(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_enums(item) for item in obj]
    elif hasattr(obj, "value"):
        return obj.value
    return obj


def write_card_yaml(card: ModelCard, filepath: Path) -> None:
    """Write a ModelCard back to its YAML+Markdown file.

    Uses the same serialization pattern as seed_huggingface.py's write_card_yaml.
    """
    data: dict[str, Any] = {}

    # Identity fields go at top level
    identity_dict = card.identity.model_dump(exclude_none=False)
    for k, v in identity_dict.items():
        if hasattr(v, "value"):
            identity_dict[k] = v.value
        elif isinstance(v, list):
            identity_dict[k] = [item.value if hasattr(item, "value") else item for item in v]
    data.update(identity_dict)

    # Other sections are nested
    sections = [
        "architecture", "lineage", "licensing", "modalities", "capabilities",
        "cost", "availability", "benchmarks", "deployment", "risk_governance",
        "inference_performance", "adoption", "downselect", "sources",
    ]
    for section_name in sections:
        section = getattr(card, section_name)
        section_data = section.model_dump(exclude_none=False)
        section_data = _convert_enums(section_data)
        data[section_name] = section_data

    # Card metadata
    data["card_schema_version"] = card.card_schema_version
    data["card_author"] = card.card_author
    data["card_created"] = card.card_created
    data["card_updated"] = card.card_updated

    yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    content = f"---\n{yaml_str}---\n\n{card.prose_body}"

    filepath.write_text(content, encoding="utf-8")


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main() -> None:
    print("=" * 60)
    print("  ModelSpec Card Enrichment")
    print("=" * 60)

    files = sorted(glob.glob(str(MODELS_DIR / "**" / "*.md"), recursive=True))
    total = len(files)
    print(f"Found {total} model card files\n")

    if total == 0:
        print("No cards found. Exiting.")
        return

    # Stats
    license_enriched = 0
    caps_enriched = 0
    cards_modified = 0
    errors = 0
    error_details: list[tuple[str, str]] = []

    # Per-license-type counts
    license_assignments: dict[str, int] = {}
    # Per-model-type capability enrichment counts
    caps_by_type: dict[str, int] = {}

    t0 = time.monotonic()

    for i, filepath in enumerate(files, start=1):
        try:
            card = ModelCard.from_yaml_file(filepath)
            modified = False

            # Fix 1 & 3: License enrichment
            if enrich_license(card):
                license_enriched += 1
                modified = True
                lt = card.licensing.license_type.value
                license_assignments[lt] = license_assignments.get(lt, 0) + 1

            # Fix 2: Capability enrichment
            if enrich_capabilities(card):
                caps_enriched += 1
                modified = True
                mt = card.identity.model_type.value if card.identity.model_type else "unknown"
                caps_by_type[mt] = caps_by_type.get(mt, 0) + 1

            # Write back if changed
            if modified:
                card.card_updated = "2026-04-05"
                write_card_yaml(card, Path(filepath))
                cards_modified += 1

        except Exception as exc:
            errors += 1
            error_details.append((filepath, f"{type(exc).__name__}: {exc}"))

        if i % 100 == 0 or i == total:
            elapsed = time.monotonic() - t0
            rate = i / elapsed if elapsed > 0 else 0
            print(f"  [{i:>4}/{total}] {cards_modified} modified, {errors} errors  ({rate:.1f} cards/sec)")

    elapsed = time.monotonic() - t0

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print("ENRICHMENT SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Total cards scanned:   {total}")
    print(f"  Cards modified:        {cards_modified}")
    print(f"  License enriched:      {license_enriched}")
    print(f"  Capabilities enriched: {caps_enriched}")
    print(f"  Errors:                {errors}")
    print(f"  Time:                  {elapsed:.1f}s")

    if license_assignments:
        print(f"\n-- License assignments --")
        for lt, count in sorted(license_assignments.items(), key=lambda x: -x[1]):
            print(f"    {lt:<25s} {count:>5}")

    if caps_by_type:
        print(f"\n-- Capability enrichment by model type --")
        for mt, count in sorted(caps_by_type.items(), key=lambda x: -x[1]):
            print(f"    {mt:<25s} {count:>5}")

    if error_details:
        print(f"\n-- Errors (first 10) --")
        for path, err in error_details[:10]:
            print(f"    {path}")
            print(f"      {err}")

    print(f"\n{'=' * 60}")


if __name__ == "__main__":
    main()
