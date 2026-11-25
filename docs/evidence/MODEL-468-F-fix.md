# MODEL-468-F absent cache copy

An absent copy is `unreachable` and logged, unless the caller opts in. `StoredRegions` takes `skip_absent_copies` (default false). With the flag, a claim whose cited copy is not in the cache is `skipped`, stays queued, and is not logged. The reason is `no retained copy in this cache: <source>#<region>`.

A corrupt copy, an unregistered source, and an unregistered region stay `unreachable` in both modes. An unreadable citation record is still refused by the cite-only door (`skipped`, not logged) in both modes. That door is unchanged. There is no fetch-failure marker. `decision/sources.py` matches `origin/main`.

`modelspec verify --skip-absent-copies` is off by default. The release-signals step "Validate cards and run two-key verification" is the only workflow step that passes it. That step appends outcome counts to `GITHUB_STEP_SUMMARY`: `verified`, `mismatch`, `unreachable`, `skipped`, and skipped for no copy. Counts only. The human summary prints the no-copy count under `skipped`, not as its own outcome. `verify --json` still includes `skipped_no_copy`.

The process job `timeout-minutes` stays 30.

An evidence reading with no sources is `unreachable` again. The fixture claim whose copy is missing is `unreachable` again. A missing or corrupt xAI copy stays `unreachable`. A deleted architecture config copy stays `unreachable`.

With the flag off, an empty cache logs `unreachable` and the completeness gate quarantines the newer row. With the flag on, the same pending re-collection appends nothing, and the older `verified` row still admits the fact.

A nightly re-check that gets HTTP 200 and cannot retain the body (a text source answering with a PDF) stores no copy. The flag stays off, so the claim stays `unreachable`, is logged, and is re-queued. A `StoredRegions` subclass that pins a failed fetch to an all-zero ref, and does not pass the flag, stays `unreachable`.

## Callers of `verify` / `run`

- `.github/private-writers/release-signals.yml`, step "Validate cards and run two-key verification": opted in
- `cli/modelspec/verify_cmd.py`: unchanged (flag off), unless `--skip-absent-copies` is passed
- `scripts/accuracy.py`: unchanged (flag off)
- `scripts/admission_drafter.py`: unchanged (flag off)
- `scripts/data_trust/sample.py`: unchanged (flag off)
- `scripts/model_163_local.py`: unchanged (flag off)
- `scripts/model_235_recite.py`: unchanged (flag off)
- `scripts/model_348_architecture.py`: unchanged (flag off)
- `scripts/price_reread.py`: unchanged (flag off)
- `scripts/refresh_leaderboards.py`: unchanged (flag off)

No other file under `.github/private-writers/` or `.github/workflows/` passes `--skip-absent-copies`. Tests that call `verify` or `run` leave the flag off, except the opt-in cases named above.

## Checks

Focused serial pytest, no cache provider, exit code read directly: the verify tests, the xAI matrix reader, the architecture extractors, the release-signals workflow tests, the accuracy file, and the snapshot regression. 1277 passed. No full suite. No site build. No live fetch. No Worker deploy, no Linear write, and no merge.
