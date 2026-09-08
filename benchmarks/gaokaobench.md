---
id: gaokaobench
name: "GAOKAO-Bench"
aliases:
  - "GaokaoBench"
  - "Gaokao Bench"
  - "Evaluating the Performance of Large Language Models on GAOKAO Benchmark"
page_kind: benchmark
category: knowledge
subcategory: "real Chinese national college entrance examination (Gaokao) questions, 2010-2022, objective and subjective"
status: active
summary: "Real Chinese Gaokao exam questions from 2010-2022 (1,781 objective, 1,030 subjective), scored zero-shot and converted to the exam's own 750-point scale; most harnesses run only the objective subset."
measures: >
  GAOKAO-Bench tests broad academic knowledge and reasoning by using actual questions collected from
  China's national college entrance examination (the Gaokao) sat between 2010 and 2022, spanning
  Chinese, Mathematics (scored separately for the science and humanities tracks, which set different
  papers), English, Physics, Chemistry, Biology, Political Science, History and Geography. The suite
  keeps both halves of the real exam: 1,781 objective questions (63.4%, machine-checkable formats such
  as multiple choice, cloze and fill-in-the-blank) and 1,030 subjective questions (36.6%, free-form
  answers that a human grader would mark by hand), for 2,811 questions in total. Its English-subject
  questions are themselves written in English, since that mirrors the actual Gaokao English paper
  Chinese students sit.
task_format: >
  Zero-shot, designed by the authors to mirror how a human examinee takes the exam rather than a
  few-shot evaluation protocol. Objective questions are scored by rule-based extraction of the
  predicted answer letter or value. Subjective questions were originally graded by human teachers (the
  authors thank teachers at a Shanghai secondary school for this); the repository also ships a
  GPT-4-based LLM-as-judge script as a scalable alternative, and the paper reports Spearman and
  Kendall-Tau correlation between the two rather than treating the LLM judge as ground truth.
metric:
  name: "accuracy on the objective subset (most harness implementations); the original paper's primary figure is a converted total score matched to the Gaokao's own point scale"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single random-guess figure applies: the objective subset mixes single-answer multiple choice,
    multi-select, cloze and fill-in-the-blank formats with different option counts rather than a
    uniform 4-option layout, so a flat random baseline would misstate difficulty. The introducing
    paper's own headline metric is different again: a "converted total score" that rescales
    weighted objective-plus-subjective performance onto the real Gaokao's own 750-point scale (the
    same maximum a real student's total score is reported on), with GPT-4 scoring above 400 points in
    the original 2023 comparison. No formal human baseline percentage is published, though subjective
    questions were originally graded by human teachers as the reference standard.
dataset:
  size: 2811
  size_note: >
    2,811 questions total: 1,781 objective (63.36%) and 1,030 subjective (36.64%), collected from
    official national Gaokao exam papers from 2010 to 2022, confirmed directly from the count table in
    the repository's own README.
  url: "https://github.com/OpenLMLab/GAOKAO-Bench"
  license: "Apache License 2.0, confirmed from the repository's own LICENSE file"
  languages: [zh, en]
  modalities: [text]
  splits: "single set, organised by year (2010-2022) and exam paper/category rather than a train/test split"
  public_test_set: true
publisher:
  org: "School of Computer Science, Fudan University, with School of Computer Science and Technology, East China Normal University (confirmed from the paper's own affiliation footnotes)"
  authors:
    - "Xiaotian Zhang"
    - "Chunyang Li"
    - "Yi Zong"
    - "Zhengyu Ying"
    - "Liang He"
    - "Xipeng Qiu"
    - "Tianxiang Sun"
    - "Peng Li"
    - "Shiqiao Meng"
    - "Yanjun Zheng"
    - "Jun Zhan"
    - "Zhangyue Yin"
    - "Xiannian Hu"
    - "Guofeng Quan"
    - "Qixiang Wang"
  url: "https://github.com/OpenLMLab/GAOKAO-Bench"
paper:
  title: "Evaluating the Performance of Large Language Models on GAOKAO Benchmark"
  arxiv: "2305.12474"
  url: "https://arxiv.org/abs/2305.12474"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/OpenLMLab/GAOKAO-Bench"
released: "2023-05"
last_updated: "2026-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: 89.59
  as_of: "2024-05"
  note: >
    On OpenCompass's objective-only accuracy scoring (not the paper's own converted-total-score
    metric), qwen1.5-110b-chat-hf reaches 89.59%, with several other 2024-era chat models (qwen1.5-72b
    88.58%, qwen1.5-32b 86.15%) close behind, read directly from OpenCompass's own results table. In
    the original paper's own 2023 comparison on the converted 750-point scale, GPT-4-0314 led at 72.2%
    objective-question scoring rate, with a clear gap to GPT-3.5-turbo-0301 at 53.2% -- evidence of
    real separation between models rather than ceiling clustering as of the models each source tested,
    though no 2025-2026 frontier-model figure was found for this page in either scoring convention.
contamination:
  risk: high
  note: >
    The full question set, including subjective questions and their reference/marking material, has
    been public under a permissive licence since May 2023 and covers exam papers that were already
    circulating in Chinese educational materials well before that; a companion project
    (GAOKAO-Bench-Updates, linked from the same GitHub organisation) exists specifically to add 2023-
    and-later Gaokao papers as a fresher, less-exposed extension, which is itself an implicit
    acknowledgement that the original 2010-2022 set is a contamination risk for newer models.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "GaokaoBench (dataset configs under opencompass/configs/datasets/GaokaoBench/, including GaokaoBench_no_subjective_gen_d21e37 and GaokaoBench_no_subjective_gen_4c31db, both scoring the objective-only subset)"
  bigbench: ""
  other: >
    Reference scoring scripts (objective_bench.py, subjective_bench.py, OBJ_score_evaluation.py,
    SUB_score_evaluation.py, merge_OBJ_SUB_score.py) ship in the OpenLMLab/GAOKAO-Bench repository and
    implement the paper's own converted-total-score pipeline; no lm-evaluation-harness, HELM or
    inspect_evals implementation of GAOKAO-Bench itself was found (AGIEval, a separate benchmark,
    separately includes several individual Gaokao-subject splits -- see Lineage).
tags:
  - knowledge
  - chinese
  - exam
  - multi-format
  - llm-as-judge
  - zero-shot
sources:
  - url: "https://arxiv.org/abs/2305.12474"
    title: "Evaluating the Performance of Large Language Models on GAOKAO Benchmark"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2305.12474"
    title: "GAOKAO-Bench paper, full text (ar5iv) -- affiliations, scoring methodology, 750-point conversion, results"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/OpenLMLab/GAOKAO-Bench/main/README.md"
    title: "OpenLMLab/GAOKAO-Bench GitHub README (question counts, licence, worked example, results tables)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/OpenLMLab/GAOKAO-Bench/main/LICENSE"
    title: "OpenLMLab/GAOKAO-Bench LICENSE file (Apache 2.0)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/GaokaoBench/README.md"
    title: "OpenCompass GaokaoBench dataset README (base- and chat-model results tables, per-subject breakdown)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/agieval/gaokao-biology.yaml"
    title: "lm-evaluation-harness agieval/gaokao-biology.yaml (confirms AGIEval's Gaokao splits are a separate project)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/agieval/README.md"
    title: "lm-evaluation-harness agieval README (AGIEval paper citation, arXiv 2304.06364)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 6, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

GAOKAO-Bench tests broad academic knowledge and reasoning using real questions collected from China's
national college entrance examination, the Gaokao, sat between 2010 and 2022. It spans Chinese,
Mathematics (scored on separate science- and humanities-track papers, which is how the real exam
works), English, Physics, Chemistry, Biology, Political Science, History and Geography. Unlike a
benchmark that only keeps the machine-gradable slice of an exam, GAOKAO-Bench preserves both halves:
1,781 objective questions (63.4% of the set, in machine-checkable formats such as multiple choice,
cloze and fill-in-the-blank) and 1,030 subjective questions (36.6%, free-form answers a human teacher
would mark by hand), for 2,811 questions total. Its English-subject questions are themselves written in
English, since that mirrors the real Gaokao English paper.

## How it is scored

Evaluation is zero-shot by design, intended to mirror how a human examinee sits the exam rather than
give a model few-shot examples. Objective questions are scored by rule-based extraction of the
predicted answer. Subjective questions are harder: the original paper had them graded by human
teachers (the authors credit teachers at a Shanghai secondary school), and the repository separately
ships a GPT-4-based LLM-as-judge script as a scalable alternative, reporting Spearman and Kendall-Tau
correlation between LLM-assigned and human-assigned scores rather than treating the LLM judge as
ground truth -- the paper describes the resulting agreement as "a moderate level of consistency." The
paper's headline number combines both question types into a converted total score rescaled onto the
real Gaokao's own 750-point scale, with GPT-4-0314 the strongest model tested at over 400 points. Most
downstream harnesses, by contrast, report plain accuracy on the objective subset alone: OpenCompass's
own `GaokaoBench_no_subjective_gen` configurations exclude the subjective questions entirely, so a
harness-reported GAOKAO-Bench score is not the same figure as the paper's own converted total score.

## Dataset and licence

2,811 questions in total -- 1,781 objective (63.36%) and 1,030 subjective (36.64%) -- collected from
official national Gaokao exam papers spanning 2010 to 2022, confirmed directly from the count table in
the project's own README. The dataset is distributed as JSON files in the OpenLMLab/GAOKAO-Bench GitHub
repository under an Apache License 2.0, confirmed from the repository's own LICENSE file, rather than
through an official Hugging Face release (a couple of unofficial third-party mirrors exist there).
Questions and their reference answers are fully public, including the subjective questions' marking
material.

## Who publishes it

GAOKAO-Bench was introduced by Xiaotian Zhang, Chunyang Li, Yi Zong, Zhengyu Ying, Liang He, Xipeng
Qiu and nine further co-authors, first posted to arXiv in May 2023 and subsequently revised (most
recently August 2026, per the arXiv listing, with author-metadata corrections rather than new results).
Core authors are affiliated with the School of Computer Science at Fudan University, with two authors
at the School of Computer Science and Technology, East China Normal University. The project is
maintained on GitHub under the OpenLMLab organisation, which also hosts a multimodal companion
(GAOKAO-MM) and a separate GAOKAO-Bench-Updates repository that adds 2023-and-later Gaokao papers.

## Lineage

GAOKAO-Bench has no predecessor tracked in this repository. Its GitHub organisation lists two related
follow-on projects not catalogued here: GAOKAO-MM, a multimodal variant testing perception alongside
knowledge and reasoning, and GAOKAO-Bench-Updates, which extends the question pool with post-2022
Gaokao papers specifically to outrun contamination in the original set. GAOKAO-Bench should not be
confused with AGIEval (Zhong et al. 2023, arXiv 2304.06364), a separate, broader benchmark that
independently draws several individual Gaokao-subject splits (gaokao-biology, gaokao-chemistry,
gaokao-chinese, gaokao-english, gaokao-geography, gaokao-history, gaokao-mathcloze, gaokao-mathqa,
gaokao-physics -- confirmed directly in lm-evaluation-harness's `agieval` task directory) into its own
20-exam collection alongside the American SAT, LSAT and other qualification tests; the two projects
share source material but not authorship, curation, or the objective/subjective split GAOKAO-Bench is
built around. This wiki's [C-Eval](ceval.md) and [CMMLU](cmmlu.md) pages are contemporaneous
Chinese-language exam suites but draw on original, authored-for-the-benchmark question banks rather
than a real, publicly administered exam's actual questions.

## Saturation and contamination

Two scoring conventions give two different pictures. On OpenCompass's objective-only accuracy metric,
2024-era chat models cluster high -- qwen1.5-110b-chat-hf reaches 89.59%, with qwen1.5-72b-chat-hf
(88.58%) and qwen1.5-32b-chat-hf (86.15%) close behind -- suggesting the objective subset alone is
under real ceiling pressure for strong Chinese-tuned models. On the original paper's converted
750-point scale, by contrast, the 2023 comparison showed clear separation, with GPT-4-0314 leading at
72.2% objective-question scoring rate against GPT-3.5-turbo-0301's 53.2%. No 2025-2026 frontier-model
figure was found for this page under either convention, so this is marked "watch" rather than
"saturated" or "open" outright. Contamination risk is high: the full 2010-2022 question set, including
subjective reference answers, has been public since May 2023 and covers exam papers that already
circulated widely in Chinese educational materials before that; the existence of a dedicated
GAOKAO-Bench-Updates project to add fresher, post-2022 papers is itself an implicit acknowledgement
that the original set is exposed.

## How to run it

The authors' own repository ships the full evaluation pipeline (`objective_bench.py`,
`subjective_bench.py`, scoring scripts, and a `merge_OBJ_SUB_score.py` step that produces the converted
Gaokao total score). OpenCompass implements the objective-only subset as `GaokaoBench`, with configs
including `GaokaoBench_no_subjective_gen_d21e37` and `GaokaoBench_no_subjective_gen_4c31db`. No
lm-evaluation-harness, HELM or inspect_evals implementation of GAOKAO-Bench itself was found. Because
the objective-only harness accuracy and the paper's own converted total score are different metrics on
different scales, a reported "GAOKAO-Bench" number is not meaningful without knowing which convention
produced it.

## Reading the numbers

A strong GAOKAO-Bench score shows a model handling real Chinese secondary-education exam material
across a wide subject range, in the exact multi-format style (multiple choice, cloze, fill-in-the-blank,
essay) a Chinese student actually faces, which is a richer test of format-following than a uniform
4-option multiple-choice suite. Because most harness numbers cover only the objective subset, they say
nothing about a model's performance on the 36.6% of the original exam that requires extended,
free-form answers -- a model could score well on objective GAOKAO-Bench while never having its
essay-writing or extended-reasoning ability checked by this benchmark at all. Given the 2023-2024
comparisons already show several models above 85% on the objective subset, corroborate an
unusually high score against C-Eval or CMMLU, and check whether the figure reported is objective-only
accuracy or the paper's own 750-point converted score before comparing two numbers.
