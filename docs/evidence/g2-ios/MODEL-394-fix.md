# MODEL-394 execution evidence

Engine base: `b51985205621aba2e231a8914b5d4f0be9d4db6d`.
Data base: `502683e2aee6c6ddb3f8e5fd4998f89007388ae9`.

## Design recorded before implementation

An offering's price schedule consists of dated `Fact` records for the same
price facet. Each entry has its own ID, retained sources, and verification.
Optional `effective_from` and `effective_until` dates describe an inclusive
interval. Undated facts keep their existing meaning and verification identity.
Dated facts bind the value and both dates in their verification hash. Offering
validation rejects ambiguous schedules, mixed dated and undated entries, and
overlapping intervals.

The snapshot builder requires `as_of` when a schedule exists, selects exactly
one entry for that day, and retains that entry's provenance. A signed internal
validity interval prevents a cached snapshot from serving a price across a
schedule boundary. The engine and hosted snapshot holder enforce that interval
on each use, including refresh fallbacks.

A dedicated deterministic reader handles dated claims. It requires exact model
identity, the model's own table, the requested price kind, and the exact dated
row. Dated claims cannot fall back to undated readers. The weekly re-read checks
every dated entry, including future entries, through the same reader and hash.

The public decision response keeps one numeric price per offering. No existing
response field changes, widens, or becomes optional. Contract 2.18 and bounded
1.5 remain unchanged under MODEL-59. The authored data schema and signed internal
snapshot metadata change, so private data requires the new engine pin.

The alternative was a nested schedule inside each fact. Separate dated facts
reuse the existing record IDs, source references, queue, and verification log
without a second scalar value or a recursive verification path.

## Verification plan

Record failing tests against the unchanged implementation for date resolution,
the boundary day, missing and mismatched rows, and expired snapshot use. Then
run focused suites and the required engine full suite. Run the private broader
suite exactly as `recall-private.yml` specifies, including the linked-data guard.
Build the private catalogue for 2026-11-30 and 2026-12-01 and record Argon's
resolved input, output, and cache prices.

The final evidence will record commands, versions, test outputs, commit IDs,
and unobserved behavior. No production switch, deployment, paid provider call,
or Linear write is part of this execution.
