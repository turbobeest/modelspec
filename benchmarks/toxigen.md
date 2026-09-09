---
id: toxigen
name: ToxiGen
aliases: []
page_kind: benchmark
category: safety
subcategory: implicit hate speech detection
status: active
summary: A machine-generated dataset of 274,000 toxic and benign statements about 13 minority groups, used to test whether models can catch subtle, implicit hate speech.
measures: ToxiGen targets implicit and adversarial toxicity - text that is hateful in effect without using slurs or other easily-flagged surface markers - directed at 13 minority groups. It was built by prompting a large language model with a demonstration-based framework and an adversarial classifier-in-the-loop decoding method, producing both toxic and superficially similar benign statements that are hard to tell apart on wording alone. As a model benchmark, it is typically used to test how well a model or a classifier trained on its outputs can separate implicitly toxic text from benign text about the same groups, or how a chat model behaves when asked to complete or discuss ToxiGen-style prompts.
task_format: Binary classification of statements as toxic or benign (as a classifier benchmark), or completion/discussion of ToxiGen-style prompts scored for toxic output (as a generation safety check).
metric:
  name: classification accuracy / toxicity rate
  direction: higher_is_better
  unit: '%'
  max_score: 100.0
  random_baseline: 50.0
  human_baseline: null
  baseline_note: The original paper reports human annotators labeled 94.5% of the machine-generated toxic examples as hate speech, and used ToxiGen to fine-tune HateBERT and RoBERTa classifiers, which is the paper's own reference use of the dataset. Exact scoring in a given report depends on whether it measures classifier accuracy on held-out ToxiGen examples or a generative model's toxic-output rate on ToxiGen prompts, which are not the same number.
dataset:
  size: 274000
  size_note: 274,000 machine-generated toxic and benign statements about 13 minority groups; a later release added 27,450 human annotations over a subset.
  url: https://github.com/microsoft/TOXIGEN
  license: CC BY 4.0
  languages:
  - en
  modalities:
  - text
  splits: not established
  public_test_set: true
publisher:
  org: Microsoft Research
  authors:
  - Thomas Hartvigsen
  - Saadia Gabriel
  - Hamid Palangi
  - Maarten Sap
  - Dipankar Ray
  - Ece Kamar
  url: https://github.com/microsoft/TOXIGEN
paper:
  title: 'ToxiGen: A Large-Scale Machine-Generated Dataset for Adversarial and Implicit Hate Speech Detection'
  arxiv: '2203.09509'
  url: https://arxiv.org/abs/2203.09509
  year: 2022
leaderboard_url: ''
repo_url: https://github.com/microsoft/TOXIGEN
released: '2022-03'
last_updated: ''
lineage:
  family: ''
  predecessor: ''
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ''
  note: No maintained public leaderboard was found, so a current ceiling could not be established from the sources reviewed; scores in provider system cards are self-reported and not necessarily computed the same way.
contamination:
  risk: medium
  note: The full 274k-statement dataset has been public on GitHub and Hugging Face since 2022 with no held-out split described in the sources reviewed, so text overlap with later training corpora is plausible. The official GitHub repository was archived (made read-only) on 2026-07-15, though the dataset remains available via Hugging Face.
harness:
  lm_eval: ''
  inspect_evals: ''
  helm: ''
  opencompass: ''
  bigbench: ''
  other: ''
tags:
- safety
- toxicity
- hate-speech
- classifier
sources:
- url: https://arxiv.org/abs/2203.09509
  title: 'ToxiGen: A Large-Scale Machine-Generated Dataset for Adversarial and Implicit Hate Speech Detection (arXiv abstract)'
  accessed: '2026-09-07'
- url: https://github.com/microsoft/TOXIGEN
  title: microsoft/TOXIGEN GitHub repository
  accessed: '2026-09-07'
freshness:
  researched: '2026-09-07'
  researched_by: sonnet-5 agent, batch 1, slice H
  reviewed: ''
  reviewed_by: ''
---

## What it measures

ToxiGen focuses on a specific failure mode: hate speech that does not use slurs, insults, or other obviously flaggable language, but is still hateful toward a targeted group once read in context. The authors generated the dataset by prompting a large pretrained language model with carefully designed demonstrations and an adversarial classifier-in-the-loop decoding method, producing pairs of toxic and superficially similar benign statements about 13 minority groups. The point is to stress-test toxicity detectors and language models on exactly the cases where surface-level keyword filtering fails.

As a benchmark, ToxiGen is used two ways: to score a purpose-built toxicity classifier's accuracy at separating its toxic and benign statements, and to see whether a general chat model produces or endorses toxic completions when prompted with ToxiGen-style text.

## How it is scored

There is no single official ToxiGen leaderboard metric; the paper's own reference use is fine-tuning HateBERT and RoBERTa classifiers on ToxiGen data and reporting their accuracy at detecting toxic versus benign statements, both on ToxiGen's own held-out examples and on other public hate-speech datasets. Human annotators separately confirmed that 94.5% of the machine-generated "toxic" statements were indeed judged hate speech, which the authors use as a quality check on the generation pipeline rather than a model score. When ToxiGen appears as a line item in a model or system card, it is typically measuring either a safety classifier's accuracy on ToxiGen examples or a chat model's rate of producing toxic completions when prompted with ToxiGen-style inputs - two different measurements that should not be compared to each other directly.

## Dataset and licence

The dataset contains 274,000 machine-generated statements, toxic and benign, spanning 13 minority groups, released under a CC BY 4.0 licence. A follow-up release added 27,450 human annotations over a subset of the generated text. The statements and (where released) their human labels are public rather than held out.

## Who publishes it

ToxiGen comes from Thomas Hartvigsen, Saadia Gabriel, Hamid Palangi, Maarten Sap, Dipankar Ray and Ece Kamar, published at ACL 2022 as "ToxiGen: A Large-Scale Machine-Generated Dataset for Adversarial and Implicit Hate Speech Detection," with Microsoft Research among the contributing institutions. The GitHub repository, `microsoft/TOXIGEN`, was archived and made read-only on 2026-07-15; the dataset itself remains accessible through Hugging Face.

## Lineage

ToxiGen was built specifically to probe implicit and adversarial toxicity, distinguishing it from earlier hate-speech datasets built from real social-media posts with explicit slurs. Microsoft Research later published a related "(De)ToxiGen" research blog post on using the dataset to build more robust detectors; no distinct successor benchmark id for ToxiGen exists elsewhere in this repository's corpus.

## Saturation and contamination

No maintained third-party leaderboard for ToxiGen was found, so its current ceiling is unknown rather than confirmed saturated or open. Contamination risk sits at medium: the full statement set has been public since 2022 without a described held-out split, and the source repository going read-only in 2026 removes any prospect of a refreshed or rotated test set going forward.

## How to run it

The reference generation and evaluation code lives in the (now archived) `microsoft/TOXIGEN` GitHub repository, alongside the released HateBERT and RoBERTa classifier checkpoints fine-tuned on ToxiGen data. No lm-evaluation-harness or other standard-harness task name for ToxiGen was confirmed in the sources reviewed for this page.

## Reading the numbers

A high ToxiGen score for a purpose-built classifier means it is good at telling implicitly toxic statements from superficially similar benign ones about the same groups, which is a narrower and harder skill than generic profanity filtering. A low toxic-completion rate for a chat model on ToxiGen prompts is a safety signal, not a completeness one - it says nothing about the model's usefulness or its behavior on toxicity types the dataset does not cover. Because the two use cases produce different kinds of numbers, always check which one a reported ToxiGen score refers to before comparing it across models.
