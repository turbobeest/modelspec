"""Citation assurance derived from registered origins and source references."""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import datetime
from typing import Any, Literal

from decision.retention import (
    citation_metadata, cite_only_origin, is_cite_only, metadata_origins, require_source_url,
)

_HASH = re.compile(r"sha256:[0-9a-f]{64}")

RefState = Literal["cited", "restricted", "open"]


def _fetcher_record(ref: Mapping[str, Any], sources: Mapping[str, str],
                    store: Any) -> Mapping[str, Any] | None:
    """The fetcher's citation record for this ref's snapshot hash, or None.

    A record the store cannot read, or one that names another source, raises
    ValueError: an unreadable redirect is never read as "no redirect".
    """
    snapshot_ref = ref.get("snapshot_ref")
    if store is None or not isinstance(snapshot_ref, str) or not _HASH.fullmatch(snapshot_ref):
        return None
    try:
        metadata = store.citation(snapshot_ref)
    except OSError:
        raise ValueError("unreadable citation record") from None
    if metadata is None:
        return None
    if not isinstance(metadata, Mapping) or metadata.get("snapshot_ref") != snapshot_ref:
        raise ValueError("citation record does not match its hash")
    if metadata.get("url") != sources.get(ref.get("source_id")):
        raise ValueError("citation record names another source")
    return metadata


def ref_state(ref: Mapping[str, Any], sources: Mapping[str, str], store: Any = None) -> RefState:
    """How the retention policy treats one source reference.

    ``cited``: the registered URL, or a redirect origin in the fetcher's
    citation record (``store``) for this ref's snapshot hash, is cite-only.
    Only a cited ref can stand in for verification.
    ``restricted``: not cited, but the card's own ``resolved_urls`` name a
    cite-only host, or the store holds a citation record for this hash. Its
    bytes are never retained and it still needs verification.
    ``open``: neither. Card-authored fields only ever make a ref stricter.
    """
    registered = sources.get(ref.get("source_id"), "")
    record = _fetcher_record(ref, sources, store)
    if is_cite_only(registered):
        return "cited"
    if record is not None:
        try:
            origins = metadata_origins(dict(record))
        except (TypeError, ValueError):
            raise ValueError("invalid citation redirect record") from None
        return "cited" if cite_only_origin(registered, origins) else "restricted"
    resolved = ref.get("resolved_urls") or ()
    if not isinstance(resolved, (list, tuple)):
        raise ValueError("invalid citation redirect URLs")
    return "restricted" if cite_only_origin("", resolved) else "open"


def ref_states(record: Mapping[str, Any], sources: Mapping[str, str],
               store: Any = None) -> tuple[RefState, ...]:
    return tuple(ref_state(ref, sources, store) for ref in record.get("sources") or ())


def mixed_citation(record: Mapping[str, Any], sources: Mapping[str, str],
                   store: Any = None) -> bool:
    """Whether a fact cites a cite-only source beside one that is not cited.

    Such a fact is quarantined: its other sources were never machine-verified
    apart from the cite-only one (docs/design/cite-only-sources.md).
    """
    states = ref_states(record, sources, store)
    return "cited" in states and any(state != "cited" for state in states)


def fact_citation(record: Mapping[str, Any], sources: Mapping[str, str],
                  store: Any = None) -> dict | None:
    """Return cite-only provenance, or None when no source ref is cited.

    Invalid citations raise ValueError. A supplied citation status is never
    trusted, and neither are a card's own ``resolved_urls``: the registered
    source URL decides, plus redirect origins in the fetcher's citation record
    in ``store`` for the ref's snapshot hash. Callers that admit facts must
    also refuse a ``mixed_citation``.
    """
    refs = record.get("sources") or ()
    if "cited" not in ref_states(record, sources, store):
        return None
    cited = []
    for ref in refs:
        source_id, snapshot_ref = ref.get("source_id"), ref.get("snapshot_ref")
        if source_id not in sources:
            raise ValueError("unresolved citation source")
        if not isinstance(snapshot_ref, str) or not _HASH.fullmatch(snapshot_ref):
            raise ValueError("invalid citation snapshot hash")
        if not ref.get("cited_regions"):
            raise ValueError("citation requires a cited region")
        when = ref.get("retrieved_at")
        if when is not None:
            parsed = when if isinstance(when, datetime) else datetime.fromisoformat(str(when))
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                raise ValueError("citation retrieval time must include its timezone")
        fetched = _fetcher_record(ref, sources, store)
        shown = (fetched.get("resolved_urls") if fetched is not None
                 else ref.get("resolved_urls")) or ()
        redirects = [require_source_url(url) for url in shown]
        metadata = citation_metadata(sources[source_id], snapshot_ref,
                                     retrieved_at=when, resolved_urls=redirects)
        if not metadata["resolved_urls"]:
            metadata.pop("resolved_urls")
        cited.append({"source_id": source_id, **metadata})
    return {"status": "cited", "sources": cited}
