"""What the caller holds, and the second answer it makes possible (MODEL-179).

An ``estate`` travels in the spec and is used for this one decision: it is not
stored, logged or echoed anywhere but the ``with_estate`` block of the reply.
The unrestricted answer is computed first and never sees it. ``with_estate`` is
the same question over the rows the estate reaches:

* a provider key reaches that provider's offerings, at list price;
* a plan reaches its provider's offerings of the models the plan is documented
  to cover, at marginal cost 0 (the fee is already paid). A plan that does not
  disclose its coverage reaches nothing for certain: those offerings may
  qualify, and say so;
* a device reaches the models whose published fit includes it, as their own
  rows (self-hosted, marginal cost 0). A device the fit is indeterminate on
  makes the model may-qualify.

``exhausted`` removes a plan, or a provider with its key and its plans.
``gain`` reruns the question once per hold the caller lacks and keeps those
that change the answer.

With an ``access`` (MODEL-200) only the routes that serve it count: a plan
reaches rows only when one of its surfaces matches (a plan whose surfaces are
unknown makes its rows may-qualify), a provider key only for ``coding_tool``
and ``own_software``, a device only for ``own_hardware``. ``access_reach`` is
the same rule over everything the catalogue offers, for the unrestricted
answer; there a plan-only row has no per-task price.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from decision import plans as plans_module
from decision.computed import Computed
from decision.contract import (
    Access,
    Decision,
    Estate,
    EstateGap,
    EstateHold,
    EstateMark,
    EstateResult,
    GainItem,
    Issue,
    SpecError,
    WithEstate,
)
from decision.registry import default as default_registry

COVERAGE = plans_module.MODELS_COVERED
SURFACES = plans_module.SURFACES
FITS = "model.fits_hardware"
WEIGHTS = "model.weights_openness"
#: The ``with_estate`` warning for a held plan that cannot serve own software.
PLAN_EXCLUDES_OWN_SOFTWARE = "plan_excludes_own_software"
FIT_INDETERMINATE = "model.hardware_fit_indeterminate"

_COST_BASIS = {"provider": "list_price", "plan": "plan_included", "device": "owned_hardware"}


@dataclass(frozen=True)
class Reach:
    """The rows one estate can use, by which hold reaches them."""

    via: Mapping[str, tuple[str, str]]
    unknown: Mapping[str, tuple[str, ...]]
    hosted: frozenset[str]
    marginal: Mapping[str, str]
    signature: frozenset[tuple[str, str]] = field(default_factory=frozenset)
    #: Rows reached only through a plan, outside an estate: no per-task price.
    unpriced: frozenset[str] = field(default_factory=frozenset)
    #: Row -> (plan ID, surface, coverage) for each plan that reaches it.
    routes: Mapping[str, tuple[tuple[str, str | None, Any], ...]] = field(default_factory=dict)
    #: Row -> the cheapest reaching plan's monthly price (``offering.plan.price_monthly``).
    plan_prices: Mapping[str, Computed] = field(default_factory=dict)
    #: The plans ``routes`` names, by ID.
    plans: Mapping[str, Any] = field(default_factory=dict)

    def holds(self, cid: str) -> bool:
        return cid in self.via or cid in self.unknown

    def holds_bare(self, cid: str) -> bool:
        return cid in self.hosted


class Catalogue:
    """The snapshot's rows grouped for reach: built once per decision."""

    def __init__(self, snapshot: Any) -> None:
        self.snapshot = snapshot
        self.by_provider: dict[str, list[str]] = {}
        self.bare: set[str] = set()
        for cid in snapshot.candidates():
            if snapshot.kind(cid) == "offering":
                provider = snapshot.fact(cid, "offering.provider").value
                self.by_provider.setdefault(provider, []).append(cid)
            else:
                self.bare.add(cid)
        self.plans = plans_module.load_plans(snapshot)
        self._price_sources = {
            plan["id"]: tuple(getattr(plan["facts"].get(plans_module.PRICE), "sources", ()))
            for plan in snapshot.subscription_offerings()}
        self._devices: dict[str, tuple[frozenset[str], frozenset[str]]] = {}

    def coverage(self, plan_id: str) -> frozenset[str] | None:
        return self.plans[plan_id].models

    def plan_price(self, plan_id: str) -> Computed | None:
        plan = self.plans[plan_id]
        formula = plan.monthly_formula()
        if formula is None:
            return None
        return Computed(plan.monthly, (), self._price_sources[plan_id], formula)

    def self_hosted(self) -> tuple[frozenset[str], frozenset[str]]:
        """Bare rows with a published fit on some device, and bare rows that may
        be self-hostable: not closed weights, fit not published."""
        fits, maybe = set(), set()
        for cid in self.bare:
            fact = self.snapshot.fact(cid, FITS)
            if fact.state == "known" and fact.value:
                fits.add(cid)
            elif self.snapshot.fact(cid, WEIGHTS).value != "closed_weights":
                maybe.add(cid)
        return frozenset(fits), frozenset(maybe)

    def device(self, device_id: str) -> tuple[frozenset[str], frozenset[str]]:
        """Bare rows that fit ``device_id``, and bare rows whose fit is indeterminate."""
        if device_id not in self._devices:
            snapshot = self.snapshot
            fits = set(snapshot.ids(snapshot.ids_where(FITS, "contains", device_id).passing))
            maybe = set(snapshot.ids(
                snapshot.ids_where(FIT_INDETERMINATE, "contains", device_id).passing))
            self._devices[device_id] = (
                frozenset(fits & self.bare), frozenset((maybe & self.bare) - fits))
        return self._devices[device_id]

    def offered_providers(self) -> list[str]:
        return sorted(self.by_provider)


def held(estate: Estate) -> tuple[frozenset[str], frozenset[str], frozenset[str]]:
    """The providers, plans and devices usable right now."""
    exhausted = set(estate.exhausted)
    providers = frozenset(estate.providers) - exhausted
    plans = frozenset(
        plan for plan in estate.plans
        if plan not in exhausted and plan.partition("/subscription/")[0] not in exhausted)
    return providers, plans, frozenset(estate.devices)


def _plan_rows(catalogue: Catalogue, plan: plans_module.Plan,
               covered: frozenset[str] | None) -> list[str]:
    """The rows ``plan`` could reach: its provider's rows of covered models, and
    the bare rows of covered models that provider does not sell. With unknown
    coverage, every row of its provider."""
    rows = catalogue.by_provider.get(plan.provider, ())
    if covered is None:
        return list(rows)
    sold = {catalogue.snapshot.model_of(cid) for cid in rows}
    return ([cid for cid in rows if catalogue.snapshot.model_of(cid) in covered]
            + [model for model in sorted(covered - sold) if model in catalogue.bare])


def reach(catalogue: Catalogue, providers: Iterable[str], plans: Iterable[str],
          devices: Iterable[str], access: Access | None = None, *, held: bool = True) -> Reach:
    """The rows ``providers``, ``plans`` and ``devices`` reach on ``access``.

    ``held`` rows are the caller's: a plan row costs 0 at the margin. Otherwise
    (the unrestricted answer on an ``access``) a row only a plan reaches has no
    per-task price."""
    via: dict[str, tuple[str, str]] = {}
    pending: dict[str, list[str]] = {}
    routes: dict[str, list[tuple[str, str | None, Any]]] = {}
    paid: set[str] = set()
    marginal: dict[str, str] = {}

    def unknown_on(rows: Iterable[str], facet: str) -> None:
        for cid in rows:
            facets = pending.setdefault(cid, [])
            if facet not in facets:
                facets.append(facet)

    use_plans = access is None or access.kind != "own_hardware"
    use_keys = access is None or access.kind in plans_module.PAY_PER_USE
    use_devices = access is None or access.kind == "own_hardware"
    for plan_id in sorted(plans) if use_plans else ():
        plan = catalogue.plans[plan_id]
        covered = plan.models
        surface = None
        if access is not None:
            if plan.surfaces is None:
                rows = _plan_rows(catalogue, plan, covered)
                if covered is None:
                    unknown_on(rows, COVERAGE)
                unknown_on(rows, SURFACES)
                continue
            surface = plan.surface(access)
            if surface is None:
                continue
        if covered is None:
            unknown_on(catalogue.by_provider.get(plan.provider, ()), COVERAGE)
            continue
        for cid in _plan_rows(catalogue, plan, covered):
            via.setdefault(cid, ("plan", plan_id))
            routes.setdefault(cid, []).append(
                (plan_id, surface, plan.covers(catalogue.snapshot.model_of(cid))))
    for provider in sorted(providers) if use_keys else ():
        for cid in catalogue.by_provider.get(provider, ()):
            via.setdefault(cid, ("provider", provider))
            paid.add(cid)
    for device_id in sorted(devices) if use_devices else ():
        fits, maybe = catalogue.device(device_id)
        for cid in sorted(fits):
            via.setdefault(cid, ("device", device_id))
        unknown_on(maybe, FITS)
    unknown = {cid: tuple(pending[cid]) for cid in sorted(pending) if cid not in via}
    if held:
        for cid, (kind, hold_id) in via.items():
            if kind == "plan":
                marginal[cid] = (f"included in {hold_id}: one more task inside a plan that is "
                                 "not exhausted costs nothing extra")
            elif kind == "device":
                marginal[cid] = f"runs on {hold_id}, which the caller holds: no per-task price"
    unpriced = frozenset() if held else frozenset(
        cid for cid, (kind, _) in via.items() if kind == "plan" and cid not in paid)
    plan_prices: dict[str, Computed] = {}
    for cid, reached in routes.items():
        prices = [price for price in (catalogue.plan_price(plan_id) for plan_id, _, _ in reached)
                  if price is not None]
        if prices:
            plan_prices[cid] = min(prices, key=lambda price: price.value)
    hosted = frozenset(
        cid for cid in (*via, *unknown) if cid in catalogue.bare)
    signature = frozenset((*(("row", cid) for cid in via), *(("unk", cid) for cid in unknown)))
    return Reach(via, unknown, hosted, marginal, signature, unpriced,
                 {cid: tuple(r) for cid, r in routes.items()}, plan_prices, catalogue.plans)


def access_reach(catalogue: Catalogue, access: Access) -> Reach:
    """Every route the catalogue offers on ``access``, for the unrestricted answer."""
    if access.kind == "own_hardware":
        fits, maybe = catalogue.self_hosted()
        via = {cid: ("device", "published fit") for cid in sorted(fits)}
        unknown = {cid: (FITS,) for cid in sorted(maybe)}
        return Reach(via, unknown, fits | maybe, {},
                     frozenset((*(("row", c) for c in via), *(("unk", c) for c in unknown))))
    return reach(catalogue, catalogue.offered_providers(), catalogue.plans, (), access,
                 held=False)


def check(estate: Estate, snapshot: Any) -> None:
    """Refuse an id the vocabulary does not know, naming where it sits in the spec."""
    registry = default_registry()
    providers = {p.id for p in registry.providers()}
    vendors = {v.id for v in registry.vendors()}
    plans = {plan["id"] for plan in snapshot.subscription_offerings()}
    devices = registry.allowed_values(registry.facet(FITS)) or frozenset()
    issues = []
    for field_name, noun, allowed in (
        ("providers", "provider", providers), ("plans", "plan", plans),
        ("devices", "device", devices),
        ("exhausted", "provider or plan", providers | vendors | plans),
    ):
        for index, value in enumerate(getattr(estate, field_name)):
            if value in allowed:
                continue
            message = f"unknown {noun} ID: {value}"
            if field_name == "providers" and value in vendors:
                # A subscription-only vendor has no pay-per-use key (MODEL-205).
                message = (f"{value} sells subscription plans only, not pay-per-use: "
                           "name its plan in estate.plans")
            issues.append(Issue(
                None, f"estate.{field_name}", message, f"estate.{field_name}[{index}]"))
    if issues:
        raise SpecError(issues)


@dataclass(frozen=True)
class Ran:
    """One run of the engine over a reach: the decision, every model it ranked
    best first, the candidate row behind each returned result, and the
    computed-facet view that costed them."""

    decision: Decision
    models: list[str]
    rows: list[str]
    computed: Any


Run = Callable[[Reach | None, int], Ran]


def _answered(ran: Ran) -> tuple[Any, ...]:
    lead = ran.models[0] if ran.models and ran.decision.answer is None else None
    return (ran.decision.status, ran.decision.answer, lead)


def _mark(computed: Any, cid: str, current: Reach, access: Access | None) -> EstateMark:
    kind, hold_id = current.via[cid]
    cost = None
    if kind == "provider":
        fact = computed.fact(cid, "offering.cost_per_task")
        cost = fact.value if fact.state == "known" else None
    else:
        cost = 0
    coverage = None
    if kind == "plan" and access is not None:
        coverage = next((c for plan_id, _, c in current.routes.get(cid, ()) if plan_id == hold_id),
                        None)
    return EstateMark(
        via=EstateHold(kind=kind, id=hold_id), cost_basis=_COST_BASIS[kind],
        marginal_cost_per_task_usd=cost, coverage=coverage)


def _label(answer: Any, models: list[str]) -> str:
    if answer is not None and answer.kind == "tied":
        return f"a tie of {', '.join(answer.members)}"
    return answer.leader if answer is not None else (models[0] if models else "none")


def _summary(same: bool, unrestricted: Ran, held: Ran, unreachable: list[str]) -> str:
    unrestricted_label = _label(unrestricted.decision.answer, unrestricted.models)
    if not held.models:
        return ("What you hold reaches no model that qualifies. Unrestricted, the best is "
                f"{unrestricted_label}.")
    held_label = _label(held.decision.answer, held.models)
    if same:
        return f"What you hold reaches the unrestricted answer, {held_label}."
    if not unreachable:
        return (f"Unrestricted, the best is {unrestricted_label}. With what you hold it is "
                f"{held_label}; no model ranked at or above it is outside your estate, so "
                "the answer differs only in cost or how the tie is broken.")
    names = ", ".join(unreachable[:5])
    more = len(unreachable) - 5
    tail = f" and {more} more" if more > 0 else ""
    return (f"Unrestricted, the best is {unrestricted_label}. With what you hold it is "
            f"{held_label}; {len(unreachable)} model(s) ranked at or above it are outside "
            f"your estate: {names}{tail}.")


def with_estate(
    estate: Estate,
    snapshot: Any,
    unrestricted: Ran,
    run: Run,
    limit: int,
    access: Access | None = None,
    catalogue: Catalogue | None = None,
) -> WithEstate:
    """The reply's ``with_estate`` block."""
    catalogue = catalogue or Catalogue(snapshot)
    providers, plans, devices = held(estate)
    current = reach(catalogue, providers, plans, devices, access)
    ran = run(current, limit)
    decision = ran.decision

    results = [
        EstateResult(
            rank=row.rank, offering=row.offering, soft_penalty=row.soft_penalty,
            warnings=row.warnings,
            estate=_mark(ran.computed, cid, current, access))
        for row, cid in zip(decision.results, ran.rows, strict=True)
    ]
    same = _answered(unrestricted) == _answered(ran)
    best = unrestricted.models
    if ran.models and ran.models[0] in best:
        best = best[: best.index(ran.models[0])]
    tied = unrestricted.decision.answer
    keep = set(best) | set(tied.members if tied is not None and tied.kind == "tied" else ())
    reached = set(ran.models)
    unreachable = [m for m in unrestricted.models if m in keep and m not in reached]
    gap = EstateGap(
        same_answer=same, unreachable_models=unreachable,
        summary=_summary(same, unrestricted, ran, unreachable))
    gain = _gain(catalogue, estate, (providers, plans, devices), current, ran, run, access)
    warnings = []
    if access is not None and access.kind == "own_software" and any(
        catalogue.plans[plan_id].surfaces is not None
        and plans_module.API not in catalogue.plans[plan_id].surfaces
        for plan_id in plans
    ):
        warnings.append(PLAN_EXCLUDES_OWN_SOFTWARE)
    return WithEstate(
        status=decision.status, answer=decision.answer, results=results,
        may_qualify=decision.may_qualify, truncated=decision.truncated, gap=gap, gain=gain,
        warnings=warnings)


def _gain(catalogue, estate, holds, current, ran, run, access=None):
    providers, plans, devices = holds
    base = _answered(ran)
    candidates: list[tuple[EstateHold, Reach]] = []
    for provider in catalogue.offered_providers():
        if provider not in providers and provider not in estate.exhausted:
            candidates.append((
                EstateHold(kind="provider", id=provider),
                reach(catalogue, providers | {provider}, plans, devices, access)))
    for plan_id in sorted(catalogue.plans):
        provider = plan_id.partition("/subscription/")[0]
        if (plan_id in plans or plan_id in estate.exhausted or provider in estate.exhausted
                or plan_id in estate.plans):
            continue
        candidates.append((
            EstateHold(kind="plan", id=plan_id),
            reach(catalogue, providers, plans | {plan_id}, devices, access)))
    registry = default_registry()
    for device_id in sorted(registry.allowed_values(registry.facet(FITS)) or ()):
        if device_id not in devices:
            candidates.append((
                EstateHold(kind="device", id=device_id),
                reach(catalogue, providers, plans, devices | {device_id}, access)))
    seen: dict[frozenset, Ran] = {}
    items = []
    for hold, trial in candidates:
        if trial.signature == current.signature:
            continue
        if trial.signature not in seen:
            seen[trial.signature] = run(trial, 1)
        result = seen[trial.signature]
        if _answered(result) == base:
            continue
        items.append(GainItem(
            add=hold, status=result.decision.status,
            leader=result.models[0] if result.models else None,
            answer=result.decision.answer))
    return items


