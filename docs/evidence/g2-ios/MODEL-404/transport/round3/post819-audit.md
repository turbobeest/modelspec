# Post-819 integration audit

Audited merge commit `fcf541f03455c5a95168572093cef5a161a5bef5` against local `origin/main`, `34c6dbef95371cff728a7a28aba33dcffe3e50e3`. Main's #819 reverts #813's bundled successor snapshots. No actionable integration finding. This supersedes the earlier audit's base for the final merged source.

Main's reverted implementation is retained byte-for-byte in these files, verified by comparing each working-tree file with `git show 34c6dbef:<path>`:

| File | SHA-256 |
| --- | --- |
| `api/worker/src/decide_service.py` | `e897e4c70f5ade89bb4cbf44e5f3ee4f6b7c8b12435d3debb619207994be1f02` |
| `api/worker/src/entry.py` | `196e38a394f7ffd3e727058bcfb075a7ace4a532c209d6ab66d11150c46263ae` |
| `api/worker/vendor.py` | `7d6091bc846cbee417bea15f8d2899b28a8bc7161abad6a44b11ef296cc0163c` |
| `decision/vocabulary.py` | `fe832a0fe349736971870b5730f391912015decf890c0db9ebb8f26409396acb` |

`git diff --exit-code origin/main...HEAD` also returned 0 for these files, the reverted snapshot tests, `tests/test_visit_gate_off.py`, and `docs/decision-snapshot.md`. The entire `decision` tree has no branch delta from main.

The authorized MODEL-404 changes remain intact:

- `display_vocabulary.trim` still copies the full vocabulary's `coverage.as_of` to top-level `as_of` when available. The trim, simple-page source helper, answer renderer, header, and vocabulary parser are unchanged from the pre-merge branch commit `34807d8b3d63a11228f6e4df283a4e8c7234e18b`; the corresponding `git diff --exit-code` returned 0.
- The conditional `/v1/vocabulary` OpenAPI schema still describes `as_of` as an optional string with `format: date`, copied from `coverage.as_of` and absent when unavailable. An AST inspection confirmed it is not in `required`. Removing only this property and its associated description wording makes `api/worker/openapi.py` byte-for-byte equal to main's source. Thus main's OpenAPI snapshot revert is preserved as well.
- The default checked-in OpenAPI YAML omits `/v1/vocabulary`; that route is added by `render()` only when `pipeline.public_data.enabled()` is true. The first artifact-only probe therefore found no route. The conditional source schema was then checked directly, without changing the build or production flag.
- Under backend/runtime paths, the only remaining branch changes are the display date trim, the approved agent-guide version/copy, and the OpenAPI metadata above. MCP runtime/auth source is unchanged. Ranking, legal terms, decision contract code, both Wrangler configurations, and workflows have empty diffs against main.

Final data-freeze check on the merge:

```sh
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python \
  scripts/data_freeze_guard.py --base origin/main --head HEAD \
  --branch model-404-simple-decide
```

Direct exit 0; output `data freeze: ok`.

The post-819 composed tree at `docs/evidence/g2-ios/MODEL-404/root/round3/post819/.generated/live/modelspec` passed the read-only HTML-parser link assertions, direct exit 0:

- Both about-page board links target `/decide/details/`, using the relative and canonical forms respectively.
- The use-case index keeps `Decide` navigation on `/decide/`.
- All 40 template pages keep first-visit navigation on `/decide/` and their template action on `/decide/details/?template=<that page's template id>`.
- No template action retains the old `/decide/?template=` destination.

Only this audit file was written. No source/test edits, generated artifact writes, GitHub or other remote calls, commits, or full-suite runs were made by this audit. Root owns the restarted final suites.
