# BenchGraph active catalogue eligibility

Accepted by the operator on September 8, 2026. Supersedes the objective of producing a page for every census candidate. The census is a discovery backlog, not a benchmark count or publication target.

## Product contract

The default catalogue serves comparisons of current frontier and open models. A candidate qualifies only when its distinct identity, measurement contract, current model coverage, recent result evidence and usefulness have been verified. The rolling freshness window is 60 days, inclusive. Benchmark creation date is not the freshness test.

Keep benchmark metadata and eligibility evidence separate. Existing `freshness.researched`, `freshness.reviewed`, source access dates, README edits and repository activity do not establish recent evaluation results. Existing `status: active` is not proof of catalogue eligibility.

## Required evidence

1. A canonical benchmark identity and direct supporting source. Harness aliases, duplicate names, task families, releases and subsets must have explicit relationships; they do not each count as independent benchmarks. Version-specific result eligibility does not qualify all versions of a family.
2. A defined task, metric and evaluation protocol, with source-supported reasoning about whether results still meaningfully distinguish relevant models. Saturated or unknown-usefulness candidates do not enter the active set merely because they were rerun.
3. At least one current frontier model and one current open model from different organizations, in the benchmark's domain. Qualifying results must share the benchmark version, evaluation configuration and score unit. Model-dependent reasoning budgets or scaffolds must be disclosed in the configuration and comparison limitations; incomparable runs must not be grouped by a generic label.
4. Attributable results dated within 60 days of the assessment date for both qualifying cohorts. Record the actual evaluation date when disclosed; otherwise an explicitly dated new result publication is permissible as `published`. Never infer a run date, use an old result republished without a new evaluation claim, or date an undated table from the retrieval timestamp.
5. Exact model identifiers, version/configuration, finite score, units, source URL, source kind, evidence date and date type, and verification date. Sources may be benchmark authors, independent evaluators or model providers, with that distinction retained. Provider self-report must be visibly attributed and independently checked against its primary source, rather than portrayed as an independent model evaluation.
6. A separate reviewer who opens the cited sources and approves identity, evidence dates, current model membership, compatibility and substantive claims. Mechanical checks validate the record and its consistency; they cannot prove a source supports a claim.

Maintain a dated model reference set by domain. Entries include exact model ID, organization, cohort, openness, source and selection rationale. Open-weight and open-source are different labels. A reference set older than 30 days must be refreshed before new active decisions. This 30-day check is an operational safeguard; the evaluation result window remains 60 days. Adding a model to the set does not automatically qualify its benchmarks.

## Dispositions

- **Active:** all gates pass. Only these canonical IDs enter the new authoring queue and default catalogue input.
- **Historical:** established, otherwise qualifying comparison evidence has expired, or supported saturation makes it unsuitable for the active comparison. Preserve its history and reason for exclusion.
- **Unverified:** missing identity, date, review, current coverage, comparable protocol or usefulness evidence; includes malformed records. Do not equate missing evidence with illegitimacy or proven staleness.
- **Alias:** a supported alternate identifier maps to a canonical benchmark; does not create a second active identity.

Unassessed candidates remain discovery leads. Report them separately from evaluated dispositions. An empty active set is a valid outcome; missing evidence must never trigger fallback to the old census queue.

Recompute eligibility against the actual assessment date each time the queue or catalogue is generated. A visit or review cannot rejuvenate old evidence. The earliest expiry of the qualifying pair limits its active lifetime; another compatible qualifying pair can keep it active. Daily eligibility recomputation and weekly source checks are the intended service cadence, not a scheduled job already installed by this change.

## Rollout and worker constraints

The legacy production runner stays paused behind `QUALITY_AUDIT_PAUSE.json`. `SONNET_STOP` remains authoritative. Completed workers and all existing drafts are preserved; no broad generation, checkpoint, push, deployment or publication follows from creating evidence records.

Start with six candidate groups to exercise current results, versions, duplicates, generic discovery entries and missing evidence. Research produces a source ledger; the coordinator independently verifies selected results and supplies reviewed structured records. The deterministic downselection command produces an explicit report and active IDs. Expand verification in bounded batches after the pilot, prioritizing benchmarks already used by current model cards and dated evaluation releases. Only then replace the legacy dispatcher input with the eligibility report; never merely remove its pause marker.

Rendering must eventually consume this eligibility output for its default active listing and show historical/unverified status explicitly elsewhere. This specification and initial evidence tool do not claim the deployed websites already implement that behavior.
