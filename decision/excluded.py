"""The excluded-source rules shared by the catalogue guard and snapshot build."""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlsplit

# These publishers and their owned measurements were removed by MODEL-117.
REMOVED_HOSTS = ("artificialanalysis.ai", "zapier.com")
# Publisher names match across any run of whitespace, hyphens, underscores, or
# dots. The name is a whole token: the empty legacy field
# `artificial_analysis_url` is a key, and REMOVED_ID already rejects that
# string as a benchmark id. The second alternative stays the bare second
# publisher so callers that take the pattern's second branch still see that name.
REMOVED_TEXT = re.compile(
    r"(?<!\w)artificial\s*[-_.]*\s*analysis(?!\w)|zapier|"
    r"(?<!\w)z\s*[-_.]*\s*a\s*[-_.]*\s*p\s*[-_.]*\s*i\s*[-_.]*\s*e\s*[-_.]*\s*r(?!\w)|"
    r"automationbench|gdpval-aa|aa-lcr|"
    r"aa[\s-]intelligence[\s-]index|omniscience",
    re.IGNORECASE,
)
_SEPARATORS = re.compile(r"[\s\-_.]+")
REMOVED_ID = re.compile(r"^(aa_|artificial_?analysis|automationbench)|_aa$|_aa_")


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


def excluded_publisher(text: str) -> bool:
    """True when collapsing whitespace and separator runs reveals a removed publisher."""
    if REMOVED_TEXT.search(text):
        return True
    return REMOVED_TEXT.search(_SEPARATORS.sub("", text)) is not None
