---
id: mmlu_physics
name: "MMLU: Physics (unresolved key)"
aliases:
  - mmlu_pro_physics
page_kind: subset
category: knowledge
status: unknown
summary: "Disputed key on 40 frontier cards: possibly a mis-keyed MMLU-Pro Physics score, possibly a classic-MMLU STEM subcategory rollup. Neither reading is confirmed; pending a card re-key."
measures: >
  Not established. This key appears on 40 frontier model cards in this repository with no notes on
  its source. It may be a mis-keyed MMLU-Pro Physics category score (MMLU-Pro has a ten-option
  Physics category; the original 57-subject MMLU has no subject or dataset config named plain
  "physics"), or it may be the "physics" STEM subcategory the original MMLU authors define in
  categories.py, which pools four classic subjects. See "What it measures" below for the evidence
  on each reading and why neither is confirmed.
task_format: >
  Not established -- it depends on which reading is correct. A ten-option, chain-of-thought format
  if this is an MMLU-Pro category score, or the classic four-option format if this is a
  categories.py subcategory rollup of four MMLU subjects.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  baseline_note: >
    random_baseline is left empty because it depends on which reading is correct: 10% under
    MMLU-Pro's ten options (reading one), or 25% under the classic four-option MMLU format
    (reading two). Do not assume either without confirming the source first.
dataset:
  size_note: >
    Not established, because the underlying dataset depends on which reading is correct. If this
    is the MMLU-Pro Physics category (reading one), it would draw on 1,299 test questions from
    TIGER-Lab/MMLU-Pro. If this is the categories.py "physics" STEM subcategory (reading two), it
    would pool astronomy (152), college physics (102), conceptual physics (235) and high school
    physics (151) test questions from cais/mmlu -- 640 combined. Neither is confirmed for this id.
  license: MIT
  languages:
    - en
  modalities:
    - text
  public_test_set: true
lineage:
  family: mmlu
harness:
  other: >
    If this is the MMLU-Pro Physics category (reading one), the matching lm-evaluation-harness task
    is mmlu_pro_physics -- see the mmlu_pro page. If this is the categories.py rollup (reading two),
    the four pooled subjects run as separate tasks (mmlu_astronomy, mmlu_college_physics,
    mmlu_conceptual_physics, mmlu_high_school_physics) with no dedicated rollup task in any harness
    checked for this page. Neither is confirmed for this id.
tags:
  - knowledge
  - multiple-choice
  - mmlu-subset
  - unresolved
sources:
  - url: "https://arxiv.org/abs/2406.01574"
    title: "MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark (Wang et al., arXiv:2406.01574)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro"
    title: "TIGER-Lab/MMLU-Pro dataset card, Hugging Face (14-category table, Physics = 1,299 questions)"
    accessed: "2026-09-08"
  - url: "https://github.com/hendrycks/test/blob/master/categories.py"
    title: "categories.py: MMLU subject-to-subcategory mapping, hendrycks/test repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/cais/mmlu"
    title: "cais/mmlu dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/splits?dataset=cais/mmlu"
    title: "cais/mmlu datasets-server splits API (full 59-config list; no config named plain \"physics\")"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=cais/mmlu"
    title: "cais/mmlu datasets-server size API (row counts for astronomy, college_physics, conceptual_physics, high_school_physics)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/mmlu_pro/mmlu_pro_physics.yaml"
    title: "lm-evaluation-harness mmlu_pro_physics task config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice N"
---

Part of the [MMLU](mmlu.md) family.

## What it measures

This id's meaning is not established. It appears on 40 frontier model cards here, pulled through
the llm-stats/intlpull enrichment with no notes, and none of the 40 carries any classic
four-option physics subject key (e.g. `mmlu_high_school_physics`). Two readings are possible.

Reading one: a mis-keyed MMLU-Pro Physics category score. MMLU-Pro has a ten-option Physics
category (1,299 questions); classic 57-subject MMLU has no config named plain "physics".
lm-evaluation-harness's own task name for that category, `mmlu_pro_physics`, is one segment from
this key, and on all 40 cards the value sits close in size to that model's `mmlu_pro` score.

Reading two: the "physics" STEM subcategory `categories.py` defines, pooling astronomy, college
physics, conceptual physics and high school physics (640 questions) -- the same rollup used here
for `mmlu_biology` and `mmlu_computer_science`. Against it: all 40 cards also separately report
`mmlu_astronomy`, which that rollup would include.

## Reading the numbers

The evidence leans toward reading one without confirming it -- the astronomy overlap is the
strongest fact against reading two, but nothing here traces the number to the upstream pull. Treat
it as unverified: do not compare it to `mmlu_pro`, the classic physics subjects, or `mmlu_biology`
/ `mmlu_computer_science` as if the grain matched, and do not fold it into a per-subject average.
It is pending a card re-key; check back before trusting this beyond a rough sense the model saw
physics questions.
