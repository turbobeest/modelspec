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


def test_subscription_checkout_collects_a_card_only_when_something_is_due():
    from urllib.parse import parse_qs
    from billing_stripe import checkout_form

    common = dict(price_id=PAID_PRICE, success_url="https://x/s", cancel_url="https://x/c",
                  terms_url="https://x/t")
    plan = parse_qs(checkout_form(**common, allow_promotion_codes=True))
    assert plan["payment_method_collection"] == ["if_required"]
    pack = parse_qs(checkout_form(**common, mode="payment"))
    assert "payment_method_collection" not in pack
