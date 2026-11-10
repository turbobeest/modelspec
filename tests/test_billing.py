"""Stripe Checkout funds credits (MODEL-73, MODEL-93).

Signed fixture events, never Stripe's API. The Worker runs without the Stripe
SDK; these tests call the same HMAC and handlers the isolate will. A Checkout
that presents a live key credits that key; an anonymous Checkout mints at claim.
"""

from __future__ import annotations

import asyncio
import inspect
import itertools
import json
import re
import sys
import urllib.parse
from dataclasses import replace
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
import x402  # noqa: E402
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
    assert row.legacy is True
    assert row.kind == "plan"
    assert row.name == "Solo"
    assert row.credits == 4000
    assert row.usd == 10
    assert row.tier == "paid"
    team = policy.billing.prices[TEAM_PRICE]
    assert team.kind == "plan" and team.credits == 30000 and team.usd == 50
    assert team.legacy is True
    pack = policy.billing.prices[PACK5]
    assert pack.kind == "pack" and pack.credits == 1250 and pack.usd == 5
    assert pack.legacy is True
    current = policy.billing.prices["price_1UP22XBPydVRHUBjk9rrxOxN"]
    assert current.placeholder is False and current.legacy is False
    assert current.for_sale is True
    assert current.kind == "plan" and current.name == "Solo"
    assert current.credits == 2500 and current.usd == 29
    assert policy.tier("paid").paid is True
    assert policy.tier("paid").daily_limit is None
    assert policy.credits.weights["rank"] == 1
    assert policy.credits.weights["policy-check"] == 5
    assert policy.credits.weights["decide.none"] == 1
    assert policy.credits.weights["decide.summary"] == 1
    assert policy.credits.weights["decide.full"] == 2
    assert policy.credits.pack_expiry_days == 365


def test_x402_and_stripe_read_the_same_pack_table(policy):
    card_packs = sorted(
        ((row.name, row.credits, row.usd)
        for row in policy.billing.prices.values()
        if row.kind == "pack" and not row.legacy),
        key=lambda row: row[2],
    )
    x402_packs = [
        (pack.name, pack.credits, pack.usd)
        for pack in x402.packs_from_policy(policy)
    ]
    assert x402_packs == card_packs
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

def test_billing_is_live_with_live_prices_and_access_enforcement():
    """MODEL-96 opens Checkout and requires keys for machine data access."""
    from pipeline.worker_flags import production_vars

    variables = production_vars(REPO_ROOT)
    assert variables["BILLING_ENABLED"] == "true"
    assert variables["ACCESS_ENFORCED"] == "true"
    policy = json.loads((REPO_ROOT / "api" / "worker" / "tiers.json").read_text(encoding="utf-8"))
    legacy = {pid: row for pid, row in policy["billing"]["prices"].items() if row.get("legacy")}
    current = {pid: row for pid, row in policy["billing"]["prices"].items() if not row.get("legacy")}
    assert legacy and all(pid.startswith("price_1UHRw") for pid in legacy)
    assert not any(row["placeholder"] for row in legacy.values())
    # Pricing v2 live Prices, created by Jamie on 2026-10-10. Scale overage
    # stays a placeholder until MODEL-357 (meter events without the key hash).
    assert current and all(pid.startswith("price_1UP2") for pid in current)
    assert not any(row["placeholder"] for row in current.values())
    overage = current["price_1UP25VBPydVRHUBjzN0TInX1"]["overage"]
    assert overage["price_id"] == "price_PLACEHOLDER_scale_overage_v2"
    assert overage["placeholder"] is True
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
        kv=MemoryKV(), policy=for_sale(policy, PRICE), service_commit=COMMIT, http=Stripe()))
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


def for_sale(policy, *price_ids):
    """A copy that still sells the named legacy rows. The shipped file does not."""
    prices = dict(policy.billing.prices)
    for price_id in price_ids:
        prices[price_id] = replace(prices[price_id], legacy=False)
    return replace(policy, billing=replace(policy.billing, prices=prices))


def _sellable_policy_json(*price_ids: str) -> str:
    tiers = json.loads((REPO_ROOT / "api" / "worker" / "tiers.json").read_text(encoding="utf-8"))
    selling_a_plan = False
    for price_id in price_ids:
        row = tiers["billing"]["prices"][price_id]
        row["legacy"] = False
        selling_a_plan = selling_a_plan or row.get("kind") == "plan"
    if selling_a_plan:
        # A sold legacy plan is cheaper per credit than Scale overage. Drop the
        # overage object so this test copy still loads. Checkout of that plan
        # does not use it.
        for row in tiers["billing"]["prices"].values():
            row.pop("overage", None)
    return json.dumps(tiers)


def _sellable_env(access=None, *price_ids: str, **kwargs):
    env = _billing_env(access, **kwargs)
    env.TIER_POLICY = _sellable_policy_json(*(price_ids or (PACK5,)))
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
    assert billing._price_from_invoice(obj, set()) == PRICE

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
        origin="https://api.modelspec.test", kv=MemoryKV(), policy=for_sale(policy, PACK5),
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
        origin="https://api.modelspec.test", kv=kv, policy=for_sale(policy, PACK5),
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
        origin="https://api.modelspec.test", kv=kv, policy=for_sale(policy, PRICE),
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


def test_a_paid_invoice_grants_monthly_through_an_invoice_only_ledger(policy):
    class InvoiceLedger(credits.MemoryLedger):
        async def set_monthly(self, holder, units, invoice_id, plan="", customer_id="",
                              period_end=0, period_start=0, subscription_id=""):
            return await super().set_monthly(
                holder, units, invoice_id, plan, customer_id,
                period_end=period_end, period_start=period_start,
                subscription_id=subscription_id)

    kv = MemoryKV()
    ledger = InvoiceLedger()
    key = _issue(kv, policy, tier="free")
    obj = invoice_obj(parent={"subscription_details": {
        "subscription": SUB,
        "metadata": {"modelspec_key_fingerprint": keys.fingerprint(key)},
    }})
    outcome = run(apply(kv, policy, payload("invoice.paid", obj, "evt_invoice_only"),
                        ledger=ledger))
    assert outcome.status == 200
    assert run(ledger.balance(_holder(key))).monthly == 4000
    assert serve(key, kv, policy).tier == "paid"


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
        worker.env = _sellable_env(binding, PACK5)
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
# MODEL-291 adds discovery metadata to every /v1 response; body bytes stay pinned.
from api.worker.src.agent_guide import GUIDE_URL, GUIDE_VERSION

GUIDE_HEADERS = {
    "Link": f'<{GUIDE_URL}>; rel="describedby"',
    "x-modelspec-guide-version": GUIDE_VERSION,
    "access-control-expose-headers": "Link, x-modelspec-guide-version",
}
JSON_CHECKOUT_GOLDEN_HEADERS = {
    **GUIDE_HEADERS,
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
        worker.env = _sellable_env(_Bind(), PACK5)
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
    assert {key: value for key, value in response.headers.items()
            if key.lower() != "server-timing"} == JSON_CHECKOUT_GOLDEN_HEADERS
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
        entry, urllib.parse.urlencode({"price_id": price_id}),
        env=_sellable_env(_Bind(), price_id))
    assert response.status == 303
    assert response.headers["location"] == "https://checkout.stripe.com/c/pay/cs_entry_bound"
    fields = dict(urllib.parse.parse_qsl(capture["body"]))
    assert fields["line_items[0][price]"] == price_id
    assert response.json()["applied_to"] == "new_key"


def test_a_form_post_with_a_charset_parameter_is_still_a_form(entry):
    response, _ = _form_post(entry, f"price_id={PACK5}",
                             env=_sellable_env(_Bind(), PACK5),
                             content_type=f"{FORM}; charset=UTF-8")
    assert response.status == 303


def test_a_form_post_is_anonymous_even_when_a_key_is_presented(entry, policy):
    binding = _Bind()
    key, _ = run(keys.issue(CloudflareKV(binding), tier="paid", owner="tester",
                            now=T0, policy=policy))
    response, capture = _form_post(
        entry, f"price_id={PACK5}", env=_sellable_env(binding, PACK5),
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


@pytest.mark.parametrize("isolate_served", [False, True], ids=["cold", "warm"])
def test_a_form_post_when_billing_is_off_is_refused_the_same_way_as_json(
        entry, monkeypatch, isolate_served):
    monkeypatch.setattr(entry, "_isolate_served", isolate_served)
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
    assert {key: value for key, value in form.headers.items()
            if key.lower() != "server-timing"} == {
                key: value for key, value in as_json.headers.items()
                if key.lower() != "server-timing"}
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
    assert {key: value for key, value in first.headers.items()
            if key.lower() != "server-timing"} == CLAIM_GOLDEN_HEADERS
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


class RotationKV(MemoryKV):
    fail_name = ""
    fail_after = False
    failure_seen = False

    async def get(self, name):
        value = await super().get(name)
        await asyncio.sleep(0)
        return value

    async def put(self, name, value, **kwargs):
        selected = self.fail_name and name.startswith(self.fail_name) and not self.failure_seen
        if selected and not self.fail_after:
            self.failure_seen = True
            raise OSError("fixture rotation write unavailable")
        await super().put(name, value, **kwargs)
        if selected:
            self.failure_seen = True
            raise OSError("fixture rotation write unavailable")
        await asyncio.sleep(0)


def test_rotation_keeps_source_funded_until_keyref_is_written(policy):
    async def scenario():
        kv, ledger = RotationKV(), credits.MemoryLedger()
        key, _ = await keys.issue(kv, tier="paid", owner="fixture", now=T0, policy=policy)
        holder = credits.holder_from_fingerprint(keys.fingerprint(key))
        await ledger.set_monthly(holder, 100, "rotation-invoice", "fixture")
        kv.fail_name = "keyref:"
        with pytest.raises(OSError, match="rotation write"):
            await billing.rotate(api_key=key, kv=kv, policy=policy, now=T0,
                                 service_commit=COMMIT, ledger=ledger)
        assert (await keys.lookup(kv, key)).active
        assert (await ledger.balance(holder)).available == 100
        retried = await billing.rotate(api_key=key, kv=kv, policy=policy, now=T0,
                                       service_commit=COMMIT, ledger=ledger)
        assert retried.status == 200
        successor = credits.holder_from_fingerprint(keys.fingerprint(retried.body["key"]))
        assert (await ledger.balance(successor)).available == 100
        assert (await ledger.balance(holder)).available == 0
    run(scenario())


def test_overlapping_rotations_return_one_funded_successor(policy):
    async def scenario():
        kv, ledger = RotationKV(), credits.MemoryLedger()
        key, _ = await keys.issue(kv, tier="paid", owner="fixture", now=T0, policy=policy)
        holder = credits.holder_from_fingerprint(keys.fingerprint(key))
        await ledger.set_monthly(holder, 100, "overlap-invoice", "fixture")
        results = await asyncio.gather(*(billing.rotate(
            api_key=key, kv=kv, policy=policy, now=T0,
            service_commit=COMMIT, ledger=ledger) for _ in range(2)))
        assert sorted(result.status for result in results) == [200, 403]
        successful = next(result for result in results if result.status == 200)
        successor = credits.holder_from_fingerprint(keys.fingerprint(successful.body["key"]))
        assert (await ledger.balance(successor)).available == 100
        assert not (await keys.lookup(kv, key)).active
        assert (await billing.rotate(api_key=key, kv=kv, policy=policy, now=T0,
                                    service_commit=COMMIT, ledger=ledger)).status == 403
    run(scenario())


@pytest.mark.parametrize("write_number", [1, 2, 3, 4])
@pytest.mark.parametrize("after_write", [False, True])
def test_rotation_resumes_each_metadata_write(policy, write_number, after_write):
    class InterruptedKV(MemoryKV):
        writes = 0
        armed = False

        async def put(self, name, value, **kwargs):
            if self.armed:
                self.writes += 1
                selected = self.writes == write_number
            else:
                selected = False
            if selected and not after_write:
                raise OSError("fixture metadata interruption")
            await super().put(name, value, **kwargs)
            if selected:
                raise OSError("fixture metadata interruption")

    async def scenario():
        kv, ledger = InterruptedKV(), credits.MemoryLedger()
        await apply(kv, policy, payload("checkout.session.completed", checkout_obj(),
                                       "evt_rotation_resume"), ledger=ledger)
        claimed = await billing.claim(session_id=SESSION, kv=kv, policy=policy,
                                      now=T0, service_commit=COMMIT, ledger=ledger)
        assert claimed.status == 200
        key = claimed.body["key"]
        kv.armed = True
        with pytest.raises(OSError, match="metadata interruption"):
            await billing.rotate(api_key=key, kv=kv, policy=policy, now=T0,
                                 service_commit=COMMIT, ledger=ledger)
        retried = await billing.rotate(api_key=key, kv=kv, policy=policy, now=T0,
                                       service_commit=COMMIT, ledger=ledger)
        assert retried.status == 200
        successor_key = retried.body["key"]
        successor = keys.fingerprint(successor_key)
        assert (await ledger.balance(credits.holder_from_fingerprint(successor))).monthly == 4000
        assert not (await keys.lookup(kv, key)).active
        assert (await billing.store.load_subscription(kv, SUB)).key_fingerprint == successor
        again = await billing.rotate(api_key=key, kv=kv, policy=policy, now=T0,
                                     service_commit=COMMIT, ledger=ledger)
        assert again.status == 403
        persisted = json.dumps(kv.data) + json.dumps(ledger.state.to_json())
        assert key not in persisted and successor_key not in persisted
    run(scenario())


def _billing_holder(key):
    return credits.holder_from_fingerprint(keys.fingerprint(key))


async def _dated_event(kv, ledger, policy, kind, obj, event_id, *, created=100):
    body = json.dumps({"id": event_id, "type": kind, "created": created,
                       "data": {"object": obj}})
    return await apply(kv, policy, body, ledger=ledger)


async def _billing_purchase(kv, ledger, policy, *, bound=False):
    obj = checkout_obj(invoice="in_initial", created=100)
    if bound:
        key, _ = await keys.issue(kv, tier="paid", owner="fixture", now=T0, policy=policy)
        obj["metadata"]["modelspec_key_fingerprint"] = keys.fingerprint(key)
    assert (await _dated_event(kv, ledger, policy, "checkout.session.completed", obj,
                               "evt_initial")).status == 200
    if not bound:
        claimed = await billing.claim(session_id=SESSION, kv=kv, policy=policy,
                                      now=T0, service_commit=COMMIT, ledger=ledger)
        assert claimed.status == 200
        key = claimed.body["key"]
    return key


async def _spend_billing_credits(ledger, key, units):
    reservation = await ledger.reserve(_billing_holder(key), units)
    assert reservation.ok
    assert await ledger.commit(_billing_holder(key), reservation.reservation_id)


@pytest.mark.parametrize("downgrade", ["invoice.payment_failed", "customer.subscription.deleted",
                                       "customer.subscription.updated"])
def test_renewal_and_downgrade_follow_current_subscription_key(policy, downgrade):
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy, bound=True)
        rotated = await billing.rotate(api_key=key, kv=kv, policy=policy, now=T0,
                                       service_commit=COMMIT, ledger=ledger)
        assert rotated.status == 200
        successor = rotated.body["key"]
        await _spend_billing_credits(ledger, successor, 500)
        fields = urllib.parse.parse_qs(billing_stripe.checkout_form(
            price_id=PRICE, success_url="https://local.test/success",
            cancel_url="https://local.test/cancel", terms_url="https://local.test/terms",
            key_fingerprint=keys.fingerprint(key)))
        metadata = {name: fields[f"subscription_data[metadata][{name}]"][0]
                    for name in ("modelspec_price_id", "modelspec_key_fingerprint")}
        renewal = dahlia_invoice_obj(id="in_renewal", parent={
            "type": "subscription_details", "subscription_details": {
                "subscription": SUB, "metadata": metadata}})
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", renewal,
                                   "evt_renewal", created=200)).status == 200
        assert (await ledger.balance(_billing_holder(key))).monthly == 0
        assert (await ledger.balance(_billing_holder(successor))).monthly == 4000
        sub = await billing.store.load_subscription(kv, SUB)
        assert sub.key_fingerprint == keys.fingerprint(successor)
        obj = (renewal if downgrade == "invoice.payment_failed" else
               {"id": SUB, "status": "canceled", "metadata": metadata})
        assert (await _dated_event(kv, ledger, policy, downgrade, obj,
                                   "evt_downgrade", created=300)).status == 200
        assert (await keys.lookup(kv, successor)).tier == "free"
        assert (await ledger.balance(_billing_holder(successor))).monthly == 0
        assert (await ledger.balance(_billing_holder(key))).monthly == 0
        assert not (await keys.lookup(kv, key)).active
    run(scenario())


@pytest.mark.parametrize("late_created", [150, 900])
def test_subscription_cancellation_remains_current(policy, late_created):
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        deleted = {"id": SUB, "status": "canceled", "customer": CUS, "canceled_at": 300}
        assert (await _dated_event(kv, ledger, policy, "customer.subscription.deleted",
                                   deleted, "evt_cancel", created=300)).status == 200
        invoice = invoice_obj(id="in_delayed", created=100, period_start=100, period_end=200)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", invoice,
                                   "evt_delayed", created=late_created)).status == 200
        assert (await keys.lookup(kv, key)).tier == "free"
        assert (await ledger.balance(_billing_holder(key))).monthly == 0
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", invoice,
                                   "evt_delayed", created=late_created)).body["duplicate"]
    run(scenario())


@pytest.mark.parametrize("terminal", ["customer.subscription.deleted",
                                      "customer.subscription.updated"])
def test_newer_paid_period_applies_after_terminal_status(policy, terminal):
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        if terminal == "customer.subscription.deleted":
            ended = {"id": SUB, "status": "canceled", "customer": CUS, "canceled_at": 300}
        else:
            ended = {"id": SUB, "status": "incomplete_expired", "customer": CUS}
        assert (await _dated_event(kv, ledger, policy, terminal, ended,
                                   "evt_terminal", created=300)).status == 200
        assert (await keys.lookup(kv, key)).tier == "free"
        invoice = invoice_obj(id="in_recovered", created=400, period_start=400, period_end=500)
        outcome = await _dated_event(kv, ledger, policy, "invoice.paid", invoice,
                                     "evt_recovered", created=400)
        assert outcome.status == 200
        assert outcome.body["action"] == "credited"
        assert (await keys.lookup(kv, key)).tier == "paid"
        assert (await ledger.balance(_billing_holder(key))).monthly == 4000
    run(scenario())


class _ScheduledKV(MemoryKV):
    """One handler's view of a shared store. Each get and put yields `pauses` times."""

    def __init__(self, data: dict[str, str], pauses: int) -> None:
        super().__init__()
        self.data = data
        self.pauses = pauses

    async def _pause(self) -> None:
        for _ in range(self.pauses):
            await asyncio.sleep(0)

    async def get(self, name: str) -> str | None:
        await self._pause()
        return await super().get(name)

    async def put(self, name: str, value: str, **kwargs: Any) -> None:
        await self._pause()
        await super().put(name, value, **kwargs)


class _NoProcessLock:
    """MemoryLedger with no process-local billing lock, as DurableLedger is."""

    def __init__(self, inner: credits.MemoryLedger) -> None:
        object.__setattr__(self, "_inner", inner)

    def __getattr__(self, name: str) -> Any:
        if name == "_billing_lock":
            raise AttributeError(name)
        return getattr(self._inner, name)


def test_overlapped_old_failure_keeps_newer_paid_allowance(policy):
    async def overlapped(kind: str, pauses_paid: int, pauses_other: int,
                         paid_first: bool) -> tuple[str, int]:
        data: dict[str, str] = {}
        real = credits.MemoryLedger()
        key = await _billing_purchase(_ScheduledKV(data, 0), real, policy)
        ledger = _NoProcessLock(real)
        paid_kv = _ScheduledKV(data, pauses_paid)
        other_kv = _ScheduledKV(data, pauses_other)
        if kind == "failure":
            paid = invoice_obj(id="in_new", created=300, period_start=300, period_end=400)
            other = invoice_obj(id="in_old", paid=False, created=100,
                                period_start=100, period_end=200)
            paid_event = _dated_event(
                paid_kv, ledger, policy, "invoice.paid", paid, "evt_paid", created=300)
            other_event = _dated_event(
                other_kv, ledger, policy, "invoice.payment_failed", other,
                "evt_fail", created=150)
        else:
            paid = invoice_obj(id="in_old", created=150, period_start=100, period_end=200)
            other = {"id": SUB, "status": "canceled", "customer": CUS, "canceled_at": 300}
            paid_event = _dated_event(
                paid_kv, ledger, policy, "invoice.paid", paid, "evt_paid", created=150)
            other_event = _dated_event(
                other_kv, ledger, policy, "customer.subscription.deleted", other,
                "evt_cancel", created=300)
        calls = [paid_event, other_event] if paid_first else [other_event, paid_event]
        await asyncio.gather(*calls)
        record = await keys.lookup(_ScheduledKV(data, 0), key)
        balance = await real.balance(_billing_holder(key))
        sub = await billing.store.load_subscription(_ScheduledKV(data, 0), SUB)
        return record.tier, balance.monthly, sub.tier, sub.status

    async def scenario():
        mismatches = []
        for kind, expect in (
                ("failure", ("paid", 4000, "paid", "active")),
                ("cancellation", ("free", 0, "free", "inactive"))):
            for paid_first in (True, False):
                for pauses_paid in (1, 2, 3):
                    for pauses_other in (1, 2, 3):
                        got = await overlapped(kind, pauses_paid, pauses_other, paid_first)
                        if got != expect:
                            mismatches.append(
                                (kind, paid_first, pauses_paid, pauses_other, got))
        assert mismatches == []

    run(scenario())


@pytest.mark.parametrize("canceled_at,created", [(350, 350), (350, 400), (400, 400), (401, 401)])
def test_cancel_inside_paid_period_clears(policy, canceled_at, created):
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        paid = invoice_obj(id="in_p", created=300, period_start=300, period_end=400)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", paid,
                                   "evt_p", created=300)).status == 200
        deleted = {"id": SUB, "status": "canceled", "customer": CUS, "canceled_at": canceled_at}
        outcome = await _dated_event(kv, ledger, policy, "customer.subscription.deleted",
                                     deleted, "evt_c", created=created)
        assert outcome.status == 200
        assert (await keys.lookup(kv, key)).tier == "free"
        assert (await ledger.balance(_billing_holder(key))).monthly == 0
    run(scenario())


def test_updated_canceled_inside_paid_period_clears(policy):
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        paid = invoice_obj(id="in_p", created=300, period_start=300, period_end=400)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", paid,
                                   "evt_p", created=300)).status == 200
        ended = {"id": SUB, "status": "canceled", "customer": CUS, "canceled_at": 350}
        outcome = await _dated_event(kv, ledger, policy, "customer.subscription.updated",
                                     ended, "evt_c", created=350)
        assert outcome.status == 200
        assert (await keys.lookup(kv, key)).tier == "free"
        assert (await ledger.balance(_billing_holder(key))).monthly == 0
    run(scenario())


def test_cancel_before_paid_period_start_stays_paid(policy):
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        paid = invoice_obj(id="in_p", created=400, period_start=400, period_end=500)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", paid,
                                   "evt_p", created=400)).status == 200
        deleted = {"id": SUB, "status": "canceled", "customer": CUS, "canceled_at": 300}
        outcome = await _dated_event(kv, ledger, policy, "customer.subscription.deleted",
                                     deleted, "evt_c", created=300)
        assert outcome.status == 200
        assert outcome.body["action"] == "ignored"
        assert (await keys.lookup(kv, key)).tier == "paid"
        assert (await ledger.balance(_billing_holder(key))).monthly == 4000
    run(scenario())


def test_checkout_only_terminal_cancel_clears(policy):
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        deleted = {"id": SUB, "status": "canceled", "customer": CUS, "canceled_at": 300}
        outcome = await _dated_event(kv, ledger, policy, "customer.subscription.deleted",
                                     deleted, "evt_c", created=300)
        assert outcome.status == 200
        assert outcome.body["action"] == "downgraded"
        assert (await keys.lookup(kv, key)).tier == "free"
        assert (await ledger.balance(_billing_holder(key))).monthly == 0
    run(scenario())


def test_late_invoice_that_began_before_cancellation_stays_free(policy):
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        deleted = {"id": SUB, "status": "canceled", "customer": CUS, "canceled_at": 350}
        assert (await _dated_event(kv, ledger, policy, "customer.subscription.deleted",
                                   deleted, "evt_c", created=350)).status == 200
        assert (await keys.lookup(kv, key)).tier == "free"
        paid = invoice_obj(id="in_p", created=300, period_start=300, period_end=400)
        outcome = await _dated_event(kv, ledger, policy, "invoice.paid", paid,
                                     "evt_p", created=300)
        assert outcome.status == 200
        assert outcome.body["action"] == "ignored"
        assert (await keys.lookup(kv, key)).tier == "free"
        assert (await ledger.balance(_billing_holder(key))).monthly == 0
    run(scenario())


def test_invoice_starting_after_cancellation_applies_when_event_is_later(policy):
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        deleted = {"id": SUB, "status": "canceled", "customer": CUS, "canceled_at": 350}
        assert (await _dated_event(kv, ledger, policy, "customer.subscription.deleted",
                                   deleted, "evt_c", created=400)).status == 200
        paid = invoice_obj(id="in_p", created=360, period_start=360, period_end=400)
        outcome = await _dated_event(kv, ledger, policy, "invoice.paid", paid,
                                     "evt_p", created=360)
        assert outcome.status == 200
        assert outcome.body["action"] == "credited"
        assert (await keys.lookup(kv, key)).tier == "paid"
        assert (await ledger.balance(_billing_holder(key))).monthly == 4000
    run(scenario())


def test_second_invoice_with_the_same_period_end_applies(policy):
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        first = invoice_obj(id="in_a", created=300, period_start=300, period_end=400)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", first,
                                   "evt_a", created=300)).status == 200
        await _spend_billing_credits(ledger, key, 100)
        second = invoice_obj(id="in_b", created=350, period_start=350, period_end=400)
        outcome = await _dated_event(kv, ledger, policy, "invoice.paid", second,
                                     "evt_b", created=350)
        assert outcome.status == 200
        assert outcome.body["action"] == "credited"
        assert (await keys.lookup(kv, key)).tier == "paid"
        assert (await ledger.balance(_billing_holder(key))).monthly == 4000
        replay = await _dated_event(kv, ledger, policy, "invoice.paid", second,
                                    "evt_b_replay", created=350)
        assert replay.status == 200
        assert (await ledger.balance(_billing_holder(key))).monthly == 4000
        await _spend_billing_credits(ledger, key, 100)
        earlier = invoice_obj(id="in_c", created=360, period_start=100, period_end=400)
        again = await _dated_event(kv, ledger, policy, "invoice.paid", earlier,
                                   "evt_c", created=360)
        assert again.status == 200
        assert again.body["action"] == "credited"
        assert (await ledger.balance(_billing_holder(key))).monthly == 4000
    run(scenario())


def test_payment_failed_at_the_stored_period_end_stays_paid(policy):
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        paid = invoice_obj(id="in_a", created=300, period_start=300, period_end=400)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", paid,
                                   "evt_a", created=300)).status == 200
        await _spend_billing_credits(ledger, key, 100)
        failed = invoice_obj(id="in_fail", paid=False, created=350,
                             period_start=350, period_end=400)
        outcome = await _dated_event(kv, ledger, policy, "invoice.payment_failed", failed,
                                     "evt_fail", created=350)
        assert outcome.status == 200
        assert outcome.body["action"] == "ignored"
        assert (await keys.lookup(kv, key)).tier == "paid"
        assert (await ledger.balance(_billing_holder(key))).monthly == 3900
    run(scenario())


def test_invoice_without_period_after_cancellation_stays_free(policy):
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        deleted = {"id": SUB, "status": "canceled", "customer": CUS, "canceled_at": 300}
        assert (await _dated_event(kv, ledger, policy, "customer.subscription.deleted",
                                   deleted, "evt_c", created=300)).status == 200
        bare = invoice_obj(id="in_bare", created=400)
        outcome = await _dated_event(kv, ledger, policy, "invoice.paid", bare,
                                     "evt_bare", created=400)
        assert outcome.status == 200
        assert outcome.body["action"] == "ignored"
        assert (await keys.lookup(kv, key)).tier == "free"
        assert (await ledger.balance(_billing_holder(key))).monthly == 0
    run(scenario())


def test_watermark_only_row_clears_on_cancellation():
    holder = "holder-old"
    ledger = credits.MemoryLedger(credits.LedgerState.from_json({
        "accounts": {
            holder: {
                "monthly": 4000,
                "invoice_period_watermark": 400,
                "monthly_entitled": True,
            }
        }
    }))
    result = run(ledger.clear_monthly(holder, watermark=350))
    assert result.reason == "cleared"
    assert run(ledger.balance(holder)).monthly == 0


def test_payment_failed_without_period_keeps_a_stored_paid_period(policy):
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        paid = invoice_obj(id="in_new", period_start=300, period_end=400)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", paid,
                                   "evt_new", created=300)).status == 200
        failed = invoice_obj(id="in_bare", paid=False)
        outcome = await _dated_event(kv, ledger, policy, "invoice.payment_failed", failed,
                                     "evt_bare", created=500)
        assert outcome.status == 200
        assert outcome.body["action"] == "ignored"
        assert (await keys.lookup(kv, key)).tier == "paid"
        assert (await ledger.balance(_billing_holder(key))).monthly == 4000
        stored = await billing.store.load_subscription(kv, SUB)
        assert stored.invoice_paid
        assert (stored.invoice_period_start, stored.invoice_period_end) == (300, 400)

    run(scenario())


def test_active_subscription_update_applies_after_cancellation(policy):
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        deleted = {"id": SUB, "status": "canceled", "customer": CUS, "canceled_at": 300}
        assert (await _dated_event(kv, ledger, policy, "customer.subscription.deleted",
                                   deleted, "evt_cancel", created=300)).status == 200
        active = {"id": SUB, "status": "active", "customer": CUS,
                  "items": {"data": [{"price": {"id": PRICE}}]}}
        outcome = await _dated_event(kv, ledger, policy, "customer.subscription.updated",
                                     active, "evt_active", created=400)
        assert outcome.status == 200
        assert outcome.body["action"] == "unchanged"
        assert (await keys.lookup(kv, key)).tier == policy.billing.downgrade_tier
    run(scenario())


def test_active_status_update_tier_follows_the_ledger(policy):
    """An active status update writes the downgrade tier until an accepted invoice."""

    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        deleted = {"id": SUB, "status": "canceled", "customer": CUS, "canceled_at": 300}
        assert (await _dated_event(
            kv, ledger, policy, "customer.subscription.deleted", deleted,
            "evt_cancel_follow", created=300)).status == 200
        assert (await ledger.entitlement_view(_billing_holder(key)))["entitled"] is False
        active = {"id": SUB, "status": "active", "customer": CUS,
                  "items": {"data": [{"price": {"id": PRICE}}]}}
        outcome = await _dated_event(
            kv, ledger, policy, "customer.subscription.updated", active,
            "evt_active_follow", created=400)
        assert outcome.status == 200
        assert (await keys.lookup(kv, key)).tier == policy.billing.downgrade_tier
        stored = await billing.store.load_subscription(kv, SUB)
        assert stored is not None
        assert stored.subscription_status == "active"
        assert stored.tier == policy.billing.downgrade_tier
        invoice = invoice_obj(id="in_after_active", period_start=400, period_end=500)
        paid = await _dated_event(
            kv, ledger, policy, "invoice.paid", invoice, "evt_after_active", created=400)
        assert paid.status == 200
        assert (await keys.lookup(kv, key)).tier == "paid"
        assert (await ledger.balance(_billing_holder(key))).monthly == 4000
    run(scenario())


def test_subscription_create_after_checkout_without_an_invoice_id(policy):
    """A subscription_create invoice records the checkout grant's invoice and period."""

    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key, _record = await keys.issue(kv, tier="paid", owner="fixture", now=T0, policy=policy)
        meta = {"modelspec_price_id": PRICE, "modelspec_key_fingerprint": keys.fingerprint(key)}
        assert (await _dated_event(
            kv, ledger, policy, "checkout.session.completed", checkout_obj(metadata=meta),
            "evt_checkout_no_invoice")).status == 200
        await _spend_billing_credits(ledger, key, 100)
        holder = _billing_holder(key)
        monthly = (await ledger.balance(holder)).monthly
        invoice = invoice_obj(
            id="in_create", billing_reason="subscription_create", metadata=meta,
            period_start=100, period_end=200)
        outcome = await _dated_event(
            kv, ledger, policy, "invoice.paid", invoice, "evt_create", created=100)
        assert outcome.status == 200
        assert (await ledger.balance(holder)).monthly == monthly
        stored = await billing.store.load_subscription(kv, SUB)
        assert stored is not None
        assert stored.invoice_id == "in_create"
        assert (stored.invoice_period_start, stored.invoice_period_end) == (100, 200)
        again = await _dated_event(
            kv, ledger, policy, "invoice.paid", invoice, "evt_create_again", created=100)
        assert again.status == 200
        assert (await ledger.balance(holder)).monthly == monthly

        other, _other_record = await keys.issue(
            kv, tier="paid", owner="fixture", now=T0, policy=policy)
        other_meta = {
            "modelspec_price_id": PRICE,
            "modelspec_key_fingerprint": keys.fingerprint(other),
        }
        other_invoice = invoice_obj(
            id="in_other_create", subscription=SUB2, billing_reason="subscription_create",
            metadata=other_meta, period_start=100, period_end=200)
        other_outcome = await _dated_event(
            kv, ledger, policy, "invoice.paid", other_invoice, "evt_other_create", created=100)
        assert other_outcome.status == 200
        assert other_outcome.body["action"] == "credited"
        assert (await ledger.balance(_billing_holder(other))).monthly == 4000
        assert (await ledger.balance(holder)).monthly == monthly

        later = invoice_obj(
            id="in_later_create", billing_reason="subscription_create", metadata=meta,
            period_start=300, period_end=400)
        later_outcome = await _dated_event(
            kv, ledger, policy, "invoice.paid", later, "evt_later_create", created=300)
        assert later_outcome.status == 200
        assert (await ledger.balance(holder)).monthly == 4000
    run(scenario())


@pytest.mark.parametrize("late_kind", ["invoice.payment_failed", "invoice.paid"])
@pytest.mark.parametrize("late_created", [150, 900])
def test_current_invoice_period_retains_its_allowance(policy, late_kind, late_created):
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        paid = invoice_obj(id="in_new", created=300, period_start=300, period_end=400)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", paid,
                                   "evt_new", created=300)).status == 200
        await _spend_billing_credits(ledger, key, 100)
        older = invoice_obj(id="in_old", paid=late_kind == "invoice.paid", created=100,
                            period_start=100, period_end=200)
        assert (await _dated_event(kv, ledger, policy, late_kind, older,
                                   "evt_old", created=late_created)).status == 200
        assert (await keys.lookup(kv, key)).tier == "paid"
        assert (await ledger.balance(_billing_holder(key))).monthly == 3900
    run(scenario())


@pytest.mark.parametrize("order", [("checkout", "invoice"), ("invoice", "checkout")])
@pytest.mark.parametrize("bound", [False, True])
def test_cancellation_before_first_entitlement_stays_inactive(policy, order, bound):
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = ""
        meta = {"modelspec_price_id": PRICE}
        if bound:
            key, _ = await keys.issue(kv, tier="free", owner="fixture", now=T0, policy=policy)
            meta["modelspec_key_fingerprint"] = keys.fingerprint(key)
        assert (await _dated_event(kv, ledger, policy, "customer.subscription.deleted",
                                   {"id": SUB, "status": "canceled", "canceled_at": 300},
                                   "evt_cancel_first", created=300)).status == 200
        for kind in order:
            obj = (checkout_obj(invoice="in_initial", metadata=meta, created=100)
                   if kind == "checkout" else invoice_obj(
                       id="in_initial", metadata=meta, period_start=100, period_end=200))
            type_ = "checkout.session.completed" if kind == "checkout" else "invoice.paid"
            assert (await _dated_event(kv, ledger, policy, type_, obj,
                                       "evt_" + kind, created=150)).status == 200
        active = {"id": SUB, "status": "active", "items": {"data": [{"price": {"id": PRICE}}]}}
        assert (await _dated_event(kv, ledger, policy, "customer.subscription.updated",
                                   active, "evt_old_active", created=100)).status == 200
        sub = await billing.store.load_subscription(kv, SUB)
        assert sub is not None and sub.status == "inactive" and sub.pending_monthly == 0
        if key:
            assert (await ledger.balance(_billing_holder(key))).monthly == 0
            assert (await keys.lookup(kv, key)).tier == "free"
    run(scenario())


def test_paid_invoice_recovers_its_period_once(policy):
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        invoice = invoice_obj(id="in_recovery", period_start=300, period_end=400)
        assert (await _dated_event(kv, ledger, policy, "invoice.payment_failed", invoice,
                                   "evt_failed", created=300)).status == 200
        assert (await ledger.balance(_billing_holder(key))).monthly == 0
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", invoice,
                                   "evt_paid", created=310)).status == 200
        await _spend_billing_credits(ledger, key, 100)
        assert (await _dated_event(kv, ledger, policy, "invoice.payment_failed", invoice,
                                   "evt_delayed_failure", created=300)).status == 200
        assert (await ledger.balance(_billing_holder(key))).monthly == 3900
        newer = invoice_obj(id="in_next", period_start=400, period_end=500)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", newer,
                                   "evt_next", created=400)).status == 200
        assert (await ledger.balance(_billing_holder(key))).monthly == 4000
    run(scenario())


def test_checkout_link_retains_current_invoice_plan(policy):
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy, bound=True)
        current = invoice_obj(id="in_team", period_start=300, period_end=400,
                              lines={"data": [{"price": {"id": TEAM_PRICE},
                                                "period": {"start": 300, "end": 400}}]})
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", current,
                                   "evt_team", created=300)).status == 200
        await _spend_billing_credits(ledger, key, 100)
        old_checkout = checkout_obj(id="cs_delayed", invoice="in_initial", created=100,
                                    metadata={"modelspec_price_id": PRICE,
                                              "modelspec_key_fingerprint": keys.fingerprint(key)})
        assert (await _dated_event(kv, ledger, policy, "checkout.session.completed", old_checkout,
                                   "evt_checkout_delayed", created=900)).status == 200
        sub = await billing.store.load_subscription(kv, SUB)
        assert sub.plan_name == "Team" and sub.plan_credits == 30000
        assert (await ledger.balance(_billing_holder(key))).monthly == 29900
        assert await billing.store.load_session(kv, "cs_delayed") is not None
    run(scenario())


@pytest.mark.parametrize("pack", [False, True])
def test_purchase_claim_selects_one_funded_key(policy, pack):
    class OverlappingKV(MemoryKV):
        gate = None
        readers = 0

        async def get(self, name):
            value = await super().get(name)
            if self.gate is not None and name == billing.store.session_name(SESSION):
                self.readers += 1
                if self.readers >= 2:
                    self.gate.set()
                await self.gate.wait()
            await asyncio.sleep(0)
            return value

        async def put(self, name, value, **kwargs):
            await super().put(name, value, **kwargs)
            await asyncio.sleep(0)

    async def scenario():
        kv, ledger = OverlappingKV(), credits.MemoryLedger()
        obj = (checkout_obj(mode="payment", subscription=None,
                            metadata={"modelspec_price_id": PACK5}) if pack else checkout_obj())
        assert (await apply(kv, policy, payload("checkout.session.completed", obj,
                                               "evt_claim_once"), ledger=ledger)).status == 200
        kv.gate = asyncio.Event()
        results = await asyncio.gather(*(billing.claim(
            session_id=SESSION, kv=kv, policy=policy, now=T0,
            service_commit=COMMIT, ledger=ledger) for _ in range(2)))
        assert sorted(result.status for result in results) == [200, 410]
        successful = next(result for result in results if result.status == 200)
        key = successful.body["key"]
        assert (await ledger.balance(_billing_holder(key))).available == (1250 if pack else 4000)
        sub = await billing.store.load_subscription(kv, "pack:" + SESSION if pack else SUB)
        assert sub.key_fingerprint == keys.fingerprint(key)
        assert len([name for name in kv.data if name.startswith("key:")]) == 1
        replay = await billing.claim(session_id=SESSION, kv=kv, policy=policy, now=T0,
                                     service_commit=COMMIT, ledger=ledger)
        assert replay.status == 410
    run(scenario())


@pytest.mark.parametrize("pack", [False, True])
@pytest.mark.parametrize("write_number", [1, 2, 3, 4])
@pytest.mark.parametrize("after_write", [False, True])
def test_claim_recovers_unfunded_metadata_writes(policy, pack, write_number, after_write):
    class InterruptedKV(MemoryKV):
        armed = False
        writes = 0

        async def put(self, name, value, **kwargs):
            self.writes += int(self.armed)
            selected = self.armed and self.writes == write_number
            if selected and not after_write:
                raise OSError("fixture claim metadata unavailable")
            await super().put(name, value, **kwargs)
            if selected:
                raise OSError("fixture claim metadata unavailable")

    async def scenario():
        kv, ledger = InterruptedKV(), credits.MemoryLedger()
        obj = (checkout_obj(mode="payment", subscription=None,
                            metadata={"modelspec_price_id": PACK5}) if pack else checkout_obj())
        assert (await apply(kv, policy, payload("checkout.session.completed", obj,
                                               "evt_claim_recovery"), ledger=ledger)).status == 200
        kv.armed = True
        with pytest.raises(OSError, match="claim metadata"):
            await billing.claim(session_id=SESSION, kv=kv, policy=policy, now=T0,
                                service_commit=COMMIT, ledger=ledger)
        retried = await billing.claim(session_id=SESSION, kv=kv, policy=policy, now=T0,
                                      service_commit=COMMIT, ledger=ledger)
        assert retried.status == 200
        key = retried.body["key"]
        sub = await billing.store.load_subscription(kv, "pack:" + SESSION if pack else SUB)
        assert sub.key_fingerprint == keys.fingerprint(key)
        assert (await ledger.balance(_billing_holder(key))).available == (1250 if pack else 4000)
        active = [json.loads(value) for name, value in kv.data.items()
                  if name.startswith("key:") and json.loads(value)["active"]]
        assert len(active) == 1 and active[0]["key_id"] == keys.key_id(key)
        assert (await billing.claim(session_id=SESSION, kv=kv, policy=policy, now=T0,
                                    service_commit=COMMIT, ledger=ledger)).status == 410
        assert key not in json.dumps(kv.data) + json.dumps(ledger.state.to_json())
    run(scenario())


@pytest.mark.parametrize("pack", [False, True])
@pytest.mark.parametrize("after_funding", [False, True])
def test_claim_funding_preserves_selected_owner(policy, pack, after_funding):
    class InterruptedLedger(credits.MemoryLedger):
        armed = False

        async def credit(self, *args, **kwargs):
            if not self.armed:
                return await super().credit(*args, **kwargs)
            self.armed = False
            if after_funding:
                await super().credit(*args, **kwargs)
            raise OSError("fixture claim funding unavailable")

        async def fund_claim(self, *args, **kwargs):
            if not self.armed:
                return await super().fund_claim(*args, **kwargs)
            self.armed = False
            if after_funding:
                await super().fund_claim(*args, **kwargs)
            raise OSError("fixture claim funding unavailable")

    async def scenario():
        kv, ledger = MemoryKV(), InterruptedLedger()
        obj = (checkout_obj(mode="payment", subscription=None,
                            metadata={"modelspec_price_id": PACK5}) if pack else checkout_obj())
        assert (await apply(kv, policy, payload("checkout.session.completed", obj,
                                               "evt_funding_recovery"), ledger=ledger)).status == 200
        ledger.armed = True
        with pytest.raises(OSError, match="claim funding"):
            await billing.claim(session_id=SESSION, kv=kv, policy=policy, now=T0,
                                service_commit=COMMIT, ledger=ledger)
        sub_id = "pack:" + SESSION if pack else SUB
        selected = await billing.store.load_subscription(kv, sub_id)
        retried = await billing.claim(session_id=SESSION, kv=kv, policy=policy, now=T0,
                                      service_commit=COMMIT, ledger=ledger)
        assert retried.status == 200
        current = await billing.store.load_subscription(kv, sub_id)
        assert current.key_fingerprint == keys.fingerprint(retried.body["key"])
        if after_funding:
            assert current.key_fingerprint == selected.key_fingerprint
        owner = credits.holder_from_fingerprint(current.key_fingerprint)
        assert (await ledger.balance(owner)).available == (1250 if pack else 4000)
    run(scenario())


@pytest.mark.parametrize("failed_prefix,after_write", [("keyref:", False), ("sub:", True)])
def test_rotation_resume_retains_current_subscription_status(policy, failed_prefix, after_write):
    async def scenario():
        kv, ledger = RotationKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        kv.fail_name = failed_prefix
        kv.fail_after = after_write
        with pytest.raises(OSError, match="rotation write"):
            await billing.rotate(api_key=key, kv=kv, policy=policy, now=T0,
                                 service_commit=COMMIT, ledger=ledger)
        deleted = {"id": SUB, "status": "canceled", "canceled_at": 300}
        assert (await _dated_event(kv, ledger, policy, "customer.subscription.deleted",
                                   deleted, "evt_cancel_rotation", created=300)).status == 200
        rotated = await billing.rotate(api_key=key, kv=kv, policy=policy, now=T0,
                                       service_commit=COMMIT, ledger=ledger)
        assert rotated.status == 200
        sub = await billing.store.load_subscription(kv, SUB)
        assert sub.status == "inactive" and sub.subscription_status == "canceled"
        assert (await keys.lookup(kv, rotated.body["key"])).tier == "free"
        older = invoice_obj(id="in_rotation_old", period_start=100, period_end=200)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", older,
                                   "evt_rotation_old", created=150)).status == 200
        assert (await ledger.balance(_billing_holder(rotated.body["key"]))).monthly == 0
    run(scenario())


@pytest.mark.parametrize("bound", [False, True])
@pytest.mark.parametrize("invoice_first", [False, True])
def test_initial_invoice_allowance_is_shared_with_checkout_and_claim(policy, bound, invoice_first):
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        metadata = {"modelspec_price_id": PRICE}
        key = ""
        if bound:
            key, _ = await keys.issue(kv, tier="paid", owner="fixture", now=T0, policy=policy)
            metadata["modelspec_key_fingerprint"] = keys.fingerprint(key)
        checkout = checkout_obj(invoice="in_initial", metadata=metadata)
        invoice = invoice_obj(id="in_initial", metadata=metadata, billing_reason="subscription_create")
        if invoice_first:
            assert (await _dated_event(kv, ledger, policy, "invoice.paid", invoice,
                                       "evt_initial_invoice")).status == 200
            if bound:
                await _spend_billing_credits(ledger, key, 100)
        assert (await _dated_event(kv, ledger, policy, "checkout.session.completed", checkout,
                                   "evt_initial_checkout")).status == 200
        claimed = await billing.claim(session_id=SESSION, kv=kv, policy=policy, now=T0,
                                      service_commit=COMMIT, ledger=ledger)
        assert claimed.status == 200
        if not bound:
            key = claimed.body["key"]
        if not (invoice_first and bound):
            await _spend_billing_credits(ledger, key, 100)
        if not invoice_first:
            assert (await _dated_event(kv, ledger, policy, "invoice.paid", invoice,
                                       "evt_initial_invoice")).status == 200
        for kind, obj, event_id in [
                ("invoice.paid", invoice, "evt_invoice_replay"),
                ("checkout.session.completed", checkout, "evt_checkout_replay")]:
            assert (await _dated_event(kv, ledger, policy, kind, obj, event_id)).status == 200
            assert (await ledger.balance(_billing_holder(key))).monthly == 3900
        assert (await billing.claim(session_id=SESSION, kv=kv, policy=policy, now=T0,
                                    service_commit=COMMIT, ledger=ledger)).status == 410
        renewal = invoice_obj(id="in_later", period_start=300, period_end=400)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", renewal,
                                   "evt_later", created=300)).status == 200
        assert (await ledger.balance(_billing_holder(key))).monthly == 4000
    run(scenario())


@pytest.mark.parametrize("kind", ["checkout.session.completed", "checkout.session.async_payment_succeeded"])
def test_paid_checkout_recovers_its_initial_invoice(policy, kind):
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        failed = invoice_obj(id="in_initial", paid=False, period_start=100, period_end=200)
        assert (await _dated_event(kv, ledger, policy, "invoice.payment_failed", failed,
                                   "evt_initial_failed", created=100)).status == 200
        assert (await _dated_event(kv, ledger, policy, kind,
                                   checkout_obj(invoice="in_initial"),
                                   "evt_initial_recovered", created=200)).status == 200
        claimed = await billing.claim(session_id=SESSION, kv=kv, policy=policy, now=T0,
                                      service_commit=COMMIT, ledger=ledger)
        assert claimed.status == 200 and claimed.body["tier"] == "paid"
        key = claimed.body["key"]
        await _spend_billing_credits(ledger, key, 100)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", failed,
                                   "evt_invoice_confirmed", created=210)).status == 200
        assert (await ledger.balance(_billing_holder(key))).monthly == 3900
    run(scenario())


@pytest.mark.parametrize("operation", ["transfer", "completion"])
@pytest.mark.parametrize("after_write", [False, True])
def test_rotation_recovers_ledger_write_interruptions(policy, operation, after_write):
    class InterruptedLedger(credits.MemoryLedger):
        armed = True

        async def transfer(self, src, dst):
            if operation != "transfer" or not self.armed:
                return await super().transfer(src, dst)
            self.armed = False
            if after_write:
                await super().transfer(src, dst)
            raise OSError("fixture ledger write unavailable")

        async def save_rotation(self, holder, data):
            if operation != "completion" or data["stage"] != "complete" or not self.armed:
                return await super().save_rotation(holder, data)
            self.armed = False
            if after_write:
                await super().save_rotation(holder, data)
            raise OSError("fixture ledger write unavailable")

    async def scenario():
        kv, ledger = MemoryKV(), InterruptedLedger()
        key, _ = await keys.issue(kv, tier="paid", owner="fixture", now=T0, policy=policy)
        await ledger.set_monthly(_billing_holder(key), 100, "in_write_retry", "Solo")
        if operation == "completion" and after_write:
            result = await billing.rotate(api_key=key, kv=kv, policy=policy, now=T0,
                                          service_commit=COMMIT, ledger=ledger)
        else:
            with pytest.raises(OSError, match="ledger write"):
                await billing.rotate(api_key=key, kv=kv, policy=policy, now=T0,
                                     service_commit=COMMIT, ledger=ledger)
            result = await billing.rotate(api_key=key, kv=kv, policy=policy, now=T0,
                                          service_commit=COMMIT, ledger=ledger)
        assert result.status == 200
        assert (await ledger.balance(_billing_holder(result.body["key"]))).available == 100
        assert not (await keys.lookup(kv, key)).active
        assert (await billing.rotate(api_key=key, kv=kv, policy=policy, now=T0,
                                    service_commit=COMMIT, ledger=ledger)).status == 403
    run(scenario())


@pytest.mark.parametrize("canceled", [False, True])
def test_prepared_claim_respects_current_billing_state(policy, canceled):
    async def scenario():
        kv, ledger = RotationKV(), credits.MemoryLedger()
        assert (await apply(kv, policy, payload("checkout.session.completed",
            checkout_obj(invoice="in_initial"), "evt_prepared_checkout"), ledger=ledger)).status == 200
        kv.fail_name = "keyref:"
        with pytest.raises(OSError, match="rotation write"):
            await billing.claim(session_id=SESSION, kv=kv, policy=policy, now=T0,
                                service_commit=COMMIT, ledger=ledger)
        if canceled:
            event = payload("customer.subscription.deleted", {"id": SUB, "status": "canceled"},
                            "evt_prepared_canceled")
        else:
            event = payload("invoice.paid", invoice_obj(id="in_initial"), "evt_prepared_invoice")
        assert (await apply(kv, policy, event, ledger=ledger)).status == 200
        retried = await billing.claim(session_id=SESSION, kv=kv, policy=policy, now=T0,
                                      service_commit=COMMIT, ledger=ledger)
        assert retried.status == 200
        key = retried.body["key"]
        assert (await ledger.balance(_billing_holder(key))).monthly == (0 if canceled else 4000)
        sub = await billing.store.load_subscription(kv, SUB)
        assert sub is not None
        if canceled:
            assert (await keys.lookup(kv, key)).tier == policy.billing.downgrade_tier
            assert sub.tier == policy.billing.downgrade_tier
            assert sub.status == "inactive"
        else:
            assert (await keys.lookup(kv, key)).tier == "paid"
            assert sub.tier == "paid"
            assert sub.status == "active"
    run(scenario())


def test_a_failed_period_write_does_not_grant_the_allowance_twice(policy):
    class InterruptedChronologyKV(MemoryKV):
        armed = False

        async def put(self, name, value, **kwargs):
            if self.armed and name.startswith("sub:") and json.loads(value).get("invoice_id") == "in_current":
                self.armed = False
                raise OSError("fixture chronology write unavailable")
            await super().put(name, value, **kwargs)

    async def scenario():
        kv, ledger = InterruptedChronologyKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        await _spend_billing_credits(ledger, key, 100)
        current = invoice_obj(id="in_current", period_start=300, period_end=400)
        kv.armed = True
        with pytest.raises(OSError, match="chronology write"):
            await _dated_event(kv, ledger, policy, "invoice.paid", current,
                               "evt_current", created=300)
        # The allowance lands before the period write. The retry is a replay.
        assert (await ledger.balance(_billing_holder(key))).monthly == 4000
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", current,
                                   "evt_current", created=300)).status == 200
        await _spend_billing_credits(ledger, key, 100)
        older = invoice_obj(id="in_older", period_start=100, period_end=200)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", older,
                                   "evt_older", created=100)).status == 200
        assert (await ledger.balance(_billing_holder(key))).monthly == 3900
    run(scenario())


SUB2 = "sub_second_fixture"
SES2 = "cs_second_fixture"


async def _cancel_subscription(kv, ledger, policy, *, at: int = 350, event_id: str = "evt_cancel_sub"):
    deleted = {"id": SUB, "status": "canceled", "customer": CUS, "canceled_at": at}
    return await _dated_event(kv, ledger, policy, "customer.subscription.deleted",
                              deleted, event_id, created=at)


def test_resubscribe_checkout_on_the_same_key_grants(policy):
    """A no-period checkout for a different subscription is not stale."""
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy, bound=True)
        fingerprint = keys.fingerprint(key)
        paid = invoice_obj(id="in_a1", period_start=300, period_end=400)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", paid,
                                   "evt_paid_a", created=300)).status == 200
        assert (await _cancel_subscription(kv, ledger, policy)).status == 200
        assert (await keys.lookup(kv, key)).tier == "free"
        meta = {"modelspec_price_id": PRICE, "modelspec_key_fingerprint": fingerprint}
        checkout = checkout_obj(id=SES2, subscription=SUB2, invoice="in_b0", metadata=meta)
        outcome = await _dated_event(kv, ledger, policy, "checkout.session.completed",
                                     checkout, "evt_checkout_b", created=1000)
        assert outcome.status == 200
        assert outcome.body["action"] == "credited"
        assert (await keys.lookup(kv, key)).tier == "paid"
        holder = _billing_holder(key)
        assert (await ledger.balance(holder)).monthly == 4000
        assert (await ledger.entitlement_view(holder))["entitled"] is True
        assert ledger.state.accounts[holder].canceled_at == 0
    run(scenario())


def test_resubscribe_invoice_then_checkout_grants_the_pending_allowance(policy):
    """Linking a key applies the other subscription's pending allowance."""
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy, bound=True)
        fingerprint = keys.fingerprint(key)
        paid = invoice_obj(id="in_a1", period_start=300, period_end=400)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", paid,
                                   "evt_paid_a", created=300)).status == 200
        assert (await _cancel_subscription(kv, ledger, policy)).status == 200
        invoice = invoice_obj(id="in_b0", subscription=SUB2, period_start=1000, period_end=1100)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", invoice,
                                   "evt_paid_b", created=1000)).status == 200
        meta = {"modelspec_price_id": PRICE, "modelspec_key_fingerprint": fingerprint}
        checkout = checkout_obj(id=SES2, subscription=SUB2, invoice="in_b0", metadata=meta)
        outcome = await _dated_event(kv, ledger, policy, "checkout.session.completed",
                                     checkout, "evt_link_b", created=1000)
        assert outcome.status == 200
        holder = _billing_holder(key)
        assert (await keys.lookup(kv, key)).tier == "paid"
        assert (await ledger.balance(holder)).monthly == 4000
        assert (await ledger.entitlement_view(holder))["entitled"] is True
        stored = await billing.store.load_subscription(kv, SUB2)
        assert stored is not None
        assert stored.pending_monthly == 0
        assert stored.key_fingerprint == fingerprint
    run(scenario())


def test_no_period_grant_for_the_cancelled_subscription_stays_stale(policy):
    """A no-period grant for the cancelled subscription does not reopen it."""
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        assert (await _cancel_subscription(kv, ledger, policy, at=300)).status == 200
        bare = invoice_obj(id="in_bare", created=400)
        outcome = await _dated_event(kv, ledger, policy, "invoice.paid", bare,
                                     "evt_bare_same", created=400)
        assert outcome.status == 200
        assert outcome.body["action"] == "ignored"
        assert (await keys.lookup(kv, key)).tier == "free"
        assert (await ledger.balance(_billing_holder(key))).monthly == 0
    run(scenario())


def test_same_subscription_period_grant_follows_the_cancellation(policy):
    """A period grant for the cancelled subscription keeps the period-start rule."""
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        paid = invoice_obj(id="in_p", period_start=300, period_end=400)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", paid,
                                   "evt_p", created=300)).status == 200
        assert (await _cancel_subscription(kv, ledger, policy, at=350)).status == 200
        late = invoice_obj(id="in_late", period_start=300, period_end=400)
        ignored = await _dated_event(kv, ledger, policy, "invoice.paid", late,
                                     "evt_late", created=360)
        assert ignored.body["action"] == "ignored"
        assert (await ledger.balance(_billing_holder(key))).monthly == 0
        renewed = invoice_obj(id="in_next", period_start=360, period_end=500)
        applied = await _dated_event(kv, ledger, policy, "invoice.paid", renewed,
                                     "evt_next", created=360)
        assert applied.body["action"] == "credited"
        assert (await keys.lookup(kv, key)).tier == "paid"
        assert (await ledger.balance(_billing_holder(key))).monthly == 4000
    run(scenario())


def test_unknown_cancellation_subscription_rejects_a_no_period_grant(policy):
    """An unknown cancellation id keeps the no-period grant stale, and the key stays put."""
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy, bound=True)
        fingerprint = keys.fingerprint(key)
        assert (await _cancel_subscription(kv, ledger, policy, at=300)).status == 200
        holder = _billing_holder(key)
        account = ledger.state.accounts[holder]
        if hasattr(account, "canceled_subscription_id"):
            account.canceled_subscription_id = ""
        meta = {"modelspec_price_id": PRICE, "modelspec_key_fingerprint": fingerprint}
        checkout = checkout_obj(id=SES2, subscription=SUB2, invoice="in_unknown", metadata=meta)
        outcome = await _dated_event(kv, ledger, policy, "checkout.session.completed",
                                     checkout, "evt_unknown_checkout", created=1000)
        assert outcome.status == 200
        assert outcome.body["action"] == "ignored"
        assert (await keys.lookup(kv, key)).tier == "free"
        assert (await ledger.balance(holder)).monthly == 0
        assert (await ledger.entitlement_view(holder))["entitled"] is False
    run(scenario())


def _row(subscription_id: str, *, tier: str, pending: int, invoice_id: str,
         pending_invoice_id: str) -> billing.store.SubscriptionRecord:
    return billing.store.SubscriptionRecord(
        subscription_id=subscription_id, customer_id=CUS, price_id=PRICE,
        tier=tier, status="active", key_fingerprint="", key_id="",
        created_at="2026-09-17T14:30:00Z", pending_monthly=pending,
        pending_invoice_id=pending_invoice_id, plan_name="Solo",
        plan_credits=pending, invoice_id=invoice_id, invoice_paid=True)


def test_stale_checkout_link_leaves_the_row_and_the_allowance(policy):
    """A stale link is the rejected-event answer and changes nothing on the row."""
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key, _record = await keys.issue(
            kv, tier=policy.billing.downgrade_tier, owner="fixture", now=T0, policy=policy)
        fingerprint = keys.fingerprint(key)
        holder = _billing_holder(key)
        assert (await ledger.clear_monthly(holder, watermark=300, subscription_id="")).reason == "cleared"
        pending = 4000
        await billing.store._write_sub(kv, _row(
            SUB2, tier="paid", pending=pending, invoice_id="in_row_stale",
            pending_invoice_id="in_pending_stale"))
        meta = {"modelspec_price_id": PRICE, "modelspec_key_fingerprint": fingerprint}
        checkout = checkout_obj(
            id="cs_stale_link", subscription=SUB2, invoice="in_other_stale", metadata=meta)
        outcome = await _dated_event(
            kv, ledger, policy, "checkout.session.completed", checkout,
            "evt_stale_link", created=1000)
        assert outcome.status == 200
        assert outcome.body["action"] == "ignored"
        assert (await keys.lookup(kv, key)).tier == policy.billing.downgrade_tier
        stored = await billing.store.load_subscription(kv, SUB2)
        assert stored is not None
        assert stored.key_fingerprint == ""
        assert stored.pending_monthly == pending
        assert (await ledger.balance(holder)).monthly == 0
    run(scenario())


def test_unbound_checkout_link_keeps_the_pending_allowance(policy):
    """A link whose grant is neither accepted nor stale keeps the pending allowance."""
    async def scenario():
        kv, ledger = MemoryKV(), credits.UnboundLedger()
        key, _record = await keys.issue(
            kv, tier=policy.billing.downgrade_tier, owner="fixture", now=T0, policy=policy)
        fingerprint = keys.fingerprint(key)
        pending = 4000
        await billing.store._write_sub(kv, _row(
            SUB2, tier="paid", pending=pending, invoice_id="in_row_unbound",
            pending_invoice_id="in_pending_unbound"))
        meta = {"modelspec_price_id": PRICE, "modelspec_key_fingerprint": fingerprint}
        checkout = checkout_obj(
            id="cs_unbound_link", subscription=SUB2, invoice="in_other_unbound", metadata=meta)
        outcome = await _dated_event(
            kv, ledger, policy, "checkout.session.completed", checkout,
            "evt_unbound_link", created=1000)
        assert outcome.status == 200
        stored = await billing.store.load_subscription(kv, SUB2)
        assert stored is not None
        assert stored.pending_monthly == pending
        assert stored.key_fingerprint == fingerprint
        assert (await keys.lookup(kv, key)) is not None
    run(scenario())


def test_checkout_link_and_replay_copy_the_ledger_tier(policy):
    """Link copies the paid tier. A replay after cancellation copies the downgrade."""
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key, _record = await keys.issue(
            kv, tier=policy.billing.downgrade_tier, owner="fixture", now=T0, policy=policy)
        fingerprint = keys.fingerprint(key)
        await billing.store._write_sub(kv, _row(
            SUB2, tier=policy.billing.downgrade_tier, pending=4000,
            invoice_id="in_row_link", pending_invoice_id="in_pending_link"))
        meta = {"modelspec_price_id": PRICE, "modelspec_key_fingerprint": fingerprint}
        checkout = checkout_obj(
            id="cs_link_copy", subscription=SUB2, invoice="in_link_other", metadata=meta)
        linked = await _dated_event(
            kv, ledger, policy, "checkout.session.completed", checkout,
            "evt_link_copy", created=1000)
        assert linked.status == 200
        assert (await keys.lookup(kv, key)).tier == "paid"
        stored = await billing.store.load_subscription(kv, SUB2)
        assert stored is not None and stored.key_fingerprint == fingerprint

        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key, _record = await keys.issue(
            kv, tier="paid", owner="fixture", now=T0, policy=policy)
        fingerprint = keys.fingerprint(key)
        meta = {"modelspec_price_id": PRICE, "modelspec_key_fingerprint": fingerprint}
        first = checkout_obj(id="cs_replay_copy", metadata=meta)
        assert (await _dated_event(
            kv, ledger, policy, "checkout.session.completed", first,
            "evt_replay_first", created=100)).status == 200
        assert (await keys.lookup(kv, key)).tier == "paid"
        holder = _billing_holder(key)
        assert (await ledger.clear_monthly(
            holder, watermark=300, subscription_id=SUB)).reason == "cleared"
        assert (await keys.lookup(kv, key)).tier == "paid"
        replay = await _dated_event(
            kv, ledger, policy, "checkout.session.completed", first,
            "evt_replay_second", created=400)
        assert replay.status == 200
        assert (await keys.lookup(kv, key)).tier == policy.billing.downgrade_tier
    run(scenario())


def test_replayed_link_grant_copies_the_tier(policy):
    """A link whose grant is a replay copies the tier the same way a first grant does."""
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key, _record = await keys.issue(
            kv, tier=policy.billing.downgrade_tier, owner="fixture", now=T0, policy=policy)
        fingerprint = keys.fingerprint(key)
        holder = _billing_holder(key)
        primed = await ledger.set_monthly(
            holder, 4000, "in_replay_link", "Solo", CUS, subscription_id=SUB2)
        assert primed.credited
        await billing.store._write_sub(kv, _row(
            SUB2, tier=policy.billing.downgrade_tier, pending=4000,
            invoice_id="in_row_replay", pending_invoice_id="in_replay_link"))
        assert (await keys.lookup(kv, key)).tier == policy.billing.downgrade_tier
        meta = {"modelspec_price_id": PRICE, "modelspec_key_fingerprint": fingerprint}
        checkout = checkout_obj(
            id="cs_replay_link", subscription=SUB2, invoice="in_other_replay", metadata=meta)
        linked = await _dated_event(
            kv, ledger, policy, "checkout.session.completed", checkout,
            "evt_replay_link", created=1000)
        assert linked.status == 200
        assert linked.body["action"] == "already_entitled"
        assert (await keys.lookup(kv, key)).tier == "paid"
        stored = await billing.store.load_subscription(kv, SUB2)
        assert stored is not None and stored.tier == "paid"
        assert stored.key_fingerprint == fingerprint
        assert stored.pending_monthly == 0
    run(scenario())


def test_replayed_friends_link_writes_the_mapping_tier(policy):
    """A replayed link writes the event's mapping tier."""

    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key, _record = await keys.issue(
            kv, tier=policy.billing.downgrade_tier, owner="fixture", now=T0, policy=policy)
        fingerprint = keys.fingerprint(key)
        holder = _billing_holder(key)
        primed = await ledger.set_monthly(
            holder, 4000, "in_replay_friends", "Solo", CUS, subscription_id=SUB2)
        assert primed.credited
        await billing.store._write_sub(kv, _row(
            SUB2, tier=policy.billing.downgrade_tier, pending=4000,
            invoice_id="in_row_friends", pending_invoice_id="in_replay_friends"))
        promo = {
            "id": "promo_fixture",
            "code": "FRIENDS-FIXTURE",
            "promotion": {"type": "coupon", "coupon": {
                "id": "coupon_fixture", "percent_off": 100, "duration": "forever",
            }},
        }
        meta = {"modelspec_price_id": PRICE, "modelspec_key_fingerprint": fingerprint}
        checkout = checkout_obj(
            id="cs_replay_friends", subscription=SUB2, invoice="in_other_friends",
            metadata=meta, discounts=[{"promotion_code": promo}])
        linked = await _dated_event(
            kv, ledger, policy, "checkout.session.completed", checkout,
            "evt_replay_friends", created=1000)
        assert linked.status == 200
        assert (await keys.lookup(kv, key)).tier == "friends"
        stored = await billing.store.load_subscription(kv, SUB2)
        assert stored is not None and stored.tier == "friends"
        assert stored.pending_monthly == 0
    run(scenario())


def _unclaimed_downgrade_event(kind: str) -> tuple[str, dict]:
    if kind == "invoice.payment_failed":
        return kind, invoice_obj(id="in_unclaimed_fail", paid=False, period_start=100, period_end=200)
    status = "canceled"
    obj = {"id": SUB, "object": "subscription", "status": status, "customer": CUS,
           "canceled_at": 300}
    return kind, obj


@pytest.mark.parametrize("kind", [
    "customer.subscription.deleted",
    "customer.subscription.updated",
    "invoice.payment_failed",
])
def test_unclaimed_subscription_downgrade_reaches_the_claim(policy, kind):
    """A cancellation or failed payment with no key still downgrades the row."""
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        assert (await _dated_event(
            kv, ledger, policy, "checkout.session.completed", checkout_obj(),
            "evt_unclaimed_checkout", created=100)).status == 200
        event_kind, obj = _unclaimed_downgrade_event(kind)
        outcome = await _dated_event(kv, ledger, policy, event_kind, obj,
                                     "evt_unclaimed_" + kind, created=300)
        assert outcome.status == 200
        assert outcome.body["action"] == "downgraded"
        sub = await billing.store.load_subscription(kv, SUB)
        assert sub is not None
        assert sub.tier == policy.billing.downgrade_tier
        assert sub.status == "inactive"
        assert sub.key_fingerprint == ""
        claimed = await billing.claim(session_id=SESSION, kv=kv, policy=policy, now=T0,
                                      service_commit=COMMIT, ledger=ledger)
        assert claimed.status == 200
        assert claimed.body["tier"] == policy.billing.downgrade_tier
        key = claimed.body["key"]
        assert (await keys.lookup(kv, key)).tier == policy.billing.downgrade_tier
        assert (await ledger.balance(_billing_holder(key))).monthly == 0
        stored = await billing.store.load_subscription(kv, SUB)
        assert stored.tier == policy.billing.downgrade_tier
        assert stored.status == "inactive"
        assert stored.key_fingerprint == keys.fingerprint(key)
    run(scenario())


class _RecoverySql:
    def __init__(self) -> None:
        self.table: dict[str, str] = {}

    def exec(self, query: str, *params: Any):
        class Cursor:
            def __init__(self, row: Any) -> None:
                self._row = row

            def one(self) -> Any:
                if self._row is None:
                    raise RuntimeError("no row")
                return self._row

        if query.startswith("INSERT"):
            self.table[params[0]] = params[1]
            return Cursor(None)
        if query.startswith("SELECT"):
            value = self.table.get(params[0])
            return Cursor(None if value is None else {"v": value})
        return Cursor(None)


class _RecoveryCtx:
    def __init__(self) -> None:
        self.storage = type("Storage", (), {"sql": _RecoverySql()})()
        self._gate = asyncio.Lock()

    async def blockConcurrencyWhile(self, callback):
        async with self._gate:
            return await callback()


def _recovery_ledger(kind: str, kv: MemoryKV):
    if kind == "memory":
        return credits.MemoryLedger()
    import credits_do
    from types import SimpleNamespace

    obj = credits_do.CreditsObject(_RecoveryCtx(), env=SimpleNamespace(ACCESS=kv))
    namespace = SimpleNamespace(idFromName=lambda name: name, get=lambda _id: obj)
    return credits.DurableLedger(namespace)


async def _claim_unclaimed(kv, ledger, policy):
    return await billing.claim(session_id=SESSION, kv=kv, policy=policy, now=T0,
                               service_commit=COMMIT, ledger=ledger)


@pytest.mark.parametrize("kind", ["memory", "durable"])
def test_recovering_invoice_after_a_failed_payment_restores_an_unclaimed_row(policy, kind):
    """An unclaimed row downgraded by a failed payment is paid again after invoice.paid."""
    async def scenario():
        kv = MemoryKV()
        ledger = _recovery_ledger(kind, kv)
        assert (await _dated_event(
            kv, ledger, policy, "checkout.session.completed", checkout_obj(),
            "evt_recover_fail_checkout", created=100)).status == 200
        failed = invoice_obj(id="in_n", paid=False, period_start=300, period_end=400)
        outcome = await _dated_event(
            kv, ledger, policy, "invoice.payment_failed", failed,
            "evt_recover_fail", created=300)
        assert outcome.body["action"] == "downgraded"
        paid = invoice_obj(id="in_n", period_start=300, period_end=400)
        restored = await _dated_event(
            kv, ledger, policy, "invoice.paid", paid, "evt_recover_paid", created=310)
        assert restored.status == 200
        claimed = await _claim_unclaimed(kv, ledger, policy)
        assert claimed.status == 200, claimed.body
        assert claimed.body["tier"] == "paid"
        assert (await ledger.balance(_billing_holder(claimed.body["key"]))).monthly == 4000
        row = await billing.store.load_subscription(kv, SUB)
        assert row.tier == "paid" and row.status == "active"
    run(scenario())


@pytest.mark.parametrize("kind", ["memory", "durable"])
def test_recovering_invoice_after_deletion_restores_an_unclaimed_row(policy, kind):
    """An unclaimed row downgraded by deletion is paid again by a later period."""
    async def scenario():
        kv = MemoryKV()
        ledger = _recovery_ledger(kind, kv)
        assert (await _dated_event(
            kv, ledger, policy, "checkout.session.completed", checkout_obj(),
            "evt_recover_del_checkout", created=100)).status == 200
        deleted = {"id": SUB, "status": "canceled", "customer": CUS, "canceled_at": 300}
        outcome = await _dated_event(
            kv, ledger, policy, "customer.subscription.deleted", deleted,
            "evt_recover_del", created=300)
        assert outcome.body["action"] == "downgraded"
        paid = invoice_obj(id="in_later", period_start=400, period_end=500)
        restored = await _dated_event(
            kv, ledger, policy, "invoice.paid", paid, "evt_recover_later", created=400)
        assert restored.status == 200
        claimed = await _claim_unclaimed(kv, ledger, policy)
        assert claimed.status == 200, claimed.body
        assert claimed.body["tier"] == "paid"
        assert (await ledger.balance(_billing_holder(claimed.body["key"]))).monthly == 4000
        row = await billing.store.load_subscription(kv, SUB)
        assert row.tier == "paid" and row.status == "active"
    run(scenario())


class _FailKeyTierPut(MemoryKV):
    """Fail the next key-record put. The allowance write has already landed."""

    armed = False

    async def put(self, name, value, **kwargs):
        if self.armed and name.startswith("key:"):
            self.armed = False
            raise OSError("fixture key tier write unavailable")
        await super().put(name, value, **kwargs)


def test_redelivered_invoice_repairs_the_key_tier(policy):
    """The first redelivery of a paid invoice copies the granted tier onto the key."""
    async def scenario():
        kv, ledger = _FailKeyTierPut(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        failed = invoice_obj(id="in_recover", paid=False, period_start=300, period_end=400)
        assert (await _dated_event(kv, ledger, policy, "invoice.payment_failed", failed,
                                   "evt_fail_tier", created=300)).status == 200
        assert (await keys.lookup(kv, key)).tier == "free"
        paid = invoice_obj(id="in_recover", period_start=300, period_end=400)
        kv.armed = True
        with pytest.raises(OSError, match="key tier write"):
            await _dated_event(kv, ledger, policy, "invoice.paid", paid,
                               "evt_pay_tier", created=310)
        holder = _billing_holder(key)
        assert (await keys.lookup(kv, key)).tier == "free"
        assert (await ledger.balance(holder)).monthly == 4000
        assert (await ledger.entitlement_view(holder))["entitled"] is True
        repaired = await _dated_event(kv, ledger, policy, "invoice.paid", paid,
                                     "evt_pay_tier", created=310)
        assert repaired.status == 200
        assert (await keys.lookup(kv, key)).tier == "paid"
        assert (await ledger.balance(holder)).monthly == 4000
        sub = await billing.store.load_subscription(kv, SUB)
        assert sub.tier == "paid" and sub.status == "active"
    run(scenario())


def test_first_invoice_for_a_new_subscription_repairs_the_key_tier(policy):
    """A redelivered first invoice for a bound free key copies the granted tier."""
    async def scenario():
        kv, ledger = _FailKeyTierPut(), credits.MemoryLedger()
        key, _ = await keys.issue(kv, tier="free", owner="fixture", now=T0, policy=policy)
        meta = {"modelspec_price_id": PRICE,
                "modelspec_key_fingerprint": keys.fingerprint(key)}
        paid = invoice_obj(id="in_first", metadata=meta, period_start=100, period_end=200)
        kv.armed = True
        with pytest.raises(OSError, match="key tier write"):
            await _dated_event(kv, ledger, policy, "invoice.paid", paid,
                               "evt_first_tier", created=100)
        holder = _billing_holder(key)
        assert (await keys.lookup(kv, key)).tier == "free"
        assert (await ledger.balance(holder)).monthly == 4000
        repaired = await _dated_event(kv, ledger, policy, "invoice.paid", paid,
                                     "evt_first_tier", created=100)
        assert repaired.status == 200
        assert (await keys.lookup(kv, key)).tier == "paid"
        assert (await ledger.balance(holder)).monthly == 4000
        sub = await billing.store.load_subscription(kv, SUB)
        assert sub.tier == "paid" and sub.status == "active"
    run(scenario())


def test_replayed_invoice_keeps_a_pre_round_account_on_the_paid_tier(policy):
    """An account stored before the entitled flag stays paid when the invoice is replayed."""
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        holder = _billing_holder(key)
        raw = ledger.state.accounts[holder].to_json()
        raw.pop("monthly_entitled", None)
        ledger.state.accounts[holder] = credits._Account.from_json(raw)
        replayed = invoice_obj(id="in_initial")
        outcome = await _dated_event(kv, ledger, policy, "invoice.paid", replayed,
                                     "evt_pre_round_replay", created=200)
        assert outcome.status == 200
        assert (await keys.lookup(kv, key)).tier == "paid"
        assert (await ledger.balance(holder)).monthly == 4000
        assert (await ledger.entitlement_view(holder))["entitled"] is True
    run(scenario())


def test_entitlement_view_derives_an_account_without_the_flag():
    holder = "holder-old"
    ledger = credits.MemoryLedger(credits.LedgerState.from_json({
        "accounts": {
            holder: {"monthly": 4000, "invoice_period_watermark": 400},
            "spent": {"monthly": 0, "invoice_period_watermark": 400},
            "cancelled": {
                "monthly": 0, "invoice_period_watermark": 400, "canceled_at": 50,
            },
            "empty": {"monthly": 0},
            "closed": {"monthly": 4000, "monthly_entitled": False},
        },
    }))
    assert run(ledger.entitlement_view(holder))["entitled"] is True
    assert run(ledger.entitlement_view("spent"))["entitled"] is True
    assert run(ledger.entitlement_view("cancelled"))["entitled"] is False
    assert run(ledger.entitlement_view("empty"))["entitled"] is False
    assert run(ledger.entitlement_view("closed"))["entitled"] is False


def test_a_rejected_invoice_period_does_not_block_the_next_renewal(policy):
    """A grant the ledger rejects does not store its period or move the row."""
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        paid = invoice_obj(id="in_p", period_start=300, period_end=400)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", paid,
                                   "evt_paid_period", created=300)).status == 200
        deleted = {"id": SUB, "status": "canceled", "customer": CUS, "canceled_at": 350}
        assert (await _dated_event(kv, ledger, policy, "customer.subscription.deleted",
                                   deleted, "evt_cancel_period", created=350)).status == 200
        active = {"id": SUB, "status": "active", "customer": CUS,
                  "items": {"data": [{"price": {"id": PRICE}}]}}
        assert (await _dated_event(kv, ledger, policy, "customer.subscription.updated",
                                   active, "evt_restore_period", created=400)).status == 200
        before = await billing.store.load_subscription(kv, SUB)
        overlap = invoice_obj(id="in_overlap", period_start=340, period_end=600)
        rejected = await _dated_event(kv, ledger, policy, "invoice.paid", overlap,
                                     "evt_overlap", created=410)
        assert rejected.status == 200
        assert rejected.body["action"] == "ignored"
        after = await billing.store.load_subscription(kv, SUB)
        assert (after.invoice_period_start, after.invoice_period_end) == (300, 400)
        assert after.tier == before.tier
        assert after.status == before.status
        assert after.key_fingerprint == before.key_fingerprint
        later = invoice_obj(id="in_next", period_start=360, period_end=500)
        applied = await _dated_event(kv, ledger, policy, "invoice.paid", later,
                                    "evt_next_period", created=420)
        assert applied.status == 200
        assert applied.body["action"] == "credited"
        assert (await keys.lookup(kv, key)).tier == "paid"
        assert (await ledger.balance(_billing_holder(key))).monthly == 4000
        stored = await billing.store.load_subscription(kv, SUB)
        assert stored.tier == "paid" and stored.status == "active"
        assert (stored.invoice_period_start, stored.invoice_period_end) == (360, 500)
    run(scenario())


def test_rotation_copies_the_ledger_tier(policy):
    """The new key takes the tier the ledger implies, not the tier stored on the row."""
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        paid = invoice_obj(id="in_rot", period_start=300, period_end=400)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", paid,
                                   "evt_rot_paid", created=300)).status == 200
        sub = await billing.store.load_subscription(kv, SUB)
        await billing.store._write_sub(kv, replace(sub, tier="free", status="inactive"))
        rotated = await billing.rotate(api_key=key, kv=kv, policy=policy, now=T0,
                                       service_commit=COMMIT, ledger=ledger)
        assert rotated.status == 200
        assert (await keys.lookup(kv, rotated.body["key"])).tier == "paid"

        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        holder = _billing_holder(key)
        account = ledger.state.accounts[holder]
        account.monthly = 0
        account.monthly_entitled = False
        rotated = await billing.rotate(api_key=key, kv=kv, policy=policy, now=T0,
                                       service_commit=COMMIT, ledger=ledger)
        assert rotated.status == 200
        assert (await keys.lookup(kv, rotated.body["key"])).tier == policy.billing.downgrade_tier

        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        holder = _billing_holder(key)
        account = ledger.state.accounts[holder]
        account.monthly = 0
        account.monthly_entitled = False
        account.entitlement_generation = 0
        sub = await billing.store.load_subscription(kv, SUB)
        await billing.store._write_sub(kv, replace(sub, tier="paid", status="active"))
        rotated = await billing.rotate(api_key=key, kv=kv, policy=policy, now=T0,
                                       service_commit=COMMIT, ledger=ledger)
        assert rotated.status == 200
        assert (await keys.lookup(kv, rotated.body["key"])).tier == "paid"
    run(scenario())


def test_replayed_invoice_leaves_an_unrecorded_spent_account_on_the_paid_tier(policy):
    """A replay does not downgrade an account the ledger has not recorded."""
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy)
        holder = _billing_holder(key)
        paid = invoice_obj(id="in_spent", period_start=100, period_end=200)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", paid,
                                   "evt_spent_paid", created=100)).status == 200
        account = ledger.state.accounts[holder]
        account.monthly = 0
        account.monthly_entitled = None
        account.entitlement_generation = 0
        account.canceled_at = 0
        account.canceled_subscription_id = ""
        account.invoice_period_watermark = 0
        replay = await _dated_event(
            kv, ledger, policy, "invoice.paid", paid, "evt_spent_replay", created=500)
        assert replay.status == 200
        assert (await keys.lookup(kv, key)).tier == "paid"
        stored = await billing.store.load_subscription(kv, SUB)
        assert stored is not None
        assert stored.tier == "paid" and stored.status == "active"
    run(scenario())


def test_rejected_first_invoice_for_a_second_subscription_writes_no_row(policy):
    """A stale first invoice for a subscription with no row leaves no row."""
    async def scenario():
        kv, ledger = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, ledger, policy, bound=True)
        fingerprint = keys.fingerprint(key)
        paid = invoice_obj(id="in_bound", period_start=300, period_end=400)
        assert (await _dated_event(kv, ledger, policy, "invoice.paid", paid,
                                   "evt_bound_paid", created=300)).status == 200
        older = invoice_obj(
            id="in_older_second", subscription=SUB2, period_start=100, period_end=200,
            subscription_details={"metadata": {"modelspec_key_fingerprint": fingerprint}})
        outcome = await _dated_event(
            kv, ledger, policy, "invoice.paid", older, "evt_older_second", created=100)
        assert outcome.status == 200
        assert outcome.body["action"] == "ignored"
        assert await billing.store.load_subscription(kv, SUB2) is None
        assert (await keys.lookup(kv, key)).tier == "paid"
    run(scenario())


def test_first_invoice_for_an_unknown_fingerprint_writes_no_allowance(policy):
    """A first paid invoice for a fingerprint with no key writes no allowance."""

    class Recording(credits.MemoryLedger):
        def __init__(self):
            super().__init__()
            self.monthly_calls = []

        async def set_monthly(self, holder, units, invoice_id, plan="", customer_id="",
                              period_end=0, period_start=0, subscription_id=""):
            self.monthly_calls.append(holder)
            return await super().set_monthly(
                holder, units, invoice_id, plan, customer_id,
                period_end=period_end, period_start=period_start,
                subscription_id=subscription_id)

    async def scenario():
        kv, ledger = MemoryKV(), Recording()
        fingerprint = keys.fingerprint("never-issued-key")
        holder = credits.holder_from_fingerprint(fingerprint)
        assert await keys.lookup_fingerprint(kv, fingerprint) is None
        paid = invoice_obj(
            id="in_unknown_fp", period_start=100, period_end=200,
            metadata={"modelspec_key_fingerprint": fingerprint})
        outcome = await _dated_event(
            kv, ledger, policy, "invoice.paid", paid, "evt_unknown_fp", created=100)
        assert outcome.status == 200
        assert holder not in ledger.state.accounts
        assert ledger.monthly_calls == []
        assert all(account.monthly == 0 for account in ledger.state.accounts.values())

    run(scenario())


class _TurnLedger:
    """In-memory ledger wrapper for the schedule test."""

    def __init__(self, inner: credits.MemoryLedger, pauses: int) -> None:
        self._inner = inner
        self._pauses = pauses

    def __getattr__(self, name: str) -> Any:
        if name == "_billing_lock":
            raise AttributeError(name)
        attr = getattr(self._inner, name)
        if not inspect.iscoroutinefunction(attr):
            return attr
        pauses, inner = self._pauses, self._inner

        async def call(*args: Any, **kwargs: Any) -> Any:
            for _ in range(pauses):
                await asyncio.sleep(0)
            if name in {"rotate_key", "claim_purchase"}:
                out = await attr(*args, **kwargs)
            else:
                async with inner._billing_lock:
                    out = await attr(*args, **kwargs)
            for _ in range(pauses):
                await asyncio.sleep(0)
            return out

        return call


def _terminal_overlap_event(kind: str) -> tuple[str, dict[str, Any], int]:
    if kind == "invoice.payment_failed":
        return kind, invoice_obj(
            id="in_overlap_fail", paid=False, period_start=400, period_end=500), 400
    obj = {"id": SUB, "status": "canceled", "customer": CUS, "canceled_at": 350}
    if kind == "customer.subscription.deleted":
        return kind, obj, 350
    return "customer.subscription.updated", obj, 350


async def _rotation_overlap_once(policy: access_config.AccessPolicy, kind: str,
                                 order: tuple[int, int], pauses: tuple[int, int],
                                 ledger_pauses: int) -> None:
    data: dict[str, str] = {}
    inner = credits.MemoryLedger()
    setup = _ScheduledKV(data, 0)
    key = await _billing_purchase(setup, inner, policy, bound=True)
    paid = invoice_obj(id="in_overlap_paid", period_start=300, period_end=400)
    assert (await _dated_event(
        setup, inner, policy, "invoice.paid", paid, "evt_overlap_paid", created=300)).status == 200
    event_kind, obj, created = _terminal_overlap_event(kind)
    ledger = _TurnLedger(inner, ledger_pauses)
    views = [_ScheduledKV(data, pauses[0]), _ScheduledKV(data, pauses[1])]

    async def act(which: str, view: _ScheduledKV) -> Any:
        if which == "rotate":
            return await billing.rotate(
                api_key=key, kv=view, policy=policy, now=T0,
                service_commit=COMMIT, ledger=ledger)
        return await _dated_event(
            view, ledger, policy, event_kind, obj, "evt_overlap_terminal", created=created)

    actors = ("rotate", "event")
    results = await asyncio.gather(
        *[act(actors[i], views[i]) for i in order], return_exceptions=True)
    resolved: list[Any] = []
    for index, result in zip(order, results):
        if isinstance(result, BaseException):
            result = await act(actors[index], _ScheduledKV(data, 0))
        resolved.append(result)
    rotated = resolved[order.index(0)]
    assert getattr(rotated, "status", None) == 200
    current = rotated.body["key"]
    stored = await billing.store.load_subscription(_ScheduledKV(data, 0), SUB)
    record = await keys.lookup(_ScheduledKV(data, 0), current)
    assert stored is not None and record is not None
    assert stored.key_fingerprint == keys.fingerprint(current)
    assert stored.key_id == record.key_id
    assert record.tier == policy.billing.downgrade_tier
    assert stored.tier == policy.billing.downgrade_tier
    view = await inner.entitlement_view(_billing_holder(current))
    assert view["entitled"] is False
    assert (await inner.balance(_billing_holder(current))).monthly == 0


@pytest.mark.parametrize("kind", [
    "customer.subscription.deleted",
    "customer.subscription.updated",
    "invoice.payment_failed",
])
def test_rotation_and_terminal_event_agree_on_the_newest_key(policy, kind):
    """The row names the newest key, and that key's tier is the ledger tier."""

    async def scenario():
        seen = 0
        for order in ((0, 1), (1, 0)):
            for pauses in itertools.product((1, 2, 3), repeat=2):
                for ledger_pauses in (0, 1, 2):
                    seen += 1
                    await _rotation_overlap_once(
                        policy, kind, order, pauses, ledger_pauses)
        assert seen == 54

    run(scenario())


class _BindingGapLedger:
    """The first binding read is empty. The next read finishes one rotation."""

    def __init__(self, inner: credits.MemoryLedger, kv: MemoryKV, key: str,
                 policy: access_config.AccessPolicy) -> None:
        self._inner = inner
        self._kv = kv
        self._key = key
        self._policy = policy
        self.reads = 0
        self.rotated = None

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    async def key_binding(self, holder: str) -> str:
        self.reads += 1
        if self.reads == 1:
            return ""
        if self.rotated is None:
            self.rotated = await billing.rotate(
                api_key=self._key, kv=self._kv, policy=self._policy, now=T0,
                service_commit=COMMIT, ledger=self._inner)
        return await self._inner.key_binding(holder)


class _OpenBindingLedger:
    """Every binding read names a fingerprint the key store does not hold."""

    def __init__(self, inner: credits.MemoryLedger) -> None:
        self._inner = inner
        self.reads = 0

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    async def key_binding(self, holder: str) -> str:
        self.reads += 1
        return "f" * 64


def test_chronology_write_follows_a_binding_noted_on_the_second_read(policy):
    """A chronology write names the key recorded on the second binding read."""

    async def scenario():
        kv, inner = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, inner, policy, bound=True)
        original = keys.fingerprint(key)
        ledger = _BindingGapLedger(inner, kv, key, policy)
        await billing.store.record_chronology(
            kv, SUB, now=T0, policy=policy, subscription_status="active",
            updated_at=900, ledger=ledger)
        assert ledger.rotated is not None and ledger.rotated.status == 200
        newest = ledger.rotated.body["key"]
        stored = await billing.store.load_subscription(kv, SUB)
        record = await keys.lookup(kv, newest)
        assert stored is not None and record is not None
        assert stored.key_fingerprint == keys.fingerprint(newest)
        assert stored.key_fingerprint != original
        assert stored.key_id == record.key_id
        assert stored.subscription_status == "active"
        assert stored.subscription_updated_at == 900

    run(scenario())


def test_tier_write_follows_a_binding_noted_on_the_second_read(policy):
    """A tier write names the key recorded on the second binding read."""

    async def scenario():
        kv, inner = MemoryKV(), credits.MemoryLedger()
        key = await _billing_purchase(kv, inner, policy, bound=True)
        original = keys.fingerprint(key)
        ledger = _BindingGapLedger(inner, kv, key, policy)
        action = await billing.store.set_subscription_tier(
            kv, SUB, policy.billing.downgrade_tier, policy=policy, ledger=ledger)
        assert action == "tier_set"
        assert ledger.rotated is not None and ledger.rotated.status == 200
        newest = ledger.rotated.body["key"]
        stored = await billing.store.load_subscription(kv, SUB)
        record = await keys.lookup(kv, newest)
        assert stored is not None and record is not None
        assert stored.key_fingerprint == keys.fingerprint(newest)
        assert stored.key_fingerprint != original
        assert stored.key_id == record.key_id
        assert record.tier == policy.billing.downgrade_tier

    run(scenario())


def test_unsettled_binding_reports_at_the_pass_bound(policy):
    """An open binding is reported by the writer at the fourth pass."""

    async def scenario():
        kv, inner = MemoryKV(), credits.MemoryLedger()
        await _billing_purchase(kv, inner, policy, bound=True)
        ledger = _OpenBindingLedger(inner)
        with pytest.raises(RuntimeError, match="the key binding did not settle"):
            await billing.store.record_chronology(
                kv, SUB, now=T0, policy=policy, subscription_status="active",
                updated_at=900, ledger=ledger)
        assert ledger.reads == 8

    run(scenario())
