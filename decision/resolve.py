"""Resolve a spec before filtering (MODEL-141, design §6.1).

Validate every facet against the registry, reject a free-text ``task``, and
place the inventory profile's standing rules in front of ``where``.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from decision.contract import (
    AllOf,
    AnyOf,
    Compare,
    EvidenceQualifiers,
    FacetLookup,
    InSet,
    InventoryProfile,
    Issue,
    NotOf,
    Spec,
    SpecError,
    check_facets,
)
from decision.registry import facet as registry_facet


@dataclass(frozen=True)
class Resolved:
    """A spec that has passed the registry, with profile rules already in front."""

    spec: Spec
    profile: InventoryProfile | None
    conditions: tuple[Any, ...]
    include_retired: bool
    facets: FacetLookup
    objective_qualifiers: Mapping[str, EvidenceQualifiers]


_TASK_REASON = (
    "free-text task is not yet in slice 1; send task_type and capabilities instead"
)


def _is_lifecycle(facet_id: str) -> bool:
    return facet_id == "lifecycle" or facet_id.endswith(".lifecycle")


def asks_for_retired(cond: Any) -> bool:
    """True when a condition admits retired models into the lineup."""
    if isinstance(cond, AnyOf | AllOf):
        children = cond.any if isinstance(cond, AnyOf) else cond.all
        return any(asks_for_retired(child) for child in children)
    if isinstance(cond, NotOf):
        return False
    if isinstance(cond, InSet) and cond.in_ is not None and _is_lifecycle(cond.facet):
        return any(value == "retired" for value in cond.in_)
    if isinstance(cond, Compare) and cond.op == "=" and _is_lifecycle(cond.facet):
        return cond.value == "retired"
    return False


def _loaded_profile(
    spec: Spec, profiles: Mapping[str, InventoryProfile] | None,
) -> InventoryProfile | None:
    if spec.profile is None:
        return None
    if isinstance(spec.profile, InventoryProfile):
        return spec.profile
    found = None if profiles is None else profiles.get(spec.profile)
    if not isinstance(found, InventoryProfile):
        raise SpecError([Issue(
            None, "profile",
            f"profile {spec.profile} is not loaded; write it inline or pass it to resolve",
            "profile",
        )])
    return found


def resolve(
    spec: Spec,
    *,
    facets: FacetLookup | None = None,
    profiles: Mapping[str, InventoryProfile] | None = None,
) -> Resolved:
    """Validate ``spec`` and return the condition list the filter runs, rules first."""
    lookup = facets if facets is not None else registry_facet
    issues = check_facets(spec, lookup)
    profile = _loaded_profile(spec, profiles)
    if profile is not None and not isinstance(spec.profile, InventoryProfile):
        shadow = spec.model_copy(update={"profile": profile})
        issues.extend(
            issue for issue in check_facets(shadow, lookup)
            if issue.path.startswith("profile.rules")
        )
    if spec.task is not None:
        issues.append(Issue(None, "task", _TASK_REASON, "task"))
    if issues:
        raise SpecError(issues)
    rules = () if profile is None else tuple(profile.rules)
    conditions = rules + tuple(spec.where)
    return Resolved(
        spec=spec,
        profile=profile,
        conditions=conditions,
        include_retired=any(asks_for_retired(cond) for cond in conditions),
        facets=lookup,
        objective_qualifiers=spec.optimize.qualifiers,
    )
