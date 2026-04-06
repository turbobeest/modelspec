#!/usr/bin/env python3
"""Seed ModelSpec cards from the HuggingFace Hub API.

Provides reusable functions to search HF by organization, map metadata
to ModelCard objects, and write YAML+Markdown model cards.

Usage as a library:
    from scripts.seed_huggingface import seed_org, HFProviderConfig

    seed_org(HFProviderConfig(
        hf_org="meta-llama",
        provider_slug="meta",
        provider_display="Meta",
        country="US",
    ))

Usage standalone:
    source .venv/bin/activate && python scripts/seed_huggingface.py
"""

from __future__ import annotations

import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
import yaml

# Ensure the project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from schema.card import (  # noqa: E402
    Adoption,
    Architecture,
    Capabilities,
    CodingCapability,
    Cost,
    Deployment,
    Identity,
    Licensing,
    Lineage,
    Modalities,
    ModelCard,
    ReasoningCapability,
    Runtimes,
    Sources,
    TextDetail,
    ToolUseCapability,
    VisionDetail,
    EmbeddingDetail,
    ImageGenDetail,
    AudioDetail,
    VideoDetail,
)
from schema.enums import (  # noqa: E402
    LicenseType,
    ModelStatus,
    ModelType,
    Modality,
    OrgType,
)

MODELS_DIR = PROJECT_ROOT / "models"


# ── Configuration ──────────────────────────────────────────────────

@dataclass
class HFProviderConfig:
    """Configuration for scraping a HuggingFace organization."""
    hf_org: str                          # HuggingFace org name (e.g. "meta-llama")
    provider_slug: str                   # Our directory slug (e.g. "meta")
    provider_display: str                # Display name (e.g. "Meta")
    country: str = ""                    # ISO country code
    org_type: str = "private"            # private, academic, etc.
    limit: int = 100                     # Max models to fetch
    min_downloads: int = 100             # Skip models with fewer downloads
    pipeline_tags: list[str] = field(default_factory=list)  # Filter by pipeline_tag if set
    extra_search: str = ""               # Additional search query
    include_gated: bool = True           # Include gated models


# ── HuggingFace API ────────────────────────────────────────────────

HF_API_BASE = "https://huggingface.co/api"


def fetch_hf_models(config: HFProviderConfig) -> list[dict]:
    """Fetch models from HuggingFace Hub API for a given organization."""
    all_models = []

    params: dict[str, Any] = {
        "author": config.hf_org,
        "sort": "downloads",
        "direction": "-1",
        "limit": min(config.limit, 100),
    }
    if config.extra_search:
        params["search"] = config.extra_search

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(f"{HF_API_BASE}/models", params=params)
            resp.raise_for_status()
            models = resp.json()
            all_models.extend(models)

            # If we need more and there are more available, paginate
            # HF API doesn't have cursor pagination; we get up to limit
            # For now, first page is enough for most orgs

    except httpx.HTTPError as e:
        print(f"  WARNING: Failed to fetch from HF for {config.hf_org}: {e}")
        return []

    # Filter by downloads
    filtered = [
        m for m in all_models
        if m.get("downloads", 0) >= config.min_downloads
    ]

    # Filter by pipeline_tag if specified
    if config.pipeline_tags:
        filtered = [
            m for m in filtered
            if m.get("pipeline_tag", "") in config.pipeline_tags
        ]

    return filtered


def fetch_hf_model_detail(model_id: str) -> dict | None:
    """Fetch detailed info for a single HF model."""
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(f"{HF_API_BASE}/models/{model_id}")
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError:
        return None


# ── Slugification ──────────────────────────────────────────────────

def slugify(name: str) -> str:
    """Turn a model name/id into a filesystem-safe slug."""
    s = name.lower().strip()
    # Take just the model part if it has org/ prefix
    if "/" in s:
        s = s.split("/", 1)[1]
    s = s.replace(".", "-")
    s = re.sub(r"[_/:\\]+", "-", s)
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s)
    s = s.strip("-")
    return s


# ── Model Type Detection ──────────────────────────────────────────

def determine_model_type(hf_model: dict) -> ModelType:
    """Determine ModelType from HuggingFace metadata."""
    name = (hf_model.get("id", "") + " " + hf_model.get("modelId", "")).lower()
    pipeline = hf_model.get("pipeline_tag", "")
    tags = [t.lower() for t in hf_model.get("tags", [])]

    # Safety / guard models
    if any(kw in name for kw in ("guard", "shield", "safeguard", "safety-classifier")):
        return ModelType.SAFETY_CLASSIFIER

    # Reward models
    if "reward" in name or pipeline == "text-classification" and "reward" in " ".join(tags):
        return ModelType.REWARD_MODEL

    # Reranker
    if "rerank" in name or "reranker" in name:
        return ModelType.RERANKER

    # Embeddings
    if pipeline == "feature-extraction" or pipeline == "sentence-similarity":
        return ModelType.EMBEDDING_TEXT
    if "embed" in name and "embedding" not in name.replace("embedding", ""):
        return ModelType.EMBEDDING_TEXT
    if "embedding" in name:
        return ModelType.EMBEDDING_TEXT

    # Image generation
    if pipeline in ("text-to-image", "image-to-image"):
        return ModelType.IMAGE_GENERATION

    # Video generation
    if pipeline == "text-to-video":
        return ModelType.VIDEO_GENERATION

    # ASR
    if pipeline == "automatic-speech-recognition" or "whisper" in name or "asr" in name:
        return ModelType.AUDIO_ASR

    # TTS
    if pipeline == "text-to-speech" or "tts" in name:
        return ModelType.AUDIO_TTS

    # Code models
    if any(kw in name for kw in ("coder", "codex", "codestral", "starcoder", "codegen",
                                   "code-llama", "granite-code", "devstral")):
        return ModelType.LLM_CODE
    if pipeline == "text-generation" and "code" in " ".join(tags):
        return ModelType.LLM_CODE

    # Reasoning
    if any(kw in name for kw in ("reason", "think", "r1-", "qwq", "-r1", "deepthink")):
        return ModelType.LLM_REASONING

    # VLM
    if pipeline == "image-text-to-text" or pipeline == "visual-question-answering":
        return ModelType.VLM
    if any(kw in name for kw in ("vision", "-vl-", "-vl ", "vlm", "paligemma",
                                   "molmo", "moondream", "cogview", "florence", "nvlm")):
        return ModelType.VLM

    # Document OCR
    if any(kw in name for kw in ("ocr", "document", "doctr")):
        return ModelType.DOCUMENT_OCR

    # Base models (no instruct/chat tag)
    if pipeline == "text-generation":
        if any(kw in name for kw in ("base", "-base")):
            return ModelType.LLM_BASE
        if "instruct" not in name and "chat" not in name:
            # Might be a base model, but default to chat for well-known ones
            pass

    # Default
    return ModelType.LLM_CHAT


# ── License Mapping ────────────────────────────────────────────────

LICENSE_MAP: dict[str, LicenseType] = {
    "apache-2.0": LicenseType.APACHE_2_0,
    "mit": LicenseType.MIT,
    "llama3": LicenseType.LLAMA_COMMUNITY,
    "llama3.1": LicenseType.LLAMA_COMMUNITY,
    "llama3.2": LicenseType.LLAMA_COMMUNITY,
    "llama3.3": LicenseType.LLAMA_COMMUNITY,
    "llama-3.3": LicenseType.LLAMA_COMMUNITY,
    "llama4": LicenseType.LLAMA_COMMUNITY,
    "llama-4": LicenseType.LLAMA_COMMUNITY,
    "gemma": LicenseType.GEMMA,
    "cc-by-4.0": LicenseType.CC_BY_4_0,
    "cc-by-nc-4.0": LicenseType.CC_BY_NC_4_0,
    "openrail": LicenseType.OPENRAIL,
    "openrail++": LicenseType.OPENRAIL,
    "gpl-3.0": LicenseType.GPL_3_0,
    "deepseek": LicenseType.DEEPSEEK,
}


def map_license(hf_model: dict) -> tuple[LicenseType | None, bool]:
    """Map HF license string to LicenseType. Returns (license_type, is_open_weights)."""
    lic = hf_model.get("license", "") or ""
    tags = hf_model.get("tags", [])

    # Determine open_weights from gated status and tags
    is_open = not hf_model.get("private", False)

    license_type = LICENSE_MAP.get(lic.lower())
    if license_type is None and lic:
        license_type = LicenseType.OTHER

    return license_type, is_open


# ── Parameter Count Extraction ─────────────────────────────────────

def extract_params(hf_model: dict) -> int | None:
    """Try to extract parameter count from HF metadata or model name."""
    # Check safetensors metadata
    safetensors = hf_model.get("safetensors", {})
    if isinstance(safetensors, dict):
        total = safetensors.get("total", 0)
        if total and total > 0:
            return total

    # Parse from model name
    name = hf_model.get("id", "").lower()
    # Match patterns like "70b", "7B", "1.5B", "30b-a3b"
    match = re.search(r"(\d+(?:\.\d+)?)\s*[bB](?:\b|[-_])", name)
    if match:
        billions = float(match.group(1))
        return int(billions * 1_000_000_000)

    return None


# ── Status Mapping ─────────────────────────────────────────────────

def determine_status(hf_model: dict) -> ModelStatus:
    """Determine model status from HF metadata."""
    name = hf_model.get("id", "").lower()
    tags = [t.lower() for t in hf_model.get("tags", [])]

    if "deprecated" in name or "deprecated" in tags:
        return ModelStatus.DEPRECATED
    if "preview" in name:
        return ModelStatus.PREVIEW
    if "beta" in name:
        return ModelStatus.BETA
    if "alpha" in name:
        return ModelStatus.ALPHA

    return ModelStatus.ACTIVE


# ── Model Card Builder ─────────────────────────────────────────────

def build_model_card(hf_model: dict, config: HFProviderConfig) -> ModelCard:
    """Build a ModelCard from HuggingFace model metadata."""
    hf_id = hf_model.get("id", hf_model.get("modelId", "unknown"))
    model_name = hf_id.split("/")[-1] if "/" in hf_id else hf_id
    model_slug = slugify(model_name)
    model_id = f"{config.provider_slug}/{model_slug}"

    # Display name: clean up the model name
    display_name = model_name.replace("-", " ").replace("_", " ")
    # Capitalize important parts
    display_name = re.sub(r'\b(\d+[bBmMkK])\b', lambda m: m.group(1).upper(), display_name)
    # Don't over-clean: keep the original if it's already reasonable
    if len(display_name) < 3:
        display_name = model_name

    model_type = determine_model_type(hf_model)
    status = determine_status(hf_model)
    license_type, is_open = map_license(hf_model)
    params = extract_params(hf_model)

    # Tags from HF
    hf_tags = hf_model.get("tags", [])
    our_tags = []
    if hf_model.get("gated", False):
        our_tags.append("gated")
    if params and params > 100_000_000_000:
        our_tags.append("frontier")
    pipeline = hf_model.get("pipeline_tag", "")
    if pipeline:
        our_tags.append(pipeline)

    # Library name
    library = hf_model.get("library_name", "")

    # Build card
    card = ModelCard(
        identity=Identity(
            model_id=model_id,
            display_name=display_name,
            provider=config.provider_slug,
            provider_display=config.provider_display,
            family=_extract_family(model_name, config.provider_slug),
            release_date=_extract_date(hf_model),
            last_updated=hf_model.get("lastModified", "")[:10] if hf_model.get("lastModified") else "",
            status=status,
            model_type=model_type,
            tags=our_tags,
            pipeline_tag=pipeline,
        ),
        architecture=Architecture(
            total_parameters=params,
        ),
        lineage=Lineage(
            base_model=_extract_base_model(hf_model),
            library_name=library,
        ),
        licensing=Licensing(
            open_weights=is_open,
            license_type=license_type,
            origin_country=config.country,
            origin_org_type=OrgType(config.org_type) if config.org_type in [e.value for e in OrgType] else None,
        ),
        modalities=_build_modalities(hf_model, model_type),
        deployment=_build_deployment(hf_model, library),
        adoption=Adoption(
            huggingface_downloads=hf_model.get("downloads"),
            huggingface_likes=hf_model.get("likes"),
        ),
        sources=Sources(
            huggingface_url=f"https://huggingface.co/{hf_id}",
            last_scraped_huggingface="2026-04-05",
        ),
        card_schema_version="3.0",
        card_author="huggingface-seeder",
        card_created="2026-04-05",
        card_updated="2026-04-05",
        prose_body=f"# {display_name}\n\nAuto-generated from HuggingFace Hub metadata for [{hf_id}](https://huggingface.co/{hf_id}).",
    )

    return card


def _extract_family(model_name: str, provider: str) -> str:
    """Extract model family from name."""
    name_lower = model_name.lower()
    # Common family patterns
    families = {
        "llama": "llama", "phi": "phi", "gemma": "gemma", "granite": "granite",
        "falcon": "falcon", "mistral": "mistral", "qwen": "qwen", "yi": "yi",
        "starcoder": "starcoder", "olmo": "olmo", "dbrx": "dbrx", "arctic": "arctic",
        "flux": "flux", "stable-diffusion": "stable-diffusion", "nemotron": "nemotron",
        "nvlm": "nvlm", "jamba": "jamba", "command": "command", "aya": "aya",
        "cogvideo": "cogvideo", "glm": "glm", "baichuan": "baichuan", "rwkv": "rwkv",
        "bge": "bge", "e5": "e5", "nomic": "nomic", "jina": "jina",
        "moondream": "moondream", "hermes": "hermes", "cosmos": "cosmos",
        "florence": "florence", "orca": "orca", "codegen": "codegen",
        "blip": "blip", "xgen": "xgen",
    }
    for key, family in families.items():
        if key in name_lower:
            return family
    return provider


def _extract_date(hf_model: dict) -> str:
    """Extract release date from HF metadata."""
    created = hf_model.get("createdAt", "")
    if created:
        return created[:10]  # "2024-06-15T..." → "2024-06-15"
    return ""


def _extract_base_model(hf_model: dict) -> str:
    """Extract base model from HF tags."""
    tags = hf_model.get("tags", [])
    for tag in tags:
        if tag.startswith("base_model:"):
            return tag.split(":", 1)[1]
    return ""


def _build_modalities(hf_model: dict, model_type: ModelType) -> Modalities:
    """Build Modalities section from HF pipeline_tag and model_type."""
    pipeline = hf_model.get("pipeline_tag", "")

    inputs: list[Modality] = []
    outputs: list[Modality] = []

    if pipeline in ("text-generation", "text2text-generation", "fill-mask",
                     "feature-extraction", "sentence-similarity"):
        inputs.append(Modality.TEXT)
        outputs.append(Modality.TEXT)
    elif pipeline == "text-to-image":
        inputs.append(Modality.TEXT)
        outputs.append(Modality.IMAGE)
    elif pipeline == "image-to-image":
        inputs.extend([Modality.TEXT, Modality.IMAGE])
        outputs.append(Modality.IMAGE)
    elif pipeline == "image-text-to-text":
        inputs.extend([Modality.TEXT, Modality.IMAGE])
        outputs.append(Modality.TEXT)
    elif pipeline == "visual-question-answering":
        inputs.extend([Modality.TEXT, Modality.IMAGE])
        outputs.append(Modality.TEXT)
    elif pipeline == "text-to-video":
        inputs.append(Modality.TEXT)
        outputs.append(Modality.VIDEO)
    elif pipeline == "automatic-speech-recognition":
        inputs.append(Modality.AUDIO)
        outputs.append(Modality.TEXT)
    elif pipeline == "text-to-speech":
        inputs.append(Modality.TEXT)
        outputs.append(Modality.AUDIO)
    elif pipeline == "text-to-audio":
        inputs.append(Modality.TEXT)
        outputs.append(Modality.AUDIO)
    else:
        # Default for text models
        if model_type in (ModelType.LLM_CHAT, ModelType.LLM_REASONING, ModelType.LLM_CODE,
                           ModelType.LLM_BASE, ModelType.EMBEDDING_TEXT, ModelType.RERANKER,
                           ModelType.SAFETY_CLASSIFIER, ModelType.REWARD_MODEL):
            inputs.append(Modality.TEXT)
            outputs.append(Modality.TEXT)
        if model_type == ModelType.VLM:
            inputs.extend([Modality.TEXT, Modality.IMAGE])
            outputs.append(Modality.TEXT)

    text_detail = TextDetail()
    vision_detail = VisionDetail()
    embedding_detail = EmbeddingDetail()
    image_gen_detail = ImageGenDetail()
    audio_detail = AudioDetail()
    video_detail = VideoDetail()

    if model_type == ModelType.VLM:
        vision_detail.supported = True
    if model_type == ModelType.EMBEDDING_TEXT:
        embedding_detail.supported = True
    if model_type == ModelType.IMAGE_GENERATION:
        image_gen_detail.supported = True
    if model_type == ModelType.AUDIO_ASR:
        audio_detail.input_supported = True
    if model_type == ModelType.AUDIO_TTS:
        audio_detail.output_supported = True
    if model_type == ModelType.VIDEO_GENERATION:
        video_detail.output_supported = True

    return Modalities(
        input=inputs,
        output=outputs,
        text=text_detail,
        vision=vision_detail,
        embeddings=embedding_detail,
        image_generation=image_gen_detail,
        audio=audio_detail,
        video=video_detail,
    )


def _build_deployment(hf_model: dict, library: str) -> Deployment:
    """Build Deployment section from HF metadata."""
    runtimes = Runtimes()
    if library == "transformers":
        runtimes.transformers = True
    elif library == "diffusers":
        runtimes.transformers = True
    elif library == "gguf":
        runtimes.gguf = True
        runtimes.llama_cpp = True
        runtimes.ollama = True

    tags = [t.lower() for t in hf_model.get("tags", [])]
    if "gguf" in tags:
        runtimes.gguf = True
    if "mlx" in tags:
        runtimes.mlx = True
    if "vllm" in tags or "vllm" in library:
        runtimes.vllm = True

    return Deployment(
        local_inference=True,
        self_hostable=True,
        runtimes=runtimes,
    )


# ── YAML Writing ───────────────────────────────────────────────────

def write_card_yaml(card: ModelCard, output_dir: Path) -> Path:
    """Write a ModelCard to a YAML+Markdown file.

    Uses a custom YAML serialization that puts identity fields at the
    top level (matching from_yaml_file expectations).
    """
    provider = card.identity.provider
    provider_dir = output_dir / provider
    provider_dir.mkdir(parents=True, exist_ok=True)

    slug = slugify(card.identity.model_id.split("/", 1)[-1])
    filepath = provider_dir / f"{slug}.md"

    # Build the YAML data structure matching from_yaml_file expectations
    data: dict[str, Any] = {}

    # Identity fields go at top level
    identity_dict = card.identity.model_dump(exclude_none=False)
    # Convert enums to values
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
        # Convert enums
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
    return filepath


def _convert_enums(obj: Any) -> Any:
    """Recursively convert enum values in a dict/list."""
    if isinstance(obj, dict):
        return {k: _convert_enums(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_enums(item) for item in obj]
    elif hasattr(obj, "value"):
        return obj.value
    return obj


# ── Main Seeding Function ─────────────────────────────────────────

def seed_org(
    config: HFProviderConfig,
    output_dir: Path | None = None,
    validate: bool = True,
    verbose: bool = True,
) -> list[str]:
    """Seed model cards for a single HuggingFace organization.

    Returns list of created model IDs.
    """
    if output_dir is None:
        output_dir = MODELS_DIR

    if verbose:
        print(f"\n{'='*60}")
        print(f"  Seeding: {config.hf_org} → {config.provider_slug}/")
        print(f"{'='*60}")

    # Fetch models from HF
    hf_models = fetch_hf_models(config)
    if verbose:
        print(f"  Found {len(hf_models)} models on HuggingFace (min {config.min_downloads} downloads)")

    created = []
    errors = []
    skipped = []

    for hf_model in hf_models:
        hf_id = hf_model.get("id", hf_model.get("modelId", "unknown"))
        model_slug = slugify(hf_id)
        full_id = f"{config.provider_slug}/{slugify(hf_id.split('/')[-1])}"

        # Skip if card already exists
        existing = output_dir / config.provider_slug / f"{slugify(hf_id.split('/')[-1])}.md"
        if existing.exists():
            skipped.append(full_id)
            continue

        try:
            card = build_model_card(hf_model, config)
            filepath = write_card_yaml(card, output_dir)

            # Validate round-trip
            if validate:
                try:
                    loaded = ModelCard.from_yaml_file(filepath)
                    assert loaded.identity.model_id == card.identity.model_id
                except Exception as ve:
                    print(f"    WARNING: Validation failed for {full_id}: {ve}")
                    # Don't delete — keep the file but note the issue

            created.append(full_id)
        except Exception as e:
            errors.append((full_id, str(e)))
            if verbose:
                print(f"    ERROR: {full_id}: {e}")

    if verbose:
        print(f"  Created: {len(created)}, Skipped (existing): {len(skipped)}, Errors: {len(errors)}")
        if errors:
            for eid, err in errors[:5]:
                print(f"    - {eid}: {err}")

    return created


def seed_api_model(
    model_id: str,
    display_name: str,
    provider_slug: str,
    provider_display: str,
    country: str = "US",
    model_type: ModelType = ModelType.LLM_CHAT,
    cost_input: float | None = None,
    cost_output: float | None = None,
    context_window: int | None = None,
    max_output_tokens: int | None = None,
    params: int | None = None,
    license_type: LicenseType = LicenseType.PROPRIETARY,
    open_weights: bool = False,
    tags: list[str] | None = None,
    output_dir: Path | None = None,
) -> str | None:
    """Create a card for an API-only model (not on HuggingFace).

    Returns the model_id if created, None if already exists.
    """
    if output_dir is None:
        output_dir = MODELS_DIR

    slug = slugify(display_name)
    full_id = f"{provider_slug}/{slug}"
    filepath = output_dir / provider_slug / f"{slug}.md"

    if filepath.exists():
        return None

    card = ModelCard(
        identity=Identity(
            model_id=full_id,
            display_name=display_name,
            provider=provider_slug,
            provider_display=provider_display,
            status=ModelStatus.ACTIVE,
            model_type=model_type,
            tags=tags or [],
        ),
        architecture=Architecture(
            total_parameters=params,
        ),
        licensing=Licensing(
            open_weights=open_weights,
            license_type=license_type,
            origin_country=country,
        ),
        modalities=Modalities(
            text=TextDetail(
                context_window=context_window,
                max_output_tokens=max_output_tokens,
            ),
        ),
        cost=Cost(
            input=cost_input,
            output=cost_output,
        ),
        sources=Sources(),
        card_schema_version="3.0",
        card_author="api-model-seeder",
        card_created="2026-04-05",
        card_updated="2026-04-05",
        prose_body=f"# {display_name}\n\nAPI-only model from {provider_display}.",
    )

    (output_dir / provider_slug).mkdir(parents=True, exist_ok=True)
    write_card_yaml(card, output_dir)
    return full_id


# ── Standalone runner ──────────────────────────────────────────────

if __name__ == "__main__":
    print("HuggingFace Seeder Utility")
    print("Use seed_org() or import individual functions.")
    print(f"Models directory: {MODELS_DIR}")

    # Quick test: fetch meta-llama models
    test_config = HFProviderConfig(
        hf_org="meta-llama",
        provider_slug="meta",
        provider_display="Meta",
        country="US",
        limit=5,
        min_downloads=1000,
    )
    models = fetch_hf_models(test_config)
    print(f"\nTest fetch: {len(models)} models from meta-llama")
    for m in models[:3]:
        print(f"  - {m['id']}: {m.get('downloads', 0):,} downloads, pipeline={m.get('pipeline_tag', '?')}")
