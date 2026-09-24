# Saturation: Fisher information per observation, median vs. frontier

theta is the item's own domain blend. `median` and `frontier` are the 50th and 97th
percentiles of that blend over the models observed on the item. A saturated
benchmark keeps information at the median and loses it at the frontier.

## View: sourced

| item | models | best observed | lambda | tau (pp) | info at median | info at frontier | frontier / median |
|---|---:|---:|---:|---:|---:|---:|---:|
| mmlu_pro | 13 | 87.5 | 1.13 | 4.0 | 27.92 | 5.62 | 0.20 |
| gpqa_diamond | 15 | 96.0 | 1.17 | 3.1 | 20.70 | 6.24 | 0.30 |
| swe_bench_verified | 9 | 96.0 | 1.21 | 3.7 | 49.86 | 15.73 | 0.32 |
| bbh | 8 | 55.3 | 0.68 | 3.7 | 11.94 | 4.63 | 0.39 |
| ifeval | 9 | 85.0 | 0.69 | 8.2 | 2.93 | 1.26 | 0.43 |
| musr | 8 | 43.9 | 0.58 | 3.7 | 10.42 | 5.60 | 0.54 |

## View: flat

| item | models | best observed | lambda | tau (pp) | info at median | info at frontier | frontier / median |
|---|---:|---:|---:|---:|---:|---:|---:|
| math_500 | 171 | 97.3 | 2.70 | 1.8 | 426.84 | 1.73 | 0.00 |
| gsm8k | 84 | 97.3 | 1.78 | 7.8 | 4.53 | 0.04 | 0.01 |
| ifeval | 167 | 92.0 | 1.44 | 7.3 | 10.12 | 0.39 | 0.04 |
| medqa | 23 | 96.5 | 1.43 | 3.7 | 34.91 | 1.90 | 0.05 |
| mgsm | 22 | 92.3 | 1.31 | 2.9 | 26.76 | 1.86 | 0.07 |
| mmlu_pro | 171 | 87.5 | 1.52 | 1.8 | 282.27 | 24.04 | 0.09 |
| humaneval | 42 | 93.5 | 1.18 | 2.9 | 19.46 | 1.69 | 0.09 |
| mmlu_high_school_government_and_politics | 36 | 97.9 | 0.98 | 2.9 | 2.88 | 0.27 | 0.09 |
| toxigen | 22 | 97.5 | 0.93 | 2.5 | 6.95 | 0.83 | 0.12 |
| mmlu_high_school_psychology | 36 | 92.1 | 0.85 | 3.0 | 4.81 | 0.67 | 0.14 |
| hellaswag | 36 | 87.3 | 0.81 | 3.7 | 3.69 | 0.53 | 0.14 |
| mmlu_high_school_us_history | 36 | 91.2 | 0.91 | 3.0 | 5.30 | 0.78 | 0.15 |
| mmlu_high_school_microeconomics | 36 | 88.7 | 0.93 | 3.6 | 6.97 | 1.11 | 0.16 |
| mmlu_marketing | 36 | 95.3 | 0.77 | 3.2 | 1.83 | 0.30 | 0.16 |
| mmlu_miscellaneous | 36 | 91.1 | 0.81 | 2.9 | 6.60 | 1.06 | 0.16 |
| mmlu_high_school_geography | 36 | 93.4 | 0.86 | 3.2 | 4.34 | 0.70 | 0.16 |
| mmlu_high_school_biology | 36 | 89.7 | 0.88 | 3.1 | 6.86 | 1.11 | 0.16 |
| mmlu_high_school_world_history | 36 | 90.7 | 0.84 | 3.6 | 3.79 | 0.62 | 0.16 |
| mmlu_world_religions | 36 | 90.6 | 0.86 | 3.5 | 4.12 | 0.71 | 0.17 |
| helm_safety | 22 | 95.2 | 0.80 | 2.5 | 7.38 | 1.31 | 0.18 |
| mmlu_college_biology | 36 | 90.3 | 0.95 | 3.0 | 7.38 | 1.35 | 0.18 |
| mmlu_sociology | 36 | 89.1 | 0.79 | 3.3 | 3.49 | 0.66 | 0.19 |
| winogrande | 46 | 84.1 | 0.86 | 3.1 | 6.63 | 1.28 | 0.19 |
| bbq | 17 | 86.5 | 0.71 | 2.7 | 12.71 | 2.61 | 0.21 |
| multipl_e_python | 8 | 92.5 | 0.69 | 3.2 | 5.30 | 1.12 | 0.21 |
| mmlu_us_foreign_policy | 36 | 93.0 | 0.74 | 3.0 | 1.95 | 0.44 | 0.23 |
| mmlu_prehistory | 36 | 88.9 | 0.83 | 3.2 | 8.80 | 2.01 | 0.23 |
| arc_challenge | 36 | 71.1 | 0.85 | 3.3 | 16.55 | 4.00 | 0.24 |
| docvqa | 26 | 96.5 | 0.58 | 3.1 | 2.82 | 0.70 | 0.25 |
| mmlu_professional_psychology | 36 | 82.7 | 0.83 | 2.9 | 14.36 | 3.58 | 0.25 |
| multipl_e_java | 8 | 88.5 | 0.65 | 3.2 | 6.11 | 1.55 | 0.25 |
| mmlu_management | 36 | 92.2 | 0.73 | 3.4 | 2.55 | 0.65 | 0.26 |
| mmlu_high_school_european_history | 36 | 88.5 | 0.77 | 3.0 | 5.09 | 1.31 | 0.26 |
| multipl_e_javascript | 8 | 88.2 | 0.67 | 3.2 | 6.98 | 1.80 | 0.26 |
| live_code_bench | 37 | 91.7 | 1.27 | 11.9 | 6.55 | 1.72 | 0.26 |
| mmlu_professional_medicine | 36 | 84.9 | 0.81 | 4.6 | 5.90 | 1.57 | 0.27 |
| mmlu_logical_fallacies | 36 | 88.3 | 0.78 | 3.0 | 5.53 | 1.48 | 0.27 |
| multipl_e_typescript | 8 | 87.1 | 0.66 | 3.2 | 7.10 | 1.92 | 0.27 |
| mmlu_medical_genetics | 36 | 88.0 | 0.81 | 3.0 | 4.65 | 1.29 | 0.28 |
| mmlu_human_sexuality | 36 | 89.3 | 0.76 | 3.2 | 4.42 | 1.27 | 0.29 |
| mmlu_high_school_macroeconomics | 36 | 83.6 | 0.82 | 3.0 | 12.18 | 3.50 | 0.29 |
| multipl_e | 8 | 85.7 | 0.65 | 3.2 | 7.64 | 2.19 | 0.29 |
| multipl_e_csharp | 26 | 87.8 | 0.74 | 2.3 | 16.17 | 4.77 | 0.29 |
| multipl_e_cpp | 8 | 85.1 | 0.65 | 3.2 | 7.80 | 2.30 | 0.30 |
| ai2d | 21 | 95.2 | 0.52 | 3.8 | 2.03 | 0.60 | 0.30 |
| mmlu_international_law | 36 | 91.7 | 0.68 | 3.1 | 2.79 | 0.84 | 0.30 |
| mmlu_astronomy | 39 | 89.5 | 0.80 | 3.7 | 5.85 | 1.77 | 0.30 |
| mmlu_conceptual_physics | 36 | 84.7 | 0.89 | 3.3 | 11.61 | 3.52 | 0.30 |
| mmlu_nutrition | 36 | 84.6 | 0.70 | 2.9 | 7.04 | 2.22 | 0.32 |
| mmlu_human_aging | 36 | 82.5 | 0.74 | 3.7 | 5.95 | 1.90 | 0.32 |
| mmlu_moral_disputes | 36 | 83.5 | 0.69 | 2.9 | 7.75 | 2.64 | 0.34 |
| multipl_e_go | 8 | 82.1 | 0.62 | 3.2 | 8.27 | 2.84 | 0.34 |
| mmlu_security_studies | 36 | 84.1 | 0.66 | 3.2 | 5.30 | 1.83 | 0.35 |
| multipl_e_php | 26 | 85.1 | 0.69 | 2.3 | 15.66 | 5.48 | 0.35 |
| mmlu_philosophy | 36 | 82.0 | 0.68 | 2.9 | 7.20 | 2.57 | 0.36 |
| mmlu_clinical_knowledge | 39 | 86.2 | 0.69 | 2.9 | 7.28 | 2.67 | 0.37 |
| mmlu_high_school_computer_science | 36 | 87.0 | 0.70 | 3.9 | 3.27 | 1.21 | 0.37 |
| multipl_e_kotlin | 26 | 82.1 | 0.77 | 2.3 | 22.83 | 8.46 | 0.37 |
| multipl_e_rust | 8 | 76.2 | 0.67 | 3.3 | 11.75 | 4.41 | 0.37 |
| swe_bench_verified | 28 | 96.0 | 1.20 | 4.5 | 34.23 | 12.99 | 0.38 |
| mmlu_jurisprudence | 39 | 89.8 | 0.64 | 4.3 | 2.48 | 0.95 | 0.38 |
| mmlu_moral_scenarios | 36 | 71.1 | 1.18 | 4.2 | 23.74 | 9.56 | 0.40 |
| mteb_pair_classification | 68 | 87.0 | 0.68 | 1.6 | 5.44 | 2.24 | 0.41 |
| chartqa | 24 | 90.0 | 0.47 | 4.1 | 2.21 | 0.93 | 0.42 |
| mmlu_computer_security | 36 | 86.0 | 0.59 | 3.5 | 2.37 | 1.01 | 0.43 |
| miracl | 68 | 67.8 | 1.41 | 1.6 | 44.75 | 19.91 | 0.45 |
| multipl_e_ruby | 24 | 77.5 | 0.77 | 2.4 | 24.85 | 11.11 | 0.45 |
| mteb_sts | 68 | 85.5 | 0.66 | 1.6 | 5.88 | 2.64 | 0.45 |
| gpqa_diamond | 183 | 96.0 | 2.02 | 1.3 | 76.06 | 34.85 | 0.46 |
| mmlu_elementary_mathematics | 36 | 74.3 | 0.96 | 3.8 | 15.73 | 7.35 | 0.47 |
| aider_polyglot | 18 | 72.5 | 1.01 | 12.6 | 3.62 | 1.74 | 0.48 |
| multipl_e_swift | 25 | 75.8 | 0.70 | 2.4 | 20.98 | 10.51 | 0.50 |
| mmlu_college_medicine | 36 | 75.1 | 0.68 | 3.0 | 6.69 | 3.43 | 0.51 |
| mmlu_business_ethics | 39 | 82.0 | 0.62 | 3.1 | 3.71 | 1.97 | 0.53 |
| mmlu_high_school_statistics | 36 | 72.7 | 0.77 | 3.5 | 9.12 | 4.85 | 0.53 |
| mteb_retrieval | 79 | 67.2 | 0.94 | 1.5 | 19.63 | 10.63 | 0.54 |
| mmmu | 27 | 73.4 | 0.55 | 3.1 | 16.07 | 8.93 | 0.56 |
| mteb_overall | 79 | 69.5 | 0.70 | 1.5 | 27.33 | 15.87 | 0.58 |
| mteb_classification | 79 | 73.5 | 0.65 | 1.5 | 8.57 | 5.03 | 0.59 |
| multipl_e_scala | 26 | 71.8 | 0.70 | 2.3 | 21.64 | 12.70 | 0.59 |
| mmlu_anatomy | 36 | 75.6 | 0.64 | 3.4 | 4.92 | 2.92 | 0.59 |
| mmlu_electrical_engineering | 36 | 80.7 | 0.58 | 3.3 | 4.19 | 2.50 | 0.60 |
| multipl_e_julia | 22 | 69.8 | 0.66 | 2.5 | 18.56 | 11.28 | 0.61 |
| multipl_e_r | 21 | 67.5 | 0.69 | 2.5 | 20.42 | 13.23 | 0.65 |
| mmlu_public_relations | 36 | 76.4 | 0.50 | 3.1 | 2.62 | 1.71 | 0.65 |
| mmlu_professional_law | 39 | 77.5 | 0.78 | 4.1 | 11.42 | 7.46 | 0.65 |
| bbh | 139 | 66.3 | 0.48 | 3.8 | 9.00 | 6.01 | 0.67 |
| mathvista | 25 | 73.7 | 0.63 | 4.5 | 8.07 | 5.72 | 0.71 |
| mmlu_high_school_chemistry | 36 | 70.9 | 0.65 | 3.1 | 6.99 | 5.08 | 0.73 |
| mteb_reranking | 68 | 65.1 | 0.64 | 1.6 | 9.16 | 6.76 | 0.74 |
| multipl_e_lua | 25 | 65.2 | 0.60 | 2.4 | 15.85 | 11.84 | 0.75 |
| mmlu_professional_accounting | 39 | 71.8 | 0.70 | 2.8 | 10.62 | 8.16 | 0.77 |
| mmlu_econometrics | 36 | 64.9 | 0.76 | 3.5 | 6.09 | 4.82 | 0.79 |
| beir | 55 | 58.5 | 0.66 | 1.8 | 9.57 | 7.60 | 0.79 |
| mmlu_formal_logic | 36 | 67.5 | 0.79 | 3.6 | 6.87 | 5.47 | 0.80 |
| multipl_e_perl | 22 | 62.1 | 0.67 | 2.5 | 19.11 | 15.31 | 0.80 |
| mmlu_college_computer_science | 36 | 72.0 | 0.62 | 3.6 | 3.76 | 3.02 | 0.80 |
| terminal_bench_2 | 10 | 82.0 | 0.72 | 6.1 | 4.96 | 3.98 | 0.80 |
| truthfulqa | 36 | 68.3 | 0.28 | 4.7 | 1.90 | 1.57 | 0.83 |
| mteb_clustering | 79 | 53.8 | 0.70 | 1.5 | 11.17 | 9.62 | 0.86 |
| mmlu_machine_learning | 36 | 61.6 | 0.57 | 3.5 | 3.23 | 3.20 | 0.99 |
| musr | 139 | 48.3 | 0.02 | 8.4 | 0.00 | 0.00 | 1.02 |
| mmlu_virology | 36 | 58.4 | 0.43 | 3.0 | 2.59 | 2.76 | 1.07 |
| mmlu_college_physics | 36 | 59.8 | 0.83 | 3.8 | 5.21 | 6.01 | 1.15 |
| mmlu_college_chemistry | 36 | 59.0 | 0.57 | 3.1 | 2.96 | 3.49 | 1.18 |
| mteb_summarization | 68 | 31.5 | 0.40 | 1.6 | 2.94 | 3.57 | 1.21 |
| mmlu_high_school_physics | 36 | 55.6 | 0.72 | 2.9 | 5.76 | 7.68 | 1.34 |
| mmlu_global_facts | 36 | 57.0 | 0.70 | 3.3 | 3.42 | 5.06 | 1.48 |
| mmlu_college_mathematics | 36 | 59.0 | 0.71 | 3.8 | 3.19 | 4.82 | 1.51 |
| mmlu_abstract_algebra | 36 | 56.0 | 0.79 | 3.2 | 3.92 | 6.61 | 1.69 |
| mmlu_high_school_mathematics | 36 | 51.9 | 0.68 | 3.4 | 4.75 | 8.08 | 1.70 |
| hle | 8 | 64.4 | 0.94 | 4.0 | 9.31 | 31.04 | 3.33 |
| alpaca_eval | 16 | 55.0 | 0.67 | 10.9 | 0.00 | 0.01 | 6.15 |
