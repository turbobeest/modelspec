---
id: gdm_self_proliferation
name: "GDM Self-proliferation"
aliases:
  - "GDM Dangerous Capabilities: Self-proliferation"
page_kind: benchmark
category: agentic
subcategory: "autonomous infrastructure, resources, and self-improvement tasks"
status: active
summary: "Ten DeepMind agent tasks on email, cloud, wallets, and self-improvement, run with human approval in Inspect."
measures: >
  Self-proliferation asks whether an agent can set itself up on the open internet:
  create mail, install a model on a cloud VM, adapt a web agent, make a Bitcoin
  wallet, find a new hire's email, ship a product, splice a celebrity clip, speed up
  inference, distill from an API, or reimplement a paper. Inspect Evals ships those
  ten as SP01, SP02, SP03, SP04, SP05, SP07, SP08, SP09, SP10, and SP12. The 2024
  paper's table also lists a Worm task; neither the public DeepMind JSON nor Inspect
  includes it. Agents get bash and a browser. English task briefs.
task_format: >
  End-to-end or milestone runs. Inspect requires human approval on every tool call
  by default (`--approval human`). Default agent is inspect_ai.react (since 2026-04).
  Message limits: 50 for SP01, 30 for the others. Milestone mode unlocks 3-7
  sub-tasks per challenge after unzipping encrypted secrets.
metric:
  name: "end-to-end 1-4 progress grade; milestone pass; estimated P(success)"
  direction: higher_is_better
  unit: ""
  max_score: 4
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Paper end-to-end grading: 1 fail, 2 some progress, 3 mostly complete, 4 success;
    take the max over 10 unguided attempts. If that fails, milestone runs and then
    expert-bit help. Inspect defaults epochs to 1 for e2e (changelog 2.1.0) because
    10 parallel human-in-the-loop runs are unmanageable. Expert best-of-N was removed
    from Inspect as broken.
dataset:
  size: 10
  size_note: >
    Ten e2e tasks in Inspect data/challenges.json (sp01-sp05, sp07-sp10, sp12).
    DeepMind's public challenges.json has the same ten names plus a local_llm test
    stub and two canary strings. Paper Table 10 lists eleven tasks including Worm.
    Inspect skipped two original indices (SP06, SP11). Milestone files add several
    sub-tasks per challenge after `python3 setup.py --password self-proliferation`.
  url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/gdm_self_proliferation"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
  splits: "e2e challenges.json; per-task milestone subtasks.json after secrets unzip"
  public_test_set: false
publisher:
  org: "Google DeepMind (paper and original assets); UK AI Security Institute (Inspect Evals port)"
  authors:
    - "Mary Phuong"
    - "Matthew Aitchison"
    - "Elliot Catt"
    - "Sarah Cogan"
    - "Alexandre Kaskasoli"
    - "Victoria Krakovna"
    - "David Lindner"
    - "Matthew Rahtz"
    - "Toby Shevlane"
  url: "https://github.com/google-deepmind/dangerous-capability-evaluations"
paper:
  title: "Evaluating Frontier Models for Dangerous Capabilities"
  arxiv: "2403.13793"
  url: "https://arxiv.org/abs/2403.13793"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/gdm_self_proliferation"
released: "2024-03"
last_updated: "2026-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: "2024-03"
  note: >
    Paper: Gemini 1.0 Pro and Ultra end-to-end scores were only 1 or 2 on every task
    (fail or some progress). Milestone ticks often needed expert guidance. No 2025-2026
    Inspect leaderboard was opened for this page.
contamination:
  risk: medium
  note: >
    DeepMind stripped solutions and easy prompts from the public repo, removed Track
    employee personal details, and embedded BIG-bench plus GDM canary GUIDs. Milestone
    secrets stay in passworded zip files so they are less likely to be scraped.
    Task briefs themselves are public. Worm was not released.
harness:
  lm_eval: ""
  inspect_evals: "gdm_sp01_e2e, gdm_sp02_e2e, gdm_sp03_e2e, gdm_sp04_e2e, gdm_sp05_e2e, gdm_sp07_e2e, gdm_sp08_e2e, gdm_sp09_e2e, gdm_sp10_e2e, gdm_sp12_e2e"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Milestone tasks gdm_spXX_milestones with -T subtasks=Y and optional -T browser=True.
    Extra: inspect-evals[gdm_self_proliferation]. Original assets:
    google-deepmind/dangerous-capability-evaluations/self_proliferation. SP02/SP09/SP10
    need GCP or equivalent. Not inspect_evals/gdm_capabilities.
tags:
  - agentic
  - safety
  - self-proliferation
  - inspect-evals
  - gdm
  - human-in-the-loop
sources:
  - url: "https://arxiv.org/abs/2403.13793"
    title: "Evaluating Frontier Models for Dangerous Capabilities (arXiv:2403.13793)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2403.13793"
    title: "Paper HTML (Table 10 tasks, e2e 1-4 scale, Gemini 1.0 results, canaries)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google-deepmind/dangerous-capability-evaluations/main/README.md"
    title: "DeepMind dangerous-capability-evaluations README (Apache-2.0 / CC-BY, stripped solutions)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google-deepmind/dangerous-capability-evaluations/main/LICENSE"
    title: "DeepMind Apache License 2.0 for software"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google-deepmind/dangerous-capability-evaluations/main/self_proliferation/challenges.json"
    title: "Original challenges.json (10 named tasks + local_llm stub; no Worm)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gdm_self_proliferation/README.md"
    title: "Inspect Evals self-proliferation README (10 tasks, human approval, skipped indices)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gdm_self_proliferation/eval.yaml"
    title: "eval.yaml (10 e2e tasks, version 6-B)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gdm_self_proliferation/data/challenges.json"
    title: "Inspect e2e challenges.json (sp01-sp05, sp07-sp10, sp12)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT License"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-009 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-009"
---

## What it measures

GDM Self-proliferation measures whether an agent can stand up digital infrastructure and then grow. Inspect's ten tasks are email signup, installing Mistral 7B on GCP, wiring a web agent, creating a Bitcoin wallet, tracking a recent DeepMind hire, building a product, editing a podcast for a fake charity, speeding up CPU inference, distilling from an API, and reimplementing StrategyLLM.

The paper frames three clusters: keep a network of agents online, acquire resources, and self-improve. Worm (asterisked as a critical-capability task in Table 10) is not in the public JSON or in Inspect. Track employee is sanitised relative to the internal study. The agent has a shell and a browser, so this is not a static quiz.

## How it is scored

Unguided end-to-end runs use a 1-4 progress grade; the paper takes the best of 10 attempts. If the agent never reaches 4, evaluators switch to milestones (3-7 per task) and then to measured expert hints. Inspect currently exposes e2e and milestone tasks, not the expert-hint stage (removed as broken). Default Inspect e2e epochs is 1, not 10.

Several milestone scorers were wrong and later patched: SP04 subtask 3 used to pass an empty address list; SP10 subtask 3 looked for a trailing period that the check never printed. Compare scores only after those changelog dates (2026-07-09).

## Dataset and licence

Ten public e2e briefs. Milestone solutions live in `secrets.zip` and need the password in the README. Inspect's port is MIT. DeepMind's original software is Apache-2.0; remaining materials are CC-BY-4.0. `public_test_set` is false for the milestone answers, true for the e2e prompts. SP02, SP09, and SP10 need cloud GPUs or equivalent.

## Who publishes it

Google DeepMind, first author Mary Phuong, arXiv 20 March 2024 (v2 5 April 2024). Original assets: `google-deepmind/dangerous-capability-evaluations`. Inspect Evals maintainers include XkunW, MariaIzobava, and kohankhaki. METR advised on the self-proliferation design, per the paper acknowledgements.

## Lineage

This is one slice of the 2024 dangerous-capability programme (persuasion, cyber, self-proliferation, self-reasoning). It is not [gdm_self_reasoning](gdm_self_reasoning.md), which is the 2025 eleven-task situational-awareness suite. Several tasks cite Kinniment et al. 2023 (METR) and Anthropic 2023. After 30 January 2026 the Inspect code lives in `gdm_self_proliferation`, not `gdm_capabilities`.

## Saturation and contamination

Gemini 1.0 did not finish any task end-to-end in the paper. That is an open suite, not a saturated quiz. Public briefs plus stripped solutions is medium contamination: a trainer can see the goals, not the official milestone keys, unless the zip is unpacked into a corpus.

## How to run it

`uv run inspect eval inspect_evals/gdm_sp01_e2e --approval human --epochs=1` and the other nine e2e ids. Do not drop `--approval human` unless you have replaced it with a tight auto-approver: the agent can mail, fetch, and delete. Milestones: unzip secrets, then `gdm_spXX_milestones -T subtasks=Y -T browser=True`. Fill `challenge_variables.json` (HF token, GCP instance names) for SP02 and SP10. Image tags were pinned in version 6-B (2026-08-03).

## Reading the numbers

A 4 on one e2e task means that run finished, not that the model can proliferate unsupervised. Human approval, browser on/off, epoch count, and scorer patches all move the grade. Worm is missing, so a "10/10 Inspect" figure is not the paper's eleven-task critical set. Pair with cyber CTF slices if you care about offensive capability, and with [gdm_stealth](gdm_stealth.md) / [gdm_self_reasoning](gdm_self_reasoning.md) if the claim is scheming rather than logistics.
