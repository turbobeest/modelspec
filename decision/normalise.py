"""Normalise a fetched page into stable text, and select its cited regions.

Change detection compares fingerprints of normalised text, so everything a page
changes without changing what it says must normalise away: scripts, styles,
navigation, the site header and footer, cookie banners, ads, timestamps and
relative dates ("3 days ago"), tracking query strings, attribute order and
whitespace. The output is text only, one block per line and table cells joined
by `` | ``, so markup churn never reaches a fingerprint.

A rule set is chosen by name on each source (``Source.normaliser``). HTML and
plain text are handled; PDF is not yet (see ``UnsupportedContentError``).

Deterministic and offline: the standard library only, no network.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from collections.abc import Iterator
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Literal
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# --- rule sets -----------------------------------------------------------------------------------

#: Query parameters that identify a click, never a page.
TRACKING_PARAMS = frozenset(
    {
        "gclid",
        "dclid",
        "gbraid",
        "wbraid",
        "fbclid",
        "msclkid",
        "yclid",
        "igshid",
        "twclid",
        "mc_cid",
        "mc_eid",
        "_ga",
        "_gl",
        "_hsenc",
        "_hsmi",
        "hsctatracking",
        "mkt_tok",
        "ref",
        "ref_src",
        "ref_url",
        "spm",
        "si",
        "cb",
        "cachebust",
    }
)
TRACKING_PREFIXES = ("utm_", "pk_", "mtm_", "oly_")

_MONTH = (
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?"
    r"|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\.?"
)
_DATE = (
    rf"(?:\d{{4}}-\d{{2}}-\d{{2}}|{_MONTH}\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s+\d{{4}}"
    rf"|\d{{1,2}}(?:st|nd|rd|th)?\s+{_MONTH},?\s+\d{{4}}|\d{{1,2}}/\d{{1,2}}/\d{{2,4}})"
)
_CLOCK = r"\d{1,2}:\d{2}(?::\d{2}(?:\.\d+)?)?\s*(?:[ap]\.?m\.?)?"
_ZONE = r"(?:z|utc|gmt|bst|cest|cet|ist|jst|aest|[ecmp][sd]t|[+-]\d{2}:?\d{2})"

#: Volatile time text. Deliberately narrow: a bare date can be a fact (a release
#: date), so only a date that a page labels as its own update time is removed.
VOLATILE_PATTERNS = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        # "Last updated: September 20, 2026 14:02 UTC", "Generated 2026-09-20T14:02:11Z"
        rf"\b(?:last\s+)?(?:updated|modified|edited|generated|refreshed|retrieved|checked|synced|built)"
        rf"(?:\s+(?:on|at))?\s*:?\s*{_DATE}(?:[t,\s]+{_CLOCK})?(?:\s*{_ZONE})?\b",
        # Full ISO date-times are page timestamps, not facts.
        rf"\b\d{{4}}-\d{{2}}-\d{{2}}t\d{{2}}:\d{{2}}(?::\d{{2}}(?:\.\d+)?)?(?:{_ZONE})?",
        # "3 days ago", "an hour ago", "just now"
        r"\b(?:\d+|a|an|one|a\s+few|few)\s+"
        r"(?:second|sec|minute|min|hour|hr|day|week|month|year)s?\s+ago\b",
        r"\bjust\s+now\b",
        # A clock time with a zone or am/pm: "14:02 UTC", "9:47 pm"
        rf"\b\d{{1,2}}:\d{{2}}(?::\d{{2}})?\s*(?:[ap]\.?m\.?|{_ZONE})(?![a-z])",
    )
)

_URL = re.compile(r"https?://[^\s<>\"')\]]+", re.IGNORECASE)
_SPACE = re.compile(r"\s+")
#: A line left with nothing but separators once volatile text is gone.
_EMPTY_LINE = re.compile(r"^[\W_]*$")

#: Class or id tokens of page furniture that carries no facts.
FURNITURE_TOKEN = re.compile(
    r"^(?:ad|ads|advert\w*|advertisement|sponsor\w*|promo\w*|banner-ad|"
    r"[\w-]*cookie[\w-]*|[\w-]*consent[\w-]*|gdpr|onetrust\w*|cc-banner|newsletter\w*|skip-link)$",
    re.IGNORECASE,
)
FURNITURE_ROLES = frozenset({"navigation", "banner", "contentinfo", "complementary", "search"})


@dataclass(frozen=True)
class RuleSet:
    """A named normalisation recipe. ``content`` says which parser applies."""

    name: str
    content: Literal["html", "text"]
    drop_tags: frozenset[str] = frozenset()
    #: Drop ``<header>``/``<footer>`` unless they sit inside an article, main or section.
    drop_page_chrome: bool = True
    drop_furniture: bool = True
    strip_volatile: bool = True
    strip_tracking: bool = True


NORMALISERS: dict[str, RuleSet] = {
    rules.name: rules
    for rules in (
        RuleSet(
            "html-default",
            "html",
            drop_tags=frozenset(
                {
                    "head",
                    "script",
                    "style",
                    "noscript",
                    "template",
                    "iframe",
                    "svg",
                    "canvas",
                    "nav",
                    "aside",
                    "form",
                    "button",
                    "dialog",
                    "link",
                    "meta",
                    "object",
                    "embed",
                }
            ),
        ),
        RuleSet("text-default", "text"),
    )
}


class UnsupportedContentError(ValueError):
    """The content type has no normaliser yet (PDF, for now)."""

    def __init__(self, kind: str) -> None:
        super().__init__(f"unsupported content: {kind}")
        self.kind = kind


# --- locators ------------------------------------------------------------------------------------

LocatorKind = Literal["page", "css", "heading", "table"]

_COMPOUND = re.compile(
    r"^(?P<tag>[a-zA-Z][\w-]*|\*)?(?P<rest>(?:#[\w-]+|\.[\w-]+|\[[\w-]+(?:=(?:\"[^\"]*\"|'[^']*'|[^\]]*))?\])*)$"
)
_PART = re.compile(r"#([\w-]+)|\.([\w-]+)|\[([\w-]+)(?:=(\"[^\"]*\"|'[^']*'|[^\]]*))?\]")


@dataclass(frozen=True)
class _Compound:
    tag: str | None
    id: str | None
    classes: tuple[str, ...]
    attrs: tuple[tuple[str, str | None], ...]


@dataclass(frozen=True)
class Locator:
    """Where a cited region sits in a page.

    ``page`` is the whole normalised page; ``css`` is a simple selector (tags, ``#id``,
    ``.class``, ``[attr]`` or ``[attr=value]``, joined by descendant or ``>``
    combinators); ``heading`` is a heading's id or text, and the region runs to the
    next heading of the same or a higher level; ``table`` is the n-th table (0-based).
    """

    kind: LocatorKind
    value: str = ""

    def __post_init__(self) -> None:
        if self.kind == "css":
            _parse_selector(self.value)
        elif self.kind == "table":
            if not self.value.isdigit():
                raise ValueError(f"table locator needs a non-negative index, got {self.value!r}")
        elif self.kind == "heading":
            if not self.value.strip():
                raise ValueError("heading locator needs an id or heading text")
        elif self.kind != "page":
            raise ValueError(f"unknown locator kind {self.kind!r}")

    @classmethod
    def page(cls) -> Locator:
        return cls("page")

    @classmethod
    def css(cls, selector: str) -> Locator:
        return cls("css", selector)

    @classmethod
    def heading(cls, anchor: str) -> Locator:
        return cls("heading", anchor)

    @classmethod
    def table(cls, index: int) -> Locator:
        return cls("table", str(index))


def _parse_selector(selector: str) -> tuple[tuple[str, _Compound], ...]:
    """Parse into ``((combinator, compound), ...)``; combinator is ``" "`` or ``">"``."""
    tokens = re.sub(r"\s*>\s*", " > ", selector.strip()).split()
    steps: list[tuple[str, _Compound]] = []
    combinator = " "
    for token in tokens:
        if token == ">":
            if not steps or combinator == ">":
                raise ValueError(f"bad CSS selector {selector!r}")
            combinator = ">"
            continue
        m = _COMPOUND.match(token)
        if not m or not token:
            raise ValueError(f"unsupported CSS selector {selector!r}")
        tag = m["tag"] if m["tag"] not in (None, "*") else None
        ident, classes, attrs = None, [], []
        for part in _PART.finditer(m["rest"]):
            if part[1]:
                ident = part[1]
            elif part[2]:
                classes.append(part[2])
            else:
                raw = part[4]
                attrs.append((part[3].lower(), raw.strip("\"'") if raw is not None else None))
        steps.append(
            (combinator, _Compound(tag and tag.lower(), ident, tuple(classes), tuple(attrs)))
        )
        combinator = " "
    if not steps or combinator == ">":
        raise ValueError(f"bad CSS selector {selector!r}")
    return tuple(steps)


# --- a small DOM ---------------------------------------------------------------------------------

VOID = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "source",
        "track",
        "wbr",
    }
)
BLOCK = frozenset(
    {
        "address",
        "article",
        "blockquote",
        "body",
        "caption",
        "dd",
        "details",
        "div",
        "dl",
        "dt",
        "figcaption",
        "figure",
        "footer",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "hr",
        "html",
        "li",
        "main",
        "ol",
        "p",
        "pre",
        "section",
        "summary",
        "table",
        "tbody",
        "tfoot",
        "thead",
        "tr",
        "ul",
    }
)
HEADINGS = {f"h{n}": n for n in range(1, 7)}
#: Opening one of these closes an open element of the same group, as browsers do.
_IMPLIED_CLOSE = {
    "p": ({"p"}, {"div", "section", "article", "main", "body", "td", "th", "li"}),
    "li": ({"li"}, {"ul", "ol"}),
    "dt": ({"dt", "dd"}, {"dl"}),
    "dd": ({"dt", "dd"}, {"dl"}),
    "tr": ({"tr", "td", "th"}, {"table", "thead", "tbody", "tfoot"}),
    "td": ({"td", "th"}, {"tr", "table"}),
    "th": ({"td", "th"}, {"tr", "table"}),
    "thead": ({"thead", "tbody", "tr", "td", "th"}, {"table"}),
    "tbody": ({"thead", "tbody", "tr", "td", "th"}, {"table"}),
    "tfoot": ({"thead", "tbody", "tr", "td", "th"}, {"table"}),
}


@dataclass(eq=False)
class Node:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list[Node | str] = field(default_factory=list)
    parent: Node | None = None

    @property
    def classes(self) -> tuple[str, ...]:
        return tuple(self.attrs.get("class", "").split())

    def elements(self) -> Iterator[Node]:
        """This node's descendant elements, in document order."""
        for child in self.children:
            if isinstance(child, Node):
                yield child
                yield from child.elements()


class _TreeBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("#document")
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _IMPLIED_CLOSE:
            closes, scope = _IMPLIED_CLOSE[tag]
            for i in range(len(self.stack) - 1, 0, -1):
                open_tag = self.stack[i].tag
                if open_tag in closes:
                    del self.stack[i:]
                    break
                if open_tag in scope:
                    break
        node = Node(tag, {k.lower(): v or "" for k, v in attrs}, parent=self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack[-1].tag == tag:
            self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)


def _is_furniture(node: Node, rules: RuleSet) -> bool:
    if node.tag in rules.drop_tags:
        return True
    if "hidden" in node.attrs or node.attrs.get("aria-hidden") == "true":
        return True
    if rules.drop_page_chrome and node.tag in ("header", "footer"):
        ancestor = node.parent
        while ancestor is not None:
            if ancestor.tag in ("article", "main", "section"):
                break
            ancestor = ancestor.parent
        else:
            return True
    if rules.drop_furniture:
        if node.attrs.get("role", "").lower() in FURNITURE_ROLES:
            return True
        tokens = (*node.classes, *node.attrs.get("id", "").split())
        if any(FURNITURE_TOKEN.match(t) for t in tokens):
            return True
    return False


def _prune(node: Node, rules: RuleSet) -> None:
    kept: list[Node | str] = []
    for child in node.children:
        if isinstance(child, Node):
            if _is_furniture(child, rules):
                continue
            _prune(child, rules)
        kept.append(child)
    node.children = kept


# --- rendering to text ---------------------------------------------------------------------------


def _inline(node: Node | str) -> str:
    if isinstance(node, str):
        return node
    if node.tag == "br":
        return " "
    return " ".join(_inline(c) for c in node.children)


def _render(node: Node | str, out: list[str]) -> None:
    """Append text to ``out``; a ``"\\n"`` entry is a block boundary."""
    if isinstance(node, str):
        out.append(_SPACE.sub(" ", node))
        return
    if node.tag == "tr":
        cells = [c for c in node.children if isinstance(c, Node) and c.tag in ("td", "th")]
        out += ["\n", " | ".join(_SPACE.sub(" ", _inline(c)).strip() for c in cells), "\n"]
        return
    if node.tag == "br":
        out.append("\n")
        return
    block = node.tag in BLOCK
    if block:
        out.append("\n")
    for child in node.children:
        _render(child, out)
    if block:
        out.append("\n")


def _clean_line(line: str, rules: RuleSet) -> str:
    if rules.strip_tracking:
        line = _URL.sub(lambda m: canonical_url(m.group(0)), line)
    if rules.strip_volatile:
        for pattern in VOLATILE_PATTERNS:
            line = pattern.sub(" ", line)
    line = _SPACE.sub(" ", line).strip()
    return "" if _EMPTY_LINE.match(line) else line


def _to_text(parts: list[str], rules: RuleSet) -> str:
    lines = (_clean_line(line, rules) for line in "".join(parts).split("\n"))
    return "\n".join(line for line in lines if line)


def _nodes_text(nodes: list[Node], rules: RuleSet) -> str:
    parts: list[str] = []
    for node in nodes:
        _render(node, parts)
        parts.append("\n")
    return _to_text(parts, rules)


# --- documents -----------------------------------------------------------------------------------


@dataclass
class Document:
    """A normalised page: its full text, and (for HTML) the cleaned tree for locators."""

    rules: RuleSet
    text: str
    root: Node | None = None


def normalise_document(body: bytes, rules: RuleSet, *, charset: str | None = None) -> Document:
    if body.lstrip().startswith(b"%PDF"):
        raise UnsupportedContentError("pdf")
    raw = body.decode(charset or "utf-8", errors="replace")
    raw = unicodedata.normalize("NFKC", raw).replace("\r\n", "\n").replace("\r", "\n")
    if rules.content == "text":
        return Document(rules, _to_text([raw], rules))
    builder = _TreeBuilder()
    builder.feed(raw)
    builder.close()
    root = builder.root
    _prune(root, rules)
    return Document(rules, _nodes_text([root], rules), root)


def select_region(doc: Document, locator: Locator) -> str | None:
    """The normalised text of a cited region, or ``None`` when the locator matches nothing."""
    if locator.kind == "page":
        return doc.text or None
    if doc.root is None:
        raise ValueError(f"{locator.kind} locators need an HTML document")
    if locator.kind == "table":
        tables = [n for n in doc.root.elements() if n.tag == "table"]
        index = int(locator.value)
        nodes = [tables[index]] if index < len(tables) else []
    elif locator.kind == "css":
        steps = _parse_selector(locator.value)
        nodes = [n for n in doc.root.elements() if _matches(n, steps)]
    else:
        nodes = _heading_section(doc.root, locator.value)
    return (_nodes_text(nodes, doc.rules) or None) if nodes else None


def _matches_compound(node: Node, c: _Compound) -> bool:
    if c.tag and node.tag != c.tag:
        return False
    if c.id and node.attrs.get("id") != c.id:
        return False
    if any(cls not in node.classes for cls in c.classes):
        return False
    for name, value in c.attrs:
        if name not in node.attrs or (value is not None and node.attrs[name] != value):
            return False
    return True


def _matches(node: Node, steps: tuple[tuple[str, _Compound], ...]) -> bool:
    combinator, last = steps[-1]
    if not _matches_compound(node, last):
        return False
    if len(steps) == 1:
        return True
    rest = steps[:-1]
    ancestor = node.parent
    while ancestor is not None and ancestor.tag != "#document":
        if _matches(ancestor, rest):
            return True
        if combinator == ">":
            return False
        ancestor = ancestor.parent
    return False


def _heading_level(node: Node) -> int | None:
    if node.tag in HEADINGS:
        return HEADINGS[node.tag]
    for descendant in node.elements():
        if descendant.tag in HEADINGS:
            return HEADINGS[descendant.tag]
    return None


def _heading_section(root: Node, anchor: str) -> list[Node]:
    wanted = anchor.removeprefix("#")
    folded = _SPACE.sub(" ", wanted).strip().casefold()
    heading = None
    for node in root.elements():
        if node.tag not in HEADINGS:
            continue
        ids = {node.attrs.get("id")} | {
            d.attrs.get("id") or d.attrs.get("name") for d in node.elements()
        }
        if wanted in ids or _SPACE.sub(" ", _inline(node)).strip().casefold() == folded:
            heading = node
            break
    if heading is None:
        return []
    level = HEADINGS[heading.tag]
    # A heading wrapped alone in a container (``<div><h2/></div>``) sections by the wrapper.
    start = heading
    for _ in range(2):
        parent = start.parent
        if parent is None or parent.tag in ("#document", "body", "main", "article", "section"):
            break
        if any(isinstance(c, Node) and c is not start for c in parent.children):
            break
        start = parent
    assert start.parent is not None
    siblings = [c for c in start.parent.children if isinstance(c, Node)]
    section = [start]
    for sibling in siblings[siblings.index(start) + 1 :]:
        other = _heading_level(sibling)
        if other is not None and other <= level:
            break
        section.append(sibling)
    return section


# --- urls and fingerprints -----------------------------------------------------------------------


def canonical_url(url: str) -> str:
    """``url`` without tracking query parameters or a fragment."""
    parts = urlsplit(url)
    query = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if k.lower() not in TRACKING_PARAMS and not k.lower().startswith(TRACKING_PREFIXES)
    ]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), ""))


def fingerprint(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
