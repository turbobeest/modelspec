---
id: clue_drcd
name: "CLUE: DRCD (Traditional Chinese span-extraction reading comprehension)"
page_kind: subset
category: composite
subcategory: "span-extraction reading comprehension (Traditional Chinese)"
status: active
summary: "CLUE's Traditional-Chinese span-extraction task, adopted unchanged from the separately published Delta Reading Comprehension Dataset; not scored on CLUE's live leaderboard."
measures: >
  DRCD gives a model a Traditional Chinese Wikipedia paragraph and a question, requiring an
  extracted answer span -- the same SQuAD-style span-extraction format as CMRC2018, but in
  Traditional rather than Simplified characters, and drawn from an entirely separate dataset. CLUE
  adopted DRCD unchanged from the Delta Reading Comprehension Dataset, published by a Delta Research
  Center team with no author overlap with the CLUE team -- the cleanest case of external adoption in
  this batch. CLUE provides its own traditional-to-simplified conversion tool for models evaluated
  in simplified Chinese but does not otherwise alter the data.
task_format: >
  Extractive question answering: given a Traditional Chinese passage and question, output the
  answer text span; the reference OpenCompass config scores it by exact match (EM), and the original
  paper additionally reports F1.
metric:
  name: "exact match (EM); F1 also reported by the original paper"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  human_baseline: 93.3
  baseline_note: >
    93.30 F1 is the human-performance figure from DRCD's own paper (against a baseline-model F1 of
    89.59%). This is not a CLUE-run figure: CLUE's live composite leaderboard does not score DRCD at
    all, so no CLUE-specific human baseline exists for it.
dataset:
  size: 33953
  size_note: >
    26,936 training, 3,524 development and 3,493 test questions (8,016 / 1,000 / 1,000 paragraphs
    respectively), confirmed identically by the CLUE GitHub README and the Hugging Face clue/clue
    mirror (config drcd). The original paper's abstract instead rounds to "10,014 paragraphs...and
    30,000+ questions"; this page's paragraph total (10,016) is close but not identical, a small gap
    left unreconciled.
  url: "https://huggingface.co/datasets/clue/clue"
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "train (26,936) / validation (3,524) / test (3,493, answers withheld in the public mirror)"
  public_test_set: false
publisher:
  org: "Delta Research Center -- the dataset's Chinese name (台達閱讀理解資料集) identifies it as Delta Electronics'; no further institutional detail was confirmed from the sources read"
  authors:
    - "Chih Chieh Shao"
    - "Trois Liu"
    - "Yuting Lai"
    - "Yiying Tseng"
    - "Sam Tsai"
  url: "https://github.com/DRCKnowledgeTeam/DRCD"
paper:
  title: "DRCD: a Chinese Machine Reading Comprehension Dataset"
  arxiv: "1806.00920"
  url: "https://arxiv.org/abs/1806.00920"
  year: 2018
leaderboard_url: ""
repo_url: "https://github.com/DRCKnowledgeTeam/DRCD"
released: "2018-06"
lineage:
  family: clue
harness:
  opencompass: "CLUE_DRCD (CLUE_DRCD_gen config family, several hash-suffixed revisions; loads the opencompass/drcd_dev mirror)"
tags:
  - chinese
  - reading-comprehension
  - span-extraction
  - traditional-chinese
  - clue-subset
sources:
  - url: "https://arxiv.org/abs/1806.00920"
    title: "DRCD: a Chinese Machine Reading Comprehension Dataset (Shao, Liu, Lai, Tseng, Tsai, arXiv:1806.00920)"
    accessed: "2026-09-08"
  - url: "https://github.com/DRCKnowledgeTeam/DRCD"
    title: "DRCKnowledgeTeam/DRCD GitHub repository (README)"
    accessed: "2026-09-08"
  - url: "https://github.com/CLUEbenchmark/CLUE"
    title: "CLUEbenchmark/CLUE GitHub repository (README, task 8: DRCD)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/clue/clue"
    title: "clue/clue dataset metadata, Hugging Face API (config drcd)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/CLUE_DRCD/CLUE_DRCD_gen_1bd3c8.py"
    title: "OpenCompass CLUE_DRCD_gen_1bd3c8.py config"
    accessed: "2026-09-08"
  - url: "https://www.cluebenchmarks.com/rank.html"
    title: "CLUE1.1 leaderboard, cluebenchmarks.com -- DRCD is not among its scored columns (fetched via scripts/benchmarks/fetch.py)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice A"
---

Part of the [CLUE](clue.md) family.

## What it measures

DRCD gives a model a Traditional Chinese Wikipedia paragraph and a question, requiring an extracted
answer span -- the same SQuAD-style format as [CMRC2018](clue_cmrc.md), but in Traditional rather
than Simplified characters and drawn from an entirely separate dataset. CLUE adopted DRCD unchanged
from the Delta Reading Comprehension Dataset, published by a Delta Research Center team with no
author overlap with the CLUE team -- the cleanest case of external adoption in this batch, unlike
CMRC2018 and C3 where the original authors also co-authored CLUE's paper. CLUE provides its own
traditional-to-simplified conversion tool for models evaluated in simplified Chinese, and DRCD is
not one of the paper's nine core tasks and is not a scored column on CLUE's live leaderboard; it
circulates mainly through CLUE's downloads and OpenCompass rather than a maintained ranking.

## Reading the numbers

The data holds 26,936 training, 3,524 development and 3,493 test questions (about 34,000 total,
close to the original paper's "30,000+" claim), confirmed identically by the CLUE README and the
Hugging Face mirror. Test answers are withheld (dummy text such as "FAKE_ANSWER_1" in the public mirror). DRCD's own
paper reports a baseline F1 of 89.59% against 93.30% human F1 -- figures from the original dataset's
own evaluation, not a CLUE leaderboard number, since CLUE does not score this task live. Compare a
DRCD score only against other DRCD scores, not against CMRC2018's, despite the shared format.
