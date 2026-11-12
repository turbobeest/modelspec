# MODEL-467-WRITER

A refreshed Arena row states the reading it was refreshed from. Counts only. No card names and no per-card values.

## Tests

A score-only Arena rewrite, with the matched reading left uncopied, is refused before the row is written. `test_a_score_only_rewrite_is_refused_before_it_is_written` asserts that the card score stays, the failure reason starts with `verifier:`, and no verification log is written.

After the writer, the guard, the whole-board cap, the sentence retell, and the verifier dry run:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_leaderboard_refresh.py tests/test_arena_revision.py tests/test_model_160_evidence.py
```

Exit 0. 157 passed in 8.61s. Serial, no network.

## Boards

`rating_lower`, `rating_upper`, and `vote_count` are emitted by `project_arena` in `scripts/model_160_evidence.py`. The weekly writer copies the matched reading only for Arena boards, and only onto rows whose source URL is the Arena dataset root `https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset`. Non-Arena boards are not copied. The historical Arena fillers in `scripts/model_161_data.py` and `scripts/model_191_refinements.py` read the same fields. No other live board projector emits them.

A hyphen is not an effort separator. `example-model-high` names no effort, and `test_a_hyphenated_dataset_name_keeps_null_effort` keeps effort null and verifies the row. On the round 2 catalogue, effort changed on 2 of 2289 rewritten rows.

## Round 1 live proof

Scratch catalogue, engine at this branch, private data at `origin/main`, `MODELSPEC_ARENA_REVISION=latest`, observation date 2026-11-12. Eight HTTP requests, all to huggingface.co for `lmarena-ai/leaderboard-dataset`, dataset revision `e69cdc26eb7af798d9628215ce45ce353e66d26a`. Later runs reused that cache and made no further requests.

1. `https://huggingface.co/api/datasets/lmarena-ai/leaderboard-dataset`
2. `document/latest-00000-of-00001.parquet`
3. `text/latest-00000-of-00001.parquet`
4. `text_factuality/latest-00000-of-00001.parquet`
5. `text_style_control/latest-00000-of-00001.parquet`
6. `vision/latest-00000-of-00001.parquet`
7. `vision_style_control/latest-00000-of-00001.parquet`
8. `webdev/latest-00000-of-00001.parquet`

Paths 2–8 are under `https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/e69cdc26eb7af798d9628215ce45ce353e66d26a/`. The proof wrapper refused every other host, so non-Arena boards are counted below as not read. The verifier was not changed.

First run, before a quoted interval could be rewritten from the sentence alone: 47 Arena rows written, 47 verified, 0 mismatch. 3115 rows were not written because the configuration still quoted the previous interval and vote count. Those quotes were the only copy of the interval and the vote count; both card fields were empty.

Second run, after that retell: 1200 Arena rows written, 1130 verified, 56 mismatch, 14 other quarantines, 1962 Arena rows left. Every mismatch carried a score diff. Field counts on those records: unit 63, score 56, interval 39, n 39, effort 2. The effort pair was a set card effort against a dataset name the verifier reads as no effort. The 14 other quarantines were `skipped`.

Third run, after the writer refuses a row the verifier would not accept. Same cache, same cap of 1200.

| Outcome | Count |
|---|---:|
| Arena rows written | 1200 |
| verified | 1200 |
| mismatch | 0 |
| other quarantine | 0 |
| Arena rows left | 1876 |

Rows not written, by reason:

| Reason | Count |
|---|---:|
| no unique dataset row | 154 |
| matched row is not a row the verifier reads | 60 |
| effort the card and the dataset do not share | 33 |
| board not read in this proof | 34 |
| rating does not agree in the card's unit | 26 |

Recall on that catalogue, date 2026-11-12, against the approved baseline already on `origin/main`: pass 16 (Q01, Q02, Q03, Q04, Q05, Q06, Q08, Q09, Q12, Q13, Q14, Q15, Q16, Q18, Q19, Q20), partial 4 (Q07, Q10, Q11, Q17), fail 0. Regression question ids: none. The baseline was not re-approved.

## Round 2 review

The writer does not write `benchmark_version`. In both revision modes, before any Arena row is written, a planned rewrite whose `benchmark_version` names a dataset revision different from the revision read blocks every Arena write. The run reports one failure, `the cards' benchmark_version still names a revision`, and the count. A version with no revision proceeds. The revision that was read stays in the source snapshot, the audit record, and a configuration sentence that already quotes a revision.

Latest mode with no explicit model selection and no resolver fallback includes every catalogue row on each real Arena board, premier and non-premier. `_moving_arena_benchmarks` is not that inclusion rule. It ignores `benchmark_version`, and it ignores `arena_*` ids that are not in `ARENA_BOARDS`. Those rows are reported once as `arena_rows_without_board`. Pinned mode and an explicit model selection do not expand.

Each Arena board is written whole or left whole. Boards are ordered by the oldest stored `observed_at`, missing dates first, then by board key. `ARENA_ROWS_PER_RUN` is 5000 and counts rows actually rewritten, not reconfirmations. When the next whole board would pass the cap, that board and every later board wait. `arena_rows_left` counts rows on boards left whole. Skips and the revision gate are not counted.

## Round 2 live proof

Same scratch shape as round 1. Engine at this branch, private data at `origin/main`, latest mode, observation date 2026-11-12, dataset revision `e69cdc26eb7af798d9628215ce45ce353e66d26a`. Eight huggingface.co requests, the same eight URLs as round 1. The second run reused an in-process cache and added zero requests. The wrapper refused every other host.

First run, before any revision quote was removed. Fallback null. Arena score changes 0. Rows added 0. Quarantined 0. `arena_rows_left` 0. `arena_rows_without_board` 19. One gate failure: `the cards' benchmark_version still names a revision (2240)`. Other failures: not_read 34. The 2240 count is planned would-be writes whose version names a different revision. It is not the count of every stored quote.

The scratch copy then stripped the revision quote from `benchmark_version`, including folded continuation lines indented under that key. The edit ran only inside an evidence item whose `benchmark_id` starts with `arena_` and whose `source_url`, after a trailing slash is removed, is the Arena dataset root. The substitution was `,?\s*revision\s+[0-9a-fA-F]{7,40}\b`. It removed 3279 quotes. Stored ids, computed `evidence_id`, and `value_hash` of `evidence_verification_value` were unchanged on every evidence row. The strip did not change score, interval, n, effort, configuration, `benchmark_id`, or `source_url`. After the writer ran, a comparison with the clone HEAD found no `benchmark_version` edit beyond that quote removal.

Second run, same process and the same cache. Latest true. Fallback null. The gate did not fire.

| Outcome | Count |
|---|---:|
| Arena rows rewritten | 2289 |
| reconfirmed | 0 |
| left | 0 |
| added | 0 |
| quarantined | 0 |
| writer score changes | 2271 |
| effort changed | 2 |
| verified | 2289 |
| mismatch | 0 |
| rewritten rows with no new verification log row | 0 |

No board's planned rewrites exceeded 5000. The largest board planned 140. Every collected board was written whole, and planned rewrites equalled rows rewritten on each board. `arena_rows_left` is 0. `arena_rows_without_board` is 19.

The second run skipped 1094 rows. The class split recorded for that run was mislabelled. The classifier treated the substring `unit` as the class, and the verifier uses that word for any numeric disagreement whose unit string is not byte-equal to the canonical id. The proof output was deleted with the scratch catalogue, so this file does not give a corrected split. The withdrawn labels were configuration 50, no-unique-row 154, not_read 34, unit 364, and verifier 492. The skipped column is the row count for that board. The 34 `not_read` rows sit outside the table. The table sums to 1060.

| Board | Rewritten | Reconfirmed | Left | Skipped |
|---|---:|---:|---:|---:|
| `arena_elo_coding` | 1 | 0 | 0 | 18 |
| `arena_elo_overall` | 2 | 0 | 0 | 20 |
| `arena_elo_style_control` | 140 | 0 | 0 | 50 |
| `arena_elo_vision` | 3 | 0 | 0 | 1 |
| `arena_sc_business` | 140 | 0 | 0 | 50 |
| `arena_sc_chinese` | 8 | 0 | 0 | 14 |
| `arena_sc_coding` | 139 | 0 | 0 | 51 |
| `arena_sc_creative_writing` | 139 | 0 | 0 | 51 |
| `arena_sc_document` | 5 | 0 | 0 | 9 |
| `arena_sc_english` | 7 | 0 | 0 | 16 |
| `arena_sc_expert` | 132 | 0 | 0 | 49 |
| `arena_sc_factuality` | 6 | 0 | 0 | 15 |
| `arena_sc_french` | 8 | 0 | 0 | 12 |
| `arena_sc_german` | 8 | 0 | 0 | 10 |
| `arena_sc_hard_prompts` | 140 | 0 | 0 | 50 |
| `arena_sc_industry_entertainment_sports_media` | 7 | 0 | 0 | 16 |
| `arena_sc_industry_mathematical` | 8 | 0 | 0 | 14 |
| `arena_sc_industry_software_it_services` | 8 | 0 | 0 | 15 |
| `arena_sc_instruction_following` | 139 | 0 | 0 | 51 |
| `arena_sc_japanese` | 6 | 0 | 0 | 11 |
| `arena_sc_korean` | 8 | 0 | 0 | 10 |
| `arena_sc_legal` | 134 | 0 | 0 | 50 |
| `arena_sc_longer_query` | 138 | 0 | 0 | 51 |
| `arena_sc_math` | 134 | 0 | 0 | 47 |
| `arena_sc_medicine` | 133 | 0 | 0 | 50 |
| `arena_sc_multi_turn` | 139 | 0 | 0 | 51 |
| `arena_sc_non_english` | 139 | 0 | 0 | 51 |
| `arena_sc_polish` | 7 | 0 | 0 | 10 |
| `arena_sc_russian` | 8 | 0 | 0 | 15 |
| `arena_sc_science` | 139 | 0 | 0 | 51 |
| `arena_sc_spanish` | 7 | 0 | 0 | 11 |
| `arena_sc_vision` | 51 | 0 | 0 | 32 |
| `arena_sc_vision_diagram` | 5 | 0 | 0 | 10 |
| `arena_sc_vision_homework` | 5 | 0 | 0 | 9 |
| `arena_sc_vision_ocr` | 4 | 0 | 0 | 11 |
| `arena_sc_writing` | 140 | 0 | 0 | 50 |
| `arena_webdev` | 52 | 0 | 0 | 28 |

After that run, 39 Arena benchmark ids were present. The most distinct `benchmark_version` strings on one id was 2. The most capability items with at least two models on one id was 2. The writer added no version string.

These 20 ids already had two version strings after the quote was removed: `arena_elo_overall`, `arena_elo_style_control`, `arena_elo_vision`, `arena_sc_chinese`, `arena_sc_english`, `arena_sc_factuality`, `arena_sc_french`, `arena_sc_german`, `arena_sc_industry_entertainment_sports_media`, `arena_sc_industry_mathematical`, `arena_sc_industry_software_it_services`, `arena_sc_japanese`, `arena_sc_korean`, `arena_sc_polish`, `arena_sc_russian`, `arena_sc_spanish`, `arena_sc_vision_diagram`, `arena_sc_vision_homework`, `arena_sc_vision_ocr`, `arena_webdev`.

These 15 of them have two items with at least two models: `arena_elo_overall`, `arena_elo_style_control`, `arena_sc_chinese`, `arena_sc_english`, `arena_sc_french`, `arena_sc_german`, `arena_sc_industry_entertainment_sports_media`, `arena_sc_industry_mathematical`, `arena_sc_industry_software_it_services`, `arena_sc_japanese`, `arena_sc_korean`, `arena_sc_polish`, `arena_sc_russian`, `arena_sc_spanish`, `arena_webdev`.

The other five have a second version string with fewer than two models, so that item is dropped. `decision/capability.py` was not edited. The writer cannot collapse those strings, because it does not write `benchmark_version`.

Recall on the refreshed catalogue, date 2026-11-12, against the approved baseline on `origin/main`: pass 16 (Q01, Q02, Q03, Q04, Q05, Q06, Q08, Q09, Q12, Q13, Q14, Q15, Q16, Q18, Q19, Q20), partial 4 (Q07, Q10, Q11, Q17), fail 0. Regression question ids: none. The baseline was not re-approved.

The scratch catalogue, the parquet cache, and the recall output were deleted after this file was written. Nothing from that tree was committed or pushed.
