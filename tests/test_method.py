"""Methodology page data, signing and link contracts."""

from __future__ import annotations

import gzip
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import pytest

from api.ranking.engine import neutrality_commitment
from decision.excluded import REMOVED_TEXT
from pipeline import landing, method
from pipeline.ranking import _basis

ROOT = Path(__file__).resolve().parents[1]
HREF = re.compile(r'href="([^"]+)"')


@pytest.fixture(scope="module")
def data() -> landing.LandingData:
    return landing.build_data(str(ROOT), date.today())


def test_page_uses_snapshot_tie_data(data: landing.LandingData) -> None:
    page = method.page(data, method.SigningState(method.load_key_ids(ROOT), None))
    tied = len(data.tie) - 1
    assert f"tell {tied} of these models apart" in page
    assert f"{tied} of the other {len(data.models) - 1} models reach" in page
    assert data.leader.name in page
    assert data.cheapest.name in page


def _signing_fixture(
    tmp_path: Path, key_ids: tuple[str, ...], signatures: list[dict],
) -> method.SigningState:
    root = tmp_path / "root"
    tree = tmp_path / "tree"
    keys = root / method.KEYS_REL
    keys.parent.mkdir(parents=True)
    keys.write_text(json.dumps({"keys": [{"key_id": key_id} for key_id in key_ids]}))
    snapshot = tree / method.SNAPSHOT_REL
    snapshot.parent.mkdir(parents=True)
    snapshot.write_bytes(gzip.compress(json.dumps({"signatures": signatures}).encode()))
    return method.load_signing_state(tree, root)


def test_signing_section_reads_signed_snapshot_with_published_key(
    data: landing.LandingData, tmp_path: Path,
) -> None:
    state = _signing_fixture(
        tmp_path, ("ed25519-test",),
        [{"alg": "ed25519", "key_id": "ed25519-test", "value": "fixture"}],
    )
    page = method.page(data, state)
    assert "This snapshot is Ed25519-signed with published key ID" in page
    assert "ed25519-test" in page
    assert "modelspec snapshot fetch" in page
    assert 'signature_verified": true' in page
    assert "Signing key being re-issued" not in page


def test_signing_section_reports_published_key_but_unsigned_snapshot(
    data: landing.LandingData, tmp_path: Path,
) -> None:
    page = method.page(data, _signing_fixture(tmp_path, ("ed25519-test",), []))
    assert ("A public signing key is published (id <code>ed25519-test</code>); this snapshot "
            "is not yet signed with it. Signing key being re-issued.") in page
    assert "This snapshot is Ed25519-signed" not in page
    assert 'signature_verified": false' in page


def test_signing_section_reports_no_public_key(data: landing.LandingData, tmp_path: Path) -> None:
    page = method.page(data, _signing_fixture(tmp_path, (), []))
    assert "Signing key being re-issued." in page
    assert "This snapshot is Ed25519-signed" not in page
    assert "A public signing key is published" not in page


def test_neutrality_quote_is_the_engine_commitment(data: landing.LandingData) -> None:
    page = method.page(data, method.SigningState((), None))
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
        if rel == "api/decision/snapshot.json.gz":
            target.write_bytes(gzip.compress(b'{"signatures":[]}'))
        else:
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
    page = method.page(data, method.SigningState(method.load_key_ids(ROOT), None))
    assert "MODEL-" not in page
    assert "coming soon" not in page.lower()
    assert REMOVED_TEXT.search(page) is None
    assert '<link rel="canonical" href="https://modelspec.dev/method/">' in page
    assert "noindex" not in page


def test_evidence_basis_labels_match_ranking_code(data: landing.LandingData) -> None:
    page = method.page(data, method.SigningState((), None))
    labels = {
        _basis(0, 0, 0),
        _basis(2, 0, 1),
        _basis(2, 1, 1),
        _basis(2, 2, 0.5),
        _basis(2, 2, 1),
    }
    assert labels == {"none", "unverified-legacy", "mixed", "partial-verified", "verified"}
    for label in labels:
        assert f"<code>{label}</code>" in page
    assert "_basis(): the evidence_basis labels" in page


def test_tie_benchmark_and_public_data_explanations(data: landing.LandingData) -> None:
    page = method.page(data, method.SigningState((), None))
    assert "not_separable" in page
    assert "stable transport order" in page
    assert "Inside a tie, choose on something else" in page
    assert "Every admitted benchmark with at least two model observations counts" in page
    assert "The <code>/v1/policy-check</code> determinations are private" in page
