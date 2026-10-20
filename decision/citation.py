"""Citation assurance derived from registered origins and source references."""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from decision.retention import (
    citation_metadata, cite_only_origin, metadata_origins, require_source_url,
)


def _trusted_record(ref: Mapping[str, Any], store: Any) -> Mapping[str, Any] | None:
    """Fetcher citation for this ref, or None when the store has no matching record."""
    if store is None:
        return None
    snapshot_ref = ref.get("snapshot_ref")
    if not isinstance(snapshot_ref, str):
        return None
    try:
        metadata = store.citation(snapshot_ref)
    except (OSError, ValueError):
        return None
    if not isinstance(metadata, Mapping) or metadata.get("snapshot_ref") != snapshot_ref:
        return None
    return metadata


def _trusted_origins(ref: Mapping[str, Any], store: Any) -> tuple[str, ...]:
    metadata = _trusted_record(ref, store)
    if metadata is None:
        return ()
    try:
        return metadata_origins(dict(metadata))
    except (TypeError, ValueError):
        return ()


def ref_is_cite_only(ref: Mapping[str, Any], sources: Mapping[str, str],
                     store: Any = None) -> bool:
    """A ref is cite-only from its registered URL or a matching fetcher record."""
    return cite_only_origin(sources.get(ref.get("source_id"), ""), _trusted_origins(ref, store))


def fact_citation(record: Mapping[str, Any], sources: Mapping[str, str],
                  store: Any = None) -> dict | None:
    """Return cite-only provenance when every source ref is cite-only.

    Invalid citations raise ValueError. A supplied citation status is never
    trusted. The registered source URL decides, plus redirect origins from
    ``store`` when its citation record names this ref's snapshot hash.
    """
    refs = list(record.get("sources") or ())
    decisions = []
    for ref in refs:
        trusted = _trusted_record(ref, store)
        origins: tuple[str, ...] = ()
        if trusted is not None:
            try:
                origins = metadata_origins(dict(trusted))
            except (TypeError, ValueError):
                origins = ()
        cite = cite_only_origin(sources.get(ref.get("source_id"), ""), origins)
        decisions.append((ref, cite, trusted if cite else None))
    if not any(cite for _ref, cite, _trusted in decisions):
        return None
    cited = []
    for ref, cite, trusted in decisions:
        if not cite:
            continue
        source_id, snapshot_ref = ref.get("source_id"), ref.get("snapshot_ref")
        if source_id not in sources:
            raise ValueError("unresolved citation source")
        if not isinstance(snapshot_ref, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", snapshot_ref):
            raise ValueError("invalid citation snapshot hash")
        if not ref.get("cited_regions"):
            raise ValueError("citation requires a cited region")
        when = ref.get("retrieved_at")
        if when is not None:
            parsed = when if isinstance(when, datetime) else datetime.fromisoformat(str(when))
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                raise ValueError("citation retrieval time must include its timezone")
        redirects = []
        if trusted is not None:
            redirects = [require_source_url(url) for url in (trusted.get("resolved_urls") or ())]
        metadata = citation_metadata(sources[source_id], snapshot_ref,
                                     retrieved_at=when, resolved_urls=redirects)
        if not metadata["resolved_urls"]:
            metadata.pop("resolved_urls")
        cited.append({"source_id": source_id, **metadata})
    if len(cited) != len(refs):
        return None
    return {"status": "cited", "sources": cited}
