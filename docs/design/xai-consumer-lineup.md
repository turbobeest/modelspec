# xAI current subscription lineup

MODEL-408. Design-first commit against engine base
`badf4be5fdff0a0803fd69387b165307f4190909`.

## Evidence and identities

A fresh full headed Chromium capture of https://x.ai/pricing returned HTTP
200 on 2026-10-18. The private retained document is
`research/model-408/capture/pricing.html.gz`. Its decompressed SHA-256 is
`bdf1848f0fe27294ccc7497f2016650cb32406e7252ccf191ab5d3b21d16ab21`.
The ordered comparison headers are Free, Plus, Premium, Super, Ultra, Teams
and Enterprise. Register these as seven distinct SubscriptionOfferings:

| Header | Canonical ID | Price observation |
| --- | --- | --- |
| Free | `xai/subscription/free` | $0/month |
| Plus | `xai/subscription/plus` | $8/month |
| Premium | `xai/subscription/premium` | $30/month |
| Super | `xai/subscription/super` | $100/month |
| Ultra | `xai/subscription/ultra` | $200/month |
| Teams | `xai/subscription/teams` | $30+/user/month |
| Enterprise | `xai/subscription/enterprise` | Custom |

Teams and Enterprise are organizational subscriptions in the Business
product family. The schema has no offering-family property, so this is a
documented classification, not a new field. Neither is an alias for the
existing `xai/subscription/business` record. Preserve that record and its
separately verified Grok 4.7 coverage. Do not transfer coverage between
Business, Teams and Enterprise.

The matrix names products, not versioned Grok models. It supplies no exact
model-label-to-catalogue-ID mapping. All seven new `models_covered` facts
therefore remain unknown with the attempted source recorded. Product labels
and generic references to Grok models cannot become catalogue IDs. A later
template may map literal versioned labels, subject to catalogue membership.

## Historical plans and contract impact

Keep Lite and Heavy under their existing IDs. Their current unsupported facts
remain unknown or quarantined, with a dated note explaining that the current
matrix does not name them. Historical values and verification events remain
available in history. Never infer retirement, a successor, or an alias from
the missing columns.

The spec predates an existing optional
`offering.subscription.availability` fact. At this base, the model and
decision contract already permit `open`, `existing_subscribers_only` and
`retired`, but only an explicit sourced statement establishes those values.
No such statement was observed for Lite or Heavy. Leave availability unknown.
Do not borrow model lifecycle. This change adds no schema field and widens
no contract range, so no major contract bump is needed.

## Exact reading

Extend `xai-exact-template@1` with a new reviewed current-pricing template.
It binds the new raw copy hash, complete normalized document hash, DOM
region hash, ordered literal headers, row labels, explicit cell paths and
approved SVG hashes. Keep the existing Business template. Public tests use
synthetic documents; provider HTML and screenshots stay private.

Read the first five exact USD monthly amounts from their own header cells.
Also verify their billing period through the exact reader. Teams' starting
per-seat price is not an exact subscription price under the existing scalar
contract, so leave its amount unknown and record the literal limitation.
Enterprise's custom price and billing period stay unknown. Do not coerce a
starting price to an exact amount or infer an annual option.

Read Grok Build and Grok Bot from their exact product cells. Preserve a
literal `Limited` cell as limited access, not a checkmark. Check and minus
glyphs mean included and not included for those named products. This follows
MODEL-367's product-inclusion decision for
`programmatic_or_agent_use`. It does not establish raw API entitlement or
change subscription surfaces or own-software routing. The required usage
allowance fact can remain unknown; this task does not turn relative usage
text into a token quota.

The new canonical IDs and their requested facets must use exclusive exact
dispatch. Changed bytes, reordered or extra columns, renamed plans, changed
rows, swapped glyphs and moved cells must fail with `template drifted` even
if a fallback reader could accept the claim. Unsupported model coverage,
prices and null claims must not become verified non-disclosure through
fallback. Preserve existing source-kind, whole-document and raw-byte checks.

## Filing and validation

Read the retained current terms and robots directives and record their
hashes privately. Robots directives do not establish redistribution rights.
Publish only code, hashes, short required labels and synthetic fixtures.
Use no paid-provider calls or Firecrawl credits.

Write red-first tests at `verify.verify` with retained CopyStore documents,
including all six specified mutations against the same approved synthetic
template. Replay the actual private capture separately before filing known
facts, and append verification history. Prove the seven new offerings load,
their known facts are admitted, unsupported coverage stays absent, and the
legacy records remain unsupported.

Run the focused suites, `web/npm ci`, the full engine suite under the shared
flock with four workers, and private data tests. Keep source bytes out of the
Worker bundle and measure the private snapshot and Worker memory gate with
the normal runtime probe. The private engine pin must descend from its
current pin. Both PRs remain draft for human review; the data pin cannot pass
its main-ancestry CI gate until the engine commit reaches main.
