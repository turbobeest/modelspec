# Eligibility batch 002: Artificial Analysis component evaluations

Research date: **2026-09-08**. Freshness window: **2026-07-10 through 2026-09-08**, calculated with calendar-date arithmetic. This is a source-led proposal batch, not an accepted eligibility decision. A publication date is not asserted to be an execution date; AA does not expose execution dates for the component rows below.

The dated result source is the static chart embedded in AA’s **2026-09-04** v4.2 article: <https://cdn.sanity.io/images/6vfeftx9/articles/971805b0a4b0877da6653842f240267721a56498-2256x4032.png?auto=format&w=1200>. It shows the same displayed configurations, **GPT-6 Astra (max)** (OpenAI, proprietary) and **GLM-5.3 (max)** (Z AI, open weights), across all six profiles. The article is the publication date for the snapshot; execution dates are not disclosed. The pair’s model identity/openness is also supported by AA model metadata: <https://artificialanalysis.ai/models/gpt-6-astra>, <https://artificialanalysis.ai/models/glm-5-3>.

## Proposed evidence ledger

| Profile | Exact current pair and score | Version / metric / protocol evidence | Freshness and omissions | Proposal |
|---|---|---|---|---|
| **AA-Briefcase** | Dated v4.2 chart: GPT-6 Astra (max), **53% normalized Elo**; GLM-5.3 (max), **51% normalized Elo**. The chart labels the metric `(Elo−500)/2000`; organizations differ: OpenAI / Z AI. | AA methodology describes **91 tasks across four scenarios, 1 repeat**, agentic task completion with file outputs; underlying headline is combined Elo from rubric pass rate, analytical quality Elo, and presentation Elo. Source: <https://artificialanalysis.ai/methodology/intelligence-benchmarking#aa-briefcase>. | Snapshot publication: **2026-09-04**. Execution dates and raw Elo values are undisclosed. The chart is the dated evidence; do not substitute later comparison-page Elo values or invert rounded normalized values into raw Elo. | **Proposed fresh attributable pair**, with v4.2 snapshot precision preserved. |
| **GDPval-AA v2** | Dated v4.2 chart: GPT-6 Astra (max), **54% normalized Elo**; GLM-5.3 (max), **59% normalized Elo**. The chart labels the metric `(Elo−500)/2000`; organizations differ: OpenAI / Z AI. | AA methodology identifies **GDPval-AA v2**, **220 tasks**, 1 repeat, pairwise Elo anchored to human experts at 1000, three-frontier-LLM judge panel, and 250-turn limit. Source: <https://artificialanalysis.ai/methodology/intelligence-benchmarking#gdpval-aa-v2>. | Snapshot publication: **2026-09-04**. Model release labels are not evaluation run dates; no execution timestamps are exposed. Do not combine with GDPval-AA v1 or later current-table values. | **Proposed fresh attributable pair** under v2, with normalized chart values retained as displayed. |
| **GDP.pdf (AA implementation)** | Dated v4.2 chart: GPT-6 Astra (max), **33% All-pass**; GLM-5.3 (max), **12% All-pass**. Organizations differ: OpenAI / Z AI. | AA implementation of Surge AI’s GDP.pdf: **100 tasks / 10 domains / 4,592 pages / 1,275 atomic criteria**, five independent attempts per task, headline **All-pass**; AA document preparation and GPT-5.6 Luna Medium judge differ from Surge. Sources: <https://artificialanalysis.ai/evaluations/gdp-pdf>, <https://artificialanalysis.ai/methodology/intelligence-benchmarking#gdp-pdf>. | Snapshot publication: **2026-09-04**. Execution dates undisclosed. Do not merge with Surge’s leaderboard or later AA current-table values. | **Proposed fresh attributable pair**, implementation identity `gdp_pdf_aa`. |
| **SciCode** | Dated v4.2 chart: GPT-6 Astra (max), **56%**; GLM-5.3 (max), **59%**. Organizations differ: OpenAI / Z AI. Correction recorded in [2026-09-09 chart erratum](2026-09-09-chart-correction.md). | AA methodology: **dataset v1.0.1**, 288 test subproblems, 3 repeats, pass@1/subproblem scoring, scientist-annotated background prompting, isolated executors with 300-second timeout. Source: <https://artificialanalysis.ai/methodology/intelligence-benchmarking#scicode>. | Snapshot publication: **2026-09-04**. No run dates exposed; values are chart precision. Do not substitute later current-table values. | **Proposed fresh attributable pair**, versioned to SciCode dataset v1.0.1. |
| **AA-LCR v1.1** | Dated v4.2 chart: GPT-6 Astra (max), **81%**; GLM-5.3 (max), **80%**. Organizations differ: OpenAI / Z AI. | AA methodology: **AA-LCR v1.1**, 100 questions, 3 repeats, open-answer equality-checker scoring; v1.1 adds a system prompt, corrects 16 answer keys, and uses GPT-5.6 Luna (medium) grading. Scores are not directly comparable with v1.0. Source: <https://artificialanalysis.ai/methodology/intelligence-benchmarking#aa-lcr-v1-1>. | Snapshot publication: **2026-09-04**. No execution dates exposed; do not merge with v1.0 or later current-table values. | **Proposed fresh attributable pair**, v1.1 identity preserved. |
| **CritPt** | Dated v4.2 chart: GPT-6 Astra (max), **32%**; GLM-5.3 (max), **19%**. Organizations differ: OpenAI / Z AI. | AA methodology: challenge-level CritPt, **70 test-set challenges**, 5 repeats, pass@1; two-step parsing then official grading server. Source: <https://artificialanalysis.ai/methodology/intelligence-benchmarking#critpt>. | Snapshot publication: **2026-09-04**. No execution dates exposed; do not interpret the percentages as single-run scores or substitute later current-table values. | **Proposed fresh attributable pair**, with v4.2 snapshot date and precision retained. |

## Source and identity notes

* AA’s **2026-09-04 v4.2** article says AA-Briefcase and GDP.pdf were added, AA-LCR was upgraded to v1.1, and SciCode was regraded after its timeout/sandbox changes. Its embedded static chart is the dated numeric evidence for all six rows. Source: <https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2>.
* AA’s **2026-09-07 v4.3** article is later context only. Its current component values supersede the v4.2 snapshot for present-day display, but they are not used here because this batch requires a dated source snapshot. Source: <https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-3>.
* The v4.2 article establishes snapshot publication date, not execution date. No row is assigned an invented `run_date`.
* Openness is sourced independently from AA’s model metadata: the comparison page labels GPT-6 Astra proprietary and GLM-5.3 open weights; the GLM model page identifies Z AI and open-weight status. This does not assert a particular license beyond what AA publishes.
* These are component benchmark records. The Intelligence Index aggregate is not used as a substitute for a component score.

## Not established by this batch

* No exact component result for a second open organization was required because the pair already spans OpenAI and Z AI; however, both configurations are AA display configurations and are not equal-compute claims.
* No execution timestamp, API model version, hidden prompt revision, or per-task confidence interval is exposed in the inspected sources.
* The AA-Briefcase public Lite scenario is explicitly demonstrative and does not contribute to official scores; only the private v4.2 snapshot values above are proposed.

## Visited primary URLs (accessed 2026-09-08)

1. https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2
2. https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-3
3. https://artificialanalysis.ai/methodology/intelligence-benchmarking
4. https://artificialanalysis.ai/evaluations/aa-briefcase
5. https://artificialanalysis.ai/evaluations/gdpval-aa
6. https://artificialanalysis.ai/evaluations/gdp-pdf
7. https://artificialanalysis.ai/evaluations/scicode
8. https://cdn.sanity.io/images/6vfeftx9/articles/971805b0a4b0877da6653842f240267721a56498-2256x4032.png?auto=format&w=1200
9. https://artificialanalysis.ai/models/gpt-6-astra
10. https://artificialanalysis.ai/models/glm-5-3
