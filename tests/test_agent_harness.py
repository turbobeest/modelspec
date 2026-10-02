"""Exercise scenario provenance, agent tool loops, vendor wire formats and spend refusal offline."""

from __future__ import annotations

import copy
import json

import httpx
import pytest
import yaml

from qa.agent_harness import (
    HERE,
    JUDGE_NOTE,
    ROOT,
    ReplayAgent,
    agent_request,
    expected_match,
    load_scenarios,
    main,
    metrics,
    parse_judgement,
    percentile,
    run_scenario,
)
from qa.contracts import TOOL_NAMES, capture_tools, source_hashes
from qa.providers import Budget, HttpAgent, ProviderError, SpendLimitError
from qa.tools import LiveTools, require_nonproduction, tool_result


@pytest.fixture
def config():
    return yaml.safe_load((HERE / "config.yaml").read_text())


@pytest.fixture
def definitions():
    return json.loads((HERE / "fixtures/mcp-tools.json").read_text())["tools"]


def test_catalogue_is_sourced_and_covers_all_families_and_templates():
    scenarios = load_scenarios()
    assert len(scenarios) >= 30
    assert {s["family"] for s in scenarios} == {"F1", "F2", "F3", "F4"}
    catalogue = yaml.safe_load((ROOT / "registry/templates.yaml").read_text())
    assert {s["template"] for s in scenarios if "template" in s} == {
        t["id"] for t in catalogue["templates"]
    }
    assert sum(s["expected"] is not None for s in scenarios) == 20
    for s in scenarios:
        request = json.loads(agent_request(s))
        assert set(request) == {"persona", "request", "constraints"}
        assert "expected" not in request and "gaps" not in request and "rubric" not in request
    names = " ".join(s["request"] for s in scenarios if s["family"] == "F3")
    assert all(n in names for n in ("RTX 5090", "DGX Spark", "M4 MacBook"))


def test_invented_expectations_are_rejected(tmp_path):
    scenario = copy.deepcopy(load_scenarios()[0])
    scenario["expected"] = {"id": "Q01", "acceptable": [{"model_id": "invented/winner"}]}
    (tmp_path / "bad.yaml").write_text(yaml.safe_dump(scenario))
    with pytest.raises(ValueError, match="approved recall evidence"):
        load_scenarios(tmp_path)


def test_mcp_capture_matches_current_public_sources():
    recorded = json.loads((HERE / "fixtures/mcp-tools.json").read_text())
    assert recorded == capture_tools()
    assert recorded["source_hashes"] == source_hashes()
    assert tuple(t["name"] for t in recorded["tools"]) == TOOL_NAMES
    assert "Read vocab first" in recorded["tools"][4]["description"]
    assert "input_schema" in recorded["tools"][4]


@pytest.mark.parametrize("family", ["claude", "openai", "gemini"])
def test_full_dry_replay_has_no_network_or_keys(monkeypatch, tmp_path, family):
    def forbidden(*args, **kwargs):
        raise AssertionError("Dry-run attempted network I/O")

    monkeypatch.setattr(httpx.Client, "request", forbidden)
    for name in ("MODELSPEC_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    assert (
        main(
            ["--dry-run", "--agent", family, "--output-dir", str(tmp_path), "--date", "2026-10-01"]
        )
        == 0
    )
    report = json.loads((tmp_path / "2026-10-01-agent-scenarios.json").read_text())
    assert len(report["runs"]) == len(load_scenarios())
    assert report["budget"]["real_spend_usd"] == 0
    assert report["mode"] == "dry-run"
    assert report["metadata"]["fixtures"]["agent_and_judge"].startswith("Scripted")
    assert report["per_family"]["F2"]["runs"] == sum(s["family"] == "F2" for s in load_scenarios())
    assert all(r["judge"] and r["status"] == "completed" for r in report["runs"])
    retry = next(r for r in report["runs"] if r["scenario"] == "recall-q08")
    assert retry["tool_calls"][2]["retry_of"] == "fixture-1"
    if family != "openai":
        assert retry["tool_calls"][1]["unknown_facets"] == ["model.context_tokens"]
    assert any(g["family"] == "F2" and "free-text" in g["reason"] for g in report["gap_list"])
    assert report["misuse_patterns"]["schema_confusion_by_tool"]


def test_top_or_tied_subset_is_compared_without_order_or_missing_card_invention():
    expected = {
        "acceptable": [{"model_id": "lab/a"}, {"model_id": "lab/b"}, {"name": "Missing/Card"}],
        "must_never": [{"model_id": "lab/c"}],
    }
    assert expected_match(expected, {"top_models": ["lab/b", "lab/a"], "answer_kind": "tied"})
    assert not expected_match(expected, {"top_models": ["lab/a", "lab/c"], "answer_kind": "tied"})
    assert not expected_match(expected, {"top_models": [], "answer_kind": "abstain"})
    assert expected_match(
        {"acceptable": [{"rule": "do not name a model"}]},
        {"top_models": [], "answer_kind": "abstain"},
    )
    assert expected_match(None, {"top_models": [], "answer_kind": "abstain"}) is None


def test_judge_must_extract_the_final_recommendation_consistently():
    assert "FINAL ANSWER" in JUDGE_NOTE
    assert parse_judgement(
        "```json\n"
        + json.dumps(
            {
                "passed": True,
                "rationale": "supported",
                "top_models": ["lab/a", "lab/b"],
                "answer_kind": "tied",
                "missing_capabilities": [],
            }
        )
        + "\n```"
    )["passed"]
    with pytest.raises(ValueError):
        parse_judgement(json.dumps({"passed": "yes"}))
    with pytest.raises(ValueError):
        parse_judgement(
            json.dumps(
                {
                    "passed": True,
                    "rationale": "",
                    "top_models": ["lab/a"],
                    "answer_kind": "abstain",
                    "missing_capabilities": [],
                }
            )
        )


def test_call_and_turn_caps_count_individual_calls_and_do_not_make_a_judge_call(config):
    class Shim:
        def __init__(self):
            self.names = []

        def execute(self, name, arguments):
            self.names.append(name)
            return {
                "result": tool_result({"status": 200, "body": {}}),
                "api_call": True,
                "latency_ms": 7,
                "validation_errors": [],
                "unknown_facets": [],
            }

    def no_judge(row):
        raise AssertionError("No final answer to judge")

    scenario = load_scenarios()[0]
    turns = [
        {
            "text": "",
            "tokens_in": 10,
            "tokens_out": 20,
            "calls": [{"id": str(i), "name": "vocab", "arguments": {}} for i in range(3)],
        }
    ]
    shim = Shim()
    row = run_scenario(
        scenario, "claude", ReplayAgent(turns), shim, no_judge, config | {"tool_call_cap": 2}
    )
    assert row["status"] == "tool_call_cap" and shim.names == ["vocab", "vocab"]
    assert row["tokens_out"] == 20 and not row["success"]
    row = run_scenario(
        scenario, "claude", ReplayAgent(turns), Shim(), no_judge, config | {"turn_cap": 1}
    )
    assert row["status"] == "turn_cap" and len(row["tool_calls"]) == 3


@pytest.mark.parametrize(
    "origin",
    [
        "https://api.modelspec.dev",
        "https://modelspec.dev",
        "https://www.modelspec.dev",
        "https://key@staging.test",
        "https://staging.test?api_key=secret",
        "ftp://staging.test",
    ],
)
def test_production_or_credential_origins_are_rejected(origin):
    with pytest.raises(ValueError):
        require_nonproduction(origin)


def test_tool_shim_routes_all_seven_tools_and_keeps_keys_out_of_feedback(config, definitions):
    requests = []

    def handler(request):
        requests.append(request)
        if request.url.path == "/v1/vocabulary":
            return httpx.Response(
                200,
                json={
                    "facets": [{"id": "model.context_window"}],
                    "models": {"lab/a": {"name": "A"}},
                    "providers": ["lab"],
                },
            )
        return httpx.Response(200, json={"status": "answered", "results": [], "may_qualify": []})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        shim = LiveTools(config, definitions, "secret-key", client)
        for name, args in [
            ("vocab", {"section": "providers"}),
            ("model_info", {"model_id": "lab/a"}),
            ("list_use_cases", {}),
            ("rank", {"use_case": "coding"}),
            ("decide", {"spec_version": 1, "optimize": {"max": "reasoning"}}),
            ("policy_check", {"policy": {"commercial_use": {"required": True}}}),
            ("feedback", {"rating": "confusing"}),
        ]:
            observed = shim.execute(name, args)
            assert observed["api_call"] and not observed["result"]["isError"]
        assert [r.url.path for r in requests] == [
            "/v1/vocabulary",
            "/v1/vocabulary",
            "/api/rank/profiles.json",
            "/v1/rank",
            "/v1/decide",
            "/v1/policy-check",
            "/v1/feedback",
        ]
        assert requests[3].headers["authorization"] == "Bearer secret-key"
        assert "authorization" not in requests[-1].headers
        assert json.loads(requests[-1].content)["client"] == "mcp"
        assert "secret-key" not in json.dumps(observed)
        before = len(requests)
        assert shim.execute(
            "decide", {"spec_version": 1, "task_type": "coding", "optimize": {"max": "reasoning"}}
        )["validation_errors"]
        assert not shim.execute("unknown_tool", {})["api_call"]
        assert not shim.execute("model_info", {"model_id": "../secrets"})["api_call"]
        assert len(requests) == before


def test_transport_errors_and_non_json_responses_are_tool_results(config, definitions):
    def handler(request):
        if request.url.path == "/v1/decide":
            return httpx.Response(503, text="Cloudflare CPU limit")
        raise httpx.ConnectError("connection failed")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        shim = LiveTools(config, definitions, "secret", client)
        observed = shim.execute("vocab", {})
        assert observed["result"]["isError"]
        assert json.loads(observed["result"]["content"][0]["text"])["status"] == 0
        observed = shim.execute("decide", {"spec_version": 1, "optimize": {"max": "reasoning"}})
        assert (
            json.loads(observed["result"]["content"][0]["text"])["body"] == "Cloudflare CPU limit"
        )


@pytest.mark.parametrize("family", ["claude", "openai", "gemini"])
def test_native_tool_calling_and_billable_tokens_are_replayed(family, monkeypatch):
    for name in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"):
        monkeypatch.setenv(name, "never-log-this")
    captured = []
    responses = {
        "claude": {
            "content": [{"type": "tool_use", "id": "c1", "name": "vocab", "input": {}}],
            "usage": {
                "input_tokens": 10,
                "cache_read_input_tokens": 20,
                "cache_creation_input_tokens": 30,
                "output_tokens": 5,
            },
        },
        "openai": {
            "output": [
                {"type": "reasoning", "id": "r1", "encrypted_content": "opaque"},
                {"type": "function_call", "call_id": "c1", "name": "vocab", "arguments": "{}"},
            ],
            "usage": {"input_tokens": 60, "output_tokens": 5},
        },
        "gemini": {
            "candidates": [
                {
                    "content": {
                        "role": "model",
                        "parts": [
                            {
                                "functionCall": {"id": "c1", "name": "vocab", "args": {}},
                                "thoughtSignature": "opaque",
                            }
                        ],
                    }
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 60,
                "candidatesTokenCount": 2,
                "thoughtsTokenCount": 3,
            },
        },
    }

    def handler(request):
        captured.append(request)
        return httpx.Response(200, json=responses[family])

    budget = Budget(1)
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        agent = HttpAgent(
            family,
            "configured-model",
            "ModelSpec docs",
            "question",
            [
                {
                    "name": "vocab",
                    "description": "Read vocabulary",
                    "input_schema": {"type": "object", "properties": {}},
                }
            ],
            budget,
            {"input": 2, "output": 10},
            100,
            client,
        )
        reply = agent.step()
        assert reply.tokens_in == 60 and reply.tokens_out == 5
        assert reply.calls == [{"id": "c1", "name": "vocab", "arguments": {}}]
        assert budget.spent_usd == pytest.approx(0.00017)
        agent.add_results([(reply.calls[0], tool_result({"status": 200, "body": {}}))])
        payload = agent.payload()
        assert "never-log-this" not in json.dumps(payload)
        if family == "openai":
            assert captured[0].url.path == "/v1/responses"
            assert payload["store"] is False
            assert payload["input"][1]["encrypted_content"] == "opaque"
            assert payload["input"][-1]["type"] == "function_call_output"
        elif family == "gemini":
            assert payload["contents"][1]["parts"][0]["thoughtSignature"] == "opaque"
            assert payload["contents"][-1]["parts"][0]["functionResponse"]["id"] == "c1"
        else:
            assert payload["messages"][-1]["content"][0]["tool_use_id"] == "c1"


def test_hard_budget_reserves_before_http_and_does_not_refund_unknown_usage(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "secret")
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(500, json={"error": "private-secret"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        agent = HttpAgent(
            "openai",
            "model",
            "docs",
            "question",
            [],
            Budget(0.000001),
            {"input": 2, "output": 10},
            100,
            client,
        )
        with pytest.raises(SpendLimitError):
            agent.step()
        assert not calls
        budget = Budget(1)
        agent.budget = budget
        with pytest.raises(ProviderError, match="HTTP 500"):
            agent.step()
        assert len(calls) == 1 and budget.spent_usd > 0
        assert not budget.calls[0]["usage_known"]
        budget.limit_usd = budget.spent_usd
        with pytest.raises(SpendLimitError):
            agent.step()
        assert len(calls) == 1


def test_percentiles_and_failure_denominators_are_explicit():
    assert percentile([9, 1, 3, 7], 0.5) == 3
    assert percentile([9, 1, 3, 7], 0.95) == 9
    assert percentile([], 0.95) is None
    result = metrics(
        [
            {
                "success": True,
                "expected_match": True,
                "tool_calls": [{"api_call": True, "latency_ms": 10}],
            },
            {"success": False, "expected_match": None, "tool_calls": []},
        ]
    )
    assert result["success_rate"] == 0.5
    assert result["expected_match_rate"] == 1
    assert result["mean_tool_calls"] == 0.5
    assert result["api_latency_p95_ms"] == 10


def test_live_wire_loop_and_separate_judge_share_the_invocation_budget(
    monkeypatch, tmp_path, config
):
    from qa.providers import KEY_ENV

    for name in (*KEY_ENV.values(), "MODELSPEC_API_KEY"):
        monkeypatch.setenv(name, "sensitive-test-value")
    config["api_base_url"] = "https://staging.example"
    config["export_base_url"] = "https://static-staging.example"
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config))
    seen = []
    model_calls = 0

    def handler(request):
        nonlocal model_calls
        seen.append(request)
        if request.url.host == "staging.example":
            assert request.headers["authorization"] == "Bearer sensitive-test-value"
            return httpx.Response(
                400,
                json={
                    "error": {
                        "code": "invalid_spec",
                        "issues": [{"field": "task", "reason": "free-text task is unsupported"}],
                    },
                    "echo": "sensitive-test-value",
                },
            )
        assert request.url.path == "/v1/responses"
        payload = json.loads(request.content)
        model_calls += 1
        if model_calls == 1:
            assert "approved recall evidence" not in payload["input"][0]["content"]
            output = [
                {
                    "type": "function_call",
                    "call_id": "c1",
                    "name": "decide",
                    "arguments": json.dumps(
                        {
                            "spec_version": 1,
                            "task": "exact prompt",
                            "optimize": {"max": "reasoning"},
                        }
                    ),
                }
            ]
        elif model_calls == 2:
            assert "sensitive-test-value" not in json.dumps(payload)
            assert "invalid_spec" in payload["input"][-1]["output"]
            output = [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": "ModelSpec cannot select a model for this exact prompt.",
                        }
                    ],
                }
            ]
        else:
            assert model_calls == 3 and "Judge the submitted answer" in payload["instructions"]
            assert not payload["tools"]
            output = [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": json.dumps(
                                {
                                    "passed": True,
                                    "rationale": "Honest refusal",
                                    "top_models": [],
                                    "answer_kind": "abstain",
                                    "missing_capabilities": ["prompt interpretation"],
                                }
                            ),
                        }
                    ],
                }
            ]
        return httpx.Response(
            200, json={"output": output, "usage": {"input_tokens": 100, "output_tokens": 50}}
        )

    client_class = httpx.Client
    monkeypatch.setattr(
        httpx, "Client", lambda **kw: client_class(transport=httpx.MockTransport(handler), **kw)
    )
    assert (
        main(
            [
                "--config",
                str(config_path),
                "--agent",
                "openai",
                "--scenario",
                "prompt-code",
                "--output-dir",
                str(tmp_path),
                "--date",
                "2026-10-01",
            ]
        )
        == 0
    )
    raw = (tmp_path / "2026-10-01-agent-scenarios.json").read_text()
    assert "sensitive-test-value" not in raw
    report = json.loads(raw)
    row = report["runs"][0]
    assert row["success"] and row["expected_match"] is None
    assert row["judge"]["mode"] == "live"
    assert len(row["billing_calls"]) == 3 and len(seen) == 4
    assert report["budget"]["estimated_spend_usd"] == pytest.approx(0.0021)
    assert row["estimated_cost_usd"] == pytest.approx(0.0021)
    assert row["tokens_in"] == 300 and row["tokens_out"] == 150


def test_config_rejects_prices_that_could_disable_the_spend_cap(config):
    from qa.agent_harness import validate_config

    for value in (-1, float("nan"), float("inf")):
        changed = copy.deepcopy(config)
        changed["agents"]["claude"]["price"]["input"] = value
        with pytest.raises(ValueError, match="Prices"):
            validate_config(changed)


def test_unknown_facet_detection_distinguishes_unadvertised_but_valid_ids(config, definitions):
    shim = LiveTools(config, definitions, None, None)
    shim.valid_ids = {"model.context_window"}
    args = {
        "where": [{"facet": "model.context_tokens", "op": ">=", "value": 4}],
        "optimize": {"max": "evidence.outcome"},
    }
    observed = shim.finish(
        "decide",
        args,
        {
            "status": 400,
            "body": {
                "error": {"issues": [{"field": "model.context_tokens", "reason": "unknown field"}]}
            },
        },
        5,
    )
    assert observed["unknown_facets"] == ["model.context_tokens"]
    assert observed["unadvertised_facets"] == ["evidence.outcome", "model.context_tokens"]


def test_strips_nested_fields_the_way_mcp_zod_does(config, definitions):
    shim = LiveTools(config, definitions, None, None)
    args = {
        "use_case": "coding",
        "extra": True,
        "environment": {"hardware": "gpu", "prompt": "ignored"},
    }
    assert shim.prepare("rank", args) == {
        "use_case": "coding",
        "extra": True,
        "environment": {"hardware": "gpu"},
    }
    assert shim.prepare("vocab", {"section": "facets", "private": "ignored"}) == {
        "section": "facets"
    }
