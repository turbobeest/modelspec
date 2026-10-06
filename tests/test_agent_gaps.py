"""MODEL-300: cross-family evaluation and exact first requests, entirely offline."""
from __future__ import annotations

import copy
import json

import httpx
import pytest
import yaml

from api.worker.src.display_vocabulary import SECTIONS, lookup
from decision.contract import parse_spec
from decision.registry import default
from pipeline import agent_copy
from qa import agent_harness as harness
from qa.contracts import capture_tools
from qa.providers import Budget, HttpAgent, KEY_ENV, Reply, first_request
from qa.tools import LiveTools, tool_result


@pytest.fixture
def config():
    return yaml.safe_load((harness.HERE / "config.yaml").read_text())


def opinion(passed=True, models=()):
    return {"passed": passed, "rationale": "Public fixture judgement.", "top_models": list(models),
            "answer_kind": "abstain" if not models else "single" if len(models) == 1 else "tied",
            "missing_capabilities": []}


def saved_report():
    evidence = tool_result({"origin": "https://staging.example/v1/decide", "status": 200,
                            "body": {"status": "partial", "answer": {"kind": "none", "members": []}}})
    row = {"scenario": "prompt-code", "family": "F2", "agent": "openai", "model": "gpt-6.1-sol",
           "status": "completed", "final_answer": "The evidence cannot select a model for this exact prompt.",
           "tool_calls": [{"id": "c1", "name": "decide", "arguments": agent_copy.MINIMAL_SPEC,
                           "turn": 1, "response_ref": "r1", "unknown_facets": [], "validation_errors": [],
                           "api_call": True, "latency_ms": 5}],
           "model_calls": [{"role": "agent", "model": "gpt-6.1-sol", "tokens_in": 100,
                            "tokens_out": 10, "cost_usd": 0.001},
                           {"role": "judge", "model": "old-judge", "tokens_in": 999,
                            "tokens_out": 99, "cost_usd": 0.1}],
           "judge": {"model": "old-judge", **opinion(False)}, "success": False,
           "expected_match": None, "tokens_in": 1099, "tokens_out": 109, "estimated_cost_usd": 0.101}
    return {"report_date": "2026-10-03", "metadata": {"interface": "mcp"},
            "runs": [row], "tool_responses": {"r1": evidence}}


@pytest.mark.parametrize("family,expected", [("openai", "claude"), ("claude", "openai"), ("gemini", "openai")])
def test_default_judges_use_a_different_family(config, family, expected):
    harness.validate_config(config)
    profiles = harness.judge_profiles(config, family)
    assert [p["family"] for p in profiles] == [expected]
    assert profiles[0]["model"] == config["agents"][expected]["model"]


@pytest.mark.parametrize("route", [["openai"], ["claude", "claude"], ["claude", "openai"], ["unsupported"]])
def test_self_judging_duplicate_and_invalid_routes_are_refused(config, route):
    config["judge"]["routes"]["openai"] = route
    if len(route) == 2:
        config["judge"]["mode"] = "panel"
    with pytest.raises(ValueError, match="other families"):
        harness.validate_config(config)


@pytest.mark.parametrize("votes,passed,agreed", [
    ([opinion(), opinion()], True, True),
    ([opinion(), opinion(False)], False, False),
    ([opinion(False), opinion(False)], False, True),
    ([opinion(models=("lab/a",)), opinion(models=("lab/b",))], False, False),
    ([opinion(models=("lab/a", "lab/b")), opinion(models=("lab/b", "lab/a"))], True, True),
])
def test_panel_requires_verdict_and_recommendation_agreement(config, votes, passed, agreed):
    config["judge"] = {"mode": "panel", "routes": {f: [g for g in KEY_ENV if g != f] for f in KEY_ENV}}
    harness.validate_config(config)
    row = harness.restore_transcripts(saved_report())[0]
    calls = []

    def judge(row, settings):
        calls.append(settings["family"])
        return Reply(json.dumps(votes[len(calls) - 1]), [], 1, 1)

    result = harness.rescore_scenario({"expected": None}, row, judge, config)
    assert calls == ["claude", "gemini"]
    assert result["success"] is passed and result["judge"]["agreed"] is agreed
    assert [j["family"] for j in result["judges"]] == ["claude", "gemini"]
    assert [c["family"] for c in result["model_calls"] if c["role"] == "judge"] == calls


def test_rescore_only_calls_the_routed_judge_and_preserves_saved_evidence(config, monkeypatch, tmp_path):
    source = saved_report()
    path = tmp_path / "source.json"
    path.write_text(json.dumps(source))
    seen = []
    monkeypatch.setenv("ANTHROPIC_API_KEY", "offline-key")
    for key in ("OPENAI_API_KEY", "GEMINI_API_KEY", "MODELSPEC_API_KEY"):
        monkeypatch.delenv(key, raising=False)

    def handler(request):
        seen.append(request)
        assert request.url.host == "api.anthropic.com" and request.url.path == "/v1/messages"
        payload = json.loads(request.content)
        assert payload["tools"] == []
        evidence = json.loads(payload["messages"][0]["content"])
        assert evidence["tool_calls"][0]["result"] == source["tool_responses"]["r1"]
        assert evidence["final_answer"] == source["runs"][0]["final_answer"]
        assert "old-judge" not in json.dumps(evidence)
        return httpx.Response(200, json={"content": [{"type": "text", "text": json.dumps(opinion())}],
                                        "usage": {"input_tokens": 20, "output_tokens": 10}})

    client = httpx.Client
    monkeypatch.setattr(httpx, "Client", lambda **kw: client(transport=httpx.MockTransport(handler), **kw))
    assert harness.main(["--rescore", str(path), "--output-dir", str(tmp_path / "out"),
                         "--date", "2026-10-03"]) == 0
    report = json.loads((tmp_path / "out/2026-10-03-agent-scenarios.json").read_text())
    row = report["runs"][0]
    assert len(seen) == 1 and report["mode"] == "rescore"
    assert row["success"] and row["final_answer"] == source["runs"][0]["final_answer"]
    assert row["previous_evaluation"]["judge"]["model"] == "old-judge"
    assert row["tokens_in"] == 120 and row["tokens_out"] == 20
    assert row["judges"][0]["family"] == "claude"
    assert report["budget"]["reservations"][0]["model"] == "claude-sonnet-5"
    assert row["estimated_cost_usd"] == pytest.approx(report["budget"]["estimated_spend_usd"])
    assert path.read_text() == json.dumps(source)


def test_rescore_dry_run_never_runs_an_agent_or_fetches_tools(monkeypatch, tmp_path):
    path = tmp_path / "source.json"
    source = saved_report()
    capped = copy.deepcopy(source["runs"][0])
    capped.update(final_answer="", status="spend_cap", judge=None)
    source["runs"].append(capped)
    source["runs"].append(copy.deepcopy(source["runs"][0]))
    path.write_text(json.dumps(source))

    def forbidden(*args, **kwargs):
        pytest.fail("Re-score attempted an agent, tool fetch or HTTP call")

    monkeypatch.setattr(harness, "ReplayAgent", forbidden)
    monkeypatch.setattr(harness, "ReplayTools", forbidden)
    monkeypatch.setattr(httpx.Client, "request", forbidden)
    assert harness.main(["--rescore", str(path), "--dry-run", "--output-dir", str(tmp_path / "out"),
                         "--date", "2026-10-03"]) == 0
    report = json.loads((tmp_path / "out/2026-10-03-agent-scenarios.json").read_text())
    assert report["mode"] == "rescore-dry-run" and report["scheduled_runs"] == 3
    assert report["runs"][1]["status"] == "spend_cap" and report["runs"][1]["judges"] == []
    assert report["runs"][2]["judges"]
    assert report["budget"]["estimated_spend_usd"] == 0


def test_rescore_spend_cap_prevents_the_judge_http_call(monkeypatch, tmp_path):
    path = tmp_path / "source.json"
    path.write_text(json.dumps(saved_report()))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "offline-key")
    monkeypatch.setenv("OPENAI_API_KEY", "offline-key")
    monkeypatch.setenv("GEMINI_API_KEY", "offline-key")
    monkeypatch.setattr(httpx.Client, "request", lambda *a, **k: pytest.fail("Unreserved judge call"))
    assert harness.main(["--rescore", str(path), "--spend-cap", "0.000001", "--output-dir", str(tmp_path / "out"),
                         "--date", "2026-10-03"]) == 2
    report = json.loads((tmp_path / "out/2026-10-03-agent-scenarios.json").read_text())
    assert report["runs"][0]["status"] == "spend_cap"
    assert report["budget"]["reservations"] == []


def test_rescore_refuses_missing_evidence():
    report = saved_report()
    report["tool_responses"] = {}
    with pytest.raises(ValueError, match="missing a tool response"):
        harness.restore_transcripts(report)


def test_panel_reserves_each_judge_and_stops_before_the_second_http_call(config, monkeypatch):
    config["judge"] = {"mode": "panel", "routes": {f: [g for g in KEY_ENV if g != f] for f in KEY_ENV}}
    for settings in config["agents"].values():
        settings["price"] = settings["ceiling_price"] = {"input": 1, "output": 1}
    for key in KEY_ENV.values():
        monkeypatch.setenv(key, "offline-key")
    row = harness.restore_transcripts(saved_report())[0]
    scenario = next(s for s in harness.load_scenarios() if s["id"] == row["scenario"])
    evidence = {"scenario": scenario, "final_answer": row["final_answer"], "tool_calls": row["tool_calls"]}
    payload = first_request("claude", "claude-sonnet-5", harness.JUDGE_NOTE, json.dumps(evidence), [], 4096)
    cap = Budget(25).reserve(payload, "claude-sonnet-5", {"input": 1, "output": 1}, 4096)
    budget = Budget(cap)
    seen = []

    def handler(request):
        assert len(budget.calls) == 1 and budget.spent_usd == pytest.approx(cap)
        seen.append(request)
        wire_payload = json.loads(request.content)
        # Charge the entire reserved input/output allowance, leaving no room for judge two.
        return httpx.Response(200, json={"content": [{"type": "text", "text": json.dumps(opinion())}],
                                        "usage": {"input_tokens": len(json.dumps(wire_payload, ensure_ascii=False).encode()) + 8192,
                                                  "output_tokens": 4096}})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = harness.rescore_scenario(scenario, row, harness.live_judge(scenario, budget, config, client), config)
    assert len(seen) == 1 and result["status"] == "spend_cap" and not result["success"]
    assert [j["family"] for j in result["judges"]] == ["claude"]
    assert budget.calls[0]["role"] == "judge" and budget.calls[0]["family"] == "claude"


def test_all_mcp_first_turns_fit_the_budget_without_keys_or_network(config, monkeypatch, capsys):
    for key in (*KEY_ENV.values(), "MODELSPEC_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr(httpx.Client, "request", lambda *a, **k: pytest.fail("Offline accounting made an HTTP call"))
    assert harness.main(["--first-turn-breakdown"]) == 0
    sizes = json.loads(capsys.readouterr().out)
    assert set(sizes) == {"claude", "openai", "gemini"}
    for row in sizes.values():
        assert row["total"] <= 10_000
        assert row["components"]["guide"] > 0 and row["components"]["mcp_instructions"] > 0
        assert sum(row["components"].values()) == row["total"]


@pytest.mark.parametrize("family", ["claude", "openai", "gemini"])
def test_offline_first_request_matches_the_actual_wire_and_delivers_guide(config, family, monkeypatch):
    monkeypatch.setenv(KEY_ENV[family], "offline-key")
    settings = config["agents"][family]
    tools = capture_tools()["tools"]
    prompt = harness.agent_context()
    request = harness.agent_request(harness.load_scenarios()[0])
    expected = first_request(family, settings["model"], prompt, request, tools, config["max_output_tokens"])
    seen = []

    def handler(wire_request):
        seen.append(wire_request)
        assert wire_request.content == httpx.Request("POST", "https://offline.invalid", json=expected).content
        if family == "claude":
            return httpx.Response(200, json={"content": [{"type": "text", "text": "Fixture answer"}],
                                            "usage": {"input_tokens": 1, "output_tokens": 1}})
        if family == "openai":
            return httpx.Response(200, json={"output": [{"type": "message", "content": [{"type": "output_text", "text": "Fixture answer"}]}],
                                            "usage": {"input_tokens": 1, "output_tokens": 1}})
        return httpx.Response(200, json={"candidates": [{"content": {"role": "model", "parts": [{"text": "Fixture answer"}]}}],
                                        "usageMetadata": {"promptTokenCount": 1, "candidatesTokenCount": 1}})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        agent = HttpAgent(family, settings["model"], prompt, request, tools, Budget(25), settings["price"],
                          config["max_output_tokens"], client)
        assert agent.step().text == "Fixture answer"
    copy = agent_copy.copy()
    system = expected["systemInstruction"]["parts"][0]["text"] if family == "gemini" else expected.get("instructions", expected.get("system"))
    assert system.count(copy["context_guide"]) == 1 and system.count(copy["instructions"]) == 1
    assert len(seen) == 1


@pytest.mark.parametrize("section", SECTIONS)
def test_every_vocabulary_lookup_including_empty_pages_has_a_next_hint(section):
    result = lookup({}, section=section, offset=999)
    assert result["next"].startswith("next: call decide")
    if section == "starter":
        assert result["next"] == "next: call decide with this; refine from reading"
        assert result["spec"] == {"spec_version": 1, "optimize": {"min": "offering.cost_per_task"}}
        parse_spec(result["spec"], facets=default().facet)


def test_required_reporting_rules_are_in_the_generated_guide_and_decide_copy():
    copy = agent_copy.copy()
    for text in (agent_copy.GUIDE_OUT.read_text(), copy["context_guide"], copy["tools"]["decide"]):
        assert "Never add a gate or constraint the user didn't state" in text
        assert "Arena web-dev evidence does not establish chat quality" in text
        assert "p_best is the probability of ranking best under the Spec" in text
        assert "not the probability of matching" in text
    assert "One vocabulary lookup per unknown facet, then decide" in copy["tools"]["vocab"]


def test_compact_schema_keeps_complete_validation_at_execution(config):
    tools = capture_tools()["tools"]
    shim = LiveTools(config, tools, None, None)
    invalid = {"spec_version": 1, "optimize": {"min": "offering.cost_per_task"},
               "where": [{"all": [{"facet": "model.context_window", "op": "invented", "value": 4}]}]}
    observed = shim.validate("decide", invalid)
    assert observed["validation_errors"] and not observed["api_call"]
