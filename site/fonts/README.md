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

## Still on the CDN

Space Grotesk and JetBrains Mono are still loaded from Google Fonts. They are
"the fonts already loaded" that MODEL-24 tolerates. Self-hosting them the same
way would satisfy MODEL-19's flat criterion outright; that is a follow-up, not
part of this change.
