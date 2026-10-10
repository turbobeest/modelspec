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
    agent_constraints,
    agent_request,
    evaluate_answer,
    expected_match,
    load_scenarios,
    main,
    make_report,
    markdown,
    metrics,
    parse_judgement,
    percentile,
    run_scenario,
)
from qa.providers import Budget, HttpAgent, ProviderError, Reply, SpendLimitError
from qa.contracts import TOOL_NAMES, capture_tools, source_hashes

from qa.tools import LiveTools, require_nonproduction, tool_result


@pytest.fixture(autouse=True)
def _no_retry_sleep(monkeypatch):
    import qa.providers

    monkeypatch.setattr(qa.providers, "sleep", lambda seconds: None)


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


@pytest.mark.parametrize("count,expected", [
    (1, [
        "CLI truncated or unreadable tool results; the agent did not see these answers.",
        "", "- [s01, claude]", "",
    ]),
    (12, [
        "CLI truncated or unreadable tool results; the agent did not see these answers.",
        "", "- [s01, claude]", "- [s02, claude]", "- [s03, claude]",
        "- [s04, claude]", "- [s05, claude]", "- [s06, claude]", "- [s07, claude]",
        "- [s08, claude]", "- [s09, claude]", "- [s10, claude]", "- (+2 more)", "",
    ]),
])
def test_parse_defect_markdown_counts_only_positive_overflow(count, expected):
    report = make_report([], [], False, Budget(1), "2026-10-10", {"agents": ["claude"]})
    report["parse_defects"] = [
        [f"s{number:02}", "claude", "unreadable", 1] for number in range(1, count + 1)
    ]
    rendered = markdown(report)
    lines = rendered.splitlines()
    start = lines.index(expected[0])
    assert lines[start:lines.index("## Gap list")] == expected
    assert "(+-" not in rendered


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
    assert "Call decide early" in recorded["tools"][4]["description"]
    assert "input_schema" in recorded["tools"][4]


def test_mcp_capture_reads_generated_copy_and_pins_its_hash(tmp_path, monkeypatch):
    from qa import contracts

    recorded = capture_tools()
    for path in contracts.SOURCE_PATHS:
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / path).read_bytes())
    copy_path = tmp_path / "mcp/src/agent-copy.json"
    descriptions = {name: f"Generated description for {name}" for name in TOOL_NAMES}
    copy_path.write_text(json.dumps({"tools": descriptions}))
    # MODEL-257 removed the prose constants and registers generated descriptions.
    (tmp_path / "mcp/src/server.ts").write_text(
        'import agentCopy from "./agent-copy.json";\n'
        + "\n".join(
            f'server.registerTool(\n  "{name}" , {{\n'
            f' description: agentCopy.tools.{name},\n inputSchema: input,\n}}, handler);'
            for name in TOOL_NAMES
        )
    )
    monkeypatch.setattr(contracts, "ROOT", tmp_path)
    captured = capture_tools()
    assert [t["description"] for t in captured["tools"]] == list(descriptions.values())
    assert [t["input_schema"] for t in captured["tools"]] == [
        t["input_schema"] for t in recorded["tools"]
    ]
    pinned = captured["source_hashes"]["mcp/src/agent-copy.json"]
    copy_path.write_text(json.dumps({"tools": descriptions | {"decide": "Changed copy"}}))
    assert source_hashes()["mcp/src/agent-copy.json"] != pinned
    assert capture_tools()["tools"][4]["description"] == "Changed copy"


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
    seen_null = {"status": "no_feasible", "answer": None}
    assert expected_match(expected, {"top_models": [], "answer_kind": "abstain"}, seen=seen_null)
    assert expected_match(
        expected, {"top_models": [], "answer_kind": "abstain"},
        seen={"status": "partial", "answer": {"kind": "separated", "members": ["lab/a"]}},
    )
    assert expected_match(
        expected, {"top_models": [], "answer_kind": "abstain"},
        seen={"status": "answered", "answer": None},
    )
    assert not expected_match(
        expected, {"top_models": [], "answer_kind": "abstain"},
        seen={"status": "answered", "answer": {"kind": "separated", "members": ["lab/a"]}},
    )


def _judge_reply(passed: bool, kind: str, models: list[str]) -> Reply:
    return Reply(
        text=json.dumps({
            "passed": passed,
            "rationale": "supported",
            "top_models": models,
            "answer_kind": kind,
            "missing_capabilities": [],
        }),
        calls=[],
        tokens_in=1,
        tokens_out=1,
        model="judge-fixture",
    )


def _row(tool_calls: list | None = None) -> dict:
    return {
        "agent": "claude",
        "model_calls": [],
        "tokens_in": 0,
        "tokens_out": 0,
        "tool_calls": tool_calls or [],
    }


def _decide_seen(body: dict) -> dict:
    return {
        "name": "decide",
        "result": {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "origin": "https://api.modelspec.dev/v1/decide",
                    "status": 200,
                    "body": body,
                }),
            }],
        },
    }


def test_success_follows_a_passing_judge_when_the_curated_set_does_not(config):
    scenario = {"expected": {"acceptable": [{"model_id": "lab/old"}]}}
    row = _row()
    evaluate_answer(scenario, row, lambda *_: _judge_reply(True, "single", ["lab/newer"]), config)
    assert row["success"] is True
    assert row["expected_match"] is False


def test_a_judged_abstain_matches_when_the_seen_answer_is_null(config):
    scenario = {"expected": {"acceptable": [{"model_id": "lab/old"}]}}
    row = _row([_decide_seen({"status": "no_feasible", "answer": None})])
    evaluate_answer(scenario, row, lambda *_: _judge_reply(True, "abstain", []), config)
    assert row["judge"]["passed"] is True
    assert row["expected_match"] is True
    assert row["success"] is True


def test_open_weights_false_is_shown_to_the_agent_as_not_required():
    false_case = next(s for s in load_scenarios() if s["id"] == "recall-q01")
    true_case = next(s for s in load_scenarios() if s["id"] == "recall-q12")
    assert false_case["constraints"]["open_weights"] is False
    assert true_case["constraints"]["open_weights"] is True
    assert false_case["expected"]["id"] == "Q01"
    assert json.loads(agent_request(false_case))["constraints"]["open_weights"] == "not required"
    assert json.loads(agent_request(true_case))["constraints"]["open_weights"] == "required"
    assert false_case["constraints"]["open_weights"] is False
    assert agent_constraints({"open_weights": False, "class": "generate"}) == {
        "open_weights": "not required",
        "class": "generate",
    }
    assert agent_constraints(["model.class = text-generator"]) == ["model.class = text-generator"]


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
        for index in (0, 1, 3, 4, 5):
            assert requests[index].headers["authorization"] == "Bearer secret-key"
        assert "authorization" not in requests[2].headers
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
        payload = json.loads(request.content)
        model_calls += 1
        assert request.url.path == ("/v1/responses" if model_calls < 3 else "/v1/messages")
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
            assert model_calls == 3 and "Judge the submitted answer" in payload["system"]
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
        if model_calls == 3:
            return httpx.Response(200, json={"content": [{"type": "text", "text": output[0]["content"][0]["text"]}],
                                            "usage": {"input_tokens": 100, "output_tokens": 50}})
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


@pytest.mark.parametrize("family", ["claude", "openai", "gemini"])
def test_fixture_request_has_a_literal_object_tool_root(family, config, definitions, monkeypatch):
    import re

    from jsonschema import Draft202012Validator

    from qa.agent_harness import SYSTEM_NOTE
    from qa.providers import KEY_ENV

    monkeypatch.setenv(KEY_ENV[family], "offline-key")
    settings = config["agents"][family]
    with httpx.Client(
        transport=httpx.MockTransport(lambda r: pytest.fail("Network call"))
    ) as client:
        agent = HttpAgent(
            family,
            settings["model"],
            SYSTEM_NOTE + (ROOT / "api/worker/openapi.yaml").read_text(),
            agent_request(load_scenarios()[0]),
            definitions,
            Budget(2),
            settings["price"],
            config["max_output_tokens"],
            client,
        )
        payload = agent.payload()
    if family == "claude":
        tools = payload["tools"]
        schemas = [t["input_schema"] for t in tools]
        assert payload["model"] == "claude-sonnet-5"
        assert payload["max_tokens"] == 4096 and payload["max_tokens"] <= 128_000
        assert isinstance(payload["system"], str) and payload["system"].startswith(SYSTEM_NOTE)
        assert payload["messages"] == [
            {"role": "user", "content": agent_request(load_scenarios()[0])}
        ]
    elif family == "openai":
        tools = payload["tools"]
        schemas = [t["parameters"] for t in tools]
        assert all(t["strict"] is False and t["type"] == "function" for t in tools)
        assert payload["max_output_tokens"] == 4096
        assert payload["instructions"].startswith(SYSTEM_NOTE)
        assert payload["input"][0]["role"] == "user" and payload["input"][0]["content"]
        assert payload["store"] is False
    else:
        tools = payload["tools"][0]["functionDeclarations"]
        schemas = [t["parametersJsonSchema"] for t in tools]
        assert payload["generationConfig"]["maxOutputTokens"] == 4096
        assert payload["systemInstruction"]["parts"][0]["text"].startswith(SYSTEM_NOTE)
        assert payload["contents"][0]["role"] == "user"
        assert payload["contents"][0]["parts"][0]["text"]
        # Conservative JSON vocabulary, independent of the converter's allowlist.
        allowed = {
            "type",
            "description",
            "properties",
            "required",
            "items",
            "enum",
            "anyOf",
            "minimum",
            "maximum",
            "minLength",
            "maxLength",
            "pattern",
            "format",
            "minItems",
            "maxItems",
            "minProperties",
            "maxProperties",
        }
        assert all(node.keys() <= allowed for schema in schemas for node in schema_nodes(schema))
    assert all(re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", t["name"]) for t in tools)
    assert all(s.get("type") == "object" for s in schemas)
    for schema in schemas:
        Draft202012Validator.check_schema(schema)
        assert not {"oneOf", "anyOf", "allOf"} & schema.keys()
        assert all(not {"$ref", "$defs"} & node.keys() for node in schema_nodes(schema))
    assert len(json.dumps(payload).encode()) < 1_000_000


def schema_nodes(schema):
    yield schema
    for keyword in ("properties", "patternProperties"):
        for child in schema.get(keyword, {}).values():
            yield from schema_nodes(child)
    for keyword in ("items", "additionalProperties", "not"):
        if isinstance(schema.get(keyword), dict):
            yield from schema_nodes(schema[keyword])
    for keyword in ("anyOf", "oneOf", "allOf", "prefixItems"):
        for child in schema.get(keyword, []):
            yield from schema_nodes(child)


@pytest.mark.parametrize("family", ["claude", "openai", "gemini"])
def test_provider_schemas_preserve_valid_mcp_arguments(family, definitions):
    from jsonschema import Draft202012Validator

    from qa.schemas import provider_schema

    original = copy.deepcopy(definitions)
    examples = {
        "rank": {"use_case": "coding", "environment": {"hardware": None}},
        "model_info": {"model_id": "lab/a"},
        "list_use_cases": {},
        "policy_check": {"policy": {"commercial_use": {"required": True}}},
        "vocab": {"section": "providers"},
        "feedback": {"rating": "confusing"},
        "decide": {
            "spec_version": 1,
            "capabilities": {"software_engineering": "required"},
            "optimize": {
                "weights": {
                    "reasoning": 0.6,
                    "model.class": {"prefer": "text-generator", "weight": 0.4},
                }
            },
            "where": [{"all": [{"any": [{"not": {"all": ["model.context_window >= 4000"]}}]}]}],
        },
    }
    for tool in definitions:
        schema = provider_schema(tool["input_schema"], family)
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(tool["input_schema"]).validate(examples[tool["name"]])
        Draft202012Validator(schema).validate(examples[tool["name"]])
        assert len(json.dumps(schema)) < 100_000
        for node in schema_nodes(schema):
            assert not {"$ref", "$defs", "$schema", "default", "title", "x-meaning"} & node.keys()
            if family == "gemini":
                assert (
                    not {
                        "additionalProperties",
                        "patternProperties",
                        "oneOf",
                        "prefixItems",
                        "const",
                        "exclusiveMinimum",
                        "exclusiveMaximum",
                    }
                    & node.keys()
                )
            if "type" in node:
                assert isinstance(node["type"], str)
        if tool["name"] == "decide":
            assert schema["required"] == ["spec_version", "optimize"]
            assert schema["properties"]["spec_version"]["enum"] == [1]
            if family == "gemini":
                assert (
                    "patternProperties"
                    in schema["properties"]["capabilities"]["anyOf"][0]["description"]
                )
                assert "additionalProperties: false" in schema["description"]
    assert definitions == original


@pytest.mark.parametrize("family", ["claude", "openai", "gemini"])
def test_schema_annotations_do_not_strip_parameter_names(family):
    from qa.schemas import provider_schema

    schema = {
        "type": "object",
        "properties": {
            name: {"type": "string"}
            for name in ("title", "default", "$ref", "additionalProperties")
        },
        "required": ["title"],
    }
    assert provider_schema(schema, family)["properties"] == schema["properties"]


@pytest.mark.parametrize("family", ["claude", "openai", "gemini"])
def test_local_pointer_escaping_and_unsupported_constraints(family):
    from qa.schemas import provider_schema

    schema = {
        "$ref": "#/$defs/a~1b~0c",
        "$defs": {
            "a/b~c": {
                "type": "object",
                "properties": {"value": {"type": "number", "madeUp": 7}},
            }
        },
    }
    result = provider_schema(schema, family)
    assert result["type"] == "object"
    assert "madeUp: 7" in result["properties"]["value"]["description"]
    with pytest.raises(ValueError, match="local JSON pointers"):
        provider_schema({"$ref": "https://private.example/schema"}, family)
    with pytest.raises(ValueError, match="single object root"):
        provider_schema({"anyOf": [{"type": "object"}, {"type": "string"}]}, family)


@pytest.mark.parametrize("family", ["claude", "openai", "gemini"])
@pytest.mark.parametrize("status", [400, 401, 403, 404, 422, 429, 500, 503])
def test_provider_http_error_is_private_redacted_and_rejected_calls_are_free(
    family,
    status,
    monkeypatch,
    config,
    tmp_path,
    capsys,
    caplog,
):
    from qa.agent_harness import write_report
    from qa.providers import KEY_ENV

    monkeypatch.setenv(KEY_ENV[family], "environment-secret")
    error = {
        "type" if family != "gemini" else "status": "invalid_request_error",
        "message": (
            "private-diagnostic environment-secret sk-ant-abcdefgh123456 AIzaabcdefgh123456 "
            "live_abcdefghijklmnop Bearer opaque-secret " + "x" * 400
        ),
    }

    def handler(request):
        return httpx.Response(status, json={"error": error, "unrelated": "do-not-capture"})

    budget = Budget(2)
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        agent = HttpAgent(
            family, "model", "docs", "question", [], budget, {"input": 2, "output": 10}, 100, client
        )
        row = run_scenario(load_scenarios()[0], family, agent, None, None, config)
        assert row["status"] == "provider_error" and row["error"] == f"{family} HTTP {status}"
        details = row["provider_error"]
        assert details["http_status"] == status and details["type"] == "invalid_request_error"
        assert details["message"].startswith("private-diagnostic [REDACTED]")
        assert len(details["message"]) == 300
        serialized = json.dumps(row)
        for secret in (
            "environment-secret",
            "sk-ant-abcdefgh123456",
            "AIzaabcdefgh123456",
            "live_abcdefghijklmnop",
            "opaque-secret",
            "do-not-capture",
        ):
            assert secret not in serialized
        assert not row["tool_calls"] and row["tokens_in"] == row["tokens_out"] == 0
        if status < 500:
            assert budget.spent_usd == 0
            assert budget.calls[-1]["usage_known"]
            assert budget.calls[-1]["cost_usd"] == 0
            with pytest.raises(ProviderError) as caught:
                agent.step()
            assert "private-diagnostic" not in str(caught.value) + repr(caught.value)
            assert budget.spent_usd == 0
        else:
            assert budget.spent_usd > 0 and not budget.calls[-1]["usage_known"]
    # Write the actual run via the same private report writer, without a summary.
    from qa.agent_harness import make_report

    report = make_report(
        [row], load_scenarios()[:1], False, budget, "2026-10-02", {"agents": [family]}
    )
    _, path = write_report(report, tmp_path)
    assert json.loads(path.read_text())["runs"][0]["provider_error"] == details
    captured = capsys.readouterr()
    assert "private-diagnostic" not in captured.out + captured.err + caplog.text


@pytest.mark.parametrize("body", [None, [], {"error": "not-an-object"}])
def test_malformed_http_error_body_is_not_captured(body, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "offline-key")
    with httpx.Client(
        transport=httpx.MockTransport(
            lambda r: (
                httpx.Response(400, json=body)
                if body is not None
                else httpx.Response(400, text="private HTML")
            )
        )
    ) as client:
        budget = Budget(2)
        agent = HttpAgent(
            "claude",
            "model",
            "docs",
            "question",
            [],
            budget,
            {"input": 2, "output": 10},
            100,
            client,
        )
        with pytest.raises(ProviderError) as caught:
            agent.step()
    assert caught.value.details == {"http_status": 400}
    assert budget.spent_usd == 0


@pytest.mark.parametrize(
    "status,usage", [(408, None), (400, {"input_tokens": 2, "output_tokens": 0}), (400, "unknown")]
)
def test_ambiguous_4xx_usage_keeps_the_reservation(status, usage, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "offline-key")
    with httpx.Client(
        transport=httpx.MockTransport(lambda r: httpx.Response(status, json={"usage": usage}))
    ) as client:
        budget = Budget(2)
        agent = HttpAgent(
            "claude",
            "model",
            "docs",
            "question",
            [],
            budget,
            {"input": 2, "output": 10},
            100,
            client,
        )
        with pytest.raises(ProviderError):
            agent.step()
    assert budget.spent_usd > 0 and not budget.calls[-1]["usage_known"]


def test_live_vocabulary_compacts_a_legacy_worker_during_rollout(config, definitions):
    source = {
        "vocabulary_version": 1,
        "facets": [{"id": "model.context_window", "label": "Context", "definition": "Token window. More details.", "value_type": "number", "has_data": True}],
        "templates": [{"spec": {"where": ["model.context_window >= 32000"]}}],
    }
    with httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(200, json=source))) as client:
        shim = LiveTools(config, definitions, "fixture-key", client)
        observed = shim.execute("vocab", {})
        envelope = json.loads(observed["result"]["content"][0]["text"])
    assert envelope["body"]["starter"] == [{"id": "model.context_window", "label": "Context", "definition": "Token window.", "value_type": "number"}]


@pytest.mark.parametrize("name,args", [
    ("vocab", {}),
    ("model_info", {"model_id": "lab/a"}),
    ("list_use_cases", {}),
    ("rank", {"use_case": "coding"}),
    ("policy_check", {"policy": {}}),
    ("decide", {"spec_version": 1, "optimize": {"min": "offering.cost_per_task"}}),
])
def test_data_shim_without_a_key_names_the_env_var_before_http(config, definitions, name, args):
    with httpx.Client(transport=httpx.MockTransport(
            lambda request: pytest.fail("a keyless machine tool reached HTTP"))) as client:
        shim = LiveTools(config, definitions, None, client)
        result = shim.execute(name, args)
    assert result["api_call"] is False
    error = json.loads(result["result"]["content"][0]["text"])["body"]["error"]
    assert error["code"] == "missing_api_key"
    assert "MODELSPEC_API_KEY" in error["message"]
    assert error["how_to_get_a_key"] == "https://modelspec.dev/pricing"


def test_production_vocabulary_smoke_without_a_key_stops_before_http(monkeypatch, tmp_path, capsys):
    monkeypatch.delenv("MODELSPEC_API_KEY", raising=False)
    monkeypatch.setattr(httpx.Client, "get", lambda *a, **kw: pytest.fail("keyless production HTTP"))
    with pytest.raises(SystemExit) as stopped:
        main(["--smoke-vocabulary", "--output-dir", str(tmp_path)])
    assert stopped.value.code == 2
    assert "MODELSPEC_API_KEY" in capsys.readouterr().err


def test_production_vocabulary_smoke_sends_the_key_without_saving_it(monkeypatch, tmp_path):
    from qa.agent_harness import smoke_vocabulary

    key = "offline-vocabulary-key"
    monkeypatch.setenv("MODELSPEC_API_KEY", key)
    requests = []

    def get(self, url, *, headers):
        assert headers["authorization"] == f"Bearer {key}"
        requests.append(url)
        return httpx.Response(200, request=httpx.Request("GET", url), json={
            "facets": [{"id": "model.context_window"}], "templates": [], "snapshot": "offline",
        })

    monkeypatch.setattr(httpx.Client, "get", get)
    output = tmp_path / "vocabulary-smoke.json"
    report = smoke_vocabulary(output)
    assert requests == ["https://api.modelspec.dev/v1/vocabulary"]
    assert report["keyless"] is False and report["facets"] == 1
    assert key not in output.read_text()


def test_markdown_names_isolation_misuse_rows():
    row = {
        "scenario": "budget-approved",
        "family": "F1",
        "agent": "codex",
        "status": "isolation_misuse",
        "success": False,
        "expected_match": None,
        "tool_calls": [],
        "judge": None,
        "isolation_misuse": ["mcp__bash"],
    }
    report = make_report(
        [row],
        [{"id": "budget-approved", "family": "F1"}],
        False,
        Budget(1),
        "2026-10-04",
        {"agents": ["codex"]},
    )
    text = markdown(report)
    assert "Isolation misuse keeps the doctor receipt and counts as a failure." in text
    assert "- budget-approved / codex / agent: mcp__bash" in text
