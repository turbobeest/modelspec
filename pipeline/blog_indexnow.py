"""Publish an IndexNow key at build time and notify only a verified live blog.

Run after the production deploy with ``python -m pipeline.blog_indexnow --tree
dist/modelspec``. BLOG_ENABLED=true, SITE_MODE=live and INDEXNOW_KEY are required.
Protocol: https://www.indexnow.org/documentation
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET

ENDPOINT = "https://api.indexnow.org/indexnow"
ORIGIN = "https://modelspec.dev"
BLOG_INDEX = f"{ORIGIN}/blog/"
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


class IndexNowError(ValueError):
    """A sanitized failure that can be reported without revealing the key."""


@dataclass(frozen=True)
class Response:
    status: int
    url: str
    body: bytes
    headers: Mapping[str, str] = field(default_factory=dict)


def _noindex(directives: str) -> bool:
    return bool({"noindex", "none"}.intersection(re.split(r"[\s,:]+", directives.lower())))


class _PageMetadata(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.canonicals: list[str] = []
        self.noindex = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "link" and "canonical" in (attributes.get("rel") or "").lower().split():
            self.canonicals.append(attributes.get("href") or "")
        if tag == "meta" and (attributes.get("name") or "").lower() in {
            "robots",
            "googlebot",
            "bingbot",
        }:
            self.noindex |= _noindex(attributes.get("content") or "")


def _canonical_page(body: bytes, url: str) -> bool:
    metadata = _PageMetadata()
    try:
        metadata.feed(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return False
    return metadata.canonicals == [url] and not metadata.noindex


def _blog_url(url: str) -> bool:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.netloc != "modelspec.dev"
        or parsed.query
        or parsed.fragment
    ):
        return False
    if not parsed.path.startswith("/blog/") or not parsed.path.endswith("/"):
        return False
    segments = unquote(parsed.path).split("/")[1:-1]
    return all(re.fullmatch(r"[a-z0-9-]+", segment) for segment in segments)


def _prepared(tree: Path, environment: Mapping[str, str]) -> tuple[str, list[str]] | None:
    if environment.get("BLOG_ENABLED") != "true" or environment.get("SITE_MODE") != "live":
        return None
    key = environment.get("INDEXNOW_KEY")
    if not key:
        return None
    if not re.fullmatch(r"[A-Za-z0-9-]{8,128}", key):
        raise IndexNowError("Invalid IndexNow key")
    sitemap = Path(tree) / "sitemap.xml"
    if not sitemap.is_file():
        return None
    try:
        root = ET.parse(sitemap).getroot()
    except (OSError, ET.ParseError):
        raise IndexNowError("Cannot read the built sitemap") from None
    urls = list(
        dict.fromkeys(
            (entry.text or "").strip()
            for entry in root.findall(f"{SITEMAP_NS}url/{SITEMAP_NS}loc")
            if _blog_url((entry.text or "").strip())
        )
    )
    if BLOG_INDEX not in urls:
        return None
    if len(urls) > 10_000:
        raise IndexNowError("IndexNow accepts at most 10000 URLs per submission")
    for url in urls:
        page = Path(tree) / url.removeprefix(f"{ORIGIN}/") / "index.html"
        try:
            valid = _canonical_page(page.read_bytes(), url)
        except OSError:
            valid = False
        if not valid:
            raise IndexNowError(
                "Local blog page is missing, unpublished or has the wrong canonical URL"
            )
    return key, urls


def write_key(tree: Path, *, environment: Mapping[str, str] | None = None) -> str | None:
    """Write the public root verification file only for a built live blog."""
    prepared = _prepared(tree, os.environ if environment is None else environment)
    if prepared is None:
        return None
    key, _ = prepared
    filename = f"{key}.txt"
    try:
        (Path(tree) / filename).write_text(key, encoding="utf-8")
    except OSError:
        raise IndexNowError("Cannot write the IndexNow verification file") from None
    return filename


def fetch_url(url: str) -> Response:
    """Fetch a deployed page, retaining the final URL to detect redirects."""
    request = urllib.request.Request(url, headers={"User-Agent": "modelspec-indexnow"})
    with urllib.request.urlopen(request, timeout=20) as response:
        headers = dict(response.headers) if hasattr(response, "headers") else {}
        return Response(response.status, response.geturl(), response.read(), headers)


def send_urls(endpoint: str, payload: dict[str, object]) -> int:
    """Send the documented JSON POST without logging its key or response body."""
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "modelspec-indexnow",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code


def submit(
    tree: Path,
    *,
    environment: Mapping[str, str] | None = None,
    fetch: Callable[[str], Response] = fetch_url,
    send: Callable[[str, dict[str, object]], int] = send_urls,
) -> int:
    """Verify all selected live pages and the key file, then submit their URLs."""
    prepared = _prepared(tree, os.environ if environment is None else environment)
    if prepared is None:
        return 0
    key, urls = prepared
    for url in urls:
        try:
            response = fetch(url)
        except Exception:
            raise IndexNowError("Deployed blog page could not be verified") from None
        headers = {name.lower(): value.lower() for name, value in response.headers.items()}
        if (
            response.status != 200
            or response.url != url
            or not _canonical_page(response.body, url)
            or _noindex(headers.get("x-robots-tag", ""))
        ):
            raise IndexNowError(
                "Deployed blog page is missing, unpublished or has the wrong canonical URL"
            )
    key_url = f"{ORIGIN}/{key}.txt"
    try:
        response = fetch(key_url)
    except Exception:
        raise IndexNowError("Deployed IndexNow verification file could not be verified") from None
    if response.status != 200 or response.url != key_url or response.body != key.encode("utf-8"):
        raise IndexNowError("Deployed IndexNow verification file is missing or does not match")
    payload: dict[str, object] = {
        "host": "modelspec.dev",
        "key": key,
        "keyLocation": key_url,
        "urlList": urls,
    }
    try:
        status = send(ENDPOINT, payload)
    except Exception:
        raise IndexNowError("IndexNow submission failed") from None
    if status not in {200, 202}:
        raise IndexNowError("IndexNow submission failed")
    return len(urls)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tree", type=Path, required=True, help="Built modelspec site directory")
    args = parser.parse_args(argv)
    try:
        count = submit(args.tree)
    except IndexNowError as error:
        print(str(error), file=sys.stderr)
        return 1
    print(f"IndexNow submitted {count} blog URLs." if count else "IndexNow skipped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
