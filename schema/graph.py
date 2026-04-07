"""FalkorDB graph schema — node types, edge types, and Cypher operations.

This module defines the complete ontology and provides functions to:
  - Create indexes
  - Ingest a ModelCard into the graph as nodes + edges
  - Run common traversal queries
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


# ═══════════════════════════════════════════════════════════════
# Edge type registry
# ═══════════════════════════════════════════════════════════════

class EdgeType(str, Enum):
    """All relationship types in the graph."""
    # Factual (directly observed)
    MADE_BY = "MADE_BY"
    DERIVED_FROM = "DERIVED_FROM"
    MERGED_FROM = "MERGED_FROM"
    LICENSED_AS = "LICENSED_AS"
    HAS_CAPABILITY = "HAS_CAPABILITY"
    SCORED_ON = "SCORED_ON"
    FITS_ON = "FITS_ON"
    AVAILABLE_AS = "AVAILABLE_AS"
    RUNS_ON = "RUNS_ON"
    AVAILABLE_ON = "AVAILABLE_ON"
    TAGGED_WITH = "TAGGED_WITH"
    SUITED_FOR = "SUITED_FOR"
    PUBLISHED_BY = "PUBLISHED_BY"
    SUPPORTS_RUNTIME = "SUPPORTS_RUNTIME"
    TESTS_CAPABILITY = "TESTS_CAPABILITY"
    REQUIRED_BY = "REQUIRED_BY"

    # Derived (computed by ranking engine)
    COMPETES_WITH = "COMPETES_WITH"
    OUTPERFORMS = "OUTPERFORMS"
    SIMILAR_TO = "SIMILAR_TO"
    UPGRADE_PATH = "UPGRADE_PATH"
    BEST_FOR = "BEST_FOR"
    PARETO_OPTIMAL = "PARETO_OPTIMAL"

    # Institutional (organization-specific overlay)
    APPROVED_BY = "APPROVED_BY"
    EXCLUDED_BY = "EXCLUDED_BY"
    REVIEWED_BY = "REVIEWED_BY"
    PREFERRED_BY = "PREFERRED_BY"


# ═══════════════════════════════════════════════════════════════
# Index definitions
# ═══════════════════════════════════════════════════════════════

INDEXES = [
    "CREATE INDEX ON :Model(id)",
    "CREATE INDEX ON :Model(model_type)",
    "CREATE INDEX ON :Model(status)",
    "CREATE INDEX ON :Model(origin_country)",
    "CREATE INDEX ON :Model(open_weights)",
    "CREATE INDEX ON :Model(total_parameters)",
    "CREATE INDEX ON :Model(arena_elo_overall)",
    "CREATE INDEX ON :Model(cost_input)",
    "CREATE INDEX ON :Model(context_window)",
    "CREATE INDEX ON :Model(release_date)",
    "CREATE INDEX ON :Provider(id)",
    "CREATE INDEX ON :Platform(id)",
    "CREATE INDEX ON :Platform(category)",
    "CREATE INDEX ON :Capability(id)",
    "CREATE INDEX ON :Capability(category)",
    "CREATE INDEX ON :Hardware(id)",
    "CREATE INDEX ON :Hardware(memory_gb)",
    "CREATE INDEX ON :Benchmark(id)",
    "CREATE INDEX ON :Benchmark(category)",
    "CREATE INDEX ON :License(id)",
    "CREATE INDEX ON :UseCase(id)",
    "CREATE INDEX ON :DownselectProfile(id)",
    "CREATE INDEX ON :Runtime(id)",
    "CREATE INDEX ON :Quantization(id)",
    "CREATE INDEX ON :Tag(id)",
]


def create_indexes(graph) -> None:
    """Create all indexes on a FalkorDB graph instance."""
    for idx in INDEXES:
        try:
            graph.query(idx)
        except Exception:
            pass  # Index may already exist


# ═══════════════════════════════════════════════════════════════
# Ingestion: ModelCard → Graph nodes + edges
# ═══════════════════════════════════════════════════════════════

def ingest_model_card(graph, card) -> dict[str, int]:
    """Ingest a ModelCard into FalkorDB, creating/merging all nodes and edges.
    
    Returns a dict with counts: {"nodes_created": N, "edges_created": M}
    """
    from .card import ModelCard

    stats = {"nodes_created": 0, "edges_created": 0}
    ident = card.identity
    arch = card.architecture
    lic = card.licensing

    # ── 1. Upsert the :Model node ──────────────────────────
    model_props = {
        "id": ident.model_id,
        "display_name": ident.display_name,
        "model_type": ident.model_type.value if ident.model_type else None,
        "status": ident.status.value,
        "release_date": ident.release_date,
        "family": ident.family,
        "origin_country": lic.origin_country,
        "open_weights": lic.open_weights,
        "total_parameters": arch.total_parameters,
        "active_parameters": arch.active_parameters,
        "architecture_type": arch.type.value if arch.type else None,
        "context_window": card.modalities.text.context_window,
        "max_input": card.modalities.text.max_input_tokens,
        "max_output": card.modalities.text.max_output_tokens,
        "cost_input": card.cost.input,
        "cost_output": card.cost.output,
        "arena_elo_overall": card.benchmarks.scores.get("arena_elo_overall"),
        "custom_score": card.downselect.custom_score,
        "card_completeness": card.card_completeness,
        "embedding_dimensions": arch.embedding_dimensions,
        "reasoning": card.capabilities.reasoning.chain_of_thought,
        "tool_call": card.capabilities.tool_use.function_calling,
        "vision_input": card.modalities.vision.supported,
        "multilingual": card.capabilities.language.multilingual,
        "model_subtypes": ",".join(st.value for st in ident.model_subtypes) if ident.model_subtypes else None,
    }

    # Filter out None values for cleaner Cypher
    props = {k: v for k, v in model_props.items() if v is not None}
    _merge_node(graph, "Model", "id", ident.model_id, props)
    stats["nodes_created"] += 1

    # ── 2. Upsert :Provider and :MADE_BY ───────────────────
    if ident.provider:
        _merge_node(graph, "Provider", "id", ident.provider, {
            "id": ident.provider,
            "display_name": ident.provider_display or ident.provider,
            "country": lic.origin_country,
        })
        _merge_edge(graph, "Model", ident.model_id, "MADE_BY", "Provider", ident.provider)
        stats["nodes_created"] += 1
        stats["edges_created"] += 1

    # ── 3. Upsert :License and :LICENSED_AS ────────────────
    if lic.license_type:
        license_id = lic.license_type.value
        _merge_node(graph, "License", "id", license_id, {
            "id": license_id,
            "name": license_id,
            "commercial_ok": lic.commercial_use,
            "defense_ok": lic.defense_use.value,
            "government_ok": lic.government_use.value,
        })
        _merge_edge(graph, "Model", ident.model_id, "LICENSED_AS", "License", license_id)
        stats["edges_created"] += 1

    # ── 4. Upsert :DERIVED_FROM (lineage) ──────────────────
    if card.lineage.base_model:
        _merge_node(graph, "Model", "id", card.lineage.base_model, {
            "id": card.lineage.base_model,
        })
        edge_props = {}
        if card.lineage.base_model_relation:
            edge_props["relation"] = card.lineage.base_model_relation.value
        _merge_edge(graph, "Model", ident.model_id, "DERIVED_FROM",
                     "Model", card.lineage.base_model, edge_props)
        stats["edges_created"] += 1

    # ── 5. Capabilities → :HAS_CAPABILITY edges ───────────
    cap_map = _extract_capabilities(card.capabilities)
    for cap_id, tier in cap_map.items():
        category = cap_id.split(":")[0] if ":" in cap_id else "general"
        _merge_node(graph, "Capability", "id", cap_id, {
            "id": cap_id,
            "category": category,
            "name": cap_id.split(":")[-1].replace("_", " ").title(),
        })
        _merge_edge(graph, "Model", ident.model_id, "HAS_CAPABILITY",
                     "Capability", cap_id, {"tier": tier})
        stats["edges_created"] += 1

    # ── 6. Benchmarks → :SCORED_ON edges ───────────────────
    for bench_id, value in card.benchmarks.scores.items():
        if isinstance(value, (int, float)):
            _merge_node(graph, "Benchmark", "id", bench_id, {
                "id": bench_id,
                "name": bench_id.replace("_", " ").title(),
            })
            _merge_edge(graph, "Model", ident.model_id, "SCORED_ON",
                         "Benchmark", bench_id, {
                             "value": float(value),
                             "date": card.benchmarks.benchmark_as_of,
                         })
            stats["edges_created"] += 1

    # ── 7. Hardware profiles → :FITS_ON edges ──────────────
    for hw_id, profile in card.deployment.hardware_profiles.items():
        if profile.fits:
            _merge_node(graph, "Hardware", "id", hw_id, {"id": hw_id, "display_name": hw_id})
            edge_props = {k: v for k, v in {
                "quantization": profile.best_quant,
                "vram_usage_gb": profile.vram_usage_gb or profile.ram_usage_gb,
                "tokens_per_sec": profile.tokens_per_sec,
                "ttft_ms": profile.ttft_ms,
                "max_context_tokens": profile.max_context_at_quant,
                "inference_engine": profile.inference_engine,
            }.items() if v}
            _merge_edge(graph, "Model", ident.model_id, "FITS_ON",
                         "Hardware", hw_id, edge_props)
            stats["edges_created"] += 1

    # ── 8. Platform availability → :AVAILABLE_ON edges ─────
    for field_name, field_value in card.availability:
        if isinstance(field_value, PlatformEntry_type()) and field_value.available:
            platform_id = field_name
            _merge_node(graph, "Platform", "id", platform_id, {
                "id": platform_id,
                "display_name": field_name.replace("_", " ").title(),
                "url": field_value.url,
            })
            edge_props = {k: v for k, v in {
                "model_id_on_platform": field_value.model_id,
                "fine_tuning": field_value.fine_tuning,
                "gated": field_value.gated,
                "notes": field_value.notes,
            }.items() if v}
            _merge_edge(graph, "Model", ident.model_id, "AVAILABLE_ON",
                         "Platform", platform_id, edge_props)
            stats["edges_created"] += 1

    # ── 9. Tags → :TAGGED_WITH edges ──────────────────────
    for tag in ident.tags:
        _merge_node(graph, "Tag", "id", tag, {"id": tag})
        _merge_edge(graph, "Model", ident.model_id, "TAGGED_WITH", "Tag", tag)
        stats["edges_created"] += 1

    return stats


def PlatformEntry_type():
    """Lazy import to avoid circular dependency."""
    from .card import PlatformEntry
    return PlatformEntry


# ═══════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════

def _merge_node(graph, label: str, key_field: str, key_value: str, props: dict[str, Any]) -> None:
    """MERGE a node by its key field, setting properties."""
    extra_props = {k: v for k, v in props.items() if k != key_field}
    if extra_props:
        prop_str = ", ".join(f"n.{k} = ${k}" for k in extra_props)
        query = f"MERGE (n:{label} {{{key_field}: ${key_field}}}) SET {prop_str}"
    else:
        query = f"MERGE (n:{label} {{{key_field}: ${key_field}}})"
    graph.query(query, props)


def _merge_edge(graph, from_label: str, from_id: str, edge_type: str,
                to_label: str, to_id: str, props: dict[str, Any] | None = None) -> None:
    """MERGE an edge between two nodes identified by their id fields."""
    if props:
        prop_str = " {" + ", ".join(f"{k}: ${k}" for k in props) + "}"
    else:
        prop_str = ""
    params = {"from_id": from_id, "to_id": to_id, **(props or {})}
    query = (
        f"MATCH (a:{from_label} {{id: $from_id}}) "
        f"MATCH (b:{to_label} {{id: $to_id}}) "
        f"MERGE (a)-[:{edge_type}{prop_str}]->(b)"
    )
    graph.query(query, params)


def _extract_capabilities(caps) -> dict[str, str]:
    """Extract capability IDs and tiers from the Capabilities model."""
    result = {}

    def _process_section(prefix: str, section):
        for field_name, _ in section:
            value = getattr(section, field_name)
            if field_name == "overall" and value:
                result[prefix] = value.value if hasattr(value, "value") else str(value)
            elif isinstance(value, bool) and value:
                cap_id = f"{prefix}:{field_name}"
                # Boolean capabilities get tier from their section's overall
                overall = getattr(section, "overall", None)
                tier = overall.value if overall and hasattr(overall, "value") else "tier-2"
                result[cap_id] = tier

    _process_section("coding", caps.coding)
    _process_section("reasoning", caps.reasoning)
    _process_section("tool_use", caps.tool_use)
    _process_section("language", caps.language)
    _process_section("creative", caps.creative)
    _process_section("safety", caps.safety_alignment)
    _process_section("domain", caps.domain_specific)
    _process_section("agent", caps.agent_capabilities)

    return result
