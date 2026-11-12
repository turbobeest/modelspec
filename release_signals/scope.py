"""Decide whether a release signal names work this catalogue does not rank."""

from __future__ import annotations

import re

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
