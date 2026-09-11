"""Sitemaps must stay readable by Google, not only by our parser.

A one-line 143 KiB modelspec sitemap was well-formed XML and identical to
the built file, and Search Console still reported "could not be read".
The 100 KiB one-line benchgraph sitemap on the same generator succeeded.
Pretty-printing keeps every line far under a 128 KiB cap.
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.render import sitemap  # noqa: E402

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
_MAX_LINE = 8_192


def test_sitemap_is_pretty_printed_and_well_formed() -> None:
    paths = ["/", "/models/", "/m/openai/gpt-6-astra/"]
    xml = sitemap("https://modelspec.dev", paths, date(2026, 9, 10))
    lines = xml.splitlines()
    assert lines[0] == '<?xml version="1.0" encoding="UTF-8"?>'
    assert lines[1].startswith("<urlset ")
    assert lines[-1] == "</urlset>"
    assert all(len(line) < _MAX_LINE for line in lines)
    assert xml.endswith("\n")

    root = ET.fromstring(xml)
    locs = [el.text for el in root.findall(".//sm:loc", NS)]
    assert locs == [
        "https://modelspec.dev/",
        "https://modelspec.dev/models/",
        "https://modelspec.dev/m/openai/gpt-6-astra/",
    ]
    lastmods = {el.text for el in root.findall(".//sm:lastmod", NS)}
    assert lastmods == {"2026-09-10"}


def test_a_catalogue_sized_sitemap_has_no_oversized_line() -> None:
    paths = [f"/m/provider/model-{i}/" for i in range(1_500)]
    xml = sitemap("https://modelspec.dev", paths, date(2026, 9, 10))
    assert max(len(line) for line in xml.splitlines()) < _MAX_LINE
    root = ET.fromstring(xml)
    assert len(root.findall("sm:url", NS)) == 1_500
