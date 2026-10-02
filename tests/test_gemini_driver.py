"""Replay Gemini overload responses through the real driver without network I/O."""

import copy
import json

import httpx
import jsonschema
import pytest
import yaml

from qa import providers
from qa.agent_harness import (
    HERE,
    load_scenarios,
    make_report,
    run_scenario,
    validate_config,
    write_report,
)
from qa.providers import Budget, HttpAgent, ProviderError, Reply
from qa.schemas import GEMINI_KEYWORDS


@pytest.fixture
def responses():
    return json.loads((HERE / "fixtures/gemini-responses.json").read_text())


@pytest.fixture
def config():
    return yaml.safe_load((HERE / "config.yaml").read_text())


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "offline-fixture-key")
    monkeypatch.setattr(
        httpx.HTTPTransport,
        "handle_request",
        lambda *a: pytest.fail("Network attempted"),
    )
    monkeypatch.setattr(providers, "sleep", lambda seconds: None)


def driver(client, config, budget=None, tools=None):
    settings = config["agents"]["gemini"]
    return HttpAgent(
        "gemini",
        settings["model"],
        "docs",
        "question",
        tools or [],
        budget if budget is not None else Budget(10),
        settings["price"],
        100,
        client,
        ceiling_price=settings["ceiling_price"],
        fallback=settings.get("fallback"),
    )


@pytest.mark.parametrize("statuses", [(503, 200), (429, 200), (503, 429, 200), (429, 503, 200)])
def test_transient_errors_recover_with_separate_reservations(
    statuses, responses, config, monkeypatch
):
    requests, waits = [], []
    monkeypatch.setattr(providers, "uniform", lambda low, high: 0.25)
    monkeypatch.setattr(providers, "sleep", waits.append)
    budget = Budget(10)

    def handler(request):
        # This assertion runs at the HTTP boundary, after reservation and before response.
        assert len(budget.calls) == len(requests) + 1
        assert budget.calls[-1]["cost_usd"] == budget.calls[-1]["reserved_usd"]
        requests.append(request)
        status = statuses[len(requests) - 1]
        key = {200: "answer", 429: "rate_limited", 503: "unavailable"}[status]
        return httpx.Response(status, json=responses[key])

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        agent = driver(client, config, budget)
        reply = agent.step()
    assert reply.text == "Fixture answer."
    assert (reply.tokens_in, reply.tokens_out) == (60, 5)
    assert waits == ([1.25] if len(statuses) == 2 else [1.25, 2.25])
    paths = [r.url.path for r in requests]
    assert paths[:2] == ["/v1beta/models/gemini-3.8-flash:generateContent"] * min(2, len(statuses))
    if len(statuses) == 3:
        assert paths[2] == "/v1beta/models/gemini-3.7-flash:generateContent"
    assert len(agent.history) == 2  # Only the successful response enters history.
    assert [c["usage_known"] for c in budget.calls] == [s == 429 for s in statuses[:-1]] + [True]
    assert budget.spent_usd == pytest.approx(sum(c["cost_usd"] for c in budget.calls))
    for call, status in zip(budget.calls, statuses):
        if status == 503:
            assert call["cost_usd"] == call["reserved_usd"]
    assert reply.cost_usd == pytest.approx(0.00006375)


@pytest.mark.parametrize("status", [429, 503])
@pytest.mark.parametrize("fallback", [True, False])
def test_exhaustion_never_starts_a_fourth_attempt(status, fallback, responses, config):
    if not fallback:
        config["agents"]["gemini"].pop("fallback")
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(
            status, json=responses["rate_limited" if status == 429 else "unavailable"]
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        agent = driver(client, config)
        with pytest.raises(ProviderError, match=f"HTTP {status}") as error:
            agent.step()
    assert len(requests) == len(agent.budget.calls) == 3
    assert error.value.details["http_status"] == status
    assert agent.last_model == ("gemini-3.7-flash" if fallback else "gemini-3.8-flash")


@pytest.mark.parametrize("allowed_attempts", [0, 1, 2])
def test_cap_stops_before_the_next_http_attempt(allowed_attempts, responses, config):
    requests = []
    probe = Budget(10)

    def handler(request):
        requests.append(request)
        return httpx.Response(503, json=responses["unavailable"])

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        agent = driver(client, config)
        amount = probe.reserve(agent.payload(), agent.model, agent.ceiling_price, agent.max_output)
        agent.budget.limit_usd = amount * (allowed_attempts + 0.1)
        row = run_scenario(load_scenarios()[0], "gemini", agent, None, None, config)
    assert row["status"] == "spend_cap"
    assert len(requests) == len(agent.budget.calls) == allowed_attempts
    assert agent.budget.spent_usd <= agent.budget.limit_usd
    assert row["model"] == "gemini-3.8-flash"  # A denied fallback is not reported as used.
    assert all(not c["usage_known"] for c in agent.budget.calls)


@pytest.mark.parametrize("status", [400, 401, 403, 404, 408, 422, 500, 502, 504])
def test_other_http_statuses_do_not_retry_or_fallback(status, config):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(status, json={"error": {"status": "FIXTURE_ERROR"}})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        agent = driver(client, config)
        with pytest.raises(ProviderError, match=f"HTTP {status}"):
            agent.step()
    assert len(requests) == len(agent.budget.calls) == 1
    assert agent.last_model == "gemini-3.8-flash"


@pytest.mark.parametrize("failure", ["timeout", "malformed"])
def test_transport_and_decoding_failures_keep_reservation_without_retry(failure, config):
    requests = []

    def handler(request):
        requests.append(request)
        if failure == "timeout":
            raise httpx.ReadTimeout("private transport detail", request=request)
        return httpx.Response(200, content=b"not json")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        agent = driver(client, config)
        with pytest.raises(ProviderError, match="response or transport failed") as error:
            agent.step()
    assert len(requests) == 1
    assert agent.budget.spent_usd == agent.budget.calls[0]["reserved_usd"]
    assert not agent.budget.calls[0]["usage_known"]
    if failure == "timeout":
        assert error.value.details == {"type": "ReadTimeout"}
        assert "private transport detail" not in str(error.value)


def test_rate_limit_with_possible_usage_retains_the_reservation(responses, config):
    requests = []

    def handler(request):
        requests.append(request)
        if len(requests) == 1:
            body = responses["rate_limited"] | {"usageMetadata": {"promptTokenCount": 7}}
            return httpx.Response(429, json=body)
        return httpx.Response(200, json=responses["answer"])

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        agent = driver(client, config)
        agent.step()
    assert not agent.budget.calls[0]["usage_known"]
    assert agent.budget.calls[0]["cost_usd"] == agent.budget.calls[0]["reserved_usd"]


def test_fallback_uses_its_own_rates_and_stays_selected(responses, config):
    config["agents"]["gemini"]["fallback"]["price"] = {"input": 2, "output": 10}
    config["agents"]["gemini"]["fallback"]["ceiling_price"] = {"input": 4, "output": 15}
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(
            503 if len(requests) < 3 else 200,
            json=responses["unavailable" if len(requests) < 3 else "answer"],
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        agent = driver(client, config)
        reply = agent.step()
        agent.step()
    assert [c["model"] for c in agent.budget.calls] == ["gemini-3.8-flash"] * 2 + [
        "gemini-3.7-flash"
    ] * 2
    assert agent.budget.calls[2]["reserved_usd"] > agent.budget.calls[0]["reserved_usd"]
    assert reply.cost_usd == pytest.approx(0.00017)


def test_retry_after_a_tool_reply_preserves_model_and_thought_signature(responses, config):
    requests = []

    def handler(request):
        requests.append(request)
        n = len(requests)
        return httpx.Response(
            503 if n in (2, 3) else 200,
            json=responses["unavailable" if n in (2, 3) else "tool_call" if n == 1 else "answer"],
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        agent = driver(client, config)
        reply = agent.step()
        agent.add_results([(reply.calls[0], {"isError": False, "content": []})])
        agent.step()
    assert all("gemini-3.8-flash" in r.url.path for r in requests)
    payload = json.loads(requests[-1].content)
    assert payload["contents"][1]["parts"][0]["thoughtSignature"] == "fixture-signature"
    assert payload["contents"][2]["parts"][0]["functionResponse"]["id"] == "c1"


@pytest.mark.parametrize("terminal_status", [200, 503])
def test_report_records_actual_fallback_model(terminal_status, responses, config, tmp_path):
    requests = []

    def handler(request):
        requests.append(request)
        status = 503 if len(requests) < 3 else terminal_status
        return httpx.Response(status, json=responses["answer" if status == 200 else "unavailable"])

    def judge(row):
        return Reply(
            json.dumps(
                {
                    "passed": True,
                    "rationale": "fixture",
                    "top_models": [],
                    "answer_kind": "abstain",
                    "missing_capabilities": [],
                }
            ),
            [],
            0,
            0,
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        agent = driver(client, config)
        scenario = load_scenarios()[0] | {"expected": None}
        row = run_scenario(scenario, "gemini", agent, None, judge, config)
    report = make_report(
        [row],
        [scenario],
        False,
        agent.budget,
        "2026-10-02",
        {"agents": {"gemini": config["agents"]["gemini"]}},
    )
    _, path = write_report(report, tmp_path)
    saved = json.loads(path.read_text())
    assert saved["runs"][0]["model"] == "gemini-3.7-flash"
    assert saved["budget"]["reservations"][-1]["model"] == "gemini-3.7-flash"
    assert saved["metadata"]["agents"]["gemini"]["model"] == "gemini-3.8-flash"
    if terminal_status == 200:
        assert saved["runs"][0]["model_calls"][0]["model"] == "gemini-3.7-flash"


def test_sanitised_mcp_schemas_use_the_documented_json_schema_field(responses, config):
    tools = json.loads((HERE / "fixtures/mcp-tools.json").read_text())["tools"]
    original = copy.deepcopy(tools)
    requests = []

    def check_node(node):
        assert set(node) <= GEMINI_KEYWORDS
        for value in node.get("properties", {}).values():
            check_node(value)
        if "items" in node:
            check_node(node["items"])
        for value in node.get("anyOf", []):
            check_node(value)

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=responses["answer"])

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        agent = driver(client, config, tools=tools)
        agent.step()
    declarations = json.loads(requests[0].content)["tools"][0]["functionDeclarations"]
    assert len(declarations) == 7
    for function in declarations:
        assert set(function) == {"name", "description", "parametersJsonSchema"}
        schema = function["parametersJsonSchema"]
        assert schema["type"] == "object"
        assert not {"anyOf", "oneOf", "allOf", "$ref", "$defs"} & schema.keys()
        jsonschema.Draft202012Validator.check_schema(schema)
        check_node(schema)
    assert tools == original


@pytest.mark.parametrize(
    "change", ["same_model", "negative_price", "missing_ceiling", "invalid_model"]
)
def test_invalid_fallback_config_fails_before_any_http(config, change):
    fallback = config["agents"]["gemini"]["fallback"]
    if change == "same_model":
        fallback["model"] = config["agents"]["gemini"]["model"]
    elif change == "negative_price":
        fallback["price"]["input"] = -1
    elif change == "missing_ceiling":
        fallback.pop("ceiling_price")
    else:
        fallback["model"] = "../invalid"
    with pytest.raises(ValueError):
        validate_config(config)


def test_gemini_judge_reports_its_actual_model(responses, config):
    from qa.agent_harness import ReplayAgent

    requests = []
    config["judge"]["family"] = "gemini"
    config["judge"]["model"] = "gemini-3.8-flash"
    judgement = copy.deepcopy(responses["answer"])
    judgement["candidates"][0]["content"]["parts"][0]["text"] = json.dumps(
        {
            "passed": True,
            "rationale": "fixture",
            "top_models": [],
            "answer_kind": "abstain",
            "missing_capabilities": [],
        }
    )

    def handler(request):
        requests.append(request)
        return httpx.Response(
            503 if len(requests) < 3 else 200,
            json=responses["unavailable"] if len(requests) < 3 else judgement,
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        judge = driver(client, config)
        agent = ReplayAgent(
            [{"text": "Fixture answer.", "calls": [], "tokens_in": 0, "tokens_out": 0}]
        )
        row = run_scenario(
            load_scenarios()[0] | {"expected": None},
            "gemini",
            agent,
            None,
            lambda row: judge.step(),
            config,
        )
    assert row["status"] == "completed"
    assert row["judge"]["model"] == "gemini-3.7-flash"
    assert row["model_calls"][-1]["model"] == "gemini-3.7-flash"
