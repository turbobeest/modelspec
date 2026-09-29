"""The only thing an LLM may do to a breakdown: smooth the wording of its prose.

``smooth`` hands each prose paragraph of a rendered post to a rewriter and
refuses the result unless ``check_smoothed`` finds that nothing but wording
changed. Tables, headings, lists, charts, footnotes and the headline are never
handed over. In a paragraph, a rewrite may not add, drop, reorder or change a
number or a footnote marker, add a link or a model ID, flip a direction or a
negation, add a sentence, or introduce a refused word. There is no model
client here: a caller supplies ``rewrite``, and nothing it returns is kept
unless it passes.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Callable

from release_blog.tone import refused_words

_FOOTNOTE = re.compile(r"\[\^[^\]]+\]")
_NUMBER = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?")
_URL = re.compile(r"https?://[^\s)>\]]+")
_MODEL_ID = re.compile(r"\b[a-z0-9][a-z0-9._-]*/[a-z0-9][a-z0-9._-]*\b")
_SENTENCE = re.compile(r"(?<=[.!?;])\s+")
#: Words that carry a claim's direction, polarity or band. Their counts are fixed.
CLAIM_WORDS = frozenset({
    "higher", "lower", "above", "below", "equals", "not", "no", "never", "unknown",
    "leading", "best", "rest", "thin", "outside", "within", "only", "covers", "cover",
    "awaiting", "await", "yet", "none",
})
_WORD = re.compile(r"[a-z]+")
_NOT_PROSE = ("|", "#", "![", "[^", "- ", "* ", "> ", "```", "<", "---")


class SmoothingError(ValueError):
    """A rewrite changed more than wording."""

    def __init__(self, problems: list[str]):
        self.problems = problems
        super().__init__("smoothing refused: " + "; ".join(problems))


def blocks(markdown: str) -> list[str]:
    return markdown.split("\n\n")


def is_prose(block: str) -> bool:
    text = block.strip()
    return bool(text) and not text.startswith(_NOT_PROSE)


def _facts(block: str) -> dict[str, object]:
    bare = _FOOTNOTE.sub(" ", block)
    return {
        "numbers": _NUMBER.findall(bare),
        "footnotes": _FOOTNOTE.findall(block),
        "links": sorted(_URL.findall(block)),
        "model ids": sorted(_MODEL_ID.findall(_URL.sub(" ", bare))),
        "claim words": Counter(w for w in _WORD.findall(bare.lower()) if w in CLAIM_WORDS),
    }


def _sentences(block: str) -> int:
    return len([part for part in _SENTENCE.split(block.strip()) if part.strip()])


def check_smoothed(original: str, candidate: str) -> None:
    """Raise ``SmoothingError`` unless ``candidate`` differs from ``original`` in wording only."""
    before, after = blocks(original), blocks(candidate)
    problems: list[str] = []
    if len(before) != len(after):
        raise SmoothingError([f"paragraph count changed: {len(before)} -> {len(after)}"])
    for index, (old, new) in enumerate(zip(before, after, strict=True)):
        if not is_prose(old):
            if old != new:
                problems.append(f"block {index} is not prose and must not change")
            continue
        if not is_prose(new):
            problems.append(f"block {index} stopped being prose")
            continue
        old_facts, new_facts = _facts(old), _facts(new)
        for key, value in old_facts.items():
            if new_facts[key] != value:
                problems.append(f"block {index}: {key} changed: {value!r} -> {new_facts[key]!r}")
        if _sentences(new) > _sentences(old):
            problems.append(f"block {index}: a sentence was added")
        added = Counter(refused_words(new)) - Counter(refused_words(old))
        if added:
            problems.append(f"block {index}: refused words added: {sorted(added)}")
    if problems:
        raise SmoothingError(problems)


def smooth(markdown: str, rewrite: Callable[[str], str]) -> str:
    """``markdown`` with each prose paragraph passed through ``rewrite``, checked."""
    candidate = "\n\n".join(
        rewrite(block) if is_prose(block) else block for block in blocks(markdown)
    )
    check_smoothed(markdown, candidate)
    return candidate
