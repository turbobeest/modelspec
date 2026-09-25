"""Run the slice-1 decision stages against one offline snapshot."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from itertools import combinations

from decision.contract import (
    Decision,
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
from decision.resolve import resolve
from decision.snapshot import ExplanationIndex


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
    resolved = resolve(spec, facets=facets, profiles=profiles)
    domains = frozenset(snapshot.domain_ids())
    selectors = dict(evidence_selectors or {})
    objective = spec.optimize
    names = (
        [objective.max]
        if objective.max
        else [objective.min]
        if objective.min
        else [step.facet for step in objective.lexicographic]
        if objective.lexicographic
        else list(objective.weights or objective.pareto)
    )
    for signed in names:
        name = signed.removeprefix("-")
        if resolved.facets(name).subject == "evidence" and name not in domains:
            selectors.setdefault(name, EvidenceSelector(name))
    filtered = apply(resolved, snapshot)
    ordered = run_optimise(snapshot, filtered, spec, selectors, domains)
    digest = spec_hash(spec)
    results = [
        Result(
            rank=i + 1,
            offering=offering_ref(snapshot, row.candidate_id),
            soft_penalty=row.soft_penalty,
            warnings=list(row.warnings)
            + (["deprecated"] if row.candidate_id in filtered.deprecated else []),
        )
        for i, row in enumerate(ordered.results[: spec.limit])
    ]
    relax = []
    if ordered.status == "no_feasible":
        # Search condition groups in increasing cardinality; preserve soft penalties.
        from dataclasses import replace

        from decision.contract import render_condition

        hard = [i for i, c in enumerate(resolved.conditions) if c.soft is None]
        if not filtered.feasible:
            for size in range(1, len(hard) + 1):
                for dropped in combinations(hard, size):
                    trial = replace(
                        resolved,
                        conditions=tuple(
                            c for i, c in enumerate(resolved.conditions) if i not in dropped
                        ),
                    )
                    if apply(trial, snapshot).feasible:
                        relax = [render_condition(resolved.conditions[i]) for i in dropped]
                        break
                if relax:
                    break
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
        may_qualify=[
            MayQualify(
                model=snapshot.model_of(m.candidate),
                offering=offering_ref(snapshot, m.candidate),
                unknown=list(m.unknown),
            )
            for m in filtered.may_qualify
        ],
    )
    if spec.explain != "none":
        from decision.explain import explain

        explain(decision, resolved, snapshot, filtered, ordered, selectors, domains)
    return decision
