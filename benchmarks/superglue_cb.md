---
id: superglue_cb
name: "SuperGLUE CB (CommitmentBank)"
aliases:
  - "CB"
  - "CommitmentBank"
  - "SuperGLUE_CB"
page_kind: benchmark
category: reasoning
subcategory: "three-class textual entailment from speaker commitment (SuperGLUE)"
status: saturated
summary: "SuperGLUE's three-class entailment recast of CommitmentBank: 250/56/250 English pairs, scored with accuracy and macro-F1."
measures: >
  SuperGLUE CB asks whether a premise commits its author to a hypothesis extracted from an
  embedded clause. The original CommitmentBank labels how committed a speaker is to that
  clause on a Likert scale. SuperGLUE recasts the items as three-class textual entailment:
  entailment, contradiction, or neutral. Premises come from the Wall Street Journal, British
  National Corpus fiction, and Switchboard. SuperGLUE keeps a subset with inter-annotator
  agreement above 80% and uses its own split. The task is English text, single-turn
  classification, not open-ended generation.
task_format: "Three-way classification: premise plus hypothesis to entailment, contradiction, or neutral; English."
metric:
  name: "accuracy and macro-F1 (unweighted mean of per-class F1); SuperGLUE reports both"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 33.3
  human_baseline: 98.9
  baseline_note: >
    Three-way random guessing is 33.3% accuracy. Official SuperGLUE train labels in the
    public v2 zip are contradiction 119, entailment 115, and neutral 16 of 250, so a
    majority-class accuracy baseline on train is 47.6% if applied unchanged. SuperGLUE
    Table 3 human estimates are 95.8 macro-F1 / 98.9 accuracy on the hidden test set.
    BERT++ in that table scored 84.7 F1 / 90.4 accuracy. OpenCompass AccEvaluator reports
    accuracy only; lm-evaluation-harness's `cb` task reports acc and a multi-class F1.
dataset:
  size: 556
  size_note: >
    Official SuperGLUE v2 CB.zip, counted from the jsonl files: 250 train (labels public),
    56 validation (labels public), 250 test (labels omitted in the file). Hugging Face
    `super_glue` config `cb` matches 250/56/250. SuperGLUE Table 1 lists validation as 57,
    which disagrees with the released files and with the Hugging Face card; this page uses
    56 from the files. The original CommitmentBank has 1,200 discourses; SuperGLUE is a
    high-agreement subset with a SuperGLUE resplit, not the full 1,200.
  url: "https://huggingface.co/datasets/aps/super_glue"
  license: "other"
  languages:
    - en
  modalities:
    - text
  splits: "train 250 / validation 56 / test 250 (test labels withheld in the public files)"
  public_test_set: false
publisher:
  org: "New York University (SuperGLUE); original CommitmentBank from Ohio State / Carnegie Mellon / Ohio State authors"
  authors:
    - "Marie-Catherine de Marneffe"
    - "Mandy Simons"
    - "Judith Tonhauser"
    - "Alex Wang"
    - "Yada Pruksachatkun"
    - "Nikita Nangia"
    - "Amanpreet Singh"
    - "Julian Michael"
    - "Felix Hill"
    - "Omer Levy"
    - "Samuel R. Bowman"
  url: "https://super.gluebenchmark.com/"
paper:
  title: "The CommitmentBank: Investigating projection in naturally occurring discourse"
  arxiv: ""
  url: "https://doi.org/10.18148/sub/2019.v23i2.601"
  year: 2019
leaderboard_url: "https://super.gluebenchmark.com/"
repo_url: "https://github.com/mcdm/CommitmentBank"
released: "2019-05"
last_updated: "2025-05"
lineage:
  family: ""
  predecessor: "glue"
  successors: []
  variants: []
saturation:
  status: saturated
  top_score: null
  as_of: ""
  note: >
    SuperGLUE's own 2019 human estimate is already 98.9% accuracy on 250 hidden test items,
    and the labelled validation split is only 56 examples. No current SuperGLUE leaderboard
    table was recovered from the JavaScript site, so no present-day top score is recorded.
    In practice the task is treated as saturated: harnesses score the tiny public validation
    split, and three-class NLI of this size no longer separates frontier models.
contamination:
  risk: high
  note: >
    Train and validation labels have been public since the 2019 SuperGLUE release. Test
    labels are withheld in CB.zip, but OpenCompass and lm-evaluation-harness score the
    labelled validation file, not the hidden test set. Neutral is rare (16 train, 5
    validation), so memorising the majority of a 56-row file is a realistic contamination
    path.
harness:
  lm_eval: "cb"
  inspect_evals: ""
  helm: ""
  opencompass: "SuperGLUE_CB"
  bigbench: ""
  other: "lm-eval also ships super_glue-cb-t5-prompt; OpenCompass dataset abbr is CB"
tags:
  - nli
  - superglue
  - commitmentbank
  - classification
  - saturated
sources:
  - url: "https://arxiv.org/abs/1905.00537"
    title: "SuperGLUE: A Stickier Benchmark for General-Purpose Language Understanding Systems"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1905.00537"
    title: "SuperGLUE full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://dl.fbaipublicfiles.com/glue/superglue/data/v2/CB.zip"
    title: "Official SuperGLUE v2 CB.zip (250/56/250 jsonl)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/super_glue/resolve/main/README.md"
    title: "Hugging Face super_glue dataset card (redirects to aps/super_glue)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/super_glue"
    title: "Hugging Face dataset API: super_glue renamed to aps/super_glue; cb splits 250/56/250"
    accessed: "2026-09-08"
  - url: "https://github.com/mcdm/CommitmentBank"
    title: "mcdm/CommitmentBank repository README"
    accessed: "2026-09-08"
  - url: "https://doi.org/10.18148/sub/2019.v23i2.601"
    title: "de Marneffe, Simons, Tonhauser, Sinn und Bedeutung 23"
    accessed: "2026-09-08"
  - url: "https://ojs.ub.uni-konstanz.de/sub/index.php/sub/article/view/601"
    title: "CommitmentBank article landing page (CC BY 4.0 on the paper)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/super_glue/cb/default.yaml"
    title: "lm-evaluation-harness cb task YAML"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/super_glue/README.md"
    title: "lm-evaluation-harness SuperGLUE README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/SuperGLUE_CB/SuperGLUE_CB_gen_854c6c.py"
    title: "OpenCompass SuperGLUE_CB generation config"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/cb.py"
    title: "OpenCompass CBDatasetV2 loader"
    accessed: "2026-09-08"
  - url: "https://super.gluebenchmark.com/"
    title: "SuperGLUE homepage (JavaScript app; scores not recovered as static text)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-002 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-002"
---

## What it measures

SuperGLUE CB is a three-class entailment task built from CommitmentBank. Each item is a short English premise that contains an embedded clause, plus a hypothesis that is that clause standing alone. The model must say whether the premise entails the hypothesis, contradicts it, or is neutral. The original resource scored speaker commitment on a seven-point scale. SuperGLUE keeps examples with inter-annotator agreement above 80% and frames the remaining labels as entailment, contradiction, or neutral.

The premises are naturally occurring discourse from news, fiction, and conversation, not crowd-written NLI pairs. Neutral is rare, so the task is easy to game with a two-class strategy unless macro-F1 is reported with accuracy.

## How it is scored

SuperGLUE reports accuracy and macro-F1 (unweighted mean of per-class F1) because the label distribution is skewed. Table 3 of the SuperGLUE paper gives a human estimate of 95.8 F1 / 98.9 accuracy on the hidden test set, and BERT++ at 84.7 / 90.4. Three-way chance is 33.3% accuracy. In the released train file, contradiction is 119 of 250 labels.

OpenCompass `SuperGLUE_CB` generation configs score accuracy only, with options A/B/C mapped from contradiction/entailment/neutral, on `val.jsonl` (56 labelled rows). Perplexity configs also read that validation file. lm-evaluation-harness task `cb` (tag `super-glue-lm-eval-v1`) loads `aps/super_glue` config `cb`, uses the validation split, and reports acc plus a custom F1. A separate `super_glue-cb-t5-prompt` task matches T5-style prompts. Those harness numbers are not SuperGLUE test-server scores.

## Dataset and licence

The public SuperGLUE v2 zip contains 250 train, 56 validation, and 250 test rows. Test jsonl has `premise`, `hypothesis`, and `idx` but no `label`. Hugging Face `aps/super_glue` config `cb` repeats 250/56/250 (the older `super_glue` id now redirects there). SuperGLUE Table 1's validation count of 57 does not match the files. The parent CommitmentBank has 1,200 discourses; SuperGLUE is a subset. The Hugging Face card lists licence `other` and says each SuperGLUE task keeps its original licence, understood to allow research redistribution. The Sinn und Bedeutung paper is CC BY 4.0; the GitHub data README does not add a separate SPDX id.

## Who publishes it

CommitmentBank is by Marie-Catherine de Marneffe, Mandy Simons, and Judith Tonhauser, *Proceedings of Sinn und Bedeutung* 23, 2019 (doi:10.18148/sub/2019.v23i2.601). Data live at `mcdm/CommitmentBank`. SuperGLUE, by Wang, Pruksachatkun, Nangia, Singh, Michael, Hill, Levy, and Bowman (arXiv:1905.00537; NeurIPS 2019), defined the three-class split and the public leaderboard at super.gluebenchmark.com. This OpenCompass/census id is SuperGLUE's CB, not the full 1,200-item resource.

## Lineage

GLUE (`glue.md`) is the predecessor suite; SuperGLUE replaced it with harder, smaller tasks, and this repository has no SuperGLUE family page yet. `boolq.md` is another SuperGLUE task already documented here. `anli.md` is a later three-class NLI benchmark with a different item-writing process, not a CB successor. SuperGLUE's paper notes that CB was resplit relative to the original resource.

## Saturation and contamination

Human accuracy of 98.9% on 250 test items, and a 56-row public validation file that harnesses actually score, leave almost no ranking headroom. Contamination risk is high: labels for the scored split have been public since 2019, and the class prior is sharp. A current model that reports 100% OpenCompass CB accuracy has solved 56 known items, not the hidden SuperGLUE test set.

## How to run it

OpenCompass: configs under `opencompass/configs/datasets/SuperGLUE_CB/` (generation and PPL). Dataset abbr `CB`; loaders `CBDatasetV2` / `HFDataset` on `./data/SuperGLUE/CB/val.jsonl`. lm-evaluation-harness: `--tasks cb` or `super_glue-cb-t5-prompt`. Official SuperGLUE test numbers require the SuperGLUE evaluation server; the public test file has no labels. inspect_evals and HELM have no CB scenario in the sources opened for this page. Prompt wording differs (True/False/Neither vs Contradiction/Entailment/Neutral vs T5 prefixes), so compare only matching harness configs.

## Reading the numbers

A high CB score today mostly shows that a model can do three-class NLI on a handful of public SuperGLUE items. It does not show robust commitment or presupposition reasoning, and it does not match SuperGLUE's hidden-test protocol unless the reporter submitted to the official server. Always check whether the number is accuracy, macro-F1, or both, and whether it is validation or test. Pair CB with a larger NLI set such as `anli` before treating the figure as evidence of inference skill.
