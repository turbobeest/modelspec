"""Neither site loads fonts from a CDN at runtime (MODEL-92)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline import build as builder  # noqa: E402
from pipeline import render as r  # noqa: E402

CDN_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com")

_RUNTIME_DIRS = (ROOT / "site", ROOT / "web3d", ROOT / "pipeline")
_RUNTIME_SUFFIXES = {".html", ".css", ".js", ".py"}


def _mentions_cdn(text: str) -> bool:
    return any(host in text for host in CDN_HOSTS)


def _scan_tree(root: Path) -> list[Path]:
    hits: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in _RUNTIME_SUFFIXES:
            continue
        if _mentions_cdn(path.read_text(encoding="utf-8", errors="replace")):
            hits.append(path.resolve())
    return hits


def test_no_runtime_file_or_built_page_names_a_google_font_host(tmp_path) -> None:
    hits: list[Path] = []
    for directory in _RUNTIME_DIRS:
        hits.extend(_scan_tree(directory))
    fixture = ROOT / "tests" / "fixtures"
    if fixture.is_dir():
        hits.extend(_scan_tree(fixture))

    ms = tmp_path / "modelspec"
    builder._ship_instrument(ROOT, ms)
    hits.extend(_scan_tree(ms))

    assert sorted(hits) == [], [str(p) for p in sorted(hits)]
    assert not _mentions_cdn(r.FONTS)
    assert not _mentions_cdn(r.CSS)
