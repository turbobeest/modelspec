#!/usr/bin/env python3
"""Draft verified token prices for a new card, independently of premier admission.

The caller opens a draft PR. This command never runs git or calls a model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path

import httpx
import yaml

from decision.registry import default as default_registry
from decision.retention import cite_only_origin_status, record_origin_status
from decision.model import SourceRef
from decision.snapshot import Gap
from decision.sources import CopyStore, fingerprint_bytes, load_sources
from decision.verify import Queue, StoredRegions, VerificationLog
from pipeline.load import split_front_matter
from scripts.admission_drafter import (
    API_PROVIDERS, MODEL_ID, SourceBlockedError, load_source_terms, read_facts,
    source_block, source_candidates,
)

REQUIRED_PRICES = {"offering.price.input", "offering.price.output"}


@dataclass
class OfferingDraft:
    model_id: str
    checked_on: date
    offering: dict | None = None
    gaps: list[Gap] = field(default_factory=list)
    sources: list[dict] = field(default_factory=list)
    credits_spent: int = 0
    checks: list = field(default_factory=list, repr=False)
    registrations: dict = field(default_factory=dict, repr=False)

    @property
    def offering_path(self) -> Path | None:
        if self.offering is None:
            return None
        return Path("offerings") / self.offering["provider"] / f"{self.model_id}.yaml"

    def to_dict(self):
        return {
            "model": self.model_id, "checked_on": self.checked_on.isoformat(),
            "offering": self.offering,
            "gaps": [{**asdict(g), "sources": list(g.sources)} for g in self.gaps],
            "sources": self.sources, "firecrawl_credits_used": self.credits_spent,
        }

    def write(self, root: Path):
        """Add a new offering and append provenance; preserve existing records."""
        if self.offering_path is None:
            return
        path = root / self.offering_path
        if path.exists():
            return
        used = {ref.source_id for claim, _ in self.checks for ref in claim.sources}
        source_path = root / "registry/sources.yaml"
        registered = load_sources(source_path)
        additions = []
        for sid in sorted(used):
            source = self.registrations[sid]
            if sid in registered:
                if registered[sid] != source:
                    raise ValueError(f"source registration changed: {sid}")
            else:
                additions.append(source.model_dump(mode="json", exclude_none=True))
        if additions:
            source_path.parent.mkdir(parents=True, exist_ok=True)
            if not source_path.exists():
                source_path.write_text("schema_version: 1\nsources:\n")
            # Append sequence items without reserializing existing registrations.
            existing = source_path.read_text()
            document = yaml.compose(existing)
            sequence = next(value for key, value in document.value if key.value == "sources")
            indent = sequence.start_mark.column if isinstance(sequence, yaml.SequenceNode) else 0
            suffix = "\n" + "\n".join(
                " " * indent + line for line in yaml.safe_dump(additions, sort_keys=False).splitlines()
            ) + "\n"
            # Flow-style registries cannot be extended without rewriting their bytes.
            extended = yaml.safe_load(existing + suffix)
            if len(extended["sources"]) != len(registered) + len(additions):
                raise ValueError("source registry cannot be safely extended")
            with source_path.open("a") as output:
                output.write(suffix)
        queue, log = Queue(root / "verification"), VerificationLog(root / "verification")
        at = datetime.combine(self.checked_on, datetime.min.time(), tzinfo=UTC)
        filed, latest = queue.filed(), log.latest()
        for claim, result in self.checks:
            key = ("fact", claim.target.id)
            if filed.get(key) == claim and latest.get(key) == result.verification:
                continue
            queue.file(claim, at=at)
            log.append(result.verification)
            queue.checked(result, at=at)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x") as output:
            yaml.safe_dump([self.offering], output, sort_keys=False)


def draft_offering(*, root: Path, model_id: str, fetcher, store: CopyStore,
                   today: date, registry=None) -> OfferingDraft:
    if len(model_id) > 128 or not MODEL_ID.fullmatch(model_id) or ".." in model_id:
        raise ValueError("model must be a catalogue ID such as google/gemini-3")
    card, _ = split_front_matter((root / "models" / f"{model_id}.md").read_text())
    if card["model_id"] != model_id:
        raise ValueError("card identity differs from the requested release")
    registry = registry or default_registry()
    packet = OfferingDraft(model_id, today)
    lab, slug = model_id.split("/")
    provider = API_PROVIDERS.get(lab, lab)
    subject = f"{provider}/{model_id}/global/standard"
    facets = [f for f in registry.facets() if f.id.startswith("offering.price.")
              and not f.computed_by]

    def gaps(reason):
        packet.gaps = [Gap(model_id, subject, f.id, reason) for f in facets]
        return packet

    if (root / "offerings" / provider / f"{model_id}.yaml").exists():
        return gaps("existing offering retained; new-card drafter does not rewrite records")
    if card.get("model_type") in {"video-generation", "image-generation", "audio-generation",
                                  "speech-to-text", "text-to-speech"}:
        return gaps("model uses non-token pricing; no applicable deterministic price reader")
    if provider not in {p.id for p in registry.providers()}:
        return gaps(f"no registered first-party provider mapping for {lab}")
    names = tuple(dict.fromkeys((card.get("display_name") or slug,
                                card.get("version") or slug, slug)))
    registered = load_sources(root / "registry/sources.yaml")
    terms = load_source_terms(root)
    candidates = source_candidates(card, registered)
    # Once ownership is checked, the provider's own model docs can state prices.
    candidates = list({str(s.url): s.model_copy(update={
        "kind": "provider_documentation",
        "id": "offering-" + hashlib.sha256(str(s.url).encode()).hexdigest()[:20],
    }) for s in candidates if s.kind in {"lab_documentation", "provider_documentation"}}.values())
    selected, references, found, conflicts = {}, [], {}, []
    blocked, cited_urls = set(), set()
    for stage in ("fetch", "render", "fallback"):
        read = getattr(fetcher, stage, None)
        if read is None:
            continue
        for source in candidates:
            url = str(source.url)
            if url in blocked or url in cited_urls:
                continue
            status = {"url": url, "source_id": source.id, "stage": stage}
            packet.sources.append(status)
            if reason := source_block(url, lab, terms):
                status.update(outcome="blocked", reason=reason)
                blocked.add(url)
                continue
            try:
                result = read(url)
            except SourceBlockedError as error:
                status.update(outcome="blocked", reason=str(error))
                blocked.add(url)
                continue
            if result.outcome != "ok":
                status.update(outcome="unreachable", reason=(
                    result.error or (f"HTTP {result.status}" if result.status
                                     else f"{stage} unavailable")))
                continue
            if reason := next((reason for hop in result.resolved_urls
                               if (reason := source_block(str(hop), lab, terms))), None):
                status.update(outcome="blocked", reason=reason)
                blocked.add(url)
                continue
            cited = cite_only_origin_status(url, result.resolved_urls)
            if cited is None:
                status.update(outcome="blocked", reason="malformed source or redirect URL")
                blocked.add(url)
                continue
            retrieved_at = result.retrieved_at or datetime.now(UTC)
            if cited:
                ref = result.snapshot_ref or fingerprint_bytes(result.body)
                try:
                    existing = store.citation(ref)
                    if existing is not None and (existing.get("url") != url
                                                 or record_origin_status(existing) is None):
                        raise ValueError("existing citation differs")
                except ValueError:
                    status.update(outcome="blocked", reason="existing citation cannot be reused")
                    blocked.add(url)
                    continue
                if existing is None:
                    store.record_citation(ref, source_url=url, resolved_urls=result.resolved_urls,
                                          retrieved_at=retrieved_at)
                cited_urls.add(url)
                status.update(outcome="cited", reason="cite-only source; no independent price read")
            else:
                ref = fingerprint_bytes(result.body)
                if os.path.lexists(store.path(ref)) and not store.has(ref):
                    status.update(outcome="blocked", reason="existing source copy cannot be reused")
                    blocked.add(url)
                    continue
                ref = store.put(result.body, source_url=url, resolved_urls=result.resolved_urls,
                                retrieved_at=retrieved_at)
                # A rendered projection is read as raw HTML using the same page locator.
                selected[source.id] = source
                references = [r for r in references if r.source_id != source.id]
                references.append(SourceRef(
                    source_id=source.id, snapshot_ref=ref,
                    cited_regions=[r.id for r in source.cited_regions],
                    retrieved_at=retrieved_at, resolved_urls=list(result.resolved_urls)))
                status.update(outcome="fetched")
            status.update(snapshot_ref=ref, retrieved_at=retrieved_at.isoformat(),
                          resolved_urls=list(result.resolved_urls))
        regions = StoredRegions(store, selected, cache_documents=True)
        found, conflicts = read_facts(subject, names, facets, references, regions, today, registry)
        if REQUIRED_PRICES <= found.keys():
            break
    reasons = list(dict.fromkeys(s["reason"] for s in packet.sources if s.get("reason")))
    reason = "; ".join(reasons) or "no unambiguous first-party price passed the independent reader"
    packet.gaps = [Gap(model_id, subject, f.id, reason) for f in facets if f.id not in found]
    packet.gaps += conflicts
    packet.registrations = selected
    packet.checks = [(claim, result) for _, claim, result in found.values()]
    packet.credits_spent = getattr(fetcher, "credits_spent", 0)
    if found:
        packet.offering = {
            "model": model_id, "provider": provider, "region": "global", "tier": "standard",
            "facts": [fact.model_dump(mode="json", exclude_none=True)
                      for fact, _, _ in found.values()],
        }
    return packet


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--firecrawl-ledger", type=Path,
                        help="Opt in with an existing durable ledger; at most 5/run and 100/month")
    args = parser.parse_args(argv)
    cache = args.cache_dir or os.environ.get("MODELSPEC_SOURCE_CACHE")
    if args.write and not cache:
        parser.error("--write requires --cache-dir or MODELSPEC_SOURCE_CACHE")
    from scripts.offering_fetch import OfferingFetcher, OfferingHTTPFetcher

    with tempfile.TemporaryDirectory(prefix="offering-") as temporary, httpx.Client() as client:
        lab = args.model.split("/")[0]
        terms = load_source_terms(args.data_dir)
        primary = OfferingHTTPFetcher(client, lab=lab, terms=terms, retries=0, timeout=20)
        with OfferingFetcher(primary, lab=lab, terms=terms,
                             sources=load_sources(args.data_dir / "registry/sources.yaml"),
                             ledger=args.firecrawl_ledger) as fetcher:
            packet = draft_offering(root=args.data_dir, model_id=args.model, fetcher=fetcher,
                                    store=CopyStore(cache or temporary), today=datetime.now(UTC).date())
            if args.write:
                packet.write(args.data_dir)
            content = json.dumps(packet.to_dict(), indent=2) + "\n"
            if args.report:
                args.report.parent.mkdir(parents=True, exist_ok=True)
                args.report.write_text(content)
            print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
