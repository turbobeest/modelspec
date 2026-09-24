"""Stripe Checkout funds credits (MODEL-73, MODEL-93).

Signed fixture events, never Stripe's API. The Worker runs without the Stripe
SDK; these tests call the same HMAC and handlers the isolate will. A Checkout
that presents a live key credits that key; an anonymous Checkout mints at claim.
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
import urllib.parse
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
import credits  # noqa: E402
from access_kv import CloudflareKV, MemoryKV, UnboundKV  # noqa: E402

T0 = datetime(2026, 9, 17, 14, 30, 0, tzinfo=UTC)
TS = int(T0.timestamp())
WEBHOOK_SECRET = "whsec_test_fixture_not_a_real_secret"
COMMIT = "testsha"
PRICE = "price_1UHRwmBPydVRHUBjqhKcx8xV"
TEAM_PRICE = "price_1UHRwmBPydVRHUBjBYfcWhkW"
PACK5 = "price_1UHRwmBPydVRHUBjMFS5bDPD"
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
                header: str | None = None,
                secret: str | None = WEBHOOK_SECRET, now: datetime = T0,
                ledger: Any = None):
    return await billing.webhook(
        payload=body, signature=header if header is not None else signed(body),
        secret=secret, kv=kv, policy=policy, now=now,
        service_commit=COMMIT, ledger=ledger)


# ── configuration ────────────────────────────────────────────────────────────

def test_the_shipped_price_map_is_real_test_mode_credits_not_limits(policy):
    row = policy.billing.prices[PRICE]
    assert row.placeholder is False
    assert not any(p.startswith("price_PLACEHOLDER") for p in policy.billing.prices)
    assert row.kind == "plan"
    assert row.name == "Solo"
    assert row.credits == 4000
    assert row.usd == 10
    assert row.tier == "paid"
    team = policy.billing.prices[TEAM_PRICE]
    assert team.kind == "plan" and team.credits == 30000 and team.usd == 50
    pack = policy.billing.prices[PACK5]
    assert pack.kind == "pack" and pack.credits == 1250 and pack.usd == 5
    assert policy.tier("paid").paid is True
    assert policy.tier("paid").daily_limit is None
    assert policy.credits.weights["rank"] == 1
    assert policy.credits.weights["policy-check"] == 5
    assert policy.credits.pack_expiry_days == 365
    assert policy.billing.downgrade_tier == "free"
    assert "terms" in policy.billing.terms_url
    assert "subscriber" not in policy.tiers


def test_changing_a_price_mapping_needs_no_code_change(policy):
    table = json.loads(access_config.DEFAULT_POLICY_PATH.read_text(encoding="utf-8"))
    table["billing"]["prices"][PRICE]["tier"] = "free"
    mapped = access_config.policy_from_json(json.dumps(table))
    kv = MemoryKV()
    body = payload("checkout.session.completed", checkout_obj(), "evt_map")
    outcome = run(apply(kv, mapped, body))
    assert outcome.status == 200
    claimed = run(billing.claim(session_id=SESSION, kv=kv, policy=mapped,
                                now=T0, service_commit=COMMIT))
    assert claimed.status == 200
    assert claimed.body["tier"] == "free"
    served = serve(claimed.body["key"], kv, mapped)
    assert served.tier == "free" and served.status == 200


def test_changing_a_price_credit_amount_needs_no_code_change(policy):
    """MODEL-93: a credit figure is configuration. Replaces the MODEL-73
    subscriber daily-limit test, whose semantics this ticket removed."""
    table = json.loads(access_config.DEFAULT_POLICY_PATH.read_text(encoding="utf-8"))
    table["billing"]["prices"][PRICE]["credits"] = 7
    mapped = access_config.policy_from_json(json.dumps(table))
    kv = MemoryKV()
    ledger = credits.MemoryLedger()
    body = payload("checkout.session.completed", checkout_obj(), "evt_amt")
    assert run(apply(kv, mapped, body, ledger=ledger)).status == 200
    claimed = run(billing.claim(session_id=SESSION, kv=kv, policy=mapped,
                                now=T0, service_commit=COMMIT, ledger=ledger))
    assert claimed.status == 200
    holder = credits.holder_from_fingerprint(keys.fingerprint(claimed.body["key"]))
    assert run(ledger.balance(holder)).monthly == 7
    assert run(ledger.balance(holder)).available == 7


# ── signatures ───────────────────────────────────────────────────────────────

def test_a_missing_signature_is_rejected(policy):
    kv = MemoryKV()
    body = payload("checkout.session.completed", checkout_obj(), "evt_nosig")
    outcome = run(apply(kv, policy, body, header=""))
    assert outcome.status == 400
    assert outcome.body["error"]["code"] == "invalid_webhook_signature"
    not_ready = run(billing.claim(session_id=SESSION, kv=kv,
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
    claimed = run(billing.claim(session_id=SESSION, kv=kv, policy=policy,
                                now=T0, service_commit=COMMIT))
    assert claimed.status == 200
    key = claimed.body["key"]
    assert key.startswith(policy.live_prefix)
    assert claimed.body["tier"] == "paid"
    assert claimed.body["shown"] == "once"
    assert key not in json.dumps(kv.data)
    assert not any(key in v for n, v in kv.data.items() if n.startswith("key:"))
    served = serve(key, kv, policy)
    assert served.status == 200
    assert served.tier == "paid"


def test_the_key_is_shown_once(policy):
    kv = MemoryKV()
    body = payload("checkout.session.completed", checkout_obj(), "evt_once")
    assert run(apply(kv, policy, body)).status == 200
    first = run(billing.claim(session_id=SESSION, kv=kv, policy=policy,
                              now=T0, service_commit=COMMIT))
    second = run(billing.claim(session_id=SESSION, kv=kv, policy=policy,
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
    first = run(billing.claim(session_id=SESSION, kv=kv, policy=policy,
                              now=T0, service_commit=COMMIT))
    second = run(billing.claim(session_id=SESSION, kv=kv, policy=policy,
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
    claimed = run(billing.claim(session_id=SESSION, kv=kv, policy=policy,
                                now=T0, service_commit=COMMIT))
    assert claimed.status == 200
    assert len([n for n in kv.data if n.startswith("key:")]) == 1


def test_claim_before_webhook_does_not_mint(policy):
    kv = MemoryKV()
    outcome = run(billing.claim(session_id=SESSION, kv=kv, policy=policy,
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
    claimed = run(billing.claim(session_id=SESSION, kv=kv, policy=policy,
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
    rotated = run(billing.rotate(api_key=key, kv=kv, policy=policy,
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
    claimed = run(billing.claim(session_id=SESSION, kv=kv, policy=policy,
                                now=T0, service_commit=COMMIT))
    return claimed.body["key"]


def test_payment_failed_downgrades_to_free_immediately(policy):
    kv = MemoryKV()
    key = _provision(kv, policy)
    assert serve(key, kv, policy).tier == "paid"
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
    assert served.tier == "paid"


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
    rotated = run(billing.rotate(api_key=key, kv=kv, policy=policy,
                                 now=T0, service_commit=COMMIT))
    assert rotated.status == 200
    new_key = rotated.body["key"]
    assert new_key != key
    assert serve(new_key, kv, policy, T0 + timedelta(seconds=61)).status == 200
    old = serve(key, kv, policy, T0 + timedelta(seconds=122))
    assert old.status == 403
    assert old.body["error"]["code"] == "key_revoked"


# ── the switch ───────────────────────────────────────────────────────────────

def test_billing_is_off_while_the_sites_are_in_holding_mode():
    """Checkout is closed (Jamie, 2026-09-24): modelspec.dev is dark until he
    says go, and nobody can buy meanwhile. The Prices stay mapped, so past
    purchases keep resolving and reopening is one flag."""
    config = (REPO_ROOT / "api" / "worker" / "wrangler.jsonc").read_text(encoding="utf-8")
    live = "\n".join(l for l in config.splitlines() if not l.lstrip().startswith("//"))
    assert '"BILLING_ENABLED": "false"' in live
    policy = json.loads((REPO_ROOT / "api" / "worker" / "tiers.json").read_text(encoding="utf-8"))
    assert all(p.startswith("price_1UHRw") for p in policy["billing"]["prices"])
    assert not any(row["placeholder"] for row in policy["billing"]["prices"].values())
    assert billing.enabled("false") is False
    assert billing.enabled("true") is True


def test_the_webhook_applies_a_valid_event_whatever_the_flag(policy):
    """The flag gates Checkout only. An event is money that already moved."""
    import inspect
    for handler in (billing.webhook, billing.claim, billing.rotate):
        assert "flag" not in inspect.signature(handler).parameters, handler.__name__
    for handler in (billing.checkout, billing.checkout_form):
        assert "flag" in inspect.signature(handler).parameters, handler.__name__
    kv = MemoryKV()
    body = payload("checkout.session.completed", checkout_obj(), "evt_off")
    outcome = run(apply(kv, policy, body))
    assert outcome.status == 200
    assert outcome.body["action"] == "entitled"


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
        payload={"price_id": PRICE}, flag=True, secret="sk_test_fixture",
        origin="https://api.modelspec.test",
        kv=MemoryKV(), policy=policy, service_commit=COMMIT, http=Stripe()))
    assert outcome.status == 200
    assert outcome.body["url"].startswith("https://checkout.stripe.com/")
    assert outcome.body["tier"] == "paid"
    assert outcome.body["kind"] == "plan"
    assert outcome.body["credits"] == 4000
    assert "determinations" in outcome.body["what_you_buy"]
    assert "token" not in outcome.body["what_you_buy"].lower()
    assert outcome.body["placeholder"] is False


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


def _billing_env(access=None, *, flag: str = "true", secret: str = WEBHOOK_SECRET,
                 stripe_secret: str = "sk_test_fixture"):
    import types
    env = types.SimpleNamespace(
        BUILD_COMMIT=COMMIT, EXPORT_ORIGIN="https://modelspec.test",
        ACCESS_ENFORCED="false", BILLING_ENABLED=flag,
        STRIPE_WEBHOOK_SECRET=secret, STRIPE_SECRET_KEY=stripe_secret,
        TIER_POLICY=(REPO_ROOT / "api" / "worker" / "tiers.json").read_text(encoding="utf-8"),
        CREDITS=credits.MemoryLedger())
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
    assert claimed.json()["tier"] == "paid"


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


def test_with_billing_off_nobody_can_buy_and_past_purchases_are_honoured(entry):
    """Holding mode (2026-09-24), end to end through entry.py with the flag off.

    Checkout refuses before any Stripe call. A pack paid for before the flag
    went off still arrives by webhook and is claimed; its key keeps drawing
    credits on /v1/rank; a dispute holds and restores them, and a refund takes
    them back. Stripe is never reached: `js.fetch` raises in this fixture.
    """
    env = _billing_env(_Bind(), flag="false")
    worker = entry.Default()
    worker.env = env
    stamp = int(datetime.now(UTC).timestamp())

    def hook(type_: str, obj: dict[str, Any], event_id: str):
        body = payload(type_, obj, event_id)
        response = run(worker.fetch(_Req(
            "/v1/billing/stripe-webhook", body=body,
            headers={"stripe-signature": signed(body, timestamp=stamp)})))
        assert response.status == 200, response.json()
        return response.json()

    refused = run(worker.fetch(_Req(
        "/v1/billing/checkout", body=json.dumps({"price_id": PACK5}),
        headers={"content-type": "application/json"})))
    assert refused.status == 503
    assert refused.json()["error"]["code"] == "billing_not_enabled"

    pi, amount = "pi_holding_fixture", 535
    hook("checkout.session.completed", {
        "id": "cs_holding_fixture", "object": "checkout.session", "mode": "payment",
        "payment_status": "paid", "customer": None, "payment_intent": pi,
        "amount_total": amount, "metadata": {"modelspec_price_id": PACK5},
    }, "evt_holding_buy")
    claimed = run(worker.fetch(_Req(
        "/v1/billing/claim?session_id=cs_holding_fixture", method="GET", body="")))
    assert claimed.status == 200, claimed.json()
    key = claimed.json()["key"]
    holder = x402_holder(key)

    async def ranked(payload, service_commit, origin):
        return 200, {"schema_version": "1.0", "service_commit": service_commit,
                     "result": [{"model_id": "example/ok"}]}

    worker._rank = ranked
    answer = run(worker.fetch(_Req(
        "/v1/rank", body=json.dumps({"use_case": "coding"}),
        headers={"authorization": f"Bearer {key}"})))
    assert answer.status == 200, answer.json()
    assert "exhausted" not in json.dumps(answer.json())
    assert run(env.CREDITS.balance(holder)).available == 1249

    dispute = {"id": "dp_holding", "object": "dispute", "amount": amount,
               "currency": "usd", "charge": "ch_holding", "payment_intent": pi,
               "status": "needs_response", "metadata": {}}
    hook("charge.dispute.created", dispute, "evt_holding_dispute")
    assert run(env.CREDITS.balance(holder)).available == 0
    hook("charge.dispute.closed", {**dispute, "status": "won"}, "evt_holding_won")
    assert run(env.CREDITS.balance(holder)).available == 1249

    refund = hook("charge.refunded", {
        "id": "ch_holding", "object": "charge", "amount": amount,
        "amount_captured": amount, "amount_refunded": amount, "refunded": True,
        "currency": "usd", "customer": None, "payment_intent": pi,
        "status": "succeeded", "metadata": {},
    }, "evt_holding_refund")
    assert refund["credits"]["removed"] == 1249
    assert run(env.CREDITS.balance(holder)).available == 0


def x402_holder(key: str) -> str:
    return credits.holder_from_fingerprint(keys.fingerprint(key))


def test_docs_name_the_human_steps():
    text = (REPO_ROOT / "docs" / "billing.md").read_text(encoding="utf-8")
    for needle in ("Turning it on", "STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET",
                   "BILLING_ENABLED", "test mode", "terms-of-service",
                   "determinations", "immediate", "credits"):
        assert needle in text, needle
    assert "credit" in text.lower()


def _holder(key: str) -> str:
    return credits.holder_from_fingerprint(keys.fingerprint(key))


def _claim(kv, policy, ledger, session_id: str = SESSION):
    return run(billing.claim(session_id=session_id, kv=kv, policy=policy,
                             now=T0, service_commit=COMMIT, ledger=ledger))


def test_solo_grant_is_4000_and_team_is_30000(policy):
    kv = MemoryKV()
    ledger = credits.MemoryLedger()
    run(apply(kv, policy, payload("checkout.session.completed", checkout_obj(), "evt_solo"),
              ledger=ledger))
    key = _claim(kv, policy, ledger).body["key"]
    assert run(ledger.balance(_holder(key))).monthly == 4000
    assert run(ledger.balance(_holder(key))).available == 4000

    kv2 = MemoryKV()
    ledger2 = credits.MemoryLedger()
    team_session = "cs_test_team"
    obj = checkout_obj(id=team_session, subscription="sub_team",
                       metadata={"modelspec_price_id": TEAM_PRICE})
    run(apply(kv2, policy, payload("checkout.session.completed", obj, "evt_team"),
              ledger=ledger2))
    key2 = _claim(kv2, policy, ledger2, team_session).body["key"]
    assert run(ledger2.balance(_holder(key2))).monthly == 30000


def test_renewal_resets_monthly_and_does_not_accumulate(policy):
    kv = MemoryKV()
    ledger = credits.MemoryLedger()
    run(apply(kv, policy, payload("checkout.session.completed", checkout_obj(), "evt_r1"),
              ledger=ledger))
    key = _claim(kv, policy, ledger).body["key"]
    holder = _holder(key)
    reserved = run(ledger.reserve(holder, 100))
    assert reserved.ok
    run(ledger.commit(holder, reserved.reservation_id))
    assert run(ledger.balance(holder)).monthly == 3900
    run(apply(kv, policy, payload("invoice.paid", invoice_obj(), "evt_r2"), ledger=ledger))
    assert run(ledger.balance(holder)).monthly == 4000
    assert run(ledger.balance(holder)).available == 4000



def dahlia_invoice_obj(**extra: Any) -> dict[str, Any]:
    """An invoice as API version 2026-08-26.dahlia sends it (the shape since
    2025-03-31.basil): no top-level `subscription`, and each line names its
    Price under `pricing.price_details`, not `price`."""
    body = {
        "id": "in_test_dahlia",
        "object": "invoice",
        "customer": CUS,
        "status": "paid",
        "parent": {
            "type": "subscription_details",
            "subscription_details": {
                "subscription": SUB,
                "metadata": {"modelspec_price_id": PRICE},
            },
        },
        "lines": {"data": [{
            "object": "line_item",
            "pricing": {"type": "price_details",
                        "price_details": {"price": PRICE, "product": "prod_test"}},
        }]},
    }
    body.update(extra)
    return body


def test_renewal_in_the_dahlia_invoice_shape_resets_monthly(policy):
    kv = MemoryKV()
    ledger = credits.MemoryLedger()
    run(apply(kv, policy, payload("checkout.session.completed", checkout_obj(), "evt_d1"),
              ledger=ledger))
    key = _claim(kv, policy, ledger).body["key"]
    holder = _holder(key)
    reserved = run(ledger.reserve(holder, 100))
    run(ledger.commit(holder, reserved.reservation_id))
    outcome = run(apply(kv, policy, payload("invoice.paid", dahlia_invoice_obj(), "evt_d2"),
                        ledger=ledger))
    assert outcome.status == 200, outcome.body
    assert run(ledger.balance(holder)).monthly == 4000


def test_price_from_a_dahlia_invoice_without_line_prices_uses_subscription_metadata():
    obj = dahlia_invoice_obj(lines={"data": []})
    assert billing._price_from_invoice(obj) == PRICE

def test_pack_adds_credits_with_12_month_expiry(policy):
    kv = MemoryKV()
    ledger = credits.MemoryLedger()
    session = "cs_test_pack"
    obj = {
        "id": session, "object": "checkout.session", "mode": "payment",
        "payment_status": "paid", "customer": CUS,
        "metadata": {"modelspec_price_id": PACK5},
    }
    outcome = run(apply(kv, policy, payload("checkout.session.completed", obj, "evt_pack"),
                        ledger=ledger))
    assert outcome.status == 200
    claimed = _claim(kv, policy, ledger, session)
    assert claimed.status == 200
    holder = _holder(claimed.body["key"])
    bal = run(ledger.balance(holder, now="2026-09-17T14:30:00Z"))
    assert bal.monthly == 0
    assert bal.packs == 1250
    assert bal.available == 1250
    assert bal.grants[0].expires_at.startswith("2027-09-17")
    later = run(ledger.balance(holder, now="2027-09-18T00:00:00Z"))
    assert later.available == 0
    assert later.packs == 0


def test_monthly_is_spent_before_packs(policy):
    ledger = credits.MemoryLedger()
    holder = "key:" + "ab" * 32
    run(ledger.set_monthly(holder, 10, "in_m", "Solo"))
    run(ledger.credit(holder, "pack_old", 10, "tx",
                      expires_at="2027-01-01T00:00:00Z", source="pack"))
    reserved = run(ledger.reserve(holder, 6, now="2026-09-17T00:00:00Z"))
    assert reserved.ok
    run(ledger.commit(holder, reserved.reservation_id))
    bal = run(ledger.balance(holder, now="2026-09-17T00:00:00Z"))
    assert bal.monthly == 4
    assert bal.packs == 10


def test_oldest_pack_is_spent_first():
    ledger = credits.MemoryLedger()
    holder = "key:" + "cd" * 32
    run(ledger.credit(holder, "newer", 5, "tx1",
                      expires_at="2027-06-01T00:00:00Z", source="pack"))
    run(ledger.credit(holder, "older", 5, "tx2",
                      expires_at="2027-01-01T00:00:00Z", source="pack"))
    reserved = run(ledger.reserve(holder, 3, now="2026-09-17T00:00:00Z"))
    assert reserved.ok
    run(ledger.commit(holder, reserved.reservation_id))
    bal = run(ledger.balance(holder, now="2026-09-17T00:00:00Z"))
    by_id = {g.grant_id: g.remaining for g in bal.grants}
    assert by_id["older"] == 2
    assert by_id["newer"] == 5


def test_cancellation_zeros_monthly_and_leaves_packs(policy):
    kv = MemoryKV()
    ledger = credits.MemoryLedger()
    run(apply(kv, policy, payload("checkout.session.completed", checkout_obj(), "evt_c1"),
              ledger=ledger))
    key = _claim(kv, policy, ledger).body["key"]
    holder = _holder(key)
    run(ledger.credit(holder, "keep", 80, "tx",
                      expires_at="2027-09-17T00:00:00Z", source="pack"))
    run(apply(kv, policy, payload("invoice.payment_failed", invoice_obj(paid=False),
                                  "evt_c2"), ledger=ledger))
    bal = run(ledger.balance(holder))
    assert bal.monthly == 0
    assert bal.packs == 80
    assert serve(key, kv, policy, T0 + timedelta(seconds=61)).tier == "free"


def test_pack_checkout_uses_payment_mode(policy):
    seen = {}

    class Stripe:
        async def __call__(self, url, *, method, headers, body):
            from urllib.parse import parse_qs
            seen.update({k: v[0] for k, v in parse_qs(body).items()})

            class Resp:
                ok = True
                status = 200

                async def text(self):
                    return json.dumps({"id": "cs_pack",
                                       "url": "https://checkout.stripe.com/c/pay/cs_pack"})
            return Resp()

    outcome = run(billing.checkout(
        payload={"price_id": PACK5}, flag=True, secret="sk_test_fixture",
        origin="https://api.modelspec.test", kv=MemoryKV(), policy=policy,
        service_commit=COMMIT, http=Stripe()))
    assert outcome.status == 200
    assert seen["mode"] == "payment"
    assert outcome.body["kind"] == "pack"
    assert outcome.body["credits"] == 1250


def test_x402_top_up_and_card_pack_land_in_the_same_balance():
    ledger = credits.MemoryLedger()
    holder = "key:" + "ef" * 32
    run(ledger.credit(holder, "card", 1250, "cs_1",
                      expires_at="2027-09-17T00:00:00Z", source="pack"))
    run(ledger.credit(holder, "chain", 3, "0xabc",
                      expires_at="2027-09-17T00:00:00Z", source="x402"))
    bal = run(ledger.balance(holder, now="2026-09-17T00:00:00Z"))
    assert bal.packs == 1253
    assert {g.source for g in bal.grants} == {"pack", "x402"}
    assert bal.monthly == 0


def _issue(kv, policy, *, tier: str = "paid") -> str:
    secret, _ = run(keys.issue(kv, tier=tier, owner="tester", now=T0, policy=policy))
    return secret


def _key_records(kv) -> list[str]:
    return [n for n in kv.data if n.startswith("key:")]


class _StripeCapture:
    def __init__(self, session_id: str = "cs_bound") -> None:
        self.session_id = session_id
        self.body = ""

    async def __call__(self, url, *, method, headers, body):
        self.body = body

        class Resp:
            ok = True
            status = 200

            async def text(inner_self):
                return json.dumps({
                    "id": self.session_id,
                    "url": f"https://checkout.stripe.com/c/pay/{self.session_id}",
                })

        return Resp()


def test_omitted_checkout_price_id_is_400_naming_valid_ids(policy):
    stripe = _StripeCapture()
    outcome = run(billing.checkout(
        payload={}, flag=True, secret="sk_test_fixture",
        origin="https://api.modelspec.test", kv=MemoryKV(), policy=policy,
        service_commit=COMMIT, http=stripe))
    assert outcome.status == 400
    assert outcome.body["error"]["code"] == "invalid_request"
    ids = outcome.body["error"]["valid_price_ids"]
    assert PRICE in ids and PACK5 in ids and TEAM_PRICE in ids
    assert ids == sorted(ids)
    for price_id in ids:
        assert price_id in outcome.body["error"]["message"]
    assert "never guessed" in outcome.body["error"]["message"]
    assert stripe.body == ""


def test_unknown_key_on_checkout_is_401_not_anonymous(policy):
    stripe = _StripeCapture()
    outcome = run(billing.checkout(
        payload={"price_id": PACK5}, flag=True, secret="sk_test_fixture",
        origin="https://api.modelspec.test", kv=MemoryKV(), policy=policy,
        service_commit=COMMIT, http=stripe, api_key="live_unknown_not_issued"))
    assert outcome.status == 401
    assert outcome.body["error"]["code"] == "invalid_api_key"
    assert stripe.body == ""


def test_revoked_key_on_checkout_is_401_not_anonymous(policy):
    kv = MemoryKV()
    key = _issue(kv, policy)
    assert run(keys.revoke(kv, key)) is True
    stripe = _StripeCapture()
    outcome = run(billing.checkout(
        payload={"price_id": PACK5}, flag=True, secret="sk_test_fixture",
        origin="https://api.modelspec.test", kv=kv, policy=policy,
        service_commit=COMMIT, http=stripe, api_key=key))
    assert outcome.status == 401
    assert outcome.body["error"]["code"] == "key_revoked"
    assert stripe.body == ""


def test_authenticated_pack_adds_to_existing_balance_and_does_not_mint(policy):
    kv = MemoryKV()
    ledger = credits.MemoryLedger()
    key = _issue(kv, policy)
    holder = _holder(key)
    run(ledger.set_monthly(holder, 4000, "in_existing", "Solo"))
    assert len(_key_records(kv)) == 1

    stripe = _StripeCapture("cs_auth_pack")
    started = run(billing.checkout(
        payload={"price_id": PACK5}, flag=True, secret="sk_test_fixture",
        origin="https://api.modelspec.test", kv=kv, policy=policy,
        service_commit=COMMIT, http=stripe, api_key=key))
    assert started.status == 200
    assert started.body["applied_to"] == "existing_key"
    assert started.body["key_id"] == keys.key_id(key)
    from urllib.parse import parse_qs, unquote
    fields = {k: v[0] for k, v in parse_qs(stripe.body).items()}
    fingerprint = keys.fingerprint(key)
    assert fields["metadata[modelspec_key_fingerprint]"] == fingerprint
    assert key not in stripe.body
    assert key not in unquote(stripe.body)

    session = "cs_auth_pack"
    obj = {
        "id": session, "object": "checkout.session", "mode": "payment",
        "payment_status": "paid", "customer": CUS,
        "metadata": {"modelspec_price_id": PACK5,
                     "modelspec_key_fingerprint": fingerprint},
    }
    first = run(apply(kv, policy, payload("checkout.session.completed", obj, "evt_auth_pack"),
                      ledger=ledger))
    assert first.status == 200
    assert first.body["action"] == "credited"
    replay = run(apply(kv, policy, payload("checkout.session.completed", obj, "evt_auth_pack"),
                       ledger=ledger))
    assert replay.body["duplicate"] is True
    assert replay.body["action"] == "duplicate"

    bal = run(ledger.balance(holder, now="2026-09-17T14:30:00Z"))
    assert bal.monthly == 4000
    assert bal.packs == 1250
    assert bal.available == 5250
    assert len(_key_records(kv)) == 1
    for name, value in kv.data.items():
        assert key not in name and key not in value

    claimed = _claim(kv, policy, ledger, session)
    assert claimed.status == 200
    assert "key" not in claimed.body
    assert claimed.body["applied_to"] == "existing_key"
    assert claimed.body["message"] == billing.CREDITS_ADDED
    assert claimed.body["key_id"] == keys.key_id(key)
    assert len(_key_records(kv)) == 1
    again = _claim(kv, policy, ledger, session)
    assert again.status == 410
    assert serve(key, kv, policy).status == 200
    bal2 = run(ledger.balance(holder, now="2026-09-17T14:30:00Z"))
    assert bal2.packs == 1250


def test_anonymous_pack_mints_one_key(policy):
    kv = MemoryKV()
    ledger = credits.MemoryLedger()
    session = "cs_anon_pack"
    obj = {
        "id": session, "object": "checkout.session", "mode": "payment",
        "payment_status": "paid", "customer": CUS,
        "metadata": {"modelspec_price_id": PACK5},
    }
    assert run(apply(kv, policy, payload("checkout.session.completed", obj, "evt_anon_pack"),
                     ledger=ledger)).status == 200
    assert _key_records(kv) == []
    claimed = _claim(kv, policy, ledger, session)
    assert claimed.status == 200
    assert claimed.body["applied_to"] == "new_key"
    assert claimed.body["key"].startswith(policy.live_prefix)
    assert len(_key_records(kv)) == 1
    holder = _holder(claimed.body["key"])
    assert run(ledger.balance(holder, now="2026-09-17T14:30:00Z")).packs == 1250


def test_authenticated_plan_attaches_to_existing_key(policy):
    kv = MemoryKV()
    ledger = credits.MemoryLedger()
    key = _issue(kv, policy, tier="free")
    fingerprint = keys.fingerprint(key)
    assert serve(key, kv, policy).tier == "free"

    stripe = _StripeCapture("cs_auth_plan")
    started = run(billing.checkout(
        payload={"price_id": PRICE}, flag=True, secret="sk_test_fixture",
        origin="https://api.modelspec.test", kv=kv, policy=policy,
        service_commit=COMMIT, http=stripe, api_key=key))
    assert started.status == 200
    assert started.body["applied_to"] == "existing_key"
    from urllib.parse import parse_qs
    fields = {k: v[0] for k, v in parse_qs(stripe.body).items()}
    assert fields["metadata[modelspec_key_fingerprint]"] == fingerprint
    assert fields["subscription_data[metadata][modelspec_key_fingerprint]"] == fingerprint
    assert key not in stripe.body

    session = "cs_auth_plan"
    sub = "sub_auth_plan"
    obj = checkout_obj(id=session, subscription=sub,
                       metadata={"modelspec_price_id": PRICE,
                                 "modelspec_key_fingerprint": fingerprint})
    outcome = run(apply(kv, policy, payload("checkout.session.completed", obj, "evt_auth_plan"),
                        ledger=ledger))
    assert outcome.status == 200
    assert outcome.body["action"] == "credited"
    assert len(_key_records(kv)) == 1
    holder = _holder(key)
    assert run(ledger.balance(holder)).monthly == 4000
    assert serve(key, kv, policy).tier == "paid"

    claimed = _claim(kv, policy, ledger, session)
    assert claimed.status == 200
    assert "key" not in claimed.body
    assert claimed.body["applied_to"] == "existing_key"
    assert claimed.body["message"] == billing.PLAN_ATTACHED
    assert claimed.body["key_id"] == keys.key_id(key)
    assert len(_key_records(kv)) == 1
    again = _claim(kv, policy, ledger, session)
    assert again.status == 410
    replay = run(apply(kv, policy, payload("checkout.session.completed", obj, "evt_auth_plan"),
                       ledger=ledger))
    assert replay.body["duplicate"] is True
    assert run(ledger.balance(holder)).monthly == 4000


def test_authenticated_pack_stores_no_plaintext_key(policy):
    kv = MemoryKV()
    ledger = credits.MemoryLedger()
    key = _issue(kv, policy)
    fingerprint = keys.fingerprint(key)
    session = "cs_plain_pack"
    obj = {
        "id": session, "object": "checkout.session", "mode": "payment",
        "payment_status": "paid", "customer": CUS,
        "metadata": {"modelspec_price_id": PACK5,
                     "modelspec_key_fingerprint": fingerprint},
    }
    assert run(apply(kv, policy, payload("checkout.session.completed", obj, "evt_plain_pack"),
                     ledger=ledger)).status == 200
    claimed = _claim(kv, policy, ledger, session)
    assert claimed.status == 200
    for name, value in kv.data.items():
        assert key not in name
        assert key not in value
        parsed = json.loads(value)
        assert "secret" not in parsed
        assert parsed.get("key") != key
        if "key_fingerprint" in parsed:
            assert parsed["key_fingerprint"] in {"", fingerprint}


def test_invoice_paid_with_fingerprint_attaches_to_existing_key(policy):
    kv = MemoryKV()
    ledger = credits.MemoryLedger()
    key = _issue(kv, policy, tier="free")
    fingerprint = keys.fingerprint(key)
    obj = invoice_obj(parent={"subscription_details": {
        "subscription": SUB,
        "metadata": {"modelspec_key_fingerprint": fingerprint},
    }})
    outcome = run(apply(kv, policy, payload("invoice.paid", obj, "evt_inv_fp"),
                        ledger=ledger))
    assert outcome.status == 200
    assert len(_key_records(kv)) == 1
    assert run(ledger.balance(_holder(key))).monthly == 4000
    assert serve(key, kv, policy).tier == "paid"
    replay = run(apply(kv, policy, payload("invoice.paid", obj, "evt_inv_fp"),
                       ledger=ledger))
    assert replay.body["duplicate"] is True
    assert run(ledger.balance(_holder(key))).monthly == 4000


def test_a_plaintext_key_in_stripe_metadata_is_not_treated_as_a_fingerprint(policy):
    kv = MemoryKV()
    ledger = credits.MemoryLedger()
    key = _issue(kv, policy)
    obj = {
        "id": "cs_not_a_fp", "object": "checkout.session", "mode": "payment",
        "payment_status": "paid", "customer": CUS,
        "metadata": {"modelspec_price_id": PACK5,
                     "modelspec_key_fingerprint": key},
    }
    assert run(apply(kv, policy, payload("checkout.session.completed", obj, "evt_not_fp"),
                     ledger=ledger)).status == 200
    for name, value in kv.data.items():
        assert key not in name
        assert key not in value
    claimed = _claim(kv, policy, ledger, "cs_not_a_fp")
    assert claimed.status == 200
    assert claimed.body["applied_to"] == "new_key"
    assert claimed.body["key"] != key
    assert len(_key_records(kv)) == 2


def _patch_entry_fetch(entry, capture: dict[str, str]):
    previous = entry.fetch

    async def stripe_fetch(url, options=None):
        capture["url"] = url
        capture["body"] = (options or {}).get("body", "")

        class Resp:
            ok = True
            status = 200

            async def text(self):
                return json.dumps({
                    "id": "cs_entry_bound",
                    "url": "https://checkout.stripe.com/c/pay/cs_entry_bound",
                })

        return Resp()

    entry.fetch = stripe_fetch
    return previous


def test_entry_checkout_bearer_binds_fingerprint_and_does_not_call_stripe_for_a_bad_key(
        entry, policy):
    capture: dict[str, str] = {}
    previous = _patch_entry_fetch(entry, capture)
    try:
        binding = _Bind()
        kv = CloudflareKV(binding)
        key, _ = run(keys.issue(kv, tier="paid", owner="tester", now=T0, policy=policy))
        worker = entry.Default()
        worker.env = _billing_env(binding)
        response = run(worker.fetch(_Req(
            "/v1/billing/checkout",
            body=json.dumps({"price_id": PACK5}),
            headers={"authorization": f"Bearer {key}"})))
        assert response.status == 200
        body = response.json()
        assert body["applied_to"] == "existing_key"
        assert body["key_id"] == keys.key_id(key)
        from urllib.parse import parse_qs, unquote
        fields = {k: v[0] for k, v in parse_qs(capture["body"]).items()}
        assert fields["metadata[modelspec_key_fingerprint]"] == keys.fingerprint(key)
        assert key not in capture["body"]
        assert key not in unquote(capture["body"])

        capture.clear()
        bad = run(worker.fetch(_Req(
            "/v1/billing/checkout",
            body=json.dumps({"price_id": PACK5}),
            headers={"authorization": "Bearer live_unknown_not_issued"})))
        assert bad.status == 401
        assert bad.json()["error"]["code"] == "invalid_api_key"
        assert "body" not in capture
    finally:
        entry.fetch = previous


def test_entry_omitted_price_id_is_400_and_does_not_call_stripe(entry):
    capture: dict[str, str] = {}
    previous = _patch_entry_fetch(entry, capture)
    try:
        worker = entry.Default()
        worker.env = _billing_env(_Bind())
        response = run(worker.fetch(_Req("/v1/billing/checkout", body="{}")))
        assert response.status == 400
        error = response.json()["error"]
        assert error["code"] == "invalid_request"
        assert PRICE in error["valid_price_ids"]
        assert PACK5 in error["valid_price_ids"]
        assert "never guessed" in error["message"]
        assert "body" not in capture
    finally:
        entry.fetch = previous


def test_checkout_always_asks_stripe_tax_for_a_billing_address():
    for mode in ("subscription", "payment"):
        form = billing_stripe.checkout_form(
            price_id=PRICE, success_url="https://s", cancel_url="https://c",
            terms_url="https://modelspec.dev/legal/terms/", mode=mode)
        fields = dict(urllib.parse.parse_qsl(form))
        assert fields["automatic_tax[enabled]"] == "true"
        assert fields["billing_address_collection"] == "required"


# ── MODEL-105: the form post beside JSON ─────────────────────────────────────

#: The exact response `POST /v1/billing/checkout` gave a JSON caller before
#: MODEL-105 added the form variant, captured from the unchanged Worker with
#: the stub Stripe in `_patch_entry_fetch`. A JSON caller keeps getting this.
JSON_CHECKOUT_GOLDEN_STATUS = 200
JSON_CHECKOUT_GOLDEN_HEADERS = {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
    "x-modelspec-service-commit": "testsha",
}
JSON_CHECKOUT_GOLDEN_BODY = (
    '{\n'
    '  "schema_version": "1.0",\n'
    '  "endpoint": "billing.checkout",\n'
    '  "service_commit": "testsha",\n'
    '  "url": "https://checkout.stripe.com/c/pay/cs_entry_bound",\n'
    '  "session_id": "cs_entry_bound",\n'
    '  "tier": "paid",\n'
    '  "kind": "pack",\n'
    '  "name": "1,250-credit pack",\n'
    '  "credits": 1250,\n'
    '  "price_id": "price_1UHRwmBPydVRHUBjMFS5bDPD",\n'
    '  "placeholder": false,\n'
    '  "what_you_buy": "1,250-credit pack: 1250 credits added to this key, '
    'expiring 12 months after purchase, oldest spent first. A funded key '
    'receives the paid answer, including cited commercial-use and '
    'data-residency determinations. Only successful results draw credits.",\n'
    '  "terms_url": "https://modelspec.dev/legal/terms/",\n'
    '  "applied_to": "new_key",\n'
    '  "result": []\n'
    '}'
)


def _json_checkout_through_entry(entry, headers: dict[str, str]):
    capture: dict[str, str] = {}
    previous = _patch_entry_fetch(entry, capture)
    try:
        worker = entry.Default()
        worker.env = _billing_env(_Bind())
        return run(worker.fetch(_Req(
            "/v1/billing/checkout", body=json.dumps({"price_id": PACK5}),
            headers=headers))), capture
    finally:
        entry.fetch = previous


@pytest.mark.parametrize("headers", [
    {},
    {"content-type": "application/json"},
    # What `curl -d '{"price_id": …}'` sends without `-H`: a JSON body under the
    # form content type. It was a JSON call before MODEL-105 and stays one.
    {"content-type": "application/x-www-form-urlencoded"},
], ids=["no-content-type", "application-json", "curl-d-default"])
def test_a_json_checkout_is_byte_identical_to_before_the_form_variant(entry, headers):
    response, capture = _json_checkout_through_entry(entry, headers)
    assert response.status == JSON_CHECKOUT_GOLDEN_STATUS
    assert response.headers == JSON_CHECKOUT_GOLDEN_HEADERS
    assert response.body == JSON_CHECKOUT_GOLDEN_BODY
    assert capture["url"].startswith("https://api.stripe.com/")


FORM = "application/x-www-form-urlencoded"


def _form_post(entry, body: str, *, env=None, content_type: str = FORM,
               headers: dict[str, str] | None = None):
    capture: dict[str, str] = {}
    previous = _patch_entry_fetch(entry, capture)
    try:
        worker = entry.Default()
        worker.env = env if env is not None else _billing_env(_Bind())
        response = run(worker.fetch(_Req(
            "/v1/billing/checkout", body=body,
            headers={"content-type": content_type, **(headers or {})})))
        return response, capture
    finally:
        entry.fetch = previous


@pytest.mark.parametrize("price_id", [PRICE, TEAM_PRICE, PACK5])
def test_a_form_post_is_a_303_to_stripe_checkout(entry, price_id):
    response, capture = _form_post(
        entry, urllib.parse.urlencode({"price_id": price_id}))
    assert response.status == 303
    assert response.headers["location"] == "https://checkout.stripe.com/c/pay/cs_entry_bound"
    fields = dict(urllib.parse.parse_qsl(capture["body"]))
    assert fields["line_items[0][price]"] == price_id
    assert response.json()["applied_to"] == "new_key"


def test_a_form_post_with_a_charset_parameter_is_still_a_form(entry):
    response, _ = _form_post(entry, f"price_id={PACK5}",
                             content_type=f"{FORM}; charset=UTF-8")
    assert response.status == 303


def test_a_form_post_is_anonymous_even_when_a_key_is_presented(entry, policy):
    binding = _Bind()
    key, _ = run(keys.issue(CloudflareKV(binding), tier="paid", owner="tester",
                            now=T0, policy=policy))
    response, capture = _form_post(
        entry, f"price_id={PACK5}", env=_billing_env(binding),
        headers={"authorization": f"Bearer {key}"})
    assert response.status == 303
    assert response.json()["applied_to"] == "new_key"
    assert "key_id" not in response.json()
    fields = dict(urllib.parse.parse_qsl(capture["body"]))
    assert not fields.get("metadata[modelspec_key_fingerprint]")
    assert keys.fingerprint(key) not in capture["body"]


@pytest.mark.parametrize(("body", "status", "code"), [
    # The same refusal a JSON caller gets for an unmapped Price.
    ("price_id=price_unknown_not_in_tiers", 500, "price_not_mapped"),
    ("price_id=", 400, "invalid_request"),
    ("", 400, "invalid_request"),
], ids=["unknown", "blank", "empty-body"])
def test_a_form_post_without_a_mapped_price_is_refused_not_redirected(
        entry, body, status, code):
    response, capture = _form_post(entry, body)
    assert response.status == status
    assert "location" not in response.headers
    assert response.json()["error"]["code"] == code
    assert "body" not in capture


def test_a_form_post_for_a_placeholder_price_is_refused_not_redirected(entry):
    tiers = json.loads((REPO_ROOT / "api" / "worker" / "tiers.json").read_text(encoding="utf-8"))
    tiers["billing"]["prices"][PACK5]["placeholder"] = True
    env = _billing_env(_Bind())
    env.TIER_POLICY = json.dumps(tiers)
    response, capture = _form_post(entry, f"price_id={PACK5}", env=env)
    assert response.status == 500
    assert "location" not in response.headers
    error = response.json()["error"]
    assert error["code"] == "price_not_mapped"
    assert error["price_id"] == PACK5
    assert "placeholder" in error["message"]
    assert "body" not in capture


@pytest.mark.parametrize("body", [
    f"price_id={PACK5}&price_id={PRICE}",
    f"price_id={PACK5}&key=live_something",
], ids=["repeated", "stray"])
def test_a_malformed_form_is_refused_before_stripe(entry, body):
    response, capture = _form_post(entry, body)
    assert response.status == 400
    assert response.json()["error"]["code"] == "invalid_request"
    assert "location" not in response.headers
    assert "body" not in capture


def test_a_form_post_when_billing_is_off_is_refused_the_same_way_as_json(entry):
    form, form_capture = _form_post(
        entry, f"price_id={PACK5}", env=_billing_env(_Bind(), flag="false"))
    capture: dict[str, str] = {}
    previous = _patch_entry_fetch(entry, capture)
    try:
        worker = entry.Default()
        worker.env = _billing_env(_Bind(), flag="false")
        as_json = run(worker.fetch(_Req(
            "/v1/billing/checkout", body=json.dumps({"price_id": PACK5}),
            headers={"content-type": "application/json"})))
    finally:
        entry.fetch = previous
    assert form.status == as_json.status == 503
    assert form.json()["error"]["code"] == "billing_not_enabled"
    assert form.body == as_json.body
    assert form.headers == as_json.headers
    assert "body" not in form_capture and "body" not in capture


# ── MODEL-105: the claim page a browser lands on after paying ───────────────

BROWSER_ACCEPT = ("text/html,application/xhtml+xml,application/xml;q=0.9,"
                  "image/avif,image/webp,*/*;q=0.8")

#: `GET /v1/billing/claim` as a JSON caller got it before MODEL-105, captured
#: from the unchanged Worker. The key is random per run, so it and its id are
#: masked; every other byte is pinned.
CLAIM_GOLDEN_HEADERS = JSON_CHECKOUT_GOLDEN_HEADERS
CLAIM_GOLDEN_BODY = (
    '{\n'
    '  "schema_version": "1.0",\n'
    '  "endpoint": "billing.claim",\n'
    '  "service_commit": "testsha",\n'
    '  "key_id": "<KEY_ID>",\n'
    '  "tier": "paid",\n'
    '  "plan": "Solo",\n'
    '  "credits": 4000,\n'
    '  "kind": "plan",\n'
    '  "what_you_bought": "Solo: 4000 credits each paid month, reset with no '
    'rollover. A funded key receives the paid answer, including cited '
    'commercial-use and data-residency determinations. Only successful results '
    'draw credits. Pack credits are unaffected by cancellation.",\n'
    '  "how": "Authorization: Bearer <key>",\n'
    '  "applied_to": "new_key",\n'
    '  "result": [],\n'
    '  "key": "<KEY>",\n'
    '  "shown": "once",\n'
    '  "message": "API key shown once. Store it; claiming again will not reveal it."\n'
    '}'
)


def _paid_then_claim(entry, accept: str | None, *, session: str = SESSION,
                     price: str = PRICE):
    binding = _Bind()
    worker = entry.Default()
    worker.env = _billing_env(binding)
    obj = checkout_obj(id=session, metadata={"modelspec_price_id": price})
    body = payload("checkout.session.completed", obj, f"evt_{session}")
    header = signed(body, timestamp=int(datetime.now(UTC).timestamp()))
    hook = run(worker.fetch(_Req("/v1/billing/stripe-webhook", body=body,
                                 headers={"stripe-signature": header})))
    assert hook.status == 200
    headers = {"accept": accept} if accept is not None else {}

    def claim():
        return run(worker.fetch(_Req(
            f"/v1/billing/claim?session_id={session}", method="GET", headers=headers)))
    return claim


def _mask(text: str, key: str) -> str:
    return text.replace(key, "<KEY>").replace(keys.key_id(key), "<KEY_ID>")


@pytest.mark.parametrize("accept", [
    None, "*/*", "application/json", "text/html, application/json",
    "application/json, text/html;q=0.5",
], ids=["none", "curl", "json", "tie", "json-preferred"])
def test_a_json_claim_is_byte_identical_to_before_the_html_page(entry, accept):
    first = _paid_then_claim(entry, accept)()
    key = first.json()["key"]
    assert first.status == 200
    assert first.headers == CLAIM_GOLDEN_HEADERS
    assert _mask(first.body, key) == CLAIM_GOLDEN_BODY


def _assert_static_page(page: str) -> None:
    lowered = page.lower()
    assert lowered.startswith("<!doctype html>")
    assert "<script" not in lowered
    # Inside real tags only: escaped text may spell anything.
    assert re.search(r"<[^>]*\bon[a-z]+=", lowered) is None
    assert re.search(r"<[^>]*\bsrc=", lowered) is None
    assert re.search(r"<link\b", lowered) is None
    assert "https://modelspec.dev" in page


@pytest.mark.parametrize("price", [PRICE, PACK5], ids=["plan", "pack"])
def test_a_browser_claim_is_a_readable_page_with_the_key_shown_once(
        entry, price, capsys):
    claim = _paid_then_claim(entry, BROWSER_ACCEPT, session=f"cs_html_{price[-4:]}",
                             price=price)
    first = claim()
    assert first.status == 200
    assert first.headers["content-type"] == "text/html; charset=utf-8"
    assert first.headers["cache-control"] == "no-store"
    assert first.headers["x-modelspec-service-commit"] == COMMIT
    page = first.body
    _assert_static_page(page)
    key = re.search(r"live_[A-Za-z0-9_\-]+", page).group(0)
    assert page.count(key) == 1
    assert "copy it now" in page.lower()
    assert "will not be shown again" in page.lower()
    assert f"Authorization: Bearer {key}" not in page  # the key appears once only
    assert "Authorization: Bearer &lt;key&gt;" in page
    mapping = access_config.load_policy().price(price)
    assert mapping.name.replace("&", "&amp;") in page
    assert f"{mapping.credits:,}" in page
    # The key is never logged.
    out = capsys.readouterr()
    assert key not in out.out and key not in out.err

    again = claim()
    assert again.status == 410
    assert again.headers["content-type"] == "text/html; charset=utf-8"
    _assert_static_page(again.body)
    assert key not in again.body
    assert "rotate" in again.body.lower()


def test_a_browser_claim_before_the_webhook_says_to_reload(entry):
    worker = entry.Default()
    worker.env = _billing_env(_Bind())
    response = run(worker.fetch(_Req(
        "/v1/billing/claim?session_id=cs_not_yet", method="GET",
        headers={"accept": BROWSER_ACCEPT})))
    assert response.status == 409
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    _assert_static_page(response.body)
    assert "reload" in response.body.lower()


def test_the_claim_page_escapes_everything():
    import billing_page
    body = {
        "endpoint": "billing.claim", "key": "live_<b>x</b>", "key_id": "<i>",
        "plan": "<script>alert(1)</script>", "credits": 5, "kind": "pack",
        "what_you_bought": "\"quoted\" & <tag>", "shown": "once",
        "message": "<m>", "applied_to": "new_key", "tier": "paid",
    }
    page = billing_page.claim_page(200, body)
    assert "<script>" not in page and "<b>" not in page and "<tag>" not in page
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page
    assert "live_&lt;b&gt;x&lt;/b&gt;" in page
    refusal = billing_page.claim_page(400, {"error": {
        "code": "invalid_request", "message": "<img src=x onerror=alert(1)>"}})
    assert "<img" not in refusal
    _assert_static_page(refusal)


@pytest.mark.parametrize(("accept", "html"), [
    (None, False), ("", False), ("*/*", False), ("application/json", False),
    ("text/html, application/json", False),
    ("text/html;q=0, */*", False),
    (BROWSER_ACCEPT, True), ("text/html", True),
    ("application/json;q=0.5, text/html", True),
])
def test_prefers_html_is_an_explicit_preference(accept, html):
    import billing_page
    assert billing_page.prefers_html(accept) is html
