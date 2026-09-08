---
id: charxiv
name: "CharXiv"
aliases:
  - "CharXiv: Charting Gaps in Realistic Chart Understanding in Multimodal LLMs"
page_kind: family
category: multimodal
subcategory: "scientific chart understanding (descriptive and reasoning questions)"
status: active
summary: "2,323 hand-picked charts from arXiv papers, paired with descriptive and reasoning questions built to resist the score inflation seen on template-based chart benchmarks."
measures: >
  CharXiv gives a model an image of a chart pulled from a real arXiv paper and one of two kinds of
  question about it. Descriptive questions ask about basic chart elements: reading off a value,
  counting marks, extracting a label. Reasoning questions require synthesising information across
  multiple visual elements of the chart -- comparing series, working out a trend, cross-referencing
  the legend against the axes -- rather than reading a single labelled point. Every chart and
  question was handpicked and verified by a human, specifically to avoid the simplified, homogeneous,
  template-generated charts the authors argue inflate scores on earlier chart-QA benchmarks.
task_format: >
  Open-ended, free-text short-answer questions about a chart image (not multiple-choice). One
  reasoning question and four descriptive questions are written per chart. Models answer in natural
  language; there is no fixed answer template.
metric:
  name: "accuracy (GPT-4o judged)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  human_baseline: 80.5
  baseline_note: >
    80.5% is the paper's human baseline on reasoning questions specifically, the number the abstract
    foregrounds against GPT-4o's 47.1% at release. Descriptive questions have a separate, higher human
    baseline (92.1% overall on the official leaderboard); the two question types are not on one scale.
    There is no fixed random-guess baseline because answers are open-ended free text, not a choice
    among fixed options.
dataset:
  size: 2323
  size_note: >
    2,323 charts in total: a 1,000-chart validation split with publicly released question-answer pairs,
    and a 1,323-chart test split whose answers the authors keep private "to prevent data leakage," the
    same approach as MathVista and MMMU. Each chart carries 4 descriptive questions (9,292 total) and 1
    reasoning question (2,323 total), for 11,615 questions overall. The public leaderboard scores models
    on the 1,000-chart validation split only (5,000 questions).
  url: "https://huggingface.co/datasets/princeton-nlp/CharXiv"
  license: "CC BY-SA 4.0 (QA annotations); charts retain the copyright of their original papers; code Apache-2.0"
  languages:
    - en
  modalities:
    - image
    - text
  splits: "validation (1,000 charts, answers public) + test (1,323 charts, answers held out)"
  public_test_set: false
publisher:
  org: "Princeton Language and Intelligence (PLI), Princeton University"
  authors:
    - "Zirui Wang"
    - "Mengzhou Xia"
    - "Luxi He"
    - "Howard Chen"
    - "Yitao Liu"
    - "Richard Zhu"
    - "Kaiqu Liang"
    - "Xindi Wu"
    - "Haotian Liu"
    - "Sadhika Malladi"
    - "Alexis Chevalier"
    - "Sanjeev Arora"
    - "Danqi Chen"
  url: "https://github.com/princeton-nlp/CharXiv"
paper:
  title: "CharXiv: Charting Gaps in Realistic Chart Understanding in Multimodal LLMs"
  arxiv: "2406.18521"
  url: "https://arxiv.org/abs/2406.18521"
  year: 2024
leaderboard_url: "https://charxiv.github.io/"
repo_url: "https://github.com/princeton-nlp/CharXiv"
released: "2024-06"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - charxiv_reasoning
    - charxiv_reasoning_tools
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: >
    The two question types sit at different points on the saturation curve, which is why this family
    page does not pin a single top score -- see charxiv_reasoning for the reasoning-specific number.
    Descriptive questions are close to ceiling for strong models (mid-to-high 80s to 90%, against a
    92.1% human baseline). Reasoning questions still separate models by a wide margin: the official
    leaderboard's strongest entry (o3, high reasoning effort) reads 78.6%, near the 80.5% human
    baseline, while most other evaluated models sit far lower, down to single digits for the weakest.
contamination:
  risk: medium
  note: >
    Charts are drawn from arXiv papers published between January 2020 and September 2023, which were
    already public before the benchmark existed. The 1,000-chart validation split's questions and
    answers are openly released and have circulated since June 2024, so some leakage into later
    training data is plausible for that split specifically. The 1,323-chart test split's answers are
    kept private for this reason, but most vendor-reported scores (including the official leaderboard
    and the Anthropic system card citation on this page) evaluate the public validation split, not the
    held-out test split.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    No major third-party harness (lm-evaluation-harness, inspect_evals, HELM, OpenCompass, BIG-bench)
    was found to carry CharXiv as of this research. The authors' own `src/generate.py` and
    `src/evaluate.py` scripts in the GitHub repository are the reference implementation; evaluate.py
    calls GPT-4o as an automatic grader, so reproducing a published score requires access to that judge
    model and its behaviour can drift as OpenAI updates it.
tags:
  - multimodal
  - chart-understanding
  - scientific-figures
  - vision-language
  - open-ended
  - gpt-4o-judge
sources:
  - url: "https://arxiv.org/abs/2406.18521"
    title: "CharXiv: Charting Gaps in Realistic Chart Understanding in Multimodal LLMs (Wang et al., arXiv:2406.18521)"
    accessed: "2026-09-08"
  - url: "https://github.com/princeton-nlp/CharXiv"
    title: "princeton-nlp/CharXiv GitHub repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/princeton-nlp/CharXiv"
    title: "princeton-nlp/CharXiv dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://charxiv.github.io/"
    title: "CharXiv project page and leaderboard"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice K"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

CharXiv shows a model a chart image taken from a real arXiv paper and asks either a descriptive or a
reasoning question about it. Descriptive questions probe basic chart elements: reading a value off an
axis, counting marked points, pulling out a label. Reasoning questions require combining information
across several visual elements of the same chart -- comparing two series, computing a difference,
cross-referencing a legend against plotted data -- rather than reading a single labelled point.

The benchmark exists because the authors found that earlier chart-understanding datasets (subsets of
DVQA, FigureQA and ChartQA) use simplified, template-generated charts and questions that let models
score well without genuinely reading the chart. CharXiv's charts are real figures from papers, and every
chart and question was handpicked, curated and verified by a human expert rather than templated.

## How it is scored

Answers are open-ended free text rather than a choice among fixed options, so CharXiv does not use exact
string matching. The authors instead use GPT-4o as an automatic judge: it extracts the model's final
answer and assigns a binary correct/incorrect score, chosen to tolerate notational variation (Greek
letters, different ways of writing the same number) that exact match would penalise unfairly. Scores are
reported separately for reasoning and descriptive questions and are not combined into one number;
reasoning is further broken into four answer-type categories and descriptive into five. Because grading
depends on a specific, externally hosted judge model, a score is tied to whichever GPT-4o snapshot
graded it and is not perfectly reproducible over time.

## Dataset and licence

The full set is 2,323 charts, split into a 1,000-chart validation set (questions and answers fully
public) and a 1,323-chart test set (answers held private, "to prevent data leakage," following the same
approach as MathVista and MMMU). Each chart has one reasoning question and four descriptive questions,
for 2,323 reasoning and 9,292 descriptive questions in total; the public leaderboard scores models on
the 1,000-chart validation split's 5,000 questions. The QA annotations are released under CC BY-SA 4.0
and the evaluation code under Apache-2.0; the chart images themselves keep the copyright of their
original source papers, since CharXiv does not claim ownership of figures it did not create.

## Who publishes it

CharXiv was introduced by Zirui Wang, Mengzhou Xia, Luxi He, Howard Chen, Yitao Liu, Richard Zhu, Kaiqu
Liang, Xindi Wu, Haotian Liu, Sadhika Malladi, Alexis Chevalier, Sanjeev Arora and Danqi Chen, mostly at
Princeton Language and Intelligence (PLI), Princeton University, with co-authors at the University of
Wisconsin-Madison and the University of Hong Kong. The paper was posted to arXiv in June 2024 and
accepted at NeurIPS 2024. The authors maintain the reference repository, dataset and a public leaderboard
at charxiv.github.io.

## Lineage

CharXiv has no formal predecessor or successor of its own, but the paper positions itself explicitly
against earlier chart-QA benchmarks -- DVQA, FigureQA and subsets of ChartQA used inside MathVista --
showing that models which do well on those benchmarks fail consistently on CharXiv's reasoning
questions. Two subtypes of the benchmark exist as separate pages in this repository: `charxiv_reasoning`
(the reasoning-question half, `lineage.family: charxiv`) and `charxiv_reasoning_tools` (the same
questions scored with the model given a tool, currently documented only for the reasoning half). The
descriptive-question half does not yet have its own page here.

## Saturation and contamination

Descriptive and reasoning questions sit at different points on the saturation curve. Descriptive
questions are close to ceiling for capable models, scoring in the high 80s to low 90s against a 92.1%
human baseline. Reasoning questions still separate models by a wide margin: the official leaderboard's
strongest entry (o3, high reasoning effort) reads 78.6%, close to the 80.5% human baseline, while most
other evaluated models score far lower, down to single digits at the bottom of the table. Contamination
risk is medium: the validation split's questions and answers have been public since June 2024 and could
appear in later training data, while the test split's held-out answers exist to blunt that risk, though
most published scores evaluate the public validation split rather than the private test split.

## How to run it

No major third-party evaluation harness was found to carry CharXiv. The authors' own repository ships
`src/generate.py` to produce model responses and `src/evaluate.py` to grade them via a GPT-4o judge call,
plus `src/get_stats.py` to aggregate scores into the category breakdown used on the leaderboard. Because
grading depends on an externally hosted judge model rather than a fixed rubric, and because vendors
report scores from their own harnesses (different thinking-effort settings, sampling counts, and
sometimes added tool access -- see `charxiv_reasoning_tools`) rather than the reference scripts, scores
from different sources are not guaranteed to be directly comparable.

## Reading the numbers

A strong CharXiv descriptive score mostly shows a model can read a chart's stated values and labels
accurately; a strong reasoning score is the more informative one, since it requires combining several
pieces of visual information rather than retrieving one. Because the two are graded and reported
separately, do not average them into a single "CharXiv score." Check which question type, which split
(validation or test) and whether tool access was allowed before comparing two reported numbers, and
prefer the reasoning subtype's own page for saturation detail, since it is the harder and more actively
tracked half of the benchmark.
