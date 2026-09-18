# Legal documents — drafts

MODEL-70. Three documents, all **drafts**, none adopted:

| File | Published at | What it is |
| --- | --- | --- |
| `terms-of-service.md` | `/legal/terms/` | Terms for the hosted API |
| `neutrality.md` | `/legal/neutrality/` | The honest-broker commitment |
| `privacy.md` | `/legal/privacy/` | What the service records today |

## Who adopts these

Sparks & Sawdust LLC is the operator, and its operator is the only person who
can adopt terms of service. These were drafted by an agent, not by a lawyer.
§11 of the terms lists what needs counsel before any money moves.

## How they are published

`pipeline/legal.py` renders each file through the site's own Markdown renderer
and shell into the modelspec.dev tree during `pipeline/build.py`. While
`DRAFT = True` the pages carry `noindex, nofollow` and stay out of
`sitemap.xml`: the URL is stable, but a draft should not be found by anyone
looking for terms that bind. Adoption is flipping that one constant, after the
legal review and after the contact details in the terms and the privacy
statement are filled in.

The pages are **not yet linked from the landing page or the API docs**. Those
surfaces belong to other tickets in flight (MODEL-24 for the site, MODEL-72 for
the API docs) and were deliberately left alone. Linking them is the last step
before adoption, and MODEL-70's acceptance criterion about it is not met yet.

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

The rule for this ticket was that nothing in the terms may claim a capability
that is not shipped. As of 2026-09-17 these do not describe, as live: API keys,
tiers or rate limits (MODEL-69 is merged but not wired into the deployed
Worker), any paid plan or price, Stripe checkout (MODEL-73), x402 prepaid
credits (MODEL-75), outcome logging (not built), an MCP server, a policy-check
endpoint (MODEL-80, not merged), any uptime or support commitment. §6 of the
terms states the rules that will govern a charge, and says plainly that no
charge exists today.
