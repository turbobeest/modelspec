# MODEL-209: sourced offering identifiers

The REVIEW-718 fixes passed the full Python, web, and MCP suites, each
with exit 0. Python passed 10,044 tests, web passed 813, and MCP passed 136.
The review-fix section below records the new red/green tests and delivery
checks. The original implementation evidence is retained before that section.

- Base SHA: `2b0770afab18d101ea033c9259d53ae4ac42e2ce`.
- Initial implementation: `add83fb9ee8c3fe179f9a24c57db9f17e59d9668`.
- Initial tested implementation: `63a48b01e2bb0ead5de048ca9c16ba0d5522b56a`.
- Review-fix tested implementation: `a442167af362991194da273a2f70898116607f36`.
- Worktree: `/Users/terbeest/dev/worktrees/model-209`.
- Branch: `sparksandsawdust/model-209-api-model-id`.
- Final delivery SHA: resolve the commit containing this evidence after
  delivery with the command below. The evidence cannot contain its own
  literal commit hash.

```sh
git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-209-fix.md
```

## Result

`offering.api_model_id` and the separate `offering.router_slug` are sourced
offering facts. Existing card availability IDs become unverified candidates.
The snapshot admits values only through the existing two-key and source
guards. Explicit sourced offering facts take precedence over card candidates.

Contract 2.17 adds optional `OfferingRef.api_model_id` and `router_slug`.
Missing identifiers are omitted from offering references. Full decisions show
known identifiers in `top[].facts` with `record_id` and `source_ids`.
LiteLLM output uses the provider ID. OpenRouter output uses the separate slug.
A missing ID keeps its `<...>` placeholder and a reason naming the missing
verified fact. The generic JSON format includes the null ID, placeholder, and
reason per route. The decide page accepts the new fields and version.

## Red-first evidence

The executor added these tests before their corresponding implementation.
Red outputs are excerpts from retained local logs under `tmp/model-209`.

| Defect and red-first test | Red output | Green output |
|---|---|---|
| The snapshot had no identifier facts, so verified provider IDs could not reach router output. `test_verified_ids_are_emitted_and_router_slugs_stay_separate` also checks full-decision provenance. | `SnapshotBuildError: facet 'offering.api_model_id' is not registered`. The three router tests below reported `19 deselected, 3 errors in 12.49s`, exit 1. | Identifier selection: `4 passed, 103 deselected in 1.93s`, exit 0. Final focused suite: `492 passed, 4 skipped in 56.26s`, exit 0. |
| Unverified and null identifiers need placeholders and reasons. `test_unverified_or_null_ids_keep_placeholders_with_reasons`. | The same missing-facet error prevented the fixture from compiling, exit 1. | Included in the successful identifier selection and focused suite above. It checks all three router formats and rejects the unverified strings. |
| A provider ID must not fill an absent router slug. `test_provider_id_cannot_fill_an_unknown_router_slug`. | The same missing-facet error, exit 1. | Included in the successful identifier selection and focused suite above. |
| Card availability IDs were not collected. `test_card_identifier_candidates_need_sourced_verification_before_admission`. | `KeyError: 'offering.api_model_id'`; `1 failed, 84 deselected in 0.67s`, exit 1. Provider alias cases `typesafe-TypeSafe AI` and `zai-Z.ai` later reproduced the same error: `2 failed, 1 passed, 94 deselected in 0.58s`, exit 1. | The original selection passed above. All three provider cases pass in the final focused suite. The test also checks that unsourced candidates stay unknown and that explicit verified facts win. |
| Normalized string comparison admitted changed case or punctuation. `test_offering_identifiers_require_literal_source_values`, parameterized over both facts. | `AssertionError: assert 'verified' == 'mismatch'`; `6 failed, 4 passed, 369 deselected in 0.89s`, exit 1. | `10 passed, 369 deselected in 0.61s`, exit 0. |
| The prose reader could verify an ID absent from its exact source quote. `test_offering_identifiers_reject_prose_values_missing_from_exact_source`; the control is `test_offering_identifiers_accept_exact_prose_with_layout_whitespace`. | `AssertionError: assert 'verified' == 'skipped'`; `8 failed, 2 passed, 379 deselected in 0.67s`, exit 1. | All identifier verifier tests: `20 passed, 369 deselected in 0.48s`, exit 0. Complete verifier suite: `389 passed in 1.43s`, exit 0. |
| The page decoder rejected 2.17 and the new offering fields. Vitest tests `retains the provider API model ID and separate OpenRouter slug in a 2.17 decision` and `accepts null offering identifiers in a 2.17 decision`. | `ZodError` reports invalid `contract_version` and unrecognized `api_model_id` and `router_slug`; `2 failed \| 2 passed (4)`, exit 1. | Targeted web suites: `35 passed (35)`, exit 0. Complete web suite: `813 passed (813)`, exit 0. |
| Record-only IDs were published as selectable vocabulary facets. `test_every_decision_facet_is_listed_with_label_unit_subject_type_and_operators` and `test_every_condition_and_objective_the_page_can_build_is_a_valid_spec`. | `AssertionError: assert 'string' in ('number', 'enum', 'boolean', 'date', 'set')` and `offering.api_model_id is record-only and cannot be used in a spec`; `2 failed in 0.84s`, exit 1. | Complete vocabulary suite: `70 passed in 1.99s`, exit 0. The vocabulary excludes record-only identifiers while decisions retain their values and provenance. |

Additional snapshot tests use `test_identifier_facts_use_existing_two_key_and_source_guards`
to reject a same-family verifier, stale value hash, missing source, unresolved
source, and excluded source for each identifier fact. These pass in the final
focused suite. Reader-family independence is also covered by
`test_offering_identifiers_need_an_independent_verification_family`.

`router-green.log` records an intermediate `1 failed, 2 passed` attempt whose
new assertion assumed an OpenRouter allow-list order. The green evidence above
uses the later successful run and the final focused suite.

## First full run and follow-up fixes

The first required full run exited 1:

```text
138 failed, 9859 passed, 8 skipped, 11 warnings, 12 errors in 1576.00s (0:26:15)
```

The contract bump exposed helpers that reconstructed the current `Decision`
with a 2.16 payload. The shared helpers caused 85 failures across summary,
next-move, and must-mention tests. Those helpers now use the current version.
The follow-up selection passed `207 passed, 1 skipped in 270.81s`, exit 0.

Generated CLI guidance, QA captures, the bounded MCP fixture, and web decision
fixtures retained old contract or source hashes. The existing generators
refreshed them. The generated/link/bounded check passed `205 passed in
35.61s`, exit 0. A separate bounded-fixture check passed one test, exit 0.
Decision-link byte probes restored only the previous contract-version fields
and matched each old baseline, confirming that the pinned-byte changes came
from the version bump. The link tests now pin the current bytes.

The first run also found the record-only vocabulary defect above. Its complete
suite now passes. References that failed the tracked-source exclusion guard
were removed. The follow-up selection includes that guard.

All 12 landing setup errors came from missing `web/dist`. The web build
completed with exit 0, and the refreshed web suite again passed all 813 tests.
An additional combined page/landing run was interrupted after 652 tests
passed, so it is not a completed green check. The final full-suite rerun
passed the landing computation and browser cases with the build present.

## Commands and versions

Commands run from the worktree root use Python 3.14.4 and pytest 9.1.1.
Web commands run from `web/` with Node v22.22.3, npm 10.9.8, Vitest 5.0.1,
and TypeScript 5.9.3. Git is 2.50.1 and GitHub CLI is 2.102.0.
Versions were read with `--version`; npm used `npm --version`.

The executor checked process exit codes directly. The common capture pattern
was a command redirected to a log, followed by saving `$?`, reading that log,
and exiting with the saved code. No test exit code was taken from a pipe.
The command bodies below omit repeated log redirection.

Initial router red selection:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_router_config.py -k 'verified_ids or unverified_or_null or provider_id_cannot'
```

Initial card red selection and the later provider-alias red selection:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_snapshot.py -k card_identifier
```

Successful identifier selection, after schema regeneration:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m decision.schema
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_router_config.py tests/test_decision_snapshot.py -k 'verified_ids or unverified_or_null or provider_id_cannot or card_identifier'
```

Literal-comparison red and green verifier selection:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_verify.py -k offering_identifiers --tb=short
```

Exact-source prose red selection:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_verify.py -k 'offering_identifiers_reject_prose or offering_identifiers_accept_exact_prose' --tb=short
```

The final verifier selection used the literal-comparison command above.
The complete verifier suite used:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_verify.py
```

Final focused Python suite, exit 0:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_router_config.py tests/test_decision_snapshot.py tests/test_decision_contract.py tests/test_api_docs.py tests/test_decision_registry.py tests/test_decision_compact_explain.py
```

First required full Python suite, exit 1 with the counts above:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
```

Final required full Python suite, **exit 0: 10009 passed, 8 skipped, 11 warnings in 1448.88s**.
Its log is `tmp/model-209/python-full-final.log`:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
```

Follow-up helper/snapshot/source-guard check, exit 0:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_summary.py tests/test_next_move.py tests/test_must_mention_overreach.py tests/test_decision_snapshot.py tests/test_removed_sources.py
```

Vocabulary check, exit 0:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_vocabulary.py
```

Generated artifact refreshes, each exit 0:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.decide_budget
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
```

Web fixture refresh, from the worktree root, exit 0 with 13 tests passed:

```sh
MODELSPEC_WRITE_FIXTURES=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decide_page_fixtures.py
```

Page fixture/spec checks, exit 0 with 624 tests passed:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decide_page_fixtures.py tests/test_decide_page_specs.py
```

Web dependency installation and complete web suite, from `web/`. The web
suite exited 0 with `50 passed | 1 skipped (51)` test files and 813 tests.

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test
```

Web typecheck, exit 0 with no diagnostic output:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH ./node_modules/.bin/tsc -b
```

Web build from `web/`, exit 0:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=/Users/terbeest/dev/worktrees/model-209 npm run build
```

The web red selection used `npm test -- src/decide/__tests__/offering-ids.test.ts`.
Its green selection added `adapter.test.ts`, `contract-nulls.test.ts`,
`contract-plans.test.ts`, and `architecture-facts.test.ts` from the same
directory. Both used the Node PATH above.

OpenAPI regeneration and drift check both exited 0:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
```

The version/doc checks passed 10 tests, exit 0:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_contract.py::test_objective_terms_accept_evidence_qualifiers tests/test_decision_contract.py::test_schema_file_is_generated_from_the_types tests/test_decision_contract.py::test_doc_names_the_contract_version tests/test_decision_contract.py::test_doc_names_every_field_of_every_type tests/test_decision_contract.py::test_doc_names_every_closed_value tests/test_decision_contract.py::test_doc_examples_are_valid tests/test_decision_estate.py::test_the_contract_version_took_the_next_minor tests/test_architecture_facts.py::test_optional_interval_is_absent_unless_set_and_bounded_version_is_unchanged tests/test_api_docs.py::test_decide_response_description_uses_the_bounded_version tests/test_api_docs.py::test_the_committed_spec_is_what_the_implementation_generates
```

Current contract version assertions and generated schemas were updated to
2.17. Historical version references remain unchanged.

## Data PR collection scope

The local `budget-coding` decision uses the frozen data and
`as_of=2026-10-13`, with the default 40,000 input and 4,000 output tokens.
The best band contains `google/gemini-3-7-flash` and
`google/gemini-3-8-flash`. Each qualifying route costs $0.045 per task.
The later private `modelspec-data` PR must collect a provider API ID for each
of these four offering identities:

- `google-gemini-api/google/gemini-3-7-flash/global/standard`
- `google-vertex-ai/google/gemini-3-7-flash/global/standard`
- `google-gemini-api/google/gemini-3-8-flash/global/standard`
- `google-vertex-ai/google/gemini-3-8-flash/global/standard`

Primary collection entry points are the existing registered
[Gemini 3.7 model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash),
[Gemini 3.8 model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash),
and [Vertex 3.8 model page](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-8-flash).
No Vertex 3.7 model-specific source is currently registered. Follow Google's
model/catalog links from the registered
[Vertex pricing page](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing)
to the authoritative page for that exact model.

Collect separate OpenRouter slugs for the two models from actual entries in
[OpenRouter's model catalog](https://openrouter.ai/api/v1/models). Preserve
the offering association and confirm its provider endpoint where needed.
Do not construct a slug or reuse a Gemini API ID as a Vertex ID.
Every non-null fact needs a registered primary source, retained source copy,
cited region, claim, and matching independent verification. Missing or
unverified values stay null with their reason.

The local scope script is
`tmp/model-209/data_followup_reader/list_budget_routes.py`. Its equivalent
standalone command reproduces the best-band collection scope:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from datetime import date
from pathlib import Path
from decision.contract import parse_spec
from decision.engine import decide
from decision.registry import default
from decision.router_config import listed
from decision.snapshot import build_from_repo, load_built_snapshot
from decision.templates import template_by_id

root = Path.cwd()
registry = default()
built = build_from_repo(root, premier=root / "premier/slice-1.yaml",
                        as_of=date(2026, 10, 13), registry=registry)
index = load_built_snapshot(built)
spec = parse_spec(template_by_id("budget-coding")["spec"], facets=registry.facet)
decision = decide(spec, index, facets=registry.facet)
print(built.snapshot_id)
for model in listed(decision):
    for route in model.routes:
        print(route.offering_id, route.cost_per_task)
PY
```

The latest captured scope output is `tmp/model-209/budget-routes-final.json`,
snapshot `snap_da350b74acc7c61f`. Its four routes match the original frozen
build, snapshot `snap_79eb85bc75644d1c`. Both cards currently have blank
primary-provider, Vertex, and OpenRouter ID fields.

## What was not observed

- No live provider IDs or live OpenRouter slugs were collected. Source URLs
  above are collection entry points from the repository, not live findings.
- No real LLM reader was called. Reader tests injected local replies through
  the completion interface and checked exact retained source text.
- LiteLLM runtime execution was unavailable. Exported configurations were
  checked against the vendored published schemas, and OpenRouter guardrail
  creation was not called.
- No deployment, production switch change, paid-provider call, or WSL gate
  ran. No excluded source was fetched or admitted.
- The initial delivery preceded the independent cross-model review.
  REVIEW-718 findings and their fixes are recorded below. CI is separate
  from these local verification results.

## Delivery checks

The OpenAPI implementation check and data freeze both exited 0.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base 2b0770afab18d101ea033c9259d53ae4ac42e2ce --head HEAD --branch sparksandsawdust/model-209-api-model-id
git diff --check
```

The branch is delivered as a draft PR. Push uses `CI_LOCAL_SKIP=1`, as the
executor brief requires after focused checks, while CI supplies its own gate.
The initial delivery did not include a merge or production deployment.
The later local main merge is recorded below.

## REVIEW-718 fixes

The Grok 4.7 review requested changes at PR head
`6d2744381bfecf4768279e2257edfcae732e38a5`. Before changing code, the executor
fetched and merged `origin/main`, SHA
`3234406f0663231f02a033ce595019580134cc28`. The clean local merge is
`e55f4042bf6fbba79d82f41c4700c52226c8e98d`. Jamie explicitly requested this
local merge. The PR remains a draft and was not merged into main.

The tested code commit is `a442167af362991194da273a2f70898116607f36`.
The final evidence commit is resolved by the delivery-SHA command at the top
of this record.

### Finding 1: Worker identifier omission

`OfferingRef` now extends `_ExcludeIf`, matching `HardwareEstimate`. Its
existing `exclude_if` predicates omit absent identifiers on both native and
compatibility serializers. Existing nullable provider, region, and tier
fields retain their values.

The regression is
`test_offering_identifiers_serialize_in_pre_212_compatibility_mode`. A fresh
subprocess moves exclusion predicates into `json_schema_extra`, prevents the
feature probe from detecting native support, and imports the contract. It
asserts that native exclusion is disabled. Literal expected objects pin
omission for default and explicit null identifiers, retention of populated
identifiers, `model_dump(mode="json")`, `model_dump_json()`, and nested
`CandidateValues` serialization. This exercises the actual import-time
compatibility serializer regardless of the installed pydantic version.

Red, exit 1, `1 failed in 0.78s`:

```text
At index 0 diff: {'dump': {'model': 'lab/alpha', 'provider': None,
'region': None, 'tier': None, 'api_model_id': None, 'router_slug': None}, ...}
```

Green, exit 0, `279 passed in 1.97s`, from the contract and plan suites.
The final combined regression check also exited 0 with
`4 passed in 11.52s`. Logs are `tmp/model-209/compat-red.log`,
`compat-green.log`, and `review-regression-green.log`.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_contract.py::test_offering_identifiers_serialize_in_pre_212_compatibility_mode
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_contract.py tests/test_decision_plans.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_contract.py::test_offering_identifiers_serialize_in_pre_212_compatibility_mode tests/test_mcp_contract_version.py
```

### Finding 2: MCP fallback version

Both bounded fallbacks in `mcp/src/server.ts` now use
`CURRENT_CONTRACT_VERSION`. `python -m decision.schema` generates
`mcp/src/contract-version.ts` from `decision.contract.CONTRACT_VERSION`.
The generator's `--check` mode rejects stale or missing artifacts without
writing them. The QA MCP capture was regenerated because it hashes
`server.ts`; only that source hash changed.

The two MCP regressions are `uses contract 2.17 when a bounded trimmed body
has neither version field` and `uses contract 2.17 when empty versions reach
the over-budget minimal fallback`. Both assert literal `2.17` and a response
within 16,384 bytes.

Red, exit 1, `2 failed`: both expected `projects_contract: "2.17"` and
received `"2.16"`. Green, exit 0, `2 passed`.

The Python sync/generator tests were also red first, exit 1 with `3 failed`,
because the generated module was missing and the generator lacked check-mode
arguments. Green, exit 0, `3 passed in 0.64s`.

From `mcp/`:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test -- test/contract-version.test.ts
```

From the repository root, each final command exited 0:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_mcp_contract_version.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m decision.schema
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m decision.schema --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
```

Logs are under `tmp/model-209/mcp-review/`.

### Full verification after the review fixes

The full Python suite exited 0: `10044 passed, 8 skipped, 11 warnings in 1090.70s (0:18:10)`. Its log is `tmp/model-209/review-python-full.log`.

The full web suite exited 0, with 50 test files passed, one skipped, and
813 tests passed in 26.35 seconds. Web installation and build each exited 0.
The full MCP suite exited 0, with eight files and 136 tests passed in
1.45 seconds. MCP installation and typecheck each exited 0. Exit codes came
directly from the completed commands, not a pipe or a log-reader exit code.

The full Python command, from the worktree root:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
```

From `web/`:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm ci
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm run build
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm test
```

From `mcp/`:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm run typecheck
```

The schema drift check, OpenAPI check, data freeze guard against
`origin/main`, and `git diff --check` exited 0.
After updating this evidence, the source-exclusion suite also exited 0 with
`5 passed, 1 skipped in 93.76s`.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base origin/main --head HEAD --branch sparksandsawdust/model-209-api-model-id
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_removed_sources.py
git diff --check
```

Versions were Python 3.14.4, pydantic 2.13.5, pytest 9.1.1, Node v22.22.3,
npm 10.9.8, and Vitest 5.0.1. MCP typecheck used TypeScript 7.0.2.

### Other review points and limits

The review passed the additive 2.17 contract bump, admission guards, literal
identifier verification, distinct router placeholders, data freeze, the
16 KB response limit, and keyed machine access. They required no behavioral
change. The fixes leave their implementation and limits in place; the MCP
regressions explicitly retain the same byte cap.

No Pyodide boot, deployed Worker request, live provider catalogue fetch, or
paid-provider call ran. The new Worker regression simulates the older
pydantic metadata and serializer-registration path in CPython, rather than
booting the locked 2.10.6 Worker runtime. CI and a second cross-model review
are not part of these local results. All executor-started processes were
completed before delivery.
