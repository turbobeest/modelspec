---
id: mmmu
name: MMMU
aliases:
  - Massive Multi-discipline Multimodal Understanding
page_kind: benchmark
category: multimodal
subcategory: expert multi-discipline knowledge
status: active
summary: 11.5K college-level, image-paired exam questions across six disciplines, testing expert knowledge that requires reading a figure, chart or diagram.
measures: >
  MMMU pairs text questions with images such as charts, diagrams, maps, tables, music sheets and chemical
  structures, drawn from real college exams, quizzes and textbooks. It spans six core disciplines (Art
  and Design, Business, Science, Health and Medicine, Humanities and Social Science, and Tech and
  Engineering) across 30 subjects and 183 subfields, and 30 distinct image types. The goal is to test
  whether a model can combine expert-level subject knowledge with genuine reading of the accompanying
  image, rather than treating the image as decoration for a question answerable from text alone.
task_format: "Mostly four-option multiple-choice questions, each paired with one or more images; a smaller portion are open-ended."
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: null
  human_baseline: 88.6
  baseline_note: "Random baseline is not fixed, since option counts vary by question. The paper reports three human expert tiers from a study of 90 college seniors: best 88.6%, medium 82.6%, worst 76.2%."
dataset:
  size: 11500
  size_note: "11.5K questions total; Hugging Face lists 150 dev, 900 validation and 10,500 test examples."
  url: https://huggingface.co/datasets/MMMU/MMMU
  license: Apache-2.0
  languages:
    - English
  modalities:
    - text
    - image
  splits: "dev (150) / validation (900) / test (10,500)"
  public_test_set: true
publisher:
  org: ""
  authors:
    - Xiang Yue
    - Yuansheng Ni
    - Kai Zhang
    - Tianyu Zheng
    - Ruoqi Liu
    - Ge Zhang
    - Samuel Stevens
    - Dongfu Jiang
    - Weiming Ren
    - Yuxuan Sun
    - Cong Wei
    - Botao Yu
    - Ruibin Yuan
    - Renliang Sun
    - Ming Yin
    - Boyuan Zheng
    - Zhenzhu Yang
    - Yibo Liu
    - Wenhao Huang
    - Huan Sun
    - Yu Su
    - Wenhu Chen
  url: https://mmmu-benchmark.github.io/
paper:
  title: "MMMU: A Massive Multi-discipline Multimodal Understanding and Reasoning Benchmark for Expert AGI"
  arxiv: "2311.16502"
  url: https://arxiv.org/abs/2311.16502
  year: 2023
leaderboard_url: https://mmmu-benchmark.github.io/
repo_url: https://github.com/MMMU-Benchmark/MMMU
released: "2023-11"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors:
    - mmmu_pro
  variants: []
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: "At launch (November 2023) the strongest models scored well below the human expert ceiling (GPT-4V 56%, Gemini Ultra 59%, versus 88.6% best-expert), so the original test was not saturated. A harder successor, MMMU-Pro, was created specifically to filter out questions answerable without genuinely using the image and to raise the ceiling again, which is itself evidence that the original MMMU was starting to be gamed by text-only shortcuts on some questions; no current top score for base MMMU was confirmed from a source opened during this research."
contamination:
  risk: high
  note: "The maintainers released the test-set answers on 2026-02-12, announced on the benchmark's own site, and struck through the EvalAI submission server that previously held them back. Every score dated after that was produced against a set whose answers are public."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Official scoring for the test split runs through the EvalAI submission platform, per the benchmark's own site."
tags:
  - multimodal
  - college-level
  - multi-discipline
  - multiple-choice
  - vision-language
sources:
  - url: https://arxiv.org/abs/2311.16502
    title: "MMMU: A Massive Multi-discipline Multimodal Understanding and Reasoning Benchmark for Expert AGI"
    accessed: "2026-09-07"
  - url: https://mmmu-benchmark.github.io/
    title: "MMMU Benchmark"
    accessed: "2026-09-07"
  - url: https://huggingface.co/datasets/MMMU/MMMU
    title: "MMMU/MMMU · Datasets at Hugging Face"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice H"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MMMU tests whether a model can apply college-level subject knowledge to questions that genuinely require
reading an accompanying image, not just recognising that an image is present. Its 11.5K questions are
drawn from real college exams, quizzes and textbooks across six disciplines: Art and Design, Business,
Science, Health and Medicine, Humanities and Social Science, and Tech and Engineering, spanning 30
subjects and 183 subfields. The images themselves are unusually varied for a multimodal benchmark,
covering 30 types including charts, diagrams, maps, tables, sheet music and chemical structures, which
means a model has to bring different visual reading skills to different questions rather than one general
image-captioning ability.

## How it is scored

Most items are four-option multiple-choice questions, graded by exact match against the labelled option;
a smaller portion are open-ended. Because option counts are not perfectly uniform across every question,
there is no single fixed random baseline for the whole set. The paper establishes a human expert ceiling
by having 90 college seniors, three per subject, answer questions in their own field of study without
internet access, giving three baselines depending on which experts are counted: 88.6% best, 82.6% medium,
76.2% worst.

## Dataset and licence

The dataset was manually curated by the authors' team from college exams, quizzes, course materials and
textbooks, with what the paper describes as strict attention to copyright and licensing during
collection. It is distributed on Hugging Face under the Apache-2.0 licence, split into 150 dev, 900
validation and 10,500 test examples. Whether the test split's answers are held out from public
redistribution, with scoring instead going through the EvalAI submission platform referenced on the
benchmark's own site, was not confirmed during this research.

## Who publishes it

MMMU comes from a 22-author paper led by Xiang Yue, posted to arXiv in November 2023 and later accepted
as a CVPR 2024 oral presentation. The authors maintain the benchmark website and the `MMMU-Benchmark/MMMU`
evaluation repository on GitHub.

## Lineage

MMMU's authors and collaborators later released MMMU-Pro (id: `mmmu_pro`, no page yet in this
repository) as a harder follow-up, built by filtering out MMMU questions that turn out to be answerable
by text-only models, expanding the answer options, and adding a vision-only setting where the question
itself is embedded in the image rather than given as separate text. No predecessor benchmark or other
variant is recorded here.

## Saturation and contamination

At release, leading models were well short of the human expert ceiling: GPT-4V scored 56% and Gemini
Ultra 59%, against an 88.6% best-expert baseline, so the benchmark opened with clear headroom. That
MMMU-Pro exists at all, built specifically to close text-only shortcuts and re-widen the gap between
models, is itself a sign that base MMMU was starting to be gameable on at least some questions by the
time MMMU-Pro was built.

The leaderboard has since moved well past that ceiling: its top entry stands at 86.9 as of 1 July 2026,
above the 85.4 human-expert approximation, and nearly every entry after 2024 is marked self-reported
rather than independently verified. Contamination risk is now high for a specific, dated reason. On
12 February 2026 the maintainers released the answers for the test set and struck through the EvalAI
submission server that had previously held them back, so any score dated after that was produced
against a set whose answers are public. Treat pre-2026 and post-February-2026 numbers as different
measurements, and prefer MMMU-Pro when the question is whether a model can still be separated from
its peers.

## How to run it

The authors' `MMMU-Benchmark/MMMU` repository provides the reference evaluation code, and official
scoring on the held test split runs through EvalAI. Because vision-language models differ widely in how
they accept interleaved image-and-text prompts, and MMMU's items sometimes include more than one image
per question, prompt formatting is a plausible source of score differences between reporters beyond
underlying model quality; no specific comparability caveat beyond that was confirmed from a source opened
during this research.

## Reading the numbers

A high MMMU score suggests a model can combine subject-matter knowledge with reading genuinely
information-bearing images across a wide range of academic fields, which is a broader claim than most
single-domain multimodal benchmarks support. It does not by itself show the model uses the image on every
question, since some fraction of MMMU items are answerable from text alone, which is exactly the gap
MMMU-Pro was built to close. A score should be read alongside MMMU-Pro where available, and treated with
more caution the closer it sits to the human expert range, since headroom on the original test appears to
be narrowing for the strongest models.
