---
id: mind2web_sc
name: "Mind2Web-SC"
aliases:
  - "Mind2Web SC"
  - "Mind2Web Safety Control"
page_kind: benchmark
category: safety
subcategory: "web-agent guardrails (SeeAct + user constraints)"
status: active
summary: "A GuardAgent safety eval: generate and execute code that grants or denies a SeeAct web action under six user-constraint rules."
measures: >
  Mind2Web-SC tests a guard model, not a web navigator. The model sees a user task from Mind2Web,
  a synthetic user profile (age plus boolean flags for membership, vaccine, driver's licence, and
  domestic status), and a SeeAct agent output. It must decompose the applicable safety rule,
  write Python guardrail code, and decide GRANT or DENY. On DENY it must also name the violated
  rule. English text plus executed code. It is not the [Mind2Web](mind2web.md) action-prediction
  task.
task_format: >
  Few-shot code generation (inspect default num_shots=3) inside a Docker sandbox. inspect_evals
  asks for task decomposition and guardrail code, runs the code, then parses "Action granted" /
  "Action denied" and an optional "Violation:" line. Paper metrics include label precision/recall
  and comprehensive control accuracy; inspect reports accuracy() plus accuracy grouped by domain.
metric:
  name: "accuracy (comprehensive correctness: decision plus violation on DENY)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: null
  baseline_note: >
    inspect JSON is balanced 100 ALLOW / 100 DENY, so chance on the binary decision is 50%;
    comprehensive correctness is stricter because DENY also requires the right violation string.
    The GuardAgent paper table reports 90.0% label-prediction accuracy for GuardAgent on
    Mind2Web-SC, and 80.0% on its comprehensive/final-response columns in the same row. The v3
    abstract instead says "over 98% and 83%" guardrail accuracies for EICU-AC and Mind2Web-SC
    respectively. No human baseline was stated.
dataset:
  size: 200
  size_note: >
    Paper and inspect file sample_labeled_all.json both hold 200 examples (100 label 0 / 100
    label 1). inspect_evals metadata says dataset_samples: 200. Domain mix in that JSON: Travel
    79, Shopping 65, Entertainment 56. The paper builds them from SeeAct-correct Mind2Web test
    tasks in travel, shop, and entertainment, with random user profiles and six hand-written
    rules. inspect_evals.mind2web_sc.utils.load_seeact_dataset currently slices raw_dataset[:10],
    so a default inspect run scores 10 of 200 unless that line is changed.
  url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/mind2web_sc"
  license: "inspect_evals MIT; GuardAgent paper HTML states CC BY 4.0; original data also hosted at guardagent/dataset"
  languages:
    - en
  modalities:
    - text
  splits: "single labeled pool of 200; no train/test split in inspect"
  public_test_set: true
publisher:
  org: "University of Georgia, University of Chicago, UIUC, UT Austin, UC Berkeley, Emory, Virtue AI (GuardAgent authors)"
  authors:
    - "Zhen Xiang"
    - "Linzhi Zheng"
    - "Yanjie Li"
    - "Junyuan Hong"
    - "Qinbin Li"
    - "Han Xie"
    - "Jiawei Zhang"
    - "Zidi Xiong"
    - "Chulin Xie"
    - "Carl Yang"
    - "Dawn Song"
    - "Bo Li"
  url: "https://guardagent.github.io/"
paper:
  title: "GuardAgent: Safeguard LLM Agents by a Guard Agent via Knowledge-Enabled Reasoning"
  arxiv: "2406.09187"
  url: "https://arxiv.org/abs/2406.09187"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/guardagent/code"
released: "2024-06"
last_updated: "2026-04"
lineage:
  family: ""
  predecessor: mind2web
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: 93.0
  as_of: "2025-05"
  note: >
    Paper Table 1 (v3 HTML, 29 May 2025), SeeAct on Mind2Web-SC, GuardAgent rows: Llama3.3-70B
    has the highest label-prediction accuracy at 93.0% (explanation accuracy 94.0%). GPT-4 is
    90.0% LPA / 80.0% EA. Llama3-70B is 83.5% LPA, which is the floor behind the abstract's
    "over 83%". No public live leaderboard. inspect's default 10-example slice is not comparable
    to the 200-example paper number.
contamination:
  risk: medium
  note: >
    The 200 labeled examples, user profiles, and six rules are public in inspect_evals (and in
    the GuardAgent dataset repo). They are derived from public Mind2Web test tasks plus synthetic
    profiles, not a held-out live site.
harness:
  lm_eval: ""
  inspect_evals: "mind2web_sc"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "`inspect eval inspect_evals/mind2web_sc` (Docker required). -T num_shots=3 default. Original runner: guardagent/code with --agent seeact."
tags:
  - safety
  - agentic
  - guardrail
  - code-generation
  - web-agent
sources:
  - url: "https://arxiv.org/abs/2406.09187"
    title: "GuardAgent paper abs (arXiv:2406.09187; 98%/83% abstract wording)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2406.09187"
    title: "GuardAgent HTML v3 (six rules, 200 examples, 90.0% table, CC BY 4.0)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/mind2web_sc/README.md"
    title: "inspect_evals mind2web_sc README (task, metrics, Docker, few-shot)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/mind2web_sc/eval.yaml"
    title: "inspect_evals mind2web_sc eval.yaml (task mind2web_sc, dataset_samples 200)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/mind2web_sc/utils.py"
    title: "inspect_evals mind2web_sc utils.py (loads only raw_dataset[:10])"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/mind2web_sc/scorer.py"
    title: "inspect_evals mind2web_sc scorer (comprehensive correctness)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/guardagent/code/main/README.md"
    title: "guardagent/code README (SeeAct + Mind2Web-SC dataset pointer)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/LICENSE"
    title: "inspect_evals MIT License"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/guardagent/dataset/main/README.md"
    title: "guardagent/dataset README (EICU-AC and Mind2Web-SC Drive downloads; no LICENSE file)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-012 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-012"
---

## What it measures

Mind2Web-SC asks whether a model can guard a web agent. Each item pairs a Mind2Web-style user request and SeeAct output with a fake user profile. The model must write code that checks six rules: membership to shop, vaccine to book a flight, a driver's licence to buy or rent a car, age 18+ to book a hotel, country flags to search media, and age 15+ to apply for jobs. It then GRANT or DENY the action. English. It is not [Mind2Web](mind2web.md) next-action prediction.

## How it is scored

inspect_evals runs the generated code in Docker and parses the printed decision. Accuracy is comprehensive: ALLOW/DENY must match the label, and a DENY must also name the expected violation. Domain accuracy is the same metric grouped by Travel, Shopping, or Entertainment. The paper instead reports label precision/recall, comprehensive control accuracy, and final response accuracy. Those names are not interchangeable with inspect's single accuracy(). Default few-shot is three code examples.

## Dataset and licence

The paper and inspect's `sample_labeled_all.json` both contain 200 examples, 100 per class, from SeeAct-correct Mind2Web test tasks in three domains. inspect eval.yaml records 200 samples. `load_seeact_dataset` currently returns only the first 10 rows. Original data is also advertised at github.com/guardagent/dataset. inspect_evals is MIT. The GuardAgent paper HTML states CC BY 4.0; a separate dataset licence file was not opened.

## Who publishes it

Zhen Xiang, Linzhi Zheng, Yanjie Li, Junyuan Hong, Qinbin Li, Han Xie, Jiawei Zhang, Zidi Xiong, Chulin Xie, Carl Yang, Dawn Song, and Bo Li introduced it in the GuardAgent paper (arXiv:2406.09187, 13 Jun 2024; v3 29 May 2025). Project page: guardagent.github.io. inspect_evals (UK AI Security Institute) hosts the portable task `mind2web_sc`.

## Lineage

Predecessor is [Mind2Web](mind2web.md): the tasks and SeeAct traces are reused, then overlaid with synthetic profiles and six rules. GuardAgent's other benchmark, EICU-AC, is a healthcare access-control set, not this id. Do not treat inspect `mind2web` and `mind2web_sc` as the same number.

## Saturation and contamination

Table 1's highest GuardAgent label accuracy on 200 items is 93.0% (Llama3.3-70B); GPT-4 is 90.0% LPA / 80.0% comprehensive. The abstract still quotes "over 83%", matching the Llama3-70B floor (83.5%). Those figures are author-reported; no independent leaderboard was opened here. The 200 items are public, so later models may have seen the rules and labels. inspect's 10-row default is a different experiment.

## How to run it

`inspect eval inspect_evals/mind2web_sc --model ...` with Docker. `-T num_shots=3` is the default. To match the paper's 200 items, the `raw_dataset[:10]` slice in utils.py has to be removed or raised; as shipped, inspect scores 10 examples. The original script is `python main.py --agent seeact` in guardagent/code after downloading their dataset.

## Reading the numbers

A high inspect accuracy means the model both decided GRANT/DENY correctly and, on denials, named the rule. It does not mean the underlying SeeAct agent completed the web task. Binary chance is 50% only for the decision bit. Do not compare inspect's 10-example default to the paper's 200-example table (Llama3.3-70B 93.0% LPA; GPT-4 90.0% LPA). For whether the agent clicks the right element at all, use [mind2web](mind2web.md).
