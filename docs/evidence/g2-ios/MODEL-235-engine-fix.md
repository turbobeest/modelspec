# MODEL-235-engine: parse retained pages once per price reread

Execution date: 2026-10-13. Worktree: `/Users/terbeest/dev/worktrees/model-235-engine`.
Branch: `sparksandsawdust/model-235-reread-parse-once`.

Base SHA: `b5ec02b18d8edffdd8504b0ea7d108367e5903fd`.
Red-first test commit: `42d4f3dd46f1b687175b4f07fa4fb00d13db8fcb`.
Tested implementation SHA: `0b298c6ddfdf591ec49a7bc03d1b3c86b0848ea1`.
At delivery, the final delivery SHA is the commit containing this report. Resolve it with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-235-engine-fix.md`.
The PR body and executor completion record contain its literal SHA.

The originating diagnosis is the final comment on
[modelspec-data PR 70](https://github.com/turbobeest/modelspec-data/pull/70).
I read that comment with `gh pr view 70 -R turbobeest/modelspec-data --json comments --jq '.comments[-1].body'`.
I did not fetch or retain its provider page.

`StoredRegions` now optionally memoises successfully normalised documents by
content-hash copy reference and the complete effective `RuleSet`.
`reread_fact` creates a cache-enabled instance immediately before its first
verification, so candidate verification and proposals share the same parsed
document. The memo expires when that fact reread returns. Existing callers keep
the uncached default.

The verifier still sets `strip_volatile=False`, and every region lookup still
checks `CopyStore.has` before reading a memoised document. Region selection,
extractors, comparison, verdicts and published contracts are unchanged.
The page-size diagnostic retains its existing normaliser rules, which can differ
from verification rules and require a separate normalisation.

## Red-first reproduction and timing

`test_many_coverage_readings_parse_each_document_once` exercises `reread_fact`
with synthetic HTML, 220 feature lines, 266 readings, and thousands of nested
HTML spans. It compares serialized `FactResult` JSON against the per-reading
path. That path uses ordinary uncached `StoredRegions`. Claim and verification
are both `None` for this `needs_review` scenario and also compare equal.
The test also rereads the same input twice and requires each invocation to
normalise once, proving the memo does not persist between calls.

Before the production edit, the test failed with exit code 1:

```text
MODEL-235 synthetic timing: 266 -> 266 normalisations; 15.168s -> 14.538s; 266 readings
E       assert 266 == 1
FAILED tests/test_price_reread.py::test_many_coverage_readings_parse_each_document_once
1 failed in 30.28s
```

The initial fixture repeated the word `included` twenty times per line.
The profiled cache-enabled reread still took 13.192 seconds. The retained profile
showed remaining work in reader regexes and candidate comparisons. The final fixture
removes those repeated filler words while retaining its lines, readings and
nested HTML nodes. No extractor or comparison optimization was added.

Final minimized fixture, comparing the same input through both paths:

```text
MODEL-235 synthetic timing: 266 -> 1 normalisations; 8.887s -> 2.709s; 266 readings
1 passed in 14.94s
```

Both paths return the byte-identical `needs_review` result and its whole-page
free-text warning. The call-count assertion is the performance guard. Timing
is supporting evidence, without a load-sensitive deadline assertion.

The following document-cache boundaries passed, exit code 0:

- `test_cached_documents_keep_normaliser_rules_and_verifier_dates`: the same
  bytes produce distinct text under `html-default` and `html-icon-labels`, with
  exactly two normalisations. Labeled update timestamps remain in verifier text.
- `test_cached_document_reuses_regions_after_a_missing_locator`: missing CSS,
  CSS, table, heading and page citations match literal expected text and the
  uncached path, with exactly one normalisation.
- `test_cached_document_rechecks_retained_copy_integrity[delete]` and
  `[corrupt]`: cached content becomes unreachable after its retained copy changes.

Boundary result: `4 passed, 389 deselected in 0.81s`.
Focused result: `718 passed in 20.35s`, exit code 0.
Initial full-suite result: `2 failed, 10429 passed, 23 skipped, 11 warnings in
1877.62s (0:31:17)`, exit code 1. Both failures were in
`test_social_cards.py`, at `test_build_emits_every_template_preview_and_card`
and `test_every_frozen_template_card_has_clean_chromium_layout`.
Both renderer subprocesses reported:

```text
Error [ERR_MODULE_NOT_FOUND]: Cannot find package '@playwright/test' imported from .../web/scripts/render-social-cards.mjs
```

The first isolated Node-backed rerun was interrupted with SIGINT, exit code 2;
its partial result was `35 passed, 14 skipped in 183.89s`. `npm ci` installed the locked web
dependencies, exit code 0, without changing tracked files. A real Chromium
renderer probe then passed: `1 passed in 2.43s`, exit code 0. The final full-suite
run uses Node 22.22.3 and these installed dependencies.

A prepared run used an in-repository `TMPDIR`, which changed its temporary
fixtures' public/private classification. Output guards rejected paths inside
the repository, and source-validation redaction expectations failed. I interrupted that run, exit code
2, and removed the override. The interrupted result was `209 failed, 6063 passed,
2 skipped, 4 warnings, 91 errors in 158.32s (0:02:38)`. No guard or test was
changed. With the standard temporary directory, representative private-output,
source-registry and Chromium tests passed: `3 passed in 2.49s`, exit code 0.

The interrupted run left copied test files and a fixture symlink to the public
repository in the visible scratch directory. An unqualified collection followed
that symlink repeatedly. I interrupted collection, exit code 2, with `1597 errors
in 652.07s (0:10:52)`. Moving this session's scratch directory under `.artifacts`
restored collection of the intended repository tests through pytest's default
directory exclusion. Both completed full runs account for 10,454 tests.

That clean run reached the previously skipped landing-browser fixture, which
required `web/dist/decide.html`. I interrupted it, exit code 2, with `9128 passed,
7 skipped, 10 warnings, 12 errors in 746.94s (0:12:26)`. The shared fixture errors
were `FileNotFoundError` for that missing bundle. `npm run build` completed,
exit code 0, without changing tracked files. Both Node-backed modules then ran
with the installed dependencies and compiled bundle: `59 passed in 1011.45s
(0:16:51)`, exit code 0.

The completed full-suite run then returned exit code 1:

```text
FAILED tests/test_agent_ready.py::test_built_tree_passes_surface_lint
1 failed, 10445 passed, 8 skipped, 11 warnings in 1898.66s (0:31:38)
```

This remaining failure is an existing local-date/UTC-date mismatch in the site
build. `pipeline/build.py` writes sitemap dates with `date.today()`, while
`pipeline/export.py` records `built_at` with `datetime.now(UTC)`.
`pipeline/surface_lint.py` expects the sitemap date to match that UTC timestamp.
The retained failing tree has `built_at: 2026-10-14T00:53:07+00:00` and all
2,618 sitemap dates equal to `2026-10-13`. All 2,618 findings are
`freshness.source`, with actual `2026-10-13` and expected `2026-10-14`.
An isolated rerun in the same local time zone also failed, exit code 1,
`1 failed in 178.25s`.

An isolated rerun with the test process set to `TZ=UTC` returned exit code 0,
`1 passed in 297.58s (0:04:57)`.
The full suite remains recorded as exit code 1. No site-build source or test
changed to address this separate date-zone issue.

## Commands and tools

Commands ran from the assigned worktree unless stated otherwise. Test process
exit codes came directly from command completion, without a pipeline.

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python -V
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --version
/Users/terbeest/dev/modelspec/.venv/bin/python -c 'import importlib.metadata as m; print("pytest-xdist", m.version("pytest-xdist")); print("pydantic", m.version("pydantic"))'
git --version
gh --version
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --version

PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -s tests/test_price_reread.py::test_many_coverage_readings_parse_each_document_once > tmp-model-235-red.log 2>&1
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -s tests/test_price_reread.py::test_many_coverage_readings_parse_each_document_once > tmp-model-235-green.log 2>&1
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_verify.py -k 'cached_document' > tmp-model-235-boundaries.log 2>&1
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m cProfile -s cumulative -m pytest -q -s tests/test_price_reread.py::test_many_coverage_readings_parse_each_document_once > tmp-model-235-profile.log 2>&1

mkdir -p tmp/model-235-engine/executor
mv tmp-model-235-*.log tmp/model-235-engine/executor/
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_price_reread.py tests/test_price_reread_fallback.py tests/test_decision_verify.py tests/test_decision_sources.py > tmp/model-235-engine/executor/focused.log 2>&1
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile > tmp/model-235-engine/executor/full.log 2>&1
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -o cache_dir=tmp/model-235-engine/executor/pytest-node-cache --basetemp=tmp/model-235-engine/executor/node-tests tests/test_landing.py tests/test_social_cards.py > tmp/model-235-engine/executor/node-pinned.log 2>&1
kill -INT 77823
# From web/:
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm_config_cache=/Users/terbeest/dev/worktrees/model-235-engine/tmp/model-235-engine/executor/npm-cache npm ci > ../tmp/model-235-engine/executor/npm-ci.log 2>&1
# From the worktree root:
CI=1 PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -o cache_dir=tmp/model-235-engine/executor/pytest-node-cache --basetemp=tmp/model-235-engine/executor/node-probe tests/test_social_cards.py::test_renderer_writes_every_card_at_the_contract_size > tmp/model-235-engine/executor/node-probe.log 2>&1
mkdir -p tmp/model-235-engine/executor/final-temp
TMPDIR=$PWD/tmp/model-235-engine/executor/final-temp PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile > tmp/model-235-engine/executor/full-prepared.log 2>&1
kill -INT 57309
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_tui_harness.py::test_plugin_install_uses_run_scoped_native_commands_and_does_not_leak tests/test_decision_sources.py::test_source_registry_rejects_xpath_instead_of_dropping_the_region tests/test_social_cards.py::test_renderer_writes_every_card_at_the_contract_size > tmp/model-235-engine/executor/environment-probe.log 2>&1
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile > tmp/model-235-engine/executor/full-final.log 2>&1
kill -INT 33571
mkdir -p .artifacts/model-235-engine
mv tmp/model-235-engine/executor .artifacts/model-235-engine/executor
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile > .artifacts/model-235-engine/executor/full-clean.log 2>&1
kill -INT 86194
# From web/:
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm run build > ../.artifacts/model-235-engine/executor/web-build.log 2>&1
# From the worktree root:
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -x tests/test_landing.py tests/test_social_cards.py > .artifacts/model-235-engine/executor/node-ready.log 2>&1
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile > .artifacts/model-235-engine/executor/full-ready.log 2>&1
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_ready.py::test_built_tree_passes_surface_lint > .artifacts/model-235-engine/executor/freshness-rerun.log 2>&1
TZ=UTC PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_ready.py::test_built_tree_passes_surface_lint > .artifacts/model-235-engine/executor/freshness-utc.log 2>&1
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 4 --summary
git diff --check
```

Versions: Python 3.14.4, pytest 9.1.1, pytest-xdist 3.8.0, Pydantic 2.13.5,
Node 22.22.3, npm 10.9.8, Git 2.50.1, GitHub CLI 2.102.0. The initial full-suite
shell Node was 22.23.1. The final full-suite run puts the brief's required Node
directory first in `PATH`. A source audit found every active Node invocation in
`test_landing.py` and `test_social_cards.py`. Other site-build modules launch
Node only through optional social-card rendering. `MODELSPEC_RENDER_SOCIAL_CARDS`
was unset, so those gated paths were inactive.
The shard summary reports 63, 62, 63 and 63 files, with predicted loads of
3380.284, 3380.283, 3380.285 and 3380.283 seconds.

Delivery commands:

```bash
git diff --check b5ec02b1..HEAD
git diff --check
git add docs/evidence/g2-ios/MODEL-235-engine-fix.md
git commit --file .artifacts/model-235-engine/executor/evidence-commit-message.txt
git rev-parse HEAD
CI_LOCAL_SKIP=1 git push -u origin sparksandsawdust/model-235-reread-parse-once
# From /tmp, using an absolute path for the body file:
gh pr create -R turbobeest/modelspec --draft --base main --head sparksandsawdust/model-235-reread-parse-once --title "price re-read: parse each page once, not once per reading (MODEL-235)" --body-file /Users/terbeest/dev/worktrees/model-235-engine/.artifacts/model-235-engine/executor/pr-body.md
gh pr view sparksandsawdust/model-235-reread-parse-once -R turbobeest/modelspec --json number,url,isDraft,headRefName,headRefOid,baseRefName
```

The evidence commit message ends with
`Co-Authored-By: ChatGPT Codex <noreply@openai.com>`, as do the two source/test
commits. The PR remains a draft for independent review.

## Limits of the observations

I did not replay the saved x.ai page, measure its scheduled workflow, or observe
production timings. These results establish parsing reuse and unchanged output
for synthetic inputs. Candidate extraction, comparisons and narrow region
selection still run for every candidate, so other page shapes may retain costs
beyond parsing.

No provider page was committed, no Firecrawl or paid-provider call ran, and no
workflow was dispatched. Production switches, ranking floors, legal terms and
frozen data were not changed. No Linear write, merge or ready transition ran.
