# Eligibility batch 003: HLE and AA-Omniscience

Research date: **2026-09-09**. Freshness window: **2026-07-11 through 2026-09-09** (calendar-date arithmetic). This is a proposal for independent review; no eligibility approval is recorded here. The dated result source for both rows is the static chart embedded in AA’s **2026-09-04** Intelligence Index v4.2 article: <https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2>. The inspected chart is <https://cdn.sanity.io/images/6vfeftx9/articles/971805b0a4b0877da6653842f240267721a56498-2256x4032.png?auto=format&w=1200>. The chart date is a publication date, not an execution date.

The comparison pair is **GPT-6 Astra (max)** (OpenAI, proprietary) and **GLM-5.3 (max)** (Z AI, open weights), as identified by AA model metadata: <https://artificialanalysis.ai/models/gpt-6-astra> and <https://artificialanalysis.ai/models/glm-5-3>. The labels were checked against the native chart, including the distinction between GLM-5.3 (max) and GLM-5.3-Flash.

## Proposed evidence ledger

| Canonical profile | Dated chart result pair | Metric / protocol and identity scope | Freshness / gaps | Proposal |
|---|---|---|---|---|
| **Humanity’s Last Exam (`hle`)** | GPT-6 Astra (max), **55% accuracy**; GLM-5.3 (max), **42% accuracy**. Both are exact chart labels; organizations differ (OpenAI / Z AI). | AA methodology lists HLE under Scientific Reasoning: **2,158 questions**, one repeat, open-answer response, equality-checker LLM, pass@1. Existing canonical page `benchmarks/hle.md` identifies the broader HLE benchmark and its accuracy metric; AA’s v4.2 chart is the evaluator-specific result. Sources: <https://artificialanalysis.ai/methodology/intelligence-benchmarking#hle-humanitys-last-exam>, <https://artificialanalysis.ai/evaluations/humanitys-last-exam> (linked from AA’s evaluation directory), <https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2>. | Snapshot published **2026-09-04**, inside the window. Actual execution dates, hidden prompt pins, and equality-checker version are not disclosed. Do not merge with `hle_tools`, HLE-Rolling, HLE-Verified, or older public HLE rows; those are different protocols/sets. | **Proposed fresh attributable pair.** Canonical identity remains `hle`; AA’s 2,158-question profile is a protocol/result record, not a new HLE benchmark identity. |
| **AA-Omniscience (`artificialanalysis_aa_omniscience_public`) — Accuracy metric** | GPT-6 Astra (max), **63% accuracy**; GLM-5.3 (max), **34% accuracy**. Both are exact chart labels; organizations differ (OpenAI / Z AI). | AA evaluation page describes one benchmark with **6,000 questions across six domains**. Methodology lists one repeat, open-answer responses, and two separate Index components: **Accuracy (10%)** and **1 − Hallucination Rate (5%)**. This row intentionally chooses **Accuracy** as the single metric; hallucination rate/non-hallucination is another metric of the same AA-Omniscience benchmark, not another profile. Sources: <https://artificialanalysis.ai/evaluations/omniscience>, <https://artificialanalysis.ai/methodology/intelligence-benchmarking#aa-omniscience>, <https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2>. | Snapshot published **2026-09-04**, inside the window. Actual execution dates, private question set details, answer/parser pins, and refusal handling beyond the published methodology are not disclosed. The AA page says the dataset is private; do not treat the public suffix in the repository page ID as a public dataset claim. | **Proposed fresh attributable pair.** Keep one canonical AA-Omniscience profile with Accuracy as the selected metric; retain Index and hallucination/non-hallucination as related measures within that profile. |

## Scope and counterevidence notes

* HLE’s existing page describes the canonical benchmark, while AA’s chart/methodology describes the evaluator’s current 2,158-question, one-repeat profile. This is a protocol subset/version difference to record, not grounds for inventing an HLE variant ID.
* AA-Omniscience’s evaluation page describes the full 6,000-question benchmark and six domains; the methodology’s Accuracy and 1 − Hallucination Rate are separate components of the same benchmark. No second AA-Omniscience identity is proposed for the second metric.
* The chart values are rounded display precision. No raw counts, confidence intervals, execution timestamps, or current API model versions are inferred.
* The v4.2 chart is used for dated evidence. Later live-table values are not backdated into this 2026-09-04 snapshot.

## Visited primary URLs (accessed 2026-09-09)

1. https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2
2. https://cdn.sanity.io/images/6vfeftx9/articles/971805b0a4b0877da6653842f240267721a56498-2256x4032.png?auto=format&w=1200
3. https://artificialanalysis.ai/methodology/intelligence-benchmarking
4. https://artificialanalysis.ai/evaluations/humanitys-last-exam
5. https://artificialanalysis.ai/evaluations/omniscience
6. https://artificialanalysis.ai/models/gpt-6-astra
7. https://artificialanalysis.ai/models/glm-5-3
8. https://github.com/centerforaisafety/hle
9. https://arxiv.org/abs/2501.14249
10. https://lastexam.ai
