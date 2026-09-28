"""Facets the engine computes for one decision (MODEL-153).

A computed facet (``computed_by`` in ``registry/facets.yaml``) is never stored
in a snapshot: its value depends on the spec. ``offering.cost_per_task`` is the
offering's list price for one task at the spec's ``task_tokens``:

    (offering.price.input × input + offering.price.output × output) / 1,000,000

It is unknown when either price is unknown. ``with_computed`` wraps a loaded
snapshot so the filter, the optimiser and the explanations read the computed
value exactly as they read a stored one, and can ask ``computed()`` for the
records and the formula behind it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from decision.contract import TaskTokens
from decision.snapshot import UNKNOWN, Bitset3, FactValue, _FacetBitsets, _holds

COST_PER_TASK = "offering.cost_per_task"
COMPUTED_FACETS = (COST_PER_TASK,)
_PRICE_INPUT = "offering.price.input"
_PRICE_OUTPUT = "offering.price.output"


@dataclass(frozen=True)
class Computed:
    """A computed value, the snapshot records it came from, and how."""

    value: float
    records: tuple[str, ...]
    sources: tuple[str, ...]
    formula: str


def _price(fact: FactValue) -> float | None:
    value = fact.value
    if fact.state != "known" or isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return float(value)


def _number(value: float) -> str:
    return f"{round(value, 10):,.10g}"


class ComputedFacets:
    """A snapshot index that also answers the computed facets for one spec."""

    def __init__(self, base: Any, task_tokens: TaskTokens) -> None:
        self._base = base
        self.task_tokens = task_tokens
        self._values: dict[str, Computed | None] = {}
        self._column: _FacetBitsets | None = None

    def __getattr__(self, name: str) -> Any:
        return getattr(self._base, name)

    def computed(self, cid: str, facet_id: str) -> Computed | None:
        """The computed value of ``facet_id`` for ``cid``, or ``None`` when unknown
        or when ``facet_id`` is not computed."""
        if facet_id != COST_PER_TASK:
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

    # SnapshotIndex -----------------------------------------------------------

    def fact(self, cid: str, facet_id: str) -> FactValue:
        if facet_id not in COMPUTED_FACETS:
            return self._base.fact(cid, facet_id)
        found = self.computed(cid, facet_id)
        return UNKNOWN if found is None else FactValue("known", found.value, found.sources)

    def ids_where(self, facet_id: str, op: str, arg: Any) -> Bitset3:
        if facet_id not in COMPUTED_FACETS:
            return self._base.ids_where(facet_id, op, arg)
        ids = self._base.candidates()
        everyone = (1 << len(ids)) - 1
        if self._column is None:
            rows = []
            for row, cid in enumerate(ids):
                found = self.computed(cid, facet_id)
                if found is not None:
                    rows.append((row, found.value))
            self._column = _FacetBitsets(rows)
        column = self._column
        if op == "known":
            return Bitset3(column.known, everyone & ~column.known, 0)
        passing = column.passing(op, arg)
        if passing is None:
            passing = 0
            for row, cid in enumerate(ids):
                found = self.computed(cid, facet_id)
                if found is not None and _holds(found.value, op, arg):
                    passing |= 1 << row
        return Bitset3(passing, column.known & ~passing, everyone & ~column.known)


def with_computed(snapshot: Any, task_tokens: TaskTokens) -> ComputedFacets:
    """``snapshot``, answering the computed facets at ``task_tokens``."""
    if isinstance(snapshot, ComputedFacets):
        snapshot = snapshot._base
    return ComputedFacets(snapshot, task_tokens)
