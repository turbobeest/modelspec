"""Derive COMPETES_WITH edges from the graph, with no database.

The rule is `scripts/compute_competition.py`'s, ported unchanged so the two can
be compared:

    Two active models compete if they share a model_type, their parameter counts
    are within 3x (skipped when either is unknown or zero), and they report at
    least one benchmark in common. The edge carries the Jaccard similarity of
    their capability sets.

Two deliberate differences from the script, both recorded rather than silent:

* One edge per unordered pair. The script MERGEs both directions because an
  undirected relationship has to be traversable both ways in Cypher; a rendered
  graph would just draw every line twice.
* The derivation date is the build date, not a constant. The script hardcodes
  COMPUTED_DATE = "2026-04-05", which was five months stale by the time this was
  written — a derived edge that cannot say when it was derived is exactly the
  kind of undated claim this project removes everywhere else.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from itertools import combinations
from typing import Any

from schema.graph import CollectingSink

PARAM_RATIO = 3.0

#: Competition is quadratic in the size of a model_type group: 145,619 pairs
#: qualify 12,561 edges across the current corpus, which is three times what a
#: force layout can show legibly.
#:
#: A similarity threshold is the wrong instrument — the capability sets are
#: coarse, so even 0.7 only trims to 8,088. Keeping each model's closest N is
#: both smaller and a better claim: "the models most like this one" is what a
#: reader wants, where "every model within 3x that shares any benchmark" is
#: merely true.
#:
#: At 6 the view is 2,652 edges and renders whole; at 8 it is 3,410 and the
#: client has to sample it.
TOP_N_PER_MODEL = 6


def params_compatible(p1: Any, p2: Any) -> bool:
    """Unknown or zero parameter counts skip the check, as in the original."""
    if p1 is None or p2 is None or p1 == 0 or p2 == 0:
        return True
    return max(p1, p2) / min(p1, p2) <= PARAM_RATIO


def jaccard(a: set[str], b: set[str]) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def compute(sink: CollectingSink, as_of: date, top_n: int = TOP_N_PER_MODEL) -> dict[str, Any]:
    """Append COMPETES_WITH edges to the sink. Returns counts for the summary."""
    models = {
        node_id: props
        for (label, node_id), props in sink.nodes.items()
        if label == "Model" and props.get("status") == "active" and props.get("model_type")
    }

    benchmarks: dict[str, set[str]] = defaultdict(set)
    capabilities: dict[str, set[str]] = defaultdict(set)
    for edge in sink.edges:
        if edge["type"] == "SCORED_ON":
            benchmarks[edge["from"]].add(edge["to"])
        elif edge["type"] == "HAS_CAPABILITY":
            capabilities[edge["from"]].add(edge["to"])

    groups: dict[str, list[str]] = defaultdict(list)
    for node_id, props in models.items():
        groups[str(props["model_type"])].append(node_id)

    checked = skipped_params = skipped_bench = 0
    qualifying: list[tuple[str, str, float]] = []

    for member_ids in groups.values():
        if len(member_ids) < 2:
            continue
        for a, b in combinations(sorted(member_ids), 2):
            checked += 1
            if not params_compatible(models[a].get("total_parameters"),
                                     models[b].get("total_parameters")):
                skipped_params += 1
                continue
            if not (benchmarks[a] & benchmarks[b]):
                skipped_bench += 1
                continue
            qualifying.append((a, b, jaccard(capabilities[a], capabilities[b])))

    # Keep each model's closest competitors. An edge survives if either endpoint
    # ranks it in its own top N, so a small model is not erased from the graph
    # by a popular one's crowded neighbourhood.
    ranked: dict[str, list[tuple[str, str, float]]] = defaultdict(list)
    for pair in qualifying:
        ranked[pair[0]].append(pair)
        ranked[pair[1]].append(pair)
    kept: set[tuple[str, str, float]] = set()
    for pairs in ranked.values():
        pairs.sort(key=lambda p: -p[2])
        kept.update(pairs[:top_n])
    found = sorted(kept, key=lambda p: (p[0], p[1]))

    for a, b, overlap in found:
        sink.edge("Model", a, "COMPETES_WITH", "Model", b, {
            "dimension": "overall",
            "overlap_score": round(overlap, 4),
            "computed_date": as_of.isoformat(),
            # The shared-benchmark test rests entirely on card scores, which
            # carry one date per card and no per-score attribution.
            "basis": "unverified-legacy",
        })

    return {
        "pairs_checked": checked,
        "skipped_params": skipped_params,
        "skipped_no_shared_benchmark": skipped_bench,
        "qualifying_pairs": len(qualifying),
        "edges": len(found),
        "top_n_per_model": top_n,
    }
