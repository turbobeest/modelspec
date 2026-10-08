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

from decision.contract import EvidenceQualifiers, Objective, Preference, Tolerance
from decision.refinements import is_refinement_key

NO_COMPLETE_OBJECTIVE_VALUES = "no complete objective values"
# Every reason string ``optimise`` returns with status ``no_feasible``.
OPTIMISER_DIAGNOSTICS = frozenset({
    NO_COMPLETE_OBJECTIVE_VALUES,
})
#: User-facing ``relax`` text when the gates left candidates and none has an
#: objective value. The engine appends the objective's name.
OBJECTIVE_GAP_PREFIX = "no model that meets the requirements has a value for "

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


#: Same cutoff as ``n()`` in ``web/src/decide/engine/reference.ts``.
SPAN_EPSILON = 1e-9


@dataclass(frozen=True)
class Normalisation:
    minimum: float | None
    maximum: float | None
    direction: Literal["max", "min"]

    def zero_span(self) -> bool:
        """One known value, or known values equal within the reference cutoff."""
        low, high = self.minimum, self.maximum
        return low is not None and high is not None and high - low < SPAN_EPSILON

    def constant(self) -> float:
        """The reference ranker's zero-span value, after direction.

        ``n()`` returns 1 when the span is zero. A maximum uses that value.
        A minimum, including cost, uses ``1 - n``.
        """
        return 1.0 if self.direction == "max" else 0.0


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
    preference_status: Literal["satisfied", "not_satisfied", "unknown"] | None = None
    preferred_value: bool | int | float | date | str | None = None
    interval: tuple[float, float] | None = None


@dataclass(frozen=True)
class OptimisedResult:
    candidate_id: str
    contributions: tuple[DimensionContribution, ...]
    score: float | None
    soft_penalty: float
    penalties: tuple[tuple[str, float], ...]
    warnings: tuple[str, ...] = ()
    score_interval: tuple[float, float] | None = None


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


def _normalise(value: float, normalisation: Normalisation) -> float:
    low, high = normalisation.minimum, normalisation.maximum
    assert low is not None and high is not None
    if normalisation.zero_span():
        return normalisation.constant()
    scaled = (value - low) / (high - low)
    return 1 - scaled if normalisation.direction == "min" else scaled


def _transform_interval(
    point: float, raw_low: float, raw_high: float, normalisation: Normalisation,
) -> tuple[float, float]:
    """The dimensionless interval. A zero point-span uses this candidate's raw width."""
    if normalisation.zero_span():
        constant = normalisation.constant()
        width = raw_high - raw_low
        if width < SPAN_EPSILON:
            return constant, constant
        sign = 1.0 if normalisation.direction == "max" else -1.0
        low = constant + sign * (raw_low - point) / width
        high = constant + sign * (raw_high - point) / width
        return (low, high) if low <= high else (high, low)
    transformed = sorted((
        _normalise(raw_low, normalisation),
        _normalise(raw_high, normalisation),
    ))
    return transformed[0], transformed[1]


def _raw_interval(
    value: float,
    evidence: tuple[EvidenceValue, ...],
    estimate: CapabilityEstimateValue | None,
    measured: tuple[float, float] | None = None,
) -> tuple[float, float]:
    if estimate is not None:
        return estimate.low, estimate.high
    if (
        len(evidence) == 1
        and evidence[0].interval is not None
    ):
        return evidence[0].interval
    if measured is not None:
        return measured
    return value, value


def _dimensions(
    objective: Objective,
) -> list[tuple[str, float, Tolerance | None, Preference | None]]:
    if objective.weights is not None:
        return [
            (key, term.weight if isinstance(term, Preference) else term, None,
             term if isinstance(term, Preference) else None)
            for key, term in sorted(objective.weights.items())
        ]
    if objective.pareto is not None:
        return [(key, 1, None, None) for key in sorted(objective.pareto)]
    if objective.lexicographic is not None:
        return [(step.max or f"-{step.min}", 1, step.within, None)
                for step in objective.lexicographic]
    return [(objective.max or f"-{objective.min}", 1, None, None)]


def _adjusted(row: OptimisedResult, i: int) -> float:
    value = row.contributions[i].value
    assert value is not None
    return value - row.soft_penalty


def _lex_order(rows: list[OptimisedResult],
               dimensions: list[tuple[str, float, Tolerance | None, Preference | None]],
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
              tuple[float, float] | None,
          ]:
    """The value, its sources, evidence, estimate and a measured fact's interval."""
    if is_refinement_key(facet):
        nested = snapshot.refinement_estimate(cid, facet)
        if nested is None:
            return None, (), (), None, None
        return nested.estimate.value, (), (), nested.estimate, None
    if facet in domains and selector is None:
        estimate = snapshot.capability_estimate(cid, facet)
        return ((None, (), (), None, None) if estimate is None
                else (estimate.value, (), (), estimate, None))
    if selector is None:
        fact = snapshot.fact(cid, facet)
        value = _number(fact.value) if fact.state == "known" else None
        return value, fact.sources, (), None, fact.interval if value is not None else None
    if selector.direct and not snapshot.direct_for(selector.benchmark_id, selector.domains):
        return None, (), (), None, None
    evidence = snapshot.evidence(
        cid, selector.benchmark_id,
        measured_by=set(selector.measured_by) if selector.measured_by is not None else None,
        effort=selector.effort, harness=selector.harness, after=selector.after)
    matches = [e for e in evidence if e.verified and not e.quality_flags
               and _number(e.value) is not None
               and (selector.version is None or e.version == selector.version)
               and e.subcategory == selector.subcategory]
    # Multiple measurements need a resolver decision, not an implicit max or average.
    if len(matches) != 1:
        return None, (), (), None, None
    item = matches[0]
    return float(item.value), tuple(item.source_ids), (item,), None, None


def optimise(snapshot: SnapshotIndex, candidates: Sequence[str], objective: Objective, *,
             penalties: Mapping[str, Mapping[str, float]] | None = None,
             evidence_selectors: Mapping[str, EvidenceSelector] | None = None,
             domains: set[str] | frozenset[str] = frozenset()) -> Optimisation:
    """Order complete candidates first; ID breaks exact ties without adding a bonus.

    All dimensions use feasible-set min-max values, which are dimensionless.
    A zero span maps to 1 when the dimension is maximised and to 0 when it is
    minimised, matching the reference ranker. The interval then uses that
    candidate's own raw width, so uncertainty does not collapse to a point.
    Weights are used as supplied, not rescaled to sum to one. Penalties are
    subtracted once from a scalar total, or from each lexicographic/Pareto dimension.
    Tolerances are in raw units, converted to normalised units before grouping.
    The resolver must supply all domain objective IDs in ``domains`` and bind
    benchmark objectives through ``evidence_selectors``. Neither is inferred from
    spelling. Penalties map candidate IDs to condition IDs and incurred amounts.
    """
    dimensions = _dimensions(objective)
    selectors = evidence_selectors or {}
    estimate_lookup = getattr(snapshot, "capability_estimate", None)
    gaps = []
    for signed, _, _, preference in dimensions:
        facet = signed.removeprefix("-")
        if preference is not None or facet not in domains or facet in selectors:
            continue
        if estimate_lookup is None or not any(
            estimate_lookup(cid, facet) is not None for cid in candidates
        ):
            gaps.append(facet)
    if gaps:
        # No candidate has an estimate. They passed the gates, so they stay
        # visible as missing the objective rather than disappearing.
        if not candidates:
            return Optimisation("no_feasible", (), NO_COMPLETE_OBJECTIVE_VALUES)
        missing = tuple(sorted(set(candidates)))
        return Optimisation(
            "no_feasible", (), NO_COMPLETE_OBJECTIVE_VALUES,
            missing=missing,
            unknown={cid: tuple(gaps) for cid in missing},
        )
    cids = sorted(set(candidates))
    contributions: dict[str, list[DimensionContribution]] = {cid: [] for cid in cids}
    for signed, weight, _, preference in dimensions:
        if not isfinite(weight):
            raise ValueError("weights must be finite")
        facet = signed.removeprefix("-")
        if preference is not None:
            norm = Normalisation(0.0, 1.0, "max")
            for cid in cids:
                fact = snapshot.fact(cid, facet)
                if fact.state == "known":
                    satisfied = fact.value == preference.prefer
                    raw_value = 1.0 if satisfied else 0.0
                    status: Literal["satisfied", "not_satisfied", "unknown"] = (
                        "satisfied" if satisfied else "not_satisfied"
                    )
                    sources = fact.sources
                else:
                    raw_value = None
                    status = "unknown"
                    sources = ()
                pref_value = 0.0 if status == "unknown" else raw_value
                contributions[cid].append(DimensionContribution(
                    signed,
                    raw_value,
                    pref_value,
                    weight,
                    norm,
                    sources,
                    (),
                    None,
                    status,
                    preference.prefer,
                    (pref_value, pref_value),
                ))
            continue
        readings = {
            cid: _read(snapshot, cid, facet, selectors.get(facet), domains) for cid in cids
        }
        raw = {cid: reading[0] for cid, reading in readings.items()}
        known = [v for v in raw.values() if v is not None]
        low, high = (min(known), max(known)) if known else (None, None)
        norm = Normalisation(
            low, high, "min" if signed.startswith("-") else "max",
        )
        for cid, value in raw.items():
            normalised = None
            interval = None
            if value is not None:
                normalised = _normalise(value, norm)
                raw_low, raw_high = _raw_interval(
                    value,
                    readings[cid][2],
                    readings[cid][3],
                    readings[cid][4],
                )
                # Do not clamp. Values beyond the feasible point-estimate range
                # carry uncertainty the answer bands need. A zero point-span
                # stays dimensionless and uses this candidate's raw width.
                interval = _transform_interval(value, raw_low, raw_high, norm)
            contributions[cid].append(DimensionContribution(
                signed, value, normalised, weight, norm, readings[cid][1], readings[cid][2],
                readings[cid][3], interval=interval))
    complete, missing = [], []
    for cid in cids:
        parts = tuple(sorted((penalties or {}).get(cid, {}).items()))
        if any(not isfinite(p) or p < 0 for _, p in parts):
            raise ValueError("penalties must be finite and nonnegative")
        penalty = sum(p for _, p in parts)
        values = contributions[cid]
        unknown = any(c.value is None for c in values)
        preference_unknown = any(c.preference_status == "unknown" for c in values)
        scalar = objective.lexicographic is None and objective.pareto is None
        score = sum(c.value * c.weight for c in values) - penalty if not unknown else None
        warnings = (
            (("missing_objective_value",) if unknown else ())
            + (("unknown_preference_value",) if preference_unknown else ())
        )
        score_interval = None
        if scalar and not unknown:
            score_interval = (
                sum(c.interval[0] * c.weight for c in values) - penalty,
                sum(c.interval[1] * c.weight for c in values) - penalty,
            )
        row = OptimisedResult(cid, tuple(values), score if scalar else None, penalty, parts,
                              warnings, score_interval)
        (missing if unknown else complete).append(row)
    missing_ids = tuple(row.candidate_id for row in missing)
    unknown = {row.candidate_id: tuple(c.dimension.removeprefix("-")
                                       for c in row.contributions if c.value is None)
               for row in missing}
    if not complete:
        return Optimisation("no_feasible", (), NO_COMPLETE_OBJECTIVE_VALUES, missing=missing_ids,
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
