# Worker memory at pull-request time

MODEL-407 keeps the deployment limit at 120 MiB and introduces a 115 MiB
pull-request gate. Both limits measure retained memory after the same request
sequence in Pyodide 0.28.3. The difference reserves 5 MiB before deployment.
Decision 2.18, bounded 1.5, hardware-fit 2.0, ranking, and production switches
remain unchanged.

## Measure the failure before changing it

The starting engine commit is `b4a7074f37a3ba940bd86db9d1e2459a25fd40af`,
which already contains #813. Its parent `7908f238` supplies the code without
the successor. The private data comparison uses `fd3145c`, the parent of
data#93, and `74947c3`, its hardware-fit records. Use these exact commits for
the comparison.

Measure all four combinations with `api/worker/vendor.py` and
`api/worker/measure_memory.cjs`. Use a synthetic signing key and Node 22.22.3.
The probe executes decide, vocabulary, rank, and policy-check in that order,
without collecting between requests. Its retained total includes the complete
WebAssembly allocation and live JavaScript memory outside that allocation.
Record each command, direct exit status, runtime version, and byte count.
Separate diagnostic measurements attribute snapshot parsing, provenance,
vocabulary, and verification state; they do not replace the acceptance probe.

The private checkout stays read-only. Private bundles, snapshots, and probe
outputs stay under the authorized `/tmp/model-407-private` directory and are
deleted after measurement. No private input, generated bundle, response, or
raw log belongs in this public repository. Public evidence from private data
contains only memory numbers and commit SHAs.

## Fail the pull request before the deployment

Replace the warning-only public probe with a failing memory check. Build the
frozen public data image with a committed deterministic synthetic fixture that
adds private-scale catalogue and provenance structure. The fixture contains
only invented identifiers and public source material. It exercises dated
current and successor snapshots as well as many-source hardware-fit records.
Calibration compares measured retained memory for the private bundle and the
public fixture. Refreshing calibration means rerunning the private matrix,
adjusting the public recipe, and recording both memory results.

The same probe runs against the PR and main with the same fixture recipe,
synthetic key, requests, and runtime. Both candidate periods must pass 115 MiB.
Main releases without successor support provide only a current-period baseline;
the job announces that the successor comparison is unavailable. An incomplete
successor pair still fails. When main supports both periods, both comparisons
use their matching period. A PR total above 115 MiB fails. An
increase above 1 MiB emits a warning even when the total passes. Missing or
invalid measurements fail rather than silently passing. Deployment continues
to enforce 120 MiB. The calibration must not reduce the measured private
workload merely to pass the check.

Provide a patch in `docs/` for a manually dispatched memory job in the private
repository's `recall-private` workflow. It builds the selected private data
revision with the selected engine revision and enforces the same 115 MiB
headroom limit. This session does not edit or publish the private repository.
Workflow changes exclude the engine PR from automerge; the PR stays a draft
for independent review.

## Initial fixture calibration and refresh

The recipe in `api/worker/memory-fixture.json` adds synthetic lower-bound
workloads citing many invented sources and a dated price that expires three
UTC days after fixture creation. The fixture copies every file it modifies;
other public data paths are read-only symlinks.
Its model belongs to the production premier slice. The admission test uses
that same slice and completeness gate, so a fixture silently filtered out of
the deployed snapshot cannot pass.

The resulting public current and successor snapshots each retain all 15
synthetic workloads and 68 distinct synthetic source IDs, with 317 total
retained source IDs. Not every registered source belongs to a retained fact.

With the same public fixture and Pyodide 0.28.3, the starting `b4a7074f` code
retained 115.41149 MiB and this implementation retained 104.47210 MiB. The
115 MiB gate therefore rejects the previous eager implementation on this
workload. The general provenance table shrinks from 171,072 to 134,028 slots;
the separate hardware table has 1,350 slots. These observations establish
public regression coverage. They do not establish private memory equivalence.
Repeating the baseline gate returned 116.47690 MiB with the same 71.875 MiB
Wasm allocation, showing about 1.07 MiB of V8 measurement variation. The
candidate's Wasm allocation was 59.875 MiB. The 1 MiB regression warning can
therefore include runtime noise and should be investigated with repeat runs.
The private four-cell matrix is recorded in the execution evidence. Its first
follow-up exposed a successor-loaded failure that the original current-period
public check missed. Both periods now run as separate 115 MiB gates. Each
compares with its matching period on main when that period exists. A separate warm-rollover
measurement also serves the current period before crossing the boundary.

The final implementation `bb41f0f6` measures 104.48928 MiB current,
104.51080 MiB with the successor loaded, and 104.53250 MiB on warm rollover
for this public recipe. With private data `74947c3`, the corresponding totals
are 104.57204, 104.57278 and 104.61679 MiB. Every scenario uses 59.875 MiB
of Wasm memory. The public/private steady differences are below 0.09 MiB;
these measurements calibrate the fixture without publishing private rows or
structural counts. The private scratch directory is empty after measurement.

To refresh, measure the four private combinations and the final private build
with the pinned probe, using only synthetic signing credentials. Keep private
probe outputs under `/tmp/model-407-private`; copy only memory numbers and
commit SHAs into public evidence. Adjust the public recipe using the memory
comparison, then build both public comparison bundles with that same recipe.
Confirm the generated current and successor snapshots retain every synthetic
workload, and repeat the probe before accepting the calibration. Update the
evidence with the memory results. Keep private rows, URLs, bundles, and raw
logs under the authorized private scratch directory.

```sh
python api/worker/memory_fixture.py --out /path/to/public-memory-data
MODELSPEC_SNAPSHOT_KEY=model247-ci-fixture-key \
  python api/worker/vendor.py --data-dir /path/to/public-memory-data
MODELSPEC_SNAPSHOT_KEY=model247-ci-fixture-key \
  NODE_PATH=/path/to/pyodide/node_modules \
  node --expose-gc api/worker/measure_memory.cjs api/worker/src \
    --limit-mib 115 --attribute --output /path/to/public-memory.json
MODELSPEC_SNAPSHOT_KEY=model247-ci-fixture-key \
  NODE_PATH=/path/to/pyodide/node_modules \
  node --expose-gc api/worker/measure_memory.cjs api/worker/src \
    --successor --limit-mib 115 --attribute --output /path/to/public-successor-memory.json
```

The [complete commands](../evidence/g2-ios/MODEL-407/memory-commands.md) also
measure warm rollover after serving the current period.

For the main comparison, build the same recipe with main's engine code, run
the probe with `--measure-only --output`, and pass that JSON to the candidate
probe with `--baseline`. The workflow checks out the PR's main base commit.
Object attribution runs after the acceptance sample. Categories overlap and
are Python object-size estimates; their sum is not the Worker allocation.

## Keep one parsed price snapshot

Retain #813's signed current and successor bundle and its response-binding
guarantees. Module import does not parse or verify the successor. Vendoring
supplies small authentication and validity metadata alongside its compressed
payload. On the first request, authenticate both publisher signatures before
serving either period. Validate the exact payload against its metadata and
the signed content hash when loading it. A missing key or invalid signature
fails closed.

Defer parsing the successor until a request needs its period, at the UTC
boundary or later. This lies within the allowed loading window, which opens
24 hours before the current snapshot's exclusive `valid_until`. No timer or
background request is required. At handover, release the holder's current
snapshot and current vocabulary before retaining the successor. Keep only
compact metadata for health and the compressed deployment artifacts. Avoid
module-level aliases that keep the old parsed objects alive.

Every live selection checks the signed interval. If neither period covers
today, return the existing 503 refusal. Comparison reselects after historical
I/O. Decision and hardware-fit headers continue to use their own response
body's snapshot ID across credit commit and release awaits. A completed
response does not depend on which snapshot another request selected later.

## Bound temporary JSON allocations

WebAssembly memory does not shrink when Python releases a temporary buffer.
The first private successor measurement remained over budget after the old
snapshot was released. Diagnostic allocation samples located the next peaks
in snapshot JSON parsing and then ranking-catalogue JSON parsing.

Read JSON containers incrementally, retaining only a bounded text buffer
except when an individual scalar is larger. Delegate scalar decoding to the
standard-library JSON decoder and share object-key strings within one parse,
as that decoder does. Preserve every parsed value and the public wire format.
For canonical signed snapshots, hash the exact consumed UTF-8 content while
reading. Keep semantic-hash compatibility for older noncanonical envelopes,
and consume the gzip stream to EOF so footer corruption cannot be hidden.

The ranking and policy catalogues use the same reader. Ranking calculations
and data remain unchanged. Policy evaluation retains the requested page and
first ten error examples while aggregating counts and provenance over every
evaluated row. This avoids holding all response rows alongside summary sets.
Memory acceptance uses the actual requests without extra collections or
diagnostic instrumentation; attribution follows the sample.

## Materialize hardware-fit provenance on demand

Hardware-fit already uses source IDs and resolves URLs through the signed
source table when constructing responses. The existing snapshot duplicates
full workload records and also packs them into the general provenance table.
That table has one column for each distinct nested field path. Adding hardware
workload and verification fields widens every unrelated provenance row with
empty slots, so a small set of hardware records can expand the whole corpus.

Store hardware workload and numeric-input records in a separate packed table,
and index the workloads by record ID. Keep the general provenance table's
columns unchanged. Defer hardware record materialization until the first
hardware-fit request. Preserve record order, winning verification, source
ordering, numeric inputs, and serialization. Capture golden response bytes
from the unchanged implementation and compare the new implementation against
them. Normalize only the content-addressed snapshot ID, which changes when
the signed storage representation changes.

The signed snapshot format must remain explicit about the representation it
loads. Continue to read existing snapshots where necessary; do not widen any
public response field. Regenerate affected generated pins with their existing
generators.

## Acceptance and evidence

Write and run failing regressions before each implementation change. The
agreed test boundaries are bundle generation and loading, Worker requests at
UTC boundaries and billing awaits, hardware-fit response bytes, and the memory
gate's process exit status. Re-run #813's tests, focused hardware and workflow
suites, and the exact probe. The final private bundle with data#93 and the lazy
successor must retain at most 115 MiB.

Run `npm ci` in `web`, then the full four-worker pytest suite under
`/tmp/modelspec-fullsuite.lock` as specified in MODEL-407. Record red and green
output, exact commands, tool versions, base and tested commit IDs, memory
tables, calibration limits, and unobserved behavior in
`docs/evidence/g2-ios/MODEL-407-fix.md`. No production deployment, vendor API
spend, or private-data publication forms part of this work.
