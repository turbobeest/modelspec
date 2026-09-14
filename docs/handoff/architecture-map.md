# Architecture map — coverage policy

Bounded Graphify map of **selected code and current docs**, not the catalogue.
Helpers and the allowlist live in [`../../graphify-out/`](../../graphify-out/).

## What the graph is

A navigation aid over the serving path, the CLI/DPF contract, ranking floors,
and the current handoff. Original files remain authoritative. Edges include
documented intent; they are not runtime proof.

Query it after checking freshness:

```bash
python3 graphify-out/prepare_scope.py --check
~/.local/bin/graphify query 'CLI rank snapshot export_schema_version' --budget 2000
```

`--check` returns nonzero when a scoped file, `scope.json`, or the extraction
prompt hash changed. A fresh hash is not a claim that Linear or live Pages
still match.

## DATA, not fact-checked content

These paths are **excluded** from the map. They are catalogue data. Indexing
them would treat volume as verification.

| Path | Why excluded |
|---|---|
| `models/**` | Model cards. Nulls, incomplete evidence, and unverified-legacy scores are normal. A card in git is not a checked fact. |
| `benchmarks/**` | Benchmark wiki pages and `_census/` scrape ledgers. Same rule. |
| `hardware/**` | Device SKUs. Vendor-spec figures belong on the card; the map does not audit them. |
| `docs/superpowers/**` | Dated plans and census-run notes. Not current policy. |
| `docs/screenshots/**` | Images, not contracts. |
| `docs/system-architecture-v3.md` | 2026-04 FalkorDB-served design. Historical. |
| `.github/**`, `scripts/**`, `researcher/**`, `web/**` | Other owners; not this bounded cut. |

Covered paths are the explicit list in `graphify-out/scope.json`. Source commit
and per-file SHA-256 are in `graphify-out/scope-manifest.json`. The commit is
context; the hashes are the bytes that were read.

## Incremental refresh

No watcher and no post-commit hook. Follow `graphify-out/README.md`. After a
controlled edit to a scoped file, `prepare_scope.py --check` must go stale,
re-extraction must change nodes for that file, and the probe string in
`docs/handoff/current.md` (`MODEL-40-PROBE-2026-09-14`) must be retrievable.
Receipt: `graphify-out/refresh-verification.json`.

Do **not** run bare `graphify extract .` or `graphify update` on this repo:
those commands do not enforce the allowlist and would ingest `models/`.
