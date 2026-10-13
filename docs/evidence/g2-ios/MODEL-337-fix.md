# MODEL-337 fix evidence

When a decide Spec omits `fields`, the keyed CLI sends the bounded row list. An explicit `fields` value, including null, is sent unchanged. The printed `--json` body is still the API body. A bounded request is answered with `explanation.omitted`, and with `explanation.fetch` when records were left out. `modelspec-dev` is 1.0.0 because that changes the default result shape. The CLI error contract stays at 2.0.

Worktree: `/Users/terbeest/dev/worktrees/model-337`.
Branch: `sparksandsawdust/model-337-bounded-cli`.
Base SHA: `8825a31c2f215f6737eefbc7fa2ab2927161b7b5`.
Final tested implementation SHA: `2970caf2b98821e4679cb89efdf4191f20c34e13`.

The final delivery commit adds only this evidence report. Resolve its SHA with `git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-337-fix.md`. The PR body and executor completion line also record that SHA. A report committed to Git cannot contain its own commit hash.

All commands below ran from the worktree above. Each pytest and npm process's exit code was read directly. No test command was piped.

Tools: Python 3.14.4, pytest 9.1.1, pytest-xdist 3.8.0, Git 2.50.1, GitHub CLI 2.102.0, Node v22.22.3, npm 10.9.8. The host reported macOS 27.2, arm64. Versions came from:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import platform
import sys
from importlib.metadata import version
print('Python:', sys.version.split()[0])
print('pytest:', version('pytest'))
print('pytest-xdist:', version('pytest-xdist'))
print('Platform:', platform.platform())
PY
git --version
gh --version
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --version
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm --version
```

## Defect

The keyed `decide` command posted the Spec unchanged when `fields` was absent, so the default `--json` body was the complete Decision.

Red test, written before the production change: `test_decide_adds_bounded_fields_only_when_the_spec_omits_them`.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cli_concierge.py::test_decide_adds_bounded_fields_only_when_the_spec_omits_them --tb=short
```

Exit code: `1`. The unset fixture spec has no `explain` and no `fields`. The server default for `explain` is summary, so the expected list includes `contributions` and `evidence`. The CLI sent neither. Output:

```text
F                                                                        [100%]
=================================== FAILURES ===================================
________ test_decide_adds_bounded_fields_only_when_the_spec_omits_them _________
tests/test_cli_concierge.py:429: in test_decide_adds_bounded_fields_only_when_the_spec_omits_them
    assert sent.get("fields") == expected
E   AssertionError: assert None == ['model_rank', 'cost_per_task', 'estimates', 'p_best', 'contributions', 'evidence']
1 failed in 0.77s
```

The same test after the change:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cli_concierge.py::test_decide_adds_bounded_fields_only_when_the_spec_omits_them --tb=line
```

Exit code: `0`. Output:

```text
.                                                                        [100%]
1 passed in 15.68s
```

The test pins that list to `decision.bounded.row_fields_for` and to `mcp/test/fixtures/default-decide-request.json`. MCP's unset request forces `explain: none` and therefore the four default fields. The CLI leaves `explain` unset, so it sends the summary list. Explicit `fields`, including null, matches the fixture request's `fields` and is not rewritten. A keyless call still exits `missing_api_key` before HTTP. When the mock sees a field list, the printed body keeps `explanation.omitted` and `explanation.fetch`.

## Commands

Focused CLI tests, before the full suite:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_cli_concierge.py tests/test_cli_compare.py tests/test_pypi_packaging.py tests/test_agent_copy.py --tb=line
```

Exit code: `0`. `221 passed`.

The required suite, after `npm ci` and `npm run build` in `web/` so the `CI=true` browser checks had Playwright and `web/dist`:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
```

Exit code: `0`. `9719 passed, 8 skipped, 11 warnings in 1734.02s`.

An earlier run of that same command exited `1` with 2 failures and 12 errors, all in `tests/test_social_cards.py` and `tests/test_landing.py`, because `CI=true` and `web/node_modules` and `web/dist` were absent. Those tests do not import the CLI change. After the web install and build, `tests/test_landing.py::test_landing_behaviour_in_browser` passed (`12 passed`) and the full command above exited 0.

MCP:

```bash
cd mcp && /Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm ci && /Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm test
```

Exit code: `0`. Vitest 5.0.1, `7` files, `134` tests passed.

`python -m pipeline.agent_copy check` exited 0 after the bundle was regenerated for `cli_version` 1.0.0.

The full pytest run finished before one sentence in `docs/cli-contract.md` was shortened so it no longer says `explanation.fetch` is always present. That sentence is in `2970caf2`. It does not change code.

## Not observed

No call to the live `api.modelspec.dev`. The CLI test uses a mock. It does not measure a production Worker body. No PyPI publish, no tag, no merge, and no Linear write. `compare` was not changed. Its existing tests passed inside the full suite.
