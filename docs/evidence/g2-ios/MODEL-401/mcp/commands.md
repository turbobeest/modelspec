# MODEL-401 MCP verification

Working directory: `/Users/terbeest/dev/worktrees/model-401` unless noted.
Design-only first commit supplied by executor: `03006c66`.

Environment versions: Node `v22.22.3`; Python `3.14.4`; Vitest `5.0.1`.

1. From `mcp/`, dependency installation (exit 0):
   `env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHON=/Users/terbeest/dev/modelspec/.venv/bin/python npm ci > ../docs/evidence/g2-ios/MODEL-401/mcp/npm-ci.log 2>&1`
2. From `mcp/`, red against unchanged Python implementation and descriptions (exit 1):
   `env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHON=/Users/terbeest/dev/modelspec/.venv/bin/python npm test -- --run test/hardware-fit.test.ts > ../docs/evidence/g2-ios/MODEL-401/mcp/red.log 2>&1`
   Output: 3 failed, 34 passed. The description lacked basis guidance. Full Python output was hardware-fit 1.0 without basis. Lower-bound Python output was undetermined, also version 1.0.
   Before dependency installation an initial attempt exited 127 because vitest was absent. No test ran in that attempt.
3. Regenerate published agent copy and CLI bundle (exit 0):
   `env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write > docs/evidence/g2-ios/MODEL-401/mcp/agent-copy-write.log 2>&1`

The parity test calls the local Python checker against signed fixture snapshots. It performs no live API request, device execution, or paid-provider call. MCP receives the real Python assessment through a mocked origin binding, and the test compares its complete response body with the API result.

4. From `mcp/`, TypeScript check (exit 0):
   `env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHON=/Users/terbeest/dev/modelspec/.venv/bin/python npm run typecheck > ../docs/evidence/g2-ios/MODEL-401/mcp/typecheck.log 2>&1`
5. From `mcp/`, full MCP suite after Python implementation and copy generation (exit 0):
   `env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHON=/Users/terbeest/dev/modelspec/.venv/bin/python npm test > ../docs/evidence/g2-ios/MODEL-401/mcp/green.log 2>&1`
   Output: 10 test files passed; 203 tests passed, including both actual Python API parity variants and the description budget check.

The generator logged existing unregistered hardware source URLs, then wrote all configured generated artifacts. It completed with exit 0. Dependency installation reported 8 high severity dependency vulnerabilities. This task did not change package versions or run an audit remediation.
