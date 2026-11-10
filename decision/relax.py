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


#: Filter calls one ``fewest`` search may spend. Past this it returns no
#: relaxation. That empty result is the same every time.
FEWEST_FILTER_BUDGET = 64


class _FilterBudget:
    def __init__(self) -> None:
        self.used = 0

    def apply(self, resolved, snapshot):
        if self.used >= FEWEST_FILTER_BUDGET:
            return None
        self.used += 1
        return apply(resolved, snapshot)


def _cap_count(conditions, indexes) -> int:
    return sum(_cap_or_floor(conditions[index]) for index in indexes)


def _sort_key(conditions, indexes):
    return (len(indexes), -_cap_count(conditions, indexes), indexes)


def _render(conditions, indexes) -> list[str]:
    return [render_condition(conditions[index]) for index in indexes]


def _lazy_drops(conditions, hard: list[int]):
    """Size ascending, caps before other gates, then index order.

    Each size is scanned once per cap count. The combinations are not stored.
    """
    for size in range(1, len(hard) + 1):
        for caps_wanted in range(size, -1, -1):
            for combo in combinations(hard, size):
                if _cap_count(conditions, combo) == caps_wanted:
                    yield combo


def _search_indexes(budget: _FilterBudget, resolved, snapshot, conditions, hard: list[int]):
    """The first drop that confirms, or None when the filter budget is spent."""
    for dropped in _lazy_drops(conditions, hard):
        trial = budget.apply(without(resolved, dropped), snapshot)
        if trial is None:
            return None
        if trial.feasible:
            return _render(conditions, dropped)
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


def _candidate_blocks(resolved, snapshot, conditions, hard: list[int],
                      groups: list[tuple[int, ...]]) -> list[tuple[tuple[int, ...], int]]:
    """Each eligible candidate and the gate groups that keep it out."""
    run = _Run(resolved, snapshot)
    retired, structural = _excluded_bits(run)
    hard_set = set(hard)
    always_blocks = 0
    fixed_retired = False
    for index, cond in enumerate(conditions):
        if cond.soft is not None or index in hard_set:
            continue
        always_blocks |= _blocked_bits(run, cond)
        fixed_retired = fixed_retired or asks_for_retired(cond)
    group_blocks = [_blocked_bits(run, conditions[group[0]]) for group in groups]
    group_retired = [
        any(asks_for_retired(conditions[index]) for index in group) for group in groups
    ]
    eligible = run.universe & ~structural
    found: list[tuple[tuple[int, ...], int]] = []
    bit = 1
    while bit <= eligible:
        if eligible & bit and not always_blocks & bit:
            chosen = [group for group, blocks in enumerate(group_blocks) if blocks & bit]
            retired_kept = fixed_retired or any(
                group_retired[group] and group not in chosen for group in range(len(groups))
            )
            if not bit & retired or retired_kept:
                indexes = tuple(sorted(index for group in chosen for index in groups[group]))
                found.append((indexes, bit))
        bit <<= 1
    return found


def _failure_proposals(resolved, snapshot, conditions, hard: list[int],
                       groups: list[tuple[int, ...]]) -> list[tuple[int, ...]]:
    """Smallest index sets that would qualify some candidate, caps first.

    A best margin depends on which other gates remain, so callers score those
    gates separately.
    """
    seen: set[tuple[int, ...]] = set()
    proposals: list[tuple[int, ...]] = []
    for indexes, _bit in _candidate_blocks(resolved, snapshot, conditions, hard, groups):
        if indexes not in seen:
            seen.add(indexes)
            proposals.append(indexes)
    proposals.sort(key=lambda indexes: _sort_key(conditions, indexes))
    return proposals


def _anchor_bits(resolved, snapshot, candidate_ids) -> tuple[int, _Run]:
    run = _Run(resolved, snapshot)
    bits = 0
    for cid in candidate_ids:
        position = run.pos.get(cid)
        if position is not None:
            bits |= 1 << position
    return bits, run


def _best_proposals(budget: _FilterBudget, resolved, snapshot, conditions, hard: list[int],
                    groups: list[tuple[int, ...]]):
    """Best conditions are scored against the lineup left by the other gates.

    One trial per blocking set, then the same size and cap order as before.
    None when the filter budget is spent.
    """
    plain = [group for group in groups if not _has_best(conditions[group[0]])]
    best_groups = [group for group in groups if _has_best(conditions[group[0]])]
    best_indexes = [index for group in best_groups for index in group]
    by_plain: dict[tuple[int, ...], list[int]] = {}
    order: list[tuple[int, ...]] = []
    for indexes, bit in _candidate_blocks(resolved, snapshot, conditions, hard, plain):
        if indexes not in by_plain:
            order.append(indexes)
            by_plain[indexes] = []
        by_plain[indexes].append(bit)
    proposals: list[tuple[int, ...]] = []
    seen: set[tuple[int, ...]] = set()
    for plain_indexes in order:
        dropped = tuple(sorted(set(plain_indexes) | set(best_indexes)))
        trial = budget.apply(without(resolved, dropped), snapshot)
        if trial is None:
            return None
        anchor, run = _anchor_bits(resolved, snapshot, trial.feasible)
        run.anchor = anchor
        best_blocks = [_blocked_bits(run, conditions[group[0]]) for group in best_groups]
        for bit in by_plain[plain_indexes]:
            extra = [
                index
                for group, blocks in zip(best_groups, best_blocks, strict=True)
                if blocks & bit
                for index in group
            ]
            proposal = tuple(sorted(set(plain_indexes) | set(extra)))
            if proposal not in seen:
                seen.add(proposal)
                proposals.append(proposal)
    proposals.sort(key=lambda indexes: _sort_key(conditions, indexes))
    return proposals


def fewest(resolved, snapshot, domains: frozenset[str]) -> list[str]:
    """The fewest relaxable conditions whose removal gives a feasible answer.

    The search spends at most ``FEWEST_FILTER_BUDGET`` filter calls. When that
    budget is spent it returns no relaxation. That empty result is deterministic.
    An already feasible spec uses the same size, cap and index order as the
    per-index search and stops at the first drop that confirms.
    """
    conditions = resolved.conditions
    hard = _relaxable(resolved, domains)
    if not hard:
        return []
    budget = _FilterBudget()
    current = budget.apply(resolved, snapshot)
    if current is None:
        return []
    if current.feasible:
        found = _search_indexes(budget, resolved, snapshot, conditions, hard)
        return [] if found is None else found
    groups = _equivalent_groups(conditions, hard)
    if any(_has_best(cond) for cond in conditions):
        proposals = _best_proposals(budget, resolved, snapshot, conditions, hard, groups)
        if proposals is None:
            return []
    else:
        proposals = _failure_proposals(resolved, snapshot, conditions, hard, groups)
    for indexes in proposals:
        if not indexes:
            continue
        trial = budget.apply(without(resolved, indexes), snapshot)
        if trial is None:
            return []
        if trial.feasible:
            return _render(conditions, indexes)
    if not proposals or not any(proposals):
        return []
    found = _search_indexes(budget, resolved, snapshot, conditions, hard)
    return [] if found is None else found


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
