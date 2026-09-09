---
id: the_facts_leaderboard
name: "The FACTS Leaderboard"
aliases:
  - "FACTS Leaderboard Suite"
  - "FACTS Score"
page_kind: benchmark
category: composite
subcategory: "four-track factuality suite: multimodal, parametric, search and grounding v2"
status: active
summary: "Google FACTS suite averages multimodal, parametric, search and grounding-v2 tracks into one FACTS Score on public and private splits."
measures: >
  The FACTS Leaderboard is a four-track factuality suite, not a single prompt set.
  FACTS Multimodal asks image questions that need visual grounding plus world
  knowledge. FACTS Parametric asks closed-book factoids that users care about and
  that Wikipedia supports. FACTS Search requires a shared Brave Search tool on
  tail and multi-hop questions. FACTS Grounding v2 reuses the v1 long-document
  prompts with newer judges. The headline FACTS Score is the unweighted mean of
  the four track accuracies, each already averaged over that track's public and
  private items.
task_format: >
  Mixed: image-plus-text QA with a human rubric; short closed-book factoids;
  tool-using search with Brave Search API; long-form grounded generation from a
  supplied document. Kaggle runs official scoring.
metric:
  name: "FACTS Score (mean of four track accuracies)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    Paper Table 1 (public+private, 95% CI): Gemini 3 Pro 68.8 overall; Gemini 2.5
    Pro 62.1; GPT-5 61.8. Track metrics differ: Grounding v2 is eligible-and-grounded
    accuracy; Multimodal requires covering essential rubric facts with no
    contradictions; Parametric and Search use a grader with correct / incorrect /
    not-attempted / unknown and report accuracy plus F1 and hedging.
dataset:
  size: 7229
  size_note: >
    Sum of published split sizes: Multimodal 711 public + 811 private (1,522);
    Parametric 1,052 + 1,052 (2,104); Search 890 + 994 (1,884); Grounding 860 + 859
    (1,719). Search internals: Hard Tail 328, Wiki Two-Hop 932, Wiki Multi-Doc 268,
    KG Hops 356. Only Grounding's 860 public prompts are on Hugging Face as
    google/FACTS-grounding-public.
  url: "https://www.kaggle.com/benchmarks/google/facts"
  license: ""
  languages:
    - en
  modalities:
    - text
    - image
  splits: "each track has a public split and a private split; Kaggle scores both"
  public_test_set: false
publisher:
  org: "Google DeepMind, Google Research, Google Cloud, and Kaggle"
  authors:
    - "Aileen Cheng"
    - "Alon Jacovi"
    - "Amir Globerson"
    - "Ben Golan"
    - "Charles Kwong"
    - "Chris Alberti"
    - "Connie Tao"
    - "Eyal Ben-David"
    - "Gaurav Singh Tomar"
    - "Lukas Haas"
    - "Yonatan Bitton"
    - "Dipanjan Das"
    - "Sasha Goldshtein"
  url: "https://www.kaggle.com/benchmarks/google/facts"
paper:
  title: "The FACTS Leaderboard: A Comprehensive Benchmark for Large Language Model Factuality"
  arxiv: "2512.10791"
  url: "https://arxiv.org/abs/2512.10791"
  year: 2025
leaderboard_url: "https://www.kaggle.com/benchmarks/google/facts"
repo_url: ""
released: "2025-12"
last_updated: "2025-12"
lineage:
  family: ""
  predecessor: the_facts_grounding_leaderboard
  successors: []
  variants: []
saturation:
  status: open
  top_score: 68.8
  as_of: "2025-12"
  note: >
    Gemini 3 Pro 68.8 FACTS Score in the paper table. The authors highlight ~69% as
    remaining headroom. Multimodal accuracy is the lowest band (top about 47%).
    Grounding v2 and Search sit higher.
contamination:
  risk: medium
  note: >
    Parametric answers are Wikipedia-supported user-interest facts, adversarially
    filtered so five open-weight closed-book models all failed silver labels.
    Grounding documents are web text. Search items were filtered so search-off
    Gemini 2.5 Flash failed them. Each track keeps a private split. Public
    Grounding prompts are the main easy-to-train slice.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Kaggle-hosted official evaluation; Search track uses Brave Search API"
tags:
  - factuality
  - composite
  - multimodal
  - search
  - grounding
sources:
  - url: "https://arxiv.org/abs/2512.10791"
    title: "The FACTS Leaderboard paper (arXiv:2512.10791v1)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2512.10791"
    title: "The FACTS Leaderboard HTML full text"
    accessed: "2026-09-08"
  - url: "https://www.kaggle.com/benchmarks/google/facts"
    title: "FACTS Benchmark Suite Kaggle leaderboard"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/google/FACTS-grounding-public"
    title: "Public Grounding split (suite reuses these prompts as Grounding v2)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-082 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

The FACTS Leaderboard is Google's four-track factuality suite. One FACTS Score averages four different failure modes rather than one prompt distribution.

Multimodal: answer an image question with essential facts from a human rubric and no contradictions. Parametric: answer a short, stable, single-fact question from memory. Search: use Brave Search on questions built to need lookup (hard tail, wiki two-hop, multi-doc, knowledge-graph hops). Grounding v2: same long-document prompts as [the_facts_grounding_leaderboard](the_facts_grounding_leaderboard.md), new judges.

## How it is scored

Each track has its own judge protocol. Grounding v2 still filters ineligible answers, but judges are Gemini 2.5 Flash and GPT-5 with a revised prompt (Macro-F1 on a 320-example holdout). Parametric grades three Gemini-2.5-Pro samples per item as correct, incorrect, not-attempted or unknown. Search uses Gemini 2.0 Flash against a gold answer, with the same attempt labels, and logs search-call counts.

The FACTS Score is the mean of the four track accuracies. Kaggle holds private items and runs submissions. Paper Table 1 is API models on public-plus-private.

## Dataset and licence

About 7,229 items if you add the published split sizes. Only the Grounding public 860 rows are clearly licensed CC-BY-4.0 on Hugging Face. A suite-wide dataset licence was not on the arXiv page or the Kaggle suite URL opened for this page. Do not copy the Grounding CC-BY-4.0 onto Multimodal, Parametric or Search.

Search gold answers were filtered by three raters for correctness, uniqueness and five-year stability, then by a search-off Gemini 2.5 Flash fail filter.

## Who publishes it

Google Research, Google DeepMind, Google Cloud and Kaggle. arXiv:2512.10791v1 is dated 11 December 2025, CC BY 4.0 for the paper. Alon Jacovi is the submitting author. The live board is kaggle.com/benchmarks/google/facts, distinct from the older kaggle.com/facts-leaderboard grounding URL.

## Lineage

Predecessor: [the_facts_grounding_leaderboard](the_facts_grounding_leaderboard.md) (v1, January 2025 paper). This suite adds three tracks and refreshes Grounding judges. Parametric is closer in spirit to [simpleqa](simpleqa.md) (short factoids, attempt-aware grading) but uses Wikipedia-backed, adversarially sampled user-interest questions.

Census also lists a `facts_leaderboard` slug. This page is the assigned id `the_facts_leaderboard`. They name the same Google suite; do not author a second copy under the shorter slug without an alias decision from the coordinator.

## Saturation and contamination

Gemini 3 Pro at 68.8 leaves headroom. Track gaps are the point: a model can lead Grounding and lag Parametric (Claude 4.5 Opus is 62.1 Grounding vs 30.6 Parametric in Table 1). Multimodal accuracy stays in the 40s for the leaders.

Private splits and adversarial Parametric/Search filters reduce some leakage. Public Grounding prompts remain the easiest contamination path.

## How to run it

Official numbers are Kaggle-judged. There is no confirmed lm-eval or inspect_evals id for the suite. Search comparisons are only fair with the same Brave Search tool description.

Do not average a v1 Grounding 83.6 from 2025-01 with a 2025-12 FACTS Score. Grounding v2 is a different judge stack on the same prompts.

## Reading the numbers

68.8 FACTS Score means mid-sixties to low-seventies mean accuracy across four unlike tracks, not that two-thirds of all facts in the world are right. Always read the four columns.

Search rewards tool use; Parametric rewards memory and punishes hedging on the accuracy column (attempted-accuracy and F1 are the calibration view). Grounding v2 still does not test closed-book truth. If a model card says "FACTS" without a track name, ask which of the two Kaggle URLs and which year.
