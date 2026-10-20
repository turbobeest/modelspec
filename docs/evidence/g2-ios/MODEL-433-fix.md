# MODEL-433 execution evidence

The local Chromium renderer executes validated source-registry recipes before
capture. Recipes can click UI controls, select options, scroll, reject consent,
and wait for text. They have at most 16 steps and share one interaction deadline.
An unsuccessful recipe returns an unreachable result with no page bytes.

The interrupted attempt was resumed in the assigned worktree and branch.
Its existing implementation and private scratch artifacts were inspected and
preserved before further changes.

- Pre-feature base: `3c8042a11aa47e8577559e01f71379119bda2cec`.
- Resumed HEAD: `bd38d72e326e3d603a45dac6fc758dc8acfeb324`.
- Final implementation SHA: `8e2cdd8dd5b8e7d21948d3e5fb4d22e9d3fb9a38`.
- The following commit adds execution evidence only. The draft PR records its
  final branch SHA separately.

## Red-first evidence

| Defect | Test boundary | Red | Green |
| --- | --- | --- | --- |
| Registry cannot express pricing interactions; live/replay preparation bypasses them | `test_registry_loads_a_bounded_data_only_recipe`; `test_render_to_and_live_reread_use_the_registry_recipe_for_a_legacy_source` | Reproduced against the pre-feature modules: 2 failed, exit 1 | Included in 339 passing focused tests |
| Popup navigation and form POST escape page-level routing; a blocked POST still yields stale successful HTML | `test_recipe_blocks_requests_from_controls_and_discards_the_capture` | 3 failed, 24 deselected, exit 1 | All three cases pass |
| Treating every aborted request as a failed pricing action rejects identified analytics | `test_recipe_blocks_listed_telemetry_without_discarding_selected_prices`; `test_registry_rejects_ambiguous_telemetry_endpoints` | 5 failed, 7 passed, 27 deselected, exit 1 | All cases pass; unlisted requests and listed navigation still fail closed |

The initial attempt's [inherited red output](MODEL-433/inherited-red.txt)
records 13 failures and nine passes. That original invocation was not observed
in this resumed session. The two registry boundaries were independently rerun
against unchanged modules read from the pre-feature Git revision, without
changing this checkout.

Recorded outputs:

- [Reproduced baseline failures](MODEL-433/baseline-red.txt).
- [Popup and request failures](MODEL-433/requests-red.txt).
- [Telemetry failures](MODEL-433/telemetry-red.txt).
- [Final focused suite with Chromium](MODEL-433/focused-browser.txt).
- [Final focused suite in the required shared environment](MODEL-433/focused-main.txt).
- [Worker bundle tests](MODEL-433/worker-bundle-tests.txt).

The browser regression fixtures intercept every network request. They assert
that forbidden requests never reach the fixture responder, captures fail
closed, and popup pages are closed. The existing tests also cover selector
ambiguity, missing text, the shared deadline, conflicting recipes, prohibited
controls, and consent rejection.

## Final implementation

The request guard uses context routing so it catches the first request of a
popup. It remains active through capture and page closure. Service workers are
disabled. Navigation and unlisted non-GET/HEAD requests abort and invalidate
the result.

A `block_telemetry` step names an exact HTTPS endpoint without credentials,
query, or fragment. Requests to that scheme, host, and path remain aborted;
their query strings do not affect the match. Such blocked analytics do not
invalidate a completed capture. Navigation and form requests remain fatal even
at listed endpoints. There is no global exception for third-party traffic.
Registry authors must correctly identify these endpoints.

Recipes take precedence over legacy preparations. Existing sources with no
recipe keep their previous preparation behavior. Empty recipe fields are
omitted from serialization. The public frozen registry and data remain
unchanged; the AWS and Azure recipes and per-fact results are in the separate
private data draft.

## Commands and versions

Commands ran in `/Users/terbeest/dev/worktrees/model-433` unless shown otherwise.
Tests ran serially with the cache provider disabled.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-433/baseline_red.py
env PYTHONPATH=$PWD /tmp/model-433-scratch/venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rendered_interactions.py -k blocks_requests
env PYTHONPATH=$PWD /tmp/model-433-scratch/venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rendered_interactions.py -k 'listed_telemetry or ambiguous_telemetry'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rendered_interactions.py tests/test_rendered_sources.py tests/test_price_reread.py tests/test_decision_sources.py tests/test_decision_registry.py tests/test_cite_only_retention.py
env PYTHONPATH=$PWD /tmp/model-433-scratch/venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rendered_interactions.py tests/test_rendered_sources.py tests/test_price_reread.py tests/test_decision_sources.py tests/test_decision_registry.py tests/test_cite_only_retention.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --check
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_worker_bundle.py tests/test_worker_vendor_imports.py
git diff --check
```

The final shared-environment suite passed 318 tests and skipped 21 browser
cases because Playwright is absent there. The scratch Playwright environment
passed all 339 tests with no skips. The two Worker bundle files passed seven
tests. Both vendor commands exited 0, generated 129 public bundle files, and
the import check passed with declared dependencies only. `git diff --check`
passed. Red commands intentionally exited 1; green commands exited 0.

| Tool | Version |
| --- | --- |
| Python, both environments | 3.14.4 |
| Shared pytest / Pydantic | 9.1.1 / 2.13.5 |
| Browser-environment pytest / Pydantic | 9.0.3 / 2.13.4 |
| Playwright | 1.63.0 |
| PyYAML / httpx | 6.0.3 / 0.28.1 |
| Node | v22.22.3 at the required executable path |
| Git / GitHub CLI | 2.50.1 / 2.102.0 |

## Private-data run and retention

The existing clone under `/tmp/model-433-scratch/modelspec-data` was reused
at `a6f8fd798d7d6f40b35ed08320796b773f29df9a`. The executor read data#98's
terms audit at `8fb320abf57dddd63bcdd8709b686e8cb7f02080` before retaining
new copies. Hosts classed forbids and absent from the cite-only list were
blocked before fetch. No retention policy was changed.

The focused runner allows only the four audited commercial source hosts,
rejects retained redirects outside that set, and calls `run(..., write=False)`.
A second script diagnoses the ticket's retired claims against the same fresh
copies. Both commands exited 0. SHA-256 comparison confirmed that every
offering and verification file stayed unchanged. Recipes, reproduction
scripts, source hashes, cohort counts, discrepancy candidates, and the
Anthropic/Kimi/Luna diagnosis are retained only in the private data draft.
No raw private data or captured pages are committed here.

The data draft retains its existing engine pin because its workflow requires
pins to belong to public main. Its new recipes require this engine PR to merge
and the data pin to advance before adoption.

## Worker memory

`decision/model.py` is vendored, so the final code was exported with private
data using the deployment's vendor path and a throwaway signing key.
The repository's pinned Pyodide 0.28.3 probe exercised decide, vocabulary,
rank, and policy-check in both periods with a 115 MiB steady-memory ceiling.

| Period | Steady MiB | Peak MiB | Exit |
| --- | ---: | ---: | ---: |
| Current | 104.599373 | 105.422554 | 0 |
| Successor | 103.727020 | 104.974838 | 0 |

Neither final run emitted a warning. These results supersede the preliminary
probe before the telemetry schema was added. Exact commands, source hashes,
runtime dependencies, and limitations are in
[the memory report](MODEL-433/worker-memory.md), with
[current](MODEL-433/memory-current.json) and
[successor](MODEL-433/memory-successor.json) measurements.
The public bundle was re-vendored after the final implementation.

## What was not observed

No live production Worker was measured or deployed. The local probe used
Python 3.14.4 to build, whereas CI builds with 3.13; its measured Pyodide runtime
matches the workflow. No local full suite, WSL gate, paid-provider request,
Firecrawl call, or real-secret operation ran. No forbidden-host response was
observed. Historical value discrepancies do not establish temporal price
changes. CI and independent cross-model review remain pending.

The executor pushes only the assigned branches and opens both PRs as drafts.
No merge or Linear write is part of this execution. Scratch private clones,
captures, and bundles are deleted after the draft PRs are published.
