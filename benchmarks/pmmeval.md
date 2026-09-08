---
id: pmmeval
name: "P-MMEval"
aliases:
  - "PMMEval"
  - "P MMEval"
page_kind: benchmark
category: composite
subcategory: "parallel multilingual suite: translation, NLI, commonsense, code, math, logic, knowledge, instruction following"
status: active
summary: "A Qwen/Tongyi parallel multilingual suite that extends eight existing tasks across the same ten languages so cross-lingual gaps are not confounded with different item sets."
measures: >
  P-MMEval (Parallel Multilingual Multitask Evaluation) scores the same underlying items in up
  to ten languages: English, Chinese, Arabic, Spanish, French, Japanese, Korean, Portuguese,
  Thai and Vietnamese. The paper body says those ten span seven language families; the Hub
  card says eight. Where a source benchmark lacked a language, the authors add expert-reviewed
  translations so coverage is consistent and samples are parallel. The eight source tasks mix
  generation (FLORES-200 English-to-X, HumanEval-XL) with understanding and specialised skills
  (XNLI, MHellaSwag, MGSM, MLogiQA, MMMLU, MIFEval).
task_format: >
  Varies by task: free-text translation (FLORES), code generation (HumanEval-XL), numeric or
  short-answer math (MGSM), four-option multiple choice (MLogiQA, MMMLU, MHellaSwag), three-way
  NLI (XNLI), and instruction-following checks (MIFEval). OpenCompass runs each language as its
  own generate-until task under the pmmeval_gen umbrella.
metric:
  name: "task-dependent: BLEU (FLORES), pass@1 (HumanEval-XL), accuracy (XNLI, MHellaSwag, MGSM, MLogiQA, MMMLU, MIFEval)"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single random or human baseline covers the suite. Multiple-choice constituents have
    their own option counts; FLORES is a continuous BLEU; HumanEval-XL is pass@1. The paper
    compares model series across tasks and languages rather than one official suite average.
dataset:
  size: null
  size_note: >
    Hugging Face datasets-server reports 19,749 rows across seven configs that loaded:
    FLORES 9,108, MGSM 2,500, MHellaSwag 1,181, MIFEval 960, MLogiQA 800, MMMLU 4,000
    (easy 2,000 + hard 2,000), XNLI 1,200. The card also declares a humaneval-xl config
    (12 programming-language splits) that the size endpoint did not include in that total.
    Paper Table 1 counts per language: FLORES 1,012 x 10, XNLI 120 x 10, MHellaSwag 120 x 10,
    HumanEval-XL 80 x 10 x 12, MGSM 250 x 10, MLogiQA 80 x 10, MMMLU 400 x 10, MIFEval 96 x 10.
    OpenCompass FLORES runs nine target languages (English is the source, not a target),
    which matches 1,012 x 9 = 9,108 and disagrees with the paper's "x 10" FLORES column.
    MHellaSwag is 1,181 on the Hub versus 1,200 implied by 120 x 10. Size is left empty
    rather than picking one of those conventions.
  url: "https://huggingface.co/datasets/Qwen/P-MMEval"
  license: "Apache-2.0"
  languages:
    - en
    - zh
    - ar
    - es
    - fr
    - ja
    - ko
    - pt
    - th
    - vi
  modalities:
    - text
    - code
  splits: >
    Mostly a single test split per config; MMMLU is split into easy and hard (2,000 rows
    each). HumanEval-XL uses per-programming-language splits.
  public_test_set: true
publisher:
  org: "Tongyi Lab, Alibaba Group"
  authors:
    - "Yidan Zhang"
    - "Yu Wan"
    - "Boyi Deng"
    - "Baosong Yang"
    - "Haoran Wei"
    - "Fei Huang"
    - "Bowen Yu"
    - "Junyang Lin"
    - "Fei Huang"
    - "Jingren Zhou"
  url: "https://huggingface.co/datasets/Qwen/P-MMEval"
paper:
  title: "P-MMEval: A Parallel Multilingual Multitask Benchmark for Consistent Evaluation of LLMs"
  arxiv: "2411.09116"
  url: "https://arxiv.org/abs/2411.09116"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/PMMEval"
released: "2024-11"
last_updated: "2025-05"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: "2024-11"
  note: >
    The introducing paper compares Qwen, Gemma, LLaMA and closed-source series and reports
    that multilingual scores generally rise with size, with task- and language-dependent
    gaps remaining. No maintained public leaderboard with one confirmed suite-wide top
    score was found, so top_score is empty.
contamination:
  risk: medium
  note: >
    Several source sets (FLORES, XNLI, MGSM, HumanEval-family, MMLU translations) have been
    public for years and are widely mirrored. Newly translated parallel slices are newer.
    Answers are public on Hugging Face. No suite-wide contamination study was found.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: >
    pmmeval_gen umbrella; summarizer groups flores-*, humanevalxl-{python,java,javascript}-*,
    mgsm-*, mhellaswag-*, mifeval-*, mlogiqa-*, mmmlu-* (OpenAI-style language codes),
    xnli-*. Example: opencompass --datasets pmmeval_gen
  bigbench: ""
  other: >
    Official Hugging Face card recommends OpenCompass (optionally with vLLM). No
    lm-evaluation-harness group named pmmeval was found. Constituent English tasks exist
    separately in this repository under their own ids.
tags:
  - multilingual
  - composite
  - translation
  - code
  - math
  - instruction-following
sources:
  - url: "https://arxiv.org/abs/2411.09116"
    title: "P-MMEval arXiv abs (submitted 14 Nov 2024)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2411.09116"
    title: "P-MMEval paper full text (ar5iv), including Table 1 counts"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Qwen/P-MMEval/raw/main/README.md"
    title: "Qwen/P-MMEval dataset card"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/Qwen/P-MMEval"
    title: "Qwen/P-MMEval Hugging Face API (Apache-2.0, ten languages)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/size?dataset=Qwen/P-MMEval"
    title: "Qwen/P-MMEval datasets-server size (19,749 rows in seven configs)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/PMMEval/pmmeval_gen.py"
    title: "OpenCompass pmmeval_gen.py umbrella import"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/summarizers/groups/PMMEval.py"
    title: "OpenCompass P-MMEval summarizer language and task groups"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/PMMEval/flores_gen_2697d7.py"
    title: "OpenCompass P-MMEval FLORES config (nine target languages)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/PMMEval/humanevalxl_gen_bdec92.py"
    title: "OpenCompass P-MMEval HumanEval-XL config (python/java/javascript x 10 languages)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/examples/eval_PMMEval.py"
    title: "OpenCompass examples/eval_PMMEval.py"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-019 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-019"
---

## What it measures

P-MMEval is a parallel multilingual suite from Tongyi Lab. It does not invent eight new tasks. It takes existing benchmarks, keeps language coverage aligned, and adds expert-reviewed translations where a language was missing, so a drop from English to Thai is not an artefact of different questions. The ten languages are English, Chinese, Arabic, Spanish, French, Japanese, Korean, Portuguese, Thai and Vietnamese. The paper body counts seven language families for that set; the Hugging Face card counts eight.

The eight sources, from the paper's Table 1, are FLORES-200 (English-to-X translation), XNLI, MHellaSwag, HumanEval-XL (natural-language prompts into code), MGSM, MLogiQA, MMMLU and MIFEval (instruction following, adapted from IFEval). OpenCompass implements all eight under `pmmeval_gen`.

## How it is scored

Scoring follows each source. FLORES uses BLEU. HumanEval-XL uses pass@1. The understanding and exam-style tasks use accuracy. There is no official one-number suite metric in the paper; OpenCompass instead defines per-task summarizer groups (for example `mgsm-en` … `mgsm-vi`). MMMLU inside P-MMEval is a 400-item-per-language slice with easy and hard splits, not the full 14-language OpenAI MMMLU dump. OpenCompass HumanEval-XL runs only Python, Java and JavaScript, not the twelve programming languages named in the paper.

## Dataset and licence

The Hugging Face dataset `Qwen/P-MMEval` is Apache-2.0. Datasets-server counted 19,749 rows in seven configs; the card also lists `humaneval-xl`, which that size call did not add in. Paper Table 1 and the Hub disagree on two points worth keeping: FLORES is 1,012 × 10 in the table but 9,108 rows on the Hub, matching OpenCompass's nine translation targets (English is source-only); MHellaSwag is 120 × 10 in the table versus 1,181 Hub rows. Gold labels are public.

## Who publishes it

Yidan Zhang, Yu Wan (corresponding), Boyi Deng, Baosong Yang, Haoran Wei, Fei Huang, Bowen Yu, Junyang Lin, Fei Huang and Jingren Zhou, Tongyi Lab, Alibaba Group. Zhang and Deng's work is noted as an internship. arXiv v1 is 14 November 2024 (v2 14 May 2025). The dataset card points evaluators at OpenCompass rather than a standalone leaderboard.

## Lineage

P-MMEval is not a rename of [MMMLU](mmmlu.md), [MGSM](mgsm.md), [FLORES](flores.md), [IFEval](ifeval.md), [HumanEval](humaneval.md), [HumanEval-X](humanevalx.md) or [HellaSwag](hellaswag.md). Those remain the source evaluations; this suite is a parallel, ten-language overlay with extra translated items. [PortugueseBench](portuguese_bench.md) also uses FLORES and Belebele, but for European Portuguese only and under IberoBench, not this Qwen suite.

## Saturation and contamination

The paper's own runs still separate model families and sizes, with remaining language gaps, but this page found no maintained leaderboard, so saturation is unknown and top_score is empty. Contamination risk is medium: FLORES, XNLI, MGSM and MMLU-family items are old and public; the newly translated parallel slices are newer. Nothing is held out.

## How to run it

The Hugging Face card's recipe is `opencompass --models … --datasets pmmeval_gen` (vLLM optional) or `opencompass ./configs/eval_PMMEval.py`. Task abbreviations follow `flores-Chinese`, `mgsm-en`, `mmmlu-EN-US`, `humanevalxl-python-English`, and the other groups in `configs/summarizers/groups/PMMEval.py`. No lm-eval group named `pmmeval` was found. A reporter must say which of the eight tasks, which languages, and for code which programming languages, because OpenCompass's default HumanEval-XL cut is three languages of code, not twelve.

## Reading the numbers

A strong P-MMEval showing means the model keeps competence when the same items move out of English, not that it mastered eight unrelated skills from scratch. Do not treat a P-MMEval MMMLU slice as OpenAI MMMLU, or P-MMEval HumanEval-XL as [HumanEval](humaneval.md) / [HumanEval-X](humanevalx.md). Watch the FLORES language count (nine OpenCompass targets versus ten in Table 1) before averaging translation with the rest.
