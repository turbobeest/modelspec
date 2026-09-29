"""MODEL-200: plan surfaces, quoted family coverage and allowance, and ``access``.

People decide by how they will use a model. ``access`` picks the routes that
serve that use: plans whose surfaces match, pay-per-use offerings, or
self-hosting. Leaving it out changes nothing.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from decision import contract as c
from decision.bands import BASIS
from decision.contract import SpecError, parse_spec
from decision.engine import decide
from decision.snapshot import build_snapshot, load_snapshot_bytes
from tests.plan_records import (
    CONTEXT,
    MAX,
    NO_ACCESS_SPECS,
    OLD_OPUS,
    OPUS,
    PLUS,
    PRO,
    SONNET,
    inputs,
)

ROOT = Path(__file__).parents[1]
KEY = b"model-200-test-key"
GOLDEN = ROOT / "tests" / "fixtures" / "model-200-no-access.json"


def _load(max_coverage: bool):
    data = build_snapshot(inputs(max_coverage=max_coverage)).to_bytes(key=KEY)
    return data, load_snapshot_bytes(data, key=KEY, source="MODEL-200 test snapshot")


@pytest.fixture(scope="module")
def sourced():
    return _load(True)[1]


@pytest.fixture(scope="module")
def undisclosed():
    return _load(False)[1]


def _decide(snapshot, access=None, estate=None, **over):
    raw = {"spec_version": 1, "optimize": {"max": CONTEXT}, "explain": "none"}
    if access is not None:
        raw["access"] = access
    if estate is not None:
        raw["estate"] = estate
    return decide(parse_spec(raw | over, facets=None), snapshot)


def _rows(results):
    return [(r.offering.model, r.offering.provider) for r in results]


# ── the spec ───────────────────────────────────────────────────────────────


def test_access_takes_the_bare_kind_or_an_object_and_hashes_the_same() -> None:
    bare = parse_spec({"spec_version": 1, "optimize": {"max": CONTEXT},
                       "access": "chat_app"}, facets=None)
    full = parse_spec({"spec_version": 1, "optimize": {"max": CONTEXT},
                       "access": {"kind": "chat_app"}}, facets=None)

    assert bare.access == full.access == c.Access(kind="chat_app")
    assert c.spec_hash(bare) == c.spec_hash(full)
    assert json.loads(c.canonical_json(bare))["access"] == {"kind": "chat_app"}


def test_an_omitted_access_leaves_the_spec_hash_alone() -> None:
    raw = {"spec_version": 1, "optimize": {"max": CONTEXT}}

    assert "access" not in json.loads(c.canonical_json(parse_spec(raw, facets=None)))


@pytest.mark.parametrize("access", [
    {"kind": "chat_app", "harness": "claude-code"},
    {"kind": "own_software", "harness": "claude-code"},
    {"kind": "radio"},
    {"kind": "coding_tool", "harness": "Claude Code"},
])
def test_a_malformed_access_is_refused(access) -> None:
    with pytest.raises(SpecError):
        parse_spec({"spec_version": 1, "optimize": {"max": CONTEXT}, "access": access},
                   facets=None)


def test_an_unregistered_harness_is_refused_with_its_path(sourced) -> None:
    with pytest.raises(SpecError) as caught:
        _decide(sourced, {"kind": "coding_tool", "harness": "nonesuch"})

    assert "access.harness" in str(caught.value)


# ── an omitted access is byte-identical ────────────────────────────────────


def _same_bytes(decision, golden) -> None:
    ours = decision.model_dump(mode="json")
    assert ours["contract_version"] == c.CONTRACT_VERSION
    ours["contract_version"] = golden["contract_version"]
    # 2.7 (MODEL-206) adds the bands and the blend and states the band rule as
    # every answer's basis; the golden predates both.
    ours.pop("bands", None)
    ours.pop("blend", None)
    text = json.dumps(ours, sort_keys=True).replace(
        json.dumps(BASIS), json.dumps("leader-overlap score intervals; "
                                      "capability estimates use 80% intervals"))
    assert text == json.dumps(golden, sort_keys=True)


@pytest.mark.parametrize("index", range(len(NO_ACCESS_SPECS)))
def test_an_omitted_access_reproduces_the_decision_from_before_model_200(
    undisclosed, index,
) -> None:
    golden = json.loads(GOLDEN.read_text())["undisclosed"][index]

    _same_bytes(decide(parse_spec(NO_ACCESS_SPECS[index], facets=None), undisclosed), golden)


@pytest.mark.parametrize("index", range(3))
def test_new_plan_facts_do_not_move_an_answer_without_access(sourced, index) -> None:
    golden = json.loads(GOLDEN.read_text())["sourced_without_estate"][index]

    _same_bytes(decide(parse_spec(NO_ACCESS_SPECS[index], facets=None), sourced), golden)


# ── the Max 20x holder in a coding tool (the ticket's done-when) ───────────


CODING = {"kind": "coding_tool", "harness": "claude-code"}


def test_a_max_holder_in_claude_code_gets_claude_through_the_plan_at_zero(sourced) -> None:
    held = _decide(sourced, CODING, {"plans": [MAX]}).with_estate

    assert _rows(held.results) == [(OPUS, "anthropic"), (SONNET, "anthropic")]
    for row in held.results:
        assert row.estate.via == c.EstateHold(kind="plan", id=MAX)
        assert row.estate.cost_basis == "plan_included"
        assert row.estate.marginal_cost_per_task_usd == 0
    opus = held.results[0].estate.coverage
    assert opus.family == "anthropic/claude-opus"
    assert opus.quote == "Opus and Sonnet models"
    assert OPUS in opus.resolves_to
    assert OLD_OPUS not in opus.resolves_to  # retired: the rule never reaches it
    assert "anthropic/claude-opus-" in opus.rule
    assert held.may_qualify == []


def test_with_todays_null_coverage_the_max_holder_may_qualify_naming_the_fact(
    undisclosed,
) -> None:
    held = _decide(undisclosed, CODING, {"plans": [MAX]}).with_estate

    assert held.results == []
    assert held.status == "no_feasible"
    assert [(m.model, m.unknown) for m in held.may_qualify] == [
        (OPUS, ["offering.subscription.models_covered"]),
        (SONNET, ["offering.subscription.models_covered"]),
    ]


def test_a_plan_whose_surfaces_are_unknown_names_that_fact_too(sourced) -> None:
    held = _decide(sourced, CODING, {"plans": [PLUS]}).with_estate

    assert held.results == []
    assert [(m.model, m.unknown) for m in held.may_qualify] == [(
        "other/huge",
        ["offering.subscription.models_covered", "offering.subscription.surfaces"],
    )]


def test_a_plan_for_another_harness_reaches_nothing(sourced) -> None:
    held = _decide(sourced, {"kind": "coding_tool", "harness": "aider"},
                   {"plans": [MAX]}).with_estate

    assert held.results == [] and held.may_qualify == []


def test_the_plan_beats_the_key_and_exhausting_it_falls_back_to_the_key(sourced) -> None:
    both = _decide(sourced, CODING, {"plans": [MAX], "providers": ["anthropic"]})
    spent = _decide(sourced, CODING, {"plans": [MAX], "providers": ["anthropic"],
                                      "exhausted": [MAX]})

    assert both.with_estate.results[0].estate.via.kind == "plan"
    assert spent.with_estate.results[0].estate.via.kind == "provider"
    assert spent.with_estate.results[0].estate.cost_basis == "list_price"
    assert spent.results == both.results


# ── own software ───────────────────────────────────────────────────────────


def test_own_software_is_pay_per_use_and_warns_about_a_plan_without_api(sourced) -> None:
    decision = _decide(sourced, "own_software", {"plans": [MAX]})
    held = decision.with_estate

    assert held.results == []
    assert held.warnings == ["plan_excludes_own_software"]
    assert sorted(_rows(decision.results)) == [
        (OPUS, "anthropic"), (OPUS, "aws-bedrock"), (SONNET, "anthropic"), ("other/huge", "openai"),
    ]
    # Only the plan whose surfaces include api is a route for own software.
    assert {(r.offering.model, p.plan) for r in decision.results for p in r.plans} == {
        (SONNET, "anthropic/subscription/team-api")}
    with_key = _decide(sourced, "own_software", {"plans": [MAX], "providers": ["anthropic"]})
    assert {r.estate.via.kind for r in with_key.with_estate.results} == {"provider"}


def test_own_software_uses_a_plan_that_covers_the_api(sourced) -> None:
    held = _decide(sourced, "own_software", {"plans": ["anthropic/subscription/team-api"]})

    assert _rows(held.with_estate.results) == [(SONNET, "anthropic")]
    assert held.with_estate.warnings == []
    sonnet = next(r for r in held.results if r.offering == held.with_estate.results[0].offering)
    assert [p.plan for p in sonnet.plans] == ["anthropic/subscription/team-api"]
    assert sonnet.plans[0].coverage.family is None
    assert sonnet.plans[0].coverage.resolves_to == [SONNET]


# ── break-even ─────────────────────────────────────────────────────────────


def test_a_coding_tool_answer_carries_both_routes_and_the_break_even(sourced) -> None:
    decision = _decide(sourced, CODING)
    opus = next(r for r in decision.results if r.offering.provider == "anthropic"
                and r.offering.model == OPUS)
    bedrock = next(r for r in decision.results if r.offering.provider == "aws-bedrock")

    assert opus.cost_per_task == pytest.approx(15.0 * 44_000 / 1_000_000)
    [route] = opus.plans
    assert route.plan == MAX
    assert route.surface == "coding_tool:claude-code"
    assert route.price == c.PlanPrice(amount=200, currency="USD", period="monthly")
    assert route.price_monthly_usd == 200
    assert route.break_even_tasks_per_month == pytest.approx(round(200 / 0.66, 1))
    assert "303" in route.basis
    assert "allowance in tokens is not published" in route.basis
    assert route.allowance == c.PlanAllowance(relative_to=PRO, multiplier=20)
    assert bedrock.plans == []  # a plan never reaches another provider's offering
    sonnet = next(r for r in decision.results if r.offering.model == SONNET)
    assert [p.plan for p in sonnet.plans] == [PRO, MAX]  # cheapest first


def test_a_plan_without_a_price_has_no_break_even_and_says_why(sourced) -> None:
    decision = _decide(sourced, "own_software")
    sonnet = next(r for r in decision.results if r.offering.model == SONNET)

    [route] = sonnet.plans
    assert route.break_even_tasks_per_month is None
    assert route.price is None
    assert "does not publish a price" not in route.basis  # own software: no break-even at all
    coding = _decide(sourced, {"kind": "coding_tool"})
    assert all(p.plan != "anthropic/subscription/team-api"
               for r in coding.results for p in r.plans)


def test_break_even_is_labelled_when_the_price_is_unknown(undisclosed) -> None:
    from decision.contract import Access
    from decision.plans import load_plans, route

    plan = load_plans(undisclosed)["anthropic/subscription/team-api"]
    made = route(plan, "api", plan.coverage[0], Access(kind="coding_tool"), 0.5, "x")

    assert made.break_even_tasks_per_month is None
    assert "does not publish a price" in made.basis


# ── chat app ───────────────────────────────────────────────────────────────


def test_a_chat_app_ranks_on_capability_with_no_per_task_cost(sourced) -> None:
    decision = _decide(sourced, "chat_app")

    assert sorted(_rows(decision.results)) == [(OPUS, "anthropic"), (SONNET, "anthropic")]
    for row in decision.results:
        assert row.cost_per_task is None
        assert all(p.break_even_tasks_per_month is None for p in row.plans)
        assert all(p.surface == "chat_app" for p in row.plans)
    assert [(m.model, m.unknown) for m in decision.may_qualify] == [(
        "other/huge",
        ["offering.subscription.models_covered", "offering.subscription.surfaces"],
    )]


def test_a_chat_app_breaks_a_tie_on_the_cheapest_plan(sourced) -> None:
    decision = _decide(sourced, "chat_app")

    assert decision.answer.kind == "tied"
    assert decision.answer.tie_breakers.cheapest == SONNET


def test_plan_price_is_a_where_filter(sourced) -> None:
    decision = _decide(sourced, "chat_app", where=["offering.plan.price_monthly <= 50"])

    assert _rows(decision.results) == [(SONNET, "anthropic")]
    assert decision.results[0].plans[0].plan == PRO


# ── own hardware ───────────────────────────────────────────────────────────


def test_own_hardware_ranks_self_hosting_only(sourced) -> None:
    decision = _decide(sourced, "own_hardware")

    assert _rows(decision.results) == [("acme/tiny", None)]
    assert [(m.model, m.unknown) for m in decision.may_qualify] == [
        ("acme/unfit", ["model.fits_hardware"])]
    held = _decide(sourced, "own_hardware", {"devices": ["apple_m3_max"], "plans": [MAX]})
    assert _rows(held.with_estate.results) == [("acme/tiny", None)]


# ── the plan records ───────────────────────────────────────────────────────


def test_repository_plans_carry_the_new_facts_from_sourced_text_only() -> None:
    from decision.model import load_subscription_offerings
    from decision.registry import default

    plans = {
        plan.id: {fact.facet: fact for fact in plan.facts}
        for path in sorted((ROOT / "offerings" / "subscriptions").glob("*.yaml"))
        for plan in load_subscription_offerings(path, registry=default())
    }
    surfaces = plans[MAX]["offering.subscription.surfaces"]
    assert surfaces.value == ["chat_app", "coding_tool:claude-code", "desktop_app", "mobile_app"]
    assert surfaces.sources == plans[MAX]["offering.subscription.programmatic_or_agent_use"].sources
    assert plans[MAX]["offering.subscription.allowance.multiplier"].value == 20
    assert plans[MAX]["offering.subscription.allowance.relative_to"].value == PRO
    for plan in plans.values():
        # Nothing new was researched: family coverage and tokens wait for MODEL-201.
        for facet in ("families_covered", "coverage_quote", "allowance.tokens",
                      "allowance.window"):
            assert plan["offering.subscription." + facet].state == "unknown"
        # Every known new fact cites a source an existing fact of the plan already cites.
        cited = {s.source_id for f in plan.values() if not f.facet.startswith(
            ("offering.subscription.surfaces", "offering.subscription.allowance."))
            for s in f.sources}
        for fact in plan.values():
            if fact.state == "known":
                assert {s.source_id for s in fact.sources} <= cited, fact.id


def test_a_family_resolves_only_within_its_prefix() -> None:
    from decision.registry import default

    families = {f.id: f for f in default().families()}

    assert families["anthropic/claude-opus"].resolves(OPUS)
    assert not families["anthropic/claude-opus"].resolves(SONNET)
    for family in families.values():
        assert family.prefix.startswith(family.id.partition("/")[0] + "/")


def test_the_vocabulary_publishes_each_plan_record(sourced) -> None:
    from decision.vocabulary import build_vocabulary

    plans = {p["id"]: p for p in build_vocabulary(sourced)["estate"]["plans"]}
    record = plans[MAX]

    assert record["price"] == {"amount": 200.0, "currency": "USD", "period": "monthly"}
    assert record["surfaces"] == ["chat_app", "coding_tool:claude-code", "desktop_app",
                                  "mobile_app"]
    assert record["coverage"][0]["family"] == "anthropic/claude-opus"
    assert OPUS in record["coverage"][0]["resolves_to"]
    assert record["allowance"] == {"relative_to": PRO, "multiplier": 20.0, "window": None,
                                   "tokens": None}
    assert plans[PLUS]["surfaces"] is None and plans[PLUS]["coverage"] is None


def test_the_contract_took_the_next_minor_and_publishes_the_plan_types() -> None:
    assert c.CONTRACT_VERSION == "2.7"
    defs = c.json_schema()["$defs"]
    for name in ("Access", "PlanRoute", "PlanCoverage", "PlanPrice", "PlanAllowance"):
        assert name in defs, name
    assert "access" in defs["Spec"]["properties"]
    assert "access" not in defs["Spec"].get("required", [])


# ── CLI and Worker ─────────────────────────────────────────────────────────


def _service():
    spec = importlib.util.spec_from_file_location(
        "modelspec_decide_service_plans", ROOT / "api" / "worker" / "src" / "decide_service.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("access, estate", [
    (CODING, {"plans": [MAX]}),
    ("chat_app", None),
    ("own_software", {"plans": [MAX], "providers": ["anthropic"]}),
    ("own_hardware", {"devices": ["apple_m3_max"]}),
])
def test_cli_and_worker_return_the_same_bytes_with_an_access(tmp_path, access, estate) -> None:
    from cli.modelspec import cli as cli_mod

    data, snapshot = _load(True)
    service = _service()
    payload = {"spec_version": 1, "optimize": {"max": CONTEXT}, "explain": "summary",
               "access": access}
    if estate is not None:
        payload["estate"] = estate
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(payload))
    snapshot_path = tmp_path / "snapshot.json.gz"
    snapshot_path.write_bytes(data)

    result = CliRunner().invoke(
        cli_mod.app,
        ["decide", str(spec_path), "--snapshot-file", str(snapshot_path), "--json"],
        env={"MODELSPEC_SNAPSHOT_KEY": KEY.decode()})
    status, body = service.decide(payload, snapshot)

    assert result.exit_code == 0, result.output
    assert status == 200
    assert result.stdout.encode("utf-8") == service.serialise(body)


def test_an_unregistered_harness_is_a_400_with_the_existing_error_code(sourced) -> None:
    status, body = _service().decide(
        {"spec_version": 1, "optimize": {"max": CONTEXT},
         "access": {"kind": "coding_tool", "harness": "nonesuch"}}, sourced)

    assert status == 400
    assert body["error"]["code"] == "invalid_spec"
    assert "access.harness" in json.dumps(body)


# ── the Worker's pydantic ──────────────────────────────────────────────────


def test_the_contract_drops_what_exclude_if_drops_on_any_pydantic(undisclosed) -> None:
    """The Worker runs Pyodide's pydantic 2.10.6, which ignores ``exclude_if``
    and emitted ``plans: []`` on every result. ``apply_exclude_if`` is what
    ``_Strict`` falls back to there; CI also runs this file under that version."""
    decision = decide(parse_spec(NO_ACCESS_SPECS[3], facets=None), undisclosed)
    result = decision.results[0]
    held = decision.with_estate

    native = result.model_dump(mode="json")
    assert "plans" not in native
    assert c.apply_exclude_if(result, native | {"plans": []}) == native
    native = held.model_dump(mode="json")
    assert "warnings" not in native
    assert c.apply_exclude_if(held, native | {"warnings": []}) == native
    mark = held.results[0].estate if held.results else None
    if mark is not None:
        native = mark.model_dump(mode="json")
        assert c.apply_exclude_if(mark, native | {"coverage": None}) == native


def test_an_exhausted_plan_raises_no_own_software_warning(sourced) -> None:
    spent = _decide(sourced, "own_software", {"plans": [MAX], "exhausted": [MAX]})

    assert spent.with_estate.warnings == []
