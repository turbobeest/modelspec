---
id: hle
name: Humanity's Last Exam
aliases:
  - HLE
page_kind: benchmark
category: reasoning
subcategory: frontier academic knowledge Q&A
status: active
summary: 2,500 expert-written, closed-ended questions spanning dozens of academic subjects, built by CAIS and Scale AI to replace saturated benchmarks like MMLU.
measures: >
  Humanity's Last Exam (HLE) tests whether a model can answer closed-ended academic questions at
  the frontier of human expertise, across dozens of subjects including mathematics, the humanities
  and the natural sciences. Each question was written by a subject-matter expert and is deliberately
  constructed to have a single, unambiguous, verifiable answer that cannot be produced quickly by
  searching the internet. About 90% of questions are text-only; the remainder pair text with a
  reference image, so the benchmark is described by its authors as multi-modal rather than
  vision-first. The benchmark also scores calibration: whether a model's stated confidence matches
  how often it is actually correct.
task_format: >
  Single-turn question, either exact-match (a short string or number the model must produce, roughly
  80% of items) or multiple-choice with five or more options (the remainder). About 10% of questions
  include a reference image alongside the text. Models are also asked to state a numeric confidence
  (0-100%) alongside their answer, which feeds the calibration metric.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  baseline_note: >
    No fixed random baseline applies because the format mixes exact-match questions (no baseline) with
    multiple-choice questions of varying option counts. The paper reports a second metric alongside
    accuracy, RMS calibration error (0-100, lower is better), computed with the method from Hendrycks
    et al.; HLE does not publish a single human-expert baseline the way some closed-ended benchmarks
    do, since the questions are selected specifically to stump the domain experts who help write them.
dataset:
  size: 2500
  size_note: >
    The dataset launched in January 2025 with 3,000 questions; the abstract of the arXiv paper, as
    revised through mid-2026, now describes 2,500, after later revisions removed contested or flawed
    items. A private held-out set is kept alongside the public set specifically to detect overfitting
    and gaming. The authors also maintain "HLE-Rolling," a separately versioned dynamic fork that
    swaps in harder held-out questions over time and is not comparable to the static set.
  url: https://huggingface.co/datasets/cais/hle
  license: CC BY 4.0
  languages:
    - en
  modalities:
    - text
    - image
  splits: single public test split, plus a private held-out set not released
  public_test_set: true
publisher:
  org: Center for AI Safety and Scale AI
  authors:
    - Long Phan
    - Alice Gatti
    - Ziwen Han
    - Nathaniel Li
    - Summer Yue
    - Alexandr Wang
    - Dan Hendrycks
  url: https://lastexam.ai
paper:
  title: "Humanity's Last Exam"
  arxiv: "2501.14249"
  url: https://arxiv.org/abs/2501.14249
  year: 2025
leaderboard_url: https://agi.safe.ai/dashboard
repo_url: https://github.com/centerforaisafety/hle
released: "2025-01"
last_updated: "2026-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - hle_tools
saturation:
  status: open
  top_score: 37.5
  as_of: "2025-11"
  note: >
    At the January 2025 release, the best model (DeepSeek-R1, text-only subset) scored 9.4% against
    GPT-4o's 3.3%. By November 2025, Anthropic's Claude Opus 4.5 System Card measured Gemini 3 at
    37.5% without search, the highest of six frontier models it charted (Claude Opus 4.1, Claude
    Sonnet 4.5, GPT-5, GPT-5 Pro, Claude Opus 4.5, Gemini 3). Scores have risen quickly but remain far
    below the ceiling, so HLE still separates frontier models by a wide margin.
contamination:
  risk: medium
  note: >
    The public release carries a canary string and the authors screened candidate questions against
    contemporary frontier models before inclusion, but the questions have been public since January
    2025 and are a popular target for both training and evaluation. A third-party audit ("HLE-Verified")
    has since re-checked the static set for erroneous or compromised items. Anthropic's Claude Opus 4.5
    System Card (November 2025) reports actively flagging and re-grading transcripts in its
    search-enabled evaluation that had visited known answer-sheet domains or otherwise appeared to
    retrieve answers rather than derive them, which is direct evidence that contamination is a live
    risk once a model is allowed to browse.
harness:
  lm_eval: ""
  inspect_evals: hle
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    The authors' own repository (centerforaisafety/hle) ships run_model_predictions.py and
    run_judge_results.py, using an automated GPT-4o judge against a standardized reasoning-then-answer
    prompt; this is the closest thing to an official harness and is what most labs' self-reported
    numbers are built on.
tags:
  - reasoning
  - multi-modal
  - closed-ended
  - calibration
  - frontier-knowledge
sources:
  - url: https://arxiv.org/abs/2501.14249
    title: "Humanity's Last Exam (arXiv:2501.14249)"
    accessed: "2026-09-08"
  - url: https://lastexam.ai
    title: "Humanity's Last Exam (official site)"
    accessed: "2026-09-08"
  - url: https://github.com/centerforaisafety/hle
    title: "centerforaisafety/hle (README, LICENSE)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/cais/hle
    title: "cais/hle dataset (gated access page)"
    accessed: "2026-09-08"
  - url: https://www.anthropic.com/claude-opus-4-5-system-card
    title: "System Card: Claude Opus 4.5 (Anthropic, November 2025), Section 2.16"
    accessed: "2026-09-08"
  - url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/hle
    title: "inspect_evals: hle task implementation"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice L"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Humanity's Last Exam tests whether a model can answer closed-ended academic questions at the
frontier of expert human knowledge, across dozens of subjects spanning mathematics, the humanities
and the natural sciences. Each question was written and vetted by a subject-matter expert and
filtered so that it cannot be answered quickly by searching the internet, distinguishing it from
benchmarks that mostly reward recall or lookup. About 90% of questions are text-only; the rest pair
text with a reference image.

The benchmark was built as a response to earlier knowledge benchmarks like MMLU saturating: frontier
models were clearing 90%+ on MMLU, leaving little room to distinguish further progress. HLE also asks
models to report a numeric confidence alongside each answer, so it measures calibration (whether
stated confidence tracks actual correctness) as well as raw accuracy.

## How it is scored

Models are graded on accuracy: the percentage of questions answered correctly, judged automatically
by GPT-4o against the reference answer, using a standardized prompt that structures responses into
"Reasoning" and "Final Answer" sections. Because the question set mixes free-text exact-match items
(about 80%) with multiple-choice items of varying option counts (about 20%), there is no single fixed
random baseline the way a uniform four-option test would have. A second published metric, RMS
calibration error, measures the gap between a model's stated confidence and its actual accuracy;
HLE's authors report this is uniformly poor (above 80% error) across every model they tested at
launch, indicating models answer confidently even when wrong.

## Dataset and licence

HLE launched in January 2025 with 3,000 questions contributed by nearly 1,000 expert reviewers from
over 500 institutions; later revisions to the paper describe 2,500 questions after removing contested
or flawed items. The dataset is released under CC BY 4.0 and distributed through Hugging Face
(`cais/hle`), though access there is gated behind an agreement intended to slow the dataset's entry
into future training corpora, alongside an embedded canary string. A private held-out set is kept
alongside the public release specifically to detect models that have been overfit to the public
questions. The authors separately maintain "HLE-Rolling," a continuously refreshed fork that swaps
in harder questions over time; scores on it are not comparable to the static set.

## Who publishes it

HLE was introduced by the Center for AI Safety (CAIS) and Scale AI, with an organizing team led by
Long Phan, Alice Gatti, Ziwen Han and Nathaniel Li, and senior authorship from Summer Yue, Alexandr
Wang (Scale AI) and Dan Hendrycks (CAIS). The January 2025 arXiv paper has since been revised
repeatedly (through at least a v11 in mid-2026) as the authors refine decontamination and add
evaluation detail; it was also published in Nature. CAIS runs a public dashboard tracking frontier
model performance on an ongoing basis.

## Lineage

HLE has no formal predecessor; it was created specifically because MMLU and similar knowledge
benchmarks had stopped separating frontier models. It shares that motivation with benchmarks like
GPQA Diamond, though HLE is broader in subject coverage and explicitly multi-modal. This repository
tracks one direct variant: `hle_tools`, the same question set scored when a model is given tool
access (search, browsing, code execution) rather than the untooled default this page describes.

## Saturation and contamination

Progress has been fast relative to the benchmark's age. At the January 2025 release, the strongest
model on the text-only subset (DeepSeek-R1) scored 9.4% against GPT-4o's 3.3%. By November 2025,
Anthropic's Claude Opus 4.5 System Card measured Gemini 3 at 37.5% without search — the best of six
frontier models it charted — a roughly four-fold gain in ten months. Scores remain far from any
ceiling, so HLE still separates frontier models well. Contamination risk sits at medium: the public
questions carry a canary string and a private held-out set catches overfitting, but the dataset has
circulated publicly since January 2025, and Anthropic's November 2025 system card describes actively
re-grading transcripts that appeared to retrieve answers online during search-enabled runs — direct
evidence that browsing access raises leakage risk in practice.

## How to run it

The authors' repository supplies a reference harness (`run_model_predictions.py` and
`run_judge_results.py`) built around the OpenAI Python client and a GPT-4o judge, and most published
numbers trace back to it. UK AISI's `inspect_evals` package also implements the benchmark as the `hle`
task, with options to restrict to the HLE-Verified gold subset or run the rolling variant instead of
the static set — either of which produces scores not comparable to the standard number. Judge choice,
prompt wording and tool access all affect reported scores, so compare figures across sources with
care.

## Reading the numbers

A high HLE score today mostly indicates strong closed-ended recall and reasoning across a broad
academic sweep, produced under a prompt that discourages guessing without justification. It does not
indicate open-ended research capability, and calibration error is worth reading alongside accuracy:
HLE's results show models are frequently wrong with high stated confidence. Because scores remain
well below any plausible ceiling, differences between frontier models here are currently meaningful
rather than noise. Compare a plain HLE score against `hle_tools` deliberately: the gap shows how much
of a model's apparent knowledge is retrieval it can do itself versus recall from training.
