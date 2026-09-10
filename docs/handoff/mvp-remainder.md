# MVP remainder: MODEL-5, 7, 30, 34

Four tickets. **None of them can be closed by an agent working alone**, and that
is not a limitation to work around — it is the actual shape of the work. Two need
elapsed time or Jamie's hands on an external console; two need product decisions
that are his to make.

Grok Build's job here is to be a **preparer**, not a decider: gather the evidence,
lay out the options with their consequences, and reduce each decision to
something Jamie can answer in one line. Do not implement a choice he has not made.

---

## MODEL-5 — Daily model research

**Status: needs seven consecutive days of elapsed time. It has run once, on
2026-09-10.** No amount of work compresses this.

What an agent *can* do, and should:

* Watch the daily run. Each morning, check the previous night's
  `daily-research.yml` run: did it complete, did it open a PR, did the PR
  validate. Report a one-line status; do not merge it. The ticket's design is
  human-merged and that stays.
* Fix the two real gaps found in verification, which do *not* need seven days:
  * The survey only covers **new models from models.dev**, while the ticket asks
    for every card against every listed source.
  * The seeder creates only a `models_dev_url` source and populates neither
    licence nor per-source freshness. `models/openai/gpt-6-astra.md` still has
    `license_type: null` and empty `last_scraped_*` fields.
* **Prove the failure path deliberately.** The acceptance says the last good data
  must survive a failed run. Break a source on purpose in a scratch branch,
  observe, restore. Do not wait seven days to discover this does not work.

**Close only when:** seven consecutive successful runs exist, a human-merged PR
has actually happened, and the deliberate-failure test passed.

---

## MODEL-7 — Serve the benchmark wiki at benchgraph.dev

**Status: blocked on Jamie in Google Search Console.** The site serves; the
remaining acceptance is domain verification and sitemap submission, which needs
an account an agent does not have.

What to do:

* Verify everything that *is* checkable from outside: the sitemap builds, is
  reachable, is well-formed, and its URL count matches the build (1,108 at last
  count). Cache-bust every live fetch — `?cb=<epoch-ms>` plus
  `Cache-Control: no-cache` — because a stale edge cache has already produced one
  wrong conclusion here.
* Prepare Jamie's step precisely: the exact URL to visit, the verification method
  to choose, the sitemap URL to submit. One short paragraph, no research homework.
* Then stop. Do not attempt to verify the domain.

---

## MODEL-30 — Two defects in the ranking profiles

**Status: three open questions, all Jamie's.** Prepare each; decide none.

1. **`clip_score` normalization** is unresolved. Establish what the metric's
   real range and direction are from a primary source, state what the current
   code does with it, and show which models' rankings change under each option.
2. **All-zero default cost weights.** Every profile currently has
   `cost_weight: 0.10` reverted to zero by default, so price does not influence
   any default ranking. Jamie previously set all 51 profiles to 0.10 and it made
   rankings *worse* — GPT-5.4 nano topped coding on price alone — so cost became
   a query parameter instead. The question is whether zero-by-default is the
   intended policy or an accident of that revert. Show the top 5 for `coding`
   at cost weights 0.0, 0.05 and 0.10 so the trade-off is visible, not described.
3. **`image_generation`** is not an offered profile, and `speech_to_text`
   currently produces **0 precomputed rankings**. Either make them offered and
   defensible, or exclude them explicitly. A profile that silently returns
   nothing is the worst of the three states.

**Deliverable:** one comment on MODEL-30 with three questions, each with options,
each with the concrete before/after a reader can judge. Then wait.

---

## MODEL-34 — Ranking under unequal evidence

**Status: implemented and shipped. Open only because the default is a product
decision.**

A model is ranked only if its measurements cover **≥50% of a profile's benchmark
weight across ≥2 benchmarks**. Everything else is reported as explicitly
*unranked* with a reason, rather than scored zero and buried.

The consequence, which is the whole question: **coding ranks 122 models and
withholds 1,103.** That is clearly right for a tool dpf calls — it should never
recommend a model on absent evidence. It is arguably too aggressive for a person
browsing modelspec.dev, who may reasonably want to see the catalogue.

What to prepare:

* The top 10 for `coding` and `reasoning` at coverage floors of 0.25, 0.50 and
  0.75, with the ranked/withheld counts at each. Numbers, not adjectives.
* Whether the wizard and the CLI should use **different** floors — the honest
  possibility nobody has costed. dpf wants conservatism; a browser wants breadth.
  Both can be true, and the machinery already separates the two surfaces.
* One unresolved design disagreement, recorded in
  `docs/incomplete-evidence-ranking.md`: the earlier analysis says explicitly
  **not to sort by the lower endpoint**, and the implementation does. The
  eligibility floor answers that objection but produces a weaker claim than the
  strict-dominance partial order that was recommended. Say plainly whether that
  matters in practice, with an example where the two orderings differ.

**Do not change the floor without Jamie's answer.** It is a one-line change and
it decides what a visitor sees.
