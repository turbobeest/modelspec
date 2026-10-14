# MODEL-384 execution evidence

Base SHA: `56c39ac3a826af6f79f8755c49ed52b68bad37c4`.
Initial delivery SHA: `365627fbcb7ffc63afe42261ac42c8eb8251f358`.
Decoder-follow-up implementation SHA: `016c57d00003fe519982f947eab69302da77398c`, before its evidence commits.
Decoder-follow-up full-suite SHA: `37ae52fe5ce9a9ec5a3dc993c80b5d211f1b07cd`.
MODEL-381 merge source: `e078f6562ce69099724a025a05b4016e8a1e5e4d`.
Resolved merge and latest full-suite SHA: `55ffdfb59d1df9e9b5b3bab3de980b190f9f56b6`.
The final delivery SHA is the commit containing this file. Resolve it with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-384-fix.md`.

The latest follow-up merges MODEL-381's router configuration with MODEL-384.
Complete contract remains 2.18. Bounded advances from main's 1.4 to 1.5 under
the orchestrator's explicit exception: main lacks `excluded_plans`,
`with_estate.excluded_plans` and
`with_estate.results[].estate.availability`. These optional fields reach
bounded responses, so the combined representation adds fields to 1.4.
Existing ranges remain unchanged. The merge preserves `router_config`,
`pick`, intact configuration text, budget refusals and availability trimming.
The web decoder is unchanged from the approved decoder follow-up.

The orchestrator authorized the decoder, its tests and current generated web
fixtures on 2026-10-14. That original scope boundary is resolved. The decoder
now accepts complete 2.18 while retaining every previously supported version,
including 2.17. It strictly validates optional `excluded_plans` at both answer
levels and the nullable/optional holding availability enum. Existing strict
object schemas remain strict; no unknown-field catch-all was added.

A local probe identified a separate, pre-existing estate heading bug: the
estate answer names Opus and Sonnet, but the heading names the unrestricted
band leader `other/huge`. A paired probe of 2.18 with the new fields and 2.17
without them produces identical headings and held-plan routes. The current
page displays neither exclusion reasons nor holding availability; its
"included in your plan" text remains truthful for a closed plan's existing
holder. It displays no inappropriate new-buyer exclusion reason to that
holder. This does not block the authorized decoder follow-up.

A separate rendering scope request was sent for
`web/src/decide/facet-board/routes.ts` and `web/src/decide/App.tsx`; it remains
unanswered. Those files were not changed. The heading bug is reported for
separate work. The executor brief says: "If you need a file outside them,
stop and report it."

The engine now reads the sourced `offering.subscription.availability` fact.
Unrestricted routes exclude `existing_subscribers_only` and `retired`; held
plans can use the former, and nobody can use the latter. Prospective estate
gains never suggest buying either unavailable plan. Availability checks run
before unknown coverage or surfaces can admit a candidate.

Complete contract 2.17 becomes 2.18. New optional fields are
`Decision.excluded_plans`, `WithEstate.excluded_plans` and
`EstateMark.availability`. Exclusions contain a plan ID and a reason. Ranked
holders of a closed plan receive its availability and a sentence in
`with_estate.gap.summary`. The initial bounded 1.3 implementation added
optional exclusions and projected 2.18; the latest merge records these
additions as bounded 1.5 after main's 1.4. Main's MODEL-339 bounded 1.3,
optional `pick` and withheld tie-breakers were preserved during the required
merge. Unknown availability adds no
availability field and preserves existing routes.

The vocabulary publishes the record-only facet under `estate.plan_facets`
and known values under `estate.plans[].availability`. Exact facet lookup,
compact search and the display projection retain these additions. The
deterministic reader accepts explicit plan-scoped statements and labelled
table cells. Other subscription fields retain their previous reader dispatch.

## MODEL-381 merge follow-up

The orchestrator reported cross-model approval of PR #742 and explicitly
authorized resolving its conflicts with main, regenerating artifacts,
verifying the combined branch and commenting on the PR. Its draft state was
`true` before this follow-up. No ready/draft action was taken.

`git fetch origin && git merge origin/main` exited 1 because ten files
conflicted. Main was `e078f6562ce69099724a025a05b4016e8a1e5e4d`; branch HEAD
was `ff3e62c180f6bb1ad7f644052903c1a88c92e4fc`. The resolution preserves both
parents through merge commit `55ffdfb59d1df9e9b5b3bab3de980b190f9f56b6`.
Version conflicts keep complete 2.18. Generated conflicts were regenerated
from the combined source. Router rendering and both intact-config budget
refusals match main; availability projection and whole-record trimming match
the approved branch. The web decoder is unchanged.

The bounded version is **1.5**. Direct comparison of main's schema and
source shows that 1.4 includes `router_config` but lacks top-level
`excluded_plans`, estate `excluded_plans` and holding `availability`.
MODEL-384 adds those optional bounded fields, so the orchestrator's explicit
exception requires an additive minor bump. Existing field ranges are
unchanged. Both Python's version constant and literal schema and MCP's
current-version constant are 1.5, with `projects_contract: "2.18"`.
The MODEL-381 1.4 history remains in the documentation.

Red-first version check:
`test_bounded_worker_answer_keeps_plan_exclusion_reason` now also checks
bounded identity, 1.5 and projection of 2.18. Before the version update it
exited 1, `1 failed, 28 deselected in 0.37s`, with `assert '1.4' == '1.5'`.
After the update it exited 0, `1 passed, 28 deselected in 0.34s`.
Decision-link hash tests assert the live 2.18/1.5 metadata, then normalize
exactly those version values to main's 2.17/1.4 before checking the original
main hashes. All remaining bytes retain their hash protection.

Schema, OpenAPI, agent copy, the MCP budget fixture and MCP tool fixtures
were regenerated; all commands exited 0. Schema and OpenAPI checks also
exited 0. The documented web writer exited 0, `13 passed in 0.45s`, and
produced no committed diffs because those fixtures were already current.
The ignored corpus was regenerated with exit 0 in 39.76s: 319 decisions,
five vocabularies and an index. All 286 answered decisions and all five
vocabularies use complete 2.18; this corpus contains no bounded responses.

MCP `npm ci` exited 0, adding 236 packages. Typecheck exited 0. `npm test`
exited 0, `166 passed` across nine files in 955ms. Web `npm ci` exited 0,
adding 346 packages. Build exited 0; the existing unresolved font-reference
warnings remain. Web `npm test` exited 0, `1236 passed` across 52 files in
18.51s. Focused Python checks exited 0, `520 passed, 3 skipped in 38.09s`.
Full pytest with the built web app at `55ffdfb5` exited **0**:
`10598 passed, 9 skipped, 11 warnings in 1138.50s (0:18:58)`.
Only the evidence changed after this validation revision. All started
generator and test processes completed and their final statuses were read.

Exact commands, from the worktree root unless a directory is specified:

```sh
git fetch origin && git merge origin/main
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_subscription_availability.py -k bounded_worker
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m decision.schema
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.decide_budget
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python qa/contracts.py
MODELSPEC_WRITE_FIXTURES=1 TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decide_page_fixtures.py
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m tests.corpus decisions --out web/src/decide/__corpus__
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m decision.schema --check
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
TZ=UTC PYTHONPATH=$PWD PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_subscription_availability.py tests/test_decide_bounded.py tests/test_bounded_pick.py tests/test_decision_contract.py tests/test_architecture_facts.py tests/test_keyed_router_worker.py tests/test_keyed_router_cli.py tests/test_decision_link.py tests/test_api_docs.py
TZ=UTC PYTHONPATH=$PWD PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

From `mcp/`, with Node 22 on PATH:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm run typecheck
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test
```

From `web/`:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm ci --no-audit --no-fund
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=/Users/terbeest/dev/worktrees/model-384 npm run build
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test
```

Each test exit was read directly from the process return code. The root
shell saved `$?` immediately before displaying its log. No output pipe
determined success. Tool versions match the earlier recorded versions.
No live vendor, deployment, private-data or paid-provider observation was
added by this follow-up.


## Red and green results

The follow-up decoder regression file is
`web/src/decide/__tests__/contract-availability.test.ts`. Before the decoder
edit, its positive 2.18 cases failed: exit 1, `6 failed, 6 passed` in 650ms.
The failures cover the 2.18 version, both exclusion arrays, and the holding's
three enum values and null. The same suite passed after the edit: exit 0,
`12 passed` in 457ms. Two additional malformed-ID cases check the contract's
one-to-120-character constraint. The final web suite includes all 14 cases.
The deliberate older-version tests remain; no compatibility case was replaced
with a current-version assertion.

Current web fixtures were regenerated with their documented writer: exit 0,
`13 passed in 0.53s`. Exactly 13 committed fixtures changed. Historical live
captures, older sample decisions and `ui-specs.json` remain byte-identical to
the initial delivery. The ignored corpus was also regenerated locally: exit
0 in 44.10s, 319 decisions, five vocabularies and an index. The generated
current-engine answers use contract 2.18.

`npm ci` exited 0 and installed 346 packages. `npm run build` exited 0.
The first full web suite exposed two remaining current-fixture assertions
expecting 2.17: exit 1, `2 failed, 1234 passed` across 52 files in 20.79s.
Only those version assertions were changed. The final `npm test` exited 0:
`1236 passed` across 52 files in 19.04s, including the generated corpus.
All non-web generators ran again, and their outputs had no additional real
diffs. Schema, OpenAPI and agent-copy checks exited 0.

Follow-up full pytest at `37ae52f`, with the built web app, exited **0**:
`10547 passed, 8 skipped, 11 warnings in 1243.34s (0:20:43)`.
The previous 13 stale-fixture and two missing-Playwright-package failures are
resolved. The skipped count fell from 23 to eight with the web build present.
After that run, main advanced to MODEL-385's jurisdiction-reader fix at
`60c26c62`. It merged without conflicts through `016c57d0`. The subscription
reader and web changes were preserved. Post-merge verification exited 0:
`468 passed, 1 skipped in 12.56s` across jurisdiction, subscription-availability
reader and general verifier tests. Generated schema, OpenAPI and agent-copy
checks also exited 0. The full suite was not rerun after that reader-only
merge or this evidence-only commit.

The earlier execution results below are retained as history. The original
decoder/fixture failures no longer describe the follow-up implementation.

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
test failed. At the initial delivery, the scope extension was necessary for
the strict live decoder even after regenerating the page fixtures.

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
Thirteen page fixture failures required the scope extension above. Two social
card failures reported missing `@playwright/test` in the uninstalled web
dependencies.

An earlier full invocation is invalid evidence. The archived red-test base
was accidentally left under pytest's discovery root, so pytest imported its
old decision package and collected archived tests. That invocation exited 1:
`280 failed, 9930 passed, 23 skipped, 63 errors, 11 warnings in 1590.57s`.
The archive was removed before either clean full run. This invalid run is
recorded as an executor error, not a product regression.

## Follow-up commands

The follow-up began with `git fetch origin && git merge --no-commit
origin/main`, which reported `Already up to date.`. The user explicitly
authorized updating PR #742's body, overriding the original brief's ban on
`gh pr edit` for that action only. The PR remains a draft.

From `web/`, with Node 22 on `PATH`:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm ci --no-audit --no-fund
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test -- src/decide/__tests__/contract-availability.test.ts
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=/Users/terbeest/dev/worktrees/model-384 npm run build
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test
```

From the worktree root:

```sh
MODELSPEC_WRITE_FIXTURES=1 TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decide_page_fixtures.py
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m tests.corpus decisions --out web/src/decide/__corpus__
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m decision.schema
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.decide_budget
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python qa/contracts.py
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m decision.schema --check
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy check
TZ=UTC PYTHONPATH=$PWD PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_lab_jurisdiction.py tests/test_decision_verify.py tests/test_subscription_availability_reader.py
```

The running adapter probe uses Vite's local SSR loader and closes the server
in `finally`. Its first two attempts used the legacy benchmark view without
matching benchmark evidence; their errors were setup errors, not rendering
defects. The corrected probe sets `boardWeights: {}` to select the actual
facet-board view. It constructs a validated 2.18 decision from the generated
coding and band fixtures, makes `other/huge` the unrestricted band leader,
and marks the held Max plan `existing_subscribers_only`. It calls the real
`estateAsDecision`, `mapDecisionToViewModel`, `leadingModels` and
`estateRouteView` functions. The output is:

```json
{
  "estate_answer": ["anthropic/claude-opus-5-5", "anthropic/claude-sonnet-5"],
  "rendered_heading_models": ["other/huge"],
  "inherited_new_buyer_exclusions": [{
    "plan": "anthropic/subscription/max-20x",
    "reason": "Claude Max 20x is closed to new buyers; only existing subscribers can use it."
  }],
  "held_plan_route": {
    "figure": "included in your plan",
    "column": "$0 per task"
  }
}
```

The held route has no availability note, and its explanation has no closure
label. The same displayed route and heading occur after decoding the equivalent
2.17 decision with both exclusion fields and holding availability removed.
The paired comparison exits 0 and prints `availability_metadata_changes_display: false`.
Thus the heading bug predates the new fields, and "included in your
plan" remains truthful for an existing subscriber. This is a local module
probe using synthetic fixtures, not a browser observation or a live API call.
The final probe exited 0 and closed its server. Its exact successful command,
run from `web/`, is:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH node --input-type=module <<'JS'
import { readFileSync } from 'node:fs';
import { createServer } from 'vite';
const server = await createServer({ configFile: 'vitest.config.ts', server: { watch: null } });
try {
  const { decisionSchema } = await server.ssrLoadModule('/src/decide/adapter/contract.ts');
  const { estateAsDecision, estateRouteView } = await server.ssrLoadModule('/src/decide/facet-board/routes.ts');
  const { leadingModels } = await server.ssrLoadModule('/src/decide/facet-board/leading.ts');
  const { mapDecisionToViewModel } = await server.ssrLoadModule('/src/decide/adapter/view-model.ts');
  const { baseSpec } = await server.ssrLoadModule('/src/decide/state/spec.ts');
  const { planVocabulary } = await server.ssrLoadModule('/src/decide/__tests__/plan-vocabulary.ts');
  const read = name => JSON.parse(readFileSync('src/decide/__fixtures__/' + name + '.json', 'utf8'));
  const coding = read('plans-coding-full');
  const banded = read('compact-bands-full');
  const best = coding.results.find(row => row.offering.model === 'other/huge');
  const band = banded.bands?.best[0];
  if (!best || !band) throw new Error('Expected unrestricted leader fixtures');
  const decision = decisionSchema.parse({ ...coding,
    results: coding.results.map(row => ({ ...row, plans: row.plans?.filter(plan => plan.plan !== 'anthropic/subscription/max-20x') })),
    bands: { ...banded.bands, leader: 'other/huge', best: [{ ...band, model: 'other/huge', offering: best.offering }], rest: [], thin: [] },
    excluded_plans: [{ plan: 'anthropic/subscription/max-20x', reason: 'Claude Max 20x is closed to new buyers; only existing subscribers can use it.' }],
    with_estate: { ...coding.with_estate, results: coding.with_estate.results.map(row => ({ ...row, estate: { ...row.estate, availability: 'existing_subscribers_only' } })) },
  });
  const held = estateAsDecision(decision);
  if (!held) throw new Error('Expected an estate view');
  const view = mapDecisionToViewModel(held.decision, { ...baseSpec, boardWeights: {} }, { axis: 'task$', dismissed: [] });
  const row = decision.with_estate.results[0];
  if (!row) throw new Error('Expected a held plan result');
  process.stdout.write(JSON.stringify({ estate_answer: decision.with_estate.answer.members, rendered_heading_models: leadingModels(view), inherited_new_buyer_exclusions: held.decision.excluded_plans, held_plan_route: estateRouteView({ vocabulary: planVocabulary }, row.estate, undefined, row.offering) }, null, 2) + '\n');
  const legacy = structuredClone(decision);
  legacy.contract_version = '2.17';
  delete legacy.excluded_plans;
  delete legacy.with_estate.excluded_plans;
  for (const result of legacy.with_estate.results) delete result.estate.availability;
  const previous = decisionSchema.parse(legacy);
  const previousHeld = estateAsDecision(previous);
  if (!previousHeld) throw new Error('Expected the 2.17 estate view');
  const previousView = mapDecisionToViewModel(previousHeld.decision, { ...baseSpec, boardWeights: {} }, { axis: 'task$', dismissed: [] });
  const previousRow = previous.with_estate.results[0];
  if (!previousRow) throw new Error('Expected the 2.17 held plan result');
  const currentDisplay = { heading: leadingModels(view), route: estateRouteView({ vocabulary: planVocabulary }, row.estate, undefined, row.offering) };
  const previousDisplay = { heading: leadingModels(previousView), route: estateRouteView({ vocabulary: planVocabulary }, previousRow.estate, undefined, previousRow.offering) };
  const changed = JSON.stringify(currentDisplay) !== JSON.stringify(previousDisplay);
  process.stdout.write(JSON.stringify({ availability_metadata_changes_display: changed }) + '\n');
  if (changed) throw new Error('Availability metadata changed the displayed estate result');
} finally { await server.close(); }
JS
```

Observed follow-up package versions from their installed `package.json`
files: Vite 8.0.3, Vitest 5.0.1, TypeScript 5.9.3 and Playwright 1.63.0.

## Initial commands and versions

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
The orchestrator reported cross-model approval before the MODEL-381 merge
follow-up. The PR's draft state is preserved.
