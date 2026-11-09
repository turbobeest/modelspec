# MODEL-458-DOCS execution evidence

Base: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`. `git fetch origin main` confirmed this was current `origin/main` before changes.

All pytest invocations used serial execution in the `model-458-docs` worktree. Each regression ran against unchanged documentation before its correction. Existing behavior tests were preserved.

Tool versions: Python 3.14.4, pytest 9.1.1, Node v22.22.3, git 2.50.1. Version commands: `python3 --version`, `/Users/terbeest/dev/modelspec/.venv/bin/python --version`, `/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --version`, `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --version`, `git --version`.

Not observed: deployed service responses, production account inventory, private catalogue contents, payment settlement, edge memory or latency. No deployment, paid calls, production configuration changes, legal changes or catalogue changes were performed. CI owns the full suite; local checks are focused. No background services were started.

## AUD-09-F1

The decide transport reference matches contract 2.19, bundled split serving, keyed vocabulary and the thin hosted CLI. Legacy export and library modes are identified explicitly.

f1-red; exit 1.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f1-red tests/test_reference_decide.py
```

```text
FAILED tests/test_reference_decide.py::test_decide_reference_current_contract_matches_implementation
FAILED tests/test_reference_decide.py::test_decide_reference_describes_split_serving_and_legacy_exports
2 failed in 0.29s
```

f1-green; exit 0.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f1-green tests/test_reference_decide.py tests/test_api_docs.py::test_the_policy_example_is_a_request_the_endpoint_answers tests/test_api_docs.py::test_the_policy_reference_states_the_parsers_limits tests/test_api_docs.py::test_the_access_gate_is_wired_and_the_reference_says_it_is_enforced tests/test_decision_contract.py tests/test_hardware_fit_worker.py tests/test_feedback.py tests/test_decide_worker.py::test_entry_prepares_bundle_before_the_first_request tests/test_cli_concierge.py::test_decide_sends_exactly_the_supplied_spec_and_passes_the_body_through tests/test_cli_concierge.py::test_decide_adds_bounded_fields_only_when_the_spec_omits_them
```

```text
368 passed in 3.89s
```

## AUD-09-F2

The worked policy request reaches the local enforced Worker with a fixture key. Pagination defaults and boundaries match the parser; sandbox recovery directs callers to a live key.

f2-red; exit 1.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f2-red tests/test_reference_policy_transport.py
```

```text
FAILED tests/test_reference_policy_transport.py::test_policy_reference_worked_command_reaches_success
FAILED tests/test_reference_policy_transport.py::test_policy_reference_pagination_defaults_match_parser[offset]
FAILED tests/test_reference_policy_transport.py::test_policy_reference_sandbox_recovery_requires_a_live_key
3 failed, 1 passed in 1.04s
```

f2-green; exit 0.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f2-green tests/test_reference_policy_transport.py tests/test_api_docs.py
```

```text
60 passed, 2 skipped in 17.39s
```

## AUD-09-F3

Public replay guidance distinguishes deterministic evaluation from hosted snapshot availability. The synthetic pinned request returns 200 before replacement, 409 afterward, and 200 with latest. Generated guide outputs were refreshed.

f3-red; exit 1.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f3-red tests/test_reference_decide.py::test_public_snapshot_replay_guidance_discloses_current_only_availability
```

```text
FAILED tests/test_reference_decide.py::test_public_snapshot_replay_guidance_discloses_current_only_availability
1 failed in 0.87s
```

f3-green; exit 1.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f3-green tests/test_reference_decide.py tests/test_access_wiring.py::test_on_an_unkeyed_request_is_refused_and_told_how_to_get_a_key tests/test_agent_guide.py tests/test_llms_txt.py tests/test_decide_worker.py::test_a_requested_snapshot_must_be_the_loaded_snapshot
```

```text
FAILED tests/test_agent_guide.py::test_coverage_pointer_keeps_all_three_mcp_first_turns_under_budget
FAILED tests/test_agent_guide.py::test_harness_prompt_arms_replay_offline[mcp-False]
FAILED tests/test_agent_guide.py::test_harness_prompt_arms_replay_offline[http-False]
FAILED tests/test_agent_guide.py::test_harness_prompt_arms_replay_offline[mcp-True]
FAILED tests/test_agent_guide.py::test_harness_prompt_arms_replay_offline[http-True]
5 failed, 25 passed in 30.27s
```

f3-focused; exit 0.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f3-focused tests/test_reference_decide.py tests/test_access_wiring.py::test_on_an_unkeyed_request_is_refused_and_told_how_to_get_a_key tests/test_agent_guide.py::test_generated_guide_and_constants_are_stable_and_within_budget tests/test_agent_guide.py::test_all_guide_specs_parse_against_the_registry tests/test_llms_txt.py tests/test_data_lag.py::test_no_commit_old_enough_changes_nothing tests/test_data_lag.py::test_the_seed_publishes_on_the_ninth_month tests/test_decide_worker.py::test_a_requested_snapshot_must_be_the_loaded_snapshot tests/test_legal.py
```

```text
106 passed in 3.46s
```

Generation command: `env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write`; exit 0. The generated Worker change is only its same-width guide version. No schema or catalogue output changed.

The broader guide run reported five capture-coherence failures because `qa/fixtures/mcp-tools.json` pins the two regenerated guide hashes. A combined metadata patch was prepared in scratch. It updates two guide-version strings in `api/worker/openapi.yaml` and three source hashes in `qa/fixtures/mcp-tools.json`. Both files are outside the spec's named edit paths and await scope approval. The spec's focused guide checks and the complete legal test file passed.

The required private-data memory probe ran through `~/.codex-g2/heavy.sh` with a throwaway signing key, Python 3.14.4, Node v22.22.3 and Pyodide 0.28.3; exit 0. Current steady memory was 114269259 bytes (108.97566 MiB), successor 108793627 bytes (103.75369 MiB). Both passed 115 MiB. Public vendoring with `--check` passed. The private clone, generated bundles and raw private logs were removed. No production service was queried.

The probe script was invoked as `/Users/terbeest/.codex-g2/heavy.sh /bin/bash /tmp/MODEL-458-DOCS-scratch/operations/memory/run-memory.sh`. Its exact commands follow; setup ran `mkdir -p /tmp/MODEL-458-DOCS-scratch/operations/memory/tmp`, then `GIT_TERMINAL_PROMPT=0 git clone --depth 1 --single-branch https://github.com/turbobeest/modelspec-data.git /tmp/MODEL-458-DOCS-scratch/operations/memory/modelspec-data > /tmp/MODEL-458-DOCS-scratch/operations/memory/clone.log 2>&1`. Both returned 0.

```bash
#!/bin/bash
set -euo pipefail
cd /Users/terbeest/dev/worktrees/model-458-docs
scratch=/tmp/MODEL-458-DOCS-scratch/operations/memory
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
export PYTHONPATH=$PWD
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR=$scratch/tmp
export MODELSPEC_SNAPSHOT_KEY=model458-docs-memory-fixture-key
export MODELSPEC_REQUIRE_DATA_DIR=0
python=/Users/terbeest/dev/modelspec/.venv/bin/python
"$python" api/worker/vendor.py --out "$scratch/public-bundle" --check > "$scratch/public-vendor.log" 2>&1
export MODELSPEC_REQUIRE_DATA_DIR=1
"$python" api/worker/vendor.py --data-dir "$scratch/modelspec-data" --out "$scratch/private-bundle" > "$scratch/private-vendor.log" 2>&1
"$python" - <<'PY'
import shutil, subprocess
from pathlib import Path
scratch=Path('/tmp/MODEL-458-DOCS-scratch/operations/memory')
paths=subprocess.run(['git','ls-files','api/worker/src/*.py'],check=True,capture_output=True,text=True).stdout.splitlines()
for name in paths:
    path=Path(name)
    if path.parent == Path('api/worker/src'):
        shutil.copyfile(path,scratch/'private-bundle'/path.name)
assert (scratch/'private-bundle/agent_guide.py').read_bytes() == Path('api/worker/src/agent_guide.py').read_bytes()
PY
npm install --prefix "$scratch/runtime" --no-save pyodide@0.28.3 > "$scratch/npm.log" 2>&1
export NODE_PATH=$scratch/runtime/node_modules
node --expose-gc api/worker/measure_memory.cjs "$scratch/private-bundle" --limit-mib 115 --output "$scratch/current.json" > "$scratch/current.log" 2>&1
node --expose-gc api/worker/measure_memory.cjs "$scratch/private-bundle" --successor --limit-mib 115 --output "$scratch/successor.json" > "$scratch/successor.log" 2>&1
"$python" - <<'PY'
import json
from pathlib import Path
scratch=Path('/tmp/MODEL-458-DOCS-scratch/operations/memory')
for period in ('current','successor'):
    data=json.loads((scratch/f'{period}.json').read_text())
    print(json.dumps({key:data[key] for key in ('period','steady_bytes','steady_mib')} | {'limit_mib':115}))
PY
```

## AUD-09-F5

The access guide uses the workflow deploy command, documents generated tier-policy fallback and matches checked-in access, visit and friends configuration.

f5-red; exit 1.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f5-red tests/test_reference_access.py
```

```text
FAILED tests/test_reference_access.py::test_access_reference_deploy_command_matches_workflow
FAILED tests/test_reference_access.py::test_access_reference_explains_generated_policy_fallback
FAILED tests/test_reference_access.py::test_access_reference_shipped_settings_match_configuration
3 failed in 0.09s
```

f5-green; exit 0.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f5-green tests/test_reference_access.py tests/test_tier_policy_bundle.py tests/test_friends_billing.py tests/test_x402.py::test_enforcement_refuses_a_spoofed_site_origin_when_x402_is_on tests/test_access_wiring.py::test_on_an_unkeyed_request_is_refused_and_told_how_to_get_a_key tests/test_visit_gate.py::test_spoofed_origin_with_no_token_gets_no_answer
```

```text
31 passed in 1.14s
```

## AUD-09-F6

Billing defaults match the shipped friends prefix and local stubbed Checkout request. Current x402 flags and generated policy delivery are documented without changing commercial terms.

f6-red; exit 1.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f6-red tests/test_reference_billing.py
```

```text
FAILED tests/test_reference_billing.py::test_billing_reference_friends_defaults_match_checkout
FAILED tests/test_reference_billing.py::test_billing_reference_current_x402_flags_and_policy_delivery
2 failed in 0.10s
```

f6-green; exit 0.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f6-green tests/test_reference_billing.py tests/test_friends_billing.py tests/test_tier_policy_bundle.py tests/test_billing.py
```

```text
106 passed in 0.72s
```

## AUD-09-F8

The data-split guide documents both enforced 115 MiB PR periods, the separate growth warning, and every retained public export category. Synthetic export retention and the memory assessor agree with the guide.

f8-red; exit 1.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f8-red tests/test_reference_data_split.py
```

```text
FAILED tests/test_reference_data_split.py::test_data_split_operating_guide_matches_memory_gate_and_retained_exports
1 failed in 0.11s
```

f8-green; exit 0.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f8-green tests/test_reference_data_split.py tests/test_worker_memory.py::test_memory_gate_accepts_exactly_115_mib_and_rejects_one_byte_above tests/test_worker_memory.py::test_public_memory_workflow_gates_and_compares_the_main_bundle tests/test_feedback_digest.py::test_no_workflow_runs_the_digest tests/test_data_freeze_guard.py::test_a_data_change_on_an_ordinary_branch_fails_and_names_the_file tests/test_blog_deployment.py::test_retained_snapshot_is_preserved_while_other_bulk_exports_are_removed tests/test_cli_concierge.py::test_local_and_usage_errors_always_carry_next
```

```text
30 passed in 0.83s
```

## AUD-09-F10

The holding runbook separates SITE_MODE from Checkout and describes the current CLI and bundled Worker. Its documented command resolves through the installed CLI command tree; existing holding tests pass.

f10-red; exit 1.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f10-red tests/test_reference_holding.py
```

```text
FAILED tests/test_reference_holding.py::test_holding_runbook_matches_checkout_flag_and_current_cli
1 failed in 0.12s
```

f10-green; exit 0.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f10-green tests/test_reference_holding.py tests/test_holding.py tests/test_cli_concierge.py::test_local_and_usage_errors_always_carry_next
```

```text
71 passed in 62.64s (0:01:02)
```

## AUD-09-F12

The contribution entry routes fresh card edits to the private data repository and identifies the public image as frozen. The destination matches the executable Data freeze guard.

f12-red; exit 1.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f12-red tests/test_reference_contributions.py
```

```text
FAILED tests/test_reference_contributions.py::test_readme_routes_fresh_card_contributions_to_private_data
1 failed in 0.05s
```

f12-green; exit 0.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f12-green tests/test_reference_contributions.py tests/test_data_freeze_guard.py
```

```text
12 passed in 0.25s
```

## AUD-09-F14

The x402 reference matches local Worker admission under checked-in flags, limits the verified visit exception to decide and vocabulary, and distinguishes production, staging and legacy enforcement-off behavior.

f14-red; exit 1.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f14-red tests/test_reference_x402.py
```

```text
FAILED tests/test_reference_x402.py::test_x402_reference_origin_admission_matches_shipped_flags
FAILED tests/test_reference_x402.py::test_x402_reference_settings_match_production_and_staging
2 failed in 0.56s
```

f14-green; exit 0.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f14-green tests/test_reference_x402.py tests/test_x402.py tests/test_visit_gate.py
```

```text
183 passed in 2.11s
```

## AUD-09-F15

The x402 runbook identifies the completed checked-in mainnet rollout and separates staging procedures from historical preparation. Configuration tests retain the existing production and staging values.

f15-red; exit 1.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f15-red tests/test_reference_x402_launch.py
```

```text
FAILED tests/test_reference_x402_launch.py::test_x402_launch_reference_matches_completed_configuration
1 failed in 0.05s
```

f15-green; exit 0.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f15-green tests/test_reference_x402_launch.py tests/test_x402.py::test_production_x402_config_is_live tests/test_x402.py::test_wrangler_enables_x402_on_base_mainnet tests/test_release_signals.py::test_v1_schema_accepts_the_documented_contract tests/test_release_signals.py::test_parser_accepts_rfc3339_and_rejects_instances_outside_the_contract tests/test_release_signals.py::test_hmac_signature_covers_the_exact_request_body tests/test_release_signals.py::test_worker_intake_authenticates_deduplicates_and_lists_pending tests/test_release_signals.py::test_pending_work_includes_every_signal_and_due_recheck tests/test_release_signals.py::test_hourly_workflow_keeps_github_credentials_out_of_the_signal_sender tests/test_release_signals.py::test_worker_endpoint_ships_off_and_vendors_the_shared_contract tests/test_decision_verify.py::test_cli_verifies_what_is_queued_and_prints_a_summary tests/test_decision_verify.py::test_cli_claude_reader_uses_an_injected_extractor tests/test_cli_concierge.py::test_local_and_usage_errors_always_carry_next
```

```text
38 passed in 1.50s
```

## AUD-02-F6

The literal policy-contract request returns HTTP 200 with nonempty rows against the frozen catalogue. The optional model filter is omitted and the example explains how to choose catalogue IDs. The broader API documentation check reports the separate guide-version metadata dependency noted under AUD-09-F3.

aud02-f6-red; exit 1.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-aud02-f6-red tests/test_reference_policy_contract.py
```

```text
FAILED tests/test_reference_policy_contract.py::test_policy_contract_complete_request_returns_a_nonempty_answer
1 failed in 8.81s
```

aud02-f6-green; exit 1.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-aud02-f6-green tests/test_reference_policy_contract.py tests/test_api_docs.py
```

```text
FAILED tests/test_api_docs.py::test_the_committed_spec_is_what_the_implementation_generates
1 failed, 56 passed, 2 skipped in 12.73s
```

aud02-f6-focused; exit 0.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-aud02-f6-focused tests/test_reference_policy_contract.py
```

```text
1 passed in 7.58s
```

## AUD-09-F4

Additive AGENTS descriptions list all public export classes and all automerge exceptions. Every original line, including all binding rules, remains unchanged.

f4-red; exit 1.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f4-red tests/test_reference_agent_entry.py
```

```text
FAILED tests/test_reference_agent_entry.py::test_agent_entry_documents_public_export_exceptions
FAILED tests/test_reference_agent_entry.py::test_agent_entry_documents_automerge_exceptions
2 failed in 0.04s
```

f4-green; exit 0.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f4-green tests/test_reference_agent_entry.py tests/test_worker_memory.py::test_memory_gate_accepts_exactly_115_mib_and_rejects_one_byte_above tests/test_worker_memory.py::test_public_memory_workflow_gates_and_compares_the_main_bundle tests/test_feedback_digest.py::test_no_workflow_runs_the_digest tests/test_data_freeze_guard.py::test_a_data_change_on_an_ordinary_branch_fails_and_names_the_file tests/test_blog_deployment.py::test_retained_snapshot_is_preserved_while_other_bulk_exports_are_removed tests/test_cli_concierge.py::test_local_and_usage_errors_always_carry_next
```

```text
31 passed in 0.77s
```

## Final validation

After the local commit cleanup, all final documentation regressions, landing copy checks, source exclusions and billing-launch checks passed. The first final run was stopped during commit cleanup and is not used as evidence; the stable-tree rerun below is the measured result.

f1-review-red; exit 1.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f1-review-red tests/test_reference_decide.py::test_decide_reference_bundled_comparison_does_not_fetch_public_history tests/test_reference_decide.py::test_decide_reference_describes_bundled_successor_transition
```

```text
FAILED tests/test_reference_decide.py::test_decide_reference_bundled_comparison_does_not_fetch_public_history
FAILED tests/test_reference_decide.py::test_decide_reference_describes_bundled_successor_transition
2 failed in 0.68s
```

f1-review-green; exit 0.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-f1-review-green tests/test_reference_decide.py tests/test_snapshot_successor.py
```

```text
23 passed in 1.52s
```

final-focused; exit 0.

```bash
env PYTHONDONTWRITEBYTECODE=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/MODEL-458-DOCS-scratch/root/pytest-final-focused tests/test_reference_decide.py tests/test_reference_policy_transport.py tests/test_reference_access.py tests/test_reference_billing.py tests/test_reference_data_split.py tests/test_reference_holding.py tests/test_reference_contributions.py tests/test_reference_x402.py tests/test_reference_x402_launch.py tests/test_reference_policy_contract.py tests/test_reference_agent_entry.py tests/test_removed_sources.py tests/test_landing.py::test_the_positioning_copy_types_no_numbers tests/test_landing.py::test_every_analysis_row_links_to_a_proof_that_exists tests/test_landing.py::test_the_positioning_does_not_overclaim tests/test_billing_launch.py
```

```text
98 passed, 1 skipped in 96.84s (0:01:36)
```

The final focused command above was invoked through `/Users/terbeest/.codex-g2/heavy.sh` because the landing fixtures build site data. The first overlapping attempt was terminated with exit 143 and discarded before the stable-tree rerun.

Additional scope checks: `git diff --check 5dd0eb5a HEAD` exited 0. A line-subsequence check against `git show 5dd0eb5a:AGENTS.md` confirmed all 72 original lines remain. Inspection of `git diff --name-only 5dd0eb5a HEAD` confirmed no frozen data, legal files, workflows, prices, ranking floors or production configuration changed. `gh --version` reported 2.103.3.

The branch contains exactly 12 finding commits in spec order. Local review corrections were folded into their finding commits with `GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash 5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`; the final tree matches the pre-cleanup tree. No existing tests were weakened.

Final tested implementation SHA: `9fbc8c457764bea0859c81456cd72c81128443aa`. The final evidence-only amendment changes this file; the submitted full head SHA is recorded in the PR body and executor completion marker, and can be reproduced with `git rev-parse model-458-docs`.

Publication commands: `CI_LOCAL_SKIP=1 git push -u origin model-458-docs`, then from `/tmp`, `gh pr create -R turbobeest/modelspec --draft --base main --head model-458-docs --title "MODEL-458: reference docs match the running service" --body-file /tmp/MODEL-458-DOCS-scratch/root/pr-body.md`. No merge or ready action is authorized or performed.

Remaining limitation: the requested scope does not name the two generated metadata files above. The actual worktree therefore retains five guide-capture coherence failures and one OpenAPI generation coherence failure. All permanent regression cases for the twelve findings pass. The draft is BLOCKED until that prepared metadata update is authorized and the affected existing checks are rerun. No runtime fix, schema-range widening, production switch, legal text, price or plan change is needed.

The final focused skip is the optional built-dist source check, which requires `MODELSPEC_DIST`. The two earlier API-documentation skips require `MODELSPEC_LIVE_API=1`; no live probes ran.
