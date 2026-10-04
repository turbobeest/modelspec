"""MODEL-96's production access boundary through the real Worker entry."""
import asyncio
import json

import pytest

from tests.replay_billing_launch import NOW, replay


def call(path="/v1/decide", *, visit=None, turnstile=None, now=NOW, body=None, method=None):
    headers = {"origin": "https://modelspec.dev", "x-modelspec-intent": "AAAAAAAAAAAAAAAAAAAAAA"}
    if visit is not None:
        headers["x-modelspec-visit-token"] = visit
    if turnstile is not None:
        headers["x-modelspec-turnstile"] = turnstile
    return {"path": path, "method": method or ("GET" if path in (
        "/v1/vocabulary", "/v1/health", "/v1/human-status") else "POST"),
        "headers": headers, "now": now,
        "body": json.dumps(body if body is not None else {
            "spec_version": 1, "where": [], "optimize": {"max": "model.context_window"},
        })}


def run(calls, **flags):
    return asyncio.run(replay({"calls": calls, **flags}))


def exchange():
    request = call("/v1/visit-token", turnstile="browser-test-token-1")
    response, = run([request])
    assert response["status"] == 200
    assert response["visit_objects"] == 0
    return request, json.loads(response["body"])["token"]


@pytest.mark.parametrize("gate", [False, True])
@pytest.mark.parametrize("path", ["/v1/decide", "/v1/compare", "/v1/rank", "/v1/policy-check", "/v1/vocabulary"])
def test_live_keyless_machine_requests_name_where_to_get_a_key(path, gate):
    response, = run([call(path)], visit_gate=gate, human_gate=False)
    assert response["status"] == 401
    error = json.loads(response["body"])["error"]
    assert error["code"] == "missing_api_key"
    assert error["how_to_get_a_key"] == "https://modelspec.dev/pricing"
    assert error["docs"] == "https://modelspec.dev/docs/api"
    assert "Get one at https://modelspec.dev/pricing" in error["message"]
    assert response["produced"] == 0
    assert response["visit_objects"] == 0


def test_live_health_status_and_disabled_feedback_stay_keyless():
    health, status, submitted, withdrawn = run([
        call("/v1/health"),
        call("/v1/human-status"),
        call("/v1/feedback", body={"rating": "reliable", "client": "agent"}),
        call("/v1/feedback", method="DELETE", body={"receipt": "fbr_20261004_" + "a" * 32}),
    ])
    assert health["status"] == 200
    assert json.loads(health["body"])["endpoint"] == "health"
    assert status["status"] == 200
    assert json.loads(status["body"]) == {
        "enabled": True, "mode": "visit", "day_limit": 300, "burst_limit": 30,
    }
    assert submitted["status"] == 200
    assert json.loads(submitted["body"])["status"] == "not_recorded"
    assert withdrawn["status"] == 404
    assert json.loads(withdrawn["body"])["error"]["code"] == "receipt_not_found"
    assert submitted["visit_objects"] == withdrawn["visit_objects"] == 0


def test_live_visit_exchange_without_turnstile_is_a_human_challenge_not_a_key_refusal():
    response, = run([call("/v1/visit-token")])
    assert response["status"] == 403
    assert json.loads(response["body"])["error"]["code"] == "human_challenge_required"
    assert response["visit_objects"] == 0


def test_verified_visit_admits_and_renews_keyless_vocabulary_and_decide():
    request, token = exchange()
    vocabulary = call("/v1/vocabulary", visit=token, now=NOW + 1)
    _, response = run([request, vocabulary])
    renewed = response["headers"]["x-modelspec-visit-token"]
    assert renewed != token
    decide = call(visit=renewed, now=NOW + 2)
    outcomes = run([request, vocabulary, decide])
    assert [outcome["status"] for outcome in outcomes] == [200, 200, 200]
    assert outcomes[1]["headers"]["x-modelspec-decisions-remaining"] == "59"
    assert outcomes[2]["headers"]["x-modelspec-decisions-remaining"] == "299"
    assert outcomes[2]["headers"]["x-modelspec-visit-token"] != renewed
    assert outcomes[2]["produced"] == 1
    assert outcomes[2]["visit_objects"] == 1
    assert all(outcome["headers"]["cache-control"] == "no-store" for outcome in outcomes[:2])


@pytest.mark.parametrize("path", ["/v1/decide", "/v1/vocabulary"])
@pytest.mark.parametrize("kind,code", [("invalid", "visit_token_invalid"), ("expired", "visit_token_expired")])
def test_invalid_or_expired_visit_is_refused_without_anonymous_fallback(path, kind, code):
    request, token = exchange()
    refused = call(path, visit=token if kind == "expired" else token + "x", now=NOW + 1800)
    _, response = run([request, refused])
    assert response["status"] == 401
    assert json.loads(response["body"])["error"]["code"] == code
    assert response["produced"] == 0
    assert response["visit_objects"] == 0


@pytest.mark.parametrize("path", ["/v1/rank", "/v1/compare", "/v1/policy-check"])
def test_verified_visit_does_not_admit_other_machine_endpoints(path):
    request, token = exchange()
    _, response = run([request, call(path, visit=token, now=NOW + 1)])
    assert response["status"] == 401
    assert json.loads(response["body"])["error"]["code"] == "missing_api_key"
    assert response["visit_objects"] == 0


def test_turnstile_exchange_is_single_use_and_needs_the_visit_gate():
    request = call("/v1/visit-token", turnstile="browser-test-token-1")
    assert [row["status"] for row in run([request, request])] == [200, 403]
    assert run([request], visit_gate=False, human_gate=False)[0]["status"] == 404
