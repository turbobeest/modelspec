"""The graph must derive without a database, and stay internally consistent.

The derivation in `schema/graph.py` is shared with the FalkorDB ingest. These
tests pin the sink contract that makes that sharing safe, so what the build
reads and the database cannot drift apart.
"""

from __future__ import annotations

import functools
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.card_ids import prefer_card, resolve_card_ids  # noqa: E402
from schema.card import HardwareProfile, ModelCard  # noqa: E402
from schema.graph import (  # noqa: E402
    INDEXES, CollectingSink, CypherSink, derive_graph, ingest_model_card,
)


@functools.lru_cache(maxsize=1)
def _sink() -> CollectingSink:
    paths = sorted(p for p in (REPO_ROOT / "models").rglob("*.md") if p.name != "LICENSE.md")
    return derive_graph([ModelCard.from_yaml_file(str(p)) for p in paths])


# ── the sink contract ────────────────────────────────────────────────────────

def test_collecting_sink_merges_like_merge_set() -> None:
    """A node seen twice keeps the union of its properties, later values winning.

    This matters because a model can be referenced as another model's base model
    before its own card is read; without merge semantics it would be published
    as a bare id.
    """
    sink = CollectingSink()
    sink.node("Model", "id", "m1", {"id": "m1"})
    sink.node("Model", "id", "m1", {"id": "m1", "display_name": "One", "family": "f"})
    sink.node("Model", "id", "m1", {"id": "m1", "display_name": "One v2"})
    assert sink.nodes[("Model", "m1")] == {"id": "m1", "display_name": "One v2", "family": "f"}


def test_collecting_sink_ignores_nulls() -> None:
    """Null means "not yet researched" in this schema and must not overwrite a value."""
    sink = CollectingSink()
    sink.node("Model", "id", "m1", {"id": "m1", "family": "real"})
    sink.node("Model", "id", "m1", {"id": "m1", "family": None})
    assert sink.nodes[("Model", "m1")]["family"] == "real"


def test_ingest_still_accepts_a_raw_graph_handle() -> None:
    """scripts/ingest_all.py passes a FalkorDB graph, not a sink. Keep that working."""
    class FakeGraph:
        def __init__(self) -> None:
            self.queries: list[str] = []

        def query(self, q: str, params: dict | None = None) -> None:
            self.queries.append(q)

    fake = FakeGraph()
    card = ModelCard.from_yaml_file(str(REPO_ROOT / "models/anthropic/claude-haiku-4-5.md"))
    ingest_model_card(fake, card)
    assert fake.queries, "a raw graph handle should still receive Cypher"
    assert any(q.startswith("MERGE (n:Model") for q in fake.queries)


def test_cypher_sink_and_collecting_sink_agree_on_shape() -> None:
    """Both sinks must see the same derivation for the same card."""
    class FakeGraph:
        def __init__(self) -> None:
            self.merges = 0

        def query(self, q: str, params: dict | None = None) -> None:
            self.merges += 1

    card = ModelCard.from_yaml_file(str(REPO_ROOT / "models/anthropic/claude-haiku-4-5.md"))
    fake = FakeGraph()
    ingest_model_card(CypherSink(fake), card)
    collected = CollectingSink()
    ingest_model_card(collected, card)
    assert fake.merges == len(collected.nodes) + len(collected.edges)


# ── the derived graph ────────────────────────────────────────────────────────

def test_graph_derives_with_no_database() -> None:
    sink = _sink()
    assert len(sink.nodes) > 1000
    assert len(sink.edges) > 10000


def test_every_edge_endpoint_resolves_to_a_node() -> None:
    """A dangling edge would render as a node that appears from nowhere."""
    sink = _sink()
    ids = {node_id for _, node_id in sink.nodes}
    for edge in sink.edges:
        assert edge["from"] in ids, f"{edge['type']} from unknown node {edge['from']}"
        assert edge["to"] in ids, f"{edge['type']} to unknown node {edge['to']}"


def test_models_referenced_only_as_a_base_model_still_become_nodes() -> None:
    """Lineage points at models that have no card of their own; they must exist."""
    sink = _sink()
    model_ids = {i for label, i in sink.nodes if label == "Model"}
    carded = {p.stem for p in (REPO_ROOT / "models").rglob("*.md") if p.name != "LICENSE.md"}
    assert len(model_ids) > len(carded) - 50  # sanity: most cards produced a node
    for edge in (e for e in sink.edges if e["type"] == "DERIVED_FROM"):
        assert edge["to"] in model_ids


# ── Hub repo ids are not card ids ────────────────────────────────────────────

def test_prefer_card_picks_the_slug_that_matches_the_repo() -> None:
    assert prefer_card(
        "google/gemma-4-26B-A4B-it",
        "google/gemma-4-26b",
        "google/gemma-4-26b-a4b-it",
    ) == "google/gemma-4-26b-a4b-it"


def test_huggingface_lineage_ids_resolve_to_cards() -> None:
    sink = CollectingSink()
    sink.node("Model", "id", "unsloth/qwen3-0-6b",
              {"id": "unsloth/qwen3-0-6b", "display_name": "Unsloth Qwen3 0.6B"})
    sink.node("Model", "id", "qwen/qwen3-0-6b",
              {"id": "qwen/qwen3-0-6b", "display_name": "Qwen3 0.6B"})
    sink.node("Model", "id", "Qwen/Qwen3-0.6B", {"id": "Qwen/Qwen3-0.6B"})
    sink.edge("Model", "unsloth/qwen3-0-6b", "DERIVED_FROM", "Model", "Qwen/Qwen3-0.6B")
    resolve_card_ids(
        sink,
        card_ids={"unsloth/qwen3-0-6b", "qwen/qwen3-0-6b"},
        huggingface_ids={"Qwen/Qwen3-0.6B": "qwen/qwen3-0-6b"},
    )
    assert ("Model", "Qwen/Qwen3-0.6B") not in sink.nodes
    assert sink.nodes[("Model", "qwen/qwen3-0-6b")]["display_name"] == "Qwen3 0.6B"
    assert sink.edges[0]["to"] == "qwen/qwen3-0-6b"


def test_unresolved_hub_ids_stay_in_place() -> None:
    sink = CollectingSink()
    sink.node("Model", "id", "child", {"id": "child", "display_name": "Child"})
    sink.node("Model", "id", "Qwen/Qwen2.5-32B", {"id": "Qwen/Qwen2.5-32B"})
    sink.edge("Model", "child", "DERIVED_FROM", "Model", "Qwen/Qwen2.5-32B")
    counts = resolve_card_ids(sink, card_ids={"child"}, huggingface_ids={})
    assert counts == {"rewritten": 0, "unresolved": 1}
    assert ("Model", "Qwen/Qwen2.5-32B") in sink.nodes
    assert sink.edges[0]["to"] == "Qwen/Qwen2.5-32B"

















# ── Hardware nodes carry their device class (MODEL-76) ───────────────────────

def _fitting_card(hw_id: str) -> ModelCard:
    """A card whose deployment profile says it fits on `hw_id`.

    No card in the corpus sets `fits: true` today, so the Hardware branch of
    the derivation has to be exercised with one built here.
    """
    card = ModelCard.from_yaml_file(str(REPO_ROOT / "models/anthropic/claude-haiku-4-5.md"))
    card.deployment.hardware_profiles = {hw_id: HardwareProfile(fits=True, best_quant="q4")}
    return card


def test_a_derived_hardware_node_carries_its_device_class() -> None:
    """Without the class the node cannot be grouped or filtered by it."""
    sink = derive_graph([_fitting_card("nvidia_rtx_5090")],
                        {"nvidia_rtx_5090": "consumer"})
    assert sink.nodes[("Hardware", "nvidia_rtx_5090")]["device_class"] == "consumer"




def test_an_unknown_hardware_id_gets_no_class_rather_than_a_guess() -> None:
    """`nvidia_5090_32gb` is a legacy profile key, not a device record.

    Labelling it by resemblance would put a made-up class in the export, which
    is worse than a class filter skipping the node.
    """
    sink = derive_graph([_fitting_card("nvidia_5090_32gb")],
                        {"nvidia_rtx_5090": "consumer"})
    assert "device_class" not in sink.nodes[("Hardware", "nvidia_5090_32gb")]


def test_the_derivation_still_works_with_no_device_records() -> None:
    """scripts/ingest_all.py and the ranking CLI derive without the mapping."""
    sink = derive_graph([_fitting_card("nvidia_rtx_5090")])
    assert ("Hardware", "nvidia_rtx_5090") in sink.nodes
    assert "device_class" not in sink.nodes[("Hardware", "nvidia_rtx_5090")]


def test_a_class_outside_the_vocabulary_is_refused() -> None:
    """A sixth class would split a group in two and be found by nobody."""
    with pytest.raises(ValueError):
        derive_graph([_fitting_card("nvidia_rtx_5090")],
                     {"nvidia_rtx_5090": "datacenter"})


def test_both_sinks_agree_on_a_classed_hardware_node() -> None:
    """The FalkorDB ingest and the JSON export must derive the same node."""
    class FakeGraph:
        def __init__(self) -> None:
            self.params: list[dict] = []

        def query(self, q: str, params: dict | None = None) -> None:
            self.params.append(params or {})

    card = _fitting_card("nvidia_rtx_5090")
    classes = {"nvidia_rtx_5090": "consumer"}
    fake = FakeGraph()
    ingest_model_card(CypherSink(fake), card, device_classes=classes)
    collected = CollectingSink()
    ingest_model_card(collected, card, device_classes=classes)
    assert len(fake.params) == len(collected.nodes) + len(collected.edges)
    assert any(p.get("device_class") == "consumer" for p in fake.params)


def test_the_device_class_index_exists() -> None:
    """Filtering the whole corpus by class without an index is a full scan."""
    assert "CREATE INDEX ON :Hardware(device_class)" in INDEXES


def test_published_model_nodes_do_not_carry_coverage() -> None:
    """applicable_field_coverage is an internal ModelCard statistic (MODEL-74)."""
    sink = _sink()
    for (label, _nid), props in sink.nodes.items():
        if label != "Model":
            continue
        assert "applicable_field_coverage" not in props
        assert "card_completeness" not in props
