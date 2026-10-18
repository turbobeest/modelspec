# MODEL-258 execution evidence

Worktree: `/Users/terbeest/dev/worktrees/model-258-guides`.
Branch: `model-258-guides`.
Base SHA: `6f45c2a7dc9ce2e771bd1ecea926a1a29fe1ad49`.
Final implementation and test SHA: `14f10d3767612fbf70a96a01c4235d2def47150c`.
The subsequent evidence-only commit records the completed checks; the PR head
and executor completion line identify that final commit.

## Result

The build publishes `/guides/`, `/guides/how-to-choose-an-ai-model/` and
`/guides/analysis-of-alternatives-vs-model-router-vs-hard-coded-model/`.
Both articles and the index survive live-site composition and have sitemap
dates from the frozen public image. The method page and related-page links
lead to the guide index.

The choice guide reuses `public_use_case_image()` and the existing
`budget-coding` template. It runs that template with `explain: full` on the
same public snapshot and registry. Full explanations are necessary because
summary responses omit individual excluded candidates. No ranking code or
data image changed.

The example preserves engine scores, intervals, probabilities, task costs,
tie rules and excluded-candidate conditions and values. Model and offering
aliases keep product names out of the guide. Offering-level failures remain
distinct from whole-model exclusion. The page links to the dated named
use-case example and `/decide/?template=budget-coding`.

The category comparison has three category columns and eight decision rows.
The choice guide emits `DefinedTerm` and `Article`; the category comparison
emits `Article`. All content is static HTML with the existing site CSS.

## Red-first evidence

The following commands ran from the worktree. No existing assertion was
removed or weakened.

### Missing guide pages and worked example

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_guides.py
```

Before implementation, exit 1:

```text
ImportError: cannot import name 'guides' from 'pipeline'
2 failed, 4 errors in 0.52s
```

The two failures were
`test_swapping_public_image_changes_engine_numbers_and_exclusions` and
`test_guide_without_supported_answer_keeps_the_limit_visible`. The remaining
tests failed fixture setup because the generator did not exist:

- `test_example_has_exact_public_image_label_tie_rules_and_template_link`
- `test_guides_compare_categories_without_product_names`
- `test_guides_have_dated_sitemap_entries_and_visible_structured_data`
- `test_guides_are_readable_and_linked_without_client_javascript`

After implementation, the same command exited 0:

```text
6 passed in 4.73s
```

The image-swap test supplies two compiled snapshot fixtures at the public
image-loading boundary. Both use the real parser and decision engine. Changing
an offering price changes the rendered scores, costs and exclusion rows.
Expected values come from a separate engine call. The fixture poisons the
private data directory and refuses network access.

### Guides lost during live composition or missed by validation

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_live_use_cases.py
```

Before the integration changes, exit 1:

```text
8 failed, 7 passed in 2.61s
```

The failures covered guide file and sitemap preservation, guide dead links,
the raw-HTML thin-page check, entity-lead linting, `DefinedTerm` acceptance,
guide discovery outside the sitemap, and source dates in both build layouts.
The named tests are:

- `test_live_checks_links_on_every_worked_example`, guide parameter
- `test_live_guides_preserve_pages_navigation_and_image_dates`
- `test_live_thin_page_check_rejects_a_guide_that_needs_javascript`
- `test_surface_lint_checks_guide_leads`
- `test_surface_lint_accepts_a_visible_defined_term`
- `test_live_surface_lint_discovers_guides_outside_the_sitemap`
- `test_surface_lint_guide_freshness_uses_the_image_date`, both parameters

After implementation:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_live_use_cases.py tests/test_surface_lint.py tests/test_crawler_access.py
```

Exit 0: `140 passed in 13.75s`.

### Evidence bands can exceed the response row limit

Review found that aliases derived only from `by_model` missed candidates
retained in the complete evidence bands. A real-engine fixture with additional
qualifying models reproduced a build failure.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_guides.py::test_guide_keeps_every_band_model_when_results_are_truncated
```

Before the fix, exit 1:

```text
pipeline/guides.py:92: KeyError: 'lab/extra-18'
1 failed in 1.11s
```

Aliases now include every model in the evidence bands. The regression checks
that every numeric row survives, aliases are unique, and model IDs do not leak.
It passes in the final focused suite below.

## Verification commands and results

Tool versions: Python 3.14.4; pytest 9.1.1; Node v22.22.3; npm 10.9.8;
Git 2.50.1; GitHub CLI 2.102.0; Playwright CLI 0.1.22.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_guides.py tests/test_live_use_cases.py tests/test_surface_lint.py tests/test_crawler_access.py tests/test_structured_data.py tests/test_sitemap.py
```

Exit 0: `161 passed in 8.91s`.

The web commands ran in `web/` with the specified Node version and the shared
Python environment on PATH:

```sh
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm ci
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm run build
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm test
```

All exited 0. The web suite passed 843 tests. The install reported dependency
audit findings; dependency versions were not changed by this ticket.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree dist/modelspec
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.live build --src dist --web web/dist --out dist/live
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree dist/live/modelspec
```

The site build and live composition exited 0. Both surface lints exited 0
with no findings. Live composition reported:

```text
dist/modelspec: 0 findings; 5365 files checked
dist/live/modelspec: 0 findings; 154 files checked
modelspec: 2751 files; discovery links resolve
```

Both trees contain all three guide URLs with `lastmod` of `2026-09-23`, the
frozen image date. The live tree passes `live.thin_pages()`. The site build
reported unregistered hardware-source warnings already present in the public
image; this ticket did not change that data.

The full suite command uses the required shared lock and specified Node:

```sh
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

The full run exited 1:

```text
FAILED tests/test_decide_preview_workflow.py::test_live_assembly_matches_internal_and_preserves_holding_byte_for_byte
1 failed, 11727 passed, 9 skipped, 11 warnings in 1422.41s (0:23:42)
```

The failure was a missing directory in the existing deployment fixture:

```text
FileNotFoundError: [Errno 2] No such file or directory: '.../dist-v1/modelspec/guides'
```

The fixture predated guide publication. It now includes all three guide pages
and their sitemap entries, and asserts that live/internal composition keeps
their content and frozen dates. Existing holding-tree preservation assertions
remain intact. This correction changes only the test fixture and assertions;
the production implementation was unchanged after the full run.

The failed file and all related focused suites then passed:

```sh
env PYTHONPATH=$PWD PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decide_preview_workflow.py tests/test_guides.py tests/test_live_use_cases.py tests/test_surface_lint.py tests/test_crawler_access.py tests/test_structured_data.py tests/test_sitemap.py
```

Exit 0: `169 passed in 22.09s`. A first attempt to run this focused command
behind the shared lock waited without starting pytest; that lock wait was
canceled with exit 130, then the focused command above ran directly. The
required full run held the shared lock. The full suite was not repeated after
the fixture-only correction, so the evidence is a complete run plus a green
targeted rerun, not a claim that the original full run exited zero.

## Browser observations

The browser read the generated HTML from a local server:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python -m http.server 8768 --bind 127.0.0.1 --directory dist/modelspec
```

Each browser command used this prefix:

```sh
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex/skills/playwright/scripts/playwright_cli.sh -s=model258
```

The arguments, in execution order, were:

```text
open http://127.0.0.1:8768/guides/how-to-choose-an-ai-model/
resize 390 844
screenshot --filename=choose-mobile.png --full-page
eval '() => ({viewport: innerWidth, width: document.documentElement.scrollWidth, heading: document.querySelector("h1").textContent, tables: [...document.querySelectorAll(".use-case-table")].map(e => ({width:e.clientWidth, scroll:e.scrollWidth})), rows: document.querySelectorAll("#example-results tbody tr").length})'
goto http://127.0.0.1:8768/guides/analysis-of-alternatives-vs-model-router-vs-hard-coded-model/
screenshot --filename=compare-mobile.png --full-page
eval '() => ({viewport: innerWidth, width: document.documentElement.scrollWidth, columns: [...document.querySelectorAll("#category-comparison th")].map(e => e.textContent), rows: document.querySelectorAll("#category-comparison tbody tr").length, tableWidth: document.querySelector(".use-case-table").clientWidth, tableScroll: document.querySelector(".use-case-table").scrollWidth})'
resize 1440 1000
screenshot --filename=compare-desktop.png --full-page
close
```

All browser commands exited 0. Screenshots were inspected locally. At mobile
width, each article's document width was 390 pixels, matching the viewport.
Tables were 720 pixels wide inside 342-pixel scrolling containers. The choice
example rendered two result rows. The comparison rendered eight rows and the
three required category columns. The local server and the browser session
were stopped after inspection.

## Observation limits

This execution does not establish deployed crawler access, search indexing,
answer-engine quotations, or a production rollout. It makes no live model
recommendation. No paid-provider call, Linear write, production switch change,
merge, ranking-floor change or legal-text edit was performed. Agent-copy,
OpenAPI and MCP-capture generators and their pins were not edited.
