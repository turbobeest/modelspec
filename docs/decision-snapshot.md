# The decision snapshot

`decision/snapshot.py` (MODEL-138) compiles the verified catalogue into the
**snapshot** every decision reads (design §4.2, §5). Same inputs, same bytes.

## Build

```bash
modelspec snapshot build --out snapshot.json.gz [--premier premier/slice-1.yaml] [--as-of YYYY-MM-DD]
```

Inputs, read by `collect_repo`:

| Input | Where |
|---|---|
| Models | cards in `models/`: `lifecycle` (else v1 `status`: `deprecated`/`sunset` → `deprecated`, else `active`), v2 `facts`, `benchmarks.evidence` rows |
| Offerings | `offerings/<provider>/<lab>/<model>.yaml`, each a list |
| Sources | `registry/sources.yaml`: `sources: [{id, url}]` (provisional, until MODEL-137 fixes the file) |
| Domains | each benchmark page's `domains` tags (MODEL-133) |
| Verification log | `verification/*.jsonl`, one MODEL-134 `Verification` per line; the latest per target wins |

What never enters:

- a fact or evidence row whose latest verification is not `verified`;
- anything with no source, or a source ID with no registered URL;
- anything from an excluded source. The rules are parsed from
  `tests/test_removed_sources.py`, and the serialised output is scanned with
  them; a hit fails the build;
- the legacy `benchmarks.scores` block, which is never read.

Retired models and their offerings go to the `archive` section.
`content.excluded` counts what was kept out, by reason.

## The completeness gate

With a premier list, the build fails unless every **guaranteed** facet is
known (or verified `not_disclosed` / `requires_contract`), sourced and verified
for each premier model and each of its offerings. The error names the subject,
the facet, the reason and the source. Facets with `computed_by` in the registry
(`estimate.capability`, MODEL-129) are skipped in slice 1. Retired premier
models are skipped; a premier model missing from the catalogue is a gap.

## File format

Gzipped canonical JSON (sorted keys, no whitespace, gzip `mtime=0`):

```json
{"format": "modelspec.decision-snapshot", "format_version": 1,
 "snapshot_id": "snap_<16 hex>", "content_hash": "sha256:<hex>",
 "signature": {"alg": "hmac-sha256", "value": "<hex>"} | null,
 "content": {"as_of", "facet_subjects", "lineup", "archive",
             "benchmark_domains", "sources", "excluded"}}
```

`content_hash` is SHA-256 over the canonical `content`; the ID is its first 16
hex digits. The signature is HMAC-SHA256 over the `content_hash` string with
`MODELSPEC_SNAPSHOT_KEY`; unset, the snapshot is unsigned.

`lineup` and `archive` are columnar: `candidates` (id, kind, model, lifecycle,
sorted by id), `facets` (per facet, sparse columns `row`, `state`, `value`,
`sources`) and `evidence` (per candidate, rows of benchmark, version,
sub-category, value, unit, measured_by, effort, harness, date, source IDs).

## Load

`load_snapshot(path, key=…, include_archive=False)` checks the hash, then the
signature when a key is available (default: the environment). With a key, an
unsigned or wrongly signed file is refused. It returns a `SnapshotIndex`:

- `candidates()`: models and offerings in the lineup, sorted; the archive only
  when asked;
- `fact(cid, facet)`: a `FactValue`. An offering answers its model's facets;
  `offering.provider`, `.region` and `.tier` come from its identity;
- `ids_where(facet, op, arg)`: a `Bitset3` (passing, failing, unknown). Any
  state but `known` is unknown. `unbounded` exceeds every number; `not_offered`
  fails ordered comparisons;
- `evidence(...)` with qualifier filters (`after` is exclusive), and
  `evidence_for_domain(...)`, which sets `directness`.

The bitsets are built at load time from the columns, so the file cannot hold a
bitset that disagrees with its values.

## Publishing

`python -m pipeline.build --decision-snapshot` writes
`api/decision/snapshot.json.gz` beside the static export, linked from no page.
Off by default.
