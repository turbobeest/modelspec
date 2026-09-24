"""Resolve a spec before filtering (MODEL-141, design §6.1).

Validate every facet against the registry, reject a free-text ``task``, and
place the inventory profile's standing rules in front of ``where``. The facet
registry is MODEL-133. Until it is merged, :func:`stub_facet` answers the
facets the contract examples use and rejects every other id.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

from decision.contract import (
    AllOf,
    AnyOf,
    Compare,
    FacetLookup,
    InSet,
    InventoryProfile,
    Issue,
    NotOf,
    Spec,
    SpecError,
    check_facets,
)

Risk = Literal["capability", "governance"]


@dataclass(frozen=True)
class FacetView:
    """The facet fields the filter needs. ``value_type`` is the registry kind."""

    id: str
    value_type: str
    tier: str
    risk: Risk
    subject: str


@dataclass(frozen=True)
class Resolved:
    """A spec that has passed the registry, with profile rules already in front."""

    spec: Spec
    profile: InventoryProfile | None
    conditions: tuple[Any, ...]
    include_retired: bool
    facets: FacetLookup


# Kind, tier, risk, subject. Not a score, and not a benchmark weight.
_STUB_ROWS: dict[str, tuple[str, str, Risk, str]] = {
    "input_price": ("number", "guaranteed", "capability", "offering"),
    "context_window": ("integer", "guaranteed", "capability", "model"),
    "swe_bench_pro": ("number", "best_effort", "capability", "evidence"),
    "coding": ("number", "guaranteed", "capability", "model"),
    "cost_per_task": ("number", "best_effort", "capability", "model"),
    "output_tps": ("number", "best_effort", "capability", "offering"),
    "offered_on": ("string", "guaranteed", "capability", "offering"),
    "deployment": ("enum", "guaranteed", "capability", "model"),
    "license": ("enum", "guaranteed", "governance", "model"),
    "origin.lab_country": ("enum", "guaranteed", "governance", "model"),
    "data.trains_on_customer_data": ("bool", "guaranteed", "governance", "offering"),
    "license.commercial_use": ("bool", "guaranteed", "governance", "model"),
    "parameters.total": ("integer", "best_effort", "capability", "model"),
    "release_date": ("date", "guaranteed", "capability", "model"),
    "model.lifecycle": ("enum", "guaranteed", "capability", "model"),
    "lifecycle": ("enum", "guaranteed", "capability", "model"),
}

_STUB: dict[str, FacetView] = {
    facet_id: FacetView(facet_id, kind, tier, risk, subject)
    for facet_id, (kind, tier, risk, subject) in _STUB_ROWS.items()
}

_TASK_REASON = (
    "free-text task is not yet in slice 1; send task_type and capabilities instead"
)


def stub_facet(facet_id: str) -> FacetView:
    """Registry stand-in. Raises ``KeyError`` for an id it does not hold."""
    try:
        return _STUB[facet_id]
    except KeyError:
        raise KeyError(facet_id) from None


def load_facet_lookup() -> FacetLookup:
    """``decision.registry.facet`` when MODEL-133 is importable, else :func:`stub_facet`."""
    try:
        from decision.registry import facet as registry_facet
    except ImportError:
        return stub_facet
    return registry_facet


def _view(facet_id: str, info: Any) -> FacetView:
    if isinstance(info, FacetView):
        return info
    raw_type = getattr(info, "value_type", None)
    kind = raw_type if isinstance(raw_type, str) else getattr(raw_type, "kind", None)
    if not isinstance(kind, str):
        raise SpecError([Issue(None, facet_id, f"{facet_id} has no value type", facet_id)])
    risk = getattr(info, "risk", None)
    if risk not in ("capability", "governance"):
        raise SpecError([Issue(
            None, facet_id,
            f"{facet_id} has no risk direction (capability or governance)", facet_id,
        )])
    subject = getattr(info, "subject", None) or "model"
    tier = getattr(info, "tier", "") or ""
    return FacetView(getattr(info, "id", facet_id), kind, str(tier), risk, str(subject))


def _lookup(raw: FacetLookup) -> FacetLookup:
    def lookup(facet_id: str) -> FacetView:
        try:
            info = raw(facet_id)
        except KeyError:
            raise KeyError(facet_id) from None
        return _view(facet_id, info)

    return lookup


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
    lookup = _lookup(facets if facets is not None else load_facet_lookup())
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
    )
