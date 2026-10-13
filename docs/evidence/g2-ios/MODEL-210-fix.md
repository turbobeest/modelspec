# MODEL-210 execution evidence

An open-ended coding-tool list is a plan surface, `coding_tool:*`. The
engine routes that plan for `access: coding_tool` and for every harness.
A harness the page also names is marked confirmed. Any other harness is
marked not named by the provider. `PlanRoute.surface` stays an
unconstrained string, so `contract_version` stays 2.16.

## Revisions and tools

Work started at `3234406f0663231f02a033ce595019580134cc28`.
Before the first push the branch was rebased onto `origin/main`
`434dd2b0` (MODEL-364). The only conflict was the changelog in
`docs/decision-contract.md`; both the MODEL-364 bullet and the MODEL-210
bullet were kept. The cited red and green runs are the pre-rebase tree.
That tree and the rebased tree differ only by that changelog merge.
Rebased implementation SHA: `f820dd273e2d4f7c3f063344750b1482cb67937b`.
The evidence commit is the tip of `sparksandsawdust/model-210-coding-tool-surface`.
It cannot contain its own SHA. The executor's final line records that SHA.

Commands ran in `/Users/terbeest/dev/worktrees/model-210`.
Python 3.14.4 (main, Apr 7 2026), pytest 9.1.1, Git 2.50.1, gh 2.102.0.

## Contract gate

`PlanRoute.surface` in `decision/contract.py` is `str`. The JSON schema
property is `{"type": "string"}` with no enum. `plan_surfaces` is the
registry list behind `offering.subscription.surfaces`. Adding
`coding_tool:*` widens that list. It does not add an enum value, and no
response field was added. Proceeded. No major bump.

## Red tests and fixes

The new tests ran before the registry token and the quote facet existed:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_coding_tool_open.py --tb=line
```

Exit 1. `6 failed in 0.44s`.

| Missing behavior | Red-first test | Red output | Green output |
| --- | --- | --- | --- |
| `coding_tool:*` is a legal surface and the quote facet is registered | `test_an_open_list_is_a_legal_plan_fact` | `ValidationError`: surfaces value not in the registered list (no `coding_tool:*`), and `unknown facet ID: offering.subscription.coding_tools_quote` | Passed inside the focused suite below |
| The answer field stays a string | `test_coding_tool_star_is_a_registry_surface_and_the_answer_field_stays_a_string` | `AssertionError: assert 'coding_tool:*' in frozenset({'api', 'chat_app', 'coding_tool:aider', ...})` | Passed; schema `surface.type` is `string` and has no `enum` |
| Named harness is confirmed | `test_a_glm_coding_holder_is_confirmed_for_a_named_harness` | `SnapshotBuildError: facet 'offering.subscription.coding_tools_quote' is not registered` (`decision/snapshot.py:825`, from `UnknownIdError`) | Passed; surface `coding_tool:claude-code`, `confirmed` on the coverage rule and the basis |
| Unlisted harness is not confirmed | `test_a_glm_coding_holder_is_not_named_for_an_unlisted_harness` | Same `SnapshotBuildError` | Passed; surface `coding_tool:*`, both texts contain `tool not named by the provider` and the quoted sentence, and neither contains `confirmed` |
| Bare `coding_tool` routes with no verdict | `test_an_open_list_routes_for_bare_coding_tool_without_a_tool_verdict` | Same `SnapshotBuildError` | Passed; surface `coding_tool:*`, neither label |
| Other access kinds do not match | `test_an_open_coding_tool_list_does_not_serve_another_access` | Same `SnapshotBuildError` | Passed; `with_estate.results == []` for `chat_app`, `own_software`, and `own_hardware` |

An earlier run of the same file, before the fixture sold the closed-weights
model, exited 1 with `4 failed, 1 passed`. The three decision tests raised
`StopIteration` because a bare unsold closed-weights row is `no_route`.
That run is a bad fixture, not the defect above. The cited red is the run
after the fixture included a Z.ai offering and `registry=default()`.

After the engine change, one existing count was still 13:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_coding_tool_open.py tests/test_decision_plans.py tests/test_decision_vendors.py tests/test_decision_registry.py --tb=short
```

Exit 1. `1 failed, 147 passed in 18.16s`.
`test_subscription_facets_are_record_only_until_holder_costs_exist` got
`assert 14 == 13`. The new quote facet is the fourteenth subscription facet.
The assertion is now 14. The same command then exited 0: `148 passed in 15.95s`.
After the rebase onto `434dd2b0`, that command exited 0 again: `148 passed in 42.52s`.
Cursor Pro's exact basis in `test_decision_vendors.py` stayed unchanged.

The required full command, with the executor shell's `CI=true` removed so a
missing Playwright install skips instead of failing:

```sh
env -u CI PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
```

Exit 0. `9995 passed, 22 skipped, 11 warnings in 1441.55s (0:24:01)`.
The warnings are the existing unsigned vocabulary fixtures in the CLI
snapshot tests.

The same command with the inherited `CI=true` exited 1: `2 failed, 9995
passed, 8 skipped, 12 errors in 1747.19s`. Every failure and error is
`web/node_modules/playwright` missing (`tests/test_social_cards.py`,
`tests/test_landing.py`). This change does not touch `web/`. Those tests
skip when `CI` is unset.

## What was not observed

- Live Z.ai, MiniMax, or Alibaba plan pages. The quote in the test is fixture text.
- The decide board. `surfacePhrase` turns `coding_tool:*` into `*` through `harnessName`. When a plan has a break-even, `breakEvenNote` replaces `basis`, so the new sentence is in the API answer and not in that board note.
- A data-repo recording of `coding_tool:*` or `coding_tools_quote`. `decision/verify.py` was not changed.
- Ranking floors, `neutrality_commitment()`, and frozen public data. None of those files changed.
- Linear writes, a merge, or a non-draft PR.
