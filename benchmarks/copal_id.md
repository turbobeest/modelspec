---
id: copal_id
name: "COPAL-ID (Choice of Plausible Alternatives — Local Nuances, Indonesia)"
aliases:
  - "COPAL-ID"
  - "COPAL"
  - "copal_id_standard"
  - "copal_id_colloquial"
page_kind: benchmark
category: reasoning
subcategory: "Indonesian COPA-style causal commonsense with Jakartan local nuances"
status: active
summary: "Two 559-item Indonesian COPA-style tests of Jakartan local terms, culture, and language, written from scratch in standard and colloquial Indonesian."
measures: >
  COPAL-ID is a two-choice causal commonsense task in Indonesian. The model
  reads one premise and a cause or effect cue, then picks the more plausible
  of two alternatives. Items were written from scratch by Jakartan natives,
  not translated from English COPA. They target local terminology, culture,
  and language phenomena that XCOPA-ID does not stress. Each item exists in
  standard Indonesian and in Jakartan colloquial Indonesian.
task_format: >
  Two-choice classification: Indonesian premise plus cause/effect cue and two
  alternatives. lm-eval verbalizes the cue as "karena" (cause) or "maka"
  (effect) after the premise. No free-text explanation is required.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: 95.0
  baseline_note: >
    Binary choice gives a 50% chance rate. Paper Table 4 reports native
    Jakartan human accuracy 95.00 on standard COPAL-ID and 95.62 on the
    colloquial twin. The abstract's 66.91% is BLOOMZ-7B 5-shot on standard
    COPAL-ID; 73.88% is Sailor-7B 5-shot on the same column. Table 4's GPT-4
    5-shot 92.13 / 91.06 matches Table 6 Local GPT-4 (Jakartan-culture
    instruction); Table 6 without that instruction is 89.80 on both
    variants. lm-eval scores log-likelihood accuracy, not that 5-shot setup.
dataset:
  size: 559
  size_note: >
    GitHub README and Hugging Face splits each hold 559 items. Direct CSV
    counts: test_copal.csv 559 and test_copal_colloquial.csv 559 (1,118
    rows if both variants are pooled; datasets-server reports 1,118). Labels
    279 vs 280; cause 279 / effect 280. Paper Table 2: Terminology 186/181
    cause/effect, Culture 136/146, Language 49/57. CSV Language flag is 107
    versus Table 2's 106. Items may carry more than one category. Test-only;
    no train split.
  url: "https://huggingface.co/datasets/haryoaw/COPAL"
  license: "CC-BY-SA-4.0 (Hugging Face card and README badge). The GitHub LICENSE file also opens with an MIT License line before the CC BY-SA 4.0 text."
  languages:
    - id
  modalities:
    - text
  splits: "test 559 (standard) / test_colloquial 559; no training split"
  public_test_set: true
publisher:
  org: "MBZUAI, with independent collaborators"
  authors:
    - "Haryo Akbarianto Wibowo"
    - "Erland Hilman Fuadi"
    - "Made Nindyatama Nityasya"
    - "Radityo Eko Prasojo"
    - "Alham Fikri Aji"
  url: "https://github.com/haryoa/COPAL-ID"
paper:
  title: "COPAL-ID: Indonesian Language Reasoning with Local Culture and Nuances"
  arxiv: "2311.01012"
  url: "https://arxiv.org/abs/2311.01012"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/haryoa/COPAL-ID"
released: "2023-11"
last_updated: "2023-12"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 92.13
  as_of: "2023-11"
  note: >
    Paper Table 4, GPT-4 5-shot on standard COPAL-ID (91.06 on colloquial).
    Human 95.00 / 95.62. No live leaderboard of current open models was
    read. lm-eval numbers use a different protocol than the paper's 5-shot
    prompts.
contamination:
  risk: medium
  note: >
    The full labelled test set has been public on Hugging Face and GitHub
    since late 2023. There is no hidden split. The authors wrote items from
    scratch so English COPA text is not a copy source, but web-trained
    models may still have seen the posted CSV.
harness:
  lm_eval: "copal_id (tag); tasks copal_id_standard (split test) and copal_id_colloquial (split test_colloquial); dataset haryoaw/COPAL config id; output_type multiple_choice; metric acc"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - indonesian
  - commonsense
  - causal-reasoning
  - copa-style
  - multiple-choice
sources:
  - url: "https://arxiv.org/abs/2311.01012"
    title: "COPAL-ID: Indonesian Language Reasoning with Local Culture and Nuances (arXiv:2311.01012)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2311.01012"
    title: "COPAL-ID full text on ar5iv (Table 2 counts, Table 4 scores, human 95.00/95.62)"
    accessed: "2026-09-08"
  - url: "https://github.com/haryoa/COPAL-ID"
    title: "haryoa/COPAL-ID repository (559 instances, lm-eval task names, CC BY-SA 4.0 badge)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/haryoa/COPAL-ID/main/LICENSE"
    title: "COPAL-ID LICENSE file (MIT header line, then CC BY-SA 4.0 text)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/haryoaw/COPAL"
    title: "haryoaw/COPAL dataset card (cc-by-sa-4.0, test and test_colloquial)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=haryoaw/COPAL"
    title: "Hugging Face datasets-server size (559 + 559 = 1,118 rows)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/copal_id/README.md"
    title: "lm-evaluation-harness copal_id README (group, standard vs colloquial tasks)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/copal_id/standard.yaml"
    title: "lm-eval copal_id_standard.yaml (haryoaw/COPAL, acc, test split)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/copal_id/colloquial.yaml"
    title: "lm-eval copal_id_colloquial.yaml (test_colloquial split)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/copal_id/utils.py"
    title: "lm-eval copal_id utils.py (karena/maka connectors)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-035 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-035"
---

## What it measures

COPAL-ID asks which of two Indonesian sentences is the more plausible cause or effect of a one-sentence premise. The format matches English COPA, but the items are original Jakartan writing, not a translation of [XCOPA](xcopa.md). They probe local terms (foods, documents, public figures), local norms, and language tricks such as idioms and ambiguous words. Each item has a standard-Indonesian version and a Jakartan colloquial paraphrase with the same label.

## How it is scored

The published metric is accuracy on a two-way choice, so chance is 50%. Paper Table 4 gives human scores of 95.00% (standard) and 95.62% (colloquial). The same table's GPT-4 5-shot scores are 92.13 and 91.06; Table 6 shows those peaks use a Jakartan-culture instruction (Local GPT-4), versus 89.80 without it. Open 5-shot prompting in Table 4 peaks at Sailor-7B 73.88% on standard COPAL-ID; BLOOMZ-7B's 66.91% is the abstract's "general multilingual" figure. lm-eval does not use those prompts. It scores multiple-choice log-likelihood (`acc`) on `haryoaw/COPAL`, with "karena" or "maka" appended to the premise.

## Dataset and licence

Both CSVs counted here have 559 labelled test items and no train split. Hugging Face config `id` exposes `test` and `test_colloquial`. Cause/effect is 279/280. Category flags overlap; paper Table 2 lists Terminology 367, Culture 282, Language 106 across cause and effect, while the standard CSV Language column is 107. The Hub card and README badge say CC BY-SA 4.0. The GitHub LICENSE file starts with "MIT License" and then prints the CC BY-SA 4.0 text; this page does not pick one.

## Who publishes it

Haryo Akbarianto Wibowo and Alham Fikri Aji (MBZUAI) with Erland Hilman Fuadi, Made Nindyatama Nityasya, and Radityo Eko Prasojo. The paper is arXiv:2311.01012, posted 2023-11-02; v3 (2024-04-21) is the NAACL 2024 camera-ready. No separate live leaderboard was found. The authors point to lm-eval for reproduction.

## Lineage

This is not a translation of SuperGLUE [COPA](superglue_copa.md) and not the Indonesian slice of [XCOPA](xcopa.md). The paper uses XCOPA-ID as an easier contrast: GPT-4 5-shot is 97.20 there versus 92.13 on standard COPAL-ID. GEN-X Indonesian COPA is training data in some paper setups because COPAL-ID itself has no train set. No successor page exists in this repository.

## Saturation and contamination

GPT-4 5-shot in the paper is close to, but still below, the 95% human ceiling on both variants. Open models in that table sit well below. There is no current public leaderboard of 2025–2026 models, and lm-eval scores are not those 5-shot numbers. Labels have been public since 2023, so treat contamination as at least medium.

## How to run it

Install lm-evaluation-harness and run `copal_id_standard` or `copal_id_colloquial`. The tag `copal_id` selects both. Dataset path is `haryoaw/COPAL`, config `id`. Do not compare a 5-shot ChatGPT-style prompt from the paper to a harness log-likelihood `acc` without saying so. Report standard and colloquial separately; the authors say colloquial is generally harder.

## Reading the numbers

A high standard-Indonesian score means the model can do COPA-style cause/effect with Jakartan facts and wording, not that it handles every Indonesian variety. A gap between standard and colloquial is the dialect check the authors wanted. XCOPA-ID is an easier related number, not a substitute. Human 95% is the practical ceiling in the paper; GPT-4 5-shot did not pass it. Check which variant, which prompt, and whether the scorer used log-likelihood or generated a choice letter.
