---
id: mmlu_pro
name: "MMLU-Pro"
page_kind: benchmark
category: knowledge
subcategory: "multitask academic and professional knowledge (reasoning-augmented)"
status: active
summary: "A harder, ten-option successor to MMLU with about 12,000 reasoning-heavy questions across 14 categories, built to restore headroom lost to MMLU's saturation at the frontier."
measures: >
  MMLU-Pro gives a model a question and up to ten labelled answer options (most questions use all
  ten; a small number carry fewer after manual review removed unreasonable distractors), drawn from
  14 broad categories spanning STEM, humanities, social sciences and business/health/other topics:
  Biology, Business, Chemistry, Computer Science, Economics, Engineering, Health, History, Law,
  Math, Philosophy, Physics, Psychology and Other. The model must select the single correct option.
  Roughly 57% of the questions are a difficulty-filtered subset of the original MMLU test set (with
  "trivial and ambiguous" items removed); the remaining 43% are newly written from a STEM question
  website, TheoremQA and SciBench, with GPT-4-generated distractors expanding every question from
  four options toward ten, reviewed afterward by a panel of over ten subject-matter experts.
task_format: >
  Multiple-choice question answering with up to ten labelled options, graded on the single option
  the model selects. The reference protocol is 5-shot with chain-of-thought prompting, with fewshot
  examples drawn from a dedicated 70-question validation split; scoring extracts the answer letter
  from free-form generated text (for example via a regex matching "the answer is (X)") rather than
  comparing option log-likelihoods, because the authors found direct/log-likelihood scoring
  under-performs chain-of-thought by up to 19 points on this dataset -- the opposite of the original
  MMLU. Across 24 prompt styles the authors tested, score sensitivity to prompt wording fell from
  4-5% on MMLU to about 2% on MMLU-Pro.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 10
  baseline_note: >
    10% is the ten-option random-guess rate, versus 25% on the original four-option MMLU -- one
    reason raw scores are not comparable between the two benchmarks. No human baseline has been
    published for MMLU-Pro.
dataset:
  size: 12032
  size_note: >
    The Hugging Face mirror (TIGER-Lab/MMLU-Pro, "default" config) holds 12,032 test questions
    (used for scoring) plus a separate 70-question validation split reserved for few-shot prompting
    -- 12,102 rows total. Of the 12,032 test questions, 6,810 are difficulty-filtered survivors of
    the original MMLU test set and 5,222 are newly collected, per the dataset card's own count.
    Math (1,351) and Physics (1,299) are the largest of the 14 categories; History (381) and
    Computer Science (410) are the smallest.
  url: "https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro"
  license: MIT
  languages:
    - en
  modalities:
    - text
  splits: "validation (70, few-shot CoT source), test (12,032, scored)"
  public_test_set: true
publisher:
  org: "TIGER Lab, University of Waterloo (with co-authors at the University of Toronto and Carnegie Mellon University)"
  authors:
    - "Yubo Wang"
    - "Xueguang Ma"
    - "Ge Zhang"
    - "Yuansheng Ni"
    - "Abhranil Chandra"
    - "Shiguang Guo"
    - "Weiming Ren"
    - "Aaran Arulraj"
    - "Xuan He"
    - "Ziyan Jiang"
    - "Tianle Li"
    - "Max Ku"
    - "Kai Wang"
    - "Alex Zhuang"
    - "Rongqi Fan"
    - "Xiang Yue"
    - "Wenhu Chen"
  url: "https://github.com/TIGER-AI-Lab/MMLU-Pro"
paper:
  title: "MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark"
  arxiv: "2406.01574"
  url: "https://arxiv.org/abs/2406.01574"
  year: 2024
leaderboard_url: "https://huggingface.co/spaces/TIGER-Lab/MMLU-Pro"
repo_url: "https://github.com/TIGER-AI-Lab/MMLU-Pro"
released: "2024-06"
last_updated: "2026-01"
lineage:
  family: mmlu
  predecessor: mmlu
  successors: []
  variants: []
saturation:
  status: open
  top_score: 91.16
  as_of: "2026-09"
  note: >
    The paper's own GPT-4o baseline scored 72.55% (CoT) at launch in June 2024. The public
    leaderboard's top TIGER-Lab-verified row, as read for this page in September 2026, credits
    Gemini-3.1-Pro (added to the leaderboard 2026-03 per the dataset card changelog) with 91.16%
    overall -- a roughly 19-point rise in a little over two years. Per-category scores still spread
    models out (one verified run showed category scores from 73.6% to 93.0%), so the benchmark has
    not collapsed the way original MMLU did, but the pace of the climb plus a January 2026 fix for
    an exploitable formatting shortcut in the answer options are both worth watching.
contamination:
  risk: medium
  note: >
    About 57% of MMLU-Pro's questions are carried over from the original MMLU test set, which has
    been public with its answer key since September 2020 and is already assessed as high
    contamination risk on the `mmlu` family page. The remaining ~43% are newly written, and the
    full test-set answer key (old and new questions alike) has been public on Hugging Face since
    the June 2024 release with no held-out or refreshed portion. No contamination study specific to
    MMLU-Pro, and no publisher statement about the fraction of frontier pretraining corpora that
    include it, was found in this research.
harness:
  lm_eval: "mmlu_pro (group of 14 mmlu_pro_<category> tasks; generate_until scoring with regex answer-letter extraction, 5-shot from the validation split by default)"
  inspect_evals: "mmlu_pro"
  helm: ""
  opencompass: "mmlu_pro (0-shot CoT, few-shot and generic-LLM-judge config variants)"
  bigbench: ""
  other: "Reference evaluation scripts and cached model predictions are maintained in TIGER-AI-Lab/MMLU-Pro on GitHub (eval_results/)."
tags:
  - knowledge
  - multiple-choice
  - multitask
  - chain-of-thought
  - ten-option
  - five-shot
sources:
  - url: "https://arxiv.org/abs/2406.01574"
    title: "MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark (Wang et al., arXiv:2406.01574)"
    accessed: "2026-09-08"
  - url: "https://github.com/TIGER-AI-Lab/MMLU-Pro"
    title: "TIGER-AI-Lab/MMLU-Pro GitHub repository (reference code, eval scripts, licence)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro"
    title: "TIGER-Lab/MMLU-Pro dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/spaces/TIGER-Lab/MMLU-Pro"
    title: "MMLU-Pro Leaderboard, Hugging Face Space"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/mmlu_pro/README.md"
    title: "lm-evaluation-harness mmlu_pro task README (groups, tasks, changelog)"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/mmlu_pro"
    title: "inspect_evals mmlu_pro task source"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/mmlu_pro"
    title: "OpenCompass mmlu_pro dataset configs"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=TIGER-Lab/MMLU-Pro"
    title: "TIGER-Lab/MMLU-Pro datasets-server size API"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice N"
---

## What it measures

MMLU-Pro gives a model a question and up to ten labelled options -- a few carry fewer after review
removed weak distractors -- across 14 categories: Biology, Business, Chemistry, Computer Science,
Economics, Engineering, Health, History, Law, Math, Philosophy, Physics, Psychology and Other. The
model selects the single correct option.

About 57% of the 12,032 test questions are difficulty-filtered MMLU survivors; the rest are new,
from a STEM website, TheoremQA and SciBench, with options expanded toward ten via GPT-4-generated
distractors and reviewed by a panel of over ten experts. This cuts accuracy 16-33 points versus
the same models on original MMLU.

## How it is scored

Accuracy against a 10% random-guess floor, versus 25% on four-option MMLU -- one reason raw scores
are not comparable between the two. No human baseline is published for MMLU-Pro.

Where original MMLU favoured log-likelihood scoring over chain-of-thought (CoT), MMLU-Pro was
built so CoT wins: accuracy drops as much as 19 points when CoT is switched off for GPT-4o.
Grading extracts the answer letter from free-form text rather than comparing option
log-likelihoods. Reference protocol is 5-shot, examples drawn from a dedicated 70-question
validation split, though the leaderboard notes this isn't uniform -- "some models like Gemini use
0-shot" -- so shot count is not guaranteed comparable across reported scores.

## Dataset and licence

The Hugging Face mirror holds 12,032 test questions (scored) plus a 70-question validation split,
12,102 rows total: 6,810 carried over from original MMLU after a difficulty filter, 5,222 newly
written. Math (1,351) and Physics (1,299) are the largest categories; History (381) and Computer
Science (410) the smallest. Licence is MIT per the dataset card; the GitHub repository's
evaluation code is separately licensed Apache-2.0. Answers are public in both splits; maintainers
actively fix errors, most recently a January 2026 trim of a leading-space quirk flagged as a
potential shortcut.

## Who publishes it

Yubo Wang, Xueguang Ma, Ge Zhang, Yuansheng Ni, Abhranil Chandra, Shiguang Guo, Weiming Ren, Aaran
Arulraj, Xuan He, Ziyan Jiang, Tianle Li, Max Ku, Kai Wang, Alex Zhuang, Rongqi Fan, Xiang Yue and
Wenhu Chen published MMLU-Pro in June 2024 (arXiv:2406.01574), accepted at NeurIPS 2024. Most are
at TIGER Lab, University of Waterloo (led by Wenhu Chen), with co-authors at Toronto and Carnegie
Mellon. TIGER Lab maintains the GitHub repository, dataset and leaderboard Space.

## Lineage

MMLU-Pro's predecessor is MMLU (`mmlu`): both test multitask academic and professional knowledge,
but MMLU-Pro pools MMLU's 57 subjects into 14 categories, expands four options to ten, adds harder
reasoning questions, and drops items judged trivial or noisy. No formal successor was found.
Separately, several frontier cards here carry a `mmlu_physics` key close in value to that model's
`mmlu_pro` score -- possibly a mis-keyed MMLU-Pro Physics score, not confirmed; see `mmlu_physics`
rather than treating it as part of this lineage yet.

## Saturation and contamination

MMLU-Pro was built to restore headroom MMLU lost to saturation, and per-category scores still
separate models: one verified run showed scores from 73.6% (Engineering) to 93.0% (Biology), and
every tested model dropped 16-33 points versus its own MMLU score. But the ceiling is approaching
fast: GPT-4o scored 72.55% (CoT) at launch in June 2024, and the top verified leaderboard row read
for this page in September 2026 credits Gemini-3.1-Pro with 91.16% -- roughly 19 points higher in
two years. That pace, plus the January 2026 answer-formatting fix (see Dataset and licence), is
worth watching even though scores have not fully collapsed together.

Contamination risk is assessed here as medium. About 57% of questions carry over from original
MMLU and inherit its high contamination risk (public with its answer key since 2020); the rest are
new, and the full test-set answer key has been public since the June 2024 release with no held-out
portion. No contamination study specific to MMLU-Pro was found in this research.

## How to run it

Reference code and eval scripts live in TIGER-AI-Lab/MMLU-Pro on GitHub. In
lm-evaluation-harness the group is `mmlu_pro`, 14
`mmlu_pro_<category>` tasks generating free text and extracting the answer letter by regex,
5-shot by default from the validation split. inspect_evals ships an equivalent `mmlu_pro` task.
OpenCompass carries `mmlu_pro` with several config variants (0-shot CoT, few-shot, generic-LLM-judge).
Shot count and CoT-versus-direct prompting are not applied uniformly across the public leaderboard,
so treat cross-source comparisons with that in mind.

## Reading the numbers

A strong MMLU-Pro score is harder to reach by guessing or recall than a strong MMLU score,
reflecting more genuine reasoning under harder distractors -- the benchmark's whole reason for
existing. It says nothing about tasks outside multiple-choice knowledge testing: open-ended
generation, tool use, multi-turn dialogue. A single overall number also hides real per-category
spread, so check the 14 category scores before assuming uniform strength, especially between the
Math/Physics/Engineering cluster and the Law/History/Philosophy cluster. Before comparing two
models, check both used chain-of-thought and the same shot count, and treat MMLU-Pro and `mmlu`
scores as non-comparable given their different option counts and baselines.
