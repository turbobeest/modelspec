"""MODEL-384: subscription routes respect who can still use a plan."""

from __future__ import annotations

import pytest

from decision.contract import parse_spec
from decision.engine import decide
from decision.snapshot import build_snapshot, load_snapshot_bytes
from decision.vocabulary import build_vocabulary
from tests.plan_records import CONTEXT, CURSOR_PRO, MAX, OPUS, PRO, SONNET, inputs, vendor_inputs
from tests.snapshot_records import fact

AVAILABILITY = "offering.subscription.availability"
KEY = b"model-384-test-key"


def snapshot_for(value=None, *, state="known", max_coverage=True):
    catalogue = inputs()
    if not max_coverage:
        catalogue.subscriptions[0]["facts"] = [
            row for row in catalogue.subscriptions[0]["facts"]
            if row["facet"] not in {
                "offering.subscription.models_covered",
                "offering.subscription.families_covered",
                "offering.subscription.coverage_quote",
            }
        ]
    if value is not None or state != "known":
        catalogue.subscriptions[0]["facts"].append(
            fact("offering", MAX, AVAILABILITY, value, state=state, source="src-pricing")
        )
    data = build_snapshot(catalogue).to_bytes(key=KEY)
    return load_snapshot_bytes(data, key=KEY, source="MODEL-384 test snapshot")


def answer(snapshot, access="chat_app", estate=None, **overrides):
    spec = {"spec_version": 1, "optimize": {"max": CONTEXT}, "explain": "none"}
    if access is not None:
        spec["access"] = access
    if estate is not None:
        spec["estate"] = estate
    return decide(parse_spec(spec | overrides, facets=None), snapshot)


@pytest.mark.parametrize("access", ["chat_app", "coding_tool", "own_software"])
def test_new_buyer_cannot_route_through_closed_plan(access):
    decision = answer(snapshot_for("existing_subscribers_only"), access)

    assert all(route.plan != MAX for row in decision.results for route in row.plans)
    [excluded] = decision.excluded_plans
    assert excluded.plan == MAX
    assert "closed to new buyers" in excluded.reason
    if access == "chat_app":
        assert [row.model for row in decision.results] == [SONNET]
        assert [route.plan for route in decision.results[0].plans] == [PRO]
    else:
        assert OPUS in {row.model for row in decision.results}


@pytest.mark.parametrize("access", [None, "chat_app", "coding_tool"])
def test_estate_holder_keeps_closed_plan_and_answer_labels_it(access):
    snapshot = snapshot_for("existing_subscribers_only")
    decision = answer(snapshot, access, {"plans": [MAX]})
    held = decision.with_estate

    assert held is not None
    assert {row.offering.model for row in held.results} == {OPUS, SONNET}
    for row in held.results:
        assert row.estate.via.id == MAX
        assert row.estate.marginal_cost_per_task_usd == 0
        assert row.estate.availability == "existing_subscribers_only"
    assert "closed to new buyers" in held.gap.summary
    assert held.excluded_plans == []
    assert decision.results == answer(snapshot, access).results


@pytest.mark.parametrize("access", [None, "chat_app", "coding_tool"])
def test_retired_plan_never_routes_even_for_holder(access):
    decision = answer(snapshot_for("retired"), access, {"plans": [MAX]})

    assert all(route.plan != MAX for row in decision.results for route in row.plans)
    held = decision.with_estate
    assert held is not None
    assert held.results == []
    assert held.may_qualify == []
    [excluded] = held.excluded_plans
    assert excluded.plan == MAX
    assert "retired" in excluded.reason


def test_retired_plan_does_not_hide_usable_provider_key():
    held = answer(snapshot_for("retired"), "coding_tool",
                  {"plans": [MAX], "providers": ["anthropic"]}).with_estate

    assert held is not None
    assert {row.offering.model for row in held.results} == {OPUS, SONNET}
    assert all(row.estate.via.kind == "provider" for row in held.results)


@pytest.mark.parametrize("value", ["existing_subscribers_only", "retired"])
@pytest.mark.parametrize("access", [None, "chat_app", "coding_tool"])
def test_estate_gain_never_suggests_buying_unavailable_plan(value, access):
    held = answer(snapshot_for(value), access, {}).with_estate

    assert held is not None
    assert MAX not in {item.add.id for item in held.gain}


@pytest.mark.parametrize("value", ["existing_subscribers_only", "retired"])
def test_unavailable_plan_with_unknown_coverage_does_not_make_new_buyer_may_qualify(value):
    decision = answer(snapshot_for(value, max_coverage=False))

    assert OPUS not in {row.model for row in decision.may_qualify}


@pytest.mark.parametrize("state", ["unknown", "not_disclosed"])
def test_unknown_availability_keeps_todays_routes(state):
    baseline = answer(snapshot_for())
    decision = answer(snapshot_for(state=state))

    assert decision.results == baseline.results
    assert decision.may_qualify == baseline.may_qualify
    assert "excluded_plans" not in decision.model_dump(mode="json")


def test_absent_and_open_availability_keep_todays_routes():
    absent = answer(snapshot_for())
    opened = answer(snapshot_for("open"))

    assert {row.model for row in absent.results} == {OPUS, SONNET}
    assert absent.results == opened.results
    assert absent.may_qualify == opened.may_qualify
    assert "excluded_plans" not in absent.model_dump(mode="json")


def test_vocabulary_lists_availability_facet_and_sourced_plan_value():
    vocabulary = build_vocabulary(snapshot_for("existing_subscribers_only"))
    [facet] = vocabulary["estate"]["plan_facets"]

    assert facet["id"] == AVAILABILITY
    assert facet["allowed_values"] == ["existing_subscribers_only", "open", "retired"]
    plans = {plan["id"]: plan for plan in vocabulary["estate"]["plans"]}
    assert plans[MAX]["availability"] == "existing_subscribers_only"
    assert "availability" not in plans[PRO]


def test_bounded_worker_answer_keeps_plan_exclusion_reason():
    from tests.test_decision_plans import _service

    status, body = _service().decide({
        "spec_version": 1, "optimize": {"max": CONTEXT}, "access": "chat_app",
        "explain": "none", "fields": ["model"],
    }, snapshot_for("existing_subscribers_only"))

    assert status == 200
    [excluded] = body["excluded_plans"]
    assert excluded["plan"] == MAX
    assert "closed to new buyers" in excluded["reason"]


def test_bounded_answer_counts_exclusion_records_removed_to_fit_budget():
    import json

    from decision.bounded import RESPONSE_BYTES, project
    from decision.contract import PlanExclusion, ResponseOptions

    decision = answer(snapshot_for("existing_subscribers_only"))
    decision.excluded_plans = [
        PlanExclusion(plan=f"anthropic/subscription/closed-{number}",
                      reason="This plan is closed to new buyers. " * 50)
        for number in range(80)
    ]
    body = project(decision, ResponseOptions(fields=["model"]), not_applied=[])

    assert len(json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode()) <= RESPONSE_BYTES
    assert body["explanation"]["omitted"]["excluded_plans"] > 0
    assert len(body["excluded_plans"]) + body["explanation"]["omitted"]["excluded_plans"] == 80


def test_drill_down_counts_held_plan_exclusions_removed_to_fit_budget():
    import json

    from decision.bounded import DRILL_DOWN_BYTES, project
    from decision.contract import ModelEvidence, OfferingRef, PlanExclusion, ResponseOptions

    decision = answer(snapshot_for("retired"), estate={"plans": [MAX]})
    assert decision.with_estate is not None
    decision.with_estate.excluded_plans = [
        PlanExclusion(plan=f"anthropic/subscription/retired-{number}",
                      reason="This plan is retired and cannot be used by existing subscribers. " * 30)
        for number in range(80)
    ]
    body = project(
        decision, ResponseOptions(evidence_for=SONNET), not_applied=[],
        detail=ModelEvidence(model=SONNET, status="ranked", offering=OfferingRef(model=SONNET)),
    )

    assert len(json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode()) <= DRILL_DOWN_BYTES
    omitted = body["explanation"]["omitted"]["with_estate.excluded_plans"]
    assert omitted > 0
    assert len(body["with_estate"]["excluded_plans"]) + omitted == 80


@pytest.mark.parametrize("value", ["existing_subscribers_only", "retired"])
def test_subscription_only_vendor_does_not_route_new_buyer_through_unavailable_plan(value):
    catalogue = vendor_inputs()
    catalogue.subscriptions[-1]["facts"].append(
        fact("offering", CURSOR_PRO, AVAILABILITY, value, source="src-pricing")
    )
    data = build_snapshot(catalogue).to_bytes(key=KEY)
    snapshot = load_snapshot_bytes(data, key=KEY, source="MODEL-384 vendor snapshot")
    decision = answer(snapshot, {"kind": "coding_tool", "harness": "cursor"})

    assert all(row.offering.provider is not None for row in decision.results)
    assert all(route.plan != CURSOR_PRO for row in decision.results for route in row.plans)
    assert CURSOR_PRO in {row.plan for row in decision.excluded_plans}


def test_closed_plan_price_cannot_satisfy_new_buyers_monthly_price_filter():
    decision = answer(snapshot_for("existing_subscribers_only"),
                      where=["offering.plan.price_monthly >= 100"])

    assert decision.results == []


def test_exhausted_closed_plan_falls_back_to_held_key_without_purchase_suggestion():
    held = answer(snapshot_for("existing_subscribers_only"), "coding_tool", {
        "plans": [MAX], "providers": ["anthropic"], "exhausted": [MAX],
    }).with_estate

    assert held is not None
    assert all(row.estate.via.kind == "provider" for row in held.results)
    assert "closed to new buyers" not in held.gap.summary
    assert MAX not in {item.add.id for item in held.gain}
