---
id: fewclue_chid
name: "FewCLUE: CHID (Chinese Idiom Cloze Test)"
page_kind: subset
category: reasoning
subcategory: "Chinese idiom cloze test (multiple-choice fill-in-the-blank), few-shot"
status: unknown
summary: "FewCLUE's Chinese idiom cloze task: pick the idiom that fits a masked slot from seven near-synonym candidates, learned from 42 labelled training examples."
measures: >
  A Chinese passage with one blank marked #idiom# and seven candidate idioms, several chosen as
  near-synonyms of the correct answer to block shallow pattern matching; the model selects the idiom
  that fits the context, learned few-shot from 42 labelled training examples.
task_format: >
  Seven-way multiple-choice cloze, graded on the single correct candidate; evaluated from a
  42-example few-shot training split (six examples for each of the seven blank positions), one of
  five parallel splits FewCLUE provides for this task.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 14.3
  human_baseline: 87.1
  baseline_note: >
    14.3% is the paper's majority-class baseline, matching the seven-way random-guess rate. See the
    fewclue family page for the top overall few-shot method scores.
dataset:
  size: 2002
  size_note: >
    2,002 labelled public test items (test_public.json, used for scoring), plus 2,000 in the private
    test set (original leaderboard only), 42 train and 42 dev examples per split (5 parallel splits,
    train_0..train_4 / dev_0..dev_4, plus a merged train_few_all/dev_few_all), and 7,585 unlabelled
    items not used for scoring. Figures from the FewCLUE paper's Table 1, matching the GitHub README.
    The underlying idiom-cloze format and its 3,848-idiom candidate pool originate in ChID (Zheng et
    al. 2019, arXiv:1906.01265), sampled here from news, novels and essays.
  url: "https://github.com/CLUEbenchmark/FewCLUE/tree/main/datasets/chid"
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "train_0..train_4 (42 each) + train_few_all; dev_0..dev_4 (42 each) + dev_few_all; test_public (2,002, labelled); test (2,000, private); unlabeled (7,585)"
  public_test_set: true
publisher:
  org: "CLUE team"
  authors:
    - "Liang Xu"
    - "Xiaojing Lu"
    - "Chenyang Yuan"
    - "Xuanwei Zhang"
    - "Huilin Xu"
    - "Hu Yuan"
    - "Guoao Wei"
    - "Xiang Pan"
    - "Xin Tian"
    - "Libo Qin"
    - "Hu Hai"
  url: "https://github.com/CLUEbenchmark/FewCLUE"
paper:
  title: "FewCLUE: A Chinese Few-shot Learning Evaluation Benchmark"
  arxiv: "2107.07498"
  url: "https://arxiv.org/abs/2107.07498"
  year: 2021
leaderboard_url: "https://www.cluebenchmarks.com/fewclue.html"
repo_url: "https://github.com/CLUEbenchmark/FewCLUE"
released: "2021-04"
lineage:
  family: fewclue
  predecessor: ""
harness:
  opencompass: "FewCLUE_chid"
tags:
  - chinese
  - few-shot
  - fewclue-subset
  - cloze
sources:
  - url: "https://arxiv.org/abs/2107.07498"
    title: "FewCLUE: A Chinese Few-shot Learning Evaluation Benchmark (Xu et al., arXiv:2107.07498)"
    accessed: "2026-09-08"
  - url: "https://github.com/CLUEbenchmark/FewCLUE"
    title: "CLUEbenchmark/FewCLUE GitHub repository (task description, dataset statistics)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/FewCLUE_chid/FewCLUE_chid_gen.py"
    title: "OpenCompass FewCLUE_chid dataset config"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice B"
---

Part of the [FewCLUE](fewclue.md) family.

## What it measures

CHID (Chinese IDiom cloze test) gives the model a passage with one blank marked #idiom# and seven
candidate idioms, several of them near-synonyms of the correct answer chosen specifically to block
shallow pattern matching; the model must pick the one that actually fits the context. Passages are
drawn from news, novels and essays, sampled from a larger idiom-cloze corpus covering 3,848 idioms
(Zheng et al. 2019, arXiv:1906.01265). CHID is one of six FewCLUE tasks resampled from the CLUE
benchmark rather than newly built, and because a blank slot with candidates is already cloze-shaped,
the paper notes that training on CHID with PET comes close to zero-shot prompting in practice.

## Reading the numbers

The labelled public test set holds 2,002 items, scored by accuracy against a 14.3% seven-way random
baseline. Human evaluators scored 87.1%; the paper's few-shot methods clustered around 57-61% (PET
and LM-BFF both reached 61.2%), well below human performance but far above chance, while plain
fine-tuning badly underperformed at under 15% -- direct fine-tuning could not make good use of 42
training examples on a task this format-sensitive. A score close to 15% suggests a fine-tuning-style
approach rather than a cloze-native one. See the [FewCLUE](fewclue.md) family page for the shared
few-shot protocol and contamination notes that apply here too.
