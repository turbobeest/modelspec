---
id: phybench
name: PHYBench
aliases:
  - PHYBench
  - PhyBench
page_kind: benchmark
category: reasoning
subcategory: original text-only physics problems with symbolic answers
status: active
summary: >
  500 original text-only physics problems scored by expression-tree edit distance;
  Gemini 2.5 Pro reached 36.9% accuracy versus a 61.9% human baseline.
measures: >
  PHYBench asks a model to derive a single symbolic expression for a stated
  physical quantity from a text-only scenario. Problems span mechanics,
  electromagnetism, thermodynamics, optics, modern physics, and advanced
  physics, from high school through Physics Olympiad difficulty. Authors at
  Peking University wrote original items and filtered them so each has one
  unambiguous symbolic answer and needs no figure. The benchmark is aimed at
  physical perception and multi-step reasoning, not formula lookup.
task_format: >
  Free-response: read a physics problem, reason, and box one LaTeX expression.
  Equivalent algebraic forms count as correct. Equations and decimal
  approximations are rejected. Official metrics are binary accuracy and EED
  Score (0-100) from tree edit distance on simplified SymPy expression trees.
metric:
  name: accuracy and EED Score (Expression Edit Distance)
  direction: higher_is_better
  unit: "% accuracy; EED points 0-100"
  max_score: 100
  random_baseline: null
  human_baseline: 61.9
  baseline_note: >
    81 PKU physics students, 50 of them Chinese Physics Olympiad gold medalists,
    each sat 8 problems (559 valid sheets). Human accuracy 61.9% ± 2.1 and EED
    70.4 ± 1.8. Gemini 2.5 Pro: 36.9% accuracy, 49.5 EED. Binary accuracy has
    no chance rate for free-form expressions. EED gives 100 on exact tree match,
    60-100r when relative distance r is in (0, 0.6), and 0 when r >= 0.6.
dataset:
  size: 500
  size_note: >
    The paper and phybench-official/phybench README state 500 finalized
    problems, kept from 757 reviewed drafts. The Hub card lists three JSON
    files: 100 fully worked examples, 400 question-and-tag examples, and a
    500-question comprehensive file. datasets-server reports 1,000 rows on the
    default split, equal to 100+400+500, so that Hub figure is the stacked
    files, not 1,000 unique evaluation problems.
  url: https://huggingface.co/datasets/Eureka-Lab/PHYBench
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "single public evaluation set of 500 problems; no train split in the paper"
  public_test_set: true
publisher:
  org: "School of Physics, Peking University (with Institute for Artificial Intelligence, Peking University, and Beijing Computational Science Research Center)"
  authors:
    - Shi Qiu
    - Shaoyang Guo
    - Zhuo-Yang Song
    - Yunbo Sun
    - Zeyu Cai
    - Jiashen Wei
    - Tianyu Luo
    - Yixuan Yin
    - Haoxu Zhang
    - Yi Hu
    - Chenyang Wang
    - Chencheng Tang
    - Haoling Chang
    - Qi Liu
    - Ziheng Zhou
    - Tianyu Zhang
    - Jingtian Zhang
    - Zhangyi Liu
    - Minghao Li
    - Yuku Zhang
    - Boxuan Jing
    - Xianqi Yin
    - Yutong Ren
    - Zizhuo Fu
    - Jiaming Ji
    - Weike Wang
    - Xudong Tian
    - Anqi Lv
    - Laifu Man
    - Jianxiang Li
    - Feiyu Tao
    - Qihua Sun
    - Zhou Liang
    - Yushu Mu
    - Zhongxuan Li
    - Jing-Jun Zhang
    - Shutao Zhang
    - Xiaotian Li
    - Xingqi Xia
    - Jiawei Lin
    - Zheyu Shen
    - Jiahang Chen
    - Qiuhao Xiong
    - Binran Wang
    - Fengyuan Wang
    - Ziyang Ni
    - Bohan Zhang
    - Fan Cui
    - Changkun Shao
    - Qing-Hong Cao
    - Ming-xing Luo
    - Yaodong Yang
    - Muhan Zhang
    - Hua Xing Zhu
  url: https://www.phybench.cn/
paper:
  title: "PHYBench: Holistic Evaluation of Physical Perception and Reasoning in Large Language Models"
  arxiv: "2504.16074"
  url: https://arxiv.org/abs/2504.16074
  year: 2025
leaderboard_url: https://www.phybench.cn/leaderboard
repo_url: https://github.com/phybench-official/phybench
released: "2025-04"
last_updated: "2025-05"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 36.9
  as_of: "2025-05"
  note: >
    Paper and GitHub: Gemini 2.5 Pro at 36.9% accuracy (49.5 EED), well below
    the 61.9% human mean. The project site advertises a live leaderboard at
    phybench.cn/leaderboard; that page did not render a static table here, so
    later scores are not recorded.
contamination:
  risk: medium
  note: >
    Authors required original or hard-to-search problems and a multi-round
    expert review. The 500-item set, and at least 100 worked solutions, have
    been public on GitHub and Hugging Face since April–May 2025.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: PHYBench
  bigbench: ""
  other: >
    OpenCompass config phybench_gen.py sets abbr phybench-eed, type
    PhyBenchDataset, path opencompass/PHYBench, evaluator MathEEDEvaluator,
    zero-shot boxed LaTeX prompt. Official EED code is
    phybench-official/phybench/EED. No lm-eval, HELM, inspect_evals, or
    BIG-bench task was confirmed. Not the BIG-bench task named physics, and
    not this repository's physics.md (Yale/NYU PhD qualifying problems).
tags:
  - physics
  - symbolic
  - free-response
  - eed
  - olympiad
sources:
  - url: https://arxiv.org/abs/2504.16074
    title: "PHYBench paper abstract (arXiv:2504.16074)"
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/html/2504.16074
    title: "PHYBench paper HTML (500 items, EED, 36.9% / 61.9%)"
    accessed: "2026-09-08"
  - url: https://github.com/phybench-official/phybench
    title: "phybench-official/phybench README"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/phybench-official/phybench/main/LICENSE
    title: "PHYBench MIT licence"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/Eureka-Lab/PHYBench
    title: "Hugging Face Eureka-Lab/PHYBench card"
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/size?dataset=Eureka-Lab/PHYBench
    title: "datasets-server size (1,000-row default split; 100+400+500 Hub files)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/PHYBench/phybench_gen.py
    title: "OpenCompass phybench-eed config"
    accessed: "2026-09-08"
  - url: https://www.phybench.cn/leaderboard
    title: "PHYBench leaderboard page (JS; no static table recovered)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-018 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-018"
---

## What it measures

PHYBench gives a model a self-contained physics story and asks for one symbolic answer, such as a tension or a period, written as LaTeX. Problems are text-only and were written or adapted by Peking University physics students so they are not easy web copies. Difficulty runs from school exercises to Olympiad. The intended skills are setting up the physical situation and carrying a long derivation, not picking a formula from a list.

## How it is scored

Official reporting uses two numbers. Accuracy is 1 if the simplified expression matches the gold expression, else 0. EED Score compares SymPy trees with an extended Zhang-Shasha distance, then maps relative distance r onto 0–100 so small coefficient errors still get partial credit. OpenCompass's `phybench-eed` config uses `MathEEDEvaluator` on Hub path `opencompass/PHYBench` with a boxed-expression prompt. Binary accuracy and EED must not be mixed as if they were one scale.

## Dataset and licence

The paper keeps 500 problems after human review of 757 drafts. GitHub and Hugging Face cards say MIT. The Hub card's three JSON files (100 + 400 + 500) sum to the 1,000-row datasets-server default split; the evaluation size remains 500 unique problems. Answers are public.

## Who publishes it

A large Peking University School of Physics collaboration, with core writing from Shi Qiu, Shaoyang Guo, Zhuo-Yang Song, and colleagues, posted arXiv:2504.16074 in April 2025. Code is phybench-official/phybench; the project site is phybench.cn. Hugging Face currently hosts Eureka-Lab/PHYBench.

## Lineage

The paper argues that MATH-500, AIME, GPQA, and [olympiadbench](olympiadbench.md) are either too easy, contaminated, or weakly checked. This repository's [physics.md](physics.md) is a different PhD-qualifying set from Yale/NYU. [cmphysbench](cmphysbench.md) extends PHYBench's EED idea into SEED for condensed-matter items; it is a related metric, not a successor of this 500-item set. PHYBench is not the BIG-bench task named physics.

## Saturation and contamination

Gemini 2.5 Pro at 36.9% still sits well below the 61.9% human mean, so the set is open on the paper's own table. The live leaderboard did not render here, so later scores are unknown. Originality lowers pre-2025 leakage; the public 2025 dump raises medium risk for models trained after that.

## How to run it

Use the official EED package, or OpenCompass `PHYBench` / `phybench-eed`. Report whether the number is accuracy or EED, and which prompt and equivalent-form checker were used. No lm-eval or inspect_evals task was confirmed.

## Reading the numbers

A high EED with modest accuracy means many near-miss expressions, not solved problems. Human experts still lead the paper's models, so a mid-30s accuracy is competence, not saturation. Do not quote a PHYBench number as a [physics.md](physics.md) or [olympiadbench](olympiadbench.md) physics score. Those are different item pools and, for OlympiadBench, often different modalities.
