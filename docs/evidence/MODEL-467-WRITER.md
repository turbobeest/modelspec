# MODEL-467-WRITER

A refreshed Arena row states the reading it was refreshed from. Counts only. No card names and no per-card values.

## Tests

The score-only write, before the matched reading was copied onto the row, left the real verifier at `mismatch` for a refreshed Arena fixture. That case is still asserted by `test_stale_arena_reading_mismatches_without_the_writer_change`.

After the writer, the guard, the all-cards cap, the sentence retell, and the refusal to write a row the verifier would reject:

```sh
env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider tests/test_leaderboard_refresh.py tests/test_arena_revision.py tests/test_model_160_evidence.py
```

Exit 0. 142 passed in 7.98s. Serial, no network.

## Boards

`rating_lower`, `rating_upper`, and `vote_count` are emitted by `project_arena` in `scripts/model_160_evidence.py`. The weekly writer copies interval, vote count, and effort on rows whose benchmark id starts with `arena_`. The historical Arena fillers in `scripts/model_161_data.py` and `scripts/model_191_refinements.py` read the same fields. No other live board projector emits them.

## Live proof

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

The scratch catalogue, the parquet cache, and the recall output were deleted after this file was written. Nothing from that tree was committed or pushed.
