# MODEL-390 exact operative-sentence redesign

The orchestrator's second design decision replaces corpus-wide licence patterns
with exact operative-sentence templates. The reader no longer interprets grantor
slots, nearby conditions, competition words, or negation/repeal vocabulary.
Six sentence hashes in four source families are seeded from the retained private
data PR #80 snapshots. No retained legal text is committed.

## Revisions and scope

Reviewed base SHA: `4437f35eb7e6649366ad90f0ba4fe893d5c279fb`.
Verified implementation SHA: `012c690b93cde331345ae4c59d92b25239da042f`.
The final delivery SHA is the commit containing this record, reproducible with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-390-engine-sentences-fix.md`.
The final execution marker and PR response record that delivery SHA.

The executor read both REV-747 verdicts in full, reread AGENTS.md and CLAUDE.md,
and inspected the retained governing sentences offline. Work remains in
`/Users/terbeest/dev/worktrees/model-390-engine`, branch
`sparksandsawdust/model-390-licence-readers`. The Graphify query does not cover
these symbols. No CodeGraph index or new subagent was created.

## Registry and matcher

`LicenceSentenceTemplate` records the source family, exact source URL,
normalized cited-region SHA-256, normalized sentence SHA-256, facet, value, and
a short paraphrase label. The six records in `decision/verify.py` cover:

| Family | Templates | Supported readings |
| --- | ---: | --- |
| Gemini API terms | 1 | Grounded-search output-training restriction |
| OpenAI Services Agreement | 2 | Customer access under the agreement; competing-model output limits |
| TypeSafe Master Customer Agreement | 2 | Conditional customer/API licence; output distillation and imitation limits |
| Meta API terms | 1 | Conditional integrated-product grant |

The public registry holds hashes and labels, including for the long complete
operative sentences. It holds no whole licence or private clause text.
The seed script uses curator-selected sentence positions in data revision
`4bc5f4cfa9c1f29689aaf3142be22cabc44454db`. It checks that revision and a clean
data checkout, verifies retained byte hashes, blocks socket operations, and
prints only registry metadata. Repeating it reproduces all six rows exactly.
It does not choose readings using phrase searches or the collector's values.

`normalise_licence_sentence` collapses whitespace, canonicalizes quote forms,
and case-folds. It retains punctuation. `licence_sentences` preserves sentence
terminators, including question marks. The matcher compares complete candidate
sentence hashes; there are no partial or cross-sentence prose windows.
Block breaks are conservative candidate boundaries. Whitespace inside a
candidate normalizes; a layout reflow that changes those boundaries can lose
a reading even when the normalized region hash remains the same.

A matching sentence must also occur at its registered source URL in the reviewed
normalized cited region. This additional context hash makes an inserted ban,
repeal, example marker, or other substantive edit unread without trying to
interpret the new wording. It prevents an unchanged grant sentence from becoming
a reading after its governing context changes. Whitespace, case, and quote-form
changes remain equivalent. Unregistered sentences never supply conditions or
prohibition prefixes to another sentence.

The numeric MAU separate-agreement rule remains a full match. It requires the
entire cited region to be the operative statement ending in a period, so a
question, example introduction, exception, or additional context skips. The
number scale and published unit are read independently of the claim. No prose
absence or unregistered unbounded statement becomes a cap reading.

The actor method is now `licence-terms@2`. Source-kind permissions, the decision
contract range, model binding, and canonical Apache operative-body acceptance
remain unchanged. Source URLs are passed into reader selection only for licence
claims; unrelated extractors keep their existing selection behavior.

The registry intentionally does not seed the Gemini audience description,
Voxell ownership/privacy statements, TypeSafe's services-modification ban,
or Meta's output-training list fragment without its separate prohibition header.
Those words do not independently state the claimed value. Gemma 4's actual
Apache source continues through the canonical reader. No synthetic test clause
is included in the production registry.

## Red-first and regression results

The new REV-747b probes were run on the reviewed implementation before the
redesign. Result: **27 failed, one passed, 126 deselected**, exit 1, in 0.81 seconds.
Each failure expected `skipped` and observed `verified`.

| Finding | Negative tests |
| --- | --- |
| Denied or hypothetical grantors | `test_review747b_denied_and_subordinate_limited_grants_remain_unread`, `test_review747b_denied_or_hypothetical_access_with_integration_remains_unread` |
| Commercial ban synonyms | `test_review747b_commercial_bans_are_not_permissions` |
| Repealed or void prohibition | `test_review747b_repealed_prohibitions_remain_unread` |
| Questions treated as statements | `test_review747b_questions_are_not_operative_statements` |
| Illustrative or false context | `test_review747b_nonoperative_context_does_not_prove_a_value` |

Both verdicts' earlier negative probes remain in the module. The re-review's
previously held training, modification, cap, grant, and integration probes are
also explicit negative fixtures. Old synthetic positive clauses were retained
as unregistered negatives under the new design. Existing canonical and numeric
cap positives remain. Positive exact-template coverage uses a separate injected
synthetic registry at the public `verify.verify` boundary, never production seeds.
It verifies literal rights and checks mismatches against different literal values.

The exact-template tests cover equivalent spacing, case and quotes, and one-word
`not`, `except`, or `if` insertions. For the mutation tests, even approving the
changed synthetic region leaves the original sentence hash unmatched. Question
tests do the same to prove punctuation is preserved independently of the context
guard. Other tests cover added bans, repeals, nonoperative prefixes, source-family
borrowing, binding, source kinds, and conflicting registered values.

All **228 clause tests pass**, exit 0, in 0.56 seconds. The final focused suites
report **861 passed**, exit 0, in 38.58 seconds. The earlier focused run before
adding the previously held probes reports 838 passed, exit 0, in 45.02 seconds.

During construction, a test used `dataclasses.replace` on a named tuple, causing
18 TypeErrors. Three tests also expected a source-kind mismatch for a known
value, whereas the existing API skips that case. These were corrected to named
tuple replacement and the existing literal `skipped` outcome. They are test
construction errors, not red-first evidence. Source-kind mismatches for absence
claims and model-binding mismatches remain covered. The old unregistered-positive
expectations initially fail during migration, then become explicit negatives.

## Offline recheck

[The aggregate](MODEL-390-engine-sentences-recheck.json) comes from the unchanged
offline helper against `/tmp/d390`, data SHA
`4bc5f4cfa9c1f29689aaf3142be22cabc44454db`. The engine pin remains
`60c26c623f2fd3b1be1ca7dbedf75dde9d7d77fa`. Actual `verify`, fidelity,
collection, and snapshot-building calls run; new verification records are
overlaid in memory. No data files or historical logs are edited.

The 64 licence facts give **37 verified, 17 skipped, two model-binding mismatches,
and eight facts without a governing snapshot**. Source-kind mismatches, unknown
source kinds, unreachable cited copies, network calls, and completion calls are
zero. The two mismatches concern Meta commercial-use facts and the unchanged
relative-link binding issue. Binding rules are not relaxed.

Across the 56 cited facts, fidelity reports 37 verified and 19 undetermined,
zero mismatches and zero unreachable. Its generic status is `pass`; this does
not establish complete ticket coverage. The helper exits 1 because unresolved
facts and the premier gate remain. Go verifies.

The stored premier gate fails with 31 gaps. With current reader outcomes
overlaid, it fails with **26 gaps**: five commercial, eight fine-tuning, five
output-training, and eight user-cap facts. Historical keys remain in the overlay
when a reread skips; they do not establish a new governing-text reading. Tracked
and untracked data status are unchanged. Only aggregate results are committed.

## Commands and full verification

Python 3.14.4, pytest 9.1.1, Ruff 0.16.6 from the repo environment, Node 22.22.3.
Process exit codes are checked directly, with no pipeline hiding a test status.

```sh
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py -k review747b > /tmp/model-390-sentences-red.log 2>&1
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py -k review747 > /tmp/model-390-sentences-probes.log 2>&1
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -B docs/evidence/g2-ios/MODEL-390-engine-sentence-seeds.py --data /tmp/d390 > /tmp/model-390-sentence-templates-final.json

PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py tests/test_decision_verify.py tests/test_decision_registry.py tests/test_licence_coverage.py tests/test_decision_sources.py tests/test_model_345_collect.py tests/test_decision_model.py > /tmp/model-390-sentences-focused-final.log 2>&1

PYTHONDONTWRITEBYTECODE=1 MODELSPEC_DATA_DIR=/tmp/d390 MODELSPEC_REQUIRE_DATA_DIR=1 TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -B docs/evidence/g2-ios/MODEL-390-engine-recheck.py --data /tmp/d390 > /tmp/model-390-sentences-recheck.json

PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile > /tmp/model-390-sentences-full.log 2>&1
/Users/terbeest/dev/modelspec/.venv/bin/ruff check tests/test_model_390_licence_readers.py docs/evidence/g2-ios/MODEL-390-engine-sentence-seeds.py
git diff --check
```

Full suite: **10760 passed, nine skipped, 11 warnings**, exit 0,
in 1233.38 seconds, or 20 minutes 33 seconds.
The browser dependencies and built assets remain present from the initial
execution. No browser environment repair was needed for this run.
Ruff comparison against the reviewed SHA finds eight inherited findings in the
two changed Python files, eight current findings, zero introduced findings,
exit 0. The test module and new seed helper pass Ruff. Initial import ordering
and long-line errors were corrected. The source-line/code comparator is recorded
in the initial execution evidence, with this reviewed SHA and the two files as
its inputs. Registry rows reproduce byte-equivalent metadata from the seed script.

## Delivery and limitations

After verification, normal push and the authorized PR comment use:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH CI_LOCAL_SKIP=1 git push
gh pr comment 747 -R turbobeest/modelspec --body-file /tmp/model-390-sentences-comment.md
gh pr view 747 -R turbobeest/modelspec --json number,url,isDraft,headRefOid,state
```

PR #747 remains a draft. No merge, ready-state action, Linear write, private-data
edit, pin edit, production switch, ranking-floor change, published legal-text
edit, workflow change, paid API call, WSL gate, SSH, or tmux action is performed.
No complete data gate or production behavior is claimed. All executor-started
command processes finish before delivery. Earlier evidence remains historical.
