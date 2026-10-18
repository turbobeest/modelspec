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
# The legacy card field. Exempt as a key only. A value with this spelling
# still collapses to the first publisher name.
_LEGACY_SOURCE_KEY = re.compile(
    r"""(?<![\w])["']?artificial_analysis_url["']?(?=\s*:)"""
)


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

    The legacy field key ``artificial_analysis_url`` collapses to the same
    letters. Callers that read a document pass the text through
    ``without_legacy_source_keys`` first. That helper removes the key only.
    A value stays, including a value spelled like the key.
    """
    folded = _fold(text)
    return any(name in folded for name in PUBLISHER_NAMES)


def without_legacy_source_keys(text: str) -> str:
    """Drop the legacy field key. A value with the same spelling stays."""
    return _LEGACY_SOURCE_KEY.sub("", text)


def publisher_span(text: str) -> tuple[int, int] | None:
    """Original slice whose letters contain a publisher, skipping the legacy key."""
    indexes: list[int] = []
    chars: list[str] = []
    for index, char in enumerate(text):
        for piece in char.casefold():
            if piece.isalpha() or piece.isdigit():
                chars.append(piece)
                indexes.append(index)
    folded = "".join(chars)
    for name in PUBLISHER_NAMES:
        start = 0
        while True:
            at = folded.find(name, start)
            if at < 0:
                break
            origin = indexes[at]
            end = indexes[at + len(name) - 1] + 1
            if not _legacy_key_covers(text, origin, end):
                return origin, end
            start = at + 1
    return None


def _legacy_key_covers(text: str, start: int, end: int) -> bool:
    left = start
    while left > 0 and (text[left - 1].isalnum() or text[left - 1] == "_"):
        left -= 1
    right = end
    while right < len(text) and (text[right].isalnum() or text[right] == "_"):
        right += 1
    if text[left:right] != "artificial_analysis_url":
        return False
    return text[right:].lstrip(" \t\"'").startswith(":")
