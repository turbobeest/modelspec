# MODEL-329 execution evidence

The engine guard reads a synthetic HTML table. The retained vendor page is
gone. `OfferingPriceExtractor` already selects the price column. That reader
landed in MODEL-341, commit `081d7967976ce689ffc6c5cda2015061b27b2201`, which
is an ancestor of this branch. The stored input price stays 2.0. The ledger
closure stays in the companion `modelspec-data` pull request.

Fix base SHA: `dfa4694f9c70621f602521c6f99dbcf88676efad`.
Code SHA: `211552cd516678f323da541050b4539fcfa14c08`.
The final SHA is the commit that contains this report. Resolve it with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-329-fix.md`.

GitHub's pull request base at review time was
`543bc4f4e4b0802bc606bd2bc710d2cb23931ebc`. The merge-base with the local
`origin/main` during this run was `faed1e6a9d5cb6461c214c2d195e650b2fe1c486`.

## Defect

`tests/fixtures/verification/914aa685dc8ae8f32ed92b506792e5396983f633e4d5703c8925260131527c9f.html`
was a 667046-byte vendor HTML page committed in `dfa4694f`. `CONTRIBUTING.md`
requires third-party material to name its source and a licence that permits
the use. No such licence is recorded for that page. The file is deleted.

The replacement is `tests/fixtures/verification/alibaba-singapore-band-price.html`,
187 bytes, written for this test. After `html-default` with
`strip_volatile=False` and table locator `0`:

- The header `Input tokens per request` is the band `0<Token≤1M`.
- The next header, `Input price (per 1 million tokens)`, is `$2`.
- The row begins with `qwen3.8-max-0902`.

## Red and green

| Defect | Red | Green |
|---|---|---|
| Retained vendor page has no reuse licence | `test_retained_alibaba_singapore_table_reads_the_price_column` on the 667046-byte file, with `assert len(body) < 1000` added. `AssertionError: assert 667046 < 1000`. 1 failed in 0.38s. `RED_EXIT:1`. | Same test on the 187-byte table, plus `test_band_tiered_table_reads_the_price_column_of_the_lowest_band`. 2 passed in 0.38s. `FOCUSED_EXIT:0`. |
| The pre-MODEL-341 header scan reads the band cell | Historical `OfferingPriceExtractor` from `081d7967^`, loaded into the current module and run on the synthetic table. `AssertionError: assert ['0<Token≤1M'] == ['$2']`. 1 failed in 0.21s. `HISTORICAL_EXTRACTOR_TEST_EXIT=1`. | The current extractor returns `$2`, and `compare` against stored 2.0 is empty. Covered by the focused run above. |

`tests/test_decision_verify.py` then passed: 390 passed in 1.28s.
`VERIFY_MODULE_EXIT:0`.

`git diff --check` on the code commit was exit 0.

The first full suite, run on `211552cd` while this file still named a removed
source, exited 1. `tests/test_removed_sources.py::test_no_tracked_file_names_a_removed_source`
failed. 1 failed, 10341 passed, 23 skipped, 11 warnings in 1268.78s.
Exit file `/tmp/model-329-fix-pytest.exit` contained `1`. This rewrite drops
that name. The rerun exited 0: 10342 passed, 23 skipped, 11 warnings in
1236.91s (0:20:36). Exit file `/tmp/model-329-fix-pytest2.exit` contained `0`.
These counts were written after that run. The removed-source guard was run
again on this finished text.

## Commands

Commands ran in `/Users/terbeest/dev/worktrees/model-329`. `PYTHONPATH=$PWD`.
The interpreter is `/Users/terbeest/dev/modelspec/.venv/bin/python`. Exit codes
were the shell status of the pytest process, written to `RED_EXIT`,
`FOCUSED_EXIT`, `VERIFY_MODULE_EXIT`, or `/tmp/model-329-fix-pytest.exit`.
No pipe sat between pytest and that status.

Tool versions: Python 3.14.4, pytest 9.1.1, Ruff 0.16.6 from the venv,
Git 2.50.1, gh 2.102.0.

Red, exit 1:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_decision_verify.py::test_retained_alibaba_singapore_table_reads_the_price_column
```

Focused, exit 0:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_decision_verify.py::test_retained_alibaba_singapore_table_reads_the_price_column \
  tests/test_decision_verify.py::test_band_tiered_table_reads_the_price_column_of_the_lowest_band
```

Verify module, exit 0:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_decision_verify.py
```

Historical extractor, exit 1, expected:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import ast
import subprocess
import sys
from unittest.mock import patch
import pytest
from decision import verify

historical_ref = '081d7967976ce689ffc6c5cda2015061b27b2201^:decision/verify.py'
source = subprocess.run(['git', 'show', historical_ref], check=True, capture_output=True, text=True).stdout
node = next(n for n in ast.parse(source).body if isinstance(n, ast.ClassDef) and n.name == 'OfferingPriceExtractor')
namespace = dict(vars(verify))
exec(compile(ast.Module(body=[node], type_ignores=[]), historical_ref, 'exec'), namespace)
with patch.object(verify, 'OfferingPriceExtractor', namespace['OfferingPriceExtractor']):
    result = pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_decision_verify.py::test_retained_alibaba_singapore_table_reads_the_price_column'])
print(f'HISTORICAL_EXTRACTOR_TEST_EXIT={result}')
sys.exit(result)
PY
```

Full suite, `CI` unset. The first run is the failure recorded above.

```sh
env -u CI PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
```

`ruff check tests/test_decision_verify.py --select E501` reports pre-existing
long lines. The lines this edit added are within 100 characters. `ruff format`
was not run on the file.

## What was not observed

- The live vendor pages were not fetched. No paid provider call was made.
- `decision/verify.py` was not edited. The offering value 2.0 was not changed.
- Offering files that cite snapshot `sha256:914aa685dc8ae8f32ed92b506792e5396983f633e4d5703c8925260131527c9f` were not edited. They cite the collected snapshot. They do not contain the page.
- `modelspec-data` pull request 69 was not edited. Its resolution row still says `test_retained_alibaba_singapore_table_reads_the_price_column` runs on that retained snapshot. The test name remains. The bytes it reads are now the synthetic table.
- Linear was not edited. Pull request 730 was not merged.
- A browser pass with `CI=true` was not run. Playwright is not installed under `web/node_modules`.
