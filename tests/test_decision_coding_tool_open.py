"""MODEL-210: an open-ended coding-tool list (``coding_tool:*``).

A plan page that says the coding tools it works with are an open list ("such
as …", "More tools") records ``coding_tool:*``. The quote of that wording is
``offering.subscription.coding_tools_quote``. A harness the page also names is
confirmed. Any other harness still routes, labelled as not named by the
provider, and is never called confirmed.
"""

from __future__ import annotations

from decision import contract as c
from decision.contract import parse_spec
from decision.engine import decide
from decision.registry import default
from decision.snapshot import SnapshotInputs, build_snapshot, load_snapshot_bytes
from tests.plan_records import CONTEXT
from tests.snapshot_records import SOURCES, fact, model, offering, subscription

KEY = b"model-210-test-key"
GLM = "zai/glm-4-6"
PLAN = "zai/subscription/glm-coding"
QUOTE = "Claude Code, Cline, and other coding tools"
OPEN = "coding_tool:*"
NAMED = {"kind": "coding_tool", "harness": "claude-code"}
UNLISTED = {"kind": "coding_tool", "harness": "aider"}


def _plan() -> dict:
    row = subscription("zai", "glm-coding")
    row["name"] = "GLM Coding"

    def put(facet: str, value) -> None:
        full = "offering.subscription." + facet
        row["facts"] = [item for item in row["facts"] if item["facet"] != full]
        row["facts"].append(fact("offering", PLAN, full, value, source="src-pricing"))

    put("models_covered", [GLM])
    put("surfaces", ["coding_tool:claude-code", OPEN])
    put("coding_tools_quote", QUOTE)
    return row


def _snapshot():
    built = build_snapshot(SnapshotInputs(
        models=[model(GLM, facts=[
            fact("model", GLM, CONTEXT, 200_000),
            fact("model", GLM, "model.weights_openness", "closed_weights"),
        ])],
        offerings=[offering(GLM, "zai", price=1.0)],
        sources=SOURCES,
        subscriptions=[_plan()],
    ), registry=default())
    return load_snapshot_bytes(built.to_bytes(key=KEY), key=KEY, source="MODEL-210 test snapshot")


def _decide(snapshot, access, estate=None):
    raw = {"spec_version": 1, "optimize": {"max": CONTEXT}, "explain": "none", "access": access}
    if estate is not None:
        raw["estate"] = estate
    return decide(parse_spec(raw, facets=None), snapshot)


def _held(snapshot, access):
    decision = _decide(snapshot, access, {"plans": [PLAN]})
    row = next(r for r in decision.with_estate.results if r.offering.model == GLM)
    route = next(p for r in decision.results if r.offering.model == GLM
                 for p in r.plans if p.plan == PLAN)
    return row, route


def test_an_open_list_is_a_legal_plan_fact() -> None:
    from decision.model import SubscriptionOffering

    SubscriptionOffering.model_validate(_plan(), context={"registry": default()})


def test_coding_tool_star_is_a_registry_surface_and_the_answer_field_stays_a_string() -> None:
    registry = default()
    allowed = registry.allowed_values(registry.facet("offering.subscription.surfaces"))

    assert OPEN in allowed
    surface = c.json_schema()["$defs"]["PlanRoute"]["properties"]["surface"]
    assert surface["type"] == "string"
    assert "enum" not in surface


def test_a_glm_coding_holder_is_confirmed_for_a_named_harness() -> None:
    row, route = _held(_snapshot(), NAMED)

    assert row.offering.model == GLM
    assert row.estate.via == c.EstateHold(kind="plan", id=PLAN)
    assert route.surface == "coding_tool:claude-code"
    assert "confirmed" in row.estate.coverage.rule
    assert "confirmed" in route.basis
    assert "tool not named" not in row.estate.coverage.rule
    assert "tool not named" not in route.basis


def test_a_glm_coding_holder_is_not_named_for_an_unlisted_harness() -> None:
    row, route = _held(_snapshot(), UNLISTED)

    assert row.offering.model == GLM
    assert route.surface == OPEN
    for text in (row.estate.coverage.rule, route.basis):
        assert "tool not named by the provider" in text
        assert f"provider lists tools such as {QUOTE}; your tool isn't named" in text
        assert "confirmed" not in text


def test_an_open_list_routes_for_bare_coding_tool_without_a_tool_verdict() -> None:
    row, route = _held(_snapshot(), "coding_tool")

    assert row.offering.model == GLM
    assert route.surface == OPEN
    assert "tool not named" not in route.basis
    assert "confirmed" not in route.basis


def test_an_open_coding_tool_list_does_not_serve_another_access() -> None:
    snapshot = _snapshot()

    for access in ("chat_app", "own_software", "own_hardware"):
        held = _decide(snapshot, access, {"plans": [PLAN]}).with_estate
        assert held.results == [], access
