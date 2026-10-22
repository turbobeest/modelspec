"""Admission packets use real source readers and the premier completeness gate."""

import json
from copy import deepcopy
from datetime import UTC, date, datetime

import httpx
import pytest
import yaml

from decision.registry import Registry, default
from decision.sources import CopyStore

TODAY = date(2026, 10, 20)
MODEL = "google/fixture-model"
MODEL_URL = "https://ai.google.dev/gemini-api/docs/models/fixture-model"
PRICE_URL = "https://ai.google.dev/gemini-api/docs/pricing"


def catalogue(tmp_path):
    root = tmp_path / "data"
    card = root / "models" / f"{MODEL}.md"
    card.parent.mkdir(parents=True)
    card.write_text("---\n" + yaml.safe_dump({
        "model_id": MODEL,
        "display_name": "Fixture Model",
        "version": "fixture-model",
        "status": "active",
        "sources": {"provider_docs_url": MODEL_URL},
        # Card values are deliberately wrong; only source readings may become facts.
        "modalities": {"text": {"context_window": 999}},
        "cost": {"input": 999, "output": 999},
        "benchmarks": {"scores": {"gpqa_diamond": 99}, "evidence": []},
    }) + "---\nFixture release.\n")
    (root / "premier").mkdir()
    (root / "premier/slice-1.yaml").write_text(
        "schema_version: 1\nmodels:\n- model_id: openai/existing\n"
    )
    (root / "registry").mkdir()
    (root / "registry/source-terms.json").write_text(json.dumps({
        "ai.google.dev": "restricts",
        "developers.openai.com": "forbids",
        "claude.com": "forbids",
        "platform.claude.com": "unclear",
        "docs.x.ai": "forbids",
    }))
    return root


def small_registry(*extra):
    real = default()
    ids = (
        "model.context_window", "offering.provider", "offering.region", "offering.tier",
        "offering.price.input", "offering.price.output", *extra,
    )
    return Registry(
        units={}, source_kinds={},
        facets={key: real.facet(key) for key in ids},
        providers={}, harnesses={}, domains={},
        named_lists={"registry:providers": lambda: frozenset(p.id for p in real.providers()),
                     "model_classes": lambda: frozenset({"text-generator"}),
                     "iso_3166_1_alpha_2": None},
    )


def pages(model="<h1>Fixture Model</h1><p>Context window</p><p>32K tokens</p>"):
    return {
        MODEL_URL: model,
        PRICE_URL: (
            "<table><tr><th>Model</th><th>Input price per 1M tokens</th>"
            "<th>Output price per 1M tokens</th></tr>"
            "<tr><td>Fixture Model</td><td>$2</td><td>$8</td></tr></table>"
        ),
    }


def draft(tmp_path, root, bodies, registry, model_id=MODEL):
    from scripts.admission_drafter import AdmissionFetcher, draft_packet, load_source_terms

    def request(req):
        text = bodies.get(str(req.url))
        return httpx.Response(404 if text is None else 200, text=text or "",
                              headers={"content-type": "text/html"})

    with httpx.Client(transport=httpx.MockTransport(request)) as client:
        return draft_packet(
            root=root, model_id=model_id,
            fetcher=AdmissionFetcher(client, lab=model_id.split("/")[0],
                                     terms=load_source_terms(root), retries=0, min_host_interval=0),
            store=CopyStore(tmp_path / "copies"), today=TODAY, registry=registry,
        )


def test_partial_packet_lists_gate_gaps_and_keeps_offering_out_of_catalogue(tmp_path):
    root = catalogue(tmp_path)
    before = (root / "models" / f"{MODEL}.md").read_text()
    packet = draft(tmp_path, root, pages(), small_registry("feature.streaming"))
    assert (root / "models" / f"{MODEL}.md").read_text() == before
    assert packet.ready is False
    assert [(g.subject, g.facet) for g in packet.gaps] == [(MODEL, "feature.streaming")]
    assert {f["facet"]: f["value"] for f in packet.model_facts} == {
        "model.context_window": 32000,
    }
    assert {f["facet"]: f["value"] for f in packet.offering["facts"]} == {
        "offering.price.input": 2, "offering.price.output": 8,
    }
    assert packet.benchmarks == []
    packet.write(root)
    assert not list((root / "offerings").rglob("*.yaml"))
    assert MODEL not in (root / "premier/slice-1.yaml").read_text()
    assert "feature.streaming" in packet.markdown()
    assert (root / "verification/log.jsonl").exists()


def test_complete_packet_writes_lineup_and_offering_together_and_repeats_safely(tmp_path):
    from decision.excluded import excluded_sources
    from decision.model import load_offerings
    from decision.snapshot import audit_build, collect_repo

    root = catalogue(tmp_path)
    packet = draft(tmp_path, root, pages(), small_registry())
    assert packet.ready
    packet.write(root)
    lineup = yaml.safe_load((root / "premier/slice-1.yaml").read_text())
    assert lineup["models"] == [
        {"model_id": "openai/existing"}, {"model_id": MODEL},
    ]
    offerings = list((root / "offerings").rglob("*.yaml"))
    assert len(offerings) == 1
    assert yaml.safe_load(offerings[0].read_text())[0]["facts"][0]["value"] == 2
    assert load_offerings(offerings[0])[0].model == MODEL
    assert audit_build(collect_repo(root), registry=small_registry(), premier=[MODEL],
                       as_of=TODAY, guard=excluded_sources()).gaps == ()
    before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    packet.write(root)
    assert {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()} == before


def test_absent_price_page_is_an_offering_gap_even_with_complete_model_facts(tmp_path):
    root = catalogue(tmp_path)
    packet = draft(tmp_path, root, {MODEL_URL: pages()[MODEL_URL]}, small_registry())
    assert not packet.ready
    assert {g.facet for g in packet.gaps} == {"offering.price.input", "offering.price.output"}
    assert not packet.offering["facts"]


def test_held_cite_only_source_never_stores_or_admits_even_existing_fact(tmp_path):
    from decision.model import Source
    from decision.sources import fingerprint_bytes

    root = catalogue(tmp_path)
    old = root / "models" / f"{MODEL}.md"
    card = yaml.safe_load(old.read_text().split("---")[1])
    card.update(model_id="xai/fixture-model", sources={
        "provider_docs_url": "https://docs.x.ai/docs/models/fixture-model",
    })
    secret_page = "<h1>Fixture Model</h1><p>Context window</p><p>32K tokens</p>"
    source = Source(id="xai-fixture", url=card["sources"]["provider_docs_url"],
                    kind="lab_documentation",
                    cited_regions=[{"id": "page", "locator": {"kind": "page"}}])
    card["facts"] = [{
        "facet": "model.context_window", "state": "known", "value": 32000,
        "sources": [{"source_id": source.id,
                     "snapshot_ref": fingerprint_bytes(secret_page.encode()),
                     "cited_regions": ["page"], "retrieved_at": "2026-10-20T00:00:00Z"}],
    }]
    path = root / "models/xai/fixture-model.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text("---\n" + yaml.safe_dump(card) + "---\n")
    (root / "registry").mkdir(exist_ok=True)
    (root / "registry/sources.yaml").write_text(yaml.safe_dump({
        "schema_version": 1, "sources": [source.model_dump(mode="json")],
    }))
    packet = draft(tmp_path, root, {str(source.url): secret_page}, small_registry(),
                   model_id="xai/fixture-model")
    assert not packet.ready
    assert any(g.facet == "model.context_window" and "cite-only" in g.reason for g in packet.gaps)
    assert packet.model_facts == []
    cache_files = [p for p in (tmp_path / "copies").rglob("*") if p.is_file()]
    assert cache_files == []
    assert all(source["outcome"] == "cited" for source in packet.sources)
    assert all("not fetched" in source["reason"] for source in packet.sources)
    assert all("snapshot_ref" not in source and "retrieved_at" not in source
               for source in packet.sources)


def test_unregistered_restricted_and_third_party_sources_block_before_fetch(
    tmp_path, monkeypatch
):
    from scripts import admission_drafter as drafter

    root = catalogue(tmp_path)
    monkeypatch.setattr(drafter, "cite_only_hosts", lambda: ())
    assert drafter.source_block("https://docs.x.ai/x", "xai", {}) == "source-terms hold (MODEL-409)"
    for url in ("https://artificial" "analysis.ai/model", "https://zap" "ier.com/x",
                "https://openai.com.evil.example/model", "https://example.com/model"):
        assert drafter.source_block(url, "openai", {}) is not None
    calls = []

    class Fetch:
        def fetch(self, url):
            calls.append(url)
            raise AssertionError("blocked source was fetched")

    monkeypatch.setattr(drafter, "source_candidates", lambda *args: [
        drafter.Source(id="untrusted", url="https://example.com/model",
                       cited_regions=[{"id": "page", "locator": {"kind": "page"}}]),
    ])
    packet = drafter.draft_packet(root=root, model_id=MODEL, fetcher=Fetch(),
                                  store=CopyStore(tmp_path / "cache"), today=TODAY,
                                  registry=small_registry())
    assert not calls
    assert packet.sources[0]["outcome"] == "blocked"


def test_redirect_to_third_party_is_not_retained_or_read(tmp_path):
    from decision.sources import FetchResult
    from scripts.admission_drafter import draft_packet

    root = catalogue(tmp_path)

    class Fetch:
        def fetch(self, url):
            return FetchResult("ok", 200, body=pages()[MODEL_URL].encode(),
                               resolved_urls=("https://example.com/stolen",))

    packet = draft_packet(root=root, model_id=MODEL, fetcher=Fetch(),
                          store=CopyStore(tmp_path / "cache"), today=TODAY,
                          registry=small_registry())
    assert not packet.model_facts
    assert all(s["outcome"] == "blocked" for s in packet.sources)
    assert not (tmp_path / "cache").exists()


def test_conflicting_source_readings_stay_gaps_and_preserve_existing_facts(tmp_path):
    root = catalogue(tmp_path)
    bodies = pages("<h1>Fixture Model</h1><p>Context window</p><p>32K tokens</p>"
                   "<p>Context window</p><p>64K tokens</p>")
    packet = draft(tmp_path, root, bodies, small_registry())
    assert not packet.ready
    assert not packet.model_facts
    assert any("conflicting" in g.reason for g in packet.gaps)


@pytest.mark.parametrize("model", ["../other", "openai/../other", "/tmp/data", "x/y/z"])
def test_invalid_model_id_is_rejected(tmp_path, model):
    from scripts.admission_drafter import draft_packet

    with pytest.raises(ValueError, match="catalogue ID"):
        draft_packet(root=tmp_path, model_id=model, fetcher=None,
                     store=CopyStore(tmp_path), today=TODAY)


@pytest.mark.parametrize("provenance", ["source_url", "redirect"])
def test_existing_verified_fact_requires_first_party_provenance(tmp_path, provenance):
    root = catalogue(tmp_path)
    first = draft(tmp_path, root, pages(), small_registry())
    first.write(root)
    if provenance == "source_url":
        path = root / "registry/sources.yaml"
        document = yaml.safe_load(path.read_text())
        for index, source in enumerate(document["sources"]):
            source["url"] = f"https://third-party.example/source/{index}"
        path.write_text(yaml.safe_dump(document))
    else:
        path = root / "models" / f"{MODEL}.md"
        card = yaml.safe_load(path.read_text().split("---")[1])
        for fact in card["facts"]:
            for reference in fact["sources"]:
                reference["resolved_urls"] = ["https://third-party.example/redirect"]
        path.write_text("---\n" + yaml.safe_dump(card) + "---\n")
    packet = draft(tmp_path, root, {}, small_registry())
    assert not packet.ready
    assert packet.to_dict()["lineup_entry"] is None
    assert any(
        gap.subject == MODEL and gap.facet == "model.context_window"
        and "first-party" in gap.reason
        for gap in packet.gaps
    )


def test_existing_offering_without_id_and_sibling_offering_are_preserved(tmp_path):
    from decision.model import load_offerings
    from decision.verify import VerificationLog

    root = catalogue(tmp_path)
    first = draft(tmp_path, root, pages(), small_registry())
    first.write(root)
    path = root / "offerings/google-gemini-api/google/fixture-model.yaml"
    [standard] = yaml.safe_load(path.read_text())
    standard.pop("id", None)
    enterprise = deepcopy(standard)
    enterprise["tier"] = "enterprise"
    enterprise_id = f"google-gemini-api/{MODEL}/global/enterprise"
    for fact in enterprise["facts"]:
        fact["id"] = f"{enterprise_id}#{fact['facet']}"
        fact["subject"]["id"] = enterprise_id
    log = VerificationLog(root / "verification")
    for claim, result in first.checks:
        if claim.subject == MODEL:
            continue
        verification = result.verification
        log.append(verification.model_copy(update={
            "target": verification.target.model_copy(update={
                "id": f"{enterprise_id}#{claim.field}",
            }),
        }))
    path.write_text(yaml.safe_dump([standard, enterprise], sort_keys=False))
    packet = draft(tmp_path, root, pages(), small_registry())
    assert packet.ready
    packet.write(root)
    saved = yaml.safe_load(path.read_text())
    assert len(saved) == 2
    assert next(row for row in saved if row["tier"] == "enterprise") == enterprise
    assert len([row for row in saved if row["tier"] == "standard"]) == 1
    assert {offering.tier for offering in load_offerings(path)} == {"standard", "enterprise"}


def test_google_release_uses_registered_lab_api_provider(tmp_path):
    from decision.model import load_offerings

    root = catalogue(tmp_path)
    model_id = "google/fixture-model"
    model_url = "https://ai.google.dev/gemini-api/docs/models/fixture-model"
    price_url = "https://ai.google.dev/gemini-api/docs/pricing"
    original = root / "models" / f"{MODEL}.md"
    card = yaml.safe_load(original.read_text().split("---")[1])
    card.update(model_id=model_id, sources={"provider_docs_url": model_url})
    path = root / "models" / f"{model_id}.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text("---\n" + yaml.safe_dump(card) + "---\n")
    packet = draft(
        tmp_path, root,
        {model_url: pages()[MODEL_URL], price_url: pages()[PRICE_URL]},
        small_registry(), model_id=model_id,
    )
    assert packet.ready
    assert packet.offering["provider"] == "google-gemini-api"
    assert packet.offering["id"] == f"google-gemini-api/{model_id}/global/standard"
    packet.write(root)
    offerings = load_offerings(root / "offerings/google-gemini-api/google/fixture-model.yaml")
    assert len(offerings) == 1 and offerings[0].provider == "google-gemini-api"


def test_cite_only_fallback_keeps_original_fingerprint(tmp_path):
    from decision.sources import FetchResult, fingerprint_bytes
    from scripts.admission_drafter import draft_packet

    root = catalogue(tmp_path)
    (root / "registry/source-terms.json").write_text(json.dumps({"docs.x.ai": "permits"}))
    model_id = "xai/fixture-model"
    model_url = "https://docs.x.ai/docs/models/fixture-model"
    original = root / "models" / f"{MODEL}.md"
    card = yaml.safe_load(original.read_text().split("---")[1])
    card.update(model_id=model_id, sources={"provider_docs_url": model_url})
    path = root / "models" / f"{model_id}.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text("---\n" + yaml.safe_dump(card) + "---\n")
    expected_ref = fingerprint_bytes(b"cite-only source bytes never retained")
    retrieved = datetime(2026, 10, 20, 12, tzinfo=UTC)

    class Fetch:
        def fetch(self, url):
            if url != model_url:
                return FetchResult("unreachable", 404)
            return FetchResult(
                "ok", 200, body=b"", snapshot_ref=expected_ref,
                retrieved_at=retrieved, resolved_urls=(model_url,),
            )

    store = CopyStore(tmp_path / "copies")
    packet = draft_packet(
        root=root, model_id=model_id, fetcher=Fetch(), store=store,
        today=TODAY, registry=small_registry(),
    )
    assert not packet.ready and packet.model_facts == []
    [source] = [source for source in packet.sources if source["outcome"] == "cited"]
    assert source["snapshot_ref"] == expected_ref
    assert store.citation(expected_ref)["retrieved_at"] == retrieved.isoformat()
    assert not store.has(expected_ref)
    assert not store.path(fingerprint_bytes(b"")).with_suffix(".citation.json").exists()


def test_write_requires_persistent_cache_before_any_fetch(tmp_path, monkeypatch, capsys):
    from scripts import admission_drafter as drafter

    monkeypatch.delenv("MODELSPEC_SOURCE_CACHE", raising=False)

    def never_fetch(*args, **kwargs):
        raise AssertionError("write attempted a fetch before validating retained provenance")

    monkeypatch.setattr(drafter, "Fetcher", never_fetch)
    with pytest.raises(SystemExit) as error:
        drafter.main(["--data-dir", str(tmp_path), "--model", MODEL, "--write"])
    assert error.value.code == 2
    assert "--write requires --cache-dir" in capsys.readouterr().err


def test_retired_release_cannot_enter_lineup(tmp_path):
    root = catalogue(tmp_path)
    path = root / "models" / f"{MODEL}.md"
    card = yaml.safe_load(path.read_text().split("---")[1])
    card["lifecycle"] = "retired"
    path.write_text("---\n" + yaml.safe_dump(card) + "---\n")
    packet = draft(tmp_path, root, pages(), small_registry())
    assert not packet.ready and packet.to_dict()["lineup_entry"] is None
    assert any(
        gap.facet == "model.lifecycle" and "retired" in gap.reason for gap in packet.gaps
    )


def test_untyped_historical_price_sources_do_not_hide_new_raw_page_reading(tmp_path):
    from decision.model import Source

    root = catalogue(tmp_path)
    path = root / "registry/sources.yaml"
    path.parent.mkdir(exist_ok=True)
    sources = [
        Source(
            id=f"historical-{normaliser}", url=PRICE_URL, normaliser=normaliser,
            cited_regions=[{"id": "page", "locator": {"kind": "page"}}],
        )
        for normaliser in ("html-default", "text-default")
    ]
    path.write_text(yaml.safe_dump({
        "schema_version": 1,
        "sources": [source.model_dump(mode="json") for source in sources],
    }))
    packet = draft(tmp_path, root, pages(), small_registry())
    assert packet.ready
    assert {fact["facet"]: fact["value"] for fact in packet.offering["facts"]} == {
        "offering.price.input": 2, "offering.price.output": 8,
    }


def test_catalogue_benchmarks_keep_first_party_records_without_promoting_legacy_scores(tmp_path):
    root = catalogue(tmp_path)
    path = root / "models" / f"{MODEL}.md"
    card = yaml.safe_load(path.read_text().split("---")[1])
    evidence = [
        {"benchmark_id": "gpqa_diamond", "score": 74.2,
         "source_url": "https://ai.google.dev/gemini-api/docs/fixture-model/"},
        {"benchmark_id": "terminal_bench", "score": 55.0,
         "source_url": "https://anthropic.com/competitor-comparison"},
        {"benchmark_id": "aa_intelligence_index", "score": 80.0,
         "source_url": "https://artificial" "analysis.ai/leaderboards"},
    ]
    card["benchmarks"] = {
        "evidence": evidence,
        "scores": {"mmlu_pro": 88.0},
        "benchmark_source": "https://ai.google.dev/gemini-api/docs/fixture-model/",
    }
    path.write_text("---\n" + yaml.safe_dump(card) + "---\n")
    packet = draft(tmp_path, root, pages(), small_registry())
    assert {row["benchmark_id"] for row in packet.benchmarks} == {"gpqa_diamond", "mmlu_pro"}
    assert next(row for row in packet.benchmarks if row["benchmark_id"] == "gpqa_diamond") \
        == evidence[0]
    legacy = next(row for row in packet.benchmarks if row["benchmark_id"] == "mmlu_pro")
    assert legacy["score"] == 88.0
    assert legacy["source_url"] == "https://ai.google.dev/gemini-api/docs/fixture-model/"
    assert legacy["status"] == "catalogue_only" and legacy["verified"] is False
    packet.write(root)
    saved = yaml.safe_load(path.read_text().split("---")[1])
    assert saved["benchmarks"] == card["benchmarks"]


def test_write_does_not_persist_snapshot_generated_identifier_candidates(tmp_path):
    from decision.model import load_offerings

    root = catalogue(tmp_path)
    draft(tmp_path, root, pages(), small_registry()).write(root)
    card_path = root / "models" / f"{MODEL}.md"
    card = yaml.safe_load(card_path.read_text().split("---")[1])
    card["availability"] = {"primary_provider": {
        "name": "Google", "model_id_on_platform": "fixture-model",
    }}
    card_path.write_text("---\n" + yaml.safe_dump(card) + "---\n")
    packet = draft(tmp_path, root, pages(), small_registry("offering.api_model_id"))
    assert packet.ready
    assert "offering.api_model_id" not in {f["facet"] for f in packet.offering["facts"]}
    packet.write(root)
    assert len(load_offerings(root / "offerings/google-gemini-api/google/fixture-model.yaml")) == 1


def test_existing_dated_price_schedule_is_preserved_by_an_undated_page(tmp_path):
    from copy import deepcopy

    from decision.model import load_offerings

    root = catalogue(tmp_path)
    draft(tmp_path, root, pages(), small_registry()).write(root)
    path = root / "offerings/google-gemini-api/google/fixture-model.yaml"
    rows = yaml.safe_load(path.read_text())
    price = next(f for f in rows[0]["facts"] if f["facet"] == "offering.price.input")
    price.update(effective_from="2026-10-01", effective_until="2026-10-31")
    future = deepcopy(price)
    future.update(id=price["id"] + "-future", value=4,
                  effective_from="2026-11-01", effective_until=None)
    rows[0]["facts"].append(future)
    path.write_text(yaml.safe_dump(rows))
    expected = [price, future]
    # The old undated verification cannot verify this new schedule.
    packet = draft(tmp_path, root, pages(), small_registry())
    assert not packet.ready
    assert [f for f in packet.offering["facts"] if f["facet"] == "offering.price.input"] \
        == expected
    before = path.read_bytes()
    packet.write(root)
    assert path.read_bytes() == before
    assert len(load_offerings(path)[0].facts) == 3


def test_lineup_entry_carries_verified_class_and_review_clause(tmp_path):
    root = catalogue(tmp_path)
    packet = draft(tmp_path, root, pages(), small_registry("model.class"))
    assert packet.ready
    entry = packet.to_dict()["lineup_entry"]
    assert entry["class"] == "text-generator"
    assert entry["clauses"] == [{"clause": 4, "reason": "Admission packet for human review"}]
    packet.write(root)
    assert yaml.safe_load((root / "premier/slice-1.yaml").read_text())["models"][-1] == entry


@pytest.mark.parametrize(('host', 'lab', 'cited'), [
    ('developers.openai.com', 'openai', True),
    ('help.openai.com', 'openai', True),
    ('docs.x.ai', 'xai', True),
    ('claude.com', 'anthropic', False),
    ('platform.claude.com', 'anthropic', False),
    ('unlisted.openai.com', 'openai', False),
    ('sub.ai.google.dev', 'google', False),
])
def test_source_terms_hold_never_fetches_or_stores(tmp_path, monkeypatch, host, lab, cited):
    from decision.sources import FetchResult
    from scripts import admission_drafter as drafter

    root = catalogue(tmp_path)
    url = f'https://{host}/fixture-model'
    monkeypatch.setattr(drafter, 'source_candidates', lambda *args: [
        drafter.Source(id='held', url=url,
                       cited_regions=[{'id': 'page', 'locator': {'kind': 'page'}}]),
    ])
    # Keep ownership independent from the terms decision.
    monkeypatch.setitem(drafter.LAB_HOSTS, 'google', drafter.LAB_HOSTS[lab])
    calls = []

    class Fetch:
        def fetch(self, url):
            calls.append(url)
            return FetchResult('ok', 200, body=pages()[MODEL_URL].encode())

    packet = drafter.draft_packet(
        root=root, model_id=MODEL, fetcher=Fetch(), store=CopyStore(tmp_path / 'copies'),
        today=TODAY, registry=small_registry(),
    )
    assert calls == []
    assert not list((tmp_path / 'copies').rglob('*'))
    assert packet.model_facts == []
    outcome = 'cited' if cited else 'blocked'
    reason = 'source-terms hold (MODEL-409)'
    if cited:
        reason += '; cited, not machine-verified; not fetched'
    assert packet.sources == [{
        'url': url, 'source_id': 'held', 'outcome': outcome, 'reason': reason,
    }]
    assert f'{outcome}; {reason}' in packet.markdown()


@pytest.mark.parametrize(('host', 'lab'), [
    ('developers.openai.com', 'openai'),
    ('help.openai.com', 'openai'),
    ('docs.x.ai', 'xai'),
])
def test_cite_only_fetcher_still_enforces_source_terms(tmp_path, host, lab):
    from scripts.admission_drafter import AdmissionFetcher, SourceBlockedError

    calls = []

    def request(req):
        calls.append(str(req.url))
        return httpx.Response(200, text='held page bytes')

    with httpx.Client(transport=httpx.MockTransport(request)) as client:
        fetcher = AdmissionFetcher(client, lab=lab, terms={host: 'forbids'},
                                   retries=0, min_host_interval=0)
        with pytest.raises(SourceBlockedError, match='source-terms hold'):
            fetcher.fetch(f'https://{host}/model')
    assert calls == []


@pytest.mark.parametrize('policy', [None, {}, {'ai.google.dev': 'permits-ish'}])
def test_missing_or_unknown_terms_fail_closed(tmp_path, policy):
    root = catalogue(tmp_path)
    path = root / 'registry/source-terms.json'
    if policy is None:
        path.unlink()
    else:
        path.write_text(json.dumps(policy))
    packet = draft(tmp_path, root, pages(), small_registry())
    assert all(s['outcome'] == 'blocked' for s in packet.sources)
    assert not list((tmp_path / 'copies').rglob('*'))


def test_no_first_party_offering_is_an_explicit_gap(tmp_path, monkeypatch):
    from scripts import admission_drafter as drafter

    root = catalogue(tmp_path)
    monkeypatch.delitem(drafter.PRICE_URLS, 'google')
    packet = draft(tmp_path, root, pages(), small_registry())
    assert packet.offering is None
    assert not packet.ready
    assert [(g.subject, g.facet, g.reason) for g in packet.gaps] == [
        (MODEL, 'no_offering', 'no first-party offering in packet or data'),
    ]
    packet.write(root)
    assert MODEL not in (root / 'premier/slice-1.yaml').read_text()


@pytest.mark.parametrize('target', [
    'https://developers.openai.com/api/docs/model',
    'https://platform.claude.com/docs/model',
    'https://unlisted.openai.com/model',
])
def test_cli_blocks_redirect_before_target_request(tmp_path, monkeypatch, capsys, target):
    from scripts import admission_drafter as drafter

    root = catalogue(tmp_path)
    calls = []
    client_type = httpx.Client

    def request(req):
        calls.append(str(req.url))
        if str(req.url) in (MODEL_URL, PRICE_URL):
            return httpx.Response(302, headers={'location': target})
        return httpx.Response(200, text=pages()[MODEL_URL])

    monkeypatch.setattr(drafter.httpx, 'Client', lambda: client_type(
        transport=httpx.MockTransport(request)))
    monkeypatch.setitem(drafter.LAB_HOSTS, 'google', ('ai.google.dev', 'openai.com', 'claude.com'))
    report = tmp_path / 'packet.json'
    assert drafter.main([
        '--data-dir', str(root), '--model', MODEL, '--dry-run',
        '--report', str(report), '--cache-dir', str(tmp_path / 'cache'),
    ]) == 0
    assert target not in calls
    assert set(calls) == {MODEL_URL, PRICE_URL}
    packet = json.loads(report.read_text())
    assert all(s['outcome'] == 'blocked' and s['reason'] == 'source-terms hold (MODEL-409)'
               for s in packet['sources'])
    assert not list((tmp_path / 'cache').rglob('*'))


def test_cli_manifest_contains_only_source_metadata(tmp_path, monkeypatch, capsys):
    from scripts import admission_drafter as drafter

    root = catalogue(tmp_path)
    client_type = httpx.Client
    monkeypatch.setattr(drafter.httpx, 'Client', lambda: client_type(
        transport=httpx.MockTransport(lambda req: httpx.Response(
            200, text=pages()[str(req.url)], headers={'content-type': 'text/html'}))))
    manifest = tmp_path / 'manifest.json'
    report = tmp_path / 'packet.json'
    assert drafter.main([
        '--data-dir', str(root), '--model', MODEL, '--dry-run',
        '--report', str(report), '--manifest', str(manifest),
    ]) == 0
    sources = json.loads(manifest.read_text())['sources']
    assert sources == json.loads(report.read_text())['sources']
    assert len(sources) == 2
    for source in sources:
        assert set(source) == {
            'url', 'source_id', 'outcome', 'snapshot_ref', 'retrieved_at', 'resolved_urls',
        }
        assert source['outcome'] == 'fetched'
        assert source['snapshot_ref'].startswith('sha256:')
        assert datetime.fromisoformat(source['retrieved_at']).tzinfo is not None
    assert '32K tokens' not in manifest.read_text()
    assert '32K tokens' not in report.read_text()
