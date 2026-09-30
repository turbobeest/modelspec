# Privacy statement

Version `1.3`, effective 2026-09-29. Adopted by Sparks and Sawdust LLC, which
operates the service. MODEL-70. Version 1.0 was adopted on 2026-09-19; what
changed since is listed under [Changes](#changes).

This describes **what the service does today**, not what it is planned to do.
Most claims below name the file that makes them true, so they can be checked and
so they fail visibly when the code changes. Where something is built but not yet
switched on, it is marked **not yet live**, and what is said of it describes the
service only once it is switched on.

## The short version

We do not ask for your prompts: no field of the rank, decide or policy-check API
takes one. The feedback endpoint has an optional free-text note, and asks you not
to put a prompt, a key or personal details in it. We do not proxy your model
calls, so the content of your inference never reaches us. The decision API keeps
nothing from the content of a request: it reads your request, computes an answer,
returns it and forgets it. The separate release-signal automation described below
stores authenticated public release notices while it processes them. Feedback you
choose to send about an answer is described below; storing it is not yet switched
on. If you use an API key or buy credits, we keep a hash of the key
(never the key), its usage counters and credit balance, and the Stripe identifiers
of your purchase. Stripe, not us, handles your card. Cloudflare, our infrastructure
provider, records request metadata as platform logs.

We want to know where our visitors come from and how they use the site, so we
can make a better product. That is why we run Cloudflare Web Analytics. It
tells us where visitors come from, which pages they use and how fast those
pages load. It does not tell us who you are: it sets no cookie, and nothing it
shows us identifies you.

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

A rank body is capped at 16 KB; a larger one is refused, and nothing of it is
kept.

`POST https://api.modelspec.dev/v1/policy-check` accepts a **policy**: the
licence types, origin countries, processing regions and commercial-use
requirement you want checked, an optional name for the policy, and which models,
platforms and verdicts to return (`api/worker/src/policy_service.py`). It has no
field for prompt text either. Its body is capped at 256 KB.

`POST https://api.modelspec.dev/v1/decide` accepts a **decision spec**
(`api/worker/src/decide_service.py`; the fields are defined in
`docs/decision-contract.md`): the capabilities you require, conditions on
catalogued facets, what to optimise, how much explanation to return and how many
results. A spec may also carry an **estate**: the providers, subscription plans
and devices you hold, named by catalogue ids. `POST /v1/compare` takes the same
spec and the id of an earlier published snapshot to compare it against. A field
the spec does not define is refused, not ignored. The contract's one free-text
field, `task`, is refused in this version: a spec that sets it is rejected, not
answered (`decision/contract.py`). `/v1/compare` reads only `spec` and
`compare_to` from its body and ignores anything else. Their bodies are capped at
64 KB.

`POST https://api.modelspec.dev/v1/feedback` accepts **feedback on an answer**:
a `rating` (reliable, unreliable, trustworthy, untrustworthy or confusing), a
`client` (agent, cli, mcp or page), and, optionally, the `decision_id` of the
answer, a `note` of up to 1,000 characters, what you were `trying_to_decide` in
up to 300 characters, the site `page` and the `template` you used
(`api/worker/src/feedback_service.py`). No key is needed and none is read. Any
other field is refused. Its body is capped at 4 KB. Before anything is kept,
text that looks like an email address, a phone number, an IP address, a card
number, a social security number or a credential is replaced by a placeholder,
and the query of a URL is removed; this catches the shape of such text, not its meaning, so please do
not send a prompt, a key or personal details in the note. The feedback endpoint
(MODEL-221) is disclosed here before it is deployed; until it is, `/v1/feedback`
answers 404 and the Feedback button described under *The websites* is not shown.

The remote MCP server at `https://api.modelspec.dev/mcp` (`mcp/`) is stateless.
It passes each tool call through to those endpoints or to the public export,
forwarding the `Authorization` header you sent, and stores nothing. Its feedback
tool forwards no `Authorization` header; it passes your address instead, used
only for the feedback limits described under *The feedback store*.

## What we store

**Nothing from the content of a rank, decide, compare or policy-check request.**
Those endpoints compute each answer from your request, return it and forget the
request: no body, no field of it and no answer is written anywhere. The
release-signal intake is the deliberately narrow exception described below, and
feedback, once its storage is switched on, is the other.

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

It holds no prompt, no request body, no field of a rank, decide, compare or
policy-check request, no answer, no IP address and no user-agent: our code reads none of
those into it. A rank, decide, compare or policy-check request that presents no
key, or a `test_` sandbox key, writes nothing to it. Card data never reaches this store: Checkout is hosted on
Stripe.

### The release-signal queue

The same `ACCESS` namespace can hold an authenticated **release signal** from
Grok Bot (MODEL-113). This automation ships off behind `SIGNALS_ENABLED`; while
that flag is false, the endpoint returns 404 and writes nothing. When Jamie
enables it, each pending record contains exactly the public model name, provider
name, first-seen X URL, timestamp, confidence and signal id submitted by the bot.
X is discovery only: none of these values becomes model-card evidence.

A second submitter, our primary-source release watcher (MODEL-216,
`release_signals/watch.py`), files the same fields for a release it finds on a
lab's or provider's public model page, a provider's public model list or a lab's
Hugging Face feed, with that page's URL as the first-seen URL. It authenticates
with the repository workflow's read key. For each of its
discoveries the queue also keeps a marker holding the signal id and timestamp,
so the same discovery is not queued twice; the marker is kept permanently. Its
discoveries are not model-card
evidence either.

After the repository workflow handles the signal, it stores an audit record with
that signal, the processing date, result and pull-request or issue URL. It also
schedules copies for re-checks after 1, 7 and 30 days. A pending or scheduled
record is deleted when acknowledged; the audit record remains so the automation's
actions can be reconstructed. The queue stores no prompt, completion, private X
message, API key, IP address or user-agent. `SIGNALS_ENABLED` must be on before intake accepts anything. Grok Bot's intake
also needs the HMAC write secret, and the watcher's needs the read key, which
also protects retrieval and acknowledgement by the repository workflow
(`api/worker/src/signals_service.py`).

### The feedback store

A third KV namespace, `FEEDBACK`, is to hold feedback on answers (MODEL-221). It
is **not yet live**: `FEEDBACK_ENABLED` is `"false"` and the namespace is not
bound, so feedback is checked, answered and not kept. While storage is off, the
only limit applied is a per-minute count kept in the running Worker's memory,
under a keyed hash of your address, and nothing is written anywhere.

When it is live, each piece of feedback is one record holding exactly: the day
it was received (`received_on`, never the time of day, which the record's expiry
does not reveal either), the `rating`, the `client`, and whichever of
`decision_id`, `page`, `template`, `note` and `trying_to_decide` you sent, after
the replacement described above, plus which kinds of text were replaced
(`redacted`). It holds no IP address, no key, no user-agent, no origin and no
time of day. Records are deleted automatically between 180 and 181 days after they are
received.
A `decision_id` identifies the question that was asked (it is derived from the question and the data it was answered from), not who asked it; anyone who
can guess the whole question can recompute it.

A recorded response gives you a random receipt; we keep only its SHA-256 hash.
Sending the receipt to `DELETE /v1/feedback` deletes the stored record at once.
It cannot reach a copy already made for the weekly review described below.

To limit abuse without keeping addresses, the Worker will then also count
feedback per address (for IPv6, per /64 network) per day under a name derived
from the address with a keyed hash (HMAC-SHA256 with a secret that is not
published) and the day, so the count cannot be turned back into the address or
linked across days, and it will keep a per-day total for the website and one for
the API, which name no address. These counts expire within two days. The
ModelSpec MCP server passes its caller's address to the Worker for these limits
only.

Once storage is live, once a week we will copy the feedback to our own computer,
count it by rating, page and template, and group repeated negative feedback into
issues in our private issue tracker (Linear), with the decision IDs and short
excerpts of the scrubbed `note` and `trying_to_decide` text. The issues are
drafted and filed with the help of an AI assistant, whose provider processes that
text under its terms as our processor. The weekly copies are deleted within 14
days; an issue keeps its excerpts until the issue is deleted. What we change
because of feedback is listed, in our own words and never quoting anyone, at
https://modelspec.dev/feedback/.

### The credit ledger

A Durable Object class `CreditsObject`, bound as `CREDITS`
(`api/worker/wrangler.jsonc`), holds credit balances (MODEL-75, MODEL-93).
Credits are added only by a paid Stripe purchase (a new purchase can start only
while `BILLING_ENABLED` is on; renewals and claims of purchases already paid are
credited while it is off), or by an x402 payment, which runs only while
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
into it. A rank, decide, compare or policy-check request that presents no key,
or a `test_` sandbox key, writes nothing to it. A request that presents a live key reserves its cost against
that key's balance, which can create an empty balance record under the key's
hash even when nothing has been bought (`api/worker/src/x402.py`).

Workers KV is not this ledger. KV is eventually consistent and has no
compare-and-set, so it cannot keep a balance non-negative when two requests
race. The Durable Object is the serial mailbox that can.

Apart from the per-minute feedback count described above, the only other things
held between requests are short-lived copies of our own catalogue, decision
snapshot and determinations, which contain nothing of yours
(`api/worker/src/entry.py`).

Our own code writes no log line about your request. There is no analytics call,
no telemetry beacon and no third-party tag on the API path. Cloudflare's
analytics script (see *The websites*) is inserted into the one HTML page the API
serves, the page that shows a purchased key, but that page's content security
policy stops a browser from loading it (`api/worker/src/billing_page.py`).

## What Stripe holds

Purchases are made on Checkout pages hosted by Stripe
(`api/worker/src/billing_stripe.py`), which processes payments for Sparks &
Sawdust LLC. Stripe collects your card details and the contact and billing
details its Checkout form asks for, and holds them under its own privacy
policy. **We never receive your card number, expiry or CVC.** From Stripe we
keep only the identifiers listed under *The API-key store* and *The credit
ledger*: event, customer, subscription,
Checkout session, invoice, PaymentIntent, chargeback and Price ids. We do
not copy your name, email address or billing address into our stores; they
remain in our Stripe account, where we can see them to handle a request from
you.

## What Cloudflare records

The API and the website run on Cloudflare, and Cloudflare records request
metadata as any host does: the source IP address, timestamp, request method and
path, response status, and user-agent. Cloudflare also asks your browser, in the
`NEL` and `Report-To` headers of its responses, to report to
`a.nel.cloudflare.com` any request to our site or API that fails to connect or
is answered with an error status; a report carries the address requested, the
referring page, the status and timings. It asks for no report of a request that
succeeds. Cloudflare **Workers observability is enabled** on the API Worker and the MCP Worker (`api/worker/wrangler.jsonc`,
`mcp/wrangler.jsonc`), which retains invocation logs — request metadata,
outcome and any uncaught error — under Cloudflare's own retention. We use this
to tell whether the service is working.

We do not export it, join it to anything else, or use it to build a profile of
you. Cloudflare processes it under its own terms as our infrastructure provider.

## The websites

`modelspec.dev` is a static site on Cloudflare Pages. `benchgraph.dev`
redirects to it.

- **No cookies are set.** No tag manager, no tracking pixel, no advertising
  network.
- **Cloudflare Web Analytics is on**, as described under *Cloudflare Web
  Analytics* below.
- **No account exists** to sign into, so there is nothing about you to hold.
- The **decide page** (`/decide/`) answers by sending the board's current spec
  to `POST /v1/decide`, described above, whenever it needs an answer, including
  when it first loads (`web/src/decide/adapter/hosted.ts`). That endpoint keeps
  nothing of it. The board itself, including the estate below, is kept in the
  page address after the `#`, which your browser does not send to any server; a
  link you copy or share from the page carries it.
- **Your browser keeps three things for the decide page**, in its
  `localStorage`: your light or dark theme (`modelspec-theme`,
  `web/src/decide/theme.ts`); the providers, plans and devices the board is
  set to hold (`modelspec-estate-v1`, `web/src/decide/facet-board/model.ts`),
  which leave your browser as the estate of a spec sent to `/v1/decide` and in
  the page address described above; and, if you press **Save and watch**, the
  spec and the alerts you ticked (`modelspec-alerts`, or
  `modelspec-sample-alerts` on a sample,
  `web/src/decide/components/Share.tsx`). The saved spec and alerts are never
  sent to us, and the service holds no watch list. Clearing this site's data
  in your browser removes all three.
- The **Feedback** button, on every page, and the "Was this answer reliable?"
  prompt on the decide page send what you enter to `/v1/feedback` only when you
  press Send. They set no cookie and store nothing in your browser.
- **One third-party request:** each page loads Cloudflare's analytics script,
  above, from `static.cloudflareinsights.com`, and pages load nothing else from
  a third party. Web fonts and the graph explorer's libraries are served from
  our own origin rather than a CDN.

### Cloudflare Web Analytics

We want to know where our visitors come from and how they use the site, so we
can make a better product. That is why we run Cloudflare Web Analytics. It
tells us where visitors come from, which pages they use and how fast those pages
load. It does not tell us who you are.

Cloudflare inserts its analytics script into each page of the site as it serves
the page; the script is not in our code. Your browser loads it from
`static.cloudflareinsights.com`, a Cloudflare host, and it sends to
`modelspec.dev/cdn-cgi/rum`, which Cloudflare answers: the page's address
without its query string or the part after the `#`; the page you came from,
shortened the same way; a random identifier made afresh for that one page load;
your browser's make and version and your operating system's version; and how
quickly the page loaded and responded, naming the page element involved in the
slowest paint, layout shift or interaction. The script sets no cookie, uses no
other storage in your browser and sends no identifier that outlasts the page
load, so nothing it sends follows you from visit to visit or from site to site.
Cloudflare also receives the request metadata described under *What Cloudflare
records*, as for any request.

From this, Cloudflare shows us counts of page views and visits and page-load
times, by page, referrer, country, browser, operating system and device type.
Web Analytics never shows us an IP address, and nothing it shows us identifies
you or any customer. We do not export it, join it to anything else, or use it to
build a profile of you. Cloudflare processes this data for us, as our processor,
under its own terms. Cloudflare's own description of Web Analytics and its
privacy is at
[cloudflare.com/web-analytics](https://www.cloudflare.com/web-analytics/).

## Inference, and why there is nothing to say about it

We never sit between you and a model. We return a recommendation and hand off;
your calls go to the provider, gateway or local runtime directly. We do not see
your prompts, your completions, your token counts or your model traffic, and we
do not meter, resell or bill any of it. This is an architectural boundary rather
than a retention promise: there is no path by which that data could reach us.

The ModelSpec CLI, which runs on your machine, reads none of your provider API
keys. They stay with you.

From the first CLI release after 0.2.0, and in the repository's source since
2026-09-29, the CLI can also keep a log of outcomes
on your machine: whether you adopted a decision and whether the task succeeded.
It records **nothing until you turn it on** with `modelspec outcome enable`,
which shows you every field it records and asks you to agree
(`cli/modelspec/outcome.py`, `docs/outcome-privacy.md`). The log lives under
`~/.modelspec/`, or `$MODELSPEC_HOME` if you set it. It holds identifiers, catalogue names, fixed-choice results, rounded numbers,
the minute each record was made and the CLI's version, and no free text.
**It never leaves your machine:** no `outcome` command opens a network
connection, and we never receive the log. `modelspec outcome disable --delete`
stops recording and deletes it.

## Not yet live

Named so that this statement can be checked against the code, and so that
nothing below is read as describing the service today:

- **x402 payments.** The rail (MODEL-75) is wired behind `X402_ENABLED`, which
  ships off: no request is charged by x402 and no x402 payment is credited.
  Coinbase's x402 facilitator, when the flag is on, receives the signed
  payment payload in order to verify and settle it; that payload is the
  caller's, not a store of ours. No private key for receiving funds is in this
  repository. `X402_PAY_TO` is an on-chain address in configuration, currently
  empty. This describes the production service at `api.modelspec.dev`. A
  separate staging copy of the API, on a `workers.dev` address that the site
  never calls, runs with x402 on, on a test network, for testing; a request
  sent to it directly can be metered as described next. Turning x402 on would
  also change two things this statement says today, and each has to be settled
  before it is turned on. A request from a browser on this site that presents
  no key would be metered in `ACCESS`, under counters named from the SHA-256
  of your IP address (`_site_free_visitor` in `api/worker/src/entry.py`). An
  unsalted hash of an IP address can be reversed by trying every address, so
  it is a pseudonymous address, not an anonymous one; a keyed or rotating
  scheme replaces it, and this statement is revised, before x402 is switched
  on. And a payment made without a key would be recorded in the credit ledger
  under the paying wallet's public address, with the credits it bought, which
  are spent at once.
- **Outcome logging by the service.** Not built. The service does not receive or
  record what you chose, whether a recommendation worked, or anything about the
  result of acting on one. The CLI's local log (see *Inference, and why there is nothing to say
  about it*) is not sent to us, and uploading it is designed but not built
  (`docs/design/outcome-upload.md`). The feedback described under
  *The feedback store* is separate: a rating you choose to
  send, with optional text. When upload is built it will send only records you
  choose to upload, under a consent of its own, and never prompt text, and this
  statement will be updated before it ships, not after.

## Your requests about your data

Without a key, the service holds nothing that identifies you, so there is
generally nothing to access, correct, export or delete. With a purchased key, we
hold the records described above, linked to your Stripe customer id. To ask
what we hold about you, or to have it corrected or deleted, write to
**sales@modelspec.dev**. Never send us your API key.

Feedback is not linked to you. To delete a piece of feedback, send its receipt
to `DELETE /v1/feedback`, or write to us with it.

## Changes

A change to what the service records is a change to this statement, and it is
published here before the change ships. The version above is the one in force.

- **1.3, 2026-09-29.** Brought the statement back in line with the service.
  Described `POST /v1/decide` and `/v1/compare`, their fields and their 64 KB
  cap, and what the decide page sends to them. Replaced the retired downselect
  wizard with the decide page, and disclosed the three things it keeps in your
  browser's `localStorage`. Said that `benchgraph.dev` now redirects to
  `modelspec.dev`, and that Cloudflare asks browsers to report failed
  connections to it. Disclosed the primary-source release watcher as a second
  submitter to the release-signal queue, and the duplicate marker it keeps
  (MODEL-216). Described the CLI's opt-in outcome log, which stays on your
  machine (MODEL-211), and narrowed "Outcome logging" under *Not yet live* to
  the service and to upload. Under *Not yet live*, disclosed that x402, if
  turned on as built, would meter keyless browser requests under an unsalted
  hash of the IP address and record keyless payments under the paying wallet's
  address, and that the first is replaced before x402 is turned on. Disclosed
  the feedback endpoint before it is deployed, with its storage not yet live:
  the fields it accepts, what a record would hold, the 180-day retention,
  deletion by receipt, the keyed per-day abuse counter and the weekly review
  into our issue tracker (MODEL-221). Corrected statements that had gone stale:
  a rank body is measured after it is read; the CLI reads none of your provider
  API keys; which requests write nothing to the key store and the credit ledger;
  that Stripe renewals and claims are still credited while `BILLING_ENABLED` is
  off; which Stripe identifiers we keep; what the Worker holds in memory between
  requests; which intake needs which secret; and that not every claim names a
  file. Disclosed Cloudflare Web Analytics, which Cloudflare inserts into our web
  pages: why we run it, what its script sends, what Cloudflare shows us from it,
  and that the pages' one third-party request is that script (MODEL-236).
- **1.2, 2026-09-26.** Disclosed the release-signal queue before it is enabled:
  the public release fields it stores, its processing audit, its 1-, 7- and
  30-day re-check records, and its `SIGNALS_ENABLED` switch (MODEL-113).

- **1.1, 2026-09-23.** The credit ledger now records, for each pack bought
  through Stripe, the PaymentIntent id that paid for it and what refunds and
  chargebacks have done to its credits (see *The credit ledger*), so that a
  refunded or charged-back pack no longer keeps its credits (MODEL-106). **This
  was published a few hours after the change shipped, not before it**, contrary
  to the rule above; it is recorded here rather than hidden.
- **1.0, 2026-09-19.** Adopted.
