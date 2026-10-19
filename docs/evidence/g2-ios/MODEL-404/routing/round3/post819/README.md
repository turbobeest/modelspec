# MODEL-404 after upstream #819

Merged upstream `34c6dbef95371cff728a7a28aba33dcffe3e50e3` into the working
tree based on `34807d8b3d63a11228f6e4df283a4e8c7234e18b`. #819 reverts the
bundled successor snapshot from #813 to restore the Worker memory budget.
This verification preserves that revert and MODEL-404's optional display date.
The earlier round-three results remain historical in the parent directory.

The sole conflict, `qa/fixtures/mcp-tools.json`, was resolved by running the
repository generators: agent copy, OpenAPI, then QA capture. Only that
generated conflict file was staged by this worker. No runtime fix, commit,
full pytest run, or production request was performed here.

The auto-merged OpenAPI source retains optional `as_of` with `format: date`
and the original required vocabulary fields. The committed flag-off schema
removes the reverted `decision_snapshot` health metadata. Its only generated
delta is that upstream removal. QA now pins those bytes while retaining
MODEL-404's guide and MCP copy hashes.

| Check | Direct exit | Evidence |
| --- | ---: | --- |
| Agent-copy generation | 0 | [Write](agent-copy-write.txt) |
| Agent-copy final check | 0 | [Check](agent-copy-check.txt) |
| OpenAPI generation and final check | 0 / 0 | [Write](openapi-write.txt), [check](openapi-check.txt) |
| QA capture | 0 | [Write](qa-contracts-write.txt) |
| Artifact, literal, CLI and QA pin audit | 0 | [Audit](generated-audit.txt), [pins](generated-pins.json) |
| Full display-vocabulary producer | 0 | [Generation](fixture-generation.txt), [comparison](fixture-comparison.json) |
| Vocabulary, vendor imports, price boundaries and refresh | 0 | [165 passed](vocabulary-vendor-green.txt) |
| Agent guide/copy, decision link and API docs | 0 | [138 passed, 2 skipped](agent-api-green.txt) |

The generator command is unchanged:

```text
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-404/routing/round3/generate-display-vocabulary.py
```

It used the merged `decision/vocabulary.py` and `api/worker/vendor.py`, as
recorded in the [current provenance](../display-vocabulary-provenance.json).
The output passed without a clock override or a validation bypass. Full
vocabulary bytes and trimmed fixture bytes are both unchanged:

- Snapshot `snap_e9c30eaacfa8f2f2`; date `2026-10-04`.
- Fixture SHA-256 `d01851094b4907f9e8ecad14b369c987616a778da5e41d3197809e7f20ae2f23`.
- Full vocabulary SHA-256 `d92d64172ad0228b5a833f6b3954b8a9101486b3d1fb909544e2261d3360a636`.
- 44 model names, 40 templates, 28 available templates. Coverage remains absent.

New generated hashes:

- OpenAPI: `4856fae354f22642f19b77c57b18d823a59ed0d4ccb1cf159f6e0d3d68b3ab0e`.
- QA capture: `221a6438534b4cad5890261ddbc7fb2eb839df53f053ada475ce1d88ac8a50de`.

The four other artifacts and all three hardcoded reviewed-catalogue digests
are unchanged. Guide version remains `1-f226d9942791da1c`. The
[flag-on schema proof](flag-on-openapi-proof.json) confirms the optional date.
[First-turn budgets](first-turn-budget.json) remain 9,328 / 9,421 / 9,500.

The focused Python command replaces the upstream-deleted successor suite
with the remaining relevant tests:

```text
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_compact_vocabulary.py tests/test_decision_vocabulary.py tests/test_worker_vendor_imports.py tests/test_dated_price_snapshot.py tests/test_decide_snapshot_refresh.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_guide.py tests/test_agent_copy.py tests/test_decision_link.py tests/test_api_docs.py
```

`audit-generated.py` reproduces the pin and fixture comparison checks after
the generator writes. Preserved pre-#819 provenance, pins, and flag-on schema
proof are adjacent files prefixed `pre819-`.

All command sessions completed. `git diff --check` and every local link in
the routing evidence READMEs passed.
