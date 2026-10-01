# The neutrality commitment

Version `1.3`, effective 2026-09-30. Adopted by Sparks & Sawdust LLC.
MODEL-70. Version 1.0 was adopted on 2026-09-19; what changed in 1.1 is listed
under [Changes](#changes). The commitment itself is `neutrality-v1`, which is
the same string the machine-readable copy carries.

## The rule

**Charging the consumer of a recommendation is compatible with being an honest
broker. Charging the subjects of one is not.**

An agent paying to ask "what should I use" has no stake in which answer comes
back. It wants the true one, which is exactly what it is paying for. A model
provider paying to appear is buying placement, and every ranking afterwards is
suspect whether or not it was actually influenced. The second is not a conflict
to be managed with a disclosure line. It is a different product, and we are not
in it.

## The commitment

**No referral fees, no paid placement, no provider-paid visibility,
permanently.**

Stated as the things we are not able to do rather than the things we promise not
to do, because the first kind can be checked:

- **We take no money from the subjects of a ranking.** No provider, host,
  gateway or vendor can buy inclusion, position, prominence or a mention. There
  is no rate card, because there is no price.
- **We do not proxy inference tokens.** We recommend and hand off. Your
  inference traffic goes to the provider, gateway or local runtime directly. We
  therefore earn nothing that scales with your token spend, and have no reason
  to prefer the route that spends more.
- **We do not hold your prompts.** A request carries a locally computed profile,
  not prompt text, so there is nothing to sell, leak or mine. See the privacy
  statement.
- **We are neutral in sourcing, not only in money.** No provider, gateway,
  hosting route or inference vendor is privileged at any stage: not in the
  ranking, not in the tie-breaks, not in a default hosting suggestion, not in
  routing advice, and not by any commercial relationship of the operator's.
  Refusing payment from the subjects of a ranking is the easy half. The harder
  half is refusing the version where nobody pays and the advice leans anyway.
- **When we buy from a vendor we catalogue, we say so.** We may be a paying
  customer of a vendor whose models we catalogue. When we are, the card
  says so, and no field on that vendor's card is ever set by that vendor's own
  model. Today that vendor is TypeSafe: the catalogue pays for Jev, TypeSafe's
  model, to judge ambiguous creator attributions, and no TypeSafe card is
  written by a Jev judgment. This is held by code, not by care:
  `schema/suppliers.py` lists the catalogued vendors we pay; the card page
  prints the disclosure from that list, so it cannot be left off a card
  (`pipeline/render.py`); and `scripts/attribution.py` refuses a vendor's model
  a judgment on that vendor's card before it is asked (`supplier_conflict`) and
  again before a stored one is applied (`apply_policy`).

"Permanently" is the load-bearing word. A commitment that lasts until the offer
is good enough is a price, not a commitment.

## How to check it, without trusting us

The commitment is published as data, next to the ranking floors, in the same
object that describes the policy an answer was computed under:

```
GET https://modelspec.dev/api/rank/profiles.json
```

No key. No account. No rate limit. It is a static file, and it stays keyless so
that anyone can check the commitment. The public model cards lag the service by
about nine months; the commitment and the ranking policy do not lag.

```
.ranking_policy.neutrality
```

```json
{
  "version": "neutrality-v1",
  "operator": "Sparks & Sawdust LLC",
  "rule": "Charging the consumer of a recommendation is compatible with being an honest broker. Charging the subjects of one is not.",
  "pledge": "No referral fees, no paid placement, no provider-paid visibility, permanently.",
  "permanent": true,
  "assertions": {
    "accepts_referral_fees": false,
    "accepts_paid_placement": false,
    "accepts_provider_paid_visibility": false,
    "proxies_inference_tokens": false,
    "stores_customer_prompts": false,
    "conceals_purchases_from_catalogued_vendors": false,
    "lets_supplier_models_write_supplier_cards": false
  },
  "source_neutral_at": ["ranking", "tie_breaks", "hosting_suggestions", "route_advice"],
  "charges": "the consumer of a recommendation, never its subjects",
  "vendor_purchases": "We may be a paying customer of a vendor whose models we catalogue. When we are, the card says so, and no field on that vendor's card is ever set by that vendor's own model."
}
```

The same block appears in the `policy` object of every response from
`POST https://api.modelspec.dev/v1/rank`, so an agent reads the commitment out
of the very answer it acted on rather than out of a page it never fetched.

Three further things are checkable without asking us:

- **The method is public.** `api/ranking/engine.py` is the scorer, and the
  floors it publishes (`min_benchmark_coverage`, `min_benchmark_count`) are the
  ones it applies. The rank endpoint runs that file, vendored verbatim, and the
  test suite fails if the two ever disagree.
- **The evidence is dated.** Every card cites its sources with the date each was
  read, and each ranked row reports its `evidence_basis`.
- **Absence is reported, not hidden.** Models without enough evidence are
  returned as unranked rather than quietly ranked last, and the response says
  how many there were. A ranking that hid them would look better and say less.

If we ever break this commitment, the JSON breaks first. That is the point of
putting it there.

## Changes

A change to this commitment gets a new version and date here; the version above
is the one in force.

- **1.3, 2026-09-30.** Corrected the operator's legal name to Sparks & Sawdust
  LLC, the name registered with Rhode Island and the IRS, here and in the
  `operator` field of the published data. The commitment itself is unchanged,
  so the identifier stays `neutrality-v1`.
- **1.2, 2026-09-30.** Corrected the description of who reads the published
  policy: the sites, and no command-line client (there is none). Stated that
  the public cards are a delayed image about nine months behind and that this
  file stays keyless. The commitment itself is unchanged, so the identifier
  stays `neutrality-v1`.
- **1.1, 2026-09-23.** Added the commitment on buying from a vendor we
  catalogue: the card says so, and no field on that vendor's card is set by
  that vendor's own model (MODEL-101). The published data gained the matching
  `vendor_purchases` sentence and two assertions,
  `conceals_purchases_from_catalogued_vendors` and
  `lets_supplier_models_write_supplier_cards`, both `false`. Nothing was
  removed or changed, so the identifier stays `neutrality-v1`.
- **1.0, 2026-09-19.** Adopted.
