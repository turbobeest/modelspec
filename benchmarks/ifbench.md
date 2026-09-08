---
id: ifbench
name: IFBench
aliases: []
page_kind: benchmark
category: instruction-following
subcategory: "generalization to unseen, verifiable output constraints"
status: active
summary: "IFBench tests whether a model can follow verifiable output constraints it was not trained on, rather than the small fixed set most instruction-following benchmarks reuse."
measures: >
  IFBench tests whether a model can follow explicit, machine-checkable output constraints -- things like
  "answer only yes or no" or "mention the word 'abrakadabra' at least three times" -- when the specific
  constraints are new to it rather than drawn from a small, well-known set. The paper that introduces it
  shows that models "strongly overfit on a small set of verifiable constraints from the benchmarks" used to
  train and evaluate them, and do not generalize well to constraint types they have not seen before; IFBench
  supplies 58 such new, out-of-domain constraint types, organised into seven categories (count, ratio,
  words, sentence, format, custom and copy), to measure that generalization gap directly rather than
  measure compliance with familiar constraints.
task_format: >
  A prompt with one or more verifiable constraints appended; the model answers in a single turn or across a
  short multi-turn exchange where the constraint is introduced separately from the original request. A
  constraint-specific verification function checks the response programmatically and returns pass or fail,
  the same mechanical approach IFEval uses.
metric:
  name: "strict and loose accuracy (prompt-level and instruction-level)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No formal random or human baseline is published. Following IFEval's convention, "strict" accuracy
    checks the raw response and "loose" accuracy tolerates minor formatting variation; both are reported at
    the prompt level (every constraint in the prompt must pass) and the instruction level (each constraint
    scored on its own).
dataset:
  size: 300
  size_note: >
    300 test prompts covering 58 new, hand-curated, out-of-domain verifiable constraint types across seven
    categories, evaluated under both a single-turn setting (the constraint appended to the original prompt)
    and a multi-turn setting (the constraint introduced in a separate follow-up turn). The paper separately
    releases 29 additional hand-annotated constraints with verification functions, plus RLVR training
    prompts, as training material distinct from this 300-prompt test set.
  url: "https://huggingface.co/datasets/allenai/IFBench_test"
  license: "ODC-BY-1.0 for the dataset (Hugging Face card); the allenai/IFBench code repository is separately licensed Apache-2.0."
  languages: ["en"]
  modalities: ["text"]
  splits: "single 300-prompt test set, run under single-turn and multi-turn conditions; no train/validation split in the test dataset itself"
  public_test_set: true
publisher:
  org: "Allen Institute for AI (Ai2), with the University of Washington"
  authors: ["Valentina Pyatkin", "Saumya Malik", "Victoria Graf", "Hamish Ivison", "Shengyi Huang", "Pradeep Dasigi", "Nathan Lambert", "Hannaneh Hajishirzi"]
  url: "https://github.com/allenai/IFBench"
paper:
  title: "Generalizing Verifiable Instruction Following"
  arxiv: "2507.02833"
  url: "https://arxiv.org/abs/2507.02833"
  year: 2025
leaderboard_url: "https://artificialanalysis.ai/evaluations/ifbench"
repo_url: "https://github.com/allenai/IFBench"
released: "2025-07"
last_updated: ""
lineage:
  family: ""
  predecessor: "ifeval"
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 83.3
  as_of: "2026-09"
  note: >
    At release (mid-2025), the paper reported that even strong instruction-tuned models such as Qwen3-32B
    and Claude 4 Sonnet scored below 50%. Artificial Analysis's independently run leaderboard, accessed
    2026-09-08 and tracking 450 models, instead showed Grok 4.3 (medium) leading at 83.3%, with Grok 4.20
    0309 (Reasoning) and MiniMax-M3 tied close behind at 82.9% each -- both a large rise from the paper's
    own headline finding and a top tier bunched within half a percentage point of each other, which is why
    this page reads the benchmark as under watch rather than fully open or saturated.
contamination:
  risk: medium
  note: >
    The 300-prompt test set and its verification code have been fully public on GitHub and Hugging Face
    since July 2025, over a year before this research pass, so its specific constraints are plausibly
    present in newer pretraining corpora. As with IFEval, mechanical, non-answer-matched scoring means
    memorising one plausible response is less directly rewarded than on a fixed-answer benchmark, which may
    blunt but does not eliminate the risk, and the paper's own finding -- that models overfit to whichever
    constraints they have already seen -- is itself evidence that prior exposure changes scores.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "IFBench"
  bigbench: ""
  other: >
    The authors' own evaluation code ships in github.com/allenai/IFBench, built on the same verification-
    function approach as IFEval and tied to Ai2's open-instruct RLVR training pipeline used in the paper's
    training experiments. OpenCompass registers the task as `IFBench`, with generation and raw-prompt config
    variants. Not confirmed in the lm-evaluation-harness, HELM or BIG-bench task lists.
tags: ["instruction-following", "verifiable", "generalization", "zero-shot", "multi-turn", "text"]
sources:
  - url: "https://arxiv.org/abs/2507.02833"
    title: "Generalizing Verifiable Instruction Following"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2507.02833"
    title: "Generalizing Verifiable Instruction Following, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/allenai/IFBench_test"
    title: "allenai/IFBench_test dataset card API, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=allenai/IFBench_test"
    title: "allenai/IFBench_test split size, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://github.com/allenai/IFBench"
    title: "allenai/IFBench repository"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/IFBench"
    title: "OpenCompass IFBench dataset configs"
    accessed: "2026-09-08"
  - url: "https://artificialanalysis.ai/evaluations/ifbench"
    title: "IFBench Benchmark Leaderboard, Artificial Analysis"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

IFBench tests whether a model can follow explicit, machine-checkable output constraints -- instructions
like "answer only yes or no" or "mention the word 'abrakadabra' at least three times" -- when the specific
constraints are new to it rather than drawn from a small, familiar set. The paper that introduces it shows
that models "strongly overfit on a small set of verifiable constraints from the benchmarks" used to train
and evaluate them, scoring well on constraint types they have effectively memorised while failing to
generalize to unseen ones, a skill the authors call precise instruction following. IFBench supplies 58 new,
hand-curated, out-of-domain constraint types across seven categories (count, ratio, words, sentence,
format, custom and copy) specifically to measure that generalization gap, rather than to measure compliance
with constraints a model has likely already seen during training or fine-tuning.

## How it is scored

A verification function specific to each constraint checks the model's response programmatically and
returns pass or fail, the same mechanical approach IFEval established. IFBench reports both strict accuracy
(the raw response must satisfy the constraint) and loose accuracy (minor formatting variation, such as
stray markdown, is tolerated), each computed at the prompt level (every constraint in a prompt must pass)
and the instruction level (each constraint scored independently). Prompts are run under two conditions: a
single-turn setting, where the constraint is appended to the original request, and a multi-turn setting,
where the constraint is introduced in a separate follow-up turn -- a harder test of whether a model tracks
an instruction once the immediate context has moved past it.

## Dataset and licence

300 test prompts cover the 58 new constraint types. The dataset card lists the release under ODC-BY-1.0,
distinct from the allenai/IFBench code repository's Apache-2.0 licence; both are maintained by the Allen
Institute for AI. Separately, and not part of this 300-prompt test set, the authors release 29 additional
hand-annotated constraints with their own verification functions, plus reinforcement-learning training
prompts, as material for training models to generalize better rather than for evaluating them.

## Who publishes it

IFBench comes from Valentina Pyatkin, Saumya Malik, Victoria Graf, Hamish Ivison, Shengyi Huang, Pradeep
Dasigi, Nathan Lambert and Hannaneh Hajishirzi, working at the Allen Institute for AI with the University of
Washington, published as "Generalizing Verifiable Instruction Following" on arXiv in July 2025 and accepted
to NeurIPS 2025's Datasets and Benchmarks track. Ai2 maintains the reference dataset and code at
github.com/allenai/IFBench; Artificial Analysis independently runs and publishes a continuously updated
leaderboard.

## Lineage

IFBench is a direct response to IFEval (also in this repository, ifeval.md): the paper builds on IFEval's
mechanically-verifiable-instruction approach but deliberately uses a disjoint set of 58 new constraints,
stating these "go beyond the 25 constraints included in IFEval," specifically because models had begun
overfitting to IFEval's fixed set. It has no successor or variant catalogued in this repository.

## Saturation and contamination

At release in mid-2025, even strong instruction-tuned models such as Qwen3-32B and Claude 4 Sonnet scored
below 50%, and reinforcement learning with verifiable rewards measurably improved smaller models
(Tülu-3-8B rose from 28.9% to 45.9%). Artificial Analysis's independently run leaderboard, accessed
2026-09-08 and tracking 450 models, instead showed Grok 4.3 (medium) leading at 83.3%, with Grok 4.20 0309
(Reasoning) and MiniMax-M3 close behind at 82.9% each -- a large rise from the paper's results and a top
tier bunched within half a point, which is why this page treats it as under watch rather than open or
saturated. Contamination risk is medium: the test set and verification code have been public for over a
year, so specific constraints are plausibly in newer pretraining data, though mechanical, non-answer-matched
scoring blunts (without eliminating) the reward for memorising one response, and the paper's central finding
-- that models overfit to constraints they have already seen -- is itself evidence that prior exposure moves
scores here too.

## How to run it

The reference evaluation code ships in github.com/allenai/IFBench, using the same per-constraint
verification-function approach as IFEval, and ties to Ai2's open-instruct RLVR training pipeline used in the
paper's own experiments. OpenCompass registers the task as `IFBench`, with separate generation and
raw-prompt config variants. Not confirmed in the lm-evaluation-harness, HELM or BIG-bench task lists.

## Reading the numbers

A high IFBench score is stronger evidence of genuine instruction-following generalization than a high
IFEval score, precisely because its constraints were built to be unfamiliar rather than reused from a
well-known set -- that is the whole point of the benchmark. Because the multi-turn setting is measurably
harder than the single-turn one (the constraint has to survive being separated from the original request),
check which setting a reported score used before comparing it to another. As with IFEval, a high score says
a model reliably obeys literal, checkable formatting and content rules; it says nothing about whether the
substance of the response is correct or useful, and strict versus loose, and prompt-level versus
instruction-level, accuracy can diverge enough to change a ranking.
