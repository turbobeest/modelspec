---
id: bbh
name: BIG-Bench Hard
aliases:
  - BBH
page_kind: benchmark
category: reasoning
subcategory: multi-step reasoning suite
status: active
summary: A 23-task suite pulled from BIG-Bench specifically because prior language models failed to beat average human raters on them.
measures: BIG-Bench Hard bundles 23 tasks selected from the much larger BIG-Bench collection, chosen because, at the time of selection, no language model in the original BIG-Bench evaluation had outperformed the average human rater on them. The tasks span logical deduction, causal judgement, object tracking and counting, date and arithmetic reasoning, and several language-understanding puzzles such as disambiguation and sarcasm detection (snarks), so the suite is best read as a stress test of multi-step reasoning under diverse, individually simple-looking task formats rather than a single coherent skill.
task_format: A mix of multiple-choice and short free-response prompts, varying by task; most are answered directly or via chain-of-thought prompting before a final answer.
metric:
  name: accuracy (exact match), averaged across the 23 tasks
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: Tasks were selected specifically because average human-rater performance exceeded the best contemporary language model at the time BBH was created; no single averaged human-baseline number across all 23 tasks was confirmed from a source opened during this research.
dataset:
  size: 6511
  size_note: "6,511 examples across 23 tasks; most tasks have 250 examples each, with three smaller exceptions (penguins_in_a_table 146, causal_judgement 187, snarks 178)"
  url: https://github.com/suzgunmirac/BIG-Bench-Hard
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "no train/test split; each task is a single fixed evaluation set"
  public_test_set: true
publisher:
  org: Google Research
  authors:
    - Mirac Suzgun
    - Nathan Scales
    - Nathanael Scharli
    - Sebastian Gehrmann
    - Yi Tay
    - Hyung Won Chung
    - Aakanksha Chowdhery
    - Quoc V. Le
    - Ed H. Chi
    - Denny Zhou
    - Jason Wei
  url: https://github.com/suzgunmirac/BIG-Bench-Hard
paper:
  title: "Challenging BIG-Bench Tasks and Whether Chain-of-Thought Can Solve Them"
  arxiv: "2210.09261"
  url: https://arxiv.org/abs/2210.09261
  year: 2022
leaderboard_url: ""
repo_url: https://github.com/suzgunmirac/BIG-Bench-Hard
released: "2022-10"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: BBH was adopted as one of the harder replacement benchmarks in the Hugging Face Open LLM Leaderboard v2 (2024) specifically for its resistance to the saturation that had hit ARC-Challenge, HellaSwag and MMLU; no current top-score figure was confirmed from a source opened during this research, and that leaderboard has itself since been archived.
contamination:
  risk: medium
  note: All 23 task files and answers are public in the GitHub repository and widely mirrored on Hugging Face, so exposure through web-scale pretraining is plausible; no source read during this research demonstrated specific memorization.
harness:
  lm_eval: bbh
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "lm-evaluation-harness also exposes bbh_zeroshot, bbh_fewshot, bbh_cot_fewshot and bbh_cot_zeroshot variants; the bare bbh group is an alias for bbh_cot_fewshot"
tags:
  - reasoning
  - chain-of-thought
  - multi-task
  - legacy-benchmark
sources:
  - url: https://arxiv.org/abs/2210.09261
    title: "Challenging BIG-Bench Tasks and Whether Chain-of-Thought Can Solve Them"
    accessed: "2026-09-07"
  - url: https://github.com/suzgunmirac/BIG-Bench-Hard
    title: "GitHub - suzgunmirac/BIG-Bench-Hard"
    accessed: "2026-09-07"
  - url: https://github.com/suzgunmirac/BIG-Bench-Hard/blob/main/README.md
    title: BIG-Bench-Hard README
    accessed: "2026-09-07"
  - url: https://huggingface.co/datasets/maveriq/bigbenchhard
    title: maveriq/bigbenchhard dataset card
    accessed: "2026-09-07"
  - url: https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/bbh/README.md
    title: lm-evaluation-harness BBH task README
    accessed: "2026-09-07"
  - url: https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard
    title: Open LLM Leaderboard (archived) space
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

BIG-Bench Hard (BBH) is a curated subset of 23 tasks pulled out of the much larger BIG-Bench collection, selected because, when BBH was assembled, no language model evaluated on BIG-Bench had beaten the average human rater on them. The 23 tasks are individually varied: logical deduction and object tracking (following several entities through a sequence of swaps or moves), causal judgement, date and multistep arithmetic, geometric shape recognition from SVG-like path descriptions, and language tasks like disambiguating an ambiguous pronoun or spotting sarcasm. What ties them together is not a single skill but the fact that solving any of them reliably requires chaining several reasoning steps rather than pattern-matching a single fact.

Because the tasks are so heterogeneous, a single averaged BBH score is best read as a broad reasoning-robustness signal rather than a measurement of one specific capability.

## How it is scored

Each of the 23 tasks is scored by exact-match accuracy against its own fixed set of examples (250 examples for most tasks, fewer for three tasks), and the headline BBH number is the accuracy averaged across all 23. The original paper's central finding was that chain-of-thought prompting made a large difference on this suite: it let PaLM exceed average human-rater performance on 10 of the 23 tasks, and let Codex (code-davinci-002) exceed it on 17 of the 23, compared to far fewer under standard direct prompting. Because of this, whether a reported BBH score used chain-of-thought prompting, and how many few-shot examples were given, materially changes the number, and different harnesses (bbh_cot_fewshot vs bbh_zeroshot, for instance) are not directly comparable.

## Dataset and licence

BBH totals 6,511 examples spread across its 23 tasks; most tasks contribute exactly 250 examples, with three exceptions running smaller (penguins_in_a_table at 146, causal_judgement at 187, snarks at 178). There is no train/validation/test split within a task; every example exists only to be evaluated once. The GitHub repository, which holds both the task data and the code-davinci-002 outputs and chain-of-thought prompts used in the paper, is released under the MIT licence.

## Who publishes it

BBH comes from a Google Research team: Mirac Suzgun, Nathan Scales, Nathanael Scharli, Sebastian Gehrmann, Yi Tay, Hyung Won Chung, Aakanksha Chowdhery, Quoc V. Le, Ed H. Chi, Denny Zhou and Jason Wei, published as "Challenging BIG-Bench Tasks and Whether Chain-of-Thought Can Solve Them" in October 2022. The dataset and code are maintained in Suzgun's GitHub repository rather than through a dedicated hosted leaderboard.

## Lineage

BBH is a hard subset drawn from the much larger BIG-Bench collection, which is not itself a page in this repository. It does not have its own family of per-task subset pages in this repository; all 23 tasks are represented here only as the single averaged `bbh` score. BBH was later adopted as one of the harder replacement tasks (alongside `mmlu_pro`, `gpqa_diamond`, `musr`, `ifeval` and MATH Level 5) when the Hugging Face Open LLM Leaderboard moved to its v2 iteration in 2024, specifically to replace benchmarks like `arc_challenge`, `hellaswag` and the original MMLU that had become saturated.

## Saturation and contamination

BBH was picked as a v2 replacement benchmark specifically for being harder to saturate than the benchmarks it replaced, and no current ceiling figure was confirmed from a source opened during this research; the Hugging Face leaderboard that most recently tracked it at scale has itself since been archived, which limits how easy it is to check a current, broadly comparable top score. Because every task's examples and answers are public in the GitHub repository and mirrored on Hugging Face, contamination through web-scale pretraining is plausible for any model trained since 2022, though no source read here demonstrated it directly for a specific model.

## How to run it

lm-evaluation-harness exposes several BBH variants: `bbh` (an alias for `bbh_cot_fewshot`, its chain-of-thought few-shot default), plus `bbh_zeroshot`, `bbh_fewshot` and `bbh_cot_zeroshot`. Because the original paper's headline result was specifically about chain-of-thought prompting mattering a great deal on this suite, scores from a zero-shot, non-CoT run and a few-shot CoT run on the same model can differ substantially, and reports rarely state which variant they used unless the harness task name is quoted directly.

## Reading the numbers

A high BBH score suggests a model can sustain multi-step reasoning across a genuinely varied set of small puzzle-like tasks, not just one narrow skill, which makes it a reasonable broad checkpoint. Because the suite averages 23 dissimilar tasks into one number, two models with the same overall BBH score can have very different strengths and weaknesses underneath it, so a large gap on any single sub-task is worth checking directly rather than trusting the average. As with any benchmark whose data has been public for several years, treat an unusually high score with some caution absent corroboration from a fresher or held-out reasoning benchmark.
