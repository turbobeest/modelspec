"""Decide whether a release signal names work this catalogue does not rank."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from scripts.attribution import normalise

_IMAGE_TOKEN_EXCEPTIONS = frozenset({
    "vl",
    "vlm",
    "vision",
    "omni",
    "multimodal",
    "embed",
    "embedding",
    "embeddings",
    "captioning",
    "clip",
    "text",
})

_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"(?<![a-z0-9])(?:robotics|embodied)(?![a-z0-9])"),
        "robotics or embodied checkpoint",
    ),
    (
        re.compile(
            r"(?<![a-z0-9])(?:text-to-image|image-generation|imagen|dall-e|"
            r"stable-diffusion|sdxl|flux|gpt-image|nano-banana)(?![a-z0-9])"
        ),
        "image generation",
    ),
    (
        re.compile(r"(?<![a-z0-9])imagine(?![a-z0-9])"),
        "image or video generation",
    ),
    (
        re.compile(
            r"(?<![a-z0-9])(?:text-to-video|video-generation|veo|sora)(?![a-z0-9])"
        ),
        "video generation",
    ),
    (
        re.compile(r"(?<![a-z0-9])(?:transcribe|tts|voice)(?![a-z0-9])"),
        "speech",
    ),
    (
        re.compile(r"(?<![a-z0-9])ocr(?![a-z0-9])"),
        "ocr",
    ),
    (
        re.compile(
            r"(?<![a-z0-9])(?:time-series|timeseries|timestral)(?![a-z0-9])"
        ),
        "time series",
    ),
    (
        re.compile(r"(?<![a-z0-9])anomaly-detection(?![a-z0-9])"),
        "anomaly detection",
    ),
    (
        re.compile(r"(?<![a-z0-9])(?:checkpoint-\d+|sdg-export|sae)(?![a-z0-9])"),
        "training or dataset artefact",
    ),
)


def out_of_scope_reason(provider: str, model_name: str) -> str | None:
    """Why this signal is out of scope, or None when it stays in scope.

    Rules match the normalised model name. The provider string is not a scope
    signal, so a lab named Voice AI keeps its language models.
    """
    del provider
    name = normalise(model_name)
    if not name:
        return None
    tokens = set(name.split("-"))
    if "image" in tokens and tokens.isdisjoint(_IMAGE_TOKEN_EXCEPTIONS):
        return "image generation"
    for pattern, reason in _RULES:
        if pattern.search(name):
            return reason
    return None


# Hugging Face pipeline tags the catalogue ranks. An unknown tag stays in scope.
IN_SCOPE_PIPELINE_TAGS = frozenset({
    "text-generation",
    "text2text-generation",
    "feature-extraction",
    "sentence-similarity",
    "text-ranking",
    "image-text-to-text",
    "visual-question-answering",
    "any-to-any",
    "conversational",
    "video-text-to-text",
})

# Single-task vision, audio, robotics, reinforcement learning and generation
# tags. `audio-` is the prefix form of the audio class.
OUT_OF_SCOPE_PIPELINE_TAGS = frozenset({
    "robotics",
    "reinforcement-learning",
    "text-to-image",
    "image-to-image",
    "text-to-video",
    "image-to-video",
    "text-to-speech",
    "automatic-speech-recognition",
    "time-series-forecasting",
    "image-classification",
    "object-detection",
    "image-segmentation",
    "depth-estimation",
    "zero-shot-object-detection",
    "zero-shot-image-classification",
    "mask-generation",
    "video-classification",
    "keypoint-detection",
    "unconditional-image-generation",
    "image-feature-extraction",
    "text-to-audio",
    "audio-to-audio",
    "audio-classification",
    "voice-activity-detection",
})


def _folded(value: str) -> str:
    return value.strip().casefold()


def out_of_scope_pipeline_tag(tag: str) -> bool:
    folded = _folded(tag)
    return (
        folded in OUT_OF_SCOPE_PIPELINE_TAGS
        or folded == "audio"
        or folded.startswith("audio-")
    )


def in_scope_pipeline_tag(tag: str) -> bool:
    return _folded(tag) in IN_SCOPE_PIPELINE_TAGS


def known_pipeline_tag(tag: str) -> bool:
    return in_scope_pipeline_tag(tag) or out_of_scope_pipeline_tag(tag)


@dataclass(frozen=True)
class TagDecision:
    """`decided` is false when the name rules still have to run."""

    decided: bool
    reason: str | None = None
    tag: str | None = None


def derivative_reason(repository_id: str, base_model: str | None) -> str | None:
    """A fine-tune of another organisation's repository is not this lab's release.

    The same organisation, including a case difference, is this lab's own base.
    """
    if not base_model or "/" not in base_model or "/" not in repository_id:
        return None
    owner, _, _name = repository_id.partition("/")
    base_owner, _, base_name = base_model.partition("/")
    if not owner or not base_owner or not base_name:
        return None
    if owner.casefold() == base_owner.casefold():
        return None
    return f"derivative of {base_owner}/{base_name}"


def tag_scope(pipeline_tag: str | None, tags: Sequence[str] = ()) -> TagDecision:
    """Scope from the pipeline tag, then from task tags. No tag stays undecided.

    An unknown pipeline tag is in scope. The reason for an out-of-scope tag is
    the tag itself. A set pipeline tag wins over the other tags.
    """
    primary = _text(pipeline_tag) or ""
    if primary:
        if out_of_scope_pipeline_tag(primary):
            return TagDecision(True, primary, primary)
        return TagDecision(True, None, primary)
    for tag in tags:
        text = _text(tag)
        if text and out_of_scope_pipeline_tag(text):
            return TagDecision(True, text, text)
    for tag in tags:
        text = _text(tag)
        if text and in_scope_pipeline_tag(text):
            return TagDecision(True, None, text)
    return TagDecision(False)


def _text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def repository_id(value: object) -> str | None:
    """One `org/repo` id from a card value or the body of a `base_model:` tag."""
    if isinstance(value, dict):
        for key in ("id", "model", "repo", "modelId"):
            found = repository_id(value.get(key))
            if found:
                return found
        return None
    text = _text(value)
    if text is None:
        return None
    for part in text.split(":"):
        piece = part.strip()
        if piece.count("/") != 1 or " " in piece:
            continue
        owner, _, name = piece.partition("/")
        if owner and name:
            return f"{owner}/{name}"
    return None


def _repository_ids(value: object) -> list[str]:
    if isinstance(value, list):
        found = []
        for item in value:
            found.extend(_repository_ids(item))
        return found
    one = repository_id(value)
    return [one] if one else []


def reported_base_model(repository: str, candidates: Sequence[str]) -> str | None:
    """The base to record. Another organisation wins over this repository's own."""
    unique: list[str] = []
    for item in candidates:
        if item and item not in unique:
            unique.append(item)
    if not unique:
        return None
    owner = repository.partition("/")[0].casefold()
    for item in unique:
        if item.partition("/")[0].casefold() != owner:
            return item
    return unique[0]


def relevant_hub_tags(
    tags: object, library_name: object, pipeline_tag: str | None,
) -> tuple[str, ...]:
    """Library, `base_model:*` tags, and task tags. Licence and language tags stay off."""
    kept: list[str] = []

    def add(value: str) -> None:
        if value not in kept:
            kept.append(value)

    library = _text(library_name)
    if library:
        add(library)
    if not isinstance(tags, list):
        return tuple(kept)
    declared = _folded(pipeline_tag) if pipeline_tag else ""
    for tag in tags:
        text = _text(tag)
        if text is None:
            continue
        if text.startswith("base_model:") or known_pipeline_tag(text) or _folded(text) == declared:
            add(text)
    return tuple(kept)


def hub_metadata(
    row: Mapping[str, Any], repository: str,
) -> tuple[str | None, tuple[str, ...], str | None]:
    """`pipeline_tag`, the tags that matter, and `base_model` from one listing row.

    The organisation listing already carries these. `cardData` is read when the
    row includes it and is not requested on its own.
    """
    pipeline_tag = _text(row.get("pipeline_tag"))
    tags = relevant_hub_tags(row.get("tags"), row.get("library_name"), pipeline_tag)
    bases: list[str] = []
    card = row.get("cardData")
    if isinstance(card, dict) and "base_model" in card:
        bases.extend(_repository_ids(card.get("base_model")))
    if isinstance(row.get("tags"), list):
        for tag in row["tags"]:
            text = _text(tag)
            if text and text.startswith("base_model:"):
                bases.extend(_repository_ids(text.split(":", 1)[1]))
    return pipeline_tag, tags, reported_base_model(repository, bases)
