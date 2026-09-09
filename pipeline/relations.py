"""Index the derived graph by model, so a page can render its relationships.

The graph knows everything a model page needs — what it descends from, what
descends from it, where it runs, what it fits on, what it can do, what competes
with it. This turns the flat edge list into per-model lookups.

Ordering here is editorial, not incidental: each list is sorted so the most
useful row is first, because a reader looks at the top of a table and stops.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from schema.graph import CollectingSink


@dataclass
class ModelRelations:
    ancestors: list[dict[str, Any]] = field(default_factory=list)
    descendants: list[dict[str, Any]] = field(default_factory=list)
    platforms: list[dict[str, Any]] = field(default_factory=list)
    hardware: list[dict[str, Any]] = field(default_factory=list)
    capabilities: list[dict[str, Any]] = field(default_factory=list)
    competitors: list[dict[str, Any]] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not any((self.ancestors, self.descendants, self.platforms,
                        self.hardware, self.capabilities, self.competitors))


class Relations:
    """Per-model views of the derived graph."""

    def __init__(self, sink: CollectingSink) -> None:
        self._nodes = {(label, node_id): props for (label, node_id), props in sink.nodes.items()}
        self._by_model: dict[str, ModelRelations] = defaultdict(ModelRelations)

        for edge in sink.edges:
            kind, src, dst = edge["type"], edge["from"], edge["to"]
            props = edge.get("props") or {}

            if kind == "DERIVED_FROM":
                self._by_model[src].ancestors.append(
                    {"id": dst, "name": self._name("Model", dst), **props})
                self._by_model[dst].descendants.append(
                    {"id": src, "name": self._name("Model", src), **props})
            elif kind == "AVAILABLE_ON":
                self._by_model[src].platforms.append(
                    {"id": dst, "name": self._name("Platform", dst), **props})
            elif kind == "FITS_ON":
                self._by_model[src].hardware.append(
                    {"id": dst, "name": self._name("Hardware", dst),
                     "device": self._nodes.get(("Hardware", dst), {}), **props})
            elif kind == "HAS_CAPABILITY":
                self._by_model[src].capabilities.append(
                    {"id": dst, "name": self._name("Capability", dst), **props})
            elif kind == "COMPETES_WITH":
                # Undirected: one edge, both endpoints see it.
                self._by_model[src].competitors.append(
                    {"id": dst, "name": self._name("Model", dst), **props})
                self._by_model[dst].competitors.append(
                    {"id": src, "name": self._name("Model", src), **props})

        for relations in self._by_model.values():
            relations.ancestors.sort(key=lambda r: str(r["name"]).lower())
            relations.descendants.sort(key=lambda r: str(r["name"]).lower())
            relations.platforms.sort(key=lambda r: str(r["name"]).lower())
            relations.capabilities.sort(key=lambda r: str(r["name"]).lower())
            # Closest competitor first — the reason a reader opens this section.
            relations.competitors.sort(key=lambda r: -float(r.get("overlap_score") or 0))
            # Fastest device first, then by the memory it needs.
            relations.hardware.sort(
                key=lambda r: (-float(r.get("fastest_predicted_decode_tps") or 0),
                               str(r["name"]).lower()))

    def _name(self, label: str, node_id: str) -> str:
        props = self._nodes.get((label, node_id), {})
        return str(props.get("display_name") or props.get("name") or node_id)

    def for_model(self, model_id: str) -> ModelRelations:
        return self._by_model.get(model_id, ModelRelations())

    def counts(self) -> dict[str, int]:
        return {
            "models_with_relations": len(self._by_model),
            "with_lineage": sum(1 for r in self._by_model.values()
                                if r.ancestors or r.descendants),
            "with_platforms": sum(1 for r in self._by_model.values() if r.platforms),
            "with_hardware": sum(1 for r in self._by_model.values() if r.hardware),
            "with_competitors": sum(1 for r in self._by_model.values() if r.competitors),
        }
