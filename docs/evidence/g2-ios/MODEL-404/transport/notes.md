# Simple decide transport verification

The transport reuses `prepareVisit`, `loadVocabulary`, `decisionAction`,
`hostedEngine`, `prepareDecisionRequest`, `retryOnSnapshotChange`, and
`sharedReload`. The page still supplies the existing `HumanGate` and
`VisitGate` components. No adapter or gate implementation changed here.

The first focused run failed because `useSimpleDecision` did not exist.
The output is preserved in [results.txt, section 1](results.txt). An added race assertion then failed with an old
request's timeout replacing a newer successful answer. That behavioral red
output is in [results.txt, section 2](results.txt). The watchdog now checks its abort
signal before changing state.

Independent review found that a vocabulary refresh changing a template's
task size aborted the verified lookup and left it idle. The first reproduction
is in [results.txt, section 3](results.txt). Retrying the changed question under the
same intent is not a valid fix: the real SQLite human gate charges a new
admission when task tokens change. A local replay through
`tests/replay_human_gate.py` returned remaining counts 19, 18, 18 for an old
summary, changed-task summary and changed-task full explanation. The replay
input and output are preserved in [results.txt, section 4](results.txt).

The final regression requires one request before an explicit new lookup,
an actionable `question_changed` error, and a fresh verification token in
manual mode. [Results sections 5 and 6](results.txt) record the three-request
failure before the guard and the passing run after it. Metadata-only snapshot changes retain the same action;
material changes stop before an altered request. Automatic Retry starts a new
action. A material change during the full explanation clears the old summary.

Node v22.22.3, npm 10.9.8, and Vitest v5.0.1 were used. From the worktree root:

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm --prefix web test -- src/decide/__tests__/simple-transport.test.tsx
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH MODELSPEC_TEST_PYTHON=/Users/terbeest/dev/modelspec/.venv/bin/python npm --prefix web test -- src/decide/__tests__/simple-transport.test.tsx src/decide/__tests__/human-gate.test.tsx src/decide/__tests__/visit-gate.test.tsx src/decide/__tests__/adapter.test.ts src/decide/__tests__/vocabulary-fetch.test.ts
git diff --check -- web/src/decide/simple/useSimpleDecision.ts web/src/decide/__tests__/simple-transport.test.tsx
```

All three final commands exited 0. The combined regression run passed 68
tests in five files, recorded in [results.txt, section 7](results.txt). Assertions cover summary and
full request headers, automatic and manual lookups, pending gate status,
runtime gate changes, delayed replies, vocabulary retry, snapshot refresh,
unavailable templates, watchdog retry, and twelve transport cases in total.

After the UI recovery fixes, two component regressions were added in
`simple-recovery.test.tsx`. They drive the rendered page through an EU limit
becoming unsupported after a snapshot reload, then remove only EU and retain
the no-training condition, route and workload. The second mutates the
vocabulary's date, available-template count and template token sizes, checking
both the displayed values and the outgoing requests. This additional command
exited 0 with 14 tests across two files, recorded in [results.txt, section 8](results.txt):

```sh
PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH npm --prefix web test -- src/decide/__tests__/simple-recovery.test.tsx src/decide/__tests__/simple-transport.test.tsx
```

The recovery tests were written after the reviewed UI fixes, so no new
production red is claimed for them. Their first run caught a test-fixture
assumption: the saved vocabulary has no coverage block. The mutation now adds
a complete coverage block and verifies the initial unavailable-date state.

A later component test reproduced a disabled Self-hosting button after the
visitor removed its open-weights condition. The availability calculation kept
the removed condition while its click handler cleared it. Job and priority
availability now check exactly the choice their handlers would apply.
[Results sections 10 and 11](results.txt) preserve the behavioral red and the
27-test green run. The regression verifies restored self-hosting conditions
and the retained explicit no-training limit at every priority.

The local engine's route probe then exposed a no-feasible result with no
removable named constraint for chat-app and own-hardware routes. The UI now
states that no comparison is available for the selected route and offers
an explicit "Try all routes" action. It does not assign a cause to the
missing comparison. [Results sections 12 and 13](results.txt) record two
behavioral failures and the 29-test green run. The regressions check that
there is no automatic broader request, the full-evidence link remains, and
the recovery changes only access while preserving the selected job,
priority, explicit limit, and workload.

The tests use the real request adapter with mocked fetch responses from the
repository fixtures. They do not observe production decisions, a live
Turnstile challenge, browser rendering, or private data. No background
process remains from this transport work. Root execution records the final
commit and broader checks.

After root merged main `0cf4080a`, the MCP typecheck and all 203 unit tests
passed. [Merge results](merge-mcp-results.txt) record direct exit codes,
commands, and compact output links. The read-only parity check also confirms
that main's hardware-fit code, MCP snapshot, fixture, and tests are unchanged;
both saved 2.0 assessments match in-memory Python regeneration. The merged
context guide retains `/decide/details/`, and every MCP tool description
matches main. No source changes were needed for this verification.

The merged CI run later exposed a test-isolation failure in the billing replay
helper: restoring the entire `sys.modules` table removed newly imported
Pydantic modules while leaving cached classes on their parent package. The
same billing-then-OpenAPI sequence reproduced the exact CI error locally.
The helper now restores only its three runtime stubs. A cold-process regression
prevents collection-time imports from hiding the defect. [Import-isolation
results](import-isolation-results.txt) record both red runs, the 56-test relevant
suite pass, the 149-test merged regression pass, and a real decision,
hardware-fit assessment, and OpenAPI generation after replay. Hardware-fit
production behavior and generated pins were not changed.
