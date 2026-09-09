---
id: mental_health
name: "MentalHealth (MedHELM)"
aliases:
  - "MedHELM MentalHealth"
  - "mental_health_accuracy"
page_kind: benchmark
category: domain
subcategory: "counseling-response generation (LLM jury)"
status: active
summary: "MedHELM's private counseling task: generate the next English counselor turn from dialogue history and score it with an LLM jury."
measures: >
  This id is HELM's mental_health scenario in MedHELM, not a public therapy
  dataset and not a psychiatric diagnostic exam. The model reads an English
  conversation history labelled with counselor and client turns, plus topic and
  dialogue-type fields, and must write the next counselor response. HELM scores
  that text with an LLM jury on accuracy, completeness and clarity. Inputs and
  outputs are English text.
task_format: >
  Generation. Instruction: "Given a mental health conversation history, generate
  an empathetic and appropriate counselor response." Output noun Counselor
  response. max_tokens 512 in the run spec; some MedHELM private entries raise
  num_output_tokens to 4000. The scenario emits only TEST_SPLIT. get_generation_adapter_spec
  defaults to five train instances, but no train split exists, so the protocol is
  effectively zero-shot.
metric:
  name: "mental_health_accuracy (HELM LLM-jury average of accuracy, completeness, clarity, each 1-5)"
  direction: higher_is_better
  unit: "points"
  max_score: 5
  random_baseline: null
  human_baseline: null
  baseline_note: >
    schema_medhelm.yaml display name is MentalHealth Jury Score. Each of three
    judges rates accuracy, completeness and clarity on a 1-5 scale against the gold
    counselor turn. The MedHELM paper states the jury score is the mean of those
    nine ratings. The metric uses default_score 1.0 when a jury score is missing.
    HELM also attaches summarization metrics (BERTScore with distilbert-base-uncased).
    No random or human baseline for this jury protocol is stated in the scenario file.
dataset:
  size: null
  size_note: >
    The scenario docstring says the set includes 7 complete dialogues covering
    topics such as workplace issues, anxiety, suicidal thoughts and relationship
    problems. Each scored instance is a counselor turn with prior context, so the
    instance count is not established from the public file. HELM reads a caller
    supplied CSV with columns context, gold_counselor_response, topic and
    dialogue_type. Official private runs point at
    /share/pi/nigam/data/medhelm/mental_health/processed_dialogues.csv. Appendix C
    of arXiv:2505.23802v2 lists the benchmark as Private and New.
  url: ""
  license: ""
  languages:
    - en
  modalities:
    - text
  splits: "HELM test-only from a private CSV; instance count not published in opened sources"
  public_test_set: false
publisher:
  org: "Stanford CRFM and collaborators (MedHELM)"
  authors:
    - "Suhana Bedi"
    - "Hejie Cui"
    - "Miguel Fuentes"
    - "Alyssa Unell"
  url: https://crfm.stanford.edu/helm/medhelm/latest
paper:
  title: "MedHELM: Holistic Evaluation of Large Language Models for Medical Tasks"
  arxiv: "2505.23802"
  url: https://arxiv.org/abs/2505.23802
  year: 2025
leaderboard_url: https://crfm.stanford.edu/helm/medhelm/latest
repo_url: https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/mental_health_scenario.py
released: "2025-05"
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
    The MedHELM paper heatmap is normalized 0-1 for display and reports pairwise
    model gaps; it is not a raw jury ceiling. No numeric MentalHealth Jury Score
    top was read from the JavaScript leaderboard.
contamination:
  risk: low
  note: >
    MedHELM marks the benchmark private and new. The CSV is not on Hugging Face.
    That does not make counselor-style English immune to generic therapy-text
    overlap, only to wholesale copying of this file.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "mental_health"
  opencompass: ""
  bigbench: ""
  other: >
    Run spec mental_health in medhelm_run_specs.py. Annotator
    MentalHealthAnnotator (LLM-as-jury). Official entries in
    run_entries_medhelm_private_stanford.conf with data_path to processed_dialogues.csv.
tags:
  - medical
  - counseling
  - generation
  - llm-judge
  - helm
  - medhelm
  - private
sources:
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/mental_health_scenario.py
    title: "HELM mental_health_scenario.py"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/medhelm_run_specs.py
    title: "HELM medhelm_run_specs.py (mental_health run spec)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/annotation/mental_health_annotator.py
    title: "HELM MentalHealthAnnotator (1-5 accuracy, completeness, clarity)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_medhelm.yaml
    title: "HELM schema_medhelm.yaml (mental_health_accuracy)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries_medhelm_private_stanford.conf
    title: "HELM private Stanford MedHELM run entries (processed_dialogues.csv)"
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/2505.23802
    title: "MedHELM paper (arXiv:2505.23802)"
    accessed: "2026-09-08"
  - url: https://arxiv.org/html/2505.23802v2
    title: "MedHELM HTML (Appendix C: MentalHealth Private, New; jury mean of nine 1-5 ratings)"
    accessed: "2026-09-08"
  - url: https://crfm.stanford.edu/helm/medhelm/latest/
    title: "HELM MedHELM leaderboard shell (JavaScript; no numeric cells in HTML)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-058 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-058"
---

## What it measures

`mental_health` is MedHELM's counseling-response task. The model sees prior English turns between a counselor and a client, tagged with a topic and a dialogue type, and must write the next counselor utterance. HELM's prompt asks for an empathetic, appropriate reply. The gold is the recorded counselor turn in the private CSV. The skill is therapeutic reply writing, not diagnosis coding or exam QA.

The scenario docstring mentions seven complete dialogues and topics such as workplace stress, anxiety, suicidal thoughts and relationships. Those dialogues are not in the public HELM tree. Appendix C of arXiv:2505.23802v2 lists MentalHealth as Private and New.

## How it is scored

The headline metric is `mental_health_accuracy`, an LLM-jury average. The MedHELM methods section uses a three-model jury (GPT-4o, Claude 3.7 Sonnet, Llama 3.3 70B in that paper) scoring accuracy, completeness and clarity from 1 to 5, then takes the mean of the nine ratings. Missing jury output falls back to 1.0. HELM also logs summarization overlap, including BERTScore with `distilbert-base-uncased`. The paper's heatmap is a 0-1 normalisation of those scores. No random or human baseline for this protocol was stated in the opened files.

## Dataset and licence

HELM requires a local CSV and will refuse to run without it. Official Stanford entries use `processed_dialogues.csv` under a MedHELM data path. Columns used in code are `context`, `gold_counselor_response`, `topic` and `dialogue_type`. Every instance is tagged test. The instance count is not published in the scenario file or in the arXiv table text that was opened. No data licence string was found. HELM evaluation code is Apache-2.0; that licence does not cover the dialogues.

## Who publishes it

The task sits in MedHELM, from Stanford CRFM with medical collaborators. Equal first authors on the arXiv paper (26 May 2025, 2505.23802) include Suhana Bedi, Hejie Cui, Miguel Fuentes and Alyssa Unell. CRFM hosts the MedHELM leaderboard. The HELM scenario and annotator live in the public HELM repository.

## Lineage

This is not a psychiatric multiple-choice set and not [healthbench](healthbench.md). It is also not [medi_qa](medi_qa.md), which answers consumer health questions. Sibling MedHELM generation tasks that use the same jury pattern include [mimic_bhc](mimic_bhc.md) and [medi_qa](medi_qa.md). There is no MedHELM family page. A geographic origin for the dialogues was not established from the opened paper HTML.

## Saturation and contamination

Saturation is unknown; the live board is JavaScript and was not read as numbers here. Contamination risk is low for this CSV because MedHELM marks it private and new. Generic counseling prose may still appear in pretraining.

## How to run it

Run HELM with scenario `mental_health` and a `data_path` to the private CSV. Optional `jury_config_path` selects annotator models. Official entries are in `run_entries_medhelm_private_stanford.conf`. Public reproduction of the reported score is not possible without that file. No matching task was confirmed in lm-evaluation-harness, Inspect Evals, OpenCompass or BIG-bench.

## Reading the numbers

A high MentalHealth Jury Score means an LLM panel thought the reply was accurate, complete and clear relative to one gold counselor turn. It is not a licence to deploy a therapy bot, and it is not a PHQ-9 or diagnostic accuracy number. The item pool is small if the seven-dialogue description holds. Pair it with a public clinical communication set and with safety evals before any product claim.
