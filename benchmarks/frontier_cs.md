---
id: frontier_cs
name: Frontier-CS
aliases:
  - FrontierCS
  - "FrontierCS: Evolving Challenges for Evolving Intelligence"
page_kind: benchmark
category: coding
subcategory: "open-ended algorithmic and research CS problems with continuous partial scoring"
status: active
summary: "Open-ended CS problems with continuous partial scoring on algorithmic and research tracks; Inspect pins 238 items while later releases add more."
measures: >
  Frontier-CS asks a model to write an executable program for a computer-science problem
  whose optimum is unknown, then scores that program with a deterministic checker rather
  than pass-or-fail unit tests. The December 2025 paper has 156 problems: 107 algorithmic
  (optimization, constructive, and interactive contest-style tasks, typically C++) and 49
  research tasks in operating systems, HPC, AI, databases, programming languages, and
  security. Inspect Evals pins an expanded Hugging Face snapshot of 238 problems (172
  algorithmic + 66 research). English problem statements. GPU research tasks are off by
  default in Inspect (`include_gpu_problems=False`, 23 of 66 research items).
task_format: >
  Inspect default is an agentic ReAct loop with bash and Python, message_limit 100, in
  Docker. `agentic=False` is single-turn generation, closer to the paper. Track filters:
  frontier_cs (all), frontier_cs_algorithmic, frontier_cs_research. Algorithmic solutions
  compile with g++ -O2 -std=gnu++17 and run through testlib checkers. Research solutions
  run problem-specific Python evaluators.
metric:
  name: "mean per-problem score in [0, 1] (Inspect); paper also reports Score@k / Avg@k / Pass@k"
  direction: higher_is_better
  unit: ""
  max_score: 1.0
  random_baseline: null
  human_baseline: 95.41
  baseline_note: >
    Paper Table 1 human-expert Score@1 on the 107-problem algorithmic track is 95.41.
    Table 1 best model Score@1 is Gemini 3.0 Pro at 29.37 (Score@5 52.06). Table 2
    research-track Score@1 leaders: Claude Opus 4.5 29.40, GPT 5.1 Thinking 28.39,
    Gemini 3.0 Pro 26.95. Pass@k is the share of problems beating a trivial baseline,
    not the human reference. Inspect reports mean and stderr of per-problem scores
    on its pinned 238-item snapshot and, by default, drops GPU research problems.
    Inspect's README quotes paper Score@1 figures of 33.12% algorithmic and 46.55%
    research for Gemini 3.0 Pro; those numbers are not in arXiv:2512.15699v1 Tables 1–2.
dataset:
  size: 238
  size_note: >
    Inspect eval.yaml and the pinned Hugging Face revision
    9375d73b1633f5239e8edb277292f00429815ac7: 238 test problems (172 algorithmic, 66
    research). Paper abstract and Figure 2: 156 problems (107 algorithmic, 49 research)
    as of 17 December 2025. Hugging Face card on 2026-09-08 (current SHA
    73d9801f9735da727060169b57aafbf4d47b6489, lastModified 2026-08-12): 275 problems
    (188 algorithmic, 66 research, 21 "2.0"). Upstream GitHub README badges the same
    day: 188 algorithmic, 68 research, 20 2.0 problems. Inspect GitHub pin
    c7ec558160646dbe797828ccd1a4fded503ab87c. This page's size field follows the Inspect
    task this id names.
  url: "https://huggingface.co/datasets/FrontierCS/Frontier-CS"
  license: "Hugging Face card Apache-2.0; GitHub LICENSE file MIT (dated 2025). Two licence strings are published."
  languages:
    - en
  modalities:
    - text
    - code
  splits: "Hugging Face test split; Inspect downloads checker/evaluator assets from a pinned GitHub archive"
  public_test_set: true
publisher:
  org: "FrontierCS team (ICML 2026); paper lists a large multi-institution author list led by Qiuyang Mang and Wenhao Chai"
  authors:
    - "Qiuyang Mang"
    - "Wenhao Chai"
    - "Zhifei Li"
    - "Huanzhi Mao"
    - "Shang Zhou"
    - "Alexander Du"
    - "and 44 further co-authors on arXiv:2512.15699"
    - "Ion Stoica"
    - "Joseph E. Gonzalez"
    - "Jingbo Shang"
    - "Alvin Cheung"
  url: "https://github.com/FrontierCS/Frontier-CS"
paper:
  title: "FrontierCS: Evolving Challenges for Evolving Intelligence"
  arxiv: "2512.15699"
  url: "https://arxiv.org/abs/2512.15699"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/FrontierCS/Frontier-CS"
released: "2025-12"
last_updated: "2026-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 29.37
  as_of: "2025-12"
  note: >
    Paper algorithmic Score@1: Gemini 3.0 Pro 29.37 versus human experts 95.41. Research
    Score@1 tops out at 29.40 (Claude Opus 4.5). Inspect's own February 2026 43-problem
    slices are lower and are not a full-set ranking. The 2.0 track is newer and not in
    the Inspect pin.
contamination:
  risk: medium
  note: >
    Statements and, since 26 May 2026, formerly private algorithmic tests are public on
    GitHub. Inspect still pins an older archive. Problems are original contest variants
    and research tasks, not copied textbook tests, but the public repo is crawlable.
harness:
  lm_eval: ""
  inspect_evals: "frontier_cs, frontier_cs_algorithmic, frontier_cs_research"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Official CLI: `frontier eval` in FrontierCS/Frontier-CS (Docker or SkyPilot). Harbor
    adapters exist upstream for agent trials. Inspect needs Docker; builds g++, python3,
    and testlib.h. Inspect version 2-A (2026-04-21) switched the default agent from
    basic_agent to react.
tags:
  - coding
  - algorithms
  - research
  - agentic
  - inspect-evals
  - partial-scoring
sources:
  - url: "https://arxiv.org/abs/2512.15699"
    title: "FrontierCS: Evolving Challenges for Evolving Intelligence (arXiv:2512.15699)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2512.15699"
    title: "FrontierCS paper HTML (156 problems, Tables 1–2, human 95.41)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/FrontierCS/Frontier-CS"
    title: "FrontierCS/Frontier-CS dataset card (Apache-2.0; 275 problems on the current card)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/FrontierCS/Frontier-CS"
    title: "Hugging Face dataset API (created 2025-12-19, lastModified 2026-08-12, license apache-2.0)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/FrontierCS/Frontier-CS/main/README.md"
    title: "Upstream README (ICML 2026, current track counts, Harbor, 2.0)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/FrontierCS/Frontier-CS/main/LICENSE"
    title: "Upstream GitHub LICENSE (MIT, Copyright 2025 FrontierCS Team)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/frontier_cs/README.md"
    title: "Inspect Evals Frontier-CS README (238 problems, agentic vs single-turn)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/frontier_cs/eval.yaml"
    title: "Inspect eval.yaml (238 / 172 / 66 sample counts, pinned assets)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/frontier_cs/dataset.py"
    title: "Inspect dataset.py (HF revision 9375d73b, GitHub pin c7ec5581)"
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

Frontier-CS scores a program on an open-ended computer-science task, not a yes/no unit test. Algorithmic items start from contest problems but drop the unique-optimum pass/fail rule so partial quality still earns points. Research items look like lab work: kernels, indexes, symbolic regression, proof-of-concept exploits. The model must emit code. English statements.

This id is the Inspect Evals port (`frontier_cs` and the two track tasks). It is not [live_code_bench](live_code_bench.md). LiveCodeBench is contest pass@k on public problems with known solutions.

## How it is scored

Inspect averages per-problem scores in [0, 1]. Algorithmic cases compile and run through custom testlib checkers. Research cases parse a score from the evaluator's stdout. The paper instead reports Score@k (best of k), Avg@k, and Pass@k against a trivial baseline and a human reference. Human algorithmic Score@1 is 95.41. Gemini 3.0 Pro's paper Score@1 is 29.37 on that track.

Inspect's default agent can iterate with tools. The paper is single-turn. Set `-T agentic=False` before citing Inspect next to Table 1. Inspect also drops GPU research problems unless you turn them on, so a "research" mean is not the paper's 49- or 66-item track.

## Dataset and licence

Count depends on the snapshot. Paper: 156. Inspect pin: 238. Current Hugging Face card: 275 including a 2.0 track. Hugging Face says Apache-2.0; the GitHub LICENSE file is MIT. Record both. Tests for the algorithmic track were made public on 26 May 2026.

## Who publishes it

The FrontierCS team. First authors Qiuyang Mang and Wenhao Chai. arXiv 17 December 2025. Accepted to ICML 2026 (upstream README, 30 April 2026). Hugging Face dataset created 19 December 2025, last updated 12 August 2026. Inspect port by JayBaileyCS, version 2-A.

## Lineage

No predecessor page in this repository. The authors contrast saturated coding quizzes with unsolved, verifiable tasks. Upstream 2.0 (Harbor-first, repo-level) is a successor track that Inspect does not run. Harbor adapters are a packaging change, not a new benchmark id here.

## Saturation and contamination

Paper scores sit far below the human algorithmic reference, so the original tracks are open. Public statements plus public tests raise contamination risk for models trained after May 2026. Inspect's pin is older than the current Hub SHA, so a live `load_dataset("FrontierCS/Frontier-CS")` is not the Inspect eval.

## How to run it

Official: clone FrontierCS/Frontier-CS and `frontier eval algorithmic|research <id> <file>`. Inspect: `uv run inspect eval inspect_evals/frontier_cs` (or `_algorithmic` / `_research`) with Docker. Match `agentic`, `include_gpu_problems`, `message_limit`, and the pinned revision before comparing runs. Inspect 2-A (2026-04-21) changed the default agent to `react`.

## Reading the numbers

A 0.3 mean on Inspect is partial credit on hard tasks, not 30% pass@1 on HumanEval. Always name the snapshot (156 / 238 / 275), the track, GPU inclusion, and agentic versus single-turn. Do not use the Inspect README's 33.12% / 46.55% Gemini 3.0 Pro line as the paper result; Tables 1–2 of v1 disagree. Pair with [live_code_bench](live_code_bench.md) if you need closed-form contest coding.
