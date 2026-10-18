# MODEL-219 part 2 execution evidence

Worktree: `/Users/terbeest/dev/worktrees/model-219-cmp`.
Branch: `model-219-comparison-pages`.
Draft PR: https://github.com/turbobeest/modelspec/pull/818.

Base SHA: `7908f238465ea88f0568738f13d8e8bbec949deb`.
Design-only first commit: `86fb8f663b63315c17c5f99891e0d29a0bac6cf6`.
Final implementation SHA: `7148004ef1ddad8fb4dfea20257ae65fbaa03cf4`.
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
on the final implementation. The full suite remains pending.

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
