---
id: charxiv_reasoning
name: "CharXiv Reasoning"
aliases:
  - "CharXiv-R"
page_kind: benchmark
category: multimodal
subcategory: "chart reasoning over scientific figures"
status: active
summary: "The reasoning half of CharXiv: one open-ended question per chart that requires combining several visual elements, not just reading a labelled value."
measures: >
  CharXiv Reasoning is the reasoning-question half of the CharXiv family: for each of 2,323 real
  charts pulled from arXiv papers, the model must answer one open-ended question that requires
  synthesising information across multiple parts of the chart -- comparing series, computing a
  derived value, cross-referencing the legend against the plotted data -- rather than reading a
  single labelled point. The benchmark's own taxonomy further splits reasoning questions into four
  answer-type categories: text-in-chart, text-in-general, number-in-chart and number-in-general,
  depending on whether the answer is text or a number and whether it is read directly off the chart
  or requires outside synthesis.
task_format: >
  Open-ended, free-text short-answer question about one chart image, one per chart, not
  multiple-choice. Models typically reason before committing to a final answer; there is no fixed
  answer template beyond what individual harnesses impose.
metric:
  name: "accuracy (GPT-4o judged)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  human_baseline: 80.5
  baseline_note: >
    80.5% is the CharXiv paper's human baseline specifically for reasoning questions (the "Overall"
    reasoning row for the Human entry on the official leaderboard), the number the paper's abstract
    highlights against GPT-4o's 47.1% at release. Descriptive questions have a separate, higher human
    baseline (92.1%); see the charxiv family page. There is no fixed random-guess baseline because
    answers are open-ended free text.
dataset:
  size: 2323
  size_note: >
    2,323 reasoning questions, one per chart: 1,000 from the validation split (questions and answers
    public) and 1,323 from the test split (answers held private "to prevent data leakage"). The public
    leaderboard and most vendor-reported scores evaluate the 1,000-question validation split only.
  url: "https://huggingface.co/datasets/princeton-nlp/CharXiv"
  license: "CC BY-SA 4.0 (QA annotations); charts retain the copyright of their original papers; code Apache-2.0"
  languages:
    - en
  modalities:
    - image
    - text
  splits: "validation (1,000 reasoning questions, public) + test (1,323 reasoning questions, answers held out)"
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
  family: charxiv
  predecessor: ""
  successors: []
  variants:
    - charxiv_reasoning_tools
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: >
    The official leaderboard's strongest reasoning entry (o3, high reasoning effort) reads 78.6%,
    close to the 80.5% human baseline, but most other evaluated models sit well below that -- the
    median of the roughly 90 tracked entries is far lower, and weak open-weight models score in the
    single digits. Anthropic's Claude Opus 4.6 system card (2026-02), evaluating on the 1,000-question
    validation split with adaptive thinking and max effort, reports 68.5% without tools and 77.4% with
    a simple image-cropping tool (see charxiv_reasoning_tools), versus 65.7% and 68.7% for Claude Opus
    4.5 in the same settings -- consistent with a benchmark where the frontier is closing in on the
    human baseline while the wider model population is not.
contamination:
  risk: medium
  note: >
    The 1,000-question validation split's questions and answers have been public since June 2024 and
    could appear in later training corpora; the 1,323-question test split's answers are held private
    specifically to blunt that risk. Almost all published reasoning scores this page found, including
    the official leaderboard and the Anthropic system card cited above, evaluate the public validation
    split rather than the held-out test split, so the benchmark's main defence against leakage is not
    the one most reporters actually rely on.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    No major third-party harness was found to carry this benchmark. The reference implementation is
    the CharXiv authors' `src/generate.py` and `src/evaluate.py` (GPT-4o judge). Vendors report their
    own numbers from their own harnesses instead: Anthropic's Claude Opus 4.6 system card, for example,
    averages five runs at a stated "adaptive thinking, max effort" setting on the validation split, a
    protocol distinct from the reference scripts, and separately reports scores with and without a
    cropping tool (see charxiv_reasoning_tools).
tags:
  - multimodal
  - chart-reasoning
  - open-ended
  - gpt-4o-judge
  - charxiv
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
  - url: "https://www-cdn.anthropic.com/6a5fa276ac68b9aeb0c8b6af5fa36326e0e166dd/Claude%20Opus%204.6%20System%20Card.pdf"
    title: "Claude Opus 4.6 System Card, section 2.19.3 CharXiv Reasoning (Anthropic, 2026-02)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice K"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

CharXiv Reasoning asks one open-ended question per chart, drawn from a real arXiv paper, that requires
combining information across several parts of the chart rather than reading one labelled value: for
example, comparing two plotted series, computing a difference between points, or cross-referencing a
legend against the axes. The benchmark's own taxonomy sorts these questions into four answer-type
categories -- text-in-chart, text-in-general, number-in-chart, number-in-general -- based on whether the
correct answer is text or a number, and whether it comes directly off the chart or needs outside
synthesis.

This is the harder of CharXiv's two question types (the other, descriptive, is not yet a separate page in
this repository); the paper's headline finding is the gap between reasoning and descriptive accuracy, and
between model and human reasoning accuracy, rather than either number in isolation.

## How it is scored

Models answer in free text; there is no fixed set of options. CharXiv grades reasoning answers with
GPT-4o acting as an automatic judge, extracting the model's final answer and assigning a binary
correct/incorrect score rather than using exact string match, since exact match would unfairly penalise
answers that are correct but differently formatted (a different notation for the same number, for
example). Because the grader is an externally hosted model, a reported score is tied to whichever GPT-4o
snapshot produced it. Vendors reporting their own numbers add further protocol choices on top of this --
Anthropic's system card, for instance, averages five runs at a specific thinking-effort setting -- so
scores from different sources reflect different harnesses, not one shared evaluation.

## Dataset and licence

2,323 reasoning questions, one per chart: 1,000 in the validation split, where both the chart and the
question-answer pair are public, and 1,323 in the test split, where the answer is kept private "to
prevent data leakage," following the same approach as MathVista and MMMU. The public leaderboard and
most vendor system cards this page found evaluate the 1,000-question validation split. Question-answer
annotations are released under CC BY-SA 4.0; the underlying chart images keep the copyright of their
original source papers.

## Who publishes it

CharXiv, and its reasoning subset, was introduced by Zirui Wang, Mengzhou Xia, Luxi He, Howard Chen,
Yitao Liu, Richard Zhu, Kaiqu Liang, Xindi Wu, Haotian Liu, Sadhika Malladi, Alexis Chevalier, Sanjeev
Arora and Danqi Chen, mostly at Princeton Language and Intelligence (PLI), Princeton University, posted
to arXiv in June 2024 and accepted at NeurIPS 2024. The authors maintain the reference repository,
dataset and public leaderboard at charxiv.github.io, which reports reasoning and descriptive scores
separately for each submitted model.

## Lineage

This page is the `charxiv` family's reasoning half; see that page for the sibling descriptive-question
half, which is not yet separately documented here. `charxiv_reasoning_tools` is a variant of this exact
benchmark scored with the model given a tool during evaluation (an image-cropping tool, in the one vendor
system card this page found); it is not part of CharXiv's own official protocol, and it is the only
variant tracked in this repository. No formal predecessor or successor benchmark exists for CharXiv
Reasoning specifically, though the parent family page discusses the earlier, simpler chart-QA benchmarks
CharXiv was built to improve on.

## Saturation and contamination

The official leaderboard's strongest reasoning entry (o3, high reasoning effort) reads 78.6%, close to
the 80.5% human baseline, but most other tracked models sit well below that, down to single digits for
the weakest open-weight entries -- the benchmark still separates models broadly even as its very top
approaches human performance. Anthropic's Claude Opus 4.6 system card (dated 2026-02), evaluating the
1,000-question validation split with adaptive thinking and max effort, reports Claude Opus 4.6 at 68.5%
without tools and 77.4% with a simple image-cropping tool, against 65.7% and 68.7% for Claude Opus 4.5 in
the same two settings. Contamination risk is medium: the validation split has been public since June
2024 and is the split most reporters actually evaluate, even though the test split's held-out answers
exist specifically to reduce that risk.

## How to run it

No major third-party harness (lm-evaluation-harness, inspect_evals, HELM, OpenCompass, BIG-bench) was
found to carry this benchmark. The CharXiv authors' own `src/generate.py` and `src/evaluate.py` scripts,
which call GPT-4o as the grader, are the reference implementation. Reported scores vary with which split
was used (validation versus test), the judge model snapshot, the vendor's own sampling and thinking-effort
settings, and whether the model had tool access during the eval (see `charxiv_reasoning_tools`) -- none
of which is standardised across reporters, so treat cross-vendor comparisons cautiously.

## Reading the numbers

A high CharXiv Reasoning score shows a model can combine several pieces of visual information from a
real scientific chart into a correct free-text answer, which is a meaningfully harder skill than reading
a single labelled value off the same chart. Because grading uses an LLM judge rather than exact match,
and because vendors run their own harnesses and sampling settings, treat a reasoning score as
directionally informative rather than precisely comparable across sources. Check specifically whether a
reported number came from the public validation split or the private test split, and whether the model
had tool access, before comparing two scores.
