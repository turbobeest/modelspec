"""Citation assurance derived from registered origins and source references."""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from decision.retention import citation_metadata, cite_only_origin, require_source_url


def fact_citation(record: Mapping[str, Any], sources: Mapping[str, str]) -> dict | None:
    """Return cite-only provenance, or None when every origin permits retention.

    Invalid citations raise ValueError. A supplied citation status is never
    trusted; the registered source and observed redirect origins decide it.
    """
    refs = record.get("sources") or ()
    if not any(cite_only_origin(sources.get(ref.get("source_id"), ""),
                                ref.get("resolved_urls") or ()) for ref in refs):
        return None
    cited = []
    for ref in refs:
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
        redirects = [require_source_url(url) for url in ref.get("resolved_urls") or ()]
        metadata = citation_metadata(sources[source_id], snapshot_ref,
                                     retrieved_at=when, resolved_urls=redirects)
        if not metadata["resolved_urls"]:
            metadata.pop("resolved_urls")
        cited.append({"source_id": source_id, **metadata})
    return {"status": "cited", "sources": cited}
