"""The /about/ facts page, rendered from the entity registry and tiers.json."""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from pipeline import brand, entity, landing_chrome, structured_data
from pipeline.pricing import load_tiers

PAGE_PATH = Path("about/index.html")


def _href(url: str) -> str:
    if url.startswith(entity.SITE):
        rest = url.removeprefix(entity.SITE)
        return rest or "/"
    return url


def _item(text: str, href: str | None = None) -> str:
    escaped = html.escape(text, quote=False)
    if href is None:
        return "<li>" + escaped + "</li>"
    return '<li><a href="' + html.escape(href, quote=True) + '">' + escaped + "</a></li>"


def page(tiers: dict[str, Any], root: Path) -> str:
    """Server-rendered facts. Every sentence in `<main>` is a registry string."""
    claims = "".join(_item(claim.statement, _href(claim.proof)) for claim in entity.CLAIMS)
    calls = "".join(_item(call.statement, call.href) for call in entity.CALLS)
    costs = "".join(_item(line) for line in entity.cost_statements(tiers))
    description = html.escape(entity.ONE_SENTENCE, quote=True)
    heading = html.escape(entity.ABOUT_HEADING, quote=False)
    lead = (html.escape(entity.DISAMBIGUATION, quote=False) + " "
            + html.escape(entity.ONE_SENTENCE, quote=False))
    script = structured_data.script(structured_data.graph("/about/", root, root))
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>" + heading + "</title>"
        '<meta name="description" content="' + description + '">'
        '<meta property="og:description" content="' + description + '">'
        '<link rel="canonical" href="' + entity.SITE + '/about/">'
        + brand.head_links()
        + brand.social_meta(entity.ABOUT_HEADING, path="/about/")
        + '<link rel="stylesheet" href="/landing-assets/landing.css">'
        + '<link rel="stylesheet" href="/landing-assets/method.css">'
        + landing_chrome.lockup_style()
        + script
        + "</head><body><div class=\"axis\" aria-hidden=\"true\"></div>"
        + landing_chrome.site_header(current="/about/")
        + "<main><section class=\"method-hero\"><div><h1>" + heading + "</h1><p>" + lead
        + "</p></div></section><section><h2>"
        + html.escape(entity.CLAIMS_HEADING, quote=False) + "</h2><ul>" + claims
        + "</ul></section><section><h2>"
        + html.escape(entity.CALL_HEADING, quote=False) + "</h2><ul>" + calls
        + "</ul></section><section><h2>"
        + html.escape(entity.COST_HEADING, quote=False) + "</h2><ul>" + costs
        + '</ul></section><p><a href="' + entity.NEUTRALITY_PATH + '">'
        + html.escape(entity.NEUTRALITY_LINK, quote=False)
        + "</a></p></main>"
        + landing_chrome.footer()
        + "</body></html>\n"
    )


def write(tree: Path, root: Path) -> dict[str, Any]:
    out = Path(tree) / PAGE_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page(load_tiers(Path(root)), Path(root)), encoding="utf-8")
    return {"path": "/about/", "sitemap_paths": ["/about/"]}
