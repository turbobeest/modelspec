# OLL leftovers audit (MODEL-154)

Read on 2026-09-24. This follows MODEL-116 / PR #232. Only cards, this audit
record and regression tests change. The v1 ranking implementation and the
`premier/` directory are outside this change.

## Method

The source is the model's own repository in the Open LLM Leaderboard v2
[results dataset](https://huggingface.co/datasets/open-llm-leaderboard/results).
The frozen dataset revision, exact run URLs, model revisions, precision and
raw metrics are in
[`tests/fixtures/oll_leftovers_audit.json`](../../tests/fixtures/oll_leftovers_audit.json).
All external sources in that record were read on 2026-09-24. Fetches used
plain HTTP; Firecrawl usage was zero.

A repository match is exact, ignoring case. The documented THUDM to zai-org
rename is the only repository alias accepted. Mirrors, quantizations, base
models and instruction-tuned models do not share evidence. For each card,
retain a run matching its existing IFEval value when one exists. Otherwise,
prefer bfloat16, then the latest available result file within that precision.
This selects a reproducible run, not the highest score. No exact repository
row or run means null. The 12 cards without their own results have all four
unsupported keys removed. The current flat-score schema does not accept
literal YAML nulls; absence represents null without widening the contract.

The arithmetic reproduces the leaderboard's raw columns:

- IFEval: mean of strict prompt-level and strict instruction-level accuracy.
  It is a composite, not either stock IFEval metric on its own.
- BBH and MuSR: unweighted mean of subtask `acc_norm` values. The harness's
  sample-weighted group aggregates differ and are not the published raw column.
- MMLU-Pro: `acc`.

Multiply each by 100 and round to one decimal place. Do not use the
leaderboard's normalized columns. These remain legacy flat values with
qualified audit notes; this single-agent audit does not confer independent
verification or promote values into decision-engine evidence.

## IFEval sample and complete check

The starting inventory had 160 non-null IFEval values on cards mentioning
OLL v2. A deterministic sample used sorted card paths and
`random.Random(154).sample(population, ceil(n * 0.1))`, selecting 16.
Git history then identified 20 IFEval values unchanged since initial release
`21d504b3`, before OLL enrichment, with lab-report provenance. One was in the
sample. They are excluded from the OLL audit and retained unchanged; the
fixture lists each card and its original attribution. This is a provenance
exclusion, not a claim that those values have been verified.

MODEL-116 removes two failed-run zeros, neither in the sample. That leaves
138 OLL-sourced values, and 15 sampled values (10.87%). Three of 15 were
wrong or unsupported (20%): open-mixtral-8x7b, qwen2-5-math-1-5b and the
NousResearch llama-2-13b-hf mirror. That exceeds the 10% threshold, so all
138 were checked. There are 24 wrong or unsupported values (17.39%):
12 numeric mismatches and 12 without their own run. All 24 belong to the
25 MODEL-116 leftovers. Granite's IFEval already matched at 72.1, but its
BBH, MuSR and MMLU-Pro did not. The other 114 IFEval values match their own
raw run to one decimal place.

## Full MATH

The three lab-reported full-MATH values move from `math_500` to the existing
`math` key. Anthropic's launch table gives 78.3 for the new Claude 3.5 Sonnet;
Meta's Llama 3.1 model card gives 73.8 for 405B Instruct, 0-shot CoT,
`final_em`; OpenAI's simple-evals table gives 76.6 for GPT-4o 2024-05-13.
OpenAI's footnote 6 explicitly reserves MATH-500 for o1 and later models.
Each source URL and read date appears in the corresponding card note and
fixture. Earlier MODEL-116 overlap notes are replaced so they no longer
claim the mislabeled keys remain in place.

## Corrections

Every source below was read on 2026-09-24. A null cites the frozen contents
inventory; the exact repository was also queried in the results dataset and
had no directory. Ministral has no repository on its card, so the community
`ministral/Ministral-3b-instruct` result cannot establish its evidence.

| Card | Field | Old | New | Source |
| --- | --- | ---: | ---: | --- |
| `01-ai/yi-1-5-34b-chat` | `ifeval` | 77.3 | 60.7 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-34B-Chat/results_2025-02-13T18-27-04.338360.json) |
| `01-ai/yi-1-5-34b-chat` | `bbh` | 48.2 | 60.8 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-34B-Chat/results_2025-02-13T18-27-04.338360.json) |
| `01-ai/yi-1-5-34b-chat` | `musr` | 18.2 | 42.8 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-34B-Chat/results_2025-02-13T18-27-04.338360.json) |
| `01-ai/yi-1-5-34b-chat` | `mmlu_pro` | 52.8 | 45.2 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-34B-Chat/results_2025-02-13T18-27-04.338360.json) |
| `01-ai/yi-1-5-34b` | `ifeval` | 77.3 | 28.4 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-34B/results_2025-02-13T18-27-04.338360.json) |
| `01-ai/yi-1-5-34b` | `bbh` | 48.2 | 59.8 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-34B/results_2025-02-13T18-27-04.338360.json) |
| `01-ai/yi-1-5-34b` | `musr` | 18.2 | 42.4 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-34B/results_2025-02-13T18-27-04.338360.json) |
| `01-ai/yi-1-5-34b` | `mmlu_pro` | 52.8 | 46.7 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/01-ai/Yi-1.5-34B/results_2025-02-13T18-27-04.338360.json) |
| `01-ai/yi-6b-chat-4bits` | `ifeval` | 34.0 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `01-ai/yi-6b-chat-4bits` | `bbh` | 41.3 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `01-ai/yi-6b-chat-4bits` | `musr` | 36.9 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `01-ai/yi-6b-chat-4bits` | `mmlu_pro` | 30.6 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `allen-ai/olmo-2-1124-7b` | `ifeval` | 72.4 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `allen-ai/olmo-2-1124-7b` | `bbh` | 40.2 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `allen-ai/olmo-2-1124-7b` | `musr` | 35.1 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `allen-ai/olmo-2-1124-7b` | `mmlu_pro` | 26.7 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `cerebras/llama3-1-8b` | `ifeval` | 33.2 | 49.2 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/meta-llama/Llama-3.1-8B-Instruct/results_2025-02-13T18-27-04.338360.json) |
| `cerebras/llama3-1-8b` | `bbh` | 47.8 | 50.9 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/meta-llama/Llama-3.1-8B-Instruct/results_2025-02-13T18-27-04.338360.json) |
| `cerebras/llama3-1-8b` | `musr` | 39.3 | 39.7 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/meta-llama/Llama-3.1-8B-Instruct/results_2025-02-13T18-27-04.338360.json) |
| `cerebras/llama3-1-8b` | `mmlu_pro` | 31.6 | 38.0 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/meta-llama/Llama-3.1-8B-Instruct/results_2025-02-13T18-27-04.338360.json) |
| `google/gemma-2-2b-it` | `ifeval` | 12.7 | 56.7 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/google/gemma-2-2b-it/results_2024-07-29T16-25-50.870458.json) |
| `google/gemma-2-2b-it` | `bbh` | 44.0 | 42.0 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/google/gemma-2-2b-it/results_2024-07-29T16-25-50.870458.json) |
| `google/gemma-2-2b-it` | `musr` | 42.4 | 39.3 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/google/gemma-2-2b-it/results_2024-07-29T16-25-50.870458.json) |
| `google/gemma-2-2b-it` | `mmlu_pro` | 27.2 | 25.5 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/google/gemma-2-2b-it/results_2024-07-29T16-25-50.870458.json) |
| `ibm/granite-3-1-8b-instruct` | `bbh` | 39.5 | 53.6 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/ibm-granite/granite-3.1-8b-instruct/results_2025-02-13T18-27-04.338360.json) |
| `ibm/granite-3-1-8b-instruct` | `musr` | 13.1 | 47.1 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/ibm-granite/granite-3.1-8b-instruct/results_2025-02-13T18-27-04.338360.json) |
| `ibm/granite-3-1-8b-instruct` | `mmlu_pro` | 43.5 | 35.4 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/ibm-granite/granite-3.1-8b-instruct/results_2025-02-13T18-27-04.338360.json) |
| `meta/llama-3-2-1b-instruct` | `ifeval` | 58.1 | 57.0 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/meta-llama/Llama-3.2-1B-Instruct/results_2025-02-13T18-27-04.338360.json) |
| `meta/llama-3-2-1b-instruct` | `bbh` | 34.8 | 35.0 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/meta-llama/Llama-3.2-1B-Instruct/results_2025-02-13T18-27-04.338360.json) |
| `meta/llama-3-2-1b-instruct` | `musr` | 32.0 | 33.3 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/meta-llama/Llama-3.2-1B-Instruct/results_2025-02-13T18-27-04.338360.json) |
| `meta/llama-3-2-1b-instruct` | `mmlu_pro` | 17.4 | 16.8 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/meta-llama/Llama-3.2-1B-Instruct/results_2025-02-13T18-27-04.338360.json) |
| `microsoft/phi-3-5-mini-instruct` | `ifeval` | 72.4 | 57.7 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/Phi-3.5-mini-instruct/results_2025-02-13T18-27-04.338360.json) |
| `microsoft/phi-3-5-mini-instruct` | `bbh` | 38.1 | 55.2 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/Phi-3.5-mini-instruct/results_2025-02-13T18-27-04.338360.json) |
| `microsoft/phi-3-5-mini-instruct` | `musr` | 11.2 | 40.2 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/Phi-3.5-mini-instruct/results_2025-02-13T18-27-04.338360.json) |
| `microsoft/phi-3-5-mini-instruct` | `mmlu_pro` | 42.3 | 39.6 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/Phi-3.5-mini-instruct/results_2025-02-13T18-27-04.338360.json) |
| `microsoft/phi-3-mini-4k-instruct` | `ifeval` | 54.4 | 56.1 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/Phi-3-mini-4k-instruct/results_2024-06-17T11-04-33.850464.json) |
| `microsoft/phi-3-mini-4k-instruct` | `bbh` | 55.0 | 56.8 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/Phi-3-mini-4k-instruct/results_2024-06-17T11-04-33.850464.json) |
| `microsoft/phi-3-mini-4k-instruct` | `musr` | 42.8 | 39.5 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/Phi-3-mini-4k-instruct/results_2024-06-17T11-04-33.850464.json) |
| `microsoft/phi-3-mini-4k-instruct` | `mmlu_pro` | 40.3 | 38.7 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/Phi-3-mini-4k-instruct/results_2024-06-17T11-04-33.850464.json) |
| `mistral/ministral-3b-latest` | `ifeval` | 13.6 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `mistral/ministral-3b-latest` | `bbh` | 31.9 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `mistral/ministral-3b-latest` | `musr` | 33.8 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `mistral/ministral-3b-latest` | `mmlu_pro` | 10.9 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `mistral/mixtral-8x22b-instruct-v0-1` | `ifeval` | 77.8 | 71.8 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-06-26T15-18-07.434042.json) |
| `mistral/mixtral-8x22b-instruct-v0-1` | `bbh` | 48.5 | 61.2 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-06-26T15-18-07.434042.json) |
| `mistral/mixtral-8x22b-instruct-v0-1` | `musr` | 18.5 | 43.1 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-06-26T15-18-07.434042.json) |
| `mistral/mixtral-8x22b-instruct-v0-1` | `mmlu_pro` | 52.3 | 44.8 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x22B-Instruct-v0.1/results_2024-06-26T15-18-07.434042.json) |
| `mistral/mixtral-8x7b-instruct-v0-1` | `ifeval` | 69.5 | 56.0 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2025-02-13T18-27-04.338360.json) |
| `mistral/mixtral-8x7b-instruct-v0-1` | `bbh` | 36.8 | 49.6 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2025-02-13T18-27-04.338360.json) |
| `mistral/mixtral-8x7b-instruct-v0-1` | `musr` | 11.8 | 42.0 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2025-02-13T18-27-04.338360.json) |
| `mistral/mixtral-8x7b-instruct-v0-1` | `mmlu_pro` | 40.5 | 36.9 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x7B-Instruct-v0.1/results_2025-02-13T18-27-04.338360.json) |
| `mistral/mixtral-8x7b-v0-1` | `ifeval` | 69.5 | 24.2 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x7B-v0.1/results_2025-02-13T18-27-04.338360.json) |
| `mistral/mixtral-8x7b-v0-1` | `bbh` | 36.8 | 50.9 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x7B-v0.1/results_2025-02-13T18-27-04.338360.json) |
| `mistral/mixtral-8x7b-v0-1` | `musr` | 11.8 | 43.2 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x7B-v0.1/results_2025-02-13T18-27-04.338360.json) |
| `mistral/mixtral-8x7b-v0-1` | `mmlu_pro` | 40.5 | 38.5 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x7B-v0.1/results_2025-02-13T18-27-04.338360.json) |
| `mistral/open-mixtral-8x22b` | `ifeval` | 77.8 | 25.8 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x22B-v0.1/results_2025-02-13T18-27-04.338360.json) |
| `mistral/open-mixtral-8x22b` | `bbh` | 48.5 | 62.4 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x22B-v0.1/results_2025-02-13T18-27-04.338360.json) |
| `mistral/open-mixtral-8x22b` | `musr` | 18.5 | 40.4 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x22B-v0.1/results_2025-02-13T18-27-04.338360.json) |
| `mistral/open-mixtral-8x22b` | `mmlu_pro` | 52.3 | 46.4 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x22B-v0.1/results_2025-02-13T18-27-04.338360.json) |
| `mistral/open-mixtral-8x7b` | `ifeval` | 69.5 | 24.2 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x7B-v0.1/results_2025-02-13T18-27-04.338360.json) |
| `mistral/open-mixtral-8x7b` | `bbh` | 36.8 | 50.9 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x7B-v0.1/results_2025-02-13T18-27-04.338360.json) |
| `mistral/open-mixtral-8x7b` | `musr` | 11.8 | 43.2 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x7B-v0.1/results_2025-02-13T18-27-04.338360.json) |
| `mistral/open-mixtral-8x7b` | `mmlu_pro` | 40.5 | 38.5 | [OLL run](https://huggingface.co/datasets/open-llm-leaderboard/results/blob/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x7B-v0.1/results_2025-02-13T18-27-04.338360.json) |
| `nous-research/llama-2-13b-hf` | `ifeval` | 24.8 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/llama-2-13b-hf` | `bbh` | 41.3 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/llama-2-13b-hf` | `musr` | 35.4 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/llama-2-13b-hf` | `mmlu_pro` | 23.8 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/llama-2-7b-chat-hf` | `ifeval` | 39.9 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/llama-2-7b-chat-hf` | `bbh` | 31.1 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/llama-2-7b-chat-hf` | `musr` | 36.8 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/llama-2-7b-chat-hf` | `mmlu_pro` | 16.9 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/llama-2-7b-hf` | `ifeval` | 25.2 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/llama-2-7b-hf` | `bbh` | 35.0 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/llama-2-7b-hf` | `musr` | 37.0 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/llama-2-7b-hf` | `mmlu_pro` | 18.6 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/llama-3-2-1b` | `ifeval` | 14.8 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/llama-3-2-1b` | `bbh` | 31.1 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/llama-3-2-1b` | `musr` | 34.5 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/llama-3-2-1b` | `mmlu_pro` | 12.0 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/meta-llama-3-70b-instruct` | `ifeval` | 81.0 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/meta-llama-3-70b-instruct` | `bbh` | 65.5 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/meta-llama-3-70b-instruct` | `musr` | 41.5 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/meta-llama-3-70b-instruct` | `mmlu_pro` | 52.1 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/meta-llama-3-8b-instruct` | `ifeval` | 47.8 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/meta-llama-3-8b-instruct` | `bbh` | 49.1 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/meta-llama-3-8b-instruct` | `musr` | 38.1 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/meta-llama-3-8b-instruct` | `mmlu_pro` | 35.9 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/meta-llama-3-8b` | `ifeval` | 14.6 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/meta-llama-3-8b` | `bbh` | 46.0 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/meta-llama-3-8b` | `musr` | 36.1 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `nous-research/meta-llama-3-8b` | `mmlu_pro` | 32.1 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `qwen/qwen2-5-coder-7b-instruct-gptq-int4` | `ifeval` | 34.5 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `qwen/qwen2-5-coder-7b-instruct-gptq-int4` | `bbh` | 48.6 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `qwen/qwen2-5-coder-7b-instruct-gptq-int4` | `musr` | 34.5 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `qwen/qwen2-5-coder-7b-instruct-gptq-int4` | `mmlu_pro` | 36.8 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `qwen/qwen2-5-math-1-5b` | `ifeval` | 18.6 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `qwen/qwen2-5-math-1-5b` | `bbh` | 37.5 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `qwen/qwen2-5-math-1-5b` | `musr` | 36.9 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `qwen/qwen2-5-math-1-5b` | `mmlu_pro` | 18.0 | null | [OLL inventory](https://huggingface.co/datasets/open-llm-leaderboard/contents/blob/9c09a7cae43334062a82cb164f2ef255013dafa2/data/train-00000-of-00001.parquet) |
| `anthropic/claude-3-5-sonnet-20241022` | `math_500` → `math` | 78.3 | 78.3 | [Lab report](https://www.anthropic.com/news/3-5-models-and-computer-use) |
| `meta/llama-3-1-405b-instruct` | `math_500` → `math` | 73.8 | 73.8 | [Lab report](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/MODEL_CARD.md) |
| `openai/gpt-4o-2024-05-13` | `math_500` → `math` | 76.6 | 76.6 | [Lab report](https://github.com/openai/simple-evals/blob/main/README.md) |
