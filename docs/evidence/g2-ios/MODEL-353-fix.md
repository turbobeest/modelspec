# MODEL-353 execution evidence

This ticket adds a signed decision link and a read-only human summary page.
`DECISION_LINK_ENABLED` remains false in production and staging configuration.
Jamie has not approved visibility or storage. The recommendations and activation
requirements are in [the draft design](../../design/decision-link.md).

## Revisions and tools

Base SHA: `8825a31c2f215f6737eefbc7fa2ab2927161b7b5`.
Implementation SHA: `d66761aff532134a370096081b43838137057af0`.
Final delivery SHA is the tip of `sparksandsawdust/model-353-decision-link`.
Resolve it with `git rev-parse HEAD` on the PR branch. The evidence commit
cannot contain its own SHA; the executor's final output records that SHA.

The commands ran in `/Users/terbeest/dev/worktrees/model-353` with Python
3.14.4, pytest 9.1.1, Node 22.22.3, npm 10.9.8, Vitest 5.0.1,
Playwright 1.63.0, Chromium 153.0.8010.12, Git 2.50.1, and gh 2.102.0.
Node commands used `/Users/terbeest/.nvm/versions/node/v22.22.3/bin`.

## Red tests and fixes

The first command ran new tests before changing implementation:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_link.py
```

It exited 1 with `11 failed, 27 passed in 1.54s`. The compatibility tests
already passed on the base. The new link, reporting rule, and replay tests
failed as follows.

| Missing behavior | Red-first test | Red output | Green output |
| --- | --- | --- | --- |
| Link in bounded responses | `test_flag_on_bounded_link_is_signed_unguessable_and_within_budget` | `assert body.get("decision_url")`, got `None` | Passed; independently verifies HMAC, nonce, exact pin, 30-day lifetime and budget, then retrieves the human summary |
| Reporting instruction on trusted channels | `test_flag_on_copy_adds_decision_url_on_trusted_channels` | Required `and give the user decision_url` phrase absent | Passed for MCP instructions, decide description, guide and CLI answer text |
| Summary-only replay | `test_page_returns_only_summary_requirements_and_snapshot` | Expected HTTP 200, got 404 | Passed with exact response field allowlist and summary/caveat equality |
| Expiry boundary | `test_link_expiry_is_enforced` | Before expiry expected 200, got 404; at expiry expected 410, got 404 | Passed immediately before expiry, at expiry, and before issuance |
| Snapshot and engine pin refusal | `test_tampering_or_changed_pins_refuse_replay` | Snapshot/hash/service changes expected 409, got 404 | Passed; altered inputs/signature/citation also refuse without summary content |
| Human admission | `test_machine_cannot_read_a_link_without_human_admission` | Expected HTTP 401, got 404 | Passed with access enforcement both on and off |
| Drill-down link budget | `test_complete_and_drill_down_keep_their_budgets` | Drill-down `decision_url` absent | Passed; complete bytes unchanged and drill-down remains within its existing budget |

The original snapshot-tampering test helper had an argument-name collision.
After correcting the helper, the test was rerun against the base entry point
and failed with `404 == 409`. The exact rerun was:

```sh
mkdir -p .scratch/model-353-exec/base
git show 8825a31c:api/worker/src/entry.py > .scratch/model-353-exec/base/entry.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
import tests.test_x402 as fixture
import pytest
fixture.WORKER_SRC = Path('.scratch/model-353-exec/base').resolve()
raise SystemExit(pytest.main(['-q', 'tests/test_decision_link.py', '-k', 'pins and snapshot']))
PY
```

Two additional tests caught defects during implementation review:

- `test_page_discloses_benchmark_exclusions_and_unapplied_task_type` initially
  failed with `None == ['swe_bench_pro']`, exit 1. Replay now includes the
  applied benchmark exclusion set and labels task type as not applied.
- `test_flag_on_bounded_link_is_signed_unguessable_and_within_budget`, after
  adding strict contract validation, failed with `decision_url: Extra inputs
  are not permitted`, exit 1. The new optional contract field, generated schema
  and OpenAPI definition now agree. Existing versions remain 2.16 and 1.2.

The following existing generated-document check failed before regeneration:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_api_docs.py
```

`test_the_committed_spec_is_what_the_implementation_generates` reported a
missing generated `decision_url` schema field, exit 1. Regenerating OpenAPI
turned this suite green: `42 passed, 2 skipped`, exit 0.

The page and shell tests first ran before the page existed:

```sh
cd web
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test -- src/decision-link/__tests__/page.test.tsx src/decision-link/__tests__/pages-routing.test.ts
```

The red run exited 1 with `2 failed` test files, including the missing page
module and `ENOENT` for `decision.html`. The final web suite passes all current
decision-link tests. These cover human admission before content fetch, expired
and invalid links, unavailable visit verification, summary-only rendering,
escaped text, and shell privacy metadata.

`test_decision_link_shell_is_private_and_not_discoverable` failed before the
live build copied the shell, exit 1. The broad site suite subsequently passed
41 tests, exit 0. An extra HTTP robots header was explored, then removed
because the existing deployment gate forbids it. The HTML retains early
`noindex, nofollow, noarchive` metadata. Existing deployment guards remain
unchanged.

The existing site-fixture diagnostic command was:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decide_preview_workflow.py tests/test_private_serving.py
```

It exited 1 with `2 failed, 19 passed`. Both
`test_live_assembly_matches_internal_and_preserves_holding_byte_for_byte` and
`test_private_model_is_absent_from_every_public_file` raised
`FileNotFoundError` for `decision.html`. The synthetic web artifacts now include
the new page, and every existing assertion remains intact. This green command
exited 0 with `9 passed`:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decide_preview_workflow.py tests/test_private_serving.py::test_private_model_is_absent_from_every_public_file
```

## Compatibility and privacy checks

`test_flag_off_response_bytes_match_base` pins literal SHA-256 values measured
from the unchanged fixture responses at the base. It verifies complete,
bounded and drill-down response bytes for absent, false, zero, off, no and
empty flag values. `test_flag_off_agent_copy_bytes_match_base` pins the original
MCP copy, guide and CLI answer text. All pass.

Generated CLI bundle metadata changes only three source hashes for the edited
generator, Wrangler configuration and contract schema. Its user-facing text
and guide version remain unchanged. MCP copy and `docs/agents.md` are unchanged.
The recorded MCP tool fixture updates two hashes for the contract schema and
OpenAPI. Its tool descriptions and input schemas are unchanged.

The stale capture test failed with a source-hash mismatch, exit 1. The following
offline commands, with the pinned Node path and `PYTHONPATH=$PWD`, regenerated
the fixture and passed `140 passed`, exit 0:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_gaps.py tests/test_agent_guide.py tests/test_agent_harness.py
```

`test_staging_x402_config_is_isolated_on_base_sepolia` initially failed because
its exact configuration fixture omitted the newly added false flag, exit 1.
The fixture now explicitly expects `DECISION_LINK_ENABLED: false`. A new check
also requires it false in both production and staging. The command below
passed `111 passed`, exit 0:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_x402.py tests/test_decision_link.py
```

The existing script-disclosure test initially treated the verification script
under `web/scripts` as shipped code and refused its localhost URL, exit 1.
Moving it to `qa/decision-link-smoke.mjs` made this unchanged test pass, exit 0:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_legal.py::test_pages_load_no_third_party_script_but_the_disclosed_beacon
```

Further tests verify that estate, profile and saved-spec inputs receive no
link; incomplete configuration receives no link; an optional link is omitted
when it cannot fit; and turning off visit gating does not open a machine read
path. Human view requests use fresh admission, without decision-intent reuse.
The signed capsule is readable, not encrypted. The design note records this
privacy limitation and the lack of snapshot or engine retention.

`git diff 8825a31c -- docs/api.md docs/legal` is empty. No frozen data,
ranking floors, legal terms or existing production switches changed.

## Commands and final checks

These commands regenerated the required artifacts:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m decision.schema
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
```

All exited 0. The copy generator emitted existing unregistered hardware-source
warnings while reading the frozen data; it made no provider calls.

Focused Python checks:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_link.py tests/test_decide_worker.py tests/test_decide_bounded.py tests/test_decide_agent_budget.py tests/test_agent_copy.py tests/test_visit_gate.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_link.py tests/test_decision_contract.py tests/test_agent_copy.py tests/test_visit_gate.py
```

The first passed `252 passed, 1 skipped`, exit 0. The second passed
`366 passed`, exit 0, after the final contract and replay fixes.

Including the OpenAPI suite in that second command passed `408 passed,
2 skipped`, exit 0. The broad site command was:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_holding.py
```

It passed `41 passed`, exit 0. The required full suite below rechecks the final
site composition after removing the extra HTTP header.

The required full command was:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
```

It exited 0 on implementation `d66761af` with `9766 passed, 8 skipped,
11 warnings in 1515.44s`. The warnings came from the existing unsigned
vocabulary fixtures in CLI snapshot and keyed-origin tests.

Two earlier full runs were deliberately interrupted while integration edits
were still underway, exit 2, after 738 and 664 passes. Another run exposed the
generated OpenAPI and synthetic site-fixture integration failures, stale MCP
capture hashes, a configuration expectation missing the new off flag, and
the verifier being in the directory scanned as shipped scripts. It exited 1
with `20 failed, 9746 passed, 8 skipped`. These preliminary runs are not
presented as a completed gate.

The frontend checks ran from `web` with the pinned Node path:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npx tsc -b
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npx eslint src/decision-link vite.config.ts
```

All exited 0. Full web tests reported `809 passed`, with one skipped test file.
The production build ran from `web`:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH VITE_VISIT_GATE_ENABLED=true VITE_TURNSTILE_SITE_KEY=public-test-key npm run build
```

The committed browser script ran from the repository:

```sh
MODELSPEC_TEST_PYTHON=/Users/terbeest/dev/modelspec/.venv/bin/python /Users/terbeest/.nvm/versions/node/v22.22.3/bin/node qa/decision-link-smoke.mjs
```

Both exited 0. The browser script reported `PASS`, Chromium 153.0.8010.12,
requests to human status, visit-token exchange and decision-link view, no
referrers, no CSP errors, no result table, and no overflow at 390 pixels.
It runs the compiled page with generated CSP, stubs the external verification
and API responses, and closes its browser and preview server in `finally`.
Desktop and mobile screenshots were visually inspected.

`git diff --check` exited 0. Test exits were checked directly, without pipes.
The shard-balance command also exited 0:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 4 --summary
```

It predicted 60 files per shard and 3320.908 through 3320.911 seconds per shard.

## What was not observed

There was no Cloudflare deployment, production flag change, actual Turnstile
verification, real paid-key view, paid-provider request, or 30-day production
retention observation. The browser smoke stubs its remote boundaries and does
not prove a live Cloudflare Pages rewrite. A reviewer's local Wrangler routing
probe could not start with the installed compatibility-date support; its
process group was terminated. No ticket writes, uploads, SSH, WSL gate,
tmux operations or merge occurred. All started background processes were
reaped before delivery. Cross-model review remains pending.
