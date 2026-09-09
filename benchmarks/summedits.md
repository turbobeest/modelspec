---
id: summedits
name: "SummEdits"
aliases:
  - "SummEdits Benchmark"
page_kind: benchmark
category: reasoning
subcategory: "binary factual-consistency detection between a document and an edited summary, across 10 domains"
status: active
summary: "6,348-item binary benchmark asking whether a small edit to a factually consistent summary preserved consistency with its source document, across 10 text domains."
measures: >
  SummEdits tests factual-consistency detection: given a source document and a summary of it, the model
  must judge whether the summary remains factually consistent with the document. Every item starts from
  a summary an annotator has already confirmed is fluent and consistent, then a small, "atomic" edit is
  applied (originally by ChatGPT) that either preserves consistency or introduces a factual error; a
  human annotator labels the edited version as consistent or inconsistent, discarding ambiguous
  ("borderline") cases. The benchmark spans 10 domains -- news, podcasts, legal bill summaries
  (BillSum), dialogue (SamSum), Shakespeare, scientific-paper abstracts (SciTLDR), meeting summaries
  (QMSum), financial earnings calls (ECTSum), sales emails, and sales calls -- so it is English text
  throughout but deliberately not limited to news-style summarization.
task_format: "Binary classification: given a document and an edited summary, judge the summary factually consistent or inconsistent with the document."
metric:
  name: "balanced accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50.0
  human_baseline: 90.9
  baseline_note: >
    Balanced accuracy makes a coin flip 50% regardless of class imbalance. The paper reports human
    performance at 90.9% balanced accuracy, GPT-4 at 82.4%, ChatGPT at 71.3%, and a specialised
    inconsistency detector (QAFactEval) at 65.7%, on the released benchmark; the class split overall is
    roughly 37% consistent to 63% inconsistent.
dataset:
  size: 6348
  size_note: >
    6,348 examples total across the 10 domains, with per-domain counts ranging from 431 to 853 in the
    paper's own reporting. The benchmark is a single evaluation set built for a few hundred dollars per
    domain (about $3,000 total, the paper states roughly 20x cheaper per item than prior consistency
    benchmarks it compares against), not split into train/validation/test, since it is meant to be
    scored directly rather than trained on.
  url: "https://github.com/salesforce/factualNLG"
  license: "Apache License 2.0 (salesforce/factualNLG repository)"
  languages:
    - en
  modalities:
    - text
  splits: "single 6,348-item evaluation set across 10 domains; no train/validation/test split"
  public_test_set: true
publisher:
  org: "Salesforce Research"
  authors:
    - "Philippe Laban"
    - "Wojciech Kryscinski"
    - "Divyansh Agarwal"
    - "Alexander R. Fabbri"
    - "Caiming Xiong"
    - "Shafiq Joty"
    - "Chien-Sheng Wu"
  url: "https://github.com/salesforce/factualNLG"
paper:
  title: "SummEdits: Measuring LLM Ability at Factual Reasoning Through The Lens of Summarization"
  arxiv: ""
  url: "https://aclanthology.org/2023.emnlp-main.600/"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/salesforce/factualNLG"
released: "2023-12"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 82.4
  as_of: "2023-12"
  note: >
    At release, GPT-4 (82.4%) still trailed the paper's 90.9% human balanced-accuracy figure by about
    8.5 points, and most other tested models scored close to chance (50%), so the benchmark was
    described as unsolved rather than saturated at that time. Marked `watch` rather than `open` because
    no source opened for this page gives a post-2023 top score, so it is unclear whether current
    frontier models have since closed the gap to the human figure.
contamination:
  risk: medium
  note: >
    The full 6,348-item set with labels has been publicly hosted on GitHub since the paper's release in
    late 2023, so it is a plausible pretraining-data member for any model trained on public code-hosting
    data since then. Risk is set to medium rather than high because the benchmark is comparatively
    recent (versus benchmarks public since the 2010s) and the paper's edit-based construction method
    means even a memorised source document/summary pair does not obviously reveal which specific edited
    variant, or its consistency label, appears in the released file without also having seen that file.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "summedits"
  bigbench: ""
  other: ""
tags:
  - factual-consistency
  - summarization
  - classification
  - hallucination
  - nli
sources:
  - url: "https://aclanthology.org/2023.emnlp-main.600/"
    title: "SummEdits: Measuring LLM Ability at Factual Reasoning Through The Lens of Summarization (ACL Anthology)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2305.14540"
    title: "SummEdits paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/salesforce/factualNLG"
    title: "salesforce/factualNLG repository (SummEdits data and code, Apache-2.0)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/summedits"
    title: "OpenCompass summedits dataset configs directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/summedits/summedits_ppl_1fbeb6.py"
    title: "OpenCompass summedits_ppl_1fbeb6 config (raw)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/summedits.py"
    title: "OpenCompass SummeditsDataset_V2 loader (raw)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Claude Sonnet 5, sonnet-batch-006 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Claude Sonnet 5 independent review, sonnet-batch-006"
---

## What it measures

SummEdits tests whether a model can tell if a summary remains factually consistent with its source document after a small edit. Every item starts from a document/summary pair that a human annotator already confirmed is fluent and consistent; a language model (ChatGPT, in the original construction) then applies a minor "atomic" edit to the summary, and a human annotator labels the result as consistent or inconsistent with the document, discarding ambiguous ("borderline") edits before release. The benchmark deliberately spans 10 domains beyond ordinary news summarization -- podcasts, legal bill summaries, dialogue, Shakespeare plays, scientific abstracts, meeting transcripts, financial earnings calls, and sales emails and calls -- so a model has to generalize its consistency judgment across very different document styles, not just news.

The task is entirely English text and framed as binary classification rather than open-ended generation: the model is not asked to summarize anything itself, only to judge a given summary against its document.

## How it is scored

Each item is scored as a binary consistent/inconsistent judgment against the human-assigned label, aggregated as balanced accuracy so that the roughly 37%-consistent/63%-inconsistent class split does not let a model win by always predicting the majority class. The paper reports human performance at 90.9% balanced accuracy, GPT-4 at 82.4%, ChatGPT at 71.3%, and the specialised prior detector QAFactEval at 65.7%, with inter-annotator agreement (Cohen's kappa) around 0.9 on the underlying labeling task, which the authors cite as evidence the labels themselves are reliable.

OpenCompass's `summedits` configuration loads the released data as a local JSONL file and recasts the binary label as a two-way multiple-choice question ("A"/"B") -- "Is the summary factually consistent with the document?" -- scored by perplexity-based (`_ppl`) or generation-based (`_gen`) variants with `AccEvaluator`, which is a specific reading of the task rather than the paper's own model-facing prompt format.

## Dataset and licence

The released benchmark totals 6,348 examples across the 10 domains, with the paper reporting per-domain counts ranging from 431 to 853 items. It is a single evaluation set, not split into train/validation/test, because SummEdits is meant to be scored directly rather than fine-tuned against; the authors state it cost roughly $3,000 total to build (about $300 per domain), which they present as about 20 times cheaper per item than the prior consistency benchmarks (such as AggreFact) it compares against, partly because the edit-based protocol needs less full-document re-annotation. The data and code are hosted at `salesforce/factualNLG` under an Apache License 2.0.

## Who publishes it

SummEdits is by Philippe Laban, Wojciech Kryscinski, Divyansh Agarwal, Alexander R. Fabbri, Caiming Xiong, Shafiq Joty, and Chien-Sheng Wu at Salesforce Research, published as "SummEdits: Measuring LLM Ability at Factual Reasoning Through The Lens of Summarization" at EMNLP 2023 (pages 9662-9676). Salesforce Research maintains the reference data and code at `salesforce/factualNLG`.

## Lineage

SummEdits is presented by its own authors as a successor to earlier factual-consistency benchmarks including FactCC and the same group's own SummaC, built specifically to address annotation-quality problems the paper documents in a prior benchmark, AggreFact (the paper reports finding roughly 6% mislabeled samples there). None of FactCC, SummaC, or AggreFact has its own page in this repository at the time of writing, and no successor to SummEdits itself was found in the sources opened for this page.

## Saturation and contamination

At release, GPT-4's 82.4% balanced accuracy still trailed the paper's 90.9% human figure by about 8.5 points, and most other tested models, including Llama2-7b at 50.4%, sat close to chance -- so the benchmark was explicitly unsolved, not saturated, as of its December 2023 publication. This page marks it `watch` rather than `open` because no source consulted gives a more recent top score, so whether current frontier models have since closed that gap is not established here. Contamination risk is set to medium: the full labelled dataset has been public on GitHub since the paper's release, making memorisation possible for models trained on recent public data, but the benchmark is young relative to older, decade-old test sets, and its edit-based construction means a model would need to have specifically seen the released file (not just the underlying source documents) to have memorised the actual labels.

## How to run it

OpenCompass configures the task as `summedits`, loading the released benchmark as a local JSONL file with `doc` and `summary` fields plus a binary `label`, recast as a two-choice ("A"/"B") consistency question scored via `AccEvaluator`, with both perplexity-based and generation-based prompt template variants available. No configuration was found in this pass for lm-evaluation-harness, HELM, or BIG-bench. The original paper's own evaluation code and Jupyter notebook for reproducing the reported numbers, including the exact prompts used for GPT-4 and ChatGPT, are in the `salesforce/factualNLG` repository; because OpenCompass's prompt format differs from the paper's own, and because balanced accuracy on a skewed label set is sensitive to how ties or refusals are handled, scores from different harnesses are not guaranteed to be directly comparable.

## Reading the numbers

A high SummEdits score indicates a model can catch small, deliberately introduced factual edits across a wide range of document styles, which is a reasonable proxy for whether that model's own summaries (or its judgments of others' summaries) are likely to be factually careful. Because most items differ from their consistent counterpart by only one small edit, the task specifically tests fine-grained factual sensitivity rather than gross hallucination detection, and a model that is only good at catching obvious contradictions may still score poorly. As of the paper's own numbers, no evaluated model reached human-level balanced accuracy, so treat scores as still meaningfully separating models rather than assume the ceiling has been reached, but confirm this against a source with a more recent top score before relying on that assumption for current frontier models.
