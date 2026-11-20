"""Every fetch path checks redirect hops against the terms register (MODEL-509). No network."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import httpx
import pytest

from decision.model import Source
from decision.retention import using_data_dir
from decision.sources import CopyStore, Fetcher, recheck

NOW = datetime(2026, 11, 19, 6, tzinfo=UTC)
START = "https://lab.example/page"
TERMS = {"lab.example": "permits", "www.lab.example": "permits", "mirror.example": "unclear"}


@pytest.fixture
def data_dir(tmp_path):
    (tmp_path / "data" / "registry").mkdir(parents=True)
    (tmp_path / "data" / "registry" / "source-terms.json").write_text(json.dumps(TERMS))
    with using_data_dir(tmp_path / "data"):
        yield tmp_path / "data"


def _fetcher(routes: dict[str, str], sent: list[str]) -> Fetcher:
    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        sent.append(url)
        if url in routes:
            return httpx.Response(302, headers={"location": routes[url]})
        return httpx.Response(200, text="<html><body><p>hello</p></body></html>",
                              headers={"content-type": "text/html"})

    return Fetcher(httpx.Client(transport=httpx.MockTransport(handler)), retries=0,
                   min_host_interval=0, sleep=lambda _s: None)


def test_hop_to_an_unclassified_host_is_refused_before_the_request(data_dir) -> None:
    sent: list[str] = []
    result = _fetcher({START: "https://unknown.example/x"}, sent).fetch(START)
    assert (result.outcome, result.error, result.body) == (
        "unreachable", "redirect_unclassified:unknown.example", b"")
    assert sent == [START]


def test_hop_to_a_classified_host_and_within_a_host_pass(data_dir) -> None:
    sent: list[str] = []
    routes = {START: "https://www.lab.example/page", "https://www.lab.example/page": "https://www.lab.example/p2",
              "https://www.lab.example/p2": "https://mirror.example/z"}
    result = _fetcher(routes, sent).fetch(START)
    assert result.outcome == "ok"
    assert sent[-1] == "https://mirror.example/z"


def test_a_later_unclassified_hop_is_refused_too(data_dir) -> None:
    sent: list[str] = []
    routes = {START: "https://www.lab.example/page", "https://www.lab.example/page": "https://other.example/"}
    result = _fetcher(routes, sent).fetch(START)
    assert result.error == "redirect_unclassified:other.example"
    assert "https://other.example/" not in sent


def test_without_a_data_dir_redirects_behave_as_before(monkeypatch) -> None:
    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)
    sent: list[str] = []
    result = _fetcher({START: "https://unknown.example/x"}, sent).fetch(START)
    assert result.outcome == "ok"
    assert sent[-1] == "https://unknown.example/x"


def test_an_unreadable_register_behaves_as_before(tmp_path) -> None:
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry" / "source-terms.json").write_text("{")
    sent: list[str] = []
    with using_data_dir(tmp_path):
        result = _fetcher({START: "https://unknown.example/x"}, sent).fetch(START)
    assert result.outcome == "ok"


def test_recheck_names_the_refusal_keeps_no_bytes_and_counts_no_failure(data_dir, tmp_path) -> None:
    source = Source(id="lab-page", url=START, kind="official_registry", normaliser="html-default",
                    fetch="http", cited_regions=[{"id": "page", "locator": {"kind": "page"}}])
    sent: list[str] = []
    store = CopyStore(tmp_path / "copies")
    report = recheck([source], {}, [], fetcher=_fetcher({START: "https://unknown.example/x"}, sent),
                     store=store, now=NOW)
    assert [(s.source_id, s.reason) for s in report.skipped] == [
        ("lab-page", "redirect_unclassified:lab-page:unknown.example")]
    assert report.states["lab-page"].consecutive_failures == 0
    assert report.states["lab-page"].snapshot is None
    assert not list((tmp_path / "copies").rglob("*")) if (tmp_path / "copies").exists() else True
