---
id: lambada_multilingual_stablelm
name: "LAMBADA multilingual (Stable LM translations)"
aliases:
  - "lambada_openai_mt_stablelm"
  - "lambada_mt_stablelm"
page_kind: benchmark
category: reasoning
subcategory: "multilingual last-word prediction on Stable LM retranslations of OpenAI LAMBADA"
status: active
summary: "lm-eval group of OpenAI-format LAMBADA last-word tests using Stability AI's retranslations, not the older googletrans EleutherAI/lambada_openai files."
measures: >
  lambada_multilingual_stablelm is EleutherAI's lm-evaluation-harness group over
  machine-translated OpenAI-format LAMBADA cloze sets released for the Stable LM
  2 1.6B report. Each item is a narrative passage whose last word is withheld.
  The model must rank that word above alternatives using discourse beyond the
  last sentence. Stability AI judged EleutherAI/lambada_openai translations too
  noisy and published new ones. Text only. Distinct from
  [lambada_multilingual](lambada_multilingual.md).
task_format: >
  Causal LM cloze scored as loglikelihood. Prompt is the passage minus the last
  whitespace token; the target is a leading space plus that token. Group tag
  lambada_multilingual_stablelm. Runnable names lambada_openai_mt_stablelm_{en,de,es,fr,it,nl,pt}.
metric:
  name: "accuracy (next-word exact match); perplexity also reported"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    YAML metric_list records acc (mean, higher better) and perplexity (lower
    better). No random or human baseline is defined for open-vocabulary
    next-word prediction. The 2016 LAMBADA human filter applies to English
    source passages, not these translations.
dataset:
  size: 36071
  size_note: >
    EleutherAI/lambada_multilingual_stablelm has seven language configs plus
    default, each with a test split of 5,153 rows (en, de, es, fr, it, nl, pt).
    Running the full group scores 7 × 5,153 = 36,071 passages. The README lists
    only en, fr, de, it, es; nl and pt YAML files exist and the Hub has those
    configs. marcob/lambada_multilingual is the Stability AI upload cited in
    the paper (created 2024-01-24; MIT); it also has nl and pt_br files. This
    session did not byte-compare marcob pt_br with EleutherAI pt.
  url: "https://huggingface.co/datasets/EleutherAI/lambada_multilingual_stablelm"
  license: "MIT on marcob/lambada_multilingual; EleutherAI mirror card states no licence field"
  languages:
    - en
    - de
    - es
    - fr
    - it
    - nl
    - pt
  modalities:
    - text
  splits: "test only, 5,153 rows per language config"
  public_test_set: true
publisher:
  org: "Stability AI (translations and report); EleutherAI (harness group and Hub mirror); original LAMBADA, University of Trento CIMeC and University of Amsterdam"
  authors:
    - "Marco Bellagente"
    - "Jonathan Tow"
    - "Dakota Mahan"
  url: "https://huggingface.co/datasets/EleutherAI/lambada_multilingual_stablelm"
paper:
  title: "Stable LM 2 1.6B Technical Report"
  arxiv: "2402.17834"
  url: "https://arxiv.org/abs/2402.17834"
  year: 2024
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/lambada_multilingual_stablelm"
released: "2024-02"
last_updated: "2025-11"
lineage:
  family: ""
  predecessor: "lambada"
  successors: []
  variants:
    - "lambada_multilingual"
    - "lambada_cloze"
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    English LAMBADA was already near ceiling in GPT-3 (see lambada.md). No dated
    numeric table for these Stable LM translation tasks was copied out of the
    report HTML here. Translation quality can dominate non-English accuracy.
contamination:
  risk: high
  note: >
    YAML sets should_decontaminate: true with the full passage as the query.
    English OpenAI LAMBADA has been public for years. The Stability AI files
    have been on Hugging Face since 2024-01-24 (marcob) and 2025-11-19
    (EleutherAI mirror). Machine translation does not hide the items.
harness:
  lm_eval: "lambada_multilingual_stablelm"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Runnable tasks lambada_openai_mt_stablelm_{en,de,es,fr,it,nl,pt}. Dataset path EleutherAI/lambada_multilingual_stablelm, not EleutherAI/lambada_openai."
tags:
  - language-modelling
  - cloze
  - multilingual
  - machine-translation
  - lambada
  - lm-eval
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/lambada_multilingual_stablelm/README.md"
    title: "lm-eval lambada_multilingual_stablelm README (group, Stable LM report, task names)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/lambada_multilingual_stablelm/lambada_mt_stablelm_en.yaml"
    title: "lambada_openai_mt_stablelm_en YAML (EleutherAI/lambada_multilingual_stablelm; acc and perplexity)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/lambada_multilingual_stablelm/lambada_mt_stablelm_nl.yaml"
    title: "lambada_openai_mt_stablelm_nl YAML (include en; dataset_name nl)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/EleutherAI/lambada_multilingual_stablelm"
    title: "EleutherAI/lambada_multilingual_stablelm card (7 configs × 5,153 test; created 2025-11-19)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/EleutherAI/lambada_multilingual_stablelm"
    title: "Hugging Face API for the EleutherAI mirror (no license field)"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=EleutherAI/lambada_multilingual_stablelm"
    title: "datasets-server split counts (5,153 test per config)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/marcob/lambada_multilingual"
    title: "marcob/lambada_multilingual (Stability AI upload; MIT; de/en/es/fr/it plus nl and pt_br files)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/marcob/lambada_multilingual"
    title: "marcob dataset API (created 2024-01-24; license mit)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2402.17834"
    title: "Stable LM 2 1.6B report HTML (rejects EleutherAI/lambada_openai MT; points to marcob)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2402.17834"
    title: "arXiv abs 2402.17834"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1606.06031"
    title: "Original LAMBADA paper (Paperno et al., 2016)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-053 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-053"
---

## What it measures

This group asks a language model to predict the last word of a short narrative
passage. The English items are the OpenAI reformat of [LAMBADA](lambada.md):
humans could guess the word from the full passage, not from the last sentence
alone. Non-English configs are new machine translations made for the Stable LM
2 1.6B technical report. The authors inspected [lambada_multilingual](lambada_multilingual.md)
(`EleutherAI/lambada_openai`) and called those googletrans files too noisy.
The intended skill is still discourse tracking. A bad translation of the target
word can fail the item even when the model followed the story.

## How it is scored

Each YAML task uses loglikelihood scoring. Accuracy is the fraction of passages
where the next-token ranking matches the gold last word. Perplexity is also
reported and is lower-is-better. There is no answer list and no partial credit.
The group name `lambada_multilingual_stablelm` runs every `lambada_openai_mt_stablelm_*`
task that carries that tag. Do not mix these numbers with `lambada_openai`,
`lambada_standard`, or `lambada_openai_mt_*` from the older multilingual group.

## Dataset and licence

The harness loads `EleutherAI/lambada_multilingual_stablelm`. The Hub API lists
test-only configs en, de, es, fr, it, nl, pt, and default, each 5,153 rows.
The EleutherAI card has no licence field. The report points to
`marcob/lambada_multilingual`, created 2024-01-24, card licence MIT, languages
de/en/es/fr/it in YAML plus `lambada_test_nl.jsonl` and `lambada_test_pt_br.jsonl`
in the repo. The harness README names five languages; nl and pt are extra
YAML includes. Original English LAMBADA is CC BY 4.0 on `cimec/lambada`. Labels
are the last tokens of public passages.

## Who publishes it

Stability AI described the translations in the Stable LM 2 1.6B report
(arXiv 2402.17834, 2024). EleutherAI hosts the harness group and a 2025-11-19
Hub mirror. The underlying cloze task is Paperno et al. 2016. There is no
separate live leaderboard for this group.

## Lineage

Predecessor: [lambada](lambada.md). Sibling group:
[lambada_multilingual](lambada_multilingual.md), which still uses
`EleutherAI/lambada_openai`. [lambada_cloze](lambada_cloze.md) is another
English formatting. The Stable LM files are a translation variant, not an
alias of the older mt tasks.

## Saturation and contamination

English LAMBADA has been easy for large models since GPT-3. Whether these
retranslations still separate models was not established from a dated table
here. The passages are public, and the YAML turns decontamination on using
the full text as the query.

## How to run it

In lm-evaluation-harness, run `lambada_multilingual_stablelm` or one
`lambada_openai_mt_stablelm_{en,de,es,fr,it,nl,pt}` task. Confirm
`dataset_path: EleutherAI/lambada_multilingual_stablelm`. Tokenization of the
gold last word still drives accuracy, as on English LAMBADA. A score on
`lambada_openai_mt_de` is not this German config.

## Reading the numbers

A high accuracy means the model assigned the gold last word the best
likelihood in that language’s translation. It does not mean the model can
write in that language. Compare language by language. Treat the README’s
five-language list as incomplete relative to the YAML. If a paper cites
`marcob/lambada_multilingual`, check whether it used `pt_br` rather than
`pt`.
