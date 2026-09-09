---
id: compassbench_20_v1_1
name: "CompassBench v1.1"
aliases:
  - "CompassBench 2.0 v1.1"
  - "compassbench_20_v1_1"
page_kind: benchmark
category: composite
subcategory: "OpenCompass's own composite evaluation aggregating six category groups -- language, knowledge, reasoning, mathematics, code, and agent/tool-use -- each itself a naive average across several pre-existing and self-built datasets"
status: unknown
summary: "OpenCompass's own composite: naive-averages six category scores (language, knowledge, reasoning, math, code, agent), each itself an average across many pre-existing and self-built datasets."
measures: >
  CompassBench v1.1 is not a single skill test; it is OpenCompass's own composite evaluation
  aggregating six category groups, established directly from its dataset and summarizer
  configurations in the opencompass GitHub repository: language (intention recognition, sentiment
  analysis, translation, content criticism, content summarization, and Chinese cultural/semantic
  understanding, mostly paired English/Chinese tasks), knowledge (a WikiBench-derived Chinese
  single-choice split across common knowledge, humanities, natural science and social science, plus an
  English TriviaQA-style cloze set), reasoning (ReasonBench, circular multiple-choice items covering
  abductive, deductive, inductive and commonsense reasoning in English and Chinese, several machine-
  translated from BBH, LogiQA and OCNLI), mathematics (MathBench, arithmetic through college-level
  problems in English and Chinese), code (HumanEval, HumanEval+, MBPP, HumanEval-X, LCBench2023 and
  TACO, spanning multiple languages and three difficulty tiers), and agent/tool-use (CIBench, a code-
  interpreter task, and T-Eval/plugin_eval, a tool-planning evaluation). Each category score is itself
  a naive average across its constituent datasets, and the suite's own top-level "average" is a naive
  average of the six category scores -- three layers of averaging stand between any single reported
  number and one underlying task, which is why this page's category field is `composite` rather than
  any single skill.
task_format: >
  Overwhelmingly multiple choice with a few generation tasks: most sub-datasets are graded with
  OpenCompass's `CircularEvaluator`, which permutes a multiple-choice item's answer options across
  several passes and only credits the model if every permutation is answered correctly (`perf_circular`
  or `perf_4` for four-option items), reported alongside plain single-pass accuracy (`acc_origin` /
  `acc_1`). Free-text tasks use task-appropriate metrics: BLEU for translation (against FLORES-style
  references), ROUGE for summarization, and functional test execution (pass@1 / pass@k) for the code
  category's HumanEval-, MBPP- and TACO-derived tasks. Knowledge and math use 4-shot in-context
  prompting; most other categories are zero-shot.
metric:
  name: "top-level 'average' -- a naive average of six category-level naive averages (language, knowledge, reasoning, math, code, agent), each itself averaging several differently-scored constituent datasets (circular-eval accuracy, BLEU, ROUGE, pass@1) -- not one measurement"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No official leaderboard table for this exact configuration could be read for this page (the
    CompassRank site's results load through client-side scripts this page's tools could not execute),
    so no headline top_score is recorded. Because the top-level score blends circular-eval accuracy
    percentages with BLEU and ROUGE figures that are not calibrated to the same 0-100 scale in the same
    way, the practical ceiling of the blended "average" is not a clean 100 even though every individual
    accuracy-type component tops out there; read the per-category and per-dataset numbers rather than
    the single blended average when precision matters.
dataset:
  size_note: >
    No single item count is published for the composite as a whole, and this page did not download
    and count every constituent file, so `size` is left empty rather than estimated. What is
    established directly from the dataset configuration files: the code category alone spans at least
    seven constituent test sets (HumanEval-CN, HumanEval+, MBPP-CN, sanitized MBPP, HumanEval-X across
    five programming languages, LCBench2023 at three difficulty levels in English and Chinese, and TACO
    at five difficulty levels); the knowledge category spans four Chinese WikiBench splits plus one
    English cloze set; the reasoning category spans 13 named circular-MCQ subsets across English and
    Chinese; and the math category spans arithmetic through college level in both languages. Several
    constituent datasets (HumanEval, MBPP, TACO, LogiQA, OCNLI, TriviaQA, BBH) are pre-existing public
    benchmarks repackaged into this composite rather than newly authored for it.
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/compassbench_20_v1_1"
  license: ""
  languages:
    - en
    - zh
  modalities:
    - text
    - code
  splits: "single evaluation set per constituent dataset; no train/validation split documented in the configs read for this page"
  public_test_set: null
publisher:
  org: "OpenCompass (Shanghai AI Laboratory)"
  authors: []
  url: "https://github.com/open-compass/opencompass"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://rank.opencompass.org.cn/home"
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/compassbench_20_v1_1"
released: ""
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors:
    - compassbench_v1_3
  variants:
    - compassbench_20_v1_1_public
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    OpenCompass's own CompassRank leaderboard is the natural place to read current standing, but its
    results table loads through client-side JavaScript that this page's tools could not render, so no
    top score could be confirmed from it. No other source read for this page reported a cross-model
    score table for this exact id. Saturation is left unknown rather than guessed.
contamination:
  risk: medium
  note: >
    Risk is genuinely mixed across the composite rather than one answer. Several constituent datasets
    are long-public, widely reused benchmarks (HumanEval, MBPP, TriviaQA, LogiQA, OCNLI, BBH) with
    documented contamination concerns of their own, independent of CompassBench. OpenCompass appears to
    treat this id's own item set as more guarded than its sibling: the code this page's evidence is
    drawn from reads test data for `compassbench_20_v1_1` from a directory separate from, and not
    labelled, "public" (`data/compassbench_v1.1/`, versus `data/compassbench_v1.1.public/` for the
    sibling id), and the public sibling's config measurably restricts three code datasets to their
    first five test cases rather than the full set -- consistent with OpenCompass holding back part of
    this id's full item set specifically to protect leaderboard integrity, though this page did not
    verify how the non-public data directory is itself distributed or access-controlled.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "compassbench_20_v1_1 (opencompass/configs/datasets/compassbench_20_v1_1/{agent,code,knowledge,language,math,reason}; aggregated by opencompass/configs/summarizers/compassbench_v1_1_objective.py)"
  bigbench: ""
  other: ""
tags:
  - composite
  - opencompass
  - compassbench
  - chinese
  - bilingual
  - agent
  - code
  - reasoning
  - circular-evaluation
sources:
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/compassbench_20_v1_1"
    title: "opencompass configs/datasets/compassbench_20_v1_1 (agent, code, knowledge, language, math, reason subdirectories)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/summarizers/compassbench_v1_1_objective.py"
    title: "compassbench_v1_1_objective.py summarizer (defines the six category groups and the top-level average)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/compassbench_20_v1_1/code/compassbench_v1_1_code_gen_986f01.py"
    title: "compassbench_v1_1_code_gen_986f01.py (HumanEval-CN, HumanEval+, MBPP variants, HumanEval-X, LCBench2023, TACO)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/compassbench_20_v1_1/knowledge/compassbench_v1_knowledge_gen_bd74e0.py"
    title: "compassbench_v1_knowledge_gen_bd74e0.py (WikiBench splits and TriviaQA-style cloze)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/compassbench_20_v1_1/reason/compassbench_v1_reason_gen_d26d08.py"
    title: "compassbench_v1_reason_gen_d26d08.py (ReasonBench circular-MCQ subsets)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/compassbench_20_v1_1/language/compassbench_v1_language_gen_7aa06d.py"
    title: "compassbench_v1_language_gen_7aa06d.py (intention recognition, sentiment, translation, critic, summarization, cultural/semantic understanding)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/releases/tag/v0.2.1"
    title: "opencompass v0.2.1 release notes (references \"CompassBench-2024-Q1\", January 2024)"
    accessed: "2026-09-08"
  - url: "https://rank.opencompass.org.cn/home"
    title: "CompassRank leaderboard home (results table did not render for this page's tools)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

CompassBench v1.1 is OpenCompass's own composite evaluation, not a single benchmark measuring one skill. Established directly from its dataset and summarizer configuration files, it aggregates six category groups: language (intention recognition, sentiment analysis, translation, content criticism, summarization, and Chinese cultural/semantic understanding), knowledge (a Chinese WikiBench-derived split across four domains, plus an English cloze set), reasoning (ReasonBench, abductive/deductive/inductive/commonsense items in English and Chinese), mathematics (MathBench, arithmetic through college level), code (HumanEval, HumanEval+, MBPP, HumanEval-X, LCBench2023 and TACO), and agent/tool-use (CIBench, a code-interpreter task, and T-Eval, a tool-planning evaluation). Several components are pre-existing public benchmarks folded into the composite rather than newly written for it; others (WikiBench, ReasonBench, MathBench, CIBench) are OpenCompass's own constructions. Because each category score is itself a naive average across multiple constituent datasets, and the suite's headline "average" is a naive average of the six category scores, a single CompassBench v1.1 number describes roughly a dozen underlying test sets rather than one task.

## How it is scored

Most sub-datasets are multiple choice, scored with OpenCompass's circular evaluation: the same item is presented with its answer options in every rotation, and the model is credited only if it answers every rotation correctly (`perf_circular`, or `perf_4` for four-option items), a stricter and position-bias-resistant alternative to the single-pass accuracy figure (`acc_origin`) the configs also record. Free-text categories use task-specific metrics instead: BLEU for translation, ROUGE for summarization, and pass@1 (functional test execution) for the code category. Knowledge and math use 4-shot prompting; most other categories are zero-shot. The published summarizer fixes the exact aggregation: each category above naive-averages its constituent datasets (for example, code naive-averages its seven HumanEval/MBPP/HumanEval-X/LCBench/TACO variants), and the top-level "average" then naive-averages the six resulting category figures.

## Dataset and licence

No single item count is published for the composite, and this page did not download and count every constituent file, so dataset size is left unrecorded here (see the `size_note` in the front matter for the per-category breakdown that is directly confirmed). Licensing is not one answer: the opencompass repository itself is Apache-2.0, but the composite repackages several pre-existing datasets (HumanEval, MBPP, TACO, LogiQA, OCNLI, TriviaQA, BBH-derived items) each under their own original terms, alongside OpenCompass's own self-built items whose specific licence is not separately published in the configs this page read. No single dataset licence is recorded in the front matter as a result. Content is bilingual, English and Chinese, text and code.

## Who publishes it

CompassBench is published by OpenCompass, the evaluation platform maintained principally by Shanghai AI Laboratory, as part of its CompassRank leaderboard project. No dedicated academic paper documents CompassBench specifically; OpenCompass's own citation (a 2023 GitHub-hosted `misc` entry, "OpenCompass: A Universal Evaluation Platform for Foundation Models") covers the platform generally, not this composite, so this page leaves `paper` and `publisher.authors` empty rather than attribute CompassBench to that citation. OpenCompass's release notes reference "CompassBench-2024-Q1" as of January 2024, indicating a earlier, unversioned generation this page does not separately catalogue.

## Lineage

This id sits in a versioned CompassBench line inside the opencompass repository: filenames show the knowledge, language and reasoning configs carry an unbumped `_v1_` version tag while the math and code configs carry `_v1_1_`, indicating v1.1 updated math and code over an earlier "v1" generation (plausibly the "CompassBench-2024-Q1" release named in OpenCompass's own v0.2.1 release notes) while carrying knowledge, language and reasoning forward unchanged; that earlier generation is not separately catalogued in this repository. `compassbench_20_v1_1_public` is a same-structure, reduced-item variant of this id, catalogued here as its subset: its configuration reads from a directory not labelled "public" for this id (`data/compassbench_v1.1/`, versus `data/compassbench_v1.1.public/` for the sibling), and the public sibling measurably restricts three code datasets to five test cases each rather than the full set -- consistent with OpenCompass holding back part of this id's data to protect leaderboard integrity, though this page did not verify the access mechanism for the non-public directory itself. `compassbench_v1_3` is the next dated release in the same project, but the evidence does not support treating it as a superset of this benchmark: it drops language and reasoning as standalone categories, narrows math to college-level and arithmetic only, and rebuilds knowledge around a different, per-domain wiki split -- so this page records it as a successor id rather than claiming score comparability between the two. No arXiv paper or model card in this repository was found referencing this id.

## Saturation and contamination

OpenCompass's own CompassRank leaderboard would be the natural source for current standing, but its results table loads through client-side scripts this page's tools could not render, so no top score or saturation reading could be confirmed; this page records both as unknown rather than guessed. Contamination risk is mixed: several constituent datasets (HumanEval, MBPP, TriviaQA, LogiQA, OCNLI, BBH) are long-public benchmarks with contamination concerns independent of CompassBench, while this id's own item set appears more guarded than its public sibling, consistent with OpenCompass holding back part of this id's data to protect leaderboard integrity (see Lineage and the public sibling's own page for the evidence).

## How to run it

The reference implementation is the opencompass repository's own dataset configs under `configs/datasets/compassbench_20_v1_1/{agent,code,knowledge,language,math,reason}`, run through the OpenCompass evaluation framework and aggregated by `configs/summarizers/compassbench_v1_1_objective.py`, which defines every category grouping and the top-level average exactly. No other harness (lm-evaluation-harness, HELM, BIG-bench, inspect_evals) was confirmed to implement this composite. Because the suite blends zero-shot and 4-shot tasks, circular and single-pass multiple choice, and generation metrics under one aggregation formula, reproducing a published number exactly requires matching OpenCompass's own prompt templates and shot counts per category, not just running "CompassBench" generically.

## Reading the numbers

Treat the top-level "average" as a coarse summary of roughly a dozen underlying test sets, not a single skill measurement -- a change in the blended number can come from any one of six very different category areas, and the code and agent categories in particular weight heavily toward capabilities (functional code execution, tool planning) that language, knowledge and reasoning scores do not touch. Prefer the per-category and, where precision matters, per-dataset numbers the summarizer also reports (for example `code_cn` versus `code_en`, or a single ReasonBench subset) over the blended average. Because several constituent datasets are well-known public benchmarks, a very high score on this composite may partly reflect exposure to those specific items rather than general capability, and because CompassBench v1.3 restructured rather than extended this version's category set, scores on the two are not directly comparable.
