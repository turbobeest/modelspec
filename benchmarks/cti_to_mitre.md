---
id: cti_to_mitre
name: "CTI-to-MITRE"
aliases:
  - "CTI to MITRE"
  - "cti-to-mitre-with-nlp"
page_kind: benchmark
category: domain
subcategory: "multiple-choice mapping of CTI sentences to MITRE ATT&CK enterprise techniques"
status: unknown
summary: "HELM multiple-choice wrap that maps a short cyber threat intelligence sentence to a MITRE ATT&CK enterprise technique name."
measures: >
  HELM scenario cti_to_mitre turns Orbinato et al. 2022's CTI-to-technique
  classification into a generative multiple-choice task. The model sees one
  English sentence describing attacker behaviour and must pick the ATT&CK
  enterprise technique name from a lettered list. The source dataset labels
  sentences with technique IDs; HELM maps those IDs to names using MITRE
  ATT&CK v10.1 enterprise-attack.json. This is static text classification, not
  an agent writing detections. It is not [cti_realm](cti_realm.md).
task_format: >
  Multiple-choice joint adaptation. HELM run spec default: num_options=10,
  seed=42, max_train_instances=10, instruction "Classify the following
  situation by the type of security attack. Answer with only a single letter."
  The last option is Others when the list is shorter than the full category
  set. Scenario code default num_options is 199 (all enterprise technique
  categories in the v10.1 zip), which is not the run-spec default.
metric:
  name: exact_match (HELM run spec; scenario metadata also names quasi_exact_match)
  direction: higher_is_better
  unit: "%"
  max_score: 100.0
  random_baseline: 10.0
  human_baseline: null
  baseline_note: >
    Uniform chance is 1/num_options. The HELM run spec default is 10 options
    (10%). Using all 199 categories would make chance about 0.5%. No human
    baseline is in the HELM scenario or in the ISSRE paper's LLM protocol,
    which originally scored classical and deep classifiers, not GPT-style
    multiple choice.
dataset:
  size: 12945
  size_note: >
    Paper Table I: 12,945 sentence-level samples covering 188 ATT&CK
    techniques, 7,881 unique words. HELM downloads
    dessertlab/cti-to-mitre-with-nlp dataset.csv at commit
    a8cacf3185d098c686e0d88768a619a03a4d76d1. Both that commit and GitHub
    main expose a 132-byte Git LFS pointer to the same object
    (sha256:f4f8830…, size 1,847,828 bytes), not a truncated replacement
    file. HELM counts 199 enterprise technique categories in ATT&CK v10.1,
    which does not match the paper's 188. Row count of the LFS payload was
    not independently verified here.
  url: "https://github.com/dessertlab/cti-to-mitre-with-nlp"
  license: "CC BY-SA 4.0"
  languages:
    - en
  modalities:
    - text
  splits: "HELM: 70% train / 30% test, shuffled with seed 42; paper also has a document-level set not used by this scenario"
  public_test_set: true
publisher:
  org: "DIETI, Università degli Studi di Napoli Federico II, and University of Bern (HELM scenario by Stanford CRFM)"
  authors:
    - "Vittorio Orbinato"
    - "Mariarosaria Barbaraci"
    - "Roberto Natella"
    - "Domenico Cotroneo"
  url: "https://github.com/dessertlab/cti-to-mitre-with-nlp"
paper:
  title: "Automatic Mapping of Unstructured Cyber Threat Intelligence: An Experimental Study"
  arxiv: "2208.12144"
  url: "https://arxiv.org/abs/2208.12144"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/cti_to_mitre_scenario.py"
released: "2022-08"
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
    No HELM leaderboard cell for cti_to_mitre was opened. The ISSRE paper
    reports classical and neural classifiers on a different protocol, not
    this multiple-choice wrap, so those figures are not copied here.
contamination:
  risk: medium
  note: >
    Sentences are public CTI paraphrases shipped on GitHub since 2022. HELM
    holds out 30% only after a seeded shuffle of that public file. ATT&CK
    technique names are themselves widely copied into training data.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "cti_to_mitre"
  opencompass: ""
  bigbench: ""
  other: >
    Run spec name cti_to_mitre:num_options={n},seed={s},method={m}. Default n=10,
    seed=42, method multiple_choice_joint. inspect_evals does not ship this
    scenario; CTI-REALM is a different task.
tags:
  - cybersecurity
  - classification
  - mitre-attack
  - helm
  - cti
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/cti_to_mitre_scenario.py"
    title: "HELM CtiToMitreScenario (199 options, 70/30 split, pinned CSV)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/enterprise_run_specs.py"
    title: "HELM enterprise run spec cti_to_mitre (default 10 options, 10-shot)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2208.12144"
    title: "Orbinato et al. ISSRE 2022 paper abs (CC BY 4.0 on arXiv)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2208.12144"
    title: "Paper HTML (Table I: 12,945 samples, 188 techniques; affiliations)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/dessertlab/cti-to-mitre-with-nlp/main/README.md"
    title: "dessertlab/cti-to-mitre-with-nlp README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/dessertlab/cti-to-mitre-with-nlp/main/LICENSE"
    title: "dessertlab CC BY-SA 4.0"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/LICENSE"
    title: "HELM Apache License 2.0"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-036 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-036"
---

## What it measures

cti_to_mitre asks a model to name the MITRE ATT&CK enterprise technique described in one English sentence. HELM shows a short “Situation:” line and a lettered list of technique names. The gold label is the category name for `label_tec`, looked up in ATT&CK v10.1. The model must answer with a letter.

This is not [cti_realm](cti_realm.md). CTI-REALM is an agent that writes Sigma and KQL against telemetry. It is also not TRAM, the CTID baseline classifier cited in the 2022 paper.

## How it is scored

HELM reports exact match on the letter (run spec `get_exact_match_metric_specs`). Scenario metadata names `quasi_exact_match` as the main metric. Default HELM runs use 10 options and 10 in-context items. Chance is then 10%, not 0.5%. The scenario class itself defaults to 199 options if you construct it without the run spec. Those two defaults will not match. The ISSRE paper scored SVM, CNN, LSTM, and similar models on the original label set, not this lettered wrap.

## Dataset and licence

Orbinato, Barbaraci, Natella, and Cotroneo released 12,945 sentence-level samples covering 188 techniques (paper Table I), plus a document-level set HELM does not use. Licence on the GitHub repo is CC BY-SA 4.0. HELM pins `dataset.csv` at commit a8cacf3 and a MITRE v10.1 JSON. GitHub main and that commit both serve a Git LFS pointer (132 bytes) to a 1,847,828-byte object, not an emptied replacement file. HELM’s 199 v10.1 categories do not match the paper’s 188 techniques. The 70/30 split is HELM’s, not a published author split.

## Who publishes it

The dataset paper is ISSRE 2022 / arXiv:2208.12144, from DIETI at Università degli Studi di Napoli Federico II (Orbinato, Natella, Cotroneo) and the University of Bern (Barbaraci). Stanford CRFM added the HELM scenario. There is no separate live leaderboard page that was opened here.

## Lineage

Predecessor: the dessertlab CTI-to-MITRE classification study, which itself compares to TRAM. [cti_realm](cti_realm.md) is a later agent bench from Microsoft Security AI, not a successor of this HELM wrap. No other variant id is in this repository.

## Saturation and contamination

No current HELM score table was opened, so saturation is unknown. The sentences and ATT&CK names have been public since 2022. A high exact-match on 10 options can be option-set luck as much as CTI skill.

## How to run it

HELM: run spec `cti_to_mitre` in `enterprise_run_specs.py`. Record `num_options`, `seed`, and `method` in the run name. inspect_evals and lm-eval do not ship this scenario. Do not drop HELM numbers next to the paper’s classifier F1.

## Reading the numbers

A 70% exact-match with 10 options is not a 70% 188-way technique classifier. Check `num_options` before ranking models. `Others` is never the gold label in the sampler, so a model that picks Others always scores zero. Read [cti_realm](cti_realm.md) if the claim is about writing detections, not naming a technique from a sentence.
