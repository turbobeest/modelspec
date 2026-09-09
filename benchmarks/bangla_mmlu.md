---
id: bangla_mmlu
name: "Bangla MMLU"
aliases:
  - "BN MMLU"
  - "titulm-bangla-mmlu"
  - "TituLLM Bangla MMLU"
page_kind: benchmark
category: knowledge
subcategory: "Bangla four-choice exam questions from Bangladeshi admissions, HSC and job tests"
status: active
summary: "87,869 Bangla four-choice exam questions from Bangladeshi admissions, HSC and job tests; lm-eval scores the 14,750-item test split."
measures: >
  Bangla MMLU asks a model to pick one of four options for a Bangla multiple-choice question
  drawn from Bangladeshi educational and professional exams. The TituLLMs paper describes it as
  inspired by English MMLU, not as a translation of Hendrycks's 57-subject set. Items were curated
  from open educational sites and textbooks covering university admission, higher secondary, job
  exams, medical admission and engineering admission. The skill is Bangla-medium school and
  professional knowledge, including Bangladesh-specific general knowledge.
task_format: >
  Four-option multiple-choice QA in Bangla. lm-eval task `bangla_mmlu` formats the stem plus
  A–D options and scores by comparing log-likelihoods of the letters. Few-shot examples come
  from the 175-item `dev` split (`sampler: first_n`). Headline split is `test`.
metric:
  name: "accuracy (acc and length-normalised acc_norm)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    Four labelled options, so uniform chance is 25%. The TituLLMs paper reports normalised
    accuracy for models at or below 3B parameters plus GPT-davinci-002. No Bangla human
    baseline was given. Highest figure in that table on Bangla MMLU is 0.35 (Qwen-2.5-1.5B,
    5-shot).
dataset:
  size: 87869
  size_note: >
    Paper and Hugging Face `all` config agree: 175 dev / 14,750 test / 72,944 validation, totalling
    87,869. Figure 5 of the paper breaks the same 87,869 into University Admission 47,394, Higher
    Secondary 25,437, Job Exams 9,122, Medical Admission 3,764, Engineering Admission 2,152.
    lm-eval loads config `all` and scores the 14,750-item test split. Per-subject Hugging Face
    configs also exist; those slice the same pool and must not be added to `all`.
  url: "https://huggingface.co/datasets/hishab/titulm-bangla-mmlu"
  license: ""
  languages:
    - bn
  modalities:
    - text
  splits: "dev (175, few-shot) / test (14,750, lm-eval default) / validation (72,944)"
  public_test_set: true
publisher:
  org: "Hishab Singapore Pte. Ltd., with University of Central Florida and Qatar Computing Research Institute"
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
  predecessor: "mmlu"
  successors: []
  variants:
    - bangla_boolqa
    - bangla_commonsenseqa
    - bangla_openbookqa
    - bangla_piqa
saturation:
  status: open
  top_score: 35.0
  as_of: "2025-02"
  note: >
    The introducing paper only reports models of 3B parameters or fewer, plus GPT-davinci-002.
    Within that set, Bangla MMLU 5-shot normalised accuracy tops out at 35% (Qwen-2.5-1.5B),
    ten points above chance. No frontier-model number was read. That is early, thin evaluation,
    not a saturated ceiling.
contamination:
  risk: high
  note: >
    Items come from published Bangladeshi exams and open educational websites, with answers in
    the public Hugging Face dataset. Exam stems of this kind are widely copied on the web, so
    leakage into pretraining is plausible even though this packaging dates to February 2025.
    No held-out or rotating split is described.
harness:
  lm_eval: "bangla_mmlu"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "YAML lives at lm_eval/tasks/bangla/bangla_mmlu.yaml (directory bangla, not bangla_mmlu)."
tags:
  - knowledge
  - bangla
  - multiple-choice
  - exams
  - mmlu-style
sources:
  - url: "https://arxiv.org/abs/2502.11187"
    title: "TituLLMs paper abstract (arXiv:2502.11187)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2502.11187"
    title: "TituLLMs paper HTML: Table 2 splits, Figure 5 category counts, Table 3 scores"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bangla/bangla_mmlu.yaml"
    title: "lm-eval bangla_mmlu.yaml (hishab/titulm-bangla-mmlu config all, acc/acc_norm)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/bangla/README.md"
    title: "lm-eval bangla/ README (Bangla MMLU listed beside BoolQA, PIQA, CommonsenseQA, OpenBookQA)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/hishab/titulm-bangla-mmlu/raw/main/README.md"
    title: "hishab/titulm-bangla-mmlu dataset card (all-config 175/14750/72944; no licence field)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/hishab/titulm-bangla-mmlu"
    title: "Hugging Face dataset API (language bn, arXiv:2502.11187, no licence tag)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/hishab-nlp/titulm/main/README.md"
    title: "hishab-nlp/titulm README (publisher Hishab; points at a forked lm-eval runner)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-027 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "GPT-5.6 Luna independent review, luna-batch-027"
---

## What it measures

Bangla MMLU is a four-choice knowledge test in Bangla. Each item is a question plus options A–D, taken from Bangladeshi university admission tests, higher-secondary exams, job exams, and medical or engineering admission papers. The TituLLMs paper says the authors curated these from open educational websites and textbooks, "inspired by" English MMLU. It is not a translation of the Hendrycks subjects. A score mainly reflects school- and exam-style knowledge in Bangla, including Bangladesh-specific general knowledge, not the original MMLU item pool.

This is a different dataset from the other four TituLLM benchmarks in this repository. [Bangla BoolQA](bangla_boolqa.md), [Bangla CommonsenseQA](bangla_commonsenseqa.md), [Bangla OpenBookQA](bangla_openbookqa.md) and [Bangla PIQA](bangla_piqa.md) share a paper, not this item pool.

## How it is scored

lm-eval task `bangla_mmlu` is multiple-choice log-likelihood scoring. The prompt concatenates the question and the four options and compares the likelihood of "A", "B", "C" and "D". Metrics are accuracy and length-normalised accuracy. Few-shot uses the first N rows of `dev` (175 items). The paper reports 0-shot and 5-shot normalised accuracy. Chance is 25%. No human baseline was published in the sources opened here.

## Dataset and licence

The paper, Figure 5, and the Hugging Face `all` config all give 87,869 questions: 175 dev, 14,750 test, 72,944 validation. Category totals in Figure 5 sum to the same 87,869. Answers are in the public dataset. A licence was not found: the Hugging Face card and API have no `license` field, and the TituLLM GitHub tree had no LICENSE file at the path tried for this page.

lm-eval scores only the 14,750-item test split of config `all`. Do not add the per-subject configs on top of that number.

## Who publishes it

The TituLLMs paper (arXiv:2502.11187, February 2025) is from Hishab Singapore, with co-authors at the University of Central Florida and Qatar Computing Research Institute. Models and benchmark pointers live at `hishab-nlp/titulm`. The dataset card is `hishab/titulm-bangla-mmlu`. There is no separate maintained leaderboard; published numbers are the paper's small-model table and later lm-eval runs.

## Lineage

English [MMLU](mmlu.md) is the format predecessor, not the source of the questions. The same TituLLMs paper also released the four Bangla commonsense and reading sets already paged in this repository. Those are siblings, not subsets of Bangla MMLU. The census URL `lm_eval/tasks/bangla_mmlu` is wrong: the YAML sits under `lm_eval/tasks/bangla/`.

## Saturation and contamination

Among models the paper actually ran, scores sit in the mid-20s to 35%, barely above chance. That does not tell you where GPT-class systems sit in 2026. Contamination risk is high for a public exam harvest with answers attached. Many of these stems existed on Bangladeshi education sites long before the 2025 packaging.

## How to run it

In EleutherAI lm-evaluation-harness: `--tasks bangla_mmlu`. The task file is `lm_eval/tasks/bangla/bangla_mmlu.yaml`, dataset `hishab/titulm-bangla-mmlu`, config `all`. Hishab's own README points at a fork (`hishab-nlp/lm-evaluation-harness`) and `scripts/bangla_lm_benchmark.py`; a number from that fork is not automatically the same as upstream `bangla_mmlu`. HELM and OpenCompass names were not found.

## Reading the numbers

A 35% 5-shot score on the paper's small models is a weak knowledge signal, not exam mastery. Compare only test-split, four-choice, Bangla numbers, and say whether they are `acc` or `acc_norm`. Do not treat this as English MMLU in translation, and do not average it with Bangla BoolQA or PIQA. Pair it with those siblings if you want a broader Bangla picture, and treat any large jump after 2025 as possibly exam-leakage rather than new competence.
