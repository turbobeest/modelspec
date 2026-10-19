"""Collectors reject restricted fetches before retaining derived source text."""

import hashlib
import io
import json
import urllib.request
import urllib.response
from email.message import Message
from types import SimpleNamespace

import pytest

from decision.sources import CopyStore
from scripts import model_160_evidence as boards
from scripts import model_163_local as local
from scripts import migrate_oll_evidence, model_158_fable_terminal_bench, model_161_data
from scripts import model_174_hardware_private, model_191_verify_existing, model_192_evidence
from scripts import model_233_evidence, refresh_leaderboards


SENTINEL = "MODEL411-COLLECTOR-SENTINEL"
URL = "https://ordinary.example/board"
RESTRICTED = "https://docs.x.ai/models"


class Response(io.BytesIO):
    def __init__(self, body, resolved):
        super().__init__(body)
        self.resolved = resolved

    def geturl(self):
        return self.resolved


def _assert_no_source_text(root):
    assert all(SENTINEL.encode() not in path.read_bytes()
               for path in root.rglob("*") if path.is_file())


def _mock_response(monkeypatch, fetch):
    monkeypatch.setattr(urllib.request, "urlopen", fetch)
    monkeypatch.setattr(urllib.request, "build_opener",
                        lambda *handlers: SimpleNamespace(open=fetch))


@pytest.fixture(params=[
    "pdf", "board", "rendered", "data", "local-json", "local-text", "hardware", "existing",
    "finance", "evidence", "oll", "leaderboards",
])
def collector(request, tmp_path, monkeypatch):
    store = CopyStore(tmp_path / "copies")
    body = json.dumps({"excerpt": SENTINEL}).encode()
    name = request.param
    url = URL
    timeout = 180
    if name == "pdf":
        url = model_158_fable_terminal_bench.CARD_URL
        timeout = 120

        def pdf_reader(stream):
            text = "8.6 Terminal-Bench 4.0 " + stream.getvalue().decode() + " 8.7 "
            return SimpleNamespace(pages=[SimpleNamespace(extract_text=lambda: text)] * 172)

        monkeypatch.setattr(model_158_fable_terminal_bench.pypdf, "PdfReader", pdf_reader)
        read = lambda: model_158_fable_terminal_bench.system_card_copy(store)
    elif name == "board":
        read = lambda: boards.Registry(store).fetch(url)
    elif name == "rendered":
        url = "https://api.firecrawl.dev/v2/scrape"
        body = json.dumps({"data": {"markdown": SENTINEL,
                                   "metadata": {"sourceURL": URL}}}).encode()
        monkeypatch.setenv("FIRECRAWL_API_KEY", "synthetic-key")
        registry = boards.Registry(store, rendered_cache=tmp_path / "rendered")
        read = lambda: registry.fetch_rendered(URL)
    elif name == "data":
        read = lambda: model_161_data.fetch(url)
    elif name == "local-json":
        timeout = 30
        read = lambda: local._fetch_json(url)
    elif name == "local-text":
        timeout = 30
        read = lambda: local._fetch_text(url)
    elif name == "hardware":
        read = lambda: model_174_hardware_private.fetch_bytes(url)
    elif name == "existing":
        read = lambda: model_191_verify_existing._fetch(url)
    elif name == "finance":
        url = model_192_evidence.URL
        timeout = 60
        row = {"model_name": SENTINEL, "provider": "test", "harness_version": "v1",
               "task_set_version": "v2", "pass_at_1": 0.5,
               "completed_at": "2026-09-28T00:00:00Z"}
        body = json.dumps(row, separators=(",", ":")).replace('"', '\\"').encode()
        read = lambda: model_192_evidence.fetch_rows(store)
    elif name == "evidence":
        timeout = 120
        source = model_233_evidence.Source("test", url, "text-default", "rows")
        read = lambda: model_233_evidence.retain(source, store)
    elif name == "oll":
        read = lambda: migrate_oll_evidence._get(url, tmp_path / "cache")
    else:
        read = lambda: refresh_leaderboards._fetch(url)
    return read, url, body, timeout


def _redirect_transport(monkeypatch, url, body, *, restricted):
    calls = []
    intermediate = RESTRICTED if restricted else URL + "/ordinary-hop"
    final = URL + "/final"

    class Transport(urllib.request.HTTPSHandler):
        def https_open(self, request):
            calls.append((request.full_url, request.timeout))
            headers = Message()
            if request.full_url == final:
                code, payload = 200, body
            else:
                code, payload = 302, b""
                headers["Location"] = final if request.full_url == intermediate else intermediate
            response = urllib.response.addinfourl(io.BytesIO(payload), headers,
                                                 request.full_url, code)
            response.msg = "OK" if code == 200 else "Found"
            return response

    build_opener = urllib.request.build_opener
    monkeypatch.setattr(urllib.request, "urlopen", build_opener(Transport()).open)
    monkeypatch.setattr(urllib.request, "build_opener",
                        lambda *handlers: build_opener(*handlers, Transport()))
    return calls, intermediate, final


def test_intermediate_cite_only_hop_is_refused_before_following(
        tmp_path, monkeypatch, collector):
    read, url, body, timeout = collector
    calls, _, _ = _redirect_transport(monkeypatch, url, body, restricted=True)
    with pytest.raises(ValueError, match="cite-only"):
        read()
    assert calls == [(url, timeout)]
    _assert_no_source_text(tmp_path)


def test_ordinary_redirect_chain_preserves_collection(tmp_path, monkeypatch, collector):
    read, url, body, timeout = collector
    calls, intermediate, final = _redirect_transport(monkeypatch, url, body, restricted=False)
    result = read()
    assert calls == [(url, timeout), (intermediate, timeout), (final, timeout)]
    assert SENTINEL in repr(result) or any(
        SENTINEL.encode() in path.read_bytes() for path in tmp_path.rglob("*") if path.is_file())


def test_board_redirect_cannot_retain_a_new_projection_hash(tmp_path, monkeypatch):
    body = json.dumps({"rows": [{"model": SENTINEL, "pass_at_1": 0.7}]}).encode()
    _mock_response(monkeypatch, lambda *args, **kwargs: Response(body, RESTRICTED))
    registry = boards.Registry(CopyStore(tmp_path))
    blocked = False
    try:
        raw, ref = registry.fetch(URL)
        projected = boards.project_deepswe(raw, url=URL, page_ref=ref)
        registry.add("board", "source", URL, projected, "pass_at_1")
    except ValueError as error:
        assert "cite-only" in str(error)
        blocked = True
    _assert_no_source_text(tmp_path)
    assert blocked


@pytest.mark.parametrize("metadata", [
    {"sourceURL": RESTRICTED},
    {"sourceURL": URL, "resolved_urls": [RESTRICTED, URL + "/final"]},
])
def test_rendered_board_redirect_cannot_retain_projection_text(tmp_path, monkeypatch, metadata):
    markdown = ("| # | Model | Score | Pass Rate |\n| --- | --- | --- | --- |\n"
                f"| 1 | {SENTINEL} | 50 | 40% |\n")
    payload = json.dumps({"data": {"markdown": markdown, "metadata": metadata}}).encode()
    monkeypatch.setenv("FIRECRAWL_API_KEY", "synthetic-key")
    _mock_response(monkeypatch, lambda *args, **kwargs: Response(payload, URL))
    registry = boards.Registry(CopyStore(tmp_path / "copies"),
                               rendered_cache=tmp_path / "rendered")
    blocked = False
    try:
        text, ref = registry.fetch_rendered(URL)
        projected = boards.project_frontiercode(text, url=URL, page_ref=ref)
        registry.add("board", "source", URL, projected, "score", fetch="rendered")
    except ValueError as error:
        assert "cite-only" in str(error)
        blocked = True
    _assert_no_source_text(tmp_path)
    assert blocked


def test_local_memory_redirect_cannot_retain_quoted_table(tmp_path, monkeypatch):
    html = ("<table><tr><th>Model name</th><th>Quant</th><th>Total @ 8K</th></tr>"
            f"<tr><td>{SENTINEL}</td><td>Q4_K_M</td><td>3.5 GB</td></tr></table>")
    _mock_response(monkeypatch, lambda *args, **kwargs: Response(html.encode(), RESTRICTED))
    store = CopyStore(tmp_path)
    blocked = False
    try:
        source = local._fetch_text(URL)
        configuration = local.parse_memory_configuration(
            source, model_names=(SENTINEL,), quantisation="Q4_K_M",
            context_tokens=8192, runtime_memory_gb=3.5,
        )
        store.put(json.dumps(configuration).encode(), source_url=URL)
    except ValueError as error:
        assert "cite-only" in str(error)
        blocked = True
    _assert_no_source_text(tmp_path)
    assert blocked


@pytest.mark.parametrize("reader", [local._fetch_json, local._fetch_text])
def test_local_source_redirect_is_rejected_before_extraction(monkeypatch, reader):
    _mock_response(monkeypatch,
                   lambda *args, **kwargs: Response(b'{"modelId":"test"}', RESTRICTED))
    with pytest.raises(ValueError, match="cite-only"):
        reader(URL)


@pytest.mark.parametrize("reader", ["http", "rendered", "local-json", "local-text"])
def test_direct_cite_only_collector_does_not_fetch(tmp_path, monkeypatch, reader):
    def forbidden(*args, **kwargs):
        pytest.fail("unsupported cite-only source reached the collector fetch")

    monkeypatch.setenv("FIRECRAWL_API_KEY", "synthetic-key")
    _mock_response(monkeypatch, forbidden)
    registry = boards.Registry(CopyStore(tmp_path))
    call = {"http": registry.fetch, "rendered": registry.fetch_rendered,
            "local-json": local._fetch_json, "local-text": local._fetch_text}[reader]
    with pytest.raises(ValueError, match="cite-only"):
        call(RESTRICTED)
    assert not list(tmp_path.iterdir())


def test_ordinary_collectors_keep_bodies_and_reuse_existing_caches(tmp_path, monkeypatch):
    payload = b'{"modelId":"ordinary"}'
    calls = []

    def fetch(*args, **kwargs):
        calls.append(args)
        return Response(payload, URL + "/final")

    _mock_response(monkeypatch, fetch)
    store = CopyStore(tmp_path / "copies")
    cache = tmp_path / "rendered"
    cache.mkdir()
    (cache / (hashlib.sha256(URL.encode()).hexdigest() + ".md")).write_text("ordinary markdown")
    registry = boards.Registry(store, rendered_cache=cache)
    body, ref = registry.fetch(URL)
    assert body == store.get(ref, source_url=URL) == payload
    assert registry.fetch(URL) == (body, ref)
    text, rendered_ref = registry.fetch_rendered(URL)
    assert text == "ordinary markdown"
    assert store.get(rendered_ref, source_url=URL) == text.encode()
    assert len(calls) == 1
    assert local._fetch_json(URL) == {"modelId": "ordinary"}
    assert local._fetch_text(URL) == payload.decode()
    oll_cache = tmp_path / "oll-cache"
    oll_cache.mkdir()
    cached = b'{"ordinary":"historic-cache"}'
    (oll_cache / (hashlib.sha256(URL.encode()).hexdigest() + ".json")).write_bytes(cached)
    call_count = len(calls)
    assert migrate_oll_evidence._get(URL, oll_cache) == cached
    assert len(calls) == call_count
