# MODEL-404 execution evidence

Draft PR: https://github.com/turbobeest/modelspec/pull/814. Work remained in
`/Users/terbeest/dev/worktrees/model-404`, on `model-404-simple-decide`.

## Round 3 — snapshot date and objective source

Review input: `/Users/terbeest/.codex-g2/exec/REV-814.verdict.md`, reviewed
HEAD `53fde1fd302da4fd050758d42a4c5ead8bd7a593`. The two blocking findings are
fixed in `09bbb4203e00fb99a72379c11801885a3f6dae7f`. The historical-fixture
provenance assertion is corrected in `2488fbc3`. Main later advanced to
`34c6dbef95371cff728a7a28aba33dcffe3e50e3` (#819, reverting #813). It is
integrated in merge `fcf541f03455c5a95168572093cef5a161a5bef5`, the final tested
source for this round. The earlier full suite was interrupted at 88% before
changing source; its exit 130 is recorded, with no pass claimed.

The Worker's display projection preserves the snapshot date as optional top-level
`as_of`, copied from the same full vocabulary's `coverage.as_of`. Catalogue counts
remain trimmed. The header reads that field, with full-vocabulary coverage as a
fallback. Absent dates remain explicit. Vocabulary version 1, decision 2.18 and
bounded 1.5 stay unchanged: this is additive optional vocabulary metadata under
MODEL-59. The frontend schema, vocabulary documentation and OpenAPI generator
include the field. The flag-on OpenAPI response schema proves it is optional;
the committed flag-off YAML has no display-vocabulary route. The date addition
does not change that artifact; the subsequent #819 integration regenerates it
with main's removal of successor health metadata.

The answer source comes from the unique largest-share estimated capability term.
It uses that term's contribution evidence on each verdict member's best-ranked
offering, including retained `top` contributions when needed. Across tied members,
priority is highest `estimate_weight`, direct before proxy, then record id in the
engine's Unicode code-point order; model id breaks an otherwise equal member tie.
This rule is independent of result, member and evidence-array order. Missing or
conflicting metadata, ambiguous capability terms and missing display names use
"Sources and dates: see the full evidence". Unweighted domain groups do not
supply a replacement source. The exact rule is also in the
[design](../../design/simple-decide-page.md).

| Finding | Observed red | Observed green |
| --- | --- | --- |
| Snapshot date dropped by trim | Trim assertion received no `as_of`; rendered header could not find `Data as of 2026-10-04`. The immutable pre-review browser bundle also showed the unavailable-date text with the genuine generated fixture. | Trim/OpenAPI: 33 passed. Vocabulary/vendor: 77 passed. Header/recovery: 7 passed. Browser date assertion passes without grafted coverage. |
| Source followed result order | The review's Gemini-first mutation changed WebDev to Arena Elo — Coding in both rendered unit and immutable pre-review browser runs. The initial source run had 18 failures. | 54 focused simple tests pass, including 23 source cases; browser reorder and evidence permutations retain the literal WebDev line. |
| Conflicting duplicate offering metadata | Two additional rendered cases failed the full-evidence fallback. | Both now fall back; merely reordered equivalent records still produce the same source. |
| Historical capture compared with new vocabulary | Fresh web run: five snapshot assertions failed. Captured decisions retain contract 2.12/snapshot `snap_483dd2fb6c5915b5`; the real generated vocabulary is contract 2.18/snapshot `snap_e9c30eaacfa8f2f2`. | Eight fixture-stub tests pass. Original response bytes are unchanged; the test explicitly pins their historical snapshot and still exercises matching a request with the new vocabulary snapshot. |

The vocabulary fixture is produced by the repository snapshot/vocabulary code and
actual `trim()`, with the vendor's model and enum allowlists. It uses the frozen
public repository at snapshot date 2026-10-04, not production or private data.
Its 44 model names and 40 template specs match the previous capture; 28 templates
are available. The [producer and provenance](MODEL-404/routing/round3/README.md)
record the exact inputs and hashes. Historical decision stubs remain clearly
labelled; new screenshot decisions use this same generated snapshot and verify
every request against its generated response. The new Coding capture cites
CursorBench 4.0 (2026-09-28) from software-engineering contribution evidence;
the example and tie cite Arena WebDev (2026-09-23).

Round 3 command results and screenshots are recorded in
[final root results](MODEL-404/root/round3/post819/results.txt),
[initial root red/green results](MODEL-404/root/round3/results.txt),
[post-#819 routing results](MODEL-404/routing/round3/post819/README.md),
[source results](MODEL-404/transport/round3/notes.md), and
[browser evidence](MODEL-404/gates/README.md).

The required checks were rerun after #819 on source
`fcf541f03455c5a95168572093cef5a161a5bef5`:

| Verification | Final result |
| --- | --- |
| `pipeline.build --out dist` | Exit 0 |
| Fresh `npm ci` / `npm run build` | Both exit 0 |
| `npm test` | 898 passed; one opt-in corpus file skipped; exit 0 |
| `npm run test:browser` | 38 passed, 16 expected skips; exit 0 |
| Four human/visit gate combinations | 36/10, 38/8, 45/1, 45/1 passed/skipped; all exit 0 |
| `pipeline.live build` | 2,711 files; discovery links resolve; exit 0 |
| Surface lint | 0 findings across 111 pages; exit 0 |
| Full pytest, shared lock, 4 workers, `--dist loadfile` | **11,540 passed, 9 skipped, 11 warnings in 1271.39s; exit 0** |
| Data freeze / protected code / composed link audit | Pass; About and all 40 use-case template pages retain the inventory |
| Screenshot capture | All 11 regenerated and inspected after #819; hashes match the manifest |

The post-#819 full run waited for the shared lock, then ran to completion without
source changes. Later commits contain evidence only. The regenerated OpenAPI hash
is `4856fae354f22642f19b77c57b18d823a59ed0d4ccb1cf159f6e0d3d68b3ab0e`;
the QA capture hash is
`221a6438534b4cad5890261ddbc7fb2eb839df53f053ada475ce1d88ac8a50de`.
The other four generated artifacts and all three literal catalogue digests remain
unchanged. All six artifact hashes and all eleven screenshot hashes were verified
against their recorded manifests.

At the final source-CI observation, 15 checks passed and six deployment/auto-merge
checks were skipped. The remaining Python shard (1/4) was still running; no CI
failure was reported. `Build both sites`, `Check evidence against release charts`
and `Data freeze` passed. The aggregate `Run pytest` check awaits that shard;
its CI pass is not claimed. See the [captured source-CI state](MODEL-404/root/round3/post819/ci-source-results.json)
and [test workflow](https://github.com/turbobeest/modelspec/actions/runs/39105507954).
The final evidence-only push starts a fresh CI run.

No production deployment or live decision, paid-provider call, Firefox/Safari
run, assistive-technology session or recruited usability session was performed.
The PR remains draft for independent follow-up review and Jamie's visual review.
The final evidence-only handoff SHA is recorded in the PR body and executor result;
the reproducible tested source SHA is above.

## Earlier implementation and integration evidence

The remaining sections record work through `53fde1fd`. Their test totals and
source SHAs are historical; round 3 verification above supersedes them.

- Base SHA: `72cd65f81aeae93add87b9a52157ae8cbce698a3`.
- Prior integrated main SHA: `b4a7074f37a3ba940bd86db9d1e2459a25fd40af`
  (#813 and #816, following the first integration of #811 and #812; #810 was already in the original base).
- Design-only first commit: `eeaf493e` (`docs/design/simple-decide-page.md`).
- MODEL-404 implementation SHA: `e0053beaa0515892667dfcbb3225422560ea43d5`.
- Prior product/build source SHA: `1b3d8e3a66b3ddf572702ab11e3d40fdbc580226`.
  Product code, generated artifacts, composed pages and screenshots retain this source.
- Prior final tested source SHA: `f4b13af3e11618304a73d07bcec685fe372e46cc`.
  Its only source change awaits actual verdict focus in the Coding unit assertion.
  Full Python passed with 11,584 tests; all required CI checks passed.
- Earlier fully verified source SHA: `dcf398d6f27f8a84e72c5aef0492ec1f73aee1af`.
  This added a billing replay isolation fix and regression test. Its complete
  Python and CI passes below are historical evidence, not results for the second merge.

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
| Coding unit assertion ran before scheduled verdict focus | CI on `1b3d8e3a`, human off / visit on, expected the verdict `h2` to have focus but received `body`. The other three gate jobs passed. Twelve local iterations and all 1,271 corpus-enabled unit tests passed before the fix; only CI reproduced the intermittent failure. | Test-only `f4b13af3` uses `waitFor` around the actual focus assertion. Twelve post-fix iterations and all 1,271 corpus-enabled unit tests pass. Suppressing focus still makes the assertion fail; that negative control was removed. Runtime code is unchanged. |

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

The first integration followed #811 (use-case pages) and #812 (hardware-fit 2.0), which
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
started so it could not read a merge in progress. That integration's locked run passed with
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

Main then advanced to `b4a7074f37a3ba940bd86db9d1e2459a25fd40af` with #813
(MODEL-402 bundled snapshot boundaries) and #816 (MODEL-403 MCP API-key headers
and discovery). The second merge is `1b3d8e3a66b3ddf572702ab11e3d40fdbc580226`.
Only the QA capture conflicted; ordered regeneration resolved it. Main's Worker
entry, decision service, vendor, vocabulary and OpenAPI generator retain exact
upstream bytes. OpenAPI preserves main's optional snapshot-health metadata;
its difference from main remains the two MODEL-404 guide-version values.
The QA capture changes only its server and OpenAPI source hashes. Existing
literal catalogue digests, tool definitions and guide version remain unchanged.

[Late routing verification](MODEL-404/routing/late-merge-verification.md)
records 149 focused Python passes with 2 opt-in skips, 48 snapshot/header/vendor
and midnight-refresh passes, both generator checks, and matching source hashes.
[Late MCP verification](MODEL-404/transport/late-merge-mcp-results.txt) records
typecheck and all 233 tests passing. Its parity check preserves all 32 upstream
MCP/registry files, including key normalization, refusal behavior and discovery.
[Fresh browser evidence](MODEL-404/gates/late-merge-results.txt) records the
web suite, all four gate combinations and eleven regenerated, inspected captures.

The [latest published-file audit](MODEL-404/routing/late-artifact-audit.json)
matches the composed build to `1b3d8e3a`: both decide entries and source dates,
all 40 detailed-board template actions, 82 introductory links, and exact published
agent/OpenAPI bytes pass. All 22 noindex use-case pages are absent from the
sitemap. The final full Python suite passed on the test-only correction
`f4b13af3` described below. Earlier full and CI passes remain historical evidence.

CI on `1b3d8e3a` subsequently exposed an intermittent focus assertion in the
human-off/visit-on unit job; the other three gate jobs passed. The assertion
observed the loaded Coding answer before its scheduled verdict focus. The
test-only correction `f4b13af3e11618304a73d07bcec685fe372e46cc` awaits the existing
`toHaveFocus()` assertion with `waitFor`, without increasing a timeout. It changes
no runtime code, build output or generated artifact. Twelve local iterations and 1,271 corpus-enabled unit
tests passed both before and after the correction, so no local reproduction of
the intermittent CI failure is claimed. A temporary negative control suppressed
focus and still failed the awaited assertion; it was removed before commit.
[Focus verification](MODEL-404/gates/focus-race-results.txt) records those results
and four final keyboard-flow browser checks, each returning exit 0 with one pass
across the four human/visit gate combinations. Full Python and CI passed on the
corrected testing source.

## Verification

Tools: Python 3.14.4, pytest 9.1.1, Node v22.22.3, npm 10.9.8,
TypeScript 5.9.3 for web and 7.0.2 for MCP, Vitest 5.0.1, Playwright 1.63.0, Vite 8.0.3, Git 2.50.1.
Node commands use `/Users/terbeest/.nvm/versions/node/v22.22.3/bin` at the front
of `PATH`; Python uses `/Users/terbeest/dev/modelspec/.venv/bin/python`.
Exit codes were read directly from each process, never through a pipe.
Product and artifact results below use the resolved second merge,
`1b3d8e3a66b3ddf572702ab11e3d40fdbc580226`; the focus checks use test-only
`f4b13af3e11618304a73d07bcec685fe372e46cc`. Fresh web installation,
build, unit/browser suites, gate matrix, screenshots, corpus, site composition and
surface lint passed. Browser billing flows include the merged Worker and replay
cleanup correction. The full Python suite passed with `f4b13af3` unchanged
throughout the run; only evidence files were edited while it ran.

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
| Built-page browser corpus | Exit 0: 112 passed, 10 expected skips in 23.5 seconds. Corpus regeneration produced 319 decisions and 5 vocabularies. |
| `python -m pipeline.build --out dist` | Exit 0: 2,641 site URLs and 2,605 Markdown pages. Existing frozen-data hardware-source warnings remain. |
| Real live composition | Exit 0: 2,711 files; discovery links resolve. |
| Surface lint on composed site | Exit 0: zero findings and notices across 111 checked pages. |
| Thin-page inspection and published artifacts | Exit 0: no thin pages among the 14 core pages. Both routes and sitemap dates pass; all 40 use-case template actions target the detailed board. Published agent/OpenAPI bytes match source. |
| Focus assertion correction at `f4b13af3` | Twelve post-fix iterations and all 1,271 corpus-enabled unit tests pass. Each of four gate combinations passes its targeted keyboard-focus browser check. The temporary negative control failed when focus was suppressed and was then removed; runtime behavior is unchanged. |
| Latest full Python suite under shared lock | Direct exit 0 on `f4b13af3`: 11,584 passed, 9 skipped, 11 warnings in 1213.18 seconds (20 minutes 13 seconds). Testing source remained unchanged throughout the run. |
| Historical full Python suite | Exit 0 on `dcf398d6`: 11,536 passed, 9 skipped, 11 warnings in 1356.88 seconds. This corrected the earlier run's stale catalogue pin and startup-copy budget failures, which had left 11,492 passed, 9 skipped and 2 failed. Assertions and the budget remain intact. |
| Data freeze guard | Exit 0: `data freeze: ok`. |
| Agent-copy/OpenAPI checks and regenerated source hashes | Exit 0 after ordered regeneration. Six focused Python suites pass: 149 passed, 2 live probes skipped. [Latest pins](MODEL-404/routing/late-merge-pins.json). |
| Snapshot integration | Exit 0: 48 successor, response-header, vendor and midnight-refresh tests pass. |
| MCP verification after second merge | Typecheck and all 233 tests pass; upstream source, header/discovery and hardware-fit parity checks pass. |
| Historical replay cleanup regression | Exit 0: 56 billing/smoke/guide tests and billing browser combinations of 2, 2, 4 and 4 passes. The current complete gate matrix above also covers billing after the second merge. |
| Historical CI on `dcf398d6` | All checks passed or were intentionally skipped, including Run pytest, Build both sites, evidence, data freeze, both Workers and all four browser gate combinations. [Earlier check set](MODEL-404/root/ci-source-results.json). |
| Final CI on `f4b13af3` | Complete: 17 successful, 6 intentionally skipped, 0 failed. All required checks passed. Aggregate Run pytest completed at 2026-10-18 05:37:00 UTC; [final check snapshot](MODEL-404/root/ci-late-source-results.json) was captured at 05:37:56 UTC. |
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
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree docs/evidence/g2-ios/MODEL-404/root/.live/modelspec --report docs/evidence/g2-ios/MODEL-404/root/surface-late-merge-report.json
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -c 'from pathlib import Path; from pipeline.live import thin_pages; assert not thin_pages(Path("docs/evidence/g2-ios/MODEL-404/root/.live/modelspec"))'
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base b4a7074f37a3ba940bd86db9d1e2459a25fd40af --head HEAD --branch model-404-simple-decide
git diff --check
CI_LOCAL_SKIP=1 git push -u origin model-404-simple-decide
```

Focused red/green commands and the four environment combinations are recorded in
the linked worker evidence. The deployed smoke is explicitly opt-in through
`MODELSPEC_DECIDE_URL`; ordinary browser runs do not contact production.

Regenerated artifacts are [docs/agents.md](../../agents.md),
[MCP copy](../../../mcp/src/agent-copy.json),
[CLI bundle](../../../cli/modelspec/agent-bundle.json),
[Worker guide](../../../api/worker/src/agent_guide.py),
[OpenAPI](../../../api/worker/openapi.yaml), and
[QA capture](../../../qa/fixtures/mcp-tools.json). CLI source hashes match current source files and
QA capture hashes match `qa.contracts.source_hashes()`. Guide version:
`1-f226d9942791da1c`. Relative to integrated main, OpenAPI changes only the guide
version in its description and header constant. Request and feedback schemas are
unchanged from integrated main. Generation order
is agent copy, then OpenAPI, then QA capture, followed by checks after all writes.
The initial OpenAPI pass preceded guide generation and was superseded by this
final verification. Exact current hashes are in
[final-pins.txt](MODEL-404/routing/final-pins.txt) and
[late-merge-pins.json](MODEL-404/routing/late-merge-pins.json). After the second
merge, OpenAPI is `7e30bfcd60cef8ba9b273650e05186a35581eb7fddf82be3614c45ed4036aa3b`
and QA capture is `4e19159461875c105ca223eda3e5932a3d2801a4cce28040f69257fa6084f1f4`;
the other four hashes are unchanged.
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
the question, snapshot and decision identity. All eleven screenshots were regenerated and inspected after the second main integration at `1b3d8e3a`;
their bytes and recorded decision identities are unchanged. No current recommendation is
claimed. The screenshot vocabulary has no coverage date, so it shows
“Data date unavailable”; mutation tests separately prove metadata date rendering.

No paid provider calls, production decisions, live Turnstile challenge, private
data, recruited usability session, screen-reader session, Firefox or Safari run
was observed. Gate verification uses browser stubs and the real local Worker
admission service; it includes the unchanged keyless-machine HTTP 401 behavior.
Cross-model review and Jamie's visual review remain pending. The wsl gate was not
run, as required by the executor brief.

## Main sync after approval

This is the requested merge-only sync of draft PR #814. The approved starting
head was `7b833056a4cb8aa10c0f56cf6001b13224634ada`. `git fetch origin` followed by
`git merge origin/main` integrated main `8971608aab849862b4a4870f1bc06e46fc9e7dd2`,
including #808, #824 and #825 and the intervening main changes. Merge commit
`61e8dbfa2e69077f6ed72940eaf0789d558188df` retains both parents. No rebase or reset
was used. Later changes in this sync contain evidence only.

The merge command exited 1 with exactly four content conflicts. All four were
resolved as follows:

| Conflicted file | Resolution |
| --- | --- |
| `cli/modelspec/agent-bundle.json` | Regenerated with `pipeline.agent_copy write`. This preserves #814's detailed-board guidance and main's MODEL-406 source-pin formatting. The merged generator source hash was derived by the generator. |
| `qa/fixtures/mcp-tools.json` | Recaptured with `qa.contracts` after regenerating agent copy and OpenAPI. This retains main's separate source-key/digest layout and derives the merged OpenAPI hash. Tool descriptions and input schemas remain unchanged. |
| `tests/replay_billing_launch.py` | Both branches fixed the same module-cleanup defect. Kept main's helper byte-for-byte: restore only `js`, `workers` and `bundled_data` in `try/finally`, distinguish absent entries from entries holding `None`, and preserve newly imported modules. |
| `tests/test_billing_launch.py` | Combined the required imports and retained both regression families without changing their assertions: main's absent/module/`None` cases and #814's subsequent OpenAPI/hardware-fit schema generation case. |

Main's guides, comparison pages, platform drafts, surface-lint implementation and
remaining fixture fixes survive. The approved `web/` tree and vocabulary date
projection are byte-identical to the starting head. Both `/decide/` and
`/decide/details/` remain present. Generic navigation and free-human lookup links
still target `/decide/`. The new guide and comparison "Apply this template"
buttons target `/decide/details/?template=...`, exactly like #814's equivalent
use-case action; their existing test expectations follow that destination.
The same template and state reach the detailed board. No new page behavior was
introduced in the resolution.

Generators ran in dependency order using the repository virtual environment:
`python -m pipeline.agent_copy write`, OpenAPI generation, then
`python -m qa.contracts`. The exact `python -m api.worker.openapi` module command
also returned 0 with byte-identical output. Agent-copy and OpenAPI checks returned
0. No generated field or pinned hash was edited by hand. The three existing
catalogue digest assertions need no update. Only the CLI bundle, OpenAPI YAML
and QA capture changed from the approved head; the full hashes and source-pin
checks are in [generated artifact evidence](MODEL-404/routing/sync/README.md).

Verification uses Python 3.14.4 and Node 22.22.3 with npm 10.9.8. Commands were run
from the authorized worktree and their direct exits were observed:

| Check | Observed result |
| --- | --- |
| Site build | Exit 0 in the prior sync session. |
| Surface lint and built-link audit | Both exit 0 in the prior sync session. |
| Fresh web install / build / unit tests | All exit 0; 898 tests passed. |
| Generated-pin focused suite | Exit 0; 235 passed, 2 skipped. |
| Billing merge-resolution suite | Exit 0; 44 passed. |
| Resumed agent-copy / OpenAPI / QA generator commands | All exit 0; all nine generated artifacts unchanged. |
| Locked full pytest on the sync merge | Exit 0 on `61e8dbfa`: 12,102 passed, 9 skipped, 11 warnings in 1408.89s. |

MODEL-404-sync2 resumed from `61e8dbfa2e69077f6ed72940eaf0789d558188df`.
A fresh `git fetch origin` confirmed that main remains at `8971608a`, so no
further merge or site/web rebuild was needed. PR #814 was observed open and
draft. Its locked pytest log stops without a summary line and is not a pass.
MODEL-404-sync3 fetched again at 2026-10-18 21:58:06 UTC. Main was still
`8971608a`, so the recorded site build and web chain were not repeated.
`pipeline.agent_copy check`, `api.worker.openapi --check` and `qa.contracts`
each exited 0, and the nine generated artifacts were unchanged.
The locked suite then exited 0: 12,102 passed, 9 skipped, 11 warnings in
1408.89s (23 minutes 28 seconds), from 21:58:33Z to 22:22:02Z. Python 3.14.4,
pytest 9.1.1 and flock 0.4.0. The tested source stayed `61e8dbfa` throughout.
Approved `web/` and `display_vocabulary.py` remain byte-identical to
`7b833056`. The eleven warnings are unsigned decision-vocabulary fetches in
the CLI snapshot tests. This continuation changes evidence only and needs no
new red-first regression test. Earlier red/green observations remain recorded
below.

The initial billing/agent-guide check ran while the QA fixture still contained
conflict markers. Its five artifact parse failures disappeared after capture;
no implementation or assertion changed in response. The rerun passed all 44
checks. [Billing resolution evidence](MODEL-404/transport/sync/notes.md) records
both runs and the comparison preserving every original test body and decorator.

Exact commands and merge inputs are in [root sync results](MODEL-404/root/sync/results.txt)
and [merge inputs](MODEL-404/root/sync/merge-inputs.txt). Fresh web results are in
[web sync results](MODEL-404/gates/sync/results.txt). The generated-pin focused suite
passed 235 tests with two skips, including main's byte-stability, stale-pin and
independent-pin merge checks. No screenshots or browser matrix were rerun for
this merge-only sync. No deployment, paid-provider call, PR readiness change or
PR merge was performed. The PR stays draft and awaits Jamie's look.
