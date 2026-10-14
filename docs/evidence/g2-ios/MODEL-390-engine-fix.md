# MODEL-390-engine execution evidence

The engine verifies explicit licence clauses without a completion reader. The
private data PR remains blocked by unsupported readings, unresolved model
bindings, and missing governing snapshots. The premier gate remains enabled.

## Revisions and scope

Base SHA: `822aa83af2c715ddfbc88acbd4875bd50db0afd4`.
Verified implementation SHA: `c3f8a56fd0b0258822c72b69260e9fc8b3b89269`.
The final delivery SHA is the commit containing this evidence, reproducible with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-390-engine-fix.md`.
The execution marker and draft PR head record the full delivery SHA.

Worktree: `/Users/terbeest/dev/worktrees/model-390-engine`.
Branch: `sparksandsawdust/model-390-licence-readers`.
Private data PR #80 was rechecked at
`4bc5f4cfa9c1f29689aaf3142be22cabc44454db` in `/tmp/d390`.
Its engine pin remains `60c26c623f2fd3b1be1ca7dbedf75dde9d7d77fa`.

The executor read CODEX-EXEC.md, the full ticket spec, CLAUDE.md, AGENTS.md,
the private PR body and evidence, the registry definitions, licence reading
rules, and decision contract before implementation. The existing Graphify index
did not cover this verification code. There is no `.codegraph/` directory here.
Two read-only workers checked contract semantics and retained clause structures.
Another worker built the offline recheck helper. Each worker had separate file
ownership, and only the executor changed the reader.

## Changes and source-kind decision

`CanonicalLicenceExtractor` accepts the complete Apache 2.0 operative body
without its optional application appendix. The exact-body and residual checks
still reject additions or truncation. This addresses the actual four Gemma 4
cards in data PR #80, which cite Apache 2.0 rather than Gemma Terms of Use.

`LicenceTermsExtractor`, method `licence-terms@1`, reads fixed clause families
for Gemma permission and prohibited-use duties, output-derived model restrictions,
provider grants for customer applications, customer output-training restrictions,
model-weight modification prohibitions, and explicit MAU agreement thresholds.
It retains source-kind and model-binding checks. Unsupported prose falls through
to the existing completion reader, if configured, or remains skipped.

`licence.user_cap` now permits `provider_terms` as well as `licence_text`.
Its definition measures monthly active users before a separate agreement is
required. Provider terms can impose that agreement for an API model. The field
still accepts the same number or `unbounded` values, so this input permission
does not widen the decision contract's range or require a major-version bump.
Existing forbidden-source tests now use a genuinely forbidden documentation
kind and retain their rejection assertions.

The reader does not infer `unbounded` from a short excerpt or from a title plus
silence. Delegation of usage limits to an order cannot establish an unlimited
cap. Ownership of output is not a commercial-use grant. Provider privacy promises
are not customer output-training rights. A hosted-service modification ban is
not an express model-weight modification ban. The TypeSafe service clause
therefore does not verify the filed fine-tuning prohibition.

## Red-first results

All new clause fixtures are synthetic paraphrases. The Apache tests use the
repository's existing standard-licence fixture, not a copied vendor document.
No retained private terms were added to the public repository.

| Defect or clause family | Test | Red output | Final green |
| --- | --- | --- | --- |
| Complete Apache body lacks an optional appendix | `test_complete_apache_terms_without_optional_appendix` | All four facets returned `skipped`, expected `verified`; `4 failed, 2 passed`, exit 1 | All four facets verify; additions still skip |
| Provider-term MAU threshold and source permission | `test_provider_terms_can_state_a_monthly_user_agreement_cap` | Both source kinds skipped; the new permission-dependent negatives saw `source_kind` mismatches; `7 failed, 1 passed, 5 deselected`, exit 1 | Explicit cap verifies with the published MAU unit; silence and unrelated thresholds skip |
| Conditional grants, output-specific restrictions, weight modification | `test_conditional_service_grants_read_commercial_use`, `test_output_training_subset_restrictions`, `test_model_modification_prohibition_reads_fine_tuning` | Grants and output restrictions skipped; `8 failed, 19 passed, 10 deselected`, exit 1 | Express supported clauses verify; wrong values mismatch |
| Gemma grant, policy, output-derived model clauses | `test_gemma_clause_families` | Three facets skipped; `3 failed, 61 passed`, exit 1 | Explicit clauses verify |
| Gemma use and distribution clause structure | `test_gemma_use_grant_and_distribution_restrictions` | All three facets skipped; `3 failed, 66 deselected`, exit 1 | All three supported readings verify |
| Restriction list spans adjacent enumerated paragraphs | `test_prohibition_prefix_covers_adjacent_enumerated_paragraphs` | `skipped` instead of `verified`; `1 failed, 3 passed, 69 deselected`, exit 1 | The list's prohibition applies to its enumerated actions, but not the next unrelated paragraph |
| Wrong action/object, negated grants, excluded derivatives | `test_output_prohibition_requires_customer_model_training_action`, `test_negated_provider_grants_remain_unread`, `test_gemma_output_definition_and_distribution_rule_cannot_exclude_output_models`, `test_quoted_false_gemma_grant_remains_unread` | Nine unsupported fixtures verified; `9 failed, 1 passed, 73 deselected`, exit 1 | Every prior unsafe probe skips |

The first API modification test treated modifying Services as modifying model
weights. Reading the definition showed that expectation was unsupported. The
positive fixture now expressly names model weights, and the services-only
clause remains as a negative fixture. No existing test was weakened.

Cap scale conversion initially compared `200` with `200000000`. The final
reading scales the number and reports `monthly_active_users` independently of
the claim. Malformed comma groups, an incomplete agreement object, a forged
unit, missing binding, repealed clauses, and contradictory scopes are covered.
An initial empty-residual implementation failed its module-level appendix
invariant during collection; the exact optional-appendix form now passes that
invariant. These implementation errors were corrected before the focused pass.

## Private recheck

The committed [recheck helper](MODEL-390-engine-recheck.py) runs real
`verify`, `verify_fidelity_sample`, `collect_repo`, and `build_snapshot` calls
against the current engine. It refuses socket operations, restores verified
archive hashes only into a temporary directory under `/tmp`, and holds new
verification records in memory. It does not bypass the data pin assertion in
the old private script. It calls the branch's APIs directly instead.

Aggregate results are in [MODEL-390-engine-recheck.json](MODEL-390-engine-recheck.json).
The licence check covers 64 facts: 38 verified, 14 skipped, four model-binding
mismatches, and eight facts with no governing snapshot. Source-kind mismatches,
unknown source kinds, unreachable cited copies, network calls, and completion
calls are zero. The four model-binding mismatches concern the two Meta variants'
commercial-use and output-training readings. Their relative terms links do not
pass the existing binding reader. Binding rules were not relaxed.

The targeted fidelity function covers the 56 cited facts and reports 38 verified,
18 undetermined, zero mismatches, and zero unreachable. It treats missing model
bindings as undetermined. Its generic status is `pass`, which does not establish
complete ticket verification. The helper exits 1 because ticket completion and
the premier gate fail.

The stored-verification premier gate still rejects 31 facts. With genuine new
reader outcomes overlaid in memory, it rejects 25: four commercial-use, eight
fine-tuning, five output-training, and eight user-cap facts. Eight uncited rows
alone prevent a fully passing gate without new data evidence. Go verifies.
Tracked and untracked data status is identical before and after the run.

The overlay retains historical records when a current reread skips. Ingot's
earlier commercial-use key therefore remains in the gate inputs. A historical
admission does not establish a fresh governing-text verification. The targeted
licence counts report the current readings independently of those older keys.

A separate offline probe against the retained Gemma Terms confirms three
readings with synthetic model binding: commercial use and fine-tuning are
`permitted_with_conditions`, and output training is `restricted`. Its silent
user cap remains skipped. This probe does not claim to bind those terms to the
Apache-licensed Gemma 4 cards.

## Commands and versions

Python 3.14.4, pytest 9.1.1, Ruff 0.16.6, Git 2.50.1, gh 2.102.0,
Node 22.22.3, npm 10.9.8, and Playwright 1.63.0.
Commands run from the engine worktree unless a working directory is named.
Exit codes are checked directly, without a pipeline.

```sh
gh pr view 80 -R turbobeest/modelspec-data --json title,body,headRefName,url
git -C /Users/terbeest/dev/modelspec-data fetch origin sparksandsawdust/model-390-licence-sources
git -C /Users/terbeest/dev/modelspec-data worktree add --detach /tmp/d390 FETCH_HEAD

TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py -k 'user_agreement_cap or user_cap'
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py -k 'commercial_use or output_training or fine_tuning'
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py -k 'gemma_use_grant_and_distribution'
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py -k 'adjacent_enumerated or scopes_do_not_extend'
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py -k 'requires_customer_model_training or negated_provider or cannot_exclude or false_gemma'

TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_390_licence_readers.py tests/test_decision_verify.py tests/test_decision_registry.py tests/test_licence_coverage.py tests/test_decision_sources.py tests/test_model_345_collect.py tests/test_decision_model.py
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile

# From web/:
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npx --no-install playwright install chromium
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH PYTHONPATH=/Users/terbeest/dev/worktrees/model-390-engine npm run build
# From the engine worktree:
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_social_cards.py --tb=short --show-capture=no
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_landing.py --tb=short --show-capture=no
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile > /tmp/model-390-final-pytest.log 2>&1
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile > /tmp/model-390-final-pytest-complete.log 2>&1

PYTHONDONTWRITEBYTECODE=1 MODELSPEC_DATA_DIR=/tmp/d390 MODELSPEC_REQUIRE_DATA_DIR=1 TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -B docs/evidence/g2-ios/MODEL-390-engine-recheck.py --data /tmp/d390 > docs/evidence/g2-ios/MODEL-390-engine-recheck.json
git diff --check
```

Final ticket suite: 83 passed, exit 0. Final broader focused suite: 716 passed,
exit 0. Corrected social-card module: 27 passed, exit 0, in 453.85 seconds.
Corrected landing module: 33 passed, exit 0, in 142.63 seconds.
Final full suite: 10615 passed, nine skipped, and 11 warnings, exit 0,
in 1094.77 seconds (18 minutes 14 seconds).

The first full run reports two failed, 10588 passed, 24 skipped, and 11 warnings,
exit 1, in 1230.84 seconds. Both failures are in `tests/test_social_cards.py`:
`test_build_emits_every_template_preview_and_card` and
`test_every_frozen_template_card_has_clean_chromium_layout`. Their subprocesses
raise `ERR_MODULE_NOT_FOUND` for `@playwright/test` because `web/node_modules`
was absent. The first run also picked up default Node 22.23.1. Installing the
locked web dependencies and selecting the brief's Node 22.22.3 fixes the test
environment without changing tracked files. Chromium installation exits 0.
The second full run reports 10603 passed, nine skipped, 11 warnings, and
12 setup errors, exit 1, in 1082.37 seconds. All 12 errors are landing-browser
fixtures missing `web/dist/decide.html`. Installing Playwright had enabled
previously skipped tests that also require the built frontend. The locked
frontend build exits 0 and supplies both the HTML and its assets without
changing tracked files. Its four font-resolution warnings leave runtime paths
that the test site supplies. A read-only audit confirms the referenced built
assets, fonts, browser packages, and Chromium are present. The final full run
uses the hardened implementation and this complete browser environment.

The unrestricted Ruff invocation initially reported inherited formatting errors
and four new long lines. The new lines were corrected. A comparison against
the base SHA, using Ruff JSON findings keyed by error code and source line,
reports 45 inherited findings, 45 current findings, zero introduced findings,
exit 0. The new test and recheck files pass Ruff. Two exploratory source probes
initially used nonexistent `Source.regions` and `whole_document` locator names;
both exited 1 and were corrected to `cited_regions` and `Locator.page()`.
Those operational errors are not red-test evidence.

The lint comparison is reproducible with:

```sh
python3 - <<'PY'
import json
import subprocess
from pathlib import Path

base = '822aa83af2c715ddfbc88acbd4875bd50db0afd4'
paths = subprocess.run(
    ['git', 'diff', '--name-only', base, 'HEAD'],
    check=True, capture_output=True, text=True,
).stdout.splitlines()
prior_count = current_count = 0
introduced = []
for path in (path for path in paths if path.endswith('.py')):
    prior = subprocess.run(
        ['git', 'show', f'{base}:{path}'], capture_output=True, text=True,
    )
    findings = []
    for source in (prior.stdout if prior.returncode == 0 else '', Path(path).read_text()):
        result = subprocess.run(
            ['ruff', 'check', '--output-format', 'json', '--stdin-filename', path, '-'],
            input=source, capture_output=True, text=True,
        )
        if result.returncode not in (0, 1):
            raise SystemExit(result.stderr)
        lines = source.splitlines()
        findings.append({
            (item['code'], lines[item['location']['row'] - 1].strip())
            for item in json.loads(result.stdout)
        })
    prior_count += len(findings[0])
    current_count += len(findings[1])
    introduced.extend((path, code, line) for code, line in findings[1] - findings[0])
print(json.dumps({
    'baseline_findings': prior_count,
    'current_findings': current_count,
    'introduced_findings': introduced,
}, indent=2))
raise SystemExit(bool(introduced))
PY
```

## Delivery and observations not made

After the checks, the branch is pushed using the authorized local-gate skip:

```sh
CI_LOCAL_SKIP=1 git push -u origin sparksandsawdust/model-390-licence-readers
```

From `/tmp`, the draft PR is created with the prepared body file:

```sh
gh pr create -R turbobeest/modelspec --draft --base main --head sparksandsawdust/model-390-licence-readers --title "verify: licence readers for Gemma terms and provider API terms (MODEL-390)" --body-file /tmp/model-390-engine-pr-body.md
```

No complete governing snapshots for Seed or April Muse were obtained. No private
orders, provider inference API, completion service, device, or paid model call
was used. No passing data completeness gate or production behavior is claimed.
No private source text, facts, or verification log was copied into this public
repository. Only aggregate recheck results are retained.

No data edits, engine-pin edits, production switches, ranking floors, legal terms,
workflow changes, WSL gate, SSH, SCP, curl, wget, Linear writes, merge, ready-state
action, force-push, or real tmux actions were performed. All executor-started
processes finish before delivery. The draft awaits cross-model review.
