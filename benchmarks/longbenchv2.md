---
id: longbenchv2
name: "LongBench v2"
aliases: ["LongBench v2: Towards Deeper Understanding and Reasoning on Realistic Long-context Multitasks"]
page_kind: benchmark
category: long-context
subcategory: "multiple-choice long-context deep understanding and reasoning (8k-2M words)"
status: active
summary: "503 hard multiple-choice questions with contexts from 8k to 2M words, built so a model must reason over long context rather than just retrieve, with human experts scoring only 53.7%."
measures: >
  LongBench v2 gives a model a long context (8,000 to 2,000,000 words, mostly under 128K) and a
  four-option multiple-choice question that cannot be answered by simple retrieval. The 503 questions
  span six task categories: single-document QA, multi-document QA, long in-context learning,
  long-dialogue history understanding, code repository understanding, and long structured-data
  (table/graph) understanding. Questions were collected from nearly 100 highly educated contributors
  across diverse professional backgrounds, then filtered through automated and manual review for
  quality and genuine difficulty. The explicit design goal is to require deep understanding and
  multi-step reasoning over the full context rather than locating one planted fact, in contrast to
  needle-in-a-haystack-style long-context tests.
task_format: >
  A long document, document set, dialogue history, code repository, or structured dataset plus a
  four-option multiple-choice question in; a single selected option (A-D) out. All questions carry
  a difficulty label (easy/hard) and a length bucket (short/medium/long), and the reference protocol
  reports both direct answering and answering with extended chain-of-thought reasoning.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: 53.7
  baseline_note: >
    25% is the four-option random-guess rate. The paper's own human baseline comes from expert
    annotators answering under a 15-minute time limit with search tools available inside the
    document, scoring 53.7% overall -- itself evidence the benchmark resists simple retrieval, since
    unlimited search time did not let experts approach a high score.
dataset:
  size: 503
  size_note: >
    503 multiple-choice questions, each with its own context (contexts are not shared across
    questions). Hugging Face lists a single unsplit collection (`train` in the loader API, used
    entirely as the evaluation set); there is no separate train/test division. Context length ranges
    from 8k to 2M words, with the majority under 128K.
  url: "https://huggingface.co/datasets/zai-org/LongBench-v2"
  license: "Apache-2.0 (per the Hugging Face dataset card)"
  languages: ["en"]
  modalities: ["text", "code"]
  splits: "single evaluation set of 503 questions; no train/validation split"
  public_test_set: true
publisher:
  org: "Tsinghua University and Zhipu.AI"
  authors: ["Yushi Bai", "Shangqing Tu", "Jiajie Zhang", "Hao Peng", "Xiaozhi Wang", "Xin Lv", "Shulin Cao", "Jiazheng Xu", "Lei Hou", "Yuxiao Dong", "Jie Tang", "Juanzi Li"]
  url: "https://github.com/THUDM/LongBench"
paper:
  title: "LongBench v2: Towards Deeper Understanding and Reasoning on Realistic Long-context Multitasks"
  arxiv: "2412.15204"
  url: "https://arxiv.org/abs/2412.15204"
  year: 2024
leaderboard_url: "https://longbench2.github.io/#leaderboard"
repo_url: "https://github.com/THUDM/LongBench"
released: "2024-12"
last_updated: "2026-01"
lineage:
  family: ""
  predecessor: "longbench"
  successors: []
  variants: []
saturation:
  status: open
  top_score: 57.7
  as_of: "2024-12"
  note: >
    At release, a model answering directly reached only 50.1% accuracy at best, below the 53.7% human
    expert baseline; o1-preview, using extended reasoning, reached 57.7%, the first tested model to
    exceed the human baseline, by about 4 points. The project's own leaderboard page (updated as of a
    2026-01-15 changelog entry naming Gemini-Exp-1206, Gemini-2.0-Flash, DeepSeek-V3 and MiniMax-Text-01
    as later additions) is described by the authors as "updating"; this page could not confirm a
    current top score beyond that changelog note, since the leaderboard site requires JavaScript
    rendering this research pass did not fully capture. Given the wide gap between direct-answer and
    reasoning-augmented scores at release, this benchmark is marked "open" rather than "watch" or
    "saturated" -- it was built specifically to separate models on reasoning, and the evidence
    available here shows it still doing so.
contamination:
  risk: low
  note: >
    All 503 questions and their contexts were newly collected from nearly 100 contributors
    specifically for this benchmark and first published in December 2024, so verbatim memorization
    from pretraining corpora predating the release is unlikely for early-2020s-trained models, though
    the dataset and its answer key are fully public, so risk grows for any model trained after
    December 2024 on web-scale crawls that could include it.
harness:
  lm_eval: "longbench2 (tag; groups longbench2_single, longbench2_multi, longbench2_incontext, longbench2_history, longbench2_structured; task names such as longbench2_govt_single, longbench2_code, longbench2_table)"
  inspect_evals: ""
  helm: ""
  opencompass: "longbenchv2 (opencompass/configs/datasets/longbenchv2, gen-style config)"
  bigbench: ""
  other: "The authors' own repository (THUDM/LongBench) provides reference evaluation scripts (pred.py, result.py) that deploy the model under test with vLLM and support a --cot flag for chain-of-thought and a --rag N flag for retrieval-augmented baselines."
tags: ["long-context", "reasoning", "multiple-choice", "multitask", "code", "structured-data"]
sources:
  - url: "https://arxiv.org/abs/2412.15204"
    title: "LongBench v2: Towards Deeper Understanding and Reasoning on Realistic Long-context Multitasks (Bai et al., arXiv:2412.15204)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2412.15204"
    title: "LongBench v2, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/THUDM/LongBench"
    title: "THUDM/LongBench GitHub repository (LongBench v2 README, evaluation instructions, changelog)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/zai-org/LongBench-v2"
    title: "zai-org/LongBench-v2 dataset card, Hugging Face (formerly THUDM/LongBench-v2; Apache-2.0)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/longbench2/README.md"
    title: "lm-evaluation-harness longbench2 task README (groups, tasks; the harness directory is named longbench2, not longbenchv2)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/longbenchv2"
    title: "OpenCompass longbenchv2 dataset configs"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

LongBench v2 gives a model a long context -- anywhere from 8,000 to 2,000,000 words, mostly under
128K -- and a four-option multiple-choice question built specifically so it cannot be answered by
simple retrieval of one fact. Its 503 questions span six task categories: single-document QA,
multi-document QA, long in-context learning, long-dialogue history understanding, code repository
understanding, and long structured-data understanding over tables and graphs. Questions were
collected from nearly 100 highly educated contributors with diverse professional backgrounds, then
filtered through both automated checks and manual review for quality and genuine difficulty. The
explicit design goal, stated by the same author group that built the original LongBench, is to
require deep understanding and multi-step reasoning across the full context rather than locating one
planted fact, in contrast to needle-in-a-haystack-style probes.

## How it is scored

Accuracy against a 25% four-option random-guess floor. The paper's own human baseline comes from
expert annotators answering under a 15-minute time limit with search tools available inside the
document, who reached only 53.7% overall -- itself evidence the benchmark resists brute-force search,
since unlimited lookup time did not let experts approach a high score. Every question carries a
difficulty label (easy/hard) and a length bucket (short/medium/long), letting results be broken down
along both axes. The reference protocol reports both a direct-answer setting and a setting that
allows extended chain-of-thought reasoning before the model commits to an option; the gap between the
two is itself part of what the benchmark is designed to surface.

## Dataset and licence

503 multiple-choice questions, each paired with its own context; contexts are not reused across
questions. The Hugging Face dataset card (zai-org/LongBench-v2, Apache-2.0) lists a single unsplit
collection used entirely as the evaluation set -- there is no separate train/test division, and all
503 answers are public. Context length ranges from 8k to 2M words, with the majority under 128K,
covering domains such as government and legal documents, academic papers, financial filings, news,
detective stories, agent and dialogue transcripts, user guides, and code repositories.

## Who publishes it

Yushi Bai, Shangqing Tu, Jiajie Zhang, Hao Peng, Xiaozhi Wang, Xin Lv, Shulin Cao, Jiazheng Xu, Lei
Hou, Yuxiao Dong, Jie Tang and Juanzi Li, at Tsinghua University and Zhipu.AI, published LongBench v2
in December 2024 -- largely the same team that built the original LongBench two years earlier. The
authors host both benchmark generations in the same GitHub repository (THUDM/LongBench) and maintain
a dedicated project site and leaderboard at longbench2.github.io, described by the authors as
"updating."

## Lineage

LongBench v2's predecessor is `longbench` (August 2023), built by an overlapping author team. Where
the original LongBench used mostly extractive QA, summarization and classification tasks over
5k-15k-word contexts, LongBench v2 moves to a uniform multiple-choice format, extends context length
up to 2M words, and adds task categories (long in-context learning, dialogue-history understanding,
structured-data understanding) chosen specifically to demand reasoning that a single retrieval pass
cannot satisfy. No further successor to LongBench v2 was identified in this research. Separately, this
repository catalogues two unrelated long-context suites built around a similar "beyond retrieval"
goal -- `infinitebench` and `ruler` -- neither of which shares data or authorship with the LongBench
family.

## Saturation and contamination

At release, the best model answering directly reached only 50.1% accuracy, below the 53.7% human
expert baseline; o1-preview, using extended reasoning, reached 57.7% -- the first tested model to
exceed the human baseline, by roughly 4 points, and the paper's headline result. The project's own
leaderboard names later additions in a changelog (Gemini-Exp-1206, Gemini-2.0-Flash, DeepSeek-V3,
MiniMax-Text-01, dated 2026-01-15) but is described by the authors as still "updating," and this
research could not confirm a current top score beyond that changelog note because the leaderboard
page requires JavaScript rendering not fully captured here. Given the wide direct-answer-versus-
reasoning gap at release and no evidence the benchmark has since collapsed toward the ceiling, it is
marked "open." Contamination risk is low: every question and context was newly collected for this
December 2024 release, making verbatim memorization unlikely for models trained on data predating
that date, though risk rises for any model trained afterward on web-scale crawls that could include
the now-public dataset.

## How to run it

lm-evaluation-harness implements the benchmark under a `longbench2` directory and tag -- not
`longbenchv2`, despite that being the name used in some third-party references -- with groups
`longbench2_single`, `longbench2_multi`, `longbench2_incontext`, `longbench2_history` and
`longbench2_structured`, and per-domain tasks such as `longbench2_govt_single` and `longbench2_code`.
OpenCompass instead registers it under the name `longbenchv2`, with a `longbenchv2_gen` config. The
authors' own repository provides the reference scripts (`pred.py`, `result.py`), which deploy the
model under test through vLLM and support a `--cot` flag for chain-of-thought and a `--rag N` flag
for a retrieval-augmented baseline comparison. Because harness names differ (`longbench2` versus
`longbenchv2`) and direct-answer versus CoT settings are not always distinguished in reported scores,
check which protocol and which harness produced a given number before comparing across sources.

## Reading the numbers

A high LongBench v2 score is comparatively strong evidence a model can reason over a long, realistic
context rather than merely retrieve a fact from it, since the benchmark was built and filtered
specifically to resist retrieval shortcuts and since even time-unlimited-lookup human experts topped
out around 54%. A score that improves substantially under chain-of-thought prompting relative to
direct answering, as o1-preview showed at release, is itself informative about whether a model's gains
come from reasoning depth rather than raw context capacity. Because six very different task categories
(QA, in-context learning, dialogue history, code, structured data) are pooled into one accuracy figure,
check the category and length-bucket breakdown before assuming uniform capability, and confirm whether
a reported score used direct answering or extended reasoning before comparing it to another model's.
