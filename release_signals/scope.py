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
    "mask-generation",
    "video-classification",
    "keypoint-detection",
    "unconditional-image-generation",
    "text-to-audio",
    "audio-to-audio",
    "audio-classification",
    "voice-activity-detection",
})

# An out-of-scope pipeline tag is filed when the row also carries one of these.
_TASK_TAGS_THAT_KEEP = frozenset({
    "text-generation",
    "image-text-to-text",
    "any-to-any",
    "audio-text-to-text",
    "feature-extraction",
    "sentence-similarity",
    "text-ranking",
})

# Whole tags for an interpretability tool. Matched after `_artefact_key`.
_ARTEFACT_TAGS = frozenset({
    "interpretability",
    "mechanistic-interpretability",
    "transcoder",
    "cross-layer-transcoder",
    "sparse-autoencoder",
    "sparse-autoencoders",
    "sae",
    "saelens",
    "sae-lens",
    "crosscoder",
})


def _folded(value: str) -> str:
    return value.strip().casefold()


def _artefact_key(value: str) -> str:
    """The existing fold, then an underscore is the same mark as a hyphen."""
    return _folded(value).replace("_", "-")


def out_of_scope_pipeline_tag(tag: str) -> bool:
    folded = _folded(tag)
    if folded == "audio-text-to-text":
        return False
    return folded in OUT_OF_SCOPE_PIPELINE_TAGS or folded.startswith("audio-")


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


def _listed_bases(base_model: str | Sequence[str] | None) -> list[str]:
    if base_model is None:
        return []
    raw: Sequence[object] = (base_model,) if isinstance(base_model, str) else base_model
    found: list[str] = []
    for item in raw:
        one = repository_id(item)
        if one and one not in found:
            found.append(one)
    return found


def _named_after(repository_name: str, base_name: str) -> bool:
    """`<base-name>` or `<base-name>-<suffix>`, after the same normalisation as names."""
    repo = normalise(repository_name)
    base = normalise(base_name)
    if not repo or not base:
        return False
    return repo == base or repo.startswith(f"{base}-")


def derivative_reason(
    repository: str, base_model: str | Sequence[str] | None,
) -> str | None:
    """An artefact named after another organisation's model.

    Reject only when no listed base is in this repository's organisation and
    the repository name is that other model's name plus a suffix. A fine-tune
    with its own name, or a model that also lists its own base, is filed.
    A malformed base is ignored. The recorded base is unchanged either way.
    """
    repo = repository_id(repository)
    if repo is None:
        return None
    owner, _, name = repo.partition("/")
    bases = _listed_bases(base_model)
    if not bases:
        return None
    own = owner.casefold()
    if any(item.partition("/")[0].casefold() == own for item in bases):
        return None
    for item in bases:
        if _named_after(name, item.partition("/")[2]):
            return f"derivative of {item}"
    return None


def _keeping_task_tag(tags: Sequence[str]) -> str | None:
    for tag in tags:
        text = _text(tag)
        if text and _folded(text) in _TASK_TAGS_THAT_KEEP:
            return text
    return None


def _generation_or_multimodal_task_tag(tags: Sequence[str]) -> str | None:
    """A generation or multimodal member of `_TASK_TAGS_THAT_KEEP`, after `_folded`.

    That set also holds feature-extraction, sentence-similarity and
    text-ranking so an out-of-scope pipeline tag can still be filed. Those
    three do not skip artefact rejection when the pipeline tag is missing.
    """
    not_generation = ("feature-extraction", "sentence-similarity", "text-ranking")
    for tag in tags:
        text = _text(tag)
        if text is None:
            continue
        folded = _folded(text)
        if folded in _TASK_TAGS_THAT_KEEP and folded not in not_generation:
            return text
    return None


def _artefact_tag(tags: Sequence[str]) -> str | None:
    for tag in tags:
        text = _text(tag)
        if text and _artefact_key(text) in _ARTEFACT_TAGS:
            return text
    return None


def tag_scope(pipeline_tag: str | None, tags: Sequence[str] = ()) -> TagDecision:
    """Scope from the pipeline tag. With none, the name rules decide.

    An interpretability artefact tag is out of scope when the pipeline tag is
    feature-extraction. It is also out of scope when the pipeline tag is
    absent, unless a generation or multimodal member of `_TASK_TAGS_THAT_KEEP`
    is present. That case falls through, so the result matches a missing
    pipeline from before this check. feature-extraction is the stated task, so
    a generation tag beside it does not keep the repository. Any other
    pipeline tag leaves the row in scope.

    An unknown pipeline tag is in scope. The reason for an out-of-scope tag is
    the tag itself. An out-of-scope pipeline tag is filed when the tag list
    also names an in-scope task. With no pipeline tag, a free-form tag rejects
    only when it is out of scope and no in-scope task tag is present.
    """
    primary = _text(pipeline_tag) or ""
    artefact = _artefact_tag(tags)
    stated_feature_extraction = _artefact_key(primary) == "feature-extraction"
    if artefact is not None and (not primary or stated_feature_extraction):
        if stated_feature_extraction or _generation_or_multimodal_task_tag(tags) is None:
            return TagDecision(
                True, f"interpretability artefact (tag: {artefact})", artefact,
            )
    if primary:
        if out_of_scope_pipeline_tag(primary):
            keeper = _keeping_task_tag(tags)
            if keeper:
                return TagDecision(True, None, keeper)
            return TagDecision(True, primary, primary)
        return TagDecision(True, None, primary)
    if _keeping_task_tag(tags) is None:
        for tag in tags:
            text = _text(tag)
            if text and out_of_scope_pipeline_tag(text):
                return TagDecision(True, text, text)
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
    """Library, base-model tags, task tags, and interpretability artefact tags.

    Licence and language tags stay off.
    """
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
        if (
            text.startswith("base_model:")
            or known_pipeline_tag(text)
            or _folded(text) == declared
            or _artefact_key(text) in _ARTEFACT_TAGS
        ):
            add(text)
    return tuple(kept)


def hub_metadata(
    row: Mapping[str, Any], repository: str,
) -> tuple[str | None, tuple[str, ...], str | None, tuple[str, ...]]:
    """`pipeline_tag`, the tags that matter, the recorded base, and every base.

    The organisation listing already carries these. `cardData` is read when the
    row includes it and is not requested on its own. The recorded base prefers
    another organisation; the full list is what the derivative rule reads.
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
    listed = tuple(dict.fromkeys(bases))
    return pipeline_tag, tags, reported_base_model(repository, listed), listed
