---
id: core_bench
name: "CORE-Bench"
aliases:
  - "Computational Reproducibility Benchmark"
page_kind: benchmark
category: agentic
subcategory: "computational reproducibility: scientific code execution and result verification"
status: active
summary: "Tests whether an agent can reproduce a published paper's results by installing dependencies, running its code, and extracting the right numbers, across three levels of given scaffolding."
measures: >
  CORE-Bench gives an agent a real, previously published research repository ("capsule," in the
  source platform's terminology) and a set of questions about the numeric or visual results that
  running that code correctly should produce -- for example, a model's test accuracy after a given
  epoch, or the value of a specific axis label on a generated figure. The agent must read
  instructions, install the right dependencies, run the code (or, at the easiest level, skip
  straight to reading output that is already provided), and report answers for every question tied
  to that paper. Papers span computer science, social science and medicine, written in Python or R,
  and some questions require reading a generated chart or table image rather than only text. It
  measures a genuinely agentic skill -- multi-step tool use, debugging, and retrieval inside a real
  software environment -- rather than single-turn code generation or question answering.
task_format: >
  Given a paper's code repository and a fixed set of questions about its outputs, the agent works
  inside an isolated container (with bash and, for image-based questions, a vision-language-model
  tool) and writes its final answers to a report.json file. A task counts as solved only if every
  question tied to that paper is answered correctly; there is no partial credit for a task.
metric:
  name: "task accuracy (all task questions correct)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Task accuracy is the share of tasks where every associated question was answered correctly;
    numeric answers are checked against a tolerance and non-numeric answers by normalized match. The
    authors designed each task to include at least one question that cannot be solved by guessing, so
    no single random-guess percentage applies across the benchmark, and no human-reproducibility
    baseline percentage was found in the sources reviewed for this page. The paper also reports
    average API cost per agent run alongside accuracy, since the original baselines were capped at
    $4 per task.
dataset:
  size: 270
  size_note: >
    270 tasks drawn from 90 papers (three difficulty levels per paper: easy, medium, hard), each
    with at least one question -- 181 distinct task questions in total, since the same questions
    repeat across a paper's three difficulty levels. The 90 papers were filtered from 5,090
    candidate CodeOcean.com capsules against ten selection criteria (local reproducibility chief
    among them), confirmed directly from the paper's own description of this process. The dataset
    splits the 90 papers 45/45 into training and test papers (135 tasks each); the `core_bench` task
    most harnesses run evaluates only the 45-paper test half. The test split ships PGP-encrypted;
    the decryption password is published in the reference repository's own README, so this is better
    read as a light deterrent against casual scraping than a true secrecy mechanism.
  url: "https://huggingface.co/datasets/siegelz/core-bench"
  license: "MIT"
  languages:
    - en
  modalities:
    - text
    - code
    - image
  splits: >
    45 papers / 135 tasks for training, 45 papers / 135 tasks for test (encrypted); most reported
    scores use only the test half.
  public_test_set: true
publisher:
  org: "Princeton University"
  authors:
    - "Zachary S. Siegel"
    - "Sayash Kapoor"
    - "Nitya Nadgir"
    - "Benedikt Stroebl"
    - "Arvind Narayanan"
  url: "https://github.com/siegelz/core-bench"
paper:
  title: "CORE-Bench: Fostering the Credibility of Published Research Through a Computational Reproducibility Agent Benchmark"
  arxiv: "2409.11363"
  url: "https://arxiv.org/abs/2409.11363"
  year: 2024
leaderboard_url: "https://agent-evals-leaderboard.hf.space"
repo_url: "https://github.com/siegelz/core-bench"
released: "2024-09"
last_updated: "2024-10"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 21.0
  as_of: "2024-09"
  note: >
    The paper's own headline result -- the best baseline agent (CORE-Agent with GPT-4o) reached 21%
    task accuracy on CORE-Bench-Hard -- is over two years old at the time of this research and
    predates most current frontier agent scaffolds. The successor leaderboard the reference
    repository now points to, the Holistic Agent Leaderboard (agent-evals-leaderboard.hf.space),
    returned an error page rather than rendering results when checked on 2026-09-08 ("Your space is
    in error"), so no current top score could be confirmed. Given how far even a capable 2024 agent
    sat below full accuracy, and no confirmed evidence the gap has since closed, this is graded
    "open" rather than "watch" or "saturated."
contamination:
  risk: low
  note: >
    The paper states directly that "CORE-Bench's foundation in public repositories enables periodic
    updates of the benchmark tasks, which could mitigate concerns about contamination and
    saturation," and the test split's task questions and reference answers are distributed
    PGP-encrypted rather than in plain text, unlike the underlying CodeOcean code itself (which was
    already public before selection). That encryption is a soft deterrent, since its password is
    published in the reference repository, but it does prevent the specific question/answer pairs
    from appearing in a plain web crawl.
harness:
  lm_eval: ""
  inspect_evals: "core_bench (single task, `difficulty` parameter: easy | medium | hard, default easy; confirmed directly in the inspect_evals source)"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >-
    The reference implementation (siegelz/core-bench on GitHub) states in its own README that it "is
    no longer actively maintained" and directs users to the Holistic Agent Leaderboard harness
    (princeton-pli/hal-harness) instead, from the same research group. The original baselines
    (AutoGPT and a task-specific CORE-Agent, both run with GPT-4o and GPT-4o-mini) were capped at $4
    of API spend per task. Medium and hard tasks that need a GPU require Docker-in-Docker sandboxing;
    inspect_evals' implementation notes it can only run every task without a GPU at the easy
    difficulty level, since that level requires no code execution.
tags:
  - agentic
  - code-execution
  - reproducibility
  - tool-use
  - scientific-research
  - multi-step
sources:
  - url: "https://arxiv.org/abs/2409.11363"
    title: "CORE-Bench: Fostering the Credibility of Published Research Through a Computational Reproducibility Agent Benchmark"
    accessed: "2026-09-08"
  - url: "https://github.com/siegelz/core-bench"
    title: "siegelz/core-bench repository (README, LICENSE)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/siegelz/core-bench"
    title: "siegelz/core-bench dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/siegelz/core-bench"
    title: "siegelz/core-bench, Hugging Face Hub API (licence tag, last-modified date)"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/core_bench"
    title: "inspect_evals: core_bench task implementation and README"
    accessed: "2026-09-08"
  - url: "https://agent-evals-leaderboard.hf.space"
    title: "Holistic Agent Leaderboard (current recommended CORE-Bench leaderboard; returned an error page on access)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice B"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

CORE-Bench gives an agent a real, previously published research code repository ("capsule," in the
source platform's own terminology) and a set of questions about the numeric or visual results that
running that code correctly should produce -- for example, a model's test accuracy after a given
epoch, or the value on a specific axis of a generated figure. The agent must read instructions,
install the right dependencies, run the code, and report an answer for every question tied to that
paper (at the easiest difficulty level, it is instead given the output already and only needs to
extract from it). Papers span computer science, social science and medicine, written in Python or R,
and some questions require reading a generated chart or table image rather than only text. Unlike
single-turn code-generation or question-answering benchmarks, this measures a genuinely agentic
skill: multi-step tool use, debugging and retrieval inside a real, occasionally uncooperative
software environment.

## How it is scored

An agent writes its final answers to a report.json file; a task counts as solved only if every
question associated with that paper is answered correctly, with no partial credit. Numeric answers
are checked against a tolerance, other answers by a normalized match. The three difficulty levels
give progressively less help: CORE-Bench-Easy hands the agent the output of an already-successful
run and asks only for information extraction; CORE-Bench-Medium provides a Dockerfile and README
instructions, so the agent need only run the given command and then extract results; CORE-Bench-Hard
provides only a README and no Dockerfile, requiring the agent to work out and install the correct
dependencies itself before running anything. The authors designed each task to include at least one
question that cannot be answered by guessing, so there is no meaningful random baseline, and no
human-reproducibility baseline percentage was found in the sources reviewed for this page.

## Dataset and licence

The benchmark comprises 270 tasks from 90 papers (three difficulty levels per paper), with 181
distinct task questions in total, since the same questions repeat across a paper's three difficulty
levels. The 90 papers were filtered from 5,090 candidate capsules on CodeOcean.com against ten
selection criteria, chief among them that the authors could verify the capsule was locally
reproducible. The 90 papers split 45/45 into training and test sets (135 tasks each); the standard
`core_bench` evaluation runs only against the 45-paper test half. That test half is distributed
PGP-encrypted, with the decryption password published in the reference repository's own README -- a
light deterrent against casual scraping rather than genuine secrecy. The dataset and code are
released under the MIT licence.

## Who publishes it

CORE-Bench was introduced by Zachary S. Siegel, Sayash Kapoor, Nitya Nadgir, Benedikt Stroebl and
Arvind Narayanan of Princeton University, posted to arXiv in September 2024. The same group
maintains the dataset on Hugging Face and, more recently, the Holistic Agent Leaderboard (HAL), a
broader multi-benchmark agent leaderboard that has become the recommended way to run and report
CORE-Bench results; the original standalone harness's own README now states it "is no longer
actively maintained."

## Lineage

CORE-Bench has no named predecessor or formal successor benchmark. Its most direct continuation is
organizational rather than a new benchmark id: the same Princeton group folded CORE-Bench into the
Holistic Agent Leaderboard, a shared harness and leaderboard covering multiple agentic benchmarks,
superseding the original standalone evaluation harness (though not the underlying task or dataset,
which are unchanged). This repository does not have separate pages for the three difficulty levels,
which are run as parameters of one task rather than as separately identified benchmarks.

## Saturation and contamination

The paper's own headline result is that the best baseline agent (a task-specific CORE-Agent running
GPT-4o) reached only 21% task accuracy on CORE-Bench-Hard, "showing the vast scope for improvement."
That figure is now over two years old and predates most current frontier agent scaffolds; the
Holistic Agent Leaderboard, the successor leaderboard the reference repository now points to,
returned an error page rather than rendering results when checked for this page (2026-09-08), so no
current top score could be confirmed. Given how far even a capable contemporary agent sat below full
accuracy, this benchmark is graded "open." Contamination risk is graded low: the paper explicitly
argues that drawing from public repositories lets the benchmark be refreshed over time to manage
contamination, and the test split's specific question/answer pairs are distributed encrypted rather
than in plain text, even though the underlying research code itself was already public before
selection.

## How to run it

inspect_evals implements this as a single `core_bench` task with a `difficulty` parameter (easy,
medium or hard) plus filters for field, language and GPU requirement; running it downloads and
PGP-decrypts the test split and requires Docker-in-Docker sandboxing for medium/hard tasks that
execute code, which in turn can require a GPU. The original reference harness (siegelz/core-bench)
capped agents at $4 of API spend per task and evaluated a general-purpose AutoGPT agent alongside a
task-specific CORE-Agent, both with GPT-4o and GPT-4o-mini; that harness is no longer actively
maintained in favor of the Holistic Agent Leaderboard harness from the same authors. No lm-eval-harness, HELM, OpenCompass or BIG-bench implementation was found.

## Reading the numbers

A high CORE-Bench score shows an agent can navigate an unfamiliar, real code repository well enough
to install its dependencies, execute it correctly, and pull out the right numbers or figure
readings -- a close proxy for whether it could actually help verify or replicate a piece of
published research, rather than merely writing plausible-looking code. Because a task requires every
associated question to be answered correctly, scores are stricter than a per-question accuracy would
suggest, and comparing scores across difficulty levels shows how much of an agent's success depends
on being handed a working environment versus building one itself. Given the benchmark's low
reported ceiling as of its original publication and the unconfirmed state of current leaderboard
data, treat any single CORE-Bench number as provisional until checked against the harness, model and
difficulty level that produced it.
