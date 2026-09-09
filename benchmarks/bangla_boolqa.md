---
id: bangla_boolqa
name: "Bangla BoolQA"
aliases:
  - "bangla_boolQA"
  - "BoolQ Bangla"
  - "BoolQ-BN"
page_kind: benchmark
category: reasoning
subcategory: "Bangla yes/no reading comprehension, GPT-4-generated rather than translated"
status: active
summary: "1,976 Bangla yes/no reading-comprehension questions GPT-4-generated from Bangla Wikipedia, Banglapedia and news passages; inspired by BoolQ's format but not a translation of it."
measures: >
  Bangla BoolQA tests whether a model can answer a yes/no question about a short Bangla passage,
  following the same task shape as the English BoolQ: a (passage, question, answer) triplet where
  the answer is "yes" or "no". It differs from the other three Bangla benchmarks introduced
  alongside it (bangla_commonsenseqa, bangla_piqa, bangla_openbookqa) in one important way: it is
  not a translation of the English dataset. The TituLLMs paper that introduces it describes it as
  "inspired by BoolQ", built from scratch with passages sourced from Bangla Wikipedia, Banglapedia
  and Bangla news articles, and yes/no questions generated over those passages by GPT-4. That
  construction method changes how a score should be read: unlike a translation, where the exact
  same 15,942 English items reappear in Bangla, this dataset is a fresh, natively-sourced set of
  1,976 items that only shares BoolQ's task format and inspiration, not its item pool.
task_format: >
  Binary yes/no question answering given a short Bangla passage. The reference lm-evaluation-harness
  task scores it zero- or few-shot as a multiple-choice comparison between the log-likelihood the
  model assigns to the Bangla words for "yes" and "no", rather than free-form generation.
metric:
  name: "accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50.0
  human_baseline: null
  baseline_note: >
    50% is the two-class random-guess rate. No Bangla-specific human baseline was established from
    a source read for this page; the original English BoolQ's approximately 90% human accuracy
    (recorded on this repository's boolq.md page) describes a different item pool in a different
    language and should not be assumed to transfer.
dataset:
  size: 1976
  size_note: >
    The TituLLMs paper's own Table 2 gives a 815/432/729 train/validation/test split (1,976 total),
    which matches the Hugging Face datasets-server's live row counts for hishab/boolq_bn exactly.
    Two other figures appear elsewhere in the same dataset card and should not be used: the card's
    prose summary states "15,942 examples," which is the English BoolQ's total item count and
    appears to be copied from a description of the original dataset rather than measured from this
    one; the card's own "Data Split" table gives a third figure (1,511 train / 947 test / 552
    validation, summing to 3,010), which matches neither the prose figure nor the paper nor the
    datasets-server. This page uses 1,976, the figure confirmed by both the introducing paper and
    the live served data. The card also states the dataset was manually spot-checked by a human
    annotator, who found a 1.33% error rate on a random sample and corrected it.
  url: "https://huggingface.co/datasets/hishab/boolq_bn"
  license: "MIT (Hugging Face dataset card)"
  languages:
    - bn
  modalities:
    - text
  splits: "train (815, used for few-shot sampling) / validation (432, the harness's scored eval split) / test (729, not used by the harness config read for this page)"
  public_test_set: true
publisher:
  org: "Hishab (Hishab Singapore Pte. Ltd), with the University of Central Florida and the Qatar Computing Research Institute"
  authors:
    - "Shahriar Kabir Nahin"
    - "Rabindra Nath Nandi"
    - "Sagor Sarker"
    - "Quazi Sarwar Muhtaseem"
    - "Md Kowsher"
    - "Apu Chandraw Shill"
    - "Md Ibrahim"
    - "Mehadi Hasan Menon"
    - "Tareq Al Muntasir"
    - "Firoj Alam"
  url: "https://github.com/hishab-nlp/titulm"
paper:
  title: "TituLLMs: A Family of Bangla LLMs with Comprehensive Benchmarking"
  arxiv: "2502.11187"
  url: "https://arxiv.org/abs/2502.11187"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/hishab-nlp/titulm"
released: "2025-02"
last_updated: ""
lineage:
  family: ""
  predecessor: "boolq"
  successors: []
  variants: []
saturation:
  status: open
  top_score: 69.0
  as_of: "2025-02"
  note: >
    The introducing paper's own results table reports only models of 3B parameters or fewer, plus
    the legacy GPT-davinci-002 as a baseline -- no frontier or larger model's score was established
    from a source read for this page. Within that limited set, scores range from close to the 50%
    random baseline (several small models score 0.53) up to 69% for Llama-3.2-3B at five-shot, with
    the paper's own TituLLM-3B model reaching only 51-54%. That is a real but modest separation from
    random guessing, well short of any ceiling, so this reflects an early, thinly-evaluated
    benchmark rather than a saturated one.
contamination:
  risk: medium
  note: >
    The question-answer pairs are GPT-4-generated and specific to this dataset, first published
    alongside the February 2025 paper, so they are unlikely to have been memorised by models
    trained well before that date. The source passages are a different matter: they come from
    Bangla Wikipedia, Banglapedia and news articles, all of which plausibly already appear in
    Bangla-capable models' pretraining data as raw text, independent of this benchmark. No held-out
    or refreshed portion is described by the authors.
harness:
  lm_eval: "boolqa_bn"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - reasoning
  - yes-no-qa
  - reading-comprehension
  - bangla
  - low-resource
sources:
  - url: "https://arxiv.org/abs/2502.11187"
    title: "TituLLMs: A Family of Bangla LLMs with Comprehensive Benchmarking"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2502.11187"
    title: "TituLLMs paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/hishab/boolq_bn"
    title: "hishab/boolq_bn dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/hishab/boolq_bn"
    title: "hishab/boolq_bn dataset metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=hishab/boolq_bn"
    title: "hishab/boolq_bn split sizes, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bangla/bangla_boolqa.yaml"
    title: "lm-evaluation-harness bangla_boolqa.yaml task config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bangla/README.md"
    title: "lm-evaluation-harness bangla tasks directory README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/README.md"
    title: "lm-evaluation-harness top-level task registry (lists 'bangla_boolQA')"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Bangla BoolQA asks a model to answer a yes/no question about a short Bangla passage, the same task shape as the English BoolQ: a (passage, question, answer) triplet. It is not, however, a translation of BoolQ. The TituLLMs paper that introduces it, alongside three other Bangla benchmarks in this batch, describes it as "inspired by BoolQ" -- built from Bangla-native passages drawn from Bangla Wikipedia, Banglapedia and news articles, with GPT-4 used to generate a fresh yes/no question over each passage. That matters for how a score reads: this is a natively-sourced, LLM-generated dataset that borrows BoolQ's format and motivation, not a Bangla copy of the 15,942 items the English benchmark uses. The other three Bangla benchmarks in the same paper (CommonsenseQA, PIQA, OpenBookQA) are machine translations of their English originals; this one is not, and the paper is explicit about the distinction.

## How it is scored

Every item is a binary yes/no judgement, so random guessing scores 50%. The reference lm-evaluation-harness task treats this as a multiple-choice problem: rather than generating free text, the model's log-likelihood for the Bangla equivalent of "yes" is compared against its log-likelihood for "no," and the higher-scoring option is taken as the prediction. The harness config scores the "validation" split (432 items) as its evaluation set and samples few-shot examples from "train" (815 items); the "test" split (729 items) exists in the released data but is not used by that task definition.

## Dataset and licence

The dataset totals 1,976 items. That figure comes from the TituLLMs paper's own Table 2 (815 train / 432 validation / 729 test) and is confirmed independently by the Hugging Face datasets-server's live row counts for `hishab/boolq_bn`. Two other, larger figures appear elsewhere on the same dataset card and should be treated as errors in that card, not alternate readings: its prose summary states "15,942 examples" (the English BoolQ's total, apparently carried over by description rather than measured from this dataset), and its own "Data Split" table gives a third figure (1,511/947/552, summing to 3,010) that matches neither the prose nor the paper nor the live data. The card states an MIT licence, and that a human annotator spot-checked a random sample, finding and correcting a 1.33% error rate.

## Who publishes it

Bangla BoolQA comes from the TituLLMs paper, "TituLLMs: A Family of Bangla LLMs with Comprehensive Benchmarking" (Shahriar Kabir Nahin, Rabindra Nath Nandi, Sagor Sarker, Quazi Sarwar Muhtaseem and Md Kowsher, credited to Hishab Singapore Pte. Ltd and the University of Central Florida; Apu Chandraw Shill, Md Ibrahim, Mehadi Hasan Menon, Tareq Al Muntasir and Firoj Alam, credited to the Qatar Computing Research Institute), posted to arXiv in February 2025. Hishab, a Bangla-language NLP company, maintains the reference `titulm` repository and the dataset on Hugging Face.

## Lineage

This page names `boolq` (BoolQ, on this repository's boolq.md) as its predecessor in the sense that it borrows BoolQ's task format and cites BoolQ as its direct inspiration, but the two do not share an item pool: BoolQ's items were never translated here, and this dataset's 1,976 items are original to it. It belongs to a family of four Bangla benchmarks published together in the same paper -- `bangla_commonsenseqa`, `bangla_piqa` and `bangla_openbookqa`, all in this repository -- of which it is the only one built by generation rather than translation.

## Saturation and contamination

The introducing paper's own results table covers only models of 3B parameters or fewer, plus the legacy GPT-davinci-002 as a reference point; no larger or more recent frontier model's score on this benchmark was found from a source read for this page. Among the models it does report, scores range from close to the 50% random baseline up to 69% (Llama-3.2-3B, five-shot), with the paper's own TituLLM-3B model reaching only 51-54%. That is real separation from chance but far from a ceiling, consistent with a new, thinly-evaluated benchmark rather than a saturated one. Contamination risk sits at medium: the specific question-answer pairs are GPT-4-generated and only as old as the February 2025 paper, but the underlying Bangla Wikipedia, Banglapedia and news passages they were built from are plausibly already present in Bangla-capable models' general pretraining data.

## How to run it

The reference implementation lives in lm-evaluation-harness's shared `lm_eval/tasks/bangla/` directory, in `bangla_boolqa.yaml` -- not in a task-specific directory of its own, despite what some external listings of this benchmark suggest. The runnable task name declared inside that file is `boolqa_bn`, not `bangla_boolqa`: the two differ, and only `boolqa_bn` works with `--tasks`. The harness's own top-level registry (`lm_eval/tasks/README.md`) separately lists this benchmark under a third name, `bangla_boolQA`, a display label linking to the shared directory's README rather than to a runnable task -- an inconsistency across the harness's own files, recorded here in `aliases` rather than treated as the real identifier. No HELM, OpenCompass, inspect_evals or BIG-bench implementation was found.

## Reading the numbers

A high Bangla BoolQA score indicates a model can perform entailment-style yes/no reasoning over Bangla passages drawn from encyclopaedic and news sources -- but because the benchmark is brand new and only reported for small models so far, there is no established sense of where a strong frontier-model score would land, or of what score should be considered good. Do not compare a Bangla BoolQA number directly against an English BoolQ number: they are different item pools in different languages, with BoolQ closer to its ceiling than this benchmark appears to be. Because this dataset was generated rather than translated, a low score cannot be blamed on translation artefacts the way it could for this batch's other three Bangla benchmarks; a low score here more plausibly reflects genuine weakness in Bangla reading comprehension or in handling news-length context.
