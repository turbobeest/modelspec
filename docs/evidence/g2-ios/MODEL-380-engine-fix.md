# MODEL-380 engine verification evidence

The fidelity readers now distinguish an unsupported reading from an observed
disagreement. Genuine changed values and stated conditions still produce
mismatches. No comparison tolerance or accuracy threshold changed.

## Revision and environment

- Base SHA: `a333ce7e798972488eac1ab62021065116681567`.
- Final implementation SHA: `7a2b48d48b2badf86a214be828cfacd43bc4fa8b`.
- Full-suite and census SHA: `9abeb4a231167ccc4208a6a08ea022570a3346f7`.
  The final implementation adds only the diagnostic reason count and its test.
- The delivery SHA is the head of this PR. The evidence commit follows the tested
  implementation commit, so the document does not attempt to contain its own hash.
- Worktree: `/Users/terbeest/dev/worktrees/model-380-engine`.
- Branch: `sparksandsawdust/model-380-readers`.
- Python `3.14.4`, pytest `9.1.1`, Node `v22.22.3`, npm `10.9.8`,
  Chromium `153.0.8010.12`, git `2.50.1`, gh `2.102.0`.
- Private archive: `modelspec-data` origin/main
  `20c154d89c5bc8ace0601d95ab2785b6fa6592d1`, read only.

All committed source fixtures are synthetic. Live reports and baseline replay
scripts stay under `/tmp/model-380-engine`, outside the public repository.

## Defects and red-first observations

| Class | Regression test | Observed red result | Corrected behavior |
| --- | --- | --- | --- |
| A | `test_missing_licence_source_kind_is_undetermined` | Both changed-source and same-bytes cases reported mismatch instead of undetermined. | A rejection consisting only of unknown source kind is undetermined. |
| B | `test_absent_plan_wording_is_undetermined`, `test_unrelated_card_feature_is_undetermined`, `test_raw_inline_markup_is_undetermined`, `test_absent_coverage_quote_is_undetermined` | Missing wording produced headings, prices, unrelated features, or raw markup. Identical bytes could also promote no reading to mismatch. | Quote candidates must match the stored wording. Allowance and agent-use candidates must describe the relevant fact. Missing readings remain undetermined. |
| C | `test_unidentified_model_list_is_undetermined` | Unidentified plan prose was compared against a model-ID list. | Lists with identifiable models use the existing ID/name comparison. Unidentified prose is undetermined; explicit empty lists and identified subset disagreements remain observable. |
| D | `test_benchmark_key_value_reader_uses_explicit_source_unit`, `test_benchmark_missing_optional_conditions_has_no_determination`, `test_benchmark_without_source_unit_has_no_determination` | Explicit units were ignored. Missing source units, effort, and date produced mismatches. | Explicit units reach the existing stored-precision comparison. Missing metadata is undetermined; stated score and condition disagreements remain mismatches. |
| E | `test_price_reader_selects_the_models_own_table`, `test_price_reader_never_verifies_the_table_above_the_model`, `test_price_reader_requires_the_table_owners_exact_model` | A preceding model's table could cause both false mismatch and false verification. A longer sibling declaration could falsely name the target. | A generic price table belongs to its immediately preceding exact model declaration. Missing target rates are undetermined. |
| F | `test_unsupported_open_tool_list_is_undetermined` | A closed list from `subscription-page@1` disagreed with a claim containing `coding_tool:*`. | This reader returns no reading for an open tool list. Changed closed tool lists still disagree. |

The first licence run exited 1 with `2 failed, 4 passed in 0.74s`.
The first quote run exited 1 with `4 failed, 2 passed in 0.34s`.
The initial subscription-type run exited 1 with `3 failed, 4 passed in 0.55s`.
The initial evidence/price run exited 1 with `15 failed, 4 passed in 0.37s`.
Additional cases were reproduced before their fixes, including exact table
ownership and unchanged-source confidence. The initial 68-case regression set
replayed against the base SHA exited 1 with `45 failed, 23 passed in 2.19s`.
The 76 reader cases exited 1 against the base SHA with `50 failed, 26 passed in
0.59s`; they include the later score-unit and team-wording cases below. The final
77-case set, including the reporting regression, exits 1 against the base SHA
with `51 failed, 26 passed in 0.82s`.

The first focused suites exit 0 with `526 passed in 2.60s`. Including the existing
price reread suite gives `615 passed in 3.56s`, exit 0. After integrating current
main, the complete focused suites give `620 passed in 9.78s`, exit 0. Preservation tests
cover an identified missing model, an additional identified model, explicit model
withdrawal, a changed closed tool list, a changed allowance, a stated tool
restriction, a changed score, a changed price, and conflicting effort or date even
when other metadata is absent. Core verification still refuses an unsupported
licence absence. Known disallowed source kinds still cause fidelity mismatches.

Class A is a registry metadata defect. The 41 supplied licence failures cite 25
sources missing top-level `kind` in both the frozen public registry and private
origin/main. `Source.kind` defaults to null, `StoredRegions.source_kind` forwards
it, and `_absence_block` reports unknown. The private overlay did not drop the
tags. Correcting those tags belongs in `modelspec-data`; this PR changes only the
nightly classification when the metadata prevents a value reading.

The first full-suite run exited 1 with `10 failed, 10497 passed, 23 skipped,
11 warnings in 1358.31s`. Eight existing price reread cases exposed valid
consumption and rolling-window wording missing from the relevance predicate.
The focused reproduction exited 1 with `8 failed, 81 deselected in 10.22s`.
The corrected predicate keeps those allowance readings, and all eight cases pass
without changing the tests or the narrow-region write safeguards.

Two social-card cases failed because the worktree lacked `@playwright/test`.
The Node error occurred before the unchanged renderer ran. The isolated layout
test reproduced the failure, exit 1 after 55.47s. `npm ci` installed the local
dependencies, and a headless Chromium launch and close passed. The two social-card
tests then exited 0 with `2 passed in 321.16s`. No package manifest, lockfile, or
browser installation changed.

Current main added MODEL-235's unchanged performance test requiring many recrawl
quote candidates. The merged focused run exposed the conflict, exit 1 with
`1 failed, 619 passed in 2.86s`; the broad rerun started prematurely and was stopped
with exit 143, so it is not counted as validation. `quote_candidates` now supplies
possible recrawl replacements. Each still verifies against the cited region,
and the narrow-region write guard remains intact. Ordinary `extract` retains
only matching quotes. The original performance assertions and per-fact document
cache from PR #737 remain intact.

Installing Playwright also activated twelve landing browser cases that previously
skipped. Their shared fixture requires `web/dist/decide.html` and built assets.
The isolated case reproduced a `FileNotFoundError`, exit 1 with one setup error
in 0.46s. The broad run showing those setup errors was stopped, exit 143, and is
not counted as completed validation. The local web build then exited 0. It used
`npm --ignore-scripts run build` to execute TypeScript and Vite without the
`prebuild` metadata writer. All 32 landing tests subsequently passed in 170.55s.
The build changed no tracked source or data files.

The first corrected live sweep still reported seven banking-score mismatches
because raw numeric text had a trailing comma parsed as an unregistered unit.
`test_benchmark_unrecognized_source_unit_has_no_determination` reproduced that
case and an unknown explicit unit: exit 1, `2 failed, 3 passed, 30 deselected in
0.23s`. Fidelity now treats those units as insufficient metadata. Known conflicting
units and a stated effort conflict remain mismatches. A replay of all seven
current HTTP 200 sources produces seven undetermined readings with reason
`missing_source_metadata`, zero mismatches, and zero verified readings.
The retained-copy replay uses no network and gives the same result. Ten probes
preserve changed scalar/composite scores, stated interval/count changes,
conflicting conditions, and known-unit disagreements even when other metadata
is absent. The evidence/price file independently passes all 35 cases.

The same sweep exposed a team-plan scope error. A one-word individual tier alias
let an individual card supply a team offering's agent wording.
`test_team_plan_without_its_own_wording_is_undetermined` reproduced false mismatch
and false verification: exit 1, `2 failed, 1 passed in 0.25s`. Team offerings now
exclude one-word aliases without a team identity, while retaining compound seat
aliases. An initial broader run caught three existing seat-allowance regressions
from excluding too many aliases (`3 failed, 773 passed in 10.24s`). The refined
fix preserves those tests unchanged. The final focused run exits 0 with
`776 passed in 11.07s`. Replay against the exact retained Cursor source produces
no subscription readings and an undetermined outcome.

A final report audit found that the undetermined total included seven
`missing_source_metadata` rows while the diagnostic reason map counted only the
three previous reasons. `test_fidelity_report_counts_missing_metadata_reason`
reproduced the omission through `data_fidelity`, using a synthetic HTTP fetcher:
exit 1, `1 failed, 35 deselected in 0.18s`. Adding the missing reason to that map
changes neither comparison nor gating. After the full suite completed, the final
focused suites exited 0 with `777 passed in 9.11s` on the final implementation.
The diagnostic reason is documented beside the existing reasons. This report
details map has no declared closed enum; the Decision, CLI, and API contracts
were not changed by this fix.

## Commands

Commands run from the assigned worktree unless another directory is stated.
Each command's exit code was read directly, without a pipeline.

```bash
git rev-parse HEAD
git status --short --branch
/Users/terbeest/dev/modelspec/.venv/bin/python --version
/Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --version
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --version
git --version
gh --version

TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model380_licence_metadata.py
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model380_subscription_quotes.py
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model380_subscription_types.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model380_evidence_prices.py

TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model380_subscription_quotes.py tests/test_model380_subscription_types.py tests/test_model380_evidence_prices.py tests/test_model380_licence_metadata.py tests/test_decision_verify.py tests/test_accuracy.py
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_price_reread.py -k free_text_changes
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_price_reread.py tests/test_model380_subscription_quotes.py tests/test_model380_subscription_types.py tests/test_model380_evidence_prices.py tests/test_model380_licence_metadata.py tests/test_decision_verify.py tests/test_accuracy.py
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model380_evidence_prices.py -k 'unrecognized_source_unit or stated_known_unit or unknown_unit_does_not_hide'
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model380_cursor_wording.py
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model380_evidence_prices.py -k fidelity_report_counts_missing_metadata_reason
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model380_licence_metadata.py tests/test_model380_subscription_quotes.py tests/test_model380_subscription_types.py tests/test_model380_evidence_prices.py tests/test_model380_cursor_wording.py tests/test_decision_verify.py tests/test_accuracy.py tests/test_price_reread.py tests/test_price_reread_fallback.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/pytest_shards.py --shard-count 4 --summary

# From web/:
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm --ignore-scripts run build
# From the assigned worktree:
TZ=UTC PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_social_cards.py::test_build_emits_every_template_preview_and_card tests/test_social_cards.py::test_every_frozen_template_card_has_clean_chromium_layout
env -u FIRECRAWL_API_KEY -u ANTHROPIC_API_KEY -u MISTRAL_API_KEY TZ=UTC PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_landing.py

git -C /Users/terbeest/dev/modelspec-data fetch origin main
git fetch origin
git merge origin/main -m 'Merge origin/main for MODEL-380 validation

Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
git fetch origin
git merge --no-edit origin/main
git commit --amend --no-edit --trailer 'Co-Authored-By: ChatGPT Codex <noreply@openai.com>'

env -u FIRECRAWL_API_KEY -u ANTHROPIC_API_KEY -u MISTRAL_API_KEY TZ=UTC PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile

git diff --check
git restore -- verification/log.jsonl verification/queue/events.jsonl

# Delivery, after validation:
CI_LOCAL_SKIP=1 git push -u origin sparksandsawdust/model-380-readers
# From /tmp:
gh pr create -R turbobeest/modelspec --draft --base main --head sparksandsawdust/model-380-readers --title "accuracy: reader false positives become undetermined (MODEL-380)" --body-file /tmp/model-380-engine/pr-body.md
```

The private archive was created with Python's `subprocess.run` and `tarfile` so
the archive command's exit status was checked directly:

```python
from pathlib import Path
import subprocess
import tarfile

scratch = Path('/tmp/model-380-engine')
scratch.mkdir(exist_ok=True)
archive = scratch / 'private-main.tar'
with archive.open('wb') as output:
    subprocess.run(['git', '-C', '/Users/terbeest/dev/modelspec-data',
                    'archive', 'origin/main'], stdout=output, check=True)
destination = scratch / 'private-main'
destination.mkdir(exist_ok=True)
with tarfile.open(archive) as source:
    source.extractall(destination, filter='data')
```

The final regression set can be replayed against the original modules without
changing worktree files. Module filenames retain their repository locations so
the baseline resolves the real frozen catalogue and registry:

```python
import importlib
from pathlib import Path
import subprocess
import sys
import types
import pytest

repo = Path.cwd()
for name, relative in (('decision.verify', 'decision/verify.py'),
                       ('scripts.accuracy', 'scripts/accuracy.py')):
    parent_name, attribute = name.rsplit('.', 1)
    parent = importlib.import_module(parent_name)
    module = types.ModuleType(name)
    module.__file__ = str(repo / relative)
    module.__package__ = parent_name
    sys.modules[name] = module
    setattr(parent, attribute, module)
    source = subprocess.check_output(['git', 'show', f'a333ce7e:{relative}'], text=True)
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
raise SystemExit(pytest.main(['-q', 'tests/test_model380_licence_metadata.py',
                             'tests/test_model380_subscription_quotes.py',
                             'tests/test_model380_subscription_types.py',
                             'tests/test_model380_evidence_prices.py',
                             'tests/test_model380_cursor_wording.py']))
```

Executed as `env -u FIRECRAWL_API_KEY -u ANTHROPIC_API_KEY -u MISTRAL_API_KEY TZ=UTC PYTHONPATH=$PWD
/Users/terbeest/dev/modelspec/.venv/bin/python
/tmp/model-380-engine/run-baseline.py`, with output in
`/tmp/model-380-engine/all-baseline-delivery-red.log` for the final replay.

## Full sweep

The supplied 2026-10-13 sweep had 78 mismatches, 1,876 undetermined readings,
3,824 verified readings, 15 unreachable sources, and 39 public-image-lag cases.
The fresh baseline on the same implementation and current private archive had
76 mismatches, 1,875 undetermined readings, 3,820 verified readings, 20 unreachable
sources, and 41 public-image-lag cases. Its command exited 1.

```bash
env -u FIRECRAWL_API_KEY -u ANTHROPIC_API_KEY -u MISTRAL_API_KEY PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/accuracy.py --root $PWD --profile nightly --layers data_fidelity --sample-size 100000 --output-dir /tmp/model-380-engine/before --private-data-root /tmp/model-380-engine/private-main
```

The first completed green full suite exited 0 with `10538 passed, 8 skipped, 11 warnings in
1544.07s`. The complete run used UTC, four workers with file distribution,
Node 22.22.3, and the three paid-provider keys unset. Output is retained at
`/tmp/model-380-engine/full-pytest-final.log`.

The delivery full suite, at the full-suite SHA above, exits 0 with `10554 passed,
8 skipped, 11 warnings in 1328.13s (0:22:08)`. It uses the same UTC/four-worker
command and environment. Output remains at
`/tmp/model-380-engine/full-pytest-delivery.log`. The subsequent reporting-only
change was checked by the 777-test focused run, including the actual public
fidelity-report path, rather than repeating unchanged build and browser tests.

The final live sweep uses the same private archive and all eligible frozen public
verified values. Its command is:

```bash
env -u FIRECRAWL_API_KEY -u ANTHROPIC_API_KEY -u MISTRAL_API_KEY PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python scripts/accuracy.py --root $PWD --profile nightly --layers data_fidelity --sample-size 100000 --output-dir /tmp/model-380-engine/after-final --private-data-root /tmp/model-380-engine/private-main
```

The completed final census exits 1 with the following counts. All 5,832 eligible
values were drawn; 3,844 could be assessed against current copies. The request
for 100,000 assessed values remains an active gate. Six real disagreements and
eleven unreachable readings also remain failures. The undetermined share is
0.3362 against the unchanged ceiling of 0.6. All 443 sources used plain HTTP,
and Firecrawl credits used were zero. The raw report stays in scratch at
`/tmp/model-380-engine/after-final/accuracy.json`.

| Outcome | Fresh baseline | Final implementation |
| --- | ---: | ---: |
| Mismatch | 76 | 6 |
| Undetermined | 1,875 | 1,947 |
| Verified | 3,820 | 3,827 |
| Unreachable | 20 | 11 |
| Public image lag | 41 | 41 |

The first corrected census, before the final unit and team-scope fixes, exited 1
with 14 mismatches, 1,939 undetermined, 3,827 verified, 11 unreachable, and 41
public-image-lag cases. Its report remains at `/tmp/model-380-engine/after`.
The final census ran at the full-suite SHA before the reporting-only correction.
Its sample contains 1,874 `source_changed`, 66 `source_unchanged`, and seven
`missing_source_metadata` undetermined rows, totaling 1,947. The later reason-map
fix accounts for those seven rows without changing any outcome or gate.

One source disagreement was independently audited before the final sweep:
`fact:alibaba-model-studio/subscription/coding-pro#offering.subscription.models_covered`.
The [official Coding Plan page](https://www.alibabacloud.com/help/en/model-studio/coding-plan)
has one supported-model row under the matching Pro column and explicitly limits
support to its listed exact versions. The six published labels resolve uniquely;
no label is missing or ambiguous in the catalogue. The stored public and private
facts each contain nine models, and the three additional stored models have no
known alias anywhere in the fetched page. The cited URL, regions, and normaliser
are identical in both data images. Verification of the current HTTP 200 copy
returns a value mismatch. This is a data disagreement, not a different table,
partial list, or lost model alias. The proof and fetched page remain outside the
repository at `/tmp/model-380-engine/subscription_types`.

Five GitHub model-list disagreements were also checked against both the
[plans page](https://docs.github.com/en/copilot/get-started/plans) and its linked
[supported-models reference](https://docs.github.com/en/copilot/reference/ai-models/supported-models).
Both current availability tables resolve to the same catalogue IDs. Every extra
stored model appears only in the reference's retirement history, dated
2026-10-02. Public and supplied private facts are identical; no private correction
applies. Preview or fast-mode label cleanup restores none of the missing IDs.
The existing treatment of uncatalogued models remains unchanged.

| Remaining data target (`offering.subscription.models_covered`) | Stored count | Identified current count | Source evidence |
| --- | ---: | ---: | --- |
| `alibaba-model-studio/subscription/coding-pro` | 9 | 6 | Closed exact-version list; three stored additions absent throughout the source. |
| `github-copilot/subscription/pro` | 20 | 17 | Three stored additions retired on 2026-10-02. |
| `github-copilot/subscription/business` | 29 | 25 | Four stored additions retired on 2026-10-02. |
| `github-copilot/subscription/pro-plus` | 31 | 27 | Four stored additions retired on 2026-10-02. |
| `github-copilot/subscription/enterprise` | 29 | 25 | Four stored additions retired on 2026-10-02. |
| `github-copilot/subscription/max` | 30 | 26 | Four stored additions retired on 2026-10-02. |

## Observational limits

The run uses deterministic readers and plain HTTP. No paid renderer, live model
reader, production switch, private-data write, Linear write, or deployment was
part of this work. Live source and transport changes can change sweep counts.
The exhaustive request does not imply that 100,000 eligible verified values exist.
The configured sample floor and undetermined ceiling remain active.

`StoredRegions` is unchanged relative to the integrated main branch. The required
`git fetch origin` and `git merge origin/main` first reported already up to date.
A second fetch integrated main `56c39ac3a826af6f79f8755c49ed52b68bad37c4`
with merge commit `1631b60e7d8bfefa0b97e9e29d3094cbaac78b3a`, preserving PR #737's
cache implementation and tests.
A final pre-validation fetch and merge integrated main
`0b4bab44eb5835bda1bcf70eb0c8ec74f171d426` as merge commit
`9abeb4a231167ccc4208a6a08ea022570a3346f7`, used by the full suite and census.
No conflict occurred. The shard summary exits 0 with 65, 64, 64, and 64
test files, respectively.
