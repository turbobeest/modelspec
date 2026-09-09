---
id: writingbench
name: WritingBench
aliases: []
page_kind: benchmark
category: generation
subcategory: LLM-judged generative writing, professional and creative domains
status: active
summary: 1,000 real-world writing prompts across 6 domains and 100 subdomains, each graded on five auto-generated, instance-specific criteria by an LLM or critic-model judge.
measures: >
  WritingBench asks a model to complete an open-ended, real-world writing request - drafting a
  paper outline, a marketing brief, a legal summary, a lesson plan and similar tasks - drawn from
  six domains (Academic & Engineering, Finance & Business, Politics & Law, Literature & Art,
  Education, Advertising & Marketing) and 100 finer-grained subdomains. Prompts are often long and
  specific, averaging over 1,500 tokens and sometimes embedding source material the response must
  work from, such as a financial statement or a sample abstract, rather than a short one-line
  instruction. Rather than judging every response against one fixed rubric, the benchmark
  generates five criteria specific to each individual query - covering things like required
  structure, tone or factual grounding for that particular request - so that a lesson plan and a
  legal brief are not scored on the same axes.
task_format: "Open-ended long-form writing prompt in, spanning six primary domains and 100 subdomains, with prompt lengths from tens to thousands of words and some prompts supplying source material to write from; free-text written response out, graded rather than matched against a reference answer."
metric:
  name: "LLM-judged or critic-model score, 1-10 per criterion, averaged over five query-specific criteria"
  direction: higher_is_better
  unit: "points (1-10 per criterion; the public leaderboard multiplies the mean by 10 to display it out of 100)"
  max_score: 10
  random_baseline: null
  human_baseline: null
  baseline_note: "The authors' fine-tuned Qwen-7B critic model reaches 83% agreement with human judgments using this query-specific, five-criteria protocol, against 65-69% for static global criteria and 40-59% for static domain-specific criteria (paper Table 4). No numeric human score on the 1-10 scale itself was found in the sources read."
dataset:
  size: 1000
  size_note: "1,000 writing queries in the current release - 555 English and 445 Chinese, counted directly from the repository's benchmark_query/benchmark_all.jsonl - each paired with five auto-generated criteria. The original 2025-03-10 release shipped 1,239 queries; an update on 2025-04-29 revised the set down to the current 1,000 and switched the requirement-dimension subsets, per the repository's own changelog."
  url: https://github.com/X-PLUG/WritingBench/blob/main/benchmark_query/benchmark_all.jsonl
  license: Apache-2.0
  languages:
    - en
    - zh
  modalities:
    - text
  splits: "one evaluation set (benchmark_all.jsonl, 1,000 queries), plus separate style/format/length 'requirement' subsets used to probe specific instruction-following axes; there is no train/test split, since nothing is trained against it."
  public_test_set: true
publisher:
  org: Alibaba Group
  authors:
    - Yuning Wu
    - Jiahao Mei
    - Ming Yan
    - Chenliang Li
    - Shaopeng Lai
    - Yuran Ren
    - Zijia Wang
    - Ji Zhang
    - Mengyue Wu
    - Qin Jin
    - Fei Huang
  url: https://github.com/X-PLUG/WritingBench
paper:
  title: "WritingBench: A Comprehensive Benchmark for Generative Writing"
  arxiv: "2503.05244"
  url: https://arxiv.org/abs/2503.05244
  year: 2025
leaderboard_url: https://huggingface.co/spaces/WritingBench/WritingBench
repo_url: https://github.com/X-PLUG/WritingBench
released: "2025-03"
last_updated: "2025-11"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: unknown
  top_score: null
  as_of: ""
  note: "The public leaderboard (a Hugging Face Space) renders client-side and its current standings could not be read from this page fetch, so no current top score is established here. Separately, the leaderboard's own judge model has changed at least four times since launch (an unnamed initial judge, then Claude-3-7-Sonnet from 2025-04-29, Claude-Sonnet-4 from 2025-09-05, and Claude-Sonnet-4-5 from 2025-11-27, per the repository changelog), so scores from different leaderboard snapshots are not on the same scale and should not be compared directly regardless."
contamination:
  risk: medium
  note: "The fixed 1,000-query set has been publicly downloadable since April 2025 (the original 1,239-query set since March 2025), so a released model's pretraining data could plausibly include it. Risk is not marked high because scoring depends on a live judge call rather than a fixed answer key, which limits the benefit of memorising the prompts alone, and no source read for this page reported demonstrated contamination."
harness:
  lm_eval: ""
  inspect_evals: writingbench
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "Reference generation, scoring and aggregation scripts (generate_response.py, evaluate_benchmark.py, calculate_scores.py) ship in the X-PLUG/WritingBench GitHub repository."
tags:
  - writing
  - generation
  - llm-judge
  - creative-writing
  - professional-writing
sources:
  - url: https://arxiv.org/abs/2503.05244
    title: "WritingBench: A Comprehensive Benchmark for Generative Writing (arXiv abstract)"
    accessed: "2026-09-08"
  - url: https://ar5iv.labs.arxiv.org/html/2503.05244
    title: WritingBench paper, full text (ar5iv)
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/X-PLUG/WritingBench/main/README.md
    title: X-PLUG/WritingBench README (raw, version changelog and construction pipeline)
    accessed: "2026-09-08"
  - url: https://raw.githubusercontent.com/X-PLUG/WritingBench/main/benchmark_query/benchmark_all.jsonl
    title: X-PLUG/WritingBench benchmark_all.jsonl (raw query data, sampled for language counts)
    accessed: "2026-09-08"
  - url: https://github.com/X-PLUG/WritingBench
    title: X-PLUG/WritingBench GitHub repository
    accessed: "2026-09-08"
  - url: https://neurips.cc/virtual/2025/poster/121666
    title: "WritingBench at NeurIPS 2025 (Datasets and Benchmarks track poster page)"
    accessed: "2026-09-08"
  - url: https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/writingbench
    title: inspect_evals writingbench task implementation
    accessed: "2026-09-08"
  - url: https://huggingface.co/spaces/WritingBench/WritingBench
    title: WritingBench public leaderboard (Hugging Face Space)
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice C"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

WritingBench tests open-ended generative writing rather than a single narrow skill: each of its 1,000 prompts asks for a complete piece of writing - a paper outline, a financial brief, a lesson plan, an advertisement - drawn from six domains (Academic & Engineering, Finance & Business, Politics & Law, Literature & Art, Education, Advertising & Marketing) and 100 finer subdomains. Prompts run long, averaging over 1,500 tokens, and many embed real source material the response has to work from, such as a sample abstract or a financial statement, rather than a short one-line instruction. The benchmark is bilingual, with 555 English and 445 Chinese queries in the current release.

Instead of scoring every response against one fixed rubric, WritingBench generates five criteria specific to each individual query before any response is judged, so a legal brief and a children's story are evaluated on different, query-appropriate axes rather than a generic "quality" scale.

## How it is scored

For each query, an LLM first generates five instance-specific criteria, each with a name, a description and a scoring rubric. A judge - either a general-purpose LLM or the authors' own fine-tuned Qwen-7B critic model - then scores a response 1 to 10 against each of the five criteria independently, with a written justification, and the five scores are combined into a per-response result; the public leaderboard multiplies this average by 10 to display it on a 0-100 scale. The authors validate the approach by showing their critic model, using this query-specific protocol, agrees with human judgments 83% of the time, compared with 65-69% for a static set of criteria shared across all queries and 40-59% for static criteria that vary only by domain (paper Table 4) - the paper's central claim is that query-specific criteria track human judgment better than either static alternative.

## Dataset and licence

The current release ships 1,000 writing queries under an Apache-2.0 licence, built through a four-stage pipeline: LLMs first draft candidate queries from a two-tiered domain pool and diversify them with style, format, length and personalization variations, after which 30 trained annotators collect supporting real-world materials and five domain experts screen and refine the results. The original 2025-03-10 release shipped a larger set of 1,239 queries; an update on 2025-04-29 revised it down to the current 1,000 and reworked the style/format/length "requirement" subsets, per the repository's own changelog - a report citing "WritingBench" without a date should be read as possibly referring to either version.

## Who publishes it

WritingBench comes from Yuning Wu, Jiahao Mei, Ming Yan, Chenliang Li, Shaopeng Lai, Yuran Ren, Zijia Wang, Ji Zhang, Mengyue Wu, Qin Jin and Fei Huang, with Alibaba Group among the contributing institutions alongside Renmin University of China and Shanghai Jiao Tong University. It was posted to arXiv in March 2025 and accepted as a poster at NeurIPS 2025's Datasets and Benchmarks track. Alibaba's X-PLUG team maintains the GitHub repository, the fine-tuned critic model and writing model on Hugging Face, and a public leaderboard mirrored on both Hugging Face Spaces and ModelScope.

## Lineage

WritingBench does not have a named predecessor or successor benchmark in this repository. Its distinguishing idea - generating evaluation criteria per query instead of using one fixed rubric - sets it apart from earlier open-ended generation benchmarks that score every response against the same static instructions; the paper positions this query-dependent approach as the main methodological contribution over that style of prior work.

## Saturation and contamination

The public leaderboard is a client-rendered Hugging Face Space whose current standings could not be extracted from a page fetch, so no current top score is established here. More fundamentally, the leaderboard's judge model has changed at least four times since launch - an initial judge, then Claude-3-7-Sonnet, Claude-Sonnet-4, and Claude-Sonnet-4-5 as of 2025-11-27, per the repository changelog - so scores from different leaderboard snapshots sit on different scales regardless of any single top score. Contamination risk is medium: the query set has been public since 2025, but because scoring depends on a live judge call against dynamically generated criteria rather than a fixed answer key, memorising the prompts alone offers a model less direct benefit than it would on an exact-match benchmark.

## How to run it

The reference pipeline lives in the `X-PLUG/WritingBench` GitHub repository (`generate_response.py`, `evaluate_benchmark.py`, `calculate_scores.py`), and inspect_evals ships a `writingbench` task that loads the same `benchmark_all.jsonl` query file. Reported numbers depend heavily on which judge was used - the authors' fine-tuned critic model, a proprietary LLM judge such as Claude, or another model entirely - and inspect_evals defaults to a different, cheaper judge (`anthropic/claude-3-5-haiku-latest`) than the leaderboard's own Claude-Sonnet-4-5. Since the judge is itself a Claude-family model in both the official leaderboard and the inspect_evals default, scores may carry some family bias toward writing styles a Claude model favours; treat any single WritingBench number as tied to its specific judge and criteria-generation model, not as judge-independent.

## Reading the numbers

A high WritingBench score is evidence a model can produce long, structured, domain-appropriate writing that a judge model finds well-organised and on-brief across a wide range of real-world requests - a broader and more subjective skill than exact-match benchmarks capture. It is not evidence of factual accuracy beyond what the query-specific criteria happen to check, and because the judge is normally a proprietary LLM rather than a person, a score partly reflects that judge's own stylistic preferences and any bias toward outputs that resemble its own writing. Always check which dataset version (1,239-query original or 1,000-query revision), which judge model, and which scale (raw 1-10 or the leaderboard's x10 display) a reported number uses before comparing it across sources.
