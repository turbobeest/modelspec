"""Friends entitlements use signed Stripe events and the existing one-time claim."""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "api/worker/src"))

import access_config  # noqa: E402
import access_keys  # noqa: E402
import billing  # noqa: E402
import billing_stripe  # noqa: E402
import credits  # noqa: E402
from access_kv import MemoryKV  # noqa: E402

NOW = datetime(2026, 10, 14, 12, tzinfo=UTC)
SECRET = "whsec_fixture_friends"
PAID_PRICE = "price_1UP22XBPydVRHUBjk9rrxOxN"
FRIENDS_PRICE = "price_fixture_friends"


def policy(**config):
    data = json.loads((ROOT / "api/worker/tiers.json").read_text())
    # The billing seam has its own tier fixture, independent of tier rollout.
    data["tiers"]["friends"] = {
        "live_data": True, "paid": True, "credits_exempt": True,
        "daily_limit": None, "burst_limit": 60,
    }
    data["billing"].update(config)
    return access_config.policy_from_mapping(data)


def session(price=PAID_PRICE, **changes):
    return {
        "id": "cs_fixture_friends", "object": "checkout.session",
        "mode": "subscription", "payment_status": "no_payment_required",
        "subscription": "sub_fixture_friends", "customer": "cus_fixture_friends",
        "metadata": {"modelspec_price_id": price}, **changes,
    }


def event(obj, kind="checkout.session.completed", event_id="evt_fixture_friends"):
    return json.dumps({"id": event_id, "type": kind, "data": {"object": obj}})


async def hook(kv, cfg, obj, **kwargs):
    raw = event(obj, **{k: kwargs.pop(k) for k in ("kind", "event_id") if k in kwargs})
    return await billing.webhook(
        payload=raw, signature=billing_stripe.sign_header(raw, SECRET, int(NOW.timestamp())),
        secret=SECRET, kv=kv, policy=cfg, now=NOW, service_commit="fixture", **kwargs,
    )


async def claim(kv, cfg):
    return await billing.claim(
        session_id="cs_fixture_friends", kv=kv, policy=cfg, now=NOW,
        service_commit="fixture",
    )


class Stripe:
    def __init__(self, objects):
        self.objects, self.calls = objects, []

    async def __call__(self, url, **kwargs):
        self.calls.append((url, kwargs))
        path = urlparse(url).path
        assert kwargs["headers"]["authorization"] == "Bearer sk_fixture"
        assert kwargs["headers"]["stripe-version"] == billing_stripe.STRIPE_API_VERSION
        data = self.objects[path]

        class Response:
            status, ok = 200, True

            async def text(self):
                return json.dumps(data)

        return Response()


def promotion(percent=100, duration="forever", code="FRIENDS-JAMIE"):
    return {"id": "promo_fixture", "code": code, "promotion": {
        "type": "coupon", "coupon": {"id": "coupon_fixture", "percent_off": percent,
                                       "duration": duration},
    }}


def test_configured_zero_price_claims_once_rotates_and_cancels():
    async def scenario():
        kv = MemoryKV()
        cfg = policy(friends_price_ids=[FRIENDS_PRICE])
        result = await hook(kv, cfg, session(FRIENDS_PRICE))
        assert result.status == 200, result.body
        result = await claim(kv, cfg)
        assert result.status == 200, result.body
        assert result.body["tier"] == "friends"
        assert result.body["credits"] == 0
        assert "credits" not in result.body["what_you_bought"].lower()
        key = result.body["key"]
        assert (await access_keys.lookup(kv, key)).tier == "friends"
        assert (await claim(kv, cfg)).status == 410
        rotated = await billing.rotate(api_key=key, kv=kv, policy=cfg, now=NOW,
                                       service_commit="fixture")
        assert rotated.status == 200
        assert rotated.body["tier"] == "friends"
        assert not (await access_keys.lookup(kv, key)).active
        canceled = await hook(kv, cfg, {"id": "sub_fixture_friends"},
                              kind="customer.subscription.deleted", event_id="evt_cancel")
        assert canceled.status == 200
        assert (await access_keys.lookup(kv, rotated.body["key"])).tier == "free"

    asyncio.run(scenario())


def test_unconfigured_price_never_grants_friends():
    async def scenario():
        kv, cfg = MemoryKV(), policy()
        result = await hook(kv, cfg, session(FRIENDS_PRICE))
        assert result.status == 500
        assert result.body["error"]["code"] == "price_not_mapped"
        assert (await claim(kv, cfg)).status == 409

    asyncio.run(scenario())


def test_configured_promotion_id_resolves_customer_code_and_claims_friends():
    async def scenario():
        kv = MemoryKV()
        cfg = policy(friends_promotion_code_prefix="friends-")
        http = Stripe({"/v1/promotion_codes/promo_fixture": promotion()})
        result = await hook(kv, cfg, session(discounts=[{"promotion_code": "promo_fixture"}]),
                            stripe_secret="sk_fixture", http=http)
        assert result.status == 200, result.body
        result = await claim(kv, cfg)
        assert result.status == 200, result.body
        assert result.body["tier"] == "friends"
        assert result.body["credits"] == 0
        assert "credits" not in result.body["what_you_bought"].lower()
        assert len(http.calls) == 1
        assert parse_qs(urlparse(http.calls[0][0]).query) == {
            "expand[]": ["promotion.coupon"],
        }
        # A renewal and an active-subscription update retain the promo entitlement.
        for kind, obj in [
            ("invoice.paid", {"id": "in_fixture", "subscription": "sub_fixture_friends",
                              "lines": {"data": [{"price": PAID_PRICE}]}}),
            ("customer.subscription.updated", {"id": "sub_fixture_friends", "status": "active",
                                                "items": {"data": [{"price": PAID_PRICE}]}}),
        ]:
            obj["discounts"] = [{"promotion_code": promotion()}]
            renewal = await hook(kv, cfg, obj, kind=kind, event_id=kind)
            assert renewal.status == 200, renewal.body
            assert (await access_keys.lookup(kv, result.body["key"])).tier == "friends"

    asyncio.run(scenario())


@pytest.mark.parametrize("config,discount", [
    ({"friends_promotion_code_prefix": ""}, promotion()),  # unconfigured, whatever ships
    ({"friends_promotion_code_prefix": "OTHER-"}, promotion()),
    ({"friends_promotion_code_prefix": "FRIENDS-"}, promotion(percent=99)),
    ({"friends_promotion_code_prefix": "FRIENDS-"}, promotion(duration="once")),
])
def test_unconfigured_or_nonqualifying_promotion_keeps_paid_tier(config, discount):
    async def scenario():
        kv, cfg = MemoryKV(), policy(**config)
        result = await hook(kv, cfg, session(discounts=[{"promotion_code": discount}]))
        assert result.status == 200, result.body
        result = await claim(kv, cfg)
        assert result.status == 200
        assert result.body["tier"] == "paid"

    asyncio.run(scenario())


def test_payment_link_webhook_resolves_unexpanded_line_items():
    async def scenario():
        kv, cfg = MemoryKV(), policy(friends_price_ids=[FRIENDS_PRICE])
        resolved = session(FRIENDS_PRICE, metadata={}, line_items={
            "data": [{"price": {"id": FRIENDS_PRICE}}],
        })
        http = Stripe({"/v1/checkout/sessions/cs_fixture_friends": resolved})
        result = await hook(kv, cfg, session(metadata={}),
                            stripe_secret="sk_fixture", http=http)
        assert result.status == 200, result.body
        assert (await claim(kv, cfg)).body["tier"] == "friends"
        assert len(http.calls) == 1

    asyncio.run(scenario())


def test_unresolved_promotion_is_retryable_and_does_not_mint_paid_key():
    async def scenario():
        kv, cfg = MemoryKV(), policy(friends_promotion_code_prefix="FRIENDS-")
        result = await hook(kv, cfg, session(discounts=[{"promotion_code": "promo_fixture"}]))
        assert result.status == 503
        assert (await claim(kv, cfg)).status == 409

    asyncio.run(scenario())


@pytest.mark.parametrize("prefix,price,expected", [
    ("", PAID_PRICE, "false"),
    ("FRIENDS-", PAID_PRICE, "true"),
    ("FRIENDS-", "price_1UP2AVBPydVRHUBjlyyyEjb1", "false"),
])
def test_checkout_allows_promotion_entry_only_when_configured(prefix, price, expected):
    async def scenario():
        cfg = policy(friends_promotion_code_prefix=prefix)
        http = Stripe({"/v1/checkout/sessions": {
            "id": "cs_fixture_checkout", "url": "https://checkout.stripe.com/fixture",
        }})
        result = await billing.checkout(
            payload={"price_id": price}, flag=True, secret="sk_fixture",
            origin="https://api.modelspec.dev", kv=MemoryKV(), policy=cfg,
            service_commit="fixture", http=http,
        )
        assert result.status == 200, result.body
        assert parse_qs(http.calls[0][1]["body"])["allow_promotion_codes"] == [expected]

    asyncio.run(scenario())


def test_matching_promotion_on_external_pack_keeps_pack_entitlement():
    async def scenario():
        import credits

        kv, cfg = MemoryKV(), policy(friends_promotion_code_prefix="FRIENDS-")
        ledger = credits.MemoryLedger()
        obj = session("price_1UP2AVBPydVRHUBjlyyyEjb1", mode="payment", subscription=None,
                      discounts=[{"promotion_code": promotion()}])
        result = await hook(kv, cfg, obj, ledger=ledger)
        assert result.status == 200, result.body
        result = await billing.claim(session_id=obj["id"], kv=kv, policy=cfg, now=NOW,
                                     service_commit="fixture", ledger=ledger)
        assert result.status == 200, result.body
        assert result.body["tier"] == "paid"
        assert result.body["kind"] == "pack"
        assert result.body["credits"] == 250

    asyncio.run(scenario())


class _CreditsSql:
    def __init__(self):
        self.table = {}

    def exec(self, query, *params):
        class Cursor:
            def __init__(self, row):
                self._row = row

            def one(self):
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


class _CreditsCtx:
    def __init__(self):
        self.storage = type("Storage", (), {"sql": _CreditsSql()})()
        self._gate = asyncio.Lock()

    async def blockConcurrencyWhile(self, callback):
        async with self._gate:
            return await callback()


def real_ledger(kind, kv):
    if kind == "memory":
        return credits.MemoryLedger()
    import credits_do
    from types import SimpleNamespace

    obj = credits_do.CreditsObject(_CreditsCtx(), env=SimpleNamespace(ACCESS=kv))
    namespace = SimpleNamespace(idFromName=lambda name: name, get=lambda _id: obj)
    return credits.DurableLedger(namespace)


def friends_invoice(**extra):
    body = {
        "id": "in_fixture",
        "subscription": "sub_fixture_friends",
        "customer": "cus_fixture_friends",
        "lines": {"data": [{"price": {"id": PAID_PRICE}}]},
        "discounts": [{"promotion_code": promotion()}],
        "period_start": 100,
        "period_end": 200,
    }
    body.update(extra)
    return body


async def _promo_checkout(kv, cfg, ledger, **changes):
    http = Stripe({"/v1/promotion_codes/promo_fixture": promotion()})
    result = await hook(
        kv, cfg, session(discounts=[{"promotion_code": "promo_fixture"}], **changes),
        stripe_secret="sk_fixture", http=http, ledger=ledger)
    assert result.status == 200, result.body
    return result


async def _friends_row_and_key(kv, key):
    row = await billing.store.load_subscription(kv, "sub_fixture_friends")
    record = await access_keys.lookup(kv, key)
    return row, record


@pytest.mark.parametrize("kind", ["memory", "durable"])
def test_promotion_invoice_and_replay_keep_friends(kind):
    """A promotion-code Friends subscription stays friends after invoice.paid."""
    async def scenario():
        kv = MemoryKV()
        cfg = policy(friends_promotion_code_prefix="FRIENDS-")
        ledger = real_ledger(kind, kv)
        await _promo_checkout(kv, cfg, ledger)
        claimed = await billing.claim(
            session_id="cs_fixture_friends", kv=kv, policy=cfg, now=NOW,
            service_commit="fixture", ledger=ledger)
        assert claimed.status == 200, claimed.body
        key = claimed.body["key"]
        paid = await hook(kv, cfg, friends_invoice(), kind="invoice.paid",
                          event_id="evt_friends_invoice", ledger=ledger)
        assert paid.status == 200, paid.body
        row, record = await _friends_row_and_key(kv, key)
        assert record.tier == "friends"
        assert row.tier == "friends" and row.status == "active"
        again = await hook(kv, cfg, friends_invoice(), kind="invoice.paid",
                           event_id="evt_friends_invoice_replay", ledger=ledger)
        assert again.status == 200, again.body
        row, record = await _friends_row_and_key(kv, key)
        assert record.tier == "friends"
        assert row.tier == "friends" and row.status == "active"

    asyncio.run(scenario())


def test_promotion_checkout_bound_to_a_key_keeps_friends():
    async def scenario():
        kv = MemoryKV()
        cfg = policy(friends_promotion_code_prefix="FRIENDS-")
        ledger = credits.MemoryLedger()
        issued, _ = await access_keys.issue(
            kv, tier="free", owner="fixture", now=NOW, policy=cfg)
        fingerprint = access_keys.fingerprint(issued)
        await _promo_checkout(
            kv, cfg, ledger,
            metadata={"modelspec_price_id": PAID_PRICE,
                      "modelspec_key_fingerprint": fingerprint})
        row, record = await _friends_row_and_key(kv, issued)
        assert record.tier == "friends"
        assert row.tier == "friends"

    asyncio.run(scenario())


def test_promotion_rotation_after_a_grant_keeps_friends():
    async def scenario():
        kv = MemoryKV()
        cfg = policy(friends_promotion_code_prefix="FRIENDS-")
        ledger = credits.MemoryLedger()
        await _promo_checkout(kv, cfg, ledger)
        claimed = await billing.claim(
            session_id="cs_fixture_friends", kv=kv, policy=cfg, now=NOW,
            service_commit="fixture", ledger=ledger)
        key = claimed.body["key"]
        assert (await hook(kv, cfg, friends_invoice(), kind="invoice.paid",
                           event_id="evt_friends_rotate_invoice", ledger=ledger)).status == 200
        rotated = await billing.rotate(
            api_key=key, kv=kv, policy=cfg, now=NOW, service_commit="fixture", ledger=ledger)
        assert rotated.status == 200, rotated.body
        assert rotated.body["tier"] == "friends"
        row, record = await _friends_row_and_key(kv, rotated.body["key"])
        assert record.tier == "friends"
        assert row.tier == "friends"

    asyncio.run(scenario())


def test_promotion_cancellation_after_a_grant_downgrades():
    async def scenario():
        kv = MemoryKV()
        cfg = policy(friends_promotion_code_prefix="FRIENDS-")
        ledger = credits.MemoryLedger()
        await _promo_checkout(kv, cfg, ledger)
        claimed = await billing.claim(
            session_id="cs_fixture_friends", kv=kv, policy=cfg, now=NOW,
            service_commit="fixture", ledger=ledger)
        key = claimed.body["key"]
        assert (await hook(kv, cfg, friends_invoice(), kind="invoice.paid",
                           event_id="evt_friends_cancel_invoice", ledger=ledger)).status == 200
        canceled = await hook(
            kv, cfg, {"id": "sub_fixture_friends", "status": "canceled",
                      "customer": "cus_fixture_friends", "canceled_at": 300},
            kind="customer.subscription.deleted", event_id="evt_friends_cancel",
            ledger=ledger)
        assert canceled.status == 200, canceled.body
        row, record = await _friends_row_and_key(kv, key)
        assert record.tier == cfg.billing.downgrade_tier
        assert row.tier == cfg.billing.downgrade_tier
        assert row.status == "inactive"

    asyncio.run(scenario())


def test_same_price_without_a_qualifying_promotion_stays_paid():
    async def scenario():
        kv = MemoryKV()
        cfg = policy(friends_promotion_code_prefix="FRIENDS-")
        ledger = credits.MemoryLedger()
        assert (await hook(kv, cfg, session(), ledger=ledger)).status == 200
        claimed = await billing.claim(
            session_id="cs_fixture_friends", kv=kv, policy=cfg, now=NOW,
            service_commit="fixture", ledger=ledger)
        assert claimed.status == 200, claimed.body
        key = claimed.body["key"]
        invoice = friends_invoice()
        invoice["discounts"] = []
        assert (await hook(kv, cfg, invoice, kind="invoice.paid",
                           event_id="evt_paid_price", ledger=ledger)).status == 200
        row, record = await _friends_row_and_key(kv, key)
        assert record.tier == "paid"
        assert row.tier == "paid"

    asyncio.run(scenario())


@pytest.mark.parametrize("kind", ["memory", "durable"])
def test_cancelled_promotion_resubscribe_invoice_keeps_friends(kind):
    """A later paid period writes the event mapping after the row was downgraded."""
    async def scenario():
        kv = MemoryKV()
        cfg = policy(friends_promotion_code_prefix="FRIENDS-")
        ledger = real_ledger(kind, kv)
        await _promo_checkout(kv, cfg, ledger)
        claimed = await billing.claim(
            session_id="cs_fixture_friends", kv=kv, policy=cfg, now=NOW,
            service_commit="fixture", ledger=ledger)
        assert claimed.status == 200, claimed.body
        key = claimed.body["key"]
        assert (await hook(kv, cfg, friends_invoice(), kind="invoice.paid",
                           event_id="evt_friends_before_cancel", ledger=ledger)).status == 200
        canceled = await hook(
            kv, cfg, {"id": "sub_fixture_friends", "status": "canceled",
                      "customer": "cus_fixture_friends", "canceled_at": 300},
            kind="customer.subscription.deleted", event_id="evt_friends_resub_cancel",
            ledger=ledger)
        assert canceled.status == 200, canceled.body
        row, record = await _friends_row_and_key(kv, key)
        assert record.tier == cfg.billing.downgrade_tier
        assert row.tier == cfg.billing.downgrade_tier
        later = friends_invoice(id="in_friends_later", period_start=400, period_end=500)
        paid = await hook(kv, cfg, later, kind="invoice.paid",
                          event_id="evt_friends_later", ledger=ledger)
        assert paid.status == 200, paid.body
        row, record = await _friends_row_and_key(kv, key)
        assert record.tier == "friends"
        assert row.tier == "friends" and row.status == "active"

    asyncio.run(scenario())


def test_cancelled_promotion_checkout_link_keeps_friends():
    """A Checkout that links a downgraded key writes the event mapping."""
    async def scenario():
        kv = MemoryKV()
        cfg = policy(friends_promotion_code_prefix="FRIENDS-")
        ledger = credits.MemoryLedger()
        await _promo_checkout(kv, cfg, ledger)
        claimed = await billing.claim(
            session_id="cs_fixture_friends", kv=kv, policy=cfg, now=NOW,
            service_commit="fixture", ledger=ledger)
        assert claimed.status == 200, claimed.body
        key = claimed.body["key"]
        fingerprint = access_keys.fingerprint(key)
        assert (await hook(kv, cfg, friends_invoice(), kind="invoice.paid",
                           event_id="evt_link_before_cancel", ledger=ledger)).status == 200
        canceled = await hook(
            kv, cfg, {"id": "sub_fixture_friends", "status": "canceled",
                      "customer": "cus_fixture_friends", "canceled_at": 300},
            kind="customer.subscription.deleted", event_id="evt_link_cancel",
            ledger=ledger)
        assert canceled.status == 200, canceled.body
        row, record = await _friends_row_and_key(kv, key)
        assert record.tier == cfg.billing.downgrade_tier
        assert row.tier == cfg.billing.downgrade_tier
        opened = friends_invoice(
            id="in_open_paid", subscription="sub_open_friends",
            period_start=100, period_end=200, discounts=[])
        assert (await hook(kv, cfg, opened, kind="invoice.paid",
                           event_id="evt_open_paid", ledger=ledger)).status == 200
        open_row = await billing.store.load_subscription(kv, "sub_open_friends")
        assert open_row is not None and open_row.tier == "paid"
        assert open_row.key_fingerprint == ""
        link = session(
            id="cs_friends_link", subscription="sub_open_friends",
            discounts=[{"promotion_code": promotion()}],
            metadata={"modelspec_price_id": PAID_PRICE,
                      "modelspec_key_fingerprint": fingerprint})
        linked = await hook(kv, cfg, link, event_id="evt_friends_link", ledger=ledger)
        assert linked.status == 200, linked.body
        record = await access_keys.lookup(kv, key)
        open_row = await billing.store.load_subscription(kv, "sub_open_friends")
        assert record.tier == "friends"
        assert open_row.tier == "friends" and open_row.status == "active"
        assert open_row.key_fingerprint == fingerprint

    asyncio.run(scenario())


def test_friends_price_is_neither_advertised_nor_sold_by_public_checkout():
    async def scenario():
        cfg = policy(friends_price_ids=[FRIENDS_PRICE])
        http = Stripe({"/v1/checkout/sessions": {
            "id": "cs_fixture_checkout", "url": "https://checkout.stripe.com/fixture",
        }})
        arguments = dict(flag=True, secret="sk_fixture", origin="https://api.modelspec.dev",
                         kv=MemoryKV(), policy=cfg, service_commit="fixture", http=http)
        omitted = await billing.checkout(payload={}, **arguments)
        assert omitted.status == 400
        assert FRIENDS_PRICE not in omitted.body["error"]["valid_price_ids"]
        direct = await billing.checkout(payload={"price_id": FRIENDS_PRICE}, **arguments)
        assert direct.status == 500
        assert direct.body["error"]["code"] == "price_not_mapped"
        assert http.calls == []

    asyncio.run(scenario())
