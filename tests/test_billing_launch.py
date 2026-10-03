"""MODEL-96's browser admission boundary through the real Worker entry."""
import asyncio
import json

import pytest

from tests.replay_billing_launch import replay


def call(path="/v1/decide", *, token=None, origin="https://modelspec.dev"):
    headers = {"origin": origin, "x-modelspec-intent": "AAAAAAAAAAAAAAAAAAAAAA"}
    if token is not None:
        headers["x-modelspec-turnstile"] = token
    return {"path": path, "method": "POST" if path == "/v1/decide" else "GET",
            "headers": headers, "body": json.dumps({
                "spec_version": 1, "where": [],
                "optimize": {"max": "model.context_window"},
            })}


@pytest.mark.parametrize("gate,enforced,status", [
    (False, False, 200), (False, True, 401),
    (True, False, 200), (True, True, 200),
])
def test_keyless_browser_under_each_access_and_human_gate_mode(gate, enforced, status):
    outcome, = asyncio.run(replay({
        "human_gate": gate, "enforced": enforced,
        "calls": [call(token="browser-test-token")],
    }))
    assert outcome["status"] == status
    assert outcome["produced"] == (1 if status == 200 else 0)
    if status == 401:
        error = json.loads(outcome["body"])["error"]
        assert error["code"] == "missing_api_key"
        assert error["how_to_get_a_key"] == "https://modelspec.dev/pricing"


@pytest.mark.parametrize("token", [None, "invalid-token"])
def test_origin_alone_does_not_pass_the_human_gate(token):
    outcome, = asyncio.run(replay({"human_gate": True, "calls": [call(token=token)]}))
    assert outcome["status"] == 403
    assert outcome["produced"] == 0


@pytest.mark.parametrize("gate", [False, True])
def test_launch_flags_preserve_keyless_vocabulary_and_lookup(gate):
    outcomes = asyncio.run(replay({"human_gate": gate, "calls": [
        call("/v1/human-status"), call("/v1/vocabulary"),
        call(token="browser-test-token"), call(token="browser-test-token"),
    ]}))
    assert [outcome["status"] for outcome in outcomes] == [200] * 4
    assert json.loads(outcomes[0]["body"])["enabled"] is gate
    assert outcomes[-1]["produced"] == 2
    if gate:
        # The second presentation request continues the verified intent without
        # replaying its single-use token or spending a second daily admission.
        assert outcomes[-1]["headers"]["x-modelspec-decisions-remaining"] == "19"
