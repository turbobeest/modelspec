# Decision fixtures

The `live-assistant-balanced-{summary,full,plot}.json` and `live-empty-board-{summary,full}.json` fixtures were captured from our own API on 2026-10-04, at snapshot `snap_483dd2fb6c5915b5`, contract 2.12. No vendor keys were used.

The assistant's `spec` came from `GET https://api.modelspec.dev/v1/vocabulary?section=templates&ids=assistant-balanced`. Each answer is the unmodified response from `POST https://api.modelspec.dev/v1/decide`, with `x-modelspec-snapshot` pinned to that snapshot. `live-decision-requests.json` records the exact summary, full explanation and plot bodies the page sends on opening and after Clear, including the page's default 40,000 input and 4,000 output tokens. The plot differs from the assistant ranking: no conditions, a preferred capability, and equal capability and cost weights. The empty board uses the engine's cost objective while the page presents it as unranked. MODEL-313 removed `"task_type": "new_feature"` from these five request bodies by hand, because the page no longer sends it. The captured answers were not recaptured, so their `spec_hash` and `decision_id` still belong to the bodies that included it. Ranking is unaffected, because the engine never reads `task_type`. Recapture them on the next snapshot refresh.

`live-vocabulary.json` retains its historical filename but is now generated
locally from the frozen repository snapshot `snap_e9c30eaacfa8f2f2`, dated
2026-10-04, with vocabulary version 1 and contract 2.18. The
[producer](../../../../docs/evidence/g2-ios/MODEL-404/routing/round3/generate-display-vocabulary.py)
builds the full vocabulary and applies the Worker's actual `trim()` function
with its model and facet allowlists. Its optional top-level `as_of` comes from
that full vocabulary's `coverage.as_of`; no coverage counts or metadata from
another fixture are added. The
[provenance](../../../../docs/evidence/g2-ios/MODEL-404/routing/round3/display-vocabulary-provenance.json)
records source and output hashes. No production request is made. Model names
and template specs match the older capture, but the historical decision stubs
above retain their original snapshot IDs. They are not a same-snapshot
vocabulary/decision pair. MODEL-404 screenshot responses are generated locally
from the same snapshot as this vocabulary.

`web/scripts/decision-fixtures.mjs` matches these requests in browser tests and the assembled landing check. It ignores snapshot pins and object key order, and falls back to the empty-board answer for other specs. Summary fallbacks use the summary fixture; other fallbacks use the full explanation.

Other files retain their original snapshots and cover older contracts or specific adapter cases.
