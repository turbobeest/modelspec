---
id: mgsm
name: "MGSM (Multilingual Grade School Math)"
aliases: ["Multilingual Grade School Math Benchmark", "Multilingual GSM8K"]
page_kind: benchmark
category: math
subcategory: "multilingual math reasoning"
status: active
summary: "The same 250 GSM8K grade-school math problems, human-translated into ten languages, to test whether chain-of-thought reasoning holds up outside English."
measures: >
  MGSM gives a model the same 250 grade-school arithmetic word problems used in GSM8K, each
  professionally translated by human annotators into ten languages (Spanish, French, German,
  Russian, Chinese, Japanese, Thai, Swahili, Bengali, Telugu), alongside the English originals. The
  model reads one problem in one language and produces a final numeric answer, typically after a
  worked chain-of-thought solution. The paper frames this as a test of multilingual chain-of-thought
  reasoning, not of translation quality: the translation is fixed and given to the model, and what
  is scored is whether multi-step arithmetic reasoning still works once the problem is not in
  English.
task_format: "Free-response grade-school word problem in one of eleven languages; the model outputs a final answer as an Arabic numeral, usually after a chain-of-thought solution."
metric:
  name: "accuracy (exact match on final numeric answer)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: "The source paper reports no human baseline for MGSM. Scores are usually reported per language and then averaged; direct vs chain-of-thought and native vs English exemplar prompting change results substantially, so protocol must match before comparing two numbers."
dataset:
  size: 250
  size_note: "250 source problems, each translated into 10 languages; the repository ships 11 files of 250 rows each (10 translations plus the original English GSM8K subset)."
  url: "https://github.com/google-research/url-nlp/tree/main/mgsm"
  license: "CC-BY-4.0"
  languages: ["en", "es", "fr", "de", "ru", "zh", "ja", "th", "sw", "bn", "te"]
  modalities: ["text"]
  splits: "no train/test split; 250 evaluation problems per language, with separately translated few-shot exemplars in exemplars.py"
  public_test_set: true
publisher:
  org: "Google Research"
  authors: ["Freda Shi", "Mirac Suzgun", "Markus Freitag", "Xuezhi Wang", "Suraj Srivats", "Soroush Vosoughi", "Hyung Won Chung", "Yi Tay", "Sebastian Ruder", "Denny Zhou", "Dipanjan Das", "Jason Wei"]
  url: "https://github.com/google-research/url-nlp"
paper:
  title: "Language Models are Multilingual Chain-of-Thought Reasoners"
  arxiv: "2210.03057"
  url: "https://arxiv.org/abs/2210.03057"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/google-research/url-nlp/tree/main/mgsm"
released: "2022-10"
last_updated: ""
lineage:
  family: ""
  predecessor: "gsm8k"
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 92.3
  as_of: "2026-09"
  note: "Aggregator llm-stats.com lists Llama 4 Maverick at 92.3%, o3-mini at 92.0% and Claude 3.5 Sonnet at 91.6% across 31 tracked models, with a field average of 77.9%. The top of the field has compressed into a narrow band even though scores overall still spread widely, which is why this is watch rather than fully open or fully saturated."
contamination:
  risk: high
  note: "Problems and answers are public in plain-text TSV files and have been on GitHub since October 2022. The underlying GSM8K English problems have been public since 2021 and are widely believed to appear in pretraining corpora; translated or paraphrased copies of those same problems are a plausible route for the same contamination to reach non-English training data."
harness:
  lm_eval: "mgsm_direct, mgsm_cot_native (per-language variants, e.g. mgsm_direct_en, mgsm_cot_native_de)"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags: ["math", "multilingual", "chain-of-thought", "grade-school-math"]
sources:
  - url: "https://arxiv.org/abs/2210.03057"
    title: "Language Models are Multilingual Chain-of-Thought Reasoners (Shi et al., 2022)"
    accessed: "2026-09-07"
  - url: "https://ar5iv.labs.arxiv.org/html/2210.03057"
    title: "Language Models are Multilingual Chain-of-Thought Reasoners (ar5iv HTML rendering)"
    accessed: "2026-09-07"
  - url: "https://github.com/google-research/url-nlp/tree/main/mgsm"
    title: "google-research/url-nlp, mgsm directory (data, exemplars, licence, README)"
    accessed: "2026-09-07"
  - url: "https://arxiv.org/abs/2110.14168"
    title: "Training Verifiers to Solve Math Word Problems (Cobbe et al., 2021) - introduces GSM8K"
    accessed: "2026-09-07"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/mgsm/README.md"
    title: "lm-evaluation-harness mgsm task README (task group names)"
    accessed: "2026-09-07"
  - url: "https://llm-stats.com/benchmarks/mgsm"
    title: "MGSM Leaderboard | llm-stats.com"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice G"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MGSM gives a model the same 250 grade-school arithmetic word problems used in GSM8K, each
professionally translated by human annotators into ten typologically diverse languages: Spanish,
French, German, Russian, Chinese, Japanese, Thai, Swahili, Bengali and Telugu. The English originals
ship alongside the translations, so the repository holds eleven 250-row files in total. A model
reads one problem in one language and must produce a final numeric answer, usually via a worked
chain-of-thought solution. The paper frames this explicitly as a test of multilingual chain-of-thought
reasoning, not of translation quality: the translation itself is fixed and handed to the model, and
what is scored is whether multi-step arithmetic reasoning still works once the problem text is no
longer in English.

## How it is scored

The lm-evaluation-harness implementation exposes two protocols. `mgsm_direct` asks the model to
answer without showing its work. `mgsm_cot_native` gives few-shot exemplars with worked solutions in
the same language as the question and asks the model to reason before answering. The source paper
mainly used six-shot native-language exemplars (fewer for some languages where GPT-3's context limit
forced truncation) and scored the fraction of problems where the model's final answer, written as an
Arabic numeral, exactly matches the reference. Scores are typically reported per language and then
averaged across the ten (or eleven, including English) languages. Because direct-vs-chain-of-thought
and native-vs-English exemplar prompting change scores substantially, two reported MGSM numbers are
only comparable once both state which protocol produced them. No human baseline is reported in the
source paper.

## Dataset and licence

MGSM does not introduce new problems: all 250 are GSM8K word problems (Cobbe et al., 2021),
translated by human annotators rather than machine translation. There is no train/test split in the
usual sense; all 250 problems per language are used for evaluation, and a separate small set of
few-shot exemplars, also manually translated per language, ships in `exemplars.py`. The data is
plain-text TSV (problem, answer) and is licensed CC-BY-4.0, per the LICENSE file in the `mgsm`
directory of the repository. Reference answers are public in the same files used for evaluation, so
there is no held-out grading server.

## Who publishes it

MGSM was introduced by Freda Shi, Mirac Suzgun, Markus Freitag, Xuezhi Wang, Suraj Srivats, Soroush
Vosoughi, Hyung Won Chung, Yi Tay, Sebastian Ruder, Denny Zhou, Dipanjan Das and Jason Wei, a team
spanning Google Research, Google Brain and academic co-authors, in "Language Models are Multilingual
Chain-of-Thought Reasoners" (arXiv 2210.03057, posted October 2022). No formal conference publication
was confirmed for this page; the paper is tracked here as an arXiv preprint. The dataset and
evaluation code are maintained in Google Research's `url-nlp` GitHub repository, which also hosts
several unrelated under-resourced-language datasets. No dedicated MGSM leaderboard site was found;
aggregators such as llm-stats.com track scores that vendors report in their own model releases.

## Lineage

MGSM translates the 250-problem evaluation set built from GSM8K (Cobbe et al., 2021; `gsm8k` in this
repository) into ten additional languages. It has no announced successor and the repository lists no
further language variants beyond the original ten plus English. It sits alongside, rather than
supersedes, English-only GSM8K: models are commonly reported on both.

## Saturation and contamination

MGSM shows the signature of a benchmark under pressure at the top without being fully saturated.
Aggregator llm-stats.com (accessed September 2026) lists Llama 4 Maverick at 92.3%, o3-mini at 92.0%
and Claude 3.5 Sonnet at 91.6% as the top three of 31 tracked models, a gap of well under a point
between the leaders, while the field average sits at 77.9%. That combination — a compressed top end
over a still-wide overall spread — is why this page marks it "watch" rather than "open" or fully
"saturated." Contamination risk is high: both the problems and their answers are public in plain text
and have been since October 2022, and the underlying GSM8K English problems have circulated since
2021 and are widely believed to be present in pretraining corpora; translated or paraphrased versions
of the same problems are a plausible path for that contamination to reach non-English training data
as well.

## How to run it

lm-evaluation-harness implements MGSM as the task groups `mgsm_direct` and `mgsm_cot_native`, each
with one task per language (for example `mgsm_direct_en`, `mgsm_cot_native_de`). The reference data
and few-shot exemplars live in Google Research's `url-nlp` repository under `mgsm/`. Because the
harness supports both a no-reasoning and a native-language chain-of-thought protocol, and vendors
sometimes report an English-chain-of-thought variant instead, check which protocol and which subset
of languages (all eleven, or just the ten translations) a reported average covers before treating two
MGSM scores as comparable.

## Reading the numbers

A strong MGSM average means a model's arithmetic word-problem reasoning survives translation into
typologically distant languages, including lower-resource ones like Swahili and Bengali; a weak one
usually reflects English-centric training rather than an inability to do the arithmetic itself. The
overall average can hide large per-language gaps, so check the per-language breakdown, not just the
mean, before concluding a model is multilingual-capable. Given the high contamination risk and the
compressed spread at the top of the field, treat small differences between frontier models' MGSM
averages as noise, and weight it alongside a genuinely held-out or recent multilingual reasoning
benchmark where one is available.
