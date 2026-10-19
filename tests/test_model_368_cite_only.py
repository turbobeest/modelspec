"""Perplexity FAQ citations keep values and provenance without page copies."""

from datetime import UTC, date, datetime

import pytest

from decision.model import CitedRegion, Source, SourceRef, TargetRef, VerificationActor
from decision.perplexity_faq import prepare_pro_faq
from decision.sources import CopyStore, FetchResult, fingerprint_bytes, recheck
from decision.verify import Claim, Queue, StoredRegions, VerificationLog, deterministic_extractors, run, verify
from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
from scripts.price_reread import fetch_sources
from tests.snapshot_records import SOURCES, fact, model, subscription


FETCHED = datetime(2026, 10, 18, 16, tzinfo=UTC)
TODAY = date(2026, 10, 19)
PAGE = b'<section id="faq"><p>Synthetic transient FAQ sentinel.</p></section>'
VALUE = ["anthropic/claude-sonnet-5", "openai/gpt-5-6-terra"]
URLS = ["https://perplexity.ai/pro", "https://www.perplexity.ai/pro"]


def source(url):
    return Source(
        id="model-368-perplexity-pro-faq", url=url, kind="provider_documentation",
        normaliser="html-icon-labels",
        cited_regions=[CitedRegion(id="faq", locator={"kind": "css", "value": "#faq"})],
    )


def claim():
    return Claim(
        target=TargetRef(kind="fact", id="perplexity-pro-models"),
        subject="perplexity/subscription/pro", names=("Perplexity Pro",),
        field="offering.subscription.models_covered", value=VALUE,
        collector=VerificationActor(agent="collector", model_family="openai", method="read"),
        sources=(SourceRef(source_id="model-368-perplexity-pro-faq",
                           snapshot_ref=fingerprint_bytes(PAGE), cited_regions=["faq"]),),
    )


@pytest.mark.parametrize("url", URLS)
def test_perplexity_recheck_persists_only_citation_metadata(tmp_path, url):
    class TransientFetch:
        def fetch(self, *args, **kwargs):
            return FetchResult("ok", 200, body=PAGE, content_type="text/html")

    store = CopyStore(tmp_path)
    report = recheck([source(url)], {}, [], fetcher=TransientFetch(), store=store, now=FETCHED)
    ref = fingerprint_bytes(PAGE)
    assert not store.path(ref).exists()
    assert all(b"Synthetic transient FAQ sentinel" not in p.read_bytes()
               for p in tmp_path.rglob("*") if p.is_file())
    assert store.citation(ref)["url"] == url
    assert store.citation(ref)["retrieved_at"] == FETCHED.isoformat()
    assert report.states[source(url).id].snapshot.copy_ref == ref


@pytest.mark.parametrize("url", URLS)
def test_perplexity_verify_is_cited_without_page_bytes(tmp_path, url):
    regions = StoredRegions(CopyStore(tmp_path), {source(url).id: source(url)})
    filed = claim()
    result = verify(filed, regions, deterministic_extractors(), today=TODAY)
    assert result.outcome == "cited"
    assert result.verification is None
    assert filed.value == VALUE


@pytest.mark.parametrize("url", URLS)
def test_perplexity_historical_html_is_not_replayed(tmp_path, url):
    store = CopyStore(tmp_path)
    ref = fingerprint_bytes(PAGE)
    # Simulate an old copy without a marker. Never fetch a real page.
    store.path(ref).parent.mkdir(parents=True, exist_ok=True)
    store.path(ref).write_bytes(PAGE)
    regions = StoredRegions(store, {source(url).id: source(url)})
    assert regions.page_html(source(url).id, ref) is None


def test_perplexity_queue_records_cited_without_verification_or_recrawl(tmp_path):
    queue = Queue(tmp_path / "verification")
    log = VerificationLog(tmp_path / "verification")
    filed = claim()
    queue.file(filed, at=FETCHED)
    regions = StoredRegions(CopyStore(tmp_path / "copies"), {source(URLS[1]).id: source(URLS[1])})
    report = run(queue, log, regions, deterministic_extractors(), today=TODAY)
    assert report.counts.get("cited", 0) == 1
    assert report.counts["verified"] == 0
    assert not log.records()
    assert queue.pending() == ([], [])
    assert queue.recrawl_requests() == []


@pytest.mark.parametrize("url", URLS)
def test_perplexity_rendered_faq_reread_keeps_only_citation(tmp_path, url):
    registered = source(url).model_copy(update={"fetch": "rendered"})

    class RenderedFaq:
        def fetch(self, requested_url, **kwargs):
            assert requested_url == url
            assert kwargs["prepare"] is prepare_pro_faq
            return FetchResult("ok", 200, body=PAGE, content_type="text/html", retrieved_at=FETCHED)

    class NoHttp:
        def fetch(self, *args, **kwargs):
            pytest.fail("rendered FAQ must use the rendered reader")

    store = CopyStore(tmp_path)
    result = fetch_sources([registered.id], {registered.id: registered}, NoHttp(), store,
                           rendered=RenderedFaq())[registered.id]
    assert result.outcome == "cited"
    assert result.copy_ref == fingerprint_bytes(PAGE)
    assert store.citation(result.copy_ref)["retrieved_at"] == FETCHED.isoformat()
    assert not store.path(result.copy_ref).exists()
    assert all(b"Synthetic transient FAQ sentinel" not in p.read_bytes()
               for p in tmp_path.rglob("*") if p.is_file())


@pytest.mark.parametrize("url", URLS)
def test_perplexity_snapshot_preserves_values_as_cited_even_with_old_verification(url):
    sid = "perplexity/subscription/pro"
    row = fact("offering", sid, "offering.subscription.models_covered", VALUE, source="faq")
    row["sources"][0].update(snapshot_ref=fingerprint_bytes(PAGE), retrieved_at=FETCHED.isoformat())
    index = load_built_snapshot(build_snapshot(SnapshotInputs(
        models=[model(mid) for mid in VALUE],
        subscriptions=[subscription("perplexity", facts=[row])],
        sources={**SOURCES, "faq": url},
    ), as_of=TODAY))
    plans = index.subscription_offerings()
    assert len(plans) == 1
    assert plans[0]["id"] == sid
    admitted = plans[0]["facts"]["offering.subscription.models_covered"]
    assert admitted.state == "known"
    assert list(admitted.value) == ["anthropic/claude-sonnet-5", "openai/gpt-5-6-terra"]
    record = index.record(admitted.record_id)
    assert record["verification"] is None
    assert record["citation"] == {"status": "cited", "sources": [{
        "source_id": "faq", "url": url, "snapshot_ref": fingerprint_bytes(PAGE),
        "retrieved_at": FETCHED.isoformat(),
    }]}
