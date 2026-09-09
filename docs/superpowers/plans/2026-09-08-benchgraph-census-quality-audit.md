# BenchGraph census scope and quality audit — September 8, 2026

The operator asked whether the batch programme was over-counting benchmarks and relying on legitimate sources. The audit confirms that the dispatch target was a discovery queue, not a verified count of distinct benchmarks. Increasing throughput before enforcing identity and canonicalization was a coordination error. The earlier 12–18 active-hour estimate describes processing that raw queue and is not a reliable estimate for a vetted catalogue or the full ModelSpec delivery.

## Scope evidence

The immutable original queue in `benchmarks/_census/cache/grok-window-20260908/queue.json` has 414 batches and 2,887 candidate IDs: 589 priority-2 registry candidates and 2,298 priority-3 discovery-shortlist candidates. Seven pilot IDs brought programme accounting to 2,894. Of the 2,887 queue candidates, 2,756 occur in one census source, 124 in two, and seven in three or more. These are discovery-source counts, not citation counts or a validity verdict. A single authoritative source can establish a benchmark.

`benchmarks/_census/REPORT.md` reports 8,950 harvested leads and 7,226 normalized slugs overall, including 172 model-card keys, 829 registry candidates, and 6,225 discovery candidates. None of these totals certifies distinct benchmark identity. The collectors include harness directories/scenario names, Hugging Face keyword results and spaces, arXiv title extraction, community link lists, and search results. Name normalization and keyword filtering do not establish a task, metric, evaluation protocol, release, or canonical identity.

## Concrete findings

- `obqa.md` and `openbookqa.md` describe the same OpenBookQA evaluation. Harness spellings should be aliases. The author's repository is https://github.com/allenai/OpenBookQA .
- `translation.md` describes a task family but is tagged `page_kind: benchmark`. `mmmlu_lite.md` explicitly describes a slice. Such documentation may be useful, but it should not inflate a count of independent benchmarks.
- `openml_benchmark.md` and `openml_benchmarks.md` cite generic OpenML search/home pages without a specific task/dataset ID or protocol. Their distinct benchmark identity is unproven.
- `opt_engine.md` cites a real benchmark paper, https://arxiv.org/abs/2601.19924 , but omits its ten-problem optimization scope and supplies unsupported generic accuracy/harness prose.
- The independent six-page audit additionally found real source support for VIBE, SWE-Explore and SWE-Together, with substantially different draft quality. This was a purposive sample and does not establish a corpus-wide defect percentage. See `benchmarks/_census/cache/grok-continuation-20260908/legitimacy-audit-sample.md` for claim-level findings and primary URLs.
- A literal summary-pattern scan found 52 drafts containing “is a benchmark task documented by its cited evaluation harness”; all 52 were untracked at the audit snapshot. Their IDs are preserved in `quality-hold-generic-drafts.json` in the continuation cache. This is an audit hold, not deletion or an assertion that all underlying benchmarks are invalid.

## Operational response

Sonnet remains disabled by the operator's `SONNET_STOP` instruction. Primary supervisor PID is recorded in `QUALITY_AUDIT_PAUSE.json` and was suspended with SIGSTOP, preserving existing Grok worker processes. This pauses new dispatch and supervisor checkpoints. The continuation controller and Luna claim helper now honor the quality-pause marker so automatic continuation cannot restart expansion. Existing workers can finish their current work into their assigned files/cache. No draft or completed source material was deleted.

## Required correction before resuming broad generation

1. Establish eligibility before authoring: a distinct task/evaluation, defined metric or scoring protocol, identifiable release/data/task construction, and a primary source that directly supports that identity. Paper publication is not mandatory when an authoritative benchmark release or harness implementation supplies the evidence.
2. Resolve canonical identities and represent aliases, subsets, translations and harness variants explicitly; report their counts separately.
3. Reject tools, model names, generic platform/index labels, result uploads and unidentifiable leads from the benchmark-page target. Leave useful discovery leads in a backlog.
4. Repair or exclude unsupported boilerplate drafts. Validate evidence-to-claim correspondence and concrete benchmark-specific content, in addition to schema validity. Re-audit duplicate cases that previously received reviewer approval.
5. Prioritize the benchmarks actually used by ModelSpec model cards and confirmed benchmark suites for the first public catalogue. Determine the catalogue size from that audit rather than choosing a large page-count target. Re-estimate remaining work after triage; full site rendering remains separate work.
