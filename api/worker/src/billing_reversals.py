"""A refund or a chargeback takes the credits back (MODEL-106).

`charge.refunded`, `charge.dispute.created` and `charge.dispute.closed` act on
the **credits** a purchase put on a key, because credits are the paid
entitlement: `entry.py` serves the paid answer, with no daily cap, whenever
the ledger can reserve the call's weight, whatever tier the key record names.
Moving a key's tier row to `free` would not stop a funded key; zeroing the
whole key would also take credits the dispute does not cover. So:

* **Refund.** The refunded share of the pack's credits is removed from what is
  still unspent on it. Proportional, not refused: a partial refund takes
  `ceil(credits × amount_refunded / amount)`, both amounts the Charge's (tax
  included), capped at the unspent balance. Refunding the value of the unused
  balance, which terms §6.6 promises on request, therefore removes exactly the
  unused credits. Credits already spent are not clawed back and are reported
  as `already_spent`. `amount_refunded` is Stripe's running total, so the
  share is a target: a re-sent event removes nothing more.
* **Dispute opened.** The pack's unspent credits are **held** — not drawable,
  not removed — while the dispute is open.
* **Dispute closed.** `won`, or an inquiry closed without a chargeback
  (`warning_closed`: the funds never left), gives the held credits back. `lost`
  forfeits them. Any other status keeps them held and says so, because that
  is the one outcome that can still be undone by hand.

The charge is matched to a pack by its PaymentIntent id, which the pack's
ledger payment claim records as its settlement reference. A Charge (API
version 2026-08-26.dahlia) names no invoice and no subscription, and a
Dispute names no customer, so a **plan** invoice's charge cannot be matched
from the data this Worker is allowed to keep: it is acknowledged with
`action: unmatched` and its ids echoed for review, never guessed at. See
`docs/billing.md`.

Nothing here writes Workers KV. The ledger is the Durable Object.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

REFUNDED = "charge.refunded"
DISPUTE_CREATED = "charge.dispute.created"
DISPUTE_CLOSED = "charge.dispute.closed"
TYPES = frozenset({REFUNDED, DISPUTE_CREATED, DISPUTE_CLOSED})

#: Closed statuses that give held credits back. `warning_closed` is an inquiry
#: that never became a chargeback: the money stayed with us.
RESTORE_STATUSES = frozenset({"won", "warning_closed"})
FORFEIT_STATUSES = frozenset({"lost"})


def _id(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("id") or "")
    return "" if value is None else str(value)


def _int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _clock(now: datetime) -> str:
    moment = now if now.tzinfo else now.replace(tzinfo=UTC)
    return moment.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _review(obj: dict[str, Any], type_: str) -> dict[str, str]:
    """The ids an operator needs to find this payment in the Dashboard."""
    if type_ == REFUNDED:
        return {"charge": _id(obj.get("id")),
                "payment_intent": _id(obj.get("payment_intent")),
                "customer": _id(obj.get("customer"))}
    return {"dispute": _id(obj.get("id")), "charge": _id(obj.get("charge")),
            "payment_intent": _id(obj.get("payment_intent"))}


async def apply(type_: str, obj: dict[str, Any], *, ledger: Any,
                now: datetime) -> tuple[str, dict[str, Any]]:
    """Apply one verified reversal event. Returns (action, extra body fields).

    Raises `credits.StoreNotConfigured` when the ledger is not bound, so the
    webhook answers 503 and Stripe retries.
    """
    tx = _id(obj.get("payment_intent"))
    clock = _clock(now)
    if type_ == REFUNDED:
        amount = _int(obj.get("amount_captured")) or _int(obj.get("amount"))
        refunded = _int(obj.get("amount_refunded"))
        full = bool(obj.get("refunded")) or (amount > 0 and refunded >= amount)
        result = await ledger.refund(tx, amount, refunded, full, now=clock)
        if not result.found:
            return "unmatched", {"review": _review(obj, type_)}
        return ("refunded" if full else "refunded_partially"), {"credits": {
            "purchased": result.purchased,
            "refunded_share": result.refunded_share,
            "removed": result.removed,
            "already_spent": result.already_spent,
            "expired": result.expired,
            "pending_claim": result.pending,
        }}

    dispute_id = _id(obj.get("id"))
    status = str(obj.get("status") or "")
    if type_ == DISPUTE_CREATED:
        result = await ledger.hold(tx, dispute_id, now=clock)
        if not result.found:
            return "unmatched", {"review": _review(obj, type_)}
        return ("held" if result.held else "already_held"), {
            "credits": {"purchased": result.purchased, "held": result.held,
                        "pending_claim": result.pending},
            "dispute_status": status,
        }

    if status in RESTORE_STATUSES or status in FORFEIT_STATUSES:
        result = await ledger.end_hold(
            tx, dispute_id, status in RESTORE_STATUSES, now=clock)
        if not result.found:
            return "unmatched", {"review": _review(obj, type_)}
        if result.restored:
            action = "restored"
        elif result.forfeited:
            action = "forfeited"
        else:
            action = "already_closed"
        return action, {
            "credits": {"purchased": result.purchased, "restored": result.restored,
                        "forfeited": result.forfeited, "expired": result.expired,
                        "pending_claim": result.pending},
            "dispute_status": status,
        }
    return "held_for_review", {"review": _review(obj, type_), "dispute_status": status}
