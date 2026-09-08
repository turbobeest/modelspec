---
id: lambada_cloze
name: "LAMBADA Cloze"
aliases:
  - "lambada openai cloze"
  - "lambada standard cloze"
page_kind: benchmark
category: reasoning
subcategory: "cloze-format last-word prediction on LAMBADA passages"
status: unknown
summary: "The LAMBADA last-word task with an explicit cloze blank in the prompt, scored as log-likelihood accuracy on the withheld word."
measures: >
  lambada_cloze is EleutherAI's cloze presentation of the LAMBADA dataset, not a new passage set.
  The model still sees a narrative passage whose final word is withheld, and must assign highest
  probability to that word. The cloze YAMLs differ from lambada_standard and lambada_openai only
  in the prompt: after the passage-without-last-word they insert a visible blank of the form
  " ____. ->" before scoring the last word. The original 2016 construction still applies: humans
  could guess the word from the full passage and could not from the last sentence alone.
task_format: "Cloze / language modelling: passage with last word replaced by an explicit blank, scored as log-likelihood of the true last word rather than free generation or multiple choice."
metric:
  name: "accuracy (log-likelihood exact match on the last word); perplexity also reported"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Same as LAMBADA: no random baseline for open-vocabulary last-word prediction. The cloze
    YAMLs report acc (higher is better) and perplexity (lower is better). No cloze-specific
    human figure is given beyond the original dataset filter. The two cloze tasks are not
    guaranteed to match each other or the non-cloze lambada_standard / lambada_openai numbers.
dataset:
  size: 5153
  size_note: >
    Same LAMBADA test passages as lambada: 5,153 test items. lambada_standard_cloze_yaml loads
    cimec/lambada (validation 4,869 plus test 5,153; card licence CC BY 4.0).
    lambada_openai_cloze_yaml loads EleutherAI/lambada_openai default, test split only, 5,153
    examples on the Hugging Face API (card licence MIT). No new items are authored for the cloze
    group.
  url: "https://huggingface.co/datasets/cimec/lambada"
  license: "CC BY 4.0"
  languages:
    - en
  modalities:
    - text
  splits: "standard cloze: validation + test; openai cloze: test only"
  public_test_set: true
publisher:
  org: "University of Trento (CIMeC); University of Amsterdam (dataset). EleutherAI (cloze harness configs)"
  authors:
    - "Denis Paperno"
    - "Germán Kruszewski"
    - "Angeliki Lazaridou"
    - "Quan Ngoc Pham"
    - "Raffaella Bernardi"
    - "Sandro Pezzelle"
    - "Marco Baroni"
    - "Gemma Boleda"
    - "Raquel Fernández"
  url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/lambada_cloze"
paper:
  title: "The LAMBADA dataset: Word prediction requiring a broad discourse context"
  arxiv: "1606.06031"
  url: "https://arxiv.org/abs/1606.06031"
  year: 2016
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/lambada_cloze"
released: "2016-08"
last_updated: ""
lineage:
  family: ""
  predecessor: "lambada"
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    No EleutherAI cloze-YAML leaderboard figure was opened. GPT-3 few-shot 86.4% (Brown et al.,
    2020, Table 3.2) used a fill-in-the-blank prompt with a blank and an arrow, not a raw LM
    prefix; it is still not a score for lambada_*_cloze_yaml (zero-shot log-likelihood,
    " ____. ->"). GPT-3 zero-shot without that framing was 76%.
contamination:
  risk: high
  note: >
    Same passages as LAMBADA, public since 2016. GPT-3 reported a significant minority of
    LAMBADA in its training data, with a clean subset within 0.5% of the full set, and noted
    that fill-in-the-blank framing blocks the simplest verbatim continuation. Both cloze YAMLs
    set should_decontaminate true with the full passage as the query. The EleutherAI blank does
    not make the last words private.
harness:
  lm_eval: "lambada_openai_cloze_yaml, lambada_standard_cloze_yaml (group lambada_cloze)"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Runnable task names include the _yaml suffix as written in the EleutherAI YAMLs.
    OpenCompass abbr lambada is a different protocol (generation: "Please complete the
    following sentence"), not this cloze group.
tags:
  - language-modelling
  - cloze
  - long-range-dependency
  - zero-shot
  - narrative
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/lambada_cloze/README.md"
    title: "lm-evaluation-harness lambada_cloze README (group and task names)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/lambada_cloze/lambada_standard_cloze.yaml"
    title: "lambada_standard_cloze.yaml (cimec/lambada; cloze doc_to_text)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/lambada_cloze/lambada_openai_cloze.yaml"
    title: "lambada_openai_cloze.yaml (EleutherAI/lambada_openai; cloze doc_to_text)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/lambada/lambada_standard.yaml"
    title: "lambada_standard.yaml (non-cloze control: same dataset, no blank)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1606.06031"
    title: "The LAMBADA dataset (Paperno et al., 2016)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/cimec/lambada/raw/main/README.md"
    title: "cimec/lambada dataset card (CC BY 4.0; test 5,153)"
    accessed: "2026-09-08"
  - url: "https://zenodo.org/records/2630551"
    title: "The LAMBADA dataset, Zenodo record"
    accessed: "2026-09-08"
  - url: "https://zenodo.org/api/records/2630551"
    title: "Zenodo API record 2630551 (license id cc-by-4.0; publication_date 2016-08-07)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/EleutherAI/lambada_openai"
    title: "EleutherAI/lambada_openai API (default test 5,153; license MIT)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2005.14165"
    title: "GPT-3 paper HTML (LAMBADA few-shot cloze 86.4%; contamination note)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2005.14165"
    title: "Language Models are Few-Shot Learners (arXiv:2005.14165)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/lambada/lambada_gen_217e11.py"
    title: "OpenCompass lambada_gen_217e11.py (abbr lambada; sentence-completion, not cloze YAML)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-010 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-010"
---

## What it measures

lambada_cloze is the LAMBADA last-word problem with a visible cloze blank. The passages are the same English narrative excerpts used by [LAMBADA](lambada.md): several sentences of context, then a final sentence whose last word was filtered so that people need the whole passage to guess it. lm-evaluation-harness does not change the items. It only changes the prompt. The non-cloze tasks feed the passage minus the last word straight to a causal language model. The cloze tasks append ` ____. ->` after that prefix and then score the true last word. The extra blank is a format cue, not a new comprehension skill. English narrative text only.

## How it is scored

Scoring is log-likelihood, not generation. Accuracy is the fraction of passages where the true last word is the highest-probability continuation of the cloze prompt; perplexity over that continuation is also reported. There is no choice list and no partial credit. Two YAMLs exist under the `lambada_cloze` group: `lambada_standard_cloze_yaml` on `cimec/lambada` (validation and test) and `lambada_openai_cloze_yaml` on `EleutherAI/lambada_openai` (test only). Those two passage tokenisations already differ on the parent task; the cloze blank is a third axis. A number from `lambada_openai` is not a number from `lambada_openai_cloze_yaml`. The 2016 paper does not define this blank. GPT-3 few-shot 86.4% used a related fill-in-the-blank format with a blank and an arrow, not this YAML's zero-shot log-likelihood protocol.

## Dataset and licence

The item pool is LAMBADA: 4,869 development and 5,153 test passages from disjoint novels, plus a separate 2,662-novel background corpus that is not scored here. Hugging Face `cimec/lambada` lists `cc-by-4.0`. The Zenodo API for record 2630551 reports licence id `cc-by-4.0` and publication_date 2016-08-07. `EleutherAI/lambada_openai` used by the openai cloze YAML lists MIT on the Hub API. Both cloze YAMLs set `should_decontaminate: true` and use the full passage as the decontamination query. Answers (the last words) have been public since 2016.

## Who publishes it

The dataset is still Paperno, Kruszewski, Lazaridou, Pham, Bernardi, Pezzelle, Baroni, Boleda (University of Trento, CIMeC) and Fernández (University of Amsterdam), ACL 2016, archived on Zenodo. The cloze configs are EleutherAI's, in lm-evaluation-harness under `lm_eval/tasks/lambada_cloze`. The cloze README's checklist for "what each new variant adds" is unchecked; the files themselves are the specification. No organisation runs a cloze-specific leaderboard.

## Lineage

This page is a harness variant of [LAMBADA](lambada.md), not a successor dataset. Predecessor id `lambada`. It is not a spelling of `lambada_standard` or `lambada_openai`: those tasks omit the blank. GPT-3 (2020) already framed few-shot LAMBADA as a cloze test with a blank and an arrow; EleutherAI's YAMLs are a later zero-shot log-likelihood spelling of that idea, not that paper's few-shot generation setup. It is also not StoryCloze (`storycloze` in this repository), which is a different narrative-ending dataset.

## Saturation and contamination

No score from `lambada_standard_cloze_yaml` or `lambada_openai_cloze_yaml` was opened as a current top result. GPT-3's 86.4% few-shot figure used a fill-in-the-blank prompt, so it is a historical cloze-style snapshot, not a number for these YAMLs. GPT-3 zero-shot without that framing was 76%. Contamination risk is high: the passages are old and public, and GPT-3 already reported substantial genuine overlap with its training data. The decontamination flag in the YAMLs only helps if the runner actually filters overlapping training documents.

## How to run it

In lm-evaluation-harness, run the group `lambada_cloze` or the tasks `lambada_standard_cloze_yaml` and `lambada_openai_cloze_yaml`. The `_yaml` suffix is part of the published `task:` field. OpenCompass abbr `lambada` (`lambada_gen_217e11.py`) asks the model to complete a sentence in generation, not this cloze group. Because both accuracy and perplexity depend on tokenisation, compare two cloze numbers only when they used the same YAML and the same tokenizer.

## Reading the numbers

A high cloze accuracy means the model can still pick LAMBADA's last word when the prompt looks like a fill-in-the-blank exam rather than raw next-token prediction. It does not measure a new discourse skill beyond LAMBADA, and it does not tell you whether the model would have scored the same without the blank. Do not treat GPT-3's 86.4% few-shot cloze figure as a result for `lambada_*_cloze_yaml`. Report which of the two cloze YAMLs produced the number, and put a non-cloze LAMBADA score next to it before treating either as evidence of long-range understanding. Given the 2016 public targets, a strong score today is a weak claim about contamination-free comprehension.
