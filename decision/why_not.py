"""Why one model is, or is not, where a decision put it (MODEL-180).

Read from a finished decision, never recomputed: a model that failed a Must says
which; a model that may qualify says what is unknown; a ranked model says where
it ranked and which weight change would put it first. The decision must be
explained at ``full`` to know about eliminated models.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from decision.filter import strip_unverified_condition
from decision.contract import (
    ConstraintCost,
    Decision,
    FacetId,
    ModelId,
    ModelOffering,
    Scalar,
    TippingPoint,
    _Strict,
)

Verdict = Literal["ranked", "may_qualify", "eliminated", "not_in_decision"]


class FailedMust(_Strict):
    """One Must condition the model's offerings failed."""

    condition: str
    value: Scalar | None = None
    values: list[Scalar] = Field(default_factory=list)
    unit: str | None = None
    formula: str | None = None
    #: How far the value is from the condition's threshold, when it has one.
    distance: float | None = None


class WhyNot(_Strict):
    model: ModelId
    verdict: Verdict
    #: The model's place among ranked models, for a ranked model.
    model_rank: int | None = Field(default=None, ge=1)
    #: How many models were ranked.
    ranked_models: int = Field(default=0, ge=0)
    offerings: list[ModelOffering] = Field(default_factory=list)
    failed: list[FailedMust] = Field(default_factory=list)
    unknown: list[FacetId] = Field(default_factory=list)
    #: For an eliminated model: what relaxing each failed Must costs and admits.
    constraint_costs: list[ConstraintCost] = Field(default_factory=list)
    #: For a ranked model below first place: the weight changes that put it first.
    tipping_points: list[TippingPoint] = Field(default_factory=list)
    summary: str


def _figure(value: Scalar | None, unit: str | None) -> str:
    return "" if value is None else f" ({value}{' ' + unit if unit else ''})"


def why_not(decision: Decision, model: str) -> WhyNot:
    """Answer "why not ``model``?" from ``decision``; see the module docstring."""
    row = next((r for r in decision.by_model if r.model == model), None)
    ranked = sum(r.status == "ranked" for r in decision.by_model)
    if row is None:
        reason = f"{model} is not in this decision."
        if decision.truncated.models:
            reason += (
                f" {decision.truncated.models} ranked model(s) were cut by the limit;"
                " raise the limit to see them."
            )
        if decision.explain != "full":
            reason += (
                f" It was explained at {decision.explain!r}, which does not list eliminated"
                " models; explain at 'full' to see whether it failed a Must."
            )
        return WhyNot(model=model, verdict="not_in_decision", ranked_models=ranked, summary=reason)

    if row.status == "eliminated":
        near = {(n.offering.model, n.condition): n.distance for n in decision.near_misses}
        failed: dict[str, FailedMust] = {}
        for item in decision.eliminated.models:
            if item.model == model and item.condition not in failed:
                failed[item.condition] = FailedMust(
                    condition=item.condition,
                    value=item.value,
                    values=item.values,
                    unit=item.unit,
                    formula=item.formula,
                    distance=near.get((model, item.condition)),
                )
        costs = [
            c for c in decision.constraint_costs
            if any(c.condition == strip_unverified_condition(text) for text in failed)
        ]
        first = next(iter(failed.values()), None)
        summary = f"{model} was eliminated"
        if first is not None:
            summary += f": it failed {first.condition}{_figure(first.value, first.unit)}"
            if len(failed) > 1:
                summary += f" and {len(failed) - 1} more"
        summary += "."
        if costs:
            summary += f" Relaxing {costs[0].condition} would admit {costs[0].admits} candidate(s)."
        return WhyNot(
            model=model, verdict="eliminated", ranked_models=ranked, offerings=row.offerings,
            failed=list(failed.values()), constraint_costs=costs, summary=summary,
        )

    if row.status == "may_qualify":
        unknown = sorted({f for o in row.offerings if o.status == "may_qualify" for f in o.unknown})
        gaps = [o.reason for o in row.offerings if o.status == "may_qualify" and o.reason]
        if gaps:
            summary = (
                f"{model} may qualify but is not ranked: {gaps[0]}. "
                "Unknown is never ranked last and never dropped."
            )
        else:
            summary = (
                f"{model} may qualify but is not ranked: {', '.join(unknown)} is not known"
                " for it. Unknown is never ranked last and never dropped."
            )
        return WhyNot(
            model=model, verdict="may_qualify", ranked_models=ranked, offerings=row.offerings,
            unknown=unknown, summary=summary,
        )

    points = [p for p in decision.tipping_points if p.new_top == model]
    summary = f"{model} ranked #{row.rank} of {ranked} model(s)"
    tied = decision.answer is not None and decision.answer.kind == "tied"
    if tied and model in decision.answer.members:
        summary += f", tied for the answer with {', '.join(m for m in decision.answer.members if m != model)}"
    summary += "."
    if row.rank == 1:
        points = []
    elif points:
        first = points[0]
        direction = first.description.split()[0]
        past = "" if first.threshold is None else f" past {first.threshold:g}"
        summary += f" It takes first place if you {direction} the weight on {first.dimension}{past}."
    else:
        summary += " No single weight change puts it first."
    return WhyNot(
        model=model, verdict="ranked", model_rank=row.rank, ranked_models=ranked,
        offerings=row.offerings, tipping_points=points, summary=summary,
    )
