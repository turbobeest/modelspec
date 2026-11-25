"""The one reading of a card row's observation date, shared by the freshness layer
(``scripts.accuracy``) and the leaderboard refresh's stale-row report."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, datetime
from typing import Any


def day(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


def observation_metadata_date(record: Mapping[str, Any]) -> date | None:
    """Return a source observation date, never an evaluation/publication date."""
    containers = [record]
    source_snapshot = record.get("source_snapshot")
    if isinstance(source_snapshot, Mapping):
        containers.append(source_snapshot)
    sources = record.get("sources")
    if isinstance(sources, Sequence) and not isinstance(sources, (str, bytes)):
        containers.extend(source for source in sources if isinstance(source, Mapping))
    for key in ("observed_at", "retrieved_at"):
        for container in containers:
            if (value := day(container.get(key))) is not None:
                return value
    return day(record.get("verified_at"))
