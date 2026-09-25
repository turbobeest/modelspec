"""Explain decisions using retained snapshot records, without capability blending."""

from __future__ import annotations

from decision.contract import Contribution, DomainEvidence, EvidenceItem
from decision.registry import facet as registry_facet


class ExplanationError(ValueError):
    """A displayed measurement cannot be traced to a verified snapshot record."""


def facet_unit(facet_id):
    return registry_facet(facet_id).unit


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


def evidence_item(snapshot, row, domain):
    record = checked_record(snapshot, row.record_id)
    if not row.verified or row.date is None or row.directness is None:
        raise ExplanationError(f"{row.record_id}: missing evidence date or domain directness")
    if record.get("score") != row.value:
        raise ExplanationError(f"{row.record_id}: evidence differs from retained record")
    measured = {"independent_evaluator": "independent"}.get(row.measured_by, row.measured_by)
    date_type = {"evaluated": "observed"}.get(row.date_type, row.date_type)
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
        harness=row.harness,
        date=row.date,
        date_type=date_type,
        source=snapshot.source_url(row.source_ids[0]),
        source_snapshot=row.source_snapshot,
        directness=row.directness,
        n=record.get("n"),
    )


def domain_evidence(snapshot, cid, domains):
    subjects = [cid]
    if snapshot.model_of(cid) != cid:
        subjects.append(snapshot.model_of(cid))
    return [
        DomainEvidence(
            domain=domain,
            items=[
                evidence_item(snapshot, row, domain)
                for subject in subjects
                for row in snapshot.evidence_for_domain(subject, domain)
                if row.verified
            ],
        )
        for domain in sorted(domains)
    ]


def contributions(snapshot, cid, parts, evidence):
    out = []
    for part in parts:
        records = []
        items = []
        unit = None
        if part.evidence:
            ids = {e.record_id for e in part.evidence}
            items = [item for group in evidence for item in group.items if item.record_id in ids]
            # A benchmark objective may have no requested domain. Do not invent directness.
            if not items:
                groups = domain_evidence(snapshot, cid, snapshot.domain_ids())
                items = [item for group in groups for item in group.items if item.record_id in ids]
            records = sorted(ids)
            unit = part.evidence[0].unit
            for rid in records:
                checked_record(snapshot, rid)
        elif part.raw_value is not None:
            facet_id = part.dimension.removeprefix("-")
            fact = snapshot.fact(cid, facet_id)
            checked_record(snapshot, fact.record_id)
            records = [fact.record_id]
            unit = facet_unit(facet_id)
        norm = part.normalisation
        out.append(
            Contribution(
                dimension=part.dimension,
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
            )
        )
    return out


def explain(decision, resolved, snapshot, filtered, ordered, selectors, domains):
    requested = set(resolved.spec.capabilities or {})
    for result, row in zip(decision.results, ordered.results):
        result.evidence = domain_evidence(snapshot, row.candidate_id, requested)
        result.contributions = contributions(
            snapshot, row.candidate_id, row.contributions, result.evidence
        )
    decision.eliminated.funnel = [step.as_contract() for step in filtered.funnel]
    _alternatives(decision, resolved, snapshot, filtered, ordered, selectors, domains)
    from decision.contract import TippingPoint

    decision.tipping_points = [
        TippingPoint(
            description=(
                f"{point.direction} weight past threshold; other weights and normalisation fixed"
            ),
            dimension=point.dimension,
            threshold=point.threshold,
            new_top=snapshot.model_of(point.new_top),
        )
        for point in ordered.tipping_points
    ]
    if decision.explain == "full":
        _full(decision, snapshot, filtered, ordered, requested)
        decision.chart = contribution_chart(decision)
        decision.number_origins = list(number_origins(decision, snapshot))


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

    from decision.contract import ConstraintCost, ModelElimination, NearMiss, render_condition
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
        gains, units, records = {}, {}, set()
        for dimension in current:
            before, after = best(ordered.results, dimension), best(alternative.results, dimension)
            if before is None or after is None:
                continue
            gains[dimension] = after - before
            for row in (*ordered.results, *alternative.results):
                for part in contributions(snapshot, row.candidate_id, row.contributions, []):
                    if part.dimension == dimension:
                        records.update(part.records)
                        units[dimension] = part.unit
        decision.constraint_costs.append(
            ConstraintCost(
                condition=text,
                admits=len(set(relaxed.feasible) - set(filtered.feasible)),
                gain=gains,
                units=units,
                records=sorted(records),
            )
        )
        for reason in single.eliminated:
            values = list(reason.value) if isinstance(reason.value, (tuple, list)) else []
            value = None if values else reason.value
            ref = offering_ref(snapshot, reason.candidate)
            records = []
            unit = None
            if reason.facet and reason.value is not None:
                fact = snapshot.fact(reason.candidate, reason.facet)
                if fact.record_id:
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
                    )
                )
            if (
                reason.candidate in relaxed.feasible
                and not reason.unverified
                and reason.candidate not in filtered.feasible
            ):
                decision.near_misses.append(
                    NearMiss(
                        offering=ref,
                        condition=text,
                        facet=reason.facet,
                        value=value,
                        values=values,
                        distance=_distance(reason, condition),
                        unit=unit,
                        records=records,
                    )
                )
    if decision.explain == "full":
        already = {m.offering.model_dump_json() for m in decision.eliminated.models}
        for reason in filtered.eliminated:
            ref = offering_ref(snapshot, reason.candidate)
            if ref.model_dump_json() not in already:
                decision.eliminated.models.append(
                    ModelElimination(
                        model=ref.model,
                        offering=ref,
                        condition=reason.condition,
                        value=reason.value,
                    )
                )
        for cid, dominators in ordered.dominance.items():
            ref = offering_ref(snapshot, cid)
            decision.eliminated.models.append(
                ModelElimination(
                    model=ref.model, offering=ref, condition="dominated by " + ", ".join(dominators)
                )
            )
        for cid in ordered.missing:
            ref = offering_ref(snapshot, cid)
            decision.eliminated.models.append(
                ModelElimination(model=ref.model, offering=ref, condition="missing objective value")
            )
        for row in ordered.results[len(decision.results) :]:
            ref = offering_ref(snapshot, row.candidate_id)
            decision.eliminated.models.append(
                ModelElimination(
                    model=ref.model, offering=ref, condition="outside requested result limit"
                )
            )


def _full(decision, snapshot, filtered, ordered, requested):
    from decision.contract import CandidateValues, ShownFact
    from decision.engine import offering_ref

    for row in ordered.results[:20]:
        cid = row.candidate_id
        facts = []
        for facet in snapshot.facet_ids():
            fact = snapshot.fact(cid, facet)
            if fact.state != "known":
                continue
            unit = None
            if fact.record_id:
                checked_record(snapshot, fact.record_id)
                unit = facet_unit(facet)
            facts.append(
                ShownFact(facet=facet, value=fact.value, unit=unit, record_id=fact.record_id)
            )
        evidence = domain_evidence(snapshot, cid, set(snapshot.domain_ids()) | requested)
        decision.top.append(
            CandidateValues(
                offering=offering_ref(snapshot, cid),
                facts=facts,
                evidence=evidence,
                contributions=contributions(snapshot, cid, row.contributions, evidence),
            )
        )


def contribution_chart(decision):
    """Faceted raw-value bars: dimensions with different units never share a scale."""
    from html import escape

    rows = [
        (r.offering.model, c)
        for r in decision.top
        for c in r.contributions
        if c.raw_value is not None
    ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 {max(60, len(rows) * 55)}" '
        'role="img" aria-label="Objective contributions in original units">'
    ]
    maxima = {
        c.dimension: max(
            abs(other.raw_value) for _, other in rows if other.dimension == c.dimension
        )
        for _, c in rows
    }
    for i, (model, c) in enumerate(rows):
        width = 300 * abs(c.raw_value) / (maxima[c.dimension] or 1)
        reported = (
            " · Lab-reported"
            if any(e.measured_by == "provider_self_report" for e in c.evidence)
            else ""
        )
        label = escape(
            f"{model}{reported} · {c.dimension}: {c.raw_value:g} {c.unit or 'unit not recorded'}"
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


def number_origins(decision, snapshot):
    """Distinguish measurements from spec inputs and reproducible calculations."""
    from decision.contract import NumberOrigin

    data = decision.model_dump(mode="json")
    all_records = set()

    def collect(node):
        if isinstance(node, dict):
            all_records.update(node.get("records", []))
            if node.get("record_id"):
                all_records.add(node["record_id"])
            for child in node.values():
                collect(child)
        elif isinstance(node, list):
            for child in node:
                collect(child)

    collect(data)
    # Include known condition facts even when no result survives.
    for cid in snapshot.candidates():
        for facet in snapshot.facet_ids():
            rid = snapshot.fact(cid, facet).record_id
            if rid:
                all_records.add(rid)
    for path, value in numbers(data):
        nodes = path.strip("/").split("/")
        parent = data
        ancestors = []
        for node in nodes[:-1]:
            ancestors.append(parent)
            parent = parent[int(node)] if isinstance(parent, list) else parent[node]
        key = nodes[-1]
        list_index = int(key) if isinstance(parent, list) else None
        if list_index is not None:
            parent = ancestors[-1]
            key = nodes[-2]
        records = parent.get("records", []) if isinstance(parent, dict) else []
        if isinstance(parent, dict) and parent.get("record_id"):
            records = [parent["record_id"]]
        raw = (
            key == "raw_value"
            or key in ("value", "values")
            and ("record_id" in parent or "condition" in parent or "facet" in parent)
        )
        if raw and records:
            basis = "snapshot measurement"

            def original(rid):
                record = checked_record(snapshot, rid)
                raw = record.get("score", record.get("value"))
                return raw[list_index] if list_index is not None and isinstance(raw, list) else raw

            if not any(value == original(rid) for rid in records):
                raise ExplanationError(f"{path}: value differs from retained record")
        elif key == "weight":
            basis = "spec objective weight; unweighted objectives use unit weight"
        elif key == "soft_penalty":
            basis = "sum of spec penalties on failed or unknown soft conditions"
        elif key == "distance":
            basis = "distance from snapshot value to spec condition boundary, in original units"
        elif "/gain/" in path:
            basis = "best relaxed raw objective value minus best current raw value"
        elif key == "threshold":
            basis = "optimise weight crossing with other weights and normalisation fixed"
        elif key == "value" and "dimension" in parent:
            basis = "feasible-set min-max normalisation of snapshot measurements"
        elif key == "n":
            basis = "sample count from snapshot evidence"
        else:
            basis = "count or ordinal from snapshot candidates after filtering and optimisation"
        records = sorted(set(records) or all_records)
        sources = sorted(
            {
                snapshot.source_url(s["source_id"])
                for rid in records
                for s in checked_record(snapshot, rid)["sources"]
            }
        )
        yield NumberOrigin(path=path, basis=basis, records=records, sources=sources)


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
                f"<p>{esc(c.dimension)}: {quantity(c.raw_value, c.unit)}; "
                f"normalised value {quantity(c.value, 'dimensionless')}; "
                f"weight {quantity(c.weight, 'dimensionless')}. "
                f"{esc(c.normalisation)} {links(c.records)}</p>"
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
        "<p>Evidence is unblended. Capability estimates and probabilities are not available.</p>",
    ]
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
        for dimension, gain in cost.gain.items():
            out.append(
                f"<p>{esc(dimension)}: relaxed minus current = "
                f"{quantity(gain, cost.units.get(dimension))}. {links(cost.records)}</p>"
            )
        if not cost.gain:
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
            f"distance to boundary {quantity(miss.distance, miss.unit)}. {links(miss.records)}</p>"
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
            f"<p>{esc(point.dimension)}: {quantity(point.threshold, 'dimensionless weight')}; "
            f"{esc(point.description)}; new top {esc(point.new_top)}.</p>"
        )
    out.append("</section>")
    if decision.top:
        out.append("<section><h2>Top candidates with every value</h2>")
        for row in decision.top:
            out.append(f"<h3>{esc(row.offering.model)}</h3>")
            for fact in row.facts:
                value = (
                    quantity(fact.value, fact.unit)
                    if isinstance(fact.value, (int, float)) and not isinstance(fact.value, bool)
                    else esc(fact.value)
                )
                out.append(
                    f"<p>{esc(fact.facet)}: {value}. "
                    f"{links([fact.record_id]) if fact.record_id else 'Identity'}</p>"
                )
            out.append(parts(row.contributions) + evidence(row.evidence))
        out.append("</section>")
    out.append("</body></html>")
    return "".join(out)
