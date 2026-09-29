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
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from decision.contract import (
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

COVERAGE = "offering.subscription.models_covered"
FITS = "model.fits_hardware"
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
        self.plans = {plan["id"]: plan for plan in snapshot.subscription_offerings()}
        self._devices: dict[str, tuple[frozenset[str], frozenset[str]]] = {}

    def coverage(self, plan_id: str) -> frozenset[str] | None:
        fact = self.plans[plan_id]["facts"].get(COVERAGE)
        if fact is None or fact.state != "known" or fact.value is None:
            return None
        return frozenset(fact.value)

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


def reach(catalogue: Catalogue, providers: Iterable[str], plans: Iterable[str],
          devices: Iterable[str]) -> Reach:
    via: dict[str, tuple[str, str]] = {}
    coverage_unknown: set[str] = set()
    indeterminate: set[str] = set()
    marginal: dict[str, str] = {}
    for plan_id in sorted(plans):
        provider = catalogue.plans[plan_id]["provider"]
        covered = catalogue.coverage(plan_id)
        rows = catalogue.by_provider.get(provider, ())
        if covered is None:
            coverage_unknown.update(rows)
            continue
        sold_here = set()
        for cid in rows:
            model = catalogue.snapshot.model_of(cid)
            if model in covered:
                sold_here.add(model)
                via.setdefault(cid, ("plan", plan_id))
        for model in sorted(covered - sold_here):
            if model in catalogue.bare:
                via.setdefault(model, ("plan", plan_id))
    for provider in sorted(providers):
        for cid in catalogue.by_provider.get(provider, ()):
            via.setdefault(cid, ("provider", provider))
    for device_id in sorted(devices):
        fits, maybe = catalogue.device(device_id)
        for cid in sorted(fits):
            via.setdefault(cid, ("device", device_id))
        indeterminate.update(maybe)
    unknown: dict[str, tuple[str, ...]] = {}
    for cid in sorted(coverage_unknown - via.keys()):
        unknown[cid] = (COVERAGE,)
    for cid in sorted(indeterminate - via.keys()):
        unknown[cid] = (*unknown.get(cid, ()), FITS)
    for cid, (kind, hold_id) in via.items():
        if kind == "plan":
            marginal[cid] = (f"included in {hold_id}: one more task inside a plan that is not "
                             "exhausted costs nothing extra")
        elif kind == "device":
            marginal[cid] = f"runs on {hold_id}, which the caller holds: no per-task price"
    hosted = frozenset(
        cid for cid in (*via, *unknown) if cid in catalogue.bare)
    signature = frozenset((*(("row", cid) for cid in via), *(("unk", cid) for cid in unknown)))
    return Reach(via, unknown, hosted, marginal, signature)


def check(estate: Estate, snapshot: Any) -> None:
    """Refuse an id the vocabulary does not know, naming where it sits in the spec."""
    registry = default_registry()
    providers = {p.id for p in registry.providers()}
    plans = {plan["id"] for plan in snapshot.subscription_offerings()}
    devices = registry.allowed_values(registry.facet(FITS)) or frozenset()
    issues = []
    for field_name, noun, allowed in (
        ("providers", "provider", providers), ("plans", "plan", plans),
        ("devices", "device", devices), ("exhausted", "provider or plan", providers | plans),
    ):
        for index, value in enumerate(getattr(estate, field_name)):
            if value not in allowed:
                issues.append(Issue(
                    None, f"estate.{field_name}", f"unknown {noun} ID: {value}",
                    f"estate.{field_name}[{index}]"))
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


def _mark(computed: Any, cid: str, via: tuple[str, str]) -> EstateMark:
    kind, hold_id = via
    cost = None
    if kind == "provider":
        fact = computed.fact(cid, "offering.cost_per_task")
        cost = fact.value if fact.state == "known" else None
    else:
        cost = 0
    return EstateMark(
        via=EstateHold(kind=kind, id=hold_id), cost_basis=_COST_BASIS[kind],
        marginal_cost_per_task_usd=cost)


def _summary(same: bool, unrestricted: list[str], held_models: list[str],
             unreachable: list[str]) -> str:
    if not held_models:
        return ("What you hold reaches no model that qualifies. Unrestricted, the best is "
                + (unrestricted[0] if unrestricted else "none") + ".")
    if same:
        return f"What you hold reaches the unrestricted answer, {held_models[0]}."
    names = ", ".join(unreachable[:5])
    more = len(unreachable) - 5
    tail = f" and {more} more" if more > 0 else ""
    lead = unrestricted[0] if unrestricted else "none"
    return (f"Unrestricted, the best is {lead}. With what you hold it is {held_models[0]}; "
            f"{len(unreachable)} better-ranked model(s) are outside your estate: {names}{tail}.")


def with_estate(
    estate: Estate,
    snapshot: Any,
    unrestricted: Ran,
    run: Run,
    limit: int,
) -> WithEstate:
    """The reply's ``with_estate`` block."""
    catalogue = Catalogue(snapshot)
    providers, plans, devices = held(estate)
    current = reach(catalogue, providers, plans, devices)
    ran = run(current, limit)
    decision = ran.decision

    results = [
        EstateResult(
            rank=row.rank, offering=row.offering, soft_penalty=row.soft_penalty,
            warnings=row.warnings,
            estate=_mark(ran.computed, cid, current.via[cid]))
        for row, cid in zip(decision.results, ran.rows, strict=True)
    ]
    same = _answered(unrestricted) == _answered(ran)
    best = unrestricted.models
    if ran.models and ran.models[0] in best:
        best = best[: best.index(ran.models[0])]
    unreachable = [m for m in best if m not in set(ran.models)]
    gap = EstateGap(
        same_answer=same, unreachable_models=unreachable,
        summary=_summary(same, unrestricted.models, ran.models, unreachable))
    gain = _gain(catalogue, estate, (providers, plans, devices), current, ran, run)
    return WithEstate(
        status=decision.status, answer=decision.answer, results=results,
        may_qualify=decision.may_qualify, truncated=decision.truncated, gap=gap, gain=gain)


def _gain(catalogue, estate, holds, current, ran, run):
    providers, plans, devices = holds
    base = _answered(ran)
    candidates: list[tuple[EstateHold, Reach]] = []
    for provider in catalogue.offered_providers():
        if provider not in providers and provider not in estate.exhausted:
            candidates.append((
                EstateHold(kind="provider", id=provider),
                reach(catalogue, providers | {provider}, plans, devices)))
    for plan_id in sorted(catalogue.plans):
        provider = plan_id.partition("/subscription/")[0]
        if (plan_id in plans or plan_id in estate.exhausted or provider in estate.exhausted
                or plan_id in estate.plans):
            continue
        candidates.append((
            EstateHold(kind="plan", id=plan_id),
            reach(catalogue, providers, plans | {plan_id}, devices)))
    registry = default_registry()
    for device_id in sorted(registry.allowed_values(registry.facet(FITS)) or ()):
        if device_id not in devices:
            candidates.append((
                EstateHold(kind="device", id=device_id),
                reach(catalogue, providers, plans, devices | {device_id})))
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


