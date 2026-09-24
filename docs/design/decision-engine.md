# The decision engine: ModelSpec's next architecture

*Design, written before the code. Discovery session with Jamie, 2026-09-24; §12 questions decided the same day. Status: proposed.*
*Vocabulary: [`CONTEXT.md`](../../CONTEXT.md). Decisions: [`docs/adr/`](../adr/).*

ModelSpec is off the market (the public domains serve a holding page, and billing is off) until this design is built, tested and proven. This document says what we are building, why, and in what order. It replaces the v1 ranking design for everything except the parts listed in §10 as reused.

---

## 1. Why v1 has to go

An independent audit on 2026-09-24 graded v1's answers, freshness and method F. The causes were structural, not bugs:

| v1 behaviour | Consequence |
|---|---|
| Each use case is a hand-picked list of benchmarks with fixed weights (`USE_CASE_PROFILES`) | Labs moved to new benchmarks. Every model released after May fell below the 0.50 coverage floor and was never ranked. On 2026-09-23 the coding #1 was an 18-month-old model. |
| Up to 35 of 100 points come from capability tiers declared on the card, a context-length bonus and a model-type bonus | Rankings rewarded documentation density, not measured performance. Old, richly documented cards won. |
| Constraints (context, type) were added as score, not applied as filters | A retrieval question could return an embedding model for a generation task. |
| Fixed normalisation ceilings | Frontier values clipped to the same 100; the top of the table flattened. |
| Flat, unsourced score blocks from a one-time bulk load | Many were estimated or copied between models. Nothing re-verified them. |
| Availability as a fixed list of platform fields on the card | Price, speed and data handling could not vary by provider, region or tier. |
| Unscored models dropped silently | Stale results looked authoritative. |

Every one of these is a case of the same mistake: **locking in a list that the world then moves past.** The design below has no fixed benchmark list, no fixed platform list, no fixed use-case list, and no score that measures anything but evidence.

---

## 2. What ModelSpec becomes

A **neutral decision engine**. Given a spec (a task, conditions on any facet, an objective) and optionally an inventory profile, it returns a decision:
- the results, each with a capability estimate, an interval and a probability of being the best choice;
- the models that **may qualify** but are unknown on a facet;
- what was eliminated and why;
- what each constraint costs;
- a snapshot ID that makes the decision reproducible.

It returns decisions. It does not proxy model traffic ([ADR 0001](../adr/0001-decisions-not-traffic.md)).

**Users** are who asks: an autonomous agent (the reference user; DPF is first), a builder, a platform engineer who writes an organisation's policy, a local runner, a researcher, a journalist, a compliance reviewer. **Use cases** are what they ask about, and those are unbounded, so the engine decomposes each request into capabilities at query time rather than looking up a prebuilt profile.

---

## 3. Principles

1. **No false negatives on capability.** A filter never silently drops a model that should have qualified. Unknown means "may qualify".
2. **No false positives on governance.** A rights, data or compliance filter never passes a model that should not pass. Unknown counts as not satisfied.
3. **Constraints filter; only evidence scores.** Declared tiers, context length and model type are facets to filter on or tradeoffs to show. They never add points.
4. **Nothing is locked in.** Benchmarks, domains, providers and facets are open, registered sets that grow without code changes ([ADR 0002](../adr/0002-learned-capability-model.md)).
5. **Every value is sourced, dated, qualified and independently verified** before it can reach a decision.
6. **Uncertainty is shown**: intervals and probabilities, not false-precision decimals.
7. **Explanation is a first-class result**, and it doubles as our own lie detector: a decision we cannot break down does not ship.
8. **Reproducible**: same spec, same snapshot, same decision.
9. **Neutral by structure**: no paid placement, referral fees or traffic margin; relationships (DPF, the decision-model vendor we use) are disclosed.

---

## 4. The domain model

```
                 ┌──────────┐ trained by ┌─────┐
                 │  Model   │───────────▶│ Lab │
                 └────┬─────┘            └─────┘
        offered as    │  measured by
      ┌───────────────┼───────────────────────────┐
      ▼               │                           ▼
 ┌──────────┐  sold by ┌──────────┐        ┌────────────┐  of   ┌───────────┐
 │ Offering │────────▶ │ Provider │        │  Evidence  │─────▶ │ Benchmark │─ tags ─▶ Domain
 └────┬─────┘          └──────────┘        └─────┬──────┘       └───────────┘
      │ facts                                    │ qualifiers: version, sub-category,
      ▼                                          │ effort, harness, tools, measured_by, date
 ┌──────────┐   read from   ┌─────────────────┐  │
 │   Fact   │──────────────▶│ Source snapshot │◀─┘
 └────┬─────┘               └─────────────────┘
      │ on                         ▲ re-checked by
      ▼                            │
 ┌──────────┐              ┌──────────────┐
 │  Facet   │ (registry)   │ Verification │── fails ──▶ Quarantine
 └──────────┘              └──────────────┘

 Snapshot = { verified Facts + verified Evidence + Capability estimates }, signed
 Decision  = f(Spec, Inventory profile?, Snapshot)      Outcome record → Evidence (first-party)
```

### 4.1 Entities

**Model.** Identity (`lab/model-id`), lab, class and model type, modalities, context and maximum output, open or closed weights, parameters (total and active; "not disclosed" is a state), architecture, licence rights, origin (lab jurisdiction, base-model lineage, weights hosting), lifecycle (release, knowledge cutoff, deprecation), features (tool calling, structured output, effort controls, batch, streaming), languages. Model-level values are **facts**.

*Lifecycle and the live archive:* a model is `active`, `deprecated` (its lab has announced retirement) or `retired`. Retired models stay in a **live archive**, fully sourced and browsable for reference, but out of the lineup: decisions exclude them unless a spec asks for them explicitly (`lifecycle in {retired}`). Deprecated models stay in decisions, with a warning and the retirement date.

**Provider.** Identity, jurisdiction, provider-level attestations (SOC 2 …), a registry entry. Replaces the fixed platform fields in `Availability`.

**Offering.** `(model, provider, region, tier)`. Price (input, output, cached, batch), speed (time to first token, throughput, always with method and source), rate limits and SLA, data handling (retention, training on customer data, zero retention), offering-level attestations (BAA …), fine-tuning, private deployment options, harness compatibility. **Speed belongs here**, not to the model. Self-hosted speed is a labelled estimate only.

*Which tiers are separate offerings:* a tier is its own offering **only when a guaranteed fact differs** (price, data handling or an attestation). In practice: standard API, enterprise or zero-retention API, and government cloud. Consumer chat apps are out of scope for now.

**Harness.** A registered scaffold with a version. Evidence and outcomes are recorded per harness, because the same model performs differently inside different harnesses. IDs are canonical `name@major.minor` (for example `claude-code@2.1`, `codex-cli@1.4`, `aider@0.9`, `openhands@1.2`, `dpf-native@1.0`). New harnesses are added by a registry PR. An outcome record from an unregistered harness is reported as `unregistered`, never as free text.

**Benchmark.** ID, versions, sub-categories, metric, unit and direction, the **domains it measures and its directness for each**, saturation status (computed from the spread of frontier evidence), who publishes results and under what terms, and whether it is live (dated by observation) or static (dated by publication).

**Evidence.** `(subject: model or offering, benchmark@version, sub-category, value, unit)` plus qualifiers: effort, harness, tools, configuration, `measured_by` (benchmark author, independent evaluator, provider self-report, ModelSpec, outcome protocol), evidence date and date type, source snapshot, verification status. Evidence is never copied between models. A missing value is a missing value, never an estimate.

**Fact.** `(subject, facet, value, state)`, where state is one of `known`, `unknown`, `not_disclosed` or `requires_contract`, plus source snapshot and verification status.

**Source.** A registered URL that one or more facts or pieces of evidence were read from, with how to fetch it (plain HTTP, conditional request, or rendered), how to normalise it, and which **cited regions** of it the facts depend on. Many facts share one source, so one fetch re-checks all of them.

**Source snapshot.** A dated retrieval of a source: the normalised content, a **fingerprint** of the whole page and of each cited region, and the retained copy. Governance facts diff their snapshots over time, and a change raises an alert.

**Verification.** `(target, verifier, method, outcome, date)`. The verifier must differ from the collector in agent and method. The outcome is `verified`, `mismatch` (re-crawl) or `unreachable` (re-crawl). Anything else is **quarantined** and excluded from snapshots.

**Facet (registry).** ID, subject type (model, offering, evidence), value type, **exact definition** (for example, which of lab jurisdiction, base-model origin and weights hosting "origin" means), tier (guaranteed or best-effort), risk direction (capability or governance, which sets the default unknown policy) and permitted sources. Adding a facet is a registry entry plus data, not an engine change.

**Capability estimate.** `(model or offering, domain, harness?, effort?) → value, interval`, produced by the capability model (§6.3) from verified evidence only.

**Snapshot.** A signed build of all verified facts, evidence and estimates, with an ID and a content hash. Decisions cite it.

**Decision, outcome record.** As in the decision contract (§7) and the outcome protocol (§9).

### 4.2 Where the data lives

- **Cards stay the human-editable source** for model facts and evidence, as YAML front matter plus prose. The flat `benchmarks.scores` block is retired. Its values are quarantined as legacy until re-sourced into evidence (MODEL-118). Quarantined values never reach a decision.
- **Offerings get their own files**, one per model per provider (`offerings/<provider>/<lab>/<model>.yaml`), each holding regions and tiers. They replace the fixed `Availability` platform fields.
- **Providers, harnesses, benchmarks, domains and facets are registries**, one file each, reviewed like code.
- **Source snapshots** are stored outside git (content-addressed); cards and offerings reference them by hash.
- **The build compiles everything into an in-memory knowledge graph**, then into the **snapshot**: a compact columnar index with bitsets per facet value, precomputed capability estimates, and the evidence needed for explanations. The snapshot is served statically and downloaded by the local library. FalkorDB remains an optional exploration tool.

---

## 5. Trust: how a value earns its way into a decision

```
collect ──▶ source snapshot ──▶ verify (different agent + method) ──▶ verified ──▶ snapshot
                                        │
                                        └─ mismatch / unreachable ──▶ quarantine ──▶ re-crawl
```

- **Two keys.** The agent that collects a value never verifies it. A model checking its own work shares its blind spots; that is how copied scores passed before.
- **New values are verified before first use.**
- **Every fact and piece of evidence names its sources.** Cards and offerings reference the registered source URLs each value came from, so re-checking never needs a search.
- **Change detection is deterministic and cheap; agents run only on change.** On each re-check, a plain fetcher retrieves each registered source, using conditional requests (`ETag`, `Last-Modified`) where the server supports them. It normalises the content, stripping navigation, timestamps and other volatile boilerplate, and compares fingerprints of the **cited regions**.
  - *Unchanged:* every fact citing that region is re-confirmed at no agent cost.
  - *Changed:* only the facts citing the changed region are re-extracted and re-verified by agents (two keys), and governance changes raise an alert.
  - *Unreachable:* the facts are quarantined after a grace period.

  Pages that need a rendered browser to show their content are marked as such, and cost more to check.
- **Re-check intervals match how often each kind of fact changes:**

  | Kind | Interval |
  |---|---|
  | Price, rate limits | weekly |
  | Governance facts (licence, data handling, attestations) | weekly fingerprint check; full re-verification and an alert on change |
  | Live leaderboard evidence | weekly, all entries on one board re-read on one date |
  | Static evidence (papers, system cards, launch posts) | verified once; fingerprint check quarterly for changes and dead links |
  | Model specifications (context, modalities, features) | at release, then monthly |
- **The premier set is computed, not hand-listed**, and recomputed weekly (expected size 100–200). A model is in it if any of these holds:
  1. it is in the top 10 of its class in any domain by current verified evidence (before the capability model exists: by rank on independent leaderboards under licences we may use);
  2. it was released in the last 90 days by a lab that had a model in (1) during the past year;
  3. at least three major providers offer it;
  4. a reviewer added it.

  Retired models leave the premier set.
- **Premier-set completeness gate.** Every guaranteed facet on every premier model is known, sourced and verified, or the build fails.
- **Recall tests.** A standing set of specs with independently established correct answers (starting with the independent audit's 20 questions). A change that drops a correct premier answer fails the build.
- **Freshness gates** (MODEL-111): the build fails if a premier model released more than 7 days ago has no verified evidence in its domains, or if a guaranteed fact's source snapshot is older than its re-check interval.
- **Excluded sources.** Publishers whose terms forbid our use are excluded entirely, and a guard test keeps them out ([ADR 0003](../adr/0003-excluded-sources.md)).
- **Governance facts are documented, never certified.** "The provider offers a BAA for this offering", with snapshot and date. Never "compliant".

---

## 6. The engine

A decision runs five stages. Stages 2–5 run in memory against the snapshot.

### 6.1 Resolve
Validate the spec against the facet registry. If free-text `task` is present, the decision model (Jev) classifies it into task type, domains, required capabilities and difficulty. Results are cached for similar tasks. Unknown facet names fail loudly; nothing is silently ignored.

### 6.2 Filter (three-valued)
Each condition evaluates to pass, fail or unknown per candidate, using bitset intersection over the index. The unknown policy comes from the condition, else the facet's risk direction:
- capability: unknown → **may qualify** (reported, not ranked with the results unless asked);
- governance: unknown → **not satisfied**, shown as "unverified: may qualify".

The grammar covers comparisons, windows, sets, `any`/`all`/`not`, existence, **relative conditions** (`coding >= model(x)`), **soft conditions** with a penalty, and **evidence conditions with qualifiers** (`swe_bench_pro >= 55 @independent @default_effort measured_after 2026-06-01`). The inventory profile's rules are applied as conditions first.

### 6.3 Estimate (the capability model)
Benchmarks are noisy measurements of latent capabilities. The capability model (MODEL-129) fits all verified evidence across all models and benchmarks:
- item-response or factor model with **learned** benchmark discriminations, and pairwise preference data fitted in the same framework;
- missing values handled natively and **not assumed average**: a lab that did not report a benchmark is not given a typical score for it;
- learned offsets for source kind (provider self-report vs independent) and for effort and harness;
- saturation handled by the model: a benchmark the frontier has saturated stops separating frontier models;
- evidence decays with age; each estimate carries an interval.

Estimates are computed at build time and shipped in the snapshot, so decisions only read them. **Until the capability model exists (the first slice), stage 3 shows the evidence per requested domain without blending it**, which is honest and already better than v1.

### 6.4 Optimise
One objective form per spec:
- single: `max`/`min` any numeric facet or estimate;
- lexicographic with tolerances ("fastest, then cheapest within 5%");
- weighted over normalised facets, with the normalisation shown;
- Pareto: return the non-dominated set.

Soft-condition penalties apply here. **P(best)** and **top-3 stability** come from resampling estimates within their intervals.

### 6.5 Explain
- **Why these won:** contributions per dimension, each with raw evidence (value, benchmark version, qualifiers, source, date, directness).
- **Why the others did not:** the funnel (count after each condition), per-model reasons, near misses.
- **How sure:** intervals, P(best), stability.
- **What constraints cost:** what relaxing each condition would gain.
- **Tipping points:** the weight changes that would flip the top result.

Levels: `none` (IDs, results, P(best)), `summary` (plus contributions, funnel, costs, tipping points), `full` (plus per-model reasons, the top 20 with every score, and a chart).

---

## 7. The decision contract

The request and response schemas, the condition grammar and the explanation levels are specified in the DPF integration spec (kept with the business documents) and are summarised in §6. The public contract document will be `docs/decision-contract.md`, versioned under the MODEL-59 rules: adding optional fields is compatible, and widening a field's range bumps the major version.

Transport: a **local library and CLI** answering from the offline snapshot (the primary path for agents), the hosted API, and MCP, all with one contract. The v1 `/v1/rank` endpoint stays until the cutover, then is retired with notice.

---

## 8. Facet catalogue (initial registry)

G = guaranteed for the premier set. B = best effort. Governance facets default to fail-safe unknowns.

| Subject | Facet | Tier |
|---|---|---|
| Model | class and output; modalities; context; maximum output | G |
| Model | open or closed weights; parameters; architecture | G / B |
| Model | licence rights (commercial use, user caps, output-training limits, fine-tuning) | G, governance |
| Model | origin (lab jurisdiction, base lineage, weights hosting; each defined separately) | G, governance |
| Model | release, knowledge cutoff, deprecation, lifecycle | G / B |
| Model | features (tool calling, structured output, effort controls, batch, streaming) | G |
| Model | languages; fits on a hardware class (estimate) | B |
| Offering | provider, region, tier | G |
| Offering | price (input, output, cached, batch) | G |
| Offering | speed (time to first token, throughput; with method) | B |
| Offering | rate limits, SLA | B |
| Offering | data handling (retention, training on customer data, zero retention) | G, governance |
| Offering | attestations: SOC 2, BAA availability (G); FedRAMP, ISO (B) | governance |
| Offering | fine-tuning; private deployment; harness compatibility | B |
| Evidence | any benchmark × sub-category, with qualifiers | B |
| Estimate | capability per domain, with interval | G for the premier set |
| Evidence | real-world outcomes by task type × harness (outcome protocol) | B |
| Derived | cost per task, cost per correct answer, relative comparisons, Pareto membership | follows its inputs |

**Domains at launch:** software engineering, engineering and STEM, maths, legal, medical, finance, writing, marketing and SEO (proxy evidence only, stated as such), agentic and tool use, vision and documents, multilingual. Sub-scores are harvested from benchmarks that already publish them (per-language and per-repository software results, legal task families, medical themes, subject breakdowns, preference-board categories).

**Out of scope:** exact download artifacts (specific quantized files). The engine names the model and offering; resolving a download is an optional post-process.

---

## 9. Our own measurements and the outcome protocol

ModelSpec produces first-party evidence ([ADR 0004](../adr/0004-first-party-measurement.md)). It starts narrow, publishes the method every time, and needs Jamie's approval before each step that spends money:
1. **Passive:** outcome records from agents acting on decisions, starting with DPF. Each record carries the task's description (never its content), the decision ID, the offering, harness and effort used, objective results, a verifier rubric, the human verdict with fixed reason codes, failure modes, and speed (time to first token, throughput). Privacy rules: closed vocabularies only, no client identifiers, a local inspectable log, opt in per project, minimum counts before publishing. Consented exploration removes selection bias.
2. **Active speed probes** on premier offerings.
3. **Runs of open benchmarks** to close gaps labs leave.

Outcome records feed the capability model as a labelled first-party source, detect silent model changes (a shift in success rate or speed with no announced change), and recalibrate probabilities. The protocol is intended to become open, so any agent can report through it. The full protocol is in the DPF integration spec.

---

## 10. Migration from v1

**Reused**
- Cards, evidence records (`BenchmarkEvidence`) and their provenance fields.
- Class fit (MODEL-100), as the first facet: class and output.
- Policy-check determinations (MODEL-80), as the paid determination service.
- Hardware fit, as the "fits on a hardware class" estimate.
- The unranked disclosure (MODEL-110), which becomes "may qualify".
- Authoring guides, as prompt guidance per result.
- The rank Worker's packaging and the static export pipeline.

**Retired**
- `USE_CASE_PROFILES` fixed benchmark weights.
- Capability-tier, context and type bonuses.
- Fixed normalisation ceilings.
- The flat `benchmarks.scores` block (quarantined, then re-sourced or dropped).
- The fixed platform fields in `Availability`.
- The `evidence_basis` label, replaced by per-evidence verification status and directness.

**Contract:** the decision contract is a new major version alongside `/v1/rank`, which is retired after the cutover. Legacy card fields left empty by the source exclusions (`artificial_analysis_url`) are removed in the same major version, so they cost no separate bump.

---

## 11. Build order

**Slice 1: the whole chain, narrow.** About 30 premier models across the main classes:
- every guaranteed facet verified by the two-key process;
- offerings on the major providers;
- stages 1, 2, 4 and 5 of the engine, with stage 3 as evidence shown per domain, unblended;
- the decision contract in the local library and CLI, with snapshot IDs;
- recall tests from the audit's 20 questions;
- the completeness gate and the excluded-source guard.

Acceptance: every recall test passes, no guaranteed facet is unknown, and each of the 20 answers is defensible to an independent reviewer. That slice alone replaces v1's scoring with honest filtering and visible evidence.

**Slice 2:** the capability model (MODEL-129) with intervals and P(best), validated by held-out prediction, historical replay and the recall set.

**Slice 3:** offerings and facets widened to the full catalogue; domain sub-scores; governance facts with snapshot diffs and change alerts.

**Slice 4:** the outcome protocol with DPF, and active speed probes.

**Slice 5:** the human downselect experience, saved specs and alerts, and the claims-versus-evidence pages. The downselect page is meant to be exceptional, not a form. It should make choosing a model exciting and intuitive, with benchmark graphs that pop. It is **research-led**: a dedicated UX research phase, contrasting prototypes and usability tests on the recall-set questions, all over the same decision contract and explanations that agents use (MODEL-147).

**Launch** is Jamie's call, after slice 2 at the earliest.

---

## 12. Decisions taken (2026-09-24)

1. **The premier set** is computed by rule, recomputed weekly (§5). Retired models move to the live archive, out of the lineup (§4.1).
2. **Offerings by tier:** a tier is a separate offering only when a guaranteed fact differs (§4.1).
3. **Re-checks:** intervals by kind of fact. Every value names its registered sources, and deterministic fingerprint checks mean agents run only when a cited region changes (§5).
4. **Harness IDs:** `name@major.minor`, a registry, and `unregistered` for unknown harnesses (§4.1).
5. **The legacy `artificial_analysis_url` field** is removed at the decision-contract cutover (§10).
6. **First-party measurement** is a decision: passive (DPF) first, then speed probes, then open-benchmark runs, each approved before any spend (§9, ADR 0004).

## 13. Open questions

None blocking slice 1. Questions will be added here as the build raises them.
