# benchgraph.dev landing page

`build.py` reads the model cards in `../../models`, draws the logo (a table whose top is a graph, the wordmark between the legs) as inline SVG, fills the SWE-bench Verified preview and the family map, and renders `index.tpl.html` into `../index.html`.

Headline counts (benchmark pages, benchmarks with reported scores, scored models, scores) are not baked here. `pipeline.build` injects them into `p.today` on every deploy so they cannot go stale, and so they never depend on this script or on a font download.

PNG assets (logo, icon, favicon, og-card) are a separate step. Fonts for that step are not committed. Fetch the face into this folder first:

    curl -sL -o SpaceGrotesk-VF.ttf "https://raw.githubusercontent.com/google/fonts/main/ofl/spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf"

Then, from this folder: `OUT=.. python3 build.py` writes HTML and SVGs and leaves the PNGs alone. `OUT=.. python3 build.py --png` redraws the PNGs.
