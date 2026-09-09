---
id: haerae
name: "HAE-RAE Bench (lm-eval haerae)"
aliases:
  - "HAE-RAE Bench"
  - "HAE_RAE_BENCH"
  - "HAERAE-BENCH"
  - "HRB"
page_kind: benchmark
category: knowledge
subcategory: "Korean cultural and lexical multiple-choice (lm-eval five-task cut)"
status: unknown
summary: "lm-eval group for HAE-RAE Bench: five Korean multiple-choice tasks of native vocabulary and culture; the paper's reading-comprehension slice is omitted."
measures: >
  haerae is EleutherAI lm-evaluation-harness's group over HAE-RAE Bench, a Korean
  multiple-choice suite built to test cultural and lexical knowledge that does
  not transfer easily from English. The model sees a Korean query and must pick
  among five lettered options. The paper's six tasks are loan words, standard
  nomenclature, rare words, general knowledge, history, and reading
  comprehension. The harness drops reading comprehension for copyright and
  runs the other five. This id is not [csatqa](csatqa.md) (CSAT items from the
  same project) and not [click](click.md) (a later Korean culture exam).
task_format: >
  Zero-shot multiple choice in the harness (output_type multiple_choice).
  Prompt is the dataset `query` field. Choices are (A)–(E). Gold is `answer`.
  fewshot_split is test, so any few-shot run draws demonstrations from the
  same test items. The paper also reported 5-shot and 10-shot log-likelihood
  for open models, and a separate numbered-option generation protocol for
  GPT-3.5/GPT-4.
metric:
  name: "accuracy and length-normalized accuracy (acc, acc_norm)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 20
  human_baseline: null
  baseline_note: >
    Five options give 20% chance. The paper's reading-comprehension items were
    four-way; they are not in this harness group. No human baseline is stated
    in the paper or the 1.0/1.1 dataset cards. GPT-4 scored 67.8% (Korean
    prompt) and 68.2% (English prompt) zero-shot on the full six-task paper
    set, including reading comprehension, via generated option numbers rather
    than log-likelihood; that protocol is not this harness group.
dataset:
  size: 1091
  size_note: >
    1,091 test items in the five harness configs, matching both HAE_RAE_BENCH_1.0
    and 1.1 cards and the Hugging Face size API: standard_nomenclature 153,
    loan_words 169, rare_words 405, general_knowledge 176, history 188. The
    paper and 1.0 card total 1,538 including 447 KLAT reading-comprehension
    items, which lm-eval omits. HAE_RAE_BENCH_1.1 is 4,900 items across 13
    configs (the five paper tasks plus date understanding, proverb/lyrics
    denoising, definition matching, CSAT reading/law/geo/socio). HAE_RAE_BENCH_2.0
    is a separate five-task mini BIG-bench-style set, not this id. Hugging Face
    currently redirects HAERAE-HUB/HAE_RAE_BENCH to 1.1 (CC-BY-NC-ND-4.0).
    The 1.1 card YAML still has extra_gated fields, but the Hub API reported
    gated=false. Config names in the YAML (general_knowledge, loan_words, …)
    match 1.1, not 1.0's spaced names.
  url: "https://huggingface.co/datasets/HAERAE-HUB/HAE_RAE_BENCH_1.1"
  license: "CC-BY-NC-ND-4.0"
  languages:
    - ko
  modalities:
    - text
  splits: "five test-only configs in the lm-eval group; paper/1.0 also has a reading_comprehension test split not wired here"
  public_test_set: true
publisher:
  org: "HAE-RAE / HAERAE-HUB"
  authors:
    - "Guijin Son"
    - "Hanwool Lee"
    - "Suwan Kim"
    - "Huiseo Kim"
    - "Jaecheol Lee"
    - "Je Won Yeom"
    - "Jihyu Jung"
    - "Jung Woo Kim"
    - "Songseong Kim"
  url: "https://huggingface.co/datasets/HAERAE-HUB/HAE_RAE_BENCH_1.0"
paper:
  title: "HAE-RAE Bench: Evaluation of Korean Knowledge in Language Models"
  arxiv: "2309.02706"
  url: "https://arxiv.org/abs/2309.02706"
  year: 2023
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/haerae"
released: "2023-09"
last_updated: "2024-03"
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
    Paper (June 2023 GPT-4 snapshot): 67.8% Korean / 68.2% English zero-shot on
    the six-task set including reading comprehension, via generated numbers, not
    this five-task log-likelihood group. No later public leaderboard cell was
    read. Current ceiling on the harness cut is not established.
contamination:
  risk: medium
  note: >
    Gold labels have been public on Hugging Face since the 1.0 upload
    (created 2023-05-13). Loan-word and nomenclature items come from NIKL lists;
    rare-word items come from Woorimal Battle; history items were written from
    Namuwiki; general knowledge was crowd-sourced. 1.1's card still asks for a
    non-commercial research pledge, but the Hub API reported gated=false, so
    the 1.0 public mirror remains the practical contamination path. The omitted
    KLAT reading-comprehension slice is exam material.
harness:
  lm_eval: "haerae"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Group haerae aggregates haerae_general_knowledge, haerae_history,
    haerae_loan_word, haerae_rare_word, and haerae_standard_nomenclature with
    weight_by_size mean acc and acc_norm. dataset_path is HAERAE-HUB/HAE_RAE_BENCH
    (redirects to 1.1 as of this research). Paper evaluation code pointed at
    guijinSON/lm-evaluation-harness task name HRB.
tags:
  - korean
  - multiple-choice
  - cultural-knowledge
  - vocabulary
  - lm-eval
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/haerae/README.md"
    title: "lm-eval haerae README (five tasks; RC omitted; arXiv:2309.02706)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/haerae/_haerae.yaml"
    title: "lm-eval haerae group YAML (five tasks, weight_by_size acc/acc_norm)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/haerae/_default_haerae_yaml"
    title: "lm-eval haerae default config (HAERAE-HUB/HAE_RAE_BENCH, (A)–(E))"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2309.02706"
    title: "HAE-RAE Bench paper abs (submitted 2023-09-06, v5 2024-03-20)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2309.02706"
    title: "HAE-RAE Bench paper HTML (1,538 items, CC BY-NC-ND, GPT-4 67.8%)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/HAERAE-HUB/HAE_RAE_BENCH_1.0/raw/main/README.md"
    title: "HAE_RAE_BENCH_1.0 card (1,538 items, six tasks)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/HAERAE-HUB/HAE_RAE_BENCH_1.1/raw/main/README.md"
    title: "HAE_RAE_BENCH_1.1 card (4,900 items, 13 tasks, extra_gated YAML, CC-BY-NC-ND-4.0)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=HAERAE-HUB/HAE_RAE_BENCH_1.1"
    title: "Hugging Face size API for HAE_RAE_BENCH_1.1 (per-config row counts)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/HAERAE-HUB/HAE_RAE_BENCH_1.1"
    title: "Hugging Face dataset API for HAE_RAE_BENCH_1.1 (gated=false, lastModified 2024-03-30)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/HAERAE-HUB/HAE_RAE_BENCH"
    title: "Hugging Face dataset API: HAE_RAE_BENCH id resolves to HAE_RAE_BENCH_1.1"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/HAERAE-HUB/HAE_RAE_BENCH_2.0/raw/main/README.md"
    title: "HAE_RAE_BENCH_2.0 card (separate mini BIG-bench-style set, MIT)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-047 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-047"
---

## What it measures

The model answers Korean multiple-choice questions that depend on native vocabulary and culture, not on skills borrowed from English. Loan-word and standard-nomenclature items use National Institute of Korean Language lists, filtered for loan words through Naver and Daum encyclopedias. Rare-word items use definitions from the TV quiz *Woorimal Battle*, then the same five-option Levenshtein distractor method. General knowledge covers tradition, law, geography, K-pop, and Korean drama. History items were written from Namuwiki pages tagged Korean history. The paper also had a four-option reading-comprehension slice from the Korean Language Ability Test; lm-eval leaves that slice out for copyright. Inputs and labels are Korean text.

## How it is scored

The harness scores accuracy and length-normalized accuracy, then averages the five tasks weighted by item count. Open models in the paper used log-likelihood over the five option strings, 0-/5-/10-shot, bfloat16. GPT-3.5-Turbo and GPT-4 were instead asked to emit an option number, which the authors call harder and not directly comparable. Chance on the five harness tasks is 20%. No human score is published. Do not treat the paper's 67.8% GPT-4 figure as this group: that run included reading comprehension and used generation, not `haerae`.

## Dataset and licence

The five harness configs sum to 1,091 test items (153 + 169 + 405 + 176 + 188), confirmed on both 1.0 and 1.1 cards and the size API. The paper's full 1.0 release is 1,538 with 447 reading-comprehension items. Version 1.1 grows to 4,900 items in 13 tasks and replaces KLAT passages with CSAT reading items; those extra configs are not in `haerae`. Version 2.0 is a different, MIT-licensed mini-suite and is not this id. The paper and the 1.1 card release the data as CC BY-NC-ND 4.0, citing KLAT restrictions. The 1.1 README still has extra_gated fields for non-commercial research, but the Hub API reported `gated=false` on 2026-09-08. `HAERAE-HUB/HAE_RAE_BENCH` now redirects to 1.1, whose config names match the YAML.

## Who publishes it

Guijin Son and co-authors released the paper on 6 September 2023 (arXiv:2309.02706; v5 20 March 2024). The Hugging Face 1.0 repo was created 13 May 2023. The project sits under HAERAE-HUB. Contact on the cards is a Yonsei address. There is no live official leaderboard; the paper tables are the reference numbers.

## Lineage

HAE-RAE Bench was built because translated English tests miss Korean cultural depth. It is not [csatqa](csatqa.md), a separate HAE-RAE CSAT collection, and not [click](click.md). 1.1 extends the original five tasks; 2.0 is a different probe. The paper compared against KoBEST rather than claiming a successor.

## Saturation and contamination

No current harness leaderboard was opened. In 2023, GPT-4 was well above chance on the full paper set but not at ceiling (67.8% Korean prompt). Native Polyglot-Ko models were strong on loan words and history and weak on general knowledge (12.8B zero-shot 32.95% there). Contamination risk is medium: labels have been public since 2023, and sources include NIKL lists, Woorimal Battle, and Namuwiki.

## How to run it

`lm_eval --tasks haerae` runs the five subtasks. The group YAML sets `weight_by_size` aggregation. The dataset path is `HAERAE-HUB/HAE_RAE_BENCH`, which currently resolves to 1.1. Prompting GPT-4 with numbered options, as in the paper, is not this task. No inspect_evals, HELM, OpenCompass, or BIG-bench task with this id was found.

## Reading the numbers

A high `haerae` score means the model picks the right Korean option on these 1,091 public items, especially NIKL loan-word/nomenclature lists, Woorimal Battle rare words, and authored history/culture questions. It does not measure Korean reading of exam passages, CSAT science/social sets, or general reasoning. Quote the five-task harness result separately from paper tables that include reading comprehension or that mix log-likelihood with generated numbers. Compare Korean-prompt and English-prompt figures only when the paper's XLT setup is what was run. Look at [csatqa](csatqa.md) and [click](click.md) for other Korean knowledge cuts from nearby projects.
