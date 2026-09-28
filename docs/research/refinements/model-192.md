# MODEL-192 source and coverage report

Read on 2026-09-28. The machine-readable companion is [`model-192-coverage.yaml`](model-192-coverage.yaml).

## Finding

The permitted sources contain no per-language coding evidence for an exact premier-set model identity. Finance Benchmark v2 contains direct finance evidence for eight premier models. The direct legal sources contain none.

I collected the eight finance rows. The deterministic second key verified all eight against a retained projection of the public leaderboard. I did not collect coding or legal values. A null beats an identity inference.

## Per-language coding coverage before collection

The language columns below apply to every premier model named in the indicated row.

| Premier model coverage | C | C++ | Go | Java | JavaScript | TypeScript | PHP | Ruby | Rust | Python |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `anthropic/claude-opus-4-6` | prohibited | prohibited | prohibited | prohibited | prohibited | prohibited | prohibited | prohibited | prohibited | none |
| All other 31 premier models | none | none | none | none | none | none | none | none | none | none |

"Prohibited" means the official SWE-bench Multilingual result exists and its per-instance records could be grouped by repository language, but ModelSpec cannot reuse it. The official result repository has no licence, while the official leaderboard site uses CC BY-NC 4.0. ModelSpec has paid decision paths, so non-commercial terms do not permit catalogue ingestion.

The other candidate sources had no exact lineup match:

- [Multi-SWE-bench results](https://github.com/multi-swe-bench/experiments) are Apache-2.0 and split by language.
- [Aider Polyglot](https://github.com/Aider-AI/aider/blob/main/aider/website/_data/polyglot_leaderboard.yml) is Apache-2.0, but its official table publishes aggregate values rather than per-language values.
- [MultiPL-E](https://github.com/nuprl/MultiPL-E) permits redistribution under its modified BSD licence and forbids model-training use. Its published models do not match the premier set.

## Direct finance and legal coverage

| Benchmark | Terms | Exact premier matches | Disposition |
| --- | --- | ---: | --- |
| [Finance Benchmark v2](https://finbenchmark.ai/) | [MIT](https://github.com/gaschwanden/finbenchmark/blob/main/LICENSE) | 8 | Collected and verified |
| [FinanceBench](https://github.com/patronus-ai/financebench) | No root licence found | 0 | Not collected |
| [LegalBench](https://github.com/HazyResearch/legalbench) | Licence differs by task | 0 | Not collected |
| [TW-LegalBench](https://github.com/feiyuehchen/TW-LegalBench) | [CC BY-SA 4.0](https://github.com/feiyuehchen/TW-LegalBench/blob/main/LICENSE-DATA) | 0 | Not collected |

Finance Benchmark v2 directly tests finance workflows, including quantitative pricing, credit underwriting, banking regulation, derivatives, portfolio management, and corporate finance. Its exact premier matches are Claude Fable 5, Claude Opus 4.6, Claude Opus 4.7, DeepSeek V4 Pro, Gemini 3.5 Flash, Kimi K3, GPT-5.4, and GPT-5.6 Sol.

TW-LegalBench publishes results for GPT-5 and GPT-5.2. Neither identity is in the premier set. LegalBench's original results also predate the current lineup.

## Refinement registry dependency

PR #322, which adds `registry/refinements.yaml`, remained open during this work. I did not copy its draft schema or add an incompatible parallel tag. After #322 merges, `finance_benchmark_v2` should receive direct refinement tags for the workflow families its task categories actually isolate. The aggregate row should remain unrefined because it combines those categories.

## Card changes

All values are Finance Benchmark v2 `pass_at_1`, in percent:

| Card | Old | New |
| --- | ---: | ---: |
| `models/anthropic/claude-fable-5.md` | null | 90.411 |
| `models/anthropic/claude-opus-4-6.md` | null | 86.3014 |
| `models/anthropic/claude-opus-4-7.md` | null | 93.1507 |
| `models/deepseek/deepseek-v4-pro.md` | null | 89.0411 |
| `models/google/gemini-3-5-flash.md` | null | 83.5616 |
| `models/moonshot/kimi-k3.md` | null | 89.0411 |
| `models/openai/gpt-5-4.md` | null | 63.0137 |
| `models/openai/gpt-5-6-sol.md` | null | 91.7808 |
