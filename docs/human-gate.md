# Manual decision gate (MODEL-248)

`HUMAN_GATE_ENABLED` ships `false` in production and `true` in isolated staging
for verifying the gate on Cloudflare before production. Off preserves
the existing access and x402 paths. On, keyless `/v1/decide` calls from the
three existing site origins need a fresh Turnstile token in the
`X-ModelSpec-Turnstile` header. The decision Spec, response body and contract
versions do not change. Other keyless callers use the paid x402 path when
that flag is on, or receive a refusal when it is off. Funded keyed calls retain
their existing access and billing behavior. Unfunded keys receive 402 on
`/v1/decide` while the human gate is on, even when x402 is off, so presenting an
empty key cannot bypass the human gate.

The `human_*` refusals are access/transport errors outside the decision
contract, routed like `origin_not_allowed`. They do not widen its closed
error-code enum or change its version. See [access errors](decide-api.md#access-errors).

## Admission and storage

Siteverify must return boolean `success: true`, the hostname matching the
allowed request origin, and `action: decide`. Tokens expire after five minutes
and Siteverify refuses replay. A verification request has a ten-second network
timeout. The optional `remoteip` parameter is omitted. No token is logged or
persisted by this code. See [Cloudflare's validation contract](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/).

The `HUMAN_GATE` binding points to `HumanGateObject`, with one instance named
by a daily HMAC visitor ID. For this gate only, IPv6 addresses are normalised
to their /64 network before deriving the ID. IPv4 stays as supplied, and the
MODEL-241 keyless meter keeps its existing identity behavior. The object uses
synchronous SQLite reads and writes without yielding during admission. The
caps are 20 admitted lookups per UTC day and three in a rolling 60 seconds. Admission consumes a lookup
even if the decision engine subsequently refuses the Spec or fails. Failed
verification and cap refusals do not consume a lookup. This prevents concurrent
or deliberately invalid requests from obtaining more answers than the cap.

The state contains a UTC day, admitted count, recent timestamps, keyed Spec
fingerprints and a suspicion expiry. Fingerprints are scoped to the daily
visitor ID and exclude `explain`, `limit`
and `snapshot`. Every admitted lookup counts toward interval detection,
regardless of whether its fingerprint matches an earlier lookup.
It retains ten minutes of lookup history on the next admission. Five lookups
with four nearly equal intervals within ten minutes set a ten-minute refusal.
Distinct Specs do not trigger a refusal. Equal means the interval spread
is at most 5% of their mean or 250 milliseconds, whichever is larger, with
intervals at least one second long. Suspicion persists through later uneven
requests until it expires. Detection is per visitor, not a shared ASN cap.

An alarm deletes each daily object's state at the following UTC midnight.
Alarms can be delayed or retried, so deletion is scheduled rather than an
exact retention deadline. Daily ID rotation prevents the next day's requests
from reading yesterday's object. Cloudflare's SQLite point-in-time recovery
can retain historical storage for up to 30 days. No raw IP, bare IP hash, raw
Spec or Turnstile token enters the object. People sharing one public IP share
a daily allowance. IPv6 addresses within one /64 share that allowance;
different /64s have separate allowances. Changing networks can yield another
allowance.

Siteverify does not expose a documented headless flag or bot score. Turnstile
uses browser signals internally and this gate refuses failed validation.
The Worker does not invent or trust a client-supplied headless signal.
See [challenge outcomes](https://developers.cloudflare.com/turnstile/turnstile-analytics/challenge-outcomes/)
and [SQLite storage and concurrency](https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/).

## Page

Build with `VITE_HUMAN_GATE_ENABLED=true` and a public
`VITE_TURNSTILE_SITE_KEY`. The deploy-sites workflow reads those from GitHub
repository variables `HUMAN_GATE_ENABLED` and `TURNSTILE_SITE_KEY`. The key
is public configuration, not a secret. Both are unset by default.

The page obtains the current allowance from `GET /v1/human-status`, which is
origin restricted and never spends a lookup. When no state exists, a
status-only visit returns the full allowance without creating a table, writing
state or scheduling an alarm. A gated build waits for the status response. When
it reports `enabled: false`, the page uses the existing ungated behavior,
including automatic lookups and CSV download, without loading Turnstile or
showing an unavailable message. Only `enabled: true` activates the manual
flow. A transient status failure shows a retry button and can recover without
a reload. A manual button sends one full decision. The
page disables automatic lookup on edits, explanation requests,
canvas plot requests, estate requests, question probes and automatic Spec
fallback/retry. Estate data can accompany that single manual lookup.
The widget is replaced after every submission, including a refusal, and token
expiry disables submission. A cap message links to the paid API/MCP without
quoting prices. CSV download is hidden while the page gate is enabled.

`X-ModelSpec-Decisions-Remaining` reports allowance after admission or refusal;
`Retry-After` reports the wait for caps and suspicion. CORS exposes both.
The CSP allows `challenges.cloudflare.com` for scripts, frames and connections,
inside the existing single `/*` headers rule.

## Launch, owned by Jamie

Merge the clearly marked Durable Object binding and migration in
`api/worker/wrangler.jsonc`. No existing flags change. Set the secrets manually:

```sh
npx wrangler secret put VISITOR_HMAC_KEY --config api/worker/wrangler.jsonc
npx wrangler secret put TURNSTILE_SECRET --config api/worker/wrangler.jsonc
```

For an isolated staging check, use those commands with `--env staging` and
staging-specific values. The staging Worker is
`https://modelspec-rank-staging.flat-snowflake-881f.workers.dev`; it allows
`Origin: https://internal.modelspec-7np.pages.dev`. The current Rank API
workflow deploys staging only on `workflow_dispatch`, so dispatch it on `main`
after the merge before verifying the gate. Never reuse or publish secret values in a PR.
Create a Turnstile widget permitting the production, www and internal preview
hostnames. Configure its public key in the Pages build variables above.
Jamie adopts the separate privacy disclosure before enabling the gate. Publish
the page gate first: set repository variable `HUMAN_GATE_ENABLED=true`,
rebuild the site and verify that the gated build is live and still performs
automatic lookups while the Worker reports `enabled: false`. Only then enable
the Worker's `HUMAN_GATE_ENABLED`. This order keeps lookups working throughout
the rollout. The current ungated page receives 403 responses
if the Worker flag flips before the rebuilt page is live. Missing either Worker
secret, the binding or the request IP fails closed with a temporarily unavailable message.
Missing public site configuration disables the lookup button only when the
Worker reports `enabled: true`. It does not prevent ungated lookups.

This ticket gates `/v1/decide`. Existing static exports and the offline CLI
remain existing repository behavior; retiring downloads and all other machine
entry points requires separate changes. Turnstile and IP-based limits deter
batching but cannot prove personhood or prevent an actor rotating networks.
