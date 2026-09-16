# Revenue backlog

**Proposed 2026-09-16.** Derived from [`BUSINESS_CONTEXT.md`](BUSINESS_CONTEXT.md),
measured against the tree in [`repo-audit-2026-09-16.md`](repo-audit-2026-09-16.md),
and constrained by [`../agent-commerce-assessment.md`](../agent-commerce-assessment.md).

These are **proposals, not Linear tickets**. `REV-n` are working ids so the docs
can cross-reference; each becomes a `MODEL-n` when Jamie creates it. Highest
existing id at the time of writing is MODEL-60.

Standing rules in [`../handoff/README.md`](../handoff/README.md) apply to every
item here, especially: absence is data, a wrong answer is worse than no answer,
and verify by running.

## The two sentences that order this list

The plan's strongest revenue lever is enterprise governance — licence, origin
and residency gating. **Two of its four fields are empty** (`commercial_use` 1%,
`data_residency` 0%), so it cannot be sold today, and no payment rail changes
that.

Everything a paying customer would get from `recommend` today, they can get free
by cloning the repo. **The billable difference has to be something a clone
cannot reproduce** — a policy gate over fields nobody else maintains, a signed
attestation, an alert on change, or an eval on their own tasks.

So: fields first, then the free commands that prove the fields are worth
something, then the paid surface. Not the other way round.

---

## Gate 0 — decisions before any of this is built

### DEC-1 — Resolve `recommend` against the MODEL-3/MODEL-6 hold

**Jamie only. Blocks REV-6 (hosted), REV-8 (priced) and anything with a price.**

[`BUSINESS_CONTEXT.md`](BUSINESS_CONTEXT.md) §11 says ship hosted `recommend` in
30 days. `CLAUDE.md`, `AGENTS.md`, `docs/handoff/current.md` and
`docs/handoff/post-mvp-loop.md` all say do not start MODEL-3 or MODEL-6, resting
on an assessment that set an explicit evidence bar for charging at all.

Both documents are treated as current. They cannot both be. One of three
outcomes, written into the decision log of whichever document loses:

1. the assessment's bar stands → `recommend` waits on `REV-4`, `REV-5`, `REV-11`;
2. the bar is revised → say which part, and why the evidence now justifies it;
3. `recommend` ships free and unpriced → MODEL-3 without MODEL-6, which the
   assessment already endorses ("ship attestation unpriced").

**Recommendation: 3, then 1.** Unpriced shipping tests demand, costs no
credibility, and is the assessment's own advice.

### DEC-2 — Publication tiering

Option A, B or C in [`data-policy.md`](data-policy.md). Blocks `REV-7`'s hosted
half and any data-licensing conversation. **Recommendation: A now, B on evidence
of demand, not C.**

### DEC-3 — Signing scheme and key custody for attestation

Blocks `REV-8`. A signing key held only on Jamie's laptop is a founder-dependency
of exactly the kind section 10 says makes the company unsellable. Decide custody
and rotation before the first signature, because the first signature is the one
that has to keep verifying for years.

---

## Track A — make the governance product real (do these first)

### REV-4 — Determine `commercial_use` across the corpus

**The highest revenue-per-hour item in the repository.** 8 of 1,339 cards filled.
The plan's strongest lever depends on it.

Not a scrape. A determination, recorded with its source, in four tiers of
descending confidence:

| Tier | Cards | Method | Confidence |
|---|---|---|---|
| OSI-standard (`apache-2.0`, `mit`) | 683 | licence text; one mapping table, cited by clause | deterministic |
| Family licences (`llama-community`, `gemma`, `deepseek`) | 169 | **three** readings of the family licence, each conditional (Llama's MAU threshold, Gemma's use policy) | high, conditional |
| `proprietary` | 150 | provider terms; ~20 providers cover the set | per-provider, dated |
| `other` + null | 336 | per-card research | **leave null** until each is done |
| `cc-by-nc-4.0` | 1 | no | deterministic |

**A bool cannot express tier 2.** `schema/card.py:162` has
`commercial_use: bool | None`; Llama-community is neither true nor false, it is
allowed-subject-to-conditions. `schema/enums.py:144` already defines
`UsePermission` (`allowed` / `restricted` / `prohibited` / `unspecified`) — the
right shape exists and is unused here.

Widening that field's range is a **contract major bump under MODEL-59**. Plan it
once, with `REV-5`, rather than twice.

**Done when:** ≥75% of cards carry a non-null `commercial_use` with a
`commercial_use_source` naming the licence or terms URL and the date it was
read; the mapping table is in code with tests, not in prose; tier 4 is still
null and the count is published; no card was filled from a model's memory of a
licence.

**Do not:** infer commercial use from `license_type` for tiers 2–4. Rule 2 — the
1,589 wrong "it fits" answers came from exactly this kind of plausible inference.

### REV-5 — Determine `data_residency`

0 of 1,339. `schema/card.py:429` — `data_residency: list[str] = []`, and an
empty list is currently indistinguishable from "not researched", which violates
rule 1 on its face.

Splits cleanly:

- **Open weights** — residency is a property of where *you* run it, not of the
  model. The honest value is a sentinel (`self-hosted`), not a country list.
  Mechanical for ~1,100 cards once `weights_available` is derivable.
- **Hosted/proprietary** — the provider's published region list, dated. ~20
  providers cover the 150 proprietary cards. Several publish nothing, and those
  stay null.

**Done when:** every card is either residency-typed or explicitly null with a
reason; the empty-list ambiguity is gone from the schema; the provider region
table carries a URL and a read date per row.

### REV-6 — `modelspec offline policy-check`

The enterprise lead magnet, and the thing that proves `REV-4` and `REV-5` were
worth paying for. **Free, offline, local** — same posture as `rank` and `fit`.

```
modelspec offline policy-check --policy policy.yaml [--model <id>] [--json]
```

A policy file states licence, origin, residency and commercial-use requirements.
Output says, per model, pass / fail / **undetermined**, and on a fail names the
constraint that eliminated it — which is also the draft registry description's
promise in §13 ("on failure, returns which constraint eliminated every option").

**The whole product is the third state.** "Undetermined" is what a governance
buyer is actually paying to eliminate, and it is the one answer no competitor
gives. A tool that silently treats null as pass is worse than no tool, because a
model gets deployed on it.

Exit codes and envelope: additive under MODEL-59, but a **new command is a
contract change** — write it into [`../cli-contract.md`](../cli-contract.md) in
the same PR, not a docs pass afterwards.

**Depends on:** REV-4, REV-5. Buildable against partial data; do not ship it
while `commercial_use` is at 1%, because every answer would be "undetermined".

### REV-7 — `modelspec offline diff` / watch

Diff two snapshots and report what changed that matters: new models, ranking
movements, licence or policy-field changes, models that newly pass or newly fail
a given policy. Free and local. The hosted half — alerting, per §6 `watch` — is
the subscription hook and waits on DEC-1/DEC-2.

Cheap to build (both snapshots are already on disk), and it is the only endpoint
in §6 with a natural recurring shape.

---

## Track B — the moat, which has to start before the paid surface

### REV-8 — Attestation, unpriced

Straight from [`../agent-commerce-assessment.md`](../agent-commerce-assessment.md)
§2, which argued attestation is the product and the recommendation is not,
because the recommendation is arithmetic any caller can redo.

A signed, timestamped envelope over: the constraints asked, `build.commit`,
`export_schema_version`, ranking-method version, the floors in force, the
`evidence_basis` of each row, and the result. Plus `modelspec verify
<attestation>` and a published verification method.

**Ship it unpriced.** Find out whether anyone wants a provable recommendation
before charging for one. It is also the only response shape that resists
free-riding and resale, per the x402 analysis in §5 of that assessment.

**Depends on:** DEC-3.

### REV-9 — Consented outcome logging

§9 calls this the **primary data moat** now that latency is cancelled, and §11
says it must be in `recommend` from the first release. It cannot be
retrofitted — data not collected in month one does not exist in month twelve.

Local-first and opt-in: the CLI writes `~/.modelspec/outcomes.jsonl` only after
an explicit opt-in, with a documented, separately-consented upload path.

**Never record:** prompt or task content, API key values (the CLI reads only
*presence* of keys, per §6, and that must stay true), customer identifiers,
anything not needed to answer "was this recommendation adopted, and did the task
succeed".

**Done when:** the consent flow is legible to a human reading the terminal, the
schema is documented in the CLI contract, opting out is one command, and a
privacy note in `docs/business/` states exactly what leaves the machine.

### REV-10 — Receipts, and a savings method that survives a customer checking it

§7.5 wants receipts carrying *"estimated savings"* — "recommended X over Y, ~$340/month
less at your volume".

**This is a trust landmine and needs to be specified before it is built.** A
fabricated or hand-wavy savings figure on a receipt is the fastest way to lose a
positioning built entirely on evidence discipline. The figure must be derived
only from published per-token prices with a read date, an explicitly stated
volume assumption supplied by the caller, and the alternative it is measured
against named. Where a price is unknown, the receipt says so and shows no
number — a null beats a guess, on an invoice most of all.

**Depends on:** REV-8 (receipts should ride the attestation envelope).

---

## Track C — credibility and sellability

### REV-11 — Benchgraph coverage, told honestly

§11 item 1, restated against measurement: not "7 active with 0 models
reporting", but **164 of 1,112 pages have any model reporting, and 948 have
none** (see the audit). Four ids carry a third of the corpus.

Work: a disposition per page that renders honestly on the site; a noise filter
for entries like "Beyond MSE" and "benchmark_results" that is a **rule in code**,
not a hand-curated list (rule 3); and a published coverage number that a first
visitor can see without being sold to.

Do not fix this by deleting the tail. A page saying "no model in this catalogue
reports this benchmark" is the catalogue declining to answer, which the handoff
README already identifies as the thing that has to *read* as rigour.

### REV-12 — Founder-independence audit

§10: *"Runs without the founder: automated data refresh, documented ops, no
single-person steps."* Every item below is a measured single-person step.

- **MODEL-5's Actions token.** The canonical example: the daily research loop
  cannot merge anything until Jamie creates a credential. An acquirer sees a
  data pipeline that stops when one person is unavailable.
- **CLA sign-off.** 10 of 50 commits carry `Signed-off-by`. All 50 are the
  owner's, so IP is clean today; the gap becomes real on the first outside PR,
  and diligence will diff the two logs.
- **Operational runbook.** Firecrawl budget and reset date, Cloudflare Pages
  deploys, the 25 MiB export cap (MODEL-39), what to do when a build fails.
- **Paths in docs.** `/Users/terbeest/...` appears in `CLAUDE.md`,
  `post-mvp-loop.md` and `worktrees.md`. Harmless daily; it is a tell during
  diligence, and it breaks for anyone else on day one.

### REV-13 — Agent-readable docs and registry listings

§11 items 4–5 and §13: under 800 words, OpenAPI where an endpoint exists, a full
worked request/response, every error with its fix, rate limits, test keys, and
one task-worded page per endpoint.

**Gated on DEC-1.** The docs describe a surface; write them when the surface is
decided. The `<60`-word registry description in §13 is good and can be reused
verbatim.

### REV-2 — Third-party source-terms audit

**A sale blocker, and the quietest one.** `LICENSE` says third-party terms govern
the material cards draw on. §9 flags it. Nobody has checked.

Enumerate every source domain cited across `models/**` and `benchmarks/**`,
record each one's position on redistribution and commercial reuse with the date
its terms were read, and add a CI guard so a new source domain cannot enter the
corpus without a terms entry (rule 3: the limit goes in code).

Until this exists, a data-licensing deal cannot be signed honestly and an
acquirer's diligence has an open question with no owner.

### REV-3 — Publish the honest-broker rule

[`../agent-commerce-assessment.md`](../agent-commerce-assessment.md) §3 stated
it and said it *"should be written into the project's terms before any money
moves, not after someone offers"*:

> Charging the consumer of a recommendation is compatible with being an honest
> broker. Charging the subjects of one is not.

Make it a published, machine-checkable commitment — no referral fees, no paid
placement, no provider-paid visibility, ever — surfaced in the ranking policy
JSON alongside the floors, so an agent can check it rather than trust it. Cheap,
and it is the whole of §5's positioning in one file.

---

## Order of work

1. **DEC-1, DEC-2, DEC-3** — three decisions, no code.
2. **REV-4, REV-5** — the fields. Nothing sellable exists until these land.
3. **REV-6, REV-11, REV-3** — the free commands and the credibility pass that
   prove the fields are worth money.
4. **REV-8, REV-9** — attestation and outcome logging, unpriced, before any
   paid surface exists, because they cannot be retrofitted.
5. **REV-2, REV-12** — diligence debt. Start early; both are slow and neither
   can be crammed before a sale.
6. **REV-7, REV-10, REV-13** — once there is a surface and a customer.

The month-4 checkpoints in §11 are unchanged and are the right test. Note that
checkpoint 1 (coverage credible, outcome data accumulating) maps to `REV-11` and
`REV-9`, and checkpoint 4 (a serious enterprise governance conversation) is
`REV-4` plus `REV-6` — so the ordering above is also the shortest path to two of
the four.
