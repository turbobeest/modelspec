# Design brief: the facet board (decide page, pass 2)

**For:** a Claude Design pass that produces a handoff package in the format of
[`../handoff/core-flow/`](../handoff/core-flow/README.md).
**From:** Jamie's design session, 2026-09-27. Every decision below is his.
**Replaces:** the arrive screen and the spec panel of the core flow. Everything
downstream of the spec (narrowing, canvas, shortlist, table, why) stays and is
restyled only where this brief says so.

## Why this pass exists

The core flow starts from a sentence: "Describe your task". A keyword table
turns it into conditions. Two live runs on 2026-09-27 show why that cannot work:

- "Coding agent for a TypeScript monorepo on a budget" became *context ≥ 200K*
  (invented from "monorepo"), dropped "TypeScript", and still named the most
  expensive model "Best value".
- "Something private I can host … for customer support" found no domain, so it
  silently ranked on *software engineering*, read "private" as *open weights
  only*, then asked whether the provider trains on your data.

The niche reasons an answer is wrong are constraints the person never wrote
down. No parser finds what was not said, and a frontier model would only guess
better. **The human page does no interpretation at all.** It shows every
criterion that can move the answer, and the person sees the answer change as
they set them.

The page is free, used by a person, with no AI anywhere in it. Agents use the
CLI and API, which is where interpretation belongs: the agent is the model.

## Principles

1. **Everything up front.** The first screen is the full set of facets, not a
   text box. No wizard, no steps.
2. **Three states per facet** (decided):
   - **Doesn't matter** is the default. The row is greyed, never hidden, so the
     board always shows what was and was not chosen.
   - **Must** is a hard gate, with a threshold where the facet has one
     (context ≥ 200K, ≤ $0.10 per task, BAA required). Failing models are
     excluded and stay visible as excluded.
   - **Prefer** is a weight slider. It ranks and never excludes.
   Gates and weights must look different. The existing rule holds: *conditions
   filter; they never add points.*
3. **The answer is always on screen and always live.** No "Run decision"
   button. Every control shows how many models survive before it is used.
4. **Never claim an order the evidence cannot support** (decided). When
   several models fit and their capability intervals overlap, the top of the
   results says so as one group: "These 4 fit. The evidence can't separate
   them." Then show what breaks the tie: cheapest, fastest, open weights, most
   independently measured. A single #1 appears only when its interval
   separates it from the rest.
5. **Benchmarks are the person's to distrust.** Capability is an estimate
   learned from every benchmark in a domain. The person can switch off any
   benchmark they don't believe, and the estimate is refitted without it.
6. **Unknown is a visible third state.** "May qualify" never disappears. A
   facet the catalogue has not measured says so rather than looking empty.
7. **Keep the core-flow outputs.** The narrowing card, the trade-off canvas
   and the decision table are first-class and stay. They are good; the data
   under them is what has to be right.

## The facet board

Group the facets so a person can scan the page in one pass. Groups and
coverage come from the live vocabulary
(`https://modelspec.dev/api/decision/vocabulary.json`, snapshot
`snap_f0a30b23be5070c7`, 32 models, 38 offerings). The design reads that file
and never keeps its own list. "n/32" is how many models have a value.

| Group | Facets (coverage today) | Natural control |
| --- | --- | --- |
| **What it does** | Model class (32/32), input modalities (32), output modalities (32) | Must only (pick one class) |
| **What it's good at** | Capability per domain, 12 domains with lineup coverage: software engineering, chat and preference, agentic and tool use, engineering and STEM, maths, reasoning, legal, medical, writing, multilingual, vision and documents, retrieval. Estimated from 39 benchmarks. Finance and marketing exist in the registry with no coverage yet. | Prefer (weight); Must = a floor |
| **Budget** | Cost per task at your token counts (38/38 offerings), input and output price, cached and batch price | Prefer (weight) or Must (cap) |
| **Size of work** | Context window (32), max output tokens (19) | Must (floor) |
| **Where it runs** | Open weights (32), provider (38), inference region (38), private deployment (0), fits hardware (0) | Must |
| **Your data** | Trains on customer data (35 offerings), retention (25), zero retention available (15), HIPAA BAA (20), SOC 2 (7) | Must |
| **Licence** | Commercial use (28), user cap (27), training on outputs (27), fine-tuning rights (27) | Must |
| **Features** | Tool calling (25), structured output (25), streaming (24), effort controls (25), batch (16) | Must or Prefer |
| **Provenance** | Lab jurisdiction (20), lifecycle (32), release date (31) | Must |
| **Speed** | Time to first token (0), throughput (0) | Prefer (weight) |

Two design problems the board must solve, not hide:

- **Empty facets.** Speed, rate limits, SLA, FedRAMP, ISO 27001, private
  deployment, fits-hardware, parameters and languages have no values for any
  model yet. Show them in a collapsed "Not yet tracked" group, with the reason.
  A Must on an empty facet would make everything "may qualify", so disable
  Must there and say why.
- **Density.** About 40 usable facets have to scan in seconds. Two levels
  only: the group line (its state summary and survivor count) and the
  expanded facets. Most people will touch five or six.

### Benchmarks under a domain

Expanding a capability domain lists the benchmarks it is estimated from, each
with a switch (on by default), its directness (direct or proxy), how many
lineup models it covers and its date. Switching one off refits the estimate.
That takes a second or two, so show a short busy state on the domain only.
The "Measured by" single-benchmark drill-down stays as it is today.

### Templates

About eight, in a collapsible section at the top of the page that collapses
to a small info button once the person has used the board. A template is a
set of facet states, not a sentence. Choosing one sets the board and shows
*why* each facet is set that way, so templates teach the three states by
example. Suggested set (the design may change it):

1. Coding agent on a budget
2. Private assistant you host yourself
3. Regulated data (BAA, zero retention, no training)
4. Maths and proofs
5. Retrieval embeddings
6. High-volume, cheapest that is good enough
7. Long documents
8. EU-only data handling

Each template card shows its live "N fit · M may" count, as today.

## The answer area

Top to bottom, beside or below the board:

1. **Narrowing card** (exists): counts per condition in the order set. Now it
   also counts Prefer weights as "ranking on …".
2. **The answer:** the tied group and its tie-breakers (principle 4), or a
   single separated pick. Plain-language scale, not z-scores: "1.44 ± 1.10"
   means nothing to a person.
3. **Trade-off canvas** and **decision table** (exist).
4. **Why** panel (exists): contributions, evidence and provenance, condition
   checks, what each condition costs, near misses, why not X, offerings.

## The 3D view with gravity

`web3d/explorer.html` (the MODEL-24 force-directed explorer) comes back as a
view of the **same decision**, for play:

- Prefer weights are gravity. Models that score well on what you weight drift
  to the centre; moving a slider visibly moves the cloud.
- Must failures drift outward and fade. They are not removed.
- The tied group from the answer area is highlighted.

It is a toggle beside Canvas first and Table first, not a separate site.

## Saving (phase 1: URLs, not accounts)

A decision is already a URL. Phase 1 saves a board as a URL, plus a list of
saved boards in browser storage. The design should also cover the view that
comes later with accounts: **"what your answer became"**, meaning a saved
board re-run against a newer snapshot, showing what entered, what left and
why. Login itself is a later ticket, coordinated with the work on access and
keys. Design the view; don't design sign-in.

## Out of scope

- Any free-text task input, parser or LLM on this page.
- Login and sign-in screens.
- Mobile (as in the core flow, a later pass).
- Billing, keys, x402.
- Changing the ranking floors or the neutrality text.

## Engine and data work this depends on

These are tickets, not design. The design should assume they land.

1. **Result limit hides contenders.** The page asks for 20 *offerings*; every
   qualifying offering past that is shown as "Excluded, outside requested
   result limit". On 2026-09-27 that hid Claude Fable 5.1, GPT-6 Astra and
   DeepSeek V4 Pro. A live answer must rank the whole qualifying set.
2. **Tie-aware answer.** The engine flags `not_separable`, but the page and
   the roles still name a #1. Recall Q01 to Q09 fail for this reason.
3. **Refit without chosen benchmarks.** `fit_capabilities` in
   `decision/capability.py` runs at snapshot build. The snapshot keeps the
   evidence rows, so the engine can refit per request with an excluded set.
   A throwaway timing at lineup scale (551 observations) took about 1 s in
   CPython; cache by excluded set.
4. **Must/Prefer on every facet.** Today `where` holds gates and `optimize`
   holds only capability, cost and speed weights. Prefer on other facets
   (for example "prefer zero retention") needs `optimize` to accept them, or
   a soft condition that ranks without excluding.
5. **Data gaps that the board will expose:** speed (0/38), private deployment
   and fits-hardware (0/32). The self-host need cannot be answered well until
   these are researched.
6. **Stale copy:** "A small classifier turns this into conditions" (it is a
   keyword table) and "SWE-bench Pro is preselected for Measured by" (the
   estimate is preselected since MODEL-167). Both go with the text box.

## Evidence

- Research principles and rejected patterns: [`../../ux/downselect-research.md`](../../ux/downselect-research.md),
  [`../../ux/prototype-comparison.md`](../../ux/prototype-comparison.md).
- Current core flow: [`../handoff/core-flow/README.md`](../handoff/core-flow/README.md),
  code in `web/src/decide/`.
- Recall questions and expected answers: `tests/recall/`.
- Decision contract: [`../../decision-contract.md`](../../decision-contract.md) (1.7).
