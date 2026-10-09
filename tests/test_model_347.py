"""MODEL-347: models that pass the gates stay visible, self-host unknown weights
are not a route, and a no_feasible hint names the constraint that bound.
"""
from __future__ import annotations

import json
import re

from decision.contract import parse_spec
from decision.engine import decide
from decision.snapshot import FactValue, build_snapshot, load_snapshot_bytes
from tests.plan_records import inputs
from tests.snapshot_records import loaded_index

_TICKET = re.compile(r"MODEL-\d+")


def _decide(snapshot, raw):
    return decide(parse_spec({"spec_version": 1, "explain": "none", **raw}, facets=None), snapshot)


def test_models_that_pass_every_gate_stay_visible_when_the_objective_has_no_estimate():
    snapshot = loaded_index(
        {
            "lab/passes": {"model.max_output_tokens": 2000},
            "lab/also": {"model.max_output_tokens": 1000},
            "lab/fails": {"model.max_output_tokens": 100},
        },
        benchmark_domains={"unused_bench": [("software_engineering", "direct")]},
    )

    decision = _decide(snapshot, {
        "where": ["model.max_output_tokens >= 500"],
        "optimize": {"max": "software_engineering"},
    })

    assert decision.status == "no_feasible"
    assert decision.results == []
    qualified = {row.model: row.unknown for row in decision.may_qualify}
    assert qualified["lab/passes"] == ["software_engineering"]
    assert qualified["lab/also"] == ["software_engineering"]
    assert "lab/fails" not in qualified
    listed = {row.model for row in decision.by_model}
    assert {"lab/passes", "lab/also"} <= listed
    assert decision.relax == [
        "no model that meets the requirements has a value for software_engineering",
    ]
    assert _TICKET.search(json.dumps(decision.model_dump(mode="json"))) is None


def test_unknown_weights_on_a_sold_model_are_not_a_self_host_route():
    snapshot = loaded_index(
        {
            "lab/open": {
                "model.context_window": 8000,
                "model.weights_openness": "open_weights",
                "model.fits_hardware": ["apple_m3_max"],
            },
            "lab/unknown-sold": {
                "model.context_window": 16000,
                "model.weights_openness": FactValue("unknown"),
            },
        },
        hosted=True,
    )
    seen = {}
    decision = decide(
        parse_spec({
            "spec_version": 1,
            "access": "own_hardware",
            "where": ["model.weights_openness = open_weights"],
            "optimize": {"max": "model.context_window"},
            "explain": "none",
        }, facets=None),
        snapshot,
        _filter_trace=lambda filtered: seen.update(filtered=filtered),
    )

    assert [row.offering.model for row in decision.results] == ["lab/open"]
    assert decision.status == "answered"
    assert "lab/unknown-sold" not in {row.model for row in decision.may_qualify}
    eliminated = [
        row for row in seen["filtered"].eliminated if row.candidate == "lab/unknown-sold"
    ]
    assert len(eliminated) == 1
    assert eliminated[0].condition == "model.weights_openness = open_weights unknown(fail)"
    assert eliminated[0].unverified is True


def test_closed_or_unknown_weights_are_not_a_self_host_route_without_a_weights_condition():
    """A tools-all or reasoning-all spec names no weights_openness condition.
    Own hardware still drops a sold model whose weights are closed or unknown.
    """
    snapshot = loaded_index(
        {
            "lab/open": {
                "model.context_window": 8000,
                "model.weights_openness": "open_weights",
                "model.fits_hardware": ["apple_m3_max"],
            },
            "lab/closed-sold": {
                "model.context_window": 16000,
                "model.weights_openness": "closed_weights",
                "model.fits_hardware": ["apple_m3_max"],
            },
            "lab/unknown-sold": {
                "model.context_window": 32000,
                "model.weights_openness": FactValue("unknown"),
                "model.fits_hardware": ["apple_m3_max"],
            },
        },
        hosted=True,
    )
    seen = {}
    decision = decide(
        parse_spec({
            "spec_version": 1,
            "access": "own_hardware",
            "optimize": {"max": "model.context_window"},
            "explain": "none",
        }, facets=None),
        snapshot,
        _filter_trace=lambda filtered: seen.update(filtered=filtered),
    )

    assert [row.offering.model for row in decision.results] == ["lab/open"]
    assert decision.status == "answered"
    by_candidate = {row.candidate: row for row in seen["filtered"].eliminated}
    closed = by_candidate["lab/closed-sold"]
    unknown = by_candidate["lab/unknown-sold"]
    assert closed.condition == "model.weights_openness = open_weights unknown(fail)"
    assert unknown.condition == closed.condition
    assert closed.unverified is False
    assert unknown.unverified is True


def test_a_no_reach_does_not_name_a_condition_whose_removal_does_not_help():
    """The context floor empties the lineup, and the class still would.
    Removing the floor does not produce a feasible answer, so relax does not name it.
    """
    snapshot = loaded_index({
        "lab/text": {
            "model.class": "text-generator",
            "model.context_window": 8000,
        },
    })

    decision = _decide(snapshot, {
        "where": [
            "model.context_window >= 1000000",
            "model.class = decider",
        ],
        "optimize": {"max": "model.context_window"},
    })

    assert decision.status == "no_feasible"
    assert decision.results == []
    assert decision.relax == ["no complete objective values"]
    assert all("model.context_window" not in item for item in decision.relax)
    assert all("model.class" not in item for item in decision.relax)


def test_a_reach_names_the_condition_that_emptied_the_lineup():
    snapshot = loaded_index(
        {
            "lab/open": {
                "model.context_window": 8000,
                "model.weights_openness": "open_weights",
                "model.fits_hardware": ["apple_m3_max"],
                "origin.lab_jurisdiction": "KR",
            },
        },
        hosted=True,
    )

    decision = _decide(snapshot, {
        "access": "own_hardware",
        "where": ["origin.lab_jurisdiction in {US}"],
        "optimize": {"max": "model.context_window"},
    })

    assert decision.status == "no_feasible"
    assert decision.results == []
    assert decision.relax == ["origin.lab_jurisdiction in {US}"]
    assert _TICKET.search(json.dumps(decision.model_dump(mode="json"))) is None


def test_with_estate_status_follows_the_estate_lineup_not_the_unrestricted_one():
    """An open-weights model with no published fit is may_qualify on the
    unrestricted own_hardware lineup, so that answer is partial. A device the
    model does not fit, and is not indeterminate for, does not reach it, so
    with_estate is answered over the same ranked model.
    """
    data = build_snapshot(inputs()).to_bytes(key=b"model-347")
    snapshot = load_snapshot_bytes(data, key=b"model-347", source="MODEL-347 estate status")

    decision = _decide(snapshot, {
        "access": "own_hardware",
        "estate": {"devices": ["apple_m3_max"]},
        "optimize": {"max": "model.context_window"},
    })

    assert [row.offering.model for row in decision.results] == ["acme/tiny"]
    assert [(row.model, row.unknown) for row in decision.may_qualify] == [
        ("acme/unfit", ["model.fits_hardware"]),
    ]
    assert decision.status == "partial"
    assert [row.offering.model for row in decision.with_estate.results] == ["acme/tiny"]
    assert decision.with_estate.may_qualify == []
    assert decision.with_estate.status == "answered"
