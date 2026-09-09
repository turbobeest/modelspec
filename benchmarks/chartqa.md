---
id: chartqa
name: ChartQA
aliases:
  - "ChartQA: A Benchmark for Question Answering about Charts with Visual and Logical Reasoning"
page_kind: benchmark
category: multimodal
subcategory: chart and figure question answering
status: active
summary: Visual question answering over real-world chart images that require reading values off the chart and doing arithmetic or logical reasoning to answer.
measures: "ChartQA shows a model a chart image, drawn from real published sources, together with a natural-language question about it. The model must produce a short answer, which may require reading a value directly off the chart, comparing two or more values, or doing simple arithmetic or logical reasoning across several data points. Roughly three in ten question-answer pairs come from human annotators who wrote compositional, visually grounded questions; the rest were generated from human-written chart summaries and then checked. The task exercises visual perception of chart elements, such as axes, legends and bar heights, together with the reasoning needed to compute an answer, not just lookup."
task_format: "Visual question answering over chart images; open-vocabulary short answers (numbers, phrases, yes/no)"
metric:
  name: relaxed accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "Numeric answers are scored correct within a 5% tolerance of the gold value; non-numeric answers require an exact string match."
dataset:
  size: null
  size_note: "About 9.6K human-written question-answer pairs plus about 23.1K machine-generated from human-written chart summaries (about 32.7K total, per the paper's abstract). Exact chart-image count was not confirmed from the sources read for this page."
  url: https://huggingface.co/datasets/ahmed-masry/ChartQA
  license: GPL-3.0
  languages:
    - en
  modalities:
    - image
    - text
  splits: "train / val / test (official split shipped in the repository)"
  public_test_set: true
publisher:
  org: ""
  authors:
    - Ahmed Masry
    - Do Xuan Long
    - Jia Qing Tan
    - Shafiq Joty
    - Enamul Hoque
  url: https://github.com/vis-nlp/ChartQA
paper:
  title: "ChartQA: A Benchmark for Question Answering about Charts with Visual and Logical Reasoning"
  arxiv: "2203.10244"
  url: https://arxiv.org/abs/2203.10244
  year: 2022
leaderboard_url: ""
repo_url: https://github.com/vis-nlp/ChartQA
released: "2022"
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
  note: "Not independently verified against a primary publisher source in this research pass. This repository's own model cards show several current vision-language models reporting scores in the high 80s to mid 90s on relaxed accuracy, which would suggest the benchmark is being approached from the top, but that has not been confirmed here against a primary source."
contamination:
  risk: medium
  note: "Train and test questions and answers are fully public since 2022, and many vision-language models explicitly fine-tune on the ChartQA training split before reporting a test-split score. That is expected, standard practice for this benchmark rather than an unusual leak, but it means scores are not comparable to a zero-shot evaluation."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - multimodal
  - chart-understanding
  - visual-question-answering
  - document-understanding
sources:
  - url: https://arxiv.org/abs/2203.10244
    title: "ChartQA: A Benchmark for Question Answering about Charts with Visual and Logical Reasoning"
    accessed: "2026-09-07"
  - url: https://aclanthology.org/2022.findings-acl.177/
    title: "ChartQA (ACL Anthology)"
    accessed: "2026-09-07"
  - url: https://github.com/vis-nlp/ChartQA
    title: "vis-nlp/ChartQA (GitHub repository)"
    accessed: "2026-09-07"
  - url: https://huggingface.co/datasets/ahmed-masry/ChartQA
    title: "ChartQA dataset card (Hugging Face)"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

ChartQA shows a model a chart image, drawn from real published sources, together with a natural-language question about it. The model must give a short answer that may require reading a value directly off the chart, comparing two or more values, or carrying out simple arithmetic or logical reasoning across several data points.

It targets the gap between simple lookup questions and the compositional, visually grounded questions people actually ask about charts, which most earlier chart-QA datasets did not cover, since those relied on fixed-vocabulary answers and template-based questions.

## How it is scored

The metric is relaxed accuracy: a numeric answer counts as correct if it falls within 5% of the gold value, and a non-numeric answer must match the reference string exactly. About 9.6K of the roughly 32.7K total question-answer pairs were written directly by human annotators; the rest were generated from human-written chart summaries using a fine-tuned T5 model and then checked. Because the answer space is open-vocabulary rather than fixed, models are typically evaluated end to end rather than as multiple choice, and some reporters split scores by the human-written and machine-generated subsets rather than reporting one pooled number.

## Dataset and licence

The dataset totals roughly 9.6K human-written and 23.1K machine-generated question-answer pairs over chart images drawn from public chart-hosting sources; the GitHub repository lists Pew Research Center charts among them. Both the GitHub repository and the Hugging Face dataset card list the licence as GPL-3.0. Questions, chart images and gold answers are all public, with an official train, validation and test split; the exact total image count was not confirmed from the sources read for this page.

## Who publishes it

ChartQA was introduced by Ahmed Masry, Do Xuan Long, Jia Qing Tan, Shafiq Joty and Enamul Hoque, appearing in Findings of the Association for Computational Linguistics: ACL 2022. The vis-nlp GitHub organisation maintains the reference repository and the Hugging Face dataset mirror. There is no separately maintained leaderboard, so scores mostly appear as one line among many benchmarks in individual model or lab reports.

## Lineage

ChartQA does not sit inside a family in this repository's taxonomy and has no direct predecessor; it superseded earlier, more template-based chart-QA datasets by adding compositional and visual-reasoning questions. A harder successor, ChartQAPro, has since been published to address ceiling effects and add more diverse question types; it does not yet have a page in this repository.

## Saturation and contamination

A current ceiling was not independently confirmed against a publisher page during this research pass, so saturation status is recorded as unknown rather than asserted; this repository's own model cards suggest several current vision-language models score in the high 80s to mid 90s on relaxed accuracy, which points toward the benchmark being approached from the top, but that pattern has not been verified here against a primary source. Contamination risk is medium: the dataset, including its training split, has been fully public since 2022, and fine-tuning on the ChartQA training split before reporting a test-split score is standard, expected practice for this benchmark, not an unusual leak, but it does mean a ChartQA score is not a zero-shot measurement for models that did so.

## How to run it

The reference implementation and evaluation scripts live in vis-nlp/ChartQA, alongside separate files for the human-authored (ChartQA-H) and machine-generated (ChartQA-M) question sets and the underlying data tables behind each chart. No lm-evaluation-harness, inspect_evals, HELM, OpenCompass or BIG-bench task name could be confirmed from those projects' own documentation during this research pass. Reported numbers are hardest to compare when a reporter does not say whether they fine-tuned on the ChartQA training split, evaluated the human-written and machine-generated subsets separately or pooled, and whether they used the 5% relaxed-accuracy tolerance or exact match.

## Reading the numbers

A high ChartQA score shows a model can read values off an image accurately and chain simple arithmetic or comparisons across them, a reasonable proxy for real chart-reading tasks like reading a dashboard or a slide. It does not test chart types, question styles or reasoning depth beyond what is in the original 2022 set, so a very high score does not guarantee robustness on newer, harder chart benchmarks such as ChartQAPro. Check whether a reported number is pooled across the human and machine-generated subsets, since the two are not equally difficult, and whether the model was fine-tuned on ChartQA's own training data before being tested on it.
