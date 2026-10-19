# Cite-only mismatch supersession

MODEL-415, 2026-10-19. Line references are to base
`2bdc4eb31` (main with #840, MODEL-411, merged).

## Problem

A cite-only fact (`docs/design/cite-only-sources.md`) is admitted as "Cited,
not machine-verified". `verify()` returns `cited` for it and deliberately
appends no `Verification` row. The snapshot still quarantines a cite-only fact
whose latest logged outcome for its value hash is `mismatch` or `unreachable`
(`decision/snapshot.py:822-823`).

Those two rules together make an old mismatch permanent. Nothing can append a
newer outcome for a cite-only fact, so a mismatch recorded before the host
became cite-only stays the latest row forever. The fact can never leave
quarantine with its current value, even after its citation moves to a region
that supports it.

MODEL-368 is the case. `perplexity/subscription/pro#offering.subscription.models_covered`
has a 2026-10-14 `mismatch` (`subscription-page@1`) for value hash
`sha256:d8f1c80f…1a685`. That check re-read the `pricing` region of the Pro
page, which no longer lists model versions. A transient cite-only read of the
FAQ region on 2026-10-19 (17:51:11Z, page `sha256:8b56772b…9faac`) supports
the same value. Refiling the citation does not change the value hash, so the
mismatch still wins.

## Rule

A mismatch is **superseded**, never deleted, when all of these hold:

1. **(a) Different region.** The fact's current citation does not cite the
   region the mismatch read, and does cite the region of the new read.
2. **(b) Newer supporting read.** A cite-only read of that new region is
   recorded with its URL, fetch time and page hash. It is newer than the
   mismatch, and it supports the fact's current value hash.
3. **(c) Recorded event.** The supersession is an append-only record that
   names both regions and both reads.

A superseded mismatch admits the fact as cited, never as verified. The
mismatch stays visible in provenance. A mismatch against the same region is
never superseded by a cited read. A non-cite-only fact is unaffected, and an
`unreachable` outcome is never superseded.

## Record

### Store

The private data repository is the store of record:
`verification/supersessions.jsonl`, beside `verification/log.jsonl`. It is
append-only, one record per line, under the same rule as the log: never edit
or delete a line; a correction is a new line. The engine reads it the way it
reads the log. `collect_repo` (`decision/snapshot.py:1684`, log read at
`:1772-1777`) loads it into a new `SnapshotInputs.supersessions` field
(`:349-373`), which defaults to empty. A checkout without the file builds
exactly as before.

`decision.supersession.append_only_violation(base, head)` reports a line that
changed or disappeared between two versions of the file. The private repo's
data checks can call it. Wiring that check, and filing the MODEL-368 record,
belong to a later data PR. This change does not touch the private repository.

### Schema

`decision.supersession.MismatchSupersession`, `schema_version: 1`, extra
fields forbidden:

```json
{
  "schema_version": 1,
  "target": {"kind": "fact", "id": "<fact id>", "value_hash": "sha256:<64 hex>"},
  "mismatch": {
    "date": "2026-10-14",
    "method": "subscription-page@1",
    "source_id": "<source id the mismatch read>",
    "url": "<that source's registered URL>",
    "region": "pricing",
    "snapshot_ref": "sha256:<64 hex> (optional: the page the mismatch read)"
  },
  "read": {
    "source_id": "<source id of the new read>",
    "url": "<that source's registered URL>",
    "region": "faq",
    "retrieved_at": "2026-10-19T17:51:11.546Z",
    "snapshot_ref": "sha256:<64 hex>"
  },
  "recorded_at": "2026-10-19T18:00:00Z",
  "recorded_by": "<agent or person>",
  "reason": "<why the old region no longer answers>"
}
```

- `target.kind` is `fact`. Evidence is never superseded.
- `read.retrieved_at` and `recorded_at` carry a timezone. `recorded_at` is
  not earlier than `read.retrieved_at`.
- `read.snapshot_ref` is a SHA-256 page hash. A missing or malformed hash makes
  the record invalid.
- Both URLs are HTTP(S).

A `Verification` row names no region, so the record names the mismatch's
region. The engine binds the record to the mismatch through the log's own
coordinates: target ID, value hash, date and method. A reviewer checks the
region claim in the data PR, as for any curated provenance.

## Admission

The change is in `decision/snapshot.py`. The rule today:

- `_verification` (`:769-783`) picks the winning row for
  `(kind, id, value_hash)`: the logged row or the inline one, latest date and
  then latest line.
- `_admit` (`:812-835`) returns `quarantined (mismatch)` for a cited fact whose
  winner is a mismatch (`:822-823`).
- `_add_facts` (`:861-915`) computes the citation (`:883`) and calls `_admit`
  (`:893-901`), then `_retain` (`:906`).
- `_retain` (`:789-807`) replaces a cited record's verification with `None`
  and adds `citation` (`:800-801`).

New behaviour:

1. `_Compiler.__init__` groups `inputs.supersessions` by
   `(target.id, target.value_hash)`. Rows are parsed one at a time. A row
   that fails the schema is kept as invalid and never supersedes. It is
   logged and named in the gate reason, so it is not lost silently.
2. In `_add_facts`, for a cited fact whose winning verification is a
   `mismatch`, `decision.supersession.supersede(...)` checks the candidate
   records for the fact's ID and current value hash. Candidates are checked in
   canonical-hash order. The first record that passes every check applies.
   The checks:
   - The winning row is a `mismatch` with the record's date and method.
     A newer mismatch therefore cancels an older supersession.
   - `mismatch.url` and `read.url` equal the registered URLs of their source
     IDs.
   - `read.url` is cite-only (`decision.retention.is_cite_only`).
   - Region identity is `(registered URL, region)`, so an alias source ID with
     the same URL is the same region. The fact's current refs must not cite
     the mismatch region (a). They must cite the read region (a).
   - The fact's ref for the read's source and region has the same
     `snapshot_ref`. If that ref records `retrieved_at`, it is the same
     instant. The citation is the read (b).
   - `read.retrieved_at`, as a UTC date, is strictly after `mismatch.date`.
     A read on the mismatch's own day is not newer, because the log records
     only dates (b).
3. `_admit` takes the result. A cited mismatch with a supersession applied is
   treated like a cited fact with no failing outcome. It still needs
   registered, non-excluded sources. Without a supersession the reason stays
   `quarantined (mismatch)`. When records targeted the fact and all were
   refused, the reason is `quarantined (mismatch; supersession refused: <why>)`
   so the gate message says why. `unreachable` and every non-cited path are
   unchanged.
4. `_retain` keeps `verification: null` and `citation` exactly as for any
   cited fact. It adds `superseded_mismatches`, a list with one entry per
   applied supersession:
   - `verification`: the superseded row's target, collector, verifier,
     method, outcome and date, plus `diff_sha256` in place of `diff`. The
     diff of a cite-only check can hold page-derived text, which the
     retention policy forbids copying.
   - `supersession`: the applied record, normalised JSON.
   - `supersession_hash`: SHA-256 of that record's canonical JSON.

No path sets `verification` or an outcome of `verified`. A superseded fact is
counted in `cited_fact_records`, and its decisions carry
`cite_only_not_machine_verified` like any cited fact.

## Provenance

The retained snapshot record is the provenance. `LoadedSnapshot.record(rid)`
returns it, signed and hashed with the rest of the content. For a superseded
fact it shows:

- `citation.status: "cited"` with the new region's source, hash and fetch
  time;
- `verification: null`;
- `superseded_mismatches[0].verification.outcome: "mismatch"`, its date,
  method and verifier;
- `superseded_mismatches[0].supersession`, naming both regions and both
  reads.

`docs/decision-snapshot.md` documents the field. It is additive inside
`format_version: 1`: retained records are already open dictionaries, and the
field appears only on superseded records, so other snapshots keep their bytes.

## Contract impact

There is no public contract change. Public responses project a cited fact's
`citation` through the closed `FactCitation` (`decision/contract.py:1738-1748`).
The explanation guard validates against it (`decision/explain.py:148-158`).
`superseded_mismatches` is a sibling of `citation` on the snapshot record and
is never copied into `FactCitation`, `ShownFact`, `ComparisonFact`, the
vocabulary, OpenAPI or the CLI and MCP payloads. No field widens, no enum
gains a value, and no contract version changes. The `Verification` outcome
enum stays `verified | mismatch | unreachable`.

## Not changed

- The verification log and its schema. No row is edited, deleted or appended.
- `verify()` still returns `cited` with no verification row.
- Ranking floors, class boundaries, cost-to-correct, `docs/legal/` and every
  production switch.
- Order sensitivity of `value_hash` for set-valued facets, noted in the
  MODEL-368 evidence, is a separate gap.

## Tests

`tests/test_cite_only_supersession.py` builds synthetic sources, page hashes
and records at runtime. It contains no real perplexity.ai text.

- The MODEL-368 shape: a cite-only subscription fact moves from `pricing` to
  `faq`. A newer read supports it. The fact is admitted as cited after
  supersession.
- A same-region mismatch stays quarantined.
- A read older than the mismatch, or on the same day, does not supersede.
- A newer mismatch after the supersession's mismatch quarantines again.
- A missing or malformed page hash does not supersede.
- A read whose hash differs from the fact's citation does not supersede.
- A non-cite-only fact with a mismatch and a record stays quarantined.
- The superseded mismatch appears in the retained record.
- No record, decision or export reports `verified` for the fact.
- `collect_repo` reads `verification/supersessions.jsonl`, and
  `append_only_violation` detects an edited or removed line.
