---
id: r_bench
name: "R-Bench (Reasoning Bench)"
aliases:
  - "RBench"
  - "Reasoning Bench"
page_kind: benchmark
category: reasoning
subcategory: "graduate-level multi-disciplinary reasoning (text and multimodal)"
status: active
summary: A graduate-level, English/Chinese multi-disciplinary reasoning benchmark - 1,094 text questions across 108 subjects and 665 multimodal questions across 83 subjects, calibrated for Olympiad-level difficulty.
measures: >
  R-Bench (the authors expand "R" as Reasoning) tests complex, graduate-level reasoning across many
  academic and professional disciplines rather than a single subject. It has two tracks: RBench-T,
  text-only multiple-choice questions spanning 108 subjects across 19 departments (mathematics,
  physics, biology, computer science, chemistry, and more, plus applied areas such as law, finance
  and medicine), and RBench-M, a multimodal track of 665 image-plus-text questions across 83
  subjects. Both tracks are released in parallel English and Chinese versions with the same
  questions, so cross-lingual consistency can be checked directly. Questions are calibrated for
  difficulty and subject balance and are intended to be Olympiad-level rather than textbook recall.
task_format: >
  Multiple-choice questions with up to six options (A-F); RBench-M questions additionally include
  one or more images. Models are prompted zero-shot to answer and asked to end their response with
  "ANSWER: $LETTER"; OpenCompass ships both a direct letter-extraction scorer and an
  LLM-judge scorer that compares a free-form response against the gold answer for cases where letter
  extraction is unreliable.
metric:
  name: "accuracy (top-1, single-letter answer)"
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Questions offer up to six options each, so random-guess accuracy varies by item and is not a
    single clean number; this page leaves random_baseline unset rather than approximate it. No
    human baseline is published. The OpenCompass-hosted results table (read 2026-09-08) lists
    OpenAI o1 leading the text track at 69.6% average (RBench-T English 69.0%, Chinese 70.1%) and
    the multimodal track at 53.1% average, with Gemini 2.0 Flash Thinking (68.0% text) and
    Doubao-1.5-Pro (62.7% text, 40.2% multimodal) next; GPT-4o and the Qwen2.5 family score well
    below those. These are opt-in submissions to a config-hosted table rather than a continuously
    audited leaderboard, so treat them as illustrative rather than exhaustive.
dataset:
  size: 3518
  size_note: >
    3,518 rows total across four Hugging Face configs, confirmed via the datasets-server API:
    rbench-t_en (1,094 text questions), rbench-t_zh (1,094, the same questions in Chinese),
    rbench-m_en (665 multimodal questions), rbench-m_zh (665, the same questions in Chinese). The
    paper's own figures (1,094 text questions across 108 subjects; 665 multimodal questions across
    83 subjects) match the English configs exactly, confirming the Chinese configs are parallel
    translations of the same underlying question sets rather than a separate pool.
  url: https://huggingface.co/datasets/R-Bench/R-Bench
  license: Apache 2.0
  languages:
    - en
    - zh
  modalities:
    - text
    - image
  splits: "single 'test' split per config (rbench-t_en, rbench-t_zh, rbench-m_en, rbench-m_zh); no train/validation split"
  public_test_set: true
publisher:
  org: "Tsinghua University, with Stanford University, Carnegie Mellon University, University of Pennsylvania, Tencent Hunyuan X and Fitten"
  authors:
    - Meng-Hao Guo
    - Jiajun Xu
    - Yi Zhang
    - Jiaxi Song
    - Haoyang Peng
    - Yi-Xuan Deng
    - Xinzhi Dong
    - Kiyohiro Nakayama
    - Zhengyang Geng
    - Chen Wang
    - Bolin Ni
    - Guo-Wei Yang
    - Yongming Rao
    - Houwen Peng
    - Han Hu
    - Gordon Wetzstein
    - Shi-Min Hu
  url: https://evalmodels.github.io/rbench/
paper:
  title: "R-Bench: Graduate-level Multi-disciplinary Benchmarks for LLM & MLLM Complex Reasoning Evaluation"
  arxiv: "2505.02018"
  url: https://arxiv.org/abs/2505.02018
  year: 2025
leaderboard_url: https://evalmodels.github.io/rbench/
repo_url: https://evalmodels.github.io/rbench/
released: "2025-05"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 69.6
  as_of: "2025-05"
  note: >
    Even the OpenCompass-listed leader, OpenAI o1, averages 69.6% on the text track and only 53.1%
    on the multimodal track, well short of a ceiling; the paper's own abstract highlights that "even
    the top-performing model OpenAI o1 achieves only 53.2% accuracy on our multimodal evaluation" as
    evidence the benchmark is far from saturated. No evidence of score compression at the top was
    found.
contamination:
  risk: medium
  note: >
    The dataset, including gold answers, has been fully public on Hugging Face under Apache 2.0
    since May 2025 with no held-out or rotating split described by the authors, so by this page's
    research date (September 2026) it has had over a year of public exposure. The questions are
    described as newly authored for graduate-level, Olympiad-style difficulty rather than sourced
    from pre-existing exam banks, which reduces (but does not eliminate) the chance they were already
    in earlier pretraining corpora at release time.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "R_Bench (rbench_gen, rbench_llmjudge_gen and rbench_llmjudge_rawprompt_gen configs)"
  bigbench: ""
  other: ""
tags:
  - reasoning
  - multidisciplinary
  - bilingual
  - multimodal
  - graduate-level
sources:
  - url: https://arxiv.org/abs/2505.02018
    title: "R-Bench: Graduate-level Multi-disciplinary Benchmarks for LLM & MLLM Complex Reasoning Evaluation (Guo et al., arXiv:2505.02018)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/R-Bench/R-Bench
    title: "R-Bench/R-Bench dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/R_Bench
    title: "OpenCompass R_Bench dataset configs and results table (R-Bench.md)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/MM-Hallu/R-Bench
    title: "MM-Hallu/R-Bench dataset card, Hugging Face (unrelated relationship-hallucination benchmark, name collision)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

R-Bench tests graduate-level reasoning spread across many disciplines rather than depth in one
subject -- the authors expand "R" as Reasoning. The text track, RBench-T, covers 108 subjects
across 19 departments, from abstract mathematics and physics through chemistry and biology to
applied fields like law and finance; the multimodal track, RBench-M, pairs 83 subjects' worth of
questions with images the model must read alongside the text. Both tracks ship in parallel English
and Chinese versions of the same questions, letting a reader check whether a model's reasoning
ability holds steady across languages rather than only checking overall accuracy.

The authors describe the questions as calibrated for consistent, Olympiad-level difficulty and
cross-linguistic alignment, distinguishing R-Bench from broader knowledge tests that mix easy and
hard items indiscriminately.

## How it is scored

Each question offers up to six labelled options (A-F). OpenCompass's reference configuration prompts
the model zero-shot to answer, with a system instruction requiring the response to end
"ANSWER: $LETTER," then extracts that letter for grading. A second configuration substitutes an
LLM-judge grader that compares the model's full response against the gold answer, for cases where
simple letter-extraction is unreliable (for example, when a model explains its reasoning without
emitting the exact expected format). Because option count is up to six rather than a fixed four,
random-guess accuracy is not one clean number across the dataset. Reported leaderboard figures
average over both English and Chinese items per track; a score under a bare "R-Bench" label should
be checked for whether it covers the text track, the multimodal track, or both.

## Dataset and licence

The dataset totals 3,518 released items across four configs on Hugging Face: 1,094 English text
questions (`rbench-t_en`) and their 1,094 Chinese counterparts (`rbench-t_zh`), plus 665 English
multimodal questions (`rbench-m_en`) and their 665 Chinese counterparts (`rbench-m_zh`) -- each pair
is a translation of the same underlying question set, not an independently sized pool. The data is
released under Apache 2.0. Each config ships a single `test` split with no train or validation
portion, and gold answers are included rather than held out.

## Who publishes it

R-Bench was published in May 2025 by a team led by Meng-Hao Guo and Shi-Min Hu at Tsinghua
University, with co-authors from Stanford University (Kiyohiro Nakayama, Gordon Wetzstein),
Carnegie Mellon University (Zhengyang Geng), the University of Pennsylvania (Chen Wang), and Tencent
Hunyuan X (Bolin Ni, Yongming Rao, Houwen Peng). The paper appeared at ICML 2025. The authors host
data, code and a results leaderboard at the project's own site rather than a separate GitHub code
repository.

## Lineage

R-Bench has no predecessor or successor benchmark tracked in this repository. Its short name
collides with an unrelated dataset of the same title, `MM-Hallu/R-Bench`, which benchmarks
relationship hallucinations in vision-language models (image-level and instance-level questions
about inter-object relationships) and has no connection to the reasoning benchmark this page
documents. This repository's own census data (OpenCompass's `R_Bench` harness task, which loads
`R-Bench/R-Bench` on Hugging Face) points unambiguously at the Tsinghua-led reasoning benchmark
described here, not at the hallucination dataset; a reader should confirm which "R-Bench" a given
source means before comparing scores.

## Saturation and contamination

R-Bench is open, not saturated: per the OpenCompass-hosted results table, the leading model (OpenAI
o1) averages 69.6% on the text track and only 53.1% on the multimodal track, and the paper's own
abstract stresses that even o1 manages just 53.2% on its multimodal evaluation -- clear headroom
remains, especially for multimodal reasoning. Contamination risk is medium: the full item set,
including gold answers, has been publicly downloadable under Apache 2.0 since May 2025 with no
described held-out or rotating portion, so it has accumulated over a year of public exposure by this
page's research date; the authors' claim that questions are newly authored for this benchmark (not
pulled from existing exam banks) limits, without eliminating, the risk that early copies were
already inside pretraining data at release.

## How to run it

OpenCompass carries three configuration variants under the `R_Bench` task: a direct generation
config with letter-postprocessing (`rbench_gen`), and two LLM-judge configs
(`rbench_llmjudge_gen`, `rbench_llmjudge_rawprompt_gen`) that grade free-form responses against the
gold answer using a separate judge model. No lm-evaluation-harness, inspect_evals, HELM or
BIG-bench implementation was confirmed. Because one grading path depends on an LLM judge and the
other on exact letter-format compliance, and because the dataset loads from `R-Bench/R-Bench` on
Hugging Face with separate English and Chinese configs, a reported R-Bench score should be checked
for which grading method, language, and track (text, multimodal, or both) it used before comparing
it to another.

## Reading the numbers

A high R-Bench score signals a model can apply subject-specific reasoning correctly across a wide
spread of graduate-level disciplines and hold up when the same question is asked in a second
language, which broader knowledge tests with only English, single-discipline, or lower-difficulty
items do not directly test. It does not by itself indicate multimodal competence -- the paper's own
finding that even leading models score far lower on the multimodal track than the text track shows
these are meaningfully different skills, so check which track a reported number covers. Given the
option count varies per question and two different grading paths exist (letter extraction vs. LLM
judge), compare scores only when you know both used the same scoring method and language split.
