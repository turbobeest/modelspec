# MODEL-384 execution evidence

Base SHA: `56c39ac3a826af6f79f8755c49ed52b68bad37c4`.
Final implementation SHA: `ec145f41c6d02dc3cde71f4b952e55fc4e699724`, before this evidence-only commit.
Required full-suite SHA: `68ef6bb66e49ac74a417dae02624c314f2a818d2`.
The final delivery SHA is the commit containing this file. Resolve it with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-384-fix.md`.

Delivery status: **BLOCKED**. The web decoder and generated page fixtures
need changes outside the paths authorized by the executor brief. The decoder
accepts only complete contracts through 2.17 and uses strict object schemas.
It therefore rejects every 2.18 response and has no schemas for the new
optional exclusion and holding fields. `hosted.ts` calls this decoder and
reports `invalid_response` when parsing fails. The scope request is pending;
no web source or fixture was changed.

Required follow-up paths are `web/src/decide/adapter/contract.ts`, its tests,
and the generated decision/vocabulary fixtures under
`web/src/decide/__fixtures__/`. The executor
brief says: "If you need a file outside them, stop and report it."
The requested draft PR records the permitted implementation and this blocker.

The engine now reads the sourced `offering.subscription.availability` fact.
Unrestricted routes exclude `existing_subscribers_only` and `retired`; held
plans can use the former, and nobody can use the latter. Prospective estate
gains never suggest buying either unavailable plan. Availability checks run
before unknown coverage or surfaces can admit a candidate.

Complete contract 2.17 becomes 2.18. New optional fields are
`Decision.excluded_plans`, `WithEstate.excluded_plans` and
`EstateMark.availability`. Exclusions contain a plan ID and a reason. Ranked
holders of a closed plan receive its availability and a sentence in
`with_estate.gap.summary`. Bounded 1.3 adds optional exclusions and projects
2.18; its existing fields retain their ranges. Main's MODEL-339 bounded 1.3,
optional `pick` and withheld tie-breakers were preserved during the required
merge. Unknown availability adds no
availability field and preserves existing routes.

The vocabulary publishes the record-only facet under `estate.plan_facets`
and known values under `estate.plans[].availability`. Exact facet lookup,
compact search and the display projection retain these additions. The
deterministic reader accepts explicit plan-scoped statements and labelled
table cells. Other subscription fields retain their previous reader dispatch.

## Red and green results

The initial engine tests ran against the unchanged checkout before any
implementation edit: exit 1, `19 failed, 3 passed in 0.72s`. An unknown-coverage
fixture initially left another plan's coverage unknown too. It was corrected
to isolate the unavailable plan. The final test file was also run against an
archive of the actual base revision: exit 1,
`22 failed, 4 passed, 3 deselected in 0.76s`. The deselected cases test the
new bounded reporting fields. This second run also covers the API-enabled
closed-plan route, subscription-only vendors and monthly-price filtering.

| Defect | Red-first test | Red output | Green output |
| --- | --- | --- | --- |
| New buyers can use closed plans | `test_new_buyer_cannot_route_through_closed_plan` | `assert all(route.plan != MAX ...)` fails for a matching plan surface | Passes for chat, coding and own software |
| Existing holders have no availability label | `test_estate_holder_keeps_closed_plan_and_answer_labels_it` | `AttributeError: 'EstateMark' object has no attribute 'availability'` | Passes with and without access; both covered models remain reachable at zero marginal cost |
| Retired plans still reach holders | `test_retired_plan_never_routes_even_for_holder` | A retired plan remains in routes or held results instead of `[]` | Passes with and without access |
| Gain suggests an unavailable purchase | `test_estate_gain_never_suggests_buying_unavailable_plan` | `MAX` remains among `item.add.id` | Passes for closed and retired plans |
| Unknown coverage leaks unavailable plans into may-qualify | `test_unavailable_plan_with_unknown_coverage_does_not_make_new_buyer_may_qualify` | `OPUS` remains in `decision.may_qualify` | Passes for closed and retired plans |
| Vocabulary lacks availability | `test_vocabulary_lists_availability_facet_and_sourced_plan_value` | `KeyError: 'plan_facets'` | Descriptor and known plan value are published; absent values remain absent |
| Subscription-only vendor and plan-price routes remain usable | `test_subscription_only_vendor_does_not_route_new_buyer_through_unavailable_plan`, `test_closed_plan_price_cannot_satisfy_new_buyers_monthly_price_filter` | Bare vendor rows or a priced closed-plan result remain | Passes |
| Bounded answers discard the exclusion reason | `test_bounded_worker_answer_keeps_plan_exclusion_reason` | `KeyError: 'excluded_plans'`; exit 1, `1 failed, 26 deselected in 0.63s` | Reason is retained |
| Drill-down cannot trim retired-holding exclusions | `test_drill_down_counts_held_plan_exclusions_removed_to_fit_budget` | `SpecError: the reporting essentials exceed the drill-down byte budget`; exit 1, `1 failed, 28 deselected in 0.80s` | Exclusions are trimmed whole and counted; the response fits the drill-down budget |
| Reader cannot read explicit availability | `test_reader_reads_explicit_plan_availability` | Initial reader run: exit 1, `10 failed, 10 passed in 0.36s` | Explicit open, existing-only and retired statements pass |
| Reader carries scope into sibling sections or tables | `test_reader_never_guesses_availability_or_uses_a_sibling_plan` | Section run: `3 failed, 20 passed`; table run: `1 failed, 23 passed` | Sibling statements, stale table headings, negated and future retirement produce no reading |
| Availability-only acceptance changes unrelated verification | `test_availability_only_page_keeps_other_subscription_claims_skipped` | `mismatch` instead of `skipped`; exit 1, `3 failed, 24 passed in 0.43s` | Existing price, period and allowance checks remain skipped |
| Questions and bare siblings falsely verify retirement | `test_reader_never_guesses_availability_or_uses_a_sibling_plan`, `test_reader_does_not_inherit_retirement_from_an_unpriced_bare_sibling` | Exit 1, `5 failed, 13 passed, 14 deselected in 0.19s` | Exit 0, `18 passed, 14 deselected in 0.21s`; question marks are checked before normalization and ambiguous bare sections end the target scope |

Absent and explicit unknown availability already preserved the previous
routes in the base tests. They remain green. The existing no-access decision
goldens also pass. The decision-link helper asserts that the emitted contract
is 2.18 and changes exactly one compact version value to 2.17 before hashing.
All other bytes and the original main hashes remain checked. MODEL-339's two
bounded hashes arrived with main and were preserved.

The display-vocabulary cases each failed before their respective edits:

| Selection in `tests/test_compact_vocabulary.py` | Red, exit 1 | Green, exit 0 |
| --- | --- | --- |
| `subscription_availability_resolves_by_its_exact_estate_facet_id` | `2 failed, 24 deselected in 0.55s` | `2 passed, 24 deselected in 0.57s` |
| `trim_preserves_subscription_availability_without_other_plan_facts` | `1 failed, 26 deselected in 0.51s` | `1 passed, 26 deselected in 0.54s` |
| `compact_estate_plan_search_discloses_only_known_availability` | `1 failed, 27 deselected in 0.54s` | `1 passed, 27 deselected in 0.72s` |
| `plain_compact_estate_lists_the_subscription_availability_facet` | `1 failed, 28 deselected in 0.90s` | `1 passed, 28 deselected in 1.17s` |

Final availability suite: exit 0, `29 passed in 0.78s`.
Initial reader and existing verifier suite: exit 0, `421 passed in 2.11s`.
Final reader and existing verifier suite after the two audit findings and main
merge: exit 0, `426 passed in 1.12s`.
Display vocabulary and vocabulary-search suites: exit 0, `96 passed in 7.23s`.
Combined focused suite before the final drill-down edge case: exit 0,
`922 passed in 43.09s`. The subsequent bounded cases passed with exit 0,
`3 passed, 26 deselected in 0.64s`.

MCP typecheck passed with exit 0. The first MCP run exposed two stale 2.17
assertions and the changed tool-description snapshot: exit 1,
`3 failed, 163 passed`. The synchronized suite passed with exit 0,
`166 passed` across 9 files. The unnecessary availability sentence in the
agent guide was then removed. Regeneration restored the original tool
description snapshot, and the final merged MCP run passed with exit 0,
`166 passed` across 9 files in 1.07s. No MCP snapshot diff remains.

The registry and decision-link synchronization passed with exit 0,
`132 passed in 14.44s`. QA copy checks after restoring the original wording
passed with exit 0, `275 passed in 56.39s`. The post-merge registry, link,
bounded, pick, architecture and contract checks passed with exit 0,
`477 passed in 46.09s`. Schema, OpenAPI and agent-copy checks exited 0.

The final required full suite at `68ef6bb6` exited **1**:
`15 failed, 10515 passed, 23 skipped, 11 warnings in 1374.54s (0:22:54)`.
Thirteen failures are the generated decision/vocabulary page fixtures that
still expect 2.17 responses or the vocabulary without `estate.plan_facets`.
Two failures are social card builds whose Node process cannot import
`@playwright/test`. No engine, reader, registry, contract, bounded or MCP
test failed. The scope extension remains necessary for the strict live
decoder even after the page fixtures are regenerated.

After this run, the final delivery merge incorporated MODEL-383 at `3e7003d7`.
It changed only site/date code, its tests and its evidence; the MODEL-384
implementation and contract did not change. Focused site checks after this
merge exited 0: `68 passed, 12 skipped in 163.59s (0:02:43)`.
Schema, OpenAPI and agent-copy checks also exited 0 after the merge.
The full suite was not rerun after that merge or this
evidence-only commit.

The earlier clean full run at `f7a53a5d` exited 1:
`84 failed, 10433 passed, 23 skipped, 11 warnings in 1292.91s (0:21:32)`.
Its 48 QA copy-guard failures came from the unnecessary guide sentence;
removing that sentence restored the guards without editing their expected
copy. One registry count failure and 20 decision-link failures were fixed
while preserving the old response hashes apart from asserted version metadata.
Thirteen page fixture failures require the scope extension above. Two social
card failures reported missing `@playwright/test` in the uninstalled web
dependencies.

An earlier full invocation is invalid evidence. The archived red-test base
was accidentally left under pytest's discovery root, so pytest imported its
old decision package and collected archived tests. That invocation exited 1:
`280 failed, 9930 passed, 23 skipped, 63 errors, 11 warnings in 1590.57s`.
The archive was removed before either clean full run. This invalid run is
recorded as an executor error, not a product regression.

## Commands and versions

All Python commands used `/Users/terbeest/dev/modelspec/.venv/bin/python` in
this worktree with `TZ=UTC` and `PYTHONPATH=$PWD`, apart from the archived
baseline run described below. Root executor test runs saved scratch logs and
the shell saved `$?` immediately, then exited with that status after displaying
the log. Reader runs saved subprocess output and read its return code. Display
vocabulary runs read exit codes directly from the command tool's result.
No output pipe determined success.

```sh
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_subscription_availability.py
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_subscription_availability.py -k bounded
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_subscription_availability.py -k drill_down
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_subscription_availability.py -k 'drill_down or bounded'
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_subscription_availability_reader.py
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_subscription_availability_reader.py tests/test_decision_verify.py
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_subscription_availability_reader.py -k 'never_guesses or unpriced_bare_sibling'
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_compact_vocabulary.py tests/test_vocabulary_search.py
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_compact_vocabulary.py -k subscription_availability_resolves_by_its_exact_estate_facet_id
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_compact_vocabulary.py -k trim_preserves_subscription_availability_without_other_plan_facts
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_compact_vocabulary.py -k compact_estate_plan_search_discloses_only_known_availability
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_compact_vocabulary.py -k plain_compact_estate_lists_the_subscription_availability_facet
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_subscription_availability.py tests/test_subscription_availability_reader.py tests/test_decision_plans.py tests/test_decision_estate.py tests/test_decision_vocabulary.py tests/test_decision_contract.py tests/test_decide_bounded.py tests/test_compact_vocabulary.py tests/test_decision_verify.py
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m decision.schema
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.decide_budget
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python qa/contracts.py
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m decision.schema --check
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy check
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_registry.py tests/test_decision_link.py
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_ablation.py tests/test_ablation_targets.py tests/test_ablation_proxy.py
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_registry.py tests/test_decision_link.py tests/test_decide_bounded.py tests/test_bounded_pick.py tests/test_architecture_facts.py tests/test_decision_contract.py
TZ=UTC PYTHONPATH=$PWD PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile tests/test_pipeline.py tests/test_landing.py
```

The final regression file was rerun against base-revision `decision`,
`registry`, `hardware`, `tests/plan_records.py`, `tests/snapshot_records.py`
and `tests/__init__.py`, extracted with `git archive` into worktree-local
scratch. Its subprocess command was:

```sh
TZ=UTC PYTHONPATH=/Users/terbeest/dev/worktrees/model-384/docs/evidence/g2-ios/model-384-root/baseline:/Users/terbeest/dev/worktrees/model-384 /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_subscription_availability.py -k 'not bounded and not drill_down'
```

That subprocess ran from the archived root, with the final regression file
copied into its tests directory. The implementation checkout was never
switched or overwritten to perform this reproduction.

From `mcp/`, all Node commands prepended
`/Users/terbeest/.nvm/versions/node/v22.22.3/bin` to `PATH`:

```sh
npm ci --no-audit --no-fund
npm run typecheck
npm test
npm test -- --update
npm run typecheck
npm test
```

Observed versions: Python 3.14.4; pytest 9.1.1; pytest-xdist 3.8.0;
pydantic 2.13.5; PyYAML 6.0.3; Node v22.22.3; npm 10.9.8; Vitest 5.0.1;
git 2.50.1; gh 2.102.0. Version commands were `python --version`,
`python -m pytest --version`, `git --version`, `gh --version`, `node --version`,
`npm --version`, and `importlib.metadata.version` for the Python packages.

The branch was fetched and merged with `git fetch origin && git merge
origin/main`; the first invocation reported `Already up to date.` at the
supplied base revision. The required delivery invocation merged
`0b4bab44` through merge commit `3e1a37f2`. MODEL-339 bounded 1.3 and MODEL-348
documentation were preserved. Contract/version conflicts were combined as
complete 2.18 and bounded 1.3; generated files were rebuilt from the combined
source. The historical MODEL-378 paragraph keeps main's original 2.16/1.2
version statement.
The final fetch/merge brought in `3e7003d7` without conflicts, through
`ec145f41`. Every executor commit, including both merge commits, ends with
the required Codex co-author footer.
The required overload wait was `sleep 120 && uptime`.

## Observations and limits

Tests exercised the decision engine, synthetic signed snapshots, the local
Worker entry point, vocabulary lookup and the MCP server. They cover provider
fallback, exhaustion, unknown facts, plan-only vendor rows, monthly-price
filtering, ordinary bounded answers and drill-down byte budgets.

No live vendor page, private curated data, deployed Worker or live subscription
was observed. The reader cases use synthetic published wording. No availability
facts were added to the frozen public data. New facts belong in
`modelspec-data`; engine routing changes only when the snapshot carries them.
No production switch or ranking floor changed. No paid-provider, device or
upload call, WSL gate, SSH, SCP, Linear write or PR merge was performed.
Cross-model review remains pending on the draft PR.
