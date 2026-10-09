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

`task_tokens_hint` names the one case where the question itself is not the
problem: a per-task cost cap fails only because the spec gave no `task_tokens`,
so every model was priced as a 40,000-token task (MODEL-316).

`single_gates` names each other hard condition whose removal alone, with every
remaining condition and the same reach kept, admits a model (MODEL-356).
"""

from __future__ import annotations

from dataclasses import replace
from itertools import combinations
from fractions import Fraction
from math import ceil, floor
from typing import Any

from decision.contract import (
    DEFAULT_TASK_TOKENS,
    AllOf,
    AnyOf,
    Compare,
    NotOf,
    Relaxation,
    RelaxSingle,
    SingleGate,
    TaskTokens,
    TaskTokensHint,
    render_condition,
)
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


def binding_constraint(funnel, domains: frozenset[str]) -> str | None:
    """The condition that first emptied the lineup, when dropping it would not
    change the question. ``None`` when that condition is the class or a
    requested capability domain, or when nothing with candidates went to zero."""
    for step in funnel:
        if step.before > 0 and step.after == 0 and not _changes_the_question(
            step._condition, domains,
        ):
            return step.condition
    return None


def _distinct_models(snapshot, candidate_ids) -> int:
    return len({snapshot.model_of(cid) for cid in candidate_ids})


def single_gates(resolved, snapshot, domains: frozenset[str], reach=None) -> RelaxSingle:
    """Each relaxable hard condition whose removal alone admits a model.

    Every other condition stays, and so does ``reach``. ``admits`` counts
    distinct models. Gates are ordered by that count, then by spec order.
    ``none`` means no single removal admits a model. ``together_admits`` counts
    the distinct models that qualify when every relaxable gate is removed at
    once. It is 0, with no extra pass, when there are no relaxable gates.
    """
    conditions = resolved.conditions
    relaxable = _relaxable(resolved, domains)
    found: list[tuple[int, int, str]] = []
    for index in relaxable:
        trial = replace(
            resolved,
            conditions=tuple(cond for i, cond in enumerate(conditions) if i != index),
        )
        admits = _distinct_models(snapshot, apply(trial, snapshot, reach).feasible)
        if admits < 1:
            continue
        found.append((admits, index, render_condition(conditions[index])))
    found.sort(key=lambda item: -item[0])
    gates = [SingleGate(condition=text, admits=admits) for admits, _, text in found]
    together = 0
    if relaxable:
        dropped = set(relaxable)
        trial = replace(
            resolved,
            conditions=tuple(cond for i, cond in enumerate(conditions) if i not in dropped),
        )
        together = _distinct_models(snapshot, apply(trial, snapshot, reach).feasible)
    return RelaxSingle(
        status="found" if gates else "none",
        gates=gates,
        together_admits=together,
    )


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


def task_tokens_hint(resolved, relax: list[str], relax_to: list[Relaxation],
                     task_tokens: TaskTokens | None) -> TaskTokensHint | None:
    """The per-task cost cap failed only at the default task size, and the task that passes.

    Only when the spec gave no ``task_tokens`` and ``relax`` is that cap alone.
    Cost per task is linear in tokens, so scaling the default by cap / nearest
    excluded cost gives the largest task at the default's ratio that a model
    meets; a strict cap stays strict.
    """
    if task_tokens is not None or len(relax) != 1:
        return None
    cap = next((cond for cond in resolved.conditions
                if isinstance(cond, Compare) and cond.facet == "offering.cost_per_task"
                and cond.op in ("<", "<=") and _numeric(cond.value)
                and render_condition(cond) == relax[0]), None)
    nearest = next((r.value for r in relax_to if r.condition == relax[0]), None)
    if cap is None or not nearest:
        return None
    # Exact: in floats 0.07 / 0.1 × 40,000 is 28,000.000000000004, and a strict
    # cap would then be offered a task that costs exactly the cap.
    scale = Fraction(str(cap.value)) / Fraction(str(nearest))
    fit = floor if cap.op == "<=" else (lambda tokens: ceil(tokens) - 1)
    default = DEFAULT_TASK_TOKENS
    admits = TaskTokens(input=max(fit(default.input * scale), 0),
                        output=max(fit(default.output * scale), 0))
    if admits.input == 0:
        return None
    return TaskTokensHint(
        condition=relax[0],
        default=default,
        admits_at=admits,
        message=(
            f"No model meets {relax[0]} at the default task size of {default.input:,} input "
            f"and {default.output:,} output tokens, used because the spec gives no task_tokens. "
            f"A task of at most {admits.input:,} input and {admits.output:,} output tokens "
            "admits a model. Set task_tokens to your task's size and decide again."
        ),
    )
