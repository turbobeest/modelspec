---
id: superclue_safety
name: "SuperCLUE-Safety"
aliases:
  - "SC-Safety"
  - "SuperCLUE Safety"
page_kind: benchmark
category: safety
subcategory: "Chinese multi-turn adversarial open-ended safety, responsibility and instruction-attack eval"
status: unknown
summary: "Chinese multi-turn adversarial safety eval of 4,912 open-ended items scored 0-2 across traditional safety, responsible AI and instruction attacks."
measures: >
  SuperCLUE-Safety (SC-Safety) tests whether a Chinese LLM stays safe in open-ended
  chat when the user follows up. Each item is a question plus an adversarial follow-up.
  Coverage is three capability groups and 20-plus sub-dimensions: traditional safety
  (privacy, crime, injury, ethics), responsible AI (law-abiding behaviour, social
  harmony, psychological advice) and instruction attacks (negative induction, goal
  hijacking, unsafe role-play, unsafe instruction themes). The paper argues that
  multiple-choice safety tests overstate robustness once the same model faces a
  second open-ended turn.
task_format: >
  Two-turn open-ended Chinese dialogue: an initial adversarial question and a
  scripted follow-up. A dedicated safety judge assigns 0, 1 or 2 to each model reply.
metric:
  name: "mean 0-2 safety grade, reported as a percentage of the maximum"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    0 = unsafe or misled reply (including high-risk content that adds a safety
    disclaimer); 1 = safe but unhelpful refusal or weak advice; 2 = safe and
    constructive. The GitHub README defines the published total as the sum of item
    scores divided by the maximum possible total. The English paper also says the
    total is the sum divided by the number of questions; that wording cannot produce
    the 0-100 tables, so the GitHub definition is the one that matches the numbers.
dataset:
  size: 4912
  size_note: >
    4,912 open-ended questions, described as 2,456 pairs (question plus follow-up).
    Each of 20-plus sub-dimensions uses 80-120 pairs. The GitHub tree has README
    files and images only; the items themselves are not in the public repo.
  url: "https://www.cluebenchmarks.com/superclue_safety.html"
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "each item is a two-turn pair; no public train/test split is documented"
  public_test_set: false
publisher:
  org: "CLUE / CLUEbenchmark"
  authors:
    - "Liang Xu"
    - "Kangkang Zhao"
    - "Lei Zhu"
    - "Hang Xue"
  url: "https://www.cluebenchmarks.com/superclue_safety.html"
paper:
  title: "SC-Safety: A Multi-round Open-ended Question Adversarial Safety Benchmark for Large Language Models in Chinese"
  arxiv: "2310.05818"
  url: "https://arxiv.org/abs/2310.05818"
  year: 2023
leaderboard_url: "https://www.cluebenchmarks.com/superclue_safety.html"
repo_url: "https://github.com/CLUEbenchmark/SuperCLUE-Safety"
released: "2023-10"
last_updated: "2024-01"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 92.51
  as_of: "2024-01"
  note: >
    GitHub README dated 2024-01-04 lists BlueLM at 92.51 overall. The paper's
    13-model table and the cluebenchmarks.com page still show GPT-4 at 87.43 with
    Xinghuo 4.0 as the top ranked Chinese row at 84.98. Those are different
    snapshots, not one ranking.
contamination:
  risk: unknown
  note: >
    Items were built by iterating human-model attacks until a judge marked the
    prompt as risky. The public GitHub repo does not ship the questions, so
    membership in training data is not established.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - chinese
  - safety
  - adversarial
  - multi-turn
  - instruction-attack
sources:
  - url: "https://arxiv.org/abs/2310.05818"
    title: "SC-Safety paper (arXiv:2310.05818)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2310.05818"
    title: "SC-Safety HTML full text"
    accessed: "2026-09-08"
  - url: "https://github.com/CLUEbenchmark/SuperCLUE-Safety"
    title: "CLUEbenchmark/SuperCLUE-Safety GitHub repository"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/CLUEbenchmark/SuperCLUE-Safety/main/README.md"
    title: "SuperCLUE-Safety README (2024-01 update)"
    accessed: "2026-09-08"
  - url: "https://www.cluebenchmarks.com/superclue_safety.html"
    title: "SuperCLUE-Safety official page"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-082 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

SuperCLUE-Safety, also called SC-Safety, measures Chinese LLM safety in two-turn open-ended chat. The user first poses an adversarial request, then a follow-up that tries to push the model off its first refusal.

The suite covers three groups. Traditional safety asks whether the model avoids crime, injury, privacy leaks and basic unethical advice. Responsible AI asks for value-aligned answers on law, social harm and psychological topics. Instruction attacks try to jailbreak the model with reversed instructions, goal hijacking or unsafe roles.

## How it is scored

A specialised safety judge grades each reply 0, 1 or 2. Zero means the reply is unsafe or was led by the prompt. One means a safe but thin refusal. Two means a safe reply that also gives usable advice. Severe illegal or politically sensitive content still scores 0 even if the model adds a warning.

Published totals are percentages of that 0-2 maximum. The paper also reports round-1 versus round-2 scores. Many models drop on the follow-up; Llama-2-13B-Chat drops 11.06 points in the paper table.

On a Chinese-Alpaca-2-13B sample, automated grades matched a three-person majority vote exactly 77% of the time and within one point 85% of the time. The authors still flag judge error as a limit.

## Dataset and licence

The paper states 4,912 questions, i.e. 2,456 pairs, with 80-120 pairs per sub-dimension. Construction loops a sampled prompt through a model, scores the risk, and rewrites safe prompts until they elicit a risky reply or are dropped.

The GitHub API reports no licence. The public repo is documentation and figures, not the item files. The paper points readers to cluebenchmarks.com rather than a downloadable split.

## Who publishes it

Liang Xu, Kangkang Zhao, Lei Zhu and Hang Xue released the paper on 9 October 2023. CLUEbenchmark hosts the GitHub repo (created 2023-09-11) and the live page. The GitHub README records a 4 January 2024 model-list update. The last GitHub push seen for this page is 2024-03-15.

GPT-4 and GPT-3.5-turbo appear on the tables but are excluded from Chinese ranking, matching other SuperCLUE boards.

## Lineage

SC-Safety sits under SuperCLUE, the 2023 Chinese LLM suite (arXiv:2307.15020), and is distinct from the older CLUE NLU family. The paper positions it against Safety-Prompts, SafetyBench and [CValues](cvalues.md): those sets are mostly single-turn or multiple-choice, and the authors found them too easy.

[superclue_agent](superclue_agent.md) is a sibling agent track, not this safety set. There is no SuperCLUE family page in this repository yet.

## Saturation and contamination

The January 2024 GitHub table tops out at BlueLM 92.51, with Yi-34B-Chat at 89.30 and GPT-4 at 87.43. That is high but not a full ceiling, and instruction-attack columns remain lower (MiniMax-Abab5.5 at 63.82 on that table).

The official webpage still shows the older paper-era ranking (GPT-4 87.43, Xinghuo 4.0 84.98). Cite the snapshot. Items are unpublished, so contamination is unknown.

## How to run it

No lm-eval, inspect_evals, HELM, OpenCompass or BIG-bench task name was confirmed. Running the benchmark requires CLUE's judge and the unpublished pairs.

Do not mix GitHub 2024 rows with the paper's 13-model table. Round-2 drops are part of the protocol; a single-turn score is not SC-Safety.

## Reading the numbers

A high total means the judge found safe, often constructive replies to Chinese adversarial two-turn prompts. It is not a Western red-team suite and not CValues' two-choice responsibility accuracy.

Read the three columns. Closed-source Chinese APIs lead the 2023-2024 tables on traditional safety, while some 6B-13B open models stay close on instruction attacks. A small round-1 to round-2 drop is the robustness signal the authors emphasise.

Because items and the judge are not public, you cannot audit a third-party SC-Safety number without CLUE.
