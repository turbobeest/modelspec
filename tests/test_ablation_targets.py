"""Target convergence and failure isolation, using only recorded or local traffic."""

from __future__ import annotations

import copy
import gzip
import http.client
import json
import os
import time
from collections import Counter
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest

from qa import ablation, tui_harness
from qa.ablation_proxy import (
    AGENT_BYTES,
    DECIDE_WORKED_EXAMPLE,
    LEGACY_COPY,
    OLD_SUMMARY_RULE,
    SUMMARY_RULE,
    Audit,
    Handler,
    Rewrite,
    RewriteError,
    Variants,
    agent_summary,
    packed,
    proxy_port,
    rewrite,
    running_proxy,
    text_bytes,
)
from qa.docker.entrypoint import VENDOR_ENV
from tests import test_ablation_proxy as proxy_fixtures
from tests.test_ablation_proxy import body, no_fetch

decision_case = proxy_fixtures.decision_case
proxy_snapshot = proxy_fixtures.proxy_snapshot


@pytest.fixture(autouse=True)
def no_credentials(monkeypatch):
    for name in tuple(os.environ):
        if VENDOR_ENV.search(name):
            monkeypatch.delenv(name)


def expected_copy(variants):
    initialized = LEGACY_COPY["instructions"]
    tools = dict(LEGACY_COPY["tools"])
    if variants.next_move:
        initialized = initialized.replace(OLD_SUMMARY_RULE, SUMMARY_RULE)
        tools["decide"] = tools["decide"].replace(OLD_SUMMARY_RULE, SUMMARY_RULE)
    if variants.worked_example:
        tools["decide"] += DECIDE_WORKED_EXAMPLE
    return initialized, tools


@pytest.mark.parametrize("arm", ablation.ARMS)
@pytest.mark.parametrize("upstream_arm", ablation.ARMS)
def test_metadata_converges_every_direction_and_is_idempotent(arm, upstream_arm):
    initialized, descriptions = expected_copy(ablation.ARMS[upstream_arm])
    expected_instructions, expected_tools = expected_copy(ablation.ARMS[arm])
    responses = {
        "initialize": {"instructions": initialized},
        "tools/list": {
            "tools": [
                {"name": name, "description": text}
                for name, text in descriptions.items()
            ]
        },
    }
    for method, result in responses.items():
        message, call = {"id": 1, "result": result}, {"id": 1, "method": method}
        untouched = copy.deepcopy(message)
        first = rewrite(message, call, ablation.ARMS[arm], no_fetch)
        second = rewrite(first.message, call, ablation.ARMS[arm], no_fetch)
        assert second.message is first.message
        assert not second.fields
        assert message == untouched
        if method == "initialize":
            assert first.message["result"]["instructions"] == expected_instructions
        else:
            assert {
                t["name"]: t["description"] for t in first.message["result"]["tools"]
            } == expected_tools


@pytest.mark.parametrize("arm", ablation.ARMS)
def test_current_production_fixture_converges_exactly_to_pre682_plus_arm(arm):
    instructions, tools = expected_copy(ablation.ARMS[arm])
    for method, result in ablation.METADATA_FIXTURE["results"].items():
        message = {"id": 1, "result": copy.deepcopy(result)}
        outcome = rewrite(
            message, {"id": 1, "method": method}, ablation.ARMS[arm], no_fetch
        )
        if method == "initialize":
            assert (
                outcome.message["result"]["instructions"].encode()
                == instructions.encode()
            )
        else:
            assert {
                t["name"]: t["description"] for t in outcome.message["result"]["tools"]
            } == tools


@pytest.mark.parametrize("arm", ablation.ARMS)
@pytest.mark.parametrize("deployed", [False, True])
def test_decide_both_directions_and_idempotence(decision_case, arm, deployed):
    legacy, call, complete = decision_case
    incoming = (
        rewrite(legacy, call, Variants(True, True, True), complete).message
        if deployed
        else legacy
    )
    untouched = copy.deepcopy(incoming)
    variants = ablation.ARMS[arm]
    outcome = rewrite(incoming, call, variants, no_fetch if deployed else complete)
    actual = body(outcome.message)
    assert ("next_move" in actual) == variants.next_move
    assert actual["bounded_version"] == ("1.2" if variants.next_move else "1.1")
    if variants.next_move:
        assert actual["summary_for_user"].endswith(" " + actual["next_move"]["say"])
        assert (
            outcome.counters["next_move_upstream" if deployed else "next_move_added"]
            == 1
        )
    else:
        assert actual == body(legacy)
        if deployed:
            assert outcome.counters["next_move_removed"] == 1
            assert outcome.counters["summary_strip_trim_gap"] == 1
    expected = (
        {
            "type": "text",
            "text": actual["summary_for_user"],
            "annotations": {"audience": ["user"]},
        }
        if variants.annotations
        else {"type": "text", "text": agent_summary(actual)}
    )
    assert outcome.message["result"]["content"][1] == expected
    assert text_bytes(outcome.message["result"]) <= AGENT_BYTES
    repeated = rewrite(outcome.message, call, variants, no_fetch)
    assert repeated.message is outcome.message
    assert not repeated.fields
    assert incoming == untouched


def test_removal_strips_only_the_exact_trailing_say(decision_case):
    legacy, call, complete = decision_case
    incoming = rewrite(
        legacy, call, Variants(next_move=True, annotations=True), complete
    ).message
    envelope = json.loads(incoming["result"]["content"][0]["text"])
    move = envelope["body"]["next_move"]
    paragraph = "An interior quotation: " + move["say"] + " This stays."
    envelope["body"]["summary_for_user"] = paragraph + " " + move["say"]
    incoming["result"]["content"][0]["text"] = packed(envelope).decode()
    incoming["result"]["content"][1]["text"] = envelope["body"]["summary_for_user"]
    result = rewrite(incoming, call, Variants(), no_fetch)
    assert body(result.message)["summary_for_user"] == paragraph


@pytest.mark.parametrize("change", ["ending", "move", "annotation", "example", "copy"])
def test_unrecognised_deployed_state_fails_loudly(decision_case, change):
    legacy, call, complete = decision_case
    incoming = rewrite(legacy, call, Variants(True, True, True), complete).message
    if change in {"copy", "example"}:
        text = ablation.METADATA_FIXTURE["results"]["tools/list"]["tools"]
        incoming = {"id": 7, "result": {"tools": copy.deepcopy(text)}}
        tool = next(t for t in incoming["result"]["tools"] if t["name"] == "decide")
        tool["description"] = (
            tool["description"].replace("offer it instead of a pick", "offer a pick")
            if change == "copy"
            else tool["description"] + " Unexpected example."
        )
        call = {"id": 7, "method": "tools/list"}
    else:
        envelope = json.loads(incoming["result"]["content"][0]["text"])
        if change == "ending":
            envelope["body"]["summary_for_user"] += " drift"
            incoming["result"]["content"][1]["text"] += " drift"
        elif change == "move":
            envelope["body"]["next_move"]["kind"] = "pick"
        else:
            incoming["result"]["content"][1]["annotations"]["audience"] = ["assistant"]
        incoming["result"]["content"][0]["text"] = packed(envelope).decode()
    with pytest.raises(RewriteError):
        rewrite(incoming, call, Variants(), no_fetch)


@pytest.mark.parametrize("arm", ablation.ARMS)
@pytest.mark.parametrize("keyed", [False, True])
@pytest.mark.parametrize("sse", [False, True])
def test_preflight_uses_public_metadata_and_checks_keyed_body_locally(
    tmp_path, monkeypatch, decision_case, arm, keyed, sse
):
    legacy, call, complete = decision_case
    deployed = rewrite(legacy, call, Variants(True, True, True), complete).message[
        "result"
    ]
    seen = []
    key = "fixture-preflight-secret"
    monkeypatch.setenv("MODELSPEC_API_KEY", key)

    def upstream(request):
        rpc = json.loads(request.content)
        method = rpc["method"]
        seen.append(method)
        assert request.headers.get("authorization") == (
            "Bearer " + key if method == "tools/call" else None
        )
        result = (
            deployed
            if method == "tools/call"
            else ablation.METADATA_FIXTURE["results"][method]
        )
        message = {"jsonrpc": "2.0", "id": rpc["id"], "result": result}
        if sse:
            events = (
                b': heartbeat\r\n\r\ndata: {"jsonrpc":"2.0","method":"ping"}\r\n\r\ndata: '
                + packed(message)
                + b"\r\n\r\n"
            )
            return httpx.Response(
                200, content=events, headers={"Content-Type": "text/event-stream"}
            )
        return httpx.Response(200, json=message)

    with running_proxy(
        ablation.ARMS[arm],
        tmp_path / "proxy",
        port=0,
        client=httpx.Client(transport=httpx.MockTransport(upstream)),
    ) as proxy:
        check = ablation.preflight(proxy, keyed=keyed)
        assert check == {
            "metadata": "passed",
            "decide": "passed" if keyed else "skipped: no key",
        }
    assert seen == ["initialize", "tools/list"] + (["tools/call"] if keyed else [])
    assert key not in "".join(p.read_text() for p in (tmp_path / "proxy").iterdir())


def test_preflight_mismatch_aborts_only_that_arm(tmp_path, monkeypatch):
    checks, agents = [], []
    real_preflight, launch = ablation.preflight, ablation.FixtureReplay.launch

    def preflight(proxy, **kwargs):
        checks.append(proxy.variants.names())
        if proxy.variants.next_move:
            raise ValueError("Preflight initialize V1-copy state mismatch")
        return real_preflight(proxy, **kwargs)

    def capture(self, cli, *args, mcp_enabled, **kwargs):
        if mcp_enabled:
            agents.append(self.proxy.variants.names())
        return launch(self, cli, *args, mcp_enabled=mcp_enabled, **kwargs)

    monkeypatch.setattr(ablation, "preflight", preflight)
    monkeypatch.setattr(ablation.FixtureReplay, "launch", capture)
    out = tmp_path / "out"
    code = ablation.main(
        [
            "--dry-run",
            "--arms",
            "v1",
            "baseline",
            "v3",
            "--scenario",
            "budget-approved",
            "--out",
            str(out),
            "--state-dir",
            str(tmp_path / "state"),
        ]
    )
    assert code == 2
    assert checks == [["v1"], [], ["v3"]]
    assert agents == [[], ["v3"]]
    report = json.loads((out / "ablation.json").read_text())
    assert report["arms"]["v1"]["status"] == "INVALID"
    assert report["arms"]["v1"]["pass_rate"] is None
    assert report["runs"][0]["status"] == "INVALID"
    assert "V1-copy state mismatch" in report["arms"]["v1"]["reason"]
    assert "INVALID" in (out / "ablation.md").read_text()


def test_unexpected_harness_exception_still_continues_next_arm(tmp_path, monkeypatch):
    run = tui_harness.main
    calls = []

    def failed(arguments, **kwargs):
        calls.append(arguments)
        if len(calls) == 1:
            raise RuntimeError("private exception body")
        return run(arguments, **kwargs)

    monkeypatch.setattr(tui_harness, "main", failed)
    out = tmp_path / "out"
    assert (
        ablation.main(
            [
                "--dry-run",
                "--arms",
                "baseline",
                "v1",
                "--scenario",
                "budget-approved",
                "--out",
                str(out),
                "--state-dir",
                str(tmp_path / "state"),
            ]
        )
        == 2
    )
    assert len(calls) == 2
    report = json.loads((out / "ablation.json").read_text())
    assert report["arms"]["baseline"]["reason"] == "Arm failed with RuntimeError"
    assert len(report["runs"]) == 2
    assert "private exception body" not in (out / "ablation.json").read_text()


@pytest.mark.parametrize(
    "failure,reason",
    [("proxy_error", "Proxy error in scenario budget-approved")],
)
def test_first_scenario_proxy_error_stops_arm_and_continues_next(
    tmp_path, monkeypatch, failure, reason
):
    agents = []
    launch = ablation.FixtureReplay.launch

    def injected(self, cli, *args, mcp_enabled, **kwargs):
        if mcp_enabled:
            agents.append(self.proxy.variants.names())
            if not self.proxy.variants.names():
                self.proxy.audit.record(
                    {}, Rewrite({}, counters=Counter({failure: 1})), before=0, after=0
                )
        return launch(self, cli, *args, mcp_enabled=mcp_enabled, **kwargs)

    monkeypatch.setattr(ablation.FixtureReplay, "launch", injected)
    out = tmp_path / "out"
    assert (
        ablation.main(
            [
                "--dry-run",
                "--arms",
                "baseline",
                "v1",
                "--scenario",
                "budget-approved",
                "--scenario",
                "hardware-spark",
                "--out",
                str(out),
                "--state-dir",
                str(tmp_path / "state"),
            ]
        )
        == 2
    )
    assert agents == [[], ["v1"], ["v1"]]
    report = json.loads((out / "ablation.json").read_text())
    assert report["arms"]["baseline"]["status"] == "INVALID"
    assert report["arms"]["baseline"]["reason"] == reason
    assert [r["status"] for r in report["runs"][:2]] == ["INVALID", "INVALID"]
    assert len(report["runs"]) == 4


def wait_for_count(proxy, name):
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        counts = proxy.audit.snapshot()["counters"]
        if counts.get(name):
            return counts
        time.sleep(0.01)
    pytest.fail("Expected handler counter " + name)


@pytest.mark.parametrize("error", [BrokenPipeError, ConnectionResetError, ConnectionAbortedError])
def test_keepalive_reset_before_next_request_parse_preserves_completion(tmp_path, error):
    class ResetReader:
        def peek(self, size):
            return b"partial request line"

        def readline(self, size):
            raise error()

    audit = Audit(tmp_path / "proxy", {"variants": []})
    handler = Handler.__new__(Handler)
    handler.server = SimpleNamespace(proxy=SimpleNamespace(audit=audit))
    handler.rfile = ResetReader()
    handler.response_complete = True
    handler.close_connection = False
    handler.handle_one_request()
    counts = audit.snapshot()["counters"]
    assert counts["client_disconnect"] == 1
    assert not counts.get("proxy_error") and not counts.get("handler_error")
    assert handler.close_connection


@pytest.mark.parametrize("method", ["POST", "DELETE"])
@pytest.mark.parametrize("error", [BrokenPipeError, ConnectionResetError, ConnectionAbortedError])
@pytest.mark.parametrize("boundary", ["empty_write", "flush"])
def test_client_reset_after_complete_response_is_not_a_proxy_error(
    tmp_path, monkeypatch, method, error, boundary
):
    setup = Handler.setup

    def setup_disconnect(self):
        setup(self)
        operation = "write" if boundary == "empty_write" else "flush"
        original = getattr(self.wfile, operation)

        def disconnected(*args):
            if boundary == "empty_write" and args != (b"",):
                return original(*args)
            # The full response has already reached the client.
            # Raise once so handler cleanup cannot add another error.
            monkeypatch.setattr(self.wfile, operation, original)
            raise error()

        monkeypatch.setattr(self.wfile, operation, disconnected)

    monkeypatch.setattr(Handler, "setup", setup_disconnect)

    raw = b"complete" if method == "POST" and boundary == "flush" else b""

    def upstream(request):
        return httpx.Response(200 if request.method == "POST" else 204, content=raw)

    with running_proxy(
        Variants(),
        tmp_path / "proxy",
        port=0,
        client=httpx.Client(transport=httpx.MockTransport(upstream)),
    ) as proxy:
        with closing(http.client.HTTPConnection(
            "127.0.0.1", proxy_port(proxy.audit.info["proxy_url"]), timeout=2
        )) as connection:
            connection.request(method, "/mcp", body=b"{}" if method == "POST" else None)
            response = connection.getresponse()
            assert response.status == (200 if method == "POST" else 204)
            assert response.read() == raw
        counts = wait_for_count(proxy, "client_disconnect")
        assert counts["client_disconnect"] == 1
        assert not counts.get("handler_error") and not counts.get("proxy_error")


@pytest.mark.parametrize("error", [BrokenPipeError, ConnectionResetError, ConnectionAbortedError])
def test_disconnect_before_complete_response_is_a_proxy_error(tmp_path, monkeypatch, error):
    def incomplete(self, status, raw, headers, marker=None):
        self.send_response(200)
        self.send_header("Content-Length", "20")
        self.end_headers()
        self.wfile.write(b"partial")
        raise error()

    monkeypatch.setattr(Handler, "reply", incomplete)
    with running_proxy(
        Variants(),
        tmp_path / "proxy",
        port=0,
        client=httpx.Client(
            transport=httpx.MockTransport(lambda request: httpx.Response(204))
        ),
    ) as proxy:
        with pytest.raises(httpx.RemoteProtocolError):
            httpx.delete(
                f"http://127.0.0.1:{proxy_port(proxy.audit.info['proxy_url'])}/mcp",
                trust_env=False,
            )
        counts = wait_for_count(proxy, "handler_error")
        assert counts["handler_error"] == 1 and counts["proxy_error"] == 1
        assert not counts.get("client_disconnect")


@pytest.mark.parametrize("error", [BrokenPipeError, ConnectionResetError, ConnectionAbortedError])
@pytest.mark.parametrize("terminated", [False, True])
@pytest.mark.parametrize("multiline", [False, True])
def test_sse_disconnect_after_complete_rpc_is_not_a_proxy_error(
    tmp_path, monkeypatch, error, terminated, multiline
):
    setup = Handler.setup

    def setup_disconnect(self):
        setup(self)
        flush = self.wfile.flush

        def disconnected():
            monkeypatch.setattr(self.wfile, "flush", flush)
            raise error()

        monkeypatch.setattr(self.wfile, "flush", disconnected)

    monkeypatch.setattr(Handler, "setup", setup_disconnect)
    message = packed(
        {"id": 1, "result": ablation.METADATA_FIXTURE["results"]["initialize"]}
    )
    if multiline:
        message = message.replace(b",", b",\ndata: ", 1)
    event = b"event: message\ndata: " + message + (b"\n\n" if terminated else b"")
    upstream = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200, content=event, headers={"Content-Type": "text/event-stream"}
            )
        )
    )
    with running_proxy(
        Variants(), tmp_path / "proxy", port=0, client=upstream
    ) as proxy:
        reply = httpx.post(
            f"http://127.0.0.1:{proxy_port(proxy.audit.info['proxy_url'])}/mcp",
            json={"id": 1, "method": "ping" if multiline else "initialize"},
            trust_env=False,
        )
        assert reply.status_code == 200 and b'"result"' in reply.content
        counts = wait_for_count(proxy, "client_disconnect")
        assert counts["client_disconnect"] == 1
        assert not counts.get("handler_error") and not counts.get("proxy_error")


@pytest.mark.parametrize(
    "case",
    json.loads(
        (
            Path(__file__).resolve().parents[1]
            / "qa/fixtures/ablation-legacy-summaries.json"
        ).read_text()
    )["cases"],
    ids=lambda c: c["name"],
)
def test_legacy_summary_is_byte_equal_to_41125577_renderer(case):
    assert agent_summary(case["body"]).encode() == case["summary"].encode()


DECIDE_FIXTURES = json.loads(
    gzip.decompress(
        (
            Path(__file__).resolve().parents[1] / "qa/fixtures/ablation-decide.json.gz"
        ).read_bytes()
    )
)


@pytest.mark.parametrize("name", ["recall-q04", "recall-q09"])
@pytest.mark.parametrize("change", ["identity", "records"])
def test_unknown_projection_reports_uncertainty_instead_of_a_proven_gap(name, change):
    row = DECIDE_FIXTURES["default"][name]
    current = copy.deepcopy(row["post"]["body"])
    if change == "identity":
        current["snapshot"] = "unrecorded-snapshot"
    else:
        current["results"][0]["model"] = "unrecorded/model"
    message = {
        "id": 1,
        "result": {"content": [
            {"type": "text", "text": packed({"status": 200, "body": current}).decode()},
            {"type": "text", "text": current["summary_for_user"],
             "annotations": {"audience": ["user"]}},
        ]},
    }
    outcome = rewrite(
        message,
        {"id": 1, "method": "tools/call", "params": {"name": "decide"}},
        Variants(),
        no_fetch,
    )
    assert outcome.counters["upstream_projection_unverified"] == 1
    assert not outcome.counters.get("upstream_projection_gap")


@pytest.mark.parametrize("name", ablation.TUNING + ablation.HOLDOUT)
@pytest.mark.parametrize("projection", ["default", "fields_model"])
def test_actual_engine_stripping_and_documented_gaps(name, projection):
    row = DECIDE_FIXTURES[projection][name]
    current = row["post"]["body"]
    content = [
        {
            "type": "text",
            "text": packed({"status": row["post"]["status"], "body": current}).decode(),
        }
    ]
    if row["post"]["status"] == 200:
        content.append(
            {
                "type": "text",
                "text": current["summary_for_user"],
                "annotations": {"audience": ["user"]},
            }
        )
    message = {
        "id": 1,
        "result": {"isError": row["post"]["status"] >= 400, "content": content},
    }
    outcome = rewrite(
        message,
        {
            "id": 1,
            "method": "tools/call",
            "params": {"name": "decide", "arguments": row["post"]["arguments"]},
        },
        Variants(),
        no_fetch,
    )
    actual = body(outcome.message)
    expected = row["pre"]["body"]
    differences = {
        key
        for key in set(actual) | set(expected)
        if actual.get(key) != expected.get(key)
    }
    allowed = {"summary_for_user"} if name == "budget-approved" else set()
    budget_gaps = {
        "recall-q01": {"explanation", "may_qualify"},
        "recall-q02": {"explanation", "may_qualify"},
        "recall-q03": {"explanation", "may_qualify", "results"},
        "recall-q09": {"explanation", "results"},
    }
    if projection == "default" and name in budget_gaps:
        allowed |= budget_gaps[name]
        assert outcome.counters["upstream_projection_gap"] == 1
    else:
        assert not outcome.counters.get("upstream_projection_gap")
    assert differences == allowed
    if name == "budget-approved":
        assert (
            len(expected["summary_for_user"].encode())
            - len(actual["summary_for_user"].encode())
            == 128
        )
        assert outcome.counters["summary_strip_trim_gap"] == 1
    assert text_bytes(outcome.message["result"]) <= AGENT_BYTES
    repeated = rewrite(
        outcome.message,
        {"id": 1, "method": "tools/call", "params": {"name": "decide"}},
        Variants(),
        no_fetch,
    )
    assert repeated.message is outcome.message


def test_projection_gap_is_reported_but_does_not_invalidate_the_arm(tmp_path, monkeypatch):
    launch = ablation.FixtureReplay.launch

    def injected(self, cli, *args, mcp_enabled, **kwargs):
        if mcp_enabled and not self.proxy.variants.names():
            self.proxy.audit.record(
                {}, Rewrite({}, counters=Counter(upstream_projection_gap=1)), before=0, after=0
            )
        return launch(self, cli, *args, mcp_enabled=mcp_enabled, **kwargs)

    monkeypatch.setattr(ablation.FixtureReplay, "launch", injected)
    out = tmp_path / "out"
    ablation.main([
        "--dry-run", "--arms", "baseline", "--scenario", "budget-approved",
        "--out", str(out), "--state-dir", str(tmp_path / "state"),
    ])
    report = json.loads((out / "ablation.json").read_text())
    assert report["arms"]["baseline"].get("status") != "INVALID"
    assert report["runs"][0]["status"] != "INVALID"
    assert "upstream_projection_gap" in (out / "ablation.md").read_text()
