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
data#93, and `74947c3`, its hardware-fit records. Local private `origin/main`
still points to the merge of data#93, so neither that ref nor the older
checked-out private HEAD is a substitute for the pre-change baseline.

Measure all four combinations with `api/worker/vendor.py` and
`api/worker/measure_memory.cjs`. Use a synthetic signing key and Node 22.22.3.
The probe executes decide, vocabulary, rank, and policy-check in that order,
without collecting between requests. Its retained total includes the complete
WebAssembly allocation and live JavaScript memory outside that allocation.
Record each command, direct exit status, runtime version, and byte count.
Separate diagnostic measurements attribute snapshot parsing, provenance,
vocabulary, and verification state; they do not replace the acceptance probe.

The private checkout stays read-only. No private input, generated bundle,
response, or raw log belongs in this public repository. Only aggregate counts
and measured sizes may enter the evidence. Private temporary files need an
explicitly authorized location outside the public worktree and are deleted
after measurement. Until that location is authorized, public development can
continue but the private target remains unverified.

## Fail the pull request before the deployment

Replace the warning-only public probe with a failing memory check. Build the
frozen public data image with a committed deterministic synthetic fixture that
adds private-scale catalogue and provenance structure. The fixture contains
only invented identifiers and public source material. It exercises dated
current and successor snapshots as well as many-source hardware-fit records.
Calibration records the measured private dimensions, fixture dimensions, and
retained-memory comparison. Refreshing calibration means rerunning the private
matrix, adjusting the public recipe, and recording both results.

The same probe runs against the PR and main with the same fixture recipe,
synthetic key, requests, and runtime. A PR total above 115 MiB fails. An
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
