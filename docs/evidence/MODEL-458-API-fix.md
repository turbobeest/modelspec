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
| AUD-02-F1 | OpenAPI states the rank, policy, and decide ranges the Worker returns. Rank and policy envelopes are 2.0. Round 1 set the decision contract to 3.0. Round 2 sets it to 2.20. Bounded stays 1.5. Named comparison stays 1.1. | `13c2d0bf8295d3070103d8124605a5101faa2857` |

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

- Decision `CONTRACT_VERSION` 2.19 → 3.0 in round 1. The decide HTTP refusal code enum gains `invalid_request`. Decide malformed JSON stays `invalid_request`. Round 2 sets `CONTRACT_VERSION` to 2.20. The 3.0 figure in this section is that round-1 bump.
- Rank and policy `SCHEMA_VERSION` 1.0 → 2.0 together. They share one OpenAPI `info.version`.
- `BOUNDED_VERSION` stays 1.5. `MODEL_COMPARISON_VERSION` stays 1.1. Feedback schema stays 1.0. Catalogue and CLI export schema versions stay as they were.

## Companion files

Regenerated with the repo generators, not by hand:

- `api/worker/openapi.yaml` via `python api/worker/openapi.py`.
- `docs/decision-contract.schema.json` and `mcp/src/contract-version.ts` via `python -m decision.schema`.
- `cli/modelspec/agent-bundle.json` source digest for that schema, via `python -m pipeline.agent_copy write`. The other artifacts that command writes were already current. `python -m pipeline.agent_copy check` exited 0.
- Decide page fixtures, via `MODELSPEC_WRITE_FIXTURES=1 pytest tests/test_decide_page_fixtures.py`. Round 1 set each file's `contract_version` to 3.0. Round 2 sets those pins to 2.20. The v1 rank golden's envelope `schema_version` is 2.0. `qa/fixtures/mcp-tools.json` was regenerated with `python -m qa.contracts`.

Existing tests and fixtures updated because the versions moved: decision suites that pin `contract_version`, `mcp/test/contract-version.test.ts`, `mcp/test/fixtures/decide-budget.json` (`projects_contract` 3.0 in round 1, 2.20 after round 2, `bounded_version` still 1.5), `web/src/decide/adapter/contract.ts` (round 1 added 3.0 and kept 2.19; round 2 adds 2.20 and removes 3.0), `web/src/decide/__tests__/contract.test.ts`, and the health `schema_version` assert. Round 1's floor scanner skipped every `SCHEMA_VERSION` assignment. Round 2 skips only a quoted dotted version. Docs that state the current envelope were updated. Historical changelog rows and saved 2.19 web fixtures stay.

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

## Round 2

The decision contract as built is 2.20. Rank and policy envelopes stay at `schema_version` 2.0. Bounded stays 1.5. Named comparison stays 1.1. Catalogue and CLI export schema stay 3.0. Card schema stays 3.0. The 3.0 sentences in the sections above are the round-1 bump.

### A1. Merge origin/main

Commit `531e418ca3e4ff88c3aaae89f61097528ad7cd3c`. Merged `origin/main` `4c59989970e01bbb318fbd1f05c58323682053f6` into `fd14f3c5fafee3b04e179e591c67a445acb9301e`. The only conflict was `tests/test_decision_relax.py`. The resolution keeps this branch's contract pin and every test added on main. No conflict markers remain.

Focused serial tests on that merge, before the version edit: exit 1, 1 failed, 890 passed, 3 skipped, 51.77s. The failure was `tests/test_decision_numeric_bounds.py::test_contract_version_stays_current` (`assert '3.0' == '2.19'`). A2 changes that pin.

### A2. Decision contract 2.20

Commit `5010c98f295e94141ee91d2e75441baf29ed1f1d`.

`CONTRACT_VERSION` is `"2.20"`. The changelog in `docs/decision-contract.md` says the published HTTP refusal codes for decide now list `invalid_request`, which the service already returned. The decision shape and every declared range are unchanged, so this is not a major. Rank `SCHEMA_VERSION` and policy `SCHEMA_VERSION` stay `"2.0"`. `BOUNDED_VERSION` stays 1.5. `MODEL_COMPARISON_VERSION` stays 1.1.

`web/src/decide/adapter/contract.ts` adds `"2.20"` to the closed version list, keeps every older value, and removes `"3.0"`.

Companions were regenerated by their generators. `docs/decision-contract.schema.json` and `mcp/src/contract-version.ts` came from `python -m decision.schema`. `api/worker/openapi.yaml` came from `python api/worker/openapi.py`. The CLI bundle digest came from `python -m pipeline.agent_copy write`. Decide page fixtures came from `MODELSPEC_WRITE_FIXTURES=1` on `tests/test_decide_page_fixtures.py` (13 passed). `qa/fixtures/mcp-tools.json` came from `python -m qa.contracts`. After those writes, `python -m decision.schema --check`, `python api/worker/openapi.py --check`, and `python -m pipeline.agent_copy check` exited 0.

One expected string in `tests/test_api_docs.py` named `contract_version 3.0` inside a longer sentence, so a quoted replace missed it. It now says `contract_version 2.20`. That test: 1 passed in 0.62s.

Version-touched pytest before that string fix, 24 files through `~/.codex-g2/heavy.sh`: exit 1, 1 failed, 1295 passed, 3 skipped, 85.48s. The failure was `tests/test_api_docs.py::test_decide_response_description_uses_the_bounded_version`.

Decide page, on the final tree:

```bash
(cd web && env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH node node_modules/vitest/vitest.mjs run src/decide/__tests__ --maxWorkers=1)
```

Exit 0. 59 files passed, 1 file skipped, 887 tests, 70.06s.

MCP contract test, on the final tree:

```bash
(cd mcp && env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH node node_modules/vitest/vitest.mjs run test/contract-version.test.ts)
```

Exit 0. 1 file, 2 tests, 205ms.

`git grep` uses a regular expression, so `.` matches any character. The pattern `"3.0"` also matches `"300"`, `"320"`, and `"390"`.

```bash
git grep -n '"3.0"'
```

Exit 0. 74 lines. None are a decision-contract `contract_version` or `CONTRACT_VERSION`. Export schema `"3.0"`, card schema `"3.0"`, and the regex false positives stay. Full output:

```text
.github/scripts/check_policy_response.py:35:EXPORT_SCHEMA_VERSION = "3.0"
.github/scripts/check_rank_response.py:39:EXPORT_SCHEMA_VERSION = "3.0"
api/worker/openapi.py:396:            "export_schema_version": "3.0",
api/worker/wrangler.jsonc:104:    "VISIT_DECIDE_DAY_LIMIT": "300",
api/worker/wrangler.jsonc:212:        "VISIT_DECIDE_DAY_LIMIT": "300",
benchmarks/superglue_rte.md:39:    the Hugging Face counts and treats Table 1's "300" test figure as unresolved typesetting. Official
benchmarks/superglue_rte.md:145:Hugging Face `aps/super_glue` config `rte` has 2,490 / 277 / 3,000 rows for train / validation / test. SuperGLUE Table 1 prints 2,500 / 278 / 300. The 3,000-row test split matches GLUE RTE; Table 1's "300" is treated here as an unresolved mismatch, not as a third split. The card licence is "other", with SuperGLUE pointing at the original RTE licences. Test labels are hidden for official scoring. Common LLM harnesses use the public 277-row validation set.
brand/2a/modelspec-lockup-dark.svg:20:  <text x="50" y="31.5" font-family="'Segoe UI Variable Display','Segoe UI',system-ui,sans-serif" font-size="20" letter-spacing="-0.4" fill="#F3F2F1"><tspan font-weight="600">Model</tspan><tspan font-weight="300">Spec</tspan></text>
brand/2a/modelspec-lockup-light.svg:20:  <text x="50" y="31.5" font-family="'Segoe UI Variable Display','Segoe UI',system-ui,sans-serif" font-size="20" letter-spacing="-0.4" fill="#201F1E"><tspan font-weight="600">Model</tspan><tspan font-weight="300">Spec</tspan></text>
brand/social/instagram-avatar.svg:1:<svg xmlns="http://www.w3.org/2000/svg" width="320" height="320" viewBox="0 0 40 40">
cli/modelspec/snapshot.py:92:EXPORT_SCHEMA_VERSION = "3.0"
docs/api-policy-check.md:95:    "export_schema_version": "3.0"
docs/api.md:73:    "export_schema_version": "3.0"
docs/design/class-and-null-semantics.md:212:| `pipeline/export.py::EXPORT_SCHEMA_VERSION` | `"2.0"` | **`"3.0"`** | `model_type`'s published range widens |
docs/design/class-and-null-semantics.md:213:| `cli/modelspec/snapshot.py::EXPORT_SCHEMA_VERSION` | `"2.0"` | **`"3.0"`** | must equal the producer; `tests/test_export.py` holds them equal |
docs/design/class-and-null-semantics.md:214:| `.github/scripts/check_*_response.py::EXPORT_SCHEMA_VERSION` | `"2.0"` | **`"3.0"`** | the live smoke checks assert the deployed tree's version |
docs/design/class-selection.md:400:  "build": { "commit": "…", "export_schema_version": "3.0" },
docs/evidence/g2-ios/MODEL-225-build.txt:161: "export_schema_version": "3.0",
docs/evidence/g2-ios/MODEL-261-site-build.txt:351: "export_schema_version": "3.0",
docs/evidence/g2-ios/MODEL-404/routing/ci-sitemap-red.txt:14:        (real / "api/build.json").write_text('{"built_at":"2026-10-17","export_schema_version":"3.0"}')
docs/evidence/g2-ios/MODEL-404/routing/ci-sitemap-red.txt:71:        (real / "api/build.json").write_text('{"built_at":"2026-10-17","export_schema_version":"3.0"}')
docs/evidence/g2-ios/MODEL-404/routing/final-artifact-audit.json:8:    "export_schema_version": "3.0"
docs/evidence/g2-ios/MODEL-404/routing/late-artifact-audit.json:8:    "export_schema_version": "3.0"
docs/evidence/g2-ios/MODEL-404/routing/merge-use-case-red.txt:16:            "export_schema_version": "3.0", "built_at": "2026-10-17T00:00:00Z",
docs/evidence/g2-ios/MODEL-404/routing/merge-use-case-red.txt:78:            "export_schema_version": "3.0", "built_at": "2026-10-17T00:00:00Z",
docs/evidence/g2-ios/MODEL-404/routing/merge-use-case-red.txt:140:            "export_schema_version": "3.0", "built_at": "2026-10-17T00:00:00Z",
docs/evidence/g2-ios/MODEL-404/routing/red.txt:16:        (real / "api/build.json").write_text('{"built_at":"2026-10-17","export_schema_version":"3.0"}')
docs/evidence/g2-ios/MODEL-orchestrator-recipe-r2/worker-dry-run.txt:342:env.VISIT_DECIDE_DAY_LIMIT ("300")                                                 Environment Variable      
docs/evidence/g2-ios/MODEL-orchestrator-recipe/red.txt:112: "export_schema_version": "3.0",
docs/evidence/g2-ios/MODEL-orchestrator-recipe/site-build-final.txt:159: "export_schema_version": "3.0",
docs/evidence/g2-ios/MODEL-orchestrator-recipe/site-build.txt:159: "export_schema_version": "3.0",
docs/history/offline-cli-contract.md:520:`build.export_schema_version` `"3.0"`. A snapshot from before this field has no
docs/model-card-template-v3.md:1023:card_schema_version: "3.0"
docs/policy-check-api.md:373:"build":        { "commit": "…", "built_at": "…", "export_schema_version": "3.0" },
docs/rank-api.md:134:`build.export_schema_version` (`"3.0"`, `pipeline/export.py`), plus
docs/rank-api.md:141:  "build": { "commit": "b1cb67d…", "built_at": "…", "export_schema_version": "3.0" },
docs/rank-api.md:254:`"3.0"`.
pipeline/export.py:56:EXPORT_SCHEMA_VERSION = "3.0"
pipeline/feedback_assets/feedback.js:74:    var trying = el("input", { type: "text", maxlength: "300", "aria-describedby": id + "-privacy" });
pipeline/method.py:84:            '<rect width="772" height="420" rx="6"/><line class="axis-y" x1="150" y1="24" x2="150" y2="370"/>'
pipeline/method.py:85:            '<line class="axis-x" x1="150" y1="370" x2="752" y2="370"/>'
release_signals/pipeline.py:672:        "card_schema_version": "3.0",
schema/card.py:854:    card_schema_version: str = "3.0"
scripts/card_confirmed_leaderboard_gaps.py:424:        card_schema_version="3.0",
scripts/seed_huggingface.py:567:        card_schema_version="3.0",
scripts/seed_huggingface.py:931:        card_schema_version="3.0",
scripts/seed_models_dev.py:776:        card_schema_version="3.0",
tests/fixtures/blog/posts/2026-09-26-alpha/r1/charts/claims.svg:10:<rect class="f-s1" x="320" y="38" width="10" height="10" rx="2"/><text x="336" y="47">Independent reading</text>
tests/fixtures/decision/v1-rank.json:22:      "export_schema_version": "3.0"
tests/test_blog_deployment.py:53:                "export_schema_version": "3.0",
tests/test_ci_workflows.py:951:        "build": {"commit": "abc", "export_schema_version": "3.0"},
tests/test_ci_workflows.py:1064:    path.write_text('{"build": {"commit": "abc", "export_schema_version": "3.0"},'
tests/test_cite_only_exports.py:62:    assert result["build"]["export_schema_version"] == "3.0"
tests/test_class_and_null_semantics.py:250:    assert EXPORT_SCHEMA_VERSION == "3.0", "decision-model widens a published enum"
tests/test_class_and_null_semantics.py:262:        snapshot._require_compatible_export_schema("3.0")
tests/test_class_and_null_semantics.py:263:    assert "3.0" in str(exc.value)
tests/test_class_fit.py:426:        {"commit": "abc", "export_schema_version": "3.0"},
tests/test_class_fit.py:446:        {"commit": "abc", "export_schema_version": "3.0"}, model_type_counts={})
tests/test_class_fit.py:458:        {"commit": "abc", "export_schema_version": "3.0"},
tests/test_data_trust.py:441:        "card_schema_version": "3.0",
tests/test_decide_preview_workflow.py:43:        'dist/modelspec/api/build.json': b'{"built_at":"2026-09-29T00:00:00+00:00","export_schema_version":"3.0"}',
tests/test_decision_cli.py:145:            "index": {"build": {"commit": "abc123", "export_schema_version": "3.0"}},
tests/test_decision_compatibility.py:64:        "export_schema_version": "3.0",
tests/test_export.py:37:    assert EXPORT_SCHEMA_VERSION == "3.0"
tests/test_live_use_cases.py:43:        "export_schema_version": "3.0", "built_at": "2026-10-17T00:00:00Z",
tests/test_policy_check.py:60:         "eligibility_as_of": "2026-09-01", "export_schema_version": "3.0"}
tests/test_policy_check.py:624:    assert body["build"]["export_schema_version"] == "3.0"
tests/test_rank_worker.py:370:    export = {"build": {"commit": "abc", "export_schema_version": "3.0"},
tests/test_simple_decide_routes.py:22:    (real / "api/build.json").write_text('{"built_at":"2026-10-17","export_schema_version":"3.0"}')
tests/test_social_cards.py:549:    assert set(checks) == {"390", "1440"}
tests/test_structured_data.py:23:        {"built_at": "2026-09-29T19:11:08+00:00", "export_schema_version": "3.0"}))
tests/test_structured_data.py:99:    assert dataset["version"] == "3.0"
tests/test_withdrawn_routes.py:67:        "export_schema_version": "3.0", "built_at": "2026-10-02T00:20:00Z",
tests/test_x402.py:1011:        "VISIT_DECIDE_DAY_LIMIT": "300",
```

```bash
git grep -n "'3.0'"
```

Exit 0. 1,373 lines. 1,372 lines are `card_schema_version: '3.0'` under `models/`. The other line is historical evidence, not a live decision-contract pin:

```text
docs/evidence/g2-ios/MODEL-364-fix.md:233:`Input should be '3.0'` for the fixture's `2.16`. Green exit 0: 70 passed in
```

No line in either output contains `contract_version`, `CONTRACT_VERSION`, or `projects_contract`. The double-quote hit in `tests/test_class_and_null_semantics.py` is the export-schema guard, and its message text contains the word `decision-model`.

### A3. Floor-version skip

Commit `5a38258b2672868c628f1d0af69c1209ca1e89e0`. `tests/test_rank_worker.py::test_no_floor_is_written_down_a_second_time` skips a line only when it assigns `SCHEMA_VERSION` and the stripped right-hand side is exactly one quoted dotted version. Any other line, including a `SCHEMA_VERSION =` line whose value is a number, is scanned. No floor changed. `api/ranking/engine.py` was not edited.

Temporary edits were added after `SCHEMA_VERSION = "2.0"` in `api/worker/src/rank_service.py`, then both that file and the test were restored to the committed bytes (`cmp` matched, and `git diff` on those paths was empty).

`SCHEMA_VERSION = 3`, with the round-2 guard:

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rank_worker.py::test_no_floor_is_written_down_a_second_time
```

Exit 0. 1 passed in 0.21s. The integer 3 is not a ranking floor, and the scanner matches only a dotted literal, so this line does not fail the test.

`SCHEMA_VERSION = 2.0` on that same line, a floor written as a number: exit 1, 1 failed in 0.26s.

```text
AssertionError: rank_service.py: 'SCHEMA_VERSION = 2.0' writes a ranking floor down again; import it from api.ranking.engine instead
assert 2.0 not in {0.25, 0.5, 2.0}
```

That same `SCHEMA_VERSION = 2.0` line with the round-1 skip restored (`if re.search(r"\bSCHEMA_VERSION\s*=", code): continue`): exit 0, 1 passed in 0.22s.

### A4. Budget caps kept

Caps stay at 240,000 bytes, 60,000 tokens, and 9,800 MCP first-turn tokens. Nothing was raised.

Token method in this environment is `ceil(characters / 4)` from `pipeline.agent_overhead.tokens`. Tiktoken is not installed. The same function backs `tests/test_agent_guide.py`.

Before the A5 sentence, `api/worker/openapi.yaml` was 239,361 bytes and 59,837 tokens. Headroom was 639 bytes and 163 tokens.

After A5 the file is 239,407 bytes (headroom 593) and 59,848 tokens (headroom 152). The growth is 46 bytes and 11 tokens: the longer 503 description, once.

MCP first turn, `python -m qa.agent_harness --first-turn-breakdown`, same method, no network call:

| family | tokens | headroom under 9,800 | wire bytes |
| --- | --- | --- | --- |
| claude | 9,484 | 316 | 37,943 |
| openai | 9,576 | 224 | 38,313 |
| gemini | 9,679 | 121 | 38,725 |

All three are under the cap.

### A5. Feedback storage wording

Commit `73b675ff1d7e7b503e337ff0c247273112c63172`. `docs/feedback-api.md` and the OpenAPI description of the 503 `feedback_store_unavailable` response say the code is returned when storage is not configured or when a storage read or delete fails. The OpenAPI text comes from `ERRORS` in `api/worker/src/feedback_service.py` through `python api/worker/openapi.py`. `qa/fixtures/mcp-tools.json` was regenerated with `python -m qa.contracts`. Runtime `error()` messages were not changed.

On the final tree, `python api/worker/openapi.py --check` exited 0, `python -m qa.contracts` exited 0, and `python -m pipeline.agent_copy check` exited 0.

`tests/test_feedback.py`, `tests/test_api_docs.py`, and `tests/test_agent_guide.py`: exit 0, 281 passed, 2 skipped, 14.95s.

### Focused tests on the final tree

```bash
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rank_worker.py tests/test_decide_worker.py tests/test_feedback.py tests/test_keyed_router_worker.py tests/test_decision_contract.py tests/test_decision_link.py tests/test_decide_bounded.py tests/test_api_docs.py tests/test_snapshot_successor.py tests/test_decision_relax.py tests/test_decision_numeric_bounds.py tests/test_agent_guide.py
```

Exit 0. 891 passed, 3 skipped, 55.25s.

No new test module, so `tests/shard_durations.json` is unchanged. The 120 MiB, 115 MiB, and 100 ms gates are unchanged. No ranking floor, Worker var, tier, legal text, or `FEEDBACK` KV binding changed. The memory probe was not run. This round does not change Worker-exported snapshot fields, rank rows, or the engine import graph.

