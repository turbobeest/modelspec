---
id: omni_math
name: "Omni-MATH"
aliases: ["OmniMATH", "Omni-Math"]
page_kind: benchmark
category: math
subcategory: "olympiad mathematics"
status: active
summary: "A 4,428-problem olympiad-level mathematics benchmark built after GSM8K and MATH became easy for frontier models, graded by an LLM judge rather than exact string match."
measures: >
  Omni-MATH gives a model an olympiad-level mathematics competition problem -- drawn from
  international, national and regional competitions such as the IMO, Putnam, USAMO and HMMT -- and
  asks for a full solution and final answer, with no answer choices. Problems are categorised into
  33-plus sub-domains (algebra, number theory, geometry, combinatorics, calculus and more) and
  assigned one of ten difficulty levels, calibrated mainly against the Art of Problem Solving
  community's own difficulty ratings. It targets reasoning clearly beyond grade-school or standard
  competition mathematics: the authors built it specifically because GSM8K and the original MATH
  dataset were, by their account, already being solved with high accuracy by 2024-era models.
task_format: "Free-response: read an olympiad-level mathematics problem, produce a full solution and final answer; graded by comparing the extracted final answer to a reference answer."
metric:
  name: "accuracy (LLM-judged answer equivalence)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No random-guess or human baseline is established; free-response olympiad problems have no
    meaningful chance rate and the paper reports no controlled human trial. At launch (September
    2024), the strongest reported model, OpenAI o1-mini, reached 60.54% overall accuracy, and 48.56%
    restricted to problems above difficulty level 5 of 10.
dataset:
  size: 4428
  size_note: >
    4,428 problems in a single public "test" split (confirmed via the Hugging Face
    datasets-server), each with a domain label, a difficulty rating, the problem statement, a full
    solution and a final answer.
  url: "https://huggingface.co/datasets/KbsdJames/Omni-MATH"
  license: "Apache-2.0"
  languages: ["en"]
  modalities: ["text"]
  splits: "single 'test' split, 4,428 rows; no separate train split is published"
  public_test_set: true
publisher:
  org: "Peking University; Alibaba"
  authors: ["Bofei Gao", "Feifan Song", "Zhe Yang", "Zefan Cai", "Yibo Miao", "Qingxiu Dong", "Lei Li", "Chenghao Ma", "Liang Chen", "Runxin Xu", "Zhengyang Tang", "Benyou Wang", "Daoguang Zan", "Shanghaoran Quan", "Ge Zhang", "Lei Sha", "Yichang Zhang", "Xuancheng Ren", "Tianyu Liu", "Baobao Chang"]
  url: "https://omni-math.github.io/"
paper:
  title: "Omni-MATH: A Universal Olympiad Level Mathematic Benchmark For Large Language Models"
  arxiv: "2410.07985"
  url: "https://arxiv.org/abs/2410.07985"
  year: 2024
leaderboard_url: "https://omni-math.github.io/"
repo_url: "https://github.com/KbsdJames/Omni-MATH"
released: "2024-09"
last_updated: "2024-12"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 60.54
  as_of: "2024-09"
  note: >
    The project's own leaderboard (omni-math.github.io) has not visibly changed since its September
    2024 rows; OpenAI o1-mini leads at 60.54% overall (62.2% under the later rule-based evaluation),
    with o1-preview second at 52.55%, and the next-best model (Qwen2.5-MATH-72B-Instruct) well behind
    at 36.20%. No score for a 2025-2026 frontier model (GPT-5, Claude 4.x, Gemini 2.5+) was found on
    this or any other source during this research, so current standing is not established -- the
    leaderboard being roughly two years stale is itself worth flagging to anyone citing it as current.
contamination:
  risk: medium
  note: >
    Problems are drawn from public competition archives and the AoPS community wiki, some of which
    likely appear individually in pretraining corpora, but the specific 4,428-problem selection,
    domain labels and reference solutions have only been packaged together and downloadable since
    September 2024, limiting exact-set memorization for models trained before that date.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "omni_math"
  opencompass: "omni_math"
  bigbench: ""
  other: >
    Reference grading uses either GPT-4o as an LLM judge (the method behind the official leaderboard)
    or "Omni-Judge", a Llama-3-8B-Instruct model the authors fine-tuned on GPT-4o's judgments (about
    95% agreement with GPT-4o on a held-out internal test set); a separate rule-based evaluator
    covering a subset of the problems was released in December 2024.
tags: ["math", "olympiad", "llm-judge", "free-response", "chain-of-thought"]
sources:
  - url: "https://arxiv.org/abs/2410.07985"
    title: "Omni-MATH: A Universal Olympiad Level Mathematic Benchmark For Large Language Models (Gao et al., 2024)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2410.07985"
    title: "Omni-MATH paper, full text (ar5iv HTML)"
    accessed: "2026-09-08"
  - url: "https://github.com/KbsdJames/Omni-MATH"
    title: "KbsdJames/Omni-MATH GitHub repository (official, README documents grading methods and news)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/KbsdJames/Omni-MATH"
    title: "KbsdJames/Omni-MATH dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://omni-math.github.io/"
    title: "Omni-MATH project page and leaderboard"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/omni_math_scenario.py"
    title: "HELM omni_math_scenario.py"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/omni_math"
    title: "OpenCompass omni_math dataset configs"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 2, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

Omni-MATH gives a model an olympiad-level mathematics problem drawn from international, national and
regional competitions -- the IMO, Putnam, USAMO, HMMT and others -- and asks for a full solution and
final answer, with no answer choices offered. Problems are organised into more than 33 sub-domains
(algebra, number theory, geometry, combinatorics, calculus and more) and assigned one of ten
difficulty levels, calibrated primarily against the Art of Problem Solving community's own difficulty
ratings, with GPT-4o assigning a level to any problem AoPS had not already rated. It is built to
demand genuine olympiad-level reasoning rather than the standard competition mathematics that GSM8K
and the original MATH dataset test, which the authors argue were already solved at high accuracy by
2024-era models -- their own headline example is OpenAI o1 scoring 94.8% on MATH.

## How it is scored

The official protocol extracts a model's final answer and checks it against the reference answer with
GPT-4o as an equivalence judge, following a documented few-shot prompt; because free-form
mathematical answers can be written in more than one equivalent form, exact string matching is not
used. Because GPT-4o judging is expensive at scale, the authors separately released "Omni-Judge," a
Llama-3-8B-Instruct model fine-tuned on 21,451 of their own GPT-4o judgments, which they report
agrees with GPT-4o about 95% of the time on a held-out internal test set of 2,690 examples. A
rule-based evaluator, adapted from Qwen2.5-MATH's grading code and covering a subset of problems
suited to exact-match checking, was released in December 2024 as a third, cheaper option, which the
authors report is "generally consistent" with the GPT-4o-judged leaderboard. Because three different
graders exist, two reported scores are only safely comparable once you confirm they used the same
one.

## Dataset and licence

The Hugging Face dataset (`KbsdJames/Omni-MATH`, Apache-2.0) ships 4,428 problems in a single public
"test" split, each with a domain path, a difficulty rating, the problem statement, a full worked
solution and a final answer; no separate training split is published. Problems without a pre-existing
AoPS solution were converted to LaTeX and difficulty-rated by the authors' own pipeline rather than
sourced verbatim from a single existing corpus, so licensing follows the authors' Apache-2.0 grant on
the packaged dataset rather than a single upstream competition's own terms.

## Who publishes it

Omni-MATH was introduced by Bofei Gao, Feifan Song, Zhe Yang and eighteen coauthors across Peking
University and Alibaba, posted to arXiv in October 2024 and accepted at ICLR 2025. The authors
maintain both the GitHub repository and a project page (omni-math.github.io) that hosts the
leaderboard; HELM and OpenCompass each ship their own scenario/config for the benchmark, pulling
directly from the Hugging Face dataset.

## Lineage

Omni-MATH has no predecessor dataset of its own; it was built as a response to the saturation of
GSM8K and MATH (`math`, also documented in this batch) rather than as a derived subset of either. No
successor benchmark to Omni-MATH specifically was identified during this research, though it sits
alongside other post-2024 olympiad-difficulty math evaluations built for the same reason -- frontier
models outgrowing MATH-500-era benchmarks.

## Saturation and contamination

At launch (September 2024), OpenAI o1-mini led the official leaderboard at 60.54% overall accuracy,
falling to 48.56% restricted to the hardest quarter of problems (difficulty above 5 of 10); o1-preview
followed at 52.55%, with the next tier of open models (Qwen2.5-MATH-72B-Instruct and similar) well
behind at 36.20%. The project's own leaderboard has not visibly changed since those September 2024
entries, so it does not reflect 2025-2026 frontier models, and no later score was found elsewhere
during this research -- current saturation status is not established. Contamination risk is medium:
individual competition problems circulate publicly and may appear piecemeal in pretraining data, but
the specific curated set, with its domain and difficulty labels, has only been packaged and
downloadable since September 2024.

## How to run it

HELM's `omni_math` scenario and OpenCompass's `omni_math` configs both load `KbsdJames/Omni-MATH`
directly and implement their own grading rather than calling the authors' GPT-4o-judge or Omni-Judge
pipelines verbatim, so a score reported from either harness is not guaranteed to match the official
leaderboard's methodology. No lm-evaluation-harness or Inspect Evals task was confirmed for Omni-MATH
during this research. Because grading is LLM-judged rather than exact-match, reported scores depend
on which judge model and prompt produced them; always check whether a number came from the official
GPT-4o-judged leaderboard, the Omni-Judge model, the December 2024 rule-based evaluator, or a
third-party harness's own grader before comparing two Omni-MATH scores.

## Reading the numbers

A high Omni-MATH score is decent evidence a model can solve genuinely hard, olympiad-tier problems
rather than the routine competition mathematics that MATH-500 and GSM8K now saturate on -- at launch,
even the best reasoning models cleared barely 60%, with accuracy nearly halving on the hardest
quarter of problems. Because grading depends on an LLM judge, an unfavourably-phrased correct answer
can be marked wrong and a plausible-looking wrong one can slip through, so a single score is noisier
than a fixed-format multiple-choice one. The benchmark's own leaderboard is roughly two years stale
relative to the frontier, so treat any current-model number as coming from the reporting lab's own
run rather than a verified leaderboard entry, and check which grader produced it.
