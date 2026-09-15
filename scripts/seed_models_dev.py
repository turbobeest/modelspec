#!/usr/bin/env python3
"""Seed ModelSpec cards from the models.dev API.

Fetches https://models.dev/api.json, maps entries to ModelCard objects,
and writes YAML+Markdown model cards to the models/ directory.

Usage:
    source .venv/bin/activate && python scripts/seed_models_dev.py
"""

from __future__ import annotations

import contextlib
import os
import re
import sys
import tempfile
from pathlib import Path

import httpx
import yaml

# Ensure the project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.card_updates import StaleNotice, carry_guide_forward, write_notices  # noqa: E402

KNOWN_IDENTITIES_PATH = PROJECT_ROOT / "scripts" / "models_dev_known_identities.yaml"

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


MODELS_DEV_URL = "https://models.dev/api.json"


class SourceError(RuntimeError):
    """models.dev could not be read, or did not return what the seeder needs.

    Treated as fatal before anything is written. A broken source must never
    look like a quiet day with no new models.
    """


def check_payload(api_data: object) -> None:
    """Refuse a payload that is not the models.dev provider → models shape."""
    if not isinstance(api_data, dict):
        raise SourceError(f"expected a JSON object of providers, got {type(api_data).__name__}")
    present = [pid for pid in PROVIDER_MAP if pid in api_data]
    if not present:
        raise SourceError(
            f"none of the {len(PROVIDER_MAP)} mapped providers are in the payload "
            f"({len(api_data)} top-level keys)"
        )
    for provider_id in present:
        provider_data = api_data[provider_id]
        if not isinstance(provider_data, dict):
            raise SourceError(f"provider '{provider_id}' is not an object")
        raw_models = provider_data.get("models")
        if not isinstance(raw_models, dict):
            raise SourceError(f"provider '{provider_id}' has no 'models' object")
        for model_key, raw_model in raw_models.items():
            if not isinstance(raw_model, dict):
                raise SourceError(f"model '{provider_id}/{model_key}' is not an object")


def fetch_models_dev() -> dict:
    """Fetch and shape-check the models.dev payload, or raise SourceError."""
    try:
        resp = httpx.get(
            MODELS_DEV_URL,
            headers={"User-Agent": "ModelSpec-Seeder/1.0"},
            follow_redirects=True,
            timeout=60,
        )
        resp.raise_for_status()
        api_data = resp.json()
    except httpx.HTTPError as exc:
        raise SourceError(f"{type(exc).__name__}: {exc}") from exc
    except ValueError as exc:  # JSONDecodeError
        raise SourceError(f"response is not valid JSON: {exc}") from exc
    check_payload(api_data)
    return api_data


def write_card_atomically(file_path: Path, content: str) -> None:
    """Write via a sibling temp file and rename, so no reader ever sees half a card."""
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{file_path.name}.", suffix=".tmp", dir=file_path.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, file_path)
    except BaseException:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp_name)
        raise


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


def load_known_identities(path: Path | None = None) -> dict[str, str]:
    """Load the explicit models.dev → canonical catalogue mapping.

    Keys are models.dev ``provider/id`` strings and, when present, the seeder's
    ``slug/file-slug`` identity. Values are catalogue ``model_id``s. Display
    names never appear here.
    """
    path = path or KNOWN_IDENTITIES_PATH
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = raw.get("identities")
    if not isinstance(rows, list):
        raise ValueError(f"{path} has no identities list")
    mapping: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(f"{path} identity row is not a mapping: {row!r}")
        try:
            models_dev_id = row["models_dev"]
            canonical = row["canonical"]
        except KeyError as exc:
            raise ValueError(f"{path} identity row missing {exc}: {row!r}") from exc
        keys = [models_dev_id]
        seeder_id = row.get("seeder")
        if seeder_id:
            keys.append(seeder_id)
        for key in keys:
            previous = mapping.get(key)
            if previous and previous != canonical:
                raise ValueError(
                    f"conflicting identity {key}: {previous} vs {canonical}"
                )
            mapping[key] = canonical
    return mapping


def models_dev_identity(provider_id: str, raw: dict, model_key: str) -> str:
    """The models.dev identity: ``<provider>/<id>`` as published."""
    return f"{provider_id}/{raw.get('id', model_key)}"


def seeder_model_id(provider_cfg: dict, raw: dict, model_key: str) -> str:
    """The identity the seeder would mint: ``<provider-slug>/<file-slug>``."""
    return f"{provider_cfg['slug']}/{slugify(raw.get('id', model_key))}"


def seeder_file_path(
    models_dir: Path, provider_cfg: dict, raw: dict, model_key: str
) -> Path:
    return models_dir / provider_cfg["slug"] / f"{slugify(raw.get('id', model_key))}.md"


def canonical_card_path(models_dir: Path, canonical_id: str) -> Path:
    provider, sep, slug = canonical_id.partition("/")
    if not sep or not provider or not slug:
        raise ValueError(f"canonical id must be provider/slug, got {canonical_id!r}")
    return models_dir / provider / f"{slug}.md"


def already_held(
    *,
    models_dev_id: str,
    seeder_id: str,
    file_path: Path,
    models_dir: Path,
    known: dict[str, str],
    new_only: bool,
) -> str | None:
    """Return a skip reason if this models.dev row must not become a new card.

    ``known:<canonical>`` — explicit registry, and that card file exists.
    ``exists`` — ``--new-only`` and the seeder path is already a card.

    Display names are not an argument and are never consulted. A registry row
    whose canonical card is missing is ignored, so a typo cannot swallow a
    genuinely new model.
    """
    for key in (models_dev_id, seeder_id):
        canonical = known.get(key)
        if canonical and canonical_card_path(models_dir, canonical).is_file():
            return f"known:{canonical}"
    if new_only and file_path.exists():
        return "exists"
    return None


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
    if data.get("authoring_guide") is not None:
        out["authoring_guide"] = data.pop("authoring_guide")

    yaml_str = yaml.dump(
        dict(out),
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=120,
    )
    return f"---\n{yaml_str}---\n\n{card.prose_body}"


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--new-only", action="store_true",
        help="Only write cards that do not exist yet. Required for any scheduled run: "
             "without it this script overwrites every card, discarding curation.")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Report what would be written without writing anything.")
    parser.add_argument(
        "--stale-notices", type=Path, default=None,
        help="Write a PR-body snippet here when an overwrite marks an authoring "
             "guide stale because the card's version changed (MODEL-65).")
    args = parser.parse_args()

    print("Fetching models.dev API...")
    try:
        api_data = fetch_models_dev()
    except SourceError as exc:
        # Fail before writing anything, and never exit 0: a zero here would
        # read as "no new models today".
        print(f"ERROR: models.dev source is broken; no cards written: {exc}", file=sys.stderr)
        sys.exit(2)
    print(f"  Fetched {len(api_data)} providers from API")

    models_dir = PROJECT_ROOT / "models"
    known = load_known_identities()
    total_created = 0
    total_skipped_existing = 0
    total_skipped_known = 0
    total_errors = 0
    created_ids: list[str] = []
    total_completeness = 0.0
    seen_model_ids: set[str] = set()
    stale_notices: list[StaleNotice] = []

    for provider_id, provider_cfg in PROVIDER_MAP.items():
        if provider_id not in api_data:
            print(f"  SKIP: provider '{provider_id}' not found in API")
            continue

        provider_data = api_data[provider_id]
        raw_models = provider_data.get("models", {})
        provider_dir = models_dir / provider_cfg["slug"]
        if not args.dry_run:
            provider_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n  Processing {provider_cfg['display']} ({provider_id}): {len(raw_models)} models")

        for model_key, raw_model in raw_models.items():
            try:
                card = build_model_card(raw_model, provider_id, provider_cfg)

                # Skip duplicates (e.g. perplexity and perplexity-agent overlap)
                if card.identity.model_id in seen_model_ids:
                    continue
                seen_model_ids.add(card.identity.model_id)

                file_path = seeder_file_path(models_dir, provider_cfg, raw_model, model_key)
                md_id = models_dev_identity(provider_id, raw_model, model_key)
                seed_id = seeder_model_id(provider_cfg, raw_model, model_key)

                # A card that already exists may carry research this script
                # cannot reproduce — enrichment, hardware profiles, reviewed
                # evidence. Overwriting it silently discards that.
                # A models.dev row we already hold under another provider/slug
                # is the same model, not a new one (see models_dev_known_identities.yaml).
                held = already_held(
                    models_dev_id=md_id,
                    seeder_id=seed_id,
                    file_path=file_path,
                    models_dir=models_dir,
                    known=known,
                    new_only=args.new_only,
                )
                if held and held.startswith("known:"):
                    canonical = held.split(":", 1)[1]
                    total_skipped_known += 1
                    print(f"    SKIP {seed_id} (already {canonical})")
                    continue
                if held == "exists":
                    total_skipped_existing += 1
                    continue

                if args.dry_run:
                    print(f"    NEW {card.identity.model_id}")
                    created_ids.append(card.identity.model_id)
                    total_created += 1
                    continue

                # Validate by round-tripping BEFORE touching disk, then write
                # atomically: a card that does not parse, or a write that dies
                # halfway, must leave no file behind.
                # Overwriting an existing card (never under --new-only): keep its
                # authoring guide, and mark it stale if the version moved.
                notice = None
                if file_path.exists():
                    existing = ModelCard.from_yaml_file(file_path)
                    notice = carry_guide_forward(existing, card)
                content = card_to_yaml_clean(card)
                loaded = ModelCard.from_yaml_string(content)
                write_card_atomically(file_path, content)
                created_ids.append(card.identity.model_id)
                completeness = loaded.card_completeness
                total_completeness += completeness
                total_created += 1
                if notice is not None:
                    stale_notices.append(notice)
                    print(f"    STALE guide {notice.model_id}: {notice.old_version} -> {notice.new_version}")

                print(f"    OK  {card.identity.model_id:55s} ({completeness:5.1f}% complete)")

            except Exception as e:
                total_errors += 1
                print(f"    ERR {model_key}: {e}")

    if args.stale_notices is not None and not args.dry_run:
        write_notices(stale_notices, args.stale_notices)

    # Summary
    print("\n" + "=" * 70)
    print(f"SUMMARY")
    print(f"  Total cards created:     {total_created}")
    print(f"  Skipped, file exists:    {total_skipped_existing}")
    print(f"  Skipped, known identity: {total_skipped_known}")
    print(f"  Total errors:            {total_errors}")
    if total_created > 0:
        avg = total_completeness / total_created
        print(f"  Average completeness:    {avg:.1f}%")
    print(f"  Unique model IDs:        {len(seen_model_ids)}")
    print(f"  Output directory:        {models_dir}")
    print("=" * 70)
    if total_errors:
        print(f"ERROR: {total_errors} models.dev rows could not be carded", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


def _summary(created_ids: list[str], skipped: int, errors: int) -> str:
    """A run summary a workflow can paste into a pull request."""
    lines = [f"{len(created_ids)} new cards, {skipped} existing left untouched, {errors} errors"]
    for model_id in sorted(created_ids)[:50]:
        lines.append(f"- {model_id}")
    if len(created_ids) > 50:
        lines.append(f"- ...and {len(created_ids) - 50} more")
    return "\n".join(lines)
