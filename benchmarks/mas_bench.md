---
id: mas_bench
name: MAS-Bench
aliases:
  - MAS-Bench
  - MAS-Bench-Eval
page_kind: benchmark
category: agentic
subcategory: shortcut-augmented hybrid mobile GUI agents
status: active
summary: >
  MAS-Bench scores Android GUI agents on 139 live-app tasks when they may call
  APIs, deep links, and RPA scripts instead of tapping through every screen.
measures: >
  The agent receives an English instruction on a real Android app, or several
  apps, and must finish the task. It may tap the GUI, or it may invoke a
  shortcut: an API, a deep link, or a short RPA script. All 139 tasks are
  solvable with GUI only; shortcuts are an efficiency option, not a hidden
  gold path. A second track asks the agent to generate its own shortcut
  library from exploration, then a fixed T3A baseline runs the tasks with
  that library. The suite covers shopping, news, mail, maps, health, and
  similar daily apps, with screenshots plus structured UI state.
task_format: >
  Multi-step Android control on an emulator snapshot (MAS-Bench-AVD). 92
  single-app tasks and 47 cross-app tasks. Shortcuts are retrieved by app
  name and injected as function signatures. Success uses a two-stage
  describe-and-judge pipeline (MAS-Bench-Eval).
metric:
  name: success rate (SR), with separate efficiency and cost metrics
  direction: higher_is_better
  unit: '%'
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Nine metrics in three groups. Success: SR. Efficiency: Mean Steps (MS),
    Mean Step Ratio (MSR), Mean Step Ratio on Successful tasks (MSRS), Mean
    Execution Time (MET). Cost and strategy: Mean Token Cost (MToC), Mean
    Shortcut Call Count (MSC), Shortcut Success Rate (SSR), Shortcut-to-GUI
    Ratio (S2GR). MSR and MSRS compare agent steps to a human GUI-only path
    collected from three experienced users; MSRS below 1.0 means fewer steps
    than that human GUI path. Table 2 is a weighted average over 92
    single-app and 47 cross-app tasks. MAS-GLM-4.5V reached 68.3% SR with
    the predefined shortcut bank.
dataset:
  size: 139
  size_note: >
    139 tasks across 11 Android apps: 92 single-app and 47 cross-app. Human
    GUI traces average 9.27 steps (single-app) and 17.66 steps (cross-app).
    Shortcut bank: 11 APIs, 70 deep links, 7 custom RPA scripts (88 total),
    from 2 shortcuts (Google Calendar) to 21 (Fitbit). Apps named in Table 6
    are Amazon, Booking.com, Yelp, BBC News, Chrome, YouTube, Contacts,
    Fitbit, Gmail, Calendar, and Maps. A 69-task subset (50% sample, 46
    single-app plus 23 cross-app) is used for shortcut-generation tests.
  url: https://github.com/Pengxiang-zhao/MAS-Bench
  license: ''
  languages:
    - en
  modalities:
    - text
    - image
  splits: >
    No train/test split. All 139 tasks are the evaluation set. Shortcut
    generation uses a random 69-task subset. Environment recovery uses one
    system snapshot (MAS-Bench-AVD) rather than per-task snapshots.
  public_test_set: true
publisher:
  org: Zhejiang University and vivo AI Lab, with Peking University
  authors:
    - Pengxiang Zhao
    - Guangyi Liu
    - YaoZhen Liang
    - Weiqing He
    - Zhengxi Lu
    - WenHao Wang
    - Yuehao Huang
    - Yuxiang Chai
    - Zhaolu Kang
    - Yaxuan Guo
    - Hao Wang
    - Kexin Zhang
    - Liang Liu
    - Yong Liu
  url: https://pengxiang-zhao.github.io/MAS-Bench
paper:
  title: 'MAS-Bench: A Unified Benchmark for Shortcut-Augmented Hybrid Mobile GUI Agents'
  arxiv: '2509.06477'
  url: https://arxiv.org/abs/2509.06477
  year: 2025
leaderboard_url: https://pengxiang-zhao.github.io/MAS-Bench
repo_url: https://github.com/Pengxiang-zhao/MAS-Bench
released: '2025-09'
last_updated: '2026-05'
lineage:
  family: ''
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: open
  top_score: 68.3
  as_of: '2026-04'
  note: >
    Best reported SR in Table 2 is 68.3% for MAS-GLM-4.5V with the predefined
    shortcut bank (paper v2, April 2026). GUI-only counterparts sit lower
    (GLM-4.5V 52.6% SR in the same table). No public live leaderboard beyond
    the paper and project page.
contamination:
  risk: medium
  note: >
    Task text is public in the paper. Execution is on live commercial Android
    apps with a snapshot and dedicated test accounts, so there is no frozen
    answer key. App UI and APIs can drift after the snapshot date.
harness:
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: 'Paper protocol MAS-Bench-Eval (describe-and-judge). GitHub README (2026) says code and environment will be open-sourced; they were not on the main branch when this page was written.'
tags:
  - mobile
  - GUI
  - Android
  - shortcuts
  - agents
  - multimodal
sources:
  - url: https://arxiv.org/abs/2509.06477
    title: 'MAS-Bench (arXiv abs)'
    accessed: '2026-09-08'
  - url: https://arxiv.org/html/2509.06477v2
    title: 'MAS-Bench (arXiv HTML v2)'
    accessed: '2026-09-08'
  - url: https://pengxiang-zhao.github.io/MAS-Bench/
    title: 'MAS-Bench project page'
    accessed: '2026-09-08'
  - url: https://github.com/Pengxiang-zhao/MAS-Bench
    title: 'Pengxiang-zhao/MAS-Bench repository'
    accessed: '2026-09-08'
  - url: https://raw.githubusercontent.com/Pengxiang-zhao/MAS-Bench/main/README.md
    title: 'MAS-Bench GitHub README'
    accessed: '2026-09-08'
freshness:
  researched: '2026-09-08'
  researched_by: 'Grok Build, batch-078 (Codex coordinated)'
  reviewed: ''
  reviewed_by: ''
---

## What it measures

MAS-Bench tests a mobile agent that can either tap through an Android UI or take a shortcut. A shortcut is an API, a deep link, or a short RPA script. The agent gets an English instruction, a live app (or several apps), and an optional bank of 88 predefined shortcuts.

Every task can be finished with GUI actions alone. Shortcuts should cut steps and time, not unlock a hidden answer. A second track hides some shortcuts and asks the agent to invent reusable ones from its own traces. A fixed T3A baseline then runs the tasks with that generated library, so the score reflects the library rather than the generator's own control policy.

## How it is scored

The authors list nine metrics. Success rate (SR) is the one quoted as 68.3%. Efficiency uses step counts and time, including MSR and MSRS against a human GUI-only path from three experienced users. Cost and strategy metrics count tokens, shortcut calls, shortcut success, and the shortcut-to-GUI mix.

Success is not a string match. MAS-Bench-Eval first captions each step with an MLLM, then a stronger MLLM judge reads the instruction, the captions, and the last screenshot and issues a binary verdict. On 278 human-labeled traces the paper reports F1 96.3% and precision 98.1% against those labels. Table 2 averages 92 single-app and 47 cross-app tasks with task-count weights.

## Dataset and licence

There are 139 tasks on 11 apps: Amazon, Booking.com, Yelp, BBC News, Chrome, YouTube, Contacts, Fitbit, Gmail, Calendar, and Maps. Human GUI traces average 9.27 steps for single-app work and 17.66 for cross-app work. The shortcut bank is 11 APIs, 70 deep links, and 7 RPA scripts. Google Calendar has two shortcuts; Fitbit has 21.

The environment is a single AVD snapshot with logged-in test accounts. Online apps such as Amazon, YouTube, and Gmail use isolated accounts. No SPDX licence is on the GitHub repository or the project page. The arXiv HTML uses arXiv's non-exclusive distribution licence for the paper, not for the tasks or apps.

## Who publishes it

The authors are at Zhejiang University, vivo AI Lab, and Peking University. Equal first authors are Pengxiang Zhao, Guangyi Liu, and YaoZhen Liang. Corresponding author Kexin Zhang; project lead Liang Liu. arXiv v1 appeared on 8 September 2025; v2 on 15 April 2026. The GitHub README and project page say ACL 2026. The project page is the current public face of the results.

## Lineage

The hybrid agents wrap published GUI stacks such as T3A/M3A (AndroidWorld) and Mobile-Agent-v2. Those predecessors are not catalogued under this id. [GUI-CC](gui_cc.md) also uses mobile GUIs, but it scores world-model screen consistency, not shortcut use. Salesforce's MASBench in [mas_orchestra](mas_orchestra.md) is a different evaluation: synthetic multi-agent math graphs, not Android.

## Saturation and contamination

68.3% SR for MAS-GLM-4.5V leaves headroom, and GUI-only GLM-4.5V is at 52.6% SR in the same table. Task statements are public. Rewards depend on live apps and a judge, so memorizing the PDF does not finish a run. App updates can still invalidate shortcuts after the snapshot.

## How to run it

The paper's protocol is MAS-Bench-Eval on MAS-Bench-AVD. The GitHub README (accessed 2026-09-08) still says the code, environment, and evaluation resources will be open-sourced; the main branch had no runnable harness. Until that lands, numbers come from the paper's Table 2 protocol: predefined shortcut bank, T3A action-space mapping, Gemini-2.5-Pro for agentic-workflow bases. There is no lm-eval or inspect task.

## Reading the numbers

A high SR with MSRS below 1.0 means the agent finished more tasks in fewer steps than the human GUI path, usually by calling shortcuts. A high SR with many irrelevant shortcut calls is a different skill; the paper reports selection precision and a 23-task interference split for that. Do not treat 68.3% as a generic mobile-agent score: it is hybrid MAS-GLM-4.5V with the authors' 88-shortcut bank. Compare GUI-only and hybrid rows of the same backbone before reading a gain. This is not Salesforce MASBench.
