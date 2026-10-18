# MODEL-404 execution evidence

Draft PR: https://github.com/turbobeest/modelspec/pull/814. Work remained in
`/Users/terbeest/dev/worktrees/model-404`, on `model-404-simple-decide`.

- Base SHA: `72cd65f81aeae93add87b9a52157ae8cbce698a3`.
- Design-only first commit: `eeaf493e` (`docs/design/simple-decide-page.md`).
- Final implementation and test SHA: `36a1dda13c6c8091dedd2fa13f067c363388976e`.
  Later commits contain execution evidence only. The final PR verification
  comment records the publication SHA including that evidence.

## Delivered behavior

`/decide/` starts with the labelled Everyday help example. Six jobs use existing
template tiers and supported constraints. Ties have equal emphasis and alphabetical
ordering; prices, providers, dates, counts and blend descriptions use the decoded
engine/vocabulary data. Missing data remains explicitly unavailable. The evidence
action carries the exact question to the existing board at `/decide/details/`.

Old stateful `/decide/` URLs redirect before rendering, preserving query and hash.
Detailed-board links, generated agent copy, metadata, composition, sitemap and
tests now target `/decide/details/`; introductory links retain `/decide/`.

The page reuses the existing request adapters and human/visit gates. Unsupported
selected conditions stop the request until explicitly removed. A snapshot refresh
that materially changes a question requires a new lookup; a metadata-only refresh
retries the same action. Neither path silently broadens the requested constraints.

No changes were made to decision contract 2.18, bounded 1.5, ranking floors,
neutrality terms, legal text, production switches, billing admission or access
enforcement. No deployment or merge was performed. The PR remains draft for
cross-model review and Jamie's visual review.

## Red-first results

Compact output is in [root/results.txt](MODEL-404/root/results.txt),
[routing/red.txt](MODEL-404/routing/red.txt),
[routing/jsonld-red.txt](MODEL-404/routing/jsonld-red.txt),
[transport/results.txt](MODEL-404/transport/results.txt), and
[gates/results.txt](MODEL-404/gates/results.txt). Large DOM dumps, superseded runs,
build trees and generated corpus responses remain local and ignored.

| Defect / requirement | Red test and observed failure | Green result |
| --- | --- | --- |
| Simple page absent | `simple-decide.test.tsx` initially could not import `../simple/model`; this was a collection failure, not an assertion pass. Browser `opens with a labelled example and an alphabetical tie with equal emphasis` failed the missing labelled example. The first full simple browser run had six behavior failures. | 12 simple unit tests pass; simple browser cases pass in every gate combination. |
| New route and generated surfaces absent | `tests/test_simple_decide_routes.py`: five failures and one pass for missing detailed route/sitemap and old metadata/links/template destination. | All route tests pass, including composed output and deterministic source lastmod. |
| Normalized answer never displayed | `loads the labelled example and renders a picked job after request normalization`: could not find the six-way verdict; one failed, eight passed. | Loaded example and changed job both render. |
| Unsupported selected limits silently dropped | `refuses unsupported selected limits and a self-host question without its required gates`: expected null, received a broadened question. | Unsupported conditions stop selection; two additional rendered recovery tests preserve other limits, route and workload after explicit removal. |
| Blend emphasis did not follow changed shares | `describes a changed blend without inventing a winner or workload mix`: expected greater conversational-evidence emphasis; received only the dimensions. | Share mutations change the plain-language emphasis. |
| Truncated rows falsely described as own hardware | `uses retained best-band routes and objective evidence when result rows are truncated`: expected `via Anthropic`, received own-hardware text and unknown cost. | Retained band routes supply provider/cost; genuinely absent route data says unknown. |
| Same-job pick left focus on the page body | The normalized-example test expected the verdict heading to have focus after clicking Everyday help; body retained focus. | Both same-job and changed-job picks focus the verdict. |
| Old request watchdog replaced a newer answer | `aborts a changed question and cannot display its delayed answer`: stale timeout replaced successful state. | Aborted requests cannot mutate the newer request state. |
| Snapshot workload changes reused a spent action | Transport snapshot regressions observed a changed-task request under the previous action. Real SQLite admission replay returned remaining counts 19, 18, 18 for old summary, changed summary, changed full. | Material changes stop before a changed request; manual mode requires new verification; automatic mode requires explicit Retry. Metadata-only changes preserve the existing action. |
| Detailed JSON-LD name absent from visible content | `test_decide_jsonld_names_and_descriptions_are_visible`: one detailed-page failure, one simple-page pass. Real surface lint reported two visibility findings. | JSON-LD matches the existing heading; 114 focused checks and real lint pass with zero findings. |
| Self-hosting could not be reselected after removing its defining limit | `can choose Self-hosting again after removing its open-weights limit and preserves explicit limits`: expected enabled, received a disabled button. | Availability uses the same candidate as the click action. Reselection restores template gates and retains the explicit no-training limit at all three priorities. |
| An unmeasurable route had no recovery action | Two `offers an explicit all-routes recovery for %s without changing the question` cases reproduced real-engine `no_feasible` shapes for chat apps and own hardware; both lacked `Try all routes`. | The explicit action changes only access. Complete request comparison verifies preservation of job, priority, limits, weights and workload; no automatic broadening occurs. |
| Mobile home target was too short | Expanded `the example fits 390 by 844 with readable contrast, full ties and 44px controls in both themes`: home link measured 28 px, expected at least 44. | A 44 px minimum home-link height passes the target checks while retaining the complete example inside 390 by 844. |
| OpenAPI retained the previous generated guide version | Local `api/worker/openapi.py --check` and CI Rank Worker bundle both exited 1 after agent-copy generation. | OpenAPI and its QA hash were regenerated after the guide. Final check and 56 API-doc tests pass; parsed YAML comparison confirms only the two guide-version values changed. |

The gate/browser matrix also checks state handoff, both legacy redirect forms,
separate EU/training constraints, route selection, response-derived numeric
changes, no-fit/undetermined behavior, keyboard focus, equal tie emphasis, contrast
and mobile fit. See [browser evidence](MODEL-404/gates/README.md),
[transport evidence](MODEL-404/transport/notes.md), and
[routing evidence](MODEL-404/routing/verification.md) for exact cases and commands.

An intermediate full web test run caught stale expectations for template preview
URLs. Preview pages remain at `/decide/templates/<id>/`; only their board
destination changed. Those expectations were corrected without changing the
preview route. Early browser runs during source edits had hot-reload failures;
all reported matrix runs used stable source. A detailed-board scroll test now waits
for its initial answer before holding the next request; its scroll assertion is
unchanged. Recovery component tests were added after the corresponding UI fixes;
no additional pre-fix red is claimed for those initial two tests. Later reselection
and route-recovery regressions were red-first. One concurrent corpus run failed
during trace teardown because another browser run cleaned the shared default
artifact directory. The final corpus invocation uses its own
`MODELSPEC_BROWSER_OUTPUT` directory; no application assertion was weakened.

## Verification

Tools: Python 3.14.4, pytest 9.1.1, Node v22.22.3, npm 10.9.8,
TypeScript 5.9.3, Vitest 5.0.1, Playwright 1.63.0, Vite 8.0.3, Git 2.50.1.
Node commands use `/Users/terbeest/.nvm/versions/node/v22.22.3/bin` at the front
of `PATH`; Python uses `/Users/terbeest/dev/modelspec/.venv/bin/python`.
Exit codes were read directly from each process, never through a pipe.

| Check | Result |
| --- | --- |
| `npm ci` | Exit 0. |
| `npm run build` (TypeScript and Vite) | Exit 0. Static fonts are supplied by the composed site, as before. |
| Full web `npm test` | Exit 0: 872 passed, 55 files passed and one opt-in corpus file skipped. |
| General `npm run test:browser -- --workers=2 --reporter=line` | Exit 0: 37 passed, 16 expected opt-in/gate skips. |
| Human off / visit off | Exit 0: 35 passed, 10 skipped. |
| Human on / visit off | Exit 0: 37 passed, 8 skipped. |
| Human off / visit on | Exit 0: 44 passed, 1 capture skipped. |
| Human on / visit on | Exit 0: 44 passed, 1 capture skipped. |
| Built-page browser corpus | Exit 0: 112 passed, 10 expected gate/capture skips; generated 319 decisions and 5 vocabularies. |
| `python -m pipeline.build --out dist` | Exit 0. Existing frozen-data hardware-source warnings were reported. |
| Real live composition | Exit 0: 2670 files; discovery links resolve. |
| Surface lint on composed site | Exit 0: zero findings across 70 files. |
| Thin-page inspection | `pipeline.live.thin_pages(...)` returned `[]`; composition also verified discovery links. |
| Full Python suite under shared lock | Pending: queued behind other tickets; result will be recorded before completion. |
| Data freeze guard | Exit 0: `data freeze: ok`. |
| OpenAPI check and regenerated source hashes | Final exit 0 after guide-version regeneration; 56 API-doc tests passed, 2 live probes skipped. |
| `git diff --check` | Exit 0. |

Root commands (run from this worktree unless a directory change is shown):

```bash
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
(cd web && npm ci)
(cd web && npm run build)
(cd web && npm test -- --run src/decide/__tests__/simple-decide.test.tsx)
(cd web && npm test)
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m tests.corpus decisions --out docs/evidence/g2-ios/MODEL-404/root/.corpus
(cd web && MODELSPEC_CORPUS_DIR=/Users/terbeest/dev/worktrees/model-404/docs/evidence/g2-ios/MODEL-404/root/.corpus MODELSPEC_BROWSER_OUTPUT=/Users/terbeest/dev/worktrees/model-404/docs/evidence/g2-ios/MODEL-404/root/.corpus-playwright npm run test:browser -- --config playwright.corpus.config.ts --workers=2 --reporter=line)
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.live build --src dist --web web/dist --out docs/evidence/g2-ios/MODEL-404/root/.live
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree docs/evidence/g2-ios/MODEL-404/root/.live/modelspec --report docs/evidence/g2-ios/MODEL-404/root/surface-final-report.json
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -c 'from pathlib import Path; from pipeline.live import thin_pages; assert not thin_pages(Path("docs/evidence/g2-ios/MODEL-404/root/.live/modelspec"))'
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base 72cd65f81aeae93add87b9a52157ae8cbce698a3 --head HEAD --branch model-404-simple-decide
git diff --check
CI_LOCAL_SKIP=1 git push -u origin model-404-simple-decide
```

Focused red/green commands and the four environment combinations are recorded in
the linked worker evidence. The deployed smoke is explicitly opt-in through
`MODELSPEC_DECIDE_URL`; ordinary browser runs do not contact production.

Regenerated required pins: `docs/agents.md`, `mcp/src/agent-copy.json`,
`cli/modelspec/agent-bundle.json`, `api/worker/src/agent_guide.py`,
`api/worker/openapi.yaml`, and `qa/fixtures/mcp-tools.json`. CLI source hashes match current source files and
QA capture hashes match `qa.contracts.source_hashes()`. Guide version:
`1-c87335a7b267ef2f`. OpenAPI changes only the guide version in its description
and header constant. Request and feedback schemas are unchanged. Generation order
is agent copy, then OpenAPI, then QA capture, followed by checks after all writes.
The initial OpenAPI pass preceded guide generation and was superseded by this
final verification. Exact final hashes are in
[final-pins.txt](MODEL-404/routing/final-pins.txt).

## Screenshots and limits of observation

Eleven inspected captures are in [MODEL-404/gates/](MODEL-404/gates/):
desktop and mobile example, coding, tie, no-fit, and detailed board, plus a full
mobile example. At 390 by 844, all example job buttons, priority choices, verdict,
six tied names/prices and the evidence action fit. Browser assertions verify
44-pixel job, priority, home, theme, Change and evidence controls, and 4.5:1
contrast for visible main-content text in the
initial example in both themes.

| State | Desktop | Mobile |
| --- | --- | --- |
| Example | [Capture](MODEL-404/gates/simple-desktop-example.png) | [Viewport](MODEL-404/gates/simple-mobile-example.png), [full page](MODEL-404/gates/simple-mobile-example-full.png) |
| Coding | [Capture](MODEL-404/gates/simple-desktop-coding.png) | [Capture](MODEL-404/gates/simple-mobile-coding.png) |
| Tie | [Capture](MODEL-404/gates/simple-desktop-tie.png) | [Capture](MODEL-404/gates/simple-mobile-tie.png) |
| No fit | [Capture](MODEL-404/gates/simple-desktop-no-fit.png) | [Capture](MODEL-404/gates/simple-mobile-no-fit.png) |
| Detailed board | [Capture](MODEL-404/gates/details-desktop.png) | [Capture](MODEL-404/gates/details-mobile.png) |

The example and tie use the existing captured assistant response. Coding and
no-fit use exact requests computed by the local engine against frozen data;
[screenshot-decisions.json](MODEL-404/gates/screenshot-decisions.json) records
the question, snapshot and decision identity. No current recommendation is
claimed. The screenshot vocabulary has no coverage date, so it shows
“Data date unavailable”; mutation tests separately prove metadata date rendering.

No paid provider calls, production decisions, live Turnstile challenge, private
data, recruited usability session, screen-reader session, Firefox or Safari run
was observed. Gate verification uses browser stubs and the real local Worker
admission service; it includes the unchanged keyless-machine HTTP 401 behavior.
Cross-model review and Jamie's visual review remain pending. The wsl gate was not
run, as required by the executor brief.
