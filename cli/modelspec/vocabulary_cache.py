"""Read the decision vocabulary selected by the local cache."""

from __future__ import annotations

import json
from typing import Any

from . import snapshot


class VocabularyMissingError(ValueError):
    """No decision vocabulary has been cached."""


class VocabularyInvalidError(ValueError):
    """The selected decision vocabulary cannot be read."""


def load_cached_vocabulary() -> dict[str, Any]:
    """Return the selected vocabulary, distinguishing absence from corruption."""
    try:
        current = (
            snapshot.cache_dir() / snapshot.DECISION_DIRECTORY / "current"
        ).read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise VocabularyMissingError(
            "no cached decision vocabulary. Run `modelspec snapshot fetch`."
        ) from exc
    except (OSError, UnicodeError) as exc:
        raise VocabularyInvalidError(
            f"cannot read the cached decision vocabulary: {exc}"
        ) from exc
    if snapshot.DECISION_SNAPSHOT_ID.fullmatch(current) is None:
        raise VocabularyInvalidError(
            "cannot read the cached decision vocabulary: "
            "decision/current contains an invalid snapshot ID"
        )
    path = (
        snapshot.cache_dir() / snapshot.DECISION_DIRECTORY / current
        / snapshot.DECISION_VOCABULARY_FILENAME
    )
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise VocabularyMissingError(
            "no cached decision vocabulary. Run `modelspec snapshot fetch`."
        ) from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise VocabularyInvalidError(
            f"cannot read the cached decision vocabulary: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise VocabularyInvalidError("cached decision vocabulary is not a JSON object")
    return value
