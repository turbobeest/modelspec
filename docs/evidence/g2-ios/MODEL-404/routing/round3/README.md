# MODEL-404 round 3: vocabulary date and generated contracts

Base: `53fde1fd302da4fd050758d42a4c5ead8bd7a593`, with this round's working
tree changes. Python 3.14.4 from `/Users/terbeest/dev/modelspec/.venv/bin/python`;
Node v22.22.3. All listed exits were captured directly. No production request,
paid API call, full pytest run, commit, or push was made by this worker.

`trim()` now copies the full vocabulary's `coverage.as_of` to optional
top-level `as_of`. Missing or null dates remain absent. `coverage`, catalogue
counts, and the existing per-model exclusions remain trimmed. The frontend
parser accepts this optional ISO date without changing its full `coverage`
shape. Vocabulary version remains 1; decision contract remains 2.18. MODEL-59
permits this additive field without a major bump.

| Check | Direct exit | Result / evidence |
| --- | ---: | --- |
| New trim regression before implementation | 1 | [Expected 2026-09-24, got None](trim-red.txt); full vocabulary and snapshot dates already matched |
| New parser regression before implementation | 1 | [Schema stripped top-level date](parser-red.txt) |
| Optional OpenAPI property before implementation | 1 | [Missing `as_of` property](openapi-red.txt) |
| Trim and OpenAPI module after changes | 0 | [33 passed](compact-green.txt), including absent dates, trim boundaries, and real HTTP byte preservation |
| Vocabulary and successor vendor suites | 0 | [77 passed](vocabulary-vendor-green.txt) |
| Frontend vocabulary suite | 0 | [223 passed](vocabulary-unit-green.txt) |
| Historical fixture assertions after vocabulary regeneration | 1 → 0 | [5 failed, 3 passed](fixture-stubs-red.txt) → [8 passed](fixture-stubs-green.txt) |
| Agent guide, agent copy, decision link, API docs | 0 | [138 passed, 2 skipped](agent-api-green.txt) |
| Agent-copy generation then check | 0 / 0 | [Write](agent-copy-write.txt), [check](agent-copy-check.txt) |
| OpenAPI generation then final check | 0 / 0 | [Write](openapi-write.txt), [check](openapi-check.txt) |
| QA tool/schema capture | 0 | [Capture](qa-contracts-write.txt), source pins independently verified |

Python test commands use `PYTHONPATH=$PWD` and the interpreter above:

```text
-m pytest -q tests/test_compact_vocabulary.py::test_trim_keeps_snapshot_date_without_catalogue_coverage
-m pytest -q tests/test_compact_vocabulary.py::test_openapi_documents_query_lookup_without_changing_legacy_schema
-m pytest -q tests/test_compact_vocabulary.py
-m pytest -q tests/test_decision_vocabulary.py tests/test_snapshot_successor_vendor.py
-m pytest -q tests/test_agent_guide.py tests/test_agent_copy.py tests/test_decision_link.py tests/test_api_docs.py
-m pipeline.agent_copy write
api/worker/openapi.py
-m qa.contracts
-m pipeline.agent_copy check
api/worker/openapi.py --check
-m qa.agent_harness --first-turn-breakdown
```

Frontend commands ran from `web/` with Node v22.22.3 first on PATH:

```text
npm exec vitest -- run src/decide/__tests__/vocabulary.test.ts -t 'preserves the optional display snapshot date'
npm exec vitest -- run src/decide/__tests__/vocabulary.test.ts
npm exec vitest -- run src/decide/__tests__/fixture-stubs.test.tsx
```

## Genuine display fixture

Run from the repository root:

```text
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-404/routing/round3/generate-display-vocabulary.py
```

The [producer](generate-display-vocabulary.py) builds the frozen public
snapshot at `2026-10-04`, writes its full vocabulary through
`pipeline.build.write_decision_vocabulary`, then calls the actual Worker
`trim()` with the vendor's active-model and enum/boolean facet allowlists.
Its temporary snapshot uses an explicit public fixture-only HMAC key; it
does not read deployment signing credentials. The whole resulting display
document replaces `live-vocabulary.json`; no field is borrowed from an older
fixture. The date assertion compares the full vocabulary, trimmed output,
and pinned snapshot date before writing.

[Generation output](fixture-generation.txt) and
[provenance](display-vocabulary-provenance.json) record the source base,
producer/input hashes, full-vocabulary hash, and resulting fixture hash.
The recorded base commit is supplemented by hashes of the working-tree
producer inputs, including the changed trim source.

- Snapshot: `snap_e9c30eaacfa8f2f2`; `as_of`: `2026-10-04`.
- Fixture SHA-256: `d01851094b4907f9e8ecad14b369c987616a778da5e41d3197809e7f20ae2f23`.
- Full vocabulary SHA-256: `d92d64172ad0228b5a833f6b3954b8a9101486b3d1fb909544e2261d3360a636`.
- 44 model names, 40 template IDs/specs, 28 available templates, and 13 domain
  IDs remain unchanged from the old capture. Four facets added since contract
  2.12 appear from the real 2.18 producer: hardware weight size, estimated
  decode throughput, expert count, and experts per token.
- Historical `live-assistant-balanced-*` decision fixtures remain at
  `snap_483dd2fb6c5915b5`; their metadata was not rewritten. The fixture README
  identifies them as older test stubs. The gates worker generates screenshot
  decisions from the same frozen snapshot as the new display vocabulary.

The fresh full web run exposed five old `fixture-stubs.test.tsx` assertions
that equated captured decision snapshots with the current vocabulary snapshot.
The focused run reproduced all five failures. The replacement pins the
historical response ID literally to `snap_483dd2fb6c5915b5`, alongside its
existing literal contract 2.12 assertion. The request-key test still injects
the regenerated vocabulary's actual snapshot ID and checks that the matcher
returns the identical captured response bytes. The historical response files
remain unchanged. This checks capture provenance without claiming the two
fixture generations share a snapshot.

## Artifact integrity

Generation ran in dependency order: agent/CLI/Worker copy, OpenAPI, then QA
capture. [All six artifact hashes and three literal reviewed-catalogue
digests](generated-pins.json) are unchanged and match their committed pins.
Guide version remains `1-f226d9942791da1c`. QA and CLI source hashes match
current files. The committed OpenAPI is generated with data split off, so
it has no vocabulary route and stays unchanged; the flag-on renderer includes
the optional date with the same required fields, as recorded in
[flag-on schema proof](flag-on-openapi-proof.json) and exercised by the test.

[First-turn budgets](first-turn-budget.json) remain Claude 9,328, OpenAI 9,421,
Gemini 9,500, within the unchanged 9,500 limit. `git diff --check` and the
fixture README's local links passed.

## Independent source-line review

Read `simple/source.ts` against `decision/bands.py::blend` and
`decision/explain.py::_evidence_priority`, plus the rendered source mutation
tests. No blocking mismatch found. The selector uses the largest estimated
capability share, only verdict members' best ranked offerings, and contribution
evidence ordered by descending estimate weight, direct before proxy, then
Python-compatible code-point record order. It preserves retained `top`
contributions for truncated results and falls back when objective evidence is
missing or ambiguous. It no longer derives the source from domain-group or
result array order. This was read-only review; the transport worker owns its
implementation and test execution.
