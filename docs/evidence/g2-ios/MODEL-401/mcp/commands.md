# MODEL-401 MCP verification

Working directory: `/Users/terbeest/dev/worktrees/model-401` unless noted.
Design-only first commit supplied by executor: `03006c66`.
Tool versions: Node `v22.22.3`, npm `10.9.8`, Python `3.14.4`, Vitest `5.0.1`.

## Shared fixture method

`mcp/test/fixtures/generate-hardware-fit.py` calls the real Python checker using verified fixture snapshots. It writes complete `full` and `lower_bound` responses to `hardware-fit.json`. The lower-bound fixture uses 65.5e9 weight bytes, sourced 32e9 capacity bytes, and no runtime headroom. These fixture snapshots use the snapshot builder's record verification, without an HMAC signature. Signature round trips have separate tests.

`test_mcp_hardware_fit_fixture_matches_current_api_assessments` reconstructs both requests and verified snapshots, then checks the complete generated response bodies against the current checker. Node imports that JSON, forwards each response through the real MCP handler with a mocked origin, and compares the complete result. Literal version, verdict, byte-count, headroom marker and no-`fits` assertions remain. No assertion was skipped or removed. No test calls a live API, device, or paid provider.

Generate the shared fixture, exit 0, output in `fixture-generate.log`:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python mcp/test/fixtures/generate-hardware-fit.py > docs/evidence/g2-ios/MODEL-401/mcp/fixture-generate.log 2>&1
```

Check the fixture against the current checker, exit 0, one test passed in `fixture-parity.log`:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_hardware_fit.py::test_mcp_hardware_fit_fixture_matches_current_api_assessments > docs/evidence/g2-ios/MODEL-401/mcp/fixture-parity.log 2>&1
```

## CI failure and reproduction

PR #812's MCP job has Node and standard-library Python but does not install Python application dependencies. The initial Node parity test spawned Python and imported the checker, so CI failed with missing pydantic. Local validation had supplied the application's shared Python environment and did not expose that dependency.

The local `stdlib-python/python3` wrapper invokes `/opt/homebrew/bin/python3 -S`, Python 3.14.4 without site packages. Both pydantic and yaml are absent. Running the initial subprocess test variant with this interpreter and no `PYTHON` environment variable failed with missing yaml before it reached the pydantic import. `ci-stdlib-red.log` records two failed and 35 passed, exit 1. The temporary old source was restored immediately afterward.

The focused command, run from `mcp/` against that initial subprocess variant, was:

```sh
env -u PYTHON PATH=/Users/terbeest/dev/worktrees/model-401/docs/evidence/g2-ios/MODEL-401/mcp/stdlib-python:/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test -- --run test/hardware-fit.test.ts > ../docs/evidence/g2-ios/MODEL-401/mcp/ci-stdlib-red.log 2>&1
```

An earlier local probe used `/usr/bin/python3 -S`, which is Python 3.9.6 here. Its focused failure was unsupported Python syntax, and its full-suite failure came from existing vocabulary code requiring newer Python. Those exploratory outputs remain in `ci-python39-red.log` and `ci-python39-suite.log`. They are separate from the final CI reproduction and final green evidence.

## Final verification

Full MCP suite from `mcp/`, with modern standard-library Python and no `PYTHON` override, exit 0. `ci-stdlib-green.log` records all 203 tests passing across 10 files:

```sh
env -u PYTHON PATH=/Users/terbeest/dev/worktrees/model-401/docs/evidence/g2-ios/MODEL-401/mcp/stdlib-python:/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test > ../docs/evidence/g2-ios/MODEL-401/mcp/ci-stdlib-green.log 2>&1
```

TypeScript check from `mcp/` with the same environment, exit 0, in `ci-typecheck.log`:

```sh
env -u PYTHON PATH=/Users/terbeest/dev/worktrees/model-401/docs/evidence/g2-ios/MODEL-401/mcp/stdlib-python:/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm run typecheck > ../docs/evidence/g2-ios/MODEL-401/mcp/ci-typecheck.log 2>&1
```

## Original contract red and generation

The original red ran against unchanged Python implementation and descriptions, exit 1, three failed and 34 passed in `red.log`. The description lacked basis guidance; full output was hardware-fit 1.0 without basis; the lower-bound output was undetermined with version 1.0. From `mcp/`:

```sh
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHON=/Users/terbeest/dev/modelspec/.venv/bin/python npm test -- --run test/hardware-fit.test.ts > ../docs/evidence/g2-ios/MODEL-401/mcp/red.log 2>&1
```

`npm ci` completed with exit 0, recorded in `npm-ci.log`. Before dependency installation, one attempted test command exited 127 because vitest was absent; no test ran in that attempt. The installation reported eight high severity dependency vulnerabilities. Package versions remain unchanged.

The agent-copy generator completed with exit 0 and refreshed the MCP description and CLI source hash. `agent-copy-write.log` includes existing unregistered hardware source URL notices and all configured artifact writes:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write > docs/evidence/g2-ios/MODEL-401/mcp/agent-copy-write.log 2>&1
```

The description uses 650 characters, or 163 planning tokens, within its 1,500-token allowance.
