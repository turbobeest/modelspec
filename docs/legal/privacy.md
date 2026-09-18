# Privacy statement

**Status: DRAFT. Not adopted.** Drafted 2026-09-17 for MODEL-70, against the
code as it stood at that date.

This describes **what the service does today**, not what it is planned to do.
Every claim below names the file that makes it true, so it can be checked and so
it fails visibly when the code changes. Where something is built but not yet
switched on, it is marked **not yet live** and claims nothing.

## The short version

We do not receive your prompts, because the API has no field for them. We do not
proxy your model calls, so the content of your inference never reaches us. The
rank endpoint keeps no store of any kind: it reads your request, computes an
answer, returns it and forgets it. The one thing recorded about your call is
recorded by Cloudflare, our infrastructure provider, as platform request logs.

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

A body is capped at 16 KB and larger ones are refused unread past that point.

## What we store

**Nothing from your request.** The endpoints are stateless: each one reads your
request, computes an answer, returns it and forgets it.

The Worker binds exactly one store, a Cloudflare KV namespace called
`DETERMINATIONS` (`api/worker/wrangler.jsonc`). It holds **our own research** —
the licence and data-residency determinations the paid tier serves — and the
Worker only ever reads from it. There is no code path that writes to it, and
nothing from your request is written anywhere: no database, no object storage,
no queue and no analytics dataset is bound at all.

The only other thing held between requests is a short-lived copy of our own
published catalogue, which is public data and contains nothing of yours
(`api/worker/src/entry.py`).

Our own code writes no log line about your request. There is no analytics call,
no telemetry beacon and no third-party tag on the API path.

## What Cloudflare records

The API and both sites run on Cloudflare, and Cloudflare records request
metadata as any host does: the source IP address, timestamp, request method and
path, response status, and user-agent. Cloudflare **Workers observability is
enabled** on the rank endpoint (`api/worker/wrangler.jsonc`), which retains
invocation logs — request metadata, outcome and any uncaught error — under
Cloudflare's own retention. We use this to tell whether the service is working.

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
- **One third-party request:** page styling loads web fonts from Google Fonts
  (`fonts.googleapis.com`, `fonts.gstatic.com`), so your browser's IP address
  and user-agent reach Google when a page loads, as with any site that uses
  them. Nothing else on the page is third-party; the graph explorer's libraries
  are served from our own origin rather than a CDN.

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

- **API keys, tiers and rate limits.** The code exists
  (`api/worker/src/access*.py`, MODEL-69) but is **not wired into the deployed
  Worker**: the entry point does not call it. No key is required and none is
  issued today. When it is switched on, this statement must say what a key
  record holds before that happens. As designed, a key is stored as the SHA-256
  of its own bytes and identified in logs by a 12-character fingerprint, so the
  key value itself is never written down.
- **Payment.** No payment rail, checkout or billing is in operation, so no
  payment or billing data is collected or held. Payments would be handled by a
  payment processor, and that arrangement is not yet made.
- **Outcome logging.** Not built. The service does not record what you chose,
  whether a recommendation worked, or anything about the result of acting on
  one. When it is built it will record the profile, the recommendation and the
  outcome — never prompt text — and this statement will be updated before it
  ships, not after.
- **A policy-check endpoint.** Not merged.

## Your requests about your data

Since the service holds nothing that identifies you, there is generally nothing
to access, correct, export or delete. If you believe we hold something about
you, ask and we will look. Contact details to be filled in before adoption.

## Changes

A change to what the service records is a change to this statement, and it is
published here before the change ships. The version above is the one in force.
