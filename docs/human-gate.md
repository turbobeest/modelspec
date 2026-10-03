# Human admission on the decide page

## Visit gate (MODEL-292)

`VISIT_GATE_ENABLED` is a new Worker flag. `VITE_VISIT_GATE_ENABLED` is the
new page build flag, supplied by the repository variable `VISIT_GATE_ENABLED`.
Both default to off. Production and staging retain every existing reserved
flag value. The legacy manual gate below remains available when the new
Worker flag is off.

When both new flags are enabled, the page runs a managed Turnstile check on
its first request of a visit, then updates the answer on every facet change
with the existing 300 ms debounce. There is no lookup button. The same random
intent identifies the summary, details, plot, estate and snapshot retries of
one action. MODEL-270's question derivations, eight-request bound, 60-second
intent window and pacing remain in force. Verification does not consume a
question, and an admitted question still spends allowance if its producer fails.

The widget uses `appearance: interaction-only`. Most visits pass in the
background. When interaction is required, the widget appears in the answer
panel, including during renewal. Network requests have deadlines; time spent
completing the widget does not consume those deadlines. See [Cloudflare's
appearance configuration](https://developers.cloudflare.com/turnstile/get-started/client-side-rendering/widget-configurations/).

`POST /v1/visit-token` accepts `X-ModelSpec-Turnstile`. Siteverify must report
boolean success, the hostname matching the request origin, and `action: decide`.
The origin must be one of `entry.CORS_ORIGINS`. The existing ten-second
Siteverify timeout and omission of `remoteip` apply. Failed verification,
missing identity, secret or binding never issues a credential.

The Worker signs a base64url JSON tuple of daily visitor id, exact origin,
issued-at and expiry using HMAC-SHA256 under the new Wrangler secret
`VISIT_TOKEN_HMAC_KEY`, which must contain at least 32 characters. The daily id
comes from `visitor.py` through the existing human-gate IPv6 /64 normalization.
The token is held only in page memory, never a cookie. Application code stores
or logs neither the visit token nor the Turnstile token. It expires after a
30-minute sliding window: each admitted decide or vocabulary request returns a
renewed token in `X-ModelSpec-Visit-Token` and its Unix expiry in
`X-ModelSpec-Visit-Expires`. Responses containing credentials are `no-store`.
Daily identity rotation also invalidates yesterday's credential.

A presented API key always takes the key path, even alongside a valid or
invalid visit token. With no key, a visit token must authenticate and match
both the visitor id and origin before `/v1/decide` or `/v1/vocabulary` receives
page admission. Expired tokens receive 401 `visit_token_expired`; tampering or
binding mismatch receives 401 `visit_token_invalid` under access enforcement.
With enforcement off, invalid credentials fall back to the existing anonymous
path. Expiry still requests a new check. These are access errors
outside the decision contract. The page silently rechecks on local expiry or
`visit_token_expired` and retries the request once, retaining its action intent.
Concurrent requests share one verification. A binding mismatch also gets one
fresh check, allowing a person whose network or UTC-day identity changed to
continue. A repeated refusal ends the retry.

Without either credential, `ACCESS_ENFORCED` decides whether to allow anonymous
access. With the new Worker flag on, the legacy manual route and MODEL-241's
Origin-only free shortcut are disabled. Under `ACCESS_ENFORCED=true`, a spoofed
allowlisted Origin without a credential gets 401 `missing_api_key`, including
when x402 is enabled. Visit tokens grant no admission to rank, compare,
policy-check or MCP; those paths require keys under enforcement. Worker-hosted
vocabulary checks keys or visit admission before returning its data, including
HEAD and query variants. Static distribution remains governed by
`DATA_SPLIT_ENABLED`; enable the data split for the private-data product.

The existing daily HumanGate SQLite object keeps a separate visit question
meter and vocabulary meter. Synchronous reads, admission and writes precede
any await. The existing sweep detection and midnight deletion alarm apply.
The token grants access; it does not reset the visitor-day allowance. Renewals
and fresh checks cannot reset the counters. Defaults are configuration in
`api/worker/wrangler.jsonc`, repeated for staging:

| Variable | Default | Window |
| --- | ---: | --- |
| `VISIT_DECIDE_DAY_LIMIT` | 300 | UTC day, questions |
| `VISIT_DECIDE_BURST_LIMIT` | 30 | rolling minute, questions |
| `VISIT_VOCABULARY_DAY_LIMIT` | 60 | UTC day, lookups |
| `VISIT_VOCABULARY_BURST_LIMIT` | 10 | rolling minute, lookups |

Jamie may tune these values in configuration. Missing or invalid configuration
fails closed. Vocabulary uses its own allowance and does not spend a question.
The continuation fingerprints and daily state retention remain as documented
below, with up to the configured number of question intents per visitor-day.
People sharing a public IPv4 address or IPv6 /64 share allowances.

Before enabling production, Jamie must adopt privacy v1.9 and mark the visit
gate disclosure live. The proposed diff is `model-292.privacy-v1.9.md` in the
session scratchpad; no adopted legal file changes in this ticket.
`tests/test_legal.py` refuses an ON Worker flag without that wording and its
configured allowance numbers. Configure the new signing secret separately in
each environment, retain the existing visitor and Turnstile secrets, and use
a **managed** Turnstile widget with the allowlisted hostnames and no pre-clearance.
Publish the new page build first, confirm that Worker-off lookups stay live,
then enable the new Worker flag with enforcement only after privacy adoption.
The existing gate and billing flag values are Jamie's separate decisions.

CI builds both new page variants alongside both legacy variants. Browser tests
exercise one silent verification, facet updates, local expiry, Worker expiry,
one retry per request, and interaction inside the answer panel. Worker tests
use real SQLite to verify quotas, concurrency, sweep detection and intent
metering, with only external Siteverify replaced.

## Legacy manual gate (MODEL-248)

`HUMAN_GATE_ENABLED` ships `false` in production and `true` in isolated staging
for verifying the gate on Cloudflare before production. Off preserves
the existing access and x402 paths. On, keyless `/v1/decide` actions from the
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
caps are 20 admitted questions per visitor per UTC day and three in a rolling
60 seconds. Admission consumes a question allowance even if the decision
engine subsequently refuses the Spec or fails. Failed verification and cap
refusals do not consume a lookup. This prevents concurrent or deliberately
invalid requests from obtaining more answers than the cap.

The state contains a UTC day, admitted count, recent timestamps, a suspicion
expiry and at most 20 verified intent IDs. Each intent stores its first-request
time, request count, recent continuation timestamps and canonical Spec
fingerprints. These are SHA-256 digests, not the raw Spec, conditions, resource
IDs or objective. The hashes support equality checks; they are not encryption
and guessable Specs can be matched against them. Every new question admission
counts toward interval detection, including a question admitted under a reused
intent ID. The continuation rule below binds each admission to its primary
question.
Already-deployed objects may contain timestamp/fingerprint pairs in the meter
history. Admission keeps only their timestamps. Legacy intents without a
question fingerprint fail closed with `human_intent_limit`; a fresh intent
needs a fresh verification and admission.
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
state or scheduling an alarm. A gated build waits for the status response without showing manual-gate
wording or controls. The board remains editable; once status resolves, the
first ungated lookup answers the current edited Spec. When
it reports `enabled: false`, the page uses the existing ungated behavior,
including automatic lookups and CSV download, without loading Turnstile or
showing an unavailable message. Only `enabled: true` activates the manual
flow. A transient status failure shows a retry button and can recover without
a reload. A `human_challenge_required` response refreshes status so an open
tab can adopt a newly enabled Worker gate. A manual button starts one intent after verification. The page retains summary-then-full
explanations, canvas plot decisions, estate requests,
the 409 snapshot-change retry and compatible Spec fallback. Every request caused
by that action carries the same intent header. Automatic Spec edits still wait for the
manual button while the gate is enabled.
The widget is replaced after every submission, including a refusal, and token
expiry disables submission. A cap message links to the paid API/MCP without
quoting prices. CSV download is hidden while the page gate is enabled.

`X-ModelSpec-Decisions-Remaining` reports allowance after admission or refusal;
`Retry-After` reports the wait for caps and suspicion. CORS exposes both.
The CSP allows `challenges.cloudflare.com` for scripts, frames and connections,
inside the existing single `/*` headers rule.


## Action intents (MODEL-270)

The page mints a cryptographically random 128-bit ID encoded as 22 unpadded
base64url characters in `x-modelspec-intent`. Initial answers, template applies,
facet edits and retries each start a new intent. The existing 300 ms debounce
groups rapid facet changes into one action. Each asynchronous request captures
its action's options, including snapshot retries, so later actions cannot
change the ID of an in-flight request. CORS allows this header.

The first request for a new ID verifies Turnstile and atomically admits its
question in the visitor's daily SQLite object. The Worker passes the same
parsed body to the gate and decision producer. The object parses the Spec with the decision
contract and fingerprints its canonical representation, including defaults,
normalised `where`, `optimize`, `access` and every other question field.
Condition order does not affect equality; duplicate conditions remain counted.
`explain` and `limit` do not define the question. A structurally invalid primary
still spends admission but permits no continuations.

Continuations use that verified admission without replaying a single-use
Turnstile token. They spend no further daily or minute allowance and add no
primary interval samples. Every continuation must match a permitted derivation
of the immutable primary, never of the previous continuation. An admission permits
at most eight requests, including its first, strictly within 60 seconds of its
first request. The ninth request or a continuation at or after 60 seconds receives
HTTP 429 with `human_intent_limit`. Refusals do not extend the window. Expired
and exhausted admissions remain closed to continuations.
Missing or malformed IDs meter every request individually and require fresh
verification. IDs are scoped to the daily visitor object; another visitor must
verify and spend its own admission even when it presents the same ID. The keyed
daily HMAC, fail-closed behavior and Turnstile validation conditions stay intact.

The auxiliary inventory and admission rules come from `App.tsx`,
`components/canvas-axis.ts` and `facet-board/model.ts`:

| Call | Difference from the primary | Permitted rule |
| --- | --- | --- |
| Full details | `explain: full` | The identical question with a different `explain` or `limit`. |
| Canvas plot | Clears `where`; replaces `optimize` with one or two numeric axes at equal weights; replaces `capabilities` with the selected capability axes marked `preferred`; `explain: full`, `limit: 500` | Accepts this exact transformation using registered numeric facets or capability domains. Optional preferred capability keys must be objective axes. The first accepted plot fixes the objective and capabilities for that admission. Date axes use the numeric fallback and do not add objective dimensions. |
| Estate comparison | Adds held provider, plan and device IDs | Adds only the contract's `estate.providers`, `estate.plans` and `estate.devices`. The primary question otherwise stays identical. The first accepted estate fixes those IDs for the admission; reordering IDs is canonical. `exhausted` is not a page derivation. |
| 409 retry | Reloads vocabulary, changes the snapshot header and resends | Header-only changes are admitted. A body change must independently meet the same derivation rules or spend a new admission. The body `snapshot` field defines part of the question. |
| Refinement compatibility fallback | Folds refinement objective weights into parent domains after a 400 | A changed objective is a new metered question, including when vocabulary re-filtering changes the objective on retry. |

The hosted page neither computes candidate next questions nor calls
`evaluateQuestionOptions` / `probeSpec`. Its only `Field` has
`showQuestions={false}`. Question rendering and the probe adapter remain
available for a future page that shows questions and sends metered intents for
its probes. Adding or removing even one atomic where-condition is a new question.

Plot and estate changes cannot be combined as a free continuation. Task tokens,
task type, profile, exclusions, capabilities outside the plot rule, access and
any future question fields define part of the question. The object stores only
digests for comparisons and never accepts a fingerprint supplied by the caller.

A well-formed new primary under an already verified ID spends a fresh daily and
minute admission, using that visitor's existing verification. This includes a
one-condition what-if, a different plot or estate variant, and a compatibility
fallback. The object atomically replaces the primary and resets its presentation
allowance only after admission succeeds. New questions still face the 20/day,
3/minute and even-interval sweep limits, including when the previous admission
has expired or exhausted its requests. A refused new question leaves the
previous primary and its fixed variants intact. An invalid continuation or a
legacy ID without a primary fingerprint fails closed with `human_intent_limit`.

Within the 60-second window, an admission permits at most eight requests in any
rolling second, including its primary. Concurrent admissions use the same
synchronous SQLite update. A pace refusal uses `human_intent_limit` and
`Retry-After: 1`. The browser reserves slots 150 ms apart across details, plot,
estate and snapshot retries. Aborted queued calls do not reach the producer.
This pacing applies to verified manual actions.

The deterministic real-vocabulary fixture measures this inventory for both a
fresh load and one Coding Budget template apply, with no saved estate:

| Request purpose | Fresh load | Template apply |
| --- | ---: | ---: |
| Main summary | 1 | 1 |
| Main full details | 1 | 1 |
| Canvas plot | 1 | 1 |
| Follow-up option probes | 0 | 0 |
| Total POST /v1/decide | 3 | 3 |
| Metered admissions | 1 | 1 |

Each action drops from 12 requests to three. A saved estate adds one comparison
request, for four. One snapshot retry on each of these four paths fits the
eight-request cap. Tests retain coverage for estate, full-details fallback,
compatibility fallback and snapshot reload behavior.

The bound is **at most 20 distinct questions per visitor per UTC day**, each
with at most the fixed set of presentation variants: the identical question
with different `explain` or `limit`, one fixed plot, one fixed estate comparison,
and snapshot retries of those requests. New questions are limited to three per
rolling minute, with the existing even-interval refusal. A varied-spec sweeper
spends another admission for every independently chosen question, even when it
reuses a verified ID or changes only one filter. Presentation variants and
retries share the eight-request cap for each admission.

Vitest drives a gated page load and a Coding Budget template apply through
the actual Python/SQLite admission code, with external Turnstile validation
replaced by the test verifier. Each action sends three successful requests
and spends one daily admission. `MODELSPEC_TEST_PYTHON` can select the Python environment;
otherwise this test uses `python3` with the repository's Python dependencies.

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
Privacy v1.8 already discloses the Spec-derived fingerprints described above.
Before enabling the legacy gate, Jamie marks its disclosure live. Publish
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
