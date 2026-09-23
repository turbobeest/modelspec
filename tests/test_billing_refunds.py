"""A refund or chargeback takes the credits back (MODEL-106).

Found in a live $5 test on 2026-09-23: the webhook handled no refund or
dispute event, so a refunded pack left its credits on the key. Signed fixture
events in the API version 2026-08-26.dahlia shapes, never Stripe's API.

The link from a charge back to a pack is the PaymentIntent id. A payment-mode
Checkout Session names it, and the ledger's payment claim for that pack stores
it as the claim's settlement reference (`tx`). No new ACCESS record kind: the
adopted privacy statement lists those kinds, and it is not ours to widen.
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

import access_config  # noqa: E402
import access_keys as keys  # noqa: E402
import billing  # noqa: E402
import billing_stripe  # noqa: E402
import credits  # noqa: E402
from access_kv import MemoryKV  # noqa: E402

T0 = datetime(2026, 9, 23, 14, 30, 0, tzinfo=UTC)
TS = int(T0.timestamp())
NOW = "2026-09-23T14:30:00Z"
SECRET = "whsec_test_fixture_not_a_real_secret"
COMMIT = "testsha"
PACK5 = "price_1UHRwmBPydVRHUBjMFS5bDPD"      # 1,250 credits, $5
SESSION = "cs_live_refund_fixture"
PI = "pi_3UIwobBPydVRHUBj0ICY5dH3"            # the live test's PaymentIntent id
CHARGE = "ch_3UIwobBPydVRHUBj0refund"
DISPUTE = "dp_1UIwobBPydVRHUBjdispute"
AMOUNT = 535                                   # $5 plus 7% Rhode Island tax


def run(coro: Any) -> Any:
    return asyncio.run(coro)


@pytest.fixture
def policy() -> access_config.AccessPolicy:
    return access_config.load_policy()


def event(type_: str, obj: dict[str, Any], event_id: str) -> str:
    return json.dumps(
        {"id": event_id, "object": "event", "type": type_,
         "api_version": "2026-08-26.dahlia", "data": {"object": obj}},
        separators=(",", ":"))


def pack_session(*, session: str = SESSION, pi: Any = PI, price: str = PACK5,
                 fingerprint: str = "") -> dict[str, Any]:
    meta = {"modelspec_price_id": price}
    if fingerprint:
        meta["modelspec_key_fingerprint"] = fingerprint
    body: dict[str, Any] = {
        "id": session, "object": "checkout.session", "mode": "payment",
        "payment_status": "paid", "customer": None, "metadata": meta,
        "amount_total": AMOUNT,
    }
    if pi is not None:
        body["payment_intent"] = pi
    return body


def charge(*, refunded_amount: int, pi: Any = PI, amount: int = AMOUNT,
           customer: str | None = None, charge_id: str = CHARGE) -> dict[str, Any]:
    """A Charge as dahlia sends it: no `invoice`, `payment_intent` a string."""
    return {
        "id": charge_id, "object": "charge", "amount": amount,
        "amount_captured": amount, "amount_refunded": refunded_amount,
        "refunded": refunded_amount >= amount, "currency": "usd",
        "customer": customer, "payment_intent": pi, "status": "succeeded",
        "disputed": False, "metadata": {},
    }


def dispute(*, status: str, pi: Any = PI, dispute_id: str = DISPUTE) -> dict[str, Any]:
    """A Dispute: `charge` and `payment_intent` ids, and no customer."""
    return {
        "id": dispute_id, "object": "dispute", "amount": AMOUNT, "currency": "usd",
        "charge": CHARGE, "payment_intent": pi, "reason": "fraudulent",
        "status": status, "is_charge_refundable": False, "metadata": {},
    }


async def _apply(kv: Any, policy: Any, body: str, ledger: Any) -> Any:
    return await billing.webhook(
        payload=body, signature=billing_stripe.sign_header(body, SECRET, TS),
        secret=SECRET, flag=True, kv=kv, policy=policy, now=T0,
        service_commit=COMMIT, ledger=ledger)


def apply(kv: Any, policy: Any, type_: str, obj: dict[str, Any], event_id: str,
          ledger: Any) -> Any:
    return run(_apply(kv, policy, event(type_, obj, event_id), ledger))


def claim(kv: Any, policy: Any, ledger: Any, session: str = SESSION) -> Any:
    return run(billing.claim(session_id=session, flag=True, kv=kv, policy=policy,
                             now=T0, service_commit=COMMIT, ledger=ledger))


def holder(key: str) -> str:
    return credits.holder_from_fingerprint(keys.fingerprint(key))


def spend(ledger: Any, who: str, units: int) -> None:
    reserved = run(ledger.reserve(who, units, now=NOW))
    assert reserved.ok, reserved
    assert run(ledger.commit(who, reserved.reservation_id))


def balance(ledger: Any, who: str) -> credits.Balance:
    return run(ledger.balance(who, now=NOW))


def issued_key(kv: Any, policy: Any) -> str:
    secret, _ = run(keys.issue(kv, tier="free", owner="test", now=T0, policy=policy))
    return secret


def bought_pack(kv: Any, policy: Any, ledger: Any, **extra: Any) -> str:
    """An authenticated pack purchase: returns the key it credited."""
    key = issued_key(kv, policy)
    obj = pack_session(fingerprint=keys.fingerprint(key), **extra)
    outcome = apply(kv, policy, "checkout.session.completed", obj, "evt_buy", ledger)
    assert outcome.status == 200 and outcome.body["action"] == "credited", outcome.body
    return key


# ── the bug ──────────────────────────────────────────────────────────────────

def test_a_full_refund_removes_the_unspent_pack_credits(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    key = bought_pack(kv, policy, ledger)
    spend(ledger, holder(key), 1)                       # the live test spent one
    assert balance(ledger, holder(key)).packs == 1249

    outcome = apply(kv, policy, "charge.refunded", charge(refunded_amount=AMOUNT),
                    "evt_refund", ledger)

    assert outcome.status == 200, outcome.body
    assert outcome.body["action"] == "refunded"
    assert outcome.body["credits"] == {
        "purchased": 1250, "refunded_share": 1250, "removed": 1249,
        "already_spent": 1, "expired": 0, "pending_claim": False}
    assert balance(ledger, holder(key)).available == 0


def test_spent_credits_are_not_clawed_back_and_other_credits_stay(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    key = bought_pack(kv, policy, ledger)
    who = holder(key)
    run(ledger.credit(who, "pack:cs_other", 7500, "pi_other",
                      expires_at="2027-12-31T00:00:00Z", source="pack"))
    run(ledger.set_monthly(who, 4000, "in_plan", "Solo"))
    spend(ledger, who, 4000 + 1000)                     # monthly, then the oldest pack

    outcome = apply(kv, policy, "charge.refunded", charge(refunded_amount=AMOUNT),
                    "evt_refund", ledger)

    assert outcome.body["credits"]["removed"] == 250
    assert outcome.body["credits"]["already_spent"] == 1000
    after = balance(ledger, who)
    assert after.monthly == 0
    assert {g.grant_id: g.remaining for g in after.grants} == {"pack:cs_other": 7500}


def test_a_replayed_refund_event_changes_nothing(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    key = bought_pack(kv, policy, ledger)
    body = charge(refunded_amount=AMOUNT)
    apply(kv, policy, "charge.refunded", body, "evt_refund", ledger)
    run(ledger.credit(holder(key), "pack:cs_later", 50, "pi_later",
                      expires_at="2027-12-31T00:00:00Z", source="pack"))

    replay = apply(kv, policy, "charge.refunded", body, "evt_refund", ledger)
    assert replay.body["duplicate"] is True
    # A second delivery under a new event id (or a KV miss on the event record)
    # is still a no-op: removal is computed against the refunded total so far.
    again = apply(kv, policy, "charge.refunded", body, "evt_refund_again", ledger)
    assert again.body["duplicate"] is False
    assert again.body["credits"]["removed"] == 0
    assert balance(ledger, holder(key)).packs == 50


def test_a_partial_refund_removes_a_proportional_share_capped_at_unspent(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    key = bought_pack(kv, policy, ledger)
    who = holder(key)
    spend(ledger, who, 1000)                            # 250 unused

    # Refund exactly the unused value (250 of 1,250 credits = 107 of 535 cents).
    first = apply(kv, policy, "charge.refunded", charge(refunded_amount=107),
                  "evt_partial_1", ledger)
    assert first.body["action"] == "refunded_partially"
    assert first.body["credits"]["refunded_share"] == 250
    assert first.body["credits"]["removed"] == 250
    assert balance(ledger, who).packs == 0

    # A later refund of the rest: nothing unspent is left to remove.
    rest = apply(kv, policy, "charge.refunded", charge(refunded_amount=AMOUNT),
                 "evt_partial_2", ledger)
    assert rest.body["action"] == "refunded"
    assert rest.body["credits"]["refunded_share"] == 1250
    assert rest.body["credits"]["removed"] == 0
    assert rest.body["credits"]["already_spent"] == 1000


def test_two_partial_refunds_are_cumulative_not_additive(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    key = bought_pack(kv, policy, ledger)
    # amount_refunded on a Charge is the running total, so 100 then 200 is 200.
    apply(kv, policy, "charge.refunded", charge(refunded_amount=100), "evt_p1", ledger)
    second = apply(kv, policy, "charge.refunded", charge(refunded_amount=200),
                   "evt_p2", ledger)
    share = -(-1250 * 200 // AMOUNT)                    # ceil: never round in the buyer's favour
    assert second.body["credits"]["refunded_share"] == share
    assert balance(ledger, holder(key)).packs == 1250 - share


def test_a_refund_follows_the_credits_through_key_rotation(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    key = bought_pack(kv, policy, ledger)
    rotated = run(billing.rotate(api_key=key, flag=True, kv=kv, policy=policy, now=T0,
                                 service_commit=COMMIT, ledger=ledger))
    assert rotated.status == 200
    new_key = rotated.body["key"]
    assert balance(ledger, holder(new_key)).packs == 1250

    apply(kv, policy, "charge.refunded", charge(refunded_amount=AMOUNT), "evt_rot", ledger)
    assert balance(ledger, holder(new_key)).packs == 0


def test_a_request_in_flight_during_the_refund_does_not_bring_credits_back(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    key = bought_pack(kv, policy, ledger)
    who = holder(key)
    in_flight = run(ledger.reserve(who, 5, now=NOW))
    assert in_flight.ok
    outcome = apply(kv, policy, "charge.refunded", charge(refunded_amount=AMOUNT),
                    "evt_flight", ledger)
    assert outcome.body["credits"]["removed"] == 1245
    # The request fails, and its reservation is released: the five credits it
    # held belong to the refund, not to the key.
    assert run(ledger.release(who, in_flight.reservation_id))
    assert balance(ledger, who).available == 0


# ── an anonymous pack refunded before it is claimed ─────────────────────────

def test_a_pack_refunded_before_claim_mints_no_key(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    apply(kv, policy, "checkout.session.completed", pack_session(), "evt_anon", ledger)
    refunded = apply(kv, policy, "charge.refunded", charge(refunded_amount=AMOUNT),
                     "evt_anon_refund", ledger)
    assert refunded.body["action"] == "refunded"
    assert refunded.body["credits"]["pending_claim"] is True
    assert refunded.body["credits"]["removed"] == 1250

    claimed = claim(kv, policy, ledger)
    assert claimed.status == 410
    assert claimed.body["error"]["code"] == "purchase_refunded"
    assert "key" not in claimed.body


def test_a_pack_partly_refunded_before_claim_grants_the_rest(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    apply(kv, policy, "checkout.session.completed", pack_session(), "evt_anon", ledger)
    apply(kv, policy, "charge.refunded", charge(refunded_amount=107), "evt_p", ledger)
    claimed = claim(kv, policy, ledger)
    assert claimed.status == 200
    assert balance(ledger, holder(claimed.body["key"])).packs == 1000


def test_an_anonymous_pack_refunded_after_claim_loses_its_credits(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    apply(kv, policy, "checkout.session.completed", pack_session(), "evt_anon", ledger)
    key = claim(kv, policy, ledger).body["key"]
    assert balance(ledger, holder(key)).packs == 1250
    apply(kv, policy, "charge.refunded", charge(refunded_amount=AMOUNT), "evt_r", ledger)
    assert balance(ledger, holder(key)).packs == 0


def test_the_payment_intent_may_arrive_expanded(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    key = bought_pack(kv, policy, ledger, pi={"id": PI, "object": "payment_intent"})
    outcome = apply(kv, policy, "charge.refunded",
                    charge(refunded_amount=AMOUNT, pi={"id": PI}), "evt_x", ledger)
    assert outcome.body["action"] == "refunded"
    assert balance(ledger, holder(key)).packs == 0


# ── what cannot be matched ───────────────────────────────────────────────────

def test_a_charge_we_cannot_match_is_acknowledged_for_review(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    key = bought_pack(kv, policy, ledger)
    # A plan invoice's charge: dahlia's Charge names no invoice or subscription.
    outcome = apply(kv, policy, "charge.refunded",
                    charge(refunded_amount=1070, pi="pi_plan_invoice", amount=1070,
                           customer="cus_plan"), "evt_plan", ledger)
    assert outcome.status == 200
    assert outcome.body["action"] == "unmatched"
    assert outcome.body["review"] == {
        "charge": CHARGE, "payment_intent": "pi_plan_invoice", "customer": "cus_plan"}
    assert balance(ledger, holder(key)).packs == 1250


def test_a_pack_bought_before_this_change_is_unmatched_not_guessed(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    key = bought_pack(kv, policy, ledger, pi=None)      # no PaymentIntent on the session
    outcome = apply(kv, policy, "charge.refunded", charge(refunded_amount=AMOUNT),
                    "evt_old", ledger)
    assert outcome.body["action"] == "unmatched"
    assert balance(ledger, holder(key)).packs == 1250


def test_an_unbound_ledger_is_503_so_stripe_retries(policy):
    kv = MemoryKV()
    outcome = apply(kv, policy, "charge.refunded", charge(refunded_amount=AMOUNT),
                    "evt_unbound", credits.UnboundLedger())
    assert outcome.status == 503
    assert outcome.body["error"]["code"] == "access_store_not_configured"
    # Not remembered: Stripe's retry is applied once the ledger is bound.
    ledger = credits.MemoryLedger()
    retry = apply(kv, policy, "charge.refunded", charge(refunded_amount=AMOUNT),
                  "evt_unbound", ledger)
    assert retry.body["duplicate"] is False


# ── disputes ─────────────────────────────────────────────────────────────────

def test_a_dispute_holds_the_pack_until_it_is_won(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    key = bought_pack(kv, policy, ledger)
    who = holder(key)
    run(ledger.credit(who, "pack:cs_other", 7500, "pi_other",
                      expires_at="2027-12-31T00:00:00Z", source="pack"))
    spend(ledger, who, 250)                             # from the disputed pack (older)

    opened = apply(kv, policy, "charge.dispute.created",
                   dispute(status="needs_response"), "evt_dp1", ledger)
    assert opened.body["action"] == "held"
    assert opened.body["credits"]["held"] == 1000
    assert balance(ledger, who).available == 7500       # only the disputed pack is frozen
    spend(ledger, who, 7500)
    assert not run(ledger.reserve(who, 1, now=NOW)).ok

    won = apply(kv, policy, "charge.dispute.closed", dispute(status="won"),
                "evt_dp2", ledger)
    assert won.body["action"] == "restored"
    assert won.body["credits"]["restored"] == 1000
    assert balance(ledger, who).available == 1000


def test_a_lost_dispute_forfeits_the_held_credits(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    key = bought_pack(kv, policy, ledger)
    apply(kv, policy, "charge.dispute.created", dispute(status="needs_response"),
          "evt_dp1", ledger)
    lost = apply(kv, policy, "charge.dispute.closed", dispute(status="lost"),
                 "evt_dp2", ledger)
    assert lost.body["action"] == "forfeited"
    assert lost.body["credits"]["forfeited"] == 1250
    assert balance(ledger, holder(key)).available == 0
    # Nothing to restore afterwards, whatever arrives.
    late = apply(kv, policy, "charge.dispute.closed", dispute(status="won"),
                 "evt_dp3", ledger)
    assert late.body["credits"]["restored"] == 0
    assert balance(ledger, holder(key)).available == 0


def test_an_inquiry_closed_without_a_chargeback_restores(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    key = bought_pack(kv, policy, ledger)
    apply(kv, policy, "charge.dispute.created", dispute(status="warning_needs_response"),
          "evt_i1", ledger)
    closed = apply(kv, policy, "charge.dispute.closed", dispute(status="warning_closed"),
                   "evt_i2", ledger)
    assert closed.body["action"] == "restored"
    assert balance(ledger, holder(key)).packs == 1250


def test_a_dispute_closed_with_an_unknown_status_stays_held(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    key = bought_pack(kv, policy, ledger)
    apply(kv, policy, "charge.dispute.created", dispute(status="needs_response"),
          "evt_u1", ledger)
    odd = apply(kv, policy, "charge.dispute.closed", dispute(status="something_new"),
                "evt_u2", ledger)
    assert odd.body["action"] == "held_for_review"
    assert balance(ledger, holder(key)).available == 0


def test_a_replayed_dispute_changes_nothing(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    key = bought_pack(kv, policy, ledger)
    body = dispute(status="needs_response")
    apply(kv, policy, "charge.dispute.created", body, "evt_d", ledger)
    apply(kv, policy, "charge.dispute.closed", dispute(status="won"), "evt_w", ledger)
    # Created delivered again after the win (new event id): the hold is over,
    # and a second hold for the same dispute is refused.
    again = apply(kv, policy, "charge.dispute.created", body, "evt_d_again", ledger)
    assert again.body["credits"]["held"] == 0
    assert balance(ledger, holder(key)).packs == 1250


def test_a_request_released_during_a_dispute_stays_held(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    key = bought_pack(kv, policy, ledger)
    who = holder(key)
    in_flight = run(ledger.reserve(who, 5, now=NOW))
    apply(kv, policy, "charge.dispute.created", dispute(status="needs_response"),
          "evt_d", ledger)
    assert run(ledger.release(who, in_flight.reservation_id))
    assert balance(ledger, who).available == 0
    won = apply(kv, policy, "charge.dispute.closed", dispute(status="won"), "evt_w", ledger)
    assert won.body["credits"]["restored"] == 1250
    assert balance(ledger, who).available == 1250


def test_a_pack_disputed_before_claim_is_granted_held(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    apply(kv, policy, "checkout.session.completed", pack_session(), "evt_anon", ledger)
    apply(kv, policy, "charge.dispute.created", dispute(status="needs_response"),
          "evt_d", ledger)
    key = claim(kv, policy, ledger).body["key"]
    assert balance(ledger, holder(key)).available == 0
    apply(kv, policy, "charge.dispute.closed", dispute(status="won"), "evt_w", ledger)
    assert balance(ledger, holder(key)).available == 1250


def test_a_held_pack_survives_the_ledger_round_trip():
    """The Durable Object stores LedgerState as JSON between calls."""
    state = credits.LedgerState()
    who = "key:" + "ab" * 32
    state.credit(who, "pack:cs_rt", 100, PI, expires_at="2027-09-23T00:00:00Z",
                 source="pack")
    assert state.hold(PI, DISPUTE).held == 100
    state = credits.LedgerState.from_json(json.loads(json.dumps(state.to_json())))
    assert state.balance(who, now=NOW).available == 0
    assert state.end_hold(PI, DISPUTE, restore=True).restored == 100
    state = credits.LedgerState.from_json(json.loads(json.dumps(state.to_json())))
    assert state.balance(who, now=NOW).available == 100


# ── subscriptions and docs ───────────────────────────────────────────────────

def test_the_new_events_are_handled_and_documented():
    assert {"charge.refunded", "charge.dispute.created",
            "charge.dispute.closed"} <= billing.HANDLED_TYPES
    doc = (REPO_ROOT / "docs" / "billing.md").read_text(encoding="utf-8")
    for type_ in sorted(billing.HANDLED_TYPES):
        assert f"`{type_}`" in doc, f"docs/billing.md does not name {type_}"


def test_the_pack_claim_records_the_payment_intent_not_the_session(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    bought_pack(kv, policy, ledger)
    record = run(ledger.payment(f"pack:{SESSION}"))
    assert record["tx"] == PI
    assert record["kind"] == "pack"


def test_expired_pack_refund_removes_nothing_and_says_so(policy):
    kv, ledger = MemoryKV(), credits.MemoryLedger()
    key = bought_pack(kv, policy, ledger)
    later = T0 + timedelta(days=400)
    body = event("charge.refunded", charge(refunded_amount=AMOUNT), "evt_late")
    outcome = run(billing.webhook(
        payload=body, signature=billing_stripe.sign_header(body, SECRET, int(later.timestamp())),
        secret=SECRET, flag=True, kv=kv, policy=policy, now=later,
        service_commit=COMMIT, ledger=ledger))
    assert outcome.body["credits"]["removed"] == 0
    assert outcome.body["credits"]["expired"] == 1250
    assert run(ledger.balance(holder(key), now="2027-10-28T00:00:00Z")).available == 0


# ── the Durable Object path ──────────────────────────────────────────────────

class _Namespace:
    """The CREDITS binding: one CreditsObject, reached through DurableLedger's RPC."""

    def __init__(self) -> None:
        import credits_do

        from tests.test_credits_do import Ctx
        self.obj = credits_do.CreditsObject(Ctx(lambda v: {"v": v}), env=None)

    def idFromName(self, name: str) -> str:  # noqa: N802 - the Workers API name
        return name

    def get(self, _id: str) -> Any:
        return self.obj


def test_refund_and_dispute_through_the_durable_object(policy):
    kv, ledger = MemoryKV(), credits.DurableLedger(_Namespace())
    apply(kv, policy, "checkout.session.completed", pack_session(), "evt_anon", ledger)
    assert run(ledger.payment(f"pack:{SESSION}"))["pending"] is True
    key = claim(kv, policy, ledger).body["key"]
    spend(ledger, holder(key), 50)

    held = apply(kv, policy, "charge.dispute.created", dispute(status="needs_response"),
                 "evt_d", ledger)
    assert held.body["credits"]["held"] == 1200
    assert balance(ledger, holder(key)).available == 0
    apply(kv, policy, "charge.dispute.closed", dispute(status="won"), "evt_w", ledger)
    assert balance(ledger, holder(key)).available == 1200

    refunded = apply(kv, policy, "charge.refunded", charge(refunded_amount=AMOUNT),
                     "evt_r", ledger)
    assert refunded.body["credits"]["removed"] == 1200
    assert refunded.body["credits"]["already_spent"] == 50
    assert balance(ledger, holder(key)).available == 0
