"""The excluded-source rules shared by the catalogue guard and snapshot build."""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlsplit

# These publishers and their owned measurements were removed by MODEL-117.
REMOVED_HOSTS = ("artificialanalysis.ai", "zapier.com")
# Owned benchmark names. Publisher names are `excluded_publisher`.
REMOVED_TEXT = re.compile(
    r"automationbench|gdpval-aa|aa-lcr|"
    r"aa[\s-]intelligence[\s-]index|omniscience",
    re.IGNORECASE,
)
REMOVED_ID = re.compile(r"^(aa_|artificial_?analysis|automationbench)|_aa$|_aa_")
# Substrings of the casefolded letters and digits. No word boundary.
PUBLISHER_NAMES = ("artificialanalysis", "zapier")
# Exempt only when this is the dict key. The same characters in a value are not.
LEGACY_SOURCE_KEY = "artificial_analysis_url"


@dataclass(frozen=True)
class ExcludedSources:
    hosts: tuple[str, ...] = REMOVED_HOSTS
    text: re.Pattern[str] = REMOVED_TEXT
    ids: re.Pattern[str] = REMOVED_ID

    def url(self, url: object) -> bool:
        host = (urlsplit(str(url or "").strip()).hostname or "").lower().rstrip(".")
        return any(host == item or host.endswith("." + item) for item in self.hosts)

    def benchmark(self, benchmark_id: object) -> bool:
        return bool(self.ids.search(str(benchmark_id)))


def excluded_sources() -> ExcludedSources:
    return ExcludedSources()


def _fold(text: str) -> str:
    return "".join(char for char in text.casefold() if char.isalpha() or char.isdigit())


def excluded_publisher(text: str) -> bool:
    """True when the letters and digits in ``text`` contain a removed publisher.

    Casefold the text, drop every character that is not a letter or digit,
    and match ``artificialanalysis`` or ``zapier`` as a substring. Domains
    such as ``artificialanalysis.ai`` and ``zapier.com`` match, and so does
    ``ArtificialAnalysisPro``.
    """
    folded = _fold(text)
    return any(name in folded for name in PUBLISHER_NAMES)


def each_string(obj: object):
    """Every string in ``obj``, except a dict key equal to ``LEGACY_SOURCE_KEY``.

    Lists and tuples are walked. Any other scalar is converted with ``str``.
    The legacy key's value is walked. A string that only looks like the key
    is not an exemption.
    """
    if isinstance(obj, str):
        yield obj
        return
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key != LEGACY_SOURCE_KEY:
                yield from each_string(key)
            yield from each_string(value)
        return
    if isinstance(obj, (list, tuple)):
        for item in obj:
            yield from each_string(item)
        return
    yield str(obj)


def excluded_in(obj: object) -> bool:
    """True when any walked string names a removed publisher."""
    return any(excluded_publisher(text) for text in each_string(obj))


def removed_text_hit(obj: object) -> re.Match[str] | None:
    """An owned-benchmark name in a walked string, if one is present."""
    for text in each_string(obj):
        hit = REMOVED_TEXT.search(text)
        if hit:
            return hit
    return None


def publisher_excerpt(obj: object, *, before: int = 40, after: int = 80) -> str:
    """A short slice of the first walked string that names a publisher."""
    for text in each_string(obj):
        if not excluded_publisher(text):
            continue
        span = publisher_span(text)
        if span is None:
            return text[: before + after]
        start, end = span
        return text[max(0, start - before) : end + after]
    return ""


def publisher_span(text: str) -> tuple[int, int] | None:
    """Original slice whose letters contain a publisher."""
    indexes: list[int] = []
    chars: list[str] = []
    for index, char in enumerate(text):
        for piece in char.casefold():
            if piece.isalpha() or piece.isdigit():
                chars.append(piece)
                indexes.append(index)
    folded = "".join(chars)
    for name in PUBLISHER_NAMES:
        at = folded.find(name)
        if at < 0:
            continue
        return indexes[at], indexes[at + len(name) - 1] + 1
    return None
