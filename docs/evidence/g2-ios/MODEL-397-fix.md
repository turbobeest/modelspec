# MODEL-397 execution evidence

Base SHA: `c9b625605750f29ede73ade4d7020eb2714b1513`.
Final implementation SHA: `735b1b86cbd33434e165c603e9fa5ecfa8a212b5`.
The delivery commit adds this evidence only. Resolve its final SHA with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-397-fix.md`.
Branch: `model-397-premarketing`.
Worktree: `/Users/terbeest/dev/worktrees/model-397`.

## Billing documentation

The base already contains pricing v2, introduced by MODEL-342 in
`f1bfbdbc` on 2026-10-10, PR #636. The $10 Solo and $50 Team rows are
explicitly legacy prices, retained for renewals. No price amount needed changing.
The change adds separate current-v2 and legacy headings, explains their status,
and validates both tables against the policy that the Worker and pricing page
read, `api/worker/tiers.json`.

Red-first test:
`test_billing_document_price_tables_match_policy`, parametrized for current
and legacy tables. Before the documentation change, both cases failed with
`AssertionError: Current and legacy prices need separate, explicit headings`.
Red result: `2 failed, 84 deselected`, exit 1.
Green result: `2 passed, 84 deselected`, exit 0.
The test compares every row's Price id, kind, name, credits, interval and USD
price, and rejects duplicate Price ids. A separate in-memory mutation replaced
the current Solo row with $10 / 4,000 credits. The test rejected it with an
assertion failure. The actual document and policy were unchanged by that probe.

Reproduce the tests:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_pricing_v2.py -k billing_document_price_tables_match_policy
```

Mutation probe, exit 0 after catching the expected test assertion:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
from pathlib import Path
from unittest.mock import patch
from tests.test_pricing_v2 import access_config, test_billing_document_price_tables_match_policy
policy = access_config.load_policy()
document = Path('docs/billing.md').read_text()
mutant = document.replace('| plan | Solo | 2,500 / month | 29 |',
                          '| plan | Solo | 4,000 / month | 10 |')
assert mutant != document
with patch.object(Path, 'read_text', return_value=mutant):
    try:
        test_billing_document_price_tables_match_policy(
            policy, False, '### Current prices (pricing v2)')
    except AssertionError:
        print('PASS: billing table test rejects current Solo reverted to $10 / 4,000 credits')
    else:
        raise AssertionError('billing table test accepted stale pricing')
PY
```

## Landing headline preserved

The live headline observed on 2026-10-15 at 01:56:53 UTC was:

> Model routers make educated guesses. ModelSpec makes informed, unbiased decisions from evidence.

This supersedes the September 29 decision deliberately. MODEL-244 set the
first line on September 30 in `de5af17e72`,
[PR #427](https://github.com/turbobeest/modelspec/pull/427), merged at
13:58:28 UTC. Later that day, `243b40015d`,
[PR #443](https://github.com/turbobeest/modelspec/pull/443), merged at
21:12:42 UTC, explicitly removed the eyebrow and set the current second line.
Its commit message and PR body attribute those choices to Jamie on September 30.
No headline or eyebrow changes are part of MODEL-397. This item requires no
new failing headline test because the spec directs preservation of the later
deliberate decision.

History commands:

```sh
git log --format='%h %ad %s' --date=iso -- pipeline/landing.py
git blame -L 25,35 pipeline/landing.py
git log --all --format='%h %ad %s' --date=iso --grep='MODEL-244'
git show --format=fuller --stat 243b4001
git show --format=fuller fb1faac0 -- pipeline/landing.py
gh pr view 427 --json title,body,mergedAt,url
gh pr view 443 --json title,body,mergedAt,url
git log -3 --format='%h %ad %s' --date=iso -S '2,500 / month' -- docs/billing.md
```

## Card counts describe different data images

The same public observation returned:

| Output | Value |
| --- | --- |
| Site coverage `catalogue.models` | 1,372 |
| Site coverage `board.models` | 44 |
| Site coverage `catalogue.catalogued_not_decidable` | 1,328 |
| Worker health `model_count` | 1,384 |
| Worker health `policy_model_count` | 1,384 |
| Worker `build.commit` and `service_commit` | `c9b625605750f29ede73ade4d7020eb2714b1513` |
| Worker `build.built_at` | `2026-10-15T01:11:44+00:00` |

Reproduce the read-only public observation:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python -u - <<'PY'
import json
import re
from datetime import datetime, UTC
from urllib.request import urlopen
print('Observed at', datetime.now(UTC).isoformat())
for url in ('https://modelspec.dev/api/coverage.json',
            'https://api.modelspec.dev/v1/health', 'https://modelspec.dev/'):
    with urlopen(url, timeout=30) as response:
        raw = response.read().decode()
    print(url)
    if url.endswith('.json') or url.endswith('/health'):
        data = json.loads(raw)
        keys = ('coverage_version', 'as_of', 'board', 'catalogue',
                'schema_version', 'build', 'service_commit',
                'model_count', 'policy_model_count')
        print(json.dumps({k: data[k] for k in keys if k in data}, sort_keys=True))
    else:
        print(re.sub('<[^>]+>', '', re.search(r'<h1\b[^>]*>(.*?)</h1>', raw, re.S).group(1)))
PY
```

`gh variable get DATA_SPLIT_ENABLED` returned `true`. In that mode,
`pipeline/build.py::main` always calls `build_site` with the public repository
root, even when a private data directory is supplied. `pipeline/coverage.py`
counts the cards loaded from that frozen public image. It separately counts
active admitted models for the decision board.

`api/worker/vendor.py::export_data` overlays the current private data directory,
loads its cards, and builds the ranking and policy catalogues. Both exporters
produce one record per input card, with no decision-admission or quarantine
filter. `api/worker/src/entry.py::_health` counts those serving records.
The engine SHA identifies the code, not the private data revision. The net
12-card difference therefore does not indicate 12 quarantined or excluded
cards. These catalogue totals intentionally differ from decision coverage.

The actual local build confirms that the three catalogue totals agree when
they use the same frozen image, exit 0:

```sh
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import json
from pathlib import Path
root = Path('dist/modelspec/api')
coverage = json.loads((root / 'coverage.json').read_text())
rank = json.loads((root / 'rank/candidates.json').read_text())
policy = json.loads((root / 'policy/catalogue.json').read_text())
counts = (coverage['catalogue']['models'], len(rank['candidates']), len(policy['models']))
print('Frozen image counts (coverage, ranking, policy):', counts)
assert counts == (1372, 1372, 1372)
PY
```

The change adds `catalogue.label` to coverage JSON and `model_count_label` and
`policy_model_count_label` to health JSON. Coverage prose identifies the frozen
image and warns that Worker counts can differ. The landing and method pages
use that prose. The general catalogue and provider-index freshness notice also
identifies the frozen image. The generated CLI coverage bundle is refreshed.

Red-first tests:

- `test_health_and_site_counts_label_their_own_data_images[False/True]`
  initially failed with `KeyError: 'label'`, `2 failed, 29 deselected`, exit 1.
  With labels present: `2 passed, 29 deselected`, exit 0. The tests use real
  snapshot and ranking builders and the Worker HTTP route over synthetic
  bundled bytes. Equal images give 2 cards on each side. One extra private
  card gives 3 Worker cards and 2 public cards. A retired card remains in the
  catalogue total but not the decision board.
- `test_catalogue_page_labels_the_frozen_public_card_count` initially failed
  because the rendered page lacked the image label, `1 failed, 20 deselected`,
  exit 1. After the notice change: `1 passed, 20 deselected`, exit 0.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_worker_compression.py -k health_and_site_counts
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_coverage.py -k catalogue_page_labels
```

Contract review: MODEL-59 permits new fields. Existing count fields retain
their names, types, units, ranges and presence. No enum or nullable range is
widened. Health schema version 1.0, coverage version 1.0, decision contract
2.18 and export schema version 3.0 remain unchanged. OpenAPI is regenerated
with the additional health labels. No legal text, ranking floor, data file or
production switch changes.

## Verification

Tools: Python 3.14.4, pytest 9.1.1, Node v22.22.3, npm 10.9.8,
Playwright 1.63.0, git 2.50.1, gh 2.102.0.
All Node commands use `/Users/terbeest/.nvm/versions/node/v22.22.3/bin`.
Web builds also put `/Users/terbeest/dev/modelspec/.venv/bin` on `PATH` for
the Python prebuild step. Logs are under `.scratch/model-397/` in this worktree.
For logged commands, stdout and stderr were redirected to a file; the shell
saved `$?`, printed the tail, and exited with that saved status.

The final full Python suite passed: `11180 passed, 9 skipped, 11 warnings`,
exit 0, in 1,316.97 seconds. Its log is
`.scratch/model-397/full-pytest-final.log`. The final static site build also
passed, exit 0. The source tree already contained the final wording when it
started; its build identity was captured before that wording was committed.
`api/build.json` records `d483418991c11048c16c0fa1e0f9c515583af2e5` and
`2026-10-15T02:05:25+00:00`. An additional assertion expecting the later
implementation commit in that metadata failed. The artifact checks below
verify the actual final wording. The first full Python run starts on
`8c93b456`; the final rerun starts on `735b1b86`.
Assertions over generated artifacts confirmed the coverage label and
`board.models + catalogued_not_decidable == catalogue.models`, both landing
and method summaries, both catalogue-index freshness notices, and the preserved
headline. The public image still contains 1,372 catalogue cards and 44
admitted decision models.

Completed commands, each with exit 0:

```sh
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.contracts
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m tests.corpus decisions --out web/src/decide/__corpus__
cd web
npm ci
npm run build
MODELSPEC_CORPUS_REQUIRED=1 npm test
CI=true npx playwright test --config=playwright.corpus.config.ts
cd ..
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base c9b625605750f29ede73ade4d7020eb2714b1513 --head HEAD --branch model-397-premarketing
git diff --check
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 4 --summary
```

The corpus generator wrote 319 decisions and 5 vocabularies. The initial web
suite, before corpus generation, passed 843 tests with one skipped file.
With the corpus required, all 53 files and 1,242 tests passed. Chromium passed
104 checks and skipped 6 checks for gate-specific build configurations.
The shard planner assigns 68 files to each shard, with predicted durations
between 3,540.397 and 3,540.400 seconds.
The fast Python focused suite passed 183 tests with 2 skips. The direct
landing-summary and count-label recheck passed 3 tests with 61 deselected.
The final combined landing, Worker and coverage suite passed all 85 tests,
including the landing browser checks, exit 0:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile tests/test_landing.py tests/test_worker_compression.py tests/test_coverage.py
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_api_docs.py tests/test_pricing_v2.py tests/test_worker_compression.py tests/test_agent_copy.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_relations.py -k freshness
```

The additional freshness-notice regression check passed, with 24 deselected.

The first full run returned `14 failed, 11166 passed, 9 skipped`, exit 1,
in 1,362.74 seconds. All failures shared one stale QA capture. The direct
`test_mcp_capture_matches_current_public_sources` assertion showed that
`qa/fixtures/mcp-tools.json` still pinned the previous OpenAPI hash. The
other 13 tests stopped at the same `MCP definitions drifted` guard before
any replay or provider call.

`python -m qa.contracts` refreshed that generated fixture. Comparing the old
and regenerated `tools` arrays proved they are identical; only the
`api/worker/openapi.yaml` entry in `source_hashes` changes. No QA test or
guard was altered. The complete affected suites then passed all 141 tests,
exit 0, in 18.22 seconds:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile tests/test_agent_harness.py tests/test_agent_gaps.py tests/test_agent_guide.py
```

Full-suite commands:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD PYTEST_ADDOPTS='-vv --tb=short' /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
```

The second invocation preserves full collection and uses verbose reporting
so a failure's test name is visible before the final integration test ends.
During it, the machine's one-minute load rose to 49.59. Following the executor
brief, the agent waited 120 seconds in two foreground 60-second waits without
starting new work. Load remained 38.06, so the wait was repeated. The next
check was 18.63. The already-running suite continued during those waits.

The initial focused run caught the API reference's 800-word budget and the
landing renderer's escaping of the apostrophe in the new coverage sentence.
The count reference now lives behind a short link, and the sentence avoids
the apostrophe. The existing tests remain unchanged. That initial run finished
with `2 failed, 434 passed, 2 skipped`, exit 1, in 1,297.26 seconds. Its only
failures were `test_each_reference_is_under_the_word_budget[api.md]` and
`test_landing_copy_uses_the_computed_figures`. It also completed the expensive
private-data isolation checks. The final fast suite and 85-test suite above
recheck both failures successfully.

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile tests/test_pricing_v2.py tests/test_pricing_page.py tests/test_billing.py tests/test_worker_compression.py tests/test_coverage.py tests/test_landing.py tests/test_method.py tests/test_api_docs.py tests/test_legal.py tests/test_private_serving.py
```

## Limits of observation

No new code was deployed, and no post-deployment labels were observed.
The production checks were read-only GETs to the public landing, coverage and
health endpoints. The private model-data checkout was not inspected to
identify the individual cards behind the net 12-card difference.
No payment, refund, Stripe write, vendor model call, device action, workflow
dispatch, Linear write, merge or production-switch change was performed.
The wsl gate was not run. No simulator or tmux session was used.
