"""Run the slice-1 decision stages against one offline snapshot."""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Mapping
from dataclasses import replace
from math import inf, isfinite, sqrt

from decision import estate as estate_module
from decision import plans as plans_module
from decision.by_model import build_by_model
from decision.computed import with_computed
from decision.contract import (
    DEFAULT_TASK_TOKENS,
    Decision,
    Estimate,
    FacetLookup,
    InventoryProfile,
    Issue,
    MayQualify,
    OfferingRef,
    RefinementEstimate,
    Result,
    SeparatedAnswer,
    Spec,
    SpecError,
    TieBreakers,
    TiedAnswer,
    Truncated,
    spec_hash,
)
from decision.filter import FilterResult, apply
from decision.optimise import EvidenceSelector, OptimisedResult, optimise
from decision.refinements import RANKABLE, is_refinement_key, split_dimension
from decision.refinements import evidence_state as refinement_evidence_state
from decision.refinements import lineup as refinement_lineup
from decision.relax import fewest, smallest_changes
from decision.resolve import Resolved, resolve
from decision.snapshot import ExplanationIndex


def _objective_names(spec: Spec) -> list[str]:
    objective = spec.optimize
    return (
        [objective.max]
        if objective.max
        else [objective.min]
        if objective.min
        else [step.facet for step in objective.lexicographic]
        if objective.lexicographic
        else list(objective.weights or objective.pareto)
    )


def offering_ref(snapshot, cid: str) -> OfferingRef:
    if snapshot.kind(cid) == "model":
        return OfferingRef(model=cid)
    return OfferingRef(
        model=snapshot.model_of(cid),
        **{
            key: snapshot.fact(cid, "offering." + key).value
            for key in ("provider", "region", "tier")
        },
    )


def split_missing(ordered):
    """Rank only complete rows; a missing objective value is a capability unknown.

    Principle 1 of the design: unknown means may qualify, never ranked last
    and never dropped. Returns the ranked stage result and, per candidate
    without a value, the objective facets it is unknown on.
    """
    missing = set(ordered.missing)
    ranked = tuple(row for row in ordered.results if row.candidate_id not in missing)
    # A refinement is unknown when its parent is: report the parent's facet ID.
    return replace(ordered, results=ranked), {
        cid: list(dict.fromkeys(
            split_dimension(name)[0] for name in ordered.unknown.get(cid, ())
        ))
        for cid in ordered.missing}


def run_optimise(snapshot, filtered, spec, selectors, domains):
    penalties = {}
    for penalty in filtered.penalties:
        for cid in penalty.failing + penalty.unknown:
            penalties.setdefault(cid, {})[penalty.condition] = penalty.penalty
    return optimise(
        snapshot,
        filtered.feasible,
        spec.optimize,
        penalties=penalties,
        evidence_selectors=selectors,
        domains=domains,
    )


def refinement_keys(spec: Spec) -> list[str]:
    """The refinement keys in ``optimize.weights``, unsigned, in spec order."""
    return [key.removeprefix("-") for key in spec.optimize.weights or ()
            if is_refinement_key(key)]


def _check_refinements(spec: Spec, snapshot) -> None:
    """Refuse a refinement key the vocabulary would not offer as rankable."""
    keys = refinement_keys(spec)
    if not keys:
        return
    known = set(snapshot.refinement_keys())
    candidates = refinement_lineup(snapshot)
    issues = []
    for key in keys:
        if key not in known:
            reason = f"{key} is not a registered refinement in this snapshot"
        else:
            state, measured, of_models = refinement_evidence_state(
                snapshot, candidates, snapshot.refinement_benchmarks(key),
                snapshot.refinement_eligible_classes(key),
            )
            if state in RANKABLE:
                continue
            reason = (
                f"{key} is not rankable: evidence_state {state} "
                f"(measured on {measured} of {of_models} models); rank on "
                f"{split_dimension(key)[0]} instead"
            )
        issues.append(Issue(None, key, reason, "optimize.weights"))
    if issues:
        raise SpecError(issues)


def validate(
    spec: Spec,
    snapshot: ExplanationIndex,
    *,
    facets: FacetLookup | None = None,
    profiles: Mapping[str, InventoryProfile] | None = None,
) -> Resolved:
    """Run the decision stages through resolve, stopping before filtering."""
    if snapshot is None:
        raise ValueError("a loaded decision snapshot is required")
    if spec.exclude_benchmarks:
        known_benchmarks = set(snapshot.benchmark_ids())
        issues = [
            Issue(
                None,
                benchmark_id,
                "unknown benchmark ID in this snapshot",
                f"exclude_benchmarks[{index}]",
            )
            for index, benchmark_id in enumerate(spec.exclude_benchmarks)
            if benchmark_id not in known_benchmarks
        ]
        if issues:
            raise SpecError(issues)
    if spec.estate is not None:
        estate_module.check(spec.estate, snapshot)
    if spec.access is not None:
        plans_module.check_access(spec.access)
    snapshot = with_computed(snapshot, spec.task_tokens or DEFAULT_TASK_TOKENS)
    if spec.explain in ("summary", "full"):
        snapshot.require_explanation_records()
    resolved = resolve(spec, facets=facets, profiles=profiles)
    _check_refinements(spec, snapshot)
    return resolved


def _overlaps_raw_evidence(row, others, snapshot) -> bool:
    """Whether a selected measurement overlaps another model's interval."""
    model_id = snapshot.model_of(row.candidate_id)
    for contribution in row.contributions:
        if len(contribution.evidence) != 1:
            continue
        evidence = contribution.evidence[0]
        interval = evidence.interval
        if interval is None:
            continue
        for other in others:
            if snapshot.model_of(other.candidate_id) == model_id:
                continue
            for compared in other.contributions:
                if compared.dimension != contribution.dimension or len(compared.evidence) != 1:
                    continue
                other_evidence = compared.evidence[0]
                measurement_identity = (
                    evidence.benchmark_id,
                    evidence.version,
                    evidence.unit,
                    evidence.subcategory,
                    evidence.effort,
                    evidence.harness,
                )
                other_identity = (
                    other_evidence.benchmark_id,
                    other_evidence.version,
                    other_evidence.unit,
                    other_evidence.subcategory,
                    other_evidence.effort,
                    other_evidence.harness,
                )
                if measurement_identity != other_identity:
                    continue
                other_interval = other_evidence.interval
                if other_interval is not None and max(interval[0], other_interval[0]) <= min(
                    interval[1], other_interval[1]
                ):
                    return True
    return False


_ANSWER_BASIS = (
    "leader-overlap score intervals; capability estimates use 80% intervals"
)
_INDEPENDENT_MEASURERS = frozenset({
    "benchmark_author",
    "independent",
    "independent_evaluator",
    "modelspec",
    "outcome_protocol",
})


def _known_number(snapshot, cid: str, facet: str) -> float | None:
    value = snapshot.fact(cid, facet)
    if (
        value.state != "known"
        or isinstance(value.value, bool)
        or not isinstance(value.value, int | float)
        or not isfinite(value.value)
    ):
        return None
    return float(value.value)


def _candidate_cost(snapshot, cid: str) -> float | None:
    return _known_number(snapshot, cid, "offering.cost_per_task")


def _offering_costs(snapshot) -> Callable[[OfferingRef], float | None]:
    """The task cost of any offering, by its reference; the snapshot is scanned on first use."""
    by_model: dict[str, list[str]] = {}

    def cost_of(ref: OfferingRef) -> float | None:
        if not by_model:
            for cid in snapshot.candidates():
                if snapshot.kind(cid) == "offering":
                    by_model.setdefault(snapshot.model_of(cid), []).append(cid)
        for cid in by_model.get(ref.model, ()):
            if offering_ref(snapshot, cid) == ref:
                return _candidate_cost(snapshot, cid)
        return None

    return cost_of


def _plan_price(snapshot, cid: str) -> float | None:
    return _known_number(snapshot, cid, plans_module.PRICE_MONTHLY)


def _representative_rows(
    rows: tuple[OptimisedResult, ...], snapshot, cost=_candidate_cost,
) -> list[OptimisedResult]:
    """One best offering per model, ordered by point score, cost, then model ID."""
    by_model: dict[str, list[OptimisedResult]] = {}
    for row in rows:
        if row.score is not None:
            by_model.setdefault(snapshot.model_of(row.candidate_id), []).append(row)

    representatives = []
    for model_id, choices in by_model.items():
        representatives.append(min(
            choices,
            key=lambda row: (
                -row.score,
                cost(snapshot, row.candidate_id)
                if cost(snapshot, row.candidate_id) is not None
                else inf,
                row.candidate_id,
            ),
        ))
    return sorted(
        representatives,
        key=lambda row: (
            -row.score,
            cost(snapshot, row.candidate_id)
            if cost(snapshot, row.candidate_id) is not None
            else inf,
            snapshot.model_of(row.candidate_id),
        ),
    )


def _unique_extreme(values: Mapping[str, float | None], *, highest: bool) -> str | None:
    known = {model_id: value for model_id, value in values.items() if value is not None}
    if not known:
        return None
    extreme = (max if highest else min)(known.values())
    winners = sorted(model_id for model_id, value in known.items() if value == extreme)
    return winners[0] if len(winners) == 1 else None


def _independent_measurements(snapshot, model_id: str) -> int:
    records = set()
    for benchmark_id in snapshot.benchmark_ids():
        for row in snapshot.evidence(
            model_id, benchmark_id, measured_by=set(_INDEPENDENT_MEASURERS)
        ):
            if row.verified and not row.quality_flags:
                records.add(row.record_id or (
                    row.benchmark_id,
                    row.version,
                    row.subcategory,
                    row.value,
                    row.effort,
                    row.harness,
                ))
    return len(records)


def _tie_breakers(rows: list[OptimisedResult], snapshot, cost=_candidate_cost) -> TieBreakers:
    by_model = {snapshot.model_of(row.candidate_id): row for row in rows}
    costs = {
        model_id: cost(snapshot, row.candidate_id)
        for model_id, row in by_model.items()
    }
    speeds = {
        model_id: _known_number(snapshot, row.candidate_id, "offering.speed.throughput")
        for model_id, row in by_model.items()
    }
    open_models = sorted(
        model_id
        for model_id in by_model
        if snapshot.fact(model_id, "model.weights_openness").value == "open_weights"
    )
    measurements = {
        model_id: float(_independent_measurements(snapshot, model_id))
        for model_id in by_model
    }
    return TieBreakers(
        cheapest=_unique_extreme(costs, highest=False),
        open_weights=open_models[0] if len(open_models) == 1 else None,
        most_independently_measured=_unique_extreme(measurements, highest=True),
        fastest=_unique_extreme(speeds, highest=True),
    )


def _answer(rows: list[OptimisedResult], snapshot, cost=_candidate_cost):
    if not rows or rows[0].score_interval is None:
        return None
    leader = rows[0]
    leader_low, leader_high = leader.score_interval
    members = [
        row
        for row in rows
        if row.score_interval is not None
        and max(leader_low, row.score_interval[0])
        <= min(leader_high, row.score_interval[1])
    ]
    model_ids = [snapshot.model_of(row.candidate_id) for row in members]
    if len(members) == 1:
        return SeparatedAnswer(
            kind="separated",
            members=model_ids,
            leader=model_ids[0],
            basis=_ANSWER_BASIS,
            tie_breakers=TieBreakers(),
            deterministic_order=model_ids,
        )
    return TiedAnswer(
        kind="tied",
        members=model_ids,
        basis=_ANSWER_BASIS,
        tie_breakers=_tie_breakers(members, snapshot, cost),
        deterministic_order=model_ids,
    )


def _score_distribution(row: OptimisedResult):
    """The weighted score posterior, with exact facets contributing zero variance."""
    if row.score is None or row.score_interval is None:
        return None
    variance = 0.0
    has_capability = False
    for contribution in row.contributions:
        estimate = contribution.estimate
        normalisation = contribution.normalisation
        if estimate is None:
            continue
        has_capability = True
        low, high = normalisation.minimum, normalisation.maximum
        if low is not None and high is not None and high != low:
            variance += (contribution.weight * estimate.sd / (high - low)) ** 2
    if not has_capability:
        return None
    from decision.capability import CapabilityEstimate

    return CapabilityEstimate(
        row.score,
        row.score_interval[0],
        row.score_interval[1],
        sqrt(variance),
    )


def _refinement_estimate(key: str, found) -> RefinementEstimate | None:
    if found is None:
        return None
    parent, refinement = split_dimension(key)
    return RefinementEstimate(
        key=key,
        domain=parent,
        refinement=refinement,
        value=found.estimate.value,
        interval=(found.estimate.low, found.estimate.high),
        evidence_count=found.evidence_count,
    )


def _plan_routes(cid: str, snapshot, access, reach) -> list:
    """The plans that reach ``cid`` on ``access``, cheapest first (MODEL-200).

    None for a row the caller already holds: at the margin it has no
    pay-per-use cost to break even against."""
    if cid in reach.marginal:
        return []
    ref = offering_ref(snapshot, cid)
    where = f"{ref.model} through {ref.provider}" if ref.provider else ref.model
    cost = _candidate_cost(snapshot, cid)
    routes = [
        plans_module.route(reach.plans[plan_id], surface, coverage, access, cost, where)
        for plan_id, surface, coverage in reach.routes.get(cid, ())
    ]
    return sorted(routes, key=lambda r: (r.price_monthly_usd is None,
                                         r.price_monthly_usd or 0, r.plan))


def decide(
    spec: Spec,
    snapshot: ExplanationIndex,
    *,
    facets: FacetLookup | None = None,
    profiles: Mapping[str, InventoryProfile] | None = None,
    evidence_selectors: Mapping[str, EvidenceSelector] | None = None,
    _filter_trace: Callable[[FilterResult], None] | None = None,
    comparison: bool = False,
) -> Decision:
    """Return a reproducible decision. Explanation work is skipped at ``none``.

    ``comparison`` retains named facts for every returned candidate in the
    intermediate Decision. Ordinary full decisions still cap ``top`` at 20.

    A spec with an ``estate`` (MODEL-179) is answered twice: the unrestricted
    decision is computed as if the estate were absent, and ``with_estate``
    carries the same question over what the estate holds.

    A spec with an ``access`` (MODEL-200) is answered over the routes that
    serve it: plans whose surfaces match, pay-per-use offerings for a coding
    tool or the caller's own software, self-hosting for their own hardware.
    """
    if spec.estate is None and spec.access is None:
        return _decide(
            spec, snapshot, facets=facets, profiles=profiles,
            evidence_selectors=evidence_selectors, _filter_trace=_filter_trace,
            comparison=comparison,
        )
    if spec.estate is not None:
        estate_module.check(spec.estate, snapshot)
    if spec.access is not None:
        plans_module.check_access(spec.access)
    catalogue = estate_module.Catalogue(snapshot)
    routes = (None if spec.access is None
              else estate_module.access_reach(catalogue, spec.access))
    if spec.estate is None:
        return _decide(
            spec, snapshot, facets=facets, profiles=profiles,
            evidence_selectors=evidence_selectors, _filter_trace=_filter_trace,
            comparison=comparison, _reach=routes,
        )
    question = spec.model_copy(update={"estate": None})
    capture: dict = {}
    decision = _decide(
        question, snapshot, facets=facets, profiles=profiles,
        evidence_selectors=evidence_selectors, _filter_trace=_filter_trace,
        comparison=comparison, _capture=capture, _identity=spec, _reach=routes,
    )

    def run(reach, limit):
        trial = question.model_copy(update={"explain": "none", "limit": limit})
        seen: dict = {}
        answered = _decide(
            trial, snapshot, facets=facets, profiles=profiles,
            evidence_selectors=evidence_selectors, _reach=reach, _capture=seen,
        )
        return estate_module.Ran(answered, seen["models"], seen["rows"], seen["computed"])

    unrestricted = estate_module.Ran(
        decision, capture["models"], capture["rows"], capture["computed"])
    decision.with_estate = estate_module.with_estate(
        spec.estate, snapshot, unrestricted, run, spec.limit, spec.access, catalogue)
    return decision


def _decide(
    spec: Spec,
    snapshot: ExplanationIndex,
    *,
    facets: FacetLookup | None = None,
    profiles: Mapping[str, InventoryProfile] | None = None,
    evidence_selectors: Mapping[str, EvidenceSelector] | None = None,
    _filter_trace: Callable[[FilterResult], None] | None = None,
    comparison: bool = False,
    _reach=None,
    _capture: dict | None = None,
    _identity: Spec | None = None,
) -> Decision:
    resolved = validate(spec, snapshot, facets=facets, profiles=profiles)
    if spec.exclude_benchmarks:
        from decision.capability import excluding_benchmarks

        snapshot = excluding_benchmarks(snapshot, spec.exclude_benchmarks)
    # Computed facets (offering.cost_per_task) depend on the spec, so the
    # remaining stages use the same per-decision view validation prepared for.
    snapshot = with_computed(
        snapshot, spec.task_tokens or DEFAULT_TASK_TOKENS,
        None if _reach is None else _reach.marginal,
        frozenset() if _reach is None else _reach.unpriced,
        None if _reach is None else _reach.plan_prices,
    )
    access = spec.access
    # A chat app route is paid by the month: order and break ties on the plan's price.
    tie_cost = (_plan_price if access is not None and access.kind == "chat_app"
                else _candidate_cost)
    domains = frozenset(snapshot.domain_ids())
    requested = frozenset(spec.capabilities or {})
    selectors = dict(evidence_selectors or {})
    names = _objective_names(spec)
    for signed in names:
        name = signed.removeprefix("-")
        if is_refinement_key(name):
            continue
        if resolved.facets(name).subject == "evidence" and name not in domains:
            selectors.setdefault(
                name,
                EvidenceSelector.from_qualifiers(
                    name, resolved.objective_qualifiers.get(name), domains=requested
                ),
            )
    filtered = apply(resolved, snapshot, _reach)
    if _filter_trace is not None:
        _filter_trace(filtered)
    ordered, objective_unknown = split_missing(
        run_optimise(snapshot, filtered, spec, selectors, domains)
    )
    digest = spec_hash(spec)
    identity = digest if _identity is None else spec_hash(_identity)
    objective_domains = [name.removeprefix("-") for name in names
                         if name.removeprefix("-") in domains]
    shown_domains = sorted(requested | set(objective_domains))
    shown_refinements = refinement_keys(spec)
    proxy_only_domains = {
        domain
        for domain in shown_domains
        if {
            directness
            for item in snapshot.capability_items.values()
            for tagged_domain, directness in item.get("domains", ())
            if tagged_domain == domain
        }
        == {"proxy"}
    }
    proxy_only_refinements = {
        key for key in shown_refinements
        if {directness for _, directness in snapshot.refinement_benchmarks(key)} == {"proxy"}
    }
    probability_domain = (
        objective_domains[0] if len(objective_domains) == 1 and len(names) == 1 else None
    )
    probabilities = {}
    model_estimates = {}
    representative_rows = _representative_rows(ordered.results, snapshot, tie_cost)
    answer = _answer(representative_rows, snapshot, tie_cost)
    if spec.optimize.lexicographic is None and spec.optimize.pareto is None:
        from decision.capability import deterministic_probabilities

        for row in representative_rows:
            distribution = _score_distribution(row)
            if distribution is not None:
                model_estimates[snapshot.model_of(row.candidate_id)] = distribution
        probabilities = deterministic_probabilities(
            model_estimates,
            seed_material=f"{snapshot.snapshot_id}:{digest}:{probability_domain or 'weighted'}",
        )

    returned_rows = ordered.results[: spec.limit]
    if _capture is not None:
        _capture["models"] = list(dict.fromkeys(
            snapshot.model_of(row.candidate_id) for row in ordered.results))
        _capture["rows"] = [row.candidate_id for row in returned_rows]
        _capture["computed"] = snapshot
    omitted_rows = ordered.results[spec.limit :]
    returned_models = {
        snapshot.model_of(row.candidate_id) for row in returned_rows
    }
    omitted_models = {
        snapshot.model_of(row.candidate_id) for row in omitted_rows
    } - returned_models
    truncated = Truncated(
        offerings=sum(snapshot.kind(row.candidate_id) == "offering" for row in omitted_rows),
        models=len(omitted_models),
    )
    results = []
    model_ranks: dict[str, int] = {}
    for i, row in enumerate(returned_rows):
        model_id = snapshot.model_of(row.candidate_id)
        model_ranks.setdefault(model_id, len(model_ranks) + 1)
        stored_estimates = [
            (domain, snapshot.capability_estimate(row.candidate_id, domain))
            for domain in shown_domains
        ]
        estimates = [
            Estimate(domain=domain, value=estimate.value, interval=(estimate.low, estimate.high))
            for domain, estimate in stored_estimates
            if estimate is not None
        ]
        nested = [
            _refinement_estimate(key, snapshot.refinement_estimate(row.candidate_id, key))
            for key in shown_refinements
        ]
        nested = [estimate for estimate in nested if estimate is not None]
        warnings = list(row.warnings)
        if row.candidate_id in filtered.deprecated:
            warnings.append("deprecated")
        if any(estimate.domain in proxy_only_domains for estimate in estimates) or any(
            estimate.key in proxy_only_refinements and estimate.evidence_count
            for estimate in nested
        ):
            warnings.append("proxy_evidence_only")
        current = model_estimates.get(model_id)
        if current is not None and any(
            other_id != model_id
            and max(current.low, other.low) <= min(current.high, other.high)
            for other_id, other in model_estimates.items()
        ):
            warnings.append("not_separable")
        if (
            len(names) == 1
            and _overlaps_raw_evidence(row, ordered.results, snapshot)
            and "not_separable" not in warnings
        ):
            warnings.append("not_separable")
        if (
            answer is not None
            and answer.kind == "tied"
            and model_id in answer.members
            and "not_separable" not in warnings
        ):
            warnings.append("not_separable")
        p_best, top3 = probabilities.get(model_id, (None, None))
        plan_routes = (
            _plan_routes(row.candidate_id, snapshot, access, _reach)
            if access is not None and _reach is not None else []
        )
        results.append(Result(
            rank=i + 1,
            offering=offering_ref(snapshot, row.candidate_id),
            model_rank=model_ranks[model_id],
            cost_per_task=_candidate_cost(snapshot, row.candidate_id),
            estimates=estimates or None,
            refinement_estimates=nested or None,
            p_best=p_best,
            top3_stability=top3,
            soft_penalty=row.soft_penalty,
            warnings=warnings,
            plans=plan_routes,
        ))
    relax, relax_to = [], []
    if ordered.status == "no_feasible":
        # Never the class or a requested domain: that would change the question.
        if not filtered.feasible and _reach is None:
            relax = fewest(resolved, snapshot, requested)
            relax_to = smallest_changes(resolved, snapshot, requested)
        if not relax:
            relax = [ordered.reason or "no candidates in the snapshot"]
    decision = Decision(
        decision_id="dec_"
        + hashlib.sha256((identity + snapshot.snapshot_id).encode()).hexdigest()[:24],
        spec_hash=identity,
        snapshot=snapshot.snapshot_id,
        signature_verified=getattr(snapshot, "signature_verified", False),
        explain=spec.explain,
        status="partial"
        if ordered.status == "answered" and filtered.may_qualify
        else ordered.status,
        answer=answer,
        results=results,
        relax=relax,
        relax_to=relax_to,
        may_qualify=[
            MayQualify(
                model=snapshot.model_of(cid),
                offering=offering_ref(snapshot, cid),
                unknown=unknown,
            )
            for cid, unknown in sorted(
                [(m.candidate, list(m.unknown)) for m in filtered.may_qualify]
                + list(objective_unknown.items())
            )
        ],
        truncated=truncated,
        out_of_lineup=getattr(snapshot, "out_of_lineup", 0),
    )
    cost_of = _offering_costs(snapshot)
    decision.by_model = build_by_model(decision, cost_of)
    if spec.explain != "none":
        from decision.explain import explain

        explain(
            decision, resolved, snapshot, filtered, ordered, selectors, domains,
            comparison=comparison,
        )
        if spec.explain == "full":
            decision.by_model = build_by_model(decision, cost_of)
    return decision
