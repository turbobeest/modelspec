---
id: clue_ocnli
name: "CLUE: OCNLI (Original Chinese Natural Language Inference)"
page_kind: subset
category: composite
subcategory: "natural language inference (Chinese, natively authored)"
status: active
summary: "CLUE's native-Chinese NLI task, collected without translation; replaced CMNLI as the suite's scored natural-language-inference task from the 1.1 leaderboard onward."
measures: >
  OCNLI asks whether a Chinese premise entails, contradicts, or is neutral toward a Chinese
  hypothesis -- the same three-way judgment as CMNLI, but built without translation. Premises are
  drawn from five genres of Chinese source text (news, government documents, fiction, TV
  transcripts, telephone transcripts); university students majoring in language-related fields were
  hired to write the hypotheses directly in Chinese, following MultiNLI's elicitation procedure but
  adapted for native collection. The authors state this makes OCNLI "more suitable than XNLI" for
  Chinese-specific evaluation, since XNLI's Chinese portion is itself translated from English.
task_format: >
  Three-way classification (entailment / neutral / contradiction) over a Chinese sentence pair,
  scored by accuracy; items also carry a difficulty level (easy/medium/hard) and a genre label.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 33.3
  human_baseline: 90.3
  baseline_note: >
    33.3% is the three-option random-guess rate. 90.3% is the human-performance figure both the
    CLUE paper and OCNLI's own paper report, matching the "HUMAN" row (OCNLI_50K column) on the
    live CLUE1.1 leaderboard.
dataset:
  size: 56387
  size_note: >
    50,437 train / 2,950 validation / 3,000 test, per the Hugging Face clue/clue mirror (config
    ocnli) and its datasets-server split counts -- close to the paper's own rounded "56k inference
    pairs" and to the CLUE README's rounded 50k/3k/3k.
  url: "https://huggingface.co/datasets/clue/clue"
  license: ""
  languages:
    - zh
  modalities:
    - text
  splits: "train (50,437) / validation (2,950) / test (3,000, label always -1 in the public mirror)"
  public_test_set: false
publisher:
  org: "OCNLI project team, a subset of the CLUE benchmark's authors (GitHub organisation cluebenchmark)"
  authors:
    - "Hai Hu"
    - "Kyle Richardson"
    - "Liang Xu"
    - "Lu Li"
    - "Sandra Kübler"
    - "Lawrence S. Moss"
  url: "https://github.com/cluebenchmark/OCNLI"
paper:
  title: "OCNLI: Original Chinese Natural Language Inference"
  arxiv: "2010.05444"
  url: "https://arxiv.org/abs/2010.05444"
  year: 2020
leaderboard_url: "https://www.cluebenchmarks.com/rank.html"
repo_url: "https://github.com/cluebenchmark/OCNLI"
released: "2019-11"
lineage:
  family: clue
  predecessor: clue_cmnli
harness:
  opencompass: "CLUE_ocnli (CLUE_ocnli_gen / CLUE_ocnli_ppl config variants; loads the opencompass/OCNLI-dev mirror)"
tags:
  - chinese
  - natural-language-inference
  - native-chinese
  - clue-subset
sources:
  - url: "https://arxiv.org/abs/2010.05444"
    title: "OCNLI: Original Chinese Natural Language Inference (Hu, Richardson, Xu, Li, Kübler, Moss, arXiv:2010.05444; EMNLP Findings 2020)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2004.05986"
    title: "CLUE paper, full text (ar5iv) -- OCNLI description, Section 4.2"
    accessed: "2026-09-08"
  - url: "https://github.com/CLUEbenchmark/CLUE"
    title: "CLUEbenchmark/CLUE GitHub repository (README, task 4: OCNLI, states it replaced CMNLI on the leaderboard)"
    accessed: "2026-09-08"
  - url: "https://github.com/cluebenchmark/OCNLI"
    title: "cluebenchmark/OCNLI GitHub repository"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/clue/clue"
    title: "clue/clue dataset metadata, Hugging Face API (config ocnli)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/CLUE_ocnli/CLUE_ocnli_gen_51e956.py"
    title: "OpenCompass CLUE_ocnli_gen_51e956.py config"
    accessed: "2026-09-08"
  - url: "https://www.cluebenchmarks.com/rank.html"
    title: "CLUE1.1 leaderboard, cluebenchmarks.com (OCNLI_50K column; fetched via scripts/benchmarks/fetch.py)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice A"
---

Part of the [CLUE](clue.md) family.

## What it measures

OCNLI asks whether a Chinese premise entails, contradicts, or is neutral toward a Chinese
hypothesis -- the same three-way judgment as [CMNLI](clue_cmnli.md), but collected without
translation. Premises are drawn from five genres of Chinese text (news, government documents,
fiction, TV transcripts, telephone transcripts); university students majoring in language-related
fields were hired to write the hypotheses directly in Chinese, following MultiNLI's elicitation
procedure adapted for native collection. The authors state this makes OCNLI "more suitable than
XNLI" for Chinese evaluation, since XNLI's Chinese portion is itself translated from English. OCNLI
was built for CLUE and also has its own dedicated paper (Hu et al., EMNLP Findings 2020); CLUE's
README says it replaced CMNLI as the suite's scored NLI task from the 1.1 leaderboard onward.

## Reading the numbers

The data holds 50,437 training, 2,950 validation and 3,000 test pairs (about 56,400 total, close to
the paper's own "56k" claim). Test labels are withheld, so most harnesses score the public
validation split. Read a score against 90.3%, the human baseline both papers report -- the
strongest score on CLUE's live leaderboard (86.5%, dated November 2022) still falls about 3.8
points short of it, a real gap that AFQMC and C3 no longer show, making OCNLI one of this suite's
less-saturated tasks.
