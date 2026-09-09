---
id: uncheatable_eval
name: "Uncheatable Eval"
aliases:
  - "UncheatableEval"
  - "UE"
page_kind: benchmark
category: generation
subcategory: "rolling log-likelihood / bits-per-byte on newly published web documents"
status: active
summary: "Rolling perplexity on monthly snapshots of new Wikipedia, GitHub, BBC, arXiv, bioRxiv and AO3 text, meant to limit train-set leakage."
measures: >
  Uncheatable Eval does not ask questions. It scores how well a causal language model
  assigns probability to documents published after typical training cutoffs: new Wikipedia
  pages, GitHub files, BBC news, arXiv and bioRxiv papers, and AO3 fiction. The publisher
  argues that a public static QA set can leak into training, while last-week's crawl cannot
  already be in a released checkpoint. lm-eval implements the upstream rolling log-likelihood
  over a pinned Hub snapshot. The README says the method is for base models, not chat-tuned
  ones.
task_format: >
  output_type loglikelihood_rolling. doc_to_text is empty; doc_to_target is the document
  content field. Fifteen category tasks filter the snapshot on the category column. Group
  uncheatable_eval averages word_perplexity, byte_perplexity and bits_per_byte weighted by
  size. Lower is better for all three.
metric:
  name: "bits_per_byte (also word_perplexity and byte_perplexity)"
  direction: lower_is_better
  unit: "bpb"
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    There is no bounded maximum. The original README equates the sum of negative log
    probabilities with arithmetic-coding compression rate and prefers comparing systems
    (model plus tokenizer) on compression, not tokenizer-dependent word perplexity.
    lm-eval still reports all three. Numbers are only comparable on the same snapshot.
    No human or random baseline is defined.
dataset:
  size: 7500
  size_note: >
    Hugging Face Jellyfish042/UncheatableEval-2026-07, the snapshot pinned in
    _uncheatable_eval_base.yaml, has a single test split of 7,500 rows (datasets-server
    and the dataset card agree). Fifteen category filters: wikipedia_english,
    wikipedia_nonenglish, github_python, github_cpp, github_javascript, github_markdown,
    github_other, bbc_news, arxiv_physics, arxiv_math, arxiv_cs, arxiv_other,
    biorxiv_all, ao3_english, ao3_nonenglish. Per-category row counts were not re-counted
    from parquet. New monthly dumps appear on the UncheatableEval collection.
  url: "https://huggingface.co/datasets/Jellyfish042/UncheatableEval-2026-07"
  license: "MIT on the evaluation code (Jellyfish042/uncheatable_eval). The 2026-07 Hub card states no dataset licence."
  languages: []
  modalities:
    - text
    - code
  splits: "single test split per snapshot; lm-eval test_split: test"
  public_test_set: true
publisher:
  org: "Jellyfish042"
  authors:
    - "Jellyfish042"
  url: "https://github.com/Jellyfish042/uncheatable_eval"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: "https://huggingface.co/spaces/Jellyfish042/UncheatableEval"
repo_url: "https://github.com/Jellyfish042/uncheatable_eval"
released: "2024-05"
last_updated: "2026-08"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: null
  as_of: ""
  note: >
    Snapshots rotate. A ceiling on one month is not a ceiling on the next. The GitHub
    README plots compression rate by size class (about 1.5B, 3B, 7B, 14B) but those
    figures are images, not a transcribed numeric top score. The lm-eval pin is the
    2026-07 dump, last updated on the Hub on 2026-08-06.
contamination:
  risk: low
  note: >
    The design is to crawl documents from a recent window so released models cannot have
    trained on them. Once a snapshot is public on the Hub, later training runs can ingest
    it; compare a model only to snapshots dated after its training cutoff. Risk is low
    relative to static 2021 QA sets, not zero for models trained after the dump date.
harness:
  lm_eval: "uncheatable_eval"
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Group uncheatable_eval (alias Uncheatable Eval) lists the 15 category tasks. Example
    task uncheatable_eval_wikipedia_english (alias UE_wiki_en). dataset_path in
    _uncheatable_eval_base.yaml is Jellyfish042/UncheatableEval-2026-07; bump that path
    to change months. Upstream evaluator.py is the reference implementation.
tags:
  - perplexity
  - bits-per-byte
  - contamination-resistant
  - language-modeling
  - dynamic-data
sources:
  - url: "https://github.com/Jellyfish042/uncheatable_eval"
    title: "Jellyfish042/uncheatable_eval README (dynamic crawl, NLL, MIT, Zenodo)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/Jellyfish042/uncheatable_eval/master/LICENSE"
    title: "MIT licence on the evaluation code"
    accessed: "2026-09-08"
  - url: "https://zenodo.org/records/11284692"
    title: "Zenodo 10.5281/zenodo.11284692, version 0.1, May 2024"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/Jellyfish042/UncheatableEval-2026-07/raw/main/README.md"
    title: "UncheatableEval-2026-07 card: 7,500 test rows, no licence field"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=Jellyfish042/UncheatableEval-2026-07"
    title: "datasets-server: test split 7,500 examples"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/uncheatable_eval/README.md"
    title: "lm-eval uncheatable_eval README (group, 15 tasks, 2026-07 pin)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/uncheatable_eval/_uncheatable_eval_base.yaml"
    title: "Base YAML: rolling NLL, bpb, 2026-07 dataset_path"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/spaces/Jellyfish042/UncheatableEval"
    title: "UncheatableEval Gradio leaderboard space (page opened; scores are JS-rendered)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/collections/Jellyfish042/uncheatableeval"
    title: "Hub collection listing monthly UncheatableEval-YYYY-MM snapshots"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-023 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-023"
---

## What it measures

Uncheatable Eval measures language-model likelihood on text that did not exist when most public checkpoints were trained. Crawlers pull recent Wikipedia, GitHub, BBC, arXiv, bioRxiv and AO3 documents. A model that assigns higher probability to that text is treated as stronger. There is no question, no gold answer, and no accuracy. The publisher frames it as a leakage-resistant substitute for static benchmarks and as a compression test: better models should compress the same bytes into fewer bits.

lm-eval does not crawl. It scores a frozen Hub snapshot. The YAML pin at the time of this page is `Jellyfish042/UncheatableEval-2026-07`.

## How it is scored

Each document is scored with rolling log-likelihood. lm-eval reports word perplexity, byte perplexity, and bits per UTF-8 byte, all lower-is-better. The group average is size-weighted. Word perplexity is not comparable across tokenizers; bits-per-byte is. Two models compared on different months are not comparable. The README tells users to pick `bos_mode` with `bos_mode_finder.py` before claiming a number.

## Dataset and licence

The 2026-07 card lists 7,500 test rows with fields `content`, `untruncated_content`, `category`, `date`, `url` and `metadata`. Code in `Jellyfish042/uncheatable_eval` is MIT (copyright 2024 Jellyfish042). The snapshot card has no licence field; do not assume MIT covers BBC, AO3 or arXiv text. The collection also lists 2025-12, 2026-01, 2026-04 and 2026-07 dumps (plus Long variants). Zenodo records version 0.1 on 24 May 2024 (DOI 10.5281/zenodo.11284692).

## Who publishes it

The project is maintained by GitHub user Jellyfish042 as software, not as a peer-reviewed paper. A Gradio space is advertised as a leaderboard; the page loads as a Hugging Face Space shell and this research did not read numeric ranks off it.

## Lineage

This is a dynamic language-modelling eval, closer in spirit to [The Pile](pile.md) bits-per-byte group than to a QA set. It is not a replacement id for Pile. No successor id is in this repository. The name "uncheatable" is a claim about leakage, not a proof that a model never saw similar text from earlier months.

## Saturation and contamination

The task stays open because the documents change. A small bpb on 2026-07 says nothing about 2026-10. Contamination risk is low for checkpoints whose training ended before the snapshot window, and higher for models trained after the dump became public. That is the point of dating the snapshot in the reported score.

## How to run it

```bash
lm_eval --model hf --model_args pretrained=<base-model> --tasks uncheatable_eval
```

Upstream: clone `Jellyfish042/uncheatable_eval`, set `EvaluationConfig.data` to a Hub snapshot, run `eval_single.py`. Always name the snapshot next to the number. Do not run this as a chat-template eval unless you have shown the template does not change the rolling NLL.

## Reading the numbers

A lower bpb means the model plus tokenizer assign more probability to that month's documents, not that it answers facts correctly. Domain mix matters: GitHub Python and AO3 English are different skills. Report the snapshot id, `bos_mode`, and whether the run was a base model. If you need a static QA number as well, use a held-out set rather than treating this as a drop-in TruthfulQA or MMLU substitute.
