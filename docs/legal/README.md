# Legal documents — adopted v1.0

MODEL-70. Three documents, **adopted and in force**:

| File | Published at | What it is |
| --- | --- | --- |
| `terms-of-service.md` | `/legal/terms/` | Terms for the hosted API |
| `neutrality.md` | `/legal/neutrality/` | The honest-broker commitment |
| `privacy.md` | `/legal/privacy/` | What the service records today |

## Adoption

Sparks and Sawdust LLC, the operator and the seller, adopted all three as
**version 1.0, effective 2026-09-19**, at the direction of its operator.

They were drafted by an agent (2026-09-17), then brought up to date with what
was actually built on 2026-09-19 — API keys, the credit ledger, Stripe Checkout
and its KV records, `POST /v1/policy-check`, the remote MCP server — before
adoption. Each factual claim was checked against the code it names.

**They were adopted without the counsel review that the drafts' §11 called
for.** That was the operator's decision, recorded here rather than smoothed
over. The items that review was meant to settle are listed below and remain
open. The terms' §11 now says, in the terms themselves, which of them the terms
do not address.

Contact for all three: **sales@modelspec.dev** (forwards to the operator). No
postal address is published; the terms say it is available on request there.

## Still open — for later counsel review

Moved here from §11 of the draft terms, unchanged in substance:

- governing law, jurisdiction and venue;
- limitation of liability, and any cap;
- indemnity;
- dispute resolution, and whether arbitration or a class-action waiver is wanted;
- consumer-protection, distance-selling and cooling-off rules in the places
  paying callers will actually be, and whether the refund position in §6 clears
  the strictest of them;
- sales tax and VAT registration and collection (see the Stripe Tax note in
  `docs/billing.md`);
- the data-protection basis and any controller/processor terms (§7 and the
  privacy statement describe what the system does; whether that is all that is
  required is a legal question);
- whether §4 should be a contractual undertaking that survives a change of
  control, which is the only version of "permanently" a buyer cannot quietly
  drop.

Added at adoption, for the same review:

- §6.6 refunds unused prepaid balance on request, while §6 also says monthly
  credits reset without rollover and are zeroed when a plan ends, and pack
  credits expire after 12 months. Counsel should confirm the two read together
  as intended.
- Cancellation is by email to sales@modelspec.dev; there is no self-serve
  cancellation path in the product.

## How they are published

`pipeline/legal.py` renders each file through the site's own Markdown renderer
and shell into the modelspec.dev tree during `pipeline/build.py`. `DRAFT` is
`False`: the pages are served `index, follow` and are listed in `sitemap.xml`.
Setting it back to `True` would publish them `noindex, nofollow`, out of the
sitemap and under a banner saying they bind nobody. A future revision is
drafted on a branch and adopted by merging it with a new version and effective
date, not by flipping the flag.

The pages are linked from the footer of the landing page
(`site/holding/index.html`) and of every generated page (`pipeline/render.py`
`shell`), from the pricing page, from the agent skill (`pipeline/agent_ready.py`), and from the API reference
(`docs/api.md`). `tests/test_legal.py` checks the adopted state.

## The machine-readable half

The neutrality commitment is not only prose. It is published as data in the same
object as the ranking floors:

```
GET https://modelspec.dev/api/rank/profiles.json  →  .ranking_policy.neutrality
```

and in the `policy` block of every `POST /v1/rank` response. Both are reachable
with no key. The single source is `neutrality_commitment()` in
`api/ranking/engine.py`; the pages above and that function are held to the same
strings by `tests/test_legal.py`, so the prose cannot drift from the JSON.

## What these documents deliberately do not claim

The rule is unchanged: nothing in the terms may claim a capability that is not
shipped. As of 2026-09-19 they do not describe, as live: x402 prepaid credits
(MODEL-75; built, `X402_ENABLED` off — the terms say only that x402 is not
currently offered), outcome logging (not built), or any uptime or support
commitment. §6 of the terms states the rules that govern a purchase without
asserting that purchase is or is not open today — `BILLING_ENABLED` decides
that, and `https://modelspec.dev/pricing` says which. Access enforcement
(`ACCESS_ENFORCED`) is off, and the terms say so as of the effective date.
