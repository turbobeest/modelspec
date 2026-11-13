# MODEL-477 writer rounding and read date

Two faults in the Arena refresh writer, and the rules that close them. Counts and field names only.

## Rounding

An Arena row whose `benchmark_id` starts with `arena_` and whose `source_url` is the Arena dataset root had its `score` written as the raw float. The writer now stores `round(value, 2)`. That same rounded value is the evidence id, the configuration sentence, `RefreshReport.new_value`, the audit JSON, and the pull-request table. A rounded value equal to the card value, with the same publish date, interval, sample size, and rank, is reconfirmed. A card `score` with more than two decimal places that rounds to the reading is rewritten at two decimals and counted reconfirmed. Any other board keeps the precision it already had.

The verifier accepts that rounded score against the raw dataset value at the existing tolerance. `decision/verify.py` is unchanged.

## Read date

`_retell_reading` retells or removes a stale read date. It does not leave one in place.

When the quoted publish date changes:

- `read <date>` beside that publish date becomes this run's observed date.
- The sentence `The live arena.ai board read <date> still shows this snapshot (same vote counts).` is removed.
- An ISO date that is neither the new publish date nor this run's observed date is not written. The failure reason is `configuration states a date the writer cannot retell`, with the card and the benchmark. Round 2 below states which dates this rule sees.

When the quoted publish date is unchanged, that clause and that sentence stay, and the sentence stays byte for byte apart from figures the writer already retells. A sentence with no publish quote is left, including `observation_fetch_date`.

`check_score_only` accepts those two edits on an Arena dataset-root row. A changed word elsewhere still fails. Removing the snapshot sentence while the publish date stays also fails.

## Shape table

Public arena rows in this repository: 3378. Dataset-root rows: 3368. Rows off that root: 10. Distinct configuration skeletons after dates, numbers, and hex are masked: 132. Each skeleton is one class below. The date settlement ran after the publish-date and `Observed` substitutions. An unchanged quoted publish date mutated 0 sentences.

| Class | Rows | Quoted publish date changes |
|---|---:|---|
| Publish date only | 2995 | Retell the publish date. Write. |
| Publish date and `Observed` date | 284 | Retell both dates. Write. |
| Blank configuration | 40 | Write. |
| `read <date>` beside the publish date | 11 | Retell that read date to the observed date. Write. |
| Snapshot sentence | 20 | Remove that sentence. Write. |
| `dataset re-read <date>` | 18 | Refuse. Reason: `configuration states a date the writer cannot retell`. |
| Off root, `observation_fetch_date`, no publish quote | 10 | Leave the sentence. The date check does not run. |

The `dataset re-read` class is refused only when the quoted publish date changes. An unchanged publish date keeps that sentence apart from figures.

The refresh tests cover the publish-and-`Observed` sentence, both read-date shapes, a third date, an unchanged publish date, a raw card score repaired as a reconfirmation, and a non-Arena score left at its own precision.

## Tests

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_leaderboard_refresh.py tests/test_writer_isolation.py
```

Exit 0. 411 passed in 16.31s. Serial, no network. `tests/test_arena_revision.py` on the same writer: exit 0, included in a combined run of 476 passed in 16.26s.

## Round 2

Review fixes on draft pull request 1062. The branch started at `148f1c82`. `origin/main` was merged as `f5c0b722` before these fixes.

### Added rows

`_new_evidence` stores an Arena dataset-root `score` with the same `round(value, 2)` a refresh uses, and hashes the evidence id from that score. Before that helper, an added row for raw rating 1210.256789 stored 1210.256789. After it, the card stores 1210.26, the id differs from the id of the raw score, and the next refresh of the same reading reconfirms the row. Some added rows already hold the raw float. The next refresh rewrites them at two decimals and counts them reconfirmed. The evidence id changes because the stored score changed. That is intended. A non-Arena added row keeps its precision.

### Standalone dates

Only a standalone ISO date is a date the writer cannot retell. A date glued to a letter, digit, hyphen, slash, or underscore is part of a longer token. A dot that continues a token is too, as in `file.2024-08-06` or `2024-08-06.txt`. A sentence period still bounds a date, so `noted 2026-08-01.` is still refused. A date inside a backticked span or a URL is left byte for byte. The writer and `check_score_only` use that same set. An unchanged id that contains a date does not fail the guard. Changing that id does, including when the new suffix is one of the row's dates.

A date after the standalone word `read` may change only to the row's `observed_at`. `re-read` is not that word. Any other changed date may become `evidence_date`, `observed_at`, or `verified_at`. Before this rule, the guard accepted a read date changed to `evidence_date`. Existing guard tests kept their outcomes after the rule.

`check_score_only` accepts the read-date retelling and the snapshot-sentence removal on an Arena dataset-root row. The same edits fail on a non-Arena row and on an Arena row whose `source_url` is not the dataset root. The sentence left after the snapshot sentence is removed is asserted in full.

### What a person sees

Refusals whose reason is `configuration states a date the writer cannot retell` are listed under `## Dates the writer cannot retell`, with the count, the card, and the benchmark. The report and a pull-request body that is over the length limit both keep that section. The section includes this sentence. These rows need a person to rewrite the sentence; they will not refresh until then.

The class counts above were not re-counted. The 18 `dataset re-read` rows stay in that section when the quoted publish date changes.

### Tests

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_leaderboard_refresh.py tests/test_writer_isolation.py tests/test_arena_revision.py
```

Exit 0. 487 passed in 15.89s. Serial, no network.

Not observed here: a live weekly run, and the pull-request checks. Those checks are read after the push. The fixture rating is `1234.5678912345`, rounded to `1234.57`. The previous raw digits are gone from the tests and from this note.
