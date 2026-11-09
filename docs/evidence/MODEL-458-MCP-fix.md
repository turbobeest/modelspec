MODEL-458-MCP execution evidence

Status: blocked on authorization for two generated-artifact dependencies.
The executor's file list omits `api/worker/openapi.py` and
`mcp/test/__snapshots__/server.test.ts.snap`. Both remain unchanged. The first
must describe the new authentication operation before regenerating the allowed
`api/worker/openapi.yaml`. The second needs six `additionalProperties: false`
declarations. Proposed changes are prepared in ticket scratch.

Base: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`. The remote main reference
matched this base before work began. Worktree and branch remained
`model-458-mcp` throughout.

Final implementation SHA: `60832f25a7b762debb40ef4a1b6ed5508991d6cc`.
The following evidence-only commit is the execution's final HEAD, recorded in
the PR and final execution result. It can be identified with
`git log -1 --format=%H -- docs/evidence/MODEL-458-MCP-fix.md`.

| Finding | Enforced behavior | Commit |
| --- | --- | --- |
| AUD-04-F2 | Static MCP reads require current live-data authorization. Verification returns authentication status only and does not meter reads or use the credit ledger. | `68a361f8f4e759cf070aafe0c183228eacd71e2f` |
| AUD-04-F1 | All six nested ranking and policy blocks validate their fields. Valid inputs and existing outer-object behavior are preserved. | `5c98caf9363d9c428bd6c5cf0cb15326d079923f` |
| AUD-04-F5 | Model-card identifiers satisfy catalogue syntax before origin I/O. | `e180950628a22fd64d805ea74e72471c5f68b8f2` |
| AUD-04-F3 | Local vocabulary lookup retains optional subscription availability and resolves plan-facet descriptors. | `5208dff6618a65dfb5cc1d169691300ae98593a7` |
| AUD-04-F4 | Bounded decision notices retain estate and recovery fields when they fit and count whole records or sections removed for the byte budget. | `60832f25a7b762debb40ef4a1b6ed5508991d6cc` |

Each supplied local reproduction was run before its finding's implementation,
returned exit 1, and returned exit 0 after implementation. Detailed local
observations are confined to `/tmp/MODEL-458-MCP-scratch/`. The vocabulary
reproduction adds a mocked successful authentication operation to accommodate
the preceding F2 change. Its permanent fixture uses the current contract's
`existing_subscribers_only` value.

| Permanent regression category and test names | Red output | Green output |
| --- | --- | --- |
| F2: `static data authorization` cases in `access-discovery.test.ts`; `live_data_authentication` and `auth_check` cases in the Worker tests | MCP: `56 failed, 30 passed`, exit 1. Worker: `32 failed, 102 deselected`, exit 1. | The MCP package passed all 291 tests at the F2 commit; Worker access suites passed all 134 tests. Both exited 0. |
| F1: `preserves or refuses every nested` | `6 failed, 105 skipped`, exit 1. | `10 passed, 105 skipped`, exit 0, including four valid-input and outer-object checks. |
| F5: `non-catalogue ids` and `configured model directory` | `34 failed, 14 passed, 115 skipped`, exit 1. | `48 passed, 115 skipped`, exit 0. |
| F3: `subscription vocabulary` | Vocabulary suite: `7 failed, 23 passed`, exit 1. | Vocabulary suite: `30 passed`, exit 0. Covers exact and cross-section lookup, compact/default/full projection, optional omission, Python parity, and real MCP fallback calls. |
| F4: recovery-field retention and whole-record/section omission tests | `5 failed, 4 passed, 160 skipped`, exit 1. | `9 passed, 160 skipped`, exit 0. Fixtures are validated through the current Python `Decision` schema. |

The F3 expected search result was corrected to include the second plan matched
by the existing partial-token search behavior. The Python parity check confirms
that result; the availability assertion remains exact. No pre-existing
assertion was removed or weakened.

Tool versions: Node `v22.22.3`, npm `10.9.8`, TypeScript `7.0.2`, Vitest
`5.0.1`, Python `3.14.4`, pytest `9.1.1`, Git `2.50.1`, GitHub CLI `2.103.3`.
Node setup and checks used `/Users/terbeest/.nvm/versions/node/v22.22.3/bin`
and the machine-wide heavy-command wrapper. Commands below ran from the
worktree root. Output was captured in ticket scratch and exit codes checked
directly.

```bash
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex-g2/heavy.sh npm ci --prefix mcp

PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex-g2/heavy.sh npm test --prefix mcp -- test/access-discovery.test.ts

env PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_api_access.py tests/test_access_wiring.py -k 'live_data_authentication or auth_check'

env PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_api_access.py tests/test_access_wiring.py

PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex-g2/heavy.sh npm test --prefix mcp -- test/server.test.ts -t 'preserves or refuses every nested'

PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex-g2/heavy.sh npm test --prefix mcp -- test/server.test.ts -t 'preserves or refuses every nested|existing outer-object behavior'

PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex-g2/heavy.sh npm test --prefix mcp -- test/server.test.ts -t 'non-catalogue ids|configured model directory'

PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex-g2/heavy.sh npm test --prefix mcp -- test/vocabulary.test.ts

PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex-g2/heavy.sh npm test --prefix mcp -- test/server.test.ts -t recovery

PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex-g2/heavy.sh npm run typecheck --prefix mcp

PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/.codex-g2/heavy.sh npm test --prefix mcp

env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH="$PWD" DATA_SPLIT_ENABLED=false /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_api_access.py tests/test_access_wiring.py tests/test_api_docs.py tests/test_worker_vendor_imports.py tests/test_worker_memory_compaction.py tests/test_friends_access.py tests/test_x402.py::test_entry_unfunded_catalog_reads_keep_free_limits tests/test_x402.py::test_entry_catalog_finishes_prepaid_block_before_free_fallback tests/test_pricing_v2.py::test_a_paid_vocabulary_read_charges_one_credit_per_block tests/test_pricing_v2.py::test_a_refused_vocabulary_read_is_not_charged

env PYTHONPATH="$PWD" DATA_SPLIT_ENABLED=false /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check

git diff --check
```

Final typecheck: exit 0. Final MCP package: `362 passed, 1 failed`, exit 1.
The sole failure is the discovery schema snapshot, whose six new declarations
require the unlisted snapshot file. Final focused Worker checks:
`244 passed, 2 skipped, 1 failed`, exit 1. The sole failure is
`test_the_spec_describes_exactly_the_endpoints_the_worker_routes`, pending the
unlisted generator change. `openapi.py --check` exits 0 because the existing
YAML matches the unchanged generator; it does not substitute for the route
enumeration test. The proposed generator was rendered successfully in scratch.

The existing memory-compaction and vendor-import checks pass. The change adds
no Worker imports, snapshot/export fields, or ranking rows, so it does not
trigger the private-data memory probe or bundle regeneration. No local full
Python suite, live Worker probe, production deployment, or paid-provider call
was run. Production behavior and CI results were not observed. Production
switches, prices, plans, legal text, ranking floors, release tags and frozen
data were not changed. The aggregate MCP text cap remains 16,384 UTF-8 bytes.

A separate agent reviewed the completed code diff and reported no additional
actionable defects. That source review did not execute tests and does not
replace the pending independent review.
