# MODEL-467-ENG

Base `18c7c31902cc745c076220890f5891cbdf935559`, even with `origin/main`.
Part A, the Arena revision resolver, is `7b914a3c9c2c04b4bfc7ef16556dbfa3f4b99c46`.
The design and this file are the following commit on `model-467-eng`.

Environment: Python 3.14.4, pytest 9.1.1, PyYAML 6.0.3, pyarrow 25.0.1,
Git 2.50.1, GitHub CLI 2.103.3. Tests are serial and offline.

## Red, then green

`tests/test_arena_revision.py` was run against the unchanged tree.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_arena_revision.py
```

Exit 1. `15 failed, 1 passed`. The failures are `AttributeError` for
`resolve_arena_revision` and `choose_arena_revision`, `KeyError: arena_latest`,
`SystemExit: 2` on the unknown `--arena-latest` argument, and `TypeError`
because `collect_readings` took 3 arguments. The passing test is
`test_collect_without_a_revision_stays_on_the_pin`, which already matched the
pinned URL.

After the resolver and the flag:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_arena_revision.py
```

Exit 0. `16 passed`.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_leaderboard_refresh.py tests/test_model_160_evidence.py
```

Exit 0. `64 passed`.

## What the flag does

`ARENA_REVISION` stays `1880dbebff5ba3e2dd3865ecf6fc43539c2099db`.
`--arena-latest` reads `sha` from
`https://huggingface.co/api/datasets/lmarena-ai/leaderboard-dataset`.
The sha must be 40 lowercase hex characters. Any other response, or a network
error, keeps the pin, names the reason in the report, and lets the run finish.
Without the flag the resolver is not called. The fetch URL for each Arena
config contains the revision that run read, and that URL is the source on the
rewritten-row report. The weekly workflow file does not pass the flag, so a
Monday run stays on the pin until the invocation adds it.

## Live read

One probe, four HTTPS requests to huggingface.co, nothing written into the
catalogue or the copy store. Each request returned 200.

| Request | Bytes |
|---|---:|
| `https://huggingface.co/api/datasets/lmarena-ai/leaderboard-dataset` | 22695 |
| `.../resolve/4217986c2fa1163d072e7a3dda637bb56cce8d79/text/latest-00000-of-00001.parquet` | 626995 |
| `.../resolve/4217986c2fa1163d072e7a3dda637bb56cce8d79/vision/latest-00000-of-00001.parquet` | 64607 |
| `.../resolve/4217986c2fa1163d072e7a3dda637bb56cce8d79/webdev/latest-00000-of-00001.parquet` | 31920 |

The dataset prefix on the three parquet URLs is
`https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset`.

Revision `4217986c2fa1163d072e7a3dda637bb56cce8d79`. `lastModified` on that
API response is `2026-11-11T04:01:46.000Z`. Fallback was not used.

| Config | Parquet rows | `overall` rows the reader keeps | Board publish date |
|---|---:|---:|---|
| text | 11175 | 421 | 2026-11-09 |
| vision | 1161 | 167 | 2026-11-09 |
| webdev | 672 | 156 | 2026-11-10 |

`project_arena` for category `overall` kept the same counts. The projection
`source_url` is the resolve URL above.

## Part B

`docs/design/first-row-filing.md` is design only, 86 lines. No filing code
was added.

## Shard timings

`tests/test_arena_revision.py` had no row in `tests/shard_durations.json`.
`test_shard_timings_cover_the_current_suite_and_browser_modules` then saw
362 of 382 modules, under the 0.95 gate. A serial JUnit run of that file,
read by `durations_from_junit` in `scripts/refresh_shard_durations.py`,
recorded 0.011 seconds. That one row was inserted. The other rows stayed.

## Not run

No full local suite, site build, Worker memory probe, or workflow edit.
No ranking floor, legal text, contract, frozen data file, or source-terms
class was changed. `scripts/premier_slice1.py` and `scripts/premier_live.py`
were not changed.

## Round 2

Merged `origin/main` (`101a9eed`) before the review fixes. The parent of
those fixes is `fe09be2d`.

### One setting

`tests/test_arena_revision.py` against the unchanged resolver, the new tests
only. Exit 1. `5 failed, 2 passed`. A release-signal refresh with
`MODELSPEC_ARENA_REVISION=latest` still read the pin. `head` did not raise.
The weekly workflow file had no `MODELSPEC_ARENA_REVISION`. The CLI without
`--arena-latest` passed `arena_latest=False`.

After `arena_revision_setting` and the workflow variable:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_arena_revision.py
```

Exit 0. `22 passed`. An explicit argument wins. Unset or empty stays on the
pin. `latest` reads the head. Any other value raises `ValueError` and the
message names `MODELSPEC_ARENA_REVISION`. The weekly file sets the variable
to `pinned` and does not pass `--arena-latest`.

### Registry citation

`test_latest_mode_writes_no_arena_rows_when_the_registry_cites_another_revision`
against the unchanged writer. Exit 1. The failure list did not mention the
registry, so the run still wrote the Arena rows.

`registry_revision_conflict` then refuses every Arena row in `latest` mode
when a cited source URL contains a commit SHA other than the revision that
was read. A URL with no SHA is written. The one failure names the source
ids. The same file after that change:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_arena_revision.py
```

Exit 0. `24 passed`. `registry/sources.yaml` was not edited.

### One revision for every Arena config

The three new tests against the per-config reader. Exit 1. `2 failed, 1 passed`.
A resolver fallback was not a failure row. A missing `document` config at
head was not re-read at the pin, and the configs that were present stayed on
the head revision. The all-seven read already passed.

`latest` mode now fetches every Arena config before it projects. When any
required config is missing and the resolved revision is not the pin, that
revision is not projected. Every Arena config is read at the pin, and one
`config fallback:` failure names the missing configs. A resolver fallback is
also a failure row, and the summary line `fallback to the pinned default`
stays. The report revision, and the registry comparison, are the revision
that was read.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_arena_revision.py
```

Exit 0. `27 passed`.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_leaderboard_refresh.py tests/test_model_160_evidence.py tests/test_release_signals.py
```

Exit 0. `236 passed`. Callers that replace `collect_readings` now accept the
`arena_complete` keyword `run` passes.

### Seven configs at head

One dry run on 2026-11-11 with `MODELSPEC_ARENA_REVISION=latest`. The reader
is `refresh_leaderboards.run` with an empty scratch root, `dry_run=True`, and
a scratch copy cache. A fetch whose host is not huggingface.co fails before
the request. The catalogue was not written.

Eight HTTPS requests, each status 200. No ninth request. No fallback.

| Request | Bytes |
|---|---:|
| `https://huggingface.co/api/datasets/lmarena-ai/leaderboard-dataset` | 22695 |
| `.../resolve/4217986c2fa1163d072e7a3dda637bb56cce8d79/document/latest-00000-of-00001.parquet` | 7637 |
| `.../resolve/4217986c2fa1163d072e7a3dda637bb56cce8d79/text/latest-00000-of-00001.parquet` | 626995 |
| `.../resolve/4217986c2fa1163d072e7a3dda637bb56cce8d79/text_factuality/latest-00000-of-00001.parquet` | 211644 |
| `.../resolve/4217986c2fa1163d072e7a3dda637bb56cce8d79/text_style_control/latest-00000-of-00001.parquet` | 627640 |
| `.../resolve/4217986c2fa1163d072e7a3dda637bb56cce8d79/vision/latest-00000-of-00001.parquet` | 64607 |
| `.../resolve/4217986c2fa1163d072e7a3dda637bb56cce8d79/vision_style_control/latest-00000-of-00001.parquet` | 64600 |
| `.../resolve/4217986c2fa1163d072e7a3dda637bb56cce8d79/webdev/latest-00000-of-00001.parquet` | 31920 |

The dataset prefix on the parquet URLs is
`https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset`.

Revision `4217986c2fa1163d072e7a3dda637bb56cce8d79`. `lastModified` is
`2026-11-11T04:01:46.000Z`.

| Config | At head | Parquet rows | Overall rows the reader keeps | Publish date |
|---|---|---:|---:|---|
| document | present | 46 | 46 | 2026-11-09 |
| text | present | 11175 | 421 | 2026-11-09 |
| text_factuality | present | 4079 | 190 | 2026-11-09 |
| text_style_control | present | 11175 | 421 | 2026-11-09 |
| vision | present | 1161 | 167 | 2026-11-09 |
| vision_style_control | present | 1161 | 167 | 2026-11-09 |
| webdev | present | 672 | 156 | 2026-11-10 |

A latest run against this repository's frozen `registry/sources.yaml` still
writes no Arena rows. Those source URLs name the pin
`1880dbebff5ba3e2dd3865ecf6fc43539c2099db`, which is not the revision above.
The weekly workflow stays on `pinned`. The proof used a scratch root, so it
did not load that registry.
`test_latest_mode_writes_no_arena_rows_when_the_registry_cites_another_revision`
covers the refusal.
