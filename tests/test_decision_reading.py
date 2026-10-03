"""Agent reporting guidance follows the actual engine answer (MODEL-284)."""

from __future__ import annotations

import json

import pytest

from decision.contract import parse_spec
from decision.engine import decide
from decision.registry import facet
from decision.reading import MAX_BYTES, for_decision, for_refusal
from decision.contract import Issue, TieBreakers, TiedAnswer
from tests.snapshot_records import TIED_INTERVALS, loaded_index
from tests.test_decide_page_fixtures import _service, _snapshot, _spec

# Compact JSON, UTF-8. Prose must not repeat member IDs or rejected task text.
READING_BUDGET_BYTES = MAX_BYTES


def _size(reading):
    return len(json.dumps(reading, ensure_ascii=False, separators=(",", ":")).encode())


@pytest.mark.parametrize("level", ["none", "summary", "full"])
def test_tie_names_all_members_even_when_results_are_limited(level):
    status, body = _service().decide(_spec(level) | {"limit": 1}, _snapshot(TIED_INTERVALS))
    assert status == 200
    assert body["answer"]["kind"] == "tied"
    reading = body["reading"]
    assert len(body["results"]) == 1
    assert len(reading["tied"]) > 1
    assert reading["tied"] == body["answer"]["members"]
    assert "Do not name a single winner among tied." in reading["do_not_claim"]
    assert _size(reading) <= READING_BUDGET_BYTES


@pytest.mark.parametrize("requirement, field", [
    ({"task": "Check a private cache race prompt. " * 1000}, "task"),
    ({"where": ["model.thread_safe_code_and_tests = true"]}, "model.thread_safe_code_and_tests"),
])
def test_refusal_names_unapplied_requirements_without_echoing_the_prompt(requirement, field):
    status, body = _service().decide(_spec("summary") | requirement, _snapshot())
    assert status == 400
    assert body["error"]["code"] == "invalid_spec"
    reading = body["reading"]
    assert reading["not_applied"] == [field]
    assert "Do not claim rejected requirements were checked, including after retry." in (
        reading["do_not_claim"])
    assert "private cache race prompt" not in json.dumps(reading)
    assert _size(reading) <= READING_BUDGET_BYTES


@pytest.mark.parametrize("where", [
    ["model.fits_hardware in {nvidia_rtx_5090}"],
    [{"all": [{"not": "model.fits_hardware in {apple_m3_max}"},
              "model.context_window >= 8192"]}],
])
def test_hardware_membership_is_an_estimate_even_at_explain_none(where):
    snapshot = loaded_index({"lab/local": {
        "model.fits_hardware": ["nvidia_rtx_5090"],
        "model.context_window": 32768,
    }})
    spec = parse_spec({"spec_version": 1, "where": where,
                       "optimize": {"max": "model.context_window"}, "explain": "none"},
                      facets=facet)
    body = decide(spec, snapshot).model_dump(mode="json")
    assert body["results"][0]["model"] == "lab/local"
    assert body["reading"]["estimates"] == ["model.fits_hardware"]
    assert "Do not present estimates as measurements." in body["reading"]["do_not_claim"]
    assert "Do not claim fit for a specific quantization or context workload." in (
        body["reading"]["do_not_claim"])
    assert _size(body["reading"]) <= READING_BUDGET_BYTES


def test_returned_capability_estimates_are_identified():
    from tests.test_decision_capability import snapshot

    status, body = _service().decide(
        {"spec_version": 1, "optimize": {"max": "software_engineering"}}, snapshot())
    assert status == 200
    assert any(row["estimates"] for row in body["results"])
    assert "results.estimates" in body["reading"]["estimates"]
    assert _size(body["reading"]) <= READING_BUDGET_BYTES


def test_an_unavailable_requested_capability_is_disclosed_on_success():
    status, body = _service().decide(
        _spec("summary") | {"capabilities": {"thread_safety": "required"}}, _snapshot())
    assert status == 200
    assert body["results"]
    assert body["reading"]["not_applied"] == ["thread_safety"]
    assert "Do not claim not_applied requirements were evaluated." in body["reading"]["do_not_claim"]
    assert _size(body["reading"]) <= READING_BUDGET_BYTES


def test_cost_order_is_not_a_quality_rank():
    status, body = _service().decide(
        _spec("none") | {"optimize": {"min": "offering.cost_per_task"}}, _snapshot())
    assert status == 200
    assert body["results"]
    assert "Do not claim a quality rank from this objective." in body["reading"]["do_not_claim"]


def test_no_reading_for_a_separated_measured_answer_or_an_empty_refusal():
    status, body = _service().decide(
        _spec("none") | {"capabilities": {}, "optimize": {"max": "quality"}}, _snapshot())
    assert status == 200
    assert body["answer"]["kind"] == "separated"
    assert "reading" not in body
    assert "reading" not in _service().snapshot_changed("snap_other", _snapshot())[1]
    status, malformed = _service().decide([], _snapshot())
    assert status == 400
    assert "reading" not in malformed


def test_reading_is_additive_and_does_not_change_the_existing_decision():
    snapshot = _snapshot(TIED_INTERVALS)
    body = decide(parse_spec(_spec("full"), facets=_service()._facets(snapshot)), snapshot,
                  facets=_service()._facets(snapshot))
    with_reading = body.model_dump(mode="json")
    without_reading = body.model_copy(update={"reading": None}).model_dump(mode="json")
    assert with_reading.pop("reading")
    assert with_reading == without_reading


@pytest.mark.parametrize("estate", [False, True])
def test_size_budget_covers_large_ties_and_long_rejected_field_ids(estate):
    snapshot = _snapshot(TIED_INTERVALS)
    spec = parse_spec(_spec("none"), facets=_service()._facets(snapshot))
    decision = decide(spec, snapshot, facets=_service()._facets(snapshot))
    if estate:
        decision.with_estate = decide(parse_spec({
            "spec_version": 1, "optimize": {"max": "quality"},
            "estate": {"devices": ["apple_m3_max"]}, "explain": "none",
        }, facets=facet), _reading_snapshot(), facets=facet).with_estate
    members = [f"lab/model-{i:03d}" for i in range(500)]
    decision.answer = TiedAnswer(kind="tied", members=members, basis="test",
                                 tie_breakers=TieBreakers(),
                                 deterministic_order=members)
    reading = for_decision(decision, hardware_fit=True, quality_objective=False,
                           not_applied=["unsupported_" + "x" * 2000])
    wire = reading.model_dump(mode="json")
    assert _size(wire) <= READING_BUDGET_BYTES
    assert len(reading.tied) + reading.omitted["tied"] == len(members)
    assert reading.omitted["not_applied"] == 1
    assert decision.answer.members == members
    assert "Do not treat omitted lists as complete" in " ".join(reading.do_not_claim)

    refused = for_refusal([Issue(None, "字段" * 2000, "unknown", "where[0]")])
    assert _size(refused.model_dump(mode="json")) <= READING_BUDGET_BYTES
    assert refused.omitted == {"not_applied": 1}


def _reading_snapshot():
    from datetime import date
    from decision.registry import default
    from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
    from tests.snapshot_records import SOURCES, evidence, fact, model, offering

    scores = {"lab/frontier": 95, "lab/held-a": 70, "lab/held-b": 70,
              "lab/low-a": 40, "lab/low-b": 20}
    models = [model(mid, facts=[
        fact("model", mid, "model.class", "text-generator"),
        fact("model", mid, "model.weights_openness", "open_weights"),
        fact("model", mid, "model.fits_hardware",
             ["apple_m3_max"] if mid.startswith("lab/held-") else []),
    ]) for mid in scores]
    rows = [evidence(mid, benchmark, score, interval=[score - 0.1, score + 0.1])
            for mid, score in scores.items() for benchmark in ("quality", "medical_suite")]
    built = build_snapshot(SnapshotInputs(
        models=models, evidence=rows, sources=SOURCES,
        offerings=[offering(mid, "together-ai" if mid.startswith("lab/held-") else "openai")
                   for mid in scores],
        benchmark_domains={"quality": [("software_engineering", "direct")],
                           "medical_suite": [("medical", "direct")]},
        benchmark_refinements={"quality": [("input_length_long_context", "direct")]},
        benchmark_metadata={name: {"random_baseline": 0, "sample_size": 500,
                                   "direction": "higher_is_better"}
                            for name in ("quality", "medical_suite")},
    ), registry=default(), gate=False, as_of=date(2026, 9, 25))
    return load_built_snapshot(built)


@pytest.mark.parametrize("estate", [None, {"devices": ["apple_m3_max"]}])
def test_any_parent_refinement_weights_are_quality_evidence(estate):
    raw = {"spec_version": 1,
           "optimize": {"weights": {"any/input_length_long_context": 1}},
           "explain": "none"}
    if estate is not None:
        raw["estate"] = estate
    decision = decide(parse_spec(raw, facets=facet), _reading_snapshot(), facets=facet)
    assert decision.results
    assert all(row.refinement_estimates for row in decision.results)
    assert "Do not claim a quality rank from this objective." not in decision.reading.do_not_claim
    if estate is not None:
        assert "model.fits_hardware" in decision.reading.estimates


@pytest.mark.parametrize("estate", [
    {"devices": ["apple_m3_max"]}, {"providers": ["together-ai"]},
])
def test_estate_tie_is_disclosed_when_the_main_answer_is_separated(estate):
    decision = decide(parse_spec({
        "spec_version": 1, "optimize": {"max": "quality"}, "explain": "none",
        "estate": estate,
    }, facets=facet), _reading_snapshot(), facets=facet)
    assert decision.answer.kind == "separated"
    assert decision.with_estate.answer.kind == "tied"
    assert set(decision.with_estate.answer.members) == {"lab/held-a", "lab/held-b"}
    assert not decision.reading.tied
    assert ("Do not name a single winner among with_estate.answer.members; that answer is tied."
            in decision.reading.do_not_claim)
    assert _size(decision.reading.model_dump(mode="json")) <= READING_BUDGET_BYTES


def test_estate_reading_keeps_requirements_unapplied_after_benchmark_exclusion():
    snapshot = _reading_snapshot()
    assert "medical" in snapshot.domain_ids()
    raw = {
        "spec_version": 1, "optimize": {"max": "quality"}, "explain": "none",
        "capabilities": {"medical": "required", "thread_safety": "required"},
        "exclude_benchmarks": ["medical_suite"],
    }
    plain = decide(parse_spec(raw, facets=facet), snapshot, facets=facet)
    decision = decide(parse_spec(raw | {"estate": {"devices": ["apple_m3_max"]}},
                                 facets=facet), snapshot, facets=facet)
    assert decision.results
    assert not any(row.estimates for row in decision.results)
    assert decision.reading.not_applied == plain.reading.not_applied == ["thread_safety"]
    assert ("Do not claim a quality rank from this objective." in decision.reading.do_not_claim) == (
        "Do not claim a quality rank from this objective." in plain.reading.do_not_claim)
    assert "Do not claim not_applied requirements were evaluated." in decision.reading.do_not_claim
