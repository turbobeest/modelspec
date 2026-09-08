---
id: aime
name: "AIME (American Invitational Mathematics Examination)"
aliases:
  - "American Invitational Mathematics Examination"
  - "AIME 1983-2024"
page_kind: family
category: math
subcategory: "competition mathematics, exact integer answers (historical pack and yearly sittings)"
status: active
summary: "The American Invitational Mathematics Examination as an LLM test: exact integer answers to contest problems, packaged as a 1983–2024 historical set and as yearly 30-problem sittings."
measures: >
  AIME is a US/Canada invitational math contest. Each sitting has 15 problems
  and a three-hour limit. Every official answer is an integer from 0 to 999.
  Language-model evals reuse those problems as free-response reasoning tests:
  the model must output the integer, with no multiple-choice list and no
  partial credit. This family page covers that shared format. lm-evaluation-harness
  task `aime` is specifically the 1983–2024 historical pack
  (`gneubig/aime-1983-2024`). Tasks `aime24` and `aime25`, and this repository's
  `aime_2024`, `aime_2025`, and `aime_2026` pages, are single-year 30-problem
  sittings (AIME I and II).
task_format: >
  Free-response contest problem in, single integer 0–999 out. lm_eval extracts a
  boxed or dollar-delimited answer and scores exact match after light TeX
  normalisation, greedy decoding, up to 32,768 generated tokens.
metric:
  name: "exact_match / pass@1 accuracy on the final integer"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    There is no useful random baseline: the answer is any integer 0–999. Human
    contest scores are not a published LLM-eval baseline on these packs.
    Yearly-sitting pages record model numbers (for example OpenAI o1 on AIME
    2024); this family page does not copy those as a family-wide baseline.
dataset:
  size: 933
  size_note: >
    Hugging Face datasets-server reports 933 rows in gneubig/aime-1983-2024
    (single train split; lm_eval uses that split as the test set). The same
    card's README claims 2,250 problems; the API size_categories tag is n<1K
    while cardData says 1K<n<10K. This page uses 933 as the count of rows the
    harness actually loads, and treats 2,250 as an unresolved card claim.
    Each yearly sitting used as an LLM test has 30 problems (15+15).
  url: "https://huggingface.co/datasets/gneubig/aime-1983-2024"
  license: CC0-1.0
  languages:
    - en
  modalities:
    - text
  splits: "historical pack: one train split of 933 rows, scored in full by lm_eval. Yearly sittings: 30-row test sets, no train split"
  public_test_set: true
publisher:
  org: "Mathematical Association of America (exam); LLM packs by Hemish Veeraboina / Graham Neubig (1983–2024), Maxwell Jia (2024), math-ai (2025)"
  authors: []
  url: "https://huggingface.co/datasets/gneubig/aime-1983-2024"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://matharena.ai/"
repo_url: ""
released: "2024"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants:
    - aime_2024
    - aime_2025
    - aime_2026
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: >
    Saturation depends on the sitting. AIME 2024 is already treated as saturated
    on this repository's aime_2024 page. AIME 2025 is on watch. AIME 2026 was
    still listed without a confirmed ceiling when that page was written. The
    1983–2024 historical pack is older public contest material and should be
    assumed easier to memorise than a fresh sitting. No single family-wide top
    score is recorded here.
contamination:
  risk: high
  note: >
    Official answers and worked solutions for past AIME contests are public
    (contest archives, community wikis, and the machine-readable packs). The
    1983–2024 mix is the most exposed. Newer sittings start cleaner and then
    age. BeyondAIME (`beyondaime`) is a different, harder set, not this family.
harness:
  lm_eval: aime
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "lm_eval also ships aime24 and aime25; inspect_evals and OpenCompass ship yearly ids such as aime_2024"
tags:
  - math
  - competition-math
  - exact-match
  - family
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/aime/README.md"
    title: "lm-evaluation-harness AIME README (aime / aime24 / aime25)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/aime/aime.yaml"
    title: "lm_eval task aime (gneubig/aime-1983-2024)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/aime/aime24.yaml"
    title: "lm_eval task aime24"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/aime/aime25.yaml"
    title: "lm_eval task aime25"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/gneubig/aime-1983-2024"
    title: "gneubig/aime-1983-2024 dataset card"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=gneubig/aime-1983-2024"
    title: "datasets-server row count for gneubig/aime-1983-2024"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/gneubig/aime-1983-2024"
    title: "Hugging Face dataset API for gneubig/aime-1983-2024"
    accessed: "2026-09-08"
  - url: "https://matharena.ai/"
    title: "MathArena live competitions (AIME 2025 and AIME 2026 listed; AIME 2024 not listed)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-024 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-024"
---

## What it measures

AIME problems are invitational high-school contest items in algebra, geometry, number theory, and combinatorics. Each problem has one integer answer between 0 and 999. As an LLM benchmark, that format is a strict reasoning test: the derivation can be long, but only the integer counts.

This id is the family name. It is not a fourth yearly sitting. lm_eval's task `aime` loads a 1983–2024 dump. `aime24` / `aime_2024` and `aime25` / `aime_2025` are the 30 problems from those years. `aime_2026` is the 2026 pair of sittings. Do not average a 933-row historical run with a 30-row sitting and call both "AIME".

## How it is scored

lm_eval uses greedy generation (`temperature: 0.0`, `max_gen_toks: 32768`) and `exact_match` after pulling a `\\boxed{}` or `$...$` span and normalising TeX the way Hendrycks MATH does. Yearly reporters often instead quote pass@1 or cons@k on 30 items, sometimes with a Python tool. Those protocols are not the same number. There is no random baseline.

## Dataset and licence

The historical pack lm_eval calls `aime` is `gneubig/aime-1983-2024`, compiled from Hemish Veeraboina's Kaggle set and released as CC0-1.0. datasets-server lists 933 train rows; the card README says 2,250 problems. This page records 933 as the loaded size and flags 2,250 as a disagreement. Yearly mirrors (`Maxwell-Jia/AIME_2024`, `math-ai/aime25`) are separate transcriptions, often Apache-2.0 or MIT for the packaging, while the contest itself is an MAA exam. The MAA invitational page returned HTTP 403 in this session, so contest-administration details are taken from the dataset cards rather than from maa.org.

## Who publishes it

The contest is the Mathematical Association of America's. No single lab owns the LLM eval. Graham Neubig's Hugging Face dump is what `lm_eval --tasks aime` runs. Maxwell Jia and math-ai maintain yearly dumps. MathArena's live board, when opened for this page, listed AIME 2025 and AIME 2026 among final-answer contests and did not list AIME 2024 or the 1983–2024 pack.

## Lineage

Yearly pages in this repository: `aime_2024`, `aime_2025`, `aime_2026`. `beyondaime` is a different, harder contest-style set, not a sitting of AIME. GSM8K and MATH sit well below this difficulty. USAMO is a proof contest, not this integer format.

## Saturation and contamination

Read saturation on the yearly page, not as one family number. AIME 2024 is already a weak discriminator among reasoning models. The 1983–2024 mix is public contest lore and is high contamination risk. A fresh sitting is more informative until its answers have been on the web for a training cycle.

## How to run it

`lm_eval --tasks aime` is the historical pack (all 933 rows as the test set). `aime24` and `aime25` are the yearly YAML files in the same directory. inspect_evals and OpenCompass use underscored yearly names such as `aime_2024`. Always name the year or the pack, the sample count, and whether tools were allowed.

## Reading the numbers

A high score on `aime` (1983–2024) mostly says the model can emit AIME-style integers on a large public archive, including many years of leaked solutions. A high score on `aime_2026` is a stronger claim about current contest math, and still not a proof contest. Never compare a 933-item greedy exact-match run with a 30-item cons@64 sitting, and never treat "AIME" in a model card as this family unless the card names the year or the pack.
