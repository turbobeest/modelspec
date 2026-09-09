---
id: cti_realm
name: "CTI-REALM"
aliases:
  - "CTI REALM"
  - "Cyber Threat Real World Evaluation and LLM Benchmarking"
page_kind: benchmark
category: agentic
subcategory: "agentic detection-rule writing from CTI reports against Kusto telemetry"
status: active
summary: "Inspect AI agent benchmark where a model writes Sigma and KQL detection rules from cyber threat intelligence reports against live Kusto telemetry."
measures: >
  CTI-REALM (Cyber Threat Real World Evaluation and LLM Benchmarking) tests
  whether an AI agent can turn a detection objective and public CTI reports
  into working detections. The agent must find a relevant report, map MITRE
  ATT&CK techniques, explore Kusto tables, write and run KQL, and emit a Sigma
  rule plus query results as JSON. The environment is a Docker stack with a
  shared Kusto emulator, 12 log sources, 37 CTI reports, and cached MITRE and
  Sigma stores. Attacks are emulated on Linux endpoints, Azure Kubernetes
  Service (AKS), and Azure cloud. Scoring is a five-checkpoint trajectory
  reward in [0, 1], not a static multiple-choice grade. This page treats it as
  agentic because success depends on tool use against live telemetry.
task_format: >
  ReAct agent, English. inspect_evals defaults: message_limit 70, one epoch,
  hard difficulty (minimal workflow hints). Output must be JSON with
  sigma_rule, kql_query, and query_results. Tools include Kusto query/schema
  helpers, CTI retrieval, MITRE lookup, and Sigma lookup. bash and python run
  in a per-sample sandbox without Kusto network access. Four tasks:
  cti_realm_25, cti_realm_50, cti_realm_25_minimal (CTI tools removed),
  cti_realm_25_seeded (workflow files in /memories/).
metric:
  name: "weighted trajectory reward R_total in [0, 1]"
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Weights: C0 CTI analysis 0.125 (LLM judge), C1 MITRE mapping 0.075
    (Jaccard), C2 data exploration 0.100 (Jaccard), C3 query execution 0.050
    (binary: ≥2 successful queries), C4 detection quality 0.650 (KQL F1 plus
    Sigma judge). C0–C3 are 35%; C4 is 65%. Default grader
    openai/azure/gpt-5-mini. inspect_evals README table (CTI-REALM-50, 16
    models, message_limit=70, task version 1-A, February–March 2026):
    claude-opus-4-6 0.6373. The paper tags that cell as Claude Opus 4.6
    (High) at 0.637. No random-guess or human-operator baseline.
dataset:
  size: 50
  size_note: >
    Full set CTI-REALM-50: 50 samples (25 Linux, 17 AKS, 8 Cloud).
    CTI-REALM-25 is a 25-sample subset (12 Linux, 9 AKS, 4 Cloud). Hugging Face
    arjun180-new/cti_realm also ships 37 CTI reports (reports.jsonl), Sigma
    rules JSON, seed-memory markdown, and 12 Kusto jsonl logs. inspect_evals
    pins MITRE STIX from mitre/cti commit 68d2992. The Hub card has no licence
    tag.
  url: "https://huggingface.co/datasets/arjun180-new/cti_realm"
  license: "MIT (inspect_evals package and CTI_REALM_TRANSPARENCY.md); Hugging Face dataset licence not stated"
  languages:
    - en
  modalities:
    - text
  splits: "no train split; 25-sample subset and 50-sample full eval"
  public_test_set: true
publisher:
  org: "Microsoft Security AI (inspect_evals packaging by UK AI Security Institute)"
  authors:
    - "Arjun Chakraborty"
    - "Sandra Ho"
    - "Adam Cook"
    - "Manuel Meléndez"
  url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/cti_realm"
paper:
  title: "CTI-REALM: Benchmark to Evaluate Agent Performance on Security Detection Rule Generation Capabilities"
  arxiv: "2603.13517"
  url: "https://arxiv.org/abs/2603.13517"
  year: 2026
leaderboard_url: ""
repo_url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/cti_realm"
released: "2026-03"
last_updated: "2026-06"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 0.6373
  as_of: "2026-03"
  note: >
    inspect_evals README: Claude Opus 4.6 at 0.6373 on CTI-REALM-50 (95% CI
    0.562–0.712), well below 1.0. The paper labels that run High reasoning.
    The README states the benchmark is not saturated. Platform averages in
    that report: Linux 0.585, AKS 0.517, Cloud 0.282. Version 4-A (2026-06-10)
    changed the Kusto runtime; a two-model re-run was comparable to 2-A, not a
    new 16-model table.
contamination:
  risk: medium
  note: >
    CTI reports are public vendor write-ups. Telemetry is emulated and shipped
    on the Hub. Ground-truth rules are in the download bundle. That is enough
    for leakage into later training runs, but the live KQL F1 still needs the
    sandbox. No publisher contamination study was opened here.
harness:
  lm_eval: ""
  inspect_evals: "cti_realm_50"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Also cti_realm_25, cti_realm_25_minimal, cti_realm_25_seeded. There is no
    inspect task named exactly cti_realm. eval.yaml version 4-A. Run as
    inspect eval inspect_evals/cti_realm_50.
tags:
  - agentic
  - cybersecurity
  - detection-engineering
  - kql
  - sigma
  - inspect-evals
sources:
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/cti_realm/README.md"
    title: "inspect_evals CTI-REALM README (tasks, scoring, 16-model table, changelog)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/cti_realm/eval.yaml"
    title: "eval.yaml (arxiv 2603.13517, four tasks, HF pin, version 4-A)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/cti_realm/CTI_REALM_TRANSPARENCY.md"
    title: "CTI-REALM transparency note (MIT licence, intended use)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/cti_realm/cti_realm.py"
    title: "Task constructors cti_realm_25/50/_minimal/_seeded"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT License"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2603.13517"
    title: "CTI-REALM paper abs (Microsoft Security AI; v2 2026-03-17)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/arjun180-new/cti_realm"
    title: "Hub API arjun180-new/cti_realm (files; no licence tag)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-036 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-036"
---

## What it measures

CTI-REALM asks an agent to write detections the way a security analyst would. The model gets a detection objective, a CTI report library, Kusto tables, and MITRE/Sigma lookups. It must return a Sigma rule, a KQL query, and the rows that query actually returns. The setting is Linux, AKS, and Azure cloud telemetry from emulated attacks, not a quiz about ATT&CK IDs.

This is not [cti_to_mitre](cti_to_mitre.md), which maps one CTI sentence to a technique name. It is also not [cybench](cybench.md) or [cve_bench](cve_bench.md), which score offensive capture-the-flag or live CVE exploitation.

## How it is scored

The headline is a weighted reward in [0, 1]. C4 (detection quality) is 65% of the mass. C0 and C4 Sigma use an LLM judge; the default grader is Azure GPT-5-mini. C1 and C2 use Jaccard overlap. C3 is a binary “did the agent run at least two successful queries.” Unparseable JSON used to return an invalid FAILED score; version 3-A (2026-06-10) returns zeros instead. Changing the grader, `message_limit`, or task version moves the number. The README’s 16-model table used version 1-A and one epoch; the authors say three epochs on the 25-set is the more stable protocol.

## Dataset and licence

The full eval is 50 samples. The 25-set is a stratified subset. Hugging Face `arjun180-new/cti_realm` holds reports, answers, Sigma JSON, and Kusto logs. The Hub API `usedStorage` field is 2,199,432,855 bytes (about 2.05 GiB). inspect_evals is MIT. The transparency note is also MIT. The Hub dataset has no licence field, so the data licence is not established. Reports come from Microsoft Security, Datadog Security Labs, Palo Alto Networks, and Splunk Security Content.

## Who publishes it

Arjun Chakraborty, Sandra Ho, Adam Cook, and Manuel Meléndez (Microsoft Security AI) wrote the paper (arXiv:2603.13517, March 2026). The reference implementation lives in UK AISI inspect_evals, contributor `arjun180-new`. inspect_evals 1-A is dated 2026-03-27; 4-A (2026-06-10) shares one Kusto container across samples. There is no separate public leaderboard beyond that README table.

## Lineage

CTI-REALM is a detection-engineering agent bench, not a static CTI classifier. [cti_to_mitre](cti_to_mitre.md) is the HELM wrap of Orbinato et al. 2022 sentence-to-technique classification. No successor id is in this repository.

## Saturation and contamination

The best reported cell is 0.6373 on the 50-set (Claude Opus 4.6; the paper tags High reasoning), with a wide confidence interval. Cloud samples score much lower than Linux. The authors call the bench unsaturated. Public CTI text and shipped ground-truth rules can leak into later pretraining; the live F1 still needs the emulator.

## How to run it

Download data with `download_data.py` (needs Docker and several GB). Then `uv run inspect eval inspect_evals/cti_realm_50 --model …`. Use `cti_realm_25` for the subset, `_minimal` to drop CTI tools, `_seeded` to preload workflow notes. Set `--model-role grader=…` if you change the judge. First start is slow because of the ~4.5 GB Kusto image. Do not compare 1-A scores to 4-A without noting the runtime change.

## Reading the numbers

0.64 is a strong agent on this harness, not a solved detection-engineering job. C4 dominates, so a model that writes pretty Sigma and fails KQL F1 will look worse than the trajectory scores suggest. Judge choice, seed memory, and tool ablation each move results by several points in the README. Read Linux/AKS/Cloud separately. Pair with [cti_to_mitre](cti_to_mitre.md) only if you also need static technique naming.
