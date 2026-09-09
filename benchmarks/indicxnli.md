---
id: indicxnli
name: "IndicXNLI"
aliases:
  - "INDICXNLI"
  - "Divyanshu/indicxnli"
page_kind: benchmark
category: reasoning
subcategory: "11-language Indic three-way NLI (lm-eval currently Gujarati only)"
status: unknown
summary: "Machine-translated XNLI for 11 Indic languages; lm-evaluation-harness currently scores only Gujarati three-way NLI on Divyanshu/indicxnli."
measures: >
  IndicXNLI is three-way natural language inference in eleven Indic languages.
  Given a premise and a hypothesis, the model must choose entailment, neutral,
  or contradiction. Aggarwal, Gupta and Kunchukuttan built the set by running
  IndicTrans over English XNLI, then checking translation quality with paired
  human ratings on a 100-sentence DPP sample of each language's test set.
  The paper lists Assamese, Gujarati (written "Gujarat ('gu')"), Kannada,
  Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu, Hindi and Bengali.
  lm-evaluation-harness currently ships only Gujarati, because facebook/xnli
  already covers Hindi and does not include Gujarati.
task_format: >
  Three-way classification. lm-eval task indicxnli_gu scores multiple-choice
  log-likelihood over a Gujarati cloze: premise + ", સાચું? {હા|તેથી|ના}, " +
  hypothesis, with gold label 0/1/2 mapped onto those three continuations.
  The YAML sets training_split train, validation_split validation and
  test_split test, so the default run uses the 5,010-row Gujarati test split.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 33.3
  human_baseline: null
  baseline_note: >
    Three labels, so uniform chance is 33.3%. The paper reports human
    translation-quality ratings (mean above 0.85, Pearson above 0.7, Spearman
    above 0.8 on the 100-sentence samples), not a pooled NLI accuracy ceiling.
dataset:
  size: 5010
  size_note: >
    Paper, Hub card table, and datasets-server agree on 392,702 train and
    5,010 test per language. Validation is 2,490 on ten configs; Tamil
    validation is 3,238 on datasets-server (the ta/dev JSON is also larger
    than the other languages). Do not total 4,402,222 as if every config
    matched XNLI's 2,490-row dev. lm-eval indicxnli_gu scores the Gujarati
    test split only (5,010). The Hub repo also stores a backward/ folder of
    Indic-to-English files; the loading script reads only forward/
    English-to-Indic JSON.
  url: "https://huggingface.co/datasets/Divyanshu/indicxnli"
  license: ""
  languages:
    - as
    - bn
    - gu
    - hi
    - kn
    - ml
    - mr
    - or
    - pa
    - ta
    - te
  modalities:
    - text
  splits: "per language train 392,702 / test 5,010; validation 2,490 except ta 3,238 on datasets-server; lm-eval Gujarati uses test"
  public_test_set: true
publisher:
  org: "Delhi Technological University, University of Utah, and Microsoft Research"
  authors:
    - "Divyanshu Aggarwal"
    - "Vivek Gupta"
    - "Anoop Kunchukuttan"
  url: "https://github.com/divyanshuaggarwal/IndicXNLI"
paper:
  title: "IndicXNLI: Evaluating Multilingual Inference for Indian Languages"
  arxiv: "2204.08776"
  url: "https://aclanthology.org/2022.emnlp-main.755/"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/divyanshuaggarwal/IndicXNLI"
released: "2022-04"
last_updated: "2022-10"
lineage:
  family: ""
  predecessor: xnli
  successors: []
  variants:
    - xnli_eu
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The Hugging Face card says there is no dedicated leaderboard. No current
    LLM ceiling was read from a source opened for this page.
contamination:
  risk: high
  note: >
    The test labels have been public on Hugging Face since 2022 as a
    machine-translated copy of English XNLI, itself public since 2018. No
    private held-out Indic test is described. This is from publicity and age,
    not a measured leakage study.
harness:
  lm_eval: "indicxnli_gu"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Directory lm_eval/tasks/indicxnli holds only indicxnli_gu.yaml. It loads
    Divyanshu/indicxnli at revision refs/convert/parquet with
    gu/{train,validation,test}/0000.parquet. It is not in the xnli group.
tags:
  - nli
  - indic
  - cross-lingual
  - entailment
  - multilingual
  - classification
sources:
  - url: "https://arxiv.org/abs/2204.08776"
    title: "IndicXNLI paper abstract (arXiv:2204.08776, 19 Apr 2022)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2204.08776"
    title: "IndicXNLI HTML (IndicTrans, 11 languages, 392702/2490/5010, human ratings)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2022.emnlp-main.755/"
    title: "EMNLP 2022 anthology page (pages 10994–11006, December 2022)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Divyanshu/indicxnli/raw/main/README.md"
    title: "Divyanshu/indicxnli card (languages, splits, CC BY-NC 4.0 body vs cc0-1.0 YAML)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/Divyanshu/indicxnli"
    title: "Hub API (cardData license cc0-1.0; lastModified 2022-10-06)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=Divyanshu/indicxnli"
    title: "datasets-server split counts (392702 / 5010 / 2490 per language)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Divyanshu/indicxnli/raw/main/indicxnli.py"
    title: "Loading script (forward/ JSON only; 11 language configs)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/indicxnli/README.md"
    title: "lm-eval IndicXNLI README (Gujarati-only task indicxnli_gu)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/indicxnli/indicxnli_gu.yaml"
    title: "indicxnli_gu.yaml (test split, Gujarati cloze, acc)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/divyanshuaggarwal/IndicXNLI/main/README.md"
    title: "GitHub README (EMNLP 2022; points to Hub data; non-academic licence note)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/divyanshuaggarwal/IndicXNLI/main/LICENSE"
    title: "GitHub LICENSE (MIT, code copyright 2021; not a dataset grant)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-050 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-050"
---

## What it measures

IndicXNLI asks whether a hypothesis is entailed by, contradicted by, or independent of a premise, in eleven Indic languages. The pairs are IndicTrans translations of English XNLI, not native authoring. The paper is an NLI transfer study: train on some languages, test on others, and compare multilingual and mix-language setups. It is not a new English entailment set. Hindi already sits in [XNLI](xnli.md); Gujarati does not, which is why lm-eval added only `indicxnli_gu`.

The skill is cross-lingual three-way NLI after machine translation. Errors can come from translation artefacts as well as from inference. Human checks in the paper rate translation, not NLI accuracy.

## How it is scored

lm-eval reports mean accuracy on the three cloze continuations. Chance is one in three. The YAML evaluates the Gujarati test split (5,010 items). That is a different cut from the XNLI group in this repo, which scores facebook/xnli validation unless a reporter overrides it. Do not average IndicXNLI Gujarati test with XNLI Hindi validation and call the mix "Indic NLI."

The paper's own tables are fine-tuned encoder results, not zero-shot LLM cloze scores. Those two protocols are not interchangeable.

## Dataset and licence

Ten Hub configs have 392,702 train, 2,490 validation and 5,010 test rows. Tamil matches on train and test, but datasets-server reports 3,238 validation rows and a larger `forward/dev/xnli_ta.json` than the other languages. The paper and the Hub card table still print 2,490 for every language, including Tamil. The loading script reads `forward/` English-to-Indic JSON. A `backward/` tree exists on the Hub but is unused by that script. Licence statements disagree: Hub YAML says CC0-1.0, the card body says CC BY-NC 4.0, the citation block says CC BY 4.0, and the GitHub tree ships an MIT licence for code. This page leaves `dataset.license` empty rather than pick one.

## Who publishes it

Divyanshu Aggarwal (Delhi Technological University), Vivek Gupta (University of Utah) and Anoop Kunchukuttan (Microsoft Research) released the paper on arXiv on 19 April 2022 and at EMNLP 2022 (pages 10994–11006). Data live at `Divyanshu/indicxnli` (Hub last modified 2022-10-06). Code and experiment scripts are at divyanshuaggarwal/IndicXNLI. The card says there is no leaderboard.

## Lineage

The predecessor is [XNLI](xnli.md) (Conneau et al., 2018), itself MultiNLI translated into 15 languages. IndicXNLI adds eleven Indic languages via IndicTrans rather than professional translation. [xnli_eu](xnli_eu.md) is a later Basque extension with post-edited and native tests; it is not IndicXNLI. lm-eval's `xnli` group does not include `indicxnli_gu`.

## Saturation and contamination

No current LLM ceiling was confirmed. The test labels have been public since 2022 as translations of a 2018 test set, so contamination risk is high in the usual public-set sense. The paper's human study is a 100-sentence translation check per language, not a leakage audit.

## How to run it

```
lm_eval --model hf --model_args pretrained=<model> --tasks indicxnli_gu
```

There is no `indicxnli` group in the harness directory. Prompt cues are hard-coded Gujarati particles, not the English Yes/Also/No strings from `xnli` `utils.py`. Compare only against other Gujarati IndicXNLI cloze runs that use the test split.

## Reading the numbers

A strong `indicxnli_gu` score means the model ranked the right Gujarati continuation on these translated XNLI test pairs. It does not mean the model handles native Gujarati discourse, the other ten Indic languages, or English XNLI. Translation noise can inflate or hide NLI errors. Report the language, split and cloze strings. Read it next to [XNLI](xnli.md) Hindi and, if present, a native Indic NLI set, not as a drop-in multilingual average.
