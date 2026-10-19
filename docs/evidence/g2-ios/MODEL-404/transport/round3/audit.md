# Final integration audit

Read-only audit at `2488fbc3c92a271d002dc1179b0c6b87345d1c96`, compared with local `origin/main` at `b4a7074f37a3ba940bd86db9d1e2459a25fd40af`. No actionable finding in the requested scope. This audit made no remote calls and changed only this file.

The source helper matches the objective and evidence representations. `decision/bands.py` emits the signed objective key and marks capability estimates with `estimated`; `decision/refinements.py::split_dimension` preserves the sign on the parent and separates the refinement. `simple/source.ts` reconstructs that exact key, chooses the unique largest positive capability share, and restricts candidates to verdict members' best ranked offerings. Its source priority matches `decision/explain.py::_evidence_priority`: descending estimate weight, direct before proxy, then record ID in Unicode code-point order. Model ID resolves otherwise equal priorities across members. The required missing-data and ambiguity fallbacks are explicit; they do not substitute cost evidence or domain-group order. Matching retained `top` contributions remain usable when result rows are truncated. The helper and answer renderer are unchanged since source commit `09bbb4203e00fb99a72379c11801885a3f6dae7f`.

Protected paths are unchanged. This command returned exit 0 with no diff:

```sh
git diff --exit-code origin/main...HEAD -- decision api/ranking docs/legal \
  api/worker/wrangler.jsonc mcp/wrangler.jsonc \
  web/src/decide/adapter/contract.ts .github/workflows
```

That includes ranking floors, `neutrality_commitment`, legal terms, decision contract code, evidence priority, and deployment configuration/workflows. Inspection of the build, composition, and Vite diffs found only the requested page routing, entries, and copy, with no production-switch change. The backend diffs are the approved display-vocabulary snapshot date, its OpenAPI documentation/schema entry, and the agent-guide version. The decision-contract document's added paragraph describes optional vocabulary metadata; decision contract code and versions are unchanged. MCP runtime/auth code is unchanged; its generated agent copy points to the detailed board.

The data-freeze guard passed directly:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python \
  scripts/data_freeze_guard.py --base origin/main --head HEAD \
  --branch model-404-simple-decide
```

Exit 0, output `data freeze: ok`. No frozen data path or lag-image manifest changed.

The composed tree at `docs/evidence/g2-ios/MODEL-404/root/round3/.generated/live/modelspec` was inspected with Python's `HTMLParser`. All assertions passed, exit 0:

- `/about/`: `Open the board` links to `/decide/details/`; `People decide on the board.` links to `https://modelspec.dev/decide/details/`.
- `/use-cases/`: `Decide` navigation links to `/decide/`.
- All 40 composed template pages keep `Decide` navigation on `/decide/` and `Apply this template on Decide` on `/decide/details/?template=<that page's template id>`. None retains the old `/decide/?template=` action.
- For example, `/use-cases/coding/coding-best/` links its template action to `/decide/details/?template=coding-best`.

The source route tests and `pipeline/build.py::use_case_page` agree with these composed links. No broader test suite was rerun for this audit. Existing focused source/UI results remain in [results.txt](results.txt); root owns the final full-suite and browser results.
