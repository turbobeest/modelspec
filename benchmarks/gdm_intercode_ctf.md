---
id: gdm_intercode_ctf
name: "GDM InterCode CTF"
aliases:
  - "InterCode-CTF"
  - "InterCode CTF"
  - "inspect_evals/gdm_intercode_ctf"
page_kind: benchmark
category: agentic
subcategory: "picoCTF capture-the-flag in a Docker sandbox (Inspect GDM port)"
status: active
summary: "78 picoCTF tasks from InterCode-CTF: a tool-using agent must recover picoCTF{...} flags in Docker, as used in DeepMind's 2024 cyber evals."
measures: >
  The agent is a capture-the-flag player on Ubuntu. Each item is a picoCTF challenge
  from InterCode-CTF: a natural-language brief, local assets, and a hidden flag of
  the form picoCTF{...}. Categories include general Linux skill, reverse engineering,
  cryptography, forensics, binary exploitation, and web exploitation. Success is
  finding the flag with bash and python tools, not answering a static quiz. English
  prompts. Inspect Evals runs 78 of the original 100 tasks (22 internet-requiring
  tasks are dropped). DeepMind used the same suite in its 2024 dangerous-capability
  cyber evals, with a different exclusion list.
task_format: >
  Multi-turn ReAct agent in Docker. Default solver is inspect_ai.agent.react with
  bash and python (180s timeouts) and a submit tool. Defaults: max_attempts 3,
  max_messages 50. Scorer is includes() on the gold flag string. Task-level sandbox
  via bundled compose, or a caller-supplied SandboxEnvironmentSpec.
metric:
  name: accuracy
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Binary per-task success (flag found or not). Inspect README (evaluation version
    2.1.0, February 2026) reports claude-opus-4-5-20251101 at 0.936 (stderr 0.028)
    and gpt-5.1-2025-11-13 at 0.897 (stderr 0.035) on the 78-sample set, one epoch.
    DeepMind Table 6 on 81 tasks: Gemini Nano 6/81, Pro 22/81, Ultra 24/81.
dataset:
  size: 78
  size_note: >
    InterCode-CTF is 100 picoCTF tasks (Yang et al. 2023). Inspect filters 22 ids
    that need the internet: 1, 7, 9, 14, 16, 20, 28, 29, 35, 39, 41, 42, 43, 54,
    57, 62, 66, 73, 87, 88, 89, 95 (eval.yaml dataset_samples: 78). DeepMind's
    main text omits 19 internet tasks (footnote list matches 19 of those ids) and
    scores 81 remaining in Table 6. Inspect README also claims DeepMind dropped
    seven extra non-internet ids; that 26-task story does not match Table 6's 81.
    Data are loaded from princeton-nlp/intercode at commit
    c3e46d827cfc9d4c704ec078f7abf9f41e3191d8 (ic_ctf.json plus task_assets).
  url: "https://github.com/princeton-nlp/intercode"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
    - code
  splits: "single evaluation set; no train split. Inspect pins a GitHub zip of the CTF folder."
  public_test_set: true
publisher:
  org: "Princeton NLP (InterCode); Google DeepMind (2024 protocol); UK AI Security Institute (Inspect Evals port)"
  authors:
    - "John Yang"
    - "Akshara Prabhakar"
    - "Karthik Narasimhan"
    - "Shunyu Yao"
  url: "https://intercode-benchmark.github.io/#ctf"
paper:
  title: "InterCode: Standardizing and Benchmarking Interactive Coding with Execution Feedback"
  arxiv: "2306.14898"
  url: "https://arxiv.org/abs/2306.14898"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/gdm_intercode_ctf"
released: "2023-06"
last_updated: "2026-06"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 0.936
  as_of: "2026-02"
  note: >
    Inspect README, 78 tasks, one epoch, version 2.1.0 (February 2026): Claude
    Opus 4.5 at 0.936. DeepMind Gemini Ultra 1.0 was 24/81. The two denominators
    are not the same set.
contamination:
  risk: high
  note: >
    picoCTF tasks and InterCode assets are public. Inspect's loader also reads
    each task's solution/README.md into sample metadata. Flags follow a known
    picoCTF{...} pattern. No source opened here measured training overlap.
harness:
  lm_eval: ""
  inspect_evals: "gdm_intercode_ctf"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    inspect eval inspect_evals/gdm_intercode_ctf. eval.yaml version 4-B
    (2026-06-17). Changelog 4-A (2026-04-21) replaced basic_agent() with react().
    Needs Docker. Not Cybench and not DeepMind's separate in-house or Hack The Box CTFs.
tags:
  - agentic
  - cybersecurity
  - capture-the-flag
  - inspect-evals
  - gdm
  - intercode
  - docker
sources:
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gdm_intercode_ctf/README.md"
    title: "Inspect Evals gdm_intercode_ctf README (78 tasks, GDM exclusion table, Feb 2026 scores)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gdm_intercode_ctf/eval.yaml"
    title: "eval.yaml (task gdm_intercode_ctf, 78 samples, version 4-B, arXiv 2306.14898)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gdm_intercode_ctf/dataset.py"
    title: "dataset.py (pinned intercode commit, 22 excluded ids, prompt and solution loader)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/gdm_intercode_ctf/gdm_intercode_ctf.py"
    title: "Task constructor (react agent, includes() scorer, Docker compose sandbox)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2306.14898"
    title: "InterCode paper (arXiv:2306.14898); 100 picoCTF InterCode-CTF tasks"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2306.14898"
    title: "InterCode HTML (CTF as <instruction, assets, hidden flag>)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2403.13793"
    title: "Evaluating Frontier Models for Dangerous Capabilities (arXiv:2403.13793)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2403.13793"
    title: "GDM paper HTML (19 omitted internet CTFs; Table 6 6/81, 22/81, 24/81)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/princeton-nlp/intercode/master/README.md"
    title: "princeton-nlp/intercode README (MIT badge; CTF among InterCode envs)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/princeton-nlp/intercode/master/LICENSE.md"
    title: "InterCode MIT License (Princeton NLP, 2023)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT License (UK AI Security Institute, 2024)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-045 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-045"
---

## What it measures

GDM InterCode CTF asks whether a tool-using agent can solve easy picoCTF challenges inside a sandbox. Each task ships a short English brief and local files. The agent must recover a flag string of the form `picoCTF{...}`. The original InterCode paper built 100 such tasks as an interactive coding environment, with execution feedback instead of one-shot code generation. Google DeepMind reused the suite in 2024 as a cyber dangerous-capability probe on Gemini 1.0. Inspect Evals is the public runnable port. It is not [Cybench](cybench.md), and it is not DeepMind's separate in-house or Hack The Box CTFs from the same paper.

## How it is scored

Inspect scores each of 78 tasks as success if the submitted text includes the gold flag (`includes()`). The headline figure is mean accuracy on that set. Defaults are three submit attempts and 50 messages. DeepMind scored 81 tasks after dropping 19 internet challenges, and reported category fractions for Gemini Nano, Pro, and Ultra (Table 6: 6/81, 22/81, 24/81). Those 81-task rates are not comparable to Inspect's 78-task table without mapping ids. Inspect's February 2026 report used one epoch and `react()` (since changelog 4-A, 2026-04-21), not DeepMind's bash-only shell.

## Dataset and licence

InterCode-CTF has 100 picoCTF items. Inspect downloads `princeton-nlp/intercode` at commit `c3e46d8` and drops 22 ids that need the network, leaving 78. DeepMind's footnote lists 19 omitted internet ids; Table 6's 81 matches 100 minus those 19. Inspect's README also says DeepMind dropped seven extra non-internet tasks; that 26-count does not match Table 6. InterCode and inspect_evals are MIT. picoCTF challenge text is not given a separate licence in the files opened here. Solutions ship in `task_assets/*/solution/README.md` and are copied into sample metadata.

## Who publishes it

John Yang, Akshara Prabhakar, Karthik Narasimhan, and Shunyu Yao released InterCode in June 2023 (arXiv:2306.14898, v3 October 2023). DeepMind's dangerous-capability paper (Phuong et al., March 2024) is the GDM protocol. UK AISI hosts the Inspect task (`gdm_intercode_ctf`), contributed by jjallaire. Folder split from a shared GDM evals directory in inspect_evals 2.0.0 (2026-01-29). No public live leaderboard was opened.

## Lineage

This page is the Inspect spelling `gdm_intercode_ctf`, not a second InterCode-CTF id. InterCode also ships Bash, SQL, and Python environments; those are not this page. DeepMind's 2024 paper adds other cyber suites (in-house CTF, Hack The Box) that Inspect does not run here. [Cybench](cybench.md) is a later, harder 40-task professional CTF eval.

## Saturation and contamination

Inspect's 2026 Claude Opus 4.5 run sits at 0.936 on 78 tasks, so the easy picoCTF slice no longer separates frontier agents well. Gemini Ultra's 24/81 in 2024 is a different set and harness. Assets, flags, and written solutions are public, so contamination risk is high. Compare only matching exclusion lists and agent stacks.

## How to run it

`uv run inspect eval inspect_evals/gdm_intercode_ctf --model ...` after Docker is installed. Optional `-T` flags: `shuffle`, `max_attempts`, `max_messages`, `sample_ids`, package lists, `sandbox_config`. Changelog 4-B (2026-06-17) added k8s-style sandbox specs. The bundled image is generated from `Dockerfile.template`. Do not compare bash-only DeepMind traces with Inspect's bash-plus-python `react()` agent.

## Reading the numbers

A 0.9 Inspect score means the agent submitted the right flag on most of 78 offline picoCTF tasks, not that it can do live professional CTF. Quote the task count (78 vs 81 vs 100), the excluded ids, and whether tools include Python. `includes()` can credit a flag buried in extra text. Solutions in the download make memorisation hard to rule out. Pair this number with a harder suite such as [Cybench](cybench.md) before talking about cyber capability.
