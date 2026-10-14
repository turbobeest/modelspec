"""Friends billing through Worker routing and the Workers HTTP adapter."""

import asyncio
import json
from datetime import UTC, datetime
from urllib.parse import urlparse

from tests.test_access_wiring import Request, WorkersKV, _env
from tests.test_access_wiring import entry as entry
from tests.test_friends_billing import SECRET, promotion, session


def test_stripe_get_omits_request_body(entry, monkeypatch):
    async def fetch(url, options):
        assert options["method"] == "GET"
        assert "body" not in options
        return "response"

    monkeypatch.setattr(entry, "fetch", fetch)
    assert asyncio.run(entry._stripe_http(
        "https://api.stripe.com/v1/promotion_codes/promo_fixture",
        method="GET", headers={}, body="",
    )) == "response"


def test_routed_promotion_webhook_and_claim_use_configured_stripe_reader(entry, monkeypatch):
    calls = []

    async def fetch(url, options):
        calls.append((url, options))
        assert options["method"] == "GET"
        assert "body" not in options
        assert options["headers"]["authorization"] == "Bearer sk_fixture"
        assert urlparse(url).path == "/v1/promotion_codes/promo_fixture"

        class Response:
            status = 200

            async def text(self):
                return json.dumps(promotion())

        return Response()

    monkeypatch.setattr(entry, "fetch", fetch)
    env = _env(enforced="true", access=WorkersKV())
    config = json.loads(env.TIER_POLICY)
    config["billing"]["friends_promotion_code_prefix"] = "FRIENDS-"
    env.TIER_POLICY = json.dumps(config)
    env.STRIPE_SECRET_KEY = "sk_fixture"
    env.STRIPE_WEBHOOK_SECRET = SECRET
    worker = entry.Default()
    worker.env = env
    obj = session(discounts=[{"promotion_code": "promo_fixture"}])
    request = Request("/v1/billing/stripe-webhook", {
        "id": "evt_routed_friends", "type": "checkout.session.completed",
        "data": {"object": obj},
    })
    request._headers["stripe-signature"] = entry.billing.billing_stripe.sign_header(
        request._body, SECRET, int(datetime.now(UTC).timestamp()),
    )
    response = asyncio.run(worker.fetch(request))
    assert response.status == 200, response.json()
    claimed = asyncio.run(worker.fetch(Request(
        "/v1/billing/claim", {"session_id": obj["id"]},
    )))
    assert claimed.status == 200, claimed.json()
    assert claimed.json()["tier"] == "friends"
    assert claimed.json()["credits"] == 0
    assert len(calls) == 1
