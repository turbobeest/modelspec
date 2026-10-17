# MODEL-401 hardware-fit lower-bound evidence

Base SHA: `a551fe82eef93fcb1d4389a435b2f62927d0a25e`.
The first commit, `03006c6684c79343b1139c72e1b26880a8b304ea`, changes only
the design note. Final implementation SHA:
`05ea0f41216e86fa89e79d0e892b94cecab798ab`.
The delivery SHA is the evidence commit containing this file. Resolve it with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-401-fix.md`.

Worktree: `/Users/terbeest/dev/worktrees/model-401`.
Branch: `model-401-hardware-fit-lower-bound`.
Draft PR: [#812](https://github.com/turbobeest/modelspec/pull/812).
Delivery status: **BLOCKED** by publication checks outside the named scope
and the OpenAPI byte budget.

## Observed behavior

A signed fixture with 65,500,000,000 weight bytes, 100,000 KV bytes per token,
batch 2, context 1,024, and 32,000,000,000 capacity bytes now returns
hardware-fit 2.0, `status: estimated`, `basis: lower_bound`, and
`estimated_fit: unlikely`. Its per-device lower bound is 65,704,800,000 bytes
and its margin is -33,704,800,000 bytes. Missing headroom is an explicit
`not_required` object with a reason. The response retains the numeric input
record IDs, source IDs, resolved citations, capacity provenance, and winning
verification.

Under-capacity and equality cases without headroom return `undetermined`,
naming missing runtime headroom. Full estimates retain their previous
arithmetic and add `basis: full`. Measurements, keyed-only access, Decision
2.18, bounded 1.5, ranking, and frozen data remain unchanged.

The tests below were added or extended before implementation. The initial
Python run against unchanged code returned **7 failed, 12 passed**. The
Worker red run returned **4 failed**. The MCP red run returned **3 failed,
34 passed**.

The complete red outputs are preserved for [Python](MODEL-401/executor/python-red.log.gz),
[Worker](MODEL-401/executor/worker-red.log.gz),
[MCP](MODEL-401/mcp/red.log.gz), [maximum topology](MODEL-401/executor/topology-red.log.gz),
and [OpenAPI discriminators](MODEL-401/executor/schema-red.log.gz).

| Defect or invariant | Test | Red observation | Green observation |
| --- | --- | --- | --- |
| Over-capacity weights without headroom | `test_qwen_like_weights_exceed_capacity_without_runtime_headroom` | `undetermined` instead of `estimated` | Exact lower-bound response, negative margin, signed snapshot round trip |
| Missing headroom under capacity or at equality | `test_lower_bound_at_or_below_capacity_needs_sourced_headroom` | Record rejected, with generic missing-record inputs | Both cases name only missing headroom and give a reason |
| Full estimate contract | `test_estimated_workload_reports_literal_formula_inputs_and_never_asserts_fit` | Version `1.0` instead of `2.0` | Version 2.0, basis full, previous literal arithmetic |
| Mixed per-device headroom | `test_mixed_headroom_topology_uses_each_device_lower_bound` | `undetermined` instead of lower-bound estimate | Each device uses its own bound, without pooling |
| Excluded or unregistered source | `test_untrusted_parameters_cannot_become_estimates` | All 12 full and lower-bound trust cases passed as baseline guards | All remain `undetermined` |
| Worker version and lower-bound forwarding | `test_keyed_worker_returns_the_lower_bound_assessment_unchanged`, `test_hardware_fit_transport_refusals_keep_its_own_contract` | Old status and version | Fetched and bundled signed snapshots preserve the checker response |
| MCP/API parity and agent description | `matches the generated Python API $basis assessment`, `lists an optional strict workload schema and distinguishes estimates from measured fit` | Old API version, missing basis guidance, lower bound abstained | Both complete real API bodies survive MCP forwarding unchanged |
| Lower-bound schema | `test_lower_bound_response_schema_forbids_likely_and_fabricated_headroom` | No estimated result initially. A later red exposed an inline discriminator target instead of a reference | Published schema accepts the result and rejects `likely` and numeric zero headroom |
| Maximum topology | `test_maximum_topology_without_headroom_returns_a_valid_undetermined_response` | Missing-input reason exceeded its 512-character contract limit | Valid bounded reason for 1,024 devices |

Additional passing regressions prove that adding or removing headroom without
resigning the record fails admission, and that absent headroom and sourced
zero remain distinct conflicting inputs. The no-`fits` tests from MODEL-287
remain in the focused suites.

## Commands and results

All Python commands ran from the worktree root. Node commands use the pinned
Node directory. Commands return their own exit status directly. Raw logs are
compressed beside this file. Read them with Python's `gzip` module or `gzcat`.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_hardware_fit.py -k 'qwen_like or lower_bound or mixed_headroom or untrusted_parameters or estimated_workload'
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_hardware_fit_worker.py -k 'lower_bound or transport_refusals'
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_hardware_fit.py -k maximum_topology
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_hardware_fit.py -k response_schema
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_hardware_fit.py tests/test_hardware_fit_worker.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_hardware_fit.py tests/test_hardware_fit_worker.py tests/test_decision_snapshot.py tests/test_agent_copy.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_api_docs.py tests/test_agent_overhead.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-401/executor/contract-probe.py
/opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
git diff --check
```

The OpenAPI generator exited 0. Its `--check` exited 0 and printed
`api/worker/openapi.yaml matches the implementation`. The final focused
snapshot, hardware-fit, Worker, and agent-copy run exited 0 with **215 passed**.
The API-doc and agent-overhead run exited 0 with **57 passed, 2 skipped**.
An earlier hardware-fit-only green run passed 97 tests before the additional
verification and maximum-topology regressions were added.

The required full suite completed under the shared lock with exit **1**:
**18 failed, 11,452 passed, 24 skipped, 11 warnings in 1,178.23 seconds**.
The [complete log](MODEL-401/executor/full-suite.log.gz) and
[failure summary](MODEL-401/executor/full-suite-summary.txt) retain every
failure. Fourteen failures concern the stale MCP capture, one concerns the
reviewed agent-copy hash, and one concerns the OpenAPI byte budget. Two local
social-card tests also fail because `web/` has no installed `@playwright/test`
package. That dependency failure is an environment observation, not a proven
code regression. No baseline full-suite run was performed.

An initial broader-test command included nonexistent `tests/test_openapi.py`.
It exited 4 and ran no tests. The published API tests are in
`tests/test_api_docs.py`, which the successful run above covers.
The first 97-test green attempt also exposed normalization of the fixture's
winning verification, which adds `diff: null`. The test now expects that
retained value and still checks the complete verification.

The repository's discriminator-aware validator also accepted both actual
full and lower-bound responses. The exact probe is recorded in
`MODEL-401/executor/contract-probe.py`, with output in
`MODEL-401/executor/contract-probe.log.gz`.

MCP commands, including dependency installation, red output, copy generation,
type checking, and the complete suite, are in
[MCP verification commands](MODEL-401/mcp/commands.md). All final MCP commands
exited 0. The suite passed **203 tests across 10 files**. The updated tool
description uses 163 planning tokens against its existing 1,500-token limit.
The copy generator refreshed the CLI bundle's source hash.

The initial PR CI run exposed a test environment dependency. The new MCP
parity test launched Python with application dependencies, but the Node job
does not install Pydantic. Its two parity cases failed with
`ModuleNotFoundError: No module named 'pydantic'`. The original local run
used the shared application environment and passed. The [CI red log](MODEL-401/executor/mcp-ci-red.log.gz)
records that failure, retrieved with
`gh run view 39073296368 --log-failed`.

The correction commits complete API responses as a generated test fixture.
A Python equality test checks both fixture bodies against the current
checker. MCP imports those fixtures and compares the complete forwarded
bodies, preserving the literal assertions. The final MCP run passes all
203 tests with no `PYTHON` override and Python 3.14 restricted to its standard
library. The fixture generator, reproduction commands, and final logs are
recorded in the MCP verification commands above. No workflow change or
skipped assertion was needed.

After the correction, `gh pr checks 812 --json name,state` reported
`MCP Worker tests: SUCCESS`, alongside successful data-freeze, sign-off, and
release-chart evidence checks. Other CI jobs were still running at that check.

Delivery commands use the executor brief's pre-push-hook override after the
focused suites pass:

```sh
CI_LOCAL_SKIP=1 git push -u origin model-401-hardware-fit-lower-bound
gh pr create --base main --head model-401-hardware-fit-lower-bound --draft --title 'MODEL-401: report hardware-fit lower bounds without runtime headroom' --body-file docs/evidence/g2-ios/MODEL-401/executor/pr-body.log
```

Both commands exited 0. The PR body ends with the required executor and
pending cross-model-review attribution. Every commit ends with
`Co-Authored-By: ChatGPT Codex <noreply@openai.com>`.

## Tool versions

| Tool | Version |
| --- | --- |
| Python | 3.14.4 |
| pytest | 9.1.1 |
| pytest-xdist | 3.8.0 |
| Pydantic | 2.13.5 |
| jsonschema | 4.26.0 |
| Node | v22.22.3 |
| npm | 10.9.8 |
| Vitest | 5.0.1 |
| flock | 0.4.0 |
| git | 2.50.1 |
| gh | 2.102.0 |

## Blocking publication checks

Delivery is **BLOCKED** by the broad publication checks. The downloaded CI
JUnit artifact reports five failures saying
`MCP definitions drifted; run python -m qa.contracts and review the capture`.
It also reports the OpenAPI size failure, 235,348 bytes against the existing
233,000-byte cap. The base OpenAPI was 232,015 bytes, proving that this change
introduces the size regression. The capture errors coincide with the changed
MCP description. No clean baseline QA run was observed, and these failures
are not classified as baseline failures. [The CI findings](MODEL-401/review/findings.md) record the exact
test names, commands, and archived failure evidence.

The executor brief says, "Stay inside the paths the spec names. If you need
a file outside them, stop and report it." The required QA capture is outside
the spec's named paths. Implementation changes stopped at that boundary.
No QA capture, QA implementation, budget test, or existing assertion was
changed. The full suite also reports the reviewed copy hash mismatch in
`tests/test_decision_link.py::test_flag_off_agent_copy_matches_reviewed_catalogue`.
Completing this ticket requires scope for the QA capture and reviewed-copy
pin, a generated schema that meets the existing OpenAPI byte budget, and the
web test dependencies for a clean local full-suite result.

## Limits of observation

All hardware inputs are synthetic verified test fixtures. No model was loaded
and no physical device, live deployment, paid provider, or vendor API was
called. This work adds no production hardware-fit records and establishes no
measured fit, runtime compatibility, throughput, or latency.

The hardware-fit Markdown pages are repository documents, not generated site
pages. `pipeline/build.py` points API documentation at GitHub and does not
render these files. Both-site builds were therefore outside the spec's
conditional build requirement. The OpenAPI document was regenerated and
checked directly. No wsl gate, SSH, SCP, Linear write, merge, production
switch, or ranking change was performed. Cross-model review remains pending.
