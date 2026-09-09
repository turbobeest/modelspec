---
id: adv_glue
name: "AdvGLUE (Adversarial GLUE)"
aliases:
  - "Adversarial GLUE"
  - "AdvGLUE"
page_kind: family
category: composite
subcategory: "adversarial robustness suite over five GLUE tasks (SST-2, QQP, QNLI, RTE, MNLI)"
status: active
summary: "Adversarial restatement of five GLUE tasks using word-level, sentence-level and human-written attacks; OpenCompass scores a public annotated development pack, not the original hidden test set."
measures: >
  AdvGLUE asks whether a model that looks strong on GLUE still labels the same
  sentence-pair and sentiment tasks after adversarial edits. It covers five GLUE
  tasks: SST-2 sentiment, QQP paraphrase, and the NLI tasks MNLI, QNLI and RTE.
  CoLA and WNLI from GLUE are omitted. Attacks include 14 methods grouped as
  word-level (embedding similarity, typos, context-aware, knowledge-guided,
  compositions), sentence-level (syntactic and distraction), and human-crafted
  sets (CheckList, StressTest, ANLI, AdvSQuAD). Crowd workers filtered examples
  so that the label should still hold.
task_format: >
  Same classification or NLI format as the parent GLUE task, on adversarially
  perturbed text. OpenCompass instead prompts for an option letter and reports
  accuracy drop against concatenated original items.
metric:
  name: "per-task GLUE metrics averaged as an AdvGLUE score; OpenCompass additionally reports acc_drop = 1 - (adversarial accuracy / original accuracy)"
  direction: higher_is_better
  unit: ""
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper reuses each GLUE task's metric. ELECTRA (Large) is reported to fall
    from a 93.16 GLUE score to 41.69 on AdvGLUE. That is a 2021 encoder result,
    not a current LLM figure. OpenCompass's acc_drop is a different statistic:
    lower drop means more robustness, so it is not the AdvGLUE score.
dataset:
  size: 4978
  size_note: >
    Paper Table 1 sums the AdvGLUE test set to 4,978 examples (SST-2 1,420, QQP
    422, QNLI 968, RTE 304, MNLI 1,864). Section 3.5 then splits curated items
    9:1: examples generated from 90% of the benign GLUE sources are the hidden
    CodaLab test, and the rest are public dev; human-crafted items are also 90%
    test / 10% dev. That is not the abstract's separate claim that around 90% of
    *raw* attack outputs were invalid and filtered. Hugging Face
    `AI-Secure/adv_glue` currently exposes only validation splits totalling 738
    rows (SST-2 148, QQP 78, QNLI 148, RTE 81, MNLI 121, MNLI-mismatched 162).
    The project site on 2024-01-25 announced a released annotated test set; that
    full file was not loaded here. OpenCompass loads `opencompass/advglue-dev`
    (Hugging Face API returned 401 from this session).
  url: "https://huggingface.co/datasets/AI-Secure/adv_glue"
  license: CC-BY-SA-4.0
  languages:
    - en
  modalities:
    - text
  splits: "original protocol: public dev plus hidden test; HF mirror: validation only, 738 rows; OpenCompass concatenates each adversarial item with its original counterpart for acc_drop"
  public_test_set: false
publisher:
  org: "University of Illinois Urbana-Champaign and Microsoft"
  authors:
    - "Boxin Wang"
    - "Chejian Xu"
    - "Shuohang Wang"
    - "Zhe Gan"
    - "Yu Cheng"
    - "Jianfeng Gao"
    - "Ahmed Hassan Awadallah"
    - "Bo Li"
  url: "https://adversarialglue.github.io/"
paper:
  title: "Adversarial GLUE: A Multi-Task Benchmark for Robustness Evaluation of Language Models"
  arxiv: "2111.02840"
  url: "https://arxiv.org/abs/2111.02840"
  year: 2021
leaderboard_url: "https://adversarialglue.github.io/"
repo_url: "https://github.com/AI-secure/adversarial-glue"
released: "2021-11"
last_updated: "2024-01"
lineage:
  family: ""
  predecessor: glue
  successors:
    - decodingtrust_adv_robustness
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    2021 encoder models scored far below their GLUE numbers (ELECTRA Large 41.69
    AdvGLUE vs 93.16 GLUE). No current LLM leaderboard figure was read from the
    homepage or Hugging Face card. Saturation among today's models is not
    established.
contamination:
  risk: medium
  note: >
    The public development set has been downloadable since release. After
    curation, the paper's §3.5 protocol held out 90% of remaining items as a
    hidden CodaLab test (not 90% of raw generated attacks). The homepage later
    (2024-01-25) announced a released annotated test set, which raises leakage
    risk for any run after that date, even though the GitHub README still
    describes CodaLab-only test scoring. Hugging Face still ships only the
    738-row validation pack. This is not DecodingTrust AdvGLUE++
    (`decodingtrust_adv_robustness`).
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: adv_glue
  bigbench: ""
  other: ""
tags:
  - adversarial
  - robustness
  - glue
  - nli
  - family
sources:
  - url: "https://arxiv.org/abs/2111.02840"
    title: "AdvGLUE paper on arXiv (NeurIPS 2021 Datasets and Benchmarks oral)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2111.02840"
    title: "AdvGLUE paper full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://adversarialglue.github.io/"
    title: "AdvGLUE project homepage"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/AI-Secure/adv_glue"
    title: "AI-Secure/adv_glue dataset card"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=AI-Secure/adv_glue"
    title: "Hugging Face datasets-server split counts for AI-Secure/adv_glue"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/adv_glue"
    title: "OpenCompass adv_glue config directory"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/advglue.py"
    title: "OpenCompass AdvDataset and AccDropEvaluator"
    accessed: "2026-09-08"
  - url: "https://github.com/AI-secure/adversarial-glue"
    title: "Official AdvGLUE GitHub (dev.json, evaluate.py; test still described as hidden)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-024 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-024"
---

## What it measures

AdvGLUE is GLUE under attack. A model sees the same five English classification tasks — SST-2, QQP, QNLI, RTE, MNLI — after word edits, sentence-level distractions, or human-written adversarial templates. The claim is robustness: does the original label still come out when the text is perturbed but, after human filtering, still has that label?

It is not the full nine-task GLUE suite. CoLA and WNLI are absent. It is also not DecodingTrust's AdvGLUE++, which this repository files as `decodingtrust_adv_robustness`.

## How it is scored

The paper keeps each GLUE task's metric and summarises them as an AdvGLUE score, analogous to the GLUE score. Models in 2021 dropped sharply; ELECTRA (Large) is the cited example, 93.16 down to 41.69. Official scoring originally required uploading a model to CodaLab so it could run on a hidden test set.

OpenCompass does something else. Each Adv* dataset concatenates adversarial rows with reconstructed original rows, then `AccDropEvaluator` splits the list in half and reports `acc_after`, `acc_before`, and `acc_drop = 1 - acc_after / acc_before`. That drop is not the AdvGLUE score. A reporter who quotes OpenCompass `adv_sst2` without saying "accuracy drop on the annotated dev pack" is not quoting the paper.

## Dataset and licence

Table 1 of the paper counts 4,978 adversarial test examples across the five tasks. After human filtering, §3.5 puts 90% of the remaining items in a hidden CodaLab test and 10% in public dev; that is separate from the abstract's ~90% raw-attack filter rate. The public Hugging Face validation splits now total 738 rows including MNLI-mismatched. The homepage, under CC BY-SA 4.0, still offers a dev download and, as of 25 January 2024, an annotated test download. Code lives at `AI-secure/adversarial-glue` (`dev.json`, `evaluate.py`). Paths `AI-secure/AdvGLUE` and `AI-Secure/AdvGLUE` 404. The GitHub README still says the test set is not public, which conflicts with the homepage news item.

## Who publishes it

Boxin Wang, Chejian Xu, and co-authors at UIUC and Microsoft. The paper is arXiv:2111.02840, submitted 4 November 2021, with an oral at NeurIPS 2021 Datasets and Benchmarks. The project site is adversarialglue.github.io.

## Lineage

Predecessor is `glue`. DecodingTrust later built AdvGLUE++ (`decodingtrust_adv_robustness`), a larger perturbed pack used by HELM, which is not this benchmark. SuperGLUE is a different GLUE successor and is not AdvGLUE.

## Saturation and contamination

Encoder-era AdvGLUE scores were far from GLUE ceilings; whether today's LLMs have closed that gap on the hidden test set was not established here. Contamination is mixed: the small public validation set is old and fully labeled, while the original protocol kept most test items off the hub. After the January 2024 test-set announcement, assume later training crawls may have seen the annotated test file.

## How to run it

OpenCompass configs live under `opencompass/configs/datasets/adv_glue/` with abbreviations `adv_sst2`, `adv_qqp`, `adv_qnli`, `adv_rte`, `adv_mnli`, and `adv_mnli_mm`, loading `opencompass/advglue-dev` and `AccDropEvaluator`. The paper's `evaluate.py` plus CodaLab path is the official AdvGLUE score. Do not mix those two numbers. Use `AI-secure/adversarial-glue` for the authors' `evaluate.py`, not the 404 `AdvGLUE` path.

## Reading the numbers

A high AdvGLUE score means the model kept GLUE-style labels under the paper's filtered attacks, not that it is jailbreak-hard or generally robust. An OpenCompass `acc_drop` near zero can mean robustness, or it can mean both halves were already easy. Always check which split (738-row HF validation, annotated homepage test, or hidden CodaLab test) and which metric (task accuracy versus accuracy drop) a paper used, and do not average AdvGLUE with AdvGLUE++.
