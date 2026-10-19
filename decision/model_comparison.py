"""Complete sourced facts for named models, shared by static pages and the API."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from decision.contract import MODEL_COMPARISON_VERSION, FacetLookup
from decision.engine import offering_ref
from decision.explain import DISPLAY_FACETS, source_ids
from decision.registry import facet as registry_facet
from decision.snapshot import ExplanationIndex


def collect_models(
    models: Sequence[str], snapshot: ExplanationIndex, *, facets: FacetLookup | None = None
) -> dict[str, Any]:
    """Collect validated model IDs without a transport budget or an objective."""
    snapshot.require_explanation_records()
    candidates = tuple(snapshot.candidates())
    lookup = facets or registry_facet
    definitions = [
        lookup(name) for name in sorted(set(snapshot.facet_ids()) | set(DISPLAY_FACETS))
    ]
    model_facets = [f for f in definitions if f.subject == "model" and not f.computed_by]
    offering_facets = [
        f
        for f in definitions
        if f.subject == "offering"
        and not f.computed_by
        and f.id not in {"offering.provider", "offering.region", "offering.tier"}
    ]

    def facts(cid, definitions):
        rows = []
        for definition in definitions:
            found = snapshot.fact(cid, definition.id)
            row = {
                "facet": definition.id,
                "state": found.state,
                "value": found.value,
                "unit": definition.unit,
            }
            citation = (snapshot.record(found.record_id).get("citation")
                        if found.record_id is not None else None)
            if found.state == "known" or citation is not None:
                row["record_id"] = found.record_id
                row["source_ids"] = source_ids(snapshot, [found.record_id])
                if citation is not None:
                    row["citation"] = citation
            rows.append(row)
        return rows

    rows = []
    for mid in models:
        members = [cid for cid in candidates if snapshot.model_of(cid) == mid]
        cid = next((cid for cid in members if snapshot.kind(cid) == "model"), members[0])
        measurements = []
        for benchmark in snapshot.benchmark_ids():
            for value in snapshot.evidence(cid, benchmark):
                measurements.append(
                    {
                        "benchmark": benchmark,
                        "value": value.value,
                        "unit": value.unit,
                        "record_id": value.record_id,
                        "source_ids": source_ids(snapshot, [value.record_id]),
                        "version": value.version,
                        "effort": value.effort,
                        "harness": value.harness,
                        "measured_by": value.measured_by,
                        "date": value.date.isoformat() if value.date else None,
                        "subcategory": value.subcategory,
                        "interval": list(value.interval) if value.interval else None,
                        "n": value.n,
                    }
                )
        rows.append(
            {
                "model": mid,
                "lifecycle": snapshot.lifecycle(cid),
                "facts": facts(cid, model_facets),
                "evidence": measurements,
                "offerings": [
                    {
                        "offering": offering_ref(snapshot, member).model_dump(mode="json"),
                        "facts": facts(member, offering_facets),
                    }
                    for member in members
                    if snapshot.kind(member) == "offering"
                ],
            }
        )
    body = {
        "comparison_version": MODEL_COMPARISON_VERSION,
        "endpoint": "compare-models",
        "snapshot": snapshot.snapshot_id,
        "models": rows,
        "sources": [],
        "omitted": {"facts": 0, "offerings": 0, "evidence": 0},
    }
    update_sources(body, snapshot)
    return body


def update_sources(body: dict[str, Any], snapshot: ExplanationIndex) -> None:
    """Keep citations consistent after a caller removes complete records."""
    rows = body["models"]
    items = [item for row in rows for item in row["facts"] + row["evidence"]]
    items.extend(
        item for row in rows for offering in row["offerings"] for item in offering["facts"]
    )
    ids = sorted({source for item in items for source in item.get("source_ids", [])})
    body["sources"] = [{"id": sid, "url": snapshot.source_url(sid)} for sid in ids]
