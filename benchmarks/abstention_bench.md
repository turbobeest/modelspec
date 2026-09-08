---
id: abstention_bench
name: "AbstentionBench"
aliases: []
page_kind: benchmark
category: safety
subcategory: "epistemic calibration -- abstaining on unanswerable, underspecified or false-premise questions"
status: active
summary: "A FAIR/Meta benchmark of 20 aggregated datasets testing whether models decline to answer questions that cannot or should not be answered confidently, finding reasoning fine-tuning makes this worse."
measures: >
  AbstentionBench tests whether a model recognises when it should decline to give a confident, direct
  answer, rather than whether it can answer correctly. It aggregates questions across six scenarios where
  abstention (or at least hedging) is the appropriate response: the answer is genuinely unknown or
  undocumented, the question rests on a false premise, the question concerns events after the relevant
  knowledge cutoff (stale), the question is inherently subjective, the question's context is
  underspecified, or the user's intent behind the question is underspecified. Most of its 20 source
  datasets are existing benchmarks repurposed or filtered for these properties; three (GPQA-Abstain,
  GSM8K-Abstain, MMLU-Math-Abstain) are new variants the authors built by editing established math and
  science benchmarks to remove information needed to answer confidently. The paper's headline finding is
  that abstention remains an unsolved problem even for frontier models, that model scale barely helps, and
  that reasoning-focused fine-tuning specifically makes it worse.
task_format: >
  Free-text question answering: a model reads a question drawn from one of the 20 source datasets or
  scenario variants and produces an open-ended response. Rather than checking the response against a
  fixed answer key, an LLM judge (Llama 3.1 8B Instruct, by default) classifies whether the response
  abstained or attempted a direct answer; for items that are answerable, a separate correctness check is
  also applied to the non-abstaining responses.
metric:
  name: "abstention recall (share of should-abstain items where the model abstained), plus precision, F1, and response accuracy on answerable items"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The paper reports abstention recall as its primary number but pairs it with precision and F1
    specifically to catch over-abstention -- a model that refuses everything would score perfectly on
    recall alone, the same failure mode XSTest is built to catch in the opposite (safety-refusal)
    direction. Response accuracy on the answerable, non-abstention items is tracked separately, so a
    model's behaviour is only fully characterised by looking at all of these together rather than
    recall in isolation. No random or majority-class baseline was stated in the sources read for this
    page, and no controlled human abstention-rate baseline is published (human annotation was used only
    to validate the LLM judge itself, not to set a target abstention rate).
dataset:
  size: null
  size_note: >
    The paper states the aggregate size only as "over 35k" questions, without giving one precise total
    figure, so size is left unset here rather than rounded. It draws on 20 source datasets across the
    six abstention scenarios, most repurposed or filtered from existing published benchmarks (among
    them BBQ, FreshQA, SQuAD 2.0, MuSiQue, QASPER, CoCoNot, MoralChoice, WorldSense and UMWP) and three
    newly constructed by the authors (GPQA-Abstain, GSM8K-Abstain, MMLU-Math-Abstain, built by editing
    GPQA, GSM8K and MMLU items to remove information needed for a confident answer); some source
    datasets are capped at a maximum sample count during aggregation rather than used in full.
  url: "https://huggingface.co/datasets/facebook/AbstentionBench"
  license: "CC BY-NC 4.0"
  languages: ["en"]
  modalities: ["text"]
  splits: "aggregated from 20 source datasets; no single unified train/test split of its own"
  public_test_set: true
publisher:
  org: "FAIR at Meta"
  authors: ["Polina Kirichenko", "Mark Ibrahim", "Kamalika Chaudhuri", "Samuel J. Bell"]
  url: "https://github.com/facebookresearch/AbstentionBench"
paper:
  title: "AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions"
  arxiv: "2506.09038"
  url: "https://arxiv.org/abs/2506.09038"
  year: 2025
leaderboard_url: ""
repo_url: "https://github.com/facebookresearch/AbstentionBench"
released: "2025-06"
last_updated: "2025-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    No exact leaderboard figures were found in the sources read for this page, but the paper's own
    framing is explicit that this is not a solved or saturated benchmark: it reports that "abstention
    remains a key problem even for frontier LLMs, with model scale having almost no effect," and singles
    out GPT-4o and Qwen 2.5 32B as ranking highest among the roughly 20 models it tested, without stating
    their exact scores in the sources read. It further finds that reasoning-focused fine-tuning
    (comparing models such as DeepSeek R1 and s1.1 against non-reasoning counterparts) produces an
    average 24% drop in abstention rate. That combination -- no model near a ceiling, and training
    choices measurably moving scores in both directions -- points to an open, actively separating
    benchmark rather than a saturated or merely-watch one.
contamination:
  risk: medium
  note: >
    Many of the 20 underlying source datasets (SQuAD 2.0, GSM8K, MMLU and similar) are themselves older
    and widely present in pretraining data in their original form, but AbstentionBench's specific
    contribution -- which items count as should-abstain, and the three new GPQA/GSM8K/MMLU abstention
    variants -- has been public on GitHub and Hugging Face since mid-to-late 2025, only around a year
    before this research pass, with no private held-out portion. Because grading depends on an LLM
    judge assessing whether a free-text response abstained, rather than matching a fixed answer string,
    memorising a specific correct response is less directly rewarded than on an answer-keyed benchmark,
    which tempers but does not eliminate the risk.
harness:
  lm_eval: ""
  inspect_evals: "abstention_bench"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Reference implementation and the CC BY-NC 4.0-licensed data pipeline are at
    github.com/facebookresearch/AbstentionBench, with the aggregated data also published as
    facebook/AbstentionBench on Hugging Face. inspect_evals implements it as `abstention_bench`, but
    ships it with its own isolated dependency environment (under `packages/abstention_bench/`) because
    its requirements conflict with other evals in that repository.
tags: ["safety", "abstention", "calibration", "unanswerable-questions", "hallucination", "reasoning-models", "llm-judge"]
sources:
  - url: "https://arxiv.org/abs/2506.09038"
    title: "AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions (Kirichenko, Ibrahim, Chaudhuri, Bell, 2025)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2506.09038"
    title: "AbstentionBench, full text (ar5iv) -- scenario definitions, dataset list, judge validation, results"
    accessed: "2026-09-08"
  - url: "https://github.com/facebookresearch/AbstentionBench"
    title: "facebookresearch/AbstentionBench repository -- overview, licence, Hugging Face pointer"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/facebook/AbstentionBench"
    title: "facebook/AbstentionBench dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/facebook/AbstentionBench"
    title: "facebook/AbstentionBench dataset card API (licence tag, language)"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/abstention_bench"
    title: "inspect_evals abstention_bench task README"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

AbstentionBench asks a different question from most benchmarks: not whether a model can answer
correctly, but whether it recognises when it should not attempt a confident answer at all. It aggregates
questions across six scenarios chosen to make abstention the appropriate response -- the true answer is
unknown or undocumented, the question rests on a false premise, it concerns events past the model's
knowledge cutoff (stale), it is inherently subjective, its context is underspecified, or the user's
underlying intent is underspecified. Most of its 20 source datasets are existing benchmarks (among them
BBQ, FreshQA, SQuAD 2.0, MuSiQue, QASPER, CoCoNot, MoralChoice, WorldSense and UMWP) repurposed or
filtered for one of these properties; three -- GPQA-Abstain, GSM8K-Abstain and MMLU-Math-Abstain -- are
new variants the authors built by editing established math and science benchmark items to strip out
information a confident answer would require. The paper's central finding is that abstention is still
unsolved even in frontier models, scaling barely helps, and reasoning-focused fine-tuning specifically
makes models more confidently wrong rather than appropriately cautious.

## How it is scored

Because responses are free text rather than multiple choice, scoring uses an LLM judge -- Llama 3.1 8B
Instruct by default -- to classify each response as abstaining or attempting a direct answer; the authors
validated this judge against 300 manually annotated response pairs (from GPT-4o and Llama 3.1 70B
outputs) and report 88% agreement with the human labels. The primary number is abstention recall: the
share of should-abstain items where the model actually abstained. Because recall alone cannot distinguish
genuine calibration from a model that simply refuses everything, the paper also reports precision and F1
to penalise over-abstention, plus a separate accuracy check on the answerable subset, so behaviour is
characterised by the full set of numbers rather than any one alone.

## Dataset and licence

The paper describes the aggregate size only as "over 35k" questions without one exact total. It spans 20
source datasets across the six scenarios: most are existing published benchmarks repurposed or filtered
for abstention-relevant properties, and three (GPQA-Abstain, GSM8K-Abstain, MMLU-Math-Abstain) are new
constructions built by editing GPQA, GSM8K and MMLU items. The aggregated dataset and pipeline are
released under a CC BY-NC 4.0 licence (non-commercial, unlike most benchmarks in this repository) and
published on GitHub and as `facebook/AbstentionBench` on Hugging Face; some source datasets are capped at
a maximum sample count during aggregation rather than included in full.

## Who publishes it

AbstentionBench comes from Polina Kirichenko, Mark Ibrahim, Kamalika Chaudhuri and Samuel J. Bell at FAIR,
Meta's AI research group, posted to arXiv on 2025-06-10. The team maintains the reference implementation
and data pipeline at github.com/facebookresearch/AbstentionBench, and published the aggregated dataset to
Hugging Face in mid-2025.

## Lineage

AbstentionBench does not extend a single predecessor; it aggregates roughly 20 existing datasets (several
built for adjacent purposes, such as CoCoNot's contextual non-compliance work and FreshQA's stale-answer
questions) into one holistic evaluation, plus three newly constructed abstention variants of GPQA, GSM8K
and MMLU. It is not catalogued as part of a family here and has no confirmed successor. It probes a
related but distinct failure mode from over-refusal benchmarks such as `xstest`: XSTest checks whether a
model wrongly refuses a genuinely safe request, while AbstentionBench checks whether a model wrongly
answers a request it should have declined -- opposite directions of the same calibration question.

## Saturation and contamination

No exact top-model scores were found in the sources read for this page, but the paper's own framing rules
out a saturated reading: it states plainly that "abstention remains a key problem even for frontier LLMs,
with model scale having almost no effect," naming GPT-4o and Qwen 2.5 32B as strongest of roughly 20
models tested. It further reports reasoning-focused fine-tuning drives an average 24% drop in abstention
rate versus non-reasoning counterparts -- evidence training choices move scores substantially in both
directions rather than clustering near a ceiling, consistent with an open, still-separating benchmark.
Contamination risk is medium: several source datasets are old and widely known, but AbstentionBench's own
labels and its three new variants have been public for only around a year, with no private holdout,
tempered by LLM-judge grading that does not directly reward memorising one fixed string.

## How to run it

inspect_evals implements the benchmark as `abstention_bench`, but ships it with its own isolated
dependency environment under `packages/abstention_bench/`, because its requirements conflict with the
rest of that repository -- installing it needs a separate `uv sync` from that subdirectory rather than
the shared inspect_evals environment. The authors' own pipeline, including the reference LLM judge, is at
github.com/facebookresearch/AbstentionBench, with pre-computed results explorable from a CSV in that
repository without rerunning models. No lm-evaluation-harness, HELM, OpenCompass or BIG-bench
implementation was confirmed. Because scoring depends on an LLM judge, reported numbers shift with the
judge model and its prompt; check which judge produced a given figure before comparing sources.

## Reading the numbers

A high abstention recall is only meaningful alongside precision and response accuracy on answerable
items -- alone, it cannot distinguish a well-calibrated model from one that simply hedges on everything,
the mirror image of the problem XSTest is built to catch for over-refusal. The finding that
reasoning-focused fine-tuning measurably reduces abstention is worth checking for any reasoning-tuned
model: a strong math or reasoning score does not imply the model knows when to say it does not know.
Treat AbstentionBench as a check on epistemic calibration across six scenario types, not a general
hallucination score, and note its non-commercial (CC BY-NC 4.0) licence if reuse terms matter.
