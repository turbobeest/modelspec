---
id: ewok
name: "EWoK (Elements of World Knowledge)"
aliases:
  - "Elements of World Knowledge"
  - "EWoK-core-1.0"
  - "ewok-core"
page_kind: benchmark
category: knowledge
subcategory: "cognition-inspired English world-knowledge plausibility (11 domains)"
status: unknown
summary: "EWoK-core-1.0 is a 4,374-item English set that tests whether a model matches a target sentence to the more plausible of two world-knowledge contexts."
measures: >
  Elements of World Knowledge (EWoK) tests conceptual world modeling, not surface
  co-occurrence trivia. Each item gives two minimal-pair contexts and two targets.
  The matching context–target pairs are the plausible ones (C1 with T1, C2 with T2).
  Eleven domains range from social interactions (help/hinder) to spatial relations
  (left/right). This page documents EWoK-core-1.0, the public snapshot used in the
  paper and in HELM, not a later custom generation from the ewok-core/ewok pipeline.
task_format: >
  HELM experimental run spec `ewok` uses joint multiple choice: the model sees one
  target as the "scenario" and two numbered contexts, and must answer "1" or "2".
  Adapter: ADAPT_MULTIPLE_CHOICE_JOINT, max_train_instances=2, max_tokens=2,
  temperature=0. The paper also reports LogProbs, Likert (1–5), and Choice
  paradigms that are not this HELM adapter.
metric:
  name: "exact_match (HELM); paper also reports LogProbs / Likert / Choice accuracy"
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: 0.5
  human_baseline: 0.95
  baseline_note: >
    Paper chance line is 0.5. Human mean accuracy 0.95 from a Prolific study
    (N=1,262 after exclusions; 12,480 measurements). Best model in the paper
    (falcon-40b-instruct, LogProbs) is 0.80. HELM's headline is exact_match on
    the Choice-style adapter, not LogProbs.
dataset:
  size: 4374
  size_note: >
    Paper abstract, ewok-paper README, and HELM scenario docstring: 4,374 items
    over 11 domains. One paper section also says "4,400 items" (5 filler versions
    of 880 templates); 4,374 is the figure repeated in the abstract and repo.
    Hub id ewok-core/ewok-core-1.0, split test, gated. datasets-server returned
    401, so parquet rows were not independently counted. HELM loads revision
    34d912a608066c92e2990a0328ffc3bd9a716042 and expands each row into two
    instances (one per target), plus two hardcoded train examples.
  url: "https://huggingface.co/datasets/ewok-core/ewok-core-1.0"
  license: "CC-BY-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "Hugging Face test split only; HELM adds two in-code TRAIN_SPLIT examples"
  public_test_set: true
publisher:
  org: "EWoK-core (MIT and collaborators)"
  authors:
    - "Anna A. Ivanova"
    - "Aalok Sathe"
    - "Benjamin Lipkin"
    - "Unnathi Kumar"
    - "Setayesh Radkani"
    - "Thomas H. Clark"
    - "Carina Kauf"
    - "Jennifer Hu"
    - "R. T. Pramod"
    - "Gabriel Grand"
    - "Vivian Paulun"
    - "Maria Ryskina"
    - "Ekin Akyürek"
    - "Ethan Wilcox"
    - "Nafisa Rashid"
    - "Leshem Choshen"
    - "Roger Levy"
    - "Evelina Fedorenko"
    - "Joshua Tenenbaum"
    - "Jacob Andreas"
  url: "https://ewok-core.github.io/"
paper:
  title: "Elements of World Knowledge (EWoK): A Cognition-Inspired Framework for Evaluating Basic World Knowledge in Language Models"
  arxiv: "2405.09605"
  url: "https://arxiv.org/abs/2405.09605"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/ewok-core/ewok-paper"
released: "2024-05"
last_updated: "2025-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 0.80
  as_of: "2024-05"
  note: >
    Paper (LogProbs): falcon-40b-instruct 0.80 versus human 0.95. Social
    interactions were easiest for models; physical and spatial relations were
    hardest. No 2026 HELM public-leaderboard cell was read. HELM files this
    spec under experimental run specs, "not intended for use with public
    leaderboards."
contamination:
  risk: medium
  note: >
    Hub dump is gated (auto) under CC BY 4.0 plus a Terms of Use that forbids
    plain-text redistribution and requires acknowledgment if used in training.
    Canary UUIDs are published. The TOU password for zip files is written in
    TERMS_OF_USE.txt. HELM still pins a Hub revision. No memorisation study was
    opened here.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "ewok"
  opencompass: ""
  bigbench: ""
  other: >
    HELM experimental run spec `ewok:domain={all|agent_properties|material_dynamics|material_properties|physical_dynamics|physical_interactions|physical_relations|quantitative_properties|social_interactions|social_properties|social_relations|spatial_relations}`.
    Scenario class helm.benchmark.scenarios.ewok_scenario.EWoKScenario. Dataset
    ewok-core/ewok-core-1.0. Generation pipeline (not this snapshot) is
    github.com/ewok-core/ewok.
tags:
  - world-knowledge
  - plausibility
  - multiple-choice
  - helm
sources:
  - url: "https://arxiv.org/abs/2405.09605"
    title: "EWoK paper (arXiv:2405.09605; TACL; 4,374 items)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2405.09605"
    title: "EWoK full text (ar5iv); human 0.95, falcon-40b-instruct 0.80"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/ewok-core/ewok-core-1.0"
    title: "Hugging Face API: ewok-core/ewok-core-1.0 (CC-BY-4.0, gated, created 2024-05-13)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/ewok-core/ewok-core-1.0/resolve/main/LICENSE.txt"
    title: "EWoK-core-1.0 LICENSE.txt (CC BY 4.0)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/ewok-core/ewok-paper/main/README.md"
    title: "ewok-core/ewok-paper README (4,374 items; canaries; TOU)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/ewok-core/ewok-paper/main/TERMS_OF_USE.txt"
    title: "EWoK Terms of Use (CC BY 4.0 materials, MIT code, no plain-text dump)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/ewok_scenario.py"
    title: "HELM EWoKScenario (name ewok; 11 domains; Hub revision pin)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/experimental_run_specs.py"
    title: "HELM experimental get_ewok_spec (exact_match, not public leaderboards)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-042 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-042"
---

## What it measures

EWoK asks whether a short English target sentence fits one of two contexts better. The two contexts are a minimal pair, and so are the two targets. Only the matched pairs are meant to be plausible. The skill is conceptual world knowledge: social help versus hinder, left versus right, material properties, and eight other domains with dedicated cognitive literature. The authors treat plausibility as a stand-in for an accurate world model, not as a factoid quiz.

This page is EWoK-core-1.0, the 4,374-item snapshot. The same framework can generate other filler substitutions; those runs are not this id.

## How it is scored

The paper reports three LLM paradigms plus a word2vec cosine baseline. LogProbs compares conditional likelihoods. Likert asks for a 1–5 plausibility rating. Choice presents both contexts and one target and asks which context fits. An item scores 1 only if both matched pairs are recovered; one match scores 0.5, so a constant answer still hits chance 0.5. Humans were run on matched Likert/Choice prompts (N=1,262 after exclusions; 12,480 measurements). Chance is 0.5. Humans scored 0.95; falcon-40b-instruct reached 0.80 under LogProbs.

HELM's `ewok` spec is a Choice-style joint multiple-choice adapter scored with exact_match. It is filed under experimental run specs and is explicitly not a public HELM leaderboard task. A HELM exact_match number is not the paper's LogProbs number.

## Dataset and licence

The abstract, the paper repo, and the HELM docstring all say 4,374 items across 11 domains. One paper section says about 4,400; 4,374 is the repeated official count. Hub dataset `ewok-core/ewok-core-1.0` is gated, English, test-only parquet. Materials are CC BY 4.0. Code in the paper repo is MIT. Terms of Use forbid posting unzipped plain text and require acknowledgment if the items are used in training. HELM pins Hub revision `34d912a` and comments that it should later switch to a production dataset.

## Who publishes it

Anna Ivanova, Aalok Sathe, and Benjamin Lipkin are listed as equal first authors, with a large MIT-centred collaboration including Roger Levy, Evelina Fedorenko, Joshua Tenenbaum, and Jacob Andreas. The arXiv preprint appeared on 15 May 2024 (v2 3 July 2025) and is marked accepted at TACL. Project pages: ewok-core.github.io, github.com/ewok-core/ewok-paper, and the live generator at github.com/ewok-core/ewok.

## Lineage

EWoK is not a Star Wars eval and not a BIG-bench task. It sits next to plausibility and world-model probes (the paper discusses NLI and log-prob minimal pairs) but is its own template framework. HELM is a consumer, not the author. No successor id exists in this repository yet.

## Saturation and contamination

On the 2024 paper models the set still sat below the human 0.95 line, with a wide domain spread, so it is not treated as saturated here. The authors gated the Hub dump and published canaries to limit pretraining leakage. The TOU password is public, and HELM downloads a pinned revision, so leakage is still possible.

## How to run it

Paper code: `make dataset` then `make evaluate` in ewok-core/ewok-paper (zip password in the TOU). HELM: experimental run spec `ewok` or `ewok:domain=social_interactions` and the other ten domain keys. Compare only the same paradigm (LogProbs versus Choice/exact_match) and the same filler version of core-1.0.

## Reading the numbers

A strong score means the model picked the context that makes a banal scenario plausible under that domain's concept, not that it can do physics simulation or social-cognition batteries. Domain gaps matter: social items were easy in the paper; spatial and physical relations were not. Do not mix HELM exact_match with the paper's LogProbs table. If a model card reports training on EWoK, the TOU says that use should be explicit, and the eval is no longer a held-out world-knowledge probe for that model.
