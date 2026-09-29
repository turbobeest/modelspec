"""The decision grouped by model: one row per model, its offerings beneath it (MODEL-180).

The page, the CLI and agents all ask "which models, and through which offerings?".
This answers it once, from the decision's own lists, so they cannot disagree.
"""

from __future__ import annotations

from collections.abc import Callable

from decision.contract import Decision, ModelOffering, ModelRow, OfferingRef

_ORDER = {"ranked": 0, "may_qualify": 1, "eliminated": 2}


def _key(ref: OfferingRef) -> tuple[str, str | None, str | None, str | None]:
    return (ref.model, ref.provider, ref.region, ref.tier)


def build_by_model(
    decision: Decision, cost_of: Callable[[OfferingRef], float | None]
) -> list[ModelRow]:
    """Group results, may-qualify and eliminated candidates by model, best first.

    A model is ranked when any offering is, else may qualify when any is unknown,
    else eliminated. An offering is in the strongest state the decision gives it.
    Eliminated candidates are listed only when the explanation carries them.
    """
    offerings: dict[str, dict[tuple, ModelOffering]] = {}

    def add(item: ModelOffering) -> None:
        offerings.setdefault(item.offering.model, {}).setdefault(_key(item.offering), item)

    for result in decision.results:
        add(ModelOffering(
            offering=result.offering,
            status="ranked",
            rank=result.rank,
            cost_per_task=result.cost_per_task,
        ))
    for candidate in decision.may_qualify:
        ref = candidate.offering or OfferingRef(model=candidate.model)
        add(ModelOffering(
            offering=ref,
            status="may_qualify",
            cost_per_task=cost_of(ref),
            unknown=list(candidate.unknown),
        ))
    for group in decision.eliminated.model_groups:
        rows = group.offerings or (
            [group.model_elimination] if group.model_elimination is not None else []
        )
        for row in rows:
            ref = row.offering or OfferingRef(model=group.model)
            add(ModelOffering(
                offering=ref,
                status="eliminated",
                cost_per_task=cost_of(ref),
                reason=row.condition,
            ))

    ranks = {r.model: r.model_rank for r in decision.results}
    rows = []
    for model, items in offerings.items():
        ordered = sorted(items.values(), key=lambda item: (_ORDER[item.status], item.rank or 0))
        status = ordered[0].status
        rows.append(ModelRow(
            model=model,
            status=status,
            rank=ranks.get(model) if status == "ranked" else None,
            cost_per_task=ordered[0].cost_per_task if status == "ranked" else None,
            offerings=ordered,
        ))
    # ``sorted`` is stable: may-qualify and ranked models keep first-seen order.
    return sorted(rows, key=lambda row: (_ORDER[row.status], row.rank or 0, row.model
                                          if row.status == "eliminated" else ""))
