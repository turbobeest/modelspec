"""The graph must derive without a database, and stay internally consistent.

The derivation in `schema/graph.py` is shared with the FalkorDB ingest. These
tests pin the sink contract that makes that sharing safe, so the published
graph and the database cannot drift apart.
"""

from __future__ import annotations

import functools
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.graph import (  # noqa: E402
    LEGIBLE_EDGE_LIMIT, VIEWS, node_key, prefer_card, resolve_card_ids, write,
)
from schema.card import ModelCard  # noqa: E402
from schema.graph import CollectingSink, CypherSink, derive_graph, ingest_model_card  # noqa: E402


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


def test_unresolved_hub_ids_stay_but_are_marked_as_having_no_page(tmp_path: Path) -> None:
    sink = CollectingSink()
    sink.node("Model", "id", "child", {"id": "child", "display_name": "Child"})
    sink.node("Model", "id", "Qwen/Qwen2.5-32B", {"id": "Qwen/Qwen2.5-32B"})
    sink.edge("Model", "child", "DERIVED_FROM", "Model", "Qwen/Qwen2.5-32B")
    resolve_card_ids(sink, card_ids={"child"}, huggingface_ids={})
    write(tmp_path, sink, {"commit": "test"}, card_ids={"child"})
    nodes = {n["id"]: n for n in json.loads((tmp_path / "nodes.json").read_text())["nodes"]}
    assert nodes["child"]["has_page"] is True
    assert nodes["Qwen/Qwen2.5-32B"]["has_page"] is False
    assert nodes["Qwen/Qwen2.5-32B"]["huggingface_url"] == "https://huggingface.co/Qwen/Qwen2.5-32B"


# ── the published views ──────────────────────────────────────────────────────

def test_views_are_written_and_self_describing(tmp_path: Path) -> None:
    counts = write(tmp_path, _sink(), {"commit": "test"})
    index = json.loads((tmp_path / "views.json").read_text())
    assert {v["key"] for v in index["views"]} == {v.key for v in VIEWS}
    for view in index["views"]:
        assert view["question"], "a view must say which question it answers"
        payload = json.loads((tmp_path / "views" / f"{view['key']}.json").read_text())
        assert payload["counts"]["edges"] == view["edges"]
    assert counts["nodes"] == len(_sink().nodes)


def test_a_view_carries_only_the_nodes_its_edges_touch(tmp_path: Path) -> None:
    write(tmp_path, _sink(), {"commit": "test"})
    payload = json.loads((tmp_path / "views" / "lineage.json").read_text())
    touched = {e["from"] for e in payload["edges"]} | {e["to"] for e in payload["edges"]}
    assert {n["key"] for n in payload["nodes"]} == touched


def test_an_illegible_view_says_so(tmp_path: Path) -> None:
    """Publishing a hairball without warning the client is how tabs hang."""
    write(tmp_path, _sink(), {"commit": "test"})
    payload = json.loads((tmp_path / "views" / "benchmarks.json").read_text())
    assert payload["counts"]["edges"] > LEGIBLE_EDGE_LIMIT
    assert payload["legible"] is False


def test_ids_reused_across_labels_stay_distinct(tmp_path: Path) -> None:
    """`deepseek` is a Provider, a Platform and a License in the current corpus.

    Keyed on the bare id those would collapse into one node and their edges
    would become ambiguous. The published key carries the label.
    """
    sink = _sink()
    by_id: dict[str, set[str]] = {}
    for label, node_id in sink.nodes:
        by_id.setdefault(node_id, set()).add(label)
    reused = {i: labels for i, labels in by_id.items() if len(labels) > 1}
    assert reused, "expected at least one id reused across labels in this corpus"

    write(tmp_path, sink, {"commit": "test"})
    published = json.loads((tmp_path / "nodes.json").read_text())
    keys = {n["key"] for n in published["nodes"]}
    assert len(keys) == len(sink.nodes), "no node may be lost to an id collision"
    for node_id, labels in reused.items():
        for label in labels:
            assert node_key(label, node_id) in keys


def test_dangling_edges_fail_the_build(tmp_path: Path) -> None:
    sink = CollectingSink()
    sink.node("Model", "id", "m1", {"id": "m1"})
    sink.edge("Model", "m1", "DERIVED_FROM", "Model", "ghost")
    with pytest.raises(ValueError, match="unknown nodes"):
        write(tmp_path, sink, {"commit": "test"})
