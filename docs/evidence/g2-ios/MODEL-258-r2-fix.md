# MODEL-258 round 2 execution evidence

Worktree: `/Users/terbeest/dev/worktrees/model-258-guides`.
Branch: `model-258-guides`. PR: <https://github.com/turbobeest/modelspec/pull/824>.
Review input: `REV-824.verdict.md`, read in full.

Starting SHA: `3d96ca383188f3272323a708a59c68f2cd860128`.
Fetched and merged `origin/main` at `e621e1219aa7702dc1539ef54747f27dbc5f8519`
before changing the implementation. The merge had no conflicts.
Post-merge baseline: `878d631c8feb199688db37ca720837284d618b3e`.
Final implementation and test SHA: `93ee0865d6a497b348f83df1d6583fe11f03a70d`.
The subsequent evidence-only commit records the completed checks; the executor
completion line identifies that final commit.

This record supersedes the decision-reuse and exclusion-list descriptions in
the initial `MODEL-258-fix.md` evidence.

## Changes

The guide receives the canonical decision already computed for the stored
`budget-coding` template. It does not change that template's `explain` setting.
The secondary full explanation returns only exclusion rows. Its decision ID,
probabilities and other decision results cannot enter either page.

The guide groups exclusion rows by failed condition and renders the first ten
examples. Counts describe rows, not distinct models: a model can have multiple
offerings and failed conditions. The linked use-case renderer previously omitted
exclusions, so it now renders the complete supplementary list at `#screened-out`.
The main build computes those reasons once and shares them between both pages.

The DefinedTerm now says "decides which models fit a job and shows its work".
The comparison article visibly displays its `dateModified`, `2026-09-23`.
The task-cost explanation now describes input and output prices.

## Red-first results

All commands below ran from this worktree, except npm commands, which ran from
its `web/` directory. Test processes' exit codes were read directly.
Local log directories can be recreated with:

```sh
mkdir -p docs/evidence/g2-ios/model-258-r2-root docs/evidence/g2-ios/model-258-r2-tests
```

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_guides.py --tb=short -p no:cacheprovider > docs/evidence/g2-ios/model-258-r2-tests/red.log 2>&1
```

Against unchanged implementation after the main merge, exit 1:

```text
8 failed, 5 passed in 24.15s
```

The red failures covered:

- `test_guide_and_linked_use_case_have_same_identifiers[dec_]`: guide
  `dec_0fe8be7430e935c986d5b640`, use-case `dec_46dd76737f6aeb565720ef18`.
- `test_guide_and_linked_use_case_have_same_scores_probability_and_cost`:
  fixture P(best) `0.546875` versus canonical `0.50390625`.
- `test_swapping_public_image_changes_engine_numbers_and_exclusions` and
  `test_guide_keeps_every_band_model_when_results_are_truncated`: canonical
  probability assertions failed.
- `test_large_screened_out_list_stays_a_short_explainer`: 4,443 words exceeded
  the 3,000-word bound with a real-engine fixture containing 400 extra exclusions.
- `test_guide_links_to_full_screened_out_list_on_use_case`: the link target
  and full list were absent.
- `test_guides_have_dated_sitemap_entries_and_visible_structured_data`:
  the comparison date was absent from visible text.
- `test_defined_term_describes_deciding_model_fit_and_showing_work`:
  the requested phrase was absent.

The full frozen-image build reproduced the same defects independently:

```sh
env PYTHONPATH=$PWD PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_holding.py::test_built_guide_and_linked_use_case_show_the_same_decision tests/test_holding.py::test_built_guide_has_a_bounded_exclusion_summary > docs/evidence/g2-ios/model-258-r2-root/red-build.log 2>&1
```

Exit 1, `2 failed in 293.42s`:

```text
'dec_bde9bc2baee43dbd6ffb794e' != 'dec_e714b968d27e687c50bbf4db'
assert 14602 <= 3000
```

## Green focused checks

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_guides.py --tb=short > docs/evidence/g2-ios/model-258-r2-root/green-guides.log 2>&1
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_pipeline.py -k use_case > docs/evidence/g2-ios/model-258-r2-root/focused-use-cases.log 2>&1
env PYTHONPATH=$PWD PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_guides.py tests/test_live_use_cases.py tests/test_comparison_pages.py tests/test_surface_lint.py tests/test_crawler_access.py tests/test_structured_data.py tests/test_sitemap.py tests/test_decide_preview_workflow.py > docs/evidence/g2-ios/model-258-r2-root/focused.log 2>&1
```

All exited 0:

```text
13 passed in 12.72s
15 passed, 47 deselected in 37.48s
186 passed in 143.21s
```

An initial broader-suite invocation used the nonexistent path
`tests/test_use_case_pages.py`; pytest exited 4 without running tests. The
corrected runs above cover `tests/test_pipeline.py` use-case tests and
`tests/test_comparison_pages.py`.

## Site and web checks

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist > docs/evidence/g2-ios/model-258-r2-root/site-build.log 2>&1
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree dist/modelspec > docs/evidence/g2-ios/model-258-r2-root/surface-lint.log 2>&1
```

Both exited 0. Lint result:

```text
dist/modelspec: 0 findings; 5365 files checked
```

From `web/`:

```sh
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm ci > ../docs/evidence/g2-ios/model-258-r2-root/npm-ci.log 2>&1
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm run build > ../docs/evidence/g2-ios/model-258-r2-root/web-build.log 2>&1
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test > ../docs/evidence/g2-ios/model-258-r2-root/web-test.log 2>&1
```

All exited 0. Web tests: 843 passed; 52 test files passed and one skipped.

## Built artifact measurements

The built guide has 978 visible words, ten screened-out examples, and four
reason-count rows. Its linked use-case has all 1,381 exclusion rows. Counts
match the complete list: class 7, context 6, open-weights unknown/fail 1,332,
task cost 36. The ten sample rows match the start of the full list.

Both pages show decision `dec_e714b968d27e687c50bbf4db` and snapshot
`snap_05a963d2477ac2fb`. Their result values match exactly:

| Score | Score interval | P(best) | Cost per task, USD |
| --- | --- | --- | --- |
| 0.6 | [-1.248386, 2.448386] | 0.63671875 | 0.045 |
| 0.0 | [-1.549939, 1.549939] | 0.36328125 | 0.045 |

Both new `tests/test_holding.py` regression functions also passed when invoked
against the completed `dist` tree. An independent read-only review parsed the
same artifacts and confirmed the values, counts, sample, link, date and term
wording. No product IDs from the exclusion list appeared in the guide.

The direct artifact audit exited 0:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY' > docs/evidence/g2-ios/model-258-r2-root/built-guide-audit.log 2>&1
import json
from pathlib import Path
import re
from pipeline.surface_lint import Page
from tests.test_guides import _rows
from tests.test_holding import test_built_guide_and_linked_use_case_show_the_same_decision, test_built_guide_has_a_bounded_exclusion_summary

trees = {"real": Path("dist")}
test_built_guide_and_linked_use_case_show_the_same_decision(trees)
test_built_guide_has_a_bounded_exclusion_summary(trees)
root = Path("dist/modelspec")
guide = (root / "guides/how-to-choose-an-ai-model/index.html").read_text()
use_case = (root / "use-cases/coding/budget-coding/index.html").read_text()
counts = {row[0]: int(row[1]) for row in _rows(guide, "example-exclusion-counts")[1:]}
full_rows = _rows(use_case, "use-case-excluded")[1:]
assert sum(counts.values()) == len(full_rows)
print(json.dumps({
    "visible_words": len(Page(guide).visible.split()),
    "decision_id": re.findall(r"dec_[a-z0-9]+", Page(guide).visible),
    "snapshot_id": re.findall(r"snap_[a-z0-9]+", Page(guide).visible),
    "guide_results": _rows(guide, "example-results"),
    "exclusion_counts": counts,
    "sample_rows": len(_rows(guide, "example-excluded")[1:]),
    "full_exclusion_rows": len(full_rows),
    "built_regressions": "both passed",
}, indent=2))
PY
```

## Full suite

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile > docs/evidence/g2-ios/model-258-r2-root/full-suite.log 2>&1
```

The command waited for the existing lock holder, then ran with four workers.
Exit 0:

```text
11868 passed, 9 skipped, 11 warnings in 1441.39s (0:24:01)
```

This includes both new frozen-build regressions in `tests/test_holding.py`.
The eleven warnings concern unsigned vocabulary fixtures in the CLI tests.

## Versions and limits

Python 3.14.4; pytest 9.1.1; Node v22.22.3; npm 10.9.8;
git 2.50.1; gh 2.102.0.

No production deployment, live browser session, live API decision, private-data
read, or paid-provider call was performed in round 2. The site build reported
existing unregistered hardware-source URL warnings; it exited successfully.
PR #824 was confirmed open and draft before work. It will remain a draft.
No legal terms, ranking logic, contracts or frozen data were changed by this fix.
