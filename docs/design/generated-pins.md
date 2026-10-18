# Generated source pins

MODEL-406 changes the layout of `cli/modelspec/agent-bundle.json` and
`qa/fixtures/mcp-tools.json` so independent digest updates merge cleanly.
The JSON objects, source paths, SHA-256 algorithm and consumers stay the same.

## What the pins protect

`pipeline.agent_copy.cli_bundle()` hashes the generator itself, entity and
pricing code, Worker flag code and configuration, tiers, the decision and
feedback schemas, and package metadata. `hatch_build.py` compares every pin
with source bytes before building an sdist or wheel. The source distribution
includes those inputs through the allowlist in `pyproject.toml`; this repo
has no `MANIFEST.in`. `tests/test_agent_copy.py` also checks these digests and
generated guidance. `python -m pipeline.agent_copy check` compares complete
generated artifacts byte for byte. The installed CLI reads the bundled JSON
through `cli/modelspec/guidance.py`; it does not hash repository sources at
runtime, and its wheel does not contain the engine or catalogue.

`qa.contracts.source_hashes()` pins MCP server and vocabulary code, the decide
budget fixture, the decision schema, OpenAPI, the agent guide and generated
MCP copy. The capture freshness test compares both the reconstructed tools
and their source hashes with the committed fixture. These hashes detect
source edits even when the extractor produces unchanged tools. OpenAPI has
its own byte-for-byte generation check.

## Decision

Choose layout isolation and retain the existing failing CI checks. Sort only
the `source_hashes` keys. Give each digest its own line after its source key:

```json
{
  "source_hashes": {
    "pipeline/entity.py":
      "<sha256>",
    "pipeline/pricing.py":
      "<sha256>"
  }
}
```

The unchanged, distinct key lines separate digest edits. Sorting alone
would leave adjacent changed lines and would not fix the conflict. Share
this formatting through the existing `pipeline.agent_copy.render()` and
use it for the MCP capture. Importing that module loads only entity and
Worker flag helpers; it does not load the decision engine or catalogue.
Objects without `source_hashes` retain their existing serialization.

A preliminary measurement with Git 2.50.1 used a temporary repository with
base, first and second branches. Each child changed a different neighboring
digest. `git merge --no-edit first` on second exited 1 with the existing
adjacent layout and 0 with separate key and digest lines. The merged JSON
retained both edits. The implementation tests will repeat this with the
actual generator output and all pairs of their pinned sources.

CI already runs the capture and CLI freshness tests and the OpenAPI check.
Keep those gates, exercise the full agent-copy check in pytest, and give
capture failures the exact regeneration command. Regenerate in dependency
order when needed:

```bash
python -m pipeline.agent_copy write
python -m api.worker.openapi
python -m qa.contracts
```

No workflow or automerge change is needed. CI will never regenerate and
push these files automatically. Workflow changes are excluded from
automerge and would require a human merge; this change avoids that path.

Generating the CLI bundle only at package-build time is out of scope. The
current sdist includes pinned inputs for validation, but not the catalogue
and coverage inputs that `cli_bundle()` loads. Removing the committed bundle
would require changing the package contents and build dependencies, while
also replacing the reviewed generated artifact. Layout fixes the conflict
without those changes. A local merge driver would not run on GitHub and is
not part of this solution.

## Validation and limits

Tests generate each pin file once per pytest session in process and reuse
those bytes. One end-to-end test runs each writing command once, with a
600-second timeout, and compares its output with that independent baseline.
The existing `perf` marker routes this test to CI's single serial job.
The ordinary tests compare committed bytes, serialization and sorted keys.
For every pair of pinned sources, they will mutate source bytes in a
temporary repository, serialize the updated digests through the production
formatter, commit two branches, and run a real three-way Git merge. They
will check both merged digests against the merged sources and check that
the payload is unchanged. The CLI stale-pin probe reuses the fresh bundle
while running the real check command's comparison and diagnostic logic.
Stale-pin probes will keep the CLI
check, MCP capture assertion, package hook and OpenAPI check effective.
Run the focused suites, installed-package smoke test, and the full suite
under `/tmp/modelspec-fullsuite.lock` after `npm ci` in `web`.

This addresses independent pin changes. Two branches that change the same
source, the same generated prose/schema, or a common guide version can still
conflict and need review. Adding or removing source keys can also conflict.
The one-time format migration can conflict with branches using the old
layout; those branches need to regenerate once after adopting this change.
