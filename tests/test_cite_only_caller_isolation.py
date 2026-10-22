"""One malformed URL fails closed for its own record and never aborts a build or job.

REV-857 round-2 probes (MODEL-420). ``is_cite_only_restrictive`` reads a malformed HTTP(S)
URL as cite-only, the restrictive choice for retention and display; callers
where cite-only status grants something use ``cite_only_status`` and refuse.
"""

from dataclasses import replace
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
import yaml

from decision.model import Source, SourceRef
from decision.retention import (
    canonical_host, cite_only_origin_status, cite_only_status, is_cite_only_restrictive,
)
from decision.sources import CopyStore, FetchResult, recheck
from decision.verify import StoredRegions, verify
from tests.snapshot_records import SOURCES, evidence, fact
from tests.test_price_reread import estate  # noqa: F401  (fixture)
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
    assert is_cite_only_restrictive(url) is cited
    assert cite_only_status(url) is cited


@pytest.mark.parametrize("url", [BAD_URL, "https://x.ai:99999/", "https://reader@example.org/",
                                 "http://["])
def test_malformed_url_is_restricted_but_never_granted(url):
    assert is_cite_only_restrictive(url) is True
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
    # Granting: "cited" would skip verification, so a malformed URL is refused.
    assert (result.outcome, result.verification) == ("skipped", None)


def test_malformed_store_record_never_marks_a_claim_cited(tmp_path):
    import json

    claim = make_claim()
    store = CopyStore(tmp_path / "cache")
    ref = claim.sources[0].snapshot_ref
    path = store.path(ref).with_suffix(".citation.json")
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"snapshot_ref": ref, "url": SOURCES["src-lab-docs"],
                                "resolved_urls": ["https://reader@x.ai/"]}))
    source = Source(id="src-lab-docs", url=SOURCES["src-lab-docs"],
                    cited_regions=[{"id": "r1", "locator": {"kind": "page", "value": ""}}])
    regions = StoredRegions(store, {"src-lab-docs": source})
    assert regions.cite_only_status("src-lab-docs", ref) is None
    assert regions.cite_only("src-lab-docs", ref) is True  # restrictive: copy withheld
    assert regions.text("src-lab-docs", ref, "r1") is None
    assert verify(claim, regions, [], today=TODAY).outcome == "skipped"


def test_malformed_registered_url_is_not_reread_exempt():
    """Granting: a cite-only source puts a fact in re-read scope without a verified result."""
    from scripts.price_reread import _in_scope

    claim = make_claim()
    row = fact("model", "lab/alpha", "model.context_window", 128000, outcome=None)

    def sources(url):
        return {"src-lab-docs": Source(id="src-lab-docs", url=url)}

    assert _in_scope(row, claim, {}, sources("https://x.ai/pricing")) is None
    assert _in_scope(row, claim, {}, sources("https://reader@x.ai/pricing")) == (
        "a source URL is malformed")


@pytest.mark.parametrize("redirect,accepted", [
    ("https://docs.x.ai/pricing", True),
    ("https://reader@x.ai/pricing", False),
])
def test_rendered_replay_needs_well_formed_cite_only_origins(tmp_path, redirect, accepted):
    """Granting: a byte-free replay artifact is accepted only for a cite-only origin."""
    from scripts.price_reread import RenderedReplayFetcher

    url = "https://plans.example/pricing"
    entry = {"file": "a.html", "outcome": "ok", "status": 200, "error": None, "citation": {
        "url": url, "snapshot_ref": "sha256:" + "4" * 64, "resolved_urls": [redirect],
        "retrieved_at": "2026-10-19T12:00:00+00:00"}}
    if accepted:
        RenderedReplayFetcher(tmp_path, manifest={url: entry})
    else:
        with pytest.raises(ValueError, match="invalid cite-only rendered citation"):
            RenderedReplayFetcher(tmp_path, manifest={url: entry})


@pytest.mark.parametrize("redirect", ["https://reader@x.ai/", "https://x.ai:99999/"])
def test_byte_free_fetch_with_malformed_origin_is_refused(tmp_path, redirect):
    """Granting: a hash-only fetch result is recorded as cited only for a cite-only origin."""
    from decision.model import CitedRegion
    from scripts import price_reread

    class HashOnly:
        def fetch(self, url, **kwargs):
            return FetchResult("ok", 200, body=b"", snapshot_ref="sha256:" + "5" * 64,
                               resolved_urls=(redirect,))

    source = Source(id="s", url="https://plans.example/pricing", cited_regions=[
        CitedRegion(id="page", locator={"kind": "page", "value": ""})])
    store = CopyStore(tmp_path / "cache")
    fetched = price_reread.fetch_sources(["s"], {"s": source}, HashOnly(), store)
    assert (fetched["s"].outcome, fetched["s"].copy_ref) == ("invalid_citation_metadata", None)
    assert not list(tmp_path.rglob("*.citation.json"))


# REV-857 round-three probes


REV3_BAD = "https://reader@x.ai/pricing"


@pytest.mark.parametrize("hash_only", [False, True])
def test_fetch_sources_continues_after_malformed_redirect(tmp_path, hash_only):
    from scripts import price_reread

    class FakeFetcher:
        def __init__(self):
            self.calls = []

        def fetch(self, url, **kwargs):
            self.calls.append(url)
            return FetchResult(
                "ok", 200, body=b"<p>sample</p>",
                resolved_urls=(REV3_BAD,) if url.endswith("bad") else (),
                snapshot_ref="sha256:" + "5" * 64 if hash_only and url.endswith("bad") else None,
            )

    sources = {sid: Source(id=sid, url="https://example.org/" + sid) for sid in ("bad", "good")}
    fetcher = FakeFetcher()
    store = CopyStore(tmp_path / "cache")
    result = price_reread.fetch_sources(sources, sources, fetcher, store)
    assert result["good"].outcome == "ok"
    assert result["bad"].outcome == "invalid_citation_metadata"
    assert len(fetcher.calls) == 2
    assert not list(tmp_path.rglob("*.citation.json"))


@pytest.mark.parametrize("hash_only", [False, True])
def test_weekly_run_continues_after_malformed_fetch_redirect(estate, hash_only):
    from scripts import price_reread
    from tests.test_price_reread import API_URL, AT, PLANS_URL, ReplayFetcher, page
    from tests.test_price_reread import TODAY as REREAD_TODAY

    root, store = estate

    class BadFirst(ReplayFetcher):
        def fetch(self, url, **kwargs):
            result = super().fetch(url, **kwargs)
            return replace(result, resolved_urls=(REV3_BAD,),
                           snapshot_ref="sha256:" + "5" * 64 if hash_only else None) \
                if url == API_URL else result

    fetcher = BadFirst({API_URL: [page("api-pricing.html")], PLANS_URL: [page("plans.html")]})
    report = price_reread.run(root=root, fetcher=fetcher, store=store, today=REREAD_TODAY, at=AT)
    assert PLANS_URL in fetcher.fetched
    assert report.sources["example-plans"].outcome == "ok"
    assert report.sources["example-api-pricing"].outcome == "invalid_citation_metadata"


def _store_record(store, ref, data):
    import json

    path = store.path(ref).with_suffix(".citation.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))
    return path


@pytest.mark.parametrize("field,value", [
    ("url", REV3_BAD), ("sourceURL", REV3_BAD), ("final_url", REV3_BAD),
    ("sourceURL", 7), ("final_url", ""), ("sourceURL", "javascript:alert(1)"),
])
def test_all_store_origins_are_checked_before_verifier_cited_grant(tmp_path, field, value):
    from decision.citation import ref_state

    claim = make_claim()
    ref = claim.sources[0].snapshot_ref
    store = CopyStore(tmp_path / "cache")
    _store_record(store, ref, {"snapshot_ref": ref, "url": SOURCES["src-lab-docs"],
                               "resolved_urls": [], field: value})
    regions = StoredRegions(store, {"src-lab-docs": Source(id="src-lab-docs",
                                                           url=SOURCES["src-lab-docs"])})
    with pytest.raises(ValueError):
        ref_state({"source_id": "src-lab-docs", "snapshot_ref": ref},
                  {"src-lab-docs": SOURCES["src-lab-docs"]}, store)
    assert regions.cite_only_status("src-lab-docs", ref) is None
    assert regions.cite_only("src-lab-docs", ref) is True  # restrictive: copy withheld
    assert verify(claim, regions, [], today=TODAY).outcome == "skipped"


def test_well_formed_store_record_still_grants_the_verifier_cited_skip(tmp_path):
    claim = make_claim()
    ref = claim.sources[0].snapshot_ref
    store = CopyStore(tmp_path / "cache")
    store.record_citation(ref, source_url=SOURCES["src-lab-docs"], resolved_urls=[CITE_URL])
    regions = StoredRegions(store, {"src-lab-docs": Source(id="src-lab-docs",
                                                           url=SOURCES["src-lab-docs"])})
    assert regions.cite_only_status("src-lab-docs", ref) is True
    assert verify(claim, regions, [], today=TODAY).outcome == "cited"


@pytest.mark.parametrize("field", ["url", "sourceURL", "final_url"])
def test_recheck_refuses_malformed_prior_record_origins(tmp_path, field):
    import json

    now = datetime(2026, 10, 20, tzinfo=UTC)
    source = Source(id="ordinary", url="https://ordinary.example/pricing")
    store = CopyStore(tmp_path / "cache")

    class Fresh:
        def fetch(self, url, **kwargs):
            return FetchResult("ok", 200, body=b"<p>sample</p>")

    initial = recheck([source], {}, [], fetcher=Fresh(), store=store, now=now)
    snapshot = initial.states[source.id].snapshot
    assert snapshot is not None
    data = {"snapshot_ref": snapshot.copy_ref, "url": str(source.url), "resolved_urls": [],
            field: REV3_BAD}
    path = _store_record(store, snapshot.copy_ref, data)

    class NotModified:
        def fetch(self, url, **kwargs):
            return FetchResult("not_modified", 304)

    result = recheck([source], initial.states, [], fetcher=NotModified(), store=store, now=now)
    assert ("ordinary", "invalid_citation_metadata") in {
        (item.source_id, item.reason) for item in result.skipped}
    assert json.loads(path.read_text()) == data


@pytest.mark.parametrize("record,expected", [
    ({"url": "https://example.org/"}, False),
    ({"url": "https://example.org/", "resolved_urls": ["https://x.ai/"]}, True),
    ({"url": "https://example.org/", "final_url": "https://docs.x.ai/"}, True),
    ({"url": "https://example.org/", "sourceURL": REV3_BAD}, None),
    ({"url": "https://example.org/", "final_url": None}, None),
    ({"url": "https://example.org/", "resolved_urls": None}, None),
    ({}, None),
    ([], None),
])
def test_record_origin_status_checks_every_origin(record, expected):
    from decision.retention import record_origin_status

    assert record_origin_status(record) is expected


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


@pytest.mark.parametrize("redirect", ["https://example.org:bad/", "https://reader@x.ai/"])
def test_store_put_bad_redirect_keeps_nothing(tmp_path, redirect):
    """Granting: a citation record could later admit a fact, so a bad origin writes none."""
    store = CopyStore(tmp_path / "cache")
    with pytest.raises(ValueError):
        store.put(b"private content", source_url="https://example.org/",
                  resolved_urls=[redirect])
    assert not list(tmp_path.rglob("*"))


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


@pytest.mark.parametrize("origins,expected", [
    (("https://example.org/", ()), False),
    (("https://example.org/", ("https://x.ai/",)), True),
    (("https://x.ai/", ("https://reader@example.org/",)), None),
    (("https://example.org:bad/", ("https://x.ai/",)), None),
])
def test_origin_status_refuses_any_malformed_origin(origins, expected):
    assert cite_only_origin_status(*origins) is expected


# Admission drafter (#861) and fallback


@pytest.mark.parametrize("url", ["https://docs.x.ai:bad/x", "https://docs.x.ai:99999/x",
                                 "https://reader@docs.x.ai/x", "http://["])
def test_admission_source_block_refuses_malformed_urls_without_raising(url):
    from scripts import admission_drafter as drafter

    assert drafter.source_block(url, "xai", {}) is not None


def _xai_draft(tmp_path, monkeypatch, redirect, *, bypass_block):
    from scripts import admission_drafter as drafter
    from tests.test_admission_drafter import MODEL, TODAY as DRAFT_TODAY, catalogue, small_registry

    root = catalogue(tmp_path)
    model_id = "xai/fixture-model"
    model_url = "https://docs.x.ai/docs/models/fixture-model"
    card = yaml.safe_load((root / "models" / f"{MODEL}.md").read_text().split("---")[1])
    card.update(model_id=model_id, sources={"provider_docs_url": model_url})
    path = root / "models" / f"{model_id}.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text("---\n" + yaml.safe_dump(card) + "---\n")
    if bypass_block:
        # Isolate the granting check itself: the host gate is tested above.
        monkeypatch.setattr(drafter, "source_block", lambda *args: None)

    class Fetch:
        def fetch(self, url):
            if url != model_url:
                return FetchResult("unreachable", 404)
            return FetchResult("ok", 200, body=b"", snapshot_ref="sha256:" + "6" * 64,
                               retrieved_at=datetime(2026, 10, 20, 12, tzinfo=UTC),
                               resolved_urls=(redirect,))

    store = CopyStore(tmp_path / "copies")
    packet = drafter.draft_packet(root=root, model_id=model_id, fetcher=Fetch(), store=store,
                                  today=DRAFT_TODAY, registry=small_registry())
    return packet, store


@pytest.mark.parametrize("bypass_block", [False, True])
@pytest.mark.parametrize("redirect", ["https://reader@docs.x.ai/docs/models/fixture-model",
                                      "https://docs.x.ai:99999/docs/models/fixture-model"])
def test_admission_draft_never_cites_a_malformed_origin(tmp_path, monkeypatch, redirect,
                                                        bypass_block):
    """Granting: a "cited" source writes a citation record, so a malformed origin is refused."""
    packet, store = _xai_draft(tmp_path, monkeypatch, redirect, bypass_block=bypass_block)
    assert not [s for s in packet.sources if s["outcome"] == "cited"]
    assert any(s["outcome"] == "blocked" for s in packet.sources)
    assert not list((tmp_path / "copies").rglob("*.citation.json"))
    if bypass_block:
        assert any(s.get("reason") == "malformed source or redirect URL" for s in packet.sources)


def test_admission_draft_still_cites_a_well_formed_cite_only_origin(tmp_path, monkeypatch):
    packet, store = _xai_draft(tmp_path, monkeypatch,
                               "https://docs.x.ai/docs/models/fixture-model", bypass_block=False)
    [source] = [s for s in packet.sources if s["outcome"] == "cited"]
    assert store.citation(source["snapshot_ref"]) is not None


@pytest.mark.parametrize("redirect", ["https://reader@docs.x.ai/x", "https://docs.x.ai:99999/x"])
def test_admission_fallback_withholds_bytes_for_a_malformed_origin(redirect):
    """Restrictive: the fallback drops bytes; the drafter then refuses to cite (above)."""
    from scripts.admission_fallback import _without_restricted_bytes

    result = _without_restricted_bytes(
        "https://docs.example.com/models",
        FetchResult("ok", 200, body=b"page bytes", resolved_urls=(redirect,)))
    assert result.body == b"" and result.snapshot_ref is not None


# REV-857 round-four probes: an existing citation record for the fetched hash


def _current_record(store, ref, url, field):
    import json

    record = {"snapshot_ref": ref, "url": url, "resolved_urls": []}
    record[field] = [REV3_BAD] if field == "resolved_urls" else REV3_BAD
    path = store.path(ref).with_suffix(".citation.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record))
    return path, record


@pytest.mark.parametrize("field", ["url", "sourceURL", "final_url", "resolved_urls"])
def test_existing_current_citation_is_validated_before_fetch_grant(tmp_path, field):
    import json

    from decision.sources import fingerprint_bytes
    from scripts import price_reread

    body = b"<p>current page</p>"
    ref = fingerprint_bytes(body)
    store = CopyStore(tmp_path / "cache")
    path, record = _current_record(store, ref, "https://example.org/bad", field)

    class Fake:
        def fetch(self, url, **kwargs):
            return FetchResult("ok", 200, body=body if url.endswith("/bad") else b"healthy")

    sources = {sid: Source(id=sid, url="https://example.org/" + sid) for sid in ["bad", "good"]}
    result = price_reread.fetch_sources(sources, sources, Fake(), store)
    assert result["good"].outcome == "ok"
    assert json.loads(path.read_text()) == record  # untouched
    assert not store.path(ref).exists()  # bytes still withheld
    assert (result["bad"].outcome, result["bad"].copy_ref) == ("invalid_citation_metadata", None)


@pytest.mark.parametrize("field", ["url", "sourceURL", "final_url", "resolved_urls"])
def test_byte_free_fetch_never_overwrites_a_malformed_record(tmp_path, field):
    import json

    from scripts import price_reread

    ref = "sha256:" + "7" * 64
    store = CopyStore(tmp_path / "cache")
    path, record = _current_record(store, ref, "https://x.ai/pricing", field)

    class HashOnly:
        def fetch(self, url, **kwargs):
            return FetchResult("ok", 200, body=b"", snapshot_ref=ref)

    sources = {"s": Source(id="s", url="https://x.ai/pricing")}
    result = price_reread.fetch_sources(sources, sources, HashOnly(), store)
    assert (result["s"].outcome, result["s"].copy_ref) == ("invalid_citation_metadata", None)
    assert json.loads(path.read_text()) == record


def test_valid_existing_citation_record_still_gives_cited(tmp_path):
    from decision.sources import fingerprint_bytes
    from scripts import price_reread

    body = b"<p>current page</p>"
    ref = fingerprint_bytes(body)
    store = CopyStore(tmp_path / "cache")
    store.record_citation(ref, source_url="https://example.org/s", resolved_urls=[CITE_URL])

    class Fake:
        def fetch(self, url, **kwargs):
            return FetchResult("ok", 200, body=body)

    sources = {"s": Source(id="s", url="https://example.org/s")}
    result = price_reread.fetch_sources(sources, sources, Fake(), store)
    assert (result["s"].outcome, result["s"].copy_ref) == ("cited", ref)
    assert not store.path(ref).exists()


@pytest.mark.parametrize("field", ["url", "sourceURL", "final_url", "resolved_urls"])
def test_weekly_run_refuses_existing_malformed_current_citation(estate, field):
    from decision.sources import fingerprint_bytes
    from scripts import price_reread
    from tests.test_price_reread import API_URL, AT, PLANS_URL, ReplayFetcher, page
    from tests.test_price_reread import TODAY as REREAD_TODAY

    root, store = estate
    _current_record(store, fingerprint_bytes(page("api-pricing.html")), API_URL, field)
    fetcher = ReplayFetcher({API_URL: [page("api-pricing.html")], PLANS_URL: [page("plans.html")]})
    report = price_reread.run(root=root, fetcher=fetcher, store=store, today=REREAD_TODAY, at=AT)
    assert report.sources["example-plans"].outcome == "ok"
    assert report.sources["example-api-pricing"].outcome == "invalid_citation_metadata"
    cited = [(f.fact_id, f.status.value) for f in report.facts
             if f.status is price_reread.Status.CITED]
    assert not cited, cited
    # MODEL-423 (#863): no report row carries a citation for the refused source.
    assert not [row for rows in report.to_dict().values() if isinstance(rows, list)
                for row in rows if isinstance(row, dict)
                and "example-api-pricing" in (row.get("citations") or {})]


def test_weekly_write_does_not_record_cited_for_malformed_current_record(estate):
    import json

    from decision.sources import fingerprint_bytes
    from decision.verify import Queue
    from scripts import price_reread
    from tests.test_price_reread import API_URL, AT, PLANS_URL, ReplayFetcher, page
    from tests.test_price_reread import TODAY as REREAD_TODAY

    root, store = estate
    path, record = _current_record(store, fingerprint_bytes(page("api-pricing.html")), API_URL,
                                   "sourceURL")
    queue = Queue(root / "verification")
    before = len(queue.path.read_text().splitlines())
    fetcher = ReplayFetcher({API_URL: [page("api-pricing.html")], PLANS_URL: [page("plans.html")]})
    report = price_reread.run(root=root, fetcher=fetcher, store=store, today=REREAD_TODAY, at=AT,
                              write=True)
    assert json.loads(path.read_text()) == record
    assert not [f for f in report.facts if f.status is price_reread.Status.CITED]
    events = [json.loads(line) for line in queue.path.read_text().splitlines()[before:]]
    cited = [event for event in events
             if event.get("event") == "checked" and event.get("outcome") == "cited"]
    assert not cited, cited


def test_valid_cited_record_still_appears_in_report_citations(estate):
    """MODEL-423 (#863) control: a well-formed cite-only record is still written to citations."""
    from scripts import price_reread
    from tests.test_price_reread import API_URL, AT, PLANS_URL, ReplayFetcher, page
    from tests.test_price_reread import TODAY as REREAD_TODAY

    root, store = estate
    registry = root / "registry/sources.yaml"
    registry.write_text(registry.read_text().replace(PLANS_URL, "https://x.ai/pricing"))
    fetcher = ReplayFetcher({API_URL: [page("api-pricing.html")],
                             "https://x.ai/pricing": [page("plans.html")]})
    report = price_reread.run(root=root, fetcher=fetcher, store=store, today=REREAD_TODAY, at=AT)
    assert report.sources["example-plans"].outcome == "cited"
    rows = [row for row in report.to_dict()["cited"] if row.get("citations")]
    assert rows and all(set(row["citations"]) == {"example-plans"} for row in rows)
