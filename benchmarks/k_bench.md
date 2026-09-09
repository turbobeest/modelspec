---
id: k_bench
name: "K-Bench"
aliases:
  - "K-Bench 01"
  - "K-Bench01"
page_kind: benchmark
category: agentic
subcategory: "private scientific-agent evaluation on real first-turn K-Dense Web requests"
status: active
summary: "K-Bench 01 scores nine frontier models on 178 private first-turn scientific requests from K-Dense Web using three LLM judges and an eight-dimension 0-10 rubric."
measures: >
  K-Bench 01 measures what a frontier model does with a real scientific request when it
  has only a stock agent harness, web tools, and the files the user attached. Items are
  first-turn messages sampled from live K-Dense Web traffic, kept verbatim, with no
  reference answers. Judges score the transcript and the files left on disk, not prose
  alone. The skill is executed scientific work: methods, claims, artifacts, and honesty.
  It is not exam QA, not protocol editing, and not GPU-kernel coding.
task_format: >
  One-shot agent run: the first user message plus attachments, inside an isolated Modal
  sandbox running stock pi 0.84.0 with shell, file tools, web search, fetch, and source
  check. No K-Dense production skills, no sub-agents, no retries, no follow-up user turns.
  Three blinded LLM judges then score each run against rubric v1.0.
metric:
  name: "panel mean of holistic overall (0-10); 8-anchor is scientist-acceptable with minor edits"
  direction: higher_is_better
  unit: "points"
  max_score: 10.0
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No human expert scored any run, so the 8-anchor is a written standard, not a measured
    human baseline. A run's overall is the mean of three judges' holistic scores. Model
    means average the 178 tasks. The paper also reports majority/unanimous fully_successful
    rates and 534 paired per-task, per-judge comparisons. gpt-5.6-sol's pooled mean is 8.04
    with 95% bootstrap interval [7.80, 8.23] in the v2 PDF; the 2026-08-25 K-Dense blog
    prints [7.81, 8.24].
dataset:
  size: 178
  size_note: >
    178 complete-case first-turn sessions (93 + 85 from two August 2026 draws), after
    dropping 22 sessions that at least one model refused. Nine models times 178 tasks =
    1,602 runs, 4,806 assessments, 39,934 scored judgments excluding N/A cells. Domains:
    life sciences 59, clinical and health 59, physical sciences/engineering/CS 43,
    chemistry/drug/materials 17. 125 of 178 sessions (70%) have at least one attachment.
    The prompts, attachments, transcripts, and output trees are not released.
  url: ""
  license: ""
  languages: []
  modalities:
    - text
  splits: "single private evaluation draw; no public train/test files"
  public_test_set: false
publisher:
  org: "K-Dense, Inc."
  authors:
    - "Aubrey M. Brueckner"
    - "Darshil Patel"
    - "Yuhuan He"
    - "Timothy Kassis"
  url: "https://www.k-dense.ai/"
paper:
  title: "K-Bench: measuring model performance on real scientific agent requests"
  arxiv: "2608.21601"
  url: "https://arxiv.org/abs/2608.21601"
  year: 2026
leaderboard_url: ""
repo_url: ""
released: "2026-08"
last_updated: "2026-09"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 8.04
  as_of: "2026-08"
  note: >
    gpt-5.6-sol has the highest pooled mean (8.04/10) but its interval spans the 8-anchor,
    and two of three judges rank claude-opus-5 first. The paper treats the top of the table
    as unresolved. 47.6% of scored judgments fall below 8. 22 of 178 tasks (12.4%) were
    not majority-solved by any model. 47.9% of runs leave no output file. This is the
    August 2026 campaign only.
contamination:
  risk: low
  note: >
    The task set is private user content and is not released. The publisher's blog states
    it is an evaluation set, never to be trained on. The paper says score tables and
    analysis code will be released, not the items. Residual risk is that some user
    attachments could overlap public papers or datasets, which cannot be audited from
    outside.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    Reference campaign: stock pi 0.84.0 (Earendil Works) in Modal sandboxes, models via
    OpenRouter, campaign 6-12 August 2026. Judges: gpt-5.6-sol, qwen3.8-max, grok-4.5,
    each as a pi agent with read/bash/write. No lm-eval, inspect_evals, HELM, OpenCompass,
    or BIG-bench task exists, and outside groups cannot rerun the items.
tags:
  - agentic
  - science
  - llm-as-judge
  - private-eval
  - tool-use
  - k-dense
sources:
  - url: "https://arxiv.org/abs/2608.21601"
    title: "K-Bench: measuring model performance on real scientific agent requests (Brueckner et al., arXiv:2608.21601v2)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/html/2608.21601"
    title: "K-Bench HTML full text (methods, results, limitations, availability)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/pdf/2608.21601.pdf"
    title: "K-Bench v2 PDF"
    accessed: "2026-09-08"
  - url: "https://www.k-dense.ai/blog/introducing-k-bench-01-internal-benchmark"
    title: "K-Dense blog, 2026-08-25: Introducing K-Bench 01"
    accessed: "2026-09-08"
  - url: "https://creativecommons.org/licenses/by/4.0/"
    title: "CC BY 4.0 (licence on the arXiv HTML/abstract for 2608.21601)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-077 (Codex coordinated)"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

K-Bench 01 takes the first message of a real K-Dense Web session, with whatever files came with it, and asks a frontier model to do the work in a stock agent loop. The requests are underspecified scientific jobs: a count matrix and a differential-expression question, three papers and a replication ask, a clinical export and a power question. There is no answer key.

Nine models each ran all 178 complete-case tasks in identical sandboxes, 1,602 runs in total. Three blinded judges opened the output tree and scored eight dimensions plus a holistic overall. The object of measurement is delivered scientific work, including empty directories and overclaimed results, not a chat reply.

This is not [KernelBench](kernelbench.md) (GPU kernels) and not [K-MetBench](k_metbench.md) (Korean meteorology). Those only share a K- prefix.

## How it is scored

Rubric v1.0 (7 August 2026) scores each dimension 0-10 with written anchors at 0, 3, 5, 8, and 10. Eight means a domain scientist would accept the work with minor edits. Dimensions are task fulfillment, scientific accuracy, reasoning quality, tool use, data handling, artifact quality, communication, and honesty/calibration. Data handling and artifact quality may be N/A. Judges also mark `fully_successful` and tag failures from a 16-tag list.

A run's headline overall is the mean of three judges. Model means average 178 tasks, with 95% percentile bootstrap intervals over sessions. Pairing uses 534 same-task, same-judge comparisons. gpt-5.6-sol's pooled mean is 8.04, interval [7.80, 8.23] in the v2 paper. That interval spans the 8-anchor. Two judges still rank claude-opus-5 first. The only non-contestant judge, qwen3.8-max, ranks claude-opus-5 8.29 above gpt-5.6-sol 8.20. The paper therefore calls the top unresolved.

Across 39,934 scored judgments, 47.6% fall below 8. Scientific accuracy averages 6.22 against communication 7.33, in the same direction for every model. Overclaiming is the leading tag, on 31.4% of assessments. 47.9% of runs write no file.

## Dataset and licence

Items come from about 18,000 K-Dense Web sessions. A uniform draw of 200 sessions, in two batches on 6-7 August 2026, was reduced to sessions that all nine models completed, leaving 178. Follow-up turns were dropped. 70% of sessions carry attachments. Prompt length spans from a 96-byte first-quartile median to 6,217 bytes in the longest quartile.

The prompts, attachments, transcripts, and artifacts are not released. They are user content. The arXiv paper is CC BY 4.0. No dataset licence applies because there is no public dataset. The authors say a de-identified score dump will be enough to check the tables; that dump was not found as a public URL during this research. Language inventory is not published, so `languages` is left empty.

## Who publishes it

Aubrey M. Brueckner, Darshil Patel, Yuhuan He, and Timothy Kassis are all at K-Dense, Inc. Kassis is corresponding author. arXiv v1 is 21 August 2026; v2 (2 September 2026) is textual corrections only. The company blog posted on 25 August 2026. All authors are K-Dense employees, and the corpus is product traffic. The paper states that competing-interest point explicitly.

## Lineage

K-Bench sits with traffic-derived evals such as [WildBench](wildbench.md) and with scientific execution suites such as [LAB-Bench](lab_bench.md) and [CORE-Bench](core_bench.md). The authors' claimed difference is verbatim first turns with attachments, no reconstructed verifier, and judges that open files. Rubric judging is closer to [HealthBench](healthbench.md) than to exact-match science QA. ScienceAgentBench, AstaBench, RealClawBench, and ResearchRubrics do not yet have pages here.

## Saturation and contamination

The suite is open. No model clears the 8-anchor under all three judges. 12.4% of tasks are unsolved by every model on majority vote. Empty-handed rates run from 17.4% (claude-opus-5) to 74.7% (nemotron-3-ultra-550b-a55b).

Contamination risk is low for the usual public-test-set reason: the items are held in. The publisher says the set is not training data. Outside groups cannot audit overlap with public corpora.

## How to run it

You cannot run the official items. The campaign used pi 0.84.0, Modal isolation, OpenRouter model ids, thinking-level max where exposed, and a locked output tree hashed before judging. Two of three judges are also contestants (gpt-5.6-sol, grok-4.5). Blinding removes names, not writing style; gpt-5.6-sol's calibration-adjusted self-preference is +0.83. No standard harness task name exists. The blog frames this as an internal series they intend to rebuild.

## Reading the numbers

A pooled mean near 8 is not a clean win. Ask which judge panel produced it, and whether empty files and overclaiming were scored. claude-opus-5 loses the pooled mean and wins tool-use pairings (73%); gpt-5.6-sol is the more careful scientist on honesty and accuracy. Domain is a weak difficulty signal; long prompts and attachments are stronger. gpt-5.6-sol averaged $8.51 per task against $0.02 for gemma-4-31b-it. Treat K-Bench 01 as one private August 2026 campaign, not as a public leaderboard anyone can extend.
