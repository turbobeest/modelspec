# Billing: Stripe Checkout entitles a key (MODEL-73)

A human pays by card on Stripe-hosted Checkout and claims a working API key
at the tier mapped from the Price they bought. There is no console step after
payment. **The switch is off.** `BILLING_ENABLED` in
`api/worker/wrangler.jsonc` ships `"false"`. Nothing here runs until that
flips, and the secrets exist, in test mode.

What a paid month buys **today**: live rank access at the mapped tier's
limits (`subscriber` in `api/worker/tiers.json`). It does **not** buy the
policy-check determinations. Pricing copy must say that.

Seller: Sparks & Sawdust LLC. Card data never touches ModelSpec: Checkout is
hosted on Stripe.

## Endpoints

All on `https://api.modelspec.dev`. Flag off → `503 billing_not_enabled` after
a webhook signature still being checked.

| Method | Path | Who |
| --- | --- | --- |
| `POST` | `/v1/billing/checkout` | the buyer. Optional JSON `{"price_id": "price_…"}`; omitted, the sole mapped price is used. Returns `{url, session_id, tier, terms_url, what_you_buy}`. Redirect the browser to `url`. |
| `POST` | `/v1/billing/stripe-webhook` | Stripe. Raw body. `Stripe-Signature` required. |
| `GET` or `POST` | `/v1/billing/claim` | the buyer, once. `session_id` as query (`?session_id={CHECKOUT_SESSION_ID}`) or JSON. Mints the key and returns it **once**. |
| `POST` | `/v1/billing/rotate` | the buyer, authenticated by the current key (`Authorization: Bearer` or `X-API-Key`). Returns a new key once; the old key is then `403 key_revoked`. |

Checkout Session `success_url` is this Worker's claim path with
`{CHECKOUT_SESSION_ID}`. A later `GET` of that URL is the claim.

## Webhook

Verified in process: HMAC-SHA256 over `t.payload` with `STRIPE_WEBHOOK_SECRET`,
compared against every `v1` in `Stripe-Signature`. Timestamp must fall within
`billing.signature_tolerance_seconds` (configuration). Unsigned, wrong, or
stale events are `400 invalid_webhook_signature`. No Stripe SDK.

| Event | Action |
| --- | --- |
| `checkout.session.completed`, `checkout.session.async_payment_succeeded` | map the Price → tier; record the entitlement (subscription, customer, status, tier); link the session so claim can mint |
| `invoice.paid` | same entitlement if this subscription has none yet; otherwise restore the mapped tier (a failed renewal that later pays) |
| `invoice.payment_failed` | **immediate** downgrade to `billing.downgrade_tier` (`free`). No dunning window on our side. Stripe may still retry; a later `invoice.paid` restores. |
| `customer.subscription.deleted` | downgrade to free |
| `customer.subscription.updated` with `canceled` / `unpaid` / `incomplete_expired` | downgrade to free (expiry) |
| anything else | `200` `action: ignored` after the signature checks out |

The webhook never mints a key. A replay of the same `event.id` is `200`
`duplicate: true` and does not write a second entitlement. Subscription
identity is the second lock: checkout-then-invoice (or the reverse) shares
one entitlement; claim mints one key.

Unknown Price ids are `500 price_not_mapped` so Stripe retries until the
mapping exists. Add the id to `tiers.json` `billing.prices`; do not edit a
module.

## Configuration

`api/worker/tiers.json` (injected as `TIER_POLICY`, same as MODEL-69):

- `tiers.<name>.daily_limit` / `burst_limit` — the quota. `null` is unlimited.
- `billing.prices.<stripe_price_id>.tier` — Price → tier. Placeholders are
  marked `placeholder: true` and named `price_PLACEHOLDER_…`. No amount is in
  force.
- `billing.downgrade_tier` — where a failed or cancelled subscription lands.
- `billing.signature_tolerance_seconds`, `billing.event_ttl_seconds`
- `billing.terms_url` — linked from Checkout. The terms are still a draft
  (`docs/legal/terms-of-service.md`).

Changing a limit or a mapping is an edit to that file (or to `TIER_POLICY`).
`tests/test_billing.py` proves both.

The day-one mapped tier is `subscriber`: live data, **not** `paid: true`, so
`POST /v1/policy-check` still answers from the public export.

## Claim and rotation

The webhook writes the entitlement only. `GET`/`POST /v1/billing/claim` with
the Checkout session id confirms that session is linked to an active
entitlement, calls `access_keys.issue`, returns the plaintext **once**, and
stores only the SHA-256 hash. The session is then marked claimed. A second
claim is `410 claim_consumed` and does not mint a second key. A lost key is
recovered by rotation, not by claiming again.

If the webhook has not arrived, `409 claim_not_ready`: payment received, key
not ready, retry in a few seconds. Claim does not mint in that case.

Keys are stored hashed (`key:<sha256>`). No ACCESS record holds the key
value, before or after claim.

Rotation is authenticated by the current key. The old key is then
`403 key_revoked`.

## Downgrade window

**Immediate** on `invoice.payment_failed`, on `customer.subscription.deleted`,
and on expiry statuses above. Paid limits do not continue during Stripe's
retry window. A later successful `invoice.paid` restores the mapped tier on
the same key.

## Turning it on

Human steps. This repository does not create Stripe objects and does not call
Stripe's live API.

1. Stripe Dashboard, **test mode**. Seller account: Sparks & Sawdust LLC.
2. Product named for live rank access, not for compliance. One Price,
   recurring monthly. Copy the Price id (`price_…`) over
   `price_PLACEHOLDER_live_monthly` in `api/worker/tiers.json`. Keep
   `placeholder: false` once it is real.
3. Checkout → **Terms of service URL** =
   `https://modelspec.dev/legal/terms/` (required: we send
   `consent_collection[terms_of_service]=required`).
4. Developers → Webhooks → add
   `https://api.modelspec.dev/v1/billing/stripe-webhook`. Events: the table
   above. Copy the **test** signing secret (`whsec_…`).
5. API keys: a **restricted** test key with Checkout Sessions write is
   better than `sk_test_…`. Never a live key until Jamie says so.
6. `npx wrangler secret put STRIPE_SECRET_KEY` and
   `npx wrangler secret put STRIPE_WEBHOOK_SECRET` in the
   `modelspec-rank` Worker (test values only). Do not put either in git or in
   `wrangler.jsonc`.
7. ACCESS KV must exist (MODEL-69). Enforcement can stay off; a presented
   key is still checked.
8. Set `"BILLING_ENABLED": "true"` in `wrangler.jsonc` vars, regenerate
   `openapi.yaml`, merge. The deploy is push-to-main only.

If you will charge US or EU customers, consider Stripe Tax and an active
registration before going live; without a registration Stripe calculates
nothing. That is a Dashboard step, not this Worker.

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
No plaintext key is stored, even before claim.
