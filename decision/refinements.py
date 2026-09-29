"""Refinement evidence states, shared by the vocabulary and the engine (MODEL-190).

The vocabulary publishes each refinement's state (MODEL-189); the engine ranks
on a refinement only when that same state is ``live`` or ``thin``. Both call
``evidence_state`` so the page never offers a key the engine refuses.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any, Literal

EvidenceState = Literal["live", "thin", "not_measured", "no_benchmark"]

RANKABLE: frozenset[str] = frozenset({"live", "thin"})
#: Lineup models with direct evidence a refinement needs to be live.
LIVE_DIRECT_MODELS = 3


def lineup(snapshot: Any) -> list[str]:
    """The candidates a state is counted over: every one not retired."""
    return [cid for cid in snapshot.candidates() if snapshot.lifecycle(cid) != "retired"]


def evidence_state(
    snapshot: Any,
    candidates: Sequence[str],
    benchmarks: Iterable[tuple[str, str]],
    eligible_classes: Iterable[str],
) -> tuple[EvidenceState, int, int]:
    """(state, measured models, eligible models) over ``candidates``.

    ``benchmarks`` are the refinement's (benchmark ID, directness) tags. A
    model is measured when any of its candidates has a verified row on one.
    """
    classes = set(eligible_classes)
    candidates_by_model: dict[str, list[str]] = {}
    for candidate in candidates:
        candidates_by_model.setdefault(snapshot.model_of(candidate), []).append(candidate)
    eligible = {
        model_id for model_id in candidates_by_model
        if snapshot.fact(model_id, "model.class").value in classes
    }
    tags = list(benchmarks)
    measured: set[str] = set()
    direct: set[str] = set()
    for benchmark_id, directness in tags:
        for model_id in eligible:
            if any(
                row.verified
                for candidate in candidates_by_model[model_id]
                for row in snapshot.evidence(candidate, benchmark_id)
            ):
                measured.add(model_id)
                if directness == "direct":
                    direct.add(model_id)
    if len(direct) >= LIVE_DIRECT_MODELS:
        state: EvidenceState = "live"
    elif measured:
        state = "thin"
    elif tags:
        state = "not_measured"
    else:
        state = "no_benchmark"
    return state, len(measured), len(eligible)


def is_refinement_key(dimension: str) -> bool:
    return "/" in dimension


def split_dimension(signed: str) -> tuple[str, str | None]:
    """A signed objective dimension as (signed parent, refinement or ``None``).

    ``-software_engineering/rust`` is ``("-software_engineering", "rust")``.
    Contract fields that carry a facet ID carry the parent; the refinement
    travels beside it.
    """
    parent, _, refinement = signed.partition("/")
    return parent, refinement or None
