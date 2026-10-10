"""MODEL-342: v2 prices, legacy grants, Scale overage, and catalog-read metering.

Checkout of a legacy or placeholder Price is refused on the shipped table.
Webhooks still grant those rows. Tests inject HTTP; none of them call Stripe.
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
import urllib.parse
from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKER_SRC = REPO_ROOT / "api" / "worker" / "src"
for path in (str(REPO_ROOT), str(WORKER_SRC)):
    if path not in sys.path:
        sys.path.insert(0, path)

import access_config  # noqa: E402
import access_keys  # noqa: E402
import access_limits  # noqa: E402
import billing  # noqa: E402
import billing_stripe  # noqa: E402
import credits  # noqa: E402
import x402  # noqa: E402
from access_kv import MemoryKV  # noqa: E402
from pipeline.pricing import procurement_data  # noqa: E402
from tests.test_billing import (  # noqa: E402
    COMMIT,
    CUS,
    PACK5,
    PRICE,
    SUB,
    _Bind,
    _Req,
    _billing_env,
    _claim,
    _form_post,
    _holder,
    _patch_entry_fetch,
    apply,
    checkout_obj,
    invoice_obj,
    payload,
)
from tests.test_visit_gate import IP, ORIGIN, environment, mint  # noqa: E402
from tests.test_x402 import _Req as _VocabReq  # noqa: E402
from tests.test_x402 import _decision_request, _decision_worker  # noqa: E402
from tests.test_x402 import entry as _x402_entry  # noqa: E402

SOLO_V2 = "price_1UP22XBPydVRHUBjk9rrxOxN"
TEAM_V2 = "price_1UP247BPydVRHUBjgGVrchgZ"
SCALE_V2 = "price_1UP25VBPydVRHUBjzN0TInX1"
PACK_250 = "price_1UP2AVBPydVRHUBjlyyyEjb1"
PACK_1300 = "price_1UP2FRBPydVRHUBj6VKuZzqb"
PACK_2750 = "price_1UP2H7BPydVRHUBjitFs1Iua"
PACK_6000 = "price_1UP2J5BPydVRHUBjgr7fOGIl"
OVERAGE_PRICE = "price_PLACEHOLDER_scale_overage_v2"
LEGACY_PACKS = {
    "price_1UHRwmBPydVRHUBjMFS5bDPD": 1250,
    "price_1UHRwmBPydVRHUBjN2mEnzdD": 7500,
    "price_1UHRwmBPydVRHUBj08ctUUjN": 20000,
    "price_1UHRwnBPydVRHUBjhRYBngwH": 50000,
}


def run(coro):
    return asyncio.run(coro)


@pytest.fixture
def policy() -> access_config.AccessPolicy:
    return access_config.load_policy()


@pytest.fixture
def entry(monkeypatch):
    return _x402_entry.__wrapped__(monkeypatch)


@pytest.fixture
def bundled_entry(monkeypatch):
    bundle = SimpleNamespace(
        read=lambda path: b'{"facets":[]}' if path == "/api/decision/vocabulary.json" else None)
    monkeypatch.setitem(sys.modules, "bundled_data", bundle)
    return _x402_entry.__wrapped__(monkeypatch)


def _tiers() -> dict:
    return json.loads(access_config.DEFAULT_POLICY_PATH.read_text(encoding="utf-8"))


def _scale_configured_text(*, cap: int = 2, sell: bool = False) -> str:
    """Scale overage configured. `sell` also clears the plan's own placeholder."""
    table = _tiers()
    row = table["billing"]["prices"][SCALE_V2]
    if sell:
        row["placeholder"] = False
    row["overage"]["placeholder"] = False
    row["overage"]["cap_credits"] = cap
    return json.dumps(table)


def _stable_clock() -> str:
    now = datetime.now(UTC)
    if now.second >= 58:
        time.sleep(2.1)
        now = datetime.now(UTC)
    return now.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _vocab(key=None, token=None, query="", method="GET"):
    headers = {"origin": ORIGIN, "cf-connecting-ip": IP}
    if token:
        import visit_token
        headers[visit_token.HEADER] = token
    if key:
        headers["authorization"] = f"Bearer {key}"
    return _VocabReq("/v1/vocabulary" + query, method=method, headers=headers)


async def _issue(env, tier: str, secret: str) -> str:
    await access_keys.issue(
        env.ACCESS, tier=tier, owner="fixture", now=datetime.now(UTC),
        policy=access_config.load_policy(env), secret=secret)
    return secret


def _stripe_ok(payload: dict):
    async def http(url, *, method, headers, body, timeout_ms=None):
        http.calls.append((url, body))

        class Resp:
            ok = True
            status = 200

            async def text(self):
                return json.dumps(payload)

        return Resp()

    http.calls = []
    return http


# ── table ────────────────────────────────────────────────────────────────────


def test_v2_rows_and_legacy_rows_parse(policy):
    expect = {
        SOLO_V2: ("plan", "Solo", 2500, 29),
        TEAM_V2: ("plan", "Team", 25000, 199),
        SCALE_V2: ("plan", "Scale", 150000, 799),
        PACK_250: ("pack", "250-credit pack", 250, 5),
        PACK_1300: ("pack", "1,300-credit pack", 1300, 25),
        PACK_2750: ("pack", "2,750-credit pack", 2750, 50),
        PACK_6000: ("pack", "6,000-credit pack", 6000, 100),
    }
    for price_id, (kind, name, amount, usd) in expect.items():
        row = policy.billing.prices[price_id]
        assert (row.kind, row.name, row.credits, row.usd) == (kind, name, amount, usd)
        assert row.placeholder is False and row.legacy is False
        assert row.for_sale is True
    legacy = {
        PRICE: ("plan", "Solo", 4000, 10),
        "price_1UHRwmBPydVRHUBjBYfcWhkW": ("plan", "Team", 30000, 50),
        **{price_id: ("pack", None, amount, None) for price_id, amount in LEGACY_PACKS.items()},
    }
    for price_id, (kind, name, amount, usd) in legacy.items():
        row = policy.billing.prices[price_id]
        assert row.kind == kind and row.credits == amount and row.legacy is True
        assert row.placeholder is False and row.for_sale is False
        assert "legacy price kept for existing customers" in row.description.lower()
        if name is not None:
            assert row.name == name
        if usd is not None:
            assert row.usd == usd
    scale = policy.billing.prices[SCALE_V2]
    assert scale.overage is not None
    assert scale.overage.usd_per_credit == "0.006"
    assert scale.overage.cap_credits == 150000
    assert scale.overage.price_id == OVERAGE_PRICE
    assert scale.overage.meter_event == "modelspec_scale_overage"
    assert scale.overage.placeholder is True and scale.overage.active is False
    reads = policy.credits.reads
    assert reads is not None
    assert (reads.reads_per_credit, reads.daily_cap, reads.burst_limit) == (10, 1000, 30)
    assert policy.x402 is not None and policy.x402.list_usd_per_decision == "0.02"
    # Legacy Solo is $0.0025, below the new overage rate. The check ignores it.
    assert Decimal(10) / Decimal(4000) < scale.overage.rate()


def test_overage_rate_must_sit_between_this_plan_and_the_other_current_plans():
    low = _tiers()
    low["billing"]["prices"][SCALE_V2]["overage"]["usd_per_credit"] = "0.001"
    with pytest.raises(access_config.PolicyError, match="above the plan"):
        access_config.policy_from_json(json.dumps(low))
    high = _tiers()
    high["billing"]["prices"][SCALE_V2]["overage"]["usd_per_credit"] = "0.02"
    with pytest.raises(access_config.PolicyError, match="below"):
        access_config.policy_from_json(json.dumps(high))
    pack = _tiers()
    pack["billing"]["prices"][PACK_250]["overage"] = {
        "usd_per_credit": "0.006", "cap_credits": 1,
        "price_id": "price_PLACEHOLDER_nope", "meter_event": "nope",
    }
    with pytest.raises(access_config.PolicyError, match="only valid on a plan"):
        access_config.policy_from_json(json.dumps(pack))


def test_published_rates_and_x402_list_price_use_the_v2_table(policy):
    data = procurement_data(_tiers())
    plans = {row["name"]: row["credits"] for row in data["products"] if row["kind"] == "plan"}
    packs = sorted(row["credits"] for row in data["products"] if row["kind"] == "pack")
    assert plans == {"Solo": 2500, "Team": 25000, "Scale": 150000}
    assert packs == [250, 1300, 2750, 6000]
    assert 4000 not in {row["credits"] for row in data["products"]}
    assert data["usd_per_credit"]["max"] == pytest.approx(5 / 250)
    assert data["usd_per_credit"]["min"] == pytest.approx(799 / 150000)
    offers = x402.packs_from_policy(policy)
    assert [pack.credits for pack in offers] == [250, 1300, 2750, 6000]
    derived = Decimal(offers[0].usd) / Decimal(offers[0].credits)
    assert policy.x402.rate() == derived == Decimal("0.02")
    loaded = x402.load_config(SimpleNamespace())
    assert loaded.price_atomic == offers[0].atomic // offers[0].credits == 20_000


# ── grants and balances ──────────────────────────────────────────────────────


@pytest.mark.parametrize("price_id,kind,amount,name", [
    (SOLO_V2, "plan", 2500, "Solo"),
    (TEAM_V2, "plan", 25000, "Team"),
    (SCALE_V2, "plan", 150000, "Scale"),
    (PACK_250, "pack", 250, "250-credit pack"),
    (PACK_1300, "pack", 1300, "1,300-credit pack"),
    (PACK_2750, "pack", 2750, "2,750-credit pack"),
    (PACK_6000, "pack", 6000, "6,000-credit pack"),
])
def test_a_v2_webhook_grants_the_row(policy, price_id, kind, amount, name):
    assert policy.price(price_id).for_sale is True
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    session = "cs_v2_" + price_id[-6:]
    if kind == "plan":
        obj = checkout_obj(
            id=session, subscription="sub_v2_" + price_id[-6:],
            metadata={"modelspec_price_id": price_id})
    else:
        obj = {
            "id": session, "object": "checkout.session", "mode": "payment",
            "payment_status": "paid", "customer": CUS,
            "payment_intent": "pi_v2_" + price_id[-6:],
            "metadata": {"modelspec_price_id": price_id},
        }
    outcome = run(apply(
        kv, policy, payload("checkout.session.completed", obj, "evt_" + price_id[-6:]),
        ledger=ledger))
    assert outcome.status == 200, outcome.body
    claimed = _claim(kv, policy, ledger, session)
    assert claimed.status == 200, claimed.body
    bal = run(ledger.balance(_holder(claimed.body["key"])))
    if kind == "plan":
        assert bal.monthly == amount and bal.packs == 0 and bal.plan == name
    else:
        assert bal.packs == amount and bal.monthly == 0


def test_a_legacy_solo_renewal_still_sets_4000_not_2500(policy):
    assert policy.billing.prices[SOLO_V2].credits == 2500
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    run(apply(kv, policy, payload("checkout.session.completed", checkout_obj(), "evt_old"),
              ledger=ledger))
    key = _claim(kv, policy, ledger).body["key"]
    holder = _holder(key)
    spent = run(ledger.reserve(holder, 1))
    assert spent.ok
    assert run(ledger.commit(holder, spent.reservation_id))
    assert run(ledger.balance(holder)).monthly == 3999
    renewed = run(apply(
        kv, policy, payload("invoice.paid", invoice_obj(), "evt_old_renew"), ledger=ledger))
    assert renewed.status == 200, renewed.body
    bal = run(ledger.balance(holder))
    assert bal.monthly == 4000 and bal.available == 4000 and bal.plan == "Solo"


def test_a_legacy_pack_still_grants_1250(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    session = "cs_legacy_pack"
    obj = {
        "id": session, "object": "checkout.session", "mode": "payment",
        "payment_status": "paid", "customer": CUS, "payment_intent": "pi_legacy_pack",
        "metadata": {"modelspec_price_id": PACK5},
    }
    assert run(apply(kv, policy, payload("checkout.session.completed", obj, "evt_old_pack"),
                     ledger=ledger)).status == 200
    claimed = _claim(kv, policy, ledger, session)
    bal = run(ledger.balance(_holder(claimed.body["key"]), now="2026-09-17T14:30:00Z"))
    assert bal.packs == 1250 and bal.monthly == 0
    assert bal.grants[0].expires_at.startswith("2027-09-17")


def test_existing_credit_balances_survive_the_v2_table(policy):
    ledger = credits.MemoryLedger()
    holder = "key:" + "ab" * 32
    assert run(ledger.set_monthly(holder, 4000, "in_kept", "Solo")).credited
    assert run(ledger.credit(
        holder, "pack_kept", 1250, "tx_kept",
        expires_at="2027-09-17T00:00:00Z", source="pack")).credited
    reloaded = access_config.load_policy()
    assert reloaded.billing.prices[SOLO_V2].credits == 2500
    assert reloaded.credits.weight("decide.summary") == 1
    before = run(ledger.balance(holder, now="2026-10-08T00:00:00Z"))
    assert before.monthly == 4000 and before.packs == 1250 and before.available == 5250
    spent = run(ledger.reserve(holder, reloaded.credits.weight("decide.summary"),
                               now="2026-10-08T00:00:00Z"))
    assert spent.ok
    assert run(ledger.commit(holder, spent.reservation_id))
    after = run(ledger.balance(holder, now="2026-10-08T00:00:00Z"))
    assert after.monthly == 3999 and after.packs == 1250 and after.available == 5249


def test_shipped_checkout_refuses_legacy_prices(entry, policy):
    legacy = {pid: row for pid, row in policy.billing.prices.items() if row.legacy}
    assert legacy and all(not row.for_sale for row in legacy.values())
    env = _billing_env(_Bind())
    for price_id, row in legacy.items():
        capture: dict[str, str] = {}
        previous = _patch_entry_fetch(entry, capture)
        try:
            worker = entry.Default()
            worker.env = env
            response = run(worker.fetch(_Req(
                "/v1/billing/checkout", body=json.dumps({"price_id": price_id}))))
        finally:
            entry.fetch = previous
        form, form_capture = _form_post(entry, f"price_id={price_id}", env=env)
        for response, capture in ((response, capture), (form, form_capture)):
            assert response.status == 500, (price_id, response.body)
            error = response.json()["error"]
            assert error["code"] == "price_not_mapped"
            assert error["price_id"] == price_id
            assert "legacy" in error["message"]
            assert "url" not in capture
            assert "location" not in {name.lower() for name in response.headers}


def test_configured_scale_checkout_adds_the_metered_overage_price(entry):
    sold = access_config.policy_from_json(_scale_configured_text(cap=150000, sell=True))
    row = sold.billing.prices[SCALE_V2]
    assert row.for_sale and row.overage.active
    env = _billing_env(_Bind())
    env.TIER_POLICY = _scale_configured_text(cap=150000, sell=True)
    capture: dict[str, str] = {}
    previous = _patch_entry_fetch(entry, capture)
    try:
        worker = entry.Default()
        worker.env = env
        response = run(worker.fetch(_Req(
            "/v1/billing/checkout", body=json.dumps({"price_id": SCALE_V2}))))
    finally:
        entry.fetch = previous
    assert response.status == 200, response.body
    fields = dict(urllib.parse.parse_qsl(capture["body"]))
    assert fields["line_items[0][price]"] == SCALE_V2
    assert fields["line_items[0][quantity]"] == "1"
    assert fields["line_items[1][price]"] == OVERAGE_PRICE
    assert "line_items[1][quantity]" not in fields
    assert capture["url"].endswith("/v1/checkout/sessions")


# ── Scale overage ────────────────────────────────────────────────────────────


def test_scale_overage_is_off_while_the_price_is_a_placeholder(policy):
    cap, spec = access_config.overage_for(policy, "Scale")
    assert cap == 0 and spec is not None and spec.placeholder
    ledger = credits.MemoryLedger()
    holder = "scale-off"
    assert run(ledger.set_monthly(holder, 0, "in_off", "Scale", "cus_off")).credited
    refused = run(ledger.reserve(holder, 1, overage_cap=cap))
    assert refused.ok is False
    assert run(ledger.balance(holder)).overage_used == 0


def test_configured_scale_overage_spends_past_zero_then_resets(policy):
    sold = access_config.policy_from_json(_scale_configured_text(cap=2))
    cap, spec = access_config.overage_for(sold, "Scale")
    assert cap == 2 and spec.active and spec.meter_event == "modelspec_scale_overage"
    ledger = credits.MemoryLedger()
    holder = "scale-on"
    assert run(ledger.set_monthly(holder, 1, "in_a", "Scale", "cus_on")).credited

    included = run(ledger.reserve(holder, 1, overage_cap=cap))
    assert included.ok and run(ledger.commit(holder, included.reservation_id)).overage == 0
    assert run(ledger.balance(holder)).available == 0

    released = run(ledger.reserve(holder, 1, overage_cap=cap))
    assert released.ok
    assert run(ledger.release(holder, released.reservation_id)) is True
    assert run(ledger.balance(holder)).overage_used == 0

    for _ in range(2):
        reserved = run(ledger.reserve(holder, 1, overage_cap=cap))
        assert reserved.ok
        assert run(ledger.commit(holder, reserved.reservation_id)).overage == 1
    assert run(ledger.balance(holder)).overage_used == 2
    assert run(ledger.reserve(holder, 1, overage_cap=cap)).ok is False

    replay = run(ledger.set_monthly(holder, 1, "in_a", "Scale", "cus_on"))
    assert replay.credited is False
    assert run(ledger.balance(holder)).overage_used == 2
    assert run(ledger.set_monthly(holder, 1, "in_b", "Scale", "cus_on")).credited
    assert run(ledger.balance(holder)).overage_used == 0
    assert run(ledger.balance(holder)).monthly == 1

    assert run(ledger.clear_monthly(holder)).credited
    cleared = run(ledger.balance(holder))
    assert cleared.plan == "" and cleared.monthly == 0 and cleared.overage_used == 0
    assert access_config.overage_for(sold, cleared.plan) == (0, None)


def test_meter_event_body_names_the_customer_and_the_settled_units():
    http = _stripe_ok({"id": "evt_meter"})
    result = run(billing_stripe.create_meter_event(
        secret="sk_test_fixture", event_name="modelspec_scale_overage",
        customer_id="cus_on", value=2, identifier="key:abc:res:7", http=http))
    assert result == {"id": "evt_meter"}
    url, body = http.calls[0]
    assert url.endswith("/v1/billing/meter_events")
    fields = dict(urllib.parse.parse_qsl(body))
    assert fields == {
        "event_name": "modelspec_scale_overage",
        "payload[stripe_customer_id]": "cus_on",
        "payload[value]": "2",
        "identifier": "key:abc:res:7",
    }
    silent = _stripe_ok({})
    assert run(billing_stripe.create_meter_event(
        secret="sk_test_fixture", event_name="modelspec_scale_overage",
        customer_id="cus_on", value=0, identifier="none", http=silent)) == {}
    assert silent.calls == []


def test_create_meter_event_posts_timestamp():
    http = _stripe_ok({"id": "evt_meter"})
    result = run(billing_stripe.create_meter_event(
        secret="sk_test_fixture", event_name="modelspec_scale_overage",
        customer_id="cus_on", value=2, identifier="key:abc:res:7",
        timestamp=1_700_000_000, http=http))
    assert result == {"id": "evt_meter"}
    fields = dict(urllib.parse.parse_qsl(http.calls[0][1]))
    assert fields["timestamp"] == "1700000000"


# ── catalog reads ────────────────────────────────────────────────────────────


def test_read_meter_charges_a_block_up_front_and_not_on_a_refusal(policy):
    reads = policy.credits.reads
    per = reads.reads_per_credit
    ledger = credits.MemoryLedger()
    holder = "reader"
    clock = "2026-10-08T12:00:00Z"
    assert run(ledger.set_monthly(holder, 2, "in_read", "Solo")).credited

    async def one():
        taken = await ledger.take_read(
            holder, per, reads.daily_cap, reads.burst_limit, now=clock)
        assert taken.ok, taken.reason
        await ledger.keep_read(holder, int(taken.token))
        return True

    for n in range(per):
        assert run(one())
    bal = run(ledger.balance(holder, now=clock))
    assert bal.available == 1 and bal.monthly == 1
    assert ledger.state.accounts[holder].reads_in_block == 0
    assert ledger.state.accounts[holder].read_count == per

    assert run(one())
    assert run(ledger.balance(holder, now=clock)).available == 0
    for _ in range(per - 1):
        assert run(one())
    assert ledger.state.accounts[holder].read_count == per * 2
    assert run(ledger.balance(holder, now=clock)).available == 0

    blocked = run(ledger.take_read(
        holder, per, reads.daily_cap, reads.burst_limit, now=clock))
    assert blocked.ok is False and blocked.reason == "exhausted"
    assert ledger.state.accounts[holder].read_count == per * 2
    assert run(ledger.balance(holder, now=clock)).available == 0

    topped = credits.MemoryLedger()
    assert run(topped.set_monthly(holder, 3, "in_abort", "Solo")).credited
    taken = run(topped.take_read(holder, per, reads.daily_cap, reads.burst_limit, now=clock))
    assert taken.ok and taken.overage == 0
    assert run(topped.balance(holder, now=clock)).available == 2
    assert topped.state.accounts[holder].read_count == 1
    assert run(topped.release_read(holder, int(taken.token))) is True
    assert run(topped.balance(holder, now=clock)).available == 3
    assert topped.state.accounts[holder].read_count == 0


def test_read_meter_refuses_the_daily_cap_and_the_burst_without_charging(policy):
    reads = policy.credits.reads
    ledger = credits.MemoryLedger()
    holder = "capped"
    clock = _stable_clock()
    assert run(ledger.set_monthly(holder, 5, "in_cap", "Solo")).credited
    account = ledger.state.accounts[holder]
    account.read_day = clock[:10]
    account.read_count = reads.daily_cap
    account.read_minute = clock[:16]
    daily = run(ledger.take_read(
        holder, reads.reads_per_credit, reads.daily_cap, reads.burst_limit, now=clock))
    assert daily.ok is False and daily.reason == "daily"
    assert account.read_count == reads.daily_cap
    assert run(ledger.balance(holder, now=clock)).available == 5

    account.read_count = 0
    account.read_burst = reads.burst_limit
    burst = run(ledger.take_read(
        holder, reads.reads_per_credit, reads.daily_cap, reads.burst_limit, now=clock))
    assert burst.ok is False and burst.reason == "burst"
    assert account.read_burst == reads.burst_limit
    assert account.read_count == 0
    assert run(ledger.balance(holder, now=clock)).available == 5


def test_a_paid_vocabulary_read_charges_one_credit_per_block(bundled_entry):
    env = environment(HUMAN_GATE_ENABLED="false", X402_ENABLED="false")
    key = run(_issue(env, "paid", "live_read_block"))
    holder = x402.holder_from_key(key)
    assert run(env.CREDITS.set_monthly(holder, 2, "in_vocab", "fixture")).credited
    worker = _decision_worker(bundled_entry, env)
    first = run(worker.fetch(_vocab(key)))
    assert first.status == 200
    assert run(env.CREDITS.balance(holder)).available == 1
    assert env.CREDITS.state.accounts[holder].read_count == 1
    counts = [name for name in env.ACCESS.store.data if name.startswith("count:")]
    assert counts == []
    for _ in range(9):
        assert run(worker.fetch(_vocab(key))).status == 200
    assert run(env.CREDITS.balance(holder)).available == 1
    assert env.CREDITS.state.accounts[holder].reads_in_block == 0
    assert env.CREDITS.state.accounts[holder].read_count == 10
    assert run(worker.fetch(_vocab(key))).status == 200
    assert run(env.CREDITS.balance(holder)).available == 0
    assert env.CREDITS.state.accounts[holder].read_count == 11
    for _ in range(9):
        assert run(worker.fetch(_vocab(key))).status == 200
    assert env.CREDITS.state.accounts[holder].read_count == 20
    served = run(worker.fetch(_vocab(key)))
    assert served.status == 200
    assert env.CREDITS.state.accounts[holder].read_count == 20
    assert run(env.CREDITS.balance(holder)).available == 0


def test_a_vocabulary_read_past_the_daily_cap_or_burst_is_rate_limited(bundled_entry, policy):
    env = environment(HUMAN_GATE_ENABLED="false", X402_ENABLED="false")
    key = run(_issue(env, "paid", "live_read_cap"))
    holder = x402.holder_from_key(key)
    assert run(env.CREDITS.set_monthly(holder, 5, "in_vocab_cap", "fixture")).credited
    clock = _stable_clock()
    account = env.CREDITS.state.accounts[holder]
    account.read_day = clock[:10]
    account.read_count = policy.credits.reads.daily_cap
    account.read_minute = clock[:16]
    worker = _decision_worker(bundled_entry, env)
    daily = run(worker.fetch(_vocab(key)))
    assert daily.status == 429
    assert daily.json()["error"]["code"] == "rate_limited"
    assert account.read_count == policy.credits.reads.daily_cap
    assert run(env.CREDITS.balance(holder)).available == 5

    account.read_count = 0
    account.read_burst = policy.credits.reads.burst_limit
    account.read_minute = _stable_clock()[:16]
    burst = run(worker.fetch(_vocab(key)))
    assert burst.status == 429
    assert burst.json()["error"]["code"] == "rate_limited"
    assert account.read_burst == policy.credits.reads.burst_limit
    assert run(env.CREDITS.balance(holder)).available == 5


def test_a_refused_vocabulary_read_is_not_charged(bundled_entry):
    env = environment(HUMAN_GATE_ENABLED="false", X402_ENABLED="false")
    key = run(_issue(env, "paid", "live_read_bad"))
    holder = x402.holder_from_key(key)
    assert run(env.CREDITS.set_monthly(holder, 2, "in_bad", "fixture")).credited
    worker = _decision_worker(bundled_entry, env)
    response = run(worker.fetch(_vocab(key, query="?section=not-a-section")))
    assert response.status == 400
    assert response.json()["error"]["code"] == "invalid_request"
    assert run(env.CREDITS.balance(holder)).available == 2
    assert env.CREDITS.state.accounts[holder].read_count == 0


def test_vocabulary_free_paths_are_not_charged(bundled_entry):
    env = environment(HUMAN_GATE_ENABLED="false", X402_ENABLED="false")
    worker = _decision_worker(bundled_entry, env)
    visit = run(worker.fetch(_vocab(token=mint(env))))
    assert visit.status == 200
    assert env.CREDITS.state.accounts == {}

    free = run(_issue(env, "free", "live_read_free"))
    assert run(worker.fetch(_vocab(free))).status == 200
    assert x402.holder_from_key(free) not in env.CREDITS.state.accounts

    exempt = run(_issue(env, "dpf", "live_read_exempt"))
    assert run(worker.fetch(_vocab(exempt))).status == 200
    assert x402.holder_from_key(exempt) not in env.CREDITS.state.accounts

    sandbox = run(worker.fetch(_vocab("test_read_sandbox")))
    assert sandbox.status == 400
    assert sandbox.json()["error"]["code"] == "sandbox_not_available"
    assert env.CREDITS.state.accounts == {}

    open_env = environment(
        VISIT_GATE_ENABLED="false", HUMAN_GATE_ENABLED="false",
        ACCESS_ENFORCED="false", X402_ENABLED="false")
    open_worker = _decision_worker(bundled_entry, open_env)
    assert run(open_worker.fetch(_vocab())).status == 200
    assert open_env.CREDITS.state.accounts == {}


def test_scale_catalog_read_reports_one_meter_event_per_settled_block(bundled_entry):
    calls = []

    async def fetch(url, options=None):
        calls.append((url, (options or {}).get("body", "")))

        class Resp:
            ok = True
            status = 200

            async def text(self):
                return "{}"

        return Resp()

    bundled_entry.fetch = fetch
    env = environment(
        HUMAN_GATE_ENABLED="false", X402_ENABLED="false",
        STRIPE_SECRET_KEY="sk_test_fixture",
        TIER_POLICY=_scale_configured_text(cap=1))
    key = run(_issue(env, "paid", "live_scale_read"))
    holder = x402.holder_from_key(key)
    assert run(env.CREDITS.set_monthly(holder, 0, "in_scale", "Scale", "cus_meter")).credited
    worker = _decision_worker(bundled_entry, env)
    for n in range(10):
        assert run(worker.fetch(_vocab(key))).status == 200, n
    assert len(calls) == 1
    url, body = calls[0]
    assert url.endswith("/v1/billing/meter_events")
    fields = dict(urllib.parse.parse_qsl(body))
    assert fields["event_name"] == "modelspec_scale_overage"
    assert fields["payload[stripe_customer_id]"] == "cus_meter"
    assert fields["payload[value]"] == "1"
    assert fields["identifier"] == (
        f"{env.CREDITS.state.accounts[holder].meter_id}:read:1")
    stopped = run(worker.fetch(_vocab(key)))
    assert stopped.status == 200
    assert len(calls) == 1
    account = env.CREDITS.state.accounts[holder]
    assert account.overage_used == 1 and account.read_count == 10

    shipped = environment(HUMAN_GATE_ENABLED="false", X402_ENABLED="false",
                          STRIPE_SECRET_KEY="sk_test_fixture")
    shipped_key = run(_issue(shipped, "paid", "live_scale_off"))
    shipped_holder = x402.holder_from_key(shipped_key)
    assert run(shipped.CREDITS.set_monthly(
        shipped_holder, 0, "in_scale_off", "Scale", "cus_off")).credited
    off = _decision_worker(bundled_entry, shipped)
    served = run(off.fetch(_vocab(shipped_key)))
    assert served.status == 200
    assert len(calls) == 1
    shipped_account = shipped.CREDITS.state.accounts[shipped_holder]
    assert shipped_account.overage_used == 0 and shipped_account.read_count == 0


@pytest.mark.parametrize("price_id,mode", [
    (SOLO_V2, "subscription"), (TEAM_V2, "subscription"), (SCALE_V2, "subscription"),
    (PACK_250, "payment"), (PACK_1300, "payment"), (PACK_2750, "payment"), (PACK_6000, "payment"),
])
def test_shipped_checkout_sells_each_live_v2_price(policy, price_id, mode):
    http = _stripe_ok({"id": "cs_live", "url": "https://checkout.stripe.com/c/pay/cs_live"})
    outcome = run(billing.checkout(
        payload={"price_id": price_id}, flag=True, secret="sk_test_fixture",
        origin="https://api.modelspec.test", kv=MemoryKV(), policy=policy,
        service_commit=COMMIT, http=http))
    assert outcome.status == 200, outcome.body
    assert len(http.calls) == 1
    fields = dict(urllib.parse.parse_qsl(http.calls[0][1]))
    assert fields["mode"] == mode
    assert fields["line_items[0][price]"] == price_id
    # The overage Price is a placeholder until MODEL-357, so Scale sells alone.
    assert "line_items[1][price]" not in fields


def test_checkout_helpers_do_not_sell_a_legacy_row_through_billing_checkout(policy):
    """The entry tests above cover HTTP. This pins the function the form calls."""
    async def boom(*_args, **_kwargs):
        raise AssertionError("stripe was called")

    for price_id in (PRICE,):
        outcome = run(billing.checkout(
            payload={"price_id": price_id}, flag=True, secret="sk_test_fixture",
            origin="https://api.modelspec.test", kv=MemoryKV(), policy=policy,
            service_commit=COMMIT, http=boom))
        assert outcome.status == 500
        assert outcome.body["error"]["code"] == "price_not_mapped"
        form = run(billing.checkout_form(
            raw=f"price_id={price_id}", flag=True, secret="sk_test_fixture",
            origin="https://api.modelspec.test", kv=MemoryKV(), policy=policy,
            service_commit=COMMIT, http=boom))
        assert form.status == 500
        assert form.headers == {}
        sold = replace(
            policy,
            billing=replace(policy.billing, prices={
                **policy.billing.prices,
                SCALE_V2: replace(
                    policy.billing.prices[SCALE_V2], placeholder=False,
                    overage=replace(policy.billing.prices[SCALE_V2].overage,
                                    placeholder=False)),
            }))
    http = _stripe_ok({"id": "cs_scale", "url": "https://checkout.stripe.com/c/pay/cs_scale"})
    outcome = run(billing.checkout(
        payload={"price_id": SCALE_V2}, flag=True, secret="sk_test_fixture",
        origin="https://api.modelspec.test", kv=MemoryKV(), policy=sold,
        service_commit=COMMIT, http=http))
    assert outcome.status == 200, outcome.body
    fields = dict(urllib.parse.parse_qsl(http.calls[0][1]))
    assert fields["line_items[1][price]"] == OVERAGE_PRICE
    assert "line_items[1][quantity]" not in fields


def _scale_key(policy):
    """A claimed Scale key, granted by the webhook."""
    kv = MemoryKV()
    ledger = credits.MemoryLedger()
    run(apply(
        kv, policy,
        payload("checkout.session.completed",
                checkout_obj(metadata={"modelspec_price_id": SCALE_V2}),
                "evt_scale_claim"),
        ledger=ledger))
    claimed = _claim(kv, policy, ledger)
    assert claimed.status == 200, claimed.body
    return kv, ledger, claimed.body["key"]


def test_a_scale_key_at_zero_allowance_decides_past_the_free_daily_limit(bundled_entry):
    env = environment(
        HUMAN_GATE_ENABLED="false", X402_ENABLED="false",
        TIER_POLICY=_scale_configured_text(cap=20))
    key = run(_issue(env, "paid", "live_scale_decide"))
    holder = x402.holder_from_key(key)
    assert run(env.CREDITS.set_monthly(
        holder, 0, "in_scale_decide", "Scale", "cus_scale")).credited
    worker = _decision_worker(bundled_entry, env)
    statuses = []
    for _ in range(11):
        response = run(worker.fetch(_decision_request(key=key)))
        statuses.append(response.status)
    assert statuses == [200] * 11
    assert run(env.CREDITS.balance(holder)).overage_used == 11


def test_a_scale_key_without_a_stripe_customer_does_not_draw_overage(bundled_entry):
    sold = access_config.policy_from_json(_scale_configured_text(cap=20))
    cap, spec = access_config.overage_for(sold, "Scale", "")
    assert cap == 0 and spec is not None and spec.active
    assert access_config.overage_for(sold, "Scale")[0] == 20

    ledger = credits.MemoryLedger()
    holder = "scale-unbilled"
    assert run(ledger.set_monthly(holder, 0, "in_unbilled", "Scale")).credited
    refused = run(ledger.reserve(holder, 1, overage_cap=20))
    assert refused.ok is False
    assert run(ledger.balance(holder)).overage_used == 0

    env = environment(
        HUMAN_GATE_ENABLED="false", X402_ENABLED="false",
        TIER_POLICY=_scale_configured_text(cap=20))
    key = run(_issue(env, "paid", "live_scale_unbilled"))
    live = x402.holder_from_key(key)
    assert run(env.CREDITS.set_monthly(live, 0, "in_unbilled_live", "Scale")).credited
    worker = _decision_worker(bundled_entry, env)
    first = run(worker.fetch(_decision_request(key=key)))
    assert first.status == 200
    assert run(env.CREDITS.balance(live)).overage_used == 0
    key_id = first.headers["x-modelspec-key-id"]
    now = datetime.now(UTC)
    day_bucket, _reset = access_limits.day_window(now)
    env.ACCESS.store.data[access_limits.counter_name(
        key_id, access_limits.DAY, day_bucket)] = "10"
    limited = run(worker.fetch(_decision_request(key=key)))
    assert limited.status == 429
    assert limited.json()["error"]["code"] == "rate_limited"
    assert limited.json()["error"]["limit"] == 10
    assert run(env.CREDITS.balance(live)).overage_used == 0


def test_a_meter_event_5xx_still_returns_the_catalog(bundled_entry):
    async def fetch(url, options=None):
        fetch.calls.append(url)

        class Resp:
            ok = False
            status = 500

            async def text(self):
                return "unavailable"

        return Resp()

    fetch.calls = []
    bundled_entry.fetch = fetch
    env = environment(
        HUMAN_GATE_ENABLED="false", X402_ENABLED="false",
        STRIPE_SECRET_KEY="sk_test_fixture",
        TIER_POLICY=_scale_configured_text(cap=5))
    key = run(_issue(env, "paid", "live_meter_fail"))
    holder = x402.holder_from_key(key)
    assert run(env.CREDITS.set_monthly(
        holder, 0, "in_meter_fail", "Scale", "cus_fail")).credited
    worker = _decision_worker(bundled_entry, env)
    response = run(worker.fetch(_vocab(key)))
    assert response.status == 200
    account = env.CREDITS.state.accounts[holder]
    assert account.overage_used == 1
    assert account.overage_unreported == 0
    assert account.overage_unreconciled == 0
    assert [row[1] for row in account.overage_uncertain] == [1]
    assert "unreported_overage" not in account.to_json()
    assert len(fetch.calls) == 1

    account.reads_in_block = 0
    second = run(worker.fetch(_vocab(key)))
    assert second.status == 200
    assert account.overage_used == 2
    assert account.overage_unreported == 0
    assert [row[1] for row in account.overage_uncertain] == [1, 1]


def _overage_spec():
    return access_config.OverageConfig(
        usd_per_credit="0.006", cap_credits=150_000, price_id=OVERAGE_PRICE,
        meter_event="modelspec_scale_overage", placeholder=False)


def _meter_fetch(*, fail_backlog=False):
    calls = []

    async def fetch(url, options=None):
        fields = dict(urllib.parse.parse_qsl((options or {}).get("body", "")))
        calls.append(fields)
        failed = fail_backlog and ":backlog:" in fields.get("identifier", "")

        class Resp:
            ok = not failed
            status = 500 if failed else 200

            async def text(self):
                return "" if failed else "{}"

        return Resp()

    return calls, fetch


def _meter_script(outcomes):
    """Each outcome is an HTTP status, 'timeout', or 'duplicate'."""
    calls = []

    async def fetch(url, options=None):
        fields = dict(urllib.parse.parse_qsl((options or {}).get("body", "")))
        calls.append(fields)
        outcome = outcomes[len(calls) - 1] if len(calls) <= len(outcomes) else 200
        if outcome == "timeout":
            raise TimeoutError("stripe timed out")
        duplicate = outcome == "duplicate"
        status = 400 if duplicate else int(outcome)

        class Resp:
            ok = 200 <= status < 300

            async def text(self, status=status, duplicate=duplicate):
                if duplicate:
                    return json.dumps({"error": {
                        "code": "duplicate_meter_event",
                        "message": (
                            "A meter event with a duplicate identifier "
                            "has already been submitted."
                        ),
                    }})
                if status >= 400:
                    return json.dumps({"error": {
                        "code": "resource_missing",
                        "message": "No such customer",
                    }})
                return "{}"

        Resp.status = status
        return Resp()

    return calls, fetch


def _overage_env():
    return SimpleNamespace(
        STRIPE_SECRET_KEY="sk_test_fixture", CREDITS=credits.MemoryLedger())


def test_failed_meter_reports_are_one_unreported_integer():
    ledger = credits.MemoryLedger()
    holder = "bounded"
    for n in range(4):
        assert run(ledger.note_unreported(
            holder, 2, f"evt-{n}", "cus_b", "modelspec_scale_overage"))
    account = ledger.state.accounts[holder]
    stored = account.to_json()
    assert account.overage_unreported == 8
    assert stored["overage_unreported"] == 8
    assert "unreported_overage" not in stored
    assert "evt-" not in json.dumps(stored)

    legacy = credits.LedgerState.from_json({"accounts": {"old": {
        "unreported_overage": [
            {"units": 2, "identifier": "a", "customer_id": "cus", "event_name": "m"},
            {"units": 3, "identifier": "b", "customer_id": "cus", "event_name": "m"},
        ],
    }}})
    assert legacy.accounts["old"].overage_unreported == 5
    assert "unreported_overage" not in legacy.accounts["old"].to_json()

    both = credits.LedgerState.from_json({"accounts": {"both": {
        "overage_unreported": 5,
        "unreported_overage": [
            {"units": 2, "identifier": "a"},
            {"units": 3, "identifier": "b"},
        ],
    }}})
    assert both.accounts["both"].overage_unreported == 5
    assert "unreported_overage" not in both.accounts["both"].to_json()


def test_the_next_meter_report_sends_the_backlog_then_the_new_event(entry):
    env = SimpleNamespace(STRIPE_SECRET_KEY="sk_test_fixture", CREDITS=credits.MemoryLedger())
    holder = "key:abc"
    for n in range(3):
        assert run(env.CREDITS.note_unreported(
            holder, 1, f"evt-{n}", "cus_ok", "modelspec_scale_overage"))
    calls, fetch = _meter_fetch()
    entry.fetch = fetch
    run(entry._post_overage(
        env, _overage_spec(), "cus_ok", 4, f"{holder}:read:9", holder=holder))
    meter = env.CREDITS.state.accounts[holder].meter_id
    assert [row["identifier"] for row in calls] == [
        f"{meter}:backlog:0", f"{holder}:read:9"]
    assert calls[0]["payload[value]"] == "3"
    assert calls[1]["payload[value]"] == "4"
    assert calls[0]["event_name"] == "modelspec_scale_overage"
    assert calls[0]["payload[stripe_customer_id]"] == "cus_ok"
    assert env.CREDITS.state.accounts[holder].overage_unreported == 0


def test_a_meter_event_timeout_records_unreported_overage_and_returns_the_catalog(
        bundled_entry):
    timeouts = []

    async def fetch(url, options=None):
        timeouts.append((options or {}).get("timeout_ms"))
        raise TimeoutError("stripe timed out")

    bundled_entry.fetch = fetch
    env = environment(
        HUMAN_GATE_ENABLED="false", X402_ENABLED="false",
        STRIPE_SECRET_KEY="sk_test_fixture",
        TIER_POLICY=_scale_configured_text(cap=5))
    key = run(_issue(env, "paid", "live_meter_timeout"))
    holder = x402.holder_from_key(key)
    assert run(env.CREDITS.set_monthly(
        holder, 0, "in_meter_timeout", "Scale", "cus_timeout")).credited
    assert run(env.CREDITS.note_unreported(
        holder, 2, "evt-old", "cus_timeout", "modelspec_scale_overage"))
    worker = _decision_worker(bundled_entry, env)
    response = run(worker.fetch(_vocab(key)))
    assert response.status == 200
    account = env.CREDITS.state.accounts[holder]
    assert account.overage_used == 1
    assert account.overage_unreported == 2
    assert account.overage_backlog_open == 2
    assert [row[1] for row in account.overage_uncertain] == [1]
    assert account.overage_uncertain[0][0] == f"{account.meter_id}:read:1"
    assert account.overage_unreconciled == 0
    assert timeouts == [5_000]


def test_a_duplicate_backlog_identifier_is_accepted_and_acked(entry):
    env = SimpleNamespace(STRIPE_SECRET_KEY="sk_test_fixture", CREDITS=credits.MemoryLedger())
    holder = "key:dup"
    assert run(env.CREDITS.note_unreported(
        holder, 4, "evt-0", "cus_d", "modelspec_scale_overage"))
    calls = []

    async def fetch(url, options=None):
        fields = dict(urllib.parse.parse_qsl((options or {}).get("body", "")))
        calls.append(fields)
        duplicate = ":backlog:" in fields.get("identifier", "")

        class Resp:
            ok = not duplicate
            status = 400 if duplicate else 200

            async def text(self):
                if duplicate:
                    return json.dumps({"error": {
                        "code": "duplicate_meter_event",
                        "message": (
                            "A meter event with a duplicate identifier "
                            "has already been submitted."
                        ),
                        "type": "invalid_request_error",
                    }})
                return "{}"

        return Resp()

    entry.fetch = fetch
    run(entry._post_overage(
        env, _overage_spec(), "cus_d", 1, f"{holder}:read:2", holder=holder))
    account = env.CREDITS.state.accounts[holder]
    assert [row["identifier"] for row in calls] == [
        f"{account.meter_id}:backlog:0", f"{holder}:read:2"]
    assert account.overage_unreported == 0
    assert account.overage_backlog_open == 0
    assert account.overage_backlog_n == 1


def test_ack_backlog_acks_only_the_open_n():
    ledger = credits.MemoryLedger()
    holder = "ack-n"
    assert run(ledger.note_unreported(
        holder, 4, "evt-0", "cus", "modelspec_scale_overage"))
    opened = run(ledger.open_backlog(holder))
    account = ledger.state.accounts[holder]
    assert opened == (4, 0, f"{account.meter_id}:backlog:0")
    assert run(ledger.ack_backlog(holder, 4, 1)) is False
    assert account.overage_unreported == 4
    assert account.overage_backlog_open == 4
    assert account.overage_backlog_n == 0
    assert run(ledger.ack_backlog(holder, 4, 0)) is True
    assert account.overage_unreported == 0
    assert account.overage_backlog_open == 0
    assert account.overage_backlog_n == 1
    assert run(ledger.note_unreported(
        holder, 4, "evt-1", "cus", "modelspec_scale_overage"))
    assert run(ledger.open_backlog(holder)) == (
        4, 1, f"{account.meter_id}:backlog:1")
    assert run(ledger.ack_backlog(holder, 4, 0)) is False
    assert account.overage_unreported == 4
    assert account.overage_backlog_open == 4
    assert account.overage_backlog_n == 1


def test_settled_overage_from_a_dropped_read_ticket_is_recorded_unreported(
        bundled_entry):
    calls = []

    async def fetch(url, options=None):
        calls.append(url)

        class Resp:
            ok = True
            status = 200

            async def text(self):
                return "{}"

        return Resp()

    bundled_entry.fetch = fetch
    env = environment(
        HUMAN_GATE_ENABLED="false", X402_ENABLED="false",
        STRIPE_SECRET_KEY="sk_test_fixture",
        TIER_POLICY=_scale_configured_text(cap=5))
    key = run(_issue(env, "paid", "live_dropped_ticket"))
    holder = x402.holder_from_key(key)
    assert run(env.CREDITS.set_monthly(
        holder, 0, "in_dropped", "Scale", "cus_drop")).credited
    real_keep = env.CREDITS.keep_read

    async def drop_ticket(holder, token):
        env.CREDITS.state.accounts[holder].taken_reads.pop(int(token), None)
        return await real_keep(holder, token)

    env.CREDITS.keep_read = drop_ticket
    worker = _decision_worker(bundled_entry, env)
    response = run(worker.fetch(_vocab(key)))
    assert response.status == 200
    account = env.CREDITS.state.accounts[holder]
    assert account.overage_used == 1
    assert account.overage_unreported == 1
    assert calls == []


def test_a_failed_backlog_drain_keeps_the_unreported_total(entry):
    env = SimpleNamespace(STRIPE_SECRET_KEY="sk_test_fixture", CREDITS=credits.MemoryLedger())
    holder = "key:abc"
    assert run(env.CREDITS.note_unreported(
        holder, 4, "evt-0", "cus_f", "modelspec_scale_overage"))
    calls, fetch = _meter_fetch(fail_backlog=True)
    entry.fetch = fetch
    run(entry._post_overage(
        env, _overage_spec(), "cus_f", 1, f"{holder}:read:2", holder=holder))
    account = env.CREDITS.state.accounts[holder]
    backlog = f"{account.meter_id}:backlog:0"
    assert [row["identifier"] for row in calls] == [backlog]
    assert calls[0]["payload[value]"] == "4"
    assert account.overage_unreported == 4
    assert [row[0] for row in account.overage_uncertain] == [f"{holder}:read:2"]

    calls.clear()
    ok_calls, ok_fetch = _meter_fetch()
    entry.fetch = ok_fetch
    run(entry._post_overage(
        env, _overage_spec(), "cus_f", 1, f"{holder}:read:3", holder=holder))
    assert [row["identifier"] for row in ok_calls] == [
        f"{holder}:read:2", backlog, f"{holder}:read:3"]
    assert ok_calls[1]["payload[value]"] == "4"
    assert account.overage_unreported == 0
    assert account.overage_uncertain == []


def test_a_failed_keep_does_not_report_metered_overage(bundled_entry):
    calls = []

    async def fetch(url, options=None):
        calls.append((url, (options or {}).get("body", "")))

        class Resp:
            ok = True
            status = 200

            async def text(self):
                return "{}"

        return Resp()

    bundled_entry.fetch = fetch
    env = environment(
        HUMAN_GATE_ENABLED="false", X402_ENABLED="false",
        STRIPE_SECRET_KEY="sk_test_fixture",
        TIER_POLICY=_scale_configured_text(cap=5))
    key = run(_issue(env, "paid", "live_keep_fail"))
    holder = x402.holder_from_key(key)
    assert run(env.CREDITS.set_monthly(
        holder, 0, "in_keep_fail", "Scale", "cus_keep")).credited
    before = run(env.CREDITS.balance(holder)).overage_used

    async def fail_keep(holder, token):
        raise RuntimeError("keep failed")

    env.CREDITS.keep_read = fail_keep
    worker = _decision_worker(bundled_entry, env)
    with pytest.raises(RuntimeError, match="keep failed"):
        run(worker.fetch(_vocab(key)))
    assert calls == []
    assert run(env.CREDITS.balance(holder)).overage_used == before
    assert env.CREDITS.state.accounts[holder].overage_unreported == 0


def test_post_overage_never_raises_when_the_http_stub_raises(bundled_entry):
    async def fetch(url, options=None):
        fetch.calls.append(url)
        raise RuntimeError("stripe down")

    fetch.calls = []
    bundled_entry.fetch = fetch

    class Ctx:
        def waitUntil(self, coro):  # noqa: N802
            coro.close()
            raise TypeError("Python coroutine is not a Promise")

    env = environment(
        HUMAN_GATE_ENABLED="false", X402_ENABLED="false",
        STRIPE_SECRET_KEY="sk_test_fixture",
        TIER_POLICY=_scale_configured_text(cap=5))
    key = run(_issue(env, "paid", "live_meter_raise"))
    holder = x402.holder_from_key(key)
    assert run(env.CREDITS.set_monthly(
        holder, 0, "in_meter_raise", "Scale", "cus_raise")).credited
    worker = _decision_worker(bundled_entry, env)
    worker.ctx = Ctx()
    response = run(worker.fetch(_vocab(key)))
    assert response.status == 200
    account = env.CREDITS.state.accounts[holder]
    assert account.overage_used == 1
    assert account.overage_unreported == 0
    assert [row[1] for row in account.overage_uncertain] == [1]
    assert fetch.calls


def test_take_read_drops_undo_tickets_from_before_today():
    ledger = credits.MemoryLedger()
    holder = "stale-read"
    assert run(ledger.set_monthly(holder, 5, "in_stale", "Solo")).credited
    yesterday = run(ledger.take_read(
        holder, 10, 1000, 100, now="2026-10-07T23:00:00Z"))
    assert yesterday.ok and yesterday.token is not None
    today = run(ledger.take_read(
        holder, 10, 1000, 100, now="2026-10-08T01:00:00Z"))
    assert today.ok and today.token is not None
    account = ledger.state.accounts[holder]
    assert int(yesterday.token) not in account.taken_reads
    assert int(today.token) in account.taken_reads
    assert account.monthly == 4
    later = run(ledger.take_read(
        holder, 10, 1000, 100, now="2026-10-08T01:05:00Z"))
    assert later.ok and later.token is not None
    assert int(today.token) in account.taken_reads
    assert int(later.token) in account.taken_reads
    assert account.monthly == 4


def test_a_timeout_retries_the_original_meter_identifier(entry):
    env = _overage_env()
    holder = "key:slow"
    ident = f"{holder}:read:7"
    calls, fetch = _meter_script(["timeout"])
    entry.fetch = fetch
    run(entry._post_overage(env, _overage_spec(), "cus_t", 3, ident, holder=holder))
    account = env.CREDITS.state.accounts[holder]
    assert calls[0]["identifier"] == ident
    assert [(row[0], row[1]) for row in account.overage_uncertain] == [(ident, 3)]
    assert account.overage_unreported == 0
    assert account.overage_unreconciled == 0

    calls, fetch = _meter_script([200, 200])
    entry.fetch = fetch
    run(entry._post_overage(
        env, _overage_spec(), "cus_t", 1, f"{holder}:read:8", holder=holder))
    assert [row["identifier"] for row in calls] == [ident, f"{holder}:read:8"]
    assert calls[0]["payload[value]"] == "3"
    assert account.overage_uncertain == []
    assert account.overage_unreported == 0


def test_a_5xx_retries_the_original_meter_identifier(entry):
    env = _overage_env()
    holder = "key:down"
    ident = f"{holder}:read:3"
    calls, fetch = _meter_script([500])
    entry.fetch = fetch
    run(entry._post_overage(env, _overage_spec(), "cus_5", 4, ident, holder=holder))
    account = env.CREDITS.state.accounts[holder]
    assert [(row[0], row[1]) for row in account.overage_uncertain] == [(ident, 4)]
    assert account.overage_unreported == 0

    calls, fetch = _meter_script([200, 200])
    entry.fetch = fetch
    run(entry._post_overage(
        env, _overage_spec(), "cus_5", 1, f"{holder}:read:4", holder=holder))
    assert [row["identifier"] for row in calls] == [ident, f"{holder}:read:4"]
    assert calls[0]["payload[value]"] == "4"
    assert account.overage_uncertain == []
    assert account.overage_unreported == 0


def test_a_duplicate_response_on_retry_clears_the_uncertain_entry(entry):
    env = _overage_env()
    holder = "key:dup-u"
    ident = f"{holder}:read:1"
    _calls, fetch = _meter_script(["timeout"])
    entry.fetch = fetch
    run(entry._post_overage(env, _overage_spec(), "cus_d", 2, ident, holder=holder))
    account = env.CREDITS.state.accounts[holder]
    assert [(row[0], row[1]) for row in account.overage_uncertain] == [(ident, 2)]

    calls, fetch = _meter_script(["duplicate", 200])
    entry.fetch = fetch
    run(entry._post_overage(
        env, _overage_spec(), "cus_d", 1, f"{holder}:read:2", holder=holder))
    assert [row["identifier"] for row in calls] == [ident, f"{holder}:read:2"]
    assert account.overage_uncertain == []
    assert account.overage_unreported == 0
    assert account.overage_unreconciled == 0


def test_a_definite_4xx_goes_to_the_backlog_total(entry):
    env = _overage_env()
    holder = "key:rej"
    ident = f"{holder}:read:1"
    calls, fetch = _meter_script([400])
    entry.fetch = fetch
    run(entry._post_overage(env, _overage_spec(), "cus_r", 6, ident, holder=holder))
    account = env.CREDITS.state.accounts[holder]
    assert calls[0]["identifier"] == ident
    assert account.overage_unreported == 6
    assert account.overage_uncertain == []
    assert account.overage_unreconciled == 0

    calls, fetch = _meter_script([200, 200])
    entry.fetch = fetch
    run(entry._post_overage(
        env, _overage_spec(), "cus_r", 1, f"{holder}:read:2", holder=holder))
    assert [row["identifier"] for row in calls] == [
        f"{account.meter_id}:backlog:0", f"{holder}:read:2"]
    assert calls[0]["payload[value]"] == "6"
    assert account.overage_unreported == 0
    assert account.overage_backlog_open == 0


def test_one_timeout_parks_the_new_event_without_another_send(entry):
    env = _overage_env()
    holder = "key:stall"
    created = int(time.time())
    for n in range(5):
        assert run(env.CREDITS.note_uncertain(
            holder, n + 1, f"{holder}:u:{n}", created))
    assert run(env.CREDITS.note_unreported(
        holder, 9, "evt-old", "cus_stall", "modelspec_scale_overage"))
    ident = f"{holder}:read:9"
    before = int(time.time())
    calls, fetch = _meter_script(["timeout"] * 8)
    entry.fetch = fetch
    run(entry._post_overage(
        env, _overage_spec(), "cus_stall", 8, ident, holder=holder))
    account = env.CREDITS.state.accounts[holder]
    assert len(calls) == 1
    assert calls[0]["identifier"] == f"{holder}:u:0"
    assert calls[0]["timestamp"] == str(created)
    assert calls[0]["payload[value]"] == "1"
    assert [row[0] for row in account.overage_uncertain] == [
        f"{holder}:u:{n}" for n in range(5)] + [ident]
    parked = account.overage_uncertain[-1]
    assert parked[1] == 8
    assert before <= parked[2] <= int(time.time())
    assert account.overage_unreported == 9
    assert account.overage_backlog_open == 0
    assert account.overage_unreconciled == 0


def test_a_request_retries_at_most_three_uncertain_entries(entry):
    env = _overage_env()
    holder = "key:bound"
    created = int(time.time()) - 30
    for n in range(4):
        assert run(env.CREDITS.note_uncertain(holder, 1, f"{holder}:u:{n}", created))
    calls, fetch = _meter_script([200] * 6)
    entry.fetch = fetch
    ident = f"{holder}:read:1"
    before = int(time.time())
    run(entry._post_overage(env, _overage_spec(), "cus_b", 1, ident, holder=holder))
    after = int(time.time())
    assert [row["identifier"] for row in calls] == [
        f"{holder}:u:0", f"{holder}:u:1", f"{holder}:u:2", ident]
    assert {row["timestamp"] for row in calls[:3]} == {str(created)}
    assert before <= int(calls[3]["timestamp"]) <= after
    assert [row[0] for row in env.CREDITS.state.accounts[holder].overage_uncertain] == [
        f"{holder}:u:3"]


def test_a_rejected_uncertain_retry_is_unreconciled(entry):
    env = _overage_env()
    holder = "key:rej-retry"
    created = int(time.time())
    assert run(env.CREDITS.note_uncertain(holder, 6, f"{holder}:u:0", created))
    assert run(env.CREDITS.note_uncertain(holder, 2, f"{holder}:u:1", created))
    ident = f"{holder}:read:1"
    calls, fetch = _meter_script([400, 200, 200])
    entry.fetch = fetch
    run(entry._post_overage(env, _overage_spec(), "cus_rr", 3, ident, holder=holder))
    account = env.CREDITS.state.accounts[holder]
    assert [row["identifier"] for row in calls] == [f"{holder}:u:0"]
    assert [row[0] for row in account.overage_uncertain] == [f"{holder}:u:1", ident]
    assert account.overage_uncertain[-1][1] == 3
    assert account.overage_unreconciled == 6
    assert account.overage_unreported == 0


def test_uncertain_entries_older_than_20_hours_are_unreconciled_before_retry(entry):
    env = _overage_env()
    holder = "key:aged"
    now = int(time.time())
    stale_at = now - credits.UNCERTAIN_MAX_AGE_SECONDS - 5
    fresh_at = now - 10
    assert run(env.CREDITS.note_uncertain(holder, 4, f"{holder}:stale", stale_at))
    assert run(env.CREDITS.note_uncertain(holder, 5, f"{holder}:fresh", fresh_at))
    calls, fetch = _meter_script([200, 200])
    entry.fetch = fetch
    ident = f"{holder}:read:1"
    run(entry._post_overage(env, _overage_spec(), "cus_age", 1, ident, holder=holder))
    assert [row["identifier"] for row in calls] == [f"{holder}:fresh", ident]
    assert calls[0]["timestamp"] == str(fresh_at)
    account = env.CREDITS.state.accounts[holder]
    assert account.overage_unreconciled == 4
    assert account.overage_uncertain == []


def test_an_uncertain_entry_is_kept_until_it_is_older_than_20_hours():
    state = credits.LedgerState()
    now = 1_800_000_000
    limit = credits.UNCERTAIN_MAX_AGE_SECONDS
    state.note_uncertain("h", 1, "edge", now - limit)
    state.note_uncertain("h", 2, "over", now - limit - 1)
    kept = state.age_uncertain("h", now)
    assert [row[0] for row in kept] == ["edge"]
    assert state.accounts["h"].overage_unreconciled == 2


def test_an_uncertain_entry_without_created_at_loads_as_created_now():
    before = int(time.time())
    state = credits.LedgerState.from_json({"accounts": {"h": {
        "overage_uncertain": [{"identifier": "evt-old", "units": 3}],
    }}})
    after = int(time.time())
    ident, units, created = state.accounts["h"].overage_uncertain[0]
    assert (ident, units) == ("evt-old", 3)
    assert before <= created <= after
    assert state.accounts["h"].overage_unreconciled == 0
    again = credits.LedgerState.from_json(json.loads(json.dumps(state.to_json())))
    assert again.accounts["h"].overage_uncertain[0][2] == created
    assert [row[0] for row in again.age_uncertain("h", created)] == ["evt-old"]


def test_durable_ledger_keeps_created_at_and_unreconciles_a_retry():
    import credits_do
    from tests.test_credits_do import Ctx

    class Namespace:
        def __init__(self):
            self.obj = credits_do.CreditsObject(Ctx(lambda v: {"v": v}), env=None)

        def idFromName(self, name):  # noqa: N802 - the Workers API name
            return name

        def get(self, _id):
            return self.obj

    ns = Namespace()
    ledger = credits.DurableLedger(ns)
    now = 1_800_000_000
    stale_at = now - credits.UNCERTAIN_MAX_AGE_SECONDS - 1
    assert run(ledger.note_uncertain("h", 4, "stale", stale_at))
    assert run(ledger.note_uncertain("h", 6, "fresh", now))
    assert run(ledger.list_uncertain("h")) == [("stale", 4, stale_at), ("fresh", 6, now)]
    assert run(ledger.age_uncertain("h", now)) == [("fresh", 6, now)]
    assert run(ledger.unreconcile_uncertain("h", "fresh")) is True
    assert run(ledger.list_uncertain("h")) == []
    raw = json.loads(ns.obj.ctx.storage.sql.table["state"])
    assert raw["accounts"]["h"]["overage_unreconciled"] == 10


def test_the_21st_uncertain_event_is_unreconciled_and_never_sent(entry):
    env = _overage_env()
    holder = "key:cap"
    for n in range(credits.UNCERTAIN_METER_CAP):
        assert run(env.CREDITS.note_uncertain(holder, 1, f"{holder}:u:{n}"))
    overflow = f"{holder}:u:overflow"
    calls, fetch = _meter_script([500] * (credits.UNCERTAIN_METER_CAP + 1))
    entry.fetch = fetch
    run(entry._post_overage(env, _overage_spec(), "cus_c", 7, overflow, holder=holder))
    account = env.CREDITS.state.accounts[holder]
    assert len(calls) == 1
    assert calls[0]["identifier"] == f"{holder}:u:0"
    assert len(account.overage_uncertain) == credits.UNCERTAIN_METER_CAP
    assert overflow not in [row[0] for row in account.overage_uncertain]
    assert account.overage_unreconciled == 7

    stored = credits.LedgerState.from_json(json.loads(json.dumps(
        env.CREDITS.state.to_json())))
    assert stored.accounts[holder].overage_unreconciled == 7
    assert len(stored.accounts[holder].overage_uncertain) == credits.UNCERTAIN_METER_CAP
    assert stored.accounts[holder].overage_uncertain[0][2] > 0

    calls, fetch = _meter_script([200] * (credits.UNCERTAIN_RETRIES_PER_REQUEST + 1))
    entry.fetch = fetch
    nxt = f"{holder}:read:next"
    run(entry._post_overage(env, _overage_spec(), "cus_c", 1, nxt, holder=holder))
    sent = [row["identifier"] for row in calls]
    assert overflow not in sent
    assert sent == [
        f"{holder}:u:{n}" for n in range(credits.UNCERTAIN_RETRIES_PER_REQUEST)
    ] + [nxt]
    assert "7" not in [row["payload[value]"] for row in calls]
    assert account.overage_unreconciled == 7
    assert [row[0] for row in account.overage_uncertain] == [
        f"{holder}:u:{n}"
        for n in range(credits.UNCERTAIN_RETRIES_PER_REQUEST, credits.UNCERTAIN_METER_CAP)
    ]
    assert account.overage_unreported == 0


def test_rotation_preserves_uncertain_events_and_identifiers(entry):
    env = _overage_env()
    src, dst = "key:old", "key:new"
    assert run(env.CREDITS.note_uncertain(src, 2, "key:old:read:1"))
    assert run(env.CREDITS.note_uncertain(src, 3, "key:old:read:4"))
    stamped = [row[2] for row in env.CREDITS.state.accounts[src].overage_uncertain]
    env.CREDITS.state.accounts[src].overage_unreconciled = 8
    assert run(env.CREDITS.note_unreported(
        src, 5, "evt-reject", "cus_rot", "modelspec_scale_overage"))
    opened = run(env.CREDITS.open_backlog(src))
    meter = env.CREDITS.state.accounts[src].meter_id
    assert opened == (5, 0, f"{meter}:backlog:0")
    assert run(env.CREDITS.transfer(src, dst))
    assert src not in env.CREDITS.state.accounts
    moved = env.CREDITS.state.accounts[dst]
    assert [(row[0], row[1]) for row in moved.overage_uncertain] == [
        ("key:old:read:1", 2), ("key:old:read:4", 3)]
    assert [row[2] for row in moved.overage_uncertain] == stamped
    assert moved.overage_unreconciled == 8
    assert moved.overage_backlog_open == 5
    assert moved.overage_backlog_n == 0
    assert moved.meter_id == meter
    assert moved.overage_backlog_id == f"{meter}:backlog:0"

    calls, fetch = _meter_script([200, 200, 200, 200])
    entry.fetch = fetch
    run(entry._post_overage(
        env, _overage_spec(), "cus_rot", 1, "key:new:read:9", holder=dst))
    assert [row["identifier"] for row in calls] == [
        "key:old:read:1",
        "key:old:read:4",
        f"{meter}:backlog:0",
        "key:new:read:9",
    ]
    assert calls[2]["payload[value]"] == "5"
    assert "8" not in [row["payload[value]"] for row in calls]
    assert moved.overage_uncertain == []
    assert moved.overage_unreported == 0
    assert moved.overage_backlog_open == 0
    assert moved.overage_unreconciled == 8


def test_transfer_onto_an_existing_holder_keeps_backlog_identifiers():
    state = credits.LedgerState()
    state.set_monthly("key:new", 1, "in_rot", "Scale")
    state.note_unreported("key:old", 5, "evt-old")
    opened_old = state.open_backlog("key:old")
    old_meter = state.accounts["key:old"].meter_id
    assert opened_old == (5, 0, f"{old_meter}:backlog:0")
    state.note_uncertain("key:old", 2, "key:old:read:1")
    state.accounts["key:old"].overage_unreconciled = 4
    assert state.transfer("key:old", "key:new")
    acc = state.accounts["key:new"]
    assert acc.monthly == 1
    assert acc.meter_id == old_meter
    assert acc.overage_backlog_id == opened_old[2]
    assert acc.overage_backlog_open == 5
    assert acc.overage_backlog_n == 0
    assert [(row[0], row[1]) for row in acc.overage_uncertain] == [("key:old:read:1", 2)]
    assert acc.overage_unreconciled == 4
    assert acc.overage_unreported == 5

    both = credits.LedgerState()
    both.note_unreported("key:new", 3, "evt-dest")
    dest_open = both.open_backlog("key:new")
    dest_meter = both.accounts["key:new"].meter_id
    assert dest_open == (3, 0, f"{dest_meter}:backlog:0")
    both.note_unreported("key:old", 5, "evt-src")
    src_open = both.open_backlog("key:old")
    src_meter = both.accounts["key:old"].meter_id
    assert src_open == (5, 0, f"{src_meter}:backlog:0")
    assert both.transfer("key:old", "key:new")
    merged = both.accounts["key:new"]
    assert merged.meter_id == dest_meter
    assert merged.overage_backlog_id == dest_open[2]
    assert merged.overage_backlog_open == 3
    assert merged.overage_unreported == 3
    assert (src_open[2], 5) in [(row[0], row[1]) for row in merged.overage_uncertain]


def test_billing_docs_name_the_unreported_overage_backlog():
    text = (REPO_ROOT / "docs" / "billing.md").read_text(encoding="utf-8")
    assert "overage_unreported" in text
    assert "overage_backlog_n" in text
    assert "overage_uncertain" in text
    assert "overage_unreconciled" in text
    assert "meter event list" in text
    assert "{meter_id}:backlog:{n}" in text
    assert "meter_id" in text
    prose = " ".join(text.split())
    assert (
        "The backlog drains on the account's next overage report; an account "
        "that never reports overage again needs the manual fallback already "
        "documented."
    ) in prose
    assert (
        "That total needs manual reconciliation against Stripe's meter event "
        "list before anyone posts it."
    ) in prose
    assert "up to 3 uncertain events" in prose
    assert "older than 20 hours" in prose
    assert "created_at" in prose
    assert "timestamp" in prose


def test_billing_docs_name_meter_event_write():
    text = (REPO_ROOT / "docs" / "billing.md").read_text(encoding="utf-8")
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("5. API keys:"))
    step = [lines[start]]
    for line in lines[start + 1:]:
        head, dot, _rest = line.partition(". ")
        if dot and head.isdigit():
            break
        step.append(line)
    assert "Billing meter events: write" in " ".join(step)


def test_one_take_read_admits_one_caller_at_the_daily_cap(policy):
    reads = policy.credits.reads
    ledger = credits.MemoryLedger()
    holder = "racer"
    clock = "2026-10-08T12:00:00Z"
    assert run(ledger.set_monthly(holder, 5, "in_race", "Solo")).credited
    account = ledger.state.accounts[holder]
    account.read_day = clock[:10]
    account.read_count = reads.daily_cap - 1
    account.read_minute = clock[:16]
    account.reads_in_block = 3

    async def race():
        return await asyncio.gather(*[
            ledger.take_read(
                holder, reads.reads_per_credit, reads.daily_cap, reads.burst_limit, now=clock)
            for _ in range(8)
        ])

    results = run(race())
    assert sum(1 for item in results if item.ok) == 1
    assert account.read_count == reads.daily_cap
    assert run(ledger.balance(holder, now=clock)).available == 5


def test_parallel_reads_at_a_block_boundary_charge_one_credit(policy):
    reads = policy.credits.reads
    ledger = credits.MemoryLedger()
    holder = "block"
    clock = "2026-10-08T12:00:00Z"
    assert run(ledger.set_monthly(holder, 5, "in_block", "Solo")).credited
    account = ledger.state.accounts[holder]
    account.reads_in_block = 0

    async def race():
        return await asyncio.gather(*[
            ledger.take_read(
                holder, reads.reads_per_credit, reads.daily_cap, reads.burst_limit, now=clock)
            for _ in range(reads.reads_per_credit)
        ])

    results = run(race())
    assert [item.ok for item in results] == [True] * reads.reads_per_credit
    assert sum(item.overage for item in results) == 0
    balance = run(ledger.balance(holder, now=clock))
    assert balance.monthly == 4 and balance.available == 4 and balance.reserved == 0
    assert account.read_count == reads.reads_per_credit
    assert account.reads_in_block == 0


def test_a_scale_invoice_with_the_overage_line_first_resets_the_allowance(policy):
    kv, ledger, key = _scale_key(policy)
    holder = _holder(key)
    account = ledger.state.accounts[holder]
    account.monthly = 10
    account.overage_used = 4
    outcome = run(apply(
        kv, policy,
        payload("invoice.paid", invoice_obj(
            id="in_scale_metered_first",
            lines={"data": [
                {"price": {"id": OVERAGE_PRICE}},
                {"price": {"id": SCALE_V2}},
            ]},
        ), "evt_scale_invoice"),
        ledger=ledger))
    assert outcome.status == 200, outcome.body
    balance = run(ledger.balance(holder))
    assert balance.monthly == policy.billing.prices[SCALE_V2].credits
    assert balance.overage_used == 0


def test_subscription_updated_restores_access_without_granting_credits(policy):
    """Only a paid invoice or Checkout grants credits. An update is not a payment."""
    kv, ledger, key = _scale_key(policy)
    holder = _holder(key)
    account = ledger.state.accounts[holder]
    account.monthly = 0
    account.overage_used = 3
    outcome = run(apply(
        kv, policy,
        payload("customer.subscription.updated", {
            "id": SUB,
            "object": "subscription",
            "status": "active",
            "customer": CUS,
            "items": {"data": [
                {"price": {"id": OVERAGE_PRICE}},
                {"price": {"id": SCALE_V2}},
            ]},
        }, "evt_scale_sub"),
        ledger=ledger))
    assert outcome.status == 200, outcome.body
    balance = run(ledger.balance(holder))
    assert balance.monthly == 0
    assert balance.overage_used == 3

    paid = run(apply(
        kv, policy,
        payload("invoice.paid", invoice_obj(id="in_scale_paid_resets", lines={
            "data": [{"price": {"id": SCALE_V2}}],
        }), "evt_scale_paid_resets"),
        ledger=ledger))
    assert paid.status == 200, paid.body
    reset = run(ledger.balance(holder))
    assert reset.monthly == 150000
    assert reset.overage_used == 0


def test_an_upgrade_grants_nothing_until_its_invoice_is_paid(policy):
    kv = MemoryKV()
    ledger = credits.MemoryLedger()
    run(apply(
        kv, policy,
        payload("checkout.session.completed",
                checkout_obj(metadata={"modelspec_price_id": SOLO_V2}), "evt_solo_claim"),
        ledger=ledger))
    claimed = _claim(kv, policy, ledger)
    holder = _holder(claimed.body["key"])
    assert run(ledger.balance(holder)).monthly == 2500
    run(apply(
        kv, policy,
        payload("customer.subscription.updated", {
            "id": SUB, "object": "subscription", "status": "active", "customer": CUS,
            "metadata": {"modelspec_price_id": SOLO_V2},
            "items": {"data": [{"price": {"id": SCALE_V2}}]},
        }, "evt_upgrade"),
        ledger=ledger))
    assert run(ledger.balance(holder)).monthly == 2500
    run(apply(
        kv, policy,
        payload("invoice.paid", invoice_obj(
            id="in_upgrade_paid", lines={"data": [{"price": {"id": SCALE_V2}}]},
        ), "evt_upgrade_paid"),
        ledger=ledger))
    assert run(ledger.balance(holder)).monthly == 150000


def test_a_funded_vocabulary_head_is_counted_and_charged_like_a_get(bundled_entry):
    env = environment(HUMAN_GATE_ENABLED="false", X402_ENABLED="false")
    worker = _decision_worker(bundled_entry, env)
    key = run(_issue(env, "paid", "live_head_paid"))
    holder = x402.holder_from_key(key)
    assert run(env.CREDITS.set_monthly(holder, 2, "in_head", "Solo")).credited
    head = run(worker.fetch(_vocab(key, method="HEAD")))
    assert head.status == 200 and head.body is None
    assert env.CREDITS.state.accounts[holder].read_count == 1
    assert run(env.CREDITS.balance(holder)).available == 1
    assert [name for name in env.ACCESS.store.data if name.startswith("count:")] == []
    follow = run(worker.fetch(_vocab(key)))
    assert follow.status == 200
    assert env.CREDITS.state.accounts[holder].read_count == 2
    assert run(env.CREDITS.balance(holder)).available == 1


def test_a_free_keys_eleventh_vocabulary_head_in_a_day_is_rate_limited(bundled_entry):
    env = environment(HUMAN_GATE_ENABLED="false", X402_ENABLED="false")
    worker = _decision_worker(bundled_entry, env)
    free = run(_issue(env, "free", "live_head_free_day"))
    first = run(worker.fetch(_vocab(free, method="HEAD")))
    assert first.status == 200 and first.body is None
    key_id = first.headers["x-modelspec-key-id"]
    now = datetime.now(UTC)
    day_bucket, _reset = access_limits.day_window(now)
    env.ACCESS.store.data[access_limits.counter_name(
        key_id, access_limits.DAY, day_bucket)] = "10"
    limited = run(worker.fetch(_vocab(free, method="HEAD")))
    assert limited.status == 429 and limited.body is None
    assert limited.headers["ratelimit-limit"] == "10"
    assert limited.headers["ratelimit-remaining"] == "0"


def test_an_exhausted_paid_key_reads_vocabulary_under_the_free_daily_limit(bundled_entry):
    env = environment(HUMAN_GATE_ENABLED="false", X402_ENABLED="false")
    key = run(_issue(env, "paid", "live_vocab_empty"))
    holder = x402.holder_from_key(key)
    assert run(env.CREDITS.set_monthly(holder, 0, "in_empty", "Solo")).credited
    worker = _decision_worker(bundled_entry, env)
    first = run(worker.fetch(_vocab(key)))
    assert first.status == 200
    assert env.CREDITS.state.accounts[holder].read_count == 0
    key_id = first.headers["x-modelspec-key-id"]
    now = datetime.now(UTC)
    day_bucket, _reset = access_limits.day_window(now)
    env.ACCESS.store.data[access_limits.counter_name(key_id, access_limits.DAY, day_bucket)] = "9"
    assert run(worker.fetch(_vocab(key))).status == 200
    limited = run(worker.fetch(_vocab(key)))
    assert limited.status == 429
    body = limited.json()
    assert body["error"]["code"] == "rate_limited"
    assert body["error"]["limit"] == 10
    assert env.CREDITS.state.accounts[holder].read_count == 0


def test_an_invoice_grants_the_billed_plan_not_stale_checkout_metadata(policy):
    """A Scale plan switched to Solo in Stripe keeps Scale in its metadata."""
    kv, ledger, key = _scale_key(policy)
    holder = _holder(key)
    outcome = run(apply(
        kv, policy,
        payload("invoice.paid", invoice_obj(
            id="in_switched_to_solo",
            metadata={"modelspec_price_id": SCALE_V2},
            lines={"data": [{"price": {"id": SOLO_V2}}]},
        ), "evt_switched_invoice"),
        ledger=ledger))
    assert outcome.status == 200, outcome.body
    assert run(ledger.balance(holder)).monthly == 2500


def test_an_invoice_with_no_mapped_line_falls_back_to_metadata(policy):
    kv, ledger, key = _scale_key(policy)
    holder = _holder(key)
    ledger.state.accounts[holder].monthly = 0
    outcome = run(apply(
        kv, policy,
        payload("invoice.paid", invoice_obj(
            id="in_overage_only",
            metadata={"modelspec_price_id": SCALE_V2},
            lines={"data": [{"price": {"id": OVERAGE_PRICE}}]},
        ), "evt_overage_only"),
        ledger=ledger))
    assert outcome.status == 200, outcome.body
    assert run(ledger.balance(holder)).monthly == 150000


@pytest.mark.parametrize("old,new,granted", [
    (SOLO_V2, SCALE_V2, 150000),
    (SCALE_V2, SOLO_V2, 2500),
    (PRICE, TEAM_V2, 25000),
])
def test_a_proration_invoice_grants_the_new_plan_not_the_credited_old_one(
        policy, old, new, granted):
    """An upgrade or downgrade invoice credits the old plan first, then charges the new one."""
    kv, ledger, key = _scale_key(policy)
    holder = _holder(key)
    outcome = run(apply(
        kv, policy,
        payload("invoice.paid", invoice_obj(
            id="in_proration_" + new[-6:],
            metadata={"modelspec_price_id": old},
            lines={"data": [
                {"amount": -1500, "proration": True, "price": {"id": old}},
                {"amount": 4200, "parent": {"subscription_item_details": {"proration": True}},
                 "pricing": {"price_details": {"price": new}}},
            ]},
        ), "evt_proration_" + new[-6:]),
        ledger=ledger))
    assert outcome.status == 200, outcome.body
    assert run(ledger.balance(holder)).monthly == granted


def test_a_renewal_with_leftover_prorations_grants_the_regular_line(policy):
    kv, ledger, key = _scale_key(policy)
    holder = _holder(key)
    outcome = run(apply(
        kv, policy,
        payload("invoice.paid", invoice_obj(
            id="in_renewal_with_prorations",
            lines={"data": [
                {"amount": -900, "proration": True, "price": {"id": SOLO_V2}},
                {"amount": 600, "proration": True, "price": {"id": TEAM_V2}},
                {"amount": 79900, "proration": False, "price": {"id": SCALE_V2}},
            ]},
        ), "evt_renewal_with_prorations"),
        ledger=ledger))
    assert outcome.status == 200, outcome.body
    assert run(ledger.balance(holder)).monthly == 150000


def test_an_invoice_for_an_unmapped_price_is_refused_not_read_from_metadata(policy):
    kv, ledger, key = _scale_key(policy)
    holder = _holder(key)
    before = run(ledger.balance(holder)).monthly
    outcome = run(apply(
        kv, policy,
        payload("invoice.paid", invoice_obj(
            id="in_unmapped",
            metadata={"modelspec_price_id": SCALE_V2},
            lines={"data": [{"price": {"id": "price_not_in_tiers"}}]},
        ), "evt_unmapped_invoice"),
        ledger=ledger))
    assert outcome.status == 500
    assert outcome.body["error"]["code"] == "price_not_mapped"
    assert run(ledger.balance(holder)).monthly == before


def test_a_subscription_on_an_unmapped_price_is_refused_not_read_from_metadata(policy):
    kv, ledger, _key = _scale_key(policy)
    outcome = run(apply(
        kv, policy,
        payload("customer.subscription.updated", {
            "id": SUB, "object": "subscription", "status": "active", "customer": CUS,
            "metadata": {"modelspec_price_id": SCALE_V2},
            "items": {"data": [{"price": {"id": "price_not_in_tiers"}}]},
        }, "evt_unmapped_sub"),
        ledger=ledger))
    assert outcome.status == 500
    assert outcome.body["error"]["code"] == "price_not_mapped"
