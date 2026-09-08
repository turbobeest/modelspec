---
id: meqsum
name: "MeQSum"
aliases:
  - "Medical Question Summarization"
  - "Consumer Health Question Summarization"
page_kind: benchmark
category: generation
subcategory: "abstractive summarisation of long consumer health questions into a single focused question"
status: active
summary: "1,000 real consumer health questions paired with an expert-condensed one-sentence summary, from the ACL 2019 paper that introduced medical question summarisation as a task."
measures: >
  MeQSum tests whether a model can compress a long, often rambling real-world consumer health
  question -- the kind a patient submits to a health Q&A service, with extra context, background
  details and multiple sub-questions folded in -- into a single, focused question that preserves
  the core information need. The paper's own motivation is practical: overly long questions
  increase false positives in downstream answer retrieval, so summarising the question first, before
  trying to answer it, is framed as a way to make question-answering systems more accurate. Inputs
  and outputs are both English text; there is no multiple-choice or classification step, only
  free-text generation.
task_format: >
  Single-document abstractive summarisation: the model reads one consumer health question (CHQ) and
  generates a single condensed summary question, scored against one expert-written reference summary
  per item.
metric:
  name: "ROUGE-1/2/L, BLEU, BERTScore and BLEURT (harness-dependent)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  baseline_note: >
    There is no random-guess baseline for open-ended summarisation. The original paper's own best
    model, a pointer-generator network, reached a ROUGE-1 score of 44.16%, which the authors present
    as the reference point competing approaches should be measured against, not a ceiling.
dataset:
  size: 1000
  size_note: >
    1,000 consumer health questions, each paired with one expert-written single-sentence summary;
    confirmed via the Hugging Face datasets-server for the `bigbio/meqsum` mirror, which exposes the
    corpus as two 1,000-row configurations (`meqsum_source`, the original question/summary pairs, and
    `meqsum_bigbio_t2t`, a text-to-text-formatted version) rather than as separate train/dev/test
    splits.
  url: "https://github.com/abachaa/MeQSum"
  license: >
    Stated two ways: the original GitHub repository's README states CC BY 4.0 explicitly; the
    `bigbio/meqsum` mirror on Hugging Face lists its licence as "unknown."
  languages:
    - en
  modalities:
    - text
  splits: "single 1,000-question corpus, exposed as one split; lm-evaluation-harness maps its training, validation and test splits all onto this same set rather than using an independent held-out portion"
  public_test_set: true
publisher:
  org: "U.S. National Library of Medicine (NIH)"
  authors:
    - "Asma Ben Abacha"
    - "Dina Demner-Fushman"
  url: "https://github.com/abachaa/MeQSum"
paper:
  title: "On the Summarization of Consumer Health Questions"
  arxiv: ""
  url: "https://aclanthology.org/P19-1215/"
  year: 2019
leaderboard_url: ""
repo_url: "https://github.com/abachaa/MeQSum"
released: "2019-07"
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
    No continuously maintained public leaderboard was found for MeQSum. The original paper reports
    ROUGE-1 44.16% for its own best (2019-era) pointer-generator model against pure sequence-to-
    sequence attentional baselines; no current LLM-era score was confirmed from the sources reviewed
    for this page, and because later systems are typically scored on a different combination of
    metrics (BLEU, BERTScore, BLEURT alongside ROUGE variants), a 2019 ROUGE number is not directly
    comparable to a modern multi-metric report without knowing exactly which metrics were used.
contamination:
  risk: high
  note: >
    The 1,000 question-summary pairs have been publicly downloadable, with reference summaries
    included, from GitHub since the 2019 release and from Hugging Face since 2022, roughly seven
    years of exposure by this research date. No canary string or access gate was found. Because
    lm-evaluation-harness treats the entire corpus as one set reused for training, validation and
    test, there is no held-out portion to fall back on even in principle.
harness:
  lm_eval: "meqsum"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - medical
  - summarization
  - generation
  - consumer-health
  - question-summarization
sources:
  - url: "https://aclanthology.org/P19-1215/"
    title: "On the Summarization of Consumer Health Questions"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/P19-1215.pdf"
    title: "On the Summarization of Consumer Health Questions (PDF)"
    accessed: "2026-09-08"
  - url: "https://github.com/abachaa/MeQSum"
    title: "abachaa/MeQSum GitHub repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/bigbio/meqsum"
    title: "bigbio/meqsum dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/bigbio/meqsum"
    title: "bigbio/meqsum dataset metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/meqsum/meqsum.yaml"
    title: "meqsum task config, EleutherAI lm-evaluation-harness"
    accessed: "2026-09-08"
  - url: "https://sites.google.com/site/asmabenabacha/"
    title: "Asma Ben Abacha, personal/academic site (career history)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MeQSum tests whether a model can compress a long, often rambling real-world consumer health question into a single, focused question that preserves the core information need. The source questions come from real messages submitted to a consumer health question-answering service: they typically bundle background context, personal details and more than one sub-question into a single, verbose message. The task is to produce a short, well-formed summary question that a retrieval or answering system could act on directly. The paper's own motivation is practical rather than purely academic: it argues that overly long, unfocused questions increase false positives when a downstream system tries to retrieve an answer, so summarising the question first is a way to make consumer health question-answering more accurate. Both the input and the generated summary are English text.

## How it is scored

Because MeQSum is open-ended generation rather than classification, there is no random-guess baseline. The original 2019 paper scores generated summaries against one expert-written reference summary per question using ROUGE, and reports its own best model, a pointer-generator network, at a ROUGE-1 score of 44.16%, ahead of plain sequence-to-sequence attentional baselines. The current lm-evaluation-harness implementation scores a wider set of metrics against the same reference summaries: BLEU, ROUGE-1/2/L, BERTScore and BLEURT, computed per example and averaged. Because these metrics disagree on nuance -- n-gram overlap metrics like ROUGE and BLEU reward surface-level match, while BERTScore and BLEURT better tolerate paraphrase -- a MeQSum report is only fully comparable to another when both used the same metric.

## Dataset and licence

MeQSum totals 1,000 consumer health questions, each paired with one expert-written single-sentence summary. It is released as a single corpus rather than split into train, validation and test sets; the `bigbio/meqsum` mirror on Hugging Face confirms this directly, exposing the same 1,000 rows under two configurations (raw source pairs, and a text-to-text-formatted version) with no separate splits. The licence is stated two different ways across the dataset's own hosting: the original GitHub repository's README states CC BY 4.0 explicitly, while the Hugging Face mirror's card lists the licence as "unknown." Because there is no held-out split, every question and its reference summary have been public since release.

## Who publishes it

MeQSum comes from Asma Ben Abacha and Dina Demner-Fushman, both affiliated with the U.S. National Library of Medicine (part of the NIH) at the time of publication, presented at ACL 2019 in Florence, Italy. The authors maintain the reference data at `github.com/abachaa/MeQSum`; no separately maintained leaderboard was found.

## Lineage

This repository does not track a formal predecessor or successor for MeQSum. It sits alongside a broader family of consumer-health and clinical text-summarisation datasets from the same NLM research group and the wider medical-NLP community, none of which are covered by this page or clearly established from the sources reviewed here as direct descendants.

## Saturation and contamination

No continuously maintained public leaderboard was found for MeQSum. The paper's own reference point -- ROUGE-1 44.16% from a 2019-era pointer-generator network -- predates the current wave of instruction-tuned LLMs, and no current score was confirmed from the sources reviewed for this page, so saturation status is recorded as unknown rather than asserted either way. Contamination risk is high: the full 1,000-item corpus, reference summaries included, has been publicly downloadable without gating since 2019 on GitHub and since 2022 on Hugging Face, and because the entire corpus doubles as the harness's training, validation and test data, there is no held-out portion that could have avoided that exposure even in principle.

## How to run it

lm-evaluation-harness implements MeQSum as the `meqsum` task, reading the `bigbio/meqsum` mirror, prompting the model to summarise the question, and computing BLEU, ROUGE-1/2/L, BERTScore and BLEURT against the reference summary with a `generate_until` protocol. No HELM, OpenCompass, inspect_evals or BIG-bench implementation was confirmed for MeQSum in the sources reviewed for this page. Because the harness reuses the same 1,000 items for every split, running the task under a few-shot setting risks prompting with examples the model is also being scored on, a protocol detail worth checking before trusting a reported few-shot number.

## Reading the numbers

A high MeQSum score suggests a model is good at extracting the essential ask from a verbose, real-world health question and restating it concisely, which is a narrow but practically useful skill for triage and retrieval systems, not a proxy for medical knowledge or answer correctness -- MeQSum never asks the model to answer the health question, only to summarise it. Because different harnesses may report different subsets of BLEU, ROUGE and embedding-based metrics, always check which metric a number uses before comparing it across sources: a strong ROUGE score and a strong BERTScore do not always move together on paraphrase-heavy generation tasks like this one. Given the small size and long public availability of the corpus, treat an unusually high score from a model with an unclear training cutoff with some caution.
