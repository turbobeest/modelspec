---
id: physics
name: "PHYSICS (Benchmarking Foundation Models on University-Level Physics Problem Solving)"
aliases:
  - "PHYSICS Benchmark"
page_kind: benchmark
category: reasoning
subcategory: "PhD-qualifying-exam-level physics problem solving across six subfields"
status: active
summary: "1,297 PhD-qualifying-exam physics problems across six subfields, needing multi-step derivation; the best model in the 2025 paper solved only 59.9% of the test set."
measures: >
  This page documents the "physics" hint that resolves to OpenCompass's `PHYSICS` dataset: Feng et
  al.'s 2025 benchmark of graduate, PhD-qualifying-exam-level physics problems. The name collides
  with an unrelated BIG-bench task also called "physics" -- a much smaller, high-school-level,
  multiple-choice task asking a model only to identify the correct formula for a word problem,
  authored by two individual contributors as part of BIG-bench's 2021-2022 crowdsourced task
  collection. This page is about the former; see Lineage for the latter. Feng et al.'s PHYSICS
  requires solving expert-annotated problems across six subfields -- classical mechanics, quantum
  mechanics, thermodynamics and statistical mechanics, electromagnetism, atomic physics, and optics
  -- each demanding multi-step mathematical derivation and reasoning to a final answer, not formula
  selection or fact recall. About 23% of problems include an accompanying figure.
task_format: >
  Open-ended, free-response problem solving: the model works step by step and gives its final
  answer in LaTeX boxed format. Some problems bundle several sub-questions that must each be
  answered in order. Scoring combines SymPy-based symbolic equivalence checking with an LLM-based
  (originally GPT-4o) natural-language answer validator, since physics answers can be correct while
  differing in algebraic form.
metric:
  name: "accuracy (SymPy symbolic equivalence plus LLM-judged answer validation)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  baseline_note: >
    There is no random-guess baseline for open-ended, multi-step problem solving. The original
    paper's own top-scoring model, o3-mini, reached 59.9% accuracy on the 1,000-question test split
    (55.0% on the 297-question validation split); the weakest evaluated open-source models scored
    below 2%.
dataset:
  size: 1297
  size_note: >
    1,297 expert-annotated problems, confirmed from the paper's own statistics table: split 297
    validation / 1,000 test, with 298 of the 1,297 (about 23%) including a figure and therefore
    multimodal, and 523 flagged by the paper's annotators as a harder "HARD" subset against 774
    regular problems. Subject-area counts: 242 electromagnetism, 240 statistical/thermodynamic
    physics, 236 quantum mechanics, 221 classical mechanics, 200 atomic physics, and 158 optics.
    OpenCompass's own configuration reads a text-only subset (`*_dataset_textonly`, one file per
    subject) that excludes the figure-based items; this page could not independently confirm the
    exact row count of that specific text-only mirror.
  url: "https://github.com/yale-nlp/PHYSICS"
  license: "MIT, stated explicitly in the repository's README and confirmed via the GitHub API"
  languages:
    - en
  modalities:
    - text
    - image
  splits: "297 validation / 1,000 test; 523 of the 1,297 flagged as a harder subset by the paper's own difficulty annotation"
  public_test_set: true
publisher:
  org: "Yale University and New York University"
  authors:
    - "Kaiyue Feng"
    - "Yilun Zhao"
    - "Yixin Liu"
    - "Tianyu Yang"
    - "Chen Zhao"
    - "John Sous"
    - "Arman Cohan"
  url: "https://github.com/yale-nlp/PHYSICS"
paper:
  title: "PHYSICS: Benchmarking Foundation Models on University-Level Physics Problem Solving"
  arxiv: "2503.21821"
  url: "https://arxiv.org/abs/2503.21821"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/yale-nlp/PHYSICS"
released: "2025-03"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 59.9
  as_of: "2025-03"
  note: >
    Not saturated. The paper's own leaderboard-style results table spans from near 0% (several
    smaller open-source models scored 1% or below) up to 59.9% for the best model, o3-mini, with a
    wide, roughly continuous spread in between across 33 evaluated models (5 proprietary, 28
    open-source). The paper's own comparison table positions PHYSICS as harder, by these accuracy
    figures, than several contemporaries such as SciBench and GPQA at the time of its release.
contamination:
  risk: medium
  note: >
    The full problem set, including test-split answers, has been downloadable from the GitHub
    repository without gating or a canary string since the March 2025 release, roughly a year and a
    half of exposure by this research date. The paper's own validation/test split was designed, in
    the authors' words, so the test portion is "reserved for standard evaluation to prevent data
    contamination" relative to researchers who might fine-tune on the validation set -- an
    internal-split safeguard against a specific reuse pattern, not a defence against the whole
    public dataset eventually appearing in a future pretraining crawl.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "PHYSICS (six subject configs: atomic_dataset_textonly, electro_dataset_textonly, mechanics_dataset_textonly, optics_dataset_textonly, quantum_dataset_textonly, statistics_dataset_textonly; LLM-judge evaluation)"
  bigbench: ""
  other: ""
tags:
  - physics
  - reasoning
  - graduate-level
  - multi-step
  - llm-judge
sources:
  - url: "https://arxiv.org/abs/2503.21821"
    title: "PHYSICS: Benchmarking Foundation Models on University-Level Physics Problem Solving"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2503.21821"
    title: "PHYSICS paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/yale-nlp/PHYSICS"
    title: "yale-nlp/PHYSICS GitHub repository"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/PHYSICS/PHYSICS_llm_judge_gen_a133a2.py"
    title: "OpenCompass PHYSICS_llm_judge_gen_a133a2.py dataset config"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/datasets/physics.py"
    title: "OpenCompass PHYSICSDataset loader"
    accessed: "2026-09-08"
  - url: "https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/physics"
    title: "BIG-bench physics task (unrelated, same-named task; see Lineage)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

This id is ambiguous in this repository's own census hints, which point to two genuinely different, unrelated benchmarks that happen to share almost the same name (see Lineage). This page documents the substantial one: OpenCompass's `PHYSICS` dataset, from Feng et al.'s 2025 paper "PHYSICS: Benchmarking Foundation Models on University-Level Physics Problem Solving." It gives a model an expert-annotated, graduate or PhD-qualifying-exam-level physics problem from one of six subfields -- classical mechanics, quantum mechanics, thermodynamics and statistical mechanics, electromagnetism, atomic physics, and optics -- and requires a multi-step derivation to a final answer, not formula selection or single-fact recall. About 23% of problems include an accompanying figure.

## How it is scored

Because problems require open-ended, multi-step reasoning rather than selecting from fixed options, scoring combines SymPy-based symbolic equivalence checking (to catch algebraically equivalent but differently formatted answers) with an LLM-based natural-language answer validator, originally GPT-4o, and a weighted scheme that accounts for correctness and problem complexity. Some problems bundle multiple sub-questions, each graded and required to be correct for full credit on that problem. The paper's own top model, o3-mini, reached 59.9% accuracy on the 1,000-question test split; the weakest of the 33 evaluated models scored below 2%, and OpenCompass's own configuration reuses essentially the same LLM-judge grading approach.

## Dataset and licence

PHYSICS totals 1,297 expert-annotated problems sourced from publicly available PhD-qualifying exam materials, split 297 for validation and 1,000 for test. Of the 1,297, 298 (about 23%) include a figure and are therefore multimodal; the paper's own difficulty annotation flags 523 as a harder "HARD" subset against 774 regular ones, and subject-area counts range from 158 (optics) to 242 (electromagnetism). The GitHub repository states an MIT licence explicitly, confirmed independently through the GitHub API. OpenCompass reads a text-only subset (one file per subject, excluding figure-based items); this page could not independently confirm that mirror's exact row count.

## Who publishes it

PHYSICS comes from Kaiyue Feng (New York University), and Yilun Zhao, Yixin Liu, Tianyu Yang, Chen Zhao, John Sous and Arman Cohan (Yale University), posted to arXiv in March 2025. The authors maintain the reference dataset and evaluation code at `github.com/yale-nlp/PHYSICS`, including the raw per-subject problem files and both a rule-based (SymPy) and model-based offline evaluation pipeline.

## Lineage

This id collides with an unrelated BIG-bench task of the same name, which this repository's own `big_bench.md` family page does not separately enumerate: BIG-bench's "physics" is a 229-item, high-school-level, multiple-choice task asking only which formula would solve a word problem, authored by two individual contributors around 2021-2022 with a GPT-2 baseline near random chance. It shares nothing with the graduate-level, free-response benchmark this page documents beyond the word "physics"; a score on one says nothing about the other. Within its own space, the PHYSICS paper positions itself against GPQA, SciBench, OlympiadBench, JEEBench and HARDMath as comparison points, none of which are tracked as a formal predecessor or successor here.

## Saturation and contamination

PHYSICS is not saturated: the paper's own results span from near 0% up to 59.9% for its best model, o3-mini, across 33 evaluated proprietary and open-source models, a wide and roughly continuous spread rather than a cluster near a ceiling. Contamination risk is medium: the full problem set, test-split answers included, has been downloadable from GitHub without gating since March 2025, about a year and a half of exposure by this research date. The paper's validation/test split was designed, in the authors' own words, to give researchers who want to fine-tune or develop against the benchmark a portion to use freely while reserving the test split "to prevent data contamination" from that specific reuse pattern -- a narrower safeguard than protection against the whole public dataset eventually entering a future pretraining crawl.

## How to run it

OpenCompass implements this as the `PHYSICS` dataset family, with one configuration per subfield (`atomic_dataset_textonly`, `electro_dataset_textonly`, `mechanics_dataset_textonly`, `optics_dataset_textonly`, `quantum_dataset_textonly`, `statistics_dataset_textonly`), each prompted for step-by-step reasoning with a boxed final answer and graded with an LLM-judge (`GenericLLMEvaluator`) against the gold answer. The paper's own repository ships a separate, non-OpenCompass pipeline combining SymPy symbolic checking with GPT-4o-based validation, plus a step-level evaluator that finds the first incorrect reasoning step. No lm-evaluation-harness, HELM, inspect_evals or BIG-bench implementation was confirmed for this benchmark -- do not confuse a `bigbench` "physics" score with an OpenCompass `PHYSICS` score; they are different tasks (see Lineage).

## Reading the numbers

A high PHYSICS score indicates a model can carry out the kind of multi-step, symbolic physics reasoning expected of a graduate student preparing for a qualifying exam, across a genuinely broad set of subfields -- meaningfully harder evidence of quantitative reasoning than a multiple-choice science benchmark, since there is no option list to narrow down from. Because grading blends symbolic equivalence checking with an LLM judge, a reported score depends partly on which judge model was used and how leniently it accepts differently phrased but equivalent answers, so scores from different judge setups are not automatically comparable. Given the wide spread between the best and weakest models in the original paper, a mid-range score reflects genuine partial competence rather than measurement noise, and the paper's HARD/regular problem split is worth checking separately, since a model's aggregate score can hide much lower performance on the harder half.
