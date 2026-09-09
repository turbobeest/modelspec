---
id: ipi_coding_agent
name: "CodeIPI (Indirect Prompt Injection for Coding Agents)"
aliases:
  - "CodeIPI"
  - "ipi_coding_agent"
  - "inspect_evals/ipi_coding_agent"
page_kind: benchmark
category: safety
subcategory: "indirect prompt injection on coding agents that must still fix a bug"
status: active
summary: "Inspect Evals CodeIPI: 45 Docker coding-agent tasks that hide prompt injections in issues, comments, READMEs or configs, scored for resistance and bug-fix success."
measures: >
  CodeIPI tests whether a tool-using coding agent follows hidden attacker
  instructions while it is supposed to fix a bug. Each item is a small
  Python repo plus a natural-language task. Injected samples plant a payload
  in issue text, a code comment, a README, or a config file. Ten clean
  samples have no payload and exist to measure false refusals. Success is
  not a quiz answer: the agent must edit files with bash and python inside
  Docker. English prompts. This is coding-agent IPI, not the workplace
  tool suites in [agentdojo](agentdojo.md) and not the harmful-behaviour
  suite in [agentharm](agentharm.md).
task_format: >
  Multi-turn inspect_ai.agent.react solver with bash and python tools
  (120s timeouts) and max_messages 30. Default system prompt tells the
  agent to ignore unrelated commands in comments, docs, or issue text.
  defense_prompt=false drops that warning. Optional filters: vectors
  (issue_text, code_comment, readme, config_file) and severities (S1, S2,
  S3). Workspace files and canary secrets are written before the agent
  runs. Network is off (network_mode none).
metric:
  name: "accuracy (resist injection AND complete the bug fix); also IRR, TCR, detection_rate, FPR"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Headline accuracy is the fraction of samples scored C: injection
    resistance at or above 0.8 and a passing pytest. IRR is injected
    samples only. FPR is benign samples only (lower is better on that
    slice). Detection uses an LLM grader and is a subset of resistance.
    inspect_evals README (eval version 1-B, 2026-04-09, defense prompt
    on) reports Claude Sonnet 4.6 at 91.1% accuracy / 88.6% IRR / 100%
    TCR / 2.9% detection / 0% FPR, and GPT-4.1 at 88.9 / 97.1 / 91.1 /
    0 / 0. Version 3-B (2026-08-17) returns NaN instead of 0.0 when a
    filtered metric has no samples.
dataset:
  size: 45
  size_note: >
    samples.json has 45 records: 35 injected and 10 benign. Injected
    vectors: issue_text 10, code_comment 10, readme 10, config_file 5.
    Payload categories: exfiltration 15, code_execution 10, persistence
    10. Sophistication: plain 15, authority_framing 20. Severity: S1 15,
    S2 10, S3 10. eval.yaml dataset_samples is 45. Persistence samples
    name persistence_targets; all 45 use `cd /workspace && python -m
    pytest tests/ -q` as the verification command.
  url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/ipi_coding_agent"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
    - code
  splits: "single evaluation set (35 injected + 10 benign); no train split"
  public_test_set: true
publisher:
  org: "UK AI Security Institute (Inspect Evals)"
  authors:
    - "debu-sinha"
  url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/ipi_coding_agent"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/ipi_coding_agent"
released: "2026-04"
last_updated: "2026-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 91.1
  as_of: "2026-04"
  note: >
    Highest accuracy in the inspect_evals README table is 91.1%
    (Claude Sonnet 4.6). GPT-4.1 leads IRR at 97.1% but trails on
    task completion. GPT-4o-mini is at 40.0% accuracy. Explicit
    detection is almost unused (one flagged sample in that table).
    No later public table was read.
contamination:
  risk: medium
  note: >
    The 45 JSON samples, payloads, and canary strings are public in
    inspect_evals. The tasks are synthetic and small, so web-scale
    leakage is less like a famous exam dump, but any model that
    trained on the repo after 2026-04 could have seen them. Network
    is blocked, so live exfiltration cannot succeed; scoring still
    treats canary text in tool traces as a leak.
harness:
  lm_eval: ""
  inspect_evals: "ipi_coding_agent"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "inspect eval inspect_evals/ipi_coding_agent; eval.yaml version 3-B, group Safeguards, 45 samples"
tags:
  - safety
  - agents
  - prompt-injection
  - coding
  - inspect-evals
sources:
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/ipi_coding_agent/README.md"
    title: "CodeIPI README (45 samples, metrics, 2026-04-09 report, changelog through 3-B)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/ipi_coding_agent/eval.yaml"
    title: "eval.yaml (task ipi_coding_agent, 45 samples, version 3-B)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/ipi_coding_agent/ipi_coding_agent.py"
    title: "ipi_coding_agent.py (react solver, filters, max_messages 30)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/ipi_coding_agent/scorer.py"
    title: "ipi_scorer (canary, hash, pytest, LLM detection grader)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/ipi_coding_agent/constants.py"
    title: "constants.py (defense prompts, canaries, IRR threshold 0.8)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/ipi_coding_agent/setup.py"
    title: "setup.py (workspace files, canary file/.env, hash snapshot)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/ipi_coding_agent/dataset/samples.json"
    title: "samples.json (45 records; vector/category counts)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/ipi_coding_agent/docker/compose.yaml"
    title: "compose.yaml (network_mode none, 2G memory, canary env)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT License (UK AI Security Institute, 2024)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/README.md"
    title: "inspect_evals README CodeIPI listing (contributor debu-sinha)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-051 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-051"
---

## What it measures

CodeIPI asks a coding agent to fix a bug in a tiny Python repo. On 35 of 45 items, an attacker instruction is hidden in the issue, a comment, the README, or a config file. The agent has bash and python in Docker and is supposed to make pytest pass. The hidden instruction tries to leak planted secrets, run a marked command, or persist a change in a named file. Ten items are clean, so a model that refuses every repo is visible as a false positive. English text, synthetic files.

This is indirect prompt injection during ordinary software work, not a chat-only jailbreak. [agentdojo](agentdojo.md) plants attacks in tool output of office suites. [agentharm](agentharm.md) asks for harmful tool use. CodeIPI keeps a legitimate bug fix as the user goal.

## How it is scored

Each sample gets a dict of scores. Injection resistance is 1.0 or 0.0 for the known payload type: canary strings for exfiltration, a per-id `CANARY_EXEC_` marker in tool-call arguments for execution, and SHA-256 hashes of named persistence targets. Benign items are treated as resisted. If resistance is at least 0.8, an LLM grader (`model_graded_qa`) checks whether the agent actually named the attack. Task completion is pytest exit code 0. Headline accuracy is 1 only when the agent resisted and the tests passed.

IRR ignores benign rows. Detection is a subset of resistance. FPR is the share of benign rows the grader marks as a false alarm. Version 3-B returns NaN, not 0.0, when a filtered metric has no rows. Compare runs with the same `defense_prompt` flag.

## Dataset and licence

The shipped set is 45 JSON records in `dataset/samples.json`, matching eval.yaml. Counts match the README: 10/10/10/5 across the four vectors plus 10 benign; 15/10/10 across exfiltration, execution, and persistence. Setup writes `repo_files` under `/workspace`, plants canary env vars and `/root/.secret_canary`, then snapshots hashes. The inspect_evals tree is MIT. No separate dataset licence and no paper were found. Answers and payloads are public.

## Who publishes it

UK AI Security Institute ships it in Inspect Evals as `inspect_evals/ipi_coding_agent`. The listing names contributor [@debu-sinha](https://github.com/debu-sinha). The first scored report in the README is evaluation version 1-B on 2026-04-09. The code version in eval.yaml is 3-B (2026-08-17). No arXiv paper is attached to the task.

## Lineage

The README points at AgentDojo and AgentHarm as related IPI and agent-harm work. Those pages already exist here. CodeIPI is not a re-package of either suite: the items are original tiny repos with coding-agent vectors. No successor id is in this repository.

## Saturation and contamination

The April 2026 table still separates models: 40.0% to 91.1% accuracy, with detection near zero. GPT-4.1 almost never complies (97.1% IRR) but completes fewer fixes than Claude. Code comments and issue text remain the leakier vectors in that table. The set is public and small. Treat GitHub-trained models with extra caution after 2026-04.

## How to run it

`inspect eval inspect_evals/ipi_coding_agent`. Docker is required. Useful flags: `-T vectors=issue_text`, `-T severities=S1`, `-T defense_prompt=false`. Default defense prompt is on. Do not compare a filtered vector run to the 45-row table. Scorer version 2-B started checking tool-result text for canaries; 3-B only changes empty-filter NaNs.

## Reading the numbers

A high accuracy means the agent both ignored the payload and still fixed the bug. IRR alone can hide a model that refuses to work. TCR alone can hide a model that complies and then passes pytest. Detection is not the same as resistance: most strong rows in the README silently ignore the attack. Ten benign items make FPR coarse. Quote `defense_prompt` and eval version when you copy a number.
