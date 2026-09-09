---
id: inference_ppl
name: "Inference-PPL"
aliases:
  - "inference-ppl"
  - "OpenCompass InferencePPL"
page_kind: benchmark
category: generation
subcategory: "token-weighted negative log-likelihood on labeled spans of a reasoning corpus"
status: unknown
summary: "OpenCompass metric that averages token NLL only on labeled positions, shipped with a local cn-reasoning-val example rather than a fixed public test."
measures: >
  Inference-PPL is a language-modeling score, not a multiple-choice exam.
  OpenCompass feeds each example's text through InferencePPLOnlyInferencer and
  asks the model for a tokenwise loss on labeled positions, then averages those
  losses. The config README says the method is meant for reasoning corpora,
  where only the "answer" or other marked span should contribute. The bundled
  example file is named cn-reasoning-val.jsonl under ./data/inference_ppl.
  The same inferencer can point at other jsonl files with a text field.
task_format: >
  Zero-shot completion over raw {text}. The dataset loader requires a local
  jsonl named {name}.jsonl (default name cn-reasoning-val), drops empty texts,
  and sets output_column to None. The inferencer then calls
  get_ppl_tokenwise_from_template(entry, label) and stores per-example ppl and
  token_len. AverageInferencePPLEvaluator returns sum(ppl) / sum(token_len).
metric:
  name: "average_ppl (token-weighted mean of labeled-span NLL)"
  direction: lower_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: >
    The README writes a mean negative-log-probability formula and labels it
    ppl; it is not exp(NLL). Example numbers in that README are Qwen1.5-7B
    0.59, Qwen1.5-14B 0.54, Llama-2-7B 0.49, Llama-2-13B 0.43, which sit in
    NLL range rather than typical perplexity (>1). No random or human baseline
    applies.
dataset:
  size: null
  size_note: >
    OpenCompass does not publish an item count. The default config loads a
    local file ./data/inference_ppl/cn-reasoning-val.jsonl; that file is not
    in the GitHub configs tree. samples=None means the full jsonl test split;
    setting samples to an integer truncates to test[:N].
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/inference_ppl"
  license: ""
  languages: []
  modalities:
    - text
  splits: "local jsonl loaded as Hugging Face test (optional test[:N] truncation)"
  public_test_set: false
publisher:
  org: "OpenCompass"
  authors: []
  url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/inference_ppl"
paper:
  title: ""
  arxiv: ""
  url: ""
  year: null
leaderboard_url: ""
repo_url: "https://github.com/open-compass/opencompass/tree/main/opencompass/configs/datasets/inference_ppl"
released: ""
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
    The README table only lists four 2024-era open models on the example file.
    No current leaderboard cell was read.
contamination:
  risk: unknown
  note: >
    The example corpus is a local jsonl that is not in the public configs
    tree. Whether those texts appear in pretraining is not established.
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: "inference_ppl"
  bigbench: ""
  other: >
    Runnable example: python run.py examples/eval_inference_ppl.py. Dataset
    abbr is inference-ppl. Inferencer InferencePPLOnlyInferencer; evaluator
    AverageInferencePPLEvaluator in icl_misc_evaluator.py. Distinct from
    OpenCompass PPLInferencer, which picks a multiple-choice label by minimum
    sequence perplexity.
tags:
  - opencompass
  - perplexity
  - language-modeling
  - reasoning-corpus
sources:
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/inference_ppl/README.md"
    title: "inference_ppl README (labeled-span NLL formula, cn-reasoning-val, four model numbers)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/configs/datasets/inference_ppl/inference_ppl.py"
    title: "inference_ppl.py (InferencePPLDataset, abbr inference-ppl, path ./data/inference_ppl)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/examples/eval_inference_ppl.py"
    title: "examples/eval_inference_ppl.py (Qwen1.5 7B/14B and Llama-2 7B/13B)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/datasets/inference_ppl.py"
    title: "InferencePPLDataset loader (local jsonl, empty-text filter)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/openicl/icl_inferencer/icl_inference_ppl_only_inferencer.py"
    title: "InferencePPLOnlyInferencer (tokenwise ppl, no choice)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/opencompass/openicl/icl_evaluator/icl_misc_evaluator.py"
    title: "AverageInferencePPLEvaluator (sum ppl / sum token_len)"
    accessed: "2026-09-08"
  - url: "https://raw.githubusercontent.com/open-compass/opencompass/main/LICENSE"
    title: "OpenCompass Apache License 2.0"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "Grok Build, batch-050 (Codex coordinated)"
  reviewed: "2026-09-08"
  reviewed_by: "Grok Build independent review, batch-050"
---

## What it measures

Inference-PPL asks how surprised a model is on the labeled tokens of a text, not which letter it would pick on a quiz. OpenCompass's README describes the intended use as scoring a reasoning corpus where only marked positions count. The default config looks for `cn-reasoning-val.jsonl` under `./data/inference_ppl`. That file is not in the public configs tree, so this page cannot name the prompts or the language. The method can be reused on any jsonl with a `text` field.

This is not OpenCompass `PPLInferencer`. That class scores multiple-choice items by taking the option with the lowest full-sequence perplexity. Inference-PPL never chooses a label.

## How it is scored

`InferencePPLOnlyInferencer` calls `get_ppl_tokenwise_from_template` and writes per-example `ppl` and `token_len`. `AverageInferencePPLEvaluator` returns `sum(ppl) / sum(token_len)`, a token-weighted mean. The README's displayed formula is mean negative log probability, not `exp` of that mean. Lower is better. The four example scores (0.43–0.59) sit in NLL range. Do not treat them as conventional perplexity.

The example run script evaluates Qwen1.5-7B, Qwen1.5-14B, Llama-2-7B and Llama-2-13B with batch size 8. Those numbers are tied to the unpublished example file.

## Dataset and licence

No public item count, language list or dataset licence was established. The loader requires a local jsonl. OpenCompass itself is Apache-2.0; that grant covers the harness, not an unseen corpus. `public_test_set` is false because the default file is not on GitHub.

## Who publishes it

OpenCompass maintains the config, inferencer and evaluator. No paper, author list or leaderboard is attached to this dataset directory. The example script lives at `examples/eval_inference_ppl.py`.

## Lineage

This is a scoring method, not a successor to a named exam. It is easy to confuse with OpenCompass's many `*_ppl` multiple-choice configs (for example Winograd-ppl). Those pick a class. This one reports a mean labeled-span loss.

## Saturation and contamination

The only numbers in the README are four mid-size open models on the example file. No ceiling is known. Contamination cannot be judged without the corpus.

## How to run it

Place a jsonl at `./data/inference_ppl/cn-reasoning-val.jsonl`, then:

```
python run.py examples/eval_inference_ppl.py
```

or import `inference_ppl_datasets` from `opencompass.configs.datasets.inference_ppl.inference_ppl`. Change `name` to point at another jsonl stem. Compare runs only when the file, the labeled-span definition and the token-weighted average match.

## Reading the numbers

A lower Inference-PPL means the model assigned higher probability to the labeled tokens of that local file. It does not mean the model solved the underlying reasoning items, and it is not a multiple-choice accuracy. Quote the jsonl name and whether the reporter used `exp` of the mean. A 0.43 on Llama-2-13B in the README is not "43%." Pair it with a task that grades answers if you care about correctness rather than token loss.
