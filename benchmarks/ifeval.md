---
id: ifeval
name: IFEval
aliases: ["Instruction-Following Eval", "Instruction-Following Evaluation for Large Language Models"]
page_kind: benchmark
category: instruction-following
subcategory: "objectively verifiable natural-language instruction compliance"
status: active
summary: "IFEval scores whether a model's response obeys objectively checkable instructions, such as word counts or keyword frequency, using code rather than human or LLM judgment."
measures: >
  IFEval tests whether a model follows explicit, machine-checkable instructions layered onto a prompt,
  such as "write more than 400 words," "mention the keyword 'AI' at least 3 times," or "wrap your answer
  in double quotation marks." Each of the roughly 500 prompts combines one or more of 25 instruction types
  covering things like length, keyword use, formatting, punctuation and casing. Because every instruction
  can be checked by a program rather than a human or another model, scoring needs no subjective judgment
  call, unlike most instruction-following or helpfulness evaluations.
task_format: >
  A model is given a prompt containing one or more verifiable instructions and generates a free-form
  response in a single turn, zero-shot, with no few-shot examples. A separate verification function checks
  the response against each instruction mechanically (for example, counting words or scanning for a
  keyword) and returns pass/fail per instruction.
metric:
  name: "instruction-following accuracy (strict and loose, at the prompt level and the instruction level)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No formal random or human baseline published. Four related scores are reported per model: strict and
    loose accuracy, each computed both per-prompt (every instruction in the prompt must pass) and
    per-instruction (each instruction scored independently); "loose" scoring allows minor, immaterial
    response variations (such as markdown wrappers) that "strict" scoring does not.
dataset:
  size: 500
  size_note: "Approximately 500 prompts, each built from one or more of 25 types of verifiable instruction."
  url: "https://huggingface.co/datasets/google/IFEval"
  license: "CC BY 4.0"
  languages: [English]
  modalities: [text]
  splits: "single set (the lm-evaluation-harness implementation reads it from the \"train\" split)"
  public_test_set: true
publisher:
  org: "Google Research"
  authors: ["Jeffrey Zhou", "Tianjian Lu", "Swaroop Mishra", "Siddhartha Brahma", "Sujoy Basu", "Yi Luan", "Denny Zhou", "Le Hou"]
  url: "https://github.com/google-research/google-research/tree/master/instruction_following_eval"
paper:
  title: "Instruction-Following Evaluation for Large Language Models"
  arxiv: "2311.07911"
  url: "https://arxiv.org/abs/2311.07911"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/google-research/google-research/tree/master/instruction_following_eval"
released: "2023-11"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No current leaderboard was opened for this page, so a present-day top score is not established here.
    IFEval is widely reported (this repository's own model cards show scores well above 90% for several
    current models), which is at least suggestive of a benchmark under ceiling pressure, but that was not
    independently confirmed against a primary leaderboard in this research pass.
contamination:
  risk: medium
  note: >
    The prompt set and its verification code are fully public on Hugging Face and GitHub, and the
    benchmark has been in wide use since late 2023, so specific prompts and expected behaviours are likely
    present in more recent pretraining corpora. Because scoring is mechanical rather than answer-matched,
    memorising a plausible-sounding response is less obviously rewarded than on a fixed-answer benchmark,
    which may blunt but does not eliminate this risk.
harness:
  lm_eval: "ifeval"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Reference scoring code ships in the paper's own repository
    (google-research/instruction_following_eval). In lm-evaluation-harness, the `ifeval` task reads the
    `google/IFEval` dataset's "train" split, generates zero-shot with greedy decoding (temperature 0), and
    reports four metrics: prompt_level_strict_acc, inst_level_strict_acc, prompt_level_loose_acc and
    inst_level_loose_acc.
tags: [instruction-following, verifiable, zero-shot, text]
sources:
  - url: "https://arxiv.org/abs/2311.07911"
    title: "Instruction-Following Evaluation for Large Language Models"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/ifeval/ifeval.yaml"
    title: "lm-evaluation-harness: ifeval task config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice M"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

IFEval tests whether a model obeys explicit, checkable instructions layered onto an otherwise ordinary
prompt: constraints like writing more than 400 words, mentioning a keyword at least three times, avoiding
commas entirely, or wrapping the answer in double quotation marks. Roughly 500 prompts each combine one or
more of 25 such instruction types, covering length, keyword use, formatting, punctuation and casing. Every
instruction is written so that a program, not a person or another model, can check whether it was
followed.

## How it is scored

A model answers each prompt zero-shot, with no examples shown. A verification function checks the
response against every instruction in the prompt mechanically — counting words, scanning for a keyword,
checking capitalisation — and returns a pass or fail per instruction. Four related numbers are reported:
strict and loose accuracy, each computed at the prompt level (every instruction in the prompt must pass
for the prompt to count) and at the instruction level (each instruction scored on its own, so a
three-instruction prompt with two passes contributes partial credit at this level even though it fails at
the prompt level). "Loose" scoring tolerates minor response variations, such as extra markdown wrapping,
that "strict" scoring does not.

## Dataset and licence

About 500 prompts, released under CC BY 4.0 and hosted on Hugging Face as `google/IFEval`. The
lm-evaluation-harness implementation reads the dataset's "train" split, since no separate test split is
provided.

## Who publishes it

IFEval comes from Jeffrey Zhou, Tianjian Lu, Swaroop Mishra, Siddhartha Brahma, Sujoy Basu, Yi Luan, Denny
Zhou and Le Hou at Google Research, first posted to arXiv in November 2023. The reference dataset and
scoring code are maintained in Google's `google-research` GitHub monorepo.

## Lineage

This entry has no predecessor, successor or variant catalogued elsewhere in this repository; it is scored
as a standalone benchmark by every model card that reports it.

## Saturation and contamination

No primary leaderboard was opened for this page, so a current top score cannot be stated here with a
source behind it; this repository's own model cards show several current models scoring well above 90%,
which is at least suggestive of a benchmark under ceiling pressure, but that pattern was not checked
against an external leaderboard in this pass. Contamination risk is medium: the prompt set and its
verification logic are fully public and have been in wide use since late 2023, so specific prompts are
plausibly present in newer pretraining data, though the mechanical, non-answer-matched scoring means
memorising a specific correct answer is less directly rewarded than on a fixed-answer benchmark.

## How to run it

The paper's own repository ships reference scoring code. The most common path today is
lm-evaluation-harness's `ifeval` task, which generates greedily (no sampling) with a 1,280-token cap and
computes all four accuracy variants automatically; it also underlies several third-party leaderboard
suites built on that harness. It was not confirmed in the HELM, OpenCompass or BIG-bench task lists.

## Reading the numbers

A high IFEval score shows a model reliably obeys explicit, literal formatting and content constraints —
useful for anyone building on top of an API where downstream code parses the output. It says nothing about
whether the content of the response is correct, helpful, or well-reasoned, only whether its surface form
complied with what was asked; a model can write a wrong or unhelpful answer that nonetheless satisfies
every instruction. Because strict and loose, and prompt-level and instruction-level, accuracy can diverge,
check which of the four numbers is being reported before comparing scores across sources.
