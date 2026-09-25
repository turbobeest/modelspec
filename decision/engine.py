"""Run the slice-1 decision stages against one offline snapshot."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import replace

from decision.computed import with_computed
from decision.contract import (
    DEFAULT_TASK_TOKENS,
    Decision,
    Estimate,
    FacetLookup,
    InventoryProfile,
    MayQualify,
    OfferingRef,
    Result,
    Spec,
    spec_hash,
)
from decision.filter import apply
from decision.optimise import EvidenceSelector, optimise
from decision.relax import fewest, smallest_changes
from decision.resolve import resolve
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
    return replace(ordered, results=ranked), {
        cid: list(ordered.unknown.get(cid, ())) for cid in ordered.missing}


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


def decide(
    spec: Spec,
    snapshot: ExplanationIndex,
    *,
    facets: FacetLookup | None = None,
    profiles: Mapping[str, InventoryProfile] | None = None,
    evidence_selectors: Mapping[str, EvidenceSelector] | None = None,
) -> Decision:
    """Return a reproducible decision. Explanation work is skipped at ``none``."""
    if snapshot is None:
        raise ValueError("a loaded decision snapshot is required")
    # Computed facets (offering.cost_per_task) depend on the spec, so the
    # snapshot answers them through a per-decision view.
    snapshot = with_computed(snapshot, spec.task_tokens or DEFAULT_TASK_TOKENS)
    if spec.explain in ("summary", "full"):
        snapshot.require_explanation_records()
    resolved = resolve(spec, facets=facets, profiles=profiles)
    domains = frozenset(snapshot.domain_ids())
    requested = frozenset(spec.capabilities or {})
    selectors = dict(evidence_selectors or {})
    names = _objective_names(spec)
    for signed in names:
        name = signed.removeprefix("-")
        if resolved.facets(name).subject == "evidence" and name not in domains:
            selectors.setdefault(
                name,
                EvidenceSelector.from_qualifiers(
                    name, resolved.objective_qualifiers.get(name), domains=requested
                ),
            )
    filtered = apply(resolved, snapshot)
    ordered, objective_unknown = split_missing(
        run_optimise(snapshot, filtered, spec, selectors, domains)
    )
    digest = spec_hash(spec)
    objective_domains = [name.removeprefix("-") for name in names
                         if name.removeprefix("-") in domains]
    shown_domains = sorted(requested | set(objective_domains))
    probability_domain = (
        objective_domains[0] if len(objective_domains) == 1 and len(names) == 1 else None
    )
    probabilities = {}
    model_estimates = {}
    if probability_domain is not None:
        from decision.capability import CapabilityEstimate, deterministic_probabilities

        for row in ordered.results:
            model_id = snapshot.model_of(row.candidate_id)
            stored = snapshot.capability_estimate(row.candidate_id, probability_domain)
            if stored is not None:
                model_estimates.setdefault(
                    model_id,
                    CapabilityEstimate(stored.value, stored.low, stored.high, stored.sd),
                )
        probabilities = deterministic_probabilities(
            model_estimates,
            seed_material=f"{snapshot.snapshot_id}:{digest}:{probability_domain}",
        )

    results = []
    for i, row in enumerate(ordered.results[: spec.limit]):
        model_id = snapshot.model_of(row.candidate_id)
        stored_estimates = [
            (domain, snapshot.capability_estimate(row.candidate_id, domain))
            for domain in shown_domains
        ]
        estimates = [
            Estimate(domain=domain, value=estimate.value, interval=(estimate.low, estimate.high))
            for domain, estimate in stored_estimates
            if estimate is not None
        ]
        warnings = list(row.warnings)
        if row.candidate_id in filtered.deprecated:
            warnings.append("deprecated")
        current = model_estimates.get(model_id)
        if current is not None and any(
            other_id != model_id
            and max(current.low, other.low) <= min(current.high, other.high)
            for other_id, other in model_estimates.items()
        ):
            warnings.append("not_separable")
        p_best, top3 = probabilities.get(model_id, (None, None))
        results.append(Result(
            rank=i + 1,
            offering=offering_ref(snapshot, row.candidate_id),
            estimates=estimates or None,
            p_best=p_best,
            top3_stability=top3,
            soft_penalty=row.soft_penalty,
            warnings=warnings,
        ))
    relax, relax_to = [], []
    if ordered.status == "no_feasible":
        # Never the class or a requested domain: that would change the question.
        if not filtered.feasible:
            relax = fewest(resolved, snapshot, requested)
            relax_to = smallest_changes(resolved, snapshot, requested)
        if not relax:
            relax = [ordered.reason or "no candidates in the snapshot"]
    decision = Decision(
        decision_id="dec_"
        + hashlib.sha256((digest + snapshot.snapshot_id).encode()).hexdigest()[:24],
        spec_hash=digest,
        snapshot=snapshot.snapshot_id,
        explain=spec.explain,
        status="partial"
        if ordered.status == "answered" and filtered.may_qualify
        else ordered.status,
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
        out_of_lineup=getattr(snapshot, "out_of_lineup", 0),
    )
    if spec.explain != "none":
        from decision.explain import explain

        explain(decision, resolved, snapshot, filtered, ordered, selectors, domains)
    return decision
