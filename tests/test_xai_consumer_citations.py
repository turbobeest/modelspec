"""MODEL-408 cite-only integration, using synthetic documents and offline HTTP."""

from datetime import UTC, datetime

import httpx
import pytest

from decision import verify
from decision.model import CitedRegion, Source, SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore, Fetcher, fingerprint_bytes, recheck
from tests.test_xai_consumer_lineup import PAGE, PLANS

FETCHED = datetime(2026, 10, 19, 12, 0, tzinfo=UTC)
URLS = ("https://x.ai/pricing", "https://docs.x.ai/docs/grok")


def source_for(url):
    return Source(
        id="current-xai-plans", url=url, kind="provider_documentation",
        normaliser="html-default",
        cited_regions=[CitedRegion(id="page", locator={"kind": "page", "value": ""})],
    )


@pytest.mark.parametrize("url", URLS)
def test_current_plan_recheck_persists_citation_without_page_bytes(tmp_path, url):
    source = source_for(url)
    body = PAGE.encode()
    store = CopyStore(tmp_path / "copies")
    with httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, content=body, headers={"content-type": "text/html"})
    )) as client:
        report = recheck([source], {}, [], fetcher=Fetcher(client), store=store, now=FETCHED)

    ref = fingerprint_bytes(body)
    assert not store.path(ref).exists()
    citation = store.citation(ref)
    assert citation["url"] == url
    assert citation["snapshot_ref"] == ref
    assert citation["retrieved_at"] == FETCHED.isoformat()
    assert not report.reconfirmed
    for path in tmp_path.rglob("*"):
        if path.is_file():
            assert b"Synthetic current-plan page" not in path.read_bytes()
            assert b"<table>" not in path.read_bytes()


@pytest.mark.parametrize("url", URLS)
@pytest.mark.parametrize("plan", PLANS)
def test_current_plan_verification_is_cited_without_a_retained_copy(tmp_path, url, plan):
    source = source_for(url)
    claim = verify.Claim(
        target=TargetRef(kind="fact", id=f"{plan}-price"),
        subject=f"xai/subscription/{plan}", names=(plan.title(),),
        field="offering.subscription.price", value=8,
        collector=VerificationActor(agent="fixture", model_family="openai", method="collect"),
        sources=(SourceRef(source_id=source.id, snapshot_ref=fingerprint_bytes(PAGE.encode()),
                           cited_regions=["page"]),),
    )
    result = verify.verify(
        claim, verify.StoredRegions(CopyStore(tmp_path / "copies"), {source.id: source}),
        verify.deterministic_extractors(), today=FETCHED.date(),
    )
    assert result.outcome == "cited"
    assert result.verification is None
    assert not list(tmp_path.rglob("*"))
