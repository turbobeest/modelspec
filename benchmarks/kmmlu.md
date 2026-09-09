---
id: kmmlu
name: "KMMLU (Korean-MMLU)"
aliases:
  - "Korean-MMLU"
  - "k_mmlu"
page_kind: benchmark
category: knowledge
subcategory: "Korean native exam multiple choice across 45 subjects (STEM, HUMSS, applied science, other)"
status: active
summary: "35,030 Korean four-option exam questions across 45 subjects, collected from original Korean tests rather than translated from MMLU."
measures: >
  KMMLU tests expert-level Korean knowledge and reasoning with four-option questions drawn from
  original Korean exams, not machine-translated MMLU. Forty-five subjects span STEM, humanities
  and social science (HUMSS), applied science, and a residual Other bucket. Many items come from
  Korean licence tests, including papers that assume years of industry experience, plus items
  that need Korean cultural, regional, or legal knowledge. The default lm-eval group `kmmlu`
  is the full 45-subject test set scored as multiple-choice log-likelihood. Direct, hard, and
  hard-CoT groups are separate harness variants of the same project, not different ids.
task_format: >
  Four-option multiple choice in Korean. Default yaml: output_type multiple_choice, prompt
  question plus A-D and "정답：", target is answer-1 (0-based index into A-D). test_split is
  test; fewshot_split is dev (five items per subject). The default yaml does not set
  num_fewshot; the paper ran every method five-shot. kmmlu_direct instead generates an option
  and scores exact_match.
metric:
  name: "accuracy (acc); lm-eval group kmmlu is size-weighted micro-average"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25
  human_baseline: 62.6
  baseline_note: >
    Four options give 25% chance on the log-likelihood protocol. Direct generation's chance
    rate is 1/vocab under the paper's description, not 25%. Human 62.6% is the average of
    recorded test-taker accuracy on about 90% of the source exams. The paper also notes that
    many licence exams use an 80% pass mark, which is a professional threshold, not this
    human_baseline. Paper GPT-4 59.95%; best public model in the abstract 50.5% (lm-eval
    README quotes 50.54% and HyperCLOVA X 53.40%). lm-eval defaults to micro-average; the
    README says to take macro-average to match the paper.
dataset:
  size: 35030
  size_note: >
    Hugging Face dataset info splits: test 35,030, dev 225 (45 x 5), train 208,522, total
    243,777 across 45 configs, matching the Hub README table. One sentence in the paper says
    35,050; the paper's own split table is 35,030. Test set is the lowest-human-accuracy slice,
    at least 100 items per subject. KMMLU-HARD is 4,104 test questions that at least one of
    GPT-3.5 Turbo, Gemini Pro, HyperCLOVA X, or GPT-4 missed. The paper does not name the
    protocol for that filter; the lm-eval README says the misses were under log-likelihood.
    Features include Human Accuracy per row.
  url: "https://huggingface.co/datasets/HAERAE-HUB/KMMLU"
  license: "CC-BY-ND-4.0 (Hub card); paper text says CC-BY-ND"
  languages:
    - ko
  modalities:
    - text
  splits: "per-subject configs with train / dev / test; lm-eval default group scores test, few-shot from dev"
  public_test_set: true
publisher:
  org: "HAERAE-HUB (authors at Yonsei, NCSOFT, NAVER Cloud, KAIST, Carnegie Mellon, Contextual AI, EleutherAI)"
  authors:
    - "Guijin Son"
    - "Hanwool Lee"
    - "Sungdong Kim"
    - "Seungone Kim"
    - "Niklas Muennighoff"
    - "Taekyoon Choi"
    - "Cheonbok Park"
    - "Kang Min Yoo"
    - "Stella Biderman"
  url: "https://huggingface.co/datasets/HAERAE-HUB/KMMLU"
paper:
  title: "KMMLU: Measuring Massive Multitask Language Understanding in Korean"
  arxiv: "2402.11548"
  url: "https://arxiv.org/abs/2402.11548"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/kmmlu"
released: "2024-02"
last_updated: "2024-03"
lineage:
  family: ""
  predecessor: "mmlu"
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    At publication GPT-4 scored 59.95%, below the 62.6% human test-taker mean and below the
    80% licence-exam pass mark the authors cite. No later public leaderboard top was opened,
    so top_score is empty.
contamination:
  risk: medium
  note: >
    Items come from real Korean exams and the test split is public on Hugging Face (card
    created 2023-11-27, lastModified 2024-03-05). The paper's Section C reports that tested
    models failed to recall KMMLU, which the authors read as low contamination at release.
harness:
  lm_eval: "kmmlu"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Groups kmmlu_direct, kmmlu_hard, kmmlu_hard_direct, kmmlu_hard_cot; per-subject tasks kmmlu_{subject}."
tags:
  - korean
  - mmlu-style
  - multiple-choice
  - exams
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kmmlu/README.md"
    title: "lm-eval kmmlu README (groups, micro vs macro, abstract scores)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kmmlu/default/_kmmlu_default.yaml"
    title: "group kmmlu (stem/other/applied_science/humss, acc weighted by size)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kmmlu/default/_default_kmmlu_yaml"
    title: "default multiple_choice yaml (HAERAE-HUB/KMMLU, 정답：, no num_fewshot)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kmmlu/default/kmmlu_accounting.yaml"
    title: "kmmlu_accounting (dataset_name Accounting, tag kmmlu_humss_tasks)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kmmlu/direct/_kmmlu_direct.yaml"
    title: "group kmmlu_direct (exact_match, size-weighted)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/kmmlu/hard/_kmmlu_hard.yaml"
    title: "group kmmlu_hard"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/HAERAE-HUB/KMMLU/raw/main/README.md"
    title: "Hub README (35,030 test, 243,777 total, supercategories, CC-BY-ND on card)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/HAERAE-HUB/KMMLU"
    title: "Hub API (license cc-by-nd-4.0, lastModified 2024-03-05)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=HAERAE-HUB/KMMLU"
    title: "dataset info splits (test 35030, dev 225, train 208522)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2402.11548"
    title: "KMMLU paper abs (submitted 18 Feb 2024)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2402.11548"
    title: "KMMLU paper HTML (62.6% human, 59.95% GPT-4, HARD 4104, 5-shot, CC-BY-ND)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-052 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-052"
---

## What it measures

KMMLU is a Korean four-option exam suite built to play the role MMLU plays in English, without translating MMLU. Questions come from Korean licence and academic tests across 45 subjects. The model must pick A-D on Korean stems that often assume local law, history, or trade knowledge. It is not [haerae](haerae.md) (smaller cultural/lexical set), not [click](click.md), not [csatqa](csatqa.md), and not [kormedmcqa](kormedmcqa.md). Default lm-eval `kmmlu` is the full 35,030-item test split.

## How it is scored

The paper evaluates every model five-shot, comparing log-likelihood, direct generation, and CoT. Default lm-eval yaml is multiple_choice `acc`, grouped with size-weighted micro-average. The README says to macro-average subject scores to match the paper. Direct group `kmmlu_direct` uses exact_match on generated letters. The default yaml leaves `num_fewshot` unset, so a bare `lm_eval --tasks kmmlu` is not automatically the paper's 5-shot run. Four-option chance is 25% only on the likelihood protocol.

## Dataset and licence

Test 35,030, dev 225, train 208,522, counted from the Hub dataset-info splits. Authors dropped items that were not four-option, shrinking the raw scrape by 34% to 243,777 rows. KMMLU-HARD (4,104) is the subset at least one of four proprietary models missed. Hub licence tag is CC-BY-ND-4.0; the paper says CC-BY-ND. No-derivatives is stricter than most exam suites in this repository.

## Who publishes it

Guijin Son, Hanwool Lee, Sungdong Kim, Seungone Kim, Niklas Muennighoff, Taekyoon Choi, Cheonbok Park, Kang Min Yoo, Stella Biderman. Dataset under HAERAE-HUB. arXiv 2402.11548, submitted 18 February 2024, revised 6 June 2024. Hub lastModified 5 March 2024.

## Lineage

The design follows [mmlu](mmlu.md) and is compared in the paper to [cmmlu](cmmlu.md). Korean siblings in this repository are HAE-RAE, CLIcK, CSAT-QA, and KorMedMCQA; those are narrower. KMMLU-HARD and the CoT/direct groups are harness variants, not separate pages. [kbl](kbl.md) covers Korean law in more depth than KMMLU's law subjects.

## Saturation and contamination

GPT-4 at 59.95% was still under the 62.6% human mean in the paper, so the original spread was open. Later ceilings were not read. Source exams are public, and the test set has been on the Hub since late 2023 / early 2024. The authors' own recall check argued contamination was limited at release; that check is dated.

## How to run it

`lm_eval --tasks kmmlu` with `num_fewshot 5` if you want the paper protocol, plus a macro-average if you want the paper aggregate. Dataset `HAERAE-HUB/KMMLU`. Other groups: `kmmlu_direct`, `kmmlu_hard`, `kmmlu_hard_direct`, `kmmlu_hard_cot`. Do not compare likelihood `acc` with generative exact_match, or micro with macro, without saying so.

## Reading the numbers

A high KMMLU score means the model ranked the right letter on hard Korean exam items, including licence material. It does not mean the model would pass those licences (authors flag 80% as a human pass mark) and it is not English MMLU. Watch shot count, micro versus macro, and whether HARD was substituted for the full 35k. For Korean culture without professional exams, use HAE-RAE or CLIcK; for Korean law practice, use KBL.
