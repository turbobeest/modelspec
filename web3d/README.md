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
longer on the serving path, so they render nothing when published.

`../web/` — a React and Vite explorer against the same API, with the same
problem.

Both are prototypes, not dead code: `downselect.html` is the starting point for
MODEL-21 (the wizard, client-side) and the React `DetailPanel` is the reference
for MODEL-20 (model pages with their relationships). Do not delete them without
reading those tickets first.
