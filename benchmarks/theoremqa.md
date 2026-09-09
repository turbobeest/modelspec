---
id: theoremqa
name: TheoremQA
aliases:
  - Theorem QA
page_kind: benchmark
category: math
subcategory: university STEM theorem application
status: active
summary: >
  800 university-level STEM questions that require applying a named theorem,
  with answers as numbers, lists, booleans or multiple-choice letters.
measures: >
  TheoremQA tests whether a model can apply a STEM theorem, not whether it can
  do grade-school arithmetic. Domain experts wrote 800 questions over 350-odd
  theorems in mathematics, physics, electrical engineering and computer science,
  and finance. Answer forms are limited to an integer, a float, a list of
  numbers, a boolean, or a multiple-choice option so automatic grading is
  possible. 51 items also include a diagram. [MMLU-Pro](mmlu_pro.md) later reused
  some TheoremQA stems as a source of new questions; that is a different exam.
task_format: >
  English generation. OpenCompass's current 5-shot config (`TheoremQA_5shot`)
  prompts `Problem:` / `Solution:` with five worked examples and parses the
  completion with `TheoremQAEvaluatorV3`. A zero-shot CoT config asks for
  "Therefore, the answer is ..." and one of four canonical forms.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 10
  human_baseline: null
  baseline_note: >
    The paper states a random-guess baseline of 10% and reports GPT-4 at 51%
    with Program-of-Thoughts. A 20-question undergraduate spot-check is
    described but no full-set human percentage is given. OpenCompass's own
    README tables are older open-model numbers, not a live leaderboard.
dataset:
  size: 800
  size_note: >
    Paper, GitHub README and Hugging Face `TIGER-Lab/TheoremQA` all list 800
    test questions covering 350+ theorems (the paper's statistics paragraph
    says 354 theorems). 51 of the 800 include an image. The Hub split is a
    single `test` split of 800 rows with an optional `Picture` field.
  url: https://huggingface.co/datasets/TIGER-Lab/TheoremQA
  license: MIT
  languages:
    - en
  modalities:
    - text
    - image
  splits: "test (800); no train split"
  public_test_set: true
publisher:
  org: "University of Waterloo / TIGER-Lab"
  authors:
    - Wenhu Chen
    - Ming Yin
    - Max Ku
    - Pan Lu
    - Yixin Wan
    - Xueguang Ma
    - Jianyu Xu
    - Xinyi Wang
    - Tony Xia
  url: https://github.com/TIGER-AI-Lab/TheoremQA
paper:
  title: "TheoremQA: A Theorem-driven Question Answering dataset"
  arxiv: "2305.12524"
  url: https://arxiv.org/abs/2305.12524
  year: 2023
leaderboard_url: https://huggingface.co/spaces/TIGER-Lab/Science-Leaderboard
repo_url: https://github.com/TIGER-AI-Lab/TheoremQA
released: "2023-05"
last_updated: "2024-05"
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
    GPT-4 with Program-of-Thoughts reached 51% in the EMNLP 2023 paper. OpenCompass's
    bundled README later lists Mixtral-8x22B at 36.75% and Llama-3-70B-Instruct
    at 36.25% under its 5-shot config. No current top score was read from the
    Science Leaderboard space.
contamination:
  risk: medium
  note: >
    All 800 answers are public. University theorem problems are easier to leak
    than a hidden contest, but the set is smaller and more specialised than
    GSM8K. The paper's own random baseline of 10% is for guessing among
    formatted answer types, not a contamination check.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: TheoremQA
  bigbench: ""
  other: >
    OpenCompass recommended config is `TheoremQA_5shot_gen_6f0af8` (abbr
    `TheoremQA`, local `data/TheoremQA/theoremqa_test.json`). Deprecated
    configs and a zero-shot CoT file (`ThroremQA_0shot_cot_gen_8acdf7`, note
    the typo) also exist. Official scripts are in TIGER-AI-Lab/TheoremQA;
    an older GitHub path is wenhuchen/TheoremQA. No lm-evaluation-harness
    task directory was found.
tags:
  - math
  - theorems
  - stem
  - university
  - english
sources:
  - url: https://arxiv.org/abs/2305.12524
    title: TheoremQA paper (arXiv abs, EMNLP 2023)
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/html/2305.12524
    title: TheoremQA HTML full text on ar5iv
    accessed: "2026-09-08"
  - url: https://github.com/TIGER-AI-Lab/TheoremQA
    title: TIGER-AI-Lab/TheoremQA repository
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/TIGER-AI-Lab/TheoremQA/main/README.md
    title: TheoremQA GitHub README (800 QA pairs, 350+ theorems, MIT)
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/TIGER-AI-Lab/TheoremQA/main/LICENSE
    title: TheoremQA MIT LICENSE
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/TIGER-Lab/TheoremQA
    title: TIGER-Lab/TheoremQA dataset card
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/info?dataset=TIGER-Lab/TheoremQA
    title: TIGER-Lab/TheoremQA split info (800 test)
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/TheoremQA/README.md
    title: OpenCompass TheoremQA config README
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/TheoremQA/TheoremQA_5shot_gen_6f0af8.py
    title: OpenCompass TheoremQA 5-shot config
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/TheoremQA/main.py
    title: OpenCompass TheoremQADatasetV3 and evaluator
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-022 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-022"
---

## What it measures

TheoremQA is a university STEM quiz whose items are built around a named theorem. The model must apply Taylor's theorem, Huffman coding, an elasticity result, or similar, not just add and subtract. Coverage is math, physics, EE and CS, and finance. Experts wrote the questions so that a solver without the theorem should fail.

Answers are forced into a small set of types: integer, float, list, boolean, or a multiple-choice letter. Fifty-one items add a diagram. Text-only models skip that visual slice unless the image is described.

## How it is scored

Accuracy is exact match after type-aware comparison. OpenCompass's `TheoremQAEvaluatorV3` uses `compare_answer_with_groundtruth` on the cleaned prediction. The paper's headline GPT-4 number used Program-of-Thoughts, not plain chain-of-thought. OpenCompass's documented path is 5-shot ICL with local JSON.

The paper's 10% random-guess figure is the chance baseline they quote for open models that scored below 15%. It is not a four-option MCQ chance rate. A 20-item undergraduate check is mentioned; no full human score is published.

## Dataset and licence

800 test questions, 350+ theorems (354 in the statistics paragraph). Hugging Face `TIGER-Lab/TheoremQA` has one `test` split of 800 rows and MIT on the card. The GitHub LICENSE is MIT. The Hub card's usage snippet still says `wenhu/TheoremQA`; the live id is `TIGER-Lab/TheoremQA`. Answers and diagrams are public.

## Who publishes it

Wenhu Chen and co-authors at Waterloo, UCSB and UCLA. arXiv 2305.12524 appeared 21 May 2023; v3 (6 December 2023) is the EMNLP 2023 camera-ready. Hugging Face `TIGER-Lab/TheoremQA` last listed a 15 May 2024 revision. The maintained repo is TIGER-AI-Lab/TheoremQA. A Hugging Face Science Leaderboard space is linked from that README.

## Lineage

TheoremQA is harder than [GSM8K](gsm8k.md) by design and different from [MATH](math.md), which is contest problems rather than named-theorem application. [MMLU-Pro](mmlu_pro.md) used TheoremQA among other sources when writing new ten-option items; MMLU-Pro is not a TheoremQA subset. No successor page exists here.

## Saturation and contamination

GPT-4 at 51% in 2023 left the set open then. No 2026 top was sourced, so saturation is unknown. Public answers and a small specialised set make leakage possible; that is recorded as medium, not high, because the items are not the mass-market grade-school dumps.

## How to run it

Official: `python run.py --model ... --form short` in TIGER-AI-Lab/TheoremQA. OpenCompass: `--datasets TheoremQA_5shot_gen_6f0af8` with local `theoremqa_test.json`. Avoid the deprecated configs and the misspelled zero-shot filename unless you mean that exact file. Say whether Program-of-Thoughts, tools, or vision were enabled, especially for the 51 diagrams.

## Reading the numbers

A TheoremQA score is "can this model apply a textbook theorem," not GSM8K. A text-only run silently drops visual items unless the harness describes them. Compare OpenCompass 5-shot numbers only with other OpenCompass 5-shot numbers. If a paper used TheoremQA as a question source for MMLU-Pro, that is not a TheoremQA result.
