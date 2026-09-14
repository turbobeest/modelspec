# Bounded ModelSpec architecture graph

This map covers the **24 files** listed in `scope.json`: the current handoff,
the DPF CLI/export contract, ranking implementation, and their tests. It is
not a repository-wide graph and it does **not** index `models/` or
`benchmarks/`. Those trees are catalogue DATA. A card in git is not a
fact-check. Policy: [`../docs/handoff/architecture-map.md`](../docs/handoff/architecture-map.md).

Original files remain authoritative. Edges are navigation aids.

## Query and freshness

From this repository root (the worktree you are in, not a sibling checkout):

```sh
python3 graphify-out/prepare_scope.py --check
~/.local/bin/graphify query 'CLI rank snapshot export_schema_version' --budget 2000
```

`--check` uses the standard library and returns nonzero when a scoped file,
`scope.json`, or the extraction prompt changed. A fresh hash does not prove
Linear or live Pages still match.

Do **not** run `graphify extract .` or `graphify update` here. Those commands
do not enforce `scope.json` and would ingest the catalogue.

`cache/` is local hashed AST/semantic JSON (gitignored). A clone does not need
it; `prepare_scope.py` rebuilds AST from the allowlist. Do not commit it.

## Manual scoped refresh

1. `"$(cat graphify-out/.graphify_python)" graphify-out/prepare_scope.py`
   stages the allowlist under `/tmp/modelspec-graphify-scope-<worktree>` (never
   inside the repo — pytest would collect copied tests), runs AST on scoped
   Python, and checks the semantic cache. It does not call an LLM.
2. Read `.graphify_uncached.txt`. Host-session semantic extraction uses the
   Graphify skill's `extraction-spec.md`, with absolute source paths and
   absolute chunk paths under `graphify-out/`.
3. `"$(cat graphify-out/.graphify_python)" graphify-out/build_artifacts.py`
   merges AST + semantic, checks every scoped file contributed nodes, clusters,
   and prints community vocabulary.
4. Write 2–5 word names to `labels.json` for every community id, then
   `build_artifacts.py --labelled`.
5. `~/.local/bin/graphify export html` and a vocabulary-expanded query.
   Receipts: `refresh-verification.json`.
6. After a verified refresh:
   `~/.local/bin/graphify global add graphify-out/graph.json --as modelspec-architecture`

There is deliberately no `.graphify_root`. Registration is a snapshot, not a
live link to DPF.

## DPF

DPF consumers read [`../docs/cli-contract.md`](../docs/cli-contract.md). DPF's
own Graphify tag `dpf-operating-contracts` excludes ModelSpec. This tag is
`modelspec-architecture`.
