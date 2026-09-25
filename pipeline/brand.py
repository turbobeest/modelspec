"""The ModelSpec mark 2a as served: favicons, touch and manifest icons, social card.

Source of truth is the delivered package in `brand/2a/`, committed unchanged
with its C2PA provenance. The served PNGs and SVG are those files byte for
byte; `favicon.ico` wraps the 16, 32 and 48 PNGs without resampling. The social
card `brand/og-card-2a.png` is the light lockup rendered by
`web/scripts/render-og-card.mjs`, committed because CI has no Segoe UI.

`pipeline.agent_ready` writes the set into the real build. The holding tree
keeps it (`pipeline.holding.KEEP_FILES`), and the live and internal decide
compositions copy it from the real build (`.github/workflows/deploy-sites.yml`).
"""

from __future__ import annotations

import json
import shutil
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "brand" / "2a"
SOCIAL_CARD = ROOT / "brand" / "og-card-2a.png"
SITE = "https://modelspec.dev"
TILE = "#0B1426"
#: The decide page's light background (`--bg` in web/src/decide/decide.css).
BACKGROUND = "#FAF9F8"

FAVICON_SIZES = (16, 32, 48)
#: Served name -> source file, copied byte for byte.
COPIED = {
    "favicon-64.png": PACKAGE / "png" / "modelspec-mark-64.png",
    "icon.svg": PACKAGE / "modelspec-mark.svg",
    "apple-touch-icon.png": PACKAGE / "png" / "modelspec-mark-180.png",
    "icon-192.png": PACKAGE / "png" / "modelspec-mark-192.png",
    "icon-512.png": PACKAGE / "png" / "modelspec-mark-512.png",
    "og-card.png": SOCIAL_CARD,
}
FILES = ("favicon.ico", *COPIED, "site.webmanifest")


def png_to_ico(*pngs: bytes) -> bytes:
    """Wrap PNGs in one ICO, one entry each. No resampling, no external fetch."""
    header = struct.pack("<HHH", 0, 1, len(pngs))
    entries, offset = b"", 6 + 16 * len(pngs)
    for png in pngs:
        if png[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError("not a PNG")
        if png[12:16] != b"IHDR":
            raise ValueError("PNG missing IHDR")
        width, height = struct.unpack(">II", png[16:24])
        entries += struct.pack("<BBBBHHII", width % 256, height % 256, 0, 0, 1, 32,
                               len(png), offset)
        offset += len(png)
    return header + entries + b"".join(pngs)


def manifest() -> str:
    return json.dumps({
        "name": "ModelSpec",
        "short_name": "ModelSpec",
        "start_url": "/",
        "display": "browser",
        "background_color": BACKGROUND,
        "theme_color": TILE,
        "icons": [
            {"src": f"/icon-{size}.png", "sizes": f"{size}x{size}", "type": "image/png"}
            for size in (192, 512)
        ],
    }, indent=2) + "\n"


def write_icons(tree: Path) -> list[str]:
    """Write the icon set into a site root. Returns the names written."""
    tree.mkdir(parents=True, exist_ok=True)
    (tree / "favicon.ico").write_bytes(png_to_ico(*(
        (PACKAGE / "png" / f"modelspec-mark-{size}.png").read_bytes()
        for size in FAVICON_SIZES)))
    for name, src in COPIED.items():
        shutil.copyfile(src, tree / name)
    (tree / "site.webmanifest").write_text(manifest(), encoding="utf-8")
    return list(FILES)


def head_links() -> str:
    """The `<head>` tags for the icon set."""
    sizes = " ".join(f"{s}x{s}" for s in FAVICON_SIZES)
    return (
        f'<link rel="icon" href="/favicon.ico" sizes="{sizes}">\n'
        '<link rel="icon" type="image/svg+xml" href="/icon.svg">\n'
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n'
        '<link rel="manifest" href="/site.webmanifest">\n'
    )


def social_meta(title: str) -> str:
    """og:image and twitter:card for `/`, pointing at the social card."""
    image = f"{SITE}/og-card.png"
    return (
        f'<meta property="og:title" content="{title}">\n'
        f'<meta property="og:url" content="{SITE}/">\n'
        f'<meta property="og:image" content="{image}">\n'
        '<meta property="og:image:width" content="1200">\n'
        '<meta property="og:image:height" content="630">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:image" content="{image}">\n'
    )
