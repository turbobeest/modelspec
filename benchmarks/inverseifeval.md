---
id: inverseifeval
name: "Inverse IFEval"
aliases: ["InverseIFEval"]
page_kind: benchmark
category: instruction-following
subcategory: "counter-conventional instruction following: overriding SFT-trained habits to comply with instructions that conflict with them"
status: active
summary: "Inverse IFEval tests whether a model can override trained habits -- always answering, always correct, always-commented code -- to comply with instructions that deliberately conflict with them."
measures: >
  Inverse IFEval tests a model's ability to override the standardised habits instilled by supervised
  fine-tuning and comply with an instruction that deliberately conflicts with them, rather than testing
  whether it follows ordinary, cooperative instructions the way IFEval (in this repository) does. Its
  1,012 prompts span eight challenge types: Question Correction (recognise that a multiple-choice
  question has no correct option, instead of picking the closest wrong one), Intentional Textual Flaws,
  Code without Comments, Counter-Conventional Formatting, Deliberately Incorrect Answers, Instructional
  Induction, Mid-turn Instruction Modification, and Counterfactual Answering. One released example asks
  a model to solve a rigged word problem whose four multiple-choice options are all numerically wrong;
  earning credit requires stating that none of the options is correct rather than defaulting to picking
  one, the trained habit the item is built to surface.
task_format: >
  Single-turn free-text generation for most items; Mid-turn Instruction Modification introduces a
  change to the instruction partway through a multi-part prompt instead. Every item carries its own
  reference criteria describing exactly what a compliant response must and must not contain, and its
  own bundled LLM-judge system prompt and prompt template, rather than one fixed judge prompt applied
  across the whole dataset. Items were constructed through a human-in-the-loop pipeline across 23
  domains, in matched Chinese and English versions.
metric:
  name: "binary pass rate under LLM-as-judge grading (0 or 1 per response, scored against the item's own bundled reference criteria), reported overall and per instruction type and language"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Grading is strictly binary per the dataset's own bundled judge system prompt: a response earns one
    point only if it satisfies every requirement in the item's reference criteria, and zero otherwise,
    with explicit instructions to the judge not to award partial credit for meeting some but not all
    requirements. No random or human baseline applies to open-ended generation graded this way.
dataset:
  size: 1012
  size_note: >
    1,012 prompts, confirmed directly from the released dataset file: exactly 506 Chinese and 506
    English items, split across eight instruction types (Code without Comments 198, Deliberately
    Incorrect Answers 186, Instructional Induction 154, Mid-turn Instruction Modification 108,
    Counterfactual Answering 108, Question Correction 90, Intentional Textual Flaws 86,
    Counter-Conventional Formatting 82), each type split evenly in half between the two languages. The
    paper states the 1,012 items cover 23 domains. OpenCompass's own config reproduces the same eight
    per-type counts as combined Chinese+English totals, built into 16 separate dataset variants -- one
    per instruction type per language.
  url: "https://huggingface.co/datasets/m-a-p/Inverse_IFEval"
  license: ""
  languages: [English, Chinese]
  modalities: [text, code]
  splits: "single 'train' split (1,012 rows) used as the evaluation set"
  public_test_set: true
publisher:
  org: "Hosted under the m-a-p (Multimodal Art Projection) organisation on Hugging Face; individual authors' institutional affiliations were not confirmed from a source read for this page"
  authors: ["Qinyan Zhang", "Xinping Lei", "Ruijie Miao", "Yu Fu", "Haojie Fan", "Le Chang", "Jiafan Hou", "Dingling Zhang", "Zhongfei Hou", "Ziqiang Yang", "Changxin Pu", "Fei Hu", "Jingkai Liu", "Mengyun Liu", "Yang Liu", "Xiang Gao", "Jiaheng Liu", "Tong Yang", "Zaiyuan Wang", "Ge Zhang", "Wenhao Huang"]
  url: "https://huggingface.co/datasets/m-a-p/Inverse_IFEval"
paper:
  title: "Inverse IFEval: Can LLMs Unlearn Stubborn Training Conventions to Follow Real Instructions?"
  arxiv: "2509.04292"
  url: "https://arxiv.org/abs/2509.04292"
  year: 2025
leaderboard_url: ""
repo_url: "https://huggingface.co/datasets/m-a-p/Inverse_IFEval"
released: "2025-09"
last_updated: "2025-09"
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
    The paper's abstract states that experiments on "existing leading LLMs demonstrate the necessity"
    of the benchmark, implying non-trivial failure rates, but the full results tables were not
    extracted from a source read for this page (the PDF's results tables did not render through the
    tools available in this research pass), so no specific model score is recorded here.
contamination:
  risk: medium
  note: >
    The dataset, including every item's detailed reference criteria, has been public on Hugging Face
    for about a year as of this research. Grading is a qualitative LLM-judge match against those
    criteria rather than an exact-string answer key, so classic answer memorisation does not apply
    directly -- but because each item's expected response pattern is fixed and specific (for example,
    "state that no option is correct" for a given Question Correction item), a model could still be
    tuned on the known items and their expected behaviour pattern, which is a narrower but real
    contamination path.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "InverseIFEval_gen"
  other: >
    OpenCompass's config builds 16 separate dataset entries named `InverseIFEval_{language}_{type}`
    (for example `InverseIFEval_en_QC`), one per instruction type per language, each scored through
    OpenCompass's `GenericLLMEvaluator` using that specific item's own bundled `judge_system_prompt` and
    `judge_prompt_template` fields rather than one fixed judge template applied dataset-wide.
tags: [instruction-following, counter-conventional, bilingual, llm-judge, adversarial-instructions]
sources:
  - url: "https://arxiv.org/abs/2509.04292"
    title: "Inverse IFEval: Can LLMs Unlearn Stubborn Training Conventions to Follow Real Instructions?"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/m-a-p/Inverse_IFEval"
    title: "m-a-p/Inverse_IFEval metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=m-a-p/Inverse_IFEval"
    title: "Inverse_IFEval split info and features, datasets-server"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/m-a-p/Inverse_IFEval/resolve/main/Inverse_IFEval_Dataset.json"
    title: "Inverse_IFEval_Dataset.json: the 1,012 released items"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/InverseIFEval/InverseIFEval_rawprompt_gen.py"
    title: "OpenCompass InverseIFEval_rawprompt_gen.py: instruction-type counts and dataset build"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Inverse IFEval tests whether a model can override the standardised habits instilled by supervised
fine-tuning -- always give an answer, always write correct code, always add comments, always follow a
learned formatting convention -- when an instruction explicitly asks it to do otherwise. That is close to
the opposite of what IFEval (in this repository) tests: IFEval checks compliance with ordinary,
cooperative verifiable instructions, while Inverse IFEval checks compliance when the instruction runs
against what training has taught the model to do by default. Its 1,012 prompts span eight challenge types,
including Question Correction, Code without Comments, Deliberately Incorrect Answers and Counterfactual
Answering. One released item asks a model to solve a rigged word problem whose four multiple-choice options
are all numerically wrong; the correct behaviour is to state that none of the options is right rather than
default to picking the closest one, which is exactly the trained habit the item is designed to surface.

## How it is scored

Most items are single-turn free-text generation; Mid-turn Instruction Modification instead introduces a
change to the instruction partway through a multi-part prompt, testing whether the model keeps following
the update rather than the original framing. Every item carries its own reference criteria spelling out
what a compliant response must and must not do, together with its own bundled LLM-judge system prompt and
prompt template -- an unusual design choice, since most LLM-judged benchmarks apply one fixed judge prompt
across the whole set. Grading is strictly binary: a response earns one point only if it satisfies every
stated requirement, and the judge is explicitly instructed not to award partial credit.

## Dataset and licence

1,012 prompts, confirmed directly from the released file: exactly 506 Chinese and 506 English items,
divided across the eight instruction types in proportions ranging from 82 items (Counter-Conventional
Formatting) to 198 (Code without Comments), each type split evenly between the two languages. The paper
states the items span 23 domains. No licence is published on the Hugging Face dataset page. There is a
single `train` split used directly for evaluation, with no separate held-out test split.

## Who publishes it

The paper "Inverse IFEval: Can LLMs Unlearn Stubborn Training Conventions to Follow Real Instructions?" was
submitted to arXiv on 4 September 2025, with 21 listed authors headed by Qinyan Zhang, Xinping Lei and
Ruijie Miao; individual institutional affiliations were not confirmed from a source read for this page. The
dataset is hosted under the m-a-p (Multimodal Art Projection) organisation on Hugging Face, which also
publishes several other benchmarks and datasets independent of this one.

## Lineage

No predecessor or successor is tracked for this id in this repository. Its name and its explicit framing as
testing the complement of ordinary instruction-following place it alongside IFEval, IFBench and AdvancedIF
(all in this repository), though none of those pages' own materials cite Inverse IFEval directly, and
Inverse IFEval's own materials read for this page do not cite IFEval by name either -- the relationship is
one of shared territory and an intentionally opposite name, not a confirmed direct lineage. It is also a
close cousin of `ifevalcode` (also in this repository), which decouples code correctness from instruction
adherence rather than testing adherence against a model's trained default behaviour specifically.

## Saturation and contamination

The paper's abstract states that testing "existing leading LLMs" demonstrates the benchmark's necessity,
which implies meaningful failure rates among current models, but this page's research did not extract the
paper's full results tables, so no specific model score is recorded here. Contamination risk is medium: the
dataset, including every item's detailed reference criteria, has been public for about a year as of this
research. Grading is a qualitative LLM-judge match rather than an exact-string answer key, so classic
memorisation does not apply directly, but each item's expected response pattern is fixed and specific
enough that a model could plausibly be tuned against the known items and what they expect.

## How to run it

OpenCompass implements this as 16 separate dataset entries, one per instruction type per language, named
`InverseIFEval_{language}_{type}` (for example `InverseIFEval_en_QC`), built from the config module
`InverseIFEval_rawprompt_gen.py`. Each entry is scored through OpenCompass's `GenericLLMEvaluator` using
that specific item's own bundled judge system prompt and judge prompt template rather than one fixed
dataset-wide judge configuration, so reproducing a reported score requires using the exact per-item judge
prompts shipped with the dataset, not a generic LLM-judge setup substituted in by a different harness.

## Reading the numbers

A high score shows a model can suppress its trained default behaviour on command -- answering "no correct
option" instead of guessing, omitting comments when told to, following a formatting instruction it was
never trained to prefer. It says nothing about how well the model performs when instructions are ordinary
and cooperative, which is what IFEval-style benchmarks measure instead; a model can score well on one and
poorly on the other, since they test opposite failure modes. Because grading depends on a per-item bundled
judge prompt rather than one fixed judge, scores computed with a substituted judge setup are not a reliable
comparison against scores computed with the dataset's own judge prompts.
