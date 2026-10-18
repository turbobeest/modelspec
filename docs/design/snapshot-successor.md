# Snapshot handover at dated price boundaries

MODEL-402 closes the interval between a signed price snapshot expiring at
midnight UTC and the next Worker deployment. MODEL-394 already refuses expired
prices. This change supplies the next verified snapshot before that refusal
becomes necessary.

## Build both price periods from one checkout

`api/worker/vendor.py` builds `decision/snapshot.json.gz` with the build's UTC
date. If its signed content has `valid_until`, the same export operation builds
`decision/snapshot-successor.json.gz` with `as_of` equal to that exclusive bound.
Both builds use the same data checkout, registry, premier list, completeness
rules, and signing configuration. A failed successor build fails vendoring.
The existing canonical JSON and gzip writer determine both files' bytes.

`bundled_data` embeds the successor under
`/api/decision/snapshot-successor.json.gz` only when it exists. An export without
an expiry produces no successor. Its current snapshot and vocabulary keep their
existing bytes. Rebuilding an existing export directory removes any obsolete
successor so a prior build cannot supply one accidentally.

Each snapshot also has its own display vocabulary. The successor's vocabulary
ships as `/api/decision/vocabulary-successor.json`, with the same builder and
display projection as the primary vocabulary. Build-time template decisions
read the snapshot's resolved prices without checking today's live interval.
Live decisions retain that check. An undated export builds only the original
snapshot and vocabulary, and removes both obsolete successor artifacts.

## Authenticate the pair before serving either snapshot

MODEL-407 changes residency as described in [Worker memory](worker-memory.md).
`entry.py` parses and hash-checks only the current snapshot during deployment
snapshot creation. The successor stays compressed, alongside generated
metadata containing its signed content hash, publisher signature, validity
interval, snapshot ID, and compressed-payload checksum. No deployment secret
enters this step.

On the first runtime load, the holder verifies both HMAC signatures with the
runtime key before accepting either snapshot. A missing key or a tampered
signature refuses the pair. The successor's content and compressed-payload
checksum are checked when it is parsed. The signed content must match its
descriptor before the successor can serve.

For each request, `SnapshotHolder.current()` checks the current UTC date
against the snapshot's signed `[valid_from, valid_until)` interval. Once that
interval excludes the date and the successor can cover it, the holder releases
the old snapshot and vocabulary, then parses and authenticates the successor.
Loading occurs on the first request at or after the boundary. No preloading
timer holds both parsed periods. The response body retains the snapshot ID
used for its computation. If neither interval covers the date, the existing
`503 no_snapshot` response applies. Historical comparison loads continue to
retain their original prices. Comparison releases its initial current reference
before retained-history I/O, then selects the current snapshot again before
evaluating prices.

Bundled vocabulary requests select through the same authenticated holder after
the access gate. Full responses name the selected snapshot, and lookups use its
facet and template metadata. Dated vocabulary uses `cache-control: no-store` so
a cached primary vocabulary cannot persist across midnight. A client that gets
`409 snapshot_changed` can reload vocabulary and retry with the successor's ID.
Unbounded vocabulary keeps its existing bytes and cache behavior.

Decide, compare, compare-models, and hardware-fit response headers use a shared
helper to bind the ID to their own body snapshot reference. A null reference
omits the ID header. Billing can await after an answer has been computed, so
reading the shared holder at response time could instead name another
concurrent request's snapshot. Each route retains its existing serialization
and service headers. Routes that emit no decision snapshot ID header keep
their existing response contracts.

An alternative would make every holder manage a general collection of dated
snapshots, including fetched snapshots. That would change refresh, ETag, and
concurrent-load behavior without helping this bundled deployment gap. The pair
belongs only to the immutable bundled path. The existing conditional fetch,
refresh-failure fallback, and current-date refusal remain in place for fetched
snapshots.

## One successor covers the deployment delay

The Worker redeploys every six hours. Dated prices have day-level boundaries,
so distinct boundaries are at least 24 hours apart. One successor covers the
first midnight boundary and leaves at least four scheduled deployment
opportunities before another boundary. A new deployment builds its own pair
from the same rule. This does not promise availability through a deployment
outage lasting multiple price periods. If both snapshots expire, the holder
refuses service instead of extending a price. No workflow change is needed.

## Public health metadata

`/v1/health` adds an optional `decision_snapshot` object. It names the serving
snapshot with `id` and `valid_until`, and describes the authenticated successor
with `successor_held` and `successor_valid_from`. Dates use ISO calendar dates.
An unbounded date is null. When no snapshot can serve, `id` and `valid_until`
are null. An absent or unauthenticated successor has `successor_held: false`
and `successor_valid_from: null`. The existing health error field reports a
snapshot load failure. The object contains no prices, records, or secrets.

Health uses the same holder selection as decisions, including on a cold
isolate and at midnight. It selects after other metadata reads finish, so
their I/O cannot cross midnight after selection. The new object is additive
in the health schema.
Decision contract 2.18, bounded contract 1.5, and ranking stay unchanged.

## Verification

Tests exercise the Worker request path with signed Argon-like input and output
prices of $2/$10 before midnight and $4/$20 from midnight onward. They check
the instant before the boundary, the boundary itself, and one day later, along
with snapshot references and health metadata. Additional tests cover a cold
load after the boundary, an expired primary with no successor, an invalid
successor signature, and exhaustion of both intervals.

Vendor tests compare repeated builds byte for byte, check both signatures and
the successor's build date, and verify that undated exports produce no
successor and preserve the current bytes. Existing refresh and comparison
tests run alongside boundary regressions. Validation includes a Worker dry
run and total upload measurement against the Worker limit, followed by
the full pytest suite under the shared lock after `web/npm ci`.
