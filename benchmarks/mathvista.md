---
id: mathvista
name: MathVista
aliases: []
page_kind: benchmark
category: math
subcategory: visual mathematical reasoning
status: active
summary: 6,141 examples testing mathematical reasoning across charts, diagrams, word problems and textbook figures, pooled from 28 existing datasets plus three new ones.
measures: >
  MathVista tests whether a model can perform mathematical reasoning that depends on understanding a
  visual context, rather than reasoning over text alone. It spans five task types: figure question
  answering (reasoning over charts and plots), geometry problem solving, math word problems set in
  images, textbook question answering, and general visual question answering with a numeric or
  quantitative answer. Underlying visual contexts include natural images, geometry diagrams, abstract
  and synthetic scenes, function plots, and puzzle-test figures, and the questions draw on seven
  reasoning types from arithmetic and algebra to logical, statistical and scientific reasoning.
task_format: >
  An image paired with a question, answered as either a multiple-choice letter or a free-form
  numerical answer (integer, one or two decimal places, or a list), in English.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 17.9
  human_baseline: 60.3
  baseline_note: >
    17.9% is the paper's own measured random-guess baseline (choosing the most frequent option or
    value by question type), not a fixed theoretical rate, since the benchmark mixes multiple-choice
    questions of varying option counts with free-form numeric and list answers. The 60.3% human
    baseline comes from Amazon Mechanical Turk annotators with a high-school diploma or higher, each
    answering five questions from the testmini subset within 20 minutes.
dataset:
  size: 6141
  size_note: >
    6,141 examples total, split into a public "testmini" subset of 1,000 (used for most reported
    leaderboard numbers and for the human baseline) and a "test" subset of the remaining 5,141, whose
    answers are not publicly released to limit contamination. The set pools 9 math-focused and 19
    general VQA datasets (31 source datasets total, 28 pre-existing) plus three datasets built for this
    paper (IQTest, FunctionQA, PaperQA); 736 examples are newly curated.
  url: https://huggingface.co/datasets/AI4Math/MathVista
  license: CC BY-SA 4.0
  languages:
    - en
    - zh
    - fa
  modalities:
    - image
    - text
  splits: "testmini (1,000, public); test (5,141, answers withheld)"
  public_test_set: true
publisher:
  org: "UCLA, University of Washington, Microsoft Research (collaboration)"
  authors:
    - Pan Lu
    - Hritik Bansal
    - Tony Xia
    - Jiacheng Liu
    - Chunyuan Li
    - Hannaneh Hajishirzi
    - Hao Cheng
    - Kai-Wei Chang
    - Michel Galley
    - Jianfeng Gao
  url: https://mathvista.github.io/
paper:
  title: "MathVista: Evaluating Mathematical Reasoning of Foundation Models in Visual Contexts"
  arxiv: "2310.02255"
  url: https://arxiv.org/abs/2310.02255
  year: 2023
leaderboard_url: https://mathvista.github.io/
repo_url: https://github.com/lupantech/MathVista
released: "2023-10"
last_updated: "2025-06"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 85.2
  as_of: "2025-06"
  note: >
    At release (October 2023), the best model was GPT-4V at 49.9%, itself 10.4 points short of the
    60.3% human baseline. The project's own leaderboard, fetched directly for this page, currently
    lists its top testmini entry as "DreamPRM (o4-mini)" at 85.2% (dated 2025-06-04, citing
    arXiv:2505.20241), well above the human baseline and with no newer entry recorded since. Top
    scores are now comfortably clear of the original human baseline, though the leaderboard's own data
    file shows no update after mid-2025, so a more recent snapshot may exist elsewhere.
contamination:
  risk: medium
  note: >
    The 1,000-example testmini subset is fully public with released answers and has been the standard
    reported split for nearly two years, making it a plausible target for training-data inclusion. The
    larger test subset (5,141 examples) has its answers withheld specifically to limit this, with
    submissions handled through an online evaluation platform, but most published leaderboard numbers
    are testmini scores rather than test scores.
harness:
  lm_eval: ""
  inspect_evals: mathvista
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    The original paper's own evaluation used a three-stage protocol (response generation, then a
    GPT-4-based answer extractor measured at over 99.5% accuracy on a 200-example pilot, then
    normalization and scoring) rather than exact string matching. UK AISI's inspect_evals
    implementation instead extracts answers with a regular expression against a fixed answer-format
    instruction, which is a real protocol difference from the paper's own GPT-4 extractor and can
    affect comparability of reported scores.
tags:
  - math
  - multimodal
  - multiple-choice
  - visual-reasoning
  - benchmark-aggregation
sources:
  - url: https://arxiv.org/abs/2310.02255
    title: "MathVista: Evaluating Mathematical Reasoning of Foundation Models in Visual Contexts (arXiv:2310.02255)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/AI4Math/MathVista
    title: "AI4Math/MathVista dataset card"
    accessed: "2026-09-08"
  - url: https://mathvista.github.io/
    title: "MathVista project page and leaderboard"
    accessed: "2026-09-08"
  - url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/mathvista
    title: "inspect_evals: mathvista task implementation"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice L"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MathVista tests mathematical reasoning that depends on understanding a visual context, rather than
reasoning over text alone. It spans five task types: figure question answering over charts and plots,
geometry problem solving, math word problems embedded in images, textbook question answering, and
general visual question answering with a quantitative answer. The underlying images range across
natural photos, geometry diagrams, abstract and synthetic scenes, function plots and puzzle-test
figures, and the questions draw on seven reasoning types from arithmetic and algebra through logical,
statistical and scientific reasoning.

The benchmark addresses a specific gap: prior work studied mathematical reasoning in text and,
separately, visual question answering, but not the intersection, even though many real-world
mathematical problems (reading a chart, working a geometry diagram, interpreting a textbook figure)
are inherently visual.

## How it is scored

Models are graded on accuracy: the fraction of examples answered correctly, either by selecting the
right multiple-choice letter or producing the correct free-form numeric value (an integer, a decimal
to one or two places, or a list). The paper's evaluation runs in three stages: the model generates a
full response, a GPT-4-based extractor pulls the short final answer from it (measured at over 99.5%
accuracy on a 200-example pilot), and the extracted answer is normalized and scored. The paper reports
a measured random-guess baseline of 17.9% (guessing the most common option or value per question type)
rather than a fixed rate, since answer format varies by question. A human baseline of 60.3% comes from
Mechanical Turk annotators with at least a high-school education, each completing five testmini
questions within 20 minutes.

## Dataset and licence

MathVista pools 6,141 examples from 31 source datasets: 9 existing math-focused QA datasets, 19
existing general VQA datasets filtered and hand-verified for mathematical content, and three datasets
built for this paper (IQTest, puzzle-figure logical reasoning; FunctionQA, algebraic reasoning over
function plots; PaperQA, scientific reasoning over academic figures), contributing 736 new examples.
The data splits into a 1,000-example "testmini" subset, sampled to match the full set's distribution
and used for most reported scores, and a 5,141-example "test" subset whose answers are withheld to
limit contamination. It is distributed on Hugging Face (`AI4Math/MathVista`) under CC BY-SA 4.0 per
that dataset card; the arXiv paper's own front matter separately states CC BY 4.0.

## Who publishes it

MathVista was introduced by Pan Lu, Hritik Bansal, Tony Xia, Jiacheng Liu, Chunyuan Li, Hannaneh
Hajishirzi, Hao Cheng, Kai-Wei Chang, Michel Galley and Jianfeng Gao, a collaboration spanning UCLA,
the University of Washington and Microsoft Research. It was posted to arXiv in October 2023 and
accepted at ICLR 2024. The authors maintain the project site and leaderboard at mathvista.github.io,
which takes result submissions by email and publishes separate testmini and test leaderboards.

## Lineage

MathVista has no single named predecessor; it is a deliberate aggregation of 28 pre-existing math and
VQA datasets plus three newly built ones, rather than an extension of any one prior benchmark. It has
no formally named successor and no variant is tracked in this repository yet, though it is frequently
cited alongside later, harder visual-math benchmarks as scores on it have risen.

## Saturation and contamination

At release, the best-performing model (GPT-4V) scored 49.9%, a 15.1-point jump over the next-best
model (Multimodal Bard) but still 10.4 points short of the 60.3% human baseline. The project's own
leaderboard, fetched directly for this page, currently lists its top testmini entry as "DreamPRM
(o4-mini)" at 85.2%, dated June 2025, well clear of the human baseline, with no newer entry recorded
in the leaderboard's own data as of this research. That trajectory — a roughly 35-point gain in about
twenty months — points toward saturation, though this leaderboard snapshot may lag the true state of
the art. Contamination risk sits at medium: the testmini subset has been fully public with released
answers for close to two years and is the split nearly everyone reports, even though a larger,
answer-withheld test subset exists to guard against this.

## How to run it

UK AISI's `inspect_evals` package implements the benchmark as the `mathvista` task over the public
`testmini` split, but scores answers with a regular-expression match against a fixed answer-format
instruction rather than the paper's own GPT-4-based answer extractor — a protocol difference that can
affect comparability, particularly for free-form numeric answers where formatting varies. No
lm-evaluation-harness, HELM, OpenCompass or BIG-bench task was confirmed for this benchmark. Because
most published numbers report testmini rather than the larger held-out test subset, and extraction
method differs between the paper's protocol and at least one third-party harness, treat scores from
different sources as only roughly comparable.

## Reading the numbers

A strong MathVista score indicates a model can combine visual perception with quantitative reasoning:
reading a value off a chart, tracking a geometric relationship, or extracting a number from a diagram
and computing with it correctly. It is a composite of five different task types, so one overall number
can hide large gaps between, say, geometry problem solving and general visual question answering — the
per-task breakdown is worth reading alongside the headline score. Given how far top scores have moved
past the human baseline, and how long testmini has circulated publicly, read a very high recent score
with some contamination caution, and check it against the harder, answer-withheld test subset where
available.
