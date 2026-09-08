---
id: clbench
name: CL-bench
aliases:
  - CLBench
  - "CL-bench: A Benchmark for Context Learning"
page_kind: benchmark
category: reasoning
subcategory: "context learning: applying novel in-prompt knowledge, rule systems and procedures"
status: active
summary: 1,899 tasks testing whether a model can learn new domain knowledge, rules or procedures from its own prompt and apply them; the best of ten frontier models solved only 23.7%.
measures: >
  CL-bench (OpenCompass folder name "CLBench") tests what its authors call context learning: whether a
  model can absorb new, task-specific material supplied directly in its prompt -- new domain-specific
  knowledge, rule systems, complex procedures, or laws derived from empirical data, all absent from
  pretraining -- and then apply that material correctly to solve a task grounded in it. Every one of
  its 1,899 tasks is built so the information needed to solve it sits entirely inside its accompanying
  context; the authors explicitly distinguish this from long-context benchmarks, which mainly test
  retrieval or reading comprehension over a large volume of text, and from ordinary in-context
  learning, where a model learns a simple pattern from a handful of demonstrations. Contexts span four
  main categories and 18 sub-categories (for example "Rule System Application" / "Game Mechanics"),
  and tasks are presented as multi-turn conversations in OpenAI chat format.
task_format: >
  Each sample supplies a multi-turn conversation (a context, in system or user turns, followed by a
  task) and a list of rubric criteria the response must satisfy. The model produces a free-text
  response; there are no answer options.
metric:
  name: "rubric pass rate (binary, LLM-judged, all-or-nothing per task)"
  direction: higher_is_better
  unit: "%"
  max_score: 100
  random_baseline: null
  human_baseline: null
  baseline_note: >
    A task counts as solved only if an LLM judge rates every one of its rubric criteria as satisfied;
    partial credit is not given at the task level. No random-guess baseline applies to open-ended,
    rubric-graded response generation, and no human baseline is reported in the sources reviewed for
    this page. The paper's own headline numbers: across ten evaluated frontier models, tasks were
    solved at an average rate of 17.2%; the best model, GPT-5.1, solved 23.7%.
dataset:
  size: 1899
  size_note: >
    500 complex contexts, 1,899 tasks built from them, and 31,607 verification rubrics in total (about
    16.6 rubrics per task on average), all authored by domain experts, per the paper's abstract. A
    companion dataset, CL-bench Life (see Lineage), adds 405 further context-task pairs and 5,348
    rubrics under a separate arXiv paper and a separate Hugging Face repository; those are not counted
    in this page's dataset.size, which covers the main CL-bench release only.
  url: "https://huggingface.co/datasets/tencent/CL-bench"
  license: >
    Custom "evaluation-only" licence (Hugging Face lists it as "other"): the LICENSE file permits use,
    copying and redistribution of the dataset solely for evaluation, testing and benchmarking of
    models, and explicitly prohibits using it for training, fine-tuning, calibrating, distilling,
    adapting or any other form of parameter updating.
  languages:
    - en
  modalities:
    - text
  splits: >-
    All 1,899 rows ship under a single Hugging Face split named "train" (used directly as the
    evaluation set by OpenCompass); there is no separate held-out test partition.
  public_test_set: true
publisher:
  org: "Hunyuan Team, Tencent, and Fudan University"
  authors:
    - Shihan Dou
    - Ming Zhang
    - Zhangyue Yin
    - Chenhao Huang
    - Yujiong Shen
    - Junzhe Wang
    - Jiayi Chen
    - Yuchen Ni
    - Junjie Ye
    - Cheng Zhang
    - Tao Gui
    - Zuxuan Wu
    - Xipeng Qiu
    - Qi Zhang
    - Xuanjing Huang
    - Yu-Gang Jiang
    - Di Wang
    - Shunyu Yao
  url: "https://github.com/Tencent-Hunyuan/CL-bench"
paper:
  title: "CL-bench: A Benchmark for Context Learning"
  arxiv: "2602.03587"
  url: "https://arxiv.org/abs/2602.03587"
  year: 2026
leaderboard_url: "https://www.clbench.com"
repo_url: "https://github.com/Tencent-Hunyuan/CL-bench"
released: "2026-02"
last_updated: ""
lineage:
  family: ""
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 23.7
  as_of: "2026-02"
  note: >
    Not saturated. The paper's own results show ten frontier models solving 17.2% of tasks on average,
    with the best model, GPT-5.1, reaching only 23.7% -- a low ceiling that the authors present as
    evidence that current models "have yet to achieve effective context learning."
contamination:
  risk: low
  note: >
    The dataset's own licence explicitly forbids using it for training or fine-tuning, and it has been
    public only since around February 2026 (roughly seven months by this research date), which limits
    the window for it to have entered any evaluated model's pretraining data even inadvertently.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "clbench"
  bigbench: ""
  other: >
    OpenCompass also ships a separate dataset abbreviation, "clbench-life", pointing at the companion
    CL-bench Life dataset (tencent/CL-bench-Life) under the same CLBench config folder; both use the
    same rubric-based GenericLLMEvaluator grading approach with a shared binary, all-or-nothing judge
    prompt template.
tags:
  - reasoning
  - context-learning
  - long-context
  - rubric-grading
  - llm-judge
sources:
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/CLBench/clbench_llmjudge_rawprompt_gen_84a8f0.py"
    title: "OpenCompass clbench dataset config (tencent/CL-bench)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/configs/datasets/CLBench/clbench_life_llmjudge_rawprompt_gen_84a8f0.py"
    title: "OpenCompass clbench-life dataset config (tencent/CL-bench-Life)"
    accessed: "2026-09-08"
  - url: "https://github.com/open-compass/opencompass/blob/main/opencompass/datasets/clbench.py"
    title: "OpenCompass CLBenchDataset loader and rubric-judge postprocessing"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/tencent/CL-bench"
    title: "tencent/CL-bench dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://huggingface.co/datasets/tencent/CL-bench-Life"
    title: "tencent/CL-bench-Life dataset card, Hugging Face"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2602.03587"
    title: "CL-bench: A Benchmark for Context Learning"
    accessed: "2026-09-08"
  - url: "https://ar5iv.labs.arxiv.org/html/2602.03587"
    title: "CL-bench paper, full text (ar5iv)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2604.27043"
    title: "CL-bench Life: Can Language Models Learn from Real-Life Context? (companion paper)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2607.25294"
    title: "CLBench-V: Evaluating Multimodal Context Learning from Grounding to Knowledge Acquisition (name-adjacent, unrelated authors)"
    accessed: "2026-09-08"
  - url: "https://arxiv.org/abs/2606.05661"
    title: "Continual Learning Bench: Evaluating Frontier AI Systems in Real-World Stateful Environments (unrelated benchmark, same self-abbreviation \"CL-Bench\")"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 5, slice D"
  reviewed: ""
  reviewed_by: ""
---

## What it measures

CL-bench (the OpenCompass config folder spells it "CLBench") tests what its authors call context learning: whether a model can absorb new, task-specific material supplied directly in its prompt -- new domain-specific knowledge, rule systems, complex procedures, or laws derived from empirical data, all absent from pretraining -- and then apply that material correctly to solve a task grounded in it. Every one of its 1,899 tasks is built so the information needed to solve it sits entirely inside its accompanying context (one of 500 hand-crafted contexts). The authors explicitly distinguish this from long-context benchmarks, which mainly test retrieval or reading comprehension over a large volume of text, and from ordinary in-context learning, where a model learns a simple task pattern from a handful of demonstrations rather than genuinely new knowledge or rules.

Contexts span four main categories and 18 sub-categories (for example "Rule System Application" with the sub-category "Game Mechanics"), and each task is a multi-turn conversation in OpenAI chat format, graded against expert-written rubric criteria rather than a single reference answer.

## How it is scored

A response is judged by an LLM grader against the task's rubric list, following a strict, all-or-nothing protocol: the grader checks every requirement individually, and the task counts as solved (score 1) only if every one is fully met. There are 31,607 rubrics across the 1,899 tasks, about 16.6 per task. OpenCompass implements this with `GenericLLMEvaluator` and a template that asks the judge to list and check each requirement, self-check its own consistency, and output a structured JSON verdict with a binary "Overall Score"; reported accuracy is the share of tasks scored 1.

## Dataset and licence

CL-bench totals 500 contexts, 1,899 tasks and 31,607 rubrics, authored by domain experts rather than mined from an existing corpus. It carries a custom "evaluation-only" licence (recorded as "other" on Hugging Face): permitting use, copying and redistribution solely for evaluating, testing and benchmarking models, and explicitly forbidding use for training, fine-tuning, calibrating or distilling. All 1,899 rows ship in a single split, confusingly still named "train" despite the licence prohibiting training on it; OpenCompass reads that split directly as its evaluation set, with no separate held-out partition, so rubrics and reference material are fully visible to anyone who downloads it.

## Who publishes it

CL-bench was published in February 2026 by a team spanning Tencent's Hunyuan Team and Fudan University, including Shihan Dou, Ming Zhang, Zhangyue Yin, Tao Gui, Zuxuan Wu, Xipeng Qiu, Qi Zhang, Xuanjing Huang and Yu-Gang Jiang among eighteen listed authors. The team maintains the dataset on Hugging Face (`tencent/CL-bench`), a reference implementation on GitHub (`Tencent-Hunyuan/CL-bench`), and a standalone leaderboard at clbench.com.

## Lineage

The name "CL-bench" / "CLBench" is genuinely ambiguous and this page documents only one of several distinct things it can mean. Closest to home, the same authors published a direct companion, **CL-bench Life** ("Can Language Models Learn from Real-Life Context?", arXiv 2604.27043, April 2026), extending the same idea to messier, everyday contexts with 405 further context-task pairs; OpenCompass wires this up as a separate `clbench-life` config in the same folder as this page's `clbench`. A different team (Lai Wei, Chengqi Li and colleagues) later published **CLBench-V** (arXiv 2607.25294, July 2026), extending the same framing to multimodal contexts; it is not wired into OpenCompass's CLBench folder and is not what this page's id resolves to. Separately, and unrelated beyond the abbreviation, Parth Asawa, Christopher M. Glaze and colleagues published **Continual Learning Bench**, self-abbreviated "CL-Bench" (arXiv 2606.05661, June 2026), testing whether AI systems improve through sequential experience across six domains -- a genuinely different capability (learning across episodes over time) from single-shot context learning, sharing only the name. A score reported simply as "CLBench" should specify which of these it names.

## Saturation and contamination

CL-bench is not saturated: across ten evaluated frontier models the paper reports an average solve rate of only 17.2%, with the best model, GPT-5.1, reaching just 23.7%. The authors present this low ceiling as the paper's central finding -- current frontier models "have yet to achieve effective context learning." Contamination risk is assessed as low: the licence explicitly forbids training or fine-tuning on the data, and it has been public only since around February 2026, roughly seven months by this research date, limiting the window for inadvertent inclusion in pretraining data.

## How to run it

OpenCompass implements this as the `clbench` dataset (folder `CLBench`), loading `tencent/CL-bench` and grading with `GenericLLMEvaluator` against the strict rubric-judge template above; a sibling `clbench-life` dataset in the same folder evaluates the companion CL-bench Life data the same way. No lm-evaluation-harness, inspect_evals, HELM or BIG-bench implementation was found. Because grading depends entirely on which model serves as judge and how strictly it applies the all-or-nothing rubric, scores from different judge configurations are not guaranteed comparable.

## Reading the numbers

A high CL-bench score suggests a model can genuinely absorb new rules, procedures or domain knowledge placed in its prompt and apply them correctly, by the authors' own framing a harder skill than retrieving facts from a long document or following a simple in-context demonstration. Given that even the best model solved under a quarter of tasks at release, a reported score is evidence of a real capability gap rather than near-ceiling performance, and a small difference between two models is unlikely to be noise given how far both sit from 100%. Because scoring runs through an LLM judge applying a strict rubric check, confirm which judge model produced a given score, and do not confuse a "CLBench" figure with CL-bench Life, CLBench-V, or the unrelated Continual Learning Bench.
