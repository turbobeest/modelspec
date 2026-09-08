---
id: bangla_commonsenseqa
name: "Bangla CommonsenseQA"
aliases:
  - "bangla_commonsenseQA"
  - "CommonsenseQA-BN"
  - "CommonsenseQA Bangla"
page_kind: benchmark
category: reasoning
subcategory: "Bangla commonsense multiple-choice QA, machine-translated from CommonsenseQA"
status: active
summary: "10,962-item machine translation of CommonsenseQA into Bangla, built with an automated Google-Translate-plus-LLM-rewriting pipeline the authors call Expressive Semantic Translation."
measures: >
  Bangla CommonsenseQA tests the same thing as the English CommonsenseQA -- whether a model can
  answer a five-way multiple-choice question that requires general world knowledge rather than
  information stated in the question itself -- but in Bangla. It is a translation, not a
  from-scratch Bangla benchmark: the TituLLMs paper that introduces it states plainly that the
  authors "translated the CommonsenseQA dataset ... into Bangla" using a custom pipeline they call
  Expressive Semantic Translation (EST), which combines a standard neural machine translation pass
  with an iterative, LLM-based refinement step that generates and ranks multiple candidate
  re-translations before selecting one. No human translation or per-item human verification of the
  translated benchmark items themselves is described for this dataset, which distinguishes it from
  `bangla_boolqa` in the same paper, where a human annotator did spot-check the (independently
  generated, not translated) items.
task_format: >
  Five-way multiple-choice question answering in Bangla (answer labels A-E), no supporting passage;
  the reference lm-evaluation-harness task scores it zero- or few-shot by comparing the
  log-likelihood the model assigns to each of the five answer options.
metric:
  name: "accuracy (acc and length-normalised acc_norm)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 20.0
  human_baseline: null
  baseline_note: >
    20% is the five-way random-guess rate. No Bangla-specific human baseline was established from a
    source read for this page; the original English CommonsenseQA's reported human accuracy of 89%
    (recorded on this repository's commonsense_qa.md page) describes a different item pool in a
    different language and should not be assumed to transfer to the translated version.
dataset:
  size: 10962
  size_note: >
    9,741 train and 1,221 validation rows (10,962 total), consistent between the dataset card's own
    split table and the Hugging Face datasets-server, and matching the "CommonsenseQA BN (10,962
    entries)" figure the introducing paper reports directly. No test split is published; the
    original English CommonsenseQA's test-set labels are also not public (commonsense_qa.md on this
    repository records the same constraint), so this gap is inherited rather than introduced by the
    translation. The train and validation counts match the English original's train and validation
    split sizes exactly, consistent with a row-for-row translation rather than a re-sampling of the
    source data. The Hugging Face repository's own commit history shows this dataset was first
    uploaded in October 2024, about four months before the TituLLMs paper that documents it appeared
    on arXiv.
  url: "https://huggingface.co/datasets/hishab/commonsenseqa-bn"
  license: "MIT (Hugging Face dataset card)"
  languages:
    - bn
  modalities:
    - text
  splits: "train (9,741, used for few-shot sampling) / validation (1,221, the harness's scored eval split); no test split"
  public_test_set: true
publisher:
  org: "Hishab (Hishab Singapore Pte. Ltd), with the University of Central Florida and the Qatar Computing Research Institute"
  authors:
    - "Shahriar Kabir Nahin"
    - "Rabindra Nath Nandi"
    - "Sagor Sarker"
    - "Quazi Sarwar Muhtaseem"
    - "Md Kowsher"
    - "Apu Chandraw Shill"
    - "Md Ibrahim"
    - "Mehadi Hasan Menon"
    - "Tareq Al Muntasir"
    - "Firoj Alam"
  url: "https://github.com/hishab-nlp/titulm"
paper:
  title: "TituLLMs: A Family of Bangla LLMs with Comprehensive Benchmarking"
  arxiv: "2502.11187"
  url: "https://arxiv.org/abs/2502.11187"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/hishab-nlp/titulm"
released: "2025-02"
last_updated: ""
lineage:
  family: ""
  predecessor: "commonsense_qa"
  successors: []
  variants: []
saturation:
  status: open
  top_score: 33.0
  as_of: "2025-02"
  note: >
    The introducing paper reports results only for models of 3B parameters or fewer, plus the
    legacy GPT-davinci-002; no frontier or larger model's score was found from a source read for
    this page. Within that set, scores are weak and close to random: the paper's own TituLLM-3B
    model reaches the reported maximum of 33% at five-shot, only 13 points above the 20% random
    baseline, and most other small models score in the low-to-mid 20s. That is a difficult result
    to read as evidence of a hard ceiling; it more likely reflects that small models struggle with
    Bangla commonsense reasoning, translated or otherwise, and that no strong model has yet been
    evaluated against it in a source this page could confirm.
contamination:
  risk: medium
  note: >
    The English CommonsenseQA has been fully public with answers since 2019 and is very likely
    present in most models' pretraining data in some form. This Bangla translation is newer -- its
    Hugging Face repository dates to around October 2024 -- but because it is a mechanical,
    automated translation of a long-public source rather than newly authored content, a model that
    has memorised the English original could plausibly transfer that memorisation through
    translation, especially given how formulaic the EST pipeline's output can be.
harness:
  lm_eval: "bangla_commonsenseqa"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - reasoning
  - commonsense
  - multiple-choice
  - bangla
  - low-resource
  - machine-translated
sources:
  - url: "https://arxiv.org/abs/2502.11187"
    title: "TituLLMs: A Family of Bangla LLMs with Comprehensive Benchmarking"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2502.11187"
    title: "TituLLMs paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/hishab/commonsenseqa-bn"
    title: "hishab/commonsenseqa-bn dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/hishab/commonsenseqa-bn"
    title: "hishab/commonsenseqa-bn dataset metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=hishab/commonsenseqa-bn"
    title: "hishab/commonsenseqa-bn split sizes, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bangla/bangla_commonsenseqa.yaml"
    title: "lm-evaluation-harness bangla_commonsenseqa.yaml task config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bangla/README.md"
    title: "lm-evaluation-harness bangla tasks directory README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/README.md"
    title: "lm-evaluation-harness top-level task registry (lists 'bangla_commonsenseQA')"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Bangla CommonsenseQA is a Bangla translation of CommonsenseQA: a five-way multiple-choice question that requires general world knowledge to answer, built originally from ConceptNet relations by the English dataset's authors. The TituLLMs paper that introduces the Bangla version states directly that the authors "translated the CommonsenseQA dataset ... into Bangla" using their own pipeline, Expressive Semantic Translation (EST), which runs a standard machine-translation pass and then refines it through multiple LLM-generated candidate re-translations, ranked and selected by further model-based evaluation. That is a fully automated process: no human translation or per-item human verification of the finished Bangla benchmark items is described, unlike `bangla_boolqa` in the same paper, where a human annotator did spot-check the dataset (which was independently generated rather than translated).

## How it is scored

Every item is five-way multiple choice (labels A-E), so random guessing scores 20%. The reference lm-evaluation-harness task scores it as a likelihood comparison across the five options rather than free-form generation, reporting both raw accuracy and length-normalised accuracy (`acc_norm`), matching how the harness typically scores CommonsenseQA-shaped tasks. The harness config samples few-shot examples from the 9,741-row "train" split and scores against the 1,221-row "validation" split; no test split exists to score against instead.

## Dataset and licence

The dataset totals 10,962 rows: 9,741 train and 1,221 validation, a figure confirmed independently by the dataset card's own split table, the Hugging Face datasets-server's live row counts, and the introducing paper's reported total. No test split is published, which mirrors the English CommonsenseQA's own missing public test-set labels rather than being a gap specific to the translation. The train and validation row counts match the English original's split sizes exactly, consistent with a direct, row-for-row translation rather than a re-sampled subset. The Hugging Face repository's own history shows this specific dataset was first uploaded around October 2024, roughly four months before the TituLLMs paper describing it was posted to arXiv -- a minor discrepancy this page notes without further explanation, since no source read for this page accounts for the gap. The dataset card states an MIT licence.

## Who publishes it

Bangla CommonsenseQA comes from the same TituLLMs paper as the other three Bangla benchmarks in this batch: Shahriar Kabir Nahin, Rabindra Nath Nandi, Sagor Sarker, Quazi Sarwar Muhtaseem and Md Kowsher (Hishab Singapore Pte. Ltd and the University of Central Florida), together with Apu Chandraw Shill, Md Ibrahim, Mehadi Hasan Menon, Tareq Al Muntasir and Firoj Alam (Qatar Computing Research Institute), posted to arXiv in February 2025. Hishab maintains the reference `titulm` repository and the dataset's Hugging Face page.

## Lineage

This page names `commonsense_qa` (CommonsenseQA, on this repository's commonsense_qa.md) as its predecessor: unlike `bangla_boolqa`, this is a direct, item-for-item translation of that English benchmark rather than an independently constructed dataset that merely shares its format. It belongs to a family of four Bangla benchmarks published together in the TituLLMs paper -- `bangla_boolqa`, `bangla_piqa` and `bangla_openbookqa`, all in this repository -- three of which (this one, `bangla_piqa` and `bangla_openbookqa`) share the same EST translation pipeline, while `bangla_boolqa` alone was generated rather than translated.

## Saturation and contamination

The introducing paper reports results only for models of 3B parameters or fewer, plus the legacy GPT-davinci-002 as a reference point; no larger or more recent frontier model's score was found from a source read for this page. Scores within that set are weak: the paper's own TituLLM-3B model reaches the reported maximum, 33% at five-shot, only 13 points above the 20% random baseline, and most other small models tested score in the low-to-mid 20s. That reads as a genuinely hard benchmark for small models rather than a saturated one, though it leaves open how a strong frontier model would score. Contamination risk sits at medium: the English CommonsenseQA has been public with answers since 2019 and is very likely present in most models' pretraining data, and because this Bangla version is a mechanical translation of that same public source rather than newly authored content, memorisation of the English original could plausibly transfer through translation.

## How to run it

The reference implementation lives in lm-evaluation-harness's shared `lm_eval/tasks/bangla/` directory, in `bangla_commonsenseqa.yaml`, alongside the other Bangla tasks rather than in a directory of its own. The runnable task name declared inside that file is `bangla_commonsenseqa`, which -- unlike the harness's `bangla_boolqa`, `bangla_piqa` and `bangla_openbookqa` tasks, whose internal task names all differ from their filenames -- happens to match this page's id exactly. The harness's own top-level task registry (`lm_eval/tasks/README.md`) separately lists this benchmark under a differently-cased display label, `bangla_commonsenseQA`, recorded here in `aliases`. No HELM, OpenCompass, inspect_evals or BIG-bench implementation was found.

## Reading the numbers

A high Bangla CommonsenseQA score would indicate a model can apply general world knowledge to a Bangla multiple-choice question -- but so far, no evaluated model comes close to a strong score: the best reported result among small models is only 33%, barely above random. That makes the benchmark hard to interpret today: a low score is expected and uninformative on its own, and there is not yet a frontier-model result to anchor what a genuinely strong score would look like. Because this dataset is a machine translation rather than natively authored, treat unusually low scores with some caution and consider whether translation artefacts -- awkward phrasing, lost idioms, or EST's automated candidate-ranking step choosing a less natural option -- could be responsible before concluding a model lacks the underlying commonsense-reasoning skill.
