"""Stripe Checkout entitles and claim mints an API key (MODEL-73).

Signed fixture events, never Stripe's API. The Worker runs without the Stripe
SDK; these tests call the same HMAC and handlers the isolate will.
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKER_SRC = REPO_ROOT / "api" / "worker" / "src"
for path in (str(REPO_ROOT), str(WORKER_SRC)):
    if path not in sys.path:
        sys.path.insert(0, path)

import access  # noqa: E402
import access_config  # noqa: E402
import access_keys as keys  # noqa: E402
import billing  # noqa: E402
import billing_stripe  # noqa: E402
from access_kv import MemoryKV, UnboundKV  # noqa: E402

T0 = datetime(2026, 9, 17, 14, 30, 0, tzinfo=UTC)
TS = int(T0.timestamp())
WEBHOOK_SECRET = "whsec_test_fixture_not_a_real_secret"
COMMIT = "testsha"
PRICE = "price_PLACEHOLDER_live_monthly"
SESSION = "cs_test_fixture_session"
SUB = "sub_test_fixture"
CUS = "cus_test_fixture"


def run(coro: Any) -> Any:
    return asyncio.run(coro)


@pytest.fixture
def policy() -> access_config.AccessPolicy:
    return access_config.load_policy()


def payload(type_: str, obj: dict[str, Any], event_id: str) -> str:
    return json.dumps(
        {"id": event_id, "object": "event", "type": type_, "data": {"object": obj}},
        separators=(",", ":"))


def checkout_obj(**extra: Any) -> dict[str, Any]:
    body = {
        "id": SESSION,
        "object": "checkout.session",
        "mode": "subscription",
        "payment_status": "paid",
        "customer": CUS,
        "subscription": SUB,
        "metadata": {"modelspec_price_id": PRICE},
    }
    body.update(extra)
    return body


def invoice_obj(*, paid: bool = True, **extra: Any) -> dict[str, Any]:
    body = {
        "id": "in_test_1",
        "object": "invoice",
        "customer": CUS,
        "subscription": SUB,
        "paid": paid,
        "lines": {"data": [{"price": {"id": PRICE}}]},
    }
    body.update(extra)
    return body


def signed(body: str, *, secret: str = WEBHOOK_SECRET, timestamp: int = TS) -> str:
    return billing_stripe.sign_header(body, secret, timestamp)


async def _live(record: Any) -> tuple[int, dict[str, Any]]:
    return 200, {"schema_version": "1.0", "tier_served": record.tier, "result": [{"ok": True}]}


def _sandbox() -> tuple[int, dict[str, Any]]:
    raise AssertionError("sandbox reached")


def serve(key: str, kv: Any, policy: access_config.AccessPolicy, now: datetime = T0):
    return run(access.serve(api_key=key, kv=kv, policy=policy, live=_live,
                            sandbox=_sandbox, now=now, envelope={"schema_version": "1.0"}))


async def apply(kv: Any, policy: access_config.AccessPolicy, body: str, *,
                header: str | None = None, flag: bool = True,
                secret: str | None = WEBHOOK_SECRET, now: datetime = T0):
    return await billing.webhook(
        payload=body, signature=header if header is not None else signed(body),
        secret=secret, flag=flag, kv=kv, policy=policy, now=now,
        service_commit=COMMIT)


# ── configuration ────────────────────────────────────────────────────────────

def test_the_shipped_price_map_is_placeholder_and_not_compliance(policy):
    row = policy.billing.prices[PRICE]
    assert row.placeholder is True
    assert row.tier == "subscriber"
    assert policy.tier("subscriber").paid is False
    assert policy.tier("subscriber").live_data is True
    assert policy.billing.downgrade_tier == "free"
    assert "terms" in policy.billing.terms_url


def test_changing_a_price_mapping_needs_no_code_change(policy):
    table = json.loads(access_config.DEFAULT_POLICY_PATH.read_text(encoding="utf-8"))
    table["billing"]["prices"][PRICE]["tier"] = "free"
    mapped = access_config.policy_from_json(json.dumps(table))
    kv = MemoryKV()
    body = payload("checkout.session.completed", checkout_obj(), "evt_map")
    outcome = run(apply(kv, mapped, body))
    assert outcome.status == 200
    claimed = run(billing.claim(session_id=SESSION, flag=True, kv=kv, policy=mapped,
                                now=T0, service_commit=COMMIT))
    assert claimed.status == 200
    assert claimed.body["tier"] == "free"
    served = serve(claimed.body["key"], kv, mapped)
    assert served.tier == "free" and served.status == 200


def test_changing_a_subscriber_limit_needs_no_code_change(policy):
    table = json.loads(access_config.DEFAULT_POLICY_PATH.read_text(encoding="utf-8"))
    table["tiers"]["subscriber"]["daily_limit"] = 1
    table["tiers"]["subscriber"]["burst_limit"] = 1
    tight = access_config.policy_from_json(json.dumps(table))
    kv = MemoryKV()
    body = payload("checkout.session.completed", checkout_obj(), "evt_lim")
    assert run(apply(kv, tight, body)).status == 200
    claimed = run(billing.claim(session_id=SESSION, flag=True, kv=kv, policy=tight,
                                now=T0, service_commit=COMMIT))
    key = claimed.body["key"]
    first = serve(key, kv, tight, T0)
    second = serve(key, kv, tight, T0 + timedelta(seconds=61))
    assert first.status == 200
    assert second.status == 429


# ── signatures ───────────────────────────────────────────────────────────────

def test_a_missing_signature_is_rejected(policy):
    kv = MemoryKV()
    body = payload("checkout.session.completed", checkout_obj(), "evt_nosig")
    outcome = run(apply(kv, policy, body, header=""))
    assert outcome.status == 400
    assert outcome.body["error"]["code"] == "invalid_webhook_signature"
    not_ready = run(billing.claim(session_id=SESSION, flag=True, kv=kv,
                                  policy=policy, now=T0, service_commit=COMMIT))
    assert not_ready.status == 409
    assert not_ready.body["error"]["code"] == "claim_not_ready"
    assert "retry in a few seconds" in not_ready.body["error"]["message"]


def test_a_wrong_signature_is_rejected(policy):
    kv = MemoryKV()
    body = payload("checkout.session.completed", checkout_obj(), "evt_badsig")
    outcome = run(apply(kv, policy, body, header=signed(body, secret="whsec_other")))
    assert outcome.status == 400
    assert outcome.body["error"]["code"] == "invalid_webhook_signature"


def test_a_stale_timestamp_is_rejected(policy):
    kv = MemoryKV()
    body = payload("checkout.session.completed", checkout_obj(), "evt_stale")
    old = TS - policy.billing.signature_tolerance_seconds - 1
    outcome = run(apply(kv, policy, body, header=signed(body, timestamp=old)))
    assert outcome.status == 400
    assert "tolerance" in outcome.body["error"]["message"]


# ── end-to-end provision ─────────────────────────────────────────────────────

def test_a_signed_checkout_event_produces_a_working_key_at_the_purchased_tier(policy):
    kv = MemoryKV()
    body = payload("checkout.session.completed", checkout_obj(), "evt_ok")
    outcome = run(apply(kv, policy, body))
    assert outcome.status == 200
    assert outcome.body["action"] == "entitled"
    assert not [n for n in kv.data if n.startswith("key:")]
    claimed = run(billing.claim(session_id=SESSION, flag=True, kv=kv, policy=policy,
                                now=T0, service_commit=COMMIT))
    assert claimed.status == 200
    key = claimed.body["key"]
    assert key.startswith(policy.live_prefix)
    assert claimed.body["tier"] == "subscriber"
    assert claimed.body["shown"] == "once"
    assert key not in json.dumps(kv.data)
    assert not any(key in v for n, v in kv.data.items() if n.startswith("key:"))
    served = serve(key, kv, policy)
    assert served.status == 200
    assert served.tier == "subscriber"


def test_the_key_is_shown_once(policy):
    kv = MemoryKV()
    body = payload("checkout.session.completed", checkout_obj(), "evt_once")
    assert run(apply(kv, policy, body)).status == 200
    first = run(billing.claim(session_id=SESSION, flag=True, kv=kv, policy=policy,
                              now=T0, service_commit=COMMIT))
    second = run(billing.claim(session_id=SESSION, flag=True, kv=kv, policy=policy,
                               now=T0, service_commit=COMMIT))
    assert first.status == 200
    assert second.status == 410
    assert second.body["error"]["code"] == "claim_consumed"
    assert serve(first.body["key"], kv, policy).status == 200
    assert len([n for n in kv.data if n.startswith("key:")]) == 1


def test_replayed_events_are_idempotent(policy):
    kv = MemoryKV()
    body = payload("checkout.session.completed", checkout_obj(), "evt_replay")
    first = run(apply(kv, policy, body))
    second = run(apply(kv, policy, body))
    assert first.body["action"] == "entitled"
    assert second.body["duplicate"] is True
    assert second.body["action"] == "duplicate"
    assert len([n for n in kv.data if n.startswith("key:")]) == 0
    assert len([n for n in kv.data if n.startswith("sub:")]) == 1


def test_checkout_then_invoice_paid_does_not_mint_a_second_key(policy):
    kv = MemoryKV()
    a = payload("checkout.session.completed", checkout_obj(), "evt_a")
    b = payload("invoice.paid", invoice_obj(), "evt_b")
    assert run(apply(kv, policy, a)).body["action"] == "entitled"
    assert run(apply(kv, policy, b)).body["action"] == "already_entitled"
    assert len([n for n in kv.data if n.startswith("key:")]) == 0
    first = run(billing.claim(session_id=SESSION, flag=True, kv=kv, policy=policy,
                              now=T0, service_commit=COMMIT))
    second = run(billing.claim(session_id=SESSION, flag=True, kv=kv, policy=policy,
                               now=T0, service_commit=COMMIT))
    assert first.status == 200
    assert second.status == 410
    assert len([n for n in kv.data if n.startswith("key:")]) == 1


def test_invoice_then_checkout_still_lets_the_session_claim(policy):
    kv = MemoryKV()
    paid = payload("invoice.paid", invoice_obj(), "evt_inv")
    checkout = payload("checkout.session.completed", checkout_obj(), "evt_cs")
    assert run(apply(kv, policy, paid)).body["action"] == "entitled"
    assert run(apply(kv, policy, checkout)).body["action"] == "already_entitled"
    assert not [n for n in kv.data if n.startswith("key:")]
    claimed = run(billing.claim(session_id=SESSION, flag=True, kv=kv, policy=policy,
                                now=T0, service_commit=COMMIT))
    assert claimed.status == 200
    assert len([n for n in kv.data if n.startswith("key:")]) == 1


def test_claim_before_webhook_does_not_mint(policy):
    kv = MemoryKV()
    outcome = run(billing.claim(session_id=SESSION, flag=True, kv=kv, policy=policy,
                                now=T0, service_commit=COMMIT))
    assert outcome.status == 409
    assert outcome.body["error"]["code"] == "claim_not_ready"
    assert outcome.body["error"]["message"] == (
        "payment received, key not ready, retry in a few seconds")
    assert not kv.data


def test_no_access_record_written_by_billing_contains_the_key_plaintext(policy):
    kv = MemoryKV()
    body = payload("checkout.session.completed", checkout_obj(), "evt_plain")
    assert run(apply(kv, policy, body)).status == 200
    assert not [n for n in kv.data if n.startswith("key:")]
    for value in kv.data.values():
        parsed = json.loads(value)
        assert "secret" not in parsed
        assert "key" not in parsed
    claimed = run(billing.claim(session_id=SESSION, flag=True, kv=kv, policy=policy,
                                now=T0, service_commit=COMMIT))
    assert claimed.status == 200
    key = claimed.body["key"]
    assert key.startswith(policy.live_prefix)
    for name, value in kv.data.items():
        assert key not in name
        assert key not in value
        parsed = json.loads(value)
        assert "secret" not in parsed
        assert parsed.get("key") != key
    rotated = run(billing.rotate(api_key=key, flag=True, kv=kv, policy=policy,
                                 now=T0, service_commit=COMMIT))
    new_key = rotated.body["key"]
    for name, value in kv.data.items():
        assert key not in name and new_key not in name
        assert key not in value and new_key not in value
        parsed = json.loads(value)
        assert "secret" not in parsed
        assert parsed.get("key") not in {key, new_key}


# ── cancellation and failed renewal ──────────────────────────────────────────

def _provision(kv: Any, policy: access_config.AccessPolicy) -> str:
    body = payload("checkout.session.completed", checkout_obj(), "evt_have")
    assert run(apply(kv, policy, body)).status == 200
    claimed = run(billing.claim(session_id=SESSION, flag=True, kv=kv, policy=policy,
                                now=T0, service_commit=COMMIT))
    return claimed.body["key"]


def test_payment_failed_downgrades_to_free_immediately(policy):
    kv = MemoryKV()
    key = _provision(kv, policy)
    assert serve(key, kv, policy).tier == "subscriber"
    failed = payload("invoice.payment_failed", invoice_obj(paid=False), "evt_fail")
    outcome = run(apply(kv, policy, failed))
    assert outcome.body["action"] == "downgraded"
    served = serve(key, kv, policy, T0 + timedelta(seconds=61))
    assert served.status == 200
    assert served.tier == "free"


def test_invoice_paid_after_failure_restores_the_purchased_tier(policy):
    kv = MemoryKV()
    key = _provision(kv, policy)
    run(apply(kv, policy, payload("invoice.payment_failed", invoice_obj(paid=False),
                                  "evt_fail2")))
    restored = run(apply(kv, policy, payload("invoice.paid", invoice_obj(), "evt_pay2")))
    assert restored.body["action"] in {"already_entitled", "restored", "unchanged",
                                       "tier_set"}
    # invoice.paid on an existing entitlement restores the mapped tier.
    served = serve(key, kv, policy, T0 + timedelta(seconds=61))
    assert served.tier == "subscriber"


def test_subscription_deleted_downgrades_to_free(policy):
    kv = MemoryKV()
    key = _provision(kv, policy)
    body = payload("customer.subscription.deleted",
                   {"id": SUB, "object": "subscription", "status": "canceled",
                    "customer": CUS}, "evt_del")
    assert run(apply(kv, policy, body)).body["action"] == "downgraded"
    assert serve(key, kv, policy, T0 + timedelta(seconds=61)).tier == "free"


def test_subscription_expiry_downgrades_to_free(policy):
    kv = MemoryKV()
    key = _provision(kv, policy)
    body = payload("customer.subscription.updated",
                   {"id": SUB, "object": "subscription", "status": "unpaid",
                    "customer": CUS, "items": {"data": [{"price": {"id": PRICE}}]}},
                   "evt_exp")
    assert run(apply(kv, policy, body)).body["action"] == "downgraded"
    assert serve(key, kv, policy, T0 + timedelta(seconds=61)).tier == "free"


# ── rotation ─────────────────────────────────────────────────────────────────

def test_rotation_issues_a_new_key_and_refuses_the_old_one(policy):
    kv = MemoryKV()
    key = _provision(kv, policy)
    rotated = run(billing.rotate(api_key=key, flag=True, kv=kv, policy=policy,
                                 now=T0, service_commit=COMMIT))
    assert rotated.status == 200
    new_key = rotated.body["key"]
    assert new_key != key
    assert serve(new_key, kv, policy, T0 + timedelta(seconds=61)).status == 200
    old = serve(key, kv, policy, T0 + timedelta(seconds=122))
    assert old.status == 403
    assert old.body["error"]["code"] == "key_revoked"


# ── the switch ───────────────────────────────────────────────────────────────

def test_billing_ships_off():
    config = (REPO_ROOT / "api" / "worker" / "wrangler.jsonc").read_text(encoding="utf-8")
    live = "\n".join(l for l in config.splitlines() if not l.lstrip().startswith("//"))
    assert '"BILLING_ENABLED": "false"' in live
    assert billing.enabled("false") is False
    assert billing.enabled("true") is True


def test_a_valid_event_is_refused_when_the_flag_is_off(policy):
    kv = MemoryKV()
    body = payload("checkout.session.completed", checkout_obj(), "evt_off")
    outcome = run(apply(kv, policy, body, flag=False))
    assert outcome.status == 503
    assert outcome.body["error"]["code"] == "billing_not_enabled"
    assert not [n for n in kv.data if n.startswith("key:")]


def test_checkout_with_a_stubbed_stripe_returns_a_hosted_url(policy):
    class Stripe:
        async def __call__(self, url, *, method, headers, body):
            assert method == "POST"
            assert "sk_test_fixture" in headers["authorization"]
            assert "payment_method_types" not in body
            from urllib.parse import unquote
            assert "consent_collection" in body
            assert "payment_method_types" not in unquote(body)
            assert policy.billing.terms_url in unquote(body)

            class Resp:
                ok = True
                status = 200

                async def text(self):
                    return json.dumps({"id": "cs_test_created",
                                       "url": "https://checkout.stripe.com/c/pay/cs_test_created"})
            return Resp()

    outcome = run(billing.checkout(
        payload={}, flag=True, secret="sk_test_fixture", origin="https://api.modelspec.test",
        kv=MemoryKV(), policy=policy, service_commit=COMMIT, http=Stripe()))
    assert outcome.status == 200
    assert outcome.body["url"].startswith("https://checkout.stripe.com/")
    assert outcome.body["tier"] == "subscriber"
    assert "not" in outcome.body["what_you_buy"] and "policy-check" in outcome.body["what_you_buy"]
    assert outcome.body["placeholder"] is True


def test_unbound_store_cannot_provision(policy):
    body = payload("checkout.session.completed", checkout_obj(), "evt_unbound")
    outcome = run(apply(kv=UnboundKV("ACCESS"), policy=policy, body=body))
    assert outcome.status == 503
    assert outcome.body["error"]["code"] == "access_store_not_configured"


# ── through entry.py ─────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def entry():
    import importlib.util
    import types
    saved = {name: sys.modules.get(name) for name in ("js", "workers")}
    js = types.ModuleType("js")

    async def _no_fetch(url, options=None):
        raise AssertionError(f"unexpected fetch of {url}")

    js.fetch = _no_fetch
    workers = types.ModuleType("workers")

    class _Response:
        def __init__(self, body, status=200, headers=None):
            self.body, self.status, self.headers = body, status, headers or {}

        def json(self):
            return json.loads(self.body)

    workers.Response = _Response
    workers.WorkerEntrypoint = type("WorkerEntrypoint", (), {})
    sys.modules["js"], sys.modules["workers"] = js, workers
    spec = importlib.util.spec_from_file_location(
        "modelspec_worker_entry_billing", WORKER_SRC / "entry.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        yield module
    finally:
        for name, value in saved.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


class _Bind:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.missing = None

    async def get(self, name):
        return self.values.get(name, self.missing)

    async def put(self, name, value, options=None):
        self.values[name] = value

    async def delete(self, name):
        self.values.pop(name, None)


class _Req:
    def __init__(self, path: str, *, method: str = "POST", body: str = "",
                 headers: dict[str, str] | None = None) -> None:
        import types
        self.url = f"https://api.modelspec.test{path}"
        self.method = method
        self._body = body
        self._headers = {k.lower(): v for k, v in (headers or {}).items()}
        self.headers = types.SimpleNamespace(get=lambda name: self._headers.get(name.lower()))

    async def text(self):
        return self._body


def _billing_env(access=None, *, flag: str = "true", secret: str = WEBHOOK_SECRET):
    import types
    env = types.SimpleNamespace(
        BUILD_COMMIT=COMMIT, EXPORT_ORIGIN="https://modelspec.test",
        ACCESS_ENFORCED="false", BILLING_ENABLED=flag,
        STRIPE_WEBHOOK_SECRET=secret,
        TIER_POLICY=(REPO_ROOT / "api" / "worker" / "tiers.json").read_text(encoding="utf-8"))
    if access is not None:
        env.ACCESS = access
    return env


def test_entry_webhook_provisions_and_claim_returns_the_key(entry):
    binding = _Bind()
    body = payload("checkout.session.completed", checkout_obj(), "evt_entry")
    worker = entry.Default()
    worker.env = _billing_env(binding)
    header = signed(body, timestamp=int(datetime.now(UTC).timestamp()))
    response = run(worker.fetch(_Req(
        "/v1/billing/stripe-webhook", body=body,
        headers={"stripe-signature": header})))
    assert response.status == 200
    assert response.json()["action"] == "entitled"
    claimed = run(worker.fetch(_Req(
        f"/v1/billing/claim?session_id={SESSION}", method="GET", body="")))
    assert claimed.status == 200
    assert claimed.json()["key"].startswith("live_")
    assert claimed.json()["tier"] == "subscriber"


def test_entry_rejects_a_bad_signature_before_the_flag_matters(entry):
    worker = entry.Default()
    worker.env = _billing_env(_Bind(), flag="false")
    body = payload("checkout.session.completed", checkout_obj(), "evt_entry_bad")
    response = run(worker.fetch(_Req(
        "/v1/billing/stripe-webhook", body=body,
        headers={"stripe-signature": signed(
            body, secret="whsec_nope", timestamp=int(datetime.now(UTC).timestamp()))})))
    assert response.status == 400
    assert response.json()["error"]["code"] == "invalid_webhook_signature"


def test_docs_name_the_human_steps():
    text = (REPO_ROOT / "docs" / "billing.md").read_text(encoding="utf-8")
    for needle in ("Turning it on", "STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET",
                   "BILLING_ENABLED", "test mode", "terms-of-service",
                   "policy-check determinations", "immediate"):
        assert needle in text, needle
