"""Subscription plans as records the engine can reason over (MODEL-200).

A plan's facts (``offering.subscription.*``) are read from the snapshot into a
``Plan``: its price, the surfaces it can be used through, what it covers and
its allowance. Each part is ``None`` when its fact is not known.

Coverage is the union of two sourced facts. ``models_covered`` names model IDs
directly. ``families_covered`` names families from ``registry/families.yaml``,
and a family resolves to every model in the snapshot's lineup, not retired,
whose ID starts with the family's prefix. Every coverage entry keeps its rule,
so an explanation can say why a model counts as covered.

A spec's ``access`` picks the surfaces that count: ``chat_app`` matches the
chat, desktop and mobile apps; ``coding_tool`` matches ``coding_tool:<harness>``
(any harness when the spec names none); ``own_software`` matches ``api``;
``own_hardware`` matches no plan.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from decision.contract import (
    Access,
    Issue,
    PlanAllowance,
    PlanCoverage,
    PlanPrice,
    PlanRoute,
    SpecError,
)
from decision.registry import CODING_TOOL
from decision.registry import default as default_registry

MODELS_COVERED = "offering.subscription.models_covered"
SURFACES = "offering.subscription.surfaces"
FAMILIES = "offering.subscription.families_covered"
QUOTE = "offering.subscription.coverage_quote"
PRICE = "offering.subscription.price"
PERIOD = "offering.subscription.billing_period"
ALLOWANCE = {
    "relative_to": "offering.subscription.allowance.relative_to",
    "multiplier": "offering.subscription.allowance.multiplier",
    "window": "offering.subscription.allowance.window",
    "tokens": "offering.subscription.allowance.tokens",
}
PRICE_MONTHLY = "offering.plan.price_monthly"

CHAT_SURFACES = frozenset({"chat_app", "desktop_app", "mobile_app"})
API = "api"
#: Access kinds whose pay-per-use offerings are routes.
PAY_PER_USE = frozenset({"coding_tool", "own_software"})

MODELS_COVERED_RULE = "named directly in the plan's offering.subscription.models_covered"


def _value(facts: Mapping[str, Any], facet: str) -> Any:
    fact = facts.get(facet)
    if fact is None or fact.state != "known" or fact.value is None:
        return None
    return fact.value


def _number(value: float) -> str:
    return f"{round(value, 6):,.6g}"


@dataclass(frozen=True)
class Plan:
    """One subscription plan's facts, as the engine reads them."""

    id: str
    provider: str
    name: str
    price: PlanPrice | None
    monthly: float | None
    surfaces: frozenset[str] | None
    coverage: tuple[PlanCoverage, ...] | None
    allowance: PlanAllowance

    @property
    def models(self) -> frozenset[str] | None:
        """Every model the plan covers, or ``None`` when its coverage is unknown."""
        if self.coverage is None:
            return None
        return frozenset(model for entry in self.coverage for model in entry.resolves_to)

    def covers(self, model_id: str) -> PlanCoverage | None:
        """The first coverage entry that reaches ``model_id``."""
        return next((entry for entry in self.coverage or () if model_id in entry.resolves_to),
                    None)

    def surface(self, access: Access) -> str | None:
        """The surface ``access`` uses this plan through, or ``None``.

        Call only when ``surfaces`` is known."""
        return next((s for s in sorted(self.surfaces or ()) if matches(access, s)), None)

    def monthly_formula(self) -> str | None:
        if self.price is None or self.monthly is None:
            return None
        if self.price.period == "monthly":
            return f"{self.name} lists {_number(self.price.amount)} USD a month"
        return (f"{self.name} lists {_number(self.price.amount)} USD a year ÷ 12 = "
                f"{_number(self.monthly)} USD a month")


def matches(access: Access, surface: str) -> bool:
    """Whether a plan surface serves ``access``."""
    if access.kind == "chat_app":
        return surface in CHAT_SURFACES
    if access.kind == "coding_tool":
        if access.harness is None:
            return surface.startswith(CODING_TOOL)
        return surface == CODING_TOOL + access.harness
    if access.kind == "own_software":
        return surface == API
    return False


def _coverage(facts: Mapping[str, Any], lineup: list[str],
              registry: Any) -> tuple[PlanCoverage, ...] | None:
    named, families = _value(facts, MODELS_COVERED), _value(facts, FAMILIES)
    if named is None and families is None:
        return None
    entries = []
    if named is not None:
        entries.append(PlanCoverage(resolves_to=sorted(named), rule=MODELS_COVERED_RULE))
    quote = _value(facts, QUOTE)
    for family_id in sorted(families or ()):
        try:
            family = registry.family(family_id)
        except KeyError:
            entries.append(PlanCoverage(
                family=family_id, quote=quote,
                rule=f"{family_id} is not in this registry's families, so it reaches no model"))
            continue
        entries.append(PlanCoverage(
            family=family_id, quote=quote,
            resolves_to=[model for model in lineup if family.resolves(model)],
            rule=(f"{family.name}: every model in the snapshot's lineup, not retired, "
                  f"whose ID starts with {family.prefix}")))
    return tuple(entries)


def _plan(raw: Mapping[str, Any], lineup: list[str], registry: Any) -> Plan:
    facts = raw["facts"]
    amount, period = _value(facts, PRICE), _value(facts, PERIOD)
    price = monthly = None
    if isinstance(amount, int | float) and period in ("monthly", "annual"):
        price = PlanPrice(amount=float(amount), currency="USD", period=period)
        monthly = float(amount) if period == "monthly" else round(float(amount) / 12, 6)
    surfaces = _value(facts, SURFACES)
    return Plan(
        id=raw["id"], provider=raw["provider"], name=raw["name"], price=price, monthly=monthly,
        surfaces=None if surfaces is None else frozenset(surfaces),
        coverage=_coverage(facts, lineup, registry),
        allowance=PlanAllowance(**{part: _value(facts, facet)
                                   for part, facet in ALLOWANCE.items()}),
    )


def load_plans(snapshot: Any, registry: Any = None) -> dict[str, Plan]:
    """Every plan in ``snapshot``, by ID, with its families resolved over its lineup."""
    registry = registry or default_registry()
    lineup = sorted(
        cid for cid in snapshot.candidates()
        if snapshot.kind(cid) == "model" and snapshot.lifecycle(cid) != "retired")
    return {raw["id"]: _plan(raw, lineup, registry)
            for raw in snapshot.subscription_offerings()}


def check_access(access: Access, registry: Any = None) -> None:
    """Refuse a harness the registry does not know."""
    if access.harness is None:
        return
    registry = registry or default_registry()
    if access.harness not in {h.id for h in registry.harnesses()}:
        raise SpecError([Issue(None, "access.harness",
                               f"unknown harness: {access.harness}", "access.harness")])


def _allowance_text(allowance: PlanAllowance) -> str:
    if allowance.tokens is not None:
        window = allowance.window or "allowance window"
        return (f" The plan includes {_number(allowance.tokens)} tokens per {window}, "
                "so tasks beyond that are not covered.")
    ratio = ""
    if allowance.multiplier is not None and allowance.relative_to is not None:
        ratio = (f" The page gives the allowance only as {_number(allowance.multiplier)}x "
                 f"{allowance.relative_to}'s.")
    return (f"{ratio} The allowance in tokens is not published, so whether that many "
            "tasks fit inside the plan is unknown.")


def route(plan: Plan, surface: str, coverage: PlanCoverage, access: Access,
          cost_per_task: float | None, where: str, *, bare: bool = False) -> PlanRoute:
    """``plan`` as a route to one row. ``cost_per_task`` is the row's pay-per-use
    cost; ``where`` names the row, for the basis. ``bare`` is a model's own row,
    which a plan reaches when no offering of its seller does (a subscription-only
    vendor's plans always do, MODEL-205)."""
    break_even = None
    if access.kind != "coding_tool":
        basis = ("A plan is paid by the month; ModelSpec does not turn its price into a "
                 "per-task cost.")
    elif plan.monthly is None:
        basis = f"{plan.name} does not publish a price, so no break-even is computed."
    elif bare:
        basis = (f"{plan.name} reaches {where} directly, not through a pay-per-use "
                 "offering, so no break-even is computed; each pay-per-use offering of "
                 "it is a result of its own.")
    elif cost_per_task is None:
        basis = (f"No pay-per-use price is known for {where}, so no break-even is computed.")
    elif cost_per_task == 0:
        basis = f"Pay-per-use on {where} costs nothing per task, so the plan never pays for itself."
    else:
        break_even = round(plan.monthly / cost_per_task, 1)
        basis = (f"{plan.name} costs {_number(plan.monthly)} USD a month; one task costs "
                 f"{_number(cost_per_task)} USD pay-per-use on {where} at list price, so the "
                 f"plan pays for itself above {_number(break_even)} tasks a month."
                 + _allowance_text(plan.allowance))
    return PlanRoute(
        plan=plan.id, name=plan.name, surface=surface, price=plan.price,
        price_monthly_usd=plan.monthly, coverage=coverage, allowance=plan.allowance,
        break_even_tasks_per_month=break_even, basis=basis)
