# MODEL-210-fix2 execution evidence

REREVIEW-720 P2: a `coding_tools_quote` of only whitespace still routed as `coding_tool:*`. `Plan.surface()` and `tool_listing()` both ask `_routable_quote()`. That function now requires `quote.strip()` to leave text, and it still returns the original string.

## Revisions and tools

Base `f7e19cb6eabfc83a9ee697782909323c304d81df`. Fix commit `ba0d3359a7145b4490a3c1782fb2335409d8a9a1` on `sparksandsawdust/model-210-coding-tool-surface`. This evidence commit is the tip. It cannot contain its own SHA. The executor's final line records that SHA.

Commands ran in `/Users/terbeest/dev/worktrees/model-210`.
Python 3.14.4, pytest 9.1.1, pytest-xdist 3.8.0, Git 2.50.1, gh 2.102.0.

## Red test

`test_an_unlisted_harness_does_not_take_the_open_list_without_a_provider_quote` and `test_a_named_harness_stays_confirmed_when_the_open_quote_is_missing`, parametrized over `absent`, `unknown`, `empty`, and `whitespace`, against unchanged `decision/plans.py`. The whitespace fixture records `"   "`.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_coding_tool_open.py::test_an_unlisted_harness_does_not_take_the_open_list_without_a_provider_quote tests/test_decision_coding_tool_open.py::test_a_named_harness_stays_confirmed_when_the_open_quote_is_missing --tb=short
```

Log `/tmp/model-210-fix2-red.log` ends with `1 failed, 7 passed in 0.68s`. The whitespace unlisted case failed `assert wildcard == []`. The route was `surface='coding_tool:*'` and the basis contained `provider lists tools such as    ; your tool isn't named`. The other seven cases passed, including the named harness with a whitespace quote. This shell then assigned `status=$?`, which zsh rejects, so that wrapper's exit code is not pytest's.

## Green tests

Same two tests after the `strip()` check:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_coding_tool_open.py::test_an_unlisted_harness_does_not_take_the_open_list_without_a_provider_quote tests/test_decision_coding_tool_open.py::test_a_named_harness_stays_confirmed_when_the_open_quote_is_missing --tb=short
```

Exit 0. `8 passed in 1.12s`.

Touched files, same interpreter:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_coding_tool_open.py tests/test_decision_registry.py tests/test_decision_plans.py tests/test_decision_vendors.py --tb=short
```

Exit 0. `156 passed in 34.15s`.

Full suite, exit code of this command:

```sh
env -u CI PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
```

Exit 0. `10251 passed, 23 skipped, 11 warnings in 1420.27s (0:23:40)`.

## Not observed

Live provider pages, the decide board in a browser, and both site builds. `docs/decision-contract.md` was left as the re-review described it. CI on the push was not awaited. No Linear write.
