---
id: anthropic_hh_rlhf
name: "Anthropic HH-RLHF (HELM Instruct)"
aliases:
  - "HH-RLHF"
  - "Anthropic RLHF dataset"
  - "anthropic_hh_rlhf:subset=hh"
  - "anthropic_hh_rlhf:subset=red_team"
page_kind: benchmark
category: instruction-following
subcategory: "HELM Instruct critique of first-turn prompts from Anthropic HH-RLHF"
status: unknown
summary: "HELM Instruct scores first human utterances from Anthropic HH-RLHF with a 1-5 Helpfulness critique; it does not train on or rank the chosen/rejected pairs."
measures: >
  anthropic_hh_rlhf, as this id, is Stanford CRFM's HELM Instruct scenario over Anthropic's
  public HH-RLHF dialogues. The model sees only the first human utterance of a conversation and
  must write a free-form English reply. HELM does not present the assistant turns, does not use
  chosen versus rejected labels as the score, and does not run RLHF. Two subsets exist: `hh`
  (helpfulness/harmlessness preference dialogues) and `red_team` (red-team transcripts). The
  skill is following that first request, under a human critique, not preference-model accuracy.
task_format: >
  Zero-shot generation via get_instruct_adapter_spec (max_tokens 512, temperature 0.7,
  max_train_instances 0). References are empty. Scoring is InstructionFollowingCritiqueMetric
  with caller-chosen num_respondents. Official classic run entries use num_respondents=1.
metric:
  name: Helpfulness
  direction: higher_is_better
  unit: "1-5"
  max_score: 5.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Annotators also rate Understandability, Completeness, Conciseness, and Harmlessness on the
    same 1-5 maps. schema_instruction_following.yaml sets main_name Helpfulness
    ("Does the model appear to do what it is instructed to?"). If fewer than num_respondents
    critiques return, the metric emits no stats. This is not reward-model accuracy on chosen
    versus rejected completions.
dataset:
  size: null
  size_note: >
    HELM `subset=hh` loads Anthropic/hh-rlhf default (revision
    09be8c5bbc57cb3887f3a9732ad6aa7ec602a1fa) and keeps the first utterance of each `chosen`
    field. Hugging Face datasets-server reports 160,800 train and 8,552 test rows (169,352
    total) for that default preference config. HELM `subset=red_team` loads data_dir
    red-team-attempts and maps the original train split to HELM test. Ganguli et al. (arXiv
    2209.07858 abstract) release 38,961 red-team attacks; datasets-server size for that config
    returned HTTP 500 when requested. Unique first utterances may be fewer than row counts
    because many pairs share a prompt. HELM does not deduplicate in the scenario source.
  url: "https://huggingface.co/datasets/Anthropic/hh-rlhf"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
  splits: "hh: HF train and test kept; red_team: original train used as HELM test"
  public_test_set: true
publisher:
  org: "Anthropic (dataset); Stanford CRFM (HELM Instruct scenario)"
  authors:
    - "Yuntao Bai"
    - "Andy Jones"
    - "Kamal Ndousse"
    - "Amanda Askell"
    - "Deep Ganguli"
  url: "https://huggingface.co/datasets/Anthropic/hh-rlhf"
paper:
  title: "Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback"
  arxiv: "2204.05862"
  url: "https://arxiv.org/abs/2204.05862"
  year: 2022
leaderboard_url: "https://crfm.stanford.edu/helm/instruct/latest/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/anthropic_hh_rlhf_scenario.py"
released: "2022-04"
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
    No numeric HELM Instruct cell was read (the public page is a JavaScript app). Anthropic's
    papers report RLHF training results, not this critique protocol.
contamination:
  risk: high
  note: >
    Prompts have been public since 2022 (HF dataset created 8 December 2022; papers April and
    September 2022). The files are widely reused in preference-tuning. HELM Instruct scores the
    first human turn of those public transcripts. HELM Safety ships a separate
    anthropic_red_team scenario on the same red-team transcripts, scored with safety_score
    rather than this Helpfulness critique. Ganguli et al. release 38,961 attacks.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "anthropic_hh_rlhf"
  opencompass: ""
  bigbench: ""
  other: "Run spec anthropic_hh_rlhf:subset=hh|red_team in instruction_following_run_specs.py; classic run_entries.conf uses num_respondents=1 (hh priority 1, red_team priority 3)."
tags:
  - instruction-following
  - helm
  - critique
  - hh-rlhf
  - red-teaming
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/anthropic_hh_rlhf_scenario.py"
    title: "HELM AnthropicHHRLHFScenario (first utterance only; hh vs red_team)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/instruction_following_run_specs.py"
    title: "HELM anthropic_hh_rlhf run spec (Instruct adapter, critique metrics)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/instruction_following_critique_metrics.py"
    title: "InstructionFollowingCritiqueMetric (1-5 Helpfulness and four other axes)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/static/schema_instruction_following.yaml"
    title: "HELM Instruct schema (main_name Helpfulness; anthropic_hh_rlhf group)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/presentation/run_entries.conf"
    title: "HELM classic run entries (hh and red_team, num_respondents=1)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/adaptation/common_adapter_specs.py"
    title: "get_instruct_adapter_spec (512 tokens, temperature 0.7, zero-shot)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Anthropic/hh-rlhf/raw/main/README.md"
    title: "Anthropic/hh-rlhf dataset card (MIT; PM data vs red-team data)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/Anthropic/hh-rlhf"
    title: "HF API (licence mit, created 2022-12-08, revision 09be8c5b…)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=Anthropic/hh-rlhf"
    title: "datasets-server default config size (160800 train / 8552 test)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2204.05862"
    title: "Bai et al. HH-RLHF paper (arXiv:2204.05862)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2209.07858"
    title: "Ganguli et al. red-teaming paper (38,961 attacks; arXiv:2209.07858)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/anthropics/hh-rlhf/master/README.md"
    title: "anthropics/hh-rlhf GitHub README (deprecated in favour of the HF copy)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/anthropic_red_team_scenario.py"
    title: "HELM AnthropicRedTeamScenario (same red-team transcripts; safety_score)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/README.md"
    title: "HELM README (maintenance mode from 2026-06-01)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-025 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-025"
---

## What it measures

This id is HELM Instruct's use of Anthropic's HH-RLHF dialogues, not Anthropic's training recipe. The model is given the first Human: turn only and must answer it. HELM strips later turns and ignores which completion was chosen. Subset `hh` draws those first turns from the public preference files. Subset `red_team` draws them from red-team transcripts whose original train split HELM treats as test. The language is English. The intended skill is following that request, including when the request is a harmful probe.

## How it is scored

`InstructionFollowingCritiqueMetric` collects human (or HELM critique-backend) ratings on five 1–5 axes. Helpfulness is the schema headline: whether the model appears to do what it was instructed to do. Harmlessness is a separate axis and can pull the other way on red-team prompts. Official `run_entries.conf` sets `num_respondents=1`. Empty references mean there is no exact-match to a gold assistant. Bai et al. and Ganguli et al. report preference-model and red-team analyses, not this 1–5 critique; do not mix those figures with HELM Helpfulness.

## Dataset and licence

Anthropic/hh-rlhf is MIT-licensed. The default preference config has 160,800 train and 8,552 test pairs on datasets-server. HELM `hh` walks every pair and keeps the first utterance of `chosen`. Ganguli et al. state 38,961 red-team attacks; HELM `red_team` loads that directory and scores it all as test. Unique prompts may be fewer than pair counts. The HF card warns that the data contain offensive content and are not meant for supervised training of dialogue agents.

## Who publishes it

Preference data: Bai, Jones, Ndousse, Askell, and co-authors, "Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback" (arXiv:2204.05862, April 2022). Red-team data: Ganguli, Lovitt, Kernion, and co-authors (arXiv:2209.07858, September 2022). Hugging Face copy created 8 December 2022. HELM packaging is Stanford CRFM's Instruct leaderboard (`https://crfm.stanford.edu/helm/instruct/`). The original GitHub tree is deprecated in favour of the HF dataset.

## Lineage

HELM Instruct groups this scenario with [self_instruct](self_instruct.md), Vicuna, Koala, Open Assistant, and grammar, all sharing the same critique metric. It is not [helm_safety](helm_safety.md): that leaderboard's `anthropic_red_team` scenario scores the same red-team first turns with `safety_score`, not this Helpfulness critique. Using HH-RLHF to train a reward model is a different job from this eval.

## Saturation and contamination

No HELM Instruct top cell was read from the JavaScript leaderboard. Contamination risk is high. The prompts have been public since 2022 and are standard preference-tuning data. A model that was RLHF'd on HH-RLHF may look strong here because it has seen the first turns, not because the critique protocol is hard.

## How to run it

HELM run spec `anthropic_hh_rlhf:subset=hh` or `subset=red_team`, with `num_respondents` and a working critique backend. Generation is 512 tokens at temperature 0.7, zero-shot. Without enough critiques the metric returns nothing, so a missing Helpfulness cell is not a zero. HELM entered maintenance mode on 1 June 2026. lm-evaluation-harness and Inspect Evals were not confirmed to ship this HELM critique task under this id.

## Reading the numbers

A high Helpfulness mean means the critique rater thought the model followed the first human turn, on a 1–5 rubric, with the configured respondent count. It is not win-rate against `rejected`, not harmlessness, and not HELM Safety. On `red_team`, a helpful answer to a harmful request can raise Helpfulness while lowering Harmlessness; read both axes. Compare only the same subset, respondent count, and temperature.
