---
id: osworld
name: OSWorld
aliases:
- OS-World
page_kind: benchmark
category: agentic
subcategory: computer-use / GUI agents
status: active
summary: Tests whether a multimodal agent can complete open-ended tasks in a real, live desktop operating
  system.
measures: 'OSWorld gives an agent a natural-language instruction and a live view of a virtual machine,
  usually a screenshot and sometimes an accessibility tree, and asks it to operate real desktop and web
  applications to complete the task: finding files, editing documents, configuring settings, and other
  workflows that span multiple applications and OS file I/O rather than a single scripted action.'
task_format: screenshot (optionally plus accessibility tree) as observation; agent issues GUI actions
  (click, type, drag, hotkey) in a loop until it signals completion or hits a step limit
metric:
  name: success rate
  direction: higher_is_better
  unit: '%'
  max_score: 100.0
  random_baseline: null
  human_baseline: 72.36
  baseline_note: Human baseline of 72.36% measured by the paper's authors performing the same 369 tasks;
    the strongest agent evaluated in the original paper reached 12.24%.
dataset:
  size: 369
  size_note: 369 tasks across real desktop and web applications; 8 require a Google Drive account and
    are sometimes excluded, leaving 361.
  url: https://github.com/xlang-ai/OSWorld
  license: Apache-2.0 (repository licence, from the GitHub LICENSE file; the project website separately
    displays a CC BY-SA 4.0 notice for its own page content)
  languages:
  - en
  modalities:
  - text
  - image
  splits: single evaluation set; no train/test split described in the sources reviewed
  public_test_set: true
publisher:
  org: University of Hong Kong, Salesforce Research, Carnegie Mellon University, University of Waterloo
  authors:
  - Tianbao Xie
  - Danyang Zhang
  - Jixuan Chen
  - Xiaochuan Li
  - Siheng Zhao
  - Ruisheng Cao
  - Toh Jing Hua
  - Zhoujun Cheng
  - Dongchan Shin
  - Fangyu Lei
  - Yitao Liu
  - Yiheng Xu
  - Shuyan Zhou
  - Silvio Savarese
  - Caiming Xiong
  - Victor Zhong
  - Tao Yu
  url: https://os-world.github.io/
paper:
  title: 'OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments'
  arxiv: '2404.07972'
  url: https://arxiv.org/abs/2404.07972
  year: 2024
leaderboard_url: https://os-world.github.io/
repo_url: https://github.com/xlang-ai/OSWorld
released: 2024-04
last_updated: ''
lineage:
  family: ''
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: open
  top_score: 12.24
  as_of: 2024-04
  note: Best agent result from the original paper; a more recent dated leaderboard reading was not established
    from the sources reviewed. The human baseline (72.36%) sits far above this, so the gap may have closed
    since publication.
contamination:
  risk: medium
  note: Task configs, initial-state setup and checker scripts are public in the GitHub repository since
    April 2024, so a model could have seen them in pretraining. Execution-based grading against a live
    environment limits how useful verbatim memorization is compared with a text-answer benchmark, but
    the authors do not describe a specific mitigation.
harness:
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: ''
tags:
- gui-agents
- computer-use
- multimodal-agents
- desktop-automation
sources:
- url: https://arxiv.org/abs/2404.07972
  title: 'OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments (arXiv)'
  accessed: '2026-09-07'
- url: https://github.com/xlang-ai/OSWorld
  title: xlang-ai/OSWorld GitHub repository
  accessed: '2026-09-07'
- url: http://osworld-v1.xlang.ai/
  title: OSWorld project site (canonical URL os-world.github.io redirects here)
  accessed: '2026-09-07'
freshness:
  researched: '2026-09-07'
  researched_by: sonnet-5 agent, batch 1, slice H
  reviewed: ''
  reviewed_by: ''
---

## What it measures

OSWorld measures whether a multimodal agent can operate a real desktop the way a person would.
Given a natural-language instruction and a live view of a virtual machine, usually a screenshot and
sometimes an accessibility tree, the agent must decide which application to open, what to click, type
or drag, and when the task is finished. Tasks run against real software: office suites, browsers, file
managers and other GUI utilities, and many span OS file I/O and multiple applications rather than a
single isolated action. The modality is image plus text; the primary environment is Ubuntu, with
Windows and macOS support added since the original release.

## How it is scored

Each of the 369 tasks ships with an initial-state setup config and a task-specific, execution-based
checker script that inspects the resulting file system, application state or output after the agent
finishes. Success is binary per task, and the headline metric is success rate: successful tasks divided
by tasks attempted, reported as a percentage. The original paper measured a human baseline of 72.36% by
having people perform the same 369 tasks, and reported that the strongest agent tested at publication
reached only 12.24%, struggling mainly with GUI grounding (clicking the right element) and operational
knowledge (knowing an application's workflow). Eight of the 369 tasks require a Google Drive account and
are sometimes excluded, leaving a commonly reported 361-task variant.

## Dataset and licence

369 tasks (361 excluding the Google-Drive-dependent ones), each built from a real-world computer-use
case with a config describing initial state, instruction and a task-specific evaluation script. Tasks
are grouped into categories such as Office, Daily and Professional workflows. The GitHub repository is
Apache-2.0 licensed per its LICENSE file; the project's companion website separately carries a Creative
Commons Attribution-ShareAlike 4.0 notice for its own page content. There is no single held-out set of
textual answers, since grading runs an executable checker against the final machine state, and the task
configs and checkers are themselves public in the repository.

## Who publishes it

OSWorld comes from a multi-institution academic collaboration: authors from the University of Hong Kong,
Salesforce Research, Carnegie Mellon University and the University of Waterloo, led by Tianbao Xie with
16 co-authors including Shuyan Zhou, Silvio Savarese, Caiming Xiong, Victor Zhong and Tao Yu. The paper,
"OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments," appeared
on arXiv in April 2024 and was accepted at NeurIPS 2024. The xlang-ai group continues to maintain the
GitHub repository and project site, which hosts a verified leaderboard that researchers submit
implementations to for official scoring.

## Lineage

OSWorld names no direct predecessor; the paper frames it as the first real, scalable, cross-OS computer
environment for agent evaluation, rather than a scripted or web-only sandbox. It has since spawned
follow-on projects from the same group and wider community, including OSWorld-Verified (task-config
fixes and AWS support for parallel evaluation) and OSWorld-MCP (testing whether computer-use agents can
invoke Model Context Protocol tools). Neither has its own id or page in this repository yet.

## Saturation and contamination

At publication (April 2024) the gap between the human baseline (72.36%) and the best evaluated agent
(12.24%) was large, and the paper treats the benchmark as far from solved at that point — open, as of
April 2024. A more recent, dated leaderboard reading beyond the original paper's numbers was not
established from the sources reviewed here, so treat "open" as reflecting the 2024 publication, not
necessarily today's state of the field. Because task configs, checker scripts and reference solutions
live in the open GitHub repository since 2024, a model's pretraining data could plausibly include them;
the authors do not describe a specific contamination mitigation, though execution-based grading against
a live environment makes rote memorization of a "correct answer" less directly useful than for a
question-answering benchmark, since the agent still has to act correctly.

## How to run it

The reference implementation is at github.com/xlang-ai/OSWorld, which provisions virtual machines
(VMware, VirtualBox, Docker, Modal, Daytona or AWS for Ubuntu; Docker for Windows) and drives them
through an agent loop that issues actions until the agent signals completion or hits a step limit.
Comparability depends on the observation space (screenshot only versus screenshot plus accessibility
tree), the step budget, and which task subset (369 versus 361) was used. None of these were confirmed as
standardized entries in lm-evaluation-harness, inspect_evals, HELM, OpenCompass or BIG-bench's task lists.

## Reading the numbers

A high OSWorld score means an agent can chain together multi-step, multi-application desktop work, the
kind a human assistant would do, without being told the exact clicks. It does not say how the agent
performs on tasks outside the 369-task distribution, on operating systems or applications not covered,
or under UI changes the checker scripts do not anticipate. Because grading is execution-based, a passing
task genuinely happened in a live environment, a stronger signal than a model merely claiming success in
text. Before comparing two reported scores, check whether they used the full 369-task set or the
361-task variant, and what observation space the agent had.
