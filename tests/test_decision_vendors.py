"""MODEL-205: subscription-only vendors (Cursor, GitHub Copilot, Perplexity).

A vendor sells plans and nothing else. Its plan reaches the lab models it is
documented to cover, through its own tool, and the vendor never appears as a
pay-per-use route: it owns no metered offering and ``estate.providers``
refuses it.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from decision import contract as c
from decision.contract import SpecError, parse_spec
from decision.engine import decide
from decision.registry import RegistryError, UnknownIdError, default, load
from decision.snapshot import build_snapshot, load_snapshot_bytes
from tests.plan_records import CONTEXT, CURSOR_COVERS, CURSOR_PRO, MAX, OPUS, vendor_inputs

ROOT = Path(__file__).parents[1]
KEY = b"model-205-test-key"
CURSOR = {"kind": "coding_tool", "harness": "cursor"}


@pytest.fixture(scope="module")
def snapshot():
    data = build_snapshot(vendor_inputs()).to_bytes(key=KEY)
    return load_snapshot_bytes(data, key=KEY, source="MODEL-205 test snapshot")


def _decide(snapshot, access=None, estate=None):
    raw = {"spec_version": 1, "optimize": {"max": CONTEXT}, "explain": "none"}
    if access is not None:
        raw["access"] = access
    if estate is not None:
        raw["estate"] = estate
    return decide(parse_spec(raw, facets=None), snapshot)


def _cursor_rows(results):
    return [(r.offering.model, r.offering.provider) for r in results
            if any(p.plan == CURSOR_PRO for p in getattr(r, "plans", ()))]


# ── the registry ───────────────────────────────────────────────────────────


def test_a_vendor_owns_plans_but_is_never_a_provider() -> None:
    registry = default()

    assert {v.id for v in registry.vendors()} >= {"cursor", "github-copilot", "perplexity"}
    assert registry.plan_owner("cursor").name == "Cursor"
    assert registry.plan_owner("anthropic").id == "anthropic"
    with pytest.raises(UnknownIdError, match="unknown provider 'cursor'"):
        registry.provider("cursor")
    assert "cursor" not in {p.id for p in registry.providers()}


def test_the_vendors_own_tools_are_registered_harnesses() -> None:
    harnesses = {h.id for h in default().harnesses()}

    assert {"cursor", "cursor-agent", "copilot-cli"} <= harnesses


def _registry_copy(tmp_path: Path, vendors: str) -> Path:
    root = tmp_path / "registry"
    shutil.copytree(ROOT / "registry", root)
    text = (root / "providers.yaml").read_text(encoding="utf-8")
    text = text[: text.index("subscription_vendors:")] + vendors
    (root / "providers.yaml").write_text(text, encoding="utf-8")
    return root


def test_a_vendor_may_not_reuse_a_provider_id(tmp_path) -> None:
    root = _registry_copy(tmp_path, "subscription_vendors:\n"
                          "  - {id: anthropic, name: Anthropic, url: 'https://anthropic.com/'}\n")

    with pytest.raises(RegistryError, match="id is already a provider"):
        load(root)


def test_a_vendor_needs_an_https_url_and_no_unknown_fields(tmp_path) -> None:
    root = _registry_copy(tmp_path, "subscription_vendors:\n"
                          "  - {id: acme, name: Acme, url: 'http://acme.test/', kind: cloud}\n")

    with pytest.raises(RegistryError) as raised:
        load(root)
    assert "url must be an https URL" in str(raised.value)
    assert "unknown field 'kind'" in str(raised.value)


def test_a_providers_document_without_vendors_has_none(tmp_path) -> None:
    assert load(_registry_copy(tmp_path, "")).vendors() == ()


# ── the records ────────────────────────────────────────────────────────────


def test_a_vendor_may_sell_a_plan_but_never_a_metered_offering() -> None:
    from decision.model import Offering, SubscriptionOffering

    [plan] = vendor_inputs().subscriptions[-1:]
    SubscriptionOffering.model_validate(plan, context={"registry": default()})

    metered = next(o for o in vendor_inputs().offerings if o["provider"] == "anthropic")
    with pytest.raises(ValueError, match="unknown provider ID: cursor"):
        Offering.model_validate({**metered, "provider": "cursor"},
                                context={"registry": default()})


# ── the decision ───────────────────────────────────────────────────────────


@pytest.mark.parametrize("access", [{"kind": "coding_tool"}, CURSOR])
def test_a_cursor_pro_holder_in_a_coding_tool_gets_the_models_cursor_covers(
    snapshot, access,
) -> None:
    held = _decide(snapshot, access, {"plans": [CURSOR_PRO]}).with_estate

    assert sorted(r.offering.model for r in held.results) == sorted(CURSOR_COVERS)
    for row in held.results:
        assert row.offering.provider is None  # the model's own row, not a Cursor offering
        assert row.estate.via == c.EstateHold(kind="plan", id=CURSOR_PRO)
        assert row.estate.cost_basis == "plan_included"
        assert row.estate.marginal_cost_per_task_usd == 0
        assert row.estate.coverage.resolves_to == sorted(CURSOR_COVERS)
    assert held.may_qualify == []


def test_cursor_never_appears_as_a_pay_per_use_offering(snapshot) -> None:
    for access in ({"kind": "coding_tool"}, CURSOR, "own_software", "chat_app", None):
        decision = _decide(snapshot, access, {"plans": [CURSOR_PRO]})
        rows = [*decision.results, *decision.with_estate.results]
        assert all(r.offering.provider != "cursor" for r in rows), access
        assert all(g.add.id != "cursor" for g in decision.with_estate.gain), access


def test_the_unrestricted_coding_answer_lists_cursor_on_each_models_own_row(snapshot) -> None:
    decision = _decide(snapshot, CURSOR)

    assert sorted(_cursor_rows(decision.results)) == sorted(
        (model, None) for model in CURSOR_COVERS)
    opus = next(r for r in decision.results
                if r.offering.model == OPUS and r.offering.provider is None)
    [route] = opus.plans
    assert route.surface == "coding_tool:cursor"
    assert route.price == c.PlanPrice(amount=20, currency="USD", period="monthly")
    assert route.break_even_tasks_per_month is None
    assert route.basis == (
        f"Cursor Pro reaches {OPUS} directly, not through a pay-per-use offering, so no "
        "break-even is computed; each pay-per-use offering of it is a result of its own.")
    # The lab's own pay-per-use row stays a result of its own, without the plan.
    anthropic = next(r for r in decision.results
                     if r.offering.model == OPUS and r.offering.provider == "anthropic")
    assert all(p.plan != CURSOR_PRO for p in anthropic.plans)


def test_a_cursor_plan_serves_no_other_access(snapshot) -> None:
    for access in ({"kind": "coding_tool", "harness": "claude-code"}, "chat_app",
                   "own_software", "own_hardware"):
        decision = _decide(snapshot, access, {"plans": [CURSOR_PRO]})
        assert decision.with_estate.results == [], access
        assert _cursor_rows(decision.results) == [], access


def test_a_vendor_is_refused_as_a_pay_per_use_key(snapshot) -> None:
    with pytest.raises(SpecError) as raised:
        _decide(snapshot, CURSOR, {"providers": ["cursor"]})

    [issue] = raised.value.issues
    assert issue.path == "estate.providers[0]"
    assert "sells subscription plans only" in issue.reason


def test_exhausting_the_vendor_removes_its_plans(snapshot) -> None:
    spent = _decide(snapshot, CURSOR, {"plans": [CURSOR_PRO, MAX], "exhausted": ["cursor"]})

    assert spent.with_estate.results == []


def test_the_vocabulary_names_vendors_apart_from_providers(snapshot) -> None:
    from decision.vocabulary import build_vocabulary

    vocabulary = build_vocabulary(snapshot)

    assert vocabulary["vendors"]["cursor"] == "Cursor"
    assert "cursor" not in vocabulary["providers"]
    assert "cursor" not in vocabulary["estate"]["providers"]
    plan = next(p for p in vocabulary["estate"]["plans"] if p["id"] == CURSOR_PRO)
    assert plan["provider"] == "cursor"
    assert plan["surfaces"] == ["coding_tool:cursor", "coding_tool:cursor-agent"]


# ── the repository's vendor plans ──────────────────────────────────────────


def _repository_plans():
    from decision.model import load_subscription_offerings

    vendors = {v.id for v in default().vendors()}
    return {plan.id: {fact.facet: fact for fact in plan.facts}
            for path in sorted((ROOT / "offerings" / "subscriptions").glob("*.yaml"))
            for plan in load_subscription_offerings(path, registry=default())
            if plan.provider in vendors}


def test_the_repository_records_each_vendors_plans_through_its_own_tool() -> None:
    plans = _repository_plans()

    assert sorted(plans) == [
        "cursor/subscription/pro", "cursor/subscription/pro-plus",
        "cursor/subscription/teams-premium", "cursor/subscription/teams-standard",
        "cursor/subscription/ultra",
        "github-copilot/subscription/business", "github-copilot/subscription/enterprise",
        "github-copilot/subscription/max", "github-copilot/subscription/pro",
        "github-copilot/subscription/pro-plus",
        "perplexity/subscription/max", "perplexity/subscription/pro",
    ]
    tool = {"cursor": ["coding_tool:cursor"], "github-copilot": ["coding_tool:copilot-cli"],
            "perplexity": ["chat_app"]}
    for plan_id, facts in plans.items():
        assert facts["offering.subscription.surfaces"].value == tool[plan_id.split("/")[0]]
        for fact in facts.values():
            assert fact.state != "known" or fact.sources, fact.id
    pro = plans["cursor/subscription/pro"]
    assert pro["offering.subscription.price"].value == 20
    assert "anthropic/claude-opus-5-5" in pro["offering.subscription.models_covered"].value
    premium = plans["cursor/subscription/teams-premium"]
    assert premium["offering.subscription.allowance.relative_to"].value == (
        "cursor/subscription/teams-standard")
    assert premium["offering.subscription.allowance.multiplier"].value == 5
    copilot_pro = plans["github-copilot/subscription/pro"]["offering.subscription.models_covered"]
    assert "anthropic/claude-sonnet-4-6" in copilot_pro.value
    assert "anthropic/claude-opus-5-5" not in copilot_pro.value  # "Not included" on Pro
    # The page gives only a monthly equivalent of an annual price.
    assert plans["perplexity/subscription/pro"]["offering.subscription.price"].state == "unknown"


def test_no_repository_offering_is_sold_by_a_vendor() -> None:
    vendors = {v.id for v in default().vendors()}

    assert not [p for p in (ROOT / "offerings").iterdir() if p.name in vendors]
