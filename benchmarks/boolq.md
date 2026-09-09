---
id: boolq
name: "BoolQ"
aliases:
  - "Boolean Questions"
page_kind: benchmark
category: reasoning
subcategory: "reading comprehension: naturally occurring yes/no questions requiring entailment-style inference over a passage"
status: saturated
summary: "15,942 naturally occurring yes/no reading-comprehension questions paired with a Wikipedia passage; part of SuperGLUE and now largely saturated for frontier models."
measures: >
  BoolQ tests whether a model can answer a naturally occurring yes/no question by reading a short
  passage and performing non-factoid, entailment-like inference rather than simple word matching.
  Each item pairs a question with a Wikipedia passage that answers it, and the model must output
  yes or no. Unlike constructed reading-comprehension datasets, the questions were not written by
  annotators looking at a passage: they were sampled from real, anonymised queries people had
  already typed into a search engine, then matched to a passage that answers them, which the
  original authors argue makes them harder and more natural than templated question-answer pairs.
task_format: "Binary yes/no question answering given a short passage, zero- or few-shot, English."
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50.0
  human_baseline: 90.0
  baseline_note: >
    50% is the two-class random-guess rate. The paper separately reports a majority-class baseline
    of about 62% (the majority gold answer is "yes") and human accuracy of about 90% on a sample.
    Its own best model in 2019, BERT pretrained then transferred from MultiNLI, reached 80.4%.
dataset:
  size: 15942
  size_note: >
    15,942 examples total: 9,427 train, 3,270 validation (both labelled), and 3,245 test (labels
    never publicly released by the original authors). The Hugging Face mirror `google/boolq`
    exposes only the labelled train and validation splits -- 12,697 rows, confirmed via the
    datasets-server size endpoint -- because the true test split was never published with answers.
  url: "https://huggingface.co/datasets/google/boolq"
  license: "CC BY-SA 3.0 (Hugging Face dataset card and GitHub repository both state this)"
  languages:
    - en
  modalities:
    - text
  splits: "train (9,427) / validation (3,270, labelled) / test (3,245, answers not publicly released)"
  public_test_set: false
publisher:
  org: "Google Research"
  authors:
    - "Christopher Clark"
    - "Kenton Lee"
    - "Ming-Wei Chang"
    - "Tom Kwiatkowski"
    - "Michael Collins"
    - "Kristina Toutanova"
  url: "https://github.com/google-research-datasets/boolean-questions"
paper:
  title: "BoolQ: Exploring the Surprising Difficulty of Natural Yes/No Questions"
  arxiv: "1905.10044"
  url: "https://arxiv.org/abs/1905.10044"
  year: 2019
leaderboard_url: "https://super.gluebenchmark.com/leaderboard"
repo_url: "https://github.com/google-research-datasets/boolean-questions"
released: "2019-05"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: null
  as_of: ""
  note: >
    No specific current top score is recorded here: this page's attempts to read a maintained
    leaderboard did not succeed (the SuperGLUE leaderboard did not render as static content, and
    paperswithcode's historical BoolQ page no longer resolves to leaderboard data), so no number is
    claimed that was not read from a source. That said, the paper's own reference points already
    suggest a close ceiling -- human accuracy near 90%, majority-class baseline near 62%, and a
    BERT-based model at 80.4% in the year of release -- and BoolQ is treated in practice as saturated
    for instruction-tuned frontier models, which is why it now appears as one line inside broader
    suites (HELM, lm-evaluation-harness, inspect_evals) rather than as a standalone leaderboard.
contamination:
  risk: high
  note: >
    The split every harness reviewed for this page actually scores -- the 3,270-example validation
    set -- has carried public answers since the 2019 release; only the 3,245-example official test
    split has ever had its answers withheld, and none of lm-evaluation-harness, HELM or inspect_evals
    evaluates against that held-out split. Passages are drawn from Wikipedia, a second route by
    which the source text, if not the exact question-answer pairing, could reach pretraining data.
harness:
  lm_eval: "boolq"
  inspect_evals: "boolq"
  helm: "boolq"
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - reading-comprehension
  - yes-no
  - entailment
  - superglue
  - saturated
sources:
  - url: "https://arxiv.org/abs/1905.10044"
    title: "BoolQ: Exploring the Surprising Difficulty of Natural Yes/No Questions"
    accessed: "2026-09-08"
  - url: "https://github.com/google-research-datasets/boolean-questions"
    title: "google-research-datasets/boolean-questions GitHub repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/google/boolq"
    title: "google/boolq dataset metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/boolq_scenario.py"
    title: "HELM boolq_scenario.py"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/boolq"
    title: "inspect_evals boolq task"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/super_glue"
    title: "lm-evaluation-harness super_glue tasks directory"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice E"
---

## What it measures

BoolQ tests whether a model can answer a naturally occurring yes/no question by reading a short passage and performing non-factoid, entailment-like inference rather than simple word matching. Each item pairs a question with a Wikipedia passage that answers it, and the model must output yes or no. Unlike constructed reading-comprehension datasets, the questions were not written by annotators looking at a passage: they were sampled from real, anonymised queries people had already typed into a search engine, then matched to a Wikipedia passage that answers them. The original authors argue this makes BoolQ questions harder and more natural than templated question-answer pairs, since nothing about how a question was phrased was shaped by the passage that would later answer it.

## How it is scored

Scoring is plain accuracy against the gold yes/no label. The paper reports a majority-class baseline near 62% (most gold answers are "yes"), separate from the 50% two-class random-guess rate, and a human accuracy of about 90% measured on a sample. Its own best 2019 model, BERT pretrained and then transferred from the MultiNLI entailment dataset, reached 80.4%, and the paper's central finding is that transfer from entailment data helped more than transfer from paraphrase or extractive-QA data. Current harnesses score the same way: a generated or ranked yes/no answer compared against the gold label, with no partial credit.

## Dataset and licence

BoolQ totals 15,942 examples: 9,427 for training, 3,270 for validation, and 3,245 for test. Both the train and validation splits carry public labels; the test split's answers were never released by the original authors, and the Hugging Face mirror (`google/boolq`) exposes only the 12,697 labelled train-plus-validation rows as a result. The Hugging Face dataset card and the GitHub repository both give the licence as CC BY-SA 3.0. Passages come from Wikipedia articles; questions were filtered from real search queries down to ones answerable yes or no by a matched passage, then annotated and checked by crowd workers.

## Who publishes it

BoolQ comes from Christopher Clark, Kenton Lee, Ming-Wei Chang, Tom Kwiatkowski, Michael Collins and Kristina Toutanova at Google Research, published at NAACL 2019. The reference repository is `google-research-datasets/boolean-questions` on GitHub. BoolQ is also one of the eight tasks in the SuperGLUE benchmark suite, whose own leaderboard (`super.gluebenchmark.com`) is the closest thing to a maintained comparison point today, alongside the dataset's own repository, which notes a standalone leaderboard was planned but not confirmed live at the time of this research.

## Lineage

This repository does not track a predecessor or successor for BoolQ directly. It is one of the eight SuperGLUE tasks, and this repository does not yet have a SuperGLUE family page for it to belong to. BoolQ Contrast Sets, a smaller set of human-perturbed items from Allen AI used by HELM as a robustness check, is a variant that also does not have its own page here.

## Saturation and contamination

The paper's own numbers already point toward a close ceiling: human accuracy near 90%, a majority-class baseline near 62%, and an early BERT-based model already at 80.4% in 2019. This page could not read a current maintained leaderboard to confirm a specific present-day top score, but BoolQ is widely treated as saturated for frontier instruction-tuned models, consistent with its current role as one line inside broader suites rather than a standalone leaderboard. Contamination risk is high in practice: every harness reviewed for this page scores the labelled validation split, which has been public since 2019, rather than the genuinely held-out test split, so a model could plausibly have encountered both the questions and their answers during training.

## How to run it

lm-evaluation-harness implements BoolQ as task `boolq` inside its `super_glue` task group, scored by comparing the log-likelihood the model assigns to "yes" against "no." HELM's `boolq` scenario adds an optional robustness check against the human-perturbed contrast sets. inspect_evals' `boolq` task pulls the Hugging Face validation split (3,270 samples) and computes simple accuracy. All three score the labelled validation split rather than the official held-out test split, so "BoolQ test accuracy" in most papers and model cards actually means validation accuracy.

## Reading the numbers

A high BoolQ score today mostly confirms a model can do basic passage-grounded yes/no inference, a capability frontier models cleared years ago, so it reads better as a floor check than as a differentiator between strong models. Because every mainstream harness scores the public validation split, treat scores from recent models with some caution for contamination rather than as clean evidence of reasoning ability. Compare a reported number against the roughly 90% human ceiling and roughly 62% majority baseline from the original paper: many current models exceed the ceiling that separated strong 2019 systems, which is more consistent with saturation and prior exposure than with genuine remaining headroom. Pair a BoolQ number with a harder, less exposed reading-comprehension or entailment benchmark before drawing conclusions about a model's inference ability from it alone.
