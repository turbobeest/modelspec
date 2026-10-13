"""Offline proxy traffic. The only HTTP sockets used are local fixture servers."""

from __future__ import annotations

import copy
from datetime import date
import json
import os
from pathlib import Path

import httpx
import pytest
import yaml

from decision.bounded import AGENT_BYTES, agent_summary, project
from decision.contract import Decision, ResponseOptions, parse_spec
from decision.engine import decide
from decision.registry import facet
from decision.summary import SUMMARY_BYTES, summarize
from qa import tui_harness as harness
from qa import tui_homes as homes
from qa.ablation_proxy import (
    DECIDE_WORKED_EXAMPLE,
    HEADER,
    LEGACY_COPY,
    OLD_SUMMARY_RULE,
    SUMMARY_RULE,
    CompleteFetchError,
    CopyDriftError,
    RewriteError,
    Variants,
    metadata,
    packed,
    proxy_port,
    rewrite,
    running_proxy,
    sse_event,
    text_bytes,
)
from qa.docker.entrypoint import VENDOR_ENV
from tests.test_decide_worker import snapshot as make_snapshot
from tests.test_decide_worker import snapshot_bytes as make_snapshot_bytes
from tests.test_decision_summary import _tied


@pytest.fixture(autouse=True)
def no_vendor_credentials(monkeypatch):
    for name in tuple(os.environ):
        if VENDOR_ENV.search(name) and not name.startswith("MODELSPEC_"):
            monkeypatch.delenv(name)


@pytest.fixture
def decision_case(proxy_snapshot):
    arguments = {
        "spec_version": 1,
        "optimize": {"max": "swe_bench_pro"},
        "where": ["offering.provider = sambanova"],
        "task_type": "review",
        "explain": "summary",
        "limit": 10,
    }
    spec = parse_spec(arguments, facets=None)
    full = decide(spec, proxy_snapshot)
    bounded = project(full, ResponseOptions(fields=["model"]), spec=spec, not_applied=[])
    bounded.pop("next_move", None)
    bounded["bounded_version"] = "1.1"
    bounded["summary_for_user"], bounded["must_mention"] = summarize(full, spec)
    envelope = {"origin": "https://api.modelspec.dev/v1/decide", "status": 200, "body": bounded}
    message = {
        "jsonrpc": "2.0",
        "id": 7,
        "result": {
            "content": [
                {"type": "text", "text": packed(envelope).decode()},
                {"type": "text", "text": agent_summary(bounded)},
            ],
            "isError": False,
        },
    }
    call = {"id": 7, "method": "tools/call", "params": {"name": "decide", "arguments": arguments}}

    def complete(raw):
        return decide(parse_spec(raw, facets=None), proxy_snapshot)

    return message, call, complete


@pytest.fixture(scope="module")
def proxy_snapshot():
    return make_snapshot.__wrapped__(make_snapshot_bytes.__wrapped__())


def body(message):
    return json.loads(message["result"]["content"][0]["text"])["body"]


def legacy_copy():
    return LEGACY_COPY["instructions"], LEGACY_COPY["tools"]["decide"]


def no_fetch(*args):
    pytest.fail("Unexpected complete fetch")


def test_passthrough_has_no_mutation_or_fetch(decision_case):
    message, call, _complete = decision_case
    result = rewrite(message, call, Variants(), no_fetch)
    assert result.message is message and result.fields == []
    assert result.before == result.after == text_bytes(message["result"])


def test_exact_summary_rule_and_example_match_generated_copy():
    instructions, description = legacy_copy()
    initialized = rewrite(
        {"id": 1, "result": {"instructions": instructions}},
        {"id": 1, "method": "initialize"},
        Variants(next_move=True),
        no_fetch,
    )
    assert initialized.message["result"]["instructions"] == instructions.replace(OLD_SUMMARY_RULE, SUMMARY_RULE)
    for variants in (Variants(next_move=True), Variants(worked_example=True), Variants(True, True)):
        message = {
            "id": 2,
            "result": {
                "tools": [
                    {"name": "decide", "description": description},
                    {"name": "rank", "description": LEGACY_COPY["tools"]["rank"]},
                ]
            },
        }
        result = rewrite(message, {"id": 2, "method": "tools/list"}, variants, no_fetch)
        actual = result.message["result"]["tools"][0]["description"]
        expected = (
            description.replace(OLD_SUMMARY_RULE, SUMMARY_RULE)
            if variants.next_move
            else description
        )
        expected += DECIDE_WORKED_EXAMPLE if variants.worked_example else ""
        assert actual == expected
        assert result.message["result"]["tools"][1]["description"] == LEGACY_COPY["tools"]["rank"]
        assert message["result"]["tools"][0]["description"] == description


@pytest.mark.parametrize(
    "text", ["new upstream wording", OLD_SUMMARY_RULE * 2, SUMMARY_RULE, None, 1]
)
def test_copy_drift_refuses_exact_replacement(text):
    with pytest.raises(CopyDriftError, match="SUMMARY_RULE drifted"):
        rewrite(
            {"id": 1, "result": {"instructions": text}},
            {"id": 1, "method": "initialize"},
            Variants(next_move=True),
            no_fetch,
        )


def test_example_anchor_drift_refuses():
    with pytest.raises(CopyDriftError, match="insertion point"):
        rewrite(
            {"id": 1, "result": {"tools": [{"name": "decide", "description": "changed ending"}]}},
            {"id": 1, "method": "tools/list"},
            Variants(worked_example=True),
            no_fetch,
        )


def test_complete_fetch_recovers_fields_and_verifies_pinned_identity(decision_case):
    message, call, complete = decision_case
    # The MCP projection has lost both candidates and may_qualify, as a drill-down can.
    old = body(message)
    old["results"] = []
    old["may_qualify"] = []
    message["result"]["content"][0]["text"] = packed({"status": 200, "body": old}).decode()
    message["result"]["content"][1]["text"] = agent_summary(old)
    call["params"]["arguments"].update(fields=["model"], evidence_for="lab/a")
    seen = []

    def fetch(raw):
        seen.append(raw)
        return complete(raw)

    result = rewrite(message, call, Variants(next_move=True), fetch)
    updated = body(result.message)
    assert len(seen) == 1
    assert seen[0]["snapshot"] == old["snapshot"]
    assert seen[0]["limit"] == 500
    assert "fields" not in seen[0] and "evidence_for" not in seen[0]
    assert updated["next_move"]["candidates"] == ["lab/a", "lab/b"]
    assert updated["summary_for_user"].endswith(" " + updated["next_move"]["say"])
    assert result.counters == {"complete_fetch": 1, "identity_snapshot_limit_pin": 1,
                               "next_move_added": 1, "v1_body_present": 1, "v4_absent": 1}
    assert "next_move" not in body(message)


@pytest.mark.parametrize("pin_snapshot,limit,identity", [
    (False, 500, "snapshot_pin"), (True, 10, "limit_pin"), (True, 500, "matched"),
])
def test_identity_accepts_snapshot_and_limit_pins(decision_case, pin_snapshot, limit, identity):
    message, call, complete = decision_case
    snapshot_id = body(message)["snapshot"]
    if pin_snapshot:
        call["params"]["arguments"]["snapshot"] = snapshot_id
    call["params"]["arguments"]["limit"] = limit
    full = complete(call["params"]["arguments"])
    original = body(message) | {"spec_hash": full.spec_hash, "decision_id": full.decision_id}
    message["result"]["content"][0]["text"] = packed({"status": 200, "body": original}).decode()
    result = rewrite(message, call, Variants(next_move=True), complete)
    assert result.counters["identity_" + identity] == 1


@pytest.mark.parametrize("where", [[], ["model.max_output_tokens >= 8000"]])
def test_serialized_complete_fetch_matches_server_move_before_agent_limit(where):
    from decision.snapshot import SnapshotInputs, build_snapshot, load_snapshot_bytes
    from tests.snapshot_records import SOURCES, fact, model

    models = []
    for index in range(1, 13):
        mid = f"lab/m{index:02d}"
        facts = [fact("model", mid, "model.context_window", index * 10000),
                 fact("model", mid, "model.parameters_total", index * 1000000)]
        if index != 2:
            facts.append(fact("model", mid, "model.max_output_tokens", 8000))
        models.append(model(mid, facts=facts))
    built = build_snapshot(SnapshotInputs(models=models, sources=SOURCES), as_of=date(2026, 9, 25))
    snapshot = load_snapshot_bytes(built.to_bytes(key=b"proxy-test"), key=b"proxy-test")
    arguments = {"spec_version": 1, "task_type": "review", "where": where, "limit": 3,
                 "explain": "none", "optimize": {"lexicographic": [
                     {"max": "model.context_window"}, {"max": "model.parameters_total"},
                 ]}}
    spec = parse_spec(arguments, facets=facet)
    full = decide(spec, snapshot, facets=facet)
    assert full.answer is None and full.truncated.models > 0
    server = project(full, ResponseOptions(fields=["model"]), spec=spec, not_applied=[])
    expected = packed(server.pop("next_move"))
    server["summary_for_user"], server["must_mention"] = summarize(full, spec)
    message = {"id": 7, "result": {"content": [
        {"type": "text", "text": packed({"status": 200, "body": server}).decode()},
    ]}}
    call = {"id": 7, "method": "tools/call", "params": {"name": "decide", "arguments": arguments}}

    def fetch(raw):
        complete = decide(parse_spec(raw, facets=facet), snapshot, facets=facet)
        serialized = Decision.model_validate(json.loads(complete.model_dump_json()))
        assert serialized._feasible_models is None
        return serialized

    result = rewrite(message, call, Variants(next_move=True), fetch)
    assert packed(body(result.message)["next_move"]) == expected
    assert body(result.message)["next_move"]["candidates_total"] == 12


@pytest.mark.parametrize("annotations", [False, True])
def test_truncated_complete_candidates_pass_through_and_are_counted(decision_case, annotations):
    message, call, complete = decision_case

    def truncated(raw):
        decision = complete(raw)
        decision.truncated.models = 1
        return decision

    result = rewrite(message, call, Variants(next_move=True, annotations=annotations), truncated)
    assert result.message is message and result.fields == []
    assert result.before == result.after == text_bytes(message["result"])
    assert result.counters["candidates_truncated"] == 1
    assert "next_move" not in body(result.message)


def test_complete_answer_drift_is_refused(decision_case):
    message, call, complete = decision_case
    old = body(message)
    old["answer"] = _tied(["lab/unexpected-a", "lab/unexpected-b"])
    message["result"]["content"][0]["text"] = packed({"status": 200, "body": old}).decode()
    with pytest.raises(RewriteError, match="answer drifted"):
        rewrite(message, call, Variants(next_move=True), complete)


def test_identity_drift_never_uses_bounded_fallback(decision_case):
    message, call, complete = decision_case

    def wrong(raw):
        decision = complete(raw)
        decision.spec_hash = "sha256:" + "f" * 64
        return decision

    with pytest.raises(RewriteError, match="identity drifted"):
        rewrite(message, call, Variants(next_move=True), wrong)


def test_failed_fetch_counts_bounded_fallback(decision_case):
    message, call, _complete = decision_case

    def failed(raw):
        raise CompleteFetchError()

    result = rewrite(message, call, Variants(next_move=True), failed)
    assert result.counters["bounded_fallback"] == 1
    assert body(result.message)["next_move"]["kind"] == "decide_by_testing"


def test_annotations_use_exact_updated_summary_as_second_text(decision_case):
    message, call, complete = decision_case
    result = rewrite(message, call, Variants(next_move=True, annotations=True), complete)
    content = result.message["result"]["content"]
    assert len(content) == 2
    assert content[1] == {
        "type": "text",
        "text": body(result.message)["summary_for_user"],
        "annotations": {"audience": ["user"]},
    }
    assert result.after == sum(len(item["text"].encode()) for item in content)


def test_error_response_never_fetches_or_adds_annotations(decision_case):
    message, call, _complete = decision_case
    message["result"]["isError"] = True
    result = rewrite(message, call, Variants(next_move=True, annotations=True), no_fetch)
    assert result.message is message and result.fields == []


def test_budget_counts_both_texts_and_passes_through_all_or_nothing(decision_case):
    message, call, complete = decision_case
    # Pad the envelope, keeping the recognised legacy summary intact.
    envelope = json.loads(message["result"]["content"][0]["text"])
    envelope["padding"] = ""
    message["result"]["content"][0]["text"] = packed(envelope).decode()
    base = text_bytes(message["result"])
    envelope["padding"] = "x" * (AGENT_BYTES - base - 2)
    message["result"]["content"][0]["text"] = packed(envelope).decode()
    unchanged = copy.deepcopy(message)
    result = rewrite(message, call, Variants(next_move=True), complete)
    assert result.message == unchanged and result.message is message
    assert result.fields == [] and result.counters["budget_passthrough"] == 1
    assert result.before == result.after < AGENT_BYTES


def test_summary_reserves_verbatim_ending_and_records_trim_gap(decision_case):
    message, call, complete = decision_case
    old = body(message)
    first = "ModelSpec's answer is incomplete, so it names no pick."
    old["summary_for_user"] = first + " " + "An additional caveat. " * 50
    message["result"]["content"][0]["text"] = packed({"status": 200, "body": old}).decode()
    result = rewrite(message, call, Variants(next_move=True), complete)
    summary = body(result.message)["summary_for_user"]
    assert summary.startswith(first)
    assert summary.endswith(" " + body(result.message)["next_move"]["say"])
    assert len(summary.encode()) <= SUMMARY_BYTES
    assert result.counters["summary_trim_gap"] == 1


def test_sse_preserves_other_lines_and_passthrough_bytes(tmp_path):
    instructions, _description = legacy_copy()
    call = {"id": 2, "method": "initialize"}
    wire = packed({"id": 2, "result": {"instructions": instructions}})
    event = (
        b": heartbeat\r\nevent: message\r\nid: sse-4\r\nretry: 1000\r\ndata: " + wire + b"\r\n\r\n"
    )
    with running_proxy(Variants(), tmp_path / "baseline", port=0) as proxy:
        assert sse_event(proxy, event, call, None) == event
    with running_proxy(Variants(next_move=True), tmp_path / "v1", port=0) as proxy:
        result = sse_event(proxy, event, call, None)
        assert result.startswith(b": heartbeat\r\nevent: message\r\nid: sse-4\r\nretry: 1000\r\n")
        assert result.endswith(b"\r\n\r\n")
        assert SUMMARY_RULE.encode() in result


@pytest.mark.parametrize("sse", [False, True])
def test_http_forwarding_sessions_auth_and_json_or_sse_without_logging(
    tmp_path, capsys, monkeypatch, sse
):
    secret = "sentinel-auth-ablation-proxy-secret"
    private_value = "sentinel-other-modelspec-value"
    monkeypatch.setenv("MODELSPEC_API_KEY", secret)
    monkeypatch.setenv("MODELSPEC_PRIVATE_TEST", private_value)
    instructions, _description = legacy_copy()
    seen = []
    wire = packed({"jsonrpc": "2.0", "id": 3, "result": {"instructions": instructions}})
    stream = b"event: message\r\nid: 42\r\ndata: " + wire + b"\r\n\r\n"

    def upstream(request):
        seen.append(request)
        assert request.headers["authorization"] == "Custom " + secret
        assert request.headers["mcp-session-id"] == "session-in"
        return httpx.Response(
            200,
            content=stream if sse else wire,
            headers={
                "Content-Type": "text/event-stream" if sse else "application/json",
                "Mcp-Session-Id": "session-out",
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(upstream))
    with running_proxy(Variants(next_move=True), tmp_path / "logs", port=0, client=client) as proxy:
        port = proxy_port(proxy.audit.info["proxy_url"])
        with httpx.Client(trust_env=False) as incoming:
            response = incoming.post(
                f"http://127.0.0.1:{port}/mcp",
                json={"id": 3, "method": "initialize"},
                headers={"Authorization": "Custom " + secret, "Mcp-Session-Id": "session-in"},
            )
            assert response.status_code == 200
            assert response.headers["mcp-session-id"] == "session-out"
            assert json.loads(response.headers[HEADER])["variants"] == ["v1"]
            assert SUMMARY_RULE.encode() in response.content
        assert proxy.audit.snapshot()["counters"]["instructions"] == 1
    assert len(seen) == 1
    logged = "".join(path.read_text() for path in (tmp_path / "logs").iterdir())
    assert secret not in logged and private_value not in logged and instructions not in logged
    assert secret not in capsys.readouterr().out


def test_complete_http_post_forwards_only_in_memory_auth(decision_case, tmp_path):
    message, call, complete = decision_case
    original = body(message)
    calls = []

    def upstream(request):
        calls.append(request)
        assert request.headers["authorization"] == "Bearer fixture-token"
        if request.url.path == "/mcp":
            return httpx.Response(200, json=message)
        assert request.url.path == "/v1/decide"
        raw = json.loads(request.content)
        assert "fields" not in raw and "evidence_for" not in raw
        assert raw["snapshot"] == original["snapshot"]
        assert raw["limit"] == 500
        return httpx.Response(200, json=complete(raw).model_dump(mode="json"))

    call["params"]["arguments"].update(fields=["model"], evidence_for="lab/a")
    with running_proxy(
        Variants(next_move=True),
        tmp_path / "logs",
        port=0,
        client=httpx.Client(transport=httpx.MockTransport(upstream)),
    ) as proxy:
        port = proxy_port(proxy.audit.info["proxy_url"])
        response = httpx.post(
            f"http://127.0.0.1:{port}/mcp",
            json=call,
            headers={"Authorization": "Bearer fixture-token"},
            trust_env=False,
        )
        assert response.status_code == 200
        assert body(response.json())["next_move"]["kind"] == "decide_by_testing"
        assert proxy.audit.snapshot()["counters"]["complete_fetch"] == 1
    assert [request.url.path for request in calls] == ["/mcp", "/v1/decide"]
    assert "fixture-token" not in (tmp_path / "logs/calls.jsonl").read_text()


def test_copy_drift_is_loud_http_failure_and_safe_counter(tmp_path):
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200, json={"id": 1, "result": {"instructions": "upstream changed"}}
            )
        )
    )
    with running_proxy(Variants(next_move=True), tmp_path / "logs", port=0, client=client) as proxy:
        port = proxy_port(proxy.audit.info["proxy_url"])
        response = httpx.post(
            f"http://127.0.0.1:{port}/mcp", json={"id": 1, "method": "initialize"}, trust_env=False
        )
        assert response.status_code == 502 and HEADER in response.headers
        info = proxy.audit.snapshot()
        assert info["failures"] == {"Upstream SUMMARY_RULE drifted": 1}
        assert info["counters"]["proxy_error"] == 1


def test_sse_drift_returns_protocol_error_and_counts_failure(tmp_path):
    wire = b'event: message\ndata: {"id":1,"result":{"instructions":"changed"}}\n\n'
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200, content=wire, headers={"Content-Type": "text/event-stream"}
            )
        )
    )
    with running_proxy(Variants(next_move=True), tmp_path / "logs", port=0, client=client) as proxy:
        port = proxy_port(proxy.audit.info["proxy_url"])
        response = httpx.post(
            f"http://127.0.0.1:{port}/mcp", json={"id": 1, "method": "initialize"}, trust_env=False
        )
        assert response.status_code == 200 and HEADER in response.headers
        error = json.loads(response.content.split(b"data: ", 1)[1].strip())
        assert error == {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {"code": -32603, "message": "Upstream SUMMARY_RULE drifted"},
        }
        assert proxy.audit.snapshot()["counters"]["proxy_error"] == 1


def test_get_delete_and_notification_forward_session_and_receive_audit_headers(tmp_path):
    seen = []
    event = b': heartbeat\r\nevent: message\r\ndata: {"jsonrpc":"2.0","method":"ping"}\r\n\r\n'

    def upstream(request):
        assert request.headers["mcp-session-id"] == "fixture-session"
        seen.append(request.method)
        if request.method == "GET":
            return httpx.Response(200, content=event, headers={"Content-Type": "text/event-stream"})
        return httpx.Response(202 if request.method == "POST" else 204)

    with running_proxy(
        Variants(),
        tmp_path / "logs",
        port=0,
        client=httpx.Client(transport=httpx.MockTransport(upstream)),
    ) as proxy:
        port = proxy_port(proxy.audit.info["proxy_url"])
        with httpx.Client(trust_env=False, headers={"Mcp-Session-Id": "fixture-session"}) as client:
            url = f"http://127.0.0.1:{port}/mcp"
            assert client.get(url).content == event
            notification = client.post(
                url, json={"jsonrpc": "2.0", "method": "notifications/initialized"}
            )
            assert notification.status_code == 202 and HEADER in notification.headers
            deleted = client.delete(url)
            assert deleted.status_code == 204 and HEADER in deleted.headers
        assert proxy.audit.snapshot()["counters"]["responses"] == 4
    assert seen == ["GET", "POST", "DELETE"]


def test_named_profile_refuses_instead_of_approximating_hidden_rules(decision_case):
    message, call, _complete = decision_case
    call["params"]["arguments"]["profile"] = "profile:private-profile"
    with pytest.raises(RewriteError, match="inline profile"):
        rewrite(message, call, Variants(next_move=True), no_fetch)


def test_unsupported_http_methods_still_receive_audit_header(tmp_path):
    client = httpx.Client(transport=httpx.MockTransport(lambda request: pytest.fail("Upstream")))
    with running_proxy(Variants(), tmp_path / "logs", port=0, client=client) as proxy:
        port = proxy_port(proxy.audit.info["proxy_url"])
        with httpx.Client(trust_env=False) as incoming:
            for method in ["HEAD", "OPTIONS"]:
                response = incoming.request(method, f"http://127.0.0.1:{port}/mcp")
                assert response.status_code == 501 and HEADER in response.headers
        assert proxy.audit.snapshot()["counters"]["responses"] == 2


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost:8765/mcp",
        "http://127.0.0.1:8765/mcp",
        "http://host.docker.internal/mcp",
        "http://host.docker.internal:0/mcp",
        "http://host.docker.internal:65536/mcp",
        "http://host.docker.internal:8765/mcp?key=secret",
        "http://user@host.docker.internal:8765/mcp",
        "http://host.docker.internal:8765/mcp#frag",
        "http://host.docker.internal:8765/mcp/",
        "https://host.docker.internal:8765/mcp",
    ],
)
def test_harness_refuses_every_other_proxy_url(url):
    config = yaml.safe_load((harness.HERE / "tui_config.yaml").read_text())
    config["mcp_url"] = url
    with pytest.raises(ValueError):
        harness.validate_config(config, ablation_proxy=url)


def test_http_requires_explicit_opt_in_and_private_state(tmp_path):
    config = yaml.safe_load((harness.HERE / "tui_config.yaml").read_text())
    original = copy.deepcopy(config)
    url = "http://host.docker.internal:8765/mcp"
    config["mcp_url"] = url
    with pytest.raises(ValueError, match="HTTPS"):
        harness.validate_config(config)
    info = metadata(Variants(next_move=True), url)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(info))
    harness.apply_ablation_proxy(config, url, tmp_path, metadata_path=manifest, dry_run=True)
    assert config["ablation"] == info
    row = harness.empty_row({"id": "fixture", "family": "F1"}, "claude", config, "dry_run")
    assert row["ablation"] == info
    assert "ablation" not in harness.empty_row(
        {"id": "fixture", "family": "F1"}, "claude", original, "dry_run"
    )
    with pytest.raises(ValueError, match="subscription-jobs"):
        harness.apply_ablation_proxy(
            config,
            url,
            Path.home() / "Library/Application Support/ModelSpec/subscription-jobs",
            metadata_path=manifest,
            dry_run=True,
        )


def test_receipt_identity_and_directory_are_private_and_variant_specific(tmp_path, monkeypatch):
    config = yaml.safe_load((harness.HERE / "tui_config.yaml").read_text())
    config["_state_dir"] = str(tmp_path / ".tui-state")
    monkeypatch.setattr(homes, "binary_identity", lambda *a, **k: {})
    before = homes.isolation_identity("claude", config, {"fixture": "binary"})
    config["ablation"] = metadata(Variants(), "http://host.docker.internal:8765/mcp")
    config["mcp_url"] = config["ablation"]["proxy_url"]
    baseline = homes.isolation_identity("claude", config, {"fixture": "binary"})
    config["ablation"]["variants"] = ["v1"]
    variant = homes.isolation_identity("claude", config, {"fixture": "binary"})
    assert len({before, baseline, variant}) == 3
    assert homes.state_directory("claude", config) == tmp_path / ".tui-state/claude"
