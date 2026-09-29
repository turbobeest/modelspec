"""MODEL-179: the estate in the spec, and the two answers it produces.

The unrestricted answer never changes. With an ``estate`` a decision also
carries ``with_estate``: the same question answered from what the caller holds.
"""

from __future__ import annotations

import importlib.util
import json
import logging
from pathlib import Path

import pytest
from typer.testing import CliRunner

from decision import contract as c
from decision.contract import SpecError, parse_spec
from decision.engine import decide
from decision.snapshot import SnapshotInputs, build_snapshot, load_snapshot_bytes
from tests.snapshot_records import SOURCES, evidence, fact, model, offering, subscription

ROOT = Path(__file__).parents[1]
KEY = b"model-179-test-key"
CONTEXT = "model.context_window"


def _model(mid, context, *, open_weights=False, fits=None):
    facts = [
        fact("model", mid, CONTEXT, context),
        fact("model", mid, "model.weights_openness",
             "open_weights" if open_weights else "closed_weights"),
    ]
    if fits is not None:
        facts.append(fact("model", mid, "model.fits_hardware", fits))
    return model(mid, facts=facts)


def _offering(mid, provider, price):
    row = offering(mid, provider, price=price)
    oid = f"{provider}/{mid}/global/standard"
    row["facts"].append(fact("offering", oid, "offering.price.output", price, source="src-pricing"))
    return row


def _inputs() -> SnapshotInputs:
    models = [
        _model("acme/big", 200_000),
        _model("acme/mid", 100_000, open_weights=True, fits=["apple_m3_max"]),
        _model("acme/tiny", 50_000, open_weights=True, fits=["apple_m3_max", "nvidia_h100_sxm"]),
        _model("other/huge", 500_000),
    ]
    offerings = [
        _offering("acme/big", "anthropic", 15.0),
        _offering("acme/big", "aws-bedrock", 18.0),
        _offering("acme/mid", "together-ai", 1.0),
        _offering("other/huge", "openai", 30.0),
    ]
    covered = fact("offering", "anthropic/subscription/pro",
                   "offering.subscription.models_covered", ["acme/big"], source="src-pricing")
    undisclosed = fact("offering", "openai/subscription/plus",
                       "offering.subscription.models_covered", None, state="not_disclosed",
                       source="src-pricing")
    base_pro = subscription("anthropic", "pro")
    base_plus = subscription("openai", "plus")
    base_pro["facts"] = [f for f in base_pro["facts"]
                         if not f["facet"].endswith("models_covered")] + [covered]
    base_plus["facts"] = [f for f in base_plus["facts"]
                          if not f["facet"].endswith("models_covered")] + [undisclosed]
    return SnapshotInputs(models=models, offerings=offerings, sources=SOURCES,
                          subscriptions=[base_pro, base_plus])


@pytest.fixture(scope="module")
def snapshot_bytes() -> bytes:
    return build_snapshot(_inputs()).to_bytes(key=KEY)


@pytest.fixture(scope="module")
def snapshot(snapshot_bytes):
    return load_snapshot_bytes(snapshot_bytes, key=KEY, source="estate test snapshot")


def _raw(estate=None, **over) -> dict:
    raw = {"spec_version": 1, "optimize": {"max": CONTEXT}, "explain": "none"}
    if estate is not None:
        raw["estate"] = estate
    return raw | over


def _decide(snapshot, estate=None, **over):
    spec = parse_spec(_raw(estate, **over), facets=None)
    return decide(spec, snapshot)


def _models(with_estate) -> list[str]:
    return [r.offering.model for r in with_estate.results]


def _by_model(with_estate) -> dict:
    return {r.offering.model + "@" + (r.offering.provider or "device"): r
            for r in with_estate.results}


# ── the spec block ─────────────────────────────────────────────────────────


def test_a_spec_without_an_estate_is_unchanged(snapshot) -> None:
    decision = _decide(snapshot)
    dumped = decision.model_dump(mode="json")

    assert decision.with_estate is None
    assert "with_estate" not in dumped
    assert "estate" not in json.loads(c.canonical_json(parse_spec(_raw(), facets=None)))


def test_estate_ids_are_sorted_and_deduplicated_in_the_spec_hash() -> None:
    a = parse_spec(_raw({"providers": ["openai", "anthropic", "openai"]}), facets=None)
    b = parse_spec(_raw({"providers": ["anthropic", "openai"]}), facets=None)

    assert a.estate.providers == ["anthropic", "openai"]
    assert c.spec_hash(a) == c.spec_hash(b)


def test_the_estate_never_changes_the_unrestricted_answer(snapshot) -> None:
    plain = _decide(snapshot)
    held = _decide(snapshot, {"providers": ["together-ai"], "devices": ["apple_m3_max"]})

    assert held.answer == plain.answer
    assert held.results == plain.results
    assert held.may_qualify == plain.may_qualify
    assert held.status == plain.status
    assert plain.answer.leader == "other/huge"


@pytest.mark.parametrize("estate, message", [
    ({"providers": ["nonesuch"]}, "estate.providers[0]"),
    ({"plans": ["anthropic/subscription/nonesuch"]}, "estate.plans[0]"),
    ({"devices": ["quantum_toaster"]}, "estate.devices[0]"),
    ({"exhausted": ["nonesuch"]}, "estate.exhausted[0]"),
])
def test_an_id_outside_the_vocabulary_is_refused_with_its_path(snapshot, estate, message) -> None:
    with pytest.raises(SpecError) as caught:
        _decide(snapshot, estate)

    assert message in str(caught.value)


def test_an_unknown_key_in_the_estate_is_refused() -> None:
    with pytest.raises(SpecError):
        parse_spec(_raw({"keys": ["sk-secret"]}), facets=None)


# ── with_estate ────────────────────────────────────────────────────────────


def test_a_held_provider_marks_its_offerings_at_list_price(snapshot) -> None:
    held = _decide(snapshot, {"providers": ["anthropic"]}).with_estate

    assert _models(held) == ["acme/big"]
    row = held.results[0]
    assert row.offering.provider == "anthropic"
    assert row.estate.via.kind == "provider"
    assert row.estate.via.id == "anthropic"
    assert row.estate.cost_basis == "list_price"
    assert row.estate.marginal_cost_per_task_usd == pytest.approx(
        15.0 * 44_000 / 1_000_000)
    assert held.answer.leader == "acme/big"


def test_a_held_plan_is_costed_at_its_marginal_cost(snapshot) -> None:
    held = _decide(snapshot, {"plans": ["anthropic/subscription/pro"]}).with_estate

    assert _models(held) == ["acme/big"]
    row = held.results[0]
    assert row.estate.via.kind == "plan"
    assert row.estate.via.id == "anthropic/subscription/pro"
    assert row.estate.cost_basis == "plan_included"
    assert row.estate.marginal_cost_per_task_usd == 0


def test_a_plan_beats_the_metered_price_when_both_are_held(snapshot) -> None:
    held = _decide(snapshot, {
        "providers": ["anthropic"], "plans": ["anthropic/subscription/pro"],
    }).with_estate

    assert held.results[0].estate.via.kind == "plan"
    assert held.results[0].estate.marginal_cost_per_task_usd == 0


def test_a_plan_that_does_not_disclose_coverage_only_may_qualify(snapshot) -> None:
    held = _decide(snapshot, {"plans": ["openai/subscription/plus"]}).with_estate

    assert held.results == []
    assert [(m.model, m.unknown) for m in held.may_qualify] == [
        ("other/huge", ["offering.subscription.models_covered"])]
    assert held.status == "no_feasible" or held.answer is None


def test_a_held_device_adds_the_self_hosted_models_that_fit(snapshot) -> None:
    held = _decide(snapshot, {"devices": ["apple_m3_max"]}).with_estate

    assert sorted(_models(held)) == ["acme/mid", "acme/tiny"]
    for row in held.results:
        assert row.offering.provider is None
        assert row.estate.via.kind == "device"
        assert row.estate.via.id == "apple_m3_max"
        assert row.estate.cost_basis == "owned_hardware"
        assert row.estate.marginal_cost_per_task_usd == 0
    assert held.answer.leader == "acme/mid"


def test_a_device_the_model_does_not_fit_adds_nothing(snapshot) -> None:
    held = _decide(snapshot, {"devices": ["nvidia_h100_sxm"]}).with_estate

    assert _models(held) == ["acme/tiny"]


def test_the_two_answers_differ_and_the_gap_is_explained(snapshot) -> None:
    decision = _decide(snapshot, {"providers": ["together-ai"]})
    held = decision.with_estate

    assert decision.answer.leader == "other/huge"
    assert held.answer.leader == "acme/mid"
    assert held.gap.same_answer is False
    assert held.gap.unreachable_models == ["other/huge", "acme/big"]
    assert "other/huge" in held.gap.summary


def test_when_the_estate_reaches_the_unrestricted_answer_the_gap_says_so(snapshot) -> None:
    held = _decide(snapshot, {"providers": ["openai"]}).with_estate

    assert held.gap.same_answer is True
    assert held.gap.unreachable_models == []


@pytest.fixture(scope="module")
def tied_snapshot():
    quality = {"tie/a": (92.0, [86.0, 98.0]), "tie/b": (90.0, [84.0, 96.0]),
               "tie/c": (40.0, [36.0, 44.0])}
    models = [_model(mid, 100_000) for mid in quality]
    offerings = [_offering("tie/a", "anthropic", 3.0), _offering("tie/b", "openai", 4.0),
                 _offering("tie/c", "together-ai", 1.0)]
    rows = [evidence(mid, "quality", score, interval=interval)
            for mid, (score, interval) in quality.items()]
    built = build_snapshot(
        SnapshotInputs(models=models, offerings=offerings, evidence=rows, sources=SOURCES,
                       benchmark_domains={"quality": [("software_engineering", "direct")]}),
        gate=False)
    return load_snapshot_bytes(built.to_bytes(key=KEY), key=KEY, source="tied estate snapshot")


def _decide_tied(snapshot, estate):
    spec = parse_spec({"spec_version": 1, "capabilities": {"software_engineering": "required"},
                       "optimize": {"max": "quality"}, "explain": "none",
                       "estate": estate}, facets=None)
    return decide(spec, snapshot)


def test_a_tied_answer_names_the_tie_members_the_estate_cannot_reach(tied_snapshot) -> None:
    decision = _decide_tied(tied_snapshot, {"providers": ["anthropic", "together-ai"]})
    held = decision.with_estate

    assert decision.answer.kind == "tied"
    assert decision.answer.members == ["tie/a", "tie/b"]
    assert held.answer.kind == "separated"
    assert held.answer.leader == "tie/a"
    assert held.gap.same_answer is False
    assert held.gap.unreachable_models == ["tie/b"]
    assert "tie/b" in held.gap.summary
    assert "tie of tie/a, tie/b" in held.gap.summary
    assert "0 model" not in held.gap.summary


def test_a_tied_answer_reached_in_full_says_so(tied_snapshot) -> None:
    held = _decide_tied(tied_snapshot, {"providers": ["anthropic", "openai"]}).with_estate

    assert held.gap.same_answer is True
    assert held.gap.unreachable_models == []
    assert "tie/a" in held.gap.summary and "tie/b" in held.gap.summary


def test_a_tied_answer_with_no_tie_member_reachable_lists_them_all(tied_snapshot) -> None:
    decision = _decide_tied(tied_snapshot, {"providers": ["together-ai"]})
    held = decision.with_estate

    assert held.answer.leader == "tie/c"
    assert held.gap.unreachable_models == ["tie/a", "tie/b"]
    assert "0 model" not in held.gap.summary


def test_an_empty_estate_reaches_nothing_and_says_what_to_add(snapshot) -> None:
    held = _decide(snapshot, {}).with_estate

    assert held.results == []
    assert held.answer is None
    assert held.status == "no_feasible"
    assert held.gain


# ── exhausted ──────────────────────────────────────────────────────────────


def test_an_exhausted_plan_drops_out_of_with_estate_only(snapshot) -> None:
    estate = {"plans": ["anthropic/subscription/pro"]}
    live = _decide(snapshot, estate)
    spent = _decide(snapshot, estate | {"exhausted": ["anthropic/subscription/pro"]})

    assert _models(live.with_estate) == ["acme/big"]
    assert spent.with_estate.results == []
    assert spent.answer == live.answer
    assert spent.results == live.results


def test_an_exhausted_plan_leaves_the_key_path_usable(snapshot) -> None:
    held = _decide(snapshot, {
        "providers": ["anthropic"], "plans": ["anthropic/subscription/pro"],
        "exhausted": ["anthropic/subscription/pro"],
    }).with_estate

    assert held.results[0].estate.via.kind == "provider"
    assert held.results[0].estate.cost_basis == "list_price"


def test_an_exhausted_provider_takes_its_key_and_its_plans_with_it(snapshot) -> None:
    held = _decide(snapshot, {
        "providers": ["anthropic", "together-ai"], "plans": ["anthropic/subscription/pro"],
        "exhausted": ["anthropic"],
    }).with_estate

    assert _models(held) == ["acme/mid"]


# ── gain ───────────────────────────────────────────────────────────────────


def test_gain_names_what_added_would_change_the_answer(snapshot) -> None:
    held = _decide(snapshot, {"providers": ["together-ai"]}).with_estate
    gains = {(g.add.kind, g.add.id): g for g in held.gain}

    assert gains[("provider", "openai")].answer.leader == "other/huge"
    assert gains[("plan", "openai/subscription/plus")].status == "partial"
    assert ("provider", "together-ai") not in gains
    # A device that fits only models the estate already reaches changes nothing.
    assert ("device", "apple_m3_max") not in gains
    # acme/big is below acme/mid's reach only through other/huge, not through it.
    assert gains[("provider", "anthropic")].answer.leader == "acme/big" or (
        ("provider", "anthropic") not in gains)


def test_gain_never_offers_what_is_already_held_or_exhausted(snapshot) -> None:
    held = _decide(snapshot, {
        "providers": ["together-ai"], "plans": ["anthropic/subscription/pro"],
        "exhausted": ["anthropic/subscription/pro"],
    }).with_estate

    offered = {(g.add.kind, g.add.id) for g in held.gain}
    assert ("provider", "together-ai") not in offered
    assert ("plan", "anthropic/subscription/pro") not in offered


def test_gain_is_deterministic(snapshot) -> None:
    a = _decide(snapshot, {"providers": ["together-ai"]}).model_dump(mode="json")
    b = _decide(snapshot, {"providers": ["together-ai"]}).model_dump(mode="json")

    assert json.dumps(a, sort_keys=False) == json.dumps(b, sort_keys=False)


# ── the estate is a request, not a record ──────────────────────────────────


def test_marginal_cost_drives_a_cost_objective(snapshot) -> None:
    spec = _raw({"providers": ["anthropic", "aws-bedrock"],
                 "plans": ["anthropic/subscription/pro"]},
                optimize={"min": "offering.cost_per_task"})
    held = decide(parse_spec(spec, facets=None), snapshot).with_estate

    assert held.results[0].estate.marginal_cost_per_task_usd == 0
    assert held.results[0].offering.provider == "anthropic"


# ── contract and vocabulary ────────────────────────────────────────────────


def test_the_contract_version_took_the_next_minor() -> None:
    assert c.CONTRACT_VERSION == "2.9"


def test_the_json_schema_publishes_the_estate_types() -> None:
    schema = c.json_schema()
    defs = schema["$defs"]

    for name in ("Estate", "EstateHold", "EstateMark", "EstateResult", "EstateGap",
                 "GainItem", "WithEstate"):
        assert name in defs, name
    assert "estate" in defs["Spec"]["properties"]
    assert "with_estate" in defs["Decision"]["properties"]
    assert "estate" not in defs["Spec"].get("required", [])


def test_the_vocabulary_publishes_the_estate_ids(snapshot) -> None:
    from decision.vocabulary import build_vocabulary

    estate = build_vocabulary(snapshot)["estate"]

    assert "anthropic" in estate["providers"]
    assert "apple_m3_max" in estate["devices"]
    plans = {p["id"]: p for p in estate["plans"]}
    assert plans["anthropic/subscription/pro"]["provider"] == "anthropic"


# ── CLI and Worker ─────────────────────────────────────────────────────────


def _service():
    spec = importlib.util.spec_from_file_location(
        "modelspec_decide_service_estate", ROOT / "api" / "worker" / "src" / "decide_service.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ESTATES = [
    {"providers": ["together-ai"], "devices": ["apple_m3_max"]},
    {"plans": ["anthropic/subscription/pro"], "exhausted": ["anthropic/subscription/pro"]},
    {"providers": ["anthropic"],
     "plans": ["openai/subscription/plus", "anthropic/subscription/pro"]},
]


@pytest.mark.parametrize("estate", ESTATES)
def test_cli_and_worker_return_the_same_bytes_with_an_estate(
    tmp_path, snapshot_bytes, snapshot, estate,
) -> None:
    from cli.modelspec import cli as cli_mod

    service = _service()
    payload = _raw(estate)
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(payload))
    snapshot_path = tmp_path / "snapshot.json.gz"
    snapshot_path.write_bytes(snapshot_bytes)

    result = CliRunner().invoke(
        cli_mod.app,
        ["decide", str(spec_path), "--snapshot-file", str(snapshot_path), "--json"],
        env={"MODELSPEC_SNAPSHOT_KEY": KEY.decode()})
    status, body = service.decide(payload, snapshot)

    assert result.exit_code == 0, result.output
    assert status == 200
    assert body["with_estate"]
    assert result.stdout.encode("utf-8") == service.serialise(body)


def test_the_worker_does_not_log_or_store_the_estate(
    snapshot, caplog, tmp_path, monkeypatch,
) -> None:
    service = _service()
    monkeypatch.chdir(tmp_path)
    marker = ["together-ai"]

    with caplog.at_level(logging.DEBUG):
        status, _ = service.decide(_raw({"providers": marker}), snapshot)

    assert status == 200
    assert "together-ai" not in caplog.text
    assert list(tmp_path.iterdir()) == []


def test_an_invalid_estate_is_a_400_with_the_existing_error_code(snapshot) -> None:
    service = _service()

    status, body = service.decide(_raw({"providers": ["nonesuch"]}), snapshot)

    assert status == 400
    assert body["error"]["code"] == "invalid_spec"
    assert "estate.providers[0]" in json.dumps(body)


def test_a_comparison_ignores_the_estate(snapshot) -> None:
    service = _service()
    plain = {"spec": _raw(), "compare_to": snapshot.snapshot_id}
    held = {"spec": _raw({"providers": ["together-ai"]}), "compare_to": snapshot.snapshot_id}

    assert service.compare(held, snapshot, snapshot) == service.compare(plain, snapshot, snapshot)
