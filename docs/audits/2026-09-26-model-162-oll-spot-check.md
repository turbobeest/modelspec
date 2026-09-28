# MODEL-162 Open LLM Leaderboard evidence spot-check

Read on 2026-09-26 from the pinned Open LLM Leaderboard result files cited by
the sampled evidence. This audit checks the evidence migrated in #282. It does
not revisit the accepted licence analysis in MODEL-118.

## Method

- Population: the 2,856 rows marked `migrated` in
  [`model-118-oll-migration.csv`](model-118-oll-migration.csv).
- Seed: `16220260926`, used with Python's `random.Random`.
- Draw: sort candidate rows by card, benchmark ID and evidence ID; shuffle the
  19 card `family` strata; draw one row from every family, preferring a
  benchmark not already drawn and requiring a new card; then draw from the
  remaining rows until the sample reaches 30, requiring both a new card and a
  benchmark not already drawn.
- Coverage: 30 cards, all 19 families, and 26 benchmarks. Twenty rows use OLL
  v1 result files and 10 use OLL v2 result files.
- Verification: fetch every cited `resolve/<commit>/...` source URL over HTTP.
  Read the evaluated model identity and evaluation date from the result file,
  derive the benchmark value with the OLL v1 or v2 metric definition used by
  the migration, and compare it with the evidence row. Card values must equal
  the source values rounded to the card's one-decimal precision. Both
  `source_kind` and `measured_by` must be `independent_evaluator`.

`CSV row` is the physical line number in the migration CSV, including its
header. `Source value` is shown before rounding. A check mark means the model
identity, evaluation date, value and rounding, source URL, benchmark ID,
`source_kind`, and `measured_by` all matched.

## Sample

| CSV row | Model | Benchmark | Source URL | Card value | Source value | Match |
|---:|---|---|---|---:|---:|:---:|
| 53 | `01-ai/yi-1-5-34b-32k` | `mmlu_philosophy` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B-32K/results_2024-05-26T07-04-09.158901.json) | 80.4 | 80.38585209003215 | ✅ |
| 262 | `01-ai/yi-1-5-34b` | `mmlu_sociology` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-34B/results_2024-05-16T00-23-07.920103.json) | 87.1 | 87.06467661691542 | ✅ |
| 357 | `01-ai/yi-1-5-6b` | `mmlu_econometrics` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-6B/results_2024-05-30T17-21-52.581058.json) | 46.5 | 46.49122807017544 | ✅ |
| 448 | `01-ai/yi-1-5-9b-32k` | `mmlu_machine_learning` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-32K/results_2024-05-25T18-20-24.039645.json) | 50.9 | 50.89285714285714 | ✅ |
| 475 | `01-ai/yi-1-5-9b-chat-16k` | `gsm8k` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B-Chat-16K/results_2024-05-25T18-33-08.508160.json) | 59.7 | 59.66641394996209 | ✅ |
| 647 | `01-ai/yi-1-5-9b` | `mmlu_human_aging` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-1.5-9B/results_2024-05-16T10-35-34.857914.json) | 74.4 | 74.43946188340807 | ✅ |
| 697 | `01-ai/yi-34b-200k` | `mmlu_electrical_engineering` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/01-ai/Yi-34B-200K/results_2024-04-16T04-20-00.686323.json) | 77.2 | 77.24137931034483 | ✅ |
| 1048 | `ai21/jamba-v0-1` | `musr` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/ai21labs/Jamba-v0.1/results_2025-02-13T18-27-04.338360.json) | 35.9 | 35.90208333333334 | ✅ |
| 1080 | `allen-ai/olmo-1b-hf` | `mmlu_high_school_macroeconomics` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/allenai/OLMo-1B-hf/results_2024-04-23T06-24-47.411659.json) | 27.2 | 27.17948717948718 | ✅ |
| 1148 | `baichuan/baichuan-7b` | `winogrande` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/baichuan-inc/Baichuan-7B/results_2023-09-22T17-53-01.811068.json) | 66.8 | 66.77190213101815 | ✅ |
| 1268 | `deepseek/deepseek-coder-6-7b-base` | `mmlu_moral_disputes` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/deepseek-ai/deepseek-coder-6.7b-base/results_2024-04-02T21-41-57.054032.json) | 40.5 | 40.46242774566474 | ✅ |
| 1525 | `google/flan-t5-large` | `ifeval` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/google/flan-t5-large/results_2025-02-13T18-27-04.338360.json) | 22.0 | 22.009490374428736 | ✅ |
| 1611 | `google/gemma-2b-it` | `mmlu_jurisprudence` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/google/gemma-2b-it/results_2024-02-22T15-21-47.760131.json) | 46.3 | 46.2962962962963 | ✅ |
| 1805 | `ibm/granite-3-0-8b-instruct` | `mmlu_pro` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/ibm-granite/granite-3.0-8b-instruct/results_2025-02-13T18-27-04.338360.json) | 34.6 | 34.56615691489361 | ✅ |
| 2133 | `meta/meta-llama-3-8b` | `mmlu_high_school_microeconomics` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/meta-llama/Meta-Llama-3-8B/results_2024-05-28T19-40-23.721752.json) | 73.5 | 73.52941176470588 | ✅ |
| 2171 | `microsoft/dialogpt-medium` | `math_lvl5` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/microsoft/DialoGPT-medium/results_2025-02-13T18-27-04.338360.json) | 0.0 | 0.0 | ✅ |
| 2272 | `microsoft/phi-3-mini-128k-instruct` | `mmlu_high_school_chemistry` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/microsoft/Phi-3-mini-128k-instruct/results_2024-04-25T11-04-08.300273.json) | 60.1 | 60.09852216748769 | ✅ |
| 2399 | `mistral/mistral-7b-instruct-v0-1` | `gpqa_pooled` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mistral-7B-Instruct-v0.1/results_2025-02-13T18-27-04.338360.json) | 25.0 | 25.0 | ✅ |
| 2446 | `mistral/mistral-7b-instruct-v0-2` | `mmlu_human_sexuality` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/mistralai/Mistral-7B-Instruct-v0.2/results_2023-12-12T03-37-50.599841.json) | 74.0 | 74.04580152671755 | ✅ |
| 2753 | `mistral/open-mixtral-8x22b` | `bbh` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/mistralai/Mixtral-8x22B-v0.1/results_2025-02-13T18-27-04.338360.json) | 62.4 | 62.39807473187269 | ✅ |
| 2790 | `nous-research/hermes-2-pro-llama-3-8b` | `mmlu_high_school_geography` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Pro-Llama-3-8B/results_2024-05-02T09-00-48.637180.json) | 78.8 | 78.78787878787878 | ✅ |
| 2829 | `nous-research/hermes-2-theta-llama-3-8b` | `arc_challenge` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Hermes-2-Theta-Llama-3-8B/results_2024-05-27T00-35-30.762626.json) | 63.1 | 63.13993174061433 | ✅ |
| 3030 | `nous-research/meta-llama-3-8b-instruct` | `mmlu_security_studies` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Meta-Llama-3-8B-Instruct/results_2024-04-19T18-40-48.433302.json) | 73.9 | 73.87755102040816 | ✅ |
| 3155 | `nous-research/nous-hermes-2-mixtral-8x7b-dpo` | `mmlu_professional_law` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO/results_2024-01-22T17-09-50.643842.json) | 55.5 | 55.54106910039114 | ✅ |
| 3182 | `nous-research/nous-hermes-2-solar-10-7b` | `mmlu_college_mathematics` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/NousResearch/Nous-Hermes-2-SOLAR-10.7B/results_2024-01-04T13-44-46.879799.json) | 37.0 | 37.0 | ✅ |
| 3441 | `qwen/qwen2-5-0-5b-instruct` | `bbh` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/Qwen/Qwen2.5-0.5B-Instruct/results_2025-02-13T18-27-04.338360.json) | 33.2 | 33.219164295491375 | ✅ |
| 3502 | `rwkv/rwkv-raven-14b` | `gpqa_pooled` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/RWKV/rwkv-raven-14b/results_2025-02-13T18-27-04.338360.json) | 22.9 | 22.90268456375839 | ✅ |
| 3509 | `stability/stablelm-2-1-6b` | `ifeval` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/stabilityai/stablelm-2-1_6b/results_2025-02-13T18-27-04.338360.json) | 11.6 | 11.570521771122843 | ✅ |
| 3578 | `tii/falcon-40b` | `mmlu_elementary_mathematics` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/23474373f8874f9057d23b97e5a41e911d2721c5/tiiuae/falcon-40b/results_2023-11-27T10-24-56.579363.json) | 33.9 | 33.86243386243386 | ✅ |
| 3717 | `together/redpajama-incite-7b-chat` | `ifeval` | [pinned JSON](https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/aa81ecc38fdc5708254b833923368970efdf5ef5/togethercomputer/RedPajama-INCITE-7B-Chat/results_2025-02-13T18-27-04.338360.json) | 15.6 | 15.57977278066641 | ✅ |

## Verdict

All 30 sampled evidence rows match their pinned result files. The model
identities and evaluation dates match, every card value is the correct
one-decimal rounding of the source value, and both evaluator fields correctly
say `independent_evaluator`. The spot-check found no mismatch and requires no
card fix.
