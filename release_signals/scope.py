"""Decide whether a release signal names work this catalogue does not rank."""

from __future__ import annotations

import re

_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"(?<![a-z0-9])(?:robotics|embodied)(?![a-z0-9])"),
        "robotics or embodied checkpoint",
    ),
    (
        re.compile(
            r"(?<![a-z0-9])(?:text-to-image|image-generation|imagen|dall-e|"
            r"stable-diffusion|sdxl)(?![a-z0-9])"
        ),
        "image generation",
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
        re.compile(r"(?<![a-z0-9])(?:time-series|timeseries)(?![a-z0-9])"),
        "time series",
    ),
    (
        re.compile(r"(?<![a-z0-9])(?:checkpoint-\d+|sdg-export|sae)(?![a-z0-9])"),
        "training or dataset artefact",
    ),
)


def out_of_scope_reason(provider: str, model_name: str) -> str | None:
    """Why this signal is out of scope, or None when it stays in scope.

    A name that does not match one of these tokens is in scope.
    """
    text = f"{provider}\n{model_name}".casefold()
    for pattern, reason in _RULES:
        if pattern.search(text):
            return reason
    return None
