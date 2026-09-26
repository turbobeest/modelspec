"""$ per task, computed from the spec's token counts (MODEL-153, contract 1.3).

The design's central unit is the cost of one task. A spec says how many input
and output tokens a task takes (`task_tokens`); the engine computes
`offering.cost_per_task` = (price.input × input + price.output × output) / 1e6
for each offering, and nothing else. Either price unknown makes it unknown.
"""

from __future__ import annotations

from datetime import date

import pytest

from decision.contract import (
    DEFAULT_TASK_TOKENS,
    Decision,
    SpecError,
    canonical_json,
    parse_spec,
    spec_hash,
)
from decision.engine import decide
from decision.explain import render_html
from decision.registry import default as registry
from decision.registry import facet as facets
from decision.snapshot import SnapshotBuildError, SnapshotInputs, build_snapshot, load_snapshot_bytes
from tests.snapshot_records import SOURCES, evidence, fact, model, offering

AS_OF = date(2026, 9, 24)
BENCH = "swe_bench_verified"
DOMAINS = {BENCH: [("software_engineering", "direct")]}


def generator(mid: str):
    return model(mid, facts=[
        fact("model", mid, "model.class", "text-generator"),
        fact("model", mid, "model.lifecycle", "active"),
    ])


def sold(mid: str, provider: str, price_in: float | None, price_out: float | None):
    oid = f"{provider}/{mid}/global/standard"
    facts = []
    if price_in is not None:
        facts.append(fact("offering", oid, "offering.price.input", price_in, source="src-pricing"))
    if price_out is not None:
        facts.append(fact("offering", oid, "offering.price.output", price_out, source="src-pricing"))
    return offering(mid, provider, facts=facts)


def oid(provider: str, mid: str) -> str:
    return f"{provider}/{mid}/global/standard"


def index(offerings=None):
    inputs = SnapshotInputs(
        models=[generator("lab/cheap"), generator("lab/dear"), generator("lab/half")],
        offerings=offerings if offerings is not None else [
            sold("lab/cheap", "p1", 1.0, 5.0),
            sold("lab/dear", "p1", 2.0, 10.0),
            sold("lab/half", "p1", 1.0, None),
        ],
        evidence=[evidence("lab/cheap", BENCH, 60.0), evidence("lab/dear", BENCH, 70.0)],
        sources=SOURCES,
        benchmark_domains=DOMAINS,
    )
    built = build_snapshot(inputs, gate=False, as_of=AS_OF)
    return load_snapshot_bytes(built.to_bytes(key=None), key=None, include_archive=True)


def spec(where=(), objective=None, explain="none", tokens=None):
    raw = {
        "spec_version": 1,
        "where": ["model.class = text-generator", *where],
        "optimize": objective or {"min": "offering.cost_per_task"},
        "explain": explain,
    }
    if tokens is not None:
        raw["task_tokens"] = tokens
    return parse_spec(raw, facets=facets)


def offerings_only(results):
    return [r for r in results if r.offering.provider is not None]


# ── the registry and the contract ──────────────────────────────────────────


def test_cost_per_task_is_a_computed_offering_facet_in_usd_per_task():
    facet = registry().facet("offering.cost_per_task")
    assert facet.subject == "offering"
    assert facet.value_type.kind == "number"
    assert facet.unit == "usd_per_task"
    assert facet.computed_by == "MODEL-153"
    assert registry().unit("usd_per_task").definition


def test_the_spec_takes_task_tokens_and_refuses_nonsense():
    parsed = spec(tokens={"input": 60000, "output": 6000})
    assert parsed.task_tokens.input == 60000 and parsed.task_tokens.output == 6000
    for bad in ({"input": -1, "output": 10}, {"input": 10}, {"input": 1, "output": 1, "cached": 2}):
        with pytest.raises(SpecError) as caught:
            spec(tokens=bad)
        assert all(issue.path.startswith("task_tokens") for issue in caught.value.issues)


def test_an_absent_task_tokens_keeps_the_12_hash_and_defaults_are_documented():
    without = spec()
    assert "task_tokens" not in canonical_json(without)
    assert spec_hash(without) != spec_hash(spec(tokens={"input": 40000, "output": 4000}))
    assert (DEFAULT_TASK_TOKENS.input, DEFAULT_TASK_TOKENS.output) == (40000, 4000)


def test_a_card_cannot_author_a_computed_facet():
    mid = "lab/cheap"
    with pytest.raises(SnapshotBuildError, match="computed"):
        build_snapshot(SnapshotInputs(
            models=[generator(mid)],
            offerings=[offering(mid, "p1", facts=[
                fact("offering", oid("p1", mid), "offering.cost_per_task", 0.1, source="src-pricing"),
            ])],
            evidence=[], sources=SOURCES, benchmark_domains=DOMAINS,
        ), registry=registry(), gate=False, as_of=AS_OF)


# ── the engine ─────────────────────────────────────────────────────────────


def test_the_value_is_the_design_formula_from_the_specs_token_counts():
    snapshot = index()
    decision = decide(spec(tokens={"input": 100000, "output": 10000}), snapshot, facets=facets)
    ranked = offerings_only(decision.results)
    assert [r.offering.model for r in ranked] == ["lab/cheap", "lab/dear"]
    # cheap: (1.0 × 100k + 5.0 × 10k) / 1e6 = 0.15; dear: (2 × 100k + 10 × 10k) / 1e6 = 0.30


def test_either_price_unknown_makes_it_unknown_so_the_offering_may_qualify():
    decision = decide(spec(), index(), facets=facets)
    unknown = {m.offering.model: m.unknown for m in decision.may_qualify if m.offering.provider}
    assert unknown["lab/half"] == ["offering.cost_per_task"]
    assert "lab/half" not in {r.offering.model for r in decision.results}


def test_a_condition_filters_on_the_computed_value():
    snapshot = index()
    # Default tokens 40k in, 4k out: cheap 0.06, dear 0.12.
    cheap = decide(spec(where=["offering.cost_per_task <= 0.10"],
                        objective={"max": f"{BENCH}"}), snapshot, facets=facets)
    assert [r.offering.model for r in offerings_only(cheap.results)] == ["lab/cheap"]
    # More output tokens price the cheap offering out as well.
    none = decide(spec(where=["offering.cost_per_task <= 0.10"], objective={"max": BENCH},
                       tokens={"input": 40000, "output": 20000}), snapshot, facets=facets)
    assert offerings_only(none.results) == []


def test_minimising_cost_orders_by_it_and_the_explanation_shows_the_formula():
    snapshot = index()
    decision = decide(
        spec(objective={"weights": {BENCH: 0.5, "-offering.cost_per_task": 0.5}},
             explain="full", tokens={"input": 40000, "output": 4000}),
        snapshot, facets=facets,
    )
    Decision.model_validate(decision.model_dump(mode="json"))
    by_model = {r.offering.model: r for r in offerings_only(decision.results)}
    cost = next(c for c in by_model["lab/cheap"].contributions
                if c.dimension == "-offering.cost_per_task")
    assert cost.raw_value == pytest.approx(0.06)
    assert cost.unit == "usd_per_task"
    assert cost.formula == (
        "(1 USD per 1M input tokens × 40,000 input tokens + 5 USD per 1M output tokens "
        "× 4,000 output tokens) ÷ 1,000,000 = 0.06 USD per task"
    )
    price_records = {
        snapshot.fact(oid("p1", "lab/cheap"), "offering.price.input").record_id,
        snapshot.fact(oid("p1", "lab/cheap"), "offering.price.output").record_id,
    }
    assert set(cost.records) == price_records
    origins = {o.path: o for o in decision.number_origins}
    raw_path = next(p for p in origins if p.endswith("raw_value")
                    and "results" in p and origins[p].basis.startswith("computed"))
    assert "× 40,000 input tokens" in origins[raw_path].basis
    shown = [f for row in decision.top for f in row.facts if f.facet == "offering.cost_per_task"]
    assert shown and all(f.formula and f.unit == "usd_per_task" for f in shown)
    assert "0.06 USD per task" in render_html(decision, snapshot)


def test_a_near_miss_on_cost_carries_the_formula_and_both_price_records():
    snapshot = index()
    decision = decide(
        spec(where=["offering.cost_per_task <= 0.10"], objective={"max": BENCH}, explain="summary"),
        snapshot, facets=facets,
    )
    miss = next(m for m in decision.near_misses if m.offering.model == "lab/dear")
    assert miss.value == pytest.approx(0.12)
    assert miss.unit == "usd_per_task"
    assert len(miss.records) == 2
    assert "= 0.12 USD per task" in miss.formula


def test_the_worker_answers_a_spec_with_task_tokens():
    import importlib.util
    from pathlib import Path

    source = Path(__file__).resolve().parents[1] / "api" / "worker" / "src" / "decide_service.py"
    loader = importlib.util.spec_from_file_location("modelspec_decide_service_cost", source)
    decide_service = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(decide_service)

    status, body = decide_service.decide({
        "spec_version": 1,
        "task_tokens": {"input": 40000, "output": 4000},
        "where": ["model.class = text-generator", "offering.cost_per_task <= 0.1"],
        "optimize": {"weights": {BENCH: 0.7, "-offering.cost_per_task": 0.3}},
        "explain": "none",
    }, index())
    assert status == 200, body
    assert body["contract_version"] == "1.8"
