# Graph front ends

## What is on the serving path

`explorer.html` — the graph explorer published at `https://modelspec.dev/graph/`.
It reads the static export under `/api/graph/` and needs no API and no database.
The build copies it, with `vendor/`, into the site tree.

`vendor/` holds three.js and 3d-force-graph. They are committed rather than
loaded from a CDN so the page cannot break when someone else's host does.

## What is not, and why it is kept

`index.html`, `downselect.html`, `contribute.html` — the original explorer,
downselect wizard and contribute flow. These call a live FastAPI backed by
FalkorDB (`/api/v1/graph`, `/api/v1/rank`, `/api/v1/search`, …), which is no
longer on the serving path, so they render nothing when published. Their only
reader is `api/main.py`, which serves them at `/graph`, `/downselect` and
`/contribute`; no workflow deploys that app. Each file now carries a header
comment saying so, because the page source alone does not reveal that editing it
ships nothing.

`../web/` — a React and Vite explorer against the same API, with the same
problem.

MODEL-21 has since shipped as `downselect.v2.html`, a ground-up rewrite that
scores in the browser, so `downselect.html` is no longer its starting point. The
React `DetailPanel` in `../web/src` remains the reference for MODEL-20 (model
pages with their relationships). Read MODEL-20 before deleting `../web/`, and
retire the three pages above together with the `api/main.py` routes that serve
them rather than on their own.
