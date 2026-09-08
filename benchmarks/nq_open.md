---
id: nq_open
name: "NQ-Open"
aliases:
  - "NQ-open"
  - "nq-open"
  - "Natural Questions Open"
page_kind: benchmark
category: knowledge
subcategory: "closed-book short-answer QA on real Google queries derived from Natural Questions"
status: active
summary: "Closed-book short-answer QA on real Google queries from Natural Questions, usually scored by exact match on the public 3,610-item original NQ-Open dev split."
measures: >
  This id is EleutherAI lm-eval task nq_open and the NQ-Open task of Lee, Chang
  and Toutanova (ACL 2019). It is not HELM natural_qa and not the 2019
  long-answer span-selection competition. Each item is an English question from
  aggregated Google searches. The model must emit a short answer string with no
  Wikipedia page in the prompt. Lee et al. keep Natural Questions items that
  have a short answer of at most five tokens and drop the evidence document.
  All questions are answerable from English Wikipedia in principle.
task_format: >
  lm-eval generate_until. Prompt "Q: {question}?\nA:" after a few-shot header
  "Answer these questions:\n\n". Stops at newline, period or comma. Greedy
  decoding (temperature 0). English text.
metric:
  name: "exact match (lm-eval exact_match; official NQ-Open also uses EM against answer aliases)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Official NQ-Open evaluation is exact match to any listed answer after light
    normalisation (Lee et al.; Google evaluate_predictions.py). lm-eval reports
    exact_match with ignore_case, ignore_punctuation, and a regex that strips
    leading articles. The YAML sets doc_to_target to "{{answer}}" and comments
    that the target should be multi-answer; treat single-string versus
    multi-alias scoring as a protocol gap. Official README baselines on original
    dev: TF-IDF nearest question 22%, T5-XXL 37%, REALM 40%, DPR 41%. Those are
    2020-era retrieval or closed-book systems, not a human ceiling. Original NQ
    human F1 (76% short-answer span selection) is a different task.
dataset:
  size: 3610
  size_note: >
    lm-eval loads google-research-datasets/nq_open and scores the validation
    split. Hugging Face and the official nq_open README agree: train 87,925,
    original dev 3,610 (91,535 labelled rows; EfficientQA has separate 1,800 /
    1,769 files that this task does not use). Lee et al. 2019 Table 3 instead
    lists Natural Questions open splits as train 79,168 / dev 8,757 / test 3,610.
    This page follows the Google README and Hugging Face counts for the files
    lm-eval actually reads. EfficientQA used different dev/test cuts (Min et al.
    2021).
  url: "https://huggingface.co/datasets/google-research-datasets/nq_open"
  license: "CC BY-SA 3.0 (nq_open README and Hugging Face card); natural-questions GitHub LICENSE file is Apache-2.0 for the repository"
  languages:
    - en
  modalities:
    - text
  splits: "Hugging Face: train 87,925 / validation 3,610. lm-eval uses validation. Official also ships EfficientQA dev/test jsonl."
  public_test_set: true
publisher:
  org: "Google Research"
  authors:
    - "Kenton Lee"
    - "Ming-Wei Chang"
    - "Kristina Toutanova"
  url: "https://github.com/google-research-datasets/natural-questions/tree/master/nq_open"
paper:
  title: "Latent Retrieval for Weakly Supervised Open Domain Question Answering"
  arxiv: "1906.00300"
  url: "https://aclanthology.org/P19-1612/"
  year: 2019
leaderboard_url: "https://ai.google.com/research/NaturalQuestions/efficientqa"
repo_url: "https://github.com/google-research-datasets/natural-questions/tree/master/nq_open"
released: "2019"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors:
    - simpleqa
  variants: []
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: >
    Wei et al. SimpleQA (arXiv 2411.04368) name Natural Questions, with TriviaQA,
    as an older factual-recall set that is now saturated. No 2026 closed-book
    lm-eval top EM was copied from a live board, so top_score is empty. Status
    is watch rather than saturated because EfficientQA and retrieval settings
    are different numbers.
contamination:
  risk: high
  note: >
    Questions and answer aliases have been public since 2019. lm-eval scores the
    public original-dev file, not a sequestered test. Closed-book EM is exposed
    to memorisation of popular queries.
harness:
  lm_eval: "nq_open"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    YAML version 4.0. dataset_path google-research-datasets/nq_open.
    OpenCompass also ships NQOpenDataset (nq-open-{train,validation}.jsonl) and
    a separate Chinese nq_cn config; those are not this lm-eval id.
tags:
  - question-answering
  - wikipedia
  - closed-book
  - google-search
  - lm-eval
sources:
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/nq_open/nq_open.yaml"
    title: "lm-eval nq_open.yaml (prompt, exact_match, stop sequences)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/nq_open/README.md"
    title: "lm-eval nq_open README"
    accessed: "2026-09-08"
  - url: "https://github.com/google-research-datasets/natural-questions/blob/master/nq_open/README.md"
    title: "Official NQ-Open README (87,925 / 3,610; CC BY-SA 3.0; EfficientQA splits)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/google-research-datasets/nq_open"
    title: "Hugging Face nq_open card (counts; five-token filter; CC BY-SA 3.0)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/google-research-datasets/nq_open"
    title: "Hugging Face nq_open API split counts"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/P19-1612/"
    title: "Lee et al. ACL 2019 (NQ-Open task; Table 3 split disagreement)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/1906.00300"
    title: "arXiv 1906.00300 HTML (Table 3: 79,168 / 8,757 / 3,610; five-token filter)"
    accessed: "2026-09-08"
  - url: "https://aclanthology.org/Q19-1026/"
    title: "Kwiatkowski et al. TACL 2019 Natural Questions"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2411.04368"
    title: "SimpleQA paper (NQ named as saturated recall set)"
    accessed: "2026-09-08"
  - url: "https://github.com/stanford-crfm/helm/blob/main/src/helm/benchmark/scenarios/natural_qa_scenario.py"
    title: "HELM natural_qa scenario (different id; cited to keep the split clear)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-013 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-013"
---

## What it measures

`nq_open` is closed-book English question answering on Natural Questions.
The question is a real aggregated Google query. The model must produce a short
string. No Wikipedia HTML is shown. Lee et al. built the open task by keeping
short answers of at most five tokens and dropping the evidence document.

This is not the 2019 long-answer candidate-selection contest. It is not HELM
[natural_qa](natural_qa.md), which scores token F1 in closed-book or open-book
modes on filtered official NQ dev shards.

## How it is scored

The usual number is exact match on the original 3,610-item dev split. Google’s
script compares the prediction to every listed alias after light cleanup.
lm-eval uses `exact_match` with case and punctuation ignored and leading
articles stripped, greedy generation, and hard stops at `.` `,` or newline.
The YAML still interpolates `{{answer}}` and notes that multi-target scoring
is unfinished, so two lm-eval runs can disagree with the official multi-alias
script. EfficientQA numbers use different files and extra rated aliases
(Min et al. 2021).

## Dataset and licence

Google’s nq_open README and Hugging Face list train 87,925 and original dev
3,610. EfficientQA adds 1,800 / 1,769. Lee et al. Table 3 instead prints
79,168 / 8,757 / 3,610. This page uses the hosted files. The nq_open README
and HF card say CC BY-SA 3.0 for the data. The parent repository LICENSE is
Apache-2.0, the same split already noted on [natural_qa](natural_qa.md).
The GitHub project is archived (API `archived` true; archive date not returned).

## Who publishes it

NQ-Open is Google Research: Lee, Chang and Toutanova (ACL 2019, P19-1612),
derived from Kwiatkowski et al. (TACL 2019). lm-eval maintains the closed-book
task YAML (version 4.0). EfficientQA (NeurIPS 2020) reused the format with
new splits.

## Lineage

[TriviaQA](triviaqa.md) is the other widely reported 2010s open-domain set.
[SimpleQA](simpleqa.md) is a later factual-recall benchmark that names NQ as
saturated. [natural_qa](natural_qa.md) is HELM’s wrap of original NQ, not this
id. OpenCompass `nq_cn` is a Chinese-prompt config with its own matcher.

## Saturation and contamination

SimpleQA’s authors treat NQ as a saturated recall set. lm-eval still reports
dev EM, but a high 2026 closed-book number on a 2019 public file is weak
evidence of current factuality. Contamination is high.

## How to run it

`lm_eval --tasks nq_open`. State shot count (the YAML ships a few-shot
header), stop sequences, and whether scoring is multi-alias. Do not mix with
HELM F1, EfficientQA test, or OpenCompass `nq` / `nq_cn`.

## Reading the numbers

A strong original-dev EM means the model emitted a normalised alias for
2018-era Google queries. It does not measure browsing, citation or
post-cutoff facts. Prefer [SimpleQA](simpleqa.md) or [BrowseComp](browsecomp.md)
when the claim is current knowledge, and always name closed-book versus
retrieved-evidence NQ-Open.
