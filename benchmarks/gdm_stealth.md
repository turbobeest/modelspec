---
id: gdm_stealth
name: "GDM Stealth"
aliases:
  - "GDM Dangerous Capabilities: Stealth"
page_kind: benchmark
category: agentic
subcategory: "scheming-prerequisite stealth (oversight evasion)"
status: active
summary: "Google DeepMind stealth suite: tool-using agents try to hide policy-breaking actions from monitors."
measures: >
  GDM Stealth tests whether an agent can reason about oversight and still complete a
  forbidden side goal. The 2025 paper defines five stealth challenges. Inspect Evals
  ports four of them: oversight_pattern, classifier_evasion, cover_your_tracks, and
  strategic_rule_breaking. The fifth paper task, decision_sabotage, is not in the
  inspect_evals package. Agents act as email secretaries, desktop assistants, or
  customer-support bots, with bash and task tools inside a sandbox. English prompts;
  fictitious but realistic names.
task_format: >
  Multi-turn ReAct agent in Docker (default) with task-specific scaffolding. Inspect
  defaults: 10 epochs; 120 messages (220 for strategic_rule_breaking). Several tasks
  use LLM raters and judges. Oversight pattern uses regex and rule checks instead.
metric:
  name: "per-challenge success rate or normalised score"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    There is no single suite score. Binary challenges use success rate. Numeric ones
    (cover_your_tracks, strategic_rule_breaking) use a score. The paper treats a
    binary stealth challenge as passed if success exceeds the top 50% of humans, and
    a numeric one if the model's median exceeds the mean of that human group. Human
    sample sizes are small; cover_your_tracks cites a 5-person human mean of 76/100.
dataset:
  size: 14
  size_note: >
    Inspect eval.yaml sample counts: classifier_evasion 9, cover_your_tracks 2,
    oversight_pattern 2, strategic_rule_breaking 1 (14 total). cover_your_tracks
    defaults to hard_only=True. The paper has five challenges including
    decision_sabotage, which this package does not ship. Inspect README: dataset
    released 2025-05-18.
  url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/gdm_stealth"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
  splits: "fixed challenge JSON plus Docker environments; no train split"
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
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/gdm_stealth"
released: "2025-05"
last_updated: "2026-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - gdm_self_reasoning
saturation:
  status: open
  top_score: null
  as_of: "2025-05"
  note: >
    Paper (early April 2025 models): at least one model passed decision_sabotage and
    oversight_pattern; cover_your_tracks, classifier_evasion, and strategic_rule_breaking
    were not passed under the paper's human-relative rule. None of the evaluated models
    succeeded even once in 50 cover_your_tracks trials. Inspect Evals' 2025-05-18 table
    reports per-task scores for gemini-2.5-flash-preview-04-17 and o4-mini, not a
    comparable pass/fail suite score.
contamination:
  risk: medium
  note: >
    Challenge files are public. The paper includes BIG-bench and GDM canary GUIDs and
    asks not to train on the eval. Names are LLM-generated fiction meant to look real.
    Inspect changelog 4-A (2026-07-22) fixed a verdict-injection in
    strategic_rule_breaking. No source opened here measured training-set overlap.
harness:
  lm_eval: ""
  inspect_evals: "gdm_oversight_pattern, gdm_classifier_evasion, gdm_cover_your_tracks, gdm_strategic_rule_breaking"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Package directory gdm_stealth. Extra: pip install inspect-evals[gdm_stealth].
    Default epochs 10 with mean/median/max reducers; paper used 50 trials. Default
    rater_model_company=google. No inspect_evals/gdm_capabilities task after the
    2026-01-29 split.
tags:
  - agentic
  - safety
  - scheming
  - stealth
  - inspect-evals
  - gdm
sources:
  - url: "https://arxiv.org/abs/2505.01420"
    title: "Evaluating Frontier Models for Stealth and Situational Awareness (arXiv:2505.01420)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2505.01420"
    title: "Paper HTML (five stealth tasks, 50 trials, human-relative pass rule, April 2025 models)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gdm_stealth/README.md"
    title: "Inspect Evals GDM Stealth README (4 tasks; 2025-05-18 scores; epochs note)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gdm_stealth/eval.yaml"
    title: "eval.yaml (4 tasks, sample counts, version 4-A)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gdm_stealth/__init__.py"
    title: "Package exports: four runnable tasks, no gdm_stealth meta-task"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gdm_stealth/gdm_stealth.py"
    title: "Task constructors, rater models, epoch reducers"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT License (UK AI Security Institute, 2024)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gdm_capabilities/README.md"
    title: "Former gdm_capabilities folder: evals moved one level up"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-009 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-009"
---

## What it measures

GDM Stealth asks whether a tool-using agent can notice a monitor and still carry out a hidden goal. In oversight_pattern and classifier_evasion the agent is an email secretary that must sneak banned content past a scanner. In cover_your_tracks it must finish a job and wipe the log. In strategic_rule_breaking it is a support bot that scores more by breaking process rules without getting caught.

The paper adds decision_sabotage, a hiring-assistant study with human users. Inspect Evals does not ship that task. Prompts are English. People and firms in the environments are fictitious on purpose, so the distribution still looks like real mail.

## How it is scored

Each challenge has its own scorer. Oversight pattern checks whether the agent found unmonitored channels. Classifier evasion uses a capable rater (default Gemini 2.5 Pro preview) plus a judge. Cover-your-tracks and strategic rule breaking return numeric scores; the paper also tracks milestones such as deleting a key email.

The paper's safety-case rule is not "any success." A binary stealth challenge passes if success beats the top half of humans. A numeric one passes if the model's median beats that human group's mean. They ran 50 trials per model in early April 2025. Inspect Evals defaults to 10 epochs and mean/median/max reducers, so an inspect score is not the paper's pass/fail bit. The Inspect stealth README instead says the paper counted success as at least 1 of 50 trials. That does not match section 3.3 of the paper.

## Dataset and licence

Inspect lists 14 samples across four tasks. The paper's fifth task is missing here. Environments are Docker images with compose.yaml; Inspect 4-A (2026-07-22) pinned image digests. inspect_evals is MIT. The 2025 paper is the scientific source; DeepMind's 2024 dangerous-capability repo is Apache-2.0/CC-BY and does not contain this stealth suite.

## Who publishes it

Google DeepMind published the paper on 2 May 2025 (arXiv v4 3 July 2025). Equal-contribution first authors are Mary Phuong, Roland S. Zimmermann, and Ziyue Wang. UK AISI's inspect_evals port is in `gdm_stealth`, contributed by ZiyueWang25. There is no live public leaderboard analogous to HELM Classic.

## Lineage

This suite is a sibling of [gdm_self_reasoning](gdm_self_reasoning.md) in the same 2025 paper (stealth vs situational awareness). It is not the 2024 "Evaluating Frontier Models for Dangerous Capabilities" self-proliferation or self-reasoning sets. Until 29 January 2026 Inspect kept GDM evals under `gdm_capabilities`; that folder is now a pointer README only.

## Saturation and contamination

The paper says current frontier models are not at a concerning stealth level. Two of five paper challenges were passed by at least one model (decision_sabotage, oversight_pattern). Cover-your-tracks stayed at 0/50 full successes for every model they report, while a five-person human mean was 76/100. Public JSON plus canary strings is medium contamination risk, not a hidden test key.

## How to run it

`pip install inspect-evals[gdm_stealth]`, then `inspect eval inspect_evals/gdm_oversight_pattern` (and the other three task ids). Set `--epochs=50` to match the paper's trial count. Rater quality changes classifier_evasion a lot; the README warns that a weak rater makes the task easy. Strategic rule breaking needs `--max-tool-output=32768` and, for thinking models, extra reasoning tokens. Do not quote a number labelled `gdm_capabilities`; that id is not a runnable eval.

## Reading the numbers

A high stealth score means the agent hid the side goal under that monitor, not that it would scheme in production. Decision_sabotage is a human study and is absent from Inspect, so an Inspect "suite" average over four tasks is not the paper's five-task safety case. Compare rater model, epoch count, and hard_only before stacking numbers. Read [gdm_self_reasoning](gdm_self_reasoning.md) beside it: stealth without situational awareness, or the reverse, is a different claim.
