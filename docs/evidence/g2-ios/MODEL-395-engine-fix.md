# MODEL-395 engine follow-up

The subscription integration tests now compare the loader and snapshot with
independent projections of their source YAML. Historical plan lists, fact totals,
and known-facet lists no longer pin the tests to one data image. Complete
identity, value, and source comparisons still detect dropped plans and facts.

## Revisions and scope

- Engine base: `fe5f62392507ed86667dd41d53b350608859e018`, public main including
  merged MODEL-392 PR #753.
- Implementation commit: `334b6a1b`, followed by formatting and this evidence.
- Engine worktree: `/Users/terbeest/dev/worktrees/model-395-engine`.
- Branch: `model-395-engine-tests`.
- Private main checked out for composition:
  `85e71131d455d5517bcf9eb50630a649dfbedccb`.
- Final SHA is the commit containing this report, resolved with
  `git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-395-engine-fix.md`.
  The engine PR body and executor completion line record the literal SHA.

Only tests and evidence change. No runtime code, registry vocabulary, public
contract output, or frozen public data changes. No contract version bump applies.
Data #87 retains its merged `.engine-pin`; it waits for this engine PR to merge
and one more pin bump before its full broader gate can be retested at that pin.

## Red reproduction

The untouched engine was physically composed into a fresh clone of private main
with `scripts/prepare_data_writer.py`, the same script used by data #87's workflow.
Both named tests failed, exit **1**, `2 failed in 37.16s`:

- `test_repository_subscription_offerings_validate_against_the_real_registry`
  failed at the old ID list after availability loading succeeded. The private
  image includes MiniMax Go/Explore/Build in addition to the historical list.
- `test_production_snapshot_admits_supported_subscription_facts` failed at
  `37 == 34`.

[Red receipt](MODEL-395-engine/private-red.log.gz).

## Source expectations and retained regression checks

`tests/subscription_sources.py` reads YAML directly, rather than deriving expected
subscriptions from either API under test. It checks that every subscription file
tracked by the checkout exists, validates plan owners and facets against the real
registry, excludes the MODEL-205 vendor plans as before, and rejects duplicate
identities/facets and unsourced or unresolved known facts. Git's tracked inventory
catches a missing source file even when every plan in that file lacks a targeted
literal assertion. Both CI workflows provide a Git checkout.

The loader check compares its complete ordered identity list with the source
identity list. For each plan it compares metadata, fact count, and every authored
fact field, including cited regions, source snapshot references, verification,
and values. The existing known/unknown-state invariants remain. The xAI consumer
terms source assertion remains and now explicitly requires both selected plans
and their two programmatic-use facts, preventing a vacuous `all()` result.

The snapshot expectation independently filters raw facts using matching value
hashes, latest counting verification, inline/log tie precedence, unknown-state
exclusion, resolved nonempty sources, and measurement staleness. It uses the
public value-hash, verification-lineage, and measurement contracts; it calls no
snapshot compiler, collector, or build-audit implementation to derive expected
facts. The test compares the complete supported identity set and the complete
per-plan facet-to-`FactValue` map, including exact source IDs. A compiler that
drops a plan or source, or admits an extra/quarantined fact, differs from this map.

All six original targeted snapshot assertions are AST-identical to the base:
Anthropic Max 20x price/source, Gemini Ultra 20x price/source, OpenAI Plus model
coverage, Anthropic Pro price/source, OpenAI Pro 5x usage/source, and xAI SuperGrok
model coverage/source. The exclusion from metered candidates also remains.
[Assertion preservation receipt](MODEL-395-engine/targeted-assertions.json).

## Mutations fail both actual tests

`tests/test_subscription_source_expectations.py` copies the offering files into
a temporary source tree and calls each actual integration test. Its four cases
require the intended assertion failure for each test and corruption:

| Corruption in the temporary Mistral file | Loader test | Snapshot test |
| --- | --- | --- |
| Delete `offerings/subscriptions/mistral.yaml` | `missing subscription files` | `missing subscription files` |
| Remove the sources from one known fact | `unsourced known subscription fact` | `unsourced known subscription fact` |

Mistral deliberately has no targeted plan/value assertion in either original
test; these failures exercise the source completeness and citation checks.
The temporary copies link the remaining read-only inputs and Git inventory.
Neither public nor private source data was changed.

[mutations.py](MODEL-395-engine/mutations.py) also launches pytest itself against
both corrupted copies. Each subprocess returns **1**, reports **2 failed**, and
names exactly the two requested integration tests. The replay driver returns
**0** only after checking those exit codes, node IDs, and reasons.
[Mutation verdicts](MODEL-395-engine/mutations.json),
[deleted-file pytest receipt](MODEL-395-engine/mutation-missing-file.log.gz),
[unsourced-fact pytest receipt](MODEL-395-engine/mutation-unsourced-fact.log.gz).

## Public and private checks

The public-image focused run returned **0**, `6 passed in 34.34s`; the private
composition returned **0**, `6 passed in 31.67s`. Each run includes the two target
tests and all four mutation cases.

Both were then repeated under Python **3.11.15**, matching the engine and data
workflows, using a fresh environment installed with only the declared `.[dev]`
dependencies:

- Public image: **0**, `6 passed in 50.82s`.
- Private main, physically composed by `prepare_data_writer.py`: **0**,
  `6 passed in 49.31s`.

[Public CI-version receipt](MODEL-395-engine/public-ci-focused.log.gz),
[private CI-version receipt](MODEL-395-engine/private-ci-focused.log.gz).
The exact required full engine command returned **0**:
`11071 passed, 9 skipped, 11 warnings in 1184.97s (0:19:44)`.
[Full engine receipt](MODEL-395-engine/full-engine.log.gz).

Ruff passes for every changed Python module and the replay driver. The new files
pass formatter checks. Whitespace checks pass. The four-shard planner includes
the new mutation module and reports balanced predicted totals, exit **0**.
[Shard planner receipt](MODEL-395-engine/shards.log.gz).

## Reproduction commands

From the engine worktree, after reading the execution brief, spec, `AGENTS.md`,
`CLAUDE.md`, `CONTEXT.md`, and handoff rules:

```bash
git fetch origin
git rev-parse HEAD origin/main
git clone --quiet --filter=blob:none --single-branch --branch main https://github.com/turbobeest/modelspec-data.git .artifacts/model-395/private-data
python scripts/prepare_data_writer.py --engine . --data .artifacts/model-395/private-data
```

From that composed private directory, before the repair, then after composition
of the repaired tests:

```bash
MODELSPEC_REQUIRE_DATA_DIR=1 MODELSPEC_DATA_DIR="$PWD" PYTHONPATH="$PWD" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_model.py::test_repository_subscription_offerings_validate_against_the_real_registry tests/test_decision_snapshot.py::test_production_snapshot_admits_supported_subscription_facts
```

The focused green commands add `tests/test_subscription_source_expectations.py`.
For the CI-version runs, setup from the engine root was:

```bash
uv venv --python 3.11 .artifacts/model-395/ci-venv
uv pip install --python .artifacts/model-395/ci-venv/bin/python -e '.artifacts/model-395/private-data[dev]'
PYTHONPATH=$PWD .artifacts/model-395/ci-venv/bin/python -m pytest -q tests/test_decision_model.py::test_repository_subscription_offerings_validate_against_the_real_registry tests/test_decision_snapshot.py::test_production_snapshot_admits_supported_subscription_facts tests/test_subscription_source_expectations.py
```

The private CI-version command ran from the composed private directory with
`MODELSPEC_REQUIRE_DATA_DIR=1 MODELSPEC_DATA_DIR="$PWD" PYTHONPATH="$PWD"` and
`../ci-venv/bin/python`, using exactly the same pytest arguments.

From the engine root:

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-395-engine/mutations.py
python -m ruff check tests/conftest.py tests/subscription_sources.py tests/test_subscription_source_expectations.py tests/test_decision_model.py tests/test_decision_snapshot.py docs/evidence/g2-ios/MODEL-395-engine/mutations.py
python -m ruff format --check tests/subscription_sources.py tests/test_subscription_source_expectations.py docs/evidence/g2-ios/MODEL-395-engine/mutations.py
python scripts/pytest_shards.py --shard-count 4 --summary
git diff --check
git diff --cached --check
export PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH"
npm ci --prefix web --no-audit --no-fund
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.artifacts/model-395/browsers"
web/node_modules/.bin/playwright install chromium
npm run build --prefix web
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

Each pytest run captured `result=$?` immediately after the command. Receipts use
deterministic gzip compression; measured exit codes and SHA-256 digests are in
`MODEL-395-engine/checks.json`.

The shared full-suite interpreter is Python **3.14.4**; the isolated CI-version
interpreter is **3.11.15**. Both use pytest **9.1.1**. Ruff **0.16.6**, Node
**22.22.3**, and npm **10.9.8** were used.

No data pin was advanced to an unmerged commit. No hosted CI verdict or data #87
broader gate at a future merged pin is claimed. No vendor inference, workflow
dispatch, PR merge, Linear write, or deployment ran. The draft workflow change
in data #87 still requires human review and merge.
