"""Synthetic pages exercise every source retention boundary without network calls."""

import json
from datetime import UTC, datetime

import httpx
import pytest

from decision.model import CitedRegion, Source
from decision.retention import cite_only_hosts, cite_only_status
from decision.sources import Citation, CopyStore, FactKind, Fetcher, FetchResult, fingerprint_bytes, recheck
from scripts import fetch_pricing, price_reread
from scripts.benchmarks import fetch as benchmark_fetch
from tests.test_price_reread import estate


PAGE = b"<html><p>Synthetic page text never retained for restricted hosts.</p></html>"
AT = datetime(2026, 10, 19, 12, tzinfo=UTC)


def test_cite_only_policy_contains_exactly_the_approved_hosts():
    assert set(cite_only_hosts()) == {
        "x.ai", "docs.x.ai", "perplexity.ai", "www.anthropic.com",
        "developers.openai.com", "help.openai.com", "chatgpt.com", "cursor.com",
    }


@pytest.mark.parametrize("url", [
    "https://x.ai/pricing", "https://DOCS.X.AI.:443/models", "https://www.perplexity.ai/pro",
    "https://www.anthropic.com/models", "https://sub.WWW.ANTHROPIC.COM.:443/models",
    "https://developers.openai.com/models", "https://sub.DEVELOPERS.OPENAI.COM.:443/models",
    "https://help.openai.com/models", "https://sub.HELP.OPENAI.COM.:443/models",
    "https://chatgpt.com/models", "https://sub.CHATGPT.COM.:443/models",
    "https://cursor.com/models", "https://sub.CURSOR.COM.:443/models",
])
def test_copy_store_cite_only_keeps_only_citation(tmp_path, url):
    store = CopyStore(tmp_path)
    ref = store.put(PAGE, source_url=url, retrieved_at=AT)
    assert ref == fingerprint_bytes(PAGE)
    assert not store.has(ref)
    assert not store.path(ref).exists()
    metadata = store.citation(ref)
    assert metadata["snapshot_ref"] == ref
    assert metadata["url"] == url
    assert metadata["retrieved_at"] == AT.isoformat()
    assert all(PAGE not in path.read_bytes() for path in tmp_path.rglob("*") if path.is_file())


@pytest.mark.parametrize("host", [
    "www.anthropic.com", "developers.openai.com", "help.openai.com", "chatgpt.com", "cursor.com",
])
def test_new_cite_only_hosts_require_a_label_boundary(host):
    assert cite_only_status(f"https://not{host}/models") is False
    assert cite_only_status(f"https://{host}.example/models") is False


@pytest.mark.parametrize("host", ["anthropic.com", "docs.anthropic.com", "openai.com", "api.openai.com"])
def test_new_cite_only_hosts_do_not_include_parents_or_siblings(host):
    assert cite_only_status(f"https://{host}/models") is False


def test_copy_store_requires_origin_and_preserves_unrestricted_hosts(tmp_path):
    store = CopyStore(tmp_path)
    with pytest.raises((TypeError, ValueError)):
        store.put(PAGE)
    for url in ("https://x.ai.example/pricing", "https://notx.ai/pricing", "https://example.test/"):
        ref = store.put(PAGE, source_url=url)
        assert store.get(ref) == PAGE
        assert store.citation(ref) is None


def test_copy_store_redirect_is_cite_only_even_with_existing_hash(tmp_path):
    store = CopyStore(tmp_path)
    ref = store.put(PAGE, source_url="https://example.test/")
    store.put(PAGE, source_url="https://example.test/redirect", resolved_urls=("https://x.ai/",))
    assert store.citation(ref)["resolved_urls"] == ["https://x.ai/"]


def test_fetcher_keeps_redirect_origins_for_retention(tmp_path):
    def respond(request):
        if request.url.host == "example.test":
            return httpx.Response(302, headers={"location": "https://x.ai/pricing"})
        return httpx.Response(200, content=PAGE)

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        result = Fetcher(client, min_host_interval=0).fetch("https://example.test/start")
    store = CopyStore(tmp_path)
    ref = store.put(result.body, source_url="https://example.test/start",
                    resolved_urls=result.resolved_urls)
    assert not store.path(ref).exists()
    assert "https://x.ai/pricing" in store.citation(ref)["resolved_urls"]


def source(url="https://x.ai/pricing", *, rendered=False):
    return Source(id="restricted", url=url, fetch="rendered" if rendered else "http",
                  cited_regions=[CitedRegion(id="page", locator={"kind": "page", "value": ""})])


class Replay:
    def fetch(self, url, **kwargs):
        return FetchResult("ok", 200, body=PAGE, content_type="text/html")


def test_recheck_hash_does_not_reconfirm_a_cited_fact(tmp_path):
    store = CopyStore(tmp_path)
    citations = [Citation("fact-1", "restricted", "page", FactKind.PRICE)]
    first = recheck([source()], {}, citations, fetcher=Replay(), store=store, now=AT)
    second = recheck([source()], first.states, citations, fetcher=Replay(), store=store, now=AT)
    assert second.reconfirmed == []
    assert second.states["restricted"].snapshot.copy_ref == fingerprint_bytes(PAGE)
    assert not store.path(fingerprint_bytes(PAGE)).exists()


def test_price_fetch_cite_only_does_not_write_copy(tmp_path):
    store = CopyStore(tmp_path)
    fetched = price_reread.fetch_sources(["restricted"], {"restricted": source()}, Replay(), store)
    assert fetched["restricted"].outcome == "cited"
    assert fetched["restricted"].copy_ref == fingerprint_bytes(PAGE)
    assert not store.path(fingerprint_bytes(PAGE)).exists()


def test_benchmark_named_cache_retains_metadata_not_text(tmp_path):
    result = benchmark_fetch.write_named_cache(
        "https://x.ai/pricing", PAGE.decode(), tmp_path, fetched_at="2026-10-19")
    assert result.text == PAGE.decode()
    assert not result.path.exists()
    metadata = json.loads(next(tmp_path.glob("*.meta.json")).read_text())
    assert metadata["snapshot_ref"] == fingerprint_bytes(PAGE)
    assert benchmark_fetch.load_named_cache("https://x.ai/pricing", tmp_path) is None


@pytest.mark.parametrize("url", [
    "https://x.ai/pricing", "https://sub.docs.x.ai/models", "https://WWW.PERPLEXITY.AI.:8443/pro",
])
def test_disk_scraper_refuses_cite_only_before_subprocess(tmp_path, monkeypatch, url):
    def forbidden(*args, **kwargs):
        pytest.fail("a direct cite-only URL must be refused before any scraper call")

    monkeypatch.setattr(fetch_pricing.subprocess, "run", forbidden)
    monkeypatch.setattr(benchmark_fetch, "scrape", forbidden)
    with pytest.raises(ValueError, match="cite-only"):
        fetch_pricing.scrape_url(url, tmp_path / "page.md")
    assert not list(tmp_path.iterdir())


def test_rendered_replay_carries_only_hash_and_fetch_date(estate, tmp_path):
    import hashlib

    root, store = estate
    registry = root / "registry/sources.yaml"
    registry.write_text(registry.read_text().replace("https://rendered.example/pricing", "https://x.ai/pricing"))
    destination = tmp_path / "rendered"
    destination.mkdir()
    previous = hashlib.sha256(b"https://x.ai/pricing").hexdigest() + ".html"
    (destination / previous).write_bytes(PAGE)
    price_reread.render_to(root=root, directory=destination, rendered=Replay())
    assert list(destination.iterdir()) == [destination / "manifest.json"]
    replay = price_reread.RenderedReplayFetcher(destination)
    result = replay.fetch("https://x.ai/pricing")
    assert result.body == b""
    assert result.snapshot_ref == fingerprint_bytes(PAGE)
    assert result.retrieved_at is not None
    fetched = price_reread.fetch_sources(["restricted"], {"restricted": source(rendered=True)},
                                         Replay(), store, rendered=replay)
    assert fetched["restricted"].outcome == "cited"
    assert not store.path(fingerprint_bytes(PAGE)).exists()


def test_weekly_citation_update_keeps_values_and_records_retrieval(estate):
    import yaml
    from decision.verify import Queue, VerificationLog

    root, store = estate
    registry = root / "registry/sources.yaml"
    registry.write_text(registry.read_text().replace("https://plans.example/pricing", "https://x.ai/pricing"))
    prior = len(VerificationLog(root / "verification").records())
    report = price_reread.run(root=root, store=store, fetcher=Replay(), today=AT.date(), at=AT, write=True)
    cited = [fact for fact in report.facts if fact.status.value == "cited"]
    assert len(cited) == 3
    assert len(VerificationLog(root / "verification").records()) == prior
    offerings = yaml.safe_load((root / "offerings/subscriptions/example.yaml").read_text())
    fact = offerings[0]["facts"][0]
    assert fact["value"] == 20
    assert fact["sources"][0]["snapshot_ref"] == fingerprint_bytes(PAGE)
    assert fact["sources"][0]["retrieved_at"]
    claim = Queue(root / "verification").filed()[("fact", fact["id"])]
    assert claim.sources[0].snapshot_ref == fingerprint_bytes(PAGE)
    assert claim.sources[0].retrieved_at is not None
    assert PAGE.decode() not in json.dumps(report.to_dict())
    assert not report.diffs.get("example-plans")
    # MODEL-423: the report carries each citation exactly as written, so the data
    # repository's guard can require the written citation to be this run's.
    [row] = [row for row in report.to_dict()["cited"] if row["fact"] == fact["id"]]
    written = fact["sources"][0]
    assert row["citations"] == {"example-plans": {
        key: written[key] for key in ("snapshot_ref", "retrieved_at", "resolved_urls")}}
    assert all("citations" not in row for row in report.to_dict()["alerts"]
               if row["status"] != "cited")


@pytest.mark.parametrize("url,links", [
    ("https://x.ai/pricing", False),
    ("https://example.test/start", False),
    ("https://example.test/start", True),
])
def test_benchmark_cli_emits_only_citation_metadata(tmp_path, monkeypatch, capsys, url, links):
    from types import SimpleNamespace

    payload = {"markdown": PAGE.decode(), "links": ["https://copied-page-link.example/"],
               "metadata": {"sourceURL": url, "url": "https://x.ai/pricing"}}
    monkeypatch.setattr(benchmark_fetch, "resolve_key", lambda: "synthetic-key")
    monkeypatch.setattr(benchmark_fetch, "CreditGuard", lambda **kwargs: SimpleNamespace(
        start=lambda: 200, last_remaining=199, spent=lambda: 1))
    monkeypatch.setattr(benchmark_fetch, "scrape", lambda *args, **kwargs: payload)
    args = [url, "--cache-dir", str(tmp_path)] + (["--links"] if links else [])
    assert benchmark_fetch.main(args) == 0
    output = capsys.readouterr().out
    assert PAGE.decode() not in output
    assert "copied-page-link" not in output
    citation = json.loads(output)
    assert citation["url"] == url
    assert citation["snapshot_ref"].startswith("sha256:")
    assert citation["retrieved_at"]


def test_failed_cite_only_reread_report_omits_old_quoted_value(estate):
    from dataclasses import replace
    import yaml
    from decision.verify import Queue

    root, store = estate
    registry = root / "registry/sources.yaml"
    registry.write_text(registry.read_text().replace("https://plans.example/pricing", "https://x.ai/pricing"))
    path = root / "offerings/subscriptions/example.yaml"
    rows = yaml.safe_load(path.read_text())
    fact = rows[0]["facts"][0]
    fact["value"] = PAGE.decode()
    path.write_text(yaml.safe_dump(rows))
    queue = Queue(root / "verification")
    claim = queue.filed()[("fact", fact["id"])]
    queue.file(replace(claim, value=PAGE.decode()), at=AT)

    class Unreachable:
        def fetch(self, url, **kwargs):
            return FetchResult("unreachable", 503, error="HTTP 503")

    report = price_reread.run(root=root, store=store, fetcher=Unreachable(), today=AT.date())
    assert PAGE.decode() not in json.dumps(report.to_dict())
