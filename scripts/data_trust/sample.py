"""Stratified fresh HTTP re-reads using the engine's deterministic readers."""

from __future__ import annotations

import math
import re
import random
import tempfile
from collections import Counter, defaultdict
from dataclasses import replace
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from pydantic import ValidationError

from decision.excluded import excluded_sources
from decision.final_hosts import observe
from decision.model import (
    Source,
    SourceRef,
    TargetRef,
    VerificationActor,
    evidence_verification_value,
    fact_verification_value,
    value_hash,
)
from decision.sources import CopyStore, Fetcher
from decision.verify import (
    Claim,
    StoredRegions,
    claim_verification_value,
    deterministic_extractors,
    verify,
)
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


#: Boards the audit reads, by the version a field names (MODEL-509). The 4.0 board is
#: gone, so its claims are not compared with the 4.1 page.
TBENCH_BOARD_GONE = "terminal_bench_v4_0"
TBENCH_READ_FIELD = "terminal_bench_v4_1"


def unauditable(f: dict) -> str | None:
    """Why a row is not compared with a live page at all, or None."""
    if f.get("not_published_since") not in (None, ""):
        return "not_published_since"
    field = str(f.get("field") or "")
    if field == TBENCH_BOARD_GONE:
        return "board no longer published"
    if field.startswith("terminal_bench") and field != TBENCH_READ_FIELD:
        return "board version not named by an audited field"
    return None


#: A mismatch records the value the reader found, cut to this many characters.
READ_VALUE_LIMIT = 200


def read_detail(result, fetched_bytes: dict[str, bytes]) -> dict:
    """What a mismatch read, so a reviewer can tell source drift from a reader fault.

    ``read_value`` is the found value of the first diff that has one, cut to
    ``READ_VALUE_LIMIT`` characters (``read_value_truncated`` says whether it was cut).
    ``diff_fields`` names every field that differed. ``source_snapshots`` maps each
    fetched URL to the hash of the bytes the reader was given, before any projection.
    """
    from decision.sources import fingerprint_bytes

    from decision.retention import cite_only_origin_restrictive

    found = next((d for d in result.diffs if d.found is not None), None)
    text = None if found is None else str(found.found)
    # A cite-only host's page text is not kept: only the hashes are recorded.
    withheld = cite_only_origin_restrictive(None, tuple(fetched_bytes))
    if withheld:
        text = None
    return {
        "read_value": None if text is None else text[:READ_VALUE_LIMIT],
        **({"read_value_withheld": "cite-only"} if withheld else {}),
        "read_value_truncated": text is not None and len(text) > READ_VALUE_LIMIT,
        "read_field": None if found is None else found.field,
        "diff_fields": sorted({d.field for d in result.diffs}),
        "source_snapshots": {u: fingerprint_bytes(b) for u, b in sorted(fetched_bytes.items())},
    }


def _read(
    f: dict, c: Catalogue, registry, fetcher, store: CopyStore, fetched: dict, today: date,
    pin: str | None = None,
) -> tuple[str, str] | tuple[str, str, dict]:
    """One read of the row's sources. ``pin`` reads each Arena parquet at that revision."""
    if (skip := unauditable(f)) is not None:
        return "skipped", skip
    urls = source_urls(f, c)
    if not urls:
        return "unreadable", "no_primary_source"
    try:
        claim = claim_for(f, c, registry)
        sources, fresh_refs, raw_bytes = {}, [], {}
        shell_reason = None
        for index, listed in enumerate(dict.fromkeys(urls)):
            url = at_revision(listed, pin) if pin else listed
            if not safe_url(url) or excluded_sources().url(url):
                continue
            raw_ref = next(
                (
                    r
                    for r in f.get("sources") or []
                    if isinstance(r, dict)
                    and c.sources.get(r.get("source_id"), {}).get("url") == listed
                ),
                None,
            )
            sid = raw_ref["source_id"] if raw_ref else f"audit-primary-{index}"
            if url not in fetched:
                response = fetcher.fetch(url)
                from decision.sources import named_refusal, refusal_reason

                if (refused := refusal_reason(response)) is not None:
                    return "redirect_unclassified", named_refusal(refused, sid)
                from decision.retention import cite_only_origin_restrictive
                from decision.sources import (
                    ShellCheck, ShellPageError, fingerprint_bytes, shell_refusal,
                )

                if response.outcome == "ok":
                    try:
                        store.check_shell(
                            response.body, fingerprint_bytes(response.body), url,
                            response.resolved_urls,
                            ShellCheck(_shell_normaliser(response.content_type)))
                    except ShellPageError as stop:
                        # Bytes that are a shell cite nothing (MODEL-519); a fallback
                        # source may still read.
                        shell_reason = shell_refusal(stop.reason, sid)
                        fetched[url] = (None, "")
                        continue
                if cite_only_origin_restrictive(url, response.resolved_urls):
                    store.put(response.body, source_url=url,
                              retrieved_at=response.retrieved_at,
                              resolved_urls=response.resolved_urls)
                    return "unreadable", "cite_only_not_machine_verified"
                fetched[url] = (
                    (response.body, response.content_type)
                    if response.outcome == "ok"
                    else (None, "")
                )
            body, content_type = fetched[url]
            if body is None:
                continue
            raw_bytes[url] = body
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
                    snapshot_ref=store.put(body, source_url=str(source.url)),
                    cited_regions=(raw_ref.get("cited_regions") if raw_ref else None)
                    or [r.id for r in source.cited_regions],
                )
            )
        if not fresh_refs and shell_reason is not None:
            return "shell_page", shell_reason
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
        return "mismatched", "deterministic_difference", read_detail(result, raw_bytes)
    except (ValidationError, ValueError, KeyError, TypeError, OSError, ImportError):
        # Diagnostics contain reason codes, never exception text or credential-bearing URLs.
        return "unreadable", "unsupported_source_or_claim"


#: The Arena dataset, whose boards are read at a revision (MODEL-516).
ARENA_DATASET = "lmarena-ai/leaderboard-dataset"
ARENA_COMMITS = f"https://huggingface.co/api/datasets/{ARENA_DATASET}/commits/main"
#: Commit pages searched for the revision a row was read at; 50 commits a page.
ARENA_COMMIT_PAGES = 8
_REVISION_TEXT = re.compile(r"(?i)\brevision\s+([0-9a-f]{7,40})\b")
_RESOLVE_REVISION = re.compile(r"/resolve/([0-9a-f]{40})/")
_RESOLVE_SEGMENT = re.compile(r"(/resolve/)[^/]+(/)")


def is_arena(url: str) -> bool:
    return f"{ARENA_DATASET}/resolve/" in url and url.endswith(".parquet")


def at_revision(url: str, sha: str) -> str:
    """An Arena parquet URL read at ``sha``; any other URL is unchanged."""
    return _RESOLVE_SEGMENT.sub(rf"\g<1>{sha}\g<2>", url, count=1) if is_arena(url) else url


def stored_revision(f: dict, urls: list[str]) -> str | None:
    """The dataset revision a row records: a pinned source URL, else ``revision <hex>``
    in its benchmark version or configuration. 7 to 40 hex characters."""
    for url in urls:
        if is_arena(url) and (m := _RESOLVE_REVISION.search(url)):
            return m.group(1)
    for key in ("benchmark_version", "configuration"):
        if m := _REVISION_TEXT.search(str(f.get(key) or "")):
            return m.group(1).lower()
    return None


def arena_commits(fetcher, fetched: dict) -> list[tuple[str, str]]:
    """(sha, UTC time) of the dataset's recent commits, newest first. Empty when unreadable."""
    import json

    commits: list[tuple[str, str]] = []
    for page in range(ARENA_COMMIT_PAGES):
        url = ARENA_COMMITS + (f"?p={page}" if page else "")
        if url not in fetched:
            response = fetcher.fetch(url)
            fetched[url] = (response.body if response.outcome == "ok" else None, "")
        body = fetched[url][0]
        try:
            rows = json.loads(body) if body else []
            commits += [(r["id"], r["date"]) for r in rows]
        except (ValueError, KeyError, TypeError):
            break
        if not rows:
            break
    return commits


def revisions_by(f: dict, commits: list[tuple[str, str]]) -> list[str]:
    """The newest commit made on or before the end of the row's ``observed_at`` day."""
    seen = day(f.get("observed_at"))
    if seen is None:
        return []
    cutoff = (seen + timedelta(days=1)).isoformat()
    return [sha for sha, when in commits if when < cutoff][:1]


def reread(
    f: dict, c: Catalogue, registry, fetcher, store: CopyStore, fetched: dict, today: date
) -> tuple[str, str] | tuple[str, str, dict]:
    """The outcome and reason; a mismatch adds a third item, the ``read_detail``.

    An Arena board changes after a row is read. A row that records its dataset revision is
    compared at it. Otherwise a value that differs from the latest board, yet equals the board
    at the revision of its ``observed_at`` day, is ``source_moved``: the source changed, the
    row was right when read. Only a value that fits neither is a mismatch.
    """
    urls = source_urls(f, c)
    if not any(is_arena(u) for u in urls) or unauditable(f) is not None:
        return _read(f, c, registry, fetcher, store, fetched, today)
    recorded = stored_revision(f, urls)
    if recorded is not None:
        full = recorded if len(recorded) == 40 else next(
            (s for s, _ in arena_commits(fetcher, fetched) if s.startswith(recorded)), None
        )
        if full is not None:
            return _read(f, c, registry, fetcher, store, fetched, today, pin=full)
    out = _read(f, c, registry, fetcher, store, fetched, today)
    if out[0] != "mismatched":
        return out
    for sha in revisions_by(f, arena_commits(fetcher, fetched)):
        again = _read(f, c, registry, fetcher, store, fetched, today, pin=sha)
        if again[0] == "matched":
            return "source_moved", "board_changed_after_read", out[2]
    return out


def _shell_normaliser(content_type: str) -> str:
    """The recipe the shell check reads a reply with: only HTML is held to the text rule."""
    kind = (content_type or "").split(";")[0].strip().lower()
    if kind == "application/json" or kind.endswith("+json"):
        return "json-default"
    if kind in {"text/html", "application/xhtml+xml", ""}:
        return "html-default"
    return "text-default"


#: The audit's record of each registered source's final host, beside its reports.
FINAL_HOSTS_FILE = "final-hosts.json"


class _RecordingFetcher:
    """The audit's fetcher, noting the redirect chain of each fetch that read (MODEL-525)."""

    def __init__(self, fetcher) -> None:
        self._fetcher = fetcher
        self.ended: dict[str, tuple[str, ...]] = {}

    def fetch(self, url: str, *args, **kwargs):
        response = self._fetcher.fetch(url, *args, **kwargs)
        if getattr(response, "outcome", None) == "ok":
            self.ended[url] = tuple(getattr(response, "resolved_urls", ()) or ())
        return response

    def __getattr__(self, name: str):
        return getattr(self._fetcher, name)


def registered_finals(c: Catalogue, ended: dict[str, tuple[str, ...]]) -> dict[str, tuple[str, ...]]:
    """Each registered source the audit fetched, with the URLs its fetch resolved through."""
    return {
        sid: ended[str(row["url"])]
        for sid, row in c.sources.items()
        if isinstance(row, dict) and ended.get(str(row.get("url")))
    }


def run(
    c: Catalogue, registry, *, n: int, seed: str, as_of: date, fetcher=None, reader=reread,
    final_hosts: Path | None = None, write: bool = False,
) -> dict:
    """The sample. With ``final_hosts``, each registered source's final host is recorded
    there (written only with ``write``) and a moved host is a ``final_host_changed`` entry.
    """
    eligible = [
        f
        for f in c.facts
        if f["kind"] != "legacy" and f.get("state") != "unknown" and source_urls(f, c)
    ]
    chosen = select(eligible, n, seed, as_of)
    coverage = reader_coverage(c, registry, as_of)
    strata = defaultdict(Counter)
    skipped = Counter()
    refused = 0
    shell_pages = 0
    moved = 0
    results = []
    fetched = {}
    client = None
    if fetcher is None:
        client = httpx.Client(event_hooks={"request": [guard_request]})
        fetcher = Fetcher(client=client, timeout=15, retries=0)
    fetcher = _RecordingFetcher(fetcher)
    with tempfile.TemporaryDirectory(prefix="modelspec-data-trust-") as cache_dir:
        store = CopyStore(Path(cache_dir))
        for f in chosen:
            key = stratum(f, as_of)
            outcome, reason, *rest = reader(f, c, registry, fetcher, store, fetched, as_of)
            if outcome == "skipped":
                skipped[reason] += 1
            elif outcome == "source_moved":
                moved += 1
            elif outcome == "redirect_unclassified":
                refused += 1
            elif outcome == "shell_page":
                shell_pages += 1
            else:
                strata[key][outcome] += 1
            results.append(
                {
                    "id": f["id"],
                    "field": f["field"],
                    "stratum": list(key),
                    "outcome": outcome,
                    "reason": reason,
                    **(rest[0] if rest and outcome in ("mismatched", "source_moved") else {}),
                }
            )
    if client is not None:
        client.close()
    moved_hosts = (
        observe(final_hosts, registered_finals(c, fetcher.ended), as_of, write=write)
        if final_hosts is not None else []
    )
    counts = Counter(r["outcome"] for r in results)
    counts = {k: counts[k] for k in ("matched", "mismatched", "unreadable")}
    return {
        "reader_coverage": coverage,
        "eligible": len(eligible),
        "requested": n,
        "selected": len(chosen),
        # Assessed rows only: skipped rows (a withdrawn board, a row marked not published) are
        # reported under ``skipped`` and are not part of the sample.
        "sampled": len(chosen) - sum(skipped.values()),
        "seed": seed,
        "counts": counts,
        "skipped": dict(sorted(skipped.items())),
        # Fetches refused at the terms register (MODEL-509), reported apart from unreadable.
        "redirect_unclassified": refused,
        "shell_page": shell_pages,
        # A value that differs now but matched the board when read (MODEL-516): reported,
        # and not part of the error rate.
        "source_moved": moved,
        # A registered source whose fetch now ends on another host (MODEL-525).
        "final_host_changed": moved_hosts,
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
    if f["kind"] == "evidence":
        same = original is not None and value_hash(original.value) == value_hash(value)
    else:
        # A dated price matches only the claim for the same period (MODEL-394).
        same = original is not None and value_hash(
            claim_verification_value(original)
        ) == value_hash(fact_verification_value(f))
    if same:
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
        else {
            key: f[key]
            for key in ("effective_from", "effective_until")
            if f.get(key) is not None
        },
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
