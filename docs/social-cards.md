# Social cards

`pipeline.social_cards` renders 1200×630 PNG cards during `pipeline.build` with
the Playwright Chromium installed by `web/`. The PNGs are build artifacts and
must not be committed. The landing template receives the same `LandingData` as
the page, so its figures cannot drift into hand-written copy.

`CARD_REGISTRY` maps the main page cards to their renderers, page metadata, and
deploy filenames. To add a page card, add one `CardRegistration` containing
its filename, factory, and public page mapping. Set `source_page` for a static
HTML page and put `social-card-meta` markers in its `<head>`; `npm run build`
fills those markers from the registry. Python-rendered pages use
`card_for_page(...)`.

`render_card(card, out_path)` renders any supplied `SocialCard` through the
shared template and writes its PNG in one call. It returns the Chromium layout
report used by the tests. `render_card_html(card)` exposes the template for
inspection. The build artifacts are not committed.

Each public decision template also gets `/decide/templates/<id>/` and
`og-card-template-<id>.png`. `build_template_previews` computes the template's
availability and leading models from the frozen public repository snapshot.
The static page and its card share that copy, including ties, unavailable
answers, and the snapshot date. `all_card_filenames()` includes these cards in
the live composition and the deploy checks. Rendering uses the existing
`MODELSPEC_RENDER_SOCIAL_CARDS` flag.

The board's Share dialog offers a `Template preview` tab for the active
starting template. That link contains only the public template ID. The preview
page links to `/decide/?template=<id>` to adjust it against the latest
catalogue. A saved board hash takes priority over that query parameter. Custom
decision preview URLs and server rendering require a separate privacy review.
