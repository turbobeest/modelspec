"""Concrete hardware checks use the keyed, verified-snapshot Worker path."""

import asyncio
import json

import pytest

from tests.test_decide_worker import KEY
from tests.test_hardware_fit import REQUEST, assess, fixture_snapshot, hardware_fit_record, lower_bound_record
from tests.test_x402 import _Req, _entry_env, entry


@pytest.mark.parametrize("enforced", ["false", "true"])
@pytest.mark.parametrize("x402_enabled", ["false", "true"])
@pytest.mark.parametrize("human_enabled", ["false", "true"])
@pytest.mark.parametrize("visit_enabled", ["false", "true"])
def test_hardware_fit_refuses_keyless_requests_even_with_a_valid_visit_token(
    entry, enforced, x402_enabled, human_enabled, visit_enabled
):
    import visit_token

    worker = entry.Default()
    worker.env = _entry_env(
        ACCESS_ENFORCED=enforced,
        X402_ENABLED=x402_enabled,
        HUMAN_GATE_ENABLED=human_enabled,
        VISIT_GATE_ENABLED=visit_enabled,
        VISIT_TOKEN_HMAC_KEY="fixture-model287-visit-secret-0123456789",
    )
    headers = {"Origin": "https://modelspec.dev", "CF-Connecting-IP": "203.0.113.8"}
    credential = visit_token.credential(
        _Req("/v1/hardware-fit", headers=headers), worker.env, entry.CORS_ORIGINS
    )
    headers[visit_token.HEADER] = visit_token.issue(*credential)[0]
    response = asyncio.run(worker.fetch(_Req("/v1/hardware-fit", {}, headers=headers)))

    assert response.status == 401, response.json()
    assert response.json()["error"]["code"] == "missing_api_key"
    assert response.json()["hardware_fit_version"] == "2.0"
    assert "contract_version" not in response.json()
    assert worker.env.ACCESS.store.data == {}


def _keyed_worker(entry, **overrides):
    import access_keys

    worker = entry.Default()
    worker.env = _entry_env(
        ACCESS_ENFORCED="false", X402_ENABLED="false", MODELSPEC_SNAPSHOT_KEY=KEY.decode(),
        **overrides,
    )
    key = "sk_model287_mock"
    record = access_keys.KeyRecord(
        key_id="model287", tier="dpf", owner="test", created_at="2026-10-17"
    )
    asyncio.run(worker.env.ACCESS.put(access_keys.storage_name(key), json.dumps(record.to_json())))
    return worker, {"Authorization": "Bearer " + key}


@pytest.mark.parametrize("bundled", [False, True])
def test_keyed_worker_returns_the_lower_bound_assessment_unchanged(entry, monkeypatch, bundled):
    from decision.snapshot import load_snapshot_bytes

    compiled = fixture_snapshot([lower_bound_record()], memory_gb=32, built=True)
    snapshot_bytes = compiled.to_bytes(key=KEY)
    snapshot = load_snapshot_bytes(snapshot_bytes, key=KEY)
    expected_status, expected_body = assess(snapshot=snapshot)
    assert expected_body["status"] == "estimated"
    assert expected_body["basis"] == "lower_bound"

    async def fetch_snapshot(_etag):
        return entry._Fetched(200, "etag", snapshot_bytes)

    monkeypatch.setattr(entry, "_snapshot_fetcher", lambda _url: fetch_snapshot)
    if bundled:
        monkeypatch.setattr(entry, "_bundled_decision_snapshot", snapshot)
    worker, headers = _keyed_worker(entry)
    response = asyncio.run(worker.fetch(_Req("/v1/hardware-fit", REQUEST, headers=headers)))
    assert response.status == expected_status
    assert response.json() == expected_body


@pytest.mark.parametrize("bundled", [False, True])
@pytest.mark.parametrize("assessment", ["measured", "estimated", "undetermined"])
def test_hardware_fit_answers_from_a_verified_fetched_or_bundled_snapshot(
    entry, monkeypatch, bundled, assessment
):
    fetched = []
    records = [] if assessment == "undetermined" else [hardware_fit_record(assessment)]
    snapshot_bytes = fixture_snapshot(records, built=True).to_bytes(key=KEY)

    async def fetch_snapshot(_etag):
        fetched.append(True)
        return entry._Fetched(200, "etag", snapshot_bytes)

    monkeypatch.setattr(entry, "_snapshot_fetcher", lambda _url: fetch_snapshot)
    if bundled:
        from decision.snapshot import load_snapshot_bytes
        monkeypatch.setattr(entry, "_bundled_decision_snapshot", load_snapshot_bytes(snapshot_bytes, key=KEY))
    worker, headers = _keyed_worker(entry)
    response = asyncio.run(worker.fetch(_Req(
        "/v1/hardware-fit", REQUEST, headers=headers,
    )))

    assert response.status == 200, response.json()
    assert response.json()["status"] == assessment
    assert response.json()["hardware_fit_version"] == "2.0"
    assert response.json()["endpoint"] == "hardware-fit"
    assert response.json()["snapshot"].startswith("snap_")
    assert "contract_version" not in response.json()
    assert "fits" not in response.json()
    if assessment == "measured":
        assert response.json()["measured_fit"] is True
        assert response.json()["measurement"]["record_id"] == "hardware-fit:fixture"
    if assessment == "estimated":
        assert response.json()["estimated_fit"] == "likely"
        assert response.json()["margin_bytes"] == 18_795_200_000
    assert (fetched == []) is bundled


@pytest.mark.parametrize("raw,status,code", [
    ("{", 400, "invalid_request"),
    ("x" * 65_537, 413, "payload_too_large"),
], ids=["invalid-json", "oversized"])
def test_hardware_fit_transport_refusals_keep_its_own_contract(entry, raw, status, code):
    worker = entry.Default()
    worker.env = _entry_env()
    response = asyncio.run(worker.fetch(_Req("/v1/hardware-fit", raw)))

    assert response.status == status, response.json()
    assert response.json()["hardware_fit_version"] == "2.0"
    assert response.json()["endpoint"] == "hardware-fit"
    assert response.json()["error"]["code"] == code
    assert "contract_version" not in response.json()


def test_hardware_fit_missing_snapshot_returns_a_retryable_refusal(entry):
    worker, headers = _keyed_worker(entry)
    worker.env.MODELSPEC_SNAPSHOT_KEY = ""
    response = asyncio.run(worker.fetch(_Req("/v1/hardware-fit", {}, headers=headers)))

    assert response.status == 503, response.json()
    assert response.json()["hardware_fit_version"] == "2.0"
    assert response.json()["error"]["code"] == "no_snapshot"
    assert int(response.headers["retry-after"]) > 0


@pytest.mark.parametrize("enabled", ["false", "true"])
def test_hardware_fit_requires_funding_for_a_keyed_machine_while_human_gate_is_on(entry, enabled):
    from tests.test_x402 import _unfunded_entry_key

    env, key = _unfunded_entry_key(enabled=enabled, history="never-funded")
    env.HUMAN_GATE_ENABLED = "true"
    worker = entry.Default()
    worker.env = env
    response = asyncio.run(worker.fetch(_Req(
        "/v1/hardware-fit", {}, headers={"Authorization": "Bearer " + key},
    )))

    assert response.status == 402, response.json()
    assert response.json()["hardware_fit_version"] == "2.0"
    assert response.json()["error"]["code"] == "payment_required"


def test_unfunded_hardware_fit_answer_validates_against_its_published_contract(entry, monkeypatch):
    import yaml
    from jsonschema import Draft202012Validator
    from decision.hardware_fit import HardwareFitResponse
    from tests.test_x402 import REPO_ROOT, _unfunded_entry_key

    snapshot_bytes = fixture_snapshot(built=True).to_bytes(key=KEY)

    async def fetch_snapshot(_etag):
        return entry._Fetched(200, "etag", snapshot_bytes)

    monkeypatch.setattr(entry, "_snapshot_fetcher", lambda _url: fetch_snapshot)
    env, key = _unfunded_entry_key(enabled="false", history="never-funded")
    env.HUMAN_GATE_ENABLED = "false"
    env.MODELSPEC_SNAPSHOT_KEY = KEY.decode()
    worker = entry.Default()
    worker.env = env
    response = asyncio.run(worker.fetch(_Req(
        "/v1/hardware-fit", REQUEST, headers={"Authorization": "Bearer " + key},
    )))

    assert response.status == 200, response.json()
    body = response.json()
    assert body["status"] == "estimated"
    assert body["credits"] == {
        "exhausted": True, "available": 0, "needed": 2, "buy": "https://modelspec.dev/pricing",
        "unit": "credit",
        "message": "credits are exhausted (0 available, 2 needed for this call). "
                   "Buy a plan or pack at https://modelspec.dev/pricing.",
    }
    HardwareFitResponse.model_validate(body)
    spec = yaml.safe_load((REPO_ROOT / "api/worker/openapi.yaml").read_text(encoding="utf-8"))
    schema = spec["components"]["schemas"]["HardwareFitResponse"]
    validator = Draft202012Validator({**schema, "components": spec["components"]})
    assert validator.is_valid(body), list(validator.iter_errors(body))


@pytest.mark.parametrize("enabled", ["false", "true"])
@pytest.mark.parametrize("assessment,status,remaining", [
    ("measured", 200, 0),
    ("estimated", 200, 0),
    ("undetermined", 200, 0),
    (None, 400, 2),
])
def test_hardware_fit_charges_existing_full_decision_price_and_refunds_refusals(
    entry, enabled, assessment, status, remaining
):
    import x402
    from tests.test_x402 import _unfunded_entry_key

    env, key = _unfunded_entry_key(enabled=enabled, history="never-funded")
    holder = x402.holder_from_key(key)
    asyncio.run(env.CREDITS.credit(holder, "pack-test", 2, "fixture-tx"))
    worker = entry.Default()
    worker.env = env

    async def answer(*_args, **_kwargs):
        body = {"hardware_fit_version": "2.0", "endpoint": "hardware-fit", "snapshot": None}
        if assessment is None:
            body["error"] = {"code": "invalid_request", "message": "Bad type"}
        else:
            body["status"] = assessment
        return status, body

    worker._hardware_fit = answer
    headers = {"Authorization": "Bearer " + key}
    response = asyncio.run(worker.fetch(_Req("/v1/hardware-fit", {}, headers=headers)))

    assert response.status == status, response.json()
    balance = asyncio.run(worker.fetch(_Req("/v1/credits", method="GET", headers=headers)))
    assert balance.status == 200
    assert balance.json()["available"] == remaining
    assert asyncio.run(env.CREDITS.balance(holder)).reserved == 0
