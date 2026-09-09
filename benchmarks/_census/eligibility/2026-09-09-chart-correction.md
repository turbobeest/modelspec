# 2026-09-09 v4.2 chart correction

## Scope

This erratum records a correction to the SciCode evidence record after an independent review of the original AA v4.2 chart. It preserves the prior value and review history; it does not alter the other five batch-002 records.

Source chart: <https://cdn.sanity.io/images/6vfeftx9/articles/971805b0a4b0877da6653842f240267721a56498-2256x4032.png?auto=format&w=1200>

Source article: <https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2> (published 2026-09-04)

## Correction

| Record | Model | Prior recorded value | Correct chart value | Metric | Reason |
|---|---|---:|---:|---|---|
| `scicode.json` | GPT-6 Astra (max) | 56% | 56% | SciCode percent score | Confirmed unchanged. |
| `scicode.json` | GLM-5.3 (max) | 56% | **59%** | SciCode percent score | The original chart’s SciCode panel places GLM-5.3 (max) at 59%; the prior 56% was a label-reading error. |

## Review history

1. **2026-09-08 — initial coordinator/researcher review:** The chart was misread and recorded both GPT-6 Astra (max) and GLM-5.3 (max) as 56%.
2. **2026-09-09 — Grok reviewer finding:** Independent review correctly flagged the GLM-5.3 (max) SciCode value as wrong and identified the chart value as 59%.
3. **2026-09-09 — GPT-5.6 Luna / freshness_pilot verification:** Reopened the original full-resolution chart, checked all six batch-002 target pairs for label confusion, confirmed the other five pairs remain as recorded, and corrected only the GLM-5.3 result in `scicode.json` to 59%.

The correction preserves the v4.2 snapshot date and does not infer an execution date.
