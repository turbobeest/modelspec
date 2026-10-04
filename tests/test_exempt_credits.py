"""MODEL-322: unlimited paid live tiers bypass credits, but retain usage counters."""

import asyncio
from dataclasses import replace
from datetime import UTC, datetime

import pytest

from tests.test_human_gate import _decision_worker, _entry_env, _Req, entry, env  # noqa: F401
from tests.test_policy_check import _model, catalogue, determination, store
from tests.test_x402 import _header, _payload

import access_config
import access_keys
import x402


def _environment(human_gate_enabled="false", x402_enabled="false", **overrides):
    return _entry_env(X402_ENABLED=x402_enabled, **vars(env(
        HUMAN_GATE_ENABLED=human_gate_enabled, TURNSTILE_SECRET=None,
        VISITOR_HMAC_KEY=None, **overrides,
    )))


def _issue_key(environment, tier):
    key = f"live_exempt_credits_{tier}"
    asyncio.run(access_keys.issue(
        environment.ACCESS, tier=tier, owner="fixture", now=datetime.now(UTC),
        policy=access_config.load_policy(environment), secret=key,
    ))
    return key


@pytest.mark.parametrize("path", ["/v1/decide", "/v1/compare"])
@pytest.mark.parametrize("human_gate_enabled", ["false", "true"])
@pytest.mark.parametrize("x402_enabled", ["false", "true"])
@pytest.mark.parametrize("initial_credits,expected_remaining", [(0, 0), (5, 5)])
def test_exempt_decisions_do_not_meter_credits(
    entry, path, human_gate_enabled, x402_enabled, initial_credits, expected_remaining,
):
    environment = _environment(human_gate_enabled, x402_enabled)
    key = _issue_key(environment, "dpf")
    holder = x402.holder_from_key(key)
    if initial_credits:
        asyncio.run(environment.CREDITS.set_monthly(
            holder, initial_credits, "invoice-fixture", "fixture",
        ))
    worker = _decision_worker(entry, environment)

    async def compare(_payload, _origin, _expected):
        return 200, {
            "contract_version": "1.0", "endpoint": "compare", "snapshot": "snapshot-test",
            "results": [{"model_id": "example/ok"}],
        }

    worker._compare = compare
    request = _Req(path, {"spec_version": 1}, headers={
        "origin": "https://modelspec.dev", "authorization": f"Bearer {key}",
    })

    response = asyncio.run(worker.fetch(request))

    assert response.status == 200
    assert "credits" not in response.json()
    assert response.headers["x-modelspec-tier"] == "dpf"
    balance = asyncio.run(environment.CREDITS.balance(holder))
    assert balance.available == expected_remaining
    assert balance.reserved == 0
    assert environment.X402_FACILITATOR.calls == []
    assert environment.HUMAN_GATE.objects == {}
    counters = {
        name.split(":")[2]: value
        for name, value in environment.ACCESS.store.data.items()
        if name.startswith(f"count:{access_keys.key_id(key)}:")
    }
    assert counters == {"daily": "1", "burst": "1"}


@pytest.mark.parametrize("human_gate_enabled", ["false", "true"])
def test_exempt_key_ignores_payment_and_never_reads_or_reserves_credits(
    entry, monkeypatch, human_gate_enabled,
):
    environment = _environment(human_gate_enabled, "true")
    key = _issue_key(environment, "dpf")
    trace = x402.ChargeTrace()
    monkeypatch.setattr(x402, "ChargeTrace", lambda: trace)

    async def never(*args, **kwargs):
        pytest.fail("exempt request touched the credit ledger")

    for method in ("balance", "reserve", "credit"):
        monkeypatch.setattr(environment.CREDITS, method, never)
    request = _Req("/v1/decide", {"spec_version": 1}, headers={
        "authorization": f"Bearer {key}", **_header(_payload(value="5000000")),
    })

    response = asyncio.run(_decision_worker(entry, environment).fetch(request))

    assert response.status == 200
    assert "credits" not in response.json()
    assert environment.X402_FACILITATOR.calls == []
    assert trace.events == ["exempt"]
    assert trace.settlement is None


@pytest.mark.parametrize("human_gate_enabled", ["false", "true"])
def test_exempt_key_does_not_require_x402_configuration(entry, human_gate_enabled):
    environment = _environment(
        human_gate_enabled, "true", X402_PAY_TO=None, CREDITS=None,
    )
    key = _issue_key(environment, "dpf")
    request = _Req("/v1/decide", {"spec_version": 1}, headers={
        "authorization": f"Bearer {key}",
    })

    response = asyncio.run(_decision_worker(entry, environment).fetch(request))

    assert response.status == 200
    assert "credits" not in response.json()
    assert response.headers["x-modelspec-tier"] == "dpf"


@pytest.mark.parametrize("tier", ["paid", "free"])
@pytest.mark.parametrize("human_gate_enabled,x402_enabled,expected_status", [
    ("false", "false", 200),
    ("true", "false", 402),
    ("false", "true", 402),
    ("true", "true", 402),
])
def test_non_exempt_empty_keys_remain_credit_metered(
    entry, tier, human_gate_enabled, x402_enabled, expected_status,
):
    environment = _environment(human_gate_enabled, x402_enabled)
    key = _issue_key(environment, tier)
    worker = _decision_worker(entry, environment)
    if expected_status == 402:
        async def never(*args):
            pytest.fail("unfunded key reached the decision producer")
        worker._decide = never
    request = _Req("/v1/decide", {"spec_version": 1}, headers={
        "authorization": f"Bearer {key}",
    })

    response = asyncio.run(worker.fetch(request))

    assert response.status == expected_status
    if expected_status == 200:
        assert response.json()["credits"]["exhausted"] is True
        assert response.json()["credits"]["available"] == 0
    else:
        assert response.json()["error"]["code"] == "payment_required"
    balance = asyncio.run(environment.CREDITS.balance(x402.holder_from_key(key)))
    assert balance.available == 0
    assert balance.reserved == 0
    assert environment.HUMAN_GATE.objects == {}


@pytest.mark.parametrize("human_gate_enabled", ["false", "true"])
@pytest.mark.parametrize("tier,expected_entitlement,included,verdict", [
    ("paid", "public_export", False, "undetermined"),
    ("dpf", "determinations", True, "pass"),
])
def test_policy_check_preserves_credit_metering_and_exempt_entitlement(
    entry, monkeypatch, human_gate_enabled, tier, expected_entitlement, included, verdict,
):
    environment = _environment(human_gate_enabled)
    key = _issue_key(environment, tier)

    async def load_catalogue(_origin):
        return catalogue([_model("example/ok")])

    async def load_determinations(_env):
        if not included:
            pytest.fail("unfunded non-exempt key read private determinations")
        return store(commercial_use={"example/ok": determination("allowed")})

    monkeypatch.setattr(entry, "_load_policy_catalogue", load_catalogue)
    monkeypatch.setattr(entry, "_load_determinations", load_determinations)
    request = _Req("/v1/policy-check", {
        "policy": {"commercial_use": {"required": True}},
    }, headers={"authorization": f"Bearer {key}"})

    response = asyncio.run(_decision_worker(entry, environment).fetch(request))

    assert response.status == 200
    body = response.json()
    assert body["determinations"]["entitlement"] == expected_entitlement
    assert body["determinations"]["included"] is included
    assert body["result"][0]["verdict"] == verdict
    if included:
        assert "credits" not in body
    else:
        assert body["credits"]["exhausted"] is True
        assert body["credits"]["available"] == 0
    balance = asyncio.run(environment.CREDITS.balance(x402.holder_from_key(key)))
    assert balance.available == 0
    assert balance.reserved == 0


def test_exempt_is_decided_from_loaded_tier_data(entry):
    policy = access_config.load_policy()

    assert {
        name: entry._exempt(tier) for name, tier in policy.tiers.items()
    } == {"dpf": True, "free": False, "sandbox": False, "paid": False}
    assert entry._exempt(None) is False
    assert entry._exempt(replace(policy.tier("dpf"), name="another_paid_tier")) is True
    assert entry._exempt(replace(policy.tier("paid"), name="dpf")) is False
