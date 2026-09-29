"""Probability bands and the named blend (MODEL-206).

The model-level answer used to call a model tied with the leader when their
80% score intervals overlapped. Overlap at the edges still leaves most of the
probability on one side, so a model the evidence ranks well below the leader
read as its equal. Thin evidence read as a tie too: an interval four units
wide overlaps everything.

This module sorts the ranked models into three bands instead:

- ``best``: the leader, the best point score among models with enough
  evidence, plus every such model whose score is at least the leader's with
  probability ``BAND_PROBABILITY`` or more.
- ``rest``: the other models with enough evidence, in score order.
- ``thin``: models with a weighted capability whose 80% interval is wider
  than ``THIN_INTERVAL_WIDTH``. They are never in the leader's band.

The probability that one score is at least another's is read from the same
score posteriors ``p_best`` resamples: each model's score is normal, with the
capability terms' variance and exact terms fixed, and models are independent.
The pairwise probability has a closed form, so it is computed exactly rather
than estimated from a finite set of draws.

The blend names what the scores mix: each weighted dimension's share of the
weights, and the order on that dimension alone.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from math import erfc, sqrt

from decision.contract import (
    BandEntry,
    Bands,
    BlendTerm,
    DimensionEstimate,
    OfferingRef,
)
from decision.optimise import OptimisedResult
from decision.refinements import is_refinement_key

#: A model joins the leader's band when P(its score >= the leader's) is at
#: least this. At 0.25 the leader is ahead with at most 75% probability: the
#: evidence leans, but not enough to separate them.
BAND_PROBABILITY = 0.25
#: A model has too little evidence to band when any weighted capability's 80%
#: interval is wider than this, on the capability scale. One fresh direct
#: benchmark gives about 2.0; a model measured only on three proxy benchmarks,
#: or on one direct benchmark more than about fourteen months old, is wider
#: than 2.8. The prior alone is 5.1. See
#: docs/research/capability-interval-calibration.md.
THIN_INTERVAL_WIDTH = 2.8
BASIS = (
    f"probability bands: a model joins the leader when P(its score >= the leader's) "
    f">= {BAND_PROBABILITY} under the score posteriors; a weighted capability with an "
    f"80% interval wider than {THIN_INTERVAL_WIDTH} is not enough evidence"
)
#: A source-published measurement interval is read as a 95% interval, the usual
#: convention for leaderboard intervals; the snapshot does not record its level.
PUBLISHED_INTERVAL_Z = 1.959963984540054
_PRECISION = 4


@dataclass(frozen=True)
class Distribution:
    """A score or an estimate as a normal: its point value and its spread."""

    value: float
    sd: float


def p_at_least(challenger: Distribution, leader: Distribution) -> float:
    """P(challenger's score >= leader's) for independent normal scores."""
    spread = sqrt(challenger.sd**2 + leader.sd**2)
    if spread == 0:
        return 1.0 if challenger.value >= leader.value else 0.0
    return round(0.5 * erfc((leader.value - challenger.value) / (spread * sqrt(2))), _PRECISION)


def published_variance(row: OptimisedResult) -> float:
    """Score variance from the source-published intervals of measured objective terms."""
    variance = 0.0
    for contribution in row.contributions:
        if (contribution.estimate is None and len(contribution.evidence) == 1
                and contribution.evidence[0].interval is not None
                and contribution.interval is not None):
            low, high = contribution.interval
            variance += (contribution.weight * (high - low) / (2 * PUBLISHED_INTERVAL_Z)) ** 2
    return variance


def thin(row: OptimisedResult) -> bool:
    """Whether a weighted capability's 80% interval is wider than the threshold."""
    return any(
        contribution.estimate is not None
        and contribution.estimate.high - contribution.estimate.low > THIN_INTERVAL_WIDTH
        for contribution in row.contributions
    )


@dataclass(frozen=True)
class Banded:
    """The three bands as engine rows, one representative row per model."""

    leader: OptimisedResult | None
    best: tuple[OptimisedResult, ...]
    rest: tuple[OptimisedResult, ...]
    thin: tuple[OptimisedResult, ...]
    p_beats: Mapping[str, float]


def band(
    rows: Sequence[OptimisedResult],
    distributions: Mapping[str, Distribution],
    model_of: Callable[[str], str],
    p_best: Mapping[str, float | None],
) -> Banded:
    """Band representative rows, given best first by point score.

    ``best`` is ordered by ``p_best``, then score; ``rest`` and ``thin`` by score.
    """
    enough = [row for row in rows if not thin(row)]
    scant = tuple(row for row in rows if thin(row))
    if not enough:
        return Banded(None, (), (), scant, {})
    leader = enough[0]
    anchor = distributions[model_of(leader.candidate_id)]
    p_beats = {
        model_of(row.candidate_id): p_at_least(distributions[model_of(row.candidate_id)], anchor)
        for row in rows if row is not leader
    }
    joined = [row for row in enough[1:] if p_beats[model_of(row.candidate_id)] >= BAND_PROBABILITY]
    best = sorted(
        [leader, *joined],
        key=lambda row: (-(p_best.get(model_of(row.candidate_id)) or 0.0), -row.score,
                         model_of(row.candidate_id)),
    )
    rest = tuple(row for row in enough[1:] if row not in joined)
    return Banded(leader, tuple(best), rest, scant, p_beats)


def _capability_dimensions(row: OptimisedResult) -> list:
    return [contribution for contribution in row.contributions if contribution.estimate is not None]


def _benchmark_counts(snapshot, model_id: str, dimension: str) -> tuple[int, int]:
    """Distinct fitted benchmarks behind the model's estimate on ``dimension``: all, direct."""
    fitted = {str(item["benchmark"]) for item in snapshot.capability_items.values()}
    key = dimension.removeprefix("-")
    if is_refinement_key(key):
        tags = {
            benchmark: directness for benchmark, directness in snapshot.refinement_benchmarks(key)
            if benchmark in fitted and snapshot.evidence(model_id, benchmark)
        }
    else:
        tags = {
            row.benchmark_id: row.directness
            for row in snapshot.evidence_for_domain(model_id, key)
            if row.benchmark_id in fitted
        }
    return len(tags), sum(directness == "direct" for directness in tags.values())


def _round(value: float) -> float:
    return round(value, 6)


def entries(
    banded: Banded,
    snapshot,
    offering_ref: Callable[[str], OfferingRef],
    cost: Callable[[str], float | None],
    p_best: Mapping[str, float | None],
) -> Bands:
    """The contract view of the bands."""

    def entry(row: OptimisedResult) -> BandEntry:
        model_id = snapshot.model_of(row.candidate_id)
        low, high = row.score_interval
        return BandEntry(
            model=model_id,
            offering=offering_ref(row.candidate_id),
            score=_round(row.score),
            score_interval=(_round(low), _round(high)),
            p_best=p_best.get(model_id),
            p_beats_leader=None if row is banded.leader else banded.p_beats.get(model_id),
            cost_per_task=cost(row.candidate_id),
            estimates=[
                DimensionEstimate(
                    dimension=contribution.dimension,
                    value=contribution.estimate.value,
                    interval=(contribution.estimate.low, contribution.estimate.high),
                    benchmarks=counts[0],
                    direct_benchmarks=counts[1],
                )
                for contribution in _capability_dimensions(row)
                for counts in [_benchmark_counts(snapshot, model_id, contribution.dimension)]
            ],
        )

    return Bands(
        basis=BASIS,
        band_probability=BAND_PROBABILITY,
        thin_interval_width=THIN_INTERVAL_WIDTH,
        leader=None if banded.leader is None else snapshot.model_of(banded.leader.candidate_id),
        best=[entry(row) for row in banded.best],
        rest=[entry(row) for row in banded.rest],
        thin=[entry(row) for row in banded.thin],
    )


def blend(
    rows: Sequence[OptimisedResult],
    model_of: Callable[[str], str],
    probabilities: Callable[[str, Mapping[str, Distribution]], Mapping[str, float]],
) -> list[BlendTerm]:
    """Each weighted dimension, heaviest first, its share, and the order on it alone.

    ``rows`` are every ranked row, so a model's cheapest offering counts on a
    cost dimension even when a dearer one represents it in the bands. A
    capability dimension leads with the best point estimate among models with
    enough evidence on it; ``probabilities`` gives P(best) on that dimension.
    """
    if not rows:
        return []
    total = sum(contribution.weight for contribution in rows[0].contributions)
    terms = []
    for index, first in enumerate(rows[0].contributions):
        best: dict[str, tuple[float, object]] = {}
        for row in rows:
            contribution = row.contributions[index]
            model_id = model_of(row.candidate_id)
            if contribution.value is None:
                continue
            if model_id not in best or contribution.value > best[model_id][0]:
                best[model_id] = (contribution.value, contribution)
        estimated = first.estimate is not None
        scant = sorted(
            model_id for model_id, (_, contribution) in best.items()
            if contribution.estimate is not None
            and contribution.estimate.high - contribution.estimate.low > THIN_INTERVAL_WIDTH
        )
        order = sorted(
            (model_id for model_id in best if model_id not in scant),
            key=lambda model_id: (-best[model_id][0], model_id),
        )
        leaders: list[str] = []
        p_leader = runner_up = p_runner_up = None
        if order:
            top = best[order[0]][0]
            leaders = [model_id for model_id in order if best[model_id][0] == top]
            if estimated:
                leaders = leaders[:1]
                spreads = {
                    model_id: Distribution(
                        best[model_id][1].estimate.value, best[model_id][1].estimate.sd)
                    for model_id in order
                }
                p_leader = probabilities(first.dimension, spreads).get(leaders[0])
                if len(order) > 1:
                    runner_up = order[1]
                    p_runner_up = p_at_least(spreads[runner_up], spreads[leaders[0]])
        leader_value = None if not leaders else best[leaders[0]][1].raw_value
        terms.append(BlendTerm(
            dimension=first.dimension,
            weight=first.weight,
            share=round(first.weight / total, _PRECISION) if total else 0.0,
            estimated=estimated,
            leaders=leaders,
            value=leader_value,
            p_best=p_leader,
            runner_up=runner_up,
            p_runner_up=p_runner_up,
            order=order,
            thin=scant,
        ))
    return sorted(terms, key=lambda term: (-term.weight, term.dimension))
