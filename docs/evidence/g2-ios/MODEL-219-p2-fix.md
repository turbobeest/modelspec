# MODEL-219 part 2 execution evidence

Worktree: `/Users/terbeest/dev/worktrees/model-219-cmp`.
Branch: `model-219-comparison-pages`.
Draft PR: https://github.com/turbobeest/modelspec/pull/818.

The original execution below is historical. Round 2 records the display-name,
percentage and prose changes after REV-818 in the final section of this file.

Base SHA: `7908f238465ea88f0568738f13d8e8bbec949deb`.
Design-only first commit: `86fb8f663b63315c17c5f99891e0d29a0bac6cf6`.
Final implementation and test SHA: `5e7f10ae3a9a1fe68435bebcf4015ef1817a1bbe`.
The subsequent evidence-only commit records these results. Its final PR SHA
is available with `git rev-parse HEAD` on this branch and in the executor's
completion line; a commit cannot contain its own SHA.

## Result

The public image dated `2026-09-23` produces 40 comparison pages across
17 jobs, plus `/compare/`. The 18th answered template, `retrieval-private`,
has no eligible second model. Every pair contains the engine's leader and
another measured member of its best band or the next measured model in rank.
The code caps each job at five pairs and sorts model IDs for the URL.

The pages use the existing template decision unchanged. P(best) applies to
the complete ranked job lineup, including thin evidence, and excludes models
whose unknown objective values leave them unranked. The challenger's
`p_beats_leader` is shown separately. A best-band tie does not receive winner
styling. The shared named-model collector supplies sourced facts, missing
states, measurements and their conditions. The Worker retains its original
validation and response budget.

The design note was the only file in the first commit and was pushed before
opening the draft PR. `origin/main` was checked at the requested base; MODEL-404
was absent. The current board supports a template query but no model-pin URL,
so the links apply the template without claiming to pin either model.

## Red first

All pytest commands below used
`PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest`.
Tests were added before the corresponding production code.

| Defect or missing behavior | Test names | Observed red | Observed green |
| --- | --- | --- | --- |
| No comparison generation, selection, dated HTML or offline build | `test_pairs_use_leader_ties_then_next_rank_and_canonical_order`, `test_pairs_are_capped_without_promoting_thin_or_prior_only_estimates`, `test_unanswered_jobs_have_no_pairs`, `test_tied_page_shows_exact_engine_numbers_missing_facts_and_equal_rows`, `test_separated_verdict_states_job_date_and_probability_scope`, `test_unsupported_pair_is_noindex_and_does_not_claim_separation`, `test_page_uses_registry_copy_keyed_access_and_consistent_jsonld`, `test_real_image_is_public_offline_deterministic_and_bounded` | 9 failed; missing `pipeline.comparison_pages` | 25 passed, 46 deselected across comparison and existing use-case tests, including two real-image builds |
| No shared complete named-model projection | Four tests in `tests/test_model_comparison.py` | 4 failed; missing `decision.model_comparison` | 4 passed against the original inline Worker implementation before changing the wrapper; byte parity established |
| Live composition dropped comparisons; lint missed comparison leads and noindex discovery | Comparison cases in `tests/test_live_use_cases.py`, `tests/test_comparison_lint.py`, `tests/test_decide_preview_workflow.py` | 13 failed, 13 passed | 128 passed with `tests/test_surface_lint.py` |
| New collector absent from Worker packaging | `test_every_imported_repository_module_is_vendored` | 1 failed; `decide_service.py imports decision.model_comparison`, absent from `SOURCES` | 126 passed across packaging, collector, Worker and CLI comparison suites |
| Measurement conditions hidden and probability scope insufficiently precise | `test_measurements_keep_returned_conditions_and_probability_excludes_unranked` plus the tied and separated page tests | 3 failed; missing `xhigh` and `full ranked lineup for this job`; subsequent harness check failed on missing `unregistered` | 9 passed, 1 deselected after displaying returned conditions and clarifying unranked models |
| Template catalogue shadowed benchmark catalogue in the complete build | Required `pipeline.build --out dist` command | Exit 1, `AttributeError: 'dict' object has no attribute 'for_benchmark'` at `agent_ready.benchmark_markdown` | Complete static build exited 0 after retaining the benchmark catalogue |
| New assertions and evidence repeated excluded source names | `test_no_tracked_file_names_a_removed_source` | CI shard 2: 1 failed, 3,148 passed, 1 skipped; local reproduction: 1 failed, 5 deselected, identifying the test and evidence file | 14 passed, 1 skipped, 1 deselected in 90.20 seconds; assertions use the existing `decision.excluded.REMOVED_TEXT` pattern against raw HTML |

Representative red output:

```text
ModuleNotFoundError: No module named 'pipeline.comparison_pages'
9 failed in 0.74s

AssertionError: add to SOURCES in api/worker/vendor.py:
api/worker/src/decide_service.py imports decision.model_comparison (decision/model_comparison.py)
1 failed in 0.34s

AssertionError: assert 'xhigh' in page.visible
3 failed, 7 deselected in 0.65s

AttributeError: 'dict' object has no attribute 'for_benchmark'
```

## Commands and verification

Versions: Python 3.14.4, pytest 9.1.1, Node 22.22.3, npm 10.9.8,
Vite 8.0.3, Vitest 5.0.1, git 2.50.1, gh 2.102.0, flock 0.4.0.
Commands ran from the worktree root unless a `cd` is shown. Redirected
commands captured `$?` immediately, printed the log tail, and exited with
that original status. No test status was inferred through a pipe.

Focused red and green commands:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_comparison_pages.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_comparison_pages.py tests/test_pipeline.py -k 'comparison or use_case'
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_comparison_pages.py -k 'conditions or probability_scope or tied_page'
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_comparison_pages.py -k conditions
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_comparison_pages.py -k 'not real_image'
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_comparison.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_comparison.py tests/test_compare_models_worker.py tests/test_cli_compare_models.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_worker_vendor_imports.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_worker_vendor_imports.py tests/test_worker_bundle.py tests/test_model_comparison.py tests/test_compare_models_worker.py tests/test_cli_compare_models.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_live_use_cases.py tests/test_comparison_lint.py tests/test_decide_preview_workflow.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_live_use_cases.py tests/test_comparison_lint.py tests/test_decide_preview_workflow.py tests/test_surface_lint.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_removed_sources.py -k no_tracked_file
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_removed_sources.py tests/test_comparison_pages.py -k 'no_tracked_file or not real_image'
```

Generator:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --check
```

Exit 0. Vendored 124 files; the bundle imported with only its declared
dependencies. Generated files remain ignored. No response schema or golden
response changed, and no pin was hand-edited.

Required build and full suite:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
(cd web && PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm ci)
(cd web && PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm run build)
(cd web && PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm test)
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

The web commands each exited 0. TypeScript and the production Vite build
passed. Vitest reported 52 passed files, one skipped file, and 843 passing
tests in 19.44 seconds. The prebuild `pipeline.social_cards sync-meta`
generator produced no tracked changes. npm reported 10 existing dependency
audit findings; this change does not modify dependencies.

The final complete static build exited 0 after the catalogue and layout fixes. Live composition
exited 0 and reported `modelspec: 2748 files; discovery links resolve`.
Surface lint reported zero findings for the static tree's 5,362 checked files
and the live tree's 151 checked files. These checks were repeated successfully
on the final implementation. The full suite acquired the shared lock and
exited 0: **11,552 passed, 9 skipped, 11 warnings in 1,279.89 seconds
(21 minutes 19 seconds)**. The warnings came from CLI snapshot tests using
unsigned decision-vocabulary fixtures. Its log is retained locally as
`.model-219-p2/root/full-suite.log`. The suite ran against the final code and
tests, with only this evidence report edited afterward.

GitHub CI passed on implementation/test commit `5e7f10ae`: Run pytest,
Build both sites, Check evidence against release charts and Data freeze.
The source-guard fix passed its formerly failing shard. The browser matrix,
decision accuracy, Worker bundle, MCP and package checks also passed.
Status was read with `gh pr checks 818` and `gh pr checks 818 --required`.
The final evidence-only commit triggers fresh checks; their current status
is on the draft PR. No deployment or auto-merge ran.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.live build --src dist --web web/dist --out dist/live
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree dist/modelspec
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree dist/live/modelspec
```

## Local browser check

Used the Playwright CLI skill with a separate `model219p2` session and a local
server bound to `127.0.0.1:8879`. A context route aborted every URL outside
that local origin before navigating. No live Worker or external source was
visited. The initial `run-code` command used the wrong CLI syntax and did not
run; the corrected async-function command below did.

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python -m http.server 8879 --bind 127.0.0.1 --directory dist/live/modelspec
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex/skills/playwright/scripts/playwright_cli.sh --session model219p2 open about:blank
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex/skills/playwright/scripts/playwright_cli.sh --session model219p2 run-code 'async (page) => { await page.context().route("**/*", route => route.request().url().startsWith("http://127.0.0.1:8879/") ? route.continue() : route.abort()); await page.setViewportSize({width:1280,height:900}); await page.goto("http://127.0.0.1:8879/compare/coding-best/anthropic--claude-opus-5-5-vs-anthropic--claude-sonnet-5-5/"); }'
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex/skills/playwright/scripts/playwright_cli.sh --session model219p2 snapshot
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex/skills/playwright/scripts/playwright_cli.sh --session model219p2 screenshot --filename=desktop.png
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex/skills/playwright/scripts/playwright_cli.sh --session model219p2 resize 390 844
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex/skills/playwright/scripts/playwright_cli.sh --session model219p2 screenshot --filename=mobile.png
```

The snapshot identified the applied-template disclosure as `e76` and the
comparison-index link as `e322`. Clicking the disclosure showed the expanded
spec. Clicking the index link opened `/compare/` with 40 comparison links.
At a viewport width of 390 pixels, the document width was also 390 pixels.
The tables scrolled within 342-pixel containers. Screenshot inspection found
the model-name column too narrow, so it now reuses the existing
`use-case-model` minimum width. The nine focused rendering tests remained green.
Final layout reinspection passed on the rebuilt artifact: the model column
measured 180 pixels, while both viewport and document width remained 390
pixels. The final screenshot showed readable model IDs within the scrolling
table. The second browser session and local server were also closed.

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex/skills/playwright/scripts/playwright_cli.sh --session model219p2 click e76
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex/skills/playwright/scripts/playwright_cli.sh --session model219p2 eval '({viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,detailsOpen:document.querySelector("details").open,tables:[...document.querySelectorAll(".use-case-table")].map(el=>({width:el.clientWidth,content:el.scrollWidth}))})'
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex/skills/playwright/scripts/playwright_cli.sh --session model219p2 click e322
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex/skills/playwright/scripts/playwright_cli.sh --session model219p2 eval '({path:location.pathname,title:document.title,links:[...document.querySelectorAll("main a")].filter(a=>a.pathname.startsWith("/compare/")&&a.pathname!=="/compare/").length})'
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex/skills/playwright/scripts/playwright_cli.sh --session model219p2 close
```

The browser closed and the local server exited after Ctrl-C.

The independent real-output audit passed 2,288 assertions, including 680
numeric-value checks over all 40 pairs and the index. It compared against the
cached public decisions, checked canonical pair selection and offering IDs,
probability scope, structured data, image dates and access links. The 22
distinct external anchor URLs had no excluded source domains.
It did not rerun the engine or check remote source availability. The sorted
comparison-tree SHA-256 was
`21d468a861c38c80450c9825c73d8c5d649aeda605b8fdea4b559eb069e60da3`.
The operator-local audit script and log are retained as
`.model-219-p2/review-pages/audit-command.log` and `real-output-audit.log`.
The script can be rerun against the retained cached decisions and built tree:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/.model-219-p2/review-pages/audit-command.log
```

All operator-local logs, cached audit inputs and screenshots stay in that
ignored ticket scratch directory. They are not committed data or generated pins.

The real-image comparison test denies network connections, sets a nonexistent
private data overlay and a poisoned default registry, and verifies restoration
of the caller's registry. It builds twice, compares all 41 HTML files byte for
byte, checks the page count and image dates, and verifies keyed access and
neutrality text on every page.

Protected files were checked with:

```bash
git diff --exit-code 7908f238465ea88f0568738f13d8e8bbec949deb -- decision/contract.py decision/engine.py api/ranking/engine.py registry models benchmarks docs/legal
git diff --check
```

Both exited 0. The decision contract, engine ranking, published legal text and
frozen data are unchanged.

## Representative visible page text

Page: `/compare/coding-best/anthropic--claude-opus-5-5-vs-anthropic--claude-sonnet-5-5/`.
The following is visible text extracted from the generated HTML with
`pipeline.surface_lint.Page`, with line breaks added between paragraphs:

> anthropic/claude-opus-5-5 vs anthropic/claude-sonnet-5-5 for Coding, best available, as of 2026-09-23
>
> Find the active coding model with the strongest software-engineering evidence, whatever it costs.
>
> Worked example as of 2026-09-23, from the public data image.
>
> The evidence can't separate them for this job.
>
> anthropic/claude-sonnet-5-5 has probability 0.3891 of matching or exceeding anthropic/claude-opus-5-5 on this job's objective.
>
> Decision status: partial. P(best) and score intervals retain the full ranked lineup for this job, including models beyond this pair and models with thin evidence. Models with unknown objective values remain unranked and are outside this probability. P(best) is not a head-to-head probability. Separation from this challenger need not mean a unique best model across that lineup.

The model table preserves Opus's score `1.0`, interval `[0.661373, 1.338627]`,
P(best) `0.2109375` and task cost `0.24`; Sonnet's score `0.892297`, interval
`[0.538219, 1.246374]`, P(best) `0.1015625` and task cost `0.12`.
These are the engine's numbers, not independently verified benchmark claims.

## What was not observed

No private data checkout, live Worker request, vendor API call, deployment,
merge, Linear edit, production switch change, or paid-provider activity was
performed. Production crawl or search indexing was not observed. Browser
inspection covered a representative tied page and index; it did not exercise
the live decision service. Other page checks inspect generated HTML, visible
text, JSON-LD, links, lint findings and sitemap entries. Model pinning
was not observed because the current board does not support it in a URL.

The build reports pre-existing unregistered hardware-source warnings.
The frozen image includes evidence records whose dates are later than its
fallback image date; this work reproduces the image and engine results and
does not correct or independently verify frozen data. The first lint probe
ran on the incomplete failed build and reported missing generated files;
only a lint run after a successful build qualifies as final verification.

## Round 2: human-readable comparison pages

REV-818 approved `ab7a2342540507d005d1da394efbc24312c9d14a` without blocking
findings. This follow-up changes presentation only. Before editing, the requested
merge brought in `origin/main` at `b4a7074f37a3ba940bd86db9d1e2459a25fd40af`;
merge commit: `f46cd664ed57efaf1ef2d370d2ba16657f1b4b02`.
The first round 2 implementation commit is
`4746136a08fb3a6d5eef1a4a952c6cc224e85a06`; the metadata lint correction is
`4b0d8b72`. While verification was running, main reverted MODEL-402 in #819.
That revert (`34c6dbef95371cff728a7a28aba33dcffe3e50e3`) was merged cleanly
before final verification. The final implementation and merged-main SHA is
`67895a99289325af713f06f83b87be850c65d6b7`.
The subsequent evidence commit is identified by the final executor marker.

Display names come from the explicit frozen public root's model cards, using
the same `Model.display_name` property that feeds Decide's vocabulary. Missing
names fall back to IDs. URLs, pair order, engine lookups and `data-model` keep
the original IDs. Names are escaped in visible text and retained alongside
IDs in JSON-LD.

Probabilities use decimal half-up rounding after multiplication by 100.
Values below 0.01, including zero, display as `under 1%`; null displays as
`Unavailable`. For example, 0.63671875 becomes 64%, 0.3852 becomes 39%, and
0.015 becomes 2%. Exact response values remain in `data-probability` and
JSON-LD Dataset PropertyValue entries, identified by model and engine field.
Other engine numbers retain their original formatting. The design note
documents the rule. Mutations check both changed percentages and changed
exact values within the same rounding bucket.

The verdicts use plain sentences and public names. Only separated pages retain
the warning that separation from one challenger does not establish a unique
best model in the full lineup. The shared scope paragraph still explains
ranked, thin and unranked models. Pair selection and verdict logic are unchanged.

Round 2 red-first results (all failures were assertions or the missing name
argument, with direct exit 1; none were crashes):

| Behavior | Test | Red result | Green result |
| --- | --- | --- | --- |
| Display names, escaping and fallback | `test_display_names_replace_ids_in_visible_copy_and_fall_back_when_absent` | 1 failed: unexpected `model_names` argument | Included in 40 passing final rendering tests |
| Readable tied and separated sentences | `test_tied_page_formats_probabilities_and_keeps_other_engine_numbers_and_equal_rows`, `test_separated_verdict_states_job_date_and_probability_scope` | 2 failed: requested percentages and sentences absent | Included in 40 passing final rendering tests |
| Percentage boundaries and exact HTML/JSON-LD trace | `tests/test_comparison_probability_trace.py` | 19 failed: probability spans and Dataset absent | 20 passed, including the additional same-bucket mutation |
| Article follows the rounded number | `test_probability_articles_follow_the_rendered_number` | 6 failed, 4 passed: `a 8%`, `a 11%`, `a 18%`, and `a 80%`–`a 89%` | Included in 40 passing final rendering tests |
| Probability metadata passes the existing surface checks | `test_rendered_comparison_probability_data_passes_structured_data_lint` | 4 failed, 1 corruption guard passed: unrecognized PropertyValue and invisible field labels; both artifact lints reported 240 findings | 169 passed, 1 real-image test deselected across rendering and lint suites |

Commands ran from the same worktree, using Python 3.14.4, pytest 9.1.1,
Node 22.22.3 and npm 10.9.8. Each command's exit status was read directly.
The following commands produced the red results, then the green results
after the corresponding implementation change:

```bash
git fetch origin main
git merge --no-ff origin/main -m 'MODEL-219: merge origin/main before comparison-page polish' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_comparison_pages.py -k display_names
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_comparison_pages.py -k 'tied_page or separated_verdict'
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_comparison_probability_trace.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_comparison_probability_grammar.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_comparison_probability_grammar.py tests/test_comparison_probability_trace.py tests/test_comparison_pages.py -k 'not real_image'
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_comparison_pages.py tests/test_comparison_probability_trace.py tests/test_comparison_lint.py tests/test_model_comparison.py tests/test_live_use_cases.py tests/test_decide_preview_workflow.py tests/test_holding.py tests/test_worker_vendor_imports.py
```

The final rendering command passed 40 tests with one real-image test deselected
in 0.87 seconds. The broader focused command passed 105 tests in 401.23 seconds,
including the offline real-image test and its byte-identical builds. That
broader command started before the final article correction; the full suite
below covers the final code, including that correction and the new grammar tests.

The repository generators verified the merged pins rather than hand-merging
them. Worker vendoring regenerated 124 ignored files and passed isolated imports.
The CLI bundle, OpenAPI YAML and complete QA MCP capture already matched their
generators, so they needed no tracked changes. All commands exited 0:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import json
from pathlib import Path
from qa.contracts import capture_tools
path = Path('qa/fixtures/mcp-tools.json')
expected = json.dumps(capture_tools(), indent=2, ensure_ascii=False) + '\n'
if path.read_text() != expected:
    print('QA MCP capture differs from the repository generator; regeneration requires review.')
    raise SystemExit(1)
print('QA MCP capture exactly matches its generator; no regeneration required.')
PY
```

Web verification ran each command separately from `web/` with
`PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH`,
`npm_config_offline=true` and `npm_config_audit=false`:

```bash
npm ci
npm run build
npm test
```

All exited 0. The build compiled TypeScript and Vite 8.0.3. Vitest 5.0.1 passed
843 tests across 52 files, with one file skipped, in 20.17 seconds. Prebuild
created no tracked web changes. The npm cache supplied all packages offline.

Round 2 logs are retained under the ignored `.model-219-p2/` ticket scratch
directory: `root/round2/`, `compare-trace/grammar-*`,
`review-pages/round2-*` and `integration-plan/round2/`.

The metadata fix adds only `PropertyValue` to the reviewed schema-type allowlist
and uses visible property labels. Schema.org explicitly permits that type in
a Dataset's [variableMeasured](https://schema.org/variableMeasured) and documents
its [propertyID, value and unitText fields](https://schema.org/PropertyValue).
All generic name/description visibility checks remain intact. A corruption
test verifies that an invisible probability label still fails lint.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_comparison_lint.py -k probability
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_comparison_lint.py tests/test_surface_lint.py tests/test_structured_data.py tests/test_comparison_probability_trace.py tests/test_comparison_probability_grammar.py tests/test_comparison_pages.py -k 'not real_image'
git fetch origin main
git merge --no-ff origin/main -m 'MODEL-219: follow main revert before final verification' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
```

The first queued full-suite command was stopped while still waiting for the
shared lock (exit 143, no pytest output), so it could not test a partial merge.
An in-progress build was also stopped (exit 143). After the clean merge,
vendoring refreshed the Worker bundle before the full suite was requeued.
Other tickets' lock holders and test processes were untouched.

The local browser check used the Playwright workflow recorded above, with
session `model219r2`. External requests were aborted before navigation. The
separated page below was inspected at 390 × 844; the tied page at 1280 × 900.
Document widths equalled their viewport widths. Both screenshots show readable
display names, whole percentages and the expected verdict. DOM inspection
confirmed exact probability attributes and the existing template links.
The browser session and local HTTP server were closed. This visual check preceded
the metadata-label correction and main's revert; neither changes visible copy
or CSS. The final artifact audit and lint run cover those subsequent changes.

### Round 2 visible text: tied page

Page: `/compare/assistant-balanced/anthropic--claude-opus-5-5-vs-google--gemini-3-8-flash/`.

> Claude Opus 5.5 vs Gemini 3.8 Flash for General assistant (balanced), as of 2026-09-23
>
> The evidence can't separate them for this job.
>
> Gemini 3.8 Flash has a 42% chance of matching or beating Claude Opus 5.5 on this job's objective.

The exact challenger value is 0.4154. Table P(best) values 0.4140625 and
0.0703125 display as 41% and 7%. There is no separation caveat on this tie.

### Round 2 visible text: separated page

Page: `/compare/assistant-best/anthropic--claude-fable-5-vs-anthropic--claude-opus-5-5/`.

> Claude Fable 5 vs Claude Opus 5.5 for General assistant (best available), as of 2026-09-23
>
> The evidence separates them: Claude Opus 5.5 leads for General assistant (best available), with a 64% chance of being the best model in the full lineup for this job, as of 2026-09-23.
>
> Claude Fable 5 has a 25% chance of matching or beating Claude Opus 5.5 on this job's objective.

The exact leader P(best) is 0.63671875 and the challenger probability is 0.2473.
Fable's table P(best), 0.1015625, displays as 10%. These values remain engine
outputs from the frozen image, not independently verified benchmark claims.

### Round 2 final artifact checks

After merging main's revert, all four generator checks ran again and exited 0.
The rendering/lint regression command above then passed 169 tests with one
real-image test deselected in 3.39 seconds. The final artifact commands were:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.live build --src dist --web web/dist --out dist/live
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree dist/modelspec
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree dist/live/modelspec
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/.model-219-p2/review-pages/audit-command.log
```

All exited 0. Static lint checked 5,362 files with zero findings; live lint
checked 151 files with zero findings. Live composition reported 2,748 files
and resolving discovery links. The independent audit passed 2,809 assertions,
including 680 numeric checks, over all 40 pairs across 17 jobs and the index.
It checks raw traces against cached public engine responses and percentages
against the documented rounding rule. Public card names, unchanged numeric
cells, canonical IDs, full-lineup scope, keyed access and neutrality agree.

There are 25 tied and 15 separated pages. All 41 HTML files are distinct and
byte-identical between the static and live trees. Their canonical-path SHA-256
is `fafd6132cc169c2e32ef31f3e222a49a605a281670d01b9029cbf6b867284a8a`.
The final quotes above were extracted again from this artifact. Sitemaps retain
the public image date, `2026-09-23`.

Final artifact logs are `root/round2/build-after-revert.log`,
`live-after-revert.log`, `lint-static-final.log` and `lint-live-final.log`;
the independent audit files are `review-pages/final-after-revert-*.log`.
Generator logs use the `-after-revert` suffix.

The full suite ran under the shared lock against the final implementation:

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Direct exit 0: **11,588 passed, 9 skipped, 11 warnings in 1396.25 seconds**
(23 minutes 16 seconds). The warnings concern unsigned vocabulary fixtures in
the existing CLI snapshot tests. The log is
`root/round2/full-suite-after-revert.log`. This includes the final real-image
test's two byte-identical builds, all rounding/mutation and metadata-lint
regressions, and the preserved comparison/Worker behavior.

The final `git fetch origin main` still returned
`34c6dbef95371cff728a7a28aba33dcffe3e50e3`; MODEL-404/#814 was not merged.
Links therefore remain `/decide/?template=<id>`. The single PR metadata query
confirmed #818 is open and draft on `model-219-comparison-pages`, targeting main.
No PR metadata was changed. The final documentation commit and push follow
these successful checks.

```bash
git diff --exit-code origin/main -- decision/contract.py decision/engine.py api/ranking/engine.py registry models benchmarks docs/legal
git diff --check
gh pr view 818 --json number,state,isDraft,headRefName,headRefOid,baseRefName,url
CI_LOCAL_SKIP=1 git push -u origin model-219-comparison-pages
```

The protected-file comparison and whitespace check exited 0. No contract,
ranking, frozen-data or legal edits are introduced by this PR. Round 2 did not
deploy, merge the PR, query the live Worker, call a paid provider, access private
data, or observe production search indexing. Its browser checks used local
artifacts and blocked external requests. All launched browser, server, build,
generator and test processes finished or were explicitly stopped as noted.
