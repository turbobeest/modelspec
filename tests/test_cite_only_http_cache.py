"""Exercise real urllib redirects without sockets before named cache writes."""

import io
import json
import urllib.request
import urllib.response
from email.message import Message

import pytest

from scripts.benchmarks import fetch


PAGE = "INTERMEDIATE_SOURCE_MUST_NOT_REACH_CACHE"


@pytest.mark.parametrize("intermediate", [
    "https://x.ai/redirect", "https://DOCS.X.AI.:8443/redirect",
    "https://sub.docs.x.ai/redirect", "https://www.perplexity.ai/redirect",
    "https://ordinary.test/redirect",
])
def test_named_http_cache_respects_every_redirect(tmp_path, monkeypatch, intermediate):
    start = "https://example.test/start"
    final = "https://example.test/final"
    calls = []

    class Transport(urllib.request.HTTPSHandler):
        def https_open(self, request):
            calls.append(request.full_url)
            headers = Message()
            code = 200 if request.full_url == final else 302
            if code == 302:
                headers["Location"] = intermediate if request.full_url == start else final
            response = urllib.response.addinfourl(
                io.BytesIO(PAGE.encode() if code == 200 else b""),
                headers, request.full_url, code,
            )
            response.msg = "OK" if code == 200 else "Found"
            return response

    build_opener = urllib.request.build_opener
    monkeypatch.setattr(urllib.request, "urlopen", build_opener(Transport()).open)
    monkeypatch.setattr(urllib.request, "build_opener",
                        lambda *handlers: build_opener(*handlers, Transport()))
    page = fetch.load_or_get(start, tmp_path, fetch=True)
    assert page.text == PAGE
    assert calls == [start, intermediate, final]
    if "ordinary.test" in intermediate:
        assert page.path.read_text() == PAGE
        assert fetch.load_or_get(start, tmp_path, fetch=False).from_cache
    else:
        assert not page.path.exists()
        metadata = json.loads(next(tmp_path.glob("*.meta.json")).read_text())
        assert intermediate in metadata["resolved_urls"]
        assert metadata["snapshot_ref"].startswith("sha256:")
        assert all(PAGE.encode() not in path.read_bytes() for path in tmp_path.iterdir())
        with pytest.raises(FileNotFoundError):
            fetch.load_or_get(start, tmp_path, fetch=False)
