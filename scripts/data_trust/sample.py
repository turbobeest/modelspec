"""Stratified fresh HTTP re-reads using the engine's deterministic readers."""

from __future__ import annotations

import math
import random
import tempfile
from collections import Counter, defaultdict
from dataclasses import replace
from datetime import date
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from pydantic import ValidationError

from decision.excluded import excluded_sources
from decision.model import (
    Source,
    SourceRef,
    TargetRef,
    VerificationActor,
    evidence_verification_value,
    value_hash,
)
from decision.sources import CopyStore, Fetcher
from decision.verify import Claim, StoredRegions, deterministic_extractors, verify
from scripts.data_trust.catalogue import Catalogue, day
from scripts.data_trust.invariants import field_type, safe_url, source_urls


def stratum(f: dict, as_of: date) -> tuple[str, str, str]:
    read = day(f.get("read_date"))
    age = (as_of - read).days if read else None
    bucket = "undated" if age is None else "0-7d" if age <= 7 else "8-30d" if age <= 30 else "31+d"
    return field_type(f), f["provider"], bucket


def select(facts: list[dict], n: int, seed: str, as_of: date) -> list[dict]:
    if n < 1:
        raise ValueError("sample size must be positive")
    rng = random.Random(seed)
    groups = defaultdict(list)
    # Unknown has no stored claim to re-read.
    for f in sorted(facts, key=lambda f: (f["id"], str(f["field"]))):
        if f.get("state") != "unknown" and f["kind"] != "legacy":
            groups[stratum(f, as_of)].append(f)
    keys = sorted(groups)
    rng.shuffle(keys)
    for rows in groups.values():
        rng.shuffle(rows)
    chosen = []
    while len(chosen) < n and keys:
        next_keys = []
        for key in keys:
            chosen.append(groups[key].pop())
            if groups[key]:
                next_keys.append(key)
            if len(chosen) == n:
                break
        keys = next_keys
    return chosen


def wilson(errors: int, readable: int) -> dict:
    if readable == 0:
        return {"estimate": None, "low": None, "high": None, "readable": 0}
    z = 1.959963984540054
    p = errors / readable
    denominator = 1 + z * z / readable
    center = (p + z * z / (2 * readable)) / denominator
    radius = z * math.sqrt(p * (1 - p) / readable + z * z / (4 * readable * readable)) / denominator
    return {
        "estimate": p,
        "low": max(0, center - radius),
        "high": min(1, center + radius),
        "readable": readable,
    }


def guard_request(request: httpx.Request) -> None:
    """Apply source exclusions to redirects too, before any request is sent."""
    url = str(request.url)
    if not safe_url(url) or excluded_sources().url(url):
        raise ValueError("refused source")


def reread(
    f: dict, c: Catalogue, registry, fetcher, store: CopyStore, fetched: dict, today: date
) -> tuple[str, str]:
    urls = source_urls(f, c)
    if not urls:
        return "unreadable", "no_primary_source"
    try:
        claim = claim_for(f, c, registry)
        sources, fresh_refs = {}, []
        for index, url in enumerate(dict.fromkeys(urls)):
            if not safe_url(url) or excluded_sources().url(url):
                continue
            raw_ref = next(
                (
                    r
                    for r in f.get("sources") or []
                    if isinstance(r, dict)
                    and c.sources.get(r.get("source_id"), {}).get("url") == url
                ),
                None,
            )
            sid = raw_ref["source_id"] if raw_ref else f"audit-primary-{index}"
            if url not in fetched:
                response = fetcher.fetch(url)
                fetched[url] = (
                    (response.body, response.content_type)
                    if response.outcome == "ok"
                    else (None, "")
                )
            body, content_type = fetched[url]
            if body is None:
                continue
            body = project(claim, url, body, today)
            source = (
                Source.model_validate(c.sources[sid])
                if raw_ref
                else Source.model_validate(
                    {
                        "id": sid,
                        "url": url,
                        "normaliser": "text-default"
                        if content_type.startswith("text/plain")
                        else "html-default",
                        "cited_regions": [{"id": "page", "locator": {"kind": "page"}}],
                    }
                )
            )
            if body.lstrip().startswith(b"<"):
                source = source.model_copy(update={"normaliser": "html-default"})
            sources[sid] = source
            fresh_refs.append(
                SourceRef(
                    source_id=sid,
                    snapshot_ref=store.put(body),
                    cited_regions=(raw_ref.get("cited_regions") if raw_ref else None)
                    or [r.id for r in source.cited_regions],
                )
            )
        if not fresh_refs:
            refused = all(not safe_url(u) or excluded_sources().url(u) for u in urls)
            return "unreadable", "source_refused" if refused else "http_unavailable"
        claim = replace(claim, sources=tuple(fresh_refs))
        result = verify(
            claim, StoredRegions(store, sources), deterministic_extractors(), today=today
        )
        if result.outcome == "verified":
            return "matched", "deterministic_read"
        # A live observation's date advances when it is read again. When that
        # is the only difference, the current value still agrees. Row dates on
        # static evidence, and disagreements in value or qualifiers, still count.
        if (
            result.outcome == "mismatch"
            and f["kind"] == "evidence"
            and (
                f.get("date_type") == "evaluated"
                # This API has no row date. project_mteb adds our observation
                # date, so it cannot disprove a stored publication date either.
                or any(
                    urlsplit(str(source.url)).hostname == "mteb-leaderboard-backend.hf.space"
                    for source in sources.values()
                )
            )
            and any(source.volatility == "live" for source in sources.values())
            and result.diffs
            and all(d.field == "date" and day(d.found) == today for d in result.diffs)
        ):
            return "matched", "observation_date_advanced"
        # No extracted value or identity is lack of readability, never proof of error.
        from scripts.accuracy import _read_nothing

        if result.outcome != "mismatch" or _read_nothing(result):
            return "unreadable", "no_reading"
        if any(d.field == "model" and d.found is None for d in result.diffs):
            return "unreadable", "identity_unreadable"
        return "mismatched", "deterministic_difference"
    except (ValidationError, ValueError, KeyError, TypeError, OSError, ImportError):
        # Diagnostics contain reason codes, never exception text or credential-bearing URLs.
        return "unreadable", "unsupported_source_or_claim"


def run(
    c: Catalogue, registry, *, n: int, seed: str, as_of: date, fetcher=None, reader=reread
) -> dict:
    eligible = [
        f
        for f in c.facts
        if f["kind"] != "legacy" and f.get("state") != "unknown" and source_urls(f, c)
    ]
    chosen = select(eligible, n, seed, as_of)
    coverage = reader_coverage(c, registry, as_of)
    strata = defaultdict(Counter)
    results = []
    fetched = {}
    client = None
    if fetcher is None:
        client = httpx.Client(event_hooks={"request": [guard_request]})
        fetcher = Fetcher(client=client, timeout=15, retries=0)
    with tempfile.TemporaryDirectory(prefix="modelspec-data-trust-") as cache_dir:
        store = CopyStore(Path(cache_dir))
        for f in chosen:
            key = stratum(f, as_of)
            outcome, reason = reader(f, c, registry, fetcher, store, fetched, as_of)
            strata[key][outcome] += 1
            results.append(
                {
                    "id": f["id"],
                    "field": f["field"],
                    "stratum": list(key),
                    "outcome": outcome,
                    "reason": reason,
                }
            )
    if client is not None:
        client.close()
    counts = Counter(r["outcome"] for r in results)
    counts = {k: counts[k] for k in ("matched", "mismatched", "unreadable")}
    return {
        "reader_coverage": coverage,
        "eligible": len(eligible),
        "requested": n,
        "sampled": len(chosen),
        "seed": seed,
        "counts": counts,
        "error_rate": wilson(counts["mismatched"], counts["matched"] + counts["mismatched"]),
        "strata": [
            {
                "field_type": k[0],
                "provider": k[1],
                "age": k[2],
                **{name: v[name] for name in counts},
            }
            for k, v in sorted(strata.items())
        ],
        "results": results,
    }


def claim_for(f, c, registry) -> Claim:
    value = evidence_verification_value(f) if f["kind"] == "evidence" else f["value"]
    original = c.claims.get((f["kind"], f["id"]))
    if original is not None and value_hash(original.value) == value_hash(value):
        # Labels, aliases and qualifiers came from the collector. Do not replace
        # them with registry facet IDs or an offering's structural ID.
        return original
    refs = tuple(
        SourceRef.model_validate(r)
        for r in f.get("sources") or []
        if isinstance(r, dict) and r.get("source_id")
    )
    if not refs:
        refs = (
            SourceRef(
                source_id="audit-primary", snapshot_ref="sha256:" + "0" * 64, cited_regions=["page"]
            ),
        )
    return Claim(
        target=TargetRef(kind="evidence" if f["kind"] == "evidence" else "fact", id=f["id"]),
        subject=f["subject_id"],
        names=f["names"],
        field=f["field"],
        value=value,
        collector=VerificationActor.model_validate(
            (f.get("verification") or {}).get("collector")
            or {
                "agent": "data-trust-inventory",
                "model_family": "unrecorded",
                "method": "inventory",
            }
        ),
        sources=refs,
        unit=registry.facet(f["field"]).unit if f["kind"] == "fact" else f.get("unit"),
        conditions={
            "effort": f.get("effort"),
            "harness": f.get("harness"),
            "date": f.get("evidence_date"),
        }
        if f["kind"] == "evidence"
        else {},
    )


def project(claim, url: str, body: bytes, today: date) -> bytes:
    """Rebuild existing LLM-free projections from fresh primary bytes."""
    from scripts.accuracy import _PROJECTIONS

    projection = _PROJECTIONS.get(claim.collector.method)
    if projection is not None:
        return projection(url, body)
    if url.endswith(".parquet") and "lmarena-ai/leaderboard-dataset/resolve/" in url:
        from decision.sources import fingerprint_bytes
        from scripts.model_160_evidence import ARENA, project_arena

        config = url.split("/")[-2]
        category = ARENA.get(claim.field, (config, "overall"))[1]
        return project_arena(
            body,
            config,
            category,
            url=url,
            page_ref=fingerprint_bytes(body),
            read_date=today.isoformat(),
        )
    from decision.sources import fingerprint_bytes
    from scripts import model_160_evidence as boards

    host = urlsplit(url).hostname
    kwargs = {"url": url, "page_ref": fingerprint_bytes(body), "read_date": today.isoformat()}
    if host == "mteb-leaderboard-backend.hf.space":
        return boards.project_mteb(body, **kwargs)
    if host == "www.tbench.ai" and claim.field.startswith("terminal_bench"):
        from scripts.refresh_leaderboards import _project_tbench

        return _project_tbench(
            body.decode(), url=url, page_ref=kwargs["page_ref"], observed_at=today.isoformat()
        )
    if host == "labs.scale.com" and claim.field == "swe_bench_pro":
        return boards.project_scale(body.decode(), **kwargs)
    if host == "www.swebench.com" and claim.field in {
        "swe_bench_verified",
        "swe_bench_multilingual",
    }:
        board = "Verified" if claim.field == "swe_bench_verified" else "Multilingual"
        return boards.project_swebench(body.decode(), board, **kwargs)
    return body


def reader_coverage(c: Catalogue, registry, today: date) -> dict:
    """Capability on retained primary regions, separate from fresh readability.

    Probe every served record, including LLM-verified ones, with the existing
    deterministic extractors. Missing retained copies leave capability unknown.
    This does not certify that a changed live page is readable today.
    """
    from scripts.accuracy import _read_nothing

    sources = {sid: Source.model_validate(raw) for sid, raw in c.sources.items()}
    regions = StoredRegions(CopyStore(), sources)
    regions.text = lru_cache(maxsize=2048)(regions.text)
    counts = Counter()
    by_field = defaultdict(Counter)
    methods = {r.actor.method for r in deterministic_extractors()}
    for f in c.facts:
        if f["kind"] == "legacy":
            continue
        method = (f.get("verification") or {}).get("verifier", {}).get("method")
        # A successful deterministic verification already proves a reader for
        # this field and region. Probe the others, rather than treating an LLM
        # verification or a retained-source proof as automatically unreadable.
        status = "with_reader" if method in methods else "no_reader"
        if status == "no_reader":
            try:
                claim = claim_for(f, c, registry)
                if not any(
                    regions.text(r.source_id, r.snapshot_ref, region)
                    for r in claim.sources
                    for region in r.cited_regions
                ):
                    status = "capability_unknown"
                else:
                    result = verify(claim, regions, deterministic_extractors(), today=today)
                    if (
                        result.outcome == "verified"
                        or result.outcome == "mismatch"
                        and not _read_nothing(result)
                    ):
                        status = "with_reader"
            except (ValueError, KeyError, TypeError, OSError):
                status = "capability_unknown"
        counts[status] += 1
        by_field[str(f["field"])][status] += 1
    total = sum(counts.values())
    return {
        "served": total,
        "with_reader": counts["with_reader"],
        "no_reader": counts["no_reader"],
        "capability_unknown": counts["capability_unknown"],
        "share": counts["with_reader"] / total if total else None,
        "basis": "existing deterministic verification or deterministic probe of retained regions",
        "by_field": {
            k: {"served": sum(v.values()), **dict(v)} for k, v in sorted(by_field.items())
        },
    }
