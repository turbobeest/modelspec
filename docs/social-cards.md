# Social cards

`pipeline.social_cards` renders 1200×630 PNG cards during `pipeline.build` with
the Playwright Chromium installed by `web/`. The PNGs are build artifacts and
must not be committed. The landing template receives the same `LandingData` as
the page, so its figures cannot drift into hand-written copy.

`CARD_REGISTRY` is the source of truth for rendering, page metadata, and the
deploy allowlist. To add the pricing card, add one `CardRegistration` containing
its filename, factory, and public page mapping. Set `source_page` for a static
HTML page and put `social-card-meta` markers in its `<head>`; `npm run build`
fills those markers from the registry. Python-rendered pages use
`card_for_page(...)`.

`render_card(card, out_path)` renders any supplied `SocialCard` through the
shared template and writes its PNG in one call. It returns the Chromium layout
report used by the tests. `render_card_html(card)` exposes the template for
inspection. The build artifacts are not committed.
