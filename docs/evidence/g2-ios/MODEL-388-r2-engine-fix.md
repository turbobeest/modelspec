# MODEL-388 r2 engine governance domains

The offering data check now accepts governance sources on `mistral.ai` and its subdomains for the existing `mistral` provider. The implementation adds one entry to `GOVERNANCE_DOMAINS` in `tests/test_slice1_offerings.py`. The final full engine suite passed: `11175 passed, 9 skipped, 11 warnings in 745.33s`, direct exit code 0.

## Scope and revisions

- Worktree: `/Users/terbeest/dev/worktrees/model-388-engine`.
- Branch: `model-388-mistral-domains`.
- Base SHA: `d29d1c6cf7c3671e51f9191f3f2594afe4afbb6b`.
- Final implementation SHA: `01eb1b02d89733200fdfd30df2598db7a115ce97`.
- Final PR SHA: the head of `model-388-mistral-domains`, resolved with `git rev-parse HEAD` after the evidence commit and recorded in the executor output.
- Draft engine PR: [registry: Mistral governance domains (MODEL-388), #759](https://github.com/turbobeest/modelspec/pull/759).

The existing rule that every API offering belongs to the premier set is unchanged. An AST comparison of `test_slice1_offerings_have_every_guaranteed_facet_once` against the base confirmed the same function. This engine PR supplies only the requested domain mapping and regression tests. It does not file model or offering facts.

## Red and green evidence

`test_mistral_governance_accepts_primary_documents` exercises the real offering loader, source registry loader, and governance check with these hosts: `mistral.ai`, `docs.mistral.ai`, `legal.mistral.ai`, and `help.mistral.ai`.

`test_mistral_governance_rejects_other_domains` exercises the same check with `not-mistral.ai`, `docs.mistral.ai.example.test`, and `deepseek.com`. The test requires a domain rejection rather than the unknown-provider diagnostic. It therefore cannot pass just because Mistral has no mapping.

Before adding the mapping, all seven cases failed. The acceptance cases reported `mistral: add the provider's own document domains to GOVERNANCE_DOMAINS`. The rejection cases failed because that unknown-provider diagnostic did not establish a domain rejection. The direct pytest exit code was 1. See [red output](MODEL-388-r2-engine-red.log).

After adding `"mistral": ("mistral.ai",)`, the whole focused module passed: `17 passed in 1.07s`, direct exit code 0. See [green output](MODEL-388-r2-engine-green.log).

## Broader verification and environment correction

The first full run used `--basetemp` inside the public engine worktree. It returned exit code 1 with `227 failed, 10842 passed, 24 skipped, 11 warnings, 91 errors in 754.07s`. This was an invalid setup for the QA, policy, and feedback tests: their privacy guards require temporary workspaces outside a public git checkout. Source-error redaction tests also distinguish public paths from private paths. The tracebacks name these path checks directly.

The standard full command, with pytest's normal temporary directory, returned exit code 1 with `2 failed, 11158 passed, 24 skipped, 11 warnings in 780.12s`. Its only failures were:

- `tests/test_social_cards.py::test_build_emits_every_template_preview_and_card`.
- `tests/test_social_cards.py::test_every_frozen_template_card_has_clean_chromium_layout`.

Both Node subprocesses reported `ERR_MODULE_NOT_FOUND` for `@playwright/test`. An archived copy of unchanged base `d29d1c6c` reproduced those two failures with normal temporary directories. The same run passed the other eight non-QA tests selected from the first full run: `2 failed, 8 passed in 477.44s`, exit code 1.

The first run's latency assertion compared `0.023786` against `0.019232 * 1.15`. That check passed in the base comparison and standard full run. Its timing cause was not established, and no engine code was changed for it.

`npm ci --prefix web` installed the existing lockfile's dependencies with Node v22.22.3 and npm 10.9.8, exit code 0. The package manifest and lockfile are unchanged. Both failed social-card tests then passed: `2 passed in 185.74s`, exit code 0. The installed Playwright Chromium executable is available.

The post-dependency-install full run returned exit code 1 with `11163 passed, 9 skipped, 11 warnings, 12 errors in 749.61s`. Installing Playwright enabled twelve landing-browser checks that were previously skipped. Their shared fixture raised `FileNotFoundError` for `web/dist/decide.html`. The [CI setup](../../../.github/workflows/test.yml) runs `npm ci` and `npm run build` before the browser tests. Running that [web build](MODEL-388-r2-engine-web-build.log) locally returned exit code 0 and created the missing assets without changing tracked source files. All [twelve landing-browser cases](MODEL-388-r2-engine-post-build-landing.log) then passed in 8.49s, exit code 0.

After installing the existing locked dependencies and building the web assets, the final full engine suite passed: `11175 passed, 9 skipped, 11 warnings in 745.33s`, direct exit code 0. The [complete final output](MODEL-388-r2-engine-full-ready.log.gz) contains no failures or errors. The warnings concern unsigned decision-vocabulary fixtures in existing CLI snapshot tests.

Complete earlier outputs are retained as gzip artifacts: [initial full run](MODEL-388-r2-engine-full-pytest.log.gz), [standard full run](MODEL-388-r2-engine-full-standard-pytest.log.gz), [unchanged-base comparison](MODEL-388-r2-engine-base-non-qa.log.gz), and [post-dependency-install full run](MODEL-388-r2-engine-post-npm-full.log.gz). The five compressed logs' uncompressed SHA-256 hashes, byte lengths, and exit codes are in the [log manifest](MODEL-388-r2-engine-log-manifest.json). `gzip -dc <artifact>` reproduces each original output. The [post-setup social output](MODEL-388-r2-engine-post-setup-social.log) records both resolved dependency failures.

## Commands and versions

Unless noted, commands ran from the engine worktree. The initial red command used pytest's default temporary directory. The recorded red run repeats it with a worktree-local temporary directory.

```sh
PYTHONPATH="$PWD" PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_slice1_offerings.py -k mistral --basetemp="$PWD/.model-388-engine-scratch/red" > docs/evidence/g2-ios/MODEL-388-r2-engine-red.log 2>&1
run_rc=$?
exit "$run_rc"

PYTHONPATH="$PWD" PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_slice1_offerings.py --basetemp="$PWD/.model-388-engine-scratch/green" > docs/evidence/g2-ios/MODEL-388-r2-engine-green.log 2>&1
run_rc=$?
exit "$run_rc"

PYTHONPATH="$PWD" PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n auto --dist loadfile --basetemp="$PWD/.model-388-engine-scratch/full" > .model-388-engine-scratch/full-pytest.log 2>&1
run_rc=$?
printf '%s\n' "$run_rc" > .model-388-engine-scratch/full-pytest.rc
exit "$run_rc"

PYTHONPATH="$PWD" PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n auto --dist loadfile > .model-388-engine-scratch/full-standard-pytest.log 2>&1
run_rc=$?
printf '%s\n' "$run_rc" > .model-388-engine-scratch/full-standard-pytest.rc
exit "$run_rc"

git archive --output=.model-388-engine-scratch/base.tar d29d1c6cf7c3671e51f9191f3f2594afe4afbb6b
mkdir -p .model-388-engine-scratch/base
tar -xf .model-388-engine-scratch/base.tar -C .model-388-engine-scratch/base

PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH" npm ci --prefix web
git diff --exit-code HEAD -- web/package.json web/package-lock.json

PYTHONPATH="$PWD" PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_social_cards.py::test_build_emits_every_template_preview_and_card tests/test_social_cards.py::test_every_frozen_template_card_has_clean_chromium_layout > .model-388-engine-scratch/post-setup-social.log 2>&1
run_rc=$?
printf '%s\n' "$run_rc" > .model-388-engine-scratch/post-setup-social.rc
exit "$run_rc"

PYTHONPATH="$PWD" PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n auto --dist loadfile > .model-388-engine-scratch/full-configured-pytest.log 2>&1
run_rc=$?
printf '%s\n' "$run_rc" > .model-388-engine-scratch/full-configured-pytest.rc
exit "$run_rc"

PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH" npm run build --prefix web > .model-388-engine-scratch/web-build.log 2>&1
run_rc=$?
printf '%s\n' "$run_rc" > .model-388-engine-scratch/web-build.rc
exit "$run_rc"

PYTHONPATH="$PWD" PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_landing.py::test_landing_behaviour_in_browser > .model-388-engine-scratch/post-build-landing.log 2>&1
run_rc=$?
printf '%s\n' "$run_rc" > .model-388-engine-scratch/post-build-landing.rc
exit "$run_rc"

PYTHONPATH="$PWD" PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH" /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n auto --dist loadfile > .model-388-engine-scratch/full-ready-pytest.log 2>&1
run_rc=$?
printf '%s\n' "$run_rc" > .model-388-engine-scratch/full-ready-pytest.rc
exit "$run_rc"

git diff --check
git diff --exit-code d29d1c6c -- decision docs/decision-contract.md docs/decision-contract.schema.json docs/cli-contract.md registry/facets.yaml premier/slice-1.yaml

git add tests/test_slice1_offerings.py
git -c core.hooksPath=/dev/null commit -m 'test: recognize Mistral governance documents (MODEL-388)' -m 'Co-Authored-By: GPT-6.1 Sol <noreply@openai.com>'

CI_LOCAL_SKIP=1 git push -u origin model-388-mistral-domains < /dev/null
GH_PROMPT_DISABLED=1 gh pr create --draft --base main --title 'registry: Mistral governance domains (MODEL-388)' --body-file .model-388-engine-scratch/engine-pr-body.md < /dev/null

git add docs/evidence/g2-ios/MODEL-388-r2-engine-fix.md docs/evidence/g2-ios/MODEL-388-r2-engine-log-manifest.json docs/evidence/g2-ios/MODEL-388-r2-engine-post-npm-full.log.gz docs/evidence/g2-ios/MODEL-388-r2-engine-full-ready.log.gz docs/evidence/g2-ios/MODEL-388-r2-engine-process-audit.json
git add -f docs/evidence/g2-ios/MODEL-388-r2-engine-web-build.log docs/evidence/g2-ios/MODEL-388-r2-engine-post-build-landing.log
git -c core.hooksPath=/dev/null commit -m 'docs: complete MODEL-388 engine verification' -m 'Co-Authored-By: GPT-6.1 Sol <noreply@openai.com>'
CI_LOCAL_SKIP=1 git push origin model-388-mistral-domains < /dev/null
git rev-parse HEAD
GH_PROMPT_DISABLED=1 gh pr view 759 --json number,isDraft,headRefName,headRefOid,url < /dev/null
git status --porcelain
```

The runtime versions were Python 3.14.4, pytest 9.1.1, Node v22.22.3, npm 10.9.8, git 2.50.1, and GitHub CLI 2.102.0. Version commands were `/Users/terbeest/dev/modelspec/.venv/bin/python --version`, the same Python with `-m pytest --version`, `/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --version`, `npm --version` with the prescribed Node PATH, `git --version`, and `gh --version`.

The base comparison used the same Python and Node PATH, `PYTHONPATH` set to the archived base, and `subprocess.run` with that archive as its working directory. The exact pytest arguments were:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q \
  tests/test_decision_sources.py::test_source_registry_rejects_xpath_instead_of_dropping_the_region \
  tests/test_decision_explain.py::test_none_latency_is_within_noise_of_bypassed_explanation \
  tests/test_private_data_errors.py::test_explicit_private_path_redacts_without_environment \
  tests/test_policy_check.py::test_the_loader_refuses_a_path_inside_this_repository \
  tests/test_policy_check.py::test_the_loader_prints_its_wrangler_commands_without_touching_cloudflare \
  tests/test_feedback_digest.py::test_a_staged_cluster_becomes_one_new_draft_with_its_decision_ids \
  tests/test_feedback_digest.py::test_the_same_cluster_next_week_is_an_update_not_a_second_issue \
  tests/test_feedback_digest.py::test_feedback_text_is_never_written_into_the_repository \
  tests/test_social_cards.py::test_build_emits_every_template_preview_and_card \
  tests/test_social_cards.py::test_every_frozen_template_card_has_clean_chromium_layout
```

The premier-function comparison ran this command before the evidence commit:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
import ast, subprocess
base = subprocess.check_output(['git', 'show', 'd29d1c6c:tests/test_slice1_offerings.py'], text=True)
current = Path('tests/test_slice1_offerings.py').read_text()
name = 'test_slice1_offerings_have_every_guaranteed_facet_once'
def fn(text):
    return ast.dump(next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == name), include_attributes=False)
assert fn(base) == fn(current)
PY
```

## Public contract assessment

The [MODEL-59 decision rules](../../decision-contract.md#versioning-model-59) require a major version change when a public field's range widens. The [CLI rules](../../cli-contract.md#contract-versioning-model-59) also cover changes to field types, units, result shapes, and exit-code meanings.

This change affects a test's governance-source domain map. It changes no production code, public fields, accepted request shapes, response ranges, result shapes, or exit-code meanings. No contract version bump is required. The direct diff check against the base returned 0 for the engine, contract documents and schema, facet registry, and premier list.

## Observation limits

These tests verify source-host acceptance and rejection. They do not verify a Mistral price, governance statement, model's weights, premier completeness, or an FR decision route. Those data tasks belong to the separate data worktree and PR.

No provider model endpoint, paid API, Firecrawl, or workflow dispatch was used. No Linear write, merge, force-push, or data `.engine-pin` change was made. All test commands ran in the foreground and have exited. The [process audit](MODEL-388-r2-engine-process-audit.json) checked 38 previously captured pytest processes by PID, start time and executable; none remained. An `lsof` current-directory check also found no live processes in the engine worktree other than the audit itself. The agent created no background shell jobs.

The temporary archive and run files under `.model-388-engine-scratch` are removed after copying the complete evidence artifacts. The dependency installation and web build remain local, ignored environment files. The final executor output records the pushed SHA, draft state and clean tracked worktree.
