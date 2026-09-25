"""What to relax when nothing qualifies, without changing the question (MODEL-153).

A relaxation must keep the question the same question. Dropping the class
(`model.class = text-generator`) or a condition on a requested capability
domain answers a different one: recall Q10, a chat model under $0.20 per
million input tokens, was told to drop its class because the one model under
the cap was a decider. Those conditions are never suggested.

`relax` names the fewest other hard conditions whose removal gives a feasible
answer, preferring numeric caps and floors among equally few. `relax_to` states,
for each numeric cap or floor, the smallest change that admits a model: the
threshold moved to the nearest value an excluded candidate has.
"""

from __future__ import annotations

from dataclasses import replace
from itertools import combinations
from typing import Any

from decision.contract import AllOf, AnyOf, Compare, NotOf, Relaxation, render_condition
from decision.explain import facet_unit
from decision.filter import apply

#: Facets that say what kind of model the question is about.
QUESTION_FACETS = frozenset({"model.class"})
#: A cap or floor, and the inclusive direction it relaxes in.
_LOOSENS = {"<": "<=", "<=": "<=", ">": ">=", ">=": ">="}


def _leaves(cond: Any):
    if isinstance(cond, AnyOf | AllOf):
        for child in cond.any if isinstance(cond, AnyOf) else cond.all:
            yield from _leaves(child)
    elif isinstance(cond, NotOf):
        yield from _leaves(cond.not_)
    else:
        yield cond


def _changes_the_question(cond: Any, domains: frozenset[str]) -> bool:
    return any(
        getattr(leaf, "facet", None) in QUESTION_FACETS | domains for leaf in _leaves(cond)
    )


def _numeric(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _cap_or_floor(cond: Any) -> bool:
    return isinstance(cond, Compare) and cond.op in _LOOSENS and _numeric(cond.value)


def _relaxable(resolved, domains: frozenset[str]) -> list[int]:
    return [
        i for i, cond in enumerate(resolved.conditions)
        if cond.soft is None and not _changes_the_question(cond, domains)
    ]


def fewest(resolved, snapshot, domains: frozenset[str]) -> list[str]:
    """The fewest relaxable conditions whose removal gives a feasible answer."""
    conditions = resolved.conditions
    hard = _relaxable(resolved, domains)
    for size in range(1, len(hard) + 1):
        # Stable: caps and floors first, then the spec's order.
        groups = sorted(
            combinations(hard, size),
            key=lambda group: -sum(_cap_or_floor(conditions[i]) for i in group),
        )
        for dropped in groups:
            trial = replace(
                resolved,
                conditions=tuple(c for i, c in enumerate(conditions) if i not in dropped),
            )
            if apply(trial, snapshot).feasible:
                return [render_condition(conditions[i]) for i in dropped]
    return []


def _unit(resolved, snapshot, facet_id: str, candidates) -> str | None:
    if resolved.facets(facet_id).subject == "evidence":
        for cid in candidates:
            for row in snapshot.evidence(cid, facet_id):
                if row.unit:
                    return row.unit
        return None
    return facet_unit(facet_id)


def smallest_changes(resolved, snapshot, domains: frozenset[str]) -> list[Relaxation]:
    """For each numeric cap or floor, the smallest change that admits a model."""
    out: list[Relaxation] = []
    conditions = resolved.conditions
    for i in _relaxable(resolved, domains):
        cond = conditions[i]
        if not _cap_or_floor(cond):
            continue
        others = conditions[:i] + conditions[i + 1:]
        # With the condition last, what it eliminates passed every other one.
        last = apply(replace(resolved, conditions=others + (cond,)), snapshot)
        text = render_condition(cond)
        values = [
            v
            for reason in last.eliminated
            if reason.condition == text and not reason.unverified
            for v in (reason.value if isinstance(reason.value, tuple | list) else [reason.value])
            if _numeric(v)
        ]
        if not values:
            continue
        op = _LOOSENS[cond.op]
        nearest = min(values) if op == "<=" else max(values)
        if float(nearest).is_integer():
            nearest = int(nearest)  # `<= 2`, as a person would write it
        relaxed = cond.model_copy(update={"op": op, "value": nearest})
        admitted = apply(
            replace(resolved, conditions=conditions[:i] + (relaxed,) + conditions[i + 1:]),
            snapshot,
        ).feasible
        if not admitted:
            continue
        out.append(Relaxation(
            condition=text,
            relaxed=render_condition(relaxed),
            facet=cond.facet,
            value=float(nearest),
            unit=_unit(resolved, snapshot, cond.facet, admitted),
            admits=len({snapshot.model_of(cid) for cid in admitted}),
        ))
    return out
