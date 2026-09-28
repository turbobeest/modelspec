"""Methodology page data, signing and link contracts."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import pytest

from api.ranking.engine import neutrality_commitment
from decision.excluded import REMOVED_TEXT
from pipeline import landing, method

ROOT = Path(__file__).resolve().parents[1]
HREF = re.compile(r'href="([^"]+)"')


@pytest.fixture(scope="module")
def data() -> landing.LandingData:
    return landing.build_data(str(ROOT), date.today())


def test_page_uses_snapshot_tie_data(data: landing.LandingData) -> None:
    page = method.page(data, method.load_key_ids(ROOT))
    tied = len(data.tie) - 1
    assert f"tell {tied} of these models apart" in page
    assert f"{tied} of the other {len(data.models) - 1} models reach" in page
    assert data.leader.name in page
    assert data.cheapest.name in page


def test_signing_section_with_and_without_keys(data: landing.LandingData) -> None:
    signed = method.page(data, ("ed25519-test",))
    assert "Published key IDs:" in signed
    assert "ed25519-test" in signed
    assert "Signing key being re-issued" not in signed
    unsigned = method.page(data, ())
    assert "Signing key being re-issued" in unsigned
    assert "Published key IDs:" not in unsigned
    assert "signature_verified\": false while no public key is available" in unsigned


def test_neutrality_quote_is_the_engine_commitment(data: landing.LandingData) -> None:
    page = method.page(data, ())
    commitment = neutrality_commitment()
    assert commitment["pledge"] in page
    assert commitment["version"] in page


def test_every_github_path_exists_and_internal_data_link_is_built(
    data: landing.LandingData, tmp_path: Path,
) -> None:
    tree = tmp_path / "modelspec"
    for rel in ("api/decision/snapshot.json.gz", "api/decision/vocabulary.json",
                "api/rank/profiles.json", ".well-known/modelspec-snapshot-keys.json"):
        target = tree / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch()
    method.write(tree, ROOT, data)
    page = (tree / "method/index.html").read_text(encoding="utf-8")
    prefixes = ("https://github.com/turbobeest/modelspec/blob/main/",
                "https://github.com/turbobeest/modelspec/tree/main/")
    for href in HREF.findall(page):
        if href.startswith(prefixes):
            prefix = next(value for value in prefixes if href.startswith(value))
            rel = href.removeprefix(prefix).split("#", 1)[0]
            assert (ROOT / rel).exists(), href
        parsed = urlparse(href)
        if parsed.netloc and parsed.netloc != "modelspec.dev":
            continue
        if parsed.path.startswith("/api/") or parsed.path.startswith("/.well-known/"):
            assert (tree / parsed.path.lstrip("/")).exists(), href


def test_page_has_no_internal_ticket_language_or_removed_sources(data: landing.LandingData) -> None:
    page = method.page(data, method.load_key_ids(ROOT))
    assert "MODEL-" not in page
    assert "coming soon" not in page.lower()
    assert REMOVED_TEXT.search(page) is None
    assert '<link rel="canonical" href="https://modelspec.dev/method/">' in page
    assert "noindex" not in page
