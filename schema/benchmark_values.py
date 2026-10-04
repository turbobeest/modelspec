"""Validate stored benchmark values on the scale declared by their board."""
from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml

from decision.units import unit_id


_BOUNDED_UNITS = {"percent", "fraction", "0-1 scale", "accuracy", "f1 x100"}


def validate_value(score: Any, unit: str | None, metric: Mapping[str, Any]) -> None:
    if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score):
        raise ValueError("benchmark score must be a finite number")
    high = metric.get("max_score")
    low = metric.get("min_score")
    expected, actual = unit_id(metric.get("unit")), unit_id(unit)
    if expected == "p-mrr (x100)":
        low = max(-100, low) if low is not None else -100
        high = min(100, high) if high is not None else 100
    elif low is None and (expected in _BOUNDED_UNITS or high in (1, 100)):
        low = 0
    if low is not None and score < low or high is not None and score > high:
        raise ValueError("benchmark score is outside the board's declared range")
    # Older fraction boards left their dimensionless unit blank.
    if expected is None and high == 1:
        expected, actual = "fraction", actual or "fraction"
    if expected is not None and actual != expected:
        raise ValueError("benchmark unit differs from the board's declared scale")


def validate_rows(root: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    """Check a writer's complete batch before it changes a card.

    Unregistered boards have no declared metric to check. The catalogue and
    registry validators handle their identity separately.
    """
    metrics = {}
    for row in rows:
        benchmark = row["benchmark_id"]
        if benchmark not in metrics:
            path = root / "benchmarks" / f"{benchmark}.md"
            metrics[benchmark] = (
                (yaml.safe_load(path.read_text().split("---", 2)[1]) or {}).get("metric") or {}
                if path.is_file() else {}
            )
        validate_value(row["score"], row.get("unit"), metrics[benchmark])


def validate_card_rows(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    root = next((parent.parent for parent in path.parents if parent.name == "models"), None)
    if root is None:
        raise ValueError("benchmark writer requires a card under models/")
    validate_rows(root, rows)
