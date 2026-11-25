"""A rendered re-read also reads a fact's plain-HTTP companion sources (MODEL-489).

A fact can cite a rendered page and a plain page on another host. A job that fetches
only the rendered page leaves the companion without a fresh copy, and a reader that
needs both reports the whole fact ``unreachable``. This module lets such a job fetch
the companions with the engine's own plain ``Fetcher`` and ``CopyStore`` (the same
fetch and retention rules as the plain re-read: a cite-only origin keeps a citation
record and no bytes), then judge each fact only when every cited source was read.

Two outcomes never read as a pass:

- A source the run did not read at all makes the fact ``skipped`` with
  ``not_reread:<source ids>``.
- A redirect to a host with no class in the terms register is stopped before that
  host receives a request. The fact is ``skipped`` with
  ``redirect_unclassified:<source id>:<host>``, and no bytes are kept.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Literal

from decision.model import Source
from decision.normalise import canonical_url
from decision.retention import canonical_host, is_classified
from decision.sources import (
    CopyStore, Fetcher, FetchMode, ShellCheck, ShellPageError, UnclassifiedRedirectError,
    refusal_reason, shell_alias_urls, shell_refusal,
)

#: The ref the reader reports as an absent copy (unreachable), as the rendered job uses.
MISSING_COPY = "sha256:" + "0" * 64

CompanionOutcome = Literal["ok", "cited", "unreachable", "redirect_unclassified", "shell_page"]


@dataclass(frozen=True)
class CompanionRead:
    source_id: str
    outcome: CompanionOutcome
    copy: str | None = None
    error: str | None = None
    #: The host with no terms class, for ``redirect_unclassified``.
    host: str | None = None
    resolved_urls: tuple[str, ...] = ()


def companion_ids(claims: Iterable, sources: Mapping[str, Source],
                  attempted: Iterable[str]) -> list[str]:
    """Non-rendered sources cited beside a source this run attempted, sorted."""
    attempted = set(attempted)
    found: set[str] = set()
    for claim in claims:
        cited = {ref.source_id for ref in claim.sources}
        if not cited & attempted:
            continue
        for sid in cited - attempted:
            source = sources.get(sid)
            if source is not None and source.fetch != FetchMode.RENDERED.value:
                found.add(sid)
    return sorted(found)


def _classified(host: str | None, terms: Mapping[str, str]) -> bool:
    return is_classified(host, terms)


def fetch_companions(
    source_ids: Iterable[str],
    sources: Mapping[str, Source],
    *,
    fetcher: Fetcher,
    store: CopyStore,
    terms: Mapping[str, str],
    now: datetime | None = None,
) -> dict[str, CompanionRead]:
    """Fetch each companion over plain HTTP and retain it under the retention policy.

    ``terms`` is the terms register (host to class). A redirect to another host that
    is absent from it is refused before the request is sent.
    """
    now = now or datetime.now(UTC)
    reads: dict[str, CompanionRead] = {}
    for sid in sorted(set(source_ids)):
        source = sources[sid]
        if source.fetch == FetchMode.RENDERED.value:
            raise ValueError(f"{sid} is a rendered source, not a companion")
        url = canonical_url(str(source.url))
        try:
            start = canonical_host(url)
        except ValueError:
            start = None

        def check(request, start=start) -> None:
            try:
                host = canonical_host(str(request.url))
            except ValueError:
                host = None
            if host != start and not _classified(host, terms):
                raise UnclassifiedRedirectError(host or "unparseable")

        hooks = fetcher.client.event_hooks["request"]
        hooks.append(check)
        try:
            result = fetcher.fetch(url)
        except UnclassifiedRedirectError as stop:
            reads[sid] = CompanionRead(sid, "redirect_unclassified", host=stop.host,
                                       error=f"redirect to a host with no terms class: {stop.host}")
            continue
        finally:
            hooks.remove(check)
        if (why := refusal_reason(result)) is not None:
            reads[sid] = CompanionRead(sid, "redirect_unclassified",
                                       host=why.partition(":")[2] or None, error=why)
            continue
        if result.outcome != "ok" or not result.body.strip():
            reads[sid] = CompanionRead(sid, "unreachable", error=result.error or "empty body",
                                       resolved_urls=result.resolved_urls)
            continue
        try:
            ref = store.put(result.body, source_url=url, retrieved_at=result.retrieved_at or now,
                            resolved_urls=result.resolved_urls,
                            shell_check=ShellCheck(source.normaliser,
                                                   shell_alias_urls(source, sources.values())))
        except ShellPageError as stop:
            reads[sid] = CompanionRead(sid, "shell_page", error=shell_refusal(stop.reason, sid),
                                       resolved_urls=result.resolved_urls)
            continue
        cited = store.citation(ref) is not None
        reads[sid] = CompanionRead(sid, "cited" if cited else "ok", copy=ref,
                                   resolved_urls=result.resolved_urls)
    return reads


def claim_with_copies(claim, copies: Mapping[str, str | None], reads: Mapping[str, CompanionRead]):
    """``claim`` with each cited source pointing at the copy read this run.

    A source read this run (``copies``, the rendered pages, or ``reads``, the
    companions) takes its fresh ref; one that failed takes ``MISSING_COPY``. A
    source in neither keeps its filed ref and is the caller's ``not_reread`` case.
    """
    def ref_for(ref):
        sid = ref.source_id
        if sid in reads:
            return ref.model_copy(update={"snapshot_ref": reads[sid].copy or MISSING_COPY})
        if sid in copies:
            return ref.model_copy(update={"snapshot_ref": copies[sid] or MISSING_COPY})
        return ref

    return replace(claim, sources=tuple(ref_for(ref) for ref in claim.sources))


def judge(
    claim,
    *,
    copies: Mapping[str, str | None],
    reads: Mapping[str, CompanionRead],
    verify_claim: Callable[[object], object],
):
    """Judge a fact on every source it cites, or say why it was not judged.

    ``copies`` maps the sources this run read to their copy refs; a source whose read
    failed maps to ``None``. ``verify_claim`` gets the claim with fresh refs and returns
    the verifier's ``Result``.
    """
    from decision.verify import Result

    cited = [ref.source_id for ref in claim.sources]
    unclassified = [reads[sid] for sid in cited
                    if sid in reads and reads[sid].outcome == "redirect_unclassified"]
    if unclassified:
        first = unclassified[0]
        return Result(claim.target, "skipped",
                      reason=(f"redirect_unclassified:{first.source_id}:{first.host}"
                              if first.host else "terms_register_unreadable"))
    shelled = [reads[sid] for sid in cited
               if sid in reads and reads[sid].outcome == "shell_page"]
    if shelled:
        return Result(claim.target, "skipped", reason=shelled[0].error)
    unread = sorted({sid for sid in cited if sid not in copies and sid not in reads})
    if unread:
        return Result(claim.target, "skipped", reason="not_reread:" + ",".join(unread))
    return verify_claim(claim_with_copies(claim, copies, reads))


def refused(reads: Mapping[str, CompanionRead]) -> dict[str, str]:
    """Companions refused at the terms register, by source id. A job ends red when this is
    not empty; it is its own count, never folded into ``unreachable``."""
    return {sid: read.error or "redirect_unclassified" for sid, read in sorted(reads.items())
            if read.outcome == "redirect_unclassified"}


def shell_pages(reads: Mapping[str, CompanionRead]) -> dict[str, str]:
    """Companions whose bytes were a shell (MODEL-519), by source id. Its own count, and a
    job ends red when this is not empty."""
    return {sid: read.error or "shell_page" for sid, read in sorted(reads.items())
            if read.outcome == "shell_page"}


def report_rows(reads: Mapping[str, CompanionRead]) -> dict[str, dict]:
    """Per-source report entries for the job's report, with no page text."""
    return {sid: dict(outcome=read.outcome, copy=read.copy, error=read.error, host=read.host)
            for sid, read in sorted(reads.items())}


__all__: Sequence[str] = [
    "MISSING_COPY", "CompanionRead", "UnclassifiedRedirectError",
    "companion_ids", "fetch_companions", "refused", "shell_pages",
    "claim_with_copies", "judge", "report_rows",
]
