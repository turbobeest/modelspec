---
id: benchmarking_the_domain_gap
name: "Benchmarking the Domain Gap"
page_kind: benchmark
category: domain
subcategory: video capsule endoscopy
summary: "Benchmarking the Domain Gap measures how model rankings change across video capsule endoscopy datasets and shared-label targets."
measures: "The study evaluates image-classification backbones trained on Kvasir-Capsule and tested across Kvasir-Capsule, Capsule Vision 2024, and a shared-label subset of Galar. It measures cross-target ranking stability under domain shift."
task_format: "Supervised image classification on endoscopy frames or clips with shared-label evaluation."
metric:
  name: classification performance and ranking stability
  direction: higher_is_better
  unit: score
  baseline_note: "The paper emphasizes target-dependent ranking agreement; one universal metric maximum is not established here."
dataset:
  modalities: [image, video]
  languages: []
  public_test_set: null
publisher:
  org: "Dan Hanson and Debesh Jha"
  authors: [Dan Hanson, Debesh Jha]
  url: https://arxiv.org/abs/2607.22736
paper:
  title: "Benchmarking the Domain Gap: Model Selection Instability Under Domain Shift in Video Capsule Endoscopy"
  arxiv: "2607.22736"
  url: https://arxiv.org/abs/2607.22736
  year: 2026
released: "2026-07"
saturation:
  status: open
  note: "The paper finds target-dependent instability rather than a saturated ranking."
contamination:
  risk: low
  note: "This is a clinical image-domain evaluation; the paper does not report model pretraining contamination, so the risk remains provisional."
harness:
  other: "The standardized fine-tuning and cross-target evaluation protocol described in the paper."
tags: [medical-imaging, domain-shift, ranking-stability]
sources:
  - url: https://arxiv.org/abs/2607.22736
    title: "Benchmarking the Domain Gap paper and abstract"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "GPT-5.6 Luna, luna-stream-a-003 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---
## What it measures

Benchmarking the Domain Gap evaluates whether model selection on one video capsule endoscopy dataset transfers to other acquisition and labeling settings. The authors fine-tune general-domain pretrained backbones on official Kvasir-Capsule folds, then evaluate the same checkpoints on Capsule Vision 2024 and a shared-label subset of Galar.

The task is supervised medical image classification. The central measurement is not only accuracy on one dataset, but whether model rankings remain stable across non-source targets.

## How it is scored

Each checkpoint is evaluated under the study’s standardized classification protocol. The paper compares in-domain performance with target performance and examines agreement among rankings. Exact classification metric names, maxima, and baseline values are not established in the abstract consulted here. Report the target dataset, training configuration, and label intersection with every number.

## Dataset and licence

The study names Kvasir-Capsule, Capsule Vision 2024, and Galar, using a shared-label decision space for cross-target tests. It does not state a single combined item count or a common licence. Clinical dataset access and label policies may differ, so this record leaves size, licence, and answer visibility unknown.

## Who publishes it

Dan Hanson and Debesh Jha authored the paper, submitted to arXiv in July 2026. The arXiv abstract is the primary source consulted. No public leaderboard is identified; the contribution is a cross-target experimental protocol and analysis.

## Lineage

This is a domain-shift benchmark assembled from three named capsule-endoscopy datasets. The component datasets are its direct antecedents. The paper does not identify a successor benchmark or a separate standardized family page.

## Saturation and contamination

The study reports that in-domain ranking aligns more closely with Galar than with Capsule Vision 2024, while the two non-source targets agree only weakly. The strongest in-domain backbone leads on one target but falls to mid-pack on another. These findings show an open generalization problem. The paper does not establish training-data contamination; the provisional risk is low because the evaluation is a specialized clinical image setting.

## How to run it

Use official Kvasir-Capsule folds, the documented shared-label decision space, and the same checkpoint across target datasets. Repeat the paper’s second CV2024-trained configuration to test the reported instability. Record preprocessing, labels, splits, backbone, fine-tuning budget, and target-specific metrics.

## Reading the numbers

High source-dataset accuracy does not guarantee a high target score. Ranking stability across targets is the practical signal for model selection under domain shift. Results do not establish clinical safety or deployment utility without external validation and clinical review. Examine per-target confusion and label coverage alongside aggregate rankings.
