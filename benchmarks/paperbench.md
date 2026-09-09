---
id: paperbench
name: PaperBench
aliases:
  - PaperBench
  - PaperBench Code-Dev
page_kind: benchmark
category: agentic
subcategory: from-scratch replication of ML research papers
status: active
summary: >
  Agents must replicate 20 ICML 2024 Spotlight and Oral papers from scratch against
  author-written rubrics totaling 8,316 leaf criteria.
measures: >
  PaperBench gives an agent a paper PDF or Markdown file, an author addendum, and
  a sandbox with code execution. The agent must write a repository from scratch,
  including a reproduce.sh entrypoint, that reimplements the paper's empirical
  work. It may not use the authors' original code (blacklisted URLs). After the
  attempt, a fresh machine runs reproduce.sh, then an LLM judge scores the
  executed submission against a hierarchical rubric co-written with a paper
  author. A lighter Code-Dev variant skips execution and scores only code-development
  leaves.
task_format: >
  Long-horizon agent task. Output is a codebase plus reproduce.sh. The paper
  caps reproduce.sh at 12 hours in its experiments and does not cap agent
  runtime. inspect_evals defaults both agent time and reproduce.sh to 6 hours.
  Grading is a weighted tree of binary leaf checks (code development, execution,
  result match) rolled up to one replication score.
metric:
  name: replication score (weighted fraction of satisfied rubric leaves)
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 0
  human_baseline: null
  baseline_note: >
    Chance is effectively zero. The paper's main-setup best agent, Claude 3.5
    Sonnet (New) with BasicAgent, scored 21.0% ± 0.8. The project README
    leaderboard (dated 2025-04-02) lists IterativeAgent o1-high at 26.0% ± 0.3
    under a 36-hour limit. ML PhDs on a 3-paper subset reached 41.4% (best of 3,
    48 hours) versus 26.6% for o1 on that subset; that is not a 20-paper human
    baseline. PaperBench Code-Dev o1-high scored 43.4% ± 0.8.
dataset:
  size: 20
  size_note: >
    20 ICML 2024 Spotlight and Oral papers in the paper's test set, with 8,316
    individually gradable rubric leaves. inspect_evals documents 23 papers when
    split is None (20 prod + 3 dev); prod is the 20-paper paper split. Hugging
    Face josancamon/paperbench is MIT-licensed and holds the 20-paper files.
  url: https://huggingface.co/datasets/josancamon/paperbench
  license: MIT
  languages:
    - en
  modalities:
    - text
    - image
    - code
  splits: "prod/all: 20 papers; inspect_evals also exposes a 3-paper dev split; Code-Dev is a scoring variant, not a second item pool"
  public_test_set: true
publisher:
  org: OpenAI
  authors:
    - Giulio Starace
    - Oliver Jaffe
    - Dane Sherburn
    - James Aung
    - Jun Shern Chan
    - Leon Maksin
    - Rachel Dias
    - Evan Mays
    - Benjamin Kinsella
    - Wyatt Thompson
    - Johannes Heidecke
    - Amelia Glaese
    - Tejal Patwardhan
  url: https://github.com/openai/frontier-evals/tree/main/project/paperbench
paper:
  title: "PaperBench: Evaluating AI's Ability to Replicate AI Research"
  arxiv: "2504.01848"
  url: https://arxiv.org/abs/2504.01848
  year: 2025
leaderboard_url: https://github.com/openai/frontier-evals/tree/main/project/paperbench
repo_url: https://github.com/openai/frontier-evals/tree/main/project/paperbench
released: "2025-04"
last_updated: "2026-05"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 26.0
  as_of: "2025-04"
  note: >
    Official README leaderboard top is IterativeAgent o1-high at 26.0% (36h),
    dated 2025-04-02. The paper's headline agent is Claude 3.5 Sonnet BasicAgent
    at 21.0%. Both are far from 100%. No later public table for 2026 models was
    confirmed on the pages opened here.
contamination:
  risk: medium
  note: >
    The 20 papers and many author repos are public. Agents are forbidden from
    those repos via per-paper blacklists; confirmed hits score 0. Rubrics are
    withheld from the agent. Future models may still have seen the papers or
    leaked replications in pretraining.
harness:
  lm_eval: ""
  inspect_evals: paperbench
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    inspect_evals registers paperbench (agent rollout) and paperbench_score
    (fresh-sandbox reproduce.sh + judge). Default judge_type is dummy (all zeros);
    simple uses an OpenAI judge (paper uses o3-mini-2025-01-31). Splits: None=23,
    prod=20, dev=3. inspect_evals notes missing Docker-in-Docker and a different
    react() solver than openai/frontier-evals BasicAgent. Default inspect
    agent/reproduce timeout is 6 hours; the paper's reproduce.sh cap was 12 hours.
    The paper cited github.com/openai/preparedness; the live tree is
    openai/frontier-evals/project/paperbench. Hugging Face card still points at
    openai/preparedness.
tags:
  - agents
  - ml-research
  - code-execution
  - rubric
  - long-horizon
sources:
  - url: https://arxiv.org/abs/2504.01848
    title: "PaperBench paper abstract (arXiv:2504.01848)"
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/html/2504.01848
    title: "PaperBench paper HTML (20 papers, 8,316 leaves, scores, human subset)"
    accessed: "2026-09-08"
  - url: https://github.com/openai/frontier-evals/tree/main/project/paperbench
    title: "openai/frontier-evals PaperBench README and leaderboard"
    accessed: "2026-09-08"
  - url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/paperbench
    title: "inspect_evals paperbench README (23 papers, two-task design)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/paperbench/eval.yaml
    title: "inspect_evals paperbench eval.yaml"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/josancamon/paperbench/raw/main/README.md
    title: "Hugging Face josancamon/paperbench card (MIT, 20 papers)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-018 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-018"
---

## What it measures

PaperBench tests whether an agent can rebuild an ICML 2024 Spotlight or Oral paper's empirical contribution without the authors' code. The agent reads the paper and addendum, writes a codebase, and must leave a reproduce.sh that regenerates results in a clean environment. Rubrics break "the paper is reproduced" into thousands of leaf checks spanning code, execution, and result match. The skill is long-horizon ML engineering, not answering a question about the paper.

## How it is scored

Each leaf is pass or fail. Parent scores are weighted averages of children; the root is the replication score. The headline number is the mean over papers. Code-Dev scores only code-development leaves and skips GPU reproduction. Judges are LLM-based (SimpleJudge / o3-mini in the paper). JudgeEval reports o3-mini F1 0.83 against human leaf labels, so judge error is part of the number. inspect_evals defaults to a dummy judge that scores 0 unless `judge_type=simple` is set.

## Dataset and licence

Twenty papers, 8,316 leaves, rubrics signed off with an original author. inspect_evals adds a 3-paper development split (23 papers if you take the default split=None). Hugging Face josancamon/paperbench states MIT. Individual papers keep their own licences. Blacklists and addenda ship with each paper directory.

## Who publishes it

OpenAI Preparedness authors led by Giulio Starace, Oliver Jaffe, Dane Sherburn, James Aung, Jun Shern Chan, Leon Maksin, Rachel Dias, and Tejal Patwardhan posted arXiv:2504.01848 on 2 April 2025. The live code tree is openai/frontier-evals/project/paperbench. The paper and some Hub cards still name openai/preparedness. UK AISI inspect_evals maintains a separate port, marked work in progress.

## Lineage

Related agentic ML-engineering evals in this repository include [mle_bench](mle_bench.md) (Kaggle medals, not paper replication). The paper also cites CORE-Bench, which starts from an existing repo, and RE-Bench. Those are not parents. PaperBench Code-Dev is a scoring variant of this id, not a second benchmark page.

## Saturation and contamination

The best official 2025 agent score on the README table is 26.0%. Humans beat o1 on a 3-paper long-horizon subset. Author code is online, so contamination and blacklist evasion are real failure modes; the paper zeroed 10 of 646 runs for blacklist hits.

## How to run it

Canonical: openai/frontier-evals PaperBench with Docker images and GPU reproduction. inspect_evals: `inspect eval inspect_evals/paperbench` then `inspect eval inspect_evals/paperbench_score` with `judge_type=simple` and an OpenAI judge (paper uses o3-mini-2025-01-31). inspect defaults `judge_type=dummy` (all zeros) and 6-hour agent/reproduce limits. Do not compare dummy-judge inspect runs, Code-Dev, BasicAgent, and IterativeAgent as if they were one protocol. Time limits and Docker-in-Docker support also differ across ports.

## Reading the numbers

A 20% replication score means some code and partial experiments, not a faithful paper reproduction. Code-Dev will read higher because it never checks that results match. Judge model, time limit, and whether reproduce.sh ran in a fresh sandbox all move the number. Read PaperBench beside compute budget and scaffold name, and beside [mle_bench](mle_bench.md) if the question is ML engineering more broadly.
