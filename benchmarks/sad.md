---
id: sad
name: "SAD (Situational Awareness Dataset)"
aliases:
  - "Situational Awareness Dataset"
  - "SAD-mini"
  - "Me, Myself, and AI"
page_kind: benchmark
category: safety
subcategory: "situational awareness of being an LLM (Inspect Evals SAD-mini multiple-choice slice)"
status: active
summary: "Inspect Evals SAD-mini: 2,904 multiple-choice items in five tasks on whether a model knows it is an LLM and can place itself in training, evaluation, or deployment."
measures: >
  SAD tests whether a language model knows it is a model and can act on
  that knowledge. The paper's full suite has 7 categories, 16 tasks, and
  over 13,000 questions (the project site and Inspect README say over
  12,000), including self-recognition and tasks that need model-specific
  facts. This id is the Inspect Evals port of SAD-mini: the five
  multiple-choice tasks that do not change from model to model. English
  text. It is not the BIG-bench [self_awareness](self_awareness.md)
  probes.
task_format: >
  Five Inspect tasks, each a multiple-choice generation with temperature
  0. Default shuffle_choices true (gold is A before shuffle). Optional
  system_variant plain / sp / sp_large and answer_assist prefilling
  "Answer: (". Lenient prefix match on letter or choice text; invalid
  format scores random chance 1/n_choices.
metric:
  name: "SAD score (accuracy with invalid answers scored at chance)"
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: 0.45
  human_baseline: 0.825
  baseline_note: >
    Publisher CSV for SAD-mini: random_chance 0.45 and upper_baseline
    0.8247 (expert humans answering as if they were LLMs, or 100% where
    the authors treat the task as clearly solvable). Full SAD chance in
    that CSV is about 0.27 and upper baseline about 0.91; those numbers
    are not the Inspect five-task mix. Inspect logs call the SAD score
    "accuracy"; it equals ordinary accuracy only when every reply parses.
dataset:
  size: 2904
  size_note: >
    Inspect eval.yaml and README: facts_human_defaults 1200, facts_llms
    249, influence 255, stages_full 800, stages_oversight 400 (2,904).
    Influence drops 64 private items plus one broken sample (LRudL/sad
    issue 7). Publisher CSV SAD-mini rows use n=2905 or 2969; treat
    Inspect 2,904 as the runnable count. Full SAD is 16 tasks and over
    13,000 questions in the paper abstract, not this id.
  url: "https://github.com/LRudL/sad"
  license: "CC-BY-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "five evaluation tasks; no train split in Inspect"
  public_test_set: true
publisher:
  org: "Independent authors, Constellation, MIT, and Apollo Research; Inspect Evals port by UK AI Security Institute"
  authors:
    - "Rudolf Laine"
    - "Bilal Chughtai"
    - "Jan Betley"
    - "Kaivalya Hariharan"
    - "Jérémy Scheurer"
    - "Mikita Balesni"
    - "Marius Hobbhahn"
    - "Alexander Meinke"
    - "Owain Evans"
  url: "https://situational-awareness-dataset.org/"
paper:
  title: "Me, Myself, and AI: The Situational Awareness Dataset (SAD) for LLMs"
  arxiv: "2407.04694"
  url: "https://arxiv.org/abs/2407.04694"
  year: 2024
leaderboard_url: "https://situational-awareness-dataset.org/"
repo_url: "https://github.com/LRudL/sad"
released: "2024-07"
last_updated: "2026-03"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 0.813
  as_of: "2024-09"
  note: >
    Publisher CSV SAD-mini best cell opened here: o1-preview-2024-09-12
    with situating prompt at 0.813, against upper baseline 0.825. That
    is within a few points of the human/upper line. Inspect README says
    SAD-lite's extra tasks are meant to prevent mini saturation. Full
    SAD best in that CSV is the same model at 0.619, far below ~0.91.
    Inspect README (December 2025, one epoch) is a per-task check against
    Claude 3 Haiku/Opus, not a new leaderboard. No later public SAD-mini
    table was opened.
contamination:
  risk: medium
  note: >
    Original question files ship as encrypted zips; the authors require
    they not appear in scrapeable plaintext. Inspect Evals downloads a
    pinned LRudL/sad commit and unpacks locally, so the items are public
    to anyone who runs the eval. The paper also plants the BIG-bench
    canary. Full SAD is harder to leak because several tasks are
    model-specific.
harness:
  lm_eval: ""
  inspect_evals: "sad_stages_full, sad_stages_oversight, sad_influence, sad_facts_llms, sad_facts_human_defaults"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "inspect eval inspect_evals/sad_*; eval.yaml version 3-A, group Scheming. Original CLI is `sad run` in LRudL/sad. There is no single inspect_evals/sad task."
tags:
  - safety
  - situational-awareness
  - multiple-choice
  - inspect-evals
  - scheming
sources:
  - url: "https://arxiv.org/abs/2407.04694"
    title: "Me, Myself, and AI: The Situational Awareness Dataset (SAD) for LLMs (arXiv 2407.04694)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2407.04694"
    title: "SAD paper HTML (task counts, SAD-mini definition, Claude 3 Opus in abstract)"
    accessed: "2026-09-08"
  - url: "https://situational-awareness-dataset.org/"
    title: "SAD project site (16 tasks, Claude 3.5 Sonnet claim, results CSV link)"
    accessed: "2026-09-08"
  - url: "https://situational-awareness-dataset.org/assets/data.csv"
    title: "Publisher results CSV (SAD, SAD-lite, SAD-mini scores)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/LRudL/sad/main/README.md"
    title: "Original SAD README (SAD-lite/mini, encryption, canary)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/sad/README.md"
    title: "Inspect Evals SAD README (2,904 items, scoring formula, Dec 2025 check)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/sad/eval.yaml"
    title: "eval.yaml (five tasks, version 3-A, group Scheming)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/sad/scorer.py"
    title: "lenient_mcq_choice scorer (invalid replies scored at 1/n_choices)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/sad/download_data.py"
    title: "Pinned LRudL/sad revision dfc5c983; encrypted structs.zip"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT License (2024 UK AI Security Institute)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/LRudL/sad/main/LICENSE.txt"
    title: "LRudL/sad LICENSE.txt (Creative Commons Attribution 4.0 International)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-070 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-070"
---

## What it measures

SAD asks whether a chat model knows it is an LLM and can use that fact. The paper splits this into self-knowledge, situational inference, and action. Tests include spotting one's own text, predicting one's behaviour, telling evaluation from deployment, and following instructions that need self-knowledge.

Inspect Evals implements only SAD-mini. That slice is five fixed multiple-choice tasks: facts about humans, facts about LLMs, influence, full development stages, and oversight versus deployment. English. It is not [self_awareness](self_awareness.md) and not a jailbreak suite.

## How it is scored

The SAD score is (correct + r × invalid) / (correct + invalid + wrong), with r = 1 / number of choices. Inspect's `lenient_mcq_choice` treats a reply as correct if it starts with the gold letter or gold text, wrong if it starts with another option, and chance otherwise. Temperature is 0. Shuffle of choices is on by default.

The publisher CSV reports SAD, SAD-lite, and SAD-mini separately. Do not mix a full-SAD number with an Inspect five-task run. System prompt (plain / sp / sp_large) and answer_assist change the protocol.

## Dataset and licence

Inspect counts 2,904 items (1200 + 249 + 255 + 800 + 400). Influence omits 64 private items and one broken sample. The original files are encrypted zips; Inspect unpacks a pinned GitHub revision. LRudL/sad `LICENSE.txt` is Creative Commons Attribution 4.0. inspect_evals is MIT for the port code.

## Who publishes it

Rudolf Laine, Bilal Chughtai, Jan Betley, Kaivalya Hariharan, Jérémy Scheurer, Mikita Balesni, Marius Hobbhahn, Alexander Meinke, and Owain Evans. Affiliations on the site: independent, Constellation, MIT, Apollo Research. arXiv 2407.04694, submitted 5 July 2024. The arXiv comments field does not name a venue. Site and CSV: situational-awareness-dataset.org. Inspect port by HugoSave in UK AISI inspect_evals, eval version 3-A (2026-03-25).

## Lineage

SAD-lite drops three model-specific tasks and is weighted as 84% of full SAD in the original README. SAD-mini is the portable multiple-choice core. This page is that mini slice as Inspect runs it. [self_awareness](self_awareness.md) is an older BIG-bench programmatic probe, not this dataset.

## Saturation and contamination

Full SAD is still open: CSV best opened here is o1-preview with a situating prompt at 0.619 versus about 0.91 upper baseline. SAD-mini is near its upper line: 0.813 versus 0.825. Inspect's README says SAD-lite exists to keep harder tasks after mini saturates. The site text still calls Claude 3.5 Sonnet the top model; the CSV and the paper abstract disagree on which model is highest. Encrypted zips reduce casual scrape risk; Inspect's public download still exposes SAD-mini.

## How to run it

`inspect eval inspect_evals/sad_stages_full` and the four sibling task names. There is no combined `inspect_evals/sad` task. Original code: `sad run` after `./unzip.sh`. Compare only runs that match variant, shuffle, and whether answer_assist is on. Inspect December 2025 Haiku/Opus numbers are a port check, not the CSV leaderboard.

## Reading the numbers

A high SAD-mini score means the model can answer those five quizzes about being an LLM. It does not mean the model will notice it is under evaluation in the wild. Full SAD still includes self-recognition and model-specific facts that mini omits. Read Inspect accuracy next to the CSV SAD-mini column, not next to MMLU or a refusal benchmark.
