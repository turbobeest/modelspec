"""MODEL-266: ranked rows have a provider or verified open weights."""

from datetime import date

import pytest

from decision.contract import parse_spec
from decision.engine import decide
from decision.registry import facet
from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
from tests.snapshot_records import SOURCES, evidence, fact, model, offering


@pytest.mark.parametrize("has_offering", [True, False], ids=["hosted", "self-host"])
@pytest.mark.parametrize("weights", ["open_weights", "closed_weights", None])
@pytest.mark.parametrize("verified", [True, False], ids=["verified", "unverified"])
@pytest.mark.parametrize("allow_unknown", [False, True])
def test_ranked_rows_have_an_offering_or_open_weights(has_offering, weights, verified,
                                                    allow_unknown):
    mid = "lab/route-regression"
    benchmark = "terminal_bench_v4_0"
    inputs = SnapshotInputs(
        models=[model(mid, facts=[
            fact("model", mid, "model.class", "text-generator"),
            fact("model", mid, "model.weights_openness", weights,
                 state="known" if weights else "unknown",
                 outcome="verified" if verified else None),
        ])],
        offerings=[offering(mid, "openai")] if has_offering else [],
        evidence=[evidence(mid, benchmark, 60)],
        sources=SOURCES,
        benchmark_domains={benchmark: [("software_engineering", "direct")]},
    )
    index = load_built_snapshot(build_snapshot(
        inputs, gate=False, as_of=date(2026, 9, 24),
    ))
    question = parse_spec({
        "spec_version": 1,
        "where": ["model.class = text-generator"] + ([
            "any(offering.provider = openai; "
            "model.weights_openness = open_weights unknown(pass))",
        ] if allow_unknown else []),
        "optimize": {"max": benchmark},
        "explain": "full",
    }, facets=facet)
    answer = decide(question, index, facets=facet)

    can_use = has_offering or (weights == "open_weights" and verified)
    assert bool(answer.results) == can_use
    assert not answer.may_qualify
    for row in answer.results:
        assert row.offering.provider is not None or (
            index.fact(row.offering.model, "model.weights_openness").state == "known"
            and index.fact(row.offering.model, "model.weights_openness").value == "open_weights"
        )
    if not can_use:
        assert len(answer.eliminated.models) == 1
        removed = answer.eliminated.models[0]
        assert removed.model == mid
        assert removed.condition == "model.weights_openness = open_weights unknown(fail)"
        assert removed.value == (weights if verified else None)
