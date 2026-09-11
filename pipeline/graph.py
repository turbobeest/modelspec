"""Emit the knowledge graph as JSON, one file per edge view.

The derivation lives in `schema/graph.py` and is shared with the FalkorDB
ingest, so the published graph and the database can never disagree about what
the cards say. Nothing here needs a database running.

Why per-view files rather than one graph the client filters: the whole graph is
thousands of nodes and tens of thousands of edges. That is still a JSON file,
but far too dense to render legibly all at once. Each view answers one question,
and answering one question at a time is what makes a force-directed graph
readable rather than a hairball.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
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

#: Cloudflare Pages refuses any file over 25 MiB. The hardware view is the one
#: that actually hits it: every open-weight model × every device is a FITS_ON
#: edge, each carrying a fat props dict. The explorer already samples illegible
#: views down to LEGIBLE_EDGE_LIMIT and never reads edge props, so those views
#: are published as topology only. Full properties stay on the sink (model
#: pages, ranking candidates, FalkorDB).
CLOUDFLARE_PAGES_MAX_FILE_BYTES = 25 * 1024 * 1024


def _publish_edge(edge: dict[str, Any], *, include_props: bool) -> dict[str, Any]:
    """The view identity of an edge. Props are omitted on hairball views."""
    published = {
        "from": node_key(edge["from_label"], edge["from"]),
        "from_label": edge["from_label"],
        "to": node_key(edge["to_label"], edge["to"]),
        "to_label": edge["to_label"],
        "type": edge["type"],
    }
    if include_props and "props" in edge:
        published["props"] = edge["props"]
    return published


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


def is_hf_repo_id(value: str) -> bool:
    """A Hub repo id is `org/name`. Card ids look the same, so this is not identity."""
    if value.count("/") != 1 or "://" in value or value.startswith("/"):
        return False
    org, name = value.split("/")
    return bool(org) and bool(name)


def _norm_seg(value: str) -> str:
    return value.lower().replace(".", "-").replace("_", "-")


def prefer_card(hf_id: str, left: str, right: str) -> str:
    """When two cards share a Hub id, pick the one whose slug matches the repo name."""
    target = _norm_seg(hf_id.rsplit("/", 1)[-1])

    def score(card_id: str) -> tuple[int, int, int]:
        suffix = _norm_seg(card_id.rsplit("/", 1)[-1])
        exact = 1 if suffix == target else 0
        contained = 1 if target in suffix or suffix in target else 0
        return (exact, contained, -abs(len(suffix) - len(target)))

    return left if score(left) >= score(right) else right


def huggingface_ids(cards: Iterable[Any]) -> dict[str, str]:
    """Hugging Face repo id → ModelSpec card id, collisions resolved by prefer_card."""
    mapping: dict[str, str] = {}
    for card in cards:
        hf = str(getattr(card.availability.huggingface, "model_id", "") or "")
        cid = str(card.identity.model_id)
        if not hf:
            continue
        mapping[hf] = cid if hf not in mapping else prefer_card(hf, mapping[hf], cid)
    return mapping


def resolve_card_ids(
    sink: CollectingSink,
    *,
    card_ids: set[str],
    huggingface_ids: dict[str, str],
) -> dict[str, int]:
    """Rewrite Model nodes that are Hub repo ids to the card they belong to.

    Lineage fields store Hugging Face repo ids. The graph ingest copies them
    onto Model nodes as-is, so a renderer that links `/m/{id}/` 404s. Resolve
    to the card when one exists. Leave unresolved ids in place — the renderer
    must not mint an internal href for them.
    """
    aliases = {
        hf: card for hf, card in huggingface_ids.items()
        if hf and hf not in card_ids
    }

    def resolve(node_id: str) -> str:
        if node_id in card_ids:
            return node_id
        return aliases.get(node_id, node_id)

    rewritten = 0
    unresolved = 0
    merged: dict[tuple[str, str], dict[str, Any]] = {}
    for (label, nid), props in sink.nodes.items():
        if label != "Model":
            merged[(label, nid)] = dict(props)
            continue
        new_id = resolve(nid)
        incoming = dict(props)
        if new_id != nid:
            rewritten += 1
            incoming["id"] = new_id
            incoming.setdefault("huggingface_id", nid)
        elif nid not in card_ids:
            unresolved += 1
        key = ("Model", new_id)
        existing = merged.get(key)
        if existing is None:
            merged[key] = incoming
            continue
        richer, poorer = (
            (existing, incoming)
            if (1 if existing.get("display_name") else 0, len(existing))
            >= (1 if incoming.get("display_name") else 0, len(incoming))
            else (incoming, existing)
        )
        combined = {**poorer, **richer, "id": new_id}
        merged[key] = combined

    sink.nodes.clear()
    sink.nodes.update(merged)

    for edge in sink.edges:
        if edge["from_label"] == "Model":
            edge["from"] = resolve(edge["from"])
        if edge["to_label"] == "Model":
            edge["to"] = resolve(edge["to"])

    return {"rewritten": rewritten, "unresolved": unresolved}


def write(out_dir: Path, sink: CollectingSink, build_json: dict[str, Any],
          card_ids: set[str] | None = None) -> dict[str, Any]:
    """Write the node catalogue, one file per view, and a search index."""
    out_dir.mkdir(parents=True, exist_ok=True)

    def dump(rel: str, payload: Any) -> int:
        path = out_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(payload, sort_keys=True, default=str)
        n = len(text.encode("utf-8"))
        if n > CLOUDFLARE_PAGES_MAX_FILE_BYTES:
            raise ValueError(
                f"{rel} is {n} bytes; Cloudflare Pages refuses files over "
                f"{CLOUDFLARE_PAGES_MAX_FILE_BYTES} bytes"
            )
        path.write_text(text, encoding="utf-8")
        return n

    nodes: dict[str, dict[str, Any]] = {}
    for (label, node_id), props in sink.nodes.items():
        payload = _node_payload(label, node_id, props)
        if label == "Model" and card_ids is not None:
            payload["has_page"] = node_id in card_ids
            if not payload["has_page"] and is_hf_repo_id(node_id):
                payload["huggingface_url"] = f"https://huggingface.co/{node_id}"
        nodes[payload["key"]] = payload
    dump("nodes.json", {"build": build_json, "count": len(nodes), "nodes": list(nodes.values())})

    summaries: list[dict[str, Any]] = []
    for view in VIEWS:
        raw = [e for e in sink.edges if e["type"] in view.edge_types]
        # A hairball is topology for the explorer, not a dump of every prop.
        # Legible views keep props so a small JSON file stays self-contained.
        include_props = len(raw) <= LEGIBLE_EDGE_LIMIT
        edges = [_publish_edge(e, include_props=include_props) for e in raw]
        # A view carries only the nodes its own edges touch, so the client never
        # renders an unconnected cloud of everything else.
        touched = sorted({e["from"] for e in edges} | {e["to"] for e in edges})
        missing = [n for n in touched if n not in nodes]
        if missing:
            raise ValueError(f"view {view.key!r} references unknown nodes: {missing[:5]}")

        legible = include_props
        size = dump(f"views/{view.key}.json", {
            "build": build_json,
            "key": view.key,
            "title": view.title,
            "question": view.question,
            "edge_types": list(view.edge_types),
            "counts": {"nodes": len(touched), "edges": len(edges)},
            "legible": legible,
            "legible_edge_limit": LEGIBLE_EDGE_LIMIT,
            "edge_properties": include_props,
            "nodes": [nodes[n] for n in touched],
            "edges": edges,
        })
        summaries.append({
            "key": view.key, "title": view.title, "question": view.question,
            "nodes": len(touched), "edges": len(edges),
            "legible": legible, "edge_properties": include_props,
            "bytes": size, "empty": not edges,
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
