#!/usr/bin/env python3
"""Ingest all ModelSpec model cards into FalkorDB.

Scans models/ for YAML frontmatter files, parses each into a ModelCard,
and ingests nodes + edges into the 'modelspec' graph on FalkorDB.

Usage:
    source .venv/bin/activate && python scripts/ingest_all.py

The script is idempotent — MERGE operations allow safe re-runs.
"""

from __future__ import annotations

import glob
import sys
import time
from pathlib import Path

# Ensure the project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from falkordb import FalkorDB

from schema.card import ModelCard
from schema.graph import create_indexes, ingest_model_card

# ── Configuration ──────────────────────────────────────────────
FALKORDB_HOST = "localhost"
FALKORDB_PORT = 6382
GRAPH_NAME = "modelspec"
MODELS_DIR = PROJECT_ROOT / "models"
PROGRESS_INTERVAL = 10


def main() -> None:
    # ── 1. Connect to FalkorDB ─────────────────────────────────
    print(f"Connecting to FalkorDB at {FALKORDB_HOST}:{FALKORDB_PORT} ...")
    db = FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT)
    graph = db.select_graph(GRAPH_NAME)
    print(f"Connected. Graph: {GRAPH_NAME}")

    # ── 2. Create indexes ──────────────────────────────────────
    print("Creating indexes ...")
    create_indexes(graph)
    print("Indexes ready.")

    # ── 3. Discover model card files ───────────────────────────
    files = sorted(glob.glob(str(MODELS_DIR / "**" / "*.md"), recursive=True))
    total = len(files)
    print(f"Found {total} model card files in {MODELS_DIR}")

    if total == 0:
        print("Nothing to ingest. Exiting.")
        return

    # ── 4. Ingest each card ────────────────────────────────────
    success_count = 0
    fail_count = 0
    total_nodes = 0
    total_edges = 0
    failures: list[tuple[str, str]] = []

    t0 = time.monotonic()

    for i, filepath in enumerate(files, start=1):
        try:
            card = ModelCard.from_yaml_file(filepath)
            stats = ingest_model_card(graph, card)
            total_nodes += stats["nodes_created"]
            total_edges += stats["edges_created"]
            success_count += 1
        except Exception as exc:
            fail_count += 1
            failures.append((filepath, f"{type(exc).__name__}: {exc}"))

        if i % PROGRESS_INTERVAL == 0 or i == total:
            elapsed = time.monotonic() - t0
            rate = i / elapsed if elapsed > 0 else 0
            print(f"  [{i:>4}/{total}] {success_count} ok, {fail_count} failed  ({rate:.1f} cards/sec)")

    elapsed = time.monotonic() - t0
    print(f"\nIngestion complete in {elapsed:.1f}s")
    print(f"  Success: {success_count}")
    print(f"  Failed:  {fail_count}")
    print(f"  Nodes merged: {total_nodes}")
    print(f"  Edges merged: {total_edges}")

    if failures:
        print(f"\n{'='*60}")
        print("FAILURES:")
        for path, err in failures:
            print(f"  {path}")
            print(f"    {err}")
        print(f"{'='*60}")

    # ── 5. Verification queries ────────────────────────────────
    print(f"\n{'='*60}")
    print("VERIFICATION QUERIES")
    print(f"{'='*60}")

    # Count nodes by type
    print("\n-- Nodes by label --")
    result = graph.query(
        "MATCH (n) RETURN labels(n)[0] AS type, count(n) AS count ORDER BY count DESC"
    )
    total_node_count = 0
    for row in result.result_set:
        label, count = row
        total_node_count += count
        print(f"  {label:<20s} {count:>6}")
    print(f"  {'TOTAL':<20s} {total_node_count:>6}")

    # Count edges by type
    print("\n-- Edges by type --")
    result = graph.query(
        "MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count ORDER BY count DESC"
    )
    total_edge_count = 0
    for row in result.result_set:
        rel_type, count = row
        total_edge_count += count
        print(f"  {rel_type:<20s} {count:>6}")
    print(f"  {'TOTAL':<20s} {total_edge_count:>6}")

    # Most connected models
    print("\n-- Most connected models (top 10) --")
    result = graph.query(
        "MATCH (m:Model) "
        "RETURN m.display_name, m.model_type, size((m)--()) AS connections "
        "ORDER BY connections DESC LIMIT 10"
    )
    for row in result.result_set:
        name, mtype, conns = row
        name_str = name or "(unnamed)"
        mtype_str = mtype or "—"
        print(f"  {name_str:<40s} {mtype_str:<16s} {conns:>4} connections")

    # Provider landscape
    print("\n-- Provider landscape --")
    result = graph.query(
        "MATCH (p:Provider)<-[:MADE_BY]-(m:Model) "
        "RETURN p.display_name, count(m) AS models ORDER BY models DESC"
    )
    for row in result.result_set:
        provider, model_count = row
        print(f"  {provider:<30s} {model_count:>4} models")

    # ── 6. Final summary ───────────────────────────────────────
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"  Graph:       {GRAPH_NAME}")
    print(f"  Total nodes: {total_node_count}")
    print(f"  Total edges: {total_edge_count}")
    print(f"  Cards:       {success_count} ingested, {fail_count} failed (of {total})")
    print(f"  Time:        {elapsed:.1f}s")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
