# Privacy statement

Version `1.1`, effective 2026-09-23. Adopted by Sparks and Sawdust LLC, which
operates the service. MODEL-70. Version 1.0 was adopted on 2026-09-19; what
changed in 1.1 is listed under [Changes](#changes).

This describes **what the service does today**, not what it is planned to do.
Every claim below names the file that makes it true, so it can be checked and so
it fails visibly when the code changes. Where something is built but not yet
switched on, it is marked **not yet live** and claims nothing.

## The short version

We do not receive your prompts, because the API has no field for them. We do not
proxy your model calls, so the content of your inference never reaches us. The
API keeps nothing from the content of a request: it reads your request, computes
an answer, returns it and forgets it. If you use an API key or buy credits, we
keep a hash of the key (never the key), its usage counters and credit balance,
and the Stripe identifiers of your purchase. Stripe, not us, handles your card.
Cloudflare, our infrastructure provider, records request metadata as platform
logs.

## What a request contains

`POST https://api.modelspec.dev/v1/rank` accepts a **profile**, not a prompt:

- `use_case` — which ranking profile to apply;
- `environment` — target hardware id, hosting mode, runtime;
- `constraints` — open weights or not, a cost ceiling, price sensitivity,
  whether to include rehosts;
- `limit`.

That is the whole surface (`api/worker/src/rank_service.py`). There is no field
for prompt text, document text, user content or an identifier of your end user,
so there is nothing of that kind for us to receive, log or store. Widening these
fields toward prompt text would be a breach of the commitment in the terms, not
a feature release.

A rank body is capped at 16 KB and larger ones are refused unread past that
point.

`POST https://api.modelspec.dev/v1/policy-check` accepts a **policy**: the
licence types, origin countries, processing regions and commercial-use
requirement you want checked, an optional name for the policy, and which models,
platforms and verdicts to return (`api/worker/src/policy_service.py`). It has no
field for prompt text either. Its body is capped at 256 KB.

The remote MCP server at `https://api.modelspec.dev/mcp` (`mcp/`) is stateless.
It passes each tool call through to those endpoints or to the public export,
forwarding the `Authorization` header you sent, and stores nothing.

## What we store

**Nothing from the content of your request.** The endpoints compute each answer
from your request, return it and forget the request: no body, no field of it and
no answer is written anywhere.

The Worker binds two KV namespaces (`api/worker/wrangler.jsonc`) and one
Durable Object, each described below. `DETERMINATIONS` holds **our own
research** — the licence and data-residency determinations the paid tier
serves — and the Worker only ever reads from it. There is no code path that
writes to it. No D1 database, R2 bucket, queue or analytics dataset is bound.

### The API-key store

A second KV namespace, `ACCESS`, is bound for API keys (MODEL-69) and purchases
(MODEL-73). It is wired with enforcement off (`ACCESS_ENFORCED` is `"false"`):
no key is required, and a request without one is answered as it always was, unmetered
and with nothing written. A request that presents a key is checked against the
store. A key is issued when a purchase is claimed. It holds these kinds of
record (`api/worker/src/access_keys.py`, `access_limits.py`,
`access_billing.py`):

- **A key record per issued key.** Stored under the SHA-256 hash of the key,
  never under the key, and the key value itself is never stored, logged or
  returned. The record holds the key's tier, who it was issued to (for a
  purchased key, the Stripe customer id), an optional label, when it was
  created, whether it is active, and a 12-character fingerprint (the start of
  that hash) that identifies the key in support and cannot be turned back into
  it. A billed key is minted at claim, shown once, and only this hash is
  written — never the key, including before claim. An authenticated Checkout
  binds payment to an already-issued key by that same hash; it does not mint
  another key and does not store the key value.
- **Two counters per key.** How many calls that key made in the current UTC day
  and in the current minute, named by the key's fingerprint and the window and
  holding a single number. They expire on their own: the minute counter after a
  minute, the daily one after two days.
- **A Stripe event id** (`event:<id>`). The event's id, type, the action we took
  and when, so a replayed webhook is a no-op. The event payload itself is not
  stored.
- **A subscription record** (`sub:<id>`). Stripe subscription id, customer id,
  Price id, plan name and monthly credit amount, the mapped tier, status, when
  it was created, and the key's fingerprint once the purchase is bound or
  claimed (never the key). No card number, no expiry, no CVC.
- **A Checkout session pointer** (`session:<id>`). Session id, optional
  subscription id, Stripe customer id, claimed flag, product kind, Price id,
  credit amount, and — when Checkout was authenticated — the SHA-256
  fingerprint of the existing key (never the key).
- **A keyref** (`keyref:<fingerprint>`). Fingerprint → subscription id, so
  rotation can find the billing row.

It holds no prompt, no request body, no field of a rank or policy-check
request, no answer, no IP address and no user-agent: our code reads none of
those into it. A request that presents no key, or a `test_` sandbox key, writes
nothing to it at all. Card data never reaches this store: Checkout is hosted on
Stripe.

### The credit ledger

A Durable Object class `CreditsObject`, bound as `CREDITS`
(`api/worker/wrangler.jsonc`), holds credit balances (MODEL-75, MODEL-93).
Credits are added only by a paid Stripe purchase, which runs only while
`BILLING_ENABLED` is on, or by an x402 payment, which runs only while
`X402_ENABLED` is on. It holds these kinds of record
(`api/worker/src/credits.py`):

- **A balance per holder.** The holder name is `key:` plus the SHA-256 hash of
  an API key, never the key. The record includes two integers for the live
  meter: how many credits remain to spend (`available`) and how many are
  reserved for an in-flight request (`reserved`). It also stores the remaining
  monthly allowance, and each pack grant as remaining credits, an expiry
  timestamp, a source (`pack` or `x402`), and the payment id that created it.
  Drawdown spends the monthly allowance first, then pack grants, oldest
  expiry first. It holds no request body, no prompt, no IP address, no
  user-agent and no payment signature.
- **A payment claim per settled payload or paid invoice.** Named by the
  payment id (the SHA-256 of an x402 nonce and signature, a Checkout session
  id, or a Stripe invoice id). The record is which holder was credited, how
  many credits, the kind (`pack` or `monthly`), and the settlement transaction
  hash or invoice id, so the same payload cannot credit twice. It holds the
  transaction hash the facilitator returned, not a wallet private key (there
  is none in this repository).
- **For a pack bought through Stripe, what has happened to that payment since.**
  The payment claim for a pack also records the Stripe PaymentIntent id that
  paid for it, so that a refund or a chargeback of that payment can find the
  credits it bought (MODEL-106). With it, the record keeps: whether the pack is
  still waiting to be claimed; how many of its credits a refund took back and
  how many a lost chargeback forfeited; how many an open chargeback is
  holding, and that chargeback's Stripe id; the ids of chargebacks already
  closed against it; and how many of its credits were reserved by a request
  in flight when a refund arrived. These are counts and Stripe ids. They hold
  no card detail, no customer name and no reason given for a refund or a
  chargeback.

It holds no prompt, no request body, no field of a request, no ranking or
policy answer, no IP address and no user-agent: our code reads none of those
into it. A request that presents no key, or a `test_` sandbox key, writes
nothing to it. A request that presents a live key reserves its cost against
that key's balance, which can create an empty balance record under the key's
hash even when nothing has been bought (`api/worker/src/x402.py`).

Workers KV is not this ledger. KV is eventually consistent and has no
compare-and-set, so it cannot keep a balance non-negative when two requests
race. The Durable Object is the serial mailbox that can.

The only other thing held between requests is a short-lived copy of our own
published catalogue, which is public data and contains nothing of yours
(`api/worker/src/entry.py`).

Our own code writes no log line about your request. There is no analytics call,
no telemetry beacon and no third-party tag on the API path.

## What Stripe holds

Purchases are made on Checkout pages hosted by Stripe
(`api/worker/src/billing_stripe.py`), which processes payments for Sparks &
Sawdust LLC. Stripe collects your card details and the contact and billing
details its Checkout form asks for, and holds them under its own privacy
policy. **We never receive your card number, expiry or CVC.** From Stripe we
keep only the identifiers listed under [the API-key store](#the-api-key-store):
event, customer, subscription, Checkout session, invoice and Price ids. We do
not copy your name, email address or billing address into our stores; they
remain in our Stripe account, where we can see them to handle a request from
you.

## What Cloudflare records

The API and both sites run on Cloudflare, and Cloudflare records request
metadata as any host does: the source IP address, timestamp, request method and
path, response status, and user-agent. Cloudflare **Workers observability is
enabled** on the API Worker and the MCP Worker (`api/worker/wrangler.jsonc`,
`mcp/wrangler.jsonc`), which retains invocation logs — request metadata,
outcome and any uncaught error — under Cloudflare's own retention. We use this
to tell whether the service is working.

We do not export it, join it to anything else, or use it to build a profile of
you. Cloudflare processes it under its own terms as our infrastructure provider.

## The websites

`modelspec.dev` and `benchgraph.dev` are static pages on Cloudflare Pages.

- **No cookies are set.** No analytics, no tag manager, no tracking pixel, no
  advertising network.
- **No account exists** to sign into, so there is nothing about you to hold.
- The downselect wizard ranks **in your browser**, from the same public JSON
  anyone can fetch. The choices you make in it are not sent anywhere and are not
  saved (`web3d/downselect.v2.html`).
- **No third-party requests:** pages load nothing from a third party. Web fonts
  and the graph explorer's libraries are served from our own origin rather than
  a CDN.

## Inference, and why there is nothing to say about it

We never sit between you and a model. We return a recommendation and hand off;
your calls go to the provider, gateway or local runtime directly. We do not see
your prompts, your completions, your token counts or your model traffic, and we
do not meter, resell or bill any of it. This is an architectural boundary rather
than a retention promise: there is no path by which that data could reach us.

The ModelSpec CLI, which runs on your machine, reads **which** provider API keys
are present in your environment and never their values. The keys stay with you.

## Not yet live

Named so that this statement can be checked against the code, and so that
nothing below is read as describing the service today:

- **x402 payments.** The rail (MODEL-75) is wired behind `X402_ENABLED`, which
  ships off: no request is charged by x402 and no x402 payment is credited.
  Coinbase's x402 facilitator, when the flag is on, receives the signed payment
  payload in order to verify and settle it; that payload is the caller's, not a
  store of ours. No private key for receiving funds is in this repository.
  `X402_PAY_TO` is an on-chain address in configuration, currently empty.
- **Outcome logging.** Not built. The service does not record what you chose,
  whether a recommendation worked, or anything about the result of acting on
  one. When it is built it will record the profile, the recommendation and the
  outcome — never prompt text — and this statement will be updated before it
  ships, not after.

## Your requests about your data

Without a key, the service holds nothing that identifies you, so there is
generally nothing to access, correct, export or delete. With a purchased key, we
hold the records described above, linked to your Stripe customer id. To ask
what we hold about you, or to have it corrected or deleted, write to
**sales@modelspec.dev**. Never send us your API key.

## Changes

A change to what the service records is a change to this statement, and it is
published here before the change ships. The version above is the one in force.

- **1.1, 2026-09-23.** The credit ledger now records, for each pack bought
  through Stripe, the PaymentIntent id that paid for it and what refunds and
  chargebacks have done to its credits (see *The credit ledger*), so that a
  refunded or charged-back pack no longer keeps its credits (MODEL-106). **This
  was published a few hours after the change shipped, not before it**, contrary
  to the rule above; it is recorded here rather than hidden.
- **1.0, 2026-09-19.** Adopted.
