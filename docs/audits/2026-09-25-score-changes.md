# Audit: score changes in #241 and #254

Read date: 2026-09-25.

This audit covers the 30 Arena evidence changes in #241 and the score changes
listed in #254. It checks the value, the evaluated model identity, the effort
variant, and the evidence or observation date. A null remains preferable to an
unsupported value.

## Sources and method

The Arena checks use revision
`1880dbebff5ba3e2dd3865ecf6fc43539c2099db` of the CC BY 4.0
[`lmarena-ai/leaderboard-dataset`](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset),
read on 2026-09-25. `T` below is the pinned
[`text_style_control` Parquet file](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/text_style_control/latest-00000-of-00001.parquet).
`V` is the pinned
[`vision_style_control` Parquet file](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/1880dbebff5ba3e2dd3865ecf6fc43539c2099db/vision_style_control/latest-00000-of-00001.parquet).
The files publish each audited Arena row with `leaderboard_publish_date`
2026-09-13. The audit compared the full-precision source value with the card's
two-decimal value.

The other checks use retained source snapshots collected on 2026-09-25 from
the primary boards:

- [FrontierCode](https://cognition.com/frontiercode)
- [OSWorld 2](https://osworld-v2.xlang.ai/)
- [SWE-bench](https://www.swebench.com/)
- [SWE-bench Pro](https://labs.scale.com/leaderboard/swe_bench_pro_public)
- [CursorBench](https://cursor.com/cursorbench)

The deterministic structured-row reader verified every sampled #254 row. The
verification records are in `verification/log.jsonl`. No excluded source from
`tests/test_removed_sources.py` appears in this audit.

## MODEL-156: #241

### Result

#241 changed 30 evidence values while filing the first verified premier-set
evidence. It read `arena_elo_style_control` from the raw `text` configuration
and `arena_sc_vision` from the raw `vision` configuration. The benchmark IDs
name the style-control configurations, so all 30 changes were wrong even
though each number matched the wrong configuration.

The first 10 rows checked produced 10 errors. The 100% sample error rate
exceeded 10%, so the audit checked all 30 rows. The exact error rate is 30 of
30, or 100%.

#254 later restored every one of the 30 rows to the style-control value. The
current cards contain those restored values, so MODEL-156 needs no further card
change.

### All 30 rows

`#241 value` is the wrong raw-configuration value. `Source value` is the
correct style-control value, rounded as the card stores it. Each evaluated name
is the row selected by MODEL-123's highest-effort rule. A suffix such as
`high`, `xhigh`, or `max` is part of that selection, not a sibling model.

| Card | Benchmark | #241 value | Source value | Source | Evaluated row | Verdict |
|---|---|---:|---:|---|---|---|
| `anthropic/claude-fable-5-1` | `arena_elo_style_control` | 1507.5817496991563 | 1498.47 | T | `claude-fable-5.1-max` | wrong configuration |
| `anthropic/claude-fable-5` | `arena_elo_style_control` | 1492.62585065081 | 1505.68 | T | `claude-fable-5` | wrong configuration |
| `anthropic/claude-opus-4-6` | `arena_elo_style_control` | 1502.9605478102897 | 1504.56 | T | `claude-opus-4-6-high` | wrong configuration |
| `anthropic/claude-opus-4-7` | `arena_elo_style_control` | 1489.9999284927271 | 1501.75 | T | `claude-opus-4-7-high` | wrong configuration |
| `anthropic/claude-opus-5` | `arena_elo_style_control` | 1504.959276878543 | 1487.36 | T | `claude-opus-5-max` | wrong configuration |
| `deepseek/deepseek-v4-pro` | `arena_elo_style_control` | 1450.6296556657103 | 1457.34 | T | `deepseek-v4-pro` | wrong configuration |
| `google/gemini-3-1-pro-preview` | `arena_elo_style_control` | 1480.0754473378818 | 1486.81 | T | `gemini-3.1-pro-preview` | wrong configuration |
| `google/gemini-3-5-flash` | `arena_elo_style_control` | 1482.1079294588812 | 1477.68 | T | `gemini-3.5-flash-high` | wrong configuration |
| `google/gemini-3-7-flash` | `arena_elo_style_control` | 1490.4920154663198 | 1489.82 | T | `gemini-3.7-flash-high` | wrong configuration |
| `google/gemini-3-8-flash` | `arena_elo_style_control` | 1494.673989980363 | 1493.01 | T | `gemini-3.8-flash-high` | wrong configuration |
| `meta/muse-spark` | `arena_elo_style_control` | 1473.3254184714117 | 1488.05 | T | `muse-spark` | wrong configuration |
| `moonshot/kimi-k2-6` | `arena_elo_style_control` | 1454.9198580085667 | 1460.44 | T | `kimi-k2.6` | wrong configuration |
| `moonshot/kimi-k3` | `arena_elo_style_control` | 1472.272610174843 | 1484.77 | T | `kimi-k3-max` | wrong configuration |
| `openai/gpt-5-4` | `arena_elo_style_control` | 1469.6333474659352 | 1476.39 | T | `gpt-5.4-high` | wrong configuration |
| `openai/gpt-5-6-sol` | `arena_elo_style_control` | 1455.0457372771807 | 1483.47 | T | `gpt-5.6-sol-xhigh` | wrong configuration |
| `openai/gpt-6-astra` | `arena_elo_style_control` | 1443.7243904445113 | 1479.77 | T | `gpt-6-astra-max` | wrong configuration |
| `zhipu/glm-5-2` | `arena_elo_style_control` | 1466.9328617073902 | 1472.10 | T | `glm-5.2-max` | wrong configuration |
| `zhipu/glm-5-3` | `arena_elo_style_control` | 1475.0836598142798 | 1483.02 | T | `glm-5.3-max` | wrong configuration |
| `anthropic/claude-fable-5-1` | `arena_sc_vision` | 1322.3403440993363 | 1288.87 | V | `claude-fable-5.1-max` | wrong configuration |
| `anthropic/claude-fable-5` | `arena_sc_vision` | 1325.8646704650125 | 1309.50 | V | `claude-fable-5` | wrong configuration |
| `anthropic/claude-opus-4-6` | `arena_sc_vision` | 1315.1412061489045 | 1298.86 | V | `claude-opus-4-6-high` | wrong configuration |
| `anthropic/claude-opus-4-7` | `arena_sc_vision` | 1316.0651308650738 | 1300.94 | V | `claude-opus-4-7-high` | wrong configuration |
| `anthropic/claude-opus-5` | `arena_sc_vision` | 1321.2117571301064 | 1289.03 | V | `claude-opus-5-high` | wrong configuration |
| `google/gemini-3-1-pro-preview` | `arena_sc_vision` | 1295.6086087119418 | 1278.69 | V | `gemini-3.1-pro-preview` | wrong configuration |
| `google/gemini-3-5-flash` | `arena_sc_vision` | 1310.1635899312562 | 1283.70 | V | `gemini-3.5-flash-high` | wrong configuration |
| `meta/muse-spark` | `arena_sc_vision` | 1306.1326259105908 | 1293.68 | V | `muse-spark` | wrong configuration |
| `moonshot/kimi-k2-6` | `arena_sc_vision` | 1280.4021111479485 | 1262.37 | V | `kimi-k2.6` | wrong configuration |
| `openai/gpt-5-4` | `arena_sc_vision` | 1302.2448859376395 | 1284.79 | V | `gpt-5.4-high` | wrong configuration |
| `openai/gpt-5-6-sol` | `arena_sc_vision` | 1280.1302782857852 | 1285.95 | V | `gpt-5.6-sol-xhigh` | wrong configuration |
| `openai/gpt-6-astra` | `arena_sc_vision` | 1278.5755227326415 | 1284.00 | V | `gpt-6-astra-max` | wrong configuration |

## MODEL-158: #254

### Change-count correction

The PR body says 53 score changes, including 13 FrontierCode and OSWorld
precision trims. Its own table and a semantic diff show 48 score changes:

| Kind | Rows |
|---|---:|
| Arena style-control restorations | 30 |
| FrontierCode precision trims | 12 |
| OSWorld 2 precision trims | 2 |
| Rows added from boards | 4 |
| Total | 48 |

Five FrontierCode changes also renamed the evaluated model from the card's
lab-prefixed spelling to the board's spelling. An identity-sensitive diff
counts each renamed row as one removal and one addition, which produces 53.
Those are still five changed evidence rows, not 10 score changes.

### Result

The audit set contains 38 distinct rows: all 30 Arena restorations, four of the
14 precision trims, and all four board additions. No audited row is wrong. The
error rate is 0 of 38, or 0%, so the ticket does not require a full check of the
remaining 10 precision trims.

The Arena rows match the pinned style-control files, including the evaluated
model names and MODEL-123 effort selections. The 30 restorations exactly undo
the 30 errors from #241.

### Stratified sample

The table lists 13 representative rows from the 38-row audit set. Arena dates
are the dataset's 2026-09-13 publish date. A board with no row date uses the
2026-09-25 observation date.

| Kind | Card and benchmark | #254 value | Source value | Identity and conditions | Date | Verdict |
|---|---|---:|---:|---|---|---|
| Arena | `anthropic/claude-opus-4-6` `arena_elo_style_control` | 1504.56 | 1504.5596374157553 | `claude-opus-4-6-high` in T | 2026-09-13 | correct |
| Arena | `anthropic/claude-fable-5-1` `arena_sc_vision` | 1288.87 | 1288.8665034700095 | `claude-fable-5.1-max` in V | 2026-09-13 | correct |
| Arena | `google/gemini-3-1-pro-preview` `arena_elo_style_control` | 1486.81 | 1486.809321925295 | exact `gemini-3.1-pro-preview` row in T | 2026-09-13 | correct |
| Arena | `moonshot/kimi-k2-6` `arena_sc_vision` | 1262.37 | 1262.369449782495 | exact `kimi-k2.6` row in V | 2026-09-13 | correct |
| Arena | `openai/gpt-6-astra` `arena_elo_style_control` | 1479.77 | 1479.7712562096513 | `gpt-6-astra-max` in T | 2026-09-13 | correct |
| Precision | `anthropic/claude-opus-4-6` `frontiercode_v1_1` | 26.6 | 26.6% | exact `Opus 4.6`, high effort | observed 2026-09-25 | correct |
| Precision | `openai/gpt-6-astra` `frontiercode_v1_1` | 53.3 | 53.3% | exact `GPT-6 Astra`, max effort | observed 2026-09-25 | correct |
| Precision | `deepseek/deepseek-v4-pro` `frontiercode_v1_1` | 17.6 | 17.6% | exact `DeepSeek V4 Pro`. The `0813` row is a sibling | observed 2026-09-25 | correct |
| Precision | `anthropic/claude-opus-5` `osworld_2` | 31.4 | 31.4% | exact `Claude Opus 5`, max effort | observed 2026-09-25 | correct |
| Added | `google/gemini-3-1-pro-preview` `swe_bench_pro` | 46.1 | 46.1 | `gemini-3.1-pro (thinking)*`, mini-swe-agent | row 2026-04-08 | correct |
| Added | `anthropic/claude-opus-4-6` `swe_bench_verified` | 75.6 | 75.6 | exact `Claude 4.6 Opus`, mini-SWE-agent | row 2026-02-17 | correct |
| Added | `anthropic/claude-opus-4-6` `swe_bench_multilingual` | 72.0 | 72.0 | exact `Claude 4.6 Opus`, mini-SWE-agent | row 2026-02-13 | correct |
| Added | `meta/muse-spark-1-3` `cursorbench_4` | 41.6 | 41.6 | exact `Muse Spark 1.3`, max effort | observed 2026-09-25 | correct |

## Kimi K2.6 OSWorld 2 recommendation

Recommend removal, subject to Jamie's decision.

The [Epoch benchmark-data archive](https://epoch.ai/data/benchmark_data.zip),
read on 2026-09-25, contains `Kimi 2.6 (enabled)` at 4.6% and `MiniMax M3
(enabled)` at the same 4.6%. Epoch attributes both rows to the OSWorld site.
The retained [live OSWorld 2 board](https://osworld-v2.xlang.ai/), observed on
2026-09-25 with the release filter set to all, contains MiniMax M3 at 4.6% but
no Kimi 2.6 row.

The card's Kimi row cites the live board but has no filed claim, registered
source snapshot, or successful verification, so it remains in quarantine and
does not enter a snapshot. The permitted primary source does not support the
row. Keeping the row would preserve only a secondary copy whose stated primary
source no longer contains it. Jamie should decide whether that historical clue
is worth retaining in quarantine; this audit recommends removing it.

## Data changes

None. #254 already corrected all 30 errors from #241, and the audited #254
rows match their sources. No claim or verification-log entry was added.
