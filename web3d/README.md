# Graph front ends

## What is on the serving path

`explorer.html` — the graph explorer published at `https://modelspec.dev/graph/`.
It reads the static export under `/api/graph/` and needs no API and no database.
The build copies it, with `vendor/`, into the site tree.

`downselect.v2.html` — the wizard published at `https://modelspec.dev/downselect/`.
It scores client-side against `/api/rank/candidates.json` and
`/api/rank/profiles.json`, so it needs no API either.

`vendor/` holds three.js and 3d-force-graph. They are committed rather than
loaded from a CDN so the page cannot break when someone else's host does.

## What is not

`../web/` — a React and Vite explorer that calls `/api/v1`, the FastAPI service
backed by FalkorDB. That service is gone, so the app renders nothing. It is kept
because its `DetailPanel` is the reference for MODEL-20 (model pages with their
relationships). Read that ticket before deleting it.

The original `index.html` explorer, `downselect.html` wizard and
`contribute.html` flow called the same service and were retired with it. The
wizard shipped instead as `downselect.v2.html`, rewritten client-side.
