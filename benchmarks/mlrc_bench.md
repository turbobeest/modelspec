---
id: mlrc_bench
name: "MLRC-Bench"
aliases: ["MLRC-Bench: Can Language Agents Solve Machine Learning Research Challenges?"]
page_kind: benchmark
category: agentic
subcategory: "machine-learning research-competition agent benchmark (novel methods vs. baseline and top human)"
status: active
summary: "Tests whether a language agent can propose and implement a genuinely novel ML method across 7 real research-competition tasks, scored against each competition's own baseline and top human result."
measures: >
  MLRC-Bench gives an agent an open machine-learning research problem adapted from a real competition
  at a recent ML conference (NeurIPS, KDD, ECCV and similar venues, spanning areas such as LLM safety,
  computer vision and AI for science): a baseline code repository, background literature, and dev-set
  data to iterate against. The agent must propose a new method, implement it in code, and run it, with
  its final version evaluated once on a held test split. Unlike end-to-end agent benchmarks that grade
  a full pipeline with an LLM-as-judge, MLRC-Bench isolates the specific steps of proposing and
  implementing a novel method and grades the result with each competition's own objective metric,
  explicitly to avoid rewarding an agent for sounding innovative rather than being effective.
task_format: >
  The agent works inside a per-task sandboxed environment (its own conda/Docker setup, described in a
  README the agent can read) with shell and code-execution access, iterating on a development split
  for a time or message budget. Its method is then run once via the task's own `main.py -m
  <method_name> -p test` command on the held test split; some tasks (llm-merging, machine-unlearning,
  product-rec) require submitting a run to Kaggle or AIcrowd to obtain the final score rather than
  scoring locally.
metric:
  name: "relative_improvement_to_human (primary), with absolute_improvement_to_baseline reported alongside"
  direction: higher_is_better
  unit: "%"
  max_score: null
  random_baseline: 0
  human_baseline: 100
  baseline_note: >
    Both headline metrics are normalized per task rather than raw: relative_improvement_to_human =
    (agent_score - baseline_score) / (top_human_score - baseline_score) x 100, so 0 means the agent
    matched the provided baseline, 100 means it matched the competition's top human result, and a
    negative value means the agent did worse than the baseline it started from. absolute_improvement_to_baseline
    instead expresses the agent's gain as a percentage of the baseline's own score. There is no fixed
    upper bound -- an agent that beats the top human scores above 100 on the first metric.
dataset:
  size: 7
  size_note: >
    MLRC-Bench's first release ships 7 task environments, not 7 questions: llm-merging,
    backdoor-trigger (recovery), temporal-action-loc, machine-unlearning, meta-learning, product-rec
    and weather-forecast, each adapted from a real conference competition and each a full baseline
    repository plus development and test data rather than a single graded item. The Hugging Face
    metadata for the companion dataset (a single `mlrc.csv` summary file listing task metadata such
    as baseline and top-human scores) is tagged `size_categories:n<1K`, consistent with one row per
    task rather than per test item. As of this research, the third-party inspect_evals port notes the
    weather-forecast task's data source was unavailable at implementation time and excludes it from
    evaluation by default, leaving 6 runnable tasks in that harness.
  url: "https://huggingface.co/datasets/yunx-z/MLRC-Bench"
  license: "CC-BY-4.0 (Hugging Face dataset card and the companion Space's cardData both state this)"
  languages: ["en"]
  modalities: ["text", "code"]
  splits: "each of the 7 tasks has its own development split (visible to the agent for iteration) and a held test split (scored once, sometimes only via external submission to Kaggle or AIcrowd)"
  public_test_set: false
publisher:
  org: "University of Michigan; LG AI Research; University of Illinois at Chicago"
  authors: ["Yunxiang Zhang", "Muhammad Khalifa", "Shitanshu Bhushan", "Grant D Murphy", "Lajanugen Logeswaran", "Jaekyeom Kim", "Moontae Lee", "Honglak Lee", "Lu Wang"]
  url: "https://github.com/yunx-z/MLRC-Bench"
paper:
  title: "MLRC-Bench: Can Language Agents Solve Machine Learning Research Challenges?"
  arxiv: "2504.09702"
  url: "https://arxiv.org/abs/2504.09702"
  year: 2025
leaderboard_url: "https://huggingface.co/spaces/launch/MLRC_Bench"
repo_url: "https://github.com/yunx-z/MLRC-Bench"
released: "2025-04"
last_updated: "2026-04"
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 9.3
  as_of: "2025-04"
  note: >
    Wide open. At release, the best-performing tested agent configuration (gemini-exp-1206 run under
    the MLAB agent scaffold) closed only 9.3% of the gap between the provided baseline and the top
    human competition result, per the paper's own headline finding. A later, independent reproduction
    in the inspect_evals implementation, evaluating openai/gpt-4o under the same MLAB scaffold, found
    relative_improvement_to_human negative on five of six runnable tasks (as low as -8.9 on
    meta-learning) and barely positive on the sixth (2.0 on llm-merging) -- meaning that reproduction's
    agent often did worse than simply keeping the baseline method. The paper separately reports a
    misalignment between how novel an LLM judge rates an agent's idea and how well that idea actually
    performs, underscoring that the benchmark is not close to saturated by any tested agent so far.
contamination:
  risk: low
  note: >
    Each task's competition, baseline code and held test data are drawn from real, recent ML
    conference competitions, with test-time evaluation routed through external platforms (Kaggle,
    AIcrowd) for several tasks rather than shipped as static labelled files, which limits direct
    memorization of test answers. Task authors do provide agents with a `background.txt` of excerpts
    from related papers and technical reports to inspire solutions, which is deliberate context rather
    than leakage, and baseline repositories and competition writeups are plausibly present in some
    models' pretraining data independent of this benchmark.
harness:
  lm_eval: ""
  inspect_evals: "mlrc_bench"
  helm: ""
  opencompass: ""
  bigbench: ""
  other: >
    The original authors maintain the reference implementation and leaderboard at yunx-z/MLRC-Bench,
    built on top of Stanford's MLAgentBench agent scaffold (snap-stanford/MLAgentBench). A separate,
    community-contributed inspect_evals port re-implements scoring against the same upstream harness
    and documents several environment-setup fixes it needed to make tasks runnable, plus GPU
    requirements (16GB or 48GB VRAM depending on task).
tags: ["agentic", "machine-learning-research", "code-generation", "competition", "novelty", "coding"]
sources:
  - url: "https://arxiv.org/abs/2504.09702"
    title: "MLRC-Bench: Can Language Agents Solve Machine Learning Research Challenges? (Zhang et al., arXiv:2504.09702)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2504.09702"
    title: "MLRC-Bench, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/yunx-z/MLRC-Bench"
    title: "yunx-z/MLRC-Bench GitHub repository (setup, task list, task-contribution instructions)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/yunx-z/MLRC-Bench"
    title: "yunx-z/MLRC-Bench dataset card, Hugging Face (CC-BY-4.0, code and leaderboard links)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/spaces/launch/MLRC_Bench"
    title: "MLRC-Bench leaderboard, Hugging Face Space (launch/MLRC_Bench)"
    accessed: "2026-09-08"
  - url: "https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/mlrc_bench"
    title: "inspect_evals mlrc_bench task README (scoring formulas, task list, evaluation report, changelog)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

MLRC-Bench gives a language agent an open machine-learning research problem adapted from a real
competition at a recent conference such as NeurIPS, KDD or ECCV, covering areas including LLM
safety, computer vision and AI for science. The agent receives a baseline code repository,
background literature, and development data to iterate against, and must propose a genuinely new
method, implement it, and run it, with the final version evaluated once on a held test split. Unlike
benchmarks that judge an entire agentic pipeline end to end with an LLM-as-judge, MLRC-Bench isolates
the specific steps of proposing and implementing a method, and scores the result with each
competition's own objective metric rather than a judge's opinion of how novel the idea sounds.

## How it is scored

A task's raw performance metric (accuracy, error rate, or whatever the original competition used) is
converted into two normalized, cross-task metrics. `relative_improvement_to_human` measures how much
of the gap between the provided baseline and the competition's top human result the agent closed: 0
means it matched the baseline, 100 means it matched the top human, and a negative score means the
agent's method performed worse than simply keeping the baseline. `absolute_improvement_to_baseline`
instead expresses the gain as a percentage of the baseline's own score. Runtime and implementation
complexity, relative to the baseline's, are also recorded per task but are not part of the two
headline summary metrics, which are averaged across all tasks except machine-unlearning (its score
requires a manual Kaggle submission step). A failed run -- for example, an agent that never produces
a results file -- scores 0.0 on both headline metrics, the same as an agent that made no improvement
at all.

## Dataset and licence

The first release covers 7 task environments rather than a conventional item set: llm-merging,
backdoor-trigger recovery, temporal-action-loc, machine-unlearning, meta-learning, product-rec and
weather-forecast, each a full baseline repository with its own development and test data, curated
from real competitions. A companion Hugging Face dataset (`yunx-z/MLRC-Bench`, CC-BY-4.0) ships a
single summary file of per-task metadata rather than graded items. Test-time scoring for several
tasks (llm-merging, machine-unlearning, product-rec) runs through external Kaggle or AIcrowd
submissions rather than a static labelled file the agent can read directly. The weather-forecast
task's data source was unavailable at the time the community's inspect_evals port was built and is
excluded from that harness's evaluation by default.

## Who publishes it

Yunxiang Zhang, Muhammad Khalifa, Shitanshu Bhushan, Grant D Murphy, Lajanugen Logeswaran, Jaekyeom
Kim, Moontae Lee, Honglak Lee and Lu Wang published MLRC-Bench in April 2025, with authors at the
University of Michigan, LG AI Research and the University of Illinois at Chicago; the paper was
accepted to the NeurIPS 2025 Datasets and Benchmarks track. The authors maintain the reference
implementation and a public leaderboard (`launch/MLRC_Bench` on Hugging Face), and continue to accept
community-contributed tasks by pull request.

## Lineage

MLRC-Bench has no predecessor or successor tracked in this repository. Its agent scaffold is built
directly on Stanford's MLAgentBench (`snap-stanford/MLAgentBench`), acknowledged in the repository as
foundational infrastructure rather than as a formal predecessor benchmark. Within this repository,
`mle_bench` (agents acting as ML engineers on 75 Kaggle competitions, graded against medal
thresholds) and `core_bench` (agents reproducing a published paper's results) are related but
distinct agentic ML benchmarks: MLE-bench targets engineering execution against known techniques, and
CORE-Bench targets reproduction of existing work, while MLRC-Bench specifically targets proposing and
implementing methodological novelty against an open research problem.

## Saturation and contamination

Far from saturated. At release, the best-performing tested agent (gemini-exp-1206 under the MLAB
scaffold) closed only 9.3% of the gap between baseline and top human performance, and a later,
independent inspect_evals reproduction running gpt-4o found negative relative-improvement scores on
five of six runnable tasks -- meaning that agent configuration often did worse than the baseline it
started from. The paper separately documents a misalignment between LLM-judged novelty and actual
task performance. Contamination risk is assessed as low: held test scores for several tasks are
computed externally via Kaggle or AIcrowd rather than shipped as static answer files, though baseline
code and competition writeups are plausibly present in some pretraining corpora independent of this
benchmark.

## How to run it

The authors' own repository provides the reference harness, built on MLAgentBench, with per-task
conda/Docker environments and a `bash launch.sh ${TASK_NAME} ${MODEL} ${GPU_ID}` entry point.
inspect_evals ships an independent port under the id `mlrc_bench` (`uv run inspect eval
inspect_evals/mlrc_bench`), which documents environment-setup fixes it needed relative to the
original benchmark code, requires a GPU (16GB or 48GB VRAM depending on task), and needs Kaggle
and/or AIcrowd credentials for several tasks. Because MLRC-Bench measures whichever method an agent
last successfully evaluated on the development split -- rather than the best one it tried across
several trials, as the original paper's eight-trial-best protocol does -- scores from a
single-attempt harness run are not directly comparable to the paper's own reported numbers.

## Reading the numbers

A positive MLRC-Bench score is meaningful evidence an agent can do more than apply a known technique:
it proposed, implemented and validated something better than a competition's own baseline, on a
problem where competent humans have already tried and where a top human result sets the upper
reference point. Given how far even frontier agents currently sit from that reference point, and how
often a naive rerun can score at or below zero, a small positive number is more informative here than
on more saturated coding benchmarks. Because the benchmark is explicitly designed to grow with new
competitions, and because trial count and which model plays each of the agent's helper roles (editing
scripts, reflection) can shift results, check the task count, model and agent-scaffold version behind
any two scores before comparing them directly.
