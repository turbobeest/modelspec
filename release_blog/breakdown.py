"""Compile one model's release breakdown from signed snapshots (design §3).

``build_breakdown`` reads the snapshot pair and the decision engine and
nothing else: no card, no offering file, no verification log, no network.
Every number it returns is a ``Cited``. The same inputs give the same bytes
(``to_bytes``).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from datetime import date, timedelta
from typing import Any

from api.ranking.engine import neutrality_commitment
from decision.compare import compare
from decision.computed import COST_PER_TASK, with_computed
from decision.contract import DEFAULT_TASK_TOKENS, Decision, TaskTokens, parse_spec
from decision.engine import decide
from decision.plans import PRICE, QUOTE, load_plans
from decision.registry import default as default_registry
from decision.snapshot import EvidenceValue, LoadedSnapshot, canonical_json
from decision.templates import load_templates
from release_blog import VERSION, wording
from release_blog.gates import (
    CLAIM,
    INDEPENDENT,
    BreakdownError,
    check_publishable,
    guard_output,
    model_rows,
)
from release_blog.model import (
    AccuracyRef,
    Breakdown,
    Cited,
    ClaimRow,
    ClaimsVsEvidence,
    Cost,
    DecisionRef,
    Disclosures,
    DomainStanding,
    Driver,
    GeneratedFrom,
    GeneratorRef,
    HardwareFit,
    Leader,
    ModelRef,
    Named,
    NotYetMeasured,
    OfferingCost,
    PlanCoverage,
    Reading,
    Recheck,
    Setup,
    SnapshotRef,
    Speed,
    TaskSize,
    TemplateChange,
    TemplateChanges,
    TemplateRef,
    UnknownFacet,
    Unreported,
)
from release_blog.standing import domain_spec
from schema.suppliers import supplier_for

RECHECK_DAYS = (1, 7, 30)
SPEED_FACETS = ("offering.speed.time_to_first_token", "offering.speed.throughput")
ESTIMATE_UNIT = "capability estimate"
BACKFILL = (
    "This breakdown has no earlier snapshot to compare with, so it cannot say which "
    "decision templates the model changed."
)


def _band_of(decision: Decision, model_id: str) -> str | None:
    if decision.bands is None:
        return None
    for band in ("best", "rest", "thin"):
        if any(entry.model == model_id for entry in getattr(decision.bands, band)):
            return band
    return None


class _Compiler:
    def __init__(self, model_id: str, after: LoadedSnapshot, before: LoadedSnapshot | None,
                 registry: Any):
        self.model_id = model_id
        self.after = after
        self.before = before
        self.registry = registry
        self.sources: dict[str, str] = {}
        self.decisions: dict[str, DecisionRef] = {}
        if after.as_of is None:
            raise BreakdownError(f"snapshot {after.snapshot_id} has no as_of date")
        self.as_of: date = after.as_of

    # provenance ------------------------------------------------------------

    def _read_date(self, record_id: str, snapshot: LoadedSnapshot | None = None) -> date:
        record = (snapshot or self.after).record(record_id)
        verification = record.get("verification") or {}
        day = verification.get("date")
        if not day:
            raise BreakdownError(f"record {record_id} has no verification date")
        return date.fromisoformat(str(day)[:10])

    def _sources(self, source_ids: Iterable[str], snapshot: LoadedSnapshot | None = None,
                 ) -> list[str]:
        snapshot = snapshot or self.after
        ids = sorted(set(source_ids))
        for source_id in ids:
            self.sources[source_id] = snapshot.source_url(source_id)
        return ids

    def record(self, value: float, unit: str | None, record_id: str,
               source_ids: Iterable[str] = ()) -> Cited:
        return Cited(value=value, unit=unit, record_id=record_id,
                     source_ids=self._sources(source_ids), read_date=self._read_date(record_id))

    def computed(self, value: float, unit: str | None, computed: str, *,
                 records: Iterable[str] = (), decision_id: str | None = None,
                 source_ids: Iterable[str] = (), low: float | None = None,
                 high: float | None = None) -> Cited:
        records = sorted(set(records))
        return Cited(value=value, unit=unit, low=low, high=high, computed=computed,
                     records=records, decision_id=decision_id,
                     source_ids=self._sources(source_ids), read_date=self.as_of)

    def decide(self, purpose: str, spec: Mapping[str, Any], snapshot: LoadedSnapshot) -> Decision:
        decision = decide(parse_spec(dict(spec), facets=self.registry.facet), snapshot,
                          facets=self.registry.facet)
        self.decisions.setdefault(decision.decision_id, DecisionRef(
            purpose=purpose, spec=dict(spec), spec_hash=decision.spec_hash,
            decision_id=decision.decision_id, snapshot_id=snapshot.snapshot_id))
        return decision

    # sections ----------------------------------------------------------------

    def _setup(self, row: EvidenceValue) -> Setup:
        return Setup(version=row.version, subcategory=row.subcategory, harness=row.harness,
                     effort=row.effort, date=row.date)

    def _limitations(self, record_id: str | None) -> str | None:
        if record_id is None:
            return None
        text = self.after.record(record_id).get("limitations")
        return str(text) if text else None

    def _row(self, row: EvidenceValue) -> Cited:
        if row.record_id is None:
            raise BreakdownError(f"{self.model_id}: {row.benchmark_id} row has no record")
        return self.record(row.value, row.unit, row.record_id, row.source_ids)

    def _reading(self, claim: EvidenceValue, row: EvidenceValue) -> Reading:
        differs = [part for part in ("unit", "subcategory")
                   if getattr(claim, part) != getattr(row, part)]
        if differs:
            comparability = "not_comparable"
        else:
            differs = [part for part in ("version", "harness", "effort")
                       if getattr(claim, part) != getattr(row, part)]
            comparability = "different_setup" if differs else "same_setup"
        difference = None
        if comparability == "same_setup":
            if claim.record_id is None or row.record_id is None:
                raise BreakdownError(f"{self.model_id}: {row.benchmark_id} row has no record")
            difference = self.computed(
                round(row.value - claim.value, 6), row.unit, "difference",
                records=[claim.record_id, row.record_id])
        within = None
        if row.interval is not None:
            low, high = row.interval
            within = low <= claim.value <= high
        return Reading(
            value=self._row(row), measured_by=str(row.measured_by), setup=self._setup(row),
            n=(None if row.n is None or row.record_id is None
               else self.record(row.n, "items", row.record_id, row.source_ids)),
            quality_flags=list(row.quality_flags), limitations=self._limitations(row.record_id),
            comparability=comparability, differs_in=differs, difference=difference,
            claim_within_interval=within)

    def claims(self, estimated_domains: Sequence[str]) -> ClaimsVsEvidence:
        rows = sorted(model_rows(self.after, self.model_id),
                      key=lambda r: (r.benchmark_id, r.record_id or ""))
        claimed = [row for row in rows if row.measured_by == CLAIM]
        independent = [row for row in rows if row.measured_by in INDEPENDENT]
        out = []
        for claim in claimed:
            readings = [self._reading(claim, row) for row in independent
                        if row.benchmark_id == claim.benchmark_id]
            out.append(ClaimRow(
                benchmark=claim.benchmark_id, claim=self._row(claim), setup=self._setup(claim),
                limitations=self._limitations(claim.record_id), readings=readings,
                status="read" if readings else "no_independent_reading_yet"))
        claimed_ids = {row.benchmark_id for row in claimed}
        tags = self.after.benchmark_domain_tags()
        unreported = [
            Unreported(benchmark=row.benchmark_id, reading=self._row(row),
                       measured_by=str(row.measured_by), setup=self._setup(row))
            for row in independent
            if row.benchmark_id not in claimed_ids
            and any(domain in estimated_domains for domain, _ in tags.get(row.benchmark_id, ()))
        ]
        return ClaimsVsEvidence(claims=out, unreported=unreported)

    def _estimate(self, model_id: str, domain_id: str) -> Cited | None:
        found = self.after.capability_estimate(model_id, domain_id)
        if found is None:
            return None
        drivers = self.after.capability_drivers(model_id, domain_id)
        return self.computed(found.value, ESTIMATE_UNIT, "capability.estimate",
                             records=[d.record_id for d in drivers], low=found.low,
                             high=found.high)

    def standing(self, model_class: str) -> list[DomainStanding]:
        out = []
        for domain in self.registry.domains():
            estimate = self._estimate(self.model_id, domain.id)
            if estimate is None:
                continue
            decision = self.decide(f"standing.{domain.id}", domain_spec(domain.id, model_class),
                                   self.after)
            did = decision.decision_id
            result = next((r for r in decision.results if r.model == self.model_id), None)
            best = decision.bands.best if decision.bands is not None else []
            ranked = len({r.model for r in decision.results})
            leaders = [
                Leader(model=entry.model, estimate=self._estimate(entry.model, domain.id),
                       p_best=(None if entry.p_best is None else self.computed(
                           entry.p_best, "probability", "decision.p_best", decision_id=did)))
                for entry in best[:3]
            ]
            out.append(DomainStanding(
                domain=Named(id=domain.id, name=domain.name), estimate=estimate, decision=did,
                rank=(None if result is None or result.model_rank is None else self.computed(
                    result.model_rank, "place", "decision.model_rank", decision_id=did)),
                band=_band_of(decision, self.model_id),
                band_size=self.computed(len(best), "models", "decision.bands.best",
                                        decision_id=did),
                ranked_models=self.computed(ranked, "models", "decision.ranked_models",
                                            decision_id=did),
                p_best=(None if result is None or result.p_best is None else self.computed(
                    result.p_best, "probability", "decision.p_best", decision_id=did)),
                top3_stability=(None if result is None or result.top3_stability is None
                                else self.computed(result.top3_stability, "probability",
                                                   "decision.top3_stability", decision_id=did)),
                leaders=leaders,
                drivers=[Driver(record_id=d.record_id, benchmark=d.benchmark_id,
                                version=d.version)
                         for d in self.after.capability_drivers(self.model_id, domain.id)],
            ))
        return out

    def templates(self) -> tuple[TemplateChanges, list[dict[str, Any]]]:
        if self.before is None:
            return TemplateChanges(unavailable=BACKFILL), []
        changes, listed = [], []
        for template in load_templates(registry=self.registry):
            purpose = f"template.{template['id']}"
            old = self.decide(purpose, template["spec"], self.before)
            new = self.decide(purpose, template["spec"], self.after)
            band_before = _band_of(old, self.model_id)
            band_after = _band_of(new, self.model_id)
            top_before = [e.model for e in (old.bands.best if old.bands else [])]
            top_after = [e.model for e in (new.bands.best if new.bands else [])]
            displaced = [m for m in top_before if m not in top_after]
            # Only answers the model is in: churn elsewhere between the two
            # snapshots is not this model's doing.
            if band_before is None and band_after is None:
                continue
            counts = compare(old, new)["counts"]
            changes.append(TemplateChange(
                template=TemplateRef(id=template["id"], category=template["category"],
                                     tier=template["tier"], name=template["name"]),
                decisions={"before": old.decision_id, "after": new.decision_id},
                band_before=band_before, band_after=band_after,
                model_in_best={"before": band_before == "best", "after": band_after == "best"},
                top_before=top_before, top_after=top_after, displaced=displaced,
                compare_counts={key: self.computed(value, "models", "decision.compare",
                                                   decision_id=new.decision_id)
                                for key, value in sorted(counts.items())},
            ))
            listed.append(template)
        return TemplateChanges(changes=changes), listed

    def _offerings(self) -> list[str]:
        return sorted(cid for cid in self.after.candidates()
                      if self.after.kind(cid) == "offering"
                      and self.after.model_of(cid) == self.model_id)

    def _fact(self, cid: str, facet_id: str, unit: str | None = None) -> Cited | None:
        found = self.after.fact(cid, facet_id)
        if (found.state != "known" or found.record_id is None
                or isinstance(found.value, bool) or not isinstance(found.value, int | float)):
            return None
        if unit is None:
            unit = self.registry.facet(facet_id).unit
        return self.record(found.value, unit, found.record_id, found.sources)

    def cost(self, templates: Sequence[Mapping[str, Any]], model_class: str) -> Cost:
        sizes: list[tuple[TaskTokens, str]] = [(DEFAULT_TASK_TOKENS, "contract_default")]
        for template in templates:
            raw = template.get("task_tokens")
            if raw:
                tokens = TaskTokens(**raw)
                if all(tokens != seen for seen, _ in sizes):
                    sizes.append((tokens, f"template:{template['id']}"))
        offerings = []
        for tokens, basis in sizes:
            priced = with_computed(self.after, tokens)
            for cid in self._offerings():
                found = priced.computed(cid, COST_PER_TASK)
                offerings.append(OfferingCost(
                    offering=cid, provider=str(self.after.fact(cid, "offering.provider").value),
                    region=str(self.after.fact(cid, "offering.region").value),
                    tier=str(self.after.fact(cid, "offering.tier").value),
                    task=TaskSize(input=tokens.input, output=tokens.output, basis=basis),
                    cost_per_task=(None if found is None else self.computed(
                        found.value, "USD", COST_PER_TASK, records=found.records,
                        source_ids=found.sources)),
                    price_input=self._fact(cid, "offering.price.input"),
                    price_output=self._fact(cid, "offering.price.output")))
        return Cost(offerings=offerings, plans=self.plans(model_class))

    def plans(self, model_class: str) -> list[PlanCoverage]:
        spec = {
            "spec_version": 1,
            "where": [f"model.class = {model_class}"],
            "access": {"kind": "coding_tool"},
            "optimize": {"weights": {"software_engineering": 1.0}},
            "explain": "full",
            "limit": 500,
        }
        routes: dict[str, Any] = {}
        decision_id = None
        if self.after.subscription_offerings():
            decision = self.decide("cost.coding_tool_plans", spec, self.after)
            decision_id = decision.decision_id
            for result in decision.results:
                if result.model != self.model_id:
                    continue
                for route in result.plans:
                    known = routes.get(route.plan)
                    if known is None or (known.break_even_tasks_per_month is None
                                         and route.break_even_tasks_per_month is not None):
                        routes[route.plan] = route
        facts = {row["id"]: row["facts"] for row in self.after.subscription_offerings()}
        out = []
        for plan_id, plan in sorted(load_plans(self.after, self.registry).items()):
            models = plan.models
            covers: bool | str = "unknown" if models is None else self.model_id in models
            entry = plan.covers(self.model_id) if covers is True else None
            quote_fact = facts[plan_id].get(QUOTE)
            price_fact = facts[plan_id].get(PRICE)
            monthly = None
            if plan.monthly is not None and price_fact is not None and price_fact.record_id:
                if plan.price is not None and plan.price.period == "monthly":
                    monthly = self.record(plan.monthly, "USD per month", price_fact.record_id,
                                          price_fact.sources)
                else:
                    monthly = self.computed(plan.monthly, "USD per month", "plan.monthly",
                                            records=[price_fact.record_id],
                                            source_ids=price_fact.sources)
            route = routes.get(plan_id)
            break_even = None
            if route is not None and route.break_even_tasks_per_month is not None:
                break_even = self.computed(
                    route.break_even_tasks_per_month, "tasks per month",
                    "plan.break_even_tasks_per_month", decision_id=decision_id)
            out.append(PlanCoverage(
                plan={"id": plan.id, "provider": plan.provider, "name": plan.name},
                covers=covers, rule=None if entry is None else entry.rule,
                quote=None if entry is None else entry.quote,
                quote_record=(None if entry is None or entry.quote is None or quote_fact is None
                              else quote_fact.record_id),
                monthly=monthly, break_even=break_even,
                surface=None if route is None else route.surface))
        return out

    def hardware(self) -> HardwareFit | None:
        openness = self.after.fact(self.model_id, "model.weights_openness")
        if openness.state != "known" or openness.value != "open_weights":
            return None
        fits = self.after.fact(self.model_id, "model.fits_hardware")
        indeterminate = self.after.fact(self.model_id, "model.hardware_fit_indeterminate")
        return HardwareFit(
            weights_openness=str(openness.value),
            fits=sorted(fits.value) if fits.state == "known" and fits.value is not None else None,
            fits_record=fits.record_id if fits.state == "known" else None,
            indeterminate=(sorted(indeterminate.value)
                           if indeterminate.state == "known" and indeterminate.value is not None
                           else None),
            indeterminate_record=(indeterminate.record_id if indeterminate.state == "known"
                                  else None))

    def gaps(self, standings: Sequence[DomainStanding], claims: ClaimsVsEvidence,
             ) -> NotYetMeasured:
        offerings = self._offerings()
        unknown = []
        for facet in sorted(self.registry.facets(), key=lambda f: f.id):
            if facet.tier != "guaranteed" or facet.computed_by:
                continue
            subjects = ([self.model_id] if facet.subject == "model"
                        else offerings if facet.subject == "offering" else [])
            missing = [cid for cid in subjects if self.after.fact(cid, facet.id).state == "unknown"]
            if missing:
                unknown.append(UnknownFacet(facet=facet.id, subjects=missing))
        held: Counter[str] | None = Counter()
        for cid in [self.model_id, *offerings]:
            counts = self.after.held_back(cid)
            if counts is None:
                held = None
                break
            held.update(counts)
        estimated = {row.domain.id for row in standings}
        speed = [
            Speed(offering=cid, **{
                facet.rsplit(".", 1)[1]: self._fact(cid, facet) or "unknown"
                for facet in SPEED_FACETS})
            for cid in offerings
        ]
        return NotYetMeasured(
            unknown_facets=unknown,
            held_back=None if held is None else {
                reason: self.computed(count, "records", "snapshot.held_back")
                for reason, count in sorted(held.items())},
            domains_without_estimate=[d.id for d in self.registry.domains()
                                      if d.id not in estimated],
            claims_without_reading=sorted({row.benchmark for row in claims.claims
                                           if row.status == "no_independent_reading_yet"}),
            speed=speed)


def _snapshot_ref(snapshot: LoadedSnapshot) -> SnapshotRef:
    if snapshot.signature_key_id is None:
        raise BreakdownError(f"snapshot {snapshot.snapshot_id} is not Ed25519-signed")
    return SnapshotRef(snapshot_id=snapshot.snapshot_id, content_hash=snapshot.content_hash,
                       as_of=snapshot.as_of, key_id=snapshot.signature_key_id)


def _cited_leaves(value: Any, pointer: str = "") -> Iterable[tuple[str, Any]]:
    if isinstance(value, Mapping):
        if "read_date" in value and "value" in value:
            yield pointer, value
            return
        for key in sorted(value):
            yield from _cited_leaves(value[key], f"{pointer}/{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _cited_leaves(item, f"{pointer}/{index}")


def changes_since(first: Breakdown, current: dict[str, Any]) -> list[dict[str, Any]]:
    """Every cited value that differs from ``first``, by JSON pointer."""
    old = dict(_cited_leaves(first.model_dump(mode="json", by_alias=True)))
    new = dict(_cited_leaves(current))
    return [
        {"pointer": pointer, "old": old.get(pointer), "new": new.get(pointer)}
        for pointer in sorted(set(old) | set(new))
        if (old.get(pointer) or {}).get("value") != (new.get(pointer) or {}).get("value")
    ]


def build_breakdown(
    *,
    model_id: str,
    after: LoadedSnapshot,
    before: LoadedSnapshot | None,
    accuracy: Mapping[str, Any],
    revision: int = 1,
    first_revision: Breakdown | None = None,
    registry: Any = None,
    name: str | None = None,
    first_published: date | None = None,
    early_access: str | None = None,
) -> Breakdown:
    """The breakdown of ``model_id`` in ``after``, compared with ``before``."""
    registry = registry or default_registry()
    if accuracy.get("snapshot") != after.snapshot_id or accuracy.get("status") != "pass":
        raise BreakdownError("the accuracy report does not pass for the after snapshot")
    if revision > 1 and first_revision is None:
        raise BreakdownError("a later revision needs revision 1 to diff against")
    reasons = check_publishable(after, model_id)
    if reasons:
        raise BreakdownError("; ".join(reasons))
    if before is not None and model_id in before.candidates():
        raise BreakdownError(f"{model_id} is already in the before snapshot "
                             f"{before.snapshot_id}")
    found = after.fact(model_id, "model.class")
    if found.state != "known" or not isinstance(found.value, str):
        raise BreakdownError(f"{model_id}: model.class is unknown")
    model_class = found.value
    c = _Compiler(model_id, after, before, registry)
    standings = c.standing(model_class)
    claims = c.claims([row.domain.id for row in standings])
    template_changes, listed = c.templates()
    cost = c.cost(listed, model_class)
    gaps = c.gaps(standings, claims)
    published = first_published or (first_revision.recheck.first_published
                                    if first_revision else c.as_of)
    title = wording.headline(
        name=name or model_id,
        best=[(row.domain.name, row.band_size.value == 1) for row in standings
              if row.band == "best"],
        ranked_outside=[row.domain.name for row in standings if row.band == "rest"],
        thin=[row.domain.name for row in standings if row.band == "thin"],
        claims=len(claims.claims),
        claims_read=sum(row.status == "read" for row in claims.claims),
        same_setup=sum(r.comparability == "same_setup" for row in claims.claims
                       for r in row.readings),
    )
    supplier = supplier_for(model_id.split("/", 1)[0])
    body: dict[str, Any] = {
        "model": ModelRef(id=model_id, name=name or model_id,
                          provider=model_id.split("/", 1)[0], class_=model_class),
        "revision": revision,
        "headline": title,
        "generated_from": GeneratedFrom(
            after=_snapshot_ref(after),
            before=None if before is None else _snapshot_ref(before),
            accuracy=AccuracyRef(snapshot=after.snapshot_id, profile="pr", status="pass"),
            generator=GeneratorRef(version=VERSION)),
        "decisions": sorted(c.decisions.values(), key=lambda d: (d.purpose, d.snapshot_id)),
        "claims_vs_evidence": claims,
        "standing": standings,
        "template_changes": template_changes,
        "cost": cost,
        "hardware": c.hardware(),
        "not_yet_measured": gaps,
        "recheck": Recheck(first_published=published, schedule=[
            {"day": day, "due": (published + timedelta(days=day)).isoformat(),
             "revision": None} for day in RECHECK_DAYS]),
        "disclosures": Disclosures(
            supplier=None if supplier is None else f"{supplier.relationship} {supplier.rule}",
            early_access=early_access, neutrality=neutrality_commitment()["pledge"]),
        "sources": dict(sorted(c.sources.items())),
    }
    breakdown = Breakdown(**body)
    if first_revision is not None:
        dumped = breakdown.model_dump(mode="json", by_alias=True)
        breakdown = breakdown.model_copy(
            update={"changes_since_r1": changes_since(first_revision, dumped)})
    guard_output(breakdown.sources, to_bytes(breakdown).decode("utf-8"))
    return breakdown


def to_bytes(breakdown: Breakdown) -> bytes:
    """Canonical JSON, the snapshot's own encoding, with a trailing newline."""
    return canonical_json(breakdown.model_dump(mode="json", by_alias=True)) + b"\n"
