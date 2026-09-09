---
id: squad_completion
name: "SQuAD completion (Based / lm-eval)"
aliases:
  - "based-squad"
  - "hazyresearch/based-squad"
page_kind: benchmark
category: reasoning
subcategory: "SQuAD passages rewritten so the gold span is the last tokens of a statement"
status: unknown
summary: "Based and lm-eval rewrite 2,984 SQuAD validation items as next-token completions, scored by case-insensitive contains."
measures: >
  squad_completion is a recall-style reading task, not span extraction and not SQuAD 2.0
  abstention. A passage is followed by a statement that ends with the answer. The model must
  continue the statement so the generation contains that gold span. Hazy Research built the
  items for the BASED paper by asking GPT-4 to rewrite question-answer pairs as statements
  that end with the answer, then dropping rewrites that failed that check. English text.
  Zero-shot generation.
task_format: >
  generate_until: prompt is doc["text"] with surrounding whitespace stripped; gold is
  doc["value"] stripped. Decoding stops at a newline, max_gen_toks 48. Metric is contains:
  case-insensitive regex search of the gold string inside the continuation. lm-eval VERSION 1.
metric:
  name: contains
  direction: higher_is_better
  unit: ""
  max_score: 1
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The BASED evaluation paragraph reports accuracy as the fraction of prompts whose
    generation contains the gold value. One results table header still labels the SQUAD
    column F1. The harness comment on aggregation still says "Exact match"; the implemented
    metric is substring contains, not official SQuAD EM/F1. No human or random baseline
    is given for this rewrite.
dataset:
  size: 2984
  size_note: >
    Hugging Face hazyresearch/based-squad validation split has 2,984 rows (datasets-server
    and the dataset card agree). The BASED paper says GPT-4 reformatted 5,000 SQuAD
    validation questions and discarded about 40% that did not end with the answer, leaving
    2,984 next-token items. There is no train or test split on the Hub card.
  url: "https://huggingface.co/datasets/hazyresearch/based-squad"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "validation 2,984 only"
  public_test_set: true
publisher:
  org: "Hazy Research (Stanford); EleutherAI lm-evaluation-harness"
  authors:
    - "Simran Arora"
    - "Sabri Eyuboglu"
    - "Michael Zhang"
    - "Aman Timalsina"
    - "Silas Alberti"
    - "Dylan Zinsley"
    - "James Zou"
    - "Atri Rudra"
    - "Christopher Ré"
  url: "https://huggingface.co/datasets/hazyresearch/based-squad"
paper:
  title: "Simple linear attention language models balance the recall-throughput tradeoff"
  arxiv: "2402.18668"
  url: "https://arxiv.org/abs/2402.18668"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/squad_completion"
released: "2024-02"
last_updated: "2026-06-22"
lineage:
  family: ""
  predecessor: squad
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No current leaderboard was opened for this id. The BASED paper tables mix this SQuAD
    completion accuracy with SWDE and FDA recall tasks; a standalone dated top score for
    the 2,984-item lm-eval task was not read.
contamination:
  risk: medium
  note: >
    Underlying SQuAD passages and answers have been public since 2016. The GPT-4 rewritten
    statements were released on Hugging Face on 2024-03-12 as hazyresearch/based-squad.
    The Hub card does not state a licence. Gold values are in the public validation file.
harness:
  lm_eval: "squad_completion"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    ConfigurableTask SQUADCompletion; DATASET_PATH hazyresearch/based-squad; VERSION 1 after
    lm-eval PR 3795 (2026-06-22), which strips prompt and target whitespace. v1 contains
    scores are not comparable to v0.
tags:
  - reading-comprehension
  - recall
  - completion
  - squad
  - lm-eval
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/squad_completion/README.md"
    title: "lm-eval squad_completion README (Based paper, task name, v1 changelog 2026-06-22)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/squad_completion/task.py"
    title: "SQUADCompletion task.py (hazyresearch/based-squad, contains metric, VERSION 1)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/squad_completion/squad_completion.yaml"
    title: "squad_completion.yaml (task: squad_completion)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/hazyresearch/based-squad"
    title: "hazyresearch/based-squad dataset card (2,984 validation rows; no licence field)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/hazyresearch/based-squad"
    title: "Hugging Face API record (split size 2984, created 2024-03-12)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=hazyresearch/based-squad"
    title: "datasets-server size for hazyresearch/based-squad (2984 rows)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2402.18668"
    title: "BASED paper abstract (arXiv 2402.18668, submitted 2024-02-28)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2402.18668"
    title: "BASED paper HTML (5,000 SQuAD validation items filtered to 2,984 statements)"
    accessed: "2026-09-08"
  - url: "https://github.com/HazyResearch/based-evaluation-harness"
    title: "BASED evaluation-harness homepage linked from the lm-eval README"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/rows?dataset=hazyresearch/based-squad&config=default&split=validation&offset=0&length=3"
    title: "datasets-server first validation rows (Super Bowl 50 context; not on the Hub README card)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-015 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-015"
---

## What it measures

squad_completion is a next-token recall task built from SQuAD, not the original span-extraction protocol on [SQuAD](squad.md). The model sees a Wikipedia passage plus a statement that is supposed to end with the answer, and it must generate a continuation that contains that gold span. The BASED authors used GPT-4 to turn question-answer pairs into statements that finish with the answer, then dropped rewrites that failed that check. The paper's example and the first Hugging Face validation rows use Super Bowl 50 passages from SQuAD 1.1. The Hub README card itself has no examples. The lm-eval README still cites the SQuAD 2.0 paper, so which SQuAD release was sampled is not cleanly named. English only. Zero-shot.

## How it is scored

lm-eval class `SQUADCompletion` issues `generate_until` with stop at a newline and `max_gen_toks` 48. The score is `contains`: a case-insensitive regex search for the stripped gold `value` inside the continuation, averaged with `np.mean`. The BASED paper's evaluation paragraph calls this accuracy, the fraction of prompts whose generation contains the value. One paper table header still labels the SQUAD column F1. It is not official SQuAD exact match or token F1. Version 1 (lm-eval PR 3795, 2026-06-22) strips whitespace on prompt and target; v0 scores are not comparable.

## Dataset and licence

`hazyresearch/based-squad` has a single validation split of 2,984 rows. The API, datasets-server, and card all report that count. Fields are `doc_id`, `text`, `value`, `title`, `context`, and `question`. The paper says 5,000 SQuAD validation questions were rewritten and about 40% discarded. The Hub card does not state a licence, so `license` is left empty. Upstream SQuAD is CC BY-SA 4.0; that tag is not repeated on this card. Answers are public.

## Who publishes it

Hazy Research (Simran Arora and co-authors) introduced the rewrite in "Simple linear attention language models balance the recall-throughput tradeoff" (arXiv 2402.18668, 28 February 2024; v2 7 March 2025). The Hugging Face dump is dated 12 March 2024. EleutherAI hosts the runnable task in lm-evaluation-harness as `squad_completion`. The README points at `HazyResearch/based-evaluation-harness` as the original implementation homepage. There is no separate public leaderboard for this id.

## Lineage

This id is not an alias of [squad.md](squad.md). SQuAD scores span EM/F1, often on SQuAD 2.0 with an unanswerable option. This task scores substring contains on rewritten statements. Predecessor in this repository is [squad](squad.md). It is also not [squad_shifts](squad_shifts.md), which is a BIG-bench wrap of Miller et al.'s out-of-domain SQuAD copies. No successor page was found.

## Saturation and contamination

No dated top score for the 2,984-item harness run was read. The BASED tables mix this accuracy with other recall tasks, so a headline number needs the paper's own column, not a generic "SQuAD" label. Contamination risk is medium: SQuAD text is old and public, but the GPT-4 statements are a 2024 overlay. Gold answers sit in the public validation file.

## How to run it

```
lm_eval --model hf --tasks squad_completion
```

The YAML sets `task: squad_completion` and loads `hazyresearch/based-squad`. Confirm VERSION 1 whitespace stripping before comparing to pre-2026-06-22 logs. inspect_evals, HELM, OpenCompass, and BIG-bench were not found for this spelling. Do not mix with `squadv2` in lm-eval, which uses the official SQuAD 2.0 metric.

## Reading the numbers

A high contains score means the model emitted the gold span somewhere in a short continuation, not that it selected a span by index or refused unanswerable questions. Small models in the BASED paper are the intended subjects; a frontier chat model that paraphrases the answer can still fail contains if the exact gold string is missing. Report the harness version. Read the number next to [squad](squad.md) only as related reading comprehension, not as the same score.
