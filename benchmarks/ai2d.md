---
id: "ai2d"
name: "AI2D (AI2 Diagrams)"
aliases: ["AI2 Diagrams", "AI2D-Test"]
page_kind: "benchmark"
category: "multimodal"
subcategory: "diagram question answering"
status: "active"
summary: "Multiple-choice question answering over labeled grade-school science diagrams, testing whether a model can connect diagram text, structure and layout to a question."
measures: "Given an annotated science diagram (for example a food web, the water cycle, or a plant cell) and a multiple-choice question about it, the model must read embedded text labels and diagrammatic relationships between parts and choose the correct answer from four options."
task_format: "Multiple-choice visual question answering: one diagram image, one question, four answer options, single best choice."
metric:
  name: "accuracy"
  direction: "higher_is_better"
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: ""
dataset:
  size: 3088
  size_note: "Standard test split (3,088 question-image pairs, four options each) used by most vision-language model evaluation harnesses, hosted as lmms-lab/ai2d on Hugging Face; the original release documents over 5,000 diagrams and 15,000 questions and answers across all splits."
  url: "https://prior.allenai.org/projects/diagram-understanding"
  license: "CC BY-SA"
  languages: ["en"]
  modalities: ["image", "text"]
  splits: "train / val / test in the original release; a 3,088-item test split is what most modern harnesses score"
  public_test_set: true
publisher:
  org: "Allen Institute for AI (AI2)"
  authors: ["Aniruddha Kembhavi", "Mike Salvato", "Eric Kolve", "Minjoon Seo", "Hannaneh Hajishirzi", "Ali Farhadi"]
  url: "https://allenai.org"
paper:
  title: "A Diagram Is Worth A Dozen Images"
  arxiv: "1603.07396"
  url: "https://arxiv.org/abs/1603.07396"
  year: 2016
leaderboard_url: ""
repo_url: ""
released: "2016"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: "watch"
  top_score: null
  as_of: ""
  note: "Third-party trackers show leading vision-language models clustering in the low-to-mid 90s (percent), with several recent releases separated by well under a point, but AI2D has no publisher-maintained leaderboard to confirm a single current ceiling."
contamination:
  risk: "medium"
  note: "The dataset and its answer keys have been fully public since 2016 and are widely mirrored (Hugging Face, AWS Open Data, Kaggle), so they plausibly appear in large web-scale pretraining corpora."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags: ["diagram-understanding", "visual-question-answering", "science"]
sources:
  - url: "https://arxiv.org/abs/1603.07396"
    title: "A Diagram Is Worth A Dozen Images"
    accessed: "2026-09-07"
  - url: "https://huggingface.co/datasets/lmms-lab/ai2d"
    title: "lmms-lab/ai2d"
    accessed: "2026-09-07"
  - url: "https://registry.opendata.aws/allenai-diagrams/"
    title: "AI2 Diagram Dataset (AI2D) - Registry of Open Data on AWS"
    accessed: "2026-09-07"
  - url: "https://prior.allenai.org/projects/diagram-understanding"
    title: "Diagram Understanding - AI2 PRIOR"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures
AI2D tests whether a model can read a labeled science diagram — the kind found in a grade-school textbook — well enough to answer a multiple-choice question about it. A model is shown a diagram image (a food web, the water cycle, a plant cell, a phase-of-the-moon chart) and a question with several answer options, and must choose the correct one. Answering usually requires reading small embedded text labels, tracing arrows and lines between diagram parts, and connecting that structure to the question, rather than just describing the picture. It is an English-language, image-plus-text task.

The dataset comes from the 2016 paper "A Diagram Is Worth A Dozen Images," which also introduced Diagram Parse Graphs (DPGs), a structured representation of a diagram's constituents and their relationships, and a DPG-based question-answering model. Most modern benchmark reporting only uses the multiple-choice QA task, not the DPG parsing task the paper also proposed.

## How it is scored
Accuracy: the percentage of questions answered with the correct option out of four. There is no partial credit and no separately weighted "hard" subset in the version most benchmark suites report. Evaluation is typically zero-shot: the model sees the diagram and question once and picks an answer, with no worked examples given. Harnesses can differ in whether they present the question and options as a text prompt alongside the raw diagram image or embed the text into the image itself, which is a known source of score differences between reporters.

## Dataset and licence
The original release documents "over 5,000 diagrams and 15,000 questions and answers," each diagram annotated with segmented diagram elements, their relationships to each other, and their relationships to the diagram canvas. The version most vision-language model papers evaluate against is a fixed test split of 3,088 question-image pairs (hosted, among other places, as lmms-lab/ai2d on Hugging Face), each with four answer choices. The dataset is released under a CC BY-SA licence. Images were collected by searching Google Images with terms drawn from grade 1-6 science textbook chapter titles, then annotated through Amazon Mechanical Turk.

## Who publishes it
AI2D was built and released by the Allen Institute for AI (AI2), authored by Aniruddha Kembhavi, Mike Salvato, Eric Kolve, Minjoon Seo, Hannaneh Hajishirzi and Ali Farhadi. It was published on arXiv as arXiv:1603.07396 in 2016. AI2 hosts the raw data and test IDs on its PRIOR project page and through the AWS Open Data registry; there is no single publisher-run leaderboard, so current standings come from whichever vision-language model technical report or third-party tracker chooses to report a score.

## Lineage
AI2D predates the current wave of instruction-tuned vision-language models and was designed alongside the DPG-parsing and diagram-QA models of its era. A related academic corpus, AI2D-RST, later added rhetorical-structure annotations to a subset of AI2D's diagrams, but it is not tracked as a separate id in this repository. AI2D itself has no tools/agentic variant in this repository.

## Saturation and contamination
AI2D has been public since 2016 and is mirrored on Hugging Face, Kaggle and AWS, so its images and answer keys are plausibly present in large web-scale pretraining corpora; contamination risk should be treated as at least medium for models trained on broad web crawls. There is no AI2-run leaderboard to check against a definitive current ceiling, but third-party trackers generally show leading vision-language models clustering in the low-to-mid 90s (percent) with a narrow spread between them, consistent with the benchmark separating models less clearly than it once did.

## How to run it
Most vision-language model evaluation harnesses that include AI2D (for example lmms-eval and VLMEvalKit) load the 3,088-question test split and score plain accuracy over the four options. Check a given harness's task definition for whether it embeds the question text into the image or passes it as a separate text prompt, since scores are not always comparable across that choice.

## Reading the numbers
A high AI2D score shows a model can align text labels with diagram structure and follow simple diagrammatic relationships — a proxy for basic scientific-diagram literacy rather than general chart or document understanding. Because the test set is small, public and years old, a top score today says less about frontier capability than it did in 2016; look at harder, more recent chart and diagram benchmarks (for example CharXiv) alongside it, and treat a near-ceiling AI2D score as a baseline expectation rather than a differentiator.
