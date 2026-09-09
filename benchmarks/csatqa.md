---
id: csatqa
name: CSAT-QA
aliases:
  - "CSAT-QA(EVAL)"
page_kind: benchmark
category: domain
subcategory: "Korean College Scholastic Ability Test (CSAT) multi-subject exam questions"
status: active
summary: 187 Korean CSAT exam questions across six subjects, each with a recorded human student accuracy; GPT-4 already beat the average human score in the original 2023 evaluation.
measures: >
  csatqa is EleutherAI lm-evaluation-harness's task group for CSAT-QA, a set of multiple-choice
  questions manually collected by the HAE-RAE project from South Korea's College Scholastic Ability
  Test (CSAT, or Suneung), the standardized exam required for university admission. The harness's
  group covers six subject categories: Writing (WR), Grammar (GR), Reading Comprehension: Science
  (RCS), Reading Comprehension: Social Science (RCSS), Reading Comprehension: Humanities (RCH), and
  Literature (LI); each question presents a Korean-language passage or prompt and five numbered answer
  options. HAE-RAE separately released a larger, 936-question "full" collection of CSAT items spanning
  exams from 2007 to 2022, but that full collection is not wired into lm-evaluation-harness -- only the
  smaller, six-category subset described here, chosen because it has attached human student-accuracy
  data, is.
task_format: >
  Five-option multiple-choice question, answered zero-shot. The harness's own prompt is in Korean:
  "다음을 읽고 정답으로 알맞은 것을 고르시요" (read the following and choose the correct answer), followed by
  the context, question and five options, and the model completes "주어진 문제의 정답은" (the answer to the
  given question is) with an option number.
metric:
  name: "accuracy and length-normalized accuracy (acc, acc_norm)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 20
  human_baseline: 47.83
  baseline_note: >
    Five options give a random baseline of 20%. HAE-RAE's own release reports recorded South Korean
    student accuracy averaging 47.83% across the six categories. In the same release, GPT-4 (prompted
    directly, not through this harness) averaged 54.58% without special tokens and 54.37% with them --
    above the average human figure -- while GPT-3.5-Turbo-16K averaged 24.32-26.29% and
    Polyglot-Ko-12.8B (evaluated through lm-evaluation-harness) averaged 13.68%, below the 20% random
    baseline. The harness's own aggregate_metric_list weights each of the six subtasks by its item
    count when combining them into one score.
dataset:
  size: 187
  size_note: >
    187 questions across the six lm-evaluation-harness subtasks, confirmed by summing the live
    Hugging Face parquet row counts for each category config: GR 25, LI 37, RCH 35, RCS 37, RCSS 42,
    WR 11. HAE-RAE's own release blog post states this subset holds "188" questions -- a one-item
    discrepancy between that original description and the dataset as currently hosted, not reconciled
    by this research. A separate "full" config on the same Hugging Face repository holds all 936
    CSAT-QA questions HAE-RAE collected (2007-2022 exams, four curriculum versions), but no
    lm-evaluation-harness task reads that config; only the 187/188-question categorized subset does.
  url: "https://huggingface.co/datasets/HAERAE-HUB/csatqa"
  license: >
    Not an open licence: per the Hugging Face dataset card, "the copyright of this material belongs to
    the Korea Institute for Curriculum and Evaluation (한국교육과정평가원) and may be used for research
    purposes only."
  languages:
    - ko
  modalities:
    - text
  splits: "six category configs (GR/LI/RCH/RCS/RCSS/WR), each a single 'test' split; a separate 936-row 'full' config also exists but is not used by this harness task"
  public_test_set: true
publisher:
  org: "HAE-RAE project (open community initiative built around the Polyglot-Ko model family)"
  authors: []
  url: "https://github.com/guijinSON/hae-rae"
paper:
  title: "CSAT-QA: How Far Can LLMs Reach in Korean Language Understanding?"
  arxiv: ""
  url: "https://github.com/guijinSON/hae-rae/blob/main/blog/CSAT-QA.md"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/guijinSON/hae-rae"
released: "2023-09"
last_updated: ""
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
    The only dated result found is from the original 2023 release: GPT-4 averaged 54.58% (without
    special tokens) against a recorded average human accuracy of 47.83%, already ahead of the human
    figure at that time. No fresher published score, and no continuously updated leaderboard, was
    found during this research, so current saturation is not established.
contamination:
  risk: high
  note: >
    The underlying CSAT exams (2007-2022) were administered as real, publicly reported South Korean
    university-entrance exams before HAE-RAE compiled them into a dataset, and the compiled
    question-and-answer set, gold answers included, has been hosted on Hugging Face without gating
    since around September 2023 -- about three years by this research date.
harness:
  lm_eval: "csatqa"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    lm-evaluation-harness registers csatqa as a group of six subtasks (csatqa_gr, csatqa_li,
    csatqa_rch, csatqa_rcs, csatqa_rcss, csatqa_wr), each reading its own dataset_name config from
    HAERAE-HUB/csatqa and combined with weight_by_size aggregation over acc and acc_norm.
tags:
  - domain
  - korean
  - multiple-choice
  - exam
  - human-baseline
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/csatqa/_csatqa.yaml"
    title: "csatqa task-group definition, lm-evaluation-harness"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/csatqa/_default_csatqa_yaml"
    title: "csatqa default task config (dataset path, prompt, metrics), lm-evaluation-harness"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/csatqa/utils.py"
    title: "csatqa prompt-construction code, lm-evaluation-harness"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/HAERAE-HUB/csatqa/raw/main/README.md"
    title: "HAERAE-HUB/csatqa dataset card (subject categories, licence, results table)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=HAERAE-HUB/csatqa"
    title: "Hugging Face datasets-server per-config row counts for HAERAE-HUB/csatqa"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/guijinSON/hae-rae/main/blog/CSAT-QA.md"
    title: "CSAT-QA: How Far Can LLMs Reach in Korean Language Understanding? (HAE-RAE release blog post)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/guijinSON/hae-rae/main/README.md"
    title: "HAE-RAE project GitHub repository README"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

csatqa is EleutherAI lm-evaluation-harness's task group for CSAT-QA, a set of multiple-choice questions manually collected by the HAE-RAE project from South Korea's College Scholastic Ability Test (CSAT, or Suneung), the standardized exam required for university admission. The harness's group covers six subject categories: Writing (WR), Grammar (GR), Reading Comprehension: Science (RCS), Reading Comprehension: Social Science (RCSS), Reading Comprehension: Humanities (RCH), and Literature (LI); each question presents a Korean-language passage or prompt and five numbered answer options. HAE-RAE separately released a larger, 936-question "full" collection of CSAT items spanning exams from 2007 to 2022 across four Korean curriculum revisions, manually transcribed by the project (rather than OCR'd) to preserve quality, with archaic "Middle Korean" items excluded. That full collection is not wired into lm-evaluation-harness -- only the smaller, six-category subset described here, chosen by HAE-RAE specifically because it has recorded human student-accuracy data attached to each item, is.

## How it is scored

Every question is answered zero-shot. The harness's own prompt is written in Korean: "다음을 읽고 정답으로 알맞은 것을 고르시요" (read the following and choose the correct answer), followed by a context, a question and five numbered options, ending with "주어진 문제의 정답은" (the answer to the given question is) for the model to complete. Scoring is standard accuracy (`acc`) and length-normalized accuracy (`acc_norm`), combined across the six subtasks with `weight_by_size` aggregation, which matters here since the subtasks are very unevenly sized (11 items for Writing to 42 for Reading Comprehension: Social Science). HAE-RAE's own original release evaluated GPT-4 and GPT-3.5-Turbo-16K by direct prompting (temperature 0.01, not through this harness) and Polyglot-Ko-12.8B through lm-evaluation-harness itself; the release notes warn that comparisons across these two methods "may potentially lead to misleading interpretations."

## Dataset and licence

The six subtasks total 187 questions (GR 25, LI 37, RCH 35, RCS 37, RCSS 42, WR 11), confirmed by summing the live Hugging Face parquet row counts. HAE-RAE's own release blog post describes this subset as holding "188" questions -- a one-item discrepancy from the dataset as currently hosted, not reconciled by this research. The data is not openly licensed: the dataset card states that "the copyright of this material belongs to the Korea Institute for Curriculum and Evaluation (한국교육과정평가원) and may be used for research purposes only," since the exam questions are government-administered content, not text HAE-RAE originated. Each category is a single "test" split with no train/validation partition, and gold answers are included.

## Who publishes it

CSAT-QA comes from the HAE-RAE project, an open community initiative built around evaluating and improving the Polyglot-Ko family of Korean language models, described in its GitHub README as "a project to improve the reasoning and instruction-following abilities of Polyglot-Ko." It was released as a blog post, "CSAT-QA: How Far Can LLMs Reach in Korean Language Understanding?", rather than a peer-reviewed paper, with the dataset hosted on Hugging Face since around September 2023. No individual author byline appears on the post; the GitHub organisation behind it is HAERAE-HUB.

## Lineage

No formal predecessor or successor to CSAT-QA is documented in the sources reviewed, and no other Korean-language exam benchmark currently has a page in this repository. Within CSAT-QA itself, the "full" (936-question) and "EVAL" (187/188-question, six-category) releases are two views of the same collection rather than separate benchmarks: EVAL is a non-random subset of FULL, selected for its recorded human accuracy, and is the only one lm-evaluation-harness implements.

## Saturation and contamination

The only dated result available is from the 2023 release: GPT-4 averaged 54.58% (without special tokens) against a recorded average human accuracy of 47.83%, meaning GPT-4 already exceeded the average human test-taker at that time, while GPT-3.5-Turbo-16K (24.32-26.29%) and Polyglot-Ko-12.8B (13.68%, below the 20% random baseline) trailed well behind. No fresher published score and no continuously updated leaderboard were found, so current saturation is unknown rather than assumed from general progress since 2023. Contamination risk is high: the underlying CSAT exams were administered as real, publicly reported exams before HAE-RAE compiled them, and the compiled dataset, gold answers included, has been hosted without gating since around September 2023 -- about three years by this research date -- with source material up to nineteen years old.

## How to run it

lm-evaluation-harness registers `csatqa` as a task group over six subtasks (`csatqa_gr`, `csatqa_li`, `csatqa_rch`, `csatqa_rcs`, `csatqa_rcss`, `csatqa_wr`), each reading its own `dataset_name` configuration from `HAERAE-HUB/csatqa` and combined via `weight_by_size` aggregation over `acc` and `acc_norm`. No OpenCompass, inspect_evals, HELM or BIG-bench implementation was found. HAE-RAE's own comparison table mixes a harness-based evaluation (Polyglot-Ko) with directly-prompted proprietary models (GPT-4, GPT-3.5) under different methodology, so a harness-derived score should not be assumed directly comparable to the GPT-4/GPT-3.5 numbers in HAE-RAE's own release, even on the same questions.

## Reading the numbers

A high csatqa score suggests strong performance on real, standardized Korean-language exam material spanning grammar, literature, writing and reading comprehension, benchmarked directly against recorded human student performance -- one of relatively few benchmarks in this repository with a genuine, item-matched human baseline. Because the six subtasks are weighted by size when combined, a single aggregate score can be dominated by the larger categories (Reading Comprehension: Social Science, Literature) and obscure weaker performance on the smallest one (Writing, 11 items); check the per-category breakdown before treating one number as representative. Given the exam content's long exposure and the small item count per subtask, treat any single csatqa score as a noisy signal best read alongside other Korean-language benchmarks.
