# MODEL-219 executor evidence

Status: READY for review of the round 3 presentation follow-up. Focused
checks, both static builds, the live build, web tests, artifact comparisons,
and the new complete pytest run under the shared lock pass. PR #811 remains draft.

Base SHA: `688f1072142a6824930dd1f17473d4d0050625cc`.
Final implementation SHA: `19a157633d53afba2d826c80ba9b61d1d2fc6937`.
The following evidence-only commit is the final PR HEAD. Its exact SHA is
recorded in the executor completion line and PR body after
commit, avoiding a self-referential commit hash inside this file.

The first commit is the required design document, `63647dba`. The draft PR
was opened from that commit before implementation.

Earlier sections retain the original slice's evidence. The round 3 section
below records the final presentation behavior and newest validation results.

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

## Round 3: human rendering after REV-811

Round 3 base: `5290708b1ffeb757e02cacc0cfb37e0196f40d68`.
Grok's REV-811 verdict approved that head with no blocking findings.
This follow-up changes only human rendering, its tests, and documentation.
Missing cells say "Unavailable"; missing tie-breaker lines are omitted without
inventing a reason. Boolean values and requirements read "Yes" or "No".
The expandable applied spec uses labeled fields and lists without JSON quoting.
Every empty band loses its table and heading, while nonempty bands retain
their members. Numeric values still use the original JSON numeric serialization,
without rounding. Engine responses, JSON-LD, indexability, and sitemap logic
are unchanged.

### Red first

The first combined red run exposed the rendering failures and a missing
`facets` argument in the new test setup. That setup was corrected before
counting the standalone assertion below as a rendering failure.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_pipeline.py::test_use_case_values_are_readable_without_changing_engine_precision tests/test_pipeline.py::test_use_case_tie_is_not_a_cost_recommendation tests/test_pipeline.py::test_use_case_page_preserves_engine_values_and_registry_copy tests/test_site_merge.py::test_built_use_case_pages_have_no_visible_json_literals
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_pipeline.py::test_use_case_values_are_readable_without_changing_engine_precision
```

| Defect | Red assertion from unchanged rendering |
| --- | --- |
| Raw values in built pages | `test_built_use_case_pages_have_no_visible_json_literals` found standalone `null` in pages including `assistant-balanced`. |
| Boolean expressions, missing cells, and quoted spec | `test_use_case_values_are_readable_without_changing_engine_precision` failed on visible `false`, exit 1, `1 failed in 0.63s`. |
| Missing tie-breakers | `test_use_case_tie_is_not_a_cost_recommendation[False]` found `Fastest tie-breaker: null`. The populated case already passed and remains covered. |
| Missing cells | `test_use_case_page_preserves_engine_values_and_registry_copy` expected `Unavailable` but found the old missing-value rendering. Numeric and registry assertions stayed intact. |

After the value fix, these commands checked rendering and reproduced the band defect:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_pipeline.py -k 'use_case_page_preserves or use_case_tie or use_case_values'
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q --tb=short --show-capture=no tests/test_pipeline.py::test_use_case_without_answer_is_noindex_and_absent_from_sitemap tests/test_site_merge.py::test_built_use_case_pages_have_no_visible_json_literals tests/test_site_merge.py::test_built_use_case_pages_have_no_empty_band_tables
```

The first returned exit 0, `4 passed, 58 deselected in 0.67s`.
The second demonstrated the separate band defect, exit 1,
`2 failed, 2 passed in 158.54s`. The all-page literal scan now passed, while
the fully undetermined example still contained `<h3>Best band</h3>` and
`<tbody></tbody>`. The new all-page empty-table test also failed.
Only then was the empty-band guard added.

### Green checks and actual builds

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_pipeline.py tests/test_site_merge.py tests/test_live_use_cases.py tests/test_surface_lint.py tests/test_structured_data.py tests/test_sitemap.py tests/test_decide_preview_workflow.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_pipeline.py -k 'use_case_page_preserves or use_case_tie or use_case_values or use_case_without_answer'
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
(cd web && npm ci && npm run build && npm test)
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out .scratch/model-219-round3/root/rebuild
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.live build --src dist --web web/dist --out .scratch/model-219-round3/root/live
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree .scratch/model-219-round3/root/live/modelspec
```

All returned exit 0. Focused suites: `189 passed in 252.51s`.
The final targeted renderer checks: `6 passed, 56 deselected in 1.37s`.
They preserve the exact `0.12345678912345678` probe and interval endpoints,
assert the response is unmodified, cover all available tie-breakers, and retain
the noindex and thin-evidence assertions while checking absent band headings.
The build-level tests scan every use-case page, including the index and noindex
examples, for standalone `null`, `true`, or `false`, and empty band tables.

Web build and tests: `843 passed`, `52 passed | 1 skipped` files.
Live composition: `modelspec: 2706 files; discovery links resolve`.
Live-tree lint: `0 findings; 109 files checked`.
Tool versions and the Node PATH are unchanged from the commands section above.

The explicit source/rebuild/live artifact comparison ran this command and
returned exit 0:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python .scratch/model-219-round3/root/verify_artifacts.py
```

The comparator was:

```python
from pathlib import Path
import hashlib
import re
import xml.etree.ElementTree as ET

from decision.templates import load_templates
from pipeline import build, live, surface_lint

source = Path('dist/modelspec')
repeat = Path('.scratch/model-219-round3/root/rebuild/modelspec')
published = Path('.scratch/model-219-round3/root/live/modelspec')
pages = sorted((source / 'use-cases').rglob('*.html'))
assert len(pages) == len(load_templates()) + 1
digest = hashlib.sha256()
noindex = set()
tables = 0
for path in pages:
    rel = path.relative_to(source)
    raw = path.read_bytes()
    assert raw == (repeat / rel).read_bytes() == (published / rel).read_bytes(), rel
    page = surface_lint.Page(raw.decode())
    assert not re.search(r'\b(?:null|true|false)\b', page.visible, re.I), rel
    assert not re.search(r'"(?:spec_version|where|optimize|weights|task_tokens)"\s*:', page.visible), rel
    assert 'Human lookup is free' in page.visible, rel
    assert 'CLI, API, and MCP access requires a key' in page.visible, rel
    for table in re.findall(r'<table\b[^>]*>.*?</table>', raw.decode(), re.S):
        assert ET.fromstring(table).findall('./tbody/tr'), rel
        tables += 1
    if 'noindex' in page.meta['robots']:
        noindex.add('https://modelspec.dev/' + path.parent.relative_to(source).as_posix() + '/')
    digest.update(rel.as_posix().encode())
    digest.update(raw)
assert (source / 'sitemap.xml').read_bytes() == (repeat / 'sitemap.xml').read_bytes()
prefix = 'https://modelspec.dev/use-cases/'
maps = [{url: date for url, date in surface_lint.sitemap_entries((tree / 'sitemap.xml').read_text())
         if url.startswith(prefix)} for tree in (source, repeat, published)]
assert maps[0] == maps[1] == maps[2]
assert maps[0].keys().isdisjoint(noindex)
assert set(maps[0].values()) == {build.use_case_image_date(Path.cwd()).isoformat()}
assert not live.dead_links(published)
print(f'{len(pages)} byte-identical source/rebuild/live pages; {tables} nonempty band tables; no visible JSON literals or quoted spec keys')
print(f'{len(maps[0])} source-listed sitemap entries; {len(noindex)} noindex pages excluded; lastmod {next(iter(maps[0].values()))}; no dead links')
print(f'Use-case sha256 {digest.hexdigest()}')
```

```text
41 byte-identical source/rebuild/live pages; 51 nonempty band tables; no visible JSON literals or quoted spec keys
19 source-listed sitemap entries; 22 noindex pages excluded; lastmod 2026-09-23; no dead links
Use-case sha256 bd376b7012a71bf02f488409f3507c6051bb2fbce063c00ff4417d34fc7937b8
```

The two complete source sitemaps were also byte-identical. Every page retains
the free human lookup and keyed CLI/API/MCP lines. No pinned CLI agent bundle
or OpenAPI hashes require regeneration. `git diff --check` and the protected-file
diff command above pass. Four predicted pytest shard durations remain balanced
at about 3570 seconds each, with 70 files per shard.

```bash
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

The new full run waited behind other reviews, acquired the shared lock,
and completed without interruption. Its captured exit code was 0:

```text
11395 passed, 9 skipped, 11 warnings in 1430.05s (0:23:50)
```

The duration excludes time queued for the lock. The warnings are the same
unsigned-vocabulary warnings in the CLI snapshot and keyed-origin tests.
The renderer code and tests were unchanged during this complete run.
The tracked-source guard also passed after the new evidence was written:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_removed_sources.py::test_no_tracked_file_names_a_removed_source
```

The final rerun returned exit 0, `1 passed in 4.56s`.

## What was not observed

No deployed-site result, search indexing, answer-engine citation, or current
private-data result was measured. No vendor API calls,
credentials, paid-provider calls, production switches, Linear writes, or
merges were used. Local processes are closed before executor completion.
