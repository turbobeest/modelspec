# Business model: decision record

**Decided by Jamie, 2026-09-16**, in session with Claude Code. This supersedes
the open questions in [`data-policy.md`](data-policy.md) and Gate 0 of
[`revenue-backlog.md`](revenue-backlog.md). Where
[`BUSINESS_CONTEXT.md`](BUSINESS_CONTEXT.md) differs, this file is newer.

Operator: **Sparks & Sawdust LLC**, which also owns Dark Product Factories.

## The shape, in one paragraph

ModelSpec open-sources the construct — the schema, the ranking method, the CLI —
and keeps publishing a catalogue of facts it does not own. Neither is
protectable and neither is meant to be. The revenue comes from work that has to
be redone continuously and that nobody else is doing: determining, with a cited
source, whether a given model is actually permitted for a given company. **That
work never enters git.** The moat is architectural, not legal.

---

## 1. Licensing

| Decision | |
|---|---|
| **1.1** | **No relicensing.** Code stays MIT. The corpus in `models/` and `benchmarks/` stays CC BY-SA 4.0 |
| **1.2** | The CC BY-SA grant on already-published content is irrevocable and that is accepted. One known clone, held by a friend. Not a risk being managed |
| **1.3** | Nothing obliges the project to keep permitting commercial use; it is doing so by choice, because the open catalogue is worth more than the licence |

**Rationale.** Facts are not ownable — a benchmark score and a parameter count
belong to nobody. Relicensing buys a weak asset and spends the open-catalogue
positioning that produces search traffic, credibility and harness
conversations. The licence was never the moat and strategy time spent on it is
wasted.

## 2. The enrichment split — the load-bearing decision

**2.1 Researched enrichment is never committed to git.** This is the only lever
that actually protects anything: the cards are in a public repository, so
anyone can run `pipeline/build.py` and rebuild a current export in minutes. A
delayed export protects nothing while the enrichment sits in the tree.

**2.2 The boundary is field type, not age.** Two clocks were considered and
rejected: model release date (a two-year-old model determined today would
publish instantly, which is backwards) and a single global delay (it treats
fields whose value decays differently as if they were the same).

| Class | Examples | Where it lives |
|---|---|---|
| **Baseline** | architecture, parameters, release date, lineage, provider, model type | git, public immediately |
| **Performance evidence** | benchmark scores, rankings, pricing | enrichment layer, then **released to git 90 days after determination** |
| **Policy determinations** | `commercial_use`, `data_residency`, licence and origin analysis | **enrichment layer permanently. Never auto-released** |

**2.3 Why policy determinations never age out.** Performance evidence answers
"what is best right now", which decays in weeks. A compliance answer does not
decay at all — a company deploying a two-year-old model needs to know whether it
is allowed exactly as much as it would for a model released yesterday.
Compliance is not a freshness product. A release clock on it would simply give
the asset away on a delay.

**2.4 Why 90 days and not six months for performance evidence.** The public
catalogue is the credibility and search engine that gets a harness maintainer to
take the call. At six months stale it stops doing that job, which trades the
best marketing asset for data already worth little. 90 days is the balance.

**2.5 The clock starts at determination, not at model release.**

## 3. Publication and access tiers

| Tier | What it gets | Limit |
|---|---|---|
| **Public export** | static JSON, baseline + performance evidence older than 90 days | unlimited, free, **delayed 90 days**, labelled honestly |
| **Sandbox** | `test_*` keys returning realistic fixed results | **unlimited** |
| **Free live** | live rankings, top 3, reasons, `evidence_basis` | **10 per day**, 5/minute burst |
| **Paid** | the compliance answer — `commercial_use`, residency, clause cited — plus full ranked list and saved policies | by plan |
| **DPF** | live keyed origin, no limit | free; see §6 |

**3.1 The public export is delayed, never degraded.** Delay is defensible and
can be stated on the tin. Deliberately making the artifact painful to use would
cost the evidence-discipline reputation that is the entire product, and would
not work anyway — see 2.1.

**3.2 The free tier gates on enrichment, not on the meter.** `recommend` is an
occasional call, so a generous rate limit means nobody ever upgrades. 10/day is
about ten minutes of integration work — unusable for a build loop, ample for a
genuine occasional decision. The paywall sits on the compliance answer, which is
the thing that cost money to produce.

**3.3 The unlimited sandbox is what makes the tight quota fair.** Developers
integrate for free and without limit, then spend real calls confirming it works.

**3.4 The free answer must be genuinely good** — top 3 with real reasons and
evidence basis. A crippled taste sells nothing.

## 4. Revenue

**4.1 Subscriptions carry year one.** Team $49–99/month; enterprise governance
$1–5K/month. Both sell on compliance, not on rankings.

**4.2 x402 charges a real price** — $0.001–0.01 per successful result. Not zero.
"We have paying agent customers" is a materially different sentence to an
acquirer than "we have users", and it costs nothing to make it true.

**4.3 Prepaid credits, drawn down per successful result**, with raw per-call 402
as the fallback. Per-call settlement on every request puts the documented
free-riding and check-before-use attacks on the hot path and adds a round trip
to every answer. Credits let an agent with a budget top up once and produce
deferred revenue that can be reported.

**4.4 Bill only on success, and verify settlement before delivering the answer.**

**4.5 Never charge the subjects of a recommendation.** No referral fees, no paid
placement, no provider-paid visibility, permanently. Charging the consumer of a
recommendation is compatible with being an honest broker; charging its subjects
is a different product.

## 5. What stays public, and what does not

**5.1 Public, permanently:** the ranking method (`api/ranking/engine.py`, the
floors, `_basis`), the export format, the CLI, and every card's source citations
with the date each was read. "Published method, tiered data" is the neutrality
claim, and it only works if the method is genuinely checkable.

**5.2 Private:** crawl mechanics. `scripts/benchmarks/` and the Firecrawl
integration move to the private server repository. The budget guard stays in
code wherever it lives. Hide *how it is fetched*; keep *what is cited* and *how
it is ranked*.

## 6. DPF

**6.1 DPF uses ModelSpec free.** Same legal entity — invoicing itself is
bookkeeping with no upside.

**6.2 DPF gets a real key on the customer code path**, for telemetry and so the
first integration exercises exactly what a paying caller exercises.

**6.3 DPF points at a keyed live origin**, so staleness disappears for it while
the public export ages 90 days. `snapshot fetch --origin` already exists;
**nothing in the CLI contract changes** — same commands, same envelope, same
exit codes, `fetched_at` is simply always current.

**6.4 DPF usage is not revenue** and does not count toward MRR in any deck. A
buyer discounts related-party revenue to zero.

**6.5 ModelSpec stays separable inside Sparks & Sawdust** — its own repository,
domain, Cloudflare account and documentation, as is already the case. Same
entity is fine; entangled assets are what makes a buyer discount or walk.

## 7. Consequences that need building

These follow from the decisions above and are not themselves open.

**7.1 The withheld-value problem.** `schema/card.py:162` publishes
`commercial_use`, and a public `null` means "not yet researched" under standing
rule 1. Once a value is determined and withheld, the catalogue would be lying on
~1,300 cards. **A third state is required** — determined, not published — for
example `available_via: api` beside the null. This is honest, and every withheld
field advertises the paid tier. It is a new enum value and therefore a **major
bump under MODEL-59**, so it lands *before* the determination work, not after.

**7.2 Attestation key custody.** Cloudflare Workers secrets, not a laptop.
Rotation decided before the first signature, because signatures have to keep
verifying for years.

**7.3 Where the enrichment layer runs.** Cloudflare Worker plus KV or D1.
`CLAUDE.md`'s "no R2/D1 on the serving path" describes the **static export**
path settled in MODEL-2 and does not bind a new enrichment path — but the
wording must be updated so nobody enforces the old rule against the new thing.

**7.4 Source-terms audit** (`REV-2`) still runs, with one mitigation worth
noting: a licence determination made by *reading the licence* is the project's
own analysis, not redistributed scraped data. The enrichment model sits on
firmer ground than a data feed would.

**7.5 MODEL-3 is unblocked; MODEL-6 follows it.** The endpoint is now the plan.
The hold recorded in `CLAUDE.md`, `AGENTS.md`, `current.md` and
`post-mvp-loop.md` is superseded by this file and those documents need updating
in the same pass that starts the work. `docs/agent-commerce-assessment.md`'s
evidence bar is answered by 2.2: what is sold is the compliance determination,
not a ranking built on 14%-complete cards.

## 8. Still open

- Exact enterprise pricing and plan boundaries.
- Payment provider for card-funded keys; x402 facilitator choice.
- Outcome-logging consent and anonymisation design (`REV-9`).
- Signing scheme (`DEC-3` in the backlog), beyond custody in 7.2.

## 9. Order of work

1. **7.1** — the third state, in schema and CLI contract. Blocks the rest.
2. **Enrichment layer** — Worker, keys, rate limits, sandbox. Built for DPF.
3. **`commercial_use` and `data_residency` determinations**, written to the
   enrichment layer, never to cards.
4. **Subscriptions**, once the compliance answer returns something other than
   "undetermined".
5. **x402 credits.**
6. **Harness pitches**, with DPF as the live reference integration.
