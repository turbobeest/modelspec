---
id: cleva
name: CLEVA
aliases:
  - "CLEVA: Chinese Language Models EVAluation Platform"
  - Chinese Language Models EVAluation Platform
page_kind: benchmark
category: composite
subcategory: "31-task Chinese LLM suite (applications, abilities, and harms) with standardized prompts"
status: active
summary: "HELM wrap of CLEVA, a 31-task Chinese LLM platform with standardized prompts, 370K test instances, and contamination-aware sampling."
measures: >
  cleva is HELM's scenario family for CLEVA (Chinese Language Models EVAluation
  Platform), not one quiz. The model is tested in Chinese across application
  tasks (for example translation, summarization, dialogue, code synthesis) and
  ability tasks (subject knowledge, reasoning primitives, calculation, cultural
  knowledge, harms). CLEVA's claim is that Chinese evals were incomparable
  because prompts were not shared. HELM therefore downloads CLEVA's per-task
  JSONL plus prompt templates and inference parameters, then applies the chosen
  template. Language is Chinese except where a task is explicitly bilingual
  (en2zh / zh2en).
task_format: >
  HELM run-spec function cleva with args task, optional subtask, prompt_id
  (0-based template index), and version (v1 in the paper and README). Adaptation
  is generation, joint multiple choice, or separate multiple choice according to
  each prompt file's meta.mul_as_gen flag. Data are served from
  http://39.108.215.175/data as per-task zip files.
metric:
  name: "task-dependent (exact match, Chinese ROUGE-2, Chinese BLEU, SacreBLEU, iBLEU, math exact match, and others)"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    There is no single CLEVA score in HELM schema_classic.yaml; each cleva_*
    run group names its own main metric. The authors' GitHub README compares
    HELM reproductions of gpt-3.5-turbo-0613 to the CLEVA platform on four
    tasks (for example dialogue summarization Chinese ROUGE-2 0.3045 vs 0.3065).
    Those are not a human baseline.
dataset:
  size: 370000
  size_note: >
    Paper: 370K test instances from 84 datasets across 31 tasks, 33.98% newly
    collected, expanding to over 9 million queries after prompt templates and
    augmentations. HELM loads train.jsonl and test.jsonl per task/subtask when
    present. This page does not re-count the zip files on the CLEVA data host.
  url: "https://github.com/LaVi-Lab/CLEVA"
  license: "CC BY-NC-ND 4.0"
  languages:
    - zh
    - en
  modalities:
    - text
  splits: "per-task train/test JSONL when the files exist; HELM logs a missing split rather than inventing one"
  public_test_set: true
publisher:
  org: CUHK LaVi Lab; Shanghai AI Laboratory (collaboration); HELM integration by Stanford CRFM
  authors:
    - Yanyang Li
    - Jianqiao Zhao
    - Duo Zheng
    - Zi-Yuan Hu
    - Zhi Chen
    - Xiaohui Su
    - Yongfeng Huang
    - Shijia Huang
    - Dahua Lin
    - Michael R. Lyu
    - Liwei Wang
  url: "https://github.com/LaVi-Lab/CLEVA"
paper:
  title: "CLEVA: Chinese Language Models EVAluation Platform"
  arxiv: "2308.04813"
  url: "https://arxiv.org/abs/2308.04813"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/LaVi-Lab/CLEVA"
released: "2023-08"
last_updated: "2025-05"
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
    The paper reports mean win rates over 23 Chinese LLMs rather than a single
    ceiling. The project website listed in the README timed out from this
    session, so no current leaderboard top score is recorded.
contamination:
  risk: medium
  note: >
    About two thirds of the 370K instances reuse existing Chinese data, which
    can leak. The authors collected 33.98% new queries and describe round-wise
    sampling so each leaderboard round uses a unique subset. HELM's public v1
    dump is the paper snapshot, not a rotating holdout.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: cleva
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - chinese
  - composite
  - helm
  - prompt-sensitivity
sources:
  - url: "https://arxiv.org/abs/2308.04813"
    title: "CLEVA paper (arXiv 2308.04813)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2308.04813"
    title: "CLEVA paper HTML"
    accessed: "2026-09-08"
  - url: "https://github.com/LaVi-Lab/CLEVA"
    title: "CLEVA GitHub README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/LaVi-Lab/CLEVA/main/README.md"
    title: "CLEVA README raw"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/LaVi-Lab/CLEVA/main/LICENSE"
    title: "CLEVA CC BY-NC-ND 4.0 license text"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/cleva_scenario.py"
    title: "HELM cleva_scenario.py"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/run_specs/cleva_run_specs.py"
    title: "HELM cleva_run_specs.py"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_classic.yaml"
    title: "HELM schema_classic.yaml CLEVA groups"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2412.04947"
    title: "C2LEVA successor paper"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_cleva_v1.conf"
    title: "HELM run_entries_cleva_v1.conf (live full-suite file)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-031 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-031"
---

## What it measures

CLEVA is a Chinese evaluation platform. A model is not asked one question type. It is run through application tasks (translation, summarization, dialogue, pinyin, code) and ability tasks (knowledge, reasoning, calculation, culture, harms). HELM's `cleva` run spec is the local way to do that: pick a task, optional subtask, prompt template index, and dataset version.

The authors' point is prompt standardization. Each test set ships several Chinese templates. HELM applies template `prompt_id` and the matching `infer_params.json`. Scoring English MMLU-style numbers against CLEVA is a language mismatch. Scoring [ceval](ceval.md) or [cmmlu](cmmlu.md) against CLEVA is a suite mismatch even though all three are Chinese.

## How it is scored

There is no one CLEVA percentage in HELM. `schema_classic.yaml` registers many `cleva_*` groups, each with its own main metric: exact match for classification-style tasks, Chinese ROUGE-2 for dialogue summarization, Chinese BLEU-1 for pinyin and some generation tasks, SacreBLEU for translation, iBLEU for paraphrase, and a math matcher that looks at the last numeric expression. Harms tasks add CLEVA-specific bias, toxicity, and copyright metrics.

The GitHub README compares HELM reproductions of `gpt-3.5-turbo-0613` on v1 to the hosted platform (dialogue summarization ROUGE-2 0.3045 vs 0.3065; en2zh SacreBLEU 60.48 vs 59.23). The authors attribute gaps to seeds and ChatGPT versions. Use one prompt_id when you compare models.

## Dataset and licence

The paper states 370K test instances from 84 datasets and 31 tasks, with 33.98% newly collected, expanding past 9 million queries after templates and perturbations. HELM downloads `{version}/{task}.zip` from the CLEVA data host listed in `cleva_scenario.py` and reads `train.jsonl` / `test.jsonl` plus `prompts.json`. The repository license is CC BY-NC-ND 4.0. Test labels in the v1 dump used for local HELM runs are public once downloaded.

HELM implements a CLEVAScenario subclass per task (text classification, opinion mining, translation, subject knowledge, and the rest). The paper counts 31 tasks; the scenario file defines 32 `CLEVA*Scenario` subclasses including keyphrase extraction. Treat 31 as the paper figure unless you are counting HELM classes.

## Who publishes it

Yanyang Li, Jianqiao Zhao, Duo Zheng, and coauthors at the Chinese University of Hong Kong, with Zhi Chen, Xiaohui Su, and Dahua Lin also at Shanghai AI Laboratory, released the EMNLP 2023 system demonstration (arXiv 9 August 2023, v2 16 October 2023). Liwei Wang is corresponding author. The GitHub organisation is LaVi-Lab. Stanford CRFM merged CLEVA into HELM in the v0.3.0 release (README, 2 November 2023).

## Lineage

CLEVA sits in the Chinese suite wave after [ceval](ceval.md) and [cmmlu](cmmlu.md), with a broader task mix and explicit prompt files. The same group announced C²LEVA (arXiv 2412.04947; README says ACL 2025 Findings) as a bilingual follow-on with automated test renewal. This repository has no `c2leva` page. HELM remains the documented local runner for CLEVA v1.

## Saturation and contamination

The 2023 paper compares 23 models by mean win rate, which is not a percentage ceiling. Whether 2026 models saturate individual tasks was not established here. The project site listed in the README did not respond within 20 seconds, so no live top score is recorded.

Contamination is mixed: most items reuse older Chinese sets, and 33.98% are new. Leaderboard rounds are supposed to sample a unique subset. A HELM v1 local run uses the frozen public dump, which is the weaker of those two protections.

## How to run it

Install HELM (`crfm-helm`) and run `helm-run` with a description such as `cleva:task=translation,subtask=zh2en,prompt_id=0,version=v1`. The live HELM full-suite file is `src/helm/benchmark/presentation/run_entries_cleva_v1.conf` (253 entries on the main blob opened here). The CLEVA README still links `run_specs_cleva_v1.conf`, which 404'd on 2026-09-08. The README says `--max-eval-instances` above 5,000 is enough to cover each task's data. Optional `data_augmentation` values `cleva`, `cleva_robustness`, and `cleva_fairness` are CLEVA-specific.

Do not average HELM's heterogeneous metrics into one unofficial CLEVA score. Do not compare prompt_id 0 on one model to prompt_id 2 on another.

## Reading the numbers

A strong CLEVA task score means the model handled that Chinese template well, not that it is broadly capable in Chinese. Read several tasks and more than one prompt_id. Translation BLEU is not knowledge accuracy. A harms score is not an exam score. If you need a single Chinese exam number, use [ceval](ceval.md) or [cmmlu](cmmlu.md) and say so. If you need the contamination-renewed bilingual follow-on, that is C²LEVA, which is not this id.
