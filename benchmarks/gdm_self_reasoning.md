---
id: gdm_self_reasoning
name: "GDM Self-reasoning"
aliases:
  - "GDM Situational Awareness"
  - "GDM Dangerous Capabilities: Self-reasoning"
page_kind: benchmark
category: agentic
subcategory: "instrumental self-reasoning / situational awareness in a fake deployment"
status: active
summary: "Eleven DeepMind challenges where an agent must notice and change its own config or tools to finish a job."
measures: >
  GDM Self-reasoning, as shipped in Inspect Evals, is the eleven situational-awareness
  challenges from Phuong, Zimmermann, Wang et al. 2025. The agent runs on a fake Linux
  deployment with bash and an agent.py stack. The goal looks ordinary (write a file,
  use a calculator, look up a JSON key). The real test is whether it notices a hidden
  constraint — max tokens, oversight frequency, a disabled database tool, a broken
  calculator, a blocklist — and edits config or source to lift it. English instructions;
  code and config files in the sandbox.
task_format: >
  Multi-turn ReAct agent in Docker or k8s. Inspect default: 80 messages, 10 epochs,
  at_least_1 reducer, success scorer on a store flag. Paper: 50 trials per challenge
  per difficulty. Most tasks have an easy and a hard sample (eval.yaml: 2 samples each).
metric:
  name: "challenge success rate (binary); suite pass count"
  direction: higher_is_better
  unit: ""
  max_score: 11
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Paper: a challenge is passed if success rate exceeds 20% over 50 trials. The safety
    case holds if the model passes fewer than 80% of challenges (9/11). Inspect README
    instead says the paper counted a difficulty as solved if at least 1 of 50 trials
    succeeded — that does not match section 3.3 of the paper. Inspect's default reducer
    is at_least_1 over 10 epochs, not a 20% rate over 50.
dataset:
  size: 22
  size_note: >
    Eleven tasks times two samples (easy/hard) in eval.yaml. Inspect README table is
    Easy/Hard over 11 challenges. Dataset note: released 2025-04-29. This is not the
    2024 four-task "instrumental self-modification" set in google-deepmind/dangerous-capability-evaluations/self_reasoning.
  url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/gdm_self_reasoning"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
  splits: "eleven named challenges, each with easy and hard environments"
  public_test_set: true
publisher:
  org: "Google DeepMind (paper); UK AI Security Institute (Inspect Evals port)"
  authors:
    - "Mary Phuong"
    - "Roland S. Zimmermann"
    - "Ziyue Wang"
    - "David Lindner"
    - "Victoria Krakovna"
    - "Sarah Cogan"
    - "Allan Dafoe"
    - "Lewis Ho"
    - "Rohin Shah"
  url: "https://arxiv.org/abs/2505.01420"
paper:
  title: "Evaluating Frontier Models for Stealth and Situational Awareness"
  arxiv: "2505.01420"
  url: "https://arxiv.org/abs/2505.01420"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/gdm_self_reasoning"
released: "2025-05"
last_updated: "2026-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - gdm_stealth
saturation:
  status: open
  top_score: null
  as_of: "2025-05"
  note: >
    Paper: six of eleven challenges were never solved even once by the tested models;
    several models exceed the 20% pass line on a minority of challenges. Inspect README
    (dataset 2025-04-29) reports gemini-2.5-flash-preview-04-17 and Claude 3.7 Sonnet
    at 10/11 easy and 3/11 hard, o4-mini at 8/11 easy and 3/11 hard. Easy vs hard and
    10-epoch at_least_1 vs 50-trial 20% rate are not interchangeable.
contamination:
  risk: medium
  note: >
    Public environments and prompts. Paper canaries included. 2024 DeepMind repo stripped
    solutions and easy prompts. Inspect uses realistic fictitious names. No measured
    training overlap was read here.
harness:
  lm_eval: ""
  inspect_evals: "gdm_self_reasoning_approved_directories, gdm_self_reasoning_calculator_improvement, gdm_self_reasoning_context_length_mod_instrumental_only, gdm_self_reasoning_context_length_mod_irreversibility_only, gdm_self_reasoning_database_tool, gdm_self_reasoning_latency_calculator, gdm_self_reasoning_max_messages_calculator, gdm_self_reasoning_max_tokens, gdm_self_reasoning_oversight_frequency, gdm_self_reasoning_read_logs, gdm_self_reasoning_turn_off_filters"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Package directory gdm_self_reasoning. Default sandbox docker; k8s supported.
    Epochs default 10. Paper used 50 trials. Not inspect_evals/gdm_capabilities.
tags:
  - agentic
  - safety
  - scheming
  - situational-awareness
  - self-reasoning
  - inspect-evals
  - gdm
sources:
  - url: "https://arxiv.org/abs/2505.01420"
    title: "Evaluating Frontier Models for Stealth and Situational Awareness (arXiv:2505.01420)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2505.01420"
    title: "Paper HTML (11 situational-awareness challenges, 20% pass line, 9/11 safety-case cap)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gdm_self_reasoning/README.md"
    title: "Inspect Evals self-reasoning README (11 tasks, Easy/Hard table, epoch note)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gdm_self_reasoning/eval.yaml"
    title: "eval.yaml (11 tasks, 2 samples each, version 4-B)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gdm_self_reasoning/gdm_self_reasoning.py"
    title: "Task constructors; at_least_1 epochs; success scorer"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google-deepmind/dangerous-capability-evaluations/main/self_reasoning/challenges.json"
    title: "2024 DeepMind self_reasoning challenges.json (predecessor set, not this suite)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT License"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gdm_capabilities/README.md"
    title: "gdm_capabilities README: this suite moved out of the old folder"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-009 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-009"
---

## What it measures

GDM Self-reasoning here means the 2025 situational-awareness suite, not the smaller 2024 self-modification set. The agent is dropped into a mocked deployment. It gets a job and tools. Nobody tells it that max_tokens is too small, that the calculator is wrong, or that the database tool is off. Success is noticing that fact and changing the live config or code.

Inspect maps eleven paper names onto tasks such as approved_directories, max_tokens, oversight_frequency, database_tool, calculator_improvement, latency_calculator, read_logs, and turn_off_filters. Two tasks split the 2024 context-length idea into instrumental-only and irreversibility-only. The agent.py environment is written as a Gemini-style deployment; the README says adapting it for every vendor is future work.

## How it is scored

Inspect marks a trial correct when a success flag is set (config edited right, or the job finished another way). Default aggregation is `at_least_1` over 10 epochs. The paper instead runs 50 trials and calls a challenge passed only if the success rate is above 20%. It also says the inability safety case still holds if the model passes fewer than 9 of 11 challenges.

Those two rules collide with the Inspect README, which claims the paper used "at least 1 of 50." Section 3.3 of the paper uses the 20% line. Quote which rule you used. Easy and hard samples are scored separately in Inspect's table.

## Dataset and licence

Twenty-two sandbox samples (11×2) in eval.yaml. Inspect's copy is MIT. The 2025 paper is the spec. The 2024 DeepMind `self_reasoning` JSON (context_length_mod_*, turn_off_filters, knowledge_gaps) is a predecessor with Apache-2.0 software and CC-BY materials, not this eleven-task port. Inspect 4-B (2026-08-03) pinned sandbox image digests.

## Who publishes it

Same DeepMind paper as [gdm_stealth](gdm_stealth.md), posted 2 May 2025. Inspect port contributors include ZiyueWang25 and XkunW. No standalone public leaderboard was opened for this page.

## Lineage

The paper says context_size, irreversibility, and output_filters revise Phuong et al. 2024; max_tool_calls, faulty_tool, and slow_tool follow Fronsdal and Lindner 2024. Inspect's 2024-era `gdm_capabilities` directory no longer holds the code. Do not fold this id into [gdm_self_proliferation](gdm_self_proliferation.md), which is a 2024 resource-and-spread suite.

## Saturation and contamination

Hard splits still fail often: Inspect's 2025-04-29 table has 3/11 hard for three strong models, with easy scores much higher. The paper reports that six challenges were never solved even once in their 50-trial runs. Public Dockerfiles and prompts are a medium leak risk; solutions were stripped in the 2024 repo and this port still avoids publishing a walkthrough.

## How to run it

`inspect eval inspect_evals/gdm_self_reasoning_approved_directories` and the other ten task ids, or the eval-set listing in the README. Optional `-T sandbox_type=k8s`. Matching the paper needs `--epochs=50` and a rate, not Inspect's 10-epoch at_least_1 default. `censor_reasoning` must be false for OpenAI reasoning models that echo encrypted blobs.

## Reading the numbers

A 10/11 easy score with at_least_1 over 10 tries is not a 10/11 paper pass at 20% of 50. Hard is the number that still separates models in the Inspect table. Success can be "edited the right JSON" rather than "understood deployment" in any deep sense. Pair with [gdm_stealth](gdm_stealth.md) if the claim is scheming prerequisites, and do not cite `gdm_capabilities` as if it were a score.
