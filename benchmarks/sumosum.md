---
id: sumosum
name: "SUMOSum (HELM climate-claims summarization)"
aliases:
  - "SUMO climate summarization"
page_kind: benchmark
category: domain
subcategory: "single-document abstractive summarization of climate fact-check documents into a claim-style title"
status: active
summary: "HELM's repurposing of the climate subset of the SUMO web-claims dataset as document-to-title summarization, distinct from the original paper's claim-verification task."
measures: >
  As implemented in HELM, this task gives a model a document related to a climate-change claim
  (`Doc_text`) and asks it to generate a short title-style summary (`Title`), scored as single-document
  abstractive summarization. This is a repurposing of the underlying data: the source SUMO dataset
  (Mishra et al., 2020) was built for claim verification with extractive evidence -- given a claim and
  retrieved web evidence documents, decide whether the claim is true or false and extract supporting
  sentences -- not for title generation. HELM's scenario keeps only the climate-focused rows and reduces
  the task to document-to-title summarization, discarding the original claim-correctness labels. All
  text is English.
task_format: "Free-text generation: given a climate-claim-related document, generate a short title-style summary."
metric:
  name: "ROUGE-2 (consistent with HELM's other summarization scenarios); exact primary metric for this scenario not independently confirmed"
  direction: higher_is_better
  unit: "score"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No numeric baseline was found in the sources opened for this page. This page did not locate this
    scenario's own `get_metadata()` main-metric declaration in the source consulted, so the ROUGE-2
    listed here is inferred from HELM's shared summarization tooling (`get_summarization_metric_specs`)
    rather than independently confirmed for this specific scenario file, and should be treated as
    unconfirmed.
dataset:
  size: null
  size_note: >
    Not established with confidence. The underlying SUMO paper's climate subset contains 104 claims
    drawn from climatefeedback.org, matched against 1,050 evidence documents (97 distinct "domains" of
    source sites). HELM's scenario, however, loads a single `climate_claims_raw.xlsx` file and treats
    each row with a non-null `Doc_text` and `Title` as one instance, which may not equal either the
    104-claim or 1,050-document count from the paper; this page did not independently open and count
    the rows of that Excel file, so `dataset.size` is left null rather than assuming a figure.
  url: "https://github.com/rahulOmishra/SUMO"
  license: "Not established: no explicit licence statement was found in the sources opened for this page for either the SUMO repository or the climate_claims_raw.xlsx file HELM loads."
  languages:
    - en
  modalities:
    - text
  splits: "HELM splits the loaded rows 20% train / 80% test by random sampling (random_state=0); no separate validation split."
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM scenario); underlying data from University of Zurich / TU Kaiserslautern authors (SUMO paper)"
  authors:
    - "Rahul Mishra"
    - "Dhruv Gupta"
    - "Markus Leippold"
  url: "https://github.com/rahulOmishra/SUMO"
paper:
  title: "Generating Fact Checking Summaries for Web Claims"
  arxiv: "2010.08570"
  url: "https://arxiv.org/abs/2010.08570"
  year: 2020
leaderboard_url: "https://crfm.stanford.edu/helm/classic/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/sumosum_scenario.py"
released: "2020-10"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No source opened for this page gave a top score for this scenario, current or historical, so
    saturation status is left unknown.
contamination:
  risk: unknown
  note: >
    The underlying climate_claims_raw.xlsx data has been hosted in the public rahulOmishra/SUMO
    repository since around the paper's 2020 publication, and HELM's own scenario code and pickled
    mirror have been public since HELM's 2022 release, so both are plausible pretraining-data members
    for current large models. No contamination study specific to this scenario or the underlying SUMO
    climate data was found, so risk is left `unknown` rather than asserted from public-hosting alone.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "sumosum"
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - summarization
  - climate
  - generation
  - domain
  - fact-checking
sources:
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/sumosum_scenario.py"
    title: "HELM sumosum_scenario.py (SUMOSumScenario)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/sumosum_scenario.py"
    title: "HELM sumosum_scenario.py (raw)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2010.08570"
    title: "Generating Fact Checking Summaries for Web Claims (Mishra, Gupta, Leippold)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2010.08570"
    title: "Generating Fact Checking Summaries for Web Claims, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2020.wnut-1.12/"
    title: "Generating Fact Checking Summaries for Web Claims (ACL Anthology, W-NUT 2020)"
    accessed: "2026-09-08"
  - url: "https://github.com/rahulOmishra/SUMO"
    title: "rahulOmishra/SUMO repository (source of climate_claims_raw.xlsx)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-006 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-006"
---

## What it measures

As implemented in HELM, this scenario gives a model a document related to a climate-change claim and asks it to generate a short title-style summary of that document, scored as single-document abstractive summarization. This is a significant repurposing of the source data: the original SUMO dataset (Mishra, Gupta and Leippold, 2020) was built for claim verification with extractive evidence -- given a claim and a set of web documents retrieved as potential evidence, decide whether the claim is true or false, and extract the sentences that justify that decision. HELM's scenario discards the claim-correctness labels entirely and reduces the task to document-to-title generation on the dataset's climate subset only, loading a single `climate_claims_raw.xlsx` file with `Claim_id`, `Claim`, `Title`, `Doc_text`, and `Label` columns and using only `Doc_text` (as input) and `Title` (as the target summary). All text is English.

Anyone citing this id should be aware the census-style name "SUMOSum" describes HELM's derived summarization framing, not the original SUMO paper's own task, which this page's Lineage section describes further.

## How it is scored

HELM scores this scenario as free-text generation against the `Title` field as reference. This page infers ROUGE-2 as the likely primary metric by analogy with HELM's other summarization scenarios, which share common summarization metric-computation code, but did not independently confirm this scenario's own `main_metric` declaration in the source file consulted, so this should be treated as an educated inference rather than a confirmed fact, and is flagged as such in `metric.name`.

## Dataset and licence

Confidence here is limited. The SUMO paper's own climate subset (sourced from climatefeedback.org, with claims retrieved via a search-engine API) comprises 104 claims matched against 1,050 evidence documents from 97 distinct source domains. HELM's scenario, however, operates at the row level of a single Excel file (`climate_claims_raw.xlsx`) rather than reproducing the paper's claim/evidence structure, dropping rows with missing `Title` or `Doc_text`, so the number of usable HELM instances is not necessarily either the 104-claim or 1,050-document figure, and this page did not independently open and count that file's rows -- `dataset.size` is left null rather than asserting one of those numbers by assumption. HELM splits whatever rows remain 20% train / 80% test using a fixed random seed (`random_state=0`), with no separate validation split. No explicit licence statement was found for either the `rahulOmishra/SUMO` repository or the specific Excel file HELM downloads from it.

## Who publishes it

The underlying data and original task come from Rahul Mishra, Dhruv Gupta and Markus Leippold, published as "Generating Fact Checking Summaries for Web Claims" at the Sixth Workshop on Noisy User-generated Text (W-NUT), EMNLP 2020. The HELM scenario that repurposes this data for summarization is maintained by Stanford CRFM as part of the HELM benchmark suite (Liang et al., 2022), not by the original SUMO paper's authors.

## Lineage

This id has no predecessor or successor tracked in this repository. It is a derived, single-domain slice of the broader SUMO dataset, which also includes larger PolitiFact (3,568 claims) and Snopes (4,341 claims) subsets not used by this HELM scenario; those subsets, and the original claim-verification task itself, do not have separate pages in this repository. Readers should not confuse this HELM summarization framing with the original SUMO paper's claim-verification benchmark, which is a different task over the same underlying documents.

## Saturation and contamination

No current or historical top score for this scenario was found in the sources opened for this page, so saturation status is left `unknown`. Contamination risk is also left `unknown`: the underlying Excel file has been hosted in the public SUMO GitHub repository since around the paper's 2020 publication, and HELM's own scenario code and pickled data mirror have been public since 2022, making both plausible pretraining-data members for current models, but no dedicated contamination study for this specific scenario was found.

## How to run it

HELM implements this as the `sumosum` scenario (class `SUMOSumScenario`, tags `["summarization", "climate"]`), which downloads `climate_claims_raw.xlsx` directly from the `rahulOmishra/SUMO` GitHub repository, applies the described row filtering and an 80/20 test/train split, and evaluates with HELM's shared summarization adapter and metric machinery. No configuration for this scenario was found in lm-evaluation-harness, OpenCompass, or BIG-bench in the sources opened for this page. Because this is a HELM-specific repurposing of data built for a different original task, reported numbers are unlikely to be comparable to anything published using the original SUMO paper's own claim-verification evaluation protocol.

## Reading the numbers

A score on this scenario reflects how well a model can generate a short climate-fact-check-style title from a document, on a small, single-domain, English-only slice of data -- not verified claim-checking ability, despite the underlying dataset's origin as a fact-checking resource. Because the exact instance count and primary metric for this HELM scenario were not independently confirmed in the sources opened for this page, treat any reported number with caution until those details are verified against the running HELM code or its published results tables, and do not assume this scenario measures factual correctness rather than surface summary quality.
