# MODEL-258 round 3: billing replay import isolation

Worktree: `/Users/terbeest/dev/worktrees/model-258-guides`.
Branch: `model-258-guides`. PR: <https://github.com/turbobeest/modelspec/pull/824>.
Base SHA: `81d0ed05ef34ed26655470c2773aa88c1a9c128a`.
Final implementation and test SHA: `c980717d7470cd495f45bcc8cf2461b64731062b`.
The subsequent evidence-only commit records the completed checks; the executor
completion line identifies the final pushed SHA.

## Fix and scope

The billing replay used `patch.dict(sys.modules, ...)` to stub `js`, `workers`
and `bundled_data` while importing the Worker entry. Its cleanup restored the
entire module registry, removing modules first imported inside that block.
Pydantic retained references to classes whose defining module was then absent,
so a later generic specialization raised `KeyError: 'pydantic.root_model'`.

The replay now saves and restores only those three names in `try/finally`.
A unique sentinel distinguishes an absent entry from a pre-existing `None`.
Cleanup also runs if entry import fails. All other imported modules remain
registered.

The regression runs the real replay in fresh subprocesses. It verifies that
`pydantic.root_model` is first imported by replay, remains registered afterwards,
and supports subsequent `RootModel` specialization. It checks exact restoration
for absent names, existing module objects and existing `None` entries.

An independent read-only audit searched `tests/` for `patch.dict` targeting
`sys.modules`, quoted targets, aliases, assignments and whole-map
`clear`/`update`/`copy` restoration. The billing replay was the only affected
location. Other entry fixtures already restore individual names. Review of the
final diff found no issues.

Only `tests/replay_billing_launch.py`, `tests/test_billing_launch.py` and this
evidence file changed in round 3. No guide or production behavior changed.

## Red-first reproduction

Commands ran from the worktree using Python 3.14.4, pytest 9.1.1 and Pydantic
2.13.5. Each process exit code was read directly. Local log directories:

```sh
mkdir -p docs/evidence/g2-ios/model-258-r3-root
```

The exact reported file order, before editing the fixture:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:randomly tests/test_billing_launch.py tests/test_agent_guide.py::test_schema_compaction_preserves_every_original_rule > docs/evidence/g2-ios/model-258-r3-root/red-order.log 2>&1
```

Exit 1:

```text
pydantic/_internal/_generics.py:144
reference_module_globals = sys.modules[created_model.__module__].__dict__
KeyError: 'pydantic.root_model'
1 failed, 21 passed in 2.30s
```

The new regression, still against the unchanged fixture:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:randomly tests/test_billing_launch.py::test_replay_preserves_imports_and_restores_only_runtime_stubs > docs/evidence/g2-ios/model-258-r3-root/red-regression.log 2>&1
```

Exit 1. All three prior states failed at the same assertion:

```text
assert "pydantic.root_model" in sys.modules
AssertionError
3 failed in 1.65s
```

## Focused verification

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:randomly tests/test_billing_launch.py tests/test_agent_guide.py::test_schema_compaction_preserves_every_original_rule > docs/evidence/g2-ios/model-258-r3-root/green-order.log 2>&1
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:randomly tests/test_billing_launch.py tests/test_billing_smokes.py tests/test_agent_guide.py > docs/evidence/g2-ios/model-258-r3-root/focused.log 2>&1
```

Both exited 0:

```text
25 passed in 3.26s
58 passed in 7.37s
```

The requested order includes the three new regression cases. The existing
schema-compaction assertion was not changed.

This scope check also exited 0 with no diff:

```sh
git diff --exit-code 81d0ed05ef34ed26655470c2773aa88c1a9c128a -- pipeline web api decision
```

## Full suite

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile > docs/evidence/g2-ios/model-258-r3-root/full-suite.log 2>&1
```

Exit 0 after acquiring the shared lock:

```text
11871 passed, 9 skipped, 11 warnings in 1373.47s (0:22:53)
```

The warnings concern unsigned decision vocabulary in the CLI snapshot tests.

## Limits

No guide edits, site deployment, live API requests, private-data reads or paid
provider calls were made for this fix. No approval or ready/draft metadata was
changed. The local reproduction and checks above verify the fixture correction;
the new remote CI run is not observed in this record.
