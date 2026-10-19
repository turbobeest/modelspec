"""Perplexity FAQ citations keep values and provenance without page copies."""

from datetime import UTC, date, datetime

import pytest

from decision.model import CitedRegion, Source, SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore, FetchResult, fingerprint_bytes, recheck
from decision.verify import Claim, Queue, StoredRegions, VerificationLog, deterministic_extractors, run, verify


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
