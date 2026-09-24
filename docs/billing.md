# Billing: Stripe Checkout funds credits (MODEL-73, MODEL-93)

A human pays by card on Stripe-hosted Checkout. Plans SET a monthly credit
allowance; packs ADD pack credits. A Checkout that presents a live API key
credits **that** key. An anonymous Checkout is claimed once and mints a key.
There is no console step after payment. **The switch is off** (2026-09-24,
holding mode: see [`handoff/holding-mode.md`](handoff/holding-mode.md)).
`BILLING_ENABLED` in `api/worker/wrangler.jsonc` is `"false"`.

**What the switch gates: Checkout, and nothing else.** With it off,
`POST /v1/billing/checkout` (JSON and the `/pricing` form post) answers
`503 billing_not_enabled` before any call to Stripe, so no new purchase can
start. The webhook, claim and rotation keep answering, because each one
serves money that has already moved: a pack paid for before the flag went off
is still granted and claimed, an existing plan's renewal is still credited,
and a refund or chargeback still takes back (or holds) the pack's credits.
Existing keys and their credits keep working on `/v1/rank` and
`/v1/policy-check`; the ledger never reads this flag. Until 2026-09-24 the
flag also refused the webhook, which was harmless before the first sale and
would have kept a refunded pack's credits after it.

The unit is a **credit**.

Seller: Sparks and Sawdust LLC. Card data never touches ModelSpec: Checkout is
hosted on Stripe.

## What a funded key buys

A key with remaining credits receives the paid answer, including cited
commercial-use and data-residency determinations. Only a successful result
draws credits (4xx / 5xx / no-match cost nothing). Draw order: monthly
allowance first, then pack credits, oldest expiry first. Weights live in
`api/worker/tiers.json`: rank = 1 credit, policy-check = 5 credits.

A key with zero remaining credits is not an error: it receives the free-tier
answer (10 rank/day, 5/min, no determinations) plus a `credits.exhausted`
field naming where to buy. Paid keys have no daily cap; the burst limit is
configuration (`credits.burst_limit`, 60/min as shipped).

Cancellation, failed payment, or expiry **zeros the monthly allowance at
once**. Pack credits are unaffected. That is MODEL-73's immediate-downgrade
semantics, applied to the monthly bucket only.

Enterprise is not a Price. Contact sales@modelspec.dev.

## Endpoints

All on `https://api.modelspec.dev`. Flag off → `503 billing_not_enabled` on
checkout only; the other three answer as usual. Billing paths are never HTTP 402.

| Method | Path | Who |
| --- | --- | --- |
| `POST` | `/v1/billing/checkout` | the buyer. JSON `{"price_id": "price_…"}` — **required**. Omitted is `400 invalid_request` naming the valid Price ids; the Worker never guesses a purchase. Optional `Authorization: Bearer <key>` binds the session to that key's SHA-256 fingerprint (the key itself is not stored). Unknown or revoked key: `401`, never anonymous. Returns `{url, session_id, kind, name, credits, terms_url, what_you_buy, applied_to}`. Redirect the browser to `url`. Plans use Checkout `mode=subscription`; packs use `mode=payment`. **Form variant (MODEL-105):** the buy buttons on `/pricing` post `application/x-www-form-urlencoded` `price_id=price_…`; the answer is `303 See Other` with `Location:` the Stripe Checkout URL. A form post is always anonymous Checkout (claim mints a key). An unknown or placeholder Price is refused, never redirected. A body that parses as JSON stays the JSON call whatever its content type. |
| `POST` | `/v1/billing/stripe-webhook` | Stripe. Raw body. `Stripe-Signature` required. |
| `GET` or `POST` | `/v1/billing/claim` | the buyer, once. `session_id` as query or JSON. Anonymous Checkout: mints the key and returns it **once**. Authenticated Checkout: does **not** mint; pack credits were already ADDed (or the plan attached) on payment, and the body says `credits added to your key` / `plan attached to your key`. **Browser (MODEL-105):** when `Accept` prefers `text/html` over JSON, the same outcome is a static page (`src/billing_page.py`: no script, CSP `default-src 'none'`, `no-store`) that shows the key once and says to copy it now. Without that preference (`curl`, agents, no `Accept`) the JSON is byte-identical. |
| `POST` | `/v1/billing/rotate` | the buyer, authenticated by the current key. Returns a new key once; the old key is then `403 key_revoked`. Remaining credits move with the new key. |

Checkout Session `success_url` is this Worker's claim path with
`{CHECKOUT_SESSION_ID}`. `cancel_url` is `https://modelspec.dev/pricing`.

## Webhook

Verified in process: HMAC-SHA256 over `t.payload` with `STRIPE_WEBHOOK_SECRET`,
compared against every `v1` in `Stripe-Signature`. Timestamp must fall within
`billing.signature_tolerance_seconds` (configuration). Unsigned, wrong, or
stale events are `400 invalid_webhook_signature`. No Stripe SDK.

| Event | Action |
| --- | --- |
| `checkout.session.completed` / `async_payment_succeeded`, `mode=subscription` | map the Price → plan; record the entitlement; SET monthly to the plan amount. If Checkout metadata carries `modelspec_key_fingerprint`, attach and SET on that existing key. Otherwise pending until claim mints. |
| `checkout.session.completed` / `async_payment_succeeded`, `mode=payment` | map the Price → pack. Fingerprint present: ADD pack credits to that key immediately (claim is confirmation, not a mint). Anonymous: link the session so claim can mint and ADD. |
| `invoice.paid` | SET monthly to the plan amount (reset, no rollover). Restores a previously failed subscription. Fingerprint on the subscription metadata attaches to that existing key the same way Checkout metadata does. |
| `invoice.payment_failed` | **immediate** zero of monthly; key's access row to `billing.downgrade_tier` (`free`). Packs stay |
| `customer.subscription.deleted` | same as failed payment |
| `customer.subscription.updated` with `canceled` / `unpaid` / `incomplete_expired` | same |
| `charge.refunded` | a **pack**: remove the refunded share of its **unspent** credits (`refunded` / `refunded_partially`). Spent credits stay spent. See [Refunds and disputes](#refunds-and-disputes) |
| `charge.dispute.created` | a **pack**: **hold** its unspent credits while the dispute is open (`held`) |
| `charge.dispute.closed` | `won` or `warning_closed`: give the held credits back (`restored`). `lost`: forfeit them (`forfeited`). Any other status: stay held (`held_for_review`) |
| a refund or dispute of a charge no pack claims (a plan invoice, a pack bought before MODEL-106) | `200` `action: unmatched`, with a `review` object naming the charge, PaymentIntent and customer. Nothing changes |
| anything else | `200` `action: ignored` after the signature checks out |

The webhook never mints a key. A replay of the same `event.id` is `200`
`duplicate: true`. Subscription identity is the second lock: checkout-then-invoice
(or the reverse) shares one entitlement. Anonymous claim mints one key;
authenticated payment credits the bound key and mints none.

Unknown Price ids are `500 price_not_mapped` so Stripe retries until the
mapping exists. Add the id to `tiers.json` `billing.prices`; do not edit a
module.

## Configuration

`api/worker/tiers.json` (injected as `TIER_POLICY`):

- `credits.weights.rank` / `credits.weights.policy-check` — credits drawn on a
  successful result
- `credits.burst_limit` — per-minute burst for a funded key
- `credits.pack_expiry_days` — pack and x402 top-up expiry (365 as shipped)
- `billing.prices.<stripe_price_id>` — `{kind: plan\|pack, credits, name, usd,
  tier, placeholder}`. The ids below are **Stripe test mode** Prices on the
  Sparks and Sawdust LLC ModelSpec **live** account. The sandbox ids they
  replaced are in the git history of this file
- `billing.downgrade_tier`, `signature_tolerance_seconds`, `event_ttl_seconds`
- `billing.terms_url`, `billing.cancel_url`

Changing a credit amount, a weight, burst, or a mapping is an edit to that
file. Tests prove a price/credit change needs no code change.

Shipped Prices (**live**, Sparks and Sawdust LLC ModelSpec account `acct_1UHN0tBPydVRHUBj`, 2026-09-19):

| Price id | Kind | Name | Credits | USD |
| --- | --- | --- | --- | --- |
| `price_1UHRwmBPydVRHUBjqhKcx8xV` | plan | Solo | 4,000 / month | 10 |
| `price_1UHRwmBPydVRHUBjBYfcWhkW` | plan | Team | 30,000 / month | 50 |
| `price_1UHRwmBPydVRHUBjMFS5bDPD` | pack | 1,250-credit pack | 1,250 | 5 |
| `price_1UHRwmBPydVRHUBjN2mEnzdD` | pack | 7,500-credit pack | 7,500 | 25 |
| `price_1UHRwmBPydVRHUBj08ctUUjN` | pack | 20,000-credit pack | 20,000 | 50 |
| `price_1UHRwnBPydVRHUBjhRYBngwH` | pack | 50,000-credit pack | 50,000 | 100 |

The ledger is the MODEL-75 CREDITS Durable Object, keyed `key:` + SHA-256 of
the API key. See [`x402.md`](x402.md).

## Claim and rotation

The webhook writes the entitlement (and, for a bound or claimed key, the
ledger) only. `GET`/`POST /v1/billing/claim` with the Checkout session id
confirms that session is linked.

- **Anonymous Checkout** (no live key on `POST /v1/billing/checkout`): claim
  calls `access_keys.issue`, returns the plaintext **once**, and stores only
  the SHA-256 hash. Pack credits are granted at claim.
- **Authenticated Checkout** (a valid live key was presented): claim does not
  mint. A pack's credits were ADDed to that key on payment; a plan's monthly
  allowance was SET on that key on payment. The success page (this endpoint)
  returns `applied_to: existing_key` and `credits added to your key` or
  `plan attached to your key`. The key is not in the body.

A pack refunded (or its dispute lost) in full before anyone claimed it is
`410 purchase_refunded`: no key is minted. A pack partly refunded before
claim grants what the refund left.

A second claim is `410 claim_consumed`. A lost key is recovered by rotation,
not by claiming again. A presented unknown or revoked key on checkout is
`401`; it is never treated as anonymous.

If the webhook has not arrived, `409 claim_not_ready`: payment received, key
not ready, retry in a few seconds.

Keys are stored hashed (`key:<sha256>`). No ACCESS record holds the key
value, before or after claim. Checkout metadata and the session record store
only the fingerprint when a purchase is bound to an existing key. Rotation
moves the credit balance to the new key; the old key is `403 key_revoked`.

## Downgrade window

**Immediate** on `invoice.payment_failed`, on `customer.subscription.deleted`,
and on expiry statuses above: monthly allowance goes to 0. Pack credits
continue until they expire. A later successful `invoice.paid` SETS monthly
again on the same key.

## Refunds and disputes

MODEL-106. Found in the live $5 test on 2026-09-23: before this, a refunded or
charged-back pack kept its credits. `api/worker/src/billing_reversals.py`
decides; the ledger (`credits.LedgerState.refund`, `hold`, `end_hold`) acts.

**What they act on.** Credits, because credits are the paid entitlement: a key
gets the paid answer whenever the ledger can reserve the call's weight, and
the free answer when it cannot, whatever tier its record names. Moving the
key's tier row alone would not stop a funded key, and zeroing the whole key
would also take credits from purchases the refund or dispute does not cover.
So each acts on **the one pack it paid for**, and on nothing else on the key.

**How a charge finds its pack.** A `charge.*` event names a Charge's
PaymentIntent (`pi_…`), never a Checkout session. A payment-mode Checkout
Session does name its PaymentIntent, so `checkout.session.completed` now
records it as the pack's ledger payment claim `tx` (its settlement reference),
before the key exists if Checkout was anonymous (the claim is then `pending`,
with no holder, until claim grants it). The refund or dispute finds that claim,
and the claim's grant wherever the credits now live, rotation included. No new
ACCESS record kind: the privacy statement lists those, and this needs none.

**A refund** (`charge.refunded`):

- Takes back `ceil(credits × amount_refunded ÷ amount)` of the pack's
  credits, from what is still unspent on it. Both amounts are the Charge's,
  tax included. A full refund (`refunded: true`) takes back all of it.
- **Spent credits are not clawed back.** The outcome reports
  `credits.removed` and `credits.already_spent` (and `expired`, for a pack past
  its 12 months). A request in flight during the refund counts as spent; if it
  then fails, its reserved credits go to the refund, not back to the key.
- **Partial refunds are proportional, not refused.** The share is measured
  against the credits the pack was sold with, not against what is left, so
  refunding the value of the unused balance (terms §6.6: refunds of unused
  prepaid balance on request) removes exactly the unused credits: 250 unused
  credits of a 1,250-credit pack are 20 % of the price, and a refund of 20 %
  removes 250. Rounding is up, so a fraction of a credit never stays with a
  refunded buyer. A refund of the pre-tax price only is a little under the
  whole, and leaves the rounding remainder on the key.
- `amount_refunded` is Stripe's running total, so the share is a target: a
  second partial refund takes the difference, and a re-sent event takes
  nothing more.
- Refunded before claim: claim grants what is left, or answers
  `410 purchase_refunded` and mints no key if nothing is.

**A dispute** (`charge.dispute.created`, `charge.dispute.closed`):

- Opened: the pack's unspent credits are **held**: not drawable, not removed.
  Other credits on the key (the monthly allowance, other packs) are
  untouched. A request in flight that fails returns its credits to the hold.
- Closed `won`, or `warning_closed` (an inquiry that never became a
  chargeback; the money never left): the held credits come back, unless the
  pack expired meanwhile.
- Closed `lost`: the held credits are forfeited. What was spent before the
  dispute stays spent.
- Closed with any other status: the credits stay held and the outcome says
  `held_for_review`, because holding is the one state that can still be
  undone by hand.
- Disputed before claim: claim grants the pack already held.

**Plans are not matched.** A dahlia Charge names no invoice and no
subscription, and a Dispute names no customer, so nothing this Worker is
allowed to keep links a plan invoice's charge to a key. Matching one needs a
customer → subscription (or PaymentIntent → subscription) index: a new ACCESS
record kind, which the adopted privacy statement does not list.

**Decided (Jamie, 2026-09-23, MODEL-107): plan refunds stay manual.** No such
index is kept, and the privacy statement is not amended for it. A plan refund
or dispute is `action: unmatched`, visible for review, and **refunding a plan
means cancelling it**:

1. Refund the invoice in the Stripe Dashboard.
2. In the same sitting, **cancel the subscription immediately** (not at period
   end). `customer.subscription.deleted` zeros the monthly allowance at once,
   as above.
3. For a chargeback on a plan, cancel the subscription the same way once the
   dispute opens.

Plans are $10 and $50 a month, so plan refunds are expected to be rare.
Automate them — the index, and privacy statement 1.2 — only if that stops
being true.

**Idempotent twice over.** The event id is remembered like every other event.
Underneath, each ledger operation is idempotent on its own: the refund share is
a target, a hold is keyed by the dispute id, and a closed dispute id is
remembered on the claim, so neither a KV miss on the event record nor Stripe
re-sending under a new event id changes a balance twice.

**Purchases before MODEL-106** recorded the Checkout session, not the
PaymentIntent, as the pack's `tx`. Their refunds are `unmatched`; remove their
credits by hand if one is refunded.

## Turning it on

Human steps. This repository does not create Stripe objects and does not call
Stripe's live API.

1. Stripe Dashboard, **test mode**. Seller account: Sparks and Sawdust LLC.
2. Two recurring monthly Prices (Solo $10 / 4,000 credits, Team $50 / 30,000)
   and four one-off Prices (packs $5 / $25 / $50 / $100). **Done in test
   mode** (2026-09-19); the ids are in `api/worker/tiers.json` with
   `placeholder: false`. Live ids replace them at launch.
3. Checkout → **Terms of service URL** =
   `https://modelspec.dev/legal/terms/` (adopted 2026-09-19; source
   `docs/legal/terms-of-service.md`; required: we send
   `consent_collection[terms_of_service]=required`).
4. Developers → Webhooks → add
   `https://api.modelspec.dev/v1/billing/stripe-webhook`. Events: the table
   above. **Done in test mode** (2026-09-19): destination `modelspec-billing`,
   API version `2026-08-26.dahlia`, snapshot payloads. Copy its **test**
   signing secret (`whsec_…`). The full list, which both the live and the
   sandbox destination must carry (`billing.HANDLED_TYPES`):
   `checkout.session.completed`, `checkout.session.async_payment_succeeded`,
   `invoice.paid`, `invoice.payment_failed`, `customer.subscription.deleted`,
   `customer.subscription.updated`, and since MODEL-106 `charge.refunded`,
   `charge.dispute.created`, `charge.dispute.closed`.
5. API keys: a **restricted** test key with Checkout Sessions write is
   better than `sk_test_…`. Never a live key until Jamie says so.
6. `npx wrangler secret put STRIPE_SECRET_KEY` and
   `npx wrangler secret put STRIPE_WEBHOOK_SECRET` in the
   `modelspec-rank` Worker (test values only). Do not put either in git or in
   `wrangler.jsonc`.
7. ACCESS KV must exist (MODEL-69). The CREDITS Durable Object is bound
   (MODEL-75). Enforcement can stay off; a presented key is still checked.
8. Set `"BILLING_ENABLED": "true"` in `wrangler.jsonc` vars, regenerate
   `openapi.yaml`, merge. The deploy is push-to-main only. At relaunch this is
   the step that reopens Checkout; do it together with `SITE_MODE=live`, since
   the buy buttons live on `/pricing`, which holding mode does not publish.

**Tax.** Sparks and Sawdust LLC applies one rule to every product, set first
for dev-mux: Stripe Tax on every Checkout (`automatic_tax[enabled]=true`,
`billing_address_collection=required`). In the Dashboard: head office Rhode
Island; preset product category *Electronically Supplied Services*; tax
behaviour Automatic (exclusive for USD); one registration, Rhode Island. With
no active registration Stripe computes zero tax without an error, so the
registration is what turns collection on. dev-mux's reasoning and the
accountant's answer: `dev-mux/docs/ri-sales-tax-decision.md`.

## Secrets

| Name | Where | Used for |
| --- | --- | --- |
| `STRIPE_SECRET_KEY` | Wrangler secret | creating a Checkout Session |
| `STRIPE_WEBHOOK_SECRET` | Wrangler secret | verifying `Stripe-Signature` |
| `BILLING_ENABLED` | `wrangler.jsonc` vars | whether Checkout is open; `"false"` while the sites are in holding mode |

No secret belongs in this repository. Tests sign fixtures with a throwaway
`whsec_test_…` string.

## Privacy

ACCESS record kinds this path writes are listed in
`docs/legal/privacy.md`. Card numbers never appear; Stripe is the processor.
No plaintext key is stored, even before claim. Monthly remaining, pack grants
and their expiry live in the CREDITS Durable Object, not in ACCESS.
