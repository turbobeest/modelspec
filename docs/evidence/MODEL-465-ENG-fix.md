# MODEL-465-ENG

The weekly price and plan re-read wrote `sources[].retrieved_at` with `datetime.isoformat()`. For a UTC instant that ends in `+00:00`. Loading the fact and dumping it with `model_dump(mode="json")` spells the same instant with a trailing `Z`. `rewrite_fact`, `FactResult.citations`, and `check_value_only` now share `_utc_retrieved_at`, which replaces that suffix. Fractional seconds stay when the instant has them.

`tests/shard_durations.json` is unchanged. No new test module. Frozen public data, ranking floors, legal text, and Worker vars are unchanged. No page was fetched.

Base: `bf74ddf63aedbdfcad947f1d5c40e345c4075fea`. Head is the commit that adds this file. The executor's final line prints `git rev-parse HEAD`.

Tools: Python 3.14.4, pytest 9.1.1, pydantic 2.13.5, PyYAML 6.0.3, git 2.50.1. Pytest uses `/Users/terbeest/dev/modelspec/.venv/bin/python` with `PYTHONPATH` set to this worktree.

## Red

`tests/test_price_reread.py::test_a_cited_rewrite_stamps_retrieved_at_as_utc_z` against the unchanged writer.

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_price_reread.py::test_a_cited_rewrite_stamps_retrieved_at_as_utc_z --tb=short
```

Exit 1. The written value was `2026-11-10T07:45:29.054783+00:00`. The test expected `2026-11-10T07:45:29.054783Z`.

## Green

The same command after the writer change. Exit 0. 1 passed in 0.30s.

A seconds-only UTC datetime and one with microseconds both match `SourceRef.model_dump(mode="json")["retrieved_at"]`. Neither written string contains `+00:00`.

```text
2026-11-10T07:45:29.054783Z 2026-11-10T07:45:29.054783Z True False
2026-11-10T07:45:29Z 2026-11-10T07:45:29Z True False
```

## Focused

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_price_reread.py tests/test_price_reread_fallback.py \
  tests/test_cite_only_retention.py tests/test_cite_only_caller_isolation.py --tb=line
```

Exit 0. 388 passed in 3.17s.

## Not observed

The full public pytest suite. The private data repository's approved-answers check. Any network fetch.

Timestamps already stored with `+00:00` are not rewritten. The next cite-only `--write` emits `Z`. Rows already on disk keep the old spelling until a data change rewrites them.

## Follow-ups

Duplicate collector on a cite-only re-file. `reread_fact` copies the filed claim and replaces only its sources (`claim = replace(claim, sources=pinned)` in `scripts/price_reread.py`). `run` then calls `queue.file(fact.claim, at=at)`, so the new collected event keeps the previous collector. The unchanged path is separate and tested: a reconfirmation keeps that collector (`test_an_unchanged_page_logs_a_dated_reconfirmation_and_edits_no_offering`). Stamping the weekly actor onto a citation the job describes as not machine-verified is not a one-line correction. Left unchanged.
