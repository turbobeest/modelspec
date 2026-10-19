"""Exact template for the expanded Perplexity Pro FAQ (MODEL-368).

The reviewed structural hash was taken with this parser. Void tags are not
pushed, and a non-void start-end tag stays open, because that is how the
original retrieval hashed.
"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Mapping
from html.parser import HTMLParser
from typing import TYPE_CHECKING, Any, NoReturn
from urllib.parse import urlsplit

from decision.model import DETERMINISTIC, VerificationActor

if TYPE_CHECKING:
    from decision.verify import Claim, Reading

QUESTION = "What models do I get access to?"
PREFIX = "Pro includes "
SUFFIX_LENGTH = 70
SUFFIX_SHA256 = "d08feeac87a47183bd3e1ac74fec9de98a36ebd257bc7e92e7dae433a467c1b0"
FAQ_STRUCTURAL_HASH = "sha256:5bbb70cd6701e04065ea2497e4c0498b4bc2ec6b33b9d420f8f09c3713f2a0e2"
LIVE_ITEMS = (
    "GPT-5.6 Terra",
    "Claude Sonnet 5",
    "Gemini 3.1 Pro Thinking",
    "Grok 4.1",
    "Perplexity's in-house Sonar 2 model",
)
MAPPING = {
    "GPT-5.6 Terra": "openai/gpt-5-6-terra",
    "Claude Sonnet 5": "anthropic/claude-sonnet-5",
}
SUBJECT = "perplexity/subscription/pro"
FIELD = "offering.subscription.models_covered"
_SKIP = frozenset({"svg", "script", "style", "path", "use"})
_VOID = frozenset({"img", "br", "hr", "meta", "link", "input", "use", "source", "wbr"})


class _Node:
    def __init__(self, tag: str, attrs: dict[str, str] | None = None,
                 parent: _Node | None = None) -> None:
        self.tag = tag
        self.attrs = attrs or {}
        self.children: list[_Node | str] = []
        self.parent = parent


class _Builder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Node("#document")
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = _Node(tag, {key.lower(): value or "" for key, value in attrs}, self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in _VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)


def _drift() -> NoReturn:
    from decision.verify import ExtractorError

    raise ExtractorError("template drifted")


def _find_faq(node: _Node) -> _Node | None:
    if node.attrs.get("id") == "faq":
        return node
    for child in node.children:
        if isinstance(child, _Node):
            found = _find_faq(child)
            if found is not None:
                return found
    return None


def _slots(text: str) -> list[str] | None:
    collapsed = " ".join(text.split())
    if not collapsed.startswith(PREFIX):
        return None
    if hashlib.sha256(collapsed[-SUFFIX_LENGTH:].encode()).hexdigest() != SUFFIX_SHA256:
        return None
    middle = collapsed[len(PREFIX):-SUFFIX_LENGTH]
    if ", and " not in middle:
        return None
    head, last = middle.rsplit(", and ", 1)
    items = head.split(", ")
    if items and last and all(items) and "," not in last:
        return [*items, last]
    return None


def _inside(node: _Node, ancestor: _Node) -> bool:
    current: _Node | None = node
    while current is not None:
        if current is ancestor:
            return True
        current = current.parent
    return False


def _button_text(node: _Node) -> str:
    parts: list[str] = []

    def walk(current: _Node) -> None:
        if current.tag in _SKIP:
            return
        for child in current.children:
            if isinstance(child, str):
                parts.append(child)
            else:
                walk(child)

    walk(node)
    return " ".join(" ".join(parts).split())


def _structure(html: str) -> tuple[list[str], list[tuple[_Node, list[str]]], list[_Node]]:
    builder = _Builder()
    builder.feed(html)
    builder.close()
    faq = _find_faq(builder.root)
    if faq is None:
        _drift()
    tokens: list[str] = []
    slots: list[tuple[_Node, list[str]]] = []
    buttons: list[_Node] = []

    def walk(node: _Node) -> None:
        if node.tag in _SKIP:
            return
        tokens.append(node.tag)
        if node.tag == "button":
            buttons.append(node)
        for child in node.children:
            if isinstance(child, str):
                text = " ".join(child.split())
                if not text:
                    continue
                found = _slots(text)
                if found is None:
                    tokens.append("text:" + text)
                else:
                    tokens.append(f"text:{{slots:{len(found)}}}")
                    slots.append((node, found))
            else:
                walk(child)

    walk(faq)
    return tokens, slots, buttons


def _digest(tokens: list[str]) -> str:
    return "sha256:" + hashlib.sha256("\n".join(tokens).encode()).hexdigest()


def structural_hash(html: str) -> str:
    tokens, _slots_found, _buttons = _structure(html)
    return _digest(tokens)


class PerplexityFaqExtractor:
    """Reads Pro's model list only from the reviewed FAQ template."""

    actor = VerificationActor(
        agent="modelspec-verify", model_family=DETERMINISTIC, method="perplexity-pro-faq@1",
    )

    def __init__(self, *, template_hash: str | None = None,
                 mapping: Mapping[str, str] | None = None,
                 reviewed_order: tuple[str, ...] | None = None) -> None:
        self.template_hash = FAQ_STRUCTURAL_HASH if template_hash is None else template_hash
        self.mapping = dict(MAPPING if mapping is None else mapping)
        self.reviewed_order = LIVE_ITEMS if reviewed_order is None else reviewed_order

    def bound_to(self, claim: Claim, source_url: str | None) -> bool:
        if claim.field != FIELD or claim.subject != SUBJECT or not source_url:
            return False
        url = urlsplit(source_url)
        return (url.scheme == "https" and url.netloc == "www.perplexity.ai" and url.path == "/pro"
                and url.query == "" and url.fragment == "")

    def accepts(self, text: str) -> bool:
        return False

    def extract(self, claim: Claim, text: str) -> list[Reading]:
        from decision.verify import Reading

        if claim.field != FIELD or claim.subject != SUBJECT:
            return []
        tokens, slots, buttons = _structure(text)
        if len(slots) != 1 or _digest(tokens) != self.template_hash:
            _drift()
        questions = [button for button in buttons if _button_text(button) == QUESTION]
        if len(questions) != 1:
            _drift()
        button = questions[0]
        item = button.parent
        answer_at, items = slots[0]
        if item is None or not _inside(answer_at, item) or _inside(answer_at, button):
            _drift()
        missing = [literal for literal in items if literal not in self.mapping]
        if missing:
            from decision.verify import ExtractorError

            raise ExtractorError("incomplete mapping: " + "; ".join(missing))
        if tuple(items) != tuple(self.reviewed_order):
            _drift()
        return [Reading(claim.names[0], ", ".join(self.mapping[literal] for literal in items))]


def prepare_pro_faq(page: Any, timeout: float) -> None:
    """Expand the Pro models question before a rendered capture of this source."""
    deadline = time.monotonic() + timeout

    def remaining_ms() -> float:
        return max(1.0, (deadline - time.monotonic()) * 1000)

    page.locator("#faq").get_by_role(
        "button", name=QUESTION, exact=True,
    ).click(timeout=remaining_ms())
    page.wait_for_function(
        """question => {
            const root = document.querySelector('#faq');
            if (!root) return false;
            const button = Array.from(root.querySelectorAll('button'))
                .find(node => node.textContent.trim() === question);
            if (!button || button.getAttribute('aria-expanded') !== 'true') return false;
            const item = button.parentElement;
            return !!item && item.textContent.includes('Pro includes ');
        }""",
        arg=QUESTION,
        timeout=remaining_ms(),
    )
