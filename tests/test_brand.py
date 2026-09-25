"""The ModelSpec mark 2a: the delivered package, and the icon set every tree serves."""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline import brand  # noqa: E402

PACKAGE = ROOT / "brand" / "2a"
MARK_IDS = ("tile", "y-axis", "x-axis", "m", "dots")


def _png_size(data: bytes) -> tuple[int, int]:
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", data[16:24])


def _ico_images(data: bytes) -> list[bytes]:
    reserved, kind, count = struct.unpack("<HHH", data[:6])
    assert (reserved, kind) == (0, 1)
    images = []
    for i in range(count):
        _, _, _, _, _, _, size, offset = struct.unpack("<BBBBHHII", data[6 + 16 * i:22 + 16 * i])
        images.append(data[offset:offset + size])
    return images


def test_the_package_is_committed_as_delivered_with_its_provenance():
    names = sorted(p.relative_to(PACKAGE).as_posix() for p in PACKAGE.rglob("*") if p.is_file())
    assert names == [
        "README.md",
        "modelspec-lockup-dark.svg",
        "modelspec-lockup-light.svg",
        "modelspec-mark-transparent.svg",
        "modelspec-mark.svg",
        *(f"png/modelspec-mark-{n}.png" for n in (1024, 16, 180, 192, 32, 48, 512, 64)),
    ]
    # The transparent mark was re-exported on 2026-09-25 (the delivered file
    # still carried the navy tile). A modified derivative must not carry the
    # original's C2PA manifest; every file as delivered keeps its own.
    rexported = {"modelspec-mark-transparent.svg"}
    for svg in PACKAGE.glob("*.svg"):
        text = svg.read_text(encoding="utf-8")
        if svg.name in rexported:
            assert "<c2pa:manifest>" not in text, svg.name
        else:
            assert "<c2pa:manifest>" in text, svg.name
    transparent = (PACKAGE / "modelspec-mark-transparent.svg").read_text(encoding="utf-8")
    assert 'id="tile"' not in transparent
    for element_id in ("y-axis", "x-axis", "m", "dots"):
        assert f'id="{element_id}"' in transparent
    for png in (PACKAGE / "png").glob("*.png"):
        assert b"caBX" in png.read_bytes(), png.name
    mark = (PACKAGE / "modelspec-mark.svg").read_text(encoding="utf-8")
    for element_id in MARK_IDS:
        assert f'id="{element_id}"' in mark


def test_write_icons_writes_exactly_the_icon_set(tmp_path):
    written = brand.write_icons(tmp_path)
    assert sorted(written) == sorted(brand.FILES)
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted(brand.FILES)
    assert set(brand.FILES) == {
        "favicon.ico", "favicon-64.png", "icon.svg", "apple-touch-icon.png",
        "icon-192.png", "icon-512.png", "site.webmanifest", "og-card.png",
    }


def test_favicon_ico_holds_the_16_32_and_48_pngs_unchanged(tmp_path):
    brand.write_icons(tmp_path)
    images = _ico_images((tmp_path / "favicon.ico").read_bytes())
    assert [_png_size(image) for image in images] == [(16, 16), (32, 32), (48, 48)]
    assert images == [(PACKAGE / "png" / f"modelspec-mark-{n}.png").read_bytes()
                      for n in (16, 32, 48)]


def test_the_png_and_svg_icons_are_the_package_files(tmp_path):
    brand.write_icons(tmp_path)
    for served, size in (("favicon-64.png", 64), ("apple-touch-icon.png", 180),
                         ("icon-192.png", 192), ("icon-512.png", 512)):
        data = (tmp_path / served).read_bytes()
        assert _png_size(data) == (size, size), served
        assert data == (PACKAGE / "png" / f"modelspec-mark-{size}.png").read_bytes(), served
    assert (tmp_path / "icon.svg").read_bytes() == (PACKAGE / "modelspec-mark.svg").read_bytes()


def test_the_manifest_names_the_192_and_512_icons(tmp_path):
    brand.write_icons(tmp_path)
    manifest = json.loads((tmp_path / "site.webmanifest").read_text(encoding="utf-8"))
    assert manifest["name"] == "ModelSpec"
    assert manifest["theme_color"] == "#0B1426"
    icons = {icon["src"]: icon for icon in manifest["icons"]}
    assert icons["/icon-192.png"]["sizes"] == "192x192"
    assert icons["/icon-512.png"]["sizes"] == "512x512"
    for src, icon in icons.items():
        assert icon["type"] == "image/png"
        assert (tmp_path / src.lstrip("/")).is_file(), src


def test_the_social_card_is_1200_by_630(tmp_path):
    brand.write_icons(tmp_path)
    assert _png_size((tmp_path / "og-card.png").read_bytes()) == (1200, 630)


def test_head_links_every_icon_and_the_social_card():
    head = brand.head_links()
    for tag in ('<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48">',
                '<link rel="icon" type="image/svg+xml" href="/icon.svg">',
                '<link rel="apple-touch-icon" href="/apple-touch-icon.png">',
                '<link rel="manifest" href="/site.webmanifest">'):
        assert tag in head
    social = brand.social_meta("ModelSpec")
    assert '<meta property="og:image" content="https://modelspec.dev/og-card.png">' in social
    assert '<meta name="twitter:card" content="summary_large_image">' in social


def test_the_decide_page_head_links_the_icons_and_the_social_card():
    html = (ROOT / "web" / "decide.html").read_text(encoding="utf-8")
    for href in ("/favicon.ico", "/icon.svg", "/apple-touch-icon.png", "/site.webmanifest"):
        assert f'href="{href}"' in html, href
    assert 'property="og:image" content="https://modelspec.dev/og-card.png"' in html
    assert 'property="og:image:width" content="1200"' in html
    assert 'name="twitter:card" content="summary_large_image"' in html
    assert 'property="og:url" content="https://modelspec.dev/"' in html


def test_the_v1_landing_links_the_2a_icons():
    html = (ROOT / "site" / "holding" / "index.html").read_text(encoding="utf-8")
    assert 'href="/apple-touch-icon.png"' in html
    assert 'href="/site.webmanifest"' in html
    assert 'content="https://modelspec.dev/og-card.png"' in html
    # The build writes these from the package; stale copies here would be overwritten.
    for stale in ("favicon-64.png", "icon-512.png", "og-card.png"):
        assert not (ROOT / "site" / "holding" / stale).exists(), stale
