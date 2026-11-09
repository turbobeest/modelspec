# MODEL-458-DOCS execution evidence

Base: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`. `git fetch origin main` confirmed this was current `origin/main` before changes.

All checks ran serially in the `model-458-docs` worktree. Each regression ran against unchanged documentation before its correction. Existing behavior tests were preserved.

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
