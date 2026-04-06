#!/usr/bin/env python3
"""Seed ModelSpec cards from the models.dev API.

Fetches https://models.dev/api.json, maps entries to ModelCard objects,
and writes YAML+Markdown model cards to the models/ directory.

Usage:
    source .venv/bin/activate && python scripts/seed_models_dev.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import httpx
import yaml

# Ensure the project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from schema.card import (
    ModelCard,
    Identity,
    Licensing,
    Modalities,
    TextDetail,
    VisionDetail,
    AudioDetail,
    Capabilities,
    ReasoningCapability,
    ToolUseCapability,
    Cost,
    Sources,
)
from schema.enums import ModelStatus, ModelType, Modality


# ── Provider configuration ──────────────────────────────────────
# Map models.dev provider IDs to our directory slugs and display names.
# Only these canonical providers will be seeded (the actual model creators).
PROVIDER_MAP: dict[str, dict] = {
    "openai": {
        "slug": "openai",
        "display": "OpenAI",
        "country": "US",
        "org_type": "private",
    },
    "anthropic": {
        "slug": "anthropic",
        "display": "Anthropic",
        "country": "US",
        "org_type": "private",
    },
    "google": {
        "slug": "google",
        "display": "Google DeepMind",
        "country": "US",
        "org_type": "private",
    },
    "llama": {
        "slug": "meta",
        "display": "Meta",
        "country": "US",
        "org_type": "private",
    },
    "mistral": {
        "slug": "mistral",
        "display": "Mistral AI",
        "country": "FR",
        "org_type": "private",
    },
    "deepseek": {
        "slug": "deepseek",
        "display": "DeepSeek",
        "country": "CN",
        "org_type": "private",
    },
    "alibaba": {
        "slug": "qwen",
        "display": "Alibaba / Qwen Team",
        "country": "CN",
        "org_type": "private",
    },
    "xai": {
        "slug": "xai",
        "display": "xAI",
        "country": "US",
        "org_type": "private",
    },
    "cohere": {
        "slug": "cohere",
        "display": "Cohere",
        "country": "CA",
        "org_type": "private",
    },
    "minimax": {
        "slug": "minimax",
        "display": "MiniMax",
        "country": "CN",
        "org_type": "private",
    },
    "perplexity": {
        "slug": "perplexity",
        "display": "Perplexity AI",
        "country": "US",
        "org_type": "private",
    },
    "moonshotai": {
        "slug": "moonshot",
        "display": "Moonshot AI",
        "country": "CN",
        "org_type": "private",
    },
    "inception": {
        "slug": "inception",
        "display": "Inception (Mercury)",
        "country": "AE",
        "org_type": "private",
    },
    "stepfun": {
        "slug": "stepfun",
        "display": "StepFun",
        "country": "CN",
        "org_type": "private",
    },
    "cerebras": {
        "slug": "cerebras",
        "display": "Cerebras",
        "country": "US",
        "org_type": "private",
    },
    # NOTE: perplexity-agent excluded -- it lists proxy entries for other
    # providers' models (openai/*, anthropic/*, etc.), not original Perplexity models.
    # The "perplexity" provider already covers Sonar models.
    "upstage": {
        "slug": "upstage",
        "display": "Upstage",
        "country": "KR",
        "org_type": "private",
    },
}


def slugify(name: str) -> str:
    """Turn a model name/id into a filesystem-safe slug.

    Examples:
        'Claude Opus 4.5' -> 'claude-opus-4-5'
        'gpt-5.2-codex'   -> 'gpt-5-2-codex'
        'GPT-OSS-120B'    -> 'gpt-oss-120b'
    """
    s = name.lower().strip()
    # Replace dots with dashes (version numbers: 4.5 -> 4-5)
    s = s.replace(".", "-")
    # Replace underscores, slashes, colons with dashes
    s = re.sub(r"[_/:\\]+", "-", s)
    # Replace spaces and other non-alphanum-dash with dashes
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    # Collapse multiple dashes
    s = re.sub(r"-+", "-", s)
    # Strip leading/trailing dashes
    s = s.strip("-")
    return s


def map_modalities(raw: dict) -> tuple[list[Modality], list[Modality]]:
    """Map models.dev modality strings to Modality enum values."""
    modality_map = {
        "text": Modality.TEXT,
        "image": Modality.IMAGE,
        "audio": Modality.AUDIO,
        "video": Modality.VIDEO,
        "pdf": Modality.PDF,
        "code": Modality.CODE,
        "embeddings": Modality.EMBEDDINGS,
    }
    inputs = []
    for m in raw.get("input", []):
        if m in modality_map:
            inputs.append(modality_map[m])
    outputs = []
    for m in raw.get("output", []):
        if m in modality_map:
            outputs.append(modality_map[m])
    return inputs, outputs


def determine_model_type(
    name: str,
    raw: dict,
    input_modalities: list[Modality],
    output_modalities: list[Modality],
) -> ModelType:
    """Determine the primary model type from name, flags, and modalities."""
    name_lower = name.lower()

    # Embedding models
    if "embed" in name_lower:
        return ModelType.EMBEDDING_TEXT

    # Reranker
    if "rerank" in name_lower:
        return ModelType.RERANKER

    # ASR / whisper
    if "whisper" in name_lower or "asr" in name_lower:
        return ModelType.AUDIO_ASR

    # TTS
    if "tts" in name_lower:
        return ModelType.AUDIO_TTS

    # Image generation
    if Modality.IMAGE in output_modalities:
        return ModelType.IMAGE_GENERATION
    if "flux" in name_lower or "dall" in name_lower or "imagen" in name_lower:
        return ModelType.IMAGE_GENERATION

    # Video generation
    if Modality.VIDEO in output_modalities:
        return ModelType.VIDEO_GENERATION

    # Coding models
    if "coder" in name_lower or "codex" in name_lower or "codestral" in name_lower or "devstral" in name_lower:
        return ModelType.LLM_CODE

    # Reasoning models
    if raw.get("reasoning", False):
        return ModelType.LLM_REASONING

    # Vision-language models
    if Modality.IMAGE in input_modalities or "vision" in name_lower or "-vl" in name_lower:
        return ModelType.VLM

    # Audio realtime
    if "realtime" in name_lower and (Modality.AUDIO in input_modalities or Modality.AUDIO in output_modalities):
        return ModelType.AUDIO_REALTIME

    # Default
    return ModelType.LLM_CHAT


def map_status(raw: dict) -> ModelStatus:
    """Map models.dev status hints to ModelStatus."""
    name_lower = raw.get("name", "").lower()
    raw_id = raw.get("id", "").lower()

    if "preview" in name_lower or "preview" in raw_id:
        return ModelStatus.PREVIEW
    if "beta" in name_lower or "beta" in raw_id:
        return ModelStatus.BETA
    if "alpha" in name_lower or "alpha" in raw_id:
        return ModelStatus.ALPHA
    if "deprecated" in name_lower:
        return ModelStatus.DEPRECATED
    if "exp" in name_lower or "-exp" in raw_id:
        return ModelStatus.PREVIEW

    return ModelStatus.ACTIVE


def build_model_card(
    raw: dict,
    provider_id: str,
    provider_cfg: dict,
) -> ModelCard:
    """Build a ModelCard from a models.dev model entry."""
    slug = provider_cfg["slug"]
    display_name = raw.get("name", raw.get("id", "Unknown"))

    # Build the model_id slug
    model_slug = slugify(raw.get("id", display_name))
    model_id = f"{slug}/{model_slug}"

    # Modalities
    raw_modalities = raw.get("modalities", {})
    input_mods, output_mods = map_modalities(raw_modalities)

    # Model type
    model_type = determine_model_type(display_name, raw, input_mods, output_mods)

    # Status
    status = map_status(raw)

    # Limits
    limits = raw.get("limit", {})
    context_window = limits.get("context")
    max_input = limits.get("input")
    max_output = limits.get("output")

    # Cost
    raw_cost = raw.get("cost", {})

    # Build the card
    card = ModelCard(
        identity=Identity(
            model_id=model_id,
            display_name=display_name,
            provider=slug,
            provider_display=provider_cfg["display"],
            family=raw.get("family", ""),
            version=raw.get("id", ""),
            release_date=raw.get("release_date", ""),
            last_updated=raw.get("last_updated", ""),
            status=status,
            model_type=model_type,
        ),
        licensing=Licensing(
            open_weights=raw.get("open_weights", False),
            origin_country=provider_cfg.get("country", ""),
        ),
        modalities=Modalities(
            input=input_mods,
            output=output_mods,
            text=TextDetail(
                context_window=context_window,
                max_input_tokens=max_input,
                max_output_tokens=max_output,
                json_mode=raw.get("structured_output", None),
            ),
            vision=VisionDetail(
                supported=Modality.IMAGE in input_mods,
            ),
            audio=AudioDetail(
                input_supported=Modality.AUDIO in input_mods,
                output_supported=Modality.AUDIO in output_mods,
            ),
        ),
        capabilities=Capabilities(
            reasoning=ReasoningCapability(
                chain_of_thought=raw.get("reasoning", False),
            ),
            tool_use=ToolUseCapability(
                function_calling=raw.get("tool_call", False),
            ),
        ),
        cost=Cost(
            input=raw_cost.get("input") if raw_cost else None,
            output=raw_cost.get("output") if raw_cost else None,
            cache_read=raw_cost.get("cache_read") if raw_cost else None,
            cache_write=raw_cost.get("cache_write") if raw_cost else None,
        ),
        sources=Sources(
            models_dev_url=f"https://models.dev/{provider_id}",
        ),
        card_schema_version="3.0",
        card_author="models.dev-seeder",
        card_created="2026-04-05",
        card_updated="2026-04-05",
        prose_body=_build_prose(display_name, raw, model_type, provider_cfg),
    )

    return card


def _build_prose(
    display_name: str,
    raw: dict,
    model_type: ModelType,
    provider_cfg: dict,
) -> str:
    """Generate a brief prose body for the model card."""
    provider = provider_cfg["display"]
    family = raw.get("family", "")
    lines = [f"# {display_name}", ""]

    # Overview
    type_label = model_type.value.replace("-", " ").title()
    parts = [f"{display_name} is a {type_label} model from {provider}."]
    if family:
        parts.append(f"Part of the {family} family.")
    if raw.get("knowledge"):
        parts.append(f"Knowledge cutoff: {raw['knowledge']}.")
    lines.append(" ".join(parts))
    lines.append("")

    # Quick facts
    facts = []
    if raw.get("reasoning"):
        facts.append("Extended reasoning / chain-of-thought")
    if raw.get("tool_call"):
        facts.append("Function calling / tool use")
    if raw.get("structured_output"):
        facts.append("Structured output (JSON mode)")
    if raw.get("open_weights"):
        facts.append("Open weights")
    if raw.get("attachment"):
        facts.append("File/image attachments")

    if facts:
        lines.append("## Key Features")
        for f in facts:
            lines.append(f"- {f}")
        lines.append("")

    return "\n".join(lines)


def card_to_yaml_clean(card: ModelCard) -> str:
    """Serialize a ModelCard to clean YAML frontmatter + markdown prose.

    The from_yaml_string parser expects:
      - Identity fields FLAT at the top level
      - Other sections as nested dicts
      - Card metadata flat at the top level

    Uses model_dump(mode='json') to avoid Python-specific YAML tags for enums.
    """
    data = card.model_dump(
        mode="json",
        exclude_none=False,
        exclude={"prose_body", "card_completeness"},
    )

    # Flatten identity fields to top level (matching from_yaml_string expectations)
    identity = data.pop("identity", {})

    # Build ordered output: identity fields first, then sections, then metadata
    from collections import OrderedDict

    out = OrderedDict()
    for k, v in identity.items():
        out[k] = v

    # Add all remaining sections
    section_keys = [
        "architecture", "lineage", "licensing", "modalities", "capabilities",
        "cost", "availability", "benchmarks", "deployment", "risk_governance",
        "inference_performance", "adoption", "downselect", "sources",
    ]
    for sk in section_keys:
        if sk in data:
            out[sk] = data.pop(sk)

    # Card metadata
    for mk in ("card_schema_version", "card_author", "card_created", "card_updated"):
        if mk in data:
            out[mk] = data.pop(mk)

    yaml_str = yaml.dump(
        dict(out),
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=120,
    )
    return f"---\n{yaml_str}---\n\n{card.prose_body}"


def main() -> None:
    print("Fetching models.dev API...")
    resp = httpx.get(
        "https://models.dev/api.json",
        headers={"User-Agent": "ModelSpec-Seeder/1.0"},
        follow_redirects=True,
        timeout=60,
    )
    resp.raise_for_status()
    api_data = resp.json()
    print(f"  Fetched {len(api_data)} providers from API")

    models_dir = PROJECT_ROOT / "models"
    total_created = 0
    total_errors = 0
    total_completeness = 0.0
    seen_model_ids: set[str] = set()

    for provider_id, provider_cfg in PROVIDER_MAP.items():
        if provider_id not in api_data:
            print(f"  SKIP: provider '{provider_id}' not found in API")
            continue

        provider_data = api_data[provider_id]
        raw_models = provider_data.get("models", {})
        slug = provider_cfg["slug"]

        # Ensure provider directory exists
        provider_dir = models_dir / slug
        provider_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n  Processing {provider_cfg['display']} ({provider_id}): {len(raw_models)} models")

        for model_key, raw_model in raw_models.items():
            try:
                card = build_model_card(raw_model, provider_id, provider_cfg)

                # Skip duplicates (e.g. perplexity and perplexity-agent overlap)
                if card.identity.model_id in seen_model_ids:
                    continue
                seen_model_ids.add(card.identity.model_id)

                # Determine file path
                file_slug = slugify(raw_model.get("id", model_key))
                file_path = provider_dir / f"{file_slug}.md"

                # Write the card
                content = card_to_yaml_clean(card)
                file_path.write_text(content, encoding="utf-8")

                # Validate by round-tripping
                loaded = ModelCard.from_yaml_file(file_path)
                completeness = loaded.card_completeness
                total_completeness += completeness
                total_created += 1

                print(f"    OK  {card.identity.model_id:55s} ({completeness:5.1f}% complete)")

            except Exception as e:
                total_errors += 1
                print(f"    ERR {model_key}: {e}")

    # Summary
    print("\n" + "=" * 70)
    print(f"SUMMARY")
    print(f"  Total cards created:     {total_created}")
    print(f"  Total errors:            {total_errors}")
    if total_created > 0:
        avg = total_completeness / total_created
        print(f"  Average completeness:    {avg:.1f}%")
    print(f"  Unique model IDs:        {len(seen_model_ids)}")
    print(f"  Output directory:        {models_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
