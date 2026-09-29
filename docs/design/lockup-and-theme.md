# About the brand lockup and the dark default

MODEL-213, 2026-09-29. Jamie asked for a larger brand in the top-left corner
and for the site to be dark by default.

## One lockup, one scale

The lockup is the 2a mark beside the "ModelSpec" title, with "Model" bold.
`LOCKUP_CSS` in `pipeline/landing_chrome.py` sets its size and weight on every
page: a 48px mark and a 30px title on desktop, 38px and 24px below 900px. It
does not set the font, so each page keeps the wordmark font it already had.
`lockup()` writes the markup.

Pages the pipeline renders call both: the landing, `/method/`, `/pricing/`,
the legal and catalogue shell in `pipeline/render.py`, and the holding 404.
Two pages are built without the pipeline, so they carry verbatim copies. The
graph explorer (`web3d/explorer.html`) copies the markup and the CSS. The
decide app copies the CSS into `web/src/decide/decide.css` and uses the same
class names in its header. `tests/test_lockup.py` fails if a copy drifts.

To change the scale, edit `LOCKUP_CSS` and paste the new value into the two
copies.

## Dark unless the visitor chooses light

Every page is dark on a first visit. Most pages were already dark-only. The
two that changed are `/decide/`, which has the only theme toggle, and the
holding 404, which followed `prefers-color-scheme` and is now always dark.

`/decide/` ignores `prefers-color-scheme` on purpose. Dark is the product's
look, and a visitor who prefers light has a toggle one click away.

`initialTheme()` in `web/src/decide/theme.ts` picks the theme in this order:

1. A `?theme=light` or `?theme=dark` link, for that visit. It does not
   overwrite the stored choice.
2. The visitor's last toggle, stored in `localStorage` under
   `modelspec-theme`.
3. Dark.

An inline script in `web/decide.html` repeats that rule so the page is dark
before the first paint, with no light flash while the app loads.
`web/src/decide/__tests__/theme.test.tsx` runs the script against
`initialTheme()` for every combination of link and stored value.

The social cards and og images did not change. They render from their own
templates, not from the live pages.
