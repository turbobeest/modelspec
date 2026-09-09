---
id: cybergym
name: "CyberGym"
aliases:
  - "CyberGym: Evaluating AI Agents' Real-World Cybersecurity Capabilities at Scale"
page_kind: benchmark
category: agentic
subcategory: "proof-of-concept generation for historical OSS-Fuzz/ARVO vulnerabilities"
status: active
summary: "1,507 real patched vulnerabilities across 188 projects; agents must write a PoC that crashes the unpatched binary but not the fix."
measures: >
  CyberGym asks an agent to reproduce a historical memory-safety bug. The default
  (level-1) setting gives the unpatched codebase plus a short vulnerability
  description. The agent must emit a proof-of-concept file that crashes the
  pre-patch build under sanitizers and does not crash the post-patch build.
  A PoC that also crashes the patched program is counted as a new vulnerability,
  not a reproduction. This is live tool use against compiled targets, not a
  quiz about CVEs.
task_format: >
  Docker sandbox with a solver container and separate vulnerable and fixed
  program containers. The agent writes a PoC and submits it through submit.sh.
  inspect_evals defaults to a react solver, max_attempts=3, level1 only, no
  k8s. Four difficulty levels change which files are mounted (code only, plus
  description, plus crash log, plus patch and fixed tree).
metric:
  name: "reproduction rate (PoC crashes unpatched and not patched); new-vulnerability rate (PoC also crashes the patch)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No random-guess rate applies. arXiv v3 (24 March 2026) no longer treats
    Claude 3.7 Sonnet as the headline best: OpenHands plus Claude Sonnet 4
    reaches 17.9% reproduction with thinking off on the full primary task.
    GPT-5 with high reasoning reaches 22.0% on a 300-instance subset. Claude
    3.7 Sonnet remains 11.9% (169/1419) on the pre-cutoff split of that table.
    inspect_evals README (eval version 2-A, May 2026, full 1,507 level1
    samples) reports gpt-4.1-2025-04-14 at 0.1161 reproduced and 0.0312
    new_vulnerability under a 202-message cap and no internet in the solver
    sandbox; that is a different agent stack than the paper's OpenHands runs.
dataset:
  size: 1507
  size_note: >
    1,507 vulnerabilities across 188 projects: 1,368 adapted from ARVO and 139
    later OSS-Fuzz cases (paper; disclosure dates through 21 April 2025).
    inspect_evals eval.yaml lists 6,028 samples because it materialises all
    four variants (1,507 × 4). Hugging Face snapshot sunblaze-ucb/cybergym
    at revision bde190ded494e52bc684b66073b436c9d992c7c6; inspect README says
    the full snapshot is 236 GB, the official README says about 240 GB.
  url: "https://huggingface.co/datasets/sunblaze-ucb/cybergym"
  license: "Apache-2.0 (official repository); bundled project trees keep their upstream licences"
  languages:
    - en
  modalities:
    - text
    - code
  splits: "no train/test split; 1,507 instances, each with four difficulty variants (level0 hardest / level3 easiest)"
  public_test_set: true
publisher:
  org: "University of California, Berkeley"
  authors:
    - "Zhun Wang"
    - "Tianneng Shi"
    - "Jingxuan He"
    - "Matthew Cai"
    - "Jialin Zhang"
    - "Dawn Song"
  url: "https://github.com/sunblaze-ucb/cybergym"
paper:
  title: "CyberGym: Evaluating AI Agents' Real-World Cybersecurity Capabilities at Scale"
  arxiv: "2506.02548"
  url: "https://arxiv.org/abs/2506.02548"
  year: 2025
leaderboard_url: "https://www.cybergym.io/"
repo_url: "https://github.com/sunblaze-ucb/cybergym"
released: "2025-06"
last_updated: "2026-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 17.9
  as_of: "2026-03"
  note: >
    Full-set non-thinking best in arXiv v3: 17.9% with OpenHands + Claude
    Sonnet 4 on level 1. GPT-5 high-reasoning is 22.0% on a 300-instance
    subset, not the full 1,507. Claude 3.7 Sonnet is still 11.9% on the
    paper's pre-cutoff split. inspect_evals' GPT-4.1 full-set run is 11.61%
    reproduced under a different solver. Most of the 1,507 instances remain
    unsolved.
contamination:
  risk: medium
  note: >
    Codebases and many vulnerability reports are public web text. v3 splits
    instances by disclosure versus knowledge cutoff and reports no
    statistically significant gap (Claude 3.7 Sonnet 11.9% before cutoff vs
    12.5% after; Fisher p=0.87). Ground-truth PoCs ship in the Hugging Face
    snapshot. inspect_evals versions before 2-A (2026-04-03) tested the wrong
    PoC and are invalid.
harness:
  lm_eval: ""
  inspect_evals: "cybergym"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Official runner: python3 -m cybergym.task.gen_task with a local PoC server on port 8666. inspect default variant is level1."
tags:
  - cybersecurity
  - agentic
  - vulnerability-reproduction
  - oss-fuzz
  - arvo
  - inspect-evals
sources:
  - url: "https://arxiv.org/abs/2506.02548"
    title: "CyberGym paper (arXiv:2506.02548)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2506.02548v3"
    title: "CyberGym v3 HTML (24 Mar 2026; 17.9% / 22.0% results)"
    accessed: "2026-09-08"
  - url: "https://github.com/sunblaze-ucb/cybergym"
    title: "sunblaze-ucb/cybergym (Apache-2.0, ICLR 2026 citation, setup)"
    accessed: "2026-09-08"
  - url: "https://www.cybergym.io/"
    title: "CyberGym site (now Frontier AI Cybersecurity Observatory landing page)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/sunblaze-ucb/cybergym"
    title: "Hugging Face dataset card API (revision bde190d, 2025-05-15)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/cybergym/README.md"
    title: "inspect_evals CyberGym README (metrics, GPT-4.1 2-A report, changelog)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/cybergym/eval.yaml"
    title: "inspect_evals eval.yaml (cybergym, 6028 samples, arXiv 2506.02548)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/cybergym/dataset.py"
    title: "inspect_evals dataset.py (levels 0-3, HF pin)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/UKGovernmentBEIS/inspect_evals/main/src/inspect_evals/cybergym/scorers.py"
    title: "inspect_evals scorers.py (reproduced vs new_vulnerability)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-037 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-037"
---

## What it measures

CyberGym tests whether an agent can turn a vulnerability write-up into a working crash. Each of the 1,507 items is a real bug found by OSS-Fuzz, later patched, and packaged with pre-patch and post-patch builds. In the default level-1 setting the agent gets the unpatched tree and a short description, then must produce a PoC that hits the historical bug from the program entry point. arXiv v3 counts success only when the pre-patch build crashes and the post-patch build does not. inspect_evals still records a separate `new_vulnerability` rate when both builds crash.

The skill is multi-step code reasoning plus sanitizer-backed execution. It is not Cybench's CTF flags, CVE-Bench's web exploits, or the Lucideus CyberGym CTF of the same nickname.

## How it is scored

inspect_evals sets `reproduced` when the vulnerable binary exits non-zero and the fixed binary exits zero, and `new_vulnerability` when both crash. Missing PoC files score zero; a broken executor raises rather than counting as a model failure (changelog 3-A). arXiv v3's benchmark metric is reproduction only: a sanitizer crash on the pre-patch build and none on the post-patch build. Post-patch crashes are analysed separately as incomplete patches or other bugs, not as a second headline rate. inspect_evals' GPT-4.1 full-set row used a react solver, a 202-message limit meant to match 100 paper iterations, and a sandbox without internet. Do not mix paper rows with inspect rows.

## Dataset and licence

1,507 instances, 188 projects, 1,368 from ARVO plus 139 newer OSS-Fuzz bugs. Four levels add files: level 0 is code only; level 1 adds `description.txt`; level 2 adds the crash log; level 3 adds the patch and the fixed tree. The official GitHub tree is Apache-2.0; the Hugging Face snapshot also ships third-party sources under their own licences. Full data is about 240 GB. The authors warn not to expose the PoC server to the public internet.

## Who publishes it

UC Berkeley authors Zhun Wang, Tianneng Shi, Jingxuan He, Matthew Cai, Jialin Zhang, and Dawn Song. arXiv 2506.02548 appeared 3 June 2025; v3 (24 March 2026) is the text used here. The GitHub README cites ICLR 2026 (OpenReview `2YvbLQEdYt`). inspect_evals currently pins eval version 3-B (3 August 2026). cybergym.io now hosts a broader observatory that also links ExploitGym and CyberGym-E2E.

## Lineage

No family page. Related agent security evals already in this repository include [Cybench](cybench.md) and [CVE-Bench](cve_bench.md); they use different tasks and sandboxes. CyberGym-E2E (discover, PoC, patch) and ExploitGym are later Berkeley suites and do not yet have pages here. ARVO is a construction source, not a successor.

## Saturation and contamination

v3's full-set non-thinking best is 17.9% (Claude Sonnet 4). GPT-5 high-reasoning hits 22.0% on 300 items. Claude 3.7 Sonnet is still 11.9% on the pre-cutoff split. The v3 abstract also reports 34 zero-days and 18 incomplete patches from agent PoCs, which is a discovery claim, not a reproduction rate. Pre-/post-cutoff splits did not show a significant memorisation gap. Public code and public PoCs still make leakage possible. Discard inspect_evals runs from before version 2-A: those scored the wrong file.

## How to run it

Official: install `sunblaze-ucb/cybergym`, download the Hugging Face snapshot, bind the PoC server to the Docker-network gateway, then `python3 -m cybergym.task.gen_task --difficulty level1`. inspect_evals: `inspect eval inspect_evals/cybergym` with optional `-T eval_names` and `-T variant_names`. Default variant is level1. k8s is not implemented. Pin the eval version; 2-A and 3-A both changed scoring.

## Reading the numbers

A double-digit reproduction rate on level 1 means the agent crashed some historical bugs with the description in hand. It does not mean the agent can find new bugs from source alone (that is level 0) or write a patch (CyberGym-E2E). Always name the paper version or inspect eval version, the level, the agent stack, and whether the figure is `reproduced` or `new_vulnerability`. Compare Cybench only as a different cybersecurity skill, not as the same score.
