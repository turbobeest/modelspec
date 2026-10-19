# MODEL-404-sync generated artifacts

Approved source: `7b833056a4cb8aa10c0f56cf6001b13224634ada`.
Merged main: `8971608aab849862b4a4870f1bc06e46fc9e7dd2`.
Worktree: `/Users/terbeest/dev/worktrees/model-404`.

Only repository generators resolved the two owned conflicts:
`cli/modelspec/agent-bundle.json` and `qa/fixtures/mcp-tools.json`.
No source behavior, literal expected digest, or generated field was edited by
hand. This worker did not stage or commit anything and did not run a full
suite, browser run, or site build.

Commands used Python `/Users/terbeest/dev/modelspec/.venv/bin/python` with
`PYTHONPATH=$PWD`, from this worktree. Writes followed the dependency order
specified in `docs/design/generated-pins.md`: agent copy, OpenAPI, QA capture.
The agent-copy read-only check started after its write; the final OpenAPI
check followed all writes.

| Command | Direct exit | Output |
| --- | ---: | --- |
| `python -m pipeline.agent_copy write` | 0 | [Generation](agent-copy-write.txt) |
| `python -m pipeline.agent_copy check` | 0 | [Freshness](agent-copy-check.txt) |
| `python api/worker/openapi.py` | 0 | [Generation](openapi-write.txt) |
| `python -m qa.contracts` | 0 | [Capture](qa-capture-write.txt) |
| `python api/worker/openapi.py --check` | 0 | [Freshness](openapi-check.txt) |
| `python docs/evidence/g2-ios/MODEL-404/routing/sync/audit-artifacts.py` | 0 | [Audit](artifact-audit.txt) |
| `python -m qa.agent_harness --first-turn-breakdown` | 0 | [Token totals](first-turn-budget.json) |

Generation reported hardware-source registration warnings and still returned
0; it did not modify catalogue or hardware input files.

## Generated output

All nine files below were written by the named generators. Changes are
relative to the approved source; complete comparisons against both merge
parents are in [artifacts.json](artifacts.json).

| File | Changed | SHA-256 |
| --- | --- | --- |
| `api/worker/openapi.yaml` | Yes | `7e30bfcd60cef8ba9b273650e05186a35581eb7fddf82be3614c45ed4036aa3b` |
| `api/worker/src/agent_guide.py` | No | `ab40849d972f578840728aafde99629353a4ae51d8f3bb109fd6215fceb55c8c` |
| `cli/modelspec/agent-bundle.json` | Yes | `fc703e9793773c72f8372d712ab5fb1fb6c7e6dfbd37bceef4d5b528d8c600d1` |
| `cli/modelspec/feedback.schema.json` | No | `551a54ba5a954b73c38d5c35d0a48c62cf1b89d0cd9543d96103e2320450638b` |
| `cli/modelspec/spec.schema.json` | No | `62189b5725b8bc9df91bcf6e6775e06a628e9588a687b9adbbf007f1390f7f4f` |
| `docs/agents.md` | No | `6fc541536d3d18442ac260767d254fc02216577951fac36aae92de700ae27a37` |
| `mcp/src/agent-copy.json` | No | `8bc2672473af4b9e4c1709b923c4be95b98e89b1c1a42e391cd323c37f5468c8` |
| `qa/fixtures/mcp-tools.json` | Yes | `413082d5741c69d8ec2e80be585ca37848f323bd2cc0a38b9d70e13aadc4bce6` |
| `site/holding/index.html` | No | `035fb219784beb4aa9a596e32dc5fc708a3087d63802a05cba71aed4a8b75928` |

Only three outputs changed:

- CLI bundle adopts upstream's separate key/digest line layout and updates
  its `pipeline/agent_copy.py` source hash. Its remaining JSON payload is unchanged.
- QA capture adopts that layout and updates its OpenAPI source hash. Tool
  descriptions and input schemas are unchanged.
- OpenAPI adds main's restored optional `decision_snapshot` health metadata.
  This is the complete YAML delta from the approved source.

The guide version remains `1-f226d9942791da1c`. All three hardcoded catalogue
hashes in `tests/test_decision_link.py` still match without edits. CLI and QA
source pins match the actual merged bytes. The flag-on vocabulary schema still
has optional ISO-date `as_of` and the same required fields. Agent, MCP and CLI
full-board links still use `/decide/details/`. First-turn estimates remain
9,328 / 9,421 / 9,500 under the unchanged 9,500 limit. No additional artifact
generator was required.

## Focused verification

Direct exit **0**: **235 passed, 2 skipped in 82.43 seconds**.
[Focused output](focused-tests.txt) covers the existing agent-copy, guide,
OpenAPI, decision-link, vocabulary, and QA freshness tests, plus upstream
MODEL-406's generated-byte stability, independent-pin merge and stale-pin
rejection regressions. No test assertions changed.

```text
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_copy.py tests/test_agent_guide.py tests/test_api_docs.py tests/test_decision_link.py tests/test_compact_vocabulary.py tests/test_generated_pins.py tests/test_agent_harness.py::test_mcp_capture_matches_current_public_sources
```

All owned command sessions completed. The targeted `git diff --check` and
all local links in this evidence summary pass.

## Link review

Read-only inspection agreed with root's two template-action mappings in
`pipeline/guides.py` and `pipeline/comparison_pages.py`: both explicitly open
the live full board and carry `?template=`, matching the already-approved
use-case action in `pipeline/build.py`. Their `/decide/details/?template=`
destinations preserve the existing question. Generic navigation and free-human
lookup links remain `/decide/`. This worker did not edit those files.
