---
id: mmlu
name: "MMLU (Massive Multitask Language Understanding)"
aliases:
  - "Massive Multitask Language Understanding"
  - "Hendrycks Test"
page_kind: family
category: knowledge
subcategory: "multitask academic and professional knowledge"
status: active
summary: "A 57-subject, four-choice knowledge test from elementary to professional difficulty; the standard reference for broad model knowledge since 2020, now saturated at the frontier."
measures: >
  Each question gives the model a short prompt and four labelled answer options drawn from one of
  57 academic and professional subjects, from abstract algebra to professional law. The model must
  pick the single correct option. This mostly exercises declarative and procedural knowledge
  acquired during pretraining rather than multi-step reasoning, and the original paper found
  lopsided results across subjects rather than uniform competence.
task_format: >
  Four-option multiple-choice question answering, graded on the single labelled option (A-D) the
  model selects. Evaluated zero-shot or few-shot; the original paper's dev split provides up to 5
  worked examples per subject for the few-shot case, and 5-shot has become the common reporting
  condition. Scored either by comparing the log-likelihood the model assigns to each answer letter
  as a continuation, or by having the model generate free text and parsing out a letter.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: 89.8
  baseline_note: >
    25% is the four-option random-guess rate. The paper separately reports 34.5% average accuracy
    for unspecialized human raters on Amazon Mechanical Turk, and estimates 89.8% as an
    expert-level ceiling; Google reported Gemini Ultra at 90.0% in December 2023, by its own
    account the first published score above that estimate.
dataset:
  size: 14042
  size_note: >
    The paper reports 15,908 questions in total: a 14,079-question test split (used for scoring),
    a 1,540-question validation split, and a 285-question dev split (5 per subject, for few-shot
    prompts). The Hugging Face parquet mirror (cais/mmlu) accessed for this page totals 14,042
    test, 1,531 validation and 285 dev rows instead -- a small, unexplained drop from the paper's
    original test count that this page reports rather than reconciles -- plus a separate
    99,842-row auxiliary_train split pooled from other multiple-choice sources for fine-tuning,
    not used for scoring. Individual subject test splits range from 100 questions (the paper's
    stated minimum, e.g. Global Facts, College Mathematics) to 1,534 (Professional Law, the
    largest).
  url: "https://huggingface.co/datasets/cais/mmlu"
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "auxiliary_train (99,842, not scored), dev (285, 5/subject), validation (1,531), test (14,042 per the Hugging Face mirror; the paper reports 14,079)"
  public_test_set: true
publisher:
  org: "UC Berkeley (original); Center for AI Safety (current host)"
  authors:
    - "Dan Hendrycks"
    - "Collin Burns"
    - "Steven Basart"
    - "Andy Zou"
    - "Mantas Mazeika"
    - "Dawn Song"
    - "Jacob Steinhardt"
  url: "https://github.com/hendrycks/test"
paper:
  title: "Measuring Massive Multitask Language Understanding"
  arxiv: "2009.03300"
  url: "https://arxiv.org/abs/2009.03300"
  year: 2021
leaderboard_url: "https://github.com/hendrycks/test"
repo_url: "https://github.com/hendrycks/test"
released: "2020-09"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors:
    - mmlu_pro
  variants:
    - mmmlu
saturation:
  status: saturated
  top_score: 90.0
  as_of: "2023-12"
  note: >
    Google reported Gemini Ultra at 90.0% in December 2023, by Google's own account the first
    published score to exceed the paper's 89.8% expert-level estimate. Hugging Face cited the
    resulting loss of headroom at the top of its Open LLM Leaderboard as a reason to drop raw MMLU
    in the June 2024 v2 relaunch, replacing it with MMLU-Pro alongside GPQA, MuSR, IFEval, BBH and
    MATH Lvl 5.
contamination:
  risk: high
  note: >
    The test set, including its answer key, has been publicly downloadable since September 2020
    and is mirrored across GitHub, Hugging Face and countless secondary sites, making exclusion
    from web-scale pretraining corpora hard to guarantee. MMLU-CF, a 2024 contamination-controlled
    replacement benchmark, reports GPT-4o scoring 88.0% on standard MMLU but only 73.4% 5-shot on
    its decontaminated question set, a gap the authors attribute to leakage.
harness:
  lm_eval: "mmlu (group of 57 mmlu_<subject> tasks, plus continuation and generative variants)"
  helm: "mmlu (subject parameter, e.g. mmlu:subject=anatomy)"
  opencompass: "mmlu (mmlu_gen / mmlu_ppl config variants)"
  bigbench: ""
  other: "Open LLM Leaderboard v1 (2023-2024) ran an older harness fork with the same 57 tasks named hendrycksTest-<subject>, 5-shot."
tags:
  - knowledge
  - multiple-choice
  - multitask
  - zero-shot
  - five-shot
sources:
  - url: "https://arxiv.org/abs/2009.03300"
    title: "Measuring Massive Multitask Language Understanding (Hendrycks et al., arXiv:2009.03300)"
    accessed: "2026-09-07"
  - url: "https://github.com/hendrycks/test"
    title: "hendrycks/test GitHub repository (MMLU reference implementation)"
    accessed: "2026-09-07"
  - url: "https://huggingface.co/datasets/cais/mmlu"
    title: "cais/mmlu dataset card, Hugging Face"
    accessed: "2026-09-07"
  - url: "https://arxiv.org/abs/2406.01574"
    title: "MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark"
    accessed: "2026-09-07"
  - url: "https://huggingface.co/datasets/openai/MMMLU"
    title: "openai/MMMLU dataset card, Hugging Face"
    accessed: "2026-09-07"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/mmlu/README.md"
    title: "lm-evaluation-harness mmlu task README"
    accessed: "2026-09-07"
  - url: "https://huggingface.co/docs/leaderboards/en/open_llm_leaderboard/archive"
    title: "Open LLM Leaderboard v1 archive documentation, Hugging Face"
    accessed: "2026-09-07"
  - url: "https://huggingface.co/blog/open-llm-leaderboard-mmlu"
    title: "What is going on with the Open LLM Leaderboard?, Hugging Face blog"
    accessed: "2026-09-07"
  - url: "https://arxiv.org/abs/2412.15194"
    title: "MMLU-CF: A Contamination-free Multi-task Language Understanding Benchmark"
    accessed: "2026-09-07"
  - url: "https://blog.google/technology/ai/google-gemini-ai/"
    title: "Introducing Gemini: our largest and most capable AI model, Google"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice A"
---

## What it measures

MMLU gives a model a short question and four labelled options (A-D) drawn from one of 57 subjects
spanning STEM, the humanities, the social sciences, and an "other" bucket covering business,
health and miscellaneous topics, ranging "from an elementary level to an advanced professional
level." The model selects the one correct option.

The knowledge exercised is mostly declarative and procedural recall from pretraining rather than
open-ended reasoning. Results are lopsided: a model with a strong average can still sit near
random chance on individual subjects, and the paper flags "near-random accuracy on some socially
important subjects such as morality and law."

## How it is scored

The metric is accuracy against a 25% random-guess floor. The paper's own human baselines are 34.5%
for unspecialized Mechanical Turk raters and an estimated 89.8% expert-level ceiling, so a raw
score reads better against those anchors than against 100%.

The protocol prepends "The following are multiple choice questions (with answers) about
[subject]," then evaluates zero-shot or few-shot with up to 5 worked examples from the dev split;
5-shot is the de facto standard. Scoring either compares the log-likelihood of each answer letter
as a continuation (the original and lm-evaluation-harness default) or has the model generate free
text and parses out a letter. Hugging Face's comparison of three implementations (original code,
HELM, EleutherAI harness) found one LLaMA 65B checkpoint scoring 48.8% to 63.7% from prompt
formatting and scoring method alone -- MMLU numbers from different sources are not automatically
comparable.

## Dataset and licence

The paper reports 15,908 questions total (14,079 test, 1,540 validation, 285 dev). The Hugging
Face parquet mirror totals 14,042 test, 1,531 validation and 285 dev instead, plus a separate
99,842-row auxiliary_train split for fine-tuning, not scoring. Subject test splits range from 100
questions (the stated minimum) to 1,534 (Professional Law).

Questions were manually collected by graduate and undergraduate students from free online sources,
including GRE and USMLE practice questions and course materials. The repository and dataset card
give the licence as MIT; answers are public in every split. The dataset card's sections on
annotation process and bias discussion are marked "more information needed" by its maintainers.

## Who publishes it

Dan Hendrycks, Collin Burns, Steven Basart, Andy Zou, Mantas Mazeika, Dawn Song and Jacob Steinhardt
published MMLU in September 2020; the paper appeared at ICLR 2021. Hendrycks now directs the
Center for AI Safety, which hosts the Hugging Face mirror under the `cais` organisation. The
GitHub repository `hendrycks/test` remains the reference implementation and licence source.

## Lineage

MMLU has no predecessor. Two descendants matter: MMLU-Pro (`mmlu_pro`), which keeps the
57-subject structure but expands to ten options with harder, more reasoning-heavy questions, partly
to restore headroom lost to saturation; and MMMLU (`mmmlu`), OpenAI's human translation of the test
set into 14 languages, published as `openai/MMMLU`. Neither has its own page in this batch.

Each of the 57 subjects is a `subset` page carrying `lineage.family: mmlu`. A few ids --
`mmlu_biology`, `mmlu_chemistry`, `mmlu_computer_science` -- are not raw subjects but coarser STEM
subcategories the authors define in `categories.py`, used by publishers reporting MMLU at that
broader grain; see those pages for the subjects each pools.

## Saturation and contamination

MMLU is saturated at the frontier. Google reported Gemini Ultra at 90.0% in December 2023, by its
own account the first score to exceed the paper's 89.8% expert-level estimate. The resulting
compression at the top of leaderboards is why Hugging Face dropped raw MMLU from the Open LLM
Leaderboard in its June 2024 v2 relaunch, replacing it with MMLU-Pro and other benchmarks
described as "built to resist saturation."

Contamination risk is high: the test set and answer key have been public since September 2020 and
are mirrored widely, hard to exclude from web-scale pretraining. MMLU-CF, a contamination-controlled
replacement, reports GPT-4o scoring 88.0% on standard MMLU but only 73.4% 5-shot on its
decontaminated set, a gap the authors attribute to leakage.

## How to run it

The reference implementation is `hendrycks/test` on GitHub. In lm-evaluation-harness the group is
`mmlu`, with one `mmlu_<subject>` task per subject plus `continuation` and `generative`
prompt-format variants; the Open LLM Leaderboard v1 (2023-2024) ran an older harness fork naming
the same 57 tasks `hendrycksTest-<subject>`, 5-shot. HELM implements it as the `mmlu` scenario with
a `subject` parameter (e.g. `mmlu:subject=anatomy`). OpenCompass ships it as the `mmlu` dataset
family, with generative and log-likelihood config variants.

As the scoring section shows, prompt template and scoring method each move the number by double
digits, so only compare scores run under matching conditions.

## Reading the numbers

A high aggregate MMLU score signals broad factual and procedural knowledge but says little about
reasoning under novelty, and among frontier models it barely separates them -- most cluster within
a few points of the human-expert estimate, which is why MMLU-Pro and GPQA now carry more weight
for distinguishing top models. A single overall number also hides subject-level spread: check
per-subject scores before assuming uniform competence, especially on subjects the paper flagged as
weak or safety-relevant. Always check the shot count and scoring method behind a number before
comparing it to another model's score.
