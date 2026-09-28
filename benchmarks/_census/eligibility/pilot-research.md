# Benchmark eligibility pilot research

Research date: **2026-09-08**. Freshness window: **2026-07-10 through 2026-09-08** (60 days inclusive, using calendar-date arithmetic). “Published” means the date shown by the source; an execution/run date is recorded only when the source exposes one. An undated current leaderboard is not treated as proof of a fresh result.

This is a bounded four-cluster pilot. It records source identity and eligibility evidence; it does not claim that an aggregate index is a substitute for the benchmark’s own result record.

## Ledger

| Cluster / candidate identity | Source and protocol evidence | Dated attributable results | Frontier / open coverage | Pilot status and reason |
|---|---|---|---|---|
| **LiveBench latest release** | Official [livebench.ai leaderboard](https://livebench.ai/) shows release **2026-06-25**, 23 objective tasks across seven categories, refreshed every six months, with an Open weights filter. Official [GitHub README](https://github.com/LiveBench/LiveBench) documents selecting `--livebench-release-option`; official [changelog](https://github.com/LiveBench/LiveBench/blob/main/changelog.md) records dated refreshes and says the benchmark evaluates closed and open-weight models. | The release date **2026-06-25** is outside the 2026-07-10–09-08 window. The current page exposes exact model rows, but no per-result publication/run date within the window; these rows cannot qualify as fresh evidence. | The UI documents an Open weights filter, but the inspected extract did not expose a named open-weight row and score. | **Unverified for active pilot eligibility.** Retain the release/version identity and do not call the undated current rows fresh. |
| **OpenBookQA vs `obqa`** | Official [allenai/OpenBookQA README](https://github.com/allenai/OpenBookQA/blob/main/README.md) identifies the EMNLP-2018 dataset/model code and points to an official leaderboard. The repo’s baseline description says results are average accuracy across five seeds plus best dev run, but the inspected primary page does not expose a dated comparison-results table. | The EMNLP-2018 paper/date establishes historical identity only; it is outside the freshness window and is not an attributable old model-comparison result for this gate. | No current paired frontier/open result established. The inspected README does not establish `obqa` as a canonical benchmark alias; retain it only as an observed spelling pending official harness/citation mapping. | **Unverified for active pilot eligibility.** Historical context may be retained, but do not classify as accepted historical comparison evidence from the paper date alone. |
| **OpenML_benchmark vs OpenML_benchmarks** | Official [OpenML benchmarking docs](https://docs.openml.org/benchmark/) describe benchmark suites, standardized tasks/splits, APIs, and shared runs. The official [OpenML docs](https://docs.openml.org/) describe the platform broadly. These are platform/docs identities, not one LLM leaderboard. | No exact current frontier or open-model result with a source date was found. Docs page metadata is old/undated relative to the pilot and does not establish a recent result. | No attributable frontier/open model pair in the inspected official sources. Names appear to be aliases or generic repository labels, not distinct benchmark identities. | **Unverified alias/platform cluster.** Do not count as a canonical model benchmark until a specific OpenML suite/task, dated run, model ID, metric, and result source are supplied. |
| **SWE-Together** | Official [SWE-Together site](https://togetherbench.com/) describes **109 tasks**, `opencode` harness, **k=2**, pass@1/pass², judge, correction, tokens, and minutes. Official [arXiv record](https://arxiv.org/abs/2606.29957) is dated **2026-06-29** and describes 109 repository-level tasks reconstructed from 11,260 sessions. | Site exposes exact model IDs/results and run dates, but all inspected runs are outside the window: `claude-opus-4.8` **52% pass@1** on **2026-06-17**; `gpt-5.5` **48%** on **2026-06-28**; `claude-opus-4.6` **46%** on **2026-06-08**; `glm-5.2` **42%** on **2026-06-17**; `glm-5.1` **34%** on **2026-06-08**; `deepseek-v4-pro` **29%** on **2026-06-08**; `minimax-2.7` **24%** on **2026-06-08**. | The site lists frontier and additional model IDs, but no run inside the freshness window was found and the site does not itself label the latter models open weights. | **Unverified for active pilot eligibility.** Retain exact run dates, harness `opencode`, and `k=2`; June runs cannot qualify the current window. |

## Interpretation rules applied

* A source publication/release date and an evaluation execution date are separate fields. Where only publication/release is known, `run_date` remains unknown.
* “Open” is recorded only when the primary source labels a model as open/open-weight or supplies a model-native source establishing that fact. A model name alone is insufficient.
* Historical status requires a valid dated old comparison result, not merely a benchmark paper/release date. The inspected OpenBookQA material supplies identity context but no such comparison result, so it remains `unverified`. Missing evidence is `unverified`, not historical.

## Provisional vs accepted gate

This file is provisional research for independent review. At this pass, LiveBench, OpenBookQA, OpenML, and SWE-Together remain unverified for the active 2026-07-10–09-08 gate because the inspected evidence lacks a qualifying fresh dated frontier/open comparison (or, for SWE-Together, the exact runs are outside the window).

## Visited primary URLs (all accessed 2026-09-08)

1. https://livebench.ai/
2. https://github.com/LiveBench/LiveBench
3. https://github.com/LiveBench/LiveBench/blob/main/changelog.md
4. https://github.com/allenai/OpenBookQA/blob/main/README.md
5. https://docs.openml.org/benchmark/
6. https://docs.openml.org/
7. https://togetherbench.com/
8. https://arxiv.org/abs/2606.29957
