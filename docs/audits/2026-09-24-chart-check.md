# Chart check, 2026-09-24 (MODEL-130 phase 1, round 3)

A bar was read off the publisher's page, then compared with the evidence rows on the cards. Cards were not edited. Nine pages, 48 charts, 39 transcribed, 9 left `needs_reading`. 851 bars.

Same-source evidence is compared first, for every role. Artificial Analysis bars are `evaluated`. A second harness of the same model and benchmark is `other_configuration` when one sibling matches the row. A different unit is `unit_differs`. A non-headline metric is `other_metric`. A bar with no catalogue page is `no_benchmark_page`.

| Class | Bars |
| --- | ---: |
| matched | 26 |
| other_configuration | 7 |
| mismatched | 0 |
| unit_differs | 2 |
| other_metric | 4 |
| no_benchmark_page | 298 |
| not_held | 491 |
| competitor_gap | 11 |
| competitor_unresolved | 12 |

The seven `other_configuration` bars are DeepSeek-V4.1-Flash on Terminal-Bench 2.1, same page as the card's 90.6. That row is DeepSeek Harness Minimal, and the 90.6 bar matches. The other scaffolds are Claude Code 88.0, Codex 84.1, OpenCode 85.0, Pi 86.1, mini-SWE 90.3, DSH Standard 85.8, and DSH PTC 85.8.

The two `unit_differs` bars are AA-Briefcase on the v4.2 article. The chart prints Elo. The card holds the index-normalised percent from that same article, `clamp((Elo − 500) / 2000)`. GPT-6 Astra is 1565 Elo and 53. GLM-5.3 is 1521 Elo and 51.

The four `other_metric` bars are AutomationBench-AA tasks completed (Astra 41.6, Fable 5.1 32.1, Opus 5 28.3) and the DeepSeek-V4.1-Flash HLE text-only subset at 39.1. Astra's AutomationBench-AA Score of 68.5 matches the card.

## Coverage

Headline subject bars with a catalogue id. Held means a same-source row exists, including a mismatch or another configuration. Uncatalogued benchmarks and non-headline metrics are counted separately.

| Model | Held / published | Matched |
| --- | ---: | ---: |
| openai/gpt-6-astra | 7/14 | 7 |
| openai/gpt-6-sol | 0/2 | 0 |
| openai/gpt-5-4 | 0/0 | 0 |
| openai/o3 | 0/0 | 0 |
| openai/o3-mini | 0/0 | 0 |
| openai/o4-mini | 0/0 | 0 |
| openai/gpt-4-1 | 0/0 | 0 |
| openai/gpt-4-1-mini | 0/0 | 0 |
| google/gemini-3-8-flash | 2/15 | 2 |
| google/gemini-2-5-pro | 0/0 | 0 |
| google/gemini-2-5-flash | 0/0 | 0 |
| deepseek/deepseek-flash | 19/20 | 12 |
| deepseek/deepseek-v3-2 | 0/0 | 0 |
| deepseek/deepseek-v3-2-exp | 1/11 | 1 |
| qwen/qwen3-235b-a22b | 0/21 | 0 |
| deepseek/deepseek-v3-1-terminus | 0/11 | 0 |
| deepseek/deepseek-v4-pro | 0/8 | 0 |
| deepseek/deepseek-v4-flash | 0/8 | 0 |
| google/gemini-3-7-flash | 0/15 | 0 |
| openai/gpt-5-6-sol | 0/12 | 0 |
| qwen/qwen3-32b | 0/7 | 0 |
| qwen/qwen3-30b-a3b | 0/6 | 0 |
| qwen/qwen3-4b | 0/6 | 0 |

Astra's seven matches are the evidence rows that cite `openai.com/index/gpt-6-astra/`: GPQA Diamond 96.0, Terminal-Bench 4.0 57.9, Terminal-Bench Science 64.6, BrowseComp 91.5, HLE with tools 57.2, ARC-AGI-2 95.0, AutomationBench 41.4.

Gemini 3.8 Flash matches the two rows that cite the model card: Terminal-bench 2.1 at 89.4 and CharXiv Reasoning at 86.2. The launch post repeats those tables under a different URL.

DeepSeek-V4.1-Flash (`deepseek/deepseek-flash`) holds 19 of 20 headline bars from the README. Twelve match, including Terminal-Bench 2.1 at 90.6. Seven are the other scaffolds above. ZeroBench-main at 49.0 has no row from that page. The HLE text-only 39.1 is `other_metric` and is outside this denominator.

DeepSeek-V3.2-Exp matches Terminal-bench 37.7, the only row the card cites from that README. Qwen3-235B-A22B's evidence cites the Artificial Analysis leaderboard and the arena dataset. The blog adds one catalogue bar, MultiIF 71.9, so the denominator is 21. GPT-6 Sol's evidence cites Zapier. The other subject rows in the table are publisher models on these pages whose cards do not cite the page.

## Mismatched bars

None. GDP.pdf all-pass on the v4.2 article matches the card rows from that URL. GPT-6 Astra (max) is 33.2. GLM-5.3 (max) is 11.8.

## Competitor gaps above 2 points

One gap. Claude Fable 5.1 on Terminal-Bench 4.0 is 52.0 in the v4.3 article (`https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-3`). The card holds 55.8 from the Anthropic system card (`https://www.anthropic.com/claude-fable-5-1-system-card`) and 57.88 from tbench.ai (`https://www.tbench.ai/leaderboard`). The gap versus the closer row is −3.8.

Eleven bars are `competitor_gap` in total. The other ten are within 2 points.

## Uncatalogued benchmarks

298 bars have `benchmark_id: null`. The count is how many times the label was printed, across pages.

| Benchmark as labelled | Bars |
| --- | ---: |
| DeepSWE v1.1 | 41 |
| Harvey Legal Agent Benchmark | 18 |
| Vals Finance Agent v2 | 18 |
| Gray Swan IPI | 16 |
| BioMysteryBench human-difficult | 12 |
| BioMysteryBench human-solvable | 12 |
| LABBench2 | 12 |
| LVBench | 12 |
| ExploitGym | 11 |
| Agent's Last Exam | 7 |
| NL2Repo | 7 |
| ArenaHard | 6 |
| CodeForces | 6 |
| FrontierCode extended | 6 |
| FrontierCode main | 6 |
| ProgramBench | 6 |
| SEC-Bench Pro | 6 |
| Agents' Last Exam | 5 |
| ARC-AGI-1 | 5 |
| BenchCAD | 5 |
| Codeforces | 5 |
| Coding Agent Index | 5 |
| Computer-use safety | 5 |
| FrontierMath Tier 4 | 5 |
| INCLUDE | 5 |
| BabyVision | 4 |
| Chartography | 4 |
| MathArena Apex | 4 |
| ARC-AGI-3 | 3 |
| ExploitBench | 3 |
| Real-world vulnerability discovery | 3 |
| SRE-Bench | 3 |
| BrowseComp-zh | 2 |
| Circumvention | 2 |
| Computer-use safety with AutoReview | 2 |
| ExploitBench June-August 2026 | 2 |
| ExploitGym honeypot | 2 |
| GeneBench Pro | 2 |
| Hallucination | 2 |
| HMMT 2025 | 2 |
| LifeSciBench | 2 |
| LVBench static | 2 |
| MedChemBench | 2 |
| OpenScore String Quartets | 2 |
| CVBench | 1 |
| Image to text safety | 1 |
| Impossible ExploitGym | 1 |
| Multilingual safety | 1 |
| RefCOCO-avg | 1 |
| Text to text safety | 1 |
| Tone | 1 |
| Unjustified refusals | 1 |

## Second reading

Reader B (claude-opus, 2026-09-24) is recorded on 35 charts. The 13 OpenAI charts still have one reading: both OpenAI pages returned 403, so those sources are `unpaired_source` and nothing from them was written onto the fixtures. No `only_b` bar was added to a fixture. Paired printed values agree, so no bar is marked `disputed`. The class counts above are unchanged from round 2.

A page source is paired with the HTML and prose charts. Image charts are paired from the image file, through the sha256 in the phase 1 manifest. Two items pair when the model, the benchmark, and the setting match after normalisation. A model and benchmark that appear once on each side pair even when the surrounding prose differs. A repeated setting has to match as well.

| Source | A | B | Paired | Agree | Disagree | only_a | only_b | Unpaired |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| aa-1.png | 22 | 68 | 21 | 21 | 0 | 1 | 47 | 0 |
| aa-2.png | 0 | 107 | 0 | 0 | 0 | 0 | 107 | 0 |
| aa-3.png | 22 | 70 | 22 | 22 | 0 | 0 | 48 | 0 |
| aa-4.png | 22 | 70 | 22 | 22 | 0 | 0 | 48 | 0 |
| aa-5.png | 0 | 243 | 0 | 0 | 0 | 0 | 243 | 0 |
| aa-6.png | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| artificialanalysis.ai/.../intelligence-index-v4-2 | 0 | 7 | 0 | 0 | 0 | 0 | 7 | 0 |
| artificialanalysis.ai/.../intelligence-index-v4-3 | 21 | 31 | 21 | 21 | 0 | 0 | 10 | 0 |
| deepmind.google/.../gemini-3-8-flash/ | 90 | 102 | 90 | 90 | 0 | 0 | 12 | 0 |
| ds-agentic.png | 19 | 19 | 19 | 19 | 0 | 0 | 0 | 0 |
| ds-cost.png | 0 | 9 | 0 | 0 | 0 | 0 | 9 | 0 |
| ds-kv.png | 0 | 7 | 0 | 0 | 0 | 0 | 7 | 0 |
| g-attack.png | 16 | 48 | 16 | 16 | 0 | 0 | 32 | 0 |
| g-cwe.png | 0 | 30 | 0 | 0 | 0 | 0 | 30 | 0 |
| g-cybergym.png | 5 | 5 | 5 | 5 | 0 | 0 | 0 | 0 |
| g-deepswe.png | 0 | 76 | 0 | 0 | 0 | 0 | 76 | 0 |
| g-harvey.webp | 6 | 6 | 6 | 6 | 0 | 0 | 0 | 0 |
| g-hle.webp | 6 | 6 | 6 | 6 | 0 | 0 | 0 | 0 |
| g-rwvuln.png | 3 | 3 | 3 | 3 | 0 | 0 | 0 | 0 |
| g-table.png | 85 | 97 | 85 | 85 | 0 | 0 | 12 | 0 |
| g-vals.webp | 6 | 6 | 6 | 6 | 0 | 0 | 0 | 0 |
| blog.google/.../3-8-flash-and-3-8-flash-cyber/ | 0 | 6 | 0 | 0 | 0 | 0 | 6 | 0 |
| huggingface.co/.../DeepSeek-V3.2-Exp | 28 | 28 | 26 | 26 | 0 | 2 | 2 | 0 |
| huggingface.co/.../DeepSeek-V4.1-Flash | 176 | 179 | 173 | 173 | 0 | 3 | 6 | 0 |
| openai.com/index/gpt-6-astra/ | 139 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| openai.com/index/introducing-gpt-6-sol-and-luna/ | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| qwen-235.jpg | 58 | 58 | 58 | 58 | 0 | 0 | 0 | 0 |
| qwen-30.jpg | 42 | 63 | 42 | 42 | 0 | 0 | 21 | 0 |
| qwen-base.jpg | 75 | 75 | 75 | 75 | 0 | 0 | 0 | 0 |
| qwen-budget.png | 0 | 28 | 0 | 0 | 0 | 0 | 28 | 0 |
| qwen-post.png | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| qwenlm.github.io/blog/qwen3/ | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Totals: agree 696, disagree 0, only_a 6, only_b 751, unparsed 0, unpaired_source 2.

### Printed disagreements

None. Every paired bar is printed on both sides, and the digits agree.

### Estimated disagreements

0 outside reader B's stated uncertainty. The paired bars are printed. Reader B's estimated items are `only_b`: charts this pass left `needs_reading`, plus scatters and extra series on images that were only partly transcribed.

`only_b` is coverage reader A missed, and those bars were not added to the fixtures. The large groups are aa-5 (243, per-evaluation small multiples), aa-2 (107, output-token chart), g-deepswe (76), the cost scatters under aa-3 (48), aa-4 (48) and aa-1 (47), g-attack ASR@1 and ASR@10 segments (32), g-cwe (30), qwen-budget (28), and the extra series on qwen-30 (21).

Six bars stayed `only_a` because the model string or the setting differs:

- aa-1: reader A has Gemini 3.5 Flash (high) at 47. Reader B's 47 on that chart is Gemini 3.8 Flash (high).
- DeepSeek-V3.2-Exp, BrowseComp-zh: reader A calls the section reasoning with no tools (45.0 and 47.9). Reader B calls it agentic tool use (45 and 47.9).
- DeepSeek-V4.1-Flash HLE: reader B marks GLM-5.3 42.0, DS-V4-Pro 42.7, and DS-V4-Flash 37.8 as the text-only subset. Reader A recorded those same digits as the headline HLE cell.

### GDP.pdf on the v4.2 article

Reader B's printed all-pass bars agree with reader A. GPT-6 Astra (max) is 33.2 on both sides. GLM-5.3 (max) is 11.8 on both sides. The card still holds 33.0 and 12.0 from the same URL, so both bars stay `mismatched` and `known_mismatch`.

### g-deepswe, g-harvey, g-hle, g-vals

g-deepswe was left `needs_reading`, so reader B's 76 points are `only_b`. Within reader B's own files, the labelled Opus 5 point is 73.6 (estimated, uncertainty 0.3) and g-table prints 74.0. The gap is 0.4, outside that uncertainty. The other Opus point on that line is 73.1. The labelled Sonnet 5 point is 49.7 (uncertainty 0.3) and g-table prints 53.8. The other Sonnet points are 48.2, 39.8, and 30.5. None is 53.8.

g-harvey, g-hle, and g-vals each match g-table on all six models. Harvey all-pass is 10.0, 8.8, 6.7, 5.0, 2.5, 0.8. HLE-Verified is 54.9, 53.6, 54.4, 31.0, 54.5, 51.1. Vals Finance Agent v2 is 61.4, 59.0, 58.6, 53.9, 53.8, 54.4. The order is Gemini 3.8 Flash, Gemini 3.7 Flash, Claude Opus 5, Claude Sonnet 5, GPT-5.6 Sol, GPT-5.6 Terra.

## Phase 2a: Anthropic and xAI

Reader A, 2026-09-24. Cards were not edited. Thirteen pages, 552 charts, 26 transcribed, 526 left `needs_reading`. 746 bars. The full checker, including phase 1, is 22 pages, 600 charts, 1,597 bars, and exits clean.

### Pages

Fetched.

| Page | What came back |
| --- | --- |
| https://www.anthropic.com/claude-opus-5-5-system-card | PDF, 230 pages. Claude Opus 5.5 System Card, 22 September 2026. |
| https://www.anthropic.com/claude-fable-5-1-system-card | PDF, 212 pages. Claude Fable 5.1 and Claude Mythos 5.1. |
| https://www.anthropic.com/claude-opus-5-system-card | PDF, 198 pages. |
| https://www.anthropic.com/claude-sonnet-5-system-card | PDF, 146 pages. |
| https://www.anthropic.com/claude-opus-4-8-system-card | PDF, 246 pages. |
| https://www.anthropic.com/claude-opus-5-5 | Launch page. The `/news/claude-opus-5-5` slug redirects here. |
| https://www.anthropic.com/claude-fable-and-mythos-5-1 | Launch page. The sitemap has no `/news/` URL for Fable 5.1. |
| https://www.anthropic.com/news/claude-opus-5 | Launch post. |
| https://www.anthropic.com/news/claude-sonnet-5 | Launch post. |
| https://www.anthropic.com/news/claude-opus-4-8 | Launch post. |
| https://x.ai/news/grok-4-7 | Launch post, 21 September 2026. |
| https://x.ai/news/grok-4-6 | Launch post, 12 August 2026. |
| https://x.ai/news/grok-4-5 | Launch post. The page dates itself 16 July 2026. |

Not fetched. `https://x.ai/news` returned 403. The three post URLs returned 200. None of those posts links a model card. `https://www.anthropic.com/news/claude-fable-5-mythos-5` is the earlier Fable 5 post, so it is not a source for 5.1.

The 526 `needs_reading` charts are the Figure and Table captions in the five system cards that this pass did not transcribe, plus launch charts whose points are not labelled: the Sonnet 5 BrowseComp and OSWorld effort plots, the Opus 4.8 misalignment chart, the Grok 4.7 CursorBench scatter, the Opus 5 Frontier-Bench effort plot, and ten other images on the Opus 5 post. Summary tables, the launch grids with printed cells, and the charts whose labels were read are the 26 transcribed charts.

### Bars

| Class | Bars |
| --- | ---: |
| matched | 27 |
| other_configuration | 2 |
| mismatched | 0 |
| unit_differs | 0 |
| other_metric | 2 |
| no_benchmark_page | 306 |
| not_held | 407 |
| competitor_unresolved | 2 |

The two `other_configuration` bars are Claude Opus 5.5 on Terminal-Bench 4.0 from the system card. The summary table's 66.4 matches the card. The section also prints 66.36 at xhigh and 64.8 at max.

### Coverage

Headline subject bars with a catalogue id. Held means a same-source row exists, including a mismatch or another configuration.

| Model | Held / published | Matched |
| --- | ---: | ---: |
| anthropic/claude-opus-5-5 | 10/27 | 8 |
| anthropic/claude-fable-5-1 | 6/44 | 6 |
| anthropic/claude-mythos-5-1 | 1/3 | 1 |
| anthropic/claude-opus-5 | 1/66 | 1 |
| anthropic/claude-sonnet-5 | 1/22 | 1 |
| anthropic/claude-opus-4-8 | 2/50 | 2 |
| xai/grok-4-7 | 0/5 | 0 |
| xai/grok-4-6 | 0/10 | 0 |
| xai/grok-4-5 | 0/7 | 0 |

Opus 5.5 matches the rows that cite its system card: SWE-bench Pro 89.9, SWE-bench Multilingual 93.9, SWE-bench Multimodal 61.4, Terminal-Bench 4.0 66.4, Terminal-Bench Science 58.7, HLE 64.4, HLE with tools 67.7, AutomationBench 40.0.

Fable 5.1 matches SWE-bench Pro 81.2, SWE-bench Multilingual 89.1, SWE-bench Multimodal 54.7, Terminal-Bench Science 52.6, ARC-AGI-2 90.0, and Terminal-Bench 4.0. The table prints 56. The card holds 55.8. A whole number is ±0.5, so 56 matches 55.8. Mythos 5.1's parenthetical 61 matches the card's 60.9 the same way.

Opus 4.8 matches SWE-bench Verified 88.6 and GPQA Diamond 93.6. Opus 5 matches SWE-bench Verified 96.0. Sonnet 5 matches SWE-bench Verified 85.2. The Grok cards do not cite these posts, so those subject bars are not held.

### Mismatched bars

None.

Gemini 3.1 Pro on GPQA Diamond, Table 8.1.A of the Claude Opus 4.8 system card, prints 94.3. The Gemini card's row for that benchmark is 94.14 from https://artificialanalysis.ai/leaderboards/models, `source_kind: independent_evaluator`. An `official_reports` bar is checked against `provider_self_report` rows only. This card has none for GPQA Diamond, so the bar is `not_held` and that row is context. The `known_mismatch` mark is removed. The card was not edited.

### Gaps above 2 points

No same-unit competitor gap in this pass is larger than 2 points. There is no `competitor_gap` bar.

Twelve bars print GDPval-AA or AA-Briefcase as Elo. Each rival card holds an `independent_evaluator` percent or normalised Elo percent for that benchmark and no `provider_self_report`, so the bar is `not_held`. The row below is context.

| Model | Chart | Chart unit | Card | Card unit | Card source |
| --- | ---: | --- | ---: | --- | --- |
| GPT-5.6 Sol | 1711 | elo | 56.21 | percent | https://artificialanalysis.ai/leaderboards/models |
| Gemini 3.1 Pro | 1314 | elo | 20.2 | percent | https://artificialanalysis.ai/leaderboards/models |
| GPT-6 Astra | 1542 | elo | 54 | normalized Elo percent | https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2 |
| GPT-6 Astra | 1569 | elo | 53 | normalized Elo percent | https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-2 |
| GPT-5.6 Sol | 1588 | elo | 56.21 | percent | https://artificialanalysis.ai/leaderboards/models |
| GPT-5.6 Sol | 1736 | elo | 56.21 | percent | https://artificialanalysis.ai/leaderboards/models |
| Gemini 3.5 Flash | 1357 | elo | 37.95 | percent | https://artificialanalysis.ai/leaderboards/models |
| GPT-5.6 Sol | 1728 | elo | 56.21 | percent | https://artificialanalysis.ai/leaderboards/models |

1711 is on both the Fable 5.1 system card and https://www.anthropic.com/claude-fable-and-mythos-5-1. 1314 is on both the Opus 4.8 system card and https://www.anthropic.com/news/claude-opus-4-8. 1542 is on both the Opus 5.5 system card and https://www.anthropic.com/claude-opus-5-5. 1588 is on the Opus 5.5 launch page. 1736 is on both the Opus 5 system card and https://www.anthropic.com/news/claude-opus-5. 1357 is on the Sonnet 5 system card. 1728 is on https://x.ai/news/grok-4-6. 1569 is AA-Briefcase on the Opus 5.5 system card.

### Uncatalogued benchmarks

306 bars have `benchmark_id: null`. The count is how many times the label was printed.

| Benchmark as labelled | Bars |
| --- | ---: |
| Toolathlon | 52 |
| FrontierCode v1.1 (Main) | 19 |
| DeepSWE v1.1 | 17 |
| CursorBench 4.0 | 15 |
| ArXivMath | 15 |
| Shade coding attack success rate | 12 |
| FrontierCode v1.1 (Extended) | 10 |
| Finance Agent v2 | 9 |
| Chartography | 9 |
| Single-turn harmless response rate | 8 |
| Single-turn over-refusal rate | 8 |
| Firefox 147 exploit development | 8 |
| EEBench | 8 |
| ARC-AGI-1 | 7 |
| ARC-AGI-3 | 6 |
| BioMysteryBench | 6 |

## Publisher inconsistencies (phase 2a)

Reader A is the fixture. Reader B is the second reading in `.chart-check/reader-b-2a`. A figure is double-read when both files hold it for the same document, model, and benchmark. Card rows below are context. The cards were not edited.

### Fable 5 on Frontier-Bench v0.1

The Opus 5 launch table prints 33.7. The Opus 5 system card prints 33.8. Both readers recorded both. Both rows are labelled Frontier-Bench v0.1.

`anthropic/claude-fable-5` has no evidence row for this benchmark.

### Opus 4.8 on Terminal-Bench 2.1

The Sonnet 5 launch table, in the column marked for reference, prints 82.7. The Opus 4.8 system card and the Opus 4.8 launch table print 74.6. The card row is labelled Terminus-2 public harness. The Grok 4.5 page prints 78.9, labelled max. Both readers recorded 82.7, 74.6, and 78.9. Every row is Terminal-Bench 2.1. The harness name is on the 74.6 card row. The max label is on the 78.9 row.

`anthropic/claude-opus-4-8` has no `terminal_bench_v2_1` evidence row.

### Opus 4.8 on GDPval-AA v2

The Sonnet 5 launch table prints 1615. The Opus 5 system card and the Opus 5 launch table print 1593. Both readers recorded both. Both rows are labelled GDPval-AA v2.

`anthropic/claude-opus-4-8` holds `gdpval_aa` 49.45 percent, `source_kind: independent_evaluator`, from the Artificial Analysis leaderboard column `gdpvalNormalized`. That row is the normalized percent, not these Elo figures.

### Opus 5 on FrontierCode v1.1 Main

The Opus 5 card and the Opus 5 launch table print 53.4. Both readers recorded both.

The Opus 5.5 system card prints 48.0, labelled max effort on the summary table, and 53.4, labelled best reasoning effort. Reader A recorded both. Reader B recorded 48.0 on that card.

The Opus 5.5 page table prints 48.0. Both readers recorded it. Reader A also recorded 54.6 on that page, labelled default effort, called medium in the post. Reader B's page chart records 53.4 at med and 48.0 at max. Reader A's page fixture has no 53.4 bar.

The benchmark label is FrontierCode v1.1 Main on these rows. Effort labels sit on the Opus 5.5 card rows.

`anthropic/claude-opus-5` has no FrontierCode evidence row.

### Opus 5 on HLE

The Opus 5 card prints 56.3 with no tools and 64.7 with tools. The Fable 5.1 card and page print 56.6 and 63.6. The Opus 5.5 card and page print 56.6 and 63.6. Both readers recorded all six. The 56.3, 56.6, and 56.6 rows are all labelled no tools. The 64.7, 63.6, and 63.6 rows are all labelled with tools. No separate benchmark version is written on either side.

`anthropic/claude-opus-5` has no `hle` or `hle_tools` row. `anthropic/claude-opus-5-5` holds `hle` 64.4 and `hle_tools` 67.7, both `source_kind: provider_self_report`, from its own system card, Table 8.1.A, Opus 5.5 column.

### Opus 5 on OSWorld 2.0

The Opus 5 card prints 70.6, one OSWorld 2.0 figure. The Fable 5.1 card and page print 75.4 partial and 39.6 strict. The Opus 5.5 card and page print 74.0 partial and 37.2 strict. Both readers recorded all five. Partial and strict are labelled on the Fable 5.1 and Opus 5.5 rows. The Opus 5 card row has no partial or strict label.

`anthropic/claude-opus-5` has no `osworld` row.

### Opus 5 on GDPval-AA v2

The Opus 5 card and launch table print 1861. The Fable 5.1 card and page print 1824. Both readers recorded both. Both rows are labelled GDPval-AA v2.

`anthropic/claude-opus-5` holds `gdpval_aa` 61.75 percent, `source_kind: independent_evaluator`, from the Artificial Analysis leaderboard column `gdpvalNormalized`.

### Opus 5 on AA-Briefcase

The Opus 5 card prints 1720, labelled AA-Briefcase. The Fable 5.1 card prints 1685, labelled AA-Briefcase. The Opus 5.5 card prints 1673, labelled AA-Briefcase v1.1. Both readers recorded all three. The v1.1 label is on the 1673 row.

`anthropic/claude-opus-5` has no `aa_briefcase` row.

### Opus 5 on AutomationBench

The Opus 5 card prints 26.0. The Fable 5.1 card and page, and the Opus 5.5 card, print 26.9. Both readers recorded both figures. The rows share the AutomationBench label.

`anthropic/claude-opus-5` has no `automationbench` row. `anthropic/claude-opus-5-5` holds `automationbench` 40.0, `source_kind: provider_self_report`, from its own card, and 42.47, `source_kind: benchmark_author`, from Zapier. Those rows are the Opus 5.5 score.

### Fable 5 on the Opus 5 card and the Fable 5.1 card

The Opus 5 card, labelled Fable 5, prints HLE 56.5 and 63.9, GDPval-AA v2 1747, AA-Briefcase 1574, and AutomationBench 17.4. Both readers recorded these.

The Fable 5.1 card prints HLE 57.8 and 63.8, GDPval-AA v2 1723, AA-Briefcase 1572, AutomationBench 17.1, and HealthBench Professional 63.3. Reader A labelled the model Fable 5. Reader B labelled the column Claude Fable 5/ Mythos 5. Both readers recorded the numbers.

HealthBench Professional 66.0 is on the Opus 5 card. Reader A labelled that bar Mythos 5 and noted the footnote on the Fable 5 cell. Reader B labelled the bar Fable 5 and recorded the footnote. Both recorded 66.0, and both recorded 63.3 on the Fable 5.1 card. Both rows are HealthBench Professional.

`anthropic/claude-fable-5` has no evidence row for these benchmarks. `anthropic/claude-mythos-5` has no evidence rows.

### Mythos 5 on Terminal-Bench 4.0

The Fable 5.1 card prints 45 as a whole percent, the parenthetical under the Fable 5 / Mythos 5 column. Reader B recorded (45%) on the column Claude Fable 5/ Mythos 5. Both readers have 45.

Reader B recorded 45.8 for Mythos 5 at max on the Fable page chart, from the point data. Reader A's page fixture has no 45.8 bar. The max label is on Reader B's chart point.

`anthropic/claude-mythos-5` has no `terminal_bench_v4_0` row. `anthropic/claude-mythos-5-1` holds `terminal_bench_v4_0` 60.9, `source_kind: provider_self_report`, from the Fable 5.1 system card.

### Fable 5.1 on HLE with tools

The Fable 5.1 card and page print 65.0. The Opus 5.5 card and page print 65.6. Both readers recorded both. Both rows are labelled with tools.

`anthropic/claude-fable-5-1` has no `hle_tools` row. `anthropic/claude-opus-5-5` holds `hle_tools` 67.7, `source_kind: provider_self_report`, Opus 5.5 column of its own card.

### Fable 5.1 on OSWorld 2.0

The Fable 5.1 card and page print 77.9 partial and 41.7 strict. The Opus 5.5 card and page print 80.7 partial and 42.8 strict. Both readers recorded all four. The 77.9 and 80.7 rows are both labelled partial. The 41.7 and 42.8 rows are both labelled strict. No other version label is written on either side.

`anthropic/claude-fable-5-1` has no `osworld` row.

### GPT-5.6 Sol

GDPval-AA v2 is 1736 on the Opus 5 card and launch table, 1711 on the Fable 5.1 card and page, and 1728 on the Grok 4.6 page. Both readers recorded all three. All three rows are labelled GDPval-AA v2.

AA-Briefcase is 1505 on the Opus 5 card and 1502 on the Fable 5.1 card and the Grok 4.6 page. Both readers recorded both. These rows have no v1.1 label.

AutomationBench is 18.1 on the Opus 5 card, 19.6 on the Fable 5.1 card and page, and 28.8 on the Opus 5.5 page. Both readers recorded all three.

ARC-AGI-1 is 97.5 on the Opus 5 card. Reader A's bar there is labelled xhigh. The Fable 5.1 card prints 96.5 with no xhigh label. Both readers recorded both numbers. The xhigh label is on the 97.5 row.

`openai/gpt-5-6-sol` holds `gdpval_aa` 56.21 percent, `source_kind: independent_evaluator`, from the Artificial Analysis leaderboard column `gdpvalNormalized`. The card has no `aa_briefcase`, `automationbench`, or `arc_agi_1` row.

### GPT-5.5 on Terminal-Bench 2.1

The Opus 4.8 card and launch table print 78.2. The card row is labelled Terminus-2 public harness. The Sonnet 5 card prints 83.4, labelled Codex CLI. Both readers recorded both. Both rows are Terminal-Bench 2.1. The harness name differs.

`openai/gpt-5-5` has no `terminal_bench_v2_1` row.

### Opus 4.8 on AutomationBench

The Opus 4.8 card prints 15.5. The Opus 5 card prints 17.0. Both readers recorded both. Both rows are AutomationBench.

`anthropic/claude-opus-4-8` has no `automationbench` row.

### Toolathlon Pass@1

Opus 5 card, Table 8.13.6.A: Sonnet 5 74.7, Opus 4.8 79.9, Mythos 5 79.3. Sonnet 5 card, Table 8.11.5.A: Sonnet 5 54.3, Opus 4.8 59.9, Mythos 5 61.7. Both readers recorded all six. Reader A's benchmark label is Toolathlon on both tables. Reader B's Opus 5 card setting says Toolathlon-Verified, June 2026 release. Reader B's Sonnet 5 card label is Toolathlon.

None of these model cards has a Toolathlon evidence row.

### Fable 5.1 on Terminal-Bench 4.0

The Grok 4.7 table prints 57.9 in the Fable 5.1 column. Both readers recorded that.

The Opus 5.5 card and page print 55.8 for Fable 5.1 and 57.9 for GPT-6 Astra. Both readers recorded both. Reader A's Astra bar says high thinking effort, as OpenAI reported.

The Fable 5.1 card's summary bar is a whole percent. Reader A recorded 56 for Fable 5.1 there. The card's evidence rows, which are not chart bars, are `terminal_bench_v4_0` 55.8, `source_kind: provider_self_report`, from the system card, and 57.88, `source_kind: benchmark_author`, from https://www.tbench.ai/leaderboard.

57.9 is the Grok 4.7 table's Fable 5.1 column, and it is the GPT-6 Astra figure on the Opus 5.5 card and page. 55.8 is the Fable 5.1 figure on those Opus 5.5 documents and on the Fable 5.1 card's self-report row. 57.88 is the tbench.ai row on the Fable 5.1 card.

### Fable 5.1 on DeepSWE v1.1

The Grok 4.7 table prints 70.0. Both readers recorded it. Reader A recorded 67.4 on the Fable 5.1 card, labelled DeepSWE v1.1, mean of five trials. Reader B's item file for that PDF has no DeepSWE row and no 67.4.

`anthropic/claude-fable-5-1` has no DeepSWE evidence row.

### Grok 4.6 on DeepSWE v1.1

The Grok 4.6 page prints 65.9. The Grok 4.7 page prints 65.2. Both readers recorded both. Both rows are labelled DeepSWE v1.1.

`xai/grok-4-6` has no evidence rows.

### Grok 4.5 on DeepSWE 1.1

The Grok 4.6 table prints 54. The Grok 4.5 page prints 53. Both readers recorded both. Both rows are DeepSWE 1.1.

`xai/grok-4-5` has no DeepSWE evidence row.

### Grok 4.6 on its page and on the Grok 4.7 page

The Grok 4.6 page prints GDPval-AA v2 Elo 1753 and AA-Briefcase 1577. Both readers recorded both. The Grok 4.7 page prints GDPval 1605, labelled high on the chart tab, and AA-Briefcase 1546. Both readers recorded both. Reader A's 1605 bar uses benchmark id `gdpval`. Reader A's 1546 table bar is labelled AA Briefcase v1.1. Reader A's 1577 bar has no v1.1 label. Reader A's 1753 bar is labelled GDPVal-AA v2.

`xai/grok-4-6` has no evidence rows. `xai/grok-4-7` holds `terminal_bench_v4_0` 37.58, `source_kind: benchmark_author`, from https://www.tbench.ai/leaderboard. It has no GDPval or AA-Briefcase row.

### Opus 4.7 on Terminal-Bench 2.1, from the Grok 4.5 page

The Grok 4.5 page prints 78.9, labelled max. The Opus 4.8 card prints 66.1, labelled Terminus-2 public harness. Both readers recorded both. Both rows are Terminal-Bench 2.1.

`anthropic/claude-opus-4-7` has no `terminal_bench_v2_1` row. It holds `gdpval_aa` 44.79 percent, `source_kind: independent_evaluator`, from the Artificial Analysis leaderboard.

### Fable on SWE-bench Pro, from the Grok 4.5 page

The Grok 4.5 page prints 80.4, labelled Fable max, resolve rate. The Opus 5 card prints 80 for Fable 5 on SWE-bench Pro. Both readers recorded both. The Grok label is Fable. The Opus 5 card label is Fable 5.

`anthropic/claude-fable-5` has no `swe_bench_pro` row. `anthropic/claude-fable-5-1` holds `swe_bench_pro` 81.2, `source_kind: provider_self_report`, from its own system card.

## OpenAI second reading

Reader B (claude-opus, 2026-09-24) read both OpenAI pages in a browser. Before this pairing change the two pages were agree 40, disagree 0, only_a 109, only_b 735. After it they are agree 149, disagree 0, only_a 0, only_b 626. Every paired value agrees. There is no disagreement between two printed numbers, and no disagreement between two hover-tooltip numbers. The OpenAI charts now record reader B. No bar is `disputed`. The checker classes are unchanged: matched 53, other_configuration 9, mismatched 0, unit_differs 2, other_metric 6, no_benchmark_page 604, not_held 898, competitor_gap 11, competitor_unresolved 14.

Reader B's Astra file says the Coding table prints "-" for Claude Opus 5 on Internal Database Migration Tasks, and the chart on that page plots Opus 5 at 61.1%. That 61.1% is the dashed score-only line on the Database Migration chart. Reader A's fixture has no Internal Database Migration row and no 61.1.

The Coding table's FrontierCode 1.1 Extended cell for Claude Opus 5 is 63.6%. On the FrontierCode 1.1 Extended chart the Medium point is 63.6%. Low is 55.8%, High is 58.5%, Xhigh is 56.9%, and Max is 58.9%. Reader A's fixture holds 63.6% for that table cell, for Claude Opus 5 and for Claude Fable 5.1. It does not hold the other effort points.

Agents' Last Exam, Claude Opus 5 at high effort, is 55.2% on the Astra page and 55.9% on the Sol and Luna page. GPT-5.6 Sol at max effort is 52.7% on the Astra page and 52.8% on the Sol and Luna page. Reader A's fixture does not hold these four chart points. The 55.9 in the Astra fixture is GPT-5.6 Sol on SRE-Bench. The Sol and Luna fixture holds GPT-6 Sol at max effort, 56.4%, which is a different point and agrees with reader B.

## Phase 2b batches 1 and 2, second reading

Reader B is claude-opus, 2026-09-24. Reader A is the fixture. A disagreement on a printed cell is `disputed`, with both values on the bar. No disagreement in these two batches is a hover tooltip or an embedded chart series. Every pair below is two printed cells.

The check over all 100 fixtures, 758 charts, 11533 bars:

| Class | Bars |
| --- | ---: |
| matched | 56 |
| other_configuration | 9 |
| mismatched | 0 |
| unit_differs | 4 |
| other_metric | 171 |
| no_benchmark_page | 5491 |
| not_held | 5350 |
| competitor_gap | 71 |
| competitor_unresolved | 359 |
| disputed | 22 |

### Batch 1

agree 1582, disagree 17, only_a 638, only_b 1100, unpaired 5.

The five unpaired sources are the three `kimi-file.kimi.ai` image URLs, `https://longcat.chat/blog/longcat-2.0/` (not fetched), and `https://www.stepfun.com/step-5-preview` (no fixture with that page). The Kimi K3 coding and agents jpgs pair on their own. The LongCat SVG pairs on its own.

Printed disagreements, Hy3 appendix (`https://huggingface.co/tencent/Hy3`, image of the appendix). Reader B's starred cells keep the star in the transcribed text.

| Model | Benchmark | Reader A | Reader B |
| --- | --- | ---: | ---: |
| Seed-2.1 pro | WideSearch | 76.8 | 76.4* |
| Seed-2.1 pro | DeepSearchQA | 90.4 | 90.8* |
| GPT-5.5 | DeepSearchQA | 85.5 | 95.5* |
| Seed-2.1 pro | Apex-Agent (pass@1) | 32.8 | 33.8 |
| Seed-2.1 pro | ClawEval (pass^3) | 63.1 | 62.1* |
| DeepSeek-V4 pro | e-bench (internal) | 37.6 | 34.5* |
| Seed-2.1 pro | e-bench (internal) | 42.9 | 47.9* |
| DeepSeek-V4 pro | Hy-FinModelBench (internal) | 54.5 | 57.6* |
| Seed-2.1 pro | Hy-FinModelBench (internal) | 57.2 | 52.2* |
| Gemini-3.1-pro-preview | Hy-FinModelBench (internal) | 54.8 | 54.6* |

Printed disagreements, MiniMax-M3 card chart. YC-Bench is final assets. Reader B's text keeps the `M`.

| Model | Benchmark | Reader A | Reader B |
| --- | --- | ---: | ---: |
| Kimi K2.6 Thinking | Terminal-Bench 2.1 | 55.9 | 53.9 |
| MiniMax M3 | YC-Bench | 2.34 | 2.1M |
| Claude Opus 4.7 | YC-Bench | 2.24 | 2.2M |
| GPT 5.5 | YC-Bench | 1.34 | 1.3M |
| Gemini 3.1 Pro | YC-Bench | 1.14 | 1.1M |
| Claude Sonnet 4.6 | YC-Bench | 0.34 | 0.1M |
| DeepSeek V4 Pro | YC-Bench | 0.54 | 0.5M |

Check over the 19 batch-1 fixtures, 32 charts, 2549 bars:

| Class | Bars |
| --- | ---: |
| matched | 0 |
| other_configuration | 0 |
| mismatched | 0 |
| unit_differs | 0 |
| other_metric | 0 |
| no_benchmark_page | 1561 |
| not_held | 882 |
| competitor_gap | 9 |
| competitor_unresolved | 80 |
| disputed | 17 |

### Batch 2

agree 1840, disagree 5, only_a 813, only_b 1240, unpaired 0.

Printed disagreements, Gemma 4 technical report (`https://arxiv.org/abs/2607.02770`), MATH-Vision, max resolution, 1120 vision tokens, thinking.

| Model | Reader A | Reader B |
| --- | ---: | ---: |
| Gemma 4 12B | 79.7 | 76.7 |
| Gemma 4 26B-A4B | 82.4 | 80.3 |
| Gemma 4 31B | 85.6 | 83.4 |
| Gemma 4 E2B | 52.4 | 53.0 |
| Gemma 4 E4B | 59.5 | 59.2 |

Check over the 18 batch-2 fixtures, 42 charts, 2648 bars:

| Class | Bars |
| --- | ---: |
| matched | 3 |
| other_configuration | 0 |
| mismatched | 0 |
| unit_differs | 0 |
| other_metric | 20 |
| no_benchmark_page | 1638 |
| not_held | 942 |
| competitor_gap | 0 |
| competitor_unresolved | 40 |
| disputed | 5 |

## Publisher inconsistencies, phase 2b

Reader A is the fixture. A pair is double-read when both numbers are bars in those fixtures, for the model and benchmark named below. The label on the bar is the setting.

### GLM-5.2 MCP-Atlas, 77.0 and 76.8

The fixtures hold 76.8, labelled MCP-Atlas (Public Set), on `https://z.ai/blog/glm-5.2`, `https://huggingface.co/blog/zai-org/glm-52-blog`, and `https://huggingface.co/zai-org/GLM-5.2` (the table). The Hy3 appendix also holds 76.8 for GLM-5.2, labelled MCP atlas (public), starred, cited from that model's own report. There is no 77.0 bar. The GLM-5.2 card image has no transcribed bars. This pair is not double-read.

### GPT-5.5 PostTrainBench, 28.4 and 25.0

The fixtures hold 28.4 on the same three GLM-5.2 pages, and on the Kimi K3 card and arXiv report, labelled PostTrainBench, xhigh on the Kimi pages. There is no 25.0 bar. This pair is not double-read.

### GLM-5.2 CritPt, 20.9 and 16.7

Double-read. 20.9 is on `https://z.ai/blog/glm-5.2` and `https://huggingface.co/zai-org/GLM-5.2`, labelled CritPt. 16.7 is on `https://huggingface.co/blog/zai-org/glm-52-blog`, labelled CritPt.

### Step 3.7 Flash Terminal-Bench 2.1, 59.5 and 59.6

Double-read. 59.5 is the card chart on `https://huggingface.co/stepfun-ai/Step-3.7-Flash`. 59.6 is the blog table on `https://static.stepfun.com/blog/step-3.7-flash/`. Both bars are labelled Terminal-Bench 2.1.

### Kimi K3 blog charts against the Kimi card and the arXiv report

The blog is `https://www.kimi.com/blog/kimi-k3`, labelled max or xhigh on the launch chart. The card is `https://huggingface.co/moonshotai/Kimi-K3`. The report is `https://arxiv.org/abs/2607.24653`, Table 2, max effort in the column header. Each pair below is double-read.

Fable 5, Terminal-Bench 2.1: 84.6 on the blog, 88.0 on the card and the report.

GDPval-AA v2 (Elo) on the card and the report, and GDPval-AA on the blog chart:

| Model | Blog | Card and report |
| --- | ---: | ---: |
| Kimi K3 | 1668 | 1686 |
| Fable 5 | 1760 | 1747 |
| GPT-5.6 Sol | 1748 | 1736 |
| Opus 4.8 | 1600 | 1593 |
| GLM-5.2 | 1514 | 1510 |
| GPT-5.5 | 1494 | 1491 |

JobBench: Kimi K3 is 52.9 on the blog and 54.3 on the card and the report. GPT-5.6 Sol is 46.5 on the blog and 45.4 on the card and the report.

### Opus 4.8 Cybergym, 83.1 and 78.3

Double-read. 83.1 is on `https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731`, max effort, DeepSeek Harness minimal mode on the public code-agent rows. 78.3 is on `https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-Vision-Exp`, max effort, DeepSeek Harness minimal mode on the text-agent rows. Both bars are labelled Cybergym.

### Hy3 BrowseComp, GLM-5.2 at 79.3 and GLM-5.1 at 79.3

The appendix on `https://huggingface.co/tencent/Hy3` holds GLM-5.1 BrowseComp 79.3, unstarred, Tencent's own testing. The overview chart on that card has no transcribed bars. There is no GLM-5.2 BrowseComp bar on that card. This pair is not double-read.

### GDPval-AA v2, Opus 4.8, 1588 / 1582 / 1593 / 1600

Double-read. All four numbers are bars labelled GDPval-AA v2, except the Kimi blog bar, which is labelled GDPval-AA, max or xhigh.

| Value | Pages |
| ---: | --- |
| 1588 | `https://z.ai/blog/glm-5.3`, `https://huggingface.co/zai-org/GLM-5.3` |
| 1582 | `https://z.ai/blog/glm-5.3-flash`, `https://huggingface.co/zai-org/GLM-5.3-Flash` |
| 1593 | `https://huggingface.co/moonshotai/Kimi-K3` and `https://arxiv.org/abs/2607.24653`, max, GDPval-AA v2 (Elo). Also the Opus 5 card and the Opus 5 launch table, labelled GDPval-AA v2, Elo |
| 1600 | `https://www.kimi.com/blog/kimi-k3` |

`https://openai.com/index/gpt-5-6/` holds 1600.1 for Claude Opus 4.8 on `gdpval_aa`, with no further setting on the bar.

### Agents' Last Exam, GLM-5.2 23.8 and 20.4, Opus 4.8 25.7 and 27.0

Double-read.

GLM-5.2 at 23.8 is labelled Agents' Last Exam (ALE-CLI) on the GLM-5.3 blog and card. The same 23.8 is labelled Agents' Last Exam on the DeepSeek-V4-Flash-0731 card, max effort, public code-agent rows.

GLM-5.2 at 20.4 is labelled Agents' Last Exam on the Kimi card and arXiv report, max, and on the GLM-5.3-Flash blog and card.

Opus 4.8 at 25.7 is labelled Agents' Last Exam (ALE-CLI) on the GLM-5.3 blog and card. The same 25.7 is labelled Agents' Last Exam on both DeepSeek cards: 0731, public code-agent rows, and Vision-Exp, text-agent rows, both max effort.

Opus 4.8 at 27.0 is labelled Agents' Last Exam on the Kimi card and arXiv report, max; on the GLM-5.3-Flash blog and card; on `https://qwen.ai/blog?id=qwen3.8`, Pass@1; and on `https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B`, labelled Agents' Last Exam (Pass / Score).

### Terminal-Bench 2.1, GPT-5.5 and DeepSeek-V4-Pro

Double-read for the GPT-5.5 values 84.0, 83.4, 78.2, 82.7, and 73.8.

| Value | Where it is a bar |
| ---: | --- |
| 84.0 | Hy3 appendix; GLM-5.2 blog, HF blog, and card |
| 83.4 | Kimi blog, Kimi card, and Kimi arXiv report; GLM-5.2 blog, HF blog, and card; Sonnet 5 system card; Nex-N2-Pro card |
| 78.2 | Gemini 3.5 Flash model card and launch post, labelled Terminus-2 harness; Opus 4.8 card and system card |
| 82.7 | Step 3.7 Flash card chart and blog table |
| 73.8 | LongCat-2.0 card |

DeepSeek-V4-Pro is double-read for 64.0, 59.6, and 72.0. 64.0 is on the Hy3 appendix, the K-EXAONE-2 card, and the Inkling card. 59.6 is on the MiniMax-M3 card chart. 72.0 is on the Step 3.7 Flash blog table and the Nex-N2-Pro card.

### Kimi K3 on the Step 5 page

`https://www.stepfun.com/step-5-preview` is not a fixture. Reader A's fixtures hold Kimi K3 at 33.4 on τ³-Banking, max, on the Kimi card and the arXiv report. They hold 30.8 on AutomationBench on the Kimi blog, card, and report. They hold 46.7 on AutomationBench (v1.0.6) for Kimi K3 on the GLM-5.3 blog and card. There is no 46.0 bar on τ³-Banking. The Step 5 pair is not double-read.

### Gemini 3.1 Pro Terminal-Bench 2.1, Terminus-2, 70.3 and 73.8, and OpenAI 70.7

Double-read. 70.3 is on the Gemini 3.5 Flash model card and launch post, labelled Terminus-2 harness. 73.8 is on the Gemini 3.6 Flash model card, labelled Terminus-2 harness. 70.7 is on `https://openai.com/index/gpt-5-6/`, and also on the LongCat-2.0 card and the three GLM-5.2 pages.

### GPT-5.5 Terminal-Bench 2.1, DeepMind 78.2 and OpenAI 85.6

Double-read. 78.2 is on the Gemini 3.5 Flash model card and launch post, labelled Terminus-2 harness, and on the Opus 4.8 card and system card. 85.6 is on `https://openai.com/index/gpt-5-6/`, appendix comparison table, with no further setting on the bar.

### Claude Opus 4.8 Terminal-Bench 2.1, Qwen 84.6 and OpenAI 78.9

Double-read. 84.6 is on `https://qwen.ai/blog?id=qwen3.8` and `https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B`, model label Opus4.8 on the blog and Opus 4.8 on the README, no further setting on either bar. 78.9 is on `https://openai.com/index/gpt-5-6/`, appendix comparison table, no further setting on the bar.

### GPT-5.6 Sol GPQA Diamond, Qwen 94.1 and OpenAI 94.6

Double-read. 94.1 is on `https://qwen.ai/blog?id=qwen3.8`, model label GPT5.6 Sol (max), configuration Max, and on the Qwen3.8-2.4T README, model label GPT 5.6 Sol (max). 94.6 is on `https://openai.com/index/gpt-5-6/`, appendix, model label GPT-5.6 Sol, no further setting on the bar.

### GPT-5.6 Sol Agents' Last Exam, Qwen 53.6 and OpenAI 52.7 and 53.6

Double-read. The Qwen 3.8 blog holds two bars for GPT5.6 Sol (max): 53.6, configuration Max, Score, and 30.6, configuration Max, Pass@1. The Qwen3.8-2.4T README also holds 53.6. The OpenAI appendix holds 52.7 for GPT-5.6 Sol. The OpenAI introduction chart holds 53.6 for GPT-5.6 Sol, and that bar's configuration says the appendix table prints 52.7 for the same name.

### Gemini 3.1 Pro MMMU-Pro, 81.8 and 80.5

Double-read. 81.8 is on `https://qwen.ai/blog?id=qwen3.7-plus`, model label Gemini-3.1 Pro. 80.5 is on the Gemini 3.5 Flash model card and launch post, labelled no tools; on the MiniMax-M3 card chart; and on the OpenAI GPT-5.6 appendix, model label Gemini 3.1 Pro Preview, no tools.

### Qwen3.7-Plus CharXiv, 84.4 and 85.8, without a code interpreter

Double-read. 84.4 is on `https://qwen.ai/blog?id=qwen3.7-plus`, labelled without a code interpreter. 85.8, labelled without CI, is on `https://qwen.ai/blog?id=qwen3.8`, `https://huggingface.co/Qwen/Qwen3.8-27B`, `https://qwen.ai/blog?id=qwen3.8-flash-next`, and `https://huggingface.co/Qwen/Qwen3.8-Flash-Next`.

### Qwen3.7-Plus SWE-bench Pro, 57.6 and 55.8

Double-read. 57.6 is on `https://qwen.ai/blog?id=qwen3.7-plus`, configuration "Corrected task set", and on `https://huggingface.co/Qwen/Qwen3.8-27B`. 55.8 is on `https://qwen.ai/blog?id=qwen3.8-flash-next` and `https://huggingface.co/Qwen/Qwen3.8-Flash-Next`.

### Qwen3.7-Max CoWorkBench, 67.2 and 64.6

Double-read. 67.2 is on `https://qwen.ai/blog?id=qwen3.7`. 64.6 is on `https://qwen.ai/blog?id=qwen3.8` and `https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B`. The bars are labelled CoWorkBench.

### Gemma 4 Tau2, E4B 42.2 and E2B 24.5, and the report's domain scores

The model card `https://ai.google.dev/gemma/docs/core/model_card_4` holds Tau2 42.2 for Gemma 4 E4B and 24.5 for Gemma 4 E2B, each labelled average over 3.

The technical report `https://arxiv.org/abs/2607.02770` holds the domain scores, labelled thinking. E4B is airline 52.0, retail 67.1, telecom 18.4. E2B is airline 31.0, retail 34.6, telecom 19.7. The report fixture has no bar at 45.8 and no bar at 28.4. The pair of averages against those two means is not double-read. The card averages and the six domain scores are bars.

### OpenAI GPT-5.6 BrowseComp, 92.2 and 90.4

Double-read, both on `https://openai.com/index/gpt-5-6/`. The appendix table holds GPT-5.6 Sol at 90.4 and GPT-5.6 Sol Ultra at 92.2, the Ultra bar labelled Ultra. The introduction chart on that page does not add a second Sol bar at 92.2.
