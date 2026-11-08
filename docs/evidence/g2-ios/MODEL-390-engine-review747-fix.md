# MODEL-390 engine review follow-up

The Grok review of draft PR #747 found false verifications from loose licence
patterns. The reader now requires complete clauses that state the right or
restriction. Coverage falls rather than inferring rights from nearby words.
The private data gate remains failing.

## Revisions

Reviewed base SHA: `952f409aa3d5514cb0cf157ba95a5f65028abd60`.
Verified implementation SHA: `19a679d4214aaf90599f4705b5534e50f0b38119`.
The first clause-tightening commit is `c2a9531e8b9e9a323fcfd21dca5514b659617e85`.
The final delivery SHA is the commit containing this record, reproducible with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-390-engine-review747-fix.md`.
The PR response and final execution marker report that full delivery SHA.

Worktree: `/Users/terbeest/dev/worktrees/model-390-engine`.
Branch: `sparksandsawdust/model-390-licence-readers`.
The full review was read from
`/Users/terbeest/.codex-g2/exec/REV-747.verdict.md`.
The executor also reread CLAUDE.md, AGENTS.md, CONTEXT.md, and the evidence rules.
There is no `.codegraph/` directory. The existing Graphify query did not cover
these symbols, so current source was read directly. No subagents were started
for this follow-up.

## Findings and red-first evidence

Tests use the public `verify.verify` boundary through the existing synthetic
`check` fixture. The initial negative-test run reports **32 failed, 86 passed**,
exit 1. Every failing negative expected `skipped` and observed `verified`.
The existing Gemma Services fine-tuning assertion was also corrected to expect
`skipped` and failed before implementation.

| Verdict finding | Regression tests | Resolution |
| --- | --- | --- |
| 1. Audience description and an inserted commercial ban | `test_review747_audience_descriptions_and_commercial_bans_do_not_grant_use` | Removed the audience pattern. Permission requires an explicit grant. Commercial bans can name the model weights or Services between "use" and "is prohibited/forbidden". |
| 2. Grant, condition, and API mention in unrelated clauses | `test_review747_grant_condition_and_application_permission_share_their_scope` | The condition must be inside the complete grant clause. API integration must itself be permitted within that clause or in the immediately following sentence. Descriptive API mentions, delayed permission, and negated permission skip. |
| 3. Services modification mistaken for model-weight rights | `test_review747_gemma_services_grant_does_not_grant_weight_modification`, `test_review747_gemma_model_grant_and_weight_ban_are_ambiguous` | Separated services and model grants. Fine-tuning permission requires "modify ... Gemma and Model Derivatives" and the explicit policy duty. A Gemma grant with an express weight-modification ban gives no fine-tuning reading. |
| 4. Unrelated competition colored a training action | `test_review747_competition_must_modify_the_model_being_trained` | Removed the 360-character search gap. The complete prohibited action must train, develop, or distill a competing model or models that compete with the provider's models. Sales competition, chess, unrelated list items, and competing products skip. |
| 5. Disclosure duty mistaken for a training prohibition | `test_review747_grounded_results_ban_must_prohibit_the_customer_training_act` | The prohibited act immediately after "to," must be training on or learning from the named results. Disclosure, reporting, claims, and revealing whether someone trains skip. |
| 6. Example threshold treated as an operative cap | `test_review747_example_cap_clauses_do_not_state_an_operative_cap` | Numeric and unbounded clauses skip when the preceding clause labels them an example, sample, or illustration. |
| 7. Appendix missing its copyright line | `test_review747_apache_appendix_requires_its_copyright_line` | An empty residual is accepted only without an appendix. A present appendix requires its recognized copyright line. The module self-check and retained-residual positive test no longer construct an accepted empty-holder appendix. |

The corpus-wide tightening also anchors prohibition-list headers, their complete
training actions, Gemma definitions and recipient duties, and grounded-results
clauses. The additional actor/action probes in
`test_review747_training_restrictions_require_an_operative_actor_and_action`
report **four failed, 118 deselected**, exit 1, before the change. These cover a
quoted false prohibition, a quoted incorrect grounded-results prohibition,
disclosure of training on Google Maps data, and a negated Gemma recipient duty.

`test_review747_negative_grant_subject_is_not_a_provider_permission` adds
"no provider grants" and "nobody grants". Both initially verify, yielding
**two failed, 122 deselected**, exit 1. They now skip. The same test then added "none of the providers" and "zero providers".
These initially verify, reporting **two failed, two passed, 122 deselected**,
exit 1. Blocking the negative quantifiers makes them skip. The final clause
module reports **126 passed**, exit 0, in 0.56 seconds. All prior safe clause positives
and negatives pass. The former audience-only positive was moved to the negative
fixtures. The former distillation/competing-product positive now explicitly
names a competing AI model; the product-only pattern is a negative fixture.

## Offline data recheck

The same committed socket-blocking helper runs against the same clean data
worktree `/tmp/d390`, revision
`4bc5f4cfa9c1f29689aaf3142be22cabc44454db`, and its unchanged engine pin
`60c26c623f2fd3b1be1ca7dbedf75dde9d7d77fa`.
It calls actual verification, fidelity, collection, and snapshot-building APIs
and retains new verification records only in memory. The output is first
written under `/tmp` so generating a tracked aggregate file cannot make the
engine checkout appear dirty during the check. Only aggregate JSON is then
copied into this repository.

[The new aggregate](MODEL-390-engine-review747-recheck.json) reports:

| Result | Reviewed implementation | Follow-up |
| --- | ---: | ---: |
| Verified licence facts | 38 | 32 |
| Skipped licence facts | 14 | 24 |
| Mismatches | 4 | 0 |
| Facts without a governing snapshot | 8 | 8 |
| Source-kind mismatches | 0 | 0 |
| Premier gaps with current readings overlaid | 25 | 31 |

The 64-fact check now has 32 verified, 24 skipped, zero mismatches, and eight
facts without a governing snapshot. The 56 cited facts give 32 verified and
24 undetermined in fidelity, with zero mismatches or unreachable copies. Its
generic fidelity status is `pass`, which does not mean the ticket is complete.
The helper exits 1 because verification completion and the premier gate fail.
The stored and overlaid premier gates both fail with 31 gaps: seven commercial,
eight fine-tuning, eight output-training, and eight user-cap facts. Go verifies.
Bindings and source-kind rules were not relaxed to remove mismatches. A missing
explicit reading now skips before any model-binding comparison can be made.
Historical records remain in the overlay when a current reading skips, as in
the first execution; the licence counts report current rereads separately.

Network calls, completion calls, unknown source kinds, and unreachable cited
copies are zero. Both tracked and untracked data status remain unchanged. No
private terms, fact rows, or verification logs are copied into this public repo.
The initial execution's aggregate and evidence remain as historical records.

## Verification and commands

Python 3.14.4, pytest 9.1.1, Ruff 0.16.6 in the repo environment,
Ruff 0.14.10 on the shell PATH, and Node 22.22.3.
All process exit codes are checked directly.

```sh
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py > /tmp/model-390-review747-red.log 2>&1
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py -k operative_actor > /tmp/model-390-review747-red-siblings.log 2>&1
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py -k negative_grant_subject > /tmp/model-390-review747-red-negation.log 2>&1
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py -k negative_grant_subject > /tmp/model-390-review747-red-quantifiers.log 2>&1
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py

PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py tests/test_decision_verify.py tests/test_decision_registry.py tests/test_licence_coverage.py tests/test_decision_sources.py tests/test_model_345_collect.py tests/test_decision_model.py > /tmp/model-390-review747-focused.log 2>&1
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py tests/test_decision_verify.py tests/test_decision_registry.py tests/test_licence_coverage.py tests/test_decision_sources.py tests/test_model_345_collect.py tests/test_decision_model.py > /tmp/model-390-review747-focused-final.log 2>&1

PYTHONDONTWRITEBYTECODE=1 MODELSPEC_DATA_DIR=/tmp/d390 MODELSPEC_REQUIRE_DATA_DIR=1 TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -B docs/evidence/g2-ios/MODEL-390-engine-recheck.py --data /tmp/d390 > /tmp/model-390-review747-recheck.json
PYTHONDONTWRITEBYTECODE=1 MODELSPEC_DATA_DIR=/tmp/d390 MODELSPEC_REQUIRE_DATA_DIR=1 TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -B docs/evidence/g2-ios/MODEL-390-engine-recheck.py --data /tmp/d390 > /tmp/model-390-review747-recheck-final.json

PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile > /tmp/model-390-review747-full.log 2>&1
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile > /tmp/model-390-review747-full-final.log 2>&1
ruff check tests/test_model_390_licence_readers.py
/Users/terbeest/dev/modelspec/.venv/bin/ruff check tests/test_model_390_licence_readers.py
git diff --check
python scripts/pytest_shards.py --shard-count 4 --summary
/Users/terbeest/dev/modelspec/.venv/bin/python --version
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --version
ruff --version
/Users/terbeest/dev/modelspec/.venv/bin/ruff --version
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --version
```

Initial focused suites: **757 passed**, exit 0, in 38.13 seconds.
Final focused suites after the quantifier fix: **759 passed**, exit 0,
in 44.96 seconds.
The first full run was interrupted to include the additional quantifier
regressions. It reports 10619 passed, nine skipped, and 11 warnings in
991.40 seconds, exit 2. This is not a passing full run. The interrupted process
and its workers finished before the next run. A first exact-argv process lookup
exited 1 without sending a signal; the next lookup confirmed the one pytest
process by this worktree cwd and sent SIGINT.
Final full suite: **10658 passed, nine skipped, 11 warnings**, exit 0,
in 1139.43 seconds, or 18 minutes 59 seconds.
The browser dependencies, built web assets, and Chromium from the initial
execution were present before the full run. No environment repair was needed.
The new test module passes Ruff. The source-line/code lint comparison against
the reviewed SHA initially found one new E501; wrapping that condition removes
it. The final comparison across the three changed Python files reports 38
inherited findings, 38 current findings, zero introduced findings, exit 0,
with both Ruff versions.
The comparison algorithm is recorded in the initial execution evidence; for
this run its base is the reviewed SHA and its input is those three files.

## Preserved scope and delivery

The `provider_terms` evidence permission for `licence.user_cap` remains, with
the same numeric/unbounded contract range. Complete Apache operative terms
without an appendix remain accepted; operative edits, truncation, additions,
unrecognized copyrights, and malformed appendices remain rejected. Model
binding and source-kind checks remain unchanged. Fixtures remain synthetic,
using the existing standard Apache fixture where needed.

The branch is pushed normally with the previously authorized local-gate skip:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH CI_LOCAL_SKIP=1 git push
gh pr comment 747 -R turbobeest/modelspec --body-file /tmp/model-390-review747-comment.md
gh pr view 747 -R turbobeest/modelspec --json number,url,isDraft,headRefOid,state
```

PR #747 stays a draft. No merge, ready-state action, Linear write, data edit,
engine-pin edit, production switch, ranking-floor change, legal edit, paid API
call, WSL gate, SSH, or real tmux action occurs. All executor-started command
processes finish before delivery. No passing premier gate is claimed.
