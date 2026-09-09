---
id: clue
name: "CLUE (Chinese Language Understanding Evaluation)"
aliases:
  - "Chinese Language Understanding Evaluation Benchmark"
  - "ChineseGLUE"
page_kind: family
category: composite
subcategory: "Chinese multi-task language understanding suite (classification, natural language inference, machine reading comprehension)"
status: active
summary: "A nine-task Chinese counterpart to GLUE/SuperGLUE spanning classification, NLI and reading comprehension; its own composite leaderboard has matched or beaten its human baseline since 2023."
measures: >
  CLUE bundles several separately-scored Chinese natural-language-understanding tasks under one
  suite and one submission leaderboard: single-sentence and sentence-pair classification (news and
  app-description topic classification, semantic similarity, pronoun coreference, keyword-abstract
  matching), three-way natural language inference, and machine reading comprehension (span
  extraction, idiom cloze, free-form multiple choice). The paper itself counts nine core tasks. The
  project separately distributes further datasets under the same CLUE umbrella and downloads page,
  including two -- CMNLI and DRCD -- that are documented in this repository as clue_cmnli and
  clue_drcd but sit outside both the paper's nine and, for DRCD, the live scored leaderboard.
task_format: >
  Varies by component task: binary or multi-way classification scored by accuracy; three-way
  natural language inference scored by accuracy; reading comprehension scored by exact match/F1
  (span extraction) or accuracy (multiple choice). CLUE reports one blended "Score" per leaderboard
  submission, averaged across whichever task set that leaderboard revision scores.
metric:
  name: "accuracy / EM / F1 per component task, averaged into one composite Score"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  human_baseline: 86.678
  baseline_note: >
    86.678 is the CLUE team's own "HUMAN" row on the live CLUE1.1 leaderboard (dated 2019-12-01,
    read 2026-09-08), a composite over AFQMC, TNEWS, IFLYTEK, OCNLI_50K, WSC1.1, CSL, CMRC2018,
    CHID1.1 and C3 1.1. Per-task random baselines differ too widely (roughly 50% for binary tasks,
    33% for three-way NLI, near 0% for open-vocabulary span extraction) to average into one figure.
dataset:
  size: null
  size_note: >
    No single item count applies to the family; each component task has its own size. See this
    batch's own subset pages (clue_afqmc, clue_cmnli, clue_cmrc, clue_drcd, clue_ocnli) and, for
    tasks not yet paged here (TNEWS, IFLYTEK, CLUEWSC2020, CSL, ChID), the CLUE GitHub README.
  url: "https://github.com/CLUEbenchmark/CLUE"
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "varies by task; every component task read for this batch withholds real test-set answers"
  public_test_set: false
publisher:
  org: "CLUE benchmark community project (CLUEbenchmark on GitHub and cluebenchmarks.com); first released under the name ChineseGLUE"
  authors:
    - "Liang Xu"
    - "Hai Hu"
    - "Xuanwei Zhang"
    - "Lu Li"
    - "Chenjie Cao"
    - "Yudong Li"
    - "Yechen Xu"
    - "Kai Sun"
    - "Dian Yu"
    - "Cong Yu"
    - "Yin Tian"
    - "Qianqian Dong"
    - "Weitang Liu"
    - "Bo Shi"
    - "Yiming Cui"
    - "Junyi Li"
    - "Jun Zeng"
    - "Rongzhao Wang"
    - "Weijian Xie"
    - "Yanting Li"
    - "Yina Patterson"
    - "Zuoyu Tian"
    - "Yiwen Zhang"
    - "He Zhou"
    - "Shaoweihua Liu"
    - "Zhe Zhao"
    - "Qipeng Zhao"
    - "Cong Yue"
    - "Xinrui Zhang"
    - "Zhengliang Yang"
    - "Kyle Richardson"
    - "Zhenzhong Lan"
  url: "https://github.com/CLUEbenchmark"
paper:
  title: "CLUE: A Chinese Language Understanding Evaluation Benchmark"
  arxiv: "2004.05986"
  url: "https://arxiv.org/abs/2004.05986"
  year: 2020
leaderboard_url: "https://www.cluebenchmarks.com/rank.html"
repo_url: "https://github.com/CLUEbenchmark/CLUE"
released: "2019-11"
last_updated: "2023-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: 87.05
  as_of: "2023-07"
  note: >
    The live CLUE1.1 leaderboard's top entry (NetEase Fuxi's "Yuyan", dated 2023-07-31, read
    2026-09-08) scores 87.050 on the composite Score, above the CLUE team's own 86.678 human
    baseline (dated 2019-12-01). Among the top 20 rows read, every date falls in 2021-2023; none is
    dated 2024 or later, and cluebenchmarks.com's own homepage now promotes SuperCLUE, a separate
    foundation-model benchmark from the same team, rather than this leaderboard.
contamination:
  risk: high
  note: >
    Every component task read for this batch publishes real training and development labels; only
    each task's own held-out test split is withheld, submitted for scoring rather than downloaded.
    OpenCompass, the harness that carries every task in this batch, scores the public development
    split by default (abbreviated afqmc-dev, cmnli-dev, OCNLI-dev, cmrc_dev, drcd_dev) rather than
    submitting to CLUE's withheld test set, so most numbers a paper reports for these tasks were
    computed on data that has been public with real answers since 2019-2020.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "CLUE_<task> (one dataset-config directory per task, e.g. CLUE_afqmc, CLUE_cmnli, CLUE_CMRC, CLUE_DRCD, CLUE_ocnli, CLUE_C3; each with gen and, for most tasks, ppl config variants)"
  bigbench: ""
  other: ""
tags:
  - chinese
  - nlu
  - classification
  - natural-language-inference
  - reading-comprehension
  - composite
sources:
  - url: "https://arxiv.org/abs/2004.05986"
    title: "CLUE: A Chinese Language Understanding Evaluation Benchmark (Xu et al., arXiv:2004.05986)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2004.05986"
    title: "CLUE paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2020.coling-main.419/"
    title: "CLUE: A Chinese Language Understanding Evaluation Benchmark, ACL Anthology (COLING 2020)"
    accessed: "2026-09-08"
  - url: "https://github.com/CLUEbenchmark/CLUE"
    title: "CLUEbenchmark/CLUE GitHub repository (README)"
    accessed: "2026-09-08"
  - url: "https://github.com/CLUEbenchmark"
    title: "CLUEbenchmark GitHub organisation (repository listing)"
    accessed: "2026-09-08"
  - url: "https://www.cluebenchmarks.com/rank.html"
    title: "CLUE1.1 leaderboard, cluebenchmarks.com (fetched via scripts/benchmarks/fetch.py)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/clue/clue"
    title: "clue/clue dataset metadata, Hugging Face API"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/splits?dataset=clue%2Fclue"
    title: "clue/clue split counts, Hugging Face datasets-server"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/CLUE_afqmc"
    title: "OpenCompass CLUE_afqmc dataset configs (representative of the CLUE_<task> config family)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice A"
---

## What it measures

CLUE gives a model several distinct Chinese-language understanding tasks under one suite: single
sentences or sentence pairs to classify (news topics, long app descriptions, semantic similarity,
pronoun coreference, paper keyword-abstract matching), sentence pairs to judge for entailment,
neutrality or contradiction, and passages to answer questions about, either by extracting a text
span or by picking a free-form multiple-choice option. The paper frames this explicitly as filling
for Chinese the gap GLUE and SuperGLUE filled for English.

The published paper counts nine core tasks. CLUE's GitHub release additionally distributes CMNLI
and DRCD, an older NLI task and a Traditional-Chinese reading-comprehension task, both documented
here (clue_cmnli, clue_drcd) but absent from the paper's nine and, for DRCD, from the live
leaderboard entirely.

## How it is scored

Each component task uses its own metric -- accuracy for classification and NLI, exact match or F1
for span extraction, accuracy for multiple choice -- and CLUE averages whichever tasks a given
leaderboard revision scores into one composite "Score." The current CLUE1.1 leaderboard scores nine
columns (AFQMC, TNEWS, IFLYTEK, OCNLI_50K, WSC, CSL, CMRC2018, CHID, C3); CMNLI and DRCD are not
among them. Submission means predicting each task's held-out test split and uploading to
cluebenchmarks.com; the CLUE team supplies one reference "HUMAN" row rather than independently
validating every submitted number.

## Dataset and licence

Sizes range from CLUEWSC2020's roughly 1,500 examples to CMNLI's several hundred thousand
translated sentence pairs; see each task's own page for exact counts. No licence is stated for the
suite as a whole: the GitHub repository carries no LICENSE file (confirmed via the GitHub API) and
the Hugging Face mirror's dataset card tags its licence "unknown." Component tasks adopted from
elsewhere may carry their own stated licence -- see clue_cmrc and clue_c3.

## Who publishes it

CLUE comes from a 32-author community collaboration led by Liang Xu and Hai Hu, first released as
ChineseGLUE via the CLUEbenchmark GitHub organisation (repository created November 2019, human
baseline dated December 2019) and formally published as "CLUE: A Chinese Language Understanding
Evaluation Benchmark" at COLING 2020. Several co-authors also authored individual component tasks
later adopted into the suite: Yiming Cui (CMRC2018), Kai Sun and Dian Yu (C3), and Hai Hu, Kyle
Richardson and Lu Li (OCNLI). The same organisation now promotes SuperCLUE, a separate
foundation-model benchmark, more prominently than this original leaderboard.

## Lineage

CLUE has no predecessor here; its authors cite GLUE and SuperGLUE as the English-language model it
adapts for Chinese. Six component tasks are subset pages carrying `lineage.family: clue`:
clue_afqmc, clue_c3, clue_cmnli, clue_cmrc, clue_drcd and clue_ocnli. Adoption varies by task: OCNLI
was built from scratch for CLUE, then given its own EMNLP Findings 2020 paper. CMRC2018, DRCD and C3
were each adopted wholesale from separately published datasets -- CMRC2018 and C3 with their
original authors co-authoring the CLUE paper; DRCD from a separate team with no author overlap.
CMNLI was assembled by the CLUE team itself, machine-translating MultiNLI and XNLI into Chinese,
then formally replaced by OCNLI on the leaderboard from the 1.1 revision onward (the README states
this plainly). AFQMC repackages a 2018 Ant Financial competition dataset with no paper of its own.
TNEWS, IFLYTEK, CLUEWSC2020, CSL and ChID are further tasks without pages in this batch. CLUE also
underlies FewCLUE and ZeroCLUE (few-shot and zero-shot variants), hosted under the same organisation
without their own pages here yet. CLUE is not a predecessor of this repository's other Chinese
benchmarks -- CMMLU (`cmmlu`, 2023-06), C-Eval (`ceval`, 2023-05) and Chinese SimpleQA
(`chinese_simpleqa`, 2024-11) -- but a distinct, earlier sibling: those three test broad academic
knowledge or short-answer factuality with MMLU/SimpleQA-style formats built for the LLM era, while
CLUE tests classification, inference and reading comprehension in formats built three to five years
earlier for BERT-era encoders, and none reuses CLUE's data or task design.

## Saturation and contamination

The composite leaderboard reads as saturated: the top entry (87.050, NetEase Fuxi, 2023-07-31) sits
above the CLUE team's own 86.678 human baseline (2019-12-01), and no row among the top 20 read here
is dated later than mid-2023, consistent with the publisher's promotional shift toward SuperCLUE.
Contamination risk is high: every component task's training and development data has been public
with real labels since 2019-2020, and OpenCompass -- the harness carrying all six of this batch's
tasks -- scores the public development split by default rather than submitting to CLUE's withheld
test set, so most numbers a current paper reports never touch CLUE's held-out answers at all.

## How to run it

OpenCompass ships each task as its own `CLUE_<task>` config directory (CLUE_afqmc, CLUE_cmnli,
CLUE_CMRC, CLUE_DRCD, CLUE_ocnli, CLUE_C3), each with a generative (`_gen`) config and, for most
tasks, a perplexity-based (`_ppl`) config; several load a dataset OpenCompass mirrors under its own
`opencompass` Hugging Face organisation rather than CLUE's release. No lm-evaluation-harness,
inspect_evals or HELM implementation was found under this name (harness's similarly-named `aclue`
is an unrelated Ancient Chinese benchmark). Original baselines and the submission format live in the
CLUEbenchmark/CLUE repository.

## Reading the numbers

A strong CLUE composite score signals broad Chinese sentence- and passage-level understanding
across several classic task types, largely as BERT-era encoder models understood them -- the
leaderboard's active period (2019-2023) and its top submissions (in-house pretrained encoders, not
general chat or reasoning LLMs) both predate most of today's frontier releases. Because most
reported numbers are computed on each task's public development split rather than CLUE's withheld
test set, treat a CLUE score as a contamination-exposed sanity check on basic Chinese NLU rather
than a clean held-out measurement. Always check which component tasks a reported "CLUE" number
actually averages, since the scored task set changed between the 1.0 and 1.1 revisions.
