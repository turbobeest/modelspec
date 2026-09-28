# Social cards

`pipeline.social_cards` renders 1200×630 PNG cards during `pipeline.build` with
the Playwright Chromium installed by `web/`. The PNGs are build artifacts and
must not be committed. The landing template receives the same `LandingData` as
the page, so its figures cannot drift into hand-written copy.

To add the pricing card, construct one `SocialCard` with its filename, alt text,
headline, and HTML art, add it to the list in `render()`, and point the pricing
page's `brand.social_meta(...)` call at that filename. `render_card_html(card)`
provides the shared fonts, mark, navy field, yellow axis, and green baseline;
the existing two cards are examples. The deploy workflow must also copy and
assert the new filename when it assembles the live tree.
