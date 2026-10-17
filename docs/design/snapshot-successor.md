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

`entry.py` parses and hash-checks both bundled snapshots during deployment
snapshot creation. It passes them to `SnapshotHolder` through its existing
`bundled_snapshot` argument and a new optional `bundled_successor` argument.
No deployment secret enters that parsing step.

On the first runtime load, the holder verifies both HMAC signatures with the
runtime key before accepting either snapshot. A missing key or a tampered
successor refuses the pair. Later requests reuse those verified objects.

For each request, `SnapshotHolder.current()` checks the current UTC date
against the primary snapshot's signed `[valid_from, valid_until)` interval. If
that interval excludes the date, it checks the successor's interval. It records
the selected snapshot as the held snapshot, which supplies the response header
and the decision response's snapshot reference. If neither interval covers the
date, the existing `503 no_snapshot` response applies. Historical comparison
loads continue to retain their original prices.

Bundled vocabulary requests select through the same authenticated holder after
the access gate. Full responses name the selected snapshot, and lookups use its
facet and template metadata. Dated vocabulary uses `cache-control: no-store` so
a cached primary vocabulary cannot persist across midnight. A client that gets
`409 snapshot_changed` can reload vocabulary and retry with the successor's ID.
Unbounded vocabulary keeps its existing bytes and cache behavior.

Decision response headers use the snapshot reference in their own response
body. Billing can await after a decision has been computed, so reading the
shared holder at response time could instead name another concurrent request's
snapshot.

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
isolate and at midnight. The new object is additive in the health schema.
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
