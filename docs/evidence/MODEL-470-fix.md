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

Landing page from those builds. Desktop window 1280×900. Mobile window 390×844. Chrome headless.

- `docs/evidence/MODEL-470/desktop-before.png`
- `docs/evidence/MODEL-470/mobile-before.png`
- `docs/evidence/MODEL-470/desktop-after.png`
- `docs/evidence/MODEL-470/mobile-after.png`

At 390px the router line wraps inside the hero. `documentElement.scrollWidth` equals the viewport width. The page has one `h1`.

## Generators

- `python -m pipeline.agent_copy write` rewrote `mcp/src/agent-copy.json`, `docs/agents.md`, `cli/modelspec/agent-bundle.json`, and `api/worker/src/agent_guide.py` (guide version `1-9135abd62c344ffd`). Schema files and `site/holding/index.html` were unchanged.
- `python api/worker/openapi.py` rewrote the guide-version constants in `api/worker/openapi.yaml`.
- `python -m qa.contracts` rewrote the `docs/agents.md` and `mcp/src/agent-copy.json` hashes in `qa/fixtures/mcp-tools.json`.

`qa/fixtures/ablation-pre682-copy.json` and `qa/fixtures/ablation-metadata.json` each had the old sentence once. Both now carry the revised sentence, and the rest of each fixture is unchanged, so the old tail does not remain outside history and evidence. The ablation convergence tests passed.

## After merge

The PyPI package `modelspec-dev` still ships the previous `agent-bundle.json` until a release. The published MCP registry entry still has the previous `server.json` description until that manifest is published. The deployed MCP Worker still serves the previous guide until it is deployed. The GitHub repository description is a repository setting and still needs a manual edit.
