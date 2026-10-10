"""Check built or deployed ModelSpec copy against its sources of truth (MODEL-255)."""

from __future__ import annotations

import argparse
import html
import json
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit

import yaml

from api.ranking.engine import neutrality_commitment
from decision.excluded import REMOVED_TEXT
from pipeline import agent_copy, entity, worker_flags

ROOT = Path(__file__).resolve().parents[1]
CARD = ".well-known/mcp.json"
BUNDLE = "mcp/src/agent-copy.json"
SENTENCE_FILES = (
    "method/index.html",
    "llms.txt",
    "index.md",
    ".well-known/agent-skills/modelspec/SKILL.md",
    "brand/index.html",
)
# No product comparison vocabulary exists in the repository. Model providers
# and model names are deliberately absent: comparing models is the product.
COMPETITORS = ("OpenRouter", "LiteLLM", "Portkey", "Not Diamond", "RouteLLM")
# The schema.org types used by our generators, plus Thing for generic nodes.
# New structured-data kinds must be reviewed and added here, not accepted just
# because an arbitrary string has a schema.org prefix.
SCHEMA_TYPES = frozenset(
    {
        "Thing",
        "Organization",
        "WebSite",
        "Dataset",
        "WebAPI",
        "SoftwareApplication",
        "SoftwareSourceCode",
        "Offer",
        "BreadcrumbList",
        "ListItem",
        "WebApplication",
    }
)
USER_AGENT = "modelspec-surface-lint (+https://github.com/turbobeest/modelspec)"
MAX_LIVE_FILES = 5000
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
Fetch = Callable[[str], tuple[int, dict[str, str], bytes]]


@dataclass(frozen=True)
class Finding:
    surface: str
    check: str
    excerpt: str
    expected: str

    def line(self) -> str:
        return " | ".join(
            (
                self.surface,
                self.check,
                normalize(self.excerpt),
                "expected: " + normalize(self.expected),
            )
        )


def normalize(text: str) -> str:
    return " ".join(html.unescape(text).split())


class Page(HTMLParser):
    """Rendered text, metadata and JSON-LD; inline links preserve word spacing."""

    BLOCKS = {
        "p",
        "div",
        "section",
        "main",
        "header",
        "footer",
        "nav",
        "li",
        "br",
        "h1",
        "h2",
        "h3",
        "h4",
        "tr",
        "td",
        "th",
        "pre",
        "summary",
    }
    INVISIBLE = {"head", "title", "script", "style", "template", "svg"}
    VOID = {"meta", "link", "img", "input", "br", "hr", "source", "wbr"}

    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.title_parts: list[str] = []
        self.meta: dict[str, str] = {}
        self.links: list[str] = []
        self.ld: list[str] = []
        self.hidden: list[str] = []
        self.in_title = False
        self.in_ld = False
        self.paragraphs: list[str] = []
        self.paragraph: int | None = None
        self.feed(text)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "meta":
            key = attributes.get("name") or attributes.get("property")
            if key:
                self.meta[key.lower()] = attributes.get("content") or ""
        if attributes.get("href"):
            self.links.append(attributes["href"])
        if tag == "title":
            self.in_title = True
        if tag == "script" and (attributes.get("type") or "").lower() == "application/ld+json":
            self.in_ld = True
            self.ld.append("")
        if (
            tag in self.INVISIBLE
            or self.hidden
            or "hidden" in attributes
            or attributes.get("aria-hidden") == "true"
        ):
            if tag not in self.VOID:
                self.hidden.append(tag)
        elif tag in self.BLOCKS:
            self.parts.append(" ")
            if tag == "p":
                self.paragraph = len(self.paragraphs)
                self.paragraphs.append("")

    def handle_endtag(self, tag: str) -> None:
        if tag == "p":
            self.paragraph = None
        if tag == "title":
            self.in_title = False
        if tag == "script":
            self.in_ld = False
        if tag in self.hidden:
            at = len(self.hidden) - 1 - self.hidden[::-1].index(tag)
            del self.hidden[at:]
        if tag in self.BLOCKS and not self.hidden:
            self.parts.append(" ")

    def handle_data(self, text: str) -> None:
        if self.in_title:
            self.title_parts.append(text)
        if self.in_ld:
            self.ld[-1] += text
        if not self.hidden:
            self.parts.append(text)
            if self.paragraph is not None:
                self.paragraphs[self.paragraph] += text

    @property
    def visible(self) -> str:
        return normalize("".join(self.parts))

    @property
    def title(self) -> str:
        return normalize("".join(self.title_parts))

    @property
    def first_paragraph(self) -> str:
        return normalize(self.paragraphs[0]) if self.paragraphs else ""


def objects(value: Any):
    """Walk all JSON objects, including nested breadcrumbs and providers."""
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


def strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)


def owned(path: str) -> bool:
    return (
        path.endswith((".html", ".md"))
        or path == "llms.txt"
        or path == "openapi.yaml"
        or path.startswith(".well-known/")
        and path.endswith(".json")
    )


def lexicon_text(path: str, text: str) -> str:
    if path.endswith(".html"):
        page = Page(text)
        return normalize(" ".join([page.visible, page.title, *page.meta.values(), *page.ld]))
    if path.endswith(".json"):
        try:
            return normalize(" ".join(strings(json.loads(text))))
        except ValueError:
            return normalize(text)
    return normalize(text.replace(chr(96), ""))


def presence(
    texts: Mapping[str, str], *, absent: frozenset[str] = frozenset(), holding: bool = False
) -> list[Finding]:
    findings = []
    page = Page(texts.get("index.html", ""))
    if page.title != entity.TITLE:
        findings.append(Finding("index.html", "presence.title", page.title, entity.TITLE))
    for key in ("description", "og:description"):
        actual = normalize(page.meta.get(key, ""))
        if entity.ONE_SENTENCE not in actual:
            findings.append(Finding("index.html", "presence." + key, actual, entity.ONE_SENTENCE))
    if not page.first_paragraph.startswith(entity.ONE_SENTENCE):
        findings.append(
            Finding("index.html", "presence.lead", page.first_paragraph[:200], entity.ONE_SENTENCE)
        )
    for path in SENTENCE_FILES:
        if path in absent:
            continue
        text = (
            Page(texts.get(path, "")).visible
            if path.endswith(".html")
            else normalize(texts.get(path, ""))
        )
        if entity.ONE_SENTENCE not in text:
            findings.append(Finding(path, "presence.one_sentence", text[:200], entity.ONE_SENTENCE))
    if "method/index.html" not in absent:
        first = Page(texts.get("method/index.html", "")).first_paragraph
        if not first.startswith(entity.ONE_SENTENCE):
            findings.append(
                Finding("method/index.html", "presence.lead", first, entity.ONE_SENTENCE)
            )
    for path in ("method/index.html", "llms.txt"):
        text = (
            Page(texts.get(path, "")).visible
            if path.endswith(".html")
            else normalize(texts.get(path, ""))
        )
        if path not in absent and entity.DISAMBIGUATION not in text:
            findings.append(
                Finding(path, "presence.disambiguation", "missing", entity.DISAMBIGUATION)
            )
    if not holding:
        organizations = []
        for block in page.ld:
            try:
                organizations.extend(
                    node
                    for node in objects(json.loads(block))
                    if node.get("@type") == "Organization"
                )
            except ValueError:
                pass  # structured_data reports the parse error.
        if not organizations or any(
            node.get("description") != entity.ONE_SENTENCE for node in organizations
        ):
            findings.append(
                Finding(
                    "index.html",
                    "presence.organization",
                    "missing or different description",
                    entity.ONE_SENTENCE,
                )
            )
    return findings


SELF_DESCRIPTION = re.compile(
    rf"\b{re.escape(entity.NAME)}\s+(?:is|as|acts as|works as|serves as)\s+(?:an?\s+)?"
    r"[^.!?;:]{0,65}?\b(?:knowledge graph|router)\b"
    rf"|\b{re.escape(entity.NAME)}\s*,\s*(?:an?\s+)?[^.!?;:]{{0,45}}?\b(?:knowledge graph|router)\b"
    rf"|\b{re.escape(entity.NAME)}\s+routes\b"
    r"|\bour\s+(?:\w+\s+){0,3}(?:knowledge graph|router)\b",
    re.I,
)
X402 = re.compile(r"\bx402\b|\bpay[ -]per[ -]call without (?:an? )?(?:API )?key\b|\bBazaar\b", re.I)
CLI = re.compile(
    r"\bpip install modelspec(?![\w-])|\boffline\s+(?:decision\s+)?CLI\b"
    r"|\blocal\s+decision\s+CLI\b"
    r"|\bCLI\b[^.!?;:]{0,65}\b(?:offline|downloads? (?:the |a )?(?:data|catalogue|snapshot))\b"
    r"|\b(?:download (?:the |a )?(?:data|catalogue|snapshot))\b[^.!?;:]{0,35}\bCLI\b",
    re.I,
)
SPONSORSHIP = re.compile(r"\b(?:featured partner|sponsored|promoted|affiliate)\b", re.I)
COMPARISON = re.compile(
    r"\b(?:versus|vs\.?|compares? (?:to|with)|compared (?:to|with)|comparison|"
    r"better than|alternative to|unlike)\b",
    re.I,
)
NEGATION = re.compile(
    r"\b(?:no|not|never|without|unrelated|doesn't|does not|do not|don't|cannot|can't)\b", re.I
)


def negated(text: str, start: int, end: int) -> bool:
    # Restrict negations to the current clause, so an earlier disclaimer cannot
    # exempt a later affirmative claim. Coordinated 'no X, no Y' stays valid.
    before = re.split(r"[.!?;:]|\bbut\b", text[:start], flags=re.I)[-1]
    after = re.split(r"[.!?;:]|\bbut\b", text[end:], flags=re.I)[0]
    return bool(
        NEGATION.search(before[-100:])
        or NEGATION.search(text[start:end])
        or re.match(r"\s+(?:is|are)\s+(?:not|never|an? unrelated)\b", after, re.I)
    )


def lexicon(
    texts: Mapping[str, str], variables: Mapping[str, Any], commitment: Mapping[str, Any]
) -> list[Finding]:
    findings = []
    assertions = commitment.get("assertions", {})
    paid_placement = any(
        assertions.get(key) is False
        for key in ("accepts_paid_placement", "accepts_provider_paid_visibility")
    )
    referral_fees = assertions.get("accepts_referral_fees") is False
    for path, raw in sorted(texts.items()):
        if not owned(path):
            continue
        text = lexicon_text(path, raw)
        rules = [
            ("lexicon.positioning", SELF_DESCRIPTION, True),
            ("lexicon.cli", CLI, True),
            ("lexicon.removed-source", REMOVED_TEXT, False),
        ]
        if not worker_flags.enabled(dict(variables), "X402_ENABLED"):
            # Adopted legal disclosures describe conditional ledger behaviour.
            # Check active payment promises there; elsewhere even a mention is
            # drift while the rail is off. Legal text is never rewritten here.
            payment = (
                re.compile(
                    r"\b(?:ModelSpec|we|you)\s+(?:accept|accepts|offer|offers|support|supports|use|uses|pay)\b"
                    r"[^.!?;:]{0,50}\b(?:x402|Bazaar)\b",
                    re.I,
                )
                if path.startswith("legal/")
                else X402
            )
            rules.append(("lexicon.x402", payment, path.startswith("legal/")))
        for check, pattern, allow_negation in rules:
            for match in pattern.finditer(text):
                if allow_negation and negated(text, *match.span()):
                    continue
                findings.append(
                    Finding(
                        path,
                        check,
                        text[max(0, match.start() - 40) : match.end() + 80],
                        "current registry and decision-approved claims",
                    )
                )
        for match in SPONSORSHIP.finditer(text):
            gated = referral_fees if match.group().lower() == "affiliate" else paid_placement
            # A benchmark author's funding is provenance, not ModelSpec paid
            # placement. Retain that disclosure on the frozen benchmark pages.
            provenance = (
                path.startswith("b/")
                and match.group().lower() == "sponsored"
                and re.match(r"\s+by\b", text[match.end() :], re.I)
            )
            if gated and not provenance and not negated(text, *match.span()):
                findings.append(
                    Finding(
                        path,
                        "lexicon.neutrality",
                        text[max(0, match.start() - 40) : match.end() + 80],
                        "neutrality_commitment().assertions",
                    )
                )
        for old in entity.SUPERSEDED:
            if old.casefold() in text.casefold():
                findings.append(Finding(path, "presence.superseded", old, entity.ONE_SENTENCE))
        for sentence in re.split(r"[.!?;]|\bbut\b", text):
            if COMPARISON.search(sentence):
                for name in COMPETITORS:
                    if re.search(r"\b" + re.escape(name) + r"\b", sentence, re.I):
                        findings.append(
                            Finding(
                                path,
                                "lexicon.competitor",
                                sentence.strip()[:240],
                                "compare categories, not named products",
                            )
                        )
    return findings


def schema_context(value: Any) -> bool:
    if isinstance(value, str):
        return value.rstrip("/") in {"https://schema.org", "http://schema.org"}
    if isinstance(value, list):
        return bool(value) and all(schema_context(item) for item in value)
    if isinstance(value, dict):
        return bool(value) and all(schema_context(item) for item in value.values())
    return False


def structured_data(texts: Mapping[str, str]) -> list[Finding]:
    findings = []
    for path, text in sorted(texts.items()):
        if not path.endswith(".html"):
            continue
        page = Page(text)
        for block in page.ld:
            try:
                value = json.loads(block)
            except ValueError as error:
                findings.append(Finding(path, "jsonld.parse", str(error), "valid JSON-LD"))
                continue
            if not isinstance(value, (dict, list)):
                findings.append(
                    Finding(path, "jsonld.parse", block[:100], "a JSON-LD object or array")
                )
                continue
            for node in objects(value):
                if "@context" in node and not schema_context(node["@context"]):
                    findings.append(
                        Finding(path, "jsonld.context", str(node["@context"]), "https://schema.org")
                    )
                kinds = node.get("@type", [])
                kinds = kinds if isinstance(kinds, list) else [kinds]
                for kind in kinds:
                    local = (
                        re.sub(r"^https?://schema\.org/|^schema:", "", kind)
                        if isinstance(kind, str)
                        else ""
                    )
                    if local not in SCHEMA_TYPES:
                        findings.append(
                            Finding(path, "jsonld.type", str(kind), "a reviewed schema.org type")
                        )
                for key in ("name", "description"):
                    if key in node:
                        for claim in strings(node[key]):
                            if normalize(claim) not in page.visible:
                                findings.append(
                                    Finding(
                                        path,
                                        "jsonld.visible",
                                        claim,
                                        "same text in this page's visible body",
                                    )
                                )
    return findings


def tool_descriptions(surface: str, tools: Any, expected: Mapping[str, str]) -> list[Finding]:
    findings = []
    actual = {}
    if not isinstance(tools, list):
        return [Finding(surface, "agent.tools", str(tools)[:100], "the generated tool list")]
    for tool in tools:
        if not isinstance(tool, dict) or not isinstance(tool.get("name"), str):
            findings.append(Finding(surface, "agent.tools", str(tool)[:100], "a named tool"))
            continue
        name = tool["name"]
        if name in actual:
            findings.append(Finding(surface, "agent.tools", name, "each tool exactly once"))
        actual[name] = tool.get("description")
    for name in sorted(actual.keys() | expected.keys()):
        if actual.get(name) != expected.get(name) or name not in actual or name not in expected:
            findings.append(
                Finding(
                    surface,
                    "agent.tool." + name,
                    str(actual.get(name, "missing")),
                    expected.get(name, "no unregistered tool"),
                )
            )
    return findings


def agent_surfaces(
    texts: Mapping[str, str], copy: Mapping[str, Any], *, absent: frozenset[str] = frozenset()
) -> list[Finding]:
    findings = []
    for path in (CARD, BUNDLE):
        if path in absent or path == BUNDLE and path not in texts:
            continue
        try:
            value = json.loads(texts.get(path, ""))
            if not isinstance(value, dict):
                raise ValueError("expected an object")
        except ValueError as error:
            findings.append(Finding(path, "agent.parse", str(error), "the generated JSON object"))
            continue
        if path == CARD:
            if value.get("description") != entity.SHORT:
                findings.append(
                    Finding(path, "agent.description", str(value.get("description")), entity.SHORT)
                )
            findings.extend(tool_descriptions(path, value.get("tools"), copy["card"]))
        else:
            tools = value.get("tools")
            listed = (
                [{"name": name, "description": description} for name, description in tools.items()]
                if isinstance(tools, dict)
                else tools
            )
            findings.extend(tool_descriptions(path, listed, copy["tools"]))
            if value.get("instructions") != copy["instructions"]:
                findings.append(
                    Finding(
                        path,
                        "agent.instructions",
                        str(value.get("instructions")),
                        copy["instructions"],
                    )
                )
    if "openapi.yaml" not in absent:
        try:
            spec = yaml.safe_load(texts.get("openapi.yaml", ""))
            if not isinstance(spec, dict) or not isinstance(spec.get("paths"), dict):
                raise ValueError("expected OpenAPI paths")
            operations = {
                operation.get("operationId"): operation
                for methods in spec["paths"].values()
                if isinstance(methods, dict)
                for operation in methods.values()
                if isinstance(operation, dict)
            }
            for name, expected in copy["openapi"].items():
                operation = operations.get(name, {})
                for key, wanted in (
                    ("summary", expected["summary"]),
                    ("description", expected["lead"]),
                ):
                    actual = operation.get(key, "")
                    matches = isinstance(actual, str) and (
                        actual == wanted
                        if key == "summary"
                        else actual == wanted or actual.startswith(wanted + "\n\n")
                    )
                    if not matches:
                        findings.append(
                            Finding(
                                "openapi.yaml",
                                "agent.openapi." + name + "." + key,
                                str(actual),
                                wanted,
                            )
                        )
        except (ValueError, yaml.YAMLError) as error:
            findings.append(
                Finding("openapi.yaml", "agent.parse", str(error), "valid OpenAPI YAML")
            )
    return findings


def sitemap_entries(text: str) -> list[tuple[str, str]]:
    root = ET.fromstring(text)
    if root.tag != "{" + NS["s"] + "}urlset":
        raise ValueError("expected a sitemap urlset")
    return [
        (node.findtext("s:loc", "", NS), node.findtext("s:lastmod", "", NS))
        for node in root.findall("s:url", NS)
    ]


def freshness(
    texts: Mapping[str, str],
    *,
    lastmods: Mapping[str, str] | None = None,
    absent: frozenset[str] = frozenset(),
) -> list[Finding]:
    if "sitemap.xml" in absent:
        return []
    try:
        stamp = json.loads(texts.get("api/build.json", ""))["built_at"]
        built = datetime.fromisoformat(stamp.replace("Z", "+00:00")).date()
        entries = sitemap_entries(texts.get("sitemap.xml", ""))
    except (ValueError, KeyError, TypeError, ET.ParseError) as error:
        return [
            Finding(
                "sitemap.xml",
                "freshness.parse",
                str(error),
                "sitemap and api/build.json build date",
            )
        ]
    findings = []
    for url, stamp in entries:
        path = urlsplit(url).path
        try:
            modified = date.fromisoformat(stamp)
        except ValueError:
            findings.append(Finding(path, "freshness.lastmod", stamp or "missing", "an ISO date"))
            continue
        if modified > built:
            findings.append(
                Finding(path, "freshness.future", stamp, "no later than " + built.isoformat())
            )
        if lastmods is not None and path in lastmods and stamp != lastmods[path]:
            findings.append(Finding(path, "freshness.source", stamp, lastmods[path]))
    return findings


def lint(
    texts: Mapping[str, str],
    *,
    variables: Mapping[str, Any],
    commitment: Mapping[str, Any],
    copy: Mapping[str, Any],
    lastmods: Mapping[str, str] | None = None,
    absent: frozenset[str] = frozenset(),
    holding: bool = False,
) -> list[Finding]:
    """Pure checks over relative path -> text maps; no filesystem or network I/O."""
    return (
        presence(texts, absent=absent, holding=holding)
        + lexicon(texts, variables, commitment)
        + structured_data(texts)
        + agent_surfaces(texts, copy, absent=absent)
        + freshness(texts, lastmods=lastmods, absent=absent)
    )


def read_tree(tree: Path) -> dict[str, str]:
    return {
        path.relative_to(tree).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(tree.rglob("*"))
        if path.is_file()
        and (
            owned(path.relative_to(tree).as_posix())
            or path.relative_to(tree).as_posix() in {"api/build.json", "sitemap.xml", "robots.txt"}
        )
    }


def get(url: str) -> tuple[int, dict[str, str], bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return (
                response.status,
                {key.lower(): value for key, value in response.headers.items()},
                response.read(),
            )
    except urllib.error.HTTPError as error:
        return error.code, {}, error.read()
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return 0, {}, str(error).encode()


def holding_serves(path: str) -> bool:
    from pipeline import holding

    return (
        path in (*holding.KEEP_FILES, *holding.WRITTEN)
        or path.split("/", 1)[0] in holding.KEEP_DIRS["modelspec"]
    )


def live_tree(
    origin: str, fetch: Fetch = get
) -> tuple[dict[str, str], frozenset[str], bool, list[Finding]]:
    from pipeline import holding, live

    texts: dict[str, str] = {}
    failures = []
    origin = origin.rstrip("/")

    def read(path: str) -> int:
        url_path = "/" if path == "index.html" else "/" + path.removesuffix("index.html")
        status, _, body = fetch(origin + url_path)
        if status == 200:
            texts[path] = body.decode("utf-8", errors="replace")
        return status

    for path in ("index.html", "robots.txt", "sitemap.xml"):
        status = read(path)
        if status != 200 and path != "sitemap.xml":
            failures.append(Finding(path, "live.fetch", f"HTTP {status}", "HTTP 200"))
    is_holding = (
        "sitemap.xml" not in texts and texts.get("robots.txt", "").strip() == holding.ROBOTS.strip()
    )
    paths = {
        "openapi.yaml",
        "api/build.json",
        *SENTENCE_FILES,
        "auth.md",
        "agents.md",
        CARD,
        *live.DISCOVERY,
        *(path.lstrip("/") + "index.html" for path in live.PAGES),
    }
    paths.discard("index.html")
    if "sitemap.xml" in texts:
        try:
            for url, _ in sitemap_entries(texts["sitemap.xml"]):
                if urlsplit(url).netloc == urlsplit(origin).netloc:
                    paths.add(urlsplit(url).path.lstrip("/") + "index.html")
        except (ValueError, ET.ParseError):
            pass  # freshness reports the parse error.
    absent = frozenset(
        path for path in paths | {"sitemap.xml"} if is_holding and not holding_serves(path)
    )
    pending = sorted(paths - absent - texts.keys())
    while pending:
        path = pending.pop(0)
        if len(texts) >= MAX_LIVE_FILES:
            failures.append(
                Finding(origin, "live.limit", str(MAX_LIVE_FILES), "fewer discovered files")
            )
            break
        status = read(path)
        if status != 200:
            failures.append(Finding(path, "live.fetch", f"HTTP {status}", "HTTP 200"))
            continue
        if path.endswith(".html"):
            for link in Page(texts[path]).links:
                url = urlsplit(urljoin(origin + "/" + path, link))
                rel = url.path.lstrip("/")
                if (
                    url.netloc == urlsplit(origin).netloc
                    and owned(rel)
                    and not rel.endswith(".html")
                    and rel not in paths
                    and (not is_holding or holding_serves(rel))
                ):
                    paths.add(rel)
                    pending.append(rel)
    return texts, absent, is_holding, failures


def mcp_tools(*, get_only: bool = False) -> tuple[Any, str]:
    if get_only:
        return None, "MCP tools/list not checked: GET-only probe; JSON-RPC requires POST."
    request = urllib.request.Request(
        entity.MCP_ENDPOINT,
        method="POST",
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}).encode(),
        headers={
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read().decode()
            if response.headers.get("content-type", "").startswith("text/event-stream"):
                body = next(
                    line[5:].strip() for line in body.splitlines() if line.startswith("data:")
                )
            value = json.loads(body)
            if (
                isinstance(value, dict)
                and isinstance(value.get("result"), dict)
                and "tools" in value["result"]
            ):
                return value["result"]["tools"], "MCP tools/list checked without an API key."
            return None, "MCP tools/list not checked: endpoint did not return a tool list."
    except urllib.error.HTTPError as error:
        reason = (
            "authentication required; no key used"
            if error.code in {401, 403}
            else "metadata probe refused"
        )
        return None, f"MCP tools/list not checked: HTTP {error.code}, {reason}."
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, StopIteration) as error:
        return None, f"MCP tools/list not checked: {normalize(str(error))}."


def expected_lastmods(
    texts: Mapping[str, str], *, deployed: bool
) -> tuple[dict[str, str] | None, str]:
    from pipeline import live

    try:
        build = json.loads(texts["api/build.json"])
        stamp = datetime.fromisoformat(build["built_at"].replace("Z", "+00:00")).date().isoformat()
        if "models/index.html" in texts:
            return {
                urlsplit(url).path: stamp for url, _ in sitemap_entries(texts["sitemap.xml"])
            }, ""
        from pipeline.export import _commit

        if not deployed or build["commit"] == _commit(ROOT):
            return {path: live.lastmod(path) for path in live.PAGES}, ""
    except (ValueError, KeyError, TypeError, ET.ParseError):
        pass
    return None, "Source-change dates not checked: deployed build differs from this checkout."


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--tree", type=Path)
    mode.add_argument("--live", metavar="ORIGIN")
    parser.add_argument(
        "--get-only", action="store_true", help="skip the MCP JSON-RPC metadata POST"
    )
    parser.add_argument("--report", type=Path, help="write findings and unchecked items as JSON")
    args = parser.parse_args(argv)
    notes = []
    if args.live:
        texts, absent, is_holding, findings = live_tree(args.live)
        if is_holding:
            notes.append(
                "Holding mode: intentionally absent files are not applicable: "
                + ", ".join(sorted(absent))
            )
        tools, note = mcp_tools(get_only=args.get_only)
        notes.append(note)
    else:
        texts, absent, is_holding, findings = read_tree(args.tree), frozenset(), False, []
        texts[BUNDLE] = agent_copy.OUT.read_text(encoding="utf-8")
        tools = None
    copy = agent_copy.copy(json.loads(agent_copy.TIERS.read_text(encoding="utf-8")))
    lastmods, note = expected_lastmods(texts, deployed=bool(args.live))
    if note and not is_holding:
        notes.append(note)
    findings.extend(
        lint(
            texts,
            variables=worker_flags.production_vars(ROOT),
            commitment=neutrality_commitment(),
            copy=copy,
            absent=absent,
            holding=is_holding,
            lastmods=lastmods,
        )
    )
    if tools is not None:
        findings.extend(tool_descriptions(entity.MCP_ENDPOINT, tools, copy["tools"]))
    for finding in findings:
        print(finding.line())
    for note in notes:
        print("notices: " + note)
    print(f"{args.live or args.tree}: {len(findings)} findings; {len(texts)} files checked")
    if args.report:
        args.report.write_text(
            json.dumps(
                {
                    "origin": args.live or str(args.tree),
                    "findings": [asdict(finding) for finding in findings],
                    "notices": notes,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return int(bool(findings))


if __name__ == "__main__":
    raise SystemExit(main())
