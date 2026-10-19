"""MODEL-408 cite-only integration, using synthetic documents and offline HTTP."""

from datetime import UTC, datetime

import httpx
import pytest

from decision import verify
from decision.model import CitedRegion, Source, SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore, Fetcher, fingerprint_bytes, recheck
from tests.test_xai_consumer_lineup import PAGE, PLANS
from tests.test_xai_consumer_lineup import current_template as current_template

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
@pytest.mark.parametrize("field,value", [
    ("price", 8), ("billing_period", "monthly"), ("models_covered", None),
    ("usage_allowance", None), ("programmatic_or_agent_use", "Synthetic product access"),
    ("coverage_quote", None),
])
def test_current_plan_verification_is_cited_without_a_retained_copy(
    tmp_path, url, plan, field, value,
):
    source = source_for(url)
    claim = verify.Claim(
        target=TargetRef(kind="fact", id=f"{plan}-{field}"),
        subject=f"xai/subscription/{plan}", names=(plan.title(),),
        field=f"offering.subscription.{field}", value=value,
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


@pytest.mark.parametrize("url", URLS)
@pytest.mark.parametrize("plan,price,access", [
    ("free", 0, "Grok Build limited; Grok Bot not included"),
    ("plus", 8, "Grok Build included; Grok Bot not included"),
    ("premium", 30, "Grok Build included; Grok Bot included"),
    ("super", 100, "Grok Build included; Grok Bot included"),
    ("ultra", 200, "Grok Build included; Grok Bot included"),
    ("teams", None, "Grok Build included; Grok Bot included"),
    ("enterprise", None, "Grok Build included; Grok Bot included"),
])
def test_current_plan_values_survive_transient_read_and_cited_snapshot(
    tmp_path, current_template, url, plan, price, access,
):
    from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
    from decision.xai_matrix import read_matrix
    from tests.snapshot_records import fact, subscription

    sid = f"xai/subscription/{plan}"
    expected = {"price": price, "billing_period": "monthly" if price is not None else None,
                "models_covered": None, "usage_allowance": None,
                "programmatic_or_agent_use": access}
    source = source_for(url)
    store = CopyStore(tmp_path / "copies")
    ref = store.put(PAGE.encode(), source_url=url, retrieved_at=FETCHED)
    facts = []
    for field, value in expected.items():
        facet = f"offering.subscription.{field}"
        if value is not None:
            assert read_matrix(current_template, PAGE, subject=sid, facet=facet,
                               catalogue_ids=frozenset()) == (sid, str(value))
        row = fact("offering", sid, facet, value, source=source.id,
                   state="known" if value is not None else "unknown", outcome=None)
        row["sources"] = [SourceRef(
            source_id=source.id, snapshot_ref=ref, cited_regions=["page"], retrieved_at=FETCHED,
        ).model_dump(mode="json")]
        facts.append(row)
    index = load_built_snapshot(build_snapshot(
        SnapshotInputs(subscriptions=[subscription("xai", plan, facts=facts)],
                       sources={source.id: url}), as_of=FETCHED.date(),
    ))

    offerings = index.subscription_offerings()
    assert len(offerings) == 1
    assert offerings[0]["id"] == sid
    for field, value in expected.items():
        facet = f"offering.subscription.{field}"
        if value is None:
            assert facet not in offerings[0]["facts"]
            continue
        result = offerings[0]["facts"][facet]
        assert result.value == value
        assert result.state == "known"
        record = index.record(result.record_id)
        assert record["verification"] is None
        assert record["citation"] == {"status": "cited", "sources": [{
            "source_id": source.id, "url": url, "snapshot_ref": ref,
            "retrieved_at": "2026-10-19T12:00:00Z",
        }]}
    assert not store.path(ref).exists()
    assert len(list(tmp_path.rglob("*.citation.json"))) == 1
