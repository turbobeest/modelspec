---
id: noreval
name: NorEval
aliases: []
page_kind: family
category: composite
subcategory: Norwegian language evaluation
status: active
summary: NorEval is a 24-dataset Norwegian language evaluation benchmark integrated into lm-evaluation-harness.
measures: NorEval groups Norwegian-language tasks across nine categories, including grammar correction, commonsense, Belebele, idioms, OpenBookQA, reading comprehension, summarization, and generation. It is a suite rather than one item-level evaluation.
task_format: Varies by member task; text classification, question answering, and generation tasks are represented.
metric: {name: "", direction: higher_is_better, unit: "", max_score: null, random_baseline: null, human_baseline: null, baseline_note: "Metrics are task-specific."}
dataset: {size: 24, size_note: "The NorEval README describes 24 datasets: 19 existing peer-reviewed datasets and five created for the benchmark; member item counts vary.", url: https://github.com/ltgoslo/noreval, license: "", languages: [Norwegian], modalities: [text], splits: "", public_test_set: null}
publisher: {org: NorEval / EleutherAI lm-evaluation-harness integration, authors: [], url: https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/noreval}
paper: {title: "NorEval: A Norwegian Language Understanding and Generation Evaluation Benchmark", arxiv: "2504.07749", url: https://arxiv.org/abs/2504.07749, year: 2025}
leaderboard_url: ""
repo_url: https://github.com/EleutherAI/lm-evaluation-harness
released: ""
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: [ask_gec, ncb, norbelebele, norcommonsenseqa, norec, noridiom, noropenbookqa, norquad]}
saturation: {status: unknown, top_score: null, as_of: "", note: No aggregate leaderboard or ceiling analysis was established.}
contamination: {risk: unknown, note: The suite mixes datasets with different publication histories; aggregate risk is not established.}
harness: {lm_eval: noreval, inspect_evals: "", helm: "", opencompass: "", bigbench: "", other: ""}
tags: [norwegian, multilingual, suite]
sources:
  - url: https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/noreval
    title: lm-evaluation-harness NorEval task collection
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/noreval/README.md
    title: NorEval README
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-batch-017 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: GPT-5.6 Luna independent review, luna-batch-017}
---

## What it measures

NorEval is a collection of Norwegian-language tasks in lm-evaluation-harness. The repository tree includes grammar correction, Norwegian commonsense, Norwegian Belebele, idiom, OpenBookQA, reading comprehension, summarization, and generation directories. The README describes 24 datasets across nine categories and supports both Bokmål and Nynorsk.

Because the members test different abilities, NorEval does not define one single prompt or one universal metric. A run must identify its member tasks and language variant.

## How it is scored

Metrics are task-specific. The sources read identify the collection and its task directories, but do not establish an aggregate scoring formula, human baseline, or common maximum. Report each task’s metric separately.

## Dataset and licence

The suite README does not provide an aggregate item count or common licence. Member datasets may have different sizes and terms. Norwegian is the documented language context, but exact dialect and split details should be taken from each member task.

## Who publishes it

The task integration is distributed in EleutherAI’s lm-evaluation-harness. The README identifies the paper “NorEval: A Norwegian Language Understanding and Generation Evaluation Benchmark” (arXiv:2504.07749) and the NorEval project at `ltgoslo/noreval`. No current aggregate leaderboard was established.

## Lineage

NorEval is a family page. The repository exposes member task directories including `ask_gec`, `ncb`, `norbelebele`, `norcommonsenseqa`, `norec`, `noridiom`, `noropenbookqa`, `norquad`, `norsumm`, `nortruthfulqa`, `nrk_quiz_qa`, `norrewrite-instruct`, `norsummarize-instruct`, and `tatoeba`. These are member evaluations, not interchangeable aliases.

## Saturation and contamination

Aggregate saturation and contamination are unknown. Different members have different publication histories and exposure profiles, so a suite-level label would conceal important differences.

## How to run it

Use the lm-evaluation-harness task name `noreval` only after checking the current task registry and selecting the desired members. Record the exact subtask, dataset revision, prompt, and metric. Scores from Norwegian subdatasets should not be averaged without a documented weighting rule.

## Reading the numbers

NorEval results can indicate Norwegian performance across several task types. They do not imply uniform competence across the suite or broad Norwegian cultural and linguistic coverage. Inspect member-level scores, dialect, prompt language, and dataset provenance before drawing conclusions.

An aggregate number can hide a model’s strengths and weaknesses because the member tasks differ in objective, format, and difficulty. A reproducible report should list every selected task and preserve the harness version used to load it.
