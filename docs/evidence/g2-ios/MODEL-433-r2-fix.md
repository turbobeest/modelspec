# MODEL-433-r2 execution evidence

The failed-recipe path now excludes every canonical URL with a registered
interaction recipe before Firecrawl preparation, balance lookup, or scraping.
An alias without a recipe cannot make that URL eligible. The rendered failure
remains unreadable. Tests use an HTTP mock transport; no Firecrawl service was
called.

The control guard checks aria-label, text content, and value independently.
Consent rejection requires every nonempty label to identify rejection. A safe
aria-label cannot hide consent acceptance, login, or submission text or values.

Azure's private recipe now waits for the selected East US and USD labels.
A text wait targeting a native select checks the selected option's exact label,
so neither an unselected option nor the label "East US 2" satisfies "East US".
Other text waits retain their existing substring behavior. The Source model
uses `apply_exclude_if` from the existing compatibility shim on Pydantic 2.10.6;
modern Pydantic uses its native exclusion. The new field no longer produces a
2.10 deprecation warning, and empty recipes disappear from Python, JSON, and
nested serialization.

## Revisions and scope

- Assigned engine base: `df9d79cf1fe1e77324508d27f1aa9675aef6b101`.
- Merged origin/main: `41d1c961426efa25e951468e050e611a4c846ead`.
- Merge commit: `4cda4a1`. No rebase or force push.
- Final engine implementation: `5ef295572d9e55a69b5d6ef9fb7a45ffdc040ca2`.
- The following evidence-only commit is the final branch revision, recorded in
  PR #865 and the executor's final output. Resolve it with
  `git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-433-r2-fix.md`.
- Data base: `acd85ff25b34c3170b10adc472aff3129adb615a`.
- Data implementation: `0d62d3f69ddf03ed042f74c3271cd1246951a7bf`.
  Its origin/main was already an ancestor.

The data clone is under this worktree's ignored `tmp/model-433-r2/` directory.
Only recipe and regression/evidence files changed there. `.engine-pin`,
offerings, and verification records are unchanged. Public frozen data did not
change. Both existing PRs remain drafts.

Merge #865 first. Then move data#116's `.engine-pin` to the resulting public
main commit, validate that pin, and merge data#116. The executor does not merge
or advance the pin to an unmerged branch commit.

## Red and green results

All tests ran serially with direct exit-code checks. Logs are in
[MODEL-433-r2](MODEL-433-r2/).

| Regression | Red result | Green result |
| --- | --- | --- |
| `test_failed_recipe_never_calls_firecrawl`, direct and alias | Both made one mocked scrape instead of zero | Both pass with zero scrape and balance requests |
| `test_safe_label_cannot_hide_unsafe_text_or_value` | Six controls set a consent cookie; one already blocked | All seven pass; no cookie is set |
| `test_empty_recipe_is_omitted_from_python_json_and_nested_serialization` | Empty recipe was emitted on Pydantic 2.10.6 | Passes on 2.10.6 and 2.13.5 |
| `test_wait_text_on_select_requires_the_selected_option` | Unselected text passed; a second red run showed a selected prefix match also passed | Both selected and wrong-region cases pass |
| Private `test_azure_recipe_confirms_selected_region_and_currency` | Wrong region and wrong currency both captured stale dollar tables | All three cases pass |

The initial engine red run exited 1 with 9 failed, 1 passed, 187 deselected.
Both selection red runs exited 1 with 1 failed, 1 passed, 47 deselected.
The private recipe red run exited 1 with 2 failed and 1 passed.
An intermediate private fixture lacked a UTF-8 declaration, so the USD label's
dash decoded incorrectly. Adding the declaration corrected the fixture;
`r2-fixture-encoding-failure.txt` retains that failure in the private data PR.

The final focused scratch run passed **499 tests, zero skips**, including all
21 original browser cases and nine new browser cases. Pydantic 2.10.6 still
emits 47 existing `exclude_if` warnings from unrelated fields.

Broader Pydantic 2.10.6 results: **320 passed, 2 failed, zero skips**. The failures
are `test_repository_subscription_offerings_validate_against_the_real_registry`
and `test_schema_file_is_generated_from_the_types`. The former emits unrelated
SourceRef defaults; the latter encounters a callable in the existing contract
schema metadata. `baseline_compat.py` loads the pre-fix model from merge commit
`4cda4a1` and reproduces both failures. Their logs are retained; neither test was
weakened or excluded from the broader run.

The normal shared environment passed **341 tests, 30 skipped** across the model,
contract, Worker bundle/import, and interaction suites. All 30 skips are browser
cases because shared Python lacks Playwright. They ran in scratch above.
The public Worker bundle was regenerated and its declared-dependency import
check passed. No full repository suite or CI result is claimed.

## Commands and tools

Run from `/Users/terbeest/dev/worktrees/model-433`. `SCRATCH` below abbreviates
`tmp/model-433-r2`; `PY` is `$SCRATCH/venv/bin/python`; `SHARED` is
`/Users/terbeest/dev/modelspec/.venv/bin/python`. Output redirection stores the
named logs; each pytest process's exit status was read directly, without pipes.

```sh
git fetch origin main
git merge --no-edit origin/main
# The local merge message was amended to add the required co-author trailer.
git clone --branch model-433-interactive-pricing --single-branch https://github.com/turbobeest/modelspec-data.git "$SCRATCH/modelspec-data"
git -C "$SCRATCH/modelspec-data" fetch origin main:refs/remotes/origin/main
git -C "$SCRATCH/modelspec-data" merge origin/main -m 'Merge origin/main into model-433-interactive-pricing' -m 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
uv venv --python /opt/homebrew/bin/python3.12 "$SCRATCH/venv"
uv pip install --python "$PY" -e '.[dev]' playwright 'pydantic==2.10.6' beautifulsoup4
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH "$PY" -m playwright install chromium
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_price_reread_fallback.py tests/test_rendered_interactions.py -k 'failed_recipe_never_calls_firecrawl or safe_label_cannot_hide or empty_recipe_is_omitted'
env PYTHONPATH=$PWD "$PY" -m pytest -q -p no:cacheprovider tests/test_rendered_interactions.py -k wait_text_on_select
env PYTHONPATH=$PWD "$PY" -m pytest -q -rs -p no:cacheprovider tests/test_rendered_interactions.py tests/test_price_reread_fallback.py tests/test_rendered_sources.py tests/test_price_reread.py tests/test_decision_sources.py tests/test_decision_registry.py tests/test_cite_only_retention.py
env PYTHONPATH=$PWD "$PY" -m pytest -q -rs -p no:cacheprovider "$SCRATCH/modelspec-data/docs/evidence/g2-ios/MODEL-433/test_azure_selection.py"
env PYTHONPATH=$PWD "$PY" api/worker/vendor.py
env PYTHONPATH=$PWD "$PY" api/worker/vendor.py --check
env PYTHONPATH=$PWD "$PY" -m pytest -q -rs -p no:cacheprovider tests/test_decision_model.py tests/test_decision_contract.py tests/test_worker_bundle.py tests/test_worker_vendor_imports.py
env PYTHONPATH=$PWD "$PY" docs/evidence/g2-ios/MODEL-433-r2/baseline_compat.py
env PYTHONPATH=$PWD "$SHARED" -m pytest -q -rs -p no:cacheprovider tests/test_decision_model.py tests/test_decision_contract.py tests/test_worker_bundle.py tests/test_worker_vendor_imports.py tests/test_rendered_interactions.py
git diff --check
CI_LOCAL_SKIP=1 git push -u origin model-433-interactive-pricing
CI_LOCAL_SKIP=1 git -C "$SCRATCH/modelspec-data" push -u origin model-433-interactive-pricing
```

[versions.json](MODEL-433-r2/versions.json) records Python 3.12.11, Pydantic
2.10.6, pytest 9.1.1, Playwright 1.64.0, Chromium 156.0.8078.4, httpx 0.28.1,
PyYAML 6.0.3, Node v22.22.3, and Git 2.50.1. Shared Python is 3.14.4 with
Pydantic 2.13.5 and pytest 9.1.1.

A scoped Ruff run found existing style diagnostics plus two introduced style
issues; the introduced import ordering and line length were corrected.
An initial data merge attempt could not resolve origin/main because the clone
tracked only its feature branch; explicitly fetching that ref fixed it.
The machine initially reported load above 30. Testing started after two
60-second waits and a new reading of 10.33.

The direct Azure label probe used httpx, no redirects, a 30-second timeout,
and BeautifulSoup to print only the `us-east` and `usd` option labels. It
observed `East US` and `United States – Dollar ($) USD`. No page was saved.
An initial invocation in shared Python failed before requesting the page
because BeautifulSoup was absent; the installed scratch environment succeeded.

## Not observed

No live AWS/Azure interaction run, live price verification, production Worker,
or new Worker memory measurement was performed. Selection fixtures establish
control confirmation and fail-closed behavior; they do not establish the live
provider's table-update timing or current prices. No provider page bytes were
retained. No Firecrawl spend, paid-provider call, WSL gate, SSH, SCP, Linear
write, merge, or production switch change occurred. Independent review and CI
remain pending. Browser contexts and test processes were closed before exit.
