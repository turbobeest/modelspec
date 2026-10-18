# MODEL-404 execution evidence

Draft PR: https://github.com/turbobeest/modelspec/pull/814. Work remained in
`/Users/terbeest/dev/worktrees/model-404`, on `model-404-simple-decide`.

- Base SHA: `72cd65f81aeae93add87b9a52157ae8cbce698a3`.
- Integrated main SHA: `0cf4080a72d354295c434206257d089d26b50ed6` (#811 and #812; #810 was already in the original base).
- Design-only first commit: `eeaf493e` (`docs/design/simple-decide-page.md`).
- Final product implementation SHA: `e0053beaa0515892667dfcbb3225422560ea43d5`.
- Final tested source SHA: `dcf398d6f27f8a84e72c5aef0492ec1f73aee1af`.
  This adds only a billing replay isolation fix and regression test. Later commits
  contain execution evidence only. The final PR body records the
  publication SHA including that evidence.

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
enforcement. No deployment or PR merge was performed. Current main was merged
into this branch for integration verification. The PR remains draft for
cross-model review and Jamie's visual review.

## Red-first results

Compact output is in [root/results.txt](MODEL-404/root/results.txt),
[routing/red.txt](MODEL-404/routing/red.txt),
[routing/jsonld-red.txt](MODEL-404/routing/jsonld-red.txt),
[transport/results.txt](MODEL-404/transport/results.txt), and
[gates/results.txt](MODEL-404/gates/results.txt). Large DOM dumps, superseded runs,
build trees and generated corpus responses remain local and ignored. Text excerpts
retain the recorded errors and results, with trailing whitespace removed.

| Defect / requirement | Red test and observed failure | Green result |
| --- | --- | --- |
| Simple page absent | `simple-decide.test.tsx` initially could not import `../simple/model`; this was a collection failure, not an assertion pass. Browser `opens with a labelled example and an alphabetical tie with equal emphasis` failed the missing labelled example. The first full simple browser run had six behavior failures. | 12 simple unit tests pass; simple browser cases pass in every gate combination. |
| New route and generated surfaces absent | `tests/test_simple_decide_routes.py`: five failures and one pass for missing detailed route/sitemap and old metadata/links/template destination. | All route tests pass, including composed output and deterministic source lastmod. |
| Normalized answer never displayed | `loads the labelled example and renders a picked job after request normalization`: could not find the six-way verdict; one failed, eight passed. | Loaded example and changed job both render. |
| Unsupported selected limits silently dropped | `refuses unsupported selected limits and a self-host question without its required gates`: expected null, received a broadened question. | Unsupported conditions stop selection; a rendered recovery test verifies that explicit removal preserves other limits, route and workload. A separate metadata-mutation test checks date, template count and task size. |
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
| Reviewed-catalogue test retained old agent-copy digests | CI shard 4 and the focused `test_flag_off_agent_copy_matches_reviewed_catalogue` run failed on the old MCP-copy SHA-256. Content review identified only the approved board-link and guide-version changes across MCP copy, guide Markdown and CLI text. | Three literal expected digests were updated in that test; response-byte assertions remain unchanged. `test_decision_link.py` and `test_agent_copy.py`: 63 passed. |
| Added board-link copy exceeded agent startup budget | Full Python and focused `test_coverage_pointer_keeps_all_three_mcp_first_turns_under_budget` failed: Gemini startup used 9,540 estimated tokens against the unchanged 9,500 limit. | The shared guide retains the board URL; duplicate MCP initialization wording was removed and transport wording shortened without changing request requirements. Generated totals are Claude 9,327, OpenAI 9,420 and Gemini 9,499. The five focused suites pass: 146 passed, 2 opt-in live probes skipped. |
| New main composer requires a source sitemap | CI's two `test_both_decide_routes_are_composed_and_describe_their_own_page` cases failed with a missing source `sitemap.xml` after #811 landed. | The fixture supplies `live.sitemap()`; all route and visible-content assertions remain. Both cases pass against the merged composer. |
| New use-case composition fixture omitted the detailed entry | All three `tests/test_live_use_cases.py` cases failed on missing `web/decide-details.html` after integration. | The fixture supplies both decide entries; the complete 11-test composition selection passes without assertion changes. |
| Billing replay removed imports needed by later hardware-fit schema generation | CI `test_schema_compaction_preserves_every_original_rule` failed with `KeyError: pydantic.root_model`. The local billing-then-schema sequence and a fresh-process regression reproduced it. | Restore only the three runtime stubs instead of the complete module table. Billing, smoke and guide suites pass 56 tests; the merged six-suite selection passes 149 with 2 opt-in skips. Real decision, hardware-fit and OpenAPI generation also pass after replay. |
| New use-case template action still used the first-visit URL | `test_use_case_neutrality_and_access` expected `/decide/details/?template=coding-best` and found the old URL. | The action now opens the detailed board; the test also preserves generic `/decide/` links. All 15 use-case tests pass. |

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

## Main integration

The PR became conflicting when #811 (use-case pages) and #812 (hardware-fit 2.0)
landed during verification. Main was merged without rewriting this branch's
history. The three conflicts were generated CLI/QA artifacts and literal
catalogue hashes. Agent copy was regenerated with `pipeline.agent_copy write`,
then checked; OpenAPI was generated before the QA capture through
`python -m qa.contracts`. Generated JSON was not hand-merged.

The three catalogue hashes were re-derived from the merged copy, guide and CLI
text. The disabled decision-link response-byte assertions are unchanged.
Hardware-fit code, snapshot schema, MCP fixture/generator/tests and server
snapshot match integrated main. Both generated hardware-fit 2.0 cases match
their saved fixture. MODEL-404's OpenAPI semantic difference from integrated
main is limited to the guide version in the description and response header.

About-page board links use `entity.BOARD` (`/decide/details/`). Use-case template
actions use `/decide/details/?template=...`; their generic navigation and free
lookup links retain `/decide/`. The merged copy stays within the unchanged
9,500-token startup limit: Claude 9,328, OpenAI 9,421 and Gemini 9,500.

The [published-file audit](MODEL-404/routing/final-artifact-audit.json) verifies
these link choices in the composed site, including all 40 use-case template
actions and 82 introductory links across 41 use-case pages. Both decide sitemap
entries use the source-derived date 2026-10-17.

Merge checks passed: 149 focused Python tests with 2 opt-in live probes skipped,
203 MCP tests, MCP typecheck, both generator checks and all source-hash checks.
The exact fixture failures and copy comparisons are in the routing evidence;
[MCP merge results](MODEL-404/transport/merge-mcp-results.txt) record preservation
of main's hardware-fit behavior. A queued full run was stopped before any tests
started so it could not read a merge in progress. The final locked run passed with
the completed merge and the test-only isolation correction below. The interrupted helper's earlier three-file fixture run
had no observed exit code and is not claimed as a pass.

CI on the merge commit exposed an independent test-order defect in the billing
replay helper. Its `patch.dict(sys.modules, ...)` restored the entire module
table, removing Pydantic submodules imported during replay while their parent
module retained cached class references. Hardware-fit 2.0 schema generation
then raised `KeyError: pydantic.root_model`. Both the CI sequence and a fresh
Python process reproduced the failure locally. The helper now restores only
`js`, `workers` and `bundled_data`. The new regression checks the unchanged
keyless-machine 401 response and subsequent hardware-fit 2.0 schema generation.
[Isolation evidence](MODEL-404/transport/import-isolation-results.txt) records
red/green commands and the real-engine follow-up probe. This correction touches
only the replay helper and its tests; no product or generated artifact changed.

## Verification

Tools: Python 3.14.4, pytest 9.1.1, Node v22.22.3, npm 10.9.8,
TypeScript 5.9.3 for web and 7.0.2 for MCP, Vitest 5.0.1, Playwright 1.63.0, Vite 8.0.3, Git 2.50.1.
Node commands use `/Users/terbeest/.nvm/versions/node/v22.22.3/bin` at the front
of `PATH`; Python uses `/Users/terbeest/dev/modelspec/.venv/bin/python`.
Exit codes were read directly from each process, never through a pipe.
Fresh web installation, build, unit tests, general browser tests and all four
gate combinations passed against the resolved merge working tree, committed as
`e0053beaa0515892667dfcbb3225422560ea43d5`. Final site composition, corpus and
screenshots use that product source. The full Python suite uses
`dcf398d6f27f8a84e72c5aef0492ec1f73aee1af`, which changes only the replay helper
and its new regression. Browser billing flows also passed after that correction in all four gate combinations.

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
| Built-page browser corpus | Exit 0: 112 passed, 10 expected skips in 24.4 seconds. Corpus regeneration produced 319 decisions and 5 vocabularies. |
| `python -m pipeline.build --out dist` | Exit 0: 2,641 site URLs and 2,605 Markdown pages. Existing frozen-data hardware-source warnings remain. |
| Real live composition | Exit 0: 2,711 files; discovery links resolve. |
| Surface lint on composed site | Exit 0: zero findings and notices across 111 checked pages. |
| Thin-page inspection and published artifacts | Exit 0: no thin pages among the 14 core pages. Both routes and sitemap dates pass; all 40 use-case template actions target the detailed board. Published agent/OpenAPI bytes match source. |
| Full Python suite under shared lock | Final exit 0: 11,536 passed, 9 skipped, 11 warnings in 1356.88 seconds. This supersedes the first run, which had 11,492 passed, 9 skipped and 2 failures from the stale catalogue pin and startup-copy budget. Both defects were corrected without weakening assertions or raising the budget. |
| Data freeze guard | Exit 0: `data freeze: ok`. |
| Agent-copy/OpenAPI checks and regenerated source hashes | Final exit 0 after ordered regeneration. Six focused Python suites pass: 149 passed, 2 live probes skipped. |
| MCP verification after merge | Typecheck and all 203 tests pass; hardware-fit parity checks pass. |
| Replay cleanup regression and browser checks | Exit 0: 56 billing/smoke/guide tests; the merged focused selection still passes 149 with 2 expected skips. Billing browser combinations pass 2, 2, 4 and 4 tests; the two skips in each visit-off run require visit support. |
| CI on final tested source | All checks pass or are intentionally skipped on `dcf398d6`, including Run pytest, Build both sites, evidence, data freeze, both Workers and all four browser gate combinations. [Recorded check set](MODEL-404/root/ci-source-results.json). |
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
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base 0cf4080a72d354295c434206257d089d26b50ed6 --head HEAD --branch model-404-simple-decide
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
`1-f226d9942791da1c`. Relative to integrated main, OpenAPI changes only the guide
version in its description and header constant. Request and feedback schemas are
unchanged from integrated main. Generation order
is agent copy, then OpenAPI, then QA capture, followed by checks after all writes.
The initial OpenAPI pass preceded guide generation and was superseded by this
final verification. Exact final hashes are in
[final-pins.txt](MODEL-404/routing/final-pins.txt).
The three literal reviewed-catalogue digests in `tests/test_decision_link.py`
were also refreshed after comparing the generated content with the base commit;
[catalogue-pin-review.txt](MODEL-404/routing/catalogue-pin-review.txt) records
that comparison, with linked red and green output in the routing evidence.
The subsequent startup-budget fix regenerated the same six files and refreshed
the MCP/guide expected digests again; the CLI-text expected digest did not change.
The final hashes are in `final-pins.txt`. The MCP route test checks the URL in
`context_guide`, where agents receive the shared guide; it does not require a
duplicate in initialization instructions. The existing 9,500-token test is
unchanged. The routing evidence records this final correction and measurements.

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
the question, snapshot and decision identity. All eleven screenshots were regenerated and inspected after main integration;
their bytes and recorded decision identities are unchanged. No current recommendation is
claimed. The screenshot vocabulary has no coverage date, so it shows
“Data date unavailable”; mutation tests separately prove metadata date rendering.

No paid provider calls, production decisions, live Turnstile challenge, private
data, recruited usability session, screen-reader session, Firefox or Safari run
was observed. Gate verification uses browser stubs and the real local Worker
admission service; it includes the unchanged keyless-machine HTTP 401 behavior.
Cross-model review and Jamie's visual review remain pending. The wsl gate was not
run, as required by the executor brief.
