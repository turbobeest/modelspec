---
id: clinicbench
name: ClinicBench
aliases:
  - "Pharmacology QA for Emerging Drugs"
page_kind: benchmark
category: domain
subcategory: "pharmacology multiple-choice QA for emerging drugs (a single task from a larger 17-dataset clinical suite)"
status: unknown
summary: OpenCompass's ClinicBench task runs only a 213-item pharmacology-QA slice of a much larger, unrelated-looking 17-dataset clinical benchmark suite published under the same name.
measures: >
  The name "ClinicBench" names two different things, and the OpenCompass task this page documents
  runs only the smaller of them. OpenCompass's `ClinicBench` dataset config loads a Hugging Face
  dataset, xuxuxuxuxu/Pharmacology-QA: 213 four-option multiple-choice pharmacology questions, with
  no citation, licence or description attached to the mirror itself. Matching its exact row count and
  task description against the wider literature traces this data to one specific task, "Pharmacology
  QA for Emerging Drugs," inside a much larger benchmark suite also called ClinicBench, published by
  Fenglin Liu and co-authors (University of Oxford and Amazon) at EMNLP 2024. That original ClinicBench
  spans three scenarios, eleven tasks and seventeen datasets (over 20,000 test samples in total)
  covering clinical language generation, understanding and reasoning, evaluated across twenty-two
  LLMs -- of which OpenCompass implements only this one 213-item pharmacology task, without stating
  that connection anywhere in its own code.
task_format: >
  Four-option multiple-choice pharmacology question (options labelled A-D in the source data); the
  model is asked to think step by step and give a final "ANSWER: $LETTER" line. The prompt template's
  own instruction text mentions options "one of ABCDEFGHIJKLMNOP", but that is boilerplate shared
  across several OpenCompass multiple-choice tasks, not evidence this dataset has more than four
  options.
metric:
  name: "accuracy (LLM-judged consistency with the gold letter)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  baseline_note: >
    Four-option multiple choice gives a naive random baseline of 25%. No score for this specific
    OpenCompass task, under either name, was found published in any leaderboard or paper reviewed for
    this page, so no top or human baseline is recorded.
dataset:
  size: 213
  size_note: >
    213 questions, confirmed via the Hugging Face datasets-server against the mirror OpenCompass
    actually loads (xuxuxuxuxu/Pharmacology-QA). This exact count and a "Predict the correct answer to
    the given pharmacology question for the new drugs released between October 2023 and April 2024...
    Derived from DrugBank" description both match one row of Table 1 in Liu et al.'s ClinicBench paper,
    which is the strongest evidence tying this mirror back to that paper's "Pharmacology QA for
    Emerging Drugs" task; the mirror itself carries no citation confirming this directly. The wider
    ClinicBench suite that task comes from totals seventeen datasets and over 20,000 test samples,
    none of the rest of which are wired into OpenCompass's ClinicBench config.
  url: "https://huggingface.co/datasets/xuxuxuxuxu/Pharmacology-QA"
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "single unsplit list of 213 questions (Hugging Face 'train'); no held-out test partition"
  public_test_set: true
publisher:
  org: ""
  authors: []
  url: ""
paper:
  title: "Large Language Models in the Clinic: A Comprehensive Benchmark"
  arxiv: "2405.00716"
  url: "https://arxiv.org/abs/2405.00716"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/AI-in-Health/ClinicBench"
released: "2024-04"
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
    No score for OpenCompass's 213-item ClinicBench task, under either name, was found published in
    any leaderboard, paper or model card reviewed for this page.
contamination:
  risk: medium
  note: >
    The source task was deliberately built from drugs released between October 2023 and April 2024,
    specifically so its content would postdate the training cutoffs of the models Liu et al. evaluated
    at the time -- a design meant to keep contamination low at release. That protection erodes for any
    model with a later training cutoff, and by this research date (September 2026) those "emerging"
    drugs are over two years old and plausibly present in newer models' pretraining data. The
    OpenCompass-hosted mirror also carries the full question set and gold labels with no gating or
    canary string.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "ClinicBench"
  bigbench: ""
  other: ""
tags:
  - domain
  - clinical
  - pharmacology
  - drugbank
  - name-collision
sources:
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/ClinicBench/ClinicBench_llmjudge_gen_d09668.py"
    title: "OpenCompass ClinicBench dataset config (loads xuxuxuxuxu/Pharmacology-QA)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/datasets/ClinicBench.py"
    title: "OpenCompass ClinicBenchDataset loader"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/xuxuxuxuxu/Pharmacology-QA"
    title: "xuxuxuxuxu/Pharmacology-QA dataset metadata, Hugging Face (213 rows, A/B/C/D/question/choices/label columns, no description)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/pull/2061"
    title: "Add ClinicBench, PubMedQA and ScienceQA (#2061), stanford-crfm/helm -- opencompass PR by xuxuxuxuxuxjh"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2405.00716"
    title: "Large Language Models in the Clinic: A Comprehensive Benchmark (Liu et al.)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2405.00716"
    title: "ClinicBench paper, full text incl. Table 1 (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/AI-in-Health/ClinicBench"
    title: "AI-in-Health/ClinicBench repository metadata (Apache-2.0; EMNLP 2024 retitled description)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

The name "ClinicBench" names two different things, and the OpenCompass task this page documents runs only the smaller of them. OpenCompass's `ClinicBench` dataset config loads a Hugging Face dataset called `xuxuxuxuxu/Pharmacology-QA`: 213 four-option multiple-choice pharmacology questions, contributed to OpenCompass in May 2025 alongside PubMedQA and ScienceQA, with no citation, licence or description attached to the mirror itself beyond its raw column schema. Matching its exact row count (213) and its questions' apparent subject (pharmacology, tied to specific drugs) against the wider literature traces this data to one specific task, "Pharmacology QA for Emerging Drugs," inside a much larger benchmark suite also called ClinicBench, published by Fenglin Liu and co-authors (University of Oxford and Amazon) at EMNLP 2024. That original ClinicBench spans three scenarios, eleven tasks and seventeen datasets -- over 20,000 test samples in total -- covering clinical language generation, understanding and reasoning, evaluated across twenty-two LLMs under zero-shot and few-shot settings, plus a human expert evaluation of clinical usefulness. OpenCompass implements only this one 213-item pharmacology task from that suite, without stating the connection anywhere in its own code.

The task itself asks a model to answer a multiple-choice pharmacology question about drugs released between October 2023 and April 2024, derived from DrugBank -- material the original authors chose specifically because it postdated the training cutoffs of the models they were evaluating.

## How it is scored

The model is prompted to think step by step and end its response with a line of the form "ANSWER: $LETTER". An LLM judge then compares the extracted letter against the gold label under OpenCompass's `GenericLLMEvaluator`, following grading instructions general enough to also handle multi-select and fill-in-the-blank answers, though this particular task is a single-answer, four-option multiple-choice question. With four options, a naive random baseline is 25%. The prompt template's own instruction text describes options as "one of ABCDEFGHIJKLMNOP," but that phrasing is shared boilerplate reused across several OpenCompass multiple-choice tasks, not evidence this particular dataset offers more than the four options (A-D) actually present in its columns.

## Dataset and licence

The 213-question count is confirmed directly from the Hugging Face dataset OpenCompass loads. That dataset carries no licence field, no description, and no citation back to any paper; it was uploaded by a Hugging Face account with the same name pattern as the OpenCompass contributor who added the `ClinicBench` config in the same pull request as PubMedQA and ScienceQA. The strongest evidence connecting it to Liu et al.'s published ClinicBench suite is that Table 1 of that paper lists a task named "Pharmacology QA for Emerging Drugs," "derived from DrugBank," with exactly 213 items scored by accuracy -- an exact match on both count and description. The original ClinicBench GitHub repository (`AI-in-Health/ClinicBench`) is Apache-2.0 licensed and describes the paper's EMNLP 2024 retitling as "Large Language Models Are Poor Clinical Decision-Makers: A Comprehensive Benchmark," different from the arXiv preprint's title, "Large Language Models in the Clinic: A Comprehensive Benchmark." Whether that licence extends to this specific derived 213-row mirror, and what DrugBank's own terms permit for the underlying drug data, are not established from the sources reviewed here.

## Who publishes it

The wider ClinicBench suite this task is drawn from was built by Fenglin Liu, Zheng Li, Hongjian Zhou and co-authors, based at the University of Oxford's Institute of Biomedical Engineering and Amazon, with further co-authors from Harvard T.H. Chan School of Public Health and Institut Polytechnique de Paris, posted to arXiv in April 2024 and published at EMNLP 2024. The 213-item mirror that OpenCompass actually runs was instead re-packaged and uploaded independently to Hugging Face and to OpenCompass by a different contributor, with no visible connection back to Liu et al.'s team; this page could not confirm whether that re-packaging was authorised by the original authors.

## Lineage

This is a case where a repository's own harness id points to a narrow fragment of a much better-known, much larger project sharing its exact name. Liu et al.'s full ClinicBench aggregates eleven existing clinical datasets (including MedQA, MedMCQA and MMLU-Med, all separately documented elsewhere in this repository) with six datasets the authors built themselves, of which "Pharmacology QA for Emerging Drugs" is one; the other five novel datasets (covering open-ended clinical decision-making, long document processing and drug-interaction analysis) are not implemented by OpenCompass's ClinicBench config and have no page here. Anyone citing a "ClinicBench" score should specify whether it comes from this narrow OpenCompass task or from Liu et al.'s full suite run through their own evaluation code, since the two are not comparable.

## Saturation and contamination

No score for this specific 213-item task, under either name, was found published in any leaderboard, paper or model card reviewed for this page, so saturation is recorded as unknown. Contamination risk sits at medium: the source questions were deliberately drawn from drugs released between October 2023 and April 2024, specifically so their content would postdate the training cutoffs of the models Liu et al. evaluated at the time -- a design meant to keep contamination low at release. That protection necessarily erodes for any model trained later: by this research date those "emerging" drugs are over two years old and plausibly present in newer models' pretraining data, and the OpenCompass-hosted mirror carries the full question set and gold labels with no gating or canary string of its own.

## How to run it

OpenCompass implements this as the `ClinicBench` dataset, loading `xuxuxuxuxu/Pharmacology-QA` directly via `datasets.load_dataset` and grading with `GenericLLMEvaluator`. No lm-evaluation-harness, inspect_evals, HELM or BIG-bench implementation of either the narrow OpenCompass task or the full Liu et al. suite was found. Researchers who want to reproduce Liu et al.'s original, much larger evaluation (three scenarios, eleven tasks, seventeen datasets, twenty-two models) need the authors' own code at `github.com/AI-in-Health/ClinicBench`, which OpenCompass's `ClinicBench` task does not draw on.

## Reading the numbers

Before treating any "ClinicBench" figure as meaningful, establish which of the two things it measures: this page's narrow, 213-item, single-task pharmacology slice, or Liu et al.'s much broader seventeen-dataset clinical suite run through the original authors' own code. A score from the former says something specific and fairly narrow -- whether a model can answer multiple-choice questions about a fixed set of drugs from late 2023/early 2024 -- and, given how the task was designed, an especially high score from a model with a training cutoff after mid-2024 may reflect memorised drug facts rather than clinical reasoning. It does not speak to the generation, understanding or open-ended decision-making tasks that make up most of the original ClinicBench suite's seventeen datasets, and neither this page nor OpenCompass's implementation currently covers those.
