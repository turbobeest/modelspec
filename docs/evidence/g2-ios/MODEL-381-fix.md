# MODEL-381 execution evidence

Worktree: `/Users/terbeest/dev/worktrees/model-381`.
Branch: `sparksandsawdust/model-381-router-config-keyed`.
Base SHA: `d5569420b07ab8c7dd8efa2117789afb36505197`.
Final implementation SHA: `b00af6608bcadb328b388f5ef05949ebd99c7afb`.
The evidence-only delivery commit follows the implementation commit. Resolve
the delivery SHA with `git rev-parse HEAD` on this branch.

## Decision and behavior

Chose spec option **(b)**. Bounded responses already retain verified
`api_model_id` and `router_slug` on returned offering references, but omit
the bands that the existing renderer needs. The distributed CLI excludes
the decision engine. An optional HTTP `router_config` control lets the Worker
reuse `decision.router_config.render` on the complete decision before
projection. The CLI prints that text or writes it to `--out`.

The request names `format` and optional `include_rest` and `include_thin`
booleans. A non-null control opts into the bounded representation, including
with `fields: null`. The optional response string stays intact during budget
trimming. It counts toward the existing 16,384-byte MCP text budget and the
drill-down budget. A configuration that cannot fit is refused. No route is
silently cut from it.

Every export requires an API key, even with access enforcement off or a valid
site, visit, or human credential. Existing keyed quotas and billing apply.
Verified provider IDs and separate router slugs retain their exact values.
Unknown IDs retain their fail-closed placeholder and reason.

Complete contract 2.17 and bounded 1.2 retain their versions. Existing fields
and refusal enums keep their ranges. The new optional control, response field,
and separate `DecisionRouterConfigRefused` schema are additive. Ordinary
decision bytes and spec hashes are unchanged. The existing renderer still
lists each band's offering and the other ranked offerings retained by the
spec's `limit`; it does not rerun the engine with a larger limit.

## Red-first results

The CLI tests ran before the CLI options were implemented. Worker tests ran
before Worker production changes. The key-gate matrix ran before its guard.

| Defect or requirement | Test name | Observed red output | Observed green output |
| --- | --- | --- | --- |
| Keyed command cannot emit a LiteLLM config | `test_keyed_litellm_config_has_verified_ids_and_passes_schema` | `assert 1 == 0`; `The command or options could not be read.` | Passed; exact `openai/verified-provider-id`, Authorization header, and vendored LiteLLM schema verified |
| Optional LiteLLM runtime loading | `test_keyed_config_loads_in_litellm_router` | Unsupported option, `assert 1 == 0` | Clean skip because LiteLLM is not installed; the pure schema test passed |
| Null IDs keep placeholders and reasons | `test_null_identifiers_keep_worker_placeholder_and_reason`, `test_null_router_id_keeps_a_placeholder_and_reason` | CLI unsupported option; Worker returned 400 instead of 200 | Passed for CLI LiteLLM, OpenRouter, and JSON cases; signed Worker snapshot emits `<openai model id for lab/solid>` and its no-verified-ID reason |
| Flags reach the keyed Worker and include the requested bands | `test_template_and_band_options_reach_worker`, `test_requested_bands_are_complete_even_beyond_limit` | CLI unsupported options; Worker returned 400 instead of 200 | Passed for default, rest, thin, and both; thin is labelled and every selected band member remains beyond result `limit` |
| Flag combinations retain the legacy error code | `test_router_flag_errors_have_legacy_code_and_exit_one` | `usage_error` instead of `router_config_usage` | Five cases passed, exit 1: out/rest/thin without emit, invalid format, JSON without out; no HTTP call |
| JSON and file output stay separate | `test_config_file_keeps_one_json_worker_body` | `assert 1 == 0` | Both command-level and root-level JSON cases passed; config file and one unchanged Worker JSON body verified |
| Missing key, missing config, or unwritable output fails safely | `test_config_requires_key_before_spec_read_or_http`, `test_missing_rendered_config_fails_without_writing`, `test_unwritable_config_is_a_structured_error` | Unsupported options; generic `usage_error` | Passed with exits 5, 1, and 1 and expected codes; missing key reads no spec and makes no HTTP call |
| Worker renders verified IDs before projection | `test_verified_router_ids_survive_a_bounded_projection`, `test_openrouter_uses_verified_slugs_instead_of_provider_ids` | Worker returned 400 instead of 200 | Passed with signed synthetic snapshot, exact provider IDs and separate router slugs, schema validation, and byte-budget assertions |
| Optional controls preserve the original answer | `test_router_request_opts_into_bounded_with_explicit_null_fields`, `test_response_controls_preserve_the_spec_hash_and_ordinary_body` | Worker returned 400 instead of 200 | Passed; body except the requested string and canonical spec hash match the ordinary response |
| Oversized configs fail instead of being shortened | `test_oversized_router_config_refuses_without_cutting_the_allow_list` | Expected router-config budget issue was absent | Passed; 400 `invalid_spec`, issue path `router_config`, no returned configuration, refusal within budget |
| Empty or unrenderable decisions retain renderer codes | `test_unrenderable_router_decisions_have_their_own_refusal` | `invalid_spec` instead of renderer code | Three cases passed: `no_bands`, `no_qualifying_models`, `empty_allow_list`; existing refusal enums unchanged |
| Human paths cannot admit a keyless export | `test_router_export_never_admits_a_keyless_machine_or_site_credential` | Expected 401, received 200 in bypass cases | Sixteen cases passed across enforcement, x402, machine/site/visit/human; no snapshot fetch or access-store mutation |

Initial CLI run, exit 1:

```text
16 failed in 0.32s
```

Initial Worker run, exit 1:

```text
13 failed, 3 passed
```

Entry key-gate red run, exit 1:

```text
12 failed, 4 passed, 18 deselected
```

Focused green results, each exit 0:

```text
15 passed, 1 skipped in 0.19s
34 passed in 1.73s
264 passed, 1 skipped in 1.37s
```

## Broader verification

The first required full run used the local timezone and exited 1:

```text
FAILED tests/test_api_docs.py::test_decide_response_description_uses_the_bounded_version
FAILED tests/test_decision_link.py::test_flag_off_agent_copy_bytes_match_base
FAILED tests/test_access_wiring.py::test_with_no_tier_table_a_key_is_refused_and_anonymous_is_unaffected
FAILED tests/test_agent_ready.py::test_built_tree_passes_surface_lint
4 failed, 10487 passed, 9 skipped, 11 warnings in 1991.49s (0:33:11)
```

The OpenAPI description now names the new control. Its existing literal test
was updated to that exact description, still checking the dynamic bounded
version. The CLI-copy hash now pins the router help and error text. The MCP
copy and guide hashes and disabled decision-link response hashes are unchanged.

The no-policy test received 401 instead of 500 because Worker regeneration
created `tier_policy.py`. When the patched default path was absent, the loader
still read that generated fallback. The fixture now makes the fallback absent
too. Its original status, error-code, and anonymous-behavior assertions remain.
The failure reproduced alone; a probe confirmed the imported policy module and
the entry's module were the same object.

Those three tests then passed, exit 0:

```text
3 passed in 2.24s
```

The surface-lint failure reported source freshness `2026-10-13`, expected
`2026-10-14`. Direct calendar probes showed local date `2026-10-13` and UTC date
`2026-10-14`. The full rerun uses `TZ=UTC` to align build and lint dates.

The full UTC rerun passed, exit 0:

```text
10491 passed, 9 skipped, 11 warnings in 1346.90s (0:22:26)
```

The four-shard balance summary also exited 0. It assigned 63, 64, 63, and
63 files, with predicted durations of 3394.176, 3394.178, 3394.177, and
3394.176 seconds respectively.

MCP typechecking passed. After regenerating the one tools/list snapshot that
gained `router_config` and `RouterConfigOptions`, all MCP tests passed:

```text
Test Files  9 passed (9)
Tests  166 passed (166)
```

An intermediate Worker regression run was stopped to add the key-only guard.
It had 81 passed and 1 skipped when interrupted and exited 2 from
`KeyboardInterrupt`; it is not counted as a completed passing suite.

## Commands and tools

Python verification commands used Python 3.14.4 at
`/Users/terbeest/dev/modelspec/.venv/bin/python`, with pytest 9.1.1.
Node was v22.22.3 from `/Users/terbeest/.nvm/versions/node/v22.22.3/bin`;
npm 10.9.8, TypeScript 7.0.2, Vitest 5.0.1, Ruff 0.16.6, Git 2.50.1, and
gh 2.102.0.

From the worktree, focused and full verification commands were:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_keyed_router_cli.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_keyed_router_worker.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_keyed_router_worker.py -k keyless
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_keyed_router_worker.py tests/test_decide_worker.py tests/test_decide_agent_budget.py tests/test_decision_router_config.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_keyed_router_cli.py tests/test_decision_contract.py tests/test_worker_vendor_imports.py
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_api_docs.py::test_decide_response_description_uses_the_bounded_version tests/test_decision_link.py::test_flag_off_agent_copy_bytes_match_base tests/test_access_wiring.py::test_with_no_tier_table_a_key_is_refused_and_anonymous_is_unaffected
TZ=UTC PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 4 --summary
```

Tests logged to scratch files used this shell pattern so the test exit was
checked directly:

```sh
COMMAND > OUTPUT_FILE 2>&1
result_code=$?
cat OUTPUT_FILE
exit "$result_code"
```

The full run displayed `tail -80 OUTPUT_FILE` instead of the whole log; its
saved exit code was still returned directly.

Generators and consistency checks:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m decision.schema
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python qa/contracts.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/vendor.py --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m decision.schema --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check cli/modelspec/cli.py tests/test_keyed_router_cli.py --output-format concise
git diff --check
```

The Worker bundle imported with only declared dependencies. Only changed
generated files were committed. The targeted Ruff check passed; an earlier
exploratory check across agent-copy and vendor code also reported existing
formatting issues and the new test's long lines, which were corrected in the
new test. It was not a passing repository-wide lint check.

From `web/`:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm run build
```

From `mcp/`:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm run typecheck
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test -- --update --testNamePattern 'tools/list returns all eight tools with object input schemas'
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test
```

The first MCP run exited 1 with only the expected tools/list snapshot mismatch.
The targeted regeneration and final complete MCP run exited 0. The diff adds
only the new control and its options definition.

Machine load repeatedly exceeded 30, reaching 185 during the first full run.
The executor waited two minutes and rechecked before starting additional work.
An owned active pytest worker was sampled without terminating it:

```sh
lsof -a -p 34199 -d cwd -Fn
ps -o pid,ppid,etime,pcpu,comm -p 34189,34193,34195,34197,34199
sample 34199 1 -file docs/evidence/g2-ios/model-381-cli/pytest-sample.txt
```

Calendar probes:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python -c 'from datetime import date; print(date.today())'
TZ=UTC /Users/terbeest/dev/modelspec/.venv/bin/python -c 'from datetime import date; print(date.today())'
```

## What was not observed

LiteLLM was not installed, so actual `litellm.Router` construction was not
observed. Both mocked CLI and signed Worker output passed its vendored pure
schema. No production deployment, provider inference, router upload, paid API
probe, or live billing behavior was exercised. The WSL gate was not run.
No production switches, credentials, frozen data, legal terms, or ranking
floors changed. Cross-model review remains pending, and the PR remains draft.
