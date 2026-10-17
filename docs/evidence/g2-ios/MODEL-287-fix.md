# MODEL-287 execution evidence

Base: `2b2e9a38f19012658f2b390cbb3f00eb8a00ae75`.
Verified implementation SHA: `c13b81c9b6ee55c48b7efe4985e30291f39dc6d5`.
The delivery adds this evidence and its logs after that implementation commit.
Final checks: full pytest 11,343 passed / 9 skipped; MCP 201 passed;
TypeScript, OpenAPI regeneration and data freeze all exited 0.
Draft PR: https://github.com/turbobeest/modelspec/pull/806.

## Design recorded before implementation

`POST /v1/hardware-fit` and MCP `hardware_fit` accept a strict object with
`model`, `sku`, `device_count`, `memory`, `runtime`, `quantisation`, `batch`,
and `context`. Memory is optional, in decimal GB per device. Other omitted
inputs produce an `undetermined` answer. Invalid types and unknown fields
produce HTTP 400. Unknown identifiers remain valid questions.

The new response has `hardware_fit_version: "1.0"`, `endpoint`, `snapshot`,
`request`, `sources`, and a closed `status` discriminant:

- `measured` carries `measured_fit` and an exact cited measurement.
- `estimated` carries `estimated_fit: likely|unlikely`, `margin_bytes`, the
  formula, every numeric input with its provenance, and explicit assumptions.
- `undetermined` carries `missing`, with input names and reasons.

No estimate contains `fits`. Nothing changes the Decision contract 2.18,
estate reach, ranking floors, or `rank_score`. New response variants belong
to this endpoint's own contract. MODEL-59 applies to that contract separately.

The signed snapshot may retain optional verified hardware-fit records read
from `hardware/fit/records.yaml` in the selected data checkout. Records bind
the exact model, SKU, device count, runtime, quantisation, batch, and context.
Every record and parameter has retained provenance and registered sources.
The latest independent verification controls admission. Quarantined,
unregistered, excluded, or incomplete inputs cannot yield an estimate.
Existing frozen curated data is not changed.

Estimate records provide sourced resident `weights_bytes`, per-token
`kv_bytes_per_token`, and `runtime_headroom_bytes`, each scoped per device
for that exact topology and workload. Capacity comes from the dated hardware
record, or the explicit caller override. A SKU with several memory options
requires the override. Model maximum context is a verified snapshot fact.
The calculation is:

```text
kv_cache_bytes = kv_bytes_per_token * batch * context
required_bytes = weights_bytes + kv_cache_bytes + runtime_headroom_bytes
margin_bytes = capacity_bytes - required_bytes
estimated_fit = likely when margin_bytes >= 0, otherwise unlikely
```

Device memory is never pooled. A measurement must also match the effective
memory capacity. Runtime identifiers include any version/settings needed to
identify the cited run. Missing exact records remain undetermined. Generic
quantisation byte constants, fixed 25 percent allowance, raw card geometry,
and existing `model.fits_hardware` membership are not proof for this route.

Both API and MCP require a key even when their optional access-enforcement
switch is off. Visit tokens do not admit this endpoint. Billing uses the
existing `decide.full` resource from `api/worker/tiers.json`, currently two
credits, following named comparison. Successful assessments, including honest
undetermined answers, use the normal reserve/settle flow. Refusals release it.

## Red-first results

The design was committed as `54ca7192` and placed in draft PR 806 before
implementation. Tests ran against unchanged implementation before the first
code changes. Full outputs are compressed under [MODEL-287](MODEL-287/).
[logs.json](MODEL-287/logs.json) records their uncompressed SHA-256 digests.

| Behavior and test | Red observation | Green observation |
| --- | --- | --- |
| `test_measured_requires_exact_workload_and_cites_retained_measurement` | Missing `SnapshotInputs.hardware_fit_records`; initial core suite had 29 failures. | Exact run returns `measured`, its observed result, and retained citations. Changed batch abstains. |
| `test_estimated_workload_reports_literal_formula_inputs_and_never_asserts_fit` | `ModuleNotFoundError: No module named 'decision.hardware_fit'`. | Required bytes are 5,204,800,000 and margin is 18,795,200,000 in the synthetic worked example. No `fits` or `measured_fit` field. |
| `test_missing_request_input_is_undetermined` and `test_adversarial_questions_abstain` | Part of the 29 failing core cases. | Missing dimensions, unknown SKU/model, unsourced quantisation, and context above the verified maximum abstain. |
| `test_multi_device_estimate_uses_each_allocation_without_pooling` | Part of the initial failing core suite. | The second device's negative 2,204,800,000-byte margin yields `unlikely`, despite spare memory on the first device. |
| `test_hardware_fit_refuses_keyless_requests_even_with_a_valid_visit_token` | HTTP 404 instead of 401. Initial Worker/OpenAPI run had 30 failures. | Every switch combination returns 401 before data or metering. |
| `test_hardware_fit_charges_existing_full_decision_price_and_refunds_refusals` | Route absent, HTTP 404. | Two-credit successful assessments settle. Refusals keep both credits and release all reservations. |
| MCP `hardware_fit` listing and calls | 29 failures. `expected undefined to be defined`; tool was unregistered. | 35 focused tests pass. All response variants and upstream refusals retain their origin body/status. |
| `test_estimate_arithmetic_overflow_abstains_without_nonfinite_numbers` | Nonfinite arithmetic reached an estimate. | Overflow returns `undetermined`. |
| `test_unrelated_inline_verification_cannot_admit_a_workload_record` | An unrelated verification target admitted the record. | Wrong-target inline verification cannot admit it. Correct logged verification can. |
| Missing-headroom and winning-verifier tests | Missing-input explanation and verifier were absent. | Missing headroom is named; measured/estimated responses retain the winning verification. |
| `test_hardware_fit_input_order_does_not_change_the_signed_snapshot` | One failure: reordered workload records changed the snapshot ID. | Canonical row ordering preserves the snapshot ID. |
| `test_sourced_numbers_are_shared_across_independently_verified_workloads` and parent-pruning test | Two failures: `duplicate record ID hardware-input:weights`. | Equal sourced inputs share sorted parent links. Out-of-lineup parents disappear. Conflicting values or sources still fail. |
| `test_unfunded_hardware_fit_answer_validates_against_its_published_contract` | One failure: `estimated.credits`, `Extra inputs are not permitted`. | The actual fallback response validates against typed core and OpenAPI contracts. |
| `test_flag_off_agent_copy_bytes_match_base` (now `test_flag_off_agent_copy_matches_reviewed_catalogue`) | The additive tool/card changed the complete catalogue hash. | The reviewed exact-byte golden covers all nine tools and their compact descriptions. Guide and CLI hashes remain unchanged. All 47 decision-link tests pass. |
| `test_exact_measurement_does_not_depend_on_legacy_estimate_prerequisites` and estimate guard cases | Three failures: exact measurements were refused for closed/unknown openness or a SKU with multiple memory pools. | Exact verified runs are returned; estimates still require verified open weights and one usable pool. Core/Worker: 83 passed. |
| Gemini schema count and first-turn budget tests | Two failures: nine declarations versus eight expected, and provider totals up to 9,916 tokens versus the existing 9,500 limit. | The test checks all nine exact tool names. Duplicate description prose is removed without changing schemas, guide, instructions or the limit. |
| OpenAPI size budget | 249,382 bytes versus the existing 233,000 limit. | Schema-aware compaction omits generated titles and null defaults. All 170 public schemas retain constraints, descriptions and non-null defaults; the literal validation regression passes. |
| `test_flag_off_response_equals_main` | Six failures from the additive accepted-endpoint entry in historical 404 responses. | All 13 cases pass after adding only the literal new route to expected 404 lists. Full response equality remains enforced. |
| `test_build_emits_every_template_preview_and_card` | Missing local `@playwright/test` dependency. | Locked `web/npm ci` and the exact test under Node 22.22.3 pass; no code or lockfile change. |
| Ablation replay, preflight and new-tool regressions | The completed stable run had 79 ablation failures. New-tool regressions were red with 19 failures and three passes. | Known historical and current descriptions remain exact matches, new tools pass through unchanged, and drift/partial inventories remain refusals. All 297 native ablation cases pass, including the 22 new regressions. |
| `test_required_reporting_rules_are_in_the_generated_guide_and_decide_copy` | The vocabulary description omitted its required one-lookup cadence. | The instruction is restored without changing the token limit or request schema. |
| `test_comparison_markdown_shows_added_and_removed_tools_with_zero_columns` | `KeyError: hardware_fit` comparing eight versus nine tools. | A literal whole-table test passes, including existing, added and removed tools. |
| `test_landing_behaviour_in_browser` | Twelve setup errors: `web/dist/decide.html` did not exist. | Frontend build returned 0; all 12 real browser cases passed with `CI=1`, no skips and no tracked changes. |

Additional red-first checks caught the offline QA dispatcher routing the new
tool to vocabulary, and the deploy smoke checker's stale tool list. Both now
include the keyed hardware route. No existing behavior assertion was removed.

## Commands and versions

Commands ran from the assigned worktree unless a different directory is stated.
Python was `/Users/terbeest/dev/modelspec/.venv/bin/python`, version 3.14.4.
pytest was 9.1.1, pytest-xdist 3.8.0, Pydantic 2.13.5, and PyYAML 6.0.3.
Required Node runs used 22.22.3 and npm 10.9.8. MCP used TypeScript 7.0.2
and Vitest 5.0.1; the frontend compiler was TypeScript 5.9.3. gh was 2.102.0.
The two interrupted Python full runs inherited
the default Node 22.23.1; the final full run explicitly pins 22.22.3 for every
child process. The missing web dependencies were installed from the lockfile.

The core red command returned 1 with `29 failed in 0.35s`:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_hardware_fit.py
```

The subsequent core adversarial, ordering, and shared-input red commands used
the same file plus `--tb=short`. They returned 1 with respectively 4, 1, and
2 failures. After the measurement-prerequisite correction, this command returned 0 with
`83 passed in 1.97s`:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_hardware_fit.py tests/test_hardware_fit_worker.py --tb=short
```

Snapshot/hardware regression coverage returned 0 with
`315 passed in 175.91s`. That earlier run collected the 35-test core revision;
the final core revision and final full suite cover the later additions.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_hardware_fit.py tests/test_decision_snapshot.py tests/test_architecture_facts.py tests/test_hardware.py tests/test_hardware_review.py tests/test_model_174_hardware_private.py tests/test_data_freeze_guard.py --tb=short
```

The Worker/access/billing/vendor regression command returned 0 with
`387 passed, 2 skipped in 8.63s`:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_hardware_fit_worker.py tests/test_api_docs.py tests/test_access_wiring.py tests/test_api_access.py tests/test_compare_models_worker.py tests/test_x402.py tests/test_worker_vendor_imports.py tests/test_worker_bundle.py
```

The Worker and credit-contract red commands returned 1 with 30 failures and
one failure respectively. Their output is retained in the corresponding logs.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_hardware_fit_worker.py tests/test_api_docs.py::test_hardware_fit_documents_its_separate_keyed_contract
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_hardware_fit_worker.py::test_unfunded_hardware_fit_answer_validates_against_its_published_contract
```

After the credit-metadata correction, the two Worker/docs files passed again
with `91 passed, 2 skipped in 9.14s`, exit 0. The standalone copy compatibility
test failed first with exit 1; the complete file then passed with exit 0:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_link.py::test_flag_off_agent_copy_bytes_match_base
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_link.py
```

MCP commands ran in `mcp/` with the required Node directory first on PATH.
`npm ci` returned 0. The first focused test returned 1, then 0 after the fix.
Type checking returned 0. The full MCP suite returned 0 with 201 passing tests
and was repeated successfully after the final copy changes on implementation
commit `c13b81c9`. Type checking also returned 0 on that commit.

```sh
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
npm ci
npm test -- test/hardware-fit.test.ts
npm run typecheck
npm test -- test/server.test.ts --update
npm test
npm test -- test/overhead.test.ts
```

Generated-copy, QA adapter, capture, and smoke-check coverage all returned 0:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_copy.py tests/test_agent_ready.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_harness.py tests/test_mcp_schema_compaction.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_mcp_ci.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_harness.py -k mcp_capture
```

Those test runs reported 49, 91, 11, and 2 passes respectively. The final
capture was also checked against the real SDK tools/list schema by the MCP
overhead test. No QA agent CLI or provider API was invoked.

OpenAPI regeneration and drift checks returned 0:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
```

The drift check printed `api/worker/openapi.yaml matches the implementation`.
The data-freeze guard returned 0 and printed `data freeze: ok`:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base 2b2e9a38f19012658f2b390cbb3f00eb8a00ae75 --head HEAD --branch model-287-hardware-fit
git diff --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 4 --summary
```

The shard planner assigned 69, 69, 69, and 70 files, with balanced predictions.

## Final integration checks

The final focused Python command returned 0 with
`199 passed, 2 skipped in 10.81s`:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_link.py tests/test_hardware_fit.py tests/test_hardware_fit_worker.py tests/test_api_docs.py tests/test_visit_gate_off.py --tb=short
```

An earlier provider/schema/copy/guide command returned 0 with
`162 passed in 28.16s`:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_copy.py tests/test_agent_guide.py tests/test_gemini_driver.py tests/test_agent_harness.py tests/test_mcp_schema_compaction.py
```

Final offline first-turn totals are Claude 9,325, OpenAI 9,418 and Gemini
9,497 estimated tokens. Every provider stays within the unchanged 9,500 limit.
The final OpenAPI is 232,015 bytes, below the unchanged 233,000-byte limit.
The exact catalogue golden was repeated after restoring the published
`Call decide early` instruction: one pass, exit 0.

After restoring the vocabulary instruction, the final focused command returned
0 with `207 passed in 28.36s`:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_copy.py tests/test_agent_gaps.py tests/test_agent_guide.py tests/test_agent_harness.py tests/test_gemini_driver.py tests/test_mcp_schema_compaction.py tests/test_llms_txt.py tests/test_surface_lint.py::test_missing_duplicate_and_unknown_mcp_tools_fail tests/test_surface_lint.py::test_tool_prices_are_checked_against_tiers tests/test_surface_lint.py::test_short_card_credit_prices_follow_tiers
```

Node 22.22.3 was first on PATH. The exact reporting test failed before the fix
and passed afterward. The complete MCP suite then returned 0 with 201 passes;
the actual captured tool metadata matches current sources. The final catalogue
SHA-256 is `faa19be299fb233c78d366f2fed67897f45b87d89d2bad40f96faa2f6f3841b7`.
The exact catalogue golden was repeated successfully. Guide and CLI text
hashes remain unchanged.

The native QA and metrics commands returned 0, with respectively
`297 passed in 59.82s` and `1 passed in 0.04s`:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_ablation_proxy.py tests/test_ablation_targets.py tests/test_ablation.py --tb=short
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_overhead.py
```

These cover all 79 observed ablation failures and 22 new cases. Changed summary
rules, malformed or duplicate examples, unknown tools, altered new-tool text,
and partial current inventories remain refusals. The metric test checks a
literal complete table for existing, added and removed tools.

The literal schema-compaction regression returned 0 with one pass. The existing
whole-document equivalence test first failed on the removed annotations; its
expected comparison now permits only schema titles and null defaults to
disappear. It still compares descriptions, constraints, examples, property
names and non-null defaults. Both regressions then passed together, exit 0. The reusable
[comparison script](MODEL-287/verify_openapi_compaction.py) expands generated
shared references and compares all public schemas modulo title/null-default
annotations. It checked 170 schemas against the pre-compaction implementation.
It can be repeated from the worktree:

```sh
mkdir -p .scratch/model-287/review
git show 01de2058e6516f5e320a894d8f59982ef85a9c91:api/worker/openapi.yaml > .scratch/model-287/review/openapi-before.yaml
/Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-287/verify_openapi_compaction.py .scratch/model-287/review/openapi-before.yaml api/worker/openapi.yaml
```

The social-card environment correction and exact failing test returned 0:

```sh
(cd web && PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci)
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_social_cards.py::test_build_emits_every_template_preview_and_card
```

The test reported `1 passed in 187.99s`. Chromium was already cached. No
browser download or package-manifest change was needed. Landing-page setup
also required the ignored frontend build, then its exact 12 browser cases
returned 0 with `12 passed in 23.11s`:

```sh
(cd web && PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm --ignore-scripts run build)
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD CI=1 /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_landing.py::test_landing_behaviour_in_browser
```

`CI=1` prevents a missing browser from becoming a skip. Chromium 1243 was
already installed. No browser download or tracked-file change was needed.

## Full suite

Two preliminary full runs were interrupted while corrections were still
being integrated. Both exited 2 from SIGINT; all child processes were reaped.
The first reported one catalogue-golden failure, 8,297 passes and five skips.
The second reported 10 failures, 11,001 passes and 22 skips in 1,114.75 seconds.
Its failures were the Gemini tool count, first-turn token budget, OpenAPI byte
budget, six 404 endpoint lists, and the missing web dependency described above.
Their original outputs are retained alongside the focused red/green logs.

A completed run on `6c61b455` then returned 1 with
`80 failed, 11228 passed, 9 skipped, 12 errors in 1833.02s`. Of the 80 failures,
79 were the ablation compatibility issues and one was the vocabulary
instruction assertion. All 12 errors came from the missing frontend build.
That full report is retained as `stable-full-failed.log.gz`.

The required final command runs on the stable implementation commit named
above, with the required Node directory inherited by all child processes:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Final result: **11343 passed, 9 skipped, 11 warnings in 1401.16s (0:23:21)**,
exit **0**. The warnings are the existing unsigned-vocabulary warnings in CLI
fixture tests. The complete output is retained as
[final-full-green.log.gz](MODEL-287/final-full-green.log.gz).
No implementation files changed during this run. The delivery commit adds
only this evidence and its retained artifacts after the tested code commit.

## Observation limits

Core and API tests use synthetic source records through real admission,
verification, signing, and route code. MCP tests use synthetic origin responses
through the real local MCP transport. No real device workload, deployed
Worker, or private curated workload dataset was observed.
No new production source facts were written. Existing snapshots without exact
workload records return `undetermined`; the endpoint does not infer them from
`model.fits_hardware` or the generic quantisation/headroom constants.

No vendor API spend, production deployment, switch changes, Linear writes,
or merge occurred. The PR remains a draft for independent review.
