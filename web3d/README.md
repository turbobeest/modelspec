# v1 front ends

## What is built

`downselect.v2.html` — the v1 wizard. The v1 build still writes it to
`/downselect/`, but the live site redirects that path to `/decide/`
(`pipeline/live.py` `LEGACY`). It scores client-side against
`/api/rank/candidates.json` and `/api/rank/profiles.json`.

## What is not

`../web/` — a React and Vite explorer that calls `/api/v1`, the FastAPI service
backed by FalkorDB. That service is gone, so the app renders nothing. It is kept
because its `DetailPanel` is the reference for MODEL-20 (model pages with their
relationships). Read that ticket before deleting it.

The original `index.html` explorer, `downselect.html` wizard and
`contribute.html` flow called the same service and were retired with it. The
wizard shipped instead as `downselect.v2.html`, rewritten client-side.

The 3D graph explorer (`explorer.html`, `vendor/`) was removed by MODEL-251 on
2026-10-01: no text an answer engine can quote, and agents never use it.
`/graph/` now redirects to the home page.
