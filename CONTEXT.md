# ModelSpec

ModelSpec is a neutral decision engine for AI models. It holds sourced, verified facts and evidence about models and the ways they can be obtained. It answers "which model should handle this task, under these constraints, right now, and why?" for people and agents.

## Language

### What is catalogued

**Model**:
A trained model with a stable identity, independent of who serves it.
_Avoid_: LLM (a model need not be one), checkpoint, SKU

**Class**:
What a model consumes, emits and decides: generate, embed, rerank, classify or decide, and so on. It is a view over the model type.
_Avoid_: category, kind, type (when meaning class)

**Provider**:
An organisation that serves models for use, through an API, a cloud, or an app.
_Avoid_: platform, vendor (when meaning a server of models), host

**Lab**:
The organisation that trained a model.
_Avoid_: creator (in prose), provider (when meaning the trainer)

**Offering**:
A model as one provider sells it in one region under one account tier. Price, speed, limits, data handling and attestations belong to the offering, not to the model.
_Avoid_: endpoint, deployment, listing, SKU

**Harness**:
The agent scaffold a model runs inside (for example a coding agent), which changes how well the model performs a task.
_Avoid_: agent (when meaning the scaffold), wrapper, tool

**Premier set**:
The models whose guaranteed facets must be complete and verified: the frontier of every class, plus anything a major lab released in the last 90 days.
_Avoid_: top models, featured models

### What is known about them

**Fact**:
One sourced value about a model, offering or provider on one facet, with the source snapshot it came from.
_Avoid_: attribute, field (when meaning the sourced value)

**Evidence**:
One measured result: a score of a model or offering on a benchmark version, with its conditions (effort, harness, tools), who measured it, and when.
_Avoid_: score (alone), result, benchmark data

**Benchmark**:
A named, versioned measurement procedure, with its sub-categories and the domains it measures.
_Avoid_: eval (in prose), test suite, leaderboard (a leaderboard publishes evidence; it is not the benchmark)

**Domain**:
An area of capability that benchmarks can measure (software engineering, legal, medical, …). It is an open, tagged set.
_Avoid_: use case (a use case is what a user wants; a domain is what evidence measures), profile

**Directness**:
How closely a benchmark measures a requested capability: direct, proxy, or none. It is relative to the capability asked about, not a property of the evidence alone.
_Avoid_: relevance, confidence

**Capability estimate**:
The engine's estimate of a model's capability in a domain, with an interval, computed from all verified evidence.
_Avoid_: rank score, rating, composite score

**Source snapshot**:
A dated, content-hashed copy of the document a fact or piece of evidence was read from.
_Avoid_: citation (a citation is a link; a snapshot is the retained copy)

**Verification**:
An independent re-check of a fact or piece of evidence against its source snapshot, by a different agent and method from the one that collected it. Outcomes: verified, mismatch, unreachable.
_Avoid_: validation (schema checks), review

**Quarantine**:
The state of a fact or piece of evidence that failed or has not passed verification. Quarantined values never reach a decision.
_Avoid_: pending, draft, flagged (as a state)

### How questions are asked and answered

**Facet**:
Something a spec can constrain or optimise: a registered, exactly defined property of a model, offering or evidence, with a tier and an unknown policy.
_Avoid_: filter (a filter is a use of a facet), field, attribute

**Guaranteed facet**:
A facet that is complete and verified for every model in the premier set, so a filter on it is final for that set.
_Avoid_: core facet, required field

**Best-effort facet**:
A facet that may be unknown for some models; every answer that uses it counts and lists those models.
_Avoid_: optional facet

**Unknown policy**:
What a condition does with a model whose value is unknown. On capability facets the model is listed as "may qualify" and never dropped. On governance facets it counts as not satisfied.
_Avoid_: null handling, default

**Governance fact**:
A fact about rights, data handling, residency, attestations, origin, security posture or indemnity. It is always reported as documented, never as compliance.
_Avoid_: compliance data, policy fact

**Inventory profile**:
The set of offerings, local models, harnesses, hardware and standing rules one customer can actually use, registered once and referenced by decisions.
_Avoid_: account, config, environment

**Spec**:
A request for a decision: the task, conditions on facets, an objective, how unknowns are handled, and how much explanation to return.
_Avoid_: query (in prose), request, filter set

**Decision**:
The engine's answer to one spec against one snapshot: results with estimates and probabilities, the models that may qualify, the eliminations, and the explanation. It has an ID.
_Avoid_: recommendation, ranking (a ranking is one part of a decision)

**Explanation**:
The part of a decision that says why each result won, why the others did not, how sure the engine is, and what each constraint costs.
_Avoid_: justification, rationale, debug output

**Snapshot**:
A signed, versioned build of every fact, piece of evidence and capability estimate. The same spec against the same snapshot always gives the same decision.
_Avoid_: export, dump, release

**Determination**:
A sourced yes, no or unknown answer to whether an offering satisfies a customer's own policy. Documented facts are free; determinations are a paid service.
_Avoid_: approval, compliance check

**Outcome record**:
A privacy-safe report, from an agent that acted on a decision, of how the chosen offering performed on the task. It carries fixed fields, numbers and codes, never client content.
_Avoid_: telemetry (in prose), feedback, log

**Excluded source**:
A publisher whose terms forbid ModelSpec's use of its data. Nothing sourced from it may enter the catalogue; the list lives in `tests/test_removed_sources.py`.
_Avoid_: banned source, blocked site
