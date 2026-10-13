# MODEL-210-fix execution evidence

REVIEW-720 P2: an absent, unknown, or empty `coding_tools_quote` still routed as `coding_tool:*`, and `tool_listing()` filled the not-named label with `…`. A plan now takes that route only when the quote is a known, non-empty string. Without one, the open token is not a route and the answer is not confirmed.

## Revisions and tools

Reviewed head `4f97c6c4b98b194d3254259e4b15dfc4505030c7`. `origin/main` had moved to `e6a1b94c30af39cb2bbf7b91233f9691cfa98329`. Merge commit before the fix: `cd9438101977b6eb8895d8b62d44812a7b96d8b6`. The evidence commit is the tip of `sparksandsawdust/model-210-coding-tool-surface`. It cannot contain its own SHA. The executor's final line records that SHA.

Commands ran in `/Users/terbeest/dev/worktrees/model-210`.
Python 3.14.4, pytest 9.1.1, Git 2.50.1, gh 2.102.0.

## Red test

`test_an_unlisted_harness_does_not_take_the_open_list_without_a_provider_quote`, parametrized over `absent`, `unknown`, and `empty`, against unchanged `decision/plans.py`.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_coding_tool_open.py::test_an_unlisted_harness_does_not_take_the_open_list_without_a_provider_quote tests/test_decision_coding_tool_open.py::test_a_named_harness_stays_confirmed_when_the_open_quote_is_missing --tb=short
```

Exit 1. `3 failed, 3 passed in 0.52s`. Each failed case built a route with `surface='coding_tool:*'` and basis `provider lists tools such as …; your tool isn't named`. The three named-harness cases passed on that same run. A named surface still confirms when the open quote is missing.

## Green tests

Same two tests, then the plan suites, after the gate in `Plan.surface()` and `tool_listing()`:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_coding_tool_open.py tests/test_decision_plans.py --tb=line
```

Exit 0. `53 passed in 1.19s`.

Full suite, exit code of this command:

```sh
env -u CI PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
```

Exit 0. `10249 passed, 23 skipped, 11 warnings in 1669.71s`.

## Not observed

Live Z.ai, MiniMax, or Alibaba pages, the decide board in a browser, and both site builds. `decision/verify.py` and `docs/decision-contract.md` were not edited. The contract table still says an open-ended list routes every harness. The code now also requires the quote. CI on the push was not awaited. No Linear write.
