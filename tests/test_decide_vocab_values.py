"""A value outside a facet's vocabulary is refused, not gated into an empty answer (MODEL-318).

The 2026-10-04 Gemini proof run sent ``model.weights_openness = proprietary``.
Decide answered 200 ``no_feasible``, and the agent relaxed its way to a model
it had been told never to pick.
"""

from __future__ import annotations

import pytest

from tests.test_decide_worker import service, snapshot, snapshot_bytes  # noqa: F401

LOOKUP = "https://api.modelspec.dev/v1/vocabulary?section=facets&id="


def _decide(service, snapshot, *, where=(), weights=None):
    optimize = {"weights": weights} if weights else {"max": "model.context_window"}
    return service.decide({"spec_version": 1, "where": list(where), "optimize": optimize},
                          snapshot)


def _only_issue(status, body):
    assert status == 400, body
    assert body["error"]["code"] == "invalid_spec"
    [issue] = body["error"]["issues"]
    return issue


def test_an_unregistered_enum_gate_names_the_allowed_values(service, snapshot):
    issue = _only_issue(*_decide(service, snapshot,
                                 where=["model.weights_openness = proprietary"]))
    assert issue == {
        "path": "where[0]",
        "condition": "model.weights_openness = proprietary",
        "field": "model.weights_openness",
        "reason": "'proprietary' is not a registered value of model.weights_openness",
        "value": "proprietary",
        "value_type": "enum",
        "allowed_values": ["closed_weights", "open_weights"],
        "next": LOOKUP + "model.weights_openness",
    }


@pytest.mark.parametrize("condition", [
    "model.weights_openness != proprietary",
    "model.weights_openness not in {proprietary}",
])
def test_a_negated_unregistered_value_is_refused_not_a_tautology(service, snapshot, condition):
    issue = _only_issue(*_decide(service, snapshot, where=[condition]))
    assert issue["value"] == "proprietary"
    assert issue["allowed_values"] == ["closed_weights", "open_weights"]


def test_a_set_gate_names_only_the_unregistered_member(service, snapshot):
    issue = _only_issue(*_decide(service, snapshot,
                                 where=["model.input_modalities in {text, smell}"]))
    assert issue["value"] == "smell"
    assert issue["value_type"] == "set"
    assert issue["allowed_values"] == ["audio", "document", "image", "structured", "text", "video"]


def test_an_unregistered_enum_preference_names_the_allowed_values(service, snapshot):
    issue = _only_issue(*_decide(service, snapshot, weights={
        "model.weights_openness": {"prefer": "proprietary", "weight": 1}}))
    assert issue["path"] == "optimize.weights"
    assert issue["reason"] == "preferred value 'proprietary' is not a registered value"
    assert issue["value"] == "proprietary"
    assert issue["allowed_values"] == ["closed_weights", "open_weights"]
    assert issue["next"] == LOOKUP + "model.weights_openness"


def test_a_word_on_a_number_facet_is_refused_not_a_server_error(service, snapshot):
    issue = _only_issue(*_decide(service, snapshot, where=["model.context_window >= large"]))
    assert issue["reason"] == "model.context_window takes a number, not 'large'"
    assert issue["value"] == "large"
    assert issue["value_type"] == "number"
    assert "allowed_values" not in issue
    assert issue["next"] == LOOKUP + "model.context_window"


def test_a_date_window_on_a_number_facet_names_both_ends(service, snapshot):
    status, body = _decide(service, snapshot,
                           where=["model.context_window in [2026-01-01, 2026-02-01]"])
    assert status == 400
    assert [issue["value"] for issue in body["error"]["issues"]] == ["2026-01-01", "2026-02-01"]


def test_a_boolean_facet_takes_true_or_false(service, snapshot):
    issue = _only_issue(*_decide(service, snapshot, where=["feature.tool_calling = yes"]))
    assert issue["value"] == "yes"
    assert issue["allowed_values"] == [False, True]


def test_a_date_facet_takes_a_date(service, snapshot):
    issue = _only_issue(*_decide(service, snapshot, where=["model.release_date >= 5"]))
    assert issue["reason"] == "model.release_date takes an ISO date, not 5"


def test_a_long_value_is_clipped_before_it_is_echoed(service, snapshot):
    issue = _only_issue(*_decide(service, snapshot,
                                 where=[{"facet": "model.weights_openness", "op": "=",
                                         "value": "x" * 500}]))
    assert issue["value"] == "x" * 77 + "..."


@pytest.mark.parametrize("condition", [
    "model.weights_openness = open_weights",
    "model.weights_openness in {open_weights, closed_weights}",
    "origin.lab_jurisdiction in {US}",
    "offering.provider = openai",
    "offering.provider = cursor",  # a vendor owns a subscription plan
    "model.context_window >= 100000",
    "software_engineering >= 0.5",
    "swe_bench_pro >= 55 @independent",
    "known(model.weights_openness)",
])
def test_a_value_the_vocabulary_holds_is_still_answered(service, snapshot, condition):
    status, body = _decide(service, snapshot, where=[condition])
    assert status == 200, body.get("error")


@pytest.mark.parametrize("condition,section", [
    ("swe_bench_pro >= high", "benchmarks"),
    ("software_engineering >= high", "domains"),
])
def test_next_names_the_section_that_lists_the_facet(service, snapshot, condition, section):
    field = condition.split()[0]
    issue = _only_issue(*_decide(service, snapshot, where=[condition]))
    assert issue["next"] == (f"https://api.modelspec.dev/v1/vocabulary?section={section}&id={field}")
