"""One malformed URL fails closed for its own record and never aborts a build or job.

REV-857 round-2 probes (MODEL-420). ``is_cite_only`` reads a malformed HTTP(S)
URL as cite-only, the restrictive choice for retention and display; callers
where cite-only status grants something use ``cite_only_status`` and refuse.
"""

from dataclasses import replace
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
import yaml

from decision.model import Source, SourceRef
from decision.retention import canonical_host, cite_only_status, is_cite_only
from decision.sources import CopyStore, FetchResult, recheck
from decision.verify import StoredRegions, verify
from tests.snapshot_records import SOURCES, evidence, fact
from tests.test_cite_only_verification import (
    CITE_URL, CONTEXT, TODAY, claim as make_claim, loaded, rejected, snapshot_input,
)

BAD_URL = "https://example.com:bad/pricing"


@pytest.mark.parametrize("url,host,cited", [
    ("https://api.docs.example.org/path", "api.docs.example.org", False),
    ("https://EXAMPLE.ORG/path", "example.org", False),
    ("https://Example.ORG:443/path", "example.org", False),
    ("http://Example.ORG:443/path", "example.org", False),
    ("https://bücher.example/path", "xn--bcher-kva.example", False),
    ("https://例え.テスト/path", "xn--r8jz45g.xn--zckzah", False),
    ("https://docs.x.ai/path", "docs.x.ai", True),
    ("https://DOCS.X.AI:443/path", "docs.x.ai", True),
    ("https://x.ai。/path", "x.ai", True),
    ("https://x.ai.evil.example/path", "x.ai.evil.example", False),
    ("https://evil.example\\@x.ai/path", "evil.example", False),
])
def test_canonical_ordinary_and_restricted_hosts(url, host, cited):
    assert canonical_host(url) == host
    assert is_cite_only(url) is cited
    assert cite_only_status(url) is cited


@pytest.mark.parametrize("url", [BAD_URL, "https://x.ai:99999/", "https://reader@example.org/",
                                 "http://["])
def test_malformed_url_is_restricted_but_never_granted(url):
    assert is_cite_only(url) is True
    assert cite_only_status(url) is None


@pytest.mark.parametrize("url", ["https://board.example.org:bad/results",
                                 "https://reader@board.example.org/results"])
def test_one_bad_evidence_display_url_does_not_abort_snapshot(url):
    row = evidence("lab/alpha", "swe_bench_pro", 55.0, source_url=url)
    inputs = replace(snapshot_input(url=SOURCES["src-lab-docs"], outcome="verified"),
                     evidence=[row])
    index = loaded(inputs)
    assert index.evidence("lab/alpha", "swe_bench_pro") == ()
    assert index.fact(*CONTEXT).state == "known"


@pytest.mark.parametrize("url", [BAD_URL, "https://reader@lab.example.com/docs/models"])
def test_malformed_registered_url_excludes_only_its_fact(url):
    inputs = snapshot_input(url=url, outcome="verified")
    assert rejected(inputs)[CONTEXT] == "invalid_citation"
    assert loaded(inputs).fact(*CONTEXT).state == "unknown"


def test_bad_claim_redirect_is_excluded_without_aborting_verifier(tmp_path):
    row = fact("model", "lab/alpha", "model.context_window", 128000)
    row["sources"][0]["resolved_urls"] = ["https://reader@ordinary.example/"]
    claim = replace(make_claim(), sources=(SourceRef.model_validate(row["sources"][0]),))
    regions = StoredRegions(CopyStore(tmp_path / "cache"),
                            {"src-lab-docs": Source(id="src-lab-docs", url=SOURCES["src-lab-docs"])})
    result = verify(claim, regions, [], today=TODAY)
    assert result.outcome in {"skipped", "unreachable", "cited"}
    assert result.verification is None


def test_one_bad_fetch_redirect_does_not_abort_recheck(tmp_path):
    class FakeFetcher:
        def __init__(self):
            self.calls = []

        def fetch(self, url, **kwargs):
            self.calls.append(url)
            return FetchResult("ok", body=b"<p>sample</p>",
                               resolved_urls=("https://example.org:bad/",)
                               if len(self.calls) == 1 else ())

    fetcher = FakeFetcher()
    sources = [Source(id="bad", url="https://example.org/bad"),
               Source(id="good", url="https://example.org/good")]
    store = CopyStore(tmp_path / "cache")
    report = recheck(sources, {}, [], fetcher=fetcher, store=store,
                     now=datetime(2026, 10, 20, tzinfo=UTC))
    assert len(fetcher.calls) == 2
    assert report.states["good"].snapshot is not None
    assert report.states["bad"].snapshot is None
    assert ("bad", "invalid_citation_metadata") in {
        (item.source_id, item.reason) for item in report.skipped}


def test_store_put_bad_url_refuses_bytes(tmp_path):
    store = CopyStore(tmp_path / "cache")
    with pytest.raises(ValueError):
        store.put(b"private content", source_url="https://example.org:bad/")
    assert not list(tmp_path.rglob("*"))


def test_store_put_bad_redirect_keeps_no_bytes(tmp_path):
    store = CopyStore(tmp_path / "cache")
    ref = store.put(b"private content", source_url="https://example.org/",
                    resolved_urls=["https://example.org:bad/"])
    assert not store.path(ref).exists()
    assert store.has(ref) is False


@pytest.mark.parametrize("read_url,expected", [
    ("https://reader@x.ai/pricing", "read is not cite-only"),
    ("https://x.ai:99999/pricing", "read is not cite-only"),
])
def test_malformed_supersession_read_url_never_supersedes(read_url, expected):
    from types import SimpleNamespace

    from decision.supersession import _refusal

    record = SimpleNamespace(
        target=SimpleNamespace(id="f"),
        mismatch=SimpleNamespace(date=date(2026, 10, 1), method="re-read", source_id="m",
                                 url="https://x.ai/old", region="r"),
        read=SimpleNamespace(source_id="s", url=read_url, region="r2"),
    )
    winner = {"outcome": "mismatch", "date": "2026-10-01", "method": "re-read",
              "target": {"value_hash": "h", "id": "f"}}
    sources = {"m": "https://x.ai/old", "s": read_url}
    assert _refusal(record, winner, "h", [], sources) == expected


# Builds, pages and batch jobs


def model_front(source=BAD_URL, model_id="lab/test"):
    return {
        "model_id": model_id, "display_name": "Test", "provider": "lab",
        "model_type": "llm-chat",
        "benchmarks": {"scores": {"humaneval": 90}, "benchmark_source": source},
    }


def card_text(front):
    return "---\n" + yaml.safe_dump(front) + "---\n"


def invalid_fact(kind, subject, facet):
    return {
        "id": f"{subject}#{facet}",
        "subject": {"kind": kind, "id": subject},
        "facet": facet, "state": "known", "value": 20,
        "sources": [{
            "source_id": "ordinary", "snapshot_ref": "sha256:" + "1" * 64,
            "cited_regions": ["page"], "resolved_urls": [BAD_URL],
        }],
    }


def write_registry(root):
    path = root / "registry"
    path.mkdir()
    (path / "sources.yaml").write_text(yaml.safe_dump({
        "schema_version": 1,
        "sources": [{"id": "ordinary", "url": "https://example.com/pricing"}],
    }))


def test_page_render_survives_bad_benchmark_source():
    from pipeline.export import Build
    from pipeline.load import Catalogue, Model
    from pipeline.render import model_page

    model = Model("lab/test", Path("models/lab/test.md"), model_front(), "")
    assert model.scores_citation == {"status": "cited", "url": BAD_URL}
    page = model_page(model, Build("b" * 40, "2026-10-20", date(2026, 10, 20)), {},
                      Catalogue(date(2026, 10, 20)))
    notice = page.split("Cited, not machine-verified", 1)[1].split("</div>", 1)[0]
    assert "<a" not in notice and "score source" in notice


def test_ranking_survives_bad_benchmark_source():
    from pipeline.ranking import build_candidates
    from schema.card import ModelCard
    from schema.graph import CollectingSink

    bad = ModelCard.from_yaml_string(card_text(model_front()))
    good = ModelCard.from_yaml_string(card_text(
        model_front("https://example.com/pricing", "lab/good")))
    candidates = {item.model_id: item for item in build_candidates([bad, good], CollectingSink())}
    assert {"lab/good", "lab/test"} <= set(candidates)
    assert candidates["lab/test"].cited_benchmarks  # restrictive: never counted as verified
    assert not candidates["lab/good"].cited_benchmarks


def test_model_load_survives_invalid_fact_redirect(tmp_path):
    from pipeline.load import load_models

    write_registry(tmp_path)
    folder = tmp_path / "models" / "lab"
    folder.mkdir(parents=True)
    front = model_front()
    front["benchmarks"] = {}
    front["facts"] = [invalid_fact("model", "lab/test", "model.context_window")]
    (folder / "test.md").write_text(card_text(front))
    good = model_front(model_id="lab/good")
    good["benchmarks"] = {}
    (folder / "good.md").write_text(card_text(good))
    models = {model.model_id: model for model in load_models(tmp_path)}
    assert "lab/good" in models
    [cited] = models["lab/test"].cited_facts
    assert (cited["verification"], cited["citation"]) == (None, {"status": "cited", "sources": []})


def test_weekly_run_survives_invalid_unfiled_fact_redirect(tmp_path):
    from scripts.price_reread import run

    write_registry(tmp_path)
    folder = tmp_path / "offerings" / "subscriptions"
    folder.mkdir(parents=True)
    (folder / "lab.yaml").write_text(yaml.safe_dump([{
        "kind": "subscription", "provider": "lab", "plan": "pro", "name": "Pro",
        "facts": [invalid_fact("offering", "lab/subscription/pro", "offering.subscription.price")],
    }]))

    class NoNetwork:
        def fetch(self, *args, **kwargs):
            pytest.fail("An unfiled fact must not trigger any fetch")

    report = run(root=tmp_path, fetcher=NoNetwork(), store=CopyStore(tmp_path / "copies"),
                 today=date(2026, 10, 20))
    assert not report.sources


def test_watch_survives_malformed_card_url(tmp_path):
    from scripts.curation.watch import FetchResult as WatchFetch, watch

    (tmp_path / "bad.md").write_text("---\nid: bad\nleaderboard_url: " + BAD_URL + "\n---\n")
    watch(["bad"], tmp_path / "state", bench_dir=tmp_path,
          fetcher=lambda url: WatchFetch(url, None, error="bad port"), js_hosts=set())


def test_audit_load_survives_malformed_registered_source(tmp_path):
    from scripts.data_trust.catalogue import load, registered_cite_only

    (tmp_path / "registry").mkdir()
    (tmp_path / "registry/sources.yaml").write_text(
        "sources:\n- id: bad\n  url: " + BAD_URL + "\n")
    (tmp_path / "models").mkdir()
    (tmp_path / "models/m.md").write_text(
        "---\nmodel_id: m\nfacts:\n- id: f\n  facet: model.foo\n  citation: {status: cited}\n"
        "  sources: [{source_id: bad}]\n---\n")
    catalogue = load(tmp_path)
    # A malformed URL never earns the audit's cite-only dating.
    assert registered_cite_only(catalogue, {"source_id": "bad"}) is False


def test_purge_scan_treats_malformed_provenance_as_restricted(tmp_path):
    from scripts.purge_cite_only_copies import Provenance, find_entries

    store = CopyStore(tmp_path / "store")
    ref = store.put(b"body", source_url="https://example.com/source")
    provenance = Provenance()
    provenance.urls[ref].add(BAD_URL)
    scan = find_entries([tmp_path / "store"], provenance, [])
    assert scan.scanned == 1


def test_proposal_plan_skips_malformed_manifest_entry():
    from scripts.curation.propose import plan

    proposed, skipped = plan([{"accepted": True, "changed": True, "url": BAD_URL}])
    assert proposed == [] and len(skipped) == 1
