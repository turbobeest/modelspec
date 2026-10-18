# Routing verification

Base: `72cd65f81aeae93add87b9a52157ae8cbce698a3`. Work stayed on `model-404-simple-decide`.

Python 3.14.4; Node v22.22.3; npm 10.9.8.

The new route tests ran before production edits. `red.txt` records five failing assertions and one pass: the absent detailed route, absent sitemap entry, old first-visit metadata, old board links, and old template destination. The first fixture attempt had missing header setup and a mistyped helper name; these were corrected before the recorded red run.

After implementation, `green.txt` records six passing route tests. They execute the real live composer, inspect both published HTML pages and JSON-LD, check source-dated sitemap entries, and inspect generated agent/link/card output.

The broader routing run in `focused.txt` recorded 177 passing tests and two stale generated-copy failures because agent-copy generation was still running. After generation completed, all 16 tests in `test_agent_copy.py` passed in `agent-copy-green.txt`. No production fix was needed for those two transient failures.

Commands from the worktree root:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_simple_decide_routes.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.social_cards sync-meta
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_simple_decide_routes.py tests/test_crawler_access.py tests/test_surface_lint.py tests/test_decide_preview_workflow.py tests/test_agent_copy.py tests/test_structured_data.py tests/test_about.py tests/test_sitemap.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_copy.py
```

The initial OpenAPI check passed before agent-copy generation completed, so it did not verify the final generated guide version. The final dependency-order correction below supersedes that check. The required changed generated files are `mcp/src/agent-copy.json`, `docs/agents.md`, `cli/modelspec/agent-bundle.json`, `api/worker/src/agent_guide.py`, `api/worker/openapi.yaml`, and `qa/fixtures/mcp-tools.json`. The generator left the request and feedback schemas and holding HTML unchanged.

The board unit command runs from `web/`:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm exec vitest run -- src/decide/__tests__/real-app.test.tsx src/decide/__tests__/theme.test.tsx
```

The first invocation used the repository root and failed to read the relative HTML fixture. It was rerun from `web/`; the final result is recorded in `board-unit-green.txt`.

This worker did not run paid providers, deploy, make production requests, or inspect a screen reader. The root executor owns the complete build, browser verification, screenshots and full locked pytest run. This worker made no commits and started no background server.

Final routing review reran the following command, with 136 tests passing in 5.10 seconds in `review-green.txt`:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_simple_decide_routes.py tests/test_crawler_access.py tests/test_surface_lint.py
```

The lint mutation test covers `decide.html`, `decide-details.html`, `decide/index.html`, and `decide/details/index.html`. Route tests check generated social metadata in both source and composed HTML. A temporary Git repository test proves that a commit in `web/src/decide/simple/` updates the simple page's lastmod and an unrelated commit does not. A targeted literal-URL scan found only the intentional introductory README link still pointing at the bare decide route. AEO page descriptions and the handoff route description now name both pages.

A read-only simple UI review sent two concerns to the root executor: selecting an already-loaded job must still move focus to the verdict, and absent route data must not be labelled as an own-hardware route. The root executor owns those UI fixes and their tests.

The root executor's real composed build exposed two JSON-LD visibility errors on the detailed page. The new `test_decide_jsonld_names_and_descriptions_are_visible` reproduced both errors in `jsonld-red.txt` (one failing detailed case and one passing simple case). The detailed page's JSON-LD name now matches its existing visible heading, "Which AI model fits your job". The composition test also checks JSON-LD visibility in each published HTML page. No UI source or web HTML change was needed for this correction.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_simple_decide_routes.py -k jsonld
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_simple_decide_routes.py tests/test_surface_lint.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.live build --src dist --web web/dist --out docs/evidence/g2-ios/MODEL-404/root/.live
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree docs/evidence/g2-ios/MODEL-404/root/.live/modelspec --report docs/evidence/g2-ios/MODEL-404/routing/surface-green-report.json
```

The focused tests passed (114 tests, `jsonld-green.txt`), real composition passed with 2670 files and resolving discovery links (`live-recomposition.txt`), and real surface lint passed with zero findings across 70 files (`surface-green.txt`, `surface-green-report.json`). The original failing real lint output remains in the root executor's evidence directory.

CI later exposed stale OpenAPI guide metadata. The local `--check` reproduced exit 1 in `openapi-final-red.txt`. `api/worker/openapi.py` imports `GUIDE_VERSION` from generated `api/worker/src/agent_guide.py`, so OpenAPI generation must follow completed agent-copy generation; the QA capture must follow OpenAPI. The earlier check had run while agent-copy generation was still in progress.

The final sequence was:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_api_docs.py
```

The upstream agent-copy check passed, so those generated files needed no further write at that stage. The regeneration changed exactly the guide version in OpenAPI's `info.description`, its `AgentGuideVersion` header constant, and the QA capture's OpenAPI hash. A parsed-YAML comparison proved that no other semantic value changed. The OpenAPI check passed after every generation step (`openapi-final-green.txt`). API documentation tests passed: 56 passed, 2 skipped (`api-docs-final-green.txt`). All CLI and QA source hashes matched, and guide versions agreed across the generator, MCP, CLI and Worker. The guide version at that stage was `1-c87335a7b267ef2f`; the budget correction below supersedes it.

The CI pytest shard subsequently reported `test_flag_off_agent_copy_matches_reviewed_catalogue` with the old catalogue hash. A focused local run reproduced that failure before changing the test (`catalogue-pin-red.txt`). Review against the base commit confirmed the MCP copy changed only its guide version, guide Markdown and instructions: they add the required detailed-board link. CLI text changes only `human_message` from `/decide/` to `/decide/details/`. These are the MODEL-404 link changes, with no decision-link behavior change (`catalogue-pin-review.txt`).

The test retains three hardcoded SHA-256 assertions. At that stage they pinned MCP copy `36064102d8fcdc9b1ea6e62a68066d452ec525fe4b5366552812067189d0803e`, guide Markdown `7a15fbc29407078d53594b0755852b3f4c341ad83f7b68582c92b4b72075821a`, and sorted CLI text `625b4b758472c68f454847573d4bdd9ff1fc2aa7a5800f739dba925cf547ee86`. The disabled decision-link response-byte assertions remain unchanged.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_link.py::test_flag_off_agent_copy_matches_reviewed_catalogue
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_link.py tests/test_agent_copy.py
```

The complete focused suites passed: 63 tests in `catalogue-pin-green.txt`. No runtime source changed for this correction.

The first complete Python run also exposed the MCP first-turn budget regression. The focused `test_coverage_pointer_keeps_all_three_mcp_first_turns_under_budget` reproduced it before copy changes (`budget-red.txt`). The original breakdown was Claude 9368, OpenAI 9461, Gemini 9540 estimated tokens, exceeding the existing 9500 limit for Gemini (`budget-breakdown-red.json`).

The detailed-board link had been added both to the guide/context guide and to initialization instructions. The correction keeps one concise `Full board: https://modelspec.dev/decide/details/.` in the guide/context guide and removes the duplicate sentence from initialization instructions. Removing duplication alone still exceeded the budget, so the guide's transport paragraph now states the same requirements in fewer words: POST the Spec JSON, retain Content-Type, real User-Agent and Bearer Authorization headers, pass the Spec as MCP arguments with connection Authorization, and add no `spec` or `task` wrapper. No conduct rule, tool schema, access requirement or numeric budget changed. The route test checks the MCP context guide's link instead of requiring that link twice.

Artifacts were regenerated in dependency order, followed by literal-pin review and checks:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_guide.py::test_coverage_pointer_keeps_all_three_mcp_first_turns_under_budget
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.agent_harness --first-turn-breakdown
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_guide.py tests/test_agent_copy.py tests/test_decision_link.py tests/test_api_docs.py tests/test_simple_decide_routes.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.agent_harness --first-turn-breakdown
```

The focused run before main integration passed: 146 passed, 2 opt-in live probes skipped (`budget-green.txt`). Both generator checks passed. At that stage the first-turn totals were Claude 9327, OpenAI 9420 and Gemini 9499 (`budget-breakdown-green.json`); no provider was called. The guide version became `1-f226d9942791da1c`. The catalogue hashes at that stage pinned MCP copy `ba2e9673bb58c5d6310a0ad9d2078ed54d5189a5eee2789cee98cea30b980030`, guide Markdown `6fc541536d3d18442ac260767d254fc02216577951fac36aae92de700ae27a37`, and unchanged CLI text `625b4b758472c68f454847573d4bdd9ff1fc2aa7a5800f739dba925cf547ee86`. QA and CLI source hashes matched, and parsed OpenAPI differed only in its two guide-version values. The merged-source results below supersede these counts and the MCP hash; `final-pins.txt` records the merged artifacts.

CI run `39090006166`, pytest shard 2, then exposed a source-fixture dependency introduced by newer main: the live composer parses the source `modelspec/sitemap.xml`. The exact JUnit failures for both route cases are extracted in `ci-sitemap-red.txt`; both fail with `FileNotFoundError` at that parse. The branch's older local composer did not yet perform it. The fixture now writes a valid source sitemap using `live.sitemap()` before composition, matching a real pipeline build. All assertions remain intact, and no runtime code changed. The local command `PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_simple_decide_routes.py` passed all 8 tests (`source-sitemap-green.txt`). Verification against the newer composer follows the root executor's main-branch merge.

The integration with main `0cf4080a7` preserves main's hardware-fit description, OpenAPI compaction threshold of 72, and use-case composition. The generated conflicts were resolved from the combined source, in order: agent-copy generation, OpenAPI generation, then QA capture. The root executor ran the final two generators. MCP JSON differs from branch parent `ea1643cc` only at `tools.hardware_fit`; against main it differs only at `context_guide`, `guide_version`, and `instructions`. Guide version remains `1-f226d9942791da1c`. The three reviewed-catalogue assertions remain literal hashes, and the flag-off response-byte tests are unchanged.

Main's new use-case fixture also lacked the new `decide-details.html` entry. All three tests reproduced the missing-file error before adding that one fixture entry (`merge-use-case-red.txt`). The complete composition suites then passed all 11 tests against the merged composer (`merge-composition-green.txt`). No assertions were weakened.

Final merged-source verification commands:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.agent_harness --first-turn-breakdown
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_guide.py tests/test_agent_copy.py tests/test_decision_link.py tests/test_api_docs.py tests/test_simple_decide_routes.py tests/test_live_use_cases.py
```

Both generator checks returned exit 0 (`merge-agent-check.txt`, `merge-openapi-check.txt`). The focused suites passed 149 tests, with 2 opt-in live probes skipped, in 13.29 seconds (`merge-focused.txt`). The first-turn estimates are Claude 9328, OpenAI 9421, Gemini 9500, all within the unchanged 9500 limit; Gemini has no remaining estimated-token margin (`merge-first-turn.json`). No provider was called.

`merge-pin-link-audit.txt` records that all three literal catalogue digests, all nine CLI source hashes, and all QA source hashes match. `final-pins.txt` contains the six regenerated artifact hashes. Rendered about-page call and header links reach the detailed board. The use-case template action reaches `/decide/details/?template=...`; generic navigation and free human lookup retain `/decide/`. The root executor owns the merge commit, MCP unit run, full Python suite, and final real site composition.

The final published-file audit at `e0053beaa0515892667dfcbb3225422560ea43d5` passed. [final-artifact-audit.json](final-artifact-audit.json) records both decide routes, their canonical/OG URLs and resolving JS entries, source-derived sitemap dates, about/home board links, all 40 detailed-board template actions, 82 introductory links across 41 use-case pages, exact published agent/OpenAPI bytes, and no thin core pages. The composed sitemap contains 33 entries, including 19 use-case entries whose source date is preserved.
