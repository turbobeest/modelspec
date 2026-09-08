---
id: advancedif
name: "AdvancedIF"
aliases: ["Advanced Instruction Following"]
page_kind: benchmark
category: instruction-following
subcategory: "expert-written, rubric-graded instruction following: complex single-turn, multi-turn carried context, and system-prompt steerability"
status: active
summary: "Meta's 1,645-prompt instruction-following benchmark, expert-written and LLM-judged against per-prompt rubrics, covering complex single-turn instructions, multi-turn carried context and system-prompt steerability."
measures: >
  AdvancedIF tests instruction following across three capabilities that IFEval-style mechanically-checked
  benchmarks were not built to cover: complex single-turn instructions (each prompt combines six or more
  simultaneous constraints -- tone, format, style, structure, length, negative constraints, spelling and
  instructions that depend on one another), multi-turn carried context (whether a model keeps honouring an
  instruction given earlier in a conversation once the conversation has moved past it), and system-prompt
  steerability (whether a model follows instructions placed in the system prompt rather than the user
  turn, including persona and scope restrictions). Every prompt is expert-written rather than built from a
  template, and is paired with an expert-curated rubric -- a checklist of specific yes/no questions a
  correct response must satisfy, many of which (tone, persona consistency, whether an explanation
  "feels" grounded) cannot be checked by a program the way IFEval's or IFBench's constraints can, which is
  why AdvancedIF grades with an LLM judge instead of verification code.
task_format: >
  Free-text response to a single-turn or multi-turn conversation (including, for the system-steerability
  subset, a system prompt the response must respect). An LLM judge reads the full conversation, the
  response and the prompt's rubric, answers each rubric question, and outputs whether the response
  satisfied every rubric item.
metric:
  name: "rubric satisfaction rate (share of responses that satisfy every item in their prompt's rubric), reported per subset and averaged across the three"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    A response passes only if it satisfies every question in its rubric -- an all-or-nothing standard
    like IFEval's "prompt-level strict" accuracy, generalised to naturalistic constraints a program
    cannot check. There is no meaningful random baseline for open-ended generation graded this way. The
    paper instead validates its judge against human-labelled agreement: a fine-tuned rubric verifier
    reached an F1 of 0.728 against human judgments, its recommended off-the-shelf judge (o3-mini)
    reached 0.723, and a vanilla Llama 4 Maverick judge reached only 0.515 -- evidence that judge choice
    materially affects how trustworthy a reported score is, not a task-performance baseline itself.
dataset:
  size: 1645
  size_note: >
    1,645 prompts across three subsets, confirmed from the Hugging Face dataset card's split metadata
    and matching the paper: 402 complex single-turn instruction-following prompts (`complex_if_single_turn_v5`),
    736 multi-turn carried-context prompts (`carried_context_multi_turn_eval_v5`), and 507 system-prompt
    steerability prompts (`system_steerability_v2`). Prompts and rubrics are hand-written by experts
    rather than generated from templates, which the authors present as a deliberate contrast to
    synthetically constructed instruction-following prompt sets.
  url: "https://huggingface.co/datasets/facebook/AdvancedIF"
  license: "CC BY-NC 4.0"
  languages: ["en"]
  modalities: ["text"]
  splits: "single test split (1,645 examples) across the three named subsets; no train/validation split"
  public_test_set: true
publisher:
  org: "Meta Superintelligence Labs (Meta), with contributions from Princeton University and Carnegie Mellon University"
  authors: ["Yun He", "Wenzhe Li", "Hejia Zhang", "et al."]
  url: "https://github.com/facebookresearch/AdvancedIF"
paper:
  title: "AdvancedIF: Rubric-Based Benchmarking and Reinforcement Learning for Advancing LLM Instruction Following"
  arxiv: "2511.10507"
  url: "https://arxiv.org/abs/2511.10507"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/facebookresearch/AdvancedIF"
released: "2025-11"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 77.9
  as_of: "2025-11"
  note: >
    In the paper's own comparison, GPT-5 led at 77.9% averaged across the three subsets (86.9% complex
    single-turn, 73.9% carried-context, 72.8% system-steerability), ahead of Gemini 3 Pro at 74.7% and
    Claude 4 Sonnet at 63.8%; the paper separately characterises frontier models generally as topping out
    "around 70%." System-prompt steerability and multi-turn carried context were both harder than
    single-turn complex instructions for every model in this comparison, well short of a ceiling, which
    is why this page reads the benchmark as open rather than watch or saturated on the evidence
    available. No source read for this page gave a leaderboard figure more recent than the paper's own
    November 2025 release.
contamination:
  risk: medium
  note: >
    AdvancedIF has been fully public on GitHub and Hugging Face since November 2025, under CC BY-NC 4.0
    with no private held-out portion, but only around ten months before this research pass -- less
    exposure time than most benchmarks in this repository. Because grading depends on an LLM judge
    checking a free-text response against a rubric rather than matching one fixed answer, straightforward
    memorisation of a canonical correct response is less directly rewarded than on an answer-keyed
    benchmark, which tempers but does not eliminate the risk from a model having seen the published
    prompts and rubrics during training.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "advancedIF (advancedIF_CIF, advancedIF_CC, advancedIF_SS subset abbreviations, wrapping facebook/AdvancedIF)"
  bigbench: ""
  other: >
    The reference implementation, github.com/facebookresearch/AdvancedIF, provides a CLI
    (`AdvancedIF.cli evaluate`) with three task-type flags matching the three subsets
    (`if_complex_if_oss`, `if_carried_context_oss`, `if_system_steerability_oss`) and defaults to o3-mini
    as the grading judge. OpenCompass wraps the same underlying `facebook/AdvancedIF` Hugging Face
    dataset through a `GenericLLMEvaluator` with a subset-specific judge prompt. Not confirmed in the
    lm-evaluation-harness, HELM, Inspect Evals or BIG-bench task lists.
tags: ["instruction-following", "rubric-based", "llm-judge", "multi-turn", "system-prompt", "expert-written"]
sources:
  - url: "https://arxiv.org/abs/2511.10507"
    title: "AdvancedIF: Rubric-Based Benchmarking and Reinforcement Learning for Advancing LLM Instruction Following"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2511.10507"
    title: "AdvancedIF, full text (ar5iv) -- subset counts, judge validation, frontier-model results"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/facebook/AdvancedIF"
    title: "facebook/AdvancedIF dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/facebook/AdvancedIF"
    title: "facebook/AdvancedIF dataset card API -- licence tag, split size"
    accessed: "2026-09-08"
  - url: "https://github.com/facebookresearch/AdvancedIF"
    title: "facebookresearch/AdvancedIF repository -- CLI, task types, default judge, licence"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/advancedIF/advancedIF_rawprompt_gen.py"
    title: "OpenCompass advancedIF dataset config -- subset definitions and judge templates"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

AdvancedIF targets instruction-following capabilities that mechanically-checked benchmarks such as
`ifeval` and `ifbench` are structurally unable to cover, because their entire design requires constraints
a program can verify. AdvancedIF instead uses expert-written prompts and expert-curated rubrics across
three subsets: complex single-turn instructions, where each prompt layers six or more simultaneous
constraints across tone, format, style, structure, length, negative constraints, spelling and instructions
that depend on each other; multi-turn carried context, testing whether a model keeps honouring an earlier
instruction once a conversation has moved past it; and system-prompt steerability, testing whether a model
follows persona, scope and behavioural rules placed in the system prompt rather than the user turn. Many
of the resulting rubric questions -- did the response stay in character, was the tone appropriately
snarky, did an explanation of prior reasoning actually match what was said earlier -- have no mechanical
check, which is the paper's stated reason for grading with an LLM judge rather than verification code.

## How it is scored

Each prompt carries its own rubric, a checklist of specific yes/no questions written by the same experts
who wrote the prompt. An LLM judge reads the conversation, the model's response and the rubric, answers
every question, and the response counts as a pass only if it satisfies all of them -- an all-or-nothing
standard in the spirit of IFEval's strict, prompt-level accuracy, but applied to constraints a program
cannot check. Because judge quality directly determines how trustworthy a reported score is, the paper
validates several judges against human-labelled agreement: a fine-tuned rubric verifier reached an F1 of
0.728 against human judgments, its recommended general-purpose judge (o3-mini) reached 0.723, and an
unmodified Llama 4 Maverick judge managed only 0.515 -- a reminder that an AdvancedIF score is only as
reliable as the judge that produced it.

## Dataset and licence

1,645 prompts in total, split across the three subsets: 402 complex single-turn prompts, 736 multi-turn
carried-context prompts, and 507 system-prompt steerability prompts, confirmed from the Hugging Face
dataset card's split metadata. The dataset and reference code are released under a CC BY-NC 4.0 licence
(non-commercial use only), published as `facebook/AdvancedIF` on Hugging Face and at
github.com/facebookresearch/AdvancedIF.

## Who publishes it

AdvancedIF comes from a large team at Meta Superintelligence Labs, including Yun He, Wenzhe Li, Hejia
Zhang and more than twenty co-authors, with contributions from Princeton University and Carnegie Mellon
University, posted to arXiv on 2025-11-13. Meta maintains the reference dataset, evaluation CLI and judge
prompts in the linked GitHub repository.

## Lineage

AdvancedIF is not a formal successor of `ifeval` or `ifbench` in this repository's catalogue, but the
paper positions it directly against both: it argues that IFEval-style benchmarks rely on synthetic,
templated prompts and a fixed, narrow set of mechanically verifiable constraints, and offers "pure
expert-written prompts and rubrics for more realistic and aligned evaluation" instead. Where `ifbench`
responded to the same overfitting concern by adding new constraint types that are still mechanically
checkable, AdvancedIF goes further by including constraints -- persona consistency, cross-turn coherence,
system-prompt compliance -- that no verification function can check at all, which is why it requires an
LLM judge rather than extending the checkable-constraint paradigm. The paper also compares its approach
against MultiChallenge, a related multi-turn instruction-following benchmark not yet catalogued in this
repository.

## Saturation and contamination

Not saturated on the evidence available: the paper's own comparison has GPT-5 leading at 77.9% averaged
across the three subsets (86.9% on complex single-turn, but only 73.9% on carried-context and 72.8% on
system-steerability), with Gemini 3 Pro at 74.7% and Claude 4 Sonnet at 63.8%, and the paper separately
describes frontier models generally as topping out "around 70%." System-prompt steerability and
multi-turn carried context were both harder than single-turn complex instructions for every model
compared, well short of a ceiling. Contamination risk is medium: the benchmark has been fully public
since November 2025, under ten months before this research pass, with no private holdout, though
LLM-judge grading against a rubric (rather than a fixed answer string) tempers how directly memorising
the published prompts would help.

## How to run it

The reference CLI in github.com/facebookresearch/AdvancedIF runs one of three task types
(`if_complex_if_oss`, `if_carried_context_oss`, `if_system_steerability_oss`) against a chosen judge
model, defaulting to o3-mini. OpenCompass wraps the same underlying Hugging Face dataset with its own
`GenericLLMEvaluator` and a subset-specific judge prompt template. Because scoring depends entirely on
which judge model graded the responses -- and the paper's own numbers show a roughly 0.2 F1 gap in
human-agreement between a strong and a weak judge -- always check which judge produced a reported
AdvancedIF score before comparing it to another source; scores from different judges are not directly
comparable.

## Reading the numbers

A high AdvancedIF score is stronger evidence of naturalistic instruction-following than a high IFEval or
IFBench score on its own, because its constraints -- persona, cross-turn memory, system-prompt authority
-- are closer to how instructions actually show up in deployed assistants, and because its all-or-nothing
rubric scoring does not give partial credit for a mostly-right response. Because judge choice materially
changes reported numbers, and because the three subsets test distinguishable skills (a model strong on
single-turn complex instructions is not necessarily strong at carrying context across turns or respecting
a system prompt), check the per-subset breakdown and the judge used rather than relying on a single
blended average.
