---
id: melt_knowledge
name: "HELM MELT knowledge (ZaloE2E and ViMMRC)"
aliases:
  - "melt_knowledge_zalo"
  - "melt_knowledge_vimmrc"
  - "ZaloE2E"
  - "ViMMRC"
page_kind: family
category: knowledge
subcategory: "Vietnamese closed-book QA and multiple-choice reading"
status: unknown
summary: "HELM's Vietnamese knowledge track: closed-book answers on ZaloE2E and multiple-choice reading on ViMMRC, both scored by quasi-exact match."
measures: >
  MELT knowledge is two Vietnamese question sets behind one HELM filename, not one quiz. ZaloE2E is
  closed-book QA: the model sees a Vietnamese question and must write an answer without a passage.
  ViMMRC is multiple-choice reading: the model sees a Vietnamese article, a question, and lettered
  options, and must pick the gold option. HELM scores both with quasi-exact match on the test split.
  There is no official average of the two. The schema file's parent blurb "medical domain" does not
  describe these tasks.
task_format: >
  ZaloE2E: open generation, instruction to answer from commonsense and to say "không có đáp án" if
  unknown, max 128 tokens. ViMMRC: joint multiple-choice (`ADAPT_MULTIPLE_CHOICE_JOINT`) with
  instruction "Sau đây là các câu hỏi trắc nghiệm (có đáp án)." An optional `randomize_order` flag
  shuffles choices; default run entries set it false.
metric:
  name: "quasi_exact_match on each scenario's test split (no combined score)"
  direction: higher_is_better
  unit: ""
  max_score: 1
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_melt.yaml and the scenario `get_metadata` methods both set main_metric quasi_exact_match
    and main_split test. The Zalo run spec also attaches F1 metrics; ViMMRC's run spec attaches only
    exact-match metrics. No random or human baseline is stated in the HELM files or dataset cards
    opened here. ViMMRC options are letters A–H mapped to indices; a uniform random baseline would
    depend on how many options each item has, which was not counted.
dataset:
  size: 1114
  size_note: >
    Hugging Face datasets-server (2026-09-08): `ura-hcmut/zalo_e2eqa` has 600 train and 600 test rows
    (1,200 total, no validation split). `ura-hcmut/ViMMRC` has 1,975 train, 294 validation and 514
    test rows (2,783 total). HELM Zalo loads only train and test. HELM ViMMRC loads train, validation
    and test. The front-matter size 1,114 is the two test splits HELM actually scores (600 + 514).
  url: "https://huggingface.co/datasets/ura-hcmut/zalo_e2eqa"
  license: >
    ura-hcmut/zalo_e2eqa card: MIT. ura-hcmut/ViMMRC card: CC-BY-NC-ND-4.0. The two scenarios do not
    share a licence.
  languages:
    - vi
  modalities:
    - text
  splits: "ZaloE2E train 600 / test 600; ViMMRC train 1,975 / validation 294 / test 514"
  public_test_set: true
publisher:
  org: "Stanford CRFM (HELM); dataset mirrors ura-hcmut; ZaloE2E from Zalo AI Challenge 2022"
  authors: []
  url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/melt_knowledge_scenario.py"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/melt_knowledge_scenario.py"
released: "2022"
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
    No MELT leaderboard URL resolved (https://crfm.stanford.edu/helm/melt/latest/ returned 404).
    Saturation on ZaloE2E and ViMMRC under HELM's prompts is not established.
contamination:
  risk: medium
  note: >
    Both Hugging Face mirrors expose labelled test splits (600 ZaloE2E, 514 ViMMRC), and HELM scores
    those test splits. ZaloE2E is a copy of the 2022 challenge set; ViMMRC is a public reading set
    under CC-BY-NC-ND-4.0. No source opened here measures overlap with LLM pretraining.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "melt_knowledge_zalo and melt_knowledge_vimmrc (run_entries_melt.conf). There is no run spec named melt_knowledge."
  opencompass: ""
  bigbench: ""
  other: "Source file helm.benchmark.scenarios.melt_knowledge_scenario."
tags:
  - question-answering
  - reading-comprehension
  - vietnamese
  - helm
  - melt
sources:
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/melt_knowledge_scenario.py"
    title: "HELM melt_knowledge_scenario.py"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/run_specs/melt_run_specs.py"
    title: "HELM melt_run_specs.py (zalo and vimmrc run specs)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_melt.yaml"
    title: "HELM schema_melt.yaml"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_melt.conf"
    title: "HELM run_entries_melt.conf"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/ura-hcmut/zalo_e2eqa"
    title: "ura-hcmut/zalo_e2eqa dataset card"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=ura-hcmut/zalo_e2eqa"
    title: "zalo_e2eqa split sizes, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/ura-hcmut/ViMMRC"
    title: "ura-hcmut/ViMMRC dataset card"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=ura-hcmut/ViMMRC"
    title: "ViMMRC split sizes, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://github.com/Telegram-Zalo/zac2022-e2e-qa"
    title: "Zalo AI Challenge 2022 E2E QA winning-solution repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/Telegram-Zalo/zac2022-e2e-qa/main/LICENSE"
    title: "zac2022-e2e-qa MIT licence (solution code)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/README.md"
    title: "HELM README (maintenance mode 1 June 2026; no MELT board)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-003 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-003"
---

## What it measures

MELT knowledge is HELM's Vietnamese knowledge track. The census id names the Python file. Two scenarios live in it. ZaloE2E is closed-book Vietnamese QA: the prompt is the question only, and the model must emit an answer string. HELM's instruction tells the model to use everyday knowledge and to answer "không có đáp án" when it does not know. ViMMRC is multiple-choice reading: HELM wraps the article as "Ngữ cảnh:" and the question as "Câu hỏi:", then scores which option is tagged correct. Both are Vietnamese text. They do not measure English knowledge or tool use.

## How it is scored

Each scenario reports quasi-exact match on its test split. There is no HELM average of ZaloE2E and ViMMRC. The Zalo run spec also records token F1; ViMMRC's run spec records exact match only, even though the class metadata still names quasi-exact match. Default ViMMRC does not shuffle options (`randomize_order=False`); a priority-3 run entry turns shuffling on. No human or random baseline is given in the opened HELM files. ViMMRC maps answer letters A–H onto option indices, so the number of choices can exceed four.

## Dataset and licence

`ura-hcmut/zalo_e2eqa` is a copy of the Zalo AI Challenge 2022 E2E QA set: 600 train and 600 test rows, MIT licence on the Hugging Face card, pinned by HELM at revision `63494521f4de949bfa57a5f0b79bc3ee47e635ad`. `ura-hcmut/ViMMRC` has 1,975 / 294 / 514 train / validation / test rows, CC-BY-NC-ND-4.0, pinned at `fe68800e37aaa84d80b1d93466b36c3fa60d8bcb`. HELM scores the two test splits (600 + 514). Original ViMMRC paper details were not on the one-line Hugging Face card. The Zalo GitHub repo the card points to is a winning-solution write-up; that repo's LICENSE is MIT for the solution code, not a separate dataset card.

## Who publishes it

Stanford CRFM implements the HELM scenarios. The Hugging Face mirrors are under `ura-hcmut`. ZaloE2E originates in the 2022 Zalo AI Challenge; the mirror README points at `Telegram-Zalo/zac2022-e2e-qa`. Scenario authors for the HELM wrapper are not listed in the Python file. No MELT paper title is stated in schema_melt.yaml. `/helm/melt/latest/` returned 404. The acronym MELT is not expanded in the opened HELM files.

## Lineage

This is not English open-domain QA and not SuperGLUE. Sibling MELT file-slugs in this batch are `melt_ir` and `melt_srn`. HELM also has Vietnamese MLQA and XQuAD scenarios in other files; those are passage QA, not this knowledge track. There is no `melt_knowledge` run spec: the runnable names are `melt_knowledge_zalo` and `melt_knowledge_vimmrc`. No standalone ZaloE2E or ViMMRC page exists in this repository.

## Saturation and contamination

Saturation is unknown without a leaderboard. Contamination risk is medium: HELM scores public labelled test splits of 600 and 514 items. ZaloE2E has been associated with a 2022 contest; ViMMRC is a public CC-BY-NC-ND set. Either could appear in later training crawls. This page has no overlap study.

## How to run it

HELM run entries:

`melt_knowledge_zalo:model=text,max_train_instances=melt`

`melt_knowledge_vimmrc:model=text,randomize_order=False,max_train_instances=melt`

Canonical data-augmentation variants exist at priority 2; shuffled ViMMRC at priority 3. There is no `melt_knowledge` run spec. Not confirmed in lm-evaluation-harness, OpenCompass, inspect_evals, or BIG-bench. HELM's README marks the project as in maintenance mode from 1 June 2026.

## Reading the numbers

A ZaloE2E quasi-exact match is closed-book Vietnamese answering on 600 test questions. A ViMMRC score is multiple-choice reading on 514 test questions. They are not interchangeable and should not be averaged unless the reporter defines an average. Shuffling ViMMRC options can change the number. Because both test sets are public and small, a high score may reflect leakage or prompt format as much as knowledge. Ask which of the two scenarios produced a `melt_knowledge` figure before using it.
