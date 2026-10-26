# Cookieless site analytics

MODEL-220. Proposal for Jamie, 2026-10-26. Reviewed against repository commit
`d326a69bb46f9d573f28c6988aef95d412d01d9a` and privacy statement **1.14**, effective
2026-10-13. This is a source and documentation review, not a production capture.

The first option is to change nothing. Cloudflare Web Analytics is live and
already disclosed in privacy v1.14. It covers page views, referrers and load
times, with page-view proxies for template interest and `/decide` reach.
If actual template applications and completed answers are needed, the second
option adds two first-party event counters in the existing API Worker, with a
dedicated D1 database. Those counters need new privacy wording. **This PR stops
at the proposal**, as the ticket requires: it adds no collector, binding, switch
or browser event. The proposed legal diff below is for adoption by Jamie.

## What the current statement permits

The [adopted statement](../legal/privacy.md) already discloses Cloudflare Web
Analytics. These are its exact words, including the limits relevant here:

| Current wording | Consequence for this proposal |
| --- | --- |
| "**Cloudflare Web Analytics is on**, as described under *Cloudflare Web Analytics* below." | The existing dashboard is already covered. Adding a second beacon would duplicate collection. |
| "Cloudflare inserts its analytics script into each page of the site as it serves the page; the script is not in our code." | An application-owned embed would change this description, even if it used the same service. |
| "the page's address without its query string or the part after the `#`; the page you came from, shortened the same way" | Current collection does not expose a template query parameter or a board encoded in the fragment. |
| "We do not export it, join it to anything else, or use it to build a profile of you." | Keep the Cloudflare dashboard separate. Do not export or join it to new counters, feedback, access records or visit-gate state. |
| "No D1 database, R2 bucket, queue or analytics dataset is bound." | A new D1 counter store needs disclosure before it can be bound. The preceding inventory also names only two KV namespaces and two Durable Objects. |
| "There is no analytics call, no telemetry beacon and no third-party tag on the API path." | A new first-party analytics endpoint is an exception that must be stated. |
| "send what you enter to `/v1/feedback` only when you press Send" | The feedback disclosure does not authorize automatic template or completion events. |

The statement's *What Cloudflare records* section describes platform request
metadata and Workers observability, used to check service health. That does not
authorize a new product-usage store or mining those logs for visitor journeys.
Its cross-request-state paragraph also limits other state to the feedback
limiter and cached catalogue data. Anonymous totals still change what the
service records and need an explicit exception.

Repository evidence agrees with those boundaries:

- [Security headers](../../pipeline/security_headers.py) allow the Cloudflare
  beacon hosts. They do not install a beacon. The legal tests allow the
  disclosed edge-injected script and check its stated purpose and limits.
- [Worker configuration](../../api/worker/wrangler.jsonc) has observability on,
  two KV namespaces and two Durable Objects. `FEEDBACK_ENABLED` and
  `SIGNALS_ENABLED` are false. No analytics store is bound.
- [Feedback](../../api/worker/src/feedback_service.py) accepts voluntary ratings
  and optional page/template fields; its storage is gated separately.
  [Signals](../../api/worker/src/signals_service.py) handles authenticated public
  release notices. Neither is a site-analytics collector.
- [Template preview pages](../../pipeline/social_cards.py) have paths such as
  `/decide/templates/<id>/`. Their adjustment links use
  `/decide/details/?template=<id>`. An actual template application updates local
  board state in [FacetBoard](../../web/src/decide/facet-board/FacetBoard.tsx).
- [The detailed app](../../web/src/decide/App.tsx) and
  [the simple decision hook](../../web/src/decide/simple/useSimpleDecision.ts)
  can fetch summary, full and auxiliary answers for one action. A count of
  `/v1/decide` responses would count more than completed user actions. The
  visit gate counts admissions even when an answer fails; its identifiers and
  question digests are reserved for admission control.

## The alternatives

### Option A: change nothing

Keep Cloudflare Web Analytics alone. It is live and privacy v1.14 already
discloses its page views, referrers and load times. Views of
`/decide/templates/<id>/` give a free proxy for template interest; views of
`/decide/` and `/decide/details/` give a free proxy for `/decide` reach.
These proxies cannot measure in-app template application or completed answers.
An application changes local state, and a page view does not establish that an
answer rendered. This option needs no privacy revision, collector or new store.

### Option B: add aggregate interaction counts

Keep the existing dashboard and add the two counters described below only if
the proxies are insufficient. This requires a privacy revision, D1 database,
cleanup job, production switch and browser emitter. The comparison includes
server-side page counts to explain why they do not replace interaction events.

| Question | Cloudflare Web Analytics, already disclosed | Server-side aggregate counts in Pages or the Worker |
| --- | --- | --- |
| What is collected? | A browser beacon reports page and referrer addresses, a per-load id, browser/OS and performance information. The statement specifies no query or fragment. Reports group counts by page, referrer, country, browser, OS and device. | A proposed handler maps inputs to a finite set of approved categories and immediately increments a daily total. Store only day, counter kind, approved category and count. No raw event rows, URLs, referrer strings, identifiers, IPs or user agents. |
| Page views | Measures browser page loads and supported SPA navigations. Blockers, disabled JavaScript and failed delivery lose observations. A visit is not a unique person. | Pages middleware could count successful HTML GET responses. Exclude assets, HEAD, redirects, errors and API calls. It counts delivered requests, including bots and reloads, and misses browser-cache restores and client-only changes. The API Worker does not see Pages HTML requests. |
| Referrers | Dashboard has referrer host; GraphQL also exposes referrer path. Current policy prohibits exporting these data. | Map the request's referrer transiently to fixed categories such as internal, approved search/social hosts, other or absent. Never persist arbitrary hosts or paths, which can contain personal data. Missing referrer does not prove direct navigation. |
| Template use | Can count a template preview's page views. Cannot tell whether someone applied it. Query parameters are excluded and arbitrary custom events are unsupported. | Needs an explicit browser event on successful template application. A server page counter alone cannot see it. Use an approved catalogue id, never the resulting spec. |
| `/decide` completion | A `/decide/` view or a Web Vital does not establish that an answer rendered. No supported custom completion event. | Needs a browser event after a valid primary answer renders for an explicit user action. A successful API response alone is insufficient. Count no initial/default answer, retry, cancelled action, full-detail upgrade, plot or estate follow-up. |
| Privacy-statement fit | Continued use of the existing disclosed behavior fits unchanged. New fields, a manual embed, exports, joins or invented navigation events would require reassessment. | Both page counters and interaction counters add a collection purpose/store. They need wording changes even without identifying data. |
| Cost | Free service. Existing integration needs no new application infrastructure. | Worker/Pages Function requests, compute and durable storage consume account quotas. New validation, reporting, abuse controls and retention jobs also need maintenance. |

Cloudflare's [product privacy description](https://www.cloudflare.com/web-analytics/)
says its analytics uses no cookies or browser storage and does not fingerprint
visitors. Its [RUM documentation](https://developers.cloudflare.com/speed/observatory/rum-beacon/)
describes the per-page identifier, timing and performance fields, and receipt
and disposal of the source IP at the edge. This RUM-specific handling does not
remove the platform metadata disclosed by ModelSpec. "No personal data" here
means no personal data in the proposed JSON event body or aggregate store.
The hosting network receives an IP address, and the proposed admission check
transiently processes the existing pseudonymous visit token. Those are security
processing, disclosed separately below; the whole HTTP request is not anonymous.

The [metric definitions](https://developers.cloudflare.com/web-analytics/data-metrics/high-level-metrics/),
[dimensions](https://developers.cloudflare.com/web-analytics/data-metrics/dimensions/)
and [SPA behavior](https://developers.cloudflare.com/web-analytics/get-started/web-analytics-spa/)
support the page/referrer comparison above. Cloudflare's
[FAQ](https://developers.cloudflare.com/web-analytics/faq/) explicitly rules out
custom events and query-string/UTM reporting today. It describes seven days of
unsampled beacon data, subsequent aggregation and query sampling, with six
months accessible. It also warns about blocked beacons. Do not invent a
`/decide/completed` navigation or put a decision id in a URL to simulate an
unsupported event.

Pure server page counts would need new Pages routing and packaging. The legacy
`site/functions` files are copied into the full build by `pipeline.agent_ready`,
but [the live composition](../../pipeline/live.py) does not preserve those
functions. The [deployment](../../.github/workflows/deploy-sites.yml) uploads
`dist/modelspec`. A future Pages solution must prove its function artifact is
in that upload and constrain its routes; adding a source middleware file alone
would not establish deployed coverage. The site remains on Cloudflare Pages.

## Measurement and storage for option B

If option A's proxies are sufficient, no implementation is needed. Otherwise,
use the current Cloudflare dashboard for pages, referrers and performance and
add only the missing interaction totals through a small endpoint in the
existing API Worker. This avoids a new function invocation on every static page
and lets the new payload omit page addresses and referrers entirely. Keep both
reports separate. Do not calculate a joined visitor funnel or combine these
counts with Cloudflare, gate, feedback or billing records.

Proposed definitions and safeguards, to implement only after adoption:

- `template_applied`: one event when an explicit user choice applies an
  approved template, including an explicit template link that the board
  successfully applies. Emit it once in page memory, not again on retries or
  rerenders. Merely viewing its preview or restoring a shared board is not use.
- `decide_completed`: one event when the primary answer for an explicit user
  action renders, including a valid empty-result answer. Count a template
  action's answer once. Exclude automatic initial answers and auxiliary
  requests. This means the interface answered, not that a person read, chose
  or acted on a recommendation. There is no "unique users" claim.
- Accept a JSON event body of exactly `{event: "template_applied", template: <approved-id>}` or
  `{event: "decide_completed"}`. The completion event has no template field;
  no per-template completion funnel is proposed. Reject unknown fields and
  values, oversized bodies and content types other than JSON. Choose a small
  fixed body cap, such as 256 bytes. Do not accept arbitrary categories.
- Aggregate with one atomic D1 upsert into `(day, event, template, count)`,
  where `day` is the server's UTC day and `template` is the empty sentinel for
  completion. No event timestamps, event ids, request/decision/intent/visit
  ids, spec, estate, output, prompt, free text, API key, IP or user-agent enters
  the store. No event history or cross-category join is needed.
- Send no cookies or API keys, and set the request's referrer policy to
  `no-referrer`. Require the existing in-memory browser visit token for
  admission, checked under the existing visit gate's origin, expiry and daily
  visitor-binding rules before the collector runs. Drop the event if there is
  no valid token; do not start a new verification just for analytics. Only the
  authorization layer handles the token's pseudonymous visitor id and derives
  the existing daily HMAC from the address transiently to check its binding.
  This is validation only. An analytics POST must not renew the visit token's
  30-minute window, consume the daily or per-minute gate allowance, or ever
  write to `HUMAN_GATE`. Do not run the admission/metering or token-renewal path;
  return no renewed token. Enforce the analytics cap separately in D1.
  Pass neither the token nor its visitor id to aggregation and add no identity
  records. This use of the token must be disclosed before implementation.
- Require the exact production site Origin and permit only POST for ingestion.
  Origin alone is not authentication: a script can forge it. Missing, invalid
  and expired visit tokens must be refused; API-key machine callers have no
  analytics-ingestion path. The collector must not fingerprint a browser,
  read browser storage, hash an address or receive authorization identifiers.
  Bound accepted events by a global daily cap enforced atomically, keep the
  dimension set finite and fail without affecting decisions. Do not add
  per-address abuse records. Counts remain approximate and susceptible to
  forged or lost events; stronger identity tracking is outside this proposal.
- The endpoint returns no model data and offers no public report/read API. It
  must not call the decision service or bypass existing keyed machine access.
  An operator-only aggregate report uses account credentials. No raw-data
  export, telemetry log line or personal-data debugging is permitted.
- Delete active counters once their UTC day is 30 days old. Use a scheduled
  Worker handler for daily cleanup, independently of whether collection is
  enabled, and filter expired days from every report. A failed job can delay physical deletion. D1 Time Travel
  can retain deleted states for up to another 30 days on Paid. A restore must
  purge expired rows before ingestion or reporting resumes. Keep no exports
  or separate backups that extend this period.
- A future `SITE_ANALYTICS_ENABLED` switch must default off in production,
  staging and builds. Missing or invalid values mean off. While off, omit the
  browser emitter, return 404 before ingestion parses a body, and perform no
  counter writes. Jamie alone enables it. Do not reuse `FEEDBACK_ENABLED` or
  `SIGNALS_ENABLED`. No such switch is added by this PR.

D1 provides an atomic database operation without KV read/modify/write races;
Cloudflare documents KV's limitations in
[How KV works](https://developers.cloudflare.com/kv/concepts/how-kv-works/).
A dedicated Durable Object counter is another sound storage choice, as shown
in Cloudflare's [counter example](https://developers.cloudflare.com/durable-objects/examples/build-a-counter/).
D1 is proposed for the small daily table and operator SQL reports. No production
database, query behavior or capacity has been tested in this proposal.

The stored totals contain no visitor identifier. Small day/template counts can
still reveal activity in a known group, which is another reason to keep reports
operator-only and prohibit joins. The aggregation layer has no event
identifiers or individual event records, so it cannot deduplicate a repeated
POST or measure a person's journey. Page-memory
guards prevent routine UI duplicates, not malicious ones. These limits are
acceptable for coarse product planning, not billing or statistical claims about
individual conversion.

## Cost and retention assumptions

Prices below are USD, checked in official documentation on 2026-10-26. Included
quotas are shared with the account's other workloads; no bill or usage dashboard
was inspected.

| Component | Published cost and relevant limit |
| --- | --- |
| Web Analytics | [Free](https://developers.cloudflare.com/web-analytics/about/). |
| Static Pages vs Functions | [Static requests are free; Function requests consume Workers quotas](https://developers.cloudflare.com/pages/functions/pricing/). Intercepting every HTML request adds billed compute paths. |
| Worker | [Free allows 100,000 requests/day. Standard starts at $5/month](https://developers.cloudflare.com/workers/platform/pricing/), including 10 million requests and 30 million CPU milliseconds/month. Overage is $0.30/million requests and $0.02/million CPU milliseconds. |
| D1 | [Free includes 100,000 rows written/day, 5 million read/day and 5 GB account-wide](https://developers.cloudflare.com/d1/platform/pricing/). Paid includes 50 million writes/month, 25 billion reads/month and 5 GB account-wide. Overage is $1/million writes, $0.001/million reads and $0.75/GB-month. Index updates and deletion also consume writes. |
| D1 recovery | [Time Travel is always on](https://developers.cloudflare.com/d1/reference/time-travel/), with seven days of recovery on Free and 30 days on Paid, at no extra charge. This is why active deletion is not immediate erasure of all recovery copies. |

[D1 limits](https://developers.cloudflare.com/d1/platform/limits/) cap each
Free database at 500 MB and each Paid database at 10 GB, separately from the
account's included storage.

For scale only, 100,000 new events/month means about 100,000 Worker requests
and at least that many counter-row writes, plus cap enforcement, indexes,
cleanup and report queries. It could fit unused included Paid quotas. That is
not a $0 guarantee or a measured CPU/storage estimate. If requests and those
100,000 base writes were entirely above the included quotas, their published
request/write charges alone would be $0.03 plus $0.10. Compute and other
database operations are additional. The build, tests and maintenance are the
main new work; using the existing dashboard alone costs no new engineering
integration and provides the proxies in option A, but cannot count actual
template applications or completed answers.

## Proposed privacy-statement diff, for Jamie

This is an exact patch against the v1.14 file at the base commit. It is a
proposal only and has not been applied. The proposed 1.15 version and
2026-10-26 adoption date must be rebased if another legal revision or a later
adoption comes first. It discloses planned collection as **not built or enabled**.
Adopting v1.15 now is optional. Recommend deferring adoption unless Jamie wants
the commitment public first. The proposal can be folded into a single privacy
revision when the feature goes live, published before D1 is bound or collection
is enabled. That revision must describe the live behavior and update the store
inventory, cross-request state and API-path exception together. If Jamie adopts
the planned wording now, a later live-state revision is still required.

Any adoption PR must bump both privacy version/date expectations in
`tests/test_legal.py`: line 298 in
`test_the_x402_legal_revision_is_effective_on_the_flip_date`, and line 906,
`IN_FORCE["privacy"]`, used by `test_every_document_is_adopted_and_versioned`.
For this draft they would become ``Version `1.15`, effective 2026-10-26.``;
use the actually adopted version and date if adoption is deferred. This PR
changes neither assertion. This draft grants no permission to deploy or change
a production switch.

```diff
--- a/docs/legal/privacy.md
+++ b/docs/legal/privacy.md
@@ -1,6 +1,6 @@
 # Privacy statement

-Version `1.14`, effective 2026-10-13. Adopted by Sparks & Sawdust LLC, which
+Version `1.15`, effective 2026-10-26. Adopted by Sparks & Sawdust LLC, which
 operates the service. MODEL-70. Version 1.0 was adopted on 2026-09-19; what
 changed since is listed under [Changes](#changes).

@@ -32,6 +32,11 @@
 tells us where visitors come from, which pages they use and how fast those
 pages load. It does not tell us who you are: it sets no cookie, and nothing it
 shows us identifies you.
+
+We also plan two aggregate site-use counts: template applications and answers
+rendered after a visitor's action on the decide page. They are **not built or
+enabled**. Their proposed collection and retention are described under *Not yet
+live*. They would not record your question, the answer or who you are.

 ## What a request contains

@@ -605,6 +610,71 @@
   refused, not treated as human. No network-operator or headless score is
   stored. ModelSpec sets no cookie for this and does not enable Turnstile
   pre-clearance; we do not say that Cloudflare sets none of its own.
+- **Aggregate site-use counts (MODEL-220).** Planned, **not built or enabled**.
+  No collector, analytics database or `SITE_ANALYTICS_ENABLED` switch exists
+  yet. The proposed switch would default off. While off, the browser would
+  send no new analytics events, the collector would answer 404 and no counts
+  would be written. Cloudflare Web Analytics, described above, would continue
+  unchanged.
+
+  If built and enabled after adoption of the required live-state wording, our
+  decide page would automatically send one of two events to a separate
+  first-party endpoint on `api.modelspec.dev`: `template_applied`, with the
+  catalogue id of a template you explicitly applied, or `decide_completed`,
+  when a valid primary answer is rendered after your explicit action. The
+  latter would include an answer with no matching models. It would carry no
+  template id. Initial automatic answers, retries and supplementary detail,
+  plot or estate requests would not count as completions. These counts would
+  tell us which templates are used and how often the interface answers; they
+  would not tell us whether you read or acted on a recommendation.
+
+  The proposed Worker collector would keep only the UTC day, event kind,
+  approved template id for a template event, and a count, in a dedicated D1
+  database. It would generate the day itself and immediately increment an
+  aggregate, without keeping an individual event or time of day. The JSON
+  event body and counter store would contain no page address, referrer, question, answer,
+  estate, free text, decision id, visit or intent id, API key, IP address or
+  user-agent. Event requests would omit cookies, API keys and referrers. They
+  would carry the existing in-memory visit token for authorization, under the
+  visit gate's origin, expiry and daily visitor-binding checks. Without a
+  valid token, no event would be counted. An analytics POST would not renew
+  the visit token's 30-minute window, consume the daily or per-minute gate
+  allowance, or ever write to `HUMAN_GATE`. It would return no renewed token.
+  Authorization would handle the
+  token's pseudonymous daily visitor id separately and transiently derive
+  the existing daily HMAC from the address to validate its binding. Neither
+  the token nor the visitor id would reach aggregation, and no identity
+  record would be added. This
+  collection would set no cookie, use no browser storage, create no visitor
+  identifier and perform no fingerprinting or cross-site tracking. Cloudflare
+  would still receive network request metadata under *What Cloudflare
+  records*. The existing *The visit token* paragraph explains that the token
+  travels in request and response headers which Workers observability may
+  record in invocation logs. The token header on these analytics requests
+  would be subject to that same logging.
+
+  A daily cleanup would delete counters once their UTC day is 30 days old;
+  older days would be excluded from reports even if cleanup failed. A failed
+  cleanup could delay physical deletion. Cloudflare D1 recovery history can
+  retain deleted states for up to a further 30 days. Cleanup would continue
+  while collection is off, and a restore would remove expired rows before
+  collection or reporting resumed. We would keep no separate exports or
+  backups of these counts.
+
+  Only the operator would have access to the aggregate report. We would not
+  join these counts to Cloudflare analytics or logs, feedback, gate or billing
+  records, or build visitor profiles. The counts would be approximate: events
+  can be lost, repeated or forged, and the global daily cap could drop them.
+  The collector would add no per-address records to limit abuse and provide
+  no model data or public report endpoint. It would be separate from voluntary
+  feedback and from the release-signal automation.
+
+  This would add an exception to the store inventory, cross-request state
+  description and absence of analytics on the API path above. Those sections
+  and this planned status must be updated before a database is bound or
+  collection is enabled. The existing decision endpoints would continue to
+  keep no request content beyond their already disclosed exceptions.
+
 - **Outcome logging by the service.** Not built. The service does not receive or
   record what you chose, whether a recommendation worked, or anything about the
   result of acting on one. The CLI keeps no log of outcomes. The feedback
@@ -629,6 +699,10 @@

 A change to what the service records is a change to this statement, and it is
 published here before the change ships. The version above is the one in force.
+
+- **1.15, 2026-10-26.** Proposed aggregate template-application and rendered-answer
+  counts (MODEL-220), disclosed as not built or enabled. Described their
+  proposed payload, store, purpose, limits and retention. No collection changed.

 - **1.14, 2026-10-13.** x402 payments are live (MODEL-333). The x402 bullet moves from *Not yet live* to *What x402 payments involve*. That section discloses what the signed payment carries, that Coinbase's facilitator verifies and settles it, what we keep and do not keep, that a settlement is public on Base, and the receiving address. Keys stay enforced, so neither keyless change the earlier text predicted occurs.

```

## Verification and remaining work

The focused legal and removed-source suites validate the current repository;
they cannot approve new legal wording or prove a production configuration.
The embedded patch is checked with `git apply --check` without applying it.
The [execution evidence](../evidence/g2-ios/MODEL-220-fix.md) records commands,
results and the limits of this review.

If Jamie adopts the design, the implementation must first demonstrate failing
tests for off/missing/invalid switches, exact payload rejection, finite
categories, concurrent increments and the global cap, deletion and restore
behavior, missing/invalid/expired visit-token refusal, no token/referrer/body
logging by application code, no token renewal, no gate-allowance consumption,
no `HUMAN_GATE` writes, and duplicate UI renders. The
browser tests must distinguish one primary answer from default, retry, stale,
plot, detail and estate responses. Test that analytics failures never fail a
decision, and that no machine data path becomes keyless. Then run those focused
suites, the existing legal/access/feedback guards and the deployed-artifact
checks before any production enablement. None of that implementation is part
of this proposal.
