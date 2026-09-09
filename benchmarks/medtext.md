---
id: medtext
name: "MedText (lm-eval)"
aliases:
  - "medtext_perplexity"
  - "BI55/MedText"
page_kind: benchmark
category: domain
subcategory: "synthetic patient presentation to diagnosis and treatment"
status: unknown
summary: "lm-eval's generation wrap of BI55/MedText: write a diagnosis and treatment plan from an English patient presentation and score overlap metrics."
measures: >
  This id is EleutherAI lm-evaluation-harness task medtext. The Hugging Face set
  BI55/MedText pairs an English patient presentation (Prompt) with a diagnosis and
  treatment completion written in a clinical voice. lm-eval asks the model to
  continue that presentation. It is text-only English generation. It is not a
  licensing exam, not MIMIC notes, and not the 2019 Melamud and Shivade synthetic
  clinical-note paper that the lm-eval README cites.
task_format: >
  generate_until generation, stopping at a blank line. doc_to_text is the Prompt
  field; gold is Completion. The YAML description instructs the model to answer as
  a doctor with a likely diagnosis and treatment. Train, validation and test all
  point at the single train split. Companion task medtext_perplexity scores
  rolling likelihood of the completion.
metric:
  name: "bleu, rouge1, rouge2, rougeL, bleurt, bert_score (no designated headline)"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    lm-eval logs six overlap metrics with nanmean aggregation. BLEURT uses
    bleurt-base-512; BERTScore is English F1. The card says three doctors rated ten
    random examples as textbook quality; that is not a scored human baseline for
    this generation protocol. No random baseline is stated.
dataset:
  size: 1412
  size_note: >
    Hugging Face datasets-server reports 1,412 train examples in BI55/MedText
    (csv medtext_2.csv). The downloaded csv has a header plus 1,412 rows. The card
    describes this file as the shuffled version of medtext_1. lm-eval uses that
    train split for training, validation and test, so a default run scores all
    1,412 items. The card says "over 1000" presentations; the counted size is 1,412.
  url: https://huggingface.co/datasets/BI55/MedText
  license: "CC-BY-4.0"
  languages:
    - en
  modalities:
    - text
  splits: "single train split (1,412); lm-eval maps train/validation/test all to train"
  public_test_set: true
publisher:
  org: "Hugging Face user BI55 (card fullname L. Heinrich)"
  authors:
    - "L. Heinrich"
  url: https://huggingface.co/datasets/BI55/MedText
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/medtext
released: "2023-07"
last_updated: "2023-07"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No public MedText leaderboard was opened. Saturation of the overlap metrics is
    not established.
contamination:
  risk: high
  note: >
    The full 1,412 prompt-completion pairs have been public on Hugging Face since
    25 July 2023, including the gold completions. The card says the text was
    converted into uniform datapoints with GPT-4, so models trained on similar
    GPT-4 clinical prose may overlap even without this file.
harness:
  lm_eval: "medtext"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Also medtext_perplexity (loglikelihood_rolling on the Completion field)."
tags:
  - medical
  - generation
  - overlap-metrics
  - lm-eval
  - synthetic
sources:
  - url: https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/medtext
    title: "lm-evaluation-harness medtext task directory"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/medtext/README.md
    title: "lm-eval medtext README (cites arXiv:1905.07002; does not match this dataset)"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/medtext/medtext.yaml
    title: "lm-eval medtext.yaml"
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/medtext/utils.py
    title: "lm-eval medtext utils.py"
    accessed: "2026-09-08"
  - url: https://huggingface.co/datasets/BI55/MedText
    title: "BI55/MedText dataset card (CC-BY-4.0, GPT-4 converted original data)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/api/datasets/BI55/MedText
    title: "Hugging Face API dataset metadata (created 2023-07-25, 1412-row csv)"
    accessed: "2026-09-08"
  - url: https://datasets-server.huggingface.co/info?dataset=BI55/MedText
    title: "BI55/MedText datasets-server split counts (train 1412)"
    accessed: "2026-09-08"
  - url: https://huggingface.co/api/users/BI55/overview
    title: "Hugging Face user BI55 overview (fullname L. Heinrich)"
    accessed: "2026-09-08"
  - url: https://arxiv.org/abs/1905.07002
    title: "Melamud and Shivade 2019 (cited by lm-eval README; different work)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-058 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-058"
---

## What it measures

`medtext` is lm-eval's wrap of Hugging Face `BI55/MedText`. Each item is an English patient presentation and a gold diagnosis-and-treatment write-up. The model must produce that clinical plan from the presentation. The card covers common hospital diseases and injuries, plus noise cases where the model should refuse or ask for more information. The modality is text. The language is English.

This is not USMLE-style multiple choice and not MIMIC discharge summarization. The lm-eval README cites Melamud and Shivade 2019 on shareable synthetic clinical notes. That paper trains language models on de-identified notes. It is not this GPT-4 converted textbook-style set.

## How it is scored

The generation task is `generate_until` with stop sequence `\n\n`. Scores are BLEU, ROUGE-1/2/L, BLEURT and BERTScore F1, each with nanmean. There is no YAML headline metric. Empty strings become NaN. `medtext_perplexity` reports word and byte perplexity and bits per byte on the completion. No random or official human score for this protocol was published. The card's three-doctor check of ten examples is a quality note, not a leaderboard baseline.

## Dataset and licence

datasets-server lists 1,412 train rows. The csv `medtext_2.csv` matches that count. The card calls it the shuffled version of `medtext_1` and dates the dataset to 25 July 2023. lm-eval points train, validation and test at that same split, so a default run evaluates all 1,412 items with public golds. The licence on the card is CC BY 4.0. The card says the uniform datapoints were produced with GPT-4 from original text.

## Who publishes it

The Hugging Face dataset is under user `BI55`, with profile fullname L. Heinrich. No separate academic paper for this csv was found. EleutherAI maintains the lm-eval task files. There is no official MedText leaderboard URL.

## Lineage

Do not treat this as Melamud and Shivade 2019, despite the lm-eval README citation. It is also not [medication_qa](medication_qa.md), [medi_qa](medi_qa.md), or the MIMIC discharge tasks [mimic_bhc](mimic_bhc.md) and [mimic_rrs](mimic_rrs.md). Those use real or gated clinical notes and different metrics. No successor replaced this wrap.

## Saturation and contamination

Saturation is unknown. Contamination risk is high: prompts and gold completions are public, small, and dated 2023. GPT-4 was used to format the pairs, so lexical overlap with other GPT-4 clinical text is possible even if this file was not copied.

## How to run it

```
lm_eval --model hf --model_args pretrained=... --tasks medtext
```

Also `medtext_perplexity`. Metric extras match the MEDIQA lm-eval helper (BLEU, ROUGE, BERTScore, BLEURT). Because every split is `train`, few-shot sampling can draw from the same 1,412 rows that are scored. Compare runs only when shot count and stop rules match.

## Reading the numbers

A high ROUGE or BERTScore means the model echoed this set's diagnosis-and-treatment style, including the humble "cannot replace a doctor" completions the card describes. It does not measure bedside accuracy, coding, or exam knowledge. Pair it with a held-out clinical QA or note task, and ignore the 2019 synthetic-note citation in the harness README.
