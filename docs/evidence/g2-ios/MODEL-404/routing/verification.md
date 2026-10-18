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

The upstream agent-copy check passed, so those generated files needed no further write. The regeneration changed exactly the guide version in OpenAPI's `info.description`, its `AgentGuideVersion` header constant, and the QA capture's OpenAPI hash. A parsed-YAML comparison proved that no other semantic value changed. The final OpenAPI check passed after every generation step (`openapi-final-green.txt`). API documentation tests passed: 56 passed, 2 skipped (`api-docs-final-green.txt`). All CLI and QA source hashes match current files, and guide versions agree across the generator, MCP, CLI and Worker. Final file hashes are recorded in `final-pins.txt`; the shared guide version is `1-c87335a7b267ef2f`.
