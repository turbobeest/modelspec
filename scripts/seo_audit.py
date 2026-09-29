#!/usr/bin/env python3
"""Crawl a deployed modelspec.dev and report what a search engine or agent sees.

    python scripts/seo_audit.py --origin https://modelspec.dev > audit.md

Starts from `/` and every sitemap URL, follows same-origin links on HTML pages,
and checks each page for status, robots directives, canonical, title,
description and JSON-LD. Every same-origin link and asset is fetched once, so a
broken one is named with the page that links it. Structured data is checked
against the fields Google's rich-results rules require for the types this site
publishes; schema.org itself only requires `@type`.

Exit status is 1 when any finding is an error, 0 otherwise. MODEL-218.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import live  # noqa: E402

#: Files an agent is told to read: the list `pipeline.live` checks in the tree.
DISCOVERY = (*(f"/{rel}" for rel in live.DISCOVERY), "/openapi.yaml")
MAX_URLS = 200
Fetch = Callable[[str], tuple[int, dict[str, str], bytes]]


def fetch(url: str) -> tuple[int, dict[str, str], bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": "modelspec-seo-audit"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return (response.status, {k.lower(): v for k, v in response.headers.items()},
                    response.read())
    except urllib.error.HTTPError as error:
        return error.code, {k.lower(): v for k, v in error.headers.items()}, b""
    except (urllib.error.URLError, TimeoutError):
        return 0, {}, b""


class _Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, str] = {}
        self.links: dict[str, list[str]] = {}
        self.refs: set[str] = set()
        self.title = ""
        self.h1 = 0
        self.lang = ""
        self.json_ld: list[str] = []
        self._in: str | None = None
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: v or "" for k, v in attrs}
        if tag == "html":
            self.lang = a.get("lang", "")
        elif tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.meta[key.lower()] = a.get("content", "")
        elif tag == "link":
            for rel in a.get("rel", "").lower().split():
                self.links.setdefault(rel, []).append(a.get("href", ""))
        elif tag == "h1":
            self.h1 += 1
        elif tag == "title" or (tag == "script" and a.get("type") == "application/ld+json"):
            self._in, self._buf = tag, []
        # Every <a>, <script> and <img> target, plus stylesheets and preloads;
        # not rel=canonical or rel=alternate, which the checks read separately.
        rels = set(a.get("rel", "").lower().split())
        if tag != "link" or rels & {"stylesheet", "preload", "modulepreload", "icon"}:
            for attr in ("href", "src"):
                if a.get(attr):
                    self.refs.add(a[attr])

    def handle_data(self, data: str) -> None:
        if self._in:
            self._buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._in == tag:
            text = "".join(self._buf).strip()
            if tag == "title":
                self.title = text
            else:
                self.json_ld.append(text)
            self._in = None


@dataclass
class Finding:
    level: str  # "error" | "warn"
    where: str
    what: str


@dataclass
class PageReport:
    url: str
    status: int
    indexable: bool = False
    canonical: str = ""
    title: str = ""
    types: list[str] = field(default_factory=list)


def _types(node: Any) -> list[dict[str, Any]]:
    """Every typed object in a JSON-LD value, `@graph` flattened."""
    if isinstance(node, list):
        return [t for item in node for t in _types(item)]
    if isinstance(node, dict):
        if "@graph" in node:
            return _types(node["@graph"])
        return [node] if "@type" in node else []
    return []


def _many(value: Any) -> list[dict[str, Any]]:
    """A schema.org property may hold one object or a list of them."""
    items = value if isinstance(value, list) else [value] if value else []
    return [item for item in items if isinstance(item, dict)]


def check_json_ld(item: dict[str, Any]) -> list[tuple[str, str]]:
    """(level, message) for one typed object, per Google's rich-results rules.

    Dataset: name, and description of 50 to 5,000 characters.
    BreadcrumbList: two or more ListItems with position and name, and an item
    URL on every one but the last.
    SoftwareApplication: name; a rich result also needs offers plus
    aggregateRating or review, which this site does not invent, so their
    absence is a warning.
    Article: headline, and author, datePublished and image recommended.
    """
    kind = item.get("@type")
    kinds = kind if isinstance(kind, list) else [kind]
    out: list[tuple[str, str]] = []
    if "Dataset" in kinds:
        if not item.get("name"):
            out.append(("error", "Dataset: name missing"))
        desc = str(item.get("description") or "")
        if not 50 <= len(desc) <= 5000:
            out.append(("error", f"Dataset: description is {len(desc)} chars (50-5000)"))
        for dist in _many(item.get("distribution")):
            if not dist.get("contentUrl"):
                out.append(("error", "Dataset: distribution without contentUrl"))
    if "BreadcrumbList" in kinds:
        items = item.get("itemListElement") or []
        if len(items) < 2:
            out.append(("warn", "BreadcrumbList: fewer than two items"))
        for i, crumb in enumerate(items):
            if crumb.get("position") != i + 1 or not crumb.get("name"):
                out.append(("error", f"BreadcrumbList: item {i + 1} lacks position or name"))
            if i < len(items) - 1 and not crumb.get("item"):
                out.append(("error", f"BreadcrumbList: item {i + 1} lacks item URL"))
    if "SoftwareApplication" in kinds or "WebApplication" in kinds:
        if not item.get("name"):
            out.append(("error", f"{kinds[0]}: name missing"))
        if not item.get("offers"):
            out.append(("warn", f"{kinds[0]} {item.get('name')!r}: no offers"))
        if not (item.get("aggregateRating") or item.get("review")):
            out.append(("warn", f"{kinds[0]} {item.get('name')!r}: no rating or review, "
                                "so no rich result (by design: none are invented)"))
    if "Article" in kinds or "BlogPosting" in kinds:
        if not item.get("headline"):
            out.append(("error", "Article: headline missing"))
        for key in ("author", "datePublished", "image"):
            if not item.get(key):
                out.append(("warn", f"Article: {key} missing"))
    return out


def audit(origin: str, get: Fetch = fetch, max_urls: int = MAX_URLS
          ) -> tuple[list[PageReport], list[Finding], list[str]]:
    origin = origin.rstrip("/")
    host = urllib.parse.urlsplit(origin).netloc
    findings: list[Finding] = []

    def same_origin(url: str) -> bool:
        return urllib.parse.urlsplit(url).netloc == host

    status, _, body = get(origin + "/sitemap.xml")
    sitemap = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body.decode("utf-8", "replace"))
    if status != 200 or not sitemap:
        findings.append(Finding("error", "/sitemap.xml", f"status {status}, {len(sitemap)} URLs"))
    status, _, body = get(origin + "/robots.txt")
    if status != 200 or b"Sitemap:" not in body:
        findings.append(Finding("error", "/robots.txt", "missing, or names no sitemap"))

    for path in DISCOVERY:
        code, _, data = get(origin + path)
        if code != 200 or not data:
            findings.append(Finding("error", path, f"discovery file answers {code}"))

    queue = [origin + "/", *sitemap]
    seen: set[str] = set()
    pages: list[PageReport] = []
    linked_from: dict[str, str] = {}
    while queue and len(pages) < max_urls:
        url = queue.pop(0).split("#", 1)[0]
        if url in seen or not same_origin(url):
            continue
        seen.add(url)
        code, headers, data = get(url)
        report = PageReport(url=url, status=code)
        pages.append(report)
        path = urllib.parse.urlsplit(url).path or "/"
        if code != 200:
            where = linked_from.get(url, "sitemap" if url in sitemap else "?")
            findings.append(Finding("error", path, f"answers {code} (linked from {where})"))
            continue
        if "text/html" not in headers.get("content-type", ""):
            continue
        parsed = _Page()
        parsed.feed(data.decode("utf-8", "replace"))
        robots = (parsed.meta.get("robots", "") + " " + headers.get("x-robots-tag", "")).lower()
        report.indexable = "noindex" not in robots
        report.canonical = (parsed.links.get("canonical") or [""])[0]
        report.title = parsed.title
        if report.indexable and report.canonical and report.canonical != url:
            findings.append(Finding("warn", path, f"canonical points elsewhere: {report.canonical}"))
        if report.indexable and not report.canonical:
            findings.append(Finding("error", path, "no canonical link"))
        if url in sitemap and not report.indexable:
            findings.append(Finding("error", path, "in the sitemap but noindex"))
        if report.indexable and url not in sitemap and report.canonical == url:
            findings.append(Finding("error", path, "indexable, self-canonical, not in the sitemap"))
        if report.indexable:
            if not parsed.title:
                findings.append(Finding("error", path, "no <title>"))
            if not parsed.meta.get("description"):
                findings.append(Finding("error", path, "no meta description"))
            if parsed.h1 != 1:
                findings.append(Finding("warn", path, f"{parsed.h1} <h1> elements in the served HTML"))
            if not parsed.lang:
                findings.append(Finding("warn", path, "no <html lang>"))
            if not parsed.meta.get("og:image"):
                findings.append(Finding("warn", path, "no og:image"))
        for block in parsed.json_ld:
            try:
                value = json.loads(block)
            except json.JSONDecodeError as exc:
                findings.append(Finding("error", path, f"JSON-LD does not parse: {exc}"))
                continue
            for item in _types(value):
                kind = item["@type"]
                report.types.append(kind if isinstance(kind, str) else "/".join(kind))
                for level, message in check_json_ld(item):
                    findings.append(Finding(level, path, message))
                for dist in _many(item.get("distribution")):
                    target = dist.get("contentUrl", "")
                    if same_origin(target):
                        linked_from.setdefault(target, path + " JSON-LD")
                        queue.append(target)
        for ref in parsed.refs:
            target = urllib.parse.urljoin(url, ref).split("#", 1)[0]
            if target.startswith(("http://", "https://")) and same_origin(target):
                linked_from.setdefault(target, path)
                queue.append(target)

    missing = [u for u in sitemap if u not in {p.url for p in pages}]
    for url in missing:
        findings.append(Finding("warn", url, f"sitemap URL not crawled (--max-urls {max_urls})"))
    return pages, findings, sitemap


def markdown(origin: str, pages: list[PageReport], findings: list[Finding],
             sitemap: list[str]) -> str:
    html = [p for p in pages if p.title or p.canonical or p.types]
    lines = [
        f"# SEO crawl of {origin}", "",
        f"{len(pages)} URLs fetched, {len(html)} HTML pages, {len(sitemap)} in the sitemap.", "",
        "| Page | Status | Indexable | Canonical | JSON-LD |",
        "| --- | --- | --- | --- | --- |",
    ]
    for p in html:
        path = urllib.parse.urlsplit(p.url).path
        canon = "self" if p.canonical == p.url else (p.canonical or "none")
        lines.append(f"| {path} | {p.status} | {'yes' if p.indexable else 'no'} | "
                     f"{canon} | {', '.join(p.types) or 'none'} |")
    lines += ["", "## Findings", ""]
    if not findings:
        lines.append("None.")
    for f in sorted(findings, key=lambda f: (f.level != "error", f.where)):
        lines.append(f"- **{f.level}** `{f.where}`: {f.what}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("--origin", default="https://modelspec.dev")
    parser.add_argument("--max-urls", type=int, default=MAX_URLS,
                        help="stop after fetching this many URLs, assets included")
    args = parser.parse_args(argv)
    pages, findings, sitemap = audit(args.origin, max_urls=args.max_urls)
    sys.stdout.write(markdown(args.origin, pages, findings, sitemap))
    return 1 if any(f.level == "error" for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
