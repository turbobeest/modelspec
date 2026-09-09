# BenchGraph evidence-first downselection implementation

Scope accepted September 8, 2026: [active catalogue specification](../specs/2026-09-08-benchgraph-active-catalogue.md).

## Initial implementation

1. Preserve the legacy production pause and Sonnet stop. Inspect live processes, not stale active-job counts. At adoption, all twelve listed Grok workers were defunct; the old supervisor remained suspended and the continuation controller reported `paused-for-quality-audit`.
2. Add isolated strict evidence and current-model-reference models in `schema/benchmark_eligibility.py`, without changing the page schema consumed by legacy writers.
3. Add `scripts/benchmarks/downselect.py` to compute deterministic dispositions and an active canonical-ID list at an explicit assessment date. Invalid inputs fail closed. Tests cover freshness boundaries, future dates, stale reference sets, review requirements, aliases, duplicate IDs, different organizations and compatible protocols.
4. Research six pilot groups: AutomationBench, Terminal-Bench, LiveBench, OpenBookQA/obqa, OpenML discovery entries, SWE-Together. Save source evidence under `benchmarks/_census/eligibility/`. Assess exact versions; a family's current release cannot refresh old variants.
5. Independently review primary evidence, construct initial reference and evidence records, run the gate, and publish a local report with explicit unresolved reasons. Do not present a purposive six-group sample as an estimate of the full census acceptance rate.

## Follow-through after the pilot

- Expand source verification in bounded batches, starting from recent result releases and benchmarks referenced by current model cards. Preserve the original discovery queue as provenance; do not attempt thousands of full-page rewrites as a freshness check.
- Reconcile aliases and hold drafts lacking eligible identities. Reuse sound researched content, but verify every factual claim before publication. Keep rejection and unverified reasons auditable.
- Replace generation/checkpoint admission with the reviewed eligibility output before resuming any production runner. Its output must remain fail-closed when evidence expires or a current-model reference set is overdue.
- Wire the same eligibility data into default site/API listings in the dedicated serving implementation. Label historical and unverified pages. Complete required rendering checks before any separate merge/deployment decision.

No new universal benchmark-count target or completion ETA is justified until the eligible set is measured.

## Initial implementation result

The evidence schema, deterministic report command and batch selection admission gate are implemented. `next_batch.py` now recomputes eligibility at the current date and writes `next_batch_eligible.json`; it never falls back to the original discovery queue. The six-group pilot produced nine records: one active profile, one independently reviewed alias and seven unverified records. See [the pilot README](../../../benchmarks/_census/eligibility/README.md) and machine-readable report for precise scope and limitations. Focused validation covers 27 cases; Ruff passes on the changed implementation and tests.

Legacy supervisor/checkpoint migration and serving integration remain outstanding; their pause is intentional while the new verification batches establish evidence. The eligible profile already has a draft, so eligibility does not imply a new page or a completed article review.

Batch 002 added six independently reviewed profiles using a fixed chart in AA's dated September 4 release. The current report has seven active profiles, one alias and seven unverified identifiers. A bounded replacement runner now owns those seven profiles, with seven Grok slots, explicit eligibility rechecks, separate source-review sessions, preserved pre-edit snapshots, approval hashes, a shared exclusive lock and soft stop handling. Focused tests now total 35 passing cases. Automatic checkpoints and serving integration remain outstanding; the legacy controller stays paused and Sonnet stays disabled. See the eligibility README for live state paths and adoption instructions.
