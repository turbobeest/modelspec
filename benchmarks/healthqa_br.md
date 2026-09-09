---
id: healthqa_br
name: "HealthQA-BR (HELM)"
aliases:
  - "HealthQA-BR"
  - "healthqa-br"
  - "Larxel/healthqa-br"
page_kind: benchmark
category: domain
subcategory: "Brazilian public-health multiple-choice exams (Revalida and Enare)"
status: active
summary: "HELM wrap of HealthQA-BR: 5,632 Portuguese multiple-choice items from Brazilian medical licensing and residency exams."
measures: >
  healthqa_br is Stanford CRFM HELM's scenario over HealthQA-BR, a Portuguese
  multiple-choice set of Brazilian public-health exams. The model reads a
  question plus lettered options and must select the correct alternative.
  Items come from Revalida (revalidation of foreign medical diplomas) and
  Enare (national residency, medical and multiprofessional). Unlike USMLE-style
  English medical quizzes, the set covers medicine and allied professions in
  the Sistema Único de Saúde (nursing, dentistry, psychology, social work,
  pharmacy, physiotherapy, and others). This id is HELM's wrap, not the
  authors' own letter-only generation script, and not [healthbench](healthbench.md)
  or [medqa](medqa.md).
task_format: >
  HELM multiple-choice joint adaptation (ADAPT_MULTIPLE_CHOICE_JOINT).
  Portuguese instructions include one worked insulin/pancreas example and ask
  for a letter only. Input noun Pergunta, output noun Resposta. Default
  adapter max_train_instances is 5 and max_tokens is 1, but the scenario labels
  every instance TEST_SPLIT, so the realized shot count is not established
  from these files. The paper instead used zero-shot generation of a single
  letter A–E.
metric:
  name: exact_match
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 21.89
  human_baseline: null
  baseline_note: >
    The paper's chance floor is the most-common-answer rate 21.89% (option A),
    not 20% uniform. Official Revalida/Enare cut-offs are described as typically
    60–65%. No human-physician accuracy on this item set is published. HELM
    scores exact match via get_exact_match_metric_specs(); the paper reports
    accuracy on generated letters. GPT 4.1 reached 0.8661 overall in the paper's
    zero-shot protocol (2025-06), which is not a HELM cell.
dataset:
  size: 5632
  size_note: >
    5,632 rows in Larxel/healthqa-br train, confirmed by the dataset card, the
    paper, and the Hugging Face size API (one default config, split named
    train). Composition: Revalida 1,777; Enare Residência Médica 2,691; Enare
    Multiprofissional 1,164. HELM maps that train split to its test split and
    skips a row when the gold letter is missing from parsed options. The paper
    states every item has five choices; the Hugging Face card says some items
    have only four — unresolved here. Years span 2011–2025. Answer letter A is
    the mode at 21.89%.
  url: "https://huggingface.co/datasets/Larxel/healthqa-br"
  license: "CC-BY-4.0"
  languages:
    - pt
  modalities:
    - text
  splits: "Hugging Face train (5,632) used as HELM test; no separate held-out split"
  public_test_set: true
publisher:
  org: "Andrew Maranhão Ventura D'addario (dataset); Stanford CRFM (HELM scenario)"
  authors:
    - "Andrew Maranhão Ventura D'addario"
  url: "https://huggingface.co/datasets/Larxel/healthqa-br"
paper:
  title: "HealthQA-BR: A System-Wide Benchmark Reveals Critical Knowledge Gaps in Large Language Models"
  arxiv: "2506.21578"
  url: "https://arxiv.org/abs/2506.21578"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/healthqa_br_scenario.py"
released: "2025-06"
last_updated: "2025-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 86.61
  as_of: "2025-06"
  note: >
    Paper zero-shot overall accuracy: GPT 4.1 86.61%, DeepSeek R1 85.26%,
    GPT 4o 84.89%. The authors stress specialty gaps under that headline
    (GPT 4.1 ophthalmology 98.7% versus neurosurgery 60.0% and social work
    68.4%). No HELM leaderboard cell was read. 86.61 is the paper protocol,
    not HELM exact_match.
contamination:
  risk: high
  note: >
    Items are public national exams with published answer keys, released as
    an ungated parquet with gold letters since June 2025 (card created
    2025-06-16). Source PDFs go back to 2011. HELM and the paper both use
    the public labels. No held-out private split is described.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "healthqa_br"
  opencompass: ""
  bigbench: ""
  other: >
    Run spec src/helm/benchmark/run_specs/healthqa_br_run_specs.py; scenario
    class HEALTHQA_BR_Scenario; dataset Larxel/healthqa-br. No OpenCompass or
    lm-eval task with this id was found.
tags:
  - medical
  - portuguese
  - multiple-choice
  - exam
  - helm
  - brazil
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/healthqa_br_scenario.py"
    title: "HELM HEALTHQA_BR_Scenario (Larxel/healthqa-br, train mapped to test)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/healthqa_br_run_specs.py"
    title: "HELM healthqa_br run spec (joint MC, exact_match, Portuguese instructions)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Larxel/healthqa-br/raw/main/README.md"
    title: "Larxel/healthqa-br dataset card (5,632 items, CC-BY-4.0, GPT 4.1 0.8661)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/Larxel/healthqa-br"
    title: "Hugging Face dataset API for Larxel/healthqa-br (license, arXiv:2506.21578)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=Larxel/healthqa-br"
    title: "Hugging Face size API (5,632 train rows)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2506.21578"
    title: "HealthQA-BR paper abs (submitted 2025-06-16)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2506.21578"
    title: "HealthQA-BR paper HTML (zero-shot letter protocol, 21.89% mode baseline)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/adaptation/common_adapter_specs.py"
    title: "HELM get_multiple_choice_adapter_spec defaults (max_train_instances=5)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-047 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-047"
---

## What it measures

The model answers Portuguese multiple-choice questions drawn from Brazilian professional exams, not USMLE-style English items. Sources are Revalida (INEP exam for doctors trained abroad) and Enare (Ebserh residency exam), including the multiprofessional track used in the public health system. The skill is exam-style clinical knowledge across medicine and allied fields. The HELM scenario splits the concatenated question string into a stem and `'A': '…'`-style options, then scores a joint multiple-choice completion. It is not a dialogue or rubric-graded consultation test.

## How it is scored

HELM reports exact match from `get_exact_match_metric_specs()` under joint multiple-choice adaptation. Instructions are in Portuguese and already contain one worked example. The paper's own numbers are zero-shot letter accuracy with a fixed generation setup described only as held constant, with details in supplementary material not opened here. The paper's chance floor is 21.89% (most common key), and passing-style cut-offs are given as about 60–65%. Do not mix a HELM exact_match row with the paper table without naming the protocol.

## Dataset and licence

The hosted set has 5,632 items: 1,777 Revalida, 2,691 Enare medical, 1,164 Enare multiprofessional. Hugging Face exposes a single `train` split; HELM uses it as test. Gold letters are in the file. Licence is CC-BY-4.0 on the card and in the paper's author-accepted-manuscript note. One disagreement is option count: the paper says five choices each; the card says some items have four. The scenario drops an item if the gold letter is not among parsed options, so HELM's n may be below 5,632. Questions were parsed from public PDFs, checked against official keys, de-duplicated, and audited on a 1.5% sample (82 items) with no errors reported.

## Who publishes it

Andrew Maranhão Ventura D'addario released the dataset and paper on 16 June 2025 (arXiv:2506.21578). Funding lines name Brazil's Ministry of Health (MS/DECIT), CNPq grant 400757/2024-9, and the Gates Foundation. The Hugging Face owner is Larxel. Stanford CRFM added the HELM scenario and run spec. No continuously updated official leaderboard was found beyond the paper table.

## Lineage

The work is framed against English medical exams that hide specialty and interprofessional gaps. It is not [healthbench](healthbench.md), [medqa](medqa.md), or [medi_qa](medi_qa.md). No successor id exists in this repository.

## Saturation and contamination

Under the paper's zero-shot protocol, GPT 4.1 reached 86.61% overall in June 2025, with DeepSeek R1 and GPT 4o close behind. The authors treat that headline as too coarse because specialty scores still swing widely. HELM saturation is not established. Contamination risk is high: these are public exams with keys, now in an ungated dataset, including items from 2011 onward.

## How to run it

HELM run spec name `healthqa_br` loads `HEALTHQA_BR_Scenario`. Adapter method is joint multiple choice with Portuguese instructions. Default `max_train_instances` is 5, but only the test split is populated. The paper's letter-only script is a different protocol. No lm-eval, inspect_evals, OpenCompass, or BIG-bench task named `healthqa_br` was found.

## Reading the numbers

A high score means the model matches the official key on these Brazilian exam stems, including non-physician professions. It does not mean safe clinical use, diagnostic skill, or English USMLE competence. Prefer specialty breakdowns over one overall figure, as the paper argues. Say whether the number is HELM exact_match or the authors' zero-shot letter accuracy. Watch the four- versus five-option discrepancy and any HELM rows skipped when option parsing fails.
