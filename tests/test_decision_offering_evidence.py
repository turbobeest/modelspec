"""An offering answers its model's evidence (MODEL-158).

Capability evidence belongs to the model. An offering is that model as one
provider sells it, so it differs in price, region and data terms, not in what
the model can do. The loaded index resolves this; the stored snapshot does not
copy evidence onto offerings.
"""

from __future__ import annotations

from datetime import date

from decision.contract import parse_spec
from decision.engine import decide
from decision.registry import facet as facets
from decision.snapshot import SnapshotInputs, build_snapshot, load_snapshot_bytes
from tests.snapshot_records import SOURCES, evidence, fact, model, offering

AS_OF = date(2026, 9, 24)
TERMINAL = "terminal_bench_v4_0"
DOMAINS = {TERMINAL: [("agentic_tool_use", "direct"), ("software_engineering", "proxy")]}
PRICES = {"p1": 1.0, "p2": 2.0, "p3": 3.0}


def generator(mid: str):
    return model(mid, facts=[
        fact("model", mid, "model.class", "text-generator"),
        fact("model", mid, "model.context_window", 200000),
        fact("model", mid, "model.lifecycle", "active"),
    ])


def sold(mid: str, provider: str, price: float):
    oid = f"{provider}/{mid}/global/standard"
    return offering(mid, provider, price=price, facts=[
        fact("offering", oid, "offering.price.input", price, source="src-pricing"),
    ])


def oid(provider: str, mid: str = "lab/m") -> str:
    return f"{provider}/{mid}/global/standard"


def inputs(rows=None, extra_offerings=()):
    return SnapshotInputs(
        models=[generator("lab/m"), generator("lab/other")],
        offerings=[sold("lab/m", p, price) for p, price in PRICES.items()]
        + [sold("lab/other", "p1", 0.5), *extra_offerings],
        evidence=[evidence("lab/m", TERMINAL, 60.0)] if rows is None else rows,
        sources=SOURCES,
        benchmark_domains=DOMAINS,
    )


def build(rows=None, extra_offerings=()):
    built = build_snapshot(inputs(rows, extra_offerings), gate=False, as_of=AS_OF)
    return built, load_snapshot_bytes(built.to_bytes(key=None), key=None, include_archive=True)


def spec(where=(), objective=None):
    return parse_spec({
        "spec_version": 1,
        "capabilities": {"agentic_tool_use": "required"},
        "where": ["model.class = text-generator", *where],
        "optimize": objective or {"max": f"{TERMINAL} @independent"},
        "explain": "none",
    }, facets=facets)


def offerings_of(rows, mid="lab/m"):
    return [r for r in rows if r.offering.model == mid and r.offering.provider is not None]


def test_each_offering_ranks_on_its_models_evidence_at_its_own_price():
    _, index = build()
    decision = decide(spec(), index, facets=facets)

    ranked = offerings_of(decision.results)
    assert sorted(r.offering.provider for r in ranked) == ["p1", "p2", "p3"]
    values = {
        r.offering.provider: [e.value for e in index.evidence(oid(r.offering.provider), TERMINAL)]
        for r in ranked
    }
    assert values == {"p1": [60.0], "p2": [60.0], "p3": [60.0]}
    prices = {p: index.fact(oid(p), "offering.price.input").value for p in PRICES}
    assert prices == PRICES
    # None of the model's offerings waits in may_qualify for evidence it already has.
    assert not [m for m in decision.may_qualify if m.model == "lab/m"]


def test_an_offering_only_condition_still_tells_the_offerings_apart():
    _, index = build()
    decision = decide(spec(where=["offering.price.input <= 2"]), index, facets=facets)
    assert sorted(r.offering.provider for r in offerings_of(decision.results)) == ["p1", "p2"]

    cheapest = decide(
        spec(where=[f"{TERMINAL} >= 50 @independent"], objective={"min": "offering.price.input"}),
        index, facets=facets,
    )
    assert [r.offering.provider for r in offerings_of(cheapest.results)] == ["p1", "p2", "p3"]


def test_evidence_is_never_copied_to_another_models_offerings():
    _, index = build()
    assert index.evidence(oid("p1", "lab/other"), TERMINAL) == ()
    decision = decide(spec(), index, facets=facets)
    assert "lab/other" not in {r.offering.model for r in decision.results}
    assert {m.offering.provider for m in decision.may_qualify if m.model == "lab/other"} >= {"p1"}


def test_an_offerings_own_measurement_replaces_its_models_for_that_benchmark_only():
    rows = [
        evidence("lab/m", TERMINAL, 60.0),
        evidence("lab/m", "gpqa_diamond", 80.0),
        evidence(oid("p2"), TERMINAL, 55.0, subject_kind="offering"),
    ]
    _, index = build(rows)
    assert [e.value for e in index.evidence(oid("p2"), TERMINAL)] == [55.0]
    assert [e.value for e in index.evidence(oid("p2"), "gpqa_diamond")] == [80.0]
    assert [e.value for e in index.evidence(oid("p1"), TERMINAL)] == [60.0]
    assert [e.value for e in index.evidence("lab/m", TERMINAL)] == [60.0]


def test_inheritance_happens_at_load_so_the_stored_snapshot_is_unchanged():
    first, _ = build()
    second, _ = build()
    assert first.to_bytes(key=None) == second.to_bytes(key=None)
    # Evidence is stored once, under the model; no offering carries a copy.
    assert set(first.content["lineup"]["evidence"]) == {"lab/m"}


# --- one row per model when it has offerings (MODEL-159) ------------------------------------------


def test_a_model_with_offerings_ranks_only_through_them():
    _, index = build()
    decision = decide(spec(), index, facets=facets)
    bare = [r for r in decision.results if r.offering.provider is None]
    assert bare == []
    assert [r.offering.provider for r in decision.results if r.offering.model == "lab/m"] \
        == ["p1", "p2", "p3"]
    # Nor does the bare row wait in may_qualify beside its offerings.
    assert all(m.offering.provider is not None for m in decision.may_qualify)


def test_a_model_with_no_offering_ranks_as_itself():
    built = build_snapshot(SnapshotInputs(
        models=[generator("lab/m"), generator("lab/open")],
        offerings=[sold("lab/m", "p1", 1.0)],
        evidence=[evidence("lab/m", TERMINAL, 60.0), evidence("lab/open", TERMINAL, 58.0)],
        sources=SOURCES, benchmark_domains=DOMAINS,
    ), gate=False, as_of=AS_OF)
    index = load_snapshot_bytes(built.to_bytes(key=None), key=None)
    decision = decide(spec(), index, facets=facets)
    assert [(r.offering.model, r.offering.provider) for r in decision.results] == [
        ("lab/m", "p1"), ("lab/open", None)]


def test_a_bare_model_row_is_represented_not_eliminated():
    from decision.filter import apply
    from decision.resolve import resolve

    _, index = build()
    filtered = apply(resolve(spec(), facets=facets), index)
    assert "lab/m" not in filtered.feasible
    assert "lab/m" not in {e.candidate for e in filtered.eliminated}
    assert "lab/m" not in {m.candidate for m in filtered.may_qualify}
