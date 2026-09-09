---
id: icelandic_winogrande
name: "Icelandic WinoGrande"
aliases:
  - "IWG"
  - "icelandic-winogrande"
  - "mideind/icelandic-winogrande"
page_kind: benchmark
category: reasoning
subcategory: "Icelandic commonsense pronoun resolution, localized from WinoGrande"
status: unknown
summary: "Manually localized Icelandic WinoGrande schemas scored as two-way fill-in-the-blank accuracy; lm-eval runs the public train split."
measures: >
  Icelandic WinoGrande gives a short Icelandic sentence with a blank and two
  candidate noun phrases. The model must pick the filler that makes commonsense
  sense, not the one that merely agrees in grammar. Miðeind and the University
  of Iceland translated and adapted English WinoGrande test items by hand so
  gender, number, and case would not leak the answer. Items that could not be
  localized were skipped or rewritten. The skill is Icelandic coreference and
  everyday inference, not English WinoGrande and not IceBERT's other Icelandic
  tagging tasks.
task_format: >
  Two-way fill-in-the-blank. Each row has sentence, option1, option2, and
  answer "1" or "2". lm-evaluation-harness scores it as multiple_choice with
  partial cloze likelihoods (Trinh and Le 2018), matching English winogrande
  in the same harness. The Hub eval.py compares causal-LM loss on the two
  full sentences, default 3-shot.
metric:
  name: accuracy
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 50.0
  human_baseline: null
  baseline_note: >
    Two options, so uniform chance is 50%. On the Hub train.jsonl, answer "1"
    appears 619 times and "2" 469 times (1,088 rows), so a constant-option1
    policy scores about 56.9%. Table 10 of the LREC 2022 paper reports
    five-fold cross-validation accuracy for IceBERT-large at 57.1 ± 3.7%,
    near that majority rate; that figure is BERT fine-tuning, not the
    autoregressive harness protocol. No human-rater score is stated.
dataset:
  size: 1088
  size_note: >
    Hugging Face datasets-server and a direct count of
    mideind/icelandic-winogrande data/train.jsonl both give 1,088 train rows.
    The LREC paper (section 5.5) says the authors walked the English
    WinoGrande test set of 1,767 items and produced 1,095 Icelandic examples.
    The seven-item gap between the paper and the Hub file is not explained in
    the sources opened here. Only a train split is published.
  url: "https://huggingface.co/datasets/mideind/icelandic-winogrande"
  license: "CC-BY-4.0"
  languages:
    - is
  modalities:
    - text
  splits: "single public train split (1,088 rows); lm-eval sets test_split to train"
  public_test_set: true
publisher:
  org: "Miðeind ehf. and University of Iceland"
  authors:
    - "Vésteinn Snæbjarnarson"
    - "Haukur Barri Símonarson"
    - "Pétur Orri Ragnarsson"
    - "Svanhvít Lilja Ingólfsdóttir"
    - "Haukur Páll Jónsson"
    - "Vilhjálmur Þorsteinsson"
    - "Hafsteinn Einarsson"
  url: "https://huggingface.co/datasets/mideind/icelandic-winogrande"
paper:
  title: "A Warm Start and a Clean Crawled Corpus - A Recipe for Good Language Models"
  arxiv: ""
  url: "https://aclanthology.org/2022.lrec-1.464/"
  year: 2022
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/icelandic_winogrande"
released: "2022-06"
last_updated: "2024-06"
lineage:
  family: ""
  predecessor: "winogrande"
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    Paper Table 10 tops out at IceBERT-large 57.1 ± 3.7% under five-fold
    BERT fine-tuning, close to the Hub majority rate. No current
    autoregressive leaderboard cell was read, so saturation for today's
    decoder models is not established.
contamination:
  risk: medium
  note: >
    Labels are public on the Hub (dataset created 2022-07-04). The LREC
    paper is from June 2022. The set is small and fully labeled, so
    memorisation is possible. The authors replaced culture-specific English
    content rather than posting a raw translation, which lowers but does not
    remove overlap with English WinoGrande crawls.
harness:
  lm_eval: "icelandic_winogrande"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Hugging Face mideind/icelandic-winogrande/eval.py is a separate 3-shot
    causal-LM loss script on the train split. It is not the lm-eval task.
tags:
  - icelandic
  - winogrande
  - commonsense
  - coreference
  - multiple-choice
  - low-resource
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/icelandic_winogrande/README.md"
    title: "lm-eval icelandic_winogrande README (task name, paper, Hub dataset)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/icelandic_winogrande/default.yaml"
    title: "lm-eval default.yaml (task icelandic_winogrande, test_split train, metric acc)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/icelandic_winogrande/preprocess_winogrande.py"
    title: "lm-eval preprocess_winogrande.py (partial-scoring cloze helpers)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/mideind/icelandic-winogrande"
    title: "mideind/icelandic-winogrande dataset card (CC-BY-4.0, Icelandic, train.jsonl)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/mideind/icelandic-winogrande"
    title: "Hub API metadata (created 2022-07-04, lastModified 2024-06-25, license cc-by-4.0)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=mideind/icelandic-winogrande"
    title: "datasets-server split info (train 1,088 examples)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/mideind/icelandic-winogrande/resolve/main/data/train.jsonl"
    title: "train.jsonl (1,088 rows; answer 1=619, answer 2=469)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/mideind/icelandic-winogrande/raw/main/eval.py"
    title: "Upstream eval.py (3-shot causal-LM loss comparison on train)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2022.lrec-1.464/"
    title: "LREC 2022 paper landing page"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2022.lrec-1.464.pdf"
    title: "LREC 2022 PDF (CC-BY-NC-4.0 paper; section 5.5: 1,095 examples; Table 10 IceBERT-large 57.1%)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/2022.lrec-1.464.xml"
    title: "ACL Anthology MODS (dateIssued 2022-06, authors)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/winogrande/README.md"
    title: "English winogrande harness README (partial scoring citation)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-049 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-049"
---

## What it measures

Icelandic WinoGrande is a two-choice pronoun puzzle in Icelandic. The model sees a sentence with a blank and two names or noun phrases, then must pick the filler that fits the situation. Grammar alone is not enough, and Icelandic inflection was edited so gender or case would not give the answer away.

The set is a manual localization of English [WinoGrande](winogrande.md), not a machine translation. The LREC 2022 IceBERT paper says the authors started from the 1,767-item English test set, wrote paired sentences where English had a singlet, and skipped items that were too culture-specific to move. The Hub card repeats that translations are not meant to preserve English wording.

## How it is scored

lm-evaluation-harness task `icelandic_winogrande` reports mean accuracy. It uses the same partial cloze scoring as English `winogrande`: two completed prefixes, one continuation, higher likelihood wins. The YAML sets `test_split: train` because the Hub dump has only a train split.

That is not the paper protocol. Table 10 is five-fold cross-validation accuracy after fine-tuning BERT-style models. IceBERT-large sits at 57.1 ± 3.7%. The Hub `eval.py` is a third protocol: 3-shot causal-LM loss on the two full sentences. Do not mix those three numbers.

## Dataset and licence

The published file is `data/train.jsonl` under `mideind/icelandic-winogrande`, licence CC-BY-4.0, language `is`. The LREC PDF itself is CC-BY-NC-4.0; those terms apply to the paper, not the Hub dump. datasets-server and a line count both give 1,088 examples with fields qID, sentence, option1, option2, and answer. Gold is unbalanced (619 vs 469).

The paper states 1,095 examples. This page records both figures and does not choose between them. There is no held-out test file. Answers are public.

## Who publishes it

Vésteinn Snæbjarnarson, Haukur Barri Símonarson, Pétur Orri Ragnarsson, Svanhvít Lilja Ingólfsdóttir, Haukur Páll Jónsson, Vilhjálmur Þorsteinsson, and Hafsteinn Einarsson at Miðeind and the University of Iceland introduced it in LREC 2022 (June). The Hub dataset was created 2022-07-04 and last changed 2024-06-25. No standalone leaderboard was found. lm-eval ships the runnable task.

## Lineage

This is a localized child of [winogrande](winogrande.md), not a subset page under a WinoGrande family (that English page is a standalone benchmark). It is not SuperGLUE WSC and not IceBERT's POS, NER, or GED numbers from the same paper. The harness README says it is not in a task group yet.

## Saturation and contamination

The 2022 BERT numbers sit near chance and near the Hub majority rate, so the set was hard for those models. No current decoder-only leaderboard was read, so saturation.status stays unknown. Contamination risk is medium: the full labeled train split has been public since 2022, and lm-eval scores that same split.

## How to run it

```text
lm_eval --model hf --model_args pretrained=<model> --tasks icelandic_winogrande
```

Dataset path in the YAML is `mideind/icelandic-winogrande`. Preprocessing lives in `preprocess_winogrande.py`. Compare only against other partial-scoring runs on this file, not against Table 10 or against English WinoGrande.

## Reading the numbers

A high score means the model preferred the commonsense filler on these Icelandic schemas under cloze likelihoods. It does not measure Icelandic generation, exam knowledge, or English WinoGrande. Because eval is the public train split, treat large jumps on new web-scale models with contamination in mind. Watch the 56.9% constant-option1 floor on the Hub file, and say which protocol you used: lm-eval, Hub eval.py, or the paper's five-fold BERT setup.
