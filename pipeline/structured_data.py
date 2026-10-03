"""JSON-LD for the pages modelspec.dev serves (MODEL-218).

    structured_data.inject(tree, root)

One `<script type="application/ld+json">` per page, holding a `@graph`. The
home page describes who publishes the site, the data (a Dataset with no
download: current data is served only by the hosted service), and the hosted
HTTP API and the MCP server. The decide board is a WebApplication for people. Every other page carries a
BreadcrumbList back to the home page.

Everything is read from the tree being published: the build stamp from
`api/build.json` and the model count from `api/index.json`. Nothing is rated or reviewed here,
so no SoftwareApplication gets Google's rich-result card; that needs an
aggregateRating or review, and this site does not invent either.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from pipeline import entity
from pipeline.social_profiles import profile_urls

BASE = "https://modelspec.dev"
API = "https://api.modelspec.dev"
REPO = "https://github.com/turbobeest/modelspec"
ORG = f"{BASE}/#organization"
DATA_LICENSE = "https://creativecommons.org/licenses/by-sa/4.0/"
ROOT = Path(__file__).resolve().parents[1]

#: Breadcrumb names for every page but the home page. A page the live tree
#: publishes and this table omits gets no JSON-LD, and `tests/test_holding.py`
#: fails.
CRUMBS = {
    "/method/": "Method",
    "/decide/": "Decide",
    "/pricing/": "Pricing",
    "/legal/terms/": "Terms",
    "/legal/privacy/": "Privacy",
    "/legal/neutrality/": "Neutrality commitment",
    "/feedback/": "Feedback",
    "/brand/": "Brand and press kit",
}

_BLOCK = re.compile(r'<script type="application/ld\+json" data-structured-data>.*?</script>\n?',
                    re.DOTALL)
_HEAD_END = re.compile(r"</head\s*>", re.IGNORECASE)


def _source() -> dict[str, Any]:
    # codeRepository is defined on SoftwareSourceCode, not SoftwareApplication.
    return {"@type": "SoftwareSourceCode", "codeRepository": REPO}


def _free() -> dict[str, Any]:
    return {"@type": "Offer", "price": "0", "priceCurrency": "USD"}


def organization(root: Path) -> dict[str, Any]:
    org: dict[str, Any] = {
        "@type": "Organization",
        "@id": ORG,
        "name": "ModelSpec",
        "legalName": "Sparks & Sawdust LLC",
        "url": f"{BASE}/",
        "logo": f"{BASE}/icon-512.png",
        "description": entity.ONE_SENTENCE,
    }
    org["sameAs"] = [*entity.SAME_AS, *profile_urls(root / "brand" / "social" / "profiles.json")]
    return org


def dataset(tree: Path) -> dict[str, Any]:
    build = json.loads((tree / "api" / "build.json").read_text(encoding="utf-8"))
    index = tree / "api" / "index.json"
    # With data splitting, the index path contains a removal notice instead
    # of a catalogue. Its missing count has the same meaning as an absent file.
    count = json.loads(index.read_text(encoding="utf-8")).get("count") if index.is_file() else None
    return {
        "@type": "Dataset",
        "@id": f"{BASE}/#dataset",
        "name": "ModelSpec catalogue and decision snapshot",
        "description": (
            f"Sourced evidence on {count} AI models: model cards, benchmark "
            "results, prices, licences and where each model runs. Current data is served by "
            "the hosted API and MCP server; the public copy is a delayed image "
            "about nine months old. A null field means not yet researched, "
            "never a guess."
        ) if count is not None else (
            "The frozen public image of ModelSpec model cards and benchmark evidence. "
            "Current model selection answers are computed per request by the API."
        ),
        "url": f"{BASE}/",
        "keywords": ["AI models", "LLM benchmarks", "model selection", "model pricing"],
        "license": DATA_LICENSE,
        "creator": {"@id": ORG},
        "publisher": {"@id": ORG},
        "version": build["export_schema_version"],
        "dateModified": build["built_at"],
    }


def api() -> dict[str, Any]:
    return {
        "@type": ["WebAPI", "SoftwareApplication"],
        "@id": f"{BASE}/#api",
        "name": "ModelSpec API",
        "description": "HTTP endpoints to decide, rank and check licence and residency policy.",
        "applicationCategory": "DeveloperApplication",
        "documentation": f"{BASE}/openapi.yaml",
        "provider": {"@id": ORG},
    }


def mcp() -> dict[str, Any]:
    return {
        "@type": "SoftwareApplication",
        "@id": f"{BASE}/#mcp",
        "name": "ModelSpec MCP server",
        "url": f"{API}/mcp",
        "applicationCategory": "DeveloperApplication",
        "isBasedOn": _source(),
        "provider": {"@id": ORG},
    }


def breadcrumbs(path: str) -> dict[str, Any]:
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "ModelSpec", "item": f"{BASE}/"},
            {"@type": "ListItem", "position": 2, "name": CRUMBS[path], "item": f"{BASE}{path}"},
        ],
    }


def graph(path: str, tree: Path, root: Path = ROOT) -> list[dict[str, Any]]:
    """The JSON-LD objects for the page at `path`."""
    if path == "/":
        return [
            organization(root),
            {"@type": "WebSite", "@id": f"{BASE}/#website", "name": "ModelSpec",
             "url": f"{BASE}/", "publisher": {"@id": ORG}},
            dataset(tree), api(), mcp(),
        ]
    nodes = [breadcrumbs(path)]
    if path == "/decide/":
        nodes.append({
            "@type": "WebApplication",
            "@id": f"{BASE}/decide/#app",
            "name": "ModelSpec Decide",
            "url": f"{BASE}/decide/",
            "applicationCategory": "BusinessApplication",
            "browserRequirements": "Requires JavaScript",
            "offers": _free(),
            "publisher": {"@id": ORG},
        })
    return nodes


def script(nodes: list[dict[str, Any]]) -> str:
    payload = json.dumps({"@context": "https://schema.org", "@graph": nodes},
                         ensure_ascii=False, separators=(",", ":"))
    return ('<script type="application/ld+json" data-structured-data>'
            + payload.replace("<", "\\u003c") + "</script>\n")


def strip(html: str) -> str:
    """`html` without the block `inject` writes."""
    return _BLOCK.sub("", html)


def inject(tree: Path, root: Path = ROOT) -> list[str]:
    """Write each page's JSON-LD into `tree`; return the paths written.

    Idempotent: a page's earlier block is replaced, not repeated.
    """
    written = []
    for path in ("/", *CRUMBS):
        page = tree / path.lstrip("/") / "index.html"
        if not page.is_file():
            continue
        html = strip(page.read_text(encoding="utf-8"))
        # `</head>` is optional in HTML, and JSON-LD is valid in the body too.
        head_end = _HEAD_END.search(html)
        at = head_end.start() if head_end else len(html)
        html = html[:at] + script(graph(path, tree, root)) + html[at:]
        page.write_text(html, encoding="utf-8")
        written.append(path)
    return written
