"""Emit the knowledge graph as JSON, one file per edge view.

The derivation lives in `schema/graph.py` and is shared with the FalkorDB
ingest, so the published graph and the database can never disagree about what
the cards say. Nothing here needs a database running.

Why per-view files rather than one graph the client filters: the whole graph is
~1,600 nodes and ~18,600 edges. That is trivial as JSON but far too dense to
render legibly all at once. Each view answers one question, and answering one
question at a time is what makes a force-directed graph readable rather than a
hairball.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from schema.graph import CollectingSink


@dataclass(frozen=True)
class View:
    """One readable slice of the graph."""

    key: str
    title: str
    question: str
    edge_types: tuple[str, ...]


#: Each view is named for the question it answers, not for its edge type.
VIEWS: tuple[View, ...] = (
    View("lineage", "Lineage", "What is this model descended from?", ("DERIVED_FROM",)),
    View("provider", "Providers", "Who made what?", ("MADE_BY",)),
    View("platforms", "Availability", "Where can I actually run this?", ("AVAILABLE_ON",)),
    View("benchmarks", "Benchmark coverage", "Which models report which benchmarks?", ("SCORED_ON",)),
    View("capabilities", "Capabilities", "What can these models do?", ("HAS_CAPABILITY",)),
    View("hardware", "Hardware fit", "What fits on my machine?", ("FITS_ON",)),
    View("licensing", "Licensing", "What am I allowed to do with it?", ("LICENSED_AS",)),
    View("competition", "Competition", "What competes with what?", ("COMPETES_WITH",)),
)

#: Above this, a force-directed layout stops being readable and starts being a
#: hairball. The view is still published; the client is told to sample or warn.
LEGIBLE_EDGE_LIMIT = 4000


def node_key(label: str, node_id: str) -> str:
    """The published identity of a node.

    An id alone is not unique across labels: in the current corpus `deepseek` is
    a Provider, a Platform *and* a License, and `cohere` and `perplexity` are
    both Provider and Platform. FalkorDB disambiguates by label in its MATCH, so
    the database is unaffected — but a flat export keyed on the bare id would
    silently collapse those nodes and make their edges ambiguous.
    """
    return f"{label}:{node_id}"


def _node_payload(label: str, node_id: str, props: dict[str, Any]) -> dict[str, Any]:
    return {"key": node_key(label, node_id), "id": node_id, "label": label, **props}


def write(out_dir: Path, sink: CollectingSink, build_json: dict[str, Any]) -> dict[str, Any]:
    """Write the node catalogue, one file per view, and a search index."""
    out_dir.mkdir(parents=True, exist_ok=True)

    def dump(rel: str, payload: Any) -> int:
        path = out_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(payload, sort_keys=True, default=str)
        path.write_text(text, encoding="utf-8")
        return len(text.encode("utf-8"))

    nodes = {
        node_key(label, node_id): _node_payload(label, node_id, props)
        for (label, node_id), props in sink.nodes.items()
    }
    dump("nodes.json", {"build": build_json, "count": len(nodes), "nodes": list(nodes.values())})

    summaries: list[dict[str, Any]] = []
    for view in VIEWS:
        edges = [
            {**e,
             "from": node_key(e["from_label"], e["from"]),
             "to": node_key(e["to_label"], e["to"])}
            for e in sink.edges if e["type"] in view.edge_types
        ]
        # A view carries only the nodes its own edges touch, so the client never
        # renders an unconnected cloud of everything else.
        touched = sorted({e["from"] for e in edges} | {e["to"] for e in edges})
        missing = [n for n in touched if n not in nodes]
        if missing:
            raise ValueError(f"view {view.key!r} references unknown nodes: {missing[:5]}")

        legible = len(edges) <= LEGIBLE_EDGE_LIMIT
        size = dump(f"views/{view.key}.json", {
            "build": build_json,
            "key": view.key,
            "title": view.title,
            "question": view.question,
            "edge_types": list(view.edge_types),
            "counts": {"nodes": len(touched), "edges": len(edges)},
            "legible": legible,
            "legible_edge_limit": LEGIBLE_EDGE_LIMIT,
            "nodes": [nodes[n] for n in touched],
            "edges": edges,
        })
        summaries.append({
            "key": view.key, "title": view.title, "question": view.question,
            "nodes": len(touched), "edges": len(edges),
            "legible": legible, "bytes": size,
            "empty": not edges,
        })

    dump("views.json", {"build": build_json, "views": summaries})

    # Search index: enough to find a node, not enough to duplicate the pages.
    dump("search.json", {
        "build": build_json,
        "entries": sorted(
            ({"key": n["key"], "id": n["id"], "label": n["label"],
              "name": str(n.get("display_name") or n.get("name") or n["id"])}
             for n in nodes.values()),
            key=lambda e: (e["label"], e["name"].lower()),
        ),
    })

    return {
        "nodes": len(nodes),
        "edges": len(sink.edges),
        "views": {s["key"]: {"nodes": s["nodes"], "edges": s["edges"], "legible": s["legible"]}
                  for s in summaries},
    }
