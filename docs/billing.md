# Billing: Stripe Checkout funds credits (MODEL-73, MODEL-93)

A human pays by card on Stripe-hosted Checkout. Plans SET a monthly credit
allowance; packs ADD pack credits. A Checkout that presents a live API key
credits **that** key. An anonymous Checkout is claimed once and mints a key.
There is no console step after payment. **The switch is off.**
`BILLING_ENABLED` in `api/worker/wrangler.jsonc` ships `"false"`. Nothing
here runs until that flips, and the secrets exist, in test mode.

The unit is a **credit**.

Seller: Sparks & Sawdust LLC. Card data never touches ModelSpec: Checkout is
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

All on `https://api.modelspec.dev`. Flag off → `503 billing_not_enabled` after
a webhook signature still being checked. Billing paths are never HTTP 402.

| Method | Path | Who |
| --- | --- | --- |
| `POST` | `/v1/billing/checkout` | the buyer. JSON `{"price_id": "price_…"}` — **required**. Omitted is `400 invalid_request` naming the valid Price ids; the Worker never guesses a purchase. Optional `Authorization: Bearer <key>` binds the session to that key's SHA-256 fingerprint (the key itself is not stored). Unknown or revoked key: `401`, never anonymous. Returns `{url, session_id, kind, name, credits, terms_url, what_you_buy, applied_to}`. Redirect the browser to `url`. Plans use Checkout `mode=subscription`; packs use `mode=payment`. |
| `POST` | `/v1/billing/stripe-webhook` | Stripe. Raw body. `Stripe-Signature` required. |
| `GET` or `POST` | `/v1/billing/claim` | the buyer, once. `session_id` as query or JSON. Anonymous Checkout: mints the key and returns it **once**. Authenticated Checkout: does **not** mint; pack credits were already ADDed (or the plan attached) on payment, and the body says `credits added to your key` / `plan attached to your key`. |
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
  Sparks & Sawdust LLC ModelSpec sandbox; live ids replace them at launch
- `billing.downgrade_tier`, `signature_tolerance_seconds`, `event_ttl_seconds`
- `billing.terms_url`, `billing.cancel_url`

Changing a credit amount, a weight, burst, or a mapping is an edit to that
file. Tests prove a price/credit change needs no code change.

Shipped Prices (test mode, not live):

| Price id | Kind | Name | Credits | USD |
| --- | --- | --- | --- | --- |
| `price_1UHN91B565YfQifmuNBRGlZd` | plan | Solo | 4,000 / month | 10 |
| `price_1UHN9fB565YfQifm8NwFJSrD` | plan | Team | 30,000 / month | 50 |
| `price_1UHNBQB565YfQifmVDhOnO2I` | pack | 1,250-credit pack | 1,250 | 5 |
| `price_1UHNAHB565YfQifmlX8oeIx4` | pack | 7,500-credit pack | 7,500 | 25 |
| `price_1UHNAYB565YfQifmkxZKH5OW` | pack | 20,000-credit pack | 20,000 | 50 |
| `price_1UHNApB565YfQifm6k3NAign` | pack | 50,000-credit pack | 50,000 | 100 |

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

## Turning it on

Human steps. This repository does not create Stripe objects and does not call
Stripe's live API.

1. Stripe Dashboard, **test mode**. Seller account: Sparks & Sawdust LLC.
2. Two recurring monthly Prices (Solo $10 / 4,000 credits, Team $50 / 30,000)
   and four one-off Prices (packs $5 / $25 / $50 / $100). **Done in test
   mode** (2026-09-19); the ids are in `api/worker/tiers.json` with
   `placeholder: false`. Live ids replace them at launch.
3. Checkout → **Terms of service URL** =
   `https://modelspec.dev/legal/terms/` (the draft is
   `docs/legal/terms-of-service.md`; required: we send
   `consent_collection[terms_of_service]=required`).
4. Developers → Webhooks → add
   `https://api.modelspec.dev/v1/billing/stripe-webhook`. Events: the table
   above. **Done in test mode** (2026-09-19): destination `modelspec-billing`,
   API version `2026-08-26.dahlia`, snapshot payloads. Copy its **test**
   signing secret (`whsec_…`).
5. API keys: a **restricted** test key with Checkout Sessions write is
   better than `sk_test_…`. Never a live key until Jamie says so.
6. `npx wrangler secret put STRIPE_SECRET_KEY` and
   `npx wrangler secret put STRIPE_WEBHOOK_SECRET` in the
   `modelspec-rank` Worker (test values only). Do not put either in git or in
   `wrangler.jsonc`.
7. ACCESS KV must exist (MODEL-69). The CREDITS Durable Object is bound
   (MODEL-75). Enforcement can stay off; a presented key is still checked.
8. Set `"BILLING_ENABLED": "true"` in `wrangler.jsonc` vars, regenerate
   `openapi.yaml`, merge. The deploy is push-to-main only.

**Tax.** Sparks & Sawdust LLC applies one rule to every product, set first
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
| `BILLING_ENABLED` | `wrangler.jsonc` vars | the switch, default `"false"` |

No secret belongs in this repository. Tests sign fixtures with a throwaway
`whsec_test_…` string.

## Privacy

ACCESS record kinds this path writes are listed in
`docs/legal/privacy.md`. Card numbers never appear; Stripe is the processor.
No plaintext key is stored, even before claim. Monthly remaining, pack grants
and their expiry live in the CREDITS Durable Object, not in ACCESS.
