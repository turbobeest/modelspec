# MODEL-orchestrator-recipe execution evidence

Base SHA: `0afd269c0e2e4dbb86dd073f4b8669437470fb07`.
Final implementation SHA: `94e00537ac608605011fda649a4f33c6045e6dda`.
The later evidence commit adds this report, logs, screenshots, and the unapplied
capture-refresh patch. The delivered SHA is the draft PR's head commit and is
reported in `CODEX_EXEC_DONE`.

The implementation publishes `/orchestrators/` through both the site build and
the live allowlist. Its Spec is generated from `coding-balanced`. The page has
canonical metadata, breadcrumb JSON-LD, sitemap registration, and pointers from
the generated agent guide and `llms.txt`. The guide version and its generated
CLI, MCP, and Worker copies were regenerated together. No public contract,
ranking rule, frozen model data, legal text, or production switch changed.

## Red first

The unchanged code did not publish the recipe. These new tests reached the
missing-page assertion in their shared fixture:

- `test_every_published_command_parses_with_the_cli`
- `test_example_spec_validates_against_bundled_decide_request`
- `test_recipe_is_discoverable_and_has_structured_data`

Red output, exit 1:

```text
AssertionError: the live build must publish /orchestrators/
assert False
```

The initial test helper also used the standalone Click group class, whereas
Typer 0.27.2 uses its bundled Click classes. This produced three additional
negative-control failures. I corrected the helper to use `TyperGroup` and
`typer.Exit`, without changing any existing test. The standalone negative
controls then reported `3 passed, 3 deselected` with exit 0. The original
[red log](MODEL-orchestrator-recipe/red.txt) retains both the absent-page
assertions and the initial helper failures.

Green verification of the page uses the actual generated live HTML. Every
displayed CLI command is parsed by the CLI's argument parser without invoking
keyed command callbacks. The JSON example validates through the CLI's bundled
`DecideRequest` validator and equals the registry template's Spec. The
integration test checks the page, canonical URL, JSON-LD, sitemap, both
discovery pointers, and all live-tree links. The six new tests are among the
97 passing tests in the focused run.

## Validation

| Check | Result | Evidence |
| --- | --- | --- |
| New command-parser negative controls | 3 passed, exit 0 | [Log](MODEL-orchestrator-recipe/parser-controls.txt) |
| New Python files, Ruff | Exit 0 | [Log](MODEL-orchestrator-recipe/lint.txt) |
| Focused Python suites | 97 passed, 5 failed, exit 1 | [Log](MODEL-orchestrator-recipe/focused.txt) |
| Web dependency installation | Exit 0 | [Log](MODEL-orchestrator-recipe/npm-ci.txt) |
| Web build | Exit 0 | [Log](MODEL-orchestrator-recipe/web-build.txt) |
| Web unit tests | 843 passed, one test file skipped, exit 0 | [Log](MODEL-orchestrator-recipe/web-tests.txt) |
| Browser corpus and decide flows | 27 passed, 8 skipped, exit 0 | [Log](MODEL-orchestrator-recipe/browser-tests.txt) |
| Final-source site build | Exit 0 | [Log](MODEL-orchestrator-recipe/site-build-final.txt) |
| Final-source live build | Discovery links resolve, exit 0 | [Log](MODEL-orchestrator-recipe/live-build-final.txt) |
| Recipe in Chromium with JavaScript disabled | Passed at 1440, 390, and 320 px, exit 0 | [Log](MODEL-orchestrator-recipe/recipe-browser.txt) |
| Full Python suite | 11,161 passed, 66 failed, 9 skipped, exit 1, 1198.06 seconds | [Log, gzip](MODEL-orchestrator-recipe/full-suite.txt.gz), [JUnit, gzip](MODEL-orchestrator-recipe/full-suite.xml.gz) |
| Final-source recipe tests | 6 passed, exit 0 | [Log](MODEL-orchestrator-recipe/recipe-final-tests.txt) |

The browser skips are the existing flag-gated billing and managed-gate flows.
The full Python run actually executed all 15 landing and social-card Chromium
cases. All passed and none were skipped. Their individual results are in
[python-browser-results.json](MODEL-orchestrator-recipe/python-browser-results.json).
The recipe browser check verifies HTTP 200, the heading, the system-prompt
text, and absence of horizontal overflow in every code block. I inspected the
[desktop](MODEL-orchestrator-recipe/recipe-1440.png),
[phone](MODEL-orchestrator-recipe/recipe-390.png), and
[narrow phone](MODEL-orchestrator-recipe/recipe-320.png) screenshots.

The final live page's code blocks equal the renderer's code blocks, including
the final illustrative tie example. `live.dead_links` and `live.thin_pages`
both return empty lists. An earlier whole-document equality probe failed
because the site build injects shared page controls and structured data. The
subsequent check compares the recipe content rather than those build additions.

A broader lint attempt initially reported 97 issues. Five were in the new
files and were fixed by wrapping unchanged string literals and binding the
shared fixture without an unused import. Ruff now passes on both new files.
The other 92 issues have the same codes and messages at the base SHA and at
HEAD, verified by sending each file's base and current source to Ruff with
`--stdin-filename`. The [comparison](MODEL-orchestrator-recipe/lint-baseline.json)
records the counts. No existing lint rule was disabled.

## Dependent artifact scope blocker

All five focused failures stop at `MCP definitions drifted; run python -m
qa.contracts and review the capture`. `qa.contracts.capture_tools()` differs
from `qa/fixtures/mcp-tools.json` only in two source hashes, for `docs/agents.md`
and `mcp/src/agent-copy.json`. No captured tool definition or schema differs.

`CODEX-EXEC.md` says: "Stay inside the paths the spec names. If you need a file
outside them, stop and report it." The spec does not name `qa/fixtures/`, so
I requested permission to refresh that generated file and left it unchanged.
The exact proposed [two-hash patch](MODEL-orchestrator-recipe/mcp-capture-refresh.patch)
is reviewable and passes `git apply --check`. Applying it remains pending scope
approval. The supported regeneration command is `python -m qa.contracts`.

The full run identified additional dependent metadata and fixtures. The
[failure summary](MODEL-orchestrator-recipe/failure-summary.json) records each
failure. Counts by module are:

| Module | Failures | Observed refusal |
| --- | ---: | --- |
| `test_ablation_targets` | 40 | The captured initialize copy uses the old guide version and fails convergence with `Upstream SUMMARY_RULE drifted`; local proxy/preflight cases then refuse |
| `test_ablation` | 8 | Dry replay and related report checks fail while the captures are stale |
| `test_agent_harness` | 5 | Captured MCP source hashes differ, or the harness stops at that drift check |
| `test_agent_gaps` | 4 | The harness stops at the MCP drift check |
| `test_agent_guide` | 5 | The harness stops at the MCP drift check |
| `test_api_docs` | 1 | The generated OpenAPI guide version no longer matches the committed YAML |
| `test_private_serving` | 1 | The same committed OpenAPI version differs |
| `test_decision_link` | 1 | The test pins the previous guide and MCP-copy byte hashes |
| `test_decide_preview_workflow` | 1 | Its stand-in build has no `orchestrators/` directory for the expanded live allowlist |

I prepared a complete, unapplied
[dependent-refresh.patch](MODEL-orchestrator-recipe/dependent-refresh.patch)
covering these five files:

- `api/worker/openapi.yaml`
- `qa/fixtures/ablation-metadata.json`
- `qa/fixtures/mcp-tools.json`
- `tests/test_decision_link.py`
- `tests/test_decide_preview_workflow.py`

The OpenAPI candidate comes from `api.worker.openapi.render()`. The MCP
capture candidate comes from `qa.contracts.capture_tools()` with the generated
OpenAPI hash. The ablation metadata changes only its embedded guide version.
Its candidate initialize copy and affected tool descriptions pass
`qa.ablation_proxy.converge_copy` for every ablation arm. The test candidates
refresh two byte hashes and add the new page to the stand-in build, preserving
the existing assertions.

The 66-line patch passes `git apply --check`. All five target files remain
byte-identical to the base commit. I expanded the scope request to these files
after reading the full failure list. No approval had arrived when this blocked
draft was prepared. The patch has not been applied or tested as a combined
change, so it is not evidence that all 66 failures would pass. A successful
full-suite rerun is still required.

## Reproduction commands

All commands run from this worktree, with `web/` as the working directory for
the npm and browser-corpus commands. Test and build exit codes were captured
directly before inspecting logs. Tool versions are in
[versions.txt](MODEL-orchestrator-recipe/versions.txt): Python 3.14.4, pytest
9.1.1, pytest-xdist 3.8.0, Typer 0.27.2, Click 8.5.0, jsonschema 4.26.0,
Node v22.22.3, npm 10.9.8, Git 2.50.1, gh 2.102.0, and Chromium 153.0.8010.12.
Ruff is 0.16.6.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_orchestrators.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_orchestrators.py -k command_check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH CI=true PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_orchestrators.py tests/test_holding.py tests/test_agent_copy.py tests/test_agent_guide.py tests/test_llms_txt.py tests/test_structured_data.py tests/test_sitemap.py
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm run build
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH MODELSPEC_BROWSER_OUTPUT=$PWD/../docs/evidence/g2-ios/MODEL-orchestrator-recipe/browser-results npx playwright test --config=playwright.corpus.config.ts --workers=4
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.live build --src dist --web web/dist --out dist-live
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH node docs/evidence/g2-ios/MODEL-orchestrator-recipe/check-recipe.mjs
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH CI=true PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile --junitxml=docs/evidence/g2-ios/MODEL-orchestrator-recipe/full-suite.xml
git apply --check docs/evidence/g2-ios/MODEL-orchestrator-recipe/mcp-capture-refresh.patch
git apply --check docs/evidence/g2-ios/MODEL-orchestrator-recipe/dependent-refresh.patch
git diff --check
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check pipeline/orchestrators.py tests/test_orchestrators.py pipeline/build.py pipeline/live.py pipeline/structured_data.py pipeline/agent_copy.py
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check pipeline/orchestrators.py tests/test_orchestrators.py
```

The site and live build commands were repeated after the final prose edit.
Their initial logs are preserved alongside the final-source logs.
The final implementation commit wraps unchanged string literals and adjusts
the new test fixture binding. Its six recipe tests were rerun successfully.
The full-suite log and JUnit file are losslessly compressed with
`gzip.compress(raw, mtime=0)` after collection. Decompression was checked
against their original bytes. The readable failure summary links above avoid
adding the raw traceback and XML lines to the review diff.

## Not observed

I did not make a live keyed ModelSpec decision or an inference-provider call.
The worked answer is explicitly illustrative, not a measured recommendation.
The CLI commands were parsed, not sent to hosted services. I did not test
historical snapshot hosting, purchase a key, configure a real MCP client, or
observe production deployment of the new page. I did not run subscription
agents or judges, contact a device, upload an artifact, run the wsl gate,
edit Linear, change production switches, or merge anything.
