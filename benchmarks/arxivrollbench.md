---
id: arxivrollbench
name: "ArxivRollBench"
aliases:
  - "ArxivRoll"
  - "RoBench"
page_kind: benchmark
category: reasoning
subcategory: "rolling, contamination-auditing sentence-ordering, cloze and continuation tasks built from recent arXiv text"
status: active
summary: "A rolling benchmark turning freshly-published arXiv text into sentence-ordering, cloze and next-fragment multiple-choice tasks every six months, built to measure how much contamination inflates benchmark scores."
measures: >
  ArxivRollBench is the evaluation-task component of ArxivRoll, a framework whose actual goal is not
  to test topical arXiv knowledge but to measure how much a model's public-benchmark score is inflated
  by contamination or uneven training exposure. It does this with SCP tasks -- Sequencing (reorder
  three shuffled sentences, choosing among four candidate orderings), Cloze (fill three masked
  sentences in a paragraph from labelled candidates, again choosing among four candidate
  combinations), and Prediction (choose the correct next fragment of a passage from four options) --
  built automatically from arXiv article text collected after each task set is constructed, across
  eight domains (cs, econ, eess, math, physics, q-bio, q-fin, stat). Because the source text postdates
  every model's training cutoff at the time a round is built, and each round is evaluated once and
  then either kept private or later published as "expired," the authors use performance on
  ArxivRollBench relative to performance on long-public benchmarks to compute a "Rugged Score," a
  measure of public-benchmark overestimation -- inspired explicitly by one-time-pad encryption, where
  reusing the same key (here, the same test items) twice defeats the scheme's guarantees.
task_format: >
  Four-way multiple choice per item. Sequencing and Cloze items ask the model to answer "Selection 1"
  through "Selection 4"; Prediction items ask for a letter A-D. All are zero-shot, generation-based
  (the model's free text is parsed by regex for a selection number or letter), scored per domain, per
  release and per SCP type.
metric:
  name: "accuracy (per SCP-type, per domain, per release); the paper's own headline metric is Rugged Score (RS), a derived overestimation measure, not this page's per-item accuracy"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: 25.0
  human_baseline: null
  baseline_note: >
    25% is the four-option random-guess rate for the per-item accuracy this page's `metric` field
    describes. The paper's actual central quantity, Rugged Score, is a comparison between a model's
    performance on public benchmarks and its performance on fresh, uncontaminated ArxivRollBench
    rounds, and is not a simple accuracy percentage; this page did not confirm a numeric RS baseline
    or ceiling from a source read directly.
dataset:
  size: null
  size_note: >
    ArxivRollBench is a round-based generator, not one fixed item count. Three rounds exist in the
    OpenCompass configuration read for this page -- 2024b, 2025a and 2026a -- each covering 8 domains
    x 3 SCP task types, giving "24 private tasks per full release" per the authors' own repository
    documentation. Verified directly by downloading two sampled Hugging Face configs: the 2024b/cs/
    Sequencing "compact" split held 42 examples, and the 2025a/math/Prediction "compact" split held
    51; the repository's own naming ("-50" suffix) targets roughly 50 per domain/type/release but the
    achieved count depends on how many eligible papers a given domain produced in that window. A
    larger, unverified "full" split is also generated from the complete crawled text alongside each
    compact split.
  url: "https://github.com/liangzid/ArxivRoll"
  license: "Not established. No LICENSE file was detected by GitHub's own licence API for the liangzid/ArxivRoll source repository, and the sampled Hugging Face dataset configs carry no licence tag. The underlying text is drawn from recent arXiv papers, each subject to arXiv's own non-exclusive distribution terms or the author's chosen licence; the repository's own README explicitly instructs contributors not to redistribute paper source files beyond what each paper's licence permits."
  languages:
    - en
  modalities:
    - text
  splits: "no fixed train/test split; each ~6-month round (2024b, 2025a, 2026a so far) is generated fresh per domain and SCP type, in both a compact (~40-50 example) and a larger full configuration"
  public_test_set: null
publisher:
  org: "The Hong Kong Polytechnic University"
  authors:
    - "Zi Liang"
    - "Liantong Yu"
    - "Shiyu Zhang"
    - "Qingqing Ye"
    - "Haibo Hu"
  url: "https://arxivroll.moreoverai.com"
paper:
  title: "How Much Do Large Language Model Cheat on Evaluation? Benchmarking Overestimation under the One-Time-Pad-Based Framework"
  arxiv: "2507.19219"
  url: "https://arxiv.org/abs/2507.19219"
  year: 2025
leaderboard_url: "https://arxivroll.moreoverai.com"
repo_url: "https://github.com/liangzid/ArxivRoll"
released: "2025-07"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: >
    The project's own live leaderboard was read for this page (via a JavaScript-rendering fetch, since
    the site loads its results table client-side) and showed no populated rows at the research date --
    only column headers and an empty diagnostics panel -- so no current top score could be recorded.
    Because the benchmark's entire purpose is comparative (public-benchmark score versus
    ArxivRollBench score, expressed as Rugged Score) rather than a single ceiling to climb, "saturated"
    or "open" status is a poor fit even when scores are available; this page records "unknown" rather
    than force a reading onto a differently-shaped metric.
contamination:
  risk: medium
  note: >
    Risk here depends on which round is being scored, which is itself the benchmark's whole point.
    An active, unexpired round is built from arXiv text published after the round's own construction
    date and is kept private specifically to resist contamination -- close to zero risk by design
    while active. Once a round "expires" and is published, that protection ends: the 2024b round's
    compact Hugging Face configs were created around October-December 2024 and have been openly
    downloadable since, close to two years by this page's research date, so a model trained recently
    could have seen 2024b's exact items even though 2025a and 2026a remain comparatively fresh.
    Because OpenCompass's default configuration runs all three released rounds together, a single
    reported "arxivrollbench" score can mix genuinely fresh and now-public items.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "arxivrollbench (arxivrollbench_datasets, compact; arxivrollbench_full_datasets, full; per-release, per-domain, per-type task abbreviations, e.g. arxivrollbench-2025a-cs-s)"
  bigbench: ""
  other: >
    The authors also maintain their own lm-evaluation-harness plugin, liangzid/harness-4-arxivrollbench,
    documented as exposing tasks such as arxivrollbench2026a-50; this page did not confirm it is merged
    into the mainline EleutherAI lm-evaluation-harness repository.
tags:
  - reasoning
  - contamination
  - dynamic-benchmark
  - discourse-coherence
  - arxiv
  - rolling-benchmark
  - multiple-choice
sources:
  - url: "https://arxiv.org/abs/2507.19219"
    title: "How Much Do Large Language Model Cheat on Evaluation? Benchmarking Overestimation under the One-Time-Pad-Based Framework"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2507.19219"
    title: "ArxivRoll paper, full text (ar5iv), for author affiliation"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/arxivrollbench/arxivrollbench_gen.py"
    title: "OpenCompass arxivrollbench_gen.py dataset config (releases, domains, task types, prompts)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/arxivrollbench.py"
    title: "OpenCompass arxivrollbench.py answer postprocessors (confirms Selection N / A-D scoring)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/liangzid/ArxivRoll/master/README.md"
    title: "liangzid/ArxivRoll reference repository README (SCP definitions, round table, licence/redistribution notes)"
    accessed: "2026-09-08"
  - url: "https://api.github.com/repos/liangzid/ArxivRoll/license"
    title: "GitHub licence detection for liangzid/ArxivRoll (no licence file detected)"
    accessed: "2026-09-08"
  - url: "https://arxivroll.moreoverai.com"
    title: "ArxivRollBench live leaderboard site (publisher/maintainer credit, AAAI 2026 citation block, lm-evaluation-harness usage example)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/liangzid/robench2024b_all_setcsSCP-s-50"
    title: "liangzid/robench2024b_all_setcsSCP-s-50 dataset metadata (2024b/cs/Sequencing compact split, 42 rows)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/api/datasets/liangzid/robench2025a_test_all_category_setmathSCP-p-50"
    title: "liangzid/robench2025a_test_all_category_setmathSCP-p-50 dataset metadata (2025a/math/Prediction compact split, 51 rows)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 4, slice E"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

ArxivRollBench is the evaluation-task component of ArxivRoll, a framework whose actual goal is not to test topical arXiv knowledge but to measure how much a model's public-benchmark score is inflated by contamination or uneven training exposure. Its tasks follow the SCP scheme: Sequencing asks a model to reorder three shuffled sentences, choosing the correct order from four candidate arrangements; Cloze presents a paragraph with three sentences masked out and asks the model to fill them from labelled candidates, again choosing among four candidate combinations; Prediction shows a passage and asks the model to pick the correct next fragment from four options. All three are built automatically from arXiv article text across eight domains -- computer science, economics, electrical engineering and systems science, mathematics, physics, quantitative biology, quantitative finance, and statistics.

The mechanism that makes this a contamination *audit* rather than just another reading-comprehension set is timing: each round's source text is collected after that round is constructed, so it postdates every model's training cutoff at construction time. The authors compare a model's score here against its score on long-public benchmarks to compute a "Rugged Score" (RS), their measure of how much public-benchmark performance is overestimated. The name is a deliberate reference to one-time-pad encryption, where reusing the same key twice breaks the security guarantee -- here, reusing the same test items across many models and much time is exactly what the framework is built to avoid, by retiring each round after one evaluation pass.

## How it is scored

Every item is four-way multiple choice, generation-based rather than log-likelihood-based: the model is prompted to output only its selection, and a regex postprocessor extracts either "Selection 1" through "Selection 4" (for Sequencing and Cloze items) or a bare letter A-D (for Prediction items), which is then compared against the gold label. Random guessing therefore scores 25% on any individual item. This page's `metric` field describes that per-item accuracy, which is what OpenCompass reports per domain, release and SCP type -- but it is not the paper's own headline number. The paper's real central quantity, Rugged Score, derives from comparing a model's accuracy here against its accuracy on established public benchmarks, and this page did not confirm a specific numeric baseline or ceiling for that derived score from a source read directly.

## Dataset and licence

ArxivRollBench is a round-based generator rather than one fixed-size file. Three rounds are wired into the OpenCompass configuration read for this page -- 2024b, 2025a and 2026a -- each spanning the 8 domains above by the 3 SCP task types, which the authors' own repository documentation states gives "24 private tasks per full release." Sampling two of the underlying Hugging Face datasets directly confirmed the practical scale: the 2024b/cs/Sequencing "compact" split held 42 examples, and the 2025a/math/Prediction "compact" split held 51 -- both close to, but not exactly, the 50 the "-50" filename suffix targets, since the achieved count depends on how many eligible papers a given domain produced during that round's collection window. A larger "full" configuration is also generated per round from the complete crawled text, though this page did not verify its size. No licence was found for the assembled benchmark itself: GitHub's own licence detection found no LICENSE file in the source repository, and the sampled Hugging Face configs carry no licence tag; the underlying text remains subject to each source paper's own arXiv distribution terms.

## Who publishes it

ArxivRollBench comes from Zi Liang, Liantong Yu, Shiyu Zhang, Qingqing Ye and Haibo Hu at The Hong Kong Polytechnic University, posted to arXiv in July 2025 and, per the paper's own public citation record on the project's leaderboard site, accepted to AAAI 2026 (volume 40, DOI 10.1609/aaai.v40i44.41098). The authors maintain the source repository, a public leaderboard site described as supported by "Astaple Group in PolyU" and maintained by "MoreoverAI," and a companion lm-evaluation-harness plugin for running the benchmark.

## Lineage

ArxivRollBench has no predecessor or successor tracked elsewhere in this repository. It belongs to a broader, informal family of contamination-resistant "rolling" or "live" benchmarks that refresh their test items on a schedule specifically to stay ahead of training-data inclusion, though this repository does not yet have pages for other examples of that pattern to link here. Its SCP task design (sentence reordering, cloze, next-fragment prediction) is a distinct construction from anything else in this repository; it is unrelated to the "RollBench"-style names sometimes used informally elsewhere, and this page confirms its subject specifically from the authors' own repository and paper rather than from the census hint's OpenCompass URL alone.

## Saturation and contamination

Saturation status is unknown. This page fetched the project's own live leaderboard, including its JavaScript-rendered results table, and found it populated with column headers but no scored rows at the research date, so no current top score could be recorded. Because the benchmark's actual purpose is comparative -- a model's ArxivRollBench score set against its public-benchmark score, expressed as Rugged Score -- rather than one ceiling to climb, "saturated" or "open" would misrepresent it even where scores are available. Contamination risk is medium and round-dependent, which is the benchmark's central design feature rather than an incidental property: an active, unexpired round is built from text published after its own construction and is kept private, close to zero contamination risk while active; once a round "expires" and its data is published, that protection ends, and the 2024b round has been openly downloadable for close to two years by this page's research date. Since OpenCompass's default configuration runs all three released rounds together, a single reported "arxivrollbench" score can mix a genuinely fresh round with an already-public one.

## How to run it

OpenCompass exposes both a compact configuration (`arxivrollbench_datasets`, the recommended default per the authors' own site) and a full configuration (`arxivrollbench_full_datasets`), generating one task per release/domain/SCP-type combination (for example `arxivrollbench-2025a-cs-s`), each loading its own Hugging Face parquet file and scoring with `AccEvaluator` after the regex postprocessing described above. The authors separately document a dedicated lm-evaluation-harness plugin, `harness-4-arxivrollbench`, exposing per-round task names such as `arxivrollbench2026a-50`; this page did not confirm that plugin is merged into the mainline EleutherAI repository, so treat it as the authors' own fork rather than an upstream-supported harness.

## Reading the numbers

A score on ArxivRollBench is most meaningful next to a score on an older public benchmark, not on its own -- the entire design intent is to expose a gap between the two as evidence of contamination or overestimation, which is the paper's Rugged Score. Confirm which round (2024b, 2025a or 2026a) and which configuration (compact or full) produced a given number before comparing it across papers or models, since an already-expired, now-public round carries materially different contamination risk than the currently active one. A model that scores much lower here than on a same-difficulty public benchmark is the signal this benchmark is built to surface; a model that scores comparably on both is the stronger, harder-to-fake result.
