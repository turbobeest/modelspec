"""What an agent reads before calling ModelSpec, held to one source (MODEL-257)."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path

import pytest
import yaml

from pipeline import agent_copy, agent_ready, entity, worker_flags
from pipeline.export import Build

ROOT = Path(__file__).resolve().parents[1]
SERVER = (ROOT / "mcp" / "src" / "server.ts").read_text(encoding="utf-8")
COMMITTED = json.loads(agent_copy.OUT.read_text(encoding="utf-8"))
TIERS = json.loads(agent_copy.TIERS.read_text(encoding="utf-8"))
PAID = {"decide": "decide", "rank": "rank", "policy_check": "policy-check"}
DATA_TOOLS = (*PAID, "vocab", "model_info", "list_use_cases")


def test_the_committed_copy_is_what_the_registry_and_tiers_generate() -> None:
    assert agent_copy.OUT.read_text(encoding="utf-8") == agent_copy.render(agent_copy.copy()), (
        "mcp/src/agent-copy.json is stale or hand-edited: run python -m pipeline.agent_copy write")


def test_the_cli_bundle_and_schemas_are_generated_from_the_published_sources() -> None:
    bundle = json.loads(agent_copy.CLI_OUT.read_text(encoding="utf-8"))
    assert bundle["text"] == agent_copy.cli_text()
    assert bundle["clients"] == agent_copy.cli_clients()
    assert bundle["entity"] == entity.ONE_SENTENCE
    assert bundle["guide_version"] == COMMITTED["guide_version"]
    for relative, expected in bundle["source_hashes"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected, relative
    assert json.loads(agent_copy.CLI_SCHEMA.read_text()) == agent_copy.cli_spec_schema()
    assert agent_copy.CLI_FEEDBACK_SCHEMA.read_bytes() == (
        ROOT / "schemas/feedback-v1.schema.json").read_bytes()


def test_every_mcp_tool_description_and_the_instructions_come_from_the_copy() -> None:
    registered = re.findall(r'server\.registerTool\(\s*"(\w+)",\s*\{\s*description:\s*([^\n]+)', SERVER)
    assert sorted(name for name, _ in registered) == sorted(agent_ready.MCP_TOOLS)
    for name, expression in registered:
        assert expression.strip() == f"agentCopy.tools.{name},", (name, expression)
    assert "{ instructions: agentCopy.instructions }" in SERVER
    assert set(COMMITTED["tools"]) == set(agent_ready.MCP_TOOLS) == set(COMMITTED["card"])


def test_the_summary_rule_is_on_the_channels_an_agent_already_trusts() -> None:
    rule = agent_copy.SUMMARY_RULE
    assert rule == (
        "Present `summary_for_user` to the user unchanged and keep every `must_mention` item."
    )
    assert len(agent_copy.CONDUCT_RULES) == 8
    assert rule not in agent_copy.CONDUCT_RULES
    data = agent_copy.copy()
    guide = agent_copy.guide()[1]
    bundle = json.loads(agent_copy.CLI_OUT.read_text(encoding="utf-8"))
    assert data["instructions"].count(rule) == 1
    assert data["tools"]["decide"].count(rule) == 1
    assert data["tools"]["rank"].count(rule) == 1
    assert rule not in data["tools"]["policy_check"]
    assert rule not in data["tools"]["vocab"]
    assert agent_copy.cli_text()["answers"].count(rule) == 1
    assert guide.count(rule) == 1
    assert COMMITTED["instructions"].count(rule) == 1
    assert COMMITTED["tools"]["decide"].count(rule) == 1
    assert COMMITTED["tools"]["rank"].count(rule) == 1
    assert agent_copy.GUIDE_OUT.read_text(encoding="utf-8").count(rule) == 1
    assert bundle["text"]["answers"].count(rule) == 1


def test_the_instructions_open_with_the_entity_sentence_and_the_disambiguation() -> None:
    assert COMMITTED["instructions"].startswith(f"{entity.ONE_SENTENCE} {entity.DISAMBIGUATION}")


def test_each_paid_tool_says_the_question_the_return_the_key_and_price_and_when_not() -> None:
    for name in PAID:
        text = COMMITTED["tools"][name]
        question = text.split("? ", 1)[0] if name != "rank" else text.split(". ", 1)[1].split("? ", 1)[0]
        assert question and "?" not in question, name  # a question leads the description
        assert "Returns" in text, name
        assert "Needs an API key (Authorization: Bearer)." in text, name
        assert re.search(r"Not a router|Don't call it|doesn't choose a model", text), name


def test_each_data_tool_requires_a_key_and_only_feedback_is_keyless() -> None:
    for name in DATA_TOOLS:
        text = COMMITTED["tools"][name]
        assert "Needs an API key" in text, name
        assert "key" in COMMITTED["card"][name].lower(), name
        assert "free" not in COMMITTED["card"][name].lower(), name
        assert "Free, no key" not in text, name
    assert "Free, no key" in COMMITTED["tools"]["feedback"]
    assert "no Authorization header is forwarded" in COMMITTED["tools"]["feedback"]
    assert "Machine data access needs a ModelSpec API key" in COMMITTED["instructions"]


@pytest.mark.parametrize("billing", [False, True])
def test_procurement_copy_reads_production_billing_flag(tmp_path, monkeypatch, billing) -> None:
    config = tmp_path / worker_flags.WRANGLER_REL
    config.parent.mkdir(parents=True)
    config.write_text(json.dumps({
        "vars": {"BILLING_ENABLED": str(billing).lower()},
        "env": {"staging": {"vars": {"BILLING_ENABLED": str(not billing).lower()}}},
    }))
    expected = ("Buy a plan or pack at https://modelspec.dev/pricing/. "
                "Stripe hosts Checkout; claim your key at the success link."
                if billing else
                "Use an existing key, or see https://modelspec.dev/pricing/ for availability.")
    assert agent_copy.key_procurement(tmp_path) == expected
    assert expected in agent_copy.cli_text(tmp_path)["procurement"]
    assert expected in agent_ready.auth_markdown(tmp_path)
    build = Build(commit="test", built_at="2026-10-03T00:00:00Z", as_of=date(2026, 10, 3))
    assert expected in agent_ready.modelspec_landing_markdown([], [], build, root=tmp_path)
    assert expected in agent_ready.skill_markdown(tmp_path)
    monkeypatch.setattr(agent_copy, "key_procurement", lambda: expected)
    assert expected in agent_copy.guide_body(TIERS)
    if not billing:
        assert "Get a key at" not in agent_copy.guide_body(TIERS)


def test_prices_in_the_descriptions_are_the_ones_in_tiers_json() -> None:
    weights = TIERS["credits"]["weights"]
    low, high = agent_copy.credit_usd_range(TIERS)
    expected_credits = {
        "decide": sorted({weights["decide.none"], weights["decide.summary"], weights["decide.full"]}),
        "rank": [weights["rank"]],
        "policy_check": [weights["policy-check"]],
    }
    for name, credits in expected_credits.items():
        text = COMMITTED["tools"][name]
        stated = re.search(r"Costs ([\d ora]+) credits? a call", text).group(1)
        assert [int(n) for n in stated.split(" or ")] == credits, name
        assert f"{agent_copy._usd(low)}–{agent_copy._usd(high)}" in text, name
        assert "¢" not in text, name
    assert (low, high) == (min(p["usd"] / p["credits"] for p in TIERS["billing"]["prices"].values()
                               if not p.get("placeholder")),
                           max(p["usd"] / p["credits"] for p in TIERS["billing"]["prices"].values()
                               if not p.get("placeholder")))


def test_no_switched_off_payment_rail_is_mentioned() -> None:
    everything = json.dumps(COMMITTED).lower()
    for phrase in ("x402", "bazaar", "402 payment", "without an api key", "pay per call"):
        assert phrase not in everything, phrase


def test_rank_is_marked_legacy_and_points_to_decide() -> None:
    assert COMMITTED["tools"]["rank"].startswith("Legacy v1; use decide")
    assert "use decide" in COMMITTED["card"]["rank"]


def test_card_lines_fit_and_the_card_serves_them() -> None:
    card = agent_ready.mcp_card()
    assert [t["description"] for t in card["tools"]] == [COMMITTED["card"][n] for n in agent_ready.MCP_TOOLS]
    assert all(len(line) <= 100 for line in COMMITTED["card"].values())


def test_the_published_openapi_operations_lead_with_the_copy() -> None:
    spec = yaml.safe_load((ROOT / "api" / "worker" / "openapi.yaml").read_text(encoding="utf-8"))
    for path, key in {"/v1/decide": "decide", "/v1/rank": "rank",
                      "/v1/policy-check": "policyCheck", "/v1/feedback": "feedback"}.items():
        operation = spec["paths"][path]["post"]
        assert operation["summary"] == COMMITTED["openapi"][key]["summary"], path
        assert operation["description"].startswith(COMMITTED["openapi"][key]["lead"]), path
        assert "¢" not in operation["description"], path
