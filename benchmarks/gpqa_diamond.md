---
id: gpqa_diamond
name: GPQA Diamond
aliases:
  - GPQA-Diamond
page_kind: benchmark
category: reasoning
subcategory: graduate-level science Q&A
status: active
summary: 198 PhD-written multiple-choice science questions built to resist lookup, the hardest subset of GPQA.
measures: >
  GPQA Diamond tests whether a model can answer graduate-level multiple-choice questions in biology,
  physics and chemistry that are deliberately built to resist internet lookup. Each question was written
  and validated by a PhD-level domain expert, then filtered so that expert annotators agreed on the
  answer while most skilled non-experts, given open web access and significant time, did not. It is a
  single-turn, text-only, English-language task with four answer options and one correct letter, meant
  to reward domain reasoning rather than search skill.
task_format: >
  Four-option multiple-choice question in biology, physics or chemistry; the model returns a single
  letter answer, typically after chain-of-thought reasoning.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: 69.7
  baseline_note: >
    OpenAI recruited PhD-level experts to answer the Diamond subset specifically and measured 69.7%
    accuracy, reported in OpenAI's o1 announcement and cited on Epoch AI's methodology page. The original
    GPQA paper separately reports 65% accuracy (74% excluding self-identified mistakes) for expert
    validators across its broader validation sample, not Diamond alone.
dataset:
  size: 198
  size_note: >
    198 questions: the subset of the 448-question main GPQA set where both expert annotators answered
    correctly and most non-expert validators did not.
  url: https://huggingface.co/datasets/Idavidrein/gpqa
  license: CC BY 4.0
  languages:
    - en
  modalities:
    - text
  splits: single evaluation set, no train/test split
  public_test_set: true
publisher:
  org: ""
  authors:
    - David Rein
    - Betty Li Hou
    - Asa Cooper Stickland
    - Jackson Petty
    - Richard Yuanzhe Pang
    - Julien Dirani
    - Julian Michael
    - Samuel R. Bowman
  url: https://github.com/idavidrein/gpqa
paper:
  title: "GPQA: A Graduate-Level Google-Proof Q&A Benchmark"
  arxiv: "2311.12022"
  url: https://arxiv.org/abs/2311.12022
  year: 2023
leaderboard_url: https://epoch.ai/benchmarks/gpqa-diamond
repo_url: https://github.com/idavidrein/gpqa
released: "2023-11"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: 92.0
  as_of: "2025-12"
  note: >
    OpenAI's own tracking shows the trajectory: GPT-4 scored 39% at the benchmark's November 2023
    release against OpenAI's later-measured 69.7% PhD-expert baseline, o1 reached 77.3% in September
    2024, and GPT-5.2 scored 92% by December 2025 per OpenAI's FrontierScience announcement. Epoch AI
    separately measured Grok 4 at 87% (plus or minus 2%) in July 2025. Scores are now well clear of the
    expert baseline and close to the 100% ceiling.
contamination:
  risk: medium
  note: >
    The dataset ships with a canary string and a no-public-sharing agreement, and the GitHub copy is
    password-gated, specifically to slow contamination. But the questions have circulated, gated, since
    November 2023, and the benchmark is heavily used for both training and evaluation, so some leakage
    over almost three years is plausible despite those measures.
harness:
  lm_eval: gpqa_diamond_zeroshot
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    OpenAI's simple-evals package (github.com/openai/simple-evals, gpqa_eval.py) supplies the zero-shot
    chain-of-thought prompt most labs now use when reporting GPQA Diamond scores.
tags:
  - science
  - multiple-choice
  - phd-level
  - chain-of-thought
sources:
  - url: https://arxiv.org/abs/2311.12022
    title: "GPQA: A Graduate-Level Google-Proof Q&A Benchmark"
    accessed: "2026-09-07"
  - url: https://github.com/idavidrein/gpqa
    title: "idavidrein/gpqa (README, LICENSE, run_baseline.py)"
    accessed: "2026-09-07"
  - url: https://huggingface.co/datasets/Idavidrein/gpqa
    title: "Idavidrein/gpqa dataset card"
    accessed: "2026-09-07"
  - url: https://epoch.ai/benchmarks/gpqa-diamond
    title: "GPQA Diamond | Epoch AI"
    accessed: "2026-09-07"
  - url: https://openai.com/index/frontierscience/
    title: "Evaluating AI's ability to perform scientific research tasks | OpenAI"
    accessed: "2026-09-07"
freshness:
  researched: "2026-09-07"
  researched_by: "sonnet-5 agent, batch 1, slice F"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

GPQA Diamond tests whether a model can answer graduate-level multiple-choice questions in biology,
physics and chemistry that are deliberately built to resist internet lookup. Each question was written
and validated by a PhD-level domain expert, then filtered so that expert annotators agreed on the answer
while most skilled non-experts, given 30-plus minutes and open web access, did not. It is a single-turn,
text-only, English-language task: four answer options, one correct letter.

The "Google-proof" framing is the point. Where many knowledge benchmarks reward retrieval of a fact a
search engine could surface directly, GPQA Diamond is filtered specifically against that failure mode,
so a high score is meant to reflect domain reasoning rather than lookup skill — which is also why this
page treats it as closer to reasoning than to plain recall-style knowledge testing.

## How it is scored

Models are graded on accuracy: the percentage of the 198 questions answered with the correct letter.
Random guessing scores 25% on the four-option format. Most labs now report a zero-shot or few-shot
chain-of-thought variant, prompting the model to reason before committing to an answer; OpenAI's widely
reused simple-evals prompt is the de facto standard, with answers parsed from a final "ANSWER: X" line.
Because parsing is strict, a model that reasons correctly but formats its answer wrong can score below
the random baseline, which Epoch AI has documented happening in its own runs.

## Dataset and licence

GPQA Diamond is the 198-question hardest tier of the 448-question main GPQA set, produced by recruiting
subject-matter experts (people with or pursuing PhDs) to write questions, then having both other experts
and skilled non-expert validators attempt each one; Diamond keeps only the questions where both experts
succeeded and most non-experts failed. The dataset is released under CC BY 4.0 on Hugging Face.
Distribution is deliberately gated: the GitHub copy is password-protected, and downloaders agree not to
publicly post questions, specifically to slow the benchmark's entry into future training data. English
only, text only.

## Who publishes it

GPQA was introduced by David Rein, Betty Li Hou, Asa Cooper Stickland, Jackson Petty, Richard Yuanzhe
Pang, Julien Dirani, Julian Michael and Samuel R. Bowman, posted to arXiv in November 2023. The authors
maintain the reference dataset and code at github.com/idavidrein/gpqa. Independent trackers, notably
Epoch AI, run and publish their own GPQA Diamond evaluations of new frontier models as a standing
benchmark on their site.

## Lineage

GPQA names no formal predecessor and has no official successor within its own line, but its rapid
saturation is one of the stated reasons newer, harder science and reasoning benchmarks exist: OpenAI's
FrontierScience and Scale AI/CAIS's Humanity's Last Exam were both framed partly as responses to GPQA and
MMLU losing their power to separate frontier models. Neither has a page in this repository yet. GPQA
Diamond is one of three official subsets of the original GPQA release, alongside the full "main" set and
a broader "extended" set; only Diamond is treated as a standalone page here.

## Saturation and contamination

GPQA Diamond has moved from a genuinely hard benchmark to a largely saturated one within two years. GPT-4
scored 39% at the November 2023 release, against OpenAI's own later-measured PhD-expert baseline of
69.7%. OpenAI's o1 reached 77.3% in September 2024, already above that expert baseline. Epoch AI measured
Grok 4 at 87% in July 2025, and OpenAI reported GPT-5.2 at 92% in its December 2025 FrontierScience
announcement. That trajectory leaves little headroom before the 100% ceiling. Contamination risk sits at
medium: the dataset uses a canary string and gated, agreement-bound distribution specifically to resist
leakage, but the questions have circulated for almost three years among a research community that both
trains on and evaluates against them.

## How to run it

The authors' own repository ships `run_baseline.py` with zero-shot and chain-of-thought prompting
options. EleutherAI's lm-evaluation-harness defines a family of task names per subset and shot count,
including `gpqa_diamond_zeroshot` and `gpqa_diamond_cot_zeroshot`, plus few-shot and generative variants.
OpenAI's simple-evals package (`gpqa_eval.py`) supplies the specific zero-shot chain-of-thought prompt
most frontier-model announcements now use, which makes it the closest thing to a comparability standard
even though it is not lm-evaluation-harness's own default. Because chain-of-thought budget, answer-parsing
strictness and prompt wording all vary between these implementations, scores from different sources are
not perfectly comparable.

## Reading the numbers

A high GPQA Diamond score today mostly confirms a model has strong graduate-level scientific recall and
multi-step reasoning within a closed four-option format, not that it can do open-ended scientific work.
Because the benchmark now sits close to its ceiling, small differences between frontier models are within
noise, and it no longer separates the best systems the way it did in 2023 and 2024. Read a GPQA Diamond
number alongside a still-unsaturated benchmark, such as Humanity's Last Exam or a research-style track
like FrontierScience-Research, to judge whether a model's scientific reasoning still has headroom, and
treat scores from different harnesses or prompt formats as roughly comparable at best.
