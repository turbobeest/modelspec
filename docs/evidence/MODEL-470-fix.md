# MODEL-470

Base: `58748fec44f4055a16e37229764f60467278a5a8`.
Head: the commit on `model-470` that adds this file.

Jamie's lines, 2026-11-12:

- Tagline: `Which model, and why.`
- Router line: `Evidence-backed logic that powers complex model routing.`
- One sentence: `ModelSpec is an analysis of alternatives for AI models: it decides which models fit a job from your requirements, sourced benchmarks, and real costs, and shows its work.`

`TITLE`, `SHORT`, `DISAMBIGUATION`, `ALIASES`, `SAME_AS`, and `CLAIMS` are unchanged. `docs/legal/` has no copy of the old sentence. Frozen public data is unchanged. Existing files under `docs/evidence/` were left as they were. The old tail `sourced benchmarks and real cost` remains in:

- `docs/evidence/g2-ios/MODEL-261-live-manifest.json`
- `docs/evidence/g2-ios/MODEL-404/routing/focused.txt`
- `docs/evidence/g2-ios/MODEL-orchestrator-recipe/dependent-refresh.patch`

## Checks

Red, before the constants existed. Command:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_entity.py tests/test_about.py tests/test_surface_lint.py
```

Exit 1. Failed: `test_the_registry_carries_the_tagline_the_router_line_and_the_revised_sentence`, `test_linked_keeps_the_visible_text_and_refuses_a_missing_phrase`, `test_identity_lines_are_not_copied_outside_the_registry`, `test_raw_html_shows_the_sentence_disambiguation_first_and_every_claim`. Errors: `test_a_landing_missing_the_tagline_fails`, `test_current_registry_surfaces_pass`.

Green, after the change. Same pytest invocation, plus `tests/test_agent_copy.py`, `tests/test_brand_page.py`, `tests/test_guides.py`, `tests/test_discovery.py`, `tests/test_generated_pins.py`, `tests/test_agent_harness.py::test_mcp_capture_matches_current_public_sources`, the ablation copy-convergence tests, `tests/test_pipeline.py`, `tests/test_comparison_pages.py`, `tests/test_comparison_lint.py`, `tests/test_cli_concierge.py`, `tests/test_crawler_access.py`, `tests/test_live_use_cases.py`, and `tests/test_landing.py`. Exit 0. The landing browser checks (`test_landing_behaviour_in_browser`) passed 12 after `npm ci` in `web/`.

Sites:

```bash
~/.codex-g2/heavy.sh env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out /tmp/MODEL-470-before-dist
```

That build used a detached worktree of `58748fec`. The changed tree was built the same way to `/tmp/MODEL-470-after-dist`. Both exited 0.

```bash
(cd web && npm ci && npm run build && npm test)
```

Exit 0. Vitest: 937 passed, 64 files, 1 file skipped.

## Screenshots

Desktop window 1280×900, kept from round 1. This round did not change the page.

- `docs/evidence/MODEL-470/desktop-before.png`
- `docs/evidence/MODEL-470/desktop-after.png`

Round 1's mobile files were a wide layout cropped to 390×844. Round 2 replaced them with captures from the built sites at a 390×844 viewport, device scale 1.

- `docs/evidence/MODEL-470/mobile-before.png` from the build of `58748fec`
- `docs/evidence/MODEL-470/mobile-after.png` from the build of this round

On the current page the router line is `Evidence-backed logic that powers complex model routing.` and it wraps onto two line boxes. `documentElement.scrollWidth` is 390, the same as `innerWidth`. The page has one `h1`. The pre-change page has no router line. Its hero text fits the same 390-wide viewport.

## Generators

- `python -m pipeline.agent_copy write` rewrote `mcp/src/agent-copy.json`, `docs/agents.md`, `cli/modelspec/agent-bundle.json`, and `api/worker/src/agent_guide.py` (guide version `1-9135abd62c344ffd`). Schema files and `site/holding/index.html` were unchanged.
- `python api/worker/openapi.py` rewrote the guide-version constants in `api/worker/openapi.yaml`.
- `python -m qa.contracts` rewrote the `docs/agents.md` and `mcp/src/agent-copy.json` hashes in `qa/fixtures/mcp-tools.json`. A second run, after `openapi.py`, recorded `api/worker/openapi.yaml` as `ed0423c34e4491cec6dbc16c93768e7d42379cc4efbf956f169328987c776341`.
- `tests/test_decision_link.py` pins the rendered agent copy at `650e4fbd502cc97191e1cec9118ed94e55721dcb2262cd07e18bb323e63bd00e` and the guide at `dbdbad3f62fae2e1aa4c501765cde583c80e01d4f8fdd33c2d8e5e7b2776e146`. The CLI text hash is unchanged.

`qa/fixtures/ablation-pre682-copy.json` and `qa/fixtures/ablation-metadata.json` each had the old sentence once. Round 1 replaced that sentence and left `source_commit` and `source_sha256` in place. Round 2 restored both files from `origin/main`. Recorded fixtures keep the text they captured.

## After merge

The PyPI package `modelspec-dev` still ships the previous `agent-bundle.json` until a release. The published MCP registry entry still has the previous `server.json` description until that manifest is published. The deployed MCP Worker still serves the previous guide until it is deployed. The GitHub repository description is a repository setting and still needs a manual edit.

## Round 2

Review fixes. The three registry strings in `pipeline/entity.py` are unchanged apart from one new `SUPERSEDED` entry. `git diff 2c656a8a -- pipeline/entity.py` is that line.

Python `/Users/terbeest/dev/modelspec/.venv/bin/python`, version 3.14.4. Node v22.22.3 for the screenshots. Playwright Chromium from `web/node_modules/playwright`.

Red, before the repository scan. `tests/test_surface_lint.py::test_copied_identity_reports_readme_typescript_and_html` exited 1. The lint reported no files. The planted paths were `README.md`, `src/router.ts` and `templates/landing.html`.

Red, before the retired tail was listed. Both of these exited 1:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_entity.py::test_the_retired_cost_tail_is_superseded_and_misses_the_revised_sentence \
  tests/test_surface_lint.py::test_retired_cost_tail_is_rejected_outside_recorded_history
```

`sourced benchmarks and real cost` was absent from `entity.SUPERSEDED`, and a planted `README.md` produced no `presence.superseded` finding.

Green, after the changes. The same two tests passed, and the focused modules passed together:

```bash
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_entity.py tests/test_surface_lint.py tests/test_about.py \
  tests/test_decision_link.py tests/test_legal.py \
  tests/test_ablation.py tests/test_ablation_proxy.py tests/test_ablation_targets.py
```

670 passed in 66.74s. Exit 0. The three ablation modules alone, after the fixture restore, were 297 passed. Exit 0.

The copy lint reads `git ls-files`. Outside a checkout it walks the tree and skips `node_modules`, `dist`, `.git` and build output. It matches the tagline and the router line with or without the trailing full stop, in any case. The same pass rejects `SUPERSEDED`, including the retired tail. Exempt: `pipeline/entity.py`, `tests/`, `docs/history/`, `docs/evidence/`, `qa/fixtures/`, and the generated files named in `pipeline/surface_lint.py`. No llms Markdown twin is committed under `docs/`. `docs/agents.md` is the committed agents twin.

Site build and the lint CI runs on the built tree:

```bash
~/.codex-g2/heavy.sh env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out /tmp/MODEL-470-scratch/after-dist
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree /tmp/MODEL-470-scratch/after-dist/modelspec
```

Both exited 0. The lint reported 0 findings and 5366 files. A second build of `58748fec` supplied the pre-change mobile capture. `web/` was not changed, so this round did not run `npm ci`. The live-assembly lint was not run.

Phone metrics, both captures: `innerWidth` 390, `innerHeight` 844, `devicePixelRatio` 1, `scrollWidth` 390. On the current page the router line's two line boxes are 330px and 113px, and the element's scroll width equals its client width.

Not observed here: the pull request's GitHub checks after this push, a browser session against modelspec.dev, and the `web/` test suite.
