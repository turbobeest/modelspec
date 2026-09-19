# Self-hosted fonts

MODEL-24 constraint: "No runtime CDN dependency beyond the fonts already loaded."
MODEL-19's acceptance criterion is stricter and flat: "No runtime dependency on a
third-party CDN." Archivo was not among the fonts already loaded, so it is served
from here rather than from `fonts.gstatic.com`.

## Archivo

| | |
|---|---|
| Family | Archivo (variable weight axis, 100–900) |
| Files | `archivo-latin.woff2` (34,940 bytes), `archivo-latin-ext.woff2` (32,672 bytes) |
| Version | v25, as served by Google Fonts |
| Retrieved | 2026-09-16, from `https://fonts.gstatic.com/s/archivo/v25/` |
| Licence | SIL Open Font License 1.1 — full text in `Archivo-OFL.txt` |
| Licence source | `https://raw.githubusercontent.com/Omnibus-Type/Archivo/master/OFL.txt`, read 2026-09-16 |
| Copyright | Copyright 2020 The Archivo Project Authors (https://github.com/Omnibus-Type/Archivo) |

One file per subset covers weights 400, 500 and 700: Archivo is a variable font,
so Google Fonts serves the same file for each declared weight. Only the `latin`
and `latin-ext` subsets are shipped. The `vietnamese` subset is available upstream
and is not used by either site.

The OFL requires the licence to travel with the font. `Archivo-OFL.txt` is that
copy; do not delete it when pruning assets.

## JetBrains Mono

| | |
|---|---|
| Family | JetBrains Mono (variable weight axis; files cover 400, 500 and 700) |
| Files | `jetbrains-mono-latin.woff2` (31,340 bytes), `jetbrains-mono-latin-ext.woff2` (11,596 bytes) |
| Version | v24, as served by Google Fonts |
| Retrieved | 2026-09-18, from `https://fonts.gstatic.com/s/jetbrainsmono/v24/` |
| Licence | SIL Open Font License 1.1 — full text in `JetBrainsMono-OFL.txt` |
| Licence source | `https://raw.githubusercontent.com/JetBrains/JetBrainsMono/master/OFL.txt`, read 2026-09-18 |
| Copyright | Copyright 2020 The JetBrains Mono Project Authors (https://github.com/JetBrains/JetBrainsMono) |

One file per subset covers weights 400, 500 and 700: JetBrains Mono is a variable
font as served by Google Fonts, so the same file is used for each declared
weight. Only the `latin` and `latin-ext` subsets are shipped. The `cyrillic`,
`cyrillic-ext`, `greek` and `vietnamese` subsets are available upstream and are
not used by either site.

The OFL requires the licence to travel with the font. `JetBrainsMono-OFL.txt` is
that copy; do not delete it when pruning assets.

## Nothing on a CDN

Since #115 (MODEL-24) switched `web3d/explorer.html`, every page on both sites
takes its fonts from `/fonts/` and none requests Google Fonts or any other
third-party host. `tests/test_no_font_cdn.py` fails if a Google font host
reappears in the runtime tree or a built site.
