# Decision fixtures

The `live-assistant-balanced-{summary,full,plot}.json`, `live-empty-board-{summary,full}.json` and `live-vocabulary.json` fixtures were captured from our own API on 2026-10-04, at snapshot `snap_483dd2fb6c5915b5`, contract 2.12. No vendor keys were used.

The vocabulary came from `GET https://api.modelspec.dev/v1/vocabulary`. The assistant's `spec` came from `GET https://api.modelspec.dev/v1/vocabulary?section=templates&ids=assistant-balanced`. Each answer is the unmodified response from `POST https://api.modelspec.dev/v1/decide`, with `x-modelspec-snapshot` pinned to that snapshot. `live-decision-requests.json` records the exact summary, full explanation and plot bodies the page sends on opening and after Clear, including the page's default 40,000 input and 4,000 output tokens. The plot differs from the assistant ranking: no conditions, a preferred capability, and equal capability and cost weights. The empty board uses the engine's cost objective while the page presents it as unranked. MODEL-313 removed `"task_type": "new_feature"` from these five request bodies by hand, because the page no longer sends it. The captured answers were not recaptured, so their `spec_hash` and `decision_id` still belong to the bodies that included it. Ranking is unaffected, because the engine never reads `task_type`. Recapture them on the next snapshot refresh.

`web/scripts/decision-fixtures.mjs` matches these requests in browser tests and the assembled landing check. It ignores snapshot pins and object key order, and falls back to the empty-board answer for other specs. Summary fallbacks use the summary fixture; other fallbacks use the full explanation.

Other files retain their original snapshots and cover older contracts or specific adapter cases.
