"""Shared helpers for automated writes to existing cards (MODEL-65).

An authoring guide is pinned to ``identity.version``. Any automated path that
changes the version of an existing card must go through
:func:`apply_version_change`, which marks a current guide ``stale`` in the same
change and returns a notice for the pull request body. Nothing is silent.

``scripts/seed_huggingface.py`` skips existing cards today; if it ever updates
one, it should call this helper too.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from schema.card import ModelCard

STALE_NOTICES_FILE = "stale-guides.md"


@dataclass(frozen=True)
class StaleNotice:
    model_id: str
    old_version: str
    new_version: str

    def to_markdown(self) -> str:
        return (
            f"- authoring guide for `{self.model_id}` is now stale "
            f"(version `{self.old_version}` → `{self.new_version}`): "
            "re-review against current provider guidance"
        )


def apply_version_change(card: ModelCard, new_version: str) -> StaleNotice | None:
    """Set ``identity.version``; mark a current guide stale if it really changed.

    Idempotent. An unchanged version is a no-op. A stale guide is never flipped
    back to current. Returns a notice only when a current guide went stale.
    """
    old_version = card.identity.version
    if new_version == old_version:
        return None
    card.identity.version = new_version
    guide = card.authoring_guide
    if guide is None or guide.status != "current":
        return None
    guide.status = "stale"
    return StaleNotice(card.identity.model_id, old_version, new_version)


def carry_guide_forward(existing: ModelCard, fresh: ModelCard) -> StaleNotice | None:
    """Keep ``existing``'s authoring guide on a regenerated ``fresh`` card.

    ``fresh`` carries the version the source reports now; the guide is moved
    across and the version change is applied through :func:`apply_version_change`.
    """
    if existing.authoring_guide is None:
        return None
    new_version = fresh.identity.version
    fresh.authoring_guide = existing.authoring_guide.model_copy(deep=True)
    fresh.identity.version = existing.identity.version
    return apply_version_change(fresh, new_version)


def render_notices(notices: list[StaleNotice]) -> str:
    if not notices:
        return ""
    lines = ["### Authoring guides now stale", ""]
    lines += [n.to_markdown() for n in notices]
    return "\n".join(lines) + "\n"


def write_notices(notices: list[StaleNotice], path: Path) -> None:
    """Write the PR-body snippet. No notices, no file."""
    if notices:
        path.write_text(render_notices(notices), encoding="utf-8")
