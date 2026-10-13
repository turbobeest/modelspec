# MODEL-329 execution evidence

Status: the engine guard is a test on the retained Alibaba Singapore copy.
`OfferingPriceExtractor` already selects the price column (MODEL-341,
`081d7967976ce689ffc6c5cda2015061b27b2201`, an ancestor of the base). The
stored input price stays 2.0. The ledger closure is the companion
`modelspec-data` pull request.

Base SHA: `faed1e6a9d5cb6461c214c2d195e650b2fe1c486`.
The final delivery SHA is the commit that contains this report. Resolve it
with `git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-329-fix.md`.
This file does not embed that hash.

## What the retained copy says

File: `tests/fixtures/verification/914aa685dc8ae8f32ed92b506792e5396983f633e4d5703c8925260131527c9f.html`.
sha256: `914aa685dc8ae8f32ed92b506792e5396983f633e4d5703c8925260131527c9f`.
Size: 667046 bytes.

The audit normaliser is `html-default` with `strip_volatile=False`, then table
locator `0` (source region `singapore-qwen-max`). On the row whose model id
starts with `qwen3.8-max-0902`:

- Column "Input tokens per request" is the request-size band `0<Token≤1M`.
- Column "Input price (per 1 million tokens)" is `$2`.
- The output price on that row is `$6`. This change does not touch it.

The stored fact
`alibaba-model-studio/qwen/qwen3-8-max-0902/singapore/standard#offering.price.input`
stays `2.0` / `known`, cited to this snapshot. The copy agrees with that value.
`verification/log.jsonl` line 19437 records `offering-price-table@1` verified
on 2026-10-10 with an empty diff.

## Defects

| Defect | Red observation | Green observation |
|---|---|---|
| Alibaba input price read the band cell | The pre-`081d7967` header scan, replayed on this copy, selects header `input tokens per request` and value `0<Token≤1M`. The new test cannot fail on this branch: the current extractor already returns `$2` and `compare` against stored `2.0` is empty. Probe exit 0. | `test_retained_alibaba_singapore_table_reads_the_price_column` and the existing synthetic band test: exit 0, 2 passed in 0.48s. Full suite with `CI` unset: exit 0, 10342 passed, 23 skipped, 11 warnings in 1039.68s. |
| Azure gpt-5-4 SOC 2 ledger row still open | No engine reader change. The open `defects.jsonl` row is left as written. Data pull request 35 already stored `type_2` / `known` on source `azure-soc2`, snapshot `sha256:5a2cbf331a059528bc07306b5b735c3492ff9e9f68ee395dd533da8682cd8e94`. `verification/log.jsonl` line 19340: `governance-prose@1`, outcome `verified`, date 2026-10-08, diff null. | The data pull request appends a resolution row. It does not edit the open row and does not add a compliance inference. |

## Commands and results

Commands ran in `/Users/terbeest/dev/worktrees/model-329` unless noted.
`PYTHONPATH=$PWD`. The interpreter is
`/Users/terbeest/dev/modelspec/.venv/bin/python`. Exit codes were read from
the shell variable `ec` or `PROBE_EXIT` / `FOCUSED_EXIT`. `status` is
read-only in this zsh, so it was not used.

Tool versions: Python 3.14.4, pytest 9.1.1, Ruff 0.16.6, Git 2.50.1, gh 2.102.0.

Historical scan and current reader, exit 0. The old scan is the loop at
`decision/verify.py` as of `081d7967^` (first header containing `input tokens`):

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import hashlib
from dataclasses import replace
from pathlib import Path
from decision.normalise import NORMALISERS, Locator, normalise_document, select_region
from decision import verify

sha = "914aa685dc8ae8f32ed92b506792e5396983f633e4d5703c8925260131527c9f"
body = Path(f"tests/fixtures/verification/{sha}.html").read_bytes()
print("sha_ok", hashlib.sha256(body).hexdigest() == sha)
rules = replace(NORMALISERS["html-default"], strip_volatile=False)
text = select_region(normalise_document(body, rules), Locator("table", "0"))
rows = [[c.strip() for c in line.split("|")] for line in text.splitlines() if line.strip()]
headers = [verify.normalise_name(cell) for cell in rows[0]]
row = next(r for r in rows if r[0].startswith("qwen3.8-max-0902"))
for i, header in enumerate(headers):
    flat = header.replace("price per 1m ", "")
    if "inputtokens" in flat.replace(" ", ""):
        if "batch" in header:
            continue
        print(f"old_scan_header={header}")
        print(f"old_scan_value={row[i]}")
        break
claim = verify.Claim(
    target=verify.TargetRef(kind="fact", id="offering#input"),
    subject="provider/lab/model/global/standard",
    names=("qwen3.8-max-0902",),
    field="offering.price.input",
    label="Input",
    value=2.0,
    unit="usd_per_1m_tokens",
    collector=verify.VerificationActor(agent="probe", model_family="none", method="probe"),
    sources=(verify.SourceRef(source_id="pricing", snapshot_ref="sha256:" + "0" * 64, cited_regions=["prices"]),),
)
readings = verify.OfferingPriceExtractor().extract(claim, text)
print("current_reading", [r.value for r in readings])
print("compare_stored_2", verify.compare(claim, readings))
PY
```

Printed:

```text
sha_ok True
old_scan_header=input tokens per request
old_scan_value=0<Token≤1M
current_reading ['$2']
compare_stored_2 []
PROBE_EXIT:0
```

Focused tests, exit 0:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q \
  tests/test_decision_verify.py::test_retained_alibaba_singapore_table_reads_the_price_column \
  tests/test_decision_verify.py::test_band_tiered_table_reads_the_price_column_of_the_lowest_band
```

```text
2 passed in 0.48s
FOCUSED_EXIT:0
```

Full suite. The harness exports `CI=true`, and
`tests/test_social_cards.py` plus `tests/test_landing.py` then fail when
Playwright is absent from `web/node_modules`. That is the same class MODEL-341
recorded. Playwright was not installed and those tests were not edited.
With `CI` unset they skip.

```sh
env -u CI PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
```

```text
10342 passed, 23 skipped, 11 warnings in 1039.68s (0:17:19)
```

Exit file `/tmp/model-329-pytest-noci.exit` contains `0`.

The same command with the harness `CI=true` logged
`3 failed, 10342 passed, 8 skipped, 11 warnings, 12 errors in 1236.82s`.
Every failure and error is the Playwright guard above.

`ruff format` was not run on `tests/test_decision_verify.py`. The file was
already outside the formatter, and formatting it would rewrite pre-existing
lines. `ruff check` still reports pre-existing E501 lines that this edit did
not introduce. The new test lines are within the 100-character limit.

## What was not observed

- The live Alibaba and Microsoft pages were not fetched. No Firecrawl, no
  Artificial Analysis, and no Zapier.
- The trust-audit sampler was not re-run. `decision/verify.py` was not edited.
- The offering value `2.0` was not changed.
- Linear was not edited. Neither pull request was merged.
- A `CI=true` browser pass was not run, because Playwright is not installed
  in `web/node_modules`.
