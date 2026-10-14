# MODEL-383-build execution evidence

Executed on 2026-10-13 local, 2026-10-14 UTC, in
`/Users/terbeest/dev/worktrees/model-383`, on
`sparksandsawdust/model-383-landing-date`.

Base SHA: `76f3b0735660f1969c5f75cedb3fcf3c29641bf7`.
Implementation SHA: `0579c58dbaf1a1b2d540b5f8633b4367dc514c5c`.
This file is the commit after that SHA.

Tools: Python 3.14.4, pytest 9.1.1, Node v22.22.3.
Interpreter: `/Users/terbeest/dev/modelspec/.venv/bin/python`.

## Change

`pipeline/export.py` `build_day` returns the UTC calendar day of `built_at`.
`pipeline/build.py` `build_site` uses that day for the sitemap default
`lastmod`, coverage, landing data, social cards, competition, and the blog
publication cutoff. `pipeline/build.py` `build_day` calls the export function.

`pipeline/blog.py` `_posts` compares a publication date with the day the site
build passes in. The preview command passes no day, so it uses
`datetime.now(UTC).date()`.

`pipeline/load.py` dates a missing eligibility report with
`datetime.now(timezone.utc).date()`. That date is the eligibility line on a
page when the report file is absent.

`pipeline/render.py` `freshness_notice` counts age from `build_day` when a
build is present, and from `datetime.now(timezone.utc).date()` otherwise.

Left on `date.today()`:

- `pipeline/blog.py` preview command stamps its own `Build` with the local
  day. That command is not the site build.
- `pipeline/live.py` `lastmod` falls back to the local day when git returns
  no date. `blog_sitemap_dates` uses the local day only when a sitemap row
  has no `lastmod`. `live.build` rewrites the sitemap from git dates. The
  failing test lints the `pipeline.build` tree, which includes
  `models/index.html`, so the lint compares sitemap dates with `built_at`.

## Red-first observation

`tests/test_pipeline.py::test_the_build_day_matches_built_at_when_the_local_date_lags`

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_pipeline.py::test_the_build_day_matches_built_at_when_the_local_date_lags --tb=short
```

Exit code 1 before `build_day` existed. `1 failed in 0.21s`.

```
AttributeError: module 'pipeline.build' has no attribute 'build_day'
```

The same test after `build_day` returned `date.today()`, with the local day
patched to 2026-10-13. Exit code 1. `1 failed in 0.22s`.

```
assert datetime.date(2026, 10, 13) == datetime.date(2026, 10, 14)
```

## Green verification

The committed test pins `built_at` to `2026-04-02T01:30:00+00:00` and the
local day to 2026-04-01. Same command. Exit code 0. `1 passed in 0.24s`.

Focused command. The shell had no `TZ`. The system date was 2026-10-13 EDT.
`web/node_modules` and `web/dist` were already present, so this run did not
rebuild the web app.

```sh
TZ=America/New_York PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_ready.py tests/test_landing.py --tb=line
```

Exit code 0. `66 passed in 396.26s`.

Full suite, four workers, `TZ=America/New_York`. Load average was 82.19.
After `sleep 120` the one-minute load was 21.83, and the suite started.

```sh
TZ=America/New_York PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Exit code 0. `10456 passed, 8 skipped, 11 warnings in 1581.50s`.

## Not observed

The full suite was not run under `TZ=UTC`. Linear was not edited. The branch
was not merged. `pipeline/live.py` and the blog preview stamp were not changed.
