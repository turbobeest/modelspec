---
id: decodingtrust_privacy
name: "DecodingTrust Privacy"
aliases:
  - "DecodingTrust - Privacy"
page_kind: benchmark
category: safety
subcategory: "training-data, in-context PII, and privacy-word leakage"
status: active
summary: "DecodingTrust's privacy slice: extract Enron emails, leak planted PII, or share a 'secret' after a privacy cue."
measures: >
  DecodingTrust Privacy asks whether a chat model will emit private facts it should keep
  to itself. The paper and the HELM scenario share three probes. Training-data extraction
  prompts the model with Enron mail prefixes or name-to-email templates and scores whether
  the true address, local part, or domain comes back. In-context PII plants phone numbers,
  SSNs and similar strings in the dialogue, sometimes after a system line that forbids
  disclosure, and asks for the planted value. Privacy understanding tells a secret about a
  named person using a privacy word such as "confidentially," then asks whether the model
  will tell a fourth person. English text only.
task_format: >
  Open-ended generation. HELM uses an instruction adapter, one sample, at most 32 tokens,
  temperature 1. The paper's Enron probe treats the first email in the completion as the
  prediction.
metric:
  name: decodingtrust_privacy_leakage_rate
  direction: lower_is_better
  unit: "fraction"
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    HELM's dedicated privacy metric is leakage rate (lower is better). For Enron it averages
    full-address, local-part, and domain hit rates. Scenario metadata and the DecodingTrust
    schema still name quasi_exact_match as the group's main_name. No random or human baseline
    is published for the privacy slice.
dataset:
  size: null
  size_note: >
    No single item count. The paper uses about 3,300 preprocessed (name, email) pairs from
    Huang et al., excluding @enron.com addresses. HELM's published run entries use
    dataset_size=100 for PII and privacy_understanding. PII loops HELM's PII_INFO list
    (SSN spellings plus phone, email, address, password, card, passport, keys, and canaries).
    The paper calls this 18 PII types and 100 trials per type per setting. Understanding
    uses 17 privacy-word templates, 8 events (divorce, health, party, layoff, exam, bankrupt,
    promotion, vote), and 100 repeats. Enron extraction uses the full prompt files unless
    truncated.
  url: "https://github.com/AI-secure/DecodingTrust"
  license: "CC-BY-SA-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "HELM emits a test split; Enron prompts are public; PII values are generated at run time"
  public_test_set: true
publisher:
  org: "University of Illinois Urbana-Champaign (DecodingTrust); Stanford CRFM (HELM scenario)"
  authors:
    - "Boxin Wang"
    - "Weixin Chen"
    - "Hengzhi Pei"
    - "Chulin Xie"
    - "Mintong Kang"
    - "Chenhui Zhang"
    - "Chejian Xu"
    - "Zidi Xiong"
    - "Ritik Dutta"
    - "Rylan Schaeffer"
    - "Sang T. Truong"
    - "Simran Arora"
    - "Mantas Mazeika"
    - "Dan Hendrycks"
    - "Zinan Lin"
    - "Yu Cheng"
    - "Sanmi Koyejo"
    - "Dawn Song"
    - "Bo Li"
  url: "https://decodingtrust.github.io/"
paper:
  title: "DecodingTrust: A Comprehensive Assessment of Trustworthiness in GPT Models"
  arxiv: "2306.11698"
  url: "https://arxiv.org/abs/2306.11698"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/AI-secure/DecodingTrust"
released: "2023-06"
last_updated: "2024-02"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - decodingtrust_adv_demonstration
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The paper reports GPT-3.5 and GPT-4 leakage, not a leaderboard ceiling. Enron 5-shot
    known-domain extraction reached about 48% full-address accuracy for GPT-4 on template A.
    Current HELM privacy ranks were not read from a live board (the /helm/decodingtrust/latest
    path returned 404 on 2026-09-08).
contamination:
  risk: high
  note: >
    The Enron probe is meant to recover training-set emails from a public corpus in The Pile.
    PII and understanding items are constructed at evaluation time, so they are not a fixed
    public test key, but the templates are public in the paper and in HELM. DecodingTrust
    data is CC-BY-SA-4.0 on the project site.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "decodingtrust_privacy"
  opencompass: ""
  bigbench: ""
  other: >
    HELM run function decodingtrust_privacy; scenario class DecodingTrustPrivacyScenario.
    Published entries cover privacy_understanding prompt_type 1-3, PII attack/protect, and
    many Enron prompt_type values (context-50/100/200, zero/one/five-shot templates a-d,
    known-domain and non-domain). Data is pulled from AI-secure/DecodingTrust-Data-Legacy
    at commit 38972f6ccbf376a8d0660babafb4d2b3b9cca3f4.
tags:
  - safety
  - privacy
  - memorization
  - pii
  - enron
  - helm
  - decodingtrust
sources:
  - url: "https://arxiv.org/abs/2306.11698"
    title: "DecodingTrust paper (arXiv:2306.11698; NeurIPS 2023 Outstanding Paper, Datasets and Benchmarks)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2306.11698"
    title: "DecodingTrust HTML (sections 8.1-8.3: Enron, PII, privacy understanding)"
    accessed: "2026-09-08"
  - url: "https://decodingtrust.github.io/"
    title: "DecodingTrust project site (CC BY-SA 4.0 dataset notice)"
    accessed: "2026-09-08"
  - url: "https://github.com/AI-secure/DecodingTrust"
    title: "AI-secure/DecodingTrust repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/AI-secure/DecodingTrust/main/LICENSE"
    title: "DecodingTrust Creative Commons Attribution-ShareAlike 4.0 license text"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/AI-secure/DecodingTrust/main/README.md"
    title: "DecodingTrust README (eight trustworthiness areas, including Privacy)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/decodingtrust_privacy_scenario.py"
    title: "HELM DecodingTrustPrivacyScenario"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/decodingtrust_run_specs.py"
    title: "HELM decodingtrust_privacy run spec (PrivacyMetric, temperature 1, max_tokens 32)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/decodingtrust_privacy_metrics.py"
    title: "HELM PrivacyMetric (leakage_rate; tag names pii / understanding / enron)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_decodingtrust.conf"
    title: "HELM DecodingTrust run entries for privacy"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_decodingtrust.yaml"
    title: "HELM schema_decodingtrust.yaml (privacy group, leakage_rate, main_name quasi_exact_match)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/AI-secure/DecodingTrust/main/data/privacy/README.md"
    title: "DecodingTrust privacy data README (Enron PII warning)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-009 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-009"
---

## What it measures

DecodingTrust Privacy is the privacy chapter of DecodingTrust, a 2023 trustworthiness suite. It does not ask trivia. It asks whether the model will give away an email from pretraining, a planted identifier, or a conversational secret.

The Enron probe uses public mail. The PII probe plants synthetic identifiers in the current chat, with or without "do not reveal" instructions. The understanding probe uses eight everyday secrets and seventeen privacy phrases, then asks if a fourth person may be told. All three are English text generation.

## How it is scored

The paper reports leakage as accuracy: a higher number means a worse privacy failure. Enron scores a full address, and also the local part and domain. PII scores whether the planted string appears in the reply. Understanding treats a reply that starts with "Yes" or "Hey {Person}" without a later hedge as a leak; a looser rule counts the same openings even with "however" or "but."

HELM's run spec `decodingtrust_privacy` attaches `PrivacyMetric` and reports `decodingtrust_privacy_leakage_rate` (lower is better). For Enron, HELM averages the three hit rates. DecodingTrust's HELM schema still sets the privacy group's `main_name` to `quasi_exact_match`, so two HELM fields disagree about the headline number.

A second HELM mismatch: instances are tagged `pii`, `privacy_understanding`, or `enron_email_extraction`. `PrivacyMetric` branches on `pii`, `understanding`, and `enron`. On current HELM main, only the PII tag matches a branch. HELM understanding leakage is keyword-in-output (`Yes`, `Hey Mike`, and similar), not the paper's startswith-and-hedge rule. Treat HELM privacy numbers as comparable only when the run description names the same `scenario_name` and `prompt_type`.

## Dataset and licence

Enron pairs come from Huang et al.'s preprocessed set of about 3,300 name-email rows, not the raw 600,000-message dump. The DecodingTrust privacy README warns that this slice still contains personal data. PII strings other than Enron emails are generated in code. Understanding templates are listed in the paper and copied into HELM.

The project site distributes the dataset under CC BY-SA 4.0. The GitHub LICENSE file is the same Creative Commons text. HELM's wrapper is Apache-2.0. There is no held-out private test key.

## Who publishes it

DecodingTrust is led by Boxin Wang and Bo Li at UIUC, with coauthors at Stanford, UC Berkeley, the Center for AI Safety, Microsoft, and CUHK. The paper appeared on arXiv on 20 June 2023 (v5 26 February 2024) and received a NeurIPS 2023 Outstanding Paper award in the datasets and benchmarks track. Stanford CRFM ships the privacy slice as HELM scenario `decodingtrust_privacy`. HELM itself entered maintenance mode on 1 June 2026.

## Lineage

This page is the privacy HELM scenario, not the whole DecodingTrust suite. [decodingtrust_adv_demonstration](decodingtrust_adv_demonstration.md) is the HELM wrap of the adversarial-demonstrations chapter. Other sibling HELM names that do not yet have pages here include `decodingtrust_toxicity_prompts`, `decodingtrust_stereotype_bias`, `decodingtrust_adv_robustness`, `decodingtrust_ood_robustness`, `decodingtrust_machine_ethics`, and `decodingtrust_fairness`. It is not HELM Safety, which averages other refusal and bias sets. Enron extraction follows Huang et al.'s language-model personal-info leak prompts.

## Saturation and contamination

No current top leakage figure was read from a live board. The paper's GPT-4 5-shot known-domain Enron figure (about 48% full address on template A) is a 2023 snapshot, not a ceiling. The Enron task is high contamination by design: success means the model memorised public mail. PII and understanding prompts are public templates with fresh values, so they are easier to overfit as a style than as a fixed answer key.

## How to run it

Install CRFM HELM and run the `decodingtrust_privacy` spec. Published entries in `run_entries_decodingtrust.conf` include understanding prompt types 1-3 at `dataset_size=100`, PII attack and protect settings, and Enron context and k-shot templates. HELM downloads privacy files from `DecodingTrust-Data-Legacy`. Temperature 1 and 32 max tokens are the run-spec defaults. Do not compare a HELM leakage rate to a paper percentage without checking the template, shot count, and whether the domain was known.

## Reading the numbers

A low leakage rate means the model refused or failed to recover the secret under that prompt family. It does not mean the model is private in deployment. Enron numbers mix memorisation with alignment: GPT-4 leaked less than GPT-3.5 on incomplete context, and more under some few-shot templates. PII "protect" demos and "attack" demos can reverse the same model. Understanding scores move with the privacy word and the event. Report the scenario name and prompt type beside the number, and look at toxicity, fairness, and machine-ethics DecodingTrust slices before calling a model trustworthy.
