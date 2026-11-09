"""Billing prose agrees with the shipped policy and local Checkout request."""
import asyncio
import json
import re
from urllib.parse import parse_qs

from pipeline.worker_flags import production_vars
from tests.test_friends_billing import ROOT, PAID_PRICE, Stripe, access_config, billing, MemoryKV


def test_billing_reference_friends_defaults_match_checkout():
    doc = (ROOT / "docs/billing.md").read_text()
    defaults = dict(re.findall(r"^\| `(friends_\w+)` \| `([^`]+)` \|", doc, re.M))
    policy_json = json.loads((ROOT / "api/worker/tiers.json").read_text())
    for field in ("friends_price_ids", "friends_promotion_code_prefix"):
        assert json.loads(defaults[field]) == policy_json["billing"][field]
    cfg = access_config.policy_from_mapping(policy_json)
    http = Stripe({"/v1/checkout/sessions": {"id": "cs_fixture_checkout", "url": "https://checkout.stripe.com/fixture"}})
    result = asyncio.run(billing.checkout(
        payload={"price_id": PAID_PRICE}, flag=True, secret="sk_fixture",
        origin="https://api.modelspec.test", kv=MemoryKV(), policy=cfg,
        service_commit="fixture", http=http,
    ))
    assert result.status == 200
    expected = str(bool(json.loads(defaults["friends_promotion_code_prefix"]))).lower()
    assert parse_qs(http.calls[0][1]["body"])["allow_promotion_codes"] == [expected]
    assert f"allow_promotion_codes={expected}" in doc
    assert "Stripe issuance ships inert" not in doc
    assert "Both ship empty" not in doc


def test_billing_reference_current_x402_flags_and_policy_delivery():
    doc = (ROOT / "docs/billing.md").read_text()
    config = production_vars(ROOT)
    for flag in ("X402_ENABLED", "X402_MAINNET"):
        match = re.search(rf"`{flag}=(true|false)`", doc)
        assert match, f"missing current setting for {flag}"
        assert match[1] == config[flag]
    assert "Production x402 remains off" not in doc
    assert "tier_policy.py" in doc
    assert "api-access.md#the-tier-table-in-the-isolate" in doc
