# MODEL-458-API execution evidence

Work started at `8f9b242aa2c4674bc8dc8d8dbb30c26ae76265db`. Before this note, the five implementation commits were rebased onto `origin/main` `b8931c6101ee0e22acd6cc6627818ad392320212`. Those two later main commits do not touch the files in this branch.

Final implementation SHA: `13c2d0bf8295d3070103d8124605a5101faa2857`.
The evidence commit is the branch HEAD. Identify it with `git log -1 --format=%H -- docs/evidence/MODEL-458-API-fix.md`.

| Finding | Enforced behaviour | Commit |
| --- | --- | --- |
| AUD-02-F2 | A non-string `access.kind` is `invalid_spec` with an access issue and recovery. Registered kinds and an unknown string keep the current form. | `d808b0a32b44854c5d4dc76cacb4a67c78c5aa7c` |
| AUD-02-F3 | A rank constraint that is not a finite number is `invalid_request` naming that field. Zero, one, and ordinary finite values keep their current meaning. | `496d4dbf2c8f66f8663d6ac1172d36c0afabcb17` |
| AUD-02-F5 | Replay drops `router_config` with the other HTTP controls before rebuilding the spec. The signed inputs still drive the service decision. | `ee2d7e8b229d139385503bf880cf7b6193205861` |
| AUD-02-F4 | A feedback store read failure on submit or withdrawal, and a delete failure on withdrawal, return HTTP 503 `feedback_store_unavailable`. Counter writes stay best-effort. | `081970350afdc98667aed761f0e0c5d7d5a01edb` |
| AUD-02-F1 | OpenAPI states the rank, policy, and decide ranges the Worker returns. Rank and policy envelopes are 2.0. The decision contract is 3.0. Bounded stays 1.5. Named comparison stays 1.1. | `13c2d0bf8295d3070103d8124605a5101faa2857` |

Each finding had a permanent regression that failed before its fix and passed after. Counts below are from those runs. Detailed local notes for AUD-02-F2 and AUD-02-F3 stay in `/tmp/MODEL-458-API-scratch/`.

| Finding | Red | Green |
| --- | --- | --- |
| AUD-02-F2 | `tests/test_decision_contract.py` and `tests/test_decide_worker.py` focused cases: 6 failed, exit 1, 1.22s. | Same cases: 7 passed, 0.76s. Both files: 322 passed, 1 skipped, exit 0, 23.66s. |
| AUD-02-F3 | `tests/test_rank_worker.py` new cases: 9 failed, 7 passed, exit 1, 0.73s. | New cases: 16 passed, 0.67s. Full `tests/test_rank_worker.py`: 65 passed, 9.85s. Focused rank routing in `tests/test_access_wiring.py`: 60 passed, 0.53s. |
| AUD-02-F5 | `tests/test_decision_link.py` and `tests/test_keyed_router_worker.py`: 2 failed, 0.87s. | Both files: 83 passed, 1.92s. After the 3.0 contract bump, the same files plus the two version asserts: 50 passed, 1.61s. Link hashes held. |
| AUD-02-F4 | `tests/test_feedback.py`: 3 failed, 0.47s. | `tests/test_feedback.py`: 75 passed, 1.15s. `tests/test_api_docs.py` at that commit: 56 passed, 2 skipped, 5.56s. `python api/worker/openapi.py --check` passed. |
| AUD-02-F1 | Filtered `tests/test_api_docs.py`: 85 failed, 47 passed, 57 deselected, exit 1, 7.93s. | Full `tests/test_api_docs.py` plus two rank asserts: 189 passed, 2 skipped, 10.37s. `tests/test_policy_check.py`: 73 passed, 7.30s. `tests/test_rank_worker.py` after the envelope bump: 65 passed, 8.53s. |

AUD-02-F1 also updated version consumers that follow the decision contract. `web` vitest: 62 files passed, 1 skipped, 927 tests, 18.97s. `web` `npm run build` (`tsc -b && vite build`) exited 0. `mcp` vitest: 12 files, 363 tests, 1.80s. Both Node suites need the repo virtualenv on `PATH`; the system `python3` is 3.9 and cannot import this tree. `python api/worker/openapi.py --check` and `python -m decision.schema --check` exited 0 after the generator edits.

Two rank use cases answer 422. The conformance test accepts 200 or 422 and checks the body against that status schema. `/v1/health` echoes the rank envelope version, so its `schema_version` is 2.0. The CLI envelope stays 1.0.

## Versions

- Decision `CONTRACT_VERSION` 2.19 → 3.0. The decide HTTP refusal code enum gains `invalid_request`. Decide malformed JSON stays `invalid_request`.
- Rank and policy `SCHEMA_VERSION` 1.0 → 2.0 together. They share one OpenAPI `info.version`.
- `BOUNDED_VERSION` stays 1.5. `MODEL_COMPARISON_VERSION` stays 1.1. Feedback schema stays 1.0. Catalogue and CLI export schema versions stay as they were.

## Companion files

Regenerated with the repo generators, not by hand:

- `api/worker/openapi.yaml` via `python api/worker/openapi.py`.
- `docs/decision-contract.schema.json` and `mcp/src/contract-version.ts` via `python -m decision.schema`.
- `cli/modelspec/agent-bundle.json` source digest for that schema, via `python -m pipeline.agent_copy write`. The other artifacts that command writes were already current. `python -m pipeline.agent_copy check` exited 0.
- Decide page fixtures, via `MODELSPEC_WRITE_FIXTURES=1 pytest tests/test_decide_page_fixtures.py`. Each file's `contract_version` is 3.0. The v1 rank golden's envelope `schema_version` is 2.0. `qa/fixtures/mcp-tools.json` was regenerated with `python -m qa.contracts`.

Existing tests and fixtures updated because the versions moved: decision suites that pin `contract_version`, `mcp/test/contract-version.test.ts`, `mcp/test/fixtures/decide-budget.json` (`projects_contract` 3.0, `bounded_version` still 1.5), `web/src/decide/adapter/contract.ts` (adds 3.0 and keeps 2.19), `web/src/decide/__tests__/contract.test.ts`, and the health `schema_version` assert. The floor scanner skips `SCHEMA_VERSION` assignments so the envelope major is not read as a ranking floor. Docs that state the current envelope were updated. Historical changelog rows and saved 2.19 web fixtures stay.

## Memory probe

Not run. The diff does not change Worker-exported snapshot fields, rank rows, or the engine import graph. `openapi.py` is not in the Worker bundle. `import math` in `rank_service.py` is the standard library inside a module the Worker already loads. The 120 MiB, 115 MiB, and 100 ms gates are unchanged.

## Commands

Post-fix checks, from the worktree root unless noted. Exit codes were checked directly. The AUD-02-F3 rank-routing subset (60 passed, 0.53s) is the count in the table; its filter is not repeated here.

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_contract.py tests/test_decide_worker.py
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rank_worker.py
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_link.py tests/test_keyed_router_worker.py
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_feedback.py
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_api_docs.py
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_policy_check.py
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m decision.schema --check
bash -lc 'cd web && PATH="/Users/terbeest/dev/modelspec/.venv/bin:$PATH" npm test'
bash -lc 'cd web && PATH="/Users/terbeest/dev/modelspec/.venv/bin:$PATH" ~/.codex-g2/heavy.sh npm run build'
bash -lc 'cd mcp && PATH="/Users/terbeest/dev/modelspec/.venv/bin:$PATH" npm test'
```

`npm ci` for `web` and `mcp` ran through `~/.codex-g2/heavy.sh` before those tests. `node_modules` is not committed.

Tool versions: Python 3.14.4, pytest 9.1.1, Node v22.23.1, npm 10.9.8, Git 2.50.1, GitHub CLI 2.103.3.

## Not observed

No live client payload. No production deploy. No private-data memory measurement. No change to ranking floors, neutrality text, `docs/legal/`, Worker vars, prices, plans, or frozen public data.
