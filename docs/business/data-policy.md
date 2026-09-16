# What has to be published, and how fresh

**Open question, 2026-09-16. Not decided.** Jamie asked:

> For this open source repo to stay open source, do we have to keep it real time
> and recent? Or can we delay the publicized results by a month or later? Or do
> we even need to publish the results and we just keep the construct open
> source? Meaning the research data that we spend money on is not publicized.

This file answers the part that has an answer, separates the part that is a
product decision, and records the constraints that already exist in the code.
Nothing here is legal advice; [`../../CLA.md`](../../CLA.md) is itself still
marked pending legal review, and a data-licensing deal should not close without
a lawyer reading both licence files.

## The short answer

**Open source constrains the terms you distribute under. It says nothing about
what you publish, or when.**

Neither licence in force here contains a publication obligation or a freshness
obligation:

- **MIT** obliges one thing: ship the copyright notice with the code. It does
  not require you to publish anything, ever.
- **CC BY-SA 4.0** binds whoever redistributes the corpus or an adaptation of
  it. It does not oblige *you* to keep publishing, to publish on a schedule, or
  to publish at all.
- Even the strongest copyleft would not change this. GPL obligations trigger on
  **distribution**; AGPL's network clause triggers on offering the *program*
  over a network, and reaches the program's source — never the data the program
  operates on.

So: you could stop publishing the export tomorrow, delay it by a month, or
publish only the construct, and the repository would be exactly as open source
as it is today. **All three of Jamie's options are available.** The question is
entirely about positioning and trust, and it has a different answer for each of
four assets.

## Four assets, four different answers

The strategy document treats "the data" as one thing. It is not, and the split
is where the whole answer lives.

| Asset | What it is | Copyable from a clone? | Recommendation |
|---|---|---|---|
| **The construct** | schema, ranking engine, floors, `_basis`, CLI, export format, sites | yes, trivially | **publish forever.** It is the distribution channel and the neutrality proof |
| **The corpus** | `models/`, `benchmarks/`, `hardware/` | yes — and already has been | **keep publishing.** Already CC BY-SA and irrevocably out; see below |
| **Freshness + verification labour** | today's rows, human-checked sources, dated evidence | **no.** A clone decays from the moment it is taken | the only honest thing to charge for on the data side |
| **Work that never entered the corpus** | outcome data, measured throughput, per-customer evals, attestation receipts | **no.** It has never been published | **never publish.** This is the moat |

The fourth row is the real answer to *"do we even need to publish the results?"*
— and the answer is **no, and you already don't have to withhold anything to get
there**, because none of it exists yet. There is nothing to claw back. There is
something to start generating.

## Two things you cannot do

### 1. You cannot un-publish the corpus

CC BY-SA 4.0 is irrevocable by its own terms, the repository has been public
since 2026-04-05, and `modelspec.dev` serves the export. Every copy taken in
those five months holds a perpetual licence. [`CLA.md`](../../CLA.md) §2 lets
the project relicense **going forward** — that is exactly why it exists — but
nothing reaches a distributed copy.

Practically: a future-dated licence change would apply to new and changed cards,
producing a corpus under mixed terms that has to be tracked per file. That is
doable and it is a real cost. It is not the free option it looks like.

### 2. You cannot lean on the data licence as the moat

- **Facts are not copyrightable.** A benchmark score, a parameter count, a
  release date. In the US, *Feist* leaves only the selection and arrangement
  protected, and thinly. The EU/UK sui generis database right is stronger and
  does not travel to a US competitor.
- **Share-alike binds redistribution, not use.** A competitor who loads the
  corpus, serves answers from it, and never redistributes the database has a
  strong argument that no share-alike obligation was triggered. That hole is
  structural, not a drafting problem.
- The corpus is also **assembled from third-party sources** whose own terms
  govern that material — `LICENSE` says so explicitly. Selling a feed raises
  questions that publishing a CC BY-SA catalogue does not. That has to be
  audited before any data-licensing conversation: `REV-2`.

What actually cannot be copied is freshness, verification labour, outcome data
and attestation. Those are moats because of what they are, not because of what
a licence says about them.

## On delaying the public snapshot by a month, specifically

This one has a mechanical answer, and the code already made it.

`cli/modelspec/snapshot.py:49` — **`STALE_AFTER_DAYS = 30`**. The published
contract ([`../cli-contract.md`](../cli-contract.md)) says a snapshot older than
30 days is served with a warning on stderr, and `--require-fresh` fails on it.

So a 30-day publication delay means, for **every free user, permanently**:

- the `--json` envelope reports `"stale": true` on the day it is fetched;
- stderr carries a staleness warning on every command;
- `--require-fresh` — the flag a careful integrator reaches for — **always
  fails**;
- DPF's ticket author, the one consumer named in the contract, is a free user.

The free path does not get a little worse. It acquires a permanent warning
label, and the label is one the project wrote itself, in a contract other
programs already depend on.

[`../agent-commerce-assessment.md`](../agent-commerce-assessment.md) §1 named
this failure mode in advance: metering something the caller can compute for free
only sticks *"if you make the free path worse. That would trade the project's
actual advantage — being the open, checkable catalogue — for a small amount of
revenue."*

**If a delay ships anyway**, two constraints make it survivable:

1. **7–14 days, not 30.** Comfortably inside the staleness line, still
   commercially meaningful in a market where releases land weekly.
2. **Delay the rows, not the corpus.** Hold back *newly added or changed* cards
   for the embargo window; ship everything else live. A five-month-old model's
   facts are not perishable and withholding them buys nothing. The freshness
   that a buyer values is the week-old row, which is exactly the row the embargo
   would cover.

Both of those are honest, statable on the site, and leave the CLI's promise
intact. A flat 30-day delay is not.

## Recommendation

1. **Publish the construct forever**, including `api/ranking/engine.py`, the
   floors, and `_basis`. The neutrality claim in section 5 of
   [`BUSINESS_CONTEXT.md`](BUSINESS_CONTEXT.md) requires the **method** to be
   auditable. It does not require the data to be free. Keeping the method open
   is what makes "unbiased" machine-checkable rather than marketing.
2. **Keep publishing the corpus**, undelayed, until there is a paying customer
   who is demonstrably buying freshness. It is the credibility engine, the SEO
   surface and the reason a harness maintainer takes the call. Today it is
   costing you nothing you could otherwise sell.
3. **Never publish the fourth row** — outcome data, measured throughput,
   per-customer evals, attestation receipts. Start generating it now
   (`REV-8`, `REV-9`), with consent designed in from the first release.
4. **Charge for what a copy cannot reproduce**: a signed attestation bound to a
   request and a timestamp; a policy gate over fields nobody else maintains
   (`REV-4`, `REV-5`, `REV-6`); alerts on change (`REV-7`); an eval on the
   customer's own tasks.
5. **Where the research money goes, reconsider.** Firecrawl credits currently
   buy verification labour that lands directly in a CC BY-SA corpus. That is a
   fine trade for credibility and a bad one for margin. The place to spend
   against the moat is the fourth row — which is also the cheapest, because
   outcome logging costs compute, not crawl budget.

## The open decision, for Jamie

| Option | What it means | Cost |
|---|---|---|
| **A. Publish everything, live** (status quo) | corpus stays CC BY-SA and current; revenue comes entirely from attestation, policy, watch, evals | no data revenue; strongest trust position |
| **B. Short embargo on new rows** | 7–14 days on added/changed cards; everything else live; stated on the site | some trust cost; needs an embargo mechanism in `pipeline/export.py`; keeps `--require-fresh` working |
| **C. Future data under new terms** | new and changed cards after date *D* under a different licence, via the CLA | mixed-licence corpus tracked per file; breaks the "open catalogue" story; highest theoretical data revenue, and the hole in §2 above still applies |

**Recommended: A now, B when a customer has actually said freshness is what they
are buying. Not C** — it pays for the weakest moat with the strongest asset.

Do not change tier policy without Jamie, the same way ranking floors are not
changed without Jamie.

## Decision log

| Date | Decision | Rationale |
|---|---|---|
| 2026-09-16 | *(open)* publication tiering: A, B or C | this file |
