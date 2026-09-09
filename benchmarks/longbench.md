---
id: longbench
name: "LongBench"
aliases: ["LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding"]
page_kind: benchmark
category: long-context
subcategory: "bilingual multitask long-context understanding (QA, summarization, few-shot learning, synthetic tasks, code completion)"
status: active
summary: "A bilingual English/Chinese suite of 21 tasks across six categories, testing long-context understanding at moderate lengths of roughly 5k-15k words per document."
measures: >
  LongBench gives a model a document, or set of documents, roughly 5,000-15,000 words long and asks
  it to complete one of 21 tasks grouped into six categories: single-document QA, multi-document QA,
  summarization, few-shot in-context learning, synthetic retrieval/counting, and code completion.
  Fourteen tasks are in English, five are in Chinese, and two language-general code-completion tasks
  draw on GitHub repositories in Python, C#, and Java. English instances average 6,711 words; Chinese
  instances average 13,386 characters. Six of the 21 datasets are taken directly from earlier public
  benchmarks, ten are adapted and reprocessed for length, and five were built by the authors. A
  companion split, LongBench-E, resamples 13 of the 21 datasets for a length distribution balanced
  across 0-4k, 4-8k and 8k+ tokens, isolating length effects from task difficulty.
task_format: >
  A long document or documents plus a short task-specific instruction (a question, a classification
  query, a summarization prompt, or a code-completion prefix) in; a short free-form answer, label, or
  code continuation out. Evaluated zero-shot by default, with per-task automatic metrics rather than
  a single shared scoring rule.
metric:
  name: "task-specific metric (F1, ROUGE-L, classification accuracy, exact-match accuracy, or edit similarity), averaged across the 21 tasks for a headline score"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    No single random or human baseline applies across all 21 tasks and five underlying metric types;
    the paper reports category-level and per-task scores per model instead of one baseline figure.
dataset:
  size: 4750
  size_note: >
    4,750 test instances across 21 datasets: 19 hold 200 instances each except MultiFieldQA-en (150),
    and the two code-completion tasks (LCC, RepoBench-P) hold 500 each. Test-only; there is no
    separate train or validation split. LongBench-E is a second, length-balanced resampling of 13 of
    the 21 datasets, not additional unique data.
  url: "https://huggingface.co/datasets/zai-org/LongBench"
  license: "MIT for the LongBench code and packaging (GitHub repository); underlying source documents carry mixed original licences not restated in one place -- for example the paper describes MultiFieldQA's sources as arXiv papers, the ODC-BY-licensed C4 corpus, WuDaoCorpora, Chinese court judgment records, CC BY-SA Wikipedia, and Chinese government reports."
  languages: ["en", "zh"]
  modalities: ["text", "code"]
  splits: "test only (4,750 instances across 21 datasets); LongBench-E is a separate length-balanced resampling of 13 datasets for the same test purpose."
  public_test_set: true
publisher:
  org: "Tsinghua University, Zhipu.AI, and the Institute of Automation, Chinese Academy of Sciences"
  authors: ["Yushi Bai", "Xin Lv", "Jiajie Zhang", "Hongchang Lyu", "Jiankai Tang", "Zhidian Huang", "Zhengxiao Du", "Xiao Liu", "Aohan Zeng", "Lei Hou", "Yuxiao Dong", "Jie Tang", "Juanzi Li"]
  url: "https://github.com/THUDM/LongBench"
paper:
  title: "LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding"
  arxiv: "2308.14508"
  url: "https://arxiv.org/abs/2308.14508"
  year: 2023
leaderboard_url: "https://github.com/THUDM/LongBench/blob/main/LongBench/README.md"
repo_url: "https://github.com/THUDM/LongBench"
released: "2023-08"
last_updated: "2024-12"
lineage:
  family: ""
  predecessor: ""
  successors: ["longbenchv2"]
  variants: []
saturation:
  status: watch
  top_score: 48.5
  as_of: "2023-08"
  note: >
    The authors' own reference table (2023-era models only) shows real headroom: the strongest model
    tested, ChatGLM3-6B-32k, averaged 48.5% across English task categories and 52.8% across Chinese
    ones, with every model under 30% on summarization. No current, actively maintained leaderboard
    with newer frontier models was found during this research; the project's public attention and
    update cadence have shifted to LongBench v2 since its December 2024 release (its own README notes
    v1 files were moved into a `LongBench/` subdirectory), so a present-day top score for the original
    LongBench is not established here. A harder, actively tracked successor now exists, which is why
    this page marks the benchmark "watch" rather than "open".
contamination:
  risk: medium
  note: >
    Six of the 21 datasets are lifted directly from older public benchmarks with public answers
    (including HotpotQA, TriviaQA and 2WikiMultihopQA), so a model trained on those source datasets
    could see contamination independent of LongBench itself. The four synthetic tasks and the
    author-written subsets are less exposed since they are newly constructed, but the full test set
    and its answers have been public and downloadable without gating since August 2023.
harness:
  lm_eval: "longbench (task groups longbench_single, longbench_multi, longbench_summarization, longbench_fewshot, longbench_synthetic, longbench_code; each has an _e LongBench-E variant, plus per-task tasks such as hotpotqa, gov_report, lcc)"
  inspect_evals: ""
  helm: ""
  opencompass: "longbench (per-task configs, e.g. longbenchhotpotqa, longbenchgov_report, longbenchlcc, longbenchrepobench)"
  bigbench: ""
  other: "The authors' own pred.py/eval.py scripts in the THUDM/LongBench repository are the reference implementation and additionally support retrieval- and summarization-based context-compression baselines."
tags: ["long-context", "bilingual", "multitask", "question-answering", "summarization", "code-completion", "synthetic", "zero-shot"]
sources:
  - url: "https://arxiv.org/abs/2308.14508"
    title: "LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding (Bai et al., arXiv:2308.14508)"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2308.14508"
    title: "LongBench, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://github.com/THUDM/LongBench"
    title: "THUDM/LongBench GitHub repository (MIT licence, LongBench and LongBench v2 side by side)"
    accessed: "2026-09-08"
  - url: "https://github.com/THUDM/LongBench/blob/main/LongBench/README.md"
    title: "LongBench v1 subdirectory README (task table, leaderboard, evaluation instructions)"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/zai-org/LongBench"
    title: "zai-org/LongBench dataset card, Hugging Face (formerly THUDM/LongBench)"
    accessed: "2026-09-08"
  - url: "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/longbench/README.md"
    title: "lm-evaluation-harness longbench task README (groups, tasks, changelog)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/longbench"
    title: "OpenCompass longbench dataset configs"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 3, slice A"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

LongBench gives a model a document, or a small set of documents, roughly 5,000-15,000 words long and
asks it to complete one of 21 tasks grouped into six categories: single-document QA, multi-document
QA, summarization, few-shot in-context learning, synthetic retrieval and counting, and code
completion. Fourteen tasks are in English, five are in Chinese, and two language-general
code-completion tasks (LCC, RepoBench-P) draw on GitHub repositories written in Python, C# and Java.
English instances average 6,711 words; Chinese instances average 13,386 characters. Six of the 21
datasets are taken directly from earlier public benchmarks such as HotpotQA and TriviaQA, ten are
adapted from existing sources and reprocessed for length, and five -- including two of the three
synthetic tasks -- were built by the authors themselves.

A companion split, LongBench-E, resamples 13 of the 21 datasets to give a length distribution
balanced across 0-4k, 4-8k and 8k+ tokens, which lets a user isolate how performance changes with
length independent of task difficulty.

## How it is scored

Each of the 21 datasets is scored with the metric suited to its task: F1 for extractive QA, ROUGE-L
for summarization and dialogue summarization, classification accuracy for the two few-shot
classification tasks (TREC and LSHT), exact-match accuracy for the three synthetic tasks, and edit
similarity for the two code-completion tasks. A model's overall LongBench score averages across all
21 datasets; category-level and per-task scores are also reported and carry most of the useful
signal, since the headline average blends several unrelated metrics. Text longer than a model's
context window is truncated from the middle, preserving the beginning and end, following the "Lost
in the Middle" finding that models attend less reliably to buried content. Zero-shot is the default
reported setting.

## Dataset and licence

4,750 test instances span the 21 datasets: 19 hold 200 instances each except MultiFieldQA-en (150),
and the two code-completion tasks hold 500 each. There is no separate train or validation split --
LongBench is test-only. The GitHub repository (THUDM/LongBench, also mirrored on Hugging Face under
the zai-org namespace after Zhipu AI's Z.ai rebrand) is MIT-licensed, but the underlying documents
come from many original sources with their own terms: the paper describes MultiFieldQA's source
documents alone as drawn from arXiv papers, the ODC-BY-licensed C4 corpus, WuDaoCorpora, Chinese
court judgment records, CC BY-SA Wikipedia, and Chinese government reports, so no single licence
covers every item. All answers are public; the Hugging Face dataset card reports over 60,000
downloads.

## Who publishes it

Yushi Bai, Xin Lv, Jiajie Zhang, Hongchang Lyu, Jiankai Tang, Zhidian Huang, Zhengxiao Du, Xiao Liu,
Aohan Zeng, Lei Hou, Yuxiao Dong, Jie Tang and Juanzi Li published LongBench in August 2023, with
authors from Tsinghua University, Zhipu.AI, and the Institute of Automation at the Chinese Academy of
Sciences; the paper later appeared at ACL 2024. The same Tsinghua/Zhipu.AI group actively maintains
the GitHub repository, most recently adding LongBench v2 in December 2024 and moving the original
benchmark's files into a `LongBench/` subdirectory of the same repo.

## Lineage

LongBench positions itself against earlier, narrower long-context suites (ZeroSCROLLS, L-Eval) that
it says covered fewer task types, and against context-length probes that rely only on perplexity or
single-fact retrieval. Its own successor, built by an overlapping author team, is LongBench v2
(`longbenchv2`, December 2024): LongBench's fairly short 5k-15k-word contexts and largely extractive
tasks stopped stressing newer, longer-context models, so LongBench v2 runs contexts from 8k to 2M
words and requires genuine multi-step reasoning rather than retrieval. This repository also
catalogues two unrelated long-context suites built around a similar goal of testing beyond a single
short document -- `infinitebench`, which pushes past 100K tokens with a different 12-task mix, and
`ruler`, a synthetic length-controllable suite -- neither of which shares data or authorship with
LongBench.

## Saturation and contamination

The authors' own 2023 reference table shows real headroom at the time: the strongest model tested,
ChatGLM3-6B-32k, averaged 48.5% across English task categories and 52.8% across Chinese ones, with
every tested model under 30% on summarization in both languages. No current, actively maintained
leaderboard with newer frontier models was found during this research; the project's attention and
update cadence have shifted to LongBench v2 since its December 2024 release, so a present-day top
score for the original LongBench is not established here. Contamination risk is medium: six of the
21 datasets are lifted directly from older public benchmarks with public answers, so a model trained
on those source datasets could see contamination independent of LongBench itself, while the synthetic
and author-written subsets are less exposed; the full test set and its answers have been public and
downloadable without gating since August 2023.

## How to run it

lm-evaluation-harness implements all 21 tasks under task groups `longbench_single`, `longbench_multi`,
`longbench_summarization`, `longbench_fewshot`, `longbench_synthetic` and `longbench_code`, each with
an `_e` LongBench-E variant, alongside a `LongBench` tag for the standard 21-task suite. OpenCompass
carries an equivalent per-task config set under `longbench`. The original authors' own scripts
(`pred.py`, `eval.py` in the GitHub repository) remain the reference implementation and additionally
support retrieval- and summarization-based context-compression baselines alongside plain long-context
evaluation. Because LongBench truncates from the middle on over-length inputs and several tasks use
free-form generation graded by automatic metrics rather than exact match, scores can shift with
prompt template and generation-length settings even at a fixed task and language.

## Reading the numbers

A strong LongBench score shows a model can extract, summarize or manipulate information from a
moderately long (5k-15k word) bilingual document better than the 2023-era models the benchmark was
built to separate -- but the benchmark predates today's much longer context windows, and its
predominantly extractive tasks are weaker evidence of deep multi-step reasoning over long context
than LongBench v2's harder multiple-choice format. Because the headline average blends F1, ROUGE-L,
classification accuracy, exact match and edit similarity across very different tasks, check the
category and per-task breakdown rather than trusting the single number, and note whether a reported
score used the standard suite or the length-balanced LongBench-E split before comparing it against
another report.
