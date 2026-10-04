"""Snapshot scope and unsupported requirements, shared by every decide client."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from api.classes import CLASS_BY_ID
from decision.contract import (
    AllOf, AnyOf, Compare, CoverageRefusal, InSet, InventoryProfile, NotOf, Spec,
)

COVERAGE_URL = "https://modelspec.dev/api/coverage.json"


def lineup(snapshot: Any) -> list[str]:
    return [cid for cid in snapshot.candidates() if snapshot.lifecycle(cid) != "retired"]


def class_counts(snapshot: Any) -> dict[str, int]:
    """Count models once, excluding offerings and the retired archive."""
    counts: Counter[str] = Counter()
    for cid in lineup(snapshot):
        if snapshot.kind(cid) == "model":
            value = snapshot.fact(cid, "model.class")
            if value.state == "known" and value.value in CLASS_BY_ID:
                counts[value.value] += 1
    return {class_id: counts[class_id] for class_id in sorted(CLASS_BY_ID)}


def estimate_models(snapshot: Any, domain_id: str) -> int:
    """Distinct active models with a stored estimate, counted once across offerings."""
    return len({snapshot.model_of(cid) for cid in lineup(snapshot)
                if snapshot.capability_estimate(cid, domain_id) is not None})


def _class_match(condition: Any, class_id: str) -> bool | None:
    if getattr(condition, "soft", None) is not None:
        return None
    if isinstance(condition, AnyOf | AllOf):
        values = [_class_match(child, class_id) for child in
                  (condition.any if isinstance(condition, AnyOf) else condition.all)]
        decisive = True if isinstance(condition, AnyOf) else False
        if decisive in values:
            return decisive
        return None if None in values else not decisive
    if isinstance(condition, NotOf):
        value = _class_match(condition.not_, class_id)
        return None if value is None else not value
    if getattr(condition, "facet", None) != "model.class":
        return None
    if isinstance(condition, Compare) and isinstance(condition.value, str):
        if condition.op == "=":
            return class_id == condition.value
        if condition.op == "!=":
            return class_id != condition.value
    if isinstance(condition, InSet):
        return (class_id in condition.in_ if condition.in_ is not None
                else class_id not in condition.not_in)
    return None


def _leaves(conditions: Iterable[Any]):
    for condition in conditions:
        if isinstance(condition, AnyOf | AllOf):
            yield from _leaves(condition.any if isinstance(condition, AnyOf) else condition.all)
        elif isinstance(condition, NotOf):
            yield from _leaves([condition.not_])
        else:
            yield condition


def _named_classes(conditions: Iterable[Any]) -> set[str]:
    names: set[str] = set()
    for condition in _leaves(conditions):
        if getattr(condition, "facet", None) == "model.class":
            if isinstance(condition, Compare) and isinstance(condition.value, str):
                names.add(condition.value)
            elif isinstance(condition, InSet):
                names.update(condition.in_ or condition.not_in or ())
    return names


def _domain_names(spec: Spec, conditions: Iterable[Any]) -> set[str]:
    from decision.registry import default

    registered = {domain.id for domain in default().domains()}
    objective = spec.optimize
    dimensions = [objective.min, objective.max]
    dimensions += list(objective.weights or objective.pareto or ())
    dimensions += [step.facet for step in objective.lexicographic or ()]
    dimensions += [getattr(condition, "facet", getattr(condition, "known", None))
                   for condition in _leaves(conditions)]
    return set(spec.capabilities or {}) | {
        name.removeprefix("-").split("/", 1)[0] for name in dimensions if name
        and name.removeprefix("-").split("/", 1)[0] in registered
    }


def for_spec(spec: Spec, snapshot: Any, *, conditions: Iterable[Any] | None = None,
             ) -> CoverageRefusal | None:
    """Describe missing scope without changing the Spec, filtering, or ranking."""
    rules = list(conditions) if conditions is not None else list(spec.where)
    if conditions is None and isinstance(spec.profile, InventoryProfile):
        rules = list(spec.profile.rules) + rules
    requested = _named_classes(rules)
    domains = _domain_names(spec, rules)
    if not requested and not domains:
        return None
    counts = class_counts(snapshot)
    available = {class_id for class_id, count in counts.items() if count}
    # Only a hard class constraint can exclude scope. An unrelated arm of an
    # OR, or a soft preference, cannot turn a usable board into a refusal.
    gates = [rule for rule in rules if getattr(rule, "soft", None) is None]
    missing_classes = sorted(requested - available) if requested and not any(
        all(_class_match(rule, class_id) is not False for rule in gates)
        for class_id in available
    ) else []
    domain_ids = set(snapshot.domain_ids())
    missing_domains = sorted(domain for domain in domains
                             if domain not in domain_ids or not estimate_models(snapshot, domain))
    if not missing_classes and not missing_domains:
        return None
    covered_domains = {domain for domain in domain_ids if estimate_models(snapshot, domain)}
    covered = [{"id": class_id, "models": count} for class_id, count in counts.items() if count]
    scope = ", ".join(f"{row['id']} ({row['models']} models)" for row in covered) or "no classes"
    wanted = ", ".join(missing_classes + missing_domains)
    as_of = getattr(snapshot, "as_of", None)
    return CoverageRefusal(
        message=f"The decision board cannot decide {wanted} from this snapshot. "
                f"Covered classes: {scope}. Catalogue presence is not decision coverage.",
        snapshot=snapshot.snapshot_id,
        as_of=as_of.isoformat() if as_of else None,
        classes=covered,
        domains=sorted(covered_domains),
        requested_classes=missing_classes,
        requested_domains=missing_domains,
    )
