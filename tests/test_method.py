"""Methodology page data, signing and link contracts."""

from __future__ import annotations

import base64
import gzip
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from api.ranking.engine import neutrality_commitment
from decision.excluded import REMOVED_TEXT
from decision.registry import default as default_registry
from decision.snapshot import Ed25519Signer, Snapshot, SnapshotInputs, build_snapshot
from pipeline import landing, method
from pipeline.ranking import _basis
from tests.snapshot_records import SOURCES, evidence, model

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


KEY_ID = "ed25519-test"


def _built_snapshot() -> Snapshot:
    return build_snapshot(
        SnapshotInputs(
            models=[model("lab/alpha")],
            evidence=[evidence("lab/alpha", "swe_bench_pro", 55.0)],
            sources=SOURCES,
            benchmark_domains={"swe_bench_pro": [("software_engineering", "direct")]},
        ),
        registry=default_registry(),
        as_of=date(2026, 9, 25),
    )


def _keypair() -> tuple[str, str]:
    private = Ed25519PrivateKey.generate()
    raw = private.private_bytes(
        serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
        serialization.NoEncryption(),
    )
    public = private.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw,
    )
    return base64.b64encode(raw).decode(), base64.b64encode(public).decode()


def _signing_fixture(tmp_path: Path, *, sign_with: str | None, publish: str | None,
                     tamper: bool = False) -> method.SigningState:
    root = tmp_path / "root"
    tree = tmp_path / "tree"
    keys = root / method.KEYS_REL
    keys.parent.mkdir(parents=True)
    keys.write_text(json.dumps({
        "format": "modelspec.snapshot-keys", "version": 1,
        "keys": [] if publish is None else [
            {"alg": "ed25519", "key_id": KEY_ID, "public_key": publish}],
    }))
    signer = None if sign_with is None else Ed25519Signer(KEY_ID, sign_with)
    raw = gzip.decompress(_built_snapshot().to_bytes(key=None, ed25519_signer=signer))
    if tamper:
        assert b',null,55.0,"percent"' in raw
        raw = raw.replace(b',null,55.0,"percent"', b',null,56.0,"percent"', 1)
    snapshot = tree / method.SNAPSHOT_REL
    snapshot.parent.mkdir(parents=True)
    snapshot.write_bytes(gzip.compress(raw))
    return method.load_signing_state(tree, root)


def test_signing_section_reports_a_cryptographically_verified_signature(
    data: landing.LandingData, tmp_path: Path,
) -> None:
    private, public = _keypair()
    state = _signing_fixture(tmp_path, sign_with=private, publish=public)
    assert state.signed_key_id == KEY_ID
    page = method.page(data, state)
    assert "This snapshot is Ed25519-signed with published key ID" in page
    assert KEY_ID in page
    assert "modelspec snapshot fetch" in page
    assert 'signature_verified": true' in page
    assert "Signing key being re-issued" not in page


def test_a_signature_made_with_a_different_key_is_not_reported_as_signed(
    data: landing.LandingData, tmp_path: Path,
) -> None:
    private, _ = _keypair()
    _, other_public = _keypair()
    state = _signing_fixture(tmp_path, sign_with=private, publish=other_public)
    assert state.signed_key_id is None
    assert "Ed25519-signed" not in method.page(data, state)


def test_tampered_bytes_are_not_reported_as_signed(
    data: landing.LandingData, tmp_path: Path,
) -> None:
    private, public = _keypair()
    state = _signing_fixture(tmp_path, sign_with=private, publish=public, tamper=True)
    assert state.signed_key_id is None
    page = method.page(data, state)
    assert "Ed25519-signed" not in page
    assert "signature_verified" not in page


def test_published_key_but_unsigned_snapshot_shows_no_transcript(
    data: landing.LandingData, tmp_path: Path,
) -> None:
    _, public = _keypair()
    state = _signing_fixture(tmp_path, sign_with=None, publish=public)
    assert state.signed_key_id is None
    page = method.page(data, state)
    assert (f"A public signing key is published (id <code>{KEY_ID}</code>); this snapshot "
            "is not signed with it. Signing key being re-issued.") in page
    assert "Ed25519-signed" not in page
    assert "signature_verified" not in page
    assert "modelspec snapshot fetch" not in page
    assert "modelspec decide" not in page
    assert 'class="terminal"' not in page


def test_signing_section_reports_no_public_key(data: landing.LandingData, tmp_path: Path) -> None:
    page = method.page(data, _signing_fixture(tmp_path, sign_with=None, publish=None))
    assert "Signing key being re-issued." in page
    assert "Ed25519-signed" not in page
    assert "A public signing key is published" not in page
    assert "signature_verified" not in page


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


def test_tie_wording_matches_the_engines_overlap_rule(data: landing.LandingData) -> None:
    from decision.contract import parse_spec
    from decision.engine import decide
    from tests.test_decision_capability import snapshot

    index = snapshot()
    facets = default_registry().facet
    spec = parse_spec({"spec_version": 1, "optimize": {"max": "software_engineering"},
                       "explain": "summary", "limit": 10}, facets=facets)
    results = decide(spec, index, facets=facets).results
    ranges = {row.offering.model: index.capability_estimate(row.offering.model,
                                                             "software_engineering")
              for row in results}
    leader = results[0].offering.model

    def overlaps(a: str, b: str) -> bool:
        return max(ranges[a].low, ranges[b].low) <= min(ranges[a].high, ranges[b].high)

    for row in results:
        model_id = row.offering.model
        expected = any(overlaps(model_id, other) for other in ranges if other != model_id)
        assert ("not_separable" in row.warnings) == expected
    # The engine flags a model that overlaps a non-leader while clear of the leader.
    assert any("not_separable" in row.warnings and not overlaps(row.offering.model, leader)
               for row in results[1:])

    page = method.page(data, method.SigningState((), None))
    assert "max(A.low, B.low) ≤ min(A.high, B.high)" in page
    assert "for any other model B" in page
    assert "range of any other model in the domain being ranked, not only the leader" in page
    assert "C.high ≥ L.low" not in page
    assert "front-page figure, counted against the top estimate only" in page
