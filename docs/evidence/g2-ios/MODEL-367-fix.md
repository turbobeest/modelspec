# MODEL-367 execution evidence

Engine base: `34c6dbef95371cff728a7a28aba33dcffe3e50e3`.
Design-only first commit: `433c78eb`.
Implementation and private engine pin: `778e626505abb3c3a2687522c1c3759d42a05565`.
Private data base: `b058eb531138d7b16915f911e6b68a277b8279a9`.
Final private data commit: `fe1b57b5eaf8c80acd9f37a9d6ae1649bec682ed`,
draft [data PR #95](https://github.com/turbobeest/modelspec-data/pull/95).
The final engine SHA is the commit containing this evidence, reproducible with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-367-fix.md`.

## Result and limits

The current pricing page no longer contains the SuperGrok Lite/Heavy columns
specified by the ticket. There is no approved consumer template and no positive
consumer curation. The private report records the seven observed headers and
the eight unsupported consumer claims. No new plan is treated as an alias or
successor of an old plan. No retirement is inferred.

The separately reviewed Business matrix names Grok 4.7. Its header and glyph
ownership were independently checked against the retained DOM and screenshot.
The exact reader binds the raw copy SHA-256, full normalized HTML and selected
DOM region, then
checks literal headers, row labels and SVG hashes. Whole-document binding
intentionally rejects unrelated page changes until reviewed again.

The private source copies, screenshots and reuse review remain in the private
data PR. The public engine contains only hashes, required short labels and
synthetic test matrices. Source evidence is not bundled in the Worker.

Consumer allowances and quotes already quarantined in the baseline retain
their history. The two remaining admitted Heavy null facts and the stale
Business quote are withdrawn to unknown. Business models can be filed only
following a successful retained-copy replay by `xai-exact-template@1`.

## Retrieval

The first full-Chromium headless attempt received HTTP 403 for pricing,
Business and consumer terms. Those receipts are retained privately under
`research/model-367/attempt-1/`. A headed attempt waiting for network idle
exceeded 60 seconds and exited 1; its `finally` closed the browser.

The successful attempt used full headed Chromium, its standard user agent,
1440 by 1100 viewport, DOMContentLoaded, and at most five additional seconds
for network idle. Pricing, Business, consumer terms and robots returned 200.
A second batch retained enterprise terms, acceptable-use policy and
X-subscription terms, all 200. The private manifests hash decompressed rendered
HTML bytes; the reader hashes its documented StoredRegions representation.

Reuse terms were checked from the current retained pages. Robots permission
and content signals are not a redistribution licence. The private note records
restrictions and claims no broad licence or legal clearance. No source bodies
are published in the engine PR.

Reproduce the successful retrieval into a new private directory:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm --prefix web ci
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node \
  docs/evidence/g2-ios/MODEL-367/capture.mjs PRIVATE_DIRECTORY \
  pricing=https://x.ai/pricing business=https://x.ai/grok/business \
  terms=https://x.ai/legal/terms-of-service robots=https://x.ai/robots.txt
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node \
  docs/evidence/g2-ios/MODEL-367/capture.mjs PRIVATE_REUSE_DIRECTORY \
  enterprise-terms=https://x.ai/legal/terms-of-service-enterprise \
  acceptable-use=https://x.ai/legal/acceptable-use-policy \
  subscription-terms=https://x.ai/legal/x-subscription-terms-of-service
```

A new capture is expected to fail the approved full-document hash until
reviewed. It must not automatically replace the approved template.

## Tools

Python 3.14.4, pytest 9.1.1, Node 22.22.3, npm 10.9.8,
Playwright 1.63.0, Chromium 153.0.8010.12, Git 2.50.1,
GitHub CLI 2.102.0 and flock 0.4.0.

## Red-first checks and final validation

`test_unreviewed_matrix_never_falls_back` and
`test_no_approved_consumer_template_cannot_verify_absence` reproduced the
legacy admission path. The initial unchanged-code run had 25 failures and two
passes, exit 1. `reader-red.txt.gz` preserves its raw output. Adding the
approved synthetic matrix tests before the new module existed produced the
same 25 failures, two passes and 26 setup errors, exit 1, retained in
`reader-template-red.txt.gz`. Those setup errors are not claimed as behavioral
failures of an implemented exact parser. `reader-green.txt` is the initial
53-pass reader run before the independent-review regressions were added;
`reader-focused-green.txt` is the final 658-pass focused run.

`test_reviewed_matrix_mutation_cannot_fall_through` uses the same immutable
approved synthetic template for its positive controls and all nine mutations,
including the six required cases. It never approves a hash derived from the
mutated input. The model and product positive controls cover both columns and
both check/minus meanings; the API-access claim still fails.

Independent review reproduced `test_excerpt_cannot_hide_changed_document_ownership`
as one failed test, exit 1, before the source metadata fix. Its raw output is
`reader-excerpt-red.txt.gz`. The final source must use `text-default` and the
actual whole-page locator, not merely a region called `page`. The final reader
suite has 61 passing cases; the broader focused run has 658 passes, exit 0,
in `reader-focused-green.txt`. The reviewer independently repeated the excerpt
attack and actual private Business replay after the fix.

A second independent review found that NFKC normalization could hide changes
to raw SVG commands and text. The four cases in
`test_normalization_cannot_hide_changed_raw_template_bytes` each failed before
the fix, exit 1, retained in `reader-raw-bytes-red.txt.gz`. Local Chromium
confirmed that the fullwidth SVG command and digit mutations changed a
ten-unit path into a zero-length path. The template now requires its approved
raw copy hash in addition to the normalized document and region hashes.
CopyStore validates bytes against that reference. All four mutations now
report drift, and the actual retained Business copy still verifies. The
reviewer independently reran both checks and found no remaining blocker.

The renderer probe ran from `web/` against a local blank page, made no network
request, and exited 0. This is its complete Node command:

```sh
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node <<'JS'
const {chromium}=require('playwright');
(async()=>{
  const browser=await chromium.launch({headless:true});
  try {
    const page=await browser.newPage();
    const results=await page.evaluate(()=>{
      return ['M3 8H13','M３ 8H13','Ｍ3 8H13'].map(d=>{
        const path=document.createElementNS('http://www.w3.org/2000/svg','path');
        path.setAttribute('d',d);
        const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
        svg.appendChild(path);document.body.appendChild(svg);
        try {return {d,length:path.getTotalLength()};}
        catch(error) {return {d,error:String(error)};}
      });
    });
    console.log(JSON.stringify({browser:browser.version(),results},null,2));
  } finally {await browser.close();}
})();
JS
```

The web dependency install, web build, static-site build, and all 843 web
tests passed, exit 0. `site-build.txt.gz` retains the static-site output, including
frozen-data source-registration warnings.
`web-build.txt` and `web-tests.txt.gz` retain build/test output. The full engine
suite ran under the required shared lock with four workers and passed:
11,583 passed, 9 skipped, 11 warnings in 1,318.98 seconds (21:58), direct
exit 0. `full-suite.txt.gz` retains the complete output. The run acquired the
lock after the final raw-byte binding was committed and tested that final
implementation. Compressed logs preserve the original bytes, including
trailing blank lines in the web test output.

The private normal snapshot shrank from 2,862,805 to 2,861,413 JSON bytes and
from 361,532 to 361,442 gzip bytes. The actual snapshot build asserts all eight
consumer facts and the stale Business quote are absent and Business models
contains only `xai/grok-4-7`. These are output assertions, not estimates from
source diff size. Snapshot hashes and logs remain private. The Worker vendor
map is unchanged and its import-closure check passes. This is not a live
Worker memory probe.

Commands ran in the engine worktree unless a working directory is stated:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_xai_matrix_reader.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_xai_matrix_reader.py -k excerpt
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_xai_matrix_reader.py -k normalization_cannot_hide
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_xai_matrix_reader.py tests/test_decision_verify.py tests/test_decision_sources.py tests/test_model380_subscription_types.py tests/test_model380_subscription_quotes.py tests/test_subscription_availability_reader.py tests/test_model_396_readers.py tests/test_worker_vendor_imports.py
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH /opt/homebrew/bin/flock /tmp/modelspec-fullsuite.lock env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
# In web/:
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH npm run build
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm test
# Back in the engine:
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out dist
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/chart_check_pr.py --base 34c6dbef95371cff728a7a28aba33dcffe3e50e3
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check decision/xai_matrix.py tests/test_xai_matrix_reader.py docs/evidence/g2-ios/MODEL-367/snapshot_size.py
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/data_freeze_guard.py --base 34c6dbef95371cff728a7a28aba33dcffe3e50e3 --head HEAD --branch model-367-xai-matrix
git diff 34c6dbef --check
/Users/terbeest/dev/modelspec/.venv/bin/python scripts/prepare_data_writer.py --engine $PWD --data /Users/terbeest/dev/worktrees/data-model-367
mkdir -p tmp/model-367/root
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-367/snapshot_size.py /Users/terbeest/dev/worktrees/data-model-367 /Users/terbeest/dev/worktrees/data-model-367/research/model-367/snapshot-after-proof.json --expect-curated
```

The first private suite attempt could not import the new module because
`prepare_data_writer.py` copies only Git-tracked engine files. That run exited
2 with four collection errors. After committing the module and preparing
again, the private suite passed 966 tests with 17 existing skips, exit 0.
The final raw-byte fix was then prepared and the suite rerun with reader tests:
1,027 passed and 17 existing skips in 173.18 seconds, exit 0. Its failed setup log and
final result are retained privately. No test was weakened or skipped to
resolve that setup failure.

## Unobserved outcomes

No current positive Lite/Heavy matrix was observed. Synthetic positives prove
reader behavior only. No mapping from the new subscription names to legacy
plans, current legacy-plan allowance, or API permission was established.
No live Worker memory measurement or production deployment occurred. No paid
provider call, Firecrawl credit, Linear write, workflow dispatch or merge was
performed. The draft data pin depends on the engine commit reaching main. The first
private CI run, [39108614971](https://github.com/turbobeest/modelspec-data/actions/runs/39108614971),
stopped at that exact check with exit 1: the pin is not on engine main.
`gh run view 39108614971 --repo turbobeest/modelspec-data --log-failed`
confirmed the cause. No failing test was bypassed and no merge was attempted.
