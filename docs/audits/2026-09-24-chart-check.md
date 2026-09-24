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
