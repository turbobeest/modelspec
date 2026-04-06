#!/usr/bin/env python3
"""Compute COMPETES_WITH derived edges in the ModelSpec FalkorDB graph.

Two models compete if:
  - Same model_type (primary type)
  - Parameter count within 3x of each other (if both have params)
  - At least 1 shared benchmark (SCORED_ON the same Benchmark node)
  - Both status = 'active'

When both models lack parameter data, parameter proximity is assumed (skip check).

Edge properties:
  dimension:      "overall"
  overlap_score:  Jaccard similarity of capability sets (0–1)
  computed_date:  today's date

Usage:
    source .venv/bin/activate && python scripts/compute_competition.py
"""

from __future__ import annotations

import sys
import time
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from falkordb import FalkorDB

# ── Configuration ────────────────────────────────────────────────
FALKORDB_HOST = "localhost"
FALKORDB_PORT = 6382
GRAPH_NAME = "modelspec"
COMPUTED_DATE = "2026-04-05"
PARAM_RATIO = 3.0  # within 3x
BATCH_SIZE = 500  # edges per MERGE batch


def params_compatible(p1: int | None, p2: int | None) -> bool:
    """Check if two parameter counts are within 3x of each other.

    If either is None, we skip the check (return True).
    """
    if p1 is None or p2 is None:
        return True
    if p1 == 0 or p2 == 0:
        return True
    ratio = max(p1, p2) / min(p1, p2)
    return ratio <= PARAM_RATIO


def jaccard(set_a: set, set_b: set) -> float:
    """Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 0.0
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)


def main() -> None:
    t0 = time.monotonic()

    # ── 1. Connect ───────────────────────────────────────────────
    print(f"Connecting to FalkorDB at {FALKORDB_HOST}:{FALKORDB_PORT} ...")
    db = FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT)
    graph = db.select_graph(GRAPH_NAME)
    print(f"Connected. Graph: {GRAPH_NAME}")

    # ── 2. Load active models with model_type and params ─────────
    print("\nLoading active models ...")
    result = graph.query(
        "MATCH (m:Model {status: 'active'}) "
        "RETURN m.id, m.model_type, m.total_parameters"
    )
    models = {}  # id -> {model_type, total_parameters}
    type_groups: dict[str, list[str]] = defaultdict(list)

    for row in result.result_set:
        mid, mtype, params = row
        if not mid or not mtype:
            continue
        models[mid] = {"model_type": mtype, "total_parameters": params}
        type_groups[mtype].append(mid)

    print(f"  Loaded {len(models)} active models across {len(type_groups)} model types")

    # Skip types with only 1 model
    candidate_types = {t: ids for t, ids in type_groups.items() if len(ids) > 1}
    skipped = len(type_groups) - len(candidate_types)
    print(f"  Candidate types: {len(candidate_types)} (skipped {skipped} singleton types)")

    for mtype, ids in sorted(candidate_types.items(), key=lambda x: -len(x[1])):
        print(f"    {mtype}: {len(ids)} models")

    # ── 3. Load benchmark sets per model (for shared-benchmark check) ──
    print("\nLoading benchmark sets (SCORED_ON) ...")
    result = graph.query(
        "MATCH (m:Model {status: 'active'})-[:SCORED_ON]->(b:Benchmark) "
        "RETURN m.id, collect(DISTINCT b.id)"
    )
    benchmarks_by_model: dict[str, set[str]] = {}
    for row in result.result_set:
        mid, bench_ids = row
        if mid:
            benchmarks_by_model[mid] = set(bench_ids) if bench_ids else set()

    models_with_benchmarks = len(benchmarks_by_model)
    print(f"  {models_with_benchmarks} models have benchmark data")

    # ── 4. Load capability sets per model (for Jaccard overlap) ──
    print("Loading capability sets (HAS_CAPABILITY) ...")
    result = graph.query(
        "MATCH (m:Model {status: 'active'})-[:HAS_CAPABILITY]->(c:Capability) "
        "RETURN m.id, collect(DISTINCT c.id)"
    )
    capabilities_by_model: dict[str, set[str]] = {}
    for row in result.result_set:
        mid, cap_ids = row
        if mid:
            capabilities_by_model[mid] = set(cap_ids) if cap_ids else set()

    models_with_caps = len(capabilities_by_model)
    print(f"  {models_with_caps} models have capability data")

    # ── 5. Compute competing pairs ───────────────────────────────
    print("\nComputing competition edges ...")
    edges_to_create: list[tuple[str, str, float]] = []  # (id_a, id_b, overlap_score)

    total_pairs_checked = 0
    total_pairs_param_skip = 0
    total_pairs_bench_skip = 0

    for mtype, model_ids in candidate_types.items():
        n = len(model_ids)
        type_edge_count = 0

        for i in range(n):
            for j in range(i + 1, n):
                id_a = model_ids[i]
                id_b = model_ids[j]
                total_pairs_checked += 1

                # Check parameter proximity
                p_a = models[id_a]["total_parameters"]
                p_b = models[id_b]["total_parameters"]
                if not params_compatible(p_a, p_b):
                    total_pairs_param_skip += 1
                    continue

                # Check shared benchmarks (at least 1)
                bench_a = benchmarks_by_model.get(id_a, set())
                bench_b = benchmarks_by_model.get(id_b, set())
                shared = bench_a & bench_b
                if len(shared) < 1:
                    total_pairs_bench_skip += 1
                    continue

                # Compute capability Jaccard
                caps_a = capabilities_by_model.get(id_a, set())
                caps_b = capabilities_by_model.get(id_b, set())
                overlap = jaccard(caps_a, caps_b)

                edges_to_create.append((id_a, id_b, overlap))
                type_edge_count += 1

        if type_edge_count > 0:
            print(f"  {mtype}: {type_edge_count} competition edges (from {n} models, {n*(n-1)//2} pairs)")

    print(f"\n  Total pairs checked:     {total_pairs_checked}")
    print(f"  Skipped (param mismatch):{total_pairs_param_skip}")
    print(f"  Skipped (no shared bench):{total_pairs_bench_skip}")
    print(f"  Competition edges found: {len(edges_to_create)}")

    if not edges_to_create:
        print("\nNo competition edges to create. Done.")
        return

    # ── 6. Batch-write COMPETES_WITH edges via MERGE ─────────────
    print(f"\nWriting {len(edges_to_create)} COMPETES_WITH edges (batch size {BATCH_SIZE}) ...")

    # Create edges in both directions (undirected competition)
    edges_written = 0
    for batch_start in range(0, len(edges_to_create), BATCH_SIZE):
        batch = edges_to_create[batch_start : batch_start + BATCH_SIZE]

        # Build the UNWIND parameter list
        edge_params = []
        for id_a, id_b, overlap in batch:
            edge_params.append({
                "a": id_a,
                "b": id_b,
                "overlap": round(overlap, 4),
            })

        # MERGE in one direction (a -> b), then the reverse (b -> a)
        # Using UNWIND for batch efficiency
        query = (
            "UNWIND $edges AS e "
            "MATCH (a:Model {id: e.a}), (b:Model {id: e.b}) "
            "MERGE (a)-[r1:COMPETES_WITH {dimension: 'overall'}]->(b) "
            "SET r1.overlap_score = e.overlap, r1.computed_date = $date "
            "MERGE (b)-[r2:COMPETES_WITH {dimension: 'overall'}]->(a) "
            "SET r2.overlap_score = e.overlap, r2.computed_date = $date"
        )

        graph.query(query, {"edges": edge_params, "date": COMPUTED_DATE})
        edges_written += len(batch)

        if edges_written % 1000 < BATCH_SIZE or edges_written >= len(edges_to_create):
            print(f"  Written {edges_written}/{len(edges_to_create)} pairs ({edges_written * 2} directed edges)")

    # ── 7. Verification ──────────────────────────────────────────
    print("\nVerification ...")
    result = graph.query("MATCH ()-[r:COMPETES_WITH]->() RETURN count(r)")
    total_cw = result.result_set[0][0]
    print(f"  COMPETES_WITH edges in graph: {total_cw}")

    result = graph.query(
        "MATCH (m:Model)-[r:COMPETES_WITH]->() "
        "RETURN m.model_type, count(r) AS c ORDER BY c DESC"
    )
    print("\n  Edges by model_type:")
    for row in result.result_set:
        print(f"    {row[0]}: {row[1]}")

    result = graph.query(
        "MATCH (m:Model)-[r:COMPETES_WITH]->() "
        "WITH m, count(r) AS competitors "
        "RETURN m.display_name, m.model_type, competitors "
        "ORDER BY competitors DESC LIMIT 10"
    )
    print("\n  Most competitive models (top 10):")
    for row in result.result_set:
        name = row[0] or "(unnamed)"
        mtype = row[1] or "—"
        print(f"    {name:<45s} {mtype:<16s} {row[2]:>4} competitors")

    # Overlap score distribution
    result = graph.query(
        "MATCH ()-[r:COMPETES_WITH]->() "
        "RETURN "
        "  min(r.overlap_score), "
        "  max(r.overlap_score), "
        "  avg(r.overlap_score)"
    )
    row = result.result_set[0]
    print(f"\n  Overlap score: min={row[0]:.4f}, max={row[1]:.4f}, avg={row[2]:.4f}")

    elapsed = time.monotonic() - t0
    print(f"\nDone in {elapsed:.1f}s. Created {total_cw} COMPETES_WITH edges.")


if __name__ == "__main__":
    main()
