# MODEL-219 executor evidence

Status: READY for Grok review. Live composition is implemented after the
orchestrator granted the scope exception. Draft PR #811 remains draft.
Static and live builds, web tests, focused checks, and the complete pytest
suite under the shared lock pass.

Base SHA: `688f1072142a6824930dd1f17473d4d0050625cc`.
Final implementation SHA: `9c866949300933f6238b2cc0ca7026e44c0f9666`.
The following evidence-only commit is the final PR HEAD. Its exact SHA is
recorded in the executor completion line and PR body after
commit, avoiding a self-referential commit hash inside this file.

The first commit is the required design document, `63647dba`. The draft PR
was opened from that commit before implementation.

## Red first and green results

All test names below are in `tests/test_pipeline.py` unless a file is named.
The initial run against unchanged implementation returned exit 1:
`12 failed, 1 passed, 47 deselected in 1.13s`. Missing generator functions
raised `AttributeError`. Both AI-instruction cases and the noindex-page lead
check failed their assertions because the lint did not yet enforce them.

| Rule or defect | Red-first test | Green evidence |
| --- | --- | --- |
| Public image and shared engine | `test_use_case_decisions_use_public_image_and_the_shared_engine` | Exact response equality with the shared engine, public snapshot input, and a network connection guard pass. |
| Registry copy and engine precision | `test_use_case_page_preserves_engine_values_and_registry_copy` | Model IDs, score and capability intervals, P(best), nulls, warnings, and template reasons appear unchanged. |
| Ties and cost | `test_use_case_tie_is_not_a_cost_recommendation` | Tie membership, basis, and all four tie-breakers pass. |
| No answer and thin evidence | `test_use_case_without_answer_is_noindex_and_absent_from_sitemap[empty]` and `[fully-undetermined]` | Both pages remain readable, say no recommendation, and are excluded from the sitemap. |
| Neutrality and access | `test_use_case_neutrality_and_access` | Neutrality link, applied-template human link, keyed CLI/API/MCP copy, and prohibited-name checks pass. |
| Entity lead and JSON-LD | `test_use_case_has_entity_lead_and_visible_dated_jsonld` | Entity sentence leads, visible claims match JSON-LD, and Article date uses the image date. |
| AI instructions | `test_use_case_surface_lint_rejects_ai_instructions[instructions for AI]` and `[AI assistants should]` | Both prohibited phrases produce lint findings. |
| Coverage of noindex pages | `test_use_case_surface_lint_covers_noindex_pages` | A bad entity lead is rejected even on a noindex page. |
| Deterministic source date | `test_use_case_image_date_never_falls_back_to_build_clock` | Manifest date takes precedence, report date is the seed fallback, and missing dates fail. |
| Stable output and grouped index | `test_use_case_pages_are_stable_and_index_groups_registry_kinds` | Byte equality, both registry kinds, template links, and source sitemap dates pass. |
| Static integration and discovery | `tests/test_site_merge.py::test_use_case_pages_are_published_with_image_dates_and_method_discovery` | Red: missing `use-cases/index.html`, exit 1. Green: all template pages, method link, noindex exclusions, and image dates pass. |

The public-engine test was then strengthened with a deliberately invalid
private default registry. Before the isolation fix it returned exit 1:

```text
RegistryError: .../poison-private-default/registry: line 1: invalid data
1 failed, 59 deselected in 0.70s
```

The implementation now scopes the global registry to the public root and
restores it in `finally`. The strengthened test passed. The focused use-case
run returned exit 0, `13 passed, 47 deselected in 41.00s`.
The version guard passed both before and after implementation:
`test_use_case_complete_and_bounded_contracts_stay_pinned` checks complete
2.18 and bounded 1.5. It is a preservation check, not a pre-existing defect.

A browser check also caught decorative heading numbers inherited from the
shared CSS. Before the local override it returned exit 1:
`Error: Non-engine heading numbers: counter(sec, decimal-leading-zero)`.
The final check requires the pseudo-element content to be `none`.

## Commands and observed results

Commands ran from the assigned worktree. Exit codes were captured directly,
not through a pipe. Python is 3.14.4, pytest 9.1.1, Node v22.22.3, npm 10.9.8,
flock 0.4.0, git 2.50.1, gh 2.102.0, and Playwright CLI 0.1.22.
Node commands used `PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH`.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_pipeline.py -k use_case
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_pipeline.py -k use_case_decisions
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_site_merge.py -k use_case
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_pipeline.py tests/test_site_merge.py tests/test_surface_lint.py tests/test_structured_data.py tests/test_sitemap.py
```

The combined focused suites returned exit 0, `174 passed in 288.31s`.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
(cd web && npm ci && npm run build && npm test)
```

The static build returned exit 0. The web commands returned exit 0:
`52 passed | 1 skipped` test files, `843 passed` tests. The final static build
also includes the local CSS override that removes decorative numbers.

The actual public image date is `2026-09-23`. It produces 40 template pages
plus the index. There are 18 indexable template answers and 22 noindex pages.
A separate local check over all 41 pages returned `0 findings` for entity
leads, lexicon, and JSON-LD. The test suite checks both no-answer states.

For the independent build, this scratch script was executed with
`PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python .scratch/model-219/root/preview.py`:

```python
from pathlib import Path
from pipeline.build import write_use_case_pages
root = Path.cwd()
result = write_use_case_pages(root / '.scratch/model-219/root/preview', root)
print(f"Sitemap entries: {len(result['sitemap_paths'])}")
```

After both builds, this exact comparison was run in the same Python environment:

```python
from pathlib import Path
import hashlib
from pipeline.feedback_page import inject_tree
first = Path('.scratch/model-219/root/preview')
second = Path('dist/modelspec')
inject_tree(first)
pages = sorted((first/'use-cases').rglob('*.html'))
assert len(pages) == 41
for page in pages:
    other = second/page.relative_to(first)
    assert page.read_bytes() == other.read_bytes(), str(page)
digest = hashlib.sha256()
for page in pages:
    digest.update(page.relative_to(first).as_posix().encode())
    digest.update(page.read_bytes())
print(f'{len(pages)} independent engine-to-page outputs are byte-identical; sha256 {digest.hexdigest()}')
```

The final comparison returned exit 0:

```text
41 independent engine-to-page outputs are byte-identical; sha256 666fb2a4a810d18baf34e532685dd49c1913e15b9d7c7965b0105355ab789c34
```

The final static build returned exit 0. The final 41-page lint returned
`41 use-case pages checked; 0 findings`, exit 0. Browser verification
returned heading pseudo-element content `"none"` on the final page, and
`noindex, follow` with `noRecommendation: true` for `coding-fastest`.

The browser used a local server:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python -m http.server 8769 --bind 127.0.0.1 --directory dist/modelspec
/Users/terbeest/.codex/skills/playwright/scripts/playwright_cli.sh -s=model219 open http://127.0.0.1:8769/use-cases/coding/coding-best/
/Users/terbeest/.codex/skills/playwright/scripts/playwright_cli.sh -s=model219 resize 375 812
/Users/terbeest/.codex/skills/playwright/scripts/playwright_cli.sh -s=model219 screenshot --filename=output/playwright/model219-mobile.png
/Users/terbeest/.codex/skills/playwright/scripts/playwright_cli.sh -s=model219 resize 1440 1000
/Users/terbeest/.codex/skills/playwright/scripts/playwright_cli.sh -s=model219 screenshot --filename=output/playwright/model219-desktop.png
```

Browser assertions used the CLI's `eval` command. The red and final heading
check executed this function, returning exit 1 before and exit 0 after the CSS fix:

```javascript
() => { const content = getComputedStyle(document.querySelector("h2"), "::before").content; if(content !== "none") throw new Error("Non-engine heading numbers: " + content); return content; }
```

Mobile geometry returned viewport width 375 and document width 375, with
three band tables. The index returned 40 template links and the groups
`use` and `constraint`. The template link points to `/decide/?template=coding-best`.

```bash
git diff --exit-code 688f1072142a6824930dd1f17473d4d0050625cc HEAD -- decision/contract.py decision/bounded.py docs/decision-contract.md api/ranking/engine.py docs/legal models benchmarks offerings registry
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 4 --summary
git diff --check
```

These returned exit 0. No contract, ranking engine, legal, frozen-data, or
registry changes. No CLI agent bundle or OpenAPI hash regeneration is required.
The four predicted shard durations were each about 3573 seconds.

## Live composition after the scope exception

The orchestrator explicitly authorized `pipeline/live.py` and its tests.
The implementation copies the use-case directory into the live tree and
copies only source sitemap locations under `https://modelspec.dev/use-cases/`,
with their exact source dates. It does not infer sitemap membership from
copied files. An otherwise indexable page omitted from the source sitemap
also stays out of the live sitemap.

The live build before this change returned exit 2:

```text
error: 1 discovery links do not resolve in the live tree:
  method/index.html: /use-cases/
```

The three regression tests in `tests/test_live_use_cases.py` were added
before the implementation and returned exit 1, `3 failed in 1.06s`:

- `test_live_method_link_reaches_use_case_index`: `live.resolves` returned false.
- `test_live_sitemap_preserves_only_source_use_case_entries`: the expected source-listed URLs were absent.
- `test_live_use_case_lastmod_preserves_public_image_date`: both expected dates were null instead of `2026-01-17`.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_live_use_cases.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_live_use_cases.py tests/test_blog_deployment.py tests/test_surface_lint.py tests/test_sitemap.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_holding.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decide_preview_workflow.py -k live_assembly
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decide_preview_workflow.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
(cd web && npm ci && npm run build && npm test)
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.live build --src dist --web web/dist --out .scratch/model-219-resume/root/live
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

The focused live/blog/lint/sitemap suites returned exit 0,
`115 passed in 3.84s`. The web build and tests returned exit 0,
`843 passed`, with `52 passed | 1 skipped` files. The real-image integration
suite verifies exact source/live sitemap mapping equality, image dates,
all copied template pages, noindex exclusion, the method link, and no dead
links. The existing sitemap-count assertion now includes the exact source
use-case entries while retaining the checks for every static page.

The real-image suite returned exit 0, `43 passed in 230.33s`. The static
build returned exit 0. The live command returned exit 0:
`modelspec: 2706 files; discovery links resolve`. A separate artifact comparison
confirmed `41 use-case pages retained; 19 source-listed sitemap entries; 22
noindex pages excluded; lastmod 2026-09-23; no dead links`. Source and live HTML
for every use-case page were byte-identical.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree .scratch/model-219-resume/root/live/modelspec
```

The complete live-tree lint returned exit 0, `0 findings; 109 files checked`.

The existing workflow integration test used a hand-built source fixture with
neither the new directory nor a source sitemap. Its original run failed before
fixture updates with `FileNotFoundError: .../dist-v1/modelspec/use-cases`, exit 1,
`1 failed, 7 deselected in 12.57s`. The fixture now includes answered and noindex
examples plus source sitemap dates. All original holding/internal/live byte
checks remain, with new copied-page and exact sitemap assertions. Its full
module returned exit 0, `8 passed in 1.44s`.

The complete suite waited behind other reviews, acquired the shared lock,
and ran to completion without interruption. The exact locked command above
returned exit 0:

```text
11391 passed, 9 skipped, 11 warnings in 1279.44s (0:21:19)
```

The warnings are the existing unsigned-vocabulary warnings in CLI snapshot
and keyed-origin tests. The reported duration excludes time queued for the lock.

## Repository guard follow-up

CI's second pytest shard exposed removed-source literals in the new neutrality
test. The repository guard scans tracked tests as well as generated content.
The local reproduction returned exit 1:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_removed_sources.py
```

```text
FAILED tests/test_removed_sources.py::test_no_tracked_file_names_a_removed_source
1 failed, 4 passed, 1 skipped in 92.71s
```

The neutrality test now imports the existing `REMOVED_TEXT` pattern instead
of spelling those names in its forbidden-name tuple. This also covers separator
variants and removed measurement names. All other neutrality/access assertions
remain, and neither the repository guard nor its allowlist changed.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_removed_sources.py tests/test_pipeline.py::test_use_case_neutrality_and_access
```

The focused follow-up returned exit 0, `6 passed, 1 skipped in 103.67s`.
This test-only correction was made while the complete suite continued
uninterrupted; the focused command above exercises the final assertion.

## What was not observed

No deployed-site result, search indexing, answer-engine citation, or current
private-data result was measured. No vendor API calls,
credentials, paid-provider calls, production switches, Linear writes, or
merges were used. Local processes are closed before executor completion.
