---
id: med_dialog
name: MedDialog
aliases: []
page_kind: benchmark
category: domain
subcategory: medical dialogue summarization
status: active
summary: MedDialog evaluates concise summaries of English doctor-patient conversations from HealthCareMagic and iCliniq.
measures: MedDialog presents a medical dialogue and asks a model to produce a one-sentence summary of the patient question or exchange. It covers English conversations between patients and doctors.
task_format: Dialogue input followed by a reference summary; generate a concise medical summary.
metric: {name: med_dialog_accuracy, direction: higher_is_better, unit: "", max_score: null, random_baseline: null, human_baseline: null, baseline_note: "HELM names the metric but does not define its formula in the scenario."}
dataset: {size: 260000, size_note: "HELM describes about 0.26 million English dialogues; its cited preprocessing gives HealthCareMagic 226,405 and iCliniq 31,064 examples across train, validation, and test.", url: https://github.com/UCSD-AI4H/Medical-Dialogue-System, license: "", languages: [English], modalities: [text], splits: train, validation, test, public_test_set: true}
publisher: {org: UCSD AI4H / MedDialog authors, authors: [Shu Chen, Zeqian Ju, Xiangyu Dong, Hongchao Fang, Sicheng Wang, Yue Yang, Jiaqi Zeng, Ruisi Zhang, Ruoyu Zhang, Meng Zhou, Penghui Zhu, Pengtao Xie], url: https://github.com/UCSD-AI4H/Medical-Dialogue-System}
paper: {title: "MedDialog: a large-scale medical dialogue dataset", arxiv: "2004.03329", url: https://arxiv.org/abs/2004.03329, year: 2020}
leaderboard_url: ""
repo_url: https://github.com/UCSD-AI4H/Medical-Dialogue-System
released: "2020"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: [med_dialog_healthcaremagic, med_dialog_icliniq]}
saturation: {status: unknown, top_score: null, as_of: "", note: No current authoritative leaderboard was established.}
contamination: {risk: medium, note: The source describes public web-origin dialogues, but current model exposure is not established.}
harness: {lm_eval: "", inspect_evals: "", helm: med_dialog, opencompass: "", bigbench: "", other: ""}
tags: [medical, dialogue, summarization]
sources:
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/med_dialog_scenario.py
    title: HELM MedDialog scenario
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2004.03329
    title: MedDialog paper
    accessed: "2026-09-08"
  - url: https://github.com/UCSD-AI4H/Medical-Dialogue-System
    title: MedDialog repository
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-batch-057 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-batch-057"}
---

## What it measures

MedDialog evaluates medical dialogue summarization. A model reads a conversation between a patient and doctor and generates a concise summary of the central question or exchange. HELM describes English data from HealthCareMagic and iCliniq.

The two sources have different dialogue styles. The scenario notes that HealthCareMagic summaries are more abstractive and formal, while iCliniq summaries are more patient-written.

## How it is scored

HELM names `med_dialog_accuracy` as its main metric and uses the generated test summary as the correct reference. The scenario does not define the metric formula or normalization, so scores should not be interpreted as a particular ROUGE, BLEU, or semantic metric without the active HELM evaluator configuration.

## Dataset and licence

HELM describes about 0.26 million English dialogues. Its cited preprocessing table gives HealthCareMagic 181,122 train, 22,641 validation, and 22,642 test examples; iCliniq has 24,851 train, 3,105 validation, and 3,108 test examples. The source says the raw dialogues come from healthcaremagic.com and icliniq.com and that their copyrights belong to those sites. A redistribution licence was not established.

## Who publishes it

The benchmark paper is by Chen and colleagues, published as arXiv:2004.03329. UCSD AI4H previously maintained the linked code repository, but as of 2026-09-08 `github.com/UCSD-AI4H/Medical-Dialogue-System` returns a 404 rather than redirecting; the account no longer resolves. HELM provides a scenario that downloads the test data directly from a CodaLab bundle, independent of that repository. No current standalone leaderboard was established.

## Lineage

MedDialog is a standalone dataset with HealthCareMagic and iCliniq subsets. The sources do not establish a successor benchmark.

## Saturation and contamination

Saturation is unknown. The dialogues originate from public healthcare websites, so exposure is plausible, but no model-training analysis was found. Copyright and privacy considerations also make dataset handling material to reproducibility.

## How to run it

HELM’s `med_dialog` scenario takes a `healthcaremagic` or `icliniq` subset, downloads its test JSON, and creates dialogue-to-summary instances. It uses the test split only for the zero-shot scenario. Record the subset and active HELM metric implementation.

## Reading the numbers

A strong score indicates concise content preservation on these medical conversations. It does not establish clinical safety, factual correctness, or suitability for patient communication. Compare subsets separately because their writing styles and summary properties differ.
