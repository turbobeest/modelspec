# MODEL-401 hardware-fit lower-bound evidence

Draft PR: [#812](https://github.com/turbobeest/modelspec/pull/812).
Status: READY. The locked full suite, focused checks, and applicable CI checks pass.
PR #812 remains a draft for cross-model review.

Base SHA: `a551fe82eef93fcb1d4389a435b2f62927d0a25e`, also the fetched
`origin/main` used for the publication comparisons. The first commit,
`03006c6684c79343b1139c72e1b26880a8b304ea`, changes only the design note.
Final implementation SHA: `2cd5f104c362d5c40ba5f10dbba5a7d01fca8df5`.
The delivery SHA is the evidence commit containing this file, resolved with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-401-fix.md`.

Worktree: `/Users/terbeest/dev/worktrees/model-401`.
Branch: `model-401-hardware-fit-lower-bound`.

## Behavior and original red-first checks

A verified fixture with 65,500,000,000 weight bytes, 100,000 KV bytes per token,
batch 2, context 1,024, and 32,000,000,000 capacity bytes returns hardware-fit
2.0, `status: estimated`, `basis: lower_bound`, and `estimated_fit: unlikely`.
Its per-device lower bound is 65,704,800,000 bytes and its margin is
-33,704,800,000 bytes. Missing headroom is an explicit `not_required` object
with a reason. Numeric input records, citations, capacity provenance, and
winning verification are retained.

Under-capacity and equality cases without headroom return `undetermined`,
naming missing runtime headroom. Full estimates retain their arithmetic and
add `basis: full`. Measurements, keyed-only access, Decision 2.18, bounded
1.5, ranking, and frozen data are unchanged.

The original Python red run against unchanged code returned 7 failed and
12 passed. The Worker red returned 4 failed. MCP red returned 3 failed and
34 passed. The original red outputs are preserved for
[Python](MODEL-401/executor/python-red.log.gz),
[Worker](MODEL-401/executor/worker-red.log.gz), and
[MCP](MODEL-401/mcp/red.log.gz).

| Defect or invariant | Red-first test | Red observation | Green observation |
| --- | --- | --- | --- |
| Over-capacity weights without headroom | `test_qwen_like_weights_exceed_capacity_without_runtime_headroom` | Undetermined instead of estimated | Exact lower bound, negative margin, signed snapshot round trip |
| Under capacity and equality | `test_lower_bound_at_or_below_capacity_needs_sourced_headroom` | Record rejected, generic missing-record inputs | Both name missing headroom and abstain |
| Full estimate | `test_estimated_workload_reports_literal_formula_inputs_and_never_asserts_fit` | Version 1.0 instead of 2.0 | Basis full, version 2.0, previous literal arithmetic |
| Mixed device inputs | `test_mixed_headroom_topology_uses_each_device_lower_bound` | Undetermined instead of lower-bound estimate | Per-device bounds, no pooled memory |
| Untrusted sources | `test_untrusted_parameters_cannot_become_estimates` | All 12 baseline trust guards passed | Excluded, unregistered, or invalid verification still abstains |
| Worker contract and forwarding | `test_keyed_worker_returns_the_lower_bound_assessment_unchanged`, `test_hardware_fit_transport_refusals_keep_its_own_contract` | Old status/version | Fetched and bundled signed snapshots preserve the assessment |
| MCP description and parity | `matches the generated Python API $basis assessment`, `lists an optional strict workload schema and distinguishes estimates from measured fit` | Old API version, missing basis guidance | Both complete generated API bodies survive MCP forwarding unchanged |
| Response schema | `test_lower_bound_response_schema_forbids_likely_and_fabricated_headroom` | Missing estimated result, later an invalid discriminator target | Schema accepts the real result and rejects likely or numeric-zero headroom |
| Maximum topology | `test_maximum_topology_without_headroom_returns_a_valid_undetermined_response` | Reason exceeded its 512-character limit | Valid explanation for 1,024 devices |

The [schema red](MODEL-401/executor/schema-red.log.gz) and
[topology red](MODEL-401/executor/topology-red.log.gz) retain the later review
findings. Further regressions bind headroom's absence to verification and
keep absent headroom distinct from sourced zero. Existing no-`fits` tests
remain intact.

Original red and focused commands ran from the worktree root:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_hardware_fit.py -k 'qwen_like or lower_bound or mixed_headroom or untrusted_parameters or estimated_workload'
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_hardware_fit_worker.py -k 'lower_bound or transport_refusals'
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_hardware_fit.py -k maximum_topology
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_hardware_fit.py -k response_schema
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_hardware_fit.py tests/test_hardware_fit_worker.py tests/test_decision_snapshot.py tests/test_agent_copy.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_api_docs.py tests/test_agent_overhead.py
```

The final pre-exception focused runs passed 215 tests, and 57 tests with
2 skipped respectively. [Original MCP commands](MODEL-401/mcp/commands.md)
record dependency setup, the original Node-only CI dependency correction,
fixture generation, type checking, and 203 passing MCP tests. The shared
API fixture is generated by the real Python checker; a Python test checks
both complete bodies against that checker, while Node consumes the JSON
without requiring Python application packages.

## Publication checks resolved under the scope exception

The first locked full suite exited 1 with 18 failed, 11,452 passed,
24 skipped, and 11 warnings in 1,178.23 seconds. Its
[complete log](MODEL-401/executor/full-suite.log.gz) and
[failure summary](MODEL-401/executor/full-suite-summary.txt) are retained.
Fourteen failures concerned the stale MCP capture, one the reviewed-copy
hash, one the OpenAPI size, and two missing local `@playwright/test` packages.
The [initial CI findings](MODEL-401/review/findings.md) preserve that diagnosis.
The executor initially stopped because the capture and pin were outside the
named paths. The orchestrator then explicitly granted those paths, required
an unchanged byte cap and a semantics proof, authorized the PR body update,
and required web dependency installation and a full-suite exit of zero.

The resumed QA red returned 2 failed in
[qa-red.log.gz](MODEL-401/resume/qa-red.log.gz). The OpenAPI budget red failed
`235348 <= 233000` in
[red-budget.log.gz](MODEL-401/openapi-resume/red-budget.log.gz).

The QA capture was regenerated with `python -m qa.contracts`, never edited by
hand. Only `hardware_fit.description` differs in the tool entries against
origin/main. Its input schema and all other tool entries are identical. The
derived source hashes for `api/worker/openapi.yaml` and
`mcp/src/agent-copy.json` also refresh. No capture helper needed changing.

The reviewed agent-copy hash changes from
`faa19be299fb233c78d366f2fed67897f45b87d89d2bad40f96faa2f6f3841b7` to
`0618ceb1e4cc7e951378ce188f2b061327c61c02da5bf53d9f099be7a5befc6a`.
Only `tools.hardware_fit` changes in the generated copy; guide and CLI text
pins are unchanged. The [scope proof](MODEL-401/resume/verify_copy_scope.py)
checks those facts and the unchanged tool inputs. The exact old and final
text is retained in [copy-review.json](MODEL-401/resume/copy-review.json) and
quoted side by side in PR #812's body.

After the first capture refresh, the first-turn test exposed a second budget
failure, 9,529 tokens against 9,500. Its output is retained in
[focused-tests-after-capture.log.gz](MODEL-401/openapi-resume/focused-tests-after-capture.log.gz).
The hardware-fit description was shortened from the interim 650 characters
to 524. It retains the exact measurement, sourced estimate, full and lower-bound
basis rules, no-proof-of-fit caveat, per-device decimal GB, key, price, and
model-selection boundary. No other description or token limit changed.
Final estimated first-turn totals are Claude 9,326, OpenAI 9,419, and Gemini
9,498. All remain under the existing 9,500 limit.

The generator's existing schema-sharing cutoff changes from 80 to 72
characters of canonical schema text. The size measurements are:

| Cutoff | Generated bytes | Existing cap |
| --- | ---: | ---: |
| 80 | 235,348 | 233,000 |
| 74 | 233,251 | 233,000 |
| 72 | 230,602 | 233,000 |

The [adapted #806 proof](MODEL-401/openapi-resume/verify_openapi_compaction.py)
expands generated `Shared` references and verifies that all 174 public
components and 19 paths exactly match the previously generated 2.0 document.
It retains titles, descriptions, null and non-null defaults, and constraints.
Against fetched origin/main at a551fe82, its separate #806-compatible check
permits exactly four new and four changed HardwareFit schemas. Every path
object and all other OpenAPI content remain identical. The schema is
230,602 bytes, 2,398 below the unchanged cap. No schema YAML was hand-edited,
and no budget or acceptance assertion was weakened.

## Resumed commands and results

Python commands run from the worktree root. Node commands use
`PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH` and run from the
indicated directory. Each result is the command's direct exit status.

```sh
git fetch origin main
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-401/resume/verify_copy_scope.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-401/openapi-resume/verify_openapi_compaction.py --base-ref origin/main
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.agent_harness --first-turn-breakdown
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_api_docs.py tests/test_agent_guide.py tests/test_hardware_fit.py tests/test_hardware_fit_worker.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_harness.py tests/test_agent_gaps.py tests/test_decision_link.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_landing.py
PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH" PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_social_cards.py::test_build_emits_every_template_preview_and_card tests/test_social_cards.py::test_every_frozen_template_card_has_clean_chromium_layout
```

From `web/`, `PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH" npm ci`
exited 0 and installed 346 packages. Both previously failing social-card
tests then passed, exit 0, in 198.03 seconds. No web failure is ignored.
From `mcp/`, snapshot refresh used `npm test -- --run test/server.test.ts -u`
and changed only the hardware-fit description snapshot. Final `npm test`
passed all 203 tests and `npm run typecheck` exited 0.

The resumed API/hardware set passed 177 tests with 2 skipped, exit 0. The
QA/decision-link set passed all 170 tests, exit 0. The generator, compaction,
and scope checks all exited 0. Logs are under `MODEL-401/resume/` and
`MODEL-401/openapi-resume/`; compressed logs are readable with `gzcat` or
Python's `gzip` module.

The required full-suite rerun uses the pinned Node directory inherited through
PATH and the exact shared-lock command:

```sh
export PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH"
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

The first resumed locked run exited 1 with 11,473 passed, 9 skipped,
11 warnings, and 12 fixture errors in 1,122.07 seconds. All twelve errors
were `tests/test_landing.py::test_landing_behaviour_in_browser` cases:
`npm ci` enabled the browser fixture, which requires the previously absent
`web/dist/decide.html` and assets before browser launch. Its
[complete log](MODEL-401/resume/full-suite-before-web-build.log.gz) and
[summary](MODEL-401/resume/full-suite-before-web-build-summary.txt) are retained.

From `web/`, with the pinned Node PATH, `npm run build` then exited 0 and
generated those assets. `npm test` passed all 843 web tests (52 files passed,
one file skipped), exit 0. The complete landing suite passed all 33 tests,
including the twelve browser cases, exit 0, in 189.61 seconds. No test or
assertion changed, and no dependency failure is ignored. The corresponding
logs are `resume/web-build.log.gz`, `resume/web-tests.log.gz`, and
`resume/landing-after-web-build.log.gz`.

All 18 applicable CI checks passed on both
`a66d4170889f74fa35624e1984df0a537f8d986f` and
`2919a7e029605c3e249bfec45039fe5c4d9e5f92`; six deployment or merge checks
were skipped. The read-only command `gh pr checks 812 --json name,state`
exited 0, recorded in
[ci-a66d4170.json](MODEL-401/resume/ci-a66d4170.json) and
[ci-2919a7e0.json](MODEL-401/resume/ci-2919a7e0.json).

The full-suite retry after the web build exited **0** with **11,485 passed,
9 skipped, and 11 warnings in 1,218.92 seconds (20:18)**. It tested
`2919a7e029605c3e249bfec45039fe5c4d9e5f92` using the exact shared-lock command
above. The [complete output](MODEL-401/resume/full-suite.log.gz) and
[summary with exit status](MODEL-401/resume/full-suite-summary.txt) are retained.
No tests or assertions were weakened, and no dependency failure was ignored.
The delivery commit changes evidence only; the final implementation remains
`2cd5f104c362d5c40ba5f10dbba5a7d01fca8df5`.

The executor's shell, flock, pytest controller, and four xdist worker processes
have exited, verified by a scoped process check in
[process-cleanup.txt](MODEL-401/resume/process-cleanup.txt). No executor
background process remains running.

Delivery uses `CI_LOCAL_SKIP=1 git push -u origin model-401-hardware-fit-lower-bound`
after focused checks pass. The user scope exception explicitly authorizes
`gh pr edit 812 --body-file docs/evidence/g2-ios/MODEL-401/resume/pr-body.log`.
The PR remains a draft. Every commit ends with
`Co-Authored-By: ChatGPT Codex <noreply@openai.com>`; the PR body ends with the
required executor and pending cross-model-review attribution.

## Versions and limits of observation

Python 3.14.4; pytest 9.1.1; pytest-xdist 3.8.0; Pydantic 2.13.5;
jsonschema 4.26.0; Node v22.22.3; npm 10.9.8; Vitest 5.0.1;
flock 0.4.0; git 2.50.1; gh 2.102.0.

All hardware inputs are synthetic verified fixtures. No model was loaded,
no physical device or deployed service was exercised, and no paid-provider
or vendor API call was made. No production hardware-fit records were added.
No measured fit, runtime compatibility, latency, or throughput was established.
The hardware-fit Markdown pages are repository documents rather than generated
site pages; no local full site build was needed by that conditional requirement.
The social-card and landing tests ran their existing site-generation paths
after web setup, and the web client was built for the landing browser fixture.
No production switch, ranking, legal text, frozen data, Linear state,
or merge was changed. No wsl gate, SSH, or SCP was run. Cross-model review is
pending.
