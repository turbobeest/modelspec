"""The competition rule, ported from scripts/compute_competition.py.

The rule is a claim about which models a reader should compare, so the tests
pin the rule itself rather than just the plumbing.
"""

from __future__ import annotations

import functools
import glob
import sys
from datetime import date
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.competition import compute, jaccard, params_compatible  # noqa: E402
from schema.card import ModelCard  # noqa: E402
from schema.graph import CollectingSink, derive_graph  # noqa: E402


# ── the rule's primitives ────────────────────────────────────────────────────

@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (7_000_000_000, 8_000_000_000, True),    # within 3x
        (7_000_000_000, 70_000_000_000, False),  # 10x apart
        (7_000_000_000, 21_000_000_000, True),   # exactly 3x
        (None, 70_000_000_000, True),            # unknown skips the check
        (0, 70_000_000_000, True),               # zero skips the check
        (None, None, True),
    ],
)
def test_parameter_proximity(a: object, b: object, expected: bool) -> None:
    assert params_compatible(a, b) is expected


def test_jaccard() -> None:
    assert jaccard({"a", "b"}, {"a", "b"}) == 1.0
    assert jaccard({"a"}, {"b"}) == 0.0
    assert jaccard(set(), set()) == 0.0
    assert jaccard({"a", "b"}, {"b", "c"}) == pytest.approx(1 / 3)


# ── the rule, on a graph we control ──────────────────────────────────────────

def _model(sink: CollectingSink, node_id: str, model_type: str,
           params: int | None, benches: list[str], caps: list[str]) -> None:
    sink.node("Model", "id", node_id,
              {"id": node_id, "status": "active", "model_type": model_type,
               "total_parameters": params})
    for b in benches:
        sink.edge("Model", node_id, "SCORED_ON", "Benchmark", b)
    for c in caps:
        sink.edge("Model", node_id, "HAS_CAPABILITY", "Capability", c)


def _competitors(sink: CollectingSink) -> set[frozenset[str]]:
    return {frozenset((e["from"], e["to"]))
            for e in sink.edges if e["type"] == "COMPETES_WITH"}


def test_models_of_different_types_never_compete() -> None:
    sink = CollectingSink()
    _model(sink, "a", "llm-chat", 7, ["mmlu"], ["x"])
    _model(sink, "b", "embedding", 7, ["mmlu"], ["x"])
    compute(sink, date(2026, 9, 9))
    assert _competitors(sink) == set()


def test_a_shared_benchmark_is_required() -> None:
    sink = CollectingSink()
    _model(sink, "a", "llm-chat", 7, ["mmlu"], ["x"])
    _model(sink, "b", "llm-chat", 7, ["gpqa"], ["x"])
    compute(sink, date(2026, 9, 9))
    assert _competitors(sink) == set()


def test_models_far_apart_in_size_do_not_compete() -> None:
    sink = CollectingSink()
    _model(sink, "small", "llm-chat", 7_000_000_000, ["mmlu"], ["x"])
    _model(sink, "huge", "llm-chat", 700_000_000_000, ["mmlu"], ["x"])
    compute(sink, date(2026, 9, 9))
    assert _competitors(sink) == set()


def test_a_qualifying_pair_competes() -> None:
    sink = CollectingSink()
    _model(sink, "a", "llm-chat", 7_000_000_000, ["mmlu"], ["x", "y"])
    _model(sink, "b", "llm-chat", 8_000_000_000, ["mmlu"], ["x", "y"])
    compute(sink, date(2026, 9, 9))
    assert _competitors(sink) == {frozenset(("a", "b"))}


def test_inactive_models_are_excluded() -> None:
    sink = CollectingSink()
    _model(sink, "a", "llm-chat", 7, ["mmlu"], ["x"])
    _model(sink, "b", "llm-chat", 7, ["mmlu"], ["x"])
    sink.nodes[("Model", "b")]["status"] = "deprecated"
    compute(sink, date(2026, 9, 9))
    assert _competitors(sink) == set()


def test_one_edge_per_pair_not_two() -> None:
    """The script MERGEs both directions; a drawn graph would double every line."""
    sink = CollectingSink()
    _model(sink, "a", "llm-chat", 7, ["mmlu"], ["x"])
    _model(sink, "b", "llm-chat", 7, ["mmlu"], ["x"])
    compute(sink, date(2026, 9, 9))
    assert len([e for e in sink.edges if e["type"] == "COMPETES_WITH"]) == 1


def test_edges_carry_the_build_date_not_a_constant() -> None:
    """The script hardcoded COMPUTED_DATE, which went five months stale."""
    sink = CollectingSink()
    _model(sink, "a", "llm-chat", 7, ["mmlu"], ["x"])
    _model(sink, "b", "llm-chat", 7, ["mmlu"], ["x"])
    compute(sink, date(2026, 9, 9))
    edge = next(e for e in sink.edges if e["type"] == "COMPETES_WITH")
    assert edge["props"]["computed_date"] == "2026-09-09"
    assert edge["props"]["basis"] == "unverified-legacy"


def test_top_n_keeps_a_pair_either_endpoint_ranks() -> None:
    """A small model must not be erased by a popular one's crowded neighbourhood."""
    sink = CollectingSink()
    # `lonely` has exactly one possible competitor; `hub` has many better ones.
    _model(sink, "lonely", "llm-chat", 7, ["mmlu"], ["z"])
    _model(sink, "hub", "llm-chat", 7, ["mmlu"], ["a", "b", "c"])
    for i in range(6):
        _model(sink, f"near{i}", "llm-chat", 7, ["mmlu"], ["a", "b", "c"])
    compute(sink, date(2026, 9, 9), top_n=2)
    pairs = _competitors(sink)
    assert frozenset(("lonely", "hub")) in pairs, "lonely's only competitor was dropped"


# ── against the real corpus ──────────────────────────────────────────────────

@functools.lru_cache(maxsize=1)
def _real() -> tuple[CollectingSink, dict]:
    files = [f for f in sorted(glob.glob(str(REPO_ROOT / "models/**/*.md"), recursive=True))
             if not f.endswith("LICENSE.md")]
    sink = derive_graph([ModelCard.from_yaml_file(f) for f in files])
    stats = compute(sink, date(2026, 9, 9))
    return sink, stats


def test_the_real_corpus_produces_a_legible_view() -> None:
    from pipeline.graph import LEGIBLE_EDGE_LIMIT
    _, stats = _real()
    assert stats["edges"] > 0, "the competition view must no longer be empty"
    assert stats["edges"] <= LEGIBLE_EDGE_LIMIT, (
        f"{stats['edges']} edges exceeds the legibility limit; lower top_n"
    )


def test_trimming_actually_trims() -> None:
    _, stats = _real()
    assert stats["edges"] < stats["qualifying_pairs"]
