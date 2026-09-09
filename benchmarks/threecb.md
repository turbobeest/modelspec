---
id: threecb
name: ThreeCB
aliases: []
page_kind: benchmark
category: agentic
subcategory: cyber offense capture-the-flag
status: active
summary: 3CB (Catastrophic Cyber Capabilities Benchmark) scores LLM agents on capture-the-flag cyber offense challenges mapped to MITRE ATT&CK techniques.
measures: 3CB tests whether an LLM agent can perform offensive cyber tasks - reconnaissance, exploitation, privilege escalation, and related techniques - by solving capture-the-flag (CTF) challenges in a bash shell, each mapped to a MITRE ATT&CK technique.
task_format: Agent interacts with a containerized challenge environment (typically a bash shell) and must recover a flag string that proves successful exploitation.
metric: {name: "success rate", direction: higher_is_better, unit: fraction, max_score: 1, random_baseline: 0, human_baseline: null, baseline_note: "Success rate is the fraction of tasks solved; a task counts as solved if any one of N repeated attempts (default 10 in the Inspect Evals port) recovers the correct flag."}
dataset: {size: 15, size_note: "The original paper describes 15 original CTF-style challenges spanning 14 MITRE ATT&CK strategies; the Inspect Evals port currently implements 11 of these as containerized tasks.", url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/threecb, license: "CC BY-NC-SA 4.0 (paper/dataset, per arXiv)", languages: [English], modalities: [text, code], splits: "", public_test_set: true}
publisher: {org: Apart Research, authors: [Andrey Anurin, Jonathan Ng, Kibo Schaffer, Jason Schreiber, Esben Kran], url: https://cybercapabilities.org}
paper: {title: "Catastrophic Cyber Capabilities Benchmark (3CB): Robustly Evaluating LLM Agent Cyber Offense Capabilities", arxiv: "2410.09114", url: https://arxiv.org/abs/2410.09114, year: 2024}
leaderboard_url: https://cybercapabilities.org
repo_url: https://github.com/UKGovernmentBEIS/inspect_evals
released: "2024-10"
last_updated: ""
lineage: {family: "", predecessor: "", successors: [], variants: []}
saturation: {status: watch, top_score: null, as_of: "", note: "The paper reports Claude 3.5 Sonnet (75%) and GPT-4o (73%) as top scorers overall, but per-challenge results vary widely (one challenge solved only 3% of the time), so the aggregate can mask which techniques remain hard."}
contamination: {risk: medium, note: "The authors built original challenges specifically to avoid memorization from existing public CTFs, but the paper and challenge descriptions are now themselves public."}
harness: {lm_eval: "", inspect_evals: threecb, helm: "", opencompass: "", bigbench: "", other: ""}
tags: [agents, cybersecurity, capture-the-flag, tool-use, dual-use]
sources:
  - url: https://arxiv.org/abs/2410.09114
    title: "3CB paper (arXiv abstract)"
    accessed: "2026-09-08"
  - url: https://apartresearch.com/post/catastrophic-cyber-capabilities-benchmark-robustly-evaluating-llm-agent-cyber-offense-capabilities
    title: Apart Research 3CB project post
    accessed: "2026-09-08"
  - url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/threecb
    title: Inspect Evals ThreeCB integration
    accessed: "2026-09-08"
  - url: https://github.com/UKGovernmentBEIS/inspect_evals
    title: Inspect Evals repository
    accessed: "2026-09-08"
freshness: {researched: "2026-09-08", researched_by: GPT-5.6 Luna, luna-new-001 (Codex coordinated), reviewed: "2026-09-08", reviewed_by: "Claude Sonnet 5 independent review, luna-new-001"}
---

## What it measures

3CB (the "Catastrophic Cyber Capabilities Benchmark") tests whether an LLM agent can carry out offensive cyber operations: reconnaissance, exploitation, privilege escalation, evasion, and related techniques drawn from the MITRE ATT&CK framework. Each task is a capture-the-flag (CTF) style challenge in a containerized environment, typically driven through a bash shell, and the agent must recover a flag string that proves it completed the attack technique.

The benchmark is explicitly dual-use: it is designed to measure how close current models are to being able to autonomously carry out real cyber offense, which is safety-relevant as much as it is a capability score.

## How it is scored

Success rate is the fraction of tasks solved. The Inspect Evals port allows multiple elicitation attempts per task (default 10 repeats) and counts a task as solved if any single attempt recovers the flag, then reports the resulting success rate with a standard error. The authors of the Inspect adaptation note that its numbers are not directly comparable to the original paper's, because of differences in prompting and communication protocol between agent and environment: for example, the Inspect port measured GPT-4o at 0.818 ± 0.116 versus 0.73 in the original paper.

## Dataset and licence

The original paper built 15 original CTF-style challenges, chosen to avoid memorization from existing public CTF archives, with full coverage of at least one technique in each of 14 MITRE ATT&CK strategies. The arXiv listing states a CC BY-NC-SA 4.0 licence for the paper. The Inspect Evals port, distributed under the UK AI Security Institute's inspect_evals repository, implements 11 of these as Docker-based tasks; it does not state its own separate licence for the ported task code.

## Who publishes it

Apart Research published 3CB in an October 2024 paper by Andrey Anurin, Jonathan Ng, Kibo Schaffer, Jason Schreiber, and Esben Kran. Apart Research maintains a project site at cybercapabilities.org; the UK AI Security Institute's Inspect Evals project maintains a separate, partial reimplementation as the `threecb` task.

## Lineage

3CB is a standalone benchmark with no established predecessor in this repository. The Inspect Evals `threecb` task is a partial port (11 of the original 15 challenges) and should be treated as a distinct, non-identical variant rather than a full restatement of the paper's benchmark.

## Saturation and contamination

The paper reports Claude 3.5 Sonnet (75%) and GPT-4o (73%) as the strongest models overall, but per-challenge results vary sharply - one challenge was solved in only 3% of attempts - so the benchmark still separates models at the task level even where aggregate scores cluster near the top. Contamination risk is medium: the challenges were built to be novel and unseen in existing CTF corpora, but the challenges themselves are now public via the paper and project site.

## How to run it

Run the original 3CB challenges from the paper's release (see cybercapabilities.org) or Inspect Evals task `threecb`, which currently covers 11 of the 15 challenges. Record which implementation, how many repeated elicitations per task, the agent scaffold, and the model's tool/shell access, since the two implementations are not numerically comparable.

## Reading the numbers

A high success rate indicates the agent can complete specific, scripted offensive cyber techniques in a controlled container; it does not establish real-world cyber offense capability against unscripted targets, nor does it establish defensive competence. Compare scores only within the same implementation (paper vs. Inspect port) given the documented gap between the two on at least one model.

Because scores are pooled across techniques with very different difficulty, look at per-challenge or per-technique results rather than the aggregate alone to see where a model's offensive capability actually lies.
