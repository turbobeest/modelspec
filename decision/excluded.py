"""The excluded-source rules shared by the catalogue guard and snapshot build."""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlsplit

# These publishers and their owned measurements were removed by MODEL-117.
REMOVED_HOSTS = ("artificialanalysis.ai", "zapier.com")
REMOVED_TEXT = re.compile(
    r"artificial[\s-]?analysis|zapier|automationbench|gdpval-aa|aa-lcr|"
    r"aa[\s-]intelligence[\s-]index|omniscience",
    re.IGNORECASE,
)
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
