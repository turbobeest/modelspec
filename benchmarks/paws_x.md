---
id: paws_x
name: "PAWS-X"
aliases:
  - "paws-x"
  - "pawsx"
  - "PAWS-X: A Cross-lingual Adversarial Dataset for Paraphrase Identification"
page_kind: benchmark
category: reasoning
subcategory: "multilingual binary paraphrase identification on translated PAWS-Wiki pairs"
status: active
summary: "lm-eval multilingual paraphrase identification on PAWS-X: seven languages of high-overlap sentence pairs, scored by accuracy."
measures: >
  This id is EleutherAI lm-eval group pawsx (directory paws-x), not English-only
  Inspect paws and not a translation quality test. Each item is a sentence pair
  in German, English, Spanish, French, Japanese, Korean or Chinese. The model
  must decide whether the pair is a paraphrase. Non-English evaluation pairs
  are human translations of PAWS-Wiki; training pairs are machine translated.
  lm-eval casts the decision as two cloze strings: "{s1}, right? No, {s2}"
  versus "{s1}, right? Yes, {s2}", with language-specific wording from Google
  Translate.
task_format: >
  Multiple-choice likelihood (output_type multiple_choice) over No versus Yes
  continuations. Group pawsx aggregates paws_de, paws_en, paws_es, paws_fr,
  paws_ja, paws_ko, paws_zh. English prompt shown in the harness README;
  other languages use translated masks.
metric:
  name: "accuracy (acc); group mean weighted by size"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50
  human_baseline: null
  baseline_note: >
    Two classes, chance 50%. Development/test Yes rate is about 44-45% in the
    PAWS-X paper. Yang et al. report multilingual BERT (translate-train plus
    merged data) at 83.1-90.8 accuracy on non-English languages, with merged
    BERT best overall in their 2019 table. Those are fine-tuned encoders, not
    zero-shot LLM numbers. No human accuracy is stated.
dataset:
  size: 23659
  size_note: >
    Paper and official pawsx README: 23,659 human-translated evaluation pairs
    and 296,406 machine-translated training pairs in six languages (fr, es, de,
    zh, ja, ko). Official per-language test counts after dropping untranslated
    rows: fr 1,985, es 1,999, de 1,967, zh 1,975, ja 1,946, ko 1,972 (dev
    similarly 1,932-1,992). Hugging Face google-research-datasets/paws-x instead
    exposes 2,000 validation and 2,000 test rows per language including English
    (14,000 test rows across the seven lm-eval tasks).
    The paper's "Resulting Corpus" paragraph also prints 23,459, which does not
    match 11,815+11,844; this page follows the README total 23,659. Dev and test
    both come from PAWS-Wiki dev, so sentence1 can overlap across splits; pair
    overlap is claimed to be empty. A few translated rows contain the token
    "NS" instead of a sentence; lm-eval drops empty sentences.
  url: "https://huggingface.co/datasets/google-research-datasets/paws-x"
  license: "other (same Google PAWS licence: free use with acknowledgement, AS IS)"
  languages:
    - de
    - en
    - es
    - fr
    - ja
    - ko
    - zh
  modalities:
    - text
  splits: "Per language on Hugging Face: train 49,401 / validation 2,000 / test 2,000. Official TSV test counts are slightly smaller."
  public_test_set: true
publisher:
  org: "Google Research"
  authors:
    - "Yinfei Yang"
    - "Yuan Zhang"
    - "Chris Tar"
    - "Jason Baldridge"
  url: "https://github.com/google-research-datasets/paws/tree/master/pawsx"
paper:
  title: "PAWS-X: A Cross-lingual Adversarial Dataset for Paraphrase Identification"
  arxiv: "1908.11828"
  url: "https://arxiv.org/abs/1908.11828"
  year: 2019
leaderboard_url: ""
repo_url: "https://github.com/google-research-datasets/paws/tree/master/pawsx"
released: "2019"
last_updated: "2024-11"
lineage:
  family: ""
  predecessor: paws
  successors: []
  variants: []
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: >
    2019 merged mBERT already exceeded 90% on some languages. No current
    lm-eval group top score was copied. Headroom is more plausible on Japanese,
    Korean and Chinese than on German, French and Spanish, per the paper's
    language split, but that is not a 2026 LLM table.
contamination:
  risk: high
  note: >
    Translated pairs and labels have been public since 2019. English sources
    are the public PAWS-Wiki dev set. lm-eval scores the public test split.
harness:
  lm_eval: "pawsx (group); tasks paws_de, paws_en, paws_es, paws_fr, paws_ja, paws_ko, paws_zh"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Directory lm_eval/tasks/paws-x. Group YAML _pawsx.yaml. Template
    pawsx_template_yaml uses google-research-datasets/paws-x. Changelog: v1
    (2024-11-05) PR #2434 corrected doc_to_choice label order.
tags:
  - paraphrase
  - multilingual
  - sentence-pair
  - lm-eval
  - adversarial
sources:
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/paws-x/README.md"
    title: "lm-eval PAWS-X README (group pawsx, tasks, paper, prompt)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/paws-x/_pawsx.yaml"
    title: "lm-eval _pawsx.yaml (group list, weighted acc)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/paws-x/pawsx_template_yaml"
    title: "pawsx_template_yaml (dataset_path, acc, test_split)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/paws-x/paws_en.yaml"
    title: "paws_en.yaml (Yes/No choice order after PR #2434)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/paws-x/utils.py"
    title: "paws-x utils.py (detokenize; drop empty sentences)"
    accessed: "2026-09-08"
  - url: "https://github.com/google-research-datasets/paws/blob/master/pawsx/README.md"
    title: "Official PAWS-X README (23,659 pairs; per-language counts; NS caveat)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/google-research-datasets/paws-x"
    title: "Hugging Face paws-x card (2,000 test per language; licence)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/google-research-datasets/paws-x"
    title: "Hugging Face paws-x API split counts"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1908.11828"
    title: "PAWS-X paper abstract"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1908.11828"
    title: "PAWS-X paper HTML (mBERT 83.1-90.8; 23,459 versus 23,659)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-013 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-013"
---

## What it measures

lm-eval `pawsx` is multilingual paraphrase identification on PAWS-X. The model
sees two high-overlap sentences in one of seven languages and must prefer the
Yes continuation if they match in meaning. The hard cases are the same
argument-swap traps as English [PAWS](paws.md), now in translation.

It is not a translation benchmark. It is not Inspect `paws`, which scores
English labeled_final test with a Yes/No generation prompt.

## How it is scored

Each language task reports accuracy. The group mean is size-weighted `acc`.
lm-eval is a two-way likelihood comparison, not Inspect’s `includes()` string
match. PR #2434 (2024-11-05) fixed Yes/No choice order; older logs may not
match current YAML. The README warns that translated prompts may differ from
mGPT/XGLM. Compare only same-language tasks, or the named `pawsx` group.

## Dataset and licence

Human eval data: 23,659 pairs across six translated languages per the official
README (dev 11,815, test 11,844). Hugging Face pads each language, including
English, to 2,000/2,000, so lm-eval's seven-language test split is 14,000 rows
on that dump. Official TSV test sizes are a few dozen smaller because some rows
could not be translated or contain "NS". Training is 49,401 machine-translated
pairs per language (296,406 total). Licence is the same Google PAWS text
(`other` on Hugging Face). The parent repo is archived (API `archived` true;
archive date not returned).

## Who publishes it

Yang, Zhang, Tar and Baldridge (Google; EMNLP 2019; arXiv 1908.11828).
lm-eval maintains the seven tasks and the `pawsx` group.

## Lineage

Predecessor [paws](paws.md) is English PAWS-Wiki. IberoBench `paws_gl` and
`paws_ca` are extra translations inside [GalicianBench](galician_bench.md)
and [CatalanBench](catalan_bench.md), not members of this group. Dev and test
both come from PAWS-Wiki development data.

## Saturation and contamination

2019 mBERT already scored in the mid-80s to low-90s with translated training
data. Public labels since 2019 make contamination high. No 2026 group top
score is stored here.

## How to run it

`lm_eval --tasks pawsx` for the group, or `paws_en` and the other six task
names. Say whether you used the post-#2434 choice order. Do not quote Inspect
`paws` accuracy as `paws_x`.

## Reading the numbers

A high `pawsx` mean means the model tracked word order and roles in seven
languages on Wikipedia-style swaps. It does not measure translation quality
or paraphrase generation. English `paws_en` here is the PAWS-X English split
(2k test), not Inspect’s 8k PAWS-Wiki test. Always name the language list.
