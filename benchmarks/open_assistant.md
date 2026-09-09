---
id: open_assistant
name: "Open Assistant (HELM Instruct)"
aliases:
  - "OASST1"
  - "OpenAssistant Conversations"
  - "OpenAssistant/oasst1"
page_kind: benchmark
category: instruction-following
subcategory: "HELM Instruct critique of OASST1 first-turn prompts"
status: unknown
summary: "HELM Instruct scenario over OASST1 initial prompts, scored with a 1-5 Helpfulness critique rather than gold replies."
measures: >
  open_assistant, as this id, is Stanford CRFM's OpenAssistantScenario. The model
  sees the root prompter message from an OASST1 conversation tree and writes a
  free-form reply. HELM keeps first-turn assistant messages as references but
  scores with InstructionFollowingCritiqueMetric, not overlap against those
  replies. OASST1 is LAION's crowd-sourced assistant corpus in 35 languages.
  Later turns in the tree are unused. This is not [koala](koala.md) or
  [self_instruct](self_instruct.md).
task_format: >
  Zero-shot generation. Run spec open_assistant:language={lang} with lang a
  Hub language code or all. Adapter from get_instruct_adapter_spec: max_tokens
  512, temperature 0.7, max_train_instances 0. Loads OpenAssistant/oasst1 at
  revision fdf72ae0827c1cda404aff25b6603abec9e3399b. Roots (parent_id is None)
  become inputs; child assistant texts become CORRECT_TAG references. Train
  and validation Hub splits are both loaded; metadata main_split is valid.
metric:
  name: Helpfulness
  direction: higher_is_better
  unit: "1-5"
  max_score: 5.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    InstructionFollowingCritiqueMetric asks num_respondents annotators five 1-5
    axes: Helpfulness, Understandability, Completeness, Conciseness,
    Harmlessness. Scenario metadata main_metric is Helpfulness ("Does the model
    appear to do what it is instructed to?"). If fewer than num_respondents
    critiques return, the metric emits no stats. Volunteer rankings inside
    OASST1 are not this 1-5 scale.
dataset:
  size: 88838
  size_note: >
    Hugging Face OpenAssistant/oasst1 ready split: train 84,437 + validation
    4,401 = 88,838 messages (card and datasets-server). Paper and HELM
    docstring: 66,497 trees and 161,443 messages in the full export; 10,364
    ready trees / 88,838 ready messages match the Hub parquet. HELM instances
    are language-filtered root prompts plus first-turn assistant replies, not
    one instance per message. How many roots survive that filter was not
    counted here. Collection cutoff on the card: 12 April 2023.
  url: "https://huggingface.co/datasets/OpenAssistant/oasst1"
  license: "Apache-2.0"
  languages:
    - en
    - es
    - ru
    - de
    - zh
    - fr
    - th
    - pt
    - ca
    - ko
    - uk
    - it
    - ja
    - vi
    - eu
    - pl
    - hu
    - ar
    - nl
    - sv
    - tr
    - fi
    - cs
    - da
    - gl
    - he
    - ro
    - nb
    - id
    - bg
    - bn
    - fa
    - el
    - eo
    - sk
  modalities:
    - text
  splits: "Hub train/validation; HELM TRAIN_SPLIT and VALID_SPLIT; main_split valid"
  public_test_set: true
publisher:
  org: "LAION / Open Assistant (dataset); Stanford CRFM (HELM scenario)"
  authors:
    - "Andreas Köpf"
    - "Yannic Kilcher"
    - "Dimitri von Rütte"
    - "Sotiris Anagnostidis"
    - "Zhi-Rui Tam"
    - "Keith Stevens"
    - "Abdullah Barhoum"
    - "Nguyen Minh Duc"
    - "Oliver Stanley"
    - "Richárd Nagyfi"
    - "Shahul ES"
    - "Sameer Suri"
    - "David Glushkov"
    - "Arnav Dantuluri"
    - "Andrew Maguire"
    - "Christoph Schuhmann"
    - "Huu Nguyen"
    - "Alexander Mattick"
  url: "https://github.com/LAION-AI/Open-Assistant"
paper:
  title: "OpenAssistant Conversations -- Democratizing Large Language Model Alignment"
  arxiv: "2304.07327"
  url: "https://arxiv.org/abs/2304.07327"
  year: 2023
leaderboard_url: "https://crfm.stanford.edu/helm/instruct/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/open_assistant_scenario.py"
released: "2023-04"
last_updated: "2023-05"
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
    HELM Instruct leaderboard HTML was not rendered here (the instruct index
    returned a tiny body). No dated Helpfulness cell for this scenario was
    recorded. Volunteer quality labels in OASST1 are not a model ceiling.
contamination:
  risk: high
  note: >
    Prompts and ranked replies have been public on Hugging Face since 2023 and
    are a common SFT mix. A model can have seen the same root prompt as
    instruction data. HELM's judge scores a new completion, but leakage of the
    prompt still inflates Helpfulness.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "open_assistant"
  opencompass: ""
  bigbench: ""
  other: "run spec open_assistant:language={lang}; HELM Instruct"
tags:
  - instruction-following
  - human-feedback
  - multilingual
  - helm-instruct
sources:
  - url: "https://arxiv.org/abs/2304.07327"
    title: "OpenAssistant Conversations (arXiv 2304.07327)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/OpenAssistant/oasst1"
    title: "OpenAssistant/oasst1 dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/OpenAssistant/oasst1"
    title: "OpenAssistant/oasst1 API cardData"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=OpenAssistant/oasst1"
    title: "datasets-server info for oasst1"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/open_assistant_scenario.py"
    title: "HELM open_assistant_scenario.py"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/instruction_following_run_specs.py"
    title: "HELM instruction_following_run_specs.py"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/instruction_following_critique_metrics.py"
    title: "HELM InstructionFollowingCritiqueMetric"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/adaptation/common_adapter_specs.py"
    title: "HELM get_instruct_adapter_spec"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-063 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-063"
---

## What it measures

The model is given one human prompt from OpenAssistant Conversations (OASST1) and must write an assistant reply. OASST1 trees can run many turns; HELM keeps only the root prompter message and the first assistant children. The skill is following a real volunteer's request in one of 35 languages, not reconstructing the rest of the tree.

This is a HELM Instruct critique scenario, in the same adapter family as [koala](koala.md) and [self_instruct](self_instruct.md). It is not a BLEU-against-reference chat benchmark.

## How it is scored

`get_instruct_adapter_spec` generates one completion, temperature 0.7, 512 max tokens, zero in-context examples. `InstructionFollowingCritiqueMetric` then asks `num_respondents` annotators five 1–5 questions. Helpfulness is the published main metric: “Does the model appear to do what it is instructed to?” Other axes are understandability, completeness, conciseness, and harmlessness. If not enough critiques come back, HELM records no stats.

First-turn assistant texts are stored as references with `CORRECT_TAG`, but the critique metric does not score overlap against them. Volunteer `quality` labels in the dump are unused.

## Dataset and licence

Hub card: Apache-2.0. Ready parquet is 88,838 messages (84,437 train, 4,401 validation). The paper and HELM docstring also cite the full export: 66,497 trees, 161,443 messages, 35 languages, 13,500+ volunteers, collected through 12 April 2023. English and Spanish dominate the message counts on the card (71,956 and 43,061). HELM pins revision `fdf72ae…`, which matches the current Hub SHA. Instance count after `language=` filtering was not computed here.

## Who publishes it

Dataset: LAION Open Assistant, paper Köpf et al., arXiv 2304.07327, 14 April 2023. Code: `LAION-AI/Open-Assistant`. HELM wrap: Stanford CRFM, scenario name `open_assistant`, listed under HELM Instruct (`https://crfm.stanford.edu/helm/instruct/`). The instruct index page returned almost no HTML when fetched, so no live Helpfulness table is cited.

## Lineage

OASST1 is a crowd conversation corpus, then a HELM Instruct prompt set. Sibling HELM Instruct pages: [koala](koala.md), [self_instruct](self_instruct.md), [anthropic_hh_rlhf](anthropic_hh_rlhf.md). Not the OASST2 dump and not OpenAssistant's own reward-model training split.

## Saturation and contamination

No current Helpfulness leaderboard cell was read. The prompts have been public SFT data since 2023, so contamination risk is high even though the judge looks at a new completion. A saturated English chatbot can still fail on low-count languages in the tail (Slovak 19 messages on the card).

## How to run it

HELM run spec `open_assistant:language=en` (or `all`). You must pass `num_respondents` for the critique metric. Do not compare Helpfulness to OASST reward-model accuracy or to a ROUGE against the stored first-turn reply. Temperature 0.7 is the instruct default; greedy numbers are a different protocol.

## Reading the numbers

A 4–5 Helpfulness mean means annotators thought the model did what that volunteer asked, on the first turn only. It does not measure multi-turn consistency, ranking among several replies, or factuality (the metric has a separate unused “facts true” question in the class docstring). Always name the language filter. For a small fixed English prompt set with the same 1–5 critique, see [koala](koala.md).
