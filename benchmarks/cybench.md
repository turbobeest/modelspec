---
id: cybench
name: "Cybench"
aliases:
  - "Cybench: A Framework for Evaluating Cybersecurity Capabilities and Risks of Language Models"
page_kind: benchmark
category: agentic
subcategory: "autonomous capture-the-flag (CTF) cybersecurity task-solving, with a graded subtask mode"
status: active
summary: "Tests whether an autonomous LLM agent can solve 40 professional-level capture-the-flag cybersecurity tasks in a live sandbox, with 17 of them broken into guided subtasks for partial credit."
measures: >
  Cybench measures whether an autonomous LLM agent, given shell and Python tool access inside a Kali
  Linux sandbox, can solve real capture-the-flag (CTF) security challenges drawn from four
  professional-level competitions (HackTheBox Cyber Apocalypse 2024, SekaiCTF, Glacier and HKCert).
  Tasks span six domains -- cryptography, web security, reverse engineering, forensics, exploitation
  (pwn) and miscellaneous -- and the paper anchors difficulty in human terms: the times competitive
  human teams took to first-solve each task ranged from a few minutes up to nearly 25 hours. This
  page categorizes Cybench as agentic rather than domain knowledge, because success depends on
  multi-step planning and tool use against a live target, not a static answer.
task_format: >
  An agent is placed in a Kali Linux Docker sandbox with bash and code-execution tools and must find
  and submit a flag string for each of 40 tasks. 17 of the 40 tasks additionally ship a sequence of
  subtasks -- guided intermediate questions with their own answers -- scored sequentially for
  gradated credit. Three scoring modes result: unguided performance (binary success on the full
  task with no hints), subtask-guided performance (binary success on only the final subtask, i.e.
  full guidance up to the last step), and subtask performance (the fraction of a task's subtasks
  solved).
metric:
  name: "task success rate (fraction of the 40 CTF tasks solved), reported separately per scoring mode"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper's own unguided-mode results (its Table 3, seven models compared) put Claude 3.5 Sonnet
    on top at 17.5% (7 of 40 tasks), with GPT-4o at 12.5%, Claude 3 Opus at 10.0%, and Llama 3.1 405B
    Instruct, Mixtral 8x22B Instruct and Gemini 1.5 Pro each at 7.5%; the weakest model read, Llama 3
    70B Chat, scored 5.0%. No random-guess or human baseline percentage applies to this task, since a
    CTF flag cannot be guessed at a fixed rate; the paper instead reports how long human teams took to
    first-solve each task as its difficulty anchor.
dataset:
  size: 40
  size_note: >
    40 CTF tasks: 17 from HackTheBox's Cyber Apocalypse 2024, 12 from SekaiCTF (2022-23), 9 from
    Glacier and 2 from HKCert. By category: cryptography 16, web security 8, reverse engineering 6,
    forensics 4, miscellaneous 4, exploitation/pwn 2. All tasks are from 2022-2024 competitions,
    chosen specifically to limit train-test overlap; the paper notes nearly half were released after
    December 2023, the training cutoff of every evaluated model except Claude 3.5 Sonnet.
  url: "https://github.com/andyzorigin/cybench"
  license: "Apache-2.0 (repository code); the redistributed CTF challenge content itself is not
    uniformly licensed -- see Dataset and licence"
  languages:
    - en
  modalities:
    - text
    - code
  splits: "no train/test split; all 40 tasks form a single fixed evaluation set, 17 of them further split into ordered subtasks"
  public_test_set: true
publisher:
  org: "Stanford University (Center for AI Safety collaborators Dan Boneh, Daniel E. Ho and Percy Liang among the senior authors), with a 27-author team"
  authors:
    - "Andy K. Zhang"
    - "Neil Perry"
    - "Riya Dulepet"
    - "and 24 further co-authors (see paper for full list)"
    - "Dan Boneh"
    - "Daniel E. Ho"
    - "Percy Liang"
  url: "https://cybench.github.io"
paper:
  title: "Cybench: A Framework for Evaluating Cybersecurity Capabilities and Risks of Language Models"
  arxiv: "2408.08926"
  url: "https://arxiv.org/abs/2408.08926"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/andyzorigin/cybench"
released: "2024-08"
last_updated: "2025-04"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 17.5
  as_of: "2024-08"
  note: >
    Read from the paper's unguided-mode table (Claude 3.5 Sonnet, 7 of 40 tasks); the paper was
    revised through at least four arXiv versions (August 2024 to April 2025) and this page could not
    confirm whether later revisions re-ran or added to that table, so treat 17.5% as the number this
    page's sources support rather than a guaranteed-current figure. Either way, more than four-fifths
    of tasks went unsolved by every model tested, so the benchmark is far from saturated. CVE-Bench
    (see Lineage) separately reused Cybench's agent as a weak baseline and found it solved only 2.5%
    of its own, differently-scoped tasks, consistent with a still-hard benchmark rather than one near
    its ceiling.
contamination:
  risk: medium
  note: >
    The authors deliberately picked tasks from 2022-2024 competitions to limit train-test overlap,
    and note nearly half postdate the training cutoff of every evaluated model but one, which is a
    real mitigation. But all 40 tasks are drawn from public competitions whose writeups and solutions
    can circulate online after the fact, and the full task set itself has been public on GitHub since
    August 2024, so an agent that has memorized a public writeup for one of these specific tasks could
    succeed without the discovery and exploitation reasoning the benchmark means to test.
harness:
  lm_eval: ""
  inspect_evals: "cybench"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >-
    The reference implementation is the authors' own run_task.sh / run_benchmark.py pipeline in the
    andyzorigin/cybench repository, which can call models directly or through HELM's API layer.
    inspect_evals ships a separate port under the same name that currently covers only 39 of the 40
    tasks: its changelog records removing the "motp" challenge outright over a GPL licensing concern
    (see Dataset and licence). It downloads challenge files from pinned, checksum-verified upstream
    commits, defaults to a Kubernetes sandbox for domain filtering (Docker is available but requires
    setting CYBENCH_ACKNOWLEDGE_RISKS=1, since it grants an unrestricted-internet Kali environment),
    and scores "a simple proportion... over the challenges" -- an unguided-style pass rate.
tags:
  - agentic
  - security
  - cybersecurity
  - ctf
  - sandbox
  - exploitation
sources:
  - url: "https://arxiv.org/abs/2408.08926"
    title: "Cybench: A Framework for Evaluating Cybersecurity Capabilities and Risks of Language Models"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2408.08926"
    title: "Cybench (full text, ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/andyzorigin/cybench"
    title: "andyzorigin/cybench GitHub repository (README, LICENSE)"
    accessed: "2026-09-08"
  - url: "https://cybench.github.io"
    title: "Cybench project page"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/cybench"
    title: "inspect_evals cybench task (README, changelog)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Cybench measures whether an autonomous LLM agent, given shell and Python tool access inside a Kali Linux sandbox, can solve real capture-the-flag (CTF) security challenges drawn from four professional-level competitions: HackTheBox's Cyber Apocalypse 2024, SekaiCTF, Glacier and HKCert. The 40 tasks span six domains -- cryptography, web security, reverse engineering, forensics, exploitation and miscellaneous -- and the paper anchors difficulty in human terms, reporting that competitive human teams first-solved individual tasks in times ranging from a few minutes up to nearly 25 hours. Because success depends on multi-step planning and tool use against a live target rather than a static answer, this page categorizes Cybench as agentic rather than domain knowledge.

Cybench also grades in two resolutions. 17 of the 40 tasks ship a sequence of guided subtasks -- smaller, ordered questions with their own answers -- so a run can score partial, incremental progress even when the full flag is never captured.

## How it is scored

Three metrics come out of a Cybench run: unguided performance (binary success or failure on the full task with no hints), subtask-guided performance (binary success on only the final subtask, i.e. with guidance through every step but the last), and subtask performance (the fraction of a task's subtasks solved, for the 17 tasks that have them). The paper's headline unguided-mode comparison across seven models put Claude 3.5 Sonnet on top at 17.5% (7 of 40 tasks), with GPT-4o at 12.5%, Claude 3 Opus at 10.0%, three models clustered at 7.5%, and the weakest model at 5.0%. No fixed random or human baseline percentage applies, since flags cannot be guessed at a defined rate; the human first-solve times serve as the paper's difficulty calibration instead.

## Dataset and licence

The 40 tasks split 17/12/9/2 across HackTheBox Cyber Apocalypse 2024, SekaiCTF, Glacier and HKCert, and by category: cryptography 16, web 8, reverse engineering 6, forensics 4, miscellaneous 4, exploitation 2. All tasks come from 2022-2024 competitions, chosen specifically to limit train-test overlap; nearly half postdate the training cutoff of every evaluated model except Claude 3.5 Sonnet. The andyzorigin/cybench repository carries an Apache 2.0 licence, but that covers the harness code -- the redistributed CTF challenge content itself is not uniformly licensed. This is not hypothetical: the inspect_evals port of Cybench removed one entire challenge ("motp") specifically over a GPL licensing conflict, which is why that port covers only 39 of the original 40 tasks.

## Who publishes it

Cybench comes from a 27-author team led by Andy K. Zhang and Neil Perry, with Stanford faculty Dan Boneh, Daniel E. Ho and Percy Liang among the senior authors, first posted to arXiv in August 2024 and revised through at least four versions into April 2025. The andyzorigin GitHub organisation hosts the reference implementation; there is no separately hosted public leaderboard found for this page.

## Lineage

Cybench has no direct predecessor or successor of its own tracked in this repository. [CVE-Bench](cve_bench.md) was explicitly built to match Cybench's scale of 40 tasks and reuses a Cybench-derived agent (Cy-Agent) as one of its own baselines, but targets real, unabstracted web-application CVEs rather than CTF-style puzzles -- a related but distinct benchmark, not a successor. The same authors' project page also points to BountyBench, a newer, real-world benchmark scoring vulnerability detection, exploitation and patching by bug-bounty dollar value; it is a different named project rather than "Cybench 2" and does not have its own page here.

## Saturation and contamination

Cybench is far from saturated: the best model read for this page solved well under a fifth of the 40 tasks unguided, and every model left the large majority unsolved. Contamination risk is graded medium: the authors deliberately chose recent (2022-2024) competitions specifically to limit train-test overlap, a real mitigation, but the tasks have been fully public since August 2024 and CTF writeups for public competitions commonly circulate online, so memorizing a specific published solution remains possible without the discovery work the benchmark is meant to test.

## How to run it

The reference implementation is the authors' run_task.sh / run_benchmark.py pipeline, which can call models directly or through HELM's API layer and runs each task in a privileged Docker container. inspect_evals packages a separate 39-task port under the same `cybench` name, downloading challenge files from pinned, checksum-verified commits (some resemble malware and are excluded from the repository itself), and defaults to a Kubernetes sandbox for domain filtering since the alternative Docker sandbox grants unrestricted internet access and requires explicitly acknowledging that risk.

## Reading the numbers

A Cybench score describes a whole agent system -- model, tool scaffold and prompting -- attacking realistic but competition-scale puzzles, not a pure measure of a base model's security knowledge. Because 17 of 40 tasks carry subtasks, a subtask-performance figure can look substantially healthier than an unguided pass rate for the same model; always check which of the three metrics a reported number uses before comparing it to another. The benchmark's own difficulty anchor is human solve time, not a percentile, so a task a human team solved in minutes and one that took nearly a day are treated identically as one pass/fail data point unless a subtask breakdown is available.
