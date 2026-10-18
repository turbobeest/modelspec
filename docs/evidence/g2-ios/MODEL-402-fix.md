# MODEL-402 execution evidence

The Worker bundle contains a signed current snapshot and one signed successor
when the current snapshot has an expiry. Both come from the same checkout.
The Worker selects the price period on each request using the UTC date. Both signatures must verify before either snapshot
can serve. Exhausted coverage returns `503 no_snapshot`.

The bundle also carries matching successor vocabulary. Dated vocabulary uses
`no-store`, and the response snapshot header comes from that response's body
so another request cannot change it during an awaited billing operation.

Execution stopped at the spec's path restriction. The additive health schema
changes the OpenAPI hash captured in `qa/fixtures/mcp-tools.json`. CI requires
refreshing that capture, which is outside the allowed paths. The spec says to
stop and report if a file outside `api/worker/`, `decision/`, `docs/`, or
`tests/` is needed. That capture remains unchanged. This draft is blocked and
has not passed the required complete suite.

## Revision and review state

- Repository: `turbobeest/modelspec`.
- Worktree: `/Users/terbeest/dev/worktrees/model-402`.
- Branch: `model-402-snapshot-successor`.
- Base: `a551fe82eef93fcb1d4389a435b2f62927d0a25e`.
- First commit: `7075a312`, design only, published as draft PR
  [#813](https://github.com/turbobeest/modelspec/pull/813) before implementation.
- Final implementation commit: `cf7f72cead28e08d1e3152512c3a19202d098de9`. The evidence-only commit follows
  this revision. The completion record reports the final branch SHA, which an
  evidence file cannot contain literally without changing its own commit hash.
- Independent local review found and verified the vocabulary and concurrent
  header fixes. This was a same-model review. Claude Opus cross-model review
  remains pending. The PR stays a draft.

The [design](../../design/snapshot-successor.md) explains why one successor
covers the six-hour deployment schedule and how both expired periods refuse
service. No workflow, ranking code, contract version, legal text, frozen data,
or production switch changed.

## Red-first results

All tests below ran before the corresponding production change. No existing
test was weakened. The new validity exception remains a subclass of the
existing refusal exception, preserving MODEL-394's holder refusal assertions.

| Defect | Red-first tests | Observed red result | Green result |
|---|---|---|---|
| Midnight gap and wrong snapshot reference | `test_keyed_decide_uses_the_correct_price_and_snapshot_at_the_boundary`, four cold/warm and complete/bounded cases | At midnight, status was 503 with `snapshot_refused` instead of 200. | Correct $2/$10 price before midnight, $4/$20 at midnight and one day later; header and body name the selected signed snapshot. |
| Expired coverage error | `test_no_covering_bundled_snapshot_returns_no_snapshot`, two cases; `test_failed_fetched_refresh_cannot_keep_old_prices_but_new_snapshot_restores_service` | Received `snapshot_refused` instead of `no_snapshot`. | Both cases return 503 with `no_snapshot`; a verified refresh restores current prices. |
| Unauthenticated successor ignored | `test_tampered_successor_signature_refuses_the_bundle_before_either_is_used`, two cases | Before the boundary, the primary served 200 despite the corrupt successor. | Both pre-boundary and boundary requests refuse with a signature error and hold no serving snapshot. |
| Missing health metadata | `test_health_selects_the_serving_snapshot_even_before_the_first_decision`, `test_unbounded_snapshot_keeps_the_same_decision_bytes_and_no_successor` | `KeyError: 'decision_snapshot'`. | Cold health and midnight health select the correct snapshot; exhausted coverage reports a null serving ID; undated decision bytes match the original engine output. |
| Missing published health schema | `test_health_contract_adds_optional_snapshot_metadata_with_declared_nullability` | `KeyError: 'decision_snapshot'`. | The new object is optional; its nullable fields are declared from introduction. Existing field ranges and health version 1.0 remain unchanged. |
| Comparison blocked by expired primary | `test_comparison_uses_successor_for_now_and_keeps_historical_prices` | 503 `snapshot_refused`. | The successor answers the current side; the retained historical side keeps its original prices. The test supplies history through the existing retained-history interface. |
| No successor export or embedded blob | `test_export_builds_a_signed_successor_at_the_current_expiry`, `test_bundle_embeds_both_signed_price_snapshots`, `test_vendor_bundle_is_deterministic_with_fixed_date_build_and_keys` | Missing successor file/blob. | Both periods verify HMAC and Ed25519; successor `as_of` equals the primary expiry; repeated fixed-input bundles are byte-identical. |
| Reused output retains obsolete successor | `test_undated_export_removes_a_previously_written_successor` | The old file survived. | Both obsolete successor snapshot and vocabulary are removed; undated export invokes the snapshot builder once. |
| Vocabulary remains pinned to old period | `test_vocabulary_and_pinned_decisions_handover_together`, two response forms; `test_expired_warm_bundle_clears_snapshot_header_and_refuses_vocabulary`; `test_successor_vocabulary_names_its_snapshot_and_reaches_the_bundle` | Dated responses retained `private, max-age=3600`; expired vocabulary returned 200; successor vocabulary file was absent. | Full vocabulary, queried facet values, and decisions pinned to the reloaded ID follow the serving period; expired coverage refuses vocabulary. Queried vocabulary keeps its existing response shape. |
| Future vocabulary evaluates against today's clock | `test_real_vocabulary_builder_can_evaluate_future_price_templates` | `SnapshotError` at `decision/vocabulary.py` when its template evaluation tried to use a future period live. | Build-time template evaluation reads resolved prices; live future and expired decisions still refuse. |
| Concurrent response header names another request's snapshot | `test_each_response_header_keeps_its_own_snapshot_during_concurrent_handover` | Primary body `snap_71375f0b85d48b07` had successor header `snap_31c8f35c2efc0746`. | Both interleaved responses have headers equal to their own body snapshot references. |
| Health I/O crosses the boundary after selection | `test_health_selects_after_metadata_io_crosses_midnight` | The serving ID was null instead of `snap_31c8f35c2efc0746` when the determination read crossed midnight. | Health selects after that read, so it reports the successor's ID and expiry. |

The initial Worker run reported `12 failed in 0.84s`. The initial vendor run
reported `4 failed, 1 passed in 0.48s`. Additional health-schema, vocabulary,
future-template, and concurrent-header runs each failed before their fixes.
Raw failure output is retained beside this report in the ticket evidence
directory.

## Commands and observed validation

Commands below run from the assigned worktree unless a working directory is
stated. Each test's process exit code was checked directly. No test command was
piped through another command.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_snapshot_successor.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_snapshot_successor.py::test_health_contract_adds_optional_snapshot_metadata_with_declared_nullability
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_snapshot_successor.py -k 'vocabulary or expired_warm'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_snapshot_successor.py::test_each_response_header_keeps_its_own_snapshot_during_concurrent_handover
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_snapshot_successor.py::test_health_selects_after_metadata_io_crosses_midnight
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_snapshot_successor.py tests/test_snapshot_successor_vendor.py tests/test_dated_price_serving.py tests/test_decide_snapshot_refresh.py
```

The combined run initially exited 0 with `54 passed in 2.66s`. After the
health I/O regression, the final run exited 0 with `55 passed in 2.99s`. It includes the
existing conditional fetch, stale fallback, expiry during concurrent loading,
and historical comparison regressions from MODEL-394. The new vendor tests
also passed independently, `7 passed in 1.50s`.

The final vendor and private-serving regression exited 0 with `33 passed,
2 deselected in 143.83s`. Its command, plus the earlier interrupted broader
run, are in [vendor-green.txt](MODEL-402/vendor-green.txt). The interrupted
run exited 2 after 15 passing tests, without a test failure. The final focused
run deselected only the two unchanged full public-site build tests; the
required complete suite includes both of them.

The broader Worker run exited 0 with `274 passed, 1 skipped in 121.74s`:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_snapshot_successor.py tests/test_decide_worker.py tests/test_dated_price_serving.py tests/test_decide_snapshot_refresh.py tests/test_rank_worker.py tests/test_hardware_fit_worker.py tests/test_compare_models_worker.py
```

After vocabulary and concurrency changes, a further affected-suite run exited
0 with `280 passed, 1 skipped in 85.37s`:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_worker_compression.py tests/test_vocabulary_search.py tests/test_decide_worker.py tests/test_hardware_fit_worker.py tests/test_compare_models_worker.py
```

The vocabulary and dated-price suites also passed, `114 passed in 1.49s`:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_vocabulary.py tests/test_dated_price_snapshot.py --basetemp docs/evidence/g2-ios/MODEL-402/vendor/pytest-vocabulary-regression
```

OpenAPI regeneration and its subsequent check exited 0:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
git diff --check
```

The browser prerequisite ran first and exited 0 from `web/`:

```sh
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci
```

The required complete suite uses the shared lock:

```sh
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

The required complete suite exited **1** with `15 failed, 11464 passed,
9 skipped, 11 warnings, 12 errors in 1210.76s`. The [complete output](MODEL-402/full-suite.txt)
and [source/exit record](MODEL-402/full-suite-source.txt) are retained. Production
source stayed at `cf7f72ce` throughout the run.

Fourteen failures come from the OpenAPI capture drift, including five
agent-guide cases beyond the nine seen in the two completed CI artifacts.
The remaining failure is the snapshot-header fixture mismatch described below.
All twelve setup errors report a missing `web/dist/decide.html` while preparing
the landing-page browser fixture. `npm ci` had passed, but the browser output
was absent in this local worktree. CI's site builds and four browser gate
configurations passed. No post-stop build or rerun was attempted. The
[triage note](MODEL-402/full-suite-triage.txt) lists every failed/error node ID.
Terminal logs retain their test output with trailing whitespace removed.

Tool versions observed: CPython 3.14.4 in the shared repository environment,
pytest 9.1.1, Ruff 0.16.6, Node v22.22.3, npm 10.9.8, git 2.50.1, gh 2.102.0, and flock
0.4.0. The isolated Worker measurement uses CPython 3.13.15, uv 0.12.19,
workers-py 1.17.4, workers-runtime-sdk 1.9.0, Wrangler 4.139.0, and Pyodide
0.28.3. The measurement retained the rejected attempt with preinstalled uv
0.7.13 and then installed the workflow-pinned version in its own scratch
directory.

## CI failures and stopped work

The [CI evidence](MODEL-402/ci-failures.txt) records ten failed tests in two
completed shards. Nine failures come from the OpenAPI capture drift.
The full recorded/current comparison differs only in the captured OpenAPI
source hash. Tool definitions are unchanged.

The tenth failure is
`tests/test_visit_gate_off.py::test_flag_off_response_equals_main[decide POST]`.
Its expected response in `tests/fixtures/visit_gate_off_main.json` omits the
snapshot header now copied from the response body. The header is
`x-modelspec-snapshot: snapshot-test` in the actual response. No fixture update
or further implementation edit followed discovery of the forbidden QA path.

Both sites, all four human/visit gate browser combinations, Worker bundling,
MCP tests, decision accuracy, data freeze, and release-chart evidence checks
passed in CI at the implementation revision. Two pytest shards failed; another
was still running during evidence capture. These passes do not override the
failed pytest gate. The PR remains a draft, pending scope expansion and the
required corrections, another full run, and independent review.

## Limits and observations

The measurement uses the complete frozen repository fixture with two synthetic
signed validity periods. It does not access the private production checkout.
The [Cloudflare limits](https://developers.cloudflare.com/workers/platform/limits/)
retrieved on 2026-10-17 specify 64 MiB uncompressed per Worker, no compressed
bundle limit, and 128 MB memory per isolate.

The [measurement reproduction note](MODEL-402/measurement/README.md) gives the
fixture, commands, and limitations. The runner uses the real vendor export
from the complete frozen catalogue, then signs two copies with synthetic
validity intervals. The fixture retains all 87 lineup candidates, records,
and both corpus sections. Its archive is empty. Behavior tests separately
exercise real Argon-like schedules.

| Measurement | One snapshot | Current and successor |
|---|---:|---:|
| Uncompressed Worker upload | 9,588.70 KiB | 10,063.47 KiB |
| Gzip upload | 3,011.68 KiB | 3,371.42 KiB |
| Cached steady memory | 103.8691 MiB | 116.3302 MiB |
| Cached peak memory | 104.2697 MiB | 116.7542 MiB |
| Probe exit code | 0 | 0 |

The dual upload totals exactly 10,304,997 bytes, or 15.36% of the current
64 MiB code limit. Its actual dry-run output passes the bundle import check,
with 76 reachable local modules. The cached probe passes the unchanged
120 MiB repository safety threshold and drives current-to-successor handover,
vocabulary, rank, and policy-check with network requests refused by the stub.

An earlier probe downloaded five Pyodide wheels in its measured process and
reported 120.7204 MiB steady, 120.7852 MiB peak, exit 1 at the 120 MiB safety
threshold. That observation used source `ef31a864`. All request assertions
passed. Cached final-source runs passed at 116.3302 and 116.3462 MiB steady.
Wasm allocation was identical in
all dual runs, 71.875 MiB. Setup overhead is an inference from the downloads
and the extra retained non-Wasm memory. The logs preserve the failed
observation, and no threshold or GC policy was changed. Every observed total
remained below 128,000,000 bytes.

Reproduce the measurements with:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-402/measurement/run_measurements.py
/Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-402/measurement/measure_baseline.py
```

The adjacent `commands.json` records the exact child commands and their direct
exit codes, including tooling prerequisite corrections. The upload manifest
records the 351 output files' byte sizes and SHA-256 values. Generated source,
dependencies, and data were removed from the task's scratch directories after
measurement.

No production deployment, real clock rollover, private catalogue size, or
multi-day deployment outage was observed. No paid provider, device, SSH,
Worker upload, Linear mutation, workflow change, or production switch was used.
Historical comparison availability remains governed by the existing retained
history path. Bundling a successor does not add private historical exports.
