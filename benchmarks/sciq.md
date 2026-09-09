---
id: sciq
name: "SciQ"
aliases:
  - "SciQ dataset"
  - "Crowdsourcing Multiple Choice Science Questions"
page_kind: benchmark
category: knowledge
subcategory: "crowdsourced 4-way science exam questions (physics, chemistry, biology, earth science)"
status: active
summary: "13,679 crowdsourced 4-way science questions; lm-eval scores log-likelihood accuracy on the 1,000-item test split after prepending the support paragraph."
measures: >
  SciQ is English multiple-choice science QA. Crowd workers read a
  textbook passage from CK-12 or OpenStax and wrote a question plus a
  correct answer and three distractors, with model-suggested distractors
  as hints. Subjects include physics, chemistry, biology, and earth
  science, from elementary through intro college. The paper's
  multiple-choice protocol is the question and four options; systems may
  retrieve background. EleutherAI lm-eval instead prepends the gold
  `support` field. That is a different and easier task than Table 2.
task_format: >
  Four-way multiple choice. lm-eval task `sciq` uses output_type
  multiple_choice. doc_to_text is support (stripped) then Question and
  Answer. Choices are distractor1, distractor2, distractor3,
  correct_answer with doc_to_target index 3. Metrics acc and acc_norm.
  should_decontaminate true on support plus question. Default splits:
  train 11679, validation 1000, test 1000.
metric:
  name: "accuracy (acc and acc_norm)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: 87.8
  baseline_note: >
    Four options, so chance is 25%. Paper Table 2 (MC test, no passage):
    Humans 87.8 ± 0.045, Lucene 80.0, Aristo 77.4, AS Reader 74.1, GA
    Reader 73.8, TableILP 31.8. Those numbers are not lm-eval acc with
    the support paragraph prepended. No later public lm-eval cell was
    read for this page.
dataset:
  size: 13679
  size_note: >
    Paper and Hugging Face allenai/sciq: 13,679 questions. Splits 11,679
    / 1,000 / 1,000 (train / validation / test). datasets-server reports
    the same example counts. Most items include a support paragraph used
    when writing the question.
  url: "https://huggingface.co/datasets/allenai/sciq"
  license: "CC-BY-NC-3.0"
  languages:
    - en
  modalities:
    - text
  splits: "train 11679 / validation 1000 / test 1000"
  public_test_set: true
publisher:
  org: "Allen Institute for AI"
  authors:
    - "Johannes Welbl"
    - "Nelson F. Liu"
    - "Matt Gardner"
  url: "https://allenai.org/data/sciq"
paper:
  title: "Crowdsourcing Multiple Choice Science Questions"
  arxiv: "1707.06209"
  url: "https://aclanthology.org/W17-4413/"
  year: 2017
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/sciq"
released: "2017"
last_updated: "2024-01"
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
    Paper Table 2 (MC test): humans 87.8%, Lucene retrieval 80.0%.
    lm-eval prepends the gold support paragraph, so modern lm-eval
    numbers are not that table and were not read here. Saturation under
    lm-eval is not established from a current leaderboard.
contamination:
  risk: high
  note: >
    Public since 2017 (arXiv 1707.06209; ACL W17-4413). Hugging Face
    allenai/sciq is ungated. The paper itself uses SciQ as extra training
    data for other science exams. lm-eval sets should_decontaminate on
    support plus question. Textbook source passages are also widely
    copied.
harness:
  lm_eval: "sciq"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Hugging Face dataset allenai/sciq; lm-eval metadata.version 1.0"
tags:
  - science
  - multiple-choice
  - crowdsourcing
  - knowledge
  - lm-eval
sources:
  - url: "https://arxiv.org/abs/1707.06209"
    title: "Crowdsourcing Multiple Choice Science Questions (arXiv 1707.06209)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1707.06209"
    title: "SciQ paper HTML (13,679 items, splits, Table 2, no-passage MC protocol)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/W17-4413/"
    title: "ACL Anthology W17-4413 (NUT@EMNLP 2017)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/allenai/sciq"
    title: "Hugging Face allenai/sciq dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/allenai/sciq"
    title: "Hugging Face API (CC-BY-NC-3.0, split counts, lastModified 2024-01-04)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=allenai/sciq"
    title: "datasets-server split counts (11679/1000/1000)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/allenai/sciq/raw/main/README.md"
    title: "HF README licence CC-BY-NC-3.0 and citation"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/sciq/README.md"
    title: "lm-eval sciq README (task name sciq, paper pointer)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/sciq/sciq.yaml"
    title: "sciq.yaml (support prepended, acc/acc_norm, decontamination)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-070 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-070"
---

## What it measures

SciQ tests science fact questions in English. A model sees a four-option item about physics, chemistry, biology, or earth science. Crowd workers on Mechanical Turk wrote the questions from CK-12 and OpenStax passages. They also chose three distractors, often from model suggestions.

The paper's multiple-choice protocol gives the question and four options. Systems may retrieve background; Table 2's Lucene score is that setup. A separate "direct answer" protocol asks for a span in a passage. EleutherAI lm-eval prepends the gold `support` paragraph written with the question. An lm-eval SciQ number is therefore mostly reading that evidence span, not closed-book science.

## How it is scored

lm-eval `sciq` scores log-likelihood of each of the four choice strings after the prompt. It reports mean acc and acc_norm. Chance is 25%. The paper's Table 2 is a different setup: question and options, with retrieval allowed. Humans 87.8%, Lucene 80.0%, Aristo 77.4%. Do not treat those as lm-eval baselines.

## Dataset and licence

13,679 questions; 11,679 train, 1,000 validation, 1,000 test. Hugging Face `allenai/sciq` matches those counts. Licence on the dataset card is Creative Commons Attribution-NonCommercial 3.0. Textbook sources were themselves Creative Commons. Answers and support text are public.

## Who publishes it

Johannes Welbl, Nelson F. Liu, and Matt Gardner. The paper notes Welbl's work was done at the Allen Institute for AI. Workshop: NUT at EMNLP 2017 (ACL W17-4413). arXiv 1707.06209, 19 July 2017. Dataset card last modified 2024-01-04. lm-eval task version 1.0.

## Lineage

SciQ is a crowdsourced exam-style set, not [scienceqa](scienceqa.md) (multimodal lectures) and not [scibench](scibench.md) (college numeric problems). It is also not [arc](arc.md), though both are science multiple choice. OpenCompass dataset-index.yml has no `sciq` entry in the file opened here.

## Saturation and contamination

The 2017 multiple-choice test already had Lucene retrieval at 80.0% and humans at 87.8%. Public text since 2017 makes training-set overlap likely; lm-eval even documents a decontamination query. No current lm-eval leaderboard cell was read, so saturation is left unknown rather than guessed.

## How to run it

`lm_eval --tasks sciq` with dataset `allenai/sciq`. Default test split is 1,000 items. Compare acc versus acc_norm, and say whether support was in the prompt. A paper-style no-passage run must drop `support` from `doc_to_text`.

## Reading the numbers

A high lm-eval SciQ score mainly shows the model can use the supplied paragraph. It does not show closed-book science skill. For that, look at a no-context run or at [arc](arc.md) / [scibench](scibench.md). The CC-BY-NC-3.0 licence also blocks some commercial redistributions of the set itself.
