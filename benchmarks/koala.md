---
id: koala
name: "Koala (HELM Instruct)"
aliases:
  - "Koala Eval"
  - "koala_test_set"
  - "Koala test dataset"
page_kind: benchmark
category: instruction-following
subcategory: "HELM Instruct critique of 180 Koala user prompts"
status: unknown
summary: "HELM Instruct scenario over 180 Koala user prompts, scored with a 1-5 Helpfulness critique rather than gold answers."
measures: >
  koala, as this id, is HELM's KoalaScenario: the 180 English user prompts the BAIR Koala team
  used to human-evaluate their dialogue model. The model sees only the prompt and writes a
  free-form reply. There is no gold reference in the HELM instances. The skill is following a
  real web user's request (the test-set README says non-English and coding prompts were
  removed so raters could judge them). This is not the Koala-13B training mix, not Alpaca's
  180 self-instruct eval queries, and not [self_instruct](self_instruct.md)'s 252 tasks.
task_format: >
  Zero-shot generation. HELM downloads koala_test_set.jsonl and emits one TEST_SPLIT Instance
  per line with empty references. Adapter defaults from get_instruct_adapter_spec: max_tokens
  512, temperature 0.7, max_train_instances 0. Run spec name is koala. HELM Instruct's blog
  states that scenarios with more than 100 instances are randomly sampled to 100 in that study.
metric:
  name: Helpfulness
  direction: higher_is_better
  unit: "1-5"
  max_score: 5.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    InstructionFollowingCritiqueMetric asks num_respondents annotators five 1-5 axes:
    Helpfulness, Understandability, Completeness, Conciseness, Harmlessness. Scenario
    metadata main_metric is Helpfulness ("Does the model appear to do what it is instructed
    to?"). BAIR's original study used pairwise human preference among Koala, Alpaca, and
    ChatGPT on this set and on Alpaca's 180-query set; that ranking is not HELM's 1-5 mean.
dataset:
  size: 180
  size_note: >
    koala_test_set.jsonl counted directly: 180 lines, ids koala_0 through koala_179. Matches
    the test-set README and the BAIR blog ("our own (Koala) test set, which consists of 180
    real user queries"). Prompts were filtered to BLEU <= 20% against Koala's training set;
    non-English and coding prompts were dropped. HELM Instruct experiments may score a 100-item
    sample of this 180.
  url: "https://github.com/arnav-gudibande/koala-test-set"
  license: "Apache-2.0 (test-set LICENSE file); README additionally asks that the set not be used for training"
  languages:
    - en
  modalities:
    - text
  splits: "HELM maps every row to TEST_SPLIT; no train split in this scenario"
  public_test_set: true
publisher:
  org: "Berkeley Artificial Intelligence Research Lab (BAIR), UC Berkeley (test set); Stanford CRFM (HELM scenario)"
  authors:
    - "Xinyang Geng"
    - "Arnav Gudibande"
    - "Hao Liu"
    - "Eric Wallace"
    - "Pieter Abbeel"
    - "Sergey Levine"
    - "Dawn Song"
  url: "https://bair.berkeley.edu/blog/2023/04/03/koala/"
paper:
  title: ""
  arxiv: ""
  url: "https://bair.berkeley.edu/blog/2023/04/03/koala/"
  year: 2023
leaderboard_url: "https://crfm.stanford.edu/helm/instruct/"
repo_url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/koala_scenario.py"
released: "2023-04"
last_updated: ""
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
    No numeric HELM Instruct leaderboard cell was read (the public page is a JavaScript app).
    BAIR reported pairwise human wins on this set versus Alpaca and ChatGPT for Koala-13B;
    that protocol is not a 1-5 HELM mean.
contamination:
  risk: medium
  note: >
    The 180 prompts have been public on GitHub since the 3 April 2023 post. The README asks
    users not to train on them. HELM scores a fresh generation with a critique, so there is
    no answer key to memorise, but familiarity with the prompts can still inflate Helpfulness.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: "koala"
  opencompass: ""
  bigbench: ""
  other: "Run spec in instruction_following_run_specs.py; group koala; HELM Instruct site."
tags:
  - instruction-following
  - helm
  - critique
  - open-ended
  - chat
sources:
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/scenarios/koala_scenario.py"
    title: "HELM KoalaScenario (180-file URL, empty references, main_metric Helpfulness)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/run_specs/instruction_following_run_specs.py"
    title: "HELM @run_spec_function koala (critique metrics, helm/instruct site)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/metrics/instruction_following_critique_metrics.py"
    title: "InstructionFollowingCritiqueMetric (1-5 Helpfulness and four other axes)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/stanford-crfm/helm/main/src/helm/benchmark/adaptation/common_adapter_specs.py"
    title: "get_instruct_adapter_spec (zero-shot, max_tokens 512, temperature 0.7)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/arnav-gudibande/koala-test-set/main/koala_test_set.jsonl"
    title: "koala_test_set.jsonl counted (180 prompts, ids koala_0..koala_179)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/arnav-gudibande/koala-test-set/main/README.md"
    title: "Koala Evaluation Set README (180 queries, BLEU filter, academic use, do not train)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/arnav-gudibande/koala-test-set/main/LICENSE"
    title: "koala-test-set Apache License 2.0"
    accessed: "2026-09-08"
  - url: "https://web.archive.org/web/20230403232635/https://bair.berkeley.edu/blog/2023/04/03/koala/"
    title: "BAIR Koala blog via Wayback (3 Apr 2023; 180-query test set; authors)"
    accessed: "2026-09-08"
  - url: "https://crfm.stanford.edu/2024/02/18/helm-instruct.html"
    title: "HELM Instruct post (Koala Eval among scenarios; sample 100 if n>100; 1-5 criteria)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-052 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-052"
---

## What it measures

koala, as this id, is HELM's wrapper around the BAIR Koala team's 180-prompt eval set. The model must follow an English user request scraped from public chat logs, not a closed label set. HELM stores no gold answer. The BAIR blog distinguishes this "Koala Test Set" from Stanford Alpaca's 180 self-instruct queries. It is not [self_instruct](self_instruct.md) and not [mt_bench](mt_bench.md). Non-English and coding prompts were filtered out so human raters could score the rest.

## How it is scored

The run spec attaches `InstructionFollowingCritiqueMetric` with a caller-chosen `num_respondents`. Annotators rate Helpfulness, Understandability, Completeness, Conciseness, and Harmlessness on 1-5 maps. Metadata treats Helpfulness as the main number. BAIR's own study used pairwise human preference among Koala-13B, Alpaca, and ChatGPT; do not mix those win rates with HELM's 1-5 means. HELM Instruct's write-up samples 100 items when a scenario is larger than 100, so a HELM Instruct table cell may not be the full 180.

## Dataset and licence

180 JSONL rows, ids koala_0-koala_179, counted from the file HELM downloads. Apache-2.0 on the test-set LICENSE file. The README still asks that the prompts not be used for training and describes them as released for academic use. BLEU > 20% overlap with Koala training data was filtered.

## Who publishes it

Test set: BAIR at UC Berkeley. Students Xinyang Geng, Arnav Gudibande, Hao Liu, Eric Wallace; advisors Pieter Abbeel, Sergey Levine, Dawn Song. Blog dated 3 April 2023. HELM packaging: Stanford CRFM, run spec `koala` under HELM Instruct.

## Lineage

The Koala blog is a model release; this page is only the eval prompts as HELM scores them. HELM Instruct groups koala with [self_instruct](self_instruct.md), Vicuna, Open Assistant, grammar, and Anthropic HH RLHF run specs that share the same critique metric. Vicuna and Open Assistant do not yet have pages here. [alpaca_eval](alpaca_eval.md) and [mt_bench](mt_bench.md) are different chat-preference stacks.

## Saturation and contamination

No HELM Instruct numeric top was read. The 180 prompts have been public since April 2023. There is no answer key to leak, but instruction-tuned models may have seen the queries. Pairwise BAIR figures and HELM 1-5 figures are not a shared ceiling.

## How to run it

HELM run spec name `koala`. Needs a working critique backend and `num_respondents`. Generation: 512 tokens, temperature 0.7, zero-shot. Without enough critiques the metric returns no stats, so a missing Helpfulness cell is not a zero. Record whether the run used all 180 prompts or HELM Instruct's 100-item sample.

## Reading the numbers

A high Helpfulness mean means annotators thought the model did what the user asked, on a 1-5 rubric. It is not a win rate against ChatGPT, not MT-Bench's 1-10 judge, and not exact match. Compare HELM numbers only with the same respondent count, judge pool, temperature, and sample size. For closed-form instruction constraints, use IFEval-style checks instead of this critique.
