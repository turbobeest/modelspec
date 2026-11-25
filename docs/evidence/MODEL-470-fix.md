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

Retaken in round 2 (2026-11-25), after the headline change. Before is a build of `origin/main` at `4822b31b`. After is a build of this branch. Each is a Playwright Chromium viewport capture of the built landing page, device scale 1.

- Desktop, 1280×900: `docs/evidence/MODEL-470/desktop-before.png`, `docs/evidence/MODEL-470/desktop-after.png`
- Phone, 375×812: `docs/evidence/MODEL-470/mobile-375-before.png`, `docs/evidence/MODEL-470/mobile-375-after.png`
- Phone, 390×844: `docs/evidence/MODEL-470/mobile-390-before.png`, `docs/evidence/MODEL-470/mobile-390-after.png`

Round 1's mobile pair was a wide layout cropped to 390×844, and the first round-2 pair was 390 only. Both pairs are replaced by the files above.

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

The branch was behind `origin/main` (`3c9bc73a`, MODEL-468). That merge does not touch the round-2 files.

The first GitHub check after the round-2 push failed while installing the package. `hatch_build.py` refused `cli/modelspec/agent-bundle.json` because the digest of `pipeline/entity.py` was stale. Pytest shards, the package smoke test, the rank Worker bundle, and the Worker memory job all stopped on that same `ValueError`. `python -m pipeline.agent_copy write` changed only that digest. `python -m pipeline.agent_copy check` exited 0.

Not observed here: a browser session against modelspec.dev, and the `web/` test suite.

## Round 2, headline (2026-11-25)

Jamie, 2026-11-25: "Go with anything you have a recommendation for." The recommendation on record was to make the tagline the landing headline.

- The landing hero's one `h1` is `entity.TAGLINE`, through `landing.HEADLINE`. The previous two-line headline is gone from the page. The landing social card and its `og:image:alt` read `landing.HEADLINE` as well.
- The router line is the first paragraph after the `h1`, and the one sentence leads the second. `/about/` is unchanged: its own heading, then the three paragraphs.
- `pipeline/surface_lint.py` now requires the landing's only `h1` to be the tagline, then the router line, then a lead that starts with the one sentence. New tests: `test_the_landing_tagline_is_the_one_h1` and `test_the_landing_router_line_and_sentence_follow_the_headline` in `tests/test_surface_lint.py`. `tests/test_entity.py`, `tests/test_landing.py` and `tests/test_holding.py` check the same order and that the old headline is absent.
- Unchanged: `<title>`, `entity.SHORT` (the MCP card short description), every contract version and enum, `docs/legal/`, ranking and neutrality.

Hero layout, from the built pages (`node` with Playwright, five viewports). At every width `documentElement.scrollWidth` equals `innerWidth`, the page has one `h1`, no element in the hero extends past the viewport, and the router line's scroll width equals its client width.

| Width | `h1` height (one line) | Router line height |
| --- | --- | --- |
| 320 | 32px | 36px (two lines) |
| 375 | 32px | 36px (two lines) |
| 390 | 32px | 36px (two lines) |
| 899 | 32px | 18px |
| 1280 | 48px | 22px |

Merges: `origin/main` was merged twice (no rebase). The first merge had one conflict, the source hashes in `qa/fixtures/mcp-tools.json`. It was resolved by running the generators: `python -m pipeline.agent_copy write`, `python api/worker/openapi.py`, `python -m qa.contracts`. `python -m pipeline.agent_copy check` exited 0. The second merge had no conflict.

Round-2 review items, checked on this branch: the two ablation fixtures match `origin/main` byte for byte; the copy lint reads every git-tracked text file; `SUPERSEDED` lists the retired cost tail; the phone screenshots are real 375 and 390 viewports.

The site build and the lint on the built tree:

```bash
PYTHONPATH=$PWD /home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python -m pipeline.build --out <scratch>/after-dist
PYTHONPATH=$PWD /home/turbobeest/dev/04-modelspec/modelspec/.venv/bin/python -m pipeline.surface_lint --tree <scratch>/after-dist/modelspec
```

Both exited 0. The lint reported 0 findings.

Tests, run on jjt5090 with Python 3.12 and Node v22.23.2:

- `tests/test_surface_lint.py`, `tests/test_landing.py`, `tests/test_holding.py`, `tests/test_social_cards.py`, `tests/test_about.py`, `tests/test_agent_ready.py`, `tests/test_entity.py`, `tests/test_decision_link.py`, `tests/test_agent_copy.py` with `-n 4`: 450 passed. The 12 landing browser checks errored there because `web/dist` had not been built yet.
- After `npm ci`, `npm run build` and `npm test` in `web/` (exit 0; Vitest 949 passed, 66 files, 1 file skipped), `tests/test_landing.py` alone: 33 passed, including the 12 browser checks. Exit 0.

## Round 2, review fixes (2026-11-25)

An independent review of #1054 asked for three changes.

1. Landing order. `pipeline/surface_lint.py` reads the landing's `h1` and `p` elements together, in document order. The first must be the page's only `h1`, the tagline; the next two must be the router line and a lead that starts with the one sentence. A paragraph before the `h1` fails. Test: `test_a_paragraph_before_the_landing_h1_fails` (three layouts).
2. Whole statements. The typed-copy scan matches each registry line as a complete statement: any case, any whitespace, with or without the trailing full stop, opening at a line start, markup or a sentence end, with no word or clause running on. `SUPERSEDED` phrases match exactly, word-bounded, with no further word running on. Tests: 8 false-positive cases that pass (for example "Which model, and why does it matter?" and "sourced benchmarks and real cost savings") and 6 tagline, 1 router-line and 2 retired-tail cases that fail.
3. The one sentence. The scan now includes `ONE_SENTENCE`. It found typed copies in 4 files: `README.md`, `AGENTS.md`, `docs/cli-contract.md` and `docs/aeo/README.md`. Each now carries the sentence in a generated region between `<!-- entity:one-sentence -->` markers, which `python -m pipeline.agent_copy write` fills from `pipeline/entity.py` and `check` keeps fresh. The scan skips a region only when its text equals the registry. Tests: `test_a_typed_one_sentence_is_a_copy`, `test_the_generated_one_sentence_region_is_not_a_typed_copy`, `test_the_marked_markdown_files_carry_the_generated_sentence`. The visible text of the 4 files is unchanged; `docs/cli-contract.md` gains only the HTML comments, with no contract version, field or enum change.

`python -m pipeline.agent_copy write` also refreshed the `pipeline/agent_copy.py` digest in `cli/modelspec/agent-bundle.json`. `python -m pipeline.agent_copy check` exits 0. `python -m pipeline.surface_lint --tree` on the built tree: 0 findings.

Second review pass (2026-11-25):

- Marker form. An inline `<!-- entity:one-sentence -->` at a line start made the paragraph a raw HTML block. Each marker now sits on its own line, with a blank line between it and the sentence, so the sentence stays a Markdown paragraph (or a blockquote line in `docs/aeo/README.md`). `pipeline.agent_copy` writes that form and refuses inline markers; text that followed the sentence on its line is now the next paragraph. Tests: `test_the_writer_fills_regions_and_refuses_inline_markers`, and `test_the_marked_markdown_files_carry_the_generated_sentence` checks that each marker is alone on its line.
- Wrapped lines. The typed-copy scan splits each file into paragraphs at blank lines and normalizes whitespace and line breaks inside each, so a registry line that runs on into the next line is one longer sentence. Tests: 4 wrapped false-positive cases and `test_a_paragraph_break_ends_a_statement`.
- `docs/aeo/surface-lint.md`: the `llms.txt`, `index.md` and agent-skill ordering row is restored.
- Checks: `python -m pipeline.agent_copy check` exit 0; the repository copy scan finds nothing; the 59 test files that read the marked files, the lint, the agent copy or the landing: 3983 passed, 4 skipped, exit 0.
