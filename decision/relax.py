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
The class and a requested domain are never gates. `question_admits` records
when removing one of those alone would admit a model.
"""

from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
from itertools import combinations
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
from decision.filter import _has_best, _Run, apply
from decision.resolve import asks_for_retired, without

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
    ``none`` lists only those relaxable gates. A hard condition ``_relaxable``
    leaves out because it changes the question (the class, or a requested
    domain) is probed the same way and never listed. ``question_admits`` is
    true when removing one of those alone admits a model. ``together_admits``
    counts the distinct models that qualify when every relaxable gate is
    removed at once. It is 0, with no extra pass, when there are no relaxable
    gates.
    """
    conditions = resolved.conditions
    relaxable = _relaxable(resolved, domains)

    def admits_without(index: int) -> int:
        trial = without(resolved, (index,))
        return _distinct_models(snapshot, apply(trial, snapshot, reach).feasible)

    found: list[tuple[int, int, str]] = []
    for index in relaxable:
        admits = admits_without(index)
        if admits < 1:
            continue
        found.append((admits, index, render_condition(conditions[index])))
    found.sort(key=lambda item: -item[0])
    gates = [SingleGate(condition=text, admits=admits) for admits, _, text in found]
    together = 0
    if relaxable:
        trial = without(resolved, relaxable)
        together = _distinct_models(snapshot, apply(trial, snapshot, reach).feasible)
    question_admits = any(
        admits_without(index) >= 1
        for index, cond in enumerate(conditions)
        if cond.soft is None and _changes_the_question(cond, domains)
    )
    return RelaxSingle(
        status="found" if gates else "none",
        gates=gates,
        together_admits=together,
        question_admits=question_admits,
    )


def _equivalent_groups(conditions, hard: list[int]) -> list[tuple[int, ...]]:
    """Indexes that render alike. The filter ignores extra copies of one gate."""
    grouped: dict[str, list[int]] = {}
    for index in hard:
        grouped.setdefault(render_condition(conditions[index]), []).append(index)
    return [tuple(indexes) for indexes in grouped.values()]


def _dropped_admits(resolved, snapshot, dropped: tuple[int, ...]) -> bool:
    return bool(apply(without(resolved, dropped), snapshot).feasible)


def _fewest_from_groups(resolved, snapshot, conditions, groups: list[tuple[int, ...]]) -> list[str]:
    """Exact search over equivalent gates, caps and floors before spec order."""
    proposals: list[tuple[int, int, tuple[int, ...]]] = []
    for size in range(1, len(groups) + 1):
        for chosen in combinations(range(len(groups)), size):
            indexes = tuple(sorted(index for group in chosen for index in groups[group]))
            cap = sum(_cap_or_floor(conditions[index]) for index in indexes)
            proposals.append((len(indexes), -cap, indexes))
    proposals.sort()
    for _, _, indexes in proposals:
        if _dropped_admits(resolved, snapshot, indexes):
            return [render_condition(conditions[index]) for index in indexes]
    return []


def _excluded_bits(run: _Run) -> tuple[int, int]:
    """Retired bits, and bits that no dropped gate can put in the lineup.

    ``fewest`` reruns the filter without a reach, so a bare model that has an
    offering, and a bare model without open weights, stay out.
    """
    index = run.index
    sold = {index.model_of(cid) for cid in run.ids if index.kind(cid) == "offering"}
    retired = structural = 0
    for position, cid in enumerate(run.ids):
        bit = 1 << position
        if cid in sold:
            structural |= bit
        elif run._life(cid) == "retired":
            retired |= bit
        if index.kind(cid) == "model" and cid not in sold:
            weights = index.fact(cid, "model.weights_openness")
            if weights.state != "known" or weights.value != "open_weights":
                structural |= bit
    return retired, structural


def _blocked_bits(run: _Run, cond) -> int:
    """Candidates this hard condition keeps out of ``feasible``."""
    raw = run._eval(cond)
    unknown = run.universe & ~raw.passing & ~raw.failing
    as_pass, _, _ = run._unknown_disposition(cond, unknown)
    return run.universe & ~(raw.passing | as_pass)


def _failure_proposals(resolved, snapshot, conditions, hard: list[int],
                       groups: list[tuple[int, ...]]) -> list[tuple[int, ...]]:
    """Smallest index sets that would qualify some candidate, best key first.

    A ``best(m)`` threshold depends on which other gates remain, so callers
    skip this when any condition uses one.
    """
    run = _Run(resolved, snapshot)
    retired, structural = _excluded_bits(run)
    hard_set = set(hard)
    always = [
        index for index, cond in enumerate(conditions)
        if cond.soft is None and index not in hard_set
    ]
    always_blocks = 0
    for index in always:
        always_blocks |= _blocked_bits(run, conditions[index])
    group_blocks = [_blocked_bits(run, conditions[group[0]]) for group in groups]
    group_retired = [
        any(asks_for_retired(conditions[index]) for index in group) for group in groups
    ]
    fixed_retired = any(asks_for_retired(cond) for index, cond in enumerate(conditions)
                        if index not in hard_set)
    eligible = run.universe & ~structural
    seen: set[tuple[int, ...]] = set()
    proposals: list[tuple[int, ...]] = []
    bit = 1
    while bit <= eligible:
        if not eligible & bit or always_blocks & bit:
            bit <<= 1
            continue
        chosen = [group for group, blocks in enumerate(group_blocks) if blocks & bit]
        if bit & retired and not fixed_retired and not any(
            group_retired[group] and group not in chosen for group in range(len(groups))
        ):
            bit <<= 1
            continue
        indexes = tuple(sorted(index for group in chosen for index in groups[group]))
        if indexes not in seen:
            seen.add(indexes)
            proposals.append(indexes)
        bit <<= 1
    proposals.sort(key=lambda indexes: (
        len(indexes),
        -sum(_cap_or_floor(conditions[index]) for index in indexes),
        indexes,
    ))
    return proposals


def fewest(resolved, snapshot, domains: frozenset[str]) -> list[str]:
    """The fewest relaxable conditions whose removal gives a feasible answer."""
    conditions = resolved.conditions
    hard = _relaxable(resolved, domains)
    if not hard:
        return []
    groups = _equivalent_groups(conditions, hard)
    # best(m) is relative to whoever survived the other gates, so failure sets
    # are not fixed. Equivalent gates still search as one choice.
    if any(_has_best(cond) for cond in conditions):
        return _fewest_from_groups(resolved, snapshot, conditions, groups)
    proposals = _failure_proposals(resolved, snapshot, conditions, hard, groups)
    for indexes in proposals:
        if indexes and _dropped_admits(resolved, snapshot, indexes):
            return [render_condition(conditions[index]) for index in indexes]
    if any(not indexes for indexes in proposals) and apply(resolved, snapshot).feasible:
        return _fewest_from_groups(resolved, snapshot, conditions, groups)
    if proposals and not any(indexes for indexes in proposals):
        return []
    if not proposals:
        return []
    return _fewest_from_groups(resolved, snapshot, conditions, groups)


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
