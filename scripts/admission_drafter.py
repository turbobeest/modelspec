#!/usr/bin/env python3
"""Draft a release's sourced facts and exact premier-admission gaps.

Dry runs fetch first-party pages into a temporary cache and print a JSON packet.
--write files verified facts and provenance in a private data checkout. A new
offering and premier entry are filed together only after the real gate passes.
The caller opens one draft PR; this command never operates git or calls a model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass, field, replace
from datetime import UTC, date, datetime
from pathlib import Path
from urllib.parse import urlsplit

import httpx
import yaml

from decision.excluded import excluded_sources
from decision.model import Fact, Source, SourceRef, TargetRef, VerificationActor
from decision.normalise import NORMALISERS
from decision.registry import default as default_registry
from decision.retention import (
    canonical_host, cite_only_hosts, cite_only_origin_restrictive, cite_only_origin_status,
)
from decision.snapshot import Gap, audit_build, collect_repo
from decision.sources import CopyStore, Fetcher, load_sources
from decision.units import UNITS, unit_id
from decision.verify import (
    Claim,
    ExtractorError,
    Queue,
    StoredRegions,
    VerificationLog,
    deterministic_extractors,
    normalise_name,
    parse_quantity,
    split_model_cell,
    verify,
)
from pipeline.load import split_front_matter
from scripts.model_143_collect import LABELS

COLLECTOR = VerificationActor(
    agent="modelspec-admission-drafter", model_family="deterministic",
    method="admission-candidates@1",
)
MODEL_ID = re.compile(r"[a-z0-9][a-z0-9.-]*/[a-z0-9][a-z0-9.-]*\Z")
# Ownership is code-reviewed. A URL on a card is not proof of first-party status.
LAB_HOSTS = {
    "anthropic": ("anthropic.com", "claude.com"),
    "openai": ("openai.com",),
    "google": ("ai.google.dev", "deepmind.google", "cloud.google.com"),
    "mistral": ("mistral.ai",),
    "xai": ("x.ai",),
    "perplexity": ("perplexity.ai",),
    "deepseek": ("deepseek.com",),
    "meta": ("ai.meta.com", "ai.developer.meta.com"),
}
PRICE_URLS = {
    "anthropic": "https://platform.claude.com/docs/en/about-claude/pricing",
    "openai": "https://developers.openai.com/api/docs/pricing",
    "google": "https://ai.google.dev/gemini-api/docs/pricing",
    "mistral": "https://mistral.ai/pricing",
    "xai": "https://docs.x.ai/docs/models",
}
API_PROVIDERS = {"google": "google-gemini-api", "meta": "meta-model-api"}
IDENTITY_FACETS = {"offering.provider", "offering.region", "offering.tier"}
OFFERING_LABELS = {
    "offering.price.input": "input", "offering.price.output": "output",
    "offering.price.cached_input": "cached input",
    "offering.price.batch_input": "batch input",
    "offering.price.batch_output": "batch output",
    "offering.data.retention": "data retention",
    "offering.data.trains_on_customer_data": "data trains on customer data",
    "offering.data.zero_retention": "zero data retention",
    "offering.attestation.soc2": "attestation soc2",
    "offering.attestation.baa": "attestation baa",
}


def offering_identity(offering):
    return "/".join(str(offering[k]) for k in ("provider", "model", "region", "tier"))


def load_source_terms(root: Path) -> dict:
    try:
        terms = json.loads((root / "registry/source-terms.json").read_text())
    except (OSError, ValueError):
        return {}
    return terms if isinstance(terms, dict) else {}


def source_block(url: str, lab: str, terms: dict) -> str | None:
    # One canonical host (MODEL-420): a URL the repository's parser rejects, or
    # one with userinfo or an invalid port, is blocked, never guessed.
    try:
        parsed = urlsplit(url)
        host = canonical_host(url)
        port = parsed.port
    except ValueError:
        return "source requires a well-formed HTTPS URL"
    if (host is None or parsed.scheme != "https" or parsed.username or parsed.password
            or port not in (None, 443)):
        return "source requires an HTTPS URL without credentials or a custom port"
    if excluded_sources().url(url):
        return "excluded source"
    if not any(host == h or host.endswith("." + h) for h in LAB_HOSTS.get(lab, ())):
        return f"blocked host {host}: first-party ownership is not registered for {lab}"
    if host not in cite_only_hosts() and terms.get(host) not in ("permits", "restricts"):
        return "source-terms hold (MODEL-409)"
    return None


class SourceBlockedError(ValueError):
    """Stop an HTTP redirect before the target receives a request."""


class AdmissionFetcher(Fetcher):
    def __init__(self, client, *, lab: str, terms: dict, **kwargs):
        super().__init__(client, **kwargs)

        def check_request(request):
            if reason := source_block(str(request.url), lab, terms):
                raise SourceBlockedError(reason)

        client.event_hooks["request"].append(check_request)


def source_candidates(card: dict, registered: dict) -> list[Source]:
    mid = card["model_id"]
    lab, slug = mid.split("/")
    urls = {}
    for key, value in (card.get("sources") or {}).items():
        if key.endswith("_url") and value:
            urls[str(value)] = "lab_documentation"
    primary = (card.get("availability") or {}).get("primary_provider") or {}
    if primary.get("platform_url"):
        urls[primary["platform_url"]] = "lab_documentation"
    for key in ("license_url", "tos_url"):
        if value := (card.get("licensing") or {}).get(key):
            urls[value] = "licence_text" if key == "license_url" else "provider_terms"
    version = str(card.get("version") or slug)
    if re.fullmatch(r"[a-zA-Z0-9.-]+", version):
        if lab == "openai":
            urls[f"https://developers.openai.com/api/docs/models/{version}"] = "lab_documentation"
        elif lab == "anthropic":
            urls[f"https://platform.claude.com/docs/en/models/"
                 f"{version.removeprefix('claude-')}/overview"] = "lab_documentation"
    if lab in PRICE_URLS:
        urls[PRICE_URLS[lab]] = "provider_documentation"
    refs = {r["source_id"] for f in card.get("facts") or [] for r in f.get("sources", [])}
    selected = {s.id: s for s in registered.values() if s.id in refs}
    for url, kind in sorted(urls.items()):
        # Historical entries may describe a text projection, not today's raw HTML.
        sid = "admission-" + hashlib.sha256(url.encode()).hexdigest()[:20]
        normaliser = next((s.normaliser for s in registered.values()
                           if str(s.url) == url
                           and NORMALISERS[s.normaliser].content == "html"), "html-default")
        selected[sid] = Source(
            id=sid, url=url, kind=kind, normaliser=normaliser,
            cited_regions=[{"id": "page", "locator": {"kind": "page"}}],
        )
    return list(selected.values())


def candidate_value(reading, facet):
    raw = reading.value
    if raw is None:
        return None
    kind = facet.value_type.kind
    if kind == "number":
        if facet.value_type.unbounded and raw == "unbounded":
            return raw
        if facet.value_type.not_offered and normalise_name(str(raw)) in {
            "not offered", "n a", "na", "not available", "not supported",
        }:
            return "not_offered"
        quantity = parse_quantity(str(raw), reading.unit or facet.unit)
        if quantity is None:
            return None
        source_unit = unit_id(quantity.unit or facet.unit)
        target_unit = unit_id(facet.unit)
        number = quantity.number
        if source_unit != target_unit:
            if source_unit not in UNITS or target_unit not in UNITS:
                return None
            source_dimension, source_scale = UNITS[source_unit]
            target_dimension, target_scale = UNITS[target_unit]
            if source_dimension != target_dimension:
                return None
            number *= source_scale / target_scale
        return int(number) if float(number).is_integer() else number
    if kind == "boolean":
        text = str(raw).strip().lower()
        if text in {"yes", "true", "supported", "available"}:
            return True
        if text in {"no", "false", "not supported", "unavailable"}:
            return False
        return None
    if kind == "set":
        return [s.strip() for s in re.split(r",|;|\band\b", str(raw)) if s.strip()]
    return str(raw).strip()


def read_facts(subject, names, facets, references, regions, today, registry):
    """Propose typed reader values, then run the existing verifier on each one."""
    found = {}
    issues = []
    own_names = {normalise_name(n) for n in names}
    extractors = deterministic_extractors()
    for facet in facets:
        candidates = {}
        for ref in references:
            source = regions.sources[ref.source_id]
            if source.kind not in facet.permitted_source_kinds:
                continue
            for region_id in ref.cited_regions:
                if regions.cite_only(ref.source_id, ref.snapshot_ref):
                    continue
                text = regions.text(ref.source_id, ref.snapshot_ref, region_id)
                if text is None:
                    continue
                narrow_ref = ref.model_copy(update={"cited_regions": [region_id]})
                probe = Claim(
                    target=TargetRef(kind="fact", id=f"{subject}#{facet.id}"),
                    subject=subject, names=names, field=facet.id,
                    label=LABELS.get(facet.id, OFFERING_LABELS.get(facet.id)),
                    value=None, unit=facet.unit,
                    collector=COLLECTOR, sources=(narrow_ref,),
                )
                for extractor in extractors:
                    if not extractor.accepts(text):
                        continue
                    try:
                        readings = extractor.extract(probe, text)
                    except ExtractorError:
                        continue
                    for reading in readings:
                        if (not reading.subject
                                or split_model_cell(reading.subject)[0] not in own_names):
                            continue
                        value = candidate_value(reading, facet)
                        if value is None:
                            continue
                        try:
                            fact = Fact.model_validate({
                                "id": probe.target.id,
                                "subject": {"kind": facet.subject, "id": subject},
                                "facet": facet.id, "state": "known", "value": value,
                                "sources": [narrow_ref.model_dump(mode="json")],
                            }, context={"registry": registry})
                        except ValueError:
                            continue
                        claim = replace(probe, value=value)
                        result = verify(claim, regions, extractors, today=today)
                        if result.outcome == "verified":
                            candidates.setdefault(
                                json.dumps(value, sort_keys=True), (fact, claim, result))
        if len(candidates) == 1:
            found[facet.id] = next(iter(candidates.values()))
        elif len(candidates) > 1:
            issues.append(Gap(subject, subject, facet.id, "conflicting verified source readings"))
    return found, issues


@dataclass
class Packet:
    model_id: str
    checked_on: date
    model_facts: list[dict]
    offering: dict | None
    benchmarks: list[dict]
    gaps: list[Gap]
    sources: list[dict]
    checks: list = field(repr=False)
    registrations: dict = field(repr=False)
    lineup_entry: dict | None = None

    @property
    def ready(self):
        return not self.gaps

    def to_dict(self):
        return {
            "model": self.model_id, "checked_on": self.checked_on.isoformat(),
            "ready": self.ready, "model_facts": self.model_facts,
            "offering": self.offering, "benchmarks": self.benchmarks,
            "gaps": [asdict(g) for g in self.gaps], "sources": self.sources,
            "lineup_entry": self.lineup_entry if self.ready else None,
        }

    def markdown(self):
        lines = [f"# Admission packet: {self.model_id}", "",
                 f"Read on {self.checked_on}. Draft for human review.",
                 f"Lineup entry: {'included' if self.ready else 'withheld'}.", "",
                 f"{len(self.model_facts)} verified model facts; "
                 f"{len(self.benchmarks)} catalogue benchmark records.", "",
                 f"Full packet: `reports/admission/{self.model_id}.json`.",
                 "Workflow artifacts contain only the packet and source manifest.", "",
                 "## Guaranteed-fact gaps", ""]
        lines += [f"- {gap}" for gap in self.gaps] or ["None."]
        lines += ["", "## Sources", ""]
        lines += [f"- {s['url']}: {s['outcome']}"
                  + (f"; {s['reason']}" if s.get("reason") else "") for s in self.sources]
        return "\n".join(lines) + "\n"

    def write(self, root: Path):
        path = root / "models" / f"{self.model_id}.md"
        card, prose = split_front_matter(path.read_text())
        facts = {f["facet"]: f for f in card.get("facts") or []}
        facts.update({f["facet"]: f for f in self.model_facts})
        if self.model_facts:
            card["facts"] = list(facts.values())
            path.write_text("---\n" + yaml.safe_dump(card, sort_keys=False, allow_unicode=True)
                            + "---\n" + prose)
        to_file = self.checks if self.ready else [
            entry for entry in self.checks if entry[0].subject == self.model_id
        ]
        used = {ref.source_id for claim, _ in to_file for ref in claim.sources}
        if used:
            source_path = root / "registry/sources.yaml"
            source_path.parent.mkdir(parents=True, exist_ok=True)
            registered = load_sources(source_path)
            registered.update({sid: self.registrations[sid] for sid in used})
            source_path.write_text(yaml.safe_dump({
                "schema_version": 1,
                "sources": [s.model_dump(mode="json", exclude_none=True)
                            for s in registered.values()],
            }, sort_keys=False, allow_unicode=True))
        queue, log = Queue(root / "verification"), VerificationLog(root / "verification")
        at = datetime.combine(self.checked_on, datetime.min.time(), tzinfo=UTC)
        filed, latest = queue.filed(), log.latest()
        for claim, result in to_file:
            key = ("fact", claim.target.id)
            if filed.get(key) == claim and latest.get(key) == result.verification:
                continue
            queue.file(claim, at=at)
            log.append(result.verification)
            queue.checked(result, at=at)
        if self.ready:
            if self.offering:
                path = root / "offerings" / self.offering["provider"] / f"{self.model_id}.yaml"
                path.parent.mkdir(parents=True, exist_ok=True)
                existing = yaml.safe_load(path.read_text()) if path.exists() else []
                existing = [o for o in existing if offering_identity(o) != self.offering["id"]]
                row = {k: v for k, v in self.offering.items() if k != "id"}
                path.write_text(yaml.safe_dump([*existing, row], sort_keys=False))
            path = root / "premier/slice-1.yaml"
            document = yaml.safe_load(path.read_text())
            if not any((r if isinstance(r, str) else r["model_id"]) == self.model_id
                       for r in document["models"]):
                document["models"].append(self.lineup_entry)
                path.write_text(yaml.safe_dump(document, sort_keys=False, allow_unicode=True))


def draft_packet(*, root: Path, model_id: str, fetcher, store: CopyStore,
                 today: date, registry=None) -> Packet:
    if len(model_id) > 128 or not MODEL_ID.fullmatch(model_id) or ".." in model_id:
        raise ValueError("model must be a catalogue ID such as anthropic/claude-haiku-5-5")
    registry = registry or default_registry()
    card, _ = split_front_matter((root / "models" / f"{model_id}.md").read_text())
    if card["model_id"] != model_id:
        raise ValueError("card identity differs from the requested release")
    lab, slug = model_id.split("/")
    names = tuple(dict.fromkeys((card.get("display_name") or slug,
                                card.get("version") or slug, slug)))
    inputs = collect_repo(root)
    model = next(m for m in inputs.models if m["id"] == model_id)
    registered = load_sources(root / "registry/sources.yaml")
    terms = load_source_terms(root)
    references, statuses, selected, fetched = [], [], {}, {}
    for source in source_candidates(card, registered):
        url = str(source.url)
        status = {"url": url, "source_id": source.id}
        statuses.append(status)
        if reason := source_block(url, lab, terms):
            status.update(outcome="blocked", reason=reason)
            continue
        if url not in fetched:
            try:
                fetched[url] = fetcher.fetch(url)
            except SourceBlockedError as error:
                status.update(outcome="blocked", reason=str(error))
                continue
        result = fetched[url]
        if result.outcome != "ok":
            status.update(outcome="unreachable", reason=f"HTTP {result.status}"
                          if result.status else "source fetch failed")
            continue
        if reason := next((reason for hop in result.resolved_urls
                           if (reason := source_block(str(hop), lab, terms))), None):
            status.update(outcome="blocked", reason=reason)
            continue
        # Granting (MODEL-420): "cited" writes a citation record that later
        # stands in for verification, so a malformed origin is refused outright.
        cited = cite_only_origin_status(url, result.resolved_urls)
        if cited is None:
            status.update(outcome="blocked", reason="malformed source or redirect URL")
            continue
        if cited and result.snapshot_ref:
            ref = result.snapshot_ref
            store.record_citation(ref, source_url=url, resolved_urls=result.resolved_urls,
                                  retrieved_at=result.retrieved_at)
        else:
            ref = store.put(result.body, source_url=url, resolved_urls=result.resolved_urls,
                            retrieved_at=result.retrieved_at)
        status.update(outcome="cited" if cited else "fetched", snapshot_ref=ref,
                      retrieved_at=(result.retrieved_at or datetime.now(UTC)).isoformat(),
                      resolved_urls=list(result.resolved_urls))
        selected[source.id] = source
        references.append(SourceRef(
            source_id=source.id, snapshot_ref=ref,
            cited_regions=[r.id for r in source.cited_regions],
            retrieved_at=result.retrieved_at or datetime.now(UTC),
            resolved_urls=list(result.resolved_urls),
        ))
    regions = StoredRegions(store, selected, cache_documents=True)
    facets = [f for f in registry.facets() if not f.computed_by and not f.parameter
              and f.subject in {"model", "offering"} and f.id not in IDENTITY_FACETS
              and not f.id.startswith("offering.subscription.")]
    found, conflicts = read_facts(model_id, names, [f for f in facets if f.subject == "model"],
                                  references, regions, today, registry)
    provider = API_PROVIDERS.get(lab, lab)
    offering_id = f"{provider}/{model_id}/global/standard"
    prices, offering_conflicts = read_facts(
        offering_id, names, [f for f in facets if f.subject == "offering"],
        references, regions, today, registry,
    )
    model_facts = [fact.model_dump(mode="json", exclude_none=True)
                   for fact, _, _ in found.values()]
    offering_facts = [fact.model_dump(mode="json", exclude_none=True)
                     for fact, _, _ in prices.values()]
    offering_path = root / "offerings" / provider / f"{model_id}.yaml"
    authored = yaml.safe_load(offering_path.read_text()) if offering_path.exists() else []
    existing_offering = next((o for o in authored if offering_identity(o) == offering_id), None)
    existing_offering_facts = (existing_offering or {}).get("facts", [])
    scheduled = {f["facet"] for f in existing_offering_facts
                 if f.get("effective_from") or f.get("effective_until")}
    # An undated reading cannot replace a schedule or inherit its date bounds.
    prices = {facet: entry for facet, entry in prices.items() if facet not in scheduled}
    offering_facts = [f for f in offering_facts if f["facet"] not in scheduled]
    merged_offering_facts = [
        f for f in existing_offering_facts if f["facet"] not in prices
    ] + offering_facts
    offering = ({"id": offering_id, "model": model_id, "provider": provider,
                 "region": "global", "tier": "standard",
                 "facts": merged_offering_facts}
                if lab in PRICE_URLS or offering_facts or existing_offering else None)
    existing_facts = {f["facet"]: f for f in model["facts"]}
    existing_facts.update({f["facet"]: f for f in model_facts})
    model = {**model, "facts": list(existing_facts.values())}
    checks = [(claim, result) for _, claim, result in (*found.values(), *prices.values())]
    offerings = [o for o in inputs.offerings
                 if o["model"] == model_id
                 and (not offering or offering_identity(o) != offering_id)]
    if offering:
        offerings.append(offering)
    source_urls = {**inputs.sources, **{sid: str(s.url) for sid, s in selected.items()}}
    strict_gaps = {}
    for subject, facts in [(model_id, model["facts"]),
                           *((offering_identity(o), o["facts"]) for o in offerings)]:
        for fact in facts:
            facet = registry.facet(fact["facet"])
            if facet.tier != "guaranteed" or facet.computed_by:
                continue
            for ref in fact.get("sources", []):
                url = source_urls.get(ref["source_id"], "")
                origins = (url, *ref.get("resolved_urls", []))
                reason = ("cite-only provenance is not verified"
                          if cite_only_origin_restrictive(url, ref.get("resolved_urls", []))
                          else next((reason for origin in origins
                                     if (reason := source_block(origin, lab, terms))), None))
                if reason:
                    strict_gaps[(subject, facet.id)] = Gap(
                        model_id, subject, facet.id, reason, (url,))
    audit = audit_build(
        replace(inputs, models=[model], offerings=offerings, subscriptions=[], evidence=[],
                hardware=[], hardware_fit_records=[],
                sources=source_urls,
                verifications=[*inputs.verifications,
                               *(r.verification for _, r in checks)]),
        registry=registry, premier=[model_id], as_of=today, guard=excluded_sources(),
    )
    benchmarks = [r for r in (card.get("benchmarks") or {}).get("evidence", [])
                  if r.get("source_url") and not source_block(r["source_url"], lab, terms)
                  and not excluded_sources().benchmark(r.get("benchmark_id"))]
    block = card.get("benchmarks") or {}
    if block.get("benchmark_source") and not source_block(block["benchmark_source"], lab, terms):
        documented = {r["benchmark_id"] for r in benchmarks}
        benchmarks += [
            {"benchmark_id": bid, "score": score, "source_url": block["benchmark_source"],
             "status": "catalogue_only", "verified": False}
            for bid, score in (block.get("scores") or {}).items()
            if bid not in documented and not excluded_sources().benchmark(bid)
        ]
    gaps = {(g.subject, g.facet): g for g in audit.gaps}
    gaps.update({(g.subject, g.facet): g for g in [*conflicts, *offering_conflicts]})
    gaps.update(strict_gaps)
    if not offering and not any(o["provider"] == provider for o in offerings):
        gaps[(model_id, "no_offering")] = Gap(
            model_id, model_id, "no_offering", "no first-party offering in packet or data")
    if model["lifecycle"] == "retired":
        gaps[(model_id, "model.lifecycle")] = Gap(
            model_id, model_id, "model.lifecycle", "retired models cannot be admitted")
    lineup = {"model_id": model_id}
    if class_fact := existing_facts.get("model.class"):
        lineup.update(
            display_name=card.get("display_name", model_id),
            **{"class": class_fact["value"]},
            clauses=[{"clause": 4, "reason": "Admission packet for human review"}],
        )
    return Packet(model_id, today, model_facts, offering, benchmarks,
                  list(gaps.values()), statuses, checks, selected, lineup)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--body", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--firecrawl-ledger", type=Path,
                        help="Opt in to paid fallback using a restored UTC-month ledger; cap 50")
    args = parser.parse_args(argv)
    if args.write and args.dry_run:
        parser.error("--write and --dry-run are mutually exclusive")
    if args.write and not args.cache_dir and not os.environ.get("MODELSPEC_SOURCE_CACHE"):
        parser.error("--write requires --cache-dir or MODELSPEC_SOURCE_CACHE to retain provenance")
    with tempfile.TemporaryDirectory(prefix="admission-") as temporary, httpx.Client() as client:
        today = datetime.now(UTC).date()
        fetcher = AdmissionFetcher(
            client, lab=args.model.split("/")[0], terms=load_source_terms(args.data_dir),
            retries=0, timeout=20,
        )
        if args.firecrawl_ledger:
            from scripts.admission_fallback import AdmissionFallback

            fetcher = AdmissionFallback(
                fetcher, args.firecrawl_ledger, month=today.strftime("%Y-%m"))
        packet = draft_packet(
            root=args.data_dir, model_id=args.model,
            fetcher=fetcher,
            store=CopyStore(
                args.cache_dir or os.environ.get("MODELSPEC_SOURCE_CACHE") or temporary),
            today=today,
        )
        if args.write:
            packet.write(args.data_dir)
        text = json.dumps(packet.to_dict(), indent=2, ensure_ascii=False) + "\n"
        manifest = json.dumps({"sources": packet.sources}, indent=2) + "\n"
        for path, content in ((args.report, text), (args.body, packet.markdown()),
                              (args.manifest, manifest)):
            if path:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
