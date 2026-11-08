# MODEL-438 execution evidence

Executed on 2026-10-21 in `/Users/terbeest/dev/worktrees/model-438`, branch
`model-438-recipe-followups`. All pytest commands ran serially with browser tests
enabled in `/tmp/model-438-scratch/venv`.

Engine base SHA: `9f280970f83e0530782516890e5d4345ce590053`.
Final implementation SHA: `5eefeefa85a26ac59754210270a3cfaec00a1fbb`.
The subsequent commit adds only this evidence file; its final SHA is recorded in
the PR body and executor completion marker.

Private data final SHA: `bc6fb0a9319f020b6a86f0c8430190884b83a8e0`.
Its branch has the same name and is stacked on data PR #116,
`model-433-interactive-pricing`. Red tests used base
`3c1d517511db40fb0d6de241804b8cc3802a7c43`. During execution, #116 advanced to
`b46b859efda086a4b4a77a8dacc5cfa86f3398e8`, deleting two old research scripts and
updating their report. The follow-up was fast-forwarded to that disjoint change
before its final 66-test validation.

The private clone was isolated under `/tmp/model-438-scratch/modelspec-data`.
No private registry, facts, snapshots, or page bytes were copied into this repo.

## Changes and red-first results

| Defect | Regression and observed red result | Final behavior and green evidence |
| --- | --- | --- |
| Weekly default-state verification | `test_recipe_sources_and_their_aliases_never_get_default_state_verification[False/True]`: 2 failed, 46 deselected, exit 1. The fake client fetched `/page/0`, the recipe URL, in addition to the ordinary `/page/1`. | Recipe URLs and canonical aliases are omitted, reported as covered by the price re-read's recipe path, and retired from stale weekly state. Verification records remain unchanged. Private final suite: 66 passed, 0 skipped. |
| Popup cleanup | `test_recipe_closes_a_popup_created_while_the_capture_page_is_closing`: 1 failed, exit 1, against the original guard. `assert opened_pages[1].is_closed()` was false when `unroute()` began. | Page events close new pages; pending initial navigation requests are resolved to their pages before the route guard is removed. One cleanup deadline bounds the wait. Focused popup suite: 9 passed, 0 skipped. Ten serial repetitions of the two flaky cases: 20 passed, 0 skipped. |
| Unsafe control names | `test_recipe_refuses_unsafe_accessible_names` failed all 9 combinations of name source and unsafe action. The consent cookie had been set. `test_recipe_checks_computed_name_when_rejecting_consent` also returned `ok` for the unsafe name. | Playwright checks the computed accessible name. Visible text, value, title, raw label, and image alt are also checked independently. All 83 interaction tests passed in the combined run, with no browser skips. |
| Stale Azure tables | `test_azure_recipe_waits_for_delayed_region_table_content` failed for each of three tables delayed by 300 ms: only 2 of 3 tables had updated. Public Azure red: 13 failed, 3 passed. Private registered-recipe red: 3 failed, 3 passed. | A guarded postcondition checks every displayed USD cell against the East US regional metadata, after applying Azure's display rounding. Missing, malformed, stale, or incorrectly selected data returns no capture. Final Azure focused run: 21 passed, 0 skipped. |

The first popup test fixture used a close-event callback that completed outside
the guarded window. That fixture was discarded. The retained regression wraps
the real Playwright `Page.close()`, creates and observes a real Chromium popup
before the wrapper returns, and checks closure at the `unroute()` boundary.
It also verifies that an existing page survives normal cleanup.

A page listener plus a snapshot of `context.pages` was insufficient. The real
`listed-navigation` case still failed once, leaving `chrome-error://chromewebdata/`
open. That run reported `1 failed, 8 passed, 69 deselected`. The final guard tracks
initial navigation requests whose `request.frame.page` is not yet available and
waits for their page registration while routing remains protected. Cleanup errors
close the context and fail closed. The actual cleanup-timeout path was not forced
in a real browser test.

Computed accessible names can concatenate adjacent text and image alt text.
The intermediate computed-name-only change still failed the three image-alt
probes. Checking image labels separately resolved that case without weakening
the tests. The implementation uses Playwright's public
[accessible-name assertions](https://playwright.dev/python/docs/api/class-locatorassertions#locator-assertions-to-have-accessible-name).

An initial exact-number Azure predicate passed synthetic fixtures but timed out
against the live page. Its first-party
[pricing formatter](https://azure.microsoft.com/cdn-classic/cvt-92e6c8a972b2f733b1ce8cefffffc67f4568f7606b5be84e6316aa1ccdbbfcff/dest/bundles/pricing-layout.js)
rounds upward at `data-decimals`, default four, after normalizing the scaled
number to 15 significant digits. A precision regression then reported
`4 failed, 1 passed, 78 deselected`, including a value that distinguishes ceiling
from nearest rounding. Matching that rule made all 21 Azure cases pass. A final
in-memory live probe returned `azure_selected_region_prices_match=True`, exit 0.
Raw page and JavaScript bytes were never written. Identical prices in two regions
prove numeric consistency with the selected region, not that a recomputation
occurred.

## Commands and results

Setup and versions:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python -m venv --system-site-packages /tmp/model-438-scratch/venv
/tmp/model-438-scratch/venv/bin/python -m pip install 'playwright==1.63.0'
/tmp/model-438-scratch/venv/bin/python -m playwright install chromium
```

Python 3.14.4; pytest 9.0.3; Playwright 1.63.0; Chromium 153.0.8010.12;
pydantic 2.13.4; PyYAML 6.0.3; httpx 0.28.1; greenlet 3.5.6;
Git 2.50.1; GitHub CLI 2.102.0; actionlint 1.7.12. Node 22.22.3 was selected
from `/Users/terbeest/.nvm/versions/node/v22.22.3/bin` for the scratch dependency
installation. No Node application code changed. The scratch environment had no
ruff module; no Python lint success is claimed.

Public red and focused commands, from the engine worktree:

```sh
env PYTHONPATH=$PWD /tmp/model-438-scratch/venv/bin/python -m pytest -q -p no:cacheprovider --tb=short tests/test_rendered_interactions.py -k 'unsafe_accessible_names or computed_name or popup_created_while'
env PYTHONPATH=$PWD /tmp/model-438-scratch/venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rendered_interactions.py::test_recipe_closes_a_popup_created_while_the_capture_page_is_closing
env PYTHONPATH=$PWD /tmp/model-438-scratch/venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rendered_interactions.py -k 'closes_a_popup or blocks_requests_from_controls or blocks_listed_telemetry'
env PYTHONPATH=$PWD /tmp/model-438-scratch/venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rendered_interactions.py -k azure_recipe
env PYTHONPATH=$PWD /tmp/model-438-scratch/venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rendered_interactions.py -k declared_display_precision
```

The first command produced `11 failed, 2 passed, 49 deselected`, including the
discarded popup fixture described above. The corrected popup red was recorded
separately. The final popup subset returned `9 passed, 69 deselected in 5.71s`.
The final Azure subset returned `21 passed, 62 deselected in 17.95s`.

The popup stress run used this driver. Every child exit code was checked directly:

```sh
env PYTHONPATH=$PWD /tmp/model-438-scratch/venv/bin/python - <<'PY'
import subprocess
import sys
args = [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider',
        'tests/test_rendered_interactions.py', '-k', 'listed-navigation or listed-form-post']
for attempt in range(1, 11):
    result = subprocess.run(args, capture_output=True, text=True)
    print(f'Run {attempt}/10: exit {result.returncode}')
    print(result.stdout, end='')
    print(result.stderr, end='')
    if result.returncode:
        sys.exit(result.returncode)
PY
```

All ten runs exited 0, each with `2 passed` and no skips.

The combined public command was:

```sh
env PYTHONPATH=$PWD /tmp/model-438-scratch/venv/bin/python -m pytest -q -p no:cacheprovider -rs tests/test_rendered_interactions.py tests/test_rendered_sources.py tests/test_price_reread_fallback.py tests/test_price_reread.py tests/test_decision_sources.py tests/test_cite_only_retention.py tests/test_ci_workflows.py tests/test_workflow_dependencies.py tests/test_removed_sources.py
```

It returned `1 failed, 592 passed, 1 skipped in 174.02s`, exit 1. The sole failure
was `test_every_module_a_workflow_runs_has_its_imports_installed[test.yml:pytest-shards]`.
The dependency checker rejects `pip install -r`; the workflow now declares
`playwright==1.63.0` inline. The checker and its tests were unchanged. The only
skip was `test_a_built_dist_carries_no_removed_value`, which requires
`MODELSPEC_DIST` to point at a built site. All 83 browser interaction cases passed.

The affected workflow suites were rerun after that correction:

```sh
env PYTHONPATH=$PWD /tmp/model-438-scratch/venv/bin/python -m pytest -q -p no:cacheprovider -rs tests/test_ci_workflows.py tests/test_workflow_dependencies.py
actionlint -shellcheck= .github/workflows/test.yml
env PYTHONPATH=$PWD /tmp/model-438-scratch/venv/bin/python scripts/pytest_shards.py --shard-count 4 --summary
git diff --check
```

Results: `99 passed in 2.87s`, 0 skipped, exit 0; actionlint exit 0; shard estimates
4053.012 to 4053.013 seconds across four shards; diff check exit 0.
The browser install condition follows the assigned test file, so only its shard
installs Python Playwright and Chromium.

After staging the implementation and this evidence, the tracked-file guard was
rerun so it also covered the newly added files:

```sh
env PYTHONPATH=$PWD /tmp/model-438-scratch/venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py::test_no_tracked_file_names_a_removed_source
```

Result: `1 passed in 36.41s`, 0 skipped, exit 0.

Private commands, from `/tmp/model-438-scratch/modelspec-data`:

```sh
env PYTHONPATH=/Users/terbeest/dev/worktrees/model-438 /tmp/model-438-scratch/venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_rendered_reread.py -k recipe_sources
env PYTHONPATH=/Users/terbeest/dev/worktrees/model-438 /tmp/model-438-scratch/venv/bin/python -m pytest -q -p no:cacheprovider docs/evidence/g2-ios/MODEL-433/test_azure_selection.py
env PYTHONPATH=/Users/terbeest/dev/worktrees/model-438 /tmp/model-438-scratch/venv/bin/python -m pytest -q -p no:cacheprovider .github/scripts/tests/test_rendered_reread.py .github/scripts/tests/test_rendered_reread_workflow.py docs/evidence/g2-ios/MODEL-433/test_azure_selection.py
```

The final command returned `66 passed in 32.72s`, 0 skipped, exit 0, after the
upstream base refresh and final helper changes.

The live probe ran with `env PYTHONPATH=$PWD /tmp/model-438-scratch/venv/bin/python
/tmp/model-438-scratch/data-agent/check_azure_marker.py`. Its reproducible success
path is:

```python
from playwright.sync_api import sync_playwright
from decision.azure_pricing import wait_for_selected_prices

with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    context = browser.new_context(service_workers='block', accept_downloads=False)
    context.route('**/*', lambda route: route.continue_()
                  if route.request.method in {'GET', 'HEAD', 'OPTIONS'} else route.abort())
    try:
        page = context.new_page()
        page.goto('https://azure.microsoft.com/en-us/pricing/details/azure-openai/',
                  wait_until='domcontentloaded', timeout=45000)
        page.locator('#region-selector').select_option(value='us-east', timeout=15000)
        page.locator('#currency-selector').select_option(value='usd', timeout=15000)
        wait_for_selected_prices(page, 3)
        print('azure_selected_region_prices_match=True')
    finally:
        context.close()
        browser.close()
```

## Publication order and limits

Both PRs are drafts. Data #116 remains an open prerequisite. Merge the engine
follow-up, advance the private follow-up's `.engine-pin` to the resulting main
commit, validate that pin, and merge the data follow-up after #116. Private
workflows require the pin to be an ancestor of engine main, so this execution
does not pin an unmerged engine branch.

No full local suite, WSL gate, production deployment, paid-provider call,
Firecrawl call, or Linear write was performed. The scheduled jobs and GitHub CI
were not observed running. The live probe checked Azure's table postcondition;
it did not execute a live weekly verification or the complete production recipe.
No changed file is in the Worker's vendored source map, and the private change
does not alter registry or export data. The conditional private Worker memory
probe and public re-vendor were therefore not required and were not run.

Push commands use `CI_LOCAL_SKIP=1 git push -u origin model-438-recipe-followups`
after focused validation. PR creation uses `gh pr create --draft` from `/tmp`,
with the engine based on `main` and the private follow-up based on
`model-433-interactive-pricing`. No merge or ready action is authorized here.
