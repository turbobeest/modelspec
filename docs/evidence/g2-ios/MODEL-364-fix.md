# MODEL-364 execution evidence

Status: BLOCKED by the executor's file scope. No claim that the full suite passes.

Base SHA: `8825a31c2f215f6737eefbc7fa2ab2927161b7b5`.
Implementation checkpoint SHA: `5fb59ceaf4a74d5422d76c80506c02dd6948b875`.
The final delivery SHA is the commit containing this report. Resolve it with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-364-fix.md`.
The final executor message also records that SHA. This avoids embedding a
commit's own hash in its contents.

## Implemented behavior

Option B adds keyed `POST /v1/compare-models`, the CLI form
`modelspec compare A B [C D]`, and MCP `compare_models`. The endpoint returns
two to four requested models in caller order, with facts, offering prices,
benchmark evidence, provenance, explicit unknowns, and omission counts.
It reads the verified snapshot without running an objective or ranking models.
The decision contract is 3.0. The bounded representation remains 1.2.
The CLI package version remains 0.4.0. The design and release requirements are
in `docs/design/compare-models.md`.

The endpoint requires a key even with `ACCESS_ENFORCED` off. Visit tokens do
not admit it. Existing access quotas and billing apply. Successful HTTP bodies
fit 14,000 compact UTF-8 bytes, and MCP responses fit 16,384 bytes.
The existing snapshot comparison remains available and its tests pass.

## Scope blocker

The executor brief says: "Stay inside the paths the spec names. If you need a
file outside them, stop and report it."

The existing `tests/test_agent_copy.py` requires every MCP tool description to
come from `pipeline/agent_copy.py` and the published tool list to match
`pipeline/agent_ready.py`. The new tool needs entries in those files. They are
outside the paths named in the spec, so neither file was changed. Scope
expansion was requested and had not been authorized when this report was
written. The current local tool description is temporary and fails that
existing check. No test was relaxed to accept it.

The CLI bundle and its request schema were regenerated through the existing
generator functions without changing generator source or other output paths.
This corrects the bundle's decision-schema source hash and allows wheel tests
to pass. Centralizing the new CLI help and MCP description still needs the
generator changes.

## Red-first observations

All initial feature tests ran before their corresponding implementation.
HTTP tests use mocked transports or synthetic signed snapshots.

| Defect or missing behavior | Red-first tests | Red output | Green output |
|---|---|---|---|
| Named Worker comparisons absent | `test_named_comparison_preserves_order_facts_prices_and_verified_evidence`, `test_named_comparison_refuses_invalid_or_unknown_ids`, `test_named_comparison_checks_snapshot_header`, `test_named_comparison_never_admits_a_keyless_machine_or_visit_token`, `test_named_comparison_routes_a_keyed_request_through_signed_snapshot`, `test_named_comparison_keeps_mixed_classes_and_trims_whole_records` | Exit 1, 14 failed. Service calls raised `AttributeError: ... has no attribute 'compare_models'`; route assertions saw 404. | Exit 0, 15 Worker tests passed after the qualifier regression below. |
| Named CLI form absent | `test_keyless_named_compare_refuses_exactly_like_decide_before_validation`, `test_named_compare_posts_only_requested_models_and_preserves_json_bytes`, count, flag, rendering, recovery, and help tests in `tests/test_cli_compare_models.py` | Exit 1, 31 failed, 3 passed. Named arguments were refused before the expected keyed command behavior. | Exit 0, final named and snapshot CLI suites: 77 passed. |
| Missing records falsely displayed as unknown | `test_missing_values_are_not_shown_instead_of_reported_unknown_when_response_is_bounded` | Exit 1, 1 failed. Missing cells displayed `unknown`. | Missing cells display `not shown`, while explicit unknown facts retain `unknown`; included in the 77 passing CLI tests. |
| Evidence task and interval metadata lost | `test_named_comparison_preserves_subcategories_intervals_and_unknown_units` | Exit 1, 1 failed. Actual metadata was `(None, None, None, None)` instead of `('python', [55.0, 65.0], 50, None)`. Review also reproduced response validation errors for nullable evidence units. | Worker retains `subcategory`, `interval`, `n`, and nullable `unit`; 15 Worker tests pass. |
| CLI evidence variants indistinguishable | `test_human_named_comparison_preserves_evidence_subcategory_interval_and_sample_count` | Exit 1, 1 failed before the rendering change. | Python and Rust benchmark rows remain distinct, with intervals and sample counts; included in 77 passing CLI tests. |
| MCP tool absent | New `mcp/test/compare-models.test.ts` cases for tool discovery, forwarding, keyless refusal, validation, and response budget | Exit 1, all initial 28 new tests failed because the tool was absent. | Final MCP suite: exit 0, 164 passed across 8 files. |
| MCP validation errors exceeded the budget | `bounds validation errors for oversized invalid input` cases | Exit 1, 2 failed. Validation messages measured 28,087 and 191,039 UTF-8 bytes. | The strict input schema emits a compact constant validation message; final MCP suite passes. |
| Named endpoint missing from OpenAPI | `test_named_model_comparison_documents_bounded_keyed_facts` | Exit 1, `KeyError: '/v1/compare-models'`. A later red check also found missing 409 snapshot-pin documentation. | Named request, keyed security, snapshot pin, 409, and response budget checks pass. |
| Named native credit refusal missing from OpenAPI | `test_openapi_keeps_machine_credit_refusals_without_advertising_a_disabled_rail` | Named cases initially produced 2 failures, 6 passes. | All 8 rail and human-gate combinations pass. |

## Commands and results

Python commands ran from `/Users/terbeest/dev/worktrees/model-364` with
`PYTHONPATH=$PWD`. Node commands used
`PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH`.
Redirections preserve the command's exit status. Every status below came from
the command or its resumed execution session, not a pipeline.

Tool versions: Python 3.14.4, pytest 9.1.1, Ruff 0.16.6, Node v22.22.3,
npm 10.9.8, Vitest 5.0.1, Git 2.50.1, and gh 2.102.0.

The following commands use the exact interpreter path:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_compare_models_worker.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_compare_models_worker.py::test_named_comparison_preserves_subcategories_intervals_and_unknown_units
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cli_compare_models.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cli_compare_models.py::test_missing_values_are_not_shown_instead_of_reported_unknown_when_response_is_bounded
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cli_compare_models.py::test_human_named_comparison_preserves_evidence_subcategory_interval_and_sample_count
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cli_compare_models.py tests/test_cli_compare.py
```

The red and green statuses for these commands appear in the observation table.
The CLI's broader client command passed with exit 0, 257 tests, before the last
evidence-rendering regression was added:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cli_compare_models.py tests/test_cli_compare.py tests/test_cli_concierge.py tests/test_cli_keyed_origin.py
```

Final scoped Python check, exit 0, 436 passed and 2 skipped:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_compare_models_worker.py tests/test_cli_compare_models.py tests/test_cli_compare.py tests/test_decision_contract.py tests/test_api_docs.py tests/test_decision_cli.py tests/test_decision_cli_output.py tests/test_cli_wheel.py
```

Adding `tests/test_agent_copy.py` to that exact command returned exit 1,
451 passed, 2 skipped, and one failure:
`test_every_mcp_tool_description_and_the_instructions_come_from_the_copy`.
Its generated tool list lacks `compare_models`, and the description is local.

The required full-suite command was attempted:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
```

It was deliberately interrupted after the known scope blocker was established,
and returned exit 2 with 675 passed and two old version assertions failing.
Those assertions in `tests/test_architecture_facts.py` expected 2.16; the
implementation correctly returned 3.0. Other current-version assertions were
updated to 3.0 without changing their behavioral expectations. The current
bounded budget fixture also needed its `projects_contract` labels changed to
3.0. Historical response mocks were left intact. The focused migration command was:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_architecture_facts.py tests/test_decide_bounded.py tests/test_decision_cost_per_task.py tests/test_decision_estate.py tests/test_decision_relax.py tests/test_decision_plans.py tests/test_decision_compact_explain.py
```

The migration command returned exit 1, 197 passed and one fixture failure.
`test_committed_public_fixture_follows_the_bounded_contract` refused the
fixture's old 2.16 labels against the current 3.0 response schema. After
updating only those labels in `mcp/test/fixtures/decide-budget.json`, the exact
focused command below returned exit 0, one passed:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decide_bounded.py::test_committed_public_fixture_follows_the_bounded_contract
```

MCP commands:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci --prefix mcp
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test --prefix mcp -- test/compare-models.test.ts
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test --prefix mcp -- test/compare-models.test.ts -t 'bounds validation errors'
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test --prefix mcp -- test/server.test.ts -t 'tools/list returns all eight tools' --update
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test --prefix mcp
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm run typecheck --prefix mcp
```

Installation, the final MCP suite, and typecheck each returned exit 0. Snapshot
updates reflect the added public tool. No comparison assertion was weakened.

Artifact generation and consistency checks:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m decision.schema
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pipeline import agent_copy
agent_copy.CLI_OUT.write_text(agent_copy.render(agent_copy.cli_bundle()), encoding='utf-8')
agent_copy.CLI_SCHEMA.write_text(agent_copy.render(agent_copy.cli_spec_schema()), encoding='utf-8')
PY
git diff --check
git diff 8825a31c -- api/ranking/engine.py docs/legal/
```

Each returned exit 0. The last command produced no diff. Ranking floors and
published legal text did not change. The API documentation word-count test
passes within the 800-word limit. The main implementation was saved with:

```sh
git add -u
git add docs/design/compare-models.md mcp/test/compare-models.test.ts tests/test_cli_compare_models.py tests/test_compare_models_worker.py
git commit -m 'wip: MODEL-364 compare named models with keyed snapshot facts' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
```

Additional diagnostic commands included a Ruff check across the Worker,
contract, and new Worker test file. It returned exit 1 with 65 findings,
including existing import order and line-length issues and the new test's
reused pytest fixture imports. It is not claimed as a passing check. The CLI
worker's narrower Ruff check returned exit 0. Formatting used:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check api/worker/src/decide_service.py api/worker/src/entry.py decision/contract.py tests/test_compare_models_worker.py
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff format --range 582-685 api/worker/src/decide_service.py
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff format --range 2192-2263 decision/contract.py
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff format tests/test_compare_models_worker.py
```

Raw red and green logs remain in `.scratch/MODEL-364/` in this worktree.

Delivery uses a second commit for the fixture labels, bundle hash, current
version assertions, and this evidence report. Its commit message ends with
`Co-Authored-By: ChatGPT Codex <noreply@openai.com>`. The delivery commands are:

```sh
CI_LOCAL_SKIP=1 git push -u origin sparksandsawdust/model-364-compare-models
gh pr create --draft --base main --title 'MODEL-364: compare named models side by side' --body-file .scratch/MODEL-364/root/pr-body.md
```

The final message reports whether those delivery commands succeeded. The PR
stays draft and explicitly records the scope blocker.

## Limits of observation

No production deployment, deployed endpoint comparison, PyPI release,
provider API spend, device operation, or production switch change was made.
The wsl gate was not run. No Linear write, SSH, SCP, curl, wget, or merge was
performed. The whole Python suite did not complete and is not claimed green.
Independent review in this session found the omission and evidence metadata
issues above. The requested cross-model review remains pending.
