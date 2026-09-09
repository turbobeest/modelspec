---
id: mathqa
name: "MathQA"
aliases: []
page_kind: benchmark
category: math
subcategory: "multiple-choice math word problems with operation-program annotations"
status: active
summary: >-
  A 37k-problem multiple-choice math word problem dataset built by re-annotating AQuA-RAT with
  interpretable, formal operation programs rather than free-text rationales.
measures: >
  MathQA gives a model a short math word problem in English plus five lettered answer options and
  asks it to pick the correct one. The problems themselves come from the earlier AQuA-RAT dataset;
  MathQA's contribution is a new representation language that annotates each problem with a formal,
  step-by-step operation program (a sequence of arithmetic operations over the problem's numbers and
  a small set of constants) rather than AQuA-RAT's original free-text rationale, so that a system's
  reasoning can be checked structurally rather than only judged by its final answer. As distributed
  for language-model evaluation, only the question and options are used; the operation-program
  annotations exist in the data but the standard multiple-choice harness task does not require a
  model to produce one.
task_format: >
  Multiple-choice question answering: a word problem followed by (typically) five lettered options.
  In lm-evaluation-harness the task is scored by comparing the model's log-likelihood on each
  option's text as a completion of the question, not by free-text generation.
metric:
  name: "accuracy and length-normalised accuracy (acc, acc_norm) over the selected option"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Most items carry five answer options (labelled a-e), but option counts are extracted per item
    by the harness rather than fixed by schema, so a single random-guess percentage is not asserted
    here. No human baseline was found in the sources opened for this page; the original paper
    compares its own sequence-to-program model against prior automatic solvers, not human solvers.
dataset:
  size: 37200
  size_note: >
    The paper's own prose states "37,200 math word problems"; its Table 1 category breakdown sums to
    a slightly different total, 37,259 -- a small internal discrepancy in the source itself, not a
    rounding choice made for this page. The paper reports a random 80/12/8% train/dev/test split of
    the full set; exact per-split counts were not stated as whole numbers in the source and are not
    inferred here. MathQA extends AQuA-RAT (Ling et al. 2017), which itself was expanded by
    crowdsourcing from a seed set of 30,000 problems.
  url: "https://huggingface.co/datasets/allenai/math_qa"
  license: "Apache-2.0"
  languages: ["en"]
  modalities: ["text"]
  splits: "train/validation/test, randomly split 80/12/8% of the full problem set"
  public_test_set: true
publisher:
  org: "University of Washington; Allen Institute for AI"
  authors: ["Aida Amini", "Saadia Gabriel", "Peter Lin", "Rik Koncel-Kedziorski", "Yejin Choi", "Hannaneh Hajishirzi"]
  url: "https://math-qa.github.io/math-QA/"
paper:
  title: "MathQA: Towards Interpretable Math Word Problem Solving with Operation-Based Formalisms"
  arxiv: "1905.13319"
  url: "https://arxiv.org/abs/1905.13319"
  year: 2019
leaderboard_url: ""
repo_url: ""
released: "2019-05"
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
    The original paper's own sequence-to-program models scored well below human performance on
    MathQA at release, but no source opened for this page reported a current frontier-model score on
    MathQA specifically, and it was not found cited as a headline number in any current model card or
    leaderboard checked during this research. Its standing against 2025-2026 models is therefore not
    established here; a five-option multiple-choice grade-school-to-competition word-problem format
    is the kind of task that saturates quickly for modern LLMs, but that is not confirmed by a source
    for this page.
contamination:
  risk: high
  note: >
    MathQA's questions, options and correct answers have been fully public since 2019 on the
    project's own site and on Hugging Face, and it is one of the older, widely-mirrored benchmark
    datasets in the field. The lm-evaluation-harness task definition itself sets
    `should_decontaminate: true` with an explicit decontamination query field, which is the harness
    maintainers' own acknowledgement that training-set overlap is a live concern for this task.
harness:
  lm_eval: "mathqa"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    lm-evaluation-harness's `mathqa` task loads a `regisss/math_qa` Hugging Face mirror rather than
    the canonical `allenai/math_qa` repository used elsewhere in this page; both should carry the
    same underlying AQuA-RAT-derived problems, but a reproduction should confirm which copy a given
    score used. No HELM, OpenCompass or BIG-bench registration was confirmed during this research.
tags:
  - math
  - word-problems
  - multiple-choice
  - arithmetic-reasoning
sources:
  - url: "https://arxiv.org/abs/1905.13319"
    title: "MathQA: Towards Interpretable Math Word Problem Solving with Operation-Based Formalisms"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1905.13319"
    title: "MathQA (full text, ar5iv) -- dataset size, category table, 80/12/8% split statement"
    accessed: "2026-09-08"
  - url: "https://math-qa.github.io/math-QA/"
    title: "MathQA project homepage (annotation process, AQuA-RAT provenance)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/allenai/math_qa"
    title: "allenai/math_qa dataset card (Apache-2.0 licence, AQuA-RAT extension)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/mathqa/mathqa.yaml"
    title: "lm-evaluation-harness mathqa.yaml (multiple_choice format, regisss/math_qa path, should_decontaminate)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/mathqa/README.md"
    title: "lm-evaluation-harness mathqa README (37k problems, AQuA-RAT relationship, citation)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MathQA gives a model a short English math word problem plus five lettered answer options and asks
it to pick the correct one. The problems themselves are inherited from the earlier AQuA-RAT dataset;
MathQA's own contribution is a new representation language that re-annotates each problem with a
formal, step-by-step operation program -- a sequence of arithmetic operations over the problem's
numbers and a small constant set -- in place of AQuA-RAT's noisy, sometimes-incorrect free-text
rationales. That was meant to let a system's reasoning be checked structurally, not just its final
answer. As used for language-model evaluation, only the question text and the five options matter:
the operation-program annotations exist in the data but the standard multiple-choice harness task
does not ask a model to produce one.

## How it is scored

In lm-evaluation-harness, MathQA is a `multiple_choice` task: the model's log-likelihood is computed
for each answer option as a continuation of the question, and the option with the highest score
(plain or length-normalised) is taken as the model's answer. Both `acc` and `acc_norm` are reported.
This is a likelihood-comparison format, not free-text generation, so results depend on tokenisation
and prompt formatting in the way that all log-likelihood multiple-choice tasks do. No confirmed
human baseline was found; the original paper instead compares its own sequence-to-program models
against earlier automatic math-word-problem solvers on both MathQA and the source AQuA dataset.

## Dataset and licence

The paper's prose states MathQA holds 37,200 problems; its own Table 1 category breakdown sums to a
slightly different total, 37,259 -- a small discrepancy in the source itself rather than a rounding
choice made here. The full set is randomly split 80/12/8% into training, development and test
problems. MathQA extends AQuA-RAT (Ling et al., 2017), itself expanded by crowdsourcing from a seed
set of 30,000 problems; many MathQA items are consequently near-duplicates of each other with only
numbers or story details changed. The canonical Hugging Face mirror (`allenai/math_qa`) carries an
Apache-2.0 licence; questions, options and correct answers are all public.

## Who publishes it

MathQA was introduced by Aida Amini, Saadia Gabriel, Peter Lin, Rik Koncel-Kedziorski, Yejin Choi and
Hannaneh Hajishirzi, working at the University of Washington and the Allen Institute for AI, in a
paper posted to arXiv in May 2019. The project's homepage (math-qa.github.io) documents the
annotation platform and process; no organisation runs an actively updated public leaderboard for it
today.

## Lineage

MathQA is a direct re-annotation of AQuA-RAT (Ling et al., 2017), which does not yet have its own
page in this repository; the relationship is not a benchmark "family" in the sense of shared subset
pages, but a dataset built by adding formal operation-program labels to an existing one. No successor
benchmark or repository variant of MathQA itself was identified during this research. Readers should
not confuse MathQA (a multiple-choice math word-problem dataset) with `mathbench` (a bilingual
five-stage mathematics evaluation suite) or `matbench` (a materials-science property-prediction
benchmark) elsewhere in this batch -- the three names are easy to mistake for one another but test
unrelated things.

## Saturation and contamination

No source opened for this page reported a current frontier-model score on MathQA, and it did not
appear as a headline benchmark in any current model card or leaderboard checked during this
research, so its saturation status against 2025-2026 models is not established here. Contamination
risk is high: the dataset has been fully public, with answers, since 2019, is one of the
longest-standing benchmarks in this space, and the lm-evaluation-harness task definition itself sets
`should_decontaminate: true` with a dedicated decontamination-query field -- the harness maintainers'
own signal that training-set overlap is a live concern rather than a hypothetical one.

## How to run it

lm-evaluation-harness registers the task as `mathqa` under the `math_word_problems` tag, loading a
`regisss/math_qa` Hugging Face mirror rather than the canonical `allenai/math_qa` repository used
elsewhere on this page; both should carry the same AQuA-RAT-derived problems, but a reproduction
should confirm which copy produced a given number. No HELM, OpenCompass, inspect_evals or BIG-bench
registration was confirmed during this research, and none of MathQA's operation-program annotations
are exercised by the standard multiple-choice task.

## Reading the numbers

A MathQA score reflects five-option multiple-choice arithmetic word-problem solving under a
log-likelihood comparison, not free-text generation and not the structured operation-program
reasoning the dataset was actually built to enable -- so a high score says a model can pick the right
option, not that it can produce a verifiable calculation trace. Given the dataset's age, its full
public availability since 2019, and its origin in a crowdsourced, near-duplicate-heavy source
(AQuA-RAT), a strong MathQA score is weak evidence of contamination-free reasoning and should be read
alongside a newer, harder math benchmark rather than on its own.
