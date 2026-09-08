---
id: belebele
name: Belebele
aliases:
  - "The Belebele Benchmark"
page_kind: benchmark
category: knowledge
subcategory: "massively multilingual multiple-choice reading comprehension"
status: active
summary: "Parallel four-way reading-comprehension set: 900 questions in each of 122 language variants, 109,800 items, passages from FLORES-200."
measures: >
  Belebele tests whether a model can read a short passage and pick the correct answer among
  four options. Every question is written so that it is answerable from the passage, then
  translated into 122 language variants (115 distinct languages, 29 scripts, 27 families).
  Passages come from FLORES-200, so the same 488 passages and 900 questions are aligned
  across languages. English alone is intended to be hard enough to separate models; the
  parallel design is meant to make accuracy comparable across resource levels without
  changing the underlying questions.
task_format: >
  Four-way multiple-choice reading comprehension. lm-eval uses log-likelihood over A/B/C/D
  with English instructions and the template P/Q/A/B/C/D/Answer, zero-shot or few-shot.
  The paper also reports finetuning, translate-train, and cross-lingual settings that the
  harness group does not implement.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: 97.6
  baseline_note: >
    Four options, so random sequence-classification accuracy is 0.25. Human figure is the
    paper's English blind test: four authors, about 30 items each, mean 97.6% with 95% CI
    [93.1, 99.5] over all 900 English questions. Not a multilingual human ceiling.
dataset:
  size: 109800
  size_note: >
    900 questions × 122 language variants = 109,800 rows, matching facebook/belebele on
    Hugging Face (122 configs, 900 test rows each, datasets-server total 109,800). 488
    distinct passages; one or two questions per passage. Test-only; the authors assembled
    a separate English training mix from RACE, SciQ, MultiRC, MCTest, MCScript2.0 and ReClor
    (about 67.5k train / 3.7k development) for models that need task finetuning.
  url: "https://huggingface.co/datasets/facebook/belebele"
  license: "CC-BY-SA-4.0"
  languages: []
  modalities:
    - text
  splits: "test only (900 rows per language config); no official Belebele train split"
  public_test_set: true
publisher:
  org: "Meta (FAIR / facebookresearch)"
  authors:
    - "Lucas Bandarkar"
    - "Davis Liang"
    - "Benjamin Muller"
    - "Mikel Artetxe"
    - "Satya Narayan Shukla"
    - "Donald Husa"
    - "Naman Goyal"
    - "Abhinandan Krishnan"
    - "Luke Zettlemoyer"
    - "Madian Khabsa"
  url: "https://github.com/facebookresearch/belebele"
paper:
  title: "The Belebele Benchmark: a Parallel Reading Comprehension Dataset in 122 Language Variants"
  arxiv: "2308.16884"
  url: "https://arxiv.org/abs/2308.16884"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/facebookresearch/belebele"
released: "2023-08"
last_updated: "2024-08"
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
    No dedicated current leaderboard was opened. The 2024 ACL paper reports Llama 2 70B at
    90.9% on English in one setting, well below the English human sample (97.6%) and with
    large drops on lower-resource languages. Those 2023-era figures are not a current
    ceiling.
contamination:
  risk: medium
  note: >
    The full 109,800 labelled items have been public on GitHub and Hugging Face since
    2023-09 as a test set the authors ask people not to train on. Passages are FLORES-200
    text, which is widely copied. lm-eval enables should_decontaminate on the question
    string. No measured leakage rate was read here.
harness:
  lm_eval: "belebele"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    lm-eval group belebele averages acc and acc_norm across 122 tasks named
    belebele_{FLORES-code} (for example belebele_eng_Latn, belebele_por_Latn),
    weight_by_size true. Few-shot uses sampler first_n on the test split, which is not the
    paper's assembled English training mix. Language-bench groups in this repository
    (portuguese_bench, catalan_bench, galician_bench, basque_bench, french_bench) reuse
    single-language Belebele tasks; those numbers are one language, not the 122-language
    group.
tags:
  - reading-comprehension
  - multilingual
  - multiple-choice
  - flores
  - nlu
sources:
  - url: "https://arxiv.org/abs/2308.16884"
    title: "The Belebele Benchmark (arXiv:2308.16884)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2308.16884"
    title: "Belebele paper HTML (900×122, human 97.6%, CC-BY-SA, FLORES passages)"
    accessed: "2026-09-08"
  - url: "https://github.com/facebookresearch/belebele"
    title: "facebookresearch/belebele repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/facebookresearch/belebele/main/README.md"
    title: "Belebele README (composition, evaluation settings, CC-BY-SA-4.0)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/facebookresearch/belebele/main/LICENSE_CC-BY-SA4.0"
    title: "Belebele CC BY-SA 4.0 licence text"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/facebook/belebele"
    title: "facebook/belebele dataset API (licence cc-by-sa-4.0, created 2023-09-01)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=facebook/belebele"
    title: "facebook/belebele row counts (109,800; 900 per config × 122)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/belebele/README.md"
    title: "lm-eval belebele README (group belebele, 122 language tasks)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/belebele/_belebele.yaml"
    title: "lm-eval group belebele (122 tasks, mean acc / acc_norm)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/belebele/_default_template_yaml"
    title: "lm-eval Belebele prompt template and decontamination flag"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-028 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-028"
---

## What it measures

Belebele is a four-way multiple-choice reading test copied across 122 language variants. The model sees a short passage, a question, and four answers; exactly one answer is correct and is always supported by the passage. The 900 questions and 488 passages are the same everywhere, so a drop from English to a lower-resource language is a language-and-script effect rather than a change of items. Passages are taken from FLORES-200 (with extra Latin-script transliterations for a few Indo-Aryan languages that FLORES does not romanize). Text only.

The authors wrote the questions in English to discriminate comprehension, then translated them with quality checks. They report that English itself was already hard for 2023-era models, while four authors scored 97.6% on a blind English sample.

## How it is scored

The published metric is accuracy: correct / 900 per language, or a mean across languages. Random is 25% for a classifier over A/B/C/D. The paper evaluates several protocols: English-instruction zero-shot, translated instructions, few-shot with English or translated exemplars, English finetune then multilingual or cross-lingual eval, translate-train, and translate-test. lm-evaluation-harness implements the group `belebele` as 122 log-likelihood multiple-choice tasks with English-instruction templates, metrics `acc` and `acc_norm`, aggregated with `weight_by_size`. Its few-shot sampler draws from the test split (`fewshot_split: test`), which is not the assembled RACE/SciQ/… training mix described in the paper. A number from a language-bench group such as `belebele_por_Latn` is one language, not the 122-language mean.

## Dataset and licence

Hugging Face `facebook/belebele` holds 122 configs × 900 test rows = 109,800 labelled items, matching the paper and the GitHub README. There is no official Belebele training split; the dataset is documented as test-only. The Belebele items are CC-BY-SA-4.0, the same family as FLORES-200. The optional assembled training mix is mostly CC-BY-NC and is a different corpus. Answers are public.

## Who publishes it

Meta authors Lucas Bandarkar, Davis Liang, Benjamin Muller, Mikel Artetxe, Satya Narayan Shukla, Donald Husa, Naman Goyal, Abhinandan Krishnan, Luke Zettlemoyer and Madian Khabsa. The preprint is arXiv:2308.16884 (2023-08); the archival paper is ACL 2024 (Bangkok). Data live at facebookresearch/belebele and huggingface.co/datasets/facebook/belebele (Hub created 2023-09-01, card last modified 2024-08-12). No separate live leaderboard was opened for this page.

## Lineage

Belebele is a standalone multilingual MRC benchmark. Passages are reused from FLORES-200, which this repository already documents as [flores](flores.md); that is a translation set, not a predecessor MRC task. Language-specific IberoBench and FrenchBench groups call one Belebele config each (`belebele_por_Latn`, `belebele_cat_Latn`, `belebele_glg_Latn`, `belebele_eus_Latn`, `belebele_fra_Latn`) and must not be cited as the full Belebele score. A speech/ASL extension (2M-belebele) is mentioned in the GitHub README and is not this id.

## Saturation and contamination

Saturation is not established. The paper's strongest English figure among reported models still sat below the 97.6% English human sample, and many languages were far lower. No 2026 leaderboard reading was taken. Contamination risk is medium: the test labels have been public since 2023, FLORES passages are ubiquitous, and the authors still ask that Belebele not be used as training data. lm-eval turns on question-string decontamination.

## How to run it

In lm-evaluation-harness, run the group `belebele` or a single `belebele_{code}` task (dataset `facebook/belebele`, config equal to the FLORES code). State shot count and whether few-shot examples came from test or from the assembled English mix. No inspect_evals, HELM or OpenCompass task named `belebele` was confirmed in the sources opened here. Do not compare a 122-language group mean to a single-language IberoBench number.

## Reading the numbers

A strong English score means the model can pick the passage-supported option among four English answers; it does not mean the same skill in the other 121 variants. A 122-language mean hides script and resource gaps, so report the language or the aggregation. lm-eval `acc` versus `acc_norm`, and test-split few-shot versus the paper's training mix, are different protocols. Random is 25%. Public labels since 2023.
