"""The validator must treat only real cards as cards.

`models/` also holds prose (LICENSE.md). Validating that as a model card failed
CI on every pull request that touched it, which is a defect in the validator
rather than in the data.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_pr import is_model_card  # noqa: E402


def test_licence_prose_in_models_is_not_a_card() -> None:
    assert (REPO_ROOT / "models/LICENSE.md").is_file()
    assert is_model_card("models/LICENSE.md") is False


def test_a_real_card_is_a_card() -> None:
    assert is_model_card("models/anthropic/claude-haiku-4-5.md") is True


def test_missing_file_is_not_a_card() -> None:
    assert is_model_card("models/nope/does-not-exist.md") is False


def test_every_model_card_file_is_detected() -> None:
    """The models tree is cards plus a single licence file."""
    md = sorted(p for p in (REPO_ROOT / "models").rglob("*.md"))
    detected = [p for p in md if is_model_card(str(p.relative_to(REPO_ROOT)))]
    assert len(detected) == len(md) - 1
