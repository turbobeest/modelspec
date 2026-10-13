"""IndexNow only receives canonical blog pages after a verified live deploy."""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from pipeline import blog_indexnow

KEY = "model223-test-key"
INDEX = "https://modelspec.dev/blog/"
POST = "https://modelspec.dev/blog/sample/r1/"
ENV = {"BLOG_ENABLED": "true", "SITE_MODE": "live", "INDEXNOW_KEY": KEY}


def page(url: str, *, robots: str = "index,follow") -> bytes:
    return (
        "<!doctype html><html><head>"
        f'<link rel="canonical" href="{url}">'
        f'<meta name="robots" content="{robots}">'
        "</head><body>Published fixture only.</body></html>"
    ).encode()


def tree(tmp_path: Path, urls: list[str] | None = None) -> Path:
    root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for url in urls if urls is not None else [INDEX, POST]:
        entry = ET.SubElement(root, "url")
        ET.SubElement(entry, "loc").text = url
        if url in {INDEX, POST}:
            path = tmp_path / url.removeprefix("https://modelspec.dev/") / "index.html"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(page(url))
    ET.ElementTree(root).write(tmp_path / "sitemap.xml", encoding="utf-8")
    return tmp_path


def no_network(*args):
    pytest.fail("IndexNow must not contact the network in this case")


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("BLOG_ENABLED", None),
        ("BLOG_ENABLED", ""),
        ("BLOG_ENABLED", "false"),
        ("BLOG_ENABLED", "TRUE"),
        ("BLOG_ENABLED", " true"),
        ("SITE_MODE", None),
        ("SITE_MODE", "holding"),
        ("SITE_MODE", "preview"),
        ("SITE_MODE", "LIVE"),
        ("INDEXNOW_KEY", None),
        ("INDEXNOW_KEY", ""),
    ],
)
def test_switches_and_key_fail_closed(tmp_path, name, value):
    built = tree(tmp_path)
    env = dict(ENV)
    if value is None:
        del env[name]
    else:
        env[name] = value
    assert blog_indexnow.write_key(built, environment=env) is None
    assert blog_indexnow.submit(built, environment=env, fetch=no_network, send=no_network) == 0
    assert not (built / f"{KEY}.txt").exists()


@pytest.mark.parametrize("urls", [[], [POST], ["https://modelspec.dev/"]])
def test_no_blog_index_never_publishes_key_or_submits(tmp_path, urls):
    built = tree(tmp_path, urls)
    assert blog_indexnow.write_key(built, environment=ENV) is None
    assert blog_indexnow.submit(built, environment=ENV, fetch=no_network, send=no_network) == 0


def test_missing_sitemap_skips_submission(tmp_path):
    assert blog_indexnow.write_key(tmp_path, environment=ENV) is None
    assert blog_indexnow.submit(tmp_path, environment=ENV, fetch=no_network, send=no_network) == 0


def test_write_key_only_adds_protocol_verification_file(tmp_path):
    built = tree(tmp_path)
    relative = blog_indexnow.write_key(built, environment=ENV)
    assert relative == f"{KEY}.txt"
    assert (built / relative).read_text(encoding="utf-8") == KEY


@pytest.mark.parametrize("key", ["short", "with space in key", "../outside-key", "x" * 129])
def test_invalid_key_is_rejected_without_printing_it(tmp_path, key):
    built = tree(tmp_path)
    with pytest.raises(blog_indexnow.IndexNowError, match="Invalid IndexNow key") as caught:
        blog_indexnow.write_key(built, environment={**ENV, "INDEXNOW_KEY": key})
    assert key not in str(caught.value)


@pytest.mark.parametrize(
    "body",
    [
        page(INDEX, robots="noindex,follow"),
        page(INDEX, robots="none"),
        page(POST),
        b"<html>Draft</html>",
    ],
)
def test_local_unpublished_or_wrong_canonical_page_is_rejected(tmp_path, body):
    built = tree(tmp_path)
    (built / "blog/index.html").write_bytes(body)
    with pytest.raises(blog_indexnow.IndexNowError, match="Local blog page"):
        blog_indexnow.write_key(built, environment=ENV)
    assert not (built / f"{KEY}.txt").exists()
    with pytest.raises(blog_indexnow.IndexNowError, match="Local blog page"):
        blog_indexnow.submit(built, environment=ENV, fetch=no_network, send=no_network)


def test_missing_local_page_is_rejected_before_any_fetch(tmp_path):
    built = tree(tmp_path)
    (built / "blog/sample/r1/index.html").unlink()
    with pytest.raises(blog_indexnow.IndexNowError, match="Local blog page"):
        blog_indexnow.submit(built, environment=ENV, fetch=no_network, send=no_network)


def test_only_canonical_host_blog_sitemap_urls_are_submitted(tmp_path):
    built = tree(
        tmp_path,
        [
            "https://modelspec.dev/",
            INDEX,
            POST,
            POST,
            "https://preview.modelspec.dev/blog/",
            "https://branch.modelspec.pages.dev/blog/",
            "http://modelspec.dev/blog/",
            "https://modelspec.dev.evil.example/blog/",
            "https://modelspec.dev:443/blog/",
            "https://user@modelspec.dev/blog/",
            "https://modelspec.dev/blog/feed.xml",
            "https://modelspec.dev/blog/?preview=true",
            "https://modelspec.dev/blog/../private/",
            "https://modelspec.dev/blog/%2e%2e/private/",
        ],
    )
    fetched = []
    sent = []

    def fetch(url):
        fetched.append(url)
        body = KEY.encode() if url.endswith(".txt") else page(url)
        return blog_indexnow.Response(status=200, url=url, body=body)

    def send(endpoint, payload):
        sent.append((endpoint, payload))
        return 200

    assert blog_indexnow.submit(built, environment=ENV, fetch=fetch, send=send) == 2
    assert fetched == [INDEX, POST, f"https://modelspec.dev/{KEY}.txt"]
    assert sent == [
        (
            "https://api.indexnow.org/indexnow",
            {
                "host": "modelspec.dev",
                "key": KEY,
                "keyLocation": f"https://modelspec.dev/{KEY}.txt",
                "urlList": [INDEX, POST],
            },
        )
    ]


@pytest.mark.parametrize("status", [200, 202])
def test_success_and_pending_key_validation_are_accepted(tmp_path, status):
    built = tree(tmp_path)
    assert (
        blog_indexnow.submit(
            built,
            environment=ENV,
            fetch=lambda url: blog_indexnow.Response(
                200, url, KEY.encode() if url.endswith(".txt") else page(url)
            ),
            send=lambda endpoint, payload: status,
        )
        == 2
    )


@pytest.mark.parametrize(
    "response",
    [
        (404, INDEX, page(INDEX)),
        (200, "https://modelspec.dev/", page(INDEX)),
        (200, INDEX, page("https://preview.modelspec.dev/blog/")),
        (200, INDEX, page(INDEX, robots="noindex")),
        (200, INDEX, b"<html>Holding page</html>"),
    ],
)
def test_deployed_missing_redirected_preview_or_holding_page_blocks_post(tmp_path, response):
    built = tree(tmp_path)
    with pytest.raises(blog_indexnow.IndexNowError, match="Deployed blog page"):
        blog_indexnow.submit(
            built,
            environment=ENV,
            fetch=lambda url: blog_indexnow.Response(*response),
            send=no_network,
        )


@pytest.mark.parametrize(
    "status,url,body",
    [
        (404, f"https://modelspec.dev/{KEY}.txt", KEY.encode()),
        (200, "https://modelspec.dev/", KEY.encode()),
        (200, f"https://modelspec.dev/{KEY}.txt", b"wrong-key"),
    ],
)
def test_missing_redirected_or_wrong_verification_file_blocks_post(tmp_path, status, url, body):
    built = tree(tmp_path)

    def fetch(target):
        if target.endswith(".txt"):
            return blog_indexnow.Response(status, url, body)
        return blog_indexnow.Response(200, target, page(target))

    with pytest.raises(blog_indexnow.IndexNowError, match="Deployed IndexNow verification file"):
        blog_indexnow.submit(built, environment=ENV, fetch=fetch, send=no_network)


@pytest.mark.parametrize("directive", ["noindex", "none"])
def test_deployed_http_robots_directive_blocks_post(tmp_path, directive):
    built = tree(tmp_path)
    with pytest.raises(blog_indexnow.IndexNowError, match="Deployed blog page"):
        blog_indexnow.submit(
            built,
            environment=ENV,
            fetch=lambda url: blog_indexnow.Response(
                200, url, page(url), {"X-Robots-Tag": directive}
            ),
            send=no_network,
        )


def test_missing_deployed_post_blocks_submission_even_when_index_is_live(tmp_path):
    built = tree(tmp_path)

    def fetch(url):
        return blog_indexnow.Response(200 if url == INDEX else 404, url, page(url))

    with pytest.raises(blog_indexnow.IndexNowError, match="Deployed blog page"):
        blog_indexnow.submit(built, environment=ENV, fetch=fetch, send=no_network)


def test_network_failure_cannot_leak_key(tmp_path, capsys):
    built = tree(tmp_path)

    def fetch(url):
        raise OSError(f"request failed {KEY}")

    with pytest.raises(blog_indexnow.IndexNowError) as caught:
        blog_indexnow.submit(built, environment=ENV, fetch=fetch, send=no_network)
    assert KEY not in str(caught.value)
    assert KEY not in capsys.readouterr().out


def test_http_failure_cannot_leak_response_or_key(tmp_path):
    built = tree(tmp_path)
    with pytest.raises(blog_indexnow.IndexNowError, match="IndexNow submission failed") as caught:
        blog_indexnow.submit(
            built,
            environment=ENV,
            fetch=lambda url: blog_indexnow.Response(
                200, url, KEY.encode() if url.endswith(".txt") else page(url)
            ),
            send=lambda endpoint, payload: 403,
        )
    assert KEY not in str(caught.value)


def test_cli_disabled_is_safe_and_reports_no_key(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("BLOG_ENABLED", raising=False)
    monkeypatch.setenv("INDEXNOW_KEY", KEY)
    assert blog_indexnow.main(["--tree", str(tmp_path)]) == 0
    captured = capsys.readouterr()
    assert "skipped" in captured.out
    assert KEY not in captured.out + captured.err


def test_cli_failure_reports_sanitized_error_and_exit_one(tmp_path, monkeypatch, capsys):
    built = tree(tmp_path)
    for name, value in ENV.items():
        monkeypatch.setenv(name, value)
    (built / "blog/index.html").write_bytes(b"Draft")
    assert blog_indexnow.main(["--tree", str(built)]) == 1
    captured = capsys.readouterr()
    assert "Local blog page" in captured.err
    assert KEY not in captured.out + captured.err


def test_urllib_adapter_uses_json_post_and_exact_url(monkeypatch):
    requests = []

    class Reply:
        status = 202

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def geturl(self):
            return POST

        def read(self):
            return page(POST)

    def urlopen(request, *, timeout):
        requests.append((request, timeout))
        return Reply()

    monkeypatch.setattr(blog_indexnow.urllib.request, "urlopen", urlopen)
    assert blog_indexnow.fetch_url(POST) == blog_indexnow.Response(202, POST, page(POST))
    assert blog_indexnow.send_urls(blog_indexnow.ENDPOINT, {"host": "modelspec.dev"}) == 202
    request, timeout = requests[-1]
    assert request.full_url == "https://api.indexnow.org/indexnow"
    assert request.method == "POST"
    assert request.headers["Content-type"] == "application/json; charset=utf-8"
    assert request.data == b'{"host": "modelspec.dev"}'
    assert timeout == 20
