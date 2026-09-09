---
id: indic_dialect
name: "INDIC-DIALECT"
aliases:
  - "INDIC DIALECT"
  - "INDIC-DIALECT"
  - "Indic Dialect"
page_kind: benchmark
category: composite
subcategory: "Hindi and Odia dialect classification, translation MCQ, and dialect-standard machine translation"
status: unknown
summary: "Multi-task Hindi and Odia dialect suite: 11-way classification, translation MCQ, and dialect-standard MT over 13,000 native-speaker sentence pairs."
measures: >
  INDIC-DIALECT tests whether a model can handle regional Hindi and Odia dialects rather than
  only the standardized written forms used in news and Wikipedia. The suite has three tasks on
  the same parallel corpus. Dialect classification asks which of 11 named dialects a sentence
  belongs to. An MCQ task shows one dialect sentence and four standard-language candidates,
  one of them the true translation and three hard near-miss distractors. Machine translation
  runs in both directions: dialect to standard Hindi or Odia, and standard language to dialect.
  The skill is dialect-aware Indic NLP, not scheduled-language NLI or FLORES-style standard MT.
task_format: >
  Text in. Classification emits a dialect name. MCQ picks one of four standard-language
  options. MT emits a free-text translation. The paper's LLM classification prompt asks the
  model to reply with only the dialect name.
metric:
  name: "task-specific: classification and MCQ F1; MT BLEU (Papineni et al. 2002)"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: 9.09
  human_baseline: null
  baseline_note: >
    Classification is 11-way, so uniform chance is 1/11 (about 9.09%). The paper writes this
    as "1/11 or 9.99". GPT-4o zero-shot F1 is 4.25, below chance; Gemini 2.5 Pro zero-shot F1
    is 19.62. No human accuracy figure is reported. MT "baseline" is used two ways in the
    paper: the abstract compares hybrid BLEU 61.32 with rule-based 23.36, while the
    introduction compares it with the fine-tuned AI model at 46.5. Table 6 is the inventory:
    rule-based 23.36, AI 46.57, rule-then-AI 54.21, hybrid 61.32.
dataset:
  size: 13000
  size_note: >
    13,000 human-curated sentence pairs spanning 11 dialects and two standard languages
    (Hindi, Odia). Section 3.2 says 1,000 expert-written Hindi source sentences, covering
    science, history, culture, technology, arts, literature, and linguistics, were translated
    into the dialects and Odia by native speakers. Table 1 lists four Himachal Pradesh
    dialects (Kulluvi, Bilaspuri, Mandyali, Sirmouri), three Uttar Pradesh dialects (Meerut,
    Bhatner, Muzaffarnagar), and four Odisha dialects (Sambalpuri, Ganjami, Baleswari,
    Desia). Table 2 uses the spellings Meeruti and Bhatnair for two of those UP dialects.
    Fine-tuning uses a 70:30 train/test split; exact row counts per split are not tabulated.
    As of 2026-09-08 no official dataset URL was found. A Hugging Face search for
    INDIC-DIALECT returned an unrelated ASR set (grushaaaaa/indic-dialect-asr), not this corpus.
  url: ""
  license: ""
  languages:
    - hi
    - or
  modalities:
    - text
  splits: "70:30 train/test for fine-tuning experiments; no public files were found"
  public_test_set: null
publisher:
  org: "Indian Institute of Technology Mandi; Indian Institute of Technology Kanpur"
  authors:
    - "Tarun Sharma"
    - "Manikandan Ravikiran"
    - "Sourava Kumar Behera"
    - "Pramit Bhattacharya"
    - "Arnab Bhattacharya"
    - "Rohit Saluja"
  url: "https://arxiv.org/abs/2601.10388"
paper:
  title: "INDIC-DIALECT: A Multi-Task Benchmark to Evaluate and Translate in Indian Language Dialects"
  arxiv: "2601.10388"
  url: "https://arxiv.org/abs/2601.10388"
  year: 2026
leaderboard_url: ""
repo_url: ""
released: "2026-01"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: 89.75
  as_of: "2026-01"
  note: >
    Fine-tuned IndicBERT V2 reaches 89.75 F1 on 11-way dialect classification in the paper's
    own table, far above zero-shot GPT-4o (4.25) and Gemini 2.5 Pro (19.62). That number is
    a fine-tuned encoder on a private 70% split, not a frozen frontier LLM. MT remains much
    harder: the best dialect-to-language BLEU is 61.32 and the best language-to-dialect BLEU
    is 48.44. No later public leaderboard was found, so current saturation is not established.
contamination:
  risk: unknown
  note: >
    The authors say they plan to release the corpus as open source, but no dataset, licence
    file, or repository was found on 2026-09-08. The paper prints example sentences. If the
    70% training split is later posted in full, contamination risk would need a new reading.
    Risk is not rated high on present evidence because the test items are not known to be
    public as a downloadable set.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "No lm-evaluation-harness, inspect_evals, HELM, OpenCompass, or BIG-bench task name was found. The paper fine-tunes Hugging Face Transformers models; LLM classification is a one-line dialect-name prompt."
tags:
  - indic
  - dialects
  - hindi
  - odia
  - classification
  - translation
  - mcq
  - low-resource
sources:
  - url: "https://arxiv.org/abs/2601.10388"
    title: "INDIC-DIALECT: A Multi-Task Benchmark to Evaluate and Translate in Indian Language Dialects (Sharma et al., arXiv:2601.10388)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/pdf/2601.10388.pdf"
    title: "INDIC-DIALECT full PDF (Tables 1-7, annotation protocol, 70:30 split)"
    accessed: "2026-09-08"
  - url: "http://arxiv.org/licenses/nonexclusive-distrib/1.0/"
    title: "arXiv non-exclusive distribution license 1.0 (licence on the 2601.10388 abstract page)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets?search=INDIC-DIALECT&limit=20"
    title: "Hugging Face dataset search for INDIC-DIALECT (unrelated ASR hit only)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-077 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

INDIC-DIALECT asks whether models that look strong on standard Hindi or Odia still work on the dialects people actually speak. The authors start from 1,000 expert-written Hindi sentences and have native speakers produce aligned dialect and Odia versions, yielding 13,000 sentence pairs across 11 dialects from Himachal Pradesh, Uttar Pradesh, and Odisha.

Three tasks share that corpus. Classification labels a sentence with one of the 11 dialect names. MCQ shows a dialect sentence and four standard-language options, with three hard distractors built in the Hellaswag style. Machine translation runs dialect to standard language and the reverse. The benchmark is text-only. It is not [IndicXNLI](indicxnli.md), which is standard-language NLI, and it is not [FLORES](flores.md) standard-language translation.

## How it is scored

Classification and MCQ report precision, recall, and F1. Translation reports BLEU. Fine-tuning uses a 70:30 train/test split, five random seeds, AdamW at 2e-5, batch size 32, and 100 epochs for classification and MCQ or 150 for MT, on an NVIDIA RTX A6000.

Zero-shot GPT-4o scores 4.25 F1 on classification, below the 11-way chance rate of about 9.09%. Gemini 2.5 Pro scores 19.62 F1. Fine-tuned IndicBERT V2, pretrained on 24 Indian languages, reaches 89.75 F1. State-specific IndicBERT models beat a single 11-dialect model, especially on Uttar Pradesh dialects (83.50 vs 71.66 F1), which sit close to Hindi and to Himachal varieties.

MT needs more than a vanilla fine-tune. Table 6 (dialect to language) lists rule-based BLEU 23.36, a fine-tuned AI model 46.57, dictionary output then AI 54.21, and a hybrid that concatenates the dictionary draft with the source at 61.32. Table 7 (language to dialect) flips the ranking: rule-then-AI leads at 48.44, against AI-only 27.59, hybrid 33.82, and dictionary-only 31.71. The abstract's "baseline 23.36" is the rule-based row, not the AI row.

## Dataset and licence

Native speakers produced the dialect text. The authors recruited 23 annotators (two per dialect, one for Odia) and 11 dialect experts, paid above local minimum wage. A 5% double-annotated subset for translation judgment has mean Cohen's kappa 0.89. The remaining 95% was translated then expert-checked.

The paper's arXiv abstract page uses the arXiv non-exclusive distribution licence 1.0. No dataset licence, GitHub repository, or Hugging Face card for this corpus was found. Hugging Face search for the paper name returned only an unrelated Indic dialect ASR collection. Treat the 13,000-pair count as the paper's figure, not a datasets-server row count.

## Who publishes it

Tarun Sharma, Manikandan Ravikiran, Sourava Kumar Behera, and Rohit Saluja are at IIT Mandi. Pramit Bhattacharya and Arnab Bhattacharya are at IIT Kanpur. Sharma is corresponding author. The PDF was submitted to arXiv on 15 January 2026 as v1. No later version, venue camera-ready, or maintained leaderboard was found.

## Lineage

The authors place the work against IndicGLUE-style standard-language suites, VarDial 2018 Indo-Aryan identification, HinDialect, BanglaDialecto, and AI4Bharat Lahaja (Hindi ASR accents). None of those identification or speech sets is a parallel Hindi-Odia dialect MT benchmark. In this repository, related standard-language pages include [IndicXNLI](indicxnli.md), [FLORES](flores.md), [Belebele](belebele.md), and [Indic Cause and Effect](indic_cause_and_effect.md). Lahaja, VarDial, and HinDialect do not yet have pages. `grushaaaaa/indic-dialect-asr` is a different speech corpus that collides on the words "Indic dialect".

## Saturation and contamination

Classification looks close to solved for a fine-tuned Indic encoder, not for frozen LLMs. GPT-4o is below chance; Gemini 2.5 Pro is well below IndicBERT. Translation still has headroom, especially language-to-dialect generation. No independent rerun or later model table was found, so a current top score is not established beyond the January 2026 paper.

Contamination is unknown. The test split is not known to be downloadable. The paper prints examples. If the authors later post the full 70% training split, that reading should be revisited.

## How to run it

No public harness task name was found in lm-evaluation-harness, inspect_evals, HELM, OpenCompass, or BIG-bench. The paper's own protocol is Hugging Face Transformers fine-tunes, plus a one-line dialect-name prompt for GPT-4o and Gemini. Because the files are not posted, those numbers cannot be reproduced from this page. Do not load `grushaaaaa/indic-dialect-asr` and call it INDIC-DIALECT.

## Reading the numbers

A high classification F1 after IndicBERT fine-tuning means the encoder found dialect cues in this 11-way set. It does not mean a general LLM can name or translate those dialects zero-shot. GPT-4o's sub-chance F1 is the relevant warning for that claim. MT BLEU must name the direction and the method: hybrid 61.32 dialect-to-language is not comparable to rule-then-AI 48.44 the other way, and both used in-domain fine-tunes rather than a stock API. Until the authors publish the split files, treat every number as paper-only.
