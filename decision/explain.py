"""Explain decisions using retained snapshot records, without capability blending."""

from __future__ import annotations

from decision.contract import (
    BenchmarkEstimateChange,
    BenchmarkExclusions,
    Contribution,
    DomainEvidence,
    Estimate,
    EvidenceItem,
)
from decision.refinements import is_refinement_key, split_dimension
from decision.registry import UNREGISTERED
from decision.registry import facet as registry_facet


class ExplanationError(ValueError):
    """A displayed measurement cannot be traced to a verified snapshot record."""


#: An offering's provider, region and tier are its identity: structural, never
#: a sourced claim, so they carry no record (``decision.snapshot``). A value
#: preference on one used to fail its explanation (MODEL-203).
OFFERING_IDENTITY = frozenset({"offering.provider", "offering.region", "offering.tier"})
OFFERING_IDENTITY_FORMULA = "the offering's identity, which carries no source"


#: Facets a top candidate always shows when known, beside those the spec names:
#: what the decide page displays for a candidate (contract 1.4).
DISPLAY_FACETS = (
    "licence.commercial_use",
    "model.class",
    "model.context_window",
    "model.lifecycle",
    "model.release_date",
    "model.weights_openness",
    "offering.cost_per_task",
    "offering.data.retention",
    "offering.price.input",
    "offering.price.output",
    "offering.speed.throughput",
    "offering.speed.time_to_first_token",
    "origin.lab_jurisdiction",
)

#: The sections whose numbers a decision presents, and so the only ones
#: ``number_origins`` covers. A shown fact in ``top`` carries its own record
#: and source IDs, so it needs no origin; ``top``'s contributions repeat the
#: optimiser's arithmetic, already on their records.
PRESENTED = ("results", "top/*/evidence", "near_misses", "constraint_costs",
             "tipping_points", "eliminated/models")

#: Numbers with nothing to trace: the spec's own weights echoed back, the sum
#: of its soft penalties, ranks and counts. Funnel counts and ``out_of_lineup``
#: sit outside the presented sections for the same reason.
UNTRACED = frozenset({"weight", "soft_penalty", "rank", "admits"})


def facet_unit(facet_id):
    return registry_facet(facet_id).unit


def named_facets(resolved):
    """Every facet the spec's conditions (profile rules included) and objective name."""
    from decision.contract import AllOf, AnyOf, Known, NotOf

    names = set()

    def walk(cond):
        if isinstance(cond, AnyOf | AllOf):
            for child in cond.any if isinstance(cond, AnyOf) else cond.all:
                walk(child)
        elif isinstance(cond, NotOf):
            walk(cond.not_)
        else:
            names.add(cond.known if isinstance(cond, Known) else cond.facet)

    for cond in resolved.conditions:
        walk(cond)
    objective = resolved.spec.optimize
    terms = [objective.max, objective.min, *(step.facet for step in objective.lexicographic or ()),
             *(objective.weights or ()), *(objective.pareto or ())]
    names.update(term.removeprefix("-") for term in terms if term)
    return names


def benchmark_domains(snapshot, benchmark):
    return [domain for domain, _ in snapshot.benchmark_domain_tags().get(benchmark, ())]


def computed(snapshot, cid, facet_id):
    """The computed value behind a fact (MODEL-153), or ``None`` for a stored one."""
    lookup = getattr(snapshot, "computed", None)
    return None if lookup is None else lookup(cid, facet_id)


def fact_provenance(snapshot, cid, facet_id):
    """Records, unit and formula behind a non-evidence fact. A stored fact has
    one checked record; a computed one has the records it was computed from."""
    found = computed(snapshot, cid, facet_id)
    if found is not None:
        for rid in found.records:
            checked_record(snapshot, rid)
        return list(found.records), facet_unit(facet_id), found.formula
    if facet_id in OFFERING_IDENTITY:
        return [], None, OFFERING_IDENTITY_FORMULA
    fact = snapshot.fact(cid, facet_id)
    checked_record(snapshot, fact.record_id)
    return [fact.record_id], facet_unit(facet_id), None


def checked_record(snapshot, rid):
    if not rid:
        raise ExplanationError("snapshot lacks retained provenance; rebuild it before explaining")
    record = snapshot.record(rid)
    if record["verification"]["outcome"] != "verified":
        raise ExplanationError(f"{rid}: not verified")
    verification = record["verification"]
    collector, verifier = verification.get("collector", {}), verification.get("verifier", {})
    if (
        not collector.get("agent")
        or not verifier.get("agent")
        or collector["agent"] == verifier["agent"]
        or not collector.get("method")
        or not verifier.get("method")
        or collector["method"] == verifier["method"]
    ):
        raise ExplanationError(f"{rid}: verification must use a different agent and method")
    if not record.get("sources"):
        raise ExplanationError(f"{rid}: no source")
    from urllib.parse import urlsplit

    for source in record["sources"]:
        url = snapshot.source_url(source["source_id"])
        parsed = urlsplit(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ExplanationError(f"{rid}: source must be an http(s) URL")
    return record


def evidence_item(
    snapshot,
    row,
    domain,
    *,
    loading=None,
    estimate_weight=None,
    recency_weight=None,
):
    record = checked_record(snapshot, row.record_id)
    if not row.verified or row.date is None or row.directness is None:
        raise ExplanationError(f"{row.record_id}: missing evidence date or domain directness")
    if record.get("score") != row.value:
        raise ExplanationError(f"{row.record_id}: evidence differs from retained record")
    measured = {"independent_evaluator": "independent"}.get(row.measured_by, row.measured_by)
    date_type = {"evaluated": "observed"}.get(row.date_type, row.date_type)
    unregistered = row.harness == UNREGISTERED
    return EvidenceItem(
        requested_domain=domain,
        record_id=row.record_id,
        benchmark=row.benchmark_id,
        version=row.version,
        sub_category=row.subcategory,
        value=row.value,
        unit=row.unit,
        measured_by=measured,
        effort=row.effort,
        harness=None if unregistered else row.harness,
        harness_unregistered=unregistered,
        date=row.date,
        date_type=date_type,
        source=snapshot.source_url(row.source_ids[0]),
        source_snapshot=row.source_snapshot,
        directness=row.directness,
        n=row.n,
        interval=row.interval,
        quality_flags=list(row.quality_flags),
        loading=loading,
        estimate_weight=estimate_weight,
        recency_weight=recency_weight,
    )


def domain_evidence(snapshot, cid, domains, benchmarks=None):
    """Verified evidence per domain. An offering answers its model's evidence,
    so a row the offering and its model both return is listed once."""
    subjects = [cid]
    if snapshot.model_of(cid) != cid:
        subjects.append(snapshot.model_of(cid))
    groups = []
    for domain in sorted(domains):
        rows = {}
        for subject in subjects:
            for row in snapshot.evidence_for_domain(subject, domain):
                if row.verified and (benchmarks is None or row.benchmark_id in benchmarks):
                    rows.setdefault(row.record_id, row)
        groups.append(DomainEvidence(
            domain=domain, items=[evidence_item(snapshot, row, domain) for row in rows.values()]))
    return groups


def _estimate_drivers(snapshot, cid, dimension):
    """(drivers, their tags, requested domain) behind one estimate dimension.

    A refinement estimate moved by refinement evidence is driven by it; an
    unmeasured one is the parent's estimate, so the parent's drivers.
    """
    parent, refinement = split_dimension(dimension)
    own = snapshot.refinement_drivers(cid, dimension) if refinement else ()
    if own:
        tags = {}
        for benchmark, directness in snapshot.refinement_benchmarks(dimension):
            tags.setdefault(benchmark, []).append((dimension, directness))
        return own, tags, dimension, parent
    return (snapshot.capability_drivers(cid, parent), snapshot.benchmark_domain_tags(),
            parent, parent)


def estimate_evidence(snapshot, cid, domain):
    """The tagged measurements that drove one stored capability estimate."""
    from dataclasses import replace

    items = []
    model_id = snapshot.model_of(cid)
    drivers, tags, tag, domain = _estimate_drivers(snapshot, cid, domain)
    for driver in drivers:
        lookup = getattr(snapshot, "evidence_record", None)
        row = lookup(model_id, driver.record_id) if lookup is not None else next((
            row
            for candidate in snapshot.candidates()
            if snapshot.model_of(candidate) == model_id
            for row in snapshot.evidence(candidate, driver.benchmark_id)
            if row.record_id == driver.record_id
        ), None)
        if row is None:
            raise ExplanationError(
                f"{driver.record_id}: capability driver is not retained evidence"
            )
        directness = dict(tags.get(driver.benchmark_id, ())).get(tag)
        if directness is None:
            raise ExplanationError(
                f"{driver.record_id}: capability driver is not tagged for {tag}"
            )
        items.append(evidence_item(
            snapshot,
            replace(row, directness=directness),
            domain,
            loading=driver.loading,
            estimate_weight=driver.weight,
            recency_weight=driver.recency_weight,
        ))
    return items


def part_provenance(snapshot, cid, part):
    """Records, unit and formula behind one objective dimension's raw value."""
    if part.evidence:
        records = sorted({e.record_id for e in part.evidence})
        for rid in records:
            checked_record(snapshot, rid)
        return records, part.evidence[0].unit, None
    if part.estimate is not None and is_refinement_key(part.dimension):
        return _refinement_provenance(snapshot, cid, part.dimension.removeprefix("-"))
    if part.estimate is not None:
        domain = part.dimension.removeprefix("-")
        records = [driver.record_id for driver in snapshot.capability_drivers(
            cid, domain
        )]
        for rid in records:
            checked_record(snapshot, rid)
        directness = {
            kind
            for item in snapshot.capability_items.values()
            for tagged_domain, kind in item.get("domains", ())
            if tagged_domain == domain
        }
        formula = (
            "proxy-only monotone domain evidence estimate"
            if directness == {"proxy"}
            else "monotone domain evidence estimate"
        )
        return records, "latent capability", formula
    if part.raw_value is not None:
        return fact_provenance(snapshot, cid, part.dimension.removeprefix("-"))
    return [], None, None


def _refinement_provenance(snapshot, cid, key):
    parent, refinement = split_dimension(key)
    drivers, _tags, _tag, _domain = _estimate_drivers(snapshot, cid, key)
    records = [driver.record_id for driver in drivers]
    for rid in records:
        checked_record(snapshot, rid)
    label = refinement.replace("_", " ")
    if snapshot.refinement_estimate(cid, key).evidence_count:
        proxy = {d for _, d in snapshot.refinement_benchmarks(key)} == {"proxy"}
        formula = (f"{parent} estimate plus a partially pooled "
                   f"{'proxy-only ' if proxy else ''}{label} adjustment")
    else:
        formula = f"no {label} evidence: the {parent} estimate, with a wider interval"
    return records, "latent capability", formula


def _items(groups, ids):
    """The evidence items with these record IDs, each once."""
    found = {}
    for group in groups:
        for item in group.items:
            if item.record_id in ids:
                found.setdefault(item.record_id, item)
    return list(found.values())


def contributions(snapshot, cid, parts, evidence):
    out = []
    for part in parts:
        records, unit, formula = part_provenance(snapshot, cid, part)
        items = []
        if part.estimate is not None:
            items = estimate_evidence(snapshot, cid, part.dimension.removeprefix("-"))
        if part.evidence:
            items = _items(evidence, set(records))
            # A benchmark objective may have no requested domain. Do not invent
            # directness: read it from the domains that tag the benchmark.
            if not items:
                domains = {d for e in part.evidence for d in benchmark_domains(
                    snapshot, e.benchmark_id)}
                items = _items(domain_evidence(snapshot, cid, domains), set(records))
        norm = part.normalisation
        dimension, refinement = split_dimension(part.dimension)
        out.append(
            Contribution(
                dimension=dimension,
                refinement=refinement,
                weight=part.weight,
                value=part.value,
                raw_value=part.raw_value,
                unit=unit,
                records=records,
                normalisation=f"feasible min-max; {norm.direction}; "
                f"minimum={norm.minimum} {unit or 'unit not recorded'}; "
                f"maximum={norm.maximum} {unit or 'unit not recorded'}; "
                "constant dimensions contribute zero dimensionless",
                evidence=items,
                formula=formula,
                preferred_value=part.preferred_value,
                preference_status=part.preference_status,
            )
        )
    return out


def excluded_benchmark_impacts(snapshot, decision, result_rows, shown_domains):
    """Describe the estimate changes caused by a benchmark-exclusion view."""
    excluded = list(getattr(snapshot, "excluded_benchmarks", ()))
    if not excluded:
        return None
    candidate_by_model = {}
    for cid in snapshot.candidates():
        candidate_by_model.setdefault(snapshot.model_of(cid), cid)
    impacted_candidates = [row.candidate_id for _result, row in result_rows]
    impacted_candidates.extend(
        candidate_by_model[item.model]
        for item in decision.may_qualify
        if item.model in candidate_by_model
    )
    changes = []
    seen = set()
    for cid in impacted_candidates:
        model_id = snapshot.model_of(cid)
        for domain in sorted(shown_domains):
            identity = (model_id, domain)
            if identity in seen:
                continue
            seen.add(identity)
            before = snapshot.baseline_capability_estimate(cid, domain)
            after = snapshot.capability_estimate(cid, domain)
            baseline_drivers = {
                driver.record_id
                for driver in snapshot.baseline_capability_drivers(cid, domain)
            }
            removed = {
                evidence.record_id: evidence
                for evidence in snapshot.removed_evidence_for_domain(
                    cid, domain
                )
                if evidence.record_id in baseline_drivers
            }
            if before is None and after is None and not removed:
                continue
            changes.append(BenchmarkEstimateChange(
                model=model_id,
                domain=domain,
                before=None if before is None else Estimate(
                    domain=domain,
                    value=before.value,
                    interval=(before.low, before.high),
                ),
                after=None if after is None else Estimate(
                    domain=domain,
                    value=after.value,
                    interval=(after.low, after.high),
                ),
                removed_drivers=[
                    evidence_item(snapshot, evidence, domain)
                    for evidence in sorted(
                        removed.values(), key=lambda item: (item.benchmark_id, item.record_id)
                    )
                ],
            ))
    return BenchmarkExclusions(benchmarks=excluded, estimate_changes=changes)


def explain(
    decision, resolved, snapshot, filtered, ordered, selectors, domains, *,
    comparison=False,
):
    requested = set(resolved.spec.capabilities or {})
    result_rows = list(zip(decision.results, ordered.results))
    for result, row in result_rows:
        result.evidence = domain_evidence(snapshot, row.candidate_id, requested)
        result.contributions = contributions(
            snapshot, row.candidate_id, row.contributions, result.evidence
        )
    decision.benchmark_exclusions = excluded_benchmark_impacts(
        snapshot,
        decision,
        result_rows,
        requested | (named_facets(resolved) & set(domains)),
    )
    decision.eliminated.funnel = [step.as_contract() for step in filtered.funnel]
    _alternatives(decision, resolved, snapshot, filtered, ordered, selectors, domains)
    from decision.contract import TippingPoint

    decision.tipping_points = [
        TippingPoint(
            description=(
                f"{point.direction} weight past threshold; other weights and normalisation fixed"
            ),
            dimension=split_dimension(point.dimension)[0],
            refinement=split_dimension(point.dimension)[1],
            threshold=point.threshold,
            new_top=snapshot.model_of(point.new_top),
        )
        for point in ordered.tipping_points
    ]
    if decision.explain == "full":
        _full(
            decision, snapshot, ordered, requested, named_facets(resolved),
            comparison=comparison,
        )
        decision.chart = contribution_chart(decision)
        decision.number_origins = list(number_origins(decision, snapshot))
        decision.sources = cited_sources(decision, snapshot)


def _distance(reason, condition):
    from decision.contract import Compare, Window

    value, threshold = reason.value, reason.threshold
    if isinstance(value, (tuple, list)) and isinstance(condition, Window):
        numeric = [v for v in value if isinstance(v, (int, float)) and not isinstance(v, bool)]
        return min((max(threshold[0] - v, v - threshold[1], 0) for v in numeric), default=None)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if isinstance(condition, Compare) and condition.op in ("<", "<=", ">", ">=", "="):
        if isinstance(threshold, (int, float)) and not isinstance(threshold, bool):
            # Strict comparisons report distance to the boundary, not an invented epsilon.
            return abs(value - threshold)
    if isinstance(condition, Window):
        return max(threshold[0] - value, value - threshold[1], 0)
    return None


def _alternatives(decision, resolved, snapshot, filtered, ordered, selectors, domains):
    from dataclasses import replace

    from decision.contract import (
        ConstraintCost,
        ModelElimination,
        ModelEliminationGroup,
        NearMiss,
        OfferingElimination,
        RefinementGain,
        render_condition,
    )
    from decision.engine import offering_ref, run_optimise
    from decision.filter import apply

    current = {
        part.dimension: part
        for row in ordered.results
        for part in row.contributions
        if part.raw_value is not None
    }

    # Best observed raw value per dimension, independent of the weighted winner.
    def best(rows, dimension):
        values = [
            p.raw_value
            for r in rows
            for p in r.contributions
            if p.dimension == dimension and p.raw_value is not None
        ]
        if not values:
            return None
        return min(values) if dimension.startswith("-") else max(values)

    candidate_near_misses = {}
    for i, condition in enumerate(resolved.conditions):
        if condition.soft is not None:
            continue
        text = render_condition(condition)
        single = apply(replace(resolved, conditions=(condition,)), snapshot)
        relaxed = apply(
            replace(resolved, conditions=resolved.conditions[:i] + resolved.conditions[i + 1 :]),
            snapshot,
        )
        alternative = run_optimise(snapshot, relaxed, resolved.spec, selectors, domains)
        gains, units, records, bests = {}, {}, set(), {}
        for dimension in current:
            before, after = best(ordered.results, dimension), best(alternative.results, dimension)
            if before is not None and after is not None:
                gains[dimension] = after - before
                bests[dimension] = (before, after)
        # A gain rests on the two values it subtracts: the records behind those.
        for side, rows in enumerate((ordered.results, alternative.results)):
            for row in rows:
                for part in row.contributions:
                    if part.dimension in bests and part.raw_value == bests[part.dimension][side]:
                        rids, units[part.dimension], _ = part_provenance(
                            snapshot, row.candidate_id, part)
                        records.update(rids)
        decision.constraint_costs.append(
            ConstraintCost(
                condition=text,
                admits=len(set(relaxed.feasible) - set(filtered.feasible)),
                gain={d: g for d, g in gains.items() if not is_refinement_key(d)},
                refinement_gains=[
                    RefinementGain(dimension=parent, refinement=refinement, gain=g)
                    for d, g in gains.items() if is_refinement_key(d)
                    for parent, refinement in [split_dimension(d)]
                ],
                units=units,
                records=sorted(records),
            )
        )
        for reason in single.eliminated:
            if reason._condition != condition:
                continue
            is_collection = isinstance(reason.value, (tuple, list))
            values = list(reason.value) if is_collection else []
            value = None if is_collection else reason.value
            ref = offering_ref(snapshot, reason.candidate)
            records = []
            unit = None
            formula = None
            if reason.facet and reason.value is not None:
                fact = snapshot.fact(reason.candidate, reason.facet)
                if computed(snapshot, reason.candidate, reason.facet) is not None:
                    records, unit, formula = fact_provenance(
                        snapshot, reason.candidate, reason.facet)
                elif fact.record_id:
                    checked_record(snapshot, fact.record_id)
                    records = [fact.record_id]
                    unit = facet_unit(reason.facet)
                else:
                    for row in snapshot.evidence(reason.candidate, reason.facet):
                        if row.value in (values or [reason.value]):
                            checked_record(snapshot, row.record_id)
                            records.append(row.record_id)
                            unit = row.unit
            if decision.explain == "full":
                decision.eliminated.models.append(
                    ModelElimination(
                        model=ref.model,
                        offering=ref,
                        condition=text + (": unverified: may qualify" if reason.unverified else ""),
                        value=value,
                        values=values,
                        unit=unit,
                        records=records,
                        formula=formula,
                    )
                )
            if (
                reason.candidate in relaxed.feasible
                and not reason.unverified
                and reason.candidate not in filtered.feasible
            ):
                if not (ref.provider is None and (reason.facet or "").startswith("offering.")):
                    candidate_near_misses[reason.candidate] = NearMiss(
                        offering=ref,
                        condition=text,
                        facet=reason.facet,
                        value=value,
                        values=values,
                        distance=_distance(reason, condition),
                        unit=unit,
                        records=records,
                        formula=formula,
                    )
    if decision.explain == "full":
        already = {m.offering.model_dump_json() for m in decision.eliminated.models}
        for reason in filtered.eliminated:
            ref = offering_ref(snapshot, reason.candidate)
            if ref.model_dump_json() not in already:
                is_collection = isinstance(reason.value, (tuple, list))
                decision.eliminated.models.append(
                    ModelElimination(
                        model=ref.model,
                        offering=ref,
                        condition=reason.condition,
                        value=None if is_collection else reason.value,
                        values=list(reason.value) if is_collection else [],
                    )
                )
        for cid, dominators in ordered.dominance.items():
            ref = offering_ref(snapshot, cid)
            decision.eliminated.models.append(
                ModelElimination(
                    model=ref.model, offering=ref, condition="dominated by " + ", ".join(dominators)
                )
            )
        grouped = {}
        for row in decision.eliminated.models:
            group = grouped.setdefault(row.model, {"model": None, "offerings": {}})
            if row.offering is None or row.offering.provider is None:
                group["model"] = group["model"] or row
            else:
                key = row.offering.model_dump_json()
                group["offerings"].setdefault(key, row)
        decision.eliminated.model_groups = [
            ModelEliminationGroup(
                model=model,
                model_elimination=rows["model"],
                offerings=[
                    OfferingElimination(**row.model_dump(exclude={"model"}))
                    for row in rows["offerings"].values()
                ],
            )
            for model, rows in sorted(grouped.items())
        ]

    # A near miss is one model, represented by its best offering. Optimise all
    # offerings of that model without the hard conditions, then retain it only
    # when that best offering failed exactly one condition.
    by_model = {}
    for cid in candidate_near_misses:
        by_model.setdefault(snapshot.model_of(cid), []).append(cid)
    for model in sorted(by_model):
        if any(snapshot.model_of(cid) == model for cid in filtered.feasible):
            continue
        offerings = [
            cid for cid in snapshot.candidates()
            if snapshot.model_of(cid) == model and snapshot.kind(cid) == "offering"
        ]
        candidates = offerings or [model]
        unconstrained = replace(filtered, feasible=tuple(candidates), may_qualify=(), eliminated=())
        best = run_optimise(snapshot, unconstrained, resolved.spec, selectors, domains).results
        if best and best[0].candidate_id in candidate_near_misses:
            decision.near_misses.append(candidate_near_misses[best[0].candidate_id])


def _full(decision, snapshot, ordered, requested, named, *, comparison=False):
    """Facts and evidence for the full explanation or an internal comparison."""
    from decision.computed import COMPUTED_FACETS
    from decision.contract import CandidateValues, ShownFact
    from decision.engine import offering_ref

    shown = named | set(DISPLAY_FACETS)
    stored = [facet for facet in snapshot.facet_ids() if facet in shown]
    benchmarks = named & set(snapshot.benchmark_ids())
    ranked = len(decision.results)
    rows = ordered.results[:ranked] if comparison else ordered.results[:20]
    for position, row in enumerate(rows):
        cid = row.candidate_id
        facts = []
        for facet in stored:
            fact = snapshot.fact(cid, facet)
            if fact.state != "known":
                continue
            unit = None
            if fact.record_id:
                unit = facet_unit(facet)
            facts.append(ShownFact(
                facet=facet, value=fact.value, unit=unit, record_id=fact.record_id,
                source_ids=source_ids(snapshot, [fact.record_id] if fact.record_id else [])))
        for facet in COMPUTED_FACETS:
            found = computed(snapshot, cid, facet) if facet in shown else None
            if found is not None:
                records, unit, formula = fact_provenance(snapshot, cid, facet)
                facts.append(ShownFact(facet=facet, value=found.value, unit=unit,
                                       records=records, formula=formula,
                                       source_ids=source_ids(snapshot, records)))
        # Group each named benchmark under the requested domains that tag it,
        # or, when none does, under the first domain that does.
        domains = set(requested)
        for benchmark in benchmarks:
            tagged = benchmark_domains(snapshot, benchmark)
            if tagged and not requested & set(tagged):
                domains.add(tagged[0])
        evidence = [group for group in domain_evidence(snapshot, cid, domains, benchmarks)
                    if group.items]
        decision.top.append(
            CandidateValues(
                offering=offering_ref(snapshot, cid),
                facts=facts,
                evidence=evidence,
                # A ranked candidate's contributions are in ``results``, not repeated.
                contributions=[] if position < ranked else contributions(
                    snapshot, cid, row.contributions, evidence),
            )
        )


def dimension_label(part):
    """A contribution's or tipping point's dimension, with its refinement."""
    if part.dimension is None or part.refinement is None:
        return part.dimension
    return f"{part.dimension}/{part.refinement}"


def top_contributions(decision):
    """Each top candidate with its contributions, from ``results`` when ranked."""
    ranked = {r.offering.model_dump_json(): r.contributions for r in decision.results}
    for row in decision.top:
        yield row, row.contributions or ranked.get(row.offering.model_dump_json(), [])


def contribution_chart(decision):
    """Faceted raw-value bars: dimensions with different units never share a scale."""
    from html import escape

    rows = [
        (r.offering.model, c)
        for r, parts in top_contributions(decision)
        for c in parts
        if c.raw_value is not None
    ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 {max(60, len(rows) * 55)}" '
        'role="img" aria-label="Objective contributions in original units">'
    ]
    maxima = {
        dimension_label(c): max(
            abs(other.raw_value) for _, other in rows
            if dimension_label(other) == dimension_label(c)
        )
        for _, c in rows
    }
    for i, (model, c) in enumerate(rows):
        width = 300 * abs(c.raw_value) / (maxima[dimension_label(c)] or 1)
        reported = (
            " · Lab-reported"
            if any(e.measured_by == "provider_self_report" for e in c.evidence)
            else ""
        )
        label = escape(
            f"{model}{reported} · {dimension_label(c)}: {c.raw_value:g} "
            f"{c.unit or 'unit not recorded'}"
        )
        parts += [
            f'<text x="8" y="{i * 55 + 18}">{label}</text>',
            f'<rect x="8" y="{i * 55 + 27}" width="{width:g}" height="12" />',
        ]
    return "".join(parts) + "</svg>"


def numbers(value, path=""):
    """Walk numeric JSON leaves. IDs, dates and SVG geometry are not measurements."""
    if isinstance(value, bool):
        return
    if isinstance(value, (int, float)):
        yield path, value
    elif isinstance(value, dict):
        for key, child in value.items():
            if key != "number_origins":
                yield from numbers(child, path + "/" + key)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from numbers(child, path + "/" + str(i))


def presented_values(data):
    """The numbers ``number_origins`` covers: those in the presented sections."""
    def within(node, path, keys):
        if not keys:
            yield from ((p, v) for p, v in numbers(node, path)
                        if p.rsplit("/", 1)[-1] not in UNTRACED)
        elif keys[0] == "*":
            for i, child in enumerate(node):
                yield from within(child, f"{path}/{i}", keys[1:])
        else:
            yield from within(node.get(keys[0], []), f"{path}/{keys[0]}", keys[1:])

    for section in PRESENTED:
        yield from within(data, "", section.split("/"))


def _node(data, path):
    parent, ancestors = data, []
    nodes = path.strip("/").split("/")
    for node in nodes[:-1]:
        ancestors.append(parent)
        parent = parent[int(node)] if isinstance(parent, list) else parent[node]
    key = nodes[-1]
    if isinstance(parent, list):
        return ancestors[-1], nodes[-2], int(key)
    return parent, key, None


def number_origins(decision, snapshot):
    """Distinguish measurements from spec inputs and reproducible calculations.

    Covers the presented numbers only (``presented_values``). An origin names
    its records and their sources by ID; ``cited_sources`` lists each source
    once.
    """
    from decision.contract import NumberOrigin

    data = decision.model_dump(mode="json", include={
        "results": True,
        "top": {"__all__": {"evidence"}},
        "near_misses": True,
        "constraint_costs": True,
        "tipping_points": True,
        "eliminated": {"models"},
    })
    for path, value in presented_values(data):
        parent, key, list_index = _node(data, path)
        records = parent.get("records", []) if isinstance(parent, dict) else []
        if isinstance(parent, dict) and parent.get("record_id"):
            records = [parent["record_id"]]
        raw = (
            key == "raw_value"
            or key in ("value", "values")
            and ("record_id" in parent or "condition" in parent or "facet" in parent)
        )
        if raw and isinstance(parent, dict) and parent.get("preferred_value") is not None:
            # A value preference's raw_value is whether the value matched, not
            # the value: comparing it with the record failed every match (MODEL-203).
            basis = "1 when the value is the preferred one, 0 when it is not"
        elif raw and isinstance(parent, dict) and parent.get("formula"):
            # Computed per decision from the records listed (MODEL-153), so it is
            # checked against the formula, not against one record's value.
            basis = "computed per decision: " + parent["formula"]
        elif raw and records:
            basis = "snapshot measurement"

            def original(rid):
                record = checked_record(snapshot, rid)
                raw = record.get("score", record.get("value"))
                return raw[list_index] if list_index is not None and isinstance(raw, list) else raw

            if not any(value == original(rid) for rid in records):
                raise ExplanationError(f"{path}: value differs from retained record")
        elif key == "distance":
            basis = "distance from snapshot value to spec condition boundary, in original units"
        elif "/gain/" in path or "/refinement_gains/" in path:
            basis = "best relaxed raw objective value minus best current raw value"
        elif key == "threshold":
            basis = "optimise weight crossing with other weights and normalisation fixed"
        elif key == "value" and "dimension" in parent:
            basis = "feasible-set min-max normalisation of snapshot measurements"
        elif key == "n":
            basis = "sample count from snapshot evidence"
        else:
            basis = "count or ordinal from snapshot candidates after filtering and optimisation"
            records = []
        records = sorted(set(records))
        yield NumberOrigin(
            path=path, basis=basis, records=records, source_ids=source_ids(snapshot, records))


def source_ids(snapshot, records):
    """The registered sources behind checked records, by ID."""
    return sorted({source["source_id"] for rid in records
                   for source in checked_record(snapshot, rid)["sources"]})


def cited_sources(decision, snapshot):
    """Each source the origins and shown facts cite, once: URL, and the latest
    date a record in this decision citing it was verified."""
    from decision.contract import CitedSource

    records = {rid for origin in decision.number_origins for rid in origin.records}
    for row in decision.top:
        for fact in row.facts:
            records.update(fact.records)
            if fact.record_id:
                records.add(fact.record_id)
    verified = {}
    for rid in records:
        record = snapshot.record(rid)
        day = record["verification"].get("date")
        for source in record["sources"]:
            sid = source["source_id"]
            verified.setdefault(sid, None)
            if day and (verified[sid] is None or day > verified[sid]):
                verified[sid] = day
    return [CitedSource(id=sid, url=snapshot.source_url(sid), date=verified[sid])
            for sid in sorted(verified)]


def render_html(decision, snapshot):
    """A self-contained report. Source links are its only external resources."""
    from html import escape

    def esc(value):
        return escape(str(value))

    def quantity(value, unit):
        return "unknown" if value is None else f"{value:g} {esc(unit or 'unit not recorded')}"

    def links(records):
        urls = sorted(
            {
                snapshot.source_url(s["source_id"])
                for rid in records
                for s in checked_record(snapshot, rid)["sources"]
            }
        )
        return " ".join(f'<a href="{esc(url)}">Source</a>' for url in urls)

    def evidence(groups):
        out = []
        for group in groups:
            out.append(f"<h3>{esc(group.domain)}</h3>")
            if not group.items:
                out.append("<p>No verified evidence for this domain.</p>")
            for item in group.items:
                label = (
                    "Lab-reported"
                    if item.measured_by == "provider_self_report"
                    else item.measured_by
                )
                out.append(
                    f"<p><strong>{esc(label)}</strong> · {esc(item.benchmark)} "
                    f"· version {esc(item.version or 'not recorded')} "
                    f"· {esc(item.sub_category or 'aggregate')} "
                    f"· {quantity(item.value, item.unit)} "
                    f"· {esc(item.directness)} · {esc(item.date)} ({esc(item.date_type)}) "
                    f"· effort {esc(item.effort or 'not recorded')} "
                    f"· harness {esc(item.harness or 'not recorded')} "
                    f'<a href="{esc(item.source)}">Source</a></p>'
                )
        return "".join(out)

    def parts(contributions):
        out = []
        for c in contributions:
            out.append(
                f"<p>{esc(dimension_label(c))}: {quantity(c.raw_value, c.unit)}; "
                f"normalised value {quantity(c.value, 'dimensionless')}; "
                f"weight {quantity(c.weight, 'dimensionless')}. "
                + (f"Computed: {esc(c.formula)}. " if c.formula else "")
                + f"{esc(c.normalisation)} {links(c.records)}</p>"
            )
            groups = {}
            for item in c.evidence:
                groups.setdefault(item.requested_domain, []).append(item)
            out.append(
                evidence(
                    [DomainEvidence(domain=domain, items=items) for domain, items in groups.items()]
                )
            )
        return "".join(out)

    has_estimates = any(result.estimates for result in decision.results) or bool(
        decision.benchmark_exclusions and decision.benchmark_exclusions.estimate_changes
    )
    out = [
        '<!doctype html><html lang="en"><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>ModelSpec decision</title><style>",
        ":root{color-scheme:light dark;--bg:#fafafa;--fg:#17212b;--accent:#176b91}",
        "@media (prefers-color-scheme: dark){:root{--bg:#101820;--fg:#e7edf2;--accent:#75c9ed}}",
        "body{background:var(--bg);color:var(--fg);font:16px system-ui;max-width:1000px;",
        "margin:2rem auto;padding:0 1rem;line-height:1.6}a{color:var(--accent)}",
        "section{border-top:1px solid #888;padding:1rem 0}svg{width:100%}",
        "svg text{fill:var(--fg);font:14px system-ui}svg rect{fill:var(--accent)}",
        "</style><body><h1>ModelSpec decision</h1>",
        f"<p>{esc(decision.decision_id)} · {esc(decision.snapshot)} · {esc(decision.status)}</p>",
        (
            "<p>Capability estimates use verified evidence and include uncertainty intervals.</p>"
            if has_estimates
            else "<p>Evidence is unblended. Capability estimates and probabilities are not available.</p>"
        ),
    ]
    if decision.benchmark_exclusions is not None:
        exclusions = decision.benchmark_exclusions
        out.append(
            "<section><h2>Excluded benchmarks</h2><p>"
            + esc(", ".join(exclusions.benchmarks))
            + "</p>"
        )
        for change in exclusions.estimate_changes:
            before = change.before
            after = change.after
            before_text = (
                "unavailable"
                if before is None
                else f"{before.value:g} [{before.interval[0]:g}, {before.interval[1]:g}]"
            )
            after_text = (
                "unavailable"
                if after is None
                else f"{after.value:g} [{after.interval[0]:g}, {after.interval[1]:g}]"
            )
            records = [item.record_id for item in change.removed_drivers if item.record_id]
            removed_benchmarks = ", ".join(
                item.benchmark for item in change.removed_drivers
            )
            out.append(
                f"<p>{esc(change.model)} · {esc(change.domain)}: "
                f"{esc(before_text)} before; {esc(after_text)} after. "
                f"Removed drivers: {esc(removed_benchmarks)}. "
                f"{links(records)}</p>"
            )
        out.append("</section>")
    for r in decision.results:
        out.append(f"<section><h2>{esc(r.offering.model)}</h2>")
        if r.offering.provider:
            out.append(
                f"<p>{esc(r.offering.provider)} · {esc(r.offering.region)} "
                f"· {esc(r.offering.tier)}</p>"
            )
        out.append(parts(r.contributions) + evidence(r.evidence) + "</section>")
    if decision.explain == "full":
        # Rebuild SVG from typed values so an imported chart cannot inject HTML.
        out.append(
            "<section><h2>Contribution chart</h2>" + contribution_chart(decision) + "</section>"
        )
    out.append("<section><h2>Funnel</h2>")
    for step in decision.eliminated.funnel:
        out.append(
            f"<p>{esc(step.condition)}: {step.before} candidates before, "
            f"{step.after} candidates after, {step.may_qualify} candidates may qualify.</p>"
        )
    out.append("</section><section><h2>Constraint costs</h2>")
    for cost in decision.constraint_costs:
        out.append(f"<p>Relax {esc(cost.condition)}: admits {cost.admits} candidates.</p>")
        gains = [*cost.gain.items(),
                 *((f"{g.dimension}/{g.refinement}", g.gain) for g in cost.refinement_gains)]
        for dimension, gain in gains:
            out.append(
                f"<p>{esc(dimension)}: relaxed minus current = "
                f"{quantity(gain, cost.units.get(dimension))}. {links(cost.records)}</p>"
            )
        if not gains:
            out.append("<p>No comparable objective values.</p>")
    out.append("</section><section><h2>Near misses</h2>")
    for miss in decision.near_misses:
        value = (
            quantity(miss.value, miss.unit)
            if isinstance(miss.value, (int, float))
            else esc(miss.value)
        )
        out.append(
            f"<p>{esc(miss.offering.model)} · {esc(miss.condition)}: "
            f"{value}; "
            f"distance to boundary {quantity(miss.distance, miss.unit)}. "
            + (f"Computed: {esc(miss.formula)}. " if miss.formula else "")
            + f"{links(miss.records)}</p>"
        )
    out.append("</section><section><h2>Why others did not win</h2>")
    for reason in decision.eliminated.models:
        out.append(f"<p>{esc(reason.model)}: {esc(reason.condition)}. {links(reason.records)}</p>")
    for maybe in decision.may_qualify:
        out.append(
            f"<p>{esc(maybe.model)} may qualify; unknown: {esc(', '.join(maybe.unknown))}</p>"
        )
    for reason in decision.relax:
        out.append(f"<p>{esc(reason)}</p>")
    out.append("</section><section><h2>Tipping points</h2>")
    for point in decision.tipping_points:
        out.append(
            f"<p>{esc(dimension_label(point))}: "
            f"{quantity(point.threshold, 'dimensionless weight')}; "
            f"{esc(point.description)}; new top {esc(point.new_top)}.</p>"
        )
    out.append("</section>")
    if decision.top:
        out.append("<section><h2>Top candidates</h2>")
        for row, shown in top_contributions(decision):
            out.append(f"<h3>{esc(row.offering.model)}</h3>")
            for fact in row.facts:
                value = (
                    quantity(fact.value, fact.unit)
                    if isinstance(fact.value, (int, float)) and not isinstance(fact.value, bool)
                    else esc(fact.value)
                )
                provenance = (
                    links([fact.record_id]) if fact.record_id
                    else f"Computed: {esc(fact.formula)}. {links(fact.records)}" if fact.formula
                    else "Identity"
                )
                out.append(f"<p>{esc(fact.facet)}: {value}. {provenance}</p>")
            out.append(parts(shown) + evidence(row.evidence))
        out.append("</section>")
    out.append("</body></html>")
    return "".join(out)
