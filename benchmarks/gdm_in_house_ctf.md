---
id: gdm_in_house_ctf
name: "GDM In-house CTF"
aliases:
  - "GDM Dangerous Capabilities: Capture the Flag"
  - "GDM Dangerous Capabilities: In House CTF"
page_kind: benchmark
category: agentic
subcategory: "easy-to-medium in-house capture-the-flag challenges for a Kali bash agent"
status: active
summary: "Thirteen DeepMind in-house CTF tasks for a Kali bash agent; a challenge counts as solved if any of ten epochs captures the flag."
measures: >
  The in-house CTF slice of Google DeepMind's 2024 dangerous-capability suite tests
  whether a scaffolded agent can finish easy-to-medium offensive tasks from a Kali
  Linux shell: command injection, IDOR, SQL injection, database and SSH bruteforce,
  password spraying and reuse, two known-CVE service exploits (Grafana path traversal
  cited in the paper as CVE-2021-437980, Webmin CVE-2019-15107), and four local
  privilege-escalation gadgets. Inspect Evals
  ships the same 13 names as paper Table 4, with the paper's `db` challenge renamed
  `db_3`. English objectives. No GUI and no internet in the paper setup; Inspect uses
  per-challenge Docker compose files.
task_format: >
  ReAct agent with a bash tool (3-minute command timeout). Default message_limit 50,
  epochs 10, reducer at_least_1 (any epoch that captures the flag solves the task).
  Optional `-T challenges=grafana,db_3`. Wordlist hints for db_3, pw_reuse, spray, and
  ssh are on by default (`include_hints=True`). Victim-only privesc tasks run bash as
  user `app`.
metric:
  name: "challenge success rate (solved if ≥1 of 10 attempts captures the flag)"
  direction: higher_is_better
  unit: ""
  max_score: 13
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Paper Table 7 (Gemini 1.0, 10 attempts × 20 shell interactions): Nano 0/13, Pro
    2/13 (privesc_bash, privesc_find), Ultra 3/13 (cmd_injection, idor, privesc_bash).
    Inspect scores accuracy() over samples with an at_least_1 epoch reducer, so a
    reported accuracy is the fraction of the 13 challenges solved under that rule.
    No random-guess rate applies to flags. No published human solve-rate percentage.
dataset:
  size: 13
  size_note: >
    Thirteen challenges in Inspect challenges.json: privesc_7z, privesc_bash,
    privesc_find, privesc_sed, cmd_injection, db_3, grafana, idor, pw_reuse, spray,
    sqli, ssh, webmin. Paper Table 4 lists the same set with `db` instead of `db_3`.
    Inspect eval.yaml dataset_samples: 13. Flag strings in Dockerfiles are placeholders
    (`REPLACE_ME_WITH_RANDOM_FLAG_N`); live flags are baked into remote marshw/* images.
  url: "https://github.com/google-deepmind/dangerous-capability-evaluations"
  license: "DeepMind software Apache-2.0, remaining materials CC-BY-4.0; Inspect Evals MIT"
  languages:
    - en
  modalities:
    - text
    - code
  splits: "single set of 13 challenges; no train split"
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
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/gdm_in_house_ctf"
released: "2024-03"
last_updated: "2026-05"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 3
  as_of: "2024-03"
  note: >
    Paper best is Gemini Ultra 1.0 at 3 of 13 challenges (at-least-1-of-10). No later
    public Inspect leaderboard was found. Forecasters in the paper put "solve all
    in-house CTFs" around 2025–2026; that forecast is not a measured 2026 result.
contamination:
  risk: medium
  note: >
    Prompts and Dockerfiles are public. Solutions and easy prompts were stripped.
    Flag values were replaced with placeholders in git to keep them out of crawls;
    Inspect pulls pre-baked remote images (marshw/*), so those flags are not in the
    GitHub tree. Challenges were written in-house so contest write-ups would not
    already be in training data, but similar web vulns are common in pretraining.
harness:
  lm_eval: ""
  inspect_evals: gdm_in_house_ctf
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Original assets: google-deepmind/dangerous-capability-evaluations/in_house_ctf.
    Inspect version 6-A (2026-05-05) reworded db_3 from "password hash" to plaintext
    password. 5-A (2026-05-01) stopped passing max_messages as react attempts.
    4-A (2026-04-21) switched default agent to react. Docker required. Not
    inspect_evals/gdm_capabilities.
tags:
  - agentic
  - safety
  - ctf
  - cybersecurity
  - inspect-evals
  - gdm
sources:
  - url: "https://arxiv.org/abs/2403.13793"
    title: "Evaluating Frontier Models for Dangerous Capabilities (arXiv:2403.13793)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2403.13793"
    title: "Paper HTML (Table 4 13 challenges, Table 7 Gemini 0/2/3 of 13)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google-deepmind/dangerous-capability-evaluations/main/README.md"
    title: "DeepMind dangerous-capability-evaluations README (Apache-2.0 / CC-BY, stripped solutions)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/google-deepmind/dangerous-capability-evaluations/main/LICENSE"
    title: "DeepMind Apache License 2.0 for software"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gdm_in_house_ctf/README.md"
    title: "Inspect Evals in-house CTF README (13 challenges, epochs 10, changelog 6-A)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gdm_in_house_ctf/eval.yaml"
    title: "Inspect eval.yaml (gdm_in_house_ctf, 13 samples, version 6-A)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gdm_in_house_ctf/challenges/challenges.json"
    title: "Inspect challenges.json (13 named tasks, db_3 prompt fix)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT License"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-044 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-044"
---

## What it measures

GDM In-house CTF asks a bash agent on Kali whether it can finish 13 easy-to-medium attack labs DeepMind wrote for the 2024 dangerous-capability paper. Tasks cover web bugs, password attacks, two off-the-shelf CVEs, and local sudo/SUID privesc. The goal is a hidden flag string. This is not [cybench](cybench.md) (40 contest tasks) and not the paper's separate Hack The Box or InterCode-CTF suites.

Inspect's 13 names match Table 4, with `db` stored as `db_3`.

## How it is scored

The paper gives 10 attempts of 20 shell steps and counts a challenge solved if any attempt prints the flag. Inspect defaults to 10 epochs, 50 messages, `at_least_1`. Scorer `check_flag` reads the live flag from the sandbox and looks for it in the agent output. Sandbox read failures score INCORRECT instead of crashing (Inspect 2.1.0). Table 7: Gemini Nano 0/13, Pro 2/13, Ultra 3/13.

Inspect 6-A rewrote `db_3` so the prompt asks for the admin password, not a hash. Compare db_3 numbers only after 2026-05-05.

## Dataset and licence

Thirteen public briefs. Flags are not in git. DeepMind software is Apache-2.0; other materials CC-BY-4.0; Inspect MIT. `public_test_set` is false because flags live in pulled images, not the tree. Wordlist hints for four password tasks are Inspect's reading of the paper, not a leaked gold prompt.

## Who publishes it

Google DeepMind, first author Mary Phuong, arXiv 20 March 2024 (v2 5 April 2024). Original tree: `in_house_ctf` in google-deepmind/dangerous-capability-evaluations. Inspect port by XkunW; current metadata 6-A (2026-05-05). After 29 January 2026 the code lives in `gdm_in_house_ctf`, not `gdm_capabilities`.

## Lineage

One cyber slice of the 2024 programme that also includes [gdm_self_proliferation](gdm_self_proliferation.md), [gdm_self_reasoning](gdm_self_reasoning.md), and [gdm_stealth](gdm_stealth.md). Not Cybench, not InterCode-CTF, not Hack The Box. Those last two appear in the same paper and are not this id.

## Saturation and contamination

Ultra 1.0 solved three of thirteen in 2024. That is open relative to 13/13, and it is stale relative to 2026 agents. Prompts are public; solutions are not. Treat "13/13 Inspect" as a different protocol from Table 7 if epochs, hints, or the db_3 wording differ.

## How to run it

`uv run inspect eval inspect_evals/gdm_in_house_ctf --model ...` with Docker. Subset with `-T challenges=grafana,db_3`. Disable wordlist hints with `-T include_hints=false`. Do not drop network isolation. Building images locally needs real flags in place of `REPLACE_ME_WITH_RANDOM_FLAG_N`.

## Reading the numbers

A solved challenge means one epoch found the flag, not that the model is a useful attacker. Ultra's three wins were the shallow web and sudo cases. Pair with [cybench](cybench.md) for contest difficulty, and with the other GDM pages if the claim is dangerous capability rather than CTF trivia.
