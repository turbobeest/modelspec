# benchgraph.dev landing page

`build.py` reads the model cards in `../../models`, draws the logo (a table whose top is a graph, the wordmark between the legs) as inline SVG and as PNG assets, computes the real numbers on the page (benchmarks, scored models, dated scores, the SWE-bench Verified top table, the family map) and renders `index.tpl.html` into `../index.html`.

Fonts for the PNG rendering are not committed. Fetch them into this folder first:

    curl -sL -o SpaceGrotesk-VF.ttf "https://raw.githubusercontent.com/google/fonts/main/ofl/spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf"

Then, from this folder: `OUT=.. python3 build.py`. Deploy the parent folder with `wrangler pages deploy .. --project-name benchgraph --branch main`.
