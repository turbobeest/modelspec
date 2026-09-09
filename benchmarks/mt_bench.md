---
id: mt_bench
name: MT-Bench
aliases:
- MT-bench
page_kind: benchmark
category: human-preference
subcategory: multi-turn chat quality
status: active
summary: Eighty multi-turn chat questions graded by an LLM judge as a fast, repeatable stand-in for human conversational preference.
measures: MT-Bench gives a chat model 80 open-ended questions spread across eight categories - writing, role-play, extraction, reasoning, math, coding, and two knowledge categories covering STEM and humanities or social science. Each question carries one scripted follow-up, so the model has to hold context across two turns rather than answer a single isolated prompt. The benchmark targets general chat quality and instruction-following on subjective, everyday requests, not narrow factual recall.
task_format: Open-ended two-turn chat completion, graded after generation by a separate judge model rather than by an exact-match answer key.
metric:
  name: LLM judge score
  direction: higher_is_better
  unit: points
  max_score: 10.0
  random_baseline: null
  human_baseline: null
  baseline_note: GPT-4 grades each turn on a 1-10 scale against a fixed rubric prompt; the two turn scores for a question are averaged, then averaged again across all 80 questions to get the final score. The paper also defines pairwise-baseline and pairwise-all grading modes as alternatives to single-answer grading.
dataset:
  size: 80
  size_note: 80 questions (10 per category), each with one follow-up turn, for 160 total prompts.
  url: https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge/data/mt_bench
  license: ''
  languages:
  - en
  modalities:
  - text
  splits: single set, no train/test split
  public_test_set: true
publisher:
  org: LMSYS Org
  authors:
  - Lianmin Zheng
  - Wei-Lin Chiang
  - Ying Sheng
  - Siyuan Zhuang
  - Zhanghao Wu
  - Yonghao Zhuang
  - Zi Lin
  - Zhuohan Li
  - Dacheng Li
  - Eric P. Xing
  - Hao Zhang
  - Joseph E. Gonzalez
  - Ion Stoica
  url: https://lmsys.org
paper:
  title: Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena
  arxiv: '2306.05685'
  url: https://arxiv.org/abs/2306.05685
  year: 2023
leaderboard_url: ''
repo_url: https://github.com/lm-sys/FastChat
released: '2023-06'
last_updated: ''
lineage:
  family: ''
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: watch
  top_score: null
  as_of: ''
  note: No maintained third-party MT-Bench leaderboard was found; current scores come from providers' own model cards, which is not a reliable way to track a shared ceiling. The judge scale is compressed (1-10) and the source paper documents position, verbosity and self-enhancement bias in GPT-4-as-judge, all of which make continued separation among strong models hard to trust.
contamination:
  risk: medium
  note: The 80 questions have been posted in full on GitHub since June 2023 and have not been refreshed, so any model trained on recent web or code crawls has plausibly seen the exact prompts. There is no held-out answer key to leak, since grading judges freshly generated responses, but familiarity with the question set could still inflate scores.
harness:
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: ''
tags:
- chat
- multi-turn
- llm-judge
- instruction-following
sources:
- url: https://arxiv.org/abs/2306.05685
  title: Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena (arXiv abstract)
  accessed: '2026-09-07'
- url: https://arxiv.org/html/2306.05685
  title: Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena (full text)
  accessed: '2026-09-07'
- url: https://github.com/lm-sys/FastChat/blob/main/fastchat/llm_judge/README.md
  title: 'FastChat: fastchat/llm_judge README'
  accessed: '2026-09-07'
- url: https://lmarena.ai
  title: lmarena.ai (redirects to arena.ai)
  accessed: '2026-09-07'
freshness:
  researched: '2026-09-07'
  researched_by: sonnet-5 agent, batch 1, slice H
  reviewed: ''
  reviewed_by: ''
---

## What it measures

MT-Bench asks a chat model to answer 80 open-ended questions, then a follow-up in the same conversation, and checks whether the replies are helpful, relevant, and well-formed across everyday chat situations. The eight categories - writing, role-play, extraction, reasoning, math, coding, and two knowledge splits - were chosen to mirror how people actually use a chat assistant rather than to test isolated factual recall. Because there is a second turn, the benchmark also rewards a model for staying consistent with what it already said.

The questions themselves are static and short (80 total), which keeps MT-Bench cheap to run. What makes it distinctive is not the question set but the grading: a stronger model reads the answer and assigns a score, standing in for a human rater who would otherwise have to read every transcript.

## How it is scored

The default protocol is single-answer grading: GPT-4 is shown the question, the model's two-turn answer, and a grading rubric, then returns a score from 1 to 10 for each turn. FastChat also supports pairwise-baseline grading (compare against a fixed reference model such as GPT-3.5-turbo) and pairwise-all grading (every model against every other model), which the original paper used to validate the judge itself.

The paper found that GPT-4 as a judge agrees with both controlled and crowdsourced human preference around 80% of the time, similar to the agreement between two human raters. It also documents known judge failure modes: position bias (favoring whichever answer appears first), verbosity bias (favoring longer answers), and self-enhancement bias (a judge favoring its own outputs), along with weaker grading on math and reasoning questions that chain-of-thought and reference-guided prompts partly fix.

## Dataset and licence

The question set is 80 items, 10 per category, each with one scripted follow-up turn, held in the FastChat repository under `fastchat/llm_judge/data/mt_bench`. No separate data licence is stated for the question set; the repository code itself is open source. The questions and the paired human-preference data (3K expert votes, 30K crowdsourced conversations) are published in full rather than held out.

## Who publishes it

MT-Bench comes from LMSYS Org, the group behind Vicuna and Chatbot Arena, in the NeurIPS 2023 Datasets and Benchmarks paper "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" by Lianmin Zheng, Wei-Lin Chiang, and co-authors including Joseph E. Gonzalez and Ion Stoica. LMSYS's Chatbot Arena later separated into its own company and rebranded first to LMArena and then to Arena (arena.ai); MT-Bench itself has no actively maintained third-party leaderboard, and current scores are almost always self-reported by model providers in their own model or system cards.

## Lineage

MT-Bench and Chatbot Arena were introduced together in the same paper: MT-Bench is the static, judge-graded half, and Chatbot Arena is the live, crowdsourced human-preference half that this repository tracks separately as the `arena_elo` family. No formal successor to MT-Bench itself is documented by LMSYS in the sources reviewed here; later LLM-judge benchmarks from other groups, including this repository's `wildbench`, use a similar judge-based approach with real user tasks instead of a fixed question set.

## Saturation and contamination

There is no maintained public leaderboard to check where today's models sit against a ceiling, so saturation status is a judgment call rather than a measured fact: on a compressed 1-10 scale, with documented judge biases, further separation among strong models is hard to trust even where it is reported. The 80 questions have been public on GitHub since mid-2023 without refresh, so contamination risk is medium - the exact prompts are very likely inside recent training data, even though there is no stored "correct answer" for a model to have memorized.

## How to run it

The reference implementation lives in `fastchat/llm_judge` in the FastChat repository: `gen_model_answer.py` generates the model's answers, `gen_judgment.py` calls the judge model (GPT-4 by default) via API key, and `show_result.py` prints the aggregated scores. Because grading depends on which judge model is used and how the rubric prompt is worded, scores from different reporters are only safely comparable when the same judge and grading mode were used.

## Reading the numbers

A high MT-Bench score means a judge model found the assistant's answers coherent, on-topic, and well-structured across common chat scenarios, not that the assistant is factually reliable or safe. Because scores are graded by another LLM rather than measured against ground truth, verbosity and formatting can move the number as much as substance does. Two scores are only comparable if they used the same judge model and grading protocol, and providers rarely publish that detail alongside the headline number, so treat cross-provider MT-Bench comparisons with caution.
