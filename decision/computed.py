"""Facets the engine computes for one decision (MODEL-153).

A computed facet (``computed_by`` in ``registry/facets.yaml``) is never stored
in a snapshot: its value depends on the spec. ``offering.cost_per_task`` is the
offering's list price for one task at the spec's ``task_tokens``:

    (offering.price.input × input + offering.price.output × output) / 1,000,000

It is unknown when either price is unknown, and for a row only a subscription
plan reaches (MODEL-200): a plan has no per-task price. ``offering.plan.price_monthly``
is the monthly price of the cheapest plan reaching a row on the spec's
``access``, unknown without one. ``with_computed`` wraps a loaded
snapshot so the filter, the optimiser and the explanations read the computed
value exactly as they read a stored one, and can ask ``computed()`` for the
records and the formula behind it.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from decision.contract import TaskTokens
from decision.hardware import (
    DECODE_EFFICIENCY_HIGH, DECODE_EFFICIENCY_LOW, DECODE_TPS, HARDWARE_FACETS,
    WEIGHTS_GB, DeviceInput, compute_fit, decode_estimate,
)
from decision.snapshot import UNKNOWN, Bitset3, FactValue, _FacetBitsets, _holds
from pipeline.hardware import BANDWIDTH_EFFICIENCY, QUANT_BYTES, WORKING_ALLOWANCE

COST_PER_TASK = "offering.cost_per_task"
PLAN_PRICE_MONTHLY = "offering.plan.price_monthly"
COMPUTED_FACETS = (COST_PER_TASK, PLAN_PRICE_MONTHLY, *HARDWARE_FACETS)
_PRICE_INPUT = "offering.price.input"
_PRICE_OUTPUT = "offering.price.output"
_DELEGATED_METHODS = frozenset({
    "candidates", "model_of", "kind", "lifecycle", "evidence", "capability_estimate",
    "capability_drivers", "record", "source_url",
})


@dataclass(frozen=True)
class Computed:
    """A computed value, the snapshot records it came from, and how."""

    value: float | None
    records: tuple[str, ...]
    sources: tuple[str, ...]
    formula: str


@dataclass(frozen=True)
class HardwareComputed(Computed):
    device: str
    quantisation: str | None
    interval: tuple[float, float] | None = None
    unknown_reason: str | None = None


def _price(fact: FactValue) -> float | None:
    value = fact.value
    if fact.state != "known" or isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return float(value)


def _number(value: float) -> str:
    return f"{round(value, 10):,.10g}"


class ComputedFacets:
    """A snapshot index that also answers the computed facets for one spec."""

    def __init__(
        self, base: Any, task_tokens: TaskTokens, marginal: Mapping[str, str] | None = None,
        unpriced: frozenset[str] = frozenset(), plan_prices: Mapping[str, Computed] | None = None,
        devices: tuple[str, ...] = (), hardware_context: bool = False,
        scalar_device: str | None = None,
    ) -> None:
        self._base = base
        self.task_tokens = task_tokens
        self._marginal = marginal or {}
        self._unpriced = unpriced
        self._plan_prices = plan_prices or {}
        self.devices = devices
        self.hardware_context = hardware_context
        self.scalar_device = scalar_device
        self._hardware: dict[str, dict[str, tuple[HardwareComputed, ...]]] = {}
        self._values: dict[str, Computed | None] = {}
        self._columns: dict[str, _FacetBitsets] = {}

    def __getattr__(self, name: str) -> Any:
        value = getattr(self._base, name)
        # Bind unchanged methods on first use. Minimal index implementations
        # need only the methods the decision actually calls.
        if name in _DELEGATED_METHODS:
            setattr(self, name, value)
        return value

    def computed(self, cid: str, facet_id: str) -> Computed | None:
        """The computed value of ``facet_id`` for ``cid``, or ``None`` when unknown
        or when ``facet_id`` is not computed."""
        if facet_id == PLAN_PRICE_MONTHLY:
            return self._plan_prices.get(cid)
        if facet_id in HARDWARE_FACETS:
            rows = self.hardware_estimates(cid)[facet_id]
            return next((row for row in rows if row.device == self.scalar_device), None)
        if facet_id != COST_PER_TASK:
            return None
        if cid in self._marginal:
            return Computed(0.0, (), (), self._marginal[cid])
        if cid in self._unpriced:
            return None
        if cid not in self._values:
            self._values[cid] = self._cost_per_task(cid)
        return self._values[cid]

    def _cost_per_task(self, cid: str) -> Computed | None:
        inputs = self._base.fact(cid, _PRICE_INPUT)
        outputs = self._base.fact(cid, _PRICE_OUTPUT)
        price_in, price_out = _price(inputs), _price(outputs)
        if price_in is None or price_out is None:
            return None
        tokens = self.task_tokens
        value = round((price_in * tokens.input + price_out * tokens.output) / 1_000_000, 12)
        formula = (
            f"({_number(price_in)} USD per 1M input tokens × {tokens.input:,} input tokens"
            f" + {_number(price_out)} USD per 1M output tokens × {tokens.output:,} output tokens)"
            f" ÷ 1,000,000 = {_number(value)} USD per task"
        )
        records = tuple(r for r in (inputs.record_id, outputs.record_id) if r)
        sources = tuple(dict.fromkeys((*inputs.sources, *outputs.sources)))
        return Computed(value, records, sources, formula)

    def hardware_estimates(self, cid: str) -> dict[str, tuple[HardwareComputed, ...]]:
        """One estimate per explicitly named device, including unknown reasons."""
        model_id = self._base.model_of(cid)
        if model_id not in self._hardware:
            rows: dict[str, list[HardwareComputed]] = {facet: [] for facet in HARDWARE_FACETS}
            for device in self.devices:
                for facet, estimate in self._device_estimates(model_id, device).items():
                    rows[facet].append(estimate)
            self._hardware[model_id] = {facet: tuple(values) for facet, values in rows.items()}
        return self._hardware[model_id]

    def _device_estimates(self, cid: str, device_id: str) -> dict[str, HardwareComputed]:
        total_fact = self._base.fact(cid, "model.parameters_total")
        active_fact = self._base.fact(cid, "model.parameters_active")
        openness = self._base.fact(cid, "model.weights_openness")
        total, active = _price(total_fact), _price(active_fact)
        lookup = getattr(self._base, "hardware_device", None)
        device = None if lookup is None else lookup(device_id)
        memory_records = tuple(rid for rid in (total_fact.record_id, openness.record_id,
                                               None if device is None else device["record_id"]) if rid)
        sources = tuple(dict.fromkeys((*total_fact.sources, *openness.sources,
                                      *(() if device is None else device["source_ids"]))))

        def unknown(reason, capacity_assumption="device capacity and usable memory are unknown"):
            return {facet: HardwareComputed(
                        None, memory_records, sources,
                        f"Estimate for {device_id}: unknown; {capacity_assumption}.",
                        device_id, None, unknown_reason=reason)
                    for facet in HARDWARE_FACETS}

        if device is None:
            return unknown("snapshot has no device memory specifications for this SKU")
        if device.get("unknown_reason"):
            return unknown(device["unknown_reason"])
        capacity = device["memory_capacity_gb"]
        usable = capacity * (1 - WORKING_ALLOWANCE)
        capacity_assumption = (
            f"device capacity {_number(capacity)} GB, largest listed memory configuration;"
            f" usable memory {_number(capacity)} × (1 - {WORKING_ALLOWANCE:g})"
            f" = {_number(usable)} GB")
        if total is not None and total <= 0:
            return unknown("verified total parameter count must be positive", capacity_assumption)
        fit = compute_fit(
            weights_openness=openness.value if openness.state == "known" else None,
            parameters_total=total,
            devices=[DeviceInput(device_id, capacity, device["single_device_fit"],
                                 device["refusal_reason"])],
        ).devices[device_id]
        if fit.best_quant is None:
            reason = fit.reason
            if fit.fits is False and total is not None and fit.usable_memory_gb is not None:
                reason += (f"; even q4 needs {_number(total * QUANT_BYTES['q4'] / 1e9)} GB"
                           f" of weights, above {_number(fit.usable_memory_gb)} GB usable")
            return unknown(reason, capacity_assumption)

        quant = fit.best_quant
        bytes_per_param = QUANT_BYTES[quant]
        # Significant figures preserve tiny models, including 616k-param bf16
        # weights, while avoiding false precision in a device estimate.
        weights = float(f"{fit.weights_gb:.3g}")
        assumption = (f"Estimate for {device_id}, highest-quality fitting quantisation {quant}"
                      f" at {bytes_per_param:g} bytes/parameter; {capacity_assumption}")
        memory_formula = (
            f"{assumption}: parameters_total {_number(total)} × {bytes_per_param:g} / 1e9"
            f" = {_number(weights)} GB weights, rounded to 3 significant figures."
            " KV cache is inside the allowance; snapshot has no layer/head geometry."
            " This does not establish fit for a particular context workload."
        )
        result = {
            WEIGHTS_GB: HardwareComputed(weights, memory_records, sources, memory_formula, device_id, quant),
        }
        speed_records = tuple(dict.fromkeys((*memory_records,
                                             *((active_fact.record_id,) if active_fact.record_id else ()))))
        speed_sources = tuple(dict.fromkeys((*sources, *active_fact.sources)))
        bandwidth = device["memory_bandwidth_gb_s"]
        if active is None or active <= 0:
            reason = "verified positive parameters_active is missing; no fallback to parameters_total"
            speed = HardwareComputed(None, speed_records, speed_sources,
                                     f"{assumption}: decode speed unknown.",
                                     device_id, quant, unknown_reason=reason)
        elif bandwidth is None:
            reason = "sourced memory.bandwidth_gb_s is missing"
            speed = HardwareComputed(None, speed_records, speed_sources,
                                     f"{assumption}: decode speed unknown.",
                                     device_id, quant, unknown_reason=reason)
        else:
            point, interval = decode_estimate(bandwidth, active, quant)
            formula = (
                f"{assumption}: memory.bandwidth_gb_s {_number(bandwidth)} ×"
                f" {BANDWIDTH_EFFICIENCY:g} / (parameters_active {_number(active)} ×"
                f" {bytes_per_param:g} / 1e9) = {point:g} tokens/s. Efficiency band"
                f" {DECODE_EFFICIENCY_LOW:g} to {DECODE_EFFICIENCY_HIGH:g} gives"
                f" {interval[0]:g} to {interval[1]:g} tokens/s; scenario bounds, not measurements"
                " or a confidence interval. Bandwidth roofline omits compute, routing and contention."
            )
            speed = HardwareComputed(point, speed_records, speed_sources, formula, device_id, quant, interval)
        result[DECODE_TPS] = speed
        return result

    # SnapshotIndex -----------------------------------------------------------

    def fact(self, cid: str, facet_id: str) -> FactValue:
        if facet_id not in COMPUTED_FACETS:
            return self._base.fact(cid, facet_id)
        found = self.computed(cid, facet_id)
        return (UNKNOWN if found is None or found.value is None
                else FactValue("known", found.value, found.sources))

    def ids_where(self, facet_id: str, op: str, arg: Any) -> Bitset3:
        if facet_id not in COMPUTED_FACETS:
            return self._base.ids_where(facet_id, op, arg)
        ids = self._base.candidates()
        everyone = (1 << len(ids)) - 1
        if facet_id not in self._columns:
            rows = []
            for row, cid in enumerate(ids):
                found = self.computed(cid, facet_id)
                if found is not None and found.value is not None:
                    rows.append((row, found.value))
            self._columns[facet_id] = _FacetBitsets(rows)
        column = self._columns[facet_id]
        if op == "known":
            return Bitset3(column.known, everyone & ~column.known, 0)
        passing = column.passing(op, arg)
        if passing is None:
            passing = 0
            for row, cid in enumerate(ids):
                found = self.computed(cid, facet_id)
                if found is not None and found.value is not None and _holds(found.value, op, arg):
                    passing |= 1 << row
        return Bitset3(passing, column.known & ~passing, everyone & ~column.known)


def with_computed(
    snapshot: Any, task_tokens: TaskTokens, marginal: Mapping[str, str] | None = None,
    unpriced: frozenset[str] = frozenset(), plan_prices: Mapping[str, Computed] | None = None,
    *, devices: tuple[str, ...] = (), hardware_context: bool = False,
    scalar_device: str | None = None,
) -> ComputedFacets:
    """``snapshot``, answering the computed facets at ``task_tokens``.

    ``marginal`` maps a row the caller already pays for (an estate plan or
    device, MODEL-179) to the reason one more task costs nothing; that row's
    ``offering.cost_per_task`` is 0 instead of its list price. ``unpriced`` rows
    have no per-task price at all, and ``plan_prices`` gives
    ``offering.plan.price_monthly`` (MODEL-200).
    """
    if isinstance(snapshot, ComputedFacets):
        snapshot = snapshot._base
    return ComputedFacets(snapshot, task_tokens, marginal, unpriced, plan_prices,
                          devices, hardware_context, scalar_device)
