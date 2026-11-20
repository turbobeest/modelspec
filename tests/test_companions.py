"""A rendered re-read judges a fact on its companion sources too (MODEL-489). No network."""

from __future__ import annotations

from datetime import UTC, date, datetime

import httpx
import pytest

from decision.companions import (
    MISSING_COPY,
    claim_with_copies,
    companion_ids,
    fetch_companions,
    judge,
)
from decision.model import Source, SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore, Fetcher
from decision.verify import Claim, deterministic_extractors, verify

NOW = datetime(2026, 11, 19, 6, tzinfo=UTC)
TODAY = date(2026, 11, 19)
RENDERED_URL = "https://lab.example/terms/"
COMPANION_URL = "https://registry.example/filing/"
TERMS = {"lab.example": "permits", "registry.example": "unclear", "mirror.example": "restricts"}


def _source(sid: str, url: str, fetch: str) -> Source:
    return Source(id=sid, url=url, kind="official_registry", normaliser="html-default", fetch=fetch,
                  cited_regions=[{"id": "incorporation", "locator": {"kind": "page"}}])


SOURCES = {
    "lab-rendered": _source("lab-rendered", RENDERED_URL, "rendered"),
    "lab-companion": _source("lab-companion", COMPANION_URL, "http"),
}


def _claim() -> Claim:
    ref = lambda sid: SourceRef.model_validate(  # noqa: E731
        {"source_id": sid, "snapshot_ref": "sha256:" + "ab" * 32,
         "cited_regions": ["incorporation"]})
    return Claim(
        target=TargetRef(kind="fact", id="lab:acme#origin.lab_jurisdiction"),
        subject="lab:acme", names=("Acme LLC",), field="origin.lab_jurisdiction", value=["US"],
        collector=VerificationActor(agent="grok", model_family="grok", method="lab-registry@1"),
        sources=(ref("lab-rendered"), ref("lab-companion")))


class Regions:
    """Reads the text a copy ref names; the missing ref and unknown refs read as absent."""

    def __init__(self, texts: dict[str, str]) -> None:
        self.texts = texts

    def text(self, source_id: str, copy_ref: str, region_id: str) -> str | None:
        return self.texts.get(copy_ref)


def _fetcher(handler) -> Fetcher:
    return Fetcher(httpx.Client(transport=httpx.MockTransport(handler)), retries=0,
                   min_host_interval=0, sleep=lambda _s: None)


def _page(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, text="<html><body><p>Acme LLC, a Delaware limited liability company"
                                    "</p></body></html>", headers={"content-type": "text/html"})


def _judge(claim, copies, reads, regions):
    return judge(claim, copies=copies, reads=reads, verify_claim=lambda fresh: verify(
        fresh, regions, deterministic_extractors(), today=TODAY))


def test_companion_ids_are_the_non_rendered_sources_beside_an_attempted_one() -> None:
    assert companion_ids([_claim()], SOURCES, {"lab-rendered"}) == ["lab-companion"]
    assert companion_ids([_claim()], SOURCES, set()) == []
    assert companion_ids([_claim()], SOURCES, {"lab-rendered", "lab-companion"}) == []


def test_a_fact_with_a_rendered_and_a_plain_source_is_judged_on_both(tmp_path) -> None:
    store = CopyStore(tmp_path)
    reads = fetch_companions(["lab-companion"], SOURCES, fetcher=_fetcher(_page), store=store,
                             terms=TERMS, now=NOW)
    read = reads["lab-companion"]
    assert read.outcome == "ok" and store.has(read.copy)
    rendered = "sha256:" + "11" * 32
    text = "Acme LLC, a Delaware company"
    regions = Regions({rendered: text, read.copy: text})
    result = _judge(_claim(), {"lab-rendered": rendered}, reads, regions)
    assert result.outcome == "verified"
    seen = claim_with_copies(_claim(), {"lab-rendered": rendered}, reads)
    assert [r.snapshot_ref for r in seen.sources] == [rendered, read.copy]


def test_a_genuinely_unreachable_companion_still_yields_unreachable(tmp_path) -> None:
    store = CopyStore(tmp_path)
    reads = fetch_companions(["lab-companion"], SOURCES, store=store, terms=TERMS, now=NOW,
                             fetcher=_fetcher(lambda request: httpx.Response(404)))
    assert reads["lab-companion"].outcome == "unreachable"
    rendered = "sha256:" + "11" * 32
    result = _judge(_claim(), {"lab-rendered": rendered}, reads,
                    Regions({rendered: "Acme LLC, a Delaware company"}))
    assert result.outcome == "unreachable"
    assert "lab-companion" in result.reason


def test_a_failed_rendered_read_is_unreachable_not_verified(tmp_path) -> None:
    store = CopyStore(tmp_path)
    reads = fetch_companions(["lab-companion"], SOURCES, fetcher=_fetcher(_page), store=store,
                             terms=TERMS, now=NOW)
    regions = Regions({reads["lab-companion"].copy: "Acme LLC, a Delaware company"})
    result = _judge(_claim(), {"lab-rendered": None}, reads, regions)
    assert result.outcome == "unreachable"
    failed = claim_with_copies(_claim(), {"lab-rendered": None}, reads)
    assert failed.sources[0].snapshot_ref == MISSING_COPY


def test_a_source_never_read_is_not_reread_and_never_verifies() -> None:
    rendered = "sha256:" + "11" * 32
    result = _judge(_claim(), {"lab-rendered": rendered}, {}, Regions({rendered: "Delaware"}))
    assert result.outcome == "skipped"
    assert result.reason == "not_reread:lab-companion"


def test_a_redirect_to_an_unclassified_host_has_its_own_reason_and_keeps_nothing(tmp_path) -> None:
    sent: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(request.url.host)
        if request.url.host == "registry.example":
            return httpx.Response(302, headers={"location": "https://unknown.example/filing/"})
        return _page(request)

    store = CopyStore(tmp_path)
    reads = fetch_companions(["lab-companion"], SOURCES, fetcher=_fetcher(handler), store=store,
                             terms=TERMS, now=NOW)
    read = reads["lab-companion"]
    assert (read.outcome, read.host, read.copy) == (
        "redirect_unclassified", "unknown.example", None)
    assert sent == ["registry.example"]  # the unclassified host never received a request
    assert not list(tmp_path.rglob("*"))
    rendered = "sha256:" + "11" * 32
    result = _judge(_claim(), {"lab-rendered": rendered}, reads, Regions({rendered: "Delaware"}))
    assert result.outcome == "skipped"
    assert result.reason == "redirect_unclassified:lab-companion:unknown.example"


def test_a_redirect_to_a_classified_host_is_followed_and_recorded(tmp_path) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "registry.example":
            return httpx.Response(301, headers={"location": "https://mirror.example/filing/"})
        return _page(request)

    reads = fetch_companions(["lab-companion"], SOURCES, fetcher=_fetcher(handler),
                             store=CopyStore(tmp_path), terms=TERMS, now=NOW)
    assert reads["lab-companion"].outcome == "ok"
    assert "https://mirror.example/filing/" in reads["lab-companion"].resolved_urls


def test_a_cite_only_companion_keeps_a_citation_and_no_bytes(tmp_path) -> None:
    sources = {"lab-companion": _source("lab-companion", "https://x.ai/legal/", "http")}
    store = CopyStore(tmp_path)
    reads = fetch_companions(["lab-companion"], sources, fetcher=_fetcher(_page), store=store,
                             terms={"x.ai": "forbids"}, now=NOW)
    read = reads["lab-companion"]
    assert read.outcome == "cited"
    assert store.citation(read.copy) is not None and not store.has(read.copy)


def test_a_rendered_source_is_refused_as_a_companion(tmp_path) -> None:
    with pytest.raises(ValueError, match="rendered"):
        fetch_companions(["lab-rendered"], SOURCES, fetcher=_fetcher(_page),
                         store=CopyStore(tmp_path), terms=TERMS, now=NOW)


def test_m509_a_refused_companion_is_counted_apart_from_unreachable(tmp_path) -> None:
    from decision.companions import refused

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": "https://unknown.example/filing/"})

    reads = fetch_companions(["lab-companion"], SOURCES, fetcher=_fetcher(handler),
                             store=CopyStore(tmp_path), terms=TERMS, now=NOW)
    assert refused(reads) == {"lab-companion": "redirect_unclassified:unknown.example"}
    assert refused({"x": reads["lab-companion"].__class__("x", "unreachable")}) == {}
