"""Slice-1 optimisation over filtered candidates, without capability blending.

The resolver supplies evidence selectors and domain IDs because Objective v1
contains facet IDs only. This module returns stage values, not a Decision:
MODEL-145 resolves offering identities and registered source IDs for transport.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from math import isclose, isfinite
from typing import TYPE_CHECKING, Literal

from decision.contract import EvidenceQualifiers, Objective, Tolerance

if TYPE_CHECKING:
    from decision.snapshot import CapabilityEstimateValue, EvidenceValue, SnapshotIndex


@dataclass(frozen=True)
class EvidenceSelector:
    """A resolver's explicit benchmark selector; omitted subcategory means aggregate."""

    benchmark_id: str
    version: str | None = None
    subcategory: str | None = None
    measured_by: frozenset[str] | None = None
    effort: str | None = None
    harness: str | None = None
    after: date | None = None
    direct: bool = False
    #: The capabilities asked about; ``direct`` is relative to them.
    domains: frozenset[str] = frozenset()

    @classmethod
    def from_qualifiers(
        cls, benchmark_id: str, qualifiers: EvidenceQualifiers | None,
        domains: frozenset[str] = frozenset(),
    ) -> EvidenceSelector:
        qualifiers = qualifiers or EvidenceQualifiers()
        measured = {
            "independent": frozenset({
                "benchmark_author",
                "independent",
                "independent_evaluator",
                "modelspec",
                "outcome_protocol",
            }),
            "provider_self_report": frozenset({"provider_self_report"}),
            "any": None,
            None: None,
        }[qualifiers.measured_by]
        return cls(
            benchmark_id=benchmark_id,
            measured_by=measured,
            effort=qualifiers.effort,
            harness=qualifiers.harness,
            after=qualifiers.measured_after,
            direct=qualifiers.direct,
            domains=frozenset(domains),
        )


@dataclass(frozen=True)
class Normalisation:
    minimum: float | None
    maximum: float | None
    direction: Literal["max", "min"]


@dataclass(frozen=True)
class DimensionContribution:
    dimension: str
    raw_value: float | None
    value: float | None
    weight: float
    normalisation: Normalisation
    sources: tuple[str, ...] = ()
    evidence: tuple[EvidenceValue, ...] = ()
    estimate: CapabilityEstimateValue | None = None


@dataclass(frozen=True)
class OptimisedResult:
    candidate_id: str
    contributions: tuple[DimensionContribution, ...]
    score: float | None
    soft_penalty: float
    penalties: tuple[tuple[str, float], ...]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class WeightTippingPoint:
    """Infimum of positive single-weight changes; cross in the stated direction.

    At the threshold scores tie, so candidate ID may retain the incumbent.
    Other weights and feasible-set normalisation remain fixed.
    """

    dimension: str
    threshold: float
    direction: Literal["increase", "decrease"]
    change: float
    new_top: str


@dataclass(frozen=True)
class Optimisation:
    """Ordered stage results, with the nearest weight crossing first.

    For Pareto, dominance maps each excluded complete candidate to every candidate
    that is at least as good in all penalty-adjusted dimensions and better in one.
    Missing candidates cannot establish Pareto membership and are listed separately.
    """

    status: Literal["answered", "partial", "no_feasible"]
    results: tuple[OptimisedResult, ...]
    reason: str | None = None
    dominance: dict[str, tuple[str, ...]] = field(default_factory=dict)
    missing: tuple[str, ...] = ()
    tipping_points: tuple[WeightTippingPoint, ...] = ()
    #: Each missing candidate's objective facets without a value, unsigned.
    unknown: dict[str, tuple[str, ...]] = field(default_factory=dict)


def _number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return float(value) if isfinite(value) else None


def _dimensions(objective: Objective) -> list[tuple[str, float, Tolerance | None]]:
    if objective.weights is not None:
        return [(key, weight, None) for key, weight in sorted(objective.weights.items())]
    if objective.pareto is not None:
        return [(key, 1, None) for key in sorted(objective.pareto)]
    if objective.lexicographic is not None:
        return [(step.max or f"-{step.min}", 1, step.within)
                for step in objective.lexicographic]
    return [(objective.max or f"-{objective.min}", 1, None)]


def _adjusted(row: OptimisedResult, i: int) -> float:
    value = row.contributions[i].value
    assert value is not None
    return value - row.soft_penalty


def _lex_order(rows: list[OptimisedResult],
               dimensions: list[tuple[str, float, Tolerance | None]],
               depth: int = 0) -> list[OptimisedResult]:
    if depth == len(dimensions):
        return sorted(rows, key=lambda row: row.candidate_id)
    remaining = sorted(rows, key=lambda row: (-_adjusted(row, depth), row.candidate_id))
    ordered = []
    tolerance = dimensions[depth][2]
    while remaining:
        best = remaining[0]
        width = 0.0
        norm = best.contributions[depth].normalisation
        span = norm.maximum - norm.minimum
        if tolerance is not None and span:
            raw_best = best.contributions[depth].raw_value
            width = (tolerance.absolute if tolerance.absolute is not None
                     else abs(raw_best) * tolerance.relative) / span
        cutoff = _adjusted(best, depth) - width
        group = [row for row in remaining if _adjusted(row, depth) >= cutoff
                 or (tolerance is not None
                     and isclose(_adjusted(row, depth), cutoff, rel_tol=0, abs_tol=1e-15))]
        ordered.extend(_lex_order(group, dimensions, depth + 1))
        remaining = remaining[len(group):]
    return ordered


def _tipping_points(rows: list[OptimisedResult]) -> tuple[WeightTippingPoint, ...]:
    winner = rows[0]
    points = []
    for i, contribution in enumerate(winner.contributions):
        for direction, sign in (("increase", 1), ("decrease", -1)):
            crossings = []
            for challenger in rows[1:]:
                slope = challenger.contributions[i].value - contribution.value
                if sign * slope <= 0:
                    continue
                delta = (winner.score - challenger.score) / slope
                threshold = contribution.weight + delta
                if threshold <= 0 or not isfinite(threshold):
                    continue
                crossings.append((abs(delta), -sign * slope, challenger.candidate_id, threshold))
            if crossings:
                change, _, cid, threshold = min(crossings)
                points.append(WeightTippingPoint(contribution.dimension, threshold,
                                                direction, change, cid))
    return tuple(sorted(points, key=lambda p: (p.change, p.dimension, p.direction, p.new_top)))


def _read(snapshot: SnapshotIndex, cid: str, facet: str,
          selector: EvidenceSelector | None, domains: set[str] | frozenset[str]
          ) -> tuple[
              float | None,
              tuple[str, ...],
              tuple[EvidenceValue, ...],
              CapabilityEstimateValue | None,
          ]:
    if facet in domains and selector is None:
        estimate = snapshot.capability_estimate(cid, facet)
        return (None, (), (), None) if estimate is None else (estimate.value, (), (), estimate)
    if selector is None:
        fact = snapshot.fact(cid, facet)
        value = _number(fact.value) if fact.state == "known" else None
        return value, fact.sources, (), None
    if selector.direct and not snapshot.direct_for(selector.benchmark_id, selector.domains):
        return None, (), (), None
    evidence = snapshot.evidence(
        cid, selector.benchmark_id,
        measured_by=set(selector.measured_by) if selector.measured_by is not None else None,
        effort=selector.effort, harness=selector.harness, after=selector.after)
    matches = [e for e in evidence if e.verified and _number(e.value) is not None
               and (selector.version is None or e.version == selector.version)
               and e.subcategory == selector.subcategory]
    # Multiple measurements need a resolver decision, not an implicit max or average.
    if len(matches) != 1:
        return None, (), (), None
    item = matches[0]
    return float(item.value), tuple(item.source_ids), (item,), None


def optimise(snapshot: SnapshotIndex, candidates: Sequence[str], objective: Objective, *,
             penalties: Mapping[str, Mapping[str, float]] | None = None,
             evidence_selectors: Mapping[str, EvidenceSelector] | None = None,
             domains: set[str] | frozenset[str] = frozenset()) -> Optimisation:
    """Order complete candidates first; ID breaks exact ties without adding a bonus.

    All dimensions use feasible-set min-max values. Constant dimensions contribute
    zero. Weights are used as supplied, not rescaled to sum to one. Penalties are
    subtracted once from a scalar total, or from each lexicographic/Pareto dimension.
    Tolerances are in raw units, converted to normalised units before grouping.
    The resolver must supply all domain objective IDs in ``domains`` and bind
    benchmark objectives through ``evidence_selectors``. Neither is inferred from
    spelling. Penalties map candidate IDs to condition IDs and incurred amounts.
    """
    dimensions = _dimensions(objective)
    selectors = evidence_selectors or {}
    estimate_lookup = getattr(snapshot, "capability_estimate", None)
    for signed, _, _ in dimensions:
        facet = signed.removeprefix("-")
        if facet not in domains or facet in selectors:
            continue
        if estimate_lookup is None or not any(
            estimate_lookup(cid, facet) is not None for cid in candidates
        ):
            return Optimisation(
                "no_feasible", (),
                "specify a benchmark or wait for the capability model (MODEL-129)",
            )
    cids = sorted(set(candidates))
    contributions: dict[str, list[DimensionContribution]] = {cid: [] for cid in cids}
    for signed, weight, _ in dimensions:
        if not isfinite(weight):
            raise ValueError("weights must be finite")
        facet = signed.removeprefix("-")
        readings = {
            cid: _read(snapshot, cid, facet, selectors.get(facet), domains) for cid in cids
        }
        raw = {cid: reading[0] for cid, reading in readings.items()}
        known = [v for v in raw.values() if v is not None]
        low, high = (min(known), max(known)) if known else (None, None)
        norm = Normalisation(low, high, "min" if signed.startswith("-") else "max")
        for cid, value in raw.items():
            normalised = None
            if value is not None:
                normalised = 0.0 if high == low else (value - low) / (high - low)
                if norm.direction == "min" and high != low:
                    normalised = 1 - normalised
            contributions[cid].append(DimensionContribution(
                signed, value, normalised, weight, norm, readings[cid][1], readings[cid][2],
                readings[cid][3]))
    complete, missing = [], []
    for cid in cids:
        parts = tuple(sorted((penalties or {}).get(cid, {}).items()))
        if any(not isfinite(p) or p < 0 for _, p in parts):
            raise ValueError("penalties must be finite and nonnegative")
        penalty = sum(p for _, p in parts)
        values = contributions[cid]
        unknown = any(c.value is None for c in values)
        scalar = objective.lexicographic is None and objective.pareto is None
        score = sum(c.value * c.weight for c in values) - penalty if not unknown else None
        row = OptimisedResult(cid, tuple(values), score if scalar else None, penalty, parts,
                              ("missing_objective_value",) if unknown else ())
        (missing if unknown else complete).append(row)
    missing_ids = tuple(row.candidate_id for row in missing)
    unknown = {row.candidate_id: tuple(c.dimension.removeprefix("-")
                                       for c in row.contributions if c.value is None)
               for row in missing}
    if not complete:
        return Optimisation("no_feasible", (), "no complete objective values", missing=missing_ids,
                            unknown=unknown)
    dominance = {}
    if objective.pareto is not None:
        for row in complete:
            dominators = []
            for other in complete:
                differences = [_adjusted(other, i) - _adjusted(row, i)
                               for i in range(len(dimensions))]
                if all(d >= 0 for d in differences) and any(d > 0 for d in differences):
                    dominators.append(other.candidate_id)
            if dominators:
                dominance[row.candidate_id] = tuple(dominators)
        ordered = [row for row in complete if row.candidate_id not in dominance]
    elif objective.lexicographic is not None:
        ordered = _lex_order(complete, dimensions) + missing
    else:
        ordered = sorted(complete, key=lambda row: (-row.score, row.candidate_id)) + missing
    points = _tipping_points([row for row in ordered if row.score is not None]) \
        if objective.weights is not None else ()
    return Optimisation("partial" if missing else "answered", tuple(ordered),
                        dominance=dominance, missing=missing_ids, tipping_points=points,
                        unknown=unknown)
