"""Resolve Hugging Face repo ids in the derived graph to the cards they belong to.

Lineage fields store Hub repo ids, and the graph derivation in `schema/graph.py`
copies them onto Model nodes as they are. The build rewrites those nodes to card
ids before relations, competition and ranking read the graph, so every consumer
sees one node per model. This used to live in `pipeline/graph.py` beside the
`/graph/` explorer's export, which MODEL-251 removed.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from schema.graph import CollectingSink


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
