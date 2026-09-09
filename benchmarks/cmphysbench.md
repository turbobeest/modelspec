---
id: cmphysbench
name: CMPhysBench
aliases: []
page_kind: benchmark
category: reasoning
subcategory: "graduate-level condensed matter physics calculation problems"
status: active
summary: 520 graduate-level condensed matter physics calculation problems scored by a symbolic partial-credit metric; the best model reached only 36 average SEED score and 28% accuracy.
measures: >
  CMPhysBench tests whether a model can solve graduate-level condensed matter physics calculation
  problems, a subfield of physics concerned with the collective behaviour of matter in solid and
  liquid phases (magnetism, superconductivity, semiconductors and related phenomena). Despite the
  "CM" prefix, this is a physics-subfield benchmark, not a Chinese-language one: its questions and
  prompts are in English, though the 34-author team behind it is drawn predominantly from Chinese
  institutions. The benchmark deliberately restricts itself to calculation problems, requiring the
  model to independently derive a comprehensive, multi-step solution, rather than conceptual or
  multiple-choice questions, to probe problem-solving directly rather than recall. Six topics are
  covered: four core areas (Magnetism, Superconductivity, Strongly Correlated Systems and
  Semiconductors) chosen for domain representativeness, plus two broader categories, Theoretical
  Foundations (crystallography, plasmonics, phase transitions, condensed matter field theory) and
  Others (quantum mechanics, statistical physics, electrodynamics, quantum field theory).
task_format: >
  Open-ended calculation problem; the model is prompted to act as a condensed matter physics expert,
  solve step by step using only the symbols given in the problem statement (no new symbols allowed),
  and present its final answer as a single LaTeX expression inside a \boxed{} environment.
metric:
  name: "SEED score (Scalable Expression Edit Distance, fine-grained partial credit) and a separate binary accuracy"
  direction: higher_is_better
  unit: "SEED score (partial-credit scale); accuracy %"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No random-guess or human-expert baseline is established for open-ended, multi-step calculation
    problems. The paper's own headline result: the best-performing model, Grok-4, reached only 36
    average SEED score and 28% accuracy, both described by the authors as far below what would be
    expected of a domain expert, though no specific numeric expert baseline is given.
dataset:
  size: 520
  size_note: >
    520 problems, confirmed via the Hugging Face datasets-server against the released dataset; the
    paper's own abstract instead describes the set as "more than 520," a small discrepancy between the
    abstract's rounding and the actual released row count. Each problem is a hand-curated, graduate-
    level calculation task (not mined from an existing question bank) covering the six topics
    described above.
  url: "https://huggingface.co/datasets/weidawang/CMPhysBench"
  license: "Apache-2.0 (confirmed on both the GitHub repository and the Hugging Face dataset card)"
  languages:
    - en
  modalities:
    - text
  splits: "single unsplit set of 520 items (Hugging Face 'train'); no train/validation partition"
  public_test_set: true
publisher:
  org: "Shanghai Artificial Intelligence Laboratory, with the Institute of Physics / Beijing National Laboratory for Condensed Matter Physics (Chinese Academy of Sciences), Fudan University, Tongji University and Hong Kong Polytechnic University"
  authors:
    - Weida Wang
    - Dongchen Huang
    - Jiatong Li
    - Tengchao Yang
    - Ziyang Zheng
    - Di Zhang
    - Dong Han
    - Benteng Chen
    - Binzhao Luo
    - Zhiyu Liu
    - Kunling Liu
    - Zhiyuan Gao
    - Shiqi Geng
    - Wei Ma
    - Jiaming Su
    - Xin Li
    - Shuchen Pu
    - Yuhan Shui
    - Qianjia Cheng
    - Zhihao Dou
    - Dongfei Cui
    - Changyong He
    - Jin Zeng
    - Zeke Xie
    - Mao Su
    - Dongzhan Zhou
    - Yuqiang Li
    - Wanli Ouyang
    - Yunqi Cai
    - Xi Dai
    - Shufei Zhang
    - Lei Bai
    - Jinguang Cheng
    - Zhong Fang
    - Hongming Weng
  url: "https://github.com/CMPhysBench/CMPhysBench"
paper:
  title: "CMPhysBench: A Benchmark for Evaluating Large Language Models in Condensed Matter Physics"
  arxiv: "2508.18124"
  url: "https://arxiv.org/abs/2508.18124"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/CMPhysBench/CMPhysBench"
released: "2025-08"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 28.0
  as_of: "2025-08"
  note: >
    Clearly not saturated. The paper's best-performing model, Grok-4, reached only 36 average SEED
    score and 28% accuracy, described by the authors as "a significant capability gap" relative to
    how models perform on more traditional physics benchmarks.
contamination:
  risk: medium
  note: >
    The dataset has been public on GitHub and Hugging Face under an unrestricted Apache-2.0 licence
    since around August 2025, about one year by this research date. Problems were hand-curated by the
    author team rather than copied from an existing corpus, which limits direct memorisation risk, but
    the dataset's public availability and use as an evaluation target make later exposure during
    training plausible.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "CMPhysBench-fix_prompt"
  bigbench: ""
  other: ""
tags:
  - physics
  - condensed-matter-physics
  - reasoning
  - graduate-level
  - symbolic-math
  - partial-credit
sources:
  - url: "https://arxiv.org/abs/2508.18124"
    title: "CMPhysBench: A Benchmark for Evaluating Large Language Models in Condensed Matter Physics"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2508.18124"
    title: "CMPhysBench paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/weidawang/CMPhysBench"
    title: "weidawang/CMPhysBench dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=weidawang/CMPhysBench"
    title: "Hugging Face datasets-server row count for weidawang/CMPhysBench"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/CMPhysBench/CMPhysBench"
    title: "CMPhysBench/CMPhysBench repository metadata (Apache-2.0; ICLR 2026 description)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/CMPhysBench/cmphysbench_gen.py"
    title: "OpenCompass CMPhysBench-fix_prompt dataset config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

CMPhysBench tests whether a model can solve graduate-level condensed matter physics calculation problems, a subfield of physics concerned with the collective behaviour of matter in solid and liquid phases: magnetism, superconductivity, semiconductors and related phenomena. Despite the "CM" prefix, this is a physics-subfield benchmark, not a Chinese-language one -- its questions and prompts are in English -- though the 34-author team behind it is drawn predominantly from Chinese institutions. The benchmark deliberately restricts itself to calculation problems, requiring a model to independently derive a comprehensive, multi-step solution, rather than conceptual or multiple-choice questions, to probe problem-solving directly rather than recall.

Six topics are covered: four core areas (Magnetism, Superconductivity, Strongly Correlated Systems and Semiconductors) chosen for domain representativeness, plus two broader categories, Theoretical Foundations (crystallography, plasmonics, phase transitions, condensed matter field theory) and Others (quantum mechanics, statistical physics, electrodynamics, quantum field theory), added so the benchmark also captures foundational material beyond narrow subfield expertise.

## How it is scored

Because these are open-ended, multi-step calculation problems rather than multiple-choice questions, CMPhysBench cannot rely on exact string matching. Its central contribution is the Scalable Expression Edit Distance (SEED) score, an explicit extension of an existing metric from the PHYBench benchmark (Expression Edit Distance): a model's final boxed answer and the ground truth are represented as expression trees, and an edit distance between them yields fine-grained partial credit rather than a strict binary pass/fail, so a response that is close to correct scores better than one that is far off, even if neither is exactly right. The paper also reports a separate, stricter binary accuracy figure alongside SEED. The best model at the paper's release, Grok-4, reached only 36 average SEED score and 28% accuracy -- both far from any ceiling.

## Dataset and licence

The released dataset holds exactly 520 problems, confirmed via the Hugging Face datasets-server; the paper's own abstract describes the set more loosely as "more than 520," a small discrepancy between the abstract's rounding and the actual released row count. Each problem is a graduate-level calculation task, hand-curated by the author team rather than mined from an existing question bank, covering the six topics described above. It is released under an Apache-2.0 licence, confirmed on both the GitHub repository and the Hugging Face dataset card, as a single unsplit set (Hugging Face "train") with no train/validation partition, and the correct answer is included with each item.

## Who publishes it

CMPhysBench was built by a 34-author team led by Weida Wang (Shanghai Artificial Intelligence Laboratory) and Dongchen Huang (Beijing National Laboratory for Condensed Matter Physics and Institute of Physics, Chinese Academy of Sciences), with further co-authors including Dongzhan Zhou, Yuqiang Li, Wanli Ouyang and Lei Bai, and additional institutional affiliations spanning Fudan University, Tongji University and Hong Kong Polytechnic University. It was posted to arXiv in August 2025 and accepted at ICLR 2026. The authors maintain the reference dataset and evaluation code at github.com/CMPhysBench/CMPhysBench.

## Lineage

CMPhysBench's own introduction positions it against earlier general-physics benchmarks it judges too easy or too shallow for this domain: SciQ and ScienceQA (high-school-level science QA) and, more directly, PHYBench and UGPhysics, undergraduate-level physics benchmarks that the authors say "underrepresent the most critical and frontier areas of contemporary physics research." Its SEED scoring metric is a named, explicit extension of PHYBench's own Expression Edit Distance metric, adapted to be more scalable. This repository separately documents `physics.md`, a PhD-qualifying-exam-level general-physics benchmark from an unrelated Yale/NYU team; the two are different projects by different authors that happen to both target graduate-level physics problem solving, and neither cites the other in the sources reviewed for this page, so a "PHYSICS" score and a "CMPhysBench" score should not be assumed related beyond both testing graduate-level physics.

## Saturation and contamination

CMPhysBench is clearly not saturated: the paper's own best-performing model, Grok-4, reached only 36 average SEED score and 28% accuracy, which the authors describe as "a significant capability gap" for this domain relative to how models perform on more traditional physics benchmarks. Contamination risk is assessed as medium: the dataset has been public on GitHub and Hugging Face under an unrestricted Apache-2.0 licence since around August 2025, about one year by this research date. Problems were hand-curated rather than copied from an existing corpus, which limits direct memorisation risk, but the dataset's unrestricted public availability and use as an evaluation target make later exposure during training plausible.

## How to run it

OpenCompass implements this as `CMPhysBench-fix_prompt`, loading `weidawang/CMPhysBench` and prompting the model, in character as "a condensed matter physics expert," to solve each problem step by step using only the given symbols and present its final answer inside a LaTeX `\boxed{}` environment; a dedicated `CMPhysBenchEvaluator` implements the SEED scoring logic. No lm-evaluation-harness, inspect_evals, HELM or BIG-bench implementation was found.

## Reading the numbers

A high CMPhysBench score is evidence a model can carry out genuine multi-step condensed matter physics derivations, not merely recall or pattern-match to a known formula, since these are open-ended calculation problems rather than a fixed option list. Because SEED gives partial credit while the paper's separate accuracy figure does not, check which of the two a reported score uses: a model can show meaningfully more competence on SEED than on accuracy alone, since SEED rewards getting close to the right symbolic answer, not only getting it exactly right. Given how far even the best-tested model sits from any ceiling, small score differences between models likely reflect genuine capability gaps rather than noise, and a "CMPhysBench" score should not be confused with an unrelated, same-domain "PHYSICS" figure from the different benchmark this repository documents separately.
