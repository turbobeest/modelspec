---
id: cnn_dailymail_abisee
name: CNN/DailyMail (lm-eval, See et al. v3.0.0)
aliases:
  - cnn_dailymail
  - CNN/DailyMail
  - CNN-DM
  - abisee/cnn_dailymail
page_kind: benchmark
category: generation
subcategory: "English news abstractive summarization (non-anonymized CNN/DailyMail v3.0.0)"
status: active
summary: "lm-eval zero-shot abstractive summarization of CNN/DailyMail articles (See et al. version 3.0.0), scored with ROUGE-1/2/L and BERTScore."
measures: >
  cnn_dailymail_abisee is the runnable lm-evaluation-harness task that loads
  Hugging Face abisee/cnn_dailymail config 3.0.0. The model reads a CNN or
  Daily Mail article and writes a short multi-sentence summary. References are
  the journalist-written highlight bullets. Version 3.0.0 is the non-anonymized
  summarization split associated with See, Liu, and Manning's pointer-generator
  work, not Hermann et al.'s original cloze reading-comprehension dump.
task_format: >
  Zero-shot generation. Prompt: "Summarize the following article:" then the
  article then "Summary:". num_fewshot 0, max_gen_toks 128, do_sample false.
  YAML task field is cnn_dailymail_abisee; the directory is cnn_dailymail.
  The task README's "Tasks" list names cnn_dailymail, which does not match the
  YAML task key.
metric:
  name: "ROUGE-1/2/L F-measure and BERTScore P/R/F1"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No random baseline. The Hub card cites Zhong et al. (2020) ROUGE-1 44.41
    for an extractive system on this corpus; that is not this lm-eval prompt.
    BERTScore in utils.py uses distilbert-base-uncased, which is a cheaper
    encoder than the roberta-large setting the comments mention as optional.
dataset:
  size: 11490
  size_note: >
    lm-eval uses the test split of config 3.0.0: 11,490 articles. Full 3.0.0
    tables on the Hub card and datasets-server: train 287,113, validation
    13,368, test 11,490 (311,971). Configs 1.0.0 and 2.0.0 list the same split
    sizes on this card. Articles average 781 tokens and highlights 56 tokens
    on the card.
  url: "https://huggingface.co/datasets/abisee/cnn_dailymail"
  license: "Apache-2.0 (Hub card; licensing section names version 1.0.0)"
  languages:
    - en
  modalities:
    - text
  splits: "train 287,113 / validation 13,368 / test 11,490 (config 3.0.0); lm-eval test_split is test"
  public_test_set: true
publisher:
  org: DeepMind (original collection); Stanford / Google Brain (See et al. non-anonymized summarization code)
  authors:
    - Karl Moritz Hermann
    - Tomáš Kočiský
    - Edward Grefenstette
    - Abigail See
    - Peter J. Liu
    - Christopher D. Manning
  url: "https://github.com/abisee/cnn-dailymail"
paper:
  title: "Get To The Point: Summarization with Pointer-Generator Networks"
  arxiv: "1704.04368"
  url: "https://arxiv.org/abs/1704.04368"
  year: 2017
leaderboard_url: ""
repo_url: "https://github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/cnn_dailymail"
released: "2017"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: watch
  top_score: null
  as_of: ""
  note: >
    Classic extractive ROUGE-1 around the mid-40s is cited on the Hub card
    (Zhong et al. 2020, 44.41). LLM summarization on this prompt was not
    read from a current leaderboard. The task is old and widely trained on,
    so ROUGE gaps among strong models may be small even if this YAML has no
    posted ceiling.
contamination:
  risk: high
  note: >
    CNN/DailyMail has been a standard pretraining and distillation corpus for
    years. Highlights and articles are public. Version 3.0.0 does not hold
    answers out.
harness:
  lm_eval: cnn_dailymail_abisee
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: ""
tags:
  - summarization
  - generation
  - rouge
  - lm-eval
  - news
sources:
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/cnn_dailymail/cnn_dailymail.yaml"
    title: "lm-eval cnn_dailymail.yaml (task: cnn_dailymail_abisee)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/cnn_dailymail/README.md"
    title: "lm-eval CNN-DailyMail README"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/lm_eval/tasks/cnn_dailymail/utils.py"
    title: "lm-eval CNN/DailyMail metrics utils"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/abisee/cnn_dailymail"
    title: "Hugging Face abisee/cnn_dailymail"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/abisee/cnn_dailymail/raw/main/README.md"
    title: "abisee/cnn_dailymail dataset card"
    accessed: "2026-09-08"
  - url: "https://datasets-server.huggingface.co/info?dataset=abisee/cnn_dailymail"
    title: "datasets-server split counts"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1704.04368"
    title: "See, Liu, Manning 2017 pointer-generator paper"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/1506.03340"
    title: "Hermann et al. 2015 original CNN/DailyMail QA paper"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-031 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-031"
---

## What it measures

This id is lm-eval's CNN/DailyMail summarization task. The model is given a news article and must write a short abstractive summary. The reference is the article's highlight bullets, concatenated. Language is English. The Hub config is `abisee/cnn_dailymail` version `3.0.0`, the non-anonymized summarization tables associated with Abigail See's processing code.

Hermann et al. (2015) first released CNN and Daily Mail articles as cloze reading-comprehension data with anonymized entities. See, Liu, and Manning (ACL 2017) used a non-anonymized highlight-summary form for pointer-generator summarization. lm-eval's YAML loads that later form. The task README still leads with the 2015 paper, which is the corpus origin, not this prompt.

## How it is scored

lm-eval generates up to 128 tokens, then `utils.process_results` computes ROUGE-1/2/L F-measures with stemming and BERTScore precision, recall, and F1. BERTScore is wired to `distilbert-base-uncased`. There is no single official headline; reports usually quote ROUGE-2 or ROUGE-L. Zhong et al.'s 44.41 ROUGE-1 on the Hub card is an extractive system, not this zero-shot prompt.

A 128-token cap is shorter than some highlight concatenations. Truncation can hurt ROUGE even when the model is on topic.

## Dataset and licence

Test has 11,490 examples; train 287,113; validation 13,368. The Hub card states Apache-2.0 in the YAML licence field, and the licensing section names version 1.0.0. News-article copyright beyond that card statement was not independently checked. Answers (highlights) are public.

CNN articles in the original collection run April 2007–April 2015; Daily Mail June 2010–April 2015. Mean article length on the card is 781 tokens; highlights 56.

## Who publishes it

Karl Moritz Hermann and DeepMind coauthors collected the articles. Abigail See (Stanford), Peter J. Liu (Google Brain), and Christopher D. Manning published the 2017 pointer-generator paper and the non-anonymized processing repo `abisee/cnn-dailymail`. EleutherAI's harness adds the YAML task. Papers with Code still lists a document-summarization board for the corpus; that board was not scraped here.

## Lineage

Hermann 2015 is the cloze/QA origin. Nallapati and others recast highlights as summaries. See et al. 2017 popularized the non-anonymized abstractive split (v3.0.0). This repository has [xlsum](xlsum.md) for multilingual BBC lead summarization and [legal_summarization](legal_summarization.md) for HELM legal ROUGE. Neither is CNN/DailyMail. There is no separate `cnn_dailymail` page; this assigned id is the harness task key.

The Hub card's "Paper" line once points at ACL anthology K16-1028 for the pointer-generator work. The citation block on the same card correctly uses P17-1099 / See et al. 2017. This page follows the citation block and arXiv 1704.04368.

## Saturation and contamination

News summarization on CNN/DailyMail is a mature ROUGE task. Extractive systems already sat in the mid-40s ROUGE-1 years ago. For this exact lm-eval prompt, no current model table was opened, so no lm-eval top score is stored. Status is watch: the corpus is old, public, and heavily trained on.

Contamination risk is high. Many language-model corpora include these articles and highlights.

## How to run it

```bash
lm-eval --tasks cnn_dailymail_abisee
```

That string is the YAML `task:` field. The folder name and the README's task list say `cnn_dailymail`. If a runner only indexes directory names, confirm that `cnn_dailymail_abisee` is registered. The Hub path in YAML is `abisee/cnn_dailymail`, not `cnn_dailymail`.

ROUGE implementations and BERTScore encoders change numbers. This file uses `rouge_score` with stemming and DistilBERT. A paper that used `roberta-large` BERTScore is not this task.

## Reading the numbers

A strong ROUGE-2 here means the 128-token summary overlapped the highlights on bigrams. It does not mean the summary is faithful; CNN/DailyMail ROUGE is known to reward lead bias. It does not mean the model can summarize other domains; see [xlsum](xlsum.md) or [legal_summarization](legal_summarization.md). Quote ROUGE-1/2/L and BERTScore together, and name version 3.0.0. If someone reports `cnn_dailymail` without `_abisee`, check whether they ran this YAML or another copy of the corpus.
